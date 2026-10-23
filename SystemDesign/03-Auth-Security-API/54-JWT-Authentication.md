# 54. JWT Authentication
# हिंदी में: JWT — एक हस्ताक्षरित (signed) टोकन जिसमें यूज़र की जानकारी होती है; सर्वर हर बार DB देखे बिना उसे जाँचकर यूज़र को पहचान लेता है

---

## 🔵 Simple Definition (English)
A **JWT (JSON Web Token)** is a compact, URL-safe token with three parts: **header.payload.signature**. The payload holds **claims** (user id, role, expiry). The server **signs** it with a secret or private key; on each request the client sends it (usually `Authorization: Bearer <token>`), and the server **verifies the signature** to trust the claims **without a database lookup**.
JWTs are **signed, not encrypted**: anyone can read the payload.

## 🔵 सरल परिभाषा (Hindi)
JWT एक टोकन है जिसके तीन हिस्से होते हैं — header, payload (यूज़र id, role, expiry) और signature।
सर्वर इसे अपनी secret key से साइन करता है; हर request में ऐप यह टोकन भेजता है और सर्वर बिना DB देखे signature जाँचकर यूज़र को पहचान लेता है। ध्यान: payload कोई भी पढ़ सकता है, इसलिए उसमें password जैसी चीज़ें कभी नहीं।

---

## 🔴 Problem it Solves
HTTP is stateless (Topic 5), so the server must identify the user on **every request**:
- **Server sessions** need a session store lookup (Redis/DB) for every request and **sticky** or shared state across servers.
- **Microservices**: every service would need to call the auth service or share the session DB.
- **Mobile apps / third-party APIs** don't use cookies naturally.

A JWT is **self-contained**: any server or service with the key can verify it locally. It gives **stateless, scalable auth** across many services, domains and clients (web, iOS, Android).

## 🔴 यह क्यों बना? (Hindi)
HTTP stateless है — हर request पर यूज़र पहचानना पड़ता है। Session में हर बार Redis/DB देखना पड़ता है, और microservices में हर service को auth service से पूछना पड़ता।
JWT अपने अंदर सारी जानकारी रखता है — कोई भी सर्वर key से उसे ख़ुद जाँच सकता है। इससे web, mobile, microservices सबके लिए stateless auth मिलता है।

---

## 🟢 How it Works — Step by Step

### Structure

```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImsxIn0 . eyJzdWIiOiI0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzI5MjU... . SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
└──────────── HEADER (base64url) ───────────┘   └────────── PAYLOAD (base64url) ──────────┘   └──── SIGNATURE ────┘

HEADER   { "alg": "RS256", "typ": "JWT", "kid": "k1" }
PAYLOAD  { "sub": "42", "role": "user", "iss": "https://auth.myapp.com", "aud": "myapp-api",
           "iat": 1729250000, "exp": 1729250900, "jti": "a1b2c3" }
SIGNATURE = RSA_SHA256( base64url(header) + "." + base64url(payload), privateKey )

Standard claims: sub (user id), iss (issuer), aud (audience), exp (expiry), iat (issued at),
                 nbf (not before), jti (unique token id)
```

### Login + request flow

```
 RN App / Next.js                 Auth API                        Resource API (orders)
     │ 1. POST /login (email, pw)    │                                   │
     │──────────────────────────────►│ 2. verify password (bcrypt)       │
     │                               │ 3. sign access JWT (15 min)       │
     │                               │    + refresh token (7–30 days)    │
     │◄── {accessToken, refreshToken}│                                   │
     │ 4. GET /orders  Authorization: Bearer <access JWT>                │
     │──────────────────────────────────────────────────────────────────►│
     │                               5. verify signature with PUBLIC key  │
     │                                  check exp, iss, aud               │
     │                                  → req.user = { id: 42, role }     │
     │◄──────────────────────────────────────────────── 200 orders ──────│
     │ 6. access expired → POST /refresh (refreshToken)                  │
     │──────────────────────────────►│ 7. validate & ROTATE refresh token │
     │◄── new access + new refresh ──│                                   │
```

### Access token vs refresh token

```
┌──────────────────┬──────────────────────────────┬───────────────────────────────────┐
│                  │ Access token (JWT)           │ Refresh token                     │
├──────────────────┼──────────────────────────────┼───────────────────────────────────┤
│ Purpose          │ Call APIs                    │ Get new access tokens             │
│ Lifetime         │ Short: 5–15 min              │ Long: 7–90 days                   │
│ Sent to          │ Every API                    │ Only the auth/refresh endpoint    │
│ Format           │ JWT (stateless)              │ Opaque random string, stored in DB│
│                  │                              │ (hashed) → revocable              │
│ If stolen        │ Usable until expiry (short)  │ Rotation + reuse detection        │
└──────────────────┴──────────────────────────────┴───────────────────────────────────┘
Refresh token ROTATION: each use returns a NEW refresh token and invalidates the old one.
If an OLD one is reused → token theft detected → revoke the whole token family (log out user).
```

### Signing algorithms

```
HS256 (HMAC + shared secret)  → same secret signs & verifies; OK for ONE service/monolith
RS256 / ES256 / EdDSA (asymmetric) → auth server signs with PRIVATE key; any service verifies with
                                PUBLIC key (published at /.well-known/jwks.json) ✅ microservices
kid header → which key signed it → enables key ROTATION
```

### Revocation problem (JWT's biggest weakness)
```
A JWT is valid until exp — server doesn't store it. Logout / ban / role change won't apply instantly.
Mitigations:
  - Short access token lifetime (5–15 min) + revocable refresh token
  - Denylist of revoked jti in Redis (check per request — small, TTL = remaining lifetime)
  - Token version per user (tokenVersion claim vs DB/cache value) → bump to invalidate all
```

### Security checklist (common JWT vulnerabilities)
```
✗ alg: "none" accepted        → always specify allowed algorithms when verifying
✗ RS256 → HS256 confusion     → attacker signs with PUBLIC key as HMAC secret; pin algorithm
✗ Weak HS256 secret           → brute-forceable; use ≥ 256-bit random secret
✗ Sensitive data in payload   → it's only base64! no PII/passwords
✗ Not checking exp/iss/aud    → accept tokens for other apps
✗ Long-lived access tokens    → stolen token works for days
✗ Storing in localStorage     → readable by any XSS script (web) → prefer HttpOnly cookie
✓ HTTPS only, short expiry, rotation, key rotation via kid/JWKS
```

### Where to store tokens

```
Web (Next.js):
  ✅ Refresh token in HttpOnly + Secure + SameSite cookie (JS can't read → XSS-safe)
  ✅ Access token in memory (JS variable) or also HttpOnly cookie (then CSRF protection needed)
  ❌ localStorage / sessionStorage for long-lived tokens (XSS can steal)
Mobile (React Native):
  ✅ expo-secure-store / react-native-keychain (iOS Keychain, Android Keystore)
  ❌ AsyncStorage (plain text on device)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Login पर सर्वर password जाँचकर दो चीज़ें देता है: छोटा access token (JWT, 15 मिनट) और लंबा refresh token।
2. हर API request में `Authorization: Bearer <JWT>` भेजो; सर्वर signature, expiry, issuer, audience जाँचकर यूज़र पहचानता है — DB नहीं देखना पड़ता।
3. Access token expire हुआ तो refresh token से नया लो; refresh token हर बार बदलता है (rotation), पुराना दोबारा आए तो चोरी समझो।
4. Microservices के लिए RS256: auth सर्वर private key से साइन करे, बाक़ी services public key (JWKS) से जाँचें।
5. कमज़ोरी: JWT को बीच में रद्द करना मुश्किल — इसलिए छोटी expiry, Redis denylist; web पर HttpOnly cookie, mobile पर Keychain/Keystore।

---

## 🟡 Real World Example

**Auth0, AWS Cognito, Firebase Auth, Supabase, Clerk** — all issue JWT access tokens (RS256) with JWKS endpoints, so your APIs verify tokens locally without calling the provider on every request.

**Google / Microsoft APIs** — OAuth access tokens and OpenID Connect ID tokens are JWTs signed with rotating keys published at `/.well-known/openid-configuration` → `jwks_uri`.

**The "alg: none" vulnerability (2015)** — several popular JWT libraries accepted tokens with `"alg": "none"` (no signature), letting attackers forge any user's token. Library defaults were fixed, and this is why you must always pin algorithms.

**Indian fintech apps** — use short-lived access tokens (often 5–15 min) plus device-bound refresh tokens stored in Keychain/Keystore, with re-auth (MPIN, biometrics) for sensitive actions.

## 🟡 Real Example Hindi में
Auth0, Cognito, Firebase, Supabase — सब RS256 JWT देते हैं और JWKS पर public key रखते हैं, ताकि आपकी API बिना उनसे पूछे टोकन जाँच ले।
2015 में कई JWT libraries `"alg": "none"` वाला टोकन (बिना signature) मान लेती थीं — हैकर किसी का भी टोकन बना सकता था। इसलिए verify करते समय algorithm हमेशा तय करो।

---

## 🟠 My Stack Example

### Node.js — issue & verify with `jose` (RS256)
```js
import { SignJWT, jwtVerify, importPKCS8, createRemoteJWKSet } from 'jose';
import crypto from 'node:crypto';

const privateKey = await importPKCS8(process.env.JWT_PRIVATE_KEY, 'RS256');
const ISS = 'https://auth.myapp.com', AUD = 'myapp-api';

export async function issueTokens(user, deviceId) {
  const accessToken = await new SignJWT({ role: user.role })
    .setProtectedHeader({ alg: 'RS256', kid: 'k1' })
    .setSubject(String(user.id)).setIssuer(ISS).setAudience(AUD)
    .setIssuedAt().setExpirationTime('15m').setJti(crypto.randomUUID())
    .sign(privateKey);

  const refreshToken = crypto.randomBytes(32).toString('base64url');            // opaque
  await db.query(
    'INSERT INTO refresh_tokens(token_hash, user_id, device_id, family_id, expires_at) VALUES ($1,$2,$3,$4, now() + interval \'30 days\')',
    [sha256(refreshToken), user.id, deviceId, crypto.randomUUID()]);
  return { accessToken, refreshToken };
}

// any service: verify via JWKS (public keys), pin alg, check iss/aud/exp
const JWKS = createRemoteJWKSet(new URL(`${ISS}/.well-known/jwks.json`));
export async function authenticate(req, res, next) {
  const token = req.headers.authorization?.replace(/^Bearer /, '');
  if (!token) return res.status(401).json({ error: 'NO_TOKEN' });
  try {
    const { payload } = await jwtVerify(token, JWKS, { issuer: ISS, audience: AUD, algorithms: ['RS256'] });
    if (await redis.exists(`revoked:${payload.jti}`)) return res.status(401).json({ error: 'REVOKED' });
    req.user = { id: payload.sub, role: payload.role };
    next();
  } catch (e) {
    return res.status(401).json({ error: e.code === 'ERR_JWT_EXPIRED' ? 'TOKEN_EXPIRED' : 'INVALID_TOKEN' });
  }
}
```

### Refresh with rotation + reuse detection
```js
app.post('/auth/refresh', async (req, res) => {
  const token = req.cookies.refreshToken ?? req.body.refreshToken;
  const { rows: [rt] } = await db.query('SELECT * FROM refresh_tokens WHERE token_hash = $1', [sha256(token)]);
  if (!rt || rt.expires_at < new Date()) return res.status(401).end();
  if (rt.used_at) {                                                     // REUSE → theft!
    await db.query('UPDATE refresh_tokens SET revoked = true WHERE family_id = $1', [rt.family_id]);
    return res.status(401).json({ error: 'TOKEN_REUSE_DETECTED' });
  }
  if (rt.revoked) return res.status(401).end();
  await db.query('UPDATE refresh_tokens SET used_at = now() WHERE id = $1', [rt.id]);
  const user = await getUser(rt.user_id);
  const tokens = await issueTokens(user, rt.device_id);                 // (same family_id in real code)
  setRefreshCookie(res, tokens.refreshToken);
  res.json({ accessToken: tokens.accessToken });
});

function setRefreshCookie(res, token) {
  res.cookie('refreshToken', token, { httpOnly: true, secure: true, sameSite: 'strict', path: '/auth/refresh', maxAge: 30 * 864e5 });
}
```

### FastAPI — verify (PyJWT)
```python
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
bearer = HTTPBearer()
jwks = jwt.PyJWKClient("https://auth.myapp.com/.well-known/jwks.json")

async def current_user(creds = Depends(bearer)):
    try:
        key = jwks.get_signing_key_from_jwt(creds.credentials).key
        p = jwt.decode(creds.credentials, key, algorithms=["RS256"],
                       audience="myapp-api", issuer="https://auth.myapp.com")
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "TOKEN_EXPIRED")
    except jwt.PyJWTError:
        raise HTTPException(401, "INVALID_TOKEN")
    return {"id": p["sub"], "role": p.get("role")}
```

### React Native — secure storage + auto refresh (axios)
```ts
import * as SecureStore from 'expo-secure-store';
let accessToken: string | null = null;           // in memory
let refreshing: Promise<string> | null = null;   // single-flight refresh

api.interceptors.request.use((c) => { if (accessToken) c.headers.Authorization = `Bearer ${accessToken}`; return c; });
api.interceptors.response.use(undefined, async (err) => {
  if (err.response?.status !== 401 || err.config._retry) throw err;
  err.config._retry = true;
  refreshing ??= (async () => {
    const rt = await SecureStore.getItemAsync('refreshToken');
    const { data } = await axios.post(`${API}/auth/refresh`, { refreshToken: rt });
    await SecureStore.setItemAsync('refreshToken', data.refreshToken);
    accessToken = data.accessToken;
    return accessToken;
  })().finally(() => { refreshing = null; });
  await refreshing;                                // many 401s → ONE refresh call
  return api(err.config);
});
```

### Next.js — HttpOnly cookies, verify in middleware
```ts
// middleware.ts (edge) — protect routes
import { jwtVerify, createRemoteJWKSet } from 'jose';
const JWKS = createRemoteJWKSet(new URL('https://auth.myapp.com/.well-known/jwks.json'));
export async function middleware(req: NextRequest) {
  const t = req.cookies.get('access')?.value;
  try { await jwtVerify(t!, JWKS, { issuer: 'https://auth.myapp.com', audience: 'myapp-api' }); return NextResponse.next(); }
  catch { return NextResponse.redirect(new URL('/login', req.url)); }
}
export const config = { matcher: ['/dashboard/:path*'] };
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a JWT and how is it verified?**
A1: A token of the form base64url(header).base64url(payload).signature. The payload carries claims (sub, role, exp, iss, aud). The issuer signs header plus payload with an HMAC secret (HS256) or a private key (RS256/ES256). A server verifies by recomputing or validating the signature with the secret or public key, pinning the expected algorithm, then checking exp, nbf, iss and aud. If valid, it trusts the claims without a DB lookup.

**Q2: Why use short-lived access tokens with refresh tokens?**
A2: JWTs can't easily be revoked before expiry, so a short lifetime (5–15 min) limits the damage if one is stolen. Refresh tokens are long-lived but stored server-side (hashed), revocable, sent only to the auth endpoint, and rotated on each use, with reuse detection to catch theft. This combines stateless, fast API auth with the ability to log users out, ban them or change roles within minutes.

**Q3: How do you log out a user or revoke a JWT?**
A3: Revoke the refresh token (delete or mark revoked in the DB) so no new access tokens can be issued. The current access token stays valid until it expires (short). For immediate revocation, keep a Redis denylist of revoked `jti`s with a TTL equal to the remaining lifetime, or compare a per-user `tokenVersion` claim with the current value (cached). On "logout all devices", revoke all refresh tokens and bump tokenVersion.

**Q4: Where should a web app store JWTs? What about mobile?**
A4: Web: avoid localStorage for long-lived tokens, because any XSS can read it. Prefer HttpOnly, Secure, SameSite cookies for the refresh token (and optionally the access token, then add CSRF protection), or keep the access token in memory and refresh silently via the cookie. Mobile: use the OS secure storage (iOS Keychain, Android Keystore via expo-secure-store or react-native-keychain), never AsyncStorage. In both cases use HTTPS only and short expiry.

**Q5: HS256 vs RS256 — when to use which?**
A5: HS256 uses one shared secret for signing and verifying. It's simple and fast, fine when a single service both issues and verifies, but every verifier holds the signing power, so a leak anywhere lets an attacker mint tokens. RS256/ES256 use a private key to sign (only the auth server) and a public key to verify (any service, distributed via JWKS), which is better for microservices and third parties and allows key rotation via `kid`. Always pin the algorithm to prevent algorithm-confusion attacks.

---

## 🔷 Trade-offs
✅ Advantages:
- Stateless verification (no DB/session lookup), scales across services/regions.
- Works for web, mobile, third-party APIs; carries claims (role, tenant).
- Asymmetric keys let many services verify without sharing secrets.

❌ Disadvantages:
- Hard to revoke instantly; stale claims until expiry.
- Larger than session IDs (sent on every request).
- Payload is readable — no secrets inside.
- Easy to misconfigure (alg confusion, no aud check, long expiry, localStorage).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JWT | Signed JSON token | हस्ताक्षरित टोकन |
| Claims | Data in payload (sub, exp) | टोकन के अंदर की जानकारी |
| Signature | Proof token wasn't altered | छेड़छाड़ न होने का प्रमाण |
| Access token | Short-lived token for APIs | API के लिए छोटा टोकन |
| Refresh token | Long-lived token to get new access | नया टोकन लेने वाला लंबा टोकन |
| Token rotation | New refresh token each use | हर बार नया refresh token |
| JWKS | Published public keys | सार्वजनिक keys की सूची |
| kid | Key ID in header | कौन-सी key से साइन हुआ |
| Revocation | Invalidating a token | टोकन रद्द करना |
| Bearer token | "Whoever holds it can use it" | जिसके पास टोकन, वही इस्तेमाल करे |

---

## ⚡ 3-Line Summary
**English:**
1. JWT = header.payload.signature; servers verify the signature locally to trust claims — stateless auth.
2. Use short-lived access JWTs + rotated, revocable refresh tokens; RS256 + JWKS for microservices; pin algorithms; check exp/iss/aud.
3. Store securely (HttpOnly cookies on web, Keychain/Keystore on mobile); never put secrets in the payload.

**Hindi:**
1. JWT = header.payload.signature; सर्वर signature जाँचकर बिना DB के यूज़र पहचानता है।
2. छोटा access token + बदलने वाला, रद्द हो सकने वाला refresh token; microservices में RS256 + JWKS; algorithm तय करो।
3. Web पर HttpOnly cookie, mobile पर Keychain/Keystore; payload में कोई secret नहीं।

---

## ➡️ Next Topic Suggestion
**55. OAuth 2.0** — JWTs carry identity, but how do you "Login with Google" or let a third-party app access a user's data without their password? Next: OAuth 2.0 roles, grant types, and the Authorization Code + PKCE flow for web and mobile.
