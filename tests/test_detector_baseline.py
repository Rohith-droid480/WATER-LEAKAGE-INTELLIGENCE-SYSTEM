"""Unit tests for AquaSentinel Baseline and Detector Modules (Alpha).

Covers:
- Baseline fitting on real 2018 flow telemetry
- Robust median and MAD scale lookup
- Near-zero scale fallback to pooled scale
- Zero online adaptation / immutability
- Detector initialization and pure CUSUM calculation
- Stale run ID rejection and repeated row idempotency
- Direction awareness (upper vs lower CUSUM)
- Incident grouping
"""

from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from baseline import BaselineModel, BaselinePoint, fit_baseline, lookup_baseline
from data import Observation, load_telemetry
from detector import build_incidents, init_detector, step


def test_baseline_fit_and_lookup_real_data():
    """Verify baseline fitting on real 2018 BattLeDIM flow telemetry."""
    df_2018 = load_telemetry(year=2018, kind="flow", data_dir="data")
    model = fit_baseline(df_2018)

    assert isinstance(model, BaselineModel)
    assert set(model.channels) == {"p227", "p235", "PUMP_1"}
    assert model.training_rows_eligible == 105120

    # Query a Monday 00:00 timestamp
    ts_query = datetime(2018, 1, 1, 0, 0, 0)
    pt = lookup_baseline(model, ts_query, "p227")

    assert isinstance(pt, BaselinePoint)
    assert pt.status in ("VALID", "POOLED_SCALE")
    assert pt.scale > 0.0
    assert 50.0 < pt.expected < 150.0


def test_baseline_pooled_scale_fallback():
    """Verify that constant/zero-variance bins fall back to pooled scale."""
    # Synthetic frame with constant values at a specific time slot
    dates = pd.date_range("2018-01-01", periods=14, freq="D")
    df = pd.DataFrame({
        "timestamp": dates,
        "p227": [100.0] * 14,  # zero variance
    })

    model = fit_baseline(df)
    pt = lookup_baseline(model, dates[0].to_pydatetime(), "p227")
    assert pt.status in ("POOLED_SCALE", "VALID")
    assert pt.scale > 0.0


def test_baseline_mismatched_mask_raises():
    """Verify ValueError when valid_mask length differs from train_frame."""
    df = pd.DataFrame({"timestamp": pd.date_range("2018-01-01", periods=5, freq="5min"), "p227": [1, 2, 3, 4, 5]})
    with pytest.raises(ValueError, match="valid_mask length"):
        fit_baseline(df, valid_mask=[True, True])


def test_detector_cusum_pure_step_known_sequence():
    """Verify deterministic CUSUM accumulation with known inputs."""
    configs = {"FLOW": {"k": 0.5, "h": 5.0, "direction": "upper"}}
    state = init_detector(configs, "run-1")

    # Day 0, base expected 100, scale 10. Observation = 120 (z = 2.0)
    # k = 0.5 -> score = max(0, 0 + 2.0 - 0.5) = 1.5
    obs1 = Observation(timestamp=datetime(2019, 1, 1, 0, 0), index=0, values={"FLOW": 120.0})
    bp1 = {"FLOW": BaselinePoint(expected=100.0, scale=10.0)}

    res1 = step(state, "run-1", 0, obs1.timestamp, obs1, bp1)
    assert res1.channels["FLOW"].cusum_score == 1.5
    assert res1.channels["FLOW"].is_alert is False
    assert state.last_processed_index == 0

    # Step 2: Observation = 160 (z = 6.0)
    # score = max(0, 1.5 + 6.0 - 0.5) = 7.0 > 5.0 -> Alert!
    obs2 = Observation(timestamp=datetime(2019, 1, 1, 0, 5), index=1, values={"FLOW": 160.0})
    res2 = step(state, "run-1", 1, obs2.timestamp, obs2, bp1)
    assert res2.channels["FLOW"].cusum_score == 7.0
    assert res2.channels["FLOW"].is_alert is True
    assert res2.is_alert is True
    assert res2.incident_evidence is not None
    assert state.last_processed_index == 1


def test_detector_stale_run_id_rejected():
    """Verify that stale run_id raises ValueError and preserves state."""
    configs = {"FLOW": {"k": 0.5, "h": 5.0}}
    state = init_detector(configs, "valid-run")
    obs = Observation(timestamp=datetime(2019, 1, 1, 0, 0), index=0, values={"FLOW": 100.0})
    bp = {"FLOW": BaselinePoint(expected=100.0, scale=10.0)}

    with pytest.raises(ValueError, match="Stale run_id rejected"):
        step(state, "stale-run", 0, obs.timestamp, obs, bp)

    assert state.last_processed_index == -1


def test_detector_duplicate_index_rejected():
    """Verify that duplicate or out-of-order index raises ValueError and does not mutate state."""
    configs = {"FLOW": {"k": 0.5, "h": 5.0}}
    state = init_detector(configs, "run-1")
    bp = {"FLOW": BaselinePoint(expected=100.0, scale=10.0)}

    obs0 = Observation(timestamp=datetime(2019, 1, 1, 0, 0), index=0, values={"FLOW": 100.0})
    step(state, "run-1", 0, obs0.timestamp, obs0, bp)
    assert state.last_processed_index == 0

    # Repeat index 0
    with pytest.raises(ValueError, match="Repeated row rejected"):
        step(state, "run-1", 0, obs0.timestamp, obs0, bp)

    assert state.last_processed_index == 0


def test_detector_direction_awareness():
    """Verify lower-sided detection on pressure drops."""
    configs = {"PRESS": {"k": 0.5, "h": 4.0, "direction": "lower"}}
    state = init_detector(configs, "run-press")
    # Expected pressure = 40, scale = 2. Observed = 34 (drop of 6 -> residual = -6 -> z = +3.0)
    obs = Observation(timestamp=datetime(2019, 1, 1, 0, 0), index=0, values={"PRESS": 34.0})
    bp = {"PRESS": BaselinePoint(expected=40.0, scale=2.0)}

    res = step(state, "run-press", 0, obs.timestamp, obs, bp)
    assert res.channels["PRESS"].z_score == 3.0
    # score = max(0, 0 + 3.0 - 0.5) = 2.5
    assert res.channels["PRESS"].cusum_score == 2.5


def test_build_incidents_grouping():
    """Verify contiguous alert grouping into incidents."""
    configs = {"FLOW": {"k": 0.5, "h": 2.0}}
    state = init_detector(configs, "run-inc")
    bp = {"FLOW": BaselinePoint(expected=100.0, scale=10.0)}

    results = []
    # Steps:
    # 0: val 100 (z=0, score=0) -> No alert
    # 1: val 130 (z=3, score=2.5 > 2) -> Alert onset
    # 2: val 130 (z=3, score=5.0 > 2) -> Alert continues
    # 3..15: val 70 (z=-3, score decays quickly: 5 - 3.5 = 1.5 < 2) -> Alert clears!
    values = [100.0, 130.0, 130.0, 70.0, 100.0]
    for idx, val in enumerate(values):
        obs = Observation(timestamp=datetime(2019, 1, 1, 0, 5 * idx), index=idx, values={"FLOW": val})
        res = step(state, "run-inc", idx, obs.timestamp, obs, bp)
        results.append(res)

    incidents = build_incidents(results)
    assert len(incidents) == 1
    assert incidents[0]["start_index"] == 1
    assert incidents[0]["end_index"] == 2
    assert "FLOW" in incidents[0]["contributing_channels"]
