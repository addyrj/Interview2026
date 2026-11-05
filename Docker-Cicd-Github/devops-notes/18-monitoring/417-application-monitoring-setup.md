# 417. Application Monitoring Setup
# हिंदी में: Application Monitoring Setup

---

## 🔵 Simple Definition (English)
**Application monitoring** means making your Node.js / FastAPI app emit **metrics** (numbers over time), **logs** (events) and **health endpoints**, so a system like Prometheus + Grafana can scrape, graph and alert on them. The standard starting set is the "RED" method: Rate, Errors, Duration of requests.

## 🔵 सरल परिभाषा (Hindi)
**Application monitoring** मतलब अपने Node.js / FastAPI app से **metrics** (समय के साथ संख्याएँ), **logs** (events) और **health endpoints** निकलवाना, ताकि Prometheus + Grafana जैसा system उन्हें scrape, graph और alert कर सके। शुरुआती standard set "RED" method है: Rate, Errors, Duration (requests की)।

---

## 🔴 Problem it Solves
- "The site is slow" with no data: is it the DB, CPU, or one endpoint?
- Servers can be healthy while the app logic is broken (checkout fails, queue stuck).
- Without app metrics you only learn about problems from customers.
- Capacity planning needs history (requests/sec, memory growth).

## 🔴 यह क्यों बना? (Hindi)
- "Site slow है" पर कोई data नहीं: DB है, CPU है या कोई एक endpoint?
- Server healthy हो सकता है जबकि app logic टूटा हो (checkout fail, queue अटकी)।
- App metrics के बिना समस्याएँ customers से पता चलती हैं।
- Capacity planning के लिए history चाहिए (requests/sec, memory growth)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add a metrics library (prom-client for Node, prometheus-client for FastAPI)
Step 2 → Middleware measures every request: count, status, duration histogram
Step 3 → Expose GET /metrics in Prometheus text format (internal only)
Step 4 → Add /health (liveness) and /ready (DB/cache ping)
Step 5 → Prometheus scrapes /metrics every 15s (418)
Step 6 → Grafana graphs RED + business metrics (orders_created_total) (419)
Step 7 → Alert rules fire to Alertmanager when error rate or latency crosses limits (425)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Metrics library जोड़ो (Node के लिए prom-client, FastAPI के लिए prometheus-client)
Step 2 → Middleware हर request को मापता है: count, status, duration histogram
Step 3 → Prometheus text format में GET /metrics expose करो (सिर्फ internal)
Step 4 → /health (liveness) और /ready (DB/cache ping) जोड़ो
Step 5 → Prometheus हर 15s में /metrics scrape करता है (418)
Step 6 → Grafana RED + business metrics (orders_created_total) दिखाता है (419)
Step 7 → Error rate या latency limit पार करे तो alert rules Alertmanager को भेजते हैं (425)
```

---

## 🟡 Real World Example
A Swiggy-like ordering API had random slowness at dinner time. After adding `http_request_duration_seconds` and `orders_created_total`, graphs showed only `POST /orders` p95 rising from 200 ms to 4 s while other routes were fine. A missing Mongo index on `restaurantId` was the cause; fixed in 10 minutes, and an alert now watches p95 for that route.

## 🟡 Real Example Hindi mein
Swiggy जैसी ordering API में रात के खाने के समय random slowness आती थी। `http_request_duration_seconds` और `orders_created_total` जोड़ने पर graphs ने दिखाया कि सिर्फ `POST /orders` का p95 200 ms से 4 s हुआ है, बाकी routes ठीक हैं। कारण Mongo में `restaurantId` का index न होना था; 10 मिनट में fix हुआ, और अब उस route के p95 पर alert लगा है।

---

## 💻 Code / Config Example — Basic
```javascript
// app.js  (basic Node.js + Express + prom-client)   npm i express prom-client
const express = require('express');            // web framework
const client = require('prom-client');         // Prometheus client library
const app = express();                         // create app
client.collectDefaultMetrics();                // CPU, memory, event loop lag, GC, etc.
const httpDuration = new client.Histogram({    // request duration histogram
  name: 'http_request_duration_seconds',       // metric name (base unit = seconds)
  help: 'HTTP request latency',                // description
  labelNames: ['method', 'route', 'status'],   // keep labels LOW-cardinality
  buckets: [0.05, 0.1, 0.3, 0.5, 1, 2, 5],     // latency buckets in seconds
});
app.use((req, res, next) => {                  // middleware for every request
  const end = httpDuration.startTimer();       // start timer
  res.on('finish', () => {                     // when response is sent
    const route = req.route ? req.route.path : 'unmatched'; // template, NOT raw URL
    end({ method: req.method, route, status: res.statusCode }); // record
  });
  next();                                      // continue
});
app.get('/health', (req, res) => res.json({ status: 'ok' }));  // liveness
app.get('/metrics', async (req, res) => {      // scrape endpoint
  res.set('Content-Type', client.register.contentType);        // correct content type
  res.end(await client.register.metrics());    // text exposition format
});
app.listen(3000);                              // start server
```

## 💻 Code / Config Example — Advanced
```javascript
// metrics.js  (production: business counters, readiness, separate internal port)
const client = require('prom-client');          // library
const registry = new client.Registry();         // own registry (cleaner for tests)
registry.setDefaultLabels({ app: 'orders-api', env: process.env.NODE_ENV || 'dev' }); // global labels
client.collectDefaultMetrics({ register: registry }); // process metrics
const orders = new client.Counter({             // business metric
  name: 'orders_created_total', help: 'Orders created', labelNames: ['payment'], registers: [registry],
});
const dbUp = new client.Gauge({                 // dependency state 1/0
  name: 'db_up', help: 'Mongo reachable', registers: [registry],
});
module.exports = { registry, orders, dbUp };    // export for use in routes
```

```javascript
// server.js  (app on :3000, metrics on :9100 so /metrics is never public)
const express = require('express');             // framework
const { registry, dbUp } = require('./metrics');// metrics
const app = express();                          // public app
const internal = express();                     // internal app for scraping only
internal.get('/metrics', async (_req, res) => { // metrics endpoint
  res.set('Content-Type', registry.contentType);
  res.end(await registry.metrics());
});
app.get('/ready', async (_req, res) => {        // readiness: is DB OK?
  try { await pingMongo(); dbUp.set(1); res.json({ ready: true }); }
  catch { dbUp.set(0); res.status(503).json({ ready: false }); } // 503 => removed from pool
});
async function pingMongo() { /* e.g. await mongoose.connection.db.admin().ping() */ }
app.listen(3000);                               // public
internal.listen(9100, '0.0.0.0');               // reachable only on docker network (do NOT publish port)
```

```python
# main.py  (FastAPI)   pip install fastapi uvicorn prometheus-fastapi-instrumentator
from fastapi import FastAPI                                  # framework
from prometheus_fastapi_instrumentator import Instrumentator # auto RED metrics
app = FastAPI()                                              # create app
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)  # add /metrics
@app.get("/health")                                          # liveness
def health():
    return {"status": "ok"}
```
Note: JS and Python snippets were syntax-checked only (`node --check`, `py_compile`), not run against live Prometheus.

---

## 🟠 My Stack Integration
- **Node.js**: prom-client as above; log with pino JSON including request id.
- **FastAPI**: `prometheus-fastapi-instrumentator`; `structlog` for JSON logs.
- **React**: frontend errors and web vitals to Sentry (428); monitor Nginx for static availability.
- **Nginx/VPS**: Nginx proxies public traffic but does NOT route `/metrics` publicly.
- **AWS**: same /metrics scraped by Prometheus on EC2, or CloudWatch agent / managed Prometheus.

```nginx
# Block public access to metrics on the public server block
location = /metrics { return 404; }      # metrics only reachable on the internal network
```
**Security**: `/metrics` leaks routes, versions and traffic patterns. Keep it internal (separate port, firewall, or basic auth/IP allow). Never use user IDs, emails or full URLs as labels.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Label `path=req.url` (e.g. `/users/12345`), exploding cardinality and Prometheus memory.
✅ Correct: Use the route template `/users/:id`.

❌ Mistake 2: Publishing `/metrics` on the Internet through Nginx.
✅ Correct: Separate internal port or deny in Nginx.

❌ Mistake 3: Averages only (avg latency hides slow tail).
✅ Correct: Histograms and p95/p99 via `histogram_quantile`.

❌ Mistake 4: Health endpoint that always returns 200 even if DB is down.
✅ Correct: Separate liveness and readiness.

❌ Mistake 5: Instrumenting everything at once.
✅ Correct: Start with RED, add business metrics that map to alerts.

---

## 🧠 Tricky Interview Question
Prometheus memory keeps growing after you added a `user_id` label to a counter. Why, and what do you do?

Answer: Each unique label combination is a separate time series. Millions of user IDs create millions of series (high cardinality), so memory and disk explode. Remove the label, aggregate, and put per-user detail in logs or traces. Guideline: label values must come from a small bounded set (method, route template, status class).

---

## ⚫ Interview Questions + Answers

Q1: What are the four metric types?
A1: Counter (only increases), Gauge (up/down), Histogram (bucketed observations), Summary (client-side quantiles).

Q2: RED vs USE method?
A2: RED (Rate, Errors, Duration) for services/requests; USE (Utilization, Saturation, Errors) for resources like CPU/disk (420).

Q3: Pull vs push model?
A3: Prometheus pulls (scrapes) targets, which makes target-down detectable (`up == 0`). Push is for short batch jobs via Pushgateway.

Q4: Why histograms over averages?
A4: Averages hide outliers; histograms allow p95/p99 and aggregation across instances.

Q5: Metrics vs logs vs traces?
A5: Metrics = aggregates (what/how much), logs = events (details), traces = request path across services (where time went).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production API or worker.
- You need SLOs and alerts.
- Debugging performance after deploy.

❌ Avoid when:
- A throwaway prototype with no users.
- Tempted to add high-cardinality labels.

---

## 📊 Visual Diagram
```
  Users ─► Nginx ─► [ Node/FastAPI :3000 ]  ──► Mongo/Redis
                         │  middleware: count, status, duration
                         ▼
                  /metrics (:9100 internal)
                         ▲  scrape every 15s
                  [ Prometheus ] ──► [ Grafana dashboards ]
                         │
                         └─► rules ──► [ Alertmanager ] ──► Slack/Email
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Metric | Numeric time series | समय-श्रृंखला संख्या |
| Counter | Only goes up | सिर्फ बढ़ता है |
| Histogram | Bucketed latency data | bucket वाला latency data |
| Label | Dimension of a metric | metric का आयाम |
| Cardinality | Number of unique series | अनोखी series की संख्या |
| RED | Rate, Errors, Duration | Rate, Errors, Duration |

---

## ⚡ 3-Line Summary
English: Instrument the app with RED metrics, a /metrics endpoint and health checks.
Keep labels low-cardinality and /metrics internal.
Prometheus scrapes, Grafana shows, Alertmanager notifies.

Hindi: App में RED metrics, /metrics endpoint और health checks जोड़ो।
Labels कम-cardinality रखो और /metrics internal रखो।
Prometheus scrape करता है, Grafana दिखाता है, Alertmanager खबर देता है।

---

## ➡️ Next Topic
**418. Prometheus + Docker Compose**: run Prometheus to scrape these endpoints.

---
