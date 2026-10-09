# AquaSentinel Project Playbook
## Project-specific use of the locked Hackathon AI Orchestration Workflow V4.1

The supplied V4.1 `SKILL.md` is the generic standard workflow and must remain unchanged. This file adapts that workflow to AquaSentinel; it does not replace or redefine it.

## Lifecycle
PLAN → BUILD → EXECUTE → EVIDENCE → RISK-BASED REVIEW → LEARN → DECIDE → CHECKPOINT → NEXT

## Authority
Human/Alpha owns project scope, architecture approvals, final evaluation-protocol choices, checkpoints, and final demo acceptance. ChatGPT orchestrates tasks and adjudicates reviews. Antigravity implements, runs, tests and reports. Gemini provides evidence-focused review for T2/T3. Kimi independently red-teams milestones and significant disagreements.

A model agreement is not verification. Executed tests and inspected data outrank narratives.

## Before every implementation task
Antigravity reads:
1. Task card.
2. `PROJECT_CONTEXT.md`.
3. `BUILD_PLAN.md` and current state.
4. `ARCHITECTURE.md` and `INTERFACE_CONTRACTS.md` for relevant code.
5. `DECISION_LOG.md`.
6. Active `.agents/rules/*.md`.
7. V4.1 `SKILL.md` for workflow semantics.

If a task conflicts with approved architecture or a role's file ownership, STOP and report the conflict.

## Risk routing
- T0: copy/minor visual tweak → Antigravity → smoke check → Human quick check.
- T1: isolated feature → Antigravity → targeted test → Human quick check; checkpoint after successful work.
- T2: core detector, data schema, label handling, state, evaluation, dependency or cross-module change → Antigravity evidence → Gemini review when risk warrants → ChatGPT adjudication.
- T3: complete vertical slice, freeze, final demo → physical test → Human test → Kimi independent red team → ChatGPT adjudication → Human sign-off.
- Consult: use after two failed fix cycles, unexplained behavior, or material reviewer disagreement.

## Work report format
Every task response must contain:
- COMPLETED
- FILES
- TESTS (exact commands + result)
- RESULT
- NOT VERIFIED
- STATE DELTA
- LEARNING NOTE (what changed, why, main flow, one risk, likely judge question)

At milestone:
- WHAT WAS BUILT
- ACCEPTANCE → EVIDENCE MAP
- RAW EVIDENCE
- NOT VERIFIED
- KNOWN LIMITATIONS
- FILES ACTUALLY TOUCHED
- RISK RE-CHECK
- GEMINI/KIMI REVIEW PACKET

## Evidence statuses
- VERIFIED: actual deterministic test/runtime/data artifact proves it.
- PLAUSIBLE: supported by code or reasoning but lacks executed proof.
- REJECTED: evidence disproves it.
Impact is separately classified BLOCKER / SHOULD-FIX / DEFER.

## Two-failure rule
One fix cycle is attempt + verification. If the same approach fails twice, do not try a third blind edit. Reproduce, capture error, ask for a targeted diagnosis, then resume only after a decision.

## Review packets
External reviewers receive only the relevant context, changed files/diff, acceptance criteria, test commands/output, known risks and NOT VERIFIED items. Do not send secrets, `.env`, tokens, or unnecessary logs. Keep Gemini and Kimi first-pass reviews independent.

## Context ownership
Antigravity reports STATE DELTA. ChatGPT consolidates `PROJECT_CONTEXT.md` after milestone adjudication. Human approves material strategic changes. Update `DECISION_LOG.md` for architecture/channel/evaluation changes. Do not let multiple AI agents concurrently rewrite context/decision files.

## Feature freeze
Follow `BUILD_PLAN.md`. After 02:05 in the three-hour plan, new features are prohibited. Fix only demo-breaking defects or correctness issues.
