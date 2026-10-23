---

# 163. Helmet.js — Security Headers Complete Guide
# हिंदी में: Helmet.js — HTTP Security Headers का पूरा Setup
# Risk Level: ⚠️ Medium-High

---

## 🔵 Simple Definition (English)
Helmet.js is a Node.js middleware that sets HTTP security response headers. Each header tells the browser how to handle the page — what content to load, whether it can be framed, how to handle MIME types, what referrer to send, etc. A single `app.use(helmet())` line sets 15 headers that prevent a wide range of attacks.

## 🔵 सरल परिभाषा (Hindi)
Helmet.js एक middleware है जो HTTP response headers set करता है। ये headers browser को बताते हैं कि page को कैसे handle करे — कौन सी scripts load होंगी, page frame हो सकता है या नहीं, MIME type trust करे या नहीं। `app.use(helmet())` एक line में 15 security headers set हो जाती हैं।

---

## ⚠️ The Attack / Threat

```
WITHOUT SECURITY HEADERS — What attackers can do:

No CSP:           → XSS scripts load from external domains
No X-Frame-Options → Clickjacking — your page inside attacker's iframe
No HSTS:          → SSL stripping — HTTPS downgraded to HTTP
No X-Content-Type → MIME sniffing — JS disguised as image executes
No Referrer-Policy → URLs with sensitive params leaked in Referer header

Example — Clickjacking without X-Frame-Options:
<!-- attacker's page: evil.com -->
<iframe src="https://bank.com/transfer" style="opacity:0; position:absolute; top:0; left:0;"></iframe>
<button style="position:absolute; top:100px; left:50px;">Win a Prize!</button>
→ User clicks "Win a Prize" → actually clicks bank.com's transfer button!

Example — MIME Sniffing without X-Content-Type-Options:
Attacker uploads a .jpg file that is actually JS
Server serves it with Content-Type: image/jpeg
IE/old browsers "sniff" the content: "this looks like JS, run it!"
→ XSS via image upload bypass
```

---

## 💻 Vulnerable Code (What NOT to do)

```javascript
// ❌ VULNERABLE — No security headers

const express = require('express');
const app = express();

// Default Express response headers:
// X-Powered-By: Express  ← reveals technology stack
// No CSP                 ← XSS risk
// No HSTS               ← SSL stripping risk
// No X-Frame-Options    ← clickjacking risk
// No X-Content-Type     ← MIME sniffing risk

app.get('/', (req, res) => {
  res.send('<html><body>No security headers!</body></html>');
});
// curl -I http://localhost
// Response: X-Powered-By: Express  ← tells attacker "this is Express"
// → No CSP, HSTS, X-Frame-Options, etc.
```

---

## 💻 Secure Code (What TO do)

```javascript
// ✅ SECURE — Full Helmet.js Setup

const express = require('express');
const helmet = require('helmet');
const app = express();

// ─── Option 1: Default Helmet (Good starting point) ──────────
app.use(helmet());
// Sets these headers automatically:
// Content-Security-Policy: default-src 'self';script-src 'self';...
// Cross-Origin-Embedder-Policy: require-corp
// Cross-Origin-Opener-Policy: same-origin
// Cross-Origin-Resource-Policy: same-origin
// X-DNS-Prefetch-Control: off
// X-Frame-Options: SAMEORIGIN
// Strict-Transport-Security: max-age=15552000; includeSubDomains
// X-Download-Options: noopen
// X-Content-Type-Options: nosniff
// X-Permitted-Cross-Domain-Policies: none
// Referrer-Policy: no-referrer
// X-XSS-Protection: 0 (disabled — modern browsers use CSP instead)
// Removes X-Powered-By header

// ─── Option 2: Custom Configuration (Production-grade) ────────
app.use(helmet({
  
  // ── Content Security Policy ───────────────────────────────
  contentSecurityPolicy: {
    directives: {
      defaultSrc:  ["'self'"],
      scriptSrc:   ["'self'", "'nonce-RANDOM'"],   // nonce for inline scripts
      styleSrc:    ["'self'", "'unsafe-inline'"],   // allow inline styles
      imgSrc:      ["'self'", 'data:', 'https:'],  // allow HTTPS images
      connectSrc:  ["'self'", 'https://api.myapp.com'],
      fontSrc:     ["'self'", 'https://fonts.gstatic.com'],
      objectSrc:   ["'none'"],        // no Flash/plugins
      mediaSrc:    ["'self'"],
      frameSrc:    ["'none'"],        // no iframes from external
      frameAncestors: ["'none'"],     // can't be iframed (clickjacking)
      formAction:  ["'self'"],        // forms can only POST to same origin
      upgradeInsecureRequests: [],    // auto-upgrade HTTP→HTTPS subresources
      reportUri:   ['/csp-violation'] // receive violation reports
    },
    reportOnly: false,  // enforce (not just report)
  },
  
  // ── HTTP Strict Transport Security ────────────────────────
  // Forces HTTPS for all future visits — browser refuses HTTP
  hsts: {
    maxAge: 63072000,           // 2 years (in seconds) — HSTS preload requirement
    includeSubDomains: true,    // applies to all subdomains
    preload: true               // submit to browser HSTS preload lists
  },
  
  // ── Referrer Policy ───────────────────────────────────────
  // Controls what's sent in Referer header when user clicks links
  referrerPolicy: {
    policy: 'strict-origin-when-cross-origin'
    // 'strict-origin': sends only origin (no path) for cross-origin
    // 'no-referrer': sends nothing — most private
    // 'same-origin': sends full URL within same origin, nothing cross-origin
  },
  
  // ── Cross-Origin Policies ─────────────────────────────────
  crossOriginEmbedderPolicy: { policy: 'require-corp' },
  crossOriginOpenerPolicy: { policy: 'same-origin' },
  crossOriginResourcePolicy: { policy: 'same-site' },  // or 'same-origin'
  
  // ── Other ─────────────────────────────────────────────────
  xFrameOptions: { action: 'deny' },    // no framing at all (vs SAMEORIGIN)
  xContentTypeOptions: true,             // nosniff — always leave on!
  dnsPrefetchControl: { allow: false },  // disable DNS prefetch
  xDownloadOptions: true,                // noopen for IE downloads
  xPermittedCrossDomainPolicies: { permittedPolicies: 'none' },
  
  // ── Remove X-Powered-By ───────────────────────────────────
  hidePoweredBy: true,  // removes "X-Powered-By: Express"
}));

// ─── CSP Violation Reporting Endpoint ─────────────────────────
app.post('/csp-violation', express.json({ type: 'application/csp-report' }), (req, res) => {
  console.log('CSP Violation:', JSON.stringify(req.body, null, 2));
  // Send to logging service (DataDog, Sentry, etc.)
  res.status(204).send();
});

// ─── CSP with Nonces (for inline scripts) ─────────────────────
const crypto = require('crypto');

app.use((req, res, next) => {
  res.locals.nonce = crypto.randomBytes(16).toString('base64');
  next();
});

app.use(
  helmet.contentSecurityPolicy({
    directives: {
      scriptSrc: ["'self'", (req, res) => `'nonce-${res.locals.nonce}'`],
    },
  })
);

// In template:
// <script nonce="<%= nonce %>">/* inline script safe with matching nonce */</script>

// ─── Per-Route CSP Override ────────────────────────────────────
// Some routes need different policies (e.g., embedding a payment iframe)
app.get('/embed', 
  helmet.contentSecurityPolicy({
    directives: {
      frameAncestors: ["'self'", 'https://trusted-partner.com'],
    }
  }),
  (req, res) => res.render('embed')
);
```

---

## 🟠 Implementation in My Stack

```typescript
// ─── NestJS + Helmet ──────────────────────────────────────────
// main.ts
import { NestFactory } from '@nestjs/core';
import helmet from 'helmet';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  app.use(helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", 'data:', 'https:'],
        connectSrc: ["'self'"],
        objectSrc: ["'none'"],
        frameAncestors: ["'none'"],
        upgradeInsecureRequests: [],
      },
    },
    hsts: {
      maxAge: 63072000,
      includeSubDomains: true,
      preload: true,
    },
    referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
  }));
  
  await app.listen(3000);
}

// ─── Next.js — Security Headers ───────────────────────────────
// next.config.js
const securityHeaders = [
  { key: 'X-DNS-Prefetch-Control', value: 'on' },
  { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline'",  // Next.js needs unsafe-eval in dev
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' blob: data: https:",
      "font-src 'self'",
      "object-src 'none'",
      "frame-ancestors 'none'",
      "connect-src 'self' https://api.myapp.com",
    ].join('; ')
  }
];

module.exports = {
  async headers() {
    return [{ source: '/(.*)', headers: securityHeaders }];
  }
};

// ─── Nginx — Security Headers ─────────────────────────────────
/*
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "0" always;  # Disabled — CSP is better
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; object-src 'none';" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
server_tokens off;  # Hides nginx version
*/
```

---

## 🔧 Security Headers Reference
| Header | What it does | Key value |
|--------|-------------|-----------|
| `Content-Security-Policy` | Controls what can load/execute | `default-src 'self'` |
| `Strict-Transport-Security` | Force HTTPS | `max-age=63072000; includeSubDomains` |
| `X-Frame-Options` | Prevent clickjacking | `DENY` or `SAMEORIGIN` |
| `X-Content-Type-Options` | Stop MIME sniffing | `nosniff` |
| `Referrer-Policy` | Control Referer header | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | Disable browser features | `camera=(), microphone=()` |
| `Cross-Origin-*` | Isolate cross-origin resources | Various policies |

---

## ⚫ Interview Questions + Answers

**Q1: What is clickjacking and how does X-Frame-Options prevent it?**
A1: Clickjacking places a transparent or hidden iframe of the victim site over a fake page. The victim thinks they're clicking a button on the attacker's page, but actually clicking on the victim site's UI inside the iframe — approving a transfer, changing email, etc. `X-Frame-Options: DENY` instructs browsers to refuse to render the page inside any `<frame>` or `<iframe>`. `SAMEORIGIN` allows framing by the same origin only. Modern alternative: `Content-Security-Policy: frame-ancestors 'none'` — more flexible and supersedes X-Frame-Options in browsers that support CSP.

**Q2: What is HSTS and why does it need a long max-age?**
A2: HTTP Strict Transport Security tells browsers "for the next N seconds, always use HTTPS for this domain — even if the user types http://". It prevents SSL stripping attacks where a MITM downgrades HTTPS to HTTP. The max-age should be long (63072000 = 2 years) because: (1) Browsers cache HSTS for that duration — short max-age means frequent re-validation. (2) HSTS preload lists require 1+ year max-age — once on the preload list, the browser knows to use HTTPS before ever making an HTTP request. Caveat: if you ever need to go back to HTTP (e.g., migrating away from a domain), a long max-age means some users will be stuck trying HTTPS for that period.

**Q3: Why do modern browsers recommend setting X-XSS-Protection: 0?**
A3: The old `X-XSS-Protection` header enabled a browser's built-in XSS filter (IE/Chrome). These filters had their own vulnerabilities — they could be exploited to block legitimate content or even introduce new XSS vectors through "reflected XSS filter bypass." Modern browsers like Chrome and Edge have removed their XSS Auditor entirely. Helmet.js now sets `X-XSS-Protection: 0` to disable the filter. The proper XSS defense is a well-configured `Content-Security-Policy` — not the deprecated XSS auditor.

**Q4: What is MIME type sniffing and how does X-Content-Type-Options: nosniff prevent it?**
A4: MIME sniffing is when browsers ignore the server's `Content-Type` header and "sniff" (inspect) the file content to determine its type. Scenario: attacker uploads a `.jpg` that is actually JavaScript. Server returns it with `Content-Type: image/jpeg`. A browser without nosniff might detect "this looks like JS" and execute it as a script — even though the server said it's an image. `X-Content-Type-Options: nosniff` tells the browser: trust the Content-Type, don't sniff, never execute a file differently from what the server declared. This also blocks cross-origin reads of certain resource types in some browsers.

**Q5: How do you handle CSP violations in production?**
A5: Use the `report-uri` or `report-to` directive in your CSP: `Content-Security-Policy: ...; report-uri /csp-violation`. Browser sends a JSON report to that endpoint whenever a violation occurs (blocked script load, blocked inline script, etc.). Set up a collection endpoint that logs violations to your observability stack (DataDog, Sentry, ELK). Use `Content-Security-Policy-Report-Only: ...` first — same policy but only reports, doesn't block. This lets you identify what would break before enforcing. After tuning (adding legitimate sources to the whitelist), switch to enforcing mode. Common false positives: browser extensions, password managers injecting scripts — filter those from your reports.

---

## ✅ Security Checklist
```
□ helmet() middleware installed and active
□ Content-Security-Policy set (default-src 'self', no unsafe-inline for scripts)
□ HSTS enabled with 1+ year max-age + includeSubDomains
□ X-Frame-Options: DENY (or frame-ancestors 'none' in CSP)
□ X-Content-Type-Options: nosniff
□ Referrer-Policy: strict-origin-when-cross-origin
□ X-Powered-By header removed (hidePoweredBy: true)
□ Permissions-Policy restricts camera, microphone, geolocation
□ CSP report-uri configured for violation monitoring
□ CSP-Report-Only mode used before enforcing new policies
□ No unsafe-eval in script-src (except where explicitly needed)
□ Server version not exposed (server_tokens off in nginx)
```

---

## 📊 Visual Diagram

```
WITHOUT HELMET:
HTTP Response:
  X-Powered-By: Express  ← tech stack exposed
  (no CSP)              ← XSS scripts can load from anywhere
  (no X-Frame-Options)  ← clickjacking possible
  (no HSTS)             ← SSL stripping possible
  (no nosniff)          ← MIME sniffing possible

WITH HELMET:
HTTP Response:
  Content-Security-Policy: default-src 'self'; script-src 'self'; ...
  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Cross-Origin-Embedder-Policy: require-corp
  Cross-Origin-Opener-Policy: same-origin
  (X-Powered-By removed)

CSP NONCE FLOW:
Request → Server generates random nonce → includes in CSP header AND script tag
Browser: <script nonce="abc123"> matches CSP nonce-abc123 → ALLOWED ✅
Attacker's injected: <script>evil()</script> → no matching nonce → BLOCKED ✅
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CSP | Content Security Policy — controls what loads | कौन सी resources load हो सकती हैं |
| HSTS | HTTP Strict Transport Security — force HTTPS | HTTPS को mandatory बनाना |
| Clickjacking | Trick click via hidden iframe | Invisible iframe से click trick करना |
| MIME Sniffing | Browser guesses content type | Browser Content-Type को ignore करे |
| Nonce | One-time random value for CSP | Inline script को safe mark करने का token |
| X-Frame-Options | Prevent iframing | Page को iframe में load होने से रोकना |
| report-uri | CSP violation reporting endpoint | CSP violations का log रखना |

---

## ⚡ 3-Line Summary
**English:**
1. Helmet.js sets 15 HTTP security headers in one middleware call, protecting against XSS, clickjacking, SSL stripping, MIME sniffing, and information disclosure.
2. Critical headers: CSP (control what executes), HSTS (force HTTPS), X-Frame-Options (no clickjacking), X-Content-Type-Options (no MIME sniffing).
3. Use CSP-Report-Only first to discover violations, then enforce — and remove X-Powered-By to avoid advertising your tech stack.

**Hindi:**
1. Helmet.js एक line में 15 security headers set करता है — XSS, clickjacking, SSL stripping, MIME sniffing से protection।
2. Critical: CSP (क्या execute हो), HSTS (force HTTPS), X-Frame-Options (clickjacking नहीं), nosniff (MIME sniffing नहीं)।
3. पहले CSP-Report-Only use करो violations देखने के लिए, फिर enforce करो। X-Powered-By हटाओ।

---

## 🚨 Red Flag Signs
- No `helmet()` middleware in Express/NestJS app
- `X-Powered-By: Express` in response headers (stack fingerprinting)
- No `Content-Security-Policy` header
- CSP with `unsafe-eval` and `unsafe-inline` both — defeats the purpose
- No `Strict-Transport-Security` header on production HTTPS site
- `X-Frame-Options` missing (clickjacking risk)
- `Access-Control-Allow-Origin: *` with sensitive API endpoints

---

## ➡️ Next Topic
**171. CORS Security** — Same-origin policy, preflight requests, CORS misconfigurations, wildcard origins with credentials, and secure CORS setup.
