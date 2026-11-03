# 50. Index Selection + hint()
# हिंदी में: Index का चुनाव और hint()

---

## 🔵 Simple Definition (English)
When several indexes could serve a query, MongoDB's **query planner** runs a short **trial race** between the candidate plans, picks the winner, and caches it in the **plan cache**. **`hint()`** lets you override that choice and force a specific index (or `{ $natural: 1 }` to force a collection scan). `explain()` shows the `winningPlan` and the `rejectedPlans`.

## 🔵 सरल परिभाषा (Hindi)
जब एक query के लिए कई indexes काम आ सकते हैं, तो MongoDB का **query planner** candidate plans के बीच एक छोटी **trial race** चलाता है, जीतने वाला plan चुनता है और उसे **plan cache** में रख लेता है। **`hint()`** से आप इस चुनाव को override करके कोई specific index (या collection scan के लिए `{ $natural: 1 }`) force कर सकते हैं। `explain()` में `winningPlan` और `rejectedPlans` दिखते हैं।

---

## 🔴 Problem it Solves
A collection often has many indexes (`{city}`, `{status}`, `{city,status,amount}`). For one query the "best" index is not obvious — it depends on data distribution, which changes over time. MongoDB needs an automatic, data-driven way to choose, and developers need a manual escape hatch for the rare cases when the planner picks a poor plan (stale plan cache, skewed data) or when you want to *test* how a query behaves with a particular index. Without this you would hand-pick indexes in application code, which breaks as data changes.

## 🔴 यह क्यों बना? (Hindi)
एक collection में अक्सर कई indexes होते हैं (`{city}`, `{status}`, `{city,status,amount}`)। एक query के लिए "सबसे अच्छा" index साफ नहीं होता — ये data distribution पर निर्भर है जो समय के साथ बदलता है। MongoDB को चुनने का automatic, data-driven तरीका चाहिए, और developers को एक manual escape hatch चाहिए उन दुर्लभ cases के लिए जब planner खराब plan चुन ले (पुराना plan cache, skewed data) या जब आप किसी खास index के साथ query को *test* करना चाहें। वरना application code में index हाथ से चुनना पड़ता, जो data बदलने पर टूट जाता।

---

## 🟢 How it Works — Step by Step

Step 1 → A query arrives. The planner finds all indexes that are *relevant* (candidate plans) based on the filter, sort and projection.
Step 2 → If only one candidate exists, it is used directly. If several exist, the **multi-planner** runs all of them in parallel for a short trial (bounded number of work units / results).
Step 3 → The plan that returns results fastest (best "productivity") wins; the others become `rejectedPlans`.
Step 4 → The winner is stored in the **plan cache** keyed by the query shape (filter structure, sort, projection), so later queries of the same shape skip the race.
Step 5 → Cached plans are evicted/re-planned when indexes change, the collection changes a lot, or the cached plan performs far worse than expected.
Step 6 → With `hint({ field: 1 })` the planner skips the race and uses exactly that index. A hint on a non-existent index throws an error.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Query आती है। Planner filter, sort और projection देखकर सारे *relevant* indexes (candidate plans) ढूँढता है।
Step 2 → अगर सिर्फ एक candidate है तो सीधे वही use होता है। कई हों तो **multi-planner** सबको parallel में एक छोटे trial (सीमित work units / results) के लिए चलाता है।
Step 3 → जो plan सबसे तेज़ results देता है वो जीतता है; बाकी `rejectedPlans` बन जाते हैं।
Step 4 → विजेता को query shape (filter की structure, sort, projection) के key से **plan cache** में रखा जाता है, ताकि वैसी ही अगली queries race skip करें।
Step 5 → Indexes बदलने, collection में बहुत बदलाव होने, या cached plan उम्मीद से बहुत खराब चलने पर cached plan हटता/दोबारा plan होता है।
Step 6 → `hint({ field: 1 })` से planner race छोड़कर ठीक वही index use करता है। जो index मौजूद नहीं उस पर hint देने से error आता है।

---

## 🟡 Real World Example
**Razorpay's payments dashboard** queries `{ merchantId, status }` with a sort on `createdAt`. The collection has indexes on `merchantId`, on `status`, and on `{ merchantId, createdAt }`. For a small merchant the planner is happy with `merchantId`, but for a giant merchant with 90% "captured" payments, a stale cached plan picked the `status` index and latency spiked. The on-call engineer used `hint({ merchantId: 1, createdAt: -1 })` in the code path (and cleared the plan cache) to stabilise the p99 while the team fixed the indexes properly.

## 🟡 Real Example Hindi mein
**Razorpay के payments dashboard** में `{ merchantId, status }` पर query होती है और `createdAt` पर sort। Collection में `merchantId`, `status` और `{ merchantId, createdAt }` पर indexes हैं। छोटे merchant के लिए planner `merchantId` से खुश रहता है, पर एक बहुत बड़े merchant (90% payments "captured") के लिए पुराने cached plan ने `status` index चुन लिया और latency बढ़ गई। On-call engineer ने code में `hint({ merchantId: 1, createdAt: -1 })` लगाया (और plan cache clear किया) ताकि p99 stable रहे, जबकि team ने indexes ठीक से सुधारे।

---

## 💻 Code Example — Basic

Dataset: `shop.orders`, 5000 docs. Tested on MongoDB 8.0.4.

```javascript
// mongosh
use shop

// Create 3 candidate indexes
db.orders.createIndex({ city: 1, status: 1, amount: 1 }) // compound
db.orders.createIndex({ city: 1 })                        // single field
db.orders.createIndex({ status: 1 })                      // single field

// 1) Let the planner choose
let e = db.orders.find({ city: "Delhi", status: "placed" }).explain("executionStats")
e.queryPlanner.winningPlan.inputStage.indexName   // Output: 'city_1_status_1_amount_1'
e.queryPlanner.rejectedPlans.length               // Output: 2  (the two single-field plans lost the race)

// 2) Force the single-field city index with hint()
e = db.orders.find({ city: "Delhi", status: "placed" })
  .hint({ city: 1 })                              // hint by key pattern (or by name "city_1")
  .explain("executionStats")
e.executionStats.totalKeysExamined                // Output: 1666 (all Delhi entries)
e.executionStats.totalDocsExamined                // Output: 1666 (must FETCH to check status)

// 3) Force a collection scan with $natural
e = db.orders.find({ city: "Delhi", status: "placed" })
  .hint({ $natural: 1 })                          // $natural = disk order = COLLSCAN
  .explain("executionStats")
e.queryPlanner.winningPlan.stage                  // Output: 'COLLSCAN'
e.executionStats.totalDocsExamined                // Output: 5000

// 4) Hint on a non-existent index fails loudly
db.orders.find({ city: "Delhi" }).hint("nope").toArray()
// Output: MongoServerError: error processing query: ... planner returned error ::
//         caused by :: hint provided does not correspond to an existing index
```

## 💻 Code Example — Advanced

```javascript
// Advanced: ESR rule, sort-supporting index and plan-cache inspection
use shop
db.orders.dropIndex("city_1_status_1_amount_1") // clean slate for the demo
db.orders.dropIndex("city_1")
db.orders.dropIndex("status_1")

// Without any index on userId: full collection scan
let e = db.orders.find({ userId: 7 }).explain("executionStats")
e.queryPlanner.winningPlan.stage        // Output: 'COLLSCAN'
e.executionStats.totalDocsExamined      // Output: 5000  (for only 50 matches)

// Index that serves filter (equality) AND sort: { equality, sort }
db.orders.createIndex({ userId: 1, createdAt: -1 })

// Latest 3 orders of user 7 - index delivers rows already sorted, LIMIT stops early
e = db.orders.find({ userId: 7 }).sort({ createdAt: -1 }).limit(3).explain("executionStats")
e.queryPlanner.winningPlan.stage        // Output: 'LIMIT'
e.executionStats.totalKeysExamined      // Output: 3
e.executionStats.totalDocsExamined      // Output: 3   (only what we return)

// Sorting by a field NOT in the index -> blocking in-memory SORT stage
e = db.orders.find({ userId: 7 }).sort({ amount: -1 }).explain("executionStats")
e.queryPlanner.winningPlan.stage            // Output: 'SORT'   (blocking sort)
e.queryPlanner.winningPlan.inputStage.stage // Output: 'FETCH'

// Inspect and clear the plan cache (it holds the chosen plans per query shape)
db.orders.getPlanCache().list()    // array of cached plan entries for this collection
db.orders.getPlanCache().clear()   // drop all cached plans -> next queries re-plan
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');

const Order = mongoose.model('Order', new mongoose.Schema({
  city: String, status: String, amount: Number, userId: Number, createdAt: Date,
}, { collection: 'orders' }));

const app = express();

// Normal endpoint - let the planner choose
app.get('/api/orders/:userId', async (req, res) => {
  const rows = await Order.find({ userId: Number(req.params.userId) })
    .sort({ createdAt: -1 }).limit(10).lean();
  res.json(rows);
});

// Debug endpoint - show the plan and compare with a forced COLLSCAN
app.get('/api/debug/plan', async (req, res) => {
  const plan = await Order.find({ city: 'Delhi' })
    .hint({ $natural: 1 })              // Mongoose supports .hint() on queries
    .explain('executionStats');         // Tested: stage COLLSCAN, 5000 docs examined
  res.json({
    stage: plan.queryPlanner.winningPlan.stage,
    docsExamined: plan.executionStats.totalDocsExamined,
  });
});

mongoose.connect('mongodb://127.0.0.1:27017/shop').then(() => app.listen(3000));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Hard-coding `hint()` everywhere "to be safe"
```javascript
// Wrong — if the index is dropped/renamed the query starts failing in production
db.orders.find({ city: "Delhi" }).hint("city_1")

// Right — fix the real problem (indexes, query shape); use hint only as a targeted, documented override
db.orders.createIndex({ city: 1, status: 1 })
db.orders.find({ city: "Delhi", status: "placed" })
```

❌ Mistake 2: Reading only `winningPlan` and ignoring `executionStats`
✅ Correct: A winning plan can still be bad. Compare `totalKeysExamined` / `totalDocsExamined` against `nReturned`. Ideal ratio is close to 1:1.

❌ Mistake 3: Wrong compound index field order
✅ Correct: Follow **ESR** — Equality fields first, then Sort fields, then Range fields. `{ userId: 1, createdAt: -1 }` serves `find({userId}).sort({createdAt:-1})` with no SORT stage.

---

## 🧠 Tricky Interview Question

```javascript
db.orders.createIndex({ city: 1, status: 1, amount: 1 })
db.orders.find({ status: "placed", amount: 100 }).explain()
// Can the compound index { city, status, amount } be used efficiently?
```
Answer: No. A compound index can be used only through a **prefix** (`city`, then `city+status`, ...). The filter skips `city`, so the index is not usable. Tested on MongoDB 8.0.4: the winning plan is `COLLSCAN`, `totalDocsExamined: 5000` for just 83 matches. Fix: create `{ status: 1, amount: 1 }` or add a `city` equality to the query.

---

## ⚫ Interview Questions + Answers

Q1: How does MongoDB choose among multiple indexes?
A1: The multi-planner runs candidate plans in a short trial and picks the one that returns results with the least work. The winning plan is cached per query shape; the losers appear in `rejectedPlans`.

Q2: What is the plan cache and when is it invalidated?
A2: A per-collection cache of the winning plan per query shape. It is invalidated when an index is created/dropped, when the collection is dropped, on server restart, or when the cached plan "replans" because it performs much worse than when cached. `getPlanCache().clear()` empties it manually.

Q3: When should you use `hint()`?
A3: To work around a bad planner choice temporarily, to compare plans while tuning, or to force `{ $natural: 1 }` for testing. In general you should fix indexes instead of hinting; hints break when indexes change.

Q4: What does `{ $natural: 1 }` mean in `hint()`?
A4: It forces a collection scan in insertion/disk order (`$natural: -1` reverse). Useful to benchmark "no index" behaviour.

Q5: What is the ESR rule?
A5: Order compound index fields as Equality, Sort, Range. Equality narrows the range, Sort lets the index provide ordering (no blocking SORT), and Range last keeps the index scan tight.

---

## 🔷 When to Use + When Not to Use
✅ Use `hint()` when:
- The planner picks a measurably worse index and you cannot change indexes right now
- You are benchmarking/comparing index candidates in a test
- You need deterministic plans for a critical query (documented, with monitoring)

❌ Avoid `hint()` when:
- You have not looked at `explain()` first
- The index may be dropped/renamed later (queries will error)
- Better indexes or query rewrites would solve it

---

## 📊 Visual Diagram
```
 find({city:"Delhi", status:"placed"})
            │
            ▼
   ┌────────────────────┐   cached?  ──yes──► use cached plan
   │ Plan cache lookup  │
   └────────┬───────────┘
            │ no
            ▼
   Candidate plans (trial race)
   ┌───────────────┬──────────────┬───────────────┐
   │ IXSCAN city_1 │ IXSCAN status│ IXSCAN city_  │
   │ + FETCH       │ + FETCH      │ status_amount │
   └───────────────┴──────────────┴───────┬───────┘
                                          ▼ winner
                              stored in plan cache
   hint({city:1})  ──► skip the race, force that index
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Query planner | Chooses how to run a query | Query कैसे चले ये चुनने वाला |
| winningPlan | Plan MongoDB selected | चुना गया plan |
| rejectedPlans | Plans that lost the trial | हारे हुए plans |
| Plan cache | Stores winning plan per query shape | Query shape के हिसाब से winning plan का cache |
| hint() | Force a specific index | किसी खास index को force करना |
| $natural | Disk-order scan (COLLSCAN) | Disk order में scan |
| ESR rule | Equality, Sort, Range order | Compound index का field order नियम |

---

## ⚡ 3-Line Summary
English:
1. MongoDB races candidate indexes, picks the winner, and caches the plan per query shape.
2. `hint()` forces an index (or `$natural` for COLLSCAN) — hinting a missing index throws an error.
3. Read `executionStats` (keys/docs examined vs returned) and design compound indexes with the ESR rule.

Hindi:
1. MongoDB candidate indexes की race कराता है, विजेता चुनता है और plan को query shape के हिसाब से cache करता है।
2. `hint()` index force करता है (या COLLSCAN के लिए `$natural`) — मौजूद न होने वाले index पर hint देने से error आता है।
3. `executionStats` (examined vs returned) पढ़ो और compound indexes ESR rule से बनाओ।

---

## ➡️ Next Topic
**51. Query Optimization Checklist** — A practical step-by-step checklist to find and fix slow MongoDB queries.
