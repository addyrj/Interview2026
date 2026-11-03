# 49. Covered Queries
# हिंदी में: Covered Queries (सिर्फ index से जवाब)

---

## 🔵 Simple Definition (English)
A **covered query** is a query that MongoDB answers using **only the index** — it never touches the actual documents on disk. This happens when (1) every field in the filter is in the index, (2) every field returned (the projection) is in the same index, and (3) `_id` is either in the index or explicitly excluded (`_id: 0`). In `explain()` you see `PROJECTION_COVERED` + `IXSCAN` and `totalDocsExamined: 0`.

## 🔵 सरल परिभाषा (Hindi)
**Covered query** वो query है जिसका जवाब MongoDB **सिर्फ index से** दे देता है — असली documents को disk से पढ़ता ही नहीं। ये तब होता है जब (1) filter के सारे fields index में हों, (2) जो fields return करने हैं (projection) वो भी उसी index में हों, और (3) `_id` या तो index में हो या `_id: 0` से हटा दिया गया हो। `explain()` में `PROJECTION_COVERED` + `IXSCAN` दिखता है और `totalDocsExamined: 0` आता है।

---

## 🔴 Problem it Solves
A normal indexed query does two jobs: walk the index to find matching entries, then **FETCH** each full document from the collection to build the result. The FETCH step is random I/O and can dominate latency when thousands of documents match, and it pollutes the WiredTiger cache with large documents you barely need. If you only need two small fields (like `city` and `amount`), reading entire documents with nested arrays is wasteful. A covered query skips FETCH completely, so it is faster, uses less memory/cache and less disk I/O.

## 🔴 यह क्यों बना? (Hindi)
Normal indexed query दो काम करती है: पहले index में matching entries ढूँढना, फिर हर पूरा document collection से **FETCH** करना। FETCH random I/O है और जब हज़ारों documents match हों तो यही सबसे ज़्यादा समय लेता है, साथ में WiredTiger cache में बड़े documents भर जाते हैं जिनकी ज़रूरत भी नहीं थी। अगर आपको सिर्फ दो छोटे fields (`city`, `amount`) चाहिए तो पूरा document (nested arrays समेत) पढ़ना फिज़ूल है। Covered query FETCH को पूरी तरह skip करती है — इसलिए तेज़, कम memory और कम disk I/O।

---

## 🟢 How it Works — Step by Step

Step 1 → You create a compound index that contains the filter fields AND the fields you want back: `{ city: 1, status: 1, amount: 1 }`.
Step 2 → You run `find(filter, projection)` where the projection asks only for indexed fields and sets `_id: 0`.
Step 3 → The planner sees that all data needed is already inside index keys, so the plan becomes `PROJECTION_COVERED → IXSCAN` (no `FETCH` stage).
Step 4 → MongoDB reads index keys sequentially, builds result documents from the key values, and returns them.
Step 5 → You verify with `explain("executionStats")`: `totalKeysExamined` > 0 and `totalDocsExamined` = 0.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Compound index बनाओ जिसमें filter के fields और return होने वाले fields दोनों हों: `{ city: 1, status: 1, amount: 1 }`।
Step 2 → `find(filter, projection)` चलाओ जहाँ projection सिर्फ indexed fields माँगे और `_id: 0` हो।
Step 3 → Planner देखता है कि ज़रूरी सारा data index keys में ही है, तो plan बनता है `PROJECTION_COVERED → IXSCAN` (कोई `FETCH` stage नहीं)।
Step 4 → MongoDB index keys पढ़ता है, key values से result documents बनाता है और लौटा देता है।
Step 5 → `explain("executionStats")` से check करो: `totalKeysExamined` > 0 और `totalDocsExamined` = 0।

---

## 🟡 Real World Example
**Swiggy's "orders in my city" dashboard** for ops managers only needs `city`, `status` and `amount` for thousands of orders, to draw a quick revenue chart. Each real order document carries items arrays, address, rider info, payment details — several KB each. By adding the index `{ city:1, status:1, amount:1 }` and projecting only those three fields (with `_id: 0`), the dashboard query reads tiny index entries from RAM instead of fetching 1666 fat documents — the dashboard loads in milliseconds even during dinner-time peak.

## 🟡 Real Example Hindi mein
**Swiggy के ops managers का "मेरे city के orders" dashboard** हज़ारों orders के सिर्फ `city`, `status` और `amount` माँगता है ताकि revenue chart बने। असली order document में items arrays, address, rider info, payment details होते हैं — कई KB के। `{ city:1, status:1, amount:1 }` index बनाकर और सिर्फ ये तीन fields (`_id: 0` के साथ) project करके dashboard query RAM में पड़े छोटे index entries पढ़ती है, 1666 भारी documents fetch नहीं करती — dinner-time peak में भी dashboard milliseconds में खुलता है।

---

## 💻 Code Example — Basic

Dataset: `shop.orders` with 5000 documents `{ orderId, userId, city, status, amount, items:[...], createdAt }` (tested on MongoDB 8.0.4; numbers below come from the real run).

```javascript
// mongosh
use shop // switch to the "shop" database

// 1) Compound index: filter fields first (city, status), then the extra returned field (amount)
db.orders.createIndex({ city: 1, status: 1, amount: 1 })
// Output: 'city_1_status_1_amount_1'

// 2) COVERED query: projection only has indexed fields AND _id is excluded
const e1 = db.orders.find(
  { city: "Delhi", status: "placed" },        // filter uses indexed fields
  { _id: 0, city: 1, status: 1, amount: 1 }   // projection = only indexed fields, _id removed
).explain("executionStats")

e1.queryPlanner.winningPlan.stage                // Output: 'PROJECTION_COVERED'
e1.queryPlanner.winningPlan.inputStage.stage     // Output: 'IXSCAN'
e1.executionStats.totalKeysExamined              // Output: 1666  (index entries read)
e1.executionStats.totalDocsExamined              // Output: 0     (NO document touched = covered!)
e1.executionStats.nReturned                      // Output: 1666

// 3) NOT covered: _id is returned by default and it is NOT in this index
const e2 = db.orders.find(
  { city: "Delhi", status: "placed" },
  { city: 1, amount: 1 }                          // _id included implicitly -> must FETCH
).explain("executionStats")

e2.queryPlanner.winningPlan.stage                // Output: 'PROJECTION_SIMPLE' (a FETCH happens below it)
e2.executionStats.totalDocsExamined              // Output: 1666 (every doc fetched)
```

## 💻 Code Example — Advanced

```javascript
// Advanced: design a covering index for a hot dashboard query, then prove it in Node.js
const { MongoClient } = require('mongodb'); // official driver

async function main() {
  const client = new MongoClient('mongodb://127.0.0.1:27017'); // connect string (local)
  await client.connect();                                      // open the pool
  const orders = client.db('shop').collection('orders');       // get the collection

  // Covering index: equality fields first, then the "output only" field
  await orders.createIndex({ city: 1, status: 1, amount: 1 });

  // Range on the last indexed field is still covered
  const cursor = orders.find(
    { city: 'Mumbai', status: 'delivered', amount: { $gte: 200 } }, // filter: all 3 fields indexed
    { projection: { _id: 0, amount: 1 } }                           // return only amount, drop _id
  );
  const rows = await cursor.toArray();                              // run the query
  console.log('rows:', rows.length);                                // number of matches

  // Prove coverage: docsExamined must be 0
  const plan = await orders
    .find({ city: 'Mumbai', status: 'delivered' }, { projection: { _id: 0, amount: 1 } })
    .explain('executionStats');
  console.log('docsExamined =', plan.executionStats.totalDocsExamined); // expect 0

  // Aggregation can be covered too when $match/$group only use indexed fields
  const agg = await orders.aggregate([
    { $match: { city: 'Mumbai', status: 'delivered' } },            // uses index prefix
    { $group: { _id: '$city', revenue: { $sum: '$amount' } } },     // needs only city+amount
  ]).toArray();
  console.log(agg); // [ { _id: 'Mumbai', revenue: 125100 } ]

  await client.close(); // always close
}
main().catch(console.error);
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');

const orderSchema = new mongoose.Schema({
  city: String, status: String, amount: Number, userId: Number,
}, { collection: 'orders' });
// Declare the covering index in the schema so it exists in every environment
orderSchema.index({ city: 1, status: 1, amount: 1 });
const Order = mongoose.model('Order', orderSchema);

const app = express();

app.get('/api/amounts', async (req, res) => {
  // .select('-_id city status amount') is the Mongoose way to write the projection
  // .lean() skips Mongoose hydration - ideal for read-only covered queries
  const rows = await Order.find({ city: req.query.city, status: 'placed' })
    .select('-_id city status amount')
    .lean();
  res.json({ count: rows.length });
});

mongoose.connect('mongodb://127.0.0.1:27017/shop').then(() => app.listen(3000));
```
Note: Mongoose does NOT add `_id: 0` for you — forgetting `-_id` silently breaks coverage.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to exclude `_id`
```javascript
// Wrong — _id is returned by default; it is not in the index, so MongoDB FETCHes documents
db.orders.find({ city: "Delhi" }, { city: 1, amount: 1 })

// Right — exclude _id (or put _id in the index)
db.orders.find({ city: "Delhi" }, { _id: 0, city: 1, amount: 1 })
```

❌ Mistake 2: Projecting a field that is not in the index
```javascript
// Wrong — "items" is not indexed, so the document must be fetched
db.orders.find({ city: "Delhi" }, { _id: 0, city: 1, items: 1 })

// Right — only return indexed fields, or add the field to the index
db.orders.find({ city: "Delhi" }, { _id: 0, city: 1, status: 1 })
```

❌ Mistake 3: Expecting coverage with multikey (array) indexes
✅ Correct: If any indexed field holds an array in any document, the index is **multikey** and cannot cover queries on that array field. Also, covered queries do not work on sharded `mongos` if the index does not include the shard key.

---

## 🧠 Tricky Interview Question

```javascript
db.orders.createIndex({ city: 1, amount: 1 })
db.orders.find({ city: "Delhi" }, { city: 1, amount: 1 }).explain("executionStats")
// Is this a covered query? What is totalDocsExamined?
```
Answer: **Not covered.** `_id` is included in the output by default and is not part of `{ city, amount }`, so MongoDB must FETCH every matching document (`totalDocsExamined` equals `nReturned`, 1666 in our data). The fix is a one-word change: add `_id: 0` to the projection. This is the #1 reason people "have the right index but still see docsExamined > 0".

---

## ⚫ Interview Questions + Answers

Q1: What is a covered query?
A1: A query where the filter and the projection both use only fields in a single index, so MongoDB returns the result straight from index keys and never loads documents. `explain` shows `totalDocsExamined: 0`.

Q2: What conditions must hold for a query to be covered?
A2: (1) All fields in the query are in the index; (2) all fields returned are in the index; (3) `_id` is in the index or excluded; (4) no queried/returned field is an array in any document (not multikey). Practically: equality + projection of indexed fields with `_id: 0`.

Q3: How do you confirm a query is covered?
A3: `explain("executionStats")`: the winning plan has no `FETCH`, the top stage is `PROJECTION_COVERED`, and `totalDocsExamined` is 0 while `totalKeysExamined` > 0.

Q4: What is the cost of a covering index?
A4: Wider index = more RAM, slower writes (every insert/update on those fields updates the index), more disk. You should cover only hot, high-frequency queries, not every query.

Q5: Does field order in the covering index matter?
A5: Yes. Filter fields must form a usable prefix (equality first, then sort, then range — the ESR rule). Fields only needed in the output can go at the end, as `amount` did in `{ city, status, amount }`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A hot read endpoint returns only 1-3 small fields (leaderboards, dashboards, autocomplete lists)
- Documents are large but the response needs a few fields
- You do counts/existence checks (`countDocuments` on indexed filter can use index only)

❌ Avoid when:
- The query needs many fields — the index would become as big as the data
- The collection is write-heavy; wide indexes slow every write
- Fields are arrays (multikey) — coverage is not possible

---

## 📊 Visual Diagram
```
NORMAL INDEXED QUERY            COVERED QUERY
────────────────────            ─────────────
 find(filter)                    find(filter, {_id:0, a:1, b:1})
      │                                │
      ▼                                ▼
   IXSCAN  (index keys)            IXSCAN  (index keys)
      │                                │
      ▼                                ▼
   FETCH   (read full docs)  ◄── skipped!
      │                                │
      ▼                                ▼
   PROJECTION_SIMPLE               PROJECTION_COVERED
 totalDocsExamined = N           totalDocsExamined = 0
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Covered query | Answered fully from the index | सिर्फ index से answer होने वाली query |
| IXSCAN | Index scan stage | Index पढ़ने वाला stage |
| FETCH | Load full document from collection | Collection से पूरा document लाना |
| Projection | Choose which fields to return | कौन से fields return हों |
| PROJECTION_COVERED | Projection done on index keys | Index keys पर projection |
| totalDocsExamined | Documents read from collection | Collection से पढ़े गए documents |
| Multikey index | Index on an array field | Array field पर बना index |

---

## ⚡ 3-Line Summary
English:
1. A covered query reads only index keys — `explain` shows `totalDocsExamined: 0` and `PROJECTION_COVERED`.
2. Filter fields and returned fields must all be in one index, and `_id` must be excluded (or indexed).
3. Great for hot, small-field reads; avoid for arrays (multikey) and write-heavy collections.

Hindi:
1. Covered query सिर्फ index keys पढ़ती है — `explain` में `totalDocsExamined: 0` और `PROJECTION_COVERED` दिखता है।
2. Filter और return होने वाले सारे fields एक ही index में हों और `_id` हटाया हो (या indexed हो)।
3. छोटे fields वाली hot reads के लिए बढ़िया; arrays (multikey) और write-heavy collections में avoid करो।

---

## ➡️ Next Topic
**50. Index Selection + hint()** — How the query planner picks an index, plan cache, and forcing an index with `hint()`.
