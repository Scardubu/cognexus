# Cognexus Threat Model

## Scope

This model covers the FastAPI service, OpenAI Agents SDK orchestration, portable Agent Skills, session persistence, observability export, CI/CD, and container/Kubernetes deployment assets. It does not certify a surrounding identity provider, ingress, Redis service, cloud account, or end-user application.

## Assets

- OpenAI and service API credentials.
- User prompts, session history, and model outputs.
- Tool permissions and external-service credentials.
- Skill instructions and packaged resources.
- Build artifacts, container images, CI credentials, and provenance.
- Availability, request capacity, and provider quota.

## Trust boundaries

1. **Client to API:** untrusted request headers, paths, and JSON bodies.
2. **API to orchestrator:** validated but still adversarial natural language.
3. **Orchestrator to tools/agents:** model-selected calls constrained by schemas and registered capabilities.
4. **Runtime to OpenAI:** outbound TLS and provider authentication.
5. **Runtime to Redis/SQLite:** persistence and cross-request state.
6. **Runtime to skill filesystem:** potentially untrusted text and scripts.
7. **Runtime to telemetry:** metadata leaves the process; content must not.
8. **Source to CI/release:** workflow changes and dependency updates can affect the supply chain.

## Primary threats and controls

| Threat | Control | Residual risk |
|---|---|---|
| Oversized or malformed requests | Pydantic schemas, streaming byte limit, character limits, timeouts | Edge infrastructure must still absorb connection floods |
| API credential guessing or replay | Constant-time static-key comparison, live fail-closed configuration, TLS requirement, shared Redis rate limiting | Static keys lack user identity, rotation metadata, and fine-grained authorization |
| Prompt injection | Instruction hierarchy, heuristic screening, least-privilege tools, deterministic validation | Natural-language detection is not a security boundary and can produce false positives/negatives |
| Excessive agency | Only registered tools, bounded turns/calls, deferred tool discovery, no skill-script execution | Future side-effecting tools require independent authorization and approval controls |
| Secret disclosure | Secret-valued settings, no content logging/tracing, output secret patterns | Pattern matching cannot identify every proprietary token format |
| Session collision, traversal, or cross-replica race | Shared session-ID validation, process-local locks, and a bounded Redis distributed lease | Static service authentication does not provide tenant isolation |
| Redis outage and split brain | Fail-closed production policy; SQLite fallback forbidden for production Redis | Single-replica non-production fallback can still lose recent distributed state |
| Skill path traversal or archive abuse | Symlink-component denial, no-follow file reads, approved roots, size/UTF-8 limits, YAML alias denial | Administrators can still install malicious instruction content; review remains required |
| Provider/API exhaustion | Process run gate, queue timeout, request timeout, shared live Redis IP limits, bounded HTTP concurrency/backlog, bounded retries | Tenant/provider budgets still require an identity-aware external quota service |
| Forwarded-header spoofing | Validated proxy IP/CIDR trust list, live wildcard rejection, single configuration-driven launcher | Operators must keep ingress source ranges current and block direct backend access |
| Telemetry leakage | Content-free attributes, sensitive tracing forced false, bounded exporter queues | Collector configuration and downstream retention remain operator responsibilities |
| Dependency or workflow compromise | Dependency audit, CodeQL, dependency review, Dependabot, artifact checksums and attestations | Action tags are mutable unless the organization pins reviewed commit SHAs |
| Container escape | Non-root UID, read-only root, dropped capabilities, no-new-privileges, restricted Kubernetes context | Kernel/runtime vulnerabilities and host policy remain outside this repository |

## Abuse cases requiring an external control plane

The built-in static key is suitable for private service-to-service access, not a public multi-tenant product. Add an identity-aware gateway and policy service before supporting end users, per-user quotas, organization boundaries, billing, or regulated data. High-impact tools should use scoped credentials and a human approval or transaction-signing step that the model cannot bypass.

## Security verification

```bash
make quality
make audit
python scripts/validate_repository.py
python -m skill_runtime.cli validate
```

For a release, also scan the final container image, verify artifact checksums and provenance, test credential rotation, and exercise denial paths for authentication, rate limits, request size, capacity, session backend failure, and output validation.
