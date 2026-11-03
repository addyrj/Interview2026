# 21. Positional Operators — $, $[], arrayFilters
# हिंदी में: Positional Operators — $, $[], arrayFilters

---

## 🔵 Simple Definition (English)
**Positional operators** let you update **elements inside an array** without knowing their index. There are three tools: `$` (updates the **first** array element that matched the query), `$[]` (updates **all** elements of an array), and `$[identifier]` with the `arrayFilters` option (updates **only the elements that satisfy a condition** you define). They are used inside `updateOne` / `updateMany` / `findOneAndUpdate`.

## 🔵 सरल परिभाषा (Hindi)
**Positional operators** से आप array के अंदर के **elements को update** कर सकते हैं बिना उनका index जाने। तीन tools हैं: `$` (query से match हुआ **पहला** array element update करता है), `$[]` (array के **सभी** elements update करता है), और `$[identifier]` + `arrayFilters` option (सिर्फ वही elements update करता है जो आपकी **condition** satisfy करें)। ये `updateOne` / `updateMany` / `findOneAndUpdate` के अंदर इस्तेमाल होते हैं।

---

## 🔴 Problem it Solves
A Swiggy order document holds an `items` array. When the kitchen finishes the biryani, you need to change only that one item's status — but you do not know whether it sits at index 0, 1 or 7, and fetching the whole document, editing it in JavaScript and writing it back is slow and **race-prone** (two kitchen screens overwrite each other). Hard-coding `items.1.status` is fragile because the order of array elements can change. Positional operators let the **database itself** locate the element(s) and modify them atomically in a single round trip.

## 🔴 यह क्यों बना? (Hindi)
Swiggy के एक order document में `items` array होता है। जब kitchen में biryani तैयार होती है तो आपको सिर्फ उसी item का status बदलना है — पर आपको नहीं पता वो index 0, 1 या 7 पर है। पूरा document fetch करके JavaScript में edit करना और वापस लिखना धीमा और **race-prone** है (दो kitchen screens एक-दूसरे को overwrite कर देंगी)। `items.1.status` hard-code करना भी fragile है क्योंकि array का order बदल सकता है। Positional operators database को खुद element ढूँढने देते हैं और एक ही round trip में atomically modify करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **`$` (first match)**: put the array field in the **query filter** (`{ "items.sku": "raita" }`). MongoDB remembers the index of the first element that matched. In the update, write `"items.$.qty"` — `$` is replaced by that remembered index.
Step 2 → **`$[]` (all elements)**: no filter on the array is needed. `{ $inc: { "scores.$[]": 1 } }` applies the change to every element of `scores`.
Step 3 → **`$[name]` + `arrayFilters` (conditional)**: give a label inside the update path (`items.$[el].status`) and declare the condition for that label in the options: `arrayFilters: [{ "el.price": { $gte: 100 } }]`. Every element matching the filter is updated.
Step 4 → For arrays of **scalars**, the filter refers to the label directly: `arrayFilters: [{ s: { $gt: 10 } }]`.
Step 5 → Remember the limits: `$` touches only the **first** match, needs the array in the query, and errors out otherwise; every label you use must have a matching `arrayFilters` entry (and vice versa).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **`$` (पहला match)**: array field को **query filter** में रखो (`{ "items.sku": "raita" }`)। MongoDB पहले matched element का index याद रखता है। update में `"items.$.qty"` लिखो — `$` की जगह वही index आ जाता है।
Step 2 → **`$[]` (सारे elements)**: array पर filter की ज़रूरत नहीं। `{ $inc: { "scores.$[]": 1 } }` `scores` के हर element पर लागू होता है।
Step 3 → **`$[name]` + `arrayFilters` (conditional)**: update path में एक label दो (`items.$[el].status`) और उस label की condition options में बताओ: `arrayFilters: [{ "el.price": { $gte: 100 } }]`। जो भी elements filter से match करें, सब update होते हैं।
Step 4 → **scalar** arrays के लिए filter सीधे label पर लगता है: `arrayFilters: [{ s: { $gt: 10 } }]`।
Step 5 → सीमाएँ याद रखो: `$` सिर्फ **पहला** match छूता है, array का query में होना ज़रूरी है, वरना error; और हर label का `arrayFilters` में entry होना ज़रूरी है (और उल्टा भी)।

---

## 🟡 Real World Example
**Swiggy order tracking**: an order `{ _id: 1, items: [ {sku:"biryani", price:250, status:"pending"}, {sku:"raita", price:40, ...}, {sku:"coke", price:60, ...} ] }`.
- A customer changes raita quantity to 3 → `$` (we know the sku, not the index).
- The kitchen marks every item priced >= 100 as "cooking" (the hot station handles expensive dishes) → `$[el]` with `arrayFilters`.
- A festival offer adds +1 loyalty point to each entry of a `scores` array → `$[]`.

## 🟡 Real Example Hindi mein
**Swiggy order tracking**: एक order `{ _id: 1, items: [ {sku:"biryani", price:250, status:"pending"}, {sku:"raita", price:40, ...}, {sku:"coke", price:60, ...} ] }`।
- Customer raita की quantity 3 करता है → `$` (हमें sku पता है, index नहीं)।
- Kitchen सभी items जिनकी price >= 100 है उन्हें "cooking" mark करती है → `$[el]` + `arrayFilters`।
- Festival offer में `scores` array के हर entry में +1 loyalty point → `$[]`।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4 with mongosh.

```javascript
// mongosh shell — use a throwaway database
use swiggy_demo                                  // switch to the database
db.orders.drop()                                 // clean start
db.orders.insertOne({                            // one order with an items array
  _id: 1,                                        // fixed _id so output is predictable
  customer: "Aman",                              // order owner
  items: [                                       // array of embedded documents
    { sku: "biryani", qty: 1, price: 250, status: "pending" },
    { sku: "raita",   qty: 2, price: 40,  status: "pending" },
    { sku: "coke",    qty: 1, price: 60,  status: "pending" }
  ],
  scores: [5, 8, 12, 3]                          // array of plain numbers
})

// 1) "$" — first matched element. The array field MUST appear in the filter.
db.orders.updateOne(
  { _id: 1, "items.sku": "raita" },              // filter locates raita; MongoDB remembers its index (1)
  { $set: { "items.$.qty": 3 } }                 // "$" = remembered index, so this edits items[1].qty
)
// Output: { acknowledged: true, insertedId: null, matchedCount: 1, modifiedCount: 1, upsertedCount: 0 }
db.orders.findOne({ _id: 1 }).items[1]
// Output: { sku: 'raita', qty: 3, price: 40, status: 'pending' }

// 2) "$[]" — every element of the array
db.orders.updateOne(
  { _id: 1 },                                    // no array condition needed
  { $inc: { "scores.$[]": 1 } }                  // +1 on EVERY element of scores
)
// scores before [5,8,12,3]  ->  after [6,9,13,4]

// 3) "$[el]" + arrayFilters — only elements that satisfy a condition
db.orders.updateOne(
  { _id: 1 },                                    // pick the document
  { $set: { "items.$[el].status": "cooking" } }, // "el" is a label we invent
  { arrayFilters: [ { "el.price": { $gte: 100 } } ] } // el = items with price >= 100
)
// Result statuses: biryani:cooking, raita:pending, coke:pending

// 4) arrayFilters on a scalar array — label is used directly
db.orders.updateOne(
  { _id: 1 },
  { $set: { "scores.$[s]": 0 } },                // zero out matched numbers
  { arrayFilters: [ { s: { $gt: 10 } } ] }       // only values > 10 (here: 13)
)
// scores now [6,9,0,4]
```

## 💻 Code Example — Advanced

```javascript
// Node.js driver (mongodb v6) — nested arrays + multiple filters + safe error handling
const { MongoClient } = require('mongodb');            // official driver

async function main() {
  const client = new MongoClient('mongodb://127.0.0.1:27017'); // connection string
  await client.connect();                              // open pool
  const orders = client.db('swiggy_demo').collection('orders'); // collection handle

  // Mark one specific item cancelled ONLY IF the order is still open (atomic guard)
  const r1 = await orders.updateOne(
    { _id: 1, status: 'open', 'items.sku': 'coke' },   // doc must be open AND contain coke
    { $set: { 'items.$.status': 'cancelled' } }        // "$" targets the matched coke element
  );
  console.log(r1.matchedCount, r1.modifiedCount);      // 0 0 if the order is not open -> no write

  // Two arrayFilters with two labels: discount expensive items, tag cheap ones
  const r2 = await orders.updateOne(
    { _id: 1 },                                        // one order
    {
      $mul: { 'items.$[exp].price': 0.9 },             // 10% off for label "exp"
      $set: { 'items.$[cheap].tag': 'combo' }          // add a field for label "cheap"
    },
    {
      arrayFilters: [
        { 'exp.price': { $gte: 200 } },                // "exp"   : price >= 200
        { 'cheap.price': { $lt: 100 } }                // "cheap" : price < 100
      ]
    }
  );
  console.log('modified', r2.modifiedCount);           // 1 (one document changed)

  // $ and updateMany: for EVERY order containing a raita, set raita qty to 1
  await orders.updateMany(
    { 'items.sku': 'raita' },                          // many docs match
    { $set: { 'items.$.qty': 1 } }                     // each doc: its own first raita
  );

  // Nested arrays: orders.$[o].lines.$[l].done -> two levels, two labels
  await orders.updateOne(
    { _id: 2 },
    { $set: { 'parcels.$[p].lines.$[l].done': true } }, // two labels = two nested arrays
    { arrayFilters: [ { 'p.kind': 'hot' }, { 'l.qty': { $gt: 1 } } ] }
  );
  await client.close();                                // close pool
}
main().catch(console.error);
```

---

## 🟠 Express.js / Mongoose Integration

Tested against MongoDB 8.0.4 with Express 5 and Mongoose 8.

```javascript
const express = require('express');                    // web framework
const mongoose = require('mongoose');                  // ODM

const Order = mongoose.model('Order', new mongoose.Schema({
  customer: String,
  items: [{ sku: String, qty: Number, status: { type: String, default: 'pending' }, price: Number }]
}));

const app = express();
app.use(express.json());                               // parse JSON bodies

// PATCH /orders/:id/items/:sku  body: { "qty": 5 }  -> uses "$"
app.patch('/orders/:id/items/:sku', async (req, res) => {
  const r = await Order.updateOne(
    { _id: req.params.id, 'items.sku': req.params.sku }, // array field must be in the filter
    { $set: { 'items.$.qty': req.body.qty } }
  );
  res.json({ matched: r.matchedCount, modified: r.modifiedCount });
});
// Real run -> 200 {"matched":1,"modified":1}; unknown sku -> 200 {"matched":0,"modified":0}

// POST /orders/:id/cook  body: { "min": 100 }  -> uses $[el] + arrayFilters
app.post('/orders/:id/cook', async (req, res) => {
  const r = await Order.updateOne(
    { _id: req.params.id },
    { $set: { 'items.$[el].status': 'cooking' } },
    { arrayFilters: [{ 'el.price': { $gte: Number(req.body.min) } }] } // Mongoose passes it through
  );
  res.json({ modified: r.modifiedCount });             // real run -> {"modified":1}
});
```
Note: Mongoose casts `arrayFilters` values using the schema, so make sure `min` is a Number (not a string).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `$` without the array in the query
```javascript
// Wrong — filter does not mention items, so there is no "matched position" to remember
db.orders.updateOne({ _id: 1 }, { $set: { "items.$.qty": 9 } })
// Real error: The positional operator did not find the match needed from the query.

// Right — put the array condition in the filter (or use $[] / arrayFilters)
db.orders.updateOne({ _id: 1, "items.sku": "raita" }, { $set: { "items.$.qty": 9 } })
```

❌ Mistake 2: Expecting `$` to update every match
```javascript
// Wrong assumption — "$" only touches the FIRST matching element
db.orders.updateOne({ _id: 1, "items.status": { $in: ["cooking","pending"] } }, { $set: { "items.$.flag": true } })
// Real result: only biryani got flag:true; raita and coke untouched.

// Right — use arrayFilters when many elements should change
db.orders.updateOne({ _id: 1 }, { $set: { "items.$[e].flag": true } }, { arrayFilters: [ { "e.status": { $in: ["cooking","pending"] } } ] })
```

❌ Mistake 3: Label and arrayFilters do not match
```javascript
// Wrong — label "s" has no filter
db.orders.updateOne({ _id: 1 }, { $set: { "scores.$[s]": 1 } }, { arrayFilters: [ { x: 1 } ] })
// Real error: No array filter found for identifier 's' in path 'scores.$[s]'
```

---

## 🧠 Tricky Interview Question

Order has `items: [ {sku:"a", qty:1}, {sku:"a", qty:5} ]`. You run:
```javascript
db.orders.updateOne({ "items.sku": "a" }, { $set: { "items.$.qty": 0 } })
```
How many elements change, and how would you change both?

Answer: **Only one** — the first element (`qty:1` becomes `0`), because `$` stores the position of the first match only. To change both use `$[]` (all elements) or `$[x]` with `arrayFilters: [{ "x.sku": "a" }]`. A second subtlety: with two array conditions in the filter (`"items.sku":"a", "items.qty":5`) the `$` position may refer to a different element than you expect — use `$elemMatch` in the filter when the conditions must apply to the **same** element.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `$`, `$[]` and `$[identifier]`?
A1: `$` updates the first element that matched the query filter. `$[]` updates all elements of the array. `$[identifier]` updates all elements that satisfy the matching condition defined in `arrayFilters`.

Q2: Why does `$` fail when the array is not in the query?
A2: `$` is just a placeholder for "the index found while matching". If the filter does not reference the array, no index is recorded, so MongoDB throws "The positional operator did not find the match needed from the query".

Q3: Can you use `$` with `upsert: true`?
A3: No — `$` cannot be used together with an upsert that inserts, because a newly inserted document has no matched array position. Use `$push`/`$set` of the whole array, or `arrayFilters` where valid, and test the insert path separately.

Q4: How do you update elements in nested arrays?
A4: Use multiple filtered positional operators, e.g. `parcels.$[p].lines.$[l].done`, with one `arrayFilters` entry for each label (`p` and `l`). `$` can only be used for one level.

Q5: Why prefer positional operators to read-modify-write in application code?
A5: They run atomically inside the server on a single document, avoid an extra network trip, and remove the lost-update race that happens when two clients read the same document and write back different versions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You update specific array elements inside embedded documents (order items, cart lines, comments).
- You must change many elements by a condition (arrayFilters) or all (`$[]`).
- You want atomic, race-free partial updates.

❌ Avoid when:
- Arrays are huge and unbounded — consider a separate collection instead (each element = its own document).
- You need to change the array structure (add/remove elements) — use `$push`, `$pull`, `$addToSet`.
- You need different values per element — compute in an aggregation-pipeline update (`updateOne(filter, [ { $set: ... } ])`).

---

## 📊 Visual Diagram
```
 items: [ {raita}  {biryani}  {coke} ]       filter says: items.sku = "raita"
              │
   ┌──────────┴───────────────────────────────────────────┐
   │  $        -> first match only      items.$.qty        │
   │  $[]      -> every element         scores.$[]         │
   │  $[el]    -> where arrayFilters ok items.$[el].status  │
   └──────────────────────────────────────────────────────┘
 arrayFilters: [ { "el.price": { $gte: 100 } } ]
        only elements with price >= 100 are changed (biryani)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$` positional | Updates first array element matched by the query | Query से match हुए पहले element को update करता है |
| `$[]` all-positional | Updates every element in an array | Array के सभी elements update करता है |
| `$[identifier]` | Filtered positional operator | Condition वाला positional operator |
| `arrayFilters` | Option defining the conditions for each identifier | हर identifier की condition देने वाला option |
| `$elemMatch` | Match one element satisfying several conditions | एक ही element पर कई conditions |
| Atomic update | Single-document change that is all-or-nothing | एक document का all-or-nothing बदलाव |

---

## ⚡ 3-Line Summary
English:
1. Use `$` for the first matched array element, `$[]` for all elements, and `$[label]` with `arrayFilters` for conditional updates.
2. `$` needs the array in the query filter and touches only one element; every label needs an `arrayFilters` entry.
3. These operators update arrays atomically in one request, avoiding read-modify-write races.

Hindi:
1. पहले matched element के लिए `$`, सारे elements के लिए `$[]`, और conditional updates के लिए `$[label]` + `arrayFilters` इस्तेमाल करो।
2. `$` को array query filter में चाहिए और वो सिर्फ एक element बदलता है; हर label के लिए `arrayFilters` entry ज़रूरी है।
3. ये operators arrays को एक ही request में atomically update करते हैं, read-modify-write races से बचाते हैं।

---

## ➡️ Next Topic
**22. replaceOne and findOneAndUpdate** — replacing a whole document and updating-and-returning a document in a single atomic step.
