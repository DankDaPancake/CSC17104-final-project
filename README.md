# CSC17104 Final Project — Programming for Data Science

Đồ án cuối kỳ môn **CSC17104 – Lập trình cho Khoa học Dữ liệu** — Nhóm **drn<5** (3 thành viên).

## Trạng thái dự án
- **Bộ dữ liệu:** Nhóm đã chốt **VietJobs** (48.092 tin tuyển dụng TopCV, 18 cột) — chờ giảng viên duyệt (đề xuất: [docs/DATASET_PROPOSAL.md](docs/DATASET_PROPOSAL.md))
- **Thiết kế & kế hoạch:** [docs/superpowers/specs/](docs/superpowers/specs/) · [docs/superpowers/plans/](docs/superpowers/plans/)
- **Hạn nộp:** 15/12/2026

## Cấu trúc thư mục

```text
CSC17104-final-project/
├── data/
│   ├── raw/                  # VietJobs.csv (không commit)
│   └── processed/            # vietjobs_clean.parquet (sinh bởi notebook 02, không commit)
├── docs/                     # đề xuất dữ liệu, kế hoạch, thiết kế
├── notebooks/
│   ├── 01_collection_exploration.ipynb
│   ├── 02_cleaning.ipynb
│   ├── 03_q1_salary_region_category.ipynb   # Q1 – Đăng
│   ├── 04_q2_experience_salary.ipynb        # Q2 – Đăng
│   ├── 05_q3_negotiable_salary.ipynb        # Q3 – Tiến
│   ├── 06_q4_benefits.ipynb                 # Q4 – Tiến
│   ├── 07_q5_skills.ipynb                   # Q5 – Hiếu
│   └── 08_q6_salary_prediction.ipynb        # Q6 (ML) – Hiếu
├── src/                      # cleaning.py, modeling.py (logic dùng chung, có test)
├── tests/                    # pytest
├── scripts/                  # run_nb.py (chạy notebook), build_nb*.py (sinh notebook), build_slides.py
├── reports/                  # report.md (báo cáo nháp), slides.pdf, figures/
├── environment.yml
└── LLM_USAGE.md
```

## Thiết lập môi trường

Yêu cầu đã cài đặt [Miniconda](https://docs.conda.io/en/latest/miniconda.html) hoặc Anaconda.

```bash
# 1. Clone repository
git clone https://github.com/DankDaPancake/CSC17104-final-project.git
cd CSC17104-final-project

# 2. Tạo môi trường Conda
conda env create -f environment.yml

# 3. Kích hoạt môi trường
conda activate csc17104-final-project

# 4. Mở Jupyter Lab
jupyter lab
```

Nếu `environment.yml` có cập nhật mới:

```bash
conda env update -f environment.yml --prune
```

## Hướng dẫn tải dữ liệu

```bash
curl -L -o data/raw/VietJobs.csv https://huggingface.co/datasets/dinhieufam/VietJobs/resolve/main/VietJobs.csv
```

- **Nguồn:** Pham Dinh, H., Nguyen Huy, H., & El-Haj, M. (2026). *VietJobs: A Vietnamese Job Advertisement Dataset*. LREC 2026. [arXiv:2603.05262](https://arxiv.org/abs/2603.05262) · [GitHub](https://github.com/VinNLP/VietJobs) · [Hugging Face](https://huggingface.co/datasets/dinhieufam/VietJobs)
- **Giấy phép:** mã nguồn MIT, bài báo CC BY 4.0; trang dataset trên Hugging Face **không ghi license** → chỉ dùng cho mục đích học tập, có trích dẫn.

## Chạy lại toàn bộ

```bash
python -m pytest                         # kiểm tra hàm làm sạch & mô hình
python scripts/run_nb.py notebooks/0*.ipynb   # chạy notebook 01 → 08 theo thứ tự
python scripts/build_slides.py               # tạo reports/slides.pdf từ hình
```

Notebook 02 phải chạy trước 03–08 (tạo `data/processed/vietjobs_clean.parquet`).

## Thành viên nhóm (drn<5)

| Thành viên | MSSV | Phụ trách chính |
|---|---|---|
| Lý Huỳnh Minh Đăng | 24127272 | Khởi tạo repo/khung dự án & Q1, Q2 |
| Trần Minh Tiến | 24127130 | Tiếp nhận chốt dữ liệu/xin duyệt & Q3, Q4 |
| Trương Lê Trung Hiếu | 24127169 | Dựng pipeline phân tích & Q5, Q6 (ML) |
