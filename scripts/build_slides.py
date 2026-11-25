"""Sinh slide PDF (16:9) từ hình trong reports/figures và số liệu trong report.

Chạy SAU khi notebook 02–08 đã chạy: python scripts/build_slides.py
Kết quả: reports/slides.pdf — bản nháp, nhóm chỉnh sửa nội dung/lời thuyết trình.
"""
from pathlib import Path

import textwrap

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "figures"
OUT = ROOT / "reports" / "slides.pdf"
W, H = 13.33, 7.5

SLIDES = [
    ("title", "Thị trường tuyển dụng Việt Nam qua dữ liệu VietJobs",
     ["CSC17104 – Lập trình cho Khoa học Dữ liệu", "Nhóm: Đăng · Tiến · Thành viên 3", "12/2026"]),
    ("bullets", "Dữ liệu & làm sạch", [
        "VietJobs (LREC 2026): 48.092 tin tuyển dụng TopCV năm 2025, 18 cột",
        "Lọc Việt Nam, bỏ 11.500 tin đăng trùng → 36.457 tin",
        "29,2% tin để lương “Thoả thuận”; 25.796 tin có lương hợp lệ (trung vị 13,5 triệu/tháng)",
        "Chuẩn hoá: lương = trung điểm khoảng; kinh nghiệm → tháng; quận/huyện → thành phố",
        "Phúc lợi (~73k cách viết) → 16 nhóm; kỹ năng (~29k) → 32 nhóm (regex, có test)",
        "44 test tự động; toàn bộ notebook chạy lại được từ đầu",
    ]),
    ("figure", "Q1. Lương theo ngành × vùng", "q1_heatmap_category_region.png",
     ["Hà Nội 13,5 · TP.HCM 12,5 · tỉnh khác 12,5 triệu",
      "Chênh lệch ngành (~7 tr) ≫ chênh lệch vùng (~1 tr)",
      "CNTT Hà Nội cao nhất: 20 triệu"]),
    ("figure", "Q2. Kinh nghiệm và lương", "q2_growth_by_category.png",
     ["+21% lương / năm kinh nghiệm yêu cầu (CI95 20,5–21,7)",
      "Marketing tăng nhanh nhất (~33%/năm)",
      "Xây dựng/BĐS chậm nhất (~12%/năm)",
      "R² ≈ 0,21 — kinh nghiệm chỉ là một phần"]),
    ("figure", "Q3. Ai giấu lương?", "q3_negotiable_by_exp_region_contract.png",
     ["29% tin “Thoả thuận”",
      "Trên 5 năm KN: 69% giấu lương",
      "TP.HCM 35% vs Hà Nội 22%",
      "Liên hệ có ý nghĩa nhưng yếu (Cramér's V ≤ 0,15)"]),
    ("figure", "Q4. Phúc lợi", "q4_benefits_by_salary_quartile.png",
     ["Phổ biến: bảo hiểm bắt buộc 71%, du lịch 44%, tháng 13 41%",
      "Số phúc lợi – lương: ρ = 0,14 (yếu)",
      "Lương cao: nhiều thưởng KPI/doanh số hơn (+14 điểm %)"]),
    ("figure", "Q5. Kỹ năng gắn với lương cao (trong cùng ngành)", "q5_skill_salary_premium.png",
     ["SQL +7,2 tr · Python +6,2 · JavaScript +5,5",
      "13 kỹ năng có CI95 hoàn toàn dương",
      "Canva −1,9 tr",
      "Tương quan, không phải nhân quả"]),
    ("figure", "Q6. Dự đoán lương đăng tuyển", "q6_model_comparison.png",
     ["Ridge (TF-IDF + one-hot): MAE 3,99 tr, R² 0,33",
      "Baseline MAE 5,76 → giảm 31% sai số",
      "Chia train/test theo nhóm văn bản (không rò rỉ tin đăng lại)",
      "Văn bản tin là feature quan trọng nhất"]),
    ("figure", "Q6. Mô hình học được gì?", "q6_ridge_coefficients.png",
     ["Tăng: “trưởng phòng”, “manager”, “giám đốc”",
      "Giảm: “thực tập”, “tập sinh”, “intern”, “ctv”"]),
    ("bullets", "Hạn chế & hướng phát triển", [
        "Một nền tảng (TopCV), một thời điểm (2025); lương đăng tuyển ≠ lương thực nhận",
        "29% tin thiếu lương và không ngẫu nhiên (Q3) → mô hình không áp dụng cho các tin này",
        "Gom nhóm bằng regex có thể bỏ sót cách viết hiếm (kỹ năng: 59% tin khớp)",
        "Hướng tiếp: tách từ tiếng Việt, mô hình ngôn ngữ, thu thập thêm nhiều nền tảng",
    ]),
]


def _title(fig, text):
    fig.text(0.05, 0.9, text, fontsize=28, weight="bold", color="#1f3b57")
    fig.add_artist(plt.Line2D([0.05, 0.95], [0.87, 0.87], color="#1f3b57", lw=2))


def render(pdf, slide):
    fig = plt.figure(figsize=(W, H))
    kind = slide[0]
    if kind == "title":
        fig.patch.set_facecolor("#1f3b57")
        fig.text(0.5, 0.58, slide[1], ha="center", fontsize=34, weight="bold", color="white", wrap=True)
        for i, line in enumerate(slide[2]):
            fig.text(0.5, 0.42 - i * 0.07, line, ha="center", fontsize=18, color="#dde6ee")
    elif kind == "bullets":
        _title(fig, slide[1])
        y = 0.76
        for line in slide[2]:
            wrapped = textwrap.fill(line, 75, subsequent_indent="    ")
            fig.text(0.07, y, "•  " + wrapped, fontsize=19, color="#222", va="top")
            y -= 0.1 + 0.05 * wrapped.count(chr(10))
    else:
        _title(fig, slide[1])
        img = mpimg.imread(FIG / slide[2])
        wide = img.shape[1] / img.shape[0] > 2.2
        if wide:  # hình rộng: chiếm cả chiều ngang, ghi chú bên dưới
            ax = fig.add_axes([0.04, 0.3, 0.92, 0.55])
            ax.imshow(img)
            ax.axis("off")
            for i, line in enumerate(slide[3]):
                fig.text(0.07 + (i % 2) * 0.45, 0.2 - (i // 2) * 0.08, "•  " + line, fontsize=16, color="#222", va="top")
        else:
            ax = fig.add_axes([0.04, 0.05, 0.58, 0.78])
            ax.imshow(img)
            ax.axis("off")
            y = 0.76
            for line in slide[3]:
                wrapped = textwrap.fill(line, 30, subsequent_indent="    ")
                fig.text(0.64, y, "•  " + wrapped, fontsize=15, color="#222", va="top")
                y -= 0.09 + 0.045 * wrapped.count(chr(10))
    pdf.savefig(fig)
    plt.close(fig)


def main():
    missing = [s[2] for s in SLIDES if s[0] == "figure" and not (FIG / s[2]).exists()]
    if missing:
        raise SystemExit(f"Thiếu hình (chạy notebook trước): {missing}")
    with PdfPages(OUT) as pdf:
        for s in SLIDES:
            render(pdf, s)
    print("Saved", OUT, f"({len(SLIDES)} slides)")


if __name__ == "__main__":
    main()
