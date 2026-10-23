# F15. CORS (Cross-Origin Resource Sharing)
# हिंदी में: CORS — ब्राउज़र का नियम जिससे सर्वर बताता है कि किस दूसरी website (origin) की JavaScript उसके API का जवाब पढ़ सकती है; बिना अनुमति ब्राउज़र जवाब रोक देता है

---

## 🔵 Simple Definition (English)
Browsers enforce the **Same-Origin Policy (SOP)**: JavaScript on `https://app.myapp.com` can't read responses from a **different origin** (different **scheme, host or port**), e.g. `https://api.myapp.com` or `http://localhost:8000`.
**CORS** is the standard way for a **server to relax SOP** by sending response headers like `Access-Control-Allow-Origin: https://app.myapp.com`, telling the browser that JS from that origin may read the response.
For "non-simple" requests (e.g., `PUT/DELETE`, JSON `Content-Type`, custom headers like `Authorization`), the browser first sends a **preflight `OPTIONS` request** to ask permission.
Key point: **CORS is enforced by browsers, not servers**. It protects users, not your API. curl, Postman and mobile apps ignore it.

## 🔵 सरल परिभाषा (Hindi)
ब्राउज़र का Same-Origin नियम: एक origin (scheme + host + port) की JavaScript दूसरे origin के API का जवाब नहीं पढ़ सकती — जैसे `app.myapp.com` से `api.myapp.com` या `localhost:3000` से `localhost:8000`।
CORS में सर्वर header भेजकर बताता है "इस origin को अनुमति है"; JSON/Authorization/PUT जैसी requests से पहले ब्राउज़र एक OPTIONS (preflight) भेजकर पूछता है। CORS सिर्फ़ ब्राउज़र लागू करता है — Postman, curl, React Native ऐप पर लागू नहीं; यह आपके API की सुरक्षा नहीं, यूज़र की सुरक्षा है।

---

## 🔴 Problem it Solves
Without the Same-Origin Policy, any website you visit (`evil.com`) could use your logged-in cookies to `fetch('https://mail.google.com/...')` and **read your emails**, or read your bank balance.
SOP blocks that, but legitimate apps often need cross-origin calls:
- SPA on `app.myapp.com` calling `api.myapp.com`
- local dev: React on `localhost:3000` → FastAPI on `localhost:8000`
- public APIs used by many sites (maps, payment SDKs, fonts)
CORS gives servers a controlled, explicit way to allow **specific origins, methods, headers and credentials**.
It's also one of the most common errors in frontend work, so you must be able to debug it.

## 🔴 यह क्यों बना? (Hindi)
Same-Origin नियम न हो तो कोई भी बुरी साइट आपकी login cookies से `fetch` करके आपके emails या bank balance पढ़ लेती। यह नियम उसे रोकता है।
पर असली ऐप्स को दूसरे origin पर call करनी पड़ती है (app → api subdomain, localhost:3000 → 8000, public APIs) — CORS सर्वर को साफ़ तरीके से कुछ origins, methods, headers और cookies की अनुमति देने देता है। और यह frontend की सबसे आम error है, इसलिए debug करना आना चाहिए।

---

## 🟢 How it Works — Step by Step

### What counts as the same origin

```
Origin = scheme + host + port
https://app.myapp.com           vs  https://app.myapp.com/orders   → SAME (path doesn't matter)
https://app.myapp.com           vs  https://api.myapp.com          → DIFFERENT (host)
https://myapp.com               vs  http://myapp.com               → DIFFERENT (scheme)
http://localhost:3000           vs  http://localhost:8000          → DIFFERENT (port)
Note: "same-site" (eTLD+1, used for cookies/SameSite) ≠ "same-origin"; app.myapp.com & api.myapp.com
      are same-SITE but cross-ORIGIN.
```

### Simple request (no preflight)

```
Conditions: GET/HEAD/POST + only "simple" headers + Content-Type is text/plain,
            multipart/form-data or application/x-www-form-urlencoded
Browser → GET https://api.myapp.com/menu   Origin: https://app.myapp.com
Server  → 200  Access-Control-Allow-Origin: https://app.myapp.com   (+ Vary: Origin)
Browser → lets JS read the response ✅   (missing/mismatched header → JS gets a CORS error ❌,
                                          but the request DID reach the server!)
```

### Preflighted request

```
fetch('https://api.myapp.com/cart', { method: 'PUT', headers: { 'Content-Type': 'application/json',
       Authorization: 'Bearer …' }, body })

1) Browser → OPTIONS /cart
             Origin: https://app.myapp.com
             Access-Control-Request-Method: PUT
             Access-Control-Request-Headers: authorization, content-type
2) Server  → 204
             Access-Control-Allow-Origin: https://app.myapp.com
             Access-Control-Allow-Methods: GET, POST, PUT, DELETE
             Access-Control-Allow-Headers: authorization, content-type, x-request-id
             Access-Control-Max-Age: 600            ← cache preflight for 10 min (fewer round trips)
3) Browser → PUT /cart  (actual request)
4) Server  → 200 + Access-Control-Allow-Origin: https://app.myapp.com
Preflight adds a round trip → on mobile web that's +100–300 ms; use Max-Age, or same-origin API
```

### Credentials (cookies) cross-origin

```
Client: fetch(url, { credentials: 'include' })  /  axios withCredentials: true
Server must send:
  Access-Control-Allow-Origin: https://app.myapp.com      ← exact origin, NOT "*"
  Access-Control-Allow-Credentials: true
Cookies also need SameSite=None; Secure if truly cross-SITE (different eTLD+1);
for app.myapp.com ↔ api.myapp.com (same-site) SameSite=Lax works.
"*" is fine only for public, non-credentialed APIs (fonts, open data).
```

### Reading response headers
```
By default JS can read only "safelisted" response headers. To read e.g. X-Request-Id or a pagination header:
Access-Control-Expose-Headers: X-Request-Id, X-Total-Count
```

### Common mistakes & debugging

```
❌ Reflecting any Origin with Allow-Credentials: true  → any site can read user data (critical vuln!)
❌ Access-Control-Allow-Origin: * with credentials       → browser rejects
❌ Forgetting OPTIONS handling (auth middleware returns 401 to preflight → CORS failure)
❌ Missing Vary: Origin when ACAO varies → CDN serves wrong origin's header to others
❌ Error responses (500/401) without CORS headers → frontend sees "CORS error" instead of real error
❌ Thinking CORS secures the API → attackers use curl; you still need auth, rate limits
Debug: DevTools Network → look at the OPTIONS request + response headers; console message names the missing header
```

### Avoiding CORS entirely

```
Serve frontend and API from the SAME origin via a reverse proxy / rewrites:
  https://myapp.com/        → Next.js/static
  https://myapp.com/api/*   → Node/FastAPI (Nginx/CloudFront/Next.js rewrites)
→ no preflights, simpler cookies (first-party), but couples deployment routing
Dev: Vite proxy / Next.js rewrites to backend on localhost:8000
```

## 🟢 कैसे काम करता है? (Hindi)
1. Origin = scheme + host + port; इनमें कुछ भी अलग तो cross-origin (localhost:3000 और :8000 भी अलग)।
2. Simple GET/POST: ब्राउज़र `Origin` header भेजता है; सर्वर `Access-Control-Allow-Origin` में वही origin लौटाए तो JS जवाब पढ़ सकती है — वरना CORS error (पर request सर्वर तक पहुँच चुकी होती है!)।
3. JSON, Authorization header या PUT/DELETE पर पहले OPTIONS preflight — सर्वर allowed methods/headers बताए; `Max-Age` से preflight cache करो ताकि हर बार extra round trip न हो।
4. Cookies भेजनी हों तो client `credentials: 'include'`, सर्वर exact origin (`*` नहीं) + `Allow-Credentials: true`; हर origin को आँख मूँदकर reflect करना बड़ा security bug।
5. सबसे आसान: frontend और API एक ही origin पर (`/api` को proxy/rewrite) — CORS ही नहीं; और याद रखो CORS API की सुरक्षा नहीं, auth अलग से ज़रूरी।

---

## 🟡 Real World Example

**Google Fonts / public CDNs (jsDelivr, cdnjs)** — respond with `Access-Control-Allow-Origin: *` so any website can load fonts and modules (fonts require CORS for cross-origin use).

**Stripe / Razorpay JS SDKs** — their APIs used from browsers allow cross-origin calls with publishable keys only. Secret keys are never sent from the browser, since CORS isn't a security boundary for the API.

**Many startups (and Vercel/Next.js apps)** — avoid CORS by proxying `/api/*` to the backend through Next.js rewrites, Nginx or CloudFront behaviours, keeping a single origin, first-party cookies and no preflights.

**Real-world CORS vulnerabilities** — security researchers have repeatedly found APIs (including at bitcoin exchanges and large SaaS products) that reflected arbitrary `Origin` values with `Allow-Credentials: true`, letting any website read users' private data. This is a classic bug-bounty finding.

## 🟡 Real Example Hindi में
Google Fonts और public CDNs `Access-Control-Allow-Origin: *` भेजते हैं ताकि हर साइट fonts ले सके। Razorpay/Stripe के browser SDK में सिर्फ़ publishable key, secret key कभी browser से नहीं।
कई startups `/api/*` को Next.js rewrite या Nginx से backend पर भेजते हैं — एक ही origin, CORS नहीं। Bug bounty में आम bug: API हर Origin को reflect करे और credentials allow करे — तब कोई भी साइट यूज़र का निजी डेटा पढ़ सकती है।

---

## 🟠 My Stack Example

### Express — allow-list of origins, credentials, preflight cache
```js
import cors from 'cors';
const allowed = new Set(['https://app.myapp.com', 'https://admin.myapp.com',
                         ...(process.env.NODE_ENV !== 'production' ? ['http://localhost:3000'] : [])]);
app.use(cors({
  origin: (origin, cb) => (!origin || allowed.has(origin) ? cb(null, origin ?? false) : cb(null, false)),  // no Origin = curl/mobile
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-Id', 'Idempotency-Key', 'X-CSRF-Token'],
  exposedHeaders: ['X-Request-Id'],
  maxAge: 600,
}));
// cors() handles OPTIONS before auth middleware → preflight never gets 401
// The cors package adds Vary: Origin automatically when origin is dynamic
```

### FastAPI — CORSMiddleware
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.myapp.com", "https://admin.myapp.com"],   # never ["*"] with credentials
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Request-Id", "Idempotency-Key"],
    expose_headers=["X-Request-Id"],
    max_age=600,
)
# Preview deployments (pr-123.myapp.dev): allow_origin_regex=r"https://pr-\d+\.myapp\.dev"
```

### Nginx — add CORS headers & answer preflight (when the app can't)
```nginx
map $http_origin $cors_origin {
  default "";
  "https://app.myapp.com"   $http_origin;
  "https://admin.myapp.com" $http_origin;
}
location /api/ {
  if ($request_method = OPTIONS) {
    add_header Access-Control-Allow-Origin $cors_origin always;
    add_header Access-Control-Allow-Credentials true always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, PATCH, DELETE" always;
    add_header Access-Control-Allow-Headers "Content-Type, Authorization, X-Request-Id" always;
    add_header Access-Control-Max-Age 600 always;
    add_header Vary Origin always;
    return 204;
  }
  add_header Access-Control-Allow-Origin $cors_origin always;     # 'always' → also on 4xx/5xx errors
  add_header Access-Control-Allow-Credentials true always;
  add_header Vary Origin always;
  proxy_pass http://api_upstream;
}
```

### Avoid CORS: same-origin proxy
```js
// next.config.js — browser calls /api/* on the same origin, Next.js forwards to backend
module.exports = { async rewrites() { return [{ source: '/api/:path*', destination: 'https://api.internal.myapp.com/:path*' }]; } };
```
```ts
// vite.config.ts (dev only)
export default defineConfig({ server: { proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } } } });
```

### Client side
```ts
// Cookie-based auth cross-origin
fetch('https://api.myapp.com/me', { credentials: 'include' });
axios.create({ baseURL: 'https://api.myapp.com', withCredentials: true });
```

### React Native note
```
RN (and native iOS/Android) don't enforce CORS — there's no browser origin. Requests work without CORS headers.
But Expo Web / React Native Web runs in a browser → CORS applies there.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is CORS and why does it exist?**
A1: Browsers enforce the same-origin policy: scripts can't read responses from a different scheme, host or port. That stops malicious sites from reading data from other sites using the victim's cookies. CORS is the mechanism by which a server explicitly allows specific other origins to read its responses, via `Access-Control-Allow-*` headers. It's enforced by the browser to protect users. It doesn't protect the server from non-browser clients, so authentication and authorization are still required.

**Q2: What is a preflight request and when does it happen?**
A2: It's an automatic `OPTIONS` request the browser sends before a "non-simple" cross-origin request: methods other than GET, HEAD or POST, non-safelisted headers like `Authorization` or custom headers, or a `Content-Type` such as `application/json`. It carries `Access-Control-Request-Method` and `-Headers`. The server must answer with matching `Allow-Methods`, `Allow-Headers` and `Allow-Origin` before the browser sends the real request. `Access-Control-Max-Age` caches the result to avoid an extra round trip on each call.

**Q3: How do you make cross-origin requests with cookies work?**
A3: The client sets `credentials: 'include'` (fetch) or `withCredentials` (axios). The server responds with `Access-Control-Allow-Origin` set to the exact requesting origin (not `*`), `Access-Control-Allow-Credentials: true` and `Vary: Origin`. The cookies need appropriate SameSite attributes: `SameSite=None; Secure` if the sites are cross-site, while `Lax` works for subdomains of the same site. Validate the origin against an allow-list, never reflect arbitrary origins.

**Q4: Your frontend shows a CORS error. How do you debug it?**
A4: Open DevTools Network and check whether a preflight `OPTIONS` was sent and what it returned (status and `Access-Control-*` headers). Common causes: the origin isn't in the allow-list (watch for ports, protocol, trailing slashes), the preflight is rejected by auth middleware or gets 404/405, a missing `Allow-Headers` for a custom header, a wildcard origin with credentials, or error responses (500/401) lacking CORS headers (the real error hides behind a CORS message). Also check for a CDN serving cached headers without `Vary: Origin`. The server logs usually show the request arrived.

**Q5: Is CORS a security feature for your API?**
A5: Not for the API itself. CORS only controls whether browser JavaScript from other origins can read responses, so it protects users' data in their browsers. Attackers can call your API directly with curl or scripts, ignoring CORS. Your API needs proper authentication, authorization, CSRF protection for cookie-based auth, rate limiting and input validation. Misconfigured CORS (reflecting any origin with credentials) can, however, create a vulnerability by letting malicious sites read authenticated responses.

---

## 🔷 Trade-offs
✅ Separate API origin + CORS: independent deploys, multiple frontends — ❌ preflight latency, cookie complexity.
✅ Same-origin proxy: no CORS, first-party cookies, simpler — ❌ routing coupling, proxy hop.
✅ Wildcard `*`: simplest for public data — ❌ no credentials, never for private APIs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Origin | Scheme + host + port | scheme + host + port |
| Same-Origin Policy | Browser blocks cross-origin reads | दूसरे origin का जवाब पढ़ना मना |
| CORS | Server-granted cross-origin access | सर्वर की दी अनुमति |
| Preflight | OPTIONS permission check | पहले अनुमति पूछना |
| Simple request | No preflight needed | बिना preflight वाली request |
| Allow-Origin | Header naming allowed origin | अनुमति वाला origin |
| Allow-Credentials | Allow cookies/auth | cookies की अनुमति |
| Max-Age | Preflight cache duration | preflight कितनी देर याद |
| Expose-Headers | Headers JS may read | JS जो headers पढ़ सके |
| Same-site vs same-origin | eTLD+1 vs exact origin | site बनाम origin |

---

## ⚡ 3-Line Summary
**English:**
1. Same-origin policy blocks cross-origin reads; CORS headers from the server allow specific origins (browser-enforced, not API security).
2. Non-simple requests trigger an OPTIONS preflight; answer it before auth, cache with Max-Age, include CORS headers on errors.
3. With cookies: exact origin + Allow-Credentials + Vary: Origin + allow-list (never reflect any origin); or avoid CORS with a same-origin proxy.

**Hindi:**
1. Same-origin नियम दूसरे origin का जवाब पढ़ना रोकता है; सर्वर CORS headers से कुछ origins को अनुमति देता है (ब्राउज़र लागू करता है)।
2. JSON/Authorization/PUT पर OPTIONS preflight — auth से पहले जवाब दो, Max-Age से cache, errors पर भी CORS headers।
3. Cookies के साथ: exact origin + Allow-Credentials + Vary: Origin + allow-list; या same-origin proxy से CORS से बचो।

---

## ➡️ Next Topic Suggestion
**F16. Auth on Frontend (Token Storage + Refresh Flow)** — With XSS, CSRF and CORS understood, the big question is where to keep tokens in a web app and how to refresh them silently. Next: storage options, the refresh flow, and the BFF pattern.
