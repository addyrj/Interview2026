# 78. Load Shedding
# हिंदी में: Load Shedding — क्षमता से ज़्यादा ट्रैफ़िक आने पर कुछ (कम ज़रूरी) requests को जानबूझकर तुरंत मना कर देना, ताकि बाक़ी requests सही से चल सकें और सिस्टम न गिरे

---

## 🔵 Simple Definition (English)
**Load shedding** means **intentionally rejecting or dropping some requests** when a service is **overloaded**, so it can keep serving the rest **within acceptable latency**. Instead of accepting everything and becoming slow for everyone (then crashing), the service returns **fast failures (503/429)** for excess, preferably **low-priority**, traffic.
Like electricity boards cutting power to some areas to save the whole grid.

## 🔵 सरल परिभाषा (Hindi)
Load shedding यानी सर्वर पर क्षमता से ज़्यादा ट्रैफ़िक हो तो कुछ requests को तुरंत मना (503) कर देना — ख़ासकर कम ज़रूरी वाली — ताकि बाक़ी requests तेज़ी से चलें।
जैसे बिजली विभाग पूरा grid बचाने के लिए कुछ इलाक़ों की बिजली काटता है।

---

## 🔴 Problem it Solves
When load exceeds capacity, systems don't degrade linearly. They **collapse**:
```
Capacity: 1,000 req/s.  Incoming: 1,500 req/s
→ queues grow → latency rises from 50ms to 10s → clients time out at 5s
→ server keeps doing work for requests whose clients already gave up (wasted!)
→ clients RETRY → 3,000 req/s → memory exhausted → crash → 0 req/s served ❌ (goodput collapse)
```
Rejecting the excess 500 req/s **immediately** (which costs microseconds) lets the server serve **1,000 req/s at normal latency**. **Goodput** (useful completed work) stays high.

## 🔴 यह क्यों बना? (Hindi)
क्षमता से ज़्यादा ट्रैफ़िक पर सिस्टम धीरे-धीरे नहीं, अचानक गिरता है: queue बढ़ती है, latency 10 सेकंड, clients timeout होकर retry करते हैं, बोझ दुगुना, सर्वर crash — और फिर कोई request पूरी नहीं होती।
ज़्यादा requests तुरंत मना करने से बाक़ी 1000 requests/सेकंड सामान्य रफ़्तार से पूरी होती रहती हैं।

---

## 🟢 How it Works — Step by Step

### Goodput vs load

```
 useful work
 (goodput)           with load shedding
     │          ______________________________
     │         /
     │        /    without load shedding
     │       /\
     │      /  \____
     │     /        \_______  ← collapse
     └──────────────────────────── offered load
           capacity
```

### Signals to decide when to shed

```
- Concurrency / in-flight requests > limit (best, simple)          e.g. > 200 in flight
- Queue length or queue wait time > threshold                      e.g. waited > 100 ms
- Latency (p99) above target
- CPU / memory / event-loop lag (Node) above threshold             e.g. loop lag > 200 ms
- Downstream saturation (DB pool waiting count)
- Adaptive concurrency limits (TCP-Vegas-like, Netflix concurrency-limits) — auto-tune the limit
```

### What to shed first — prioritization

```
Priority 0 (never shed):  health checks, payments/checkout, login, order status
Priority 1:               browsing, menu, cart
Priority 2:               search suggestions, recommendations
Priority 3 (shed first):  analytics/telemetry ingestion, prefetch, background sync, crawlers/bots
Identify priority via route, header (X-Priority set by gateway/BFF), user tier, client type.
Prefer shedding NEW sessions over in-progress ones (don't break a checkout midway).
```

### Where to shed
```
Edge/CDN/WAF       → bot traffic, waiting rooms (virtual queue for ticket sales)
API gateway / LB   → global rate limits, per-route concurrency caps
Each service       → in-flight limit middleware → 503 + Retry-After (fast, cheap)
Queues/workers     → drop or defer low-priority jobs, TTL on messages (stale work is useless)
Client             → back off on 503/429, stop prefetching
```

### Important details
```
✓ Reject EARLY and CHEAPLY (before parsing big bodies, before DB calls)
✓ Use deadlines: if a request has already waited longer than the client timeout → drop it
  (work for a client who left is pure waste) — "deadline propagation"
✓ Return 503 (or 429) + Retry-After so well-behaved clients back off (with jitter)
✓ LIFO under overload can serve fresh requests first (old ones likely timed out) — used by some systems
✓ Monitor shed rate; alert; autoscale in parallel (shedding buys time, not capacity)
```

### Load shedding vs rate limiting
```
Rate limiting: per-CLIENT fairness limits ("user X ≤ 100/min") even when system is healthy
Load shedding: protects the SERVICE when total load > capacity, regardless of who sends it
Both return 429/503; often used together.
```

## 🟢 कैसे काम करता है? (Hindi)
1. सर्वर अपनी हालत देखता है: अभी कितनी requests चल रही हैं, queue में कितना इंतज़ार, CPU, event-loop lag।
2. सीमा पार → नई requests को तुरंत (सस्ते में) 503 + `Retry-After` — DB या भारी काम से पहले ही।
3. पहले कम ज़रूरी ट्रैफ़िक हटाओ (analytics, recommendations, bots), पेमेंट/login/health check कभी नहीं।
4. जो request client के timeout से ज़्यादा इंतज़ार कर चुकी, उसे छोड़ दो — उसका जवाब कोई नहीं सुनेगा।
5. Shedding समय ख़रीदता है, क्षमता नहीं — साथ में autoscaling और alerts।

---

## 🟡 Real World Example

**Google** — services estimate each request's cost and shed by criticality ("CRITICAL_PLUS, CRITICAL, SHEDDABLE"), propagating the criticality across RPCs, as described in the Google SRE book's chapter on handling overload.

**Netflix** — uses adaptive concurrency limits and prioritized load shedding at its Zuul gateway: during overload it sheds non-critical requests (prefetch, logging) before playback requests, so users can keep watching.

**Stripe** — runs multiple limiters, including a "fleet usage load shedder" that reserves capacity for critical requests (like charge creation) and sheds lower-priority traffic during spikes.

**Ticket sales (BookMyShow, IRCTC, Coldplay)** — virtual waiting rooms are edge-level load shedding: users are queued and admitted at the rate the backend can handle, instead of everyone hitting checkout at once.

## 🟡 Real Example Hindi में
Google हर request की "ज़रूरत" (CRITICAL, SHEDDABLE) तय करता है और भीड़ में पहले कम ज़रूरी हटाता है। Netflix भीड़ में prefetch/logging हटाता है, पर वीडियो चलने वाली requests नहीं।
BookMyShow/IRCTC का waiting room भी load shedding है — लोगों को लाइन में रखकर उतनी ही रफ़्तार से अंदर भेजते हैं जितना सर्वर संभाल सके।

---

## 🟠 My Stack Example

### Node.js — in-flight limit + event-loop lag + priority
```js
import { monitorEventLoopDelay } from 'node:perf_hooks';
const loop = monitorEventLoopDelay({ resolution: 20 }); loop.enable();

let inFlight = 0;
const MAX_IN_FLIGHT = Number(process.env.MAX_IN_FLIGHT ?? 300);

const priorityOf = (req) =>
  req.path.startsWith('/health') || req.path.startsWith('/api/v1/payments') || req.path.startsWith('/auth') ? 0
  : req.path.startsWith('/api/v1/orders') ? 1
  : req.path.startsWith('/api/v1/recommendations') || req.path.startsWith('/api/v1/events') ? 3
  : 2;

app.use((req, res, next) => {
  const p = priorityOf(req);
  const lagMs = loop.mean / 1e6;
  const overloaded = inFlight >= MAX_IN_FLIGHT || lagMs > 200;
  const nearlyOverloaded = inFlight >= MAX_IN_FLIGHT * 0.8 || lagMs > 100;

  if ((overloaded && p > 0) || (nearlyOverloaded && p >= 3)) {
    metrics.shed.inc({ priority: p });
    return res.status(503).set('Retry-After', '2').json({ error: 'OVERLOADED' });   // cheap, early
  }
  inFlight++;
  res.on('close', () => inFlight--);
  next();
});
```
(Ready-made: `overload-protection` / `under-pressure` for Fastify, which sheds on event-loop delay, heap and RSS.)

### Drop work for clients that already gave up (deadline)
```js
app.use((req, res, next) => {
  const deadline = Number(req.get('X-Request-Deadline'));        // set by gateway: now + client timeout
  if (deadline && Date.now() > deadline) return res.status(504).end();   // too late, don't start
  next();
});
```

### Queue consumers: shed stale low-priority jobs
```js
new Worker('analytics', async (job) => {
  if (Date.now() - job.timestamp > 10 * 60_000) return;           // >10 min old → useless, drop
  await ingest(job.data);
}, { connection, concurrency: 5 });
```

### Nginx — global concurrency cap per location
```nginx
limit_conn_zone $server_name zone=per_server:10m;
location /api/v1/recommendations { limit_conn per_server 200; limit_conn_status 503; proxy_pass http://api; }
```

### FastAPI — simple concurrency shedder
```python
MAX = 200
in_flight = 0

@app.middleware("http")
async def shed(request, call_next):
    global in_flight
    low_priority = request.url.path.startswith(("/recommendations", "/events"))
    if in_flight >= MAX or (low_priority and in_flight >= MAX * 0.8):
        return JSONResponse({"error": "OVERLOADED"}, status_code=503, headers={"Retry-After": "2"})
    in_flight += 1
    try:
        return await call_next(request)
    finally:
        in_flight -= 1
```

### Client (React Native) cooperates
```ts
// On 503: back off with jitter, stop prefetching, show cached content
if (err.response?.status === 503) { prefetchEnabled = false; await sleep(fullJitter(attempt++, 1000, 15000)); }
```

---

## ⚫ Interview Questions + Answers

**Q1: What is load shedding and why is it better than accepting all requests?**
A1: Deliberately rejecting some requests when a service is beyond capacity, so the accepted ones complete within normal latency. If everything is accepted, queues grow, latency explodes, clients time out and retry, and the server wastes work on abandoned requests until it collapses, so goodput falls to near zero. Fast rejections are cheap and keep goodput at capacity.

**Q2: How do you decide which requests to shed?**
A2: Assign priorities by business criticality: payments, login, checkout, order status and health checks are highest; browsing is next; recommendations, prefetch, analytics and bots are lowest. Propagate the priority via headers or RPC metadata. Under rising load, shed the lowest tiers first. Prefer keeping in-progress sessions or transactions, and drop requests whose deadlines have already passed.

**Q3: What signals trigger load shedding?**
A3: In-flight request count or a concurrency limit (simple and effective), queue length or queue wait time, latency SLO breaches, CPU, memory or event-loop lag, and downstream pool saturation. Adaptive concurrency algorithms adjust limits automatically based on observed latency. Shedding decisions should be fast and happen early in the request pipeline.

**Q4: Load shedding vs rate limiting vs autoscaling?**
A4: Rate limiting enforces per-client quotas for fairness and abuse prevention, even when the system has spare capacity. Load shedding protects the service as a whole when total demand exceeds capacity. Autoscaling adds capacity, but takes minutes. Shedding protects the system until autoscaling catches up, and handles spikes that exceed the maximum scale.

**Q5: How would you handle a sudden 10× traffic spike on a ticket sale?**
A5: Put a virtual waiting room at the edge to admit users at a sustainable rate. Pre-scale before the event, cache static pages and seat maps at the CDN, rate-limit per user and IP, and block bots. Shed low-priority APIs, protect checkout and payments with dedicated capacity (bulkheads), use short holds or reservations with expiry for seats, and have the client back off on 503 with jitter. Monitor and adjust the admission rate live.

---

## 🔷 Trade-offs
✅ Advantages:
- Keeps the system alive and fast for most users; prevents collapse and retry storms.

❌ Disadvantages:
- Some users get errors (by design); needs prioritization logic and tuning.
- Wrong thresholds → shedding too early (wasted capacity) or too late (collapse).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Load shedding | Rejecting excess load | ज़्यादा बोझ मना करना |
| Goodput | Useful completed work | पूरा हुआ उपयोगी काम |
| Overload | Load beyond capacity | क्षमता से ज़्यादा बोझ |
| In-flight requests | Currently processing | अभी चल रही requests |
| Priority / criticality | Importance of request | request की ज़रूरत |
| Adaptive concurrency | Auto-tuned limit | अपने आप बदलने वाली सीमा |
| Waiting room | Virtual queue at edge | आभासी लाइन |
| Deadline | Time after which result is useless | समय-सीमा |
| Event-loop lag | Node.js overload signal | Node का बोझ संकेत |

---

## ⚡ 3-Line Summary
**English:**
1. Load shedding rejects excess requests early (503/429 + Retry-After) so accepted ones stay fast — prevents goodput collapse.
2. Trigger on in-flight count, queue wait, latency, event-loop lag; shed low-priority traffic first, never critical paths.
3. Drop work past its deadline; combine with rate limiting, waiting rooms and autoscaling.

**Hindi:**
1. Load shedding = ज़्यादा requests जल्दी मना करना ताकि बाक़ी तेज़ चलें और सिस्टम न गिरे।
2. चल रही requests, queue, latency, event-loop lag देखो; पहले कम ज़रूरी ट्रैफ़िक हटाओ।
3. समय-सीमा पार वाली request छोड़ो; rate limiting, waiting room और autoscaling के साथ।

---

## ➡️ Next Topic Suggestion
**79. Timeout Pattern** — Every protection above depends on one simple rule: never wait forever. Next: choosing timeouts per layer, connect vs read timeouts, deadline propagation, and the classic timeout bugs.
