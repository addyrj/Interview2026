# 81. MongoDB Native Driver with Node.js
# हिंदी में: Node.js के साथ MongoDB Native Driver

---

## 🔵 Simple Definition (English)
The **MongoDB Node.js driver** (the `mongodb` npm package) is the official low-level library for talking to MongoDB from JavaScript/TypeScript. A single `MongoClient` manages a **connection pool**; from it you get a `Db`, then a `Collection`, and call methods like `insertOne`, `find`, `updateOne`, `aggregate`. It maps almost one-to-one to the mongosh shell API and has no schemas or validation of its own (that is what Mongoose adds on top).

## 🔵 सरल परिभाषा (Hindi)
**MongoDB Node.js driver** (`mongodb` npm package) JavaScript/TypeScript से MongoDB से बात करने की official low-level library है। एक `MongoClient` **connection pool** सँभालता है; उससे आप `Db` और फिर `Collection` लेते हैं और `insertOne`, `find`, `updateOne`, `aggregate` जैसे methods call करते हैं। यह mongosh shell API से लगभग एक-से-एक map होता है और इसमें अपने schemas या validation नहीं होते (वह Mongoose ऊपर से जोड़ता है)।

---

## 🔴 Problem it Solves
Your Node app cannot speak the MongoDB wire protocol or BSON by itself. Writing sockets, authentication (SCRAM), TLS, replica-set discovery, failover, retryable writes, and BSON type conversion manually would be a huge task. The driver does all that: it discovers the primary, reconnects on failover, retries safe writes once, pools connections and converts JS types (Date, ObjectId, Decimal128) to BSON and back.

## 🔴 यह क्यों बना? (Hindi)
आपका Node app खुद MongoDB wire protocol या BSON नहीं बोल सकता। Sockets, authentication (SCRAM), TLS, replica-set discovery, failover, retryable writes और BSON type conversion हाथ से लिखना बहुत बड़ा काम है। Driver यह सब करता है: primary खोजता है, failover पर reconnect करता है, safe writes को एक बार retry करता है, connections pool करता है और JS types (Date, ObjectId, Decimal128) को BSON में बदलता है और वापस।

---

## 🟢 How it Works — Step by Step

Step 1 → `npm install mongodb`. (Tested here with the current driver on Node v24 and MongoDB 8.0.4.)
Step 2 → `new MongoClient(uri, options)`: `maxPoolSize` (default 100) controls concurrent sockets. For a replica set add `?replicaSet=rs0` or use `mongodb+srv://` for Atlas.
Step 3 → `await client.connect()` is optional in modern drivers (the first operation connects lazily), but calling it at startup makes failures show up early.
Step 4 → `client.db('name').collection('name')` gives a handle. These calls are cheap and do not hit the network.
Step 5 → Run operations; each returns a Promise. `find()` returns a **cursor** (use `.toArray()`, `for await`, `.limit()`, `.sort()`, `.project()`).
Step 6 → On shutdown call `client.close()`. Do **not** create a client per request.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `npm install mongodb`। (यहाँ Node v24 और MongoDB 8.0.4 पर test किया।)
Step 2 → `new MongoClient(uri, options)`: `maxPoolSize` (default 100) एक साथ चलने वाले sockets तय करता है। Replica set के लिए `?replicaSet=rs0` जोड़ो या Atlas के लिए `mongodb+srv://` इस्तेमाल करो।
Step 3 → आधुनिक drivers में `await client.connect()` optional है (पहला operation lazily connect कर देता है), फिर भी startup पर call करने से failures जल्दी दिखते हैं।
Step 4 → `client.db('name').collection('name')` से handle मिलता है। ये calls सस्ती हैं और network नहीं छूतीं।
Step 5 → Operations चलाओ; हर एक Promise देता है। `find()` **cursor** देता है (`.toArray()`, `for await`, `.limit()`, `.sort()`, `.project()` इस्तेमाल करो)।
Step 6 → Shutdown पर `client.close()`। हर request पर client **मत** बनाओ।

---

## 🟡 Real World Example
**Razorpay's** internal reporting job needs raw speed and exact control: it reads millions of settlement documents using a cursor, groups with an aggregation pipeline, and writes with `bulkWrite`. They do not want ODM overhead (hydrating documents into Mongoose objects), so they use the native driver. The same company may use Mongoose in a small admin CRUD service where validation matters more than speed. The choice is per service.

## 🟡 Real Example Hindi mein
**Razorpay** का internal reporting job raw speed और exact control चाहता है: वह cursor से लाखों settlement documents पढ़ता है, aggregation pipeline से group करता है और `bulkWrite` से लिखता है। उन्हें ODM का overhead (documents को Mongoose objects में hydrate करना) नहीं चाहिए, इसलिए native driver। वही company छोटे admin CRUD service में Mongoose इस्तेमाल कर सकती है जहाँ speed से ज़्यादा validation ज़रूरी है। चुनाव service के हिसाब से होता है।

---

## 💻 Code Example — Basic

```javascript
// native-basic.js   (npm install mongodb)  — output below is from a real run
const { MongoClient, ObjectId } = require('mongodb');

(async () => {
  // One client = one connection pool; reuse it for the whole app lifetime
  const client = new MongoClient('mongodb://127.0.0.1:27116/?replicaSet=rs0', { maxPoolSize: 20 });
  await client.connect();                              // fail fast if the server is unreachable
  const db = client.db('native_demo');                 // database handle (cheap, no network call)
  await db.dropDatabase();                             // clean slate for the demo
  const items = db.collection('menuItems');            // collection handle (created lazily on first write)

  // Unique compound index: the same dish cannot be added twice for a restaurant
  await items.createIndex({ restaurantId: 1, name: 1 }, { unique: true });

  // CREATE one document — driver adds an ObjectId _id when you do not supply one
  const r = await items.insertOne({ name: 'Paneer Tikka', price: 220, restaurantId: 'rest-101' });
  console.log('insertedId is ObjectId:', r.insertedId instanceof ObjectId);
  // Output: insertedId is ObjectId: true

  // CREATE many documents in one round trip
  const many = await items.insertMany([
    { name: 'Naan', price: 50, restaurantId: 'rest-101' },
    { name: 'Dal',  price: 180, restaurantId: 'rest-101' },
  ]);
  console.log('insertedCount:', many.insertedCount);
  // Output: insertedCount: 2

  // READ with projection + sort — find() returns a cursor, toArray() drains it
  console.log(await items.find({ restaurantId: 'rest-101' })
    .project({ _id: 0, name: 1, price: 1 })            // include only name and price
    .sort({ price: 1 })                                // cheapest first
    .toArray());
  // Output: [ { name: 'Naan', price: 50 }, { name: 'Dal', price: 180 }, { name: 'Paneer Tikka', price: 220 } ]

  // UPDATE — $set changes only the listed field
  const u = await items.updateOne({ name: 'Naan' }, { $set: { price: 55 } });
  console.log('matched/modified:', u.matchedCount, u.modifiedCount);
  // Output: matched/modified: 1 1

  // THE ObjectId TRAP: a string never equals an ObjectId
  console.log('byStringId:', await items.findOne({ _id: String(r.insertedId) }));
  // Output: byStringId: null
  console.log('byObjectId:', (await items.findOne({ _id: new ObjectId(String(r.insertedId)) })).name);
  // Output: byObjectId: Paneer Tikka

  await client.close();                                // release sockets
})();
```

## 💻 Code Example — Advanced

```javascript
// native-advanced.js — duplicate errors, unordered bulk inserts, aggregation, bad ids
const { MongoClient, ObjectId } = require('mongodb');

(async () => {
  const client = new MongoClient('mongodb://127.0.0.1:27116/?replicaSet=rs0');
  const items = client.db('native_demo').collection('menuItems');   // same data as Basic example

  // 1) DUPLICATE KEY on a single insert: error.code 11000, error.name MongoServerError
  try {
    await items.insertOne({ name: 'Naan', price: 1, restaurantId: 'rest-101' });
  } catch (e) {
    console.log('code', e.code, e.name);
    // Output: code 11000 MongoServerError
  }

  // 2) UNORDERED bulk insert: a failure does not stop the rest ('Roti' still goes in)
  try {
    await items.insertMany(
      [ { name: 'Naan', restaurantId: 'rest-101' },            // duplicate -> fails
        { name: 'Roti', price: 20, restaurantId: 'rest-101' } ], // valid -> succeeds
      { ordered: false });
  } catch (e) {
    console.log('bulk code', e.code, 'inserted', e.result.insertedCount);
    // Output: bulk code 11000 inserted 1
  }

  // 3) AGGREGATION is passed as an array of stage objects (same as the shell)
  console.log(await items.aggregate([
    { $group: { _id: '$restaurantId', avg: { $avg: '$price' }, n: { $sum: 1 } } }
  ]).toArray());
  // Output: [ { _id: 'rest-101', avg: 118.75, n: 4 } ]   (Paneer 220 + Naan 55 + Dal 180 + Roti 20 = 475 / 4)

  // 4) Invalid ObjectId strings throw BEFORE reaching the server
  try { new ObjectId('abc'); } catch (e) { console.log('bad id:', e.name); }
  // Output: bad id: BSONError

  // 5) CURSOR streaming — handles millions of docs without loading everything into memory
  for await (const doc of items.find({}, { projection: { name: 1 } })) {
    // each iteration fetches from the cursor's batch; process one at a time
    void doc;
  }
  await client.close();
})();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Express + native driver: connect ONCE, then start listening
const express = require('express');
const { MongoClient, ObjectId } = require('mongodb');

const app = express();
app.use(express.json());

const client = new MongoClient(process.env.MONGO_URI || 'mongodb://127.0.0.1:27017');
let menu;   // collection handle shared by all requests

app.get('/api/menu/:restaurantId', async (req, res, next) => {
  try {
    res.json(await menu.find({ restaurantId: req.params.restaurantId }).limit(50).toArray());
  } catch (err) { next(err); }                       // forward to the error handler
});

app.get('/api/item/:id', async (req, res, next) => {
  if (!ObjectId.isValid(req.params.id)) return res.status(400).json({ error: 'Invalid id' });
  try {
    const item = await menu.findOne({ _id: new ObjectId(req.params.id) });   // convert string -> ObjectId
    item ? res.json(item) : res.status(404).json({ error: 'Not found' });
  } catch (err) { next(err); }
});

app.use((err, req, res, next) => {                   // central error handling
  if (err.code === 11000) return res.status(409).json({ error: 'Duplicate' });
  res.status(500).json({ error: 'Server error' });
});

(async () => {
  await client.connect();
  menu = client.db('zomato').collection('menuItems');
  const server = app.listen(3000, () => console.log('API ready'));
  // graceful shutdown: stop HTTP first, then close the pool
  process.on('SIGTERM', () => server.close(() => client.close()));
})();
// Mongoose equivalent is in the next topic (82); it wraps this same driver internally.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: New `MongoClient` per request
```javascript
// Wrong — a fresh pool and TCP+TLS+auth handshake on every request; server runs out of connections
app.get('/x', async (req, res) => { const c = new MongoClient(uri); await c.connect(); /* ... */ });

// Right — create once at module/startup level and share
const client = new MongoClient(uri);
```

❌ Mistake 2: Querying `_id` with a plain string
```javascript
// Wrong — returns null silently (tested above)
await items.findOne({ _id: req.params.id });

// Right
await items.findOne({ _id: new ObjectId(req.params.id) });
```

❌ Mistake 3: Forgetting `await ... .toArray()` on `find()`
✅ Correct: `find()` returns a cursor, not an array. `res.json(items.find(...))` sends garbage; always `await cursor.toArray()` (or iterate it).

---

## 🧠 Tricky Interview Question

**Q:** `insertMany([a, b, c], { ordered: true })` where `b` violates a unique index. What is in the collection afterwards, and what changes with `ordered: false`?

**Answer:** With the default `ordered: true` the server stops at the first error: `a` is inserted, `b` fails, `c` is **never attempted**, so only `a` exists. With `ordered: false` the server continues past the failure: `a` and `c` are inserted and `b` is reported in the `writeErrors` of the thrown `MongoBulkWriteError`. In our run, `insertMany([dupNaan, Roti], { ordered: false })` threw code 11000 and still inserted 1 document (`Roti`). Neither mode rolls back what already succeeded; for all-or-nothing you need a transaction.

---

## ⚫ Interview Questions + Answers

Q1: What does `MongoClient` represent and how many should an app have?
A1: A client represents connections to a deployment (standalone/replica set/sharded cluster), including a pool per server and background monitoring. One per process is the rule; share it across requests.

Q2: Is `client.connect()` mandatory?
A2: Not in modern driver versions (it connects lazily on the first operation), but calling it at startup surfaces bad URIs and network errors immediately instead of on the first user request.

Q3: What is a cursor and why not always `toArray()`?
A3: `find()` returns a lazy cursor that fetches in batches. `toArray()` loads all results in memory, which is dangerous for large results. Use `for await (const doc of cursor)` or `limit()`/pagination.

Q4: How do you detect duplicate-key errors?
A4: Catch the error and check `err.code === 11000` (a `MongoServerError`). For bulk writes the error is a `MongoBulkWriteError` which still carries `code: 11000` and `result.insertedCount`.

Q5: Native driver vs Mongoose?
A5: Native: thin, faster, no schema, you validate yourself, full access to every feature immediately. Mongoose: schemas, validation, middleware, populate, casting, at the cost of hydration overhead and an extra abstraction. Mongoose uses the native driver underneath.

---

## 🔷 When to Use + When Not to Use
✅ Use the native driver when:
- You need maximum performance or newest server features right away
- Writing scripts, ETL, migrations, high-volume ingestion
- You already validate with MongoDB `$jsonSchema` or another library (Zod, Joi)

❌ Prefer Mongoose when:
- Team wants shared schemas, validation, defaults and hooks in code
- You want populate and convenient model methods
- Many developers touch the same collections and need guard rails

---

## 📊 Visual Diagram
```
NATIVE DRIVER FLOW
──────────────────────────────────────────────────────
 Node app
   │  new MongoClient(uri, {maxPoolSize})   (ONE per process)
   ▼
 ┌──────── connection pool ────────┐        ┌──────────────┐
 │ socket 1 │ socket 2 │ ... │ N  │ ◄────► │ mongod / rs  │
 └─────────────────────────────────┘        └──────────────┘
   │ client.db('app')
   ▼
 Db ── collection('menuItems') ── insertOne / insertMany
                               ├─ find().project().sort().toArray()   (cursor)
                               ├─ updateOne / updateMany ($set,$inc)
                               ├─ deleteOne / deleteMany
                               └─ aggregate([ ...stages ]).toArray()
 Errors: e.code === 11000 → duplicate key
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MongoClient | Driver entry point owning the pool | Pool का मालिक driver entry point |
| Connection pool | Reusable set of sockets | दोबारा इस्तेमाल होने वाले sockets का set |
| Cursor | Lazy iterator over query results | Query results पर lazy iterator |
| ObjectId | 12-byte default `_id` type | 12-byte default `_id` type |
| `ordered` | Stop at first bulk error or continue | Bulk में पहली error पर रुकना या जारी रखना |
| Error 11000 | Duplicate key violation | Duplicate key उल्लंघन |
| Projection | Choose which fields to return | कौन से fields लौटें यह चुनना |

---

## ⚡ 3-Line Summary
English:
1. The `mongodb` driver gives you a `MongoClient` with a built-in connection pool; create exactly one and reuse it.
2. Convert id strings with `new ObjectId()`, drain cursors properly, and catch `err.code === 11000` for duplicates.
3. It has no schema layer; add validation yourself or use Mongoose on top.

Hindi:
1. `mongodb` driver आपको built-in connection pool वाला `MongoClient` देता है; बस एक बनाओ और reuse करो।
2. Id strings को `new ObjectId()` से convert करो, cursors को सही तरह drain करो और duplicates के लिए `err.code === 11000` पकड़ो।
3. इसमें schema layer नहीं है; validation खुद जोड़ो या ऊपर Mongoose इस्तेमाल करो।

---

## ➡️ Next Topic
**82. Mongoose Basics — Connect + Schema + Model** — adding schemas, casting and models on top of this driver.
