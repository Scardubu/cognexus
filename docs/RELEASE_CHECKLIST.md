# Release Checklist

## Source and compatibility

- [ ] `python scripts/verify_version.py --expected <release-version>` passes and the Git tag, package, image tag, manifests, changelog, and documentation agree.
- [ ] `/v1/*`, console commands, and `NEXUS_*` compatibility are reviewed.
- [ ] Database/session changes include rollback and mixed-version behavior.
- [ ] New tools and skills have strict schemas, bounds, and least-privilege scope.

## Deterministic quality gate

```bash
make quality
make audit
```

- [ ] A clean dependency installation completes and `python -m pip check` passes.
- [ ] `python scripts/verify_runtime_lock.py` proves direct-range and exact-lock consistency.
- [ ] Ruff lint and formatting checks pass.
- [ ] Strict mypy passes.
- [ ] Tests and branch coverage pass on Python 3.11 and 3.13 in CI.
- [ ] Repository and skill validation report zero errors.
- [ ] Offline smoke test passes.
- [ ] Wheel and source distribution build successfully with the provisioned toolchain and `python -m build --no-isolation`.
- [ ] Wheel installs and validates in a clean environment.
- [ ] Skill archives reproduce byte-for-byte and `SHA256SUMS` is present.

## Security and supply chain

- [ ] Dependency audit, CodeQL, and dependency review pass or approved exceptions exist.
- [ ] No credentials, local databases, logs, caches, or sensitive fixtures are included.
- [ ] GitHub Actions and container bases are pinned according to repository policy.
- [ ] Artifact checksums and provenance attestations are generated.
- [ ] Final container image is scanned after build.
- [ ] Production secrets are sourced from a managed secret store.

## Staging

- [ ] `/health`, `/ready`, `/metrics`, authenticated run, stream, skill, inspect, and delete paths pass.
- [ ] Invalid authentication, oversized body, invalid session ID, queue timeout, and output rejection paths pass.
- [ ] Redis connectivity, TLS, authentication, `noeviction`, persistence, and restore are verified.
- [ ] All replicas share one Redis-backed limiter; counters are consistent and storage failures fail closed.
- [ ] Forwarded client headers are honored only from the exact configured ingress/proxy source CIDRs.
- [ ] Key rotation is tested without leaking credentials.
- [ ] Traces and metrics arrive without prompt or output content.
- [ ] Load test stays within CPU, memory, queue, latency, and provider-budget targets.

## Deployment and rollback

- [ ] The exact staging image digest is promoted; it is not rebuilt for production.
- [ ] Rolling deployment preserves minimum availability and the configured graceful-shutdown window fits the platform termination grace period.
- [ ] HPA, disruption budget, network policy, probes, and termination grace are active.
- [ ] Dashboards and alerts are healthy before traffic migration.
- [ ] Previous image digest and rollback command are recorded.
- [ ] Post-deployment checks and an observation window complete successfully.

## Evidence

Record the release tag, source SHA, image digest, artifact checksums, quality report, dependency audit, approver, deployment time, and rollback digest in the release record.

## v3.3.1 enterprise finalization gates

- [ ] `python scripts/verify_deployment.py` passes against repository manifests.
- [ ] All three completed skill policy validators pass.
- [ ] SPDX or CycloneDX JSON SBOM is present under `dist/`.
- [ ] `python scripts/verify_release.py --dist dist --require-sbom` passes.
- [ ] GitHub build-provenance and SBOM attestations are generated and independently verified.
- [ ] Runtime container has no unaccepted high or critical vulnerability findings.
- [ ] Live `/health`, `/ready`, and authenticated recommendation smoke checks pass.
- [ ] Target-environment load, failure injection, Redis failover, and rollback rehearsal evidence is retained.
### Runtime SBOM fallback

Generate the CycloneDX 1.6 inventory from a clean runtime-only environment constrained by `constraints/runtime.txt`, then prove exact parity before sealing release checksums:

```bash
python -m venv /tmp/cognexus-runtime-sbom
/tmp/cognexus-runtime-sbom/bin/python -m pip install -r requirements.txt -c constraints/runtime.txt
/tmp/cognexus-runtime-sbom/bin/python scripts/generate_sbom.py --output dist/cognexus-runtime.cdx.json
python scripts/verify_runtime_lock.py --sbom dist/cognexus-runtime.cdx.json --require-sbom
```

The generator does not query package indexes after dependencies are installed. The isolated environment prevents development-only constraints from changing the runtime inventory. This complements the source-level SPDX inventory produced in CI; it does not replace the network-backed vulnerability audit.

