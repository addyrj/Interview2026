# 256. OpenTelemetry in Node.js
# हिंदी में: OpenTelemetry — Vendor-Neutral Observability Standard

---

## 🔵 Simple Definition (English)
**OpenTelemetry (OTel)** is a vendor-neutral, open-source standard for collecting **traces, metrics, and logs** from your application. Instead of locking into one APM vendor's proprietary agent (New Relic SDK, Datadog SDK), you instrument your code ONCE with OpenTelemetry, and then export that data to ANY backend (Jaeger, Prometheus, Datadog, New Relic, Honeycomb) just by changing the exporter config — no code changes needed.

## 🔵 सरल परिभाषा (Hindi)
**OpenTelemetry (OTel)** एक vendor-neutral, open-source standard है जो **traces, metrics, और logs** collect करता है। किसी एक APM vendor के proprietary agent (New Relic SDK, Datadog SDK) में lock होने के बजाय, तुम code को **एक बार** OpenTelemetry से instrument करते हो, फिर data को किसी भी backend (Jaeger, Prometheus, Datadog, New Relic, Honeycomb) पर export कर सकते हो — सिर्फ exporter config बदलकर, code change किए बिना।

---

## 🔴 Problem it Solves
```
BEFORE OpenTelemetry — VENDOR LOCK-IN:
  - Team instruments code with New Relic SDK → deeply tied to New Relic's
    APIs (newrelic.startSegment, newrelic.setTransactionName, etc.)
  - Company decides to switch to Datadog (cheaper contract, better UI)
    → must RE-INSTRUMENT the entire codebase with Datadog's SDK.
  - Different microservices use different vendors (team A uses New Relic,
    team B uses Elastic APM) → traces don't connect across services,
    you can't see the FULL request path across the whole system.
  - No standard trace format → tools can't interoperate.

WITH OpenTelemetry:
  - Instrument once using OTel's vendor-neutral API/SDK.
  - Data (traces/metrics/logs) is exported via a pluggable "Exporter" —
    swap Jaeger → Datadog → Prometheus by changing config, zero code change.
  - All microservices emit OTel-compatible traces → trace IDs propagate
    across service boundaries even if each service uses a different backend.
  - Became a CNCF standard — massive industry adoption means any APM
    tool today can ingest OTel data directly.
```

## 🔴 यह क्यों बना? (Hindi)
```
OpenTelemetry से पहले — VENDOR LOCK-IN:
  - Team code को New Relic SDK से instrument करती है → New Relic की
    APIs में गहराई से tied हो जाता है (newrelic.startSegment, आदि)।
  - Company Datadog पर switch करने का decision लेती है (cheaper contract)
    → पूरे codebase को Datadog SDK से फिर से instrument करना पड़ता है।
  - अलग-अलग microservices अलग vendors use करती हैं (team A New Relic,
    team B Elastic APM) → traces services के बीच connect नहीं होते,
    पूरे system में request का full path नहीं दिखता।
  - कोई standard trace format नहीं → tools आपस में interoperate नहीं
    कर सकते।

OpenTelemetry के साथ:
  - एक बार OTel के vendor-neutral API/SDK से instrument करो।
  - Data (traces/metrics/logs) pluggable "Exporter" से export होता है —
    Jaeger → Datadog → Prometheus switch सिर्फ config बदलकर, code same।
  - सभी microservices OTel-compatible traces emit करती हैं → trace IDs
    service boundaries के across propagate होती हैं, भले ही हर service
    अलग backend use करे।
  - CNCF standard बन गया — industry-wide adoption का मतलब है कि आज कोई
    भी APM tool OTel data directly ingest कर सकता है।
```

---

## 🟢 How it Works — Step by Step

Step 1 → Install `@opentelemetry/sdk-node` and `@opentelemetry/auto-instrumentations-node` — these auto-instrument common libraries (http, express, pg, mongodb, redis) without manual code changes.
Step 2 → Create a tracing setup file (e.g. `tracing.js`) that initializes the SDK with chosen exporters (console, Jaeger, Prometheus, OTLP for Datadog/New Relic).
Step 3 → Load `tracing.js` BEFORE your app code starts (`node -r ./tracing.js server.js` or `require('./tracing')` as the first line) — same "patch before load" rule as any APM agent.
Step 4 → Every incoming request auto-creates a **Span** (a single traced operation) with a unique Trace ID and Span ID; downstream calls (DB, HTTP to another service) create **child spans** linked via "context propagation".
Step 5 → When a span finishes, the SDK hands it to the configured **Exporter**, which sends it to whatever backend you chose (Jaeger UI, Prometheus scrape endpoint, Datadog agent, etc.).
Step 6 → To switch backends later (e.g. Jaeger → Datadog), you only change the Exporter configuration in `tracing.js` — the instrumentation code stays untouched.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `@opentelemetry/sdk-node` और `@opentelemetry/auto-instrumentations-node` install करो — ये common libraries (http, express, pg, mongodb, redis) को manual code changes के बिना auto-instrument करते हैं।
Step 2 → एक tracing setup file (`tracing.js`) बनाओ जो SDK को chosen exporters (console, Jaeger, Prometheus, OTLP for Datadog/New Relic) के साथ initialize करे।
Step 3 → `tracing.js` को app code से पहले load करो (`node -r ./tracing.js server.js` या पहली line में `require('./tracing')`) — किसी भी APM agent जैसा "patch before load" rule।
Step 4 → हर incoming request auto एक **Span** बनाती है (एक traced operation) जिसका unique Trace ID और Span ID होता है; downstream calls (DB, दूसरी service को HTTP) "context propagation" के through linked **child spans** बनाती हैं।
Step 5 → Span finish होने पर, SDK उसे configured **Exporter** को देता है, जो उसे चुने हुए backend (Jaeger UI, Prometheus scrape endpoint, Datadog agent) पर भेजता है।
Step 6 → Backend बाद में बदलना हो (जैसे Jaeger → Datadog) तो सिर्फ `tracing.js` में Exporter config बदलो — instrumentation code untouched रहता है।

---

## 🟡 Real World Example
**Flipkart's internal platform team:** runs 40+ microservices, with different teams historically picking different APM tools. They migrate everyone to OpenTelemetry instrumentation — same `tracing.js` setup pattern copy-pasted per service, just with each service's own `serviceName`. Traces now flow seamlessly: a single `order-id` trace can be followed from `api-gateway` → `order-service` → `inventory-service` → `payment-service` in one Jaeger UI view, even though inventory-service still exports to an older Zipkin instance during migration — because OTel's trace format is backend-agnostic, both instances show the same trace. Later when the company signs a deal with Datadog, they change ONE line (the OTLP exporter endpoint) across services via shared config, with zero app code changes.

## 🟡 Real Example Hindi mein
**Flipkart की internal platform team:** 40+ microservices चलाती है, जहाँ अलग-अलग teams historically अलग-अलग APM tools use करती थीं। वे सबको OpenTelemetry instrumentation पर migrate करते हैं — हर service में वही `tracing.js` setup pattern copy-paste होता है, सिर्फ अपना `serviceName` अलग। Traces अब seamlessly flow करती हैं: एक `order-id` trace को `api-gateway` → `order-service` → `inventory-service` → `payment-service` तक एक ही Jaeger UI view में follow किया जा सकता है, भले ही inventory-service अभी भी migration के दौरान पुराने Zipkin instance पर export कर रहा हो — क्योंकि OTel का trace format backend-agnostic है, दोनों instances same trace दिखाते हैं। बाद में जब company Datadog से deal करती है, तो सब services में सिर्फ ONE line (OTLP exporter endpoint) बदलती है, zero app code changes के साथ।

---

## 💻 Code Example — Basic

```javascript
// tracing.js — OpenTelemetry setup, MUST be loaded before the app
// Run: node -r ./tracing.js server.js
// npm install @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node
//             @opentelemetry/exporter-trace-otlp-http

const { NodeSDK } = require('@opentelemetry/sdk-node'); // core SDK
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node'); // auto-patches http/express/pg/etc
const { ConsoleSpanExporter } = require('@opentelemetry/sdk-trace-node'); // prints spans to console for learning

// ─── 1. CREATE THE SDK INSTANCE ────────────────────────────────────────────
const sdk = new NodeSDK({
  serviceName: 'order-service', // this name shows up in every trace/span — identifies which service
  traceExporter: new ConsoleSpanExporter(), // for demo: print spans to console (swap for Jaeger/OTLP in prod)
  instrumentations: [getNodeAutoInstrumentations()], // auto-instrument http, express, dns, fs, etc.
});

// ─── 2. START THE SDK — patches modules before anything else loads ────────
sdk.start();
console.log('OpenTelemetry tracing initialized for order-service');

// ─── 3. GRACEFUL SHUTDOWN — flush remaining spans before process exits ────
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('Tracing terminated'))
    .catch((err) => console.error('Error terminating tracing', err))
    .finally(() => process.exit(0));
});

module.exports = sdk;
```

```javascript
// server.js — a plain Express app, NO manual tracing code needed!
// Run: node -r ./tracing.js server.js   (tracing.js patches http/express automatically)

const express = require('express');
const app = express();

// This route is automatically traced — OTel auto-instrumentation creates
// a span for the HTTP request without you writing any tracing code here.
app.get('/orders/:id', (req, res) => {
  // Simulate some work
  const order = { id: req.params.id, status: 'CONFIRMED' };
  res.json(order);
});

app.listen(3000, () => console.log('Order service running on port 3000'));
// Open http://localhost:3000/orders/42 and watch tracing.js's console
// exporter print a full span with traceId, spanId, duration, http.method, etc.
```

## 💻 Code Example — Advanced

```javascript
// advanced-tracing.js — custom spans + context propagation across services
// npm install @opentelemetry/api @opentelemetry/sdk-node
//             @opentelemetry/auto-instrumentations-node
//             @opentelemetry/exporter-trace-otlp-http

const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http'); // sends to Jaeger/Datadog/etc via OTLP protocol
const { trace, context } = require('@opentelemetry/api'); // manual span API for custom instrumentation

// ─── 1. SETUP — exporting via OTLP so it's swappable to ANY OTLP-compatible backend ──
const sdk = new NodeSDK({
  serviceName: 'payment-service',
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_ENDPOINT || 'http://localhost:4318/v1/traces', // Jaeger collector OR Datadog agent OR any OTLP endpoint
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});
sdk.start();

// Get a "tracer" instance to create custom spans for business logic
const tracer = trace.getTracer('payment-service-tracer');

// ─── 2. CUSTOM SPAN — wrap business logic the auto-instrumentation can't see ──
async function verifyPaymentWithGateway(orderId, amount) {
  // startActiveSpan creates a child span under the current trace context
  return tracer.startActiveSpan('verify-payment-with-gateway', async (span) => {
    try {
      span.setAttribute('order.id', orderId);       // custom attribute, visible in trace UI
      span.setAttribute('payment.amount', amount);   // helps filter/search traces later

      // Simulate calling Razorpay/Paytm gateway (would be an actual HTTP call)
      const result = await new Promise((resolve, reject) => {
        setTimeout(() => {
          if (Math.random() < 0.05) reject(new Error('Gateway timeout'));
          else resolve({ status: 'SUCCESS', transactionId: 'txn_' + Date.now() });
        }, 300);
      });

      span.setAttribute('payment.status', result.status);
      return result;
    } catch (err) {
      span.recordException(err);                 // attaches error details to the span
      span.setStatus({ code: 2, message: err.message }); // SpanStatusCode.ERROR = 2
      throw err;
    } finally {
      span.end(); // IMPORTANT: always end the span, even on error, or it leaks/never reports
    }
  });
}

// ─── 3. CONTEXT PROPAGATION — passing trace context to another service via HTTP ──
const http = require('http');
const { propagation } = require('@opentelemetry/api');

async function callNotificationService(orderId) {
  const headers = {};
  // Injects traceparent header so notification-service continues the SAME trace
  propagation.inject(context.active(), headers);

  return new Promise((resolve, reject) => {
    const req = http.request(
      {
        hostname: 'notification-service.internal',
        port: 5000,
        path: `/notify?orderId=${orderId}`,
        method: 'POST',
        headers, // <-- traceparent header auto-included here, propagates the trace
      },
      (res) => resolve(res.statusCode)
    );
    req.on('error', reject);
    req.end();
  });
}

module.exports = { verifyPaymentWithGateway, callNotificationService };
```

---

## 🟠 Express.js Integration

```javascript
// app.js — Express app using OpenTelemetry end-to-end
// Entry point MUST load tracing.js FIRST (same rule as any APM agent)
require('./advanced-tracing'); // side-effect: starts OTel SDK, patches express/http

const express = require('express');
const { verifyPaymentWithGateway, callNotificationService } = require('./advanced-tracing');

const app = express();
app.use(express.json());

// Auto-instrumentation already traces this whole request. We add a custom
// child span inside for the payment gateway call for deeper visibility.
app.post('/checkout', async (req, res) => {
  const { orderId, amount } = req.body;

  try {
    // This call creates a CHILD SPAN nested under the auto-created HTTP span
    const payment = await verifyPaymentWithGateway(orderId, amount);

    // Fire-and-continue trace: notification-service will show up as a
    // separate service in the SAME trace, thanks to context propagation
    await callNotificationService(orderId);

    res.json({ status: 'checked_out', payment });
  } catch (err) {
    // Error is already recorded on the span inside verifyPaymentWithGateway
    res.status(502).json({ error: 'Payment verification failed' });
  }
});

app.listen(3001, () => console.log('Payment service (OTel instrumented) on port 3001'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Loading the app before initializing the OTel SDK
```javascript
// WRONG — express is already imported/cached, auto-instrumentation misses it
const express = require('express');
const { NodeSDK } = require('@opentelemetry/sdk-node');
// ... sdk.start() here is too late for express patching

// CORRECT — load tracing setup FIRST, as a separate file required via -r flag
// node -r ./tracing.js server.js
// OR require('./tracing') as literally the first line of your entry file
```

❌ **Mistake 2:** Forgetting to call `span.end()` on custom spans
```javascript
// WRONG — span never ends, so it never gets exported, and memory/context can leak
const span = tracer.startSpan('process-order');
await processOrder();
// missing span.end() !

// CORRECT — always end spans, ideally in a try/finally so errors don't skip it
const span = tracer.startSpan('process-order');
try {
  await processOrder();
} finally {
  span.end();
}
```

❌ **Mistake 3:** Not propagating context across async boundaries or message queues
```javascript
// WRONG — publishing to a queue without injecting trace context means the
// consumer service starts a BRAND NEW trace, breaking the end-to-end view
queue.publish('order-created', { orderId: 123 });

// CORRECT — inject trace context into the message so the consumer can
// continue the SAME trace (context propagation across async boundaries)
const headers = {};
propagation.inject(context.active(), headers);
queue.publish('order-created', { orderId: 123, traceHeaders: headers });
```

---

## 🧠 Tricky Interview Question

**Q: You see TWO separate traces in Jaeger for what should be ONE user request that hits `api-gateway` then calls `order-service` over HTTP. Why might they be disconnected?**

```javascript
// api-gateway makes a raw http.request() WITHOUT letting OTel inject headers
const http = require('http');
http.request({ hostname: 'order-service', path: '/orders/1' }, (res) => {...}).end();
// No propagation.inject() call — traceparent header never sent!
```

Answer: OpenTelemetry connects spans across services via the **`traceparent` HTTP header** (W3C Trace Context standard), which carries the trace ID and parent span ID. If auto-instrumentation is active on both ends AND they use the SAME http client/server mechanisms it patches, this usually happens automatically. But if the outgoing call bypasses the patched client (e.g., a raw socket, a custom library OTel doesn't auto-instrument, or headers get stripped by an intermediate proxy/load balancer), the receiving service has no `traceparent` to continue from — so it starts a brand-new root trace. Fix: ensure the http client library is in OTel's auto-instrumentation list, or manually call `propagation.inject()` to attach `traceparent` to outgoing requests, and make sure no proxy strips custom headers.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between OpenTelemetry and a vendor-specific APM agent like New Relic's SDK?**
A1: A vendor SDK (New Relic, Datadog) is proprietary — instrumentation code calls vendor-specific APIs and data format, locking you to that backend. OpenTelemetry is a vendor-neutral, open standard (CNCF project) — you instrument once using OTel's API, and the actual destination is decided by a pluggable Exporter. Switching from Jaeger to Datadog to Prometheus requires only changing exporter config, not re-instrumenting code. Most modern APM vendors (including New Relic and Datadog) now also accept OTel-formatted data directly via OTLP.

**Q2: What are the three pillars of OpenTelemetry observability?**
A2: **Traces** — the path of a single request through the system, broken into spans (useful for latency/root-cause debugging). **Metrics** — numeric time-series data like request count, CPU usage, error rate (useful for dashboards/alerting over time). **Logs** — timestamped event records with context, now correlatable with trace IDs so you can jump from a log line to its full distributed trace. OTel standardizes the collection and correlation of all three.

**Q3: What does "auto-instrumentation" mean in OpenTelemetry, and what are its limits?**
A3: Auto-instrumentation (via `@opentelemetry/auto-instrumentations-node`) automatically patches well-known libraries (http, express, pg, mongodb, redis, etc.) to create spans without writing any tracing code — covering ~80% of typical visibility needs. Its limits: it can't see custom business logic (e.g., "calculate discount" isn't an HTTP call or DB query) — for that you manually create custom spans using the Tracer API (`tracer.startActiveSpan`) to add business-specific visibility.

**Q4: How does context propagation work across microservices in OpenTelemetry?**
A4: Each span belongs to a Trace (identified by a Trace ID) and has a Span ID; a child span also references its Parent Span ID. When Service A calls Service B over HTTP, OTel's `propagation.inject()` serializes the current trace context into the W3C `traceparent` header on the outgoing request. Service B's instrumentation reads that header via `propagation.extract()` and creates its own span as a CHILD of A's span — even though they're different processes/services — letting tools like Jaeger reconstruct the full distributed call tree.

**Q5: Why would a company migrate from a single-vendor APM to OpenTelemetry even if it means some upfront engineering work?**
A5: Avoiding vendor lock-in (can switch backends without re-instrumenting), standardizing instrumentation across teams/services using different vendors historically, getting trace continuity across a polyglot/multi-vendor microservices architecture, future-proofing (OTel is the emerging industry standard supported by virtually every observability vendor), and reducing long-term maintenance cost of custom per-vendor instrumentation code scattered across dozens of services.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You run (or plan to run) multiple microservices and need consistent, cross-service traceability.
- You want to avoid vendor lock-in or might switch observability backends later.
- You need custom business-logic-level tracing beyond what auto-instrumentation covers.

❌ Avoid when:
- A single tiny monolith/script with no distributed calls — the setup overhead isn't worth it; simple logging may suffice.
- Your team is already deeply invested in one vendor's proprietary advanced features (e.g., New Relic's specific anomaly detection) that OTel's standard model doesn't fully replicate (though this gap is shrinking fast).

---

## 📊 Visual Diagram
```
OPENTELEMETRY ARCHITECTURE:
────────────────────────────────────────────────────────────────

  [api-gateway]        [order-service]       [payment-service]
       │ Span A              │ Span B               │ Span C
       │ traceId: T1         │ traceId: T1           │ traceId: T1
       │ spanId: S1          │ spanId: S2             │ spanId: S3
       │                     │ parentSpan: S1          │ parentSpan: S2
       │── HTTP call ───────▶│                         │
       │   traceparent: T1-S1│                         │
       │                     │── HTTP call ───────────▶│
       │                     │   traceparent: T1-S2     │
       │                     │                         │
       └─────────────────────┴─────────────────────────┘
                              │
                 All spans share traceId T1
                              │
                              ▼
                 ┌─────────────────────────┐
                 │   OTel SDK Collector      │
                 │ (buffers + batches spans) │
                 └────────────┬──────────────┘
                              │ Exporter (pluggable!)
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
      [ Jaeger ]         [ Prometheus ]        [ Datadog ]
     (trace viewer)      (metrics scrape)    (full APM backend)

  Swap any backend above by changing EXPORTER CONFIG ONLY.
  Application code never changes.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OpenTelemetry (OTel) | Vendor-neutral observability standard | Vendor-neutral observability standard |
| Span | Single traced operation with start/end time | एक traced operation, start/end time के साथ |
| Trace | Collection of spans forming one request's full path | पूरे request का path बनाने वाले spans का group |
| Exporter | Pluggable component sending data to a backend | Backend को data भेजने वाला pluggable part |
| Auto-instrumentation | Automatic patching of libraries for tracing | Libraries का automatic patching tracing के लिए |
| Context Propagation | Passing trace info across service boundaries | Trace info को services के बीच pass करना |
| traceparent | W3C header carrying trace/span IDs across HTTP calls | HTTP calls में trace/span IDs ले जाने वाला header |
| OTLP | OpenTelemetry Protocol — standard export format | Standard export format |
| CNCF | Cloud Native Computing Foundation — governs OTel | OTel को govern करने वाली foundation |

---

## ⚡ 3-Line Summary
**English:**
1. OpenTelemetry is a vendor-neutral standard to collect traces, metrics, and logs — instrument once, export to ANY backend (Jaeger, Prometheus, Datadog) by just changing exporter config.
2. Auto-instrumentation patches common libraries automatically; custom spans via the Tracer API cover business logic auto-instrumentation can't see.
3. Context propagation via the `traceparent` header links spans across microservices into one coherent distributed trace.

**Hindi:**
1. OpenTelemetry एक vendor-neutral standard है traces, metrics, logs collect करने के लिए — एक बार instrument करो, exporter config बदलकर किसी भी backend (Jaeger, Prometheus, Datadog) पर export करो।
2. Auto-instrumentation common libraries को automatically patch करता है; custom spans Tracer API से business logic को cover करते हैं जो auto-instrumentation नहीं देख सकता।
3. `traceparent` header के through context propagation spans को microservices के across जोड़ता है, एक coherent distributed trace बनाकर।

---

## ➡️ Next Topic
**257. Distributed Tracing** — एक request को multiple microservices के across कैसे trace करें, trace ID/span ID propagation, parent-child spans, Jaeger/Zipkin tools।
