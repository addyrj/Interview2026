# 10. Request-Response Lifecycle
# हिंदी में: Request-Response Lifecycle — एक request का यूज़र के टैप से लेकर सर्वर, डेटाबेस और वापस स्क्रीन तक का पूरा सफ़र

---

## 🔵 Simple Definition (English)
The **request-response lifecycle** is the complete journey of a single request: from the client, through DNS, network, CDN, load balancer, reverse proxy, application middleware, business logic, cache and database, and then the response travelling all the way back to be rendered on the screen.

## 🔵 सरल परिभाषा (Hindi)
जब यूज़र "Place Order" दबाता है, तो वो request कई जगहों से होकर गुज़रती है — DNS, नेटवर्क, Load Balancer, Nginx, Node.js, Redis, Database — और फिर जवाब उसी रास्ते से वापस आता है।
इस पूरे सफ़र को समझना debugging और performance के लिए सबसे ज़रूरी है।

---

## 🔴 Problem it Solves
This isn't a technology; it's a **mental model**. Without it:
- When "the app is slow", you don't know **where** the time goes (DNS? TLS? DB? a third-party API?).
- When users see a `502`, you don't know **which layer** failed.
- You can't decide where to add **caching, auth, rate limiting, logging, or timeouts**.

With it, you can say in an interview: *"Let me trace the request: …"*, which is the foundation of every system design answer.

## 🔴 यह क्यों बना? (Hindi)
यह कोई टेक्नोलॉजी नहीं, एक सोचने का तरीका है। जब ऐप धीमा हो या 502 error आए, तो पता होना चाहिए कि समय कहाँ लग रहा है या कौन-सी परत फ़ेल हुई।
इसी से तय होता है कि cache, auth, rate limit, logging कहाँ लगानी है।

---

## 🟢 How it Works — Step by Step

### The full journey: "Place Order" in a food app

```
 📱 RN App / 🌐 Next.js
  │
  │ 1. Client: build request, attach JWT, Idempotency-Key, start timer
  │ 2. DNS: api.myapp.com → IP  (cached? 0ms : 20–100ms)
  │ 3. TCP handshake (1 RTT) + TLS 1.3 handshake (1 RTT)   ← skipped if connection reused
  ▼
 ┌─────────────────────┐
 │ CDN / WAF           │ 4. Block bots/attacks, serve cached static; API → pass through
 │ (CloudFront/Cloudflare)
 └─────────┬───────────┘
           ▼
 ┌─────────────────────┐
 │ Load Balancer (ALB) │ 5. Pick a healthy server (round robin / least conn)
 └─────────┬───────────┘
           ▼
 ┌─────────────────────┐
 │ Nginx (reverse proxy)│ 6. TLS termination (if not at LB), gzip, rate limit, timeouts,
 └─────────┬───────────┘    add X-Request-ID, route /api → Node
           ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ Node.js / FastAPI app                                        │
 │  7. Middleware chain:                                        │
 │     request-id → logger → CORS → body parser → auth (JWT)    │
 │     → rate limit (Redis) → validation (zod/pydantic)         │
 │  8. Controller/route handler                                 │
 │  9. Service (business logic):                                │
 │       - idempotency check (Redis)                            │
 │       - read menu prices (Redis cache → fallback Postgres)   │
 │       - BEGIN; insert order + items; COMMIT  (Postgres)      │
 │       - publish "order.created" to queue (SQS/Kafka)         │
 │ 10. Serialize response JSON, set status 201                  │
 └─────────┬────────────────────────────────────────────────────┘
           │              (async, after response)
           │               Queue → Worker: notify restaurant, send push, email receipt
           ▼
 11. Response travels back: app → Nginx (gzip) → LB → internet → client
 12. Client: parse JSON, update state (React Query cache), navigate to tracking screen,
             log latency metric
```

### Where time goes (typical numbers)

```
┌──────────────────────────────┬──────────────┐
│ Step                         │ Time         │
├──────────────────────────────┼──────────────┤
│ DNS (cache miss)             │ 20–100 ms    │
│ TCP + TLS (new connection)   │ 2 × RTT      │  ← mobile 4G RTT ≈ 50–100 ms
│ LB + Nginx                   │ < 1–2 ms     │
│ Middleware (auth, validation)│ 1–5 ms       │
│ Redis GET                    │ ~0.5–1 ms    │
│ Postgres indexed query       │ 1–10 ms      │
│ Postgres unindexed query     │ 100 ms – sec │  ← most common real problem
│ 3rd-party API (payment, maps)│ 100–1000 ms  │  ← second most common
│ Response download            │ size / speed │
│ Client render                │ 16 ms/frame  │
└──────────────────────────────┴──────────────┘
TTFB (Time To First Byte) = everything until the first response byte arrives.
```

### Where it can fail — and what the user sees

```
DNS fails                    → "Server not found"
TLS cert expired             → "Your connection is not private"
WAF blocks                   → 403
LB: no healthy targets       → 503
Nginx can't reach Node       → 502 Bad Gateway
Node too slow (> proxy timeout) → 504 Gateway Timeout
Auth middleware rejects      → 401 / 403
Validation fails             → 400 / 422
Rate limit                   → 429
Unhandled exception          → 500
DB pool exhausted / DB down  → 500/503 (slow, then timeout)
```

### Cross-cutting concerns (where to put them)

```
Concern            Best layer
──────────────     ────────────────────────────────────────────
Static caching     CDN, browser
DDoS / bots        CDN / WAF
TLS                LB / Nginx
Rate limiting      API gateway / Nginx (coarse) + app (per user, Redis)
Auth               API gateway or app middleware
Validation         App (always), client (for UX only)
Data caching       App + Redis
Tracing            Every layer passes X-Request-ID / traceparent header
Timeouts           EVERY hop (client < LB < Nginx < app < DB) — inner timeouts shorter
```

## 🟢 कैसे काम करता है? (Hindi)
1. ऐप request बनाता है (token लगाकर) → DNS से IP → TCP + TLS कनेक्शन।
2. CDN/WAF हमले रोकता है → Load Balancer किसी healthy सर्वर पर भेजता है → Nginx आगे Node को देता है।
3. Node में middleware चलते हैं: logging, auth, rate limit, validation।
4. फिर business logic: Redis cache, Postgres transaction, queue में event डालना।
5. जवाब वापस उसी रास्ते से जाता है; धीमे काम (SMS, email) बाद में worker करता है। हर परत पर timeout और request-id ज़रूरी।

---

## 🟡 Real World Example

**Amazon: "every 100 ms of latency cost 1% in sales"** (famous internal finding). That's why big companies obsess over each step of this lifecycle: CDN for static, edge TLS termination, keep-alive, caches before DBs, and async work moved off the request path.

**Swiggy order placement**
- The request path only does the critical part: validate, price, create the order and reserve payment. Everything else (notify the restaurant, assign a delivery partner, send SMS, update analytics) is published as events and handled by **async consumers**. The user gets "Order placed" in ~300 ms instead of waiting 3 s for all side effects.

**Debugging with request IDs**
- Stripe returns a `Request-Id` header in every response. When you contact support, they paste it into their log system and see the exact path that request took through every service.

## 🟡 Real Example Hindi में
Amazon ने पाया कि 100 ms की देरी से 1% बिक्री कम होती है — इसलिए हर कदम पर समय बचाया जाता है।
Swiggy में ऑर्डर करते समय सिर्फ़ ज़रूरी काम (ऑर्डर बनाना, पेमेंट) तुरंत होता है; रेस्टोरेंट को सूचना, SMS, डिलीवरी असाइन — ये सब बाद में queue से होते हैं, ताकि यूज़र को जल्दी जवाब मिले।

---

## 🟠 My Stack Example

### Express: middleware order = lifecycle
```js
import pinoHttp from 'pino-http';
import { randomUUID } from 'crypto';

app.set('trust proxy', 1);
app.use((req, res, next) => {                       // 1. request id (from Nginx or new)
  req.id = req.headers['x-request-id'] || randomUUID();
  res.setHeader('X-Request-ID', req.id);
  next();
});
app.use(pinoHttp({ genReqId: (req) => req.id }));   // 2. structured log with latency
app.use(cors({ origin: ['https://myapp.com'] }));    // 3. CORS
app.use(express.json({ limit: '100kb' }));           // 4. body parser with size limit
app.use('/api', authenticate);                       // 5. JWT → req.user
app.use('/api', rateLimitRedis({ perMinute: 60 }));  // 6. rate limit
app.use('/api/v1/orders', ordersRouter);             // 7. routes (validation inside)
app.use(errorHandler);                               // 8. one error format

// Server-level timeouts
const server = app.listen(3000);
server.requestTimeout = 30_000;
server.keepAliveTimeout = 65_000;   // > ALB idle timeout (60s) to avoid random 502s
server.headersTimeout = 66_000;
```

### FastAPI: same idea with middleware + dependencies
```python
@app.middleware("http")
async def timing_and_request_id(request: Request, call_next):
    rid = request.headers.get("x-request-id", str(uuid4()))
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    response.headers["Server-Timing"] = f"app;dur={(time.perf_counter()-start)*1000:.1f}"
    logger.info("req", extra={"rid": rid, "path": request.url.path, "status": response.status_code})
    return response

@app.post("/api/v1/orders", status_code=201)
async def place_order(body: OrderIn, user=Depends(current_user), db=Depends(get_db)):
    async with db.begin():                               # transaction
        order = await orders.create(db, user.id, body)
    await events.publish("order.created", order.id)      # async side effects
    return order
```

### Nginx: request id + timeouts + timing log
```nginx
log_format timed '$remote_addr "$request" $status rt=$request_time urt=$upstream_response_time rid=$request_id';
access_log /var/log/nginx/access.log timed;

location /api/ {
  proxy_set_header X-Request-ID $request_id;
  proxy_connect_timeout 5s;
  proxy_read_timeout 30s;           # → 504 if app slower than this
  proxy_pass http://api_backend;
}
```
`rt` (total) minus `urt` (upstream) tells you if time was spent in Nginx/network or in your app.

### Client side: measure what users feel
```ts
// React Native / Next.js — interceptor logging latency per endpoint
http.interceptors.request.use((c) => ({ ...c, meta: { start: performance.now() } }));
http.interceptors.response.use((r) => {
  analytics.track('api_latency', { url: r.config.url, ms: performance.now() - r.config.meta.start, status: r.status });
  return r;
});
```

### Debug order when "the API is slow"
```
1. curl -w timing (Topic 01) → network or server?
2. Nginx log rt vs urt → proxy or app?
3. App logs / APM trace (Datadog, New Relic, OpenTelemetry) → which span is slow?
4. DB: pg_stat_statements / EXPLAIN ANALYZE → missing index?
5. External APIs: add timeouts + circuit breaker
```

---

## ⚫ Interview Questions + Answers

**Q1: Walk me through what happens when a mobile app makes an API call to your backend.**
A1: The app builds an HTTPS request with an auth token. DNS resolves the API domain, and TCP and TLS connections are set up or reused. The request passes the CDN/WAF, then the load balancer picks a healthy instance, and the reverse proxy forwards it to the app. Middleware handles request ID, logging, CORS, auth, rate limiting and validation. The handler runs business logic using cache and DB, often inside a transaction, and enqueues async side effects. The response is serialized, compressed and returned through the same layers. The client updates its state and UI. Mention timeouts and tracing at every hop.

**Q2: A user reports the "Place Order" API takes 5 seconds. How do you find the cause?**
A2: Reproduce it and break down timing. Client-side timing or `curl -w` separates network from server time. Nginx `request_time` vs `upstream_response_time` separates proxy from app. Distributed tracing or APM shows which span is slow inside the app (DB query, Redis, an external payment API). For the DB, check `pg_stat_statements` and `EXPLAIN ANALYZE` for missing indexes or lock waits, and the connection pool for exhaustion. Typical fixes are adding an index, caching, moving non-critical work to a queue, adding timeouts to external calls, and reusing connections.

**Q3: What's the difference between 502 and 504 errors, and at which layer do they occur?**
A3: Both come from a proxy or gateway (Nginx/ALB). 502 Bad Gateway: the upstream app refused the connection, crashed, closed it unexpectedly or sent an invalid response (often the app is down, a wrong port, or keep-alive timeout mismatches). 504 Gateway Timeout: the upstream accepted the request but didn't respond within the proxy's timeout (slow query or slow external API).

**Q4: Why should side effects like emails and notifications be async?**
A4: They're slow and unreliable third-party calls that aren't needed to answer the user. Doing them inline increases latency and couples the success of the order to the SMS provider's uptime. Instead, commit the core transaction, publish an event (via a transactional outbox, to avoid losing events), respond quickly, and let workers process events with retries and a DLQ.

**Q5: How do you set timeouts across layers?**
A5: Every network hop needs a timeout, and inner layers should time out before outer ones so errors are handled meaningfully: e.g. DB query 5 s < app request 25 s < Nginx 30 s < LB 60 s < client 30–60 s with a retry policy. Set Node's `keepAliveTimeout` higher than the LB idle timeout to avoid races that cause 502s. External calls get short timeouts plus retries with backoff and a circuit breaker.

---

## 🔷 Trade-offs
✅ Advantages (of a well-layered lifecycle):
- Each concern handled at the best layer (security at edge, logic in app, data in DB).
- Easy to debug with request IDs and per-layer timings.
- Async offloading keeps user-facing latency low.

❌ Disadvantages:
- Every layer adds latency and a possible failure point.
- More layers = more configuration (timeouts, headers, CORS) to keep consistent.
- Async side effects add eventual consistency (email may arrive a few seconds later).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lifecycle | Full journey of a request | request का पूरा सफ़र |
| Middleware | Functions run before the handler | handler से पहले चलने वाले function |
| TTFB | Time to first byte of response | पहला बाइट आने का समय |
| Request ID | Unique ID to trace a request | request की पहचान संख्या |
| Upstream | The server behind a proxy | प्रॉक्सी के पीछे वाला सर्वर |
| Timeout | Max time to wait | अधिकतम इंतज़ार का समय |
| Async processing | Doing work after responding | जवाब के बाद काम करना |
| APM / Tracing | Tools to see time per step | हर कदम का समय देखने के टूल |

---

## ⚡ 3-Line Summary
**English:**
1. A request goes: client → DNS → TCP/TLS → CDN → LB → proxy → middleware → logic → cache/DB → back.
2. Know typical time per step and which layer causes which error (502, 504, 429, 401...).
3. Keep the request path short: cache, index, timeouts everywhere, push side effects to queues, trace with request IDs.

**Hindi:**
1. Request: ऐप → DNS → TCP/TLS → CDN → LB → Nginx → Middleware → Logic → Cache/DB → वापस।
2. हर कदम का समय और कौन-सी परत कौन-सा error देती है, यह याद रखो।
3. रास्ता छोटा रखो: cache, index, हर जगह timeout, धीमे काम queue में, request-id से tracing।

---

## ➡️ Next Topic Suggestion
**11. Reverse Proxy (Nginx)** — Nginx appeared in the middle of this lifecycle. Next: what a reverse proxy is, everything it can do (TLS, load balancing, caching, compression, rate limiting), and production Nginx config for your apps.
