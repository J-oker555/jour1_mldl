from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass(frozen=True)
class ModelMetrics:
    recall: float
    precision: float
    accuracy: float
    train_size: int
    test_size: int


def train_and_evaluate(features: pd.DataFrame, target: pd.Series, seed: int = 42) -> ModelMetrics:
    numeric = [c for c in features.columns if pd.api.types.is_numeric_dtype(features[c])]
    categorical = [c for c in features.columns if c not in numeric]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
        ]
    )
    model = Pipeline(
        [
            ("preprocess", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )

    stratify = target if target.nunique() == 2 and target.value_counts().min() >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.25,
        random_state=seed,
        stratify=stratify,
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    return ModelMetrics(
        recall=recall_score(y_test, predictions, zero_division=0),
        precision=precision_score(y_test, predictions, zero_division=0),
        accuracy=accuracy_score(y_test, predictions),
        train_size=len(x_train),
        test_size=len(x_test),
    )


def baseline_always_not_hoax(target: pd.Series) -> float:
    return float((~target.astype(bool)).mean())

