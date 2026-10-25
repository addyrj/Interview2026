# 253. Centralized Logging (ELK)
# हिंदी में: Centralized Logging — ELK Stack से सभी Microservices के Logs एक जगह

---

## 🔵 Simple Definition (English)
**ELK Stack** (Elasticsearch + Logstash + Kibana) — or its lighter variant **EFK** (Elasticsearch + Filebeat + Kibana) — is a set of tools that collect logs from MANY servers/microservices/containers, ship them to one central searchable database (Elasticsearch), and let you search/visualize them in a web dashboard (Kibana). Instead of SSH-ing into 20 different containers to check 20 log files, you search ONE place for everything.

## 🔵 सरल परिभाषा (Hindi)
**ELK Stack** (Elasticsearch + Logstash + Kibana) — या इसका lighter version **EFK** (Elasticsearch + Filebeat + Kibana) — tools का एक set है जो बहुत सारे servers/microservices/containers से logs collect करके एक central searchable database (Elasticsearch) में भेजता है, और एक web dashboard (Kibana) में search/visualize करने देता है। 20 अलग containers में SSH करके 20 log files check करने के बजाय, आप एक जगह सब कुछ search कर सकते हो।

---

## 🔴 Problem it Solves
```
WITHOUT CENTRALIZED LOGGING:
  Microservice architecture: 15 services, each running in its own
  container/pod, each writing its own local log file.

  To debug "why did order ORD789 fail?":
    1. SSH into API Gateway container → grep logs → found nothing useful
    2. SSH into Order Service container → grep logs → found "forwarded to payment"
    3. SSH into Payment Service container → grep logs → found "timeout error"
    4. Each container might have been RESTARTED or SCALED DOWN by now
       → logs are GONE (containers are ephemeral!)
    5. Takes 20+ minutes manually hopping between services

  Problems:
    1. Logs scattered across many machines/containers
    2. Container restarts can WIPE local log files entirely
    3. No single search — manual grep across many hosts
    4. No visualization — can't see error rate trends over time
    5. Doesn't scale past a handful of services

CENTRALIZED LOGGING (ELK/EFK) SOLUTION:
  Every service ships its logs (via Filebeat agent or direct HTTP) to
  a central Elasticsearch cluster. Even if the container dies, logs
  already survive in Elasticsearch.

  Debugging now: open Kibana → search "orderId:ORD789" → see ALL
  log lines from ALL 15 services for that order, in one timeline,
  in under a minute.
```

## 🔴 यह क्यों बना? (Hindi)
```
Centralized logging के बिना:
  15 services, हर एक अपने container में, हर एक अपनी local log file में लिखता है।
  "ORD789 order क्यों fail हुआ" debug करने के लिए:
    1. हर container में SSH करके grep करना पड़ता है — 20+ मिनट लग जाते हैं
    2. Container restart होने पर local logs गायब हो सकते हैं (ephemeral storage)
    3. कोई single search नहीं — manual grep हर host पर
    4. कोई visualization नहीं — error rate trends नहीं देख सकते

ELK/EFK solution:
  हर service अपने logs Filebeat agent या direct HTTP से central
  Elasticsearch cluster में भेजती है। Container मरने के बाद भी logs
  Elasticsearch में safe रहते हैं।
  अब debugging: Kibana में "orderId:ORD789" search करो — सभी 15 services
  के logs एक timeline में एक मिनट से कम में मिल जाते हैं।
```

---

## 🟢 How it Works — Step by Step

Step 1 → Each Node.js microservice writes structured JSON logs (via Winston) to stdout or a local log file.
Step 2 → A log shipper agent (**Filebeat** — lightweight, or **Logstash** — heavier, supports transforms) runs alongside each service (as a sidecar container or host-level agent), reads those log files/stdout, and forwards each log line over the network.
Step 3 → Logstash (optional, if used) can parse/transform/enrich logs in transit (e.g., GeoIP lookup from IP, splitting fields) before forwarding — Filebeat alone just ships raw data.
Step 4 → **Elasticsearch** receives and indexes all incoming logs — a distributed, searchable database optimized for fast full-text and field-based queries across huge volumes.
Step 5 → **Kibana** is the web UI on top of Elasticsearch — engineers search/filter logs, build dashboards (error rate over time, requests per service), and set up alerts (e.g., "alert if error count > 100/min").

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → हर Node.js microservice structured JSON logs (Winston से) stdout या local file में लिखती है।
Step 2 → एक log shipper agent (**Filebeat** — lightweight, या **Logstash** — heavier) हर service के साथ चलता है, logs पढ़ता है, और network पर forward करता है।
Step 3 → Logstash (optional) logs को transit में parse/transform/enrich कर सकता है (जैसे IP से GeoIP lookup) — Filebeat सिर्फ raw data ship करता है।
Step 4 → **Elasticsearch** सभी incoming logs receive और index करता है — एक distributed, searchable database जो huge volume पर fast query देता है।
Step 5 → **Kibana** Elasticsearch के ऊपर एक web UI है — engineers logs search/filter करते हैं, dashboards बनाते हैं, alerts set करते हैं।

---

## 🟡 Real World Example
**Flipkart's Big Billion Days sale:** During peak traffic, 50+ microservices (cart, inventory, payment, recommendation, search) run across hundreds of containers that scale up/down constantly. Each ships logs via Filebeat sidecars to a central Elasticsearch cluster. When the payment success rate dips, the SRE team opens a Kibana dashboard showing error rate per service in real time, drills into the spike, filters by `service:payment-service AND level:error`, and finds the root cause (a downstream bank API timing out) within minutes — even though the exact container instance that logged the error may have already been terminated and replaced by the auto-scaler.

## 🟡 Real Example Hindi mein
**Flipkart की Big Billion Days sale:** Peak traffic के दौरान, 50+ microservices (cart, inventory, payment, recommendation, search) सैकड़ों containers में चलती हैं जो constantly scale up/down होते हैं। हर एक Filebeat sidecar से central Elasticsearch cluster में logs भेजती है। जब payment success rate गिरता है, SRE team Kibana dashboard खोलती है जो real-time error rate दिखाता है हर service का, spike में drill करती है, `service:payment-service AND level:error` filter करती है, और root cause मिनटों में ढूंढ लेती है — even though वो exact container instance शायद पहले ही terminate हो गया हो।

---

## 💻 Code Example — Basic

```javascript
// elk-basic.js — shipping Winston logs DIRECTLY to Elasticsearch (no Filebeat)
// npm install winston winston-elasticsearch @elastic/elasticsearch

const winston = require('winston');
const { ElasticsearchTransport } = require('winston-elasticsearch');

// ─── 1. CONFIGURE THE ELASTICSEARCH TRANSPORT ──────────────────────────────
const esTransportOptions = {
  level: 'info', // only info and above get shipped to ES
  clientOpts: {
    node: 'http://localhost:9200', // Elasticsearch endpoint
  },
  indexPrefix: 'order-service-logs', // logs stored under daily indices like order-service-logs-2024.01.15
};

const esTransport = new ElasticsearchTransport(esTransportOptions);

// ─── 2. CREATE LOGGER WITH BOTH CONSOLE AND ELASTICSEARCH TRANSPORTS ──────
const logger = winston.createLogger({
  format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
  transports: [
    new winston.transports.Console(), // still see logs locally too
    esTransport, // AND ship them to Elasticsearch
  ],
});

// ─── 3. LOG AN EVENT — IT GOES TO BOTH CONSOLE AND ELASTICSEARCH ──────────
logger.info('Order placed', { orderId: 'ORD789', userId: 'u55', amount: 1299 });

esTransport.on('error', (err) => {
  console.error('Elasticsearch transport error:', err); // handle ES connection issues
});

// Run: node elk-basic.js (requires a running Elasticsearch instance at localhost:9200)
// Verify: GET http://localhost:9200/order-service-logs-*/_search
```

## 💻 Code Example — Advanced

```javascript
// elk-advanced.js — Filebeat-style approach: write structured JSON to stdout/file,
// let Filebeat (a separate process/container, NOT Node code) handle shipping.
// This is the RECOMMENDED production pattern — app code stays simple and
// doesn't need to know about Elasticsearch at all.

const winston = require('winston');

// ─── 1. LOGGER JUST WRITES JSON TO STDOUT — DECOUPLED FROM SHIPPING ────────
const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json() // Filebeat/Logstash expects structured JSON lines
  ),
  defaultMeta: {
    service: 'payment-service',
    environment: process.env.NODE_ENV || 'development',
    // container/pod metadata — helps Kibana filter by instance later
    host: process.env.HOSTNAME || 'local',
  },
  transports: [
    new winston.transports.Console(), // stdout — Filebeat tails container stdout in Docker/K8s
  ],
});

// ─── 2. SAMPLE filebeat.yml (NOT JavaScript — shown for context) ──────────
// filebeat.inputs:
//   - type: container
//     paths:
//       - '/var/lib/docker/containers/*/*.log'
// output.elasticsearch:
//   hosts: ["elasticsearch:9200"]
//   index: "microservices-logs-%{+yyyy.MM.dd}"
// This config file runs as a SEPARATE Filebeat process/sidecar —
// your Node.js app never talks to Elasticsearch directly.

// ─── 3. APP CODE STAYS SIMPLE, UNAWARE OF THE LOGGING PIPELINE ────────────
function processPayment(orderId, amount) {
  logger.info('Processing payment', { orderId, amount });
  try {
    if (amount > 500000) throw new Error('Amount exceeds fraud threshold');
    logger.info('Payment successful', { orderId, amount });
    return { success: true };
  } catch (err) {
    logger.error('Payment processing failed', { orderId, error: err.message });
    return { success: false, error: err.message };
  }
}

processPayment('ORD789', 1299);
processPayment('ORD999', 600000); // triggers the error path

module.exports = { logger, processPayment };
```

---

## 🟠 Express.js Integration

```javascript
// app.js — Express service designed to run in a container, logging to stdout for Filebeat
const express = require('express');
const morgan = require('morgan');
const { logger } = require('./elk-advanced');

const app = express();
app.use(express.json());

// Morgan piped into the same JSON logger — these lines also get shipped by Filebeat
app.use(morgan('combined', { stream: { write: (msg) => logger.info(msg.trim()) } }));

app.post('/payments', (req, res) => {
  const { orderId, amount } = req.body;
  logger.info('Payment request received', { orderId, amount });

  if (!orderId || !amount) {
    logger.warn('Malformed payment request', { body: req.body });
    return res.status(400).json({ error: 'orderId and amount required' });
  }

  logger.info('Payment accepted', { orderId, amount });
  res.json({ status: 'accepted' });
});

// All logs above are plain stdout JSON — Filebeat sidecar picks them up
// and ships them to Elasticsearch; the app itself has ZERO Elasticsearch code.
app.listen(5000, () => logger.info('Payment service running on port 5000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Writing directly to Elasticsearch from every service instance
```javascript
// WRONG: app code directly depends on an Elasticsearch client + transport
// If ES goes down, every app instance's logging breaks or blocks
const esTransport = new ElasticsearchTransport({ clientOpts: { node: 'http://es:9200' } });

// CORRECT: log to stdout/file, let a decoupled agent (Filebeat) handle shipping.
// App never cares if Elasticsearch is temporarily unreachable — Filebeat buffers/retries.
logger.info('Order placed', { orderId }); // just writes JSON to stdout
```

❌ **Mistake 2:** Not including a `service` field in logs
```javascript
// WRONG: logs from 15 different microservices look identical in Elasticsearch
logger.info('Request processed', { requestId });

// CORRECT: tag every log with its originating service via defaultMeta
const logger = winston.createLogger({
  defaultMeta: { service: 'payment-service' },
});
```

❌ **Mistake 3:** Logging unbounded/unindexed free text, breaking Elasticsearch mapping
```javascript
// WRONG: logging huge raw objects/binary data that blow up index size and
// can even cause Elasticsearch field mapping conflicts (e.g., same field
// sometimes a string, sometimes an object)
logger.info('Response', { data: entireHugeApiResponseObject });

// CORRECT: log only relevant summarized fields
logger.info('Response received', { status: response.status, itemCount: response.data.length });
```

---

## 🧠 Tricky Interview Question

**Q: If a container crashes and restarts, why don't you lose its logs when using the ELK/EFK pattern, but you WOULD lose them with plain local file logging?**

Answer: With plain local file logging, logs live inside the container's writable filesystem layer. Containers are designed to be ephemeral — when a container is destroyed (crash, redeploy, auto-scaling down), its filesystem layer is destroyed too, taking any local-only log files with it. In the ELK/EFK pattern, a Filebeat agent CONTINUOUSLY tails the log output (stdout, or a mounted log file) and ships each line to Elasticsearch in near-real-time, as it's produced — so by the time the container actually dies, the vast majority of its logs are already safely stored externally in Elasticsearch, independent of the container's lifecycle. The small window of risk is only for logs produced in the few hundred milliseconds right before a hard crash that Filebeat hadn't yet shipped.

---

## ⚫ Interview Questions + Answers

**Q1: What does each letter in "ELK" stand for, and what's the role of each component?**
A1: **E**lasticsearch — distributed search/storage engine that indexes logs for fast querying. **L**ogstash — a data processing pipeline that can ingest, transform/enrich (parse fields, GeoIP lookup, filter), and forward logs to Elasticsearch; heavier resource footprint. **K**ibana — the web-based visualization/dashboard UI on top of Elasticsearch, used to search logs, build charts, and set alerts.

**Q2: What is EFK and why would you choose Filebeat over Logstash?**
A2: EFK replaces Logstash with **Filebeat** — a much lighter-weight log shipper (written in Go, minimal CPU/memory footprint) that just tails log files/stdout and forwards them, optionally straight to Elasticsearch or through Logstash for heavier transforms. In resource-constrained environments (many small containers/pods), Filebeat is preferred as a sidecar because it's cheap to run per-instance; Logstash is usually run centrally (fewer instances) only when you need its richer transform/parsing capabilities.

**Q3: Why is it considered bad practice for application code to talk directly to Elasticsearch for logging?**
A3: It tightly couples your business logic/app availability to the logging infrastructure's availability — if Elasticsearch is slow or down, logging calls could block, throw, or silently fail, affecting your core app. It also means every service needs an Elasticsearch client + credentials configured, increasing security surface and config duplication. The decoupled pattern (app writes to stdout/local file → external Filebeat agent ships it) means the app has zero dependency on Elasticsearch's availability; failures in shipping just mean a small delay, with Filebeat retrying.

**Q4: How would you use Kibana to debug a spike in errors across microservices?**
A4: Open Kibana's Discover or a saved dashboard, filter the time range to the spike window, filter by `level:error`, and group/aggregate by `service` field to see WHICH service(s) are producing the most errors. Drill into a specific service's errors, filter further by `requestId` or `orderId` if you have one from a user report, and read the full trace of structured log fields (error message, stack trace, metadata) to find the root cause — all without SSHing into any server.

**Q5: What's a potential downside/cost consideration of centralized logging at scale?**
A5: Elasticsearch storage and compute cost scale directly with log volume — logging everything at `debug` level across hundreds of high-traffic services can generate terabytes of data per day, which is expensive to store and index. Teams mitigate this by: setting appropriate log levels (info/warn/error in production, not debug), using index lifecycle management (ILM) to auto-delete/archive old indices after N days, and sampling verbose logs rather than capturing 100% of them.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running multiple microservices/containers where logs are scattered across many hosts
- You need searchable, persistent logs that survive container restarts
- You need dashboards/alerts on log data (error rates, request volume trends)

❌ Avoid when:
- A single monolith on one server — a local rotating log file may be sufficient
- Extremely cost-sensitive small projects — running an Elasticsearch cluster has real infra cost/overhead; consider managed/cheaper alternatives (hosted logging SaaS) first

---

## 📊 Visual Diagram
```
EFK ARCHITECTURE ACROSS MICROSERVICES
──────────────────────────────────────────────────────────────

  [Order Service]   [Payment Service]   [Notification Service]
   stdout (JSON)      stdout (JSON)         stdout (JSON)
       │                   │                     │
   [Filebeat]          [Filebeat]            [Filebeat]     ◀── sidecar per service
       │                   │                     │
       └───────────────────┼─────────────────────┘
                            ▼
                    [ Elasticsearch ]   ◀── central indexed, searchable storage
                            │
                            ▼
                       [ Kibana ]        ◀── search / dashboards / alerts
                            │
                            ▼
                     Engineer searches:
                 "orderId:ORD789" → sees logs
                 from ALL 3 services, timeline order
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Elasticsearch | Distributed search/index engine for logs | Logs के लिए search/index engine |
| Logstash | Heavy log processing/transform pipeline | Heavy log transform pipeline |
| Filebeat | Lightweight log shipping agent | Lightweight log shipping agent |
| Kibana | Web UI for search/visualization | Search/visualization के लिए web UI |
| Index | Elasticsearch's unit of stored, searchable data | Elasticsearch का searchable data unit |
| Sidecar | Agent container running alongside the app | App के साथ चलने वाला agent container |
| ILM | Index Lifecycle Management — auto-delete old logs | पुराने logs auto-delete करने की policy |

---

## ⚡ 3-Line Summary
**English:**
1. ELK/EFK centralizes logs from many microservices/containers into one searchable Elasticsearch store, visualized via Kibana.
2. The recommended pattern is decoupled: apps write structured JSON to stdout, a sidecar agent (Filebeat) ships it — apps never talk to Elasticsearch directly.
3. Centralized logging survives container restarts and lets you trace a single request across all services in one search, at the cost of storage/infra overhead.

**Hindi:**
1. ELK/EFK कई microservices/containers के logs को एक searchable Elasticsearch store में centralize करता है, Kibana से visualize होता है।
2. सबसे अच्छा pattern decoupled है: apps structured JSON stdout में लिखें, Filebeat sidecar उसे ship करे — apps सीधे Elasticsearch से बात नहीं करते।
3. Centralized logging container restarts में भी बचा रहता है और एक request को सभी services में एक search से trace कर सकते हो, storage cost के साथ।

---

## ➡️ Next Topic
**254. Monitoring — Prometheus + Grafana** — Metrics scraping, /metrics endpoint, और dashboards/alerting।
