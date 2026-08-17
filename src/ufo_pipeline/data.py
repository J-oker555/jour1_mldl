import csv
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .config import DATA_URL, HEADERS


@dataclass(frozen=True)
class RejectedRecord:
    line_number: int
    field_count: int
    expected_field_count: int
    row: list[str]

    @property
    def reason(self) -> str:
        return f"{self.field_count} champs au lieu de {self.expected_field_count}"


@dataclass(frozen=True)
class LoadResult:
    frame: pd.DataFrame
    total_records: int
    loaded_records: int
    rejected_records: list[RejectedRecord]

    @property
    def rejected_records_count(self) -> int:
        return len(self.rejected_records)

    @property
    def rejection_reasons(self) -> dict[str, int]:
        reasons: dict[str, int] = {}
        for record in self.rejected_records:
            reasons[record.reason] = reasons.get(record.reason, 0) + 1
        return dict(sorted(reasons.items()))


def download_data(target: Path, url: str = DATA_URL) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 0:
        return target
    urllib.request.urlretrieve(url, target)
    return target


def load_transmission(path: Path, headers: list[str] | None = None) -> LoadResult:
    expected_headers = headers or HEADERS
    rows: list[dict[str, str]] = []
    rejected: list[RejectedRecord] = []

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for line_number, row in enumerate(reader, start=1):
            if not row:
                continue
            if len(row) != len(expected_headers):
                rejected.append(
                    RejectedRecord(
                        line_number=line_number,
                        field_count=len(row),
                        expected_field_count=len(expected_headers),
                        row=row,
                    )
                )
                continue
            rows.append(dict(zip(expected_headers, row, strict=True)))

    frame = pd.DataFrame(rows, columns=expected_headers)
    return LoadResult(
        frame=frame,
        total_records=len(rows) + len(rejected),
        loaded_records=len(rows),
        rejected_records=rejected,
    )


def convert_types(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, dict[str, object]]]:
    converted = frame.copy()
    specs = {
        "datetime": ("datetime", lambda s: pd.to_datetime(s, errors="coerce")),
        "date_posted": ("date", lambda s: pd.to_datetime(s, errors="coerce")),
        "duration_seconds": ("number", lambda s: pd.to_numeric(s, errors="coerce")),
        "latitude": ("number", lambda s: pd.to_numeric(s, errors="coerce")),
        "longitude": ("number", lambda s: pd.to_numeric(s, errors="coerce")),
    }
    anomalies: dict[str, dict[str, object]] = {}

    for column, (kind, converter) in specs.items():
        raw = converted[column].astype("string")
        result = converter(raw)
        invalid = raw.notna() & raw.str.strip().ne("") & result.isna()
        converted[column] = result
        anomalies[column] = {
            "type": kind,
            "count": int(invalid.sum()),
            "examples": raw[invalid].drop_duplicates().head(10).tolist(),
        }

    return converted, anomalies
