# F16. Auth on Frontend (Token Storage + Refresh Flow)
# हिंदी में: Frontend पर Auth — login के बाद मिले tokens को ब्राउज़र में कहाँ सुरक्षित रखें (memory, cookie, localStorage), और access token की मियाद ख़त्म होने पर यूज़र को logout किए बिना चुपचाप नया token कैसे लें (refresh flow)

---

## 🔵 Simple Definition (English)
After login, the frontend must **prove identity on every API call** and keep the user signed in safely:
- **Access token** (short-lived, e.g., 5–15 min, often a JWT): sent with API requests (`Authorization: Bearer …` or a cookie).
- **Refresh token** (long-lived, e.g., 7–30 days): used **only** to get new access tokens. It must be **protected the most** and **rotated** on each use.
- **Session cookie** (traditional): an opaque session id in an HttpOnly cookie, with state on the server.
Frontend auth design answers four questions:
1. **Where to store tokens?** Memory, HttpOnly cookie, localStorage/sessionStorage, or a BFF holding them server-side.
2. **How to refresh silently?** Interceptor on 401 or proactive refresh before expiry, single-flight.
3. **How to protect routes/UI?** Middleware/SSR checks, client guards.
4. **How to log out everywhere?** Revoke refresh tokens and sync across tabs.

## 🔵 सरल परिभाषा (Hindi)
Login के बाद हर API call पर पहचान साबित करनी है और यूज़र को सुरक्षित तरीके से logged-in रखना है। Access token छोटी उम्र का (5–15 मिनट) — हर request के साथ जाता है; Refresh token लंबी उम्र का (7–30 दिन) — सिर्फ़ नया access token लेने के लिए, सबसे ज़्यादा सुरक्षित रखना और हर बार बदलना (rotation)।
चार सवाल: tokens कहाँ रखें, चुपचाप refresh कैसे, pages/routes कैसे बचाएँ, और हर जगह से logout कैसे।

---

## 🔴 Problem it Solves
Naive approaches cause real breaches and bad UX:
- **JWT in localStorage**: any XSS (including a compromised npm package or analytics script) can read it and use it from anywhere until expiry.
- **Long-lived access tokens** (7 days) can't be revoked quickly when a phone is stolen.
- **No refresh flow**: users are logged out every 15 minutes, or a page fires 10 parallel requests that all hit 401 and trigger **10 refresh calls** (race, rotation conflicts, random logouts).
- **Cookies without CSRF protection**: forged requests (F14).
- **Client-only route guards**: protected page HTML/data flashes before the redirect, or the API trusts the UI.

A deliberate design balances **security (XSS/CSRF), UX (stay logged in) and architecture (SPA vs SSR vs mobile)**.

## 🔴 यह क्यों बना? (Hindi)
आसान पर ग़लत तरीके नुक़सान करते हैं: localStorage में JWT — कोई भी XSS (या ख़राब npm package) उसे पढ़कर कहीं से भी इस्तेमाल कर सकता है; 7 दिन का access token — फ़ोन चोरी होने पर जल्दी रद्द नहीं; refresh flow नहीं — हर 15 मिनट logout, या 10 requests एक साथ 401 → 10 बार refresh → random logout; CSRF सुरक्षा के बिना cookies; सिर्फ़ client पर route guard।
सोच-समझकर बना design सुरक्षा, UX और architecture (SPA/SSR/mobile) का संतुलन देता है।

---

## 🟢 How it Works — Step by Step

### Storage options compared

```
┌──────────────────────────┬────────────────────┬────────────────────┬──────────────────────────────┐
│ Where                    │ XSS can steal?     │ CSRF risk?         │ Notes                        │
├──────────────────────────┼────────────────────┼────────────────────┼──────────────────────────────┤
│ localStorage /           │ ✅ YES (any script)│ No (not auto-sent) │ Persists; easiest; worst for │
│ sessionStorage           │                    │                    │ long-lived tokens            │
│ JS memory (variable)     │ Harder (live XSS   │ No                 │ Lost on refresh → need       │
│                          │ can still use it)  │                    │ silent refresh via cookie    │
│ HttpOnly Secure cookie   │ ❌ No (JS can't    │ Yes → SameSite +   │ Auto-sent; best for refresh  │
│                          │ read it)           │ CSRF token         │ token or session id          │
│ BFF / server session     │ ❌ No tokens in    │ Yes → SameSite +   │ Most secure for web; tokens  │
│ (tokens never reach JS)  │ browser            │ CSRF token         │ stay on server               │
│ Mobile Keychain/Keystore │ N/A                │ N/A                │ React Native (Topic M16)     │
└──────────────────────────┴────────────────────┴────────────────────┴──────────────────────────────┘
Note: XSS is game over either way (attacker can make requests as the user while the page is open);
HttpOnly just prevents EXFILTRATING long-lived credentials for use elsewhere/later.
```

### Recommended pattern A — SPA with separate API (access in memory + refresh in HttpOnly cookie)

```
Login:  POST /auth/login {email, password/OTP}
        ← 200 { accessToken (15 min), user }                         → kept in memory
        ← Set-Cookie: refresh_token=…; HttpOnly; Secure; SameSite=Lax/Strict; Path=/auth  (only refresh/logout see it)
API:    Authorization: Bearer <accessToken>
401 /   ┌─ single-flight: first 401 starts POST /auth/refresh (cookie auto-sent), others WAIT on same promise
expiry  │  server: validate refresh token, ROTATE (issue new refresh, invalidate old), return new access
        └─ retry the original requests with the new token
Page reload: memory empty → on app start call /auth/refresh → get access token (silent login)
Reuse detection: if an OLD refresh token is used again → token theft suspected → revoke the whole family
Logout: POST /auth/logout → server revokes refresh token, clears cookie; BroadcastChannel → other tabs log out
```

### Recommended pattern B — Next.js / SSR or BFF (session cookie, tokens server-side)

```
Browser ──cookie: session=opaque (HttpOnly, Secure, SameSite=Lax)──► Next.js server / BFF
                                                                       │ looks up session (Redis)
                                                                       │ holds access/refresh tokens
                                                                       ▼
                                                              calls APIs with Bearer token
+ SSR can check auth before rendering (no flash of protected content)
+ No tokens in browser JS at all
- CSRF defence needed (SameSite + token for mutations), server session store
Libraries: Auth.js (NextAuth), Clerk, Auth0/Cognito SDKs, Lucia-style custom sessions
```

### OAuth / social login in SPAs

```
Use Authorization Code + PKCE (Topic 55) — never the implicit flow
"Login with Google" → redirect → code → exchanged by BFF/backend (preferred) or SPA with PKCE
ID token (OIDC) identifies the user; access token calls APIs; keep refresh tokens out of JS where possible
```

### Protecting routes & UI

```
Server/edge (authoritative): Next.js middleware checks session cookie → redirect to /login?next=/orders
Client (UX only): hide buttons the user can't use, show login prompt; the API must still authorize every call
Role-based UI: render based on claims/permissions from /me — never trust them for security
Token expiry UX: proactive refresh ~1 min before exp; on refresh failure → "Session expired, log in again"
                 preserve unsent form state/draft before redirecting
```

### Multi-tab & multi-device

```
BroadcastChannel('auth'): login/logout/refresh events → other tabs update (avoid every tab refreshing at once)
Lock refresh with navigator.locks.request('refresh', …) → only one tab refreshes
"Log out of all devices": server revokes all refresh tokens/sessions for user; access tokens die within 15 min
Show active sessions list (device, location, last used) — like Google/Netflix
```

## 🟢 कैसे काम करता है? (Hindi)
1. localStorage में token = XSS से चोरी; HttpOnly cookie को JS पढ़ ही नहीं सकती (पर CSRF सुरक्षा चाहिए); सबसे सुरक्षित — BFF/सर्वर tokens रखे, ब्राउज़र में सिर्फ़ session cookie।
2. SPA का अच्छा तरीका: access token memory में (15 मिनट), refresh token HttpOnly cookie में (सिर्फ़ `/auth` path पर — refresh और logout); page reload पर app start में चुपचाप refresh।
3. 401 आने पर single-flight: एक ही refresh call, बाक़ी requests उसी का इंतज़ार करें, फिर दोबारा भेजें; refresh token हर बार बदलो (rotation), पुराना दोबारा आए तो चोरी मानकर सब रद्द।
4. Route सुरक्षा असली में सर्वर/middleware पर (redirect `/login?next=`); client पर सिर्फ़ UX के लिए बटन छुपाना — API हर call पर ख़ुद जाँचे।
5. कई tabs: BroadcastChannel से login/logout की ख़बर, एक ही tab refresh करे; "सब devices से logout" के लिए सर्वर सारे refresh tokens रद्द करे।

---

## 🟡 Real World Example

**Auth0 / Okta guidance** — recommends against storing tokens in localStorage for SPAs. They suggest in-memory access tokens with refresh token rotation and reuse detection, or a BFF so tokens never reach the browser.

**Google, GitHub, Netflix web** — use HttpOnly session cookies plus server-side sessions, CSRF protections, and "manage devices / sign out everywhere" features.

**Next.js apps with Auth.js (NextAuth) or Clerk** — keep an encrypted HttpOnly session cookie. Middleware protects routes at the edge and Server Components read the session server-side, with no token handling in client JS.

**Indian fintech (Zerodha, Groww, banking apps)** — short sessions, re-authentication (PIN/2FA/biometric) for sensitive actions like trades, withdrawals and adding beneficiaries, device binding, and forced logout on password change.

## 🟡 Real Example Hindi में
Auth0/Okta सलाह देते हैं कि SPA में token localStorage में न रखें — memory में access token + rotation वाला refresh token, या BFF ताकि token ब्राउज़र तक पहुँचे ही नहीं।
Google/GitHub/Netflix HttpOnly session cookie और "सब devices से sign out" देते हैं; Zerodha/Groww/बैंकिंग ऐप छोटे sessions और ज़रूरी काम (trade, withdrawal, beneficiary) पर दोबारा PIN/2FA/biometric माँगते हैं।

---

## 🟠 My Stack Example

### Backend (Node/Express): login, rotating refresh, reuse detection
```js
app.post('/auth/login', async (req, res) => {
  const user = await verifyCredentials(req.body.email, req.body.password);     // + rate limit + 2FA
  if (!user) return res.status(401).json({ error: { code: 'INVALID_CREDENTIALS' } });
  const family = crypto.randomUUID();
  const refresh = await issueRefreshToken(user.id, family);                     // store hash in DB/Redis
  setRefreshCookie(res, refresh);
  res.json({ accessToken: signAccess(user, '15m'), user: publicUser(user) });
});

app.post('/auth/refresh', async (req, res) => {
  const presented = req.cookies.refresh_token;
  const record = await findRefreshToken(presented);                             // by hash
  if (!record) return res.status(401).end();
  if (record.usedAt) { await revokeFamily(record.family); return res.status(401).end(); }   // REUSE → theft
  await markUsed(record.id);
  const next = await issueRefreshToken(record.userId, record.family);           // rotation
  setRefreshCookie(res, next);
  res.json({ accessToken: signAccess(await getUser(record.userId), '15m') });
});

function setRefreshCookie(res, token) {
  res.cookie('refresh_token', token, { httpOnly: true, secure: true, sameSite: 'strict', path: '/auth', maxAge: 30 * 864e5 });  // sent only to /auth/* (refresh, logout)
}
```

### Frontend token store: memory + silent refresh + single-flight + multi-tab
```ts
// shared/tokenStore.ts
let accessToken: string | null = null;
let refreshPromise: Promise<string> | null = null;
const channel = new BroadcastChannel('auth');

export const tokenStore = {
  getAccess: () => accessToken,
  set(t: string | null) { accessToken = t; },
  async refresh(): Promise<string> {
    refreshPromise ??= navigator.locks.request('auth-refresh', async () => {       // one tab at a time
      const r = await fetch('/auth/refresh', { method: 'POST', credentials: 'include' });
      if (!r.ok) throw new Error('refresh failed');
      const { accessToken: t } = await r.json();
      accessToken = t; channel.postMessage({ type: 'refreshed' });
      return t;
    }).finally(() => (refreshPromise = null));
    return refreshPromise;
  },
  async logout() {
    await fetch('/auth/logout', { method: 'POST', credentials: 'include' });
    accessToken = null; channel.postMessage({ type: 'logout' });
  },
  clear() { accessToken = null; },
};
channel.onmessage = (e) => { if (e.data.type === 'logout') { accessToken = null; location.assign('/login'); } };

// App start: silent login if refresh cookie exists
export async function bootstrapAuth() { try { await tokenStore.refresh(); return true; } catch { return false; } }
```
(The 401 interceptor that calls `tokenStore.refresh()` is in F11's `http.ts`.)

### Proactive refresh before expiry (fewer 401s)
```ts
import { jwtDecode } from 'jwt-decode';
function scheduleRefresh(token: string) {
  const { exp } = jwtDecode<{ exp: number }>(token);
  const ms = exp * 1000 - Date.now() - 60_000;                 // 1 min early
  setTimeout(() => tokenStore.refresh().then(scheduleRefresh).catch(() => showSessionExpired()), Math.max(ms, 0));
}
```

### Next.js: protect routes in middleware (session cookie)
```ts
// middleware.ts
export function middleware(req: NextRequest) {
  const session = req.cookies.get('session')?.value;
  if (!session && req.nextUrl.pathname.startsWith('/account')) {
    const url = new URL('/login', req.url); url.searchParams.set('next', req.nextUrl.pathname);
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}
export const config = { matcher: ['/account/:path*', '/orders/:path*'] };
// Server Component: const user = await getSessionUser(); if (!user) redirect('/login');  ← authoritative check
```

### FastAPI: verify access token per request (the API is the real guard)
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

bearer = HTTPBearer()
def current_user(creds=Depends(bearer)):
    try:
        claims = jwt.decode(creds.credentials, PUBLIC_KEY, algorithms=["RS256"], audience="api.myapp.com")
    except jwt.PyJWTError:
        raise HTTPException(401, "invalid token")
    return claims

@app.get("/orders")
def orders(user=Depends(current_user)):
    return list_orders(user["sub"])
```

### React Native (preview of M16)
```
Store refresh token in Keychain/Keystore (expo-secure-store / react-native-keychain), access token in memory;
same single-flight refresh interceptor; biometric unlock gates access to the stored refresh token.
```

---

## ⚫ Interview Questions + Answers

**Q1: Where should a web SPA store JWTs?**
A1: Avoid localStorage for long-lived tokens, because any XSS or compromised script can read and exfiltrate them. A strong pattern keeps the short-lived access token in memory and the refresh token in an HttpOnly, Secure, SameSite cookie scoped to the refresh endpoint, with rotation and reuse detection. The app silently refreshes on load and on 401. Even better for many apps, a BFF or server session keeps tokens server-side and the browser only holds an HttpOnly session cookie. Cookie-based approaches need CSRF protection.

**Q2: Explain refresh token rotation and reuse detection.**
A2: Each time a refresh token is used, the server issues a new refresh token and invalidates the old one, tracking them in a family. If an already-used refresh token is presented again, it means two parties hold it (likely theft), so the server revokes the whole family and forces re-login. This limits the window in which a stolen refresh token is useful and detects compromise. Store only hashes of refresh tokens server-side.

**Q3: How do you avoid multiple simultaneous refresh calls?**
A3: Use single-flight: the first request that hits 401 starts the refresh and stores the promise, and all other failing requests await that same promise, then retry with the new token. Across tabs, coordinate with the Web Locks API or BroadcastChannel so only one tab refreshes and the others receive the result. Refreshing proactively shortly before expiry also reduces bursts of 401s. Without this, rotation can invalidate tokens mid-flight and cause random logouts.

**Q4: How should route protection work in a Next.js app?**
A4: The authoritative checks happen on the server. Middleware or edge redirects unauthenticated users before rendering, Server Components or route handlers verify the session and permissions for data, and the backend API authorizes every request. Client-side guards and hiding UI elements are only for UX. This avoids flashing protected content and prevents bypass by calling APIs directly. Preserve the destination with a `next` parameter, and validate it to prevent open redirects.

**Q5: How do you implement "log out from all devices"?**
A5: Server-side, revoke all refresh tokens or sessions for the user (or bump a token-version claim checked on refresh), so no device can get new access tokens. Existing short-lived access tokens expire within minutes, or are immediately rejected if you maintain a denylist or check token versions. Clear cookies on the current device and broadcast logout to other tabs. Offer a session management UI listing devices, and trigger it automatically on password change or suspected compromise.

---

## 🔷 Trade-offs
✅ Memory + HttpOnly refresh cookie: XSS can't exfiltrate long-lived token — ❌ refresh on reload, CSRF care, cross-domain cookie config.
✅ BFF/session: no tokens in browser, SSR-friendly — ❌ server state (Redis), BFF to operate.
✅ localStorage: simple, works cross-domain — ❌ token theft via XSS; only acceptable for low-risk apps with short TTLs.
✅ Short access TTL: fast revocation — ❌ more refresh traffic.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Access token | Short-lived API credential | छोटी उम्र का token |
| Refresh token | Long-lived token to get new access | नया token लेने वाला |
| Rotation | New refresh token on each use | हर बार नया refresh token |
| Reuse detection | Old refresh reused → revoke | पुराना दोबारा आए तो रद्द |
| HttpOnly | Cookie unreadable by JS | JS न पढ़ सके |
| SameSite | Limits cross-site sending | दूसरी साइट से न जाए |
| Silent refresh | Getting new token without user action | चुपचाप नया token |
| Single-flight | One refresh shared by all waiters | एक ही refresh सबके लिए |
| BFF session | Server holds tokens | सर्वर पर tokens |
| PKCE | Secure OAuth code flow for public clients | सुरक्षित OAuth तरीका |

---

## ⚡ 3-Line Summary
**English:**
1. Short-lived access token (memory) + rotating refresh token (HttpOnly Secure SameSite cookie), or a BFF/session so no tokens live in JS.
2. Silent refresh on app start and on 401 with single-flight + cross-tab locking; rotation with reuse detection; proactive refresh before expiry.
3. Authoritative checks on the server (middleware/SSR/API), client guards only for UX; broadcast logout and support "sign out everywhere".

**Hindi:**
1. छोटा access token memory में + बदलता refresh token HttpOnly cookie में, या BFF ताकि JS में token ही न हो।
2. App start और 401 पर चुपचाप refresh — एक ही बार (single-flight), tabs में lock; rotation + reuse detection।
3. असली जाँच सर्वर पर, client guard सिर्फ़ UX के लिए; logout सब tabs में, "सब devices से logout" की सुविधा।

---

## ➡️ Next Topic Suggestion
**F17. Image + Asset Optimization** — Images are usually the heaviest bytes on a page and often the LCP element. Next: formats, responsive images, lazy loading, CDNs, placeholders and fonts.
