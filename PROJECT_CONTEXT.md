# AquaSentinel — Canonical Project Context

**Last updated:** 2026-10-09  
**Status:** Architecture approved with first-hour data/detectability gate  
**Time left:** Less than three hours  
**Owner:** Human / Alpha

## Problem

Municipal water-utility operators can struggle to identify suspected leaks early because normal demand changes, sensor faults, and leak signals can produce similar pressure/flow patterns. The MVP aims to identify persistent statistical anomalies and show the evidence needed to decide whether further investigation is warranted.

## Solution

AquaSentinel is an explainable water-network monitoring prototype. It replays BattLeDIM's simulated readings sequentially, compares candidate sensor readings with a robust historical baseline, applies channel-aware one-sided CUSUM, groups repeated alerts, and evaluates predictions against verified event metadata.

## Truth constraints

- BattLeDIM is a simulated benchmark, not live municipal telemetry.
- Replay is real-time-style processing, not a live SCADA connection.
- An anomaly is not proof of a leak.
- No exact pipe/zone localization without verified mapping.
- Do not claim actual litres saved, cost savings, carbon savings, or field accuracy.
- `2018_Fixed_Leakages_Report.txt` describes repair times, not leak onset.
- Do not hardcode sensor IDs before reading actual CSV headers and checking the mapping/configuration.
- The README documents three flow channels, 33 pressure sensors, one tank-level measurement, and 82 AMR demand meters; actual files must be inspected.

## Locked architecture

Single-process modular Streamlit monolith with:
- `data.py` — ingest/validate telemetry and timestamps.
- `baseline.py` — robust historical baseline and scale lookup.
- `detector.py` — channel-aware CUSUM step and incident state.
- `evaluate.py` — training exclusion mask, event parsing, post-run metrics.
- `app.py` — replay, UI, per-session state and bounded dashboard history.

No API/backend, database, Redis/Kafka, SSE/asyncio, LLM, HGNN, hydraulic digital twin, live SCADA, control action, or autonomous dispatch in the MVP.

## Conditional technical choice

Start by checking flow-channel detectability using 2018 only. If the data does not show enough measurable signal, test a small, fixed candidate pressure-channel subset using the same channel-agnostic detector and choose using 2018 validation only. Do not select channels or tune thresholds using 2019 labels.

## Success definition

A credible demo must:
1. Load and validate the real files and their actual schema.
2. Process selected telemetry in strict chronological order.
3. Produce deterministic, idempotent predictions.
4. Compare static-threshold, baseline-only, and CUSUM methods on a frozen 2019 replay.
5. Report actual event-level counts, false/unmatched alerts, and delay only where onset is verified.
6. Show a working dashboard with a permanent `Benchmark Replay — simulated data, not live municipal telemetry` label.
7. Explain missed events and limitations, not only a successful example.

## Current unknowns / risks

- Exact channel IDs and signs need file inspection.
- The configuration-file schema and event onset/end meanings need parsing and cross-checking.
- The fraction of 2018 samples masked by known leak-active intervals is unknown.
- Flow-first detectability and 2018-to-2019 residual drift are unknown.
- Event matching can be ambiguous during overlapping simulated leaks.
- CUSUM performance has not yet been measured; no model win is assumed.

## Authority and memory

Human owns scope, architecture approvals, and final sign-off. `DECISION_LOG.md` is the decision record. `INTERFACE_CONTRACTS.md` controls the module handoff. Antigravity reports code/test evidence; it does not self-approve milestones. ChatGPT is the main orchestrator and adjudicator. Gemini reviews risky changes. Kimi performs independent milestone red-team review.
