# AquaSentinel — Project Instructions (No Gemini)

## 0. Current-work rule: continue, do not restart

**This project may already be in the middle of implementation. Preserve its current state.** These instructions do not authorize a restart, rewrite, cleanup, or architecture change.

Before doing anything:
1. Inspect the current repository, branch, `git status`, uncommitted diff, untracked files, README, tests, and existing instructions.
2. Inspect the current milestone, recent task notes, and any partially completed implementation.
3. Report what is already done, what is in progress, what is blocked, and the smallest next step.
4. Preserve all existing user work. Never use destructive commands such as `git reset --hard`, `git clean -fd`, force-push, or broad file deletion. Never overwrite an uncommitted change just to make the repository look clean.
5. Do not recreate files or features that already exist. Extend the current implementation with the smallest safe change.
6. If this file conflicts with a more specific, already-approved architecture decision, stop and report the conflict instead of silently replacing that decision.

## 1. Tool workflow — Gemini is not part of this project

**Do not use Gemini, wait for Gemini, request Gemini reviews, or make progress dependent on Gemini.** Gemini is removed from the project workflow because it is unavailable.

Use these roles:

- **ChatGPT — Orchestrator:** clarify the objective, split work into small milestones, approve interfaces and scope decisions, review Antigravity reports, and adjudicate Kimi findings.
- **Antigravity — Primary executor:** inspect and edit the actual repository, run commands and tests, implement approved changes, and report concrete evidence.
- **Kimi — Optional independent reviewer:** review specific diffs, design decisions, logs, and test output for bugs and edge cases. Use it for high-risk changes or when time allows; never block ordinary implementation waiting for a review.
- **Human project owner:** decides scope changes and resolves any important trade-offs. The project owner may manually validate the demo.

No agent should pretend to have run commands, inspected files, or verified test results when it has not.

## 2. Mission

Build **AquaSentinel**, an explainable water-network monitoring MVP that learns normal historical flow patterns, detects persistent suspicious changes, displays evidence-backed suspected-anomaly alerts, and evaluates its results honestly.

The MVP uses the public simulated BattLeDIM benchmark replay. It is not a live municipal monitoring system.

## 3. Locked architecture

Keep the current approved architecture unless the project owner explicitly approves a change:

- Python modular monolith in one process.
- Streamlit UI and replay controls.
- pandas for data loading/validation; NumPy/Python for numerical calculations.
- Historical time-of-day/day-of-week baseline, with robust median and MAD-derived scale as the primary candidate and a simple mean/standard-deviation comparison during validation.
- Channel-aware one-sided CUSUM, with channel direction chosen from verified metadata and historical validation evidence.
- Separate evaluation module with predeclared event-matching rules.
- Plotly or an already-used reliable chart library.
- Local benchmark files and in-memory state; no database is needed for the MVP.

Do not add FastAPI, separate frontend/backend services, databases, Redis, Kafka, an LLM in the detection path, graph neural networks, a hydraulic digital twin, live SCADA integration, automated dispatch, valve/pump control, or exact pipe localization unless the project owner explicitly approves a scope change.

## 4. Module responsibilities

Follow existing module names if implementation has already established them. Otherwise, the target logical responsibilities are:

- `data.py`: load telemetry and validate actual schema, timestamps, intervals, units, missing values, and chronological ordering.
- `baseline.py`: fit/query expected historical profiles and a deterministic robust scale.
- `detector.py`: pure, testable CUSUM step and minimal per-channel incident state.
- `evaluate.py`: parse event metadata, create the permitted 2018 training mask, and calculate post-run evaluation metrics.
- `app.py`: Streamlit UI, replay orchestration, session state, charts, and calls to the other modules.
- `tests/`: unit and integration tests.

These are logical modules in one app, not separately deployed services. Do not rename or reorganize existing working code merely to match this list. Inspect first and propose only the smallest compatible change.

## 5. Alpha, Beta, Gamma ownership

These are workstreams in one shared product, not separate apps.

- **Alpha — Data and detection:** data validation, baseline, CUSUM, incident-state foundations, and unit tests.
- **Beta — Dashboard and replay:** Streamlit console, sequential replay controls, charts, alert cards, and user experience. Use Alpha's agreed interfaces; do not duplicate detector logic.
- **Gamma — Evaluation and quality:** label boundary, event-matching tests, evaluation integrity, integration checks, reproducibility, and demo readiness. Gamma must not change Alpha/Beta-owned modules without coordinating first.

Before editing, state which workstream owns each file touched. Avoid multiple agents editing the same files concurrently. If concurrent work is unavoidable, use separate branches/worktrees and integrate reviewed diffs; do not overwrite someone else's local changes.

## 6. Data and evaluation integrity

- Inspect actual dataset files before asserting their column names, sensor IDs, timestamp semantics, units, directions, or event-label meanings.
- Do not hardcode sensor IDs based on unverified reports.
- Use 2018 data for fitting and chronological validation.
- Select and freeze baseline method, channel set, CUSUM parameters, incident rules, and evaluation-matching rules before the final 2019 replay.
- The detector/replay path must not read event labels or future observations.
- `evaluate.py` is the only label-aware module.
- Load 2019 event labels only after the complete prediction log is finalized. The 2019 labels must not tune or alter predictions.
- The 2019 benchmark labels are public, so describe the evaluation as a procedurally held-out chronological evaluation, not a secret or blind test.
- Compare simple thresholds, baseline-only residual detection, and CUSUM fairly on the same held-out replay and a predeclared comparable false-alarm budget when feasible.
- Do not claim benchmark performance until evaluation code has actually produced it.

## 7. Detection and alert wording

- CUSUM detects persistent statistical changes; it cannot prove a physical leak.
- Use **“suspected anomaly”** or **“suspected leak event”**, never “confirmed leak” without independent confirmation.
- Verify flow channel direction before choosing upper- or lower-sided detection.
- Handle missing values and near-zero/invalid scale conservatively. Never divide by zero or invent physical variance.
- Do not automatically re-baseline during a suspected incident.
- Do not infer exact pipe/zone location from aggregate channel readings unless the mapping is documented and verified.
- Do not claim actual water saved, financial savings, or field accuracy from a simulated benchmark. A simulated leak-volume-before-alert measure is allowed only if validly calculated and clearly labelled.

## 8. Replay and dashboard correctness

- Display a persistent notice: **“Benchmark Replay — simulated data, not live municipal telemetry.”**
- Process observations chronologically and exactly once.
- Maintain a run ID, replay index, last-processed index, per-channel detector state, full prediction log, and bounded chart-history buffer as appropriate to the current implementation.
- Duplicate row/index processing must not mutate detector state twice.
- Reset must create fresh state and invalidate stale replay ticks.
- Pause, resume, reset, and end-of-data must behave predictably.
- Keep the complete prediction log separately from the rolling chart window.
- The UI must not display hardcoded metrics or alerts as if they were detector outputs. Clearly label mocks and synthetic test fixtures.

## 9. Implementation rules for a time-limited hackathon

1. Prefer a working end-to-end path over extra features.
2. Make one focused change or milestone at a time.
3. Reuse installed dependencies and existing project conventions.
4. Do not add a dependency unless the benefit is clear and necessary.
5. Avoid broad refactors, speculative abstractions, and cosmetic work that blocks correctness.
6. State assumptions and blockers instead of guessing.
7. Keep code simple, readable, modular, and testable.
8. Check `git diff` before any commit.
9. Do not commit secrets, tokens, private data, local virtual environments, or `.env` files.
10. Never report tests as passed unless they were actually run and passed. If a command cannot run, state why.
11. Preserve all unrelated user changes.
12. Do not wait for Gemini or introduce Gemini tasks, prompts, outputs, or dependencies.

## 10. Review routing without Gemini

Use review effort proportionally:

- **Low risk** (copy, small layout changes, isolated refactors): Antigravity implements and runs relevant checks; ChatGPT reviews the report if needed.
- **Medium risk** (data parsing, replay state, module integration): Antigravity implements and tests; ChatGPT checks the diff/report; use Kimi if an edge-case review adds value.
- **High risk** (evaluation split, label access, CUSUM logic, event matching, changes crossing Alpha/Beta/Gamma boundaries): require focused tests plus ChatGPT review; use Kimi for a targeted independent challenge when available. Do not block if Kimi is unavailable; document the missing independent review and rely on tests/manual verification.

Kimi should receive the relevant diff, exact test output, and a focused question—not the entire project history unless needed. ChatGPT should adjudicate specific findings against the actual code and constraints, not accept review comments blindly.

## 11. Required handoff report after each milestone

Every implementation or review handoff must include:

1. **Milestone:** what was attempted and why.
2. **Current state:** what existed before the change.
3. **Files changed:** exact paths and purpose.
4. **Interfaces/contracts:** anything another workstream must use or know.
5. **Verification:** exact commands run and actual pass/fail output or summary.
6. **Known limitations/blockers:** separate confirmed facts from assumptions.
7. **Git state:** branch and whether changes are committed; never imply a commit happened if it did not.
8. **Next smallest step:** one concrete recommendation.

Do not produce long tutorial reports during ordinary implementation. Keep the handoff concise, factual, and actionable.

## 12. Definition of done

A task is complete only when:

- It fits the locked architecture and existing work.
- Its changed paths and purpose are clear.
- Relevant tests were run, or unrun tests and reasons are explicitly stated.
- No label leakage, fabricated metrics, or unsupported claims were introduced.
- The change is integration-ready and does not overwrite other work.
- The handoff report documents evidence, limitations, and the next step.

## 13. Resume prompt for the current in-progress session

Use this prompt whenever a tool is resumed in the middle of work:

> Continue AquaSentinel from its current state; do not restart or rebuild from scratch. Read `PROJECT_INSTRUCTIONS.md`, inspect the repository and Git status, review uncommitted changes and recent task notes, and identify the active milestone. Preserve existing work and report what is complete, in progress, and blocked. Do not use Gemini or wait for Gemini. Work only on the assigned task, make the smallest safe change, run relevant checks, and return the required handoff report. Do not overwrite, delete, reset, or refactor unrelated work.

## Final principle

**Preserve progress. Verify before assuming. Ship the smallest credible system. Measure honestly. Never block on Gemini.**
