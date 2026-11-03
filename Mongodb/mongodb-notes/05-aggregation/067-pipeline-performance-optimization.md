# 67. Pipeline Performance Optimization
# हिंदी में: Aggregation Pipeline Performance Optimization

---

## 🔵 Simple Definition (English)
Pipeline optimization means shaping an aggregation so MongoDB reads as **few documents** as possible, uses **indexes**, passes **small documents** between stages and avoids memory-heavy stages. The main levers: put `$match`/`$sort`/`$limit` first, index the fields they use, `$project` only needed fields, avoid `$unwind` + `$lookup` on large sets, check with `explain("executionStats")`, and use `allowDiskUse` for big `$group`/`$sort`. Tested on MongoDB 8.0.4.

## 🔵 सरल परिभाषा (Hindi)
Pipeline optimization का मतलब aggregation को ऐसे बनाना कि MongoDB **कम से कम documents** पढ़े, **indexes** इस्तेमाल करे, stages के बीच **छोटे documents** जाएँ और memory-भारी stages से बचा जाए। मुख्य उपाय: `$match`/`$sort`/`$limit` सबसे पहले, उनके fields पर index, सिर्फ़ ज़रूरी fields का `$project`, बड़े sets पर `$unwind` + `$lookup` से बचना, `explain("executionStats")` से जाँच, और बड़े `$group`/`$sort` के लिए `allowDiskUse`।

---

## 🔴 Problem it Solves
A pipeline is executed stage by stage. A careless pipeline (`$group` first, `$match` last) scans the entire collection, builds huge in-memory groups and then throws most away. A stage that buffers (blocking stages such as `$group`, `$sort` without an index) has a **100 MB RAM limit per stage** unless `allowDiskUse` is true (on 6.0+ the default for `allowDiskUseByDefault` is true on the server, but you should not rely on spilling for speed). Result: slow dashboards, high CPU and timeouts.

## 🔴 यह क्यों बना? (Hindi)
Pipeline stage-by-stage चलती है। लापरवाह pipeline (पहले `$group`, आख़िर में `$match`) पूरी collection scan करती है, memory में बड़े groups बनाती है और फिर ज़्यादातर फेंक देती है। Blocking stages (`$group`, बिना index के `$sort`) की **हर stage पर 100 MB RAM limit** होती है जब तक `allowDiskUse` true न हो (6.0+ में server का default spill की अनुमति देता है, पर speed के लिए spill पर भरोसा मत करो)। नतीजा: slow dashboards, ज़्यादा CPU और timeouts।

---

## 🟢 How it Works — Step by Step

Step 1 → MongoDB's **optimizer** rewrites your pipeline first: it pushes `$match` before `$project`/`$sort` when safe, merges `$sort + $limit` into a top-k sort, merges adjacent `$match`es, and moves the first `$match`/`$sort` into the query layer so **indexes** apply.
Step 2 → Only a pipeline **prefix** of `$match`, `$sort`, `$limit`, `$skip`, `$project` (and some `$group` in SBE) can use indexes. After `$group`/`$lookup`/`$unwind` the data is no longer index-backed.
Step 3 → A **covered** plan (`$match` + `$project` on fields all in one index) reads zero documents (`totalDocsExamined: 0`).
Step 4 → `$lookup` hits the foreign collection per input doc — the `foreignField` must be indexed, and `$match`/`$limit` *before* `$lookup` shrinks the input.
Step 5 → Verify with `explain("executionStats")`: compare `totalDocsExamined`, `totalKeysExamined`, `nReturned` and the stage tree (`COLLSCAN` vs `IXSCAN`).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → पहले MongoDB का **optimizer** pipeline rewrite करता है: safe हो तो `$match` को `$project`/`$sort` से पहले ले जाता है, `$sort + $limit` को top-k sort में merge करता है, पास-पास के `$match` merge करता है, और पहला `$match`/`$sort` query layer में भेजता है ताकि **index** लगे।
Step 2 → सिर्फ़ pipeline के **prefix** (`$match`, `$sort`, `$limit`, `$skip`, `$project`) index इस्तेमाल कर सकते हैं। `$group`/`$lookup`/`$unwind` के बाद data index-backed नहीं रहता।
Step 3 → **Covered** plan (`$match` + `$project` के सारे fields एक index में) एक भी document नहीं पढ़ता (`totalDocsExamined: 0`)।
Step 4 → `$lookup` हर input doc पर foreign collection को hit करता है — `foreignField` पर index ज़रूरी है, और `$lookup` से पहले `$match`/`$limit` input घटाते हैं।
Step 5 → `explain("executionStats")` से जाँचो: `totalDocsExamined`, `totalKeysExamined`, `nReturned` और stage tree (`COLLSCAN` बनाम `IXSCAN`)।

---

## 🟡 Real World Example
**Flipkart's seller-analytics page** runs "top 3 customers by spend for city = Pune, status = delivered" over a 20-crore-row `orders` collection. The first version grouped everything and filtered at the end (minutes). The fix: `$match` first, compound index `{ status: 1, city: 1 }`, then `$group` → `$sort` → `$limit`. Documents examined dropped from the whole collection to just the matching slice.

## 🟡 Real Example Hindi mein
**Flipkart का seller-analytics page** 20 करोड़ rows वाली `orders` collection पर "city = Pune, status = delivered के top 3 customers by spend" चलाता है। पहला version सब कुछ group करके आख़िर में filter करता था (मिनट लगते थे)। Fix: पहले `$match`, compound index `{ status: 1, city: 1 }`, फिर `$group` → `$sort` → `$limit`। Documents examined पूरी collection से घटकर सिर्फ़ matching हिस्से तक आ गए।

---

## 💻 Code Example — Basic

```javascript
// mongosh — seed 20,000 orders (our measured numbers below come from this exact data)
use t67
let docs = [];                                          // build an array, insert once (fast)
const cities = ["Bengaluru", "Mumbai", "Delhi", "Pune"];
for (let i = 0; i < 20000; i++) {
  docs.push({ _id: i, city: cities[i % 4],             // 4 cities, 5000 each
              status: i % 5 == 0 ? "cancelled" : "delivered", // 1 in 5 cancelled
              amount: 100 + (i % 900), userId: i % 500 });    // 500 distinct users
}
db.orders.insertMany(docs)

// The pipeline: filter first, then group/sort/limit
const pipeline = [
  { $match: { status: "delivered", city: "Pune" } },    // narrow the input FIRST
  { $group: { _id: "$userId", t: { $sum: "$amount" } } },// spend per user
  { $sort: { t: -1 } },                                  // biggest spenders first
  { $limit: 3 }                                          // top 3
]

// 1) WITHOUT an index
let e = db.orders.explain("executionStats").aggregate(pipeline)
// reading e.stages[0].$cursor.executionStats  (the part that feeds the pipeline):
// totalDocsExamined: 20000   <- whole collection scanned (COLLSCAN)
// nReturned: 100             <- the $group was pushed into the query layer, so it returns 100 groups (distinct userIds)
// (exact explain shape differs by version; the key number is totalDocsExamined)

// 2) WITH a compound index matching the $match
db.orders.createIndex({ status: 1, city: 1 })           // equality fields -> any order works
e = db.orders.explain("executionStats").aggregate(pipeline)
// totalDocsExamined: 4000, totalKeysExamined: 4000      <- only matching docs read
// winning plan: GROUP -> FETCH -> IXSCAN (indexName: 'status_1_city_1')
```

## 💻 Code Example — Advanced

```javascript
// mongosh — covered pipeline, top-k sort, $lookup tuning, allowDiskUse

// 1) COVERED aggregation: $match + $group use only fields inside the index {city:1, amount:1}
db.orders.createIndex({ city: 1, amount: 1 })
db.orders.explain("executionStats").aggregate([
  { $match: { city: "Pune" } },                          // uses the index prefix "city"
  { $group: { _id: null, t: { $sum: "$amount" } } }      // needs only "amount", also in the index
])
// Measured: totalDocsExamined: 0, totalKeysExamined: 5000  <- no document fetched at all

// 2) $sort + $limit coalescence: the optimizer keeps only top-N in memory, not the whole sorted set
db.orders.aggregate([
  { $sort: { amount: -1 } },                             // without limit this would sort 20,000 docs
  { $limit: 5 }                                          // optimizer merges: top-5 heap sort
])

// 3) allowDiskUse for blocking stages beyond the memory limit
db.orders.aggregate([
  { $group: { _id: "$userId", t: { $sum: "$amount" } } },
  { $sort: { t: -1 } },
  { $limit: 2 }
], { allowDiskUse: true })                               // spill to _tmp files instead of failing
// Output: [ { _id: 299, t: 24360 }, { _id: 298, t: 24320 } ]

// 4) $lookup with a sub-pipeline: limit/project INSIDE so the join stays small
db.orders.aggregate([
  { $match: { _id: { $lt: 2 } } },                       // only 2 outer docs
  { $lookup: {
      from: "orders", localField: "userId", foreignField: "userId", as: "x",
      pipeline: [ { $limit: 2 }, { $project: { _id: 1 } } ]  // cap + slim the joined docs
  } }
])
// Output (first doc): { _id: 0, city: 'Bengaluru', ..., x: [ { _id: 0 }, { _id: 500 } ] }

// 5) Reading explain: the optimizer pushes $match into the cursor,
//    so db.orders.explain().aggregate([{$sort:{amount:-1}},{$match:{city:"Pune"}}])
//    shows only queryPlanner (no separate $match stage) - the filter was moved before the sort.
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');

const orderSchema = new mongoose.Schema({
  city: String, status: String, amount: Number, userId: Number
});
// Declare the index in the schema so autoIndex/migrations create it (build indexes explicitly in prod)
orderSchema.index({ status: 1, city: 1 });
const Order = mongoose.model('Order', orderSchema);

const app = express();

app.get('/top-spenders', async (req, res) => {
  const city = String(req.query.city || 'Pune');      // never pass raw objects from req.query into $match (NoSQL injection)
  const rows = await Order.aggregate([
    { $match: { status: 'delivered', city } },           // first, index-backed
    { $group: { _id: '$userId', t: { $sum: '$amount' } } },
    { $sort: { t: -1 } },
    { $limit: 3 }
  ]).option({ allowDiskUse: true, maxTimeMS: 5000 });    // time-box so one bad query can't hog the server
  res.json(rows);
});

// Dev helper: aggregate(...).explain('executionStats') returns the plan
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `$match` late in the pipeline
```javascript
// Wrong — groups all 20,000 docs, then filters 4 groups
[ { $group: { _id: "$city", t: { $sum: "$amount" } } }, { $match: { _id: "Pune" } } ]
// Right — filter first, group only what you need
[ { $match: { city: "Pune" } }, { $group: { _id: "$city", t: { $sum: "$amount" } } } ]
```

❌ Mistake 2: `$lookup` on an unindexed `foreignField`, and `$unwind` before `$match`
```javascript
// Wrong — each outer doc scans the whole foreign collection
{ $lookup: { from: "reviews", localField: "_id", foreignField: "restaurantId", as: "r" } }  // no index on restaurantId
// Right — db.reviews.createIndex({ restaurantId: 1 }) first, and $match/$limit the outer docs before the lookup
```
✅ Also: don't rely on `allowDiskUse` as a fix; reduce data (`$project`, earlier `$match`) first.

---

## 🧠 Tricky Interview Question

You write `[ { $sort: { amount: -1 } }, { $match: { city: "Pune" } } ]`. Does MongoDB sort all 20,000 docs and then filter?

Answer: No. The optimizer **moves `$match` before `$sort`** (a filter does not depend on order), so only matching docs are sorted. `explain()` shows no separate `$match` stage — it was folded into the query layer. The same trick does not apply if the `$match` depends on a field created by an earlier `$project`/`$group`/`$addFields` — then it can only be pushed up to just after the stage that creates the field.

---

## ⚫ Interview Questions + Answers

Q1: Which stages can use indexes?
A1: Mainly a leading `$match` and `$sort` (and `$limit`/`$skip`/`$project` attached to them), `$geoNear`, `$text` inside `$match`, and `$lookup`'s foreign side. Once a transforming stage like `$group`, `$unwind` or `$addFields` runs, later stages work on in-memory/stream data.

Q2: What is the 100 MB limit?
A2: Blocking stages (`$group`, `$sort`, `$bucket`...) have a memory budget per stage. When exceeded, with `allowDiskUse: true` (or server default on 6.0+) they spill to temporary files; otherwise the command errors. Spilling is slower than staying in RAM.

Q3: What does `explain("executionStats")` tell you?
A3: The winning plan, and real counts: `totalKeysExamined`, `totalDocsExamined`, `nReturned`, `executionTimeMillis`. A healthy query has docsExamined close to nReturned; a `COLLSCAN` over a big collection is the red flag.

Q4: How to speed up "count/sum" reports that run on every page load?
A4: Pre-aggregate: store running totals (Computed pattern), or write a nightly `$merge` into a summary collection (on-demand materialized view), and read that.

Q5: `$project` early or late?
A5: Trimming fields early (when a stage like `$group` or `$lookup` follows) reduces data moved between stages. The optimizer also auto-detects needed fields (dependency analysis) so manual `$project` matters mostly before `$lookup` or when documents are huge.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A report/dashboard pipeline takes seconds on millions of docs
- You can express the leading filter and sort with an index
- You run the same expensive aggregation repeatedly (pre-aggregate with `$merge`)

❌ Avoid when:
- Collection is tiny (premature optimization)
- You rely on `allowDiskUse` instead of reducing the working set
- You optimize by guess — always compare `explain` before/after

---

## 📊 Visual Diagram
```
BAD                           GOOD
──────────────                ─────────────────────────
COLLSCAN 20,000 docs          IXSCAN {status,city} -> 4,000 keys
   │                                │ (only matching docs fetched)
   ▼                                ▼
$group (all docs)             $group (4,000 docs)
   │                                │
   ▼                                ▼
$match (keep 1 group)         $sort + $limit (top-k heap)
                                    │
                              result: 3 docs

Covered:  IXSCAN {city,amount} -> $group   docsExamined = 0
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| explain | Shows query plan and stats | Query plan/stats दिखाता है |
| COLLSCAN / IXSCAN | Full scan / index scan | पूरा scan / index scan |
| Covered query | Answered from index alone | सिर्फ़ index से जवाब |
| Blocking stage | Needs all input before output (`$group`, `$sort`) | पूरा input चाहिए |
| allowDiskUse | Allow spilling to disk | Disk पर spill की अनुमति |
| Pipeline prefix | Leading stages that can use index | शुरुआती stages जो index लेते हैं |
| maxTimeMS | Server-side time limit | Server-side time limit |

---

## ⚡ 3-Line Summary
English:
1. Filter and sort first, backed by an index, so the pipeline starts with the smallest possible input.
2. Index `$lookup` foreign fields, slim documents before blocking stages, and use covered plans where possible.
3. Measure with `explain("executionStats")` (docsExamined vs nReturned); use `allowDiskUse` only as a safety net.

Hindi:
1. पहले filter और sort करो, index के साथ, ताकि pipeline सबसे छोटे input से शुरू हो।
2. `$lookup` के foreign fields पर index लगाओ, blocking stages से पहले documents छोटे करो, और जहाँ हो सके covered plan बनाओ।
3. `explain("executionStats")` से नापो (docsExamined बनाम nReturned); `allowDiskUse` सिर्फ़ safety net है।

---

## ➡️ Next Topic
**68. Aggregation vs MapReduce** — why `mapReduce` is deprecated and how `$group`, `$accumulator` and `$merge` replace it.
