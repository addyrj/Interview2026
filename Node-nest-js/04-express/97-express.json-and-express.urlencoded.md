# 97. express.json() + express.urlencoded()
# हिंदी में: express.json() और express.urlencoded()

---

## 🔵 Simple Definition (English)
`express.json()` parses incoming requests with JSON payloads (`Content-Type: application/json`) and populates `req.body`. `express.urlencoded()` parses requests with URL-encoded payloads (`Content-Type: application/x-www-form-urlencoded`, typical of HTML `<form>` submissions). Both are built into Express (since v4.16, no separate `body-parser` package needed).

## 🔵 सरल परिभाषा (Hindi)
`express.json()` JSON payloads वाले requests (`Content-Type: application/json`) को parse करता है और `req.body` भरता है। `express.urlencoded()` URL-encoded payloads वाले requests (`Content-Type: application/x-www-form-urlencoded`, HTML `<form>` submissions की तरह) को parse करता है। दोनों Express में built-in हैं (v4.16 से, अलग `body-parser` package की जरूरत नहीं)।

---

## 🔴 Problem it Solves
```
BEFORE (pre-Express 4.16, needed separate 'body-parser' package):
  npm install body-parser
  const bodyParser = require('body-parser');
  app.use(bodyParser.json());
  app.use(bodyParser.urlencoded({ extended: true }));

NOW (built into Express core):
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));
  // No extra dependency needed — body-parser's logic was merged into Express itself
```

## 🔴 यह क्यों बना? (Hindi)
पहले body parsing के लिए अलग `body-parser` npm package install करना पड़ता था। Express 4.16 (2017) में इसे core में merge कर दिया गया ताकि common body-parsing use cases के लिए extra dependency न चाहिए। आज भी अगर `multipart/form-data` (file uploads) चाहिए, तो `multer` जैसा अलग package चाहिए — express.json/urlencoded वो handle नहीं करते।

---

## 🟢 How it Works — Step by Step

Step 1 → Middleware checks the request's `Content-Type` header
Step 2 → `express.json()` only processes if type matches `application/json` (or custom types you configure)
Step 3 → It reads the raw body stream, buffers it up to the `limit` option, then calls `JSON.parse()`
Step 4 → If parsing succeeds, sets `req.body` to the parsed object; if it fails (malformed JSON), it calls `next(err)` with a 400-ish error
Step 5 → `express.urlencoded()` follows the same flow but uses the `qs` (extended) or `querystring` (non-extended) library instead of `JSON.parse()`

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Middleware request के `Content-Type` header को check करता है
Step 2 → `express.json()` सिर्फ तब process करता है जब type `application/json` से match करे
Step 3 → यह raw body stream पढ़ता है, `limit` option तक buffer करता है, फिर `JSON.parse()` call करता है
Step 4 → Parse सफल हुआ तो `req.body` set करता है; fail हुआ (malformed JSON) तो `next(err)` से 400 जैसा error भेजता है
Step 5 → `express.urlencoded()` similar flow follow करता है पर `qs` (extended) या `querystring` (non-extended) library use करता है

---

## 🟡 Real World Example
**Flipkart checkout API:** The mobile app sends `POST /api/checkout` with `Content-Type: application/json` containing cart items and address — `express.json()` parses this into `req.body.items`, `req.body.address`. A legacy admin panel built with plain HTML forms sends `POST /api/admin/settings` with `Content-Type: application/x-www-form-urlencoded` — `express.urlencoded()` parses THAT into `req.body` instead. Both middleware coexist; each only acts on matching content types.

## 🟡 Real Example Hindi mein
**Flipkart checkout API:** Mobile app `POST /api/checkout` भेजता है `application/json` के साथ — `express.json()` इसे `req.body.items`, `req.body.address` में parse करता है। एक legacy admin panel plain HTML forms से `application/x-www-form-urlencoded` भेजता है — `express.urlencoded()` उसे parse करता है। दोनों middleware साथ रह सकते हैं; हर एक सिर्फ अपने matching content type पर काम करता है।

---

## 💻 Code Example — Basic

```javascript
// json-urlencoded-basic.js
const express = require('express');
const app = express();

app.use(express.json());                        // for JSON requests
app.use(express.urlencoded({ extended: true })); // for form requests

app.post('/api/json-test', (req, res) => {
  // Test with: curl -X POST -H "Content-Type: application/json" -d '{"name":"Rahul"}' localhost:3000/api/json-test
  res.json({ received: req.body, type: 'json' });
});

app.post('/form-test', (req, res) => {
  // Test with: curl -X POST -d "name=Rahul&age=25" localhost:3000/form-test
  res.json({ received: req.body, type: 'form' });
});

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// json-urlencoded-advanced.js — custom options, error handling, nested data

const express = require('express');
const app = express();

// express.json() with options:
app.use(express.json({
  limit: '2mb',                               // reject bodies > 2MB
  strict: true,                                // only accept arrays/objects (default: true)
  type: ['application/json', 'application/csp-report'],  // accept extra content-types as JSON
  verify: (req, res, buf) => {
    // optional hook — e.g., verify a signature BEFORE parsing
    // throw an error here to reject the request
  },
}));

// express.urlencoded() with options:
app.use(express.urlencoded({
  extended: true,     // use 'qs' for nested objects/arrays: user[name]=Rahul&user[age]=25
  limit: '1mb',
  parameterLimit: 1000,  // max number of parameters (DoS protection)
}));

app.post('/api/nested', (req, res) => {
  // With extended:true, form data like "address[city]=Delhi&address[pin]=110001"
  // becomes: { address: { city: 'Delhi', pin: '110001' } }
  res.json(req.body);
});

// Handling JSON parse errors explicitly
app.post('/api/strict-json', (req, res) => {
  res.json({ ok: true, data: req.body });
});

app.use((err, req, res, next) => {
  if (err.type === 'entity.parse.failed') {
    // express.json() sets this err.type when JSON.parse() throws
    return res.status(400).json({ error: 'Malformed JSON in request body' });
  }
  if (err.type === 'entity.too.large') {
    return res.status(413).json({ error: 'Payload too large' });
  }
  next(err);
});

app.listen(3000, () => console.log('Server on 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// Real-world: combining both parsers with route-specific limits
const express = require('express');
const app = express();

// Global defaults — modest limit
app.use(express.json({ limit: '100kb' }));
app.use(express.urlencoded({ extended: true, limit: '100kb' }));

// Specific route needs a LARGER limit (e.g., bulk product upload)
app.post(
  '/api/products/bulk-import',
  express.json({ limit: '10mb' }),   // overrides global for this route only
  (req, res) => {
    res.json({ imported: req.body.products?.length || 0 });
  }
);

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Expecting `express.json()` to parse `multipart/form-data` (file uploads)
```javascript
// WRONG: express.json() silently ignores multipart requests — req.body stays {}
app.use(express.json());
app.post('/upload', (req, res) => {
  console.log(req.body);  // {} — file upload data is NOT parsed by express.json()!
});

// CORRECT: use multer (or similar) for multipart/form-data
const multer = require('multer');
const upload = multer({ dest: 'uploads/' });
app.post('/upload', upload.single('file'), (req, res) => {
  console.log(req.file, req.body);  // works correctly
});
```

❌ **Mistake 2:** Setting a limit too low and silently rejecting legitimate requests without clear errors
```javascript
// WRONG: default-ish limit too small for legitimate payloads, generic 500 error confuses clients
app.use(express.json({ limit: '10kb' }));  // large JSON payloads fail with unclear 500

// CORRECT: set a reasonable limit AND handle the specific error type clearly
app.use(express.json({ limit: '5mb' }));
app.use((err, req, res, next) => {
  if (err.type === 'entity.too.large') {
    return res.status(413).json({ error: 'Request body too large, max 5mb' });
  }
  next(err);
});
```

---

## 🧠 Tricky Interview Question

```javascript
const express = require('express');
const app = express();
app.use(express.json());

app.post('/data', (req, res) => {
  res.json({ body: req.body });
});

app.listen(3000);
// Client sends POST /data with NO Content-Type header and raw JSON text in the body.
// What does req.body contain?
```
Answer: `req.body` will be `{}` (empty object), NOT the parsed JSON. `express.json()` ONLY parses the body if the `Content-Type` header matches `application/json` (its default `type` option). Without that header (or with a mismatched one, like the default `text/plain` many HTTP clients send), `express.json()` skips parsing entirely and calls `next()` without touching `req.body`, leaving it as the default empty object Express initializes. This is a very common gotcha when testing APIs with tools that don't set headers correctly, or when a client forgets to set `Content-Type: application/json` explicitly.

---

## ⚫ Interview Questions + Answers

Q1: Do `express.json()` and `express.urlencoded()` require a separate `body-parser` package?
A1: No, not since Express 4.16 (released 2017) — this functionality was merged directly into Express core. The standalone `body-parser` npm package still exists and both internally use the same underlying parsing logic, but you don't need to `npm install body-parser` separately anymore; `express.json()` and `express.urlencoded()` are available directly on the `express` object.

Q2: What happens if the `Content-Type` header doesn't match what the middleware expects?
A2: The middleware simply SKIPS parsing and calls `next()` without populating `req.body` (it stays as `{}` by default, Express's initial value). It does NOT throw an error for a mismatched Content-Type — this is intentional, since multiple body-parsing middleware can coexist, each only acting on its specific content type, letting requests "fall through" to the right one.

Q3: What's the difference between `extended: true` and `extended: false` in `express.urlencoded()`?
A3: `extended: false` uses Node's built-in `querystring` module — it can ONLY parse simple flat key-value pairs (no nested objects or arrays). `extended: true` uses the `qs` library, which supports RICH data structures: nested objects (`user[name]=X`) and arrays (`tags[]=a&tags[]=b`). Modern apps almost always use `extended: true` for flexibility, though it's slightly slower for very simple payloads.

Q4: What happens when a client sends malformed JSON with `express.json()` active?
A4: `express.json()` internally calls `JSON.parse()` on the buffered body. If that throws a `SyntaxError`, the middleware catches it and calls `next(err)` with an error object that has `err.type === 'entity.parse.failed'` and `err.status === 400`. Your centralized error-handling middleware should check for this to return a clean "Invalid JSON" response instead of a generic 500.

Q5: How would you set a different body-size limit for one specific route versus the global default?
A5: Call `express.json({ limit: '...' })` again directly as a route-specific middleware argument: `app.post('/bulk-upload', express.json({ limit: '10mb' }), handler)`. The route-specific instance OVERRIDES the global one for THAT route only (both run, but the more specific one re-parses with its own limit — actually, since the global one already parsed the body if its limit wasn't exceeded, best practice is to NOT apply the global json() to that route's path, or raise the global limit deliberately and rely on route-specific validation elsewhere).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building JSON-based REST APIs (`express.json()`) — the standard for modern APIs
- Supporting legacy HTML form submissions or certain third-party webhook formats (`express.urlencoded()`)

❌ Avoid when:
- Handling file uploads / `multipart/form-data` — neither parses this; use `multer`
- Needing the EXACT raw bytes for signature verification (webhooks) — use `express.raw()` instead, parse JSON manually afterward

---

## 📊 Visual Diagram
```
  CONTENT-TYPE BASED ROUTING THROUGH PARSERS
  ─────────────────────────────────────────────
  Incoming Request
       │
       ▼
  express.json()
    Content-Type: application/json?  → YES: parse → req.body = {...} → next()
                                      → NO:  skip → next() (body unchanged)
       │
       ▼
  express.urlencoded()
    Content-Type: application/x-www-form-urlencoded?  → YES: parse → req.body = {...}
                                                        → NO: skip → next()
       │
       ▼
  multer (if configured)
    Content-Type: multipart/form-data?  → YES: parse files + fields
                                         → NO: skip
       │
       ▼
  Route handler — req.body ready (or {} if nothing matched)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `express.json()` | Parses JSON bodies | JSON bodies parse करता है |
| `express.urlencoded()` | Parses form-encoded bodies | Form-encoded bodies parse करता है |
| `extended` option | Chooses `qs` vs `querystring` parser | `qs` या `querystring` parser चुनता है |
| `limit` option | Max accepted body size | Max accepted body size |
| `entity.parse.failed` | Error type for malformed JSON | Malformed JSON का error type |

---

## ⚡ 3-Line Summary
English: 1. `express.json()`/`express.urlencoded()` are built into Express (no separate body-parser needed) and parse bodies ONLY when `Content-Type` matches. 2. `extended: true` in urlencoded enables nested object/array parsing via the `qs` library. 3. Malformed JSON or oversized bodies throw specific error types (`entity.parse.failed`, `entity.too.large`) — handle them in your error middleware.
Hindi: 1. `express.json()`/`express.urlencoded()` Express में built-in हैं और सिर्फ matching `Content-Type` पर parse करते हैं। 2. `extended: true` nested objects/arrays parse करने देता है। 3. Malformed JSON या oversized bodies specific error types throw करते हैं — error middleware में handle करो।

---

## ➡️ Next Topic
**98. express.static()** — Serving static files (images, CSS, JS) with caching and configuration options.
