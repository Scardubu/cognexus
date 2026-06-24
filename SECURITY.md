# Security Policy

## Supported versions

Security fixes are applied to the latest minor release. At the time of this package, that is `3.2.x`. Older releases should be upgraded before support is requested.

## Reporting a vulnerability

Do not open a public issue containing exploit details, credentials, personal data, or customer content. Use the repository host's private vulnerability-reporting feature or contact the maintainers through a private, authenticated channel.

Include:

- affected version and deployment mode;
- reproducible steps or a minimal proof of concept;
- expected and observed impact;
- relevant request or trace identifiers with secrets removed;
- any known mitigations.

A maintainer should acknowledge a complete report within three business days, provide a triage status within seven business days, and coordinate disclosure after a fix or mitigation is available. These are operational targets, not a warranty.

## Security expectations

Production operators must:

- set `NEXUS_ENV=production`;
- use distinct, randomly generated `OPENAI_API_KEY` and `NEXUS_API_KEY` values;
- use Redis with `NEXUS_ALLOW_SQLITE_FALLBACK=false` for replicated deployments;
- terminate TLS at a trusted ingress and restrict CORS and trusted hosts;
- keep API documentation disabled unless explicitly required;
- store secrets in a managed secret store, not `.env` files or images;
- keep the image, Python dependencies, and GitHub Actions updated;
- monitor authentication failures, rate limits, guardrail rejections, readiness, and provider errors.

See [`docs/SECURITY.md`](docs/SECURITY.md) and [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) for implementation guidance and residual risks.
