# 92. Middleware Chain
# हिंदी में: Middleware Chain

---

## 🔵 Simple Definition (English)
The **middleware chain** is the ordered sequence of middleware functions Express executes for a given request, one after another, each deciding to call `next()` (continue) or send a response (stop). It's the core execution model of Express — every request flows through this chain from top to bottom until something ends it.

## 🔵 सरल परिभाषा (Hindi)
**Middleware chain** एक ordered sequence है जिसमें Express किसी request के लिए middleware functions को एक के बाद एक चलाता है, हर एक `next()` call करे (continue) या response भेजे (stop) decide करता है। यह Express का core execution model है — हर request इस chain से top से bottom तक गुजरता है जब तक कुछ उसे खत्म न कर दे।

---

## 🔴 Problem it Solves
```
WITHOUT A CHAIN MODEL:
  Each concern (auth, logging, validation, business logic) would need
  to be manually composed inside every single handler — tightly coupled,
  impossible to reorder or reuse cleanly.

WITH A CHAIN MODEL:
  app.use(logger);        // Step 1
  app.use(auth);          // Step 2
  app.use(rateLimiter);   // Step 3
  app.get('/data', validate, handler);  // Step 4, 5

  Request flows: logger → auth → rateLimiter → validate → handler
  Each step is independent, reorderable, and reusable across routes.
  Any step can short-circuit the chain by sending a response.
```

## 🔴 यह क्यों बना? (Hindi)
बिना chain model के, हर concern (auth, logging, validation) को हर handler में manually compose करना पड़ता — tightly coupled code, reorder/reuse करना मुश्किल। Chain model ने हर concern को independent, reusable function बना दिया जो किसी भी order में compose हो सके, और जरूरत पड़ने पर chain को बीच में रोका भी जा सके।

---

## 🟢 How it Works — Step by Step

Step 1 → Express maintains an internal array/stack of all registered middleware and route handlers, in registration order
Step 2 → For each incoming request, Express starts at index 0 of this stack
Step 3 → It checks if the current layer's path+method matches the request; if yes, it invokes that function with `(req, res, next)`
Step 4 → If the function calls `next()`, Express moves to the NEXT matching layer in the stack; if it calls `next(err)`, Express skips to the nearest ERROR-HANDLING middleware
Step 5 → If a function sends a response (`res.send/json/end`) without calling `next()`, the chain stops there — no further layers run

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Express अपने अंदर एक array/stack रखता है सभी registered middleware और route handlers का, registration order में
Step 2 → हर incoming request के लिए Express इस stack के index 0 से शुरू करता है
Step 3 → यह check करता है कि current layer का path+method request से match करता है; अगर हाँ, तो उसे `(req, res, next)` के साथ invoke करता है
Step 4 → अगर function `next()` call करे, तो Express stack के अगले matching layer पर जाता है; अगर `next(err)` call करे, तो nearest ERROR-HANDLING middleware पर जाता है
Step 5 → अगर function response भेज दे (`res.send/json/end`) बिना `next()` call किए, chain वहीं रुक जाती है — आगे कोई layer नहीं चलता

---

## 🟡 Real World Example
**Razorpay payment API chain:** `requestId → helmet → cors → bodyParser → rateLimiter → authenticate → validatePaymentSchema → fraudCheck → paymentHandler → errorHandler`. Each layer is independent: fraud check can short-circuit with a 403 before reaching the actual payment handler; auth failure stops everything at step 6. This layered chain lets Razorpay's engineering teams own separate concerns (security team owns auth/fraud, platform team owns logging/rate-limiting) without touching business logic code.

## 🟡 Real Example Hindi mein
**Razorpay payment API chain:** `requestId → helmet → cors → bodyParser → rateLimiter → authenticate → validatePaymentSchema → fraudCheck → paymentHandler → errorHandler`। हर layer independent है: fraud check payment handler तक पहुँचने से पहले 403 से chain रोक सकता है; auth fail होने पर step 6 पर सब रुक जाता है। यह layered chain अलग teams को अलग concerns own करने देता है बिना business logic touch किए।

---

## 💻 Code Example — Basic

```javascript
// middleware-chain-basic.js
const express = require('express');
const app = express();

// Each middleware logs its name and calls next() to continue the chain
app.use((req, res, next) => {
  console.log('1: Logger');
  next();   // continue to next layer
});

app.use((req, res, next) => {
  console.log('2: Auth check');
  const isAuthed = true;  // pretend check
  if (!isAuthed) {
    return res.status(401).json({ error: 'Unauthorized' });  // chain stops here if false
  }
  next();
});

app.use((req, res, next) => {
  console.log('3: Attach user data');
  req.user = { id: 1, name: 'Rahul' };  // enrich req for downstream handlers
  next();
});

// Final route handler — end of the chain for this request
app.get('/profile', (req, res) => {
  console.log('4: Route handler');
  res.json({ user: req.user });
});
// Console output for GET /profile: 1: Logger → 2: Auth check → 3: Attach user data → 4: Route handler

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// middleware-chain-advanced.js — branching chains, error propagation, chain visualization

const express = require('express');
const app = express();
app.use(express.json());

// Chain segment 1: applies to ALL routes
app.use((req, res, next) => {
  req.chainLog = [];               // track which middleware ran, for debugging
  req.chainLog.push('global-1');
  next();
});

// Chain segment 2: path-scoped — only runs for /api/* routes
app.use('/api', (req, res, next) => {
  req.chainLog.push('api-scoped');
  next();
});

// Chain segment 3: async middleware with error propagation
app.use('/api', async (req, res, next) => {
  try {
    req.chainLog.push('async-check');
    const isValid = await simulateAsyncCheck();   // e.g., check DB/cache
    if (!isValid) {
      return res.status(403).json({ error: 'Forbidden', chainLog: req.chainLog });
    }
    next();
  } catch (err) {
    next(err);   // IMPORTANT: async errors must be passed to next(err) manually
  }
});

async function simulateAsyncCheck() {
  return true;   // pretend async check passes
}

// Route-specific chain: array of middleware + final handler
const checkRole = (role) => (req, res, next) => {
  req.chainLog.push(`role-check:${role}`);
  next();
};

app.get('/api/admin/stats', [checkRole('admin')], (req, res) => {
  req.chainLog.push('handler');
  res.json({ chainLog: req.chainLog });
  // Full chain for this route: global-1 → api-scoped → async-check → role-check:admin → handler
});

// Error-handling middleware — only reached via next(err)
app.use((err, req, res, next) => {
  console.error('Chain error:', err.message);
  res.status(500).json({ error: err.message, chainLog: req.chainLog });
});

app.listen(3000);
```

---

## 🟠 Express.js Integration

```javascript
// Visualizing a production middleware chain end-to-end
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const morgan = require('morgan');
const app = express();

app.use(helmet());                       // 1. security headers
app.use(cors());                         // 2. CORS check
app.use(morgan('combined'));             // 3. logging
app.use(express.json());                 // 4. body parsing
app.use('/api', apiRateLimiter);         // 5. rate limiting (scoped to /api)
app.use('/api', authenticate);           // 6. auth (scoped to /api)

app.use('/api/orders', require('./routes/orders'));   // 7. feature router (its own sub-chain)

app.use((req, res) => res.status(404).json({ error: 'Not found' }));   // 8. 404 fallback
app.use((err, req, res, next) => res.status(500).json({ error: err.message }));  // 9. error handler

function apiRateLimiter(req, res, next) { next(); }
function authenticate(req, res, next) { next(); }

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Throwing inside async middleware without catching it
```javascript
// WRONG: throw inside an async middleware is NOT caught by Express automatically
app.use(async (req, res, next) => {
  const data = await fetchData();  // if this throws, request HANGS (unhandled rejection)
  next();
});

// CORRECT: wrap in try/catch and call next(err)
app.use(async (req, res, next) => {
  try {
    const data = await fetchData();
    next();
  } catch (err) {
    next(err);  // propagates to error-handling middleware
  }
});
```

❌ **Mistake 2:** Registering error-handling middleware too early
```javascript
// WRONG: error handler placed before routes never catches their errors
app.use((err, req, res, next) => res.status(500).json({ error: err.message }));
app.get('/data', (req, res, next) => next(new Error('Oops')));  // never reaches handler above!

// CORRECT: error handler must be registered LAST, after all routes
app.get('/data', (req, res, next) => next(new Error('Oops')));
app.use((err, req, res, next) => res.status(500).json({ error: err.message }));
```

---

## 🧠 Tricky Interview Question

```javascript
app.use((req, res, next) => {
  console.log('A');
  next();
  console.log('B');   // what happens with this line?
});

app.get('/', (req, res) => {
  console.log('C');
  res.send('done');
});
```
Answer: Output is `A`, `C`, `B` — in that order. Calling `next()` does NOT return control back synchronously after the rest of the chain finishes; it SYNCHRONOUSLY invokes the next middleware immediately (like a direct function call), and only after that entire call stack unwinds does execution resume after the `next()` line. So `next()` runs the whole rest of the chain (which logs `C`) BEFORE returning to log `B`. This confuses developers who expect `next()` to behave like an async "continue" — it's actually a synchronous function call under the hood (unless wrapped in something async).

---

## ⚫ Interview Questions + Answers

Q1: What determines when a middleware chain stops executing?
A1: The chain stops when: (1) a middleware sends a terminal response (`res.send/json/end/redirect`) without calling `next()`, or (2) no further matching layers exist in the stack, falling through to Express's default 404 handler. Calling `next()` continues the chain; calling `next(err)` skips to the nearest error-handling middleware instead of the next regular one.

Q2: What happens if a middleware neither calls `next()` nor sends a response?
A2: The request hangs indefinitely — the client's connection stays open until it times out. This is one of the most common Express bugs for beginners. Every middleware MUST either call `next()` or terminate the response.

Q3: How does `next(err)` differ from just calling `next()`?
A3: `next()` with no argument moves to the next REGULAR middleware/route in the stack. `next(err)` (passing any truthy value, conventionally an Error) tells Express to SKIP all remaining regular middleware/routes and jump directly to the nearest error-handling middleware (the one with 4 parameters: `(err, req, res, next)`).

Q4: Why do async middleware functions need explicit try/catch + next(err), unlike sync ones?
A4: Express's error handling was designed before `async/await` existed — it only catches SYNCHRONOUS throws automatically within a middleware function. If an `async` function throws (i.e., its returned Promise rejects), Express has no built-in mechanism to catch that rejection, so the error is silently swallowed and the request hangs. You must manually catch and call `next(err)`, or use a wrapper utility/package like `express-async-errors` that patches this behavior.

Q5: Can the SAME middleware function run multiple times for one request?
A5: Yes, if it's registered in multiple places in the stack that both match the request (e.g., once globally via `app.use(logger)` and once again inside `router.use(logger)` for a sub-router that's also hit). Each registration is a separate "layer" Express checks independently — it doesn't deduplicate functions, so re-registering the same function runs it again.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Composing cross-cutting concerns (auth, logging, validation) that should apply consistently across many routes
- You want to reorder or reuse pieces of request-handling logic independently

❌ Avoid when:
- A single simple handler would be clearer than splitting trivial logic into multiple chained middleware (over-engineering for a one-route app)
- Business logic that's inherently sequential/stateful might be clearer as a single async function rather than fragmented across many `next()` hops

---

## 📊 Visual Diagram
```
  MIDDLEWARE CHAIN EXECUTION (stack-like, synchronous calls)
  ────────────────────────────────────────────────────────
  Request arrives
       │
       ▼
  [Layer 0] logger         → next() ──┐
                                        │
       ┌────────────────────────────────┘
       ▼
  [Layer 1] auth           → fail? res.status(401) [CHAIN STOPS]
                            → pass? next() ──┐
                                               │
       ┌─────────────────────────────────────┘
       ▼
  [Layer 2] validate        → next(err) on fail ──┐  (skips to error handler)
                             → next() on pass  ────┼──┐
                                                     │  │
       ┌─────────────────────────────────────────────┘  │
       ▼                                                  │
  [Layer 3] route handler  → res.json(...) [CHAIN ENDS]   │
                                                             │
       ┌─────────────────────────────────────────────────┘
       ▼
  [Error Layer] errorHandler(err, req, res, next)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chain | Ordered sequence of middleware/handlers | Middleware/handlers की ordered sequence |
| `next()` | Continue to next layer | अगले layer पर जाओ |
| `next(err)` | Jump to error handler | Error handler पर जाओ |
| Short-circuit | Stop chain early with a response | Response भेजकर chain रोकना |
| Layer | One middleware/route registered in the stack | Stack में registered एक middleware/route |

---

## ⚡ 3-Line Summary
English: 1. The middleware chain is an ordered stack of functions Express walks for every request, continuing via `next()` or stopping via a sent response. 2. `next(err)` jumps straight to error-handling middleware, skipping regular layers. 3. Async middleware must manually catch errors and call `next(err)` — Express doesn't auto-catch rejected promises.
Hindi: 1. Middleware chain functions का ordered stack है जिससे हर request गुजरता है, `next()` से continue या response से stop होता है। 2. `next(err)` सीधे error-handling middleware पर जाता है। 3. Async middleware में errors manually catch करके `next(err)` call करना पड़ता है।

---

## ➡️ Next Topic
**93. Built-in Middleware** — Express's own middleware functions like `express.json()`, `express.static()`, `express.urlencoded()`.
