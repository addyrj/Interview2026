# 30. Element Operators ($exists, $type)
# हिंदी में: Element Operators ($exists, $type)

---

## 🔵 Simple Definition (English)
**Element operators** test the **presence** and **BSON type** of a field rather than its value. **`$exists: true|false`** checks whether the field is present in the document (even if its value is `null`). **`$type`** checks the BSON type of the value (`"string"`, `"int"`, `"double"`, `"array"`, `"null"` ...; also numeric codes, an array of types, or the alias `"number"`).

## 🔵 सरल परिभाषा (Hindi)
**Element operators** field की **मौजूदगी** और **BSON type** जाँचते हैं, उसकी value नहीं। **`$exists: true|false`** देखता है कि field document में है या नहीं (भले ही value `null` हो)। **`$type`** value का BSON type जाँचता है (`"string"`, `"int"`, `"double"`, `"array"`, `"null"` ...; numeric codes, types का array या alias `"number"` भी चलता है)।

---

## 🔴 Problem it Solves
MongoDB is schema-flexible: some documents have `price`, others do not; some store `price` as a number, others as the string `"250"` (dirty data from an old import). Plain equality queries cannot find "documents missing a field" or "documents whose field has the wrong type". Element operators let you audit data quality, find incomplete records, and run safe migrations (`$type: "string"` -> convert to number).

## 🔴 यह क्यों बना? (Hindi)
MongoDB schema-flexible है: कुछ documents में `price` है, कुछ में नहीं; कुछ में `price` number है, कुछ में string `"250"` (पुराने import का गंदा data)। साधारण equality query "वो documents जिनमें field नहीं है" या "जिनका field ग़लत type का है" नहीं ढूँढ सकती। Element operators से data quality audit, अधूरे records की खोज और सुरक्षित migration (`$type: "string"` -> number में बदलना) हो पाते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `{ field: { $exists: true } }` matches documents where the field is **present**, including `null` values and empty strings.
Step 2 → `{ field: { $exists: false } }` matches documents where the field is **absent**.
Step 3 → `{ field: null }` matches **both** "value is null" and "field missing". To match only real nulls use `{ field: { $type: "null" } }` or `{ field: { $exists: true, $eq: null } }`.
Step 4 → `$type` accepts a string alias (`"string"`, `"int"`, `"long"`, `"double"`, `"decimal"`, `"bool"`, `"date"`, `"objectId"`, `"array"`, `"object"`, `"null"`), a number code (`2` string, `16` int32, `10` null) or an **array** of these.
Step 5 → `"number"` is a special alias matching int, long, double and decimal.
Step 6 → On **array fields** `$type` checks the elements too: `{ price: { $type: "string" } }` matches an array that contains a string. Use `$type: "array"` to match the field being an array itself.
Step 7 → An unknown alias raises an error (`Unknown type name alias: foo`). In aggregation, the `$type` **expression** returns the type name of a value (`"missing"` for absent fields).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `{ field: { $exists: true } }` उन documents से match करता है जहाँ field **मौजूद** है, `null` values और खाली strings समेत।
Step 2 → `{ field: { $exists: false } }` उनसे match करता है जहाँ field **ग़ायब** है।
Step 3 → `{ field: null }` **दोनों** से match करता है: "value null है" और "field missing है"। सिर्फ असली null चाहिए तो `{ field: { $type: "null" } }` या `{ field: { $exists: true, $eq: null } }` लो।
Step 4 → `$type` string alias (`"string"`, `"int"`, `"long"`, `"double"`, `"decimal"`, `"bool"`, `"date"`, `"objectId"`, `"array"`, `"object"`, `"null"`), number code (`2` string, `16` int32, `10` null) या इनका **array** लेता है।
Step 5 → `"number"` एक special alias है जो int, long, double और decimal सबसे match करता है।
Step 6 → **array fields** पर `$type` elements भी जाँचता है: `{ price: { $type: "string" } }` ऐसे array से भी match करता है जिसमें कोई string हो। Field के खुद array होने के लिए `$type: "array"` लो।
Step 7 → अज्ञात alias पर error आता है (`Unknown type name alias: foo`)। Aggregation में `$type` **expression** value का type name लौटाता है (absent field के लिए `"missing"`)।

---

## 🟡 Real World Example
**Flipkart catalog cleanup**: sellers upload products via CSV. Some rows lack `price` (incomplete listing), some have `price: "250"` (string) from a bad import, and some have `price: null`. The catalog team runs `find({ price: { $exists: false } })` to flag incomplete listings, `find({ price: { $type: "string" } })` to fix the string prices, and `find({ price: { $type: "null" } })` to separate real nulls from missing fields.

## 🟡 Real Example Hindi mein
**Flipkart catalog cleanup**: sellers CSV से products upload करते हैं। कुछ rows में `price` नहीं है (अधूरी listing), कुछ में ग़लत import से `price: "250"` (string), और कुछ में `price: null`। Catalog team `find({ price: { $exists: false } })` से अधूरी listings flag करती है, `find({ price: { $type: "string" } })` से string prices ठीक करती है, और `find({ price: { $type: "null" } })` से असली null को missing field से अलग करती है।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4, mongosh. Helper `ids(q)` prints matching `_id`s.

```javascript
use catalog_demo                                   // switch database
db.dropDatabase()                                  // clean start
db.p.insertMany([                                  // six products, deliberately messy
  { _id: 1, n: "A", price: 100,   note: null },    // int price (mongosh stores 100 as int32), note is null
  { _id: 2, n: "B" },                              // no price, no note
  { _id: 3, n: "C", price: "250", note: "x" },     // price stored as a STRING
  { _id: 4, n: "D", price: 99.5,  note: null },    // double price
  { _id: 5, n: "E", price: NumberInt(7) },         // explicit int, no note
  { _id: 6, n: "F", price: [10, "x"] }             // array with a number and a string
])
const ids = q => print(JSON.stringify(db.p.find(q).toArray().map(x => x._id))) // helper

ids({ price: { $exists: true } })                  // [1,3,4,5,6]  present
ids({ price: { $exists: false } })                 // [2]          absent
ids({ note: null })                                // [1,2,4,5,6]  null OR missing!
ids({ note: { $exists: true, $eq: null } })        // [1,4]        only real nulls
ids({ note: { $type: 10 } })                       // [1,4]        10 = null
ids({ note: { $type: "null" } })                   // [1,4]        same, readable alias

ids({ price: { $type: "string" } })                // [3,6]        6 matches: array contains "x"
ids({ price: { $type: "number" } })                // [1,4,5,6]    int/long/double/decimal
ids({ price: { $type: ["string", "double"] } })    // [3,4,6]      any of the listed types
ids({ price: { $type: "array" } })                 // [6]          field itself is an array
ids({ price: { $type: "int" } })                   // [1,5,6]      6 matches via element 10
ids({ price: { $type: 16 } })                      // [1,5,6]      16 = int32, same as "int"
ids({ "price.0": { $exists: true } })              // [6]          array has an element at index 0
ids({ price: { $not: { $type: "number" } } })      // [2,3]        not numeric (and 6 excluded: it has a number)

db.p.find({ price: { $type: "foo" } }).toArray()
// Error: Unknown type name alias: foo

// Aggregation $type EXPRESSION — what type is each value?
db.p.aggregate([{ $project: { t: { $type: "$price" } } }]).toArray().map(x => x._id + ":" + x.t)
// Output: [ '1:int', '2:missing', '3:string', '4:double', '5:int', '6:array' ]
```

## 💻 Code Example — Advanced

```javascript
// Data-quality audit + safe migration (mongosh, MongoDB 4.2+ pipeline updates)
// 1) How many documents per price type?
db.p.aggregate([
  { $group: { _id: { $type: "$price" }, count: { $sum: 1 } } }, // group by BSON type name
  { $sort: { count: -1 } }                                      // largest group first
])

// 2) Convert string prices to numbers in place, safely
db.p.updateMany(
  { price: { $type: "string" } },                               // only string prices
  [ { $set: { price: { $convert: { input: "$price", to: "double", onError: null } } } } ] // pipeline update
)
// Rows whose string is not numeric become null instead of failing the whole update.
// (Doc 6 holds an array, so skip arrays explicitly in real use:)
//   { price: { $type: "string" }, $expr: { $not: { $isArray: "$price" } } }

// 3) JSON-schema-like guard that uses the same types
db.createCollection("catalog", { validator: { $jsonSchema: { properties: { price: { bsonType: ["int", "double"] } } } } })
```

```javascript
// Node.js driver v6 — flag incomplete listings
const incomplete = await db.collection('p').find(
  { $or: [ { price: { $exists: false } }, { price: { $type: 'null' } } ] }, // missing OR null
  { projection: { n: 1 } }                      // only the name
).toArray();
console.log(incomplete.length);                 // listings to fix
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const Product = mongoose.model('Product', new mongoose.Schema({}, { strict: false })); // flexible schema
const app = express();

// GET /admin/products/audit?issue=missing|string|null
app.get('/admin/products/audit', async (req, res) => {
  const filters = {
    missing: { price: { $exists: false } },          // field absent
    string:  { price: { $type: 'string' } },         // wrong type
    null:    { price: { $type: 'null' } }            // explicit null
  };
  const f = filters[req.query.issue];
  if (!f) return res.status(400).json({ error: 'issue must be missing|string|null' });
  res.json(await Product.find(f).select('n price').lean()); // lean = plain objects
});
```
Mongoose note: with a strict schema where `price: Number`, Mongoose **casts** strings like `"250"` in filters and documents, but the stored value is whatever was written, so use `.lean()`/native queries for auditing real BSON types.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `{ field: null }` to find missing fields
```javascript
db.p.find({ note: null })                       // Wrong for "only null": also returns docs where note is absent
db.p.find({ note: { $exists: false } })         // Right for missing
db.p.find({ note: { $type: "null" } })          // Right for explicit null
```

❌ Mistake 2: Using `$exists: true` for "non-empty"
```javascript
db.p.find({ note: { $exists: true } })          // Wrong: includes null and ""
db.p.find({ note: { $exists: true, $nin: [null, ""] } }) // Right: present, not null, not empty
```

❌ Mistake 3: Forgetting that `$type` looks inside arrays
```javascript
db.p.find({ price: { $type: "string" } })       // returns _id 6 too (array containing "x")
db.p.find({ price: { $type: "string" }, "price.0": { $exists: false } }) // Right: exclude arrays
```

---

## 🧠 Tricky Interview Question

```javascript
db.p.find({ price: { $type: "number" } })
```
Documents: `price: 100`, `price: "250"`, `price: [10, "x"]`. Which match?

Answer: `100` matches and so does `[10, "x"]` (because the array **contains** a number), but `"250"` does not. Real output ids: `[1,4,5,6]`. Takeaway: `$type` applies per array element; to test the field being an array use `$type: "array"`, and note that `"number"` covers int, long, double and decimal.

---

## ⚫ Interview Questions + Answers

Q1: Does `$exists: true` match a field with value `null`?
A1: Yes. `$exists` only checks presence of the key, so `{ note: null }` documents match `$exists: true`.

Q2: How do you find documents where a field is explicitly null but not missing?
A2: `{ f: { $type: "null" } }` (or `{ f: { $exists: true, $eq: null } }`). `{ f: null }` alone also matches missing fields.

Q3: Can `$type` accept multiple types?
A3: Yes: `{ f: { $type: ["string", "double"] } }` matches any listed type. The alias `"number"` covers all numeric types.

Q4: Does `$exists: false` use an index?
A4: A regular index stores `null` for missing fields, so `$exists: false` still needs to examine documents; use a sparse/partial index or a different design for hot queries.

Q5: What is the difference between the `$type` query operator and the `$type` aggregation operator?
A5: The query operator filters documents by field type. The aggregation expression `{ $type: "$f" }` returns the type name as a string (`"missing"` if absent), used in `$project`/`$group`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Auditing and cleaning inconsistent data, schema migrations.
- Distinguishing missing from null.
- Querying polymorphic fields (string vs number) during a type change.

❌ Avoid when:
- You can enforce shape with `$jsonSchema` validation — prevent the problem instead.
- You need fast lookups on missing fields in a huge collection without a supporting partial index.

---

## 📊 Visual Diagram
```
 doc A: { price: 100 }      doc B: { }         doc C: { price: null }
      │                        │                      │
 $exists:true  ✔               ✖                      ✔
 $exists:false ✖               ✔                      ✖
 {price:null}  ✖               ✔  (missing)           ✔
 $type:"null"  ✖               ✖                      ✔
 $type:"number"✔               ✖                      ✖
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$exists` | Is the field present? | Field मौजूद है या नहीं |
| `$type` | BSON type of the value | Value का BSON type |
| BSON type alias | Name like `"string"`, `"int"` | `"string"`, `"int"` जैसा नाम |
| `"number"` alias | int, long, double, decimal | सभी numeric types |
| Missing vs null | Absent key vs key holding null | Key का न होना बनाम null value |
| `$convert` | Converts a value to another type | Value का type बदलता है |

---

## ⚡ 3-Line Summary
English:
1. `$exists` tests presence of a key, `$type` tests the BSON type of its value.
2. `{ f: null }` matches null AND missing; use `$type: "null"` for real nulls.
3. `$type` also inspects array elements, and `"number"` covers all numeric types.

Hindi:
1. `$exists` key की मौजूदगी जाँचता है, `$type` उसकी value का BSON type।
2. `{ f: null }` null और missing दोनों से match करता है; असली null के लिए `$type: "null"` लो।
3. `$type` array के elements भी देखता है, और `"number"` सभी numeric types को cover करता है।

---

## ➡️ Next Topic
**31. Evaluation Operators ($regex, $expr, $mod)** — pattern matching, comparing fields inside the same document, and modulo arithmetic in queries.
