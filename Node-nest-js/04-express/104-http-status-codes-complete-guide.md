# 104. HTTP Status Codes — Complete Guide
# हिंदी में: HTTP Status Codes — पूरी जानकारी

---

## 🔵 Simple Definition (English)
HTTP status codes are 3-digit numbers the server sends to tell the client the OUTCOME of a request, grouped by first digit: **1xx** Informational, **2xx** Success, **3xx** Redirection, **4xx** Client Error, **5xx** Server Error. Choosing the RIGHT code is critical for correct client behavior (retries, caching, error display).

## 🔵 सरल परिभाषा (Hindi)
HTTP status codes 3-digit numbers हैं जो server client को request का OUTCOME बताता है, first digit से grouped: **1xx** Informational, **2xx** Success, **3xx** Redirection, **4xx** Client Error, **5xx** Server Error। सही code choose करना client behavior (retries, caching, error display) के लिए जरूरी है।

---

## 🔴 Problem it Solves
```
WITHOUT PROPER STATUS CODES (everything returns 200):
  app.post('/users', (req, res) => {
    if (!req.body.email) {
      return res.status(200).json({ error: 'Email required' });  // ❌ 200 means SUCCESS!
    }
    // Client-side code checks res.ok (true for 200) and proceeds as if successful
    // → silent bugs, broken error handling, confused monitoring/alerting systems
  });

WITH PROPER STATUS CODES:
  app.post('/users', (req, res) => {
    if (!req.body.email) {
      return res.status(400).json({ error: 'Email required' });  // ✅ 400 = client error
    }
    res.status(201).json({ created: true });  // ✅ 201 = resource created
  });
  // Clients, proxies, monitoring tools, and caches all behave CORRECTLY based on the code
```

## 🔴 यह क्यों बना? (Hindi)
बिना proper status codes के, clients/proxies/monitoring tools को पता नहीं चलता कि request actually successful थी या नहीं — सब कुछ 200 भेजने से silent bugs बनते, retries गलत होते, caching गलत behave करती। HTTP spec (RFC 7231 और related RFCs) ने standardized codes define किए जो हर layer (browser, CDN, load balancer, client SDK) को सही behavior करने देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Server processes the request and determines the outcome (success, client mistake, server failure, etc.)
Step 2 → Server picks the status code category: 2xx (success), 3xx (redirect), 4xx (client's fault), 5xx (server's fault)
Step 3 → Server sets the SPECIFIC code within that category based on precise semantics (e.g., 404 vs 400 vs 403 are all "client error" but mean different things)
Step 4 → Client/browser/proxy inspects the code to decide behavior: cache the response? retry? show an error? follow a redirect?
Step 5 → Monitoring/alerting systems often track 5xx rates as a server health signal, distinct from 4xx (which usually indicates bad client requests, not server bugs)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Server request process करके outcome decide करता है
Step 2 → Status code category choose करता है: 2xx, 3xx, 4xx, 5xx
Step 3 → Category के अंदर specific code set करता है (404 vs 400 vs 403 सब अलग मतलब रखते हैं)
Step 4 → Client/browser/proxy code देखकर decide करता है: cache करे? retry करे? error दिखाए?
Step 5 → Monitoring systems 5xx rates को server health signal मानते हैं, 4xx को client-side issue

---

## 🟡 Real World Example
**Flipkart API gateway monitoring:** Their dashboards track 5xx error rate as the primary "is our server healthy" metric — a spike triggers PagerDuty alerts to engineers. 4xx errors (like 400 bad request, 404 not found, 429 rate limited) are tracked separately as "client behavior" metrics — high 404s might indicate a broken frontend link, high 429s might indicate aggressive bot traffic, neither necessarily means the SERVER is broken.

## 🟡 Real Example Hindi mein
**Flipkart API gateway monitoring:** Dashboards 5xx error rate को primary "server healthy है या नहीं" metric मानते हैं — spike आने पर engineers को alert जाता है। 4xx errors (400, 404, 429) अलग से track होते हैं "client behavior" metrics के रूप में — ये जरूरी नहीं कि SERVER टूटा हो।

---

## 💻 Code Example — Basic

```javascript
// status-codes-basic.js
const express = require('express');
const app = express();
app.use(express.json());

// 200 OK — standard success for GET
app.get('/api/users/:id', (req, res) => {
  const user = { id: req.params.id, name: 'Rahul' };
  res.status(200).json(user);
});

// 201 Created — successful resource creation (POST)
app.post('/api/users', (req, res) => {
  res.status(201).json({ id: 1, ...req.body });
});

// 204 No Content — successful action with nothing to return (DELETE)
app.delete('/api/users/:id', (req, res) => {
  res.status(204).send();
});

// 400 Bad Request — client sent invalid data
app.post('/api/orders', (req, res) => {
  if (!req.body.items) return res.status(400).json({ error: 'items required' });
  res.status(201).json({ created: true });
});

// 404 Not Found — resource doesn't exist
app.get('/api/orders/:id', (req, res) => {
  const order = null;
  if (!order) return res.status(404).json({ error: 'Order not found' });
  res.json(order);
});

// 500 Internal Server Error — something unexpected broke
app.get('/api/crash', (req, res) => {
  res.status(500).json({ error: 'Something went wrong on our end' });
});

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// status-codes-advanced.js — a comprehensive, correctly-coded API

const express = require('express');
const app = express();
app.use(express.json());

let users = [{ id: 1, email: 'rahul@example.com' }];

// 401 Unauthorized — missing/invalid authentication
app.get('/api/profile', (req, res) => {
  if (!req.headers.authorization) {
    return res.status(401).json({ error: 'Authentication required' });
  }
  res.status(200).json({ profile: 'data' });
});

// 403 Forbidden — authenticated but NOT allowed (different from 401!)
app.delete('/api/admin/users/:id', (req, res) => {
  const userRole = req.headers['x-role'];
  if (userRole !== 'admin') {
    return res.status(403).json({ error: 'Admin role required' });  // we KNOW who you are, you just can't do this
  }
  res.status(204).send();
});

// 409 Conflict — request conflicts with current server state
app.post('/api/users', (req, res) => {
  const exists = users.find(u => u.email === req.body.email);
  if (exists) {
    return res.status(409).json({ error: 'Email already registered' });
  }
  const newUser = { id: users.length + 1, ...req.body };
  users.push(newUser);
  res.status(201).json(newUser);
});

// 422 Unprocessable Entity — syntactically valid but semantically wrong (some APIs use this instead of 400)
app.post('/api/payments', (req, res) => {
  if (req.body.amount < 0) {
    return res.status(422).json({ error: 'Amount cannot be negative' });
  }
  res.status(201).json({ processed: true });
});

// 429 Too Many Requests — rate limiting
app.use('/api/sensitive', (req, res, next) => {
  const tooManyRequests = false;   // pretend rate limit check
  if (tooManyRequests) {
    res.set('Retry-After', '60');   // tell client when to retry
    return res.status(429).json({ error: 'Rate limit exceeded' });
  }
  next();
});

// 502/503/504 — upstream/server unavailable errors
app.get('/api/external-data', async (req, res) => {
  try {
    const data = await callExternalAPI();
    res.json(data);
  } catch (err) {
    if (err.code === 'ETIMEDOUT') {
      return res.status(504).json({ error: 'Gateway Timeout — upstream service too slow' });
    }
    res.status(502).json({ error: 'Bad Gateway — upstream service failed' });
  }
});
async function callExternalAPI() { return { ok: true }; }

app.listen(3000, () => console.log('Server on 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// Centralized status-code-aware error handler
const express = require('express');
const app = express();
app.use(express.json());

class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
  }
}

app.get('/api/orders/:id', (req, res, next) => {
  const order = null;
  if (!order) return next(new AppError('Order not found', 404));
  res.json(order);
});

app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  res.status(statusCode).json({ error: err.message });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Confusing 401 (Unauthorized) with 403 (Forbidden)
```javascript
// WRONG: using 401 when the user IS authenticated but lacks permission
app.delete('/admin/users/:id', (req, res) => {
  if (req.user.role !== 'admin') return res.status(401).json({ error: 'No access' });  // ❌ wrong code
});

// CORRECT: 401 = "who ARE you?" (missing/invalid auth); 403 = "I know who you are, but NO"
app.delete('/admin/users/:id', (req, res) => {
  if (!req.user) return res.status(401).json({ error: 'Please log in' });
  if (req.user.role !== 'admin') return res.status(403).json({ error: 'Insufficient permissions' });
});
```

❌ **Mistake 2:** Returning 200 for errors because "it's easier for the frontend"
```javascript
// WRONG: masks real errors, breaks HTTP semantics, confuses monitoring
app.post('/login', (req, res) => {
  if (invalidCredentials) return res.status(200).json({ success: false, error: 'Wrong password' });

// CORRECT: use the real status code — frontends should check it properly
app.post('/login', (req, res) => {
  if (invalidCredentials) return res.status(401).json({ error: 'Wrong password' });
});
```

---

## 🧠 Tricky Interview Question

```javascript
// A client sends a request, server redirects with 307, another with 302.
// What's the KEY difference between 301/302/307/308 redirects?
```
Answer: **301 (Moved Permanently)** and **302 (Found)** historically allowed browsers to CHANGE the method from POST to GET when following the redirect (a long-standing quirk), while **307 (Temporary Redirect)** and **308 (Permanent Redirect)** STRICTLY preserve the original HTTP method and body — introduced specifically to fix that ambiguity. So: 301 vs 308 are both "permanent" but 308 guarantees method preservation; 302 vs 307 are both "temporary" but 307 guarantees method preservation. For API redirects where preserving the method/body matters (e.g., redirecting a POST request), use 307/308, not 301/302.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between 400, 401, 403, and 404?
A1: **400 Bad Request** — the request itself is malformed/invalid (missing fields, wrong format). **401 Unauthorized** — authentication is missing or invalid (the server doesn't know WHO you are). **403 Forbidden** — the server knows who you are but you don't have PERMISSION for this action. **404 Not Found** — the requested resource simply doesn't exist (or the server wants to hide its existence for privacy/security).

Q2: Why might an API use 422 instead of 400 for validation errors?
A2: 400 technically means the request is malformed at the HTTP/syntax level (e.g., broken JSON). 422 (Unprocessable Entity, from WebDAV, adopted broadly) means the request was syntactically VALID (well-formed JSON) but semantically incorrect per business rules (e.g., negative age, invalid enum value). Some API design styles (notably JSON:API) prefer 422 specifically for this distinction, though many APIs use 400 for both cases without issue — it's partly convention.

Q3: What does 429 Too Many Requests typically pair with, and why?
A3: It typically pairs with a `Retry-After` header (seconds or a date) telling the client WHEN it's safe to retry. This lets well-behaved clients back off appropriately instead of hammering the server immediately, and it's a standard signal rate-limiting middleware (like `express-rate-limit`) sets automatically.

Q4: What's the difference between 502, 503, and 504 in a server error context?
A4: **502 Bad Gateway** — a server acting as a proxy/gateway got an INVALID response from an upstream server. **503 Service Unavailable** — the server is temporarily unable to handle requests (e.g., overloaded, in maintenance) — often paired with `Retry-After`. **504 Gateway Timeout** — a proxy/gateway server did NOT get a response from the upstream server within its timeout window. These are common in microservice architectures where one service calls another.

Q5: Should your API always return 500 for unexpected errors, or is there a better practice?
A5: 500 is the correct GENERIC fallback for truly unexpected server-side errors (bugs, uncaught exceptions) — but a well-designed API should use SPECIFIC codes (400/401/403/404/409/422/429) for all EXPECTED error conditions, reserving 500 only for genuinely unanticipated failures. Overusing 500 for everything (including client mistakes) makes monitoring/alerting noisy and unhelpful, since 500 spikes should mean "our code/infrastructure is broken," not "users are sending bad requests."

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always — every HTTP response needs an accurate status code; this is non-negotiable for a correct API
- Specific codes (401 vs 403, 400 vs 422, 502 vs 503 vs 504) when the distinction genuinely helps clients/monitoring behave correctly

❌ Avoid when:
- Returning 200 for all responses regardless of outcome (defeats the purpose of HTTP semantics)
- Overusing niche/obscure codes your API consumers won't understand — stick to well-known, widely-supported codes for public APIs

---

## 📊 Visual Diagram
```
  HTTP STATUS CODE CATEGORIES
  ─────────────────────────────────────────────────
  1xx  Informational   100 Continue, 101 Switching Protocols
  2xx  Success          200 OK, 201 Created, 204 No Content
  3xx  Redirection      301 Moved Permanently, 302 Found, 304 Not Modified
  4xx  Client Error     400 Bad Request, 401 Unauthorized, 403 Forbidden,
                        404 Not Found, 409 Conflict, 422 Unprocessable,
                        429 Too Many Requests
  5xx  Server Error     500 Internal Server Error, 502 Bad Gateway,
                        503 Service Unavailable, 504 Gateway Timeout

  Decision flow for an API:
  Request OK?           → 2xx
  Need to redirect?      → 3xx
  Client's mistake?      → 4xx (be specific: 400/401/403/404/409/422/429)
  Our server's fault?    → 5xx (be specific: 500/502/503/504)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| 2xx | Success category | Success category |
| 4xx | Client error category | Client error category |
| 5xx | Server error category | Server error category |
| `Retry-After` | Header telling when to retry | कब retry करें, यह header बताता है |
| Idempotent redirect | 307/308 preserve method/body | 307/308 method/body preserve करते हैं |

---

## ⚡ 3-Line Summary
English: 1. Status codes communicate outcome: 2xx success, 3xx redirect, 4xx client error, 5xx server error — pick specific codes (401 vs 403, 502 vs 503 vs 504) for precise semantics. 2. Never return 200 for error conditions — it breaks client error handling and monitoring. 3. 307/308 preserve HTTP method on redirect; 301/302 historically don't — matters for redirecting non-GET requests.
Hindi: 1. Status codes outcome बताते हैं: 2xx success, 3xx redirect, 4xx client error, 5xx server error — specific codes use करो। 2. Error conditions में कभी 200 return मत करो। 3. 307/308 redirect पर HTTP method preserve करते हैं, 301/302 नहीं।

---

## ➡️ Next Topic
**105. CORS in Express** — Cross-Origin Resource Sharing configuration and common pitfalls.
