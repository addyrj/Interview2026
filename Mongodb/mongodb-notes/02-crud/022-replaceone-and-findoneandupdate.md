# 22. replaceOne and findOneAndUpdate
# हिंदी में: replaceOne और findOneAndUpdate

---

## 🔵 Simple Definition (English)
**`replaceOne(filter, replacement)`** swaps the **entire document** (except `_id`) with a new one — fields not in the replacement are **deleted**. **`findOneAndUpdate(filter, update, options)`** updates one document **and returns it** (the old or the new version) in a single **atomic** operation. Its siblings are `findOneAndReplace` and `findOneAndDelete`. Unlike `updateOne`, which only reports counts, the `findOneAnd*` methods hand you the document.

## 🔵 सरल परिभाषा (Hindi)
**`replaceOne(filter, replacement)`** **पूरे document** को (सिवाय `_id`) नए document से बदल देता है — जो fields replacement में नहीं हैं वो **हट जाते हैं**। **`findOneAndUpdate(filter, update, options)`** एक document को update करता है **और उसे return करता है** (पुराना या नया version) — एक **atomic** operation में। इसके भाई-बहन हैं `findOneAndReplace` और `findOneAndDelete`। `updateOne` सिर्फ counts बताता है, जबकि `findOneAnd*` methods document भी देते हैं।

---

## 🔴 Problem it Solves
1. **Full overwrite**: sometimes an API says "here is the new full profile" (HTTP `PUT`). With `$set` you would have to list every field and still not remove the stale ones. `replaceOne` makes the stored document exactly equal to what you send.
2. **Read-after-write race**: to claim a job from a queue, "find a queued job, then mark it running" as two calls lets two workers grab the same job. `findOneAndUpdate` does find + update **atomically** and returns the claimed job, so exactly one worker wins.
3. **Counters / invoice numbers**: `$inc` + return new value in one trip — no gaps, no duplicates.

## 🔴 यह क्यों बना? (Hindi)
1. **Full overwrite**: कभी API कहती है "ये रहा पूरा नया profile" (HTTP `PUT`)। `$set` से हर field लिखनी पड़ेगी और पुरानी stale fields फिर भी नहीं हटेंगी। `replaceOne` stored document को ठीक वैसा बना देता है जैसा आपने भेजा।
2. **Read-after-write race**: queue से job claim करने के लिए "queued job ढूँढो, फिर running mark करो" दो calls में करने पर दो workers एक ही job उठा सकते हैं। `findOneAndUpdate` find + update **atomically** करता है और claimed job लौटाता है, इसलिए सिर्फ एक worker जीतता है।
3. **Counters / invoice numbers**: `$inc` + नई value एक ही trip में — न gap, न duplicate।

---

## 🟢 How it Works — Step by Step

Step 1 → **replaceOne**: MongoDB finds the first document matching `filter`.
Step 2 → It writes the replacement document in its place. `_id` is kept (it is immutable). Every other old field is gone.
Step 3 → The replacement must be a plain document — **no `$set`-style operators**, or you get "Replacement document must not contain atomic operators". It also must not try to change `_id`.
Step 4 → **findOneAndUpdate**: MongoDB picks the first matching document (use `sort` to choose which one), applies the update operators and returns the document.
Step 5 → By default the **old** (pre-update) document is returned; pass `returnDocument: "after"` (Node/mongosh) to get the new one. `projection` limits returned fields; `upsert: true` creates if none match. If nothing matches the result is `null`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **replaceOne**: MongoDB `filter` से match होने वाला पहला document ढूँढता है।
Step 2 → उसकी जगह replacement document लिख देता है। `_id` बनी रहती है (वो immutable है)। बाकी हर पुरानी field ग़ायब।
Step 3 → Replacement साधारण document होना चाहिए — **`$set` जैसे operators नहीं**, वरना "Replacement document must not contain atomic operators"। `_id` बदलने की कोशिश भी नहीं कर सकते।
Step 4 → **findOneAndUpdate**: MongoDB पहला matching document चुनता है (कौन-सा चुनना है इसके लिए `sort` दो), update operators लगाता है और document लौटाता है।
Step 5 → Default में **पुराना** (update से पहले का) document मिलता है; नया चाहिए तो `returnDocument: "after"` दो। `projection` fields सीमित करता है; `upsert: true` हो तो न मिलने पर बनाता है। कोई match न हो तो result `null`।

---

## 🟡 Real World Example
**Razorpay-style payout queue**: a worker process runs `findOneAndUpdate({ status: "queued" }, { $set: { status: "processing", worker: "w-7" } }, { sort: { priority: -1 } })`. Ten workers poll at once, yet each payout is handed to exactly one worker, highest priority first. For the merchant profile page, the dashboard sends the whole edited profile and the backend stores it with `replaceOne` so removed fields (like an old GST number) really disappear.

## 🟡 Real Example Hindi mein
**Razorpay जैसी payout queue**: एक worker `findOneAndUpdate({ status: "queued" }, { $set: { status: "processing", worker: "w-7" } }, { sort: { priority: -1 } })` चलाता है। दस workers एक साथ poll करें, फिर भी हर payout सिर्फ एक worker को मिलता है, सबसे ऊँची priority पहले। Merchant profile page में dashboard पूरा edited profile भेजता है और backend उसे `replaceOne` से रखता है, ताकि हटाई गई fields (जैसे पुराना GST number) सच में ग़ायब हो जाएँ।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4, mongosh.

```javascript
use pay_demo                                       // switch database
db.users.drop()                                    // clean start
db.users.insertOne({ _id: 1, name: "Riya", city: "Pune", wallet: 100, tags: ["a"] })

// replaceOne — whole document replaced, only _id survives
db.users.replaceOne(
  { _id: 1 },                                      // which document
  { name: "Riya S", city: "Delhi" }                // the new full body (no wallet, no tags!)
)
// Output: { acknowledged: true, insertedId: null, matchedCount: 1, modifiedCount: 1, upsertedCount: 0 }
db.users.findOne({ _id: 1 })
// Output: { _id: 1, name: 'Riya S', city: 'Delhi' }   <- wallet and tags are GONE

// Operators are not allowed inside a replacement
db.users.replaceOne({ _id: 1 }, { $set: { a: 1 } })
// Error: Replacement document must not contain atomic operators

// _id is immutable
db.users.replaceOne({ _id: 1 }, { _id: 2, name: "x" })
// Error: After applying the update, the (immutable) field '_id' was found to have been altered to _id: 2

// findOneAndUpdate — claim the highest priority queued job
db.jobs.insertMany([{ _id: 1, s: "queued", p: 1 }, { _id: 2, s: "queued", p: 5 }])
db.jobs.findOneAndUpdate(
  { s: "queued" },                                 // filter
  { $set: { s: "running" } },                      // update
  { sort: { p: -1 } }                              // pick priority 5 first
)
// Output (OLD doc by default): { _id: 2, s: 'queued', p: 5 }

db.jobs.findOneAndUpdate(
  { s: "queued" }, { $set: { s: "running" } },
  { sort: { p: -1 }, returnDocument: "after" }     // return the NEW version
)
// Output: { _id: 1, s: 'running', p: 1 }          <- id 2 is already running, so next queued is id 1

db.jobs.findOneAndUpdate({ s: "zzz" }, { $set: { s: "x" } })
// Output: null                                    <- nothing matched
```

## 💻 Code Example — Advanced

```javascript
// mongosh — projection, findOneAndReplace, and an auto-increment counter
db.jobs.findOneAndUpdate(
  { _id: 2 },
  { $set: { s: "done" } },
  { projection: { s: 1, _id: 0 }, returnDocument: "after" } // return only "s"
)
// Output: { s: 'done' }

db.jobs.findOneAndReplace(
  { _id: 1 },                                      // find
  { s: "replaced" },                               // full replacement
  { returnDocument: "after" }                      // return the replacement
)
// Output: { _id: 1, s: 'replaced' }

// Invoice-number generator: atomic, gap-free per call, creates the counter on first use
db.counters.findOneAndUpdate(
  { _id: "invoice" },                              // one counter document per sequence
  { $inc: { seq: 1 } },                            // add 1
  { upsert: true, returnDocument: "after" }        // create if missing, return new value
)
// Output (first call): { _id: 'invoice', seq: 1 }  (then 2, 3, ...)
```

```javascript
// Node.js driver v6 — NOTE: v6 returns the document directly (v5 and older returned { value })
const { MongoClient } = require('mongodb');
async function claimJob(db, workerId) {
  const job = await db.collection('jobs').findOneAndUpdate(
    { status: 'queued' },                          // only queued jobs
    { $set: { status: 'processing', worker: workerId, startedAt: new Date() } },
    { sort: { priority: -1 }, returnDocument: 'after' } // highest priority, return updated doc
  );
  return job;                                      // null when queue is empty
}
```

---

## 🟠 Express.js / Mongoose Integration

Tested against MongoDB 8.0.4, Mongoose 8, Express 5.

```javascript
const express = require('express');
const mongoose = require('mongoose');
const User = mongoose.model('User', new mongoose.Schema({ name: String, city: String }));
const app = express();
app.use(express.json());

// PUT = full replace (idempotent)
app.put('/users/:id', async (req, res) => {
  const r = await User.replaceOne({ _id: req.params.id }, req.body); // body becomes the whole doc
  if (!r.matchedCount) return res.status(404).json({ error: 'not found' });
  res.json({ replaced: r.modifiedCount });
});

// PATCH-like with the updated doc returned
app.put('/orders/:id', async (req, res) => {
  const o = await Order.findOneAndUpdate(
    { _id: req.params.id },
    { $set: { customer: req.body.customer } },
    { returnDocument: 'after' }          // Mongoose 8: prefer this over the deprecated { new: true }
  );
  if (!o) return res.status(404).json({ error: 'not found' });
  res.json(o);
});
// Real run -> 200 {"_id":"6ae9...","customer":"Aman K"}
```
Mongoose also warns: "the `new` option for `findOneAndUpdate()` is deprecated. Use `returnDocument: 'after'` instead." Also note that `User.replaceOne` still applies schema casting but **not** full validators unless you pass `runValidators: true`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `replaceOne` when you meant `$set`
```javascript
// Wrong — wipes wallet and tags
db.users.replaceOne({ _id: 1 }, { city: "Delhi" })

// Right — change just one field
db.users.updateOne({ _id: 1 }, { $set: { city: "Delhi" } })
```

❌ Mistake 2: Forgetting `returnDocument: "after"` and wondering why you see stale data
```javascript
// Wrong — returns the OLD document
const doc = await col.findOneAndUpdate({ _id: 1 }, { $inc: { seq: 1 } });
// Right
const doc2 = await col.findOneAndUpdate({ _id: 1 }, { $inc: { seq: 1 } }, { returnDocument: 'after' });
```

❌ Mistake 3: Two-step "find then update" claiming
```javascript
// Wrong — race: two workers can both read the same queued job
const j = await jobs.findOne({ status: 'queued' });
await jobs.updateOne({ _id: j._id }, { $set: { status: 'running' } });
// Right — one atomic step
const j2 = await jobs.findOneAndUpdate({ status: 'queued' }, { $set: { status: 'running' } });
```

---

## 🧠 Tricky Interview Question

```javascript
db.jobs.findOneAndUpdate({ s: "queued" }, { $set: { s: "running" } })
```
Two documents match. Which one is updated, and what is returned?

Answer: Without `sort` the choice follows natural order (typically insertion order, but **not guaranteed**) — so always specify `sort` when the choice matters. The call returns the **pre-update** document unless `returnDocument: "after"` is passed. Another trap: in driver v5 and older the result was `{ value, ok, lastErrorObject }`; in v6 it is the document itself (or `null`).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `replaceOne` and `updateOne`?
A1: `updateOne` modifies fields using update operators (`$set`, `$inc` ...) and leaves the other fields intact. `replaceOne` takes a plain document and replaces everything except `_id`; unmentioned fields are removed.

Q2: Why is `findOneAndUpdate` preferred over `findOne` + `updateOne` for queues?
A2: It is atomic on the single document: the match and the write happen under one lock/operation, so two concurrent workers can never claim the same document.

Q3: How do you get the updated document back?
A3: Pass `returnDocument: "after"` (older drivers used `new: true` / `returnNewDocument: true`). The default is `"before"`.

Q4: Can `findOneAndUpdate` update many documents?
A4: No, only one — the first match in the sort order. Use `updateMany` for multiple documents (it cannot return them).

Q5: Is `replaceOne` atomic? What about `_id`?
A5: Yes, a single-document write is atomic. `_id` cannot change; if the replacement omits `_id` the old one is kept, and if it contains a different one the operation fails.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `replaceOne`: HTTP PUT semantics, importing a corrected full document, resetting a document to a known shape.
- `findOneAndUpdate`: job queues, counters, "claim this resource", returning the updated document to the client in one trip.

❌ Avoid when:
- Only one field changes and others may be edited concurrently — use `$set`, otherwise you overwrite a concurrent edit.
- You need to change many documents — use `updateMany`.
- You only need counts — `updateOne` is lighter than returning documents.

---

## 📊 Visual Diagram
```
 replaceOne({_id:1}, {name:"Riya S", city:"Delhi"})

 BEFORE: { _id:1, name:"Riya", city:"Pune", wallet:100, tags:["a"] }
                          │ whole body swapped
 AFTER : { _id:1, name:"Riya S", city:"Delhi" }      (wallet, tags removed)

 findOneAndUpdate (atomic)
   Worker A ─┐                  ┌─ gets job #2 (priority 5)
   Worker B ─┼─> [find+update] ─┤
   Worker C ─┘                  └─ gets job #1 ... never the same job twice
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| replaceOne | Replace whole document except `_id` | `_id` छोड़कर पूरा document बदलना |
| findOneAndUpdate | Atomic find + update, returns a document | Atomic find + update, document लौटाता है |
| returnDocument | `"before"` (default) or `"after"` | पहले का या बाद का version |
| sort option | Chooses which match is processed | कौन-सा match चुना जाए |
| projection | Limits fields returned | लौटाई जाने वाली fields सीमित करना |
| Atomic | Happens fully or not at all | पूरा होता है या बिल्कुल नहीं |

---

## ⚡ 3-Line Summary
English:
1. `replaceOne` overwrites the whole document except `_id`; use `$set` via `updateOne` for partial changes.
2. `findOneAndUpdate` is an atomic find+update that returns the document (old by default, new with `returnDocument: "after"`).
3. Always add `sort` when several documents can match, and use these for queues and counters.

Hindi:
1. `replaceOne` `_id` को छोड़कर पूरा document बदल देता है; आंशिक बदलाव के लिए `updateOne` + `$set` इस्तेमाल करो।
2. `findOneAndUpdate` atomic find+update है जो document लौटाता है (default में पुराना, `returnDocument: "after"` से नया)।
3. जब कई documents match हो सकें तो `sort` ज़रूर दो, और queues व counters के लिए यही इस्तेमाल करो।

---

## ➡️ Next Topic
**23. upsert in MongoDB** — update-or-insert in one call, `$setOnInsert`, and avoiding duplicate documents.
