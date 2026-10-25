# 179. Error Response Format Standard
# हिंदी में: Error Response Format Standard — Consistent Error Structure

---

## 🔵 Simple Definition (English)
An **error response format standard** is a fixed JSON shape used for EVERY error response across an API — e.g., `{ success: false, error: { code, message, details } }` — so clients can reliably detect failures, show meaningful messages, and programmatically react to specific error types, instead of parsing inconsistent ad-hoc error shapes per endpoint.

## 🔵 सरल परिभाषा (Hindi)
**Error response format standard** API में हर error response के लिए एक fixed JSON shape है — जैसे `{ success: false, error: { code, message, details } }` — ताकि clients reliably failures detect कर सकें, meaningful messages दिखा सकें, और specific error types पर programmatically react कर सकें, ना कि हर endpoint का अलग-अलग ad-hoc error shape parse करें।

---

## 🔴 Problem it Solves
Without a standard, errors come back inconsistently:
```
Endpoint A: { error: "User not found" }               (string)
Endpoint B: { message: "Validation failed", fields: [...] }  (different key name)
Endpoint C: "Internal Server Error"                     (plain text, not even JSON!)
Endpoint D: { errors: [{ msg: "..." }] }                 (array shape)
```
Client code can't write ONE generic error handler — it has to special-case parsing for every endpoint, making it easy to miss errors (silently treating a malformed error response as "no error") or show broken/blank error messages to users. A standard error shape fixes this by making error-handling code reusable and reliable everywhere.

## 🔴 यह क्यों बना? (Hindi)
Standard के बिना, errors inconsistently आते हैं:
```
Endpoint A: { error: "User not found" }               (string)
Endpoint B: { message: "Validation failed", fields: [...] }  (अलग key name)
Endpoint C: "Internal Server Error"                     (plain text, JSON भी नहीं!)
Endpoint D: { errors: [{ msg: "..." }] }                 (array shape)
```
Client code ONE generic error handler नहीं लिख सकता — हर endpoint के लिए special-case parsing करनी पड़ती है, जिससे errors miss होना आसान हो जाता है (malformed error response को silently "no error" मान लेना) या broken/blank error messages users को दिखना। Standard error shape इसे fix करता है error-handling code को reusable और reliable बनाकर।

---

## 🟢 How it Works — Step by Step

Step 1 → Define ONE error envelope: `{ success: false, error: { code: 'VALIDATION_ERROR', message: 'human readable message', details?: [...] } }`.
Step 2 → `code` is a machine-readable, stable string (e.g., `USER_NOT_FOUND`, `DUPLICATE_EMAIL`) that clients can `switch` on programmatically — never changes across languages/locales, unlike `message`.
Step 3 → `message` is human-readable, suitable for displaying to a user (or logging), can be localized.
Step 4 → `details` (optional) holds structured extra info, like a list of field-level validation errors: `[{ field: 'email', issue: 'already in use' }]`.
Step 5 → Implement this centrally in an Express error-handling middleware (registered last, with 4 args) so EVERY thrown/forwarded error gets converted to this shape automatically.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → ONE error envelope define करो: `{ success: false, error: { code: 'VALIDATION_ERROR', message: 'human readable message', details?: [...] } }`।
Step 2 → `code` एक machine-readable, stable string है (जैसे `USER_NOT_FOUND`, `DUPLICATE_EMAIL`) जिस पर clients programmatically `switch` कर सकते हैं — languages/locales में कभी नहीं बदलता, `message` के विपरीत।
Step 3 → `message` human-readable है, user को दिखाने (या logging) के लिए suitable, localize हो सकता है।
Step 4 → `details` (optional) structured extra info रखता है, जैसे field-level validation errors की list: `[{ field: 'email', issue: 'already in use' }]`।
Step 5 → इसे centrally Express error-handling middleware में implement करो (सबसे आखिर में register, 4 args के साथ) ताकि हर thrown/forwarded error automatically इस shape में convert हो।

---

## 🟡 Real World Example
**Razorpay's and Stripe's APIs** both return errors with a stable `code` field (e.g., Stripe's `card_declined`, Razorpay's `BAD_REQUEST_ERROR`) PLUS a human message. This lets merchant integrations programmatically handle specific failure cases — e.g., "if code is `card_declined`, show 'try another card'; if code is `insufficient_funds`, show 'add money to wallet'" — without fragile string-matching on the human-readable message (which might get reworded, breaking client logic that string-matched on it).

## 🟡 Real Example Hindi mein
**Razorpay और Stripe के APIs** errors को stable `code` field (जैसे Stripe का `card_declined`, Razorpay का `BAD_REQUEST_ERROR`) PLUS human message के साथ return करते हैं। यह merchant integrations को specific failure cases पर programmatically react करने देता है — जैसे "अगर code `card_declined` है, तो 'try another card' दिखाओ; अगर `insufficient_funds` है, तो 'wallet में पैसे जोड़ो' दिखाओ" — बिना fragile string-matching किये human-readable message पर (जो reword होने पर client logic तोड़ सकता है)।

---

## 💻 Code Example — Basic

```javascript
// basic-error-format.js
// Install: npm install express

const express = require('express');
const app = express();
app.use(express.json());

// Helper to send a consistently shaped error response
function sendError(res, statusCode, code, message, details = undefined) {
  const body = { success: false, error: { code, message } };
  if (details) body.error.details = details;
  res.status(statusCode).json(body);
}

app.get('/users/:id', (req, res) => {
  const user = null; // pretend lookup failed
  if (!user) {
    return sendError(res, 404, 'USER_NOT_FOUND', 'No user exists with this ID');
  }
  res.json({ success: true, data: user });
});

app.post('/signup', (req, res) => {
  const { email, age } = req.body;
  const details = [];
  if (!email) details.push({ field: 'email', issue: 'required' });
  if (age && age < 18) details.push({ field: 'age', issue: 'must be at least 18' });

  if (details.length) {
    return sendError(res, 400, 'VALIDATION_ERROR', 'Invalid signup data', details);
  }
  res.status(201).json({ success: true, data: { email, age } });
});

app.listen(3000);
```

## 💻 Code Example — Advanced

```javascript
// advanced-error-format.js — custom error classes + centralized error middleware

class AppError extends Error {
  constructor(code, message, statusCode, details = undefined) {
    super(message);
    this.code = code;             // machine-readable, stable identifier
    this.statusCode = statusCode; // HTTP status to respond with
    this.details = details;       // optional structured extra info
    this.isOperational = true;    // known/expected error type
    Error.captureStackTrace(this, this.constructor);
  }
}

// Specific, reusable error subclasses for common cases across the app
class NotFoundError extends AppError {
  constructor(resource = 'Resource') {
    super('NOT_FOUND', `${resource} not found`, 404);
  }
}
class ValidationError extends AppError {
  constructor(details) {
    super('VALIDATION_ERROR', 'One or more fields are invalid', 400, details);
  }
}
class ConflictError extends AppError {
  constructor(message) {
    super('CONFLICT', message, 409);
  }
}

// Centralized Express error-handling middleware -- MUST be registered last, with 4 params
function errorHandler(err, req, res, next) {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      success: false,
      error: { code: err.code, message: err.message, ...(err.details ? { details: err.details } : {}) },
    });
  }

  // Unknown/unexpected error -- log fully server-side, never leak internals to the client
  console.error('UNEXPECTED ERROR:', err);
  res.status(500).json({
    success: false,
    error: { code: 'INTERNAL_ERROR', message: 'Something went wrong. Please try again later.' },
  });
}

module.exports = { AppError, NotFoundError, ValidationError, ConflictError, errorHandler };
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { NotFoundError, ValidationError, errorHandler } = require('./advanced-error-format');
const User = require('./models/User');

const app = express();
app.use(express.json());

app.get('/users/:id', async (req, res, next) => {
  try {
    const user = await User.findById(req.params.id);
    if (!user) throw new NotFoundError('User'); // consistent, reusable error type
    res.json({ success: true, data: user });
  } catch (err) {
    next(err); // forward to centralized handler
  }
});

app.post('/users', async (req, res, next) => {
  try {
    if (!req.body.email) {
      throw new ValidationError([{ field: 'email', issue: 'required' }]);
    }
    const user = await User.create(req.body);
    res.status(201).json({ success: true, data: user });
  } catch (err) {
    next(err);
  }
});

app.use(errorHandler); // registered LAST -- catches everything forwarded via next(err)
app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using only human-readable messages for clients to detect error types (string matching)
✅ Correct: Always include a stable `code` field — messages can change wording/localization without breaking client logic.

```javascript
// Wrong -- client has to string-match on message text (fragile, breaks on wording changes)
if (error.message === 'User not found') { ... }

// Right -- stable machine-readable code
if (error.code === 'USER_NOT_FOUND') { ... }
```

❌ Mistake 2: Leaking stack traces or internal error details to the client in production
✅ Correct: Log full details server-side; send only safe, generic info to the client for unexpected errors.

```javascript
// Wrong
res.status(500).json({ error: err.stack }); // exposes file paths, internals, security risk

// Right
console.error(err); // full details logged server-side
res.status(500).json({ success: false, error: { code: 'INTERNAL_ERROR', message: 'Something went wrong' } });
```

---

## 🧠 Tricky Interview Question

```javascript
// A validation error occurs on TWO fields at once (email missing AND age invalid).
// Should the API return only the FIRST error found, or ALL errors at once?
```
Answer: Best practice is to return **ALL validation errors at once** (in the `details` array), not just the first one encountered. If the API only reports the first error, the client fixes it, resubmits, and then discovers the SECOND error — a frustrating "whack-a-mole" UX requiring multiple round trips. Collecting and returning all violations in one response (as validation libraries like Joi/Zod/express-validator do by default or with configuration) lets the client show/fix everything in one pass.

---

## ⚫ Interview Questions + Answers

Q1: Why use a `code` field separate from the HTTP status code?
A1: HTTP status codes are coarse-grained (e.g., `400` covers MANY different validation failures). A `code` field like `EMAIL_ALREADY_EXISTS` vs `INVALID_PHONE_FORMAT` lets clients distinguish between different `400`-class errors programmatically and show the exact right message/action, which the status code alone can't convey.

Q2: Should error codes be strings (`"USER_NOT_FOUND"`) or numbers (`4001`)?
A2: Strings are generally preferred — they're self-documenting (readable in logs, networking tools, docs without a lookup table), less likely to collide/need central registry management, and easier for new developers to understand at a glance. Numeric codes are more common in older/legacy systems or where extreme payload size matters (rare for JSON APIs).

Q3: How do you avoid leaking sensitive information in error messages while still being helpful?
A3: Distinguish operational (expected, safe-to-share) errors from programming (unexpected, unsafe) errors. For operational errors (validation, not found, duplicate), the message can be specific and helpful since it doesn't reveal internals. For unexpected/programming errors (DB connection failure, null pointer bugs), always return a generic message ("Something went wrong") to the client while logging the FULL detailed error (stack trace, query, etc.) server-side only.

Q4: How should a 422 Unprocessable Entity differ from a 400 Bad Request in error response design?
A4: `400` typically means the request itself is malformed (bad JSON, missing required param). `422` means the request is well-formed syntactically but fails semantic/business validation (e.g., valid JSON, but `age: -5` is semantically invalid). Many APIs use 400 for both to keep things simple, but strict REST design distinguishes them — the error response SHAPE stays the same either way; only the status code and specific `code`/`details` differ.

Q5: How do you handle errors from a downstream service (e.g., a third-party payment gateway timeout) in your error format?
A5: Wrap/translate the downstream error into YOUR OWN standard shape rather than passing through the third party's raw error format — e.g., catch the payment gateway's specific error, map it to `{ code: 'PAYMENT_GATEWAY_TIMEOUT', message: 'Payment processing timed out, please retry', statusCode: 503 }`. This keeps your API's error contract consistent regardless of which downstream service failed, and avoids leaking third-party implementation details to your clients.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production API — error handling consistency is non-negotiable for good client DX (developer experience).
- Multi-client systems (web, mobile, partner integrations) that all need reliable error parsing.

❌ Avoid when:
- There is no realistic scenario where this isn't needed in a serious API — the only variation is how elaborate the `details`/`code` taxonomy needs to be.

---

## 📊 Visual Diagram
```
STANDARD ERROR ENVELOPE:
──────────────────────────────────────
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",      ← stable, machine-readable
    "message": "Invalid signup data", ← human-readable
    "details": [                      ← optional structured info
      { "field": "email", "issue": "required" },
      { "field": "age", "issue": "must be at least 18" }
    ]
  }
}

ERROR FLOW:
route handler throws AppError subclass
         │
         ▼
  next(err) forwards to
         │
         ▼
centralized errorHandler middleware
         │
         ▼
  consistent JSON error response
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| error.code | Stable machine-readable identifier | Stable machine-readable identifier |
| error.message | Human-readable description | Human-readable description |
| error.details | Structured extra info (e.g. field errors) | Structured extra info |
| Operational error | Expected, safe-to-show error | Expected, safe error |
| Centralized error middleware | Single place converting errors to the standard shape | Error को standard shape में बदलने वाला single middleware |

---

## ⚡ 3-Line Summary
English:
1. Use one consistent error envelope (`success: false, error: { code, message, details }`) across the entire API.
2. `code` is stable and machine-readable for programmatic handling; `message` is human-readable; `details` holds structured field-level info.
3. Centralize error shaping in Express error middleware, never leak stack traces/internals for unexpected errors, and return ALL validation errors at once.

Hindi:
1. पूरे API में एक consistent error envelope (`success: false, error: { code, message, details }`) use करो।
2. `code` stable और machine-readable है programmatic handling के लिए; `message` human-readable है; `details` structured field-level info रखता है।
3. Error shaping को Express error middleware में centralize करो, unexpected errors के लिए कभी stack trace/internals leak मत करो, और सारे validation errors एक साथ return करो।

---

## ➡️ Next Topic
**180. HATEOAS** — Response में hypermedia links include करके API को self-descriptive बनाना।
