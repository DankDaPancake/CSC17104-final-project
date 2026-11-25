"""Sinh notebook 03–07 (Q1–Q5). Chạy từ thư mục gốc: python scripts/build_nb_analysis.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbtools import SETUP, build  # noqa: E402

LIMIT = """
**Hạn chế chung:** dữ liệu chỉ từ TopCV (2025), là **lương đăng tuyển** (không phải lương thực nhận),
và ~29% tin không công bố lương. Kết luận chỉ mô tả thị trường tin tuyển dụng trên nền tảng này.
"""
AUTO = "\n*Nhận xét trên được sinh tự động từ số liệu — thành viên phụ trách cần đọc lại và diễn giải bằng lời của mình.*"

# ---------------- Q1 ----------------
build("notebooks/03_q1_salary_region_category.ipynb", [
("md", """
# Q1. Lương khác nhau thế nào theo vùng và theo ngành?
**Người phụ trách:** Đăng

**Động lực:** người tìm việc cân nhắc chuyển vùng/ngành cần biết mức chênh lệch lương trên tin tuyển dụng.
**Phương pháp:** trung vị `salary_avg_num` (triệu VND/tháng) theo vùng × ngành; kiểm định Kruskal-Wallis và
Mann-Whitney (phi tham số vì lương lệch phải mạnh).
"""),
("code", SETUP),
("md", "## 1. Phân bố lương theo vùng"),
("code", """
by_region = sal.groupby("region", observed=True)["salary_avg_num"].describe()[["count", "25%", "50%", "75%", "mean"]].round(1)
display(by_region)
fig, ax = plt.subplots(figsize=(7, 4))
sns.boxplot(data=sal, x="region", y="salary_avg_num", order=REGIONS, showfliers=False, ax=ax, color="#7aa6c2")
ax.set(xlabel="Vùng", ylabel="Lương trung bình (triệu VND/tháng)", title="Lương đăng tuyển theo vùng (ẩn điểm ngoại lai)")
savefig("q1_salary_by_region.png")
"""),
("code", """
from scipy.stats import kruskal, mannwhitneyu
groups = [g["salary_avg_num"].values for _, g in sal.groupby("region", observed=True)]
H, p = kruskal(*groups)
print(f"Kruskal-Wallis giữa 3 vùng: H = {H:.1f}, p = {p:.2e}")
_, p_hn_hcm = mannwhitneyu(sal.loc[sal.region == "Hà Nội", "salary_avg_num"], sal.loc[sal.region == "TP.HCM", "salary_avg_num"])
print(f"Mann-Whitney Hà Nội vs TP.HCM: p = {p_hn_hcm:.2e}")
"""),
("md", "## 2. Lương theo ngành"),
("code", """
by_cat = sal.groupby("cat")["salary_avg_num"].agg(["count", "median", "mean"]).sort_values("median", ascending=False).round(1)
display(by_cat)
order = by_cat.index
fig, ax = plt.subplots(figsize=(8, 6))
sns.boxplot(data=sal, y="cat", x="salary_avg_num", order=order, showfliers=False, ax=ax, color="#9cc59a")
ax.set(ylabel="", xlabel="Lương trung bình (triệu VND/tháng)", title="Lương đăng tuyển theo ngành")
savefig("q1_salary_by_category.png")
"""),
("md", "## 3. Ngành × vùng"),
("code", """
pivot = sal.pivot_table(index="cat", columns="region", values="salary_avg_num", aggfunc="median", observed=True).loc[order]
counts = sal.pivot_table(index="cat", columns="region", values="salary_avg_num", aggfunc="count", observed=True).loc[order]
pivot = pivot.where(counts >= 30)  # ô < 30 tin không đủ tin cậy
fig, ax = plt.subplots(figsize=(7, 7))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="Blues", ax=ax, cbar_kws={"label": "Trung vị lương (triệu)"})
ax.set(xlabel="", ylabel="", title="Trung vị lương theo ngành × vùng (ô < 30 tin bị ẩn)")
savefig("q1_heatmap_category_region.png")
gap = (pivot["Hà Nội"] - pivot["Khác"]).dropna().sort_values(ascending=False)
gap.to_frame("Chênh lệch Hà Nội − tỉnh khác (triệu)").round(1)
"""),
("md", "## 4. Kết luận"),
("code", """
med = sal.groupby("region", observed=True)["salary_avg_num"].median()
print(f"- Trung vị lương: Hà Nội {med['Hà Nội']:.1f}, TP.HCM {med['TP.HCM']:.1f}, tỉnh khác {med['Khác']:.1f} triệu/tháng; "
      f"khác biệt có ý nghĩa thống kê (Kruskal-Wallis p = {p:.1e}).")
print(f"- Ngành trả cao nhất (trung vị): {by_cat.index[0]} ({by_cat['median'].iloc[0]:.1f}), {by_cat.index[1]} ({by_cat['median'].iloc[1]:.1f}); "
      f"thấp nhất: {by_cat.index[-1]} ({by_cat['median'].iloc[-1]:.1f}).")
print(f"- Chênh lệch giữa ngành cao nhất và thấp nhất ≈ {by_cat['median'].iloc[0] - by_cat['median'].iloc[-1]:.1f} triệu; "
      f"giữa các vùng ≈ {med.max() - med.min():.1f} triệu.")
"""),
("md", LIMIT + AUTO),
])

# ---------------- Q2 ----------------
build("notebooks/04_q2_experience_salary.ipynb", [
("md", """
# Q2. Mỗi năm kinh nghiệm làm tăng lương bao nhiêu? Có khác giữa các ngành?
**Người phụ trách:** Đăng

**Phương pháp:** trung vị lương theo `experience_level`; hồi quy tuyến tính `log(lương) ~ experience_months` cho
toàn bộ và cho 8 ngành nhiều tin nhất → % tăng lương mỗi năm = `exp(12·β) − 1`.
"""),
("code", SETUP),
("md", "## 1. Lương theo mức kinh nghiệm"),
("code", """
levels = [l for l in EXPERIENCE_LEVELS if l != "Không rõ"]
by_lvl = sal.groupby("experience_level", observed=True)["salary_avg_num"].agg(["count", "median", "mean"]).reindex(levels).round(1)
display(by_lvl)
fig, ax = plt.subplots(figsize=(8, 4))
sns.boxplot(data=sal, x="experience_level", y="salary_avg_num", order=levels, showfliers=False, ax=ax, color="#e3b778")
ax.set(xlabel="Kinh nghiệm yêu cầu", ylabel="Lương trung bình (triệu VND/tháng)", title="Lương theo kinh nghiệm yêu cầu")
savefig("q2_salary_by_experience.png")
"""),
("md", "## 2. Hồi quy log-lương theo số tháng kinh nghiệm, từng ngành"),
("code", """
from scipy.stats import linregress
rows = []
top_cats = sal["cat"].value_counts().head(8).index
for name, g in [("Toàn bộ", sal)] + [(c, sal[sal.cat == c]) for c in top_cats]:
    r = linregress(g["experience_months"], np.log(g["salary_avg_num"]))
    rows.append({"ngành": name, "n": len(g), "β/tháng": r.slope, "% tăng/năm": (np.exp(12 * r.slope) - 1) * 100,
                 "R²": r.rvalue ** 2, "p": r.pvalue})
growth = pd.DataFrame(rows).set_index("ngành").sort_values("% tăng/năm", ascending=False)
display(growth.round({"β/tháng": 4, "% tăng/năm": 1, "R²": 3}))
fig, ax = plt.subplots(figsize=(7, 4))
growth["% tăng/năm"].drop("Toàn bộ").sort_values().plot.barh(ax=ax, color="#c98b6b")
ax.axvline(growth.loc["Toàn bộ", "% tăng/năm"], ls="--", c="k", label="Toàn bộ")
ax.set(xlabel="% tăng lương mỗi năm kinh nghiệm", ylabel="", title="Mức tăng lương theo kinh nghiệm, theo ngành")
ax.legend()
savefig("q2_growth_by_category.png")
"""),
("code", """
# Trung vị lương theo năm kinh nghiệm (0–5 năm) cho 4 ngành nhiều tin nhất
tmp = sal[sal.experience_months <= 60].assign(years=lambda d: (d.experience_months // 12).astype(int))
curve = tmp[tmp.cat.isin(top_cats[:4])].groupby(["cat", "years"])["salary_avg_num"].median().unstack(0)
ax = curve.plot(marker="o", figsize=(7, 4))
ax.set(xlabel="Số năm kinh nghiệm yêu cầu", ylabel="Trung vị lương (triệu)", title="Trung vị lương theo năm kinh nghiệm")
savefig("q2_salary_curve.png")
"""),
("md", "## 3. Kết luận"),
("code", """
t = growth.drop("Toàn bộ")
print(f"- Tổng thể, mỗi năm kinh nghiệm yêu cầu gắn với lương đăng tuyển cao hơn ≈ {growth.loc['Toàn bộ', '% tăng/năm']:.1f}%.")
print(f"- Trung vị: 'Không yêu cầu' {by_lvl.loc['Không yêu cầu', 'median']:.0f} → '1-2 năm' {by_lvl.loc['1-2 năm', 'median']:.0f} → "
      f"'3-5 năm' {by_lvl.loc['3-5 năm', 'median']:.0f} → 'Trên 5 năm' {by_lvl.loc['Trên 5 năm', 'median']:.0f} triệu.")
print(f"- Tăng nhanh nhất: {t.index[0]} ({t['% tăng/năm'].iloc[0]:.1f}%/năm); chậm nhất: {t.index[-1]} ({t['% tăng/năm'].iloc[-1]:.1f}%/năm).")
print(f"- R² tổng thể ≈ {growth.loc['Toàn bộ', 'R²']:.2f}: kinh nghiệm chỉ giải thích một phần biến động lương.")
"""),
("md", LIMIT + "\nKinh nghiệm ở đây là kinh nghiệm **yêu cầu** trong tin, không phải kinh nghiệm thực của ứng viên." + AUTO),
])

# ---------------- Q3 ----------------
build("notebooks/05_q3_negotiable_salary.ipynb", [
("md", """
# Q3. Tin để lương "Thoả thuận" tập trung ở đâu?
**Người phụ trách:** Tiến

**Động lực:** tin không công bố lương làm giảm minh bạch cho người tìm việc; biết nhóm nào hay giấu lương giúp
ứng viên chuẩn bị đàm phán. **Phương pháp:** tỉ lệ `salary_negotiable` theo ngành / kinh nghiệm / vùng / loại hợp đồng;
kiểm định chi-square độc lập và độ mạnh liên hệ Cramér's V.
"""),
("code", SETUP),
("code", """
from scipy.stats import chi2_contingency
overall = df["salary_negotiable"].mean() * 100
print(f"Tỉ lệ 'Thoả thuận' toàn bộ: {overall:.1f}%")
tests = []
for col in ["cat", "experience_level", "region", "contract_group"]:
    ct = pd.crosstab(df[col], df["salary_negotiable"])
    ct = ct[ct.sum(axis=1) > 0]
    chi2, p, dof, _ = chi2_contingency(ct)
    cramers_v = np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1)))
    tests.append({"biến": col, "chi2": chi2, "dof": dof, "p": p, "cramers_v": cramers_v})
tests = pd.DataFrame(tests).set_index("biến")
tests.round(3)
"""),
("code", """
def rate(col, order=None):
    r = df.groupby(col, observed=True)["salary_negotiable"].agg(["mean", "size"])
    r["mean"] *= 100
    return r.reindex(order) if order is not None else r.sort_values("mean", ascending=False)

r_cat = rate("cat")
fig, ax = plt.subplots(figsize=(8, 6))
r_cat["mean"].sort_values().plot.barh(ax=ax, color="#b48ead")
ax.axvline(overall, ls="--", c="k", label=f"Trung bình {overall:.0f}%")
ax.set(xlabel="% tin để lương 'Thoả thuận'", ylabel="", title="Tỉ lệ tin không công bố lương theo ngành")
ax.legend()
savefig("q3_negotiable_by_category.png")
"""),
("code", """
levels = [l for l in EXPERIENCE_LEVELS if l != "Không rõ"]
r_exp, r_reg, r_con = rate("experience_level", levels), rate("region", REGIONS), rate("contract_group")
fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
for ax, (r, t) in zip(axes, [(r_exp, "Kinh nghiệm"), (r_reg, "Vùng"), (r_con, "Loại hợp đồng")]):
    r["mean"].plot.bar(ax=ax, color="#b48ead")
    ax.axhline(overall, ls="--", c="k")
    ax.set(title=t, xlabel="", ylabel="% 'Thoả thuận'")
    ax.tick_params(axis="x", rotation=30)
savefig("q3_negotiable_by_exp_region_contract.png")
display(pd.concat({"kinh nghiệm": r_exp, "vùng": r_reg, "hợp đồng": r_con}).round(1))
"""),
("md", "## Kết luận"),
("code", """
print(f"- {overall:.1f}% tin không công bố lương.")
print(f"- Ngành giấu lương nhiều nhất: {r_cat.index[0]} ({r_cat['mean'].iloc[0]:.0f}%), {r_cat.index[1]} ({r_cat['mean'].iloc[1]:.0f}%); "
      f"ít nhất: {r_cat.index[-1]} ({r_cat['mean'].iloc[-1]:.0f}%).")
print(f"- Theo kinh nghiệm: 'Không yêu cầu' {r_exp.loc['Không yêu cầu', 'mean']:.0f}% so với 'Trên 5 năm' {r_exp.loc['Trên 5 năm', 'mean']:.0f}%.")
best = tests["cramers_v"].idxmax()
print(f"- Tất cả các biến đều có p < 0.05: {bool((tests.p < 0.05).all())}; liên hệ mạnh nhất là '{best}' "
      f"(Cramér's V = {tests.loc[best, 'cramers_v']:.3f}); mọi liên hệ đều yếu (V < 0.2).")
"""),
("md", LIMIT + AUTO),
])

# ---------------- Q4 ----------------
build("notebooks/06_q4_benefits.ipynb", [
("md", """
# Q4. Phúc lợi nào phổ biến nhất? Lương cao có đi kèm nhiều phúc lợi hơn?
**Người phụ trách:** Tiến

**Phương pháp:** phúc lợi là văn bản tự do (~73.000 cách viết) → gom về 16 nhóm chuẩn bằng regex (`src/taxonomy.py`,
có test). Tính tỉ lệ tin có từng nhóm; so sánh theo nhóm lương (tứ phân vị); tương quan Spearman giữa số nhóm phúc lợi
và lương.
"""),
("code", SETUP),
("code", """
from scipy.stats import spearmanr
from src.taxonomy import BENEFIT_GROUPS, tag_items
df["benefit_tags"] = df["benefits_list"].map(lambda l: tag_items(l, BENEFIT_GROUPS))
df["n_benefit_groups"] = df["benefit_tags"].map(len)
print(f"Tin có ít nhất 1 nhóm phúc lợi nhận diện được: {(df.n_benefit_groups > 0).mean():.1%}")
share = df["benefit_tags"].explode().value_counts() / len(df) * 100
fig, ax = plt.subplots(figsize=(8, 6))
share.sort_values().plot.barh(ax=ax, color="#88c0d0")
ax.set(xlabel="% tin tuyển dụng có phúc lợi", ylabel="", title="Mức độ phổ biến của các nhóm phúc lợi")
savefig("q4_benefit_share.png")
share.round(1).to_frame("% tin")
"""),
("md", "## Phúc lợi theo nhóm lương"),
("code", """
s = df[~df.salary_negotiable & ~df.salary_outlier].copy()
s["salary_q"] = pd.qcut(s["salary_avg_num"], 4, labels=["Q1 (thấp)", "Q2", "Q3", "Q4 (cao)"])
print(s.groupby("salary_q", observed=True)["salary_avg_num"].agg(["min", "max", "size"]))
onehot = pd.DataFrame({b: s["benefit_tags"].map(lambda t, b=b: b in t) for b in share.index[:10]})
by_q = onehot.groupby(s["salary_q"], observed=True).mean().T * 100
fig, ax = plt.subplots(figsize=(8, 5))
sns.heatmap(by_q, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax, cbar_kws={"label": "% tin"})
ax.set(xlabel="Nhóm lương (tứ phân vị)", ylabel="", title="Top 10 phúc lợi theo nhóm lương")
savefig("q4_benefits_by_salary_quartile.png")
"""),
("code", """
rho, p = spearmanr(s["n_benefit_groups"], s["salary_avg_num"])
print(f"Spearman(số nhóm phúc lợi, lương) = {rho:.3f}, p = {p:.1e}")
cmp = df.groupby("salary_negotiable")["n_benefit_groups"].mean().rename({True: "Thoả thuận", False: "Công bố lương"})
display(cmp.round(2).to_frame("TB số nhóm phúc lợi"))
fig, ax = plt.subplots(figsize=(7, 4))
sns.boxplot(data=s, x="salary_q", y="n_benefit_groups", ax=ax, color="#88c0d0", showfliers=False)
ax.set(xlabel="Nhóm lương", ylabel="Số nhóm phúc lợi", title="Số nhóm phúc lợi theo nhóm lương")
savefig("q4_n_benefits_by_salary.png")
"""),
("md", "## Kết luận"),
("code", """
diff = (by_q["Q4 (cao)"] - by_q["Q1 (thấp)"]).sort_values()
print(f"- Phổ biến nhất: {share.index[0]} ({share.iloc[0]:.0f}% tin), {share.index[1]} ({share.iloc[1]:.0f}%), {share.index[2]} ({share.iloc[2]:.0f}%).")
strength = "rất yếu" if abs(rho) < 0.1 else "yếu" if abs(rho) < 0.3 else "vừa"
print(f"- Tương quan số nhóm phúc lợi – lương: ρ = {rho:.2f} ({strength}, {'dương' if rho > 0 else 'âm'}).")
print(f"- Chênh lệch lớn nhất giữa nhóm lương cao và thấp: '{diff.index[-1]}' ({diff.iloc[-1]:+.0f} điểm %); "
      f"'{diff.index[0]}' ({diff.iloc[0]:+.0f} điểm %).")
"""),
("md", LIMIT + "\nPhúc lợi chỉ được đếm khi khớp regex — có thể bỏ sót cách viết hiếm." + AUTO),
])

# ---------------- Q5 ----------------
build("notebooks/07_q5_skills.ipynb", [
("md", """
# Q5. Kỹ năng nào được tuyển nhiều nhất theo ngành? Kỹ năng nào gắn với lương cao hơn?
**Người phụ trách:** Thành viên 3

**Phương pháp:** `technical_skills` là văn bản tự do (~29.000 cách viết) → gom về 32 nhóm kỹ năng bằng regex
(`src/taxonomy.py`). Đếm theo ngành; với mỗi kỹ năng có ≥ 100 tin có lương: so sánh trung vị lương **trong cùng ngành**
(có vs không có kỹ năng) rồi lấy trung bình có trọng số — tránh nhầm "kỹ năng IT lương cao" chỉ vì ngành IT lương cao.
"""),
("code", SETUP),
("code", """
from src.taxonomy import SKILL_GROUPS, tag_items
df["skill_tags"] = df["technical_skills_list"].map(lambda l: tag_items(l, SKILL_GROUPS))
print(f"Tin có ≥1 nhóm kỹ năng nhận diện được: {(df.skill_tags.map(len) > 0).mean():.1%} "
      f"(tin có liệt kê kỹ năng: {(df.n_technical_skills > 0).mean():.1%})")
top_cats = df["cat"].value_counts().head(6).index
ex = df[["cat", "skill_tags"]].explode("skill_tags").dropna()
share = (ex.groupby("cat")["skill_tags"].value_counts() / df["cat"].value_counts()).mul(100).rename("% tin")
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for ax, c in zip(axes.flat, top_cats):
    share.loc[c].sort_values(ascending=False).head(8).sort_values().plot.barh(ax=ax, color="#a3be8c")
    ax.set(title=c, xlabel="% tin trong ngành", ylabel="")
savefig("q5_top_skills_by_category.png")
"""),
("md", "## Kỹ năng gắn với lương cao (so sánh trong cùng ngành)"),
("code", """
s = df[~df.salary_negotiable & ~df.salary_outlier]
rows = []
for skill in SKILL_GROUPS:
    has = s["skill_tags"].map(lambda t: skill in t)
    if has.sum() < 100:
        continue
    diffs, weights = [], []
    for c, g in s.groupby("cat"):
        h = has.loc[g.index]
        if h.sum() >= 10 and (~h).sum() >= 10:
            diffs.append(g.loc[h, "salary_avg_num"].median() - g.loc[~h, "salary_avg_num"].median())
            weights.append(h.sum())
    rows.append({"kỹ năng": skill, "số tin": int(has.sum()),
                 "trung vị có (triệu)": s.loc[has, "salary_avg_num"].median(),
                 "chênh lệch thô": s.loc[has, "salary_avg_num"].median() - s.loc[~has, "salary_avg_num"].median(),
                 "chênh lệch trong ngành": np.average(diffs, weights=weights) if diffs else np.nan})
prem = pd.DataFrame(rows).set_index("kỹ năng").sort_values("chênh lệch trong ngành", ascending=False)
display(prem.round(1))
v = prem["chênh lệch trong ngành"].dropna().sort_values()
fig, ax = plt.subplots(figsize=(8, 7))
v.plot.barh(ax=ax, color=np.where(v > 0, "#a3be8c", "#bf616a"))
ax.axvline(0, c="k")
ax.set(xlabel="Chênh lệch trung vị lương (triệu), có vs không có kỹ năng, trong cùng ngành", ylabel="",
       title="Kỹ năng gắn với lương đăng tuyển cao hơn")
savefig("q5_skill_salary_premium.png")
"""),
("md", "## Kết luận"),
("code", """
overall_top = ex["skill_tags"].value_counts()
print(f"- Kỹ năng được yêu cầu nhiều nhất: {', '.join(overall_top.index[:3])}.")
pp = prem["chênh lệch trong ngành"].dropna()
print(f"- Gắn với lương cao hơn nhất (trong cùng ngành): {pp.index[0]} ({pp.iloc[0]:+.1f} triệu), "
      f"{pp.index[1]} ({pp.iloc[1]:+.1f}), {pp.index[2]} ({pp.iloc[2]:+.1f}).")
print(f"- Thấp nhất: {pp.index[-1]} ({pp.iloc[-1]:+.1f} triệu).")
"""),
("md", LIMIT + "\nChênh lệch là **tương quan**, không phải nhân quả." + AUTO),
])
print("built 03-07")
