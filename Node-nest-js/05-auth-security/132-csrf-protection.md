# 132. CSRF Protection
# हिंदी में: CSRF Protection

---

## 🔵 Simple Definition (English)
**CSRF (Cross-Site Request Forgery)** is an attack where a malicious site tricks a logged-in user's browser into sending an unwanted request (with their cookies auto-attached) to another site, performing an action without the user's consent. **CSRF protection** defends against this using tokens, SameSite cookies, and origin checks.

## 🔵 सरल परिभाषा (Hindi)
**CSRF** एक attack है जहाँ कोई malicious site logged-in user के browser को trick करके एक unwanted request (cookies attached) दूसरी site पर भेजने देती है, user की सहमति के बिना action perform हो जाता है। **CSRF protection** इसे tokens, SameSite cookies, और origin checks से रोकता है।

---

## 🔴 Problem it Solves
Browsers automatically attach cookies to requests, even cross-origin ones (unless SameSite restricts it). So if a user is logged into `yourbank.com` and visits `evil.com` which has a hidden auto-submitting form `<form action="https://yourbank.com/transfer" method="POST">`, the browser sends the request WITH the user's session cookie — the bank server sees a valid session and processes the transfer, thinking it's a legitimate user action. CSRF protection ensures the server can distinguish "a request that originated from MY own site's form" from "a request forged by another site."

## 🔴 यह क्यों बना? (Hindi)
Browsers automatically cookies attach करते हैं, cross-origin requests पर भी (जब तक SameSite restrict न करे)। तो अगर user `yourbank.com` में logged in है और `evil.com` visit करता है जहाँ hidden auto-submit form है, browser request session cookie के साथ भेजता है — bank server valid session देखता है और transfer process कर देता है, सोचता है legitimate user action है। CSRF protection server को यह बताने देता है कि request आपकी ही site से आया या किसी दूसरी site से forge हुआ।

---

## 🟢 How it Works — Step by Step

Step 1 → Server generates a unique, unpredictable **CSRF token** per session/form
Step 2 → Token embedded in the HTML form as a hidden field, or sent to frontend via a dedicated endpoint
Step 3 → Browser sends the token back with the state-changing request (POST/PUT/DELETE) — as a hidden field or custom header
Step 4 → Server verifies the submitted token matches the one stored for that session
Step 5 → If mismatch/missing → reject with 403 (this is the key defense: an attacker's forged form on `evil.com` CANNOT know/read this token due to Same-Origin Policy)
Step 6 → Additionally: set cookies with `SameSite=Strict` or `SameSite=Lax` so browsers don't send them on cross-site requests at all
Step 7 → Double-check `Origin`/`Referer` headers as a secondary defense layer

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Server हर session/form के लिए unique **CSRF token** बनाता है
Step 2 → Token HTML form में hidden field के रूप में embed होता है
Step 3 → Browser token को state-changing request के साथ वापस भेजता है
Step 4 → Server submitted token को stored token से verify करता है
Step 5 → Mismatch होने पर 403 reject करता है
Step 6 → Cookies पर `SameSite=Strict/Lax` set करो ताकि cross-site requests पर cookies न जाएं
Step 7 → `Origin`/`Referer` headers भी secondary defense की तरह check करो

---

## 🟡 Real World Example
**Paytm's fund transfer:** When a user clicks "Transfer ₹5000", the frontend form includes a hidden `_csrf` token that was issued when the page loaded. If an attacker crafts a fake page mimicking this form on `evil.com` and tricks a logged-in Paytm user into clicking submit, the attacker's form has NO access to the real CSRF token (it's tied to the legit session and same-origin restricted) — so Paytm's server rejects the request with "Invalid CSRF token" before any money moves. Paytm additionally uses `SameSite=Strict` cookies for session tokens so they aren't even sent on cross-site navigations.

## 🟡 Real Example Hindi mein
**Paytm का fund transfer:** User जब "Transfer ₹5000" click करता है, frontend form में hidden `_csrf` token होता है। Attacker का fake page असली token access नहीं कर सकता (same-origin restricted) — इसलिए Paytm server request reject कर देता है पैसे move होने से पहले। Paytm `SameSite=Strict` cookies भी use करता है।

---

## 💻 Code Example — Basic

```javascript
// csrf-basic.js — manual token generation and verification concept
// Run with: node csrf-basic.js

const crypto = require('crypto');

// ─── 1. SIMULATED SESSION STORE (in real app: Redis/DB) ─────────────────────
const sessions = new Map();  // sessionId -> { csrfToken, userId }

// ─── 2. GENERATE CSRF TOKEN FOR A SESSION ────────────────────────────────────
function generateCsrfToken(sessionId) {
  const token = crypto.randomBytes(32).toString('hex');  // unpredictable, 64 hex chars
  const session = sessions.get(sessionId) || {};
  session.csrfToken = token;
  sessions.set(sessionId, session);
  return token;
}

// ─── 3. VERIFY TOKEN ON INCOMING REQUEST ─────────────────────────────────────
function verifyCsrfToken(sessionId, submittedToken) {
  const session = sessions.get(sessionId);
  if (!session || !session.csrfToken) return false;         // no token issued
  if (!submittedToken) return false;                          // nothing submitted
  // Use timing-safe comparison to avoid timing attacks on token comparison
  const a = Buffer.from(session.csrfToken);
  const b = Buffer.from(submittedToken);
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}

// ─── 4. SIMULATE A REQUEST FLOW ───────────────────────────────────────────────
const sessionId = 'sess_123';
const issuedToken = generateCsrfToken(sessionId);
console.log('Issued token:', issuedToken);

console.log('Legit request valid?', verifyCsrfToken(sessionId, issuedToken));     // true
console.log('Forged request valid?', verifyCsrfToken(sessionId, 'wrongtoken'));   // false
```

## 💻 Code Example — Advanced

```javascript
// csrf-advanced.js — double-submit cookie pattern (stateless, scalable)
// Common for APIs/SPAs where server-side session storage is avoided

const crypto = require('crypto');

// ─── DOUBLE SUBMIT COOKIE PATTERN ─────────────────────────────────────────────
// Idea: server sets a CSRF token as a cookie (readable by JS, NOT httpOnly)
// Frontend JS reads the cookie and sends it back as a custom header.
// Attacker's cross-site form CANNOT read the cookie value (Same-Origin Policy
// blocks reading cookies set by another domain) — so they can't replicate the header.

function generateCsrfCookieToken() {
  return crypto.randomBytes(32).toString('base64url');
}

// Middleware: issue CSRF cookie if not present
function csrfCookieMiddleware(req, res, next) {
  let token = req.cookies?.['csrf-token'];
  if (!token) {
    token = generateCsrfCookieToken();
    res.cookie('csrf-token', token, {
      httpOnly: false,        // JS MUST be able to read this one (unusual, but required for this pattern)
      secure: true,           // only over HTTPS
      sameSite: 'strict',     // extra layer: don't send on cross-site requests anyway
      maxAge: 24 * 60 * 60 * 1000,
    });
  }
  req.csrfCookieToken = token;
  next();
}

// Middleware: verify header matches cookie on state-changing requests
function csrfVerifyMiddleware(req, res, next) {
  const safeMethods = ['GET', 'HEAD', 'OPTIONS'];
  if (safeMethods.includes(req.method)) return next();  // no CSRF risk on reads

  const cookieToken = req.cookies?.['csrf-token'];
  const headerToken = req.headers['x-csrf-token'];

  if (!cookieToken || !headerToken) {
    return res.status(403).json({ error: 'CSRF token missing' });
  }

  const a = Buffer.from(cookieToken);
  const b = Buffer.from(headerToken);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) {
    return res.status(403).json({ error: 'CSRF token mismatch' });
  }

  next();
}

module.exports = { csrfCookieMiddleware, csrfVerifyMiddleware };
```

---

## 🟠 Express.js Integration

```javascript
// server.js
const express = require('express');
const cookieParser = require('cookie-parser');
const { csrfCookieMiddleware, csrfVerifyMiddleware } = require('./csrf-advanced');

const app = express();
app.use(express.json());
app.use(cookieParser());

// Issue CSRF cookie on every request (idempotent — only sets if missing)
app.use(csrfCookieMiddleware);

// Endpoint for frontend to explicitly fetch the token (useful on SPA load)
app.get('/csrf-token', (req, res) => {
  res.json({ csrfToken: req.csrfCookieToken });
});

// Apply verification only to state-changing routes
app.use('/api', csrfVerifyMiddleware);

app.post('/api/transfer', (req, res) => {
  // By the time we're here, CSRF token already verified by middleware
  const { toAccount, amount } = req.body;
  // ... perform transfer logic
  res.json({ message: `Transferred ₹${amount} to ${toAccount}` });
});

app.get('/api/balance', (req, res) => {
  // GET requests skip CSRF check (safe method, no state change)
  res.json({ balance: 50000 });
});

app.listen(3000);

// FRONTEND USAGE (for reference):
// const token = document.cookie.match(/csrf-token=([^;]+)/)[1];
// fetch('/api/transfer', {
//   method: 'POST',
//   headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': token },
//   body: JSON.stringify({ toAccount: 'xyz', amount: 500 }),
//   credentials: 'include',
// });
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Applying CSRF protection to GET requests
```javascript
// WRONG: GET requests shouldn't change state, and blocking them breaks normal links/SEO
app.get('/api/profile', csrfVerifyMiddleware, getProfile);  // unnecessary friction

// CORRECT: only protect state-changing methods (POST, PUT, PATCH, DELETE)
const safeMethods = ['GET', 'HEAD', 'OPTIONS'];
if (safeMethods.includes(req.method)) return next();  // skip CSRF check
```

❌ Mistake 2: Relying only on SameSite cookies without tokens (or vice versa)
```javascript
// WRONG: SameSite=Lax still allows top-level GET navigation with cookies
// (e.g., clicking a malicious link that triggers a state change via GET)
res.cookie('session', token, { sameSite: 'lax' });  // NOT sufficient alone for strong apps

// CORRECT: layer defenses — SameSite cookies AND CSRF tokens AND never
// perform state changes via GET requests in the first place
res.cookie('session', token, { sameSite: 'strict', httpOnly: true, secure: true });
app.use('/api', csrfVerifyMiddleware);  // token check on top
```

---

## 🧠 Tricky Interview Question

```javascript
// Server sets cookie: sameSite: 'lax'
// A malicious site has: <a href="https://bank.com/transfer?to=attacker&amt=1000">Click for prize!</a>
// User clicks it while logged into bank.com. Does the cookie get sent?
```
Answer: **Yes** — `SameSite=Lax` allows cookies on top-level GET navigations (like clicking a link) even cross-site; it only blocks cookies on cross-site **sub-requests** (like `<img>`, `<iframe>`, `fetch` from another site) and cross-site POST forms. This is exactly why state-changing operations must **never** be exposed via GET endpoints — `GET /transfer?to=attacker&amt=1000` is a design flaw regardless of CSRF tokens. The fix: transfers should only be POST (where Lax cookies ARE blocked cross-site) combined with CSRF tokens, and GET requests should be read-only, idempotent, side-effect-free (per HTTP spec).

---

## ⚫ Interview Questions + Answers

Q1: Why doesn't CSRF affect APIs using only `Authorization: Bearer <token>` headers (no cookies)?
A1: CSRF relies on the browser automatically attaching credentials (cookies) to cross-site requests. If auth is done purely via a custom header like `Authorization: Bearer <JWT>` that the attacker's page cannot read or set (because it's stored in JS memory/localStorage, not auto-attached by the browser), there's nothing for the browser to "accidentally" send — the forged request from `evil.com` would have no valid Authorization header. This is why many modern SPAs using Bearer tokens (not cookies) are inherently less exposed to classic CSRF.

Q2: What is the "double-submit cookie" pattern and why is it considered stateless?
A2: The server sets a random token as a (non-httpOnly) cookie; frontend JS reads it and sends it back as a custom header on requests. The server just compares cookie value to header value — no server-side session storage needed to track issued tokens (unlike the synchronizer token pattern which stores tokens per-session). It works because an attacker's cross-site page cannot read cookies set by your domain, so they cannot forge the matching header.

Q3: What's the difference between SameSite=Strict, Lax, and None?
A3: **Strict**: cookie never sent on any cross-site request, including top-level navigation (can break "login persists after clicking email link" flows). **Lax** (default in modern browsers): cookie sent on top-level GET navigations (clicking a link) but blocked on cross-site POST/subresource requests — good balance for most apps. **None**: cookie sent on all cross-site requests (must be paired with `Secure`); needed for legitimate cross-site embeds (e.g., third-party widgets), but offers no CSRF protection by itself.

Q4: Can `Referer`/`Origin` header checking alone prevent CSRF?
A4: It helps as a secondary layer but isn't fully reliable alone: some privacy tools/proxies strip the `Referer` header, and older browsers/certain requests may omit it. The `Origin` header is more consistently present on cross-origin requests. Best practice: use it as a defense-in-depth check alongside CSRF tokens, not as the sole defense.

Q5: Does a JSON API that only accepts `Content-Type: application/json` have any built-in CSRF protection?
A5: Partially yes — classic CSRF via auto-submitting HTML forms can't set `Content-Type: application/json` (forms only support `application/x-www-form-urlencoded`, `multipart/form-data`, `text/plain` without triggering a CORS preflight). If your server strictly requires and validates `Content-Type: application/json`, a simple form-based CSRF attack fails. However, this isn't a complete defense — it's better combined with explicit CSRF tokens, since attack techniques evolve (e.g., using `fetch` with `mode: 'no-cors'` has its own limitations, but relying on Content-Type alone is fragile).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Your app uses cookie-based sessions/authentication for any state-changing (POST/PUT/DELETE) endpoint.
- Server-rendered forms (traditional MVC apps) are especially vulnerable — always include CSRF tokens there.

❌ Avoid when:
- Pure stateless APIs using only Bearer tokens in headers (no cookies) for auth — CSRF risk is much lower, though still validate Origin for extra safety.
- Public, read-only GET endpoints with no side effects — no CSRF protection needed (and none should be needed if GET truly has no side effects).

---

## 📊 Visual Diagram

```
CSRF ATTACK (without protection):
──────────────────────────────────────────────────────────

  User logged into bank.com (has session cookie)
       │
       ▼
  User visits evil.com (hidden auto-submit form)
       │
       ▼
  Browser auto-submits: POST bank.com/transfer
       + cookie: session=abc123  (browser attaches automatically!)
       │
       ▼
  bank.com sees valid session → processes transfer ❌ MONEY MOVED

WITH CSRF TOKEN PROTECTION:
──────────────────────────────────────────────────────────

  bank.com page loads → server embeds csrf_token=XYZ in form
       │
  evil.com form has NO access to XYZ (same-origin policy blocks reading it)
       │
  evil.com submits request WITHOUT valid csrf_token
       │
       ▼
  bank.com: token missing/invalid → 403 Forbidden ✅ ATTACK BLOCKED
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CSRF token | Unique per-session token to verify request origin | Request origin verify करने वाला unique token |
| SameSite cookie | Cookie attribute restricting cross-site sending | Cross-site भेजने को restrict करने वाला cookie attribute |
| Double-submit cookie | Stateless CSRF pattern: cookie + header match | Stateless CSRF pattern |
| Synchronizer token | Server-stored CSRF token per session | Session के लिए server-stored token |
| Safe method | HTTP method with no side effects (GET/HEAD) | बिना side-effect वाला method |
| Forged request | Attacker-triggered request using victim's cookies | Victim की cookies से बना fake request |

---

## ⚡ 3-Line Summary
English:
1. CSRF exploits the browser's automatic cookie attachment to trick a logged-in user's browser into sending unwanted state-changing requests.
2. Defend with CSRF tokens (synchronizer or double-submit-cookie pattern) plus `SameSite=Strict/Lax` cookies.
3. Never perform state changes via GET requests; always verify CSRF tokens on POST/PUT/PATCH/DELETE routes.

Hindi:
1. CSRF browser के automatic cookie attachment का फायदा उठाकर logged-in user से unwanted requests भेजता है।
2. CSRF tokens (synchronizer या double-submit-cookie pattern) और `SameSite=Strict/Lax` cookies से defend करो।
3. GET requests से कभी state change मत करो; POST/PUT/PATCH/DELETE पर token verify करो।

---

## ➡️ Next Topic
**133. XSS Prevention in Node** — Cross-Site Scripting attacks से बचाव, output encoding और CSP।
