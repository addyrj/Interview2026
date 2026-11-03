# 52. MongoDB Profiler and Slow Queries
# हिंदी में: MongoDB Profiler और Slow Queries

---

## 🔵 Simple Definition (English)
The **database profiler** records details of operations (command, plan, keys/docs examined, duration) into a capped collection called **`system.profile`** in each database. It has 3 levels: **0** = off, **1** = log only operations slower than `slowms` (default 100 ms), **2** = log everything. Slow operations are also written to the **mongod log** regardless of profiler level once they exceed `slowms`.

## 🔵 सरल परिभाषा (Hindi)
**Database profiler** operations की details (command, plan, keys/docs examined, duration) हर database की एक capped collection **`system.profile`** में record करता है। इसके 3 levels हैं: **0** = बंद, **1** = सिर्फ `slowms` (default 100 ms) से धीमे operations log करो, **2** = सब कुछ log करो। `slowms` से ज़्यादा समय लेने वाले operations profiler level से स्वतंत्र, **mongod log** में भी लिखे जाते हैं।

---

## 🔴 Problem it Solves
In production you cannot run `explain()` on every query — you first need to know *which* queries are slow. Without a profiler you rely on user complaints or guesses. The profiler gives hard evidence: the exact filter, the plan used (`COLLSCAN` vs `IXSCAN`), `docsExamined`, `nreturned`, `millis`, time stamp, client and user. That turns "the app feels slow" into "this one query shape scans 5000 docs to return 101".

## 🔴 यह क्यों बना? (Hindi)
Production में हर query पर `explain()` नहीं चला सकते — पहले ये जानना ज़रूरी है कि *कौन सी* queries धीमी हैं। Profiler न हो तो user की शिकायतों या अंदाज़े पर निर्भर रहना पड़ता है। Profiler ठोस सबूत देता है: सटीक filter, कौन सा plan (`COLLSCAN` या `IXSCAN`), `docsExamined`, `nreturned`, `millis`, timestamp, client और user। इससे "app slow लग रहा है" बदलकर "ये query shape 101 return करने के लिए 5000 docs scan करती है" बन जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Enable profiling per database: `db.setProfilingLevel(1, { slowms: 50 })`.
Step 2 → For every operation on that database that exceeds `slowms` (level 1) — or every operation (level 2) — mongod writes a document into `<db>.system.profile`.
Step 3 → `system.profile` is a **capped collection** (1 MB default): oldest entries are overwritten automatically.
Step 4 → You query it like any collection: `db.system.profile.find({ millis: { $gt: 100 } }).sort({ ts: -1 })`.
Step 5 → Look at `planSummary` (COLLSCAN?), `docsExamined` vs `nreturned`, `hasSortStage`, `millis`, then use `explain()` on that query shape and fix the index.
Step 6 → Turn profiling back to 0 (or keep level 1 with a high `slowms`) because level 2 adds overhead.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → हर database के लिए profiling चालू करो: `db.setProfilingLevel(1, { slowms: 50 })`।
Step 2 → उस database पर `slowms` से ज़्यादा लगने वाले (level 1) या हर operation (level 2) के लिए mongod `<db>.system.profile` में एक document लिखता है।
Step 3 → `system.profile` एक **capped collection** है (default 1 MB): पुरानी entries अपने-आप overwrite हो जाती हैं।
Step 4 → इसे किसी भी collection की तरह query करो: `db.system.profile.find({ millis: { $gt: 100 } }).sort({ ts: -1 })`।
Step 5 → `planSummary` (COLLSCAN?), `docsExamined` बनाम `nreturned`, `hasSortStage`, `millis` देखो, फिर उस query shape पर `explain()` चलाकर index ठीक करो।
Step 6 → Profiling वापस 0 कर दो (या level 1 के साथ बड़ा `slowms` रखो) क्योंकि level 2 overhead बढ़ाता है।

---

## 🟡 Real World Example
**Razorpay's settlement service** had random 2-3 second spikes at 11 PM when nightly reconciliation jobs ran. The team set profiler level 1 with `slowms: 200` on the `payments` database for one night. Next morning, `system.profile` showed one query shape (`{ settlementId: ... }` with `planSummary: COLLSCAN`, `docsExamined: 8,000,000`) responsible for 90% of the slow entries. One index later, the spikes were gone — no guessing involved.

## 🟡 Real Example Hindi mein
**Razorpay की settlement service** में रात 11 बजे nightly reconciliation चलने पर random 2-3 second के spikes आते थे। Team ने एक रात के लिए `payments` database पर profiler level 1, `slowms: 200` लगाया। अगली सुबह `system.profile` में एक ही query shape (`{ settlementId: ... }`, `planSummary: COLLSCAN`, `docsExamined: 8,000,000`) 90% slow entries के लिए ज़िम्मेदार निकली। एक index लगाया और spikes ख़त्म — कोई अंदाज़ा नहीं।

---

## 💻 Code Example — Basic

Dataset: `shop.orders` (5000 docs, index `{ userId:1, createdAt:-1 }`). MongoDB 8.0.4. `millis`, `ts` vary per run.

```javascript
// mongosh
use shop

// Check current status
db.getProfilingStatus()
// Output: { was: 0, slowms: 100, sampleRate: 1, ok: 1 }   (0 = off)

// Level 1 with slowms 0 -> for the demo we log EVERYTHING (in production use e.g. 100)
db.setProfilingLevel(1, { slowms: 0 })
// Output: { was: 0, slowms: 100, sampleRate: 1, ok: 1 }   (shows the PREVIOUS setting)

// Run two queries: one bad (COLLSCAN + sort), one good (index)
db.orders.find({ amount: { $gt: 100 } }).sort({ amount: 1 }).toArray()
db.orders.find({ userId: 7 }).sort({ createdAt: -1 }).limit(3).toArray()

db.setProfilingLevel(0) // turn it off again

// Read the profile - what did mongod record?
db.system.profile.find({ ns: "shop.orders", op: "query" }).sort({ ts: 1 }).forEach(d =>
  print(d.op, d.planSummary, "keys:", d.keysExamined, "docs:", d.docsExamined,
        "returned:", d.nreturned, "sort:", d.hasSortStage))
// Output (real run):
// query COLLSCAN 0 5000 101 true            <- bad: scans 5000 docs, blocking sort, (101 = first batch)
// query IXSCAN { userId: 1, createdAt: -1 } 3 3 3  <- good: 3 keys, 3 docs, 3 returned

// Useful fields of a profile entry (real list):
// op, ns, command, keysExamined, docsExamined, hasSortStage, nreturned, numYield,
// millis, planSummary, execStats, ts, client, appName, user, responseLength ...

db.system.profile.isCapped()   // Output: true  (capped collection, 1 MB by default)
```

## 💻 Code Example — Advanced

```javascript
// Advanced: find the worst offenders, resize the profile, use the log, inspect running ops
use shop

// Top 5 slowest operations of the last hour
db.system.profile.find({
  ts: { $gt: new Date(Date.now() - 60 * 60 * 1000) },   // last hour
  millis: { $gt: 100 }                                   // slower than 100 ms
}).sort({ millis: -1 }).limit(5)

// Group by query shape to find which pattern hurts most (aggregation over the profile!)
db.system.profile.aggregate([
  { $match: { op: "query", ns: "shop.orders" } },
  { $group: {
      _id: "$planSummary",                    // COLLSCAN vs IXSCAN {…}
      count: { $sum: 1 },
      avgMs: { $avg: "$millis" },
      maxDocsExamined: { $max: "$docsExamined" } } },
  { $sort: { avgMs: -1 } },
])

// Make the profile bigger (default 1 MB wraps quickly): drop and recreate as capped
db.setProfilingLevel(0)
db.system.profile.drop()
db.createCollection("system.profile", { capped: true, size: 50 * 1024 * 1024 }) // 50 MB
db.setProfilingLevel(1, { slowms: 100 })

// Sample only 10% of slow ops to cut overhead on very busy servers
db.setProfilingLevel(1, { slowms: 100, sampleRate: 0.1 })

// What is running RIGHT NOW? Kill long runners.
db.currentOp({ active: true, secs_running: { $gt: 5 } })  // ops running > 5 seconds
// db.killOp(<opid>)                                       // stop a runaway op

// Without the profiler: slow ops are in mongod.log as JSON lines containing "Slow query"
// (threshold = slowms). Example filter: grep '"Slow query"' mongod.log
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const app = express();

// Helper endpoint (protect it with auth in real life!) to show recent slow ops
app.get('/admin/slow-queries', async (req, res) => {
  const db = mongoose.connection.db;                      // native driver Db object
  const rows = await db.collection('system.profile')      // profile is a normal collection
    .find({ millis: { $gt: 50 } })
    .sort({ ts: -1 }).limit(10)
    .project({ _id: 0, op: 1, ns: 1, millis: 1, planSummary: 1, docsExamined: 1, nreturned: 1 })
    .toArray();
  res.json(rows);
});

mongoose.connect('mongodb://127.0.0.1:27017/shop').then(async () => {
  // Turn on profiling from code at startup (needs permissions) - level 1, 100 ms
  await mongoose.connection.db.command({ profile: 1, slowms: 100 });
  app.listen(3000);
});

// Mongoose can also print every query it sends: mongoose.set('debug', true)
```
Note: on Atlas shared tiers (M0/M2/M5) `setProfilingLevel` is not available — use Atlas Performance Advisor / Query Profiler UI.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Leaving profiling level 2 on in production
```javascript
// Wrong — every operation is written to system.profile: extra write load on every request
db.setProfilingLevel(2)

// Right — level 1 with a sensible threshold (and optionally sampleRate)
db.setProfilingLevel(1, { slowms: 100 })
```

❌ Mistake 2: Assuming the profile keeps history
✅ Correct: `system.profile` is capped (1 MB by default). On a busy server it covers only minutes. Resize it (see Advanced) or ship the mongod logs to a log system.

❌ Mistake 3: Forgetting profiling is per database (and per mongod)
✅ Correct: `use shop; db.setProfilingLevel(1)` affects only `shop` on that node. On a replica set, set it on the node you want to observe (secondaries too, if reads go there).

---

## 🧠 Tricky Interview Question

```javascript
db.setProfilingLevel(0)          // profiler OFF
db.orders.find({}).sort({ amount: 1 }).toArray()   // takes 450 ms (slowms is 100)
// Is this query recorded anywhere?
```
Answer: **Yes — in the mongod log**, not in `system.profile`. Operations slower than `slowms` are logged as "Slow query" lines in the server log even when the profiler level is 0. The profiler (`system.profile`) only gets documents at level 1 (slow ones) or level 2 (all). Also, `slowms` is both the profiler threshold at level 1 *and* the log threshold. And `db.setProfilingLevel(0, { slowms: 500 })` can raise the log threshold without enabling the profiler.

---

## ⚫ Interview Questions + Answers

Q1: What are the profiler levels?
A1: 0 = off (slow ops still go to the log), 1 = record only ops slower than `slowms`, 2 = record all operations. Controlled with `db.setProfilingLevel(level, { slowms, sampleRate })`.

Q2: Where does profiler data live, and what are its limits?
A2: In the capped collection `<db>.system.profile` (1 MB default). Old entries are overwritten, it is per-database, and data is lost when you drop it or resize it.

Q3: Which profile fields tell you a query is inefficient?
A3: `planSummary: COLLSCAN`, large `docsExamined`/`keysExamined` compared to `nreturned`, `hasSortStage: true`, high `millis`, high `numYield`.

Q4: Profiler vs `explain()` — difference?
A4: The profiler tells you *what actually ran in the real workload and how long it took* (discovery). `explain()` shows the plan for a specific query you hand it (diagnosis). Use profiler to find, explain to fix.

Q5: What is the performance cost of profiling?
A5: Level 2 writes a document for every operation, which can seriously hurt throughput. Level 1 with a reasonable `slowms` (and `sampleRate` if needed) is usually cheap.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Investigating latency spikes or a slow endpoint in a real workload
- Verifying that a new index is actually being hit (`planSummary: IXSCAN`)
- Building a periodic "top slow queries" report

❌ Avoid when:
- Running level 2 on a busy production database
- Using it as long-term monitoring — use logs/APM/Atlas instead (the profile is small and capped)
- On Atlas free/shared tiers (not supported)

---

## 📊 Visual Diagram
```
  App ──► mongod ──► executes op ──► took ms?
                                       │
                 ┌─────────────────────┼──────────────────────┐
              level 0               level 1                 level 2
         (log only if > slowms)  (profile if > slowms)    (profile everything)
                 │                     │                      │
                 ▼                     ▼                      ▼
            mongod.log        <db>.system.profile (capped, 1 MB)
                                       │
                          find / aggregate on it
                                       ▼
                  COLLSCAN? docsExamined >> nreturned? ──► explain() ──► add index
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Profiler | Records operation details | Operations का record रखने वाला |
| system.profile | Capped collection storing the records | Records की capped collection |
| slowms | Slow-operation threshold (default 100) | धीमे operation की सीमा |
| sampleRate | Fraction of slow ops to record | कितने प्रतिशत ops record हों |
| planSummary | Plan used (COLLSCAN / IXSCAN) | इस्तेमाल हुआ plan |
| currentOp | Shows operations running now | अभी चल रहे operations |
| Capped collection | Fixed-size, overwrites oldest | Fixed size, पुराना overwrite |

---

## ⚡ 3-Line Summary
English:
1. The profiler writes slow (level 1) or all (level 2) operations into the capped `system.profile` collection; slow ops also hit the mongod log.
2. Read `planSummary`, `docsExamined`, `nreturned`, `millis` to spot COLLSCANs and bad plans, then fix with `explain()` + indexes.
3. Keep level 1 with a sane `slowms`; avoid level 2 in production; not available on Atlas shared tiers.

Hindi:
1. Profiler धीमे (level 1) या सभी (level 2) operations को capped `system.profile` collection में लिखता है; धीमे ops mongod log में भी जाते हैं।
2. `planSummary`, `docsExamined`, `nreturned`, `millis` पढ़कर COLLSCAN और खराब plans पकड़ो, फिर `explain()` + indexes से ठीक करो।
3. Level 1 और समझदार `slowms` रखो; production में level 2 से बचो; Atlas shared tiers पर उपलब्ध नहीं।

---

## ➡️ Next Topic
**53. Aggregation Pipeline — Introduction** — Processing documents through multi-stage pipelines.
