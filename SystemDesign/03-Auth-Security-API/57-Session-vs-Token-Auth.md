# 57. Session vs Token Auth
# हिंदी में: Session Auth — सर्वर यूज़र की जानकारी अपने पास (Redis/DB) रखता है और ब्राउज़र को सिर्फ़ एक ID (cookie) देता है; Token Auth — यूज़र की जानकारी signed टोकन (JWT) में क्लाइंट के पास रहती है

---

## 🔵 Simple Definition (English)
After login, the server must recognize the user on later requests. Two main approaches:
- **Session-based (stateful):** the server creates a **session record** (in Redis/DB) and gives the client a random **session ID** in a **cookie**. Each request → look up the session by ID.
- **Token-based (stateless):** the server gives the client a **self-contained signed token** (JWT). Each request → **verify the signature**, with no lookup needed.

## 🔵 सरल परिभाषा (Hindi)
Session में सर्वर यूज़र की जानकारी Redis/DB में रखता है और ब्राउज़र को सिर्फ़ एक random session ID (cookie) देता है — हर request पर ID से जानकारी ढूँढी जाती है।
Token में यूज़र की जानकारी एक signed JWT में होती है जो क्लाइंट के पास रहता है — सर्वर बिना कुछ ढूँढे सिर्फ़ signature जाँचता है।

---

## 🔴 Problem it Solves
HTTP is stateless, so we need a way to carry "who is this?" between requests. The two models solve it with different trade-offs:
- **Sessions:** easy revocation, small cookie, server keeps full control, but need a shared store and lookups, and cookies are awkward for mobile and cross-domain APIs.
- **Tokens:** scale across services and domains and work great for mobile and third-party APIs, but revocation is harder and the token is bigger.

Choosing well depends on **client types, architecture (monolith vs microservices) and security needs**, and it's a very common interview question.

## 🔴 यह क्यों बना? (Hindi)
HTTP हर request को अलग मानता है, इसलिए "यह कौन है?" बताने का तरीका चाहिए।
Session: रद्द करना आसान, सर्वर का पूरा नियंत्रण, पर साझा store और हर बार lookup। Token: कई services और mobile के लिए बढ़िया, पर बीच में रद्द करना मुश्किल। सही चुनाव ऐप के प्रकार पर निर्भर है।

---

## 🟢 How it Works — Step by Step

### Session-based

```
 Browser                          Server                         Redis (session store)
   │ POST /login (email, pw)        │                                  │
   │───────────────────────────────►│ verify password                  │
   │                                │ create session sid=a8f3…         │
   │                                │ SET sess:a8f3… {userId:42, role} EX 7d ──►│
   │◄── Set-Cookie: sid=a8f3…; HttpOnly; Secure; SameSite=Lax ─────────│
   │ GET /orders  (Cookie: sid=a8f3… sent automatically)               │
   │───────────────────────────────►│ GET sess:a8f3… ─────────────────►│
   │                                │◄──── {userId:42} ────────────────│
   │◄────────── 200 orders ─────────│                                  │
   │ POST /logout                   │ DEL sess:a8f3… → instantly invalid│
```

### Token-based

```
 Client (RN app / SPA)            Auth server                     Any API service
   │ POST /login                    │                                  │
   │───────────────────────────────►│ sign JWT {sub:42, role, exp:15m} │
   │◄──── accessToken + refreshToken│                                  │
   │ GET /orders  Authorization: Bearer eyJ…                           │
   │──────────────────────────────────────────────────────────────────►│
   │                                   verify signature + exp (no lookup)
   │◄──────────────────────────────────────────────────── 200 ─────────│
```

### Comparison

```
┌───────────────────────┬────────────────────────────────┬─────────────────────────────────┐
│                       │ Session (cookie + server store)│ Token (JWT bearer)              │
├───────────────────────┼────────────────────────────────┼─────────────────────────────────┤
│ State                 │ Server-side (stateful)         │ Client-side (stateless)         │
│ Per-request cost      │ Store lookup (~1 ms Redis)     │ Signature verify (CPU, µs)      │
│ Revocation / logout   │ Instant (delete session) ✅    │ Hard until exp ❌ (short exp +  │
│                       │                                │ refresh/denylist)               │
│ Scaling               │ Needs shared store (Redis)     │ Any server verifies ✅          │
│ Microservices         │ Each service needs the store   │ Verify via public key ✅        │
│ Mobile apps           │ Cookies possible but awkward   │ Natural fit ✅                  │
│ Cross-domain / 3rd    │ Cookies limited by domain/CORS │ Easy (header) ✅                │
│ party APIs            │                                │                                 │
│ Size                  │ Small ID (~32 bytes)           │ Larger (~500 B–2 KB)            │
│ XSS risk              │ Low (HttpOnly cookie)          │ High if in localStorage         │
│ CSRF risk             │ Yes (cookies auto-sent) →      │ No if sent in header manually   │
│                       │ SameSite + CSRF token          │                                 │
│ Data freshness        │ Always current (role change    │ Stale claims until exp          │
│                       │ applies immediately)           │                                 │
└───────────────────────┴────────────────────────────────┴─────────────────────────────────┘
```

### Important nuance: cookies vs tokens are DIFFERENT axes

```
Transport (how it's sent):   Cookie   vs   Authorization header
Content (what it is):        Session ID (opaque, server lookup)  vs  JWT (self-contained)

You can combine:
  - JWT inside an HttpOnly cookie        (Next.js apps often do this)
  - Opaque token in Authorization header (OAuth introspection, Rails/Django API tokens)
```

### The common modern hybrid ⭐

```
Short-lived ACCESS token (JWT, 5–15 min)  → stateless verification on every API call
Long-lived REFRESH token (opaque, in DB/Redis, rotated) → stateful, revocable
  → gets you stateless speed + session-like revocation (logout within minutes)
Web: refresh token in HttpOnly cookie; access token in memory
Mobile: both in Keychain/Keystore
```

### Recommendations

```
Server-rendered web app / monolith (Next.js SSR, Django, Rails, Express + templates)
   → Session cookie (HttpOnly, Secure, SameSite=Lax) + Redis store. Simple, secure, instant logout.
SPA + own API on same site
   → Session cookie still great (BFF pattern); or access-in-memory + refresh cookie
Mobile apps + public API + microservices
   → Tokens: short JWT access + rotating refresh tokens
Third-party developers
   → OAuth 2.0 access tokens / API keys
```

## 🟢 कैसे काम करता है? (Hindi)
1. Session: login पर सर्वर Redis में session बनाता है और cookie में सिर्फ़ ID देता है; हर request पर ID से Redis में देखता है।
2. Logout पर session delete → तुरंत बाहर। रोल बदला तो अगली request से लागू।
3. Token: login पर signed JWT मिलता है; हर request पर सर्वर सिर्फ़ signature और expiry जाँचता है — कोई lookup नहीं।
4. Token mobile, microservices, दूसरे डोमेन के लिए बढ़िया; पर बीच में रद्द करना मुश्किल।
5. सबसे आम तरीका: छोटा JWT access token + DB में रखा, बदलने वाला refresh token — दोनों का फ़ायदा।

---

## 🟡 Real World Example

**GitHub, Basecamp, Shopify admin (web)** — classic server-side sessions with secure cookies. They're simple, and admins can instantly "sign out all sessions".

**Mobile-first apps (Swiggy, Zomato, Paytm, Uber)** — token-based: short-lived access tokens plus refresh tokens stored securely on the device, plus device binding. Sensitive actions require re-authentication (MPIN/biometric).

**Google** — uses session cookies for its own web properties (gmail.com), and OAuth/OIDC tokens for APIs and third-party apps. Both models in one company.

**Microservices at Netflix/Uber** — the edge gateway validates the user's session or token once, then passes a signed internal token (often a JWT) with identity to downstream services, so services don't each hit a session store.

## 🟡 Real Example Hindi में
GitHub और Shopify admin जैसे वेब ऐप session cookie इस्तेमाल करते हैं — "सारे devices से logout" तुरंत होता है।
Swiggy, Paytm जैसे mobile ऐप token इस्तेमाल करते हैं — छोटा access token + सुरक्षित refresh token, और बड़े काम पर MPIN/fingerprint दोबारा। Google दोनों तरीके एक साथ चलाता है।

---

## 🟠 My Stack Example

### Express — session auth with Redis (web app)
```js
import session from 'express-session';
import { RedisStore } from 'connect-redis';

app.set('trust proxy', 1);
app.use(session({
  store: new RedisStore({ client: redis, prefix: 'sess:' }),
  name: 'sid',
  secret: process.env.SESSION_SECRET,
  resave: false, saveUninitialized: false, rolling: true,           // extend on activity
  cookie: { httpOnly: true, secure: true, sameSite: 'lax', maxAge: 7 * 864e5 },
}));

app.post('/login', async (req, res) => {
  const user = await verifyCredentials(req.body.email, req.body.password);
  if (!user) return res.status(401).json({ error: 'INVALID_CREDENTIALS' });
  req.session.regenerate((err) => {                                  // prevent session fixation
    req.session.userId = user.id; req.session.role = user.role;
    res.json({ ok: true });
  });
});
const requireLogin = (req, res, next) => (req.session.userId ? next() : res.status(401).end());
app.post('/logout', (req, res) => req.session.destroy(() => res.clearCookie('sid').end()));

// "Log out all devices": keep a set of session ids per user
// SADD user_sessions:42 <sid>  →  on logout-all: SMEMBERS + DEL each sess:<sid>
```

### FastAPI — token auth for mobile
```python
@app.post("/auth/login")
async def login(body: LoginIn):
    user = await verify_credentials(body.email, body.password)
    if not user: raise HTTPException(401)
    return await issue_tokens(user, device_id=body.device_id)   # access JWT 15m + refresh (DB, rotated)

@app.get("/orders")
async def orders(user = Depends(current_user)):   # current_user verifies JWT (Topic 54)
    return await repo.orders_for(user["id"])
```

### Next.js — the BFF approach (best of both for web)
```
Browser ──cookie(sid, HttpOnly)──► Next.js server (route handlers / server actions)
                                      │ looks up session → gets user's access token
                                      └─ calls backend APIs with Bearer token (server-to-server)
Tokens never touch browser JS → no XSS token theft; backend APIs stay token-based.
(Auth.js "database" session strategy, or iron-session encrypted cookies)
```

### React Native — tokens in secure storage
```ts
await SecureStore.setItemAsync('refreshToken', rt, { keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY });
```

### CSRF protection when using cookies
```js
// SameSite=Lax blocks most cross-site POSTs. For extra safety on state-changing routes:
import { doubleCsrf } from 'csrf-csrf';
const { doubleCsrfProtection, generateToken } = doubleCsrf({ getSecret: () => CSRF_SECRET, cookieName: '__Host-csrf' });
app.get('/csrf-token', (req, res) => res.json({ token: generateToken(req, res) }));
app.post('/api/*', doubleCsrfProtection);
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between session-based and token-based authentication?**
A1: Session-based: the server stores session state (user ID, role) in a store like Redis and gives the client an opaque session ID, usually in an HttpOnly cookie, which is looked up on every request. Token-based: the server issues a self-contained signed token (JWT) carrying claims, which the client sends (usually in the Authorization header) and any server verifies by signature without a lookup. Sessions give easy revocation and fresh data. Tokens give stateless scaling and work across services and mobile.

**Q2: When would you choose sessions over JWTs?**
A2: For browser-based web apps on a single site or monolith (server-rendered pages or an SPA with a BFF), where cookies work naturally, HttpOnly cookies protect against token theft via XSS, and instant logout or revocation and immediate role changes matter (admin panels, banking web). Redis-backed sessions scale horizontally fine. JWTs add revocation complexity there without much benefit.

**Q3: When are tokens better?**
A3: Mobile apps (no natural cookie jar across domains), APIs consumed by third parties, microservices where many services must authenticate requests without a shared session store, cross-domain or multi-region setups, and server-to-server calls. Use short-lived access tokens with rotating, revocable refresh tokens to recover revocation ability.

**Q4: Cookies are vulnerable to CSRF and localStorage is vulnerable to XSS — what's the safest web setup?**
A4: Store credentials in HttpOnly, Secure cookies (JS can't read them, so XSS can't exfiltrate them) with `SameSite=Lax` or `Strict`, and add CSRF tokens for state-changing requests or rely on strict SameSite plus Origin checks. Keep any access token in memory only and obtain it via a refresh-cookie endpoint, or use a BFF so tokens never reach the browser. Prevent XSS with a CSP, output encoding, and avoiding `dangerouslySetInnerHTML`. Never put long-lived tokens in localStorage.

**Q5: How do you implement "log out from all devices"?**
A5: Sessions: track session IDs per user (a Redis set) and delete them all. Tokens: revoke all refresh tokens for the user in the DB, and to kill current access tokens immediately, bump a per-user `tokenVersion` (checked against a cached value) or add the active `jti`s to a denylist until expiry. Then require re-login. Also show active sessions or devices to the user so they can revoke individually.

---

## 🔷 Trade-offs
✅ Sessions: instant revocation, small cookies, fresh authorization data, HttpOnly security.
❌ Sessions: shared store lookups, cookie/CSRF handling, awkward for mobile/cross-domain/microservices.
✅ Tokens: stateless, scale across services/regions, mobile and 3rd-party friendly.
❌ Tokens: revocation complexity, larger requests, stale claims, risky storage on web.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Session | Server-stored login state | सर्वर पर रखी login जानकारी |
| Session ID | Random identifier in cookie | cookie में random ID |
| Stateful / Stateless | Server keeps / doesn't keep state | सर्वर याद रखता / नहीं रखता |
| HttpOnly cookie | Cookie JS can't read | JS से न पढ़ी जाने वाली cookie |
| SameSite | Limits cross-site cookie sending | दूसरी साइट से cookie न भेजना |
| CSRF | Forged cross-site request | नक़ली cross-site request |
| Session fixation | Attacker sets victim's session ID | हैकर का दिया session ID |
| BFF | Backend-for-frontend holding tokens | frontend का अपना backend |
| Revocation | Invalidating access | access रद्द करना |

---

## ⚡ 3-Line Summary
**English:**
1. Sessions = server-side state + session ID cookie (instant logout); tokens = self-contained signed JWTs (stateless, multi-service).
2. Web apps: HttpOnly session cookies (or BFF); mobile/microservices/APIs: short access JWT + rotating refresh token.
3. Mind CSRF with cookies and XSS with localStorage; support "log out all devices".

**Hindi:**
1. Session = सर्वर पर जानकारी + cookie में ID (तुरंत logout); Token = signed JWT (stateless, कई services)।
2. Web ऐप: HttpOnly session cookie; mobile/microservices: छोटा JWT + बदलने वाला refresh token।
3. Cookie में CSRF और localStorage में XSS का ध्यान; "सब devices से logout" ज़रूर दो।

---

## ➡️ Next Topic Suggestion
**58. RBAC — Role Based Access Control** — Now we know WHO the user is. Next: deciding WHAT they're allowed to do with roles and permissions, multi-tenant authorization, and enforcing it in Node, FastAPI and the UI.
