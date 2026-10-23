---

# 097. JWT Security — Vulnerabilities + Best Practices
# हिंदी में: JWT Security — Token Attacks और Secure Implementation
# Risk Level: ⛔ Critical

---

## 🔵 Simple Definition (English)
JWT (JSON Web Token) is a self-contained token used for authentication. A JWT has three base64url-encoded parts: Header (algorithm), Payload (claims), Signature (integrity check). Vulnerabilities arise when the algorithm is mishandled, secrets are weak, or tokens are stored/transmitted insecurely.

## 🔵 सरल परिभाषा (Hindi)
JWT एक self-contained token है जिसमें user की information होती है। इसके 3 parts हैं: Header (algorithm), Payload (claims), Signature। Problems तब होती हैं जब algorithm गलत तरीके से handle हो, secret weak हो, या token insecurely store हो।

---

## ⚠️ The Attack / Threat

```
JWT Structure:
header.payload.signature

Header:  { "alg": "HS256", "typ": "JWT" }    → base64url encoded
Payload: { "userId": 123, "role": "user" }   → base64url encoded
Signature: HMACSHA256(header + "." + payload, secret)

ATTACK 1 — Algorithm Confusion (alg: none):
───────────────────────────────────────────
Original token: { "alg": "HS256" } → signed with secret

Attacker modifies:
Header:  { "alg": "none" } → no signature needed!
Payload: { "userId": 1, "role": "admin" } → elevated privileges!
Signature: (empty)

Vulnerable server: "alg is 'none', skip verification" → accepts it!
Impact: FULL authentication bypass ☠️

ATTACK 2 — RS256 to HS256 Confusion:
─────────────────────────────────────
Server uses RS256 (asymmetric: private key sign, public key verify)
Attacker knows the PUBLIC key (often exposed)
Attacker creates HS256 token, signs with the PUBLIC key as the HMAC secret
Server has an old code path: "if alg=HS256, verify with... public key?" → accepts!

ATTACK 3 — Weak Secret Brute Force:
─────────────────────────────────────
Secret: "secret" or "password123" or "jwt_secret"
Attacker captures a valid JWT → uses hashcat/john to crack the secret
Tools: hashcat -a 0 -m 16500 jwt.txt wordlist.txt
Once cracked: forges any token for any user

ATTACK 4 — Token Not Verified (Library Bug / Developer Mistake):
────────────────────────────────────────────────────────────────
jwt.decode(token)  // ❌ just decodes, doesn't verify!
jwt.verify(token, secret)  // ✅ decodes AND verifies

Developers sometimes call decode() to extract claims and forget verify()!

ATTACK 5 — Expired Token Still Accepted:
─────────────────────────────────────────
No exp claim checking → stolen token works forever
Solution: always check exp, use short-lived tokens (15 min access, 7d refresh)
```

---

## 💀 Real World Breach Example
**Auth0 (2015):** Algorithm confusion vulnerability — servers that accepted both RS256 and HS256 could be tricked into verifying RS256 tokens as HS256 signed with the public key. Public keys are... public. CVE-2015-9235 affected many JWT libraries.

**Okta (2022):** JWT verification flaw — under specific conditions, a valid signature was accepted for an invalid payload. Affected customers who used specific token validation code paths.

---

## 🛡️ How to Prevent — Step by Step

```
Step 1: ALWAYS verify JWT signature — use verify(), never just decode()
Step 2: Explicitly specify allowed algorithms — NEVER accept 'none'
Step 3: Use strong secrets (≥256 bits random) for HS256
Step 4: Use RS256/ES256 for multi-service architectures (asymmetric)
Step 5: Set short expiry — access token 15 min, refresh token 7 days
Step 6: Validate all claims: exp, iat, iss, aud
Step 7: Implement token revocation (refresh token rotation or blocklist)
Step 8: Store tokens securely — httpOnly cookie or memory (not localStorage)
Step 9: Use HTTPS — never send tokens over HTTP
Step 10: Rotate secrets periodically and on breach
```

---

## 💻 Vulnerable Code (What NOT to do)

```javascript
// ❌ VULNERABLE JWT CODE

// ─── ATTACK 1: Accepting 'none' algorithm ─────────────────────
const jwt = require('jsonwebtoken');

// ❌ Not specifying allowed algorithms:
const payload = jwt.verify(token, secret);
// If attacker sends token with alg:none → library may accept it!

// ❌ Old vulnerable jsonwebtoken behavior:
// jwt.verify(token, '') with alg:none would pass in some older versions

// ─── ATTACK 2: Using decode() instead of verify() ────────────
const decoded = jwt.decode(token);  // ❌ NO signature verification!
const userId = decoded.userId;      // Attacker can inject any userId!

// ─── ATTACK 3: Weak secret ────────────────────────────────────
const secret = 'secret';           // ❌ trivially crackable
const secret = 'mysecret';         // ❌ in wordlists
const secret = process.env.JWT_SECRET || 'fallback';  // ❌ defaults to weak

// ─── ATTACK 4: No expiry check ────────────────────────────────
const token = jwt.sign({ userId }, secret);  // ❌ no exp! Token valid forever

// ─── ATTACK 5: Storing in localStorage ───────────────────────
localStorage.setItem('token', jwtToken);  // ❌ XSS can steal it!

// ─── ATTACK 6: Trusting claims without validation ────────────
const { role } = jwt.decode(token);  // ❌ not verified!
if (role === 'admin') grantAdminAccess();  // Attacker sets role: admin!
```

---

## 💻 Secure Code (What TO do)

```javascript
// ✅ SECURE JWT CODE

const jwt = require('jsonwebtoken');
const crypto = require('crypto');

// ─── Secure Token Generation ──────────────────────────────────
const ACCESS_TOKEN_SECRET = process.env.JWT_ACCESS_SECRET;  // min 256-bit random
const REFRESH_TOKEN_SECRET = process.env.JWT_REFRESH_SECRET;

// Generate strong secret (do this once, store in env):
// node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"

function generateAccessToken(userId, role) {
  return jwt.sign(
    {
      userId,
      role,
      iss: 'myapp.com',         // issuer
      aud: 'myapp.com',         // audience
    },
    ACCESS_TOKEN_SECRET,
    {
      expiresIn: '15m',          // ✅ short expiry — access token
      algorithm: 'HS256',        // explicitly set algorithm
      jwtid: crypto.randomUUID() // unique token ID (for revocation)
    }
  );
}

function generateRefreshToken(userId) {
  return jwt.sign(
    { userId, tokenVersion: 1 },  // version for invalidation
    REFRESH_TOKEN_SECRET,
    {
      expiresIn: '7d',            // longer for refresh
      algorithm: 'HS256',
    }
  );
}

// ─── Secure Token Verification ────────────────────────────────
function verifyAccessToken(token) {
  try {
    const payload = jwt.verify(token, ACCESS_TOKEN_SECRET, {
      algorithms: ['HS256'],        // ✅ WHITELIST algorithms — never 'none'!
      issuer: 'myapp.com',          // ✅ verify issuer
      audience: 'myapp.com',        // ✅ verify audience
      // exp is automatically checked by jsonwebtoken
    });
    return { valid: true, payload };
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return { valid: false, error: 'TOKEN_EXPIRED' };
    }
    if (err.name === 'JsonWebTokenError') {
      return { valid: false, error: 'INVALID_TOKEN' };
    }
    return { valid: false, error: 'VERIFICATION_FAILED' };
  }
}

// ─── Middleware (NestJS + Express) ────────────────────────────
function authMiddleware(req, res, next) {
  // Get token from httpOnly cookie OR Authorization header:
  const token = req.cookies.accessToken
    || req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }
  
  const { valid, payload, error } = verifyAccessToken(token);
  
  if (!valid) {
    if (error === 'TOKEN_EXPIRED') {
      return res.status(401).json({ error: 'Token expired', code: 'EXPIRED' });
      // Client should use refresh token to get new access token
    }
    return res.status(401).json({ error: 'Invalid token' });
  }
  
  req.user = payload;  // attach verified claims to request
  next();
}

// ─── Refresh Token Rotation (Best Practice) ──────────────────
app.post('/auth/refresh', async (req, res) => {
  const refreshToken = req.cookies.refreshToken;
  
  if (!refreshToken) {
    return res.status(401).json({ error: 'No refresh token' });
  }
  
  let payload;
  try {
    payload = jwt.verify(refreshToken, REFRESH_TOKEN_SECRET, {
      algorithms: ['HS256']  // ✅ whitelist here too
    });
  } catch {
    return res.status(401).json({ error: 'Invalid refresh token' });
  }
  
  // Check if refresh token was revoked (blocklist in Redis/DB):
  const isRevoked = await redisClient.get(`revoked:${refreshToken}`);
  if (isRevoked) {
    return res.status(401).json({ error: 'Token revoked' });
  }
  
  // ✅ ROTATE: revoke old refresh token, issue new ones
  await redisClient.setEx(`revoked:${refreshToken}`, 7 * 24 * 3600, '1');
  
  const newAccessToken = generateAccessToken(payload.userId, payload.role);
  const newRefreshToken = generateRefreshToken(payload.userId);
  
  res.cookie('accessToken', newAccessToken, {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
    maxAge: 15 * 60 * 1000  // 15 min
  });
  
  res.cookie('refreshToken', newRefreshToken, {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
    path: '/auth/refresh',  // ✅ refresh token only sent to this endpoint
    maxAge: 7 * 24 * 60 * 60 * 1000  // 7 days
  });
  
  res.json({ message: 'Tokens refreshed' });
});

// ─── RS256 for Microservices (Asymmetric) ─────────────────────
const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
  modulusLength: 2048
});

// Auth service (has private key — signs tokens):
const token = jwt.sign({ userId }, privateKey, {
  algorithm: 'RS256',
  expiresIn: '15m'
});

// API services (have public key only — verify tokens):
const payload = jwt.verify(token, publicKey, {
  algorithms: ['RS256']  // ✅ NEVER include 'HS256' here! Prevents confusion attack
});
```

---

## 🟠 Implementation in My Stack (NestJS)

```typescript
// ─── NestJS JWT Module Setup ──────────────────────────────────
// auth.module.ts
@Module({
  imports: [
    JwtModule.registerAsync({
      imports: [ConfigModule],
      useFactory: (config: ConfigService) => ({
        secret: config.get('JWT_ACCESS_SECRET'),
        signOptions: {
          expiresIn: '15m',
          algorithm: 'HS256',
          issuer: 'myapp.com',
          audience: 'myapp.com',
        },
      }),
      inject: [ConfigService],
    }),
  ],
})

// ─── JWT Guard ────────────────────────────────────────────────
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {}

// passport-jwt strategy:
@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(config: ConfigService) {
    super({
      jwtFromRequest: ExtractJwt.fromExtractors([
        (req) => req?.cookies?.accessToken,                    // httpOnly cookie
        ExtractJwt.fromAuthHeaderAsBearerToken(),              // fallback: Authorization header
      ]),
      secretOrKey: config.get('JWT_ACCESS_SECRET'),
      algorithms: ['HS256'],    // ✅ whitelist — no alg:none
      issuer: 'myapp.com',
      audience: 'myapp.com',
    });
  }

  validate(payload: any) {
    return { userId: payload.userId, role: payload.role };
  }
}
```

---

## 🔧 Security Tools + Libraries
| Tool | Purpose | Use |
|------|---------|-----|
| `jsonwebtoken` | Node.js JWT lib | `jwt.verify(token, secret, {algorithms: ['HS256']})` |
| `@nestjs/jwt` + `passport-jwt` | NestJS JWT auth | Strategy + Guard |
| `jwt.io` debugger | Decode/inspect JWTs | Development + debugging |
| `hashcat` | JWT secret cracker | Pentesting weak secrets |
| `jwt_tool` (Python) | JWT attack toolkit | Pentesting: alg:none, confusion |
| Redis | Refresh token blocklist | `SETEX revoked:TOKEN 604800 1` |

---

## ⚫ Interview Questions + Answers

**Q1: What is the "alg:none" attack and how do you prevent it?**
A1: JWT header specifies the signing algorithm. If a server accepts `alg: none`, an attacker can create a token with an empty signature — any payload, any claims, no verification needed. Prevention: always pass `algorithms: ['HS256']` (or whatever you use) to `jwt.verify()`. Never accept `none` in the allowed list. Many JWT libraries fixed this but explicit whitelisting is still required as a defense-in-depth. The vulnerability stems from trusting the `alg` field in the header which the attacker controls.

**Q2: How does RS256 vs HS256 algorithm confusion attack work?**
A2: RS256 uses asymmetric keys — private key signs, public key verifies. HS256 uses the same secret for both. The attack: if a server that uses RS256 also accepts HS256, an attacker can sign a token using HS256 with the **public key as the HMAC secret**. The server then tries to verify the HS256 signature using the public key — which it knows — and the verification passes. Prevention: when using RS256 for verification, set `algorithms: ['RS256']` only — never include HS256 in the list for services that only have the public key.

**Q3: What's the difference between jwt.decode() and jwt.verify()?**
A3: `decode()` only base64-decodes the payload — it does NOT check the signature, expiry, or any claims. Anyone can decode a JWT without a secret. `verify()` validates the signature cryptographically (proving it was signed by the expected secret/key) AND validates standard claims (exp, nbf, iss, aud). Always use `verify()` for authentication. `decode()` is useful only for inspecting token contents in debugging or when you already verified the signature by other means.

**Q4: Where should JWTs be stored — localStorage vs httpOnly cookie?**
A4: See topic 103 for the full breakdown. Summary: **localStorage** — accessible by JavaScript → XSS steals it → persistent theft. **httpOnly cookie** — not accessible by JavaScript → XSS can't steal it → but vulnerable to CSRF (mitigated by SameSite=Strict). For access tokens (15 min): in-memory (best for SPA), or httpOnly cookie with SameSite=Strict. For refresh tokens: httpOnly cookie with SameSite=Strict, path restricted to `/auth/refresh`. Never store sensitive JWT claims (password, full PAN) in the payload — it's only base64 encoded, not encrypted.

**Q5: What is refresh token rotation and why is it important?**
A5: Refresh token rotation means every time you use a refresh token to get a new access token, the old refresh token is revoked and a new one is issued. Why: if a refresh token is stolen, the attacker uses it → old token revoked → legitimate user's next request also fails (their old token is now invalid) → server detects a revoked token being used → alarm raised, all tokens for that user can be revoked. Without rotation, a stolen refresh token is valid for its full lifetime (7 days) with no way to detect theft. Implementation: store used refresh tokens in a Redis blocklist.

---

## ✅ Security Checklist
```
□ jwt.verify() used (NEVER just jwt.decode() for auth)
□ algorithms whitelist specified — ['HS256'] or ['RS256'], never 'none'
□ Strong secret: min 256-bit random (not 'secret' or 'password')
□ Access token expiry: 15 minutes max
□ Refresh token expiry: 7-30 days
□ Token claims validated: exp, iss, aud
□ Refresh token rotation implemented
□ Tokens stored in httpOnly cookies (not localStorage)
□ SameSite=Strict on token cookies
□ Refresh token cookie path restricted to /auth/refresh
□ Token revocation list (Redis) for logout/breach response
□ JWT secrets in environment variables (not hardcoded)
□ RS256 for microservices (each service has only public key)
```

---

## 📊 Visual Diagram

```
JWT ANATOMY:
eyJhbGciOiJIUzI1NiJ9  .  eyJ1c2VySWQiOjF9  .  SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
   ↑ Header (base64)        ↑ Payload (base64)    ↑ Signature (HMAC/RSA)

alg:none ATTACK:
{alg:"none"}.{userId:1,role:"admin"}.  ← empty signature
Server without algorithm whitelist: "no signature needed" → accepts!

SECURE FLOW:
Login → Server signs token with secret → Returns token
Request → Client sends token → Server VERIFIES signature + exp + iss + aud
→ Valid? Extract claims, process request
→ Invalid? 401 Unauthorized

REFRESH TOKEN ROTATION:
Access (15min) expires → Client sends refresh token
→ Server: verify + check not revoked
→ Issue NEW access token + NEW refresh token
→ REVOKE old refresh token in Redis
→ Next request with old refresh: "revoked" → logout all sessions
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| JWT | JSON Web Token — self-contained auth token | Self-contained authentication token |
| alg:none | No signature algorithm — verification skipped | Signature check bypass attack |
| HS256 | Symmetric signing (same secret for sign+verify) | एक ही secret से sign और verify |
| RS256 | Asymmetric (private key sign, public key verify) | Private key sign करे, public key verify |
| Refresh Token | Long-lived token to get new access tokens | New access token लेने के लिए |
| Token Rotation | Revoke old refresh token on each use | हर use पर नया token, पुराना revoke |
| Claims | Data payload in JWT (userId, role, exp) | Token में stored information |

---

## ⚡ 3-Line Summary
**English:**
1. JWT attacks: alg:none bypasses signature, weak secrets are crackable, decode() skips verification, no exp check means eternal tokens.
2. Prevention: always use verify() with explicit algorithm whitelist, strong random secrets, 15-min access token expiry, httpOnly cookies.
3. Refresh token rotation + Redis revocation list enables secure logout and breach response.

**Hindi:**
1. JWT attacks: alg:none signature skip, weak secrets crack होते हैं, decode() verification नहीं करता, exp check न हो तो token forever valid।
2. Fix: verify() always, algorithm whitelist, strong secret, 15-min expiry, httpOnly cookies।
3. Refresh token rotation + Redis revocation से logout और breach के बाद भी security रहती है।

---

## 🚨 Red Flag Signs
- `jwt.decode()` used for authentication (not `jwt.verify()`)
- No `algorithms` option in `jwt.verify()` call
- Secret is short, dictionary word, or same as app name
- No `expiresIn` in `jwt.sign()` — token lives forever
- JWT stored in `localStorage` in client code
- Same JWT secret used for both access and refresh tokens
- No token revocation mechanism (logout just deletes client-side cookie)
- `process.env.JWT_SECRET || 'fallback_secret'` in production

---

## ➡️ Next Topic
**103. Token Storage Security** — localStorage vs sessionStorage vs httpOnly cookie vs memory — complete security comparison with XSS and CSRF implications.
