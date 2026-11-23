# Tài liệu bàn giao cho Tiến — Hoàn thiện giai đoạn khởi động (Hạn nội bộ: 24/11/2026)

- **Người bàn giao:** Đăng
- **Người tiếp nhận:** Tiến
- **Repository:** https://github.com/DankDaPancake/CSC17104-final-project
- **Nhánh làm việc hiện tại:** `main`
- **Hạn nội bộ giai đoạn 1:** 24/11/2026 (để cả nhóm bắt đầu khám phá & làm sạch chung từ 25/11)

---

## 1. Phần Đăng đã hoàn thành (21/11)
- [x] Khởi tạo repo GitHub `CSC17104-final-project` và mời đủ 2 thành viên còn lại
- [x] Thiết lập cấu trúc thư mục: `docs/`, `notebooks/`, `data/raw/`, `data/processed/`
- [x] Tạo các tệp nền tảng: `README.md`, `.gitignore` (đã chặn commit tệp dữ liệu lớn), `environment.yml`, `LLM_USAGE.md`
- [x] Tạo notebook khung [notebooks/01_collection_exploration.ipynb](../notebooks/01_collection_exploration.ipynb) sẵn code kiểm tra file, kích thước (`shape`), kiểu dữ liệu và tỉ lệ thiếu

---

## 2. Phần bàn giao cho Tiến xử lý (22/11 – 24/11)

### Việc 1 — Kiểm tra bộ dữ liệu ưu tiên: VietJobs
- [ ] Xác minh nguồn gốc chính thức và cách thu thập của **VietJobs** (~48.000 tin tuyển dụng từ TopCV).
- [ ] Kiểm tra và ghi rõ **giấy phép (license) của chính bộ dữ liệu** (lưu ý: cần giấy phép của dữ liệu, không chỉ giấy phép của code repo đi kèm).
- [ ] Tải thử dữ liệu về thư mục `data/raw/` (không commit file dữ liệu lên Git).
- [ ] Chạy thử `notebooks/01_collection_exploration.ipynb` để kiểm tra:
  - Số dòng, số cột thực tế (yêu cầu môn học: >= 3.000 dòng, >= 10 cột)
  - Các cột quan trọng: lương, địa điểm, kinh nghiệm, kỹ năng, phúc lợi, loại hợp đồng
  - Tỉ lệ dữ liệu thiếu và định dạng thô

### Việc 2 — Gửi giảng viên duyệt (hoặc chuyển phương án dự phòng)
- [ ] **Nếu đã xác nhận giấy phép VietJobs:** Gửi giảng viên đề xuất kèm nguồn, giấy phép, quy mô (số dòng/cột) và vài hướng phân tích chính (bao gồm bài toán ML dự đoán lương đăng tuyển).
- [ ] **Nếu đến 24/11 vẫn chưa xác nhận được giấy phép VietJobs:** Chuyển sang phương án dự phòng **HealthyAir TP.HCM + Open-Meteo**, tổng hợp nguồn/giấy phép/quy mô tương tự và gửi giảng viên duyệt.

### Việc 3 — Cập nhật repo & xác nhận chạy được
- [ ] Cập nhật **trạng thái duyệt** và **hướng dẫn/link tải dữ liệu** vào `README.md`.
- [ ] Cập nhật tên tệp dữ liệu (`DATA_FILE`) trong `notebooks/01_collection_exploration.ipynb` và chạy kiểm tra lại từ đầu đến cuối.
- [ ] Xác nhận tạo môi trường từ `environment.yml` hoạt động bình thường trên máy của Tiến (và báo nhóm nếu cần bổ sung thư viện).

---

## 3. Cách bắt đầu nhanh trên máy Tiến

```bash
# 1. Clone repo
git clone https://github.com/DankDaPancake/CSC17104-final-project.git
cd CSC17104-final-project

# 2. Tạo và kích hoạt môi trường Conda
conda env create -f environment.yml
conda activate csc17104-final-project

# 3. Mở Jupyter Lab để chạy notebook đầu tiên
jupyter lab
```

> **Lưu ý Git:** Không commit các tệp dữ liệu (`.csv`, `.xlsx`, `.parquet`, `.zip`...) lên repo — `.gitignore` đã cấu hình sẵn để bỏ qua các tệp trong `data/raw/` và `data/processed/`.
