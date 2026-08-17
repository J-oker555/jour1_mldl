from pathlib import Path

from src.ufo_pipeline.data import convert_types, load_transmission
from src.ufo_pipeline.labels import build_hoax_label
from src.ufo_pipeline.modeling import baseline_always_not_hoax


def test_load_transmission_keeps_bad_rows_visible(tmp_path: Path) -> None:
    sample = tmp_path / "sample.csv"
    sample.write_text(
        "2020-01-01 20:00,paris,idf,fr,circle,10,10 sec,clear sky,2020-01-02,48.85,2.35\n"
        "bad,row\n",
        encoding="utf-8",
    )

    result = load_transmission(sample)

    assert result.total_records == 2
    assert result.loaded_records == 1
    assert len(result.rejected_records) == 1
    assert result.rejected_records[0][0] == 2


def test_convert_types_reports_invalid_values(tmp_path: Path) -> None:
    sample = tmp_path / "sample.csv"
    sample.write_text(
        "not-a-date,paris,idf,fr,circle,abc,ten,comment,also-bad,lat,2.35\n",
        encoding="utf-8",
    )
    loaded = load_transmission(sample)

    _, anomalies = convert_types(loaded.frame)

    assert anomalies["datetime"]["count"] == 1
    assert anomalies["duration_seconds"]["count"] == 1
    assert anomalies["latitude"]["count"] == 1
    assert anomalies["longitude"]["count"] == 0


def test_hoax_label_is_explainable() -> None:
    import pandas as pd

    labels = build_hoax_label(pd.Series(["this was a hoax", "bright light", "fake report"]))

    assert labels.tolist() == [True, False, True]


def test_baseline_always_not_hoax() -> None:
    import pandas as pd

    score = baseline_always_not_hoax(pd.Series([True, False, False, False]))

    assert score == 0.75

