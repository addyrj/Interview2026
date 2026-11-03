# 54. $match and $project
# हिंदी में: $match और $project

---

## 🔵 Simple Definition (English)
**`$match`** is the aggregation stage that filters documents (like `WHERE` in SQL) using the same query syntax as `find()`. **`$project`** reshapes each document: it picks fields, drops fields, renames them, and computes new ones (like the `SELECT` list). Together they are the most common first two stages of a pipeline.

## 🔵 सरल परिभाषा (Hindi)
**`$match`** वो aggregation stage है जो documents को filter करता है (SQL के `WHERE` जैसा), और syntax वही है जो `find()` में होता है। **`$project`** हर document का shape बदलता है: fields चुनता है, हटाता है, rename करता है और नए computed fields बनाता है (SQL के `SELECT` जैसा)। ये दोनों pipeline के सबसे common शुरुआती stages हैं।

---

## 🔴 Problem it Solves
Without filtering early, every later stage (`$group`, `$lookup`, `$sort`) processes the whole collection, which is slow and memory hungry. Without `$project`, big documents travel through the pipeline and across the network even when you need two fields. `$match` at the start can also use an index, and `$project` shrinks documents so later stages move less data.

## 🔴 यह क्यों बना? (Hindi)
अगर शुरू में filter न करें तो बाद के सारे stages (`$group`, `$lookup`, `$sort`) पूरी collection पर चलते हैं, जो slow है और memory खाता है। `$project` के बिना बड़े documents पूरे pipeline और network से गुज़रते हैं, जबकि चाहिए सिर्फ दो fields। Pipeline की शुरुआत में `$match` index इस्तेमाल कर सकता है, और `$project` documents छोटे कर देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `$match: { status: "delivered" }` keeps only documents satisfying the filter (all query operators like `$gte`, `$in`, `$or` work).
Step 2 → If `$match` is the first stage, MongoDB can use an index on those fields.
Step 3 → `$project: { customer: 1, amount: 1 }` is an inclusion projection: only listed fields (plus `_id`) pass on.
Step 4 → `_id: 0` removes `_id`. You cannot mix include and exclude in one `$project` (except `_id`).
Step 5 → Computed fields use expressions: `{ withGst: { $multiply: ["$amount", 1.05] } }`. `"$amount"` means "value of the field amount".

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `$match: { status: "delivered" }` सिर्फ वही documents रखता है जो filter satisfy करें (`$gte`, `$in`, `$or` सब चलते हैं)।
Step 2 → अगर `$match` पहला stage है तो MongoDB उन fields के index का इस्तेमाल कर सकता है।
Step 3 → `$project: { customer: 1, amount: 1 }` inclusion projection है: सिर्फ listed fields (और `_id`) आगे जाते हैं।
Step 4 → `_id: 0` से `_id` हट जाता है। एक `$project` में include और exclude mix नहीं कर सकते (`_id` को छोड़कर)।
Step 5 → Computed fields में expressions लगते हैं: `{ withGst: { $multiply: ["$amount", 1.05] } }`। `"$amount"` का मतलब है field amount की value।

---

## 🟡 Real World Example
**Swiggy's order-history screen** only needs restaurant name, amount and status of delivered orders from the last 30 days. The backend runs `$match` on `status` and date (using an index), then `$project` to return three fields instead of the full order with items, address and payment blob. The mobile payload shrinks a lot.

## 🟡 Real Example Hindi mein
**Swiggy की order-history screen** को सिर्फ restaurant name, amount और status चाहिए, वो भी पिछले 30 दिनों के delivered orders के। Backend `$match` (index के साथ) चलाता है, फिर `$project` से तीन fields लौटाता है, पूरा order (items, address, payment) नहीं। Mobile payload काफी छोटा हो जाता है।

---

## 💻 Code Example — Basic

Sample data (`shop.orders`, 6 docs): `{_id:1, customer:"Aarav", city:"Delhi", status:"delivered", amount:450, items:[...]}` and similar. Tested on MongoDB 8.0.4.

```javascript
// mongosh
use shop // switch to the shop database

db.orders.aggregate([
  { $match: { status: "delivered", amount: { $gte: 300 } } }, // keep delivered orders of 300 or more
  { $project: {
      _id: 0,                                              // drop _id
      customer: 1,                                         // keep customer
      amount: 1,                                           // keep amount
      withGst: { $multiply: ["$amount", 1.05] }            // computed field: amount + 5% GST
  } }
])
// Output (real):
// { customer: 'Aarav', amount: 450, withGst: 472.5 }
// { customer: 'Kabir', amount: 890, withGst: 934.5 }
// { customer: 'Diya',  amount: 310, withGst: 325.5 }
```

## 💻 Code Example — Advanced

```javascript
// $project with array expression: count items per order
db.orders.aggregate([
  { $project: { customer: 1, n: { $size: "$items" } } }, // $size gives array length
  { $limit: 3 }                                          // first 3 docs only
])
// Output (real):
// { _id: 1, customer: 'Aarav', n: 2 }
// { _id: 2, customer: 'Diya',  n: 1 }
// { _id: 3, customer: 'Aarav', n: 2 }

// Node driver: same pipeline, as a JS array
const rows = await db.collection("orders").aggregate([
  { $match: { city: "Mumbai" } },               // filter first, uses index on city if present
  { $project: { _id: 0, customer: 1, amount: 1 } } // then slim down documents
]).toArray();                                    // run and collect results
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose model bound to the existing "orders" collection (tested against mongod 8.0.4)
const Order = mongoose.model("Order", new mongoose.Schema({
  customer: String, city: String, status: String, amount: Number
}), "orders");

app.get("/api/orders/delivered", async (req, res) => {
  const rows = await Order.aggregate([
    { $match: { status: "delivered" } },                      // NOTE: no schema casting inside aggregate
    { $project: { _id: 0, customer: 1, amount: 1 } }          // return slim documents
  ]);
  res.json(rows);                                             // plain JS objects, not Mongoose docs
});
```
Important: `Model.aggregate()` does NOT cast values. If you match on an `_id`, pass `new mongoose.Types.ObjectId(id)`, not a string.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Mixing inclusion and exclusion
```javascript
// Wrong — error: cannot do exclusion on field city in inclusion projection
db.orders.aggregate([{ $project: { customer: 1, city: 0 } }])
// Right — pick one style (only _id may be excluded alongside inclusions)
db.orders.aggregate([{ $project: { customer: 1, _id: 0 } }])
```

❌ Mistake 2: Putting `$match` late in the pipeline
```javascript
// Wrong — groups everything, then filters (no index, lots of work)
db.orders.aggregate([{ $group: { _id: "$city", t: { $sum: "$amount" } } }, { $match: { _id: "Delhi" } }])
// Right — filter first
db.orders.aggregate([{ $match: { city: "Delhi" } }, { $group: { _id: "$city", t: { $sum: "$amount" } } }])
```

❌ Mistake 3: Forgetting `$` for field paths in expressions
✅ `{ $multiply: ["amount", 2] }` fails/uses a string literal; use `"$amount"`.

---

## 🧠 Tricky Interview Question
Q: What does `db.orders.aggregate([{ $project: { total: "$amount" } }])` return, and does `_id` appear?
Answer: Yes, `_id` appears by default. The output is `{ _id: 1, total: 450 }` and so on: `amount` is renamed to `total` and `_id` is kept unless you write `_id: 0`. A second trap: `$match` cannot take aggregation expressions like `{ $gt: ["$a", "$b"] }` directly; wrap them in `$expr`.

---

## ⚫ Interview Questions + Answers

Q1: How is `$match` different from `find()`?
A1: Same query operators, but `$match` is a pipeline stage, so its output feeds later stages. Inside `$match` you cannot use aggregation expressions directly (use `$expr` for that).

Q2: Why put `$match` first?
A2: It reduces the document count early and can use indexes. The optimizer also moves `$match` earlier when it can, but you should not rely on it.

Q3: Difference between `$project` and `$addFields`?
A3: `$project` controls the exact output shape (inclusion drops everything else). `$addFields`/`$set` keeps all existing fields and only adds or overwrites.

Q4: Can `$project` create nested fields?
A4: Yes: `{ $project: { "name.first": 1 } }` or `{ $project: { loc: { city: "$city" } } }`.

Q5: Does `$project` reduce memory use?
A5: Yes, later stages handle smaller documents, and MongoDB can even infer needed fields and skip loading the rest from disk (dependency analysis).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a filtered, slimmed list for an API response
- You must compute or rename fields before `$group`/`$sort`

❌ Avoid when:
- You only add fields (use `$addFields`/`$set`, simpler)
- A plain `find()` with projection is enough (no need for a pipeline)

---

## 📊 Visual Diagram
```
 orders (6 docs)
      │
      ▼
 ┌───────────────┐   status = delivered, amount >= 300
 │    $match     │──────────────► 3 docs (index can be used here)
 └───────────────┘
      │
      ▼
 ┌───────────────┐   keep customer, amount; add withGst; drop _id
 │   $project    │──────────────► { customer, amount, withGst }
 └───────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stage | One step of a pipeline | Pipeline का एक step |
| `$match` | Filters documents | Documents filter करता है |
| `$project` | Reshapes documents | Documents का shape बदलता है |
| Inclusion projection | Lists fields to keep | रखने वाले fields की list |
| Field path | `"$amount"` reference | Field की value का reference |
| Expression | Operator computing a value | Value निकालने वाला operator |

---

## ⚡ 3-Line Summary
English:
1. `$match` filters like `WHERE`; `$project` shapes output like `SELECT`.
2. Put `$match` first so it uses indexes and shrinks the data early.
3. Do not mix include and exclude in `$project`; `_id` is kept unless `_id: 0`.

Hindi:
1. `$match` `WHERE` की तरह filter करता है; `$project` `SELECT` की तरह output का shape बनाता है।
2. `$match` पहले रखो ताकि index चले और data जल्दी कम हो।
3. `$project` में include/exclude mix मत करो; `_id: 0` न लिखो तो `_id` रहता है।

---

## ➡️ Next Topic
**55. $group and Accumulators ($sum, $avg, $push)** — grouping documents and computing totals, averages and lists.
