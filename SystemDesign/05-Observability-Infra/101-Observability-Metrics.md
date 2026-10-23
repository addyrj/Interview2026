# 101. Observability — Metrics
# हिंदी में: Metrics — समय के साथ नापी गई संख्याएँ (requests/सेकंड, error %, latency, CPU), जिनसे dashboards बनते हैं और गड़बड़ी पर alert आता है

---

## 🔵 Simple Definition (English)
**Metrics** are **numeric measurements aggregated over time** (time series): request rate, error rate, latency percentiles, CPU, memory, queue depth, orders per minute. Each data point is a **name + labels + value + timestamp**, e.g. `http_requests_total{service="order",route="/orders",status="500"} 42`.
They're cheap to store and query, so they're ideal for **dashboards, trends, SLOs and alerting**. Common stacks: **Prometheus + Grafana**, CloudWatch, Datadog, New Relic, OpenTelemetry metrics.

## 🔵 सरल परिभाषा (Hindi)
Metrics समय के साथ नापी गई संख्याएँ हैं — हर सेकंड कितनी requests, कितने % errors, कितनी latency, CPU कितना, queue कितनी लंबी।
ये सस्ते होते हैं, इसलिए इनसे dashboards बनते हैं और गड़बड़ी होते ही alert आता है। Prometheus + Grafana सबसे लोकप्रिय जोड़ी है।

---

## 🔴 Problem it Solves
Logs are detailed but **expensive and slow to aggregate** across billions of events. You need to answer instantly:
- "Is the system healthy **right now**?" "Did error rate jump after the 3 PM deploy?"
- "What's p99 latency of checkout over the last 7 days?"
- "Are we about to run out of DB connections or disk?"
- "Wake up on-call **only when users are impacted**."

Metrics compress millions of events into a few numbers per interval, enabling **real-time dashboards, alerting, capacity planning and SLO tracking** at low cost.

## 🔴 यह क्यों बना? (Hindi)
Logs विस्तृत हैं पर अरबों घटनाओं को जोड़ना महँगा और धीमा है। तुरंत जवाब चाहिए: "अभी सिस्टम ठीक है?", "3 बजे के deploy के बाद errors बढ़े?", "DB connections ख़त्म होने वाले हैं?"।
Metrics लाखों घटनाओं को हर अंतराल में कुछ संख्याओं में बदल देते हैं — dashboards, alerts और capacity planning सस्ते में।

---

## 🟢 How it Works — Step by Step

### Metric types (Prometheus / OpenTelemetry)

```
Counter    → only goes up (resets on restart): total requests, errors, orders placed
             query with rate(): requests per second
Gauge      → goes up and down: in-flight requests, memory used, queue depth, active WS connections
Histogram  → counts observations in buckets: request latency, payload size
             → percentiles (p50/p95/p99) computed at query time, aggregatable across instances ⭐
Summary    → client-side quantiles (not aggregatable across instances) — prefer histograms
```

### Labels (dimensions) and cardinality

```
http_request_duration_seconds_bucket{service="order", route="/api/v1/orders/:id", method="GET", status="200", le="0.25"}
Labels let you slice: by route, status, region, version.

⚠️ CARDINALITY: each unique label combination = a new time series.
   route="/orders/9001" (raw id) or userId label → millions of series → Prometheus OOM / huge bills ❌
   Use route TEMPLATES, status classes, small fixed sets. Put per-user detail in logs/traces.
```

### Which metrics? — standard frameworks

```
RED (for request-driven services):        USE (for resources: CPU, disk, DB, queues):
  Rate     → requests/sec                   Utilization → % busy (CPU 75%)
  Errors   → failed requests/sec or %       Saturation  → queued work (run queue, pool waiting)
  Duration → latency histogram (p50/p99)    Errors      → error counts (disk errors, timeouts)

Google's 4 Golden Signals: Latency, Traffic, Errors, Saturation

Business metrics (often the most useful!):
  orders_placed_total, payment_success_ratio, otp_sent_total, signups_total, cart_abandon_rate,
  delivery_eta_breach_total → a drop in orders/min often catches bugs that technical metrics miss
```

### Pull vs push collection
```
Pull (Prometheus): server scrapes /metrics endpoints every 15–30 s; service discovery finds targets
Push (StatsD, CloudWatch PutMetricData, OTLP push to collector): app/agent sends metrics
Short-lived jobs → Pushgateway or OTLP push
Pipeline: App (prom-client / OTel SDK) → Prometheus / OTel Collector → TSDB (Prometheus, Mimir,
          Thanos, VictoriaMetrics, CloudWatch, Datadog) → Grafana dashboards + Alertmanager
```

### Alerting on metrics (good practices)
```
✓ Alert on SYMPTOMS users feel (error rate, latency SLO burn, orders/min drop), not every cause
✓ Use rates and percentiles over windows (5 min), not single spikes
✓ Every alert must be actionable, have a runbook link, and an owner
✓ Page for urgent user impact; ticket/Slack for slow-burn issues
✓ SLO burn-rate alerts (Topic 104) beat static thresholds
✗ "CPU > 80%" pages at 3 AM that need no action → alert fatigue
```

### Dashboards that help during incidents
```
Top row per service: RPS, error %, p50/p95/p99 latency, saturation (pool/queue)
Deploy markers (annotations) → correlate changes with regressions
Dependency panels: DB latency, Redis hit ratio, external API errors
Business panel: orders/min, payment success %
```

## 🟢 कैसे काम करता है? (Hindi)
1. चार प्रकार: Counter (सिर्फ़ बढ़ता — कुल requests), Gauge (ऊपर-नीचे — queue length), Histogram (latency buckets से p95/p99), Summary।
2. Labels (service, route, status) से metrics को काटकर देखते हैं — पर user id या पूरा URL label मत बनाओ (cardinality विस्फोट)।
3. क्या नापें: RED (Rate, Errors, Duration) services के लिए, USE (Utilization, Saturation, Errors) resources के लिए, और business metrics (orders/मिनट)।
4. Prometheus हर 15-30 सेकंड `/metrics` पढ़ता है; Grafana में dashboards, Alertmanager से alerts।
5. Alert सिर्फ़ यूज़र-प्रभाव वाले लक्षणों पर, runbook के साथ — बेवजह के alerts से on-call थक जाता है।

---

## 🟡 Real World Example

**SoundCloud → Prometheus** — Prometheus was created at SoundCloud (2012) and became the second CNCF project after Kubernetes. It's now the default metrics system for Kubernetes clusters.

**Google SRE "Four Golden Signals"** — Google's SRE book standardized latency, traffic, errors and saturation as the minimum metrics for any user-facing service.

**Swiggy / Zomato** — business metrics like "orders per minute by city" and "payment success rate by gateway" are watched on war-room dashboards during peaks. A sudden drop in one city's orders often reveals an outage (a payment gateway down, an app crash) faster than infrastructure metrics.

**Cardinality incidents** — many teams have taken down their Prometheus or got shocking Datadog bills after adding a `user_id` or raw URL label, creating millions of time series.

## 🟡 Real Example Hindi में
Prometheus SoundCloud में बना और अब Kubernetes का default metrics सिस्टम है। Google SRE ने 4 golden signals (latency, traffic, errors, saturation) तय किए।
Swiggy/Zomato के war-room में "हर शहर के orders/मिनट" देखे जाते हैं — किसी शहर में अचानक गिरावट outage को infra metrics से पहले पकड़ लेती है। `user_id` label जोड़ने से कई टीमों का Prometheus गिर गया।

---

## 🟠 My Stack Example

### Node.js — prom-client RED metrics + business counter
```js
import client from 'prom-client';
client.collectDefaultMetrics({ prefix: 'node_' });             // CPU, memory, event loop lag, GC

const httpDuration = new client.Histogram({
  name: 'http_request_duration_seconds', help: 'HTTP latency',
  labelNames: ['method', 'route', 'status_class'],
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
});
const ordersPlaced = new client.Counter({ name: 'orders_placed_total', help: 'Orders placed', labelNames: ['city', 'payment_method'] });
const dbPoolWaiting = new client.Gauge({ name: 'db_pool_waiting', help: 'Requests waiting for a DB connection' });

app.use((req, res, next) => {
  const end = httpDuration.startTimer();
  res.on('finish', () => end({
    method: req.method,
    route: req.route?.path ?? 'unmatched',            // TEMPLATE (/orders/:id), never raw URL
    status_class: `${Math.floor(res.statusCode / 100)}xx`,
  }));
  next();
});
setInterval(() => dbPoolWaiting.set(pool.waitingCount), 5000);

// in placeOrder(): ordersPlaced.inc({ city: order.city, payment_method: order.paymentMethod });

app.get('/metrics', async (_req, res) => {                 // scraped by Prometheus (internal only!)
  res.set('Content-Type', client.register.contentType);
  res.end(await client.register.metrics());
});
```

### FastAPI — prometheus-fastapi-instrumentator
```python
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter
Instrumentator(should_group_status_codes=True, excluded_handlers=["/health.*", "/metrics"]).instrument(app).expose(app)
payments_total = Counter("payments_total", "Payments by result", ["provider", "result"])
# payments_total.labels(provider="razorpay", result="success").inc()
```

### PromQL you should know
```promql
# RPS per route
sum(rate(http_request_duration_seconds_count{service="order"}[5m])) by (route)
# Error % (5xx)
sum(rate(http_request_duration_seconds_count{status_class="5xx"}[5m]))
  / sum(rate(http_request_duration_seconds_count[5m])) * 100
# p99 latency per route
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, route))
# Orders per minute by city (business)
sum(rate(orders_placed_total[5m])) by (city) * 60
```

### Alert rules (Prometheus Alertmanager)
```yaml
groups:
- name: order-service
  rules:
  - alert: HighErrorRate
    expr: |
      sum(rate(http_request_duration_seconds_count{service="order",status_class="5xx"}[5m]))
        / sum(rate(http_request_duration_seconds_count{service="order"}[5m])) > 0.02
    for: 5m
    labels: { severity: page }
    annotations: { summary: "Order service 5xx > 2% for 5m", runbook: "https://wiki/runbooks/order-5xx" }
  - alert: OrdersDropped
    expr: sum(rate(orders_placed_total[10m])) < 0.5 * sum(rate(orders_placed_total[10m] offset 1w))
    for: 10m
    labels: { severity: page }
    annotations: { summary: "Orders/min < 50% of same time last week" }
```

### Docker Compose (local Prometheus + Grafana)
```yaml
prometheus:
  image: prom/prometheus
  volumes: ["./prometheus.yml:/etc/prometheus/prometheus.yml"]   # scrape_configs: targets: ['api:3000']
  ports: ["9090:9090"]
grafana:
  image: grafana/grafana
  ports: ["3001:3000"]
```
AWS: CloudWatch metrics and alarms, or Amazon Managed Prometheus + Managed Grafana. K8s: kube-prometheus-stack Helm chart.

### Mobile / frontend metrics
```
Web: Core Web Vitals (LCP, INP, CLS) via web-vitals → analytics/RUM (Topic F05/F22)
Mobile: app start time, screen render time, API latency from device, crash-free sessions (Sentry/Firebase Performance)
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between logs, metrics and traces?**
A1: Metrics are numeric aggregates over time (counts, rates, gauges, histograms). They're cheap, fast to query, and ideal for dashboards, trends and alerts, but low in detail. Logs are detailed event records, good for investigating specific occurrences, but costly at volume and slow to aggregate. Traces follow one request across services as timed spans, showing where latency or errors occur. You alert on metrics, then use traces and logs to diagnose.

**Q2: Explain counter, gauge and histogram with examples.**
A2: A counter only increases (reset on restart), for example total requests, errors or orders placed, and you query its rate. A gauge is a current value that goes up and down, like in-flight requests, memory, queue depth or open connections. A histogram records observations into buckets, like request latency or payload sizes. It lets you compute percentiles over time windows and aggregate across instances, which is why it's preferred over summaries for latency.

**Q3: What are the RED and USE methods?**
A3: RED is for request-driven services: Rate (requests per second), Errors (failed requests), Duration (latency distribution). USE is for resources (CPU, memory, disks, network, connection pools, queues): Utilization (how busy), Saturation (how much work is waiting), Errors. Together with Google's four golden signals (latency, traffic, errors, saturation), they give a standard minimum set of metrics. Add business metrics like orders per minute.

**Q4: What is high cardinality and why is it dangerous?**
A4: Cardinality is the number of unique label combinations for a metric, and each one is a separate time series. Labels with unbounded values (user IDs, order IDs, raw URLs, emails, timestamps) create millions of series, exhausting memory in Prometheus, slowing queries and exploding costs in SaaS tools. Use bounded labels (route templates, status classes, region, version) and put per-entity detail in logs or traces.

**Q5: How do you design good alerts?**
A5: Alert on user-visible symptoms (high error rate, latency SLO violations, drops in key business metrics), using rates and percentiles over windows with a `for` duration to avoid flapping. Prefer SLO burn-rate alerts. Every page must be urgent, actionable and owned, with a runbook. Route non-urgent issues to tickets or chat. Regularly prune noisy alerts to avoid alert fatigue. Include dashboards and links in alert annotations.

---

## 🔷 Trade-offs
✅ Advantages:
- Cheap at scale, fast queries, real-time dashboards and alerting, capacity planning, SLOs.

❌ Disadvantages:
- Low detail (no per-request context); cardinality limits.
- Pre-defined: you only have metrics you instrumented.
- Aggregation can hide outliers (use histograms/percentiles, not averages).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Metric | Numeric time series | समय के साथ संख्या |
| Counter | Ever-increasing count | सिर्फ़ बढ़ने वाली गिनती |
| Gauge | Current value up/down | मौजूदा मान |
| Histogram | Bucketed distribution | buckets में बँटा वितरण |
| Label / dimension | Key to slice metrics | metrics को काटने की key |
| Cardinality | Number of unique series | अलग-अलग series की संख्या |
| RED / USE | Standard metric methods | मानक metrics तरीके |
| Golden signals | Latency, traffic, errors, saturation | चार मुख्य संकेत |
| Scrape | Prometheus pulling metrics | metrics खींचना |
| Alert fatigue | Too many useless alerts | बेकार alerts से थकान |

---

## ⚡ 3-Line Summary
**English:**
1. Metrics are cheap numeric time series (counters, gauges, histograms) for dashboards, trends, SLOs and alerts.
2. Instrument RED for services, USE for resources, golden signals and business metrics; use histograms for latency percentiles.
3. Keep label cardinality bounded; alert on user-impacting symptoms with runbooks; drill into traces/logs for causes.

**Hindi:**
1. Metrics = सस्ती संख्याएँ (counter, gauge, histogram) — dashboards, trends, alerts के लिए।
2. Services के लिए RED, resources के लिए USE, साथ में business metrics; latency के लिए histogram।
3. Labels सीमित रखो; यूज़र-प्रभाव वाले लक्षणों पर alert; कारण के लिए traces/logs।

---

## ➡️ Next Topic Suggestion
**102. Observability — Traces** — Metrics say checkout is slow; logs show events per service. Next: distributed tracing, following a single request across 8 services as spans to see exactly where the time and errors are.
