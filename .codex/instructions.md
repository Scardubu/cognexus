# NEXUS coding instructions

Read `AGENTS.md` before modifying this repository. Preserve canonical OpenAI Agents SDK imports from `agents`, local specialist imports from `nexus_agents`, hierarchical routing, `parallel_tool_calls=False`, bounded run admission, per-session ordering, deterministic guardrails, explicit session fallback policy, configuration-driven model names, content-free telemetry, and the required NEXUS trace block.

Do not add a local top-level `agents/` package or compatibility bridge. Do not create a new OpenAI client per request. Do not stream unvalidated model deltas. Run all required quality gates before claiming completion.
