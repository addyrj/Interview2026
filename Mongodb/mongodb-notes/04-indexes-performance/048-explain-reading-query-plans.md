# 48. explain() — Reading Query Plans
# हिंदी में: explain() — Query Plans पढ़ना

---

## 🔵 Simple Definition (English)
**`explain()`** shows how MongoDB executes (or would execute) a query: which index it chose, how many keys and documents it examined, and which stages ran. It has three verbosity modes: `"queryPlanner"` (default, just the chosen plan, query is not run), `"executionStats"` (runs the query and reports real work), and `"allPlansExecution"` (also stats for rejected candidate plans). It is the main tool for index tuning.

## 🔵 सरल परिभाषा (Hindi)
**`explain()`** दिखाता है कि MongoDB query को कैसे चलाता है (या चलाएगा): कौन सा index चुना, कितनी keys और documents examine किए, और कौन से stages चले। इसके तीन modes हैं: `"queryPlanner"` (default, सिर्फ चुना हुआ plan, query चलती नहीं), `"executionStats"` (query चलाकर असली काम बताता है), और `"allPlansExecution"` (rejected plans के stats भी)। Index tuning का मुख्य औज़ार।

---

## 🔴 Problem it Solves
"The query is slow" is not actionable. `explain()` tells you whether it is a COLLSCAN, whether it sorts in memory, and how much work was wasted (examined 5000 docs to return 10). Without it, you add indexes by guessing.

## 🔴 यह क्यों बना? (Hindi)
"Query slow है" से कुछ नहीं पता चलता। `explain()` बताता है कि COLLSCAN है या नहीं, memory में sort हो रहा है या नहीं, और कितना काम बेकार गया (10 results के लिए 5000 docs देखे)। इसके बिना index अंदाज़े से बनते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Run `db.orders.find({...}).explain("executionStats")`.
Step 2 → Read `queryPlanner.winningPlan`: the stage tree, read from the innermost stage out. `IXSCAN` (index scan) -> `FETCH` (read docs) -> `SORT`/`PROJECTION...`. `COLLSCAN` = full scan (red flag on big collections).
Step 3 → Read `executionStats`: `nReturned`, `totalKeysExamined`, `totalDocsExamined`, `executionTimeMillis`.
Step 4 → Healthy ratio: `totalDocsExamined` close to `nReturned` (ideal 1:1). Large gap = inefficient index/filter.
Step 5 → `SORT` stage in the plan = in-memory blocking sort (limit 100 MB then error unless `allowDiskUse`). Design an ESR index to remove it.
Step 6 → `PROJECTION_COVERED` + `totalDocsExamined: 0` = covered query (index-only), the best case.
Step 7 → `rejectedPlans` and `allPlansExecution` show alternatives the planner tried; use `.hint()` to force and compare.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `db.orders.find({...}).explain("executionStats")` चलाओ।
Step 2 → `queryPlanner.winningPlan` पढ़ो: stage tree अंदर से बाहर पढ़ो। `IXSCAN` -> `FETCH` -> `SORT`/`PROJECTION...`। `COLLSCAN` = पूरा scan (बड़े collection पर खतरे का संकेत)।
Step 3 → `executionStats` पढ़ो: `nReturned`, `totalKeysExamined`, `totalDocsExamined`, `executionTimeMillis`।
Step 4 → अच्छा अनुपात: `totalDocsExamined` ≈ `nReturned` (आदर्श 1:1)। बड़ा अंतर = अकुशल index/filter।
Step 5 → Plan में `SORT` = memory का blocking sort (100 MB limit)। ESR index से हटाओ।
Step 6 → `PROJECTION_COVERED` + `totalDocsExamined: 0` = covered query, सबसे बढ़िया।
Step 7 → `rejectedPlans` और `allPlansExecution` में बाकी plans दिखते हैं; `.hint()` से force करके तुलना करो।

---

## 🟡 Real World Example
At **Swiggy**, the "my orders" API p99 jumped from 40 ms to 2 s. An engineer ran `explain("executionStats")`: `COLLSCAN`, `totalDocsExamined: 5 crore`, `nReturned: 20`. A new index `{ userId: 1, createdAt: -1 }` changed it to `IXSCAN`, `totalDocsExamined: 20`, and latency dropped back to ~5 ms.

## 🟡 Real Example Hindi mein
**Swiggy** की "my orders" API का p99 40 ms से 2 s हो गया। Engineer ने `explain("executionStats")` चलाया: `COLLSCAN`, `totalDocsExamined: 5 करोड़`, `nReturned: 20`। नया index `{ userId: 1, createdAt: -1 }` बनाने पर `IXSCAN`, `totalDocsExamined: 20`, और latency वापस ~5 ms।

---

## 💻 Code Example — Basic

```javascript
// mongosh (verified on MongoDB 8.0.4). 5000 orders, no index on city/amount at first
use idx_demo

// 1) COLLSCAN: worst case
db.orders.find({ city: "Goa", amount: { $gt: 90 } }).explain("executionStats").executionStats
// { nReturned: 150, totalKeysExamined: 0, totalDocsExamined: 5000, ... }  <- read 5000 docs for 150
// winningPlan.stage: 'COLLSCAN'

// 2) After a compound index (equality city, range amount)
db.orders.createIndex({ city: 1, amount: 1 })
const e = db.orders.find({ city: "Goa", amount: { $gt: 90 } }, { _id: 0, city: 1, amount: 1 })
            .explain("executionStats")
e.queryPlanner.winningPlan.stage              // Output: 'PROJECTION_COVERED'
e.queryPlanner.winningPlan.inputStage.stage   // Output: 'IXSCAN'
e.executionStats.totalDocsExamined            // Output: 0    <- covered query! no documents read
e.executionStats.nReturned                    // Output: 150
```

## 💻 Code Example — Advanced

```javascript
// A helper to print the stage chain + work done (what we used to verify the notes)
function ex(cursor) {
  const e = cursor.explain("executionStats");
  const stg = (s) => s.inputStage ? s.stage + " > " + stg(s.inputStage) : s.stage + (s.indexName ? "(" + s.indexName + ")" : "");
  print(stg(e.queryPlanner.winningPlan), "| keys", e.executionStats.totalKeysExamined,
        "docs", e.executionStats.totalDocsExamined, "returned", e.executionStats.nReturned);
}

// In-memory sort detection
db.orders.createIndex({ status: 1, city: 1, amount: 1 })
ex(db.orders.find({ status: "paid" }).sort({ createdAt: 1 }))
// Output: SORT > FETCH > IXSCAN(status_1_city_1_amount_1) | keys 1667 docs 1667 returned 1667
// The SORT stage sorts 1667 docs in RAM -> consider index { status: 1, createdAt: 1 }

// allPlansExecution: shows the competing plans the optimizer raced
const full = db.orders.find({ userId: 42 }).explain("allPlansExecution")
Object.keys(full.queryPlanner)
// [ 'namespace','parsedQuery','indexFilterSet','planCacheShapeHash','planCacheKey','optimizationTimeMillis',
//   'maxIndexedOrSolutionsReached','maxIndexedAndSolutionsReached','maxScansToExplodeReached',
//   'prunedSimilarIndexes','winningPlan','rejectedPlans' ]   (key names vary by server version)
full.queryPlanner.rejectedPlans.length    // 0 here: only one index was applicable

// Force a plan to compare
ex(db.orders.find({ status: "paid", city: "Delhi" }).hint({ status: 1, city: 1, amount: 1 }))
ex(db.orders.find({ status: "paid", city: "Delhi" }).hint({ $natural: 1 }))   // force COLLSCAN to compare
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose: Query#explain
const plan = await Order.find({ status: 'paid', city: 'Delhi' })
  .sort({ amount: 1 })
  .explain('executionStats');         // returns the explain document (no results)

// Expose a debug-only endpoint (never in production without auth)
app.get('/debug/explain', async (req, res) => {
  const e = await db.collection('orders').find({ userId: +req.query.userId }).explain('executionStats');
  const s = e.executionStats;
  res.json({ returned: s.nReturned, keys: s.totalKeysExamined, docs: s.totalDocsExamined, ms: s.executionTimeMillis,
             stage: e.queryPlanner.winningPlan.stage });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using default `explain()` and assuming it ran the query
```javascript
// Wrong - queryPlanner mode shows the chosen plan only, no real numbers
db.orders.find({ userId: 42 }).explain()
// Right - get actual counts
db.orders.find({ userId: 42 }).explain("executionStats")
```

❌ Mistake 2: Judging by `executionTimeMillis` alone (cold cache, tiny data, noisy)
✅ Correct: compare `totalDocsExamined` / `totalKeysExamined` to `nReturned` first, then time.

❌ Mistake 3: Testing on a tiny dev collection - the planner and timings differ from production data volumes and distributions.

---

## 🧠 Tricky Interview Question

```javascript
db.orders.find({ city: "Goa", amount: { $gt: 90 } }, { _id: 0, city: 1, amount: 1 }).explain("executionStats")
// With index {city:1, amount:1}: how many documents examined?
```
Answer: `totalDocsExamined: 0`. The projection only needs fields stored in the index and `_id` is excluded, so the plan is `PROJECTION_COVERED > IXSCAN` and no documents are fetched (verified: 150 returned, 0 docs). Forgetting `_id: 0` would force a FETCH because `_id` is not in this index.

---

## ⚫ Interview Questions + Answers

Q1: Three explain modes?
A1: `queryPlanner` (plan only), `executionStats` (runs query, real stats), `allPlansExecution` (also candidate plan stats).

Q2: What do you look for first?
A2: COLLSCAN, SORT stages, and the ratio of `totalDocsExamined` to `nReturned`.

Q3: What is a covered query?
A3: One answered entirely from an index: all filter and projected fields in the index, `_id` excluded or indexed, `totalDocsExamined: 0`.

Q4: How can you force an index?
A4: `.hint({ field: 1 })` or by name; `$natural: 1` forces a collection scan.

Q5: Does `explain` change data?
A5: No for reads. For write ops (`update`, `delete`) explain shows the plan with `executionStats` without applying the write.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging slow queries, validating a new index, code-reviewing queries

❌ Avoid:
- Judging only from dev data; always verify with production-like volume

---

## 📊 Visual Diagram
```
winningPlan (read inside-out)

   PROJECTION_COVERED        <- 3) returns fields from the index only
         |
       IXSCAN {city,amount}  <- 2) walk index keys
         |
   (no FETCH => covered)

 Bad:   SORT > FETCH > COLLSCAN       Good:  FETCH > IXSCAN        Best: IXSCAN covered
 docs examined 5000 / returned 150    docs 150 / returned 150      docs 0
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| COLLSCAN | Full collection scan | पूरा collection scan |
| IXSCAN | Index scan | Index scan |
| FETCH | Read documents | Documents पढ़ना |
| nReturned | Docs returned | Return हुए docs |
| totalDocsExamined | Docs read | पढ़े गए docs |
| Covered query | Answered from index only | सिर्फ index से जवाब |

---

## ⚡ 3-Line Summary
English:
1. `explain("executionStats")` shows the plan and real work done.
2. Watch COLLSCAN, SORT, and docs examined versus returned.
3. Covered queries (docs examined 0) are the best case; test with realistic data.

Hindi:
1. `explain("executionStats")` plan और असली काम दिखाता है।
2. COLLSCAN, SORT, और examined बनाम returned docs देखो।
3. Covered queries (docs examined 0) सबसे बढ़िया; असली जैसे data पर test करो।

---

## ➡️ Next Topic
**49. Covered Queries**
