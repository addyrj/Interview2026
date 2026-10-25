# 108. Morgan — Request Logger
# हिंदी में: Morgan — HTTP Request Logging Middleware

---

## 🔵 Simple Definition (English)
**Morgan** is an HTTP request logger middleware for Express. It logs details of every incoming request (method, URL, status code, response time) to the console or a file, in predefined or custom formats. Essential for debugging, monitoring, and auditing API traffic in production.

## 🔵 सरल परिभाषा (Hindi)
**Morgan** Express के लिए एक HTTP request logger middleware है। ये हर incoming request की details (method, URL, status code, response time) console या file में log करता है, predefined या custom formats में। Production में debugging, monitoring, और API traffic audit करने के लिए ज़रूरी है।

---

## 🔴 Problem it Solves
Without a request logger, when something goes wrong in production (500 errors, slow endpoints, suspicious traffic), there's no record of what requests came in, from where, with what response time. Debugging becomes guesswork. Manually adding `console.log` in every route is tedious, inconsistent, and easy to forget. Morgan centralizes this — one line of middleware logs every request automatically in a consistent, parseable format that can be piped to log files, log aggregators (ELK, Datadog), or monitoring dashboards.

## 🔴 यह क्यों बना? (Hindi)
Request logger के बिना, production में जब कुछ गड़बड़ होती है (500 errors, slow endpoints, suspicious traffic), तो कोई record नहीं होता कि कौन सी requests आईं, कहाँ से आईं, किस response time के साथ। Debugging guesswork बन जाती है। हर route में manually `console.log` डालना tedious, inconsistent है और भूल जाना आसान है। Morgan इसे centralize करता है — एक line का middleware हर request को automatically, consistent, parseable format में log करता है जो log files, log aggregators (ELK, Datadog), या monitoring dashboards में pipe हो सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `morgan(format)` returns an Express middleware function, registered with `app.use()`.
Step 2 → For every incoming request, Morgan hooks into the response lifecycle — it records the start time when the request arrives.
Step 3 → When `res.end()` is called (response finished), Morgan calculates the elapsed time and gathers tokens (method, url, status, response-time, etc.).
Step 4 → It formats these tokens according to the chosen format string (`'combined'`, `'dev'`, `'tiny'`, or custom).
Step 5 → The formatted log line is written to the configured output stream (stdout by default, or a file stream via the `stream` option).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `morgan(format)` एक Express middleware function return करता है, जो `app.use()` से register होता है।
Step 2 → हर incoming request के लिए, Morgan response lifecycle में hook करता है — request आने पर start time record करता है।
Step 3 → जब `res.end()` call होता है (response finish), Morgan elapsed time calculate करता है और tokens (method, url, status, response-time, etc.) gather करता है।
Step 4 → ये tokens को चुने गए format string (`'combined'`, `'dev'`, `'tiny'`, या custom) के अनुसार format करता है।
Step 5 → Formatted log line configured output stream (default stdout, या `stream` option से file stream) में लिखा जाता है।

---

## 🟡 Real World Example
**Swiggy order-service:** During a flash sale, order-service receives 10,000 requests/minute. Morgan with `'combined'` format logs each request: `IP - - [timestamp] "POST /api/orders HTTP/1.1" 201 1243 "-" "SwiggyApp/4.2 Android"`. These logs stream to a file, which is shipped to an ELK (Elasticsearch-Logstash-Kibana) stack. When the on-call engineer sees a spike in 500 errors on `/api/orders`, they filter Morgan logs by status code and timestamp to pinpoint exactly when and from which client version the errors started — without this, root-causing a production incident would take hours instead of minutes.

## 🟡 Real Example Hindi mein
**Swiggy order-service:** Flash sale के दौरान, order-service को 10,000 requests/minute मिलती हैं। Morgan `'combined'` format से हर request log करता है: `IP - - [timestamp] "POST /api/orders HTTP/1.1" 201 1243 "-" "SwiggyApp/4.2 Android"`। ये logs एक file में stream होते हैं, जो ELK (Elasticsearch-Logstash-Kibana) stack में ship होते हैं। जब on-call engineer `/api/orders` पर 500 errors का spike देखता है, वो Morgan logs को status code और timestamp से filter करके exactly pinpoint करता है कि errors कब और किस client version से शुरू हुए — इसके बिना, production incident को root-cause करना घंटों लग जाता, मिनटों के बदले।

---

## 💻 Code Example — Basic

```javascript
// morgan-basic.js
const express = require('express');
const morgan = require('morgan'); // npm install morgan

const app = express();

// 'dev' format: colored, concise — great for local development
// Example output: GET /api/users 200 15.234 ms - 123
app.use(morgan('dev'));

app.get('/api/users', (req, res) => {
  res.json({ users: ['Rahul', 'Priya'] }); // Morgan logs this request automatically
});

app.get('/api/error-test', (req, res) => {
  res.status(500).json({ error: 'Something broke' }); // Morgan logs status 500 too
});

app.listen(3000, () => console.log('Server on port 3000 — check console for Morgan logs'));
```

## 💻 Code Example — Advanced

```javascript
// morgan-advanced.js — Production setup: file logging + custom tokens + log rotation
const express = require('express');
const morgan = require('morgan');
const fs = require('fs');
const path = require('path');
const rfs = require('rotating-file-stream'); // npm install rotating-file-stream

const app = express();

// ─── 1. CUSTOM TOKEN: log authenticated user id ───────────────────────────────
morgan.token('user-id', (req) => (req.user ? req.user.id : 'anonymous'));

// ─── 2. CUSTOM FORMAT STRING combining built-in + custom tokens ───────────────
const customFormat =
  ':remote-addr - :user-id [:date[clf]] ":method :url HTTP/:http-version" :status :res[content-length] ":user-agent" :response-time ms';

// ─── 3. ROTATING FILE STREAM — creates a new log file daily, auto-compresses old ones
const accessLogStream = rfs.createStream('access.log', {
  interval: '1d', // rotate daily
  path: path.join(__dirname, 'logs'), // logs directory
  compress: 'gzip', // compress rotated files to save disk space
});

// ─── 4. DUAL LOGGING: errors (4xx/5xx) to console, everything to file ─────────
app.use(
  morgan(customFormat, {
    stream: accessLogStream, // all requests go to the rotating log file
  })
);

app.use(
  morgan('dev', {
    skip: (req, res) => res.statusCode < 400, // only log errors to console
  })
);

// Fake auth middleware to populate req.user for demonstration
app.use((req, res, next) => {
  req.user = { id: 'user_123' }; // simulate authenticated user
  next();
});

app.get('/api/orders', (req, res) => {
  res.json({ orders: [] }); // logged with user-id and full metadata
});

app.get('/api/crash', (req, res) => {
  res.status(500).json({ error: 'Internal error' }); // also printed to console due to skip logic
});

app.listen(3000, () => console.log('Production logging server running on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const morgan = require('morgan');
const app = express();

// Environment-based format: verbose for dev, compact+standard for prod
if (process.env.NODE_ENV === 'production') {
  app.use(morgan('combined')); // Apache-style combined log format — includes user-agent, referrer
} else {
  app.use(morgan('dev')); // colored, concise — good for local terminal
}

app.use(express.json());

app.get('/api/health', (req, res) => res.json({ status: 'ok' })); // health checks also logged

app.listen(5000, () => console.log('App running with environment-aware logging'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `morgan('dev')` (colored output) in production log files
✅ Correct: Use `'combined'` or a custom plain-text format for production — ANSI color codes in log files break log parsers (ELK, Datadog) that expect clean text.

```javascript
// Wrong — dev format writes ANSI escape codes into the log file, breaking parsers
app.use(morgan('dev', { stream: fs.createWriteStream('access.log') }));

// Right — use 'combined' (no color codes) for file/production logging
app.use(morgan('combined', { stream: fs.createWriteStream('access.log') }));
```

❌ Mistake 2: Logging sensitive data (passwords, tokens) via custom tokens
✅ Correct: Never log full request bodies or Authorization headers directly — mask or omit sensitive fields.

```javascript
// Wrong — logs the full Authorization header (JWT token) into log files
morgan.token('auth', (req) => req.headers.authorization);

// Right — log only non-sensitive identifiers
morgan.token('user-id', (req) => (req.user ? req.user.id : 'anon'));
```

---

## 🧠 Tricky Interview Question

```javascript
const express = require('express');
const morgan = require('morgan');
const app = express();

app.use(morgan('dev'));
app.get('/slow', (req, res) => {
  setTimeout(() => res.json({ done: true }), 2000); // 2 second delay
});
app.listen(3000);
```
When does Morgan's log line for `/slow` actually get printed — when the request arrives, or when the response finishes?

Answer: Morgan logs AFTER the response finishes, not when the request arrives. Morgan hooks into the `res.on('finish', ...)` event internally — it records the start timestamp when the request comes in, but the actual `console.log` line (with method, status, and `:response-time`) is only emitted once `res.end()` is called and the response has fully flushed. For `/slow`, the log line appears ~2000ms after the request arrives, not immediately. This is a common point of confusion for developers who expect synchronous, immediate logging like a simple `console.log` at the top of a route.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between Morgan's predefined formats 'combined', 'common', 'dev', 'short', and 'tiny'?
A1: **combined**: Apache-style, most verbose — includes remote address, user-agent, referrer; standard for production logs. **common**: similar to combined but without user-agent/referrer. **dev**: colored, concise, method+url+status+response-time — ideal for local development terminal. **short**: shorter than common, includes response time. **tiny**: minimal — method, url, status, content-length, response-time; lowest overhead.

Q2: How do you create a custom log format in Morgan?
A2: Pass a format string with Morgan's built-in tokens (`:method`, `:url`, `:status`, `:response-time`, `:date[clf]`, etc.) directly as the first argument: `morgan(':method :url :status :response-time ms')`. You can also define custom tokens with `morgan.token(name, callback)` and reference them as `:name` in the format string, letting you log request-specific data like `req.user.id`.

Q3: How do you log requests to a file instead of the console?
A3: Pass a `stream` option as the second argument: `morgan('combined', { stream: fs.createWriteStream('access.log', { flags: 'a' }) })`. The `flags: 'a'` appends rather than overwriting. For production, use a rotating file stream library (`rotating-file-stream`) to avoid one giant unbounded log file and to auto-compress/archive old logs.

Q4: Can Morgan log only errors (4xx/5xx) and skip successful requests?
A4: Yes, using the `skip` option: `morgan('combined', { skip: (req, res) => res.statusCode < 400 })`. This is useful for reducing noise in console output while still capturing all requests in a separate full log file — a common pattern is dual logging: full access log to file, errors-only to console/alerting.

Q5: Does Morgan impact performance in high-traffic production apps?
A5: Morgan itself is lightweight — formatting and writing a log line is fast. The real performance concern is the **output stream**: writing synchronously to a slow destination (e.g., a network-mounted disk, or stdout piped through many layers) can become a bottleneck under very high request rates. Best practice: write to local disk with buffered/async streams, use log rotation, and ship logs asynchronously to aggregators (filebeat, fluentd) rather than making the app itself push logs over network per-request.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need visibility into HTTP traffic for debugging, monitoring, or auditing
- Running in production and need structured access logs for ELK/Datadog/CloudWatch
- Debugging locally and want quick colored request/response feedback (`'dev'` format)

❌ Avoid when:
- Extremely performance-critical paths where even minimal logging overhead matters (rare) — consider sampling instead of logging every request
- You already have a comprehensive APM/observability tool (Datadog APM, New Relic) that captures equivalent request-level tracing — avoid duplicate logging pipelines

---

## 📊 Visual Diagram
```
REQUEST LIFECYCLE WITH MORGAN:

  Client ──▶ app.use(morgan('combined')) ──▶ route handler ──▶ res.end()
                     │                                             │
              record start time                            record end time
                     │                                             │
                     └─────────────── calculate ───────────────────┘
                                   response-time
                                        │
                                        ▼
                         format log line using tokens
                                        │
                                        ▼
                    write to stream (stdout / file / rotating log)

EXAMPLE OUTPUT ('dev' format):
  GET /api/orders 200 12.345 ms - 245
  POST /api/login 401 3.120 ms - 42
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Morgan | HTTP request logger middleware | HTTP request logging middleware |
| Token | Placeholder in format string (:method, :status) | Format string में placeholder |
| Stream | Destination for log output | Log output का destination |
| combined/dev/tiny | Predefined log formats | Pre-defined log formats |
| Log rotation | Splitting logs into dated files | Logs को date-wise files में split करना |
| skip | Conditionally skip logging a request | Condition पर logging skip करना |

---

## ⚡ 3-Line Summary
English:
1. Morgan is Express's standard HTTP request logger — logs method, URL, status, and response time automatically for every request.
2. Use `'dev'` for local development (colored) and `'combined'`/custom formats for production file logging (plain text, log-parser friendly).
3. Combine with rotating file streams and `skip` filters for production-grade logging pipelines feeding into ELK/Datadog.

Hindi:
1. Morgan Express का standard HTTP request logger है — हर request के लिए method, URL, status, और response time automatically log करता है।
2. Local development के लिए `'dev'` (colored) और production file logging के लिए `'combined'`/custom formats use करो (plain text, log-parser friendly)।
3. Production-grade logging pipelines (ELK/Datadog) के लिए rotating file streams और `skip` filters के साथ combine करो।

---

## ➡️ Next Topic
**109. Rate Limiting in Express** — API abuse prevention, throttling repeated requests from the same client।
