import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

from src.cleaning import CLEAN_PATH, load_clean
from src.modeling import CAT_COLS, FORBIDDEN, NUM_COLS, TEXT_COL, evaluate, make_models, prepare_xy


@pytest.fixture(scope="module")
def small_clean_df():
    if not CLEAN_PATH.exists():
        pytest.skip("run notebooks/02_cleaning.ipynb first")
    return load_clean().sample(2000, random_state=42)


def test_prepare_xy_no_leakage(small_clean_df):
    X, y = prepare_xy(small_clean_df)
    assert not (set(X.columns) & FORBIDDEN)
    assert list(X.columns) == CAT_COLS + NUM_COLS + [TEXT_COL]
    assert y.notna().all() and len(X) == len(y)
    kept = small_clean_df.loc[X.index]
    assert not kept["salary_negotiable"].any() and not kept["salary_outlier"].any()
    assert np.allclose(np.exp(y), kept["salary_avg_num"])


def test_models_fit_and_evaluate(small_clean_df):
    X, y = prepare_xy(small_clean_df)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    res = evaluate(make_models(tfidf_min_df=2, svd_components=20), Xtr, Xte, ytr, yte)
    assert list(res.columns) == ["MAE", "RMSE", "R2"]
    assert set(res.index) == {"baseline", "ridge", "hgb"}
    assert (res["MAE"] > 0).all()
    assert res.loc["ridge", "MAE"] < res.loc["baseline", "MAE"]


@pytest.fixture(scope="module")
def synthetic_clean_df():
    from src.cleaning import clean
    rng = np.random.default_rng(0)
    rows = []
    for i in range(400):
        lo = int(rng.integers(5, 30))
        rows.append(dict(
            job_title=f"Nhân viên {['kế toán', 'kinh doanh', 'IT'][i % 3]} {i}", location=["hà nội", "hồ chí minh", "đà nẵng"][i % 3],
            country="Việt Nam", qualifications="['Đại học']", technical_skills="['Excel']", soft_skills="[]",
            languages_required=np.nan, experience_required=f"{i % 5} năm", salary=f"{lo}.0 - {lo + 5}.0 triệu",
            contract_type="Toàn thời gian", working_hours=np.nan, benefits="['BHXH']", description=f"mô tả {i}",
            requirements_text=f"yêu cầu {i % 7}", category=["a", "b"][i % 2], salary_min=lo, salary_max=lo + 5,
            salary_avg=f"{lo + 2} triệu",
        ))
    rows[0].update(salary="0.0 triệu", salary_min=0, salary_max=0, salary_avg="Thoả thuận")
    rows[1].update(salary="300.0 - 400.0 triệu", salary_min=300, salary_max=400, salary_avg="350 triệu")
    return clean(pd.DataFrame(rows))


def test_leakage_guard_runs_without_data_file(synthetic_clean_df):
    X, y = prepare_xy(synthetic_clean_df)
    assert not (set(X.columns) & FORBIDDEN)
    assert len(X) == 398  # bỏ 1 tin thoả thuận + 1 tin ngoại lai
    kept = synthetic_clean_df.loc[X.index]
    assert not kept["salary_negotiable"].any() and not kept["salary_outlier"].any()
    assert np.allclose(np.exp(y), kept["salary_avg_num"])


def test_group_split_keeps_identical_text_on_one_side():
    from src.modeling import group_train_test_split
    X = pd.DataFrame({TEXT_COL: ["a", "a", "b", "b", "c", "c", "d", "d", "e", "e"] * 10, "k": range(100)})
    y = pd.Series(np.arange(100.0))
    Xtr, Xte, ytr, yte = group_train_test_split(X, y, test_size=0.2)
    assert not set(Xtr[TEXT_COL]) & set(Xte[TEXT_COL])
    assert len(Xtr) + len(Xte) == 100 and len(Xte) > 0
