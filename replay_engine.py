"""Deterministic Replay Engine and Session State Management for AquaSentinel.

Responsibilities:
- Maintain per-session replay state, unique run ID, and last-processed index.
- Provide deterministic play, pause, resume, reset, and end-of-data controls.
- Prevent repeated row processing (idempotency / protection against index <= last_processed_index).
- Maintain bounded chart history buffer alongside complete prediction log.
- Interface with Alpha's detector (or fallback mock) without duplicating detection logic.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import interfaces


@dataclass
class ReplaySession:
    """Encapsulates all runtime state for a single replay session."""

    run_id: str
    status: str  # "READY", "PLAYING", "PAUSED", "ENDED"
    replay_index: int
    last_processed_index: int
    observations: List[Any]
    channel_configs: Dict[str, Any]
    baseline_model: Any
    detector_state: Any
    chart_buffer_max_len: int = 120
    chart_history: List[Dict[str, Any]] = field(default_factory=list)
    prediction_log: List[Dict[str, Any]] = field(default_factory=list)
    incident_log: List[Dict[str, Any]] = field(default_factory=list)
    speed_batch_size: int = 1
    is_mock: bool = True

    @property
    def is_playing(self) -> bool:
        return self.status == "PLAYING"

    @property
    def is_paused(self) -> bool:
        return self.status == "PAUSED"

    @property
    def is_ended(self) -> bool:
        return self.status == "ENDED"

    @property
    def is_ready(self) -> bool:
        return self.status == "READY"

    @property
    def total_observations(self) -> int:
        return len(self.observations)

    @property
    def progress_fraction(self) -> float:
        if not self.observations:
            return 0.0
        return min(1.0, float(self.replay_index) / float(len(self.observations)))


def create_replay_session(
    observations: Optional[List[Any]] = None,
    channel_configs: Optional[Dict[str, Any]] = None,
    baseline_model: Optional[Any] = None,
    chart_buffer_max_len: int = 120,
    speed_batch_size: int = 1,
) -> ReplaySession:
    """Create a new replay session with a fresh run_id and clean initial state."""
    if observations is None or channel_configs is None or baseline_model is None:
        dataset_obs, d_configs, b_model = interfaces.load_replay_dataset()
        observations = observations or dataset_obs
        channel_configs = channel_configs or d_configs
        baseline_model = baseline_model or b_model

    run_id = str(uuid.uuid4())
    detector_state = interfaces.init_detector_state(channel_configs, run_id)
    status_info = interfaces.get_interface_status()

    return ReplaySession(
        run_id=run_id,
        status="READY",
        replay_index=0,
        last_processed_index=-1,
        observations=observations,
        channel_configs=channel_configs,
        baseline_model=baseline_model,
        detector_state=detector_state,
        chart_buffer_max_len=chart_buffer_max_len,
        chart_history=[],
        prediction_log=[],
        incident_log=[],
        speed_batch_size=speed_batch_size,
        is_mock=status_info["is_mock"],
    )


def reset_session(session: ReplaySession) -> ReplaySession:
    """Reset session: generates fresh run_id and wipes all runtime buffers."""
    new_run_id = str(uuid.uuid4())
    detector_state = interfaces.init_detector_state(session.channel_configs, new_run_id)

    session.run_id = new_run_id
    session.status = "READY"
    session.replay_index = 0
    session.last_processed_index = -1
    session.detector_state = detector_state
    session.chart_history.clear()
    session.prediction_log.clear()
    session.incident_log.clear()
    return session


def play_session(session: ReplaySession) -> None:
    """Start or resume playback."""
    if session.is_ended:
        return
    session.status = "PLAYING"


def pause_session(session: ReplaySession) -> None:
    """Pause playback."""
    if session.is_playing:
        session.status = "PAUSED"


def resume_session(session: ReplaySession) -> None:
    """Resume playback from paused state."""
    if session.is_paused:
        session.status = "PLAYING"


def step_session(session: ReplaySession, batch_size: Optional[int] = None) -> List[Any]:
    """Execute up to batch_size sequential steps.

    Repeated-row protection:
    - Never processes row if index <= session.last_processed_index.
    - Updates last_processed_index and replay_index sequentially.
    - Transitions to "ENDED" when all observations are processed.
    """
    if session.is_ended:
        return []

    count = batch_size if batch_size is not None else session.speed_batch_size
    step_results = []

    for _ in range(count):
        if session.replay_index >= len(session.observations):
            session.status = "ENDED"
            break

        obs = session.observations[session.replay_index]

        # Repeated-row guard
        if obs.index <= session.last_processed_index:
            # Advance pointer without re-processing
            session.replay_index += 1
            continue

        # Execute pure detector step via adapter
        step_res = interfaces.execute_detector_step(
            detector_state=session.detector_state,
            run_id=session.run_id,
            index=obs.index,
            timestamp=obs.timestamp,
            observation=obs,
            baseline_model=session.baseline_model,
            channel_configs=session.channel_configs,
        )

        step_results.append(step_res)

        # Build tabular record for UI charts and prediction log
        record = {
            "index": obs.index,
            "timestamp": obs.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if hasattr(obs.timestamp, "strftime")
            else str(obs.timestamp),
            "is_alert": step_res.is_alert,
        }

        for ch_id, ch_res in step_res.channels.items():
            record[f"{ch_id}_observed"] = ch_res.observed
            record[f"{ch_id}_expected"] = ch_res.expected
            record[f"{ch_id}_residual"] = ch_res.residual
            record[f"{ch_id}_cusum"] = ch_res.cusum_score
            record[f"{ch_id}_threshold"] = ch_res.threshold
            record[f"{ch_id}_status"] = ch_res.status

        # Update complete prediction log (unbounded)
        session.prediction_log.append(record)

        # Update bounded chart history (window of latest N points)
        session.chart_history.append(record)
        if len(session.chart_history) > session.chart_buffer_max_len:
            session.chart_history = session.chart_history[-session.chart_buffer_max_len :]

        # Record incident evidence if present
        if step_res.incident_evidence is not None:
            # Store in incident log if not duplicate of current onset
            existing_ids = {inc.get("incident_id") for inc in session.incident_log}
            inc_id = step_res.incident_evidence.get("incident_id")
            if inc_id not in existing_ids:
                session.incident_log.append(step_res.incident_evidence)

        # Update last processed index and next replay index
        session.last_processed_index = obs.index
        session.replay_index = obs.index + 1

    if session.replay_index >= len(session.observations):
        session.status = "ENDED"

    return step_results
