# 73. Schema Design Patterns — Subset, Extended Reference, Polymorphic
# हिंदी में: Schema Design Patterns — Subset, Extended Reference, Polymorphic

---

## 🔵 Simple Definition (English)
- **Subset pattern**: keep only the most-used slice of a large related set (e.g. the 5 latest reviews) inside the parent, and the full set in a separate collection — a smaller document, smaller working set, faster hot reads.
- **Extended Reference pattern**: instead of a bare id, store the id **plus a few stable fields** of the referenced document (name, city) so the common read does not need a `$lookup`.
- **Polymorphic pattern**: documents of different shapes (UPI vs card vs COD payment) live in **one collection**, usually with a `type` discriminator field, so they can be queried together.

## 🔵 सरल परिभाषा (Hindi)
- **Subset pattern**: बड़े related set का सिर्फ़ सबसे ज़्यादा इस्तेमाल होने वाला हिस्सा (जैसे 5 latest reviews) parent के अंदर रखो और पूरा set अलग collection में — छोटा document, छोटा working set, तेज़ hot reads।
- **Extended Reference pattern**: सिर्फ़ id की जगह id **और referenced document के कुछ stable fields** (name, city) भी store करो ताकि आम read में `$lookup` न लगे।
- **Polymorphic pattern**: अलग-अलग shape के documents (UPI, card, COD payment) **एक ही collection** में रहते हैं, आमतौर पर `type` discriminator field के साथ, ताकि सबको साथ query किया जा सके।

---

## 🔴 Problem it Solves
- **Subset**: a product page needs 2 reviews, but the product document contains 40,000 reviews. Every read drags 10 MB into RAM; the working set stops fitting in memory.
- **Extended Reference**: an order list shows customer name and city; with only `customerId` every row needs a `$lookup` (or a second query).
- **Polymorphic**: a payments report needs all payment modes together, yet UPI has `upiId`, card has `last4` and `network`, COD has nothing. A table-per-type model needs `UNION`s; in MongoDB one collection keeps queries and indexes simple.

## 🔴 यह क्यों बना? (Hindi)
- **Subset**: Product page को 2 reviews चाहिए, पर product document में 40,000 reviews हैं। हर read 10 MB RAM में खींचता है; working set memory में नहीं समाता।
- **Extended Reference**: Order list में customer का नाम और city दिखते हैं; सिर्फ़ `customerId` हो तो हर row पर `$lookup` (या दूसरी query) चाहिए।
- **Polymorphic**: Payments report को सारे payment modes साथ चाहिए, पर UPI में `upiId`, card में `last4` और `network`, COD में कुछ नहीं। Type-wise tables में `UNION` लगता है; MongoDB में एक collection से queries और indexes सरल रहते हैं।

---

## 🟢 How it Works — Step by Step

**Subset**
Step 1 → Decide "hot" subset (latest 5 / top-rated 10) based on the page.
Step 2 → On each new review insert into `reviews` (full history) and `$push` to `product.recentReviews` with `$each` + `$slice: -N` (keeps only N).
Step 3 → Product page reads one doc; "see all reviews" paginates `reviews`.

**Extended Reference**
Step 1 → Choose fields that are read together and **rarely change** (name, city; not balance or stock).
Step 2 → Store `customer: { _id, name, city }` in the order.
Step 3 → When a copied field changes, run a background `updateMany` (or accept that the order is a snapshot - often correct for invoices).

**Polymorphic**
Step 1 → Common fields at top level (`amount`, `createdAt`, `type`), specific ones per type.
Step 2 → Index `type` (and compound with common fields).
Step 3 → Query across all types or filter one; add `$jsonSchema` with `oneOf` per type to keep it clean (note 75).

## 🟢 कैसे काम करता है? (Hindi)
**Subset**
Step 1 → Page के हिसाब से "hot" subset तय करो (latest 5 / top-rated 10)।
Step 2 → हर नए review को `reviews` (पूरा history) में insert करो और `product.recentReviews` में `$each` + `$slice: -N` के साथ `$push` करो (सिर्फ़ N बचते हैं)।
Step 3 → Product page एक doc पढ़ता है; "सारे reviews देखें" `reviews` को paginate करता है।

**Extended Reference**
Step 1 → ऐसे fields चुनो जो साथ पढ़े जाते हैं और **कम बदलते** हैं (name, city; balance या stock नहीं)।
Step 2 → Order में `customer: { _id, name, city }` रखो।
Step 3 → Copied field बदले तो background `updateMany` चलाओ (या order को snapshot मानो — invoices के लिए अक्सर यही सही है)।

**Polymorphic**
Step 1 → Common fields top level पर (`amount`, `createdAt`, `type`), specific fields type के हिसाब से।
Step 2 → `type` पर index (और common fields के साथ compound)।
Step 3 → सब types पर या एक type पर query; साफ़ रखने के लिए type-wise `oneOf` वाला `$jsonSchema` (note 75)।

---

## 🟡 Real World Example
**Flipkart product page (Subset)**: `products` embeds `topReviews` (5) and `ratingSummary`; the other 40,000 reviews live in `reviews`. **Order list (Extended Reference)**: each order stores `customer: { _id, name, city }` and `seller: { _id, shopName }` so "My Orders" renders from one collection. **Razorpay payments (Polymorphic)**: one `payments` collection with `type: "upi" | "card" | "netbanking" | "cod"`, each with its own extra fields, so settlement jobs aggregate every mode at once.

## 🟡 Real Example Hindi mein
**Flipkart product page (Subset)**: `products` में `topReviews` (5) और `ratingSummary` embedded हैं; बाकी 40,000 reviews `reviews` में। **Order list (Extended Reference)**: हर order में `customer: { _id, name, city }` और `seller: { _id, shopName }` होता है ताकि "My Orders" एक ही collection से बने। **Razorpay payments (Polymorphic)**: एक `payments` collection में `type: "upi" | "card" | "netbanking" | "cod"`, हर type के अपने extra fields, ताकि settlement jobs सारे modes एक साथ aggregate करें।

---

## 💻 Code Example — Basic

```javascript
// mongosh (MongoDB 8.0.4)
use t73

// ---------- SUBSET: full history in reviews, last 2 inside the product ----------
db.products.insertOne({ _id: "p1", name: "Phone", recentReviews: [ { u: "a", s: 5 }, { u: "b", s: 4 } ] })
db.reviews.insertMany([ { p: "p1", u: "a", s: 5 }, { p: "p1", u: "b", s: 4 }, { p: "p1", u: "c", s: 2 } ])

// New review arrives: keep the newest 2 in the parent (negative $slice keeps the LAST n)
db.products.updateOne(
  { _id: "p1" },
  { $push: { recentReviews: { $each: [ { u: "d", s: 5 } ], $slice: -2 } } }  // append, then trim to last 2
)
db.products.findOne()
// Output: { _id: 'p1', name: 'Phone', recentReviews: [ { u: 'b', s: 4 }, { u: 'd', s: 5 } ] }

// ---------- EXTENDED REFERENCE: copy stable customer fields into the order ----------
db.orders.insertOne({
  _id: "o1",
  customer: { _id: "u1", name: "Asha", city: "Pune" },   // id + the fields the list view needs
  items: [ { sku: "x", qty: 2 } ]
})
```

## 💻 Code Example — Advanced

```javascript
// mongosh — propagate a change to the copies, and the polymorphic collection

// ---------- EXTENDED REFERENCE: source changes -> update the copies ----------
db.users.insertOne({ _id: "u1", name: "Asha", city: "Pune", email: "a@x.com", addresses: [] })
db.users.updateOne({ _id: "u1" }, { $set: { name: "Asha K" } })                  // source of truth
db.orders.updateMany({ "customer._id": "u1" }, { $set: { "customer.name": "Asha K" } }) // fan-out to copies
db.orders.findOne()
// Output: { _id: 'o1', customer: { _id: 'u1', name: 'Asha K', city: 'Pune' }, items: [ { sku: 'x', qty: 2 } ] }
// Index { "customer._id": 1 } makes that updateMany cheap. Not atomic across docs (use a transaction if required).

// ---------- POLYMORPHIC: one collection, different shapes ----------
db.payments.insertMany([
  { type: "upi",  amount: 100, upiId: "a@ybl" },                        // UPI-specific field
  { type: "card", amount: 500, last4: "4242", network: "visa" },        // card-specific fields
  { type: "cod",  amount: 200 }                                         // nothing extra
])
db.payments.createIndex({ type: 1 })

// Cross-type report in ONE aggregation
db.payments.aggregate([
  { $group: { _id: "$type", total: { $sum: "$amount" } } },
  { $sort: { _id: 1 } }
])
// Output: [ { _id: 'card', total: 500 }, { _id: 'cod', total: 200 }, { _id: 'upi', total: 100 } ]

// Type-specific query
db.payments.find({ type: "card" }, { _id: 0 })
// Output: [ { type: 'card', amount: 500, last4: '4242', network: 'visa' } ]

// Optional guard: validator per type with oneOf (shown for syntax; see note 75 for running it)
// { $jsonSchema: { oneOf: [
//     { properties: { type: { enum: ["upi"] },  upiId: { bsonType: "string" } }, required: ["upiId"] },
//     { properties: { type: { enum: ["card"] }, last4: { bsonType: "string" } }, required: ["last4"] },
//     { properties: { type: { enum: ["cod"] } } } ] } }
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const mongoose = require('mongoose');
const express = require('express');
const { Schema } = mongoose;

// POLYMORPHIC with Mongoose discriminators: one collection 'payments', typed models per kind
const base = { discriminatorKey: 'type', collection: 'payments' };
const Payment = mongoose.model('Payment', new Schema({ amount: Number }, base));
const Upi  = Payment.discriminator('upi',  new Schema({ upiId: String }));
const Card = Payment.discriminator('card', new Schema({ last4: String, network: String }));

// EXTENDED REFERENCE in Mongoose: sub-document with _id + copied fields
const Order = mongoose.model('Order', new Schema({
  customer: { _id: { type: Schema.Types.ObjectId, index: true }, name: String, city: String },
  items: [{ sku: String, qty: Number }]
}));

const app = express();
app.use(express.json());

app.post('/payments/upi', async (req, res) => {
  const p = await Upi.create({ amount: req.body.amount, upiId: req.body.upiId }); // type:'upi' is added automatically
  res.status(201).json(p);
});
app.get('/payments', async (req, res) => {
  // Payment.find returns correctly-typed docs for each discriminator
  res.json(await Payment.find().lean());
});

// SUBSET in code: push + slice in one atomic update
const Product = mongoose.model('Product', new Schema({ name: String, recentReviews: [{ u: String, s: Number }] }));
app.post('/products/:id/reviews', async (req, res) => {
  await Product.updateOne({ _id: req.params.id },
    { $push: { recentReviews: { $each: [{ u: req.body.u, s: req.body.s }], $slice: -5 } } });
  // ...also insert into the full Review collection (consider a transaction if both must succeed)
  res.sendStatus(201);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Copying volatile fields in Extended Reference
```javascript
// Wrong — stock/balance changes constantly; copies are always stale and fan-out writes explode
order.product = { _id, name, stockLeft: 12 }
// Right — copy only stable fields (name, brand) or a point-in-time snapshot you intend to freeze (price at order)
order.product = { _id, name: "Phone" }
```

❌ Mistake 2: Subset `$push` without `$slice` (the "subset" quietly grows forever)
```javascript
// Wrong
{ $push: { recentReviews: review } }
// Right
{ $push: { recentReviews: { $each: [review], $slice: -5 } } }
```
✅ Also: polymorphic docs without a `type` field or validation, making queries guess the shape.

---

## 🧠 Tricky Interview Question

`$push: { recentReviews: { $each: [x], $slice: 2 } }` versus `$slice: -2` — which keeps the newest items?

Answer: A **positive** `$slice: 2` keeps the **first** 2 elements of the array after the push, so the new item `x` (appended at the end) would be dropped as soon as the array has 2 items already — the array freezes on the oldest reviews. **Negative** `-2` keeps the **last** 2, i.e. the newest. In our test, with `[a, b]` plus `d` and `$slice: -2`, the result was `[b, d]`. If you want newest-first order, add `$position: 0` with a positive `$slice`.

---

## ⚫ Interview Questions + Answers

Q1: What's the trade-off of the Subset pattern?
A1: Reads of the hot data get faster and the working set shrinks, but each write must update two places (the parent subset and the full collection) and there is duplication. Use transactions (or accept eventual consistency) if both must agree.

Q2: How is Extended Reference different from plain referencing?
A2: Plain referencing stores only the id and requires a join. Extended Reference stores the id plus selected fields from the target, eliminating the join for the common case at the cost of duplication and fan-out updates.

Q3: When is an Extended Reference copy *correct* never to update?
A3: When it is a historical snapshot: invoices, orders (price at purchase, shipping address at that time) must keep what was true then. No fan-out needed.

Q4: How do you do polymorphism safely?
A4: A `type` discriminator field, indexes on it, `$jsonSchema` `oneOf` validation (or Mongoose discriminators), and application code branching on `type`.

Q5: Why isn't polymorphic collection a problem in MongoDB but awkward in SQL?
A5: Documents within a collection can have different fields, so related variants share one collection and index set; SQL needs nullable columns, a table-per-type or EAV.

---

## 🔷 When to Use + When Not to Use
✅ Use:
- Subset: large related sets where only a few items are shown with the parent
- Extended Reference: list views / frequently joined data with stable attributes
- Polymorphic: similar entities with some type-specific fields, queried together

❌ Avoid:
- Subset when you don't know what the "hot" subset is
- Extended Reference for frequently changing fields
- Polymorphic when types have almost nothing in common (use separate collections)

---

## 📊 Visual Diagram
```
SUBSET                         EXTENDED REFERENCE            POLYMORPHIC
──────                         ──────────────────            ───────────
products                       orders                        payments
 { recentReviews:[r4,r5] }      { customer:{_id,name,city},   {type:'upi', upiId}
reviews (all 40,000)              items:[...] }               {type:'card', last4}
 { p, u, s } x 40000           users (source of truth)        {type:'cod'}
                                { _id, name, city, email... } one collection, one index on type
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Subset pattern | Keep hot slice inside parent | Hot हिस्सा parent में |
| Extended reference | id + copied stable fields | id + copy किए stable fields |
| Polymorphic pattern | Mixed shapes in one collection | एक collection में अलग shapes |
| Discriminator | Field naming the document type | Type बताने वाला field |
| `$slice` | Limit array size in `$push` | `$push` में array size सीमा |
| Fan-out | Updating all copies of a value | सारी copies update करना |
| Snapshot | Value frozen at a point in time | किसी समय का frozen value |

---

## ⚡ 3-Line Summary
English:
1. Subset keeps the hot slice inside the parent; Extended Reference copies stable fields beside the id; Polymorphic stores variants in one collection with a `type`.
2. All three trade write complexity and duplication for faster, simpler reads.
3. Use `$push` with `$each` + negative `$slice`, copy only stable fields, and validate each type's shape.

Hindi:
1. Subset hot हिस्सा parent में रखता है; Extended Reference id के साथ stable fields copy करता है; Polymorphic variants को `type` के साथ एक collection में रखता है।
2. तीनों write की जटिलता और duplication के बदले तेज़, सरल reads देते हैं।
3. `$push` में `$each` + negative `$slice` लगाओ, सिर्फ़ stable fields copy करो, और हर type की shape validate करो।

---

## ➡️ Next Topic
**74. Schema Versioning + Migrations** — evolve documents safely with `schemaVersion`, lazy and bulk migrations.
