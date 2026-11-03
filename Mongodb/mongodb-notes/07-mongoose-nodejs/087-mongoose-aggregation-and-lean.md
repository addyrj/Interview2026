# 87. Mongoose Aggregation + lean()
# हिंदी में: Mongoose Aggregation + lean()

---

## 🔵 Simple Definition (English)
`Model.aggregate([...stages])` runs a MongoDB **aggregation pipeline** through Mongoose and returns **plain JavaScript objects**. `.lean()` on a normal query (`find`, `findOne`) tells Mongoose to skip creating full Mongoose documents and return plain objects too. Both are the "fast read" tools: no hydration, no virtuals, no change tracking, no `save()`. The big difference is that `aggregate()` does **no casting** of your pipeline values, while `find()` casts filters to schema types.

## 🔵 सरल परिभाषा (Hindi)
`Model.aggregate([...stages])` Mongoose के ज़रिए MongoDB की **aggregation pipeline** चलाता है और **plain JavaScript objects** लौटाता है। सामान्य query (`find`, `findOne`) पर `.lean()` Mongoose को बताता है कि पूरे Mongoose documents न बनाओ, plain objects लौटाओ। दोनों "fast read" के औज़ार हैं: न hydration, न virtuals, न change tracking, न `save()`। बड़ा अंतर यह है कि `aggregate()` आपकी pipeline values को **cast नहीं करता**, जबकि `find()` filters को schema types में cast करता है।

---

## 🔴 Problem it Solves
Dashboards, reports and leaderboards need grouping, summing and joining over many documents: doing that by loading everything into Node and looping is slow and memory hungry. Aggregation lets the database do the heavy lifting and return a small result. Separately, read-only endpoints that return thousands of documents waste CPU and memory creating full Mongoose documents (with getters, setters, hooks and change tracking) that are immediately serialised to JSON; `lean()` removes that overhead.

## 🔴 यह क्यों बना? (Hindi)
Dashboards, reports और leaderboards को कई documents पर grouping, sum और join चाहिए: सब कुछ Node में load करके loop करना slow और memory-heavy है। Aggregation भारी काम database से करवाता है और छोटा result लौटाता है। अलग से, read-only endpoints जो हज़ारों documents लौटाते हैं, पूरे Mongoose documents (getters, setters, hooks और change tracking के साथ) बनाने में CPU और memory बर्बाद करते हैं जबकि वे तुरंत JSON में बदल जाते हैं; `lean()` यह overhead हटा देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `Order.aggregate([ {$match}, {$group}, {$sort} ])` returns a thenable `Aggregate`; `await` it to get an **array of plain objects**.
Step 2 → Put `$match` (and `$sort`/`$limit` that can use indexes) **first** so the pipeline touches fewer documents; the optimizer helps but write it right.
Step 3 → **No casting in aggregate**: `find({ userId: '65...' })` casts the string to an `ObjectId` because the schema says so; `aggregate([{ $match: { userId: '65...' } }])` does **not**. Verified: find with string id -> 4 docs; aggregate with string -> 0; aggregate with `new ObjectId()` -> 4.
Step 4 → Hooks: `pre('aggregate')` can modify the pipeline (`this.pipeline().unshift(...)`). Query middleware (like `pre('find')`) does **not** run for aggregate.
Step 5 → `lean()`: `Model.find().lean()` returns POJOs: `_id` stays an `ObjectId`, but there are no methods (`save` is `undefined`), no virtuals, no defaults applied at read, no getters.
Step 6 → Use `.explain('executionStats')` on aggregate to check index use and `allowDiskUse(true)` for pipelines exceeding the 100 MB per-stage memory limit.
Step 7 → For paginated results with a total count in one round trip use `$facet` (verified: `$count` inside a facet branch returned `[{ n: 20004 }]`).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `Order.aggregate([ {$match}, {$group}, {$sort} ])` एक thenable `Aggregate` देता है; `await` करने पर **plain objects का array** मिलता है।
Step 2 → `$match` (और index इस्तेमाल कर सकने वाले `$sort`/`$limit`) को **सबसे पहले** रखो ताकि pipeline कम documents छुए; optimizer मदद करता है पर सही लिखना आपका काम है।
Step 3 → **Aggregate में casting नहीं**: `find({ userId: '65...' })` string को `ObjectId` में cast करता है क्योंकि schema ऐसा कहता है; `aggregate([{ $match: { userId: '65...' } }])` **नहीं** करता। Verified: string id से find -> 4 docs; string से aggregate -> 0; `new ObjectId()` से aggregate -> 4।
Step 4 → Hooks: `pre('aggregate')` pipeline बदल सकता है (`this.pipeline().unshift(...)`)। Query middleware (जैसे `pre('find')`) aggregate पर **नहीं** चलता।
Step 5 → `lean()`: `Model.find().lean()` POJOs लौटाता है: `_id` `ObjectId` ही रहता है, पर methods नहीं (`save` `undefined`), virtuals नहीं, read पर defaults नहीं, getters नहीं।
Step 6 → Index use देखने के लिए aggregate पर `.explain('executionStats')` और 100 MB प्रति-stage memory limit पार करने वाली pipelines के लिए `allowDiskUse(true)`।
Step 7 → एक round trip में paginated results और total count के लिए `$facet` (verified: facet branch में `$count` ने `[{ n: 20004 }]` दिया)।

---

## 🟡 Real World Example
Zomato's **restaurant partner dashboard** shows "revenue per city for delivered orders this month, sorted descending". One `Order.aggregate` with `$match` (status + date), `$group` by city and `$sort` returns a handful of rows from millions of orders. Meanwhile the **order history API** returns the last 20 orders as JSON; it uses `find().lean()` because the response is serialised immediately and no `save()` is needed, cutting CPU per request and memory churn at peak dinner time.

## 🟡 Real Example Hindi mein
Zomato का **restaurant partner dashboard** "इस महीने delivered orders की city-wise revenue, घटते क्रम में" दिखाता है। एक `Order.aggregate`, जिसमें `$match` (status + date), city पर `$group` और `$sort` है, लाखों orders से कुछ rows लौटाता है। वहीं **order history API** आखिरी 20 orders JSON में लौटाती है; वह `find().lean()` इस्तेमाल करती है क्योंकि response तुरंत serialise होता है और `save()` नहीं चाहिए, जिससे dinner peak पर प्रति request CPU और memory churn घटता है।

---

## 💻 Code Example — Basic

```javascript
// aggregate-basic.js — real output (Mongoose 9, MongoDB 8.0.4)
const mongoose = require('mongoose'); const { Schema } = mongoose;

(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');
  await mongoose.connection.dropDatabase();

  const O = mongoose.model('Order', new Schema({
    city: String, status: String, total: Number,
    userId: Schema.Types.ObjectId, placedAt: Date,
  }));
  const uid = new mongoose.Types.ObjectId();
  await O.insertMany([
    { city: 'Pune',  status: 'DELIVERED', total: 500, userId: uid, placedAt: new Date('2025-01-05') },
    { city: 'Pune',  status: 'DELIVERED', total: 300, userId: uid, placedAt: new Date('2025-01-09') },
    { city: 'Delhi', status: 'CANCELLED', total: 900, userId: uid, placedAt: new Date('2025-01-09') },
    { city: 'Delhi', status: 'DELIVERED', total: 100, userId: uid, placedAt: new Date('2025-02-01') },
  ]);

  // Revenue and order count per city for delivered orders, biggest first
  console.log(await O.aggregate([
    { $match: { status: 'DELIVERED' } },                                      // WHERE  (first = fewer docs)
    { $group: { _id: '$city', revenue: { $sum: '$total' }, orders: { $sum: 1 } } }, // GROUP BY city
    { $sort: { revenue: -1 } },                                               // ORDER BY revenue DESC
  ]));
  // Output: [ { _id: 'Pune', revenue: 800, orders: 2 }, { _id: 'Delhi', revenue: 100, orders: 1 } ]

  // lean(): plain object vs full Mongoose document
  const doc  = await O.findOne({ city: 'Pune' });
  const lean = await O.findOne({ city: 'Pune' }).lean();
  console.log('doc has save:', typeof doc.save, '| lean has save:', typeof lean.save, '| lean _id type:', lean._id.constructor.name);
  // Output: doc has save: function | lean has save: undefined | lean _id type: ObjectId
  console.log('doc keys:', Object.keys(doc).slice(0, 3).join(','), '| lean keys:', Object.keys(lean).join(','));
  // Output: doc keys: $__,$isNew,_doc | lean keys: _id,city,status,total,userId,placedAt,__v
  await mongoose.disconnect();
})();
```

## 💻 Code Example — Advanced

```javascript
// aggregate-advanced.js — the casting trap, $facet, explain
const mongoose = require('mongoose');
(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');
  const O = mongoose.model('Order');                                   // from the Basic example
  const any = await O.findOne().lean(); const uid = any.userId;        // an ObjectId

  // 1) THE CASTING TRAP: find() casts, aggregate() does NOT
  console.log('find with string id:', (await O.find({ userId: String(uid) })).length);
  // Output: find with string id: 4         (Mongoose cast the string to ObjectId using the schema)
  console.log('aggregate with string id:', (await O.aggregate([{ $match: { userId: String(uid) } }])).length);
  // Output: aggregate with string id: 0    (string !== ObjectId inside the server, silently no match)
  console.log('aggregate with ObjectId:', (await O.aggregate([{ $match: { userId: new mongoose.Types.ObjectId(String(uid)) } }])).length);
  // Output: aggregate with ObjectId: 4     (always cast ids manually in pipelines)

  // 2) $facet: page of results + total count in ONE round trip
  const page = await O.aggregate([
    { $match: { status: 'DELIVERED' } },
    { $facet: {
        rows:  [ { $sort: { total: -1 } }, { $skip: 0 }, { $limit: 2 }, { $project: { _id: 0, city: 1, total: 1 } } ],
        count: [ { $count: 'n' } ],
    } },
  ]);
  console.log(page[0].rows, page[0].count);
  // Output: [ { city: 'Pune', total: 500 }, { city: 'Pune', total: 300 } ] [ { n: 3 } ]

  // 3) explain: confirm the plan (useful when a dashboard is slow)
  const plan = await O.aggregate([{ $match: { status: 'DELIVERED' } }]).explain('executionStats');
  console.log('has plan:', !!(plan.queryPlanner || plan.stages));          // Output: has plan: true

  // 4) Big pipelines: allow spilling to disk, set a time budget
  await O.aggregate([{ $group: { _id: '$city', n: { $sum: 1 } } }]).allowDiskUse(true).option({ maxTimeMS: 5000 });

  // 5) $lookup from Mongoose: collection name is the PLURAL lowercase name, not the model name
  // { $lookup: { from: 'users', localField: 'userId', foreignField: '_id', as: 'user' } }
  await mongoose.disconnect();
})();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const { Order } = require('./models');

const app = express();

// Report endpoint: heavy grouping happens in the DB; only a few rows cross the network
app.get('/api/reports/revenue-by-city', async (req, res) => {
  const from = new Date(req.query.from), to = new Date(req.query.to);   // convert query strings to Date yourself!
  if (isNaN(from) || isNaN(to)) return res.status(400).json({ error: 'Bad dates' });
  const rows = await Order.aggregate([
    { $match: { status: 'DELIVERED', placedAt: { $gte: from, $lt: to } } },   // must be real Date objects here
    { $group: { _id: '$city', revenue: { $sum: '$total' }, orders: { $sum: 1 } } },
    { $sort: { revenue: -1 } },
  ]);
  res.json(rows);
});

// Read endpoint: lean + projection + limit
app.get('/api/users/:id/orders', async (req, res) => {
  if (!mongoose.isValidObjectId(req.params.id)) return res.status(400).json({ error: 'Bad id' });
  const orders = await Order.find({ userId: req.params.id })       // find() casts the id string for us
    .select('city status total placedAt')                         // only needed fields
    .sort({ placedAt: -1 }).limit(20)
    .lean();                                                      // plain objects: cheaper to build and serialise
  res.json(orders);
});

// Paginated listing with total, one round trip
app.get('/api/orders', async (req, res) => {
  const page = Math.max(1, Number(req.query.page) || 1), size = 20;
  const [r] = await Order.aggregate([{ $facet: {
    rows: [{ $sort: { _id: -1 } }, { $skip: (page - 1) * size }, { $limit: size }],
    total: [{ $count: 'n' }],
  } }]);
  res.json({ rows: r.rows, total: r.total[0] ? r.total[0].n : 0 });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Passing id strings / date strings into `$match`
```javascript
// Wrong — no casting in aggregate: 0 results, no error (verified)
await Order.aggregate([{ $match: { userId: req.params.id } }]);

// Right
await Order.aggregate([{ $match: { userId: new mongoose.Types.ObjectId(req.params.id) } }]);
```

❌ Mistake 2: Using `lean()` and then calling document methods or expecting virtuals/defaults
```javascript
// Wrong
const o = await Order.findById(id).lean(); o.total = 5; await o.save();   // TypeError: o.save is not a function

// Right — use lean() only for read-only paths; for updates use updateOne or a normal doc
await Order.updateOne({ _id: id }, { total: 5 });
```

❌ Mistake 3: `$match` late in the pipeline
✅ Correct: filter first (`$match`), then `$group`. Matching after grouping forces MongoDB to group everything, ignoring indexes.

---

## 🧠 Tricky Interview Question

**Q:** Why does `Order.find({ userId: idString })` return 4 orders while `Order.aggregate([{ $match: { userId: idString } }])` returns 0 for exactly the same data?

**Answer:** Mongoose **casts** query filters using the schema (it knows `userId` is an `ObjectId`, so the string is converted). The aggregation pipeline is sent to the server **as is**; Mongoose does not know which stage fields correspond to schema paths (fields change shape between stages), so a string `"65..."` is compared against an `ObjectId` and nothing matches. No error is raised. Fix: convert ids to `new mongoose.Types.ObjectId(id)` and date strings to `Date` yourself before building the pipeline. The same applies to numbers sent as strings.

---

## ⚫ Interview Questions + Answers

Q1: What does `lean()` do and when would you avoid it?
A1: It returns plain JS objects instead of Mongoose documents, skipping hydration, virtuals, getters/setters, change tracking and defaults on read. It is quicker and uses less memory for read-only responses. Avoid it when you need `save()`, virtuals, methods, or populate-virtual behaviour without extra plugins.

Q2: Does `lean()` convert `_id` to a string?
A2: No. `_id` stays an `ObjectId` (we printed its constructor). JSON serialisation converts it to a string at response time.

Q3: Which hooks run for `aggregate()`?
A3: Only `aggregate` middleware (`schema.pre('aggregate')`). `find`/`findOne` query hooks do not run, so soft-delete filters must be repeated for pipelines.

Q4: How do you do pagination with a total count?
A4: `$facet` with a `rows` branch (`$sort`, `$skip`, `$limit`) and a `count` branch (`$count`) gives both in one query. Beware that `$facet` output is a single document (16 MB limit), so keep pages small. Alternatively run `countDocuments` and `find` in parallel.

Q5: How do you debug a slow pipeline?
A5: `.explain('executionStats')`, check that the first `$match`/`$sort` uses an index (`IXSCAN`), move `$match` earlier, project fields early, and use `allowDiskUse` for large `$group`/`$sort` stages.

---

## 🔷 When to Use + When Not to Use
✅ Use `aggregate()` when:
- Grouping, summing, bucketing, joining (`$lookup`) or reshaping data in the database
- Reports/dashboards over large collections

✅ Use `lean()` when:
- The result is read-only and serialised straight to JSON
- You return many documents per request

❌ Avoid when:
- `aggregate()`: simple lookups that `find()` handles (casting and hooks work there)
- `lean()`: you need virtuals, instance methods, or to modify and `save()` the document

---

## 📊 Visual Diagram
```
find() vs find().lean() vs aggregate()
──────────────────────────────────────────────────────
 find()          raw BSON → cast filter → HYDRATE Mongoose Document ($__, _doc, virtuals, save())
 find().lean()   raw BSON → cast filter → plain object  { _id:ObjectId, ...}   (fast)
 aggregate()     pipeline sent AS-IS (NO casting) → plain objects

 Pipeline:  [ $match ]──►[ $group ]──►[ $sort ]──►[ $limit ]
              │ index        │ in-memory (100MB/stage; allowDiskUse)
              └ keep FIRST

 Trap:  userId:"65.." (string)  vs  ObjectId("65..")  → aggregate matches 0 docs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Aggregation pipeline | Ordered data-processing stages | क्रमबद्ध data-processing stages |
| `lean()` | Return plain objects | Plain objects लौटाना |
| Hydration | Building Mongoose documents | Mongoose documents बनाना |
| Casting | Convert values to schema types | Values को schema types में बदलना |
| `$facet` | Multiple pipelines in one stage | एक stage में कई pipelines |
| `allowDiskUse` | Spill big stages to disk | बड़े stages को disk पर spill करना |
| POJO | Plain JavaScript object | साधारण JavaScript object |

---

## ⚡ 3-Line Summary
English:
1. `aggregate()` runs server-side pipelines and returns plain objects; `lean()` makes `find()` return plain objects too.
2. Aggregate does not cast: convert ids and dates yourself, or you will silently match nothing.
3. Use `lean()` only for read-only paths (no virtuals, no `save()`), and put `$match` first in pipelines.

Hindi:
1. `aggregate()` server-side pipelines चलाता है और plain objects लौटाता है; `lean()` `find()` को भी plain objects लौटाने वाला बनाता है।
2. Aggregate cast नहीं करता: ids और dates खुद convert करो, वरना चुपचाप कुछ match नहीं होगा।
3. `lean()` सिर्फ read-only paths पर इस्तेमाल करो (न virtuals, न `save()`), और pipelines में `$match` पहले रखो।

---

## ➡️ Next Topic
**88. Mongoose Transactions and Sessions** — multi-document ACID operations with `startSession` and `withTransaction`.
