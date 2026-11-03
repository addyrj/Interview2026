# 46. TTL Indexes
# हिंदी में: TTL Indexes

---

## 🔵 Simple Definition (English)
A **TTL (Time To Live) index** is a single-field index on a **date** field with an `expireAfterSeconds` option. A background thread deletes documents automatically once `field + expireAfterSeconds` is in the past. Perfect for sessions, OTPs, caches and temporary logs. Deletion is **not instant**: the TTL monitor wakes up about **every 60 seconds**.

## 🔵 सरल परिभाषा (Hindi)
**TTL (Time To Live) index** एक **date** field पर single-field index है जिसमें `expireAfterSeconds` option होता है। जब `field + expireAfterSeconds` बीत जाता है, background thread document अपने-आप delete कर देता है। Sessions, OTPs, caches और temporary logs के लिए बढ़िया। Deletion **तुरंत नहीं** होता: TTL monitor लगभग **हर 60 सेकंड** में जागता है।

---

## 🔴 Problem it Solves
Temporary data piles up forever unless a cron job cleans it. Writing, scheduling and monitoring that job is extra work and risk. A TTL index delegates cleanup to the database with zero application code.

## 🔴 यह क्यों बना? (Hindi)
Temporary data हमेशा जमा होता रहता है जब तक cron job उसे साफ़ न करे। उस job को लिखना, schedule और monitor करना अतिरिक्त काम और जोखिम है। TTL index सफाई database को सौंप देता है, application code शून्य।

---

## 🟢 How it Works — Step by Step

Step 1 → Store a BSON **Date** (or array of Dates) in a field like `createdAt`. Strings and numbers are ignored by TTL.
Step 2 → `createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })` - documents expire 1 hour after `createdAt`.
Step 3 → A background TTL monitor thread runs every 60 seconds and deletes expired documents in batches; it is not exact and can lag if the server is busy.
Step 4 → Variation: set `expireAfterSeconds: 0` and store the **exact expiry time** in the field (`expireAt`) for per-document expiry.
Step 5 → Change the duration without rebuilding: `db.runCommand({ collMod: "sessions", index: { keyPattern: { createdAt: 1 }, expireAfterSeconds: 3600 } })` (verified).
Step 6 → Restrictions: single-field only (not compound), cannot be on `_id`, not on capped collections. On replica sets, deletes happen on the primary and replicate.
Step 7 → Documents are removed regardless of other indexes; do not use TTL for data you must keep.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `createdAt` जैसे field में BSON **Date** रखो। Strings और numbers को TTL ignore करता है।
Step 2 → `createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })` - `createdAt` के 1 घंटे बाद documents expire।
Step 3 → Background TTL monitor हर 60 सेकंड चलता है और expired documents batch में delete करता है; यह exact नहीं है और server busy हो तो देर हो सकती है।
Step 4 → Variation: `expireAfterSeconds: 0` रखो और field (`expireAt`) में **exact expiry time** रखो - per-document expiry।
Step 5 → बिना rebuild के duration बदलो: `collMod` command (verified)।
Step 6 → Restrictions: सिर्फ single-field (compound नहीं), `_id` पर नहीं, capped collections पर नहीं।
Step 7 → Documents हर हाल में हटते हैं; जो data रखना ज़रूरी है उस पर TTL मत लगाओ।

---

## 🟡 Real World Example
**Paytm / Razorpay** OTP verification: an `otps` collection stores `{ phone, code, createdAt }` with `expireAfterSeconds: 300`. After 5 minutes the OTP is gone automatically, so a leaked old OTP cannot be reused and the collection stays tiny. **Swiggy** login sessions use `expireAt` with `expireAfterSeconds: 0` so "remember me" sessions last 30 days while normal ones last a day.

## 🟡 Real Example Hindi mein
**Paytm / Razorpay** OTP verification: `otps` collection में `{ phone, code, createdAt }` और `expireAfterSeconds: 300`। 5 मिनट बाद OTP अपने-आप हट जाता है, इसलिए पुराना leaked OTP दोबारा use नहीं हो सकता और collection छोटा रहता है। **Swiggy** login sessions में `expireAt` और `expireAfterSeconds: 0` से "remember me" 30 दिन चलता है और normal session 1 दिन।

---

## 💻 Code Example — Basic

```javascript
// mongosh (verified on MongoDB 8.0.4)
use ttl_demo
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 5 })   // Output: 'createdAt_1'

db.sessions.insertOne({ u: 1, createdAt: new Date(Date.now() - 60000) })   // already 60 s old -> will expire
db.sessions.insertOne({ u: 2, createdAt: new Date() })                      // fresh
db.sessions.countDocuments()      // Output: 2   (immediately; TTL monitor has not run yet)
// After the next TTL pass (up to ~60 s later): u:1 is deleted, u:2 deleted ~5 s after its createdAt
// (the background pass timing was NOT observed here; behaviour is as documented)

db.sessions.getIndexes()[1]
// Output: { v: 2, key: { createdAt: 1 }, name: 'createdAt_1', expireAfterSeconds: 5 }
```

## 💻 Code Example — Advanced

```javascript
// Per-document expiry: expireAfterSeconds 0 + exact expiry date in the field
db.sessions.createIndex({ expireAt: 1 }, { expireAfterSeconds: 0 })
db.sessions.insertOne({ u: 3, expireAt: new Date(Date.now() + 30 * 24 * 3600 * 1000) })  // lives 30 days
db.sessions.insertOne({ u: 4, expireAt: new Date(Date.now() + 24 * 3600 * 1000) })       // lives 1 day

// Change TTL on an existing index without dropping it
db.runCommand({
  collMod: "sessions",
  index: { keyPattern: { createdAt: 1 }, expireAfterSeconds: 3600 }
})
db.sessions.getIndexes()[1].expireAfterSeconds     // Output: 3600  (verified)

// Gotcha: TTL ignores non-Date values
db.sessions.insertOne({ u: 5, createdAt: "2025-01-01" })  // string -> NEVER expires
// Fix with schema validation: require BSON type "date"
db.runCommand({ collMod: "sessions", validator: { $jsonSchema: { properties: { createdAt: { bsonType: "date" } } } } })

// Monitor: serverStatus.metrics.ttl shows deletedDocuments and passes
db.serverStatus().metrics.ttl     // { deletedDocuments: Long('...'), passes: Long('...') }
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose shorthand: expires accepts seconds or a string like '5m'
const otpSchema = new mongoose.Schema({
  phone: String,
  code: String,
  createdAt: { type: Date, default: Date.now, expires: 300 }, // TTL index, 5 minutes
});
const Otp = mongoose.model('Otp', otpSchema);

app.post('/api/otp/verify', async (req, res) => {
  const otp = await Otp.findOne({ phone: req.body.phone, code: req.body.code });
  // Still check the time yourself! TTL deletion can lag up to ~60s (or more under load)
  if (!otp || Date.now() - otp.createdAt.getTime() > 300 * 1000) return res.status(400).json({ error: 'Invalid or expired' });
  await Otp.deleteOne({ _id: otp._id });   // one-time use
  res.json({ ok: true });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Relying on TTL for exact-time security
```javascript
// Wrong - assumes the OTP is gone exactly at 5 minutes
const otp = await Otp.findOne({ phone, code });  // may still exist up to ~60 s late
// Right - also compare timestamps in the query
await Otp.findOne({ phone, code, createdAt: { $gt: new Date(Date.now() - 300000) } });
```

❌ Mistake 2: Storing the date as a string or number
✅ Correct: use a real BSON Date (`new Date()`); otherwise TTL never fires.

❌ Mistake 3: Making a compound TTL index (not supported) or adding TTL on a capped collection.

---

## 🧠 Tricky Interview Question

```javascript
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 5 })
db.sessions.insertOne({ createdAt: new Date() })
// After 6 seconds, is the document gone?
```
Answer: Not necessarily. TTL monitor runs about every 60 seconds, so the document may live up to roughly a minute longer than 5 seconds (and longer under heavy load). TTL guarantees *eventual* removal, not exact-time removal. Always filter by time in queries when exactness matters.

---

## ⚫ Interview Questions + Answers

Q1: How often does the TTL monitor run?
A1: About every 60 seconds.

Q2: Which field types are supported?
A2: A BSON Date or an array containing Dates (earliest date counts). Other types are ignored.

Q3: How to expire a document at a specific time?
A3: Store the expiry timestamp in `expireAt` and create the index with `expireAfterSeconds: 0`.

Q4: How to change `expireAfterSeconds`?
A4: `collMod` with `index.keyPattern` and the new value; no rebuild needed.

Q5: Can a TTL index be compound?
A5: No, only single-field TTL indexes expire documents (a compound index with `expireAfterSeconds` does not behave as TTL).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Sessions, OTPs, password-reset tokens, caches, temporary logs

❌ Avoid when:
- Data must be retained or auditable
- You need second-exact deletion
- Time-series data: prefer time-series collections with built-in expiration (`expireAfterSeconds` on the collection)

---

## 📊 Visual Diagram
```
t=0s   insert {createdAt: now}
t=5s   document is "expired" (createdAt + 5s)
t=5..60s  still visible until next TTL pass
t<=60s TTL monitor wakes ──► deletes expired docs (batch)

TTL monitor:  |----60s----|----60s----|----60s----|
                           ^ delete pass
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TTL | Time To Live | जीवनकाल |
| expireAfterSeconds | Lifetime in seconds | सेकंड में lifetime |
| TTL monitor | Background deleter (~60 s) | Background deleter |
| expireAt | Field holding exact expiry date | Exact expiry date वाली field |
| collMod | Modify collection/index options | Options बदलने का command |

---

## ⚡ 3-Line Summary
English:
1. TTL index on a Date field auto-deletes documents `expireAfterSeconds` after that date.
2. The monitor runs about every 60 s, so deletion is eventual, not exact.
3. Use `expireAfterSeconds: 0` + `expireAt` for per-document expiry; use real Dates.

Hindi:
1. Date field पर TTL index उस date के `expireAfterSeconds` बाद documents अपने-आप delete करता है।
2. Monitor लगभग हर 60 s चलता है, इसलिए deletion देर से होता है, exact नहीं।
3. Per-document expiry के लिए `expireAfterSeconds: 0` + `expireAt`; असली Date use करो।

---

## ➡️ Next Topic
**47. Text, Hashed and Wildcard Indexes**
