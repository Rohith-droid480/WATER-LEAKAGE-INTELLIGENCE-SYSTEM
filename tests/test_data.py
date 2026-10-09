"""Unit tests for AquaSentinel Data Ingestion and Validation Module (Alpha).

Covers:
- Real BattLeDIM 2018 & 2019 flow telemetry loading and parsing
- Header, shape, delimiter, and numeric decimal conversion
- Chronological ordering and strictly monotonic timestamp verification
- Duplicate timestamp detection
- Missing/null measurement detection (no zero-filling)
- Invalid schema and missing file error handling
- Sequential Observation iteration and stable replay indexing
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from data import Observation, ValidationReport, iter_observations, load_telemetry, validate_telemetry


def test_load_telemetry_2018_flows_real_file():
    """Verify loading real BattLeDIM 2018 SCADA flow dataset."""
    df = load_telemetry(year=2018, kind="flow", data_dir="data")

    # Invariants for 2018 flows
    assert len(df) == 105120
    assert list(df.columns) == ["timestamp", "p227", "p235", "PUMP_1"]
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
    assert pd.api.types.is_float_dtype(df["p227"])
    assert pd.api.types.is_float_dtype(df["p235"])
    assert pd.api.types.is_float_dtype(df["PUMP_1"])

    assert df["timestamp"].min() == pd.Timestamp("2018-01-01 00:00:00")
    assert df["timestamp"].max() == pd.Timestamp("2018-12-31 23:55:00")
    assert df["timestamp"].is_monotonic_increasing


def test_load_telemetry_2019_flows_real_file():
    """Verify loading real BattLeDIM 2019 SCADA flow dataset."""
    df = load_telemetry(year=2019, kind="flow", data_dir="data")

    # Invariants for 2019 flows
    assert len(df) == 105120
    assert list(df.columns) == ["timestamp", "p227", "p235", "PUMP_1"]
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
    assert pd.api.types.is_float_dtype(df["p227"])
    assert pd.api.types.is_float_dtype(df["p235"])
    assert pd.api.types.is_float_dtype(df["PUMP_1"])

    assert df["timestamp"].min() == pd.Timestamp("2019-01-01 00:00:00")
    assert df["timestamp"].max() == pd.Timestamp("2019-12-31 23:55:00")
    assert df["timestamp"].is_monotonic_increasing


def test_validate_telemetry_real_dataset():
    """Verify validation report passes cleanly on real 2018 flow data."""
    df = load_telemetry(year=2018, kind="flow", data_dir="data")
    report = validate_telemetry(df, expected_interval_minutes=5.0)

    assert report.is_valid is True
    assert report.num_rows == 105120
    assert report.channels == ["p227", "p235", "PUMP_1"]
    assert report.duplicate_timestamps_count == 0
    assert report.null_counts == {"p227": 0, "p235": 0, "PUMP_1": 0}
    assert report.interval_minutes == 5.0
    assert len(report.issues) == 0


def test_validate_telemetry_duplicate_timestamps():
    """Verify detection of duplicate timestamps."""
    base_ts = pd.date_range("2018-01-01", periods=5, freq="5min")
    # Duplicate timestamp at index 2
    ts_list = list(base_ts)
    ts_list[2] = ts_list[1]

    df = pd.DataFrame({
        "timestamp": ts_list,
        "p227": [10.0, 11.0, 12.0, 13.0, 14.0],
    })

    report = validate_telemetry(df, expected_interval_minutes=5.0)
    assert report.is_valid is False
    assert report.duplicate_timestamps_count == 1
    assert any("duplicate timestamp" in issue.lower() for issue in report.issues)


def test_validate_telemetry_out_of_chronological_order():
    """Verify detection of non-monotonic timestamps."""
    ts_list = [
        pd.Timestamp("2018-01-01 00:00:00"),
        pd.Timestamp("2018-01-01 00:10:00"),
        pd.Timestamp("2018-01-01 00:05:00"),  # Out of order
    ]
    df = pd.DataFrame({
        "timestamp": ts_list,
        "p227": [10.0, 11.0, 12.0],
    })

    report = validate_telemetry(df, expected_interval_minutes=5.0)
    assert report.is_valid is False
    assert any("not monotonically increasing" in issue for issue in report.issues)


def test_validate_telemetry_missing_values():
    """Verify detection of missing (NaN) values without zero-filling."""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2018-01-01", periods=4, freq="5min"),
        "p227": [10.0, np.nan, 12.0, 13.0],
        "p235": [20.0, 21.0, np.nan, 23.0],
    })

    report = validate_telemetry(df, expected_interval_minutes=5.0)
    assert report.is_valid is False
    assert report.null_counts["p227"] == 1
    assert report.null_counts["p235"] == 1
    assert any("missing (null/nan) values" in issue.lower() for issue in report.issues)


def test_validate_telemetry_invalid_schema():
    """Verify invalid schemas (missing timestamp, 0 rows, no channels)."""
    # Missing timestamp column
    df_no_ts = pd.DataFrame({"p227": [1.0, 2.0]})
    rep1 = validate_telemetry(df_no_ts)
    assert rep1.is_valid is False
    assert any("missing required 'timestamp' column" in issue.lower() for issue in rep1.issues)

    # Empty frame
    df_empty = pd.DataFrame({"timestamp": pd.to_datetime([])})
    rep2 = validate_telemetry(df_empty)
    assert rep2.is_valid is False
    assert rep2.num_rows == 0

    # No channels (timestamp only)
    df_no_ch = pd.DataFrame({"timestamp": pd.date_range("2018-01-01", periods=3, freq="5min")})
    rep3 = validate_telemetry(df_no_ch)
    assert rep3.is_valid is False
    assert any("no telemetry channels" in issue.lower() for issue in rep3.issues)


def test_iter_observations_sequential():
    """Verify sequential yielding of immutable Observation objects."""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2018-01-01", periods=4, freq="5min"),
        "p227": [100.5, 101.2, 102.8, 103.1],
        "p235": [80.0, 81.0, 82.0, 83.0],
    })

    observations = list(iter_observations(df))
    assert len(observations) == 4

    for i, obs in enumerate(observations):
        assert isinstance(obs, Observation)
        assert obs.index == i
        assert obs.timestamp == df["timestamp"].iloc[i].to_pydatetime()
        assert obs.values["p227"] == df["p227"].iloc[i]
        assert obs.values["p235"] == df["p235"].iloc[i]

    # Test start_index parameter
    obs_from_2 = list(iter_observations(df, start_index=2))
    assert len(obs_from_2) == 2
    assert obs_from_2[0].index == 2
    assert obs_from_2[1].index == 3


def test_load_telemetry_missing_file():
    """Verify FileNotFoundError on missing file path."""
    with pytest.raises(FileNotFoundError):
        load_telemetry(year=1999, kind="flow", data_dir="data")

    with pytest.raises(ValueError, match="Unsupported telemetry kind"):
        load_telemetry(year=2018, kind="invalid_kind", data_dir="data")
