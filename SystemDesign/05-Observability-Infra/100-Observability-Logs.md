# 100. Observability — Logs
# हिंदी में: Logs — सिस्टम में हुई हर घटना का समय के साथ लिखा रिकॉर्ड (क्या हुआ, कब, किसके लिए, क्या error), जिससे debugging और जाँच होती है

---

## 🔵 Simple Definition (English)
**Observability** is the ability to understand a system's internal state from its outputs. Its three pillars are **logs, metrics and traces**.
**Logs** are **timestamped records of discrete events**: "order 9001 placed by user 42", "payment API timeout after 3 s", with context. In production they should be **structured** (JSON key-value fields), carry **correlation/trace IDs**, have proper **levels**, and be shipped to a **centralized, searchable store** (ELK/OpenSearch, Loki, CloudWatch, Datadog).

## 🔵 सरल परिभाषा (Hindi)
Observability = सिस्टम के बाहर निकलने वाली जानकारी (logs, metrics, traces) से उसके अंदर की हालत समझ पाना।
Logs हर घटना का समय के साथ रिकॉर्ड है — "order 9001 बना", "payment API timeout"। Production में logs JSON में (structured), request-id के साथ, और एक केंद्रीय जगह (ELK, Loki, CloudWatch) पर खोजने लायक होने चाहिए।

---

## 🔴 Problem it Solves
At 2 AM, a customer says "my payment failed". You have 40 containers across 12 services that auto-scaled and restarted overnight:
- `console.log("error!!")` with no context is useless.
- SSH-ing into containers to `grep` files is impossible (containers are ephemeral, logs are gone).
- Following one request across services needs a **shared ID**.
- Audits ("who refunded this order?") and security investigations need durable records.

Centralized structured logs let you **search, filter and correlate** events across the whole system in seconds.

## 🔴 यह क्यों बना? (Hindi)
रात 2 बजे ग्राहक कहता है "पेमेंट फ़ेल हुआ" — 12 services के 40 containers, जो रात में restart हो चुके हैं। बिना संदर्भ वाला `console.log("error")` बेकार है, containers में जाकर grep करना नामुमकिन।
केंद्रीय, structured logs और request-id से पूरे सिस्टम में किसी भी घटना को सेकंडों में ढूँढा और जोड़ा जा सकता है।

---

## 🟢 How it Works — Step by Step

### Unstructured vs structured

```
❌ Unstructured:
2026-10-18 13:20:05 ERROR Payment failed for user 42 order 9001: timeout
   → hard to parse/filter/aggregate reliably

✅ Structured (JSON):
{"ts":"2026-10-18T13:20:05.123Z","level":"error","service":"payment-svc","env":"prod",
 "version":"1.9.2","traceId":"4bf92f3577b34da6","requestId":"req_8f2a","userId":42,
 "orderId":9001,"event":"payment_charge_failed","provider":"razorpay","durationMs":3002,
 "err":{"type":"TimeoutError","message":"upstream timeout"}}
   → query: service:payment-svc AND event:payment_charge_failed AND provider:razorpay
```

### Log levels (use them consistently)

```
FATAL/CRITICAL → process can't continue
ERROR  → operation failed, needs attention (failed payment call after retries)
WARN   → unexpected but handled (retry happened, fallback used, deprecated API hit)
INFO   → significant business/lifecycle events (order placed, server started, job finished)
DEBUG  → detailed diagnostic info (off in prod by default; enable dynamically per service/user)
TRACE  → extremely verbose
Prod default: INFO. Noisy DEBUG in prod = cost + signal drowning.
```

### The logging pipeline

```
 App (stdout JSON) ──► Container runtime ──► Collector/agent ──► Storage + Index ──► UI / Alerts
 (pino, structlog)     (Docker/K8s logs)     (Fluent Bit,        (Elasticsearch/     (Kibana,
                                              Vector, OTel        OpenSearch, Loki,   Grafana,
                                              Collector,          CloudWatch Logs,    Datadog)
                                              CloudWatch agent)   Datadog, S3 archive)
12-Factor rule: apps write logs to STDOUT as an event stream; the platform collects them.
Don't write to local files in containers.
```

### What to log (and what NOT)

```
✅ Request summary (method, route template, status, latency, user id, request id) — one line per request
✅ Business events (order placed, refund issued, login success/failure)
✅ Errors with stack traces + context (inputs that matter, ids, dependency name)
✅ External calls: dependency, latency, status, retries
✅ Security/audit events: auth failures, permission changes, admin actions (append-only, retained)
❌ Passwords, OTPs, tokens, full card numbers, CVV, Aadhaar/PAN, secrets → redact!
❌ Huge payloads (full request bodies) by default
❌ Logging inside tight loops (millions of lines)
```

### Correlation IDs / trace IDs

```
Gateway generates X-Request-ID (or W3C traceparent) → passed in headers to every downstream service,
queue message headers, and background jobs → every log line includes it.
Search "requestId:req_8f2a" → full story across 7 services in order.
```

### Cost & retention
```
Logs are often the BIGGEST observability cost.
- Sample high-volume success logs (e.g. keep 10% of 200 OK request logs, 100% of errors)
- Retention tiers: hot 7–14 days searchable, cold archive in S3 for 1 year+ (compliance)
- Drop noisy health-check logs; aggregate into metrics instead
- Logs vs metrics: "how many errors per minute?" → metric; "what happened in request X?" → log
```

## 🟢 कैसे काम करता है? (Hindi)
1. ऐप हर घटना JSON में stdout पर लिखता है — समय, level, service, request-id, user-id, event, error।
2. Agent (Fluent Bit/Vector/OTel) logs उठाकर केंद्रीय जगह (OpenSearch, Loki, CloudWatch) भेजता है।
3. वहाँ `requestId:req_8f2a` से पूरी request की कहानी सारी services में एक साथ दिखती है।
4. Levels सही इस्तेमाल करो: error, warn, info (production default), debug (ज़रूरत पर)।
5. Password, OTP, token, कार्ड नंबर कभी log मत करो; ज़्यादा logs से ख़र्च बढ़ता है — sampling और retention नियम रखो।

---

## 🟡 Real World Example

**Uber, Netflix, LinkedIn** — ingest petabytes of logs per day. Uber built a log analytics platform on ClickHouse after Elasticsearch costs and scaling became problematic, which shows log cost is a real engineering concern at scale.

**Indian fintechs (Razorpay, PhonePe)** — keep structured audit logs of every money movement and admin action for RBI compliance and dispute resolution, retained for years in immutable storage.

**Security incident investigations** — breach postmortems often hinge on whether access logs existed. Companies without centralized logs couldn't determine what data was accessed. Logging failures is in the OWASP Top 10 ("Security Logging and Monitoring Failures").

**Accidental PII in logs** — Twitter (2018) and GitHub (2018) both discovered user passwords written in plaintext to internal logs because of bugs, and asked users to change passwords. That's why log redaction matters.

## 🟡 Real Example Hindi में
Uber रोज़ petabytes logs संभालता है — Elasticsearch महँगा पड़ा तो ClickHouse पर अपना सिस्टम बनाया। Razorpay/PhonePe हर पैसे के लेन-देन और admin काम का audit log सालों तक रखते हैं (RBI नियम)।
2018 में Twitter और GitHub ने पाया कि bug की वजह से passwords logs में सादे लिखे जा रहे थे — इसलिए logs से संवेदनशील डेटा हटाना (redaction) ज़रूरी है।

---

## 🟠 My Stack Example

### Node.js — pino structured logging + request id + redaction
```js
import pino from 'pino';
import pinoHttp from 'pino-http';
import { randomUUID } from 'node:crypto';

export const logger = pino({
  level: process.env.LOG_LEVEL ?? 'info',
  base: { service: 'order-svc', env: process.env.NODE_ENV, version: process.env.GIT_SHA },
  redact: { paths: ['req.headers.authorization', 'req.headers.cookie', '*.password', '*.otp', '*.cardNumber'], censor: '[REDACTED]' },
  timestamp: pino.stdTimeFunctions.isoTime,
});

app.use(pinoHttp({
  logger,
  genReqId: (req, res) => { const id = req.headers['x-request-id'] ?? randomUUID(); res.setHeader('X-Request-ID', id); return id; },
  customLogLevel: (req, res, err) => (err || res.statusCode >= 500 ? 'error' : res.statusCode >= 400 ? 'warn' : 'info'),
  autoLogging: { ignore: (req) => req.url.startsWith('/health') },     // no health-check noise
  serializers: { req: (r) => ({ method: r.method, url: r.url, userId: r.raw.user?.id }) },
}));

// business event with context (req.log is a child logger with reqId)
app.post('/api/v1/orders', authenticate, async (req, res) => {
  const order = await placeOrder(req.body, req.user);
  req.log.info({ event: 'order_placed', orderId: order.id, total: order.total }, 'order placed');
  res.status(201).json(order);
});

// errors with stack + context
app.use((err, req, res, _next) => {
  req.log.error({ err, event: 'unhandled_error', route: req.route?.path }, err.message);
  res.status(500).json({ error: 'INTERNAL', requestId: req.id });     // give users the id for support
});
```

### Propagate the id to downstream calls & queue jobs
```js
await fetch(`${PAYMENT_URL}/v1/charges`, { method: 'POST', headers: { 'X-Request-ID': req.id, ...traceHeaders }, body });
await queue.add('send-receipt', { orderId, requestId: req.id });     // worker logs with same requestId
```

### FastAPI — structlog JSON + request id middleware
```python
import structlog, uuid
structlog.configure(processors=[
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.dict_tracebacks,
    structlog.processors.JSONRenderer(),
])
log = structlog.get_logger(service="payment-svc")

@app.middleware("http")
async def request_context(request, call_next):
    rid = request.headers.get("x-request-id", str(uuid.uuid4()))
    structlog.contextvars.bind_contextvars(request_id=rid, path=request.url.path)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    log.info("request", status=response.status_code)
    structlog.contextvars.clear_contextvars()
    return response
```

### Collect & ship (Docker Compose / K8s)
```yaml
# Fluent Bit DaemonSet on K8s tails /var/log/containers/*.log → parses JSON → OpenSearch/Loki/CloudWatch
# AWS ECS: awslogs / FireLens log driver → CloudWatch Logs or OpenSearch
# Local: docker compose logs -f order-svc | npx pino-pretty
```

### Query examples
```
CloudWatch Logs Insights:
  fields @timestamp, event, orderId, err.message
  | filter service = "payment-svc" and level = "error"
  | stats count() by bin(5m), provider
Loki (LogQL):   {service="payment-svc"} | json | level="error" | provider="razorpay"
Kibana (KQL):   requestId:"req_8f2a"
```

### Mobile & web logs
- **React Native / Next.js client:** don't spam logs; send errors and crashes to Sentry/Crashlytics with breadcrumbs, app version, device and the `requestId` from failed API responses, so client and server logs connect.

---

## ⚫ Interview Questions + Answers

**Q1: What are the three pillars of observability, and where do logs fit?**
A1: Logs (timestamped event records with context), metrics (numeric time series aggregated over time: rates, latencies, saturation) and traces (end-to-end request paths across services, as spans). Logs answer "what exactly happened in this case?" with detailed context. Metrics answer "is something wrong and how much?" cheaply. Traces answer "where in the call path is the time or error?". They're most useful when linked through shared trace and request IDs.

**Q2: Why structured logging?**
A2: JSON key-value logs can be parsed, indexed, filtered and aggregated reliably (by service, userId, orderId or error type) without fragile regexes. They support consistent fields across services (service, env, version, traceId), enable dashboards and alerts on log fields, and make correlation across systems possible. Plain text is only good for humans reading a single process's output.

**Q3: How do you trace a single user request across many microservices using logs?**
A3: Generate a correlation ID (or W3C trace context) at the edge (gateway or BFF) and propagate it in headers to every downstream HTTP or gRPC call, in message headers for queues and events, and into background jobs. Every service binds it to its logger context so all log lines carry it. Then search for that ID in the centralized log store to see the full timeline. Return it to clients in responses and error messages for support.

**Q4: What should never be logged, and how do you prevent it?**
A4: Secrets and credentials (passwords, OTPs, API keys, tokens, session cookies), full payment card data and CVV, and sensitive personal data (Aadhaar, PAN, health data), unless masked and legally required. Prevent it with logger-level redaction rules, serializers that whitelist fields instead of dumping whole objects, code review and lint rules, automated scanning of logs for patterns, restricted access to log stores, and retention limits.

**Q5: Logs are getting too expensive. What do you do?**
A5: Reduce volume: lower the default level to INFO or WARN, remove noisy and duplicate logs, stop logging health checks, sample high-volume success logs while keeping all errors, and convert repetitive logs into metrics (counters). Reduce cost per GB: tiered retention (short hot retention, cheap S3 archive), cheaper backends (Loki or ClickHouse vs full-text indexing of everything), and indexing only key fields. Set per-team budgets and show cost visibility.

---

## 🔷 Trade-offs
✅ Advantages:
- Rich detail for debugging, audits, security forensics; flexible ad-hoc queries.

❌ Disadvantages:
- High volume → storage/indexing cost; noisy logs hide signal.
- Risk of leaking sensitive data; performance overhead if synchronous/verbose.
- Not great for trends/alerting at scale (that's metrics' job).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Observability | Understanding system from outputs | बाहर की जानकारी से अंदर की हालत समझना |
| Log | Timestamped event record | घटना का रिकॉर्ड |
| Structured logging | Key-value/JSON logs | JSON वाले logs |
| Log level | Severity (error, info...) | गंभीरता का स्तर |
| Correlation ID | ID linking related logs | जुड़े logs की पहचान |
| Centralized logging | All logs in one searchable store | सारे logs एक जगह |
| Redaction | Masking sensitive fields | संवेदनशील डेटा छिपाना |
| Retention | How long logs are kept | logs कितने समय रखें |
| Log sampling | Keep only a fraction | कुछ ही logs रखना |
| Audit log | Record of sensitive actions | ज़रूरी कामों का रिकॉर्ड |

---

## ⚡ 3-Line Summary
**English:**
1. Logs = timestamped event records; in production make them structured JSON to stdout, with levels and consistent fields.
2. Propagate request/trace IDs everywhere and centralize logs (Fluent Bit/OTel → OpenSearch/Loki/CloudWatch) for cross-service search.
3. Never log secrets/PII (redact), control volume and cost (sampling, retention tiers), and use metrics for trends.

**Hindi:**
1. Logs = घटनाओं का रिकॉर्ड; production में JSON, stdout पर, सही level और fields के साथ।
2. Request/trace ID हर जगह भेजो और logs एक केंद्रीय जगह पर रखो।
3. Secrets/PII कभी log मत करो; sampling और retention से ख़र्च नियंत्रित करो; trends के लिए metrics।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — Observability explained](https://www.youtube.com/results?search_query=observability+logs+metrics+traces+bytebytego) | Three pillars: logs, metrics, traces — visual overview |
| 📺 YouTube | [Hussein Nasser — Structured Logging](https://www.youtube.com/results?search_query=structured+logging+observability+hussein+nasser) | JSON logs, correlation IDs, log levels |
| 📝 Article | [OpenTelemetry Docs](https://opentelemetry.io/docs/) | Vendor-neutral instrumentation for logs, metrics, traces |
| 📝 Article | [Grafana — Observability best practices](https://grafana.com/blog/2021/03/31/open-source-observability/) | ELK stack vs Loki vs Tempo — what to use when |
| 🐙 GitHub | [open-telemetry/opentelemetry-js](https://github.com/open-telemetry/opentelemetry-js) | Add structured logging + tracing to Node.js apps |

---

## ➡️ Next Topic Suggestion
**101. Observability — Metrics** — Logs tell you what happened in one request. Next: metrics, the cheap numeric time series (RED/USE, golden signals, histograms) that tell you how the whole system is doing and power alerts and dashboards.
