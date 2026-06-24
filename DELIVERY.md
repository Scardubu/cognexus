# Cognexus v3.3.1 Enterprise Final Delivery

Start with `README.md`, then review:

- `docs/V3_3_1_ENTERPRISE_FINALIZATION_REPORT.md`
- `docs/V3_3_1_REPOSITORY_INVENTORY.md`
- `docs/SETUP_AND_IMPLEMENTATION.md`
- `docs/ENTERPRISE_AUDIT.md`
- `docs/V3_3_1_PRODUCTION_READINESS_REPORT.md`
- `docs/VALIDATION_REPORT.md`
- `docs/NEXUS_PROMPT_CONTRACT.md`
- `docs/RELEASE_CHECKLIST.md`

Release artifacts are under `dist/`:

- installable wheel and source distribution;
- 39 reproducible portable `.skill` packages;
- deterministic CycloneDX 1.6 runtime SBOM;
- SHA-256 checksum files;
- deterministic `RELEASE_MANIFEST.json` with hashes and sizes for every release file.

Validated repository-local evidence:

- Ruff and formatting: 110 Python files;
- strict MyPy: 107 source files;
- Pytest: 109 passed;
- branch-aware coverage: 79.56% against a 70% floor;
- 39 synchronized skills with 0 errors/warnings;
- three console entry points and 509 verified source-distribution files;
- 70 runtime SBOM components, 43 checksum entries, and 45 release-manifest entries.

Run the deterministic local gate with:

```bash
make bootstrap
python scripts/generate_repository_inventory.py --check
make quality-quick
rm -rf build dist
python -m build --no-isolation
python scripts/verify_distribution.py
python -m venv /tmp/cognexus-runtime-sbom
/tmp/cognexus-runtime-sbom/bin/python -m pip install -r requirements.txt -c constraints/runtime.txt
/tmp/cognexus-runtime-sbom/bin/python -m skill_runtime.cli package --output dist/skills
/tmp/cognexus-runtime-sbom/bin/python scripts/generate_sbom.py --output dist/cognexus-runtime.cdx.json
python scripts/verify_runtime_lock.py --sbom dist/cognexus-runtime.cdx.json --require-sbom
python scripts/create_checksums.py
python scripts/create_release_manifest.py
python scripts/verify_release.py --dist dist --sbom dist/cognexus-runtime.cdx.json --require-sbom
```

Then run the GitHub CI, security, release, and deployment-verification workflows. A
network-backed dependency audit, signed attestation verification, live OpenAI/managed
Redis integration, container/target-cluster validation, load/chaos testing, and rollback
rehearsal remain mandatory before public production promotion. The exact boundary is in
`docs/VALIDATION_REPORT.md`.
