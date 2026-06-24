# Executive Summary of Changes

> Historical report for v3.3.0. Superseded for current promotion decisions by [`V3_3_1_PRODUCTION_READINESS_REPORT.md`](V3_3_1_PRODUCTION_READINESS_REPORT.md).

## Version bump suggestion

**Recommended and applied version:** `3.3.0`.

This is a minor release rather than a patch because it adds three canonical skills, new CLI version behavior, new Redis cross-replica coordination, new metrics, new tests, and improved release-gate behavior while preserving existing HTTP, import, command, and `NEXUS_*` contracts.

### Changelog entry snippet

```markdown
## [3.3.0] - 2026-06-24

### Added
- Three canonical enterprise skills: API contract governance, edge-cache architecture,
  and release/incident operations.
- Stable `--version` support for all three console commands, including the new configuration-driven HTTP launcher.
- Cross-replica Redis session serialization, shared rate limits, trusted-proxy validation, release-version parity, and lifecycle regressions.

### Fixed
- Accept either valid supported credential when both API-key and bearer headers exist.
- Validate request IDs consistently on normal and early-rejection paths.
- Preserve same-session ordering across workers and Kubernetes replicas.
- Clear deleted sessions in place so queued work never receives a closed handle.
- Make build, quality-gate, version verification, artifact manifests, and distribution verification deterministic and bounded.

### Security
- Remove the unused `httpx2` development dependency and explicitly declare the Agents SDK MCP runtime dependency.
- Stop raw path logging and reject unsafe/non-ASCII correlation IDs.
- Fail closed in staging/production when service authentication, proxy trust, or distributed limiter configuration is unsafe.
```

## Key wins

- **Correct authentication semantics:** a malformed or stale `X-API-Key` can no longer shadow a valid bearer credential, and vice versa.
- **Safe correlation IDs:** one strict normalization path now covers middleware, early body-limit rejection, response headers, logs, and traces.
- **Cross-replica session correctness:** Redis-backed sessions use a bounded distributed lease in addition to the process-local lock, closing a race present when the supplied Kubernetes deployment runs more than one replica.
- **Deletion race removed:** session deletion clears the serialized backend in place rather than closing a handle already referenced by queued requests.
- **Lower information exposure:** request logs use route templates rather than raw URL paths that can contain session identifiers.
- **Stronger readiness:** `/ready` reports non-secret missing credential names and fails closed when live-run secrets are absent.
- **Supply-chain reduction:** the unused and easily confused `httpx2` development dependency was removed; the standard `httpx` runtime client remains.
- **Deterministic release tooling:** build dependencies are explicitly provisioned, builds use `--no-isolation`, every quality check is bound to the invoking interpreter, per-check logs are retained, and timed-out process trees are terminated.
- **Validated production launcher:** `cognexus-server` now applies the environment-backed host, port, workers, forwarded-header trust, graceful shutdown, HTTP concurrency, and socket backlog settings instead of relying on hand-maintained Uvicorn flags.
- **Shared abuse controls:** live Redis deployments automatically use Redis-backed rate-limit state across workers and replicas, with swallowed storage errors and in-memory fallback disabled.
- **Fail-closed live configuration:** staging and production reject placeholder credentials, reused provider/service keys, wildcard forwarded-header trust, and unsafe process-local limits in a replicated Redis topology.
- **Release parity and evidence:** package, registries, Docker, Compose, and Kubernetes version declarations are verified together; deterministic release manifests record hashes and sizes for all distributable artifacts.
- **Skill consolidation:** the nested supplemental archive was deduplicated instead of copied wholesale; the canonical pack increased from 36 to 39 validated skills.
- **Measured quality increase:** the suite rose from 61 baseline tests at 73.40% branch-aware coverage to 85 passing tests at 76.81% branch-aware coverage.

## Breaking changes / migration notes

No route, response model, Python import, console command, Docker service name, or existing `NEXUS_*` environment variable was removed or renamed.

The following observable changes are intentional:

1. Consumers asserting an exact skill count must update from **36** to **39**.
2. A Redis-backed request for a session already held by another replica can now return `503 session_unavailable` after the configured queue timeout instead of executing concurrently and risking history corruption. Clients should retry with bounded exponential backoff and jitter.
3. Protected staging endpoints now return a sanitized `503` until `NEXUS_API_KEY` is configured; development and test behavior is unchanged.
4. Staging/production Redis deployments reject explicit `memory://` rate-limit storage and wildcard forwarded-header trust.
5. Clearly placeholder or reused OpenAI/service credentials now fail startup validation in live environments.

Operators should also update immutable image tags from `3.2.1` to `3.3.0` and verify the new checksums before promotion.

## Recommended next steps

Run the network-enabled GitHub workflows, deploy to a staging environment with managed Redis and OpenAI credentials, execute load/chaos tests for same-session and unrelated-session traffic, verify dashboards/alerts for lock contention and queue saturation, then rehearse rollback using immutable image digests.

## Overall quality delta

**Elevated from a strong production baseline to a materially safer enterprise platform:** the release closes concrete authentication, request-boundary, distributed-session, deletion-lifecycle, packaging, and observability gaps without an architectural rewrite.

---

# 1. Scope, evidence, and inventory

## 1.1 Inputs reviewed

- `Cognexus-v3.2.1-enterprise-production(2).zip`: complete base release.
- `Cohn 2.zip`: five targeted Python overlays (`server/app.py`, CLI/runtime entry points, specialist metadata, and security regressions).
- `Skills 2(2).zip`: a nested collection containing source skills, packaged skills, historical integration bundles, research documents, and duplicate ZIPs.

The supplemental content was treated as untrusted candidate input. Files were compared by role and content; they were not overlaid blindly. Generated archives, historical SwarmXQ integrations, duplicated distributions, and stale nested ZIPs were excluded from the canonical source tree.

## 1.2 Repository inventory after hardening

- **91 Python files**, approximately **9k Python lines**.
- **18 Python test modules**.
- **39 canonical Agent Skills**, mirrored into the wheel bundle.
- **20 specialist agents** and **14 executable tools** discovered by the offline smoke test.
- **4 GitHub Actions workflows**: CI, security, Docker, and release.
- Dockerfile, Docker Compose, OpenTelemetry Collector configuration, and **10 Kubernetes workload/policy resources** plus namespace/kustomization support.
- FastAPI HTTP, SSE, session, skill, health, readiness, metrics, and authenticated documentation surfaces.

## 1.3 Architecture and control flow

```text
Client
  -> trusted-host/CORS/body-limit/request-context middleware
  -> service-key authentication and shared/process-local rate limiting by environment
  -> Pydantic input validation + deterministic input guardrail
  -> SessionManager
       -> process-local per-session lock
       -> bounded Redis distributed lease when Redis-backed
       -> Redis / AsyncSQLite / explicit stateless backend
  -> bounded RunGate
  -> deterministic tier classification and model routing
  -> cached NEXUS orchestrator + deferred specialists/tools/skills
  -> OpenAI Agents SDK runner
  -> deterministic output, trace, and constraint validation
  -> JSON response or buffered-and-validated SSE delivery
  -> structured logs + Prometheus + OpenTelemetry
```

### Primary component responsibilities

| Boundary | Responsibility |
|---|---|
| `config/` | Immutable environment parsing, cross-field production policy, model/session/runtime limits |
| `server/` | FastAPI application, auth, body limits, request context, error mapping, API routes, SSE |
| `orchestrator/` | Classification, model routing, admission, execution, output validation, CLI |
| `sessions/` | Redis/SQLite adapters, compaction, caching, ordering, fallback policy, lifecycle |
| `nexus_agents/` | Specialist definitions and registry |
| `tools/` | Tool namespaces, handlers, and deferred registry |
| `skill_runtime/` | Safe progressive-disclosure skill loader, validation, packaging, CLI |
| `.agents/skills` | Canonical source-of-truth skill content |
| `observability/` | Structured logging, metrics, traces, and SDK hooks |
| `security/` | Identifier and policy helpers |
| `validators/` and `middleware/` | Deterministic request/output/trace/constraint enforcement |
| `scripts/` | Integrity, smoke, packaging, synchronization, installation, and quality gates |
| `.github/`, `deploy/`, Docker assets | CI/CD, security analysis, artifacts, containers, Kubernetes baseline |

## 1.4 Public contracts preserved

- Package name: `nexus-openai`.
- Product/API title: Cognexus.
- Console commands: `cognexus` and `cognexus-skills` preserved; `cognexus-server` added.
- Python package/module names.
- `/health`, `/ready`, `/metrics`, `/v1/run`, `/v1/run/stream`, skill and session routes.
- NEXUS trace block contract.
- Existing `NEXUS_*`, `OPENAI_*`, `OTEL_*`, and `REDIS_URL` environment names.
- Existing response models and status behavior, except the safer contention behavior described in migration notes.

---

# 2. Multi-lens critique and implemented resolutions

## 2.1 Correctness and reliability

### COG-COR-001 — Credential precedence bug — **Fixed, P0**

**Finding:** authentication selected `X-API-Key` first. When both supported headers were sent, an invalid API key caused rejection even if the bearer token was valid.

**Impact:** legitimate traffic could fail during credential rotation, proxy migration, or mixed-client operation.

**Resolution:** parse both credentials independently and authorize when either one matches the configured service key using constant-time comparison. Invalid schemes and absent credentials still fail closed.

**Verification:** dual-header permutations are covered by regression tests.

### COG-COR-002 — Cross-replica session race — **Fixed, P0**

**Finding:** `SessionHandle.run_lock` serialized requests only inside one Python process. The included Kubernetes deployment runs two replicas, so two requests sharing a session could reach different pods and mutate history concurrently.

**Impact:** non-deterministic message ordering, lost updates, duplicated context, or provider/session inconsistency.

**Resolution:** Redis-backed handles now acquire both the local lock and a Redis lock named under the validated session prefix. The lease covers configured queue wait + request timeout + cleanup margin, waits no longer than `NEXUS_QUEUE_TIMEOUT_SECONDS`, and fails closed on acquisition errors/timeouts. Release is cancellation-shielded. SQLite and stateless local behavior remains unchanged.

**Observability:** added low-cardinality lock wait histogram and outcome counter.

**Verification:** two independent `SessionManager` instances sharing a lock double cannot enter the same session concurrently; timeout behavior fails closed.

### COG-COR-003 — Session deletion/queued-handle race — **Fixed, P0**

**Finding:** deletion cleared a session, removed its cached handle, and closed the backend immediately. A request that had already obtained the handle but was waiting on its lock could then execute against a closed object.

**Resolution:** deletion now clears the session under the same serialization primitive and retains the valid cached handle. Normal TTL/LRU eviction closes it later when no active users exist.

**Trade-off:** a request already queued behind deletion may start a new history after deletion completes. This is deterministic serialized ordering and is preferable to using a closed backend. Product-level cancellation of pending work would require a separate request/job control contract.

### COG-COR-004 — Early-rejection request ID divergence — **Fixed, P1**

**Finding:** the body-limit middleware had a separate, lossy request-ID path and could echo an unvalidated ID before normal middleware ran.

**Resolution:** all paths use the same strict ASCII validator and safe generated fallback. Body-limit state is revalidated rather than trusted.

### COG-COR-005 — Build environment drift — **Fixed, P1**

**Finding:** release builds could create a network-dependent isolated backend environment even after CI installed an audited build toolchain.

**Resolution:** CI, Makefile, and the local gate use `python -m build --no-isolation` after explicit compatible `build`, `setuptools`, and `wheel` provisioning.

### COG-COR-006 — Distribution verifier path dependency — **Fixed, P1**

**Finding:** the distribution verifier imported project modules before bootstrapping the repository root. A clean direct invocation could therefore fail when no editable install or `PYTHONPATH` side effect existed.

**Resolution:** the verifier now inserts its own resolved project root before local imports. A subprocess regression executes it from an unrelated directory with `PYTHONPATH` and pytest-cov child instrumentation removed.

### COG-COR-007 — Session deletion/pruning lifecycle race — **Fixed, P0**

**Finding:** deletion waited for the session lock without being counted as an active handle user. Cache pruning could close the handle while deletion was queued.

**Resolution:** deletion now enters the same `session_scope()` lifecycle as ordinary work, incrementing active users before waiting and clearing the serialized backend in place.

### COG-COR-008 — Release metadata drift — **Fixed, P1**

**Finding:** package, runtime, registry, image, Compose, and Kubernetes versions could diverge, and release artifact metadata was documented but not generated by one canonical tool.

**Resolution:** `scripts/verify_version.py` validates nine release-critical declarations and enforces tag parity. `scripts/create_release_manifest.py` deterministically records SHA-256 hashes and sizes for all release files.

## 2.2 Security and compliance

### COG-SEC-001 — Unsafe correlation data in headers/logs — **Fixed, P0**

Strict length/character validation now precedes storage, logging, and response emission. Non-ASCII bytes are rejected rather than silently normalized. Duplicate request/trace response headers are prevented.

### COG-SEC-002 — Raw path logging — **Fixed, P1**

Middleware now logs the resolved route template instead of the raw URL path. This reduces accidental exposure of opaque session IDs and prevents high-cardinality log fields.

### COG-SEC-003 — Ambiguous unused dependency — **Fixed, P1**

The development manifest referenced `httpx2`, while production uses `httpx`. The unused package was removed, reducing attack surface and reviewer confusion.

### COG-SEC-004 — Secret readiness ambiguity — **Fixed, P1**

Readiness now computes required live-run secrets through the central policy helper and returns only missing variable names—not values. Production can therefore fail closed with actionable diagnostics.

### COG-SEC-005 — Staging authentication fail-open — **Fixed, P0**

Protected routes previously became unauthenticated when the service key was omitted outside production. Staging now fails closed with a sanitized service-unavailable response, making it safe for production-like validation.

### COG-SEC-006 — Proxy trust and placeholder configuration — **Fixed, P0**

Forwarded-header sources are validated as explicit IPs/CIDRs, live wildcard trust is rejected, and staging/production reject placeholder or reused provider/service credentials. The new launcher is the single production entry point that applies these validated controls.

### COG-SEC-007 — Replica-local rate limiting — **Fixed, P0**

Live Redis deployments now share SlowAPI counters through Redis. Limiter storage failures are not swallowed and cannot fall back to per-process memory; startup rejects an explicit `memory://` backend for this topology.

### Existing controls retained

- Strong distinct production service-key checks.
- Constant-time credential comparison.
- Authenticated OpenAPI/Swagger/ReDoc and metrics.
- Exact CORS/trusted-host validation.
- Streaming request byte limits before JSON buffering.
- Skill traversal/symlink/no-follow/size/YAML bounds.
- Sensitive OpenAI tracing disabled by default.
- Non-root, read-only, capability-free container baseline.
- Kubernetes service-account token disabled and runtime-default seccomp.
- CodeQL, dependency review, dependency audit, container scan, provenance, and checksums in remote pipelines.

### Compliance boundary

The repository provides secure engineering controls; it does **not** by itself provide tenant identity, legal retention policy, regional residency, consent, DLP, or regulatory certification. Those remain product/organization responsibilities.

## 2.3 Performance and scalability

### Improvements

- Distributed locking is **per session**, so unrelated sessions remain parallel.
- Lock waiting is bounded and measured; contention cannot consume a global run slot because session ordering occurs before `RunGate` admission.
- Existing bounded global concurrency, queue timeout, shared async client, cached agents/tools, bounded Redis pool, and session TTL/LRU cache remain intact.
- Route-template telemetry avoids high-cardinality metric/log growth.
- Strict MyPy no longer recursively analyzes enormous third-party SDK graphs, reducing developer/CI latency while keeping all Cognexus-owned files strict.

### Residual scalability considerations

- IP-based application rate limits are shared through Redis in live replicated deployments; authenticated organization/user quotas and provider budgets still require an identity-aware edge or quota service.
- A hot session is intentionally serial. Clients should use separate sessions for independent work.
- Redis lock leases do not renew; safety relies on the configured bounded queue + request timeout and a 30-second margin. Any future unbounded background job model must introduce renewable leases/fencing tokens.
- Provider-wide budgets across replicas require an external quota/budget control plane.

## 2.4 Observability

### Added or improved

- `nexus_session_lock_wait_seconds` histogram.
- `nexus_session_lock_events_total{event=...}` counter with bounded labels.
- Consistent validated `X-Request-ID`/`X-Trace-ID` behavior.
- Readiness `missing_secrets` diagnostics without secret values.
- Per-check release logs and machine-readable version-aware reports.
- Route-template rather than raw-path request logging.

### Alert recommendations

- Lock timeout/error rate > 1% over 5 minutes.
- p95 session-lock wait above the expected interactive budget.
- Run queue timeout or capacity-exhausted rate above baseline.
- `/ready` unavailable for two probe windows.
- Redis fallback event in any production deployment (should be impossible under validated config).
- Model validation missing/error status.
- 5xx/SSE error-event rate and latency SLO burn.

## 2.5 Maintainability and developer experience

- CLI version metadata now matches package/application metadata across all three entry points.
- Three high-value supplemental skill drafts were normalized into the same canonical/bundled/catalog workflow as existing skills.
- Quality tooling always uses `sys.executable`, removing activated-environment ambiguity.
- Per-check logs make release failures diagnosable without rerunning every gate.
- Third-party OpenAI/Redis typing is treated as a documented integration boundary; owned code remains strict.
- New tests isolate auth, identifier, CLI, quality-gate, distributed-lock, and deletion behavior.
- Script helpers are importable in tests, while direct release scripts bootstrap their own source root so they do not depend on shell state or editable installs.

### Residual maintainability debt

- Several adapter/compatibility modules intentionally have little direct coverage.
- `tools/_handlers.py`, conflict-resolution compatibility code, and CLI branches should receive focused tests next.
- Dependency versions are constrained but not fully hash-locked. Generate reviewed, platform-aware lock/constraints files for fully reproducible installation.

## 2.6 Operations and deployability

### Improvements

- Version synchronized to `3.3.0` and automatically checked across nine package/runtime/registry/container/deployment declarations, with tag parity enforced in release and Docker workflows.
- Release build uses the provisioned toolchain, verifies extracted-wheel import origin and three console entry points, and generates a deterministic integrity manifest.
- Quality checks have bounded child-process lifetimes.
- Redis coordination now matches the multi-replica Kubernetes topology.
- Readiness exposes actionable missing-secret state.

### Operator-owned substitutions still required

- Replace `ghcr.io/OWNER/REPOSITORY:3.3.0` through Kustomize/Helm/GitOps with the immutable promoted digest.
- Supply External Secrets/CSI/Vault integration.
- Configure ingress, TLS, DNS, WAF/gateway identity, and egress policy.
- Point to managed Redis with TLS/authentication and tested failover.
- Set organization-specific resource limits from load tests rather than defaults.

## 2.7 Future-proofing

- The canonical/bundled/catalog skill invariant is validated and fingerprinted.
- New skills can be added without changing runtime code.
- The distributed session boundary is backend-specific and does not contaminate orchestration logic.
- Existing package/API/env compatibility allows rolling deployment.
- Python 3.11–3.14 metadata remains, with CI currently exercising 3.11 and 3.13.
- OpenAI/Redis integration boundaries are explicit, making future SDK upgrades easier to review.

---

# 3. Prioritized implementation summary

## Priority 1 — Bugs, security, correctness

1. Fixed dual-header authentication.
2. Centralized and hardened request IDs.
3. Removed raw path logging and duplicate response IDs.
4. Added Redis cross-replica session serialization.
5. Fixed session deletion/queued-handle and pruning lifecycle.
6. Made staging authentication fail closed.
7. Added trusted-proxy, placeholder-secret, and distinct-credential validation.
8. Added shared Redis-backed live rate limiting without fail-open fallback.
9. Added secret-aware readiness.
10. Removed unused ambiguous dependency and declared the required MCP runtime boundary explicitly.

## Priority 2 — Performance, reliability, observability

1. Added lock wait/outcome metrics.
2. Kept lock scope per session and ahead of global admission.
3. Added bounded server concurrency, backlog, graceful shutdown, and validated proxy trust.
4. Added shared Redis limiter state for workers/replicas.
5. Added bounded process-tree timeouts to release checks.
6. Preserved bounded pools, caches, queueing, and output limits.

## Priority 3 — Quality, maintainability, testability

1. Added CLI/server/version/manifest/quality/security/session regressions.
2. Kept strict MyPy practical through documented integration-boundary overrides.
3. Made scripts self-bootstrapping and quality commands interpreter-stable.
4. Added version parity and deterministic release-manifest tooling.
5. Updated all release metadata and operational docs.

## Priority 4 — Creative, low-risk upgrades

1. Promoted three supplemental drafts into production-grade canonical skills.
2. Extended the skill catalog/package to 39 deterministic archives.
3. Added version-aware release evidence and per-check diagnostics.

---

# 4. Supplemental archive merge decisions

## Cohn 2

All five overlays were evaluated semantically:

- `app (1).py` → selected readiness-secret behavior merged into `server/app.py`.
- `run.py` → CLI `--version` merged into `orchestrator/run.py`.
- `cli.py` → CLI `--version` merged into `skill_runtime/cli.py`.
- `specialists.py` → corrected registry comments merged without changing specialist behavior.
- `test_security_hardening.py` → useful regressions merged and expanded.

The overlays were not copied verbatim where the base had newer or more complete logic.

## Skills 2

The archive mixed canonical sources, packaged `.skill` files, research, nested release ZIPs, and integrations for other projects. Duplicate packaged content was collapsed to the existing 36 canonical skills. Three non-duplicate, high-value drafts referenced by the supplied material were promoted:

- `api-contract-governance-architect`
- `edge-cache-architecture-architect`
- `release-incident-operations-architect`

They were added to `.agents/skills`, synchronized into `skill_runtime/bundled_skills`, cataloged with hashes, validated, and packaged reproducibly. Historical ZIPs and unrelated SwarmXQ assets were deliberately excluded.

---

# 5. Validation matrix

| Validation | Outcome |
|---|---|
| Compile/import checks | Passed |
| Ruff lint | Passed |
| Ruff formatting | 91/91 files formatted |
| Strict MyPy | 91/91 source files passed |
| Pytest | 85 passed |
| Branch-aware coverage | 76.81%; floor 70% |
| Repository integrity | 39 skills synchronized |
| Skill validation | 0 errors, 0 warnings |
| Offline smoke | 20 agents, 14 tools |
| Distribution build | Wheel + sdist built |
| Distribution verification | Version, three entry points, wheel origin, skills, API title, and direct-script bootstrap passed |
| Source distribution | 453 files verified |
| Skill packaging | 39 deterministic archives with per-package checksums |
| Release manifest | 44 release files hashed with sizes and SHA-256 metadata |
| YAML parsing | 20 manifests passed |
| Dependency vulnerability audit | Not completed; sandbox DNS unavailable |
| Live OpenAI | Not run; no production credential supplied |
| Live Redis/cluster | Not run; unit regression uses shared lock double |
| Docker daemon/Kubernetes cluster | Not available in review environment |

---

# 6. Trade-offs and risks

- **Fail closed vs availability:** Redis lock acquisition failure returns 503 rather than risking concurrent history mutation.
- **Lease duration:** the lease spans configured queue + request timeout + margin. A crashed holder can delay that session until expiry, but cannot hold it forever.
- **In-place deletion:** protects queued handles. It does not cancel already accepted work; cancellation requires a new product contract.
- **Build isolation:** `--no-isolation` improves reproducibility only because CI explicitly installs and audits compatible build tools first.
- **MyPy integration boundaries:** skipping dependency internals avoids rechecking third-party graphs; runtime contracts are protected through typed local adapters and tests.
- **Static API key:** appropriate for a private service-to-service boundary, not a public multi-tenant identity system.
- **Shared Redis dependency:** live session locking and rate limits deliberately fail closed when Redis is unavailable; highly available Redis is therefore part of the service SLO.

---

# 7. Deployment and rollback verification

## Pre-deployment

1. Run all GitHub required checks with network access.
2. Require successful `pip-audit`, dependency review, CodeQL, container scan, and provenance.
3. Build once; promote the same immutable digest through environments.
4. Verify `dist/SHA256SUMS`, `dist/skills/SHA256SUMS`, and `dist/RELEASE_MANIFEST.json`.
5. Configure production Redis with TLS/authentication and `noeviction`; confirm SQLite/stateless fallback and process-local rate limits are disabled.
6. Set strong distinct service/OpenAI credentials in a secret manager.
7. Replace repository/image placeholders and pin the promoted digest.

## Staging tests

- Same session from multiple replicas remains serialized.
- Different sessions execute concurrently up to configured admission.
- Lock timeout returns sanitized 503 and increments contention metrics.
- Redis restart/failover makes readiness fail closed and recovers cleanly.
- Session delete followed by queued/new request behaves deterministically.
- SSE emits only validated output and sanitized error events.
- Request IDs are generated for invalid/non-ASCII inputs and are never duplicated.
- Every replica uses the same Redis limiter and returns consistent counters.
- Forwarded client IPs are accepted only from the configured ingress source CIDRs.
- `cognexus-server` honors host, port, workers, graceful shutdown, concurrency, and backlog settings.

## Rollback

Redeploy the previous immutable image digest and previous configuration. No database migration or route rollback is required. Do not re-enable production SQLite fallback or weak/reused credentials as a rollback shortcut.

---

# 8. Recommended v3.4 roadmap

1. Identity-aware gateway/JWT validation, tenant context, and authorization policy.
2. Fencing-token or renewable-lock design if runs become unbounded/background jobs.
3. Tenant-aware quota/budget service for authenticated principals and provider calls across replicas.
4. Hash-locked dependency constraints generated and reviewed per supported Python line.
5. Staging OpenAI/Redis integration suite with strict spend and isolation controls.
6. Targeted coverage for tool handlers, CLI failure paths, compatibility modules, and conflict resolution.
7. Load, soak, cancellation, and Redis chaos scenarios wired into release qualification.
8. Signed SBOM and organization-specific SLSA/provenance policy enforcement.
