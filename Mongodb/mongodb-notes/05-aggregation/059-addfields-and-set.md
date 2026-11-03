# 59. $addFields and $set
# हिंदी में: $addFields और $set

---

## 🔵 Simple Definition (English)
**`$addFields`** adds new fields to every document or overwrites existing ones while keeping all other fields. **`$set`** is an exact alias of `$addFields` (added in 4.2 so pipelines read like update operations). **`$unset`** is the matching stage that removes fields.

## 🔵 सरल परिभाषा (Hindi)
**`$addFields`** हर document में नए fields जोड़ता है या मौजूदा fields overwrite करता है, बाकी सब fields वैसे ही रहते हैं। **`$set`**, `$addFields` का बिल्कुल वही alias है (4.2 में आया ताकि pipelines update operations जैसे पढ़ें)। **`$unset`** fields हटाने वाला साथी stage है।

---

## 🔴 Problem it Solves
`$project` in inclusion mode drops every field you do not list. To just add `gst` to full documents you would have to list all fields. `$addFields` adds computed values without touching the rest, making multi-step calculations easy (compute `gst`, then `total` from it).

## 🔴 यह क्यों बना? (Hindi)
Inclusion mode में `$project` हर वो field हटा देता है जो आपने list नहीं किया। पूरे document में सिर्फ `gst` जोड़ना हो तो सारे fields लिखने पड़ते। `$addFields` बाकी को छुए बिना computed values जोड़ता है, जिससे multi-step गणना (पहले `gst`, फिर उससे `total`) आसान हो जाती है।

---

## 🟢 How it Works — Step by Step

Step 1 → `{ $set: { gst: { $multiply: ["$amount", 0.05] } } }` adds `gst`.
Step 2 → If the field name already exists, it is overwritten (position stays).
Step 3 → Dotted paths create or update embedded fields: `"meta.src": "app"`.
Step 4 → Within one stage, expressions see the ORIGINAL document, not fields set in the same stage. Use two stages to chain.
Step 5 → `$unset: ["items", "ts"]` removes fields (like `$project: { items: 0 }`).
Step 6 → Everything else in the document flows through untouched.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `{ $set: { gst: { $multiply: ["$amount", 0.05] } } }` से `gst` जुड़ता है।
Step 2 → अगर field का नाम पहले से है तो overwrite होता है (position वही रहती है)।
Step 3 → Dotted paths embedded fields बनाते/बदलते हैं: `"meta.src": "app"`।
Step 4 → एक stage के अंदर expressions ORIGINAL document देखते हैं, उसी stage में set हुए fields नहीं। Chain के लिए दो stages लगाओ।
Step 5 → `$unset: ["items", "ts"]` fields हटाता है (`$project: { items: 0 }` जैसा)।
Step 6 → बाकी document बिना बदले आगे जाता है।

---

## 🟡 Real World Example
**Flipkart's order summary** takes each order and adds `gst`, `deliveryFee` and `grandTotal` fields, plus a `meta.source: "app"` marker. The order's items, address and status stay as they were, so the same document feeds later `$group` and `$lookup` stages.

## 🟡 Real Example Hindi mein
**Flipkart की order summary** हर order में `gst`, `deliveryFee` और `grandTotal` fields और `meta.source: "app"` marker जोड़ती है। Order के items, address और status वैसे ही रहते हैं, इसलिए वही document आगे `$group` और `$lookup` stages को मिलता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh, MongoDB 8.0.4, shop.orders
db.orders.aggregate([
  { $match: { _id: { $lte: 2 } } },                // orders 1 and 2
  { $addFields: {
      gst: { $multiply: ["$amount", 0.05] },       // new field
      amount: { $add: ["$amount", 10] }            // overwrite: add a Rs 10 fee (uses ORIGINAL amount)
  } },
  { $project: { amount: 1, gst: 1 } }              // show only the two fields
])
// Output (real):
// { _id: 1, amount: 460, gst: 22.5 }               // gst computed from 450, not 460
// { _id: 2, amount: 240, gst: 11.5 }
```

## 💻 Code Example — Advanced

```javascript
// $set with dotted path, then $unset to remove fields
db.orders.aggregate([
  { $match: { _id: 1 } },
  { $set: { "meta.src": "app" } },                 // creates embedded object meta
  { $unset: ["items", "ts"] }                      // remove two fields
])
// Output (real):
// { _id: 1, customer: 'Aarav', city: 'Delhi', status: 'delivered', amount: 450, meta: { src: 'app' } }

// Two stages when the second value depends on the first
db.orders.aggregate([
  { $set: { gst: { $multiply: ["$amount", 0.05] } } },       // stage 1: gst
  { $set: { total: { $add: ["$amount", "$gst"] } } }         // stage 2: can now use $gst
])
```

Note: `$set` the pipeline stage is different from the update operator `$set` in `updateOne`. For pipeline-style updates (4.2+) you can write `db.orders.updateMany({}, [{ $set: { gst: { $multiply: ["$amount", 0.05] } } }])`.

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Compute fields on read without changing stored data (Mongoose)
app.get("/api/orders/with-gst", async (req, res) => {
  const rows = await Order.aggregate([
    { $set: { gst: { $round: [{ $multiply: ["$amount", 0.05] }, 2] } } }, // $round limits to 2 decimals
    { $project: { customer: 1, amount: 1, gst: 1 } }
  ]);
  res.json(rows);
});
// Mongoose virtuals are alternative for single docs; aggregation $set works for many docs in the DB.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `$project` just to add a field
```javascript
db.orders.aggregate([{ $project: { gst: { $multiply: ["$amount", 0.05] } } }]) // Wrong — loses all other fields
db.orders.aggregate([{ $set: { gst: { $multiply: ["$amount", 0.05] } } }])     // Right — keeps them
```

❌ Mistake 2: Referencing a field created in the same stage
```javascript
{ $set: { a: 1, b: "$a" } }   // Wrong — b refers to the ORIGINAL $a (missing), so b is not created at all (real output: only a: 1)
// Right: use two $set stages
```

❌ Mistake 3: Confusing the stage with the update operator
✅ Stage `$set` lives inside `aggregate([...])`; update `$set` lives in `{ $set: ... }` of `updateOne`. The pipeline stage never modifies stored data (use `$merge`/`$out` or an update).

---

## 🧠 Tricky Interview Question
Q: In the Basic example, why is `gst` 22.5 and not 23.0 even though `amount` is overwritten to 460 in the same stage?
Answer: Expressions in one stage evaluate against the input document, so `gst` uses the original 450 (450 x 0.05 = 22.5). To use the new amount, put the overwrite in a later stage.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `$addFields` and `$set`?
A1: None. `$set` is an alias introduced in 4.2.

Q2: `$addFields` vs `$project`?
A2: `$addFields` keeps everything and adds; `$project` defines the whole output shape.

Q3: How to remove fields?
A3: `$unset: ["a","b"]` or `$project` with 0.

Q4: Does `$addFields` change stored documents?
A4: No, it only changes pipeline output. Persist with `$merge`/`$out` or a pipeline update.

Q5: How to add to an array?
A5: `{ $set: { tags: { $concatArrays: ["$tags", ["new"]] } } }`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Adding computed fields while keeping the rest
- Multi-step calculations

❌ Avoid when:
- You need a strict output shape (use `$project`)
- You want to modify stored data (use update)

---

## 📊 Visual Diagram
```
 in : { customer, amount:450, items, ts }
        │  $set { gst: amount*0.05, "meta.src":"app" }
        ▼
 out: { customer, amount:450, items, ts, gst:22.5, meta:{src:"app"} }
        │  $unset ["items","ts"]
        ▼
 out: { customer, amount:450, gst:22.5, meta:{src:"app"} }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$addFields` | Add/overwrite fields | Fields जोड़ना/बदलना |
| `$set` | Alias of `$addFields` | `$addFields` का alias |
| `$unset` | Remove fields | Fields हटाना |
| Computed field | Value from expression | Expression से निकली value |
| Dotted path | `"a.b"` embedded field | Embedded field का path |
| Pipeline update | Update using stages | Stages वाला update |

---

## ⚡ 3-Line Summary
English:
1. `$addFields`/`$set` add or overwrite fields and keep the rest.
2. Expressions in one stage see the original doc; chain stages for dependencies.
3. Use `$unset` to remove; it never changes stored data by itself.

Hindi:
1. `$addFields`/`$set` fields जोड़ते या बदलते हैं और बाकी रखते हैं।
2. एक stage में expressions original doc देखते हैं; dependency हो तो stages chain करो।
3. हटाने के लिए `$unset`; ये अपने आप stored data नहीं बदलता।

---

## ➡️ Next Topic
**60. $facet — Multiple Pipelines** — running several sub-pipelines on the same input.
