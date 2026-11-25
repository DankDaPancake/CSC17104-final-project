"""Gom phúc lợi / kỹ năng dạng văn bản tự do về nhóm chuẩn bằng regex (không phân biệt hoa thường)."""
from __future__ import annotations

import re

BENEFIT_GROUPS: dict[str, str] = {
    "Bảo hiểm bắt buộc (BHXH/BHYT/BHTN)": r"bảo hiểm xã hội|bhxh|bhyt|bhtn|bảo hiểm y tế|bảo hiểm thất nghiệp|bảo hiểm bắt buộc|bảo hiểm theo (quy định|luật)",
    "Bảo hiểm sức khỏe/tai nạn bổ sung": r"bảo hiểm (sức kh|tai nạn|nhân thọ|cao cấp|chăm sóc)|bảo việt|\bpti\b|\bpvi\b",
    "Lương/thưởng tháng 13": r"tháng 13|thứ 13|lương 13",
    "Thưởng hiệu quả/KPI/doanh số": r"thưởng.*(hiệu quả|kpi|doanh số|doanh thu|kết quả|năng suất|dự án|nóng)|hoa hồng|commission",
    "Thưởng lễ, tết": r"thưởng.*(lễ|tết)|(lễ|tết).*thưởng",
    "Du lịch/nghỉ mát": r"du lịch|nghỉ mát|du xuân",
    "Team building/gắn kết": r"team ?building|gắn kết|dã ngoại|year end party|tất niên",
    "Khám sức khỏe định kỳ": r"khám sức kh",
    "Phụ cấp ăn trưa": r"ăn trưa|bữa trưa|cơm trưa|phụ cấp ăn|ăn ca|bữa ăn",
    "Phụ cấp đi lại/điện thoại": r"xăng xe|đi lại|gửi xe|điện thoại|công tác phí",
    "Đào tạo": r"đào tạo|khóa học|khoá học",
    "Cơ hội thăng tiến": r"thăng tiến",
    "Nghỉ phép": r"nghỉ phép|ngày phép|phép năm|phép/năm",
    "Trang bị máy tính/thiết bị": r"máy tính|laptop|trang thiết bị|thiết bị làm việc",
    "Xét tăng lương định kỳ": r"tăng lương|xét lương|review lương|đánh giá lương",
    "Hiếu hỉ/sinh nhật/ốm đau": r"sinh nhật|hiếu|ốm đau|thai sản|8/3|1/6",
}

SKILL_GROUPS: dict[str, str] = {
    "Excel/Tin học văn phòng": r"excel|tin học văn phòng|\bword\b|powerpoint|office",
    "AutoCAD": r"autocad|\bcad\b",
    "Photoshop": r"photoshop",
    "Illustrator": r"illustrator",
    "Revit": r"revit",
    "SketchUp": r"sketch ?up",
    "3ds Max": r"3d ?s? ?max",
    "SolidWorks": r"solidworks?",
    "CapCut": r"capcut",
    "Premiere/After Effects": r"premiere|after effects?",
    "Canva": r"canva",
    "Phần mềm kế toán/MISA": r"phần mềm kế toán|misa",
    "SEO": r"\bseo\b",
    "Google/Facebook Ads": r"google ads|facebook ads|meta ads|tiktok ads|quảng cáo",
    "Google Analytics": r"google analytics",
    "Digital marketing": r"digital marketing",
    "Phân tích dữ liệu": r"phân tích dữ liệu|data analy",
    "Power BI/Tableau": r"power ?bi|tableau",
    "SQL": r"\bsql\b|mysql|postgres|sql server",
    "Python": r"python",
    "Java": r"\bjava\b(?!script)",
    "JavaScript": r"javascript|\bjs\b|typescript",
    "React/Vue/Angular": r"react|vue|angular",
    "Node.js": r"node",
    ".NET/C#": r"\.net|c#",
    "PHP": r"\bphp\b",
    "Docker/Cloud": r"docker|kubernetes|\baws\b|azure|gcp",
    "AI/Machine Learning": r"(?<![.\w])ai\b|trí tuệ nhân tạo|chatgpt|machine learning|deep learning",
    "Tiếng Anh": r"tiếng anh|english|toeic|ielts",
    "Bán hàng/đàm phán": r"bán hàng|đàm phán|telesales|thuyết phục|chốt sale",
    "Quản lý dự án": r"quản lý dự án|project management",
    "PLC/Tự động hoá": r"\bplc\b|tự động hóa|tự động hoá|scada",
}

_COMPILED: dict[int, list[tuple[str, re.Pattern]]] = {}


def _compiled(groups: dict[str, str]) -> list[tuple[str, re.Pattern]]:
    key = id(groups)
    if key not in _COMPILED:
        _COMPILED[key] = [(name, re.compile(p, re.IGNORECASE)) for name, p in groups.items()]
    return _COMPILED[key]


def tag_items(items: list[str], groups: dict[str, str]) -> list[str]:
    """Trả danh sách nhóm (không trùng, theo thứ tự định nghĩa) mà ít nhất một phần tử khớp.

    Mỗi phần tử được so khớp riêng — pattern dạng `thưởng.*tết` không được nối hai phần tử khác nhau.
    """
    lowered = [i.lower().strip() for i in items if i]
    if groups is SKILL_GROUPS and "ai" in lowered and _has_design_tool(lowered):
        # "AI" đứng riêng cạnh Photoshop/InDesign... là Adobe Illustrator, không phải trí tuệ nhân tạo
        lowered = ["illustrator" if i == "ai" else i for i in lowered]
    return [name for name, pat in _compiled(groups) if any(pat.search(i) for i in lowered)]


_DESIGN_TOOLS = re.compile(r"photoshop|\bps\b|indesign|corel|illustrator|after effects?|premiere|figma|lightroom")


def _has_design_tool(items: list[str]) -> bool:
    return any(_DESIGN_TOOLS.search(i) for i in items)
