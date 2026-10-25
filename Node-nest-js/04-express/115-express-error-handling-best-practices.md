# 115. Express Error Handling — Best Practices
# हिंदी में: Express Error Handling — Best Practices

---

## 🔵 Simple Definition (English)
**Express error handling best practices** refer to a disciplined approach for catching, classifying, and responding to errors across an Express app: centralized error-handling middleware, consistent error response shapes, distinguishing operational (expected) errors from programmer (bug) errors, and properly catching async errors that Express doesn't handle automatically by default.

## 🔵 सरल परिभाषा (Hindi)
**Express error handling best practices** का मतलब है errors को catch, classify, और respond करने का एक disciplined approach पूरी Express app में: centralized error-handling middleware, consistent error response shapes, operational (expected) errors को programmer (bug) errors से अलग करना, और async errors को properly catch करना जो Express by default automatically handle नहीं करता।

---

## 🔴 Problem it Solves
Scattered `try/catch` blocks with inconsistent error responses across dozens of routes lead to: inconsistent API error formats (some return `{error: "..."}`, others `{message: "..."}`), unhandled promise rejections silently crashing or hanging the server, stack traces leaking to clients in production (security risk), and no central place to log errors for monitoring. A disciplined error-handling strategy (custom error classes, centralized middleware, async wrapper utilities) solves all of these, making the app predictable, debuggable, and secure.

## 🔴 यह क्यों बना? (Hindi)
दर्जनों routes में scattered `try/catch` blocks के साथ inconsistent error responses से ये problems होती हैं: inconsistent API error formats (कुछ `{error: "..."}` return करते हैं, कुछ `{message: "..."}`), unhandled promise rejections silently server crash या hang कर देती हैं, production में stack traces clients को leak होते हैं (security risk), और errors log करने के लिए कोई central जगह नहीं। एक disciplined error-handling strategy (custom error classes, centralized middleware, async wrapper utilities) ये सब solve करती है, app को predictable, debuggable, और secure बनाती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Define a custom `AppError` class extending `Error`, carrying `statusCode` and an `isOperational` flag to distinguish expected errors (bad input, not found) from bugs.
Step 2 → Wrap async route handlers with a utility (`catchAsync`) that automatically forwards rejected promises to `next(err)` — Express doesn't catch async errors in `async` functions automatically unless you explicitly call `next(err)` in a catch block.
Step 3 → Register a centralized error-handling middleware LAST, with 4 parameters `(err, req, res, next)` — Express recognizes this signature specifically as error middleware.
Step 4 → Inside this middleware, check `err.isOperational`: if true, send a clean client-facing message with the appropriate status code; if false (a genuine bug), log the full stack trace internally and send a generic "Something went wrong" message (never leak internals to the client).
Step 5 → Add `process.on('unhandledRejection')` and `process.on('uncaughtException')` handlers at the process level as a final safety net for errors that somehow escape Express's middleware chain entirely.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `Error` से extend करने वाली custom `AppError` class define करो, जिसमें `statusCode` और `isOperational` flag हो expected errors (bad input, not found) को bugs से अलग करने के लिए।
Step 2 → Async route handlers को एक utility (`catchAsync`) से wrap करो जो automatically rejected promises को `next(err)` पर forward करे — Express `async` functions में async errors automatically catch नहीं करता जब तक आप explicitly catch block में `next(err)` call न करें।
Step 3 → एक centralized error-handling middleware LAST register करो, 4 parameters के साथ `(err, req, res, next)` — Express इस signature को specifically error middleware के रूप में recognize करता है।
Step 4 → इस middleware के अंदर, `err.isOperational` check करो: true हो तो client-facing clean message भेजो appropriate status code के साथ; false हो (genuine bug) तो पूरा stack trace internally log करो और generic "Something went wrong" message भेजो (client को internals कभी leak मत करो)।
Step 5 → Process level पर `process.on('unhandledRejection')` और `process.on('uncaughtException')` handlers जोड़ो final safety net के रूप में उन errors के लिए जो Express के middleware chain से पूरी तरह बच जाते हैं।

---

## 🟡 Real World Example
**Razorpay payment gateway API:** When a merchant's payment request fails due to insufficient funds (an EXPECTED, operational error), Razorpay's API returns a clean `400 Bad Request` with `{ error: { code: "BAD_REQUEST_ERROR", description: "Insufficient funds" } }`. But if an internal bug causes a database connection failure (a PROGRAMMER error — unexpected), the centralized error handler catches it, logs the full stack trace to their monitoring system (Sentry/Datadog) for engineers to investigate, but returns only `{ error: { code: "SERVER_ERROR", description: "Something went wrong" } }` to the merchant — never exposing internal details like database hostnames or stack traces, which could aid an attacker or just confuse integrators.

## 🟡 Real Example Hindi mein
**Razorpay payment gateway API:** जब किसी merchant की payment request insufficient funds की वजह से fail होती है (एक EXPECTED, operational error), Razorpay का API clean `400 Bad Request` return करता है `{ error: { code: "BAD_REQUEST_ERROR", description: "Insufficient funds" } }` के साथ। लेकिन अगर कोई internal bug database connection failure करा दे (एक PROGRAMMER error — unexpected), centralized error handler इसे catch करता है, पूरा stack trace उनके monitoring system (Sentry/Datadog) में log करता है engineers के investigate करने के लिए, लेकिन merchant को सिर्फ `{ error: { code: "SERVER_ERROR", description: "Something went wrong" } }` return करता है — कभी भी database hostnames या stack traces जैसी internal details expose नहीं करता, जो attacker को help कर सकती हैं या integrators को confuse कर सकती हैं।

---

## 💻 Code Example — Basic

```javascript
// error-handling-basic.js
const express = require('express');
const app = express();
app.use(express.json());

// ─── 1. CUSTOM ERROR CLASS ─────────────────────────────────────────────────────
class AppError extends Error {
  constructor(message, statusCode) {
    super(message); // sets this.message
    this.statusCode = statusCode;
    this.isOperational = true; // marks this as an EXPECTED error, not a bug
    Error.captureStackTrace(this, this.constructor); // clean stack trace
  }
}

// ─── 2. A ROUTE THAT THROWS A CUSTOM OPERATIONAL ERROR ────────────────────────
app.get('/user/:id', (req, res, next) => {
  const userId = req.params.id;
  if (!/^\d+$/.test(userId)) {
    // invalid ID format — an expected, client-caused error
    return next(new AppError('User ID must be numeric', 400));
  }
  res.json({ userId, name: 'Rahul' });
});

// ─── 3. CENTRALIZED ERROR-HANDLING MIDDLEWARE (4 params = error middleware) ───
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500; // default to 500 if not set
  const message = err.isOperational ? err.message : 'Something went wrong';

  console.error(err); // always log internally, regardless of operational status

  res.status(statusCode).json({ error: message });
});

app.listen(3000, () => console.log('Server on port 3000'));
```

## 💻 Code Example — Advanced

```javascript
// error-handling-advanced.js — catchAsync wrapper, process-level safety nets, 404 handler
const express = require('express');
const app = express();
app.use(express.json());

// ─── 1. ERROR CLASSES for different HTTP scenarios ────────────────────────────
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}
class NotFoundError extends AppError {
  constructor(resource = 'Resource') {
    super(`${resource} not found`, 404);
  }
}
class ValidationError extends AppError {
  constructor(message) {
    super(message, 400);
  }
}

// ─── 2. catchAsync — eliminates repetitive try/catch in every async route ────
const catchAsync = (fn) => (req, res, next) => {
  // Wraps the async function; if the returned promise rejects, forward to next(err)
  // WITHOUT this, an unhandled rejection inside an async Express handler
  // would NOT be caught by Express automatically (pre-Express 5 behavior)
  Promise.resolve(fn(req, res, next)).catch(next);
};

// ─── 3. ROUTES using catchAsync — no manual try/catch needed ──────────────────
app.get(
  '/orders/:id',
  catchAsync(async (req, res) => {
    const order = await Order.findById(req.params.id); // mock async DB call
    if (!order) throw new NotFoundError('Order'); // thrown error auto-caught by catchAsync
    res.json({ order });
  })
);

app.post(
  '/orders',
  catchAsync(async (req, res) => {
    const { amount } = req.body;
    if (!amount || amount <= 0) {
      throw new ValidationError('Amount must be a positive number');
    }
    const order = await Order.create({ amount }); // mock
    res.status(201).json({ order });
  })
);

// ─── 4. 404 HANDLER for unmatched routes (must come after all real routes) ───
app.all('*', (req, res, next) => {
  next(new NotFoundError(`Route ${req.originalUrl}`));
});

// ─── 5. CENTRALIZED ERROR MIDDLEWARE with environment-aware detail level ─────
app.use((err, req, res, next) => {
  err.statusCode = err.statusCode || 500;

  if (process.env.NODE_ENV === 'development') {
    // Dev: full details help debugging
    return res.status(err.statusCode).json({
      status: err.status || 'error',
      message: err.message,
      stack: err.stack,
    });
  }

  // Production: never leak internals for non-operational (unexpected/bug) errors
  if (err.isOperational) {
    return res.status(err.statusCode).json({ status: err.status, message: err.message });
  }

  console.error('UNEXPECTED ERROR 💥', err); // log for engineers (Sentry/Datadog in real setup)
  res.status(500).json({ status: 'error', message: 'Something went wrong' });
});

// ─── 6. PROCESS-LEVEL SAFETY NETS — last line of defense ─────────────────────
process.on('unhandledRejection', (reason) => {
  // A promise rejected with no .catch() anywhere in the app — log and exit gracefully
  console.error('UNHANDLED REJECTION! Shutting down...', reason);
  process.exit(1); // let a process manager (PM2/Kubernetes) restart the process cleanly
});

process.on('uncaughtException', (err) => {
  // A synchronous error thrown outside any try/catch — app is in an undefined state
  console.error('UNCAUGHT EXCEPTION! Shutting down...', err);
  process.exit(1);
});

app.listen(3000, () => console.log('Production-grade error handling server running on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();
app.use(express.json());

// Reusable catchAsync + error classes imported from a shared utils module
const catchAsync = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
  }
}

const router = express.Router();

router.post(
  '/login',
  catchAsync(async (req, res) => {
    const { email, password } = req.body;
    const user = await User.findOne({ email });
    if (!user) throw new AppError('Invalid credentials', 401); // operational, safe to show
    res.json({ message: 'Logged in' });
  })
);

app.use('/auth', router);

// Centralized handler applies to errors from ANY mounted router
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  const message = err.isOperational ? err.message : 'Internal server error';
  res.status(statusCode).json({ error: message });
});

app.listen(4000, () => console.log('Modular error-handled app running on port 4000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting that Express doesn't auto-catch errors thrown inside `async` route handlers (pre-Express 5)
✅ Correct: Wrap async handlers with a `catchAsync` utility, or use `try/catch` with explicit `next(err)` — otherwise a rejected promise becomes an unhandled rejection, potentially hanging the request or crashing the process.

```javascript
// Wrong — in Express 4.x, this rejected promise is NEVER caught by Express;
// the request hangs forever (no response sent) and the rejection is unhandled
app.get('/data', async (req, res) => {
  const data = await fetchData(); // if this rejects, nothing happens — no response, no error log
  res.json(data);
});

// Right — explicit try/catch forwards the error properly
app.get('/data', async (req, res, next) => {
  try {
    const data = await fetchData();
    res.json(data);
  } catch (err) {
    next(err); // Express now routes this to the error-handling middleware
  }
});
```

❌ Mistake 2: Leaking stack traces / internal error details to clients in production
✅ Correct: Only expose error details in development; in production, send a generic message for non-operational errors and log full details server-side only.

```javascript
// Wrong — always sends the raw error object, leaking stack traces/DB details in prod
app.use((err, req, res, next) => res.status(500).json({ error: err }));

// Right — environment-aware, operational-vs-bug distinction
app.use((err, req, res, next) => {
  if (process.env.NODE_ENV === 'production' && !err.isOperational) {
    return res.status(500).json({ error: 'Something went wrong' });
  }
  res.status(err.statusCode || 500).json({ error: err.message });
});
```

---

## 🧠 Tricky Interview Question

```javascript
const express = require('express');
const app = express();

app.get('/crash', (req, res) => {
  setTimeout(() => {
    throw new Error('Thrown inside setTimeout!'); // NOT inside the request-response cycle anymore
  }, 100);
  res.send('Request received');
});

app.use((err, req, res, next) => {
  res.status(500).json({ error: err.message }); // will this ever run for /crash?
});

app.listen(3000);
```
Does the error-handling middleware catch the error thrown inside `setTimeout`?

Answer: **No.** Express's error-handling middleware only catches errors that occur synchronously within a route handler, or that are explicitly passed via `next(err)`. An error thrown inside a `setTimeout` callback happens on a LATER tick of the event loop, completely outside of Express's request-handling call stack — by the time the timeout fires, Express has already finished processing and responding to the request ("Request received" was already sent). This throw becomes an **uncaught exception** at the process level, which (without a `process.on('uncaughtException')` handler) crashes the entire Node.js process. This demonstrates why asynchronous code running outside the direct request lifecycle (timers, event emitters, background jobs) needs its own explicit error handling — Express's middleware chain simply cannot catch it.

---

## ⚫ Interview Questions + Answers

Q1: How does Express recognize error-handling middleware differently from regular middleware?
A1: By the number of parameters in the middleware function signature — regular middleware/route handlers have `(req, res, next)` (3 params), while error-handling middleware has `(err, req, res, next)` (4 params, error FIRST). Express inspects the function's arity (`fn.length`) to decide whether to treat it as error-handling middleware. It's invoked only when `next(err)` is called somewhere earlier in the chain (passing a truthy first argument), skipping all regular middleware/routes in between and jumping straight to the next error-handling middleware.

Q2: What's the difference between "operational" and "programmer" errors, and why does the distinction matter?
A2: **Operational errors** are expected failure conditions that happen during normal operation — invalid user input, a resource not found, a failed payment due to insufficient funds, network timeout to a third-party service. These are "known unknowns" — anticipated, and should be communicated clearly to the client. **Programmer errors** are bugs — a `TypeError` from accessing a property on `undefined`, a typo, a logic error. These are unexpected and indicate the app is in an unknown/unsafe state. The distinction matters because operational errors get clean, specific client messages; programmer errors should be logged for developers and only a generic message shown to clients (to avoid leaking internals and because the exact state/cause is unknown).

Q3: Why might you want to crash and restart the process after an uncaught exception rather than trying to "recover" and keep running?
A3: An uncaught exception means the application is in an UNKNOWN state — some operation failed mid-way, possibly leaving shared state (in-memory caches, open connections, partially-written data) inconsistent. Continuing to serve requests from this corrupted state risks subtle, hard-to-debug cascading failures or data corruption. The safer practice is to log the error, gracefully close existing connections, and exit the process, relying on a process manager (PM2, Kubernetes, systemd) to restart it fresh — restoring to a known-good state.

Q4: How would you handle validation errors from a library like Joi or express-validator consistently with your custom error classes?
A4: Catch the library's validation error (often thrown or returned as a result object) in a middleware step, then wrap it into your own `AppError`/`ValidationError` class with a consistent `statusCode` (typically 400) and a clean, user-facing `message` (possibly aggregating multiple field errors into one response), then pass it to `next(err)` so it flows through the same centralized error-handling pipeline as every other error type — ensuring one consistent error response shape across the whole API regardless of error source.

Q5: What's the risk of NOT having a catch-all 404 handler before the error-handling middleware?
A5: Without an explicit `app.all('*', ...)` or similar catch-all route, requests to undefined routes fall through to Express's default behavior, which sends a generic, unstyled HTML 404 page (or in API contexts, an inconsistent response not matching your JSON error format). Adding an explicit catch-all that calls `next(new NotFoundError(...))` ensures 404s also go through your centralized error handler, returning a consistent JSON shape like every other error in your API.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production Express API — centralized error handling is considered a non-negotiable best practice
- APIs consumed by other services/clients that need consistent, parseable error response shapes
- Teams with multiple developers where consistent error conventions prevent each route from inventing its own error format

❌ Avoid when:
- There's no scenario where you'd skip this in a real app — even small apps benefit; the only "avoid" is over-engineering a tiny prototype/script with elaborate error class hierarchies when a simple try/catch suffices for a one-off script with no HTTP server involved

---

## 📊 Visual Diagram
```
EXPRESS ERROR HANDLING FLOW:

  Request ──▶ Route Handler (wrapped in catchAsync)
                     │
              throws/rejects with AppError
                     │
                     ▼
              next(err) called
                     │
         (skips all remaining normal middleware)
                     │
                     ▼
         Error-Handling Middleware (err, req, res, next)
                     │
          ┌──────────┴───────────┐
   isOperational=true      isOperational=false (bug)
          │                       │
   send clean message       log full stack internally
   + correct status code    send generic "Server Error"
          │                       │
          ▼                       ▼
        Client Response (consistent JSON shape either way)

PROCESS-LEVEL SAFETY NET (outside Express entirely):
  process.on('uncaughtException')   ◀── sync errors outside try/catch
  process.on('unhandledRejection')  ◀── promise rejections with no .catch()
       │
       ▼
  log + gracefully exit ──▶ process manager restarts app
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Operational Error | Expected, anticipated failure | Expected, anticipated failure |
| Programmer Error | Unexpected bug in code | Code का unexpected bug |
| catchAsync | Wrapper forwarding async errors to next() | Async errors को next() पर forward करने वाला wrapper |
| Centralized Error Middleware | Single place handling all errors | सभी errors handle करने वाली एक जगह |
| unhandledRejection | Promise rejected with no .catch() | बिना .catch() के reject हुई promise |
| uncaughtException | Sync error outside any try/catch | try/catch के बाहर का sync error |

---

## ⚡ 3-Line Summary
English:
1. Use custom error classes with `statusCode`/`isOperational`, and wrap async handlers (`catchAsync`) so rejected promises always reach Express's error middleware.
2. Centralize error handling in one 4-parameter `(err, req, res, next)` middleware, distinguishing operational errors (clean client message) from programmer errors (generic message, full internal logging).
3. Add process-level `uncaughtException`/`unhandledRejection` handlers as a final safety net, and gracefully exit to let a process manager restart cleanly.

Hindi:
1. Custom error classes use करो `statusCode`/`isOperational` के साथ, और async handlers को (`catchAsync`) wrap करो ताकि rejected promises हमेशा Express के error middleware तक पहुंचें।
2. Error handling को एक 4-parameter `(err, req, res, next)` middleware में centralize करो, operational errors (clean client message) को programmer errors (generic message, पूरा internal logging) से अलग करो।
3. Process-level `uncaughtException`/`unhandledRejection` handlers जोड़ो final safety net के रूप में, और gracefully exit करो ताकि process manager cleanly restart कर सके।

---

## ➡️ Next Topic
**116. Authentication vs Authorization** — Understanding the fundamental difference between "who you are" and "what you can do"।
