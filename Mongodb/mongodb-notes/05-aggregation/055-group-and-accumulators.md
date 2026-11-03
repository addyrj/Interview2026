# 55. $group and Accumulators ($sum, $avg, $push)
# हिंदी में: $group और Accumulators

---

## 🔵 Simple Definition (English)
**`$group`** collapses many documents into one document per distinct `_id` key (like SQL `GROUP BY`). For each group you compute values with **accumulators**: `$sum`, `$avg`, `$min`, `$max`, `$first`, `$last`, `$push` (collect all values in an array), `$addToSet` (unique values only).

## 🔵 सरल परिभाषा (Hindi)
**`$group`** कई documents को एक `_id` key के हिसाब से एक-एक document में समेट देता है (SQL के `GROUP BY` जैसा)। हर group के लिए values **accumulators** से निकलती हैं: `$sum`, `$avg`, `$min`, `$max`, `$first`, `$last`, `$push` (सारी values array में), `$addToSet` (सिर्फ unique values)।

---

## 🔴 Problem it Solves
Reports need numbers such as "revenue per customer" or "orders per city". Fetching all documents into Node.js and looping is slow and wastes network. `$group` does the math inside the database, near the data, and returns only the small summary.

## 🔴 यह क्यों बना? (Hindi)
Reports में "customer-wise revenue" या "city-wise orders" जैसे numbers चाहिए। सारे documents Node.js में लाकर loop करना slow है और network बर्बाद करता है। `$group` गणित database के अंदर करता है और सिर्फ छोटा summary लौटाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `_id` defines the group key: `"$customer"`, a compound object `{ city: "$city", status: "$status" }`, or `null` for one big group.
Step 2 → Every other field in `$group` must be an accumulator expression.
Step 3 → MongoDB scans incoming documents and updates each group's running accumulators.
Step 4 → `$sum: 1` counts documents; `$sum: "$amount"` adds values.
Step 5 → `$first`/`$last` depend on order, so `$sort` before `$group` if you need a meaningful result.
Step 6 → Output order of groups is NOT guaranteed; add `$sort` after.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `_id` group key तय करता है: `"$customer"`, compound object `{ city: "$city", status: "$status" }`, या पूरे data का एक group बनाने के लिए `null`।
Step 2 → `$group` के बाकी हर field में accumulator होना ज़रूरी है।
Step 3 → MongoDB incoming documents पढ़कर हर group के accumulators update करता है।
Step 4 → `$sum: 1` documents गिनता है; `$sum: "$amount"` values जोड़ता है।
Step 5 → `$first`/`$last` order पर निर्भर हैं, इसलिए सही नतीजे के लिए `$group` से पहले `$sort` करो।
Step 6 → Groups का output order guaranteed नहीं है; बाद में `$sort` लगाओ।

---

## 🟡 Real World Example
**Razorpay's settlement dashboard** groups payments by merchant: total captured amount, average ticket size, number of payments, and the list of distinct payment methods (UPI, card, netbanking) via `$addToSet`. One pipeline returns one row per merchant instead of millions of payment documents.

## 🟡 Real Example Hindi mein
**Razorpay का settlement dashboard** payments को merchant के हिसाब से group करता है: कुल captured amount, average ticket size, payments की गिनती, और `$addToSet` से distinct payment methods (UPI, card, netbanking)। लाखों payment documents की जगह हर merchant की एक row आती है।

---

## 💻 Code Example — Basic

```javascript
// mongosh, tested on MongoDB 8.0.4, database shop, collection orders
db.orders.aggregate([
  { $match: { status: "delivered" } },            // only delivered orders
  { $group: {
      _id: "$customer",                           // one group per customer
      total: { $sum: "$amount" },                 // sum of amounts
      avg: { $avg: "$amount" },                   // average amount
      orders: { $sum: 1 },                        // count of documents in group
      cities: { $addToSet: "$city" },             // unique cities
      all: { $push: "$amount" }                   // every amount, in an array
  } },
  { $sort: { _id: 1 } }                           // stable order for display
])
// Output (real):
// { _id: 'Aarav', total: 450, avg: 450, orders: 1, cities: ['Delhi'],  all: [450] }
// { _id: 'Diya',  total: 540, avg: 270, orders: 2, cities: ['Mumbai'], all: [230, 310] }
// { _id: 'Kabir', total: 890, avg: 890, orders: 1, cities: ['Mumbai'], all: [890] }
```

## 💻 Code Example — Advanced

```javascript
// _id: null = one group for the whole input (grand totals)
db.orders.aggregate([
  { $group: {
      _id: null,                                  // single group
      revenue: { $sum: "$amount" },
      max: { $max: "$amount" },
      min: { $min: "$amount" },
      first: { $first: "$customer" },             // depends on input order
      last: { $last: "$customer" }
  } }
])
// Output (real): { _id: null, revenue: 2075, max: 890, min: 75, first: 'Aarav', last: 'Meera' }

// Compound key: group by two fields
db.orders.aggregate([
  { $group: { _id: { city: "$city", status: "$status" }, n: { $sum: 1 } } },
  { $sort: { "_id.city": 1, "_id.status": 1 } }
])
// Output (real):
// { _id: { city: 'Delhi',  status: 'cancelled' }, n: 1 }
// { _id: { city: 'Delhi',  status: 'delivered' }, n: 1 }
// { _id: { city: 'Mumbai', status: 'delivered' }, n: 3 }
// { _id: { city: 'Pune',   status: 'pending'   }, n: 1 }
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// GET /api/reports/customers — revenue per customer (tested with Mongoose against mongod 8.0.4)
app.get("/api/reports/customers", async (req, res) => {
  const rows = await Order.aggregate([
    { $group: { _id: "$customer", total: { $sum: "$amount" }, avg: { $avg: "$amount" } } },
    { $sort: { total: -1 } }                       // highest spender first
  ]);
  res.json(rows);
});
// Real result:
// [{"_id":"Kabir","total":890,"avg":890},{"_id":"Aarav","total":570,"avg":285},
//  {"_id":"Diya","total":540,"avg":270},{"_id":"Meera","total":75,"avg":75}]
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting the `$` on the group key
```javascript
{ $group: { _id: "customer" } }   // Wrong — ONE group with the literal string "customer"
{ $group: { _id: "$customer" } }  // Right — one group per customer value
```

❌ Mistake 2: Using `$push` on huge groups
✅ A document is capped at 16 MB. `$push` of millions of values in one group will fail. Use `$sum`/`$count`, `$firstN`, or `$topN` instead of pushing everything.

❌ Mistake 3: Relying on group output order or `$first` without `$sort`
✅ Add `$sort` before (for `$first`/`$last`) and after (for display).

---

## 🧠 Tricky Interview Question
Q: Order 6 (Meera) is pending, so she is not delivered. What does `{ $match: {status:"delivered"} }, { $group: {_id:"$customer", ...} }` return for Meera?
Answer: Nothing. `$group` only sees documents that survive `$match`, so Meera has no group. If you want a row of 0 for every customer, group first and use a conditional sum: `{ $sum: { $cond: [{ $eq: ["$status","delivered"] }, "$amount", 0] } }`. Real result: Meera gets `delivered: 0`.

---

## ⚫ Interview Questions + Answers

Q1: What is required in `$group`?
A1: The `_id` field (the key). Everything else is optional and must be an accumulator.

Q2: `$push` vs `$addToSet`?
A2: `$push` keeps all values including duplicates, in input order. `$addToSet` keeps unique values and gives no order guarantee.

Q3: How do you count documents per group?
A3: `{ $sum: 1 }`. (`$count` accumulator also exists in 5.0+ as `{ $count: {} }`.)

Q4: Can `$group` use an index?
A4: Only in special cases (`$first`/`$last` after a `$sort` that matches an index, or `$group` on a distinct pattern). Normally it scans, so `$match` first.

Q5: What if `$group` exceeds 100 MB of RAM?
A5: Stages are limited to 100 MB by default; use `{ allowDiskUse: true }` (on by default for the server in recent versions via `allowDiskUseByDefault`) to spill to disk.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need totals, averages, counts, top-N per category
- You want unique values per group

❌ Avoid when:
- You only need one number over a simple filter (`countDocuments` is simpler)
- You would `$push` unbounded arrays

---

## 📊 Visual Diagram
```
 orders: Aarav 450 | Diya 230 | Diya 310 | Kabir 890
              │
              ▼   $group { _id: "$customer", total: {$sum:"$amount"} }
   ┌──────────┬──────────────┬──────────────┐
   │ Aarav    │ Diya         │ Kabir        │
   │ 450      │ 230+310=540  │ 890          │
   └──────────┴──────────────┴──────────────┘
         one output document per group
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Group key (`_id`) | Value that defines each group | Group तय करने वाली value |
| Accumulator | Per-group running calculation | Group-wise गणना |
| `$sum` / `$avg` | Total / mean | जोड़ / औसत |
| `$push` | Collect all values in array | सारी values array में |
| `$addToSet` | Collect unique values | सिर्फ unique values |
| `_id: null` | One group for everything | पूरे data का एक group |

---

## ⚡ 3-Line Summary
English:
1. `$group` = SQL `GROUP BY`; `_id` is the key, other fields are accumulators.
2. Use `$sum: 1` to count, `$push`/`$addToSet` to collect, `_id: null` for grand totals.
3. `$match` first, `$sort` after; avoid unbounded `$push`.

Hindi:
1. `$group` = SQL `GROUP BY`; `_id` key है, बाकी fields accumulators हैं।
2. गिनती के लिए `$sum: 1`, collect करने के लिए `$push`/`$addToSet`, grand total के लिए `_id: null`।
3. पहले `$match`, बाद में `$sort`; unbounded `$push` से बचो।

---

## ➡️ Next Topic
**56. $sort, $limit, $skip in Pipelines** — ordering and paginating results.
