# 131. CORS — Complete Guide
# हिंदी में: CORS — पूरी गाइड

---

## 🔵 Simple Definition (English)
**CORS (Cross-Origin Resource Sharing)** is a browser security mechanism that blocks web pages from making requests to a different origin (different domain/port/protocol) than the one that served the page — unless the server explicitly allows it via special HTTP headers. It's a browser-enforced rule, not a server-side restriction.

## 🔵 सरल परिभाषा (Hindi)
**CORS** एक browser security mechanism है जो web pages को किसी different origin (अलग domain/port/protocol) पर requests भेजने से रोकता है — जब तक server special HTTP headers से explicitly allow न करे। यह browser द्वारा enforce किया जाता है, server की restriction नहीं।

---

## 🔴 Problem it Solves
Without CORS rules, any malicious website could silently use your browser's logged-in session to make requests to `bank.com` or `zomato.com` on your behalf (since cookies auto-attach), reading/stealing your private data via JavaScript. The **Same-Origin Policy (SOP)** is the browser's default protection — it blocks cross-origin JS requests entirely. But legitimate cases exist (frontend on `app.zomato.com` calling API on `api.zomato.com`) — CORS gives servers a controlled way to say "this specific other origin is trusted, allow it."

## 🔴 यह क्यों बना? (Hindi)
CORS rules के बिना कोई malicious website silently आपके browser की logged-in session use करके `bank.com` या `zomato.com` पर requests भेज सकती थी (cookies auto-attach होती हैं), और आपका private data चुरा सकती थी। **Same-Origin Policy (SOP)** browser का default protection है — यह cross-origin JS requests को पूरी तरह block करता है। पर legitimate cases होते हैं (frontend `app.zomato.com` पर, API `api.zomato.com` पर) — CORS servers को नियंत्रित तरीका देता है कि किसी specific origin को trust करें।

---

## 🟢 How it Works — Step by Step

Step 1 → Browser JS makes a fetch to a different origin (e.g., `app.zomato.com` → `api.zomato.com`)
Step 2 → For "simple" requests (GET/POST with simple headers), browser sends request directly, checks response headers
Step 3 → For "non-simple" requests (PUT/DELETE, custom headers, JSON content-type), browser sends a **preflight** `OPTIONS` request first, asking "are you okay with this?"
Step 4 → Server responds with headers: `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`
Step 5 → If preflight approves, browser sends the actual request
Step 6 → Browser checks `Access-Control-Allow-Origin` on the actual response — if origin doesn't match, browser blocks JS from reading the response (the request may still have reached the server!)
Step 7 → For cookies/credentials, server must also send `Access-Control-Allow-Credentials: true` and the origin must NOT be `*`

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Browser JS किसी different origin पर fetch करता है
Step 2 → Simple requests के लिए browser directly request भेजता है
Step 3 → Non-simple requests के लिए browser पहले एक preflight `OPTIONS` request भेजता है
Step 4 → Server headers के साथ respond करता है
Step 5 → Preflight approve होने पर actual request भेजी जाती है
Step 6 → Browser response के `Access-Control-Allow-Origin` header check करता है
Step 7 → Cookies के लिए `Access-Control-Allow-Credentials: true` ज़रूरी है, origin `*` नहीं हो सकता

---

## 🟡 Real World Example
**Swiggy's architecture:** Frontend React app hosted on `www.swiggy.com`, API hosted on `api.swiggy.com` — these are different origins (different subdomains). When the frontend calls `fetch('https://api.swiggy.com/orders')`, the browser enforces CORS. Swiggy's backend must respond with `Access-Control-Allow-Origin: https://www.swiggy.com` for the browser to let the frontend JS read the response. Meanwhile, their public read-only restaurant-listing API (used by partner apps) might set `Access-Control-Allow-Origin: *` since no sensitive cookies are involved.

## 🟡 Real Example Hindi mein
**Swiggy का architecture:** Frontend `www.swiggy.com` पर, API `api.swiggy.com` पर — ये different origins हैं। Frontend जब `fetch('https://api.swiggy.com/orders')` करता है, browser CORS enforce करता है। Swiggy का backend `Access-Control-Allow-Origin: https://www.swiggy.com` header भेजता है ताकि browser frontend JS को response पढ़ने दे।

---

## 💻 Code Example — Basic

```javascript
// cors-basic.js — manual CORS headers without any library
// Run with: node cors-basic.js, test with curl or browser fetch

const http = require('http');

const ALLOWED_ORIGIN = 'https://www.swiggy.com';  // the trusted frontend origin

const server = http.createServer((req, res) => {
  // Step 1: always set Allow-Origin for the specific trusted origin
  res.setHeader('Access-Control-Allow-Origin', ALLOWED_ORIGIN);
  // Step 2: tell browser which methods are allowed cross-origin
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  // Step 3: tell browser which custom headers are allowed
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  // Step 4: allow cookies to be sent cross-origin (needs specific origin, not *)
  res.setHeader('Access-Control-Allow-Credentials', 'true');

  // Step 5: handle the PREFLIGHT request (browser sends OPTIONS before real request)
  if (req.method === 'OPTIONS') {
    res.writeHead(204);  // No Content — just approving the preflight
    return res.end();
  }

  // Step 6: handle the actual request
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ message: 'Orders fetched successfully' }));
});

server.listen(3000, () => console.log('Server on port 3000'));
```

## 💻 Code Example — Advanced

```javascript
// cors-advanced.js — Production CORS with multiple allowed origins + validation

const allowedOrigins = [
  'https://www.swiggy.com',
  'https://partner.swiggy.com',
  'http://localhost:3001',  // local dev
];

// Dynamic origin check function — called per-request
function corsOriginValidator(origin, callback) {
  // origin is undefined for same-origin requests (e.g., curl, server-to-server) — allow those
  if (!origin) return callback(null, true);

  if (allowedOrigins.includes(origin)) {
    callback(null, true);   // allow this specific origin
  } else {
    callback(new Error(`Origin ${origin} not allowed by CORS`));
  }
}

// Using the `cors` npm package (production standard)
const cors = require('cors');  // npm install cors

const corsOptions = {
  origin: corsOriginValidator,       // dynamic allow-list check
  credentials: true,                  // allow cookies/Authorization headers
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  exposedHeaders: ['X-Total-Count'],  // custom headers JS can read from response
  maxAge: 86400,                      // cache preflight result for 24 hours (fewer OPTIONS calls)
  optionsSuccessStatus: 204,
};

const express = require('express');
const app = express();

app.use(cors(corsOptions));  // apply globally

// Per-route CORS override example (stricter for sensitive routes)
const strictCors = cors({
  origin: 'https://admin.swiggy.com',  // only admin dashboard
  credentials: true,
});

app.get('/public/restaurants', cors({ origin: '*' }), (req, res) => {
  // public endpoint — no cookies, safe to allow any origin
  res.json({ restaurants: [] });
});

app.delete('/admin/users/:id', strictCors, (req, res) => {
  // sensitive endpoint — only admin dashboard origin allowed
  res.json({ message: 'User deleted' });
});

app.listen(3000);

module.exports = { corsOptions };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — full Express app with environment-based CORS config
const express = require('express');
const cors = require('cors');

const app = express();

// Load allowed origins from env (comma-separated), fallback to dev defaults
const allowedOrigins = (process.env.ALLOWED_ORIGINS || 'http://localhost:3000')
  .split(',')
  .map((o) => o.trim());

app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error('Not allowed by CORS'));
      }
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization'],
  })
);

app.use(express.json());

// Error handler for CORS rejection (the cors() middleware calls next(err))
app.use((err, req, res, next) => {
  if (err.message === 'Not allowed by CORS') {
    return res.status(403).json({ error: 'CORS policy: origin not allowed' });
  }
  next(err);
});

app.get('/orders', (req, res) => {
  res.json({ orders: [] });
});

app.listen(3000, () => console.log('API on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `Access-Control-Allow-Origin: *` together with credentials
```javascript
// WRONG: browsers REJECT this combination — spec forbids wildcard + credentials
res.setHeader('Access-Control-Allow-Origin', '*');
res.setHeader('Access-Control-Allow-Credentials', 'true');
// Browser console error: "credentials flag is true, but Access-Control-Allow-Origin is *"

// CORRECT: reflect the exact requesting origin when credentials are needed
res.setHeader('Access-Control-Allow-Origin', req.headers.origin);  // specific origin
res.setHeader('Access-Control-Allow-Credentials', 'true');
```

❌ Mistake 2: Thinking CORS protects the server — it only protects the browser's JS
```javascript
// WRONG belief: "CORS blocks attackers from hitting my API"
// Reality: CORS is enforced by the BROWSER, not the server.
// curl, Postman, or a server-to-server request IGNORES CORS entirely —
// the request still reaches your server and executes!

// CORRECT: CORS is not authentication/authorization. Still need:
app.use(authenticate);          // verify JWT/session
app.use(rateLimiter);           // prevent abuse
// CORS only stops a BROWSER from letting malicious JS read the response.
```

---

## 🧠 Tricky Interview Question

```javascript
// Server has NO CORS headers configured at all.
// Browser JS on evil.com runs:
fetch('https://api.zomato.com/profile', { credentials: 'include' })
  .then(res => console.log('status:', res.status));
// The user IS logged into zomato.com (has a valid session cookie).
// What happens?
```
Answer: The browser **still sends** the request (cookies attach because `credentials: 'include'` and the user has a valid Zomato session) — **the server DOES process it and returns a 200 response with the user's profile data**. However, since there's no `Access-Control-Allow-Origin` header in the response, the browser **blocks the JavaScript from reading the response body** — `res.status` might even be readable in some cases but the body/JSON is inaccessible, and a CORS error appears in the console. Crucially: **the side effect already happened server-side** (if it were a POST changing data, the change has already occurred!) — this is why CORS alone doesn't stop state-changing attacks; CSRF tokens are needed for that (see topic 132).

---

## ⚫ Interview Questions + Answers

Q1: What triggers a CORS preflight (OPTIONS) request?
A1: A preflight is sent for "non-simple" requests: (1) methods other than GET/HEAD/POST, (2) Content-Type other than `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain` (e.g., `application/json` triggers preflight!), (3) custom headers like `Authorization`. Simple GET requests with no custom headers skip preflight and go directly.

Q2: What is the difference between `Access-Control-Allow-Origin: *` and specifying an exact origin?
A2: `*` allows ANY website's JS to read the response — fine for fully public, non-sensitive data with no cookies involved. An exact origin (e.g., `https://app.swiggy.com`) restricts access to only that origin, required when `Access-Control-Allow-Credentials: true` is set (cookies/auth), since browsers reject the wildcard+credentials combination for security.

Q3: Does CORS protect against CSRF attacks?
A3: No. CORS controls whether browser JavaScript can READ a cross-origin response — it does NOT prevent the cross-origin request from being SENT and processed by the server. A classic CSRF attack (a hidden form auto-submitting a POST to your bank) doesn't need to read the response, so CORS doesn't stop it. CSRF tokens, SameSite cookies, and checking the Origin/Referer header are the actual defenses against CSRF.

Q4: Why does `fetch` need `credentials: 'include'` for cross-origin cookies, and what server header must match?
A4: By default, `fetch` does NOT send cookies on cross-origin requests. Setting `credentials: 'include'` tells the browser to attach cookies even cross-origin. For the browser to then expose the response to JS, the server must respond with `Access-Control-Allow-Credentials: true` AND a specific (non-wildcard) `Access-Control-Allow-Origin` matching the request's origin exactly.

Q5: How do you cache preflight results to reduce the number of OPTIONS requests?
A5: Set `Access-Control-Max-Age: <seconds>` in the preflight response (e.g., `86400` for 24 hours). The browser caches the preflight approval for that duration and skips sending OPTIONS again for matching requests (same origin/method/headers) until it expires. In the `cors` npm package, this is the `maxAge` option. Browsers also impose their own maximum cap (e.g., Chrome caps at 2 hours regardless of a larger value sent).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Your frontend and API are on different origins/subdomains/ports (very common with SPA + API architecture).
- You need to allow specific trusted third-party domains to call your public API.

❌ Avoid when:
- Frontend and backend are served from the exact same origin (no CORS needed at all — same-origin requests aren't restricted).
- Never use it as your only security layer — always pair with authentication, CSRF protection, and rate limiting.

---

## 📊 Visual Diagram

```
CORS PREFLIGHT FLOW:
──────────────────────────────────────────────────────────

  Browser (app.swiggy.com) wants to PUT JSON to api.swiggy.com
       │
       ▼
  1. Browser sends preflight:
     OPTIONS /orders/5
     Origin: https://app.swiggy.com
     Access-Control-Request-Method: PUT
     Access-Control-Request-Headers: Content-Type
       │
       ▼
  2. Server responds:
     Access-Control-Allow-Origin: https://app.swiggy.com
     Access-Control-Allow-Methods: PUT
     Access-Control-Allow-Headers: Content-Type
     Access-Control-Max-Age: 86400
       │
       ▼
  3. Browser: preflight OK → sends actual request
     PUT /orders/5  (with real body)
       │
       ▼
  4. Server processes + responds with data
       │
       ▼
  5. Browser checks Access-Control-Allow-Origin on actual response
     → matches → JS CAN read response ✅
     → mismatch → JS BLOCKED from reading (but request already executed!) ❌
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Same-Origin Policy | Browser default: block cross-origin JS access | Default cross-origin JS block |
| Origin | Scheme + domain + port combination | Scheme + domain + port |
| Preflight | OPTIONS request before actual request | Actual request से पहले OPTIONS |
| Simple request | Request that skips preflight | Preflight skip करने वाली request |
| Credentials | Cookies/Authorization sent cross-origin | Cross-origin भेजे cookies/auth |
| Wildcard origin | `*` — allows any origin | `*` — कोई भी origin allow |

---

## ⚡ 3-Line Summary
English:
1. CORS is a browser-enforced mechanism letting servers specify which origins may read cross-origin responses — it does not block the request from reaching the server.
2. Use exact origin allow-lists (never `*` with credentials) and handle OPTIONS preflight requests correctly.
3. CORS is not a security boundary for state-changing requests — pair it with CSRF protection and authentication.

Hindi:
1. CORS browser-enforced है — servers बताते हैं कौन से origins response पढ़ सकते हैं, request को block नहीं करता।
2. Exact origin allow-list use करो (credentials के साथ `*` कभी नहीं), OPTIONS preflight handle करो।
3. CORS state-changing requests के लिए security नहीं है — CSRF protection और authentication भी ज़रूरी है।

---

## ➡️ Next Topic
**132. CSRF Protection** — Cross-Site Request Forgery attacks से कैसे बचें, tokens और SameSite cookies।
