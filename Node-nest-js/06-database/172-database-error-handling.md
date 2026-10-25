# 172. Database Error Handling
# हिंदी में: Database Error Handling — DB Errors को सही तरीके से Handle करना

---

## 🔵 Simple Definition (English)
**Database error handling** means catching, classifying, and responding appropriately to the different kinds of errors a database can throw — connection failures, constraint violations (duplicate key, foreign key), validation errors, timeouts, deadlocks — instead of letting them crash the server or leak raw internal details to the client.

## 🔵 सरल परिभाषा (Hindi)
**Database error handling** का मतलब है database से आने वाली अलग-अलग तरह की errors — connection failure, constraint violation (duplicate key, foreign key), validation error, timeout, deadlock — को catch, classify, और सही तरीके से respond करना, ना कि server को crash होने देना या raw internal details client को दिखा देना।

---

## 🔴 Problem it Solves
Without proper error handling:
1. **Server crashes** — an unhandled DB rejection can crash the whole Node process if not caught.
2. **Leaking internals** — sending raw error messages (`duplicate key value violates unique constraint "users_email_key"`) to the client exposes schema details to attackers.
3. **Wrong HTTP status codes** — returning 500 for a user's duplicate-email signup attempt (should be 409 Conflict) confuses clients and breaks retry logic.
4. **Silent data loss** — not distinguishing a transient network blip from a permanent validation error means apps might retry things that should never be retried (duplicate charges!) or give up on things that should be retried (timeouts).

## 🔴 यह क्यों बना? (Hindi)
सही error handling के बिना:
1. **Server crash** — unhandled DB rejection पूरा Node process crash कर सकता है।
2. **Internal details leak** — raw error message (`duplicate key value violates unique constraint "users_email_key"`) client को भेजना schema details attacker को दिखा देता है।
3. **गलत HTTP status codes** — duplicate-email signup पर 500 भेजना (जबकि 409 Conflict होना चाहिए) client confuse करता है।
4. **Silent data loss** — temporary network glitch और permanent validation error में फर्क ना करने से apps गलत चीज़ें retry करती हैं (duplicate payment!) या सही चीज़ें retry नहीं करतीं (timeout)।

---

## 🟢 How it Works — Step by Step

Step 1 → Wrap every DB call in `try/catch` (or handle rejected Promises) — never let a DB error propagate unhandled.
Step 2 → Inspect the error's `code`/`name` property to classify it: duplicate key (`11000` in MongoDB, `23505` in Postgres), validation error, connection error, timeout.
Step 3 → Map the classified error to an appropriate HTTP status code and safe, user-friendly message (never the raw DB error string).
Step 4 → Log the FULL original error (with stack trace) server-side for debugging — but send only the safe message to the client.
Step 5 → For transient errors (connection drop, timeout), optionally retry with backoff; for permanent errors (validation, duplicate), fail fast and inform the client clearly.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → हर DB call को `try/catch` में wrap करो — कभी भी DB error को unhandled propagate मत होने दो।
Step 2 → Error के `code`/`name` property से classify करो: duplicate key (MongoDB में `11000`, Postgres में `23505`), validation error, connection error, timeout।
Step 3 → Classified error को सही HTTP status code और safe, user-friendly message में map करो (raw DB error string कभी नहीं)।
Step 4 → पूरा original error (stack trace सहित) server-side log करो debugging के लिए — client को सिर्फ safe message भेजो।
Step 5 → Transient errors (connection drop, timeout) के लिए backoff के साथ retry करो; permanent errors (validation, duplicate) के लिए fail fast करो और client को clearly बताओ।

---

## 🟡 Real World Example
**Razorpay signup flow:** When a user signs up with an email already in the database, MongoDB throws a duplicate key error (`E11000`). Razorpay's API must catch this specific error code and return `409 Conflict` with `{ error: "Email already registered" }` — NOT a generic 500, and NOT the raw MongoDB error string (which would reveal the exact index name/schema). Meanwhile, if the DB connection itself drops mid-request (network blip to the DB cluster), the API should return `503 Service Unavailable` and the error-logging system (Sentry/Datadog) should alert on-call engineers — this is a totally different failure class from "user typed a duplicate email."

## 🟡 Real Example Hindi mein
**Razorpay signup flow:** जब कोई user ऐसे email से signup करे जो पहले से DB में है, MongoDB duplicate key error (`E11000`) throw करता है। Razorpay के API को यह specific error code catch करना चाहिए और `409 Conflict` के साथ `{ error: "Email already registered" }` return करना चाहिए — generic 500 नहीं, और raw MongoDB error string भी नहीं (जो exact index name/schema reveal कर देगा)। वहीं अगर request के बीच DB connection ही टूट जाये (DB cluster से network glitch), API को `503 Service Unavailable` return करना चाहिए और error-logging system (Sentry/Datadog) को on-call engineers को alert करना चाहिए — यह "user ने duplicate email डाला" से पूरी तरह अलग failure class है।

---

## 💻 Code Example — Basic

```javascript
// basic-db-error-handling.js
// Install: npm install mongoose

const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true }, // unique index -> duplicate key error
  age: { type: Number, min: 18 },                          // validation rule
});
const User = mongoose.model('User', userSchema);

async function createUser(data) {
  try {
    const user = await User.create(data); // may throw ValidationError or duplicate key error
    return { success: true, user };
  } catch (err) {
    // MongoDB duplicate key error has code 11000
    if (err.code === 11000) {
      return { success: false, status: 409, message: 'Email already registered' };
    }
    // Mongoose validation error has name 'ValidationError'
    if (err.name === 'ValidationError') {
      const messages = Object.values(err.errors).map(e => e.message); // collect field errors
      return { success: false, status: 400, message: messages.join(', ') };
    }
    // Unknown error: log full details, return generic message to caller
    console.error('Unexpected DB error:', err); // full stack logged server-side only
    return { success: false, status: 500, message: 'Something went wrong' };
  }
}

module.exports = { createUser };
```

## 💻 Code Example — Advanced

```javascript
// advanced-db-error-handling.js — centralized error classification + retry logic

class AppError extends Error {
  constructor(message, statusCode, isOperational = true) {
    super(message);
    this.statusCode = statusCode;     // HTTP status to send
    this.isOperational = isOperational; // true = expected error, false = programming bug
    Error.captureStackTrace(this, this.constructor);
  }
}

// Centralized DB error classifier — reusable across the whole app
function classifyDbError(err) {
  // MongoDB duplicate key
  if (err.code === 11000) {
    const field = Object.keys(err.keyPattern || {})[0] || 'field';
    return new AppError(`${field} already exists`, 409);
  }
  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const msgs = Object.values(err.errors).map(e => e.message).join(', ');
    return new AppError(msgs, 400);
  }
  // MongoDB cast error (invalid ObjectId etc.)
  if (err.name === 'CastError') {
    return new AppError(`Invalid ${err.path}: ${err.value}`, 400);
  }
  // Connection-level errors -> transient, service unavailable
  if (err.name === 'MongoNetworkError' || err.name === 'MongooseServerSelectionError') {
    return new AppError('Database temporarily unavailable', 503);
  }
  // Postgres unique violation
  if (err.code === '23505') {
    return new AppError('Duplicate entry', 409);
  }
  // Postgres foreign key violation
  if (err.code === '23503') {
    return new AppError('Referenced record does not exist', 400);
  }
  // Fallback: unknown/programming error -> not safe to expose details
  return new AppError('Internal server error', 500, false);
}

// Retry wrapper for transient errors (connection blips, deadlocks) with exponential backoff
async function withRetry(fn, { retries = 3, baseDelayMs = 200 } = {}) {
  let lastErr;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastErr = err;
      const isTransient = err.name === 'MongoNetworkError' || err.code === '40001'; // e.g. serialization failure
      if (!isTransient || attempt === retries) throw err; // give up on permanent errors or last attempt
      const delay = baseDelayMs * 2 ** attempt; // exponential backoff: 200ms, 400ms, 800ms...
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw lastErr;
}

// Express error-handling middleware (must have 4 args to be recognized as error handler)
function errorHandler(err, req, res, next) {
  const appErr = err instanceof AppError ? err : classifyDbError(err);

  if (!appErr.isOperational) {
    console.error('UNEXPECTED ERROR:', err); // log full stack for programming bugs
  }

  res.status(appErr.statusCode).json({
    success: false,
    message: appErr.isOperational ? appErr.message : 'Something went wrong',
  });
}

module.exports = { AppError, classifyDbError, withRetry, errorHandler };
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { classifyDbError, withRetry, errorHandler } = require('./advanced-db-error-handling');
const User = require('./models/User');

const app = express();
app.use(express.json());

app.post('/signup', async (req, res, next) => {
  try {
    const user = await withRetry(() => User.create(req.body)); // auto-retries transient failures
    res.status(201).json({ success: true, user });
  } catch (err) {
    next(classifyDbError(err)); // forward classified error to centralized handler
  }
});

app.use(errorHandler); // centralized error-handling middleware, registered LAST
app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Sending raw DB error messages directly to the client
✅ Correct: Classify and map to a safe message — never expose index names, table structure, or stack traces.

```javascript
// Wrong
catch (err) { res.status(500).json({ error: err.message }); } // leaks internals

// Right
catch (err) { const appErr = classifyDbError(err); res.status(appErr.statusCode).json({ error: appErr.message }); }
```

❌ Mistake 2: Retrying non-idempotent operations blindly
✅ Correct: Only retry operations that are safe to repeat (reads, idempotent writes with unique request IDs). Retrying a payment charge on a timeout (when the charge may have actually succeeded) can double-charge the user — use idempotency keys instead.

---

## 🧠 Tricky Interview Question

```javascript
// A write operation times out after 5 seconds, so the client retries the SAME request.
// Unknown to the client, the first request actually succeeded on the DB side
// just after the timeout fired. What problem does this cause, and how do you prevent it?
```
Answer: This causes a **duplicate write** (e.g., double order creation, double payment charge) — the classic "timeout doesn't mean failure" problem. The fix is **idempotency keys**: the client sends a unique idempotency key with the request; the server checks if that key was already processed (store result in Redis/DB) and if so, returns the SAME result without re-executing the write. This decouples "did my request get a response" from "did the operation actually happen," making retries safe.

---

## ⚫ Interview Questions + Answers

Q1: How do you distinguish a transient DB error from a permanent one?
A1: Transient errors relate to infrastructure/timing: connection drops, network timeouts, deadlocks, serialization failures (retryable — the same operation might succeed if retried). Permanent errors relate to the data/request itself: validation failures, duplicate keys, foreign key violations (retrying with the SAME input will always fail again — must fix the input, not retry). Classify by error code/name and only apply retry logic to the transient category.

Q2: What's the difference between operational and programming errors in Node.js error handling?
A2: **Operational errors** are expected failure modes of a working system — invalid user input, duplicate record, DB temporarily down, network timeout. They should be handled gracefully and shown to the user appropriately. **Programming errors** are bugs — undefined is not a function, wrong types passed, logic errors. These indicate the code itself is broken; the safest action is often to log extensively and let the process crash/restart (via a process manager) rather than continue in a corrupted state.

Q3: Why is it dangerous to let an unhandled promise rejection from a DB call go uncaught in Node.js?
A3: In modern Node.js, an unhandled promise rejection terminates the process by default (since Node 15+, `--unhandled-rejections=strict` is default behavior in many setups). A single uncaught DB error could crash the entire server, dropping ALL in-flight requests, not just the one that failed. Always wrap async DB code in try/catch or attach `.catch()` handlers.

Q4: How should connection pool exhaustion errors be handled?
A4: Detect via timeout errors when acquiring a connection from the pool (e.g., "timeout exceeded when trying to connect"). Mitigate by: setting a reasonable pool size matched to expected concurrency, adding a request queue/timeout at the application level, monitoring pool usage metrics, and returning `503 Service Unavailable` with a `Retry-After` header rather than hanging indefinitely.

Q5: What is a dead-letter / fallback strategy for failed DB writes in an async pipeline (e.g., a queue worker)?
A5: If a worker consuming from a queue fails to write to the DB after retries, instead of losing the message or retrying forever, move it to a **dead-letter queue (DLQ)** for manual inspection/reprocessing later, and alert monitoring. This prevents one bad message from blocking the whole queue (head-of-line blocking) while not silently losing data.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production API that talks to a database — always classify and handle errors explicitly.
- Building reusable error-classification middleware across many routes/services.

❌ Avoid when:
- N/A — proper DB error handling is always needed in production code; the only judgment call is how elaborate the classification/retry logic needs to be for the use case's criticality.

---

## 📊 Visual Diagram
```
DB CALL
  │
  ▼
try { await Model.create(data) }
  │
  ├─ SUCCESS ──────────────▶ return 201 + data
  │
  └─ ERROR
       │
       ├─ code 11000 (duplicate)      → 409 Conflict
       ├─ ValidationError             → 400 Bad Request
       ├─ CastError (bad ObjectId)    → 400 Bad Request
       ├─ MongoNetworkError           → 503 + retry transient
       └─ Unknown                     → log full error, 500 generic message
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Operational error | Expected failure (bad input, duplicate) | Expected failure |
| Programming error | Bug in code | Code की bug |
| Idempotency key | Unique key to make retries safe | Safe retry के लिए unique key |
| Transient error | Temporary, retryable failure | Temporary, retry-able error |
| Dead-letter queue | Storage for permanently failed messages | हमेशा fail हुए messages का storage |
| Error classification | Mapping raw errors to app-level errors | Raw error को app error में map करना |

---

## ⚡ 3-Line Summary
English:
1. Always classify DB errors (duplicate key, validation, connection, timeout) instead of exposing raw error messages to clients.
2. Map classified errors to correct HTTP status codes and log full details server-side for debugging.
3. Retry only transient/idempotent failures with backoff; use idempotency keys to make retries of writes safe.

Hindi:
1. DB errors को हमेशा classify करो (duplicate key, validation, connection, timeout) — raw error messages client को मत भेजो।
2. Classified errors को सही HTTP status codes में map करो और debugging के लिए server-side पूरी details log करो।
3. सिर्फ transient/idempotent failures को backoff के साथ retry करो; writes के retry को safe बनाने के लिए idempotency keys use करो।

---

## ➡️ Next Topic
**173. REST API Design — Best Practices** — अच्छे, consistent, और scalable REST APIs design करने के principles।
