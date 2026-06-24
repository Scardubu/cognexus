# Cognexus v3.2.0 Upgrade Report

## Executive summary

The supplied Cognexus v3.1.0 runtime was already a strong Python/OpenAI Agents SDK baseline: its original 41-test suite passed, Ruff reported no findings, and strict mypy passed before modification. The supplied skills collection, however, was fragmented across expanded directories, `.skill` packages, nested ZIP files, and standalone Markdown documents. Many skill bodies were several hundred lines long and were being treated as always-available prompt content rather than as a discoverable, progressively disclosed capability layer.

Version 3.2.0 preserves the public Python package name (`nexus-openai`), API paths, NEXUS trace format, and `NEXUS_*` environment namespace while adding a production Agent Skills subsystem. This is a minor release rather than a patch because it adds authenticated skill APIs, command-line management, a secure filesystem loader, installable skill assets, and lazy orchestration tools.

## Input assessment

### Runtime archive

The runtime archive contained the FastAPI service, OpenAI Agents SDK orchestration, 20 specialist agents, sessions, deterministic guardrails, observability, deployment files, and tests. It also contained development artifacts such as Python bytecode and caches; those are excluded from the upgraded distribution.

Confirmed baseline before the upgrade:

- 41 tests passed.
- Ruff passed.
- strict mypy passed.
- Specialist agents were exported as tools, but their schemas were eager by default.
- The runtime had no filesystem-backed Agent Skills discovery, activation, resource loading, validation, packaging, or catalog API.
- The console-script target expected a synchronous `main()` that did not exist.
- The production container did not copy any future skill runtime or skill assets.

### Skills archive

The skills archive contained 149 direct files, including 56 `.skill` packages, 17 nested ZIP archives, 53 Markdown documents, scripts, registries, and research reports. After expanding supported packages and deduplicating by YAML frontmatter `name`, 36 canonical skills remained.

Primary findings:

| Finding | Impact | Resolution |
|---|---|---|
| Multiple copies and packaging formats | Drift and non-deterministic source selection | Deterministic precedence and one canonical catalog |
| Large monolithic `SKILL.md` files | High context cost and weak progressive disclosure | Compact activation contract plus on-demand references/checklists/examples |
| Inconsistent descriptions and trigger prose | Poor discovery and false activation | Complete, bounded capability-and-trigger descriptions |
| No automated spec validation | Invalid frontmatter or duplicates could ship | Secure loader, CLI validator, repository integrity gate, tests |
| No traversal/symlink/size controls | Untrusted skill bundles could escape roots or exhaust context | Root containment, symlink denial, UTF-8 and size limits, approved resource roots |
| Script guidance mixed with instructions | Accidental execution risk | Scripts are inventory-only and never executed by the skill loader |
| No installation/packaging path | Skills worked only in their source location | `.skill` packaging CLI, cross-client installer, bundled wheel assets |
| No runtime integration | Skills could not be discovered or activated by Cognexus | Metadata catalog, search/activate/read tools, authenticated APIs |

## Architecture decisions

### 1. Preserve compatibility

The codebase keeps:

- package name `nexus-openai`;
- import namespaces such as `orchestrator`, `server`, and `nexus_agents`;
- `NEXUS_*` environment variables;
- `/v1/run`, `/v1/run/stream`, session APIs, and the NEXUS trace block;
- existing specialist names and routing policy.

The user-facing product and service name is Cognexus. New console commands are `cognexus` and `cognexus-skills`.

### 2. Use three-stage disclosure

1. **Discovery:** only `name`, `description`, category, and risk are placed in the orchestrator catalog.
2. **Activation:** `activate_skill` returns the compact `SKILL.md` body and a resource inventory.
3. **Resource loading:** `read_skill_resource` returns one bounded text resource explicitly requested by path.

The model never receives all 36 detailed playbooks at startup.

### 3. Treat skills as untrusted data

Skill text can guide work but cannot elevate permissions, override system policy, bypass guardrails, or authorize external/destructive actions. The runtime does not execute bundled scripts. Resource paths are confined to `references/`, `examples/`, `assets/`, and `scripts/`, with traversal and symlink defenses.

### 4. Keep agents and skills distinct

A skill is a lightweight, on-demand behavior and knowledge package. A specialist agent is a context-isolated delegate with its own prompt and model execution. Cognexus uses both:

- skills for reusable process/domain guidance;
- specialist tools for complex delegated reasoning;
- deterministic Python for validation, state, limits, and security.

### 5. Defer large tool surfaces

All 20 specialist agent tools and the resource reader are marked for deferred loading. `ToolSearchTool` remains the runtime mechanism for Responses-compatible tool discovery. `search_skills` and `activate_skill` stay immediately visible because they are the small control plane for skill disclosure.

## Major file changes

### New runtime subsystem

- `skill_runtime/models.py` — immutable Pydantic models for metadata, documents, resources, findings, and search results.
- `skill_runtime/security.py` — path containment, name validation, approved roots, text type policy, and file-size checks.
- `skill_runtime/loader.py` — cached discovery, YAML parsing, validation, search, activation, resource inventory, and bounded reading.
- `skill_runtime/tools.py` — OpenAI Agents SDK discovery/activation/resource tools.
- `skill_runtime/catalog.py` — settings-keyed process registry cache.
- `skill_runtime/cli.py` — list, validate, search, show, and package commands.
- `skill_runtime/bundled_skills/` — wheel-installable copy of the canonical skill pack.

### New canonical skill pack

- `.agents/skills/<name>/SKILL.md` — compact activation contract.
- `.agents/skills/<name>/references/guidance.md` — detailed supplied domain guidance.
- `.agents/skills/<name>/references/checklist.md` — deterministic quality gate and source topic map.
- `.agents/skills/<name>/examples/usage.md` — activation, composition, and output examples.
- `skills/catalog.yaml` — versioned, hashed canonical catalog with source provenance.

### New tooling and tests

- `scripts/validate_repository.py` — validates catalog hashes, bundle parity, progressive-disclosure limits, and skill integrity.
- `scripts/sync_skill_pack.py` — synchronizes source and wheel-bundled skill trees.
- `scripts/install_skills.py` — collision-safe installation into filesystem-based clients.
- `tests/test_skill_runtime.py` — discovery, activation, filters, traversal, binary denial, and tool integration.
- `tests/test_skill_api.py` — skill catalog/detail and structured error behavior.

### Updated production integration

- `orchestrator/nexus_agent.py` — bounded non-secret agent cache, skill catalog instructions, skill tools, and lazy specialist use.
- `nexus_agents/registry.py` — specialist tools use deferred loading.
- `config/settings.py` — portable skill configuration and source/package fallback.
- `server/app.py`, `server/dependencies.py`, `server/schemas.py`, `server/errors.py` — readiness and authenticated skill endpoints with structured errors.
- `orchestrator/run.py` — valid console entry point.
- `Dockerfile` — copies runtime and skill assets and uses Cognexus 3.2 labels.
- `pyproject.toml`, `MANIFEST.in` — includes the runtime and bundled skills in distributions.
- `.github/workflows/ci.yml`, `scripts/setup.sh` — run skill integrity gates.

## Assumptions and boundaries

- Detailed guidance imported from the supplied skills is preserved as source material, not treated as automatically current fact. Version-sensitive technical, legal, regulatory, pricing, and platform claims must be verified before use.
- `allowed-tools` is parsed for interoperability but does not grant permission. Execution authorization remains an application policy concern.
- The runtime deliberately does not execute files from skill `scripts/`; execution should occur through reviewed, allowlisted tools with approval controls.
- The 36 selected skills are the canonical set for this release. Nested archives may contain historical or alternate copies that are listed in `FILE_INVENTORY.md` but are not shipped twice.

## Release classification

`3.1.0 -> 3.2.0` is a backward-compatible minor upgrade:

- existing API paths and environment names remain valid;
- new endpoints and tools are additive;
- source installs gain skills automatically;
- wheel installs use `skill_runtime/bundled_skills` automatically;
- skills can be disabled with `NEXUS_SKILLS_ENABLED=false`.
