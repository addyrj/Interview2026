# 55. OAuth 2.0
# हिंदी में: OAuth 2.0 — एक मानक तरीका जिससे कोई ऐप आपका password जाने बिना, आपकी अनुमति से, आपके डेटा तक सीमित पहुँच (access token) पा सके

---

## 🔵 Simple Definition (English)
**OAuth 2.0** is an **authorization framework** that lets a **client application** get **limited access** (scopes) to a user's resources on another service **without seeing the user's password**. The user logs in at the **authorization server** (e.g. Google), approves the requested permissions, and the app receives an **access token** to call the **resource server** (e.g. Google Drive API).
OAuth is about **authorization (what you can access)**. **Authentication (who you are)** is added on top by **OpenID Connect** (next topic).

## 🔵 सरल परिभाषा (Hindi)
OAuth 2.0 से कोई ऐप आपका password जाने बिना, आपकी इजाज़त से, आपके डेटा तक सीमित पहुँच पाता है।
आप Google पर login करके "Allow" दबाते हो, और ऐप को एक access token मिलता है जिससे वो सिर्फ़ इजाज़त वाला काम (जैसे contacts पढ़ना) कर सकता है।

---

## 🔴 Problem it Solves
Before OAuth (the "password anti-pattern"):
- A photo-printing app asked for your **Gmail/Flickr password** to fetch your photos.
- The app had **full access** to everything, forever.
- You couldn't revoke access for one app without changing your password everywhere.
- If the app was hacked, **your password leaked**.

OAuth 2.0 solves it with:
1. **Delegated access:** the app never sees your password.
2. **Scopes:** limited permission ("read photos" only).
3. **Expiring, revocable tokens** per app.
4. **Standard flows** for web apps, mobile apps, SPAs, devices (TVs) and server-to-server calls.

## 🔴 यह क्यों बना? (Hindi)
पहले फ़ोटो प्रिंट करने वाला ऐप आपका Gmail password माँगता था — उसे सब कुछ हमेशा के लिए मिल जाता था, और ऐप हैक हुआ तो password भी गया।
OAuth में ऐप को password नहीं मिलता, सिर्फ़ सीमित (scope) और expire होने वाला token मिलता है, जिसे आप कभी भी रद्द कर सकते हो।

---

## 🟢 How it Works — Step by Step

### The 4 roles

```
Resource Owner      → the USER (you)
Client              → the app wanting access (your Next.js / React Native app, or a third-party app)
Authorization Server→ issues tokens after user consents (Google, GitHub, Auth0, Keycloak, Cognito)
Resource Server     → API holding the data (Google Drive API, GitHub API, YOUR API)
```

### Authorization Code flow + PKCE (the one to know — for web AND mobile)

```
 User          Client App (RN / Next.js)           Authorization Server (Google)        Resource API
  │  tap "Login with Google"  │                                │                              │
  │──────────────────────────►│ 1. create code_verifier (random)                              │
  │                           │    code_challenge = SHA256(verifier)                          │
  │                           │ 2. redirect browser to:                                        │
  │                           │  /authorize?response_type=code&client_id=..&redirect_uri=..   │
  │                           │  &scope=openid email profile&state=xyz                        │
  │                           │  &code_challenge=..&code_challenge_method=S256 ───────────────►│
  │◄────────────────── 3. login page + consent screen ("Allow MyApp to see your email?") ─────│
  │── 4. user logs in & approves ─────────────────────────────────────────────────────────────►│
  │                           │◄── 5. redirect to redirect_uri?code=AUTH_CODE&state=xyz ───────│
  │                           │ 6. check state matches (CSRF protection)                       │
  │                           │ 7. POST /token  code + code_verifier (+ client_secret if       │
  │                           │    confidential server) ──────────────────────────────────────►│
  │                           │                       8. verify SHA256(verifier)==challenge     │
  │                           │◄── 9. { access_token, refresh_token, id_token (OIDC), expires_in }
  │                           │ 10. GET /api/data  Authorization: Bearer access_token ─────────────────────────►│
  │                           │◄────────────────────────────────────────────────── data ─────────────────────────│

Why the "code" step? The access token is never exposed in the browser URL/history.
Why PKCE? Mobile apps & SPAs can't keep a client_secret. PKCE proves the app that started
the flow is the one redeeming the code → an intercepted code is useless.
```

### Grant types (flows)

```
┌──────────────────────────────┬──────────────────────────────────────────────┬──────────────┐
│ Grant type                   │ Used for                                     │ Status       │
├──────────────────────────────┼──────────────────────────────────────────────┼──────────────┤
│ Authorization Code + PKCE    │ Web apps, SPAs, mobile apps (users present)  │ ✅ default   │
│ Client Credentials           │ Server-to-server, no user (cron, microservice│ ✅           │
│                              │ calling another API with its own identity)   │              │
│ Refresh Token                │ Get new access token without re-login        │ ✅           │
│ Device Authorization         │ TVs, CLIs, IoT ("go to google.com/device,    │ ✅           │
│                              │ enter code ABCD-EFGH")                       │              │
│ Implicit                     │ Old SPAs (token in URL fragment)             │ ❌ deprecated│
│ Resource Owner Password      │ App collects user's password directly        │ ❌ deprecated│
└──────────────────────────────┴──────────────────────────────────────────────┴──────────────┘
OAuth 2.1 (consolidation) → PKCE required for all code flows, implicit & password removed.
```

### Scopes & consent
```
scope=read:orders write:orders      ← app asks for specific permissions
Consent screen shows them → user approves → token carries scopes
Resource server enforces: endpoint requires "write:orders" scope
Principle of least privilege: ask only what you need (Google may require app verification for sensitive scopes)
```

### Client types
```
Confidential client → can keep a secret (your backend server). Uses client_secret / private_key_jwt.
Public client       → can't keep secrets (SPA JS, mobile app binary can be decompiled). MUST use PKCE.
```

### Token types
```
Access token  → short-lived, sent to resource server (opaque string or JWT)
Refresh token → long-lived, exchanged at token endpoint (rotate it)
ID token      → (OIDC only) JWT describing the user's identity — for the CLIENT, not for APIs
Token introspection (RFC 7662) → resource server asks auth server "is this opaque token valid?"
```

### Security essentials
```
✓ state parameter (anti-CSRF) and validate it
✓ PKCE (S256) for every public client — and recommended for confidential too
✓ Exact redirect_uri matching (registered list) — open redirects = stolen codes
✓ Use system browser / ASWebAuthenticationSession / Custom Tabs on mobile, NOT embedded WebViews
✓ Short-lived access tokens; rotate refresh tokens; store securely
✓ Validate tokens on resource server: signature/introspection, exp, aud, scopes
```

## 🟢 कैसे काम करता है? (Hindi)
1. यूज़र "Login with Google" दबाता है → ऐप browser को Google के `/authorize` पर भेजता है (scopes, state, PKCE challenge के साथ)।
2. यूज़र Google पर login करके "Allow" करता है; Google ऐप को एक छोटा "authorization code" लौटाता है।
3. ऐप वो code + PKCE verifier Google के `/token` पर भेजकर access token (और refresh token) लेता है।
4. ऐप access token से API कॉल करता है; API token और उसके scopes जाँचती है।
5. Mobile/SPA secret नहीं रख सकते, इसलिए PKCE ज़रूरी है; बिना यूज़र वाले server-to-server काम के लिए Client Credentials flow।

---

## 🟡 Real World Example

**"Sign in with Google/Apple/GitHub"** — Authorization Code + PKCE with OpenID Connect on top. Apps like Swiggy, Zomato, Canva and Notion use it, so users never type a new password.

**GitHub Apps / Slack apps / Zapier** — third-party integrations request scopes (e.g. `repo:read`, `chat:write`) via OAuth. Users can revoke them anytime from settings.

**Account Aggregator framework (India)** — consent-based sharing of financial data between banks and fintech apps follows the same principles: explicit consent, a limited scope and duration, and revocable access, without sharing banking passwords.

**Smart TVs (YouTube, Netflix login)** — the "enter this code at youtube.com/activate" screen is the OAuth Device Authorization grant.

**Facebook "View As" breach (2018)** — a bug let attackers obtain access tokens for ~50 million accounts. Facebook invalidated all of them, forcing re-login. Tokens are powerful credentials, so revocation capability matters.

## 🟡 Real Example Hindi में
"Login with Google" OAuth (+ OIDC) है — Swiggy, Canva, Notion में नया password नहीं बनाना पड़ता। Smart TV पर "यह code youtube.com/activate पर डालो" Device flow है।
भारत का Account Aggregator सिस्टम भी इसी सोच पर है — सीमित समय और scope की सहमति, बिना बैंक password साझा किए।

---

## 🟠 My Stack Example

### React Native (Expo) — Login with Google via Auth Code + PKCE
```tsx
import * as AuthSession from 'expo-auth-session';
import * as WebBrowser from 'expo-web-browser';
WebBrowser.maybeCompleteAuthSession();

const discovery = AuthSession.useAutoDiscovery('https://accounts.google.com');
const redirectUri = AuthSession.makeRedirectUri({ scheme: 'myapp' });   // myapp://redirect

const [request, response, promptAsync] = AuthSession.useAuthRequest(
  { clientId: GOOGLE_CLIENT_ID, redirectUri, scopes: ['openid', 'email', 'profile'], usePKCE: true },
  discovery
);

useEffect(() => {
  if (response?.type === 'success') {
    // Send the code + verifier to YOUR backend → it exchanges with Google, verifies id_token,
    // creates/links the user, and issues YOUR app's own access/refresh tokens.
    api.post('/auth/google', { code: response.params.code, codeVerifier: request!.codeVerifier, redirectUri });
  }
}, [response]);
```
(It opens the **system browser** session, not a WebView, so Google can block phishing.)

### Node backend — exchange code, verify, issue your own tokens
```js
import { OAuth2Client } from 'google-auth-library';
const google = new OAuth2Client(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET);

app.post('/auth/google', async (req, res) => {
  const { code, codeVerifier, redirectUri } = req.body;
  const { tokens } = await google.getToken({ code, codeVerifier, redirect_uri: redirectUri });
  const ticket = await google.verifyIdToken({ idToken: tokens.id_token, audience: GOOGLE_CLIENT_ID });
  const p = ticket.getPayload();                       // { sub, email, email_verified, name, picture }
  if (!p.email_verified) return res.status(403).end();

  const user = await upsertUserByProvider('google', p.sub, { email: p.email, name: p.name, avatar: p.picture });
  const appTokens = await issueTokens(user, req.headers['x-device-id']);   // Topic 54
  res.json(appTokens);
});
```

### Next.js — Auth.js (NextAuth) does the OAuth dance for you
```ts
// auth.ts
import NextAuth from 'next-auth';
import Google from 'next-auth/providers/google';
import GitHub from 'next-auth/providers/github';
export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [Google, GitHub],          // Authorization Code + PKCE + state handled
  session: { strategy: 'jwt' },
  callbacks: { async jwt({ token, account, profile }) { /* link to your DB user */ return token; } },
});
// app/api/auth/[...nextauth]/route.ts → export const { GET, POST } = handlers;
```

### Your API as an OAuth Resource Server — enforce scopes
```js
function requireScope(scope) {
  return (req, res, next) => (req.auth?.scope?.split(' ').includes(scope) ? next() : res.status(403).json({ error: 'insufficient_scope' }));
}
app.post('/api/v1/orders', authenticate, requireScope('write:orders'), createOrder);
```

### Service-to-service: Client Credentials (FastAPI calling a partner API)
```python
async def get_partner_token():
    if (t := await r.get("partner:token")): return t
    async with httpx.AsyncClient() as c:
        resp = await c.post("https://auth.partner.com/oauth/token", data={
            "grant_type": "client_credentials", "client_id": CID, "client_secret": CSECRET, "scope": "shipments:write"})
    tok = resp.json()
    await r.set("partner:token", tok["access_token"], ex=tok["expires_in"] - 60)   # cache until near expiry
    return tok["access_token"]
```

---

## ⚫ Interview Questions + Answers

**Q1: What is OAuth 2.0 and what problem does it solve?**
A1: An authorization framework for delegated access. A client app obtains a scoped, time-limited access token from an authorization server, after the resource owner (the user) authenticates there and consents, and uses it to call a resource server's API. It removes the need to share passwords with third-party apps, limits access by scope, and lets users revoke access per app.

**Q2: Explain the Authorization Code flow with PKCE.**
A2: The client generates a random code_verifier and its SHA-256 code_challenge, then redirects the user to the authorize endpoint with client_id, redirect_uri, scopes, state and the challenge. The user logs in and consents, and the auth server redirects back with a short-lived authorization code. The client validates state and posts the code plus code_verifier (plus a secret if confidential) to the token endpoint. The server checks the verifier against the challenge and returns access and refresh tokens (plus an ID token with OIDC). PKCE stops an intercepted code from being redeemed by an attacker. It's mandatory for mobile and SPA public clients.

**Q3: What's the difference between authentication and authorization, and where does OAuth fit?**
A3: Authentication proves who the user is. Authorization decides what they may access. OAuth 2.0 is an authorization protocol: an access token says "this client may do X on the user's behalf", not reliably who the user is. Using OAuth access tokens as proof of identity led to vulnerabilities, so OpenID Connect adds a standard authentication layer on top: an ID token (a signed JWT) and a userinfo endpoint.

**Q4: Which OAuth flow would you use for (a) a mobile app, (b) a cron job calling an API, (c) a smart TV?**
A4: (a) Authorization Code + PKCE using the system browser (ASWebAuthenticationSession or Custom Tabs), with tokens in Keychain/Keystore. (b) Client Credentials: the service authenticates as itself with client_id and secret (or a private key JWT or mTLS) and gets a scoped token, with no user involved. (c) The Device Authorization grant: the TV shows a code and URL, the user approves on their phone, and the TV polls the token endpoint.

**Q5: Why were the Implicit and Password grants deprecated?**
A5: Implicit returned access tokens directly in the URL fragment, exposing them to browser history, referrers and malicious scripts, with no way to bind the token to the client and no refresh tokens. Code + PKCE now works safely in browsers. The Password grant requires the app to collect the user's credentials directly, which defeats OAuth's purpose, trains users to type passwords into third-party apps, and can't support MFA or SSO properly. OAuth 2.1 removes both.

---

## 🔷 Trade-offs
✅ Advantages:
- No password sharing; scoped, expiring, revocable access; standard across providers.
- Enables SSO/social login (with OIDC), third-party integrations, machine-to-machine auth.

❌ Disadvantages:
- Complex spec with many flows; easy to misconfigure (redirect URIs, missing state/PKCE).
- Redirect-based UX; mobile deep-link handling needed.
- Depends on authorization server availability.
- OAuth alone isn't authentication — need OIDC.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OAuth 2.0 | Delegated authorization framework | अनुमति देने का मानक |
| Resource Owner | The user | डेटा का मालिक (यूज़र) |
| Client | App requesting access | पहुँच माँगने वाला ऐप |
| Authorization Server | Issues tokens | टोकन देने वाला सर्वर |
| Resource Server | API holding data | डेटा वाली API |
| Scope | Permission requested | माँगी गई अनुमति |
| Authorization Code | Temporary code exchanged for tokens | टोकन के बदले का अस्थायी code |
| PKCE | Proof key protecting code exchange | code चोरी से बचाने का तरीका |
| Client Credentials | Server-to-server grant | सर्वर से सर्वर अनुमति |
| Consent | User approval screen | यूज़र की सहमति |

---

## ⚡ 3-Line Summary
**English:**
1. OAuth 2.0 lets apps get scoped, revocable access tokens without the user's password (roles: owner, client, auth server, resource server).
2. Use Authorization Code + PKCE for web/mobile, Client Credentials for services, Device flow for TVs; implicit/password are deprecated.
3. Validate state, exact redirect URIs, use the system browser on mobile, enforce scopes — and add OIDC for login.

**Hindi:**
1. OAuth 2.0 से ऐप को बिना password के सीमित, रद्द हो सकने वाला access token मिलता है।
2. Web/mobile: Authorization Code + PKCE; services: Client Credentials; TV: Device flow।
3. State और redirect URI जाँचो, mobile पर system browser, scopes लागू करो — login के लिए OIDC जोड़ो।

---

## ➡️ Next Topic Suggestion
**56. OpenID Connect** — OAuth gives access, not identity. Next: how OIDC adds a standard ID token so "Login with Google" can safely tell your app WHO the user is, plus discovery, JWKS and SSO.
