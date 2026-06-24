# Cognexus v3.3.1 Enterprise Validation Report

**Validation date:** 2026-06-24  
**Validation environment:** Linux, Python 3.13.5  
**Release status:** deterministic repository-local gates passed; environment-dependent promotion gates remain mandatory

## Verified local results

| Gate | Result |
|---|---:|
| Ruff lint | Passed |
| Ruff format check | Passed across **110 Python files** |
| Strict MyPy | Passed across **107 source files** |
| Python bytecode compilation | Passed |
| Pytest collection and execution | **109 passed** |
| Branch-aware coverage | **79.56%**; enforced floor: 70% |
| `python -m pip check` | Passed; no broken installed requirements |
| Version parity | **9** synchronized release-critical declarations at `3.3.1` |
| Repository source inventory | Deterministic manifest generated and verified |
| Canonical/bundled skill integrity | **39** synchronized portable skills |
| Skill validation | **0 errors, 0 warnings** |
| Completed skill resources | **20** required operational resources verified in the source distribution |
| Static deployment controls | Passed: non-root, healthcheck, read-only filesystem, immutable image tag, probes, resource bounds, restricted context, fail-closed production state |
| Offline runtime smoke | Passed; **20 agents** and **14 executable tools** discovered |
| Wheel/source distribution build | Passed with the provisioned toolchain and `--no-isolation` |
| Distribution verification | Passed from an extracted wheel and inspected source archive |
| Console entry points | `cognexus`, `cognexus-server`, and `cognexus-skills` present |
| Bundled wheel skills | **39** discovered and valid |
| Source distribution | **509 files**; required paths present and generated/unsafe entries absent |
| Runtime CycloneDX SBOM | **70 components**, **71 dependency records**, deterministic serial number |
| Release checksums | **43** artifact entries verified |
| Release manifest | **45** entries with size and SHA-256 integrity verified |
| Release archive safety | Passed: no duplicate, linked, absolute, or traversal paths |
| Raw session observability protection | Passed through log/span privacy processor tests and static regression checks |

Evidence is retained under `artifacts/finalization/`, including the branch-coverage XML,
quality logs, repository validation output, dependency-audit failure evidence, and final
artifact verification summary. Release artifacts and their manifest are under `dist/`.

## Functional coverage added in this finalization

The passing suite now verifies:

- six execution modes and bounded specialist policies;
- hybrid/ambiguous task classification and trusted expert override;
- confidence/source-quality conflict weighting, deterministic ties, and deduplication;
- deterministic mode-aware skill recommendations and additive response metadata;
- secret-redacted rolling session summaries and continuity scoring;
- raw session-ID replacement in structured logs and span attributes;
- backward-compatible HTTP run payloads and new recommendation/intelligence endpoints;
- completed policy assets and executable validators for the three named skills;
- exact runtime locking, isolated deterministic SBOM generation, and development-dependency exclusion;
- deterministic relative checksum generation plus top-level and nested skill checksum verification;
- static Docker/Kubernetes deployment controls;
- current repository-inventory enforcement;
- version, source-distribution, and historical agent-factory compatibility.

## Dependency and security audit boundary

The installed declared dependency set is internally consistent: `pip check` passed and the
runtime dependency closure was captured in the CycloneDX SBOM. A network-backed
`pip-audit -r constraints/runtime.txt` was attempted twice, but the execution environment could
not resolve `pypi.org`. The audit therefore remains **inconclusive**, not passed and not a
finding of zero vulnerabilities. The captured traceback and nonzero exit code are retained
under `artifacts/finalization/`.

Docker, `kubectl`, Syft, and Trivy were not installed in the local execution environment.
The repository now contains CI gates for dependency audit, CodeQL/dependency review,
container build and high/critical vulnerability scanning, source/runtime SBOM generation,
and signed GitHub artifact attestations. Those remote gates must complete successfully on
the actual repository and registry before promotion.

## Environment-dependent validation still required

1. Network-enabled dependency audit and review with accepted-risk policy and current vulnerability databases.
2. GitHub release workflow execution, provenance/SBOM attestation verification, and immutable registry artifact confirmation.
3. Live OpenAI execution, model-catalog validation, spend controls, timeout/retry behavior, and provider-failure handling.
4. Managed Redis TLS/authentication, `noeviction`, failover, latency, backup/restore, distributed lease behavior, and shared limiter consistency.
5. Container build/run validation on every target CPU architecture and target-registry Trivy scan.
6. Kubernetes admission, secrets integration, ingress proxy trust, network policy, HPA, PDB, and rolling termination validation in the target cluster.
7. Representative load, soak, cancellation, abuse, dependency-failure, and chaos tests against documented SLOs.
8. Rollback rehearsal with the actual deployment controller and production-compatible data/state restoration procedures.
9. Organization-specific identity, tenant authorization, retention, privacy, legal, and compliance review.

## Promotion rule

Promote only an immutable artifact whose version, release manifest, checksums, SBOMs, and
attestations agree and whose remote security, staging integration, load/chaos, and rollback
gates are successful. A repository score is not a substitute for target-environment
evidence.
