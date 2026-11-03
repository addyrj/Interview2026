# 58. $lookup — Joins in MongoDB
# हिंदी में: $lookup — MongoDB में Joins

---

## 🔵 Simple Definition (English)
**`$lookup`** performs a left outer join with another collection in the same database. For each input document it finds matching documents in the "from" collection and adds them as an array field. It comes in two forms: the simple **equality** form (`localField`/`foreignField`) and the **pipeline** form (`let` + `pipeline`) for complex conditions.

## 🔵 सरल परिभाषा (Hindi)
**`$lookup`** उसी database की दूसरी collection के साथ left outer join करता है। हर input document के लिए "from" collection में matching documents ढूँढकर array field के रूप में जोड़ देता है। इसके दो रूप हैं: simple **equality** form (`localField`/`foreignField`) और जटिल conditions के लिए **pipeline** form (`let` + `pipeline`)।

---

## 🔴 Problem it Solves
Data is sometimes referenced rather than embedded (orders reference customers). To show an order with the customer's tier you need data from two collections. Doing two queries in Node.js costs two round trips and N+1 problems. `$lookup` joins inside the database in one call.

## 🔴 यह क्यों बना? (Hindi)
कभी data embed नहीं बल्कि reference होता है (orders customers को refer करते हैं)। Order के साथ customer का tier दिखाने के लिए दो collections का data चाहिए। Node.js में दो queries करने से दो round trips और N+1 problem होती है। `$lookup` एक call में database के अंदर join कर देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `from`: the other collection (must be unsharded in older versions; sharded allowed from 5.1).
Step 2 → `localField`: field in the input doc. `foreignField`: field in `from` to compare against.
Step 3 → Matches are placed in the `as` array. No match = empty array (left join behaviour).
Step 4 → To get an inner join, follow with `$unwind` (drops empties) or `$match` on non-empty.
Step 5 → Pipeline form: `let` defines variables from the input doc; `pipeline` runs on `from` and uses `$expr` with `$$var` to compare.
Step 6 → Index `foreignField` (e.g. `_id` is already indexed), or the join does a collection scan per input doc.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `from`: दूसरी collection (पुराने versions में unsharded होनी चाहिए; 5.1 से sharded भी चलती है)।
Step 2 → `localField`: input doc का field। `foreignField`: `from` का वह field जिससे compare हो।
Step 3 → Matches `as` array में आते हैं। कोई match नहीं = खाली array (left join जैसा)।
Step 4 → Inner join चाहिए तो `$unwind` (खाली हटाता है) या non-empty पर `$match` लगाओ।
Step 5 → Pipeline form: `let` input doc से variables बनाता है; `pipeline` `from` पर चलता है और `$expr` के साथ `$$var` से compare करता है।
Step 6 → `foreignField` पर index बनाओ (`_id` पर पहले से है), वरना हर input doc पर collection scan होगा।

---

## 🟡 Real World Example
**Swiggy's order detail API** has `orders` with `restaurantId` and `userId`. One pipeline joins `restaurants` (name, area) and `users` (tier) so the backend gets one enriched response. Joins are used for reporting; for hot paths, Swiggy-style systems often embed a snapshot (restaurant name) in the order to avoid the join.

## 🟡 Real Example Hindi mein
**Swiggy की order detail API** में `orders` के पास `restaurantId` और `userId` हैं। एक pipeline `restaurants` (name, area) और `users` (tier) join करती है और backend को एक enriched response मिलता है। Reporting में joins चलते हैं; hot paths में अक्सर order में restaurant name की snapshot embed कर देते हैं ताकि join न लगे।

---

## 💻 Code Example — Basic

```javascript
// mongosh, MongoDB 8.0.4. customers: {_id:"Aarav",tier:"gold"}, {_id:"Diya",tier:"silver"}, {_id:"Kabir",tier:"gold"}
db.orders.aggregate([
  { $match: { _id: { $in: [1, 6] } } },            // order 1 (Aarav) and order 6 (Meera, no customer doc)
  { $lookup: {
      from: "customers",                           // collection to join
      localField: "customer",                      // orders.customer
      foreignField: "_id",                         // customers._id
      as: "cust"                                   // output array field
  } },
  { $project: { customer: 1, cust: 1 } }
])
// Output (real):
// { _id: 1, customer: 'Aarav', cust: [ { _id: 'Aarav', tier: 'gold' } ] }
// { _id: 6, customer: 'Meera', cust: [] }         // left join: kept with empty array
```

## 💻 Code Example — Advanced

```javascript
// Pipeline form + inner join via $unwind
db.orders.aggregate([
  { $match: { _id: { $in: [1, 2] } } },
  { $lookup: {
      from: "customers",
      let: { c: "$customer" },                     // variable from the order
      pipeline: [
        { $match: { $expr: { $eq: ["$_id", "$$c"] } } }, // $$c = variable, $_id = field of customers
        { $project: { tier: 1 } }                  // return only what we need
      ],
      as: "cust"
  } },
  { $unwind: "$cust" },                            // array -> object (drops orders with no customer)
  { $project: { customer: 1, tier: "$cust.tier" } }
])
// Output (real):
// { _id: 1, customer: 'Aarav', tier: 'gold' }
// { _id: 2, customer: 'Diya',  tier: 'silver' }
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// GET /api/orders/:id/with-tier (Mongoose, tested on mongod 8.0.4)
app.get("/api/orders/:id/with-tier", async (req, res) => {
  const rows = await Order.aggregate([
    { $match: { _id: Number(req.params.id) } },    // sample _id is a number; use new mongoose.Types.ObjectId(id) for ObjectIds
    { $lookup: { from: "customers", localField: "customer", foreignField: "_id", as: "c" } },
    { $unwind: "$c" },
    { $project: { customer: 1, tier: "$c.tier" } }
  ]);
  if (!rows.length) return res.status(404).json({ error: "Not found" });
  res.json(rows[0]);                               // {"_id":1,"customer":"Aarav","tier":"gold"}
});
```
Mongoose `populate()` is NOT `$lookup`: populate runs a second query in Node.js. `$lookup` joins server-side.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting a single object
```javascript
// Wrong — as: "cust" is ALWAYS an array
doc.cust.tier            // undefined
// Right
doc.cust[0]?.tier        // or add { $unwind: "$cust" }
```

❌ Mistake 2: Type mismatch between fields
✅ A string `"5"` never equals number `5` or an ObjectId. Convert (`$toObjectId`) or store consistent types.

❌ Mistake 3: Joining a huge unindexed foreign field
✅ Index `foreignField`. Also `$match` before `$lookup` to cut the input.

---

## 🧠 Tricky Interview Question
Q: `$lookup` then `$unwind` on `cust`. Order 6 had no customer. Is it in the output?
Answer: No. `$lookup` keeps it with `cust: []`, but `$unwind` drops empty arrays by default, turning the left join into an inner join. Add `preserveNullAndEmptyArrays: true` to keep it.

---

## ⚫ Interview Questions + Answers

Q1: Is `$lookup` a left or inner join?
A1: Left outer. Unmatched input documents stay with an empty array.

Q2: When to use the pipeline form?
A2: For non-equality conditions, multiple join keys, or filtering/projecting the joined side before it is attached.

Q3: Does `$lookup` scale?
A3: With an index on `foreignField` it is fine for moderate use. It is not a replacement for good schema design; embed data that is read together.

Q4: `$lookup` vs Mongoose `populate`?
A4: `$lookup` is one server-side aggregation; `populate` issues an extra query and merges in Node.

Q5: Can you join across databases?
A5: No, `from` must be in the same database (cross-database needs app code).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reports/analytics that need data from two collections
- Occasional enrichment where embedding is unsuitable

❌ Avoid when:
- A hot path needs it on every request (embed instead)
- You chain many lookups (design smell)

---

## 📊 Visual Diagram
```
 orders                         customers
 ┌────────────────────┐         ┌───────────────────┐
 │ _id:1 customer:Aarav│──────► │ _id:Aarav tier:gold│
 │ _id:6 customer:Meera│──X     └───────────────────┘
 └────────────────────┘
        │ $lookup as:"cust"
        ▼
 { _id:1, cust:[{tier:gold}] }
 { _id:6, cust:[]            }   <- left join keeps it
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$lookup` | Join with another collection | दूसरी collection से join |
| `localField` / `foreignField` | Join keys | Join की keys |
| `as` | Output array name | Output array का नाम |
| `let` | Variables for pipeline form | Pipeline form के variables |
| Left outer join | Keep all left docs | बाएँ के सारे docs रखना |
| `populate` | Mongoose app-side join | Mongoose का app-side join |

---

## ⚡ 3-Line Summary
English:
1. `$lookup` is a left outer join that returns matches as an array.
2. Add `$unwind` for an object / inner join; index the foreign field.
3. Prefer embedding on hot paths; use `$lookup` for reports.

Hindi:
1. `$lookup` left outer join है जो matches को array में देता है।
2. Object / inner join के लिए `$unwind` लगाओ; foreign field पर index बनाओ।
3. Hot paths में embed करो; reports के लिए `$lookup` इस्तेमाल करो।

---

## ➡️ Next Topic
**59. $addFields and $set** — adding or overwriting computed fields.
