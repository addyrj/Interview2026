# 114. GDPR, Data Retention and TTL Strategy
# हिंदी में: GDPR, Data Retention और TTL Strategy

---

## 🔵 Simple Definition (English)
**Data retention** means deciding *how long* each kind of data is kept and then deleting it automatically. **GDPR** (EU) and India's **DPDP Act** give users the right to access, correct and **erase** their personal data, and require you to keep data only as long as needed ("storage limitation"). In MongoDB the main tools are **TTL indexes** (automatic expiry), explicit **erasure/anonymization jobs**, field-level **minimization**, and **audit logs** that prove what was deleted.

## 🔵 सरल परिभाषा (Hindi)
**Data retention** का मतलब है तय करना कि हर तरह का data *कितने समय* तक रखा जाएगा और फिर उसे अपने-आप delete करना। **GDPR** (EU) और भारत का **DPDP Act** users को अपना personal data देखने, सुधारने और **मिटवाने (erase)** का अधिकार देते हैं, और कहते हैं कि data सिर्फ ज़रूरत भर रखो ("storage limitation")। MongoDB में मुख्य tools हैं: **TTL indexes** (automatic expiry), **erasure/anonymization jobs**, field-level **minimization**, और **audit logs** जो साबित करें कि क्या delete हुआ।

---

## 🔴 Problem it Solves
Without a retention plan, databases only grow: old sessions, OTPs, logs, deleted-account data and backups pile up. That costs storage, slows queries, enlarges the blast radius of a breach, and violates the law — a user who asks "delete my data" must really be forgotten (within ~30 days under GDPR), including copies in orders, logs and analytics. Writing ad-hoc `cron` scripts per collection is error-prone; a declarative policy (TTL index + a documented erasure routine) is auditable and consistent.

## 🔴 यह क्यों बना? (Hindi)
Retention plan के बिना database सिर्फ बढ़ता है: पुराने sessions, OTPs, logs, deleted-account का data और backups जमा होते जाते हैं। इससे storage का खर्च बढ़ता है, queries धीमी होती हैं, breach का नुकसान बड़ा होता है, और कानून भी टूटता है — जो user कहे "मेरा data delete करो" उसे सच में भुलाना पड़ता है (GDPR में लगभग 30 दिन में), orders, logs और analytics की copies समेत। हर collection के लिए अलग `cron` scripts लिखना गलतियों वाला रास्ता है; declarative policy (TTL index + documented erasure routine) ज़्यादा auditable और consistent है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Classify data**: PII (name, email, phone, address), financial (must be kept by tax law, e.g. invoices 7-8 years), operational (sessions, OTP, logs), analytics (can be anonymized).
Step 2 → **Set a retention period per class**: OTP = 5 min, sessions = 30 days, app logs = 90 days, audit logs = 1 year, invoices = per law.
Step 3 → **TTL index** on a Date field: `createIndex({ field: 1 }, { expireAfterSeconds: N })`. A background thread (the *TTL monitor*) wakes up **every 60 seconds** and deletes expired documents. Deletion is *not instant* — it can lag by a minute or more.
Step 4 → Two TTL styles: (a) **relative** — `lastSeen` + `expireAfterSeconds: 3600` (expire 1h after that date); (b) **absolute** — a per-document `expireAt` date with `expireAfterSeconds: 0` (expire exactly at that date; each doc can have its own lifetime).
Step 5 → **Right to erasure**: on a request, delete or **anonymize** the user's PII across all collections (users, orders, addresses, support tickets). Where law forces you to keep a record (invoice), keep the row but strip the identity.
Step 6 → **Log the erasure** (who/when/what, not the PII itself) in an audit collection, and remember **backups** and **replicas** still hold old data until they rotate.
Step 7 → Change a TTL later with `collMod`; no rebuild needed.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Data classify करो**: PII (नाम, email, phone, पता), financial (कानून के हिसाब से रखना पड़ता है, जैसे invoices 7-8 साल), operational (sessions, OTP, logs), analytics (anonymize हो सकता है)।
Step 2 → **हर class का retention period तय करो**: OTP = 5 मिनट, sessions = 30 दिन, app logs = 90 दिन, audit logs = 1 साल, invoices = कानून के अनुसार।
Step 3 → Date field पर **TTL index** बनाओ: `createIndex({ field: 1 }, { expireAfterSeconds: N })`। एक background thread (*TTL monitor*) **हर 60 सेकंड** जागकर expired documents delete करता है। Delete *तुरंत नहीं* होता — एक मिनट या ज़्यादा की देरी हो सकती है।
Step 4 → TTL के दो तरीके: (a) **relative** — `lastSeen` + `expireAfterSeconds: 3600` (उस date के 1 घंटे बाद expire); (b) **absolute** — हर document की अपनी `expireAt` date और `expireAfterSeconds: 0` (ठीक उसी date पर expire; हर doc की अलग उम्र हो सकती है)।
Step 5 → **Erasure का अधिकार**: request आने पर user का PII सभी collections (users, orders, addresses, support tickets) में delete या **anonymize** करो। जहाँ कानून record रखने को कहे (invoice), वहाँ row रखो पर पहचान हटा दो।
Step 6 → Erasure को audit collection में **log करो** (किसने/कब/क्या — PII खुद नहीं), और याद रखो **backups** और **replicas** में पुराना data तब तक रहेगा जब तक वे rotate न हों।
Step 7 → TTL बाद में `collMod` से बदलो; index दोबारा नहीं बनाना पड़ता।

---

## 🟡 Real World Example
**Swiggy** stores login OTPs, cart snapshots, delivery-partner GPS pings and order history. OTPs live 5 minutes (`expireAt` TTL), GPS pings 30 days, carts 7 days. When a user taps "Delete my account", a job anonymizes the `users` document (`name: "ERASED"`, `email/phone: null`), strips email from past orders (the order and payment amounts must stay for GST/accounting), and writes `{ action: "erase", userId, ts }` to an audit log. Only the 1-year audit log has its own TTL, so even proof-of-deletion is not kept forever.

## 🟡 Real Example Hindi mein
**Swiggy** login OTP, cart snapshots, delivery-partner GPS pings और order history रखता है। OTP 5 मिनट (`expireAt` TTL), GPS pings 30 दिन, carts 7 दिन। जब user "Delete my account" दबाता है तो एक job `users` document को anonymize करती है (`name: "ERASED"`, `email/phone: null`), पुराने orders से email हटाती है (order और payment की amount GST/accounting के लिए रहनी चाहिए), और audit log में `{ action: "erase", userId, ts }` लिखती है। सिर्फ 1-साल वाले audit log की अपनी TTL है, यानी deletion का सबूत भी हमेशा नहीं रखा जाता।

---

## 💻 Code Example — Basic

```javascript
// mongosh — tested on MongoDB 8.0.4
use("shop"); // select database

// 1) Relative TTL: delete a session 3600s (1h) after its lastSeen date
db.sessions.createIndex({ lastSeen: 1 }, { expireAfterSeconds: 3600 });

// a session last seen 2 hours ago -> will be removed by the TTL monitor on its next pass
db.sessions.insertOne({ u: "a", lastSeen: new Date(Date.now() - 7200000) });

// show the indexes and which one has a TTL
db.sessions.getIndexes().map(i => ({ name: i.name, ttl: i.expireAfterSeconds }));
// Output: [ { name: '_id_', ttl: undefined }, { name: 'lastSeen_1', ttl: 3600 } ]

// 2) Absolute TTL: each document carries its own expiry date, expireAfterSeconds is 0
db.otp.createIndex({ expireAt: 1 }, { expireAfterSeconds: 0 });
// this OTP expires exactly 5 minutes from now
db.otp.insertOne({ code: "1234", expireAt: new Date(Date.now() + 300000) });
db.otp.getIndexes()[1].expireAfterSeconds; // Output: 0

// 3) Change the TTL later WITHOUT dropping the index (instant metadata change)
db.runCommand({
  collMod: "sessions",                       // collection to modify
  index: { keyPattern: { lastSeen: 1 }, expireAfterSeconds: 86400 } // now 1 day
});
db.sessions.getIndexes()[1].expireAfterSeconds; // Output: 86400
```

## 💻 Code Example — Advanced

```javascript
// mongosh — Right-to-erasure by ANONYMIZATION + audit, tested on MongoDB 8.0.4
use("shop");

db.users.insertMany([
  { _id: 1, name: "Asha", email: "asha@x.in", phone: "999" },
  { _id: 2, name: "Ravi", email: "r@x.in",    phone: "888" }
]);
db.orders.insertMany([
  { userId: 1, amt: 500, email: "asha@x.in" },   // invoice data must be kept (tax law)
  { userId: 1, amt: 200, email: "asha@x.in" }
]);

function eraseUser(userId) {
  // 1) Anonymize the identity but keep the row (primary key & foreign keys stay valid)
  const u = db.users.updateOne(
    { _id: userId },
    { $set: { name: "ERASED", email: null, phone: null, erasedAt: new Date() } }
  );
  // 2) Strip PII copies that were denormalized into other collections
  const o = db.orders.updateMany({ userId }, { $unset: { email: "" } });
  // 3) Audit entry WITHOUT any PII (only ids and counts)
  db.audit.insertOne({ action: "erase", userId, users: u.modifiedCount, orders: o.modifiedCount, ts: new Date() });
  return { users: u.modifiedCount, orders: o.modifiedCount };
}

eraseUser(1);                                   // Output: { users: 1, orders: 2 }
db.users.findOne({ _id: 1 }, { erasedAt: 0 });
// Output: { _id: 1, name: 'ERASED', email: null, phone: null }

// Audit logs themselves expire after 1 year (365*24*3600 seconds)
db.audit.createIndex({ ts: 1 }, { expireAfterSeconds: 31536000 });

// Hard delete variant (when no legal hold applies): remove everything for the user
// db.sessions.deleteMany({ u: "asha" }); db.users.deleteOne({ _id: 1 });
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose schema with TTL + an erasure endpoint (Express)
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

// Schema-level TTL: Mongoose creates the TTL index on startup (autoIndex)
const otpSchema = new mongoose.Schema({
  phone: String,
  code: String,
  expireAt: { type: Date, required: true, index: { expireAfterSeconds: 0 } }, // absolute expiry
});
const Otp = mongoose.model('Otp', otpSchema);

// Alternative shorthand: "expires" creates relative TTL on createdAt
const sessionSchema = new mongoose.Schema({
  userId: String,
  createdAt: { type: Date, default: Date.now, expires: '30d' }, // delete 30 days after creation
});

const User = mongoose.model('User', new mongoose.Schema({ name: String, email: String, phone: String }));
const Audit = mongoose.model('Audit', new mongoose.Schema({ action: String, userId: String, ts: { type: Date, default: Date.now, expires: '365d' } }));

// DELETE /api/me — right to erasure (auth middleware assumed to set req.userId)
app.delete('/api/me', async (req, res) => {
  await User.updateOne({ _id: req.userId }, { $set: { name: 'ERASED', email: null, phone: null } });
  await Audit.create({ action: 'erase', userId: req.userId }); // log id only, never PII
  res.status(202).json({ status: 'erasure scheduled/complete' });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting TTL deletion to be instant
```javascript
// Wrong — assuming the OTP disappears at exactly expireAt, so no code check is needed
const otp = await Otp.findOne({ phone });
if (otp) allowLogin();

// Right — TTL monitor runs ~every 60s, so ALSO check expiry in your query
const otp = await Otp.findOne({ phone, expireAt: { $gt: new Date() } });
```

❌ Mistake 2: TTL index on a non-Date field, or on a compound index
✅ Correct: TTL only works on a **single-field** index whose value is a **BSON Date** (or an array containing Dates). A string like `"2026-01-01"` or a number is silently never expired. TTL indexes also don't work on capped collections, and `_id` cannot be a TTL field.

❌ Mistake 3: "Deleted" users still live in backups, logs and analytics
✅ Correct: Include erasure in your policy for backups (rotate within the legal window), search indexes, caches and data warehouses; keep only anonymized aggregates.

---

## 🧠 Tricky Interview Question

```javascript
db.t.createIndex({ createdAt: 1 }, { expireAfterSeconds: 60 });
db.t.insertOne({ createdAt: "2020-01-01" });   // note: a STRING
// Will this doc be deleted after a minute?
```
Answer: **No.** The TTL monitor only considers fields of BSON `Date` type. A string never expires, and nothing warns you. Always store `new Date(...)`. Related trap: setting `expireAfterSeconds: 0` with a field that has a *future* date means "delete at that date", while with a *past/now* date it is deleted on the next 60-second pass.

---

## ⚫ Interview Questions + Answers

Q1: How does a TTL index work and how often does it delete?
A1: A background TTL monitor thread runs every 60 seconds, scans the TTL index for entries older than `now - expireAfterSeconds` and deletes those documents. Deletion is approximate; on a busy server it may lag. Secondaries don't run it themselves; the deletes replicate from the primary.

Q2: Relative vs absolute TTL — which to choose?
A2: Relative (`expireAfterSeconds: N` on `createdAt`) gives every document the same lifetime. Absolute (`expireAfterSeconds: 0` on `expireAt`) lets each document choose (OTP 5 min, trial token 7 days) and lets you *extend* life by updating `expireAt`. Use absolute when lifetimes vary or must be extended.

Q3: How do you implement the GDPR "right to be forgotten" in MongoDB?
A3: Identify every collection holding the user's PII, then either hard-delete or anonymize (keep the row for legal/accounting but null the identity fields), remove denormalized copies, purge caches/search indexes, log the erasure (without PII), and make sure backups age out. Also expose a data export (right of access) endpoint.

Q4: Can you change a TTL value after creating the index?
A4: Yes: `db.runCommand({ collMod: "c", index: { keyPattern: { f: 1 }, expireAfterSeconds: N } })`. No rebuild. (Converting a regular index into a TTL one is version dependent; if collMod refuses, drop and recreate it.)

Q5: Why prefer anonymization over deletion sometimes?
A5: Foreign keys, financial records, fraud analysis and aggregate statistics need the rows. Anonymization removes the personal link (name/email/phone) while preserving totals and referential integrity. Note: truly anonymous data falls outside GDPR; merely pseudonymized data (still re-identifiable) does not.

---

## 🔷 When to Use + When Not to Use
✅ Use TTL when:
- Data is naturally temporary: sessions, OTPs, password-reset tokens, caches, rate-limit counters, logs
- You need a compliance-friendly, declarative retention rule that needs no cron job

❌ Avoid TTL when:
- You need precise, instant deletion (check expiry in queries too) or a deletion that must cascade to many collections (use an explicit erasure job)
- Data must be retained by law (invoices, financial audit trails) — anonymize instead
- Huge collections where mass TTL deletes cause load spikes; consider time-series collections or dropping time-bucketed collections instead

---

## 📊 Visual Diagram
```
RETENTION + ERASURE FLOW
──────────────────────────────────────────────────────
 Temporary data                    Personal data
 (OTP, sessions, logs)             (users, orders, tickets)
        │                                   │
   expireAt / createdAt              "Delete my account"
        │                                   │
        ▼                                   ▼
 ┌───────────────┐                 ┌─────────────────┐
 │ TTL monitor   │ every 60 s      │ Erasure job     │
 │ deleteMany(   │                 │ anonymize/delete│
 │  expired)     │                 │ all collections │
 └───────┬───────┘                 └────────┬────────┘
         │                                  │
         ▼                                  ▼
   doc gone (≈ within 1-2 min)      audit {id, ts}  ──TTL 1y──► gone
                                    backups age out (30-90 days)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TTL index | Index that auto-deletes expired docs | Expired docs अपने-आप हटाने वाला index |
| expireAfterSeconds | Seconds after the Date field to delete | Date field के कितने सेकंड बाद delete |
| TTL monitor | Background thread, runs every 60 s | हर 60 सेकंड चलने वाला background thread |
| Right to erasure | User's right to have data deleted | Data मिटवाने का अधिकार |
| Anonymization | Removing the link to a person | व्यक्ति से link हटाना |
| Storage limitation | Keep data only as long as needed | ज़रूरत भर ही data रखना |
| collMod | Command to alter collection/index options | Collection/index options बदलने का command |

---

## ⚡ 3-Line Summary
English:
1. Define a retention period per data class; use TTL indexes (single Date field, monitor runs every ~60 s) for temporary data.
2. For GDPR/DPDP erasure, delete or anonymize PII in every collection, log the action without PII, and remember backups.
3. TTL is approximate and Date-only, so still check expiry in queries and never rely on it for instant deletion.

Hindi:
1. हर data class का retention period तय करो; temporary data के लिए TTL index (single Date field, monitor ~60 सेकंड में चलता है) इस्तेमाल करो।
2. GDPR/DPDP erasure के लिए हर collection में PII delete या anonymize करो, action को PII के बिना log करो, और backups याद रखो।
3. TTL approximate है और सिर्फ Date पर चलता है, इसलिए queries में expiry भी check करो और instant deletion के लिए इस पर भरोसा मत करो।

---

## ➡️ Next Topic
**115. Design a URL Shortener Schema** — first interview-problem: schema, unique indexes, counters, click analytics and TTL for expiring links.
