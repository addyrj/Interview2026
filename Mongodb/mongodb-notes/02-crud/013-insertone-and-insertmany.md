# 13. insertOne and insertMany
# हिंदी में: insertOne और insertMany

---

## 🔵 Simple Definition (English)
**`insertOne(doc)`** adds a single document to a collection and **`insertMany([docs])`** adds many documents in one command. If the document has no `_id`, MongoDB (the driver) generates an **ObjectId** automatically. If the collection does not exist, the first insert creates it implicitly. Both return an acknowledgement with the inserted `_id` value(s).

## 🔵 सरल परिभाषा (Hindi)
**`insertOne(doc)`** collection में एक document जोड़ता है और **`insertMany([docs])`** एक ही command में कई documents जोड़ता है। अगर document में `_id` नहीं है तो MongoDB (driver) अपने आप **ObjectId** बना देता है। अगर collection मौजूद नहीं है तो पहला insert उसे अपने आप बना देता है। दोनों inserted `_id` के साथ acknowledgement लौटाते हैं।

---

## 🔴 Problem it Solves
Applications constantly create data: a new order, a signup, a batch of 5,000 product rows from a seller's CSV. Doing this one network round trip per record is slow, and without a clear failure model you do not know what happens when row 300 of 1,000 is a duplicate. `insertOne` gives a simple atomic single-document write (a single document write is always atomic in MongoDB). `insertMany` batches many documents into far fewer round trips and lets you choose the failure behaviour with the `ordered` option: stop at the first error, or keep going and report all errors at the end.

## 🔴 यह क्यों बना? (Hindi)
Applications हर समय data बनाते हैं: नया order, नया signup, seller की CSV से 5,000 product rows। हर record के लिए अलग network round trip धीमा है, और failure का नियम साफ़ न हो तो पता नहीं चलता कि 1,000 में से 300वीं row duplicate हो तो क्या होगा। `insertOne` एक document का सरल atomic write देता है (MongoDB में single document write हमेशा atomic होता है)। `insertMany` कई documents को बहुत कम round trips में भेजता है और `ordered` option से तय करने देता है कि पहली error पर रुकना है या आगे चलते रहना है और अंत में सारी errors बतानी हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Client builds the document(s). If `_id` is missing, the driver adds a new `ObjectId` before sending (so the id is known client-side).
Step 2 → The driver sends an `insert` command to the server (`insertMany` splits very large arrays into batches automatically, up to 100,000 docs or 48 MB per batch).
Step 3 → The server checks every unique index (`_id` is always unique) and any collection validation rules.
Step 4 → The document is written to the storage engine (WiredTiger) and the journal; with the default write concern the reply is sent after the primary has it.
Step 5 → You get `{ acknowledged: true, insertedId }` or `{ insertedIds: {0: .., 1: ..} }`.
Step 6 → On error: with `ordered: true` (default) the server stops at the first failing document, documents before it stay inserted. With `ordered: false` the server tries all, and reports every failure together.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client document(s) बनाता है। `_id` न हो तो driver भेजने से पहले नया `ObjectId` जोड़ देता है (इसलिए id client-side पर ही पता होती है)।
Step 2 → Driver server को `insert` command भेजता है (बहुत बड़े arrays को `insertMany` अपने आप batches में बाँट देता है)।
Step 3 → Server हर unique index (`_id` हमेशा unique) और collection validation rules जाँचता है।
Step 4 → Document storage engine (WiredTiger) और journal में लिखा जाता है; default write concern में primary के पास आने के बाद reply जाता है।
Step 5 → तुम्हें `{ acknowledged: true, insertedId }` या `{ insertedIds: {0: .., 1: ..} }` मिलता है।
Step 6 → Error पर: `ordered: true` (default) में server पहले fail होने वाले document पर रुक जाता है, उससे पहले वाले insert रहते हैं। `ordered: false` में server सबको try करता है और सारी failures साथ में बताता है।

---

## 🟡 Real World Example
**Flipkart's seller portal**: a seller uploads a CSV of 2,000 products. The backend calls `insertMany(rows, { ordered: false })`. 1,998 rows insert; 2 rows have a duplicate SKU (unique index) and fail. Because it is unordered, the good rows are not blocked by the bad ones, and the error object lists exactly which rows failed so the seller sees "2 rows rejected: duplicate SKU". With `ordered: true`, one bad row at position 5 would have stopped the whole upload with only 4 products saved.

## 🟡 Real Example Hindi mein
**Flipkart के seller portal** में seller 2,000 products की CSV upload करता है। Backend `insertMany(rows, { ordered: false })` चलाता है। 1,998 rows insert हो जाती हैं; 2 rows में duplicate SKU (unique index) है और वो fail होती हैं। Unordered होने से अच्छी rows बुरी rows की वजह से नहीं रुकतीं, और error object बताता है कि कौन सी rows fail हुईं ताकि seller को दिखे "2 rows rejected: duplicate SKU"। `ordered: true` में 5वीं row की गलती पर पूरा upload सिर्फ़ 4 products के बाद रुक जाता।

---

## 💻 Code Example — Basic

Run on MongoDB 8.0.4 (mongosh). ObjectIds and timestamps differ on every run.

```javascript
// mongosh: switch to (and implicitly create) the "shop" database
use("shop");

// insertOne: add ONE document. We give our own _id so the output is predictable
db.products.insertOne({ _id: 1, name: "Mouse", price: 499 });
// Output: { acknowledged: true, insertedId: 1 }

// insertMany: add MANY documents in one command (an array of documents)
db.products.insertMany([
  { _id: 2, name: "Keyboard", price: 1299, tags: ["usb"] }, // tags array is fine, shapes can differ
  { _id: 3, name: "Monitor", price: 8999 }                  // no tags here, also fine
]);
// Output: { acknowledged: true, insertedIds: { '0': 2, '1': 3 } }

// Without _id, MongoDB creates an ObjectId for you
const r = db.products.insertOne({ name: "Webcam", price: 2499 });
// r.insertedId -> ObjectId('...')  (24 hex chars; differs every run)

// Duplicate _id -> error code 11000
try {
  db.products.insertOne({ _id: 1, name: "dup" }); // _id 1 already exists
} catch (e) {
  print(e.code);    // 11000
  print(e.message); // E11000 duplicate key error collection: shop.products index: _id_ dup key: { _id: 1 }
}
```

## 💻 Code Example — Advanced

```javascript
// ORDERED (default): stops at the first error
try {
  db.products.insertMany([{ _id: 10 }, { _id: 1 }, { _id: 11 }]); // _id 1 is a duplicate
} catch (e) {
  print(e.code);                 // 11000
  print(e.result.insertedCount); // 1  -> only _id 10 was inserted, 11 was NEVER tried
}
// db.products.find({ _id: { $in: [10, 11] } }) -> only _id 10 exists

// UNORDERED: tries every document, reports all failures at the end
try {
  db.products.insertMany([{ _id: 20 }, { _id: 1 }, { _id: 21 }], { ordered: false });
} catch (e) {
  print(e.result.insertedCount); // 2 -> _id 20 AND 21 were inserted
  print(e.writeErrors.length);   // 1 -> only the duplicate _id 1 failed
}

// Write concern: wait until a majority of replica set members have the write
db.orders.insertOne(
  { _id: 100, total: 750 },
  { writeConcern: { w: "majority", wtimeout: 5000 } } // fail the wait after 5 seconds
);
```

Node.js driver (v7.x), verified:

```javascript
const { MongoClient } = require("mongodb");           // official driver
const client = new MongoClient("mongodb://127.0.0.1:27017");
await client.connect();                                // open the connection pool
const c = client.db("shop").collection("p");           // get a collection handle

const r = await c.insertMany([{ _id: 1, n: "a" }, { _id: 2, n: "b" }]);
console.log(r); // { acknowledged: true, insertedCount: 2, insertedIds: { '0': 1, '1': 2 } }

try {
  await c.insertMany([{ _id: 3 }, { _id: 1 }, { _id: 4 }], { ordered: false });
} catch (e) {
  console.log(e.name, e.code);          // MongoBulkWriteError 11000
  console.log(e.result.insertedCount);  // 2  (3 and 4 inserted)
  console.log(e.writeErrors.length);    // 1  (the duplicate)
}
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require("express");
const mongoose = require("mongoose");
const app = express();
app.use(express.json());                                // parse JSON bodies

const Product = mongoose.model("Product", new mongoose.Schema({
  name: { type: String, required: true },               // validation runs BEFORE insert
  price: Number,
}));

// Mongoose create() = insertOne with validation + defaults
app.post("/products", async (req, res) => {
  try {
    const p = await Product.create(req.body);           // validates, then inserts
    res.status(201).json(p);                            // 201 Created
  } catch (e) {
    res.status(400).json({ error: e.message });         // e.g. "Path `name` is required."
  }
});

// Mongoose insertMany with ordered:false = partial success on bulk upload
app.post("/products/bulk", async (req, res) => {
  try {
    const docs = await Product.insertMany(req.body, { ordered: false });
    res.status(201).json({ inserted: docs.length });
  } catch (e) {
    res.status(207).json({ error: e.message });         // 207 = partial result
  }
});
```

Verified: `Product.create({ age: 1 })` rejects with `U validation failed: name: Path \`name\` is required.` and the Express route returned status 400.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Looping `insertOne` for bulk data
```javascript
// Wrong — 5000 network round trips
for (const row of rows) await db.collection("p").insertOne(row);

// Right — one (batched) command
await db.collection("p").insertMany(rows, { ordered: false });
```

❌ Mistake 2: Assuming `insertMany` is all-or-nothing
✅ Correct: It is NOT a transaction. With an error, documents before the failure stay inserted (ordered) or all good ones stay (unordered). Use a multi-document transaction if you need all-or-nothing.

❌ Mistake 3: Passing an object (or empty array) to `insertMany`
```javascript
db.products.insertMany({ name: "x" }); // Wrong — needs an ARRAY
db.products.insertMany([]);            // Wrong — empty array throws an error
```

---

## 🧠 Tricky Interview Question

```javascript
db.t.insertMany([{ _id: 1 }, { _id: 1 }, { _id: 2 }]);              // (a) ordered
db.t.insertMany([{ _id: 3 }, { _id: 3 }, { _id: 4 }], { ordered: false }); // (b) unordered
// Which _id values exist in the collection afterwards?
```
Answer: `1` and `3` and `4`. In (a) the second document fails (duplicate `_id: 1`) and, being ordered, `_id: 2` is never attempted, so only `1` stays. In (b) the duplicate `3` fails but `4` is still inserted, so `3` and `4` exist. Both calls throw a bulk write error even though some documents were inserted, so catching the error does NOT mean "nothing was written".

---

## ⚫ Interview Questions + Answers

Q1: What does `insertOne` return?
A1: An acknowledgement object `{ acknowledged: true, insertedId: <_id> }`. The `insertedId` is the `_id` you supplied or the ObjectId the driver generated.

Q2: What happens if you insert into a collection that does not exist?
A2: MongoDB creates the collection implicitly on the first insert. (Creation can also be explicit with `createCollection` when you need options like validation, capped, or time-series.)

Q3: Difference between ordered and unordered `insertMany`?
A3: Ordered (default) processes documents in sequence and stops at the first error. Unordered continues past errors, can be faster because the server may run it in parallel, and reports all errors together. Choose unordered for bulk imports where independent rows should not block each other.

Q4: Is `insertMany` atomic?
A4: No. Each single document insert is atomic, but the batch as a whole is not. For atomicity across documents use a transaction (needs a replica set or sharded cluster).

Q5: Who generates the ObjectId, server or driver?
A5: The driver generates it client-side before sending (it contains a 4-byte timestamp, 5-byte random value and a 3-byte counter). That is why `insertedId` is available instantly and why ids are roughly time-ordered.

---

## 🔷 When to Use + When Not to Use
✅ Use `insertOne` for single creates (signup, new order). Use `insertMany` for imports, seeding, batch event ingestion, with `ordered: false` when rows are independent.

❌ Avoid `insertMany` when you need all-or-nothing semantics without a transaction, and avoid huge unbounded arrays held in memory (stream and batch ~1,000 at a time instead).

---

## 📊 Visual Diagram
```
insertMany([d1, d2, d3, d4])   where d2 is a duplicate

 ORDERED (default)            UNORDERED {ordered:false}
 ─────────────────            ─────────────────────────
 d1  ✅ inserted               d1  ✅ inserted
 d2  ❌ error -> STOP          d2  ❌ error (recorded)
 d3  ⛔ never tried            d3  ✅ inserted
 d4  ⛔ never tried            d4  ✅ inserted
 result: 1 inserted            result: 3 inserted, 1 writeError
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| insertOne | Insert a single document | एक document insert करना |
| insertMany | Insert an array of documents | Documents की array insert करना |
| ObjectId | Auto-generated 12-byte `_id` | अपने आप बनने वाली 12-byte `_id` |
| ordered | Stop at first error (default true) | पहली error पर रुकना |
| writeErrors | List of per-document failures | हर document की failures की list |
| E11000 | Duplicate key error code | Duplicate key error code |
| writeConcern | How many nodes must confirm | कितने nodes confirm करें |

---

## ⚡ 3-Line Summary
English:
1. `insertOne` adds one document, `insertMany` adds an array; missing `_id` becomes an auto ObjectId and the collection is created on first insert.
2. `ordered: true` stops at the first error, `ordered: false` continues and reports all errors; neither is a transaction.
3. Duplicate keys raise error 11000; use `insertMany` instead of loops for speed.

Hindi:
1. `insertOne` एक document जोड़ता है, `insertMany` array; `_id` न हो तो ObjectId अपने आप बनता है और पहले insert पर collection बन जाती है।
2. `ordered: true` पहली error पर रुकता है, `ordered: false` आगे चलता है और सारी errors बताता है; दोनों transaction नहीं हैं।
3. Duplicate key पर error 11000 आता है; speed के लिए loop की जगह `insertMany` इस्तेमाल करो।

---

## ➡️ Next Topic
**14. find and findOne** — Reading documents back: cursors, filters and returning a single document.
