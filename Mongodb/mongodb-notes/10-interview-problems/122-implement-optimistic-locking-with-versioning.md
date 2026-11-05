# 122. Implement Optimistic Locking with Versioning
# हिंदी में: Versioning के साथ Optimistic Locking लगाना

---

## 🔵 Simple Definition (English)
**Optimistic locking** assumes conflicts are rare. Instead of locking a document while a user edits it, you store a **version number** on the document. When saving you say "update this document *only if* its version is still the one I read", and increment the version in the same atomic update. If someone else changed it first, the update matches 0 documents, and you retry or report a conflict.

## 🔵 सरल परिभाषा (Hindi)
**Optimistic locking** मानता है कि conflicts कम होते हैं। Edit के दौरान document को lock करने की जगह document पर एक **version number** रखा जाता है। Save करते समय कहा जाता है "इस document को *सिर्फ तभी* update करो जब version अब भी वही हो जो मैंने पढ़ा था", और उसी atomic update में version बढ़ा दिया जाता है। अगर किसी और ने पहले बदल दिया तो update 0 documents match करता है, और आप retry करते हैं या conflict बताते हैं।

---

## 🔴 Problem it Solves
The **lost update** problem: two requests read the same document, each computes a new value in application memory, and both write back. The second write silently overwrites the first. We reproduced it: 10 concurrent "decrement stock" calls without any protection left `qty = 99` instead of `90`. Pessimistic locks do not exist in MongoDB at document level across requests, and long-held transactions are expensive. Versioning gives correctness with no lock held.

## 🔴 यह क्यों बना? (Hindi)
**Lost update** समस्या: दो requests एक ही document पढ़ती हैं, हर एक application memory में नई value निकालती है, और दोनों वापस लिखती हैं। दूसरा write चुपचाप पहले को मिटा देता है। हमने इसे reproduce किया: बिना सुरक्षा के 10 concurrent "stock घटाओ" calls के बाद `qty = 90` की जगह `99` रहा। MongoDB में requests के बीच document-level pessimistic lock नहीं होता, और लंबे transactions महँगे हैं। Versioning बिना lock पकड़े सही नतीजा देती है।

---

## 🟢 How it Works — Step by Step

Step 1 -> Every document has a `version` (or Mongoose's `__v`) starting at 0.
Step 2 -> Client reads the document and remembers its `version` (the API often sends it to the browser, or as an `ETag` / `If-Match` header).
Step 3 -> On save, the server runs `updateOne({_id, version: V}, {$set: {...}, $inc: {version: 1}})`. The filter and the increment happen in **one atomic document operation**.
Step 4 -> If `matchedCount === 1` the save won. If `matchedCount === 0`, someone else got in first (or the document is gone).
Step 5 -> On a conflict either **retry** (re-read, re-apply the change, try again, good for counters) or return **HTTP 409 / 412** so the user can review the newer data (good for human edits).
Step 6 -> For pure counters prefer `$inc` directly: it is already atomic and needs no version.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 -> हर document में `version` (या Mongoose का `__v`) होता है, जो 0 से शुरू होता है।
Step 2 -> Client document पढ़ता है और उसका `version` याद रखता है (अक्सर API इसे browser को भेजती है, या `ETag` / `If-Match` header में)।
Step 3 -> Save पर server चलाता है `updateOne({_id, version: V}, {$set: {...}, $inc: {version: 1}})`। Filter और increment **एक atomic document operation** में होते हैं।
Step 4 -> अगर `matchedCount === 1` तो save जीत गया। अगर `matchedCount === 0` तो किसी और ने पहले बदल दिया (या document मौजूद नहीं)।
Step 5 -> Conflict पर या तो **retry** करो (दोबारा पढ़ो, बदलाव फिर लगाओ, counters के लिए अच्छा) या **HTTP 409 / 412** लौटाओ ताकि user नया data देख सके (human edits के लिए अच्छा)।
Step 6 -> सिर्फ counters के लिए सीधे `$inc` बेहतर है: वह पहले से atomic है, version नहीं चाहिए।

---

## 🟡 Real World Example
**Flipkart seller panel:** two staff members of one seller open the same product page. Staff A changes the price to 110 and saves. Staff B (who loaded the page earlier, version 0) changes the price to 90 and clicks Save. Without versioning, B silently overwrites A. With versioning, B's save matches 0 documents and the UI says "This product was changed by someone else. Review the latest version?". No one loses work silently, and no database lock was held while B was thinking.

## 🟡 Real Example Hindi mein
**Flipkart seller panel:** एक seller के दो staff members एक ही product page खोलते हैं। Staff A price 110 करके save करता है। Staff B (जिसने page पहले load किया था, version 0) price 90 करके Save दबाता है। Versioning के बिना B चुपचाप A का बदलाव मिटा देता। Versioning के साथ B का save 0 documents match करता है और UI कहता है "यह product किसी और ने बदल दिया। नया version देखें?"। किसी का काम चुपचाप नहीं खोता, और B के सोचने के दौरान database में कोई lock नहीं रहा।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4 / mongosh.

```javascript
// mongosh --port 27017
const d = db.getSiblingDB("ol");                       // demo database
d.dropDatabase();                                      // start clean
d.products.insertOne({ _id: "p1", name: "Phone", price: 100, __v: 0 }); // version starts at 0

// Two users read the SAME version
const a = d.products.findOne({ _id: "p1" });           // user A reads version 0
const b = d.products.findOne({ _id: "p1" });           // user B reads version 0

// A saves first: filter on the version it read, bump version atomically
let ra = d.products.updateOne(
  { _id: "p1", __v: a.__v },                           // only if nobody changed it
  { $set: { price: 110 }, $inc: { __v: 1 } }           // change + version bump in ONE operation
);
print("A matched", ra.matchedCount);                   // Output: A matched 1

// B tries with the stale version 0
let rb = d.products.updateOne(
  { _id: "p1", __v: b.__v },                           // __v is now 1, so this filter fails
  { $set: { price: 90 }, $inc: { __v: 1 } }
);
print("B matched", rb.matchedCount);                   // Output: B matched 0  -> conflict detected

printjson(d.products.findOne({ _id: "p1" }));
// Output: { _id: 'p1', name: 'Phone', price: 110, __v: 1 }   (A's change survived)

// Variant: get the new document back in the same round trip
d.products.findOneAndUpdate(
  { _id: "p1", __v: 1 },                               // expected version
  { $set: { price: 120 }, $inc: { __v: 1 } },
  { returnDocument: "after" }                          // return the updated doc (null if conflict)
);
// Output: { _id: 'p1', name: 'Phone', price: 120, __v: 2 }
```

## 💻 Code Example — Advanced

```javascript
// optimistic-retry.js — Node driver: retry loop + proof that nothing is lost
const { MongoClient } = require('mongodb');

// Generic helper: read -> compute in JS -> conditional write -> retry on conflict
async function updateWithRetry(col, id, mutate, max = 5) {
  for (let attempt = 1; attempt <= max; attempt++) {
    const doc = await col.findOne({ _id: id });        // 1. read current state + version
    if (!doc) throw new Error('not found');
    const changes = mutate(doc);                       // 2. business logic in application code
    const r = await col.updateOne(
      { _id: id, version: doc.version },               // 3. succeed only if version unchanged
      { $set: changes, $inc: { version: 1 } }
    );
    if (r.matchedCount === 1) return { attempts: attempt }; // won the race
    // else: someone else wrote first -> loop re-reads and tries again
  }
  throw new Error('too much contention');              // give up -> surface 409/503
}

(async () => {
  const c = await MongoClient.connect('mongodb://127.0.0.1:27017'); // connect once
  const col = c.db('ol2').collection('stock');
  await col.deleteMany({});
  await col.insertOne({ _id: 'sku1', qty: 100, version: 0 });

  // 10 concurrent clients each decrement qty by 1
  const res = await Promise.all(
    Array.from({ length: 10 }, () => updateWithRetry(col, 'sku1', (d) => ({ qty: d.qty - 1 }), 50))
  );
  console.log('attempts per client', res.map((r) => r.attempts).sort((a, b) => a - b));
  // Output (varies each run): attempts per client [ 1, 2, 2, 3, 3, 4, 4, 5, 5, 8 ]
  console.log(await col.findOne({ _id: 'sku1' }));
  // Output: { _id: 'sku1', qty: 90, version: 10 }   <- exactly 10 decrements, none lost

  // Contrast: same job WITHOUT the version check
  await col.updateOne({ _id: 'sku1' }, { $set: { qty: 100, version: 0 } });
  await Promise.all(Array.from({ length: 10 }, async () => {
    const d = await col.findOne({ _id: 'sku1' });      // everybody reads about the same qty
    await col.updateOne({ _id: 'sku1' }, { $set: { qty: d.qty - 1 } }); // last write wins
  }));
  console.log((await col.findOne({ _id: 'sku1' })).qty);
  // Output (varies): 99   <- LOST UPDATES, expected 90
  await c.close();                                     // release the pool
})();
```

---

## 🟠 Express.js / Mongoose Integration

Mongoose already has a version key `__v`; with `optimisticConcurrency: true` every `save()` filters on it for you (tested with Mongoose 9.12).

```javascript
const express = require('express');
const mongoose = require('mongoose');

// optimisticConcurrency makes save() check __v for ANY change, not only array changes
const productSchema = new mongoose.Schema(
  { name: String, price: Number },
  { optimisticConcurrency: true }
);
const Product = mongoose.model('Product', productSchema);

const app = express();
app.use(express.json());

// GET returns the document and its version as an ETag header
app.get('/products/:id', async (req, res) => {
  const p = await Product.findById(req.params.id);
  if (!p) return res.sendStatus(404);
  res.set('ETag', String(p.__v));                      // client must send it back on update
  res.json(p);
});

// PUT requires If-Match: <version>
app.put('/products/:id', async (req, res) => {
  const expected = Number(req.get('If-Match'));        // version the client saw
  if (Number.isNaN(expected)) return res.status(428).json({ error: 'If-Match required' });
  try {
    const p = await Product.findOne({ _id: req.params.id, __v: expected }); // load exactly that version
    if (!p) return res.status(412).json({ error: 'Stale version, reload' }); // 412 Precondition Failed
    p.price = req.body.price;
    await p.save();                                    // Mongoose adds a __v filter and increments it
    res.set('ETag', String(p.__v)).json(p);
  } catch (e) {
    // thrown when another request saved between our findOne and save
    if (e.name === 'VersionError') return res.status(409).json({ error: 'Conflict, retry' });
    throw e;
  }
});
```

Tested output of two stale saves:
```
A saved, __v = 1
VersionError - No matching document found for id "<ObjectId>" version 0 modifiedPaths "price"
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Read, then write without the version in the filter
```javascript
// Wrong — classic lost update (we measured qty 99 instead of 90)
const d = await col.findOne({ _id });
await col.updateOne({ _id }, { $set: { qty: d.qty - 1 } });

// Right — either atomic $inc (no version needed) ...
await col.updateOne({ _id }, { $inc: { qty: -1 } });
// ... or a version-guarded update when logic must run in app code
await col.updateOne({ _id, version: d.version }, { $set: { qty: compute(d) }, $inc: { version: 1 } });
```

❌ Mistake 2: Incrementing the version in a separate update
✅ Correct: filter, change and `$inc` of the version MUST be in the same `updateOne`; two operations leave a gap where another writer slips in.

❌ Mistake 3: Ignoring `matchedCount`
```javascript
// Wrong — treats "0 documents updated" as success
await col.updateOne({ _id, version }, { $set: x, $inc: { version: 1 } });
res.json({ ok: true });

// Right — check the result
const r = await col.updateOne({ _id, version }, { $set: x, $inc: { version: 1 } });
if (r.matchedCount === 0) return res.status(409).json({ error: 'conflict' });
```

❌ Mistake 4: Infinite retry loop
✅ Correct: cap attempts (5 to 10) and add small random backoff; heavy contention means optimistic locking is the wrong tool for that document.

---

## 🧠 Tricky Interview Question

"MongoDB single-document writes are already atomic. So why do we need version checks at all?"

Answer: Atomicity only guarantees that *one* update operation is applied all-or-nothing. It does not protect the *read-modify-write cycle* that happens in your application between two separate operations. Two clients can both read `qty = 100`, and each writes `99`; both writes are atomic and both succeed, yet one decrement is lost (we measured 99 instead of 90). Fixes: use a single atomic operator (`$inc`), or put the expected version in the filter so the write succeeds only if the state you based your decision on is still current. Multi-document transactions also help but cost more and still need retry logic for `TransientTransactionError`.

---

## ⚫ Interview Questions + Answers

Q1: Optimistic vs pessimistic locking?
A1: Pessimistic locks the record up front, so others wait (safe with heavy contention, but risks deadlocks and slow throughput). Optimistic takes no lock, detects conflicts at write time and retries or fails. MongoDB has no user-level row locks, so optimistic locking with a version field is the standard application-level approach.

Q2: What does Mongoose `__v` do by default, and what is `optimisticConcurrency`?
A2: By default `__v` is only checked when you modify arrays (positional changes could corrupt). Setting `optimisticConcurrency: true` makes every `save()` include `__v` in the filter and increment it, throwing `VersionError` on a conflict. Note it does not apply to `updateOne`/`findOneAndUpdate` query calls; those need a manual version filter.

Q3: How do you expose it in a REST API?
A3: Send the version as an `ETag`, require `If-Match` on `PUT/PATCH`, and return `412 Precondition Failed` (or 409) on mismatch and `428 Precondition Required` if the header is missing.

Q4: When should you retry automatically and when return an error?
A4: Retry when the change can be recomputed safely from the fresh document (counters, appending to a list, setting a derived field). Return a conflict to the user when a human made a decision from stale data (editing a price or description), because blind retry would overwrite their colleague's work.

Q5: Can a timestamp (`updatedAt`) replace the version number?
A5: It is risky. Two updates inside the same millisecond have equal timestamps, and clocks differ between servers. A monotonically increasing integer incremented with `$inc` is exact. Using an `ObjectId`/UUID "etag" regenerated on each write also works, but integers are easy to read and debug.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Humans edit shared documents (profiles, product pages, settings, CMS content)
- Conflicts are rare, so retries are rare
- You want correctness without holding transactions open during user think time

❌ Avoid when:
- Simple counters or flags: use `$inc` / `$set` / `$push` directly
- A single hot document updated by hundreds of clients per second (retry storm); shard the counter into buckets or use a queue
- You need to change several documents together: use a transaction (and still keep versions if humans edit)

---

## 📊 Visual Diagram
```
OPTIMISTIC LOCKING WITH A VERSION FIELD
────────────────────────────────────────────────────
 Document in DB:  { _id:"p1", price:100, __v:0 }

 Client A                         Client B
 read  (__v=0)                    read  (__v=0)
   │                                │
   ▼                                │
 updateOne({_id,__v:0},             │
  {$set:{price:110},$inc:{__v:1}})  │
   │ matched 1  -> DB: __v=1        │
   ▼                                ▼
 success                        updateOne({_id,__v:0}, ...)
                                  │ matched 0   (DB is at __v=1)
                                  ▼
                              CONFLICT -> re-read & retry
                                          or 409 / 412 to user
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lost update | Later write overwrites earlier one unseen | बाद का write पहले को चुपचाप मिटा दे |
| Optimistic locking | Detect conflicts at write time | Write के समय conflict पकड़ना |
| Pessimistic locking | Lock first, then work | पहले lock, फिर काम |
| Version key (`__v`) | Counter changed on every write | हर write पर बदलने वाला counter |
| matchedCount | Documents matching the update filter | Filter से match हुए documents |
| ETag / If-Match | HTTP headers carrying the version | Version ले जाने वाले HTTP headers |
| VersionError | Mongoose error on stale save | Stale save पर Mongoose error |

---

## ⚡ 3-Line Summary
English:
1. Put the expected `version` in the update filter and `$inc` it in the same atomic update; `matchedCount === 0` means conflict.
2. Retry for recomputable changes (counters), return 409/412 when a human edited stale data.
3. For plain counters use `$inc`; in Mongoose enable `optimisticConcurrency: true`.

Hindi:
1. Update filter में expected `version` रखो और उसी atomic update में `$inc` करो; `matchedCount === 0` का मतलब conflict।
2. दोबारा निकल सकने वाले बदलावों (counters) में retry करो, human ने stale data पर edit किया हो तो 409/412 लौटाओ।
3. सादे counters के लिए `$inc` इस्तेमाल करो; Mongoose में `optimisticConcurrency: true` चालू करो।

---

## ➡️ Next Topic
**123. Full-text Search + Autocomplete** — text indexes, relevance scoring and prefix autocomplete.
