"""Mock interfaces for AquaSentinel UI development and replay harness.

NOTICE / DISCLAIMER:
These are MOCK interfaces designed strictly for UI development, testing,
and benchmark replay demonstration when Alpha's core detection modules
(data.py, baseline.py, detector.py) are not yet available.
THIS IS NOT REAL DETECTION LOGIC AND NOT FIELD VALIDATION.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Iterator, List, Optional


@dataclass(frozen=True)
class Observation:
    """Telemetry observation row."""
    timestamp: datetime
    index: int
    values: Dict[str, float]


@dataclass(frozen=True)
class BaselinePoint:
    """Expected value and scale for a channel at a given time."""
    expected: float
    scale: float
    status: str = "VALID"  # VALID, UNAVAILABLE, POOLED_SCALE


@dataclass
class ChannelStepResult:
    """Result of detector step for a single channel."""
    channel_id: str
    observed: float
    expected: float
    residual: float
    z_score: float
    cusum_score: float
    threshold: float
    is_alert: bool
    status: str = "NORMAL"  # NORMAL, SUSPECTED_ACTIVE


@dataclass
class StepResult:
    """Output of detector.step() for a single replay index."""
    run_id: str
    index: int
    timestamp: datetime
    channels: Dict[str, ChannelStepResult]
    is_alert: bool
    incident_evidence: Optional[Dict[str, Any]] = None
    data_quality_status: str = "OK"


@dataclass
class DetectorState:
    """Detector state tracking channel accumulators."""
    run_id: str
    last_processed_index: int = -1
    channel_scores: Dict[str, float] = field(default_factory=dict)
    active_incidents: Dict[str, Dict[str, Any]] = field(default_factory=dict)


# --- MOCK DATA LOADER ---

def generate_mock_telemetry(num_steps: int = 150) -> List[Observation]:
    """Generate deterministic synthetic telemetry with realistic sensor channels.

    Injects an anomalous rise on FLOW_INLET_1 starting at step 35
    to test threshold crossing and incident evidence UI.
    """
    base_time = datetime(2019, 1, 1, 0, 0, 0)
    observations: List[Observation] = []

    for idx in range(num_steps):
        ts = base_time + timedelta(minutes=5 * idx)
        # Diurnal pattern (period 24h = 288 steps of 5 min)
        phase = (2.0 * math.pi * (idx % 288)) / 288.0

        # Normal diurnal flow around 120 m3/h +/- 25
        flow_base = 120.0 + 25.0 * math.sin(phase)
        # Normal diurnal pressure around 45 m +/- 5 (out of phase)
        press_base = 45.0 - 5.0 * math.sin(phase)

        # Subtle noise
        pseudo_noise = 0.5 * math.sin(idx * 1.7)

        flow_val = flow_base + pseudo_noise
        press_val = press_base - 0.2 * pseudo_noise

        # Synthetic anomaly injected between step 35 and step 75
        if 35 <= idx <= 75:
            # Gradual ramp simulating leak-like persistent increase
            leak_intensity = min(18.0, 0.6 * (idx - 35))
            flow_val += leak_intensity
            press_val -= 0.15 * leak_intensity

        obs = Observation(
            timestamp=ts,
            index=idx,
            values={
                "FLOW_INLET_1": round(flow_val, 2),
                "PRESS_ZONE_A": round(press_val, 2),
            },
        )
        observations.append(obs)

    return observations


def iter_observations(observations: List[Observation], start_index: int = 0) -> Iterator[Observation]:
    """Iterate through observations strictly in order."""
    for obs in observations:
        if obs.index >= start_index:
            yield obs


# --- MOCK BASELINE MODEL ---

class MockBaselineModel:
    """Mock baseline model providing expected value and scale."""

    def __init__(self) -> None:
        self.scales = {
            "FLOW_INLET_1": 2.5,
            "PRESS_ZONE_A": 0.8,
        }

    def lookup(self, timestamp: datetime, channel_id: str) -> BaselinePoint:
        # Time-of-day expected value matching baseline diurnal curve
        minute_of_day = timestamp.hour * 60 + timestamp.minute
        phase = (2.0 * math.pi * minute_of_day) / 1440.0

        if channel_id == "FLOW_INLET_1":
            expected = 120.0 + 25.0 * math.sin(phase)
            scale = self.scales.get(channel_id, 2.5)
        elif channel_id == "PRESS_ZONE_A":
            expected = 45.0 - 5.0 * math.sin(phase)
            scale = self.scales.get(channel_id, 0.8)
        else:
            expected = 100.0
            scale = 1.0

        return BaselinePoint(expected=round(expected, 2), scale=scale, status="VALID")


def lookup_baseline(model: MockBaselineModel, timestamp: datetime, channel_id: str) -> BaselinePoint:
    return model.lookup(timestamp, channel_id)


# --- MOCK DETECTOR ---

def init_detector(channel_configs: Dict[str, Dict[str, float]], run_id: str) -> DetectorState:
    """Initialize detector state."""
    scores = {ch: 0.0 for ch in channel_configs}
    return DetectorState(run_id=run_id, last_processed_index=-1, channel_scores=scores)


def detector_step(
    state: DetectorState,
    run_id: str,
    index: int,
    timestamp: datetime,
    observation: Observation,
    baseline_points: Dict[str, BaselinePoint],
    k: float = 0.5,
    h: float = 5.0,
) -> StepResult:
    """Mock CUSUM step following INTERFACE_CONTRACTS.md.

    Guarantees:
    - Rejects stale run_id.
    - Idempotent: rejects index <= state.last_processed_index without mutating state.
    """
    if run_id != state.run_id:
        raise ValueError(f"Stale run_id: expected {state.run_id}, got {run_id}")

    if index <= state.last_processed_index:
        # Repeated row protection: do not mutate state
        raise ValueError(
            f"Repeated row rejected: index {index} <= last_processed_index {state.last_processed_index}"
        )

    channel_results: Dict[str, ChannelStepResult] = {}
    any_alert = False

    for ch_id, obs_val in observation.values.items():
        bp = baseline_points.get(ch_id)
        if bp is None or bp.scale <= 1e-6:
            # Fallback or unavailable
            bp = BaselinePoint(expected=obs_val, scale=1.0, status="UNAVAILABLE")

        residual = obs_val - bp.expected
        # For flow inlet, expected increase: z = residual / scale
        # For pressure, expected decrease: z = -residual / scale
        if "PRESS" in ch_id:
            z_score = (-residual) / bp.scale
        else:
            z_score = residual / bp.scale

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
            expected=bp.expected,
            residual=round(residual, 3),
            z_score=round(z_score, 3),
            cusum_score=round(new_score, 3),
            threshold=h,
            is_alert=is_alert,
            status=status,
        )

    # Update last processed index
    state.last_processed_index = index

    # Build incident evidence if threshold crossed
    incident_evidence = None
    if any_alert:
        alerting_channels = [ch for ch, res in channel_results.items() if res.is_alert]
        incident_evidence = {
            "incident_id": f"INC-{run_id[:6]}-{index}",
            "onset_index": index,
            "timestamp": timestamp.isoformat(),
            "contributing_channels": alerting_channels,
            "max_cusum_score": max(res.cusum_score for res in channel_results.values()),
            "status": "SUSPECTED_ACTIVE",
            "evidence_note": "Suspected statistical shift exceeding CUSUM decision interval h. Verification required.",
        }
        state.active_incidents[index] = incident_evidence

    return StepResult(
        run_id=run_id,
        index=index,
        timestamp=timestamp,
        channels=channel_results,
        is_alert=any_alert,
        incident_evidence=incident_evidence,
        data_quality_status="OK",
    )
