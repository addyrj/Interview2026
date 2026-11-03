# 89. Mongoose Indexes and Performance
# हिंदी में: Mongoose Indexes और Performance

---

## 🔵 Simple Definition (English)
In Mongoose you declare indexes **in the schema** (`{ unique: true }` / `index: true` on a path, or `schema.index({...}, options)` for compound, text, TTL and partial indexes). Mongoose then asks MongoDB to build them (`autoIndex`) when the model initialises. Performance work means choosing indexes that match your queries, verifying them with `.explain('executionStats')`, and using tools like `lean()`, `select()`, pagination and `bulkWrite` to keep the app side cheap.

## 🔵 सरल परिभाषा (Hindi)
Mongoose में indexes **schema में** declare होते हैं (path पर `{ unique: true }` / `index: true`, या compound, text, TTL और partial indexes के लिए `schema.index({...}, options)`)। Model initialise होते समय Mongoose MongoDB से उन्हें बनाने को कहता है (`autoIndex`)। Performance का काम है अपनी queries से मेल खाते indexes चुनना, `.explain('executionStats')` से उन्हें जाँचना, और app की तरफ का खर्च कम रखने के लिए `lean()`, `select()`, pagination और `bulkWrite` जैसे औज़ार इस्तेमाल करना।

---

## 🔴 Problem it Solves
Without an index, MongoDB performs a **COLLSCAN**: it reads every document to answer a query. That is fine for 1,000 documents and a disaster for 10 million. Keeping index definitions in the schema means they are versioned in git next to the fields they serve, and every environment gets the same indexes. But auto-building indexes in production on huge collections can hurt the cluster, so you also need to know how to control it (`autoIndex`, `syncIndexes`, migrations).

## 🔴 यह क्यों बना? (Hindi)
Index के बिना MongoDB **COLLSCAN** करता है: query का जवाब देने के लिए हर document पढ़ता है। 1,000 documents पर ठीक, 1 करोड़ पर आपदा। Index definitions schema में रखने से वे git में उन्हीं fields के पास version होती हैं जिनकी वे सेवा करती हैं और हर environment को वही indexes मिलते हैं। पर production में विशाल collections पर indexes अपने आप बनाना cluster को नुकसान पहुँचा सकता है, इसलिए नियंत्रण भी आना चाहिए (`autoIndex`, `syncIndexes`, migrations)।

---

## 🟢 How it Works — Step by Step

Step 1 → Field-level: `sku: { type: String, unique: true }` or `index: true`. Schema-level: `schema.index({ city: 1, status: 1, placedAt: -1 })`.
Step 2 → Special types: text `schema.index({ title: 'text' })`, TTL `schema.index({ sessionAt: 1 }, { expireAfterSeconds: 3600 })`, partial `schema.index({ status: 1 }, { partialFilterExpression: { status: 'ACTIVE' }, name: 'active_only' })`, sparse, hashed, 2dsphere.
Step 3 → On model compile Mongoose calls `Model.init()` which runs `createIndex` for each (unless `autoIndex: false`). `await Model.init()` waits for it. Our run listed: `_id_, sku_1, city_1_status_1_placedAt_-1, title_text, sessionAt_1, active_only`.
Step 4 → Check what exists: `await Model.collection.indexes()`.
Step 5 → Compare to the DB: `await Model.diffIndexes()` shows `toDrop` / `toCreate`; `await Model.syncIndexes()` makes the DB match the schema (**drops** indexes not in the schema; be careful).
Step 6 → Verify use: `Model.find(...).explain('executionStats')`. Look at `winningPlan` (IXSCAN good, COLLSCAN bad), `totalKeysExamined`, `totalDocsExamined`, `nReturned`.
Step 7 → Rule for compound indexes (**ESR**): Equality fields first, then Sort fields, then Range fields. Verified: `{ city, status, placedAt:-1 }` served `find({city, status}).sort({placedAt:-1})` with **no SORT stage** (`FETCH -> IXSCAN`).
Step 8 → Production: set `autoIndex: false` (or use `mongoose.set('autoIndex', false)`), and create indexes through migrations/deploy scripts, because building an index on a huge collection takes time and resources.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Field-level: `sku: { type: String, unique: true }` या `index: true`। Schema-level: `schema.index({ city: 1, status: 1, placedAt: -1 })`।
Step 2 → विशेष प्रकार: text `schema.index({ title: 'text' })`, TTL `schema.index({ sessionAt: 1 }, { expireAfterSeconds: 3600 })`, partial `schema.index({ status: 1 }, { partialFilterExpression: { status: 'ACTIVE' }, name: 'active_only' })`, sparse, hashed, 2dsphere।
Step 3 → Model compile होने पर Mongoose `Model.init()` call करता है जो हर index के लिए `createIndex` चलाता है (जब तक `autoIndex: false` न हो)। `await Model.init()` इसका इंतज़ार करता है। हमारे run में सूची आई: `_id_, sku_1, city_1_status_1_placedAt_-1, title_text, sessionAt_1, active_only`।
Step 4 → क्या मौजूद है देखो: `await Model.collection.indexes()`।
Step 5 → DB से तुलना: `await Model.diffIndexes()` `toDrop` / `toCreate` दिखाता है; `await Model.syncIndexes()` DB को schema जैसा बनाता है (schema में न होने वाले indexes **drop** कर देता है; सावधान रहो)।
Step 6 → Use की जाँच: `Model.find(...).explain('executionStats')`। `winningPlan` (IXSCAN अच्छा, COLLSCAN बुरा), `totalKeysExamined`, `totalDocsExamined`, `nReturned` देखो।
Step 7 → Compound indexes का नियम (**ESR**): पहले Equality fields, फिर Sort fields, फिर Range fields। Verified: `{ city, status, placedAt:-1 }` ने `find({city, status}).sort({placedAt:-1})` को **बिना SORT stage** के (`FETCH -> IXSCAN`) चलाया।
Step 8 → Production: `autoIndex: false` रखो और indexes migrations/deploy scripts से बनाओ, क्योंकि विशाल collection पर index बनाने में समय और resources लगते हैं।

---

## 🟡 Real World Example
Flipkart's order-search service queries `{ city, status }` sorted by newest `placedAt` thousands of times per second. Without the compound index `{ city: 1, status: 1, placedAt: -1 }` MongoDB scans the whole `orders` collection and sorts in memory. After adding it, the query reads only the matching index range in already sorted order. The team keeps `autoIndex: false` in production; index changes ship as migration scripts that build the index in the background on the secondary-safe rolling schedule, and `diffIndexes()` runs in CI to catch drift between schema and database.

## 🟡 Real Example Hindi mein
Flipkart की order-search service `{ city, status }` पर सबसे नए `placedAt` के क्रम में प्रति सेकंड हज़ारों queries चलाती है। Compound index `{ city: 1, status: 1, placedAt: -1 }` के बिना MongoDB पूरी `orders` collection scan करता है और memory में sort करता है। Index जोड़ने के बाद query सिर्फ matching index range को पहले से sorted क्रम में पढ़ती है। Team production में `autoIndex: false` रखती है; index बदलाव migration scripts से जाते हैं, और CI में `diffIndexes()` चलता है ताकि schema और database में drift पकड़ा जाए।

---

## 💻 Code Example — Basic

```javascript
// indexes-basic.js — real output (Mongoose 9, MongoDB 8.0.4), 20,000 generated docs
const mongoose = require('mongoose'); const { Schema } = mongoose;

(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');
  await mongoose.connection.dropDatabase();

  const s = new Schema({
    sku: { type: String, unique: true },                    // unique index sku_1
    city: String, status: String, price: Number, placedAt: Date, title: String, tags: [String],
  });
  s.index({ city: 1, status: 1, placedAt: -1 });            // compound: ESR = equality, equality, sort
  s.index({ title: 'text' });                               // text search index
  s.index({ sessionAt: 1 }, { expireAfterSeconds: 3600 });  // TTL: delete docs 1 hour after sessionAt
  s.index({ status: 1 }, { partialFilterExpression: { status: 'ACTIVE' }, name: 'active_only' }); // only ACTIVE docs indexed

  const P = mongoose.model('Idx', s);
  await P.init();                                           // wait until indexes are built
  console.log((await P.collection.indexes()).map(i => i.name).join('\n'));
  // Output:
  // _id_
  // sku_1
  // city_1_status_1_placedAt_-1
  // title_text
  // sessionAt_1
  // active_only

  // Generate data: 20 cities x 2 statuses
  const docs = [];
  for (let i = 0; i < 20000; i++)
    docs.push({ sku: 'S' + i, city: 'C' + (i % 20), status: i % 2 ? 'ACTIVE' : 'DONE',
                price: i, placedAt: new Date(2025, 0, 1 + (i % 28)), title: 'item ' + i });
  await P.insertMany(docs);

  // Query that matches the compound index (ESR): equality, equality, sort
  const ex = await P.find({ city: 'C3', status: 'ACTIVE' }).sort({ placedAt: -1 }).explain('executionStats');
  const es = ex.executionStats;
  console.log('stage:', ex.queryPlanner.winningPlan.stage, '/', ex.queryPlanner.winningPlan.inputStage?.stage,
              'keysExamined', es.totalKeysExamined, 'docsExamined', es.totalDocsExamined, 'returned', es.nReturned);
  // Output: stage: FETCH / IXSCAN keysExamined 1000 docsExamined 1000 returned 1000
  //         (keys == docs == returned: perfectly selective; no SORT stage because the index is already sorted)

  // Query on an unindexed field
  const ex2 = await P.find({ price: 5 }).explain('executionStats');
  console.log('no index ->', ex2.queryPlanner.winningPlan.stage, 'docsExamined', ex2.executionStats.totalDocsExamined);
  // Output: no index -> COLLSCAN docsExamined 20000       (read every document to return one)
  await mongoose.disconnect();
})();
```

## 💻 Code Example — Advanced

```javascript
// indexes-advanced.js — covered queries, drift detection, production settings
const mongoose = require('mongoose');
(async () => {
  // Production-style connection: do not build indexes automatically
  mongoose.set('autoIndex', false);                  // must be set BEFORE models are compiled to take effect
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');
  const P = mongoose.model('Idx');                   // compiled in the Basic example

  // 1) COVERED QUERY: only indexed fields requested, _id excluded => no document fetch at all
  const ex3 = await P.find({ city: 'C3' }).select('city -_id')
    .hint({ city: 1, status: 1, placedAt: -1 })      // force this index (hint is for diagnosis, not routine use)
    .explain('executionStats');
  console.log('covered docsExamined:', ex3.executionStats.totalDocsExamined);
  // Output: covered docsExamined: 0

  // 2) DRIFT DETECTION: compare schema indexes with the database
  console.log('diff:', JSON.stringify(await P.diffIndexes()));
  // Output: diff: {"toDrop":[],"toCreate":[]}      (empty = schema and DB agree)

  // 3) syncIndexes: make DB match the schema. Returns names of DROPPED indexes. Use in migrations, not on every boot.
  console.log('syncIndexes dropped:', await P.syncIndexes());
  // Output: syncIndexes dropped: []

  // 4) Cheap-app-side performance checklist (code, not output):
  //   - .lean() for read-only responses
  //   - .select('a b') to fetch only needed fields (and covered queries)
  //   - paginate with a range on an indexed field instead of big skip():
  //       Model.find({ _id: { $lt: lastId } }).sort({ _id: -1 }).limit(20)
  //   - bulkWrite for many writes: Model.bulkWrite([{ updateOne: { filter, update } }, ...])
  //   - set maxTimeMS to protect the DB: Model.find(q).maxTimeMS(2000)
  //   - slow queries: mongoose.set('debug', true) in dev to print every command
  const lastId = (await P.findOne().sort({ _id: -1 }).lean())._id;
  await P.find({ _id: { $lt: lastId } }).sort({ _id: -1 }).limit(20).select('sku').lean().maxTimeMS(2000);
  await mongoose.disconnect();
})();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');

// In production: no automatic index builds on every app start
mongoose.set('autoIndex', process.env.NODE_ENV !== 'production');

const orderSchema = new mongoose.Schema({
  city: String, status: String, placedAt: { type: Date, default: Date.now }, total: Number,
});
orderSchema.index({ city: 1, status: 1, placedAt: -1 });          // matches the list endpoint below
const Order = mongoose.model('Order', orderSchema);

const app = express();

// Cursor pagination: stable and uses the index (skip(100000) would walk 100000 index entries)
app.get('/api/orders', async (req, res) => {
  const { city, status, before } = req.query;                       // before = last placedAt of previous page
  const filter = { city, status };                                  // equality first (ESR)
  if (before) filter.placedAt = { $lt: new Date(before) };          // range last
  const rows = await Order.find(filter)
    .sort({ placedAt: -1 }).limit(20)                               // sort field = last index field
    .select('city status total placedAt').lean().maxTimeMS(2000);
  res.json({ rows, next: rows.length ? rows[rows.length - 1].placedAt : null });
});

// Index admin script (run in deploy pipeline, not in the web process):
//   await Order.syncIndexes();       // aligns DB with schema  (drops extra indexes!)
//   console.log(await Order.diffIndexes());
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Wrong field order in a compound index
```javascript
// Wrong — range field first; the sort cannot use the index efficiently
schema.index({ placedAt: -1, city: 1, status: 1 });

// Right — ESR: equality (city, status) then sort/range (placedAt)
schema.index({ city: 1, status: 1, placedAt: -1 });
```

❌ Mistake 2: Relying on `autoIndex` in production and never checking
```javascript
// Wrong — a big index build starts at deploy time and slows the app; failures are silent in logs
mongoose.connect(uri);   // autoIndex defaults to true

// Right — autoIndex:false in prod; build indexes in a controlled migration; run diffIndexes() in CI
```

❌ Mistake 3: Indexing everything
✅ Correct: every index slows writes and uses RAM. Index the fields your real queries filter/sort on, remove unused ones (check `$indexStats`), and prefer one compound index over many single-field ones.

---

## 🧠 Tricky Interview Question

**Q:** Your explain output shows `IXSCAN` yet the query is still slow: `totalKeysExamined: 500000`, `nReturned: 20`. What is wrong?

**Answer:** An index was used, but it is **not selective for this query**: MongoDB walked 500,000 index entries to find 20 matching results. Typical causes: the compound index has the wrong order (range or low-cardinality field first), the query filters on a field that is only the second key without an equality on the first, or the sort field is not at the end so the server filters keys one by one. The ratio `nReturned / totalKeysExamined` (ideally near 1) is the health metric. Fix by reordering to ESR, adding a field that narrows the scan, or using a partial index. Verified contrast: our good query had keys 1000 = docs 1000 = returned 1000.

---

## ⚫ Interview Questions + Answers

Q1: What does `unique: true` really do in Mongoose?
A1: It builds a MongoDB unique index (`createIndex` with `unique`). It is not a Mongoose validator, so duplicates raise a MongoServerError with code 11000. Existing duplicate data makes the index build fail.

Q2: How do you check whether a query uses an index?
A2: `.explain('executionStats')`. Look for `IXSCAN` vs `COLLSCAN` in `winningPlan`, then compare `totalKeysExamined`, `totalDocsExamined`, and `nReturned`. A `SORT` stage means an in-memory sort.

Q3: What is a covered query?
A3: One where all returned and filtered fields are in the index, so MongoDB answers from the index alone (`totalDocsExamined: 0`, verified). Requires projecting out `_id` (unless in the index) and only selecting indexed fields.

Q4: `syncIndexes()` vs `ensureIndexes()/init()`?
A4: `init()` only creates missing indexes. `syncIndexes()` also **drops** indexes in the database that are not in the schema, so use it deliberately (migrations), never blindly in a multi-service database.

Q5: Why is `skip()` a problem for deep pagination?
A5: The server still walks past all skipped entries; `skip(100000)` is O(n). Use range-based (cursor) pagination: filter by the last seen indexed value with `limit()`.

---

## 🔷 When to Use + When Not to Use
✅ Add indexes when:
- A query filters/sorts on the same fields frequently and the collection is large
- You need uniqueness (`unique`) or automatic expiry (TTL)
- `explain()` shows COLLSCAN or a large examined/returned ratio

❌ Avoid / be careful when:
- Write-heavy collections where each extra index adds write cost
- Low-cardinality single-field indexes (e.g., boolean) that barely narrow results
- Auto-building in production on very large collections without a plan

---

## 📊 Visual Diagram
```
HOW TO READ explain('executionStats')
──────────────────────────────────────────────────────
 winningPlan:  FETCH                      winningPlan: COLLSCAN
                 └─ IXSCAN  (good)                      (reads every doc: bad at scale)

 totalKeysExamined  ─┐
 totalDocsExamined  ─┼─ compare with nReturned (want ≈ equal)
 nReturned          ─┘

 Compound index {city:1, status:1, placedAt:-1}
    city = 'C3'   ┐ Equality
    status='ACTIVE'┘                    ──► seek straight to the range
    sort placedAt -1 ── Sort            ──► already ordered, no SORT stage
    placedAt < X    ── Range (last)
 ESR = Equality → Sort → Range
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Index | Structure that speeds queries | Queries तेज़ करने वाली structure |
| COLLSCAN | Full collection scan | पूरी collection scan |
| IXSCAN | Index scan | Index scan |
| ESR rule | Equality, Sort, Range order | Equality, Sort, Range क्रम |
| Covered query | Answered from index alone | सिर्फ index से जवाब |
| `syncIndexes` | Align DB indexes to schema | DB indexes को schema से मिलाना |
| TTL index | Auto-delete after time | समय बाद अपने आप delete |

---

## ⚡ 3-Line Summary
English:
1. Declare indexes in the schema (`unique`, `schema.index`, TTL, partial, text) and verify them with `explain('executionStats')`.
2. Follow ESR for compound indexes, compare keys/docs examined with returned, and use covered queries where possible.
3. Disable `autoIndex` in production, manage indexes via migrations (`diffIndexes`, `syncIndexes`), and use `lean`, `select`, cursor pagination.

Hindi:
1. Indexes schema में declare करो (`unique`, `schema.index`, TTL, partial, text) और `explain('executionStats')` से जाँचो।
2. Compound indexes के लिए ESR अपनाओ, examined keys/docs की तुलना returned से करो, और जहाँ हो सके covered queries इस्तेमाल करो।
3. Production में `autoIndex` बंद रखो, indexes migrations (`diffIndexes`, `syncIndexes`) से सँभालो, और `lean`, `select`, cursor pagination इस्तेमाल करो।

---

## ➡️ Next Topic
**90. Next in the series** — continue with the following topic in the folder listing (07-mongoose-nodejs is complete at this note).
