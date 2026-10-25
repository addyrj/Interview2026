# 105. CORS in Express
# हिंदी में: Express में CORS

---

## 🔵 Simple Definition (English)
**CORS (Cross-Origin Resource Sharing)** is a browser security mechanism that blocks web pages from making requests to a DIFFERENT origin (domain/port/protocol) than the one that served the page, UNLESS the server explicitly allows it via response headers. The `cors` npm package provides Express middleware to configure which origins, methods, and headers are allowed.

## 🔵 सरल परिभाषा (Hindi)
**CORS (Cross-Origin Resource Sharing)** एक browser security mechanism है जो web pages को किसी DIFFERENT origin (domain/port/protocol) पर requests करने से रोकता है, जब तक server explicitly response headers से allow न करे। `cors` npm package Express middleware देता है जो allowed origins, methods, headers configure करता है।

---

## 🔴 Problem it Solves
```
BROWSER'S SAME-ORIGIN POLICY (the default, restrictive behavior):
  Frontend running on https://app.myapp.com
  API running on       https://api.myapp.com
  → Browser BLOCKS the fetch() call by default — different origin!
  → Error in console: "has been blocked by CORS policy: No
    'Access-Control-Allow-Origin' header is present..."

WITH CORS MIDDLEWARE CONFIGURED:
  app.use(cors({ origin: 'https://app.myapp.com' }));
  → Server explicitly tells the browser "this origin is allowed"
  → Browser permits the frontend's JS to read the response
```

## 🔴 यह क्यों बना? (Hindi)
Browsers का Same-Origin Policy by default किसी भी cross-origin request को block करता है — यह एक security measure है ताकि malicious websites आपके bank/email session cookies का misuse न कर सकें। लेकिन modern apps में frontend और backend अक्सर अलग domains पर होते हैं (SPA + API), तो CORS एक controlled way देता है server को यह बताने के लिए कि कौन से origins को access allow है।

---

## 🟢 How it Works — Step by Step

Step 1 → Browser sends a request with an `Origin` header indicating where the JS code is running from
Step 2 → For "simple" requests (GET/POST with simple headers), browser sends the request directly, then checks the RESPONSE for `Access-Control-Allow-Origin`
Step 3 → For "non-simple" requests (PUT/DELETE, custom headers, `Content-Type: application/json`), browser first sends a PREFLIGHT `OPTIONS` request asking "are you going to allow this?"
Step 4 → Server (via `cors` middleware) responds to the preflight with `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers` — if they match, browser proceeds with the real request
Step 5 → If the ORIGIN header doesn't match what's allowed, the browser BLOCKS the JavaScript from reading the response (the request may still reach the server, but the browser hides the response from your code)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Browser `Origin` header के साथ request भेजता है
Step 2 → "Simple" requests directly भेजे जाते हैं, फिर response में `Access-Control-Allow-Origin` check होता है
Step 3 → "Non-simple" requests (PUT/DELETE, custom headers) के लिए browser पहले PREFLIGHT `OPTIONS` request भेजता है
Step 4 → Server preflight का response देता है allowed origins/methods/headers के साथ
Step 5 → Origin match न करे तो browser JavaScript को response पढ़ने से रोकता है (request server तक पहुँच सकता है, पर browser response hide करता है)

---

## 🟡 Real World Example
**Paytm web app + API:** Frontend is served from `https://paytm.com`, while the API lives at `https://api.paytm.com`. The API configures `cors({ origin: 'https://paytm.com', credentials: true })` so only the official frontend can make authenticated (cookie-based) requests. A malicious site at `https://evil-clone.com` trying to call the SAME API would be blocked by the browser — even if it somehow has a user's session cookie, the browser won't let the malicious page's JS read the response.

## 🟡 Real Example Hindi mein
**Paytm web app + API:** Frontend `https://paytm.com` से serve होता है, API `https://api.paytm.com` पर है। API `cors({ origin: 'https://paytm.com', credentials: true })` configure करता है ताकि सिर्फ official frontend authenticated requests कर सके। Malicious site `https://evil-clone.com` browser द्वारा blocked हो जाएगा।

---

## 💻 Code Example — Basic

```javascript
// cors-basic.js
// npm install express cors
const express = require('express');
const cors = require('cors');
const app = express();

// Allow ALL origins (useful for public APIs, NOT for authenticated/cookie-based APIs)
app.use(cors());

app.get('/api/public-data', (req, res) => {
  res.json({ message: 'Accessible from any origin' });
});

// Allow only a SPECIFIC origin
app.use('/api/private', cors({ origin: 'https://myapp.com' }));
app.get('/api/private/data', (req, res) => {
  res.json({ message: 'Only myapp.com can read this' });
});

app.listen(3000, () => console.log('Server on 3000'));
```

## 💻 Code Example — Advanced

```javascript
// cors-advanced.js — dynamic origin checking, credentials, preflight caching

const express = require('express');
const cors = require('cors');
const app = express();

const allowedOrigins = [
  'https://app.myapp.com',
  'https://admin.myapp.com',
  'http://localhost:3000',   // for local development
];

const corsOptions = {
  origin: (origin, callback) => {
    // origin is undefined for same-origin requests or non-browser clients (e.g., curl, mobile apps)
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);        // allow
    } else {
      callback(new Error(`Origin ${origin} not allowed by CORS`));  // block
    }
  },
  credentials: true,                // allow cookies/auth headers in cross-origin requests
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-ID'],
  exposedHeaders: ['X-Total-Count'],  // headers the CLIENT's JS is allowed to read
  maxAge: 86400,                      // cache preflight response for 1 day (reduces OPTIONS calls)
};

app.use(cors(corsOptions));
app.use(express.json());

// Handle preflight explicitly for a specific route if needed (cors() usually does this automatically)
app.options('/api/orders/:id', cors(corsOptions));  // explicit preflight handler

app.put('/api/orders/:id', (req, res) => {
  res.json({ updated: req.params.id });
});

// Error handler for CORS rejections
app.use((err, req, res, next) => {
  if (err.message.includes('not allowed by CORS')) {
    return res.status(403).json({ error: 'CORS policy: origin not allowed' });
  }
  next(err);
});

app.listen(3000, () => console.log('Server on 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// Real-world: environment-based CORS config for a Swiggy-style API
const express = require('express');
const cors = require('cors');
const app = express();

const corsOptions = {
  origin: process.env.NODE_ENV === 'production'
    ? ['https://swiggy.com', 'https://partner.swiggy.com']
    : '*',   // permissive in development
  credentials: process.env.NODE_ENV === 'production',
};

app.use(cors(corsOptions));
app.use(express.json());

app.use('/api/orders', require('./routes/orders'));

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `origin: '*'` together with `credentials: true`
```javascript
// WRONG: invalid per spec — browsers reject this combination
app.use(cors({ origin: '*', credentials: true }));

// CORRECT: specify explicit origins (or a validating function) when using credentials
app.use(cors({ origin: 'https://myapp.com', credentials: true }));
```

❌ **Mistake 2:** Assuming CORS protects the server — it's a BROWSER-enforced policy only
```javascript
// WRONG BELIEF: "My CORS config secures my API from unauthorized access"
app.use(cors({ origin: 'https://myapp.com' }));
// A non-browser client (curl, Postman, server-to-server, a malicious script using
// node-fetch) can call your API directly, completely ignoring CORS — it's NOT
// a server-side access control mechanism, only a browser-side JS restriction!

// CORRECT: use REAL authentication/authorization (JWT, API keys) for actual security
app.use(cors({ origin: 'https://myapp.com' }));  // UX/browser convenience
app.use(requireApiKeyOrJWT);                      // ACTUAL security
```

---

## 🧠 Tricky Interview Question

```javascript
// Server has NO cors middleware at all.
// A malicious page at evil.com runs:
fetch('https://api.bank.com/transfer', { method: 'POST', credentials: 'include', body: '...' });
// Does the malicious transfer request actually REACH and execute on the bank's server?
```
Answer: YES, the request likely STILL REACHES the server and MAY execute (if the user has a valid session cookie for `bank.com`, which the browser automatically attaches due to `credentials: 'include'`) — CORS does NOT prevent the request from being SENT; it only prevents the malicious page's JavaScript from READING the response. This is exactly why CORS alone is NOT sufficient protection against CSRF (Cross-Site Request Forgery) — a state-changing action can still happen even if the attacker never sees the result. Proper defenses require CSRF tokens, `SameSite` cookie attributes, or requiring custom headers that simple cross-origin requests can't set without triggering a preflight that the server can then reject.

---

## ⚫ Interview Questions + Answers

Q1: What problem does CORS solve, and who enforces it — the browser or the server?
A1: CORS solves the problem of controlling which websites' JavaScript can read responses from your API when the request originates from a DIFFERENT origin than your API. It's enforced ENTIRELY by the BROWSER — the server just sends HEADERS (`Access-Control-Allow-Origin`, etc.) indicating what's permitted, and the browser decides whether to expose the response to the page's JS based on those headers. Non-browser clients (curl, server-to-server calls, mobile apps) are NOT restricted by CORS at all.

Q2: What triggers a CORS "preflight" OPTIONS request, and what doesn't?
A2: A preflight is triggered for "non-simple" requests: any method other than GET/HEAD/POST, a `Content-Type` other than `text/plain`/`multipart/form-data`/`application/x-www-form-urlencoded` (e.g., `application/json` triggers it), or custom headers (like `Authorization`, `X-Custom-Header`). "Simple" requests (basic GET/POST with standard headers) skip the preflight and go straight to the actual request.

Q3: Why can't you combine `Access-Control-Allow-Origin: *` with credentialed requests?
A3: It's a deliberate security restriction in the CORS spec — allowing ANY origin to make authenticated (cookie/credential-bearing) requests would let ANY malicious website perform authenticated actions on behalf of a logged-in user, defeating the purpose of same-origin protections. Browsers enforce this at the spec level: a response with `*` and credentials included is simply rejected by the browser, regardless of server intent.

Q4: Does setting up CORS correctly protect your API from unauthorized access by non-browser clients?
A4: No. CORS is a browser-only mechanism — tools like `curl`, Postman, server-to-server HTTP clients, or a malicious Node.js script calling your API directly completely ignore CORS headers (since there's no browser enforcing them). Real access control requires server-side authentication (API keys, JWT, OAuth) and authorization checks — CORS is purely about controlling which WEB PAGES' JavaScript can access your API, not a general security boundary.

Q5: What does the `maxAge` option in CORS configuration do, and why would you tune it?
A5: `maxAge` tells the BROWSER how long (in seconds) it can CACHE the preflight (`OPTIONS`) response, avoiding repeated preflight round-trips for subsequent requests to the same endpoint with the same method/headers. Setting a longer `maxAge` (e.g., `86400` = 1 day) reduces latency and server load for frequently-called non-simple endpoints, at the cost of the browser potentially using a stale CORS policy if you change your allowed origins before the cache expires.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Your frontend and API are served from different origins (different domain/subdomain/port)
- You need granular control over which domains, methods, and headers are permitted cross-origin

❌ Avoid when:
- Relying on CORS alone as your API's security mechanism — always pair with real authentication/authorization
- Using `origin: '*'` for APIs that handle sensitive, credentialed (cookie-based) operations

---

## 📊 Visual Diagram
```
  CORS PREFLIGHT FLOW (non-simple request, e.g., PUT with JSON body)
  ────────────────────────────────────────────────────────────────
  Browser JS: fetch('https://api.example.com/orders/5', { method: 'PUT', ... })
       │
       ▼
  1. Browser sends PREFLIGHT:
     OPTIONS /orders/5
     Origin: https://app.example.com
     Access-Control-Request-Method: PUT
       │
       ▼
  2. Server (cors middleware) responds:
     Access-Control-Allow-Origin: https://app.example.com
     Access-Control-Allow-Methods: GET,POST,PUT,DELETE
       │
       ▼
  3. Browser checks: does my origin match the allowed one? YES
       │
       ▼
  4. Browser sends the REAL request:
     PUT /orders/5
       │
       ▼
  5. Server responds normally — browser exposes response to JS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Origin | Scheme + domain + port combination | Scheme + domain + port combination |
| Preflight | OPTIONS request checking permissions | Permissions check करने वाला OPTIONS request |
| `Access-Control-Allow-Origin` | Header stating allowed origin(s) | Allowed origin बताने वाला header |
| Credentials | Cookies/auth headers in cross-origin requests | Cross-origin requests में cookies/auth headers |
| Same-Origin Policy | Browser's default cross-origin restriction | Browser की default cross-origin restriction |

---

## ⚡ 3-Line Summary
English: 1. CORS is a browser-enforced mechanism controlling which origins' JS can read your API's responses — configured via response headers. 2. Non-simple requests trigger an OPTIONS preflight; `origin: '*'` cannot be combined with `credentials: true`. 3. CORS is NOT a security boundary against non-browser clients — always pair with real auth/authorization.
Hindi: 1. CORS browser-enforced mechanism है जो control करता है कि कौन से origins का JS आपके API का response पढ़ सकता है। 2. Non-simple requests OPTIONS preflight trigger करते हैं; `origin: '*'` और `credentials: true` साथ नहीं चल सकते। 3. CORS non-browser clients के against security नहीं है — real auth जरूरी है।

---

## ➡️ Next Topic
**106. Helmet.js — Security Headers** — Hardening Express apps against common web vulnerabilities via HTTP headers.
