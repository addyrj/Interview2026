# 34. Querying Arrays of Documents
# हिंदी में: Documents के Arrays को Query करना

---

## 🔵 Simple Definition (English)
An **array of documents** is a field whose value is a list of embedded objects, e.g. `items: [ { sku: "pizza", qty: 2 }, { sku: "coke", qty: 1 } ]`. You query it by combining **dot notation** (`"items.sku"`), **`$elemMatch`** (all conditions on the **same** element), **exact subdocument match** (`{ items: { sku, qty, price } }`) and **positional access** (`"items.0.sku"`). Getting only the matching elements back needs `items.$` projection, `$elemMatch` projection, `$filter` or `$unwind`.

## 🔵 सरल परिभाषा (Hindi)
**Documents का array** ऐसी field है जिसकी value embedded objects की list हो, जैसे `items: [ { sku: "pizza", qty: 2 }, { sku: "coke", qty: 1 } ]`। इसे query करने के लिए **dot notation** (`"items.sku"`), **`$elemMatch`** (सारी conditions **एक ही** element पर), **exact subdocument match** (`{ items: { sku, qty, price } }`) और **positional access** (`"items.0.sku"`) मिलाकर इस्तेमाल करते हैं। सिर्फ matching elements वापस पाने के लिए `items.$` projection, `$elemMatch` projection, `$filter` या `$unwind` चाहिए।

---

## 🔴 Problem it Solves
Order, cart and comment data is naturally "one parent, many child objects". Questions asked of it are subtle: "orders that contain pizza" (any element), "orders where pizza was bought with qty > 1" (same element!), "orders whose second item is coke" (position), "show me only the pizza line, not the whole order". If you don't know which operator expresses which meaning, you silently get wrong results — e.g. an order with pizza qty 1 plus fries qty 4 matching "pizza with qty > 1".

## 🔴 यह क्यों बना? (Hindi)
Order, cart और comment data स्वाभाविक रूप से "एक parent, कई child objects" होता है। इस पर पूछे जाने वाले सवाल सूक्ष्म हैं: "वो orders जिनमें pizza है" (कोई भी element), "जहाँ pizza qty > 1 के साथ ख़रीदा गया" (एक ही element!), "जिनका दूसरा item coke है" (position), "मुझे सिर्फ pizza वाली line दिखाओ, पूरा order नहीं"। अगर पता न हो कि कौन-सा operator कौन-सा मतलब देता है तो चुपचाप ग़लत results मिलते हैं — जैसे pizza qty 1 + fries qty 4 वाला order "pizza qty > 1" से match हो जाना।

---

## 🟢 How it Works — Step by Step

Step 1 → **Any element**: `{ "items.sku": "pizza" }` = at least one element has `sku: "pizza"`.
Step 2 → **Several dotted conditions** (`"items.sku": "pizza", "items.qty": { $gt: 1 }`) can be satisfied by **different** elements.
Step 3 → **Same element**: `{ items: { $elemMatch: { sku: "pizza", qty: { $gt: 1 } } } }`.
Step 4 → **Exact element**: `{ items: { sku: "coke", qty: 1, price: 60 } }` matches only an element with exactly these fields in this order (reordering the keys fails).
Step 5 → **Position**: `{ "items.0.sku": "pizza" }` tests the first element only.
Step 6 → **Length**: `{ items: { $size: 2 } }`.
Step 7 → **Returning only the matching element(s)**: `find(q, { "items.$": 1 })` (first match), projection `$elemMatch` (first match), or in aggregation `$unwind` + `$match` (all matches as separate rows) or `$filter` (all matches, kept as an array).
Step 8 → **Index**: `createIndex({ "items.sku": 1 })` creates a **multikey** index (one key per array element).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **कोई भी element**: `{ "items.sku": "pizza" }` = कम से कम एक element का `sku: "pizza"` है।
Step 2 → **कई dotted conditions** (`"items.sku": "pizza", "items.qty": { $gt: 1 }`) **अलग-अलग** elements से पूरी हो सकती हैं।
Step 3 → **एक ही element**: `{ items: { $elemMatch: { sku: "pizza", qty: { $gt: 1 } } } }`।
Step 4 → **ठीक वही element**: `{ items: { sku: "coke", qty: 1, price: 60 } }` सिर्फ उस element से match करता है जिसमें ठीक यही fields इसी क्रम में हों (keys का क्रम बदलने पर fail)।
Step 5 → **Position**: `{ "items.0.sku": "pizza" }` सिर्फ पहला element जाँचता है।
Step 6 → **Length**: `{ items: { $size: 2 } }`।
Step 7 → **सिर्फ matching element(s) लौटाना**: `find(q, { "items.$": 1 })` (पहला match), projection `$elemMatch` (पहला match), या aggregation में `$unwind` + `$match` (सारे matches अलग rows में) या `$filter` (सारे matches array के रूप में)।
Step 8 → **Index**: `createIndex({ "items.sku": 1 })` एक **multikey** index बनाता है (हर array element के लिए एक key)।

---

## 🟡 Real World Example
**Swiggy order history**: `{ cust, items: [ {sku, qty, price} ] }`. Support asks: "Which orders contain pizza?" -> `"items.sku": "pizza"`. Analytics: "orders where a pizza was bought in quantity > 1" -> `$elemMatch`. Finance: "list every item line with qty >= 4 across all orders" -> `$unwind` + `$match`. UI: "show only the pizza line of this order" -> `"items.$": 1` projection.

## 🟡 Real Example Hindi mein
**Swiggy order history**: `{ cust, items: [ {sku, qty, price} ] }`। Support पूछती है: "किन orders में pizza है?" -> `"items.sku": "pizza"`। Analytics: "वो orders जहाँ pizza की quantity > 1 है" -> `$elemMatch`। Finance: "सभी orders में qty >= 4 वाली हर item line" -> `$unwind` + `$match`। UI: "इस order की सिर्फ pizza line दिखाओ" -> `"items.$": 1` projection।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4, mongosh.

```javascript
use swiggy_orders_demo                             // switch database
db.dropDatabase()                                  // clean start
db.o.insertMany([                                  // three orders
  { _id: 1, cust: "A", items: [ { sku: "pizza", qty: 2, price: 300 }, { sku: "coke",  qty: 1, price: 60 } ] },
  { _id: 2, cust: "B", items: [ { sku: "pizza", qty: 1, price: 300 }, { sku: "fries", qty: 4, price: 90 } ] },
  { _id: 3, cust: "C", items: [ { sku: "coke",  qty: 5, price: 60 } ] }
])
const ids = q => print(JSON.stringify(db.o.find(q).toArray().map(x => x._id)))

ids({ "items.sku": "pizza" })                      // [1,2]  any element is pizza
ids({ "items.sku": "pizza", "items.qty": { $gt: 1 } })              // [1,2]  TRAP: order 2 = pizza(qty1) + fries(qty4)
ids({ items: { $elemMatch: { sku: "pizza", qty: { $gt: 1 } } } })   // [1]    same element must satisfy both
ids({ items: { sku: "coke", qty: 1, price: 60 } }) // [1]    exact element, same key order
ids({ items: { qty: 1, sku: "coke", price: 60 } }) // []     same values but different key order -> no match
ids({ "items.0.sku": "pizza" })                    // [1,2]  first element is pizza
ids({ "items.1.sku": "coke" })                     // [1]    second element is coke
ids({ items: { $size: 2 } })                       // [1,2]  exactly two lines

// ---- getting back only the matching element ----
db.o.find({ "items.sku": "pizza" }, { "items.$": 1 }).toArray()
// Output: [ { _id: 1, items: [ { sku: 'pizza', qty: 2, price: 300 } ] },
//           { _id: 2, items: [ { sku: 'pizza', qty: 1, price: 300 } ] } ]

// ---- projecting a sub-field of every element ----
db.o.find({}, { "items.sku": 1, _id: 0 }).toArray()
// Output: [ { items: [ {sku:'pizza'}, {sku:'coke'} ] }, { items: [ {sku:'pizza'}, {sku:'fries'} ] }, { items: [ {sku:'coke'} ] } ]
```

## 💻 Code Example — Advanced

```javascript
// $unwind + $match: every element that qualifies becomes its own row
db.o.aggregate([
  { $unwind: "$items" },                           // one output doc per array element
  { $match: { "items.qty": { $gte: 4 } } },        // filter the individual lines
  { $project: { cust: 1, "items.sku": 1 } }        // shape the output
])
// Output: [ { _id: 2, cust: 'B', items: { sku: 'fries' } }, { _id: 3, cust: 'C', items: { sku: 'coke' } } ]

// $filter: keep the array shape, keep only elements that match
db.o.aggregate([
  { $match: { _id: 1 } },
  { $project: { items: { $filter: { input: "$items", as: "i", cond: { $gt: ["$$i.price", 100] } } } } }
])
// Output: [ { _id: 1, items: [ { sku: 'pizza', qty: 2, price: 300 } ] } ]

// Multikey index on a field inside an array of documents
db.o.createIndex({ "items.sku": 1 })
db.o.find({ "items.sku": "pizza" }).explain().queryPlanner.winningPlan.inputStage.indexName
// Output: 'items.sku_1'   (the index is multikey: isMultiKey: true)
```

```javascript
// Node.js driver v6 — "orders with at least one pizza line of qty >= 2", return that line only
const rows = await db.collection('o').aggregate([
  { $match: { items: { $elemMatch: { sku: 'pizza', qty: { $gte: 2 } } } } }, // uses the multikey index
  { $project: { cust: 1, items: { $filter: { input: '$items', as: 'i',
      cond: { $and: [ { $eq: ['$$i.sku', 'pizza'] }, { $gte: ['$$i.qty', 2] } ] } } } } }
]).toArray();
```

---

## 🟠 Express.js / Mongoose Integration

Tested against MongoDB 8.0.4, Express 5, Mongoose 8.

```javascript
const express = require('express');
const mongoose = require('mongoose');
const Order = mongoose.model('Order', new mongoose.Schema({
  customer: String,
  items: [{ sku: String, qty: Number, price: Number }]   // array of subdocuments (each gets its own _id)
}));
const app = express();

// GET /orders?sku=raita&minQty=3  -> same-element match
app.get('/orders', async (req, res) => {
  const f = {};
  if (req.query.sku) f.items = { $elemMatch: { sku: String(req.query.sku), qty: { $gte: Number(req.query.minQty || 1) } } };
  res.json(await Order.find(f).select('customer -_id').lean());
});
// Real run (with an order containing raita qty 5) -> [{"customer":"Aman K"}]
```
Mongoose adds an `_id` to every array subdocument by default, so exact-subdocument matching in Mongoose-created data rarely works — always prefer `$elemMatch` or dotted fields. Disable with `{ _id: false }` in the sub-schema if you don't need it.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Separate dotted conditions for one element
```javascript
db.o.find({ "items.sku": "pizza", "items.qty": { $gt: 1 } })       // Wrong: [1,2] (order 2 is pizza qty 1)
db.o.find({ items: { $elemMatch: { sku: "pizza", qty: { $gt: 1 } } } }) // Right: [1]
```

❌ Mistake 2: Expecting the query to trim the array
```javascript
db.o.find({ "items.sku": "pizza" })       // Wrong expectation: returns the WHOLE items array
db.o.find({ "items.sku": "pizza" }, { "items.$": 1 }) // Right: only the first matching element
// For ALL matching elements use $filter or $unwind in aggregation
```

❌ Mistake 3: Exact-subdocument match with different key order
```javascript
db.o.find({ items: { qty: 1, sku: "coke", price: 60 } })   // Wrong: [] — key order differs
db.o.find({ items: { $elemMatch: { sku: "coke", qty: 1, price: 60 } } }) // Right: order-insensitive
```

---

## 🧠 Tricky Interview Question

```javascript
db.o.find({ "items.sku": "pizza", "items.qty": { $gt: 1 } })
```
Order 2 is `items: [ {pizza, qty:1}, {fries, qty:4} ]`. Does it match, and why?

Answer: **Yes**. The first condition is satisfied by element 0 (`pizza`), the second by element 1 (`fries`, qty 4). Plain dotted conditions are evaluated independently across the array. Use `$elemMatch` to force both conditions on one element. Real outputs: dotted `[1,2]`, `$elemMatch` `[1]`.

---

## ⚫ Interview Questions + Answers

Q1: How do you query a field inside an array of subdocuments?
A1: Use dot notation: `{ "items.sku": "pizza" }` matches if any element has that value.

Q2: What does `$elemMatch` add?
A2: It requires all its conditions to be satisfied by one and the same array element.

Q3: How do you return only matching elements?
A3: Positional projection `{ "items.$": 1 }` or projection `$elemMatch` return the first match; aggregation `$filter` returns all matches in array form, `$unwind` + `$match` returns them as separate documents.

Q4: What is a multikey index?
A4: An index on an array field (or a field inside array subdocuments) that stores one key per array element, letting `"items.sku"` queries use an index. A compound multikey index can include at most one array field.

Q5: Why is `{ items: { sku: "coke", qty: 1 } }` unreliable?
A5: It is an exact subdocument match — all fields and their order must match, and Mongoose's auto `_id` per subdocument breaks it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Child objects are few, bounded and always read with the parent (order lines, addresses, variants).
- You filter by child attributes (`$elemMatch`) and index them (multikey).

❌ Avoid when:
- The array grows without bound (chat messages, logs) — document 16 MB limit and slow updates; use a child collection.
- You need to query children independently, paginate or join heavily.
- You always need only the matching elements and arrays are large — consider a separate collection.

---

## 📊 Visual Diagram
```
 order 2: items: [ {pizza,1,300}  {fries,4,90} ]
                       ▲               ▲
 "items.sku":"pizza" ──┘               │   different elements
 "items.qty":{$gt:1} ──────────────────┘   => MATCHES (trap)

 $elemMatch:{sku:"pizza",qty:{$gt:1}}   -> must be the SAME element => no match
 projection {"items.$":1}               -> returns only the first matching element
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Array of documents | List of embedded objects | Embedded objects की list |
| `$elemMatch` | Same-element multi-condition match | एक ही element पर कई conditions |
| `items.$` | Return first matching element | पहला matching element लौटाओ |
| `$filter` | Keep matching elements of an array | Array के matching elements रखो |
| `$unwind` | One document per array element | हर element का अलग document |
| Multikey index | One index key per array element | हर element के लिए index key |

---

## ⚡ 3-Line Summary
English:
1. Use dotted paths for "any element" and `$elemMatch` when several conditions must hold on the same element.
2. Queries return whole documents; trim arrays with `items.$`, `$filter` or `$unwind`.
3. Exact subdocument matching is key-order sensitive — avoid it, and index with `"items.sku"` (multikey).

Hindi:
1. "कोई भी element" के लिए dotted paths और जब कई conditions एक ही element पर चाहिए तब `$elemMatch` इस्तेमाल करो।
2. Queries पूरे documents लौटाती हैं; arrays छाँटने के लिए `items.$`, `$filter` या `$unwind` लो।
3. Exact subdocument matching key क्रम पर निर्भर है — उससे बचो, और `"items.sku"` (multikey) पर index बनाओ।

---

## ➡️ Next Topic
**35. Projection Operators ($slice, $elemMatch)** — shaping returned arrays: first N, last N, a window, or the first matching element.
