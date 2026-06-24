# Security Guide

## Security model

Nexus applies layered controls around a probabilistic agent runtime. The main trust boundaries are the public HTTP interface, user-supplied prompts, model output, tool execution, session storage, observability export, and external OpenAI API access.

## Required production controls

- Terminate TLS at a trusted reverse proxy or load balancer.
- Set `NEXUS_ENV=production`.
- Set a distinct random `NEXUS_API_KEY` of at least 32 characters; configuring it activates API authentication for APIs, metrics, and documentation routes.
- Store `OPENAI_API_KEY` and application credentials in a secret manager.
- Restrict `NEXUS_CORS_ORIGINS` and `NEXUS_TRUSTED_HOSTS` to exact production domains.
- Set `NEXUS_FORWARDED_ALLOW_IPS` to only the reverse-proxy/ingress source IPs or CIDRs; never use `*` in staging or production.
- Use private Redis networking, authentication, TLS where supported, and `noeviction` so session, lease, and quota keys are never silently discarded.
- Use Redis-backed `NEXUS_RATE_LIMIT_STORAGE_URI` for replicated deployments; live Redis sessions select `REDIS_URL` automatically when no explicit URI is supplied.
- Production Redis mode must set `NEXUS_ALLOW_SQLITE_FALLBACK=false`; unsafe fallback configuration fails at startup.
- Run the container as the included non-root user.
- Keep prompt and output logging disabled unless a reviewed redaction policy exists.
- Patch dependencies and rebuild immutable images regularly.
- Protect CI branches and require review for workflow changes.

## Secrets

Secrets are read from environment variables and never committed. `.env` is ignored by Git and is intended only for local development.

Validate that no secret is committed:

```bash
git grep -nE '(sk-[A-Za-z0-9_-]{20,}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|password\s*=)' -- ':!docs/SECURITY.md' || true
```

Use platform-native secret stores in production. Rotate a secret immediately after suspected exposure and invalidate the old credential.

## Authentication

The built-in X-API-Key or Bearer API key is appropriate for a private service-to-service deployment or an initial controlled release. Protected routes fail closed in both staging and production when the key is absent. Public multi-user products should place Nexus behind an identity-aware gateway and use short-lived signed tokens with tenant claims.

Do not use session IDs as authentication credentials.

## Authorization and tool policy

Only registered tools are exposed. Missing historical tools remain metadata and cannot execute. New tools must define:

1. Input schema.
2. Authentication requirements.
3. Allowed network and filesystem scope.
4. Timeout and output-size limits.
5. Redaction behavior.
6. Unit and adversarial tests.

Do not grant general shell, unrestricted network, or arbitrary filesystem tools to public requests.

## Prompt-injection defense

`security/sanitization.py` and `middleware/input_guardrail.py` reject known high-risk instruction patterns, control characters, malformed payloads, and oversized content. Agent instructions also establish authority boundaries.

Prompt-injection detection is heuristic. Treat all retrieved or user-provided content as untrusted data, scope tools to least privilege, require deterministic authorization outside the model, and validate every side effect.

## Output controls

The output guardrail checks for secret-like patterns, malformed trace blocks, unsafe content, and architecture constraint violations. Buffered streaming validates the full answer before transmission.

Do not switch to raw token streaming without adding a policy-compliant incremental safety design and tests.

## CORS and hosts

Safe production example:

```dotenv
NEXUS_CORS_ORIGINS=https://app.example.com
NEXUS_TRUSTED_HOSTS=api.example.com
```

Wildcard origins and wildcard trusted hosts are rejected by production configuration validation. Origins must be exact HTTP(S) origins without paths or credentials, and CORS credentials are disabled.

## Rate limits and admission control

Rate limits are configured through environment variables and applied before expensive orchestration. Development and single-process SQLite runs use bounded in-memory storage. Staging/production Redis deployments use shared Redis-backed storage by default, and startup rejects an explicit `memory://` backend in that topology. Limiter storage errors are not swallowed and do not fall back to process-local counters.

Request bodies are rejected by a streaming byte limit before JSON buffering. The server launcher also applies a bounded Uvicorn concurrency limit and socket backlog. These controls reduce abuse but are not a complete denial-of-service defense; combine them with edge quotas, connection limits, WAF/bot controls where appropriate, and provider spend budgets.

## Data retention

Define a retention period for sessions and logs. Redis TTL is controlled by `NEXUS_REDIS_TTL_SECONDS`. Delete sessions through the API or a reviewed retention job.

Avoid storing regulated or highly sensitive data in prompts unless the complete deployment has the required legal, contractual, encryption, access-control, and retention controls.

## Dependency and image security

CI should be extended with your organization's approved vulnerability and secret scanners. Useful release gates include:

```bash
python -m pip install pip-audit
pip-audit -r constraints/runtime.txt
docker build -t nexus-openai:scan .
```

Pin direct dependencies, review transitive updates, run `python -m pip check` after every clean install, and rebuild when the base image receives security fixes. The release build must use `python -m build --no-isolation` only after the audited build toolchain is installed, so packaging cannot silently fetch a different backend toolchain.

## Incident response checklist

1. Contain affected credentials, clients, or deployments.
2. Preserve relevant logs and trace identifiers without spreading secrets.
3. Rotate credentials and revoke compromised access.
4. Identify the first affected release and request window.
5. Patch and add a regression test.
6. Redeploy an immutable image.
7. Verify health, readiness, guardrails, sessions, and telemetry.
8. Complete required notifications and a post-incident review.

## Security limitations

This repository does not by itself provide tenant isolation, end-user identity management, a web application firewall, malware scanning for file uploads, human approval workflows for high-impact actions, or compliance certification. Add those controls according to the product risk profile.
