---

# 066. CSRF — Cross-Site Request Forgery (Complete Guide)
# हिंदी में: CSRF — दूसरी Site से User के नाम पर Request करना
# Risk Level: ⛔ High

---

## 🔵 Simple Definition (English)
CSRF (Cross-Site Request Forgery) tricks an authenticated user's browser into sending unintended requests to a trusted website. The attacker doesn't steal credentials — they exploit the fact that browsers automatically attach cookies to requests. The victim doesn't know a request was made on their behalf.

## 🔵 सरल परिभाषा (Hindi)
CSRF में attacker एक malicious page बनाता है जो victim के browser से trusted site पर request भेजता है। Browser automatically उस site की cookies attach कर देता है — इसलिए server को लगता है request legitimate user ने की है। Victim को कुछ पता नहीं चलता।

---

## ⚠️ The Attack / Threat

```
CSRF Attack Flow:
─────────────────────────────────────────────────────────
Step 1: Victim logs in to bank.com → gets session cookie
        Cookie: session=abc123; HttpOnly

Step 2: Victim visits attacker's page evil.com
        (via phishing link, malicious ad, etc.)

Step 3: evil.com has hidden HTML:
        <form action="https://bank.com/transfer" method="POST">
          <input name="amount" value="10000">
          <input name="to" value="attacker_account">
        </form>
        <script>document.forms[0].submit()</script>

Step 4: Browser automatically submits form to bank.com
        WITH victim's session cookie attached!

Step 5: Bank server sees valid session cookie → processes transfer
        Victim loses $10,000 ☠️

Also works with GET requests (worse!):
<img src="https://bank.com/transfer?amount=10000&to=attacker">
→ Loading the image triggers the GET request with cookies!

Modern variant — JSON CSRF:
<script>
  fetch('https://api.site.com/user/delete', {
    method: 'POST',
    credentials: 'include',  // sends cookies cross-origin
    body: JSON.stringify({id: 123}),
    headers: {'Content-Type': 'text/plain'}  // bypasses CORS preflight!
  })
</script>
```

## ⚠️ हमला कैसे होता है? (Hindi)
Attacker एक page बनाता है जिसमें hidden form है जो bank.com पर money transfer करती है। Victim जब वो page visit करता है, form automatically submit हो जाती है। Browser victim की bank cookies automatically attach कर देता है — bank को लगता है user ने खुद transfer किया।

---

## 💀 Real World Breach Example
**Netflix (2006):** CSRF vulnerability allowed attackers to change victim's email and DVD rental queue by sending crafted requests to Netflix APIs. Users who visited malicious sites had their accounts hijacked without any interaction.

**Gmail (2007):** CSRF in Gmail allowed attackers to create email filters that forwarded all emails to attacker's address. Victims visited a page that silently created the filter in their Gmail account.

**Twitter (2010):** "Tweet Bombing" — CSRF allowed posting tweets from victim's account without their knowledge. Exploited via malicious images embedded in websites.

---

## 🛡️ How to Prevent — Step by Step

```
Step 1: CSRF Tokens — unique unpredictable token per session/form
Step 2: SameSite cookie attribute — Strict or Lax
Step 3: Check Origin/Referer headers server-side
Step 4: Double Submit Cookie pattern (for APIs)
Step 5: Use custom request headers (X-Requested-With) for XHR
Step 6: Re-authenticate for sensitive actions (confirm password)
Step 7: Short session timeouts
Step 8: Never use GET for state-changing operations
```

---

## 💻 Vulnerable Code (What NOT to do)

```javascript
// ❌ VULNERABLE CODE

// ─── Express — No CSRF protection ────────────────────────────
app.post('/transfer', (req, res) => {
  const { amount, toAccount } = req.body;
  // ❌ Only checks if user is logged in (session cookie)
  // ❌ No CSRF token check — anyone can forge this request!
  if (req.session.userId) {
    transferMoney(req.session.userId, toAccount, amount);
    res.json({ success: true });
  }
});

// ❌ Session cookie without SameSite attribute:
app.use(session({
  secret: 'secret',
  cookie: {
    httpOnly: true,
    secure: true
    // ❌ Missing SameSite! Default is 'None' — sends cookie cross-origin
  }
}));

// ❌ Using GET for state-changing operations:
app.get('/delete-account', (req, res) => {
  // <img src="https://app.com/delete-account"> triggers this!
  deleteAccount(req.session.userId);
});
```

---

## 💻 Secure Code (What TO do)

```javascript
// ✅ SECURE CODE

// ─── Method 1: CSRF Token (Most Reliable) ────────────────────
const csrf = require('csurf');
const cookieParser = require('cookie-parser');

app.use(cookieParser());
app.use(csrf({ cookie: true }));  // or session-based: csrf({ sessionKey: 'session' })

// Server sends token with each form:
app.get('/transfer-form', (req, res) => {
  res.render('transfer', { csrfToken: req.csrfToken() });
  // In template: <input type="hidden" name="_csrf" value="<%= csrfToken %>">
});

// Server verifies token on POST (csurf middleware does this automatically):
app.post('/transfer', (req, res) => {
  // csurf middleware already verified _csrf matches server-generated token
  // If token missing/wrong → 403 ForbiddenError thrown
  transferMoney(req.session.userId, req.body.toAccount, req.body.amount);
  res.json({ success: true });
});

// Error handler for CSRF token failures:
app.use((err, req, res, next) => {
  if (err.code === 'EBADCSRFTOKEN') {
    return res.status(403).json({ error: 'Invalid CSRF token' });
  }
  next(err);
});

// ─── Method 2: SameSite Cookie (Simpler, Modern) ──────────────
app.use(session({
  secret: process.env.SESSION_SECRET,
  cookie: {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',   // ✅ CSRF protection: cookie NOT sent cross-origin
    // sameSite: 'lax'    // Safer default: blocks POST/PUT/DELETE, allows GET navigation
    // sameSite: 'none'   // Sends cross-origin (requires Secure) — AVOID for auth cookies
    maxAge: 60 * 60 * 1000  // 1 hour
  }
}));

// SameSite differences:
// 'strict' — cookie never sent from cross-site requests (safest, breaks OAuth flows)
// 'lax'    — cookie sent for top-level navigation (GET links), not for subresource requests
// 'none'   — cookie sent cross-origin (must also set Secure: true)

// ─── Method 3: Origin/Referer Header Check ────────────────────
function csrfOriginCheck(req, res, next) {
  const origin = req.headers.origin || req.headers.referer;
  const allowedOrigins = [
    'https://myapp.com',
    'https://www.myapp.com'
  ];
  
  // State-changing requests must come from our origin:
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(req.method)) {
    if (!origin || !allowedOrigins.some(o => origin.startsWith(o))) {
      return res.status(403).json({ error: 'CSRF: Invalid origin' });
    }
  }
  next();
}
app.use(csrfOriginCheck);

// ─── Method 4: Custom Header (For APIs / SPA) ─────────────────
// Custom headers can't be set cross-origin without CORS preflight!
// Attacker's form can't add custom headers — HTML forms send only standard headers.

// Client (React/Vue/Angular):
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
// Or using a custom header:
axios.defaults.headers.common['X-CSRF-Token'] = getCsrfTokenFromMeta();

// Server:
function requireCustomHeader(req, res, next) {
  const xRequestedWith = req.headers['x-requested-with'];
  if (!xRequestedWith || xRequestedWith !== 'XMLHttpRequest') {
    return res.status(403).json({ error: 'CSRF: Missing custom header' });
  }
  next();
}

// ─── NestJS — CSRF Protection ────────────────────────────────
import { NestFactory } from '@nestjs/core';
import * as csurf from 'csurf';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // SameSite via cookie session:
  app.use(session({
    secret: process.env.SESSION_SECRET,
    cookie: {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
    }
  }));
  
  // CSRF token for form-based routes:
  app.use(csurf({ cookie: true }));
  
  await app.listen(3000);
}

// ─── React SPA + JWT — CSRF less of a concern ────────────────
// JWTs in localStorage: no automatic cookie attachment → not vulnerable to CSRF
// BUT: localStorage is XSS-vulnerable!
// JWTs in httpOnly cookies: CSRF-vulnerable → use SameSite=Strict + CSRF token

// Double Submit Cookie Pattern (stateless CSRF for APIs):
// 1. Server sets a CSRF cookie (non-httpOnly): Set-Cookie: csrf=TOKEN123
// 2. JavaScript reads the cookie and adds it as a header: X-CSRF-Token: TOKEN123
// 3. Server compares cookie value to header value
// Attacker can't read the cookie (same-origin policy) → can't set the header
```

---

## 🟠 Implementation in My Stack

```javascript
// ─── NestJS + JWT (modern SPA approach) ──────────────────────
// main.ts

// Option 1: JWT in httpOnly cookie (most secure) + SameSite
app.use(cookieParser());
app.use(helmet());

// CSRF protection via SameSite cookie + Origin check:
// NestJS CORS already checks Origin header

// Option 2: JWT in Authorization header (SPA approach — no CSRF)
// Client: Authorization: Bearer <token>
// No cookies → no CSRF risk
// Vulnerable to XSS (localStorage) — must have strict CSP

// ─── Next.js — CSRF protection ────────────────────────────────
// next.config.js — check origin in API routes:
// pages/api/transfer.ts
export default function handler(req, res) {
  const origin = req.headers.origin;
  
  if (req.method === 'POST' && origin !== 'https://myapp.com') {
    return res.status(403).json({ error: 'CSRF check failed' });
  }
  // process...
}

// Using next-csrf library:
import { createCsrfProtect } from '@edge-csrf/nextjs';
const csrfProtect = createCsrfProtect({ cookie: { secure: true } });
```

---

## 🔧 Security Tools + Libraries
| Tool | Purpose | Use |
|------|---------|-----|
| `csurf` (Express) | CSRF token middleware | `app.use(csrf())` |
| `@edge-csrf/nextjs` | CSRF for Next.js | Middleware-based |
| SameSite cookies | Browser-level CSRF protection | Cookie attribute |
| Origin header check | Validate request source | Server-side middleware |
| OWASP ZAP | CSRF vulnerability scanner | CI/CD testing |

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between CSRF and XSS?**
A1: **XSS** injects malicious code that runs in the victim's browser on the legitimate site — attacker needs to inject code. **CSRF** tricks the browser into sending requests using the victim's existing credentials — no code injection needed. XSS is about executing code you inject; CSRF is about forging requests using the victim's identity. XSS can enable CSRF (injected script can make authenticated requests), but they're separate vulnerabilities. Key defense overlap: both benefit from SameSite cookies and custom headers.

**Q2: Does HTTPS prevent CSRF?**
A2: No. CSRF doesn't require reading the response or intercepting traffic — it just needs the browser to send a request with the victim's cookies attached. HTTPS protects against eavesdropping (man-in-the-middle) but doesn't prevent the browser from including cookies in cross-site requests. The same CSRF attack works identically over HTTPS.

**Q3: What is SameSite=Lax vs Strict and which should I use?**
A3: **Strict** — cookie is never sent in cross-site requests, including when navigating from another site via a link. Safest, but breaks OAuth flows (user clicks Google login → redirects to your app, but cookie is not sent on that navigation). **Lax** — cookie sent for top-level navigations (user clicks a link) but NOT for cross-origin subresource requests (forms, XHR, images). Recommended default. Blocks CSRF POST forms but allows OAuth callbacks. **Recommendation**: use `Lax` for session cookies, `Strict` for sensitive actions (payment, admin), `None` only for third-party integrations (require `Secure`).

**Q4: How does a CSRF token work and why can an attacker not forge it?**
A4: A CSRF token is a random, unpredictable value generated by the server and tied to the user's session. It's embedded in each form as a hidden field (or returned in a cookie/header). On form submission, the server verifies the submitted token matches the session token. An attacker on `evil.com` cannot read the contents of `bank.com`'s pages (same-origin policy) — so they can't extract the CSRF token from the form. They can forge the request URL and method, but not the CSRF token. Key: the token must be unique per session, stored server-side, and validated on every state-changing request.

**Q5: Are SPAs with JWTs still vulnerable to CSRF?**
A5: It depends on where the JWT is stored. If JWT is in **localStorage** and sent via `Authorization: Bearer` header — NOT vulnerable to CSRF (JavaScript must explicitly add the header, which cross-origin scripts can't do for custom headers without CORS allowing it). But localStorage is XSS-vulnerable. If JWT is in **httpOnly cookie** — potentially CSRF-vulnerable (browser auto-sends cookie). Solution: combine httpOnly cookies with `SameSite=Strict` and a CSRF token, or use `Authorization` header with tokens stored in memory (lost on page refresh — common SPA tradeoff).

---

## ✅ Security Checklist
```
□ CSRF tokens on all state-changing form submissions
□ SameSite=Lax (minimum) on all session/auth cookies
□ HttpOnly + Secure on all auth cookies
□ Origin/Referer header checked on POST/PUT/DELETE endpoints
□ Custom request header (X-Requested-With) required for XHR APIs
□ GET endpoints never change state (no delete, no update)
□ Short session timeouts for sensitive operations
□ Re-authentication required for high-risk actions (password change, transfer)
□ CSRF scanning in CI/CD (OWASP ZAP)
□ Double Submit Cookie pattern if stateless CSRF protection needed
□ No wildcard CORS (Access-Control-Allow-Origin: *) with credentials
```

---

## 📊 Visual Diagram

```
WITHOUT CSRF PROTECTION:
evil.com → hidden form → bank.com/transfer + cookies ✓ → money transferred ☠️

WITH CSRF TOKEN:
evil.com → hidden form → bank.com/transfer + cookies ✓ + no CSRF token ✗
                                                               ↓
                                               Server rejects: 403 Forbidden

WITH SameSite=Strict:
evil.com → POST bank.com/transfer → browser does NOT send bank.com cookie
                                              ↓
                               Server: no session → 401 Unauthorized

TOKEN FLOW:
GET /transfer-form → Server sends: hidden _csrf=TOKEN123
                                    ↓
User fills form → POST /transfer with _csrf=TOKEN123
                                    ↓
Server: session token = TOKEN123? ✓ → process
                                  ✗ → 403 Forbidden
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CSRF | Cross-Site Request Forgery | दूसरी site से forged request |
| CSRF Token | Unpredictable value per session | Session के साथ unique secret |
| SameSite | Cookie restriction attribute | Cross-site cookie भेजने की limit |
| Double Submit | Cookie value = header value | Stateless CSRF check |
| Origin Header | Request source domain | Request किस site से आई |
| Preflight | Browser CORS check for custom headers | Custom headers cross-origin नहीं जाते |

---

## ⚡ 3-Line Summary
**English:**
1. CSRF tricks the victim's browser into sending authenticated requests to a trusted site — no code injection needed, just a forged request from a malicious page.
2. Prevention: CSRF tokens (server validates unpredictable value), SameSite=Lax cookies (browser won't send cookies on cross-site requests), custom request headers for APIs.
3. Modern SPA with Authorization header + JWT is inherently CSRF-safe; cookies require SameSite + CSRF tokens.

**Hindi:**
1. CSRF victim के browser को trusted site पर forged request भेजने के लिए trick करता है।
2. Fix: CSRF token हर form में, SameSite=Lax cookies, API के लिए custom headers।
3. JWT Authorization header में रखो — CSRF नहीं होता; cookies हों तो SameSite=Strict + CSRF token।

---

## 🚨 Red Flag Signs
- Session cookies without `SameSite` attribute (defaults to `None` in older browsers)
- GET endpoints that delete, transfer, or modify data
- Forms without CSRF tokens
- `Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true`
- No `Origin`/`Referer` check on state-changing API endpoints
- Session tokens in URL parameters (not cookies) — different problem but related

---

## ➡️ Next Topic
**097. JWT Security** — Algorithm confusion attacks, weak secrets, `alg:none` vulnerability, token storage security, refresh token patterns.
