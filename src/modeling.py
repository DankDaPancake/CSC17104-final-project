"""Q6 — Dự đoán lương đăng tuyển (log triệu VND/tháng).

Quy tắc chống rò rỉ: không dùng bất kỳ cột lương nào làm feature (xem FORBIDDEN);
mọi bộ biến đổi (TF-IDF, scaler, SVD) nằm trong Pipeline nên chỉ fit trên tập train.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

RANDOM_STATE = 42
FORBIDDEN = {
    "salary", "salary_min", "salary_max", "salary_avg",
    "salary_avg_num", "salary_negotiable", "salary_outlier",
}
CAT_COLS = ["category", "region", "experience_level", "contract_group"]
NUM_COLS = ["experience_months", "n_benefits", "n_technical_skills"]
TEXT_COL = "text"


def prepare_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Lọc tin có lương hợp lệ; X = thuộc tính + văn bản (tên việc + yêu cầu); y = log(lương)."""
    d = df[~df["salary_negotiable"] & ~df["salary_outlier"]].copy()
    d[TEXT_COL] = d["job_title"].fillna("") + " . " + d["requirements_text"].fillna("")
    X = d[CAT_COLS + NUM_COLS + [TEXT_COL]].copy()
    for c in CAT_COLS:
        X[c] = X[c].astype(str)
    y = np.log(d["salary_avg_num"]).rename("log_salary")
    return X, y


def _tfidf(min_df: int) -> TfidfVectorizer:
    return TfidfVectorizer(max_features=20000, ngram_range=(1, 2), min_df=min_df, sublinear_tf=True)


def make_models(tfidf_min_df: int = 3, svd_components: int = 100) -> dict[str, Pipeline]:
    ridge_pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
        ("num", StandardScaler(), NUM_COLS),
        ("txt", _tfidf(tfidf_min_df), TEXT_COL),
    ])
    hgb_pre = ColumnTransformer([
        ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), CAT_COLS),
        ("num", "passthrough", NUM_COLS),
        ("txt", Pipeline([("tfidf", _tfidf(tfidf_min_df)),
                          ("svd", TruncatedSVD(svd_components, random_state=RANDOM_STATE))]), TEXT_COL),
    ])
    return {
        "baseline": Pipeline([("pre", ColumnTransformer([("num", "passthrough", NUM_COLS)])),
                              ("regressor", DummyRegressor(strategy="median"))]),
        "ridge": Pipeline([("pre", ridge_pre), ("regressor", Ridge(alpha=1.0))]),
        "hgb": Pipeline([("pre", hgb_pre),
                         ("regressor", HistGradientBoostingRegressor(
                             categorical_features=list(range(len(CAT_COLS))), random_state=RANDOM_STATE))]),
    }


def evaluate(models: dict[str, Pipeline], X_train, X_test, y_train, y_test) -> pd.DataFrame:
    """Fit từng mô hình trên train, đo trên test theo đơn vị triệu VND (đã exp)."""
    rows = {}
    y_true = np.exp(y_test)
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = np.exp(model.predict(X_test))
        rows[name] = {
            "MAE": mean_absolute_error(y_true, y_pred),
            "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "R2": r2_score(y_true, y_pred),
        }
    return pd.DataFrame(rows).T[["MAE", "RMSE", "R2"]]


def group_train_test_split(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2,
                           random_state: int = RANDOM_STATE):
    """Chia train/test sao cho các tin có văn bản giống hệt (tin đăng lại) nằm cùng một phía."""
    from sklearn.model_selection import GroupShuffleSplit

    groups = X[TEXT_COL].str.lower().str.strip()
    train_idx, test_idx = next(GroupShuffleSplit(n_splits=1, test_size=test_size,
                                                 random_state=random_state).split(X, y, groups))
    return X.iloc[train_idx], X.iloc[test_idx], y.iloc[train_idx], y.iloc[test_idx]
