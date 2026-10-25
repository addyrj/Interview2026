# 119. JWT — Access Token + Refresh Token
# हिंदी में: Access Token + Refresh Token Pattern

---

## 🔵 Simple Definition (English)
The **Access + Refresh Token** pattern uses two tokens: a short-lived **access token** (minutes, sent with every API request) for actual authorization, and a long-lived **refresh token** (days/weeks, stored securely, used only to obtain new access tokens) so users stay logged in without re-entering credentials, while limiting the damage window if an access token is stolen.

## 🔵 सरल परिभाषा (Hindi)
**Access + Refresh Token** pattern दो tokens use करता है: एक short-lived **access token** (minutes, हर API request के साथ भेजा जाता है) actual authorization के लिए, और एक long-lived **refresh token** (days/weeks, securely stored, सिर्फ नए access tokens पाने के लिए use होता है) ताकि users बार-बार credentials डाले बिना logged in रहें, और access token चोरी होने पर damage window limited रहे।

---

## 🔴 Problem it Solves
A single long-lived JWT (e.g., valid for 30 days) is dangerous if stolen — the attacker has full access for a month. A single short-lived JWT (e.g., 15 minutes) is safer but forces users to re-login every 15 minutes, terrible UX. The two-token pattern solves both: the access token is short-lived (small theft window), while the refresh token lets the client silently get a NEW access token without bothering the user — combining security (short exposure) with usability (long sessions without re-login).

## 🔴 यह क्यों बना? (Hindi)
एक single long-lived JWT (जैसे 30 days valid) चोरी होने पर dangerous है — attacker को एक महीने तक पूरा access मिल जाता है। एक single short-lived JWT (जैसे 15 minutes) safer है पर users को हर 15 minutes re-login करना पड़ता, terrible UX। Two-token pattern दोनों solve करता है: access token short-lived है (छोटा theft window), जबकि refresh token client को silently नया access token पाने देता है user को disturb किए बिना — security (short exposure) को usability (बिना re-login लंबे sessions) के साथ combine करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → On login, server issues BOTH tokens: access token (15 min, signed with `JWT_ACCESS_SECRET`) and refresh token (7-30 days, signed with a DIFFERENT `JWT_REFRESH_SECRET`).
Step 2 → Access token is sent in response body, stored by the client in memory (JS variable) — used in `Authorization: Bearer <token>` header for every API call.
Step 3 → Refresh token is sent as an `HttpOnly, Secure, SameSite` cookie (not accessible via JS) and/or stored in the database linked to the user, for revocation capability.
Step 4 → When the access token expires (API returns 401 with `TOKEN_EXPIRED`), the client calls `POST /auth/refresh`, sending the refresh token cookie automatically.
Step 5 → Server verifies the refresh token, checks it exists in the DB (not revoked/reused), issues a NEW access token (and often a NEW refresh token too — "rotation" — invalidating the old one), letting the user continue seamlessly without noticing.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Login पर, server दोनों tokens issue करता है: access token (15 min, `JWT_ACCESS_SECRET` से signed) और refresh token (7-30 days, अलग `JWT_REFRESH_SECRET` से signed)।
Step 2 → Access token response body में भेजा जाता है, client memory में store करता है (JS variable) — हर API call में `Authorization: Bearer <token>` header में use होता है।
Step 3 → Refresh token `HttpOnly, Secure, SameSite` cookie के रूप में भेजा जाता है (JS से access नहीं) और/या database में user से linked store होता है, revocation capability के लिए।
Step 4 → Access token expire होने पर (API 401 के साथ `TOKEN_EXPIRED` return करता है), client `POST /auth/refresh` call करता है, refresh token cookie automatically भेजता है।
Step 5 → Server refresh token verify करता है, DB में check करता है कि exist करता है (revoked/reused नहीं), नया access token issue करता है (अक्सर नया refresh token भी — "rotation" — पुराना invalidate करते हुए), user को seamlessly continue करने देता है बिना notice किए।

---

## 🟡 Real World Example
**PhonePe/Paytm UPI app session management:** Opening the app, a user logs in with their PIN. PhonePe issues an access token (15 min expiry) used for every balance check, transaction, and transfer during active app usage. A refresh token (30 days) is stored securely (often in the device's secure keystore, equivalent to an HttpOnly cookie for web). Each time the access token expires during active use (user keeps the app open across hours), the app silently calls the refresh endpoint in the background — the user never sees a "please login again" prompt unless the refresh token itself expires (30 days of inactivity) or the user explicitly logs out, at which point the refresh token is revoked server-side, forcing a full PIN re-entry.

## 🟡 Real Example Hindi mein
**PhonePe/Paytm UPI app session management:** App खोलने पर, user अपने PIN से login करता है। PhonePe एक access token issue करता है (15 min expiry) जो active app usage के दौरान हर balance check, transaction, और transfer के लिए use होता है। एक refresh token (30 days) securely store होता है (अक्सर device के secure keystore में, web के HttpOnly cookie के equivalent)। हर बार जब access token active use के दौरान expire होता है (user hours तक app खुला रखता है), app background में silently refresh endpoint call करता है — user को "please login again" prompt तब तक नहीं दिखता जब तक refresh token खुद expire न हो (30 days inactivity) या user explicitly logout न करे, जिससे refresh token server-side revoke हो जाता है, full PIN re-entry force करता है।

---

## 💻 Code Example — Basic

```javascript
// access-refresh-basic.js
const jwt = require('jsonwebtoken'); // npm install jsonwebtoken

const ACCESS_SECRET = 'access-secret-key';
const REFRESH_SECRET = 'refresh-secret-key'; // MUST be different from access secret

// ─── ISSUE both tokens on login ────────────────────────────────────────────────
function generateTokens(user) {
  const accessToken = jwt.sign(
    { userId: user.id, role: user.role },
    ACCESS_SECRET,
    { expiresIn: '15m' } // short-lived
  );

  const refreshToken = jwt.sign(
    { userId: user.id }, // minimal payload — just enough to re-issue an access token
    REFRESH_SECRET,
    { expiresIn: '7d' } // long-lived
  );

  return { accessToken, refreshToken };
}

// ─── REFRESH: exchange a valid refresh token for a new access token ──────────
function refreshAccessToken(refreshToken) {
  try {
    const decoded = jwt.verify(refreshToken, REFRESH_SECRET); // validate refresh token
    // Issue a brand new, fresh access token
    const newAccessToken = jwt.sign(
      { userId: decoded.userId },
      ACCESS_SECRET,
      { expiresIn: '15m' }
    );
    return { success: true, accessToken: newAccessToken };
  } catch (err) {
    return { success: false, error: 'Invalid or expired refresh token' };
  }
}

// Demonstration
const user = { id: 'u1', role: 'customer' };
const { accessToken, refreshToken } = generateTokens(user);
console.log('Access token (short-lived):', accessToken.substring(0, 40) + '...');
console.log('Refresh token (long-lived):', refreshToken.substring(0, 40) + '...');

const refreshResult = refreshAccessToken(refreshToken);
console.log('Refresh result:', refreshResult);
```

## 💻 Code Example — Advanced

```javascript
// access-refresh-advanced.js — Full Express flow with rotation + reuse detection
const express = require('express');
const jwt = require('jsonwebtoken');
const cookieParser = require('cookie-parser');

const app = express();
app.use(express.json());
app.use(cookieParser());

const ACCESS_SECRET = process.env.JWT_ACCESS_SECRET || 'access-secret';
const REFRESH_SECRET = process.env.JWT_REFRESH_SECRET || 'refresh-secret';

// Mock DB storing issued refresh tokens per user (enables revocation + reuse detection)
const refreshTokenStore = new Map(); // userId -> Set of valid refresh tokens

function generateTokens(userId) {
  const accessToken = jwt.sign({ userId }, ACCESS_SECRET, { expiresIn: '15m' });
  const refreshToken = jwt.sign({ userId }, REFRESH_SECRET, { expiresIn: '7d' });
  return { accessToken, refreshToken };
}

// ─── LOGIN ──────────────────────────────────────────────────────────────────────
app.post('/auth/login', (req, res) => {
  const userId = 'u1'; // mock — normally verified via bcrypt.compare etc.
  const { accessToken, refreshToken } = generateTokens(userId);

  // Store refresh token server-side, enabling revocation and reuse detection
  if (!refreshTokenStore.has(userId)) refreshTokenStore.set(userId, new Set());
  refreshTokenStore.get(userId).add(refreshToken);

  res.cookie('refreshToken', refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 7 * 24 * 60 * 60 * 1000,
  });

  res.json({ accessToken }); // access token returned in body for client to store in memory
});

// ─── REFRESH with ROTATION + REUSE DETECTION ──────────────────────────────────
app.post('/auth/refresh', (req, res) => {
  const incomingToken = req.cookies.refreshToken;
  if (!incomingToken) return res.status(401).json({ error: 'No refresh token' });

  try {
    const decoded = jwt.verify(incomingToken, REFRESH_SECRET);
    const userTokens = refreshTokenStore.get(decoded.userId);

    // REUSE DETECTION: if this token isn't in our valid set, it was already
    // rotated out (used once before) or never issued — possible theft/replay!
    if (!userTokens || !userTokens.has(incomingToken)) {
      // SECURITY RESPONSE: invalidate ALL refresh tokens for this user immediately
      refreshTokenStore.delete(decoded.userId);
      return res.status(401).json({ error: 'Refresh token reuse detected — all sessions revoked' });
    }

    // ROTATION: invalidate the used token, issue a brand new pair
    userTokens.delete(incomingToken);
    const { accessToken, refreshToken: newRefreshToken } = generateTokens(decoded.userId);
    userTokens.add(newRefreshToken);

    res.cookie('refreshToken', newRefreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    res.json({ accessToken });
  } catch (err) {
    res.status(401).json({ error: 'Invalid or expired refresh token, please login again' });
  }
});

// ─── LOGOUT — revoke the refresh token ────────────────────────────────────────
app.post('/auth/logout', (req, res) => {
  const incomingToken = req.cookies.refreshToken;
  try {
    const decoded = jwt.decode(incomingToken); // just reading userId, no need to verify for logout
    refreshTokenStore.get(decoded?.userId)?.delete(incomingToken);
  } catch {}
  res.clearCookie('refreshToken');
  res.json({ message: 'Logged out' });
});

app.listen(3000, () => console.log('Access+Refresh token server running on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

// Middleware that auto-detects expired access tokens and signals the client to refresh
function authenticate(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No access token' });

  jwt.verify(token, process.env.JWT_ACCESS_SECRET, (err, decoded) => {
    if (err) {
      if (err.name === 'TokenExpiredError') {
        // Specific error code the frontend checks to trigger a silent refresh
        return res.status(401).json({ error: 'Access token expired', code: 'TOKEN_EXPIRED' });
      }
      return res.status(401).json({ error: 'Invalid token' });
    }
    req.user = decoded;
    next();
  });
}

app.get('/api/wallet/balance', authenticate, (req, res) => {
  res.json({ balance: 1500.50 }); // protected route using short-lived access token
});

app.listen(4000, () => console.log('Wallet API running on port 4000'));

/*
CLIENT-SIDE PATTERN (conceptual, e.g., axios interceptor):
  on 401 with code TOKEN_EXPIRED:
    call POST /auth/refresh (cookie sent automatically)
    get new accessToken, retry the original failed request
    if refresh ALSO fails -> redirect to login page
*/
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Storing the refresh token in localStorage (same XSS risk as access token)
✅ Correct: The refresh token is MORE sensitive than the access token (longer-lived) — it must go in an `HttpOnly` cookie, never in JS-accessible storage.

```javascript
// Wrong — refresh token accessible to any XSS payload, and it's valid for days/weeks!
localStorage.setItem('refreshToken', refreshToken);

// Right — HttpOnly cookie, invisible to JavaScript entirely
res.cookie('refreshToken', refreshToken, { httpOnly: true, secure: true, sameSite: 'strict' });
```

❌ Mistake 2: Not implementing refresh token rotation/reuse detection
✅ Correct: Without rotation, a stolen refresh token remains valid for its ENTIRE lifetime (days/weeks) even after the legitimate user keeps using the app — rotation (issuing a new refresh token on every use, invalidating the old) limits a stolen token's usefulness and reuse detection can flag/stop an active attack.

```javascript
// Wrong — same refresh token can be used indefinitely until natural expiry
app.post('/auth/refresh', (req, res) => {
  const decoded = jwt.verify(req.cookies.refreshToken, REFRESH_SECRET);
  res.json({ accessToken: jwt.sign({ userId: decoded.userId }, ACCESS_SECRET, { expiresIn: '15m' }) });
});

// Right — rotate: issue + store a NEW refresh token, invalidate the old one each time
```

---

## 🧠 Tricky Interview Question

```javascript
// Client A (legitimate user) and an attacker both somehow end up with
// the SAME refresh token (e.g., stolen via a network sniff).
// Client A uses it first to refresh. Then the attacker tries to use the SAME token.
```
With proper rotation + reuse detection implemented, what happens to the attacker's attempt, AND to Client A's subsequent sessions?

Answer: When Client A refreshes first, the server ROTATES the token — the old refresh token is deleted from the valid set, and a new one is issued to Client A. When the attacker then tries to use the SAME (now-old, already-used) refresh token, the server's reuse-detection logic finds it's NOT in the current valid set for that user — this is flagged as a reuse/replay attempt, a strong signal of token theft. The correct security response (as implemented in the advanced example above) is to immediately invalidate ALL refresh tokens for that user (not just the one being reused), forcing BOTH the attacker AND the legitimate Client A to re-login. This is a deliberate trade-off: Client A experiences an inconvenient forced logout, but it guarantees the attacker's stolen token is immediately useless and the account owner is alerted (often paired with a "suspicious activity" notification/email) rather than leaving the attacker with ongoing silent access.

---

## ⚫ Interview Questions + Answers

Q1: Why use two separate secrets for access and refresh tokens instead of one shared secret?
A1: If a single secret signs both token types and that secret leaks, an attacker can forge BOTH access AND refresh tokens with any claims they want (unlimited access, indefinitely renewable). Using separate secrets means compromising one doesn't automatically compromise the other — though in practice, if your signing secrets are compromised at all, you have a serious security incident regardless; separate secrets is defense-in-depth, not a complete mitigation.

Q2: Where should the access token be stored on the client, and why not the same place as the refresh token?
A2: Access token: ideally kept in memory (a JS variable, not any persistent storage) — it's used frequently and its short lifetime limits exposure even if briefly vulnerable to XSS. Refresh token: must be in an `HttpOnly` cookie (invisible to JS) since it's long-lived and far more damaging if stolen — storing it in memory would also work, but then every page refresh loses it (forcing full re-login), so HttpOnly cookies that survive page reloads are the practical choice for refresh tokens in browser apps.

Q3: What is refresh token rotation and why is it considered a security best practice?
A3: Rotation means every time a refresh token is used to get a new access token, the server ALSO issues a brand new refresh token and invalidates the old one — so each refresh token can only be used ONCE. This limits the window of usefulness for a stolen refresh token (it becomes invalid the moment it's used, whether by the legitimate owner or an attacker) and enables reuse detection: if the SAME (already-used, now-invalid) token appears again, it's a clear signal of token theft.

Q4: How does the client know when to call the refresh endpoint — does it guess based on time, or wait for a failure?
A4: Two common approaches: (1) **Reactive**: the client makes a normal API call with the access token; if it gets back a `401` with a specific error code (e.g., `TOKEN_EXPIRED`), it THEN calls `/auth/refresh`, gets a new access token, and retries the original request (often implemented via an HTTP interceptor). (2) **Proactive**: the client decodes the access token's `exp` claim client-side and preemptively refreshes slightly before expiry, avoiding any failed request at all. Reactive is simpler and more robust to clock skew; proactive gives a smoother UX with zero failed-request retries.

Q5: What happens to a user's active sessions on OTHER devices when their refresh token is revoked (e.g., on explicit "logout everywhere")?
A5: If refresh tokens are tracked per-device/session in the database (not just one token per user), "logout everywhere" deletes ALL stored refresh tokens for that user — any device trying to refresh afterward gets rejected (token not found in the valid set) and is forced to fully re-login. Their currently-active access tokens (if any) remain valid until their own short expiry (e.g., 15 min) elapses naturally, since access tokens aren't typically checked against a revocation list for performance reasons (a deliberate stateless trade-off) — this is why access tokens should stay SHORT-lived, to minimize this "still works for N more minutes after revocation" window.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production app needing both strong security AND a smooth "stay logged in" user experience
- Mobile apps, SPAs, and APIs where long browser sessions are expected but security-sensitive
- Systems that need the ability to "log out everywhere" or detect/respond to token theft

❌ Avoid when:
- Extremely simple internal tools/scripts where a single long-lived API key or basic session suffices and the complexity isn't justified
- Server-to-server (machine-to-machine) auth where OAuth2 client credentials flow or mTLS might be more appropriate than a user-oriented refresh flow

---

## 📊 Visual Diagram
```
ACCESS + REFRESH TOKEN LIFECYCLE:

  LOGIN
    │
    ▼
  Issue: accessToken (15 min) + refreshToken (7 days, HttpOnly cookie, stored in DB)
    │
    ▼
  ┌─────────────── Normal API usage (15 min window) ───────────────┐
  │  Client → Authorization: Bearer <accessToken> → API → 200 OK   │
  └──────────────────────────────────────────────────────────────────┘
    │
    ▼  (15 min passes, accessToken expires)
  API call → 401 TOKEN_EXPIRED
    │
    ▼
  Client → POST /auth/refresh (refreshToken cookie sent automatically)
    │
    ▼
  Server: verify refreshToken, check DB (not reused/revoked)
    │
    ├── Valid & unused ──▶ ROTATE: issue new accessToken + new refreshToken
    │                       (old refreshToken deleted from valid set)
    │
    └── Already used / not found ──▶ REUSE DETECTED
                                       → revoke ALL refresh tokens for user
                                       → force full re-login everywhere
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Access Token | Short-lived token for API requests | API requests के लिए short-lived token |
| Refresh Token | Long-lived token to get new access tokens | नए access tokens पाने का long-lived token |
| Rotation | Issuing a new refresh token on each use | हर use पर नया refresh token issue करना |
| Reuse Detection | Flagging an already-used refresh token | पहले use हो चुके token को flag करना |
| Silent Refresh | Background token renewal without user action | बिना user action के background renewal |
| Logout Everywhere | Revoking all sessions/devices at once | सभी sessions/devices एक साथ revoke करना |

---

## ⚡ 3-Line Summary
English:
1. Access tokens (short-lived, in memory) handle authorization for API calls; refresh tokens (long-lived, HttpOnly cookie) silently renew access tokens without re-login.
2. Implement rotation (new refresh token every use) and reuse detection (flag/revoke on replay) to limit damage from a stolen refresh token.
3. This pattern balances security (short exposure window) with usability (seamless long sessions) — essential for production auth systems.

Hindi:
1. Access tokens (short-lived, memory में) API calls के authorization handle करते हैं; refresh tokens (long-lived, HttpOnly cookie) बिना re-login access tokens silently renew करते हैं।
2. Rotation implement करो (हर use पर नया refresh token) और reuse detection (replay पर flag/revoke) stolen refresh token का damage limit करने के लिए।
3. ये pattern security (short exposure window) को usability (seamless long sessions) के साथ balance करता है — production auth systems के लिए ज़रूरी।

---

## ➡️ Next Topic
**120. JWT Best Practices** — Comprehensive security checklist for production JWT implementations।
