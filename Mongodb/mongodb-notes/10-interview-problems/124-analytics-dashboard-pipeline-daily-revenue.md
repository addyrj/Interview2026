# 124. Analytics Dashboard Pipeline (daily revenue)
# हिंदी में: Analytics Dashboard Pipeline (रोज़ का revenue)

---

## 🔵 Simple Definition (English)
An **analytics dashboard pipeline** is an aggregation pipeline that turns raw order documents into dashboard-ready numbers: revenue per day, number of orders, average order value (AOV) and unique customers. It uses `$match` -> `$group` -> `$project` -> `$sort`, and optionally `$facet`, `$setWindowFields` and `$merge`.

## 🔵 सरल परिभाषा (Hindi)
**Analytics dashboard pipeline** एक aggregation pipeline है जो raw order documents को dashboard के काम के numbers में बदलती है: रोज़ का revenue, orders की गिनती, average order value (AOV) और unique customers। इसमें `$match` -> `$group` -> `$project` -> `$sort` इस्तेमाल होते हैं, और ज़रूरत पर `$facet`, `$setWindowFields` और `$merge` भी।

---

## 🔴 Problem it Solves
A founder opens the Flipkart-style admin dashboard and wants "daily revenue for the last 30 days". Pulling every order into Node.js and summing in JavaScript moves millions of documents over the network and burns app memory. The pipeline runs **inside the database**, close to the data and the indexes, and returns only a handful of rows (one per day). It also fixes the classic bug where "day" boundaries are in UTC while the business runs in IST.

## 🔴 यह क्यों बना? (Hindi)
Founder admin dashboard खोलकर "पिछले 30 दिन का daily revenue" देखना चाहता है। सारे orders Node.js में खींचकर JavaScript में जोड़ना network और memory दोनों बर्बाद करता है। Pipeline **database के अंदर** चलती है, data और indexes के पास, और सिर्फ चंद rows (हर दिन की एक) लौटाती है। यह उस आम bug को भी ठीक करती है जहाँ "दिन" UTC में कटता है लेकिन business IST में चलता है।

---

## 🟢 How it Works — Step by Step

Step 1 -> `$match` FIRST: filter `status: "delivered"` and a date range. This is the only stage that can use an index (`{status:1, placedAt:1}`), so it must come first.
Step 2 -> `$group` by a day key built with `$dateToString` and `timezone: "Asia/Kolkata"`, accumulating `$sum` (revenue), `$sum: 1` (orders) and `$addToSet` (unique users).
Step 3 -> `$project` shapes the output: rename `_id` to `day`, compute AOV with `$divide` + `$round`, and `$size` of the user set.
Step 4 -> `$sort` by day ascending so the chart's X axis is in order (`$group` output order is NOT guaranteed).
Step 5 -> For widgets that need several results at once, use `$facet`; for running totals, `$setWindowFields`; for caching heavy results, `$merge` into a summary collection refreshed by a cron job.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 -> `$match` सबसे पहले: `status: "delivered"` और date range filter करो। सिर्फ यही stage index (`{status:1, placedAt:1}`) इस्तेमाल कर सकता है, इसलिए पहले आना चाहिए।
Step 2 -> `$group` में `$dateToString` से day key बनाओ, `timezone: "Asia/Kolkata"` के साथ, और `$sum` (revenue), `$sum: 1` (orders), `$addToSet` (unique users) accumulate करो।
Step 3 -> `$project` से output सजाओ: `_id` को `day` बनाओ, `$divide` + `$round` से AOV, और user set का `$size`।
Step 4 -> `$sort` day ascending, ताकि chart का X axis क्रम में हो (`$group` का output order guaranteed नहीं)।
Step 5 -> एक साथ कई results के लिए `$facet`; running total के लिए `$setWindowFields`; भारी results cache करने के लिए `$merge` से summary collection में डालो, cron से refresh करो।

---

## 🟡 Real World Example
**Swiggy's ops dashboard** shows "yesterday's revenue by city" and "daily revenue trend". An order placed at 00:30 IST on 3 Jan is stored as 19:00 UTC on 2 Jan. If you group by UTC date, that order lands on the wrong day and the finance team's numbers do not match the bank. Grouping with `timezone: "Asia/Kolkata"` fixes it. Heavy history (a year of data) is pre-aggregated nightly into a `daily_revenue` collection so the dashboard reads 365 tiny documents instead of scanning 50 million orders.

## 🟡 Real Example Hindi mein
**Swiggy के ops dashboard** पर "कल का city-wise revenue" और "daily revenue trend" दिखता है। 3 Jan की रात 00:30 IST पर बना order DB में 2 Jan 19:00 UTC के रूप में रहता है। UTC date से group करोगे तो order गलत दिन में जाएगा और finance team के numbers bank से नहीं मिलेंगे। `timezone: "Asia/Kolkata"` से यह ठीक होता है। पुराना भारी data (साल भर) रात को `daily_revenue` collection में pre-aggregate हो जाता है, ताकि dashboard 5 करोड़ orders scan करने की जगह 365 छोटे documents पढ़े।

---

## 💻 Code Example — Basic

Sample data (6 orders; verified on MongoDB 8.0.4, mongosh):

```javascript
// seed.js — run with: mongosh --port 27141 --file seed.js
const d = db.getSiblingDB("shop");          // pick database "shop"
d.dropDatabase();                           // start clean for repeatable demo
d.orders.insertMany([                       // insert 6 sample orders
  { _id: 1, status: "delivered", city: "Delhi", amount: 500, placedAt: ISODate("2026-01-01T02:00:00Z"), userId: "u1" }, // 07:30 IST, 1 Jan
  { _id: 2, status: "delivered", city: "Delhi", amount: 300, placedAt: ISODate("2026-01-01T10:00:00Z"), userId: "u2" }, // 15:30 IST, 1 Jan
  { _id: 3, status: "cancelled", city: "Pune",  amount: 900, placedAt: ISODate("2026-01-01T11:00:00Z"), userId: "u3" }, // cancelled -> excluded
  { _id: 4, status: "delivered", city: "Pune",  amount: 700, placedAt: ISODate("2026-01-02T05:00:00Z"), userId: "u1" }, // 10:30 IST, 2 Jan
  { _id: 5, status: "delivered", city: "Delhi", amount: 200, placedAt: ISODate("2026-01-02T19:00:00Z"), userId: "u1" }, // 00:30 IST, 3 Jan (!)
  { _id: 6, status: "delivered", city: "Delhi", amount: 400, placedAt: ISODate("2026-01-03T08:00:00Z"), userId: "u4" }  // 13:30 IST, 3 Jan
]);
d.orders.createIndex({ status: 1, placedAt: 1 }); // equality field first, range field second (ESR rule)
```

Daily revenue:

```javascript
db.orders.aggregate([
  { $match: {                                            // stage 1: filter early, uses the index
      status: "delivered",                               // only completed orders count as revenue
      placedAt: { $gte: ISODate("2026-01-01T00:00:00Z"), // start of range (inclusive)
                  $lt:  ISODate("2026-01-04T00:00:00Z") } // end of range (exclusive) - avoids midnight bugs
  } },
  { $group: {                                            // stage 2: one output doc per day
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$placedAt", timezone: "Asia/Kolkata" } }, // IST day key
      revenue: { $sum: "$amount" },                      // total money
      orders:  { $sum: 1 },                              // count of orders
      users:   { $addToSet: "$userId" }                  // distinct customers (array, deduplicated)
  } },
  { $project: {                                          // stage 3: shape output for the API
      _id: 0,                                            // hide the raw _id
      day: "$_id", revenue: 1, orders: 1,                // rename _id -> day, keep two fields
      aov: { $round: [{ $divide: ["$revenue", "$orders"] }, 2] }, // average order value, 2 decimals
      uniqueUsers: { $size: "$users" }                   // count the distinct set
  } },
  { $sort: { day: 1 } }                                  // stage 4: chronological order
]);
```

Output (real, verified):

```javascript
// [
//   { revenue: 800, orders: 2, day: '2026-01-01', aov: 400, uniqueUsers: 2 },
//   { revenue: 700, orders: 1, day: '2026-01-02', aov: 700, uniqueUsers: 1 },
//   { revenue: 600, orders: 2, day: '2026-01-03', aov: 300, uniqueUsers: 2 }
// ]
// Note: order 5 (19:00 UTC on 2 Jan) counted on 3 Jan because of the IST timezone.
// Cancelled order 3 (Rs 900) is excluded. Without the timezone option 2 Jan would show 900.
```

## 💻 Code Example — Advanced

```javascript
// 1) $facet: several dashboard widgets in ONE round trip over the same matched set
db.orders.aggregate([
  { $match: { status: "delivered" } },                   // shared filter, runs once
  { $facet: {                                            // each key is an independent sub-pipeline
      byCity: [                                          // widget 1: revenue per city
        { $group: { _id: "$city", revenue: { $sum: "$amount" } } },
        { $sort: { revenue: -1 } }                       // biggest city first
      ],
      total: [                                           // widget 2: grand total
        { $group: { _id: null, revenue: { $sum: "$amount" } } }
      ]
  } }
]);
// [ { byCity: [ { _id: 'Delhi', revenue: 1400 }, { _id: 'Pune', revenue: 700 } ],
//     total:  [ { _id: null, revenue: 2100 } ] } ]
// Caveat: $facet output is ONE document (16 MB limit) and sub-pipelines cannot use indexes.

// 2) Running (cumulative) revenue with $setWindowFields (MongoDB 5.0+)
db.orders.aggregate([
  { $match: { status: "delivered" } },
  { $group: { _id: { $dateToString: { format: "%Y-%m-%d", date: "$placedAt", timezone: "Asia/Kolkata" } },
              revenue: { $sum: "$amount" } } },          // daily revenue first
  { $sort: { _id: 1 } },
  { $setWindowFields: {
      sortBy: { _id: 1 },                                // window ordered by day
      output: { cumulative: { $sum: "$revenue",
                window: { documents: ["unbounded", "current"] } } } // from first row up to this row
  } }
]);
// [ { _id: '2026-01-01', revenue: 800, cumulative: 800 },
//   { _id: '2026-01-02', revenue: 700, cumulative: 1500 },
//   { _id: '2026-01-03', revenue: 600, cumulative: 2100 } ]

// 3) $merge: materialize the result into a summary collection (incremental refresh)
db.orders.aggregate([
  { $match: { status: "delivered" } },
  { $group: { _id: { $dateToString: { format: "%Y-%m-%d", date: "$placedAt", timezone: "Asia/Kolkata" } },
              revenue: { $sum: "$amount" } } },
  { $merge: { into: "daily_revenue", whenMatched: "replace" } } // upsert by _id; re-running is safe (idempotent)
]);
db.daily_revenue.find().sort({ _id: 1 });
// { _id: '2026-01-01', revenue: 800 }, { _id: '2026-01-02', revenue: 700 }, { _id: '2026-01-03', revenue: 600 }
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// routes/analytics.js — Mongoose model "Order" assumed with fields: status, city, amount, placedAt, userId
const express = require('express');
const Order = require('../models/Order');
const router = express.Router();

router.get('/api/analytics/daily-revenue', async (req, res) => {
  const from = new Date(req.query.from);                 // e.g. 2026-01-01T00:00:00Z from the query string
  const to = new Date(req.query.to);                     // exclusive upper bound
  if (isNaN(from) || isNaN(to)) return res.status(400).json({ error: 'Invalid dates' }); // validate input

  const rows = await Order.aggregate([                   // NOTE: Mongoose does NOT cast types inside aggregate()
    { $match: { status: 'delivered', placedAt: { $gte: from, $lt: to } } }, // so we pass real Date objects
    { $group: {
        _id: { $dateToString: { format: '%Y-%m-%d', date: '$placedAt', timezone: 'Asia/Kolkata' } },
        revenue: { $sum: '$amount' },
        orders: { $sum: 1 },
    } },
    { $sort: { _id: 1 } },
  ]);                                                    // returns plain objects, not Mongoose documents
  res.json(rows.map(r => ({ day: r._id, revenue: r.revenue, orders: r.orders })));
});

module.exports = router;
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Grouping by UTC date for an Indian business
```javascript
// Wrong — default timezone is UTC; late-night IST orders land on the previous/next day
{ $group: { _id: { $dateToString: { format: "%Y-%m-%d", date: "$placedAt" } }, revenue: { $sum: "$amount" } } }

// Right — pass the business timezone
{ $group: { _id: { $dateToString: { format: "%Y-%m-%d", date: "$placedAt", timezone: "Asia/Kolkata" } }, revenue: { $sum: "$amount" } } }
```

❌ Mistake 2: Putting `$match` after `$group` (or `$sort` before `$match`)
```javascript
// Wrong — groups the whole collection, then filters; no index use
[{ $group: {...} }, { $match: { status: "delivered" } }]
// Right — filter first so the index narrows the input
[{ $match: { status: "delivered", placedAt: { $gte: from, $lt: to } } }, { $group: {...} }]
```

❌ Mistake 3: Forgetting `$sort` after `$group`, and using `$lte` with midnight dates
✅ Correct: `$group` output order is arbitrary — always `$sort`. Use `$gte` start and `$lt` next-day-start for ranges, not `$lte` end-of-day, so no millisecond is lost or double counted.

---

## 🧠 Tricky Interview Question

"The dashboard shows Rs 900 on 2 Jan, but finance says Rs 700. Orders are correct. What is wrong?"

Answer: The pipeline groups in UTC. Order 5 (Rs 200) was placed at 00:30 IST on 3 Jan, which is 19:00 UTC on 2 Jan, so 700 + 200 = 900 appears on 2 Jan. Add `timezone: "Asia/Kolkata"` to `$dateToString` (or `$dateTrunc` with `timezone`) and 2 Jan becomes Rs 700, 3 Jan becomes Rs 600. Bonus: store timestamps in UTC always, and convert only at query time.

---

## ⚫ Interview Questions + Answers

Q1: Why must `$match` be the first stage?
A1: Only a leading `$match` (and `$sort`) can use indexes. Early filtering also reduces documents flowing through later stages. The optimizer can sometimes move `$match` earlier automatically, but do not rely on it.

Q2: `$addToSet` vs `$sum: 1` for unique users?
A2: `$addToSet` builds a deduplicated array in memory per group, fine for thousands of users per day, risky for millions (16 MB document limit for a group value is enforced). For huge cardinality, group by `{day, userId}` first and then group again by day with `$sum: 1`.

Q3: How do you make a dashboard fast when data grows to 100 million orders?
A3: Pre-aggregate: a scheduled job runs the pipeline for the last day and `$merge`s into `daily_revenue`. The dashboard reads that small collection. Alternatively use time-series collections or on-demand materialized views.

Q4: When would you use `$facet`?
A4: To compute several aggregations over the same input in a single query (revenue by city, by category, total). Limitation: sub-pipelines cannot use indexes and the combined output must fit in 16 MB.

Q5: How do you compute a running total or a 7-day moving average?
A5: `$setWindowFields` (5.0+) with `window: { documents: [-6, 0] }` for a 7-row moving average, or `["unbounded","current"]` for cumulative sums.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need grouped numbers (per day/city/category) from large raw data
- You want the DB to do the heavy lifting and return small results
- You can pre-compute summaries with `$merge` for fast dashboards

❌ Avoid when:
- Real-time, sub-second dashboards over billions of rows (use a dedicated OLAP store or pre-aggregated counters)
- The query is a simple lookup by key (use `find`)

---

## 📊 Visual Diagram
```
 orders (raw, millions)
        │
   $match  status=delivered, date range     <- uses index {status, placedAt}
        │
   $group  key = IST day                    <- revenue, orders, users
        │
  $project aov, uniqueUsers, rename _id
        │
   $sort   day asc
        │
        ├──> API / chart  (few rows)
        └──> $merge ──> daily_revenue (cache) ──> dashboard reads this
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$group` | Groups docs by a key and accumulates | Key से group करके accumulate |
| `$dateToString` | Formats a date, supports timezone | Date को string बनाता है, timezone के साथ |
| AOV | Average order value = revenue / orders | औसत order value |
| `$facet` | Multiple sub-pipelines in one pass | एक बार में कई sub-pipelines |
| `$setWindowFields` | Window functions (running totals) | Window functions (चलता total) |
| `$merge` | Writes pipeline output to a collection | Output को collection में लिखता है |

---

## ⚡ 3-Line Summary
English:
1. Daily revenue = `$match` (indexed filter) -> `$group` by `$dateToString` day key -> `$project` -> `$sort`.
2. Always pass the business `timezone`, otherwise late-night orders land on the wrong day.
3. For big data, pre-aggregate with `$merge` into a summary collection and let the dashboard read that.

Hindi:
1. Daily revenue = `$match` (index वाला filter) -> `$dateToString` day key से `$group` -> `$project` -> `$sort`।
2. हमेशा business का `timezone` दो, वरना रात के orders गलत दिन में जाएँगे।
3. बड़े data के लिए `$merge` से summary collection में pre-aggregate करो और dashboard उसी से पढ़े।

---

## ➡️ Next Topic
**125. Slow Query Debugging Scenario** — Using `explain`, indexes and the profiler to fix a slow query.
