from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score
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
    train_positive: int
    train_negative: int
    test_positive: int
    test_negative: int
    true_negative: int
    false_positive: int
    false_negative: int
    true_positive: int
    test_fraction: float
    random_seed: int


@dataclass(frozen=True)
class BaselineMetrics:
    accuracy: float
    recall: float
    precision: float
    predicted_positive: int
    predicted_negative: int


def train_and_evaluate(
    features: pd.DataFrame,
    target: pd.Series,
    seed: int = 42,
    test_size: float = 0.25,
) -> ModelMetrics:
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
        test_size=test_size,
        random_state=seed,
        stratify=stratify,
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[False, True]).ravel()

    return ModelMetrics(
        recall=recall_score(y_test, predictions, zero_division=0),
        precision=precision_score(y_test, predictions, zero_division=0),
        accuracy=accuracy_score(y_test, predictions),
        train_size=len(x_train),
        test_size=len(x_test),
        train_positive=int(y_train.sum()),
        train_negative=int((~y_train.astype(bool)).sum()),
        test_positive=int(y_test.sum()),
        test_negative=int((~y_test.astype(bool)).sum()),
        true_negative=int(tn),
        false_positive=int(fp),
        false_negative=int(fn),
        true_positive=int(tp),
        test_fraction=test_size,
        random_seed=seed,
    )


def baseline_always_not_hoax(target: pd.Series) -> float:
    return baseline_always_not_hoax_metrics(target).accuracy


def baseline_always_not_hoax_metrics(target: pd.Series) -> BaselineMetrics:
    labels = target.astype(bool)
    predictions = pd.Series(False, index=labels.index)
    return BaselineMetrics(
        accuracy=accuracy_score(labels, predictions),
        recall=recall_score(labels, predictions, zero_division=0),
        precision=precision_score(labels, predictions, zero_division=0),
        predicted_positive=int(predictions.sum()),
        predicted_negative=int((~predictions).sum()),
    )
