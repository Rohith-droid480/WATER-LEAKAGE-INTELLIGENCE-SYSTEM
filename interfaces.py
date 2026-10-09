"""Interface adapter connecting AquaSentinel UI to Alpha's core detection modules.

Per requirement:
"Integrate with Alpha's real data-loader, baseline, and detector interfaces.
If they are not ready, define a small mock interface for UI development and
clearly label it as mock—not as real detection."
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("aquasentinel.interfaces")

# Detection flags
DATA_LOADER_AVAILABLE = False
BASELINE_AVAILABLE = False
DETECTOR_AVAILABLE = False

try:
    import data as real_data
    if hasattr(real_data, "load_telemetry") and hasattr(real_data, "iter_observations"):
        DATA_LOADER_AVAILABLE = True
except ImportError:
    real_data = None  # type: ignore

try:
    import baseline as real_baseline
    if hasattr(real_baseline, "fit_baseline") and hasattr(real_baseline, "lookup_baseline"):
        BASELINE_AVAILABLE = True
except ImportError:
    real_baseline = None  # type: ignore

try:
    import detector as real_detector
    if hasattr(real_detector, "init_detector") and hasattr(real_detector, "step"):
        DETECTOR_AVAILABLE = True
except ImportError:
    real_detector = None  # type: ignore

IS_MOCK = not (DATA_LOADER_AVAILABLE and BASELINE_AVAILABLE and DETECTOR_AVAILABLE)

# Import mock components as fallback
import mock_interfaces


def get_interface_status() -> Dict[str, Any]:
    """Return status of Alpha module bindings."""
    return {
        "is_mock": IS_MOCK,
        "data_loader_real": DATA_LOADER_AVAILABLE,
        "baseline_real": BASELINE_AVAILABLE,
        "detector_real": DETECTOR_AVAILABLE,
        "status_message": (
            "Connected to Alpha's real detector pipeline"
            if not IS_MOCK
            else "MOCK INTERFACE ACTIVE (Alpha's data.py, baseline.py, or detector.py not yet ready) — NOT real detection"
        ),
    }


def load_replay_dataset(num_mock_steps: int = 150) -> Tuple[List[Any], Dict[str, Any], Any]:
    """Load observations and baseline model.

    If Alpha modules are ready, loads real data.
    Otherwise, generates mock observations and baseline.
    """
    if DATA_LOADER_AVAILABLE and BASELINE_AVAILABLE and real_data is not None and real_baseline is not None:
        # Alpha's real pipeline
        logger.info("Loading observations via Alpha's real data loader")
        observations = list(real_data.iter_observations(real_data.load_telemetry(2019, "flow", "data")))
        # Real baseline would be fitted here
        baseline_model = real_baseline.fit_baseline(None, None, {})
        channel_configs = {"FLOW": {"k": 0.5, "h": 5.0}}
        return observations, channel_configs, baseline_model
    else:
        # Fallback to mock
        logger.info("Using mock dataset and mock baseline for UI replay harness")
        observations = mock_interfaces.generate_mock_telemetry(num_steps=num_mock_steps)
        baseline_model = mock_interfaces.MockBaselineModel()
        channel_configs = {
            "FLOW_INLET_1": {"k": 0.5, "h": 5.0, "type": "flow"},
            "PRESS_ZONE_A": {"k": 0.5, "h": 4.5, "type": "pressure"},
        }
        return observations, channel_configs, baseline_model


def init_detector_state(channel_configs: Dict[str, Any], run_id: str) -> Any:
    """Initialize detector state."""
    if DETECTOR_AVAILABLE and real_detector is not None:
        return real_detector.init_detector(channel_configs, run_id)
    return mock_interfaces.init_detector(channel_configs, run_id)


def execute_detector_step(
    detector_state: Any,
    run_id: str,
    index: int,
    timestamp: Any,
    observation: Any,
    baseline_model: Any,
    channel_configs: Dict[str, Any],
) -> Any:
    """Execute a single sequential detector step."""
    # Lookup baseline points for each observed channel
    baseline_points = {}
    for ch in observation.values.keys():
        if BASELINE_AVAILABLE and real_baseline is not None:
            baseline_points[ch] = real_baseline.lookup_baseline(baseline_model, timestamp, ch)
        else:
            baseline_points[ch] = mock_interfaces.lookup_baseline(baseline_model, timestamp, ch)

    if DETECTOR_AVAILABLE and real_detector is not None:
        return real_detector.step(detector_state, run_id, index, timestamp, observation, baseline_points)
    else:
        return mock_interfaces.detector_step(
            detector_state, run_id, index, timestamp, observation, baseline_points
        )
