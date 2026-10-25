# 120. JWT Best Practices
# हिंदी में: JWT Best Practices — Production Security Checklist

---

## 🔵 Simple Definition (English)
**JWT best practices** are a set of security and architectural guidelines for using JWTs safely in production: short expiry on access tokens, secure storage (never localStorage for sensitive tokens), explicit algorithm whitelisting, strong secrets, minimal payload data, HTTPS everywhere, and a plan for revocation despite JWT's stateless nature.

## 🔵 सरल परिभाषा (Hindi)
**JWT best practices** production में JWTs को safely use करने के लिए security और architectural guidelines का एक set है: access tokens पर short expiry, secure storage (sensitive tokens के लिए कभी localStorage नहीं), explicit algorithm whitelisting, strong secrets, minimal payload data, हर जगह HTTPS, और JWT की stateless nature के बावजूद revocation का plan।

---

## 🔴 Problem it Solves
JWT is a powerful but easy-to-misuse tool — developers commonly make mistakes like storing tokens in localStorage (XSS exposure), using weak/hardcoded secrets, never expiring tokens, putting sensitive data in the payload (it's only Base64, not encrypted), or forgetting that revocation requires extra infrastructure since JWT is inherently stateless. These mistakes have caused real security breaches. A checklist of best practices, informed by common attack patterns (XSS, algorithm confusion, token replay, secret leakage), prevents these pitfalls from reaching production.

## 🔴 यह क्यों बना? (Hindi)
JWT एक powerful पर misuse करना आसान tool है — developers commonly mistakes करते हैं जैसे localStorage में tokens store करना (XSS exposure), weak/hardcoded secrets use करना, tokens को कभी expire न करना, sensitive data payload में डालना (ये सिर्फ Base64 है, encrypted नहीं), या ये भूल जाना कि revocation के लिए extra infrastructure चाहिए क्योंकि JWT inherently stateless है। इन mistakes ने real security breaches किए हैं। Best practices की एक checklist, common attack patterns (XSS, algorithm confusion, token replay, secret leakage) से informed, इन pitfalls को production तक पहुंचने से रोकती है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Short expiry**: set `expiresIn` to minutes (15m) for access tokens — limits the damage window of a stolen token.
Step 2 → **Secure storage**: access token in memory (not localStorage), refresh token in `HttpOnly, Secure, SameSite` cookie — protects against XSS token theft.
Step 3 → **Strong, rotated secrets**: use a cryptographically random secret (min 256 bits for HS256), store in environment variables or a secrets manager (AWS Secrets Manager, Vault), never hardcode or commit to git.
Step 4 → **Explicit algorithm whitelisting + minimal payload**: pass `algorithms: ['HS256']` (or RS256) to `verify()`, and keep the payload to non-sensitive identifiers only (`userId`, `role`) — never passwords, PII, or financial data.
Step 5 → **Revocation strategy + HTTPS**: implement a token blacklist (Redis) or token-versioning scheme for emergency revocation, and ALWAYS transmit tokens only over HTTPS (never HTTP) to prevent network interception.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Short expiry**: access tokens के लिए `expiresIn` को minutes में set करो (15m) — stolen token का damage window limit करता है।
Step 2 → **Secure storage**: access token memory में (localStorage नहीं), refresh token `HttpOnly, Secure, SameSite` cookie में — XSS token theft से protect करता है।
Step 3 → **Strong, rotated secrets**: cryptographically random secret use करो (HS256 के लिए min 256 bits), environment variables या secrets manager (AWS Secrets Manager, Vault) में store करो, कभी hardcode या git में commit मत करो।
Step 4 → **Explicit algorithm whitelisting + minimal payload**: `verify()` को `algorithms: ['HS256']` (या RS256) pass करो, और payload को सिर्फ non-sensitive identifiers तक रखो (`userId`, `role`) — कभी passwords, PII, या financial data नहीं।
Step 5 → **Revocation strategy + HTTPS**: emergency revocation के लिए token blacklist (Redis) या token-versioning scheme implement करो, और tokens को हमेशा सिर्फ HTTPS पर transmit करो (कभी HTTP नहीं) network interception रोकने के लिए।

---

## 🟡 Real World Example
**Zerodha (stock trading app) session security:** Given the high-stakes nature of financial trading, Zerodha's Kite platform applies strict JWT practices: access tokens expire in a very short window and require re-authentication for sensitive actions (placing large orders) even within an active session via step-up authentication (additional PIN/TOTP). Secrets are rotated periodically through a managed secrets service, never hardcoded. All traffic is HTTPS-only with HSTS enforced. If suspicious activity is detected (login from a new device/location), ALL active sessions/refresh tokens for that user are immediately invalidated via a server-side token version increment, forcing re-login everywhere — a deliberate trade-off favoring security over convenience given the financial stakes.

## 🟡 Real Example Hindi mein
**Zerodha (stock trading app) session security:** Financial trading की high-stakes nature को देखते हुए, Zerodha का Kite platform strict JWT practices apply करता है: access tokens बहुत short window में expire होते हैं और sensitive actions (बड़े orders place करना) के लिए active session के अंदर भी re-authentication चाहिए step-up authentication (additional PIN/TOTP) से। Secrets managed secrets service से periodically rotate होते हैं, कभी hardcoded नहीं। सारा traffic HTTPS-only है HSTS enforced के साथ। Suspicious activity detect होने पर (नए device/location से login), उस user के सभी active sessions/refresh tokens तुरंत invalidate हो जाते हैं server-side token version increment से, सभी जगह re-login force करता है — financial stakes को देखते हुए security को convenience से ऊपर रखने का deliberate trade-off।

---

## 💻 Code Example — Basic

```javascript
// jwt-best-practices-basic.js
const jwt = require('jsonwebtoken'); // npm install jsonwebtoken
require('dotenv').config(); // npm install dotenv — loads secrets from .env, never hardcoded

// ✅ BEST PRACTICE 1: secret from environment variable, not hardcoded in source
const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET || JWT_SECRET.length < 32) {
  throw new Error('JWT_SECRET must be set and at least 32 characters long');
}

// ✅ BEST PRACTICE 2: minimal payload — only non-sensitive identifiers
function createAccessToken(user) {
  const payload = {
    userId: user.id,
    role: user.role,
    // NEVER: password, email (if avoidable), SSN, credit card, full name if unnecessary
  };

  // ✅ BEST PRACTICE 3: short expiry
  return jwt.sign(payload, JWT_SECRET, {
    expiresIn: '15m',
    algorithm: 'HS256', // explicit algorithm
  });
}

// ✅ BEST PRACTICE 4: explicit algorithm whitelist on verify
function verifyAccessToken(token) {
  return jwt.verify(token, JWT_SECRET, { algorithms: ['HS256'] });
}

// Demonstration
const token = createAccessToken({ id: 'u1', role: 'customer' });
console.log('Token (expires in 15m):', token.substring(0, 40) + '...');
console.log('Decoded:', verifyAccessToken(token));
```

## 💻 Code Example — Advanced

```javascript
// jwt-best-practices-advanced.js — Token versioning for instant revocation + rate-limited auth endpoints
const express = require('express');
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');

const app = express();
app.use(express.json());

const JWT_SECRET = process.env.JWT_SECRET || 'use-a-real-256-bit-secret-in-prod';

// Mock DB: stores a 'tokenVersion' per user — incrementing it invalidates ALL existing tokens
const users = new Map([['u1', { id: 'u1', role: 'customer', tokenVersion: 0 }]]);

// ─── 1. INCLUDE tokenVersion IN THE PAYLOAD ────────────────────────────────────
function issueToken(user) {
  return jwt.sign(
    { userId: user.id, role: user.role, tokenVersion: user.tokenVersion },
    JWT_SECRET,
    { expiresIn: '15m', algorithm: 'HS256' }
  );
}

// ─── 2. VERIFY MIDDLEWARE checks tokenVersion against current DB value ────────
function authenticate(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token' });

  try {
    const decoded = jwt.verify(token, JWT_SECRET, { algorithms: ['HS256'] });
    const user = users.get(decoded.userId);

    // If DB's tokenVersion has advanced beyond the token's version, it was REVOKED
    if (!user || user.tokenVersion !== decoded.tokenVersion) {
      return res.status(401).json({ error: 'Token revoked, please login again' });
    }

    req.user = decoded;
    next();
  } catch (err) {
    const message = err.name === 'TokenExpiredError' ? 'Token expired' : 'Invalid token';
    res.status(401).json({ error: message });
  }
}

// ─── 3. RATE-LIMITED LOGIN endpoint (brute-force protection, best practice) ───
const loginLimiter = rateLimit({ windowMs: 10 * 60 * 1000, max: 5 });

app.post('/login', loginLimiter, (req, res) => {
  const user = users.get('u1'); // mock successful auth
  res.json({ accessToken: issueToken(user) });
});

// ─── 4. REVOKE ALL SESSIONS by incrementing tokenVersion (e.g., on password change) ──
app.post('/account/revoke-all-sessions', authenticate, (req, res) => {
  const user = users.get(req.user.userId);
  user.tokenVersion += 1; // every previously issued token is now instantly invalid
  res.json({ message: 'All sessions revoked, please login again on all devices' });
});

app.get('/profile', authenticate, (req, res) => res.json({ user: req.user }));

app.listen(3000, () => console.log('Security-hardened JWT server running on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const jwt = require('jsonwebtoken');
const helmet = require('helmet'); // npm install helmet — sets security headers
const app = express();

app.use(helmet()); // ✅ best practice: secure HTTP headers (HSTS, X-Content-Type-Options, etc.)
app.use(express.json());

// ✅ best practice: enforce HTTPS in production (redirect HTTP to HTTPS)
app.use((req, res, next) => {
  if (process.env.NODE_ENV === 'production' && req.headers['x-forwarded-proto'] !== 'https') {
    return res.redirect(`https://${req.headers.host}${req.url}`);
  }
  next();
});

app.post('/api/auth/login', async (req, res) => {
  const user = await User.findOne({ email: req.body.email }); // mock
  const token = jwt.sign(
    { userId: user._id, role: user.role, tokenVersion: user.tokenVersion },
    process.env.JWT_SECRET,
    { expiresIn: '15m', algorithm: 'HS256' }
  );
  res.json({ accessToken: token });
});

app.listen(443, () => console.log('HTTPS-enforced, header-hardened server running'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Hardcoding the JWT secret in source code (and sometimes committing it to git)
✅ Correct: Always load secrets from environment variables or a secrets manager — a secret committed to git history remains exposed forever, even if later removed.

```javascript
// Wrong — hardcoded, visible in source control forever if committed
const SECRET = 'mySecret123';

// Right — loaded from environment, never in source code
const SECRET = process.env.JWT_SECRET;
```

❌ Mistake 2: Setting an extremely long or no expiry "for convenience"
✅ Correct: A token with no practical expiry defeats the purpose of having expiry-based risk mitigation at all — if it's stolen, it's valid essentially forever.

```javascript
// Wrong — effectively permanent token
jwt.sign(payload, secret, { expiresIn: '100y' });

// Right — short-lived access token + separate refresh mechanism for longevity
jwt.sign(payload, secret, { expiresIn: '15m' });
```

---

## 🧠 Tricky Interview Question

```javascript
const jwt = require('jsonwebtoken');
const SECRET = 'weak';

const token = jwt.sign({ userId: '1', role: 'customer' }, SECRET, { expiresIn: '1h' });

// An attacker, WITHOUT knowing the secret, tries to brute-force it offline
// using the publicly visible token (anyone can see header.payload, only signature is "protected")
```
Is a weak, short secret like `'weak'` actually a security risk, even though JWT uses cryptographic signing?

Answer: **Yes, absolutely.** HMAC-based signing (HS256) is only as strong as the secret itself — a short, dictionary-word secret like `'weak'` can be BRUTE-FORCED OFFLINE by an attacker who has any valid token (which exposes the header and payload, and the signature to test guesses against). The attacker doesn't need to interact with the server at all — they can take the publicly-visible signature, try HMAC-SHA256 with millions of candidate secrets locally, and check if any produce a matching signature. Tools like `hashcat` can brute-force weak JWT secrets within seconds to minutes. This is why best practice mandates a cryptographically random secret of AT LEAST 256 bits (32+ random bytes, not a memorable word or short string) — generated via `crypto.randomBytes(32).toString('hex')`, never a human-chosen passphrase.

---

## ⚫ Interview Questions + Answers

Q1: Why is "JWT payload is not encrypted" a frequently tested interview point, and what's the practical implication?
A1: JWT's payload is only Base64URL-ENCODED (a reversible encoding, not encryption) — anyone with the token (including the end user themselves, via browser dev tools) can decode and read the full payload content. The signature only guarantees INTEGRITY (hasn't been tampered with), not CONFIDENTIALITY. Practical implication: never put passwords, SSNs, credit card numbers, or other sensitive PII directly in the JWT payload — only non-sensitive identifiers that are safe for the client (or anyone intercepting network traffic even over HTTPS at some hop) to see.

Q2: What's "token versioning" and how does it solve JWT's revocation problem?
A2: Since JWT is stateless, a signed token remains cryptographically valid until its natural expiry — there's no built-in "delete" mechanism. Token versioning adds a `tokenVersion` field to both the JWT payload AND a corresponding field in the user's DB record. On verification, the server compares the token's `tokenVersion` to the CURRENT DB value — if they don't match (because the DB value was incremented, e.g., on password change or "logout everywhere"), the token is rejected even though it hasn't technically expired. This re-introduces a lightweight DB lookup but enables effective revocation.

Q3: Why should you use HTTPS for ALL JWT-based authentication, even on "internal" APIs?
A3: Without HTTPS (TLS), tokens travel over the network in PLAIN TEXT — any network intermediary (a compromised router, a man-in-the-middle attacker on public WiFi, even internal network sniffing) can intercept and steal the token, then use it directly ("replay") to impersonate the user until it expires. HTTPS encrypts the entire connection, making this interception computationally infeasible. Even "internal" service-to-service traffic should use TLS in modern zero-trust security architectures, since internal network compromise is a real and increasingly common attack vector.

Q4: What does "algorithm confusion" mean in the context of JWT vulnerabilities, and how do you prevent it?
A4: It refers to a class of attacks exploiting ambiguity in how a JWT library selects which algorithm to use for verification — e.g., if a server is configured to accept BOTH RS256 and HS256 without restriction, an attacker could take a token meant to be RS256-verified (using a PUBLIC key), re-sign it as HS256 using that same public key AS the HMAC secret (since it's publicly known), and some vulnerable implementations would incorrectly accept it as validly signed. Prevention: always explicitly pass an `algorithms` whitelist array to `verify()` matching EXACTLY what your system issues (e.g., `algorithms: ['RS256']` only), never allowing the token's own `alg` header to dictate which verification method is used unchecked.

Q5: Besides technical token handling, what's a key best practice around WHAT data you choose to expose via a JWT's role/permission claims?
A5: Follow the principle of least privilege — include only the MINIMUM claims necessary for the token's intended use (e.g., `userId` and `role`, not a full permissions array if role-based lookup suffices, not internal flags/metadata irrelevant to the client). Overly detailed claims increase the token size (more bandwidth per request) and increase the information disclosed if the token is ever decoded/inspected by unintended parties (remember: payload is readable, not confidential) — minimizing payload content is both a performance and security best practice.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production system issuing or verifying JWTs — these practices are the minimum security bar, not optional extras
- Systems handling sensitive data (finance, healthcare, personal data) where the stakes of a JWT-related breach are high
- Multi-service/microservice architectures needing consistent, auditable token security standards across teams

❌ Avoid when:
- There's no legitimate reason to skip these practices in production; the only "shortcut" acceptable is during early local-only prototyping where security hardening can be deferred briefly, but must be addressed before any real user data or deployment

---

## 📊 Visual Diagram
```
JWT SECURITY CHECKLIST (production):

  ┌───────────────────────────────────────────────────────────┐
  │  ✅ Short expiry on access tokens (15 min typical)         │
  │  ✅ Access token in memory, refresh token in HttpOnly cookie│
  │  ✅ Strong secret (256+ bits) from env var / secrets manager│
  │  ✅ Explicit algorithms whitelist on verify()                │
  │  ✅ Minimal, non-sensitive payload claims                    │
  │  ✅ HTTPS-only transmission, HSTS enabled                    │
  │  ✅ Revocation plan: blacklist (Redis) OR token versioning   │
  │  ✅ Rate-limited login/auth endpoints                         │
  │  ✅ Refresh token rotation + reuse detection                  │
  └───────────────────────────────────────────────────────────┘
                              │
                 any ❌ here = production security gap
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Secret strength | Cryptographic randomness of signing key | Signing key की cryptographic randomness |
| Token Versioning | DB-tracked version for revocation | Revocation के लिए DB-tracked version |
| Algorithm whitelisting | Restricting accepted signing algorithms | Accepted algorithms को restrict करना |
| HSTS | Forces HTTPS, blocks downgrade attacks | HTTPS force करने वाला header |
| Least privilege | Minimal claims/permissions in payload | Payload में minimum claims/permissions |
| Brute force | Guessing secret via trial and error | Trial and error से secret guess करना |

---

## ⚡ 3-Line Summary
English:
1. Use short-lived access tokens, secure (HttpOnly) storage for refresh tokens, strong random secrets from env vars, and explicit algorithm whitelisting.
2. Keep JWT payloads minimal and non-sensitive (it's encoded, not encrypted); always transmit over HTTPS; rate-limit auth endpoints.
3. Plan for revocation despite JWT's stateless nature — use token versioning or a Redis blacklist for emergency session invalidation.

Hindi:
1. Short-lived access tokens, refresh tokens के लिए secure (HttpOnly) storage, env vars से strong random secrets, और explicit algorithm whitelisting use करो।
2. JWT payloads को minimal और non-sensitive रखो (ये encoded है, encrypted नहीं); हमेशा HTTPS पर transmit करो; auth endpoints rate-limit करो।
3. JWT की stateless nature के बावजूद revocation का plan रखो — emergency session invalidation के लिए token versioning या Redis blacklist use करो।

---

## ➡️ Next Topic
**121. bcrypt (Password Hashing)** — Secure password storage using salted, slow hashing algorithms (already covered in topic 121; see bcrypt vs argon2 comparison next)।
