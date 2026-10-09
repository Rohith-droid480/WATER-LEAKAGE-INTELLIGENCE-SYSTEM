# AquaSentinel — Interface Contracts (Freeze Before Parallel Work)

Purpose: let Alpha, Beta, and Gamma work independently without editing the same core files. These are intended contracts. If inspection shows an incompatible existing implementation, stop and ask Alpha before changing them.

## Data representation

- Telemetry tables contain a timestamp column plus verified sensor/link/node columns.
- Event labels/configuration are separate from telemetry.
- Sensor IDs, units, sign/direction and timestamp semantics come from actual files and source metadata, never guessed names.
- Every output row retains a source timestamp and a monotonically increasing replay index.
- No 2019 event label is available to the prediction path.

## `data.py` — Alpha owns

Proposed public responsibilities:
- `load_telemetry(year, kind, data_dir) -> DataFrame`
- `validate_telemetry(frame, expected_interval_minutes=5) -> ValidationReport`
- `iter_observations(frame, start_index=0) -> iterable[Observation]`

`kind` may identify flow or pressure. Do not hardcode channel IDs. `Observation` should carry source timestamp, replay index, and verified channel values. Data loading must not implicitly load evaluation labels.

## `baseline.py` — Alpha owns

Proposed responsibilities:
- `fit_baseline(train_frame, valid_mask, profile_config) -> BaselineModel`
- `lookup_baseline(model, timestamp, channel_id) -> BaselinePoint`

`valid_mask` is a Boolean array aligned with the training frame; `True` means eligible for baseline fitting. `evaluate.py` may produce the mask from known 2018 leak-active intervals. `baseline.py` receives only the mask, never raw labels. The model returns expected value, scale, and validity status. Near-zero scale must not produce infinity.

## `detector.py` — Alpha owns

Proposed responsibilities:
- `init_detector(channel_configs, run_id) -> DetectorState`
- `step(state, run_id, index, timestamp, observation, baseline_points) -> StepResult`
- `build_incidents(step_results, incident_config) -> IncidentLog` (or incident management within the detector module)

`step` must be deterministic and idempotent. If the `run_id` is stale or `index <= last_processed_index`, it must not mutate the state. Result fields should include timestamp, index, per-channel score, threshold status, residual/evidence fields and data-quality status. Do not call the score probability/confidence.

## `evaluate.py` — Beta owns

The only label-aware module:
- `load_event_metadata(data_dir, year) -> EventMetadata`
- `build_training_mask(timestamps, event_metadata) -> BooleanArray`
- `evaluate_predictions(predictions, event_metadata, matching_config) -> EvaluationSummary`

`build_training_mask` is permitted for the 2018 fitting path only. For 2019, `load_event_metadata`/evaluation cannot be called until the prediction log is finalized. Event metadata must be verified against the leakage series. The evaluator reports strict/lenient matching when overlaps are ambiguous.

`EvaluationSummary` should expose actual counts as well as metrics: events eligible, detected, missed, unmatched alerts, precision/recall, false alerts per simulated month, delays evaluable, delay values/summary and recall by size when supported. Do not fabricate fields for missing truth.

## `app.py` — Gamma owns

Consumes the public contracts above. It must not implement CUSUM logic itself. It owns:
- Replay start/pause/resume/reset/speed controls.
- Per-session state and `run_id`.
- Sequential batch controller calling detector `step` in order.
- Bounded chart window plus separate full prediction log.
- Live-style observed-vs-baseline, residual/CUSUM timeline, alert cards and computed evaluation view.
- Permanent banner: “Benchmark Replay — simulated data, not live municipal telemetry.”

Do not call Streamlit render functions inside the row loop. `parallel=False`.

## Change protocol

Any change to these contracts is a cross-cutting/T2 decision. Stop and propose the change in `DECISION_LOG.md`; Alpha/Human approves before files are changed. No role may edit another role's owned files without an explicit handoff.
