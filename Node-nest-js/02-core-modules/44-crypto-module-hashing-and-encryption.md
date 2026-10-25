# 44. crypto Module — Hashing + Encryption
# हिंदी में: crypto Module — Hashing और Encryption

---

## 🔵 Simple Definition (English)
The **`crypto`** module (`require('crypto')`) provides cryptographic functionality: **hashing** (one-way, e.g. SHA-256 for checksums), **HMAC** (keyed hash for message authentication), **password hashing** (bcrypt-style salted hashes via `pbkdf2`/`scrypt`), and **symmetric/asymmetric encryption** (AES, RSA). It wraps OpenSSL, so it's fast and battle-tested — you should never write your own crypto algorithm.

## 🔵 सरल परिभाषा (Hindi)
**`crypto`** module cryptographic functionality देता है: **hashing** (one-way, जैसे SHA-256 checksum के लिए), **HMAC** (keyed hash, message authentication के लिए), **password hashing** (salted hashes `pbkdf2`/`scrypt` से), और **encryption** (AES, RSA)। यह OpenSSL को wrap करता है — fast और battle-tested है, अपना crypto algorithm कभी मत लिखो।

---

## 🔴 Problem it Solves
Storing passwords in plain text is catastrophic (if the DB leaks, every account is compromised). Using a fast hash like MD5/SHA-1 alone is also broken — attackers precompute rainbow tables or brute-force with GPUs in seconds. Sending sensitive data (card numbers, PII) over the wire or storing it at rest needs real encryption, not "security by obscurity". Before `crypto`, developers used shaky custom encoding or weak hashing — leading to breaches. Node's `crypto` module gives access to proven, audited algorithms (bcrypt/scrypt-style KDFs, AES-256-GCM) directly from OpenSSL.

## 🔴 यह क्यों बना? (Hindi)
Passwords को plain text में store करना disaster है — DB leak होने पर सभी accounts compromise हो जाते हैं। सिर्फ MD5/SHA-1 जैसा fast hash use करना भी weak है — attackers rainbow tables या GPU brute-force से सेकंडों में तोड़ देते हैं। Sensitive data (card numbers, PII) को wire पर भेजने या store करने के लिए real encryption चाहिए। `crypto` module proven, audited algorithms (scrypt-style KDFs, AES-256-GCM) सीधे OpenSSL से देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Hashing**: `crypto.createHash('sha256').update(data).digest('hex')` — one-way, same input always gives same output, can't be reversed.
Step 2 → **HMAC**: `crypto.createHmac('sha256', secretKey).update(data).digest('hex')` — hash + secret key, used to verify message wasn't tampered (e.g. webhook signatures from Razorpay/Stripe).
Step 3 → **Password hashing**: `crypto.scrypt(password, salt, 64, callback)` — slow, memory-hard function designed to resist brute-force; each password gets a unique random salt.
Step 4 → **Symmetric encryption**: `crypto.createCipheriv('aes-256-gcm', key, iv)` encrypts; `createDecipheriv` with same key+iv decrypts. Same key both ways — fast, used for data at rest.
Step 5 → **Random values**: `crypto.randomBytes(32)` generates cryptographically secure random bytes — used for salts, IVs, tokens, session IDs (never use `Math.random()` for security).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Hashing**: `createHash('sha256')` — one-way, same input से same output, reverse नहीं हो सकता।
Step 2 → **HMAC**: hash + secret key — message tamper check के लिए (जैसे Razorpay/Stripe webhook signatures)।
Step 3 → **Password hashing**: `crypto.scrypt()` — slow, memory-hard function जो brute-force रोकता है; हर password का unique random salt होता है।
Step 4 → **Symmetric encryption**: `createCipheriv`/`createDecipheriv` same key+IV से encrypt/decrypt करते हैं — data at rest के लिए।
Step 5 → **Random values**: `crypto.randomBytes()` cryptographically secure random bytes देता है — salts, IVs, tokens के लिए (`Math.random()` कभी security में मत use करो)।

---

## 🟡 Real World Example
**Razorpay webhook verification:** When a payment completes, Razorpay sends a webhook POST to your server with an `X-Razorpay-Signature` header. Your server computes `crypto.createHmac('sha256', webhookSecret).update(rawBody).digest('hex')` and compares it to the header using a constant-time comparison (`crypto.timingSafeEqual`). If they match, the webhook is genuinely from Razorpay (not a spoofed request) — this is how every payment gateway (Stripe, Paytm, PhonePe) secures webhooks.

## 🟡 Real Example Hindi mein
**Razorpay webhook verification:** Payment complete होने पर Razorpay आपके server को webhook भेजता है `X-Razorpay-Signature` header के साथ। Server `crypto.createHmac()` से signature compute करता है और header से `timingSafeEqual` से compare करता है। Match होने पर request genuine है (spoofed नहीं) — यही तरीका हर payment gateway webhook security में use करता है।

---

## 💻 Code Example — Basic
```javascript
// crypto-basics.js
const crypto = require('crypto');

// 1. SHA-256 HASH (one-way, for checksums/fingerprints -- NOT for passwords alone)
const hash = crypto.createHash('sha256').update('hello world').digest('hex');
console.log('SHA-256:', hash);
// Same input always -> same hash (deterministic)

// 2. HMAC (hash + secret key -- for verifying message integrity/authenticity)
const secret = 'webhook-secret-key';
const hmac = crypto.createHmac('sha256', secret).update('payment_success_12345').digest('hex');
console.log('HMAC:', hmac);

// 3. Secure random bytes (for tokens, salts, IVs -- NEVER use Math.random() here)
const randomToken = crypto.randomBytes(16).toString('hex'); // 32 hex chars
console.log('Random token:', randomToken);

// 4. Password hashing with scrypt (built-in, memory-hard, brute-force resistant)
const password = 'myS3curePass!';
const salt = crypto.randomBytes(16).toString('hex'); // unique salt per user

crypto.scrypt(password, salt, 64, (err, derivedKey) => {
  if (err) throw err;
  const hashedPassword = derivedKey.toString('hex');
  console.log('Hashed password:', hashedPassword);
  console.log('Salt (store alongside hash):', salt);
});
```

## 💻 Code Example — Advanced
```javascript
// crypto-advanced.js -- production patterns: password auth + AES encryption + webhook verification
const crypto = require('crypto');
const { promisify } = require('util');
const scryptAsync = promisify(crypto.scrypt);

// ─── 1. PASSWORD HASHING + VERIFICATION (register/login flow) ────────────────
async function hashPassword(plainPassword) {
  const salt = crypto.randomBytes(16).toString('hex');
  const derivedKey = await scryptAsync(plainPassword, salt, 64);
  return `${salt}:${derivedKey.toString('hex')}`; // store "salt:hash" in DB
}

async function verifyPassword(plainPassword, storedValue) {
  const [salt, storedHash] = storedValue.split(':');
  const derivedKey = await scryptAsync(plainPassword, salt, 64);
  const computedHash = derivedKey.toString('hex');
  // timingSafeEqual prevents timing attacks (comparing byte-by-byte with early exit leaks info)
  return crypto.timingSafeEqual(Buffer.from(storedHash, 'hex'), Buffer.from(computedHash, 'hex'));
}

// ─── 2. AES-256-GCM ENCRYPTION (encrypt sensitive data at rest, e.g. PAN card number) ─
function encrypt(text, keyHex) {
  const key = Buffer.from(keyHex, 'hex');           // 32-byte (256-bit) key
  const iv = crypto.randomBytes(12);                 // 12-byte IV recommended for GCM
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  const authTag = cipher.getAuthTag();                // GCM gives integrity tag -- detects tampering
  return { encrypted, iv: iv.toString('hex'), authTag: authTag.toString('hex') };
}

function decrypt({ encrypted, iv, authTag }, keyHex) {
  const key = Buffer.from(keyHex, 'hex');
  const decipher = crypto.createDecipheriv('aes-256-gcm', key, Buffer.from(iv, 'hex'));
  decipher.setAuthTag(Buffer.from(authTag, 'hex'));   // verify integrity before decrypting
  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');                 // throws if tampered/wrong key
  return decrypted;
}

// ─── 3. WEBHOOK SIGNATURE VERIFICATION (Razorpay-style) ───────────────────────
function verifyWebhookSignature(rawBody, signatureHeader, webhookSecret) {
  const expectedSignature = crypto
    .createHmac('sha256', webhookSecret)
    .update(rawBody)
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(expectedSignature, 'utf8'),
    Buffer.from(signatureHeader, 'utf8')
  );
}

// ─── DEMO ──────────────────────────────────────────────────────────────────────
(async () => {
  const stored = await hashPassword('myS3curePass!');
  console.log('Login valid:', await verifyPassword('myS3curePass!', stored));   // true
  console.log('Login invalid:', await verifyPassword('wrongPass', stored));      // false

  const encKey = crypto.randomBytes(32).toString('hex'); // 256-bit key
  const enc = encrypt('4111-1111-1111-1111', encKey);
  console.log('Encrypted card:', enc);
  console.log('Decrypted card:', decrypt(enc, encKey));
})();
```

---

## 🟠 Express.js Integration
```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

// IMPORTANT: webhook routes need the RAW body (not JSON-parsed) to verify signatures correctly
app.use('/webhook/razorpay', express.raw({ type: 'application/json' }));
app.use(express.json()); // JSON parsing for all other routes

app.post('/webhook/razorpay', (req, res) => {
  const signature = req.headers['x-razorpay-signature'];
  const expected = crypto
    .createHmac('sha256', process.env.RAZORPAY_WEBHOOK_SECRET)
    .update(req.body) // raw Buffer, not parsed JSON
    .digest('hex');

  const isValid = crypto.timingSafeEqual(
    Buffer.from(expected, 'utf8'),
    Buffer.from(signature, 'utf8')
  );

  if (!isValid) {
    return res.status(400).json({ error: 'Invalid webhook signature' });
  }

  const event = JSON.parse(req.body.toString());
  console.log('Payment event verified:', event.event);
  res.json({ status: 'ok' });
});

// Register endpoint using scrypt password hashing
app.post('/register', express.json(), async (req, res) => {
  const { promisify } = require('util');
  const scryptAsync = promisify(crypto.scrypt);
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = (await scryptAsync(req.body.password, salt, 64)).toString('hex');
  // In real app: save `${salt}:${hash}` to database against user email
  res.json({ message: 'User registered', storedValue: `${salt}:${hash}` });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `Math.random()` for security-sensitive values (tokens, salts, session IDs)
```javascript
// Wrong -- Math.random() is predictable, not cryptographically secure
const sessionToken = Math.random().toString(36).substring(2);

// Right -- crypto.randomBytes() is cryptographically secure
const sessionToken = crypto.randomBytes(32).toString('hex');
```

❌ Mistake 2: Hashing passwords with fast hashes (MD5/SHA-256) without a slow KDF
```javascript
// Wrong -- SHA-256 is FAST, GPUs can brute-force billions of guesses/sec
const hash = crypto.createHash('sha256').update(password).digest('hex');

// Right -- scrypt/pbkdf2 are intentionally SLOW + memory-hard, resist brute-force
const hash = await promisify(crypto.scrypt)(password, salt, 64);
```

❌ Mistake 3: Comparing secrets/signatures with `===` instead of `timingSafeEqual`
```javascript
// Wrong -- regular comparison can leak timing information to attackers
if (receivedSignature === expectedSignature) { /* vulnerable to timing attack */ }

// Right -- constant-time comparison
if (crypto.timingSafeEqual(Buffer.from(receivedSignature), Buffer.from(expectedSignature))) { }
```

---

## 🧠 Tricky Interview Question
```javascript
const crypto = require('crypto');
const h1 = crypto.createHash('sha256').update('password123').digest('hex');
const h2 = crypto.createHash('sha256').update('password123').digest('hex');
console.log(h1 === h2);

const s1 = crypto.randomBytes(16).toString('hex');
const s2 = crypto.randomBytes(16).toString('hex');
console.log(s1 === s2);
```
Answer: `h1 === h2` → `true` — hashing is **deterministic**: the same input with the same algorithm always produces the same output (no randomness involved). `s1 === s2` → `false` (virtually always) — `randomBytes` generates cryptographically secure random data, so two calls produce different values. This is exactly why plain hashing of passwords is insecure without a per-user random **salt** — identical passwords produce identical hashes, letting attackers spot duplicate passwords across accounts; adding a unique salt per user breaks this pattern.

---

## ⚫ Interview Questions + Answers

Q1: Why shouldn't you hash passwords with a single SHA-256 call?
A1: SHA-256 is designed to be FAST (gigabytes/sec), which is great for checksums but terrible for passwords — attackers with GPUs/ASICs can try billions of password guesses per second against a leaked hash. Password hashing needs an intentionally SLOW, memory-hard function like `scrypt`, `pbkdf2`, or `bcrypt` (via npm) that costs attackers significant time/memory per guess, making brute-forcing impractical even with leaked hashes.

Q2: What's the difference between hashing and encryption?
A2: Hashing is one-way — you cannot recover the original input from a hash (used for passwords, checksums, integrity verification). Encryption is two-way — data encrypted with a key can be decrypted back to the original using the correct key (used for protecting data you need to read later, like card numbers, PII at rest, or data in transit).

Q3: What is HMAC and where is it used in real systems?
A3: HMAC (Hash-based Message Authentication Code) combines a hash function with a secret key to produce a signature that proves both data integrity (data wasn't altered) AND authenticity (sender knows the secret). Used in: webhook signature verification (Razorpay, Stripe, GitHub), JWT signing (`HS256` algorithm), API request signing (AWS Signature V4).

Q4: Why use a unique salt per user when hashing passwords?
A4: Without a salt, two users with the same password get identical hashes — letting an attacker who cracks one password instantly know everyone else's with that hash (and precomputed "rainbow tables" become effective). A unique random salt per user ensures identical passwords produce completely different hashes, forcing attackers to brute-force each password individually instead of once for all users.

Q5: What's the difference between symmetric (AES) and asymmetric (RSA) encryption, and when would you use each?
A5: Symmetric encryption (AES) uses the SAME key to encrypt and decrypt — fast, ideal for large data (encrypting a database field, a file). The challenge is securely sharing that key. Asymmetric encryption (RSA/ECC) uses a public key to encrypt and a private key to decrypt — slower, ideal for key exchange, digital signatures, and small payloads (e.g. HTTPS handshake uses RSA/ECC to securely exchange an AES session key, then uses AES for the actual data transfer — a hybrid approach used everywhere on the web).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Hashing passwords (with `scrypt`/`pbkdf2`, never raw SHA/MD5)
- Verifying webhook signatures (payment gateways, GitHub webhooks)
- Encrypting sensitive data at rest (PII, card numbers, tokens in DB)
- Generating secure random tokens, session IDs, API keys

❌ Avoid when:
- You need advanced password hashing with configurable cost factors — consider the well-audited `bcrypt` npm package (simpler API, battle-tested in production at scale)
- You're tempted to invent your own encryption scheme — always use standard algorithms via `crypto`, never roll your own

---

## 📊 Visual Diagram
```
HASHING (one-way):                    ENCRYPTION (two-way):
  "password123"                          "4111-1111-1111-1111"
       │ SHA-256/scrypt                        │ AES-256-GCM + key + IV
       ▼                                       ▼
  a94a8fe5ccb19...  (irreversible)        8f3e9a2b... (ciphertext)
                                                │ decrypt with same key+IV
                                                ▼
                                     "4111-1111-1111-1111" (original restored)

HMAC WEBHOOK VERIFICATION:
  Razorpay Server              Your Server
  ───────────────             ─────────────
  body + secret                body (raw) + secret
     │ HMAC-SHA256                 │ HMAC-SHA256
     ▼                             ▼
  signature A ──── sent in header ───►  signature B
                                   │
                            timingSafeEqual(A, B)?
                            ✓ match -> genuine webhook
                            ✗ mismatch -> reject (spoofed)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hash | One-way irreversible digest | One-way irreversible digest |
| HMAC | Keyed hash for authenticity | Secret key वाला hash |
| Salt | Random value added before hashing | Hashing से पहले का random value |
| scrypt/pbkdf2 | Slow, memory-hard password KDF | धीमा password hashing function |
| AES | Symmetric encryption algorithm | Symmetric encryption algorithm |
| IV (Initialization Vector) | Random value for encryption uniqueness | Encryption को unique बनाने वाला random value |
| timingSafeEqual | Constant-time comparison | Constant-time comparison (timing attack से बचाव) |
| randomBytes | Cryptographically secure random data | Cryptographically secure random data |

---

## ⚡ 3-Line Summary
English: `crypto` provides hashing (`createHash`), HMAC (`createHmac`), encryption (`createCipheriv`/`createDecipheriv`), and secure randomness (`randomBytes`) — all backed by OpenSSL. Always hash passwords with slow KDFs (`scrypt`/`pbkdf2`), never plain SHA/MD5. Use HMAC + `timingSafeEqual` for webhook/signature verification.

Hindi: `crypto` hashing, HMAC, encryption, और secure randomness देता है — सभी OpenSSL द्वारा powered। Passwords हमेशा slow KDFs (`scrypt`/`pbkdf2`) से hash करो, plain SHA/MD5 से नहीं। Webhook verification के लिए HMAC + `timingSafeEqual` use करो।

---

## ➡️ Next Topic
**45. events Module — EventEmitter** — the foundation of Node's event-driven architecture, used by streams, HTTP, and almost every async API.
