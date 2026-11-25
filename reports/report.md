# Báo cáo đồ án CSC17104 — Thị trường tuyển dụng Việt Nam qua dữ liệu VietJobs

> **Bản nháp sinh tự động (25/11/2026)** từ kết quả notebook 01–08. Mỗi thành viên cần viết lại phần nhận xét
> của câu hỏi mình phụ trách bằng lời của mình, kiểm tra số liệu, và bổ sung MSSV.

## 1. Dữ liệu
- **Nguồn:** VietJobs (Pham Dinh, Nguyen Huy & El-Haj, LREC 2026) — 48.092 tin tuyển dụng TopCV năm 2025, 18 cột.
- **Giấy phép:** mã nguồn MIT, bài báo CC BY 4.0; trang dataset không ghi license → chỉ dùng cho học tập, không phân phối lại.

## 2. Làm sạch (`notebooks/02_cleaning.ipynb`, `src/cleaning.py`)
| Bước | Số dòng | Bị loại |
|---|---|---|
| Dữ liệu gốc | 48.092 | — |
| Chỉ giữ Việt Nam | 47.957 | 135 |
| Bỏ tin đăng trùng (tên việc + địa điểm + mô tả) | **36.457** | 11.500 |

- 29,2% tin để lương "Thoả thuận"; 24 tin lương ngoại lai (< 1 hoặc > 200 triệu/tháng) → **25.796 tin có lương hợp lệ**, trung vị 13 triệu/tháng.
- Chuẩn hoá: kinh nghiệm → số tháng + 5 mức; địa điểm → tỉnh chính + 3 vùng (Hà Nội / TP.HCM / Khác); list kỹ năng/phúc lợi;
  phúc lợi (~73k cách viết) và kỹ năng (~29k) gom về 16 và 32 nhóm chuẩn bằng regex (`src/taxonomy.py`).
- Logic làm sạch có 18 test tự động (`pytest`).

## 3. Kết quả

### Q1 — Lương theo vùng và ngành (Đăng)
- Trung vị: Hà Nội 13,0 · TP.HCM 12,0 · tỉnh khác 12,0 triệu/tháng (Kruskal-Wallis p ≈ 3·10⁻²⁸).
- Ngành cao nhất: CNTT 18,0, Xây dựng/BĐS 16,0; thấp nhất: nhóm "Khác" 11,0.
- Chênh lệch giữa ngành (≈ 7 triệu) lớn hơn nhiều so với giữa vùng (≈ 1 triệu); CNTT tại Hà Nội cao nhất (20 triệu).
- Hình: `q1_salary_by_region.png`, `q1_salary_by_category.png`, `q1_heatmap_category_region.png`.

### Q2 — Kinh nghiệm và lương (Đăng)
- Trung vị: Không yêu cầu 10 → 1–2 năm 13 → 3–5 năm 19 → trên 5 năm 37 triệu.
- Mỗi năm kinh nghiệm yêu cầu ≈ +21,8% lương đăng tuyển (hồi quy log-lương, R² ≈ 0,20).
- Tăng nhanh nhất: Marketing/Truyền thông (≈ 34,5%/năm); chậm nhất: Xây dựng/BĐS (≈ 12%/năm).

### Q3 — Tin không công bố lương (Tiến)
- 29,2% tin để "Thoả thuận"; cao nhất ở nhóm "Khác" (44%) và CNTT (42%), thấp nhất ở Giáo dục (24%).
- Vị trí càng cao càng hay giấu lương: "Không yêu cầu" 26% → "Trên 5 năm" 69%.
- Mọi biến đều có liên hệ có ý nghĩa (chi-square), mạnh nhất là mức kinh nghiệm (Cramér's V ≈ 0,15).

### Q4 — Phúc lợi (Tiến)
- Phổ biến nhất: bảo hiểm bắt buộc (71% tin), du lịch/nghỉ mát (44%), thưởng lễ tết (43%).
- Tương quan số nhóm phúc lợi – lương yếu (Spearman ρ ≈ 0,14).
- Khác biệt lớn nhất giữa nhóm lương cao và thấp: thưởng hiệu quả/KPI/doanh số (+14 điểm %); đào tạo lại phổ biến hơn ở nhóm lương thấp (−5 điểm %).

### Q5 — Kỹ năng (Thành viên 3)
- Được yêu cầu nhiều nhất: Excel/tin học văn phòng, phần mềm kế toán/MISA, AutoCAD.
- So sánh **trong cùng ngành**, kỹ năng gắn với lương cao hơn nhất: SQL (+7,5 triệu), Python (+6,2), JavaScript (+6,0); Canva thấp nhất (−1,5).

### Q6 — Dự đoán lương (Thành viên 3)
| Mô hình | MAE (triệu) | RMSE | R² |
|---|---|---|---|
| Baseline (trung vị) | 5,63 | 10,81 | −0,05 |
| **Ridge (one-hot + TF-IDF)** | **3,80** | **8,42** | **0,37** |
| HistGradientBoosting (SVD) | 4,03 | 8,73 | 0,32 |

- Ridge giảm 32% sai số so với baseline. Văn bản tin tuyển dụng là feature quan trọng nhất, sau đó là số tháng kinh nghiệm.
- Từ khoá tăng lương: "trưởng phòng", "manager", "giám đốc", "kinh doanh"; giảm lương: "thực tập", "tập sinh", "intern", "ctv".

## 4. Hạn chế
- Chỉ một nền tảng (TopCV) trong 2025; lương **đăng tuyển** ≠ lương thực nhận; 29% tin thiếu lương (không ngẫu nhiên — xem Q3).
- Gom nhóm phúc lợi/kỹ năng bằng regex có thể bỏ sót cách viết hiếm (kỹ năng: 59% tin khớp ít nhất một nhóm).
- Các chênh lệch là tương quan, không phải quan hệ nhân quả.

## 5. Tái lập
```bash
conda env create -f environment.yml && conda activate csc17104-final-project
curl -L -o data/raw/VietJobs.csv https://huggingface.co/datasets/dinhieufam/VietJobs/resolve/main/VietJobs.csv
python scripts/run_nb.py notebooks/01_collection_exploration.ipynb notebooks/02_cleaning.ipynb
python -m pytest
python scripts/run_nb.py notebooks/0[3-8]*.ipynb
```
