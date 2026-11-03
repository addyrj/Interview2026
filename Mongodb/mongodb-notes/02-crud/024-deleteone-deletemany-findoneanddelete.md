# 24. deleteOne, deleteMany and findOneAndDelete
# हिंदी में: deleteOne, deleteMany और findOneAndDelete

---

## 🔵 Simple Definition (English)
**`deleteOne(filter)`** removes the **first** document that matches. **`deleteMany(filter)`** removes **all** matching documents. **`findOneAndDelete(filter, options)`** removes one document and **returns it** atomically (use `sort` to choose which). `deleteMany({})` empties a collection but keeps its indexes; `drop()` removes the collection itself.

## 🔵 सरल परिभाषा (Hindi)
**`deleteOne(filter)`** match होने वाला **पहला** document हटाता है। **`deleteMany(filter)`** match होने वाले **सारे** documents हटाता है। **`findOneAndDelete(filter, options)`** एक document को atomically हटाकर उसे **लौटाता** है (कौन-सा हटे, ये `sort` से चुनो)। `deleteMany({})` collection खाली करता है पर उसके indexes रखता है; `drop()` पूरी collection हटा देता है।

---

## 🔴 Problem it Solves
Data must be removed for many reasons: a user cancels a cart, GDPR "delete my data" requests, expiring OTPs, cleaning test data. Problems arise when (a) you delete too much because the filter was wrong, (b) you need the deleted data for an audit log or to hand to the next step (e.g. pop the next task from a queue), and (c) two workers must not pop the same task. The three methods cover: precise single removal, bulk removal, and atomic "remove and give it to me".

## 🔴 यह क्यों बना? (Hindi)
Data कई कारणों से हटाना पड़ता है: user cart cancel करे, GDPR "मेरा data delete करो" requests, expired OTPs, test data की सफ़ाई। दिक्कतें तब आती हैं जब (a) filter ग़लत होने से ज़्यादा delete हो जाए, (b) deleted data audit log या अगले step के लिए चाहिए (जैसे queue से अगला task pop करना), और (c) दो workers एक ही task pop न करें। ये तीनों methods इन्हें cover करते हैं: सटीक single delete, bulk delete, और atomic "हटाओ और मुझे दो"।

---

## 🟢 How it Works — Step by Step

Step 1 → **deleteOne**: finds the first match in natural/index order and removes it. Result: `{ acknowledged: true, deletedCount: 0 or 1 }`. No match is **not** an error — `deletedCount` is just 0.
Step 2 → **deleteMany**: removes every match in one command. `deletedCount` tells how many. An **empty filter `{}` deletes everything**.
Step 3 → The filter is required: calling `deleteMany()` with no argument throws `Missing required argument` in mongosh, protecting from accidents; but `deleteMany({})` is explicit and works.
Step 4 → **findOneAndDelete**: selects one document (honours `sort`, `projection`), deletes it and returns the full removed document, or `null` if nothing matched.
Step 5 → Deletes are **permanent**. There is no recycle bin; if you need undo, use a "soft delete" (`deletedAt` field) or a TTL/archival collection, and take backups.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **deleteOne**: natural/index order में पहला match ढूँढकर हटाता है। Result: `{ acknowledged: true, deletedCount: 0 या 1 }`। Match न मिलना error **नहीं** है — बस `deletedCount` 0 होता है।
Step 2 → **deleteMany**: एक command में हर match हटाता है। `deletedCount` बताता है कितने हटे। **खाली filter `{}` सब कुछ हटा देता है**।
Step 3 → Filter ज़रूरी है: mongosh में बिना argument `deleteMany()` चलाओ तो `Missing required argument` error आता है, जिससे गलती से बचाव होता है; पर `deleteMany({})` स्पष्ट रूप से लिखा है इसलिए चलता है।
Step 4 → **findOneAndDelete**: एक document चुनता है (`sort`, `projection` मानता है), हटाता है और पूरा हटाया हुआ document लौटाता है, या कुछ न मिले तो `null`।
Step 5 → Delete **स्थायी** है। कोई recycle bin नहीं; undo चाहिए तो "soft delete" (`deletedAt` field) या TTL/archive collection इस्तेमाल करो और backups रखो।

---

## 🟡 Real World Example
**Swiggy cart service**: when a user taps "clear cart", the backend runs `deleteMany({ userId })` on `cart_items`. When an order is placed, the cart document is removed with `deleteOne({ _id: cartId })`. A delivery-assignment queue uses `findOneAndDelete({ city: "Pune" }, { sort: { createdAt: 1 } })` to hand out the oldest pending request to exactly one rider-matching worker.

## 🟡 Real Example Hindi mein
**Swiggy cart service**: जब user "clear cart" दबाता है, backend `cart_items` पर `deleteMany({ userId })` चलाता है। Order place होने पर cart document `deleteOne({ _id: cartId })` से हटता है। Delivery-assignment queue `findOneAndDelete({ city: "Pune" }, { sort: { createdAt: 1 } })` इस्तेमाल करके सबसे पुरानी pending request ठीक एक worker को देती है।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4, mongosh.

```javascript
use swiggy_cart_demo                               // switch database
db.dropDatabase()                                  // clean start
db.carts.insertMany([                              // four cart rows
  { _id: 1, u: "a", st: "old" },
  { _id: 2, u: "a", st: "old" },
  { _id: 3, u: "b", st: "new" },
  { _id: 4, u: "a", st: "new" }
])

db.carts.deleteOne({ u: "a" })                     // removes ONLY the first match (_id 1)
// Output: { acknowledged: true, deletedCount: 1 }

db.carts.deleteMany({ st: "old" })                 // _id 2 is the only old one left
// Output: { acknowledged: true, deletedCount: 1 }

db.carts.find().toArray()
// Output: [ { _id: 3, u: 'b', st: 'new' }, { _id: 4, u: 'a', st: 'new' } ]

db.carts.deleteOne({ u: "nobody" })                // no match is not an error
// Output: { acknowledged: true, deletedCount: 0 }

// findOneAndDelete — returns the removed document
db.q.insertMany([{ _id: 1, p: 3 }, { _id: 2, p: 9 }, { _id: 3, p: 1 }])
db.q.findOneAndDelete({}, { sort: { p: -1 } })     // highest p first
// Output: { _id: 2, p: 9 }

db.q.findOneAndDelete({ p: 100 })                  // nothing matches
// Output: null

db.q.deleteMany({})                                // empty filter = delete everything
// Output: { acknowledged: true, deletedCount: 2 }
db.q.countDocuments({})                            // 0 documents left
db.q.getIndexes().length                           // 1 -> the _id index still exists (collection not dropped)

db.q.deleteMany()                                  // no argument at all
// Error: [COMMON-10001] Missing required argument at position 0 (Collection.deleteMany)
```

## 💻 Code Example — Advanced

```javascript
// Node.js driver v6 — soft delete, archive-then-delete, and queue pop
const { MongoClient } = require('mongodb');

async function archiveAndDelete(db, userId) {
  const users = db.collection('users');            // live collection
  const archive = db.collection('users_archive');  // cold storage
  const removed = await users.findOneAndDelete({ _id: userId }); // atomic remove + get doc
  if (!removed) return false;                      // nothing existed
  await archive.insertOne({ ...removed, deletedAt: new Date() }); // keep audit copy
  return true;
}

async function popOldestTask(db, city) {
  return db.collection('tasks').findOneAndDelete(  // v6 returns the doc itself (or null)
    { city },                                      // only this city
    { sort: { createdAt: 1 } }                     // oldest first
  );
}

async function purgeExpired(db) {
  // deleteMany with a date filter — dry-run first by counting
  const filter = { expiresAt: { $lt: new Date() } };            // expired rows
  const n = await db.collection('otps').countDocuments(filter); // how many would go?
  console.log('about to delete', n);
  const r = await db.collection('otps').deleteMany(filter);     // do it
  return r.deletedCount;
}
```

```javascript
// mongosh — deleteOne with collation (case-insensitive) and a handy "delete by _id" pattern
db.carts.deleteOne({ _id: { $exists: true } }, { collation: { locale: "en" } }).deletedCount // 1
db.t.insertMany([{ n: 1 }, { n: 2 }]); db.t.drop()      // drop() removes docs AND indexes
db.t.countDocuments()                                    // 0 (collection no longer exists)
```

---

## 🟠 Express.js / Mongoose Integration

Tested against MongoDB 8.0.4, Express 5, Mongoose 8.

```javascript
const express = require('express');
const mongoose = require('mongoose');
const Order = mongoose.model('Order', new mongoose.Schema({ customer: String }));
const app = express();

// DELETE /orders/:id  -> 200 when removed, 404 when nothing was deleted
app.delete('/orders/:id', async (req, res) => {
  const r = await Order.deleteOne({ _id: req.params.id }); // Mongoose casts id string to ObjectId
  res.status(r.deletedCount ? 200 : 404).json({ deleted: r.deletedCount });
});
// Real run: first call -> 200 {"deleted":1}; second call -> 404 {"deleted":0}

// Remove and return (for audit)
app.delete('/orders/:id/audit', async (req, res) => {
  const doc = await Order.findOneAndDelete({ _id: req.params.id }); // Mongoose doc or null
  if (!doc) return res.sendStatus(404);
  res.json(doc);
});
```
Mongoose note: `Model.deleteOne()` skips document middleware (`pre('remove')`), but runs query middleware (`pre('deleteOne', { query: true })`). Use `doc.deleteOne()` if you need document middleware.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Passing an empty/undefined filter by accident
```javascript
// Wrong — req.query.userId is undefined, filter becomes { userId: undefined } or {}
await db.collection('cart').deleteMany({});   // wipes EVERYTHING
// Right — validate first
if (!userId) throw new Error('userId required');
await db.collection('cart').deleteMany({ userId });
```

❌ Mistake 2: Treating `deletedCount: 0` as success
```javascript
// Wrong
await Order.deleteOne({ _id }); res.sendStatus(200);
// Right
const r = await Order.deleteOne({ _id }); res.sendStatus(r.deletedCount ? 200 : 404);
```

❌ Mistake 3: Using `deleteMany({})` to remove a collection and expecting a fresh state
```javascript
// Wrong assumption — indexes (and validators, options) remain
db.q.deleteMany({})           // getIndexes().length is still 1+ ; slow for millions of docs
// Right — for a full wipe of a big collection
db.q.drop()                    // fast, removes data and indexes; recreate indexes if needed
```

---

## 🧠 Tricky Interview Question

```javascript
db.carts.deleteOne({ u: "a" })
```
Three carts belong to user "a". Which one is deleted?

Answer: Just **one** — the first match in the query plan's order (usually the earliest inserted when using a collection scan, but **not guaranteed**). If the choice matters (oldest, highest priority) use `findOneAndDelete` with a `sort`, or delete by `_id`. Also remember: `deleteOne` on a **sharded** collection requires the shard key (or `_id`) in the filter.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `deleteOne` and `deleteMany`?
A1: `deleteOne` removes at most one (the first match); `deleteMany` removes all matches. Both return `{ acknowledged, deletedCount }`.

Q2: What does `findOneAndDelete` give that `deleteOne` does not?
A2: It returns the removed document and supports `sort` and `projection`, atomically — handy for queues, audit logs and "pop" semantics.

Q3: What is the difference between `deleteMany({})` and `drop()`?
A3: `deleteMany({})` deletes documents one by one (oplog entry per document) and keeps the collection with its indexes; `drop()` removes the collection and its indexes at once and is much faster for large collections.

Q4: How can you implement an undo for deletes?
A4: Soft-delete with a `deletedAt`/`isDeleted` flag (and filter on it), move documents into an archive collection, or rely on backups/point-in-time restore. MongoDB has no built-in recycle bin.

Q5: How do you auto-delete expired data?
A5: Create a TTL index (`createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 })`); a background task removes expired documents about every 60 seconds.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `deleteOne` by `_id` for precise removal (cancel order, delete comment).
- `deleteMany` for bulk cleanup with a safe, tested filter.
- `findOneAndDelete` for queues and audit-before-delete.

❌ Avoid when:
- You may need to restore the data — soft delete instead.
- Auto-expiry is the real need — TTL index.
- Wiping an entire large collection — `drop()` is better than `deleteMany({})`.

---

## 📊 Visual Diagram
```
   carts: [ {1,a,old} {2,a,old} {3,b,new} {4,a,new} ]

   deleteOne({u:"a"})      -> removes {1}              deletedCount: 1
   deleteMany({st:"old"})  -> removes {2}              deletedCount: 1
   findOneAndDelete(sort)  -> removes AND returns doc  { _id: 2, p: 9 }
   deleteMany({})          -> docs gone, indexes stay  (collection still exists)
   drop()                  -> collection + indexes gone
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| deleteOne | Remove first matching doc | पहला matching document हटाओ |
| deleteMany | Remove all matching docs | सारे matching documents हटाओ |
| findOneAndDelete | Atomic remove and return | Atomic हटाओ और लौटाओ |
| deletedCount | Number of documents removed | कितने documents हटे |
| Soft delete | Mark deleted instead of removing | हटाने की जगह flag लगाना |
| TTL index | Index that auto-deletes expired docs | Expired docs अपने-आप हटाने वाला index |

---

## ⚡ 3-Line Summary
English:
1. `deleteOne` removes the first match, `deleteMany` all matches, `findOneAndDelete` removes one and returns it atomically.
2. No match gives `deletedCount: 0` (not an error); an empty filter `{}` deletes everything.
3. Deletes are permanent — validate filters, prefer soft delete or TTL when appropriate, use `drop()` to wipe big collections.

Hindi:
1. `deleteOne` पहला match, `deleteMany` सारे matches हटाता है, `findOneAndDelete` एक हटाकर atomically लौटाता है।
2. Match न मिलने पर `deletedCount: 0` (error नहीं); खाली filter `{}` सब कुछ हटा देता है।
3. Delete स्थायी है — filters validate करो, ज़रूरत हो तो soft delete या TTL लो, बड़ी collection साफ़ करने के लिए `drop()` इस्तेमाल करो।

---

## ➡️ Next Topic
**25. bulkWrite — Bulk Operations** — mixing inserts, updates and deletes in a single round trip.
