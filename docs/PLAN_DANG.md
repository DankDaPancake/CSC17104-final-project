# Kế hoạch khởi động dự án — Phần việc của Đăng (21/11 – 24/11/2026)

- **Môn học:** CSC17104 – Lập trình cho Khoa học Dữ liệu
- **Quy mô nhóm:** 3 thành viên (6 câu hỏi nghiên cứu, mỗi người 2 câu, ít nhất 1 câu ML)
- **Deadline đồ án:** 15/12/2026
- **Repository:** `csc17104-final-project`
- **Mục tiêu giai đoạn 1:** Chốt phương án bộ dữ liệu để xin giảng viên duyệt và bàn giao một repository hoàn chỉnh mà cả 3 thành viên có thể clone và chạy lại được.

---

## Lộ trình chi tiết

### Ngày 1 — 21/11: Khởi tạo repository & khung dự án
- [x] Khởi tạo repo `csc17104-final-project` (local git)
- [x] Tạo cấu trúc thư mục: `docs/`, `notebooks/`, `data/raw/`, `data/processed/`
- [x] Tạo các tệp nền tảng: `README.md`, `.gitignore`, `environment.yml`, `LLM_USAGE.md`
- [x] Tạo notebook khung `notebooks/01_collection_exploration.ipynb`
- [x] Tạo repo trên GitHub, push commit đầu tiên và mời 2 thành viên còn lại

> **Cập nhật bàn giao (23/11):** Các đầu việc còn lại từ Ngày 2 đến Ngày 4 (kiểm tra giấy phép VietJobs, gửi giảng viên duyệt / phương án dự phòng, cập nhật `README.md` và hoàn thiện bước đọc dữ liệu trong notebook đầu tiên) đã được bàn giao cho **Tiến**. Chi tiết xem tại [HANDOVER_TIEN.md](HANDOVER_TIEN.md).

**Kết quả cần có:** Cả nhóm có quyền truy cập repo, có hướng dẫn tạo môi trường Conda và quy tắc bỏ qua tệp dữ liệu lớn.

---

### Ngày 2 — 22/11: Kiểm tra bộ dữ liệu ưu tiên (VietJobs)
- [ ] Xác minh nguồn gốc chính thức của bộ dữ liệu **VietJobs** (~48.000 tin tuyển dụng từ TopCV)
- [ ] Kiểm tra và ghi lại **giấy phép (license)** của chính bộ dữ liệu (không chỉ giấy phép của mã nguồn/repo đi kèm)
- [ ] Tải thử dữ liệu về `data/raw/` và chạy kiểm tra nhanh:
  - Số dòng, số cột thực tế
  - Các cột liên quan đến lương, địa điểm, kinh nghiệm, kỹ năng, phúc lợi, loại hợp đồng
  - Tỉ lệ dữ liệu thiếu và định dạng thô của các cột quan trọng
- [ ] Ghi chú lại kết quả kiểm tra vào tài liệu/notebook để dùng cho phần thu thập dữ liệu

**Kết quả cần có:** Đủ căn cứ để quyết định có dùng VietJobs hay không.

---

### Ngày 3 — 23/11: Chuẩn bị hồ sơ xin duyệt / phương án dự phòng
- [ ] **Nếu đã xác nhận giấy phép VietJobs:** Soạn và gửi giảng viên đề xuất gồm nguồn gốc, giấy phép, quy mô (số dòng/cột) và các hướng phân tích chính (bao gồm bài toán ML dự đoán lương đăng tuyển).
- [ ] **Nếu giấy phép VietJobs vẫn chưa rõ ràng:** Chuẩn bị đầy đủ thông tin (nguồn, giấy phép, quy mô, hướng câu hỏi) cho phương án dự phòng **HealthyAir TP.HCM + Open-Meteo**.

**Kết quả cần có:** Đã gửi hồ sơ xin duyệt hoặc đã sẵn sàng phương án dự phòng.

---

### Ngày 4 — 24/11: Chốt trạng thái duyệt & bàn giao cho nhóm
- [ ] Cập nhật trạng thái duyệt bộ dữ liệu trong `README.md`
- [ ] Nếu đến 24/11 vẫn chưa xác nhận được giấy phép VietJobs → chuyển hẳn sang phương án dự phòng **HealthyAir + Open-Meteo** và gửi giảng viên duyệt
- [ ] Hoàn thiện bước đọc dữ liệu và kiểm tra kích thước trong `notebooks/01_collection_exploration.ipynb`
- [ ] Nhờ ít nhất 1 thành viên khác clone repo, tạo môi trường từ `environment.yml` và chạy thử notebook đầu tiên

**Kết quả bàn giao cho nhóm:**
1. Link GitHub repo `csc17104-final-project`
2. Trạng thái duyệt bộ dữ liệu
3. Hướng dẫn tải dữ liệu vào `data/raw/`
4. Đường dẫn notebook đầu tiên (`notebooks/01_collection_exploration.ipynb`)

> **Phạm vi kết thúc:** Phần việc khởi động của Đăng kết thúc sau bước bàn giao này. Việc làm sạch chi tiết và chốt 6 câu hỏi (cùng ma trận tiêu chí D1–D6) sẽ do cả nhóm thực hiện ở giai đoạn tiếp theo (25–29/11).
