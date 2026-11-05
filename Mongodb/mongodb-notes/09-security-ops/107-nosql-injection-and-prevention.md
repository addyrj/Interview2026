# 107. NoSQL Injection + Prevention
# हिंदी में: NoSQL Injection और उससे बचाव

---

## 🔵 Simple Definition (English)
**NoSQL injection** happens when attacker-controlled input is placed into a MongoDB query **as an object or operator** instead of as a plain value. Because Express parses JSON bodies and `?a[$ne]=1` query strings into objects, a client can send `{"pass": {"$ne": null}}` and the query `findOne({user, pass})` becomes "password is not null" -> always true. Related attacks abuse `$where`, `$regex`, `$expr` and server-side JavaScript. Prevention: **validate types, sanitize `$`-keys, never build queries from raw `req.body`, disable server JS, least privilege.**

## 🔵 सरल परिभाषा (Hindi)
**NoSQL injection** तब होता है जब attacker का input MongoDB query में plain value की जगह **object या operator** बनकर घुस जाता है। Express JSON body और `?a[$ne]=1` जैसी query strings को objects में parse करता है, इसलिए client `{"pass": {"$ne": null}}` भेज सकता है और `findOne({user, pass})` का मतलब बन जाता है "password null नहीं है" -> हमेशा true। इसी तरह `$where`, `$regex`, `$expr` और server-side JavaScript का भी दुरुपयोग होता है। बचाव: **types validate करो, `$`-keys sanitize करो, raw `req.body` से query मत बनाओ, server JS बंद करो, least privilege।**

---

## 🔴 Problem it Solves
Developers know SQL injection (string concatenation) and think "Mongo uses objects, so it is immune". It is not: the *structure* of the query is controlled by the JSON the client sends. A login endpoint that passes `req.body` straight into `findOne` can be bypassed without knowing any password, data can be enumerated character by character with `$regex`, and `$where` can run arbitrary JS (CPU DoS). Knowing the attack and the defences prevents account takeover and data leaks.

## 🔴 यह क्यों बना? (Hindi)
Developers SQL injection (string जोड़ना) जानते हैं और सोचते हैं "Mongo objects इस्तेमाल करता है तो safe है"। ऐसा नहीं है: query की *structure* client के भेजे JSON से तय होती है। जो login endpoint `req.body` सीधे `findOne` में डालता है उसे बिना password जाने bypass किया जा सकता है, `$regex` से data अक्षर-अक्षर निकाला जा सकता है, और `$where` से मनमाना JS चल सकता है (CPU DoS)। हमला और बचाव समझने से account takeover और data leak रुकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Server code: `users.findOne({ user: req.body.user, pass: req.body.pass })`.
Step 2 → Attacker sends `Content-Type: application/json` body `{"user":"admin","pass":{"$ne":null}}`.
Step 3 → Query becomes `{ user:"admin", pass:{ $ne:null } }` -> matches the admin document (any non-null password) -> login succeeds.
Step 4 → Variants: `{"$gt":""}` (any string), `{"$regex":"^a"}` (blind password guess), `{"$where":"sleep(5000)"}` (DoS), URL form `user[$ne]=x` via `qs` parser.
Step 5 → Defences: (a) **type-check** each field is a string; (b) **schema validation** (Zod/Joi/Mongoose strict + `sanitizeFilter`); (c) strip keys beginning with `$` or containing `.`; (d) hash passwords with bcrypt and compare in code, never in the query; (e) disable JS (`javascriptEnabled:false`); (f) least-privilege DB user.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Server code: `users.findOne({ user: req.body.user, pass: req.body.pass })`।
Step 2 → Attacker JSON body भेजता है `{"user":"admin","pass":{"$ne":null}}`।
Step 3 → Query बन जाती है `{ user:"admin", pass:{ $ne:null } }` -> admin document match -> login सफल।
Step 4 → Variants: `{"$gt":""}`, `{"$regex":"^a"}` (blind guess), `{"$where":"sleep(5000)"}` (DoS), URL में `user[$ne]=x`।
Step 5 → बचाव: (a) हर field का **type string** जाँचो; (b) **schema validation** (Zod/Joi/Mongoose `sanitizeFilter`); (c) `$` या `.` वाली keys हटाओ; (d) bcrypt से password hash और compare code में, query में नहीं; (e) JS बंद; (f) least-privilege user।

---

## 🟡 Real World Example
A **Flipkart**-like seller portal has `/login`. The handler does `Seller.findOne({ email: req.body.email, password: req.body.password })`. A pentester posts `{"email":{"$gt":""},"password":{"$gt":""}}` and logs in as the first seller in the collection. After the fix the handler validates with Zod (`z.string().email()`), looks up by email only, then does `bcrypt.compare(password, seller.hash)` — objects are rejected with 400 and the bypass fails.

## 🟡 Real Example Hindi mein
**Flipkart** जैसे seller portal में `/login` है। Handler `Seller.findOne({ email: req.body.email, password: req.body.password })` करता है। Pentester `{"email":{"$gt":""},"password":{"$gt":""}}` भेजकर collection के पहले seller के रूप में login कर लेता है। Fix के बाद handler Zod (`z.string().email()`) से validate करता है, सिर्फ email से lookup करता है, फिर `bcrypt.compare(password, seller.hash)` — objects पर 400 आता है और bypass fail हो जाता है।

---

## 💻 Code Example — Basic

```javascript
// inj.js — executed against mongod 8.0.4 on port 27131
const { MongoClient } = require('mongodb');
(async () => {
  const c = new MongoClient('mongodb://127.0.0.1:27131'); await c.connect();
  const u = c.db('sec').collection('users'); await u.deleteMany({});
  await u.insertOne({ user: 'admin', pass: 's3cret' });      // vulnerable demo data (plain text only for the demo!)

  const body = { user: 'admin', pass: { $ne: null } };       // what an attacker sends as JSON
  // VULNERABLE: raw values go straight into the filter
  console.log('attack:', await u.findOne({ user: body.user, pass: body.pass }).then(x => !!x));
  // Output: attack: true      <- logged in without the password

  // FIX 1: enforce that every value is a primitive string
  const safe = (v) => { if (typeof v !== 'string') throw new Error('must be string'); return v; };
  try { await u.findOne({ user: safe(body.user), pass: safe(body.pass) }); }
  catch (e) { console.log('blocked:', e.message); }
  // Output: blocked: must be string

  // $where runs JS on the server — attacker-supplied string would be code
  console.log('$where:', await u.find({ $where: "this.user=='admin' || '1'=='1'" }).toArray().then(r => r.length));
  // Output: $where: 1         <- condition rewritten by injection; disable with javascriptEnabled:false
  await c.close();
})();
```

## 💻 Code Example — Advanced

```javascript
// secure-login.js — layered prevention in Express + Mongoose
const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');
const { z } = require('zod');                   // runtime schema validation

// Mongoose >= 6: sanitizeFilter wraps any $-operator object in $eq automatically
mongoose.set('sanitizeFilter', true);

const User = mongoose.model('User', new mongoose.Schema({
  email: { type: String, required: true, unique: true }, // strict string type
  hash:  { type: String, required: true, select: false } // never return/expose hash
}));

const LoginSchema = z.object({
  email: z.string().email().max(100),           // object { $ne: null } fails here
  password: z.string().min(8).max(128),
}).strict();                                    // reject unknown keys

const app = express();
app.use(express.json({ limit: '10kb' }));

app.post('/login', async (req, res) => {
  const parsed = LoginSchema.safeParse(req.body); // step 1: validate types
  if (!parsed.success) return res.status(400).json({ error: 'Invalid input' });

  const { email, password } = parsed.data;
  // step 2: look up by email ONLY — password never enters the query
  const user = await User.findOne({ email }).select('+hash');
  // step 3: compare in application code with constant-time bcrypt
  const ok = user && await bcrypt.compare(password, user.hash);
  if (!ok) return res.status(401).json({ error: 'Bad credentials' }); // same message for both cases
  res.json({ ok: true });
});
```

```javascript
// Generic sanitizer for places where you must accept filters (e.g. search params)
function stripOperators(obj) {
  if (obj && typeof obj === 'object') {
    for (const k of Object.keys(obj)) {
      if (k.startsWith('$') || k.includes('.')) delete obj[k]; // remove operator / path keys
      else stripOperators(obj[k]);                              // recurse into nested objects
    }
  }
  return obj;
}
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Query-string variant: ?role[$ne]=admin is parsed by qs into { role: { $ne: 'admin' } }
app.get('/users', async (req, res) => {
  // Wrong: User.find(req.query)
  // Right: whitelist exactly the fields you allow, and coerce to String
  const filter = {};
  if (typeof req.query.role === 'string') filter.role = req.query.role;
  res.json(await User.find(filter).limit(50));
});
// Also acceptable: app.set('query parser', 'simple') to stop nested objects in query strings
// (Express 5 default is already 'simple'; Express 4 uses qs "extended").
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Passing `req.body` / `req.query` directly to a query
```javascript
// Wrong
User.findOne(req.body);
// Right
User.findOne({ email: String(req.body.email) });
```
❌ Mistake 2: Comparing passwords inside the query (`{ email, password }`).
✅ Correct: find by email, then `bcrypt.compare` in code. Also stops plain-text password storage.

❌ Mistake 3: Using `$where` with user text, or leaving JS enabled.
✅ Correct: use `$expr`/normal operators; set `javascriptEnabled: false`.

❌ Mistake 4: Unescaped user input in `$regex` (ReDoS / wildcard dumps).
```javascript
// Right: escape regex metacharacters first
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
products.find({ name: { $regex: '^' + esc(q), $options: 'i' } });
```

---

## 🧠 Tricky Interview Question
**Q:** Your login uses `findOne({ email, password })` with Mongoose models and the `password` field is typed `String` in the schema. Is it still injectable?

**Answer:** Partly protected, not fully. Mongoose **casts** values to the schema type, so `{ $ne: null }` for a `String` path is rejected as a cast error in many cases, but **query operators are allowed on typed paths** (`password: { $ne: null }` is a legitimate filter and is NOT cast away). Without `sanitizeFilter: true`, an attacker can still send `{ "$ne": "x" }`. Hence you need explicit validation (Zod), `sanitizeFilter`, and the better design of not querying by password at all. The native driver has no casting, so it is fully injectable.

---

## ⚫ Interview Questions + Answers

Q1: How is NoSQL injection different from SQL injection?
A1: SQL injection injects text that changes the query string; NoSQL injection injects **structure** (objects/operators like `$ne`, `$gt`, `$regex`, `$where`) via JSON or parsed query strings. Parameterisation does not exist in the same way, so type validation is the key defence.

Q2: What does `mongoose.set('sanitizeFilter', true)` do?
A2: It wraps any object value containing `$` operators in `$eq` so `{ pass: { $ne: null } }` becomes "pass equals the literal object" and matches nothing. Opt in to specific operators with `mongoose.trusted({ $gt: 5 })`.

Q3: Can `$regex` be abused?
A3: Yes: blind data extraction (`^a`, `^ab`…), and catastrophic regex backtracking (ReDoS). Escape user input and anchor patterns; use indexes with prefix regex.

Q4: Why disable server-side JavaScript?
A4: `$where`, `$function`, `$accumulator` and `mapReduce` run JS in the server: injection and CPU DoS risk. `security.javascriptEnabled: false`.

Q5: List the defence layers.
A5: Input validation/types, ORM sanitize, no raw body to queries, hashed passwords, JS disabled, least-privilege DB user, rate limiting, logging.

---

## 🔷 When to Use + When Not to Use
✅ Apply these defences when:
- Any endpoint takes JSON bodies, query strings or headers that reach a Mongo filter

✅ Extra care when:
- Search, login, password reset and admin filters

❌ Don't rely on:
- Client-side validation or "Mongoose will handle it" alone

---

## 📊 Visual Diagram
```
ATTACK                                   DEFENCE
────────────────────────────────         ─────────────────────────────────
POST /login                              POST /login
{"user":"admin",                         {"user":"admin","pass":{"$ne":null}}
 "pass":{"$ne":null}}                          │
        │                                      ▼
        ▼                                Zod: pass must be string  ──✗──▶ 400
findOne({user, pass})                          │ (valid)
        │                                      ▼
        ▼                                findOne({email}) ─▶ bcrypt.compare
pass != null  → TRUE  → logged in              │
                                               ▼
                                         401 if hash mismatch
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Injection | Input changes query structure | Input से query की बनावट बदलना |
| Operator injection | `$ne`, `$gt` sent as values | Values की जगह operators भेजना |
| sanitizeFilter | Mongoose wraps $ objects in $eq | $ objects को $eq में लपेटना |
| $where | JS expression run on server | Server पर चलने वाला JS |
| ReDoS | Regex that burns CPU | CPU खाने वाला regex |
| Validation | Check type/shape of input | Input का type/shape जाँचना |
| bcrypt | Slow password hash | Password का slow hash |

---

## ⚡ 3-Line Summary
English:
1. NoSQL injection sends operators like `{ "$ne": null }` as values so a filter becomes always-true.
2. Validate that inputs are plain strings, use `sanitizeFilter`, never pass `req.body` to queries, and compare password hashes in code.
3. Disable server-side JS, escape regex input and use least-privilege DB users.

Hindi:
1. NoSQL injection में `{ "$ne": null }` जैसे operators values बनकर भेजे जाते हैं और filter हमेशा true हो जाता है।
2. Inputs को plain string validate करो, `sanitizeFilter` इस्तेमाल करो, `req.body` सीधे query में मत दो, और password hash code में compare करो।
3. Server-side JS बंद करो, regex input escape करो और least-privilege DB users रखो।

---

## ➡️ Next Topic
**108. Backup and Restore (mongodump, mongorestore, snapshots)** — Protecting data from loss.
