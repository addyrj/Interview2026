# 2. SQL vs NoSQL — MongoDB vs MySQL/PostgreSQL
# हिंदी में: SQL बनाम NoSQL — MongoDB बनाम MySQL/PostgreSQL

---

## 🔵 Simple Definition (English)
**SQL databases** (MySQL, PostgreSQL) store data in **tables** with a predefined schema, relate tables via **foreign keys and JOINs**, and are queried with the SQL language. **MongoDB** stores **documents** in collections with a flexible schema, relates data mostly by **embedding** (or by references), and is queried with a JSON-style query API. Both can be ACID-compliant and both can scale; the difference is the data model and the default trade-offs.

## 🔵 सरल परिभाषा (Hindi)
**SQL databases** (MySQL, PostgreSQL) data को पहले से तय schema वाली **tables** में रखते हैं, tables को **foreign keys और JOINs** से जोड़ते हैं, और SQL भाषा से query होते हैं। **MongoDB** flexible schema वाली collections में **documents** रखता है, data को ज़्यादातर **embedding** (या references) से जोड़ता है, और JSON-style query API से query होता है। दोनों ACID हो सकते हैं और दोनों scale कर सकते हैं; फ़र्क data model और default trade-offs का है।

---

## 🔴 Problem it Solves
Interviewers (and architects) need a decision rule instead of religion. Picking the wrong database causes pain later: forcing deeply nested, fast-changing data into 12 joined tables slows development; forcing a banking ledger with strict multi-table invariants into loosely-validated documents risks inconsistency. Knowing the real differences (schema, relationships, scaling, transactions, query language) lets you choose by **access pattern** rather than by fashion.

## 🔴 यह क्यों बना? (Hindi)
Interviewers (और architects) को "पसंद" नहीं, decision rule चाहिए। गलत database चुनने पर बाद में दिक्कत होती है: गहरे nested, तेज़ी से बदलते data को 12 joined tables में ठूँसने से development धीमा होता है; बैंक ledger जैसे multi-table strict invariants को ढीले-validated documents में रखने से inconsistency का risk होता है। Schema, relationships, scaling, transactions और query language के असली फ़र्क जानकर आप fashion नहीं, **access pattern** से चुन पाते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **Model**: SQL normalises (split into tables, avoid duplication). MongoDB models around queries (embed what is read together).
Step 2 → **Write**: SQL `INSERT` into several tables (often in a transaction). MongoDB `insertOne` of one document (atomic by itself).
Step 3 → **Read**: SQL uses `JOIN` to rebuild the object. MongoDB returns the embedded document in one read, or uses `$lookup` when references are needed.
Step 4 → **Change shape**: SQL needs `ALTER TABLE` (migration). MongoDB just writes documents with the new field.
Step 5 → **Scale**: SQL traditionally scales up (bigger machine) and read-replicas; sharding exists but is add-on. MongoDB has built-in sharding.
Step 6 → **Consistency**: SQL gives multi-row ACID natively. MongoDB gives single-document atomicity natively and multi-document ACID transactions when needed.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Model**: SQL normalise करता है (tables में तोड़ना, duplication हटाना)। MongoDB queries के आसपास model करता है (जो साथ पढ़ा जाए उसे embed करो)।
Step 2 → **Write**: SQL में कई tables में `INSERT` (अक्सर transaction में)। MongoDB में एक document का `insertOne` (अपने-आप atomic)।
Step 3 → **Read**: SQL `JOIN` से object दोबारा बनाता है। MongoDB embedded document एक read में देता है, या references हों तो `$lookup`।
Step 4 → **Shape बदलना**: SQL में `ALTER TABLE` (migration)। MongoDB में नए field वाले documents बस लिख दो।
Step 5 → **Scale**: SQL पारंपरिक रूप से scale-up (बड़ी machine) और read-replicas; sharding add-on है। MongoDB में built-in sharding।
Step 6 → **Consistency**: SQL में multi-row ACID native। MongoDB में single-document atomicity native और ज़रूरत पर multi-document ACID transactions।

---

## 🟡 Real World Example
**Swiggy** keeps **payments and settlements** (money moving between customer, restaurant, delivery partner) in a relational database such as PostgreSQL/MySQL because strict constraints and multi-table transactions matter. The **restaurant menu and search catalog** has deeply nested, frequently changing data (variants, add-ons, timings), so a document store fits better. Same company, two different databases, chosen by access pattern (polyglot persistence).

## 🟡 Real Example Hindi mein
**Swiggy** **payments और settlements** (customer, restaurant, delivery partner के बीच पैसे का movement) को PostgreSQL/MySQL जैसे relational database में रखता है क्योंकि strict constraints और multi-table transactions ज़रूरी हैं। **Restaurant menu और search catalog** में गहरा nested और बार-बार बदलने वाला data है (variants, add-ons, timings), इसलिए document store बेहतर बैठता है। एक ही company, दो अलग databases, access pattern से चुने गए (polyglot persistence)।

---

## 💻 Code Example — Basic

The same task in SQL and in MongoDB. The MongoDB part was run on mongod 8.0.4.

```javascript
// ---------- SQL (PostgreSQL) for reference ----------
// CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT, city TEXT);     -- schema first
// CREATE TABLE orders (id SERIAL, user_id INT REFERENCES users(id), amount INT);
// SELECT u.name, SUM(o.amount) FROM users u JOIN orders o ON o.user_id = u.id GROUP BY u.name;

// ---------- MongoDB (mongosh) ----------
use swiggy_demo   // no CREATE needed - created lazily on first insert

// One document holds the user AND the orders (embedding replaces the JOIN)
db.users.insertOne({
  name: "Ravi",
  city: "Pune",
  orders: [ { amount: 250 }, { amount: 400 } ]  // nested array of sub-documents
})
// Output (id varies): { acknowledged: true, insertedId: ObjectId('...') }

// Equivalent of SELECT + SUM, using the aggregation framework
db.users.aggregate([
  { $unwind: "$orders" },                                         // one row per order
  { $group: { _id: "$name", total: { $sum: "$orders.amount" } } } // GROUP BY name, SUM(amount)
])
// Output: [ { _id: 'Ravi', total: 650 } ]
```

## 💻 Code Example — Advanced

```javascript
// mongosh: when you DO need JOIN-like behaviour - referencing + $lookup
db.customers.insertMany([{ _id: 1, name: "Ravi" }, { _id: 2, name: "Anita" }]) // parent docs
db.orders.insertMany([
  { _id: 101, customerId: 1, amount: 250 },  // customerId = reference (like a foreign key)
  { _id: 102, customerId: 1, amount: 400 },
  { _id: 103, customerId: 2, amount: 100 }
])

db.orders.aggregate([
  { $lookup: {
      from: "customers",          // collection to join with
      localField: "customerId",   // field in orders
      foreignField: "_id",        // field in customers
      as: "customer"              // output array
  } },
  { $unwind: "$customer" },       // array -> single object
  { $group: { _id: "$customer.name", total: { $sum: "$amount" } } },
  { $sort: { total: -1 } }
])
// Output: [ { _id: 'Ravi', total: 650 }, { _id: 'Anita', total: 100 } ]
// Note: no foreign-key constraint exists - MongoDB will NOT stop you from inserting customerId: 999.
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose gives MongoDB some SQL-like discipline: schema, required, refs, populate (JOIN-like)
const mongoose = require('mongoose');

const Customer = mongoose.model('Customer', new mongoose.Schema({ name: String }));
const Order = mongoose.model('Order', new mongoose.Schema({
  customer: { type: mongoose.Schema.Types.ObjectId, ref: 'Customer' }, // like a foreign key
  amount: { type: Number, required: true, min: 0 },                    // validation like CHECK
}));

// Express route: populate() does a second query behind the scenes (not a real SQL JOIN)
app.get('/orders', async (req, res) => {
  const orders = await Order.find().populate('customer', 'name'); // replace id with customer doc
  res.json(orders);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Designing MongoDB like SQL (every entity its own collection, JOIN everywhere)
```javascript
// Wrong - 3 collections + 2 $lookups just to render one order page
// Right - embed what is always read together; reference only big or shared data
db.orders.insertOne({ user: { name: "Ravi" }, items: [{ sku: "A1", qty: 2 }], address: { city: "Pune" } })
```

❌ Mistake 2: Assuming MongoDB enforces foreign keys / cascades like SQL
✅ Correct: MongoDB has no foreign-key constraints. Your app (or transactions + cleanup jobs) must keep references consistent.

---

## 🧠 Tricky Interview Question

**Q: "MongoDB is faster than SQL" - true or false?**

Answer: False as a blanket statement. Speed depends on the access pattern. Reading one embedded document avoids JOINs and is very fast; but aggregations over relational data, many-to-many joins and ad-hoc reporting are often faster and simpler in PostgreSQL. Both are fast when properly indexed and slow when not. The correct answer is "it depends on data model and queries, benchmark your workload".

---

## ⚫ Interview Questions + Answers

Q1: Main differences between SQL and MongoDB?
A1: Tables/rows/fixed schema/JOINs vs collections/documents/flexible schema/embedding. SQL uses SQL language and strict constraints; MongoDB uses a JSON query API, built-in sharding and flexible shape.

Q2: Does MongoDB support JOINs?
A2: Yes, limited: the aggregation stage `$lookup` does a left outer join between collections (and `$graphLookup` for recursion). But the idiomatic way is to embed so that you need fewer joins.

Q3: Which scales better, SQL or MongoDB?
A3: MongoDB has native horizontal scaling (sharding) and is simpler to distribute because documents are self-contained. SQL systems scale vertically well and can shard (Citus, Vitess) with extra effort.

Q4: SQL ACID vs MongoDB?
A4: Relational databases give multi-row ACID by default. MongoDB gives atomic single-document writes always and multi-document ACID transactions since 4.0 (replica sets) / 4.2 (sharded), at some performance cost.

Q5: When would you choose PostgreSQL over MongoDB?
A5: Strong relational data with many entities and constraints (finance, inventory, ERP), complex reporting with joins, and teams needing mature SQL tooling.

---

## 🔷 When to Use + When Not to Use
✅ Use MongoDB when:
- Schema evolves fast, data is hierarchical, reads are by a known key/document
- You need built-in horizontal scaling and high write throughput

✅ Use SQL when:
- Data is strongly relational with constraints, complex joins and reports are common

❌ Avoid MongoDB when:
- You need enforced foreign keys, many-to-many heavy joins and strict normalised design

---

## 📊 Visual Diagram
```
        SQL (normalised)                     MONGODB (embedded)
  ┌─────────┐   ┌──────────┐          ┌─────────────────────────────┐
  │ users   │◄──│ orders   │          │ users                       │
  │ id,name │   │ user_id  │          │ { name: "Ravi",             │
  └─────────┘   │ amount   │          │   orders: [{amount:250},    │
   JOIN needed  └──────────┘          │            {amount:400}] }  │
                                      └─────────────────────────────┘
 Schema: fixed, ALTER TABLE            Schema: flexible, optional $jsonSchema
 Scale : up (+ sharding add-on)        Scale : out (built-in sharding)
 Links : foreign keys enforced         Links : embed / reference (not enforced)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Normalisation | Splitting data to avoid duplication | Duplication हटाने के लिए data बाँटना |
| Denormalisation | Duplicating/embedding for fast reads | तेज़ reads के लिए embed/duplicate करना |
| JOIN | Combine rows of tables | Tables की rows जोड़ना |
| $lookup | MongoDB's left outer join stage | MongoDB का left outer join stage |
| Foreign key | Enforced link between tables | Tables के बीच enforced link |
| Polyglot persistence | Using several DB types together | कई तरह के databases साथ इस्तेमाल करना |
| Vertical / Horizontal scaling | Bigger machine / more machines | बड़ी machine / ज़्यादा machines |

---

## ⚡ 3-Line Summary
English:
1. SQL = tables, fixed schema, JOINs, strong constraints; MongoDB = documents, flexible schema, embedding, built-in sharding.
2. Neither is always faster or "better"; choose by access pattern and consistency needs (polyglot persistence is common).
3. MongoDB has `$lookup` and transactions, but no foreign keys, so keep references consistent in the app.

Hindi:
1. SQL = tables, fixed schema, JOINs, strong constraints; MongoDB = documents, flexible schema, embedding, built-in sharding।
2. कोई हमेशा तेज़ या "बेहतर" नहीं; access pattern और consistency की ज़रूरत से चुनो (polyglot persistence आम है)।
3. MongoDB में `$lookup` और transactions हैं, पर foreign keys नहीं, इसलिए references app में consistent रखो।

---

## ➡️ Next Topic
**3. MongoDB Architecture (mongod, databases, collections, documents)** — The building blocks and the server process behind them.
