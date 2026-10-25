# 128. API Key Authentication
# हिंदी में: API Key Authentication

---

## 🔵 Simple Definition (English)
**API Key authentication** identifies and authorizes a calling application (not an individual end-user) using a long, random, static string (the API key) sent with every request, typically in a header (`X-API-Key`) or query parameter. It's simpler than OAuth/JWT — no login flow, no expiry by default — commonly used for server-to-server integrations, third-party developer access, and rate-limiting/billing by client application.

## 🔵 सरल परिभाषा (Hindi)
**API Key authentication** एक calling application (individual end-user नहीं) को identify और authorize करता है एक लंबी, random, static string (API key) से जो हर request के साथ भेजी जाती है, typically header (`X-API-Key`) या query parameter में। ये OAuth/JWT से simpler है — कोई login flow नहीं, by default कोई expiry नहीं — commonly server-to-server integrations, third-party developer access, और client application के हिसाब से rate-limiting/billing के लिए use होता है।

---

## 🔴 Problem it Solves
When the caller is a MACHINE or application (not a human user going through a login flow) — e.g., a partner service calling your payment API, a mobile app's backend calling a weather data provider, a CI/CD pipeline calling a deployment API — full OAuth/JWT login flows are unnecessary overhead. API keys provide a simple, static credential that identifies WHICH application/account is making the request, enabling per-key rate limiting, usage tracking/billing, and access revocation (regenerate/delete the key) without needing session management or token refresh flows.

## 🔴 यह क्यों बना? (Hindi)
जब caller एक MACHINE या application है (human user login flow से नहीं गुज़र रहा) — जैसे कोई partner service आपके payment API को call करे, mobile app का backend किसी weather data provider को call करे, CI/CD pipeline किसी deployment API को call करे — पूरे OAuth/JWT login flows unnecessary overhead हैं। API keys एक simple, static credential देते हैं जो identify करता है कि कौन सा application/account request कर रहा है, per-key rate limiting, usage tracking/billing, और access revocation (key regenerate/delete करना) enable करता है बिना session management या token refresh flows की ज़रूरत के।

---

## 🟢 How it Works — Step by Step

Step 1 → Developer signs up for API access on your platform's dashboard; your system generates a long, cryptographically random key (e.g., `sk_live_51H8xK2eZvKYlo2C...`) tied to their account.
Step 2 → You store a HASH of the key in your database (never the raw key, similar to password hashing) and show the RAW key to the developer ONCE, telling them to save it securely (it typically can't be retrieved again).
Step 3 → The developer's application includes this key in every API request, usually as `X-API-Key: sk_live_...` header or `Authorization: ApiKey sk_live_...`.
Step 4 → Your server middleware extracts the key, hashes the incoming value, and looks up a matching hash in the database to identify WHICH account/application made the request.
Step 5 → Once identified, apply account-specific logic: rate limits (different tiers get different quotas), permission scopes (some keys are "read-only," others "full access"), and usage logging for billing — all without any session or token refresh machinery.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Developer आपके platform के dashboard पर API access के लिए sign up करता है; आपका system एक लंबी, cryptographically random key generate करता है (जैसे `sk_live_51H8xK2eZvKYlo2C...`) उनके account से tied।
Step 2 → आप key का एक HASH database में store करते हो (कभी raw key नहीं, password hashing जैसा) और developer को RAW key सिर्फ ONCE दिखाते हो, उन्हें securely save करने बोलते हो (typically फिर से retrieve नहीं हो सकती)।
Step 3 → Developer का application हर API request में ये key include करता है, usually `X-API-Key: sk_live_...` header या `Authorization: ApiKey sk_live_...` के रूप में।
Step 4 → आपका server middleware key extract करता है, incoming value hash करता है, और database में matching hash ढूंढता है ये identify करने के लिए कि कौन सा account/application request कर रहा है।
Step 5 → Identify होने के बाद, account-specific logic apply करो: rate limits (different tiers को different quotas), permission scopes (कुछ keys "read-only" होती हैं, कुछ "full access"), और billing के लिए usage logging — बिना किसी session या token refresh machinery के।

---

## 🟡 Real World Example
**Razorpay API integration for merchants:** When an e-commerce business integrates Razorpay's payment gateway, they get a `key_id` and `key_secret` pair from the Razorpay dashboard. Every server-to-server API call (creating a payment order, checking payment status) includes these as HTTP Basic Auth credentials. Razorpay uses the `key_id` to identify WHICH merchant account is calling, applies that merchant's specific configuration (webhook URLs, settlement account), tracks usage for their transaction-fee billing, and can instantly revoke/regenerate the key pair from the dashboard if compromised — all without the merchant's backend ever needing to implement a login flow, since it's a machine (their server) calling another machine (Razorpay's API), not a human logging in.

## 🟡 Real Example Hindi mein
**Razorpay API integration for merchants:** जब कोई e-commerce business Razorpay का payment gateway integrate करता है, उन्हें Razorpay dashboard से `key_id` और `key_secret` pair मिलता है। हर server-to-server API call (payment order बनाना, payment status check करना) इन्हें HTTP Basic Auth credentials के रूप में include करती है। Razorpay `key_id` use करता है ये identify करने के लिए कि कौन सा merchant account call कर रहा है, उस merchant की specific configuration apply करता है (webhook URLs, settlement account), transaction-fee billing के लिए usage track करता है, और compromise होने पर dashboard से key pair instantly revoke/regenerate कर सकता है — सबकुछ बिना merchant के backend को login flow implement किए, क्योंकि ये एक machine (उनका server) दूसरी machine (Razorpay's API) को call कर रही है, human login नहीं कर रहा।

---

## 💻 Code Example — Basic

```javascript
// api-key-auth-basic.js
const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.json());

// Mock database of valid API keys (in production, store HASHES, not raw keys)
const validApiKeys = new Map([
  ['sk_live_abc123', { accountName: 'Zomato Partner Service', tier: 'premium' }],
  ['sk_live_def456', { accountName: 'Free Tier App', tier: 'free' }],
]);

// ─── MIDDLEWARE: validate the API key from a header ────────────────────────────
function requireApiKey(req, res, next) {
  const apiKey = req.headers['x-api-key']; // standard convention

  if (!apiKey) {
    return res.status(401).json({ error: 'API key required' });
  }

  const account = validApiKeys.get(apiKey);
  if (!account) {
    return res.status(401).json({ error: 'Invalid API key' });
  }

  req.apiAccount = account; // attach identified account info to the request
  next();
}

app.get('/api/weather', requireApiKey, (req, res) => {
  res.json({
    temperature: 32,
    city: 'Mumbai',
    requestedBy: req.apiAccount.accountName, // demonstrates account identification
  });
});

app.listen(3000, () => console.log('API key auth server running on port 3000'));
```

## 💻 Code Example — Advanced

```javascript
// api-key-auth-advanced.js — Hashed storage, scoped permissions, per-key rate limiting
const express = require('express');
const crypto = require('crypto');
const rateLimit = require('express-rate-limit');

const app = express();
app.use(express.json());

// ─── 1. HASH THE API KEY before storing (never store raw keys, like passwords) ──
function hashApiKey(rawKey) {
  return crypto.createHash('sha256').update(rawKey).digest('hex'); // SHA-256 sufficient for high-entropy random keys
}

// Mock DB storing HASHED keys with scoped permissions and tier info
const apiKeyStore = new Map([
  [hashApiKey('sk_live_premium_xyz'), { account: 'BigClient Inc', scopes: ['read', 'write'], tier: 'premium' }],
  [hashApiKey('sk_live_readonly_abc'), { account: 'ReadOnlyPartner', scopes: ['read'], tier: 'basic' }],
]);

// ─── 2. GENERATE a new API key (shown to developer ONCE at creation time) ────
function generateApiKey() {
  const rawKey = `sk_live_${crypto.randomBytes(24).toString('hex')}`; // 192 bits of randomness
  return { rawKey, hashedKey: hashApiKey(rawKey) };
}

// ─── 3. AUTHENTICATION MIDDLEWARE using hashed lookup ─────────────────────────
function requireApiKey(req, res, next) {
  const rawKey = req.headers['x-api-key'];
  if (!rawKey) return res.status(401).json({ error: 'API key required' });

  const hashedIncoming = hashApiKey(rawKey);
  const account = apiKeyStore.get(hashedIncoming);

  if (!account) return res.status(401).json({ error: 'Invalid API key' });

  req.apiAccount = account;
  next();
}

// ─── 4. SCOPE-BASED AUTHORIZATION (not just identification) ──────────────────
function requireScope(scope) {
  return (req, res, next) => {
    if (!req.apiAccount.scopes.includes(scope)) {
      return res.status(403).json({ error: `This API key lacks the '${scope}' scope` });
    }
    next();
  };
}

// ─── 5. PER-TIER RATE LIMITING ──────────────────────────────────────────────────
const premiumLimiter = rateLimit({ windowMs: 60 * 1000, max: 1000 });
const basicLimiter = rateLimit({ windowMs: 60 * 1000, max: 100 });

function tieredRateLimit(req, res, next) {
  const limiter = req.apiAccount.tier === 'premium' ? premiumLimiter : basicLimiter;
  return limiter(req, res, next);
}

app.get('/api/data', requireApiKey, tieredRateLimit, requireScope('read'), (req, res) => {
  res.json({ data: 'sensitive business data', account: req.apiAccount.account });
});

app.post('/api/data', requireApiKey, tieredRateLimit, requireScope('write'), (req, res) => {
  res.json({ message: 'Data created', account: req.apiAccount.account });
});

// ─── 6. KEY GENERATION ENDPOINT (would itself require admin/user session auth) ──
app.post('/admin/generate-key', (req, res) => {
  const { rawKey, hashedKey } = generateApiKey();
  apiKeyStore.set(hashedKey, { account: req.body.accountName, scopes: ['read'], tier: 'basic' });
  // Show raw key ONLY in this response — it cannot be retrieved again afterward
  res.json({ apiKey: rawKey, warning: 'Save this key securely — it will not be shown again' });
});

app.listen(3000, () => console.log('Production-grade API key server running on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

const hashApiKey = (key) => crypto.createHash('sha256').update(key).digest('hex');

const requireApiKey = async (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  if (!apiKey) return res.status(401).json({ error: 'API key required' });

  const hashed = hashApiKey(apiKey);
  const account = await ApiKeyModel.findOne({ hashedKey: hashed, active: true }); // Mongoose
  if (!account) return res.status(401).json({ error: 'Invalid or revoked API key' });

  // Log usage for billing/analytics
  await UsageLog.create({ accountId: account._id, endpoint: req.path, timestamp: new Date() });

  req.apiAccount = account;
  next();
};

app.use('/api/v1', requireApiKey); // applies to all v1 API routes

app.get('/api/v1/orders', (req, res) => {
  res.json({ orders: [], account: req.apiAccount.name });
});

app.listen(4000, () => console.log('API key-protected service running on port 4000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Storing raw API keys in the database (and comparing with `===`)
✅ Correct: Store a HASH of the key (SHA-256 is fine since API keys are already high-entropy random strings, unlike passwords which need bcrypt/argon2's slow hashing against low-entropy human-chosen input) — if the DB leaks, raw usable keys aren't exposed.

```javascript
// Wrong — raw key stored and compared; DB leak = instant full compromise of all keys
const account = await ApiKeyModel.findOne({ rawKey: req.headers['x-api-key'] });

// Right — hash before storing/comparing
const hashed = crypto.createHash('sha256').update(req.headers['x-api-key']).digest('hex');
const account = await ApiKeyModel.findOne({ hashedKey: hashed });
```

❌ Mistake 2: Passing the API key as a URL query parameter instead of a header
✅ Correct: Query parameters get logged in server access logs, browser history, and proxy logs by default — headers generally don't get logged the same way, reducing accidental exposure.

```javascript
// Wrong — key ends up in server logs, browser history, possibly shared/bookmarked URLs
fetch(`https://api.example.com/data?api_key=${myKey}`);

// Right — header-based transport avoids most accidental logging exposure
fetch('https://api.example.com/data', { headers: { 'X-API-Key': myKey } });
```

---

## 🧠 Tricky Interview Question

```javascript
function requireApiKey(req, res, next) {
  const apiKey = req.headers['x-api-key'];
  const validKeys = ['sk_live_abc', 'sk_live_def'];

  if (validKeys.includes(apiKey)) {
    next();
  } else {
    res.status(401).json({ error: 'Invalid key' });
  }
}
```
This code "works" functionally, but what subtle security weakness does the `validKeys.includes(apiKey)` comparison have compared to a proper hashed lookup with constant-time comparison?

Answer: `Array.includes()` (and plain `===` string comparison generally) is NOT constant-time — JavaScript string comparison typically short-circuits as soon as it finds a mismatched character, meaning the comparison takes slightly LESS time for keys that mismatch EARLY versus ones that mismatch LATE (closer to a correct guess). This creates a theoretical **timing attack** vulnerability: an attacker measuring response times very precisely across many requests could statistically infer the key character-by-character, since correct-prefix guesses take marginally longer to reject. While practically quite hard to exploit over real network conditions (network jitter usually swamps the tiny timing signal), proper security-sensitive comparisons use a constant-time comparison function (like Node's `crypto.timingSafeEqual()`) specifically to eliminate this class of attack entirely, regardless of how difficult real-world exploitation might be — defense-in-depth against a theoretical but documented attack vector. This is also why hashing the key with SHA-256 then comparing the HASHES (fixed-length, via a DB index lookup) sidesteps the issue somewhat differently — the comparison still should ideally use a timing-safe method, but hash comparison in a DB lookup context is a less direct attack surface than raw string comparison in application code.

---

## ⚫ Interview Questions + Answers

Q1: What's the fundamental difference between API key authentication and JWT/OAuth-based authentication?
A1: API keys identify and authorize an APPLICATION/ACCOUNT (machine-to-machine), typically static (no built-in expiry, manually revoked), with no "login flow" — it's just a credential presented on every request. JWT/OAuth are designed around authenticating an individual USER through an interactive login/consent flow, with built-in claims (expiry, issuer) and often short-lived tokens with refresh mechanisms. API keys are simpler and better suited for server-to-server/developer integrations; JWT/OAuth suit human end-user authentication with richer identity/session semantics.

Q2: Why should API keys be stored as hashes in the database, similar to (but using a different method than) password hashing?
A2: If the database is ever breached, stored raw API keys would give an attacker immediate, fully usable credentials for every account — a catastrophic, instantly-exploitable leak. Hashing means the breach only exposes hash values, not usable keys (assuming the hash can't be reversed). UNLIKE passwords, API keys are already high-entropy, machine-generated random strings (not guessable human choices), so a FAST hash like SHA-256 is adequate (no need for bcrypt/argon2's deliberate slowness, which exists specifically to slow down brute-forcing LOW-entropy human passwords — brute-forcing a 192-bit random API key is computationally infeasible regardless of hash speed).

Q3: How would you implement API key scoping (e.g., "read-only" vs "full access" keys) for the same account?
A3: Store a `scopes` array (e.g., `['read']`, `['read', 'write']`) alongside each API key's record in the database, generated/assigned when the key is created. Authorization middleware then checks the AUTHENTICATED key's scopes against what the specific route/action requires (`requireScope('write')` as a separate authorization middleware layered after the authentication middleware) — mirroring the authentication-vs-authorization separation pattern, just applied to machine credentials instead of human user roles.

Q4: What's a key operational advantage of API keys over JWT for third-party developer integrations?
A4: Simplicity of revocation and management from the ISSUING PLATFORM's side — a developer dashboard can show "Active API Keys," let users regenerate/revoke individual keys instantly (immediate effect, since every request involves a DB lookup anyway, unlike stateless JWT), and track per-key usage/billing without any token refresh complexity. Developers integrating your API also appreciate the simplicity — no OAuth dance, no token expiry/refresh logic to implement; just attach a static header to every request.

Q5: Should you ever combine API key authentication with rate limiting, and why is per-key (rather than per-IP) rate limiting often more appropriate here?
A5: Yes — rate limiting by API key (rather than by IP) correctly attributes usage to the actual ACCOUNT/application making requests, which matters especially when multiple different client applications/servers might share an IP (e.g., behind a corporate NAT or cloud load balancer on the CALLING side) or when a single account's traffic legitimately comes from many different IPs (distributed server fleet). Keying rate limits by the API key itself (via `keyGenerator: (req) => req.headers['x-api-key']` in `express-rate-limit`) ensures fair, accurate enforcement aligned with your actual billing/usage tiers, independent of network topology quirks.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Server-to-server integrations, third-party developer API access, webhooks, CI/CD pipeline authentication
- Simple machine-identification needs where a full OAuth/login flow is unnecessary overhead
- Usage-based billing/rate-limiting tied to a specific application/account rather than an individual end-user

❌ Avoid when:
- Authenticating individual human end-users with personal data/permissions — use session/JWT-based auth with proper login flows instead
- You need fine-grained, frequently-changing per-action authorization tied to a specific person's identity rather than a whole application's static credential
- Extremely high-security contexts where a long-lived static credential (even hashed) presents more risk than short-lived, auto-rotating tokens would

---

## 📊 Visual Diagram
```
API KEY AUTHENTICATION FLOW:

  Developer signs up ──▶ Platform generates random key
                               │
                    sk_live_abc123xyz... (shown ONCE)
                               │
                    Platform stores HASH(key) in DB
                               │
                               ▼
  Developer's app ── every request ──▶ X-API-Key: sk_live_abc123xyz...
                               │
                               ▼
                    Server: hash incoming key, lookup in DB
                               │
                    ┌──────────┴───────────┐
                 found                  not found
                    │                       │
           identify account           401 Invalid key
                    │
           apply: scopes, tier, rate limits, usage logging
                    │
                    ▼
                 200 OK (request processed)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| API Key | Static credential identifying an app/account | App/account identify करने वाला static credential |
| X-API-Key | Common header name for sending the key | Key भेजने का common header name |
| Scope | Permission level granted to a key | Key को दिया गया permission level |
| Key rotation | Regenerating a key to replace an old one | पुरानी key replace करके नई generate करना |
| Timing attack | Inferring secrets via comparison time | Comparison time से secrets infer करना |
| Per-key rate limiting | Limiting requests by API key, not IP | IP नहीं, API key से requests limit करना |

---

## ⚡ 3-Line Summary
English:
1. API keys are static, long-lived credentials identifying an application/account for machine-to-machine or developer API access — simpler than OAuth/JWT for this use case.
2. Store hashed keys (not raw), transport via headers (not URL query params), and use constant-time comparison to avoid timing attacks.
3. Layer scopes and per-key rate limiting on top for fine-grained authorization and fair usage enforcement tied to billing tiers.

Hindi:
1. API keys static, long-lived credentials हैं जो application/account को identify करती हैं machine-to-machine या developer API access के लिए — इस use case के लिए OAuth/JWT से simpler।
2. Hashed keys store करो (raw नहीं), headers से transport करो (URL query params नहीं), और timing attacks से बचने के लिए constant-time comparison use करो।
3. Fine-grained authorization और billing tiers से जुड़े fair usage enforcement के लिए scopes और per-key rate limiting layer करो।

---

## ➡️ Next Topic
**129. CORS (Cross-Origin Resource Sharing)** — Controlling which origins can access your API from browser-based clients।
