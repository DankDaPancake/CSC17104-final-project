# VietJobs Final Project Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Từ `VietJobs.csv` thô, tạo bộ dữ liệu sạch dùng chung, trả lời 6 câu hỏi (Q1–Q6, Q6 là ML dự đoán lương) trong 8 notebook chạy lại được, và hoàn thành báo cáo + slide trước 15/12/2026.

**Architecture:** Logic làm sạch và ML nằm trong module Python có test (`src/cleaning.py`, `src/modeling.py`); notebook chỉ gọi hàm, vẽ hình, viết nhận xét. `02_cleaning.ipynb` xuất `data/processed/vietjobs_clean.parquet`; notebook 03–08 chỉ đọc file này qua `load_clean()`.

**Tech Stack:** Python 3.11, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, pyarrow, pytest, Jupyter (Conda env `csc17104-final-project`).

**Spec:** `docs/superpowers/specs/2026-11-25-vietjobs-project-design.md`

## Global Constraints

- Dữ liệu gốc: `data/raw/VietJobs.csv` (48.092 × 18), tải từ `https://huggingface.co/datasets/dinhieufam/VietJobs/resolve/main/VietJobs.csv`; **không commit dữ liệu**.
- Dữ liệu sạch: `data/processed/vietjobs_clean.parquet`; mọi notebook phân tích chỉ đọc file này.
- Đơn vị lương: **triệu VND/tháng**; "Thoả thuận" → `salary_avg = NaN`, `salary_negotiable = True`.
- Chỉ giữ `country == "Việt Nam"`.
- ML: target `log(salary_avg)`; **cấm** dùng `salary`, `salary_min`, `salary_max`, `salary_avg`, `salary_negotiable` làm feature; split train/test (80/20) trước mọi fit; `random_state=42`.
- Notebook chạy từ `notebooks/` với `sys.path.insert(0, "..")` để import `src`.
- Mỗi lần dùng LLM ghi một dòng vào `LLM_USAGE.md`.
- Hạn: làm sạch xong 29/11; notebook 03–08 xong 08/12; báo cáo/slide 12/12; nộp 15/12.

## Review Focus

- Lương ngoại lai (`salary_max` tới 500 triệu): Q1/Q2/Q6 dùng trung vị/log và tin > 200 triệu bị gắn cờ `salary_outlier` → test trong Task 2.
- Tin có `salary_min == 0` nhưng `salary_avg` không phải "Thoả thuận" (hoặc ngược lại): `salary_negotiable` lấy theo `salary_avg` chuỗi → test trong Task 1.
- Chuỗi list hỏng (dấu nháy lẻ trong phần tử, `nan`, chuỗi rỗng) làm `ast.literal_eval` lỗi → `parse_list` không bao giờ raise → test trong Task 1.
- Địa điểm nhiều tỉnh ("hà nội, hồ chí minh") và "hà đông" → lấy tỉnh đầu, "hà đông" → "hà nội", `multi_location=True` → test trong Task 1.
- Tin trùng lặp: bỏ trùng theo (`job_title`, `location`, `description`) → test trong Task 2.

---

### Task 1: Hàm làm sạch từng cột (`src/cleaning.py`)

**Files:**
- Create: `src/__init__.py` (rỗng), `src/cleaning.py`, `tests/test_cleaning.py`
- Modify: `environment.yml` (thêm `pytest`)

**Interfaces:**
- Produces (trong `src/cleaning.py`):
  - `parse_salary_avg(s: str | float) -> float` — "12 triệu" → 12.0; "Thoả thuận"/NaN → `np.nan`
  - `parse_experience_months(s: str | float) -> float` — "6 tháng" → 6; "2 năm" → 24; "Không yêu cầu" → 0; không nhận diện → `np.nan`
  - `experience_level(months: float) -> str` — `0`→"Không yêu cầu", `<12`→"Dưới 1 năm", `12–24`→"1-2 năm", `25–60`→"3-5 năm", `>60`→"Trên 5 năm", NaN→"Không rõ"
  - `normalize_location(s: str) -> tuple[str, bool]` — trả (tỉnh chính đã lower/strip, có nhiều tỉnh hay không); "hà đông" → "hà nội"
  - `to_region(loc: str) -> str` — "hà nội"→"Hà Nội", "hồ chí minh"→"TP.HCM", khác→"Khác"
  - `parse_list(s: str | float) -> list[str]` — chuỗi list Python → list đã strip, bỏ phần tử rỗng; NaN/""/"nan" → `[]`; lỗi parse → tách theo dấu phẩy sau khi bỏ `[]'"`

- [ ] **Step 1: Thêm `- pytest` vào `environment.yml`, chạy `conda env update -f environment.yml --prune`**

- [ ] **Step 2: Viết test thất bại `tests/test_cleaning.py`**

```python
import numpy as np, pytest
from src.cleaning import (parse_salary_avg, parse_experience_months, experience_level,
                          normalize_location, to_region, parse_list)

def test_salary():
    assert parse_salary_avg("12 triệu") == 12.0
    assert np.isnan(parse_salary_avg("Thoả thuận"))
    assert np.isnan(parse_salary_avg(np.nan))

@pytest.mark.parametrize("s,m", [("6 tháng", 6), ("2 năm", 24), ("18 tháng", 18),
                                 ("Không yêu cầu", 0), ("10 năm", 120)])
def test_experience(s, m):
    assert parse_experience_months(s) == m

def test_experience_unknown():
    assert np.isnan(parse_experience_months("abc"))

def test_experience_level():
    assert experience_level(0) == "Không yêu cầu"
    assert experience_level(6) == "Dưới 1 năm"
    assert experience_level(24) == "1-2 năm"
    assert experience_level(36) == "3-5 năm"
    assert experience_level(120) == "Trên 5 năm"
    assert experience_level(np.nan) == "Không rõ"

def test_location():
    assert normalize_location("hà đông") == ("hà nội", False)
    assert normalize_location(" Hà Nội, hồ chí minh ") == ("hà nội", True)
    assert to_region("hồ chí minh") == "TP.HCM"
    assert to_region("đà nẵng") == "Khác"

def test_parse_list():
    assert parse_list("['Thưởng năm', ' Lương tháng 13']") == ["Thưởng năm", "Lương tháng 13"]
    assert parse_list(np.nan) == [] and parse_list("nan") == [] and parse_list("") == []
    assert parse_list("['Kỹ năng 'mềm', 'Excel']")  # malformed: không raise, trả list không rỗng
```

- [ ] **Step 3: Chạy `pytest tests/test_cleaning.py -v` → FAIL (ImportError)**

- [ ] **Step 4: Cài đặt các hàm trong `src/cleaning.py`** (regex `(\d+(?:\.\d+)?)` cho số; `ast.literal_eval` bọc try/except cho `parse_list`)

- [ ] **Step 5: Chạy `pytest tests/test_cleaning.py -v` → PASS**

- [ ] **Step 6: Commit** — `git add src tests environment.yml && git commit -m "feat: add column cleaning helpers with tests"`

---

### Task 2: Pipeline làm sạch + notebook 02

**Files:**
- Modify: `src/cleaning.py`, `tests/test_cleaning.py`
- Create: `notebooks/02_cleaning.ipynb`

**Interfaces:**
- Consumes: các hàm Task 1.
- Produces:
  - `clean(raw: pd.DataFrame) -> pd.DataFrame` — lọc Việt Nam, bỏ trùng theo (`job_title`,`location`,`description`), thêm cột: `salary_avg_num` (float), `salary_negotiable` (bool), `salary_outlier` (bool, `salary_avg_num > 200`), `experience_months`, `experience_level`, `location_primary`, `multi_location`, `region`, `contract_group` (loại có < 100 tin → "Khác"), `technical_skills_list`, `soft_skills_list`, `benefits_list`, `qualifications_list` (list[str]), `n_benefits`, `n_technical_skills` (int). Giữ nguyên các cột gốc khác.
  - `CLEAN_PATH = Path(__file__).resolve().parents[1] / "data/processed/vietjobs_clean.parquet"`
  - `load_clean(path: Path = CLEAN_PATH) -> pd.DataFrame`

- [ ] **Step 1: Viết test thất bại `test_clean_pipeline`** với DataFrame 4 dòng dựng tay: 1 dòng `country="Lào"` (bị loại), 2 dòng trùng hệt (còn 1), 1 dòng `salary_avg="300 triệu"`. Assert: `len(out) == 2`; `out.salary_outlier.sum() == 1`; `set(out.region) <= {"Hà Nội","TP.HCM","Khác"}`; `out.benefits_list.map(type).eq(list).all()`; dòng có `salary_min=0` nhưng `salary_avg="10 triệu"` → `salary_negotiable == False`.

- [ ] **Step 2: `pytest tests/test_cleaning.py::test_clean_pipeline -v` → FAIL**

- [ ] **Step 3: Cài đặt `clean`, `CLEAN_PATH`, `load_clean`**

- [ ] **Step 4: `pytest -v` → PASS toàn bộ**

- [ ] **Step 5: Tạo `notebooks/02_cleaning.ipynb`**: đọc raw → in shape/missing trước → `clean()` → bảng so sánh trước/sau (số dòng bị loại theo từng lý do, % thoả thuận, phân bố `experience_level`, `region`) → `to_parquet(CLEAN_PATH)`.

- [ ] **Step 6: Chạy `jupyter nbconvert --to notebook --execute --inplace notebooks/02_cleaning.ipynb`** → thành công, file parquet tồn tại, ~47.9k dòng.

- [ ] **Step 7: Commit** — `git commit -m "feat: cleaning pipeline and 02_cleaning notebook"`

---

### Task 3: Cập nhật repo nền (README, notebook 01, hồ sơ xin duyệt)

**Files:**
- Modify: `README.md`, `notebooks/01_collection_exploration.ipynb`, `LLM_USAGE.md`, `docs/HANDOVER_TIEN.md`
- Create: `docs/DATASET_PROPOSAL.md`

- [ ] **Step 1: README** — trạng thái "Đã chốt VietJobs, chờ giảng viên duyệt"; lệnh tải:
  `curl -L -o data/raw/VietJobs.csv https://huggingface.co/datasets/dinhieufam/VietJobs/resolve/main/VietJobs.csv`; trích dẫn bài báo LREC 2026; ghi chú license (code MIT, paper CC BY 4.0, dataset card không ghi license); thứ tự chạy notebook 01→08; `pytest` để kiểm tra.
- [ ] **Step 2: Notebook 01** — `DATA_FILE = RAW_DIR / "VietJobs.csv"`; thêm cell value_counts cho `category`, `experience_required`, `contract_type`, `country`.
- [ ] **Step 3: `docs/DATASET_PROPOSAL.md`** — nguồn, license, quy mô (48.092 × 18), danh sách cột, 6 câu hỏi (copy bảng mục 4 của spec). Tiến gửi giảng viên.
- [ ] **Step 4: Đánh dấu Việc 1–3 trong `HANDOVER_TIEN.md`, thêm dòng `LLM_USAGE.md` (25/11, Claude, chốt dữ liệu + spec + plan).**
- [ ] **Step 5: Chạy `jupyter nbconvert --execute --inplace notebooks/01_collection_exploration.ipynb`** → in `Shape: 48,092 rows x 18 columns`.
- [ ] **Step 6: Commit** — `git commit -m "docs: lock VietJobs dataset, proposal and README download steps"`

---

### Tasks 4–8: Notebook phân tích Q1–Q5

Mỗi notebook có cùng khung: (1) câu hỏi & động lực, (2) `df = load_clean()`, (3) xử lý riêng, (4) 2–4 hình lưu vào `reports/figures/qN_*.png`, (5) kiểm định thống kê nếu có, (6) **kết luận + hạn chế** (dữ liệu chỉ TopCV 2025; lương đăng tuyển ≠ lương thực). Lương dùng `salary_avg_num` với `~salary_outlier`, báo **trung vị**.

Bước chung cho mỗi task: viết notebook → `jupyter nbconvert --execute --inplace <nb>` chạy không lỗi → hình tồn tại trong `reports/figures/` → commit `feat: <nb>`.

| Task | Notebook | Người | Nội dung bắt buộc |
|---|---|---|---|
| 4 | `03_q1_salary_region_category.ipynb` | Đăng | boxplot lương theo `region`; heatmap trung vị lương `category × region`; Kruskal-Wallis giữa 3 vùng (`scipy.stats.kruskal`) |
| 5 | `04_q2_experience_salary.ipynb` | Đăng | trung vị lương theo `experience_level` (thứ tự cố định); OLS `log(salary) ~ experience_months` từng ngành (top 8 ngành) → bảng % tăng/năm = `exp(12·β)−1` |
| 6 | `05_q3_negotiable_salary.ipynb` | Tiến | tỉ lệ `salary_negotiable` theo `category`, `experience_level`, `region`; `scipy.stats.chi2_contingency` cho từng biến |
| 7 | `06_q4_benefits.ipynb` | Tiến | `explode("benefits_list")`, chuẩn hoá lower/strip, top 20; tỉ lệ top 10 phúc lợi theo nhóm lương (quartile); Spearman `n_benefits ~ salary_avg_num` |
| 8 | `07_q5_skills.ipynb` | Hiếu | `explode("technical_skills_list")`, lower/strip, top 15 mỗi ngành (top 6 ngành); với kỹ năng xuất hiện ≥ 100 tin: chênh lệch trung vị lương có/không kỹ năng, top 15 |

---

### Task 9: Mô hình dự đoán lương (`src/modeling.py`) — Q6

**Files:**
- Create: `src/modeling.py`, `tests/test_modeling.py`

**Interfaces:**
- Consumes: `load_clean()` (Task 2).
- Produces:
  - `FORBIDDEN = {"salary","salary_min","salary_max","salary_avg","salary_avg_num","salary_negotiable","salary_outlier"}`
  - `CAT_COLS = ["category","region","experience_level","contract_group"]`, `NUM_COLS = ["experience_months","n_benefits","n_technical_skills"]`, `TEXT_COL = "text"`
  - `prepare_xy(df) -> tuple[pd.DataFrame, pd.Series]` — lọc `~salary_negotiable & ~salary_outlier`; `text = job_title + " " + requirements_text`; `y = np.log(salary_avg_num)`; X chỉ gồm `CAT_COLS + NUM_COLS + [TEXT_COL]`
  - `make_models() -> dict[str, sklearn.pipeline.Pipeline]` — keys `"baseline"` (`DummyRegressor(strategy="median")`), `"ridge"` (ColumnTransformer: OneHot(CAT, handle_unknown="ignore") + StandardScaler(NUM) + `TfidfVectorizer(max_features=20000, ngram_range=(1,2), min_df=3)`(TEXT) → `Ridge(alpha=1.0)`), `"hgb"` (OneHot/Ordinal CAT + NUM + `TruncatedSVD(100)` của TF-IDF → `HistGradientBoostingRegressor(random_state=42)`)
  - `evaluate(models, X_train, X_test, y_train, y_test) -> pd.DataFrame` — index = tên mô hình; cột `MAE`, `RMSE`, `R2` tính trên **triệu VND** (`np.exp` của dự đoán và y)

- [ ] **Step 1: Viết test thất bại `tests/test_modeling.py`**

```python
def test_prepare_xy_no_leakage(small_clean_df):
    X, y = prepare_xy(small_clean_df)
    assert not (set(X.columns) & FORBIDDEN)
    assert y.notna().all() and len(X) == len(y)

def test_models_fit_and_evaluate(small_clean_df):
    X, y = prepare_xy(small_clean_df)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    res = evaluate(make_models(), Xtr, Xte, ytr, yte)
    assert list(res.columns) == ["MAE", "RMSE", "R2"]
    assert set(res.index) == {"baseline", "ridge", "hgb"}
```
  Fixture `small_clean_df`: `load_clean().sample(2000, random_state=42)` nếu parquet tồn tại, ngược lại `pytest.skip`. Đặt `min_df`/SVD đủ nhỏ cho fixture qua tham số `make_models(tfidf_min_df=3, svd_components=100)`.

- [ ] **Step 2: `pytest tests/test_modeling.py -v` → FAIL**
- [ ] **Step 3: Cài đặt `src/modeling.py`**
- [ ] **Step 4: `pytest -v` → PASS**
- [ ] **Step 5: Commit** — `git commit -m "feat: salary prediction pipelines with leakage test"`

---

### Task 10: Notebook Q6 (`08_q6_salary_prediction.ipynb`) — Hiếu

- [ ] **Step 1:** `prepare_xy` → split 80/20 `random_state=42` → `GridSearchCV` 5-fold trên train cho `ridge__regressor__alpha ∈ {0.3,1,3,10}` → `evaluate` → bảng so sánh 3 mô hình.
- [ ] **Step 2:** Giải thích: top 20 hệ số Ridge (tên feature từ `get_feature_names_out`), `permutation_importance` cho HGB trên test; hình residual vs dự đoán; MAE theo ngành.
- [ ] **Step 3:** Kết luận: mô hình tốt nhất phải có MAE thấp hơn baseline; nếu không, ghi rõ và phân tích lý do.
- [ ] **Step 4:** `jupyter nbconvert --execute --inplace` → chạy không lỗi; commit.

---

### Task 11: Báo cáo, slide, kiểm tra chạy lại (09–14/12)

**Files:** Create `reports/report.md` (xuất PDF), `reports/slides.pdf`; Modify `README.md`, `LLM_USAGE.md`

- [ ] **Step 1:** Báo cáo: giới thiệu dữ liệu, làm sạch (số liệu từ notebook 02), mỗi Q: câu hỏi → phương pháp → hình → kết luận, hạn chế chung, phân công, trích dẫn VietJobs.
- [ ] **Step 2:** Slide 12–15 trang dùng hình trong `reports/figures/`.
- [ ] **Step 3:** Review chéo: mỗi người đọc 2 notebook của người khác, ghi issue/comment.
- [ ] **Step 4:** Kiểm tra trên máy sạch: clone mới → `conda env create -f environment.yml` → tải CSV → `pytest` PASS → chạy notebook 01→08 bằng `nbconvert --execute` không lỗi.
- [ ] **Step 5:** Hoàn thiện `LLM_USAGE.md`, bảng thành viên (MSSV) trong README; commit + tag `v1.0-submission`.
