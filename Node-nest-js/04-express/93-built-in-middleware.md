# 93. Built-in Middleware
# हिंदी में: Built-in Middleware

---

## 🔵 Simple Definition (English)
**Built-in middleware** are middleware functions shipped directly with Express itself (no extra npm install needed) — namely `express.json()`, `express.urlencoded()`, `express.static()`, and `express.raw()`/`express.text()`. They handle the most common tasks: parsing request bodies and serving static files.

## 🔵 सरल परिभाषा (Hindi)
**Built-in middleware** वो middleware functions हैं जो Express के साथ ही आते हैं (कोई extra npm install नहीं चाहिए) — जैसे `express.json()`, `express.urlencoded()`, `express.static()`, और `express.raw()`/`express.text()`। ये सबसे common tasks handle करते हैं: request body parse करना और static files serve करना।

---

## 🔴 Problem it Solves
```
WITHOUT BUILT-IN MIDDLEWARE:
  app.post('/data', (req, res) => {
    let body = '';
    req.on('data', chunk => body += chunk);    // manual buffering
    req.on('end', () => {
      try {
        req.body = JSON.parse(body);            // manual JSON parsing
      } catch (e) {
        return res.status(400).json({ error: 'Invalid JSON' });
      }
      // ... handler logic
    });
  });
  // Also: manually reading files from disk, setting Content-Type, handling
  // 304 Not Modified, ETags, etc. for static files — tons of boilerplate!

WITH BUILT-IN MIDDLEWARE:
  app.use(express.json());              // body parsing — one line
  app.use(express.static('public'));    // static file serving — one line
```

## 🔴 यह क्यों बना? (Hindi)
बिना built-in middleware के, हर developer को body parsing और static file serving जैसी बहुत common चीज़ें manually implement करनी पड़ती थीं — यह repetitive और error-prone था (खासकर static files में caching headers, ETags, range requests सही से handle करना मुश्किल होता है)। Express ने इन्हें framework में ही built-in कर दिया ताकि हर project इसे दोबारा न लिखे।

---

## 🟢 How it Works — Step by Step

Step 1 → `express.json()` reads the raw request body stream, checks `Content-Type: application/json`, parses it with `JSON.parse()`, and sets `req.body`
Step 2 → `express.urlencoded()` similarly parses `Content-Type: application/x-www-form-urlencoded` bodies (HTML form submissions) into `req.body`
Step 3 → `express.static(root)` checks if the request path matches a file inside the `root` directory; if found, it streams the file with correct `Content-Type`, handles caching headers (`ETag`, `Last-Modified`), and calls `res.sendFile()` internally
Step 4 → If `express.static()` doesn't find a matching file, it calls `next()` so the request continues down the middleware chain (doesn't 404 immediately)
Step 5 → All built-in middleware are added via `app.use()` just like any other middleware — order still matters

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `express.json()` raw request body stream पढ़ता है, `Content-Type: application/json` check करता है, `JSON.parse()` से parse करके `req.body` set करता है
Step 2 → `express.urlencoded()` इसी तरह `application/x-www-form-urlencoded` bodies को `req.body` में parse करता है
Step 3 → `express.static(root)` check करता है कि request path `root` directory में किसी file से match करता है; मिलने पर correct `Content-Type` के साथ file stream करता है, caching headers handle करता है
Step 4 → `express.static()` को file नहीं मिली तो `next()` call करता है (immediately 404 नहीं करता)
Step 5 → सभी built-in middleware `app.use()` से add होते हैं — order यहाँ भी matter करता है

---

## 🟡 Real World Example
**Amazon product images:** `app.use('/images', express.static('public/product-images'))` serves millions of product photos directly from disk with proper caching headers (`Cache-Control`, `ETag`) — browsers cache these images, reducing server load. Meanwhile `app.use(express.json({ limit: '5mb' }))` parses incoming JSON for the review-submission API, rejecting bodies over 5MB to prevent abuse.

## 🟡 Real Example Hindi mein
**Amazon product images:** `app.use('/images', express.static('public/product-images'))` millions product photos को disk से proper caching headers के साथ serve करता है — browsers इन्हें cache करते हैं, server load कम होता है। और `app.use(express.json({ limit: '5mb' }))` review-submission API के incoming JSON को parse करता है, 5MB से बड़े bodies को reject करता है।

---

## 💻 Code Example — Basic

```javascript
// built-in-middleware-basic.js
const express = require('express');
const app = express();

// Parse JSON bodies (Content-Type: application/json)
app.use(express.json());

// Parse URL-encoded bodies (HTML form submissions, Content-Type: application/x-www-form-urlencoded)
app.use(express.urlencoded({ extended: true }));  // extended:true allows nested objects

// Serve static files from the 'public' folder
// e.g., public/style.css becomes accessible at http://localhost:3000/style.css
app.use(express.static('public'));

app.post('/api/data', (req, res) => {
  console.log(req.body);   // works for both JSON and form submissions
  res.json({ received: req.body });
});

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// built-in-middleware-advanced.js — options, multiple static roots, raw bodies

const express = require('express');
const path = require('path');
const app = express();

// express.json() with size limit and custom type matcher
app.use(express.json({
  limit: '1mb',                              // reject bodies over 1MB (DoS protection)
  type: ['application/json', 'application/vnd.api+json'],  // accept custom content-types too
}));

// express.urlencoded() with strict option
app.use(express.urlencoded({
  extended: true,     // use 'qs' library (supports nested objects) vs false (simple key-value only)
  limit: '1mb',
}));

// express.raw() — for binary data (e.g., webhook signature verification needs raw bytes)
app.use('/webhooks/razorpay', express.raw({ type: 'application/json' }));
app.post('/webhooks/razorpay', (req, res) => {
  // req.body is a raw Buffer here, needed to verify HMAC signature before parsing
  const signature = req.headers['x-razorpay-signature'];
  // verifySignature(req.body, signature) ...
  res.sendStatus(200);
});

// express.static() with options
app.use('/assets', express.static(path.join(__dirname, 'public'), {
  maxAge: '1d',          // Cache-Control: max-age=86400 (1 day)
  etag: true,            // send ETag headers for conditional requests
  index: 'index.html',   // default file served for directory requests
  extensions: ['html'],  // allow /about to resolve to about.html
}));

// Multiple static roots — Express checks them in order
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.static(path.join(__dirname, 'uploads')));

app.listen(3000, () => console.log('Server on 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// A realistic setup combining all built-in middleware for a Swiggy-style API
const express = require('express');
const path = require('path');
const app = express();

app.use(express.json({ limit: '2mb' }));          // JSON API payloads
app.use(express.urlencoded({ extended: true }));  // legacy form submissions (e.g., admin panel)
app.use(express.static(path.join(__dirname, 'public')));  // serve uploaded restaurant images

app.get('/api/restaurants/:id', (req, res) => {
  res.json({ id: req.params.id, image: '/images/restaurant-1.jpg' });  // served by express.static
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Expecting `req.body` to be populated without the right middleware
```javascript
// WRONG: no body-parsing middleware registered
const app = express();
app.post('/data', (req, res) => {
  console.log(req.body);  // undefined! express.json() was never added
});

// CORRECT
app.use(express.json());
app.post('/data', (req, res) => {
  console.log(req.body);  // { ... } parsed correctly
});
```

❌ **Mistake 2:** Placing `express.static()` AFTER your API routes, causing conflicts or missed files
```javascript
// WRONG: if a route and a static file share a path prefix, order matters
app.get('/index.html', customHandler);   // registered first — always wins over static file
app.use(express.static('public'));        // public/index.html never served if above matches first

// CORRECT: decide intentionally — usually static comes first for assets,
// but specific API routes under /api are fine registered in any order relative to static
app.use(express.static('public'));
app.use('/api', apiRouter);
```

---

## 🧠 Tricky Interview Question

```javascript
const express = require('express');
const app = express();
app.use(express.static('public'));  // public/data.json exists on disk

app.get('/data.json', (req, res) => {
  res.json({ fromRoute: true });
});

app.listen(3000);
// GET /data.json → does it return the file or the route's JSON?
```
Answer: It returns the STATIC FILE from `public/data.json`, NOT the route handler's response. This is because `express.static()` is registered FIRST in the middleware chain — if it finds a matching file, it serves it directly and ENDS the request-response cycle (it never calls `next()` in that case). The `app.get('/data.json', ...)` route registered afterward never even gets a chance to run. Reordering so the route is registered BEFORE `express.static()` would make the route win instead.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `express.json()` and `express.urlencoded()`?
A1: `express.json()` parses request bodies with `Content-Type: application/json` (used by modern REST APIs / fetch / axios). `express.urlencoded()` parses `Content-Type: application/x-www-form-urlencoded` bodies (traditional HTML `<form>` submissions). Both populate `req.body`, but they handle different content types and will simply skip parsing (leaving `req.body` as `{}` or undefined) if the `Content-Type` header doesn't match what they expect.

Q2: What does the `extended` option in `express.urlencoded({ extended: true })` control?
A2: It controls which library parses the URL-encoded data. `extended: false` uses Node's built-in `querystring` library (simple key-value pairs only, no nested objects/arrays). `extended: true` uses the `qs` library, which supports rich nested objects and arrays in form data (e.g., `user[name]=Rahul&user[age]=25` becomes `{ user: { name: 'Rahul', age: '25' } }`).

Q3: How does `express.static()` decide whether to serve a file or call `next()`?
A3: It checks if the requested URL path corresponds to an actual file inside the configured root directory. If the file EXISTS, it streams it as the response (setting appropriate headers like `Content-Type`, `ETag`, `Last-Modified`) and the chain ends there. If the file does NOT exist, it calls `next()`, allowing subsequent middleware/routes to handle the request (so it can safely coexist with API routes without causing 404s for non-static paths).

Q4: Why would you use `express.raw()` instead of `express.json()` for webhook endpoints?
A4: Many webhook providers (Razorpay, Stripe, GitHub) sign the payload with an HMAC signature computed over the EXACT raw bytes of the request body. If Express parses the body into a JS object first (losing exact formatting/whitespace) and you then re-stringify it to verify the signature, the signature check will likely fail due to formatting differences. `express.raw()` preserves the body as an untouched `Buffer`, letting you verify the signature against the exact bytes received before parsing it into JSON yourself.

Q5: Can you have multiple `express.static()` calls with different roots? How does Express resolve conflicts?
A5: Yes — you can register multiple `express.static()` middleware, each pointing to a different directory (e.g., one for `public/`, one for `uploads/`). Express checks them in REGISTRATION ORDER; the first one that finds a matching file serves it. If none match, the request falls through to subsequent middleware/routes. This is useful for layering a "theme" directory over a "default assets" directory, for example.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Parsing JSON/form request bodies (`express.json`, `express.urlencoded`) — needed for almost every API
- Serving static assets like images, CSS, client-side JS bundles, uploaded files (`express.static`)
- Needing raw, unparsed body bytes for signature verification (`express.raw`)

❌ Avoid when:
- Serving large media files at scale in production — better to use a CDN or dedicated object storage (S3 + CloudFront) rather than Express serving from local disk
- Needing very custom multipart/form-data parsing — built-in middleware doesn't handle file uploads; use `multer` for that (see topic on Multer)

---

## 📊 Visual Diagram
```
  BUILT-IN MIDDLEWARE DECISION FLOW
  ──────────────────────────────────────────────
  Request: POST /api/data  (Content-Type: application/json)
       │
       ▼
  express.json()
    → matches Content-Type? YES → parse body → req.body = {...} → next()
    → matches Content-Type? NO  → skip parsing → next() (req.body stays {})
       │
       ▼
  express.urlencoded()
    → matches Content-Type? NO (it's JSON) → skip → next()
       │
       ▼
  express.static('public')
    → file exists at this path? NO (it's an API route) → next()
       │
       ▼
  Route handler runs with req.body populated
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `express.json()` | Parses JSON request bodies | JSON request body parse करता है |
| `express.urlencoded()` | Parses form-encoded bodies | Form-encoded body parse करता है |
| `express.static()` | Serves static files from disk | Disk से static files serve करता है |
| `express.raw()` | Keeps body as unparsed Buffer | Body को unparsed Buffer रखता है |
| ETag | Cache validation header for files | Files के लिए cache validation header |

---

## ⚡ 3-Line Summary
English: 1. Built-in middleware (`express.json`, `express.urlencoded`, `express.static`) ship with Express and handle body parsing and static file serving without extra packages. 2. `express.static()` serves a file and ends the chain if found, otherwise calls `next()` — order relative to API routes matters. 3. Use `express.raw()` for webhooks needing exact byte-level signature verification.
Hindi: 1. Built-in middleware (`express.json`, `express.urlencoded`, `express.static`) Express के साथ आते हैं और body parsing, static file serving handle करते हैं। 2. `express.static()` file मिलने पर serve करके chain खत्म करता है, नहीं तो `next()` call करता है। 3. Webhooks के exact byte-level signature verification के लिए `express.raw()` use करो।

---

## ➡️ Next Topic
**94. Third-party Middleware** — Using npm packages like `cors`, `helmet`, `morgan`, `multer` as middleware.
