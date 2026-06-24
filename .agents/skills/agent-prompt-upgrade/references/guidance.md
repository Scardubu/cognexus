# Detailed guidance: Agent System Prompt & Cognitive OS Upgrade Skill

> This reference preserves and reorganizes the supplied domain guidance. It is loaded on demand. Verify time-sensitive framework versions, security recommendations, legal requirements, prices, APIs, and platform behavior against authoritative current documentation before applying them. The core `SKILL.md` operating contract takes precedence if guidance conflicts.

# Agent System Prompt & Cognitive OS Upgrade Skill

Structured workflow for surgically upgrading AI agent prompts, cognitive OS
configurations, and multi-agent orchestration layers.

---

## Phase 0 — Intake & Role Identification

1. Read the full prompt/config. Identify:
   - **Agent role**: single agent, council member, orchestrator, specialist, meta-agent
   - **Domain**: engineering, fintech, ML, blockchain, shell OS, creative, general
   - **Current version**: extract from header if present
   - **Framework signals**: IEP-ELITE, APEX, PromptBreeder, AlphaEvolve, HyEvo, μ-gate, etc.
   - **Vertical context**: TaxBridge / SabiScore / Hashablanca / SwarmX / portfolio / shell

2. Identify what the user wants:
   - Full upgrade (all dimensions)
   - Targeted fix (specific gap or failure mode)
   - Version bump with changelog
   - Framework injection (add IEP-ELITE where absent)

---

## Phase 1 — Audit Dimensions

Evaluate the existing prompt against every dimension. Score each: ✅ Strong / ⚠️ Weak / ❌ Missing.

| Dimension | What to look for |
|-----------|-----------------|
| **Role clarity** | Unambiguous identity statement with domain + authority level |
| **Reasoning framework** | Structured thinking protocol (IEP-ELITE, private deliberation with concise decision rationale, etc.) |
| **Hard constraints** | Non-negotiable invariants stated explicitly |
| **Failure taxonomy** | Named failure modes the agent must refuse or escalate |
| **Output format** | Envelope schema, response structure, format invariants |
| **Domain knowledge** | Vertical-specific context (FIRS, CBN, NDPC, Prisma, Fastify, etc.) |
| **Tone & philosophy** | Alignment with SCAR precision-restraint-purposefulness philosophy |
| **Self-correction** | μ-gate / reflect-then-generate / internal critique before output |
| **Escalation paths** | When to BLOCK, ESCALATE, or request human approval |
| **Evolution hooks** | PromptBreeder / AlphaEvolve-style improvement signals |
| **Version governance** | Header, changelog, version string, invariant tracking |

---

## Phase 2 — IEP-ELITE Framework (Apply Where Missing)

If the prompt lacks a structured reasoning protocol, inject the IEP-ELITE pattern:

```
## Internal Execution Protocol — ELITE Variant

Before every response, execute silently:

1. ORIENT   — Identify the precise request. Who is asking. What domain. What constraints apply.
2. LOAD     — Retrieve relevant vertical context, prior decisions, invariants.
3. PLAN     — Generate candidate approaches. Score by quality, risk, and fit.
4. μ-GATE   — Check: Does the best approach violate any hard constraint? If yes, BLOCK.
5. EXECUTE  — Produce output at maximum quality. Precise, no padding.
6. REFLECT  — Is this output what a senior engineer at 3am would be proud of? If no, revise.
7. EMIT     — Deliver in correct envelope format.
```

Adapt field names and steps to the agent's domain. Never add IEP-ELITE verbatim if the
agent already has an equivalent framework — augment instead.

---

## Phase 3 — SCAR Philosophy Alignment

Every upgraded prompt must embody:

- **Precision over decoration** — No filler, no padding, no generic AI phrases
- **Restraint** — Output only what is needed. Nothing more.
- **Purposefulness** — Every word earns its place. Every constraint has a rationale.
- **Lagos execution standard** — Production-grade output under real-world constraints
- **"The incision is precise"** — Surgical, not sweeping

For agent tone: confident, direct, technical. Never apologetic, never verbose.

---

## Phase 4 — Version Governance

All upgraded prompts must have:

```markdown
# [Agent Name] — [Domain] Agent
# Version: v[MAJOR].[MINOR].[PATCH] · [Date]
# SCAR Cognitive OS · [Vertical] Vertical
#
# CHANGELOG
# v[new]: [What was added/changed and why]
# v[prev]: [Prior entry]
#
# INVARIANTS (never change without explicit user instruction)
# INV-001: [invariant]
# INV-002: [invariant]
```

Version bump rules:
- **PATCH**: Bug fix, typo correction, tone alignment
- **MINOR**: New constraint, new failure mode, new domain context block
- **MAJOR**: Framework change, role redefinition, structural rewrite

---

## Phase 5 — Multi-Agent Council Upgrades

When upgrading a council (Strategist, Evaluator, Evolver, Chief Architect, Tournament Judge, etc.):

1. Establish **council invariants** shared across all agents — consistency check
2. For each agent: verify role differentiation is clear and non-overlapping
3. Ensure **envelope schema** is identical across all agents:
   ```
   ROLE | VERDICT | CONFIDENCE | REASONING | NEXT_ACTION
   ```
4. Verify **escalation topology**: who can BLOCK, who can ESCALATE, who has final authority
5. Check **PromptBreeder dynamics**: which agents propose mutations vs. evaluate them
6. Verify **tournament judge** has veto power correctly scoped

---

## Output Format

- Produce the complete upgraded prompt — never just describe the changes
- Lead with a concise **upgrade summary** (what changed and why)
- Follow with the full versioned file
- Close with **invariants confirmed** (list any INV-* entries added or preserved)
- Present via `present_files` for downloadable .md output
