# 135. Helmet.js — All Headers Explained
# हिंदी में: Helmet.js — सभी Headers समझो

---

## 🔵 Simple Definition (English)
**Helmet.js** is an Express middleware that sets a collection of HTTP security headers automatically, protecting against common web vulnerabilities (clickjacking, MIME sniffing, XSS, etc.) with a single `app.use(helmet())` call. It's a bundle of 15 smaller middlewares, each setting one specific header.

## 🔵 सरल परिभाषा (Hindi)
**Helmet.js** एक Express middleware है जो automatically कई HTTP security headers set करता है, common web vulnerabilities (clickjacking, MIME sniffing, XSS) से बचाता है, सिर्फ एक `app.use(helmet())` call से। यह 15 छोटे middlewares का bundle है, हर एक specific header set करता है।

---

## 🔴 Problem it Solves
By default, Express sends minimal security headers, and browsers have many optional protections that only activate when the SERVER explicitly sends the right headers (e.g., `X-Frame-Options` to prevent clickjacking, `Strict-Transport-Security` to force HTTPS). Manually remembering and correctly configuring 10-15 security headers for every project is tedious and error-prone. Helmet packages sensible, well-researched defaults into one line, while still allowing fine-grained customization per header.

## 🔴 यह क्यों बना? (Hindi)
Default रूप से Express minimal security headers भेजता है, और browsers के कई optional protections सिर्फ तब activate होते हैं जब SERVER explicitly सही headers भेजे। हर project में manually 10-15 security headers याद रखकर configure करना tedious और error-prone है। Helmet sensible defaults को एक line में package करता है, फिर भी fine-grained customization allow करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `npm install helmet`, add `app.use(helmet())` early in middleware stack (before routes)
Step 2 → Helmet internally calls a set of sub-middlewares, each adding/modifying a specific response header
Step 3 → `contentSecurityPolicy` → sets `Content-Security-Policy` restricting script/style/resource sources
Step 4 → `hsts` → sets `Strict-Transport-Security`, forcing browsers to only use HTTPS for future requests
Step 5 → `frameguard` → sets `X-Frame-Options: DENY`, preventing the page from being embedded in an `<iframe>` (clickjacking defense)
Step 6 → `noSniff` → sets `X-Content-Type-Options: nosniff`, stopping browsers from guessing content-type (MIME sniffing attacks)
Step 7 → `hidePoweredBy` → removes `X-Powered-By: Express` header, hiding tech stack fingerprint from attackers
Step 8 → Each sub-middleware can be disabled/customized individually: `helmet({ contentSecurityPolicy: false })`

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `npm install helmet`, `app.use(helmet())` early middleware में add करो
Step 2 → Helmet internally कई sub-middlewares call करता है
Step 3 → `contentSecurityPolicy` → script/style sources restrict करता है
Step 4 → `hsts` → HTTPS force करता है
Step 5 → `frameguard` → clickjacking रोकता है
Step 6 → `noSniff` → MIME sniffing रोकता है
Step 7 → `hidePoweredBy` → tech stack hide करता है
Step 8 → हर sub-middleware individually customize हो सकता है

---

## 🟡 Real World Example
**Razorpay's checkout page:** Must prevent being embedded in a hidden iframe on a phishing site (clickjacking attack tricking users into clicking "Pay" unknowingly) — `X-Frame-Options: DENY` / `frame-ancestors 'none'` in CSP stops this. Must force HTTPS always for payment pages — `Strict-Transport-Security` ensures even if a user types `http://` by mistake, the browser auto-upgrades to HTTPS before sending any data. Must prevent tech-stack fingerprinting that helps attackers target known Express/Node vulnerabilities — `hidePoweredBy` removes that hint.

## 🟡 Real Example Hindi mein
**Razorpay का checkout page:** Hidden iframe में embed होने से बचना ज़रूरी है (clickjacking) — `X-Frame-Options: DENY` यह रोकता है। Payment pages पर हमेशा HTTPS force करना ज़रूरी है — `Strict-Transport-Security` यह सुनिश्चित करता है। Tech-stack fingerprinting रोकने के लिए `hidePoweredBy` header हटाता है।

---

## 💻 Code Example — Basic

```javascript
// helmet-basic.js
// Run with: node helmet-basic.js, then curl -I http://localhost:3000

const express = require('express');
const helmet = require('helmet');  // npm install helmet

const app = express();

// ─── 1. APPLY ALL DEFAULT HELMET PROTECTIONS ─────────────────────────────────
app.use(helmet());  // one line → sets ~11 security headers with sensible defaults

app.get('/', (req, res) => {
  res.send('Hello, secured by Helmet!');
});

app.listen(3000, () => {
  console.log('Server running — check headers with: curl -I http://localhost:3000');
});

// Resulting headers (sample, defaults as of Helmet v7):
// Content-Security-Policy: default-src 'self';...
// X-Content-Type-Options: nosniff
// X-Frame-Options: SAMEORIGIN
// Strict-Transport-Security: max-age=15552000; includeSubDomains
// X-DNS-Prefetch-Control: off
// X-Download-Options: noopen
// X-Permitted-Cross-Domain-Policies: none
// Referrer-Policy: no-referrer
// X-XSS-Protection: 0   (legacy header, disabled since modern browsers use CSP instead)
// (X-Powered-By header is REMOVED entirely)
```

## 💻 Code Example — Advanced

```javascript
// helmet-advanced.js — fine-grained per-header configuration

const express = require('express');
const helmet = require('helmet');

const app = express();

app.use(
  helmet({
    // ─── Content-Security-Policy: control allowed resource sources ──────────
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", 'https://checkout.razorpay.com'],  // allow Razorpay SDK
        styleSrc: ["'self'", "'unsafe-inline'"],                   // allow inline styles
        imgSrc: ["'self'", 'data:', 'https://cdn.razorpay.com'],
        connectSrc: ["'self'", 'https://api.razorpay.com'],
        frameSrc: ["'self'", 'https://api.razorpay.com'],          // payment iframe
        objectSrc: ["'none'"],
        upgradeInsecureRequests: [],   // auto-upgrade http:// resource links to https://
      },
    },

    // ─── Strict-Transport-Security: force HTTPS for 1 year, incl. subdomains ─
    hsts: {
      maxAge: 31536000,         // 1 year in seconds
      includeSubDomains: true,
      preload: true,             // eligible for browser HSTS preload list
    },

    // ─── X-Frame-Options: prevent clickjacking entirely ──────────────────────
    frameguard: {
      action: 'deny',   // 'deny' (never framed) vs 'sameorigin' (only own site can frame)
    },

    // ─── Referrer-Policy: control how much referrer info leaks cross-site ───
    referrerPolicy: {
      policy: 'strict-origin-when-cross-origin',  // send full URL same-origin, origin only cross-origin
    },

    // ─── Cross-Origin policies for isolation (Spectre-style attack mitigation) ─
    crossOriginEmbedderPolicy: true,
    crossOriginOpenerPolicy: { policy: 'same-origin' },
    crossOriginResourcePolicy: { policy: 'same-site' },
  })
);

// Disable a specific default if it conflicts with your app's needs
// app.use(helmet({ contentSecurityPolicy: false }));  // disable CSP entirely (not recommended)

app.get('/checkout', (req, res) => {
  res.send('Checkout page — protected by fine-tuned CSP allowing Razorpay SDK');
});

app.listen(3000);
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Helmet combined with environment-specific config
const express = require('express');
const helmet = require('helmet');

const app = express();
const isProd = process.env.NODE_ENV === 'production';

app.use(
  helmet({
    // In development, relax CSP to allow webpack-dev-server / hot reload scripts
    contentSecurityPolicy: isProd
      ? {
          directives: {
            defaultSrc: ["'self'"],
            scriptSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'"],
          },
        }
      : false,  // disabled in dev to avoid breaking local tooling

    // Only enforce HSTS in production (HTTPS required; breaks local http:// dev)
    hsts: isProd ? { maxAge: 31536000, includeSubDomains: true } : false,
  })
);

app.use(express.json());

// Example: additional manual header not covered by helmet defaults
app.use((req, res, next) => {
  res.setHeader('Permissions-Policy', 'geolocation=(), camera=(), microphone=()');
  next();
});

app.get('/api/health', (req, res) => res.json({ status: 'ok' }));

app.listen(3000, () => {
  console.log(`Server running in ${isProd ? 'production' : 'development'} mode`);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Applying `helmet()` AFTER routes are defined
```javascript
// WRONG: middleware order matters — headers set after response already started won't apply
app.get('/', (req, res) => res.send('Hi'));
app.use(helmet());  // too late for the route above!

// CORRECT: apply helmet BEFORE any routes
app.use(helmet());
app.get('/', (req, res) => res.send('Hi'));
```

❌ Mistake 2: Disabling CSP entirely because "it breaks my inline scripts"
```javascript
// WRONG: giving up all CSP protection instead of fixing the actual issue
app.use(helmet({ contentSecurityPolicy: false }));  // removes a major defense layer

// CORRECT: allow specific trusted inline patterns via nonce or hash, keep CSP active
app.use((req, res, next) => {
  res.locals.nonce = crypto.randomBytes(16).toString('base64');
  next();
});
app.use(helmet({
  contentSecurityPolicy: {
    directives: { scriptSrc: ["'self'", (req, res) => `'nonce-${res.locals.nonce}'`] },
  },
}));
// Then in template: <script nonce="<%= nonce %>">...</script>
```

---

## 🧠 Tricky Interview Question

```javascript
const app = require('express')();
const helmet = require('helmet');
app.use(helmet());
app.get('/', (req, res) => res.send('hi'));
app.listen(3000);

// curl -I http://localhost:3000
// Which header, present in Express by default, is MISSING from the response?
```
Answer: **`X-Powered-By: Express`** is missing. By default, Express sends this header revealing the framework in use. Helmet's `hidePoweredBy` sub-middleware explicitly removes it (via `app.disable('x-powered-by')` under the hood, or stripping the header). This matters because attackers scanning for known Express/Node vulnerabilities use this header for reconnaissance — removing it provides "security through obscurity" (not a strong defense alone, but a useful extra layer combined with everything else Helmet does).

---

## ⚫ Interview Questions + Answers

Q1: What does `X-Content-Type-Options: nosniff` protect against?
A1: It stops browsers from "MIME sniffing" — guessing a resource's content type by inspecting its content instead of trusting the declared `Content-Type` header. Without this header, a browser might execute a file served as `Content-Type: text/plain` as JavaScript or HTML if its content looks like a script, enabling certain XSS attack vectors (e.g., uploading a malicious file disguised as an image that gets executed as HTML/JS when viewed directly).

Q2: What is the difference between `X-Frame-Options` and the CSP `frame-ancestors` directive?
A2: Both prevent clickjacking by controlling whether your page can be embedded in an `<iframe>` on another site. `X-Frame-Options` is the older header (`DENY`, `SAMEORIGIN`, or a specific origin in some browsers) with inconsistent multi-origin support. `frame-ancestors` (part of CSP) is the modern replacement, supporting multiple allowed origins and being more flexible. Helmet sets both for backward compatibility with older browsers that don't support CSP's `frame-ancestors`.

Q3: Why does Helmet disable the legacy `X-XSS-Protection` header by default (set it to `0`)?
A3: `X-XSS-Protection` was a browser-built-in XSS filter (mainly in old IE/Chrome) that tried to detect and block reflected XSS patterns automatically. It was found to introduce its OWN vulnerabilities in some cases (attackers could exploit the filter itself to leak information) and modern browsers have removed/deprecated this filter entirely in favor of CSP, which is far more robust. Helmet explicitly sets it to `0` (disabled) rather than leaving it enabled with its flawed heuristics.

Q4: What problem does `Strict-Transport-Security` (HSTS) solve that HTTPS redirects alone don't?
A4: Even if your server redirects all HTTP to HTTPS, the FIRST request a user makes could still go out over plain HTTP (e.g., typing `yoursite.com` without `https://`), and an attacker on the network (man-in-the-middle) could intercept that initial request before the redirect happens (SSL stripping attack). HSTS tells the BROWSER to remember "always use HTTPS for this domain" after the first visit, so subsequent requests never even attempt plain HTTP — closing that initial-request window. The `preload` option submits your domain to a browser-maintained list so even the FIRST-EVER visit is HTTPS-only.

Q5: Can Helmet alone fully secure a Node.js application?
A5: No. Helmet addresses HTTP response header-level protections (clickjacking, MIME sniffing, some XSS/CSP support, HTTPS enforcement) — it's one layer of defense-in-depth. It does NOT handle authentication, authorization, input validation, SQL/NoSQL injection prevention, rate limiting, or secrets management. A secure app needs Helmet PLUS proper auth, validated input, parameterized queries, rate limiting, and secure secret storage — Helmet is necessary but not sufficient.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building any Express-based web app or API exposed to the internet — there's essentially no downside to using it.
- You need quick, well-researched default security headers without manually researching each one.

❌ Avoid when:
- Rarely a reason to avoid it entirely, but you may need to disable/customize specific sub-middlewares (like CSP) if they conflict with third-party embeds/scripts your app legitimately needs — customize, don't disable Helmet wholesale.

---

## 📊 Visual Diagram

```
HELMET MIDDLEWARE STACK:
──────────────────────────────────────────────────────────

  app.use(helmet())
       │
       ├──► contentSecurityPolicy  → Content-Security-Policy header
       ├──► hsts                    → Strict-Transport-Security header
       ├──► frameguard              → X-Frame-Options header
       ├──► noSniff                 → X-Content-Type-Options header
       ├──► hidePoweredBy           → removes X-Powered-By header
       ├──► referrerPolicy          → Referrer-Policy header
       ├──► dnsPrefetchControl      → X-DNS-Prefetch-Control header
       ├──► crossOriginOpenerPolicy → Cross-Origin-Opener-Policy header
       └──► ... (and more)
       │
       ▼
  Response sent with ~11 security headers automatically applied
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Clickjacking | Tricking user into clicking hidden framed content | Hidden framed content पर click करवाना |
| MIME sniffing | Browser guessing content type from content | Content से content type guess करना |
| HSTS | Header forcing HTTPS-only connections | HTTPS-only force करने वाला header |
| CSP | Header restricting allowed resource sources | Allowed resource sources restrict करने वाला header |
| Fingerprinting | Identifying tech stack from headers/behavior | Headers से tech stack पहचानना |
| Nonce | One-time random value allowing specific inline scripts | Specific inline scripts allow करने वाला one-time value |

---

## ⚡ 3-Line Summary
English:
1. Helmet.js bundles ~11-15 security-related HTTP headers into one middleware call, covering clickjacking, MIME sniffing, HTTPS enforcement, and more.
2. Apply `app.use(helmet())` early in the middleware stack, before route definitions, and customize directives (especially CSP) per your app's actual resource needs.
3. Helmet is one defense layer — combine it with input validation, auth, rate limiting, and injection prevention for complete security.

Hindi:
1. Helmet.js ~11-15 security HTTP headers को एक middleware call में bundle करता है — clickjacking, MIME sniffing, HTTPS enforcement।
2. `app.use(helmet())` early middleware में लगाओ, routes से पहले, और CSP जैसी directives को app की ज़रूरत अनुसार customize करो।
3. Helmet एक defense layer है — input validation, auth, rate limiting के साथ combine करो complete security के लिए।

---

## ➡️ Next Topic
**136. Rate Limiting — Advanced** — Multi-tier rate limiting, distributed rate limiting with Redis।
