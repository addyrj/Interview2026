# 33. Querying Nested Documents + Dot Notation
# हिंदी में: Nested Documents को Query करना + Dot Notation

---

## 🔵 Simple Definition (English)
A **nested (embedded) document** is an object stored inside another document, e.g. `address: { city: "Pune", pin: 411001 }`. **Dot notation** (`"address.city"`) reaches into it to query, project or update **one inner field**. Querying with the whole embedded object (`{ address: { city: "Pune" } }`) is an **exact match** — same fields, same values, **same order** — which is a classic trap. Dotted paths must be wrapped in quotes.

## 🔵 सरल परिभाषा (Hindi)
**Nested (embedded) document** एक object होता है जो दूसरे document के अंदर रखा हो, जैसे `address: { city: "Pune", pin: 411001 }`। **Dot notation** (`"address.city"`) अंदर की **एक field** तक पहुँचकर query, projection या update करने देता है। पूरे embedded object से query (`{ address: { city: "Pune" } }`) **exact match** होती है — वही fields, वही values, **वही क्रम** — यह एक classic जाल है। Dotted paths को quotes में लिखना ज़रूरी है।

---

## 🔴 Problem it Solves
Embedding related data (address inside customer, geo inside address) avoids joins, but then you need a way to filter on inner fields: "customers in Pune", "addresses with latitude > 18". Without dot notation you would have to match the entire sub-object, which breaks the moment a new inner field (`landmark`) appears or the key order differs. Dot notation targets exactly the field you care about and is index-friendly (`createIndex({ "address.city": 1 })`).

## 🔴 यह क्यों बना? (Hindi)
Related data को embed करने (customer के अंदर address, address के अंदर geo) से joins बचते हैं, पर फिर inner fields पर filter करने का तरीका चाहिए: "Pune के customers", "latitude > 18 वाले addresses"। Dot notation के बिना पूरा sub-object match करना पड़ता, जो तब टूट जाता है जब कोई नई inner field (`landmark`) आए या key order अलग हो। Dot notation ठीक वही field target करता है जो चाहिए और index-friendly है (`createIndex({ "address.city": 1 })`)।

---

## 🟢 How it Works — Step by Step

Step 1 → Write the path from the outer field to the inner one, separated by dots: `"address.geo.lat"`.
Step 2 → Quote it: `{ "address.city": "Pune" }`. Without quotes JavaScript would read `address.city` as property access, not a key.
Step 3 → Normal operators work on the inner field: `{ "address.geo.lat": { $gt: 18 } }`, `$in`, `$exists`, `$regex`.
Step 4 → **Whole-object equality** `{ address: { city: "Pune", pin: 411001 } }` compares the entire embedded document: every field, value **and key order** must be identical. Extra fields or different order mean no match.
Step 5 → **Missing parents**: if `address` does not exist, `{ "address.city": ... }` simply doesn't match; `{ "address.city": { $exists: false } }` **does** match such documents.
Step 6 → **Projection** uses dot notation too (`{ "address.city": 1 }`), and **updates** do as well: `$set: { "address.pin": 110001 }` changes only `pin`, and creates `address` if absent.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → बाहरी field से अंदर वाली field तक path dots से लिखो: `"address.geo.lat"`।
Step 2 → उसे quotes में लिखो: `{ "address.city": "Pune" }`। Quotes के बिना JavaScript `address.city` को property access समझेगा, key नहीं।
Step 3 → Inner field पर सामान्य operators चलते हैं: `{ "address.geo.lat": { $gt: 18 } }`, `$in`, `$exists`, `$regex`।
Step 4 → **पूरे object की equality** `{ address: { city: "Pune", pin: 411001 } }` पूरे embedded document की तुलना करती है: हर field, value और **key का क्रम** एकदम वही होना चाहिए। Extra field या अलग क्रम हो तो match नहीं।
Step 5 → **Missing parent**: `address` न हो तो `{ "address.city": ... }` match नहीं करता; `{ "address.city": { $exists: false } }` ऐसे documents से **match करता है**।
Step 6 → **Projection** भी dot notation इस्तेमाल करता है (`{ "address.city": 1 }`), और **updates** भी: `$set: { "address.pin": 110001 }` सिर्फ `pin` बदलता है, और `address` न हो तो उसे बना देता है।

---

## 🟡 Real World Example
**Swiggy customer collection**: `{ name, address: { city, pin, geo: { lat, lng } } }`. Ops asks "all Pune customers" -> `{ "address.city": "Pune" }`. Delivery planning needs customers north of latitude 18 -> `{ "address.geo.lat": { $gt: 18 } }`. A customer updates just the pincode -> `$set: { "address.pin": 110001 }`, leaving city and geo untouched.

## 🟡 Real Example Hindi mein
**Swiggy customer collection**: `{ name, address: { city, pin, geo: { lat, lng } } }`। Ops पूछती है "Pune के सभी customers" -> `{ "address.city": "Pune" }`। Delivery planning को latitude 18 से ऊपर के customers चाहिए -> `{ "address.geo.lat": { $gt: 18 } }`। Customer सिर्फ pincode बदलता है -> `$set: { "address.pin": 110001 }`, city और geo अछूते रहते हैं।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4, mongosh.

```javascript
use swiggy_nested_demo                             // switch database
db.dropDatabase()                                  // clean start
db.c.insertMany([                                  // four customers
  { _id: 1, name: "Asha", address: { city: "Pune",  pin: 411001, geo: { lat: 18.5, lng: 73.8 } } },
  { _id: 2, name: "Ravi", address: { pin: 411001, city: "Pune" } },   // same data, DIFFERENT key order
  { _id: 3, name: "Neha", address: { city: "Delhi" } },
  { _id: 4, name: "Om" }                                              // no address at all
])
const ids = q => print(JSON.stringify(db.c.find(q).toArray().map(x => x._id)))

// ---- dot notation: reach one inner field ----
ids({ "address.city": "Pune" })                    // [1,2]    key order irrelevant
ids({ "address.geo.lat": { $gt: 18 } })            // [1]      two levels deep
ids({ "address.city": { $in: ["Pune","Delhi"] } }) // [1,2,3]

// ---- whole-object equality: exact, order-sensitive ----
ids({ address: { city: "Pune", pin: 411001 } })    // []   doc 1 has an extra "geo"; doc 2 has pin first
ids({ address: { pin: 411001, city: "Pune" } })    // [2]  only doc 2 stores keys in exactly this order
ids({ address: { city: "Pune" } })                 // []   extra fields => not equal

// ---- missing fields ----
ids({ "address.city": { $exists: false } })        // [4]     no address => no address.city
ids({ address: { $exists: false } })               // [4]
ids({ "address.geo": { $exists: true } })          // [1]

// ---- projection with dot notation ----
db.c.find({ _id: 1 }, { "address.city": 1, _id: 0 }).toArray()
// Output: [ { address: { city: 'Pune' } } ]
db.c.find({ _id: 1 }, { address: { city: 1 } }).toArray()      // nested-object form also works
// Output: [ { _id: 1, address: { city: 'Pune' } } ]

// ---- update with dot notation ----
db.c.updateOne({ _id: 3 }, { $set: { "address.pin": 110001 } })   // adds pin, keeps city
db.c.findOne({ _id: 3 }).address                                   // { city: 'Delhi', pin: 110001 }
db.c.updateOne({ _id: 4 }, { $set: { "address.city": "Goa" } })   // creates the address object
db.c.findOne({ _id: 4 }).address                                   // { city: 'Goa' }
```

## 💻 Code Example — Advanced

```javascript
// Index on a nested field + verifying it is used (mongosh)
db.c.createIndex({ "address.city": 1, "address.pin": 1 })        // compound index on two inner fields
db.c.find({ "address.city": "Pune", "address.pin": 411001 })
  .explain().queryPlanner.winningPlan.inputStage.stage           // 'IXSCAN' (index is used for dotted paths)

// Dynamic dotted filter built from user filters (Node.js driver v6)
function buildFilter(q) {
  const f = {};                                                   // start empty
  if (q.city) f['address.city'] = q.city;                         // dotted key as a plain string
  if (q.pin) f['address.pin'] = Number(q.pin);                    // cast numbers explicitly
  if (q.minLat) f['address.geo.lat'] = { $gte: Number(q.minLat) };// operator on a nested field
  return f;
}

// Security: never spread raw user JSON into a filter (operator injection)
// const f = { 'address.city': req.query.city };  // if city = { $ne: null } this returns everyone!
const safe = { 'address.city': String(req.query.city) };         // force it to a string
```

```javascript
// Atomic nested update/unset with the Node.js driver
await db.collection('c').updateOne(
  { _id: 1 },
  {
    $set:   { 'address.geo.lat': 18.52 },     // change a deep value
    $unset: { 'address.pin': '' }             // remove just one inner field
  }
);
```

---

## 🟠 Express.js / Mongoose Integration

Tested against MongoDB 8.0.4, Express 5, Mongoose 8.

```javascript
const express = require('express');
const mongoose = require('mongoose');
const Order = mongoose.model('Order', new mongoose.Schema({
  customer: String,
  address: { city: String, pin: Number }          // nested path (not a separate sub-schema)
}));
const app = express();

// GET /orders?city=Pune
app.get('/orders', async (req, res) => {
  const f = {};
  if (req.query.city) f['address.city'] = String(req.query.city); // dot notation in Mongoose filters
  const rows = await Order.find(f).select('customer address.city -_id').lean(); // projection with dots
  res.json(rows);
});
// Real run -> [{"customer":"Aman K","address":{"city":"Pune"}}]
```
Mongoose nested paths (plain object in the schema) are stored exactly like MongoDB embedded documents; use a **sub-schema** (`new Schema({...})`) when you need its own validation, defaults and `_id`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Matching the whole sub-object when you want one field
```javascript
db.c.find({ address: { city: "Pune" } })        // Wrong: [] — exact match fails when other fields exist
db.c.find({ "address.city": "Pune" })           // Right: [1,2]
```

❌ Mistake 2: Forgetting the quotes
```javascript
db.c.find({ address.city: "Pune" })             // Wrong: SyntaxError
db.c.find({ "address.city": "Pune" })           // Right
```

❌ Mistake 3: Replacing the sub-object on update
```javascript
db.c.updateOne({ _id: 3 }, { $set: { address: { pin: 110001 } } })   // Wrong: city is LOST
db.c.updateOne({ _id: 3 }, { $set: { "address.pin": 110001 } })      // Right: city stays
```

---

## 🧠 Tricky Interview Question

```javascript
db.c.find({ address: { city: "Pune", pin: 411001 } })
```
Two Pune customers have the same city and pin. Do both match?

Answer: **Neither** in our data. Document 1 has an extra `geo` field, and document 2 stores `pin` before `city`. Whole-subdocument queries are **exact, order-sensitive matches** (real output `[]`; `{ pin: 411001, city: "Pune" }` returns only doc 2). The robust form is `{ "address.city": "Pune", "address.pin": 411001 }`, which returns `[1,2]`.

---

## ⚫ Interview Questions + Answers

Q1: What is dot notation and where can it be used?
A1: A way to address inner fields (`"a.b.c"`) and array positions (`"arr.0"`) in queries, projections, updates, index definitions and aggregation field paths.

Q2: Why does `{ address: { city: "Pune" } }` fail on documents with more address fields?
A2: Querying with an embedded document is an exact equality match on the whole sub-document: all fields, values and field order must be the same.

Q3: Does `$set: { "address.city": "Goa" }` work when `address` is missing?
A3: Yes, MongoDB creates the `address` object with that field.

Q4: How do you index a nested field?
A4: `createIndex({ "address.city": 1 })`. Compound indexes can mix top-level and nested fields; `explain()` shows `IXSCAN`.

Q5: What is the risk of putting `req.query.city` directly into the filter?
A5: Operator (NoSQL) injection — `?city[$ne]=x` can become `{ $ne: "x" }` and return everything. Cast to string or validate with a schema.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data is always read together (customer + address), one-to-one or one-to-few.
- You filter or sort on inner fields.
- You want partial updates of an embedded object.

❌ Avoid when:
- The inner data is large, unbounded or shared by many parents — reference it instead.
- You query by whole-object equality (fragile) — use dotted fields.
- Field names themselves contain dots or start with `$` — they confuse dot notation.

---

## 📊 Visual Diagram
```
 { _id: 1,
   name: "Asha",
   address: {                        "address.city"      -> "Pune"
      city: "Pune",                  "address.geo.lat"   -> 18.5
      pin: 411001,
      geo: { lat: 18.5, lng: 73.8 }
   } }

 find({ address: {city:"Pune"} })           exact sub-doc  ✖  (extra fields)
 find({ "address.city": "Pune" })           one inner field ✔
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedded document | Object inside a document | Document के अंदर का object |
| Dot notation | `"a.b"` path to inner field | Inner field तक का `"a.b"` path |
| Exact match | Whole sub-document equality, order sensitive | पूरे sub-document की क्रम-संवेदी equality |
| Projection | Choose which fields to return | कौन-सी fields लौटें |
| Operator injection | Malicious operator objects in input | Input में छुपे malicious operators |
| Sub-schema | Mongoose schema for nested object | Nested object के लिए Mongoose schema |

---

## ⚡ 3-Line Summary
English:
1. Use dot notation in quotes (`"address.city"`) to query, project, update and index inner fields.
2. Querying with a whole sub-object is an exact, order-sensitive match — usually not what you want.
3. `$set` with a dotted path changes one inner field; setting the parent replaces everything inside it.

Hindi:
1. Inner fields को query, project, update और index करने के लिए quotes में dot notation (`"address.city"`) इस्तेमाल करो।
2. पूरे sub-object से query exact और क्रम-संवेदी match होती है — अक्सर यह वो नहीं जो आप चाहते हैं।
3. Dotted path के साथ `$set` एक inner field बदलता है; parent को set करने से उसके अंदर का सब कुछ बदल जाता है।

---

## ➡️ Next Topic
**34. Querying Arrays of Documents** — combining dot notation with arrays: `"items.sku"`, `$elemMatch` and the positional projection.
