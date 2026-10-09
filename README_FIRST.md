# AquaSentinel Project Operating System — Start Here

This pack configures the project for a build sprint of **less than three hours**. It contains the project context, locked architecture, decision log, compact Antigravity rules, the unchanged hackathon workflow skill, tailored subagents, the build plan, and role/tool instructions.

## Do these first

1. Extract this kit into the **root of the AquaSentinel code repository**. Merge `.agents/` carefully if it already exists; do not overwrite unrelated rules, skills, or agents.
2. Read `PROJECT_CONTEXT.md`, `ARCHITECTURE.md`, `INTERFACE_CONTRACTS.md`, `DECISION_LOG.md`, and `BUILD_PLAN.md`.
3. Keep `AGENTS.md` short and always active. Use `.agents/rules/` for triggered constraints and `.agents/agents/` for on-demand specialists.
4. Keep `.agents/skills/hackathon-ai-orchestration/SKILL.md` unchanged. It is a copy of the supplied locked V4.1 workflow. Do not edit it for AquaSentinel; project adaptation belongs in `BUILD_PLAN.md` and the project context.
5. Open `FILES_AND_SETUP_GUIDE.md` to see what to put into Antigravity, ChatGPT, Gemini, and Kimi.
6. Use `MODEL_PROMPTING_GUIDE.md` and `tool-instructions/` for tool-specific behavior. All prompts sent to Antigravity must include the exact line **FOLLOW INSTRUCTIONS DO NOT DEVIATE**.
7. Follow `BUILD_PLAN.md` time boxes. Do not spend the sprint perfecting the agent system.

## Critical product truth

AquaSentinel evaluates **simulated BattLeDIM benchmark telemetry**. Sequential replay is a demo of real-time-style processing, not a live municipal connection. The application detects statistical anomalies; it does not prove physical leaks, exact pipe locations, or actual water savings.

## File map

- `AGENTS.md` — small workspace guardrails, loaded by Antigravity.
- `PROJECT_CONTEXT.md` — canonical short project memory.
- `ARCHITECTURE.md` — final implementation architecture.
- `INTERFACE_CONTRACTS.md` — module/API contracts for parallel work.
- `DECISION_LOG.md` — decision layer and approved/rejected/deferred decisions.
- `BUILD_PLAN.md` — timed build plan for less than three hours.
- `PROJECT_PLAYBOOK.md` — project-specific operation of the locked V4.1 workflow.
- `ALPHA_ROLE.md`, `BETA_ROLE.md`, `GAMMA_ROLE.md` — non-overlapping ownership.
- `MODEL_PROMPTING_GUIDE.md` — how ChatGPT/Gemini/Kimi prompts must be generated.
- `tool-instructions/` — instructions to paste into each AI tool.
- `handoff-prompts/` — copy/paste-ready role and reviewer tasks.
- `.agents/rules/` — progressive-disclosure rules.
- `.agents/agents/` — tailored specialist subagents.
- `.agents/skills/hackathon-ai-orchestration/SKILL.md` — supplied, unchanged workflow.
