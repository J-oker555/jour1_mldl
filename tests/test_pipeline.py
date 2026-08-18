from pathlib import Path

from src.ufo_pipeline.data import convert_types, load_transmission
from src.ufo_pipeline.labels import build_hoax_label, describe_hoax_label


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
    assert result.rejected_records[0].line_number == 2
    assert result.rejected_records[0].reason == "2 champs au lieu de 11"
    assert result.rejection_reasons == {"2 champs au lieu de 11": 1}


def test_convert_types_reports_invalid_values(tmp_path: Path) -> None:
    sample = tmp_path / "sample.csv"
    sample.write_text(
        "not-a-date,paris,idf,fr,circle,abc,ten,comment,also-bad,lat,2.35\n",
        encoding="utf-8",
    )
    loaded = load_transmission(sample)

    _, anomalies = convert_types(loaded.frame)

    assert anomalies["datetime"].invalid_count == 1
    assert anomalies["datetime"].origin == "temoin"
    assert anomalies["date_posted"].origin == "service de transmission"
    assert anomalies["duration_seconds"].invalid_count == 1
    assert anomalies["duration_seconds"].origin == "capteur"
    assert anomalies["duration_seconds"].nature_counts == {"lettre dans un nombre": 1}
    assert anomalies["latitude"].invalid_count == 1
    assert anomalies["latitude"].nature_counts == {"lettre dans un nombre": 1}
    assert anomalies["longitude"].invalid_count == 0


def test_convert_types_keeps_rows_and_counts_missing_values(tmp_path: Path) -> None:
    sample = tmp_path / "sample.csv"
    sample.write_text(
        "2020-01-01 20:00,paris,idf,fr,circle,,ten,comment,2020-01-02,,\n",
        encoding="utf-8",
    )
    loaded = load_transmission(sample)

    converted, anomalies = convert_types(loaded.frame)

    assert len(converted) == loaded.loaded_records
    assert anomalies["duration_seconds"].missing_count == 1
    assert anomalies["duration_seconds"].invalid_count == 0
    assert anomalies["duration_seconds"].nature_counts == {"valeur vide": 1}
    assert anomalies["latitude"].missing_count == 1
    assert anomalies["longitude"].missing_count == 1


def test_convert_types_classifies_common_real_dataset_anomalies(tmp_path: Path) -> None:
    sample = tmp_path / "sample.csv"
    sample.write_text(
        "10/10/2005 24:00,paris,idf,fr,circle,2`,ten,comment,2020-01-02,48.85,2.35\n",
        encoding="utf-8",
    )
    loaded = load_transmission(sample)

    _, anomalies = convert_types(loaded.frame)

    assert anomalies["datetime"].nature_counts == {"heure 24:00 non parseable": 1}
    assert anomalies["duration_seconds"].nature_counts == {"caractere parasite dans un nombre": 1}


def test_hoax_label_is_explainable() -> None:
    import pandas as pd

    labels = build_hoax_label(pd.Series(["this was a hoax", "bright light", "fake report"]))

    assert labels.tolist() == [True, False, True]


def test_describe_hoax_label_reports_rule_counts_and_examples() -> None:
    import pandas as pd

    result = describe_hoax_label(pd.Series(["this was a hoax", "bright light", "fake report"]))

    assert result.labels.tolist() == [True, False, True]
    assert result.positive_count == 2
    assert result.positive_rate == 2 / 3
    assert result.trigger_counts == {"hoax": 1, "fake": 1}
    assert "temoignage contient" in result.rule
    assert len(result.examples) == 2
    assert "rate les canulars" in result.limitation


