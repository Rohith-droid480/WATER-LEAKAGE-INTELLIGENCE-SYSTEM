# ALPHA — Human Core Engineer and Final Integrator

**Owner:** Human / user  
**Priority:** Highest — detection and truth must work before polish.

## Mission
Own the most critical vertical slice: real dataset understanding, validated telemetry, baseline, channel-aware CUSUM, and final integration. You are the project's final technical authority and must understand how each alert is produced.

## Files Alpha owns
- `data.py`
- `baseline.py`
- `detector.py`
- approval of material context changes and `DECISION_LOG.md` decisions
- final integration/merge decisions

ChatGPT is the canonical `PROJECT_CONTEXT.md` editor after milestone adjudication; Alpha/Human approves material changes.

Do not allow Beta or Gamma to edit these files without an explicit handoff.

## Required work
1. Inspect real dataset filenames, headers, units, timestamp format and event metadata.
2. Establish channel IDs/direction from evidence; never copy guessed sensor names.
3. Execute the first-hour gate and decide flow-first vs pressure candidate using 2018 only.
4. Implement baseline fitting, pooled robust scale fallback and no-online-rebaseline rule.
5. Implement pure CUSUM `step()` with index/run idempotency.
6. Prove no future leakage and deterministic replay via tests.
7. Integrate Beta's evaluator and Gamma's UI through `INTERFACE_CONTRACTS.md`.
8. Freeze parameters and channel choices before final 2019 scoring.
9. Ensure misses, unmatched alerts, and limitations remain visible.

## Do not
- Tune based on 2019 labels.
- Claim physical cause from statistical anomaly.
- add HGNN, WNTR, API, database, or LLM.
- approve a merge solely because another model says PASS.
- sacrifice data validity for visual polish.

## Acceptance
Alpha must be able to explain baseline, residual, CUSUM state, threshold, incident grouping, event-matching rules and the distinction between benchmark performance and field validation.

## Handoff format
Send Beta/Gamma: contract version, existing exports, verified schema facts, allowed files, acceptance criteria, and data known/unknown. Ask them to stop if the contract does not match implementation.
