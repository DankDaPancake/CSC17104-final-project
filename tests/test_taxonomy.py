from src.taxonomy import BENEFIT_GROUPS, SKILL_GROUPS, tag_items


def test_benefit_synonyms_map_to_one_group():
    for text in ["Thưởng tháng 13", "lương tháng thứ 13", "Thưởng tháng lương thứ 13"]:
        assert tag_items([text], BENEFIT_GROUPS) == ["Lương/thưởng tháng 13"]
    assert tag_items(["BHXH", "bảo hiểm y tế"], BENEFIT_GROUPS) == ["Bảo hiểm bắt buộc (BHXH/BHYT/BHTN)"]


def test_item_can_match_multiple_groups_and_dedup():
    tags = tag_items(["Du lịch hàng năm, team building", "du lịch"], BENEFIT_GROUPS)
    assert sorted(tags) == sorted(["Du lịch/nghỉ mát", "Team building/gắn kết"])


def test_skills():
    assert tag_items(["Thành thạo Excel", "Adobe Photoshop"], SKILL_GROUPS) == ["Excel/Tin học văn phòng", "Photoshop"]
    assert tag_items(["Java", "JavaScript"], SKILL_GROUPS) == ["Java", "JavaScript"]
    assert tag_items(["email"], SKILL_GROUPS) == []  # 'ai' inside a word must not match


def test_empty():
    assert tag_items([], BENEFIT_GROUPS) == []


def test_benefit_regex_does_not_match_across_items():
    assert tag_items(["Thưởng KPI", "Nghỉ lễ tết theo luật"], BENEFIT_GROUPS) == ["Thưởng hiệu quả/KPI/doanh số"]


def test_bare_ai_in_design_list_is_illustrator():
    assert tag_items(["Photoshop", "AI"], SKILL_GROUPS) == ["Photoshop", "Illustrator"]
    assert tag_items(["Sử dụng công cụ AI"], SKILL_GROUPS) == ["AI/Machine Learning"]
    assert tag_items(["AI"], SKILL_GROUPS) == ["AI/Machine Learning"]
    assert tag_items(["Data.ai"], SKILL_GROUPS) == []
