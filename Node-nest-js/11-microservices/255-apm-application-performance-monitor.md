# 255. APM — Application Performance Monitor
# हिंदी में: APM — Application Performance Monitoring Tool

---

## 🔵 Simple Definition (English)
**APM (Application Performance Monitoring)** tools track how your Node.js application performs in production — response times, throughput (requests/sec), error rates, slow database queries, and memory/CPU usage. Tools like **New Relic, Datadog, Elastic APM, AppDynamics** auto-instrument your code and give you dashboards, alerts, and transaction traces without you writing manual logging for every endpoint.

## 🔵 सरल परिभाषा (Hindi)
**APM** tools production में तुम्हारे Node.js app की performance track करते हैं — response time, throughput (requests/sec), error rate, slow DB queries, और memory/CPU usage। **New Relic, Datadog, Elastic APM, AppDynamics** जैसे tools code को auto-instrument करते हैं और dashboards, alerts, transaction traces देते हैं — हर endpoint पर manually logging लिखे बिना।

---

## 🔴 Problem it Solves
```
WITHOUT APM (plain console.log / basic logging):
  - "Checkout API is slow" — but WHERE? DB query? Payment gateway call?
    External API? You grep through thousands of log lines manually.
  - No historical trend: was it slow yesterday too, or just now?
  - No automatic alerting: you find out from angry customer tweets,
    not from a dashboard.
  - N+1 query problem (1 query becomes 100 queries in a loop) is
    invisible in plain logs — you only see "request took 3s", not WHY.
  - No visibility across service boundaries (order-service calling
    payment-service calling notification-service).

WITH APM:
  - Every request is automatically "instrumented" — agent wraps
    HTTP handlers, DB calls, external API calls with timers.
  - Dashboard shows: p50/p95/p99 response time, throughput, error %,
    Apdex score (user satisfaction score).
  - Transaction trace: click on one slow request → see exact
    breakdown: "DB query took 2.8s of the 3s total" → root cause found
    in seconds, not hours.
  - Automatic alerts: "Error rate > 5% in last 5 min" → Slack/PagerDuty.
  - Detects N+1 queries automatically (e.g. New Relic flags
    "same query executed 50 times in one transaction").
```

## 🔴 यह क्यों बना? (Hindi)
```
APM के बिना:
  - "Checkout API slow है" — पर कहाँ? DB query? Payment gateway?
    हज़ारों log lines manually grep करनी पड़ती हैं।
  - Trend history नहीं पता — कल भी slow था या सिर्फ अभी?
  - Automatic alerting नहीं — customer के gussa करने पर पता चलता है,
    dashboard से नहीं।
  - N+1 query problem (loop में 1 query 100 बार चलना) plain logs में
    invisible है — सिर्फ "3s लगे" दिखता है, WHY नहीं।
  - Service boundaries के across visibility नहीं (order-service
    → payment-service → notification-service)।

APM के साथ:
  - हर request auto-instrument होती है — agent HTTP handlers,
    DB calls, external calls को timers से wrap करता है।
  - Dashboard में p50/p95/p99 response time, throughput, error %,
    Apdex score दिखता है।
  - Transaction trace: एक slow request click करो → exact breakdown
    दिखता है: "DB query ने 3s में से 2.8s लिया" → root cause seconds
    में, hours नहीं।
  - Automatic alerts: "Error rate > 5% last 5 min में" → Slack/PagerDuty।
  - N+1 queries auto-detect होती हैं (जैसे "same query 50 बार चली").
```

---

## 🟢 How it Works — Step by Step

Step 1 → Install the APM agent package (e.g. `newrelic`, `dd-trace`, `elastic-apm-node`) as the FIRST require in your entry file — before any other module loads.
Step 2 → Agent patches ("monkey-patches") Node's core modules and popular libraries (http, pg, mongodb, mysql, redis, express) at startup to inject timing hooks.
Step 3 → Every incoming HTTP request creates a "transaction" — agent starts a timer, tracks every downstream call (DB query, Redis call, external HTTP call) as a child "segment".
Step 4 → Agent batches collected metrics/traces and sends them async (non-blocking) to the APM vendor's backend every few seconds.
Step 5 → Vendor backend aggregates data → dashboard shows response time percentiles, throughput, error rate, slowest endpoints, slowest DB queries, and flags anomalies (N+1, memory leak trend).
Step 6 → You set alert policies (e.g. "p95 latency > 1s for 5 min") → agent-collected data triggers notifications.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → APM agent package (`newrelic`, `dd-trace`, `elastic-apm-node`) install करो और entry file में सबसे पहली require बनाओ — हर दूसरे module से पहले।
Step 2 → Agent startup पर Node के core modules और popular libraries (http, pg, mongodb, mysql, redis, express) को patch करता है, timing hooks inject करने के लिए।
Step 3 → हर incoming HTTP request एक "transaction" बनाती है — agent timer start करता है, हर downstream call (DB query, Redis, external HTTP) को child "segment" की तरह track करता है।
Step 4 → Agent collected metrics/traces को batch करता है और async (non-blocking) तरीके से हर कुछ seconds में vendor के backend को भेजता है।
Step 5 → Vendor backend data aggregate करता है → dashboard में response time percentiles, throughput, error rate, slowest endpoints, slowest DB queries दिखते हैं, और anomalies (N+1, memory leak trend) flag होती हैं।
Step 6 → तुम alert policies set करते हो (जैसे "p95 latency > 1s for 5 min") → agent का collected data notification trigger करता है।

---

## 🟡 Real World Example
**Swiggy order-service:** Team notices in New Relic dashboard that `/orders/:id/track` endpoint has p95 latency of 4 seconds, way above the 200ms target. Clicking into a sample slow transaction trace shows: 3.6s spent in a MongoDB query `Order.findById().populate('driver').populate('restaurant').populate('items')`. APM flags it as a classic N+1-style over-fetch — each `populate()` is a separate round-trip. Team fixes it by combining into a single aggregation pipeline, p95 drops to 180ms. Without APM, this would have taken days of manual log-grepping across order-service, driver-service, and restaurant-service.

## 🟡 Real Example Hindi mein
**Swiggy order-service:** Team ko New Relic dashboard में पता चलता है कि `/orders/:id/track` endpoint का p95 latency 4 seconds है, जबकि target 200ms था। Slow transaction trace click करने पर दिखता है: 3.6s MongoDB query `Order.findById().populate('driver').populate('restaurant').populate('items')` में गया। APM इसे classic over-fetch के रूप में flag करता है — हर `populate()` अलग round-trip है। Team इसे single aggregation pipeline में combine करके fix करती है, p95 180ms पर आ जाता है। APM के बिना यह order-service, driver-service, restaurant-service के logs manually grep करने में days लेता।

---

## 💻 Code Example — Basic

```javascript
// basic-apm-timer.js
// Before using a real vendor agent, this shows the CORE IDEA behind APM:
// wrapping function calls with timers to measure performance manually.
// Run: node basic-apm-timer.js

const http = require('http'); // core http module

// ─── Simple in-memory "APM" style metric collector ───────────────────────────
const metrics = {
  requestCount: 0,       // total requests served
  totalResponseTime: 0,  // sum of all response times (ms)
  slowQueries: [],       // queries slower than threshold
};

// Simulates a DB call with random latency (sometimes slow, like real life)
function simulateDbQuery(queryName) {
  return new Promise((resolve) => {
    const delay = Math.random() < 0.2 ? 800 : 50; // 20% chance of a "slow" query
    const start = Date.now();                     // start timer (this is what APM does)
    setTimeout(() => {
      const duration = Date.now() - start;         // measure elapsed time
      if (duration > 500) {
        // Flag slow query, just like an APM agent flags slow DB segments
        metrics.slowQueries.push({ queryName, duration });
        console.log(`⚠️  SLOW QUERY detected: ${queryName} took ${duration}ms`);
      }
      resolve({ duration });
    }, delay);
  });
}

// HTTP server acting as our "instrumented" Node app
const server = http.createServer(async (req, res) => {
  const transactionStart = Date.now(); // transaction timer starts (APM concept)

  // Simulate a DB call inside the request (like fetching order details)
  await simulateDbQuery('Order.findById');

  const responseTime = Date.now() - transactionStart; // total transaction time
  metrics.requestCount += 1;                           // increment throughput counter
  metrics.totalResponseTime += responseTime;           // accumulate for average calc

  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ message: 'Order fetched', responseTimeMs: responseTime }));
});

server.listen(3000, () => {
  console.log('Basic "APM" demo server running on http://localhost:3000');
  console.log('Hit the endpoint a few times, then check metrics via GET /metrics logic below.');
});

// Print a basic report every 5 seconds (like an APM dashboard refresh)
setInterval(() => {
  const avgResponseTime = metrics.requestCount
    ? (metrics.totalResponseTime / metrics.requestCount).toFixed(2)
    : 0;
  console.log('--- METRICS SNAPSHOT ---');
  console.log(`Requests served: ${metrics.requestCount}`);
  console.log(`Avg response time: ${avgResponseTime}ms`);
  console.log(`Slow queries flagged: ${metrics.slowQueries.length}`);
}, 5000);
```

## 💻 Code Example — Advanced

```javascript
// advanced-apm-wrapper.js
// A more production-style custom APM-like wrapper: tracks transactions,
// segments (child spans), error rates, and percentile latencies —
// demonstrating the SAME concepts real agents (New Relic/Datadog) use.
// Run: node advanced-apm-wrapper.js

const express = require('express');
const app = express();

// ─── 1. METRICS STORE ──────────────────────────────────────────────────────
class APMCollector {
  constructor() {
    this.transactions = []; // store completed transaction durations
    this.errors = 0;        // error counter
  }

  // Record a finished transaction (like New Relic's transaction trace)
  record(name, durationMs, isError) {
    this.transactions.push({ name, durationMs, isError, timestamp: Date.now() });
    if (isError) this.errors += 1;
  }

  // Compute percentile (p50, p95, p99) — core APM dashboard metric
  percentile(p) {
    if (this.transactions.length === 0) return 0;
    const sorted = this.transactions.map(t => t.durationMs).sort((a, b) => a - b);
    const index = Math.ceil((p / 100) * sorted.length) - 1;
    return sorted[Math.max(0, index)];
  }

  // Error rate as a percentage — used for alerting ("error rate > 5%")
  errorRate() {
    if (this.transactions.length === 0) return 0;
    return ((this.errors / this.transactions.length) * 100).toFixed(2);
  }

  report() {
    return {
      totalRequests: this.transactions.length,
      p50: this.percentile(50),
      p95: this.percentile(95),
      p99: this.percentile(99),
      errorRatePercent: this.errorRate(),
    };
  }
}

const apm = new APMCollector();

// ─── 2. MIDDLEWARE: wraps every request as a "transaction" ───────────────
app.use((req, res, next) => {
  const start = process.hrtime.bigint(); // high-res timer, like real agents use
  req.apmSegments = [];                  // child segments (DB, external calls) collected here

  res.on('finish', () => {
    const end = process.hrtime.bigint();
    const durationMs = Number(end - start) / 1e6; // convert nanoseconds to ms
    const isError = res.statusCode >= 500;
    apm.record(`${req.method} ${req.path}`, durationMs, isError);

    // Alert simulation — in real APM this triggers PagerDuty/Slack webhook
    if (parseFloat(apm.errorRate()) > 5) {
      console.log(`🚨 ALERT: Error rate ${apm.errorRate()}% exceeds 5% threshold!`);
    }
  });
  next();
});

// Helper to simulate a timed "segment" (DB query / external API call)
async function traceSegment(name, fn) {
  const start = Date.now();
  try {
    return await fn();
  } finally {
    const duration = Date.now() - start;
    if (duration > 300) {
      console.log(`⚠️  Segment "${name}" slow: ${duration}ms`);
    }
  }
}

// ─── 3. SAMPLE ROUTES ──────────────────────────────────────────────────────
app.get('/orders/:id', async (req, res) => {
  // Simulate DB fetch as a traced segment
  const order = await traceSegment('db.orders.findById', () =>
    new Promise((resolve) => setTimeout(() => resolve({ id: req.params.id, status: 'PREPARING' }), Math.random() * 400))
  );
  res.json(order);
});

app.get('/payments/:id', async (req, res) => {
  // Simulate an external payment gateway call
  try {
    const result = await traceSegment('external.razorpay.verify', () =>
      new Promise((resolve, reject) => {
        setTimeout(() => {
          if (Math.random() < 0.1) reject(new Error('Gateway timeout')); // 10% failure rate
          else resolve({ status: 'SUCCESS' });
        }, Math.random() * 600);
      })
    );
    res.json(result);
  } catch (err) {
    res.status(502).json({ error: err.message }); // triggers error tracking
  }
});

// Expose APM dashboard data, like a vendor's /metrics endpoint
app.get('/apm/report', (req, res) => {
  res.json(apm.report());
});

app.listen(4000, () => {
  console.log('Advanced APM wrapper demo running on http://localhost:4000');
  console.log('Try: GET /orders/123, GET /payments/456, GET /apm/report');
});
```

---

## 🟠 Express.js Integration

In production, you rarely build your own APM — you plug in a real agent. Here's how New Relic/Elastic-style agents integrate with Express with almost zero code changes:

```javascript
// server.js — real-world APM agent integration pattern
// IMPORTANT: the agent require MUST be the very first line, before express!
require('newrelic'); // npm install newrelic — reads config from newrelic.js
// (For Elastic APM: require('elastic-apm-node').start({ serviceName: 'order-service' }))
// (For Datadog: require('dd-trace').init())

const express = require('express');
const app = express();

// From here, EVERY route is auto-instrumented — no manual timing code needed.
// The agent patches express's router and the http/pg/mongodb drivers under the hood.

app.get('/orders/:id', async (req, res) => {
  // This DB call is automatically traced as a segment by the agent.
  const order = await db.collection('orders').findOne({ _id: req.params.id });
  res.json(order);
});

// Custom spans for business logic the agent can't see automatically
app.post('/checkout', async (req, res) => {
  const newrelic = require('newrelic');
  // Wrap a custom chunk of logic as a named segment for the dashboard
  await newrelic.startSegment('calculate-discount', true, async () => {
    await applyDiscountLogic(req.body.cartId);
  });
  res.json({ status: 'checked out' });
});

app.listen(3000, () => console.log('Instrumented server running on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Requiring the APM agent AFTER other modules
```javascript
// WRONG — express and db drivers are already loaded before the agent can patch them
const express = require('express');
require('newrelic'); // too late! instrumentation will be incomplete

// CORRECT — agent require must be the absolute first line in the entry file
require('newrelic'); // patches core modules BEFORE anything else loads
const express = require('express');
```

❌ **Mistake 2:** Treating APM as a replacement for logging
```javascript
// WRONG — relying only on APM dashboards, no structured logs for context
app.post('/payment', (req, res) => {
  processPayment(req.body); // no log at all, APM only shows timing, not WHY it failed
});

// CORRECT — use APM for performance/timing, structured logging (Winston/Pino) for
// business context (which user, which order, what error message)
const logger = require('./logger');
app.post('/payment', (req, res) => {
  logger.info('Payment initiated', { userId: req.user.id, orderId: req.body.orderId });
  processPayment(req.body);
});
```

❌ **Mistake 3:** Ignoring agent sampling/overhead settings in high-traffic services
```javascript
// WRONG — capturing 100% of transaction traces on a service doing 10k req/sec
// causes noticeable CPU/memory overhead from the agent itself
newrelic.setTransactionTraceSampleRate(1.0); // too aggressive

// CORRECT — sample a reasonable percentage in high-throughput services
newrelic.setTransactionTraceSampleRate(0.1); // trace 10%, still statistically useful
```

---

## 🧠 Tricky Interview Question

**Q: Your APM dashboard shows p50 latency is 50ms (great!) but customers still complain the app "feels slow." How is this possible?**

```javascript
// Scenario: 1000 requests/min to /search
// p50 = 50ms  → the MEDIAN request is fast
// p99 = 4000ms → but 1% of requests (10 per minute) take 4 full seconds!
```

Answer: **p50 (median) hides tail latency.** If 1% of your 1000 requests/min take 4 seconds, that's 10 very slow requests every single minute — and because APM averages/medians smooth this out, the dashboard "looks healthy." But real users experience those slow requests directly (a slow request for YOU is 100% slow, not a statistic). This is exactly why experienced engineers watch **p95 and p99**, not just averages or p50 — tail latency is where real user pain lives. Common causes: a few DB connections stuck on lock contention, GC pauses, or cold cache misses hitting only some requests.

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between APM and plain application logging?**
A1: Logging records discrete events ("user logged in", "error: X") you must manually add everywhere, searched after the fact with tools like grep/ELK. APM automatically instruments code to measure TIMING and PERFORMANCE across the whole request lifecycle — response time, throughput, DB query duration, error rate — without manual instrumentation of every function, and gives real-time dashboards + percentile stats + alerting out of the box. They're complementary: use logging for business context, APM for performance visibility.

**Q2: What is an N+1 query problem and how does an APM tool detect it?**
A2: N+1 happens when code fetches a list of N items, then runs 1 additional query PER item in a loop (e.g., fetch 50 orders, then fetch each order's customer separately = 51 queries instead of 1 joined query). APM agents detect this by noticing many near-identical DB query segments executed within a single transaction trace, and flag it (e.g., "same query executed 50 times"). Fix: use joins, `populate()` batching, or `IN` clauses/aggregation pipelines to fetch in one query.

**Q3: Why must the APM agent be required as the first line of your entry file?**
A3: Most Node.js APM agents work via "monkey-patching" — they override methods on core modules (`http`, `https`) and popular libraries (`pg`, `mongodb`, `mysql2`, `express`) at require-time to inject timing/tracing hooks. If those modules are already required and cached by Node's module system before the agent loads, the agent can't patch them anymore, so instrumentation is incomplete or missing for parts of the app.

**Q4: What metrics should you monitor in an APM dashboard for a checkout service, and why?**
A4: Throughput (requests/sec) to know load; p95/p99 response time (not just average) to catch tail latency affecting real users; error rate (5xx responses) to catch broken flows; Apdex score for overall user satisfaction; slow DB query list to find N+1/missing-index problems; and external dependency latency (e.g., payment gateway call time) since checkout often depends on third parties outside your control.

**Q5: How do APM agents avoid adding significant overhead to a production app?**
A5: They use async, non-blocking reporting (metrics buffered and sent in batches every few seconds over a background connection, never blocking the request/response cycle); sampling (only a percentage of transactions get full detailed traces, while aggregate metrics are still collected for all); and lightweight patching (wrapping functions with minimal added code rather than deep rewrites). Still, in extremely high-throughput services, teams tune sampling rates to balance visibility vs overhead.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running production services where performance issues directly affect revenue/users (checkout, payments, search).
- You need to debug "why is this slow" across a distributed system without manually adding timers everywhere.
- You want proactive alerting before customers notice issues.

❌ Avoid when:
- A tiny internal script/cron job with no real performance SLA — adds unnecessary complexity and cost.
- Extremely performance-sensitive hot paths where even microsecond agent overhead at massive scale matters (use lightweight custom metrics instead, carefully sampled).
- Local development — most teams disable the full APM agent locally and only enable detailed logging/profiling.

---

## 📊 Visual Diagram
```
APM ARCHITECTURE (Node.js app → New Relic/Datadog style):
──────────────────────────────────────────────────────────────

  [Client Request]
        │
        ▼
  ┌─────────────────────────────────────────────┐
  │  Node.js App (agent patched http/express)    │
  │                                               │
  │   Transaction Start ──┐                       │
  │                       │                       │
  │   Segment: DB query ──┼─► 2.8s (SLOW!)        │
  │   Segment: Redis get ─┼─► 5ms                 │
  │   Segment: Payment API┼─► 180ms               │
  │                       │                       │
  │   Transaction End ────┘                       │
  └───────────────┬───────────────────────────────┘
                  │ (async, batched, non-blocking)
                  ▼
      ┌─────────────────────────┐
      │   APM Vendor Backend      │
      │ (New Relic / Datadog /    │
      │  Elastic APM / AppDynamics│
      └────────────┬──────────────┘
                   │
                   ▼
      ┌─────────────────────────┐
      │  Dashboard & Alerts       │
      │  p50/p95/p99, throughput, │
      │  error rate, slow queries │
      │  → Slack/PagerDuty alert  │
      └─────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| APM | Application Performance Monitoring tool | App की performance track करने वाला tool |
| Transaction | One full request lifecycle traced | पूरी request का traced lifecycle |
| Segment | A timed sub-step within a transaction (DB call, API call) | Transaction के अंदर एक timed sub-step |
| Throughput | Requests handled per second | प्रति second handled requests |
| p95 / p99 | 95th/99th percentile response time | 95वां/99वां percentile response time |
| Apdex | User satisfaction score based on response time | Response time पर आधारित satisfaction score |
| N+1 Query | 1 query becomes many queries in a loop | Loop में 1 query कई queries बन जाती है |
| Instrumentation | Auto-injected timing/tracing code | Auto-injected timing code |
| Sampling | Tracing only a % of transactions to reduce overhead | Overhead कम करने के लिए % transactions trace करना |

---

## ⚡ 3-Line Summary
**English:**
1. APM tools (New Relic, Datadog, Elastic APM, AppDynamics) auto-instrument your Node.js app to track response times, throughput, error rates, and slow DB queries without manual timers everywhere.
2. The agent must be required FIRST, before any other module, so it can monkey-patch core modules and libraries to inject tracing hooks.
3. Watch p95/p99 latency, not just averages — tail latency is invisible in medians but very real for the users who hit it.

**Hindi:**
1. APM tools (New Relic, Datadog, Elastic APM, AppDynamics) तुम्हारे Node.js app को auto-instrument करते हैं — response time, throughput, error rate, slow DB queries बिना manual timers के track होते हैं।
2. Agent को सबसे पहले require करना ज़रूरी है, हर दूसरे module से पहले, ताकि वह core modules को patch करके tracing hooks inject कर सके।
3. सिर्फ average नहीं, p95/p99 latency देखो — tail latency medians में invisible होती है पर उन users के लिए बहुत real होती है जो इसे face करते हैं।

---

## ➡️ Next Topic
**256. OpenTelemetry in Node.js** — Vendor-neutral observability standard जो traces, metrics, logs को standardize करता है, कई APM backends के साथ काम करने के लिए।
