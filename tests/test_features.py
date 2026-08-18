import pandas as pd

from src.ufo_pipeline.features import add_basic_features, build_feature_set, leakage_table


def test_leaky_features_include_explicit_comment_keyword() -> None:
    frame = pd.DataFrame(
        {
            "duration_seconds": [1],
            "latitude": [48.0],
            "longitude": [2.0],
            "state": ["idf"],
            "country": ["fr"],
            "comments": ["obvious hoax"],
            "shape": ["light"],
            "datetime": pd.to_datetime(["2020-01-01 12:00"]),
        }
    )

    leaky = add_basic_features(frame, include_leaky=True)
    clean = add_basic_features(frame, include_leaky=False)

    assert "comment_hoax_keyword" in leaky.columns
    assert "comment_hoax_keyword" not in clean.columns
    assert "comment_length" not in clean.columns


def test_leakage_table_marks_comment_derived_features() -> None:
    rows = leakage_table(["duration_seconds", "comment_hoax_keyword"])

    assert rows[0]["knows_hoax"] == "non"
    assert rows[1]["source"] == "comments"
    assert rows[1]["knows_hoax"] == "oui"


def test_feature_set_removes_all_columns_marked_as_leaky() -> None:
    frame = pd.DataFrame(
        {
            "duration_seconds": [1],
            "latitude": [48.0],
            "longitude": [2.0],
            "state": ["idf"],
            "country": ["fr"],
            "comments": ["obvious hoax"],
            "shape": ["light"],
            "datetime": pd.to_datetime(["2020-01-01 12:00"]),
        }
    )

    feature_set = build_feature_set(frame)
    clean = feature_set.without_leakage()
    leaky_columns = [row["column"] for row in feature_set.leakage_rows if row["knows_hoax"] == "oui"]

    assert leaky_columns == ["comment_length", "comment_hoax_keyword"]
    assert all(column not in clean.columns for column in leaky_columns)
