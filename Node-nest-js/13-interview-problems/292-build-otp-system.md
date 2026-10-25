# 292. Build OTP System
# हिंदी में: OTP System कैसे बनायें

---

## 🔵 Simple Definition (English)
An **OTP (One-Time Password) system** generates a short random code, sends it via SMS/email, stores it with an expiry (usually 5-10 min), and verifies it against user input — with strict rate limiting and attempt limits to prevent brute-force and spam abuse.

## 🔵 सरल परिभाषा (Hindi)
**OTP (One-Time Password) system** एक short random code generate करता है, SMS/email से भेजता है, expiry के साथ store करता है (आमतौर पर 5-10 मिनट), और user input से verify करता है — brute-force और spam abuse रोकने के लिए strict rate limiting और attempt limits के साथ।

---

## 🔴 Problem it Solves
Passwords get forgotten, reused, and phished. OTP provides a lightweight, phone/email-bound verification for login, signup, or sensitive actions (changing bank details) without requiring users to remember anything — but naive implementations are vulnerable to brute force (guessing a 4-digit OTP), replay, and SMS-bombing abuse if not rate-limited.

## 🔴 यह क्यों बना? (Hindi)
Passwords भूल जाते हैं, reuse होते हैं, phishing का शिकार बनते हैं। OTP एक lightweight, phone/email-bound verification देता है login, signup, या sensitive actions (bank details change) के लिए बिना कुछ याद रखे — लेकिन naive implementation brute force (4-digit OTP guess करना), replay, और SMS-bombing abuse के vulnerable होते हैं अगर rate-limit न किया जाए।

---

## 🟢 How it Works — Step by Step

Step 1 → User requests OTP for a phone/email → server checks rate limit (e.g., max 3 OTP requests per phone per 10 min).
Step 2 → Server generates a cryptographically random N-digit code, hashes it (never store OTP in plaintext, just like passwords), and stores `{phone, otpHash, expiresAt, attempts: 0}` in Redis with TTL = expiry.
Step 3 → Server sends the plaintext OTP via SMS/email provider (Twilio/SES).
Step 4 → User submits the OTP; server looks up the stored record, checks `expiresAt` and `attempts < maxAttempts`.
Step 5 → Server hashes the submitted OTP and compares to stored hash (timing-safe compare); on match → verified, delete the record (single-use). On mismatch → increment `attempts`, and lock out after too many failures.
Step 6 → On successful verification, issue a session/JWT or mark the action as authorized.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → User phone/email के लिए OTP request करता है → server rate limit check करता है (जैसे max 3 OTP requests प्रति phone 10 मिनट में)।
Step 2 → Server cryptographically random N-digit code बनाता है, hash करता है (OTP कभी plaintext में store नहीं, passwords जैसे), और `{phone, otpHash, expiresAt, attempts: 0}` Redis में TTL=expiry के साथ store करता है।
Step 3 → Server plaintext OTP SMS/email provider (Twilio/SES) से भेजता है।
Step 4 → User OTP submit करता है; server record lookup करता है, `expiresAt` और `attempts < maxAttempts` check करता है।
Step 5 → Server submitted OTP hash करके stored hash से compare (timing-safe) करता है; match होने पर → verified, record delete (single-use)। Mismatch पर → `attempts` increment, बहुत fail होने पर lockout।
Step 6 → Successful verification पर session/JWT issue होता है या action authorized mark होता है।

---

## 🟡 Real World Example
**Paytm login**: User enters phone number, taps "Send OTP". Paytm's backend rate-limits to prevent SMS-bombing, generates a 6-digit OTP, stores a hash in Redis with 5-minute TTL, sends via SMS gateway. User enters the code within the app; backend verifies, allows max 3 wrong attempts before forcing a fresh OTP request, and on success issues a session token — all designed so even if someone intercepts network traffic, they can't replay or brute-force the OTP within its short window.

## 🟡 Real Example Hindi mein
**Paytm login**: User phone number डालता है, "Send OTP" दबाता है। Paytm backend SMS-bombing रोकने के लिए rate-limit करता है, 6-digit OTP बनाता है, Redis में hash 5-minute TTL के साथ store करता है, SMS gateway से भेजता है। User app में code डालता है; backend verify करता है, max 3 गलत attempts के बाद नया OTP मांगता है, success पर session token issue करता है — design ऐसा कि network traffic intercept होने पर भी OTP replay या brute-force न हो सके short window में।

---

## 💻 Code Example — Basic

```javascript
// otp-basic.js
// In-memory OTP generation + verification (run: node otp-basic.js)
const crypto = require('crypto');

const otpStore = new Map(); // phone -> { otp, expiresAt, attempts }
const OTP_LENGTH = 6;
const OTP_TTL_MS = 5 * 60 * 1000; // 5 minutes
const MAX_ATTEMPTS = 3;

// Generate a cryptographically secure random N-digit OTP (not Math.random — predictable!)
function generateOtp(length = OTP_LENGTH) {
  const max = 10 ** length;
  const randomNum = crypto.randomInt(0, max); // crypto.randomInt is CSPRNG-based
  return String(randomNum).padStart(length, '0'); // pad so "007123" stays 6 digits
}

// Request OTP for a phone number
function requestOtp(phone) {
  const otp = generateOtp();
  otpStore.set(phone, { otp, expiresAt: Date.now() + OTP_TTL_MS, attempts: 0 });
  console.log(`[SMS to ${phone}] Your OTP is: ${otp}`); // in real app, call SMS provider here
  return true;
}

// Verify OTP submitted by user
function verifyOtp(phone, submittedOtp) {
  const record = otpStore.get(phone);
  if (!record) return { success: false, reason: 'No OTP requested' };
  if (Date.now() > record.expiresAt) {
    otpStore.delete(phone);
    return { success: false, reason: 'OTP expired' };
  }
  if (record.attempts >= MAX_ATTEMPTS) {
    otpStore.delete(phone);
    return { success: false, reason: 'Too many attempts, request a new OTP' };
  }

  record.attempts++;
  if (record.otp !== submittedOtp) {
    return { success: false, reason: `Incorrect OTP (${MAX_ATTEMPTS - record.attempts} attempts left)` };
  }

  otpStore.delete(phone); // single-use — delete after successful verification
  return { success: true };
}

// --- Demo ---
requestOtp('+919999999999');
console.log(verifyOtp('+919999999999', '000000')); // wrong guess
console.log(verifyOtp('+919999999999', '123456')); // another wrong guess (unless it matches real OTP above)
```

## 💻 Code Example — Advanced

```javascript
// otp-advanced.js
// Production-style OTP system: Redis storage, hashed OTP, rate limiting, Express-ready functions
// npm i ioredis
const crypto = require('crypto');
const Redis = require('ioredis');
const redis = new Redis();

const OTP_TTL_SEC = 300;           // 5 minutes
const MAX_ATTEMPTS = 3;
const MAX_REQUESTS_PER_WINDOW = 3; // rate limit: 3 OTP requests
const RATE_LIMIT_WINDOW_SEC = 600; // per 10 minutes

// Hash OTP before storing — never store plaintext OTP, same principle as passwords
function hashOtp(otp) {
  return crypto.createHash('sha256').update(otp).digest('hex');
}

// Rate-limit OTP requests per phone to prevent SMS-bombing abuse
async function checkRateLimit(phone) {
  const key = `otp:ratelimit:${phone}`;
  const count = await redis.incr(key);
  if (count === 1) await redis.expire(key, RATE_LIMIT_WINDOW_SEC); // set TTL only on first request
  return count <= MAX_REQUESTS_PER_WINDOW;
}

async function requestOtp(phone, smsProvider) {
  const allowed = await checkRateLimit(phone);
  if (!allowed) {
    throw new Error('Too many OTP requests. Please try again later.');
  }

  const otp = String(crypto.randomInt(100000, 999999)); // 6-digit, uniform range
  const key = `otp:${phone}`;

  // Store hash + attempts counter together, atomic TTL via Redis SET with EX
  await redis.set(key, JSON.stringify({ hash: hashOtp(otp), attempts: 0 }), 'EX', OTP_TTL_SEC);

  await smsProvider.send(phone, `Your verification code is ${otp}. Valid for 5 minutes.`);
  return { sent: true, expiresInSec: OTP_TTL_SEC };
}

async function verifyOtp(phone, submittedOtp) {
  const key = `otp:${phone}`;
  const raw = await redis.get(key);
  if (!raw) return { success: false, reason: 'OTP expired or not requested' };

  const record = JSON.parse(raw);
  if (record.attempts >= MAX_ATTEMPTS) {
    await redis.del(key);
    return { success: false, reason: 'Too many failed attempts' };
  }

  const submittedHash = hashOtp(submittedOtp);
  // Timing-safe comparison to prevent timing attacks revealing partial matches
  const match = submittedHash.length === record.hash.length &&
    crypto.timingSafeEqual(Buffer.from(submittedHash), Buffer.from(record.hash));

  if (!match) {
    record.attempts++;
    await redis.set(key, JSON.stringify(record), 'EX', OTP_TTL_SEC); // preserve remaining TTL approx
    return { success: false, reason: 'Incorrect OTP', attemptsLeft: MAX_ATTEMPTS - record.attempts };
  }

  await redis.del(key); // single-use enforcement
  return { success: true };
}

module.exports = { requestOtp, verifyOtp };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — OTP-based phone login flow
const express = require('express');
const { requestOtp, verifyOtp } = require('./otp-advanced');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());

// Fake SMS provider — replace with Twilio in production
const smsProvider = { send: (phone, msg) => console.log(`[SMS] ${phone}: ${msg}`) };

app.post('/auth/request-otp', async (req, res) => {
  const { phone } = req.body;
  if (!/^\+91[0-9]{10}$/.test(phone)) { // basic phone format validation
    return res.status(400).json({ error: 'Invalid phone number' });
  }
  try {
    const result = await requestOtp(phone, smsProvider);
    res.json(result);
  } catch (err) {
    res.status(429).json({ error: err.message }); // 429 = too many requests
  }
});

app.post('/auth/verify-otp', async (req, res) => {
  const { phone, otp } = req.body;
  const result = await verifyOtp(phone, otp);

  if (!result.success) {
    return res.status(400).json(result);
  }

  // Issue a session token on success
  const token = jwt.sign({ phone }, process.env.JWT_SECRET, { expiresIn: '7d' });
  res.json({ success: true, token });
});

app.listen(3000, () => console.log('OTP auth API on :3000'));
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `Math.random()` to generate OTPs
✅ Correct: Use `crypto.randomInt()` — `Math.random()` is not cryptographically secure and can be predicted

```javascript
// Wrong — predictable PRNG, exploitable
const otp = Math.floor(100000 + Math.random() * 900000);

// Right — CSPRNG, unpredictable
const otp = crypto.randomInt(100000, 999999);
```

❌ Mistake 2: No attempt limit — allows unlimited brute-force guessing of a 6-digit OTP
✅ Correct: Cap verification attempts (e.g., 3) and invalidate the OTP after exceeding it

```javascript
// Wrong — unlimited guesses, a bot can try all 1,000,000 combos
function verify(otp, submitted) { return otp === submitted; }

// Right — bounded attempts enforced server-side, tied to the stored record
if (record.attempts >= MAX_ATTEMPTS) return { success: false, reason: 'locked' };
```

---

## 🧠 Tricky Interview Question

```javascript
// Two requests happen in quick succession for the same phone:
await requestOtp('+919999999999', sms); // generates OTP "123456", stores in Redis
await requestOtp('+919999999999', sms); // generates OTP "654321", OVERWRITES the key
// User receives BOTH SMS messages but only the SECOND OTP is valid now.
verifyOtp('+919999999999', '123456'); // what happens?
```
Answer: It returns `{ success: false, reason: 'Incorrect OTP' }` (and burns an attempt) — because the second `requestOtp` call **overwrote** the Redis key with a new hash, invalidating the first OTP even though the user has a valid-looking SMS in hand. This is actually correct, expected behavior (only the latest OTP should ever be valid), but it's a common source of user confusion/support tickets ("I entered the right code!") when double-tapping "Resend OTP" — good UX disables the resend button for a cooldown period to avoid this.

---

## ⚫ Interview Questions + Answers

Q1: Why hash the OTP before storing it instead of storing it in plaintext?
A1: Defense in depth — if Redis/DB is compromised or logs leak, plaintext OTPs could be used within their validity window to hijack accounts. Hashing (even with a fast hash like SHA-256, since OTPs are short-lived and rate-limited, unlike passwords) prevents direct reuse from a data dump.

Q2: How do you prevent SMS-bombing (someone spamming OTP requests to a victim's phone)?
A2: Rate-limit OTP requests per phone number (e.g., max 3 per 10 minutes) AND per IP/device, use CAPTCHA on repeated requests, and consider exponential backoff between allowed requests (1st instant, 2nd after 30s, 3rd after 2min).

Q3: Should OTP verification be case-sensitive or allow leading zeros to be dropped?
A3: Always compare as exact strings with leading zeros preserved (`"007123"`, not `7123`) — store and compare as zero-padded strings, not numbers, to avoid `parseInt` stripping leading zeros and causing false negatives.

Q4: How do you handle OTP for email vs SMS differently?
A4: Same core logic (generate, hash, store, verify, rate-limit), but email delivery is typically slower/less reliable for time-sensitive OTP, so some systems use a longer TTL for email (10-15 min) vs SMS (5 min), and may offer a magic-link alternative for email instead of a numeric code.

Q5: How would you scale this across multiple server instances?
A5: Store OTP state in a shared store (Redis) rather than in-memory `Map`, as shown in the advanced example — this ensures any server instance handling the verify request sees the same state as the one that handled the request-OTP call, which is essential in a load-balanced multi-instance deployment.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Phone/email-based login or signup verification
- Step-up authentication for sensitive actions (changing password, large transactions)
- You want password-less, low-friction auth

❌ Avoid when:
- High-security contexts needing stronger 2FA (prefer TOTP apps/hardware keys — SMS OTP is vulnerable to SIM-swap attacks)
- Extremely high-frequency actions where OTP friction would hurt UX (use session-based auth instead)

---

## 📊 Visual Diagram
```
 Request OTP                          Verify OTP
 ┌───────────────┐                    ┌───────────────┐
 │ check rate-    │                    │ lookup Redis   │
 │ limit (Redis)  │                    │ key: otp:phone │
 └───────┬────────┘                    └───────┬────────┘
         ▼                                     ▼
 generate CSPRNG OTP                   expired? attempts>=max?
         ▼                                     ▼  no
 hash + store (TTL)                    compare hash (timing-safe)
         ▼                                     ▼
 send via SMS/Email provider           match → delete key, success
                                        no match → attempts++, fail
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CSPRNG | Cryptographically secure random generator | Cryptographically secure random generator |
| TTL | Expiry duration of OTP | OTP की expiry अवधि |
| Rate limiting | Capping request frequency | Request frequency सीमित करना |
| Single-use | Valid for exactly one successful verification | सिर्फ एक बार valid |
| Timing-safe compare | Comparison immune to timing attacks | Timing attack से सुरक्षित comparison |

---

## ⚡ 3-Line Summary
English: A secure OTP system generates CSPRNG codes, stores only their hash with a short TTL in a shared store like Redis, and enforces both request-level rate limiting and verification-attempt limits. Always treat OTP state as single-use and compare hashes with timing-safe equality.
Hindi: Secure OTP system CSPRNG codes generate करता है, सिर्फ hash को short TTL के साथ Redis जैसे shared store में रखता है, और request-level rate limiting + verification-attempt limits दोनों enforce करता है। OTP state को हमेशा single-use मानो और hash compare timing-safe तरीके से करो।

---

## ➡️ Next Topic
**293. Implement Event Emitter** — building your own pub/sub primitive from scratch to understand Node's `events` module internals.
