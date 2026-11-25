# Đề xuất bộ dữ liệu — Nhóm CSC17104 (gửi giảng viên)

## 1. Bộ dữ liệu: VietJobs
- **Mô tả:** 48.092 tin tuyển dụng tiếng Việt thu thập từ TopCV năm 2025, phủ 34 tỉnh/thành, 16 nhóm ngành.
- **Nguồn chính thức:** Pham Dinh, H., Nguyen Huy, H., & El-Haj, M. (2026). *VietJobs: A Vietnamese Job Advertisement Dataset*. LREC 2026 (VinUniversity). arXiv:2603.05262.
  - Bài báo: https://aclanthology.org/2026.lrec-1.501/
  - Mã nguồn: https://github.com/VinNLP/VietJobs
  - Dữ liệu: https://huggingface.co/datasets/dinhieufam/VietJobs (`VietJobs.csv`, ~103 MB)
- **Giấy phép:** mã nguồn MIT; bài báo CC BY 4.0. **Trang dataset trên Hugging Face không ghi giấy phép riêng** — nhóm sử dụng cho mục đích học tập, không phân phối lại dữ liệu (không commit lên Git), và trích dẫn bài báo đầy đủ.

## 2. Quy mô & cấu trúc
**48.092 dòng × 18 cột** (đạt yêu cầu ≥ 3.000 dòng, ≥ 10 cột). Sau làm sạch (chỉ Việt Nam, bỏ tin đăng trùng): 36.457 dòng.

| Nhóm | Cột |
|---|---|
| Công việc | `job_title`, `category` (16 ngành), `contract_type`, `working_hours` |
| Địa điểm | `location`, `country` |
| Yêu cầu | `experience_required`, `qualifications`, `technical_skills`, `soft_skills`, `languages_required`, `requirements_text` |
| Lương | `salary`, `salary_min`, `salary_max`, `salary_avg` (triệu VND; 28,5% "Thoả thuận") |
| Khác | `benefits`, `description` |

## 3. Sáu câu hỏi nghiên cứu
| # | Người | Câu hỏi |
|---|---|---|
| Q1 | Đăng | Lương khác nhau thế nào theo vùng (Hà Nội / TP.HCM / tỉnh khác) và theo ngành? |
| Q2 | Đăng | Mỗi năm kinh nghiệm làm tăng lương bao nhiêu, và mức tăng có khác giữa các ngành? |
| Q3 | Tiến | Tin để lương "Thoả thuận" tập trung ở ngành / mức kinh nghiệm / vùng nào? |
| Q4 | Tiến | Phúc lợi nào phổ biến nhất; lương cao có đi kèm nhiều phúc lợi hơn không? |
| Q5 | Thành viên 3 | Kỹ năng nào được tuyển nhiều nhất theo ngành; kỹ năng nào gắn với lương cao hơn? |
| Q6 (ML) | Thành viên 3 | Dự đoán mức lương đăng tuyển từ ngành, vùng, kinh nghiệm, loại hợp đồng và văn bản tin tuyển dụng (baseline vs Ridge vs Gradient Boosting). |
