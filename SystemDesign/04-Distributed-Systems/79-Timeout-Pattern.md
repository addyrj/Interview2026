# 79. Timeout Pattern
# हिंदी में: Timeout — किसी भी बाहरी कॉल (API, DB, cache) के लिए अधिकतम इंतज़ार का समय तय करना; उसके बाद हार मानकर error/fallback देना, कभी हमेशा के लिए इंतज़ार नहीं

---

## 🔵 Simple Definition (English)
A **timeout** is the **maximum time** a caller will wait for an operation (network call, DB query, lock, queue receive) before **giving up** and treating it as a failure. It's the most basic resilience pattern: **never wait forever**.
Timeouts exist at many layers (client, CDN, load balancer, proxy, app, HTTP client, DB driver, DB statement) and must be **set deliberately and consistently**.

## 🔵 सरल परिभाषा (Hindi)
Timeout यानी किसी कॉल का अधिकतम इंतज़ार — जैसे "2 सेकंड में जवाब नहीं आया तो छोड़ दो और error/fallback दो"।
यह सबसे बुनियादी नियम है: कभी हमेशा के लिए इंतज़ार मत करो। हर परत (ऐप, Nginx, LB, DB) पर timeout सोच-समझकर लगाना चाहिए।

---

## 🔴 Problem it Solves
Without timeouts, **one slow dependency freezes everything**:
- Many HTTP clients have **no default timeout** (or a huge one). A hung TCP connection can wait **minutes**.
- Each waiting request holds memory, a socket, a DB connection, maybe a thread, so **resources pile up** until the service stops responding (Topic 76).
- Users stare at spinners; mobile apps appear frozen.
- Without a timeout there is no failure signal, so **circuit breakers, retries and fallbacks never trigger**.

Timeouts convert **"hanging forever"** into a **fast, handleable failure**.

## 🔴 यह क्यों बना? (Hindi)
बिना timeout के एक धीमी service सबको जाम कर देती है — कई HTTP libraries में default timeout होता ही नहीं, connection मिनटों तक लटका रहता है, resources भरते जाते हैं, और ऐप फ़्रीज़ दिखता है।
Timeout के बिना failure का संकेत ही नहीं मिलता, तो circuit breaker, retry, fallback भी काम नहीं करते।

---

## 🟢 How it Works — Step by Step

### Types of timeouts

```
Connect timeout   → time to establish TCP/TLS connection          (short: 0.5–3 s)
Read/response     → time waiting for response bytes after sending  (depends on operation)
Total/request     → overall cap including retries                  (the user-facing budget)
Idle timeout      → close unused keep-alive connections            (LB 60 s, Node 5 s default)
DB statement      → max query execution time (statement_timeout)
Lock timeout      → max wait for a lock (lock_timeout)
Pool acquire      → max wait for a free connection from pool
Queue visibility  → how long a consumer has before message is redelivered (SQS)
```

### Timeout budget across layers (outer > inner)

```
Mobile app total:            10 s
  └─ CDN / ALB idle:          60 s  (connection level)
     └─ Nginx proxy_read:     30 s
        └─ App request deadline: 8 s
           ├─ DB query (statement_timeout): 2 s
           ├─ Redis call:      50–100 ms
           ├─ Payment API:     5 s (read) + 1 s (connect)
           └─ Maps API:        800 ms (non-critical → fallback)

Rule: inner timeouts SHORTER than outer ones, so the inner layer fails first and the
caller can handle it (fallback/clean error) — not a generic 504 from the proxy.
```

### Choosing a value
```
Base it on the dependency's latency distribution: timeout ≈ p99 (or p99.9) + margin
  maps API p99 = 600 ms → timeout 800 ms–1 s
Consider the caller's budget: sum of sequential calls must fit the user-facing deadline
Critical vs optional: optional calls get tight timeouts + fallback; critical calls get more time
Too short → false failures + retry storms;  too long → resource exhaustion, slow UX
```

### Deadline propagation
```
Gateway receives request with 8 s budget → passes "deadline = now + 8 s" downstream
Each service: remaining = deadline - now; uses min(own timeout, remaining) for its calls
If remaining ≤ 0 → stop immediately (don't do work nobody will use)
gRPC does this natively (deadlines propagate); for HTTP use a header (X-Request-Deadline)
```

### Classic timeout bugs
```
1. No timeout at all (default infinite) → hung connections pile up
2. Proxy timeout < app timeout → client gets 504 while app keeps working (and may still commit!)
3. Node keepAliveTimeout < ALB idle timeout → ALB reuses a socket Node just closed → random 502s
   → set server.keepAliveTimeout = 65s (> ALB 60s), headersTimeout = 66s
4. Timeout without cancellation → caller gave up, but the work continues (wasted, or duplicates)
   → use AbortController / context cancellation; DB statement_timeout
5. Retry × timeout exceeds budget (3 retries × 5 s = 15 s > 10 s client timeout)
6. Timeouts on non-idempotent writes → unknown outcome → need idempotency + status check
```

## 🟢 कैसे काम करता है? (Hindi)
1. अलग-अलग timeout: connect (कनेक्शन बनाने का), read (जवाब का), total (retries सहित), DB statement, lock, pool।
2. अंदर की परत का timeout बाहर वाली से छोटा रखो (DB 2s < ऐप 8s < Nginx 30s) — अंदर वाला पहले फ़ेल हो ताकि ऊपर वाला उसे ठीक से संभाल सके।
3. Value = उस dependency का p99 + थोड़ा margin; ग़ैर-ज़रूरी कॉल्स पर छोटा timeout + fallback।
4. Deadline propagation: बचा हुआ समय नीचे की services तक भेजो; समय ख़त्म तो काम शुरू ही मत करो।
5. Timeout के साथ काम रद्द (cancel) भी करो, और पेमेंट जैसे writes पर timeout = "पता नहीं" — status check करो।

---

## 🟡 Real World Example

**AWS Builders' Library** — "Timeouts, retries, and backoff with jitter": AWS services pick timeouts from measured latency percentiles of dependencies, and stress that missing or overly long timeouts were root causes of many internal incidents.

**ALB + Node.js 502s** — a very common real issue: Node's default `keepAliveTimeout` (5 s) is shorter than the ALB idle timeout (60 s), so the ALB occasionally sends a request on a connection Node has just closed, which shows up as intermittent 502s. Raising Node's keep-alive above the ALB value fixes it. Many teams have written postmortems on this.

**Google gRPC deadlines** — Google requires every RPC to carry a deadline that propagates across services, so abandoned requests stop consuming resources deep in the call graph.

**Payment gateway integrations** — Razorpay and Stripe docs recommend client timeouts plus idempotency keys, and treating timeouts as "unknown status" with a follow-up status query or webhook.

## 🟡 Real Example Hindi में
AWS कहता है कि timeout न होने या बहुत लंबा होने से उनके कई outages हुए; वे dependency के p99 से timeout चुनते हैं।
ALB के पीछे Node.js में random 502 आना आम है — Node का keep-alive (5s) ALB (60s) से छोटा होता है; उसे 65s करने से ठीक होता है। Google हर RPC के साथ deadline भेजता है।

---

## 🟠 My Stack Example

### Node.js — fetch with AbortSignal timeout (and cancel work)
```js
async function getEta(o, d, deadline) {
  const remaining = deadline - Date.now();
  const ms = Math.min(800, remaining - 50);                 // own cap vs remaining budget
  if (ms <= 0) throw new Error('DEADLINE_EXCEEDED');
  const r = await fetch(`${MAPS}/eta?o=${o}&d=${d}`, { signal: AbortSignal.timeout(ms) });  // aborts socket
  return r.json();
}

// axios
const partner = axios.create({ baseURL: PARTNER_URL, timeout: 3000 });   // NO default timeout in axios otherwise!
```

### Server-side timeouts (Express/Node HTTP server)
```js
const server = app.listen(3000);
server.requestTimeout = 30_000;      // whole request (Node 18+ default 300s!)
server.headersTimeout = 66_000;      // must be > keepAliveTimeout
server.keepAliveTimeout = 65_000;    // > ALB/Nginx idle timeout (60s) → no random 502s

// per-request deadline middleware
app.use((req, res, next) => { req.deadline = Date.now() + 8000; next(); });
```

### Postgres timeouts
```js
const pool = new pg.Pool({
  connectionString: DATABASE_URL,
  connectionTimeoutMillis: 2000,     // pool acquire / connect
  statement_timeout: 3000,           // server cancels queries > 3s
  query_timeout: 3500,               // client-side safety
  idle_in_transaction_session_timeout: 10000,
});
// migrations: SET lock_timeout = '3s';
```

### Redis
```js
const redis = createClient({ url: REDIS_URL, socket: { connectTimeout: 1000 } });
// per call: wrap with Promise.race timeout (~50–100ms) and fall back to DB
```

### Nginx
```nginx
proxy_connect_timeout 3s;
proxy_send_timeout    10s;
proxy_read_timeout    30s;    # > app's own request deadline
keepalive_timeout     65s;
```

### FastAPI / Python
```python
async with httpx.AsyncClient(timeout=httpx.Timeout(connect=1.0, read=3.0, write=3.0, pool=1.0)) as c:
    r = await c.get(URL)

# overall budget for a block of work
try:
    result = await asyncio.wait_for(do_work(), timeout=5)
except asyncio.TimeoutError:
    return fallback()
```

### React Native / web client
```ts
const api = axios.create({ baseURL: API, timeout: 10_000 });   // user-facing budget
// show progress after 1s, offer "Retry" after timeout; for payments show "Checking status…" and poll
```

### Queue consumers
```
SQS visibility timeout > max processing time (e.g. 6× average), else message is redelivered mid-processing
BullMQ: lockDuration > job runtime, or extend lock for long jobs
```

---

## ⚫ Interview Questions + Answers

**Q1: Why are timeouts important in distributed systems?**
A1: Remote calls can hang indefinitely: lost packets, dead hosts, overloaded services. Without timeouts, waiting requests accumulate and hold threads, sockets, memory and DB connections, exhausting resources and causing cascading failure. Timeouts bound the waiting time, free resources, and produce failure signals that retries, circuit breakers and fallbacks act on.

**Q2: How do you choose timeout values?**
A2: From the dependency's observed latency distribution (around p99–p99.9 plus a margin), the caller's end-to-end budget (sequential calls plus retries must fit the user-facing deadline), and the criticality of the call (optional calls get tight timeouts with fallbacks). Separate connect and read timeouts. Make inner layers time out before outer layers. Revisit as latencies change, and monitor timeout rates.

**Q3: What is deadline propagation?**
A3: Passing the remaining time budget of the original request down through every downstream call, so each service uses `min(own timeout, remaining)` and stops work once the deadline passes. It prevents wasted work on requests the client has already abandoned, and keeps total latency bounded. gRPC supports it natively. With HTTP, propagate a deadline header and use cancellation (AbortController, context).

**Q4: What happens if the proxy timeout is shorter than the app's processing time?**
A4: The proxy returns 504 to the client while the app keeps processing and may complete the operation (e.g. create an order). The client thinks it failed and may retry, which can create duplicates, and resources are wasted. Fix: app-level deadlines shorter than proxy timeouts, cancellation of in-flight work, idempotency keys for writes, and long-running work moved to async jobs (202 + status polling).

**Q5: How should a client handle a timeout on a payment request?**
A5: Treat the outcome as unknown. Don't show failure or success immediately. Show "Checking payment status…". Query the payment status by order or idempotency key (or wait for push or webhook-driven updates), and retry only with the same idempotency key. The server reconciles with the gateway. Only then show the final result, and never let the user pay again blindly.

---

## 🔷 Trade-offs
✅ Advantages:
- Bounded latency and resource usage; enables retries/breakers/fallbacks; better UX.

❌ Disadvantages:
- Too short → false failures, retry storms, unnecessary fallbacks.
- Too long → resource exhaustion, slow failure.
- Timeouts on writes create unknown outcomes (need idempotency).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Timeout | Max wait before giving up | अधिकतम इंतज़ार |
| Connect timeout | Time to open connection | कनेक्शन बनाने का समय |
| Read timeout | Time waiting for response | जवाब का इंतज़ार |
| Deadline | Absolute time limit for request | request की आख़िरी समय-सीमा |
| Deadline propagation | Passing remaining budget downstream | बचा समय आगे भेजना |
| Cancellation | Stop work after timeout | timeout के बाद काम रोकना |
| Keep-alive timeout | Idle connection lifetime | ख़ाली कनेक्शन का समय |
| statement_timeout | Postgres max query time | DB query की सीमा |
| Unknown outcome | Don't know if op succeeded | पता नहीं काम हुआ या नहीं |

---

## ⚡ 3-Line Summary
**English:**
1. Never wait forever: set connect/read/total timeouts on every network call, DB query, lock and pool.
2. Inner timeouts < outer timeouts; base values on p99 + margin; propagate deadlines and cancel abandoned work.
3. Watch classic bugs (no default timeout, keep-alive vs ALB 502s, proxy < app); timeouts on writes need idempotency.

**Hindi:**
1. कभी हमेशा का इंतज़ार नहीं — हर कॉल, query, lock, pool पर timeout।
2. अंदर का timeout बाहर से छोटा; p99 + margin; deadline आगे भेजो और छोड़ा गया काम रद्द करो।
3. Default timeout न होना, keep-alive बनाम ALB 502 जैसे bugs से बचो; write पर timeout = idempotency ज़रूरी।

---

## ➡️ Next Topic Suggestion
**80. Health Checks (Liveness + Readiness)** — Load balancers and Kubernetes decide which instances get traffic based on health checks. Next: liveness vs readiness vs startup probes, deep vs shallow checks, and common mistakes.
