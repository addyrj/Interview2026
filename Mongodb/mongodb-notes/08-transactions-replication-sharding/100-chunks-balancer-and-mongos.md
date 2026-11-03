# 100. Chunks, Balancer and mongos
# हिंदी में: Chunks, Balancer और mongos

---

## 🔵 Simple Definition (English)
- **Chunk**: a contiguous range of shard-key values (default max size 128 MB) — the unit of data MongoDB moves between shards. Its range is recorded in `config.chunks`.
- **Balancer**: a background process on the config server primary that **splits** oversized chunks and **migrates** chunks from shards with more chunks to shards with fewer, so data stays even.
- **mongos**: the stateless router that applications connect to; it uses the cached chunk map to send each operation to the right shard(s) and merges the results.

## 🔵 सरल परिभाषा (Hindi)
- **Chunk**: shard-key values की एक निरंतर range (default अधिकतम 128 MB) — data की वह इकाई जिसे MongoDB shards के बीच move करता है। इसकी range `config.chunks` में दर्ज होती है।
- **Balancer**: config server primary पर चलने वाली background process जो बड़े chunks को **split** करती है और ज़्यादा chunks वाले shards से कम chunks वाले shards पर chunks **migrate** करती है ताकि data बराबर रहे।
- **mongos**: stateless router जिससे applications जुड़ती हैं; यह cached chunk map से हर operation को सही shard(s) पर भेजता है और results merge करता है।

---

## 🔴 Problem it Solves
Data grows and access patterns shift. Without automatic splitting and balancing, an initially even cluster drifts: one shard fills its disk while a new shard sits empty. Without a router, every application would need to know the chunk map and handle migrations itself. Chunks, balancer and mongos together make the cluster elastic: add a shard and data flows to it automatically, while applications stay unchanged.

## 🔴 यह क्यों बना? (Hindi)
Data बढ़ता है और access patterns बदलते हैं। Automatic splitting और balancing के बिना शुरू में बराबर cluster बिगड़ जाता है: एक shard की disk भर जाती है जबकि नया shard खाली रहता है। Router के बिना हर application को chunk map जानना और migrations संभालना पड़ता। Chunks, balancer और mongos मिलकर cluster को elastic बनाते हैं: shard जोड़ो तो data अपने आप उसमें बहता है, और applications वैसी की वैसी रहती हैं।

---

## 🟢 How it Works — Step by Step

**Chunks and splitting**
Step 1 → A new sharded collection starts with 1 chunk covering `MinKey → MaxKey` (hashed keys on empty collections are pre-split into 2 chunks per shard by default).
Step 2 → As a chunk grows beyond the max size (128 MB by default; configurable via `config.settings` `chunksize`, 1–1024 MB), it is **split** at a shard-key median into two chunks. Splits are cheap metadata changes.
Step 3 → A chunk whose documents all share ONE key value can't split — it becomes **jumbo**.

**Balancer migrations**
Step 4 → The balancer compares chunk counts per shard (MongoDB 6.0+ balances by **data size** per collection, not chunk count). If the difference exceeds the threshold, it picks a chunk to move.
Step 5 → Migration protocol: (1) donor shard clones the chunk's documents to the recipient, (2) applies changes made during the copy, (3) the config server atomically commits the new owner, (4) the donor deletes its copy asynchronously (`range deleter`).
Step 6 → Only ONE migration per shard at a time (except in newer versions with concurrent migrations on different shard pairs); you can limit the balancer to a **window** (e.g. 02:00–06:00).

**mongos routing**
Step 7 → mongos fetches and **caches** the chunk map from config servers.
Step 8 → For each operation it extracts the shard key: present → **targeted** to one (or a few) shard(s); absent → **broadcast**. For sorts/limits/aggregations it merges partial results.
Step 9 → If a chunk moved, the shard replies `StaleConfig`; mongos refreshes its map and retries transparently.

## 🟢 कैसे काम करता है? (Hindi)
**Chunks और splitting**
Step 1 → नया sharded collection `MinKey → MaxKey` वाले 1 chunk से शुरू होता है (खाली collection पर hashed keys default रूप से हर shard के लिए 2 chunks में pre-split होती हैं)।
Step 2 → Chunk max size (default 128 MB; `config.settings` के `chunksize` से बदलने योग्य, 1–1024 MB) से बड़ा हो तो shard-key median पर दो chunks में **split** होता है। Split सस्ता metadata बदलाव है।
Step 3 → जिस chunk के सारे documents की key value **एक ही** हो, वह split नहीं हो सकता — **jumbo** बन जाता है।

**Balancer migrations**
Step 4 → Balancer हर shard के chunks की गिनती तुलना करता है (MongoDB 6.0+ में chunk count की जगह collection के **data size** से balance करता है)। अंतर threshold से ज़्यादा हो तो एक chunk चुनकर move करता है।
Step 5 → Migration protocol: (1) donor shard chunk के documents recipient को clone करता है, (2) copy के दौरान हुए changes apply करता है, (3) config server atomically नया owner commit करता है, (4) donor अपनी copy asynchronous रूप से हटाता है (`range deleter`)।
Step 6 → हर shard पर एक समय में एक migration; balancer को **window** (जैसे 02:00–06:00) तक सीमित कर सकते हो।

**mongos routing**
Step 7 → mongos config servers से chunk map लाकर **cache** करता है।
Step 8 → हर operation से shard key निकालता है: मौजूद → एक (या कुछ) shard पर **targeted**; गायब → **broadcast**। Sort/limit/aggregation के partial results merge करता है।
Step 9 → Chunk move हो चुका हो तो shard `StaleConfig` लौटाता है; mongos अपना map refresh करके transparently retry करता है।

---

## 🟡 Real World Example
**Razorpay adds capacity before festival season**: they add shard #5 to a 4-shard cluster of the `transactions` collection. The balancer starts migrating chunks from the four full shards to the empty one, at night (balancer window 01:00–06:00) to avoid peak load. Application servers keep talking to the same two mongos routers; during each chunk move, a few requests receive `StaleConfig` internally and get retried automatically, so no customer sees an error.

## 🟡 Real Example Hindi mein
**Razorpay त्योहारी season से पहले capacity बढ़ाता है**: `transactions` collection के 4-shard cluster में shard #5 जोड़ा जाता है। Balancer चारों भरे shards से खाली shard पर chunks migrate करना शुरू करता है, peak load से बचने के लिए रात में (balancer window 01:00–06:00)। Application servers वही दो mongos routers इस्तेमाल करते रहते हैं; हर chunk move के दौरान कुछ requests को अंदर ही `StaleConfig` मिलता है और automatically retry हो जाती हैं, इसलिए किसी customer को error नहीं दिखता।

---

## 💻 Code Example — Basic

Run against the REAL local sharded cluster (2 shards, 1 mongos, MongoDB 8.0.4). Outputs observed:

```javascript
db = db.getSiblingDB('shop');

// Chunk map after sharding "orders" on hashed customerId (20,000 docs inserted)
db.getSiblingDB('config').chunks.find({ /* orders */ }, { min: 1, max: 1, shard: 1, _id: 0 });
// { min: { customerId: MinKey() }, max: { customerId: Long('0') }, shard: 's1' }
// { min: { customerId: Long('0') }, max: { customerId: MaxKey() }, shard: 's2' }
//   -> hashed key on an empty collection was pre-split: 2 chunks, one per shard

// Chunks per shard across the cluster
db.getSiblingDB('config').chunks.aggregate([{ $group: { _id: '$shard', c: { $sum: 1 } } }, { $sort: { _id: 1 } }]);
// [ { _id: 's1', c: 2 }, { _id: 's2', c: 1 } ]      (includes the separate "events" collection's chunk)

// Registered shards
db.getSiblingDB('config').shards.find({}, { _id: 1, host: 1 });
// [ { _id: 's1', host: 's1/127.0.0.1:27172' }, { _id: 's2', host: 's2/127.0.0.1:27173' } ]

// Balancer state
db.adminCommand({ balancerStatus: 1 }).mode;     // Output: 'full'  (balancer enabled)
sh.isBalancerRunning();                          // true only while a round is actually in progress
```

## 💻 Code Example — Advanced

Controlling the balancer and moving a chunk by hand (executed on the real cluster):

```javascript
// Manually move the chunk that contains customerId 'C7' to shard s1
db.adminCommand({ moveChunk: 'shop.orders', find: { customerId: 'C7' }, to: 's1' }).ok;
// Output: 1           (hashed key: `find` takes the original value, mongos hashes it for you)

// Stop the balancer (e.g. during backup), check, start again
db.adminCommand({ balancerStop: 1 }).ok;          // Output: 1
db.adminCommand({ balancerStatus: 1 }).mode;      // Output: 'off'
db.adminCommand({ balancerStart: 1 }).ok;         // Output: 1

// Limit the balancer to a nightly window (syntax reference)
db.getSiblingDB('config').settings.updateOne(
  { _id: 'balancer' },
  { $set: { activeWindow: { start: '01:00', stop: '06:00' } } },   // local time of config servers
  { upsert: true }
);

// Per-collection controls (syntax reference)
sh.disableBalancing('shop.orders');               // exclude one collection from balancing
sh.enableBalancing('shop.orders');

// Adjust max chunk size to 64 MB (syntax reference)
db.getSiblingDB('config').settings.updateOne({ _id: 'chunksize' }, { $set: { value: 64 } }, { upsert: true });

// Manual split at a value (ranged keys only; syntax reference)
sh.splitAt('shop.events', { ts: new Date('2026-01-01') });

// Find jumbo chunks
db.getSiblingDB('config').chunks.find({ jumbo: true });

// How a query is routed: SINGLE_SHARD vs SHARD_MERGE with 2 shards
db.orders.find({ customerId: 'C7' }).explain().queryPlanner.winningPlan.stage;  // 'SINGLE_SHARD'
db.orders.find({ n: 5 }).explain().queryPlanner.winningPlan.shards.length;      // 2  (broadcast)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Application connects ONLY to mongos instances; the driver load-balances between them
const uri = 'mongodb://mongos1.internal:27017,mongos2.internal:27017/shop';
await mongoose.connect(uri, {
  retryWrites: true,                     // survives chunk migration / primary stepdown hiccups
  w: 'majority',
  maxPoolSize: 50,                       // per-mongos pool; total = pool x app instances x mongos
});

// Observe routing in dev: explain shows SINGLE_SHARD vs SHARD_MERGE
const plan = await Order.find({ customerId: 'C7' }).explain('queryPlanner');
console.log(plan.queryPlanner.winningPlan.stage);   // 'SINGLE_SHARD' => targeted

// Health endpoint that reports balancer status via the admin DB
app.get('/admin/balancer', async (req, res) => {
  const admin = mongoose.connection.db.admin();
  const st = await admin.command({ balancerStatus: 1 });
  res.json({ mode: st.mode, inBalancerRound: st.inBalancerRound });  // e.g. { mode: 'full', inBalancerRound: false }
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Letting the balancer run during peak traffic
```javascript
// Wrong — migrations compete with production traffic for I/O and network
// Right — set an activeWindow (off-peak) in config.settings
```

❌ Mistake 2: Stopping the balancer and forgetting to restart it
✅ Correct: After `balancerStop` (for backups/maintenance), always `balancerStart`. Otherwise new shards stay empty and old shards fill up. Monitor `balancerStatus`.

❌ Mistake 3: Connecting to config servers or shards from the app
✅ Correct: Only mongos. Direct connections bypass routing and sharding-aware behaviours.

❌ Mistake 4: A single mongos
✅ Correct: Run at least two (often one per app host) so a mongos failure doesn't take the app down.

❌ Mistake 5: Using `sh.splitAt` / `moveChunk` as routine management
✅ Correct: Manual chunk operations are for pre-splitting or emergencies. Trust the balancer and fix the shard key if distribution is poor.

---

## 🧠 Tricky Interview Question

Q: The balancer is on, yet one shard has 90% of the data. Why?

Answer: Common causes: (1) a monotonic ranged shard key funnels all new inserts to one chunk, and migrations lag behind insert speed (in our test, 20,000 time-ordered documents were all on one shard with a single chunk); (2) jumbo chunks that can't split or move; (3) the balancer is disabled globally or for that collection (`sh.disableBalancing`), or limited by an `activeWindow`; (4) the unsharded collections of a database live on its primary shard, which is by design; (5) migrations failing due to `range deleter` backlog or long-running cursors. The first check is `balancerStatus`, then `config.chunks` distribution, then `jumbo` flags — and the long-term fix is almost always a better shard key, not a faster balancer.

---

## ⚫ Interview Questions + Answers

Q1: What exactly is a chunk?
A1: A metadata range `[min, max)` over shard-key values assigned to one shard. Documents belong to a chunk by their key; chunks are the unit of balancing. Default max 128 MB.

Q2: How does a chunk migration stay safe for reads/writes?
A2: The donor keeps serving the chunk during cloning, records writes made meanwhile and forwards them; only a brief critical section at commit blocks writes to that chunk. The config server atomically flips ownership; the donor then deletes orphaned documents in the background. mongos handles stale routing via `StaleConfig` retries.

Q3: What does mongos store?
A3: Nothing persistent. It caches routing metadata from config servers in memory and can be restarted or scaled freely.

Q4: How can you speed up initial loading into a new sharded collection?
A4: Use a hashed key with `numInitialChunks` (pre-splitting), or zone-based pre-splitting for ranged keys, and insert with `ordered: false` in parallel from multiple clients through multiple mongos.

Q5: What changed in 6.0 about balancing?
A5: The balancer balances by data size per collection rather than just chunk counts, and the default chunk size became 128 MB (from 64 MB in 5.x); autosplit moved to the shards themselves.

---

## 🔷 When to Use + When Not to Use
✅ Use / tune when:
- You add or remove shards (let the balancer redistribute)
- You need a maintenance window for balancing (`activeWindow`) or to pause it for backups

❌ Avoid when:
- Disabling the balancer permanently — cluster drifts out of balance
- Manually moving chunks routinely instead of fixing the shard key

---

## 📊 Visual Diagram
```
 chunk ranges of shop.orders (hashed customerId):
   [MinKey ──► 0)  -> s1        [0 ──► MaxKey) -> s2      (stored in config.chunks)

 Add shard s3:
   s1 ■■■■■■   s2 ■■■■■■   s3 (empty)
        │ balancer: donor clones ──► recipient ──► config commits new owner ──► donor deletes
   s1 ■■■■    s2 ■■■■    s3 ■■■■

 mongos routing
   find({customerId:'C7'}) ─► chunk map ─► s2 only                (SINGLE_SHARD)
   find({n:5})             ─► no key    ─► s1 + s2, merge          (SHARD_MERGE)
   StaleConfig? ─► refresh chunk map ─► retry
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chunk | Shard-key range owned by a shard | Shard की owned shard-key range |
| Split | Divide a big chunk in two | बड़े chunk को दो में बाँटना |
| Migration | Move chunk between shards | Chunk को shards के बीच move करना |
| Balancer | Auto-moves chunks to even out data | Data बराबर करने के लिए chunks move करने वाला |
| activeWindow | Time window when balancer may run | Balancer चलने की समय-खिड़की |
| Jumbo chunk | Oversized unsplittable chunk | न बँटने वाला बड़ा chunk |
| StaleConfig | Router's chunk map is outdated | Router का chunk map पुराना है |
| Range deleter | Cleans orphan docs after migration | Migration के बाद orphan docs हटाता है |

---

## ⚡ 3-Line Summary
English:
1. Chunks are shard-key ranges (default 128 MB) that split as they grow; the balancer migrates them between shards to keep data even.
2. mongos is a stateless router using a cached chunk map: shard key present means targeted, absent means scatter-gather; stale maps are retried automatically.
3. Run 2+ mongos, restrict balancing to off-peak windows, never leave the balancer stopped, and fix imbalance via a better shard key.

Hindi:
1. Chunks shard-key ranges हैं (default 128 MB) जो बढ़ने पर split होते हैं; balancer data बराबर रखने के लिए उन्हें shards के बीच migrate करता है।
2. mongos cached chunk map वाला stateless router है: shard key हो तो targeted, न हो तो scatter-gather; पुराना map अपने आप retry होता है।
3. 2+ mongos चलाओ, balancing को off-peak window तक सीमित करो, balancer को कभी बंद मत छोड़ो, और असंतुलन को बेहतर shard key से सुधारो।

---

## ➡️ Next Topic
**101. CAP Theorem and MongoDB** — Where MongoDB sits in the consistency/availability/partition-tolerance trade-off.
