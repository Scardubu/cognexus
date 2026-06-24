# Detailed guidance: Edge Cache Architecture Architect

> This reference preserves and reorganizes the supplied domain guidance. It is loaded on demand. Verify time-sensitive framework versions, security recommendations, legal requirements, prices, APIs, and platform behavior against authoritative current documentation before applying them. The core `SKILL.md` operating contract takes precedence if guidance conflicts.

# Edge Cache Architecture Architect

Design explicit, measurable, and privacy-safe caching architectures for Next.js,
serverless, CDN, and edge environments. Every cache decision has a key, a lifetime,
an owner, and an invalidation event. Correctness before hit ratio.

---

## Cache Layer Taxonomy

```
Browser Cache          ← per-user, not shared; controlled by Cache-Control
CDN / Edge Cache       ← globally shared; Vercel Edge, Cloudflare, CloudFront
Next.js Full Route     ← server-side HTML + RSC payload cache; per route segment
Next.js Data Cache     ← persistent fetch() result cache; tagged, on-demand purge
React Cache            ← request-scoped deduplication; cleared per request
In-memory / Redis      ← application-level; custom key, TTL, eviction
```

**Golden rule:** never use a shared cache layer (CDN, Full Route Cache, Data Cache)
for data that varies by authenticated user, session, or tenant. Serve those through
a request-scoped or per-user layer only.

---

## Step 1 — Map Request Flow

Before choosing any cache layer, draw the full request path:

```
Browser
  → CDN / Vercel Edge (Cache-Control: public, s-maxage=...)
    → Next.js Full Route Cache (static HTML + RSC payload)
      → Next.js Data Cache (fetch() with tags and revalidation)
        → Origin DB / API
          → (background) Tag-based on-demand revalidation
```

At each layer, ask: **Can this response be shared across principals?**
If the answer is anything other than "yes, for all users of all tenants," the layer
must be bypassed or the request must be routed to a non-shared cache.

---

## Step 2 — Route / Data Classification Matrix

Classify every route before writing any cache configuration:

| Route | Volatility | Audience | Sensitivity | Cache layer | TTL |
|---|---|---|---|---|---|
| `/` (homepage) | Low (hours) | All users | None | CDN + Full Route | 1h / revalidate on publish |
| `/products` | Medium (minutes) | All users | None | Data Cache + CDN | 5m / tag: `products` |
| `/products/[id]` | Low (hours) | All users | None | Data Cache + CDN | 1h / tag: `product:{id}` |
| `/dashboard` | High (real-time) | Authenticated | User data | No shared cache; dynamic | — |
| `/api/cart` | High (per-request) | Authenticated | Cart / PII | No cache; `Cache-Control: private, no-store` | — |
| `/api/prices` | Medium (minutes) | All users | Currency-specific | Data Cache | 5m / tag: `prices:{currency}` |

---

## Step 3 — Next.js Cache APIs

### A. fetch() Data Cache with Tags

```typescript
// app/products/page.tsx — Server Component
// Globally cacheable: no user-specific data

async function getProducts() {
  const res = await fetch('https://api.example.com/products', {
    next: {
      tags:      ['products'],   // tag for on-demand revalidation
      revalidate: 300,            // 5 minutes background revalidation (ISR)
    },
  })
  if (!res.ok) throw new Error(`Failed to fetch: ${res.status}`)
  return res.json() as Promise<Product[]>
}

export default async function ProductsPage() {
  const products = await getProducts()
  return <ProductList products={products} />
}
```

```typescript
// app/products/[id]/page.tsx — per-product cache with granular invalidation
import { notFound } from 'next/navigation'

async function getProduct(id: string) {
  const res = await fetch(`https://api.example.com/products/${id}`, {
    next: {
      tags:      [`product:${id}`, 'products'],  // invalidate individually or all
      revalidate: 3600,                           // 1 hour background refresh
    },
  })
  if (!res.ok) {
    if (res.status === 404) notFound()
    throw new Error(`Failed to fetch product ${id}`)
  }
  return res.json() as Promise<Product>
}
```

### B. Full Route Cache and Dynamic Opt-In

```typescript
// Force a route to always be dynamic (never cached at route level)
// Use for authenticated pages, real-time data, personalized content
export const dynamic = 'force-dynamic'

// Opt into static generation with periodic background revalidation
export const revalidate = 3600   // seconds; 0 = always dynamic

// Generate static params for known IDs (SSG at build time + ISR at runtime)
export async function generateStaticParams() {
  // getTopProducts() is a user-defined data-fetching helper; fetch only the IDs you want pre-rendered
  const products = await getTopProducts()   // fetch top 100 at build time
  return products.map(p => ({ id: p.id }))
}

// Behavior of unstated exports:
// revalidate: undefined  → Next.js default (defer to fetch() per call)
// dynamic:    'auto'     → static unless a dynamic API is used (cookies, headers)
```

### C. Partial Prerendering (PPR) — Static Shell + Dynamic Islands

PPR allows a route to serve a cached static shell immediately while streaming in
dynamic, authenticated islands. The shell and the islands must be designed together.

```typescript
// next.config.ts — enable experimental PPR
import type { NextConfig } from 'next'

const config: NextConfig = {
  experimental: {
    ppr: true,
  },
}

export default config
```

```tsx
// app/dashboard/page.tsx — PPR: static shell, dynamic islands
import { Suspense } from 'react'
import { auth } from '@/lib/auth'   // Auth.js / NextAuth v5 — adapt to your auth provider

// This component is STATIC — renders at build time, cached at CDN
function DashboardShell({ children }: { children: React.ReactNode }) {
  return (
    <main>
      <nav>Cognexus Dashboard</nav>           {/* static; cached */}
      <aside>Navigation links</aside>          {/* static; cached */}
      {children}
    </main>
  )
}

// This component is DYNAMIC — runs per-request with user session
async function UserMetrics() {
  const session = await auth()                // reads cookies → forces dynamic
  const metrics = await getUserMetrics(session.user.id)
  return <MetricsPanel metrics={metrics} />
}

export default function DashboardPage() {
  return (
    <DashboardShell>
      <Suspense fallback={<MetricsSkeleton />}>
        <UserMetrics />               {/* streams in dynamically */}
      </Suspense>
    </DashboardShell>
  )
}
```

**PPR critical rules:**
- The static shell must not read cookies, authorization headers, or any request-specific value.
- Dynamic islands are wrapped in `<Suspense>` — they stream after the static shell is sent.
- The CDN caches the static shell; dynamic islands bypass the CDN entirely.

### D. React Cache Deduplication

```typescript
// lib/data/products.ts — request-scoped deduplication with React cache()
// Prevents N+1 calls when multiple Server Components fetch the same data
import { cache } from 'react'

export const getProduct = cache(async (id: string): Promise<Product> => {
  // Called 10× in one request render → only 1 network call
  const res = await fetch(`https://api.example.com/products/${id}`, {
    next: { tags: [`product:${id}`], revalidate: 3600 },
  })
  if (!res.ok) throw new Error(`Product ${id} fetch failed`)
  return res.json()
})
```

---

## Step 4 — CDN Cache-Control and Surrogate Keys

```typescript
// app/api/prices/route.ts — route handler with CDN cache headers
import { NextRequest, NextResponse } from 'next/server'

export async function GET(req: NextRequest): Promise<NextResponse> {
  const currency = req.nextUrl.searchParams.get('currency') ?? 'USD'

  const prices = await getPricesByCurrency(currency)

  return NextResponse.json(prices, {
    headers: {
      // CDN caches for 5 minutes, browser treats as private
      'Cache-Control':     'public, s-maxage=300, stale-while-revalidate=60',
      // Surrogate keys for granular CDN purge (Vercel / Fastly / Cloudflare)
      'Surrogate-Key':     `prices prices:${currency}`,
      // Vary on nothing user-specific (currency is in the URL, not a header)
      'Vary':              'Accept-Encoding',
    },
  })
}
```

**Cache-Control directives for CDN vs browser:**

| Directive | Meaning |
|---|---|
| `public` | CDN may cache this response |
| `private` | CDN must NOT cache; browser may |
| `no-store` | Neither CDN nor browser should cache (use for authenticated API responses) |
| `s-maxage=N` | CDN TTL in seconds (overrides `max-age` for shared caches) |
| `max-age=N` | Browser TTL in seconds |
| `stale-while-revalidate=N` | Serve stale while fetching fresh in background (SWR) |
| `must-revalidate` | Do not serve stale even if origin is unavailable |

---

## Step 5 — Privacy-Safe Cache Keys

Cache key cardinality must be bounded and must exclude all secrets.

```
Safe to include in cache keys:
  ✓ Language / locale from URL path (e.g., /en-US/products)
  ✓ Currency from URL query parameter
  ✓ Device tier from a normalized Accept header (mobile|desktop) derived at CDN
  ✓ API version from URL path
  ✓ Non-sensitive feature flag (from URL path or anonymous cohort)

Never include in cache keys:
  ✗ Session tokens, JWT values, cookie values
  ✗ Raw user IDs or account IDs
  ✗ CSRF tokens
  ✗ Attacker-controlled query parameters without normalization
  ✗ Authorization header values
  ✗ IP addresses (unless strictly required and documented for geo-routing)
```

**Cloudflare cache key rule example:**

```hcl
# Cloudflare Transform Rule — normalize cache key
# Include only locale from URL; strip all cookies and user-specific headers
cache_key {
  exclude_origin    = false
  query_string {
    include = ["currency", "locale"]   # explicit allowlist
  }
  header {
    exclude_origin = true
    check_presence = ["Authorization"]  # presence signal → bypass cache
  }
  cookie {
    include = []    # no cookies in shared cache key
  }
}
```

---

## Step 6 — Tag-Based Invalidation

On-demand invalidation via tags allows surgical purge without flushing the entire cache.

```typescript
// app/api/products/revalidate/route.ts — webhook handler for CMS content update
import { revalidateTag } from 'next/cache'
import { NextRequest, NextResponse } from 'next/server'
import { verifyWebhookSignature } from '@/lib/webhooks'

export async function POST(req: NextRequest): Promise<NextResponse> {
  const body = await req.text()

  // Verify the webhook is from a trusted source
  const isValid = verifyWebhookSignature(
    body,
    req.headers.get('X-Signature-SHA256') ?? '',
    process.env.CMS_WEBHOOK_SECRET!,
  )
  if (!isValid) {
    return NextResponse.json({ error: 'invalid_signature' }, { status: 401 })
  }

  const payload = JSON.parse(body) as { type: string; productId?: string }

  if (payload.type === 'product.updated' && payload.productId) {
    // Surgical purge: only this product's cached data
    revalidateTag(`product:${payload.productId}`)
  } else if (payload.type === 'catalog.updated') {
    // Broader purge: all products
    revalidateTag('products')
  }

  return NextResponse.json({ revalidated: true })
}
```

**Tag naming convention:**

| Pattern | Scope |
|---|---|
| `products` | All product data |
| `product:{id}` | One specific product |
| `prices` | All pricing data |
| `prices:{currency}` | Prices for one currency |
| `user:{id}` | Per-user data (never in shared cache) |
| `tenant:{id}` | Per-tenant data (never in shared cache) |

---

## Step 7 — Stampede Protection

When a high-traffic route's cache entry expires simultaneously across many concurrent
requests, a thundering herd hits the origin. Mitigate with:

**Option A: stale-while-revalidate (SWR) — preferred for tolerant domains**
```typescript
await fetch(url, {
  next: {
    revalidate: 300,    // background refresh after 5 minutes
    // Up to 60 more seconds of stale content while refreshing
  },
  headers: {
    'Cache-Control': 'stale-while-revalidate=60',
  },
})
```

**Option B: Request coalescing lock for cold-start paths**
```typescript
// lib/cache/coalescing.ts
import { LRUCache } from 'lru-cache'

const inflightRequests = new LRUCache<string, Promise<unknown>>({
  max:  500,
  ttl:  30_000,   // 30 second maximum in-flight window
})

export async function coalesced<T>(
  key:     string,
  fetcher: () => Promise<T>,
): Promise<T> {
  const existing = inflightRequests.get(key) as Promise<T> | undefined
  if (existing) return existing

  const promise = fetcher().finally(() => {
    inflightRequests.delete(key)
  })
  inflightRequests.set(key, promise)
  return promise
}
```

**Option C: Jitter on background revalidation TTL**
```typescript
// Add random jitter to prevent synchronized expiry across instances
const BASE_TTL    = 3600
const JITTER_SECS = Math.floor(Math.random() * 120)  // ±2 minutes
const revalidate  = BASE_TTL + JITTER_SECS
```

---

## Step 8 — Edge Runtime Compatibility

Routes deployed to the Edge Runtime run in a V8 isolate with a restricted API surface.
Verify before assuming Node.js APIs are available.

```typescript
// next.config.ts — opt a route into edge runtime
export const runtime = 'edge'   // declare in route file or layout

// APIs available at edge:
//   ✓ fetch(), Request, Response, Headers, URL
//   ✓ TextEncoder, TextDecoder, ReadableStream, WritableStream
//   ✓ SubtleCrypto (via crypto.subtle)
//   ✓ setTimeout, setInterval (with limits)
//   ✓ WebSocket (Cloudflare only, not Vercel Edge)

// APIs NOT available at edge:
//   ✗ Node.js built-ins: fs, path, net, http, child_process
//   ✗ Buffer (use Uint8Array instead)
//   ✗ require() / CommonJS
//   ✗ Prisma Client (uses Node.js APIs; use Prisma Accelerate or a fetch-based adapter)
//   ✗ most npm packages that depend on Node internals
```

```bash
# Test edge compatibility locally
npx next build && npx next start
# Check the build output for "ƒ Edge" annotations on routes
# Any Node.js dependency used in an edge route will fail at build time
```

---

## Step 9 — Observability and Measurement

**Do not claim caching improvement without before-and-after evidence.**

```typescript
// Custom OpenTelemetry metric for cache hit ratio
import { metrics } from '@opentelemetry/api'

const meter      = metrics.getMeter('nextjs-cache')
const cacheHits  = meter.createCounter('cache_hits_total',  { description: 'Cache hit count' })
const cacheMisses = meter.createCounter('cache_misses_total', { description: 'Cache miss count' })

export function recordCacheResult(route: string, hit: boolean): void {
  const attrs = { route }
  if (hit) cacheHits.add(1, attrs)
  else     cacheMisses.add(1, attrs)
}
```

**Vercel Analytics — key metrics to track:**
```
Cache Hit Ratio by route:  Target > 80% for globally cacheable routes
Origin Requests / minute:  Should drop proportionally with hit ratio
p50/p95/p99 TTFB:         Cached response should be < 50ms at CDN edge
Revalidation queue depth:  High depth indicates origin can't keep up with ISR demand
Purge success/failure rate: Failures mean stale content until TTL expiry
```

**Baseline measurement before any cache change:**
```bash
# Simulate load before change
npx artillery run artillery-baseline.yml --output baseline.json

# After cache change, run same test
npx artillery run artillery-baseline.yml --output after.json

# Compare
npx artillery report baseline.json after.json
```

---

## Quality Gates

- No authenticated or tenant-specific response can be served across principals under any cache configuration.
- Cache keys include every representation-changing dimension and exclude all secrets and attacker-controlled values.
- Dynamic dependencies do not accidentally deoptimize shared route cache segments.
- Edge paths import only supported runtime APIs and remain within CPU and memory limits.
- Invalidation is tied to business events, is testable, and has a bounded maximum stale window.
- Performance claims include before-and-after p50/p95/p99, hit ratio, and origin-load evidence.
- Stampede protection is designed for any cold-path route that handles significant traffic.

---

## Activation Triggers

- "Which routes in this Next.js app are accidentally dynamic?"
- "Design the cache key for this multi-currency, multi-locale pricing endpoint"
- "How do I invalidate the cache when a product is updated in the CMS?"
- "This page is slow on cold start — design stampede protection"
- "Set up tag-based cache invalidation for our product catalog"
- "Is this authenticated response at risk of leaking into the CDN cache?"
- "Design the PPR strategy for this dashboard route"
- "Configure the CDN Cache-Control headers for our API route handlers"
- "Our ISR is not picking up CMS changes — diagnose and fix"

---

## Skill Chain

**Feeds into:**
- `nextjs-performance-architect` — RSC streaming, PPR boundaries, and framework-specific cache API semantics.
- `security-hardening-auditor` — private-data boundary enforcement, Vary header analysis, cross-tenant data isolation.
- `opentelemetry-observability-architect` — hit ratio instrumentation, origin load metrics, latency evidence.
- `release-incident-operations-architect` — staged cache policy rollout, kill switches for emergency purge, rollback conditions.

**Creative combination:** `edge-cache-architecture-architect` designs the cache strategy
and privacy boundaries. `opentelemetry-observability-architect` instruments every layer
with hit counters and latency histograms. `release-incident-operations-architect`
stages the rollout with automatic rollback if stale-content alerts fire. Together
these three make cache changes safe, measurable, and reversible.
