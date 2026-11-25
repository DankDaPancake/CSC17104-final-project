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
    assert tag_items(["AI"], SKILL_GROUPS) == ["AI/Machine Learning"]
    assert tag_items(["email"], SKILL_GROUPS) == []  # 'ai' inside a word must not match


def test_empty():
    assert tag_items([], BENEFIT_GROUPS) == []
