# CSC17104 Final Project — Programming for Data Science

Đồ án cuối kỳ môn **CSC17104 – Lập trình cho Khoa học Dữ liệu** (Nhóm 3 thành viên).

## Trạng thái dự án
- **Trạng thái bộ dữ liệu:** Đang kiểm tra giấy phép & chờ giảng viên duyệt
  - **Phương án ưu tiên:** VietJobs (~48.000 tin tuyển dụng từ TopCV)
  - **Phương án dự phòng:** HealthyAir TP.HCM + Open-Meteo
- **Hạn nộp:** 15/12/2026

## Cấu trúc thư mục

```text
csc17104-final-project/
├── data/
│   ├── raw/              # Dữ liệu gốc (không commit lên Git)
│   └── processed/        # Dữ liệu sau khi làm sạch (không commit lên Git)
├── docs/
│   ├── PLAN_DANG.md      # Kế hoạch khởi động dự án (21/11 – 24/11)
│   └── HANDOVER_TIEN.md  # Tài liệu bàn giao phần việc còn lại cho Tiến
├── notebooks/
│   └── 01_collection_exploration.ipynb
├── environment.yml       # Môi trường Conda
├── LLM_USAGE.md          # Nhật ký sử dụng công cụ LLM
├── .gitignore
└── README.md
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

*(Sẽ cập nhật link tải trực tiếp và tên tệp chuẩn sau khi chốt và được giảng viên duyệt bộ dữ liệu vào 24/11).*

Đặt các tệp dữ liệu gốc vào thư mục `data/raw/`.

## Thành viên nhóm

| Thành viên | MSSV | Phụ trách chính |
|---|---|---|
| Đăng | TBD | Khởi tạo repo/khung dự án & 2 câu hỏi phân tích |
| Tiến | TBD | Tiếp nhận chốt dữ liệu/xin duyệt (22–24/11) & 2 câu hỏi phân tích |
| Thành viên 3 | TBD | 2 câu hỏi phân tích |
