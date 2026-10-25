# 254. Monitoring — Prometheus + Grafana
# हिंदी में: Prometheus + Grafana — Metrics Monitoring और Dashboards

---

## 🔵 Simple Definition (English)
**Prometheus** is a metrics monitoring system that periodically **scrapes** (pulls) numeric metrics (request count, response time, memory usage) from a `/metrics` HTTP endpoint exposed by your app, and stores them as time-series data. **Grafana** is a dashboard/visualization tool that queries Prometheus and turns those numbers into graphs, gauges, and alerts. Together: Prometheus collects the "what happened over time" data, Grafana shows it visually.

## 🔵 सरल परिभाषा (Hindi)
**Prometheus** एक metrics monitoring system है जो periodically आपके app के `/metrics` HTTP endpoint से numeric metrics (request count, response time, memory usage) **scrape** (pull) करता है, और उन्हें time-series data के रूप में store करता है। **Grafana** एक dashboard/visualization tool है जो Prometheus से query करके उन numbers को graphs, gauges, और alerts में बदलता है। दोनों मिलकर: Prometheus "समय के साथ क्या हुआ" data collect करता है, Grafana उसे visually दिखाता है।

---

## 🔴 Problem it Solves
```
WITHOUT METRICS MONITORING:
  You only find out your app is slow/broken when:
    1. A user complains
    2. You manually SSH in and check CPU/memory with `top`
    3. You grep through logs hoping to spot a pattern

  Problems:
    1. No historical trend — was memory usage climbing for 3 days
       before the crash? You don't know, logs don't easily show trends.
    2. No early warning — by the time users complain, damage is done
    3. Can't answer "how many requests/sec is this endpoint handling?"
       or "what's the p99 latency?" without manual log math
    4. No automated alerting ("page me if error rate > 5%")

PROMETHEUS + GRAFANA SOLUTION:
  App exposes /metrics with counters, gauges, histograms.
  Prometheus scrapes it every 15s, stores as time-series.
  Grafana dashboard shows: requests/sec, p50/p95/p99 latency,
  memory/CPU usage, error rate — all as live graphs.
  Alertmanager (Prometheus's companion) pages on-call automatically
  when a threshold is breached (e.g., error_rate > 5% for 2 minutes).

  Result: you see problems BEFORE users complain, and have historical
  data to diagnose "when did this start degrading?"
```

## 🔴 यह क्यों बना? (Hindi)
```
Metrics monitoring के बिना:
  - App slow/broken होने का पता तब चलता है जब user complain करे
  - Manually SSH करके `top` से CPU/memory check करना पड़ता है
  - Historical trend नहीं पता — crash से पहले 3 दिन से memory बढ़ रही थी क्या?
  - "कितने requests/sec आ रहे हैं" या "p99 latency क्या है" जानना मुश्किल
  - कोई automated alerting नहीं

Prometheus + Grafana solution:
  - App /metrics expose करता है counters, gauges, histograms के साथ
  - Prometheus हर 15s scrape करता है, time-series store करता है
  - Grafana dashboard live graphs दिखाता है: requests/sec, latency, memory
  - Alertmanager threshold cross होने पर automatically on-call को page करता है
```

---

## 🟢 How it Works — Step by Step

Step 1 → Install `prom-client` in your Node.js app and define metrics: **Counter** (always-increasing, e.g., total requests), **Gauge** (goes up/down, e.g., current memory usage or active connections), **Histogram** (distribution of values, e.g., request duration buckets).
Step 2 → Expose a `GET /metrics` endpoint that returns all registered metrics in Prometheus's plain-text exposition format.
Step 3 → Configure Prometheus's `prometheus.yml` with a scrape job pointing to your app's `/metrics` endpoint, with a `scrape_interval` (e.g., every 15 seconds).
Step 4 → Prometheus pulls (scrapes) that endpoint on schedule and stores each metric value with a timestamp in its own time-series database.
Step 5 → Grafana connects to Prometheus as a data source; you write PromQL queries (e.g., `rate(http_requests_total[5m])`) to build dashboard panels, and configure Alertmanager rules for automatic notifications (Slack/PagerDuty) when thresholds are breached.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Node.js app में `prom-client` install करो और metrics define करो: **Counter** (हमेशा बढ़ता है), **Gauge** (ऊपर-नीचे हो सकता है), **Histogram** (values की distribution)।
Step 2 → एक `GET /metrics` endpoint expose करो जो सभी registered metrics को Prometheus के text format में return करे।
Step 3 → `prometheus.yml` में एक scrape job configure करो जो आपके app के `/metrics` endpoint को point करे, एक `scrape_interval` के साथ।
Step 4 → Prometheus schedule पर उस endpoint को scrape करता है और हर metric value को timestamp के साथ store करता है।
Step 5 → Grafana Prometheus से connect होता है; PromQL queries लिखकर dashboard panels बनाते हो, और Alertmanager rules configure करते हो automatic notifications के लिए।

---

## 🟡 Real World Example
**Razorpay payment gateway monitoring:** Every payment service instance exposes `/metrics` showing `payment_requests_total` (Counter), `active_payment_connections` (Gauge), and `payment_processing_duration_seconds` (Histogram). Prometheus scrapes all instances every 15s. A Grafana dashboard shows real-time payment success rate and p99 latency across all regions. An Alertmanager rule fires if `rate(payment_failures_total[5m]) / rate(payment_requests_total[5m]) > 0.05` (more than 5% failure rate) — automatically paging the on-call engineer via PagerDuty within seconds of the gateway degrading, long before customer support tickets would have surfaced the issue.

## 🟡 Real Example Hindi mein
**Razorpay payment gateway monitoring:** हर payment service instance `/metrics` expose करता है `payment_requests_total` (Counter), `active_payment_connections` (Gauge), और `payment_processing_duration_seconds` (Histogram) के साथ। Prometheus हर 15s में सभी instances scrape करता है। एक Grafana dashboard real-time payment success rate और p99 latency दिखाता है। एक Alertmanager rule fire होता है अगर failure rate 5% से ज़्यादा हो — on-call engineer को seconds में automatically page कर देता है, customer complaints आने से बहुत पहले।

---

## 💻 Code Example — Basic

```javascript
// metrics-basic.js
// npm install prom-client express
const client = require('prom-client');
const express = require('express');

const app = express();

// ─── 1. SET UP THE DEFAULT REGISTRY AND COLLECT DEFAULT NODE METRICS ──────
client.collectDefaultMetrics(); // CPU, memory, event loop lag, GC stats — free, built-in

// ─── 2. DEFINE A COUNTER — counts things that only go up ──────────────────
const httpRequestCounter = new client.Counter({
  name: 'http_requests_total',          // metric name (Prometheus naming convention: unit suffix)
  help: 'Total number of HTTP requests', // description shown in Prometheus UI
  labelNames: ['method', 'route', 'status'], // dimensions you can filter/group by
});

// ─── 3. DEFINE A HISTOGRAM — measures distribution of a value ────────────
const httpDurationHistogram = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method', 'route'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5], // response-time buckets in seconds
});

// ─── 4. MIDDLEWARE TO RECORD METRICS ON EVERY REQUEST ─────────────────────
app.use((req, res, next) => {
  const endTimer = httpDurationHistogram.startTimer(); // start the stopwatch
  res.on('finish', () => {
    httpRequestCounter.inc({ method: req.method, route: req.path, status: res.statusCode });
    endTimer({ method: req.method, route: req.path }); // records elapsed time into the histogram
  });
  next();
});

// ─── 5. EXPOSE /metrics FOR PROMETHEUS TO SCRAPE ──────────────────────────
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', client.register.contentType); // required content-type for Prometheus
  res.end(await client.register.metrics()); // dump all registered metrics as plain text
});

app.get('/', (req, res) => res.send('Hello World'));

app.listen(3000, () => console.log('App with metrics running on port 3000'));
// Run: node metrics-basic.js, then visit http://localhost:3000/metrics
```

## 💻 Code Example — Advanced

```javascript
// metrics-advanced.js — Gauge for active connections + custom business metrics
// npm install prom-client express

const client = require('prom-client');
const express = require('express');

const app = express();
app.use(express.json());

const register = new client.Registry(); // custom registry (isolates metrics, good practice for microservices)
client.collectDefaultMetrics({ register }); // attach default Node.js metrics to THIS registry

// ─── 1. GAUGE — value that goes up AND down ────────────────────────────────
const activeConnectionsGauge = new client.Gauge({
  name: 'active_connections',
  help: 'Number of currently active connections',
  registers: [register],
});

// ─── 2. BUSINESS METRIC COUNTERS — track domain events, not just HTTP ─────
const paymentsTotal = new client.Counter({
  name: 'payments_total',
  help: 'Total payment attempts',
  labelNames: ['status'], // 'success' | 'failed'
  registers: [register],
});

const paymentAmountHistogram = new client.Histogram({
  name: 'payment_amount_inr',
  help: 'Distribution of payment amounts in INR',
  buckets: [100, 500, 1000, 5000, 10000, 50000], // bucket boundaries tailored to real amounts
  registers: [register],
});

// ─── 3. TRACK ACTIVE CONNECTIONS ON CONNECT/DISCONNECT ─────────────────────
app.use((req, res, next) => {
  activeConnectionsGauge.inc(); // one more active connection
  res.on('finish', () => activeConnectionsGauge.dec()); // decrement once response is sent
  next();
});

// ─── 4. INSTRUMENT A REAL BUSINESS ENDPOINT ────────────────────────────────
app.post('/payments', (req, res) => {
  const { amount } = req.body;
  try {
    if (!amount || amount <= 0) throw new Error('Invalid amount');

    // simulate processing
    paymentAmountHistogram.observe(amount); // record this payment's amount into the histogram
    paymentsTotal.inc({ status: 'success' }); // increment success counter
    res.json({ status: 'success' });
  } catch (err) {
    paymentsTotal.inc({ status: 'failed' }); // increment failure counter with label
    res.status(400).json({ error: err.message });
  }
});

// ─── 5. EXPOSE /metrics FROM THE CUSTOM REGISTRY ───────────────────────────
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

module.exports = { app, register };
```

---

## 🟠 Express.js Integration

```javascript
// app.js — real app wiring metrics + a sample prometheus.yml for reference
const { app } = require('./metrics-advanced');

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.listen(4000, () => console.log('Service with Prometheus metrics on port 4000'));

/*
  prometheus.yml (separate config file, run by the Prometheus server, NOT Node.js):

  global:
    scrape_interval: 15s

  scrape_configs:
    - job_name: 'payment-service'
      static_configs:
        - targets: ['payment-service:4000']   # scrapes http://payment-service:4000/metrics

  Grafana then adds Prometheus as a data source (http://prometheus:9090) and
  builds panels using PromQL, e.g.:
    rate(payments_total{status="failed"}[5m])  -> failure rate over last 5 minutes
    histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))  -> p99 latency
*/
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using a Counter for a value that can decrease
```javascript
// WRONG: active_connections should go up AND down, but Counter only ever increases
const activeConnections = new client.Counter({ name: 'active_connections', help: '...' });
activeConnections.inc(); // fine
activeConnections.dec(); // ERROR — Counter has no .dec() method!

// CORRECT: use a Gauge for values that can go up or down
const activeConnections = new client.Gauge({ name: 'active_connections', help: '...' });
activeConnections.inc();
activeConnections.dec(); // works fine
```

❌ **Mistake 2:** Using unbounded/high-cardinality label values
```javascript
// WRONG: using userId or requestId as a label — creates millions of unique
// time-series, exploding Prometheus's memory/storage (cardinality explosion)
httpRequestCounter.inc({ userId: req.user.id, route: req.path });

// CORRECT: only use low-cardinality labels (fixed set of values)
httpRequestCounter.inc({ method: req.method, route: req.path, status: res.statusCode });
```

❌ **Mistake 3:** Forgetting `collectDefaultMetrics()` and missing basic Node.js health signals
```javascript
// WRONG: only tracking custom business metrics — missing event loop lag,
// heap usage, GC pauses that often explain WHY the app is slow
const register = new client.Registry();
// collectDefaultMetrics never called

// CORRECT: always collect default metrics alongside custom ones
client.collectDefaultMetrics({ register }); // adds process_cpu, nodejs_heap_size, etc.
```

---

## 🧠 Tricky Interview Question

**Q: Prometheus "scrapes" (pulls) metrics instead of apps "pushing" metrics to it. Why is pull-based the default model, and when would you need a Pushgateway instead?**

Answer: Pull-based monitoring means Prometheus controls WHEN and WHETHER to collect data — it can detect a target is "down" simply by a failed scrape (itself a useful signal), avoids apps needing to know Prometheus's address/credentials, and lets you scale monitoring independently of app deployments (just update `prometheus.yml`'s target list). It also naturally handles service discovery in dynamic environments (Kubernetes). However, pull doesn't work for short-lived batch jobs (e.g., a cron job that runs for 10 seconds and exits) — Prometheus might never get a chance to scrape it before it's gone. For THAT case, Prometheus provides a **Pushgateway**: the short-lived job pushes its final metrics to the Pushgateway before exiting, and Prometheus scrapes the Pushgateway (still pull, just with an intermediary buffer) instead of the ephemeral job directly.

---

## ⚫ Interview Questions + Answers

**Q1: What are the three main Prometheus metric types and give an example use case for each?**
A1: **Counter** — a value that only increases (resets to 0 on restart), e.g., `http_requests_total`. **Gauge** — a value that can go up or down, e.g., `active_connections` or `memory_usage_bytes`. **Histogram** — samples observations into configurable buckets to show distribution, e.g., `http_request_duration_seconds` used to compute percentiles like p95/p99 latency.

**Q2: What is "scrape interval" and what trade-off does choosing a smaller vs larger value involve?**
A2: The scrape interval is how often Prometheus pulls `/metrics` from each target (commonly 15s-60s). A smaller interval (e.g., 5s) gives finer-grained, more responsive data (faster alerting, more detailed graphs) but increases load on both the target app and Prometheus's storage (more data points to store). A larger interval reduces overhead but can miss short-lived spikes and delays alert detection.

**Q3: What does `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))` compute, and why use a Histogram instead of just averaging response times?**
A3: It computes the 99th percentile (p99) latency over a 5-minute rolling window from the histogram's bucket data. Averages hide outliers — if 99% of requests are fast (50ms) but 1% take 5 seconds, the average might still look fine (~100ms), masking a real problem affecting real users. Percentiles (p95, p99) reveal the tail latency that averages obscure, which is usually what matters for user experience and SLAs.

**Q4: What is "cardinality explosion" in Prometheus and how do you avoid it?**
A4: Each unique combination of label values creates a separate time-series stored in Prometheus's memory/disk. If you use a label with unbounded/high-cardinality values (like `userId`, `requestId`, or raw email addresses), you can create millions of unique time-series, exhausting Prometheus's memory and severely degrading query performance — this is "cardinality explosion." Avoid it by only using labels with a small, fixed/bounded set of possible values (HTTP method, route template like `/users/:id` not the literal URL, status code range, service name).

**Q5: How does Grafana relate to Prometheus, and can Grafana work without it?**
A5: Grafana is a visualization layer; it doesn't store metrics itself — it queries a data source (Prometheus being the most common for metrics, but also supports Elasticsearch, InfluxDB, CloudWatch, etc.) and renders the results as graphs, tables, and alert rules. So Grafana can absolutely work without Prometheus specifically (using a different data source), but Prometheus without any visualization tool still works too (it has a basic built-in expression browser) — they're commonly paired because Prometheus excels at collection/storage and Grafana excels at visualization, but each is independently useful.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need real-time visibility into app health (latency, error rate, throughput)
- You want historical trends to diagnose gradual degradation (memory leaks, slow creep in latency)
- You need automated alerting before customers notice problems

❌ Avoid when:
- A tiny personal project with no production traffic — overkill infra to run/maintain
- You only need occasional manual health checks — a simple `/health` endpoint might suffice without a full metrics pipeline

---

## 📊 Visual Diagram
```
PROMETHEUS + GRAFANA MONITORING FLOW
──────────────────────────────────────────────────────────────

  [ Node.js App ]
      │  exposes GET /metrics (Counter, Gauge, Histogram data)
      ▼
  [ Prometheus Server ]  ◀── scrapes /metrics every 15s (PULL model)
      │  stores as time-series DB
      │
      ├──▶ [ Alertmanager ] ── fires alert if threshold breached
      │                         (e.g. error_rate > 5%) ──▶ Slack/PagerDuty
      │
      ▼
  [ Grafana ]  ◀── runs PromQL queries against Prometheus
      │
      ▼
  Dashboard: requests/sec, p99 latency, memory usage, payment success rate
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Counter | Metric that only increases | सिर्फ बढ़ने वाला metric |
| Gauge | Metric that goes up/down | ऊपर-नीचे होने वाला metric |
| Histogram | Distribution of values in buckets | Values की bucket-wise distribution |
| Scrape | Prometheus pulling metrics from a target | Target से metrics pull करना |
| PromQL | Prometheus's query language | Prometheus की query language |
| Cardinality | Number of unique label combinations | Label combinations की संख्या |
| Alertmanager | Fires alerts based on Prometheus rules | Rules के आधार पर alert भेजने वाला |

---

## ⚡ 3-Line Summary
**English:**
1. Prometheus pulls (scrapes) numeric metrics from your app's `/metrics` endpoint (exposed via `prom-client`) and stores them as time-series.
2. Use Counter for always-increasing values, Gauge for up/down values, and Histogram for latency/distribution data like p99 response time.
3. Grafana visualizes Prometheus data as dashboards, and Alertmanager pages on-call automatically when thresholds are breached — catching problems before users complain.

**Hindi:**
1. Prometheus आपके app के `/metrics` endpoint से numeric metrics pull (scrape) करता है और time-series के रूप में store करता है।
2. हमेशा बढ़ने वाले values के लिए Counter, ऊपर-नीचे होने वालों के लिए Gauge, और latency/distribution के लिए Histogram use करो।
3. Grafana Prometheus data को dashboards में दिखाता है, और Alertmanager threshold cross होने पर automatically on-call को page करता है — user complain करने से पहले problem पकड़ी जाती है।

---

## ➡️ Next Topic
**255. APM — Application Performance Monitor**
