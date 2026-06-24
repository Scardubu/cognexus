# Usage examples: Edge Cache Architecture Architect

## Direct activation

- "Audit this Next.js route tree using the edge cache architecture architect workflow and return a cache classification matrix with privacy and correctness risks."
- "Design the caching strategy for /products and /products/[id] with ISR, surrogate-key invalidation, and CDN configuration for authenticated and anonymous users."
- "Use edge-cache-architecture-architect to identify which routes are accidentally dynamic, propose the narrowest correct cache scope, and estimate origin load reduction."
- "Design privacy-safe cache keys for this multi-tenant SaaS application where tenant data must never cross principals."
- "Propose a cache stampede mitigation strategy for the homepage route under high-traffic launch conditions."
- "Classify every fetch() call in this Server Component tree as static, revalidated, dynamic, or per-user and produce the corresponding Next.js cache policy."

## Composition example

1. Activate `edge-cache-architecture-architect` to classify the request flow, select cache layers, define keys and TTLs, and identify privacy risks.
2. Activate `nextjs-performance-architect` to verify RSC streaming compatibility, PPR boundaries, and framework-specific cache API semantics.
3. Activate `security-hardening-auditor` when the route serves authenticated, tenant-specific, or sensitive data to verify private-data boundaries are enforced.
4. Activate `opentelemetry-observability-architect` to instrument cache hit ratio, origin request rate, invalidation latency, and tail latency before and after changes.
5. Activate `release-incident-operations-architect` for staged rollout of cache policy changes, kill switches for emergency purge, and rollback conditions if stale content is served.

## Expected response shape

```text
Assessment
- Confirmed findings (routes accidentally dynamic, privacy leakage risks, cold-start cost)
- Assumptions (CDN provider, Auth.js version, revalidation event sources)
- Priorities (P0 privacy correctness, P1 performance correctness, P2 hit-ratio optimization)

Route / data classification matrix
- Route | Volatility | Audience | Sensitivity | Cache layer | TTL | Key dimensions

Cache layer decisions
- CDN (Vercel Edge / Cloudflare): which routes, headers
- Next.js Data Cache: fetch() tags and revalidation
- Next.js Full Route Cache: static vs dynamic opt-in
- React memoization: deduplicated server-side fetches

Key design
- Dimensions included (locale, device, currency)
- Dimensions excluded (session tokens, raw user IDs)
- Cardinality analysis

Freshness and invalidation policy
- Tag-based invalidation events and owning services
- Stale-while-revalidate usage and domain tolerance
- Stampede protection approach

Privacy analysis
- Authenticated / per-user routes: confirmed no shared cache
- Vary headers and authorization signal isolation
- Sensitive field exclusion from cache keys

Failure modes
- CDN miss storm on cold start
- Invalidation failure and bounded stale window
- Edge runtime incompatibility on Node-only fetch paths

Observability plan
- Cache hit ratio by route (CDN + app)
- Origin request rate before and after
- p50/p95/p99 latency by cache state (hit/miss/revalidate)
- Invalidation success/failure rate

Rollout / rollback
- Staged traffic shift with hit-ratio monitoring
- Kill switch: force-dynamic flag or purge-all path

Validation commands
- command to measure before/after hit ratio
- command to verify no authenticated response in shared cache
- load test command for cold-start behavior
```
