# 127. MongoDB Interview Classics — 20 Most Asked Questions
# हिंदी में: MongoDB के 20 सबसे ज़्यादा पूछे जाने वाले Interview Questions

> ✅ Code verified on a real `mongod` v8.0.4. ObjectIds/timestamps vary; fixed `_id`s used below.

---

## 🔵 Simple Definition (English)
This is a rapid-fire revision sheet: the 20 questions that appear in almost every MongoDB interview (backend, Node.js, data roles), each with a short, correct answer and, where useful, a command that was actually run.

## 🔵 सरल परिभाषा (Hindi)
यह तेज़ revision sheet है: वे 20 सवाल जो लगभग हर MongoDB interview में आते हैं, हर एक का छोटा और सही जवाब, और जहाँ ज़रूरी हो वहाँ असल में चलाया गया command।

---

## 🔴 Problem it Solves
Candidates know topics separately (CRUD, indexes, aggregation, replication) but freeze when the interviewer jumps between them. A single sheet that links "what + why + gotcha" for each classic builds the fast recall interviews reward.

## 🔴 यह क्यों बना? (Hindi)
Candidates को topics अलग-अलग आते हैं (CRUD, indexes, aggregation, replication) पर interviewer के बीच में topic बदलते ही अटक जाते हैं। हर classic के लिए "क्या + क्यों + gotcha" वाली एक sheet तेज़ recall बनाती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Read the question, answer in one sentence first (definition).
Step 2 → Add the "why/trade-off" (what an interviewer actually grades).
Step 3 → Give a tiny example command.
Step 4 → Mention the gotcha (the follow-up trap).
Step 5 → Practise the verified demo below so you can explain real output.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → सवाल पढ़ो, पहले एक वाक्य में जवाब (definition)।
Step 2 → "क्यों/trade-off" जोड़ो (interviewer यही परखता है)।
Step 3 → छोटा example command दो।
Step 4 → Gotcha बताओ (follow-up का जाल)।
Step 5 → नीचे का verified demo practise करो ताकि असली output समझा सको।

---

## 🟡 Real World Example
**Flipkart orders service** is the running example: `orders` (user, city, amt, status) and `users`. Nearly every classic question can be asked against it: "total paid revenue per city" (aggregation), "which users have no orders" ($lookup), "why is this query slow" (explain/index), "what if the primary dies" (replica set).

## 🟡 Real Example Hindi mein
**Flipkart orders service** हमारा running example है: `orders` (user, city, amt, status) और `users`। लगभग हर classic सवाल इस पर पूछा जा सकता है: "city-wise paid revenue" (aggregation), "किन users के orders नहीं हैं" ($lookup), "query slow क्यों है" (explain/index), "primary मर जाए तो" (replica set)।

---

## 💻 Code Example — Basic

```javascript
// mongosh — shared seed data for the demos
const d = db.getSiblingDB('cls');               // use database "cls"
d.dropDatabase();                               // clean slate
d.orders.insertMany([                           // four orders
  { _id: 1, user: "u1", city: "Pune",  amt: 500, status: "paid" },
  { _id: 2, user: "u1", city: "Pune",  amt: 300, status: "paid" },
  { _id: 3, user: "u2", city: "Delhi", amt: 900, status: "paid" },
  { _id: 4, user: "u3", city: "Delhi", amt: 100, status: "cancelled" }
]);
d.users.insertMany([{ _id: "u1", name: "Aarav" }, { _id: "u2", name: "Priya" }, { _id: "u4", name: "Zed" }]);

// Q: revenue per city for paid orders, highest first  (GROUP BY)
d.orders.aggregate([
  { $match: { status: "paid" } },                                   // WHERE status='paid'
  { $group: { _id: "$city", total: { $sum: "$amt" }, n: { $sum: 1 } } }, // GROUP BY city
  { $sort: { total: -1 } }                                          // ORDER BY total DESC
]).forEach(x => printjson(x));
// Output:
// { _id: 'Delhi', total: 900, n: 1 }
// { _id: 'Pune',  total: 800, n: 2 }

// Q: LEFT JOIN users -> orders, count per user
d.users.aggregate([
  { $lookup: { from: "orders", localField: "_id", foreignField: "user", as: "orders" } },
  { $project: { name: 1, count: { $size: "$orders" } } }            // size of joined array
]).forEach(x => printjson(x));
// Output:
// { _id: 'u1', name: 'Aarav', count: 2 }
// { _id: 'u2', name: 'Priya', count: 1 }
// { _id: 'u4', name: 'Zed',   count: 0 }   <- $lookup is a LEFT outer join (users w/o orders kept)
```

## 💻 Code Example — Advanced

```javascript
// mongosh — proving index behaviour with explain (verified output)
d.orders.createIndex({ city: 1, amt: -1 });      // compound index: equality field first, sort field next

// Equality on city + sort on amt: index gives the order, so NO in-memory SORT stage
let e = d.orders.find({ city: "Pune" }).sort({ amt: -1 }).explain("executionStats");
print(e.queryPlanner.winningPlan.stage, e.queryPlanner.winningPlan.inputStage.stage,
      e.executionStats.totalDocsExamined);
// Output: FETCH IXSCAN 2        <- index scan, only 2 docs examined

// Query on an un-indexed field => full collection scan
let e2 = d.orders.find({ status: "paid" }).explain("executionStats");
print(e2.queryPlanner.winningPlan.stage, e2.executionStats.totalDocsExamined);
// Output: COLLSCAN 4            <- scanned ALL docs

// Covered query: filter + projection use ONLY index fields and exclude _id => zero doc fetches
let e3 = d.orders.find({ city: "Pune" }, { _id: 0, city: 1, amt: 1 }).explain("executionStats");
print(e3.queryPlanner.winningPlan.stage, e3.executionStats.totalDocsExamined);
// Output: PROJECTION_COVERED 0

// Upsert: update if exists else insert
printjson(d.c.updateOne({ _id: "x" }, { $inc: { n: 1 } }, { upsert: true }));
// Output: { acknowledged: true, insertedId: 'x', matchedCount: 0, modifiedCount: 0, upsertedCount: 1 }

// Unique index violation => error code 11000
d.u.createIndex({ e: 1 }, { unique: true }); d.u.insertOne({ e: "a" });
try { d.u.insertOne({ e: "a" }) } catch (x) { print(x.code) }     // Output: 11000

// null vs missing field
d.n.insertMany([{ a: null }, {}, { a: 1 }]);
print(d.n.countDocuments({ a: null }), d.n.countDocuments({ a: { $exists: false } }));
// Output: 2 1     <- {a:null} matches BOTH null and missing; $exists:false matches only missing

// Arrays of objects: $elemMatch vs dot notation
d.arr.insertOne({ s: [{ k: 1, v: 5 }, { k: 2, v: 9 }] });
print(d.arr.countDocuments({ s: { $elemMatch: { k: 1, v: 9 } } }),   // same element must match both
      d.arr.countDocuments({ "s.k": 1, "s.v": 9 }));                  // conditions may hit different elements
// Output: 0 1

// Range pagination (better than skip on big data)
print(JSON.stringify(d.orders.find({ _id: { $gt: 2 } }).sort({ _id: 1 }).limit(1).toArray()));
// Output: [{"_id":3,"user":"u2","city":"Delhi","amt":900,"status":"paid"}]
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Classic: pagination + error handling for duplicate key, in Express + Mongoose
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

const Order = mongoose.model('Order', new mongoose.Schema({
  user: String, city: String, amt: Number, status: String
}));

// Range ("keyset") pagination: pass the last _id seen; stays fast at page 10,000
app.get('/orders', async (req, res) => {
  const filter = req.query.after ? { _id: { $gt: req.query.after } } : {}; // continue after cursor
  const rows = await Order.find(filter).sort({ _id: 1 }).limit(20).lean(); // lean() = plain objects, faster
  res.json({ rows, next: rows.length ? rows[rows.length - 1]._id : null });
});

// Duplicate key => 409, not 500
app.post('/users', async (req, res) => {
  try { res.status(201).json(await mongoose.connection.collection('users').insertOne(req.body)); }
  catch (e) { res.status(e.code === 11000 ? 409 : 500).json({ error: e.message }); }
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deep `skip()` pagination
```javascript
// Wrong — server walks past 1,000,000 docs before returning 20
db.orders.find().sort({ _id: 1 }).skip(1000000).limit(20);
// Right — range query using the last seen _id
db.orders.find({ _id: { $gt: lastId } }).sort({ _id: 1 }).limit(20);
```

❌ Mistake 2: Dot notation on arrays of objects when one element must match both
```javascript
// Wrong — matched a doc where different elements satisfied each condition
db.arr.find({ "s.k": 1, "s.v": 9 });          // returns the doc (count 1)
// Right
db.arr.find({ s: { $elemMatch: { k: 1, v: 9 } } }); // count 0, correct
```

❌ Mistake 3: Expecting `{a: null}` to find only null
✅ Correct: it also matches documents where `a` is missing. Add `{a:{$type:10}}` (null type) to isolate real nulls.

---

## 🧠 Tricky Interview Question
**Q:** `db.orders.find({ city: "Pune" }).sort({ amt: -1 })` with only an index `{ city: 1 }` vs `{ city: 1, amt: -1 }`. What differs?

**Answer:** With `{city:1}` MongoDB finds Pune docs through the index but must **sort in memory** (a `SORT` stage; fails/spills past the sort memory limit unless `allowDiskUse`). With `{city:1, amt:-1}` the index entries are already ordered by amt within city, so the plan is `FETCH -> IXSCAN` with no sort (verified above, 2 docs examined). Rule: **Equality, Sort, Range (ESR)** for compound index field order.

---

## ⚫ Interview Questions + Answers (the 20 classics)

Q1: What is MongoDB and why use it?
A1: A document database storing BSON. Flexible schema, embedded data, horizontal scaling (sharding), rich query/aggregation. Use when data is hierarchical or evolves fast.

Q2: What is BSON?
A2: Binary JSON: JSON plus extra types (ObjectId, Date, Decimal128, Binary, int/long) and length prefixes for fast traversal.

Q3: What is `ObjectId`?
A3: 12 bytes: 4-byte timestamp, 5-byte random value, 3-byte counter. Roughly time-ordered, unique without coordination. It's not a string; wrap with `new ObjectId(str)`.

Q4: Embedding vs referencing?
A4: Embed for one-to-few, data read together, bounded growth. Reference for one-to-many unbounded, many-to-many, data shared or updated independently. 16 MB document limit forces reference for unbounded arrays.

Q5: What is the max document size?
A5: 16 MB. Use GridFS for larger files.

Q6: How do indexes work and what are the costs?
A6: B-tree structures that avoid collection scans. Costs: slower writes, more RAM/disk. Verify with `explain("executionStats")`: want `IXSCAN`, small `totalDocsExamined`.

Q7: What is a compound index and what is ESR?
A7: Index on multiple fields; order matters (prefix rule). Put Equality fields first, then Sort, then Range.

Q8: What is a covered query?
A8: Filter and projection use only indexed fields (exclude `_id` unless indexed); no document fetch (`PROJECTION_COVERED`, 0 docs examined, shown above).

Q9: Aggregation pipeline vs `find`?
A9: Pipeline = ordered stages (`$match`, `$group`, `$lookup`, `$project`, `$sort`...). Put `$match`/`$sort` early to use indexes.

Q10: Does MongoDB support joins?
A10: `$lookup` does a left outer join (verified: user with no orders kept, count 0). It is not a replacement for good schema design; heavy joins signal a modelling problem.

Q11: Replica set?
A11: A group of nodes: one primary takes writes, secondaries replicate via the oplog; automatic election on failure (needs a majority). Gives HA, not scaling.

Q12: Sharding?
A12: Horizontal partitioning by shard key across shards; `mongos` routes. Pick a high-cardinality, well-distributed key; avoid monotonically increasing keys (hot shard) unless hashed.

Q13: Write concern vs read concern?
A13: Write concern (`w:1`, `w:"majority"`, `j`) = acknowledgement level. Read concern (`local`, `majority`, `snapshot`) = data visibility/consistency. `majority` for both avoids rollback surprises.

Q14: Transactions?
A14: Multi-document ACID since 4.0 (replica sets) and 4.2 (sharded). Cost latency/locks; prefer a document model where one document = one atomic unit.

Q15: Are single-document operations atomic?
A15: Yes, including nested fields and arrays inside that document.

Q16: `updateOne` vs `replaceOne`, and `$set` vs replacement?
A16: Update operators (`$set`, `$inc`) change fields; passing a plain document to replace swaps the whole document (except `_id`). Forgetting `$set` in a replacement is a classic data-loss bug.

Q17: What are TTL and partial/sparse/unique indexes?
A17: TTL deletes docs after N seconds (background monitor ~60 s). Partial indexes only index docs matching a filter (smaller). Sparse skips docs missing the field. Unique enforces uniqueness (error 11000).

Q18: How to find and fix a slow query?
A18: Profiler/slow log, `explain`, add/adjust index (ESR), project fewer fields, avoid deep `skip`, avoid unanchored regex, check cardinality.

Q19: MongoDB vs SQL, when to pick which?
A19: Mongo: variable shape, nested reads, scale-out. SQL: heavy relational integrity, complex multi-table joins and transactions as the norm.

Q20: What is `$exists:false` vs `null` query semantics?
A20: `{a:null}` matches null OR missing; `{a:{$exists:false}}` only missing (verified: 2 vs 1).

---

## 🔷 When to Use + When Not to Use
✅ Use this sheet when:
- Final-day revision before a backend/Node interview
- Linking topics (index + aggregation + replication) in one answer

❌ Don't rely on it when:
- You haven't run the commands yourself; interviewers ask "what does explain show?"
- Preparing for deep DBA topics (WiredTiger internals, chunk migration), which need dedicated study

---

## 📊 Visual Diagram
```
INTERVIEW MAP
──────────────────────────────────────────────
 Data model ── embed vs reference ── 16MB limit
     │
 Query ── find ── $elemMatch ── null vs missing
     │
 Speed ── index ── ESR ── covered ── explain
     │
 Analytics ── aggregate ── $lookup (left join)
     │
 Reliability ── replica set ── write/read concern
     │
 Scale ── sharding ── shard key (cardinality!)
     │
 Consistency ── single doc atomic ── transactions
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BSON | Binary JSON with extra types | Extra types वाला binary JSON |
| ESR | Equality, Sort, Range index order | Compound index का क्रम |
| Covered query | Answered from index alone | सिर्फ index से जवाब |
| Oplog | Log replicated to secondaries | Secondaries को भेजा जाने वाला log |
| Shard key | Field deciding data placement | Data placement तय करने वाला field |
| Write concern | Write acknowledgement level | Write की पुष्टि का स्तर |
| COLLSCAN | Full collection scan | पूरा collection scan |

---

## ⚡ 3-Line Summary
English:
1. Know the 20 classics as definition + trade-off + gotcha, backed by a command you ran.
2. Most traps: null vs missing, `$elemMatch`, deep `skip`, ESR index order, `$set` vs replace.
3. Always prove performance claims with `explain("executionStats")`.

Hindi:
1. 20 classics को definition + trade-off + gotcha के साथ याद करो, और खुद चलाए command से backup दो।
2. ज़्यादातर जाल: null vs missing, `$elemMatch`, deep `skip`, ESR index order, `$set` vs replace।
3. Performance के दावे हमेशा `explain("executionStats")` से साबित करो।

---

## ➡️ Next Topic
**128.** Continue with the next section of the notes or revisit **126. Migrate Schema Without Downtime** for a full end-to-end scenario answer.
