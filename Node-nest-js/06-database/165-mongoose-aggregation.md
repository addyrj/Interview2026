# 165. Mongoose Aggregation
# हिंदी में: Mongoose Aggregation — Multi-Stage Data Processing

---

## 🔵 Simple Definition (English)
Mongoose **Aggregation** exposes MongoDB's aggregation pipeline — a sequence of data-processing STAGES (`$match`, `$group`, `$sort`, `$project`, `$lookup`, `$unwind`, etc.) chained together, where each stage's output feeds into the next. It's MongoDB's equivalent of SQL's `GROUP BY`, `JOIN`, and complex reporting queries, called via `Model.aggregate([stage1, stage2, ...])`.

## 🔵 सरल परिभाषा (Hindi)
Mongoose **Aggregation** MongoDB के aggregation pipeline को expose करता है — data-processing STAGES (`$match`, `$group`, `$sort`, `$project`, `$lookup`, `$unwind`) की sequence, जहाँ हर stage का output अगले में जाता है। ये MongoDB का SQL के `GROUP BY`, `JOIN`, complex reporting queries का equivalent है, `Model.aggregate([stage1, stage2, ...])` से call होता है।

---

## 🔴 Problem it Solves
Simple `find()` queries can filter and sort, but can't compute GROUPED statistics (average order value per restaurant), combine data across collections (like a JOIN), or reshape documents heavily — doing this in application code means pulling potentially millions of documents into Node.js memory and processing them manually, which is slow and memory-intensive. The aggregation pipeline pushes this computation INTO the database engine, processing data close to where it lives and returning only the final, already-computed result.

## 🔴 यह क्यों बना? (Hindi)
Simple `find()` queries filter और sort कर सकती हैं, पर GROUPED statistics compute नहीं कर सकती (restaurant के हिसाब से average order value), collections के बीच data combine नहीं कर सकती (JOIN जैसा), या documents को heavily reshape नहीं कर सकती — ये application code में करना मतलब लाखों documents Node.js memory में लाना, slow और memory-intensive। Aggregation pipeline इस computation को database engine के अंदर push करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `Model.aggregate([...])` takes an ARRAY of stage objects, executed in order.
Step 2 → `$match` filters documents (like `WHERE`) — put it EARLY in the pipeline to reduce data processed by later stages.
Step 3 → `$group` groups documents by a key (`_id: '$field'`) and computes aggregates (`$sum`, `$avg`, `$min`, `$max`, `$push`, `$count`) per group.
Step 4 → `$lookup` performs a JOIN-like operation with another collection, `$unwind` flattens an array field into separate documents (one per array element), `$project`/`$addFields` reshape/compute new fields.
Step 5 → `$sort`, `$limit`, `$skip` at the end handle pagination/ordering of the final results — order matters: `$sort` before `$limit` gives top-N, not arbitrary N.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `Model.aggregate([...])` stage objects का ARRAY लेता है, order में execute होता है।
Step 2 → `$match` documents filter करता है (`WHERE` जैसा) — pipeline में EARLY रखो ताकि बाद के stages कम data process करें।
Step 3 → `$group` documents को key से group करता है और per group aggregates compute करता है (`$sum`, `$avg`, etc.)।
Step 4 → `$lookup` JOIN जैसा operation करता है, `$unwind` array field को flatten करता है, `$project`/`$addFields` fields reshape/compute करते हैं।
Step 5 → `$sort`, `$limit`, `$skip` आख़िर में pagination/ordering के लिए — order matters।

---

## 🟡 Real World Example
**Zomato's restaurant-analytics dashboard** computes "top 10 highest-rated restaurants by cuisine type, with at least 50 orders" using a single aggregation pipeline: `$match` (filter active restaurants) → `$lookup` (join with Orders collection) → `$group` (group by cuisine, compute average rating and order count) → `$match` (filter groups with orderCount >= 50) → `$sort` (by avg rating) → `$limit` (top 10). This entire report runs AS ONE database query, computed server-side, instead of pulling millions of order records into the Node.js app to calculate manually.

## 🟡 Real Example Hindi mein
**Zomato का restaurant-analytics dashboard** "cuisine type के हिसाब से top 10 highest-rated restaurants (कम से कम 50 orders वाले)" एक ही aggregation pipeline से compute करता है। पूरा report एक database query के रूप में चलता है, server-side computed, Node.js app में लाखों order records लाकर manually calculate करने के बजाय।

---

## 💻 Code Example — Basic

```javascript
// mongoose-aggregation-basic.js
const mongoose = require('mongoose');

const orderSchema = new mongoose.Schema({
  restaurantId: String,
  amount: Number,
  status: String,
  createdAt: { type: Date, default: Date.now },
});
const Order = mongoose.model('Order', orderSchema);

async function main() {
  await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/aggregation_demo');

  await Order.insertMany([
    { restaurantId: 'r1', amount: 400, status: 'completed' },
    { restaurantId: 'r1', amount: 600, status: 'completed' },
    { restaurantId: 'r2', amount: 300, status: 'completed' },
    { restaurantId: 'r1', amount: 100, status: 'cancelled' },
  ]);

  // Pipeline: filter completed orders -> group by restaurant -> compute totals
  const results = await Order.aggregate([
    { $match: { status: 'completed' } },              // like WHERE status = 'completed'
    { $group: {                                         // like GROUP BY restaurantId
        _id: '$restaurantId',
        totalRevenue: { $sum: '$amount' },               // SUM(amount)
        orderCount: { $sum: 1 },                          // COUNT(*)
        avgOrderValue: { $avg: '$amount' },               // AVG(amount)
    }},
    { $sort: { totalRevenue: -1 } },                     // ORDER BY totalRevenue DESC
  ]);

  console.log(JSON.stringify(results, null, 2));
  // [{ _id: 'r1', totalRevenue: 1000, orderCount: 2, avgOrderValue: 500 },
  //  { _id: 'r2', totalRevenue: 300, orderCount: 1, avgOrderValue: 300 }]

  await mongoose.disconnect();
}

main();
```

## 💻 Code Example — Advanced

```javascript
// mongoose-aggregation-advanced.js — $lookup (join), $unwind, $project, pagination
const mongoose = require('mongoose');

const restaurantSchema = new mongoose.Schema({ name: String, cuisine: String });
const Restaurant = mongoose.model('Restaurant', restaurantSchema);

const orderSchema = new mongoose.Schema({
  restaurantId: mongoose.Schema.Types.ObjectId,
  items: [{ name: String, price: Number }],
  status: String,
});
const Order = mongoose.model('Order', orderSchema);

async function topCuisinesByRevenue(minOrders = 1) {
  return Order.aggregate([
    { $match: { status: 'completed' } },

    // $lookup = JOIN with the restaurants collection
    { $lookup: {
        from: 'restaurants',          // actual MongoDB collection name (lowercase, pluralized)
        localField: 'restaurantId',
        foreignField: '_id',
        as: 'restaurant',
    }},
    { $unwind: '$restaurant' },        // $lookup returns an ARRAY — unwind flattens it to a single object

    // $unwind the items array to compute per-item revenue
    { $unwind: '$items' },

    { $group: {
        _id: '$restaurant.cuisine',
        totalRevenue: { $sum: '$items.price' },
        orderCount: { $sum: 1 },
    }},

    { $match: { orderCount: { $gte: minOrders } } }, // filter AFTER grouping (like SQL's HAVING)

    // $project reshapes the output — rename fields, hide _id, add computed fields
    { $project: {
        _id: 0,
        cuisine: '$_id',
        totalRevenue: 1,
        orderCount: 1,
        avgPerOrder: { $round: [{ $divide: ['$totalRevenue', '$orderCount'] }, 2] },
    }},

    { $sort: { totalRevenue: -1 } },
    { $limit: 10 },
  ]);
}

// Pagination WITHIN an aggregation pipeline using $facet (parallel sub-pipelines)
async function paginatedOrders(page = 1, pageSize = 20) {
  const result = await Order.aggregate([
    { $match: { status: 'completed' } },
    { $facet: {
        data: [
          { $sort: { _id: -1 } },
          { $skip: (page - 1) * pageSize },
          { $limit: pageSize },
        ],
        totalCount: [{ $count: 'count' }], // runs the count in the SAME query, no separate round trip
    }},
  ]);
  return {
    data: result[0].data,
    total: result[0].totalCount[0]?.count || 0,
  };
}

async function run() {
  await mongoose.connect(process.env.MONGO_URI);
  try {
    const report = await topCuisinesByRevenue(1);
    console.log('Cuisine revenue report:', report);
  } catch (err) {
    console.error('Aggregation failed:', err.message);
  } finally {
    await mongoose.disconnect();
  }
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express analytics endpoint using an aggregation pipeline
const express = require('express');
const app = express();

app.get('/api/analytics/top-cuisines', async (req, res) => {
  try {
    const minOrders = Number(req.query.minOrders) || 1;
    const report = await topCuisinesByRevenue(minOrders);
    res.json(report);
  } catch (err) {
    res.status(500).json({ error: 'Analytics query failed' });
  }
});

app.get('/api/orders', async (req, res) => {
  const page = Number(req.query.page) || 1;
  const result = await paginatedOrders(page, 20);
  res.json(result); // { data: [...], total: N }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting `$match` late in the pipeline instead of early
```javascript
// Wrong — processes ALL documents through $lookup/$unwind before filtering, wasteful
[{ $lookup: {...} }, { $unwind: '$items' }, { $match: { status: 'completed' } }]

// Right — filter FIRST to reduce the dataset before expensive stages
[{ $match: { status: 'completed' } }, { $lookup: {...} }, { $unwind: '$items' }]
```

❌ Mistake 2: Forgetting `$lookup` returns an ARRAY, not a single object
✅ Correct: `$lookup` always produces an array field (even for a 1-to-1 relation) — you must `$unwind` it (or access `restaurant[0]`) to work with it as a single object; forgetting this leads to confusing `undefined` field accesses.

---

## 🧠 Tricky Interview Question

```javascript
const result = await Order.aggregate([
  { $group: { _id: '$restaurantId', total: { $sum: '$amount' } } },
  { $match: { total: { $gt: 1000 } } },
]);
```
Why can't this `$match` be replaced with a `WHERE`-style filter BEFORE `$group`?

Answer: Because the condition (`total > 1000`) depends on the AGGREGATED value, which doesn't exist until AFTER `$group` runs — this is exactly analogous to SQL's `HAVING` clause versus `WHERE`. `WHERE`/early `$match` filters raw documents BEFORE grouping; `HAVING`/post-group `$match` filters the GROUPED results. Trying to filter by `total` before `$group` would fail because no document has a `total` field yet — it's computed by the grouping stage itself.

---

## ⚫ Interview Questions + Answers

Q1: What is the purpose of `$match`, and why should it usually appear early in the pipeline?
A1: `$match` filters documents based on conditions, similar to SQL's `WHERE`. Placing it EARLY reduces the number of documents flowing into subsequent (often more expensive) stages like `$lookup`, `$unwind`, or `$group` — improving performance significantly, and it can also use indexes if it's the FIRST stage in the pipeline (MongoDB can optimize an early `$match` with existing indexes, unlike later stages).

Q2: How does `$lookup` differ from a SQL JOIN?
A2: `$lookup` performs a left-outer-join-like operation, matching documents from another collection based on a field equality, and embeds the matched documents as an ARRAY field in the output. Unlike SQL JOINs (which can be inner, left, right, full), `$lookup`'s default behavior is closer to a LEFT JOIN (keeps documents even with no match, giving an empty array), and more complex join conditions require an additional `pipeline` option within `$lookup` (correlated sub-pipeline) rather than simple ON-clause syntax.

Q3: What does `$unwind` do, and why is it often needed after `$lookup`?
A3: `$unwind` deconstructs an ARRAY field, producing one output document per array element (duplicating all other fields). It's often needed after `$lookup` because `$lookup` always outputs an array (even for 1-to-1 matches) — `$unwind` flattens that array into a single embedded object per document, making subsequent stages (like accessing `restaurant.cuisine`) straightforward.

Q4: What's the difference between `$match` before `$group` versus after `$group`?
A4: `$match` BEFORE `$group` filters the RAW input documents (like SQL `WHERE`) — reduces data entering the grouping stage. `$match` AFTER `$group` filters the GROUPED/aggregated results (like SQL `HAVING`) — e.g., "only show groups with total > 1000," a condition that only makes sense once the aggregate value exists.

Q5: How would you implement pagination with a total count in a single aggregation query?
A5: Use `$facet` — it runs MULTIPLE independent sub-pipelines in parallel over the SAME input documents in one query. E.g., one sub-pipeline does `$sort` + `$skip` + `$limit` for the actual page of data, and another does `$count` for the total matching document count — both returned together in a single aggregate call, avoiding a separate `countDocuments()` round trip.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need grouped statistics, joins across collections, or heavily reshaped output
- Building analytics dashboards, reports, or complex search/filter features
- You want to push computation to the database instead of pulling raw data into app memory

❌ Avoid when:
- A simple `find()` with filters/sort/limit already answers the question — don't reach for aggregation unnecessarily, it's more complex to write and debug
- The pipeline becomes so complex it's hard to maintain — consider breaking the problem into simpler queries or using a pre-computed/materialized collection updated on a schedule

---

## 📊 Visual Diagram
```
AGGREGATION PIPELINE FLOW
──────────────────────────────────────────────
  Order.aggregate([
    { $match: { status: 'completed' } },   ◄── filter early (like WHERE)
          │
          ▼
    { $lookup: { from: 'restaurants', ... } },  ◄── join (produces array field)
          │
          ▼
    { $unwind: '$restaurant' },             ◄── flatten array to single object
          │
          ▼
    { $group: { _id: '$restaurant.cuisine', totalRevenue: { $sum: '$amount' } } },  ◄── group + aggregate
          │
          ▼
    { $match: { totalRevenue: { $gt: 1000 } } },  ◄── filter grouped results (like HAVING)
          │
          ▼
    { $sort: { totalRevenue: -1 } }, { $limit: 10 }   ◄── order + limit final output
  ])
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| $match | Filters documents | Documents filter करना |
| $group | Groups + aggregates | Group + aggregate करना |
| $lookup | Join with another collection | दूसरी collection से join |
| $unwind | Flattens an array field | Array field को flatten करना |
| $project | Reshapes output fields | Output fields reshape करना |
| $facet | Parallel sub-pipelines | Parallel sub-pipelines |
| pipeline stage | One step in aggregation | Aggregation का एक step |

---

## ⚡ 3-Line Summary
English:
1. The aggregation pipeline chains stages (`$match`, `$group`, `$lookup`, `$unwind`, `$project`) to compute grouped statistics and joins inside the database.
2. Place `$match` early for performance (filters raw data before expensive stages); use `$match` after `$group` for HAVING-like conditions on aggregated values.
3. `$facet` runs parallel sub-pipelines (e.g., paginated data + total count) in a single aggregate call.

Hindi:
1. Aggregation pipeline stages (`$match`, `$group`, `$lookup`, `$unwind`, `$project`) को chain करता है grouped statistics और joins database के अंदर compute करने के लिए।
2. Performance के लिए `$match` early रखो; aggregated values पर HAVING जैसी conditions के लिए `$group` के बाद `$match`।
3. `$facet` एक ही aggregate call में parallel sub-pipelines चलाता है (जैसे paginated data + total count)।

---

## ➡️ Next Topic
**166. Redis with Node.js** — Connecting to Redis for caching, sessions, and pub/sub using the `redis`/`ioredis` packages.
