# 53. Aggregation Pipeline — Introduction
# हिंदी में: Aggregation Pipeline — परिचय

---

## 🔵 Simple Definition (English)
The **aggregation pipeline** is MongoDB's framework for data processing: an array of **stages** where each stage transforms the stream of documents and passes the result to the next, like a factory conveyor belt (or Unix pipes). Common stages: `$match` (filter), `$group` (aggregate), `$sort`, `$limit`, `$project`, `$lookup` (join), `$unwind`. It is the MongoDB equivalent of SQL `WHERE` + `GROUP BY` + `ORDER BY` + `JOIN`, run inside the database.

## 🔵 सरल परिभाषा (Hindi)
**Aggregation pipeline** MongoDB का data processing framework है: **stages** का array, जहाँ हर stage documents की stream बदलता है और नतीजा अगले stage को देता है, जैसे factory की conveyor belt (या Unix pipes)। मुख्य stages: `$match` (filter), `$group` (aggregate), `$sort`, `$limit`, `$project`, `$lookup` (join), `$unwind`। यह SQL के `WHERE` + `GROUP BY` + `ORDER BY` + `JOIN` का MongoDB रूप है, जो database के अंदर चलता है।

---

## 🔴 Problem it Solves
`find()` can only filter and project documents. Reports like "revenue per city for paid orders, top 2" would require pulling all documents into the app and looping - slow, memory hungry, network heavy. The pipeline computes it on the server, close to the data, can use indexes in early stages, and returns only the small result.

## 🔴 यह क्यों बना? (Hindi)
`find()` सिर्फ filter और project कर सकता है। "paid orders में city के हिसाब से revenue, top 2" जैसी report के लिए सारे documents app में लाकर loop करना पड़ता - धीमा, memory-भारी, network-भारी। Pipeline यह server पर data के पास करता है, शुरुआती stages में index use कर सकता है, और सिर्फ छोटा result लौटाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Call `db.collection.aggregate([ stage1, stage2, ... ])`. Each stage is an object with one `$operator`.
Step 2 → Documents flow into stage 1 from the collection; its output flows into stage 2, and so on. Order matters.
Step 3 → Put `$match` (and `$sort`/`$limit` on indexed fields) **first**: only the first stages can use indexes, and filtering early shrinks later work.
Step 4 → `$group` groups by `_id` expression and computes accumulators: `$sum`, `$avg`, `$min`, `$max`, `$push`, `$addToSet`, `$first`.
Step 5 → `$sort` then `$limit` together are optimized into a top-k sort.
Step 6 → Result is a cursor (default batch 101 documents in mongosh); each stage in memory is limited to 100 MB unless `allowDiskUse: true` (default allowed in newer versions for many stages).
Step 7 → Inspect with `.explain()` to see which stages were pushed down and whether an index was used.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `db.collection.aggregate([ stage1, stage2, ... ])` call करो। हर stage में एक `$operator` वाला object होता है।
Step 2 → Documents collection से stage 1 में जाते हैं; उसका output stage 2 में, आदि। क्रम मायने रखता है।
Step 3 → `$match` (और indexed fields पर `$sort`/`$limit`) **सबसे पहले** रखो: सिर्फ शुरुआती stages index use कर सकते हैं और जल्दी filter करने से आगे का काम घटता है।
Step 4 → `$group` `_id` expression से group करता है और accumulators निकालता है: `$sum`, `$avg`, `$min`, `$max`, `$push`, `$addToSet`, `$first`।
Step 5 → `$sort` के बाद `$limit` मिलकर top-k sort में optimize होते हैं।
Step 6 → Result cursor है; memory में हर stage की 100 MB limit है जब तक `allowDiskUse: true` न हो।
Step 7 → `.explain()` से देखो कौन से stages push down हुए और index इस्तेमाल हुआ या नहीं।

---

## 🟡 Real World Example
**Swiggy** daily ops dashboard: "Total revenue and order count per city for `paid` orders, top cities first". The pipeline `$match` (status) -> `$group` (by city, sum amount, count) -> `$sort` (revenue) -> `$limit` runs inside MongoDB and returns four rows instead of shipping lakhs of orders to the app.

## 🟡 Real Example Hindi mein
**Swiggy** का daily ops dashboard: "`paid` orders के लिए हर city का कुल revenue और order count, ऊपर वाली cities पहले"। Pipeline `$match` (status) -> `$group` (city से, amount का sum, count) -> `$sort` (revenue) -> `$limit` MongoDB के अंदर चलता है और लाखों orders app को भेजने की जगह चार rows लौटाता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh (verified on MongoDB 8.0.4). 5000 orders: status new/paid/shipped, cities Delhi/Pune/Mumbai/Goa
use idx_demo
db.orders.aggregate([
  { $match: { status: "paid" } },                                        // 1) WHERE status = 'paid'
  { $group: { _id: "$city",                                              // 2) GROUP BY city
              rev: { $sum: "$amount" },                                  //    SUM(amount)
              n:   { $sum: 1 } } },                                      //    COUNT(*)
  { $sort: { rev: -1 } },                                                // 3) ORDER BY rev DESC
  { $limit: 2 }                                                          // 4) LIMIT 2
])
// Output (verified, row order by revenue):
// [ { _id: 'Goa',    rev: 21668, n: 417 },
//   { _id: 'Mumbai', rev: 21216, n: 416 } ]
```

## 💻 Code Example — Advanced

```javascript
// Build the pipeline step by step and look at the data after each stage
const p1 = [{ $match: { status: "paid" } }]                                    // stage 1 only
db.orders.aggregate([...p1, { $count: "paidOrders" }])                         // Output: [ { paidOrders: 1667 } ]

// $project reshapes documents; computed fields with expressions
db.orders.aggregate([
  { $match: { status: "paid" } },
  { $project: { _id: 0, city: 1, amountWithGst: { $multiply: ["$amount", 1.18] } } },  // add 18% GST
  { $limit: 2 }
])

// Several accumulators at once, $addToSet collects unique values
db.orders.aggregate([
  { $group: { _id: "$city", avg: { $avg: "$amount" }, max: { $max: "$amount" }, statuses: { $addToSet: "$status" } } },
  { $sort: { _id: 1 } }
])

// Inspect the plan: the first $match uses an index if one exists on status
db.orders.explain().aggregate([{ $match: { status: "paid" } }, { $group: { _id: "$city", rev: { $sum: "$amount" } } }])

// Big data: let stages spill to disk
db.orders.aggregate([{ $group: { _id: "$userId", total: { $sum: "$amount" } } }], { allowDiskUse: true })
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// GET /api/reports/revenue?status=paid
app.get('/api/reports/revenue', async (req, res) => {
  const status = req.query.status || 'paid';
  const report = await db.collection('orders').aggregate([
    { $match: { status } },                                              // always filter first
    { $group: { _id: '$city', rev: { $sum: '$amount' }, n: { $sum: 1 } } },
    { $sort: { rev: -1 } },
    { $limit: 10 },
  ]).toArray();                                                          // aggregate returns a cursor -> toArray()
  res.json(report);
});

// Mongoose: Model.aggregate() does NOT cast values by schema - cast ObjectId yourself
// const { Types } = require('mongoose');
// Order.aggregate([{ $match: { userId: new Types.ObjectId(req.params.id) } }, ...])
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting `$match` after `$group`
```javascript
// Wrong - groups ALL documents, then filters (no index, a lot of work)
db.orders.aggregate([{ $group: { _id: "$city", rev: { $sum: "$amount" } } }, { $match: { _id: "Goa" } }])
// Right - filter first
db.orders.aggregate([{ $match: { city: "Goa" } }, { $group: { _id: "$city", rev: { $sum: "$amount" } } }])
```

❌ Mistake 2: Forgetting that `$sum` on a missing/non-numeric field counts as 0, silently
✅ Correct: use `$sum: 1` to count documents and check types; non-numeric values are ignored by `$sum`.

❌ Mistake 3: In Mongoose, passing string ids to `$match` in `aggregate()` - no automatic casting, so nothing matches.

---

## 🧠 Tricky Interview Question

```javascript
db.orders.aggregate([
  { $group: { _id: "$city", n: { $sum: 1 } } },
  { $match: { status: "paid" } }
])
```
Answer: Returns an **empty array**. After `$group`, documents only contain `_id` and `n`; the original `status` field is gone, so `$match` on `status` matches nothing. Each stage sees only the output of the previous stage. Move `$match` before `$group`.

---

## ⚫ Interview Questions + Answers

Q1: What is an aggregation pipeline?
A1: An ordered array of stages that transform documents; each stage's output is the next stage's input.

Q2: Why put `$match` first?
A2: Only leading stages can use indexes, and filtering early reduces the documents later stages process.

Q3: `find()` vs `aggregate()`?
A3: `find` filters/projects/sorts; `aggregate` additionally groups, joins (`$lookup`), reshapes, unwinds arrays and computes expressions.

Q4: What is the `$group` stage's `_id`?
A4: The grouping key expression (`"$city"`, a compound object, or `null` for one group over all documents).

Q5: How to handle large aggregations?
A5: Filter early, project only needed fields, use indexes, and pass `{ allowDiskUse: true }` for memory-heavy stages (100 MB per stage limit).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reports, analytics, grouping, joins, reshaping data on the server

❌ Avoid when:
- A simple `find()` with index does the job
- Heavy analytics at huge scale where a data warehouse is better

---

## 📊 Visual Diagram
```
orders (5000 docs)
   │
   ▼
[ $match {status:"paid"} ]      -> 1667 docs
   │
   ▼
[ $group by city: sum, count ]  -> 4 docs  {Goa, Mumbai, Pune, Delhi}
   │
   ▼
[ $sort rev -1 ]                -> ordered
   │
   ▼
[ $limit 2 ]                    -> 2 docs  -> result cursor
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pipeline | Ordered list of stages | Stages की क्रमबद्ध list |
| Stage | One transformation step | एक transformation चरण |
| $match | Filter stage | Filter stage |
| $group | Group + accumulate | Group और accumulate |
| Accumulator | $sum, $avg, etc. | $sum, $avg आदि |
| allowDiskUse | Spill big stages to disk | बड़े stages disk पर |

---

## ⚡ 3-Line Summary
English:
1. The pipeline is an ordered array of stages; each stage feeds the next.
2. Filter early (`$match` first) so indexes and smaller data help every later stage.
3. `$group` + accumulators replace SQL GROUP BY; each stage only sees the previous stage's output fields.

Hindi:
1. Pipeline stages का क्रमबद्ध array है; हर stage अगले को देता है।
2. जल्दी filter करो (`$match` पहले) ताकि index और छोटा data आगे के हर stage की मदद करे।
3. `$group` + accumulators SQL GROUP BY की जगह लेते हैं; हर stage सिर्फ पिछले stage के output fields देखता है।

---

## ➡️ Next Topic
**54. $match and $project**
