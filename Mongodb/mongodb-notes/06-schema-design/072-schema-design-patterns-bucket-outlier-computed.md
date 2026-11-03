# 72. Schema Design Patterns — Bucket, Outlier, Computed
# हिंदी में: Schema Design Patterns — Bucket, Outlier, Computed

---

## 🔵 Simple Definition (English)
Three classic MongoDB design patterns:
- **Bucket**: group many small time-ordered records (sensor readings, events) into one document per time window or per N items, instead of one document per record.
- **Outlier**: handle the rare giant case (a viral book with 1 million buyers) with an overflow flag/document so it does not distort the design for the 99.9% normal documents.
- **Computed**: pre-calculate and store a derived value (sum, count, average) at write time (or by a periodic job) so reads do not recompute it.

## 🔵 सरल परिभाषा (Hindi)
तीन classic MongoDB design patterns:
- **Bucket**: बहुत सारे छोटे time-ordered records (sensor readings, events) को हर record के लिए एक document की जगह हर time window या हर N items के लिए एक document में group करना।
- **Outlier**: बहुत दुर्लभ विशाल case (10 लाख buyers वाली viral book) को overflow flag/document से संभालना, ताकि 99.9% normal documents का design न बिगड़े।
- **Computed**: derived value (sum, count, average) को write के समय (या periodic job से) पहले ही calculate करके store करना, ताकि read पर बार-बार compute न करना पड़े।

---

## 🔴 Problem it Solves
- **Bucket**: 1 sensor sending a reading every second = 86,400 tiny documents per day, each with its own `_id`, per-document overhead and index entries; indexes grow huge and range scans touch many docs.
- **Outlier**: a design tuned for "a book has ~50 buyers" (embed `buyers[]`) breaks for the one book with a million buyers (16 MB cap), forcing everyone into the slow reference model.
- **Computed**: dashboards that `$sum`/`$avg` millions of rows on every page view burn CPU for results that rarely change.

## 🔴 यह क्यों बना? (Hindi)
- **Bucket**: एक sensor हर सेकंड reading भेजे तो दिन में 86,400 छोटे documents बनते हैं, हर एक का अपना `_id`, per-document overhead और index entries; indexes बहुत बड़े हो जाते हैं और range scan कई docs छूता है।
- **Outlier**: "एक book के ~50 buyers" के लिए बना design (embed `buyers[]`) उस एक book पर टूट जाता है जिसके 10 लाख buyers हैं (16 MB cap), और सबको slow reference model में धकेलना पड़ता है।
- **Computed**: जो dashboards हर page view पर लाखों rows का `$sum`/`$avg` निकालते हैं, वे ऐसे results के लिए CPU जलाते हैं जो कम ही बदलते हैं।

---

## 🟢 How it Works — Step by Step

**Bucket**
Step 1 → Choose the bucket key: `(sensorId, hour)` or `(sensorId, count < 100)`.
Step 2 → On each reading do an **upsert**: match the open bucket, `$push` the sample, `$inc` `count`/`sum`; if no bucket matches (new hour / full), the upsert creates a new one.
Step 3 → Query by `(sensorId, hour)` range: one doc = many samples; precomputed `count`/`sum` give averages without scanning samples.

**Outlier**
Step 1 → Design the normal case (embed `buyers[]` capped by `$slice`/size check).
Step 2 → When a doc crosses the threshold, set `has_extras: true` and put overflow in another collection.
Step 3 → App code: if `has_extras`, also read the overflow collection. Normal docs never pay.

**Computed**
Step 1 → Identify read-heavy, rarely-changing, expensive aggregates.
Step 2 → Update the stored value with each write using an **update pipeline** (`$inc` or `[{ $set: ... }]`), or recompute in a batch (`$merge`).
Step 3 → Read the stored value directly.

## 🟢 कैसे काम करता है? (Hindi)
**Bucket**
Step 1 → Bucket key चुनो: `(sensorId, hour)` या `(sensorId, count < 100)`।
Step 2 → हर reading पर **upsert**: खुले bucket को match करो, sample `$push` करो, `count`/`sum` `$inc` करो; अगर कोई bucket match नहीं हुआ (नया घंटा / bucket भर गया) तो upsert नया बना देता है।
Step 3 → `(sensorId, hour)` range से query करो: एक doc = कई samples; precomputed `count`/`sum` से samples scan किए बिना average।

**Outlier**
Step 1 → Normal case का design (embed `buyers[]`, `$slice`/size check से सीमित)।
Step 2 → जब doc threshold पार करे, `has_extras: true` लगाओ और overflow दूसरी collection में डालो।
Step 3 → App code: `has_extras` हो तो overflow collection भी पढ़ो। Normal docs को कोई अतिरिक्त cost नहीं।

**Computed**
Step 1 → Read-heavy, कम बदलने वाले महंगे aggregates पहचानो।
Step 2 → हर write के साथ stored value **update pipeline** (`$inc` या `[{ $set: ... }]`) से अपडेट करो, या batch में recompute (`$merge`)।
Step 3 → Stored value सीधे पढ़ो।

---

## 🟡 Real World Example
**Ola/IoT-style vehicle telemetry (Bucket)**: each cab sends GPS + speed every 5 s. Instead of 17,000 docs per cab per day, one document per `(cabId, hour)` with `samples[]` and a running `count`. **Wattpad/Amazon-style bestseller (Outlier)**: most books have <100 buyers; "Wings of Fire" has millions, so it gets `has_extras: true` and an overflow collection. **BookMyShow rating (Computed)**: each movie stores `ratingSum`, `ratingCount`, `avgRating`, updated on each new rating, so the listing page reads one number.

## 🟡 Real Example Hindi mein
**Ola/IoT-style vehicle telemetry (Bucket)**: हर cab हर 5 सेकंड GPS + speed भेजती है। हर cab के लिए दिन में 17,000 docs की जगह `(cabId, hour)` के लिए एक document जिसमें `samples[]` और running `count`। **Amazon-style bestseller (Outlier)**: ज़्यादातर books के <100 buyers; "Wings of Fire" के लाखों, इसलिए उसे `has_extras: true` और overflow collection मिलती है। **BookMyShow rating (Computed)**: हर movie `ratingSum`, `ratingCount`, `avgRating` रखती है जो हर नई rating पर update होते हैं, इसलिए listing page एक number पढ़ता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh (MongoDB 8.0.4)
use t72

// ---------- BUCKET: one document per sensor per hour, max 100 samples ----------
const readings = [
  ["2026-03-01T10:00:05Z", 21.5], ["2026-03-01T10:05:00Z", 22.1],
  ["2026-03-01T10:59:00Z", 22.8], ["2026-03-01T11:02:00Z", 23.0]
];
for (const [t, v] of readings) {
  const d = new Date(t);                                            // reading timestamp
  const hour = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(), d.getUTCHours())); // bucket start
  db.readings.updateOne(
    { sensorId: "s1", hour: hour, count: { $lt: 100 } },            // open bucket for this hour with room left
    { $push: { samples: { ts: d, temp: v } },                       // append the sample
      $inc:  { count: 1, sum: v } },                                // maintain count + running sum (Computed inside Bucket)
    { upsert: true }                                                // no matching bucket -> create one
  );
}
db.readings.find({}, { _id: 0 })
// Output: 2 documents (ObjectIds omitted)
// { sensorId:'s1', hour: ISODate('2026-03-01T10:00:00Z'), count: 3, sum: 66.4, samples: [3 items] }
// { sensorId:'s1', hour: ISODate('2026-03-01T11:00:00Z'), count: 1, sum: 23,   samples: [1 item] }
// (field order inside the upserted doc may differ from what you expect; the content is what matters)
```

## 💻 Code Example — Advanced

```javascript
// mongosh — Computed pattern with an update PIPELINE, and Outlier pattern

// ---------- COMPUTED: keep avgRating up to date on every new rating ----------
db.movies.insertOne({ _id: 1, title: "X", ratingSum: 0, ratingCount: 0, avgRating: 0 })
for (const r of [5, 4, 3]) {
  db.movies.updateOne({ _id: 1 }, [                                        // array = update with aggregation pipeline (4.2+)
    { $set: { ratingSum:   { $add: ["$ratingSum", r] },                    // stage 1: add the rating
              ratingCount: { $add: ["$ratingCount", 1] } } },
    { $set: { avgRating: { $round: [ { $divide: ["$ratingSum", "$ratingCount"] }, 2 ] } } } // stage 2 sees stage-1 values
  ])
}
db.movies.findOne()
// Output: { _id: 1, title: 'X', ratingSum: 12, ratingCount: 3, avgRating: 4 }
// Reading the average is now O(1): no scan of the ratings

// ---------- OUTLIER: flag the rare giant, keep overflow elsewhere ----------
db.books.insertMany([
  { _id: 1, title: "Wings of Fire", buyers: ["u1", "u2"] },                    // normal: embedded buyers
  { _id: 2, title: "Viral Book",     buyers: ["u1"], has_extras: true }         // outlier flagged
])
db.books_extra.insertOne({ bookId: 2, buyers: ["u2", "u3", "u4"] })            // overflow lives here
db.books.find({ has_extras: true })
// Output: [ { _id: 2, title: 'Viral Book', buyers: [ 'u1' ], has_extras: true } ]

// Cap the embedded array and spill with a conditional update (app logic):
//   if (book.buyers.length >= 1000) { set has_extras: true; insert into books_extra }
// Index the flag partially so only outliers are indexed:
db.books.createIndex({ has_extras: 1 }, { partialFilterExpression: { has_extras: true } })

// Aggregating a bucket collection: average per hour WITHOUT scanning samples
db.readings.aggregate([
  { $project: { sensorId: 1, hour: 1, avg: { $round: [ { $divide: ["$sum", "$count"] }, 2 ] } } }
])
// Output: avg 22.13 for the 10:00 hour and 23 for the 11:00 hour (66.4/3 = 22.133)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const { Schema } = mongoose;

// Bucket model
const Reading = mongoose.model('Reading', new Schema({
  sensorId: String, hour: Date, count: { type: Number, default: 0 }, sum: { type: Number, default: 0 },
  samples: [{ ts: Date, temp: Number, _id: false }]          // _id:false -> no per-sample ObjectId overhead
}));

const app = express();
app.use(express.json());

app.post('/readings', async (req, res) => {
  const { sensorId, temp } = req.body;
  const d = new Date();
  const hour = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(), d.getUTCHours()));
  await Reading.updateOne(
    { sensorId, hour, count: { $lt: 100 } },
    { $push: { samples: { ts: d, temp } }, $inc: { count: 1, sum: temp } },
    { upsert: true }
  );
  res.sendStatus(202);
});

// Computed: average rating maintained in the same write (pipeline update works via Mongoose too)
const Movie = mongoose.model('Movie', new Schema({ ratingSum: Number, ratingCount: Number, avgRating: Number }));
app.post('/movies/:id/rate', async (req, res) => {
  const r = Number(req.body.stars);
  if (!(r >= 1 && r <= 5)) return res.status(400).json({ error: 'stars 1-5' });
  const m = await Movie.findByIdAndUpdate(req.params.id, [
    { $set: { ratingSum: { $add: ['$ratingSum', r] }, ratingCount: { $add: ['$ratingCount', 1] } } },
    { $set: { avgRating: { $round: [{ $divide: ['$ratingSum', '$ratingCount'] }, 2] } } }
  ], { new: true });
  res.json(m);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Unbounded bucket (no `count` limit)
```javascript
// Wrong — bucket per sensor forever: becomes the unbounded-array anti-pattern
db.readings.updateOne({ sensorId: "s1" }, { $push: { samples: s } }, { upsert: true })
// Right — bucket per hour/day AND cap by count: { sensorId, hour, count: { $lt: 100 } }
```

❌ Mistake 2: Computed value drifting out of sync (read-modify-write in app code)
```javascript
// Wrong — race condition: two requests read sum=10, both write 10+5
const m = await Movie.findById(id); m.ratingSum += 5; await m.save();
// Right — let the database apply the change atomically
db.movies.updateOne({ _id: id }, { $inc: { ratingSum: 5, ratingCount: 1 } })
```
✅ Also: applying Outlier to everything (premature) and forgetting to schedule a reconcile job that recomputes totals.

---

## 🧠 Tricky Interview Question

In the Bucket upsert `{ sensorId, hour, count: { $lt: 100 } }`, the 101st reading in the same hour arrives. What happens, and what race could occur?

Answer: The filter no longer matches the full bucket (`count` is 100), so `upsert: true` **creates a second bucket** for the same `(sensorId, hour)`, seeded with the filter's equality fields plus the update operators. That's intended: one hour may have several buckets, so queries must fetch *all* buckets in the hour (`find({ sensorId, hour })`). Race: two concurrent first-readings could create two buckets for an hour (no unique index fits since multiple buckets per hour are allowed), which is harmless for reads. To avoid unbounded duplicates add a `bucketSeq` or use a unique index on `(sensorId, hour, seq)`. For pure time series on 5.0+, consider native **time series collections** (`createCollection` with `timeseries`) which do bucketing for you.

---

## ⚫ Interview Questions + Answers

Q1: Why bucket instead of one document per reading?
A1: Fewer documents and index entries (smaller indexes and working set), faster range queries (one doc read returns many points), and ability to store precomputed aggregates per bucket. Cost: more complex writes/updates, and individual-point queries need `$unwind`.

Q2: When use the Outlier pattern?
A2: When a small fraction of documents is far larger than the rest (celebrity followers, viral products) and you don't want the whole schema to bend to the worst case. Flag them (`has_extras`) and handle with different code/collection.

Q3: What is the Computed pattern's main risk?
A3: Staleness/drift: the stored value can diverge from the source data (failed update, bug). Mitigate with atomic `$inc`, update pipelines, transactions when needed, and periodic reconciliation.

Q4: Are time series collections a replacement for manual bucketing?
A4: In most cases yes (MongoDB 5.0+): `db.createCollection("m", { timeseries: { timeField: "ts", metaField: "sensorId", granularity: "minutes" } })` does bucketing, compression and special indexes automatically. Manual bucketing still helps for custom bucket logic or older versions.

Q5: How do you do an average over a bucket collection?
A5: Store `sum` and `count` in each bucket (Computed inside Bucket), then `$sum` them across buckets and divide; never average the per-bucket averages unless counts are equal.

---

## 🔷 When to Use + When Not to Use
✅ Use:
- Bucket: IoT, metrics, chat messages, any high-volume time-ordered data
- Outlier: skewed data where few docs are enormous
- Computed: dashboards, counters, ratings, leaderboards read far more than written

❌ Avoid:
- Bucket when you mostly query single, random points by id
- Computed when the source changes constantly and exactness at read time is critical (compute on demand)
- Outlier before you actually have outliers

---

## 📊 Visual Diagram
```
BUCKET                              OUTLIER                    COMPUTED
──────                              ───────                    ────────
before: 1 doc / reading             normal book                write: rating=4
 {t1,v} {t2,v} {t3,v} ...           { buyers:[...50] }           │ $inc sum,count
after: 1 doc / hour (≤100)                                       ▼
 { hour, count, sum,                viral book                 { sum:12, count:3,
   samples:[t1,t2,t3...] }          { buyers:[...1000],          avg:4 }
                                      has_extras:true } ──►    read: just avg
                                    books_extra {overflow}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bucket pattern | Group time-ordered records per window | Window के हिसाब से records group |
| Outlier pattern | Special handling for rare huge docs | दुर्लभ बड़े docs की अलग handling |
| Computed pattern | Store derived values | Derived values पहले से store |
| Upsert | Update or insert if none matches | Update, नहीं मिले तो insert |
| Update pipeline | Update expressed as aggregation stages | Aggregation stages वाला update |
| Time series collection | Native bucketed collection (5.0+) | Native time-series collection |
| Reconciliation | Periodic recompute to fix drift | Drift सुधारने को recompute |

---

## ⚡ 3-Line Summary
English:
1. Bucket groups many small time-ordered records into one capped document; Outlier isolates rare giants; Computed stores derived values.
2. Use upserts with `$push`/`$inc` for buckets and atomic update pipelines for computed fields to avoid races.
3. Cap bucket size, flag outliers early, and reconcile computed values periodically; prefer native time series collections on 5.0+.

Hindi:
1. Bucket कई छोटे time-ordered records को एक capped document में group करता है; Outlier दुर्लभ विशाल docs को अलग करता है; Computed derived values store करता है।
2. Buckets के लिए `$push`/`$inc` वाले upserts और computed fields के लिए atomic update pipelines इस्तेमाल करो ताकि races न हों।
3. Bucket size सीमित रखो, outliers जल्दी flag करो, computed values को समय-समय पर reconcile करो; 5.0+ में native time series collections को प्राथमिकता दो।

---

## ➡️ Next Topic
**73. Schema Design Patterns — Subset, Extended Reference, Polymorphic** — keep the working set small, avoid joins by copying stable fields, and store different shapes in one collection.
