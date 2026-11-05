# 125. Slow Query Debugging Scenario
# हिंदी में: Slow Query Debug करने का Scenario

---

## 🔵 Simple Definition (English)
**Slow query debugging** is the repeatable process of finding why a MongoDB query is slow and fixing it: find the query (profiler / slow log), read its plan with `explain("executionStats")`, compare **keys examined / docs examined / docs returned**, then add or reshape an index and re-measure.

## 🔵 सरल परिभाषा (Hindi)
**Slow query debugging** वह दोहराई जा सकने वाली process है जिसमें पता लगाते हैं कि MongoDB query धीमी क्यों है और उसे ठीक करते हैं: query ढूँढो (profiler / slow log), `explain("executionStats")` से plan पढ़ो, **keys examined / docs examined / docs returned** की तुलना करो, फिर index जोड़ो या बदलो और दोबारा नापो।

---

## 🔴 Problem it Solves
"The My Orders page takes 4 seconds." Guessing ("add more RAM", "add an index on everything") wastes money and slows writes. A methodical approach shows the exact cause: usually a **COLLSCAN** (reading every document) or an in-memory **SORT**. The fix is typically one correctly designed compound index that drops the work from 100,000 documents to 5.

## 🔴 यह क्यों बना? (Hindi)
"My Orders page 4 second में खुल रहा है।" अंदाज़े ("RAM बढ़ाओ", "हर field पर index लगाओ") से पैसा बर्बाद होता है और writes धीमे होते हैं। व्यवस्थित तरीका असली कारण दिखाता है: अक्सर **COLLSCAN** (हर document पढ़ना) या memory में **SORT**। Fix आम तौर पर एक सही compound index होता है, जो काम 1,00,000 documents से घटाकर 5 कर देता है।

---

## 🟢 How it Works — Step by Step

Step 1 -> **Find the culprit**: enable the profiler (`db.setProfilingLevel(1, {slowms: 100})`) or read the slow-query lines in the mongod log. Pick the query with the highest total time, not just the single slowest.
Step 2 -> **Explain it**: `.explain("executionStats")` gives the winning plan and real numbers.
Step 3 -> **Read the ratios**: `totalDocsExamined` vs `nReturned`. Ideal is close to 1:1. `COLLSCAN` or a `SORT` stage (blocking, in memory) are red flags.
Step 4 -> **Design the index** with the ESR rule: **E**quality fields first, **S**ort fields next, **R**ange fields last.
Step 5 -> **Re-run explain**, confirm `IXSCAN` and tiny keys/docs counts, then deploy (build index in off-peak hours; drop indexes that became redundant).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 -> **दोषी query ढूँढो**: profiler चालू करो (`db.setProfilingLevel(1, {slowms: 100})`) या mongod log में slow-query lines देखो। सिर्फ सबसे धीमी नहीं, बल्कि जिसका total time सबसे ज़्यादा है वह चुनो।
Step 2 -> **Explain करो**: `.explain("executionStats")` winning plan और असली numbers देता है।
Step 3 -> **Ratios पढ़ो**: `totalDocsExamined` बनाम `nReturned`। आदर्श लगभग 1:1। `COLLSCAN` या `SORT` stage (memory में blocking) खतरे के संकेत हैं।
Step 4 -> **ESR rule** से index बनाओ: पहले **E**quality fields, फिर **S**ort fields, आख़िर में **R**ange fields।
Step 5 -> **दोबारा explain** करो, `IXSCAN` और छोटे keys/docs counts पक्के करो, फिर deploy करो (index off-peak में बनाओ; बेकार हुए indexes हटाओ)।

---

## 🟡 Real World Example
**Zomato's "My Orders" screen** runs: "last 5 delivered orders of user 42, newest first". The `orders` collection has 100 million documents. With no index the query scans all of them (seconds); after one compound index `{ userId: 1, status: 1, createdAt: -1 }` it touches exactly 5 index entries and 5 documents (a few milliseconds) and needs no sorting at all, because the index is already in the right order.

## 🟡 Real Example Hindi mein
**Zomato की "My Orders" screen** यह query चलाती है: "user 42 के आख़िरी 5 delivered orders, नए पहले"। `orders` collection में 10 करोड़ documents हैं। Index के बिना query सबको scan करती है (कई सेकंड); एक compound index `{ userId: 1, status: 1, createdAt: -1 }` के बाद यह ठीक 5 index entries और 5 documents छूती है (कुछ millisecond) और sort की ज़रूरत ही नहीं, क्योंकि index पहले से सही क्रम में है।

---

## 💻 Code Example — Basic

Setup: 100,000 orders, 5,000 users (verified on MongoDB 8.0.4, mongosh):

```javascript
const d = db.getSiblingDB("slow"); d.dropDatabase();       // fresh database
const cities = ["Delhi","Pune","Mumbai","Goa"], st = ["placed","delivered","cancelled"];
let b = [];
for (let i = 0; i < 100000; i++) {                          // build 100k docs in memory
  b.push({ userId: i % 5000, city: cities[i % 4], status: st[i % 3],
           amount: i % 1000, createdAt: new Date(1767225600000 + i * 60000) }); // 1 order per minute
}
d.orders.insertMany(b);                                     // bulk insert

const f = { userId: 42, status: "delivered" };              // the slow filter
// helper: print plan shape + the three numbers that matter
function s(e) {
  const x = e.executionStats;                               // real runtime stats
  const stage = (function g(p) { return p.inputStage ? p.stage + ">" + g(p.inputStage)
                 : p.stage + (p.indexName ? "(" + p.indexName + ")" : ""); })(e.queryPlanner.winningPlan);
  print(JSON.stringify({ stage, returned: x.nReturned, keys: x.totalKeysExamined, docs: x.totalDocsExamined }));
}

// ---- BEFORE: no index ----
s(d.orders.find(f).sort({ createdAt: -1 }).limit(5).explain("executionStats"));
// {"stage":"SORT>COLLSCAN","returned":5,"keys":0,"docs":100000}
//  -> reads ALL 100,000 docs, then sorts in memory to return 5.
```

```javascript
// ---- ATTEMPT 1: single-field index on userId ----
d.orders.createIndex({ userId: 1 });                        // helps the equality on userId only
s(d.orders.find(f).sort({ createdAt: -1 }).limit(5).explain("executionStats"));
// {"stage":"SORT>FETCH>IXSCAN(userId_1)","returned":5,"keys":20,"docs":20}
//  -> huge improvement (20 docs), but still fetches all of the user's docs and still has a SORT stage.

// ---- ATTEMPT 2: compound index following ESR ----
// userId (equality), status (equality), createdAt (sort field, descending)
d.orders.createIndex({ userId: 1, status: 1, createdAt: -1 });
s(d.orders.find(f).sort({ createdAt: -1 }).limit(5).explain("executionStats"));
// {"stage":"LIMIT>FETCH>IXSCAN(userId_1_status_1_createdAt_-1)","returned":5,"keys":5,"docs":5}
//  -> perfect 5:5:5. No SORT stage; the index already returns newest first and LIMIT stops after 5.
```

## 💻 Code Example — Advanced

```javascript
// 1) Covered query: answered from the index alone (docs examined = 0)
d.orders.createIndex({ userId: 1, status: 1, amount: 1 });  // index contains every field we need
s(d.orders.find(f, { _id: 0, amount: 1 })                   // project ONLY indexed fields, drop _id
   .hint("userId_1_status_1_amount_1")                      // force this index for the demo
   .explain("executionStats"));
// {"stage":"PROJECTION_COVERED>IXSCAN(userId_1_status_1_amount_1)","returned":6,"keys":6,"docs":0}
//  -> docs: 0 means MongoDB never touched the collection data.

// 2) A query no index helps: there is no index on city, so a prefix regex still scans everything
s(d.orders.find({ city: /^Del/ }).explain("executionStats"));
// {"stage":"COLLSCAN","returned":25000,"keys":0,"docs":100000}
//  -> Fix: index {city: 1}. Anchored prefix regexes (/^Del/) can then use it; /Del/ or /i regexes cannot efficiently.

// 3) Profiler: capture real slow queries (level 1 = only slower than slowms; here 0 logs everything for the demo)
d.setProfilingLevel(1, { slowms: 0 });
d.orders.find({ city: "Goa", amount: 7 }).toArray();        // a query with no matching index
d.system.profile.find({ op: "query" },
  { _id: 0, millis: 1, planSummary: 1, keysExamined: 1, docsExamined: 1, nreturned: 1 })
  .sort({ ts: -1 }).limit(1);                               // newest profile entry
// [ { keysExamined: 0, docsExamined: 100000, nreturned: 100, millis: 21, planSummary: 'COLLSCAN' } ]
//  (millis varies per machine). In production use slowms: 100 and level 1, not 0 (0 is heavy).
d.setProfilingLevel(0);                                     // turn profiling off again

// 4) Housekeeping: find unused indexes and drop redundant ones
d.orders.aggregate([{ $indexStats: {} }]);                  // shows accesses.ops per index
d.orders.dropIndex("userId_1");                             // redundant: prefix of the compound index
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose: declare the index in the schema, and log slow queries in the app
const mongoose = require('mongoose');
const orderSchema = new mongoose.Schema({
  userId: Number, status: String, amount: Number, createdAt: Date,
});
orderSchema.index({ userId: 1, status: 1, createdAt: -1 }); // ESR compound index, built by autoIndex

// In production set autoIndex: false and build indexes through a migration, because
// building an index on a huge collection takes time and resources.
// mongoose.connect(uri, { autoIndex: false });

const Order = mongoose.model('Order', orderSchema);

app.get('/api/users/:id/orders', async (req, res) => {
  const q = Order.find({ userId: Number(req.params.id), status: 'delivered' })
    .sort({ createdAt: -1 })     // matches the index order
    .limit(5)                    // always paginate; never return unbounded results
    .select('amount createdAt')  // fetch only what the UI needs
    .lean();                     // plain objects: faster, less memory
  if (req.query.explain) return res.json(await q.explain('executionStats')); // handy debug switch
  res.json(await q);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Wrong field order in the compound index
```javascript
// Wrong — range/sort field first; the equality fields can't narrow the scan well
db.orders.createIndex({ createdAt: -1, userId: 1, status: 1 });
// Right — ESR: equality (userId, status), then sort (createdAt)
db.orders.createIndex({ userId: 1, status: 1, createdAt: -1 });
```

❌ Mistake 2: Indexing every field "just in case"
✅ Correct: each index slows every insert/update and uses RAM. Index only for real query shapes; check `$indexStats` and drop unused ones.

❌ Mistake 3: Judging by time alone, or testing on tiny data
✅ Correct: look at keys/docs examined vs returned. A 2 ms COLLSCAN on 100 documents becomes 4 s on 100 million. Test on production-sized data and read `executionStats`, not just wall-clock time.

---

## 🧠 Tricky Interview Question

"The query uses `IXSCAN` yet is still slow. How is that possible?"

Answer: An index scan can still be bad: (1) the index is not selective (e.g., on `status` with 3 values), so it scans millions of keys; (2) `keysExamined` is huge but `nReturned` tiny, meaning most entries are filtered later; (3) there is still a blocking `SORT` stage because the index does not cover the sort; (4) a big `FETCH` reads many documents from disk because the working set does not fit RAM; (5) an anchored vs unanchored regex. Always compare `totalKeysExamined`, `totalDocsExamined` and `nReturned`, and look for a `SORT` stage.

---

## ⚫ Interview Questions + Answers

Q1: What do you look at in `explain("executionStats")`?
A1: `winningPlan` stages (COLLSCAN, IXSCAN, FETCH, SORT), `nReturned`, `totalKeysExamined`, `totalDocsExamined`, and `executionTimeMillis`. The goal is examined values close to `nReturned`.

Q2: What is the ESR rule?
A2: Order compound index fields as Equality, Sort, Range. Equality narrows to a contiguous index range, sort fields then come out pre-ordered (no in-memory SORT), and range fields last so they do not break sort order.

Q3: What is a covered query?
A3: One where all filter and projected fields are in the index, so MongoDB never reads documents (`totalDocsExamined: 0`, stage `PROJECTION_COVERED`). You must exclude `_id` from projection unless it is in the index.

Q4: How do you find slow queries in production?
A4: Profiler (`setProfilingLevel(1, {slowms: 100})` and read `system.profile`), the slow-query log in the mongod log, Atlas Performance Advisor, and `$currentOp` for queries running right now.

Q5: Why not just index every field?
A5: Each index adds write cost and memory; the planner may also pick a worse one. Design indexes from real query patterns, then remove unused ones via `$indexStats`.

---

## 🔷 When to Use + When Not to Use
✅ Use this process when:
- A page or API latency is high, or CPU/disk of the DB is climbing
- After a release adds a new filter/sort to a query

❌ Avoid / be careful when:
- Collection is tiny (index overhead isn't worth it)
- Building an index on a live huge collection at peak time (schedule it off-peak)
- Heavy write workloads where each extra index hurts throughput

---

## 📊 Visual Diagram
```
 Profiler / slow log ──> pick query
          │
          ▼
  explain("executionStats")
          │
   ┌──────┴────────────┐
   │ COLLSCAN or SORT? │── yes ──> design ESR compound index
   └──────┬────────────┘                   │
          │ no                             ▼
          ▼                        createIndex(...)
  keys/docs >> returned?  ── yes ──> more selective index / covered query
          │ no                             │
          ▼                                ▼
        done  <──── re-run explain: 100000 docs -> 5 docs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| COLLSCAN | Reads every document | हर document पढ़ना |
| IXSCAN | Reads via an index | Index से पढ़ना |
| `executionStats` | Real runtime numbers in explain | Explain में असली runtime numbers |
| ESR rule | Equality, Sort, Range index order | Index field का क्रम |
| Covered query | Answered from index only | सिर्फ index से जवाब |
| Profiler | Records slow operations | Slow operations record करता है |

---

## ⚡ 3-Line Summary
English:
1. Find the slow query (profiler), run `explain("executionStats")`, compare keys/docs examined to docs returned.
2. Fix with an ESR compound index: it took our query from 100,000 docs (COLLSCAN + SORT) to 5 docs (IXSCAN, no SORT).
3. Re-measure, drop redundant indexes, and avoid over-indexing because writes pay for every index.

Hindi:
1. Slow query ढूँढो (profiler), `explain("executionStats")` चलाओ, keys/docs examined की तुलना returned से करो।
2. ESR compound index से fix करो: हमारी query 1,00,000 docs (COLLSCAN + SORT) से 5 docs (IXSCAN, बिना SORT) पर आ गई।
3. दोबारा नापो, बेकार indexes हटाओ, और ज़्यादा indexing से बचो क्योंकि हर index का खर्च writes उठाते हैं।

---

## ➡️ Next Topic
**126. Migrate Schema Without Downtime** — Changing document shape in a live system safely.
