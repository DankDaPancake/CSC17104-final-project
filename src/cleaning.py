"""Hàm làm sạch dùng chung cho bộ dữ liệu VietJobs.

Mọi notebook phân tích đọc dữ liệu sạch qua ``load_clean()`` — không tự làm sạch lại.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import numpy as np
import pandas as pd

CLEAN_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "vietjobs_clean.parquet"
RAW_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "VietJobs.csv"

SALARY_OUTLIER_THRESHOLD = 200  # triệu VND/tháng
SALARY_MIN_VALID = 1  # < 1 triệu/tháng coi là ngoại lai (lương giờ/ngày hoặc lỗi)
RARE_CONTRACT_MIN = 100
EXPERIENCE_LEVELS = ["Không yêu cầu", "Dưới 1 năm", "1-2 năm", "3-5 năm", "Trên 5 năm", "Không rõ"]
REGIONS = ["Hà Nội", "TP.HCM", "Khác"]

_NUM = re.compile(r"(\d+(?:\.\d+)?)")
_HANOI_DISTRICTS = {
    "hà đông", "ba đình", "hoàn kiếm", "tây hồ", "long biên", "cầu giấy", "đống đa", "hai bà trưng",
    "hoàng mai", "thanh xuân", "bắc từ liêm", "nam từ liêm", "từ liêm", "sóc sơn", "đông anh", "gia lâm",
    "thanh trì", "mê linh", "sơn tây", "ba vì", "phúc thọ", "đan phượng", "hoài đức", "quốc oai",
    "thạch thất", "chương mỹ", "thanh oai", "thường tín", "phú xuyên", "ứng hòa", "ứng hoà", "mỹ đức",
    "mỹ đình", "linh đàm", "dương nội", "minh khai", "trương định", "tam trinh", "vĩnh tuy", "cự khối",
    "phú đô", "kcn quang minh",
}
_HCM_DISTRICTS = {
    "thủ đức", "thành phố thủ đức", "bình thạnh", "gò vấp", "phú nhuận", "tân bình", "tân phú",
    "bình tân", "củ chi", "cu chi", "hóc môn", "bình chánh", "nhà bè", "cần giờ", "tân sơn nhì",
    "tân thới nhì", "ho chi minh city", "tp hcm", "tphcm", "hcm", "sài gòn",
}
_LOCATION_ALIASES = {d: "hà nội" for d in _HANOI_DISTRICTS} | {d: "hồ chí minh" for d in _HCM_DISTRICTS}
_LOC_SPLIT = re.compile(r"[,;&/]| và ")
_LOC_PREFIX = re.compile(r"^(tp\.?|thành phố)\s+")
_HCM_QUAN = re.compile(r"^quận \d+$")


def _is_missing(s) -> bool:
    return s is None or (isinstance(s, float) and np.isnan(s)) or str(s).strip().lower() in {"", "nan"}


def parse_salary_avg(s) -> float:
    """'12 triệu' -> 12.0; 'Thoả thuận' / NaN -> NaN."""
    if _is_missing(s):
        return np.nan
    m = _NUM.search(str(s))
    return float(m.group(1)) if m else np.nan


def parse_salary_midpoint(s) -> float:
    """'8.5 - 9.0 triệu' -> 8.75; '14.0 triệu' -> 14.0; '0.0 triệu' (thoả thuận) / NaN -> NaN.

    Dùng thay cho cột `salary_avg` gốc vì cột đó làm tròn xuống (8.5–9.0 -> "8 triệu").
    """
    if _is_missing(s):
        return np.nan
    nums = [float(x) for x in _NUM.findall(str(s))]
    if not nums or max(nums) == 0:
        return np.nan
    return sum(nums[:2]) / len(nums[:2])


def parse_experience_months(s) -> float:
    """'6 tháng' -> 6; '2 năm' -> 24; 'Không yêu cầu' -> 0; không nhận diện -> NaN."""
    if _is_missing(s):
        return np.nan
    text = str(s).strip().lower()
    if "không yêu cầu" in text:
        return 0.0
    m = _NUM.search(text)
    if not m:
        return np.nan
    value = float(m.group(1))
    if "năm" in text:
        return value * 12
    if "tháng" in text:
        return value
    return np.nan


def experience_level(months: float) -> str:
    if months is None or np.isnan(months):
        return "Không rõ"
    if months == 0:
        return "Không yêu cầu"
    if months < 12:
        return "Dưới 1 năm"
    if months <= 24:
        return "1-2 năm"
    if months <= 60:
        return "3-5 năm"
    return "Trên 5 năm"


def normalize_location(s) -> tuple[str, bool]:
    """Trả (tỉnh chính, có nhiều tỉnh hay không)."""
    if _is_missing(s):
        return ("không rõ", False)
    text = str(s).lower().replace("[", "").replace("]", "").replace("'", "").replace('"', "")
    parts = [p.strip(" .-") for p in _LOC_SPLIT.split(text) if p.strip(" .-")]
    if not parts:
        return ("không rõ", False)
    return (_canonical_location(parts[0]), len(parts) > 1)


def _canonical_location(loc: str) -> str:
    loc = loc.split(" - ")[0].split(":")[0].strip()
    if loc in _LOCATION_ALIASES:
        return _LOCATION_ALIASES[loc]
    bare = _LOC_PREFIX.sub("", loc)
    if bare in _LOCATION_ALIASES:
        return _LOCATION_ALIASES[bare]
    if _HCM_QUAN.match(loc):
        return "hồ chí minh"
    return loc


def to_region(loc: str) -> str:
    if loc == "hà nội":
        return "Hà Nội"
    if loc == "hồ chí minh":
        return "TP.HCM"
    return "Khác"


def parse_list(s) -> list[str]:
    """Chuỗi list Python -> list[str]; không bao giờ raise."""
    if _is_missing(s):
        return []
    text = str(s).strip()
    try:
        value = ast.literal_eval(text)
        items = value if isinstance(value, (list, tuple)) else [value]
    except Exception:  # dữ liệu bẩn: không bao giờ raise
        items = text.strip("[]").split(",")
        items = [i.strip().strip("'\"") for i in items]
    return [str(i).strip() for i in items if str(i).strip()]


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    """Pipeline làm sạch đầy đủ: lọc Việt Nam, bỏ trùng, thêm cột đã chuẩn hoá."""
    df = raw[raw["country"] == "Việt Nam"].copy()
    df = df.drop_duplicates(subset=["job_title", "location", "description"]).reset_index(drop=True)

    df["salary_negotiable"] = df["salary_avg"].map(parse_salary_avg).isna()
    df["salary_avg_num"] = df["salary"].map(parse_salary_midpoint).where(~df["salary_negotiable"])
    df["salary_outlier"] = (df["salary_avg_num"] > SALARY_OUTLIER_THRESHOLD) | (
        df["salary_avg_num"] < SALARY_MIN_VALID
    )

    df["experience_months"] = df["experience_required"].map(parse_experience_months)
    df["experience_level"] = pd.Categorical(
        df["experience_months"].map(experience_level), categories=EXPERIENCE_LEVELS, ordered=True
    )

    loc = df["location"].map(normalize_location)
    df["location_primary"] = loc.map(lambda t: t[0])
    df["multi_location"] = loc.map(lambda t: t[1])
    df["region"] = pd.Categorical(df["location_primary"].map(to_region), categories=REGIONS)

    counts = df["contract_type"].value_counts()
    common = set(counts[counts >= RARE_CONTRACT_MIN].index)
    df["contract_group"] = df["contract_type"].where(df["contract_type"].isin(common), "Khác")

    for col in ["technical_skills", "soft_skills", "benefits", "qualifications"]:
        df[f"{col}_list"] = df[col].map(parse_list)
    df["n_benefits"] = df["benefits_list"].map(len)
    df["n_technical_skills"] = df["technical_skills_list"].map(len)
    return df


def load_clean(path: Path = CLEAN_PATH) -> pd.DataFrame:
    """Đọc dữ liệu sạch (tạo bởi notebooks/02_cleaning.ipynb)."""
    df = pd.read_parquet(path)
    for col in ["technical_skills_list", "soft_skills_list", "benefits_list", "qualifications_list"]:
        df[col] = df[col].map(list)
    return df


CATEGORY_LABELS = {
    "kinh_doanh_bán_hàng_chăm_sóc_khách_hàng": "Kinh doanh/CSKH",
    "sản_xuất_lao_động_phổ_thông_cơ_khí": "Sản xuất/Cơ khí",
    "marketing_truyền_thông_quảng_cáo_nội_dung": "Marketing/Truyền thông",
    "tài_chính_kế_toán_ngân_hàng_bảo_hiểm": "Tài chính/Kế toán",
    "du_lịch_nhà_hàng_khách_sạn_dịch_vụ": "Du lịch/Nhà hàng",
    "thiết_kế_nghệ_thuật_giải_trí_truyền_hình_báo_chí": "Thiết kế/Nghệ thuật",
    "nhân_sự_hành_chính_pháp_chế_tư_vấn": "Nhân sự/Hành chính",
    "xây_dựng_kiến_trúc_bất_động_sản": "Xây dựng/BĐS",
    "công_nghệ_thông_tin_kỹ_thuật_số": "CNTT",
    "logistics_vận_tải_chuỗi_cung_ứng": "Logistics",
    "kỹ_thuật_điện_điện_tử_viễn_thông": "Điện/Điện tử",
    "giáo_dục_đào_tạo_nghiên_cứu": "Giáo dục",
    "y_tế_dược_chăm_sóc_sức_khỏe_công_nghệ_sinh_học": "Y tế/Dược",
    "ngôn_ngữ_dịch_thuật": "Ngôn ngữ/Dịch thuật",
    "nhóm_nghề_khác": "Nghề khác",
    "nông_nghiệp_năng_lượng_môi_trường": "Nông nghiệp/Môi trường",
}
