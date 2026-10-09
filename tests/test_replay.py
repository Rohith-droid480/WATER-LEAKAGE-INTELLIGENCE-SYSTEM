"""Unit tests for AquaSentinel Replay Engine and Session State Management.

Covers:
- Replay state initialization
- Play / Pause / Resume controls
- Reset behavior and fresh run ID generation
- Repeated-row protection (idempotency against index <= last_processed_index)
- Stale run ID rejection
- Bounded chart history vs unbounded prediction log
- End-of-data detection and terminal state handling
- Incident evidence capture
"""

import pytest

import mock_interfaces
from replay_engine import (
    ReplaySession,
    create_replay_session,
    pause_session,
    play_session,
    reset_session,
    resume_session,
    step_session,
)


def test_replay_session_initial_state():
    """Verify fresh session initialization and invariant contracts."""
    session = create_replay_session()

    assert session.status == "READY"
    assert session.is_ready is True
    assert session.is_playing is False
    assert session.is_paused is False
    assert session.is_ended is False
    assert session.replay_index == 0
    assert session.last_processed_index == -1
    assert len(session.chart_history) == 0
    assert len(session.prediction_log) == 0
    assert len(session.incident_log) == 0
    assert len(session.run_id) > 0
    assert session.total_observations > 0


def test_play_pause_resume_transitions():
    """Verify play, pause, and resume state transitions."""
    session = create_replay_session()

    play_session(session)
    assert session.status == "PLAYING"
    assert session.is_playing is True

    pause_session(session)
    assert session.status == "PAUSED"
    assert session.is_paused is True

    resume_session(session)
    assert session.status == "PLAYING"
    assert session.is_playing is True


def test_reset_behavior_and_fresh_run_id():
    """Verify reset clears buffers and assigns a new run ID."""
    session = create_replay_session()
    initial_run_id = session.run_id

    # Step 15 rows
    results = step_session(session, batch_size=15)
    assert len(results) == 15
    assert session.replay_index == 15
    assert session.last_processed_index == 14
    assert len(session.prediction_log) == 15

    # Reset
    reset_session(session)
    assert session.status == "READY"
    assert session.run_id != initial_run_id
    assert session.replay_index == 0
    assert session.last_processed_index == -1
    assert len(session.chart_history) == 0
    assert len(session.prediction_log) == 0
    assert len(session.incident_log) == 0


def test_repeated_row_protection_in_detector():
    """Verify mock detector rejects index <= last_processed_index."""
    detector_state = mock_interfaces.init_detector({"FLOW_INLET_1": {}}, "test-run-1")
    obs = mock_interfaces.Observation(
        timestamp=mock_interfaces.datetime(2019, 1, 1, 0, 0),
        index=0,
        values={"FLOW_INLET_1": 120.0},
    )
    bp = {"FLOW_INLET_1": mock_interfaces.BaselinePoint(expected=120.0, scale=2.5)}

    # First step succeeds
    res1 = mock_interfaces.detector_step(detector_state, "test-run-1", 0, obs.timestamp, obs, bp)
    assert res1.index == 0
    assert detector_state.last_processed_index == 0

    # Repeating same index MUST raise ValueError and not mutate state
    with pytest.raises(ValueError, match="Repeated row rejected"):
        mock_interfaces.detector_step(detector_state, "test-run-1", 0, obs.timestamp, obs, bp)

    # Stale run ID MUST raise ValueError
    with pytest.raises(ValueError, match="Stale run_id"):
        mock_interfaces.detector_step(detector_state, "other-stale-run", 1, obs.timestamp, obs, bp)


def test_repeated_row_protection_in_replay_engine():
    """Verify replay engine guards against re-processing past rows."""
    # Create observations with a duplicate index injected
    base_obs = mock_interfaces.generate_mock_telemetry(num_steps=5)
    # Duplicate index 1
    dup_obs = [base_obs[0], base_obs[1], base_obs[1], base_obs[2]]

    configs = {"FLOW_INLET_1": {"k": 0.5, "h": 5.0}}
    b_model = mock_interfaces.MockBaselineModel()
    session = create_replay_session(
        observations=dup_obs,
        channel_configs=configs,
        baseline_model=b_model,
    )

    # Step through all 4 items
    step_session(session, batch_size=4)

    # The duplicate index 1 should have been skipped, resulting in exactly 3 processed predictions (0, 1, 2)
    processed_indices = [row["index"] for row in session.prediction_log]
    assert processed_indices == [0, 1, 2]
    assert len(session.prediction_log) == 3
    assert session.last_processed_index == 2


def test_bounded_chart_history_vs_complete_log():
    """Verify bounded rolling window does not grow indefinitely while log captures all."""
    session = create_replay_session(chart_buffer_max_len=10)

    # Step 25 items
    step_session(session, batch_size=25)

    assert len(session.prediction_log) == 25
    assert len(session.chart_history) == 10

    # Bounded buffer must contain the latest 10 items (indices 15 through 24)
    buffer_indices = [row["index"] for row in session.chart_history]
    assert buffer_indices == list(range(15, 25))


def test_end_of_data_control():
    """Verify engine transitions to ENDED and stops cleanly."""
    tiny_obs = mock_interfaces.generate_mock_telemetry(num_steps=3)
    session = create_replay_session(observations=tiny_obs)

    play_session(session)
    assert session.is_playing is True

    # Step 3 items
    step_session(session, batch_size=3)

    assert session.status == "ENDED"
    assert session.is_ended is True
    assert session.is_playing is False
    assert session.replay_index == 3
    assert session.last_processed_index == 2

    # Subsequent steps return empty and do not crash
    more = step_session(session, batch_size=2)
    assert more == []
    assert session.status == "ENDED"


def test_incident_evidence_capture():
    """Verify threshold crossing generates suspected incident evidence with disclaimer."""
    session = create_replay_session(use_mock=True)

    # Step until past anomalous injected interval (step 35 to 55)
    step_session(session, batch_size=55)

    # Should have triggered at least one suspected alert
    assert len(session.incident_log) > 0
    first_incident = session.incident_log[0]

    assert "incident_id" in first_incident
    assert first_incident["status"] == "SUSPECTED_ACTIVE"
    assert "FLOW_INLET_1" in first_incident["contributing_channels"]
    assert "Suspected statistical shift" in first_incident["evidence_note"]
