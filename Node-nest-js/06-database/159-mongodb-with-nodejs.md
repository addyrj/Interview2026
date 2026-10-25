# 159. MongoDB with Node.js
# हिंदी में: Node.js के साथ MongoDB

---

## 🔵 Simple Definition (English)
**MongoDB** is a NoSQL, document-oriented database that stores data as flexible, JSON-like **BSON documents** instead of rows/tables. Connecting it with Node.js uses the official **MongoDB Node.js Driver** (`mongodb` package), which provides a `MongoClient` to connect, and collections/documents are queried with a JS-object-based API instead of SQL.

## 🔵 सरल परिभाषा (Hindi)
**MongoDB** एक NoSQL, document-oriented database है जो data को flexible, JSON-जैसे **BSON documents** में रखता है, rows/tables की जगह। Node.js के साथ connect करने के लिए official **MongoDB Node.js Driver** (`mongodb` package) इस्तेमाल होता है, जो connect करने के लिए `MongoClient` देता है, और collections/documents को SQL की जगह JS-object-based API से query किया जाता है।

---

## 🔴 Problem it Solves
Relational databases require a fixed schema upfront (columns defined before inserting data) and complex JOINs for nested/related data. For applications with rapidly evolving data shapes (e.g., a product catalog where different categories have wildly different attributes) or deeply nested data that's always accessed together (a blog post with embedded comments), forcing it into rigid tables adds friction. MongoDB stores whole nested objects as single documents — no schema migration needed to add a new field, and related data can be embedded directly, avoiding JOINs for common access patterns.

## 🔴 यह क्यों बना? (Hindi)
Relational databases को पहले से fixed schema चाहिए (insert से पहले columns define) और nested/related data के लिए complex JOINs। जिन applications में data shape तेज़ी से बदलती है (जैसे product catalog जहाँ हर category के attributes अलग होते) या nested data जो हमेशा साथ access होता (blog post + embedded comments), वहाँ rigid tables friction create करते। MongoDB पूरे nested objects को एक document में रखता है — नया field add करने के लिए schema migration नहीं चाहिए।

---

## 🟢 How it Works — Step by Step

Step 1 → Install: `npm install mongodb`.
Step 2 → Create a `MongoClient` with a connection string (`mongodb://` or `mongodb+srv://` for Atlas) and call `.connect()`.
Step 3 → Get a reference to a database (`client.db('mydb')`) and a collection (`db.collection('users')`).
Step 4 → Run CRUD operations with JS-object queries: `insertOne`, `find`, `updateOne`, `deleteOne`, each returning Promises.
Step 5 → Always close the client (`client.close()`) on app shutdown, or reuse a single client instance across the app's lifetime (connection pooling is built in).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Install करो: `npm install mongodb`।
Step 2 → `MongoClient` बनाओ connection string के साथ (`mongodb://` या Atlas के लिए `mongodb+srv://`) और `.connect()` करो।
Step 3 → Database reference (`client.db('mydb')`) और collection (`db.collection('users')`) लो।
Step 4 → JS-object queries से CRUD operations चलाओ: `insertOne`, `find`, `updateOne`, `deleteOne` — सब Promises return करते।
Step 5 → App shutdown पर client close करो (`client.close()`), या पूरे app में एक client instance reuse करो (connection pooling built-in है)।

---

## 🟡 Real World Example
**Zomato's menu-catalog service** stores restaurant menus in MongoDB because every restaurant's menu structure differs wildly — some have size variants, some have combo deals, some have spice-level options. Each menu item is one flexible document: `{ name, price, variants: [...], tags: [...], restaurantId }`. Adding a brand-new attribute (like "allergen info") for new restaurants requires zero schema migration — just start including the field in new documents; old documents simply don't have it, and the app handles its absence gracefully.

## 🟡 Real Example Hindi mein
**Zomato की menu-catalog service** restaurant menus को MongoDB में रखती है क्योंकि हर restaurant का menu structure बहुत अलग होता है — कुछ में size variants, कुछ में combo deals। हर menu item एक flexible document है। नया attribute (जैसे "allergen info") add करने के लिए कोई schema migration नहीं चाहिए — सिर्फ नए documents में field include करना शुरू करो।

---

## 💻 Code Example — Basic

```javascript
// mongodb-basic.js
// npm install mongodb
// Requires a running MongoDB instance (local or Atlas connection string)
const { MongoClient } = require('mongodb');

const uri = process.env.MONGO_URI || 'mongodb://localhost:27017';
const client = new MongoClient(uri);

async function main() {
  try {
    await client.connect(); // establishes connection pool
    const db = client.db('zomato_demo');
    const menuItems = db.collection('menuItems');

    // INSERT — flexible document shape, no predefined schema required
    const insertResult = await menuItems.insertOne({
      name: 'Paneer Tikka',
      price: 220,
      restaurantId: 'rest-101',
      tags: ['vegetarian', 'starter'],
      variants: [{ size: 'half', price: 120 }, { size: 'full', price: 220 }],
    });
    console.log('Inserted document id:', insertResult.insertedId);

    // FIND — query using a JS object, not SQL
    const found = await menuItems.find({ restaurantId: 'rest-101' }).toArray();
    console.log('Menu items for restaurant:', found);

    // UPDATE — modify a document matching a filter
    await menuItems.updateOne(
      { name: 'Paneer Tikka' },
      { $set: { price: 240 } } // $set updates specific fields without touching the rest
    );

    // DELETE
    await menuItems.deleteOne({ name: 'Paneer Tikka' });
  } finally {
    await client.close(); // release the connection pool
  }
}

main().catch(console.error);
```

## 💻 Code Example — Advanced

```javascript
// mongodb-advanced.js — Production patterns: singleton client, indexes, bulk ops, aggregation
const { MongoClient } = require('mongodb');

// Singleton pattern — create ONE client, reuse the connection pool across the app
let clientPromise;
function getClient() {
  if (!clientPromise) {
    const client = new MongoClient(process.env.MONGO_URI, {
      maxPoolSize: 20, // like pg's "max" — limits concurrent connections
    });
    clientPromise = client.connect();
  }
  return clientPromise;
}

async function setupIndexes(db) {
  // Index on restaurantId speeds up the common "get menu for restaurant" query
  await db.collection('menuItems').createIndex({ restaurantId: 1 });
  // Compound + unique index to prevent duplicate (restaurantId, name) entries
  await db.collection('menuItems').createIndex({ restaurantId: 1, name: 1 }, { unique: true });
}

async function bulkInsertMenu(db, items) {
  // insertMany is far more efficient than looping insertOne for bulk data
  const result = await db.collection('menuItems').insertMany(items, { ordered: false });
  console.log(`Inserted ${result.insertedCount} items`);
  return result;
}

async function getRestaurantAverages(db) {
  // Aggregation pipeline — MongoDB's equivalent of SQL GROUP BY + AVG
  return db.collection('menuItems').aggregate([
    { $match: { price: { $gt: 0 } } },                       // like WHERE
    { $group: { _id: '$restaurantId', avgPrice: { $avg: '$price' }, count: { $sum: 1 } } }, // like GROUP BY
    { $sort: { avgPrice: -1 } },                               // like ORDER BY DESC
    { $limit: 10 },
  ]).toArray();
}

async function run() {
  const client = await getClient();
  const db = client.db('zomato_demo');

  try {
    await setupIndexes(db);

    await bulkInsertMenu(db, [
      { name: 'Butter Naan', price: 50, restaurantId: 'rest-101' },
      { name: 'Dal Makhani', price: 180, restaurantId: 'rest-101' },
      { name: 'Veg Biryani', price: 160, restaurantId: 'rest-102' },
    ]);

    const averages = await getRestaurantAverages(db);
    console.log('Average menu price per restaurant:', averages);
  } catch (err) {
    if (err.code === 11000) {
      // 11000 = MongoDB's duplicate key error code (violates a unique index)
      console.error('Duplicate menu item detected:', err.message);
    } else {
      console.error('MongoDB error:', err.message);
    }
  }
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express app sharing one MongoClient connection pool across all requests
const express = require('express');
const { MongoClient, ObjectId } = require('mongodb');

const app = express();
app.use(express.json());

let db;
// Connect once at startup, before accepting requests
MongoClient.connect(process.env.MONGO_URI).then((client) => {
  db = client.db('zomato_demo');
  app.listen(3000, () => console.log('Server started, DB connected'));
});

app.get('/api/menu/:restaurantId', async (req, res) => {
  const items = await db.collection('menuItems').find({ restaurantId: req.params.restaurantId }).toArray();
  res.json(items);
});

app.get('/api/menu-item/:id', async (req, res) => {
  try {
    // ObjectId must be used to query by Mongo's default _id field
    const item = await db.collection('menuItems').findOne({ _id: new ObjectId(req.params.id) });
    if (!item) return res.status(404).json({ error: 'Not found' });
    res.json(item);
  } catch {
    res.status(400).json({ error: 'Invalid ID format' });
  }
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Creating a new `MongoClient` per request
```javascript
// Wrong — opens a new connection pool EVERY request, exhausts resources
app.get('/items', async (req, res) => {
  const client = new MongoClient(uri);
  await client.connect();
  res.json(await client.db('x').collection('items').find().toArray());
});

// Right — connect ONCE at startup, reuse the client/db everywhere
let db;
MongoClient.connect(uri).then((client) => { db = client.db('x'); });
app.get('/items', async (req, res) => res.json(await db.collection('items').find().toArray()));
```

❌ Mistake 2: Forgetting `ObjectId` when querying by MongoDB's default `_id`
✅ Correct: `_id` fields are stored as `ObjectId` type, NOT plain strings. Querying `{ _id: req.params.id }` (a string) silently matches NOTHING — you must wrap it: `{ _id: new ObjectId(req.params.id) }`.

---

## 🧠 Tricky Interview Question

```javascript
await collection.insertOne({ name: 'Item A', price: 100 });
await collection.insertOne({ name: 'Item B' }); // no "price" field at all!

const result = await collection.find({ price: { $exists: true } }).toArray();
console.log(result.length);
```
Answer: Output is `1` — only "Item A" matches. Because MongoDB is schema-FLEXIBLE, "Item B" was inserted successfully even without a `price` field — there's no schema enforcing all documents to have the same shape. This demonstrates MongoDB's core trade-off: flexibility means the application code itself (or optional schema validation rules at the collection level) must handle missing/inconsistent fields, since the database won't reject them by default.

---

## ⚫ Interview Questions + Answers

Q1: What is the role of `MongoClient` in the Node.js driver?
A1: `MongoClient` represents the connection to a MongoDB cluster/server. It internally manages a connection pool (similar to `pg.Pool`) — you create ONE `MongoClient` instance, call `.connect()` once, and reuse it (via `client.db(name)`) for all database/collection access throughout the app's lifetime. You should NOT create a new client per request.

Q2: How do MongoDB documents differ from relational database rows?
A2: A document is a self-contained, JSON-like (BSON) structure that CAN be nested (objects within objects, arrays of objects) and doesn't require every document in a collection to have the same fields/shape. A relational row is a fixed set of columns defined by the table schema, and relationships to other data require JOINs across separate tables. Documents favor embedding related data; relational rows favor normalization and JOINs.

Q3: What is the `_id` field, and what type is it by default?
A3: Every MongoDB document automatically gets an `_id` field acting as its primary key, unique within the collection. By default it's an `ObjectId` — a 12-byte identifier (timestamp + machine + process + counter) that's NOT a plain string. When querying by `_id` using a string from a URL param, you must convert it: `new ObjectId(idString)`, or the query silently returns no matches (invalid ObjectId strings throw an error instead).

Q4: What's the difference between `insertOne`/`insertMany` performance-wise, and when should you use `insertMany`?
A4: `insertOne` sends ONE document per network round trip. `insertMany` batches multiple documents into significantly fewer round trips (configurable `ordered: true/false` — unordered allows MongoDB to continue inserting remaining docs even if one fails, useful for bulk imports where partial success is acceptable). Use `insertMany` whenever inserting more than a handful of documents at once — looping `insertOne` is much slower for bulk data.

Q5: How do indexes work in MongoDB, and why are they important?
A5: Indexes are data structures (commonly B-trees) that speed up queries on specific fields by avoiding a full collection scan. `db.collection('x').createIndex({ field: 1 })` creates an ascending index. Without an index on frequently-queried fields (e.g., `restaurantId` in a menu lookup), MongoDB must scan EVERY document to find matches — fine for small collections but catastrophic for millions of documents. Compound indexes (`{ a: 1, b: 1 }`) and unique indexes (`{ unique: true }`) support more complex query/constraint patterns.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data shape varies significantly between records or evolves frequently (catalogs, user-generated content, logs)
- You frequently access deeply nested/related data together and want to avoid JOINs (embed instead)
- You need horizontal scalability (sharding) for very large datasets

❌ Avoid when:
- Your data is highly relational with strict consistency/ACID transaction needs across multiple entities (though MongoDB does support multi-document transactions since v4.0, it's less idiomatic)
- You need strong schema enforcement by default (MongoDB needs explicit schema validation rules to get this, unlike SQL's inherent column constraints)

---

## 📊 Visual Diagram
```
MONGODB WITH NODE.JS
──────────────────────────────────────────────
  MongoClient (connection pool, created ONCE)
       │
       ▼
  client.db('zomato_demo')
       │
       ▼
  db.collection('menuItems')
       │
       ├── insertOne / insertMany
       ├── find({ filter }).toArray()
       ├── updateOne({ filter }, { $set: {...} })
       ├── deleteOne({ filter })
       └── aggregate([ pipeline stages ])

  DOCUMENT EXAMPLE:
  {
    _id: ObjectId("..."),
    name: "Paneer Tikka",
    variants: [{ size: "half", price: 120 }],   ◄── embedded, no JOIN needed
    tags: ["vegetarian"]
  }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Document | A JSON-like record (BSON) | JSON जैसा record |
| Collection | Group of documents (like a table) | Documents का group (table जैसा) |
| MongoClient | Connection pool manager | Connection pool manager |
| ObjectId | Default unique document ID type | Default unique document ID type |
| Embedding | Storing related data inside a document | Related data document के अंदर रखना |
| Aggregation pipeline | Multi-stage data processing query | Multi-stage data processing query |
| Index | Structure speeding up queries | Query तेज़ करने वाली structure |

---

## ⚡ 3-Line Summary
English:
1. MongoDB stores flexible, JSON-like documents in collections, queried via the `mongodb` driver's `MongoClient` using JS objects instead of SQL.
2. Create ONE `MongoClient` connection pool at app startup and reuse it everywhere — never per request.
3. Remember `_id` is an `ObjectId`, not a plain string — wrap route params with `new ObjectId(id)` before querying.

Hindi:
1. MongoDB flexible, JSON-जैसे documents को collections में रखता है, `mongodb` driver के `MongoClient` से JS objects से query होता है।
2. App startup पर एक ही `MongoClient` connection pool बनाओ और हर जगह reuse करो — हर request पर नहीं।
3. याद रखो `_id` एक `ObjectId` है, plain string नहीं — route params को `new ObjectId(id)` से wrap करो।

---

## ➡️ Next Topic
**160. Mongoose — Complete Guide** — A schema-based ODM layer on top of the native MongoDB driver, adding validation, middleware, and typed models.
