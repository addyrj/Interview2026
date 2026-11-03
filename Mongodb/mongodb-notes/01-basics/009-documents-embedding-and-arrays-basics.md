# 9. Documents — embedding and arrays basics
# हिंदी में: Documents — Embedding और Arrays की बुनियाद

---

## 🔵 Simple Definition (English)
A **document** is a BSON object of field-value pairs. Values may be scalars, **embedded documents** (objects inside objects) or **arrays** (of scalars or objects). **Embedding** means storing related data inside the parent document so it can be read in one query. Maximum document size is **16 MB**.

## 🔵 सरल परिभाषा (Hindi)
**Document** field-value pairs वाला BSON object है। Values scalar, **embedded documents** (object के अंदर object) या **arrays** (scalars या objects की) हो सकती हैं। **Embedding** का मतलब related data को parent document के अंदर रखना ताकि एक ही query में पढ़ा जा सके। Document का अधिकतम size **16 MB** है।

---

## 🔴 Problem it Solves
Relational models split an order into `orders`, `order_items`, `addresses` and need JOINs to reassemble it. Documents let you keep data that is read together, stored together: one read, one atomic write (single-document operations are atomic), no joins.

## 🔴 यह क्यों बना? (Hindi)
Relational model में order को `orders`, `order_items`, `addresses` में बाँटना पड़ता है और वापस जोड़ने के लिए JOINs चाहिए। Documents में जो data साथ पढ़ा जाता है उसे साथ रखते हैं: एक read, एक atomic write (single-document operations atomic होते हैं), कोई join नहीं।

---

## 🟢 How it Works — Step by Step

Step 1 → Design around queries: what do you read together? Put it in one document.
Step 2 → Use **embedded object** for one-to-one / one-to-few (`address: { city, pin }`).
Step 3 → Use **array** for lists (`tags: [...]`, `items: [{sku, qty}]`).
Step 4 → Query nested fields with **dot notation** (`"address.city"`) – must be in quotes.
Step 5 → Query arrays: `{ tags: "a" }` matches if any element equals "a"; use `$elemMatch` when multiple conditions must hit the same array element.
Step 6 → Avoid unbounded arrays (comments forever) – document would approach the 16 MB limit.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Queries के आधार पर design करो: साथ क्या पढ़ा जाता है? उसे एक document में रखो।
Step 2 → One-to-one / one-to-few के लिए **embedded object** (`address: { city, pin }`)।
Step 3 → Lists के लिए **array** (`tags: [...]`, `items: [{sku, qty}]`)।
Step 4 → Nested fields **dot notation** से query करो (`"address.city"`) – quotes ज़रूरी हैं।
Step 5 → Arrays: `{ tags: "a" }` तब match होता है जब कोई भी element "a" हो; एक ही element पर कई conditions चाहिए तो `$elemMatch`।
Step 6 → Unbounded arrays (हमेशा बढ़ते comments) से बचो – document 16 MB limit के पास पहुँच जाएगा।

---

## 🟡 Real World Example
A Zomato order document embeds the delivery address, the list of items (each with name, qty, price) and a `statusHistory` array. The order-tracking screen fetches everything with one `findOne({ _id })`. But restaurant reviews (could be millions) are NOT embedded in the restaurant document – they live in a separate `reviews` collection referencing `restaurantId`.

## 🟡 Real Example Hindi mein
Zomato का order document delivery address, items की list (name, qty, price के साथ) और `statusHistory` array embed करता है। Order-tracking screen एक `findOne({ _id })` से सब ले आती है। पर restaurant reviews (लाखों हो सकते हैं) restaurant document में embed नहीं होते – वे अलग `reviews` collection में `restaurantId` reference के साथ रहते हैं।

---

## 💻 Code Example — Basic

```javascript
// Run on mongod 8.0.4 in database "mh"
db.p.insertOne({
  n: "Aman",                      // scalar string
  tags: ["a", "b"],               // array of scalars
  addr: { city: "Pune" }          // embedded document
})

db.p.find({ tags: "a" }, { _id: 0 })
// Output: [ { n: 'Aman', tags: [ 'a', 'b' ], addr: { city: 'Pune' } } ]  (array contains "a")

db.p.find({ "addr.city": "Pune" }, { _id: 0 })
// Output: same document (dot notation reaches into the embedded object)
```

## 💻 Code Example — Advanced

```javascript
db.orders.insertOne({
  _id: 1,
  items: [
    { sku: "A1", qty: 1 },        // array of embedded documents
    { sku: "B2", qty: 5 }
  ]
})

// WRONG expectation: both conditions can match DIFFERENT elements
db.orders.find({ "items.sku": "A1", "items.qty": 5 }).toArray().length
// Output: 1  <- matches! sku A1 is in element 0 and qty 5 is in element 1

// RIGHT: $elemMatch forces both conditions on the SAME element
db.orders.find({ items: { $elemMatch: { sku: "A1", qty: 5 } } }).toArray().length
// Output: 0

// Positional access by index
db.orders.find({ "items.0.sku": "A1" }).toArray().length   // Output: 1
```
(All outputs in both examples were executed on mongod 8.0.4.)

---

## 🟠 Express.js / Mongoose Integration

```javascript
const mongoose = require('mongoose');
// Sub-schemas become embedded documents; [Type] becomes an array
const orderSchema = new mongoose.Schema({
  items: [{ sku: String, qty: Number }],          // array of embedded subdocuments (each gets its own _id!)
  address: { city: String, pin: String },         // nested object (no extra _id)
  tags: [String]                                  // array of strings
});
const Order = mongoose.model('Order', orderSchema);

app.get('/orders/:id', async (req, res) => {
  const o = await Order.findById(req.params.id);  // one read returns everything embedded
  res.json(o);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting quotes around dotted paths
```javascript
db.p.find({ addr.city: "Pune" })     // Wrong: syntax error
db.p.find({ "addr.city": "Pune" })   // Right
```

❌ Mistake 2: Matching an embedded document by whole-object equality
```javascript
db.p.find({ addr: { city: "Pune" } })           // matches only if addr is EXACTLY {city:"Pune"}, same field order
db.p.find({ "addr.city": "Pune" })              // Right: flexible, matches extra fields too
```

❌ Mistake 3: Unbounded arrays
✅ Correct: Cap with `$push` + `$slice`, or move growing data to its own collection.

---

## 🧠 Tricky Interview Question
Q: `{ "items.sku": "A1", "items.qty": 5 }` returns an order whose A1 item has qty 1. Why?
Answer: Without `$elemMatch`, each condition is checked independently across the array, so different elements can satisfy each. Use `$elemMatch` to require one element to satisfy all conditions.

---

## ⚫ Interview Questions + Answers

Q1: What is the max BSON document size?
A1: 16 MB. Use GridFS for larger files and reference documents for unbounded data.

Q2: Embed or reference?
A2: Embed for data read together, one-to-few, and bounded size; reference for many-to-many, unbounded growth, or data updated independently.

Q3: Is a single-document update with nested arrays atomic?
A3: Yes, any write to one document is atomic, including its embedded parts.

Q4: How do you query array contains?
A4: `{ tags: "a" }`; for multiple values use `$all` or `$in`.

Q5: Does field order matter in an embedded doc equality match?
A5: Yes. `{a:1,b:2}` is not equal to `{b:2,a:1}` in exact subdocument matching.

---

## 🔷 When to Use + When Not to Use
✅ Embed when:
- Data is read together and bounded (address, line items)

❌ Avoid embedding when:
- Array grows without limit, or the child is shared by many parents

---

## 📊 Visual Diagram
```
order document
{
  _id: 1,
  user: "Aman",
  address: { city: "Pune", pin: "411001" },   <- embedded object
  items: [                                   <- array
    { sku: "A1", qty: 1 },                    <- embedded doc in array
    { sku: "B2", qty: 5 }
  ]
}
Query: "address.city"  |  "items.sku"  |  items: {$elemMatch:{...}}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedded document | Object inside a document | Document के अंदर object |
| Array | Ordered list of values | Values की ordered list |
| Dot notation | `"a.b"` path access | Nested field का path |
| $elemMatch | Same-element array match | एक ही element पर match |
| 16 MB limit | Max document size | Document का अधिकतम size |

---

## ⚡ 3-Line Summary
English:
1. Documents hold scalars, embedded objects and arrays; max 16 MB.
2. Use dot notation for nested paths and `$elemMatch` for same-element array conditions.
3. Embed bounded, co-read data; reference unbounded or shared data.

Hindi:
1. Documents में scalars, embedded objects और arrays होते हैं; अधिकतम 16 MB।
2. Nested paths के लिए dot notation और same-element array conditions के लिए `$elemMatch` इस्तेमाल करो।
3. Bounded, साथ-पढ़े जाने वाला data embed करो; unbounded या shared data reference करो।

---

## ➡️ Next Topic
**10. _id field and uniqueness** — The mandatory primary key of every document.
