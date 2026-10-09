"""AquaSentinel Detector Module (Alpha Owned).

Responsibilities:
- Pure, deterministic, channel-aware one-sided CUSUM detector.
- Enforce idempotency: rejects duplicate index (index <= last_processed_index) without state mutation.
- Enforce run safety: rejects stale run_id without state mutation.
- Support directional detection (upper-sided for flow increase, lower-sided for pressure drop).
- Emit structured StepResult and maintain incident states (NORMAL, SUSPECTED_ACTIVE).
- Disclaimers strictly enforced: no calibrated probabilities, no confirmed-leak claims.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from data import Observation


@dataclass
class ChannelStepResult:
    """Detection output for a single channel at one time step."""
    channel_id: str
    observed: float
    expected: float
    residual: float
    z_score: float
    cusum_score: float
    threshold: float
    is_alert: bool
    direction: str  # "upper" or "lower"
    status: str = "NORMAL"  # "NORMAL", "SUSPECTED_ACTIVE"


@dataclass
class StepResult:
    """Output of detector step for a single observation index."""
    run_id: str
    index: int
    timestamp: datetime
    channels: Dict[str, ChannelStepResult]
    is_alert: bool
    incident_evidence: Optional[Dict[str, Any]] = None
    data_quality_status: str = "OK"


@dataclass
class DetectorState:
    """Encapsulates mutable detector state across steps."""
    run_id: str
    channel_configs: Dict[str, Dict[str, Any]]
    last_processed_index: int = -1
    channel_scores: Dict[str, float] = field(default_factory=dict)
    active_incidents: Dict[str, Dict[str, Any]] = field(default_factory=dict)


def init_detector(
    channel_configs: Dict[str, Dict[str, Any]],
    run_id: str,
) -> DetectorState:
    """Initialize detector state with zeroed accumulators and clean index."""
    initial_scores = {ch: 0.0 for ch in channel_configs}
    return DetectorState(
        run_id=run_id,
        channel_configs=channel_configs,
        last_processed_index=-1,
        channel_scores=initial_scores,
        active_incidents={},
    )


def step(
    state: DetectorState,
    run_id: str,
    index: int,
    timestamp: datetime,
    observation: Observation,
    baseline_points: Dict[str, Any],
) -> StepResult:
    """Execute a single deterministic detector step.

    Invariants:
    1. If run_id != state.run_id: rejects without mutating state.
    2. If index <= state.last_processed_index: rejects without mutating state.
    3. Handles near-zero or unavailable baseline scale safely.
    """
    if run_id != state.run_id:
        raise ValueError(f"Stale run_id rejected: expected '{state.run_id}', received '{run_id}'.")

    if index <= state.last_processed_index:
        raise ValueError(
            f"Repeated row rejected: index {index} <= last_processed_index {state.last_processed_index}."
        )

    channel_results: Dict[str, ChannelStepResult] = {}
    any_alert = False

    for ch_id, obs_val in observation.values.items():
        cfg = state.channel_configs.get(ch_id, {})
        k = float(cfg.get("k", 0.5))
        h = float(cfg.get("h", 5.0))
        # Direction: "upper" (flow inlet increases) or "lower" (pressure drops)
        direction = cfg.get("direction", "lower" if "press" in ch_id.lower() or ch_id.startswith("n") else "upper")

        bp = baseline_points.get(ch_id)
        if bp is None or getattr(bp, "status", "") == "UNAVAILABLE" or getattr(bp, "scale", 1.0) <= 1e-6:
            # Scale unavailable: mark normal, no update to accumulator
            prev_score = state.channel_scores.get(ch_id, 0.0)
            channel_results[ch_id] = ChannelStepResult(
                channel_id=ch_id,
                observed=obs_val,
                expected=getattr(bp, "expected", obs_val),
                residual=0.0,
                z_score=0.0,
                cusum_score=round(prev_score, 4),
                threshold=h,
                is_alert=False,
                direction=direction,
                status="SCALE_UNAVAILABLE",
            )
            continue

        expected_val = float(bp.expected)
        scale_val = float(bp.scale)
        residual = obs_val - expected_val

        # Standardized residual according to channel direction
        if direction == "lower":
            z_score = (-residual) / scale_val
        else:
            z_score = residual / scale_val

        prev_score = state.channel_scores.get(ch_id, 0.0)
        # One-sided CUSUM: S_t = max(0, S_{t-1} + z_t - k)
        new_score = max(0.0, prev_score + z_score - k)
        state.channel_scores[ch_id] = round(new_score, 4)

        is_alert = new_score > h
        if is_alert:
            any_alert = True

        status = "SUSPECTED_ACTIVE" if is_alert else "NORMAL"

        channel_results[ch_id] = ChannelStepResult(
            channel_id=ch_id,
            observed=obs_val,
            expected=expected_val,
            residual=round(residual, 3),
            z_score=round(z_score, 3),
            cusum_score=round(new_score, 3),
            threshold=h,
            is_alert=is_alert,
            direction=direction,
            status=status,
        )

    # Commit last processed index
    state.last_processed_index = index

    # Build incident evidence if an alert was triggered
    incident_evidence = None
    if any_alert:
        alerting_channels = [ch for ch, res in channel_results.items() if res.is_alert]
        max_cusum = max((res.cusum_score for res in channel_results.values()), default=0.0)
        incident_evidence = {
            "incident_id": f"INC-{run_id[:6]}-{index}",
            "onset_index": index,
            "timestamp": timestamp.isoformat() if hasattr(timestamp, "isoformat") else str(timestamp),
            "contributing_channels": alerting_channels,
            "max_cusum_score": max_cusum,
            "status": "SUSPECTED_ACTIVE",
            "evidence_note": (
                "Suspected persistent statistical shift exceeding CUSUM decision interval h. "
                "Requires operator review. Not a confirmed leak."
            ),
        }
        state.active_incidents[str(index)] = incident_evidence

    return StepResult(
        run_id=run_id,
        index=index,
        timestamp=timestamp,
        channels=channel_results,
        is_alert=any_alert,
        incident_evidence=incident_evidence,
        data_quality_status="OK",
    )


def build_incidents(
    step_results: List[StepResult],
    incident_config: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Aggregate step results into coherent incident intervals."""
    incidents: List[Dict[str, Any]] = []
    current_incident: Optional[Dict[str, Any]] = None

    for sr in step_results:
        if sr.is_alert:
            alerting_ch = [ch for ch, res in sr.channels.items() if res.is_alert]
            if current_incident is None:
                current_incident = {
                    "incident_id": f"INC-{sr.run_id[:6]}-{sr.index}",
                    "start_index": sr.index,
                    "end_index": sr.index,
                    "start_timestamp": sr.timestamp,
                    "end_timestamp": sr.timestamp,
                    "contributing_channels": set(alerting_ch),
                    "peak_cusum": max(res.cusum_score for res in sr.channels.values()),
                    "status": "SUSPECTED_ACTIVE",
                }
            else:
                current_incident["end_index"] = sr.index
                current_incident["end_timestamp"] = sr.timestamp
                current_incident["contributing_channels"].update(alerting_ch)
                current_incident["peak_cusum"] = max(
                    current_incident["peak_cusum"],
                    max(res.cusum_score for res in sr.channels.values()),
                )
        else:
            if current_incident is not None:
                current_incident["contributing_channels"] = sorted(list(current_incident["contributing_channels"]))
                incidents.append(current_incident)
                current_incident = None

    if current_incident is not None:
        current_incident["contributing_channels"] = sorted(list(current_incident["contributing_channels"]))
        incidents.append(current_incident)

    return incidents
