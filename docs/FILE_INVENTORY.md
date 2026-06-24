# Attached File Inventory

This inventory records the two user-supplied archives exactly as received, before normalization. Directory entries are omitted from counts; generated caches and compiled artifacts are called out separately.

## `COGNEXUS_v3.1.0_README_Upgrade(1).zip`

- Files: **91**
- Compressed size: **131,095 bytes**
- Main types: `.py` 64, `.md` 10, `<none>` 4, `.yml` 3, `.yaml` 3, `.json` 2, `.txt` 2, `.example` 1, `.toml` 1, `.sh` 1

<details>
<summary>Full archive file list</summary>

```text
nexus-openai-production-v3.1.0/.codex/instructions.md
nexus-openai-production-v3.1.0/.cursorrules
nexus-openai-production-v3.1.0/.dockerignore
nexus-openai-production-v3.1.0/.env.example
nexus-openai-production-v3.1.0/.github/workflows/ci.yml
nexus-openai-production-v3.1.0/.github/workflows/docker.yml
nexus-openai-production-v3.1.0/.gitignore
nexus-openai-production-v3.1.0/AGENTS.md
nexus-openai-production-v3.1.0/Dockerfile
nexus-openai-production-v3.1.0/README.md
nexus-openai-production-v3.1.0/config/__init__.py
nexus-openai-production-v3.1.0/config/agent_registry.json
nexus-openai-production-v3.1.0/config/settings.py
nexus-openai-production-v3.1.0/config/stack_manifest.json
nexus-openai-production-v3.1.0/deploy/otel-collector-config.yaml
nexus-openai-production-v3.1.0/docker-compose.yml
nexus-openai-production-v3.1.0/docs/ARCHITECTURE.md
nexus-openai-production-v3.1.0/docs/DEPLOYMENT.md
nexus-openai-production-v3.1.0/docs/EVALS.md
nexus-openai-production-v3.1.0/docs/OPERATIONS.md
nexus-openai-production-v3.1.0/docs/SECURITY.md
nexus-openai-production-v3.1.0/docs/SETUP.md
nexus-openai-production-v3.1.0/docs/migration_checklist.md
nexus-openai-production-v3.1.0/evals/cases/basic.yaml
nexus-openai-production-v3.1.0/evals/promptfoo.yaml
nexus-openai-production-v3.1.0/middleware/__init__.py
nexus-openai-production-v3.1.0/middleware/constraint_validator.py
nexus-openai-production-v3.1.0/middleware/guardrails.py
nexus-openai-production-v3.1.0/middleware/input_guardrail.py
nexus-openai-production-v3.1.0/middleware/output_guardrail.py
nexus-openai-production-v3.1.0/middleware/trace_block_validator.py
nexus-openai-production-v3.1.0/nexus_agents/__init__.py
nexus-openai-production-v3.1.0/nexus_agents/base_agent.py
nexus-openai-production-v3.1.0/nexus_agents/registry.py
nexus-openai-production-v3.1.0/nexus_agents/specialists.py
nexus-openai-production-v3.1.0/observability/__init__.py
nexus-openai-production-v3.1.0/observability/logging.py
nexus-openai-production-v3.1.0/observability/metrics.py
nexus-openai-production-v3.1.0/observability/tracing.py
nexus-openai-production-v3.1.0/orchestrator/__init__.py
nexus-openai-production-v3.1.0/orchestrator/conflict_resolver.py
nexus-openai-production-v3.1.0/orchestrator/errors.py
nexus-openai-production-v3.1.0/orchestrator/model_router.py
nexus-openai-production-v3.1.0/orchestrator/nexus_agent.py
nexus-openai-production-v3.1.0/orchestrator/nexus_prompt.py
nexus-openai-production-v3.1.0/orchestrator/run.py
nexus-openai-production-v3.1.0/orchestrator/runtime.py
nexus-openai-production-v3.1.0/orchestrator/tier_classifier.py
nexus-openai-production-v3.1.0/pyproject.toml
nexus-openai-production-v3.1.0/requirements-dev.txt
nexus-openai-production-v3.1.0/requirements.txt
nexus-openai-production-v3.1.0/scripts/setup.sh
nexus-openai-production-v3.1.0/scripts/test_nexus.py
nexus-openai-production-v3.1.0/security/__init__.py
nexus-openai-production-v3.1.0/security/policies.py
nexus-openai-production-v3.1.0/security/rate_limits.py
nexus-openai-production-v3.1.0/security/sanitization.py
nexus-openai-production-v3.1.0/security/secrets.py
nexus-openai-production-v3.1.0/server/__init__.py
nexus-openai-production-v3.1.0/server/app.py
nexus-openai-production-v3.1.0/server/dependencies.py
nexus-openai-production-v3.1.0/server/errors.py
nexus-openai-production-v3.1.0/server/middleware.py
nexus-openai-production-v3.1.0/server/schemas.py
nexus-openai-production-v3.1.0/sessions/__init__.py
nexus-openai-production-v3.1.0/sessions/compaction.py
nexus-openai-production-v3.1.0/sessions/redis_session.py
nexus-openai-production-v3.1.0/sessions/session_manager.py
nexus-openai-production-v3.1.0/sessions/sqlite_session.py
nexus-openai-production-v3.1.0/tests/conftest.py
nexus-openai-production-v3.1.0/tests/test_guardrails.py
nexus-openai-production-v3.1.0/tests/test_health.py
nexus-openai-production-v3.1.0/tests/test_model_router.py
nexus-openai-production-v3.1.0/tests/test_observability.py
nexus-openai-production-v3.1.0/tests/test_registry.py
nexus-openai-production-v3.1.0/tests/test_runtime.py
nexus-openai-production-v3.1.0/tests/test_server_run.py
nexus-openai-production-v3.1.0/tests/test_sessions.py
nexus-openai-production-v3.1.0/tests/test_validators.py
nexus-openai-production-v3.1.0/tools/__init__.py
nexus-openai-production-v3.1.0/tools/_handlers.py
nexus-openai-production-v3.1.0/tools/namespaces.py
nexus-openai-production-v3.1.0/tools/registry.py
nexus-openai-production-v3.1.0/tools/search_tool.py
nexus-openai-production-v3.1.0/tracing/__init__.py
nexus-openai-production-v3.1.0/tracing/otel_setup.py
nexus-openai-production-v3.1.0/validators/__init__.py
nexus-openai-production-v3.1.0/validators/arch02_validator.py
nexus-openai-production-v3.1.0/validators/arch04_validator.py
nexus-openai-production-v3.1.0/validators/constraint_validator.py
nexus-openai-production-v3.1.0/validators/trace_block_validator.py
```

</details>

## `Skills 2(1).zip`

- Files: **149**
- Compressed size: **1,033,919 bytes**
- Main types: `.skill` 56, `.md` 53, `.zip` 17, `.py` 10, `.json` 7, `.txt` 2, `.sh` 2, `.yaml` 2

<details>
<summary>Full archive file list</summary>

```text
Skills/ai-skills.zip
__MACOSX/Skills/._ai-skills.zip
Skills/elite-skill-forge.skill
__MACOSX/Skills/._elite-skill-forge.skill
Skills/ai-runtime-scoringmodel.json
__MACOSX/Skills/._ai-runtime-scoringmodel.json
Skills/# AI Engineering Control SysteΓÇª.txt
__MACOSX/Skills/._# AI Engineering Control SysteΓÇª.txt
Skills/Research Report.md
__MACOSX/Skills/._Research Report.md
Skills/NEXUS_OpenAI_Architecture_Analysis.md
Skills/OpenAI Codex and Agents SDK_ Production Configuration Reference (June 2026).md
__MACOSX/Skills/._OpenAI Codex and Agents SDK_ Production Configuration Reference (June 2026).md
Skills/Skills.zip
Skills/files (1).zip
__MACOSX/Skills/._files (1).zip
Skills/swarmxq_skills_integration_upgrade.zip
__MACOSX/Skills/._swarmxq_skills_integration_upgrade.zip
Skills/Skills 2.zip
Skills/OpenAI Multi-Agent and Orchestration Ecosystem_ A Technical Build Guide for NEXUS-Style Skill Orchestration (2025-2026).md
__MACOSX/Skills/._OpenAI Multi-Agent and Orchestration Ecosystem_ A Technical Build Guide for NEXUS-Style Skill Orchestration (2025-2026).md
Skills/files (1) 2.zip
Skills/elite-skill-forge.md
Skills/nexus-openai-production-v2.1.zip
__MACOSX/Skills/._nexus-openai-production-v2.1.zip
Skills/NEXUS_to_OpenAI_Migration_Guide.md
Skills/NEXUS.md
Skills/SCAR Skills v2.zip
__MACOSX/Skills/._SCAR Skills v2.zip
Skills/Skills_Enhanced 2.zip
__MACOSX/Skills/._Skills_Enhanced 2.zip
Skills/ai-skills-registry.json
Skills/CLAUDE.md
Skills/swarmxq_skills_integration_upgrade/setup_skill_integration.sh
__MACOSX/Skills/swarmxq_skills_integration_upgrade/._setup_skill_integration.sh
Skills/files (1)/ANALYSIS_REPORT.md
__MACOSX/Skills/files (1)/._ANALYSIS_REPORT.md
Skills/files (1)/ai-runtime-scoringmodel.json
__MACOSX/Skills/files (1)/._ai-runtime-scoringmodel.json
Skills/files (1)/elite-skill-forge.md
__MACOSX/Skills/files (1)/._elite-skill-forge.md
Skills/files (1)/ai-skills-registry.json
__MACOSX/Skills/files (1)/._ai-skills-registry.json
Skills/files (1)/CLAUDE.md
__MACOSX/Skills/files (1)/._CLAUDE.md
Skills/files (1) 2/NEXUS.md
__MACOSX/Skills/files (1) 2/._NEXUS.md
Skills/files (1) 2/CLAUDE.md
__MACOSX/Skills/files (1) 2/._CLAUDE.md
Skills/files 6/ai-feature-architect.skill
__MACOSX/Skills/files 6/._ai-feature-architect.skill
Skills/files 6/backend-systems-auditor.skill
__MACOSX/Skills/files 6/._backend-systems-auditor.skill
Skills/files 6/vscode-monorepo-forge.skill
__MACOSX/Skills/files 6/._vscode-monorepo-forge.skill
Skills/files 6/elite-skill-forge.skill
__MACOSX/Skills/files 6/._elite-skill-forge.skill
Skills/files 6/prisma-database-architect.skill
__MACOSX/Skills/files 6/._prisma-database-architect.skill
Skills/files 6/vscode-ai-agent-stack.skill
__MACOSX/Skills/files 6/._vscode-ai-agent-stack.skill
Skills/files 6/prompt-engineering-architect.skill
__MACOSX/Skills/files 6/._prompt-engineering-architect.skill
Skills/files 6/design-token-system-architect.skill
__MACOSX/Skills/files 6/._design-token-system-architect.skill
Skills/files 6/security-hardening-auditor.skill
__MACOSX/Skills/files 6/._security-hardening-auditor.skill
Skills/files 6/opentelemetry-observability-architect.skill
__MACOSX/Skills/files 6/._opentelemetry-observability-architect.skill
Skills/files 6/effect-ts-layer-architect.skill
__MACOSX/Skills/files 6/._effect-ts-layer-architect.skill
Skills/files 6/vscode-cognitive-os.skill
__MACOSX/Skills/files 6/._vscode-cognitive-os.skill
Skills/files 6/api-automation-architect.skill
__MACOSX/Skills/files 6/._api-automation-architect.skill
Skills/files 6/motion-interaction-architect.skill
__MACOSX/Skills/files 6/._motion-interaction-architect.skill
Skills/files 6/frontend-design-auditor.skill
__MACOSX/Skills/files 6/._frontend-design-auditor.skill
Skills/files 6/typescript-config-surgeon.skill
__MACOSX/Skills/files 6/._typescript-config-surgeon.skill
Skills/files 6/vscode-debug-profiler.skill
__MACOSX/Skills/files 6/._vscode-debug-profiler.skill
Skills/files 6/git-workflow-architect.skill
__MACOSX/Skills/files 6/._git-workflow-architect.skill
Skills/files 6/react-native-expo-architect.skill
__MACOSX/Skills/files 6/._react-native-expo-architect.skill
Skills/files 6/component-quality-gate.skill
__MACOSX/Skills/files 6/._component-quality-gate.skill
Skills/files 6/SETUP_AND_IMPLEMENTATION.md
__MACOSX/Skills/files 6/._SETUP_AND_IMPLEMENTATION.md
Skills/files 6/bullmq-job-architect.skill
__MACOSX/Skills/files 6/._bullmq-job-architect.skill
Skills/files 6/nextjs-performance-architect.skill
__MACOSX/Skills/files 6/._nextjs-performance-architect.skill
Skills/files 6/testing-strategy-architect.skill
__MACOSX/Skills/files 6/._testing-strategy-architect.skill
Skills/files/surgical-merge.skill
__MACOSX/Skills/files/._surgical-merge.skill
Skills/files/portfolio-conviction-engine.skill
__MACOSX/Skills/files/._portfolio-conviction-engine.skill
Skills/files/agent-prompt-upgrade.skill
__MACOSX/Skills/files/._agent-prompt-upgrade.skill
Skills/files/shell-cognitive-os.skill
__MACOSX/Skills/files/._shell-cognitive-os.skill
Skills/files/codebase-zip-audit.zip
__MACOSX/Skills/files/._codebase-zip-audit.zip
Skills/swarmxq_skills_integration_upgrade/tools/audit_skills.py
__MACOSX/Skills/swarmxq_skills_integration_upgrade/tools/._audit_skills.py
Skills/swarmxq_skills_integration_upgrade/tests/test_skill_loader.py
__MACOSX/Skills/swarmxq_skills_integration_upgrade/tests/._test_skill_loader.py
Skills/swarmxq_skills_integration_upgrade/tests/test_skill_catalog.py
__MACOSX/Skills/swarmxq_skills_integration_upgrade/tests/._test_skill_catalog.py
Skills/swarmxq_skills_integration_upgrade/docs/CLI_PATCH.md
__MACOSX/Skills/swarmxq_skills_integration_upgrade/docs/._CLI_PATCH.md
Skills/swarmxq_skills_integration_upgrade/docs/SKILLS.md
__MACOSX/Skills/swarmxq_skills_integration_upgrade/docs/._SKILLS.md
Skills/swarmxq_skills_integration_upgrade/skills/catalog.yaml
__MACOSX/Skills/swarmxq_skills_integration_upgrade/skills/._catalog.yaml
Skills/files/codebase-zip-audit/SKILL.md
__MACOSX/Skills/files/codebase-zip-audit/._SKILL.md
Skills/SCAR Skills v2/claude-nexus/NEXUS.md
__MACOSX/Skills/SCAR Skills v2/claude-nexus/._NEXUS.md
Skills/SCAR Skills v2/claude-nexus/SETUP_AND_IMPLEMENTATION.md
__MACOSX/Skills/SCAR Skills v2/claude-nexus/._SETUP_AND_IMPLEMENTATION.md
Skills/SCAR Skills v2/claude-nexus/CLAUDE.md
__MACOSX/Skills/SCAR Skills v2/claude-nexus/._CLAUDE.md
Skills/swarmxq_skills_integration_upgrade/src/swarmx/skill_cli.py
__MACOSX/Skills/swarmxq_skills_integration_upgrade/src/swarmx/._skill_cli.py
Skills/swarmxq_skills_integration_upgrade/src/swarmx/skill_loader.py
__MACOSX/Skills/swarmxq_skills_integration_upgrade/src/swarmx/._skill_loader.py
Skills/SCAR Skills v2/skills_new/multi-agent-orchestration-architect/SKILL.md
__MACOSX/Skills/SCAR Skills v2/skills_new/multi-agent-orchestration-architect/._SKILL.md
Skills/SCAR Skills v2/skills_new/real-time-systems-architect/SKILL.md
__MACOSX/Skills/SCAR Skills v2/skills_new/real-time-systems-architect/._SKILL.md
Skills/SCAR Skills v2/skills_new/nigerian-fintech-compliance-architect/SKILL.md
__MACOSX/Skills/SCAR Skills v2/skills_new/nigerian-fintech-compliance-architect/._SKILL.md
Skills/SCAR Skills v2/skills_new/data-visualization-architect/SKILL.md
__MACOSX/Skills/SCAR Skills v2/skills_new/data-visualization-architect/._SKILL.md
Skills/SCAR Skills v2/skills_enhanced/frontend-product-design-architect/SKILL.md
__MACOSX/Skills/SCAR Skills v2/skills_enhanced/frontend-product-design-architect/._SKILL.md
Skills/SCAR Skills v2/skills_enhanced/motion-performance-architect/SKILL.md
__MACOSX/Skills/SCAR Skills v2/skills_enhanced/motion-performance-architect/._SKILL.md
Skills/SCAR Skills v2/skills_enhanced/backend-domain-model-architect/SKILL.md
__MACOSX/Skills/SCAR Skills v2/skills_enhanced/backend-domain-model-architect/._SKILL.md
Skills/SCAR Skills v2/skills_enhanced/accessibility-system-architect/SKILL.md
__MACOSX/Skills/SCAR Skills v2/skills_enhanced/accessibility-system-architect/._SKILL.md
Skills/SCAR Skills v2/skills_enhanced/elite-skill-forge/SKILL.md
__MACOSX/Skills/SCAR Skills v2/skills_enhanced/elite-skill-forge/._SKILL.md
```

</details>

## Canonical skill normalization

The skills archive contained overlapping `.skill`, `.zip`, Markdown, and expanded-directory variants. Cognexus v3.2.0 selects one canonical source per skill, deduplicates by frontmatter `name`, and emits the following portable layout.

| Canonical skill | Selected source | Risk | Category |
|---|---|---:|---|
| `accessibility-system-architect` | `Skills/SCAR Skills v2/skills_enhanced/accessibility-system-architect/SKILL.md` | low | frontend-experience |
| `agent-prompt-upgrade` | `Skills/agent-prompt-upgrade.skill` | low | ai-engineering |
| `ai-feature-architect` | `Skills/ai-feature-architect.skill` | low | ai-engineering |
| `api-automation-architect` | `Skills/api-automation-architect.skill` | medium | backend-platform |
| `backend-domain-model-architect` | `Skills/SCAR Skills v2/skills_enhanced/backend-domain-model-architect/SKILL.md` | medium | backend-platform |
| `backend-systems-auditor` | `Skills/backend-systems-auditor.skill` | medium | backend-platform |
| `bullmq-job-architect` | `Skills/bullmq-job-architect.skill` | medium | backend-platform |
| `codebase-zip-audit` | `Skills/files/codebase-zip-audit/SKILL.md` | medium | developer-tooling |
| `component-quality-gate` | `Skills/component-quality-gate.skill` | low | frontend-experience |
| `data-visualization-architect` | `Skills/SCAR Skills v2/skills_new/data-visualization-architect/SKILL.md` | low | quality-observability |
| `design-token-system-architect` | `Skills/design-token-system-architect.skill` | low | frontend-experience |
| `effect-ts-layer-architect` | `Skills/effect-ts-layer-architect.skill` | medium | backend-platform |
| `elite-skill-forge` | `Skills/SCAR Skills v2/skills_enhanced/elite-skill-forge/SKILL.md` | low | ai-engineering |
| `frontend-design-auditor` | `Skills/frontend-design-auditor.skill` | low | frontend-experience |
| `frontend-product-design-architect` | `Skills/SCAR Skills v2/skills_enhanced/frontend-product-design-architect/SKILL.md` | low | frontend-experience |
| `git-workflow-architect` | `Skills/git-workflow-architect.skill` | high | developer-tooling |
| `motion-interaction-architect` | `Skills/motion-interaction-architect.skill` | low | frontend-experience |
| `motion-performance-architect` | `Skills/SCAR Skills v2/skills_enhanced/motion-performance-architect/SKILL.md` | low | frontend-experience |
| `multi-agent-orchestration-architect` | `Skills/SCAR Skills v2/skills_new/multi-agent-orchestration-architect/SKILL.md` | medium | ai-engineering |
| `nextjs-performance-architect` | `Skills/nextjs-performance-architect.skill` | low | quality-observability |
| `nigerian-fintech-compliance-architect` | `Skills/SCAR Skills v2/skills_new/nigerian-fintech-compliance-architect/SKILL.md` | high | security-compliance |
| `opentelemetry-observability-architect` | `Skills/opentelemetry-observability-architect.skill` | low | quality-observability |
| `portfolio-conviction-engine` | `Skills/portfolio-conviction-engine.skill` | low | frontend-experience |
| `prisma-database-architect` | `Skills/prisma-database-architect.skill` | medium | backend-platform |
| `prompt-engineering-architect` | `Skills/prompt-engineering-architect.skill` | low | ai-engineering |
| `react-native-expo-architect` | `Skills/react-native-expo-architect.skill` | low | mobile |
| `real-time-systems-architect` | `Skills/SCAR Skills v2/skills_new/real-time-systems-architect/SKILL.md` | medium | backend-platform |
| `security-hardening-auditor` | `Skills/security-hardening-auditor.skill` | high | security-compliance |
| `shell-cognitive-os` | `Skills/shell-cognitive-os.skill` | high | developer-tooling |
| `surgical-merge` | `Skills/surgical-merge.skill` | high | developer-tooling |
| `testing-strategy-architect` | `Skills/testing-strategy-architect.skill` | low | quality-observability |
| `typescript-config-surgeon` | `Skills/typescript-config-surgeon.skill` | low | quality-observability |
| `vscode-ai-agent-stack` | `Skills/vscode-ai-agent-stack.skill` | low | ai-engineering |
| `vscode-cognitive-os` | `Skills/vscode-cognitive-os.skill` | low | developer-tooling |
| `vscode-debug-profiler` | `Skills/vscode-debug-profiler.skill` | low | developer-tooling |
| `vscode-monorepo-forge` | `Skills/vscode-monorepo-forge.skill` | low | developer-tooling |

## Files intentionally excluded from the upgraded distribution

- Python bytecode and `__pycache__/` directories from the supplied runtime archive.
- Local SQLite databases, test caches, type-check caches, lint caches, logs, and build output.
- Nested duplicate skill archives after their unique content was normalized into `.agents/skills/`.
- Multiple copies of the same skill where frontmatter names and content overlapped; the selected source is listed above.
