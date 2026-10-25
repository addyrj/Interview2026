# 251. Structured Logging
# हिंदी में: Structured Logging — JSON Logs और Correlation IDs

---

## 🔵 Simple Definition (English)
**Structured logging** means writing logs as machine-readable data (usually JSON) with consistent fields (`timestamp`, `level`, `message`, `service`, `requestId`) instead of free-form text sentences. This makes logs searchable, filterable, and parseable by tools like Elasticsearch or CloudWatch Insights — you can query `requestId:"abc123"` across thousands of log lines instantly, instead of grepping text.

## 🔵 सरल परिभाषा (Hindi)
**Structured logging** का मतलब है logs को machine-readable data (आम तौर पर JSON) के रूप में लिखना — consistent fields के साथ (`timestamp`, `level`, `message`, `service`, `requestId`) — free-form text sentences के बजाय। इससे logs searchable, filterable, और parseable बन जाते हैं tools जैसे Elasticsearch या CloudWatch Insights के लिए — आप `requestId:"abc123"` से हज़ारों log lines में instantly search कर सकते हो, text grep करने की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
```
PLAIN TEXT LOGS (unstructured):
  "2024-01-15 10:23:11 User rahul@example.com placed order ORD123 for Rs 450"
  "2024-01-15 10:23:15 ERROR: Payment failed for order ORD123 - timeout"

  Problems:
    1. To find all logs for ORD123, you grep text — works, but fragile
       (what if "ORD123" appears as part of another word?)
    2. Can't easily filter "show me only payment errors above Rs 1000"
    3. Different developers log in different formats
       ("User X placed order Y" vs "Order placed: user=X order=Y")
    4. Log aggregation tools (Elasticsearch/CloudWatch) have to GUESS
       the structure using regex — brittle, breaks when format changes
    5. In microservices, correlating ONE user request across 5 services
       (API gateway → order service → payment service → notification)
       is nearly impossible without a shared identifier

STRUCTURED LOGGING SOLUTION:
  { "timestamp": "2024-01-15T10:23:11Z", "level": "info",
    "message": "Order placed", "userId": "u123", "orderId": "ORD123",
    "amount": 450, "requestId": "req-abc-999", "service": "order-service" }

  - Query engines can filter by ANY field directly: orderId="ORD123"
  - Same requestId across all 5 services = trace the full request flow
  - Consistent schema enforced by the logger, not developer discipline
```

## 🔴 यह क्यों बना? (Hindi)
```
Plain text logs की समस्या:
  - ORD123 ढूंढने के लिए text grep करना पड़ता है — fragile approach
  - "payment errors above Rs 1000" जैसे filters लगाना मुश्किल
  - अलग developers अलग format में log करते हैं — inconsistency
  - Elasticsearch/CloudWatch को regex से structure guess करना पड़ता है
  - Microservices में एक request को 5 services में trace करना impossible
    बिना किसी shared identifier (requestId) के

Structured logging solution:
  - हर field (orderId, userId, amount) directly query हो सकता है
  - एक ही requestId सभी services में use होने से पूरा flow trace होता है
  - Schema consistent रहता है क्योंकि logger खुद structure enforce करता है
```

---

## 🟢 How it Works — Step by Step

Step 1 → Configure Winston (or any logger) with `winston.format.json()` so every log entry is serialized as a JSON object, not a plain string.
Step 2 → Define a consistent schema: every log must have `timestamp`, `level`, `message`, and `service` at minimum — enforced via `defaultMeta` or a wrapper function.
Step 3 → Generate a unique `requestId` (UUID) at the start of every incoming HTTP request, using middleware (often via `cls-hooked`, `AsyncLocalStorage`, or a header like `x-request-id`).
Step 4 → Attach that `requestId` to EVERY log line produced while handling that request — including logs made deep inside async DB calls or calls to other microservices.
Step 5 → Pass the `requestId` downstream (in HTTP headers) when calling other microservices, so the SAME id appears in their logs too — enabling full distributed tracing by just filtering on one ID.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Winston को `winston.format.json()` के साथ configure करो ताकि हर log entry JSON object हो, plain string नहीं।
Step 2 → एक consistent schema define करो: हर log में कम से कम `timestamp`, `level`, `message`, `service` हो — `defaultMeta` से enforce करो।
Step 3 → हर incoming HTTP request के शुरुआत में एक unique `requestId` (UUID) generate करो, middleware के through (`AsyncLocalStorage` या `x-request-id` header)।
Step 4 → उस `requestId` को उस request के दौरान बनने वाले हर log line में attach करो — async DB calls या deep function calls में भी।
Step 5 → `requestId` को आगे दूसरी microservices में भी भेजो (HTTP headers में) ताकि वही ID उनके logs में भी दिखे — पूरे distributed flow को एक ID से trace किया जा सके।

---

## 🟡 Real World Example
**Zomato order flow across microservices:** When a user places an order, the API Gateway generates `requestId: req-9f3a`. It calls Order Service, which calls Payment Service, which calls Restaurant Service — each service logs with the SAME `requestId` in structured JSON. If payment fails, the support engineer searches Elasticsearch/Kibana for `requestId:"req-9f3a"` and sees the ENTIRE journey across all 4 services in chronological order — exactly where it broke — instead of manually checking 4 separate log files with 4 different timestamps and no shared key.

## 🟡 Real Example Hindi mein
**Zomato order flow across microservices:** जब user order place करता है, API Gateway एक `requestId: req-9f3a` generate करता है। ये Order Service को call करता है, जो Payment Service को, जो Restaurant Service को — हर service उस SAME `requestId` के साथ structured JSON log करती है। अगर payment fail होता है, support engineer Elasticsearch/Kibana में `requestId:"req-9f3a"` search करता है और पूरी journey chronological order में देखता है — exactly कहां टूटा — बजाय 4 अलग log files manually check करने के।

---

## 💻 Code Example — Basic

```javascript
// structured-logger-basic.js
// npm install winston uuid
const winston = require('winston');
const { v4: uuidv4 } = require('uuid');

// ─── 1. CREATE A JSON LOGGER ────────────────────────────────────────────────
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(), // ISO timestamp field
    winston.format.json() // output as JSON, not plain text
  ),
  defaultMeta: { service: 'order-service' }, // every log auto-tags its service name
  transports: [new winston.transports.Console()],
});

// ─── 2. LOGGING WITH STRUCTURED FIELDS ─────────────────────────────────────
const requestId = uuidv4(); // unique id for this "request" simulation

logger.info('Order placed', {
  requestId,            // same id would appear across all services
  userId: 'u123',
  orderId: 'ORD456',
  amount: 799,
});

logger.error('Payment failed', {
  requestId,             // SAME requestId links this error to the order above
  orderId: 'ORD456',
  reason: 'Gateway timeout',
});

// Run: node structured-logger-basic.js
// Output is pure JSON — one object per line, easy to pipe into jq or Elasticsearch
```

## 💻 Code Example — Advanced

```javascript
// structured-logger-advanced.js — AsyncLocalStorage for automatic requestId propagation
// npm install winston uuid express

const { AsyncLocalStorage } = require('async_hooks');
const winston = require('winston');
const { v4: uuidv4 } = require('uuid');

const asyncLocalStorage = new AsyncLocalStorage(); // context store per request

// ─── 1. LOGGER THAT AUTO-ATTACHES requestId FROM CONTEXT ───────────────────
const baseLogger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
  defaultMeta: { service: 'payment-service' },
  transports: [new winston.transports.Console()],
});

// Wrapper that pulls requestId out of AsyncLocalStorage automatically
function log(level, message, meta = {}) {
  const context = asyncLocalStorage.getStore(); // get current request's context
  baseLogger.log(level, message, {
    ...meta,
    requestId: context?.requestId || 'no-request-id', // auto-attach, no manual passing needed
  });
}

const logger = {
  info: (msg, meta) => log('info', msg, meta),
  warn: (msg, meta) => log('warn', msg, meta),
  error: (msg, meta) => log('error', msg, meta),
  debug: (msg, meta) => log('debug', msg, meta),
};

// ─── 2. MIDDLEWARE THAT CREATES THE CONTEXT PER REQUEST ────────────────────
function requestIdMiddleware(req, res, next) {
  // Reuse requestId from upstream service header if present, else generate new
  const requestId = req.headers['x-request-id'] || uuidv4();
  res.setHeader('x-request-id', requestId); // send back so client/caller can trace too

  // Run the rest of the request INSIDE this async context
  asyncLocalStorage.run({ requestId }, () => {
    next(); // any logger.info() called anywhere downstream now sees this requestId
  });
}

// ─── 3. DOWNSTREAM SERVICE CALL PROPAGATES THE SAME requestId ──────────────
async function callNotificationService(requestId, orderId) {
  const axios = require('axios');
  try {
    await axios.post('http://notification-service/notify', { orderId }, {
      headers: { 'x-request-id': requestId }, // pass it along — chain stays unbroken
    });
  } catch (err) {
    logger.error('Notification service call failed', { orderId, error: err.message });
  }
}

module.exports = { logger, requestIdMiddleware, callNotificationService };
```

---

## 🟠 Express.js Integration

```javascript
// app.js
const express = require('express');
const { logger, requestIdMiddleware } = require('./structured-logger-advanced');

const app = express();
app.use(express.json());
app.use(requestIdMiddleware); // mount FIRST — sets up context for every request

app.post('/payments', async (req, res) => {
  const { orderId, amount } = req.body;

  logger.info('Payment initiated', { orderId, amount }); // requestId auto-attached

  try {
    // simulate payment gateway call
    if (amount > 50000) {
      throw new Error('Amount exceeds limit');
    }
    logger.info('Payment successful', { orderId, amount });
    res.json({ status: 'success' });
  } catch (err) {
    logger.error('Payment failed', { orderId, error: err.message }); // same requestId still attached
    res.status(400).json({ error: err.message });
  }
});

app.listen(4000, () => logger.info('Payment service listening on 4000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Logging free-text strings with interpolated values
```javascript
// WRONG: fields buried inside a string — can't query orderId directly
logger.info(`Order ${orderId} placed by user ${userId} for Rs ${amount}`);

// CORRECT: pass values as a structured metadata object
logger.info('Order placed', { orderId, userId, amount });
```

❌ **Mistake 2:** Forgetting to propagate requestId to downstream service calls
```javascript
// WRONG: calling another microservice without passing the requestId header
await axios.post('http://payment-service/charge', data);
// now payment-service logs have a DIFFERENT requestId — trace is broken

// CORRECT: always forward the current requestId in outgoing headers
await axios.post('http://payment-service/charge', data, {
  headers: { 'x-request-id': requestId },
});
```

❌ **Mistake 3:** Inconsistent field naming across services
```javascript
// WRONG: service A logs "orderId", service B logs "order_id", service C logs "oid"
// Queries can't match across services — defeats the purpose of structured logs

// CORRECT: agree on a shared logging schema/convention org-wide
// { requestId, service, userId, orderId, level, message, timestamp }
```

---

## 🧠 Tricky Interview Question

```javascript
const logger = winston.createLogger({
  format: winston.format.json(),
  transports: [new winston.transports.Console()],
});

function handleRequest(reqId) {
  setTimeout(() => {
    logger.info('Processing done', { reqId }); // this works fine
  }, 100);
}

// But without AsyncLocalStorage, how would this code know reqId
// deep inside a DB call three function layers down, without passing
// reqId as a parameter through every single function?
```
Answer: Without a context-propagation mechanism, it CAN'T — you'd have to manually thread `reqId` through every function signature, which gets unwieldy fast in a real codebase with deep call stacks (controller → service → repository → DB driver). `AsyncLocalStorage` (Node's built-in async context API) solves this by storing `reqId` in a context that automatically follows the async execution chain (promises, `setTimeout`, callbacks) WITHOUT needing to pass it explicitly as a parameter. Any `logger.info()` call anywhere in that async chain can retrieve it via `asyncLocalStorage.getStore()`. This is exactly how libraries like `express-http-context` or NestJS's request-scoped providers implement automatic request-id logging.

---

## ⚫ Interview Questions + Answers

**Q1: What is structured logging and how is it different from plain text logging?**
A1: Structured logging writes each log entry as a machine-readable object (usually JSON) with well-defined fields (`timestamp`, `level`, `message`, custom fields like `orderId`). Plain text logging writes free-form sentences. Structured logs can be queried/filtered precisely by field (`orderId:"X"`) in tools like Elasticsearch, while plain text requires fragile regex/grep matching and can't easily support numeric range queries (e.g., `amount > 1000`).

**Q2: What is a correlation ID / request ID and why is it essential in microservices?**
A2: A correlation ID (or request ID) is a unique identifier generated at the entry point of a request (API gateway or first service) and passed along to every downstream service call (via HTTP header). Every log line produced while handling that request — across ALL services — includes this same ID. It's essential in microservices because a single user action touches multiple independent services with separate log files; without a shared ID there's no way to reconstruct the full request journey when debugging a failure.

**Q3: How do you propagate a request ID across async operations without manually passing it everywhere?**
A3: Use Node's `AsyncLocalStorage` (from `async_hooks`). You wrap the request handling in `asyncLocalStorage.run({ requestId }, () => next())` at the start of the request. Any code running inside that async context — even deep in promise chains, `setTimeout`, or DB driver callbacks — can call `asyncLocalStorage.getStore()` to retrieve `requestId` without it being an explicit function parameter. Libraries like `cls-hooked` historically did similar things before `AsyncLocalStorage` was stabilized.

**Q4: Why is a consistent log schema important across microservices owned by different teams?**
A4: If Team A logs `order_id` and Team B logs `orderId`, a single Elasticsearch/Kibana query can't match both — you'd need separate queries per service, defeating centralized search. A shared schema (agreed field names, casing, required fields like `service`, `level`, `timestamp`, `requestId`) ensures any engineer can query logs across the entire system the same way, regardless of which team wrote which service.

**Q5: What are the downsides of structured (JSON) logging compared to plain text?**
A5: JSON logs are harder to read directly in a terminal during local development — a human-friendly colorized line (Morgan's `'dev'` format) is faster to scan visually than a raw JSON blob. JSON also has more overhead per line (field names repeated every log) increasing log file size slightly. The common solution: use JSON format in production (for machine consumption) and pretty/colorized format in development (for human readability) — switching based on `NODE_ENV`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running microservices where requests span multiple services
- Logs are shipped to a centralized search/aggregation tool (ELK, CloudWatch, Datadog)
- You need to filter/query logs by specific fields at scale

❌ Avoid when:
- Quick local script/debugging — plain readable text is faster to scan by eye
- Extremely low-volume single-server app with no log aggregation tooling at all

---

## 📊 Visual Diagram
```
REQUEST TRACE ACROSS MICROSERVICES (same requestId everywhere)
────────────────────────────────────────────────────────────────

  Client
    │  requestId generated: req-9f3a
    ▼
  API Gateway        logger.info("Request received", {requestId: req-9f3a})
    │ forwards header: x-request-id: req-9f3a
    ▼
  Order Service      logger.info("Order created", {requestId: req-9f3a, orderId})
    │ forwards same header
    ▼
  Payment Service     logger.error("Payment failed", {requestId: req-9f3a, orderId})
    │
    ▼
  Notification Service  logger.info("Notify skipped", {requestId: req-9f3a})

  Kibana/Elasticsearch query: requestId:"req-9f3a"
  ──▶ returns ALL 4 log lines above, in order, across 4 different services
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Structured Log | JSON-formatted log with fields | Fields वाला JSON log |
| Correlation ID / Request ID | Unique ID tracking one request | एक request track करने वाला ID |
| AsyncLocalStorage | Node API for async context propagation | Async context भेजने वाला Node API |
| Schema | Agreed consistent field structure | Consistent field संरचना |
| Log Aggregation | Collecting logs from many services centrally | सभी services से logs एक जगह |
| defaultMeta | Fields auto-attached to every log | हर log में auto-जुड़ने वाले fields |

---

## ⚡ 3-Line Summary
**English:**
1. Structured logging means writing logs as JSON objects with consistent fields instead of free-text, making them queryable at scale.
2. Correlation/request IDs, propagated via headers and `AsyncLocalStorage`, let you trace one user request across multiple microservices.
3. Keep a shared log schema across services so centralized tools (Elasticsearch/Kibana) can query any field consistently.

**Hindi:**
1. Structured logging का मतलब है logs को JSON objects में consistent fields के साथ लिखना, free-text नहीं — ताकि scale पर query हो सके।
2. Correlation/request ID, headers और `AsyncLocalStorage` के through propagate करके एक request को कई microservices में trace कर सकते हो।
3. Services में एक shared log schema रखो ताकि centralized tools (Elasticsearch/Kibana) हर field consistently query कर सकें।

---

## ➡️ Next Topic
**252. Log Levels** — error/warn/info/debug hierarchy और environment के हिसाब से configure करना।
