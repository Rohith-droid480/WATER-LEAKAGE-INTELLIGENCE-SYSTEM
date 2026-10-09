"""Interface adapter connecting AquaSentinel UI to Alpha and Beta core modules.

Responsibilities:
- Dynamically detect Alpha (data, baseline, detector) and Beta (evaluate) modules.
- Provide unified dataset loader that fits real baseline on 2018 and streams 2019 observations.
- Preserve explicit mock fallback when requested or when modules/data are unavailable.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("aquasentinel.interfaces")

# Detection flags
DATA_LOADER_AVAILABLE = False
BASELINE_AVAILABLE = False
DETECTOR_AVAILABLE = False
EVALUATOR_AVAILABLE = False

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

try:
    import evaluate as real_evaluate
    if hasattr(real_evaluate, "load_event_metadata") and hasattr(real_evaluate, "evaluate_predictions"):
        EVALUATOR_AVAILABLE = True
except ImportError:
    real_evaluate = None  # type: ignore

IS_REAL_PIPELINE_READY = (
    DATA_LOADER_AVAILABLE and BASELINE_AVAILABLE and DETECTOR_AVAILABLE and EVALUATOR_AVAILABLE
)

# Import mock components as fallback
import mock_interfaces

# Cache fitted baseline model across UI reruns to prevent repeated fitting
_CACHED_BASELINE_MODEL: Optional[Any] = None


def get_interface_status() -> Dict[str, Any]:
    """Return status of Alpha & Beta module bindings."""
    return {
        "is_mock": not IS_REAL_PIPELINE_READY,
        "data_loader_real": DATA_LOADER_AVAILABLE,
        "baseline_real": BASELINE_AVAILABLE,
        "detector_real": DETECTOR_AVAILABLE,
        "evaluator_real": EVALUATOR_AVAILABLE,
        "status_message": (
            "Connected to Real BattLeDIM Pipeline (data.py, baseline.py, detector.py, evaluate.py)"
            if IS_REAL_PIPELINE_READY
            else "MOCK INTERFACE ACTIVE (Some Alpha/Beta modules not yet loaded) — NOT real detection"
        ),
    }


def load_replay_dataset(
    year: int = 2019,
    kind: str = "flow",
    data_dir: str = "data",
    use_mock: bool = False,
    max_steps: Optional[int] = None,
) -> Tuple[List[Any], Dict[str, Any], Any]:
    """Load observations and baseline model.

    If use_mock=False and real pipeline is ready, loads real 2019 BattLeDIM
    telemetry and fits a robust baseline on 2018 training data.
    Otherwise, generates mock telemetry.
    """
    global _CACHED_BASELINE_MODEL

    if not use_mock and IS_REAL_PIPELINE_READY and real_data is not None and real_baseline is not None and real_evaluate is not None:
        logger.info(f"Loading real BattLeDIM {year} {kind} telemetry from {data_dir}...")

        # 1. Fit baseline on 2018 training data (cache in memory)
        if _CACHED_BASELINE_MODEL is None:
            train_df = real_data.load_telemetry(2018, kind=kind, data_dir=data_dir)
            events_2018 = real_evaluate.load_event_metadata(data_dir=data_dir, year=2018)
            mask_2018 = real_evaluate.build_training_mask(train_df["timestamp"], events_2018)
            # If mask excludes almost everything, use eligible or full 2018 with robust median/MAD
            valid_mask = mask_2018 if mask_2018.sum() > 500 else None
            _CACHED_BASELINE_MODEL = real_baseline.fit_baseline(train_df, valid_mask=valid_mask)

        baseline_model = _CACHED_BASELINE_MODEL

        # 2. Load 2019 replay observations
        replay_df = real_data.load_telemetry(year, kind=kind, data_dir=data_dir)
        if max_steps is not None and max_steps > 0:
            replay_df = replay_df.iloc[:max_steps]

        observations = list(real_data.iter_observations(replay_df))

        # 3. Configure channel parameters (k=0.75, h=8.0 for robust flow CUSUM)
        channel_configs = {
            ch: {
                "k": 0.75,
                "h": 8.0,
                "direction": "upper" if "flow" in kind or not ch.startswith("n") else "lower",
            }
            for ch in baseline_model.channels
        }

        return observations, channel_configs, baseline_model
    else:
        # Fallback to mock
        logger.info("Using mock dataset and mock baseline for UI replay harness")
        num_mock = max_steps if max_steps is not None else 150
        observations = mock_interfaces.generate_mock_telemetry(num_steps=num_mock)
        baseline_model = mock_interfaces.MockBaselineModel()
        channel_configs = {
            "FLOW_INLET_1": {"k": 0.5, "h": 5.0, "type": "flow"},
            "PRESS_ZONE_A": {"k": 0.5, "h": 4.5, "type": "pressure"},
        }
        return observations, channel_configs, baseline_model


def init_detector_state(channel_configs: Dict[str, Any], run_id: str, use_mock: bool = False) -> Any:
    """Initialize detector state."""
    if not use_mock and DETECTOR_AVAILABLE and real_detector is not None:
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
    use_mock: bool = False,
) -> Any:
    """Execute a single sequential detector step."""
    # Lookup baseline points for each observed channel
    baseline_points = {}
    for ch in observation.values.keys():
        if not use_mock and BASELINE_AVAILABLE and real_baseline is not None:
            baseline_points[ch] = real_baseline.lookup_baseline(baseline_model, timestamp, ch)
        else:
            baseline_points[ch] = mock_interfaces.lookup_baseline(baseline_model, timestamp, ch)

    if not use_mock and DETECTOR_AVAILABLE and real_detector is not None:
        return real_detector.step(detector_state, run_id, index, timestamp, observation, baseline_points)
    else:
        return mock_interfaces.detector_step(
            detector_state, run_id, index, timestamp, observation, baseline_points
        )
