"""AquaSentinel Data Module (Alpha Owned).

Responsibilities:
- Ingest and validate telemetry files (BattLeDIM benchmark telemetry).
- Parse actual schemas, separators, and numeric types (semicolon delimited, comma decimal).
- Strictly validate chronology, duplicate timestamps, intervals, and missing values.
- Stream observations strictly in chronological order with stable replay indices.
- Zero label awareness: event labels and leakages are never loaded or parsed here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Iterator, List, Optional, Union

import pandas as pd


@dataclass(frozen=True)
class Observation:
    """Represents a single sequential telemetry observation.

    Attributes:
        timestamp: Source observation timestamp (datetime).
        index: Monotonically increasing 0-based replay index.
        values: Mapping of channel/sensor identifiers to observed float readings.
    """
    timestamp: datetime
    index: int
    values: Dict[str, float]


@dataclass
class ValidationReport:
    """Report detailing data quality, chronology, and schema health."""
    is_valid: bool
    num_rows: int
    channels: List[str]
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None
    interval_minutes: Optional[float] = None
    duplicate_timestamps_count: int = 0
    null_counts: Dict[str, int] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)


def _resolve_telemetry_filepath(year: Union[int, str], kind: str, data_dir: str) -> str:
    """Resolve the actual telemetry file path for a given year and kind."""
    year_str = str(year).strip()
    kind_norm = kind.strip().lower()

    if kind_norm in ("flow", "flows"):
        filename = f"{year_str}_SCADA_Flows.csv"
    elif kind_norm in ("pressure", "pressures"):
        filename = f"{year_str}_SCADA_Pressures.csv"
    elif kind_norm in ("level", "levels"):
        filename = f"{year_str}_SCADA_Levels.csv"
    elif kind_norm in ("demand", "demands"):
        filename = f"{year_str}_SCADA_Demands.csv"
    else:
        raise ValueError(f"Unsupported telemetry kind: '{kind}'. Expected flow, pressure, level, or demand.")

    filepath = os.path.join(data_dir, filename)
    return filepath


def load_telemetry(
    year: Union[int, str] = 2018,
    kind: str = "flow",
    data_dir: str = "data",
) -> pd.DataFrame:
    """Load real telemetry data into a cleaned, validated DataFrame.

    BattLeDIM SCADA CSV files use semicolon (';') delimiters and comma (',')
    decimal notation.

    Returns:
        pd.DataFrame with a datetime 'timestamp' column followed by numeric channel columns.
    """
    filepath = _resolve_telemetry_filepath(year, kind, data_dir)
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Telemetry file not found at '{filepath}'. Verify dataset acquisition in '{data_dir}'."
        )

    # Inspect first line to determine delimiter
    with open(filepath, "r", encoding="utf-8") as f:
        header_line = f.readline()
    sep = ";" if ";" in header_line else ","

    # Load with pandas, handling European decimal separator if present
    df = pd.read_csv(filepath, sep=sep, decimal=",")

    # Locate timestamp column
    ts_col = None
    for col in df.columns:
        if col.strip().lower() in ("timestamp", "time", "date", "datetime"):
            ts_col = col
            break

    if ts_col is None:
        raise ValueError(
            f"Unable to locate a valid timestamp column in '{filepath}'. Found columns: {list(df.columns)}"
        )

    # Convert timestamp column to datetime
    df["timestamp"] = pd.to_datetime(df[ts_col])
    if ts_col != "timestamp":
        df = df.drop(columns=[ts_col])

    # Reorder so timestamp is the first column
    channel_cols = [c for c in df.columns if c != "timestamp"]
    for ch in channel_cols:
        df[ch] = pd.to_numeric(df[ch], errors="coerce")

    # Order columns: timestamp, followed by sensor channels
    df = df[["timestamp"] + channel_cols]

    # Ensure chronological order
    if not df["timestamp"].is_monotonic_increasing:
        df = df.sort_values(by="timestamp").reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)

    return df


def validate_telemetry(
    frame: pd.DataFrame,
    expected_interval_minutes: float = 5.0,
) -> ValidationReport:
    """Validate schema, timestamp continuity, duplicates, and missing values.

    Rules:
    - Must have 'timestamp' column of datetime dtype.
    - Must have at least one numeric channel column.
    - Timestamps must be strictly monotonic increasing without duplicates.
    - Missing measurements must be detected (never silently zero-filled).
    """
    issues: List[str] = []

    if "timestamp" not in frame.columns:
        return ValidationReport(
            is_valid=False,
            num_rows=len(frame),
            channels=[],
            issues=["Missing required 'timestamp' column."],
        )

    channels = [c for c in frame.columns if c != "timestamp"]
    if not channels:
        issues.append("No telemetry channels found in DataFrame.")

    num_rows = len(frame)
    if num_rows == 0:
        return ValidationReport(
            is_valid=False,
            num_rows=0,
            channels=channels,
            issues=["DataFrame contains 0 rows."],
        )

    # Check timestamps
    ts_series = frame["timestamp"]
    start_ts = ts_series.iloc[0]
    end_ts = ts_series.iloc[-1]

    # Duplicate timestamps
    dup_count = int(ts_series.duplicated().sum())
    if dup_count > 0:
        issues.append(f"Found {dup_count} duplicate timestamp(s).")

    # Chronological ordering check
    if not ts_series.is_monotonic_increasing:
        issues.append("Timestamps are not monotonically increasing.")

    # Sampling interval check
    time_diffs = ts_series.diff().dropna()
    expected_delta = timedelta(minutes=expected_interval_minutes)
    if len(time_diffs) > 0:
        median_delta = time_diffs.median()
        interval_min = median_delta.total_seconds() / 60.0
        abnormal_intervals = (time_diffs != expected_delta).sum()
        if abnormal_intervals > 0:
            issues.append(
                f"{abnormal_intervals} intervals differ from expected {expected_interval_minutes}m (median interval: {interval_min:.2f}m)."
            )
    else:
        interval_min = None

    # Missing value checks per channel
    null_counts: Dict[str, int] = {}
    for ch in channels:
        null_n = int(frame[ch].isnull().sum())
        null_counts[ch] = null_n
        if null_n > 0:
            issues.append(f"Channel '{ch}' has {null_n} missing (null/NaN) values.")

    is_valid = len(issues) == 0

    return ValidationReport(
        is_valid=is_valid,
        num_rows=num_rows,
        channels=channels,
        start_timestamp=start_ts.to_pydatetime() if hasattr(start_ts, "to_pydatetime") else start_ts,
        end_timestamp=end_ts.to_pydatetime() if hasattr(end_ts, "to_pydatetime") else end_ts,
        interval_minutes=interval_min,
        duplicate_timestamps_count=dup_count,
        null_counts=null_counts,
        issues=issues,
    )


def iter_observations(
    frame: pd.DataFrame,
    start_index: int = 0,
) -> Iterator[Observation]:
    """Iterate through rows sequentially, yielding immutable Observation objects.

    Yields observations strictly in order, attaching a monotonic replay index.
    """
    if start_index < 0:
        raise ValueError(f"start_index must be >= 0, got {start_index}")

    channel_cols = [c for c in frame.columns if c != "timestamp"]

    for idx, row in frame.iterrows():
        int_idx = int(idx)
        if int_idx < start_index:
            continue

        ts = row["timestamp"]
        py_ts = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
        val_dict = {col: float(row[col]) for col in channel_cols}

        yield Observation(
            timestamp=py_ts,
            index=int_idx,
            values=val_dict,
        )
