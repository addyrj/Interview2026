# 12. MongoDB Terminology Cheat — RDBMS to MongoDB mapping
# हिंदी में: MongoDB Terminology Cheat — RDBMS से MongoDB mapping

---

## 🔵 Simple Definition (English)
A quick translation table between SQL concepts and MongoDB concepts: database -> database, table -> collection, row -> document, column -> field, primary key -> `_id`, JOIN -> `$lookup`/embedding, GROUP BY -> `$group`, index -> index, transaction -> transaction (multi-document, replica set required).

## 🔵 सरल परिभाषा (Hindi)
SQL concepts और MongoDB concepts के बीच quick translation table: database -> database, table -> collection, row -> document, column -> field, primary key -> `_id`, JOIN -> `$lookup`/embedding, GROUP BY -> `$group`, index -> index, transaction -> transaction (multi-document, replica set ज़रूरी)।

---

## 🔴 Problem it Solves
Developers coming from MySQL/PostgreSQL waste time because names differ and the mental model (rows vs nested documents, joins vs embedding) is different. A mapping makes interviews and onboarding faster, but it must not be taken too literally: a document is not just a row.

## 🔴 यह क्यों बना? (Hindi)
MySQL/PostgreSQL से आने वाले developers नामों के फ़र्क और mental model (rows बनाम nested documents, joins बनाम embedding) की वजह से समय गँवाते हैं। Mapping interviews और onboarding तेज़ करती है, पर इसे बहुत literally नहीं लेना चाहिए: document सिर्फ़ एक row नहीं है।

---

## 🟢 How it Works — Step by Step

Step 1 → Start from the schema: table `users` -> collection `users`; row -> document; column -> field.
Step 2 → Translate statements: `INSERT` -> `insertOne/insertMany`; `SELECT` -> `find`; `UPDATE` -> `updateOne/updateMany`; `DELETE` -> `deleteOne/deleteMany`.
Step 3 → Translate clauses: `WHERE` -> filter doc; `ORDER BY` -> `sort`; `LIMIT/OFFSET` -> `limit/skip`; `COUNT(*)` -> `countDocuments`.
Step 4 → Translate relations: FK + JOIN -> embed child docs or `$lookup`.
Step 5 → Translate DDL: `ALTER TABLE ADD COLUMN` is not needed – fields are flexible (optionally enforce with `$jsonSchema` validation).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Schema से शुरू करो: table `users` -> collection `users`; row -> document; column -> field।
Step 2 → Statements translate करो: `INSERT` -> `insertOne/insertMany`; `SELECT` -> `find`; `UPDATE` -> `updateOne/updateMany`; `DELETE` -> `deleteOne/deleteMany`।
Step 3 → Clauses translate करो: `WHERE` -> filter doc; `ORDER BY` -> `sort`; `LIMIT/OFFSET` -> `limit/skip`; `COUNT(*)` -> `countDocuments`।
Step 4 → Relations: FK + JOIN -> child docs embed करो या `$lookup`।
Step 5 → DDL: `ALTER TABLE ADD COLUMN` की ज़रूरत नहीं – fields flexible हैं (चाहें तो `$jsonSchema` validation लगाओ)।

---

## 🟡 Real World Example
A Flipkart team migrating the `products` module from MySQL: the `products`, `product_attributes` and `product_images` tables collapse into ONE `products` collection where `attributes` is an object and `images` an array. The nightly report that did a 3-table JOIN becomes a single `find`. Reporting across `orders` and `users` still uses `$lookup`.

## 🟡 Real Example Hindi mein
Flipkart की team MySQL से `products` module migrate करती है: `products`, `product_attributes` और `product_images` tables एक ही `products` collection में सिमट जाती हैं जहाँ `attributes` object और `images` array है। 3-table JOIN वाली nightly report एक `find` बन जाती है। `orders` और `users` के बीच reporting अब भी `$lookup` से होती है।

---

## 💻 Code Example — Basic

```javascript
// SQL                                         MongoDB (mongosh)
// INSERT INTO m(n,p) VALUES('c',30);   -->    db.m.insertOne({ n: "c", p: 30 })
// SELECT * FROM m WHERE p = 10;        -->    db.m.find({ p: 10 })
// SELECT * FROM m ORDER BY p DESC;     -->    db.m.find().sort({ p: -1 })
// SELECT COUNT(*) FROM m WHERE p=10;   -->    db.m.countDocuments({ p: 10 })   // Output (test data): 2
// UPDATE m SET z=1 WHERE p=10;         -->    db.m.updateMany({ p: 10 }, { $set: { z: 1 } })
// DELETE FROM m WHERE p=10;            -->    db.m.deleteMany({ p: 10 })
// CREATE INDEX ix ON m(p);             -->    db.m.createIndex({ p: 1 })
```

## 💻 Code Example — Advanced

```javascript
// SQL: SELECT city, COUNT(*) AS c FROM users WHERE age > 18 GROUP BY city HAVING COUNT(*) > 1 ORDER BY c DESC LIMIT 5;
db.users.aggregate([
  { $match: { age: { $gt: 18 } } },                         // WHERE
  { $group: { _id: "$city", c: { $sum: 1 } } },             // GROUP BY city + COUNT(*)
  { $match: { c: { $gt: 1 } } },                            // HAVING
  { $sort: { c: -1 } },                                     // ORDER BY c DESC
  { $limit: 5 }                                             // LIMIT 5
])

// SQL: SELECT * FROM orders o JOIN users u ON u.id = o.user_id;
db.orders.aggregate([
  { $lookup: { from: "users", localField: "userId", foreignField: "_id", as: "user" } } // LEFT OUTER JOIN
])
```
(Standard syntax; the basic CRUD translations match outputs observed on mongod 8.0.4 in the neighbouring notes.)

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose mapping: Schema ~ table definition, Model ~ table access object, document ~ row
const User = mongoose.model('User', new mongoose.Schema({ name: String, city: String }));
// SELECT * FROM users WHERE city='Pune' ORDER BY name LIMIT 10;
app.get('/users', async (req, res) => {
  res.json(await User.find({ city: 'Pune' }).sort({ name: 1 }).limit(10));
});
// JOIN equivalent: .populate('orders') (extra query) or $lookup in aggregate()
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Designing MongoDB like a normalised SQL schema
```text
Wrong: users, addresses, phones as 3 collections joined with $lookup every request.
Right: embed addresses[] and phones[] in the user document if read together.
```

❌ Mistake 2: Assuming a document equals a row (same fields everywhere)
✅ Correct: Documents in a collection can differ; add `$jsonSchema` validation if you need rigidity.

❌ Mistake 3: Using `$lookup` as a default replacement for JOIN
✅ Correct: `$lookup` is costlier than SQL joins at scale; prefer embedding or denormalising hot paths.

---

## 🧠 Tricky Interview Question
Q: Is MongoDB "schemaless"?
Answer: Not really: it is **schema-flexible**. The schema lives in your application (and optionally in collection validators). Documents in one collection may differ, but good design still plans a consistent shape.

---

## ⚫ Interview Questions + Answers

Q1: Map table, row, column, primary key.
A1: Collection, document, field, `_id`.

Q2: SQL JOIN equivalent?
A2: `$lookup` stage in aggregation or embedding/referencing in schema design.

Q3: GROUP BY equivalent?
A3: `$group` with accumulators like `$sum`, `$avg`.

Q4: Foreign keys in MongoDB?
A4: Not enforced by the server; references are plain values and integrity is the app's job.

Q5: ACID support?
A5: Single-document operations are atomic; multi-document ACID transactions are supported on replica sets and sharded clusters (since 4.0 / 4.2).

---

## 🔷 When to Use + When Not to Use
✅ Use the mapping when:
- Learning, interviews, migrating from SQL

❌ Avoid relying on it when:
- Designing schema – think in access patterns, not tables

---

## 📊 Visual Diagram
```
 RDBMS                 MongoDB
 ─────────────────     ─────────────────────
 Database           ─► Database
 Table              ─► Collection
 Row                ─► Document
 Column             ─► Field
 Primary Key        ─► _id
 JOIN               ─► $lookup / embedding
 GROUP BY           ─► $group
 Index              ─► Index
 Foreign Key        ─► (reference value, not enforced)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Collection | ~ Table | Table जैसा |
| Document | ~ Row (but nested) | Row जैसा (nested) |
| Field | ~ Column | Column जैसा |
| $lookup | ~ LEFT JOIN | LEFT JOIN जैसा |
| $group | ~ GROUP BY | GROUP BY जैसा |
| Schema-flexible | Shape may vary | Shape बदल सकती है |

---

## ⚡ 3-Line Summary
English:
1. Table=collection, row=document, column=field, PK=`_id`, JOIN=`$lookup`/embedding.
2. SQL statements map to insert/find/update/delete and aggregation stages.
3. Do not copy normalised SQL schemas; design for access patterns.

Hindi:
1. Table=collection, row=document, column=field, PK=`_id`, JOIN=`$lookup`/embedding।
2. SQL statements insert/find/update/delete और aggregation stages में map होते हैं।
3. Normalised SQL schemas की नकल मत करो; access patterns के लिए design करो।

---

## ➡️ Next Topic
**16. Sorting, limit, skip** — Ordering and paging query results.
