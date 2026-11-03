# 80. Time-Series Collections
# हिंदी में: Time-Series Collections

---

## 🔵 Simple Definition (English)
A **time-series collection** is a special MongoDB collection (introduced in 5.0) optimized for measurements that arrive over time: GPS pings, sensor readings, stock ticks, metrics. You declare a `timeField` (the timestamp) and optionally a `metaField` (what produced the data, e.g. `riderId`). Internally MongoDB groups many measurements into compressed **buckets**, so storage shrinks and range scans become fast. You still insert and query it like a normal collection.

## 🔵 सरल परिभाषा (Hindi)
**Time-series collection** एक special MongoDB collection है (5.0 में आई) जो समय के साथ आने वाली measurements के लिए optimized है: GPS pings, sensor readings, stock ticks, metrics। आप एक `timeField` (timestamp) और optionally एक `metaField` (data किसने बनाया, जैसे `riderId`) declare करते हैं। अंदर से MongoDB कई measurements को compressed **buckets** में group करता है, जिससे storage घटता है और range scans तेज़ होते हैं। Insert और query आप सामान्य collection की तरह ही करते हैं।

---

## 🔴 Problem it Solves
A food-delivery app with 100,000 active riders pinging every 5 seconds writes ~1.7 million documents per minute. In a regular collection each ping is a separate document with its own `_id`, an index entry and BSON overhead; the index on `{riderId, ts}` becomes huge, and old data must be deleted by an expensive `deleteMany`. Time-series collections store measurements in compact columnar-like buckets, compress them, build a clustered/secondary index automatically on time and meta, and can **expire old data automatically** with `expireAfterSeconds`.

## 🔴 यह क्यों बना? (Hindi)
100,000 active riders वाला food-delivery app अगर हर 5 सेकंड में ping भेजे तो हर मिनट लगभग 17 लाख documents लिखने पड़ते हैं। सामान्य collection में हर ping अलग document होता है, अपनी `_id`, index entry और BSON overhead के साथ; `{riderId, ts}` का index बहुत बड़ा हो जाता है और पुराने data को महँगे `deleteMany` से हटाना पड़ता है। Time-series collection measurements को compact buckets में रखती है, compress करती है, time और meta पर index अपने आप बनाती है और `expireAfterSeconds` से **पुराना data अपने आप हटा** सकती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Create the collection with `db.createCollection(name, { timeseries: { timeField, metaField, granularity } })`. `timeField` must be a BSON date.
Step 2 → `metaField` holds data that rarely changes between measurements (rider id, city, sensor id). MongoDB uses it to decide which bucket a document goes to, so keep it **a stable label, not a measurement**.
Step 3 → `granularity` (`seconds`, `minutes`, `hours`) is a hint for bucket time span. In our test with `seconds`, `bucketMaxSpanSeconds` was 3600 (one hour per bucket).
Step 4 → Insert normally (`insertOne`/`insertMany`, batch for best throughput). The server stores them in an internal `system.buckets.<name>` collection and presents an unpacked **view** to you.
Step 5 → Query with `find` and aggregation (`$dateTrunc`, `$group`, `$setWindowFields`) for downsampling. Add secondary indexes on `metaField` subfields and `timeField`.
Step 6 → Optionally set `expireAfterSeconds` for automatic TTL deletion of whole expired buckets.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `db.createCollection(name, { timeseries: { timeField, metaField, granularity } })` से collection बनाओ। `timeField` BSON date होना चाहिए।
Step 2 → `metaField` में वह data रखो जो measurements के बीच कम बदलता है (rider id, city, sensor id)। MongoDB इसी से तय करता है कि document किस bucket में जाए, इसलिए इसे **stable label** रखो, measurement नहीं।
Step 3 → `granularity` (`seconds`, `minutes`, `hours`) bucket के time span का hint है। हमारे test में `seconds` पर `bucketMaxSpanSeconds` 3600 निकला (यानी एक bucket = एक घंटा)।
Step 4 → सामान्य तरीके से insert करो (`insertOne`/`insertMany`, बेहतर throughput के लिए batch में)। Server उन्हें internal `system.buckets.<name>` collection में रखता है और आपको unpacked **view** दिखाता है।
Step 5 → `find` और aggregation (`$dateTrunc`, `$group`, `$setWindowFields`) से downsampling करो। `metaField` के subfields और `timeField` पर secondary indexes जोड़ो।
Step 6 → चाहो तो `expireAfterSeconds` से TTL के ज़रिए expired buckets अपने आप हटवाओ।

---

## 🟡 Real World Example
**Swiggy** tracks every delivery partner's location every few seconds. Each ping is `{ ts, meta: { riderId, city }, lat, lng, speed, battery }`. The ops team asks "average speed per rider per minute in the last hour" and the customer app asks "latest ping of rider D7". Pings older than 24 hours are useless for live tracking, so the collection is created with `expireAfterSeconds: 86400` and MongoDB drops expired buckets itself. An hourly job rolls the data up into a small `rider_hourly_stats` collection for long-term analytics.

## 🟡 Real Example Hindi mein
**Swiggy** हर delivery partner की location कुछ सेकंड में track करता है। हर ping है `{ ts, meta: { riderId, city }, lat, lng, speed, battery }`। Ops team पूछती है "पिछले एक घंटे में हर rider की प्रति मिनट average speed" और customer app पूछता है "rider D7 का latest ping"। 24 घंटे से पुराने pings live tracking के काम के नहीं, इसलिए collection `expireAfterSeconds: 86400` के साथ बनी है और MongoDB expired buckets खुद हटा देता है। हर घंटे एक job data को छोटी `rider_hourly_stats` collection में roll up करती है।

---

## 💻 Code Example — Basic

```javascript
// mongosh — tested on MongoDB 8.0.4 (time-series needs 5.0+)
const d = db.getSiblingDB("iot");
d.dropDatabase();

// Create the time-series collection
d.createCollection("rider_pings", {
  timeseries: {
    timeField: "ts",          // REQUIRED: BSON Date of each measurement
    metaField: "meta",        // label of the source: which rider, which city
    granularity: "seconds"    // hint: measurements arrive every few seconds
  },
  expireAfterSeconds: 86400   // auto-delete data older than 24 hours
});

// Insert 6 pings for rider D7 and 3 for rider D8, 30 seconds apart
const base = new Date("2025-03-01T10:00:00Z").getTime();   // fixed time so output is reproducible
const docs = [];
for (let i = 0; i < 6; i++)
  docs.push({ ts: new Date(base + i * 30000), meta: { riderId: "D7", city: "Pune" }, speed: 20 + i * 2, battery: 90 - i });
for (let i = 0; i < 3; i++)
  docs.push({ ts: new Date(base + i * 30000), meta: { riderId: "D8", city: "Pune" }, speed: 10 + i, battery: 80 - i });
d.rider_pings.insertMany(docs);      // batch insert = best throughput for time-series

d.rider_pings.countDocuments();
// Output: 9

// Inspect the options MongoDB stored
d.getCollectionInfos({ name: "rider_pings" })[0].options;
// Output: { expireAfterSeconds: Long('86400'),
//           timeseries: { timeField: 'ts', metaField: 'meta', granularity: 'seconds', bucketMaxSpanSeconds: 3600 } }

// Average and max speed per rider
d.rider_pings.aggregate([
  { $group: { _id: "$meta.riderId", avgSpeed: { $avg: "$speed" }, maxSpeed: { $max: "$speed" }, n: { $sum: 1 } } },
  { $sort: { _id: 1 } }
]).toArray();
// Output: [ { _id: 'D7', avgSpeed: 25, maxSpeed: 30, n: 6 },
//           { _id: 'D8', avgSpeed: 11, maxSpeed: 12, n: 3 } ]
```

## 💻 Code Example — Advanced

```javascript
// mongosh — continues from the Basic example

// 1) DOWNSAMPLING: average speed of rider D7 per minute with $dateTrunc ($dateTrunc needs 5.0+)
d.rider_pings.aggregate([
  { $match: { "meta.riderId": "D7" } },                                      // one rider
  { $group: { _id: { $dateTrunc: { date: "$ts", unit: "minute" } },          // bucket into minutes
              avg: { $avg: "$speed" } } },
  { $sort: { _id: 1 } }
]).toArray();
// Output: [ { _id: ISODate('2025-03-01T10:00:00.000Z'), avg: 21 },
//           { _id: ISODate('2025-03-01T10:01:00.000Z'), avg: 25 },
//           { _id: ISODate('2025-03-01T10:02:00.000Z'), avg: 29 } ]

// 2) SECONDARY INDEX on meta subfield + time for "latest ping of rider X"
d.rider_pings.createIndex({ "meta.riderId": 1, ts: -1 });
d.rider_pings.find({ "meta.riderId": "D7" }, { _id: 0, ts: 1, speed: 1 }).sort({ ts: -1 }).limit(1).toArray();
// Output: [ { ts: ISODate('2025-03-01T10:02:30.000Z'), speed: 30 } ]

// 3) UPDATE LIMITS: you cannot update a single measurement by value
try { d.rider_pings.updateOne({ "meta.riderId": "D7" }, { $set: { speed: 1 } }); }
catch (e) { print("ERR", e.codeName, e.message); }
// Output: ERR  Cannot perform a non-multi update on a time-series collection
// (updateMany on metaField only is allowed; changing measurements/timeField is not)

// 4) DELETE: in 8.0 deleteOne works; deleteMany by metaField is the efficient, supported form
d.rider_pings.deleteMany({ "meta.riderId": "D8" });
// Output: { acknowledged: true, deletedCount: 3 }
d.rider_pings.countDocuments();
// Output: 5   (9 pings - 1 removed earlier by a deleteOne in our test run - 3 = 5; yours is 6 if you skipped that)

// 5) The hidden bucket collection exists
d.getCollectionInfos({ name: "system.buckets.rider_pings" }).length;
// Output: 1   (you normally never touch it directly)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose supports time-series via schema options (Mongoose 6+/9, MongoDB 5.0+)
const express = require('express');
const mongoose = require('mongoose');
const { Schema } = mongoose;

const pingSchema = new Schema({
  ts: { type: Date, required: true },
  meta: { riderId: String, city: String },
  speed: Number, battery: Number,
}, {
  timeseries: { timeField: 'ts', metaField: 'meta', granularity: 'seconds' },
  expireAfterSeconds: 86400,       // auto-expire after a day
  autoCreate: true,                // let Mongoose create the time-series collection
  versionKey: false,               // bucketed docs don't need __v
});
const Ping = mongoose.model('RiderPing', pingSchema);

const app = express();
app.use(express.json());

// Riders post location batches; insertMany is much cheaper than many single inserts
app.post('/api/pings', async (req, res) => {
  const docs = req.body.map(p => ({ ts: new Date(p.ts), meta: { riderId: p.riderId, city: p.city }, speed: p.speed, battery: p.battery }));
  await Ping.insertMany(docs, { ordered: false });
  res.sendStatus(202);
});

// Latest known position of a rider
app.get('/api/riders/:id/latest', async (req, res) => {
  const p = await Ping.findOne({ 'meta.riderId': req.params.id }).sort({ ts: -1 }).lean();
  p ? res.json(p) : res.sendStatus(404);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting a changing measurement (like speed) in `metaField`
```javascript
// Wrong — every distinct meta value creates a new bucket: buckets stay tiny, no compression benefit
{ ts, meta: { riderId: "D7", speed: 24 } }

// Right — meta = stable identity; measurements at top level
{ ts, meta: { riderId: "D7", city: "Pune" }, speed: 24 }
```

❌ Mistake 2: Inserting one document at a time at high volume
```javascript
// Wrong — one round trip per ping
for (const p of pings) await coll.insertOne(p);

// Right — batch them
await coll.insertMany(pings, { ordered: false });
```

❌ Mistake 3: Using time-series for data you update frequently
✅ Correct: Measurements are meant to be append-only. You cannot freely update individual measurements (our test: `updateOne` on a measurement failed). Use a normal collection for mutable data such as an order's status.

---

## 🧠 Tricky Interview Question

**Q:** You created a time-series collection with `expireAfterSeconds: 86400`, yet a ping that is 25 hours old still shows up in queries. Is TTL broken?

**Answer:** Not necessarily. For time-series collections the TTL monitor deletes **whole buckets** only once *every* measurement in the bucket is older than the expiry (bucket max time span plus `expireAfterSeconds`). With a 1-hour bucket, a ping can remain visible up to about an hour longer than its age suggests. Also, the TTL background task runs roughly every 60 seconds, not instantly. So the guarantee is "eventually removed shortly after expiry", not "invisible at exactly 24:00:00". If you need exact cutoffs, filter on `ts` in your query as well.

---

## ⚫ Interview Questions + Answers

Q1: What are `timeField` and `metaField`?
A1: `timeField` is the BSON Date marking when the measurement happened (required). `metaField` is an optional field (object or scalar) identifying the source; it should change rarely. MongoDB groups measurements with the same meta and nearby times into one bucket.

Q2: Why is a time-series collection smaller than a regular one?
A2: Measurements are stored in buckets with columnar-style compression, so the `_id` and per-document overhead are reduced and there is far less index data. Typical storage savings are large (often several times smaller) for regular data.

Q3: Can you update or delete documents?
A3: Limited. You can delete (efficiently by `metaField` filter), and update only metaField values with multi-updates. You cannot update the `timeField` or measurement values in the general case (we saw `updateOne` rejected). Treat the data as append-only.

Q4: How do you query only recent data fast?
A4: Filter on `ts` (and `meta` subfields) and add a compound secondary index such as `{ "meta.riderId": 1, ts: -1 }`. Aggregations with `$dateTrunc` or `$setWindowFields` downsample into minutes/hours.

Q5: Time-series collection vs regular collection with TTL index?
A5: Regular + TTL deletes document by document (index maintenance cost), with bigger storage. Time-series expires whole buckets cheaply and stores compactly. Choose a regular collection if documents are mutable or have no natural time/meta structure.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- High-volume append-only measurements (IoT, GPS, metrics, stock prices, logs with timestamps)
- You need rolling retention (auto-expire old data)
- Queries are mostly time-range plus source filters or aggregations

❌ Avoid when:
- Records are updated frequently or individually (orders, users)
- Data has no timestamp or arrives with wildly out-of-order times
- You need unique constraints beyond `_id` (secondary unique indexes are not supported on time-series)

---

## 📊 Visual Diagram
```
TIME-SERIES COLLECTION: rider_pings
──────────────────────────────────────────────────────
 You see (view):                        MongoDB stores (system.buckets.rider_pings):
 { ts:10:00:00, meta:{D7}, speed:20 }   ┌── BUCKET  meta:{D7,Pune}  10:00–11:00 ──┐
 { ts:10:00:30, meta:{D7}, speed:22 }   │ ts   : [10:00:00,10:00:30,10:01:00,...] │
 { ts:10:01:00, meta:{D7}, speed:24 } ─►│ speed: [20,22,24,26,28,30]  (compressed)│
 ...                                    └──────────────────────────────────────────┘
 { ts:10:00:00, meta:{D8}, speed:10 }   ┌── BUCKET  meta:{D8,Pune}  10:00–11:00 ──┐
 ...                                  ─►│ speed: [10,11,12]                       │
                                        └──────────────────────────────────────────┘
 expireAfterSeconds: 86400  → whole buckets dropped once fully expired
 Index: { "meta.riderId":1, ts:-1 } → "latest ping of rider X"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| timeField | Date field for each measurement | हर measurement का date field |
| metaField | Label of the data source | Data source का label |
| Bucket | Group of measurements stored together | साथ रखी गई measurements का group |
| Granularity | Hint for bucket time span | Bucket के time span का hint |
| expireAfterSeconds | Automatic retention period | Data रखने की automatic अवधि |
| Downsampling | Aggregating to coarser intervals | बड़े intervals में aggregate करना |
| `$dateTrunc` | Round date down to a unit | Date को unit तक नीचे round करना |

---

## ⚡ 3-Line Summary
English:
1. Time-series collections (5.0+) store append-only measurements in compressed buckets keyed by `timeField` and `metaField`.
2. Use `expireAfterSeconds` for automatic retention and `$dateTrunc` aggregations for downsampling.
3. Keep `metaField` stable, insert in batches, and do not rely on updating individual measurements.

Hindi:
1. Time-series collections (5.0+) append-only measurements को `timeField` और `metaField` के आधार पर compressed buckets में रखती हैं।
2. Automatic retention के लिए `expireAfterSeconds` और downsampling के लिए `$dateTrunc` aggregations इस्तेमाल करो।
3. `metaField` stable रखो, batches में insert करो, और अलग-अलग measurements को update करने पर निर्भर मत रहो।

---

## ➡️ Next Topic
**81. MongoDB Native Driver with Node.js** — the official `mongodb` driver: `MongoClient`, CRUD, errors and connection pooling.
