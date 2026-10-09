---
name: hackathon-ai-orchestration
description: Orchestrates a human-in-the-loop hackathon engineering workflow using ChatGPT, Antigravity, Gemini, Kimi/DeepSeek, evidence-based validation, risk-based routing, milestone reviews, learning, and demo preparation.
---

# HACKATHON AI ORCHESTRATION WORKFLOW — V4.1 (LOCKED)

## Purpose

This is the canonical human-in-the-loop workflow for:
HUMAN + CHATGPT + ANTIGRAVITY + GEMINI + KIMI/DEEPSEEK.

It defines the standard workflow only. It does not replace the later project-specific AI Operating System (`AGENTS.md`, `.agents/rules/`, skills, architecture rules, etc.). The workflow remains standard across projects; project-specific execution belongs in `BUILD_PLAN.md`, the Context Pack, architecture/contracts, and active rules.

Core lifecycle:

PLAN → BUILD → EXECUTE → EVIDENCE → RISK-BASED REVIEW → LEARN → DECIDE → CHECKPOINT → NEXT

The goal is to maximize:
project quality + probability of finishing + demo reliability + Human understanding

while minimizing:
unnecessary AI calls + copy/paste overhead + context drift + endless debugging + late surprises.

## V4.1 LOCK STATUS

V4.1 is the locked standard workflow. Do not customize the workflow document per project.
Project-specific adaptation happens through `BUILD_PLAN.md`, Context Pack, architecture/contracts, and active project rules.

### V4.1 final patches
- deterministic Gemini → ChatGPT routing
- light Walking Skeleton milestone to protect validator budget
- explicit security escalation path
- explicit definition of VERIFIED
- single two-failed-cycles stop rule
- Phase 0 time/data/AI-use guardrails
- mandatory successful T1 checkpoints
- optional T0/T1 task batching
- copy-paste-ready external-AI handoff packets
- explicit Context Pack ownership/update rule
- project-specific `BUILD_PLAN.md` separation


---

# 0. ANTIGRAVITY EXECUTION RULE

Before every implementation task:

1. Read the relevant project state.
2. Read the task.
3. Read the applicable active project rules.
4. **STRICTLY FOLLOW THE ACTIVE INSTRUCTIONS IN `AGENTS.md`, `.agents/rules/`, and other applicable project rule files.**
5. If a task conflicts with an active rule, STOP and report the conflict. Never silently bypass a rule.

Important:
Not every file that happens to exist inside `.agents/rules/` is necessarily active. Only rules actually loaded/activated by the current Antigravity setup apply.

Rules/invariants belong in the project rule layer.
Multi-step operating procedures belong in the workflow/skill layer.

---

# 1. ROLE ARCHITECTURE

## HUMAN — Product Owner / Final Authority

Owns:
- problem and solution choice
- scope
- final architecture approval
- risk acceptance
- Git/checkpoint approval
- manual testing
- milestone PASS
- secrets/destructive actions
- final demo and submission
- final technical understanding

The Human does not need to write every line of code.
The Human must understand enough to defend the project.

## CHATGPT — Main Orchestrator + Adjudicator

Owns:
- converting the overall goal into the next task
- acceptance criteria
- risk classification
- Antigravity prompts
- review routing
- review triage
- architecture decisions
- milestone transitions
- judge preparation
- maintaining workflow state

ChatGPT does NOT decide correctness from model opinions alone.
Its decisions must be grounded in evidence.

## ANTIGRAVITY — Builder + Execution Engine + Technical Explainer

Owns:
- repository inspection
- planning
- implementation
- runtime execution
- testing
- debugging
- evidence collection
- compact task explanations
- deep milestone teach-backs
- review handoff preparation

Antigravity reports; it does not self-approve milestones.

## GEMINI — Risk-Based Development Reviewer

Checks:
- requirements
- acceptance criteria
- API/integration assumptions
- data/schema behavior
- cross-module effects
- AI model/prompt changes
- regressions
- missing tests
- technical risks

Gemini is NOT required for every task.

## KIMI / DEEPSEEK — Independent Red Team

Reserved for:
- milestones
- security-sensitive/high-risk work
- major integrations
- material disagreements
- repeated failed fixes
- pre-demo and final review

They must attack the evidence independently.

## AUTOMATION — Ground Truth

Use:
compiler, lint, type checking, tests, browser/E2E, API checks, secret/dependency scans, build/deployment checks.

---

# 2. EVIDENCE PRINCIPLE

Never use:
“Three AIs agreed, therefore it is correct.”

Use:
“The system was executed, evidence was collected, and independent review found no unresolved critical issue.”

When a disagreement can be experimentally resolved:
TEST > ARGUMENT.

---

# 3. PHASE 0 — PRE-BUILD HACKATHON INTELLIGENCE

Before serious coding, establish:

- official hackathon rubric
- submission rules
- sponsor requirements
- time limit/deadline
- target user
- real problem evidence
- solution
- differentiation
- MVP
- Minimum Viable Wow
- P0/P1/P2/P3/P4 feature priority
- concrete feature-freeze time
- intended deployment/demo environment
- likely external dependencies

Research should cover:
- problem severity
- existing solutions
- gaps
- APIs/data
- technical feasibility
- current documentation
- rate limits
- deployment constraints
- demo viability
- major failure modes

## Riskiest-unknown spike

Before locking architecture, prove the riskiest assumption with a small experiment:
API call, model behavior, dataset access, hardware, deployment, database, browser capability, etc.

Do not spend hours architecting around an assumption that a small spike can disprove.

## Phase 0 time cap

Default Phase 0 budget: **no more than 10% of the total event time** unless the event explicitly provides more preparation time.
Stop research when the project has enough evidence to choose the problem, MVP, architecture direction, riskiest unknown, and demo path.
Do not turn research into an open-ended task.

## AI-use, disclosure, and data handling

Before implementation, explicitly check hackathon rules for:
- allowed AI assistance
- required AI disclosure
- pre-existing code/assets restrictions
- external services and sponsor/API restrictions

Never paste into ChatGPT, Gemini, Kimi, DeepSeek, or other external AI tools:
- `.env` files
- API keys
- passwords/tokens
- private credentials
- sensitive personal data
- unredacted secret-bearing logs

Redact secrets before external validation. Use placeholders where necessary.

---

# 4. PRE-HACKATHON DRY RUN

Run the workflow on a toy project before the event:

- one T1 task
- one T2 task
- one fake milestone
- one review
- one rollback

Record friction and simplify the workflow before the real hackathon.

## Validator calibration

Before the hackathon, give Kimi and DeepSeek the same small code sample containing known defects.

Measure:
- true issues found
- false positives
- severity ranking
- quality of reproduction suggestions
- speed

Choose the default validator from evidence, not reputation.

## One-page operating card

Maintain a short card with:
- T0/T1/T2/T3/Consult routing
- NEXT TOOL rules
- milestone checklist
- evidence checklist
- validator call budget
- freeze time

The long workflow is reference material.
The operating card is for live hackathon use.

---

# 5. PROJECT CONTEXT PACK

Never rely on the whole chat history as project memory.

Maintain a compact context pack containing:

## PROJECT
- problem
- target user
- solution
- Minimum Viable Wow

## HACKATHON
- official rubric
- submission requirements
- time plan
- feature-freeze time

## TECHNICAL
- stack
- architecture summary
- important decisions
- current milestone

## CURRENT STATE
- completed
- in progress
- blocked
- known risks
- accepted risks

## QUALITY
- known defects
- recent test status
- demo status

## JUDGE BANK
- likely judge questions
- grounded answers
- unresolved questions

After meaningful tasks, Antigravity reports a short STATE DELTA.
ChatGPT is the canonical Context Pack editor: it consolidates material changes and emits the updated canonical markdown block after each milestone adjudication.
The Human approves material strategic changes.
Antigravity does not silently rewrite the canonical project state.
Refresh the canonical Context Pack at each milestone.

## Project-specific BUILD_PLAN.md

After the problem statement, target user, MVP, and architecture direction are selected, ChatGPT creates a project-specific `BUILD_PLAN.md`.

`BUILD_PLAN.md` contains:
- project objective and success definition
- selected architecture and boundaries
- walking skeleton / vertical slices
- milestone order
- task backlog and dependencies
- acceptance criteria
- project-specific risks and spikes
- deployment target
- feature priorities
- planned review points
- feature-freeze plan

`BUILD_PLAN.md` adapts the standard workflow to the project. It does **not** redefine the workflow itself.

---

# 6. AUTHORITY HIERARCHY

When information conflicts:

1. official hackathon rules
2. Human-approved project goal/scope
3. approved architecture/decisions
4. active contracts/schemas
5. automated/runtime evidence
6. current project state
7. research
8. model reports
9. conversation history

Lower-level information cannot silently override higher-level information.

---

# 7. TASK CARD — CHATGPT

Every implementation task starts with:

## T0/T1
- TASK
- ACCEPTANCE CRITERIA
- SCOPE
- OUT OF SCOPE
- RISK TIER

## T2/T3
Also include:
- WHY
- FILE/AREA BOUNDARY
- VALIDATION PLAN
- HUMAN LEARNING GOAL
- EXIT CONDITION
- TIME BOX
- STOP CONDITIONS

ChatGPT must end with:

NEXT TOOL: ANTIGRAVITY
ACTION: Paste the Task Card.

## T0/T1 task batching

For independent T0/T1 work, ChatGPT may issue a batch of **3–6 Task Cards** in one handoff.
Each card must remain independently executable, scoped, and acceptance-testable.
Do not batch tasks with hidden dependencies, shared risky state, external integrations, schema/security changes, or T2/T3 characteristics.

---

# 8. RISK TIERS

## T0 — Trivial

Examples:
copy, docs, harmless rename, simple styling, obvious cleanup, safe revert.

Path:
CHATGPT → ANTIGRAVITY → TEST/SMOKE → HUMAN QUICK CHECK → NEXT

## T1 — Normal

Examples:
isolated feature, ordinary UI behavior, standard CRUD, local state, reliable test coverage.

Path:
CHATGPT → ANTIGRAVITY → TEST → HUMAN QUICK CHECK → NEXT

## T2 — Risky / Cross-cutting

Examples:
external API, database/schema, auth/authz, secrets, AI model/prompt behavior, global state, cross-module change, demo-critical feature, sensitive data, major dependency change.

Path:
CHATGPT → ANTIGRAVITY → EVIDENCE → GEMINI →
IF GEMINI = PASS WITH NO BLOCKER/SHOULD-FIX → CONTINUE
OTHERWISE → CHATGPT TRIAGE → FIX/REPRODUCE/CONTINUE

For T2 security-sensitive work (auth/authz, secrets, dangerous operations, sensitive-data handling):
- Gemini reviews the implementation immediately.
- Flag the change for the next planned Kimi/DeepSeek red-team call.
- If the security issue is urgent/material, use a Human-approved CONSULT instead of waiting.

## T3 — Planned Milestone

Examples:
complete vertical slice, major integration, core flow, feature freeze, pre-demo/final release candidate.

Path:
CHECKPOINT → PHYSICAL TEST → HUMAN TEST → KIMI/DEEPSEEK → CHATGPT ADJUDICATION → HUMAN SIGN-OFF

## M0 — Light Walking Skeleton Milestone

M0 is a special early milestone used to prove the end-to-end path without consuming a scarce Kimi/DeepSeek call.

Path:
CHECKPOINT → ANTIGRAVITY PHYSICAL TEST → DETERMINISTIC GATES → HUMAN TEST → OPTIONAL GEMINI → CONTINUE

Escalate M0 to Kimi/DeepSeek only if a material security, architecture, or unresolved integration issue justifies it.

## CONSULT — Exceptional Escalation

Use when:
- two fix cycles fail
- behavior remains unexplained
- material disagreement persists
- complex diagnosis is needed
- urgent security/architecture question appears

Path:
SYMPTOM + ATTEMPTS + EVIDENCE → KIMI/DEEPSEEK → CHATGPT/HUMAN DECISION

Consult is not automatically a full milestone.

---

# 9. RISK RE-TIERING

ChatGPT assigns the initial tier.
Antigravity checks the actual implementation.

Antigravity MAY upgrade the tier.
Antigravity MUST NOT silently downgrade it.

STOP AND ESCALATE if implementation unexpectedly:
- adds a dependency
- touches an out-of-scope area
- changes schema/contracts
- changes authentication/security
- handles secrets
- deletes/weakens tests
- changes architecture
- changes project scope

---

# 10. CHECKPOINTS

T0: commit optional.

T1: commit after **every successful T1 task**.

T2:
- known-good commit BEFORE starting
- successful commit AFTER verification

T3:
- Git tag/checkpoint BEFORE milestone validation

Final:
- `demo-ready` checkpoint

Rollback must always point to an actual known-good state.

---

# 11. ANTIGRAVITY EXECUTION LOOP

INSPECT → PLAN → IMPLEMENT → RUN → TEST → EVIDENCE → REPORT

## INSPECT
Read:
- task
- project state
- relevant architecture/contracts
- active rules

## PLAN
State:
- files
- approach
- risks
- tests

For T2/T3, Human gets a quick chance to reject a clearly bad plan before substantial work.

## IMPLEMENT
Stay inside scope.

## RUN
Actually execute the application/services.

## TEST
Run deterministic checks first.

## EVIDENCE
Collect raw evidence where useful.

## REPORT
Use the correct short or milestone packet.

---

# 12. ANTIGRAVITY SHORT REPORT

For normal T0/T1/T2 tasks:

## COMPLETED
## FILES
## TESTS
## RESULT
## NOT VERIFIED
## STATE DELTA
## LEARNING NOTE

Learning note:
1. what changed
2. why
3. main flow
4. one risk
5. one likely judge question

No long lecture in the hot loop.

---

# 13. ANTIGRAVITY MILESTONE REPORT

At T3:

## WHAT WAS BUILT
## WHY
## SYSTEM/DATA FLOW
## IMPORTANT FILES
## TECHNICAL DECISIONS
## TRADE-OFFS
## ACCEPTANCE CRITERIA
## ACCEPTANCE → EVIDENCE MAP
## RAW EVIDENCE
## NOT VERIFIED
## KNOWN LIMITATIONS
## FAILURE MODES
## FILES ACTUALLY TOUCHED
## RISK RE-CHECK
## JUDGE QUESTIONS
## GEMINI/RED-TEAM PACKAGE

---

# 14. EVIDENCE INTEGRITY

“Tests passed” is a claim, not full evidence.

For important checks preserve:
- command
- raw output
- screenshot/log location
- environment assumptions
- test/reproduction steps

Every acceptance criterion must map to a check.

If no check exists:
NOT VERIFIED.

Run deterministic gates before AI review when applicable:
- lint
- type check
- build
- tests
- secret scan
- dependency audit
- API smoke test
- E2E/browser test

---

# 15. TEST INTEGRITY

Tests written or modified by the builder require scrutiny.

If test files change:
- flag them
- inspect whether coverage was weakened

Where practical, include:
- positive case
- negative case
- edge/boundary case
- failure case

A green test suite is weak evidence if it would also pass with broken behavior.

---

# 16. API / DEPENDENCY VERIFICATION

Before relying on an external API/package:

1. confirm it exists
2. confirm current docs
3. confirm auth requirements
4. confirm current request/response shape
5. run a minimal proof-of-concept
6. record the contract
7. implement timeout/error handling

Do not rely on model memory for uncertain API behavior.

---

# 17. HUMAN MANUAL TESTING

Human testing covers what automation cannot reliably judge:

- real-user clarity
- UX feel
- visual quality
- confusing flows
- creative misuse
- realistic data
- device/screen
- network
- cold startup
- actual service behavior
- exact demo path

At milestones test:
1. happy path
2. invalid input
3. edge case
4. failure condition
5. full demo flow

Where external APIs matter, verify actual behavior rather than trusting mocks or terminal claims.

---

# 18. GEMINI REVIEW

Use Gemini for T2/T3 or explicit high-value review.

Provide:
- Context Pack
- task
- acceptance criteria
- relevant diff
- relevant surrounding code/interfaces for cross-module/security work
- test evidence
- raw evidence
- not-verified list
- known risks

Do not send giant generated boilerplate unless relevant.
Filter package-lock/noise where appropriate.

Gemini must inspect the work itself wherever practical.

## Finding taxonomy

Evidence status:
- VERIFIED
- PLAUSIBLE
- REJECTED

`VERIFIED` means a concrete verification artifact exists: a passing/failing test result, reproducible log, screenshot/video evidence, API/browser result, or documented Human reproduction.
ChatGPT must not mark a claim VERIFIED from model reasoning alone.

Impact:
- BLOCKER
- SHOULD-FIX
- DEFER

These are separate axes.

Gemini must also challenge the acceptance criteria when appropriate.

NEXT TOOL: CHATGPT only when at least one finding is BLOCKER/SHOULD-FIX, evidence is materially disputed, acceptance criteria are challenged in a way that affects the decision, or architecture/risk escalation is needed. If Gemini reports PASS with no BLOCKER/SHOULD-FIX findings, continue directly according to the task path.

---

# 19. FAST PATH SAFETY

Never do:

GEMINI → immediate code change

based only on a narrative.

Do:

finding → ANTIGRAVITY REPRODUCE → if reproduced FIX → TEST → REPORT.

If not reproduced:
- record evidence
- do not modify code
- escalate only if disagreement is material

Fast-path fixes count toward the task's fix-cycle limit.

---

# 20. CHATGPT ADJUDICATION

ChatGPT classifies each material finding:

Evidence:
- VERIFIED
- PLAUSIBLE
- REJECTED

Impact:
- BLOCKER
- SHOULD-FIX
- DEFER

Decision:
- CONTINUE
- FIX
- REPRODUCE
- RETEST
- ROLLBACK
- ARCHITECTURE REVIEW
- HUMAN DECISION

For important rejected findings, state the evidence supporting rejection.

When creating a fix/repro task, preserve the original reviewer finding verbatim.

---

# 21. FIX CYCLE CAP

One fix cycle = attempt + verification.

Default maximum:
2 meaningful fix cycles.

After two failed fix cycles:
STOP.

Choose one:
- reproduce more carefully
- consult Kimi/DeepSeek
- simplify
- rollback
- cut scope
- architecture review
- Human decision

No endless agent loops.

---

# 22. MILESTONE 0 — WALKING SKELETON

Early in the event, prove the complete technical path in miniature:

USER
→ FRONTEND
→ BACKEND
→ CORE LOGIC
→ DATA/API
→ RESULT

The walking skeleton exists to discover:
- integration blockers
- deployment blockers
- environment problems
- sponsor API problems
- missing setup

Do not postpone integration proof until late.

---

# 23. MILESTONE CALL BUDGET

Reserve scarce Kimi/DeepSeek usage at kickoff.

Recommended planned calls:
1. architecture/plan
2. core vertical slice
3. major integration/security
4. final pre-demo red team

Additional reviews are CONSULTs requiring Human approval.

Preserve at least one high-value review for the final phase.

---

# 24. FULL MILESTONE LOOP

1. Git tag/checkpoint.
2. Antigravity end-to-end physical test.
3. Deterministic gates.
4. Human manual test.
5. Quick teach-back.
6. Blind Kimi/DeepSeek red team.
7. ChatGPT adjudication.
8. Fix/retest if required.
9. Human PASS sign-off.
10. Full teach-back.
11. Update Context Pack, accepted risks, and judge Q&A.

---

# 25. BLIND RED TEAM

Kimi/DeepSeek first pass receives:
- milestone goal
- requirements
- architecture summary
- actual diff
- test evidence
- Human observations
- relevant screenshots/logs

Do NOT provide previous AI verdicts before the first pass.

Ask it to find:
- failures
- edge cases
- security issues
- assumptions
- demo risks
- architecture weaknesses
- judge challenges
- missing evidence
- reproduction steps

---

# 26. MODEL INDEPENDENCE

At kickoff, check which underlying model(s) Antigravity is using if the environment exposes that information.

Record it.

If the builder and reviewer are strongly correlated, treat model agreement as weaker evidence.

---

# 27. HUMAN LEARNING SYSTEM

## Every meaningful task
Learn:
- what
- why
- flow
- risk
- one judge question

## Every milestone
Deep teach-back:
- problem
- architecture
- data flow
- technology choices
- alternatives
- trade-offs
- security
- failure handling
- limitations
- scalability
- why the feature matters

## Teach-back test
Explain the milestone out loud without notes.

If the Human cannot explain it, the learning loop is incomplete.

---

# 28. PROBLEM → TECH → VALUE

At each milestone connect:

USER PAIN
→ PRODUCT CAPABILITY
→ TECHNICAL MECHANISM
→ USER RESULT
→ MEASURABLE VALUE

Technical sophistication without a clear connection to user pain is weak hackathon communication.

---

# 29. DEMO ENGINEERING

Identify early:
- external dependencies
- API rate limits
- network risks
- authentication dependency
- model latency
- failure points
- required demo data

Create where appropriate:
- deterministic demo input
- cached/sample data
- timeout/retry
- degraded mode
- local fallback
- approved recording backup

Never represent cached/fake data as live data.

---

# 30. FRESH-ENVIRONMENT DEMO TEST

Before final submission:

1. fresh clone or clean environment
2. only documented setup steps
3. clean startup
4. exact demo
5. realistic network
6. failure mode
7. device/screen
8. repeat several times

Do not trust a warm developer machine alone.

---

# 31. EARLY DEPLOYMENT

As soon as the walking skeleton works:
- deploy/package the actual target environment
- verify startup
- verify env variables
- verify database
- verify external services
- verify URL/domain if relevant

Continue integration against a known deployment path.

---

# 32. FEATURE PRIORITY

P0 = core value
P1 = reliability/demo survival
P2 = differentiation
P3 = UX polish
P4 = nice-to-have

Cut P4 first, then P3, while protecting P0/P1.

---

# 33. FEATURE FREEZE

Define freeze time at kickoff.

Freeze should leave enough time for:
- stabilization
- security/reliability
- deployment
- demo rehearsal
- submission

After freeze:
NO major new features.

Only:
- reliability
- security
- deployment
- UX clarity
- loading/error states
- fallback
- demo/pitch work

Any late feature must justify its value against its risk and time cost.

---

# 34. TIME BOXING

Every T2/T3 task gets a time box.

When the time box expires:
STOP → assess → simplify/cut/escalate.

Never let one difficult feature consume the project.

---

# 35. ARCHITECTURE CHANGE

Architecture is protected by default.

A change requires:
1. blocker/evidence
2. alternatives
3. impact
4. Human decision
5. recorded decision
6. affected tests/slices revalidated

Never silently replace foundational technologies to solve a local bug.

---

# 36. AFTER-FIX VERIFICATION

After every fix:
1. rerun failing check
2. run regression tests
3. run relevant E2E path
4. re-check acceptance criteria
5. inspect diff

If the fix becomes T2-sized:
re-enter T2 review.

If milestone architecture changes:
re-enter T3.

---

# 37. FINAL HOURS

As the freeze approaches:
- no major new features
- no architecture experiments
- no speculative refactors

Focus on:
- P0
- P1
- security
- deployment
- fallback
- tests
- demo
- judge Q&A

Create a known-good `demo-ready` checkpoint.

---

# 38. FINAL RED TEAM

Independently attack:

## PRODUCT
problem, differentiation, value

## FUNCTIONALITY
happy path, invalid input, failures

## SECURITY
secrets, auth, input validation, dangerous operations, external tools

## RELIABILITY
cold start, network, timeouts, rate limits

## ARCHITECTURE
drift, coupling, unnecessary complexity

## PRESENTATION
judge confusion, unsupported claims, missing evidence

---

# 39. FINAL HUMAN SIGN-OFF

Human must be able to explain:

- problem
- user
- solution
- differentiation
- architecture
- data flow
- technical choices
- AI choices
- failure behavior
- security
- limitations
- production scaling
- actual scope vs future scope
- strongest demo moment

Only after this is the project presentation-ready.

---

# 40. NEXT TOOL PROTOCOL

Every handoff must end with a concrete, copy-paste-ready routing block:

## NEXT TOOL
Exact next person/tool.

## ACTION
Exact action the Human must take.

## PACKET
Exact information/files/evidence to transfer.

## COPY-PASTE PROMPT
When an external AI is required, provide the complete validation/review prompt here.
The Human should not have to invent the prompt.

## EXPECTED OUTPUT
Exact response structure required from the receiving tool.

## RETURN TO
Where the result must go next.

The handoff must fit into one paste or one clearly defined file/evidence packet whenever practical.

Examples:

CHATGPT:
NEXT TOOL: ANTIGRAVITY
ACTION: Implement the Task Card.
PACKET: task + criteria + tier + scope + stop conditions.

ANTIGRAVITY → GEMINI:
NEXT TOOL: GEMINI
ACTION: Run the T2 implementation review using the prompt below.
PACKET: task + acceptance criteria + relevant diff + surrounding interfaces + tests + raw evidence + known risks.
COPY-PASTE PROMPT: [complete Gemini validation prompt]
EXPECTED OUTPUT: VERIFIED/PLAUSIBLE/REJECTED + BLOCKER/SHOULD-FIX/DEFER + reproduction guidance.
RETURN TO: CHATGPT only if material findings exist; otherwise continue directly.

ANTIGRAVITY → KIMI/DEEPSEEK:
NEXT TOOL: KIMI or DEEPSEEK
ACTION: Run the blind milestone red-team using the prompt below.
PACKET: milestone goal + requirements + architecture summary + actual diff + tests + Human observations + relevant screenshots/logs.
COPY-PASTE PROMPT: [complete blind red-team prompt]
EXPECTED OUTPUT: findings + severity + evidence + reproduction steps.
RETURN TO: CHATGPT.

GEMINI:
NEXT TOOL: CHATGPT only when material findings/disagreement/escalation exists; otherwise continue.
ACTION: Provide findings in the required taxonomy.
PACKET: findings + evidence + status + impact.

KIMI/DEEPSEEK:
NEXT TOOL: CHATGPT
ACTION: adjudicate red-team findings.
PACKET: findings + severity + reproduction/evidence.

CHATGPT:
NEXT TOOL: ANTIGRAVITY / HUMAN / GEMINI / KIMI-DEEPSEEK
ACTION: one explicit next step.
PACKET: only relevant material, with a copy-paste prompt when another AI is required.

---


# 40.1 LIVE-CONTEXT RULE

Do not give any tool the entire 1,200+ line workflow by default.
Use the One-Page Operating Card for live execution and provide each tool only the sections relevant to its current role.

Recommended minimum excerpts:
- Antigravity: execution rules, risk re-tiering, execution loop, evidence/test integrity, fast-path safety, handoff protocol.
- Gemini: Gemini review section + relevant task/evidence packet.
- Kimi/DeepSeek: blind red-team section + milestone packet.
- ChatGPT: full workflow reference when making routing/adjudication decisions.

The canonical workflow remains the source of truth; excerpts are operational views, not alternative workflows.
# 41. CANONICAL STATE MACHINE

HUMAN
↓
CHATGPT
goal → task → criteria → risk
↓
ANTIGRAVITY
inspect → plan → build → run → test → evidence
↓
T0/T1 → Human quick check → NEXT
T2 → Gemini → ChatGPT triage → fix/reproduce/continue
T3 → checkpoint → physical test → human test → blind red team → ChatGPT adjudication → fix/retest/pass → Human sign-off
↓
teach-back + state update + judge Q&A
↓
NEXT MILESTONE
↓
FREEZE
↓
FINAL DEMO
↓
SUBMIT

---

# 42. FAILURE RECOVERY

## Agent loops
Stop at attempt/time limit and create diagnostic packet.

## Reviewer disagreement
Reproduce/test before changing code.

## Deployment fails
Deployment becomes P0.

## Demo path unstable
Freeze features and stabilize.

## Time collapses
Cut P4 → P3 → lower P2.
Protect P0/P1.

## Architecture blocked
Human + explicit architecture decision.

---

# 43. WHAT TO AUTOMATE

Automate:
- testing
- lint/type/build
- browser checks
- smoke tests
- scans
- evidence collection
- Git diff/state collection
- handoff packet generation
- deployment checks

Keep Human-controlled:
- problem choice
- scope cuts
- architecture approval
- risk acceptance
- milestone PASS
- final claims
- final demo
- submission

---

# 44. IMPORTANT: DOES ANTIGRAVITY ALWAYS REMEMBER THIS WORKFLOW?

No. Do not assume that simply placing a workflow document in the repository means the agent will permanently obey every instruction in every conversation.

Use the platform layers correctly:

### Persistent rules
Put non-negotiable constraints/invariants in applicable `AGENTS.md` / active `.agents/rules/`.

### Workflow/skill
Put multi-step operating procedures here and invoke/make them available as the appropriate Antigravity workflow/skill.

### Project state
Keep current state in project artifacts.

### Current task
ChatGPT supplies the task packet.

So:
- the RULES govern behavior
- the WORKFLOW governs process
- the PROJECT STATE provides memory
- the TASK PACKET provides immediate instructions

The workflow file itself should not be treated as magical permanent memory.

---


# 44.1 STANDARD WORKFLOW VS PROJECT BUILD PLAN

The workflow is intentionally project-agnostic. Do **not** rewrite V4.1 for each hackathon project.

After the problem statement and architecture are selected:
1. ChatGPT reads the selected problem, rubric, architecture, constraints, and available tools.
2. ChatGPT creates/updates `BUILD_PLAN.md`.
3. `BUILD_PLAN.md` instantiates the workflow with the project's concrete milestones, vertical slices, dependencies, acceptance criteria, risks, deployment target, and review points.
4. Antigravity executes the current Task Card against that build plan.
5. The Context Pack records current state; active rules enforce permanent constraints.

Never put project-specific architecture, API contracts, task lists, or feature details into the canonical workflow unless they are universal process rules.
# 45. SUCCESS CONDITION

The workflow is successful when:

- the core value works
- P0 requirements are evidenced
- risky work received appropriate review
- rollback is real
- demo is rehearsed from a clean environment
- external failures are planned for
- the Human understands the project
- judge answers are grounded in the actual implementation
- no unresolved critical issue exists
- Human signs off

---

# 46. FINAL OPERATING MANTRA

CHATGPT coordinates.

ANTIGRAVITY builds, executes, tests, and teaches.

GEMINI reviews risky implementation work using primary evidence.

KIMI/DEEPSEEK attacks milestones independently.

THE HUMAN tests, learns, decides, and presents.

RISK determines review depth.

EVIDENCE determines truth.

GIT makes recovery real.

PROJECT STATE prevents memory drift.

ACTIVE `.agents/rules/` constrain execution.

EVERY TOOL TELLS THE HUMAN WHAT COMES NEXT.

THE CLOSER THE DEADLINE, THE SIMPLER THE WORKFLOW.


# 47. LOCK POLICY

V4.1 is considered complete after the dry run passes.
Do not create V4.2 merely from preference or another document review. Change the standard workflow only when a real dry-run or hackathon incident exposes a reproducible process failure.

When a change is justified, record a short changelog entry with:
- observed failure
- evidence
- minimal process change
- reason the change improves speed, reliability, clarity, or safety

This keeps the workflow stable instead of endlessly expanding.

END OF WORKFLOW
