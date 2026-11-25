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


def _raw_row(**kw):
    base = dict(
        job_title="Kế toán", location="hà nội", country="Việt Nam", qualifications="['Đại học']",
        technical_skills="['Excel']", soft_skills="['Giao tiếp']", languages_required=np.nan,
        experience_required="1 năm", salary="10.0 - 14.0 triệu", contract_type="Toàn thời gian",
        working_hours=np.nan, benefits="['Thưởng', 'Bảo hiểm']", description="mô tả",
        requirements_text="yêu cầu", category="tài_chính", salary_min=10, salary_max=14,
        salary_avg="12 triệu",
    )
    base.update(kw)
    return base


def test_clean_pipeline():
    import pandas as pd
    from src.cleaning import clean

    raw = pd.DataFrame([
        _raw_row(country="Lào", description="a"),
        _raw_row(description="dup"),
        _raw_row(description="dup"),
        _raw_row(description="outlier", salary_avg="300 triệu", salary_min=200, salary_max=400),
        _raw_row(description="min0", salary_min=0, salary_avg="10 triệu", location="hà đông"),
        _raw_row(description="neg", salary_min=0, salary_max=0, salary_avg="Thoả thuận",
                 benefits=np.nan, location="hồ chí minh, hà nội"),
    ])
    out = clean(raw)
    assert len(out) == 4
    assert (out.country == "Việt Nam").all()
    assert out.salary_outlier.sum() == 1
    assert set(out.region) <= {"Hà Nội", "TP.HCM", "Khác"}
    assert out.benefits_list.map(type).eq(list).all()
    row_min0 = out[out.description == "min0"].iloc[0]
    assert not row_min0.salary_negotiable and row_min0.salary_avg_num == 10
    assert row_min0.region == "Hà Nội"
    row_neg = out[out.description == "neg"].iloc[0]
    assert row_neg.salary_negotiable and np.isnan(row_neg.salary_avg_num)
    assert row_neg.multi_location and row_neg.region == "TP.HCM"
    assert row_neg.n_benefits == 0
    assert out.experience_months.eq(12).all()
    assert set(out.contract_group) == {"Khác"}  # < 100 tin → gộp


def test_clean_flags_near_zero_salary_as_outlier():
    import pandas as pd
    from src.cleaning import clean

    out = clean(pd.DataFrame([_raw_row(salary="0.3 - 1.0 triệu", salary_min=0, salary_avg="0 triệu")]))
    row = out.iloc[0]
    assert not row.salary_negotiable
    assert row.salary_outlier


@pytest.mark.parametrize("raw,expected", [
    ("bắc từ liêm", "hà nội"), ("cầu giấy", "hà nội"), ("đống đa", "hà nội"), ("long biên", "hà nội"),
    ("thủ đức", "hồ chí minh"), ("quận 7", "hồ chí minh"), ("bình thạnh", "hồ chí minh"),
    ("củ chi", "hồ chí minh"), ("ho chi minh city", "hồ chí minh"), ("tp. thủ đức", "hồ chí minh"),
    ("['hà nội'", "hà nội"), ("hà nội & hồ chí minh", "hà nội"), ("bắc ninh; hà nội", "bắc ninh"),
    ("đà nẵng", "đà nẵng"),
])
def test_location_districts_map_to_city(raw, expected):
    assert normalize_location(raw)[0] == expected


def test_location_separators_flag_multi():
    assert normalize_location("hà nội & hồ chí minh")[1]
    assert normalize_location("hà nội/hồ chí minh")[1]


def test_parse_list_never_raises():
    for bad in ["{[1]}", "{['a']}", "[" * 500]:
        assert isinstance(parse_list(bad), list)
