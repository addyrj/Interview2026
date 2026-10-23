# 18. Throughput
# हिंदी में: Throughput — सिस्टम एक सेकंड में कितने काम (requests) पूरे कर सकता है

---

## 🔵 Simple Definition (English)
**Throughput** is the **amount of work a system completes per unit of time**: requests per second (RPS/QPS), transactions per second (TPS), messages per second, or MB/s. It tells you **capacity**: how many users or operations the system can handle at once.

## 🔵 सरल परिभाषा (Hindi)
Throughput यानी सिस्टम एक सेकंड में कितनी requests या काम पूरे करता है (जैसे 5,000 requests/second)।
यह बताता है कि सिस्टम की क्षमता कितनी है।

---

## 🔴 Problem it Solves
Throughput is a **capacity metric**. You need it to answer:
- "Can our system handle the **IPL final / Diwali sale**?" (expected peak RPS vs our max RPS)
- "**How many servers** do we need?" (capacity planning, Topic 110)
- "Where is the **bottleneck**?" (the component with the lowest throughput limits the whole system)
- "Did the new release make us **slower**?" (load tests before vs after)

Without measuring throughput, you discover your limits **during the outage**.

## 🔴 यह क्यों बना? (Hindi)
Throughput से पता चलता है कि सेल या IPL के दिन सिस्टम संभलेगा या नहीं, कितने सर्वर चाहिए, और कौन-सा हिस्सा सबसे धीमा (bottleneck) है।
इसे पहले नहीं नापा तो सीमा outage के समय पता चलती है।

---

## 🟢 How it Works — Step by Step

### Pipe analogy

```
Latency    = how long water takes to travel the pipe
Throughput = how much water comes out per second
Bandwidth  = the pipe's maximum width (theoretical max)

  ═══════════════════════════►   wide pipe, short  → high throughput, low latency
  ────────────────────────────►   narrow pipe       → low throughput (bottleneck)
```

### The system is only as fast as its slowest part

```
Client ─► LB (50k rps) ─► API x4 (4 × 2k = 8k rps) ─► Postgres (3k qps) ─► 
                                                         ▲
                                         BOTTLENECK: system max ≈ 3k rps
Adding more API servers won't help. Fix the DB (cache, index, replicas).
```

### Little's Law (must know)

```
   L  =  λ  ×  W
   concurrency = throughput × latency

Example: API has 200 ms latency, we need 5,000 RPS.
   Concurrent in-flight requests = 5,000 × 0.2 = 1,000
   → need capacity for ~1,000 concurrent requests
     (e.g. DB pool / workers / connections sized for that)

Rearranged: throughput = concurrency / latency
   Fixed 100 DB connections, each query 10 ms → max 100 / 0.01 = 10,000 queries/s
   Same pool, queries become 50 ms → max 2,000 queries/s  ← slow queries kill throughput
```

### Throughput vs latency under load

```
 Throughput (rps)                         Latency (ms)
     │         ____________                   │                     /
     │       /   saturation                   │                   /
     │     /                                  │                 /
     │   /                                    │ ______________/
     │ /                                      │
     └──────────────── load                   └─────────────── load
Up to the "knee", more load = more throughput, latency flat.
Past it: throughput flat (or DROPS), latency explodes → queueing → timeouts → retries → worse.
Rule of thumb: run at ≤ 60–70% of max to keep headroom.
```

### Ways to increase throughput

```
1. Remove the bottleneck (profile first!)
2. Scale out stateless tiers (more instances)
3. Cache reads (Redis, CDN) → DB does less
4. Batch work: insert 1,000 rows in one query, not 1,000 queries
5. Async: queue + workers absorb spikes (throughput = number of workers)
6. Non-blocking I/O (Node event loop, async FastAPI) — don't block threads
7. Connection pooling, keep-alive
8. Efficient serialization (protobuf), compression
9. Partition/shard data so work runs in parallel (Kafka partitions, DB shards)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Throughput = प्रति सेकंड पूरे हुए काम; latency = एक काम का समय।
2. पूरा सिस्टम उतना ही तेज़ है जितना उसका सबसे धीमा हिस्सा (bottleneck)।
3. Little's Law: एक साथ चल रही requests = throughput × latency। Latency बढ़ी तो उन्हीं resources से throughput घटेगा।
4. एक सीमा के बाद load बढ़ाने से throughput नहीं बढ़ता, सिर्फ़ latency बढ़ती है — इसलिए 60-70% पर चलाओ।
5. बढ़ाने के तरीके: bottleneck हटाओ, scale out, cache, batching, queue + workers।

---

## 🟡 Real World Example

**UPI (NPCI)** — handles 13+ billion transactions a month in India. Peak throughput on festival days is in the thousands of TPS. Banks are required to meet throughput SLAs, and slow banks get throttled ("bank server down" errors are throughput limits being hit).

**IRCTC Tatkal booking at 10 AM** — a massive spike in a few minutes. Throughput is limited by the booking DB, so IRCTC uses queues and waiting screens plus captcha to smooth the load. That's throughput management.

**Kafka at LinkedIn** — Kafka was built at LinkedIn for very high throughput: trillions of messages per day, using sequential disk writes, batching, compression and partitioning.

**Twitter "fail whale" (2008–2010)** — Rails app throughput couldn't keep up with tweet spikes (World Cup), so the system collapsed. They moved hot paths to JVM services and added queues and caches.

## 🟡 Real Example Hindi में
UPI हर महीने 1300 करोड़ से ज़्यादा transactions संभालता है — त्योहारों पर प्रति सेकंड हज़ारों। "Bank server down" का मतलब अक्सर यही होता है कि बैंक का throughput भर गया।
IRCTC तत्काल में सुबह 10 बजे भारी भीड़ आती है, इसलिए queue और captcha से load को धीरे-धीरे अंदर भेजा जाता है।

---

## 🟠 My Stack Example

### Load test with k6 (find your max RPS)
```js
// load.js  →  k6 run load.js
import http from 'k6/http';
import { check } from 'k6';
export const options = {
  stages: [
    { duration: '1m', target: 100 },   // ramp to 100 virtual users
    { duration: '3m', target: 500 },
    { duration: '1m', target: 0 },
  ],
  thresholds: { http_req_duration: ['p(95)<300'], http_req_failed: ['rate<0.01'] },
};
export default function () {
  const r = http.get('https://staging-api.myapp.com/api/v1/products?limit=20');
  check(r, { '200': (res) => res.status === 200 });
}
```
Output shows `http_reqs ... 2350/s` (throughput) and `p(95)` latency. Increase load until p95 breaks the threshold — that's your practical max.
Quick alternative: `npx autocannon -c 100 -d 30 http://localhost:3000/health`.

### Batching = big throughput gains
```js
// ❌ 1,000 round trips
for (const e of events) await db.query('INSERT INTO events(user_id, type) VALUES ($1,$2)', [e.u, e.t]);

// ✅ 1 round trip
await db.query(
  `INSERT INTO events(user_id, type) SELECT * FROM unnest($1::int[], $2::text[])`,
  [events.map(e => e.u), events.map(e => e.t)]
);
```
```python
# Redis pipeline: 1,000 commands, 1 round trip
pipe = redis.pipeline()
for k, v in items: pipe.set(k, v, ex=300)
await pipe.execute()
```

### Don't block the event loop (kills Node throughput)
```js
// ❌ CPU-heavy work on main thread blocks ALL requests
app.post('/hash', (req, res) => res.send(bcrypt.hashSync(req.body.pw, 12)));

// ✅ async version (uses libuv thread pool) or a worker thread
app.post('/hash', async (req, res) => res.send(await bcrypt.hash(req.body.pw, 12)));
// Heavy jobs (PDF, image resize, reports) → queue (BullMQ) + separate worker processes
```
```python
# FastAPI: never call blocking libs inside async def
@app.get("/report")
async def report():
    return await run_in_threadpool(build_heavy_report)   # or Celery task
```

### Size pools with Little's Law
```
Target 2,000 RPS, avg DB time per request 15 ms
→ concurrent DB connections needed ≈ 2,000 × 0.015 = 30
→ across 4 API instances: pool max ≈ 8–10 each (+ headroom)
Postgres max_connections must cover ALL instances (use PgBouncer for many instances).
```

### Queue absorbs spikes (throughput smoothing)
```
Diwali sale: 20k orders/min arrive
API → put "send-invoice" jobs on SQS (fast)
Workers: 10 × 50 jobs/s = 500/s → backlog drains in ~1 min, DB never overloaded
```

---

## ⚫ Interview Questions + Answers

**Q1: Define throughput and how it relates to latency.**
A1: Throughput is operations completed per unit of time (RPS, TPS, MB/s). Latency is the time per operation. By Little's Law, concurrency = throughput × latency. With fixed concurrency (threads, connections), higher latency means lower throughput. Under overload, throughput plateaus while latency grows sharply because of queueing.

**Q2: How would you find the maximum throughput of your API?**
A2: Load test in a production-like environment with tools like k6, Gatling, JMeter or Locust, using realistic traffic mixes and data. Ramp up load while watching throughput, p95/p99 latency, error rate and resource metrics (CPU, DB connections, IOPS). The max sustainable throughput is the point just before latency or error thresholds are violated. Then identify the saturated component (the bottleneck).

**Q3: Adding more app servers didn't increase throughput. Why?**
A3: The bottleneck is elsewhere: the database (CPU, locks, connection limit, slow queries), a shared cache, a third-party API with rate limits, the load balancer, network bandwidth, or a global lock in code. More app servers can even reduce throughput by opening more DB connections and creating contention. Find the saturated resource and fix that: caching, indexes, read replicas, batching, or queueing.

**Q4: Explain Little's Law with an example.**
A4: L = λ × W, so average items in the system = arrival rate × average time in the system. If an API handles 1,000 req/s with 300 ms average latency, about 300 requests are in flight at any time, so the system needs capacity for roughly 300 concurrent requests (threads, connections, memory). It's used for sizing connection pools, worker counts and queue consumers.

**Q5: How can you increase write throughput to a database?**
A5: Batch inserts (multi-row inserts, COPY), use fewer, wider transactions, remove unnecessary indexes on write-heavy tables, use faster storage (higher IOPS), and tune commit settings where durability allows. Buffer writes through a queue and write in bulk (write-behind). Partition hot tables, and shard across multiple primaries when one node is saturated. Use append-only designs or a store optimized for writes (Cassandra, time-series DBs) for event or log data.

---

## 🔷 Trade-offs
✅ Higher throughput via batching/queues/async:
- Handles more users per server → lower cost; absorbs spikes.

❌ But:
- Batching and queueing increase **latency** for individual items.
- Async processing = eventual consistency and more moving parts.
- Running near max throughput leaves no headroom → small spikes cause big latency jumps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Throughput | Work completed per second | प्रति सेकंड पूरा काम |
| RPS / QPS / TPS | Requests / queries / transactions per second | प्रति सेकंड requests |
| Bottleneck | Slowest component limiting system | सबसे धीमा हिस्सा |
| Little's Law | Concurrency = throughput × latency | एक साथ requests = throughput × समय |
| Saturation | Resource fully used | पूरी तरह भरा हुआ |
| Load test | Simulating traffic to find limits | नक़ली ट्रैफ़िक से सीमा जाँचना |
| Batching | Grouping many operations into one | कई काम एक साथ |
| Headroom | Spare capacity for spikes | अतिरिक्त क्षमता |

---

## ⚡ 3-Line Summary
**English:**
1. Throughput = work per second (RPS/TPS); the slowest component decides system throughput.
2. Little's Law: concurrency = throughput × latency — slow calls reduce throughput with fixed resources.
3. Increase it by removing bottlenecks, scaling out, caching, batching, async queues — and load test to know your limit.

**Hindi:**
1. Throughput = प्रति सेकंड काम; सबसे धीमा हिस्सा पूरी क्षमता तय करता है।
2. Little's Law: एक साथ requests = throughput × latency।
3. बढ़ाने के लिए bottleneck हटाओ, cache, batching, queue — और load test से अपनी सीमा जानो।

---

## ➡️ Next Topic Suggestion
**19. Availability** — Fast and high-capacity is useless if the system is down. Next: what "99.99% uptime" really means, how to calculate availability of a chain of components, and how redundancy improves it.
