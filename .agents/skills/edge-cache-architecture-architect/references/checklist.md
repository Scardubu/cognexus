# Edge Cache Architecture Architect checklist

## Mandatory checks

- Classify every route and every fetch() call by volatility, audience specificity, sensitivity, and acceptable staleness before choosing a cache layer.
- Confirm that no authenticated, session-specific, or tenant-specific response can ever be served to a different principal through any cache layer.
- Define an explicit cache key for every cached resource: include every dimension that changes the representation (locale, currency, device tier) and exclude all secrets and unbounded attacker-controlled values.
- Verify that every dynamic dependency (cookies, authorization headers, user IDs) is isolated to a server-rendered island and does not contaminate globally cached shells.
- Specify TTL, stale-while-revalidate window, surrogate/cache-tag naming, and purge trigger for every cached resource.
- Validate that all edge-runtime paths import only supported runtime APIs and remain within CPU and memory limits.
- Measure or estimate origin request rate, CDN hit ratio, and tail latency before and after any cache change; do not claim improvement without evidence.
- Design and test invalidation under concurrent traffic; verify that a failed purge has a bounded stale window, not an unbounded one.
- Implement stampede protection for high-traffic cold-path routes where simultaneous misses would overwhelm the origin.
- Confirm that privacy analysis covers the full Vary header set and all authorization signals visible to the CDN.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `Cache Layer Taxonomy`
- `Step 1 — Map Request Flow`
- `Step 2 — Route / Data Classification Matrix`
- `Step 3 — Next.js Cache APIs`
- `A. fetch() Data Cache with Tags`
- `B. Full Route Cache and Dynamic Opt-In`
- `C. Partial Prerendering (PPR)`
- `D. React Cache Deduplication`
- `Step 4 — CDN Cache-Control and Surrogate Keys`
- `Step 5 — Privacy-Safe Cache Keys`
- `Step 6 — Tag-Based Invalidation`
- `Step 7 — Stampede Protection`
- `Step 8 — Edge Runtime Compatibility`
- `Step 9 — Observability and Measurement`
- `Quality Gates`
- `Activation Triggers`
- `Skill Chain`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] Every route is classified by cache layer, key, TTL, and invalidation trigger.
- [ ] Privacy analysis confirms no cross-principal data leakage through any cache.
- [ ] Cache key dimensions are enumerated and exclude secrets and user-specific values.
- [ ] Stale-while-revalidate is only used where the domain explicitly tolerates staleness.
- [ ] Stampede protection is designed for all high-traffic cold-path routes.
- [ ] Edge runtime compatibility is verified for all edge-deployed paths.
- [ ] Invalidation is tied to business events and is testable.
- [ ] Observability plan includes hit ratio, origin load, and latency evidence.
- [ ] Rollback procedure and kill switch are defined before any cache change ships.
- [ ] No secrets or sensitive data appear in cache keys, Vary headers, or surrogate tags.
