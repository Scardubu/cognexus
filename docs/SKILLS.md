# Portable Agent Skills

## Purpose

Cognexus ships 39 filesystem-based Agent Skills. They add reusable domain workflows without injecting every playbook into every model call. The runtime uses skills as untrusted instructional context; authorization, validation, tool policy, and execution remain controlled by Python code and the OpenAI Agents SDK.

## Canonical layout

```text
.agents/skills/
└── <skill-name>/
    ├── SKILL.md
    ├── references/
    │   ├── guidance.md
    │   └── checklist.md
    └── examples/
        └── usage.md
```

`skill_runtime/bundled_skills/` is a byte-identical package-data copy used when Cognexus is installed from a wheel. Do not edit it directly. Edit `.agents/skills/`, then run:

```bash
python scripts/sync_skill_pack.py
python scripts/validate_repository.py
```

## Runtime lifecycle

### Discovery

`SkillRegistry.metadata()` parses only YAML frontmatter and publishes:

- `name`;
- `description`;
- category and risk metadata;
- source paths used internally by the loader.

The orchestrator receives a bounded XML catalog. The REST catalog endpoint also exposes only discovery metadata.

### Search

`search_skills(query, limit)` performs deterministic token-overlap ranking. It is a discovery aid, not an embedding service, and has no network dependency.

### Activation

`activate_skill(name)` loads the core `SKILL.md` body and returns an inventory of resources. It does not read those resources automatically.

### Resource loading

`read_skill_resource(name, relative_path)` reads one approved UTF-8 text file. The path must remain under the skill and begin with `references/`, `examples/`, `assets/`, or `scripts/`. The loader never executes it.

## Orchestrator enforcement contract

`orchestrator/nexus_prompt.py` is the canonical runtime policy for skill use. It enforces this sequence:

1. inspect the metadata-only catalog;
2. call `search_skills` only when the exact match is unclear;
3. select the smallest non-overlapping set;
4. call `activate_skill` before following a skill;
5. load only explicitly listed resources with `read_skill_resource`;
6. compose activated guidance with repository evidence and higher-priority policy;
7. report only successfully activated skills and actually used tools in the trace block.

Search results never activate a skill. Resource files are not loaded automatically, and scripts remain review-only text. Skill activation failures must be surfaced as observation gaps rather than silently ignored or fabricated.

The orchestrator prompt is assembled with `build_nexus_system_prompt()`. The response contract is appended after the live catalog so the exact trace requirement remains the last operational instruction. Agent cache keys include a SHA-256 fingerprint of the rendered catalog, preventing skill additions, removals, or metadata changes from leaving stale prompt instructions after the registry refresh interval.

## Security controls

- lowercase kebab-case names, maximum 64 characters;
- directory name must match frontmatter name;
- safe YAML parsing;
- unknown frontmatter keys produce validation findings;
- source-root containment after path resolution;
- skill and resource symlinks denied;
- absolute paths and `..` traversal denied;
- bounded file bytes and activation characters;
- UTF-8 text requirement;
- binary resources cannot be returned as model context;
- allow and deny lists;
- no implicit script execution;
- skill text cannot override system, safety, approval, or architecture policy.

## Configuration

| Variable | Default | Purpose |
|---|---:|---|
| `NEXUS_SKILLS_ENABLED` | `true` | Enable runtime discovery and tools |
| `NEXUS_SKILLS_PATH` | source or bundled pack | Override skill root |
| `NEXUS_SKILL_MAX_FILE_BYTES` | `256000` | Maximum `SKILL.md` bytes |
| `NEXUS_SKILL_MAX_RESOURCE_BYTES` | `1000000` | Maximum readable resource bytes |
| `NEXUS_SKILL_ACTIVATION_MAX_CHARS` | `40000` | Maximum activated body characters |
| `NEXUS_SKILL_CATALOG_MAX_CHARS` | `24000` | Maximum catalog injected into instructions |
| `NEXUS_SKILL_CACHE_TTL_SECONDS` | `60` | Metadata refresh interval |
| `NEXUS_SKILL_ALLOWED_NAMES` | empty | Optional comma-separated allowlist |
| `NEXUS_SKILL_DENIED_NAMES` | empty | Optional comma-separated denylist |

A name cannot appear in both lists.

## CLI

```bash
# Metadata
cognexus-skills list

# Full deterministic validation
cognexus-skills validate
cognexus-skills validate --json

# Discovery and activation
cognexus-skills search "secure API deployment"
cognexus-skills show security-hardening-auditor

# Build one .skill archive per canonical skill
cognexus-skills package --output dist/skills
```

Use `--root /path/to/skills` before the subcommand to inspect another pack.

## REST API

Both endpoints follow the normal API-key policy:

```text
GET /v1/skills
GET /v1/skills/{skill_name}
```

The detail endpoint deliberately omits the instruction body. It exposes metadata, fingerprint, and resource inventory for governance and UI discovery without turning the service into an unrestricted prompt-export endpoint.

## Install into another client

The installer copies validated skills and refuses collisions unless `--force` is explicit:

```bash
# Preview all skills
python scripts/install_skills.py --target .claude/skills --dry-run

# Install selected skills
python scripts/install_skills.py \
  --target .claude/skills \
  --skill testing-strategy-architect \
  --skill security-hardening-auditor

# Replace same-name copies after review
python scripts/install_skills.py --target .agents/skills --force
```

Use the target directory documented by the receiving agent client. Cognexus does not assume every vendor uses the same discovery path.

## Add a skill

1. Create `.agents/skills/<name>/SKILL.md`.
2. Use lowercase kebab-case for the folder and `name`.
3. Write a description that says what the skill does and when it should activate.
4. Keep the body focused on the operating contract and workflow.
5. Put detailed or version-specific material in `references/`.
6. Put short activation/output examples in `examples/`.
7. Do not grant execution authority in frontmatter or prose.
8. Add risk and category metadata:

```yaml
---
name: example-skill
description: Does X. Use when a task involves Y or Z, even when the skill name is not mentioned.
license: MIT
compatibility: Portable Agent Skills format; Cognexus 3.2+.
metadata:
  cognexus.version: 3.2.0
  cognexus.category: architecture
  cognexus.risk: medium
  cognexus.progressive_disclosure: "true"
---
```

9. Update `skills/catalog.yaml` and its SHA-256 entry. The canonical generator used for this migration is not required at runtime; future changes can be made directly or automated in your release process.
10. Synchronize and validate:

```bash
python scripts/sync_skill_pack.py
python scripts/validate_repository.py
python -m skill_runtime.cli validate
pytest tests/test_skill_runtime.py tests/test_skill_api.py
```

## Composition policy

Activate the smallest set that covers the task. A common sequence is:

1. domain skill;
2. `testing-strategy-architect` for verification;
3. `security-hardening-auditor` for sensitive boundaries;
4. `opentelemetry-observability-architect` before production rollout.

Avoid activating near-duplicate skills “just in case.” More context can reduce rather than improve routing and output quality.

## Maintenance

For each release:

- retest descriptions with positive and negative trigger prompts;
- verify time-sensitive statements in references;
- remove deprecated guidance instead of appending contradictions;
- update version metadata and catalog hashes;
- run the full quality gate;
- package `.skill` artifacts and scan them before publication;
- record additions, removals, and behavior changes in `CHANGELOG.md`.
