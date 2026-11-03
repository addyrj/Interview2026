# 11. Capped Collections
# हिंदी में: Capped Collections

---

## 🔵 Simple Definition (English)
A **capped collection** is a fixed-size collection that preserves insertion order and, once full, **overwrites the oldest documents** (circular buffer). You set `size` (bytes, required) and optionally `max` (document count). You should not delete individual documents, and updates must not grow a document.

## 🔵 सरल परिभाषा (Hindi)
**Capped collection** fixed-size collection है जो insertion order बनाए रखती है और भर जाने पर **सबसे पुराने documents को overwrite** कर देती है (circular buffer)। आप `size` (bytes, ज़रूरी) और optional `max` (documents की संख्या) देते हैं। Individual documents delete नहीं कर सकते।

---

## 🔴 Problem it Solves
Logs, recent-activity feeds and caches grow forever unless you prune them. Capped collections give automatic, constant-size, high-throughput storage with natural insertion ordering and no cleanup job.

## 🔴 यह क्यों बना? (Hindi)
Logs, recent-activity feeds और caches बिना pruning के हमेशा बढ़ते रहते हैं। Capped collections automatic, constant-size, high-throughput storage देती हैं, natural insertion ordering के साथ और बिना cleanup job के।

---

## 🟢 How it Works — Step by Step

Step 1 → Create explicitly: `db.createCollection("log", { capped: true, size: 4096, max: 3 })`.
Step 2 → Inserts append to the end of a pre-allocated space.
Step 3 → When size or `max` is reached, the oldest docs are silently removed to make room.
Step 4 → `find()` without sort returns natural (insertion) order; `.sort({$natural:-1})` gives newest first.
Step 5 → Restrictions: individual deletes are unsupported (use `drop`), updates must not increase document size, cannot be sharded. Tailable cursors can follow new inserts.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Explicitly बनाओ: `db.createCollection("log", { capped: true, size: 4096, max: 3 })`।
Step 2 → Inserts pre-allocated जगह के अंत में append होते हैं।
Step 3 → Size या `max` पूरा होने पर सबसे पुराने docs चुपचाप हट जाते हैं।
Step 4 → बिना sort के `find()` natural (insertion) order देता है; `.sort({$natural:-1})` newest first देता है।
Step 5 → पाबंदियाँ: individual deletes supported नहीं, updates से document size नहीं बढ़ना चाहिए, sharding नहीं। Tailable cursors नए inserts को follow कर सकते हैं।

---

## 🟡 Real World Example
A Swiggy rider-tracking service keeps the last 1,000 GPS pings per fleet in a capped collection `recent_pings`; a dashboard uses a tailable cursor to stream new pings. Old pings vanish automatically, so storage never grows. (For time-based retention, a TTL index is the alternative.)

## 🟡 Real Example Hindi mein
Swiggy की rider-tracking service fleet की आख़िरी 1,000 GPS pings capped collection `recent_pings` में रखती है; dashboard नए pings stream करने के लिए tailable cursor इस्तेमाल करता है। पुराने pings अपने आप गायब हो जाते हैं, इसलिए storage नहीं बढ़ता। (Time-based retention के लिए TTL index विकल्प है।)

---

## 💻 Code Example — Basic

```javascript
// mongod 8.0.4, database "mh"
db.createCollection("log", { capped: true, size: 4096, max: 3 })  // keep at most 3 docs (or 4096 bytes)
for (let i = 1; i <= 5; i++) db.log.insertOne({ i })               // insert 5 docs

db.log.find({}, { _id: 0 }).toArray()
// Output: [ { i: 3 }, { i: 4 }, { i: 5 } ]   <- docs 1 and 2 were overwritten

db.log.isCapped()          // Output: true
db.log.stats().max         // Output: 3
```

## 💻 Code Example — Advanced

```javascript
// Newest first
db.log.find().sort({ $natural: -1 })        // reverse insertion order

// Deleting single documents: officially unsupported on capped collections (docs say deletes are not allowed on replica sets/sharded clusters).
// On the standalone mongod 8.0.4 used for testing, deleteOne actually succeeded ({ deletedCount: 1 }) - do not rely on it.
db.log.deleteOne({ i: 5 })

// Convert an existing normal collection to capped
db.runCommand({ convertToCapped: "events", size: 1048576 })   // 1 MB cap, keeps newest data

// Tailable cursor in Node driver (like `tail -f`)
// const cursor = db.collection('log').find({}, { tailable: true, awaitData: true });
// for await (const doc of cursor) console.log(doc);   // waits for new inserts
```
(Verified on the test server: the 5-insert/max-3 behaviour and the standalone deleteOne result. `convertToCapped` and the tailable cursor are documented behaviour, not run.)

---

## 🟠 Express.js / Mongoose Integration

```javascript
const mongoose = require('mongoose');
// Mongoose schema option "capped" creates the collection as capped
const logSchema = new mongoose.Schema(
  { level: String, msg: String },
  { capped: { size: 1024 * 1024, max: 1000 } }   // 1 MB or 1000 docs
);
const Log = mongoose.model('Log', logSchema);
app.get('/logs', async (req, res) => {
  res.json(await Log.find().sort({ $natural: -1 }).limit(20)); // last 20 logs
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting auto-capped by inserting into a missing collection
```javascript
db.log.insertOne({a:1})                                   // Wrong: creates a NORMAL collection
db.createCollection("log", { capped: true, size: 4096 })  // Right: create explicitly first
```

❌ Mistake 2: Forgetting `size` is required (and is rounded up to a multiple of 256 bytes)
✅ Correct: Always specify `size`; `max` is only an extra limit.

❌ Mistake 3: Using it for data you must keep
✅ Correct: Data gets silently overwritten; use a normal collection with TTL or archive instead.

---

## 🧠 Tricky Interview Question
Q: You set `max: 3` and `size: 4096`. Which limit wins?
Answer: Whichever is hit first. With tiny documents `max` (3) triggers first, as shown above. With large documents, the byte `size` fills before `max`.

---

## ⚫ Interview Questions + Answers

Q1: What is a capped collection?
A1: A fixed-size, insertion-ordered collection behaving like a ring buffer.

Q2: Capped vs TTL index?
A2: Capped bounds by size/count and guarantees order; TTL deletes by age but size is unbounded and order is not guaranteed.

Q3: Can you delete documents from it?
A3: Officially no individual deletes (use `drop`); a standalone 8.0.4 test allowed `deleteOne`, but it is unsupported and not replicated safely on replica sets.

Q4: What is a tailable cursor?
A4: A cursor that stays open on a capped collection and returns new documents as they arrive.

Q5: Can a capped collection be sharded?
A5: No.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Logs, recent events, simple queues, caches with fixed size

❌ Avoid when:
- Data must not be lost, you need random deletes, or sharding

---

## 📊 Visual Diagram
```
CAPPED (max=3)
insert 1,2,3   : [1][2][3]
insert 4       : [4][2][3] -> logically [2][3][4]   (1 overwritten)
insert 5       :             logically [3][4][5]   (2 overwritten)
                  oldest ◄──────────────► newest
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Capped | Fixed-size circular collection | Fixed-size circular collection |
| size | Max bytes | अधिकतम bytes |
| max | Max document count | अधिकतम documents |
| $natural | Insertion order sort | Insertion order |
| Tailable cursor | Follows new inserts | नए inserts को follow करने वाला cursor |

---

## ⚡ 3-Line Summary
English:
1. Capped collections are fixed-size ring buffers that keep insertion order.
2. Oldest documents are overwritten; no individual deletes.
3. Great for logs and recent feeds; create them explicitly with `size`.

Hindi:
1. Capped collections fixed-size ring buffers हैं जो insertion order रखती हैं।
2. सबसे पुराने documents overwrite होते हैं; individual delete नहीं।
3. Logs और recent feeds के लिए बढ़िया; `size` के साथ explicitly बनाओ।

---

## ➡️ Next Topic
**12. MongoDB Terminology Cheat — RDBMS to MongoDB mapping**
