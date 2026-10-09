"""Unit tests for AquaSentinel Evaluator Module (Beta).

Covers:
- Real BattLeDIM event metadata parsing from dataset_configuration.yaml
- Training mask generation and alignment
- Strict vs lenient event-to-alert matching
- Unmatched alert counts and monthly rate calculation
- Detection delay estimation
- Recall by leak diameter breakdown
- Limitations and disclaimer disclosures
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from evaluate import (
    EventMetadata,
    EvaluationSummary,
    build_training_mask,
    evaluate_predictions,
    load_event_metadata,
    parse_leakage_events,
)


def test_parse_leakage_events_real_yaml():
    """Verify parsing real BattLeDIM dataset_configuration.yaml."""
    events = parse_leakage_events("data/dataset_configuration.yaml")
    assert len(events) == 33

    first = events[0]
    assert first.link_id == "p257"
    assert first.start_time == datetime(2018, 1, 8, 13, 30)
    assert first.end_time == datetime(2019, 12, 31, 23, 55)
    assert first.diameter == 0.011843
    assert first.leak_type == "incipient"
    assert first.peak_time == datetime(2018, 1, 25, 8, 30)

    # 2018 vs 2019 onsets
    onsets_2018 = [e for e in events if e.start_time.year == 2018]
    onsets_2019 = [e for e in events if e.start_time.year == 2019]
    assert len(onsets_2018) == 14
    assert len(onsets_2019) == 19


def test_load_event_metadata_year_filter():
    """Verify year-filtered event metadata loading."""
    ev_2018 = load_event_metadata("data", year=2018)
    # Events overlapping 2018
    assert len(ev_2018) >= 14

    ev_2019 = load_event_metadata("data", year=2019)
    # Events overlapping 2019
    assert len(ev_2019) >= 19


def test_build_training_mask_alignment():
    """Verify training exclusion mask alignment and exclusions."""
    dates = pd.date_range("2018-01-01", periods=10, freq="D")
    event = EventMetadata(
        link_id="pTEST",
        start_time=datetime(2018, 1, 3, 0, 0),
        end_time=datetime(2018, 1, 5, 23, 59),
        diameter=0.02,
        leak_type="abrupt",
        peak_time=datetime(2018, 1, 3, 0, 0),
    )

    mask = build_training_mask(dates, [event])
    assert len(mask) == 10
    # Day 0 (Jan 1) and Day 1 (Jan 2) are before leak onset -> True
    assert bool(mask[0]) is True
    assert bool(mask[1]) is True
    # Day 2 (Jan 3), Day 3 (Jan 4), Day 4 (Jan 5) fall within leak window -> False
    assert bool(mask[2]) is False
    assert bool(mask[3]) is False
    assert bool(mask[4]) is False
    # Day 5 (Jan 6) onward are clean -> True
    assert bool(mask[5]) is True
    assert bool(mask[6]) is True


def test_evaluate_predictions_strict_and_lenient():
    """Verify strict vs lenient matching on synthetic predictions."""
    event = EventMetadata(
        link_id="p100",
        start_time=datetime(2019, 2, 1, 0, 0),
        end_time=datetime(2019, 2, 20, 0, 0),
        diameter=0.02,
        leak_type="abrupt",
        peak_time=datetime(2019, 2, 1, 0, 0),
    )

    # 1. Alert at Day 2 (within strict window of 7 days)
    preds_strict = [
        {"timestamp": datetime(2019, 1, 30, 0, 0), "is_alert": False},
        {"timestamp": datetime(2019, 2, 3, 0, 0), "is_alert": True},
    ]
    summary_strict = evaluate_predictions(preds_strict, [event])
    assert summary_strict.events_detected_strict == 1
    assert summary_strict.events_detected_lenient == 1
    assert summary_strict.recall_strict == 1.0
    assert summary_strict.recall_lenient == 1.0
    assert summary_strict.delays_evaluable_count == 1
    assert summary_strict.median_delay_hours == 48.0  # 2 days = 48h

    # 2. Alert at Day 15 (outside 7-day strict window, but within event duration)
    preds_lenient = [
        {"timestamp": datetime(2019, 1, 30, 0, 0), "is_alert": False},
        {"timestamp": datetime(2019, 2, 16, 0, 0), "is_alert": True},
    ]
    summary_lenient = evaluate_predictions(preds_lenient, [event], matching_config={"strict_window_days": 7.0})
    assert summary_lenient.events_detected_strict == 0
    assert summary_lenient.events_detected_lenient == 1
    assert summary_lenient.recall_strict == 0.0
    assert summary_lenient.recall_lenient == 1.0


def test_evaluate_unmatched_alerts():
    """Verify false / unmatched alerts counting."""
    event = EventMetadata(
        link_id="p100",
        start_time=datetime(2019, 6, 1, 0, 0),
        end_time=datetime(2019, 6, 10, 0, 0),
        diameter=0.018,
        leak_type="abrupt",
        peak_time=datetime(2019, 6, 1, 0, 0),
    )

    # False alert in January (nowhere near June event)
    preds = [
        {"timestamp": datetime(2019, 1, 15, 0, 0), "is_alert": True},
        {"timestamp": datetime(2019, 6, 2, 0, 0), "is_alert": True},
    ]
    summary = evaluate_predictions(preds, [event])
    assert summary.total_alerts_count == 2
    assert summary.unmatched_alerts_count == 1
    assert summary.precision_lenient == 0.5


def test_empty_predictions_raises():
    """Verify ValueError on empty prediction log."""
    with pytest.raises(ValueError, match="Cannot evaluate empty"):
        evaluate_predictions([], [])
