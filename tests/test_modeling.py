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
