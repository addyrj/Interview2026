# 10. _id field and uniqueness
# हिंदी में: _id field और Uniqueness

---

## 🔵 Simple Definition (English)
Every document in a collection has a mandatory, **unique, immutable** `_id` field that acts as the primary key. If you do not supply it, the driver (or server) generates an `ObjectId`. MongoDB automatically builds a unique index named `_id_` on it. You may supply your own `_id` of almost any type (number, string, UUID, compound object) except an array.

## 🔵 सरल परिभाषा (Hindi)
Collection के हर document में अनिवार्य, **unique, immutable** `_id` field होती है जो primary key का काम करती है। अगर आप नहीं देते तो driver (या server) `ObjectId` generate करता है। MongoDB इस पर `_id_` नाम का unique index अपने आप बनाता है। आप लगभग किसी भी type की अपनी `_id` दे सकते हैं (number, string, UUID, compound object), array को छोड़कर।

---

## 🔴 Problem it Solves
Every record needs a stable identity for lookups, updates and replication. A server-generated, globally-unique `ObjectId` allows multiple app servers to create IDs without coordination (no auto-increment bottleneck). Custom `_id` lets you reuse a natural key (e.g. `email`, `orderNo`) and get uniqueness for free.

## 🔴 यह क्यों बना? (Hindi)
हर record को lookups, updates और replication के लिए स्थिर पहचान चाहिए। Globally-unique `ObjectId` कई app servers को बिना coordination के IDs बनाने देता है (auto-increment का bottleneck नहीं)। Custom `_id` से आप natural key (जैसे `email`, `orderNo`) इस्तेमाल करके uniqueness मुफ़्त पाते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → On insert without `_id`, the driver adds `_id: ObjectId()` (12 bytes: 4-byte timestamp + 5-byte random + 3-byte counter).
Step 2 → The server stores the doc and maintains the unique `_id_` index (cannot be dropped).
Step 3 → Inserting a duplicate `_id` fails with error code **11000** (E11000 duplicate key).
Step 4 → `_id` cannot be changed by `$set` after creation (to change, insert a new doc and delete the old one).
Step 5 → In `_id` queries from HTTP, convert strings with `new ObjectId(str)`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `_id` के बिना insert करने पर driver `_id: ObjectId()` जोड़ता है (12 bytes: 4-byte timestamp + 5-byte random + 3-byte counter)।
Step 2 → Server doc store करता है और unique `_id_` index maintain करता है (इसे drop नहीं कर सकते)।
Step 3 → Duplicate `_id` insert करने पर error code **11000** (E11000 duplicate key) आता है।
Step 4 → बनने के बाद `$set` से `_id` नहीं बदल सकते (बदलना हो तो नया doc insert करो और पुराना delete)।
Step 5 → HTTP से आई `_id` को `new ObjectId(str)` से convert करो।

---

## 🟡 Real World Example
Razorpay stores payments with `_id` = their public payment id like `pay_Abc123` (a string), because clients already reference it and it must be unique. A Flipkart cart service instead keeps default ObjectIds, and sorts by `_id` to get "recent first" since ObjectIds embed creation time.

## 🟡 Real Example Hindi mein
Razorpay payments को `_id` = public payment id (जैसे `pay_Abc123`, string) के साथ रखता है क्योंकि clients पहले से उसे reference करते हैं और वह unique होनी चाहिए। Flipkart cart service default ObjectIds रखती है और "recent first" के लिए `_id` पर sort करती है क्योंकि ObjectId में creation time होता है।

---

## 💻 Code Example — Basic

```javascript
// mongod 8.0.4, database "mh"
db.users.insertOne({ _id: 1, name: "A" })     // custom numeric _id
// Output: { acknowledged: true, insertedId: 1 }

try {
  db.users.insertOne({ _id: 1, name: "B" })   // same _id again
} catch (e) {
  print(e.code)                                // Output: 11000
  print(e.message)                             // Output: E11000 duplicate key error collection: mh.users index: _id_ dup key: { _id: 1 }
}

db.users.insertOne({ name: "Auto" })           // no _id -> ObjectId generated (value varies per run)
```

## 💻 Code Example — Advanced

```javascript
// Compound / object _id (e.g. one row per user per day)
db.stats.insertOne({ _id: { user: "u1", day: "2026-01-01" }, hits: 3 })

// Extract creation time from an ObjectId
const id = new ObjectId()
id.getTimestamp()                      // ISODate of creation (varies)

// Query a time range using _id only (no createdAt needed)
const from = ObjectId.createFromTime(Math.floor(Date.now() / 1000) - 3600)  // 1 hour ago
db.users.find({ _id: { $gt: from } })  // docs created in the last hour (ObjectId _ids only)

// _id is immutable
try { db.users.updateOne({ _id: 1 }, { $set: { _id: 2 } }) }
catch (e) { print(e.code, e.message) } // Output: 66 Performing an update on the path '_id' would modify the immutable field '_id'
```
(Both the duplicate-key and immutable-field outputs were verified on mongod 8.0.4.)

---

## 🟠 Express.js / Mongoose Integration

```javascript
const { ObjectId } = require('mongodb');
app.get('/users/:id', async (req, res) => {
  if (!ObjectId.isValid(req.params.id))              // validate before converting
    return res.status(400).json({ error: 'bad id' });
  const u = await db.collection('users').findOne({ _id: new ObjectId(req.params.id) });
  u ? res.json(u) : res.status(404).end();
});
// Mongoose: Model.findById(id) casts the string for you; invalid strings throw CastError.
// Handle duplicates: if (err.code === 11000) return res.status(409).json({ error: 'already exists' });
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Querying with a string instead of ObjectId
```javascript
db.users.find({ _id: "65f0c0ffee0000000000abcd" })              // Wrong: matches nothing (string != ObjectId)
db.users.find({ _id: ObjectId("65f0c0ffee0000000000abcd") })    // Right
```

❌ Mistake 2: Trying to update `_id`
✅ Correct: Insert a new doc with the new `_id`, then delete the old one.

❌ Mistake 3: Using ObjectId order as a precise timeline across servers
✅ Correct: It is only roughly ordered (second resolution); keep a `createdAt` for exact ordering.

---

## 🧠 Tricky Interview Question
Q: `insertMany` of 5 docs where doc 3 has a duplicate `_id`. How many are inserted?
Answer: With default `ordered: true`, docs 1 and 2 are inserted, doc 3 fails and 4, 5 are never attempted. With `ordered: false`, 1, 2, 4, 5 are inserted and only doc 3 errors.

---

## ⚫ Interview Questions + Answers

Q1: Can `_id` be an array?
A1: No. Arrays are not allowed (regex also is not allowed).

Q2: What does an ObjectId contain?
A2: 4-byte timestamp (seconds), 5-byte per-process random value and 3-byte incrementing counter.

Q3: Can you drop the `_id` index?
A3: No (except on capped collections created without it historically; in general no).

Q4: Auto-increment ids in MongoDB?
A4: There is none built in; use ObjectId, UUID, or a counters collection with `findOneAndUpdate` + `$inc`.

Q5: ObjectId vs UUID?
A5: ObjectId is 12 bytes, roughly time-ordered (index-friendly); UUID is 16 bytes, v4 is random and fragments the index more.

---

## 🔷 When to Use + When Not to Use
✅ Use custom `_id` when:
- A natural unique key exists and is never changing

❌ Avoid custom `_id` when:
- The natural key can change (email) – it is immutable

---

## 📊 Visual Diagram
```
ObjectId (12 bytes)
┌────────────┬─────────────┬───────────┐
│ 4B time(s) │ 5B random   │ 3B counter│
└────────────┴─────────────┴───────────┘
 unique index "_id_" on every collection
 insert dup _id  ──►  E11000 (code 11000)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| _id | Mandatory primary key | अनिवार्य primary key |
| ObjectId | Default 12-byte id | Default 12-byte id |
| E11000 | Duplicate key error | Duplicate key error |
| Immutable | Cannot be changed | बदला नहीं जा सकता |
| Unique index | Enforces uniqueness | Uniqueness लागू करने वाला index |

---

## ⚡ 3-Line Summary
English:
1. `_id` is the unique, immutable primary key, auto-generated as ObjectId.
2. Duplicates fail with code 11000; strings are not ObjectIds in queries.
3. Use custom `_id` only with stable natural keys.

Hindi:
1. `_id` unique, immutable primary key है, ObjectId के रूप में auto-generate होती है।
2. Duplicates code 11000 से fail होते हैं; queries में string ObjectId नहीं है।
3. Custom `_id` सिर्फ stable natural keys के साथ इस्तेमाल करो।

---

## ➡️ Next Topic
**11. Capped Collections** — Fixed-size, insertion-ordered circular collections.
