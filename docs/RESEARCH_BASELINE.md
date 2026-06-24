# Research and Standards Baseline

Research was verified against official documentation available on 23 June 2026. Community repositories were used only as examples; normative behavior comes from primary documentation.

## Agent Skills

Primary sources:

- Agent Skills specification: <https://agentskills.io/specification>
- Client implementation guide: <https://agentskills.io/client-implementation/adding-skills-support>
- Skill creator best practices: <https://agentskills.io/skill-creation/best-practices>
- Description optimization: <https://agentskills.io/skill-creation/optimizing-descriptions>
- Anthropic public skills repository: <https://github.com/anthropics/skills>

Applied requirements:

- a skill is a directory with `SKILL.md`;
- YAML frontmatter includes a lowercase kebab-case `name` and a concise `description`;
- discovery loads metadata only;
- activation loads the core body;
- references/assets/scripts load only when needed;
- core files remain below the recommended 500-line/5,000-token region;
- descriptions communicate both capability and activation conditions;
- resources are relative to the skill directory.

## OpenAI Agents SDK

Primary sources:

- Agents: <https://openai.github.io/openai-agents-python/agents/>
- Tools and hosted tool search: <https://openai.github.io/openai-agents-python/tools/>
- Guardrails: <https://openai.github.io/openai-agents-python/guardrails/>
- Sessions: <https://openai.github.io/openai-agents-python/sessions/>
- Tracing: <https://openai.github.io/openai-agents-python/tracing/>
- Human-in-the-loop approvals: <https://openai.github.io/openai-agents-python/human_in_the_loop/>

Applied patterns:

- keep `Agent` + `Runner` as the orchestration loop;
- expose specialists through `Agent.as_tool()`;
- use deferred tools plus hosted tool search for large tool surfaces;
- keep deterministic input/output guards outside skill text;
- use sessions for conversation state rather than duplicating state layers;
- avoid sensitive trace payloads;
- reserve human approval for privileged, destructive, financial, or externally visible tools.

## LangChain and LangGraph

Primary sources:

- Multi-agent overview: <https://docs.langchain.com/oss/python/langchain/multi-agent>
- Skills pattern: <https://docs.langchain.com/oss/python/langchain/multi-agent/skills>
- Subagents pattern: <https://docs.langchain.com/oss/python/langchain/multi-agent/subagents>
- Context engineering: <https://docs.langchain.com/oss/python/langchain/context-engineering>
- LangGraph graph API: <https://docs.langchain.com/oss/python/langgraph/graph-api>

Applied lessons:

- prefer one capable agent with dynamic tools before adding agent count;
- use skills when lightweight prompt/domain specialization is enough;
- use subagents when context isolation, ownership, or different tools/models justify delegation;
- make state schemas and transitions explicit for durable workflows;
- control what each model call sees rather than dumping all context.

## CrewAI

Primary sources:

- Documentation: <https://docs.crewai.com/>
- Flows: <https://docs.crewai.com/en/concepts/flows>
- Crews: <https://docs.crewai.com/en/concepts/crews>
- Human feedback in flows: <https://docs.crewai.com/en/learn/human-feedback-in-flows>

Applied lessons:

- distinguish autonomous collaboration from deterministic event-driven workflow control;
- preserve typed state and explicit flow transitions;
- checkpoint or externalize state for resumable work;
- insert human feedback at material approval boundaries.

## AutoGen

Primary sources:

- Teams: <https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html>
- Handoffs: <https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/handoffs.html>
- Human in the loop: <https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/human-in-the-loop.html>

Applied lessons:

- start with a single agent and move to a team only when needed;
- define termination and handoff behavior explicitly;
- avoid parallel calls where nested agent/team tools have concurrency constraints;
- make lifecycle, reset, pause, and resume behavior testable.

## LlamaIndex

Primary sources:

- Structured agent output: <https://docs.llamaindex.ai/en/latest/understanding/agent/structured_output/>
- Agents as tools example: <https://docs.llamaindex.ai/en/latest/examples/agent/agents_as_tools/>

Applied lessons:

- use structured output for machine-consumed boundaries;
- treat retrieval, agents, and workflows as separate concerns;
- use agents-as-tools when delegated context isolation is useful.

## Evaluation criteria used

Every runtime and skill component was reviewed for:

1. purpose and trigger clarity;
2. context efficiency and progressive disclosure;
3. typed interfaces and structured output;
4. path, input, secret, and execution safety;
5. bounded retries, timeouts, concurrency, and payload sizes;
6. failure, cancellation, fallback, and rollback behavior;
7. observability without sensitive or high-cardinality data;
8. deterministic tests and validation evidence;
9. portability across filesystem-based skill clients;
10. documentation, examples, versioning, and maintenance ownership.
