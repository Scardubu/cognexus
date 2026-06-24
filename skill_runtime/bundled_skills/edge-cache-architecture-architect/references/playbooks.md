# Edge-cache architecture playbooks

## Cacheability classification

Classify every route before applying a cache rule: public immutable, public revalidatable, private user-scoped, sensitive, or uncacheable mutation. Authentication alone does not prove a response is private; the response data and authorization boundary determine the policy. Sensitive and mutation responses must be `no-store` at every layer.

## Safe cache-key design

The cache key must include every input that can alter the response: canonical path, normalized supported query parameters, representation headers, tenant boundary, locale, and authorization scope where private caching is explicitly allowed. Reject unbounded or attacker-controlled headers from the key. Normalize query ordering and reject unknown parameters before cache lookup.

## Invalidation rollout

1. Identify the source of truth and all edge, regional, and application cache layers.
2. Add versioned surrogate keys or content versions before changing TTLs.
3. Test create, update, delete, permission-change, and rollback invalidation paths.
4. Release with a short TTL and stale-if-error window.
5. Increase TTL only after hit ratio, origin load, stale responses, and purge latency remain within gates.
6. Roll back by changing the policy version or bypassing the cache; never depend on global purge as the only recovery mechanism.

## Cache-poisoning response

Disable affected rules, preserve request/response samples without secrets, identify key omissions and normalization mismatches, purge the affected namespace, and verify origin authorization independently. Add a regression test that sends colliding requests across tenants, encodings, languages, and query ordering.

## Origin protection

Use request coalescing, bounded stale-while-revalidate, stale-if-error, per-key concurrency limits, and origin circuit breakers. Monitor miss storms and eviction rate. A cache must degrade safely when the edge provider or purge API is unavailable.
