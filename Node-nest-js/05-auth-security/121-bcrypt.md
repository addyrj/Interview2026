# 121. bcrypt — Password Hashing
# हिंदी में: bcrypt — Password Safely Store करो

---

## 🔵 Simple Definition (English)
**bcrypt** is a password hashing function designed specifically for passwords. Unlike MD5/SHA256 (fast hash functions), bcrypt is intentionally **slow** — making brute-force attacks expensive. It uses a **cost factor** (rounds) to tune how slow it is, and adds a **salt** automatically to protect against rainbow table attacks. The output is a 60-character string that includes the algorithm, cost, salt, and hash — all in one.

Key properties: **Adaptive** (increase cost as hardware gets faster), **Salt-included** (no need to store salt separately), **One-way** (cannot reverse the hash to get the password).

## 🔵 सरल परिभाषा (Hindi)
**bcrypt** एक password hashing function है जो specifically passwords के लिए बना है। MD5/SHA256 (fast hash functions) के विपरीत, bcrypt intentionally **slow** है — brute-force attacks को expensive बनाने के लिए। **Cost factor** (rounds) से tune करते हैं कितना slow हो, और **salt** automatically add करता है rainbow table attacks से बचाने के लिए। Output 60-character string जिसमें algorithm, cost, salt, hash सब included है।

---

## 🔴 Problem it Solves
```
WITHOUT BCRYPT (vulnerable):
  Storing plaintext password:
    users table: { email: 'rahul@ex.com', password: 'MyPass123' }
    DB leak → attacker has all passwords directly

  MD5/SHA256 (fast but wrong):
    hash('MyPass123') = '5baa61e4c...' (milliseconds)
    Attacker with GPU: 10 billion hashes/second
    Dictionary of 1M common passwords → crack all in < 1 second
    Rainbow tables: precomputed hash → password mapping

WITH BCRYPT:
  bcrypt('MyPass123', 12 rounds) = '$2b$12$K5Rq7tYJA2...LmNpQrSt...'
  Cost 12 rounds = ~300ms on modern hardware
  Attacker with GPU: ~33 attempts per second (from 10 billion!)
  Dictionary of 1M common passwords → 350 hours to crack one account
  Each password has unique salt → no rainbow tables possible
  
  If hardware doubles in speed → increase cost from 12 to 13 → back to 300ms
```

---

## 🟢 How bcrypt Works

```
BCRYPT ALGORITHM:
──────────────────────────────────────────────────────────

  Input: password 'MyPass123' + cost factor 12

  Step 1: Generate random salt (22 chars)
    salt = '$2b$12$K5Rq7tYJA2z8X9BcD3eF.'
              │    │  └── 22 chars of random salt
              │    └── cost factor (12 = 2^12 = 4096 iterations)
              └── algorithm version ($2b = bcrypt)

  Step 2: Run Blowfish cipher 2^12 = 4096 times
    Each round: EksBlowfishSetup(cost, salt, password)
    Takes ~300ms on modern CPU

  Step 3: Output (60 chars total):
    $2b$12$K5Rq7tYJA2z8X9BcD3eF.uW2mN4pQ7rS8tU1vX3yZ5aB6cD9eF0gH
    │───│ │─────────────────────│ │────────────────────────────────│
    algo  salt (22 chars)         hash (31 chars)

  VERIFICATION:
    bcrypt.compare('MyPass123', storedHash)
    → Extracts salt from storedHash
    → Runs same algorithm with extracted salt
    → Compares result with storedHash
    → Match = password correct ✅

  KEY PROPERTY:
    bcrypt.hash('MyPass123', 12) called twice → DIFFERENT hashes!
    (because random salt each time)
    But bcrypt.compare('MyPass123', hash) = true for both ✅
```

---

## 🟡 Real World Example
**PhonePe user registration + login:** 50 million users. Each user's password must be stored securely. If DB is leaked (like the 2021 Facebook leak of 530M records), attackers shouldn't get plaintext passwords. With bcrypt(12 rounds): each hash takes 300ms to generate (registration: acceptable one-time cost). For login: one compare takes 300ms (acceptable UX). For an attacker with 1000 GPU cores trying to crack one user's password: 300ms / 1000 = ~0.3ms per attempt... but still only 3333 attempts/second vs actual GPU speed of billions/second for MD5.

---

## 💻 Code Example — Basic

```javascript
// bcrypt-basics.js
const bcrypt = require('bcrypt');  // npm install bcrypt

// ─── 1. HASH A PASSWORD ───────────────────────────────────────────────────────
async function hashPassword(plainTextPassword) {
  const saltRounds = 12;  // cost factor
  // Higher = more secure but slower:
  // 10 rounds = ~65ms, 12 rounds = ~300ms, 14 rounds = ~1.2s
  // Recommendation: 12 for most apps, 10 for high-traffic login routes
  
  const hash = await bcrypt.hash(plainTextPassword, saltRounds);
  console.log('Hash:', hash);
  // $2b$12$K5Rq7tYJA2z8X9BcD3eF.uW2mN4pQ7rS8tU1vX3yZ5aB6cD9eF0gH
  return hash;
}

// ─── 2. VERIFY PASSWORD ───────────────────────────────────────────────────────
async function verifyPassword(plainText, hash) {
  const isMatch = await bcrypt.compare(plainText, hash);
  return isMatch;  // true if password matches
}

// ─── 3. IN EXPRESS: USER REGISTRATION ────────────────────────────────────────
const express = require('express');
const app = express();
app.use(express.json());

app.post('/register', async (req, res) => {
  const { email, password, name } = req.body;

  // Input validation
  if (!email || !password || password.length < 8) {
    return res.status(400).json({ error: 'Invalid input' });
  }

  try {
    // Check if user already exists
    const existing = await User.findOne({ email });
    if (existing) {
      return res.status(409).json({ error: 'Email already registered' });
    }

    // Hash password before storing
    const passwordHash = await bcrypt.hash(password, 12);
    // NEVER store the plain text 'password' — only 'passwordHash'

    const user = await User.create({
      email,
      name,
      passwordHash,  // ← only the hash goes into DB
    });

    res.status(201).json({
      message: 'Registered successfully',
      user: { id: user._id, email: user.email },
      // Never return passwordHash in response!
    });
  } catch (err) {
    res.status(500).json({ error: 'Registration failed' });
  }
});

// ─── 4. IN EXPRESS: USER LOGIN ────────────────────────────────────────────────
app.post('/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await User.findOne({ email });
    
    // SECURITY: same message whether email exists or password is wrong
    // Attacker should not know if an email is registered
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Compare with stored hash
    const isMatch = await bcrypt.compare(password, user.passwordHash);
    
    if (!isMatch) {
      return res.status(401).json({ error: 'Invalid credentials' });
      // Same message as above — don't say "password incorrect"
    }

    // Passwords match — generate JWT
    const token = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '15m' }
    );

    res.json({ token, user: { id: user._id, email: user.email } });
  } catch (err) {
    res.status(500).json({ error: 'Login failed' });
  }
});

app.listen(3000);
```

## 💻 Code Example — Advanced

```javascript
// advanced-bcrypt.js — Production patterns: pepper, migration, reset

const bcrypt = require('bcrypt');
const crypto = require('crypto');

// ─── 1. PEPPER (extra secret beyond salt) ────────────────────────────────────
// Salt: stored in hash, different per user, protects against rainbow tables
// Pepper: application-level secret, NOT stored in DB
// Even if DB is leaked, attacker needs the pepper to crack passwords

const PEPPER = process.env.PASSWORD_PEPPER;  // secret env var, min 32 chars

async function hashPasswordWithPepper(plainText) {
  // Combine password with pepper before hashing
  const pepperedPassword = `${plainText}${PEPPER}`;
  return bcrypt.hash(pepperedPassword, 12);
}

async function verifyPasswordWithPepper(plainText, hash) {
  const pepperedPassword = `${plainText}${PEPPER}`;
  return bcrypt.compare(pepperedPassword, hash);
}

// ─── 2. MIGRATE OLD MD5/SHA1 HASHES TO BCRYPT ────────────────────────────────
// Many legacy systems have MD5 or plain SHA1 passwords
// Migration strategy: verify old hash → re-hash with bcrypt on successful login

async function loginWithMigration(email, password) {
  const user = await User.findOne({ email });
  if (!user) return null;

  let isValid = false;
  let needsUpgrade = false;

  if (user.passwordType === 'bcrypt') {
    // Modern: verify with bcrypt
    isValid = await bcrypt.compare(password, user.passwordHash);
  } else if (user.passwordType === 'md5') {
    // Legacy: verify with MD5
    const md5Hash = crypto.createHash('md5').update(password).digest('hex');
    isValid = md5Hash === user.passwordHash;
    needsUpgrade = isValid;  // upgrade if login succeeds
  } else if (user.passwordType === 'sha1') {
    const sha1Hash = crypto.createHash('sha1').update(password).digest('hex');
    isValid = sha1Hash === user.passwordHash;
    needsUpgrade = isValid;
  }

  if (!isValid) return null;

  // On successful login with old hash → upgrade to bcrypt
  if (needsUpgrade) {
    const newHash = await bcrypt.hash(password, 12);
    await User.findByIdAndUpdate(user._id, {
      passwordHash: newHash,
      passwordType: 'bcrypt',
    });
    console.log(`Upgraded password hash for user ${user._id} to bcrypt`);
  }

  return user;
}

// ─── 3. PASSWORD RESET FLOW ───────────────────────────────────────────────────
async function requestPasswordReset(email) {
  const user = await User.findOne({ email });
  if (!user) return;  // don't reveal if email exists

  // Generate secure random token (NOT JWT — this is a one-time-use token)
  const resetToken = crypto.randomBytes(32).toString('hex');
  const resetTokenHash = crypto.createHash('sha256').update(resetToken).digest('hex');
  // Store hash in DB (not the token itself)
  // If DB leaks: resetTokenHash is useless without the original token

  await User.findByIdAndUpdate(user._id, {
    passwordResetToken: resetTokenHash,
    passwordResetExpires: new Date(Date.now() + 3600000),  // 1 hour
  });

  // Send email with raw token (not hash)
  const resetUrl = `https://myapp.com/reset-password?token=${resetToken}`;
  await emailService.send(email, 'Password Reset', `Reset your password: ${resetUrl}`);
}

async function resetPassword(rawToken, newPassword) {
  // Hash the received token to compare with DB
  const tokenHash = crypto.createHash('sha256').update(rawToken).digest('hex');

  const user = await User.findOne({
    passwordResetToken: tokenHash,
    passwordResetExpires: { $gt: new Date() },  // not expired
  });

  if (!user) throw new Error('Invalid or expired reset token');

  // Hash new password
  const passwordHash = await bcrypt.hash(newPassword, 12);

  // Update password and clear reset token
  await User.findByIdAndUpdate(user._id, {
    passwordHash,
    passwordResetToken: undefined,
    passwordResetExpires: undefined,
    $push: { passwordChangedAt: new Date() },  // audit trail
    // Optional: invalidate all JWTs by storing passwordChangedAt
    // and checking in JwtStrategy: if token.iat < user.passwordChangedAt → reject
  });

  // Invalidate all existing sessions
  await Session.deleteMany({ userId: user._id });
}

// ─── 4. BCRYPT TUNING ─────────────────────────────────────────────────────────
async function benchmarkBcrypt() {
  const password = 'TestPassword123';
  
  for (const rounds of [10, 11, 12, 13, 14]) {
    const start = Date.now();
    await bcrypt.hash(password, rounds);
    const ms = Date.now() - start;
    console.log(`Cost ${rounds}: ${ms}ms`);
  }
  // Cost 10: ~65ms
  // Cost 11: ~130ms
  // Cost 12: ~300ms
  // Cost 13: ~600ms
  // Cost 14: ~1200ms
  
  // Recommendation: choose cost where hashing takes ~200-300ms
  // Re-evaluate every 2-3 years as hardware improves
}
```

---

## 🟠 Express.js Integration

```javascript
// complete auth flow with bcrypt + JWT + Express

const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');

const app = express();
app.use(express.json());

// Rate limit login: 10 attempts per 15 minutes per IP
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  skipSuccessfulRequests: true,
  message: { error: 'Too many login attempts. Please wait 15 minutes.' },
});

// Rate limit registration: 5 per hour per IP
const registerLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: 5,
  message: { error: 'Too many accounts created from this IP.' },
});

// Registration
app.post('/auth/register', registerLimiter, async (req, res) => {
  const { email, password, name } = req.body;

  // Validate password strength
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
  if (!passwordRegex.test(password)) {
    return res.status(400).json({
      error: 'Password must be 8+ chars with uppercase, lowercase, number, special char'
    });
  }

  try {
    if (await User.findOne({ email })) {
      return res.status(409).json({ error: 'Email already in use' });
    }

    const passwordHash = await bcrypt.hash(password, 12);
    const user = await User.create({ email, name, passwordHash });

    const token = jwt.sign({ userId: user._id }, process.env.JWT_SECRET, { expiresIn: '15m' });
    res.status(201).json({ token, user: { id: user._id, email } });
  } catch (err) {
    res.status(500).json({ error: 'Registration failed' });
  }
});

// Login
app.post('/auth/login', loginLimiter, async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await User.findOne({ email });

    // Constant-time comparison: don't short-circuit
    // If user not found, still run bcrypt.compare (with dummy hash)
    // This prevents timing attacks (attacker can't tell if email exists by response time)
    const dummyHash = '$2b$12$invalidhashfortimingattackprotection00000000000000000';
    const passwordToCompare = user ? user.passwordHash : dummyHash;
    const isMatch = await bcrypt.compare(password, passwordToCompare);

    if (!user || !isMatch) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign({ userId: user._id, email }, process.env.JWT_SECRET, { expiresIn: '15m' });
    res.json({ token, user: { id: user._id, email } });
  } catch (err) {
    res.status(500).json({ error: 'Login failed' });
  }
});

// Change password
app.put('/auth/change-password', authenticate, async (req, res) => {
  const { currentPassword, newPassword } = req.body;
  
  const user = await User.findById(req.user.userId);
  const isMatch = await bcrypt.compare(currentPassword, user.passwordHash);
  
  if (!isMatch) {
    return res.status(401).json({ error: 'Current password incorrect' });
  }

  // Prevent reuse of same password
  const isSame = await bcrypt.compare(newPassword, user.passwordHash);
  if (isSame) {
    return res.status(400).json({ error: 'New password must be different from current' });
  }

  user.passwordHash = await bcrypt.hash(newPassword, 12);
  await user.save();
  
  res.json({ message: 'Password changed. All other sessions revoked.' });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using MD5 or SHA256 for passwords
```javascript
// WRONG: Fast hashes — easily crackable
const hash = crypto.createHash('md5').update(password).digest('hex');
// GPU: 10 billion MD5/second → all 6-char passwords cracked in seconds

// CORRECT: bcrypt, scrypt, or argon2
const hash = await bcrypt.hash(password, 12);  // ~300ms per hash
```

❌ **Mistake 2:** Not handling timing attacks
```javascript
// WRONG: Different response time reveals if email exists
const user = await User.findOne({ email });
if (!user) {
  return res.status(401).json({ error: 'User not found' });  // fast response
}
const isMatch = await bcrypt.compare(password, user.passwordHash);  // slow
if (!isMatch) {
  return res.status(401).json({ error: 'Wrong password' });  // slow response
}
// Attacker: timing difference reveals if email exists!

// CORRECT: Always run bcrypt.compare (same timing for any email)
const user = await User.findOne({ email });
const dummyHash = '$2b$12$dummyhashfortimingattackprotection0000000000000';
const hash = user?.passwordHash || dummyHash;
const isMatch = await bcrypt.compare(password, hash);
if (!user || !isMatch) {
  return res.status(401).json({ error: 'Invalid credentials' });
}
```

❌ **Mistake 3:** Too low cost factor
```javascript
// WRONG: cost 5-6 is too fast — barely better than SHA256
const hash = await bcrypt.hash(password, 6);  // ~5ms — too fast!

// CORRECT: minimum 10, prefer 12
const hash = await bcrypt.hash(password, 12);  // ~300ms — good balance
```

---

## 🧠 Tricky Interview Question

**Q: Why does `bcrypt.hash('password', 12)` return a different value each time, but `bcrypt.compare('password', hash)` still returns true?**

**Answer:** Each call to `bcrypt.hash()` generates a new random **salt** (22 random characters). The salt is embedded in the hash output: `$2b$12$<22-char-salt><31-char-hash>`. Two calls produce different outputs because the salts differ. When `bcrypt.compare('password', storedHash)` is called: (1) it extracts the salt from the `storedHash` (first 29 chars), (2) runs the bcrypt algorithm with `password` + that exact salt + cost factor, (3) compares the result with the hash portion of `storedHash`. Because we use the same salt, we get the same hash. This is why you NEVER need to store the salt separately — it's embedded in the hash output.

---

## ⚫ Interview Questions + Answers

**Q1: Why is bcrypt preferred over SHA256 for passwords?**
A1: SHA256 is designed for speed — billions of hashes per second on GPU hardware, making brute-force feasible. bcrypt is designed to be slow: cost factor 12 = ~300ms per hash, limiting brute-force to ~3 hashes/second per core. Key bcrypt advantages: (1) **Adaptive**: increase cost factor as hardware improves — SHA256 can't tune this. (2) **Built-in salting**: each hash gets a unique random salt automatically, preventing rainbow table attacks. SHA256 requires separate salt storage. (3) **Purpose-built**: specifically designed for password storage, not general-purpose hashing.

**Q2: What is a salt in bcrypt and why is it important?**
A2: A salt is a random string added to the password before hashing. bcrypt generates a new 22-character random salt automatically each time `bcrypt.hash()` is called, and embeds it in the output hash. Importance: (1) **Prevents rainbow tables**: precomputed hash→password mappings are useless because each password has a unique salt. (2) **Prevents duplicate detection**: two users with same password `'hello'` get different hashes (different salts). Without salt, identical passwords = identical hashes → easy to identify. The salt is stored IN the bcrypt output — you don't need a separate column.

**Q3: What is the cost factor in bcrypt and how do you choose it?**
A3: The cost factor (rounds) `N` means bcrypt runs `2^N` iterations. Cost 12 = 4096 iterations, takes ~300ms. Cost 13 = 8192 iterations, ~600ms. Rule: choose cost where hashing takes 200-300ms on your hardware — slow enough to resist brute force, fast enough for acceptable UX. Start with 12, benchmark with `bcrypt.hash(password, rounds)` on your production server. Increase every 2-3 years as hardware improves. For very high-traffic auth (millions of logins/day): cost 10 (~65ms) may be more practical — still much better than fast hashes.

**Q4: What is the difference between bcrypt, scrypt, and argon2?**
A4: All three are designed for password hashing with tunable slowness. **bcrypt**: oldest (1999), most battle-tested, good default choice, max input length ~72 chars (passwords longer are silently truncated!). **scrypt**: memory-hard (requires lots of RAM too), harder to parallelize on GPU/ASIC. **argon2**: winner of the Password Hashing Competition (2015), modern recommendation, 3 variants (Argon2i for password hashing, Argon2d for cryptography, Argon2id for general use). Argon2 > scrypt > bcrypt in theoretical security, but bcrypt is proven in production for 25 years.

**Q5: How do you protect against timing attacks in login?**
A5: Timing attack: measuring response time reveals if an email exists (no user found = fast response, wrong password = slow bcrypt compare). Fix: always run `bcrypt.compare()` regardless of whether user exists. Use a dummy hash for non-existent users: `const hash = user?.passwordHash || dummyBcryptHash`. This ensures consistent response time. Also: (1) Use same error message for "user not found" and "wrong password": `'Invalid credentials'`. (2) Add slight random jitter to response time (`Math.random() * 50` ms) to further obscure timing. (3) Rate limiting (10 attempts/15 min) limits brute-force regardless.

---

## 📊 Visual Diagram

```
BCRYPT HASH STRUCTURE:
──────────────────────────────────────────────────────────────────

  $2b$12$K5Rq7tYJA2z8X9BcD3eF.uW2mN4pQ7rS8tU1vX3yZ5aB6cD9eF0gH
  │──│ │─│ │─────────────────────│ │────────────────────────────│
   ↑   ↑        ↑                           ↑
  algo cost   salt (22 chars)          hash (31 chars)
  ($2b) (12)

PASSWORD VERIFICATION:
  User enters: 'MyPass123'
       │
       ▼
  Extract from stored hash:
    salt = 'K5Rq7tYJA2z8X9BcD3eF.'
    cost = 12
       │
       ▼
  Run: bcrypt(salt + 'MyPass123', 2^12 iterations)
       │
       ▼
  Compare result with stored hash portion
    Match? → ✅ Login success
    No match? → ❌ Wrong password

BRUTE FORCE COMPARISON:
  Algorithm  │ Speed on GPU  │ 1M password dict │ Time to crack
  ───────────┼───────────────┼──────────────────┼──────────────
  MD5        │ 10B/sec       │ 1M hashes        │ < 1ms
  SHA256     │ 3B/sec        │ 1M hashes        │ < 1ms
  bcrypt 12  │ ~3/sec        │ 1M hashes        │ ~4 days
  bcrypt 14  │ ~0.7/sec      │ 1M hashes        │ ~16 days
  argon2id   │ ~0.1/sec      │ 1M hashes        │ ~115 days
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Password hashing | One-way transform of password | Password का one-way transform |
| Salt | Random value added before hashing | Hash से पहले add होने वाला random value |
| Cost factor | Number of iterations (2^N) | Iterations की count (2^N) |
| Rainbow table | Precomputed hash→password map | Precomputed hashes का database |
| Brute force | Try all possible passwords | सभी possible passwords try करना |
| Timing attack | Measure response time for info | Response time से information निकालना |
| Pepper | App-level secret added to password | App-level secret password में add |
| bcrypt.compare | Verify password against hash | Hash के against password verify |

---

## ⚡ 3-Line Summary
**English:**
1. bcrypt is intentionally slow (cost 12 = ~300ms) with automatic random salt per hash — making brute-force and rainbow table attacks infeasible for password storage.
2. Always use `bcrypt.hash(password, 12)` on registration, `bcrypt.compare(input, storedHash)` on login — never store plaintext or use MD5/SHA256 for passwords.
3. Production must-haves: rate limit login (10 attempts/15 min), constant-time comparison (dummy hash if user not found), same error message for wrong email/password.

**Hindi:**
1. bcrypt intentionally slow है (cost 12 = ~300ms), automatic random salt — brute-force और rainbow table attacks infeasible।
2. Registration पर `bcrypt.hash(password, 12)`, login पर `bcrypt.compare(input, hash)` — कभी plaintext store मत करो।
3. Production: rate limit, constant-time comparison (user न हो तो dummy hash), same error message।

---

## ➡️ Next Topic
**122. Passport.js** — Authentication strategies: Local, JWT, OAuth Google/GitHub।
