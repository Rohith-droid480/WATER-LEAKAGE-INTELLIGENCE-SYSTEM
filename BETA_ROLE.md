# BETA — Evaluation and Ground-Truth Engineer

**Owner:** delegated builder/subagent/teammate  
**Priority:** Important but non-authoritative; supports Alpha's core detector.

## Mission
Build a truthful, deterministic evaluation path without changing the baseline, detector, data loader, app, or architecture.

## Exclusive file ownership
- `evaluate.py`
- `tests/test_evaluate.py`
- Optionally a small evaluator-focused fixture under `tests/` if needed.

Do not edit `data.py`, `baseline.py`, `detector.py`, `app.py`, `ARCHITECTURE.md`, `INTERFACE_CONTRACTS.md`, or `DECISION_LOG.md`. Propose any contract issue to Alpha instead.

## Contract
Implement the agreed roles:
- Parse event metadata from the actual downloaded configuration/leakage files.
- Build the 2018 training exclusion mask as a plain Boolean array.
- Keep 2019 labels inaccessible until prediction log finalization.
- Score predictions after run completion using predeclared event matching.
- Report strict/lenient matching if overlap creates attribution ambiguity.
- Report counts alongside percentages and do not fabricate missing fields.

The fixed-leakage report gives repair times and must not be used as event-onset truth. Verify actual event metadata fields from the files; if unknown, report the blocker.

## Required evaluation outputs
- event count eligible / detected / missed;
- precision/recall counts and values;
- unmatched alerts and false/unmatched alerts per simulated month;
- detection delay only for verified onset;
- recall by leak size/diameter only if metadata supports it;
- overlap ambiguity and not-evaluable cases.

## Do not
- Tune `k`, `h`, channel choice or thresholds.
- Read held-out labels during replay.
- Change prediction records to improve scores.
- claim that an unmatched alert is certainly physically false when labels may be incomplete.
- call simulated loss “water saved.”
- silently guess YAML field names.

## Acceptance
Tests cover metadata parsing, onset/repair distinction, mask alignment, strict/lenient overlapping events, no-label-before-prediction protocol, and output counts. Every displayed number must come from actual predictions and verified labels.

## Required report
COMPLETED / FILES / TESTS / RESULT / NOT VERIFIED / STATE DELTA. Include exact schema facts observed and fields that remained unknown.
