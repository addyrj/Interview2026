# 118. JWT — Sign + Verify
# हिंदी में: JWT — Sign करना और Verify करना

---

## 🔵 Simple Definition (English)
`jwt.sign()` creates a signed JWT from a payload and secret/key, encoding it into the `header.payload.signature` format. `jwt.verify()` takes a token and secret/key, recomputes the signature, and confirms the token hasn't been tampered with and hasn't expired — throwing specific errors (`TokenExpiredError`, `JsonWebTokenError`) when verification fails.

## 🔵 सरल परिभाषा (Hindi)
`jwt.sign()` एक payload और secret/key से signed JWT बनाता है, `header.payload.signature` format में encode करता है। `jwt.verify()` एक token और secret/key लेता है, signature recompute करता है, और confirm करता है कि token tamper नहीं हुआ और expire नहीं हुआ — verification fail होने पर specific errors throw करता है (`TokenExpiredError`, `JsonWebTokenError`)।

---

## 🔴 Problem it Solves
Manually implementing JWT signing/verification (Base64URL encoding, HMAC/RSA signature computation, claim validation like expiry/issuer/audience) is complex and error-prone — small mistakes (timing attacks in comparison, not checking `exp`, accepting `alg: none`) create serious security holes. The `jsonwebtoken` npm library handles all of this correctly and securely, exposing just two simple functions: `sign()` to issue tokens, `verify()` to validate them, following the JWT RFC 7519 spec precisely.

## 🔴 यह क्यों बना? (Hindi)
JWT signing/verification manually implement करना (Base64URL encoding, HMAC/RSA signature computation, claim validation जैसे expiry/issuer/audience) complex और error-prone है — छोटी गलतियाँ (comparison में timing attacks, `exp` check न करना, `alg: none` accept करना) serious security holes बना देती हैं। `jsonwebtoken` npm library इस सबको सही और securely handle करती है, सिर्फ दो simple functions expose करती है: `sign()` tokens issue करने के लिए, `verify()` उन्हें validate करने के लिए, JWT RFC 7519 spec को precisely follow करते हुए।

---

## 🟢 How it Works — Step by Step

Step 1 → `jwt.sign(payload, secret, options)`: builds the header (`{alg, typ}`), Base64URL-encodes header+payload, computes the signature (HMAC-SHA256 for HS256, or RSA-SHA256 for RS256) over `base64(header) + "." + base64(payload)`, and concatenates all three parts with dots.
Step 2 → `options` like `expiresIn`, `issuer`, `audience`, `subject` get automatically added as standard claims (`exp`, `iss`, `aud`, `sub`) in the payload during signing.
Step 3 → `jwt.verify(token, secret, options)`: splits the token into its 3 parts, recomputes the signature using the SAME algorithm and secret, and compares it to the signature in the token.
Step 4 → If the signature matches, it checks standard claims — is `exp` in the future (not expired)? does `iss`/`aud` match expected values if specified in options?
Step 5 → If everything checks out, `verify()` returns the decoded payload; otherwise it throws an error (`TokenExpiredError` if only expiry failed, `JsonWebTokenError` for signature mismatch or malformed token, `NotBeforeError` if `nbf` claim is in the future).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `jwt.sign(payload, secret, options)`: header बनाता है (`{alg, typ}`), header+payload को Base64URL-encode करता है, signature compute करता है (HS256 के लिए HMAC-SHA256, या RS256 के लिए RSA-SHA256) `base64(header) + "." + base64(payload)` पर, और तीनों parts को dots से concatenate करता है।
Step 2 → `expiresIn`, `issuer`, `audience`, `subject` जैसे `options` signing के दौरान automatically standard claims (`exp`, `iss`, `aud`, `sub`) के रूप में payload में जुड़ जाते हैं।
Step 3 → `jwt.verify(token, secret, options)`: token को 3 parts में split करता है, SAME algorithm और secret से signature recompute करता है, और token के signature से compare करता है।
Step 4 → Signature match होने पर, standard claims check करता है — क्या `exp` future में है (expired नहीं)? क्या `iss`/`aud` expected values से match करते हैं अगर options में specified हैं?
Step 5 → सब सही होने पर, `verify()` decoded payload return करता है; नहीं तो error throw करता है (`TokenExpiredError` अगर सिर्फ expiry fail हुई, `JsonWebTokenError` signature mismatch या malformed token के लिए, `NotBeforeError` अगर `nbf` claim future में है)।

---

## 🟡 Real World Example
**Ola Cabs driver app login:** When a driver logs in with their phone+OTP, Ola's backend calls `jwt.sign({ driverId, vehicleType, city }, process.env.JWT_SECRET, { expiresIn: '12h', issuer: 'ola-driver-service' })`. This token is used for all subsequent API calls during a shift. Every API gateway/microservice (trip-matching, earnings, navigation) calls `jwt.verify(token, SECRET, { issuer: 'ola-driver-service' })` to confirm the token is genuinely issued by Ola's auth service (via the `issuer` check) and hasn't expired — a driver's 12-hour shift token naturally expires at end of shift, requiring fresh login, limiting the exposure window if a token is somehow leaked.

## 🟡 Real Example Hindi mein
**Ola Cabs driver app login:** जब कोई driver phone+OTP से login करता है, Ola का backend call करता है `jwt.sign({ driverId, vehicleType, city }, process.env.JWT_SECRET, { expiresIn: '12h', issuer: 'ola-driver-service' })`। ये token shift के दौरान सभी बाद की API calls के लिए use होता है। हर API gateway/microservice (trip-matching, earnings, navigation) call करता है `jwt.verify(token, SECRET, { issuer: 'ola-driver-service' })` confirm करने के लिए कि token genuinely Ola के auth service से issued है (`issuer` check से) और expire नहीं हुआ — driver का 12-hour shift token naturally shift खत्म होने पर expire हो जाता है, fresh login की ज़रूरत होती है, जो token leak होने पर exposure window limit करता है।

---

## 💻 Code Example — Basic

```javascript
// jwt-sign-verify-basic.js
const jwt = require('jsonwebtoken'); // npm install jsonwebtoken

const SECRET = 'my-super-secret-key'; // in real apps, load from process.env.JWT_SECRET

// ─── SIGN: create a token ───────────────────────────────────────────────────────
const payload = { userId: '42', role: 'customer' };

const token = jwt.sign(payload, SECRET, {
  expiresIn: '1h', // token valid for 1 hour, adds 'exp' claim automatically
});

console.log('Generated token:', token); // header.payload.signature format

// ─── VERIFY: validate a token ───────────────────────────────────────────────────
try {
  const decoded = jwt.verify(token, SECRET); // throws if invalid/expired
  console.log('Decoded payload:', decoded); // { userId: '42', role: 'customer', iat: ..., exp: ... }
} catch (err) {
  console.error('Verification failed:', err.message);
}

// ─── WHAT HAPPENS WITH A TAMPERED TOKEN ────────────────────────────────────────
const tamperedToken = token.slice(0, -5) + 'XXXXX'; // corrupt the signature part
try {
  jwt.verify(tamperedToken, SECRET);
} catch (err) {
  console.error('Tampered token error:', err.name, '-', err.message); // JsonWebTokenError
}
```

## 💻 Code Example — Advanced

```javascript
// jwt-sign-verify-advanced.js — RS256 asymmetric signing + comprehensive error handling
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

// ─── 1. GENERATE AN RSA KEY PAIR (in real apps, generate once and store securely) ──
const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
});

// ─── 2. SIGN with the PRIVATE key (only the auth service holds this) ─────────────
function issueToken(user) {
  return jwt.sign(
    { userId: user.id, role: user.role },
    privateKey,
    {
      algorithm: 'RS256', // asymmetric: sign with private key
      expiresIn: '15m',
      issuer: 'auth-service',
      audience: 'internal-microservices',
      subject: user.id, // standard 'sub' claim
    }
  );
}

// ─── 3. VERIFY with the PUBLIC key (any microservice can have this safely) ───────
function verifyToken(token) {
  try {
    const decoded = jwt.verify(token, publicKey, {
      algorithms: ['RS256'], // IMPORTANT: explicitly restrict accepted algorithms
      issuer: 'auth-service', // reject tokens not issued by our auth service
      audience: 'internal-microservices',
    });
    return { valid: true, payload: decoded };
  } catch (err) {
    // Comprehensive error type handling
    if (err.name === 'TokenExpiredError') {
      return { valid: false, reason: 'expired', expiredAt: err.expiredAt };
    }
    if (err.name === 'JsonWebTokenError') {
      return { valid: false, reason: 'invalid', message: err.message };
    }
    if (err.name === 'NotBeforeError') {
      return { valid: false, reason: 'not_active_yet', date: err.date };
    }
    return { valid: false, reason: 'unknown', message: err.message };
  }
}

// ─── 4. DEMONSTRATION ──────────────────────────────────────────────────────────
const token = issueToken({ id: 'u99', role: 'admin' });
console.log('Token issued (RS256):', token.substring(0, 50) + '...');

const result = verifyToken(token);
console.log('Verification result:', result);

// Simulate a malicious attempt: client tries signing with 'none' algorithm (classic JWT attack)
try {
  jwt.verify(token, publicKey, { algorithms: ['none'] }); // explicitly disallowed in our verify above
} catch (err) {
  console.log('Algorithm confusion attack blocked:', err.message);
}

module.exports = { issueToken, verifyToken };
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());
const SECRET = process.env.JWT_SECRET;

app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email }); // mock
  if (!user) return res.status(401).json({ error: 'Invalid credentials' });

  // Sign a token with explicit algorithm and expiry
  const token = jwt.sign({ userId: user._id, role: user.role }, SECRET, {
    algorithm: 'HS256',
    expiresIn: '1h',
  });

  res.json({ token });
});

// Middleware verifying the token on every protected request
app.use('/api', (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token' });

  jwt.verify(token, SECRET, { algorithms: ['HS256'] }, (err, decoded) => {
    if (err) {
      const message = err.name === 'TokenExpiredError' ? 'Token expired' : 'Invalid token';
      return res.status(401).json({ error: message });
    }
    req.user = decoded;
    next();
  });
});

app.get('/api/profile', (req, res) => res.json({ user: req.user }));

app.listen(3000, () => console.log('JWT sign/verify server running on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Not restricting `algorithms` in `jwt.verify()`, enabling algorithm confusion attacks
✅ Correct: Always explicitly pass `algorithms: ['HS256']` (or whichever you use) to `verify()` — without it, in certain misconfigured setups an attacker could craft a token with `alg: none` or try to trick RS256-verifying code into treating the public key as an HMAC secret.

```javascript
// Wrong — no algorithm restriction, slightly weaker defense-in-depth
jwt.verify(token, SECRET);

// Right — explicitly whitelist accepted algorithms
jwt.verify(token, SECRET, { algorithms: ['HS256'] });
```

❌ Mistake 2: Using `jwt.decode()` instead of `jwt.verify()` to "check" a token
✅ Correct: `jwt.decode()` just Base64-decodes the payload WITHOUT any signature verification — it will happily "decode" a completely forged token. Only `jwt.verify()` cryptographically confirms authenticity.

```javascript
// Wrong — decode() never checks the signature; ANY string shaped like a JWT "works"
const payload = jwt.decode(token); // trusts payload blindly — dangerous!
if (payload.role === 'admin') { /* grant admin access — forgeable! */ }

// Right — verify() cryptographically validates before trusting the payload
const payload = jwt.verify(token, SECRET); // throws if tampered/invalid
if (payload.role === 'admin') { /* safe — signature confirmed */ }
```

---

## 🧠 Tricky Interview Question

```javascript
const jwt = require('jsonwebtoken');
const token = jwt.sign({ userId: '1' }, 'secretA', { expiresIn: '1h' });

// Later, elsewhere in the codebase, a DIFFERENT developer verifies with a typo'd secret:
try {
  const decoded = jwt.verify(token, 'secretA '); // notice the trailing space!
  console.log(decoded);
} catch (err) {
  console.log(err.name);
}
```
What error name gets logged, and why?

Answer: `JsonWebTokenError` with message "invalid signature". Even a single extra character (the trailing space in `'secretA '` vs `'secretA'`) produces a COMPLETELY different HMAC output — cryptographic hash functions are designed so any tiny change in input produces a drastically different, unpredictable output (the avalanche effect). There's no "close enough" matching in signature verification; it's exact byte-for-byte comparison. This demonstrates the importance of loading secrets from a single source of truth (environment variable, secrets manager) rather than hardcoding/retyping them in multiple places, where a typo like a trailing space or different casing silently breaks all token verification across the system — often surfacing as a confusing wave of "invalid signature" errors in production despite the signing logic looking "correct."

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `jwt.decode()` and `jwt.verify()`?
A1: `jwt.decode(token)` simply Base64URL-decodes the header and payload WITHOUT checking the signature at all — it will "successfully" decode even a completely tampered or forged token, since it performs zero cryptographic validation. `jwt.verify(token, secret)` recomputes the signature and compares it, throwing an error if it doesn't match, if the token is expired, or if other configured claims (issuer/audience) don't match. You should NEVER use `decode()` alone to make security decisions — only `verify()` provides a trust guarantee.

Q2: What claims does `jwt.sign()` add automatically, and which require explicit options?
A2: `iat` (issued at, Unix timestamp) is added automatically by default. `exp` (expiry) is added only if you pass the `expiresIn` option (e.g., `'1h'`, `'7d'`, or a number of seconds). `iss` (issuer), `aud` (audience), `sub` (subject) are added only if you pass the corresponding `issuer`, `audience`, `subject` options — none of these are automatic; you must explicitly configure them for stronger validation.

Q3: Why should you pass the `algorithms` option explicitly to `jwt.verify()`?
A3: This defends against "algorithm confusion" attacks, a historical class of JWT vulnerabilities. One variant: if a server verifies using `jwt.verify(token, key)` without restricting algorithms, and the key happens to work for BOTH RS256 (as a public key) and HS256 (as a secret), an attacker could craft a token with `alg: HS256`, sign it using the PUBLIC key (which is, well, public) as an HMAC secret, and some unguarded verification implementations would wrongly accept it. Explicitly whitelisting `algorithms: ['RS256']` (matching only what you issue) prevents this class of attack entirely.

Q4: How do `TokenExpiredError` and `JsonWebTokenError` differ, and why does the distinction matter for UX?
A4: `TokenExpiredError` means the token WAS valid/correctly signed but its `exp` claim has passed — the natural, expected lifecycle of a short-lived token. `JsonWebTokenError` means the token is malformed, has an invalid signature, or fails other claim checks — this is NOT expected and may indicate tampering or a bug. UX-wise, an expired token should trigger a silent refresh-token flow (seamless re-auth); an invalid/malformed token should force a full re-login, since something is fundamentally wrong (possibly a security concern worth logging/alerting on).

Q5: Can you verify a JWT without knowing the secret it was signed with?
A5: For HS256 (symmetric), no — you need the exact same secret used to sign it; there's no way to verify an HMAC signature without the shared secret. For RS256 (asymmetric), yes — anyone with the PUBLIC key can verify a token's signature, while only the holder of the PRIVATE key can create (sign) new valid tokens. This is why RS256 is preferred when multiple independent services need to verify tokens without being trusted to issue them.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Issuing/validating any JWT-based authentication or authorization tokens
- Microservices architecture where services need to independently verify tokens without a central auth DB lookup
- Need standard, spec-compliant claim handling (expiry, issuer, audience) rather than reinventing it

❌ Avoid when:
- You need instant token revocation as a core requirement — JWT verify alone can't "unsign" an already-issued valid token; you'd need additional infrastructure (blacklist, short expiry + refresh pattern)
- The payload needs to be confidential/encrypted (not just tamper-proof) — JWT payload is Base64, not encrypted; consider JWE (JSON Web Encryption) or just keep sensitive data server-side

---

## 📊 Visual Diagram
```
jwt.sign() FLOW:
  payload + secret + options
          │
          ▼
  { alg, typ } header built
          │
  payload + exp/iss/aud claims merged in
          │
          ▼
  signature = HMAC/RSA(base64(header)+"."+base64(payload), secret/privateKey)
          │
          ▼
  token = base64(header) + "." + base64(payload) + "." + signature

jwt.verify() FLOW:
  token + secret + options
          │
          ▼
  split into header.payload.signature
          │
  recompute signature using secret/publicKey
          │
   match? ──No──▶ throw JsonWebTokenError
          │
         Yes
          │
   exp in future? ──No──▶ throw TokenExpiredError
          │
         Yes
          │
   iss/aud match (if specified)? ──No──▶ throw JsonWebTokenError
          │
         Yes
          ▼
   return decoded payload ✅
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| jwt.sign() | Creates and signs a new JWT | नया signed JWT बनाना |
| jwt.verify() | Cryptographically validates a JWT | JWT को cryptographically validate करना |
| jwt.decode() | Decodes WITHOUT verifying signature | बिना signature verify किए decode करना |
| TokenExpiredError | Thrown when exp claim has passed | exp claim बीत जाने पर error |
| JsonWebTokenError | Thrown for invalid/malformed/tampered tokens | Invalid/tampered token पर error |
| algorithms option | Explicit whitelist of accepted signing algorithms | Accepted algorithms की whitelist |
| iat/exp/iss/aud/sub | Standard JWT claims | Standard JWT claims |

---

## ⚡ 3-Line Summary
English:
1. `jwt.sign(payload, secret, options)` creates a tamper-proof token; `jwt.verify(token, secret, options)` cryptographically validates it, throwing specific errors on failure.
2. Never use `jwt.decode()` for trust decisions — it skips signature verification entirely; always use `verify()`.
3. Always explicitly restrict `algorithms` in `verify()` to prevent algorithm confusion attacks, and handle `TokenExpiredError` vs `JsonWebTokenError` distinctly for better UX.

Hindi:
1. `jwt.sign(payload, secret, options)` एक tamper-proof token बनाता है; `jwt.verify(token, secret, options)` इसे cryptographically validate करता है, fail होने पर specific errors throw करता है।
2. Trust decisions के लिए कभी `jwt.decode()` use मत करो — ये signature verification पूरी तरह skip करता है; हमेशा `verify()` use करो।
3. Algorithm confusion attacks रोकने के लिए `verify()` में हमेशा explicitly `algorithms` restrict करो, और बेहतर UX के लिए `TokenExpiredError` vs `JsonWebTokenError` को अलग handle करो।

---

## ➡️ Next Topic
**119. JWT — Access Token + Refresh Token** — Short-lived vs long-lived token pattern for secure, seamless sessions।
