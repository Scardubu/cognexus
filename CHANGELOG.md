# Changelog

All notable changes are documented here. Cognexus follows semantic versioning.

## [3.3.1] - 2026-06-24

### Added

- Cross-platform dependency bootstrap with preflight DNS/HTTPS diagnostics, approved proxy/private-index support, and deterministic offline wheelhouse creation and installation.

- Exact Linux runtime dependency constraints plus a verifier that enforces direct requirement compatibility and CycloneDX component parity.
- Isolated runtime-only SBOM generation across CI and release workflows so development dependencies cannot alter the attested runtime graph.
- Deterministic source repository inventory generation and CI freshness enforcement.
- Deterministic offline CycloneDX 1.6 runtime dependency graph generation.
- First-class `focus`, `review`, `research`, `architect`, `brainstorm`, and `incident`
  execution modes across schemas, prompts, routing, CLI, HTTP, SSE, metrics, and tests.
- Deterministic, mode-aware skill recommendations with confidence, rationale, activation
  suggestion, category, and risk through `/v1/skills/recommend` and run responses.
- Additive response fields for next actions, assumptions, open questions, confidence,
  recommended skills, classification metadata, execution mode, and session intelligence.
- Rolling secret-redacted session summaries, continuity scoring, context optimization,
  and compaction signals through session APIs.
- Evidence-weighted conflict resolution, duplicate recommendation elimination, hybrid intent
  classification, ambiguity reporting, and trusted expert tier override.
- SBOM, signed provenance/SBOM attestation, container scan, release verification, and
  deployment verification workflows and scripts.
- Executable policy validators, policy templates, and operational playbooks for the three
  named completion skills in source and wheel-bundled locations.
- Completed examples and operational reference packs for the three v3.3.0 skills in
  both source and wheel-bundled locations.
- Regression coverage that verifies completed skill resources remain readable and are
  present in source distributions.
- Stable, domain-separated session references for observability and provider trace grouping.

### Changed

- Developer, CI, release, and deployment installs now apply `constraints/runtime.txt`, so tests and local validation exercise the same runtime dependency resolution as release artifacts.
- The development `packaging` range now accepts the certified `packaging==26.2` runtime pin instead of forcing a divergent test environment.

- Docker builds and clean-wheel release verification now use the same exact runtime constraint set as the attested runtime SBOM.
- Mode-aware runtime routing exposes a minimal specialist subset while the historical
  one-argument agent factory and omitted-mode request behavior remain compatible.
- Skill recommendations now prioritize direct skill-name, category, and domain-term evidence;
  tier and execution-mode hints remain deterministic low-confidence fallbacks instead of
  overriding explicit task relevance.
- Structured logs and spans now apply a fail-safe processor that replaces accidental raw
  session identifiers with stable domain-separated references.
- Full quality gates now remove stale `build/` and `dist/` trees before constructing
  release artifacts, preventing verification against leftovers from an earlier version.
- Starlette is now an explicit runtime dependency because Cognexus imports its ASGI
  interfaces directly; `httpx2` is an explicit development-only TestClient backend.
- Live multi-worker deployments require Redis sessions and forbid node-local SQLite
  fallback, including staging environments.

### Fixed

- Prevented package-index DNS/socket failures from being misdiagnosed as a missing `openai-agents` release during Windows setup.
- Made comma-separated list values in `.env.example` load correctly under Pydantic Settings by disabling premature JSON decoding for repository-owned CSV settings.

- Replaced shell-generated release checksums that embedded `dist/` path prefixes with a deterministic repository-owned generator that emits paths relative to the release root and is regression tested.
- Release verification now validates both the top-level artifact checksum set and the nested portable-skill checksum set before accepting a manifest.
- Restored test collection with Starlette 1.x, whose TestClient now uses `httpx2`.
- Prevented raw session identifiers from entering structured logging context, local
  OpenTelemetry attributes, Redis-session failure logs, or OpenAI trace group IDs.
- Closed the staging topology gap that allowed multi-worker SQLite sessions without
  cross-process execution ordering.
- Prevented quoted JSON credentials and user-info passwords embedded in connection URIs
  from surviving privacy-preserving rolling session summaries.
- Prevented generic architecture tier hints from recommending unrelated database or backend
  skills for explicit edge-cache, Next.js, and portfolio tasks.

### Compatibility

- No HTTP route, response schema, console command, import path, or existing environment
  variable was removed or renamed.

## [3.3.0] - 2026-06-24

### Added

- Production-ready `api-contract-governance-architect`,
  `edge-cache-architecture-architect`, and
  `release-incident-operations-architect` skills promoted from the supplemental archive.
- Stable `--version` output for `cognexus`, `cognexus-server`, and `cognexus-skills`.
- Configuration-driven `cognexus-server` launcher with validated host, port, worker,
  trusted-proxy, graceful-shutdown, HTTP-concurrency, and socket-backlog settings.
- Source/tag/container version-parity verifier used by local, CI, release, and Docker gates.
- Regression coverage for dual-header authentication, request-ID normalization,
  readiness secret reporting, CLI metadata, cross-replica session ordering, safe
  deletion semantics, staging fail-closed authentication, shared rate-limit storage,
  proxy trust, server launch options, version parity, and isolated quality-gate execution.

### Changed

- Canonical and wheel-bundled skill packs now contain 39 synchronized skills.
- The local quality gate now invokes Ruff, MyPy, Pytest, and pip-audit through the
  exact Python interpreter that launched the gate, records the application version,
  persists per-check logs, and terminates timed-out process trees.
- Strict MyPy keeps Cognexus-owned code fully checked while treating the extremely
  large OpenAI and Redis SDK type graphs as external integration boundaries.
- Readiness responses now include a non-secret `missing_secrets` list.
- Live Redis deployments now use Redis-backed SlowAPI storage by default, preserving
  rate-limit state across workers and replicas without an in-memory error fallback.
- Deterministic release builds use the audited, explicitly provisioned toolchain with
  `--no-isolation`; release tags and container build arguments must match source version.
- Redis Compose defaults now use `noeviction` so session, lease, and quota keys are not
  silently discarded under memory pressure.

### Fixed

- Authentication now accepts either valid supported credential when both
  `X-API-Key` and bearer headers are present instead of incorrectly prioritizing one.
- Request IDs are validated consistently on normal and early-rejection paths,
  non-ASCII values are rejected without lossy decoding, and duplicate response headers
  are no longer emitted.
- Request logging no longer records raw URL paths that may contain opaque session IDs.
- Redis-backed sessions now use a bounded distributed lease, preserving same-session
  ordering across workers and Kubernetes replicas.
- Session deletion clears the serialized cached backend in place instead of closing a
  handle that already-queued requests may still reference, and now participates in the
  same active-user lifecycle used by queued requests so pruning cannot close it mid-wait.
- The release quality gate no longer depends on an activated virtual environment or
  globally installed developer tools.
- Corrected stale specialist-registry comments and current-release documentation.

### Security

- Removed the unused `httpx2` development dependency, reducing dependency ambiguity
  and unnecessary supply-chain surface while retaining the standard `httpx` client.
- Made the Agents SDK's `mcp>=1.19,<2` runtime dependency explicit and added `pip check`
  to bootstrap, CI, image, quality, and clean-wheel verification paths.
- Protected staging and production endpoints now fail closed when `NEXUS_API_KEY` is
  absent; live settings reject placeholder secrets, reused service/provider keys,
  wildcard forwarded-header trust, and unsafe in-memory rate limits for Redis replicas.
- Hardened request correlation identifiers before they enter headers or structured logs.

### Compatibility

- No HTTP route, response model, Python import, console command, or `NEXUS_*`
  environment-variable contract was removed or renamed.
- Consumers that assert an exact skill count must update from 36 to 39.

## [3.2.1] - 2026-06-24

### Added

- Canonical, composable NEXUS orchestration contract with explicit instruction precedence,
  evidence rules, bounded tool use, conflict resolution, observation-gap codes, and strict
  trace-field semantics.
- Complete portable Agent Skills loading protocol covering metadata discovery,
  `search_skills`, exact-name activation, on-demand resources, composition, script safety,
  failure handling, and accurate trace reporting.
- Prompt contract regression tests, including trace-validator compatibility and catalog
  injection ordering.

### Changed

- Replaced ad-hoc skill instructions in `orchestrator/nexus_agent.py` with the centralized
  `build_nexus_system_prompt()` contract.
- Agent cache keys now include a SHA-256 fingerprint of the rendered skill catalog so skill
  additions, removals, and metadata changes cannot leave stale orchestration instructions.
- The response contract remains the final prompt section after catalog injection to preserve
  instruction recency and deterministic trace compliance.

### Security

- Catalog entries, skills, resources, repository content, and tool output are explicitly
  treated as untrusted data subordinate to system, authorization, and guardrail policy.
- Skill scripts remain review-only and cannot be executed by the loading protocol.
- Skill activation failures and unavailable evidence must be reported rather than fabricated.

## [3.2.0] - 2026-06-23

### Added

- Secure filesystem-backed Agent Skills registry and typed models.
- Three-stage metadata, instruction, and resource progressive disclosure.
- 36 deduplicated, normalized, production-ready skills.
- `search_skills`, `activate_skill`, and `read_skill_resource` agent tools.
- Authenticated `/v1/skills` and `/v1/skills/{skill_name}` endpoints.
- `cognexus` and `cognexus-skills` console commands.
- Skill validation, installation, synchronization, and packaging utilities.
- Wheel-bundled skill assets and source/package fallback.
- Skill runtime and API test suites.
- File inventory, research baseline, skill guide, implementation guide, and upgrade report.

### Changed

- Specialist agent tools now use deferred loading.
- Agent construction uses a bounded cache keyed only by non-secret policy.
- Readiness includes skill subsystem health.
- Product branding is Cognexus while NEXUS API/config compatibility remains intact.
- Container includes the skill runtime and canonical skill pack.

### Fixed

- Added the missing synchronous console entry point expected by `pyproject.toml`.
- Added structured errors for missing/invalid skills.
- Removed duplicate, stale, cache, bytecode, and local database artifacts from the release.

### Security

- Deny traversal, absolute resource paths, symlinked skills/resources, binary context loading, and oversized skill input.
- Skill scripts are never executed by the loader.
- Skill content is explicitly subordinate to system, authorization, guardrail, and approval policy.
- Added streaming request-body limits, authenticated API documentation, exact origin/host validation, and strong distinct production service keys.
- Production Redis sessions now fail closed instead of falling back to node-local SQLite.
- Added no-follow descriptor reads, symlink-component denial, YAML alias denial, and bounded skill metadata.

### Enterprise hardening

- Fixed session-creation lock cleanup and real SQLite readiness probing.
- Scoped model-validation caches to provider credentials, bounded pagination, and cached provider failures briefly.
- Added sanitized SSE error events and graceful OpenTelemetry flushing.
- Made `.skill` archives reproducible with manifests and SHA-256 checksums.
- Added a Makefile, machine-readable quality gate, split CI/security/release workflows, Dependabot, provenance attestations, and clean-wheel verification.
- Added Kubernetes deployment assets, threat model, SLO guidance, security policy, contribution guide, enterprise audit, and release checklist.

## [3.1.0]

See the original release notes in repository history and `docs/migration_checklist.md`.
