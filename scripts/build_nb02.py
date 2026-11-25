from nbtools import build

build("notebooks/02_cleaning.ipynb", [
("md", """
# 02. Làm sạch dữ liệu VietJobs

**Đầu vào:** `data/raw/VietJobs.csv` (48.092 × 18). **Đầu ra:** `data/processed/vietjobs_clean.parquet`.

Toàn bộ logic nằm trong `src/cleaning.py` (có test trong `tests/test_cleaning.py`). Notebook này chạy pipeline,
trình bày các quyết định làm sạch và kiểm tra kết quả trước/sau.

| Vấn đề | Quyết định |
|---|---|
| Lương "Thoả thuận" lưu là 0 | `salary_negotiable=True`, `salary_avg_num=NaN` |
| Lương < 1 triệu hoặc > 200 triệu/tháng | `salary_outlier=True` (lương giờ/ngày, lỗi nhập) — loại khỏi phân tích lương |
| Kinh nghiệm dạng chữ | `experience_months` (số) + `experience_level` (nhóm có thứ tự) |
| Địa điểm không chuẩn, nhiều tỉnh/tin | `location_primary` (tỉnh đầu, "hà đông"→"hà nội"), `multi_location`, `region` |
| Tin ngoài Việt Nam | loại |
| Tin trùng (cùng tên việc, địa điểm, mô tả) | giữ bản đầu tiên |
| List lưu dạng chuỗi | parse thành list, đếm `n_benefits`, `n_technical_skills` |
| Loại hợp đồng hiếm (< 100 tin) | gộp vào "Khác" |
"""),
("code", """
import sys
sys.path.insert(0, "..")
import pandas as pd
from src.cleaning import RAW_PATH, CLEAN_PATH, clean, parse_salary_avg

raw = pd.read_csv(RAW_PATH)
print(f"Raw: {raw.shape[0]:,} rows x {raw.shape[1]} columns")
(raw.isna().mean() * 100).round(1).sort_values(ascending=False).to_frame("missing_%").head(8)
"""),
("md", "## Số dòng bị loại theo từng bước"),
("code", """
vn = raw[raw["country"] == "Việt Nam"]
steps = pd.DataFrame({
    "bước": ["Dữ liệu gốc", "Chỉ giữ Việt Nam", "Bỏ trùng (job_title, location, description)"],
    "số dòng": [len(raw), len(vn), len(vn.drop_duplicates(["job_title", "location", "description"]))],
})
steps["bị loại"] = steps["số dòng"].shift(1) - steps["số dòng"]
steps
"""),
("md", """
**Nhận xét về trùng lặp:** ~11.500 tin có cùng tên việc, địa điểm và mô tả — chủ yếu là cùng một tin được đăng lại
(phúc lợi chỉ khác cách diễn đạt). Giữ lại sẽ làm các nhà tuyển dụng đăng nhiều lần bị đếm quá mức.
"""),
("code", """
df = clean(raw)
print(f"Clean: {df.shape[0]:,} rows x {df.shape[1]} columns")
summary = pd.Series({
    "% thoả thuận": df["salary_negotiable"].mean() * 100,
    "số tin ngoại lai lương": df["salary_outlier"].sum(),
    "số tin có lương hợp lệ": (~df["salary_negotiable"] & ~df["salary_outlier"]).sum(),
    "trung vị lương (triệu)": df.loc[~df["salary_outlier"], "salary_avg_num"].median(),
}).round(2)
summary
"""),
("code", """
for col in ["experience_level", "region", "contract_group"]:
    display(df[col].value_counts().to_frame())
"""),
("code", """
df[["salary_avg_num", "experience_months", "n_benefits", "n_technical_skills"]].describe().round(2)
"""),
("md", "## Lưu dữ liệu sạch"),
("code", """
CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(CLEAN_PATH, index=False)
print("Saved:", CLEAN_PATH, f"({CLEAN_PATH.stat().st_size/1e6:.1f} MB)")
"""),
])
