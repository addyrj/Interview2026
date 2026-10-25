# 122. bcrypt vs argon2
# हिंदी में: bcrypt vs argon2 — Password Hashing Algorithms की तुलना

---

## 🔵 Simple Definition (English)
**bcrypt** and **argon2** are both slow, salted password-hashing algorithms designed to resist brute-force attacks. **bcrypt** (1999) is battle-tested, widely supported, CPU-hard. **argon2** (2015, winner of the Password Hashing Competition) is newer, memory-hard (resistant to GPU/ASIC cracking), and configurable across three dimensions (time, memory, parallelism) — generally considered the stronger modern choice.

## 🔵 सरल परिभाषा (Hindi)
**bcrypt** और **argon2** दोनों slow, salted password-hashing algorithms हैं जो brute-force attacks resist करने के लिए design किए गए हैं। **bcrypt** (1999) battle-tested है, widely supported, CPU-hard। **argon2** (2015, Password Hashing Competition का winner) नया है, memory-hard (GPU/ASIC cracking resistant), और तीन dimensions में configurable (time, memory, parallelism) — generally stronger modern choice माना जाता है।

---

## 🔴 Problem it Solves
Storing passwords in plain text or with fast hashes (MD5, SHA-256) is dangerous — fast hashes can be brute-forced at billions of guesses per second using GPUs. bcrypt was created specifically to be SLOW (configurable cost factor), making brute-forcing computationally expensive. However, bcrypt is only CPU-hard — specialized hardware (GPUs, ASICs) can still parallelize attacks against it efficiently. argon2 was designed to ALSO require significant MEMORY per hash attempt, which GPUs/ASICs (optimized for raw compute, not memory bandwidth) handle far less efficiently, making it more resistant to modern cracking hardware.

## 🔴 यह क्यों बना? (Hindi)
Passwords को plain text या fast hashes (MD5, SHA-256) से store करना dangerous है — fast hashes को GPUs से billions of guesses per second पर brute-force किया जा सकता है। bcrypt specifically SLOW होने के लिए बनाया गया था (configurable cost factor), brute-forcing को computationally expensive बनाता है। लेकिन, bcrypt सिर्फ CPU-hard है — specialized hardware (GPUs, ASICs) अभी भी efficiently इसके against attacks parallelize कर सकते हैं। argon2 को भी significant MEMORY हर hash attempt के लिए require करने के लिए design किया गया, जो GPUs/ASICs (raw compute के लिए optimized, memory bandwidth नहीं) को बहुत कम efficiently handle करने देता है, modern cracking hardware के against ज़्यादा resistant बनाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **bcrypt**: generates a random salt, combines it with the password, runs it through the Blowfish-based cipher repeatedly (`2^cost` rounds, cost typically 10-12), producing a 60-character hash string that embeds the salt and cost factor.
Step 2 → **argon2**: generates a random salt, and runs a memory-hard function requiring a configurable amount of RAM (e.g., 64MB) and iterations, filling and shuffling that memory repeatedly — three variants exist: Argon2d (max GPU resistance, used for non-interactive contexts), Argon2i (resistant to side-channel attacks, used for password hashing), Argon2id (hybrid, RECOMMENDED default, used by most modern libraries).
Step 3 → Both store the salt + parameters WITHIN the final hash string, so verification doesn't need a separate salt lookup — `compare(plainPassword, storedHash)` extracts the salt/params and re-runs the same computation.
Step 4 → Verification re-runs the (slow) hashing process with the extracted salt and compares the result to the stored hash — any mismatch (even one character different in the password) fails.
Step 5 → As hardware gets faster over time, you increase bcrypt's `cost` factor or argon2's `memoryCost`/`timeCost` parameters to keep the computation appropriately "slow" relative to current attacker capabilities — both are designed to be tunable over time.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **bcrypt**: random salt generate करता है, password के साथ combine करता है, Blowfish-based cipher से repeatedly चलाता है (`2^cost` rounds, cost typically 10-12), 60-character hash string produce करता है जिसमें salt और cost factor embedded होते हैं।
Step 2 → **argon2**: random salt generate करता है, और एक memory-hard function चलाता है जिसे configurable amount of RAM चाहिए (जैसे 64MB) और iterations, उस memory को repeatedly fill और shuffle करता है — तीन variants हैं: Argon2d (max GPU resistance), Argon2i (side-channel resistant), Argon2id (hybrid, RECOMMENDED default)।
Step 3 → दोनों salt + parameters को final hash string के अंदर ही store करते हैं, तो verification को अलग salt lookup की ज़रूरत नहीं — `compare(plainPassword, storedHash)` salt/params extract करता है और same computation फिर से चलाता है।
Step 4 → Verification extracted salt के साथ (slow) hashing process फिर से चलाता है और result को stored hash से compare करता है; एक भी character password में अलग होने पर mismatch fail हो जाती है।
Step 5 → Hardware समय के साथ fast होता जाता है, इसलिए bcrypt का `cost` factor या argon2 के `memoryCost`/`timeCost` parameters बढ़ाते रहो current attacker capabilities के against appropriately "slow" रखने के लिए — दोनों समय के साथ tunable होने के लिए design किए गए हैं।

---

## 🟡 Real World Example
**CRED (Indian fintech app) credential storage:** Given CRED deals with sensitive financial data (credit card bills, payment info), their backend uses argon2id for password hashing rather than bcrypt — chosen specifically for its stronger resistance to GPU-accelerated cracking attempts, which is increasingly relevant as attackers rent cloud GPU clusters cheaply. The `memoryCost` parameter is tuned to require a non-trivial amount of RAM per hash attempt (e.g., 64MB), meaning an attacker trying to crack millions of leaked hashes in parallel would need proportionally massive RAM across all their parallel attempts — a far more expensive requirement than bcrypt's CPU-only cost, which GPUs handle more efficiently.

## 🟡 Real Example Hindi mein
**CRED (Indian fintech app) credential storage:** CRED sensitive financial data (credit card bills, payment info) handle करता है, इसलिए उनका backend password hashing के लिए bcrypt के बदले argon2id use करता है — specifically GPU-accelerated cracking attempts के against stronger resistance के लिए चुना गया, जो increasingly relevant है क्योंकि attackers cheaply cloud GPU clusters rent कर सकते हैं। `memoryCost` parameter tuned होता है हर hash attempt के लिए non-trivial RAM require करने के लिए (जैसे 64MB), मतलब millions leaked hashes parallel में crack करने की कोशिश करने वाले attacker को proportionally massive RAM चाहिए होगी सभी parallel attempts में — bcrypt के CPU-only cost से कहीं ज़्यादा expensive requirement, जिसे GPUs efficiently handle करते हैं।

---

## 💻 Code Example — Basic

```javascript
// bcrypt-vs-argon2-basic.js
const bcrypt = require('bcrypt'); // npm install bcrypt
const argon2 = require('argon2'); // npm install argon2

async function demoBcrypt() {
  const password = 'MySecureP@ss123';

  // bcrypt.hash: cost factor 12 means 2^12 = 4096 rounds of hashing
  const hash = await bcrypt.hash(password, 12);
  console.log('bcrypt hash:', hash); // e.g., $2b$12$N9qo8uLOickgx2ZMRZoMye...

  // Verification: compare plain password against stored hash
  const isMatch = await bcrypt.compare(password, hash);
  console.log('bcrypt match:', isMatch); // true

  const wrongMatch = await bcrypt.compare('wrongPassword', hash);
  console.log('bcrypt wrong password match:', wrongMatch); // false
}

async function demoArgon2() {
  const password = 'MySecureP@ss123';

  // argon2.hash: uses argon2id by default (recommended variant)
  const hash = await argon2.hash(password);
  console.log('argon2 hash:', hash); // e.g., $argon2id$v=19$m=65536,t=3,p=4$...

  const isMatch = await argon2.verify(hash, password);
  console.log('argon2 match:', isMatch); // true
}

demoBcrypt().then(demoArgon2);
```

## 💻 Code Example — Advanced

```javascript
// bcrypt-vs-argon2-advanced.js — Tuned configs + timing comparison + migration strategy
const bcrypt = require('bcrypt');
const argon2 = require('argon2');

// ─── 1. TUNED ARGON2 CONFIG — explicit memory/time/parallelism costs ─────────
async function hashWithArgon2(password) {
  return argon2.hash(password, {
    type: argon2.argon2id, // hybrid variant — resists both GPU and side-channel attacks
    memoryCost: 65536, // 64 MB of RAM required per hash attempt (in KiB)
    timeCost: 3, // number of iterations
    parallelism: 4, // number of threads
  });
}

// ─── 2. TUNED BCRYPT CONFIG ─────────────────────────────────────────────────────
async function hashWithBcrypt(password) {
  return bcrypt.hash(password, 12); // cost factor 12 — ~250ms per hash on modern hardware
}

// ─── 3. TIMING COMPARISON (illustrates the "deliberately slow" design) ───────
async function compareTiming() {
  const password = 'TestPassword123!';

  const bcryptStart = Date.now();
  await hashWithBcrypt(password);
  console.log(`bcrypt (cost 12): ${Date.now() - bcryptStart}ms`);

  const argon2Start = Date.now();
  await hashWithArgon2(password);
  console.log(`argon2id (64MB, t=3): ${Date.now() - argon2Start}ms`);
}

// ─── 4. MIGRATION STRATEGY — moving existing bcrypt hashes to argon2 gradually ──
// Common real-world scenario: legacy system used bcrypt, migrating to argon2
async function loginWithMigration(user, plainPassword) {
  if (user.passwordHash.startsWith('$2b$') || user.passwordHash.startsWith('$2a$')) {
    // Old bcrypt hash — verify with bcrypt
    const valid = await bcrypt.compare(plainPassword, user.passwordHash);
    if (valid) {
      // Successful login — opportunistically re-hash with argon2 and update DB
      user.passwordHash = await hashWithArgon2(plainPassword);
      await user.save(); // persist the upgraded hash (mock)
      console.log('Migrated user password hash from bcrypt to argon2');
    }
    return valid;
  }

  // New argon2 hash — verify with argon2
  return argon2.verify(user.passwordHash, plainPassword);
}

compareTiming();
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const argon2 = require('argon2');
const app = express();
app.use(express.json());

app.post('/register', async (req, res, next) => {
  try {
    const { email, password } = req.body;

    // Hash with argon2id for new user registrations
    const passwordHash = await argon2.hash(password, {
      type: argon2.argon2id,
      memoryCost: 65536,
      timeCost: 3,
      parallelism: 4,
    });

    const user = await User.create({ email, passwordHash }); // mock DB call
    res.status(201).json({ message: 'User registered', userId: user._id });
  } catch (err) {
    next(err);
  }
});

app.post('/login', async (req, res, next) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email });
    if (!user) return res.status(401).json({ error: 'Invalid credentials' });

    const isValid = await argon2.verify(user.passwordHash, password);
    if (!isValid) return res.status(401).json({ error: 'Invalid credentials' });

    res.json({ message: 'Login successful' });
  } catch (err) {
    next(err);
  }
});

app.listen(3000, () => console.log('Argon2-secured auth server running on port 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Treating bcrypt/argon2 hashing like a fast, synchronous operation and blocking the event loop
✅ Correct: Both are DELIBERATELY slow (that's the security feature) — always use the async versions (`bcrypt.hash()`, not `bcryptSync`) in a Node.js server to avoid blocking the event loop and stalling ALL other requests during hashing.

```javascript
// Wrong — synchronous hashing blocks the entire event loop for ~250ms+ per call
const hash = bcrypt.hashSync(password, 12); // freezes the whole server momentarily

// Right — async version doesn't block the event loop (uses a worker thread pool internally)
const hash = await bcrypt.hash(password, 12);
```

❌ Mistake 2: Using a cost factor/memory setting that's too low (fast) "for performance," undermining the whole point
✅ Correct: A cost factor of 4-6 (bcrypt) or minimal memory (argon2) hashes in milliseconds — fast for your server, but equally fast for an attacker's brute-force attempt. Balance cost against your server's acceptable latency, not against making login feel instant.

```javascript
// Wrong — cost factor 4 is crackable far too quickly with modern hardware
await bcrypt.hash(password, 4);

// Right — cost factor 10-12 is the current recommended minimum for bcrypt
await bcrypt.hash(password, 12);
```

---

## 🧠 Tricky Interview Question

```javascript
const bcrypt = require('bcrypt');

const hash1 = await bcrypt.hash('samePassword', 10);
const hash2 = await bcrypt.hash('samePassword', 10);

console.log(hash1 === hash2); // what does this print?
```
Why would two hashes of the IDENTICAL password with the IDENTICAL cost factor be different strings?

Answer: `false` — the two hashes are DIFFERENT, even though the password and cost factor are identical. This is because `bcrypt.hash()` generates a NEW RANDOM SALT every time it's called, and the salt is embedded directly in the output hash string. Different salts produce completely different hash outputs even for the same password+cost. This is intentional and crucial for security: if salts were reused/predictable, an attacker could precompute a "rainbow table" of hashes for common passwords and instantly look up matches across multiple leaked accounts sharing the same password. Random salting ensures each password hash must be attacked individually, even if two users happen to choose the exact same password — `bcrypt.compare(password, hash)` still correctly verifies matches because it extracts the embedded salt from `hash` and reapplies it during verification.

---

## ⚫ Interview Questions + Answers

Q1: What's the fundamental security advantage of argon2 over bcrypt?
A1: argon2 is MEMORY-HARD in addition to being CPU-slow — it requires a configurable, significant amount of RAM per hash computation (e.g., 64MB), which severely limits an attacker's ability to parallelize cracking attempts using GPUs or ASICs (hardware optimized for massive parallel compute but with limited memory per core). bcrypt is only CPU-hard, so GPUs — which have thousands of cores — can still crack bcrypt hashes in parallel far more efficiently than they can crack memory-hard argon2 hashes, where memory bandwidth becomes the bottleneck instead of raw compute.

Q2: Why can't you use a fast hash function like SHA-256 for password storage, even with salting?
A2: SHA-256 is designed to be FAST (useful for things like file integrity checks, blockchain), computing billions of hashes per second on modern GPUs even WITH salting. Salting prevents rainbow-table precomputation attacks but does nothing to slow down BRUTE-FORCE attempts against an individual password — an attacker can still try billions of password guesses per second against a salted SHA-256 hash. bcrypt/argon2 are deliberately slow (configurable rounds/memory), making even a billion-guess brute force attempt take impractically long.

Q3: What are the three argon2 variants (d, i, id) and when would you use each?
A3: **Argon2d** maximizes resistance against GPU cracking attacks but is vulnerable to side-channel timing attacks (suitable for non-interactive uses like cryptocurrency mining, not ideal for passwords). **Argon2i** is resistant to side-channel attacks but slightly less GPU-resistant (traditionally recommended for password hashing). **Argon2id** is a HYBRID combining both approaches, and is the RECOMMENDED default for password hashing in virtually all modern use cases — it's what the `argon2` npm package defaults to.

Q4: How do you handle increasing the hashing cost factor over time as hardware gets faster, for ALREADY-STORED password hashes?
A4: You can't retroactively "re-hash" a password you don't have in plain text (hashing is one-way). The standard approach is OPPORTUNISTIC rehashing: keep the old hash as-is until the user next logs in successfully (you have their plain password at that moment, briefly, during login) — then immediately re-hash with the new, stronger cost factor/algorithm and update the stored hash. Over time, as users log in, the password database naturally migrates to stronger settings without requiring a forced mass password reset.

Q5: Is bcrypt now considered "insecure" given argon2's advantages?
A5: No — bcrypt remains a solid, widely-trusted choice when properly configured (cost factor 10-12+) and is still recommended by many security guidelines (e.g., OWASP lists both as acceptable). It's "weaker" only in RELATIVE terms against highly resourced attackers using specialized GPU/ASIC clusters — for most applications, a properly-configured bcrypt is still extremely difficult to crack. argon2 is the newer, generally preferred choice for NEW systems, especially those at higher risk (fintech, healthcare), but migrating an existing well-configured bcrypt system isn't urgent — it's more "best current practice for new builds" than "bcrypt is broken."

---

## 🔷 When to Use + When Not to Use
✅ Use when (both apply to): any password storage scenario — never store plaintext or fast-hashed passwords
- **Prefer argon2** for new systems, especially high-value targets (fintech, healthcare) where resistance to GPU/ASIC cracking matters most
- **bcrypt is acceptable** for existing systems, simpler deployment requirements, or when ecosystem/library support strongly favors it (some older frameworks/tools only support bcrypt)

❌ Avoid when:
- Never use fast general-purpose hashes (MD5, SHA-1, SHA-256 alone) for password storage under any circumstances
- Don't use either for non-password use cases requiring FAST hashing (e.g., data integrity checksums, deduplication) — use SHA-256/SHA-3 for those; bcrypt/argon2's slowness is a feature for passwords, a bug for throughput-sensitive operations

---

## 📊 Visual Diagram
```
bcrypt vs argon2:

                    bcrypt                      argon2(id)
  ────────────────────────────────────────────────────────────────
  Hardness:         CPU-hard                    CPU + MEMORY-hard
  GPU resistance:   Moderate                    Strong
  Tunable params:   cost (rounds)               memoryCost, timeCost, parallelism
  Age:              1999 (battle-tested)         2015 (PHC winner, newer)
  Output example:   $2b$12$N9qo8uLOickgx2ZM...   $argon2id$v=19$m=65536,t=3,p=4$...
  Recommendation:   Acceptable, legacy-friendly  Preferred for new systems

CRACKING COST COMPARISON (conceptual):
  bcrypt:  GPU with 1000s of cores → each core cracks independently, fast parallel attempts
  argon2:  GPU cores starved for memory bandwidth → far fewer effective parallel attempts
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| bcrypt | CPU-hard salted password hashing algorithm | CPU-hard salted hashing algorithm |
| argon2 | Memory-hard password hashing algorithm | Memory-hard hashing algorithm |
| Salt | Random value mixed into password before hashing | Password में mix होने वाला random value |
| Cost factor | bcrypt's tunable work factor (rounds) | bcrypt का tunable work factor |
| memoryCost | argon2's RAM requirement per hash | argon2 की RAM requirement |
| Rainbow table | Precomputed hash lookup table attack | Precomputed hash lookup attack |
| Opportunistic rehashing | Upgrading hash strength on next login | Next login पर hash strength upgrade करना |

---

## ⚡ 3-Line Summary
English:
1. Both bcrypt and argon2 are deliberately slow, salted password-hashing algorithms resistant to brute-force attacks — never use fast hashes (MD5/SHA-256) for passwords.
2. argon2 additionally requires significant memory per hash attempt, making it more resistant to GPU/ASIC cracking than bcrypt's CPU-only slowness.
3. Prefer argon2id for new systems; bcrypt (cost 10-12+) remains acceptable for existing systems; use opportunistic rehashing to upgrade cost factors over time.

Hindi:
1. bcrypt और argon2 दोनों deliberately slow, salted password-hashing algorithms हैं brute-force attacks resistant — passwords के लिए कभी fast hashes (MD5/SHA-256) use मत करो।
2. argon2 additionally हर hash attempt के लिए significant memory require करता है, जो इसे bcrypt के CPU-only slowness से GPU/ASIC cracking के against ज़्यादा resistant बनाता है।
3. नए systems के लिए argon2id prefer करो; bcrypt (cost 10-12+) existing systems के लिए acceptable रहता है; समय के साथ cost factors upgrade करने के लिए opportunistic rehashing use करो।

---

## ➡️ Next Topic
**123. Passport.js — Complete Guide** — The standard Node.js authentication middleware supporting 500+ strategies।
