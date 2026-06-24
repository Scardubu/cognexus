---
name: edge-cache-architecture-architect
description: Designs explicit, measurable, and privacy-safe caching and rendering architectures for Next.js, serverless, CDN, and edge environments. Use when choosing static, dynamic, ISR, PPR, route-handler, middleware, personalization, invalidation, or cache-key strategies.
license: MIT
compatibility: Portable Agent Skills format; works with filesystem-based skill clients and Cognexus 3.3+.
metadata:
  cognexus.version: 3.3.0
  cognexus.category: frontend-experience
  cognexus.risk: medium
  cognexus.progressive_disclosure: 'true'
---

# Edge Cache Architecture Architect

## Activation boundary

**Use this skill when:** rendering mode, CDN behavior, Next.js caching, personalization boundaries, invalidation, stale content, cold starts, or edge-runtime compatibility materially affects correctness, privacy, latency, or cost.

**Do not use it when:** the surface has no meaningful cache or rendering decision, or when a simple local memoization change fully solves the problem.

## Operating contract

1. Classify every datum by volatility, sensitivity, audience specificity, consistency need, and acceptable staleness.
2. Cache only with an explicit key, scope, lifetime, ownership, and invalidation event.
3. Never place private or user-specific data in a shared cache.
4. Preserve correctness before optimizing hit rate; stale or cross-tenant data is a security defect.
5. Verify runtime compatibility and avoid Node-only dependencies in edge execution paths.
6. Measure origin load, hit ratio, tail latency, freshness, and invalidation failures before claiming improvement.

## Workflow

1. Map request flow from browser through CDN/edge, application cache, origin, and data stores.
2. Inventory static, revalidated, dynamic, and personalized fragments.
3. Select the narrowest correct cache layer and define the cache key cardinality.
4. Specify TTL, stale-while-revalidate behavior, tags/surrogate keys, purge triggers, and failure behavior.
5. Separate globally cacheable shells from sensitive or per-user islands.
6. Review headers, cookies, `Vary`, authorization, locale, device, and query-string effects.
7. Load-test cold and warm paths and verify invalidation under concurrent traffic.

## Required patterns

- Explicit cache policy for every network fetch and rendered route.
- Event-driven invalidation for business-critical freshness.
- Bounded stale-while-revalidate only where the domain tolerates staleness.
- Cache stampede protection through request coalescing, jitter, or locking where justified.
- Privacy-safe keys that avoid secrets and unbounded attacker-controlled cardinality.
- Graceful origin fallback and observable purge failures.

## Quality gates

- No authenticated or tenant-specific response can be served across principals.
- Cache keys include every representation-changing dimension and exclude secrets.
- Dynamic dependencies do not accidentally deoptimize shared layouts or route trees.
- Edge paths import only supported APIs and remain within CPU/memory limits.
- Invalidation is testable, reversible, and tied to business events.
- Performance claims include before/after p50, p95, p99, hit ratio, and origin-load evidence.

## Output contract

Return a route/data classification matrix, chosen cache layers, key design, freshness and invalidation policy, privacy analysis, failure modes, observability plan, rollout/rollback steps, and validation commands.

## Pair this skill with

- `nextjs-performance-architect` for RSC, PPR, and framework semantics.
- `security-hardening-auditor` for private-data boundaries.
- `opentelemetry-observability-architect` for latency and hit-ratio evidence.
- `release-incident-operations-architect` for staged rollout and kill switches.
