# 96. Error Handling Middleware
# हिंदी में: Error Handling Middleware

---

## 🔵 Simple Definition (English)
**Error-handling middleware** is a special Express middleware with FOUR parameters: `(err, req, res, next)`. Express identifies it by this exact arity and routes all errors (via `next(err)` or synchronous throws) to it, instead of regular middleware. It's where you centralize error formatting, logging, and status-code decisions for the entire app.

## 🔵 सरल परिभाषा (Hindi)
**Error-handling middleware** एक special Express middleware है जिसमें चार parameters होते हैं: `(err, req, res, next)`। Express इसे इस exact arity से identify करता है और सभी errors (जो `next(err)` से या synchronous throw से आएं) इसी पर route करता है। यह पूरे app के लिए centralized error formatting, logging, और status-code decisions की जगह है।

---

## 🔴 Problem it Solves
```
WITHOUT CENTRALIZED ERROR HANDLING:
  app.get('/users/:id', (req, res) => {
    try {
      const user = findUser(req.params.id);
      if (!user) return res.status(404).json({ error: 'Not found' });
      res.json(user);
    } catch (err) {
      res.status(500).json({ error: err.message });  // repeated in EVERY handler
    }
  });
  app.post('/orders', (req, res) => {
    try { ... } catch (err) {
      res.status(500).json({ error: err.message });  // same boilerplate again!
    }
  });

WITH CENTRALIZED ERROR MIDDLEWARE:
  app.get('/users/:id', (req, res, next) => {
    try {
      const user = findUser(req.params.id);
      if (!user) throw new AppError('Not found', 404);
      res.json(user);
    } catch (err) { next(err); }   // delegate to ONE central handler
  });

  app.use((err, req, res, next) => {    // ONE place for all error formatting
    res.status(err.statusCode || 500).json({ error: err.message });
  });
```

## 🔴 यह क्यों बना? (Hindi)
बिना centralized error handling के, हर route handler में try/catch और error-response formatting repeat होता था — inconsistent error formats, duplicate code। Express ने 4-parameter middleware को special बनाकर एक central जगह दी जहाँ सारे errors consistently handle, log, और format हो सकें।

---

## 🟢 How it Works — Step by Step

Step 1 → Express inspects a middleware function's parameter count (via `.length`) when registering it with `app.use()`
Step 2 → If it has exactly 4 params `(err, req, res, next)`, Express marks it as an ERROR-HANDLING middleware internally
Step 3 → Regular middleware/routes only run when `next()` is called with NO argument; if `next(err)` is called (or a sync throw occurs inside a route handler), Express SKIPS all remaining regular middleware and jumps to the nearest error-handling middleware
Step 4 → You can have MULTIPLE error-handling middleware (e.g., one for logging, one for formatting) — call `next(err)` again from inside one to pass to the next
Step 5 → Error-handling middleware MUST be registered LAST, after all routes, since Express walks the stack top-to-bottom to find them

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Express middleware function के parameter count (`.length` से) को check करता है जब उसे `app.use()` से register करते हैं
Step 2 → अगर exactly 4 params `(err, req, res, next)` हों, तो Express उसे ERROR-HANDLING middleware मानता है
Step 3 → Regular middleware/routes सिर्फ तब चलते हैं जब `next()` बिना argument call हो; `next(err)` call होने पर (या sync throw) Express बाकी regular middleware skip करके nearest error-handling middleware पर जाता है
Step 4 → कई error-handling middleware हो सकते हैं — एक से दूसरे में `next(err)` से pass कर सकते हैं
Step 5 → Error-handling middleware हमेशा LAST register होना चाहिए, सभी routes के बाद

---

## 🟡 Real World Example
**Razorpay API error handling:** A custom `AppError` class distinguishes "operational errors" (expected, like invalid card number — safe to show the message) from "programming errors" (bugs — never expose internals). The central error middleware checks `err.isOperational`: if true, sends `err.message` with the right status code; if false, logs the full stack trace internally and sends a generic "Something went wrong" to avoid leaking implementation details to API consumers.

## 🟡 Real Example Hindi mein
**Razorpay API error handling:** एक custom `AppError` class "operational errors" (expected, जैसे invalid card number) को "programming errors" (bugs) से अलग करता है। Central error middleware `err.isOperational` check करता है: true हो तो `err.message` सही status code के साथ भेजता है; false हो तो पूरा stack trace internally log करता है और generic "Something went wrong" भेजता है ताकि implementation details leak न हों।

---

## 💻 Code Example — Basic

```javascript
// error-handling-basic.js
const express = require('express');
const app = express();
app.use(express.json());

app.get('/users/:id', (req, res, next) => {
  const user = req.params.id === '1' ? { id: 1, name: 'Rahul' } : null;

  if (!user) {
    const err = new Error('User not found');
    err.statusCode = 404;
    return next(err);   // pass error to error-handling middleware
  }
  res.json(user);
});

// Synchronous throws are AUTO-caught by Express and routed to error middleware
app.get('/crash', (req, res) => {
  throw new Error('Something broke synchronously');  // Express catches this automatically
});

// ERROR-HANDLING MIDDLEWARE — must have exactly 4 params, registered LAST
app.use((err, req, res, next) => {
  console.error('Error caught:', err.message);
  const statusCode = err.statusCode || 500;
  res.status(statusCode).json({ error: err.message });
});

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// error-handling-advanced.js — custom error classes, operational vs programming errors

const express = require('express');
const app = express();
app.use(express.json());

// Custom error class distinguishing operational (expected) errors
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;   // flag: this is an EXPECTED error, safe to expose
    Error.captureStackTrace(this, this.constructor);
  }
}

class NotFoundError extends AppError {
  constructor(resource) {
    super(`${resource} not found`, 404);
  }
}

class ValidationError extends AppError {
  constructor(details) {
    super('Validation failed', 400);
    this.details = details;
  }
}

// Async route wrapper — eliminates repetitive try/catch in every async handler
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);  // catches rejected promises → next(err)
};

app.get('/api/orders/:id', asyncHandler(async (req, res) => {
  const order = await findOrder(req.params.id);   // if this rejects, asyncHandler catches it
  if (!order) throw new NotFoundError('Order');     // thrown inside async still caught by wrapper
  res.json(order);
}));

async function findOrder(id) {
  if (id === '404') return null;
  return { id, total: 599 };
}

app.post('/api/orders', (req, res, next) => {
  const { items } = req.body;
  if (!items || items.length === 0) {
    return next(new ValidationError(['items array is required and cannot be empty']));
  }
  res.status(201).json({ created: true });
});

// CENTRALIZED ERROR MIDDLEWARE — handles all error types consistently
app.use((err, req, res, next) => {
  // Known/expected errors — safe to expose message
  if (err.isOperational) {
    return res.status(err.statusCode).json({
      error: err.message,
      ...(err.details && { details: err.details }),
    });
  }

  // Specific third-party error types (e.g., from Mongoose, JWT libs)
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({ error: 'Invalid token' });
  }

  // Unknown/programming errors — log fully, hide details from client
  console.error('UNEXPECTED ERROR:', err);
  res.status(500).json({ error: 'Internal Server Error' });
});

app.listen(3000, () => console.log('Server on 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// Production error-handling setup for a full Express app
const express = require('express');
const app = express();
app.use(express.json());

app.use('/api/users', require('./routes/users'));
app.use('/api/orders', require('./routes/orders'));

// 404 handler for unmatched routes — runs BEFORE error handler, AFTER all routes
app.use((req, res, next) => {
  const err = new Error(`Cannot ${req.method} ${req.originalUrl}`);
  err.statusCode = 404;
  next(err);
});

// Centralized error-handling middleware — always LAST
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  const isProd = process.env.NODE_ENV === 'production';

  res.status(statusCode).json({
    error: err.message,
    ...(!isProd && { stack: err.stack }),   // only show stack trace outside production
  });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Error-handling middleware with the wrong parameter count
```javascript
// WRONG: 3 params — Express treats this as REGULAR middleware, never invoked for errors
app.use((err, res, next) => {
  res.status(500).json({ error: err.message });
});

// CORRECT: exactly 4 params required
app.use((err, req, res, next) => {
  res.status(500).json({ error: err.message });
});
```

❌ **Mistake 2:** Not catching async errors, causing the error handler to never run
```javascript
// WRONG: async route handler that throws is NOT automatically caught by Express
app.get('/data', async (req, res) => {
  const data = await fetchData();  // if this rejects, request hangs — no error handler triggered
  res.json(data);
});

// CORRECT: wrap with try/catch + next(err), or use an asyncHandler utility
app.get('/data', async (req, res, next) => {
  try {
    const data = await fetchData();
    res.json(data);
  } catch (err) {
    next(err);
  }
});
```

---

## 🧠 Tricky Interview Question

```javascript
app.use((err, req, res, next) => {
  console.log('Handler 1');
  next(err);   // passes the error FORWARD
});

app.use((err, req, res, next) => {
  console.log('Handler 2');
  res.status(500).json({ error: err.message });
});

// Request causes an error — what logs, and why have TWO error handlers?
```
Answer: Both `Handler 1` and `Handler 2` log, in that order. Express supports CHAINING multiple error-handling middleware — calling `next(err)` from WITHIN an error handler passes the error to the NEXT error-handling middleware in the stack (not back to regular middleware). This pattern is used to separate concerns: e.g., Handler 1 could be dedicated to LOGGING the error (to Sentry/Datadog) and then forwarding it, while Handler 2 is dedicated to FORMATTING the client-facing response. This keeps logging and response-formatting logic decoupled.

---

## ⚫ Interview Questions + Answers

Q1: How does Express distinguish error-handling middleware from regular middleware?
A1: By counting the function's declared parameters — Express checks `fn.length`. A function with exactly 4 parameters `(err, req, res, next)` is treated as an error handler; one with 2-3 parameters `(req, res, next)` is treated as regular middleware. This is a plain JavaScript function-arity check, not a special flag or decorator.

Q2: Does Express automatically catch errors thrown inside `async` route handlers?
A2: No. Express's built-in automatic error catching only works for SYNCHRONOUS throws inside regular (non-async) middleware/route handlers. For `async` functions, a thrown error becomes a REJECTED PROMISE, which Express (as of v4) does not automatically inspect. You must explicitly catch it (try/catch + `next(err)`) or use a wrapper utility (`asyncHandler`) or the `express-async-errors` package which monkey-patches Express to handle this automatically.

Q3: Where must error-handling middleware be registered relative to routes, and why?
A3: It must be registered AFTER all routes and regular middleware, because Express walks its middleware stack top-to-bottom. If the error handler were registered FIRST, no subsequent route's errors would ever reach it (since Express is already past that point in the stack when the error occurs later). It should typically be the LAST `app.use()` call in your file/app setup.

Q4: How do you differentiate "operational" errors (expected, like bad input) from "programming" errors (bugs) in your error handler?
A4: Common pattern: create a custom `AppError` class that extends `Error` and sets a flag like `this.isOperational = true`. In the central error-handling middleware, check `if (err.isOperational)` — if true, it's safe to expose `err.message` to the client with the appropriate status code. If false (meaning it's an unexpected bug, e.g., a `TypeError` from a coding mistake), log the full error internally (for debugging) but return a GENERIC message to the client to avoid leaking implementation details or stack traces.

Q5: Can you have multiple error-handling middleware functions, and what's a practical use case?
A5: Yes. Each error-handling middleware can call `next(err)` to forward the error to the NEXT error-handling middleware in the stack, similar to how regular middleware chains. A practical use: one early error handler logs the error to an external service (Sentry/Datadog) and calls `next(err)`; a later one is purely responsible for shaping the JSON response sent to the client. This separates "observability" concerns from "response formatting" concerns.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Centralizing error response formatting and logging across your entire Express app
- Distinguishing between known/expected errors (400s, 404s) and unexpected bugs (500s)

❌ Avoid when:
- A route handler needs a highly specific, one-off error response that doesn't fit the general pattern — handle it directly in the route instead of over-engineering the central handler with many special cases
- Never: skipping error handling entirely in production — always have at least one catch-all error middleware

---

## 📊 Visual Diagram
```
  ERROR PROPAGATION PATH
  ─────────────────────────────────────────
  Route handler throws / calls next(err)
       │
       ▼
  Express SKIPS all remaining regular middleware/routes
       │
       ▼
  Finds nearest middleware with 4 params (err, req, res, next)
       │
       ▼
  ┌─────────────────────────────┐
  │ Error Handler 1 (logging)    │ → next(err) forwards further
  └──────────────┬────────────────┘
                 ▼
  ┌─────────────────────────────┐
  │ Error Handler 2 (formatting) │ → res.status(x).json({...})  [ENDS HERE]
  └─────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Error middleware | 4-param `(err,req,res,next)` handler | 4-param error handler |
| `next(err)` | Forwards error, skips regular middleware | Error forward करता है, regular middleware skip |
| Operational error | Expected error, safe to expose | Expected error, expose करना safe |
| Programming error | Unexpected bug, hide details | Unexpected bug, details hide करो |
| `asyncHandler` | Wrapper to catch async rejections | Async rejections catch करने वाला wrapper |

---

## ⚡ 3-Line Summary
English: 1. Error-handling middleware has exactly 4 params `(err, req, res, next)` and must be registered last. 2. Async errors are NOT auto-caught by Express — wrap with try/catch + `next(err)` or an `asyncHandler` utility. 3. Distinguish operational errors (safe to expose) from programming errors (log internally, hide from client) using a custom error class.
Hindi: 1. Error-handling middleware में exactly 4 params होते हैं और इसे last register करना होता है। 2. Async errors auto-catch नहीं होते — try/catch + `next(err)` या `asyncHandler` use करो। 3. Operational errors (expose safe) और programming errors (internally log, client से hide) को custom error class से अलग करो।

---

## ➡️ Next Topic
**97. express.json() + express.urlencoded()** — Deep dive into body-parsing middleware configuration options.
