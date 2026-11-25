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

- 29,2% tin để lương "Thoả thuận"; 24 tin lương ngoại lai (< 1 hoặc > 200 triệu/tháng) → **25.796 tin có lương hợp lệ**, trung vị 13,5 triệu/tháng.
- Lương = **trung điểm thật** của khoảng trong chuỗi `salary` (cột `salary_avg` gốc làm tròn xuống, vd. 8,5–9,0 → 8); khoảng có một cận bằng 0 ("tới X") dùng cận còn lại.
- Chuẩn hoá: kinh nghiệm → số tháng + 5 mức; địa điểm → tỉnh chính + 3 vùng (Hà Nội / TP.HCM / Khác); list kỹ năng/phúc lợi;
  phúc lợi (~73k cách viết) và kỹ năng (~29k) gom về 16 và 32 nhóm chuẩn bằng regex (`src/taxonomy.py`).
- Logic làm sạch, gom nhóm và mô hình có 44 test tự động (`pytest`).

## 3. Kết quả

### Q1 — Lương theo vùng và ngành (Đăng)
- Trung vị: Hà Nội 13,5 · TP.HCM 12,5 · tỉnh khác 12,5 triệu/tháng (Kruskal-Wallis p ≈ 1·10⁻²⁹; Hà Nội vs TP.HCM Mann-Whitney p ≈ 3·10⁻²⁷) — có ý nghĩa thống kê nhưng nhỏ về độ lớn. Quận/huyện của Hà Nội và TP.HCM được gộp về thành phố tương ứng.
- Ngành cao nhất: CNTT 18,0, Xây dựng/BĐS 16,0; thấp nhất: "Nghề khác" 11,0.
- Chênh lệch giữa ngành (≈ 7 triệu) lớn hơn nhiều so với giữa vùng (≈ 1 triệu); CNTT tại Hà Nội cao nhất (20 triệu, so với 15,5 ở TP.HCM) — CNTT cũng là ngành chênh lệch Hà Nội − tỉnh khác lớn nhất (6 triệu).
- Hình: `q1_salary_by_region.png`, `q1_salary_by_category.png`, `q1_heatmap_category_region.png`.

### Q2 — Kinh nghiệm và lương (Đăng)
- Trung vị: Không yêu cầu 10 → 1–2 năm 14 → 3–5 năm 20 → trên 5 năm 38 triệu (nhóm cuối chỉ 59 tin có lương — cần thận trọng).
- Mỗi năm kinh nghiệm yêu cầu ≈ +21,1% lương đăng tuyển (CI95 bootstrap 20,5–21,7%; hồi quy log-lương, R² ≈ 0,21).
- Tăng nhanh nhất: Marketing/Truyền thông (≈ 33%/năm, CI95 31–36); chậm nhất: Xây dựng/BĐS (≈ 12%/năm, CI95 10–13) — hai khoảng không chồng nhau.

### Q3 — Tin không công bố lương (Tiến)
- 29,2% tin để "Thoả thuận"; cao nhất ở "Nghề khác" (44%) và CNTT (42%), thấp nhất ở Giáo dục (24%).
- Từ mức 1–2 năm trở lên, kinh nghiệm càng cao càng hay giấu lương: 28% → 41% (3–5 năm) → 69% (trên 5 năm); riêng "Dưới 1 năm" thấp nhất (15%), "Không yêu cầu" 26%.
- TP.HCM (35%) và tỉnh khác (36%) giấu lương nhiều hơn Hà Nội (22%); thực tập (47%) cao hơn toàn thời gian (29%).
- Mọi biến đều có liên hệ có ý nghĩa (chi-square) nhưng **yếu**: vùng (Cramér's V ≈ 0,150) và mức kinh nghiệm (≈ 0,147) gần như ngang nhau, ngành ≈ 0,09.

### Q4 — Phúc lợi (Tiến)
- Phổ biến nhất: bảo hiểm bắt buộc (71% tin), du lịch/nghỉ mát (44%), lương/thưởng tháng 13 (41%).
- Tương quan số nhóm phúc lợi – lương yếu (Spearman ρ ≈ 0,14).
- Khác biệt lớn nhất giữa nhóm lương cao và thấp: thưởng hiệu quả/KPI/doanh số (+14 điểm %); đào tạo lại phổ biến hơn ở nhóm lương thấp (−5 điểm %).

### Q5 — Kỹ năng (Thành viên 3)
- Được yêu cầu nhiều nhất: Excel/tin học văn phòng, phần mềm kế toán/MISA, AutoCAD.
- So sánh **trong cùng ngành** (CI95 bootstrap), kỹ năng gắn với lương cao hơn nhất: SQL +7,2 triệu (5,8…9,0; n=224), Python +6,2 (4,1…10,3; n=103), JavaScript +5,5 (2,5…8,0; n=123). Canva thấp nhất −1,9 (−2,2…−1,4).
- 13 kỹ năng có CI95 hoàn toàn dương, gồm cả Phân tích dữ liệu, Quản lý dự án, AutoCAD, Revit, PLC.
- "AI" đứng cạnh Photoshop/InDesign… được hiểu là Adobe Illustrator, không phải trí tuệ nhân tạo.

### Q6 — Dự đoán lương (Thành viên 3)
| Mô hình | MAE (triệu) | RMSE | R² |
|---|---|---|---|
| Baseline (trung vị) | 5,76 | 11,57 | −0,04 |
| **Ridge (one-hot + TF-IDF)** | **3,99** | **9,30** | **0,33** |
| HistGradientBoosting (SVD) | 4,25 | 9,71 | 0,27 |

- Chia train/test **theo nhóm văn bản** (tin đăng lại có văn bản giống hệt luôn nằm cùng một phía; 0 văn bản trùng giữa train và test), chọn `alpha` bằng GroupKFold 5-fold.
- Ridge giảm 31% sai số so với baseline. Văn bản tin tuyển dụng là feature quan trọng nhất, sau đó là số tháng kinh nghiệm.
- Từ khoá tăng lương: "trưởng phòng", "trưởng", "manager", "giám đốc", "kế toán trưởng"; giảm lương: "thực tập", "tập sinh", "intern", "ctv".
- 0,6% tin ghi mức lương ngay trong văn bản (vd. "thu nhập upto 20 triệu") — là nội dung thật của tin, không phải rò rỉ từ cột lương.

## 4. Hạn chế
- Chỉ một nền tảng (TopCV) trong 2025; lương **đăng tuyển** ≠ lương thực nhận; 29% tin thiếu lương (không ngẫu nhiên — xem Q3).
- Gom nhóm phúc lợi/kỹ năng bằng regex có thể bỏ sót cách viết hiếm (kỹ năng: 59% tin khớp ít nhất một nhóm).
- Các chênh lệch là tương quan, không phải quan hệ nhân quả.
- Lương đăng tuyển là trung điểm khoảng min–max, không phản ánh phân bố thực trong khoảng.

## 5. Tái lập
```bash
conda env create -f environment.yml && conda activate csc17104-final-project
curl -L -o data/raw/VietJobs.csv https://huggingface.co/datasets/dinhieufam/VietJobs/resolve/main/VietJobs.csv
python scripts/run_nb.py notebooks/01_collection_exploration.ipynb notebooks/02_cleaning.ipynb
python -m pytest
python scripts/run_nb.py notebooks/0[3-8]*.ipynb
```
