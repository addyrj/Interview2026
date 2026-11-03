# 51. Query Optimization Checklist
# हिंदी में: Query Optimization Checklist

---

## 🔵 Simple Definition (English)
A **query optimization checklist** is a repeatable routine to find and fix slow MongoDB queries: measure first (profiler / `explain("executionStats")`), check that the right index is used, make `docsExamined` close to `nReturned`, avoid blocking sorts, project only needed fields, paginate properly, and re-measure. The core metric is the **examined-to-returned ratio**.

## 🔵 सरल परिभाषा (Hindi)
**Query optimization checklist** धीमी MongoDB queries ढूँढने और ठीक करने का दोहराया जा सकने वाला तरीका है: पहले measure करो (profiler / `explain("executionStats")`), check करो कि सही index use हो रहा है, `docsExamined` को `nReturned` के पास लाओ, blocking sort से बचो, सिर्फ ज़रूरी fields project करो, सही pagination करो, और फिर दोबारा measure करो। मुख्य metric है **examined-to-returned ratio**।

---

## 🔴 Problem it Solves
Slow queries are usually fixed by guessing: "add an index on everything." That bloats memory, slows writes, and often does not help. Without a checklist, teams optimise the wrong query, trust `winningPlan` without reading the stats, or miss simple wins like `limit`, projection and `_id: 0`. A disciplined order of checks gives the biggest win for the least effort and prevents regressions.

## 🔴 यह क्यों बना? (Hindi)
Slow queries अक्सर अंदाज़े से ठीक की जाती हैं: "हर field पर index लगा दो।" इससे memory बढ़ती है, writes धीमे होते हैं और अक्सर फायदा भी नहीं होता। Checklist न हो तो team गलत query optimize करती है, stats पढ़े बिना `winningPlan` पर भरोसा करती है, या `limit`, projection और `_id: 0` जैसी आसान जीत छोड़ देती है। सही क्रम में checks करने से कम मेहनत में सबसे बड़ा फायदा मिलता है और regression भी रुकते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **Find** the slow query: profiler (`system.profile`), Atlas Performance Advisor, or app logs. Don't optimise what isn't slow.
Step 2 → **Explain** it: `explain("executionStats")`. Read `executionTimeMillis`, `totalKeysExamined`, `totalDocsExamined`, `nReturned`, and the stage tree.
Step 3 → **Check the stage**: `COLLSCAN` on a big collection = missing index. `SORT` = blocking in-memory sort. `FETCH` after `IXSCAN` with a big gap between keys and docs = non-selective or non-covering index.
Step 4 → **Fix the index** using ESR (Equality, Sort, Range). One compound index usually beats several single-field ones.
Step 5 → **Reduce work**: project only needed fields (`_id: 0` for covered), `limit()`, use range-based pagination instead of large `skip()`, `$match` early in pipelines.
Step 6 → **Re-measure** with the same query. Compare before/after. Drop unused indexes (`$indexStats`).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → धीमी query **ढूँढो**: profiler (`system.profile`), Atlas Performance Advisor, या app logs। जो धीमा नहीं उसे optimize मत करो।
Step 2 → उसे **Explain** करो: `explain("executionStats")`। `executionTimeMillis`, `totalKeysExamined`, `totalDocsExamined`, `nReturned` और stage tree पढ़ो।
Step 3 → **Stage देखो**: बड़ी collection पर `COLLSCAN` = index missing। `SORT` = blocking in-memory sort। `IXSCAN` के बाद `FETCH` और keys-docs में बड़ा gap = index selective या covering नहीं।
Step 4 → **Index ठीक करो** ESR (Equality, Sort, Range) से। एक compound index आमतौर पर कई single-field indexes से बेहतर होता है।
Step 5 → **काम घटाओ**: ज़रूरी fields ही project करो (covered के लिए `_id: 0`), `limit()`, बड़े `skip()` की जगह range-based pagination, pipeline में `$match` जल्दी।
Step 6 → उसी query को **दोबारा measure** करो। before/after तुलना करो। अनुपयोगी indexes हटाओ (`$indexStats`)।

---

## 🟡 Real World Example
**Flipkart's "My Orders" page** was taking 1.8 seconds for heavy buyers. The checklist found: (1) `COLLSCAN` over 40M orders for `{ userId }`; (2) a blocking `SORT` on `createdAt`; (3) full documents (with huge item arrays) returned although the list shows only 5 fields; (4) page 50 of results using `skip(500)`. Fixes: compound index `{ userId: 1, createdAt: -1 }`, projection of 5 fields, `limit(10)`, and cursor pagination using `createdAt < lastSeen`. The page dropped to ~15 ms.

## 🟡 Real Example Hindi mein
**Flipkart का "My Orders" page** heavy buyers के लिए 1.8 second ले रहा था। Checklist से मिला: (1) `{ userId }` पर 4 करोड़ orders का `COLLSCAN`; (2) `createdAt` पर blocking `SORT`; (3) पूरे documents (बड़े item arrays समेत) return हो रहे थे जबकि list में सिर्फ 5 fields दिखते हैं; (4) page 50 के लिए `skip(500)`। Fix: compound index `{ userId: 1, createdAt: -1 }`, 5 fields का projection, `limit(10)`, और `createdAt < lastSeen` से cursor pagination। Page ~15 ms पर आ गया।

---

## 💻 Code Example — Basic

Dataset: `shop.orders` (5000 docs). Tested on MongoDB 8.0.4. Timings vary; counts below are real.

```javascript
// mongosh
use shop

// STEP 1-2: measure the slow query (no index on userId yet)
let e = db.orders.find({ userId: 7 }).explain("executionStats")
e.queryPlanner.winningPlan.stage     // Output: 'COLLSCAN'     -> red flag
e.executionStats.totalDocsExamined   // Output: 5000
e.executionStats.nReturned           // Output: 50   -> ratio 100:1, bad

// STEP 4: add an index that serves filter + sort (ESR: equality userId, sort createdAt)
db.orders.createIndex({ userId: 1, createdAt: -1 })
// Output: 'userId_1_createdAt_-1'

// STEP 5: add limit so the index can stop early
e = db.orders.find({ userId: 7 }).sort({ createdAt: -1 }).limit(3).explain("executionStats")
e.queryPlanner.winningPlan.stage     // Output: 'LIMIT'  (no SORT stage = no in-memory sort)
e.executionStats.totalKeysExamined   // Output: 3
e.executionStats.totalDocsExamined   // Output: 3
e.executionStats.nReturned           // Output: 3     -> ratio 1:1, ideal

// Sorting on a non-indexed field brings back a blocking SORT
e = db.orders.find({ userId: 7 }).sort({ amount: -1 }).explain("executionStats")
e.queryPlanner.winningPlan.stage     // Output: 'SORT'
```

## 💻 Code Example — Advanced

```javascript
// Advanced: range-based (keyset) pagination vs skip(), and finding unused indexes
use shop

// BAD for deep pages: skip() still walks and discards the first N index entries
db.orders.find({ userId: 7 }).sort({ createdAt: -1 }).skip(40).limit(10)

// GOOD: remember the last createdAt of the previous page and continue from there
const lastSeen = ISODate("2025-01-10T00:00:00Z")   // sent back by the client as a cursor
db.orders.find(
  { userId: 7, createdAt: { $lt: lastSeen } }      // range starts where the last page ended
).sort({ createdAt: -1 }).limit(10)                // same index, constant cost per page

// Index usage statistics: which indexes are actually used?
db.orders.aggregate([{ $indexStats: {} }])         // per-index "accesses.ops" counters
// An index with ops: 0 after weeks of traffic is a candidate to drop (hide it first):
db.orders.hideIndex("userId_1_createdAt_-1")       // hidden = ignored by planner, still maintained
db.orders.unhideIndex("userId_1_createdAt_-1")     // restore it if latency worsens

// Aggregation tip: put $match (and $sort) FIRST so indexes are usable
db.orders.aggregate([
  { $match: { city: "Pune", status: "delivered" } }, // uses an index
  { $group: { _id: "$userId", spent: { $sum: "$amount" } } },
])

// Cap runaway queries in the application
db.orders.find({ city: "Delhi" }).maxTimeMS(200)   // server aborts if it takes > 200 ms
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');

const orderSchema = new mongoose.Schema({
  userId: Number, city: String, status: String, amount: Number, createdAt: Date,
}, { collection: 'orders' });
orderSchema.index({ userId: 1, createdAt: -1 }); // ESR index lives next to the schema

const Order = mongoose.model('Order', orderSchema);
const app = express();

// Optimised list endpoint: index-backed filter+sort, projection, lean, cursor pagination
app.get('/api/my-orders', async (req, res) => {
  const filter = { userId: Number(req.query.userId) };
  if (req.query.before) filter.createdAt = { $lt: new Date(req.query.before) }; // keyset cursor
  const rows = await Order.find(filter)
    .select('orderId amount status createdAt') // only what the UI shows
    .sort({ createdAt: -1 })
    .limit(10)                                  // never return unbounded lists
    .maxTimeMS(500)                             // protect the DB from slow requests
    .lean();                                    // plain objects: less CPU
  res.json({ rows, next: rows.length ? rows[rows.length - 1].createdAt : null });
});

mongoose.connect('mongodb://127.0.0.1:27017/shop').then(() => app.listen(3000));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Optimising without measuring
```javascript
// Wrong — add random indexes and hope
db.orders.createIndex({ amount: 1 }); db.orders.createIndex({ status: 1 }); db.orders.createIndex({ city: 1 })

// Right — explain first, then add the ONE compound index the query needs
db.orders.find({ city: "Delhi", status: "placed" }).explain("executionStats")
db.orders.createIndex({ city: 1, status: 1 })
```

❌ Mistake 2: Large `skip()` for pagination
✅ Correct: `skip(N)` costs O(N) — the server still walks N entries. Use keyset pagination (`createdAt < lastSeen`).

❌ Mistake 3: Leading-wildcard regex and `$ne`/`$nin` expecting index magic
```javascript
// Wrong — /pattern/ without ^ cannot use the index tightly (scans all keys)
db.users.find({ name: /ita/ })
// Right — anchored prefix regex can use the index range
db.users.find({ name: /^Ad/ })
```

---

## 🧠 Tricky Interview Question

```javascript
// explain shows: winningPlan = IXSCAN, totalKeysExamined: 120000, totalDocsExamined: 120000, nReturned: 20
// "It uses an index, so it is fine." True?
```
Answer: **No.** Using an index is not the same as using a *good* index. 120,000 keys and docs examined to return 20 means the index is not selective for this query (or the filter has a part that cannot use the index, so MongoDB fetches each doc and filters). Goal: `keysExamined ≈ docsExamined ≈ nReturned`. Fix by building a compound index that includes all the filter fields in ESR order, so the index narrows to ~20 entries.

---

## ⚫ Interview Questions + Answers

Q1: What is the first thing you do when a MongoDB query is slow?
A1: Measure it. Capture the exact query (profiler/logs) and run `explain("executionStats")`, look at the stage tree and the keys/docs examined vs returned. Only then decide on an index or rewrite.

Q2: What does a high `totalDocsExamined / nReturned` ratio indicate?
A2: The query reads many documents it then discards — poor selectivity or missing index fields. Ideal is about 1.

Q3: How do you avoid an in-memory sort?
A3: Create an index whose order matches the sort (after equality fields): `{ userId: 1, createdAt: -1 }` for `find({userId}).sort({createdAt:-1})`. The plan then has no `SORT` stage.

Q4: Why is `skip()` bad for deep pagination and what is the alternative?
A4: It must step over all skipped entries every time. Use keyset/range pagination: filter by the last seen sort key plus a unique tiebreaker (like `_id`).

Q5: How do you safely remove an index?
A5: Check `$indexStats` for zero usage, `hideIndex()` it first, watch latency, then `dropIndex()`. Hidden indexes are still updated, so unhiding is instant.

---

## 🔷 When to Use + When Not to Use
✅ Use the checklist when:
- A query shows up in the slow log or profiler
- Latency grows with data size (a classic COLLSCAN sign)
- Before launching a new endpoint on a large collection

❌ Avoid over-optimising when:
- The collection is tiny (a few thousand docs) — a COLLSCAN is fine
- The query runs rarely (nightly job) — don't add indexes that slow all writes
- You have no measurement yet

---

## 📊 Visual Diagram
```
  SLOW QUERY OPTIMIZATION LOOP
  ────────────────────────────
  1. Find slow query ──► profiler / logs
          │
  2. explain("executionStats")
          │
          ▼
  COLLSCAN? ──yes──► add compound index (ESR)
  SORT stage? ─yes─► index matches sort order
  docs >> returned? ► make index more selective / covering
          │
  3. project + limit + keyset pagination
          │
  4. re-measure ──► better? ──no──► back to step 2
          │ yes
          ▼
       ship it, monitor with $indexStats
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| executionStats | Actual runtime numbers of a query | Query के असली runtime आँकड़े |
| COLLSCAN | Full collection scan | पूरा collection scan |
| Selectivity | How much an index narrows results | Index results को कितना छोटा करता है |
| Keyset pagination | Page using last-seen key, not skip | Last key से pagination |
| $indexStats | Per-index usage counters | Index उपयोग की गिनती |
| hideIndex | Make planner ignore an index | Planner से index छुपाना |
| maxTimeMS | Server-side query time limit | Server-side time limit |

---

## ⚡ 3-Line Summary
English:
1. Measure with `explain("executionStats")`; aim for keysExamined ≈ docsExamined ≈ nReturned.
2. Fix with ESR compound indexes, projection, `limit`, and keyset pagination instead of big `skip`.
3. Re-measure, hide-then-drop unused indexes, and protect the DB with `maxTimeMS`.

Hindi:
1. `explain("executionStats")` से measure करो; लक्ष्य keysExamined ≈ docsExamined ≈ nReturned।
2. ESR compound indexes, projection, `limit` और बड़े `skip` की जगह keyset pagination से ठीक करो।
3. दोबारा measure करो, अनुपयोगी indexes पहले hide फिर drop करो, और `maxTimeMS` से DB को बचाओ।

---

## ➡️ Next Topic
**52. MongoDB Profiler and Slow Queries** — Capturing slow operations in `system.profile` and reading them.
