# 113. Authentication Service (Design)
# हिंदी में: Authentication Service — signup, login (password/OTP/Google), tokens, MFA, logout, और account सुरक्षा संभालने वाली केंद्रीय सेवा, जिसे web और mobile दोनों इस्तेमाल करें

---

## 🔵 Simple Definition (English)
Design a central **Authentication (AuthN) service / Identity Provider** for a product with web and mobile apps and many microservices. It handles **registration, login (password, phone OTP, social/OIDC, passkeys), MFA, session/token issuance (access + refresh), token refresh and revocation, password reset, device management, and security protections** (rate limiting, breached-password checks, anomaly detection, audit logs). Other services **verify tokens locally** (JWKS) without calling it on every request.

## 🔵 सरल परिभाषा (Hindi)
एक केंद्रीय सेवा जो signup, login (password, OTP, Google, passkey), MFA, tokens देना/नवीनीकरण/रद्द करना, password reset, devices की सूची और सुरक्षा (rate limit, संदिग्ध login पहचान, audit log) संभाले।
बाक़ी services हर बार इससे नहीं पूछतीं — public key (JWKS) से token ख़ुद जाँच लेती हैं।

---

## 🔴 Problem it Solves
If every service implements its own login:
- Inconsistent security (one service stores plaintext passwords, another forgets rate limits).
- Users log in separately to each part of the product; no single logout or device list.
- Hard to add MFA, social login or passkeys everywhere.
- Account takeover via credential stuffing, OTP abuse and session theft.

A dedicated auth service centralizes **identity, credentials and session security** and gives every client and service **one standard**: OIDC/OAuth-style tokens.

## 🔴 यह क्यों बना? (Hindi)
हर service अपना login बनाए तो सुरक्षा अलग-अलग (कहीं password सादा सेव, कहीं rate limit नहीं), हर हिस्से में अलग login, MFA/social login हर जगह जोड़ना मुश्किल, और account हैक होने का ख़तरा।
केंद्रीय auth service पहचान, credentials और session सुरक्षा एक जगह देती है — सबके लिए एक मानक token।

---

## 🟢 How it Works — Step by Step (Interview Design)

### 1. Requirements

```
Functional:
  - Signup / login: email+password, phone OTP (India!), Google/Apple (OIDC), passkeys (WebAuthn)
  - MFA (TOTP authenticator, SMS fallback), step-up auth for sensitive actions
  - Issue short-lived access tokens (JWT) + rotating refresh tokens; logout; logout-all-devices
  - Password reset, email/phone verification, account linking (same person, many login methods)
  - Device/session list; admin: lock/unlock accounts; audit trail
Non-functional:
  - Highly available (if auth is down, nobody can log in): 99.99%
  - Low latency: login < 300 ms (excluding OTP delivery); token verification at services ~0 network
  - Secure by default: OWASP ASVS, encryption, least privilege, abuse protection
  - Scale: 50M users, peak 5k logins/s (app launch storms), 100k token refreshes/s
```

### 2. High-level architecture

```
   📱 RN App   🌐 Next.js (BFF)    🤝 Partners
        │            │                 │
        └──── HTTPS ─┴─────────────────┘
                     ▼
            ┌─────────────────┐   WAF/bot protection, rate limits (Topic 112)
            │  API Gateway    │
            └────────┬────────┘
                     ▼
 ┌──────────────────────────────────────────────┐
 │               AUTH SERVICE (stateless pods)   │
 │  /signup /login /otp /oauth/callback /token  │
 │  /refresh /logout /mfa /passkeys /jwks       │
 └───┬──────────┬──────────┬──────────┬─────────┘
     ▼          ▼          ▼          ▼
 Users DB    Redis       KMS/HSM    Event bus (Kafka/SNS)
 (Postgres)  OTPs, rate  signing    UserRegistered, LoginSucceeded,
 users,      limits,     keys       LoginFailed, PasswordChanged → notification,
 identities, sessions,   (RS256/    risk engine, analytics, audit log store
 credentials denylist    ES256)
 refresh_tokens
 devices, audit

 Other services ──► verify JWT locally with cached JWKS (no call to auth service)
```

### 3. Data model (simplified)

```
users(id, status, email, email_verified, phone, phone_verified, name, created_at)
credentials(user_id, type['password','totp','passkey'], secret_hash/public_key, created_at)
identities(provider['google','apple'], provider_sub, user_id, email)         -- OIDC links (Topic 56)
refresh_tokens(id, user_id, device_id, family_id, token_hash, expires_at, used_at, revoked)
devices(id, user_id, platform, app_version, last_ip, last_seen, push_token)
audit_log(id, user_id, event, ip, user_agent, ts, metadata)                  -- append-only
```

### 4. Key flows

```
Password login:
  1. rate limit (per IP + per account) → 2. fetch user → 3. verify argon2id/bcrypt hash (constant time)
  4. risk check (new device/country? impossible travel?) → maybe require MFA/OTP step-up
  5. issue access JWT (10–15 min) + refresh token (opaque, rotated, hashed in DB) → 6. audit + event

Phone OTP login (very common in India):
  1. POST /otp {phone} → rate limits (per phone/IP/device), CAPTCHA/app attestation if suspicious
  2. generate 6-digit OTP, store HASH in Redis with TTL 5 min + attempt counter, send via SMS
     (DLT-registered template) / WhatsApp; auto-read on Android (SMS Retriever API)
  3. POST /otp/verify → max 5 attempts → delete OTP → find/create user → issue tokens

Social login: OAuth Code + PKCE → verify id_token (iss, aud, nonce) → link by (provider, sub) → tokens

Refresh: POST /token/refresh → rotate refresh token; reuse of old token → revoke family (theft)
Logout: revoke refresh token (and optionally add access jti to Redis denylist until exp)
Password reset: single-use, short-lived token (hashed), sent to verified email; revoke all sessions after
```

### 5. Token strategy (Topic 54, 57)

```
Access token: JWT RS256/ES256, 10–15 min, claims {sub, roles/scopes, tenant, sid}, kid header
Refresh token: random 256-bit, stored hashed, rotation + reuse detection, bound to device id
Web: refresh token in HttpOnly Secure SameSite cookie (BFF), access token in memory
Mobile: tokens in Keychain/Keystore; device binding; biometric unlock (Topic M16)
Key rotation: new kid published in JWKS before use; old keys kept until tokens expire
Services: verify via cached JWKS; check exp/iss/aud; optional sid revocation check via Redis
```

### 6. Security protections

```
Passwords: argon2id (or bcrypt cost 12), pepper in KMS, breached-password check (HaveIBeenPwned k-anon),
           no max-length truncation issues; NIST guidance (length > complexity rules)
Credential stuffing: rate limits per IP/account/ASN, bot detection, CAPTCHA after failures,
           device fingerprinting, risk-based MFA
Account enumeration: same response for "user not found" vs "wrong password"
OTP: hashed, TTL, limited attempts, per-phone limits, SMS pumping protection, constant-time compare
MFA: TOTP/passkeys preferred over SMS (SIM swap risk)
Sessions: rotate on privilege change, show device list, remote logout, notify on new device login
Transport/storage: TLS everywhere, PII encrypted at rest, secrets in KMS/Secrets Manager
Audit: immutable logs of auth events; alerts on anomalies
```

### 7. Scaling & availability

```
- Stateless auth pods behind LB, multi-AZ (multi-region for big products)
- Token verification is LOCAL in every service → auth service not in the hot path of every API call
- Redis for OTP/rate limits/denylist (replicated); Postgres primary + replicas (read user lookups)
- App-launch storm: thousands refresh tokens at once → refresh endpoint must scale; jitter refresh timing
- Degradation: if SMS provider down → fallback provider / WhatsApp / email OTP
- Build vs buy: Auth0/Okta/Cognito/Clerk/Firebase/Keycloak give most of this — build when you need
  deep customization, cost control at scale, or data residency
```

## 🟢 कैसे काम करता है? (Hindi)
1. Login तरीके: password, phone OTP (भारत में सबसे आम), Google/Apple, passkey; ज़रूरत पड़ने पर MFA।
2. सफल login पर छोटा access token (JWT, 15 मिनट) और बदलने वाला refresh token (DB में hash) मिलता है; बाक़ी services JWKS से ख़ुद जाँचती हैं।
3. OTP: hash करके Redis में 5 मिनट के लिए, 5 कोशिशें, हर phone/IP पर सीमा, SMS दुरुपयोग से बचाव।
4. सुरक्षा: argon2/bcrypt, लीक हुए passwords की जाँच, credential stuffing पर rate limit और CAPTCHA, नए device पर सूचना, audit log।
5. Auth pods stateless और कई AZ में; refresh endpoint ऐप खुलने की भीड़ संभाले; ज़रूरत न हो तो Auth0/Cognito/Keycloak जैसा तैयार समाधान लो।

---

## 🟡 Real World Example

**Google / Microsoft identity** — central identity providers issue OIDC tokens to all products, with risk-based challenges (new device, location) and passkeys rolled out to billions of accounts.

**Indian apps (Swiggy, Zomato, PhonePe, CRED)** — phone-number + OTP login is the default (Android auto-read via the SMS Retriever API), with device binding, MPIN or biometrics for payments, and new-device alerts. UPI apps additionally bind the device to the SIM and phone number.

**Auth0 / Okta / AWS Cognito / Firebase Auth / Keycloak** — "auth as a service" used by thousands of companies to avoid building and securing all of this.

**Credential stuffing at scale** — services like Disney+ (2019 launch) and many e-commerce sites saw accounts taken over with passwords leaked from other sites. That's why breached-password checks, MFA and rate limits are standard.

## 🟡 Real Example Hindi में
भारतीय ऐप्स (Swiggy, PhonePe, CRED) में phone + OTP login आम है — Android पर OTP अपने आप पढ़ लिया जाता है; पेमेंट के लिए MPIN/fingerprint और device binding।
Auth0, Cognito, Firebase, Keycloak यह सब तैयार देते हैं। Disney+ के launch पर दूसरी साइटों से लीक passwords से हज़ारों accounts हैक हुए — इसलिए MFA और लीक-password जाँच ज़रूरी है।

---

## 🟠 My Stack Example

### Password hashing + login (Node, argon2)
```js
import argon2 from 'argon2';

export async function register({ email, password }) {
  if (await isBreached(password)) throw new AppError(422, 'PASSWORD_BREACHED');   // HIBP k-anonymity API
  const hash = await argon2.hash(password, { type: argon2.argon2id, memoryCost: 19456, timeCost: 2 });
  return db.tx(async (t) => {
    const u = await t.one('INSERT INTO users(email) VALUES ($1) RETURNING id', [email.toLowerCase()]);
    await t.none("INSERT INTO credentials(user_id, type, secret_hash) VALUES ($1,'password',$2)", [u.id, hash]);
    await outbox(t, 'UserRegistered', { userId: u.id });
    return u;
  });
}

const DUMMY_HASH = await argon2.hash('dummy-password-for-timing');
export async function login({ email, password, deviceId, ip }) {
  const row = await db.oneOrNone(
    "SELECT u.id, u.status, c.secret_hash FROM users u JOIN credentials c ON c.user_id=u.id AND c.type='password' WHERE u.email=$1",
    [email.toLowerCase()]);
  const ok = await argon2.verify(row?.secret_hash ?? DUMMY_HASH, password);   // same timing either way
  if (!row || !ok || row.status !== 'active') {
    await audit('LOGIN_FAILED', { email, ip });
    throw new AppError(401, 'INVALID_CREDENTIALS');                          // no user enumeration
  }
  const risk = await riskEngine.assess({ userId: row.id, deviceId, ip });
  if (risk.requireMfa) return { mfaRequired: true, challengeId: await createMfaChallenge(row.id) };
  await audit('LOGIN_SUCCEEDED', { userId: row.id, ip, deviceId });
  return issueTokens({ id: row.id }, deviceId);                              // Topic 54
}
```

### OTP send/verify (Redis)
```js
app.post('/auth/otp', limit(otpPerIp, ip), limit(otpPerPhone, phone), async (req, res) => {
  const phone = normalizeIndianPhone(req.body.phone);
  const otp = crypto.randomInt(100000, 1000000).toString();
  await redis.set(`otp:${phone}`, JSON.stringify({ h: sha256(otp + PEPPER), tries: 0 }), { EX: 300 });
  await sms.send(phone, templates.otp(otp));                // DLT template; WhatsApp fallback
  res.json({ sent: true, retryAfter: 30 });
});

app.post('/auth/otp/verify', async (req, res) => {
  const phone = normalizeIndianPhone(req.body.phone);
  const raw = await redis.get(`otp:${phone}`);
  if (!raw) return res.status(400).json({ error: 'OTP_EXPIRED' });
  const st = JSON.parse(raw);
  if (st.tries >= 5) { await redis.del(`otp:${phone}`); return res.status(429).json({ error: 'TOO_MANY_ATTEMPTS' }); }
  if (!crypto.timingSafeEqual(Buffer.from(st.h), Buffer.from(sha256(req.body.otp + PEPPER)))) {
    st.tries++; await redis.set(`otp:${phone}`, JSON.stringify(st), { KEEPTTL: true });
    return res.status(401).json({ error: 'OTP_INVALID' });
  }
  await redis.del(`otp:${phone}`);
  const user = await findOrCreateByPhone(phone);
  res.json(await issueTokens(user, req.get('X-Device-Id')));
});
```

### JWKS endpoint (other services verify locally)
```js
app.get('/.well-known/jwks.json', (_, res) => res.set('Cache-Control', 'public, max-age=300').json({ keys: [currentPublicJwk, previousPublicJwk] }));
```

### FastAPI resource service verifying tokens (no call to auth service)
```python
jwks = jwt.PyJWKClient("https://auth.myapp.com/.well-known/jwks.json", cache_keys=True)
async def current_user(creds=Depends(HTTPBearer())):
    key = jwks.get_signing_key_from_jwt(creds.credentials).key
    claims = jwt.decode(creds.credentials, key, algorithms=["ES256", "RS256"], audience="myapp-api", issuer="https://auth.myapp.com")
    if await r.exists(f"revoked_sid:{claims.get('sid')}"):
        raise HTTPException(401, "SESSION_REVOKED")
    return claims
```

### React Native: OTP auto-read + secure storage
```ts
// Android SMS Retriever (react-native-otp-verify) auto-fills OTP; iOS: textContentType="oneTimeCode"
<TextInput keyboardType="number-pad" textContentType="oneTimeCode" autoComplete="sms-otp" maxLength={6} />
await SecureStore.setItemAsync('refreshToken', tokens.refreshToken);
```

---

## ⚫ Interview Questions + Answers

**Q1: Design an authentication service for web and mobile apps with many microservices.**
A1: A dedicated, stateless auth service behind the gateway, owning users, credentials, identities, sessions and refresh tokens (Postgres), with OTPs, rate limits and revocations in Redis and signing keys in KMS. It supports password, OTP, social OIDC, passkeys and MFA. It issues short-lived JWT access tokens (RS256/ES256 with kid and JWKS) and rotating refresh tokens bound to devices. Services verify tokens locally via JWKS. It publishes auth events for notifications, risk and audit. Add strong protections: hashing, rate limits, bot and credential-stuffing defences, no enumeration, audit logs. Run it multi-AZ with high availability.

**Q2: How do you store passwords securely?**
A2: Never store plaintext or reversibly encrypted passwords. Use a slow, salted, memory-hard hash: argon2id (preferred), scrypt, or bcrypt with an appropriate cost. Each hash includes a unique salt, optionally with a pepper kept in KMS. Verify in constant time, rehash on login when parameters are upgraded, check new passwords against breached-password lists, enforce a reasonable minimum length (no arbitrary complexity rules), and rate-limit login attempts.

**Q3: How would you implement OTP login securely?**
A3: Generate a random 6-digit code with a CSPRNG, store only its hash with a short TTL (about 5 minutes) and an attempt counter, and send it through a reliable provider with a fallback. Enforce per-phone, per-IP and per-device rate limits plus CAPTCHA or app attestation for suspicious traffic, and cap verification attempts (e.g. 5) before invalidating the code. Compare in constant time, delete the code after success, monitor for SMS pumping fraud, and bind the resulting session to the device. Prefer stronger MFA (TOTP, passkeys) for high-risk actions because of SIM-swap risks.

**Q4: How do you revoke access immediately when an account is compromised?**
A4: Revoke all of the user's refresh tokens (and their families) in the DB so no new access tokens can be issued. For live access tokens, maintain a Redis denylist of session IDs or JTIs (or bump a per-user token version checked by services) until those tokens expire, keeping access tokens short-lived (5–15 min). Force password reset or MFA re-enrollment, notify the user, and audit the incident. Services can subscribe to "session revoked" events to clear caches.

**Q5: Should you build your own auth or use a provider?**
A5: Use a provider (Auth0, Okta, Cognito, Clerk, Firebase, Keycloak) when you want speed, built-in security features, SSO, MFA and compliance, and the cost per user is acceptable. Build your own when you need deep customization (complex India-specific OTP and device-binding flows), very large scale where per-MAU pricing is expensive, data residency or regulatory control, or tight integration. Even then, use proven libraries and standards (OAuth 2.1, OIDC, WebAuthn) and get security reviews. Many teams start with a provider and migrate later.

---

## 🔷 Trade-offs
✅ Central auth: consistent security, SSO across products, easier MFA/passkeys, single audit trail.
❌ Critical dependency (must be HA), complex to build securely, target for attacks.
✅ Local JWT verification: scalable — ❌ revocation needs short TTL + denylist.
✅ OTP login: easy for users (India) — ❌ SMS cost, delivery issues, SIM-swap risk.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Identity Provider (IdP) | Service that authenticates users | पहचान देने वाली सेवा |
| argon2id / bcrypt | Password hashing algorithms | password hash करने के तरीके |
| OTP | One-time password | एक बार का पासवर्ड |
| MFA | Multi-factor authentication | कई तरीकों से पहचान |
| Passkey / WebAuthn | Phishing-resistant public-key login | बिना password वाला सुरक्षित login |
| Credential stuffing | Using leaked passwords elsewhere | लीक passwords से हमला |
| Account enumeration | Discovering which accounts exist | कौन-से accounts हैं पता करना |
| Step-up auth | Extra check for sensitive actions | ज़रूरी काम पर दोबारा पहचान |
| JWKS | Public keys for token verification | token जाँचने की public keys |
| Device binding | Tie session to a device | session को device से जोड़ना |

---

## ⚡ 3-Line Summary
**English:**
1. Central auth service: signup/login (password, OTP, social, passkeys), MFA, short JWT access + rotating refresh tokens, JWKS for local verification.
2. Security: argon2id, breached-password checks, rate limits & bot defense, no enumeration, hashed OTPs with attempt limits, device binding, audit logs.
3. Stateless & HA; scale refresh/OTP paths; fallbacks for SMS; consider buying (Auth0/Cognito/Keycloak) vs building.

**Hindi:**
1. केंद्रीय auth service: password/OTP/Google/passkey login, MFA, छोटा JWT + बदलने वाला refresh token, JWKS से जाँच।
2. सुरक्षा: argon2id, लीक-password जाँच, rate limit, OTP hash + सीमित कोशिशें, device binding, audit log।
3. Stateless और HA; SMS के लिए fallback; तैयार समाधान (Auth0/Cognito) बनाम ख़ुद बनाना — सोचकर चुनो।

---

## ➡️ Next Topic Suggestion
**114. Notification System** — Auth sends OTPs and new-device alerts; orders send status updates. Next: design a notification system for push, SMS, email, WhatsApp and in-app at scale, with preferences, templates, retries, priorities and dedup.
