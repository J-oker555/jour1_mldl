import pandas as pd

from .labels import HOAX_PATTERN


LEAKY_COLUMNS = {"comments", "date_posted"}


def add_basic_features(frame: pd.DataFrame, include_leaky: bool) -> pd.DataFrame:
    features = pd.DataFrame(index=frame.index)
    features["duration_seconds"] = frame["duration_seconds"]
    features["latitude"] = frame["latitude"]
    features["longitude"] = frame["longitude"]
    features["has_state"] = frame["state"].fillna("").astype(str).str.strip().ne("")
    features["has_country"] = frame["country"].fillna("").astype(str).str.strip().ne("")
    features["comment_length"] = frame["comments"].fillna("").astype(str).str.len()
    features["shape"] = frame["shape"].fillna("unknown").astype(str).str.lower()
    features["country"] = frame["country"].fillna("unknown").astype(str).str.lower()

    dt = frame["datetime"]
    features["hour"] = dt.dt.hour
    features["month"] = dt.dt.month

    if include_leaky:
        features["comment_hoax_keyword"] = (
            frame["comments"].fillna("").astype(str).str.contains(HOAX_PATTERN, regex=True)
        )
    else:
        features = features.drop(columns=["comment_length"])

    return features


def leakage_table(model_columns: list[str]) -> list[dict[str, str]]:
    leaky_feature_sources = {
        "comment_length": "comments",
        "comment_hoax_keyword": "comments",
    }
    rows = []
    for column in model_columns:
        source = leaky_feature_sources.get(column, column)
        rows.append(
            {
                "column": column,
                "source": source,
                "writer": "temoin" if source == "comments" else "capteur ou transmission",
                "moment": "apres observation" if source in LEAKY_COLUMNS else "au moment du releve",
                "knows_hoax": "oui" if source in LEAKY_COLUMNS else "non",
            }
        )
    return rows
