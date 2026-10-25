# 250. Logging — Winston + Morgan
# हिंदी में: Winston + Morgan — Application और HTTP Logging

---

## 🔵 Simple Definition (English)
**Winston** is a flexible application-level logging library for Node.js — it lets you log messages with levels (error, warn, info, debug), format them (JSON, colorized text), and send them to multiple destinations (console, files, external services) called **transports**. **Morgan** is Express middleware that automatically logs every incoming HTTP request (method, URL, status code, response time). Together they cover both "what my code is doing" (Winston) and "what requests are hitting my server" (Morgan).

## 🔵 सरल परिभाषा (Hindi)
**Winston** एक flexible application-level logging library है Node.js के लिए — ये messages को levels (error, warn, info, debug) के साथ log करता है, format करता है (JSON, colorized text), और multiple destinations पर भेजता है जिन्हें **transports** कहते हैं (console, files, external services)। **Morgan** एक Express middleware है जो हर incoming HTTP request को automatically log करता है (method, URL, status code, response time)। दोनों मिलकर cover करते हैं — "मेरा code क्या कर रहा है" (Winston) और "server पर कौन सी requests आ रही हैं" (Morgan)।

---

## 🔴 Problem it Solves
```
BEFORE (console.log everywhere):
  console.log('User logged in:', userId);
  console.log('ERROR:', err);
  console.log(req.method, req.url);

  Problems:
    1. No log levels — can't filter "only show errors in production"
    2. No structure — hard to search/parse later
    3. No file persistence — logs disappear when terminal closes
    4. No timestamps by default
    5. Printed to stdout only — can't route errors to a separate file
       or send critical errors to Slack/email
    6. Every HTTP request logged manually is tedious and inconsistent

WINSTON + MORGAN SOLUTION:
  - Winston: define levels, multiple transports (console + file + cloud),
    consistent format (JSON with timestamp), easy to filter by environment
  - Morgan: one line of middleware logs EVERY request automatically,
    consistent format (Apache-style or custom), pipes into Winston
    so HTTP logs and app logs end up in the same files

  Result: structured, filterable, persistent, production-ready logging
  instead of scattered console.log statements.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले (हर जगह console.log):
  - कोई log level नहीं — production में सिर्फ errors filter नहीं कर सकते
  - कोई structure नहीं — बाद में search/parse करना मुश्किल
  - file में persist नहीं होता — terminal बंद करने पर logs गायब
  - हर request manually log करना boring और inconsistent है

Winston + Morgan SOLUTION:
  - Winston: levels define करो, multiple transports (console + file + cloud),
    consistent JSON format, environment के हिसाब से filter आसान
  - Morgan: एक middleware line हर request को automatically log करता है,
    Winston में pipe करके सब logs एक जगह आते हैं
```

---

## 🟢 How it Works — Step by Step

Step 1 → Create a Winston `logger` instance with levels and transports (Console transport for dev, File transport for production, maybe a cloud transport like CloudWatch/Elasticsearch).
Step 2 → Configure Morgan with a format string (e.g., `'combined'` or custom), and pipe its output stream into Winston's `logger.stream` (via `logger.info`) instead of raw `console.log`.
Step 3 → Mount Morgan as the first middleware in Express so EVERY request (even ones that error out later) gets logged.
Step 4 → Use `logger.error()`, `logger.warn()`, `logger.info()`, `logger.debug()` throughout application code (DB calls, payment processing, auth) instead of `console.log`.
Step 5 → In production, set log level to `info` or `warn` (less noise); in development, set to `debug` (verbose). Rotate log files so they don't grow unbounded (using `winston-daily-rotate-file`).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Winston `logger` instance बनाओ levels और transports के साथ (dev के लिए Console, production के लिए File, cloud transport भी हो सकता है)।
Step 2 → Morgan को format string के साथ configure करो (`'combined'` या custom), और उसका output Winston में pipe करो — raw `console.log` नहीं।
Step 3 → Morgan को Express में सबसे पहले middleware के रूप में mount करो ताकि हर request (even error होने वाली भी) log हो।
Step 4 → पूरे application code में `logger.error()`, `logger.warn()`, `logger.info()`, `logger.debug()` use करो, `console.log` नहीं।
Step 5 → Production में log level `info`/`warn` रखो (कम noise), development में `debug` (verbose)। Log files rotate करो ताकि disk भर न जाए।

---

## 🟡 Real World Example
**Swiggy order service:** Every incoming API request (`POST /orders`, `GET /orders/:id`) is logged by Morgan with method, path, status, response time — written to `access.log`. Inside the order controller, Winston logs business events: `logger.info('Order placed', { orderId, restaurantId, amount })`, and on failure: `logger.error('Payment gateway timeout', { orderId, err: err.message })` written to `error.log`. When an order fails in production at 2 AM, the on-call engineer greps `error.log` by `orderId` to trace exactly what happened — no need to reproduce the bug.

## 🟡 Real Example Hindi mein
**Swiggy order service:** हर incoming API request (`POST /orders`, `GET /orders/:id`) Morgan द्वारा log होती है method, path, status, response time के साथ — `access.log` में लिखी जाती है। Order controller के अंदर, Winston business events log करता है: `logger.info('Order placed', {...})`, और failure पर `logger.error('Payment gateway timeout', {...})` जो `error.log` में जाता है। जब production में रात 2 बजे order fail होता है, on-call engineer `orderId` से `error.log` grep करके exact समस्या पता कर लेता है — bug reproduce करने की ज़रूरत नहीं।

---

## 💻 Code Example — Basic

```javascript
// logger-basic.js
// npm install winston morgan express
const winston = require('winston');

// ─── 1. CREATE A WINSTON LOGGER ────────────────────────────────────────────
const logger = winston.createLogger({
  level: 'info', // only log 'info' and above (info, warn, error) — debug is skipped
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }), // add timestamp
    winston.format.printf(({ timestamp, level, message }) => {
      return `${timestamp} [${level.toUpperCase()}]: ${message}`; // plain readable line
    })
  ),
  transports: [
    new winston.transports.Console(), // print to terminal
    new winston.transports.File({ filename: 'error.log', level: 'error' }), // only errors go here
    new winston.transports.File({ filename: 'combined.log' }), // everything goes here
  ],
});

// ─── 2. USE THE LOGGER ─────────────────────────────────────────────────────
logger.info('Server starting up...'); // normal informational log
logger.warn('Disk space running low: 85% used'); // warning, not critical
logger.error('Database connection failed'); // critical error — goes to error.log too

// ─── 3. LOG WITH EXTRA METADATA ────────────────────────────────────────────
logger.info('User logged in', { userId: 'u123', ip: '103.21.244.10' }); // structured extra data

// Run: node logger-basic.js
// Check: console output + error.log + combined.log files created in same folder
```

## 💻 Code Example — Advanced

```javascript
// logger-advanced.js — production setup: env-based levels, file rotation, Morgan pipe
// npm install winston winston-daily-rotate-file morgan express

const winston = require('winston');
require('winston-daily-rotate-file'); // adds DailyRotateFile transport

const isProduction = process.env.NODE_ENV === 'production';

// ─── 1. JSON FORMAT FOR PRODUCTION, PRETTY FOR DEV ─────────────────────────
const logger = winston.createLogger({
  level: isProduction ? 'info' : 'debug', // verbose in dev, quieter in prod
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }), // capture stack traces for Error objects
    isProduction
      ? winston.format.json() // machine-readable in prod (easy to parse/search)
      : winston.format.combine(winston.format.colorize(), winston.format.simple()) // human readable in dev
  ),
  defaultMeta: { service: 'swiggy-order-service' }, // tag every log with service name
  transports: [
    new winston.transports.Console(),
    // Rotate error logs daily, keep 14 days, auto-zip old ones
    new winston.transports.DailyRotateFile({
      filename: 'logs/error-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      level: 'error',
      maxFiles: '14d', // delete logs older than 14 days
      zippedArchive: true, // gzip rotated files to save disk space
    }),
    new winston.transports.DailyRotateFile({
      filename: 'logs/combined-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      maxFiles: '30d',
      zippedArchive: true,
    }),
  ],
  exitOnError: false, // don't crash the process on a logging error
});

// ─── 2. MORGAN PIPED INTO WINSTON ──────────────────────────────────────────
const morgan = require('morgan');

// morgan.stream — a writable stream that forwards each line to winston.info
const morganMiddleware = morgan(
  isProduction ? 'combined' : 'dev', // Apache-style in prod, colored short format in dev
  {
    stream: {
      write: (message) => logger.info(message.trim()), // pipe morgan's line into winston
    },
  }
);

// ─── 3. HANDLE UNCAUGHT EXCEPTIONS / REJECTIONS ────────────────────────────
logger.exceptions.handle(
  new winston.transports.File({ filename: 'logs/exceptions.log' })
);
process.on('unhandledRejection', (reason) => {
  logger.error('Unhandled Promise Rejection', { reason }); // log promise rejections too
});

module.exports = { logger, morganMiddleware };
```

---

## 🟠 Express.js Integration

```javascript
// app.js — wiring logger + morgan into a real Express app
const express = require('express');
const { logger, morganMiddleware } = require('./logger-advanced');

const app = express();
app.use(express.json());
app.use(morganMiddleware); // MUST be mounted early — logs every request, even 404s

app.post('/orders', async (req, res) => {
  try {
    const { restaurantId, items, amount } = req.body;
    logger.info('Order placed', { restaurantId, amount, itemCount: items.length }); // business event
    res.status(201).json({ message: 'Order placed successfully' });
  } catch (err) {
    logger.error('Order creation failed', { error: err.message, stack: err.stack }); // error with context
    res.status(500).json({ error: 'Something went wrong' });
  }
});

// Centralized error-handling middleware — logs every unhandled error
app.use((err, req, res, next) => {
  logger.error(`Unhandled error on ${req.method} ${req.url}`, { error: err.message });
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(3000, () => logger.info('Server listening on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `console.log` and Winston interchangeably
```javascript
// WRONG: mixing console.log with logger — inconsistent, unfiltered, not written to files
console.log('Payment processed for order', orderId);
logger.info('Payment processed', { orderId });

// CORRECT: always use the logger, never console.log in app code
logger.info('Payment processed', { orderId });
```

❌ **Mistake 2:** Setting log level to `debug` in production
```javascript
// WRONG: debug level in production floods log files with noise, hides real errors
const logger = winston.createLogger({ level: 'debug' }); // always debug, even in prod

// CORRECT: level based on environment
const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
});
```

❌ **Mistake 3:** Not rotating log files
```javascript
// WRONG: single ever-growing file — fills up disk over months, crashes the server
new winston.transports.File({ filename: 'app.log' });

// CORRECT: daily rotation with retention limit
new winston.transports.DailyRotateFile({
  filename: 'logs/app-%DATE%.log',
  maxFiles: '14d', // auto-delete logs older than 14 days
});
```

---

## 🧠 Tricky Interview Question

```javascript
const winston = require('winston');
const logger = winston.createLogger({
  level: 'warn', // only warn and ERROR show up
  transports: [new winston.transports.Console()],
});

logger.error('Database down');   // ?
logger.warn('High memory usage'); // ?
logger.info('User logged in');    // ?
logger.debug('Cache hit for key x'); // ?
```
Answer: Only `logger.error` and `logger.warn` will print. Winston's npm log levels have a numeric priority: `error=0, warn=1, info=2, http=3, verbose=4, debug=5, silly=6`. Setting `level: 'warn'` means "log this level AND anything with a LOWER number (higher severity)" — so `error` (0) and `warn` (1) pass, but `info` (2) and `debug` (5) are suppressed because their numbers are higher than the configured threshold. This is why in production you set `level: 'info'` (allows error, warn, info) and skip the noisy `debug`/`verbose`/`silly`.

---

## ⚫ Interview Questions + Answers

**Q1: What is a Winston "transport" and name three common ones?**
A1: A transport is a destination where Winston sends log output. Common transports: `Console` (prints to terminal, useful in dev), `File` (writes to a local file, useful for persistence), and `DailyRotateFile` or cloud transports like `WinstonCloudWatch`/Elasticsearch transport (for production, centralized logging). You can attach multiple transports to one logger, each with its own level filter — e.g., only `error` level goes to a dedicated `error.log` while everything goes to `combined.log`.

**Q2: What's the difference between Morgan's `'combined'` and `'dev'` format?**
A2: `'combined'` is the Apache-style standard log format used in production — includes IP, timestamp, HTTP version, referrer, and user-agent, good for audit/analytics tools. `'dev'` is a short, colorized format (method, URL, status color-coded, response time) meant for quick visual scanning in a development terminal — not suitable for production because it lacks IP/user-agent info and uses ANSI color codes that look messy in log files.

**Q3: Why should Morgan be mounted as early as possible in the Express middleware chain?**
A3: Express middleware executes in order. If Morgan is placed after route handlers or after an error-throwing middleware, requests that fail early (e.g., a malformed body that another middleware rejects) never reach Morgan and won't be logged. Mounting it first (right after `express.json()`) guarantees every incoming request — successful or not — gets an access log entry, which is critical for debugging "which requests are even hitting my server."

**Q4: How do you pipe Morgan's output into Winston instead of letting Morgan write directly to stdout?**
A4: Morgan accepts a `stream` option with a custom `write(message)` function. Instead of the default `process.stdout`, you pass `{ write: (msg) => logger.info(msg.trim()) }`. This way every HTTP access line is routed through Winston's formatting/transports (so it also lands in `combined.log`, gets JSON-formatted in prod, etc.) instead of being a separate, inconsistent stream.

**Q5: Why use structured metadata (`logger.info('msg', {orderId, userId})`) instead of string concatenation?**
A5: String concatenation (`logger.info('Order ' + orderId + ' placed')`) produces unstructured text that's hard to search/filter at scale. Passing an object as the second argument lets Winston (especially with `winston.format.json()`) attach it as structured fields. In production, logs are often shipped to Elasticsearch/CloudWatch where you'd want to query `orderId:"ORD123"` directly — that only works if `orderId` is a real field, not buried inside a free-text string.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production Node.js/Express application that needs persistent, filterable, leveled logs
- Microservices where you need to trace a request across logs by correlation/request ID
- You need different log destinations for different severities (errors to Slack, info to file)

❌ Avoid when:
- A tiny throwaway script or one-off local test — plain `console.log` is fine
- You already have a dedicated APM/observability tool that captures everything (though Winston often still complements it for structured app logs)

---

## 📊 Visual Diagram
```
REQUEST FLOW WITH MORGAN + WINSTON
──────────────────────────────────────────────────────────

  Client ──▶ Express App
               │
               ▼
          [ Morgan middleware ]  ── logs every request line
               │                     (method, url, status, time)
               ▼                           │
          [ Route Handler ]                │ piped via custom stream
               │                            ▼
         logger.info() / logger.error() ─▶ [ Winston Logger ]
               │                            │
               ▼                     ┌──────┴───────┬───────────────┐
        Business logic           Console       error.log      combined.log
       (DB calls, payments)      (dev view)   (errors only)  (everything)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transport | Winston's log output destination | Log भेजने की जगह (console/file) |
| Log Level | Severity ranking (error, warn, info...) | Severity का क्रम |
| Morgan | Express HTTP request logger middleware | HTTP request log करने वाला middleware |
| Format | How log lines are structured (JSON/plain) | Log कैसे structure होगा |
| Rotation | Splitting logs into dated files, auto-delete old | पुराने logs delete करना |
| defaultMeta | Fields auto-attached to every log entry | हर log में auto-add होने वाले fields |
| Stream | Custom write target for Morgan output | Morgan का custom output target |

---

## ⚡ 3-Line Summary
**English:**
1. Winston handles application-level logging with levels, formats, and multiple transports (console, file, cloud); Morgan auto-logs every HTTP request in Express.
2. Pipe Morgan's output into Winston so all logs (HTTP + business) land in the same structured files.
3. Use environment-based log levels (`debug` in dev, `info`/`warn` in prod) and rotate files daily to avoid unbounded disk growth.

**Hindi:**
1. Winston application-level logging handle करता है levels, formats, multiple transports के साथ; Morgan Express में हर HTTP request auto-log करता है।
2. Morgan का output Winston में pipe करो ताकि सब logs (HTTP + business) एक जगह structured files में आएं।
3. Environment के हिसाब से log level रखो (dev में debug, prod में info/warn) और daily rotation करो ताकि disk ना भरे।

---

## ➡️ Next Topic
**251. Structured Logging** — JSON logs, correlation IDs, और production में logs को searchable बनाना।
