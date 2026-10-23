# 102. Observability — Traces (Distributed Tracing)
# हिंदी में: Distributed Tracing — एक request का कई services से होकर गुज़रने का पूरा रास्ता और हर कदम में लगा समय (spans) देखना, ताकि पता चले देरी या error कहाँ है

---

## 🔵 Simple Definition (English)
A **trace** records the **end-to-end journey of one request** through a distributed system. It's made of **spans**: each span is one unit of work (an HTTP handler, a DB query, a Redis call, a Kafka publish, an external API call) with **start time, duration, attributes, status** and a **parent span**. All spans share a **trace ID**, propagated across services in headers (W3C `traceparent`).
Tools: **OpenTelemetry** (standard SDKs + collector), Jaeger, Zipkin, Grafana Tempo, AWS X-Ray, Datadog APM, Honeycomb, New Relic.

## 🔵 सरल परिभाषा (Hindi)
Trace एक request की पूरी यात्रा है — gateway → order service → payment service → DB → बाहरी API — और हर कदम (span) में कितना समय लगा।
सारे spans एक trace ID से जुड़े होते हैं जो headers में आगे जाती है। इससे तुरंत दिखता है कि 3 सेकंड में से 2.5 सेकंड कहाँ गए।

---

## 🔴 Problem it Solves
"Checkout p99 is 3 seconds." With 10 services involved:
- **Metrics** say checkout is slow but not **where**.
- **Logs** from each service are separate; stitching them by time is painful and error-prone.
- Latency hides in **sequential calls**, **N+1 queries**, **retries**, **queue waits**, **slow third-party APIs**.

Tracing shows a **waterfall** of the exact request: which service, which DB query, which external call, which retry consumed the time, and where the error originated.

## 🔴 यह क्यों बना? (Hindi)
"Checkout 3 सेकंड लेता है" — 10 services शामिल हैं। Metrics बताते हैं धीमा है, पर कहाँ नहीं; हर service के logs अलग-अलग, समय से जोड़ना मुश्किल।
Trace एक waterfall दिखाता है — किस service, किस DB query, किस बाहरी API या किस retry ने समय खाया, और error कहाँ से शुरू हुई।

---

## 🟢 How it Works — Step by Step

### A trace as a waterfall

```
Trace 4bf92f35...  POST /api/v1/checkout   total 2,940 ms
├─ gateway  POST /checkout                                   [0 ────────────────────────── 2940]
│  └─ order-svc  placeOrder                                    [5 ───────────────────────── 2930]
│     ├─ postgres  SELECT menu_items (N+1? 40 queries!)          [10 ── 420]
│     ├─ redis  GET coupon:DIWALI                                     [425 ─ 427]
│     ├─ payment-svc  POST /charges                                   [430 ──────────── 2600]
│     │  ├─ postgres INSERT charges                                     [435 ─ 445]
│     │  └─ razorpay  POST /payments   (retry #2, status=OK)            [450 ──────── 2590]  ← 2.1 s!
│     └─ kafka  publish order.placed                                                       [2605 ─ 2612]
Root cause visible immediately: slow payment provider + retry; plus N+1 menu queries.
```

### Core concepts

```
Trace      → one request end-to-end (trace_id, 16 bytes)
Span       → one operation (span_id, parent_span_id, name, start, end, status, attributes, events)
Context propagation → pass trace_id + parent span_id to the next hop:
   HTTP/gRPC header:  traceparent: 00-<trace_id>-<span_id>-01   (W3C Trace Context)
   Kafka/SQS headers, job payloads → async hops linked too ("span links" for fan-out/batches)
Attributes → http.route, http.status_code, db.statement (sanitized), user.id (careful), order.id
Baggage    → small key-values propagated across services (tenant, experiment id)
```

### OpenTelemetry architecture

```
App + OTel SDK (auto-instrumentation for HTTP, Express, pg, Redis, Kafka, gRPC, fetch)
     │  OTLP (gRPC/HTTP)
     ▼
OTel Collector (agent/gateway): batch, sample, add resource attrs, scrub PII, export
     │
     ├──► Jaeger / Grafana Tempo / Zipkin (open source)
     ├──► AWS X-Ray, Datadog, Honeycomb, New Relic (vendor)
     └──► Metrics/logs backends (same pipeline for all three signals)
Vendor-neutral: switch backends without re-instrumenting code.
```

### Sampling (traces are expensive at full volume)

```
Head sampling:  decide at the start (e.g. keep 5% of traces) — cheap, may miss rare errors
Tail sampling:  decide after the trace completes (in the collector):
                keep 100% of errors, 100% of slow (> 1 s) traces, 1–5% of normal ones ⭐
Always-sample:  for specific users/debug sessions (header flag) or low-traffic services
```

### Linking the three pillars
```
- Log lines include trace_id/span_id → click from a trace to its logs
- Exemplars: a latency histogram bucket links to an example trace id (Grafana)
- RED metrics can be derived from spans (span metrics)
Workflow: alert (metric) → find exemplar trace → see slow span → open its logs → root cause
```

### What tracing reveals that others don't
```
- Sequential calls that could be parallel
- N+1 DB queries (dozens of tiny identical spans)
- Retries and timeouts hidden inside client libraries
- Queue wait time (producer span → consumer span gap)
- Which downstream dependency causes errors (error status propagates up)
- Fan-out cost in BFFs/GraphQL resolvers
```

## 🟢 कैसे काम करता है? (Hindi)
1. Request आते ही एक trace ID बनती है; हर काम (HTTP handler, DB query, Redis, बाहरी API) एक span है जिसका start, अवधि और parent होता है।
2. अगली service को `traceparent` header में trace ID भेजी जाती है (Kafka/queue headers में भी), ताकि सब spans जुड़ जाएँ।
3. OpenTelemetry SDK ज़्यादातर चीज़ें (Express, pg, Redis, fetch) अपने आप trace करता है; Collector उन्हें Jaeger/Tempo/X-Ray भेजता है।
4. Waterfall में साफ़ दिखता है: N+1 queries, धीमा payment provider, retries, queue में इंतज़ार।
5. सब traces रखना महँगा है — tail sampling: सारे errors और धीमे traces रखो, सामान्य में से 1-5%; logs में trace_id डालो ताकि trace से logs पर जा सको।

---

## 🟡 Real World Example

**Google Dapper (2010 paper)** — Google's tracing system, which inspired Zipkin (Twitter), Jaeger (Uber) and eventually OpenTelemetry. Dapper showed that low-overhead sampled tracing is practical at Google scale.

**Uber Jaeger** — built and open-sourced by Uber to trace thousands of microservices. Now a CNCF graduated project.

**Shopify / Stripe / Swiggy-scale companies** — use tracing to find slow dependencies during sales events. A common discovery is a "harmless" synchronous call to a non-critical service (recommendations, analytics) sitting in the checkout path.

**OpenTelemetry** — the CNCF's second most active project after Kubernetes. It's the industry standard: AWS, Google, Microsoft, Datadog and Grafana all support OTLP.

## 🟡 Real Example Hindi में
Google के Dapper paper (2010) से Zipkin (Twitter), Jaeger (Uber) और फिर OpenTelemetry बने। Uber ने हज़ारों services trace करने के लिए Jaeger बनाया।
Sale के समय कंपनियाँ tracing से पाती हैं कि checkout में कोई "छोटी" ग़ैर-ज़रूरी कॉल (recommendations) अटकी हुई है। आज OpenTelemetry मानक है — AWS, Google, Datadog सब इसे मानते हैं।

---

## 🟠 My Stack Example

### Node.js — OpenTelemetry auto-instrumentation (load FIRST)
```js
// tracing.js  →  node --import ./tracing.js dist/server.js
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';

// version/env can also come from OTEL_RESOURCE_ATTRIBUTES="service.version=1.9.2,deployment.environment=prod"
new NodeSDK({
  serviceName: 'order-svc',
  traceExporter: new OTLPTraceExporter({ url: 'http://otel-collector:4318/v1/traces' }),
  instrumentations: [getNodeAutoInstrumentations({
    '@opentelemetry/instrumentation-fs': { enabled: false },                // too noisy
  })],
}).start();
// Express, http, fetch/undici, pg, ioredis/redis, kafkajs, grpc are traced automatically,
// and traceparent headers are injected/extracted automatically.
```

### Custom spans for business steps
```js
import { trace, SpanStatusCode } from '@opentelemetry/api';
const tracer = trace.getTracer('order-svc');

export async function placeOrder(input, user) {
  return tracer.startActiveSpan('placeOrder', async (span) => {
    span.setAttributes({ 'order.items': input.items.length, 'order.city': user.city });
    try {
      const priced = await tracer.startActiveSpan('priceCart', async (s) => { const r = await priceCart(input); s.end(); return r; });
      const order = await saveOrder(priced, user);
      span.setAttribute('order.id', order.id);
      return order;
    } catch (e) {
      span.recordException(e); span.setStatus({ code: SpanStatusCode.ERROR });
      throw e;
    } finally { span.end(); }
  });
}
```

### Put trace ids in logs (pino)
```js
import { context, trace } from '@opentelemetry/api';
const logger = pino({ mixin() {
  const s = trace.getSpan(context.active())?.spanContext();
  return s ? { traceId: s.traceId, spanId: s.spanId } : {};
}});
```

### Propagate through Kafka manually (if not auto-instrumented)
```js
import { propagation, context } from '@opentelemetry/api';
const headers = {}; propagation.inject(context.active(), headers);          // producer
await producer.send({ topic: 'order-events', messages: [{ value, headers }] });
// consumer: const ctx = propagation.extract(context.active(), message.headers); context.with(ctx, () => handle(...))
```

### FastAPI — OTel instrumentation
```bash
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install
OTEL_SERVICE_NAME=payment-svc OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317 \
  opentelemetry-instrument uvicorn main:app --host 0.0.0.0 --port 8000
# FastAPI, httpx, SQLAlchemy/asyncpg, redis auto-instrumented
```

### Collector with tail sampling
```yaml
receivers: { otlp: { protocols: { grpc: {}, http: {} } } }
processors:
  batch: {}
  tail_sampling:
    decision_wait: 10s
    policies:
      - { name: errors, type: status_code, status_code: { status_codes: [ERROR] } }
      - { name: slow,   type: latency,     latency: { threshold_ms: 1000 } }
      - { name: sample, type: probabilistic, probabilistic: { sampling_percentage: 5 } }
exporters: { otlp/tempo: { endpoint: tempo:4317, tls: { insecure: true } } }
service: { pipelines: { traces: { receivers: [otlp], processors: [tail_sampling, batch], exporters: [otlp/tempo] } } }
```

### Local: Jaeger all-in-one
```yaml
jaeger: { image: jaegertracing/all-in-one:1.57, ports: ["16686:16686", "4317:4317", "4318:4318"] }
```

### Frontend / mobile
```
Web: OTel web SDK or Sentry/Datadog RUM → start the trace in the browser, propagate traceparent to API
     (configure CORS to allow the traceparent header)
React Native: Sentry performance / Datadog RUM spans for screen loads & API calls; send traceparent
→ one trace from tap on phone to database row
```

---

## ⚫ Interview Questions + Answers

**Q1: What is distributed tracing and why is it needed?**
A1: Recording the full path of a request across services as a tree of timed spans sharing a trace ID. In microservices, a single user action fans out to many services, databases, caches and queues. Metrics show that something is slow and logs are fragmented, while tracing shows exactly which hop or dependency caused the latency or error, plus the call structure (sequential vs parallel, retries, N+1s).

**Q2: Explain traces, spans and context propagation.**
A2: A trace is the whole request journey, identified by a trace ID. A span is one operation within it, with a span ID, parent span ID, name, timing, attributes, events and status. Context propagation passes the trace ID and current span ID to the next service, through the W3C `traceparent` header for HTTP and gRPC, or message headers for queues, so downstream spans attach to the right parent. Without propagation, you get disconnected fragments.

**Q3: What is OpenTelemetry?**
A3: A vendor-neutral, CNCF standard set of APIs, SDKs, auto-instrumentation libraries, the OTLP protocol and the Collector for generating, processing and exporting traces, metrics and logs. You instrument once and send data to any backend (Jaeger, Tempo, X-Ray, Datadog, Honeycomb). The Collector handles batching, sampling, enrichment and PII scrubbing centrally.

**Q4: Head vs tail sampling?**
A4: Head sampling decides whether to record a trace when the request starts (e.g. 5% randomly). It's cheap and simple, but might drop the rare error or slow traces you care about. Tail sampling buffers spans and decides after the trace completes, based on outcome: keep all errors and slow traces, plus a small percentage of normal ones. It's more useful, but needs a collector with memory and complete traces routed to the same instance.

**Q5: How would you use tracing to fix a slow checkout?**
A5: Start from the latency alert or dashboard, open exemplar or slow traces for the checkout route, and inspect the waterfall. Look for the longest spans (an external payment API, a slow SQL query), sequential calls that could run in parallel, repeated small DB spans (N+1), retries, and time spent waiting in queues. Then fix it: add an index, batch the queries, parallelize, add timeouts or fallbacks, cache, or move non-critical calls async. Verify with p95/p99 metrics and new traces after deploying.

---

## 🔷 Trade-offs
✅ Advantages:
- Pinpoints latency/error sources across services; reveals architecture problems; links metrics ↔ logs.

❌ Disadvantages:
- Instrumentation & propagation effort (esp. async hops); storage cost → sampling needed.
- Overhead (small with sampling); PII risk in span attributes; incomplete traces if any hop drops context.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trace | End-to-end path of a request | request की पूरी यात्रा |
| Span | One timed operation | एक काम और उसका समय |
| Trace ID / Span ID | Identifiers linking spans | spans को जोड़ने वाली IDs |
| Context propagation | Passing trace context across hops | trace जानकारी आगे भेजना |
| traceparent | W3C trace header | trace का मानक header |
| OpenTelemetry | Standard observability SDKs/protocol | observability का मानक |
| Collector | Pipeline for telemetry | telemetry भेजने वाला |
| Head / tail sampling | Decide at start / after completion | शुरू में / बाद में चुनना |
| Waterfall | Timeline view of spans | spans का समय-चित्र |
| Exemplar | Metric point linked to a trace | metric से जुड़ा trace |

---

## ⚡ 3-Line Summary
**English:**
1. A trace is a tree of spans (timed operations) sharing a trace ID, propagated via traceparent across HTTP, gRPC and queues.
2. Use OpenTelemetry SDKs + Collector (auto-instrumentation) → Jaeger/Tempo/X-Ray; tail-sample errors and slow traces.
3. Traces pinpoint slow hops, N+1s, retries and queue waits; link them with logs (trace_id) and metrics (exemplars).

**Hindi:**
1. Trace = एक trace ID से जुड़े spans का पेड़; `traceparent` से HTTP, gRPC, queues में आगे जाता है।
2. OpenTelemetry SDK + Collector → Jaeger/Tempo/X-Ray; errors और धीमे traces रखो (tail sampling)।
3. धीमी जगह, N+1, retries, queue इंतज़ार तुरंत दिखते हैं; logs और metrics से जोड़ो।

---

## ➡️ Next Topic Suggestion
**103. SLI / SLO / SLA** — With metrics and traces in place, define what "reliable enough" means: service level indicators, objectives and agreements, and how they drive engineering priorities.
