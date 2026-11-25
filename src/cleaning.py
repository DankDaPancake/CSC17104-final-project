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
_LOCATION_ALIASES = {"hà đông": "hà nội"}


def _is_missing(s) -> bool:
    return s is None or (isinstance(s, float) and np.isnan(s)) or str(s).strip().lower() in {"", "nan"}


def parse_salary_avg(s) -> float:
    """'12 triệu' -> 12.0; 'Thoả thuận' / NaN -> NaN."""
    if _is_missing(s):
        return np.nan
    m = _NUM.search(str(s))
    return float(m.group(1)) if m else np.nan


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
    parts = [p.strip().lower() for p in str(s).split(",") if p.strip()]
    if not parts:
        return ("không rõ", False)
    primary = _LOCATION_ALIASES.get(parts[0], parts[0])
    return (primary, len(parts) > 1)


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
    except (ValueError, SyntaxError):
        items = text.strip("[]").split(",")
        items = [i.strip().strip("'\"") for i in items]
    return [str(i).strip() for i in items if str(i).strip()]


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    """Pipeline làm sạch đầy đủ: lọc Việt Nam, bỏ trùng, thêm cột đã chuẩn hoá."""
    df = raw[raw["country"] == "Việt Nam"].copy()
    df = df.drop_duplicates(subset=["job_title", "location", "description"]).reset_index(drop=True)

    df["salary_avg_num"] = df["salary_avg"].map(parse_salary_avg)
    df["salary_negotiable"] = df["salary_avg_num"].isna()
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
