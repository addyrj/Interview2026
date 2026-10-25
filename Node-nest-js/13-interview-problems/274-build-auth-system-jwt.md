# 274. Build Auth System (JWT)
# हिंदी में: JWT से Authentication System बनाना

---

## 🔵 Simple Definition (English)
A JWT-based auth system lets users sign up, log in, and access protected routes using a **JSON Web Token** — a signed, stateless token sent with each request instead of a server-side session. The server verifies the token's signature on every request without needing to look it up in a database.

## 🔵 सरल परिभाषा (Hindi)
JWT-based auth system में users signup/login करते हैं और protected routes को **JSON Web Token** से access करते हैं — एक signed, stateless token जो हर request के साथ भेजा जाता है, server-side session की जगह। Server हर request पर token का signature verify करता है, DB lookup की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
Traditional session-based auth stores session data server-side (in memory or Redis) and sends only a session ID cookie — this requires the server (or a shared store) to look up session data on every request, and doesn't scale easily across multiple stateless server instances without a shared session store. JWTs solve this: the token itself carries the user's identity and claims, cryptographically signed so it can't be tampered with — any server instance can verify it independently without a shared database call, making horizontal scaling trivial.

## 🔴 यह क्यों बना? (Hindi)
Traditional session-based auth server-side session data store करता है (memory या Redis) और सिर्फ session ID cookie भेजता है — हर request पर lookup चाहिए, और बिना shared session store multiple stateless servers में scale करना मुश्किल। JWT ये solve करता है: token खुद user की identity और claims रखता है, cryptographically signed — कोई भी server instance बिना shared DB call के independently verify कर सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Signup**: user submits email/password → password hashed with bcrypt (never stored plaintext) → user saved to DB.
Step 2 → **Login**: user submits email/password → server finds user, compares hash with bcrypt → if match, server creates a JWT containing `{ userId, email }` signed with a secret key.
Step 3 → JWT has 3 parts: `header.payload.signature` — header says algorithm, payload has claims, signature proves it wasn't tampered with.
Step 4 → Server sends JWT back to client — client stores it (localStorage, or better, an httpOnly cookie) and sends it in the `Authorization: Bearer <token>` header on subsequent requests.
Step 5 → **Protected route middleware**: extracts token from header, verifies signature + expiry using the SAME secret key, attaches decoded user info to `req.user`.
Step 6 → **Refresh tokens**: short-lived access token (15 min) + long-lived refresh token (7 days, stored securely) — access token expires fast (limits damage if stolen), refresh token lets the client get a new access token without re-login.
Step 7 → **Logout**: since JWTs are stateless, true server-side invalidation needs a blocklist (Redis) or short expiry + refresh token rotation.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Signup**: email/password submit → bcrypt से password hash → DB में save।
Step 2 → **Login**: email/password submit → server user ढूंढे, bcrypt से hash compare → match हो तो JWT बनाये `{ userId, email }` secret key से signed।
Step 3 → JWT के 3 parts: `header.payload.signature`।
Step 4 → Server JWT भेजे — client store करे (localStorage या httpOnly cookie), `Authorization: Bearer <token>` header में भेजे।
Step 5 → **Protected route middleware**: header से token निकाले, signature + expiry verify करे, decoded user info `req.user` में attach करे।
Step 6 → **Refresh tokens**: short-lived access token (15 min) + long-lived refresh token (7 days)।
Step 7 → **Logout**: JWT stateless है, real invalidation के लिए blocklist (Redis) या short expiry + refresh rotation चाहिए।

---

## 🟡 Real World Example
**PhonePe's** merchant dashboard API issues a 15-minute access token on login, plus a 7-day refresh token stored in an httpOnly, secure cookie. Every API request carries the access token; when it expires, the frontend silently calls `/auth/refresh` using the refresh token cookie to get a new access token — the user never notices. If a merchant's device is stolen, the short access-token lifetime limits exposure, and refresh tokens are tracked server-side so they can be revoked (e.g. on password change, all refresh tokens for that user are invalidated).

## 🟡 Real Example Hindi mein
**PhonePe** का merchant dashboard login पर 15-minute access token और 7-day refresh token (httpOnly cookie में) issue करता है। हर API request access token carry करती है; expire होने पर frontend silently `/auth/refresh` call करता है नया access token लेने के लिए। Device चोरी होने पर short access-token lifetime exposure limit करती है, और refresh tokens server-side track होते हैं (password change पर सभी invalidate हो सकते हैं)।

---

## 💻 Code Example — Basic

```javascript
// basic-jwt-auth.js — minimal JWT create + verify
// npm install jsonwebtoken bcrypt
// Run: node basic-jwt-auth.js

const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

const SECRET = 'my-super-secret-key'; // in real apps: process.env.JWT_SECRET

async function demo() {
  // 1. Hash a password at signup time (never store plaintext passwords)
  const plainPassword = 'mySecurePass123';
  const hashedPassword = await bcrypt.hash(plainPassword, 10); // 10 = salt rounds
  console.log('Hashed password:', hashedPassword);

  // 2. At login: compare submitted password against stored hash
  const isMatch = await bcrypt.compare(plainPassword, hashedPassword);
  console.log('Password matches:', isMatch); // true

  // 3. Create a JWT (signed token) containing user claims
  const token = jwt.sign(
    { userId: 42, email: 'user@example.com' }, // payload
    SECRET,                                     // signing secret
    { expiresIn: '15m' }                        // short-lived access token
  );
  console.log('JWT:', token);

  // 4. Verify a JWT (this is what protected routes do)
  try {
    const decoded = jwt.verify(token, SECRET);
    console.log('Decoded payload:', decoded); // { userId: 42, email: ..., iat, exp }
  } catch (err) {
    console.error('Invalid or expired token:', err.message);
  }
}

demo();
```

## 💻 Code Example — Advanced

```javascript
// server.js — complete worked mini-project: JWT auth with access + refresh tokens
// npm install express jsonwebtoken bcrypt

const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const app = express();
app.use(express.json());

const ACCESS_SECRET = process.env.JWT_ACCESS_SECRET || 'access-secret';
const REFRESH_SECRET = process.env.JWT_REFRESH_SECRET || 'refresh-secret';

// In-memory stores for demo (real app: DB + Redis)
const users = new Map();        // email -> { id, email, passwordHash }
const refreshTokens = new Set(); // valid refresh tokens (for revocation support)
let nextUserId = 1;

// ─── SIGNUP ────────────────────────────────────────────────────────────────
app.post('/auth/signup', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password || password.length < 8) {
    return res.status(400).json({ error: 'Valid email and password (8+ chars) required' });
  }
  if (users.has(email)) {
    return res.status(409).json({ error: 'User already exists' }); // 409 Conflict
  }

  const passwordHash = await bcrypt.hash(password, 10);
  const user = { id: nextUserId++, email, passwordHash };
  users.set(email, user);

  res.status(201).json({ message: 'User created', userId: user.id });
});

// ─── LOGIN ──────────────────────────────────────────────────────────────────
app.post('/auth/login', async (req, res) => {
  const { email, password } = req.body;
  const user = users.get(email);

  // Generic error message for both "user not found" and "wrong password"
  // — prevents attackers from learning which emails are registered
  if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
    return res.status(401).json({ error: 'Invalid email or password' });
  }

  const accessToken = jwt.sign({ userId: user.id, email: user.email }, ACCESS_SECRET, {
    expiresIn: '15m',
  });
  const refreshToken = jwt.sign({ userId: user.id }, REFRESH_SECRET, { expiresIn: '7d' });
  refreshTokens.add(refreshToken); // track for revocation

  // httpOnly cookie prevents JS access (defends against XSS stealing the token)
  res.cookie('refreshToken', refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production', // HTTPS only in prod
    sameSite: 'strict',
    maxAge: 7 * 24 * 60 * 60 * 1000,
  });

  res.json({ accessToken }); // access token goes in response body, client keeps in memory
});

// ─── REFRESH ────────────────────────────────────────────────────────────────
app.post('/auth/refresh', (req, res) => {
  const token = req.cookies?.refreshToken;
  if (!token || !refreshTokens.has(token)) {
    return res.status(401).json({ error: 'Invalid refresh token' });
  }
  try {
    const decoded = jwt.verify(token, REFRESH_SECRET);
    const newAccessToken = jwt.sign({ userId: decoded.userId }, ACCESS_SECRET, { expiresIn: '15m' });
    res.json({ accessToken: newAccessToken });
  } catch {
    res.status(401).json({ error: 'Refresh token expired, please log in again' });
  }
});

// ─── LOGOUT ─────────────────────────────────────────────────────────────────
app.post('/auth/logout', (req, res) => {
  const token = req.cookies?.refreshToken;
  refreshTokens.delete(token); // revoke this refresh token
  res.clearCookie('refreshToken');
  res.json({ message: 'Logged out' });
});

// ─── AUTH MIDDLEWARE ────────────────────────────────────────────────────────
function requireAuth(req, res, next) {
  const authHeader = req.headers.authorization; // "Bearer <token>"
  const token = authHeader?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token provided' });

  try {
    req.user = jwt.verify(token, ACCESS_SECRET);
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
}

// ─── PROTECTED ROUTE ────────────────────────────────────────────────────────
app.get('/api/profile', requireAuth, (req, res) => {
  res.json({ userId: req.user.userId, email: req.user.email });
});

app.listen(3000, () => console.log('JWT auth server on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// role-based access control building on the auth middleware above
function requireRole(role) {
  return (req, res, next) => {
    if (req.user.role !== role) {
      return res.status(403).json({ error: 'Forbidden — insufficient permissions' });
    }
    next();
  };
}

// Usage: admin-only route
app.delete('/api/products/:id', requireAuth, requireRole('admin'), (req, res) => {
  // only runs if token is valid AND req.user.role === 'admin'
  res.json({ message: 'Product deleted' });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Storing the JWT in `localStorage` for sensitive apps
✅ Correct: Prefer httpOnly cookies for refresh tokens (JS can't read them, defends against XSS); keep access tokens short-lived and in memory if stored client-side at all.

```javascript
// Wrong: localStorage is readable by any JS running on the page (XSS risk)
localStorage.setItem('token', accessToken);

// Right: httpOnly cookie for refresh token, in-memory variable for access token
// (access token lives only in JS memory, lost on page refresh — refreshed via cookie)
```

❌ Mistake 2: Using the same secret for access and refresh tokens, or a weak/short secret
✅ Correct: Use separate long random secrets for each token type, stored in env vars.

```javascript
// Wrong
const SECRET = 'secret123'; // guessable, and same secret everywhere

// Right
// JWT_ACCESS_SECRET and JWT_REFRESH_SECRET — 64+ byte random strings from env vars
// generate with: require('crypto').randomBytes(64).toString('hex')
```

---

## 🧠 Tricky Interview Question

```javascript
// Can you "delete" or "invalidate" a JWT before its expiry?
const token = jwt.sign({ userId: 1 }, SECRET, { expiresIn: '1h' });
// User logs out immediately. Is this token still valid for the next 59 minutes?
```
Answer: YES, by default — JWTs are STATELESS, meaning the server doesn't track which tokens are "active." Once issued, a JWT remains valid until its `exp` claim passes, regardless of logout. To actually revoke it before expiry, you need server-side state: a blocklist (Redis set of revoked token IDs/jti, checked on every verify), or short expiry (e.g. 15 min) combined with refresh-token revocation (as in the advanced example — deleting from `refreshTokens` set), limiting the exposure window. This statelessness-vs-revocability tradeoff is a classic JWT interview topic.

---

## ⚫ Interview Questions + Answers

Q1: What are the three parts of a JWT and what does each contain?
A1: `header.payload.signature`, base64url-encoded and dot-separated. **Header**: algorithm used (e.g. `HS256`) and token type. **Payload**: claims — custom data like `userId`, plus standard claims like `exp` (expiry), `iat` (issued at). **Signature**: HMAC or RSA signature over header+payload using the secret/private key — proves the token wasn't tampered with. Note: payload is only base64-ENCODED, not encrypted — anyone can decode and read it (never put passwords/secrets in the payload).

Q2: Why use both an access token and a refresh token instead of one long-lived token?
A2: A single long-lived token (e.g. 7 days) is dangerous if stolen — the attacker has access for the full duration. Splitting into a short-lived access token (15 min, used for API calls) and a long-lived refresh token (7 days, used ONLY to get new access tokens, stored more securely as an httpOnly cookie) limits the damage window: even if an access token leaks, it expires quickly; the refresh token is used less frequently and can be more easily revoked/rotated.

Q3: How do you handle JWT verification failures (expired vs malformed vs invalid signature)?
A3: `jwt.verify()` throws different error types: `TokenExpiredError` (expired — client should try refreshing), `JsonWebTokenError` (malformed or invalid signature — client should re-login, this could indicate tampering). Handle them distinctly: `if (err.name === 'TokenExpiredError') { /* prompt refresh */ } else { /* force re-login */ }`. Always return a generic 401 to the client regardless (don't leak which specific failure occurred — minor security hardening).

Q4: Should you store user roles/permissions inside the JWT payload?
A4: It's common for simple role checks (`role: 'admin'`) baked into the access token, avoiding a DB lookup on every request. BUT: if a user's role changes (demoted from admin), the OLD token still has the OLD role until it expires — a security gap. Mitigation: keep access tokens short-lived (15 min) so stale role data self-corrects quickly, or do a fresh DB/permission check for highly sensitive operations regardless of what the token claims.

Q5: What is the difference between authentication and authorization, and where does JWT fit?
A5: **Authentication** = verifying WHO you are (login with email/password, JWT proves "this request comes from user X"). **Authorization** = verifying WHAT you're allowed to do (role/permission checks — "is user X allowed to delete this product?"). JWT itself only handles authentication (identity) directly; authorization is built ON TOP by checking claims (like `role`) in the token or doing a fresh permissions lookup, typically in a separate middleware like `requireRole()`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Stateless APIs serving multiple client types (web, mobile, third-party integrations)
- Horizontally scaled services where you don't want a shared session store
- Microservices where each service needs to independently verify identity without calling a central auth service every time

❌ Avoid when:
- You need instant, reliable logout/revocation for every token (session-based auth with server-side store is simpler for this)
- Very simple single-server monoliths with low scale — traditional sessions (`express-session`) may be simpler to reason about

---

## 📊 Visual Diagram
```
SIGNUP/LOGIN FLOW
─────────────────
Client          Server
  │  POST /login     │
  │ ────────────────►│  verify password (bcrypt.compare)
  │                   │  create accessToken (15m) + refreshToken (7d)
  │ ◄────────────────│  accessToken in body, refreshToken in httpOnly cookie
  │

PROTECTED REQUEST FLOW
───────────────────────
  │  GET /api/profile           │
  │  Authorization: Bearer <AT> │
  │ ────────────────────────────►│  requireAuth middleware:
  │                               │   jwt.verify(token, ACCESS_SECRET)
  │                               │   attach req.user
  │ ◄────────────────────────────│  200 OK { profile data }

ACCESS TOKEN EXPIRED → REFRESH FLOW
────────────────────────────────────
  │  GET /api/profile → 401 (expired)
  │  POST /auth/refresh (refreshToken cookie sent automatically)
  │ ◄──────────────────────────── new accessToken
  │  retry GET /api/profile with new accessToken → 200 OK
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JWT | Signed stateless token carrying claims | Claims carry करने वाला signed stateless token |
| Access Token | Short-lived token for API requests | API requests के लिए short-lived token |
| Refresh Token | Long-lived token to get new access tokens | नए access tokens लेने के लिए long-lived token |
| bcrypt | Library to hash passwords securely | Passwords securely hash करने वाली library |
| httpOnly cookie | Cookie not accessible via JS (XSS defense) | JS से access न होने वाली cookie |
| Revocation | Invalidating a token before its natural expiry | Token को expiry से पहले invalid करना |

---

## ⚡ 3-Line Summary
English: 1. JWT auth hashes passwords with bcrypt, issues a signed token at login, and verifies the signature (no DB lookup) on every protected request. 2. Use short-lived access tokens + long-lived refresh tokens to balance security and user convenience. 3. JWTs are stateless by nature — real revocation needs a blocklist or refresh-token tracking.
Hindi: 1. JWT auth bcrypt से passwords hash करता है, login पर signed token issue करता है, हर protected request पर signature verify करता है (DB lookup नहीं)। 2. Security और convenience balance करने के लिए short-lived access + long-lived refresh tokens use करो। 3. JWTs stateless होते हैं — real revocation के लिए blocklist या refresh-token tracking चाहिए।

---

## ➡️ Next Topic
**275. Build File Upload API (Multer)** — Multer से file upload handling, validation, storage।
