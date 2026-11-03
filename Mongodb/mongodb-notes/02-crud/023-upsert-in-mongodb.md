# 23. upsert in MongoDB
# हिंदी में: MongoDB में upsert

---

## 🔵 Simple Definition (English)
**Upsert** = **up**date + in**sert**. When you pass `{ upsert: true }` to an update (`updateOne`, `updateMany`, `replaceOne`, `findOneAndUpdate`, `bulkWrite`), MongoDB **updates** the matching document if one exists, and otherwise **inserts a new one** built from the filter's equality fields plus your update. `$setOnInsert` lets you set fields only on the insert path.

## 🔵 सरल परिभाषा (Hindi)
**Upsert** = **up**date + in**sert**। जब आप किसी update (`updateOne`, `updateMany`, `replaceOne`, `findOneAndUpdate`, `bulkWrite`) में `{ upsert: true }` देते हैं, तो MongoDB match होने वाला document **update** करता है, और न मिले तो filter के equality fields और आपके update से बना **नया document insert** कर देता है। `$setOnInsert` से ऐसी fields सेट कर सकते हैं जो सिर्फ insert वाले रास्ते पर लगें।

---

## 🔴 Problem it Solves
Without upsert you write "find; if found update else insert" — two round trips and a **race**: two requests both see "not found" and both insert, creating duplicates. This matters for page-view counters, user-profile sync from another system, last-seen heartbeats, and idempotent event ingestion. `upsert: true` collapses this into one atomic statement (and with a **unique index** it is fully safe).

## 🔴 यह क्यों बना? (Hindi)
Upsert के बिना आप "find करो; मिला तो update नहीं तो insert" लिखते हैं — दो round trips और एक **race**: दो requests दोनों को "not found" दिखता है और दोनों insert कर देती हैं, duplicates बन जाते हैं। ये page-view counters, किसी दूसरे system से user-profile sync, last-seen heartbeat और idempotent event ingestion में मायने रखता है। `upsert: true` इसे एक atomic statement में बदल देता है (और **unique index** हो तो पूरी तरह safe)।

---

## 🟢 How it Works — Step by Step

Step 1 → MongoDB searches for a document matching the `filter`.
Step 2 → **Found** → normal update is applied. `matchedCount: 1`, `upsertedCount: 0`.
Step 3 → **Not found** → MongoDB builds a new document: first the **equality conditions** from the filter (`{ page: "home" }` becomes `page: "home"`), then it applies the update operators (`$inc` on a missing field starts from 0), then adds `$setOnInsert` fields.
Step 4 → A generated `_id` is added (unless the filter or update supplies one). The result has `upsertedId` and `upsertedCount: 1`.
Step 5 → Range conditions such as `{ b: { $gt: 5 } }` are **not** copied into the new document. For multi-clause `$or` filters nothing from the filter is copied.
Step 6 → Concurrent upserts on the same key can still both insert if there is **no unique index**; add one on the filter key, and the loser retries as an update (the driver/server may return a duplicate key error `11000` that you can retry).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → MongoDB `filter` से match होने वाला document ढूँढता है।
Step 2 → **मिला** → सामान्य update लगता है। `matchedCount: 1`, `upsertedCount: 0`।
Step 3 → **नहीं मिला** → MongoDB नया document बनाता है: पहले filter की **equality conditions** (`{ page: "home" }` से `page: "home"`), फिर update operators (missing field पर `$inc` 0 से शुरू होता है), फिर `$setOnInsert` की fields।
Step 4 → एक generated `_id` जुड़ती है (जब तक filter या update खुद न दे)। Result में `upsertedId` और `upsertedCount: 1` मिलता है।
Step 5 → `{ b: { $gt: 5 } }` जैसी range conditions नए document में **कॉपी नहीं** होतीं। कई clauses वाले `$or` filter से कुछ भी copy नहीं होता।
Step 6 → **unique index** न हो तो एक ही key पर concurrent upserts दोनों insert कर सकते हैं; filter key पर unique index लगाओ, हारने वाला update की तरह retry करता है (server duplicate key error `11000` दे सकता है जिसे retry कर सकते हैं)।

---

## 🟡 Real World Example
**Flipkart product-page view counter**: every page hit runs `updateOne({ page: "/p/iphone" }, { $inc: { views: 1 } }, { upsert: true })`. First ever view creates the counter document with `views: 1`; later hits just increment. **Customer sync** from the CRM: `updateOne({ email }, { $set: profile, $setOnInsert: { createdAt: now } }, { upsert: true })` — `createdAt` is written once and never touched again.

## 🟡 Real Example Hindi mein
**Flipkart product-page view counter**: हर page hit पर `updateOne({ page: "/p/iphone" }, { $inc: { views: 1 } }, { upsert: true })` चलता है। पहली बार view आने पर `views: 1` वाला counter document बन जाता है; बाद की hits बस increment करती हैं। CRM से **customer sync**: `updateOne({ email }, { $set: profile, $setOnInsert: { createdAt: now } }, { upsert: true })` — `createdAt` सिर्फ एक बार लिखा जाता है, फिर कभी नहीं छुआ जाता।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4, mongosh.

```javascript
use flipkart_demo                                  // switch database
db.dropDatabase()                                  // clean start

// 1) First call -> no match -> INSERT
db.pagestats.updateOne(
  { page: "home" },                                // filter (also seeds the new doc)
  { $inc: { views: 1 } },                          // $inc on a missing field starts at 0 -> 1
  { upsert: true }                                 // the magic flag
).upsertedCount
// Output: 1

// 2) Second call -> match -> UPDATE
db.pagestats.updateOne({ page: "home" }, { $inc: { views: 1 } }, { upsert: true })
// Output: { acknowledged: true, insertedId: null, matchedCount: 1, modifiedCount: 1, upsertedCount: 0 }
db.pagestats.find({}, { _id: 0 }).toArray()
// Output: [ { page: 'home', views: 2 } ]          (one document, not two)

// 3) Range operators in the filter are NOT copied to the new document
db.s2.updateOne({ a: 1, b: { $gt: 5 } }, { $set: { c: 1 } }, { upsert: true })
db.s2.find({}, { _id: 0 }).toArray()
// Output: [ { a: 1, c: 1 } ]                      (b is absent!)

// 4) $setOnInsert — only on the insert path
db.s3.updateOne({ k: "x" }, { $setOnInsert: { createdAt: "T0" }, $set: { seen: 1 } }, { upsert: true })
db.s3.updateOne({ k: "x" }, { $setOnInsert: { createdAt: "T1" }, $set: { seen: 2 } }, { upsert: true })
db.s3.find({}, { _id: 0 }).toArray()
// Output: [ { k: 'x', createdAt: 'T0', seen: 2 } ]  (createdAt stayed T0)

// 5) _id in the filter becomes the new _id
db.s5.updateOne({ _id: "fixed" }, { $set: { v: 1 } }, { upsert: true })
db.s5.find().toArray()
// Output: [ { _id: 'fixed', v: 1 } ]

// 6) Multi-clause $or filter: nothing is copied from the filter
db.s7.updateOne({ $or: [{ a: 1 }, { b: 2 }] }, { $set: { c: 1 } }, { upsert: true })
db.s7.find({}, { _id: 0 }).toArray()
// Output: [ { c: 1 } ]

// 7) replaceOne and updateMany can upsert too
db.s6.replaceOne({ u: 1 }, { u: 1, z: 2 }, { upsert: true }).upsertedCount   // 1
db.s8.updateMany({ q: 1 }, { $set: { w: 1 } }, { upsert: true }).upsertedCount // 1 (inserts ONE doc)
```
(`_id` values are ObjectIds and differ on every run.)

## 💻 Code Example — Advanced

```javascript
// Unique index + upsert = safe under concurrency (mongosh)
db.users.createIndex({ email: 1 }, { unique: true })   // guarantees one doc per email
db.users.updateOne(
  { email: "a@x.com" },                                // natural key
  { $set: { n: 1 } },
  { upsert: true }
)                                                      // first run inserts
db.users.updateOne({ email: "a@x.com" }, { $set: { n: 2 } }, { upsert: true }).matchedCount
// Output: 1   (second run updates instead of inserting a duplicate)
```

```javascript
// Node.js driver v6 — idempotent ingestion with retry on duplicate-key race
async function upsertCustomer(col, profile) {
  for (let attempt = 0; attempt < 3; attempt++) {      // small retry loop
    try {
      const r = await col.updateOne(
        { email: profile.email },                      // natural key (unique index required)
        {
          $set: { name: profile.name, city: profile.city, updatedAt: new Date() }, // always refreshed
          $setOnInsert: { createdAt: new Date() }      // only first time
        },
        { upsert: true }
      );
      return r.upsertedCount === 1 ? 'created' : 'updated'; // tells caller what happened
    } catch (err) {
      if (err.code !== 11000) throw err;               // 11000 = two concurrent upserts raced
      // loop again: the doc now exists, so this time it will match and update
    }
  }
  throw new Error('upsert failed after retries');
}
```

---

## 🟠 Express.js / Mongoose Integration

Tested against MongoDB 8.0.4, Express 5, Mongoose 8.

```javascript
const express = require('express');
const mongoose = require('mongoose');
const app = express();

// POST /visit/home  -> increments the counter, creating it on first hit
app.post('/visit/:page', async (req, res) => {
  const doc = await mongoose.connection.collection('pv').findOneAndUpdate(
    { page: req.params.page },                         // counter key
    { $inc: { views: 1 }, $setOnInsert: { first: true } }, // $setOnInsert only the first time
    { upsert: true, returnDocument: 'after', projection: { _id: 0 } }
  );
  res.json(doc);
});
// Real run: 1st call -> {"page":"home","first":true,"views":1}
//           2nd call -> {"page":"home","first":true,"views":2}

// Mongoose model version
// await Stat.findOneAndUpdate({ page }, { $inc: { views: 1 } }, { upsert: true, returnDocument: 'after', setDefaultsOnInsert: true });
```
In Mongoose, `setDefaultsOnInsert` applies schema defaults when the upsert inserts (enabled by default in Mongoose 6+), and timestamps (`createdAt`) are set via `$setOnInsert` automatically.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Upsert without a unique index
```javascript
// Wrong — two simultaneous requests may both insert { email: "a@x.com" }
db.users.updateOne({ email: "a@x.com" }, { $set: { n: 1 } }, { upsert: true })

// Right — create the unique index first
db.users.createIndex({ email: 1 }, { unique: true })
```

❌ Mistake 2: Expecting range filters to appear in the new document
```javascript
// Wrong assumption — b: { $gt: 5 } will be stored
db.s2.updateOne({ a: 1, b: { $gt: 5 } }, { $set: { c: 1 } }, { upsert: true })
// Reality: inserted { a: 1, c: 1 } — no b
// Right — set the field explicitly
db.s2.updateOne({ a: 1, b: { $gt: 5 } }, { $set: { c: 1 }, $setOnInsert: { b: 6 } }, { upsert: true })
```

❌ Mistake 3: Using `$set` for a "created at" field
```javascript
// Wrong — createdAt is overwritten on every call
{ $set: { createdAt: new Date() } }
// Right
{ $setOnInsert: { createdAt: new Date() } }
```

---

## 🧠 Tricky Interview Question

```javascript
db.s8.updateMany({ q: 1 }, { $set: { w: 1 } }, { upsert: true })
```
The collection is empty. How many documents are inserted?

Answer: **One**. `updateMany` with `upsert: true` inserts a single document `{ q: 1, w: 1 }` when nothing matches (real result: `upsertedCount: 1`). If several documents already match, all are updated and nothing is inserted. A second trap: an upsert whose filter uses a field with a unique index conflicting with your update can raise error 11000.

---

## ⚫ Interview Questions + Answers

Q1: What does `upsert: true` do?
A1: Updates the matching document, or inserts a new one built from the filter's equality conditions and the update if no document matches.

Q2: How do you set a field only when inserting?
A2: Use `$setOnInsert`. It is ignored when an existing document is updated.

Q3: Is upsert atomic and race-safe?
A3: The single operation is atomic on one document, but without a unique index two concurrent upserts for the same key may both insert. With a unique index one fails with E11000 and can be retried as an update.

Q4: What does the result look like?
A4: `matchedCount`, `modifiedCount`, `upsertedCount` and `upsertedId` (present only when an insert happened).

Q5: What gets copied from the filter into the new document?
A5: Only top-level equality conditions (including `$eq`, and dotted fields). Range operators, `$in` with several values and multi-clause `$or` are not copied.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Counters, heartbeats, "last seen", rate-limit buckets.
- Syncing data from another system keyed by a natural key.
- Idempotent consumers (event may arrive twice).

❌ Avoid when:
- You must know that the document is new vs existing and treat them differently in complex ways (use explicit insert + handle duplicate key).
- No unique index exists on the key and duplicates would be harmful.
- Using the `$` positional operator in the update (not valid with an inserting upsert).

---

## 📊 Visual Diagram
```
 updateOne(filter, update, { upsert: true })
                 │
         match found?
        ┌────yes─┴─no────┐
        ▼                ▼
   apply update     build new doc:
   (matched=1)       1. equality fields of filter
                     2. apply update operators
                     3. add $setOnInsert fields
                     4. add _id
                    (upsertedCount=1, upsertedId)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| upsert | Update if exists, else insert | है तो update, नहीं तो insert |
| `$setOnInsert` | Sets fields only when an insert happens | सिर्फ insert पर fields सेट करता है |
| upsertedId | `_id` of the inserted document | Insert हुए document की `_id` |
| Unique index | Prevents duplicate key values | Duplicate values रोकने वाला index |
| E11000 | Duplicate key error code | Duplicate key error का code |
| Idempotent | Safe to repeat with same result | बार-बार चलाने पर वही नतीजा |

---

## ⚡ 3-Line Summary
English:
1. `upsert: true` updates a matching document or inserts a new one built from the filter's equality fields plus the update.
2. Use `$setOnInsert` for insert-only fields and always back the key with a unique index.
3. Range filters and multi-clause `$or` are not copied into the inserted document; `updateMany` upserts only one document.

Hindi:
1. `upsert: true` match होने पर update करता है, नहीं तो filter की equality fields और update से नया document insert करता है।
2. Insert-only fields के लिए `$setOnInsert` इस्तेमाल करो और key पर हमेशा unique index लगाओ।
3. Range filters और multi-clause `$or` नए document में copy नहीं होते; `updateMany` का upsert सिर्फ एक document insert करता है।

---

## ➡️ Next Topic
**24. deleteOne, deleteMany and findOneAndDelete** — removing documents safely, and returning what was deleted.
