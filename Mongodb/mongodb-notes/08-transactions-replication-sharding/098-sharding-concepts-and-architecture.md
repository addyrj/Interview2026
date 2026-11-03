# 98. Sharding — Concepts and Architecture
# हिंदी में: Sharding — Concepts और Architecture

---

## 🔵 Simple Definition (English)
**Sharding** is MongoDB's method of **horizontal scaling**: splitting one logical collection into pieces (**chunks**) spread across several independent servers called **shards**. Each shard is itself a replica set. A router (**mongos**) hides the split so applications still see ONE collection, and **config servers** store the map of which chunk lives where.

## 🔵 सरल परिभाषा (Hindi)
**Sharding** MongoDB का **horizontal scaling** तरीका है: एक logical collection को टुकड़ों (**chunks**) में बाँटकर कई स्वतंत्र servers, यानी **shards**, पर फैलाना। हर shard खुद एक replica set होता है। एक router (**mongos**) इस बँटवारे को छुपाता है ताकि application को अब भी एक ही collection दिखे, और **config servers** यह map रखते हैं कि कौन सा chunk कहाँ है।

---

## 🔴 Problem it Solves
A replica set copies the SAME data everywhere, so it cannot exceed one machine's disk, RAM or write throughput. **Vertical scaling** (a bigger machine) hits a ceiling and gets exponentially expensive. When Flipkart's `orders` collection reaches 10 TB or 200k writes/second, no single server can hold or serve it. Sharding spreads data and load across N machines so capacity grows by adding shards.

## 🔴 यह क्यों बना? (Hindi)
Replica set हर जगह एक ही data की copy रखता है, इसलिए वह एक machine की disk, RAM या write throughput से आगे नहीं जा सकता। **Vertical scaling** (बड़ी machine) की एक सीमा है और वह बहुत महँगी होती जाती है। जब Flipkart की `orders` collection 10 TB या 2 लाख writes/second पर पहुँचती है, तो कोई एक server उसे रख या serve नहीं कर सकता। Sharding data और load को N machines में बाँटता है, इसलिए shards जोड़कर capacity बढ़ती है।

---

## 🟢 How it Works — Step by Step

A sharded cluster has three kinds of components:
Step 1 → **Shards** — each a replica set holding a subset of the data (chunks).
Step 2 → **mongos** — stateless query routers. Applications connect to mongos, never directly to shards. Run several for availability.
Step 3 → **Config servers** — a replica set (CSRS) storing cluster metadata: shard list, collection shard keys, chunk ranges (`config.chunks`).
Step 4 → You pick a **shard key** field(s) for a collection with `sh.shardCollection(ns, key)`.
Step 5 → MongoDB partitions the key space into **chunks** (ranges, default max 128 MB). A **hashed** key hashes values first; a **ranged** key keeps order.
Step 6 → On a request, mongos reads the chunk map (cached), and either **targets** one shard (query contains the shard key) or **scatter-gathers** across all shards (it doesn't), merging results.
Step 7 → The **balancer** moves chunks to keep shard sizes even.
Step 8 → Every database has a **primary shard** which holds its unsharded collections.

## 🟢 कैसे काम करता है? (Hindi)
Sharded cluster में तीन तरह के components हैं:
Step 1 → **Shards** — हर एक replica set जिसमें data का एक हिस्सा (chunks) है।
Step 2 → **mongos** — stateless query routers। Applications mongos से जुड़ती हैं, shards से सीधे कभी नहीं। Availability के लिए कई चलाओ।
Step 3 → **Config servers** — एक replica set (CSRS) जो cluster metadata रखता है: shard list, collections की shard keys, chunk ranges (`config.chunks`)।
Step 4 → Collection के लिए `sh.shardCollection(ns, key)` से **shard key** चुनो।
Step 5 → MongoDB key space को **chunks** (ranges, default अधिकतम 128 MB) में बाँटता है। **Hashed** key values को पहले hash करती है; **ranged** key क्रम बनाए रखती है।
Step 6 → Request आने पर mongos chunk map (cached) देखता है, और या तो एक shard को **target** करता है (query में shard key हो) या सभी shards पर **scatter-gather** करके results merge करता है।
Step 7 → **Balancer** shards का size बराबर रखने के लिए chunks move करता है।
Step 8 → हर database का एक **primary shard** होता है जिसमें उसकी unsharded collections रहती हैं।

---

## 🟡 Real World Example
**Flipkart's orders store during Big Billion Days**: `orders` is sharded on `{ customerId: 'hashed' }` over 12 shards, each a 3-node replica set. A customer's "My Orders" query includes `customerId`, so mongos routes it to exactly one shard (fast, targeted). A finance report with no `customerId` is scatter-gathered across all 12 shards and run on a secondary. Before the sale, ops add 4 more shards; the balancer migrates chunks in the background while traffic continues.

## 🟡 Real Example Hindi mein
**Big Billion Days में Flipkart का orders store**: `orders` को `{ customerId: 'hashed' }` पर 12 shards में shard किया गया है, हर shard 3-node replica set है। Customer की "My Orders" query में `customerId` होता है, इसलिए mongos उसे ठीक एक shard पर भेजता है (तेज़, targeted)। बिना `customerId` वाली finance report सभी 12 shards पर scatter-gather होती है और secondary पर चलती है। Sale से पहले ops 4 और shards जोड़ते हैं; traffic चलते हुए balancer background में chunks migrate करता है।

---

## 💻 Code Example — Basic

I built a REAL sharded cluster locally with MongoDB 8.0.4: 1 config server (replica set `cfg`), 2 shards (`s1`, `s2`, single-node replica sets) and 1 mongos. Setup (shell):

```bash
mongod --configsvr --replSet cfg --port 27171 --dbpath cfg --fork --logpath cfg.log   # config server
mongod --shardsvr  --replSet s1  --port 27172 --dbpath sh1 --fork --logpath sh1.log   # shard 1
mongod --shardsvr  --replSet s2  --port 27173 --dbpath sh2 --fork --logpath sh2.log   # shard 2
# rs.initiate(...) on each of the three, then:
mongos --configdb cfg/127.0.0.1:27171 --port 27170 --fork --logpath mongos.log        # router
```

Then in mongosh connected to **mongos** (port 27170). Observed outputs:

```javascript
sh.addShard('s1/127.0.0.1:27172');       // register shard 1 (replicaSetName/host)
sh.addShard('s2/127.0.0.1:27173');       // register shard 2
sh.enableSharding('shop');               // allow collections in db "shop" to be sharded

db = db.getSiblingDB('shop');
db.orders.createIndex({ customerId: 'hashed' });             // the shard key needs a supporting index
sh.shardCollection('shop.orders', { customerId: 'hashed' }); // shard it by hashed customerId
// Output: collectionsharded: 'shop.orders'

// Insert 20,000 docs over 2,000 customers
const d = []; for (let i = 0; i < 20000; i++) d.push({ customerId: 'C' + (i % 2000), n: i });
db.orders.insertMany(d);

db.orders.getShardDistribution();
// Shard s2: docs 10270 (51.35 %)   chunks 1
// Shard s1: docs 9730  (48.65 %)   chunks 1
// Totals:   docs 20000             chunks 2
//   -> hashing spread the data almost evenly (exact split varies per run)
```

## 💻 Code Example — Advanced

Targeted vs scatter-gather, verified with `explain()` on the same cluster:

```javascript
// Query WITH the shard key => mongos targets ONE shard
db.orders.find({ customerId: 'C7' }).explain().queryPlanner.winningPlan.stage;
// Output: 'SINGLE_SHARD'

db.orders.find({ customerId: 'C7' }).explain().queryPlanner.winningPlan.shards.length;
// Output: 1

// Query WITHOUT the shard key => scatter-gather to ALL shards
db.orders.find({ n: 5 }).explain().queryPlanner.winningPlan.shards.length;
// Output: 2

// $in on a shard key with several values may still hit multiple shards:
db.orders.find({ customerId: { $in: ['C1', 'C2'] } }).explain().queryPlanner.winningPlan.stage;
// Output: 'SINGLE_SHARD' here (both hashed values fell in the same chunk) - may be SHARD_MERGE elsewhere

// Look at cluster metadata held by config servers
db.getSiblingDB('config').shards.find({}, { _id: 1, host: 1 });
// [ { _id: 's1', host: 's1/127.0.0.1:27172' }, { _id: 's2', host: 's2/127.0.0.1:27173' } ]

db.getSiblingDB('config').collections.find({ _id: 'shop.orders' });
// key: { customerId: 'hashed' }, unique: false

sh.status();                 // human-readable cluster overview (shards, databases, balancer, chunks)
db.orders.getShardDistribution();  // per-shard docs/data (shown above)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Application code is IDENTICAL; only the connection string points at mongos routers
await mongoose.connect(
  'mongodb://mongos1:27017,mongos2:27017/shop',   // list several mongos, NOT shards/config servers
  { w: 'majority', retryWrites: true }
);

// Always include the shard key in hot queries so mongos can target one shard
app.get('/api/orders', async (req, res) => {
  const orders = await Order.find({ customerId: req.user.id }) // contains shard key => targeted
    .sort({ _id: -1 }).limit(20).lean();
  res.json(orders);
});

// Schema-level declaration (documents the key; sharding itself is configured in the cluster)
orderSchema.set('shardKey', { customerId: 'hashed' });
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Sharding too early
```text
// Wrong — shard when "we might get big". Adds mongos + config servers + operational complexity
// Right — first optimise indexes/queries, scale vertically, use replicas for reads; shard when
//         data size, working set or write throughput truly exceed one replica set
```

❌ Mistake 2: Connecting the app directly to a shard
✅ Correct: The application must connect only to mongos. Direct shard writes bypass routing metadata and can corrupt placement assumptions.

❌ Mistake 3: Queries without the shard key
✅ Correct: They scatter-gather across ALL shards (we measured 2 of 2 shards), so latency is the slowest shard's and cost grows with shard count.

❌ Mistake 4: A single config server or single mongos
✅ Correct: Config servers must be a 3-member replica set and run at least 2 mongos in production, otherwise the whole cluster is a single point of failure.

❌ Mistake 5: Expecting a sharded collection to be unique on any field
✅ Correct: Unique indexes must include the shard key as a prefix (or be the shard key); otherwise MongoDB cannot enforce uniqueness across shards.

---

## 🧠 Tricky Interview Question

Q: You shard by `{ customerId: 'hashed' }`. Is `db.orders.find({ orderId: 'O1' })` fast? And `db.orders.find({ customerId: 'C7' }).sort({ createdAt: -1 })`?

Answer: The first one is slow-ish: `orderId` is not the shard key, so mongos scatter-gathers to every shard (we saw 2 of 2) and each runs the query (hopefully with an index on `orderId`). The second is good: `customerId` targets one shard; with an index on `{ customerId: 1, createdAt: -1 }` that shard serves the sort from the index. Design the shard key around your most frequent, latency-critical query, and keep other lookups index-backed and rare, or maintain a lookup collection.

---

## ⚫ Interview Questions + Answers

Q1: Replication vs sharding?
A1: Replication = copies of the same data (availability, read scale). Sharding = partitions of different data (storage and write scale). Production uses both: each shard is a replica set.

Q2: What does mongos do?
A2: It's a stateless router. It caches the chunk map from config servers, targets or scatter-gathers queries, merges results (sorts, limits, aggregation merge stage), and routes writes. It stores no data.

Q3: What are config servers?
A3: A replica set (CSRS) holding cluster metadata — shards, databases, collections, chunk ranges, balancer settings. If they're unavailable, the cluster can still serve existing routed traffic from cached metadata but cannot split/migrate chunks.

Q4: When should you shard?
A4: When the dataset exceeds what one replica set can store, the working set exceeds RAM, or sustained write throughput exceeds a single primary — and after optimising everything else.

Q5: Can transactions span shards?
A5: Yes since 4.2 (distributed transactions), with higher latency; design to keep transactions within one shard when possible.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data in the multi-TB range, or write throughput beyond one primary
- Geo-locality needs (zone sharding: EU users' data on EU shards)

❌ Avoid when:
- A single replica set still comfortably handles the load (sharding is hard to undo; resharding exists since 5.0 but is heavy)
- Your queries rarely include a good shard key candidate

---

## 📊 Visual Diagram
```
                    ┌────────── Application (Express) ──────────┐
                    └──────────────────┬────────────────────────┘
                                       │
                         ┌─────────────┴─────────────┐
                         ▼                           ▼
                    ┌─────────┐                 ┌─────────┐   stateless routers
                    │ mongos1 │                 │ mongos2 │
                    └────┬────┘                 └────┬────┘
        reads chunk map  │        ┌──────────────────┘
                         ▼        ▼
                 ┌──────────────────────┐
                 │ Config servers (CSRS)│  shards, chunk ranges
                 └──────────────────────┘
        targeted  │              │  scatter-gather
         ┌────────┴──┐     ┌─────┴─────┐     ┌───────────┐
         │ Shard s1  │     │ Shard s2  │     │ Shard s3  │   each = replica set
         │ chunks    │     │ chunks    │     │ chunks    │
         │ [P][S][S] │     │ [P][S][S] │     │ [P][S][S] │
         └───────────┘     └───────────┘     └───────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Shard | Replica set holding part of the data | Data का हिस्सा रखने वाला replica set |
| mongos | Query router | Query router |
| Config server | Stores cluster metadata | Cluster metadata रखने वाला server |
| Shard key | Field(s) deciding data placement | Data की जगह तय करने वाले field(s) |
| Chunk | Contiguous range of shard-key values | Shard-key values की निरंतर range |
| Targeted query | Routed to one shard | एक shard पर भेजी गई query |
| Scatter-gather | Query sent to all shards | सभी shards पर भेजी गई query |
| Horizontal scaling | Adding more machines | और machines जोड़कर scale करना |

---

## ⚡ 3-Line Summary
English:
1. Sharding splits a collection into chunks across shards (each a replica set) to scale storage and writes beyond one machine.
2. Apps talk to mongos routers; config servers hold the chunk map; queries with the shard key are targeted, others scatter-gather.
3. Shard late and deliberately; the shard key decides performance, so design it around your main query.

Hindi:
1. Sharding collection को chunks में बाँटकर shards (हर एक replica set) पर फैलाता है ताकि storage और writes एक machine से आगे scale हों।
2. Apps mongos routers से बात करती हैं; config servers chunk map रखते हैं; shard key वाली queries targeted होती हैं, बाकी scatter-gather।
3. Sharding देर से और सोच-समझकर करो; shard key ही performance तय करती है, इसलिए उसे अपनी मुख्य query के हिसाब से design करो।

---

## ➡️ Next Topic
**99. Shard Keys — Choosing a Good One** — Cardinality, frequency, monotonic growth and the trade-off between hashed and ranged keys.
