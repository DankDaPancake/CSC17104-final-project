import numpy as np
import pytest

from src.cleaning import (
    experience_level,
    normalize_location,
    parse_experience_months,
    parse_list,
    parse_salary_avg,
    to_region,
)


def test_salary():
    assert parse_salary_avg("12 triệu") == 12.0
    assert np.isnan(parse_salary_avg("Thoả thuận"))
    assert np.isnan(parse_salary_avg(np.nan))


@pytest.mark.parametrize(
    "s,m",
    [("6 tháng", 6), ("2 năm", 24), ("18 tháng", 18), ("Không yêu cầu", 0), ("10 năm", 120)],
)
def test_experience(s, m):
    assert parse_experience_months(s) == m


def test_experience_unknown():
    assert np.isnan(parse_experience_months("abc"))
    assert np.isnan(parse_experience_months(np.nan))


def test_experience_level():
    assert experience_level(0) == "Không yêu cầu"
    assert experience_level(6) == "Dưới 1 năm"
    assert experience_level(12) == "1-2 năm"
    assert experience_level(24) == "1-2 năm"
    assert experience_level(36) == "3-5 năm"
    assert experience_level(60) == "3-5 năm"
    assert experience_level(120) == "Trên 5 năm"
    assert experience_level(np.nan) == "Không rõ"


def test_location():
    assert normalize_location("hà đông") == ("hà nội", False)
    assert normalize_location(" Hà Nội, hồ chí minh ") == ("hà nội", True)
    assert to_region("hà nội") == "Hà Nội"
    assert to_region("hồ chí minh") == "TP.HCM"
    assert to_region("đà nẵng") == "Khác"


def test_parse_list():
    assert parse_list("['Thưởng năm', ' Lương tháng 13']") == ["Thưởng năm", "Lương tháng 13"]
    assert parse_list(np.nan) == []
    assert parse_list("nan") == []
    assert parse_list("") == []
    assert parse_list("[]") == []
    out = parse_list("['Kỹ năng 'mềm', 'Excel']")  # malformed: must not raise
    assert isinstance(out, list) and "Excel" in out
