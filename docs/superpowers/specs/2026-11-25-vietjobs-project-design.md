# Thiết kế đồ án CSC17104 — Phân tích thị trường tuyển dụng Việt Nam (VietJobs)

- **Ngày:** 25/11/2026 — **Hạn nộp:** 15/12/2026
- **Nhóm:** Đăng, Tiến, Hiếu (mỗi người 2 câu hỏi, ≥ 1 câu ML)
- **Trạng thái:** Nhóm đã duyệt (25/11). Chờ giảng viên duyệt bộ dữ liệu.

## 1. Mục tiêu & lý do
Trả lời 6 câu hỏi về lương, kinh nghiệm, phúc lợi, kỹ năng và dự đoán lương trên dữ liệu tin tuyển dụng thật, với một pipeline **chạy lại được từ đầu** (clone → tải dữ liệu → chạy notebook theo thứ tự).

- **Mục tiêu:** dữ liệu sạch dùng chung; 6 câu hỏi có hình + kết luận; 1 mô hình ML đánh giá đúng cách; báo cáo + slide.
- **Không làm:** thu thập thêm dữ liệu (crawl), deploy mô hình, deep learning/LLM fine-tune.
- **Thất bại dù "chạy được":** mỗi người làm sạch một kiểu → số liệu mâu thuẫn; rò rỉ dữ liệu trong ML (vd. dùng `salary_min/max` làm feature); kết luận vượt quá dữ liệu (dữ liệu chỉ từ TopCV, 07/2025).

## 2. Dữ liệu
- **Nguồn:** VietJobs (Pham Dinh, Nguyen Huy, El-Haj — VinUniversity, LREC 2026, arXiv 2603.05262), tin tuyển dụng TopCV 2025.
- **Tải:** `https://huggingface.co/datasets/dinhieufam/VietJobs/resolve/main/VietJobs.csv` → `data/raw/VietJobs.csv` (~103 MB, không commit).
- **Quy mô:** 48.092 dòng × 18 cột.
- **Giấy phép:** code MIT (GitHub), bài báo CC BY 4.0; **trang dataset HF không ghi license** → nêu rõ với giảng viên, trích dẫn bài báo, chỉ dùng cho mục đích học tập.

### Vấn đề cần làm sạch (đã quan sát)
| Cột | Vấn đề | Cách xử lý |
|---|---|---|
| `salary_min/max/avg` | 28,6% "Thoả thuận" lưu là 0; `salary_avg` là chuỗi "12 triệu" | cờ `salary_negotiable`; số hoá `salary_avg` (triệu VND), NaN khi thoả thuận |
| `experience_required` | chuỗi "6 tháng", "2 năm", "Không yêu cầu" | `experience_months` (số), "Không yêu cầu" = 0; thêm `experience_level` (nhóm) |
| `location` | 984 giá trị; "hà đông" tách khỏi Hà Nội; nhiều tỉnh/1 tin | `location_primary` + `region` (Hà Nội / TP.HCM / Khác); cờ `multi_location` |
| `country` | ~135 tin ngoài Việt Nam | lọc giữ Việt Nam |
| `technical_skills`, `soft_skills`, `benefits`, `qualifications` | list dạng chuỗi | parse thành list (`ast.literal_eval`), đếm số phần tử |
| `contract_type` | tổ hợp hiếm | gộp nhóm hiếm vào "Khác" |
| Toàn bảng | có thể trùng tin | kiểm tra & bỏ trùng |

## 3. Cách tiếp cận
- **Đã chọn — Làm sạch tập trung:** 1 notebook `02_cleaning.ipynb` xuất `data/processed/vietjobs_clean.parquet`; mọi notebook phân tích chỉ đọc file này. Hàm dùng lại đặt trong `src/` (vd. `src/cleaning.py`).
- **Đã loại — Mỗi người tự làm sạch:** nhanh lúc đầu nhưng số liệu giữa các câu hỏi lệch nhau.
- **Đã loại — Pipeline script thuần (không notebook):** không phù hợp yêu cầu môn học/trình bày.

## 4. Sáu câu hỏi
| # | Người | Câu hỏi | Phương pháp chính |
|---|---|---|---|
| Q1 | Đăng | Lương khác nhau thế nào theo vùng (HN/HCM/khác) và ngành? | groupby, boxplot/heatmap, kiểm định (Kruskal-Wallis) |
| Q2 | Đăng | Mỗi năm kinh nghiệm tăng lương bao nhiêu, có khác giữa ngành? | trung vị theo mức KN, hồi quy log-lương ~ KN × ngành |
| Q3 | Tiến | Tin "Thoả thuận" tập trung ở ngành / mức KN / vùng nào? | tỉ lệ theo nhóm, chi-square |
| Q4 | Tiến | Phúc lợi nào phổ biến; lương cao có kèm nhiều phúc lợi hơn? | explode list, top-N, tương quan số phúc lợi ~ lương |
| Q5 | Hiếu | Kỹ năng nào được tuyển nhiều theo ngành; kỹ năng nào gắn lương cao? | explode + chuẩn hoá kỹ năng, top-N, chênh lệch trung vị lương |
| Q6 (ML) | Hiếu | Dự đoán `salary_avg` từ thuộc tính + văn bản | baseline (trung vị theo ngành) vs Ridge (TF-IDF + one-hot) vs Gradient Boosting; MAE/RMSE/R² trên test; giải thích feature |

**Quy tắc ML (Q6):** chỉ dùng tin có lương; target `log(salary_avg)`; **không** dùng `salary`, `salary_min`, `salary_max` làm feature; chia train/test trước mọi fit (TF-IDF fit trên train); `random_state=42`.

## 5. Cấu trúc repo đích
```
notebooks/
  01_collection_exploration.ipynb   # đọc raw, tổng quan
  02_cleaning.ipynb                 # → data/processed/vietjobs_clean.parquet
  03_q1_salary_region_category.ipynb
  04_q2_experience_salary.ipynb
  05_q3_negotiable_salary.ipynb
  06_q4_benefits.ipynb
  07_q5_skills.ipynb
  08_q6_salary_prediction.ipynb
src/cleaning.py                      # hàm làm sạch dùng chung
reports/figures/                     # hình xuất cho báo cáo/slide
reports/report.(md|pdf), slides
```

## 6. Lịch
| Thời gian | Việc | Phụ trách |
|---|---|---|
| 25/11 | Gửi giảng viên đề xuất (nguồn, license, quy mô, 6 câu hỏi); cập nhật README + notebook 01 | Tiến |
| 25–29/11 | `src/cleaning.py` + `02_cleaning.ipynb`; chốt 6 câu hỏi | Cả nhóm (Đăng chủ trì) |
| 30/11–08/12 | Notebook 03–08 | Mỗi người 2 notebook |
| 09–12/12 | Báo cáo, slide, review chéo, cập nhật `LLM_USAGE.md` | Cả nhóm |
| 13–14/12 | Dự phòng; chạy lại toàn bộ trên máy sạch | Cả nhóm |
| 15/12 | Nộp | — |

## 7. Để lại cho người thực hiện
- Ngưỡng gộp nhóm hiếm, cách chuẩn hoá tên kỹ năng, lựa chọn biểu đồ cụ thể.
- Siêu tham số mô hình (tune nhẹ bằng CV trên train).
- Tiêu chí chấm D1–D6 chưa có trong repo → khi có, đối chiếu lại mục 4–6.
