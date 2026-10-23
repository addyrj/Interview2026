# 76. Bulkhead Pattern
# हिंदी में: Bulkhead — जहाज़ के अलग-अलग पानी-रोधी कमरों की तरह, सिस्टम के resources (connections, threads, servers) को हिस्सों में बाँटना, ताकि एक हिस्से की ख़राबी पूरे सिस्टम को न डुबाए

---

## 🔵 Simple Definition (English)
The **bulkhead pattern** isolates resources into **separate pools/compartments** per dependency, feature, or customer, so that a failure or overload in one compartment **can't exhaust resources** needed by others. The name comes from ships, whose hulls are divided into watertight compartments (bulkheads): one flooded compartment doesn't sink the ship.
Examples: separate connection pools per downstream service, separate worker queues per job type, separate instances for critical vs non-critical traffic, per-tenant limits.

## 🔵 सरल परिभाषा (Hindi)
Bulkhead में resources को अलग-अलग डिब्बों में बाँटते हैं — हर बाहरी service का अलग connection pool, हर तरह के job का अलग worker, ज़रूरी और ग़ैर-ज़रूरी ट्रैफ़िक के अलग सर्वर।
जैसे जहाज़ का एक कमरा पानी से भर जाए तो भी जहाज़ नहीं डूबता — वैसे ही एक हिस्सा गिरे तो बाक़ी सिस्टम चलता रहे।

---

## 🔴 Problem it Solves
Shared resources create **shared fate**:
```
API server: one shared pool of 100 outbound connections / 200 worker threads / one event loop
Maps API becomes slow (10s) → all 100 connections are stuck waiting on Maps
→ Payment calls can't get a connection → checkout fails ❌
→ even /health and login time out → whole service looks dead
```
Other examples:
- One **heavy report** query consumes all DB connections and users can't log in.
- One **noisy tenant** in a SaaS floods the queue and every other customer's jobs wait.
- **Image processing** jobs starve **OTP SMS** jobs in a shared queue.

Bulkheads **cap the blast radius** of a failure.

## 🔴 यह क्यों बना? (Hindi)
साझा resources का मतलब साझा मुसीबत: Maps API धीमी हुई तो सारे connections उसी में अटक गए, और पेमेंट या login को connection ही नहीं मिला — पूरी service डाउन।
भारी रिपोर्ट सारे DB connections खा ले, या एक बड़ा ग्राहक पूरी queue भर दे — bulkhead हर हिस्से की सीमा तय करके नुक़सान को एक जगह रोक देता है।

---

## 🟢 How it Works — Step by Step

### Without vs with bulkheads

```
WITHOUT (shared pool of 100)              WITH bulkheads
┌─────────────────────────────┐           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ ██████████████████████████  │           │ Payments: 40 │ │ Maps: 20     │ │ Reco: 20     │
│ all 100 stuck on slow Maps  │           │ ✅ healthy    │ │ ███ all stuck│ │ ✅ healthy    │
└─────────────────────────────┘           └──────────────┘ └──────────────┘ └──────────────┘
Payments starved ❌                        Maps failure contained; payments unaffected ✅
```

### Levels of bulkheads

```
1. Code level:      separate HTTP agents / connection pools / semaphores per dependency
2. Process level:   separate worker processes / thread pools per job type
3. Queue level:     separate queues (critical: OTP, payments; bulk: emails, reports)
4. Service level:   separate deployments for critical vs non-critical endpoints
                    (e.g. checkout pods vs browsing pods; admin/reporting on separate instances)
5. Data level:      separate DB/replica for analytics; separate Redis for cache vs queues
6. Tenant level:    per-customer limits, shuffle sharding, dedicated cells for big tenants
7. Infra level:     cells / multiple clusters / AZs — "cell-based architecture"
```

### Semaphore (concurrency limit) bulkhead
```
maxConcurrent(maps) = 20, maxQueue = 50
request 1..20  → run
request 21..70 → wait in queue (short timeout)
request 71+    → rejected immediately (fail fast / fallback)
```

### Cell-based architecture (big-scale bulkheads)
```
Users are split into independent "cells" (full copies of the stack serving a subset of users):
  Cell 1: users A–F    Cell 2: users G–M    Cell 3: ...
A bad deploy or overload in Cell 2 affects only its users. Deploy cell by cell.
(AWS, Slack, DoorDash, Salesforce use cells.)

Shuffle sharding (AWS Route 53): each customer is assigned a random small SET of workers;
two customers rarely share the exact same set → one bad customer impacts very few others.
```

### Bulkhead + other patterns
```
Bulkhead     → limits HOW MUCH a dependency can consume (space isolation)
Timeout      → limits HOW LONG each call holds resources
Circuit breaker → stops calling when it's failing
Load shedding → drops excess when overall capacity is exceeded
Together they prevent cascading failure.
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर बाहरी dependency के लिए अलग सीमा रखो — Payments के 40 connections, Maps के 20, Recommendations के 20।
2. Maps धीमी हो तो सिर्फ़ उसके 20 अटकेंगे; पेमेंट पर कोई असर नहीं।
3. Jobs की अलग queues: ज़रूरी (OTP, payments) और भारी (emails, reports) — ताकि भारी काम ज़रूरी काम को न रोकें।
4. बड़े स्तर पर: ज़रूरी endpoints के अलग pods, analytics के लिए अलग DB, cache और queue के लिए अलग Redis।
5. सबसे बड़े सिस्टम "cells" बनाते हैं — यूज़र्स के समूहों के लिए पूरी अलग copies, ताकि गड़बड़ी सिर्फ़ एक cell तक रहे।

---

## 🟡 Real World Example

**Netflix Hystrix** — each dependency call ran in its own thread pool (or semaphore) with a fixed size. If the "ratings" service hung, only its thread pool filled up, and the rest of the API kept serving. This is the textbook bulkhead.

**AWS cell-based architecture & shuffle sharding** — AWS services (Route 53, Lambda, DynamoDB internals) partition customers into cells and use shuffle sharding so one customer's bad traffic (or a poison request) affects only a tiny fraction of other customers.

**Slack (2022+)** — moved toward cellular architecture after AZ-level incidents, so traffic can be drained from a sick cell or AZ without impacting the whole service.

**Swiggy / Zomato** — separate services and pods for order placement vs browsing and search. During a huge sale, browsing can degrade while checkout capacity is protected.

## 🟡 Real Example Hindi में
Netflix Hystrix में हर dependency का अपना thread pool था — "ratings" service अटकी तो सिर्फ़ उसका pool भरा, बाक़ी API चलती रही।
AWS यूज़र्स को "cells" में बाँटता है और shuffle sharding इस्तेमाल करता है, ताकि एक ग्राहक की ख़राब traffic बाक़ियों पर असर न डाले। Swiggy में ऑर्डर और browsing के अलग pods होते हैं।

---

## 🟠 My Stack Example

### Node.js — separate HTTP agents (connection pools) per dependency
```js
import { Agent } from 'undici';
const agents = {
  payments: new Agent({ connections: 40, keepAliveTimeout: 30_000 }),
  maps:     new Agent({ connections: 20 }),
  reco:     new Agent({ connections: 20 }),
};
const call = (dep, url, opts = {}) =>
  fetch(url, { ...opts, dispatcher: agents[dep], signal: AbortSignal.timeout(opts.timeoutMs ?? 2000) });
```

### Concurrency-limit bulkhead (semaphore) with p-limit / Bottleneck
```js
import Bottleneck from 'bottleneck';
const mapsBulkhead = new Bottleneck({ maxConcurrent: 20, highWater: 50, strategy: Bottleneck.strategy.OVERFLOW });
// beyond 20 running + 50 queued → new jobs dropped immediately

async function getEta(o, d) {
  try {
    return await mapsBulkhead.schedule({ expiration: 2000 }, () => call('maps', `${MAPS}/eta?o=${o}&d=${d}`).then(r => r.json()));
  } catch {
    return estimateEtaByDistance(o, d);       // fallback when bulkhead is full or call fails
  }
}
```

### Separate DB pools: user traffic vs reports
```js
export const appPool    = new pg.Pool({ connectionString: PRIMARY_URL, max: 20 });          // OLTP
export const reportPool = new pg.Pool({ connectionString: REPLICA_URL, max: 5, statement_timeout: 60_000 }); // heavy, isolated
```

### Separate queues & workers (BullMQ)
```js
const critical = new Queue('critical', { connection });   // OTP, payment webhooks
const bulk     = new Queue('bulk', { connection });       // marketing emails, report PDFs, image resize

new Worker('critical', handleCritical, { connection, concurrency: 50 });
new Worker('bulk', handleBulk, { connection, concurrency: 5, limiter: { max: 100, duration: 1000 } });
// Deploy as separate containers → a flood of bulk jobs can't delay OTPs
```

### Per-tenant bulkhead (SaaS)
```js
const tenantLimiters = new Map();
const limiterFor = (t) => tenantLimiters.get(t) ?? tenantLimiters.set(t, new Bottleneck({ maxConcurrent: 10 })).get(t);
app.use('/api', (req, res, next) => limiterFor(req.tenantId).schedule(() => new Promise((done) => { res.on('finish', done); next(); })));
```

### FastAPI — asyncio.Semaphore per dependency
```python
maps_sem = asyncio.Semaphore(20)

async def eta(o, d):
    if maps_sem.locked():                       # all 20 slots busy → fail fast
        return estimate_by_distance(o, d)
    async with maps_sem:
        async with httpx.AsyncClient(timeout=2) as c:
            return (await c.get(MAPS_URL, params={"o": o, "d": d})).json()["eta"]
```

### Kubernetes — service-level bulkheads
```yaml
# Separate Deployments with their own HPA & resource limits
checkout-api:  replicas 10, cpu 1, priorityClassName: critical
browse-api:    replicas 20, cpu 0.5
admin-reports: replicas 2,  cpu 2, separate node pool
# Istio connectionPool limits per destination = network-level bulkhead
```

### Redis separation
```
redis-cache  (allkeys-lru)  → can evict freely
redis-queue  (noeviction)   → BullMQ jobs, never evicted
redis-session                → logins
A cache memory blow-up can't delete your job queue.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the bulkhead pattern?**
A1: Isolating resources into separate pools per dependency, workload type or tenant, so a failure or overload in one can't consume the resources others need. Examples: separate connection or thread pools per downstream service, separate queues and workers for critical vs bulk jobs, separate deployments for checkout vs browsing, separate DBs or replicas for analytics, and per-tenant concurrency limits.

**Q2: How does a bulkhead differ from a circuit breaker?**
A2: A bulkhead limits how much of your resources a dependency or workload can occupy at once (concurrency or capacity isolation), so even while a dependency is slow, the damage is contained. A circuit breaker decides whether to call a dependency at all, based on its recent failure rate, and stops calls when it's unhealthy. They complement each other: the bulkhead protects while failures accumulate, and the breaker then stops the calls entirely.

**Q3: Give examples of bulkheads at different levels.**
A3: Code: separate HTTP agents or semaphores per external API. Process: separate thread or worker pools. Queue: critical vs bulk queues with dedicated workers. Service: separate pods or deployments for critical endpoints and admin or reporting. Data: an OLTP primary vs a reporting replica, a cache Redis vs a queue Redis. Tenant: per-customer quotas and dedicated cells for big customers. Infrastructure: cell-based architecture and multi-AZ isolation.

**Q4: What is cell-based architecture?**
A4: Partitioning the whole system into multiple independent, identical "cells", each a complete stack (services, data) serving a subset of users or tenants, routed by a thin global layer. A failure, bad deploy or overload is limited to one cell's users, deployments roll out cell by cell, and capacity scales by adding cells. AWS, Slack, DoorDash and Salesforce use it. Shuffle sharding further reduces the overlap between customers' resources.

**Q5: How do you size bulkhead pools?**
A5: From the dependency's capacity and your traffic share, using Little's Law: needed concurrency = RPS × latency. For example, 100 RPS × 200 ms = 20 concurrent calls, plus headroom. Make critical dependencies' pools generous and non-critical ones tight. Add a small queue with short timeouts and reject beyond it. Monitor pool saturation and rejections and tune. Ensure the sum across pools doesn't exceed shared limits (DB max_connections, file descriptors).

---

## 🔷 Trade-offs
✅ Advantages:
- Contains failures (smaller blast radius), protects critical paths, fair multi-tenancy.

❌ Disadvantages:
- Lower resource utilization (idle capacity in some pools).
- More configuration and tuning; more deployments/queues to operate.
- Pools sized wrong can cause unnecessary rejections.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bulkhead | Resource isolation compartment | resources का अलग डिब्बा |
| Blast radius | Scope of impact of a failure | ख़राबी का फैलाव |
| Connection pool | Reusable connections per dependency | कनेक्शनों का समूह |
| Semaphore | Concurrency limiter | एक साथ कामों की सीमा |
| Noisy neighbor | One tenant hurting others | दूसरों को परेशान करने वाला ग्राहक |
| Cell | Independent full-stack partition | पूरी अलग copy |
| Shuffle sharding | Random worker subsets per customer | हर ग्राहक के लिए random workers |
| Priority queue | Separate queue for critical jobs | ज़रूरी कामों की अलग queue |

---

## ⚡ 3-Line Summary
**English:**
1. Bulkheads isolate resources (pools, queues, instances, cells) so one failing part can't exhaust shared capacity.
2. Apply per dependency, job type, endpoint criticality and tenant; size with Little's Law; reject/fallback when full.
3. Combine with timeouts, circuit breakers and load shedding to stop cascading failures.

**Hindi:**
1. Bulkhead = resources को अलग डिब्बों में बाँटना, ताकि एक हिस्से की ख़राबी सब न खा जाए।
2. हर dependency, job प्रकार, ज़रूरी endpoint और ग्राहक के लिए अलग सीमा; भरने पर मना/fallback।
3. Timeout, circuit breaker और load shedding के साथ मिलकर cascading failure रोको।

---

## ➡️ Next Topic Suggestion
**77. Graceful Degradation** — When parts fail, the product should still work in a reduced form. Next: designing "degraded modes" (cached data, disabled features, static fallbacks) so users can still do the most important things.
