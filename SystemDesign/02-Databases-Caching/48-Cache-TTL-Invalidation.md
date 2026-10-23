# 48. Cache TTL + Invalidation
# हिंदी में: TTL — cache में डेटा कितनी देर रहेगा; Invalidation — डेटा बदलने पर पुराना cache हटाना/अपडेट करना

---

## 🔵 Simple Definition (English)
- **TTL (Time To Live):** how long a cached item is valid before it automatically expires. It's a **time-based** freshness guarantee: "at most N seconds stale".
- **Cache invalidation:** actively **removing or updating** cached data when the source data changes. It's an **event-based** freshness guarantee.
Real systems use **both**: invalidation for freshness, TTL as a safety net.

> "There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton

## 🔵 सरल परिभाषा (Hindi)
TTL = cache में डेटा कितने सेकंड रहेगा, फिर अपने आप हट जाएगा। Invalidation = असली डेटा बदलते ही cache से पुराना डेटा हटा देना।
दोनों साथ इस्तेमाल करो — invalidation से ताज़गी, और TTL एक safety net की तरह।

---

## 🔴 Problem it Solves
Caches are copies, and copies go **stale**:
- A user updates their name but still sees the old one.
- A restaurant marks itself closed, yet customers keep ordering from it.
- A price changes, but the old price is shown at checkout → legal and trust issues.

Without a strategy, you either serve wrong data or **disable caching** and lose performance. TTL and invalidation let you decide **how stale is acceptable** per data type, and make updates visible quickly.

## 🔴 यह क्यों बना? (Hindi)
Cache एक copy है और copy पुरानी हो जाती है — नाम बदला पर पुराना दिख रहा है, रेस्टोरेंट बंद है पर ऑर्डर आ रहे हैं, कीमत बदली पर पुरानी दिख रही है।
TTL और invalidation से तय करते हो कि कितना पुराना डेटा चलेगा, और बदलाव जल्दी कैसे दिखे।

---

## 🟢 How it Works — Step by Step

### TTL — choosing values

```
┌───────────────────────────────┬──────────────────┬───────────────────────────────┐
│ Data                          │ Typical TTL      │ Why                           │
├───────────────────────────────┼──────────────────┼───────────────────────────────┤
│ Static assets (hashed JS/CSS) │ 1 year, immutable│ filename changes on deploy    │
│ Product catalog / menu        │ 5–15 min         │ changes rarely; + invalidation│
│ Restaurant open/closed, stock │ 10–30 s          │ changes often, matters        │
│ Home feed / recommendations   │ 1–5 min          │ freshness less critical       │
│ User profile                  │ 15–60 min        │ + invalidate on update        │
│ Sessions                      │ = session length │ security                      │
│ Exchange rates / weather      │ match provider   │ provider updates every N min  │
│ "Not found" (negative cache)  │ 30–60 s          │ new items should appear soon  │
│ Balance at payment            │ don't cache      │ must be exact                 │
└───────────────────────────────┴──────────────────┴───────────────────────────────┘
Rule: TTL = maximum staleness your business can tolerate for that data.
Add JITTER (±10–20%) so many keys don't expire at the same second (Topic 50).
```

### Invalidation strategies

```
1. Delete on write (explicit)
   UPDATE DB → DEL key            simple; every write path must remember

2. Event-driven / CDC
   DB change → outbox/Debezium → Kafka → invalidator → DEL keys
   reliable, decoupled, covers ALL writers (admin tools, batch jobs, other services)

3. Versioned keys (namespace bump)
   key = product:{id}:v{version}  or  catalog:v{N}:product:{id}
   change → bump version → old keys never read again, expire via TTL
   great for "invalidate everything in a category" without scanning

4. Tag-based invalidation
   each cached page tagged with entities it uses: [restaurant:42, menu:42]
   change restaurant 42 → purge all keys/pages with tag restaurant:42
   (Varnish xkey, Fastly Surrogate-Keys, Next.js revalidateTag, Cloudflare Cache-Tags)

5. Pub/Sub broadcast for local (in-process) caches
   write → PUBLISH invalidate product:7 → every app instance drops its L1 copy

6. Stale-while-revalidate
   serve the stale value immediately, refresh in background → no user waits
```

### Invalidating MULTIPLE cache layers

```
Change: restaurant 42 updates its menu

 DB  ──► Redis key menu:42                → DEL (or bump version)
     ──► App L1 in-memory cache            → pub/sub "invalidate menu:42"
     ──► CDN cached /api/restaurants/42/menu → purge by tag/URL (or short max-age)
     ──► Browser / RN app cache             → can't purge remotely!
                                              → short Cache-Control max-age + ETag revalidation,
                                                or push event (WebSocket/push) telling app to refetch
Layer order: invalidate from the INSIDE out (DB → Redis → CDN), so outer layers refill from fresh data.
```

### HTTP caching headers (client/CDN TTL)

```
Cache-Control: public, max-age=60, s-maxage=300, stale-while-revalidate=30
   max-age          → browser TTL
   s-maxage         → CDN/shared cache TTL
   stale-while-revalidate → serve stale while refetching
Cache-Control: private, no-store     → user-specific / sensitive (never cache in CDN)
ETag: "v42"  + If-None-Match → 304 Not Modified (revalidation, saves bandwidth)
Cache-Control: public, max-age=31536000, immutable   → hashed static assets
```

### Common invalidation bugs

```
- Forgot to invalidate in one write path (admin panel, bulk import, cron) → stale forever (if no TTL!)
- Delete cache BEFORE DB commit → reader reloads old data
- Invalidate the wrong key (key format drift: product:7 vs products:7)
- Cached derived data (lists, search results) not invalidated when one item changes
- Caching user-specific data in CDN (public) → data leak to other users ❌❌
- No TTL at all → one missed invalidation = permanent bug
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर डेटा के लिए TTL चुनो = business कितनी पुरानी जानकारी सह सकता है (मेन्यू 10 मिनट, stock 30 सेकंड, balance cache नहीं)।
2. TTL में थोड़ा random jitter जोड़ो ताकि सारी keys एक साथ expire न हों।
3. Invalidation के तरीके: write पर delete, CDC/events से delete, versioned keys, tag-based purge, pub/sub से local cache साफ़।
4. कई परतें हों (Redis, CDN, ब्राउज़र) तो अंदर से बाहर की तरफ़ साफ़ करो; ब्राउज़र/ऐप का cache दूर से नहीं हटता — छोटा max-age + ETag रखो।
5. सबसे बड़ा नियम: हमेशा TTL रखो, ताकि कोई invalidation छूट भी जाए तो डेटा कुछ समय बाद ख़ुद ठीक हो जाए।

---

## 🟡 Real World Example

**Facebook** — invalidates memcache across regions by tailing the MySQL replication log (McSqueal). Every committed write produces delete commands for the affected keys, so no app code path can "forget".

**Fastly / Cloudflare surrogate keys** — news sites (The Guardian, NYT) tag every cached page with the article, author and section IDs. When an article is corrected, one purge by tag clears every page showing it, worldwide, in ~150 ms.

**Next.js ISR / revalidateTag** — e-commerce sites built on Next.js cache product pages statically and call `revalidateTag('product-7')` from a CMS webhook when the product changes.

**Steam caching incident (Christmas 2015)** — a CDN caching misconfiguration served **logged-in users' account pages to other users** for about an hour. It's a classic example of why private, user-specific responses must never be publicly cached.

## 🟡 Real Example Hindi में
Facebook MySQL के replication log को पढ़कर अपने आप cache keys delete करता है — कोई code path invalidation "भूल" नहीं सकता।
2015 में Steam पर CDN की ग़लत cache setting से दूसरे यूज़र्स के अकाउंट पेज दूसरों को दिखने लगे — इसलिए यूज़र का निजी डेटा कभी public cache में मत रखो।

---

## 🟠 My Stack Example

### Node — TTL with jitter + versioned namespace for bulk invalidation
```js
const jitter = (ttl) => Math.round(ttl * (0.9 + Math.random() * 0.2));

async function catalogVersion() {
  return (await redis.get('catalog:version')) ?? '1';
}
async function getCategoryProducts(catId) {
  const v = await catalogVersion();
  const key = `catalog:v${v}:cat:${catId}`;
  return cached(key, jitter(600), () => repo.productsByCategory(catId));
}
// admin bulk-updates prices → invalidate ALL catalog keys instantly, no SCAN needed
await redis.incr('catalog:version');
```

### Event-driven invalidation (outbox → worker)
```js
// in the same DB transaction as the update
await tx.query("INSERT INTO outbox(topic, payload) VALUES ('menu.changed', $1)", [{ restaurantId }]);

// invalidator worker (consumes outbox/Kafka)
bus.on('menu.changed', async ({ restaurantId }) => {
  await redis.del([`menu:${restaurantId}`, `restaurant:${restaurantId}`]);
  await redis.publish('l1:invalidate', `menu:${restaurantId}`);          // app-local caches
  await cdn.purgeByTag(`restaurant-${restaurantId}`);                    // CloudFront/Cloudflare
});
```

### L1 in-process cache + pub/sub invalidation
```js
import { LRUCache } from 'lru-cache';
const l1 = new LRUCache({ max: 5000, ttl: 5000 });         // 5s local cache
const sub = redis.duplicate(); await sub.connect();
await sub.subscribe('l1:invalidate', (key) => l1.delete(key));
```

### HTTP headers in Express
```js
// public, cacheable by CDN; browser revalidates quickly
res.set('Cache-Control', 'public, max-age=30, s-maxage=300, stale-while-revalidate=60');
res.set('Cache-Tag', `restaurant-${id}`);                   // (Cloudflare Enterprise) / Surrogate-Key (Fastly)
// user-specific
res.set('Cache-Control', 'private, no-store');
```

### Next.js App Router
```ts
// cache fetch with tag + time-based revalidation
const menu = await fetch(`${API}/restaurants/${id}/menu`, { next: { revalidate: 300, tags: [`restaurant-${id}`] } }).then(r => r.json());

// app/api/revalidate/route.ts — called by backend webhook on change
import { revalidateTag } from 'next/cache';
export async function POST(req: Request) {
  const { tag, secret } = await req.json();
  if (secret !== process.env.REVALIDATE_SECRET) return new Response('no', { status: 401 });
  revalidateTag(tag);
  return Response.json({ ok: true });
}
```

### React Native — client cache freshness
```ts
useQuery({ queryKey: ['menu', id], queryFn: () => getMenu(id), staleTime: 60_000 });
// Server pushes "menu.changed" over WebSocket / silent push → client invalidates:
socket.on('menu.changed', ({ restaurantId }) => queryClient.invalidateQueries({ queryKey: ['menu', restaurantId] }));
// On app foreground: refetchOnWindowFocus / AppState listener → revalidate stale queries
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you choose a TTL?**
A1: By the maximum staleness the business can tolerate for that data and how often it changes. Rarely changing catalog data gets minutes to hours (plus invalidation). Fast-changing but important data (availability, stock display) gets seconds. Must-be-exact data (balances at payment) isn't cached at all. Also consider hit ratio vs freshness, the cost of a miss, and add jitter to avoid synchronized expirations. TTL is also the safety net for missed invalidations, so always set one.

**Q2: What cache invalidation strategies do you know?**
A2: Explicit delete on write (update the DB, then delete the key). Event or CDC-driven invalidation from the DB change stream, which covers every writer. Versioned keys and namespace bumps, for bulk invalidation without scanning. Tag- or surrogate-key-based purges, for CDNs and page caches. Pub/sub broadcasts to clear in-process caches across instances. Time-based expiry and stale-while-revalidate. Often combined in layers.

**Q3: How do you invalidate data cached in multiple layers (Redis, CDN, browser)?**
A3: Invalidate from the innermost layer outward: DB, then Redis, then app L1 via pub/sub, then CDN purge by URL or tag, so outer layers refill from fresh data. Browser and mobile caches can't be purged remotely, so use short `max-age` with ETag revalidation, versioned URLs for static assets, and optionally push events (WebSocket or silent push) that tell clients to refetch. Never publicly cache user-specific responses.

**Q4: Why is cache invalidation considered hard?**
A4: Caches are distributed copies updated asynchronously. Race conditions (a stale value set after an invalidation), many write paths (admin tools, batch jobs, other services) that can forget to invalidate, derived or aggregated cached data (lists, search pages) that depend on many entities, multiple cache layers with different controls, network failures during invalidation, and ordering across regions all make it hard to guarantee that no stale value survives. TTLs, CDC and versioning reduce the risk.

**Q5: What is stale-while-revalidate and when is it useful?**
A5: A strategy where an expired (stale) cached response is served immediately while a background request refreshes it, so users never wait for the refresh and the origin gets a single revalidation instead of a stampede. It's supported in the HTTP `Cache-Control` header, CDNs, SWR and React Query, and server-side caches. Useful for data where slight staleness is fine (feeds, listings, profiles) and latency matters.

---

## 🔷 Trade-offs
✅ Long TTL: high hit ratio, low DB load — ❌ staler data.
✅ Short TTL: fresher — ❌ more misses, more DB load.
✅ Event invalidation: fresh + efficient — ❌ complexity, needs reliable event pipeline.
✅ Versioned keys: instant bulk invalidation — ❌ old keys waste memory until TTL.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TTL | Time a cache entry lives | cache में रहने का समय |
| Invalidation | Removing stale cache on change | बदलाव पर पुराना cache हटाना |
| Jitter | Random variation of TTL | TTL में थोड़ा random फ़र्क़ |
| Purge | Remove from CDN | CDN से हटाना |
| Surrogate key / tag | Label for group purge | समूह को हटाने का लेबल |
| Versioned key | Key with version number | version वाली key |
| Stale-while-revalidate | Serve stale, refresh in background | पुराना दिखाओ, पीछे ताज़ा करो |
| CDC | Change data capture | DB बदलाव की स्ट्रीम |
| ETag | Version identifier for HTTP response | जवाब का version |

---

## ⚡ 3-Line Summary
**English:**
1. TTL bounds staleness (choose by business tolerance, add jitter); invalidation removes stale data on change.
2. Strategies: delete-on-write, CDC/events, versioned keys, tag purges, pub/sub for L1, stale-while-revalidate.
3. Invalidate inside → out (DB → Redis → CDN); always set TTLs; never publicly cache private data.

**Hindi:**
1. TTL पुरानेपन की सीमा तय करता है (business के हिसाब से, jitter के साथ); invalidation बदलाव पर पुराना हटाता है।
2. तरीके: write पर delete, CDC/events, versioned keys, tag purge, pub/sub, stale-while-revalidate।
3. अंदर से बाहर साफ़ करो (DB → Redis → CDN); TTL हमेशा रखो; निजी डेटा public cache में कभी नहीं।

---

## ➡️ Next Topic Suggestion
**49. Cache Eviction (LRU/LFU)** — TTL removes data by time, but what happens when memory fills up before that? Next: eviction policies (LRU, LFU, FIFO, TTL-based), Redis maxmemory policies, and how to implement an LRU cache (a classic coding question).
