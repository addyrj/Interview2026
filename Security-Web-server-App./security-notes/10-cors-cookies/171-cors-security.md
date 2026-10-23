---

# 171. CORS Security — Misconfigurations + Secure Setup
# हिंदी में: CORS — Same-Origin Policy और Secure Configuration
# Risk Level: ⛔ High

---

## 🔵 Simple Definition (English)
CORS (Cross-Origin Resource Sharing) is a browser security mechanism that restricts cross-origin HTTP requests. The Same-Origin Policy blocks scripts on one origin from reading responses from a different origin. CORS provides controlled exceptions — servers declare which origins they trust. Misconfigurations can grant excessive trust, allowing attackers to read your API responses from malicious sites.

## 🔵 सरल परिभाषा (Hindi)
CORS browser की security mechanism है जो cross-origin requests को restrict करती है। Same-Origin Policy by default दूसरी site को responses read नहीं करने देती। CORS से server बताता है कि कौन सी origins trusted हैं। Misconfiguration से attacker भी trusted बन सकता है और API data read कर सकता है।

---

## ⚠️ The Attack / Threat

```
SAME-ORIGIN POLICY (Default Browser Behavior):
Origin = Protocol + Domain + Port
https://app.com:443 ≠ http://app.com (different protocol)
https://app.com:443 ≠ https://sub.app.com (different subdomain)
https://app.com:443 ≠ https://app.com:8080 (different port)

Without CORS, cross-origin JS CANNOT read responses:
// evil.com trying to read api.bank.com:
fetch('https://api.bank.com/account/balance', { credentials: 'include' })
  .then(r => r.json())  // ❌ BLOCKED by browser — same-origin policy

ATTACK 1 — Wildcard with Credentials:
Server: Access-Control-Allow-Origin: *
        Access-Control-Allow-Credentials: true
→ Browsers REJECT this combination — but if developer uses a workaround:
  Access-Control-Allow-Origin: (reflects Origin header!)
  Access-Control-Allow-Credentials: true
→ evil.com requests → server reflects "Origin: evil.com" back → browser allows!
→ Attacker reads all API responses WITH victim's cookies ☠️

ATTACK 2 — Null Origin Acceptance:
Server: if (origin === 'null') allow
→ Sandboxed iframes, local files, redirects use origin: null
→ Attacker: <iframe sandbox="allow-scripts"> containing fetch() sends origin: null
→ Server allows → attacker reads response

ATTACK 3 — Subdomain Wildcard:
Server: if (origin.endsWith('.app.com')) allow
→ Attacker compromises subdomain: malicious.app.com
→ Attacker's subdomain reads all API data → lateral movement

ATTACK 4 — Pre-Domain Match:
Server: if (origin.includes('app.com')) allow
→ evil-app.com passes! evil-app.com.attacker.com passes!
→ Must check: startsWith('https://app.com') AND length check

Preflight Request (OPTIONS):
Browser sends OPTIONS before non-simple requests:
Simple: GET/HEAD/POST + standard headers
Non-simple: PUT/DELETE/PATCH, custom headers, JSON content-type
→ Server responds with allowed methods/headers
→ If preflight fails → actual request not sent
```

---

## 💻 Vulnerable Code (What NOT to do)

```javascript
// ❌ VULNERABLE CORS CODE

// ─── ATTACK 1: Reflecting Origin header blindly ───────────────
app.use((req, res, next) => {
  const origin = req.headers.origin;
  // ❌ Trusting ANY origin that sends a request:
  res.setHeader('Access-Control-Allow-Origin', origin);  // reflects attacker's origin!
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  // Now evil.com gets CORS access WITH cookies → reads user data!
  next();
});

// ─── ATTACK 2: Wildcard + Credentials (developers try this) ──
app.use(cors({
  origin: '*',              // ❌ Wildcard
  credentials: true         // ❌ With credentials
  // Browsers block this, so developers often "fix" it by reflecting origin → Attack 1
}));

// ─── ATTACK 3: Regex that's too broad ─────────────────────────
app.use(cors({
  origin: /app\.com$/       // ❌ Matches evil-app.com, app.com.evil.com!
}));

// ─── ATTACK 4: Substring check ────────────────────────────────
app.use((req, res, next) => {
  const origin = req.headers.origin || '';
  if (origin.includes('app.com')) {  // ❌ evil-app.com passes!
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Credentials', 'true');
  }
  next();
});

// ─── ATTACK 5: Accepting null origin ─────────────────────────
app.use((req, res, next) => {
  const origin = req.headers.origin;
  if (!origin || origin === 'null') {  // ❌ Sandbox attacks!
    res.setHeader('Access-Control-Allow-Origin', 'null');
    res.setHeader('Access-Control-Allow-Credentials', 'true');
  }
  next();
});
```

---

## 💻 Secure Code (What TO do)

```javascript
// ✅ SECURE CORS CODE

// ─── Method 1: Strict Whitelist (Most Secure) ─────────────────
const cors = require('cors');

const ALLOWED_ORIGINS = new Set([
  'https://app.com',
  'https://www.app.com',
  'https://admin.app.com',
  // ✅ No http:// versions — force HTTPS
  // ✅ Exact matches only — no substrings/regex
]);

// Development only:
if (process.env.NODE_ENV === 'development') {
  ALLOWED_ORIGINS.add('http://localhost:3000');
  ALLOWED_ORIGINS.add('http://localhost:3001');
}

const corsOptions = {
  origin: (origin, callback) => {
    // Allow requests with no origin (same-origin, mobile apps, Postman)
    if (!origin) return callback(null, true);
    
    // ✅ Exact Set lookup — no substring, no regex
    if (ALLOWED_ORIGINS.has(origin)) {
      callback(null, true);
    } else {
      callback(new Error(`CORS: Origin ${origin} not allowed`));
    }
  },
  credentials: true,                          // allow cookies
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  exposedHeaders: ['X-Total-Count', 'X-Request-Id'],  // headers JS can read
  maxAge: 86400,  // preflight cache: 24 hours (reduce OPTIONS requests)
  optionsSuccessStatus: 200,  // some legacy browsers choke on 204
};

app.use(cors(corsOptions));

// ─── Per-Route CORS (Different policies for different routes) ──
// Public API — no credentials needed:
const publicCors = cors({ origin: '*' });
app.get('/api/public/health', publicCors, (req, res) => {
  res.json({ status: 'ok' });
});

// Private API — strict origin check:
app.use('/api/private', cors(corsOptions));

// ─── Explicitly handle preflight ──────────────────────────────
// app.use(cors()) handles OPTIONS automatically, but explicit is clearer:
app.options('*', cors(corsOptions));  // handle ALL preflight requests

// ─── CORS Error Handler ────────────────────────────────────────
app.use((err, req, res, next) => {
  if (err.message && err.message.startsWith('CORS:')) {
    return res.status(403).json({ error: 'CORS: Access denied', origin: req.headers.origin });
  }
  next(err);
});

// ─── What Access-Control headers mean ─────────────────────────
/*
Response headers set by server:
  Access-Control-Allow-Origin: https://app.com    — which origins can read responses
  Access-Control-Allow-Credentials: true           — allow cookies/auth headers
  Access-Control-Allow-Methods: GET, POST, ...     — allowed methods (preflight)
  Access-Control-Allow-Headers: Content-Type, ...  — allowed request headers (preflight)
  Access-Control-Expose-Headers: X-Total-Count     — headers JS can read (default blocked)
  Access-Control-Max-Age: 86400                    — preflight cache duration
  Vary: Origin                                     — IMPORTANT: cache varies by origin

Request headers sent by browser:
  Origin: https://app.com                          — tells server where request came from
  Access-Control-Request-Method: PUT               — method for preflight
  Access-Control-Request-Headers: Content-Type     — headers for preflight
*/

// ─── Vary: Origin Header (Critical for CDN caching) ───────────
// When using origin whitelist, add Vary: Origin to prevent cache poisoning:
app.use((req, res, next) => {
  res.vary('Origin');  // Express adds Vary header
  next();
});
// Without Vary: Origin — CDN may cache a response for app.com and serve it
// to evil.com (wrong CORS headers!)

// ─── CORS for SPA (React/Next.js) + API on different domain ───
// Frontend: https://app.com
// API: https://api.app.com

// API server CORS setup:
const apiCors = cors({
  origin: 'https://app.com',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
});

// Frontend fetch:
// fetch('https://api.app.com/data', {
//   credentials: 'include',  // ← required for cookies
//   headers: { 'Content-Type': 'application/json' }
// })
```

---

## 🟠 Implementation in My Stack

```typescript
// ─── NestJS — CORS Setup ──────────────────────────────────────
// main.ts
async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  app.enableCors({
    origin: (origin, callback) => {
      const allowed = new Set([
        'https://app.com',
        'https://www.app.com',
        ...(process.env.NODE_ENV !== 'production'
          ? ['http://localhost:3000']
          : []),
      ]);
      
      if (!origin || allowed.has(origin)) {
        callback(null, true);
      } else {
        callback(new Error('Not allowed by CORS'));
      }
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
  });
  
  await app.listen(3000);
}

// ─── Next.js API Routes — CORS ────────────────────────────────
// middleware.ts (Next.js 13+)
import { NextResponse } from 'next/server';

export function middleware(req) {
  const origin = req.headers.get('origin');
  const allowedOrigins = ['https://app.com', 'https://www.app.com'];
  
  const res = NextResponse.next();
  
  if (origin && allowedOrigins.includes(origin)) {
    res.headers.set('Access-Control-Allow-Origin', origin);
    res.headers.set('Access-Control-Allow-Credentials', 'true');
    res.headers.set('Vary', 'Origin');
  }
  
  return res;
}
```

---

## 🔧 Security Tools
| Tool | Purpose | Use |
|------|---------|-----|
| `cors` npm | CORS middleware | `app.use(cors(options))` |
| Browser DevTools | Inspect CORS headers | Network tab → response headers |
| `curl -H "Origin: ..."` | Test CORS from CLI | Check what origin gets allowed |
| OWASP ZAP | CORS misconfiguration scanner | Automated security scan |
| `Burp Suite` | CORS testing | Manual pentesting |

---

## ⚫ Interview Questions + Answers

**Q1: What is the Same-Origin Policy and what does it protect against?**
A1: Same-Origin Policy (SOP) is a browser security rule: JavaScript on `https://evil.com` cannot read responses from `https://bank.com`. Two pages have the same origin only if both have the same protocol, domain, AND port. SOP protects against: reading private data from authenticated APIs (your bank balance), reading session cookies from another site, accessing localStorage of another origin. Without SOP, any site could silently read your email, bank data, and health records. CORS provides controlled exceptions to SOP — it lets a server say "I trust https://app.com to read my responses."

**Q2: What is a preflight request and when does the browser send one?**
A2: A preflight is an automatic OPTIONS request the browser sends BEFORE the actual request to ask "is this cross-origin request allowed?" The browser sends a preflight for non-simple requests: HTTP methods other than GET/HEAD/POST, custom headers beyond Accept/Content-Type/etc., content-type: application/json. The preflight includes `Access-Control-Request-Method` and `Access-Control-Request-Headers`. If the server responds with the correct `Access-Control-Allow-*` headers, the browser proceeds with the actual request. If the preflight fails, the actual request is never sent — protecting the server from unexpected cross-origin mutations.

**Q3: Why is `Access-Control-Allow-Origin: *` with credentials dangerous?**
A3: Browsers reject `Access-Control-Allow-Origin: *` combined with `Access-Control-Allow-Credentials: true` (spec forbids it). But some developers "fix" this by reflecting the Origin header: `Access-Control-Allow-Origin: [whatever Origin header says]` + `Allow-Credentials: true`. Now every origin is allowed WITH credentials — evil.com can make authenticated requests to your API and read responses using the victim's session cookies. The browser delivers the response to the attacker's JavaScript, including private user data. Always use an explicit origin whitelist. Never reflect the Origin header blindly.

**Q4: What is the Vary: Origin header and why does it matter for CDN caching?**
A4: When your CORS policy varies by origin (different origins get different Allow-Origin values), you must include `Vary: Origin` in responses. Without it: CDN caches a response with `Access-Control-Allow-Origin: https://app.com`. Next request from `evil.com` — CDN serves the cached response with the same ACAO header. Evil.com's JavaScript sees `Access-Control-Allow-Origin: https://app.com` which doesn't match `evil.com`, so it's blocked — but the content was still served. With `Vary: Origin`, the CDN creates separate cache entries per origin — correct CORS headers per requester.

**Q5: How do you configure CORS for a microservices architecture?**
A5: Multiple patterns: (1) **API Gateway handles CORS** — all services behind a gateway (Kong, AWS API Gateway, nginx), which handles CORS centrally. Individual services use `origin: '*'` since requests come from the gateway, not browsers. (2) **Each service has its own CORS** — use a shared CORS config library/package, deploy same allowed origins list from a config service. (3) **Service mesh (Istio/Envoy)** — CORS configured at the proxy layer, not in application code. Best practice: don't let every microservice have its own CORS logic — centralize at the gateway or proxy layer to avoid inconsistencies and misconfigurations.

---

## ✅ Security Checklist
```
□ CORS uses a strict origin whitelist (not regex, not substring)
□ No blind Origin header reflection
□ Origin: null is never explicitly allowed with credentials
□ Vary: Origin header set when CORS varies by origin
□ Access-Control-Allow-Origin: * only for truly public endpoints (no credentials)
□ credentials: true only for authenticated endpoints with strict origins
□ Preflight OPTIONS requests handled correctly
□ Allowed methods list matches only what the API actually uses
□ CORS is not set on health-check/public endpoints unnecessarily
□ CORS tested from disallowed origins (should get no ACAO header back)
□ Production CORS does not include localhost origins
□ Access-Control-Allow-Headers does not include '*'
```

---

## 📊 Visual Diagram

```
CORS FLOW:
Browser on app.com → fetch('https://api.app.com/data', {credentials:'include'})
                          ↓
               [Non-simple request: JSON Content-Type]
                          ↓
                  PREFLIGHT: OPTIONS /data
                  Origin: https://app.com
                  Access-Control-Request-Method: POST
                  Access-Control-Request-Headers: Content-Type
                          ↓
              Server checks: is app.com in whitelist? YES
                          ↓
                  PREFLIGHT RESPONSE:
                  Access-Control-Allow-Origin: https://app.com
                  Access-Control-Allow-Credentials: true
                  Access-Control-Allow-Methods: POST
                  Access-Control-Allow-Headers: Content-Type
                  Access-Control-Max-Age: 86400
                          ↓
              Browser: preflight passed, send actual request
                          ↓
              POST /data with session cookie
                          ↓
              Response with ACAO: https://app.com → JS reads it ✅

MISCONFIGURATION — Blind Reflection:
evil.com → Origin: evil.com → Server reflects it back → evil.com reads response ☠️

SECURE — Whitelist:
evil.com → Origin: evil.com → Not in Set(['app.com']) → No ACAO header → blocked ✅
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CORS | Cross-Origin Resource Sharing — controlled cross-origin access | Cross-origin access की permission |
| Same-Origin Policy | Browser blocks cross-origin reads | Different origins एक-दूसरे का data नहीं पढ़ सकते |
| Preflight | Browser OPTIONS request before actual request | क्या request allowed है? Browser पूछता है |
| ACAO | Access-Control-Allow-Origin header | कौन सी origin response read कर सकती है |
| Credentials | Cookies/auth headers in cross-origin requests | Cross-origin में cookies भेजना |
| Vary: Origin | Cache varies per origin | CDN के लिए अलग-अलग cache entries |

---

## ⚡ 3-Line Summary
**English:**
1. CORS is a controlled exception to Same-Origin Policy — servers declare trusted origins; browsers enforce it by blocking JS from reading cross-origin responses.
2. Critical mistake: reflecting the Origin header blindly with credentials:true — allows any attacker to read your authenticated API responses.
3. Use a strict Set-based whitelist, add Vary: Origin for CDN caching, and never use `*` with credentials.

**Hindi:**
1. CORS Same-Origin Policy का controlled exception है — server trusted origins declare करता है, browser cross-origin reads block करता है।
2. Critical mistake: Origin header blindly reflect करना credentials:true के साथ — attacker को API responses read करने देता है।
3. Strict Set-based whitelist use करो, Vary:Origin add करो, और credentials के साथ * कभी मत use करो।

---

## 🚨 Red Flag Signs
- `res.setHeader('Access-Control-Allow-Origin', req.headers.origin)` without whitelist check
- `origin: '*'` with `credentials: true`
- `origin === 'null'` accepted with credentials
- No `Vary: Origin` header when different origins get different CORS responses
- CORS regex like `/app\.com$/` (too broad — matches substrings)
- Localhost origins present in production config
- `Access-Control-Allow-Headers: *` (spec issue in some browsers)

---

## ➡️ Next Topic
**217. Rate Limiting** — DDoS protection, brute force prevention, per-IP limits, Redis-based distributed rate limiting, and token bucket algorithm.
