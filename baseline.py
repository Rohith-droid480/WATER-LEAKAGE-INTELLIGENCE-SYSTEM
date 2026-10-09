"""AquaSentinel Baseline Module (Alpha Owned).

Responsibilities:
- Fit robust historical baseline profiles on eligible 2018 training data.
- Support day-of-week + time-of-day (2016 bins) robust median and MAD-derived scale.
- Enforce near-zero scale fallback policy using pooled robust scale.
- Deterministic, pure lookup function returning expected value, scale, and status.
- Zero label awareness: accepts only an external boolean valid_mask, never raw labels.
- Zero online adaptation during suspected incidents.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BaselinePoint:
    """Expected value and scale for a channel at a specific timestamp."""
    expected: float
    scale: float
    status: str = "VALID"  # "VALID", "POOLED_SCALE", "UNAVAILABLE"


class BaselineModel:
    """Stores fitted baseline profiles and pooled scales for sensor channels."""

    def __init__(
        self,
        profiles: Dict[str, Dict[Tuple[int, int], Tuple[float, float, str]]],
        pooled_scales: Dict[str, float],
        global_medians: Dict[str, float],
        method: str = "median_mad",
        training_rows_eligible: int = 0,
    ) -> None:
        self.profiles = profiles
        self.pooled_scales = pooled_scales
        self.global_medians = global_medians
        self.method = method
        self.training_rows_eligible = training_rows_eligible
        self.channels = list(profiles.keys())

    def lookup(self, timestamp: datetime, channel_id: str) -> BaselinePoint:
        """Query expected value and scale for a channel at a given timestamp."""
        if channel_id not in self.profiles:
            return BaselinePoint(expected=0.0, scale=1.0, status="UNAVAILABLE")

        day_of_week = timestamp.weekday()
        slot = (timestamp.hour * 60 + timestamp.minute) // 5

        bin_data = self.profiles[channel_id].get((day_of_week, slot))
        if bin_data is not None:
            expected, scale, status = bin_data
            return BaselinePoint(expected=round(expected, 4), scale=round(scale, 4), status=status)

        # Fallback to global median and pooled scale if bin was somehow empty
        pooled = self.pooled_scales.get(channel_id, 1.0)
        global_med = self.global_medians.get(channel_id, 0.0)
        return BaselinePoint(expected=round(global_med, 4), scale=round(pooled, 4), status="POOLED_SCALE")


def _compute_mad(values: np.ndarray, center: float) -> float:
    """Compute Median Absolute Deviation (MAD) scaled to normal distribution."""
    if len(values) == 0:
        return 0.0
    abs_deviations = np.abs(values - center)
    mad = float(np.median(abs_deviations))
    # Normal consistency constant: 1.4826
    return 1.4826 * mad


def fit_baseline(
    train_frame: pd.DataFrame,
    valid_mask: Optional[Union[np.ndarray, pd.Series, List[bool]]] = None,
    profile_config: Optional[Dict[str, Any]] = None,
) -> BaselineModel:
    """Fit robust historical profiles on eligible training observations.

    Args:
        train_frame: DataFrame of historical training telemetry (must include 'timestamp').
        valid_mask: Boolean array where True indicates eligible observations.
                    If None, all observations are considered eligible.
        profile_config: Configuration dictionary (e.g. {'method': 'median_mad'}).

    Returns:
        Fitted BaselineModel.
    """
    if "timestamp" not in train_frame.columns:
        raise ValueError("train_frame must contain a 'timestamp' column.")

    config = profile_config or {}
    method = config.get("method", "median_mad")
    min_samples_per_bin = config.get("min_samples", 3)
    near_zero_scale_threshold = config.get("near_zero_scale", 1e-4)

    # Filter by valid_mask
    if valid_mask is not None:
        mask_arr = np.asarray(valid_mask, dtype=bool)
        if len(mask_arr) != len(train_frame):
            raise ValueError(
                f"valid_mask length ({len(mask_arr)}) does not match train_frame ({len(train_frame)})."
            )
        eligible_df = train_frame[mask_arr].copy()
    else:
        eligible_df = train_frame.copy()

    eligible_rows = len(eligible_df)
    if eligible_rows == 0:
        raise ValueError("No eligible observations in train_frame after applying valid_mask.")

    channel_cols = [c for c in eligible_df.columns if c != "timestamp"]
    if not channel_cols:
        raise ValueError("train_frame contains no telemetry channels to fit.")

    # Compute time context indices
    dow_series = eligible_df["timestamp"].dt.weekday
    slot_series = (eligible_df["timestamp"].dt.hour * 60 + eligible_df["timestamp"].dt.minute) // 5
    eligible_df["_dow"] = dow_series
    eligible_df["_slot"] = slot_series

    profiles: Dict[str, Dict[Tuple[int, int], Tuple[float, float, str]]] = {}
    pooled_scales: Dict[str, float] = {}
    global_medians: Dict[str, float] = {}

    for ch in channel_cols:
        vals = eligible_df[ch].dropna().to_numpy()
        if len(vals) == 0:
            continue

        global_med = float(np.median(vals))
        global_medians[ch] = global_med

        # Pooled robust scale across all eligible training data
        pooled_mad = _compute_mad(vals, global_med)
        if pooled_mad <= near_zero_scale_threshold:
            # Fallback to standard deviation or minimum floor
            pooled_std = float(np.std(vals))
            pooled_mad = max(pooled_std, 1.0)
        pooled_scales[ch] = pooled_mad

        ch_profile: Dict[Tuple[int, int], Tuple[float, float, str]] = {}

        # Group by (day_of_week, 5-min slot)
        grouped = eligible_df.groupby(["_dow", "_slot"])[ch]
        for (dow, slot), group_vals in grouped:
            arr = group_vals.dropna().to_numpy()
            n_samples = len(arr)

            if method == "mean_std":
                center = float(np.mean(arr)) if n_samples > 0 else global_med
                scale = float(np.std(arr)) if n_samples > 1 else pooled_mad
            else:
                center = float(np.median(arr)) if n_samples > 0 else global_med
                scale = _compute_mad(arr, center) if n_samples > 0 else pooled_mad

            # Scale policy: if near-zero or low samples, fallback to pooled scale
            if scale <= near_zero_scale_threshold or n_samples < min_samples_per_bin:
                scale = pooled_mad
                status = "POOLED_SCALE"
            else:
                status = "VALID"

            ch_profile[(int(dow), int(slot))] = (center, scale, status)

        profiles[ch] = ch_profile

    return BaselineModel(
        profiles=profiles,
        pooled_scales=pooled_scales,
        global_medians=global_medians,
        method=method,
        training_rows_eligible=eligible_rows,
    )


def lookup_baseline(
    model: BaselineModel,
    timestamp: datetime,
    channel_id: str,
) -> BaselinePoint:
    """Convenience functional lookup conforming to INTERFACE_CONTRACTS.md."""
    return model.lookup(timestamp, channel_id)
