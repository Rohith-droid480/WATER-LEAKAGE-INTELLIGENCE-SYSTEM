# AquaSentinel — Architecture and Scope Decision Log

**Owner:** Human / Alpha  
**Rule:** Approved decisions cannot be silently changed by Antigravity, Beta, Gamma, ChatGPT, Gemini or Kimi. AI tools may propose entries; Human/Alpha approves material changes.

## Decision protocol

Every material decision must record: ID, status (`PROPOSED`, `APPROVED`, `REJECTED`, `DEFERRED`), date, owner, context, options, rationale/evidence, risks, validation required, and reversal condition.

Authority order:
1. Official hackathon requirements.
2. Human-approved project goal and scope.
3. This decision log and approved architecture.
4. `INTERFACE_CONTRACTS.md`.
5. Actual code/runtime/test evidence.
6. Context pack and build plan.
7. Research and AI opinions.
8. Conversation memory.

Evidence beats agreement between models. When a question can be tested quickly, test it.

## ADR-001 — Modular Streamlit monolith
**Status:** APPROVED  
**Date:** 2026-10-09  
**Decision:** Single-process Streamlit app; internal modules remain independently testable.  
**Reason:** Fits less-than-three-hour constraint and avoids unnecessary service boundaries.  
**Rejected for MVP:** API backend, database, message queue, Redis/SSE, LLM, HGNN, hydraulic digital twin.  
**Reopen only if:** A verified core requirement cannot be met by local replay and simple in-process state.

## ADR-002 — Statistical detector candidate
**Status:** APPROVED WITH VALIDATION GATE  
**Decision:** Robust time-context baseline + channel-aware one-sided CUSUM as primary candidate; static threshold and baseline-only residual threshold as comparators.  
**Not assumed:** CUSUM will outperform comparators; channel detectability is not yet proven.  
**Reopen if:** 2018 validation shows weak signal or unacceptable false alarms; test a small pressure-first candidate set using 2018 only.

## ADR-003 — Label and prediction isolation
**Status:** APPROVED  
**Decision:** `evaluate.py` is the only label-aware module. It may produce a plain 2018 training inclusion mask for baseline fitting. 2019 event labels are loaded only after the 2019 prediction log is finalized.  
**Reason:** Prevent training/test leakage and keep detection logic independent of event truth.

## ADR-004 — Dataset schema
**Status:** APPROVED  
**Decision:** Inspect actual headers and metadata. No hardcoded sensor IDs based on old reports.  
**Known doc-level facts:** README documents 3 flow channels, 33 pressure sensors, 1 tank-level measurement, and 82 AMR meters.  
**Unknown until file inspection:** exact IDs, signs, timestamp semantics, event configuration schema, active-at-start cases and detectability.

## ADR-005 — Evaluation integrity
**Status:** APPROVED  
**Decision:** Split chronologically within 2018 for fit/validation; select all model/channel/threshold/matching choices on 2018; refit baseline with the chosen procedure over all eligible leak-masked 2018 data; freeze; replay 2019; evaluate afterward.  
**Not a blind test:** 2019 labels are public.  
**No test tuning:** Changing parameters after viewing 2019 metrics invalidates the reported held-out evaluation.

## ADR-006 — Real-time wording and impact claims
**Status:** APPROVED  
**Decision:** Call demo “accelerated sequential replay of simulated benchmark telemetry.” Never call it live SCADA. Use “suspected anomaly”, not “confirmed leak.” Never call simulated leak volume “water saved.”

## ADR-007 — Roles and file ownership
**Status:** APPROVED  
- Alpha/Human: source-of-truth decisions, `data.py`, `baseline.py`, `detector.py`, integration and scope.
- Beta: `evaluate.py` and evaluation tests.
- Gamma: `app.py` and replay/UI tests.
No overlapping file ownership without an explicit handoff.

## ADR-008 — Three-hour feature discipline
**Status:** APPROVED  
**P0:** load/validate → detector → sequential replay → evaluator metrics → reliable demo.  
**P1:** pressure candidate comparison, polished incident cards, recall-by-size view.  
**P2/deferred:** map, volume-before-alert, live adapter, localization, advanced models.  
Feature freeze occurs at the time listed in `BUILD_PLAN.md`.

## Change request template

```md
### ADR-XXX — <short decision title>
- Status: PROPOSED
- Owner:
- Context / problem:
- Evidence:
- Options:
- Recommendation:
- Risk:
- Validation:
- Reversal condition:
- Human approval:
```
