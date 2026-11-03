# 25. bulkWrite — Bulk Operations
# हिंदी में: bulkWrite — एक साथ कई write operations

---

## 🔵 Simple Definition (English)
`bulkWrite()` sends **many different write operations** (`insertOne`, `updateOne`, `updateMany`, `replaceOne`, `deleteOne`, `deleteMany`) to the server in a **single request**. It can be **ordered** (stops at first error) or **unordered** (continues past errors, may run in parallel). It returns one summary object with counts (`insertedCount`, `matchedCount`, `modifiedCount`, `deletedCount`, `upsertedCount`).

## 🔵 सरल परिभाषा (Hindi)
`bulkWrite()` कई **अलग-अलग write operations** (`insertOne`, `updateOne`, `updateMany`, `replaceOne`, `deleteOne`, `deleteMany`) को server पर **एक ही request** में भेजता है। यह **ordered** (पहली error पर रुक जाता है) या **unordered** (error के बाद भी आगे चलता है) हो सकता है। वापस एक summary object मिलता है जिसमें counts होते हैं (`insertedCount`, `matchedCount`, `modifiedCount`, `deletedCount`, `upsertedCount`)।

---

## 🔴 Problem it Solves
If you loop over 10,000 inventory changes and call `updateOne` for each, you pay 10,000 network round trips, 10,000 acknowledgements and 10,000 `await`s. That is slow and chatty. `insertMany` only helps for inserts; `updateMany` applies **one same change** to many documents. But real jobs (nightly price sync, stock reconciliation, import of mixed new/changed/removed rows) need **different operations on different documents**. `bulkWrite` batches them: far fewer round trips, one result object, and control over error behaviour.

## 🔴 यह क्यों बना? (Hindi)
अगर 10,000 inventory changes के लिए loop में हर बार `updateOne` चलाओ तो 10,000 network round trips, 10,000 acknowledgements और 10,000 `await` लगेंगे — बहुत slow। `insertMany` सिर्फ insert के लिए है; `updateMany` **एक ही change** कई documents पर लगाता है। पर असली jobs (रात का price sync, stock reconciliation, mixed new/changed/removed rows का import) में **अलग documents पर अलग operations** चाहिए। `bulkWrite` इन्हें batch करता है: कम round trips, एक result object, और error behaviour पर control।

---

## 🟢 How it Works — Step by Step

Step 1 → You build an **array of operation objects**, each shaped `{ opName: { ...args } }`, e.g. `{ updateOne: { filter, update, upsert } }`.
Step 2 → The driver groups consecutive operations of the same type into batches and sends them (a batch is limited by `maxWriteBatchSize` = 100,000 ops and ~16 MB-48 MB message size; the driver splits automatically).
Step 3 → **Ordered (default, `ordered: true`)**: the server runs ops in array order and **stops at the first failure**; later ops are not attempted.
Step 4 → **Unordered (`ordered: false`)**: the server may reorder/parallelise, **continues after errors**, and reports all errors together. Faster, but order-dependent logic is unsafe.
Step 5 → You get a result. On failure the driver throws `MongoBulkWriteError` carrying `result` (what succeeded) and `writeErrors` (what failed and at which `index`).
Step 6 → Each individual op is atomic on its **own** document; the whole bulk is **NOT** a transaction (use a multi-document transaction if you need all-or-nothing).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Operation objects का array** बनाओ, हर एक `{ opName: { ...args } }` shape में, जैसे `{ updateOne: { filter, update, upsert } }`।
Step 2 → Driver एक ही type के लगातार operations को batches में group करके भेजता है (limit `maxWriteBatchSize` = 100,000 ops; बड़े array को driver अपने आप split कर देता है)।
Step 3 → **Ordered (default, `ordered: true`)**: server array के क्रम में चलाता है और **पहली failure पर रुक जाता है**; बाकी ops चलते ही नहीं।
Step 4 → **Unordered (`ordered: false`)**: server क्रम बदल सकता है, **error के बाद भी चलता रहता है**, और सारी errors साथ में बताता है। तेज़ है, पर order पर निर्भर logic के लिए unsafe।
Step 5 → Result मिलता है। Failure पर driver `MongoBulkWriteError` फेंकता है जिसमें `result` (जो सफल हुआ) और `writeErrors` (जो फेल हुआ, किस `index` पर) होते हैं।
Step 6 → हर op अपने **एक document** पर atomic है, पर पूरा bulk **transaction नहीं** है (all-or-nothing चाहिए तो multi-document transaction लो)।

---

## 🟡 Real World Example
**Flipkart's seller inventory sync**: every night a seller uploads a CSV of 50,000 rows. Some SKUs are new (insert), some have changed stock (update), some are discontinued (delete), and some may or may not exist yet (upsert). The import service converts each row into one operation and sends them with `bulkWrite(ops, { ordered: false })` in chunks of 1,000. One bad row (duplicate key) must not block the other 49,999, so unordered is chosen, and the returned `writeErrors` are saved into an "import report" shown to the seller.

## 🟡 Real Example Hindi mein
**Flipkart का seller inventory sync**: हर रात seller 50,000 rows की CSV upload करता है। कुछ SKUs नए (insert), कुछ का stock बदला (update), कुछ बंद हो गए (delete), कुछ शायद मौजूद ही न हों (upsert)। Import service हर row को एक operation में बदलती है और 1,000 के chunks में `bulkWrite(ops, { ordered: false })` भेजती है। एक खराब row (duplicate key) बाकी 49,999 को block न करे, इसलिए unordered चुना जाता है, और लौटे `writeErrors` seller को दिखने वाली "import report" में save होते हैं।

---

## 💻 Code Example — Basic (mongosh, tested on MongoDB 8.0.4)

```javascript
// Use a fresh database for the demo
const d = db.getSiblingDB("shop");        // pick database "shop"
d.dropDatabase();                          // start clean

// ONE call, SEVEN operations of different kinds
const r = d.items.bulkWrite([
  { insertOne:  { document: { _id: 1, name: "Paneer", stock: 10 } } },        // op 0: insert
  { insertOne:  { document: { _id: 2, name: "Naan",   stock: 5  } } },        // op 1: insert
  { updateOne:  { filter: { _id: 1 }, update: { $inc: { stock: -3 } } } },    // op 2: stock 10 -> 7
  { updateMany: { filter: { stock: { $lt: 10 } },                             // op 3: all low-stock docs
                  update: { $set: { low: true } } } },                         //        (Paneer=7, Naan=5)
  { replaceOne: { filter: { _id: 2 },                                         // op 4: replace WHOLE doc
                  replacement: { name: "Butter Naan", stock: 50 } } },
  { deleteOne:  { filter: { _id: 99 } } },                                    // op 5: nothing matches, fine
  { updateOne:  { filter: { _id: 3 }, update: { $set: { name: "Dal" } },      // op 6: no _id 3 -> upsert
                  upsert: true } }
]);
printjson(r);
// Output (real run):
// {
//   acknowledged: true,
//   insertedCount: 2,
//   insertedIds: { '0': 1, '1': 2 },   // key = index of the op in the array
//   matchedCount: 4,                    // updateOne(1) + updateMany(2) + replaceOne(1)
//   modifiedCount: 4,
//   deletedCount: 0,                    // deleteOne matched nothing
//   upsertedCount: 1,
//   upsertedIds: { '6': 3 }             // op #6 created _id 3
// }
```

## 💻 Code Example — Advanced: ordered vs unordered errors

```javascript
// Collection already has _id 1, 2, 3 (from above)

// ORDERED (default): stops at the first error
try {
  d.items.bulkWrite([
    { insertOne: { document: { _id: 1 } } },    // duplicate key -> FAILS here
    { insertOne: { document: { _id: 10 } } },   // never attempted
    { insertOne: { document: { _id: 11 } } }    // never attempted
  ]);
} catch (e) {
  print(e.name, e.result.insertedCount, e.writeErrors.length);
  // MongoBulkWriteError 0 1   -> nothing inserted, 1 error (E11000 duplicate key)
}
print(d.items.countDocuments());   // 3  (unchanged)

// UNORDERED: keeps going after the error
try {
  d.items.bulkWrite(
    [ { insertOne: { document: { _id: 1 } } },    // fails (duplicate)
      { insertOne: { document: { _id: 20 } } } ], // still inserted!
    { ordered: false }                            // <-- the switch
  );
} catch (e) {
  print("unordered", e.result.insertedCount, e.writeErrors.length);
  // unordered 1 1   -> 1 inserted, 1 failed
}
print(d.items.countDocuments());   // 4

// Write concern can be passed too (see topic 27)
// d.items.bulkWrite(ops, { writeConcern: { w: "majority" } });
```

### Node.js driver version (tested with `mongodb` driver)
```javascript
const { MongoClient } = require('mongodb');
const client = new MongoClient('mongodb://127.0.0.1:27017');
await client.connect();
const col = client.db('nodedemo').collection('orders');

const res = await col.bulkWrite([
  { insertOne: { document: { _id: 1, status: 'placed', amt: 500 } } },
  { insertOne: { document: { _id: 2, status: 'placed', amt: 900 } } },
  { updateOne: { filter: { _id: 1 }, update: { $set: { status: 'paid' } } } },
  { deleteOne: { filter: { _id: 2 } } },
], { ordered: true });
console.log(res.insertedCount, res.modifiedCount, res.deletedCount); // 2 1 1

try {
  await col.bulkWrite(
    [{ insertOne: { document: { _id: 1 } } }, { insertOne: { document: { _id: 7 } } }],
    { ordered: false });
} catch (e) {
  // e.name = 'MongoBulkWriteError'; e.result.insertedCount = 1;
  // e.writeErrors[0].err.code = 11000 (duplicate key)
}
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose: Model.bulkWrite — same op shapes, but it applies schema casting/timestamps
const Order = mongoose.model('Order', new mongoose.Schema({ status: String, amt: Number }));

app.post('/api/orders/mark-paid', async (req, res) => {
  const ids = req.body.ids;                         // array of ObjectId strings from client
  // Build ops: one updateOne per id (Mongoose casts string ids to ObjectId for us)
  const ops = ids.map((id) => ({
    updateOne: { filter: { _id: id, status: 'placed' }, update: { $set: { status: 'paid' } } },
  }));
  try {
    const r = await Order.bulkWrite(ops, { ordered: false }); // continue even if one fails
    res.json({ matched: r.matchedCount, modified: r.modifiedCount });
  } catch (e) {
    // partial success: report what worked and which indexes failed
    res.status(207).json({ ok: e.result?.modifiedCount, failed: e.writeErrors?.map((w) => w.index) });
  }
});
// Note: Mongoose bulkWrite skips document middleware (save hooks) and does NOT run validators
// by default for update ops. Test run: updateMany via bulkWrite incremented amt 10->11, 20->21.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming bulkWrite is a transaction
```javascript
// Wrong — thinking that a failure rolls back earlier ops
await col.bulkWrite([{ insertOne: { document: a } }, { insertOne: { document: dup } }]);
// 'a' STAYS inserted if it ran before the error. No rollback.

// Right — wrap in a transaction (needs replica set) when all-or-nothing is required
await session.withTransaction(() => col.bulkWrite(ops, { session }));
```

❌ Mistake 2: Using `ordered: false` when ops depend on each other
✅ Correct: "insert doc, then update that doc" in an unordered bulk may run update first and match nothing. Keep dependent ops in an **ordered** bulk.

❌ Mistake 3: Sending one gigantic array without chunking and ignoring `writeErrors`
✅ Correct: chunk into ~1,000 ops, always inspect `e.writeErrors`/`result`, and log failed `index` values.

---

## 🧠 Tricky Interview Question

```javascript
// _id 1,2,3 exist. What is inserted and what is the error count?
db.items.bulkWrite([
  { insertOne: { document: { _id: 50 } } },
  { insertOne: { document: { _id: 1  } } },   // duplicate
  { insertOne: { document: { _id: 51 } } }
]);
```
Answer: With the default **ordered** mode, `_id: 50` IS inserted (it ran before the failure), `_id: 1` fails with E11000, and `_id: 51` is **never attempted**. Result: `insertedCount: 1`, 1 write error, and the error is thrown (`MongoBulkWriteError`). In **unordered** mode both 50 and 51 would be inserted (`insertedCount: 2`) with 1 error. The trap: people think "all or nothing" - it is neither.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `insertMany`, `updateMany` and `bulkWrite`?
A1: `insertMany` only inserts many documents. `updateMany` applies **one** update to all docs matching **one** filter. `bulkWrite` mixes **different** operation types, each with its own filter/update, in one request.

Q2: Ordered vs unordered bulk — when to choose which?
A2: Ordered (default) when operations depend on one another or you want to stop at first error. Unordered when operations are independent (imports, syncs): the server can continue after errors and may be faster since it can parallelise.

Q3: Is `bulkWrite` atomic?
A3: Each individual operation is atomic on a single document, but the bulk as a whole is not a transaction. Earlier successful ops are not rolled back. Use a multi-document transaction (replica set or sharded cluster) for all-or-nothing.

Q4: What happens if the array has more than 100,000 operations?
A4: The driver automatically splits it into multiple batches (limits: `maxWriteBatchSize` 100,000 and the max BSON message size). You still call `bulkWrite` once, but the result aggregates all batches. In practice chunk to 500-5,000 for memory and clearer error handling.

Q5: How do you report which rows failed?
A5: Catch `MongoBulkWriteError`; `e.writeErrors` is an array where each item has `index` (position in your ops array), `code` (e.g. 11000) and `errmsg`. `e.result` has counts of what succeeded.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Syncing/importing many mixed changes (inventory, prices, ETL jobs)
- You need to reduce round trips for many different writes
- Independent writes where partial success is acceptable (`ordered: false`)

❌ Avoid when:
- You need all-or-nothing semantics (use a transaction)
- It is one identical change for many docs (`updateMany` is simpler)
- You only insert (`insertMany` is clearer)
- You rely on Mongoose `save` middleware/validation (bulkWrite bypasses document hooks)

---

## 📊 Visual Diagram
```
 APP                                         MONGODB SERVER
 ───                                         ──────────────
 ops = [ insertOne, updateOne,   ──ONE──►   run op0 ─► ok
         deleteOne, upsert ... ]  request   run op1 ─► ok
                                            run op2 ─► ERROR
 ORDERED  (default)                         STOP  (op3.. never run)
 UNORDERED ({ordered:false})                run op3 ─► ok   (continues)
                                            run op4 ─► ok
 ◄── one result: { insertedCount, matchedCount, modifiedCount,
                   deletedCount, upsertedCount, writeErrors[] }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| bulkWrite | Many mixed writes in one request | एक request में कई मिले-जुले writes |
| ordered | Stop at first error, keep sequence | पहली error पर रुकना, क्रम बनाए रखना |
| unordered | Continue after errors, may parallelise | error के बाद भी चलना |
| upsert | Update, or insert if no match | match न हो तो insert |
| writeErrors | Array of failed ops with index | फेल ops की list (index सहित) |
| MongoBulkWriteError | Exception holding partial result | partial result वाला exception |
| round trip | One request + response over network | network पर एक आना-जाना |

---

## ⚡ 3-Line Summary
English:
1. `bulkWrite` batches mixed insert/update/replace/delete ops into one request and returns one summary of counts.
2. Ordered stops at the first error, unordered continues; neither is a transaction (no rollback).
3. Catch `MongoBulkWriteError` and read `writeErrors[].index` to know exactly what failed.

Hindi:
1. `bulkWrite` मिले-जुले insert/update/replace/delete ops को एक request में भेजता है और counts का एक summary देता है।
2. Ordered पहली error पर रुकता है, unordered चलता रहता है; कोई भी transaction नहीं है (rollback नहीं)।
3. `MongoBulkWriteError` पकड़ो और `writeErrors[].index` से देखो कि ठीक क्या फेल हुआ।

---

## ➡️ Next Topic
**26. Cursors and Iteration** — how `find()` returns a lazy cursor, batches, and how to iterate large result sets safely.
