# AquaSentinel — Model Prompting Guide
## One source of truth, specialized models, and bounded Antigravity tasks

## Core rule

Every prompt generated for Antigravity must contain this exact directive near the top:

**FOLLOW INSTRUCTIONS DO NOT DEVIATE.**

The generated prompt must also instruct Antigravity to read active rules, project context, the build plan, architecture, interface contracts, decision log, and applicable V4.1 skill before implementation. This phrase reinforces the workflow; it does not replace acceptance criteria or evidence.

## Source-of-truth hierarchy

1. Official hackathon rules and data documentation.
2. Human-approved scope and decisions.
3. `ARCHITECTURE.md` + `DECISION_LOG.md`.
4. `INTERFACE_CONTRACTS.md`.
5. Actual code, tests, runtime data and logs.
6. `PROJECT_CONTEXT.md` / `BUILD_PLAN.md`.
7. Research and AI opinions.
8. Conversation history.

Lower-level sources do not silently override higher-level decisions.

## ChatGPT role: orchestrator/adjudicator
Use ChatGPT to:
- create the next task card for Antigravity;
- assign risk tier and ownership;
- consolidate state and decision changes;
- route T2/T3 work to Gemini/Kimi;
- compare review evidence;
- reject feature creep;
- prepare judge answers grounded in executed evidence.

ChatGPT should not issue vague prompts like “build the whole project”. It must define one bounded task, exact files, acceptance checks, exclusions, timebox, stop condition, and expected report.

## Gemini role: evidence-focused reviewer
Send Gemini:
- current task and criteria;
- relevant diff/files;
- actual test outputs/logs;
- current architecture/contract;
- known risks and NOT VERIFIED list.

Ask Gemini to classify evidence as VERIFIED / PLAUSIBLE / REJECTED and impact as BLOCKER / SHOULD-FIX / DEFER. Do not ask for another whole architecture unless a real blocker requires it.

## Kimi role: independent red team
Use Kimi on milestone or disputed/high-risk changes, not every small styling task. Whenever possible, make the first review independent of Gemini's conclusion. Give it raw artifacts and acceptance criteria; ask it to find counterexamples and demo-breaking defects.

## Antigravity task-card template

```text
FOLLOW INSTRUCTIONS DO NOT DEVIATE.

Read AGENTS.md and the active .agents/rules. Read PROJECT_CONTEXT.md, BUILD_PLAN.md, ARCHITECTURE.md, INTERFACE_CONTRACTS.md, DECISION_LOG.md, and the applicable V4.1 workflow skill before acting.

TASK:
[One concrete outcome]

RISK TIER:
[T0/T1/T2/T3]

OWNER / FILE BOUNDARY:
[Owned files only]

ACCEPTANCE CRITERIA:
- [Observable criterion]
- [Automated check]
- [Evidence to report]

SCOPE:
[Files/functions allowed]

OUT OF SCOPE:
[Explicit exclusions]

VALIDATION:
[Exact commands, tests, or manual checks]

STOP CONDITIONS:
- Stop if the contract contradicts the current repository.
- Stop before adding dependencies or changing architecture.
- If the same check fails twice, stop and report evidence.
- Never fabricate test results or dataset facts.

REPORT:
COMPLETED / FILES / TESTS / RESULT / NOT VERIFIED / STATE DELTA / LEARNING NOTE

Do not claim success without evidence.
```

## Tool-routing rules
- Simple local change: ChatGPT → Antigravity → targeted test → Human quick check.
- Cross-module/statistical/data/label change: ChatGPT task card → Antigravity implementation/evidence → Gemini review if risk requires → ChatGPT adjudication.
- Milestone / pre-demo: known-good checkpoint → full critical path test → Human manual test → independent Kimi red-team → ChatGPT adjudication.
- If two fix cycles fail: stop blind retries and escalate with exact symptom + attempts + evidence.

## External-review prompt template

```text
FOLLOW INSTRUCTIONS DO NOT DEVIATE.

Review only the supplied scope and evidence against the attached approved architecture and acceptance criteria. Do not invent test results, data fields or facts. Separate:
- VERIFIED: concrete artifact supports the claim
- PLAUSIBLE: reasoned but not proved
- REJECTED: evidence contradicts the claim

For each material issue include impact (BLOCKER / SHOULD-FIX / DEFER), exact evidence/location, reproduction/check, minimal fix and whether implementation should continue. Preserve unrelated architecture and scope. Do not rewrite the entire system.
```

## Prompt hygiene
- Do not paste `.env`, keys, tokens, passwords or secret-bearing logs into external tools.
- Do not send every project file to every model; send only canonical context and relevant artifacts.
- Do not treat three model approvals as truth. Test where possible.
- Do not allow a reviewer to implement a fix directly from narrative; first reproduce the claim locally.
