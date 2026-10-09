# AquaSentinel — Three-Hour Build Plan

**Hard timebox:** 2 hours 50 minutes maximum, with a 10-minute buffer.  
**Priority:** working data-to-alert-to-evaluation path before visual polish.  
**Alpha:** Human/primary builder of core detection.  
**Beta:** Evaluation module and tests.  
**Gamma:** UI/replay and demo presentation.

## P0 definition of done

- Actual dataset files parse; channel IDs, units, timestamps, and event timing are inspected, not guessed.
- One selected channel set produces deterministic chronological CUSUM outputs.
- At least one baseline comparator runs on the same observations.
- Parameters and matching rules are selected using 2018 only, then frozen before 2019.
- Full 2019 prediction log is generated without label access; evaluation happens afterward.
- Dashboard displays actual computed results and a permanent benchmark-replay disclosure.
- No blocker remains hidden; misses and limitations are shown.

## Timeline (strict)

### 00:00–00:10 — Workspace and walking skeleton
**Alpha:** open repo, read context/architecture/contracts, verify data availability, create known-good checkpoint.  
**Beta:** inspect evaluator contract and prepare only the event-label parsing/matching plan.  
**Gamma:** prepare a bare Streamlit layout using placeholder *layout only*, never fake metrics.  
**Exit:** files and responsibilities clear; no dependency or architecture additions.

### 00:10–00:30 — First-hour gate, compressed
**Alpha owns the gate:** print actual filenames/shapes/headers/units/timestamp ranges, parse event metadata, check leak-active overlap and remaining clean 2018 data, plot a few event windows and estimate per-channel detectability.  
**Beta:** implement `evaluate.py` metadata parsing and `build_training_mask` against the contract if schema is verified; otherwise return an explicit parser blocker.  
**Gamma:** keep UI wired against the interface contract; no sensor IDs hardcoded.  
**Gate:** decide flow-first vs small pressure candidate set using 2018 only. If there is no evidence, narrow the claim and do not fake a detector result.

### 00:30–01:10 — Core vertical slice
**Alpha:** implement `data.py`, `baseline.py`, `detector.py`; robust scale fallback; pure `step`; idempotent state; synthetic known-sequence tests.  
**Beta:** complete `evaluate.py` strict/lenient event matching and basic metrics; add `tests/test_evaluate.py`.  
**Gamma:** implement replay controls and connect to `step`; process every row in order, using configurable batches per UI tick.

**Exit:** a short dataset interval flows from source row to detector output to an incident record.

### 01:10–01:40 — Evaluation integration and correctness
**Alpha:** fix core blockers, review actual channel direction and baseline profile.  
**Beta:** verify event counts, overlapping events, onset/repair semantics, and report counts plus percentages.  
**Gamma:** bound chart history; implement reset/run ID, pause/resume/end-of-data; display actual scores/alerts.

**Exit tests:** idempotency, prefix invariance or equivalent no-lookahead test, batch-versus-stream equivalence, missing data and near-zero scale handling.

### 01:40–02:05 — Frozen full evaluation
Choose the final candidate settings on 2018 validation only. Record the chosen channel set, baseline method, `k`, `h`, scale fallback, incident grouping/matching windows, and false-alarm budget in `DECISION_LOG.md`. Freeze. Run 2019 once. Evaluate only after prediction log finalization.

**Do not retune on 2019.** If results are poor, report them honestly; do not cherry-pick a single dramatic event.

### 02:05 — Feature freeze
No new features after this point. Only fix demo-breaking defects. The remaining work is stabilization and explanation.

### 02:05–02:30 — Visual polish and demo script
Show:
1. Benchmark Replay banner.
2. Observed vs expected.
3. Residual + CUSUM trace + threshold.
4. Incident evidence cards.
5. Static threshold vs baseline-only vs CUSUM comparison.
6. Recall counts/by-size where metadata supports it, unmatched alerts and delay where onset is valid.
7. Misses/limitations.

### 02:30–02:40 — Human run-through
Restart cold. Run the demo. Verify no fake numbers, no stale state, no crash at end-of-file, and no hidden console traceback.

### 02:40–02:50 — Buffer and checkpoint
Known-good checkpoint, current context update, only blockers. Do not introduce a new feature.

## Stop rules

- If one command/test path fails twice, stop blind retries; report exact error, attempts and evidence.
- If data/config parsing is blocked, do not build fake metrics. Deliver the smallest honest telemetry/replay demo and disclose that full event evaluation is blocked.
- If flow detectability is weak, test pressure candidates only within the predeclared 2018 gate; otherwise narrow scope.
- If integration timing slips, cut P1 visual features before cutting prediction integrity or data-source honesty.
