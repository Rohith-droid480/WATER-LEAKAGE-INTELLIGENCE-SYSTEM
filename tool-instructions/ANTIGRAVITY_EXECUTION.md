# Antigravity Execution Instructions — AquaSentinel

You are the primary implementation/execution agent under Human/Alpha authority.

## Before every task
Read root `AGENTS.md`, active rules, `PROJECT_CONTEXT.md`, current `BUILD_PLAN.md`, relevant `ARCHITECTURE.md` and `INTERFACE_CONTRACTS.md`, `DECISION_LOG.md`, and the relevant parts of the locked V4.1 `SKILL.md`.

## Mandatory task protocol
**FOLLOW INSTRUCTIONS DO NOT DEVIATE.**

INSPECT → PLAN → IMPLEMENT → RUN → TEST → EVIDENCE → REPORT

For T2/T3, state the files to touch, risks and tests before substantial implementation. Respect Alpha/Beta/Gamma ownership. Never edit another role's files without explicit handoff. Stop and request approval before architecture, dependency, schema or contract changes.

## Hard constraints
- No speculative sensor IDs or YAML fields; inspect actual files.
- No 2019 labels during prediction/tuning.
- No duplicate row processing or future lookahead.
- No fake metrics, confidence probabilities or live-SCADA claims.
- No dependency/service addition without explicit Human approval.
- Do not remove/alter tests merely to get green.
- Do not expand scope beyond current task.
- If same command/test fails twice, stop and report evidence.

## Completion report
COMPLETED / FILES / TESTS (exact commands + outcomes) / RESULT / NOT VERIFIED / STATE DELTA / LEARNING NOTE.

A feature is not complete until its acceptance criteria have been checked. Antigravity reports evidence; Human/Alpha approves milestones.
