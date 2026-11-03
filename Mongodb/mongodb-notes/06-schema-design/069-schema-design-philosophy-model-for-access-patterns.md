# 69. Schema Design Philosophy — Model for Access Patterns
# हिंदी में: Schema Design का Philosophy — Access Patterns के हिसाब से Model करो

---

## 🔵 Simple Definition (English)
In MongoDB you design the schema around **how your application reads and writes data** (its *access patterns*), not around abstract entities and normal forms. The rule of thumb from MongoDB's own guidance: **"Data that is accessed together should be stored together."** You list the queries first (what, how often, how fast), then choose document shapes, embedding/referencing and indexes that make the hot queries a **single indexed read**. The schema is flexible, but the *design* is still the most important performance decision.

## 🔵 सरल परिभाषा (Hindi)
MongoDB में schema इस हिसाब से design होता है कि आपकी application **data को कैसे पढ़ती और लिखती है** (*access patterns*), न कि abstract entities और normal forms के हिसाब से। MongoDB की अपनी guidance का rule: **"जो data साथ access होता है, उसे साथ store करो।"** पहले queries की list बनाओ (क्या, कितनी बार, कितनी तेज़), फिर document shape, embedding/referencing और indexes चुनो ताकि hot queries **एक indexed read** में हो जाएँ। Schema flexible है, फिर भी *design* सबसे ज़रूरी performance फ़ैसला है।

---

## 🔴 Problem it Solves
Developers from SQL often copy the ER diagram into collections: one collection per table, joins via `$lookup` everywhere. That works but turns every page load into N round trips or expensive joins, and wastes MongoDB's strength (a document is read/written **atomically** as one unit). The opposite error is also common: stuff everything into one giant document, hit the 16 MB limit and rewrite huge docs on small updates. Without a method, schemas become slow, unscalable and painful to change. The access-pattern method gives a repeatable process.

## 🔴 यह क्यों बना? (Hindi)
SQL से आए developers अक्सर ER diagram को ही collections में copy कर देते हैं: हर table की एक collection, और हर जगह `$lookup` joins। यह चलता है पर हर page load को N round trips या महंगे joins बना देता है, और MongoDB की ताक़त (document एक unit की तरह **atomically** पढ़ा/लिखा जाता है) बेकार जाती है। उल्टी गलती भी आम है: सब कुछ एक विशाल document में भर देना, 16 MB limit छू लेना और छोटे updates पर भी बड़े documents rewrite करना। Method के बिना schema slow, unscalable और बदलने में दर्दनाक बनता है। Access-pattern method एक दोहराने लायक process देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Describe the workload**: list entities, data size (docs, avg bytes), and growth.
Step 2 → **List operations** with frequency & latency target: e.g. "show restaurant page - 5000 reads/sec, < 50 ms", "place order - 200 writes/sec", "nightly revenue report - 1/day".
Step 3 → **Pick the shape for the hottest operations**: embed what is read together and bounded in size; reference what is large, unbounded, or updated independently.
Step 4 → **Apply patterns** (bucket, computed, subset, extended reference... see notes 72-73) to fix any hot spot.
Step 5 → **Create indexes** that serve each query (equality, sort, range order - the ESR rule).
Step 6 → **Validate** with realistic data volume and `explain()`; add `$jsonSchema` validation (note 75) and a `schemaVersion` field for future change (note 74). Revisit when the workload changes.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Workload बताओ**: entities, data size (docs, औसत bytes) और growth की list।
Step 2 → **Operations की list** frequency और latency target के साथ: जैसे "restaurant page दिखाओ - 5000 reads/sec, < 50 ms", "order place करो - 200 writes/sec", "रात की revenue report - दिन में 1"।
Step 3 → **सबसे hot operations के लिए shape चुनो**: जो साथ पढ़ा जाता है और size में bounded है उसे embed करो; जो बड़ा, unbounded या अलग से update होता है उसे reference करो।
Step 4 → Hot spot हो तो **patterns लगाओ** (bucket, computed, subset, extended reference... notes 72-73)।
Step 5 → हर query के लिए **indexes** बनाओ (equality, sort, range order - ESR rule)।
Step 6 → असली data volume और `explain()` से **validate** करो; `$jsonSchema` validation (note 75) और भविष्य के बदलाव के लिए `schemaVersion` (note 74) जोड़ो। Workload बदले तो फिर से देखो।

---

## 🟡 Real World Example
**Zomato's restaurant page**: one screen shows name, address, cuisines, opening hours, top 5 reviews and average rating. These are read together (5000+ times a second) so they live in **one `restaurants` document** (embedded address, hours, cuisines, `recentReviews[5]`, precomputed `avgRating`). The 2 lakh full reviews are huge, unbounded and queried on a separate "all reviews" page, so they sit in a **`reviews` collection** referencing `restaurantId`. The page = one `findOne` by `_id`; no joins on the hot path.

## 🟡 Real Example Hindi mein
**Zomato का restaurant page**: एक screen पर नाम, address, cuisines, opening hours, top 5 reviews और average rating दिखते हैं। ये साथ पढ़े जाते हैं (सेकंड में 5000+ बार), इसलिए **एक `restaurants` document** में हैं (embedded address, hours, cuisines, `recentReviews[5]`, precomputed `avgRating`)। 2 लाख पूरे reviews बड़े, unbounded हैं और अलग "all reviews" page पर query होते हैं, इसलिए वे `restaurantId` reference वाली **`reviews` collection** में हैं। Page = `_id` से एक `findOne`; hot path में कोई join नहीं।

---

## 💻 Code Example — Basic

```javascript
// mongosh (MongoDB 8.0.4). Workload: "restaurant page" is hot, "all reviews" is cold & big.
use t69

// Hot read: ONE document holds everything the page needs
db.restaurants.insertOne({
  _id: "r1",                                           // simple string id for the demo
  name: "Meghana Foods",
  city: "Bengaluru",
  address: { line: "Koramangala", pin: "560034" },     // 1:1 -> embed
  hours: [ { d: "Mon", o: "11:00", c: "23:00" } ]      // small, bounded array -> embed
})

// Cold, unbounded data: separate collection that references the restaurant
db.reviews.insertMany([
  { _id: 1, restaurantId: "r1", userId: "u1", stars: 5 },
  { _id: 2, restaurantId: "r1", userId: "u2", stars: 4 },
  { _id: 3, restaurantId: "r1", userId: "u3", stars: 3 }
])
db.reviews.createIndex({ restaurantId: 1 })            // makes "reviews of a restaurant" an index lookup

// The hot query = one indexed read, no join
db.restaurants.findOne({ _id: "r1" })
// Output: { _id: 'r1', name: 'Meghana Foods', city: 'Bengaluru',
//           address: { line: 'Koramangala', pin: '560034' }, hours: [ { d: 'Mon', o: '11:00', c: '23:00' } ] }
```

## 💻 Code Example — Advanced

```javascript
// mongosh — when you DO need a join (cold path), $lookup computes it; and you can verify access paths
// 1) Cold report: average stars and review count per restaurant via $lookup
db.restaurants.aggregate([
  { $match: { _id: "r1" } },                           // narrow first
  { $lookup: {                                         // left outer join to reviews
      from: "reviews",
      localField: "_id",                               // restaurants._id
      foreignField: "restaurantId",                    // reviews.restaurantId (indexed)
      as: "reviews"
  } },
  { $project: { name: 1,
                avgStars: { $avg: "$reviews.stars" },  // $avg over an array path
                n: { $size: "$reviews" } } }
])
// Output: [ { _id: 'r1', name: 'Meghana Foods', avgStars: 4, n: 3 } ]

// 2) Workload checklist as data: keep your design assumptions next to the schema
db.schema_notes.insertOne({
  collection: "restaurants",
  reads:  [ { q: "findOne by _id", perSec: 5000, sla: "50ms" } ],
  writes: [ { q: "update avgRating", perSec: 20 } ],
  rule: "embed address+hours+recentReviews[5]; reference full reviews"
})
// (Optional but useful: design decisions documented where the team will find them)

// 3) Prove the hot path with explain: should be a direct _id index lookup, docsExamined 1
db.restaurants.find({ _id: "r1" }).explain("executionStats")
// Measured: nReturned: 1, totalDocsExamined: 1, winningPlan.stage: 'EXPRESS_IXSCAN' (older versions say IDHACK)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const { Schema } = mongoose;

// Hot document: embed bounded stuff as sub-schemas
const restaurantSchema = new Schema({
  name: { type: String, required: true },
  city: String,
  address: { line: String, pin: String },             // 1:1 embedded
  hours: [{ d: String, o: String, c: String }]        // bounded array embedded
});
const Restaurant = mongoose.model('Restaurant', restaurantSchema);

// Cold, unbounded: separate model with ref + index
const Review = mongoose.model('Review', new Schema({
  restaurant: { type: Schema.Types.ObjectId, ref: 'Restaurant', index: true },
  stars: { type: Number, min: 1, max: 5 }
}));

const app = express();

// HOT path: one findOne (use lean() for plain objects = faster)
app.get('/restaurants/:id', async (req, res) => {
  const r = await Restaurant.findById(req.params.id).lean();
  if (!r) return res.status(404).json({ error: 'Not found' });
  res.json(r);
});

// COLD path: paginated reviews from their own collection
app.get('/restaurants/:id/reviews', async (req, res) => {
  const page = Math.max(1, Number(req.query.page) || 1);
  const reviews = await Review.find({ restaurant: req.params.id })
    .sort({ _id: -1 }).skip((page - 1) * 20).limit(20).lean();   // ok for small pages; use range paging for deep ones
  res.json(reviews);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Designing from the ER diagram, not from queries
```javascript
// Wrong — 5 collections, hot page needs 5 queries/$lookups
// restaurants, addresses, hours, cuisines, ratings
// Right — one restaurants doc with embedded address/hours/cuisines; only unbounded data is referenced
```

❌ Mistake 2: Embedding everything because "MongoDB is schemaless"
```javascript
// Wrong — one user doc with every order ever: grows forever, rewritten on each update, hits 16 MB
{ _id: "u1", orders: [ /* 50,000 orders */ ] }
// Right — orders in their own collection with an index on userId (+ maybe last 5 orders embedded: Subset pattern)
```
✅ Also: no indexes planned for the hot query, or designing once and never revisiting when the workload changes.

---

## 🧠 Tricky Interview Question

"Should we embed or reference?" — an interviewer gives you: users have profiles (read on every request), 3 addresses, and 10 years of orders (read rarely, 500 orders avg). What do you say?

Answer: Profile and addresses are 1:few, read with the user, small and bounded: **embed**. Orders are 1:many with growth and are read on a separate screen with pagination and independent updates: **reference** (`orders.userId` + index `{ userId: 1, createdAt: -1 }`). If the home screen shows the last 3 orders, apply the **Subset pattern**: embed those 3 in the user doc (or their summaries) and keep the full history in `orders`. The key sentence: *"It depends on the access pattern, cardinality, size growth, and update frequency"*, then show you decide using those four factors.

---

## ⚫ Interview Questions + Answers

Q1: What is the core rule of MongoDB schema design?
A1: Data that is accessed together should be stored together; design for the application's read/write patterns, not for normalization. Each decision is a trade-off between read speed (fewer reads, duplication) and write cost/consistency.

Q2: Does "schemaless" mean no schema design?
A2: No. Collections don't force a shape, but your app code always assumes one. Good design (plus `$jsonSchema` validation) decides performance, correctness and how cheaply you can evolve it.

Q3: Which four factors decide embed vs reference?
A3: (1) Are they read together? (2) Cardinality and growth - bounded or unbounded? (3) Update frequency / independent updates; (4) Atomicity needs - one document gives single-doc atomic updates. Plus the 16 MB doc limit.

Q4: Is duplication allowed in MongoDB?
A4: Yes, deliberately - e.g. storing a customer name inside an order (Extended Reference). You pay at write time (update copies) to save a join at read time. Duplicate fields that rarely change.

Q5: How do you handle schema change over time?
A5: Add a `schemaVersion` field, write new-format docs immediately, migrate old ones lazily or in batches, and keep code able to read both until done (note 74).

---

## 🔷 When to Use + When Not to Use
✅ Use the access-pattern method when:
- Starting any new MongoDB collection design
- A query is slow or needs too many joins
- Workload changes (new feature screen, scale jump)

❌ Avoid / be careful when:
- You don't yet know the queries - start simple, keep `schemaVersion`, and iterate rather than over-engineer
- Many ad-hoc, unpredictable relational queries over highly normalized data (a relational DB may fit better)

---

## 📊 Visual Diagram
```
SQL THINKING                     MONGODB THINKING
─────────────                    ──────────────────────────
Entities -> tables               Access patterns -> documents
Normalize                        "Store together what is read together"
JOIN at read time                Shape docs for the hot query

 workload ──► operations list ──► embed / reference ──► patterns
                                        │                   │
                                        ▼                   ▼
                                    indexes ◄────── explain() check
                                        │
                                  validate + schemaVersion
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Access pattern | How the app reads/writes data | App data कैसे पढ़ती/लिखती है |
| Embedding | Nest related data in one document | Related data एक doc के अंदर |
| Referencing | Store the id of another document | दूसरे doc का id रखना |
| Denormalization | Intentional duplication for speed | जान-बूझकर duplicate data |
| Cardinality | 1:1, 1:N, N:N relationship size | Relationship का आकार |
| Workload | Set of operations + volumes | Operations और उनकी मात्रा |
| 16 MB limit | Max BSON document size | Document का max size |

---

## ⚡ 3-Line Summary
English:
1. Design documents around access patterns: store together what is read together.
2. Embed bounded, co-read data; reference unbounded, independent or huge data; duplicate rarely-changing fields deliberately.
3. Always write down the workload, back hot queries with indexes, and re-evaluate when usage changes.

Hindi:
1. Documents को access patterns के हिसाब से बनाओ: जो साथ पढ़ा जाता है, साथ रखो।
2. Bounded और साथ-पढ़ा जाने वाला data embed करो; unbounded, स्वतंत्र या बड़ा data reference करो; कम बदलने वाले fields जान-बूझकर duplicate करो।
3. Workload हमेशा लिखो, hot queries को indexes दो, और usage बदलने पर फिर से जाँचो।

---

## ➡️ Next Topic
**70. Embedding vs Referencing** — the concrete decision rules, size limits and trade-offs, with `$lookup` and `populate`.
