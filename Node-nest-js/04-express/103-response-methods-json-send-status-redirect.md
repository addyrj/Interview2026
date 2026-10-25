# 103. Response Methods (json, send, status, redirect)
# हिंदी में: Response Methods (json, send, status, redirect)

---

## 🔵 Simple Definition (English)
Express's `res` object provides chainable methods to shape and send the HTTP response: `res.json()` sends JSON, `res.send()` sends various types (string/buffer/object), `res.status()` sets the HTTP status code, `res.redirect()` sends a redirect response, plus helpers like `res.sendStatus()`, `res.set()`, `res.cookie()`, `res.sendFile()`. Understanding each one precisely avoids subtle bugs.

## 🔵 सरल परिभाषा (Hindi)
Express का `res` object chainable methods देता है response भेजने के लिए: `res.json()` JSON भेजता है, `res.send()` कई types भेज सकता है (string/buffer/object), `res.status()` HTTP status code set करता है, `res.redirect()` redirect भेजता है, और helpers जैसे `res.sendStatus()`, `res.set()`, `res.cookie()`, `res.sendFile()`। हर एक को precisely समझना subtle bugs से बचाता है।

---

## 🔴 Problem it Solves
```
WITHOUT HELPER METHODS (raw http module):
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ ok: true }));
  // manual header setting, manual stringify, manual status management

WITH EXPRESS RESPONSE METHODS:
  res.status(200).json({ ok: true });
  // one line: sets status, sets Content-Type, stringifies, sends — all automatically
```

## 🔴 यह क्यों बना? (Hindi)
Raw `http` module में हर response के लिए headers manually set करने पड़ते, JSON manually stringify करना पड़ता, status code manually set करना पड़ता। Express ने इन सबको chainable helper methods में wrap कर दिया, जिससे एक line में पूरी response भेजी जा सके।

---

## 🟢 How it Works — Step by Step

Step 1 → `res.status(code)` sets `res.statusCode` and RETURNS `res` itself (enabling chaining) — it does NOT send anything yet
Step 2 → `res.json(obj)` calls `JSON.stringify()` internally, sets `Content-Type: application/json`, and flushes the response — this IS terminal
Step 3 → `res.send(data)` auto-detects type: string → `text/html`, Buffer → `application/octet-stream`, object/array → delegates to `res.json()` internally
Step 4 → `res.redirect([status,] url)` sets the `Location` header and a 3xx status code (default 302), ending the response
Step 5 → Only ONE terminal method should be called per request — calling a second one throws "Cannot set headers after they are sent"

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `res.status(code)` `res.statusCode` set करता है और `res` return करता है (chaining के लिए) — अभी कुछ भेजता नहीं
Step 2 → `res.json(obj)` internally `JSON.stringify()` करता है, `Content-Type` set करता है, response flush करता है — यह terminal है
Step 3 → `res.send(data)` type auto-detect करता है
Step 4 → `res.redirect([status,] url)` `Location` header और 3xx status set करता है, response end करता है
Step 5 → एक request के लिए सिर्फ एक terminal method call करना चाहिए

---

## 🟡 Real World Example
**Amazon checkout flow:** `res.status(201).json({ orderId, estimatedDelivery })` after successful order creation. `res.status(400).json({ error: 'Invalid coupon code' })` for validation failure. `res.redirect(302, '/payment/success')` after a payment gateway callback completes. `res.status(204).send()` after successfully deleting a saved address (no content to return). Each status+method combo communicates precise semantics to the client/frontend team.

## 🟡 Real Example Hindi mein
**Amazon checkout flow:** Order create होने पर `res.status(201).json({...})`। Validation fail पर `res.status(400).json({...})`। Payment gateway callback के बाद `res.redirect(302, '/payment/success')`। Address delete होने पर `res.status(204).send()`। हर status+method combo frontend team को precise meaning बताता है।

---

## 💻 Code Example — Basic

```javascript
// response-methods-basic.js
const express = require('express');
const app = express();
app.use(express.json());

// res.json() — most common for APIs
app.get('/json-example', (req, res) => {
  res.json({ message: 'Hello', timestamp: Date.now() });
});

// res.send() — flexible, auto-detects content type
app.get('/send-string', (req, res) => res.send('<h1>Plain HTML string</h1>'));
app.get('/send-object', (req, res) => res.send({ note: 'send() with an object calls json() internally' }));

// res.status() chained with other methods
app.get('/not-found', (req, res) => {
  res.status(404).json({ error: 'Resource not found' });
});

// res.redirect()
app.get('/old-page', (req, res) => {
  res.redirect(301, '/new-page');   // 301 = permanent redirect
});
app.get('/new-page', (req, res) => res.send('You are on the new page'));

// res.sendStatus() — sends status code + its standard text as body
app.delete('/items/:id', (req, res) => {
  res.sendStatus(204);   // sends "204 No Content" — shorthand for res.status(204).send('No Content')
});

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// response-methods-advanced.js — headers, cookies, files, content negotiation

const express = require('express');
const path = require('path');
const app = express();
app.use(express.json());

// res.set() / res.header() — set custom response headers
app.get('/api/data', (req, res) => {
  res.set('X-Total-Count', '42');
  res.set({ 'X-Custom-A': '1', 'X-Custom-B': '2' });   // multiple at once
  res.status(200).json({ data: [] });
});

// res.cookie() — set a cookie
app.post('/login', (req, res) => {
  res.cookie('sessionId', 'abc123', {
    httpOnly: true,     // JS on the client can't read it (XSS protection)
    secure: true,        // only sent over HTTPS
    maxAge: 24 * 60 * 60 * 1000,  // 1 day in ms
    sameSite: 'strict',
  });
  res.status(200).json({ loggedIn: true });
});

// res.sendFile() — send a specific file (e.g., invoice PDF)
app.get('/invoices/:id', (req, res) => {
  const filePath = path.join(__dirname, 'invoices', `${req.params.id}.pdf`);
  res.sendFile(filePath, (err) => {
    if (err) res.status(404).json({ error: 'Invoice not found' });
  });
});

// res.format() — content negotiation based on Accept header
app.get('/api/report', (req, res) => {
  res.format({
    'application/json': () => res.json({ report: 'data' }),
    'text/html': () => res.send('<h1>Report</h1>'),
    default: () => res.status(406).send('Not Acceptable'),
  });
});

// res.location() + res.redirect() for a proper 201 Created response with Location header
app.post('/api/resources', (req, res) => {
  const newId = 42;
  res.location(`/api/resources/${newId}`);  // sets Location header
  res.status(201).json({ id: newId });
});

// Chaining multiple response configuration calls before the terminal call
app.get('/api/chained', (req, res) => {
  res
    .status(200)
    .set('Cache-Control', 'no-store')
    .set('X-Powered-By', 'MyAPI')
    .json({ chained: true });   // terminal call last
});

app.listen(3000, () => console.log('Server on 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// Real-world consistent response helper pattern (Zomato-style API)
const express = require('express');
const app = express();
app.use(express.json());

// A small utility to standardize success/error response shapes across the app
const sendSuccess = (res, data, statusCode = 200) => {
  res.status(statusCode).json({ success: true, data });
};
const sendError = (res, message, statusCode = 400) => {
  res.status(statusCode).json({ success: false, error: message });
};

app.get('/api/restaurants/:id', (req, res) => {
  const restaurant = { id: req.params.id, name: 'Pizza Hub' };
  if (!restaurant) return sendError(res, 'Restaurant not found', 404);
  sendSuccess(res, restaurant);
});

app.post('/api/restaurants', (req, res) => {
  const created = { id: 1, ...req.body };
  sendSuccess(res, created, 201);
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling a response method and then trying to modify headers afterward
```javascript
// WRONG: trying to set a header AFTER res.json() already sent the response
app.get('/data', (req, res) => {
  res.json({ ok: true });
  res.set('X-Custom', 'value');   // ❌ Error: Cannot set headers after they are sent
});

// CORRECT: set all headers BEFORE calling the terminal method
app.get('/data', (req, res) => {
  res.set('X-Custom', 'value');
  res.json({ ok: true });
});
```

❌ **Mistake 2:** Using `res.send()` for JSON APIs inconsistently with objects AND strings
```javascript
// WRONG: inconsistent response shapes confuse API consumers
app.get('/a', (req, res) => res.send({ data: 1 }));   // becomes JSON
app.get('/b', (req, res) => res.send('{"data":2}'));   // stays a STRING with text/html content-type!

// CORRECT: always use res.json() explicitly for JSON APIs — avoids ambiguity
app.get('/a', (req, res) => res.json({ data: 1 }));
app.get('/b', (req, res) => res.json({ data: 2 }));
```

---

## 🧠 Tricky Interview Question

```javascript
app.get('/test', (req, res) => {
  res.send('{"key":"value"}');   // a JSON-LOOKING STRING, not an object
});
// What Content-Type header does the client receive, and why does this matter?
```
Answer: The client receives `Content-Type: text/html`, NOT `application/json` — even though the string LOOKS like JSON. `res.send()` determines Content-Type based on the DATA TYPE passed, not its content: a JavaScript STRING always gets `text/html` by default (unless you already set Content-Type explicitly). To actually get `application/json`, you must either pass an actual OBJECT (`res.send({key:'value'})`, which internally calls `res.json()`), or use `res.json()` directly, or manually call `res.type('application/json')` before sending the string. This matters because many HTTP clients use the Content-Type header to decide HOW to parse the response body — a mismatched header can break client-side JSON parsing expectations.

---

## ⚫ Interview Questions + Answers

Q1: What's the exact difference between `res.send()` and `res.json()`?
A1: `res.json(data)` ALWAYS JSON-stringifies its argument and sets `Content-Type: application/json`, regardless of the argument's type. `res.send(data)` is more generic: for a STRING it sets `text/html`; for a Buffer it sets `application/octet-stream`; for an object/array/boolean/number, it internally DELEGATES to `res.json()`. In practice, `res.json()` is preferred for APIs because it's explicit and unambiguous about intent.

Q2: Why does `res.status(200)` not immediately send a response?
A2: `res.status(code)` only SETS the internal `res.statusCode` property and returns the `res` object itself to allow METHOD CHAINING (e.g., `res.status(404).json(...)`). The actual response is only sent/flushed when a TERMINAL method is called — `res.json()`, `res.send()`, `res.end()`, or `res.redirect()`. Calling `res.status()` alone leaves the request hanging if nothing terminal follows.

Q3: What's the difference between `res.redirect(url)` and `res.redirect(301, url)`?
A3: `res.redirect(url)` defaults to a `302 Found` (temporary redirect) status code. `res.redirect(301, url)` explicitly uses `301 Moved Permanently`. The distinction matters for SEO and caching: browsers/search engines CACHE 301 redirects aggressively (treating the old URL as permanently gone), while 302 redirects are treated as temporary and re-checked on each visit. Use 301 for permanent URL changes, 302 for temporary ones (e.g., post-login redirects).

Q4: How would you send a response with a specific HTTP status code but NO body?
A4: Use `res.sendStatus(code)` — e.g., `res.sendStatus(204)` sends status 204 with the STANDARD reason phrase text as the body ("No Content"). Alternatively, `res.status(204).end()` sends status 204 with a COMPLETELY EMPTY body (no text at all). The difference: `sendStatus()` includes the standard HTTP status text as plain text body; `.end()` sends nothing.

Q5: Why is calling multiple terminal response methods for one request a bug, and what error does it produce?
A5: HTTP responses can only be sent ONCE per request — headers and body are flushed to the TCP socket as soon as a terminal method runs. Calling a second terminal method (e.g., `res.json()` twice) tries to modify/resend headers that have ALREADY been sent to the client, which Node's `http` module explicitly disallows, throwing `Error: Cannot set headers after they are sent to the client`. Always ensure exactly ONE terminal response call per code path, often by using `return` before each terminal call in conditional branches.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `res.json()` for virtually all API responses — explicit and unambiguous
- `res.status()` to set meaningful HTTP status codes communicating outcome semantics
- `res.redirect()` for navigation flows (OAuth callbacks, post-form-submit redirects)

❌ Avoid when:
- Using `res.send()` with mixed types inconsistently across an API — pick `res.json()` for consistency
- Sending a body with `res.redirect()` expecting the client to read it — redirects are followed automatically by browsers, body content is typically ignored

---

## 📊 Visual Diagram
```
  RESPONSE METHOD CHAIN
  ─────────────────────────────────────────
  res.status(201)      → sets statusCode, returns res (chainable, NOT terminal)
       │
       ▼
  res.set('X-A', '1')   → sets header, returns res (chainable, NOT terminal)
       │
       ▼
  res.json({ ok:true }) → TERMINAL: stringifies, sets Content-Type, FLUSHES response
       │
       ▼
  [Response sent — any further res.* calls throw an error]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Terminal method | Ends the response-sending process | Response भेजने की process खत्म करता है |
| `res.json()` | Sends JSON response | JSON response भेजता है |
| `res.send()` | Sends auto-detected content type | Auto-detected content type भेजता है |
| `res.redirect()` | Sends a redirect (3xx) response | Redirect (3xx) response भेजता है |
| `res.sendStatus()` | Sends status code + its text body | Status code + text body भेजता है |

---

## ⚡ 3-Line Summary
English: 1. `res.status()`/`res.set()` are chainable and non-terminal; `res.json()`/`res.send()`/`res.redirect()`/`res.end()` are terminal and must be called exactly once. 2. `res.json()` always stringifies and sets `application/json`; `res.send()` auto-detects type based on the argument. 3. Use `301` for permanent redirects (cached by browsers) and `302` (default) for temporary ones.
Hindi: 1. `res.status()`/`res.set()` chainable हैं; `res.json()`/`res.send()`/`res.redirect()` terminal हैं — exactly एक बार call करो। 2. `res.json()` हमेशा stringify करता है; `res.send()` type auto-detect करता है। 3. Permanent redirect के लिए `301`, temporary के लिए `302` use करो।

---

## ➡️ Next Topic
**104. HTTP Status Codes — Complete Guide** — Full breakdown of 1xx-5xx status codes and when to use each.
