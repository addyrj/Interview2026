# 257. Distributed Tracing
# हिंदी में: Distributed Tracing — Multiple Services के across Request Track करना

---

## 🔵 Simple Definition (English)
**Distributed Tracing** is a technique to follow a single user request as it travels across MULTIPLE microservices, by attaching a shared **Trace ID** to every service call and breaking each service's work into **Spans** (parent-child timed operations). Tools like **Jaeger** and **Zipkin** visualize the entire journey as one timeline, so you can instantly see which service in the chain is slow or failing.

## 🔵 सरल परिभाषा (Hindi)
**Distributed Tracing** एक technique है जो एक user request को track करती है जब वह **multiple microservices** के across travel करती है — हर service call पर एक shared **Trace ID** attach करके, और हर service के काम को **Spans** (parent-child timed operations) में तोड़कर। **Jaeger** और **Zipkin** जैसे tools पूरी journey को एक timeline में दिखाते हैं, ताकि instantly पता चले कि chain में कौन सी service slow है या fail हो रही है।

---

## 🔴 Problem it Solves
```
BEFORE DISTRIBUTED TRACING (microservices, no tracing):
  User: "My order checkout is slow / failed!"

  Request path: api-gateway → order-service → payment-service → notification-service

  Debugging without tracing:
    1. SSH into api-gateway logs — search by rough timestamp → maybe find it
    2. SSH into order-service logs — search again by timestamp → maybe find it
    3. SSH into payment-service logs — search again → maybe find it
    4. SSH into notification-service logs — search again → maybe find it
    5. Logs have NO common identifier linking them — you're guessing based
       on timestamps, which is unreliable under concurrent traffic
    6. Takes 30+ minutes to manually correlate 4 services' worth of logs
       for ONE request, if you're lucky enough to even find it

WITH DISTRIBUTED TRACING:
    1. Get the Trace ID (from an error alert, a support ticket, or a log line)
    2. Paste it into Jaeger UI search box
    3. See ENTIRE request path as a single timeline/waterfall:
       api-gateway (5ms) → order-service (20ms) → payment-service (2800ms!) 
                                                     → notification-service (10ms)
    4. Immediately see payment-service is the bottleneck — click in to see
       WHY (external gateway timeout, DB lock, etc.)
    5. Total debugging time: under 2 minutes
```

## 🔴 यह क्यों बना? (Hindi)
```
Distributed Tracing से पहले (microservices, tracing नहीं):
  User: "मेरा order checkout slow है / fail हो गया!"

  Request path: api-gateway → order-service → payment-service → notification-service

  Tracing के बिना debugging:
    1. api-gateway logs में SSH करो — rough timestamp से search करो
    2. order-service logs में फिर SSH — फिर timestamp से search
    3. payment-service logs में फिर SSH — फिर search
    4. notification-service logs में फिर SSH — फिर search
    5. Logs में कोई common identifier नहीं जो उन्हें link करे — timestamps
       के आधार पर guess कर रहे हो, जो concurrent traffic में unreliable है
    6. एक request के लिए 4 services के logs manually correlate करने में
       30+ minutes लग जाते हैं, अगर मिल भी जाए तो

Distributed Tracing के साथ:
    1. Trace ID लो (error alert, support ticket, या log line से)
    2. Jaeger UI search box में paste करो
    3. पूरा request path एक single timeline/waterfall में दिखता है:
       api-gateway (5ms) → order-service (20ms) → payment-service (2800ms!)
                                                     → notification-service (10ms)
    4. तुरंत दिखता है payment-service bottleneck है — click करके WHY देखो
       (external gateway timeout, DB lock, आदि)
    5. Total debugging time: 2 minutes से कम
```

---

## 🟢 How it Works — Step by Step

Step 1 → When a request first enters the system (e.g. at `api-gateway`), a new **Trace ID** (globally unique, e.g. UUID) is generated — this ID will represent the ENTIRE request's journey.
Step 2 → `api-gateway` starts its own **Span** (Span A) with that Trace ID, does its work, and when calling `order-service`, it attaches the Trace ID + its own Span ID as a **parent reference** inside an HTTP header (`traceparent`).
Step 3 → `order-service` receives the header, extracts the Trace ID, and creates its own Span (Span B) marked as a **child of Span A** — same Trace ID, new Span ID, `parentSpanId = Span A`.
Step 4 → `order-service` calls `payment-service`, propagating the SAME Trace ID + its own Span ID forward, again via headers — `payment-service` creates Span C as a child of Span B.
Step 5 → This chain continues through `notification-service` (Span D, child of Span C). Each span records start time, end time, status (success/error), and custom tags.
Step 6 → Each service exports its completed spans to a central collector (Jaeger/Zipkin collector), which stores them keyed by Trace ID.
Step 7 → The Jaeger/Zipkin UI queries by Trace ID and reconstructs the full parent-child tree as a waterfall diagram — showing exactly how much time each service/span consumed.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Request जब पहली बार system में enter होती है (जैसे `api-gateway` पर), एक नया **Trace ID** (globally unique, जैसे UUID) generate होता है — यह ID पूरी request की journey को represent करेगा।
Step 2 → `api-gateway` अपना **Span** (Span A) उस Trace ID के साथ start करता है, अपना काम करता है, और `order-service` को call करते समय, Trace ID + अपना Span ID एक **parent reference** की तरह HTTP header (`traceparent`) में attach करता है।
Step 3 → `order-service` header receive करता है, Trace ID extract करता है, और अपना Span (Span B) बनाता है जो **Span A का child** मार्क होता है — same Trace ID, नया Span ID, `parentSpanId = Span A`।
Step 4 → `order-service` `payment-service` को call करता है, same Trace ID + अपना Span ID forward propagate करता है, फिर headers के through — `payment-service` Span C बनाता है, Span B का child।
Step 5 → यह chain `notification-service` तक continue होती है (Span D, Span C का child)। हर span start time, end time, status (success/error), custom tags record करता है।
Step 6 → हर service अपने complete spans को एक central collector (Jaeger/Zipkin collector) को export करती है, जो उन्हें Trace ID के हिसाब से store करता है।
Step 7 → Jaeger/Zipkin UI Trace ID से query करता है और पूरा parent-child tree एक waterfall diagram की तरह reconstruct करता है — exactly दिखाता है कि हर service/span ने कितना time लिया।

---

## 🟡 Real World Example
**Zomato order flow:** A customer places an order. The request hits `api-gateway`, which calls `order-service` to create the order, which then calls `payment-service` to charge the customer, which then calls `notification-service` to send an SMS/push notification. One day, customers report "order confirmation SMS comes 10 seconds late." Engineer grabs the Trace ID from the order's audit log, opens Jaeger, and sees the waterfall: `api-gateway` (8ms) → `order-service` (45ms) → `payment-service` (120ms) → `notification-service` (9800ms!). Drilling into `notification-service`'s span reveals a child span `external.sms-gateway.send` taking 9.7 seconds — the third-party SMS provider (not their own code) is the bottleneck. Without distributed tracing, the team would have wrongly suspected `payment-service` or their own notification code first.

## 🟡 Real Example Hindi mein
**Zomato order flow:** Customer order place करता है। Request `api-gateway` पर आती है, जो `order-service` को call करती है order बनाने के लिए, जो फिर `payment-service` को call करती है customer को charge करने के लिए, जो फिर `notification-service` को call करती है SMS/push notification भेजने के लिए। एक दिन customers complain करते हैं "order confirmation SMS 10 seconds late आता है।" Engineer order के audit log से Trace ID लेता है, Jaeger खोलता है, और waterfall देखता है: `api-gateway` (8ms) → `order-service` (45ms) → `payment-service` (120ms) → `notification-service` (9800ms!)। `notification-service` के span में drill करने पर एक child span `external.sms-gateway.send` दिखता है जो 9.7 seconds ले रहा है — third-party SMS provider (उनका अपना code नहीं) bottleneck है। Distributed tracing के बिना, team गलती से पहले `payment-service` या अपने notification code को suspect करती।

---

## 💻 Code Example — Basic

```javascript
// basic-trace-propagation.js
// A minimal, hand-rolled demonstration of trace ID / span ID propagation
// (the CORE idea behind Jaeger/Zipkin) WITHOUT any external library.
// Run: node basic-trace-propagation.js

const crypto = require('crypto'); // for generating random IDs

// Generates a short random hex ID — stand-in for a real trace/span ID
function generateId() {
  return crypto.randomBytes(8).toString('hex');
}

// Simulates one "service" doing work and calling the next service
function callService(serviceName, traceId, parentSpanId, work) {
  const spanId = generateId();         // this service's own span ID
  const start = Date.now();            // span start time

  console.log(
    `[${serviceName}] traceId=${traceId} spanId=${spanId} parentSpanId=${parentSpanId || 'none (root)'}`
  );

  const result = work(traceId, spanId); // do the actual work, passing trace context forward

  const duration = Date.now() - start;
  console.log(`[${serviceName}] span finished in ${duration}ms`);
  return result;
}

// ─── Simulate: api-gateway → order-service → payment-service ──────────────
function simulateRequest() {
  const traceId = generateId(); // ROOT: new trace starts here, at the entry point

  callService('api-gateway', traceId, null, (traceId, gatewaySpanId) => {
    // api-gateway calls order-service, passing traceId + its own span as parent
    callService('order-service', traceId, gatewaySpanId, (traceId, orderSpanId) => {
      // order-service calls payment-service, passing traceId + its own span as parent
      callService('payment-service', traceId, orderSpanId, () => {
        // Simulate payment processing taking some time
        const start = Date.now();
        while (Date.now() - start < 50) {} // busy-wait 50ms to simulate work
        return { status: 'SUCCESS' };
      });
    });
  });
}

simulateRequest();
// Output shows all 3 spans sharing the SAME traceId, each with a
// parentSpanId pointing to the service that called it — exactly what
// Jaeger reconstructs into a waterfall diagram.
```

## 💻 Code Example — Advanced

```javascript
// advanced-distributed-trace.js
// Realistic HTTP-based propagation using Express + a simple in-memory
// "trace collector" to mimic how Jaeger aggregates spans by traceId.
// Run: node advanced-distributed-trace.js (starts 3 servers on one process for demo)

const express = require('express');
const http = require('http');
const crypto = require('crypto');

// ─── IN-MEMORY TRACE COLLECTOR (stand-in for Jaeger's collector) ──────────
const collectedSpans = []; // array of all finished spans, grouped later by traceId

function recordSpan(span) {
  collectedSpans.push(span);
}

function generateId() {
  return crypto.randomBytes(8).toString('hex');
}

// ─── MIDDLEWARE: extracts or creates trace context from headers ───────────
function tracingMiddleware(serviceName) {
  return (req, res, next) => {
    // Extract incoming trace context (sent by the caller), or start a new trace if none
    const traceId = req.headers['x-trace-id'] || generateId(); // reuse if present, else new root trace
    const parentSpanId = req.headers['x-span-id'] || null;      // caller's span becomes our parent
    const spanId = generateId();                                 // this service's own new span

    const start = Date.now();
    req.traceContext = { traceId, spanId }; // store so route handlers can propagate it further

    res.on('finish', () => {
      // Record the completed span once the response is sent
      recordSpan({
        service: serviceName,
        traceId,
        spanId,
        parentSpanId,
        durationMs: Date.now() - start,
        statusCode: res.statusCode,
        path: req.path,
      });
    });

    next();
  };
}

// Helper to make a downstream call while propagating trace context in headers
function callDownstream(hostname, port, path, traceContext) {
  return new Promise((resolve, reject) => {
    const req = http.request(
      {
        hostname,
        port,
        path,
        method: 'GET',
        headers: {
          'x-trace-id': traceContext.traceId,  // propagate SAME trace ID forward
          'x-span-id': traceContext.spanId,    // propagate THIS span as the next parent
        },
      },
      (res) => {
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => resolve(JSON.parse(body || '{}')));
      }
    );
    req.on('error', reject);
    req.end();
  });
}

// ─── SERVICE 3: payment-service (deepest call, port 5002) ─────────────────
const paymentApp = express();
paymentApp.use(tracingMiddleware('payment-service'));
paymentApp.get('/charge', (req, res) => {
  setTimeout(() => res.json({ status: 'PAID' }), 150); // simulate gateway latency
});
paymentApp.listen(5002, () => console.log('payment-service on 5002'));

// ─── SERVICE 2: order-service (port 5001) ──────────────────────────────────
const orderApp = express();
orderApp.use(tracingMiddleware('order-service'));
orderApp.get('/create', async (req, res) => {
  const paymentResult = await callDownstream('localhost', 5002, '/charge', req.traceContext);
  res.json({ order: 'created', payment: paymentResult });
});
orderApp.listen(5001, () => console.log('order-service on 5001'));

// ─── SERVICE 1: api-gateway (entry point, port 5000) ───────────────────────
const gatewayApp = express();
gatewayApp.use(tracingMiddleware('api-gateway'));
gatewayApp.get('/checkout', async (req, res) => {
  const orderResult = await callDownstream('localhost', 5001, '/create', req.traceContext);
  res.json({ checkout: 'complete', ...orderResult });

  // After responding, print the reconstructed trace (like Jaeger UI would show)
  setTimeout(() => {
    const trace = collectedSpans.filter((s) => s.traceId === req.traceContext.traceId);
    console.log('\n--- RECONSTRUCTED TRACE ---');
    trace.forEach((s) =>
      console.log(`${s.service} | span=${s.spanId} parent=${s.parentSpanId || 'root'} | ${s.durationMs}ms`)
    );
  }, 300);
});
gatewayApp.listen(5000, () => console.log('api-gateway on 5000 — try GET /checkout'));
```

---

## 🟠 Express.js Integration

```javascript
// Real-world pattern: wiring OpenTelemetry + Jaeger exporter into Express
// npm install @opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node
//             @opentelemetry/exporter-jaeger

// tracing.js — load this FIRST (node -r ./tracing.js app.js)
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { JaegerExporter } = require('@opentelemetry/exporter-jaeger');

const sdk = new NodeSDK({
  serviceName: 'order-service', // shows up as this service's name in Jaeger UI
  traceExporter: new JaegerExporter({
    endpoint: 'http://localhost:14268/api/traces', // Jaeger collector endpoint
  }),
  instrumentations: [getNodeAutoInstrumentations()], // auto-traces express routes + outgoing http calls
});
sdk.start();

// app.js — your Express routes need ZERO manual tracing code;
// auto-instrumentation handles trace ID generation + header propagation automatically.
const express = require('express');
const app = express();

app.get('/orders/:id', async (req, res) => {
  // Any outgoing http.request() or axios call here automatically propagates
  // the current trace context via the traceparent header — no manual code!
  const paymentStatus = await axios.get(`http://payment-service/status/${req.params.id}`);
  res.json({ orderId: req.params.id, paymentStatus: paymentStatus.data });
});

app.listen(3000, () => console.log('order-service running with Jaeger tracing'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Generating a NEW trace ID in every service instead of propagating the existing one
```javascript
// WRONG — order-service ignores incoming trace context, starts fresh
app.get('/create', (req, res) => {
  const traceId = crypto.randomUUID(); // ignores req.headers['x-trace-id']!
  // Now this service's work is DISCONNECTED from the parent trace in Jaeger
});

// CORRECT — always check for and reuse an incoming trace ID; only generate
// a new one if this service is the TRUE entry point (no incoming header)
app.get('/create', (req, res) => {
  const traceId = req.headers['x-trace-id'] || crypto.randomUUID();
});
```

❌ **Mistake 2:** Not propagating trace headers through async message queues
```javascript
// WRONG — publishing a Kafka/RabbitMQ message without trace context means
// the consumer starts a disconnected, brand-new trace
channel.publish('order-events', Buffer.from(JSON.stringify({ orderId: 1 })));

// CORRECT — include trace context in the message payload/headers so the
// consumer can continue the SAME distributed trace
channel.publish('order-events', Buffer.from(JSON.stringify({
  orderId: 1,
  traceContext: { traceId: req.traceContext.traceId, spanId: req.traceContext.spanId },
})));
```

❌ **Mistake 3:** Sampling 100% of traces in a very high-throughput service
```javascript
// WRONG — tracing EVERY request at huge scale (e.g. 50k req/sec) creates
// massive storage cost and collector overhead in Jaeger
const sdk = new NodeSDK({ /* no sampler config = trace everything */ });

// CORRECT — use a sampling strategy (e.g. trace 10% of requests, or always
// trace requests with errors) to balance visibility with cost/overhead
const { TraceIdRatioBasedSampler } = require('@opentelemetry/sdk-trace-base');
const sdk = new NodeSDK({ sampler: new TraceIdRatioBasedSampler(0.1) }); // 10% sampling
```

---

## 🧠 Tricky Interview Question

**Q: In the trace below, `payment-service`'s span shows a duration of 2000ms, but when you sum up ALL of payment-service's own child spans (DB query 50ms + gateway call 100ms), they only add up to 150ms. Where did the other 1850ms go?**

```
payment-service span: 2000ms total
  ├── db.query span: 50ms
  └── external.gateway.call span: 100ms
  (gap: 1850ms unaccounted for)
```

Answer: This is a classic sign of **time NOT spent inside traced operations** — usually the event loop was blocked or delayed BEFORE the traced work even started. Common causes: (1) the request sat in Node's event loop queue waiting because of CPU-bound synchronous code blocking elsewhere in the process (e.g., a big `JSON.parse` or a synchronous crypto operation on another request hogging the single thread); (2) the process was under heavy GC pressure (garbage collection pauses aren't spans, but they delay everything); (3) a connection pool was exhausted and the code waited to ACQUIRE a DB connection before the "db.query" span even started timing (the wait-for-connection time often isn't instrumented, only the query execution itself is). The fix is to add a span around connection-pool acquisition too, and to check Node's event loop lag metrics (e.g. `perf_hooks` or the APM's event-loop-delay metric) to rule out event-loop blocking.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between a Trace and a Span?**
A1: A **Trace** represents the ENTIRE journey of one request across all services, identified by a single Trace ID. A **Span** represents ONE unit of work within that trace (e.g., "order-service handling this request", or "DB query inside order-service") — each span has its own Span ID, a start/end time, and (except the root span) a Parent Span ID linking it to the span that triggered it. A trace is the full tree; spans are its nodes.

**Q2: How is the trace context propagated between two microservices communicating over HTTP?**
A2: The calling service attaches the current trace ID and its own span ID into an HTTP header (standardized as `traceparent` under W3C Trace Context, though custom headers like `x-trace-id`/`x-span-id` work too in simpler setups). The receiving service's tracing middleware reads that header, extracts the trace ID, and creates a new span marked as a CHILD of the incoming span ID. This is how tools reconstruct the full call graph even though each service is a separate process/machine.

**Q3: What happens to a distributed trace if context propagation is skipped at one hop, e.g., through a message queue?**
A3: The trace is "broken" at that point — the consuming service, lacking any incoming trace context, starts a brand NEW root trace with its own trace ID. In the tracing UI (Jaeger/Zipkin), this shows up as two disconnected traces instead of one continuous one, even though they're logically the same business request. This is why async communication (Kafka, RabbitMQ, SQS) needs explicit trace context injection into message headers/payload, since there's no HTTP header channel to rely on automatically.

**Q4: Why is sampling important in distributed tracing at scale, and what sampling strategies exist?**
A4: At high request volumes (thousands/sec), tracing every single request generates enormous data volume and processing/storage cost in the tracing backend. Sampling strategies: (1) **Head-based sampling** — decide at the START of a trace (e.g., keep 10% randomly) before knowing the outcome; simple but might miss rare errors. (2) **Tail-based sampling** — decide AFTER the full trace completes, e.g., always keep traces with errors or very high latency, discard "boring" fast successful ones; more useful but requires buffering all spans before deciding, which is more complex/expensive to run.

**Q5: How would you debug a case where Jaeger shows a trace with a 10-second gap between two spans, with no child span explaining it?**
A5: Check for event loop blocking (CPU-heavy synchronous code elsewhere delaying this request's processing — profile with `clinic.js` or Node's `--prof` flag), check for resource acquisition waits not currently instrumented (e.g., waiting for a free DB connection from a pool, waiting on a mutex/lock), check for GC pauses (`node --trace-gc` or APM's GC metrics), and check if a downstream call used a library NOT covered by auto-instrumentation (so its work happened but produced no span) — in that case, add a manual custom span around that call to make the gap visible.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Your system has 2+ services calling each other (microservices, service-oriented architecture) and you need to debug cross-service latency/errors.
- You need to answer "which service in this request chain is slow/failing" quickly instead of manually correlating logs.
- You're running async workflows (queues, event-driven systems) where request flow isn't a simple linear HTTP chain.

❌ Avoid when:
- A single monolithic service with no inter-service calls — there's nothing "distributed" to trace; plain APM/logging is simpler and sufficient.
- Extremely resource-constrained environments where even sampled tracing overhead is unacceptable (rare, but consider very low sampling rates instead of fully avoiding).

---

## 📊 Visual Diagram
```
DISTRIBUTED TRACE — ONE CHECKOUT REQUEST ACROSS 4 SERVICES:
──────────────────────────────────────────────────────────────

  traceId = T1  (same across ALL services below)

  api-gateway        [Span A: 0ms ─────────────────────────── 5000ms]
                        │
  order-service          [Span B: 10ms ──────────────── 4950ms]
                            │ parentSpanId = A
                            │
  payment-service              [Span C: 50ms ──── 4800ms]   ⚠️ SLOW!
                                  │ parentSpanId = B
                                  │
  notification-service               [Span D: 4850ms - 4900ms]
                                        │ parentSpanId = C

  JAEGER UI WATERFALL VIEW:
  ┌──────────────────────────────────────────────────────────┐
  │ api-gateway        ████████████████████████████████  5000ms│
  │   order-service      ███████████████████████████     4940ms│
  │     payment-service     ████████████████████████     4750ms│ ← bottleneck!
  │       notification-svc                           ██     50ms│
  └──────────────────────────────────────────────────────────┘
  → payment-service is clearly where most time is spent.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trace | Full journey of one request across services | एक request की पूरी journey, services के across |
| Trace ID | Unique ID shared by all spans in one trace | पूरे trace में shared unique ID |
| Span | One traced unit of work (with start/end time) | एक traced work unit, start/end time के साथ |
| Parent-Child Span | Span created because of another span's call | दूसरे span के call से बना span |
| Context Propagation | Passing trace info forward via headers | Headers के through trace info आगे पास करना |
| Jaeger / Zipkin | Open-source distributed tracing backends/UIs | Open-source tracing backends/UIs |
| Waterfall View | Visual timeline of spans showing durations | Spans का visual timeline, durations दिखाते हुए |
| Sampling | Tracing only a subset of requests to reduce cost | Cost कम करने के लिए सिर्फ कुछ requests trace करना |

---

## ⚡ 3-Line Summary
**English:**
1. Distributed tracing follows one request across multiple microservices by sharing a Trace ID and linking each service's work as parent-child Spans.
2. Context propagation via HTTP headers (or message payloads for async systems) is what connects spans across process/service boundaries into one trace.
3. Tools like Jaeger/Zipkin visualize the full trace as a waterfall, instantly showing which service in the chain is the real bottleneck.

**Hindi:**
1. Distributed tracing एक request को multiple microservices के across follow करता है, एक shared Trace ID और parent-child Spans के through।
2. HTTP headers (या async systems में message payloads) के through context propagation ही spans को process/service boundaries के across एक trace में जोड़ता है।
3. Jaeger/Zipkin जैसे tools पूरे trace को waterfall की तरह दिखाते हैं, instantly बताते हुए कि chain में कौन सी service असली bottleneck है।

---

## ➡️ Next Topic
**258. Deploying Node.js on VPS** — Linux VPS setup (DigitalOcean/AWS Lightsail/Hetzner), nvm, PM2, firewall, SSH keys — production पर अपना Node.js app live करना।
