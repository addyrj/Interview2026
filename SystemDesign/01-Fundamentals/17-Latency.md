# 17. Latency
# हिंदी में: Latency — किसी request को भेजने से जवाब मिलने तक लगने वाला समय (देरी)

---

## 🔵 Simple Definition (English)
**Latency** is the **time delay** for one operation: how long it takes for a request to travel to the server, get processed, and the response to come back. It's measured in milliseconds (ms). Lower is better.
We measure it with **percentiles** (p50, p95, p99), not averages.

## 🔵 सरल परिभाषा (Hindi)
Latency यानी देरी — बटन दबाने से जवाब आने तक कितना समय लगा। इसे milliseconds में नापते हैं।
औसत (average) की जगह p95, p99 देखते हैं, ताकि सबसे धीमे यूज़र्स का अनुभव भी पता चले।

---

## 🔴 Problem it Solves
Latency is a **metric**, not a technology, but understanding it solves real business problems:
- Users leave slow apps: Google found that **53% of mobile users abandon** a site that takes over 3 s to load. Amazon found that **100 ms of extra latency cost about 1% of sales**.
- **Averages lie:** an average of 100 ms can hide 5% of users waiting 3 seconds. Those are often your heaviest users (big carts, many orders).
- You need to know **where** latency comes from in order to fix the right thing.

## 🔴 यह क्यों बना? (Hindi)
धीमा ऐप = यूज़र चले जाते हैं। 3 सेकंड से ज़्यादा लगे तो आधे से ज़्यादा मोबाइल यूज़र साइट छोड़ देते हैं; Amazon में 100 ms की देरी से 1% बिक्री घटती है।
औसत धोखा देता है — इसलिए p99 देखो और पता करो देरी कहाँ से आ रही है।

---

## 🟢 How it Works — Step by Step

### Components of latency

```
Total latency = Network + Queueing + Processing + Downstream calls + Serialization

Client ──► [ Network: propagation + transmission ] ──► Server
            ~ distance / speed of light in fiber (~200 km/ms)
            Mumbai → Delhi (~1,400 km): ~7 ms one-way minimum
            Mumbai → US East: ~100 ms one-way

Server:  [ waiting in queue ] → [ CPU work ] → [ DB 5ms ] → [ Redis 1ms ] → [ ext API 300ms ]
                 ▲                                                               ▲
          high when overloaded                                        often the biggest part
```

### Latency numbers every engineer should know (approx.)

```
L1 cache reference                         1 ns
RAM access                               100 ns
Read 1 MB sequentially from RAM          ~10 µs
SSD random read                         ~100 µs
Redis GET (same AZ, network)            ~0.5–1 ms
Postgres indexed query (same AZ)          1–5 ms
Round trip within same data center       ~0.5 ms
Round trip Mumbai ↔ Singapore             ~60 ms
Round trip Mumbai ↔ US East             ~200 ms
4G mobile RTT                           50–100 ms   (3G: 200–500 ms)
HDD seek                                  ~10 ms

Takeaway: memory ≫ SSD ≫ network ≫ cross-continent.  Cache in memory; keep calls in-region.
```

### Percentiles — why p99 matters

```
100 requests sorted by time:
  p50 (median) = 80 ms   → half the users are faster than this
  p95          = 250 ms  → 95% faster; 5 in 100 are slower
  p99          = 1,200 ms→ 1 in 100 waits > 1.2 s
  average      = 110 ms  ← hides the tail completely

Tail at scale: a page that calls 10 services in parallel waits for the SLOWEST one.
If each has p99 = 1 s, then ~10% of page loads hit at least one 1 s call.
→ Optimise tail latency, not just average.
```

### Latency vs Throughput (next topic)

```
Latency    = how long ONE request takes        (ms)
Throughput = how many requests per second      (req/s)
Highway analogy: latency = travel time for one car; throughput = cars per hour.
Under overload, throughput flattens and latency SHOOTS UP (queues build).

 latency
   │                            /
   │                          /
   │                        /
   │ ____________________ /        ← "knee": stay below ~70% utilization
   └──────────────────────────── load
```

### How to reduce latency — the toolbox

```
1. Move closer to users        → CDN, edge, region choice (ap-south-1 for India)
2. Avoid the work              → cache (browser, CDN, Redis), precompute
3. Do less per request         → indexes, select only needed columns, pagination
4. Fewer round trips           → batch APIs, GraphQL/BFF, HTTP/2, keep-alive, connection pooling
5. Do work in parallel         → Promise.all / asyncio.gather for independent calls
6. Do work later               → queues for emails, notifications, analytics
7. Smaller payloads            → gzip/brotli, compressed images, protobuf
8. Faster protocol             → HTTP/2, HTTP/3, TLS 1.3, gRPC internally
9. Protect the tail            → timeouts, hedged requests, circuit breakers, avoid GC pauses
10. Perceived latency (UI)     → skeleton screens, optimistic updates, prefetch
```

## 🟢 कैसे काम करता है? (Hindi)
1. कुल देरी = Network का समय + queue में इंतज़ार + सर्वर का काम + DB/बाहरी API का समय।
2. दूरी मायने रखती है — मुंबई से अमेरिका जाने-आने में ~200 ms सिर्फ़ रास्ते में लगते हैं।
3. Memory सबसे तेज़, फिर SSD, फिर network — इसलिए cache करो।
4. Average नहीं, p95/p99 देखो — सबसे धीमे 1% यूज़र का अनुभव भी ज़रूरी है।
5. कम करने के तरीके: CDN, cache, index, कम round trips, parallel calls, धीमे काम queue में।

---

## 🟡 Real World Example

**Google Search** — they found that adding 500 ms to search results reduced traffic by 20%. Search results pages are aggressively optimized: inlined critical CSS, prefetching, edge servers in ISPs.

**Zerodha / stock trading** — latency means money. Order placement paths are kept extremely short, run in-memory, and are co-located near the exchange (NSE colocation) where microseconds matter.

**Swiggy home screen** — the home screen is assembled by a backend aggregator that calls many services (restaurants, offers, recommendations) **in parallel** with strict per-call timeouts. If recommendations are slow, the section is skipped instead of making the whole screen wait (graceful degradation).

**Amazon** — "every 100 ms of latency cost 1% of sales", the most quoted latency stat in interviews.

## 🟡 Real Example Hindi में
Google ने पाया कि search में 500 ms देरी से ट्रैफ़िक 20% घट गया। Zerodha में ट्रेडिंग के लिए microseconds भी मायने रखते हैं, इसलिए सर्वर NSE के पास ही रखे जाते हैं।
Swiggy की home screen कई services को एक साथ (parallel) कॉल करती है, और कोई धीमी हो तो उसका हिस्सा छोड़ देती है ताकि पूरी स्क्रीन न अटके।

---

## 🟠 My Stack Example

### Parallel instead of sequential (huge, easy win)
```js
// ❌ Sequential: 120 + 80 + 150 = 350 ms
const user = await getUser(id);
const orders = await getOrders(id);
const offers = await getOffers(id);

// ✅ Parallel: max(120, 80, 150) = 150 ms
const [user, orders, offers] = await Promise.all([getUser(id), getOrders(id), getOffers(id)]);

// ✅ Parallel + tolerate slow optional parts
const [userR, ordersR, offersR] = await Promise.allSettled([
  getUser(id), getOrders(id), withTimeout(getOffers(id), 200),
]);
const offers = offersR.status === 'fulfilled' ? offersR.value : [];   // degrade gracefully
```
```python
# FastAPI
user, orders, offers = await asyncio.gather(get_user(id), get_orders(id), get_offers(id))
```

### Cache the hot read (Redis ~1 ms vs Postgres join ~40 ms)
```js
async function getMenu(restaurantId) {
  const key = `menu:${restaurantId}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);
  const menu = await db.query('SELECT ... FROM items WHERE restaurant_id=$1', [restaurantId]);
  await redis.set(key, JSON.stringify(menu.rows), { EX: 300 });
  return menu.rows;
}
```

### Measure latency properly (histograms → percentiles)
```js
import client from 'prom-client';
const httpLatency = new client.Histogram({
  name: 'http_request_duration_seconds', help: 'latency', labelNames: ['route', 'method', 'status'],
  buckets: [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
});
app.use((req, res, next) => {
  const end = httpLatency.startTimer();
  res.on('finish', () => end({ route: req.route?.path ?? req.path, method: req.method, status: res.statusCode }));
  next();
});
// Grafana: histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, route))
```

### Find slow SQL
```sql
-- enable pg_stat_statements, then:
SELECT query, calls, mean_exec_time, max_exec_time
FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 42 ORDER BY created_at DESC LIMIT 20;
-- "Seq Scan" on a big table → add index (user_id, created_at DESC)
```

### Frontend / mobile: reduce perceived latency
```tsx
// React Query: show cached data instantly, refetch in background
const { data } = useQuery({ queryKey: ['orders'], queryFn: fetchOrders, staleTime: 30_000 });

// Optimistic update: UI changes before server confirms
const mutation = useMutation({
  mutationFn: likePost,
  onMutate: async (id) => { queryClient.setQueryData(['post', id], (p) => ({ ...p, liked: true, likes: p.likes + 1 })); },
  onError: (_e, id) => queryClient.invalidateQueries({ queryKey: ['post', id] }),
});

// Next.js: prefetch the next page on hover/viewport (<Link> does it automatically)
```
- RN: show a **skeleton** while loading, cache images (`expo-image`), and prefetch the next screen's data on press-in.

### Server-Timing header → see backend breakdown in Chrome DevTools
```js
res.setHeader('Server-Timing', `db;dur=${dbMs}, cache;dur=${cacheMs}, total;dur=${totalMs}`);
```

---

## ⚫ Interview Questions + Answers

**Q1: What is latency and how is it different from throughput?**
A1: Latency is the time to complete one operation (ms). Throughput is how many operations complete per unit of time (req/s). They're related but different. A system can have high throughput with high latency (batch processing) or low latency with low throughput. Under overload, queueing makes latency rise sharply while throughput plateaus.

**Q2: Why do we use p95/p99 instead of average latency?**
A2: Latency distributions have long tails. The average hides slow outliers, and a few very slow requests can be severe user pain. Percentiles show what X% of users experience. p99 matters especially when one user action fans out into many backend calls, because the chance of hitting at least one slow call grows with the fan-out ("tail at scale"). SLOs are usually defined on p95/p99.

**Q3: How would you reduce the latency of an API that takes 2 seconds?**
A3: Measure first, with tracing or APM, and break the 2 s down by span. Common fixes: add missing DB indexes and avoid N+1 queries; cache hot reads in Redis; run independent calls in parallel; add timeouts and fallbacks for slow third-party calls, or move them async; reduce payload size and compress; reuse connections (pooling, keep-alive); move compute closer to users (region, CDN). Re-measure p95/p99 after each change.

**Q4: Your servers are in Mumbai. Users in the US complain the app is slow. What do you do?**
A4: Physics: each round trip is about 200 ms, and a page load needs many. Short term: put static assets and cacheable API responses on a CDN, terminate TLS at the edge, reduce round trips (batching, HTTP/2/3, keep-alive) and cache on the client. Long term: deploy app servers in a US region with read replicas or a geo-distributed DB, and route with latency-based DNS. Writes might still go to the primary region, or you go multi-region active-active if the business needs it.

**Q5: What is the difference between actual latency and perceived latency? How do you improve the latter?**
A5: Actual latency is measured time; perceived latency is how fast it feels. UX techniques reduce perceived latency: skeleton screens instead of spinners, optimistic updates, showing cached or stale data first and refreshing in the background (stale-while-revalidate), progressive rendering and streaming (SSR streaming, LLM token streaming), prefetching likely next screens, and instant feedback on tap.

---

## 🔷 Trade-offs
✅ Lower latency brings:
- Better UX, conversion, retention, SEO (Core Web Vitals).

❌ Costs of chasing low latency:
- Caching → staleness and invalidation complexity.
- Multi-region / edge → higher cost and data consistency problems.
- Parallel calls / hedged requests → more load on backends.
- Over-optimizing p50 while ignoring p99 → wrong focus.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Latency | Time for one operation | एक काम में लगा समय |
| RTT | Round trip time | जाने-आने का समय |
| p50 / p95 / p99 | % of requests faster than value | कितने % request इससे तेज़ |
| Tail latency | Slowest requests (p99+) | सबसे धीमे request |
| Propagation delay | Time due to physical distance | दूरी की वजह से देरी |
| Queueing delay | Time waiting to be processed | लाइन में इंतज़ार |
| TTFB | Time to first byte | पहला बाइट आने का समय |
| Perceived latency | How fast it feels to user | यूज़र को कितना तेज़ लगता है |

---

## ⚡ 3-Line Summary
**English:**
1. Latency = time for one request; measure p50/p95/p99, never just average.
2. It comes from network distance, queueing, processing and downstream calls — memory ≫ disk ≫ network.
3. Reduce it with CDN/region, caching, indexes, parallel calls, fewer round trips, async side effects, and UX tricks.

**Hindi:**
1. Latency = एक request का समय; p95/p99 नापो, सिर्फ़ औसत नहीं।
2. देरी दूरी, queue, processing और बाहरी कॉल से आती है।
3. कम करो: CDN, cache, index, parallel calls, कम round trips, धीमे काम queue में।

---

## ➡️ Next Topic Suggestion
**18. Throughput** — Latency is speed for one user. Next: throughput, how MANY requests your system can handle per second, how to measure it with load tests, and how it relates to latency and concurrency (Little's Law).
