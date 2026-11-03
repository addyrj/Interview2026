# 99. Shard Keys — Choosing a Good One
# हिंदी में: Shard Keys — अच्छी key कैसे चुनें

---

## 🔵 Simple Definition (English)
A **shard key** is the indexed field (or compound of fields) MongoDB uses to decide which chunk, and therefore which shard, each document belongs to. It is the single most important sharding decision: it controls data distribution, write scalability and whether queries are targeted or scatter-gather. A good key has **high cardinality**, **low frequency**, and **non-monotonic** change, and appears in your most common queries.

## 🔵 सरल परिभाषा (Hindi)
**Shard key** वह indexed field (या fields का combination) है जिससे MongoDB तय करता है कि हर document किस chunk में, और इसलिए किस shard पर, जाएगा। यह sharding का सबसे अहम फैसला है: यह data distribution, write scalability और queries के targeted या scatter-gather होने को नियंत्रित करता है। अच्छी key में **high cardinality**, **low frequency** और **non-monotonic** बदलाव होता है, और वह आपकी सबसे आम queries में आती है।

---

## 🔴 Problem it Solves
A bad shard key quietly ruins a cluster: all new writes hit ONE shard (a **hotspot**), one giant chunk that cannot be split (a **jumbo chunk**), or every query fans out to all shards. Because the key was historically immutable and hard to change, a wrong choice meant an expensive migration. Knowing the criteria upfront avoids those failures.

## 🔴 यह क्यों बना? (Hindi)
खराब shard key चुपचाप cluster बिगाड़ देती है: सारी नई writes **एक** shard पर (**hotspot**), एक विशाल chunk जो split नहीं हो सकता (**jumbo chunk**), या हर query सभी shards पर फैल जाती है। पहले key बदलना लगभग असंभव था, इसलिए गलत चुनाव का मतलब महँगा migration। शुरू में ही criteria जानने से ये failures बचती हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **Cardinality**: the key must have MANY distinct values. A key with 5 values (e.g. `status`) can never create more than 5 splittable chunk ranges.
Step 2 → **Frequency**: no single value should dominate. If 40% of documents have `country: "IN"`, all of them land in one unsplittable chunk (jumbo).
Step 3 → **Monotonic change**: avoid keys that always increase (`_id` ObjectId, timestamps, auto-increment). With a RANGED key every new insert falls in the max chunk on ONE shard, so write throughput = one shard. Use a **hashed** key or add a prefix to fix this.
Step 4 → **Query isolation**: include the key (or its prefix) in common queries so mongos targets a single shard.
Step 5 → Choose between **hashed** (even distribution, no efficient range queries on the key) and **ranged** (range queries stay on few shards, risk of hotspots).
Step 6 → **Compound keys** such as `{ tenantId: 1, createdAt: 1 }` or `{ region: 1, customerId: 'hashed' }` (compound keys containing a hashed field need MongoDB 7.2+) balance isolation and distribution.
Step 7 → You can evolve the key: **`refineCollectionShardKey`** (4.4+) appends fields; **`reshardCollection`** (5.0+) changes it entirely; shard-key fields are mutable since 4.2 (updates may move the doc).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Cardinality**: key में बहुत सारे अलग-अलग values हों। 5 values वाली key (जैसे `status`) 5 से ज़्यादा splittable ranges नहीं बना सकती।
Step 2 → **Frequency**: कोई एक value हावी न हो। 40% documents में `country: "IN"` हो तो वे सब एक unsplittable (jumbo) chunk में जाएँगे।
Step 3 → **Monotonic बदलाव**: हमेशा बढ़ने वाली keys (`_id` ObjectId, timestamps, auto-increment) से बचो। RANGED key में हर नया insert max chunk, यानी **एक** shard पर जाता है, तो write throughput = एक shard। **Hashed** key या prefix इससे बचाता है।
Step 4 → **Query isolation**: आम queries में key (या उसका prefix) रखो ताकि mongos एक shard को target करे।
Step 5 → **Hashed** (समान distribution, key पर range queries efficient नहीं) और **ranged** (range queries कम shards पर, hotspot का जोखिम) में से चुनो।
Step 6 → `{ tenantId: 1, createdAt: 1 }` या `{ region: 1, customerId: 'hashed' }` जैसी **compound keys** isolation और distribution का संतुलन देती हैं।
Step 7 → Key बदली जा सकती है: **`refineCollectionShardKey`** (4.4+) fields जोड़ता है; **`reshardCollection`** (5.0+) पूरी key बदलता है; shard-key fields 4.2 से mutable हैं।

---

## 🟡 Real World Example
**Swiggy order events**: first design sharded `events` on `{ createdAt: 1 }`. All new events carry the latest timestamp, so every insert hit the single "newest" chunk on one shard while the others sat idle — during dinner rush that shard saturated. The fix: `{ orderId: 'hashed' }`. Writes now spread across all shards; lookups by `orderId` are targeted, while "all events for this customer" needs an index on `customerId` and is scatter-gather.

## 🟡 Real Example Hindi mein
**Swiggy order events**: पहले design में `events` को `{ createdAt: 1 }` पर shard किया गया। सारे नए events का timestamp सबसे ताज़ा होता है, इसलिए हर insert एक shard के "सबसे नए" chunk पर गिरा और बाकी shards खाली बैठे — dinner rush में वह shard saturate हो गया। Fix: `{ orderId: 'hashed' }`। अब writes सभी shards में फैलती हैं।

---

## 💻 Code Example — Basic

Verified on the real 2-shard local cluster (MongoDB 8.0.4, described in topic 98).

Bad key: monotonic timestamp (ranged). I inserted 20,000 time-ordered events:
```javascript
db = db.getSiblingDB('shop');
sh.shardCollection('shop.events', { ts: 1 });               // RANGED on an always-increasing field
const d = [];
for (let i = 0; i < 20000; i++) d.push({ ts: new Date(1700000000000 + i * 1000), n: i });
db.events.insertMany(d);                                    // simulate time-ordered traffic

db.events.aggregate([{ $collStats: { storageStats: {} } }, { $project: { shard: 1, count: '$storageStats.count' } }]);
// Output: [ { shard: 's1', count: 20000 } ]       <- ALL 20,000 docs on ONE shard (hotspot)

db.getSiblingDB('config').chunks.find({ /* events chunk */ }, { min: 1, max: 1, shard: 1, _id: 0 });
// { min: { ts: MinKey() }, max: { ts: MaxKey() }, shard: 's1' }   <- one chunk covers the whole range
```

Good key: hashed `customerId` (from topic 98):
```javascript
sh.shardCollection('shop.orders', { customerId: 'hashed' });
// 20,000 docs -> s1: 9,730 (48.65%)   s2: 10,270 (51.35%)    <- even spread
```

## 💻 Code Example — Advanced

Compound and refinable keys (syntax reference — the evaluating commands below were not all executed in the local test cluster):

```javascript
// 1. Tenant isolation + even spread inside each tenant (multi-tenant SaaS)
db.orders.createIndex({ tenantId: 1, orderId: 1 });
sh.shardCollection('shop.orders', { tenantId: 1, orderId: 1 });
//  find({ tenantId: 'acme' })            -> targeted (prefix match)
//  find({ tenantId: 'acme', orderId: X })-> single shard

// 2. Compound hashed key (MongoDB 7.2+): range on region, hash on customer
sh.shardCollection('shop.orders', { region: 1, customerId: 'hashed' });

// 3. Pre-split a hashed key to avoid a slow start on an EMPTY collection
sh.shardCollection('shop.logs', { deviceId: 'hashed' }, false, { numInitialChunks: 8 });

// 4. Existing collection with a weak key: append a suffix field (4.4+)
db.orders.createIndex({ tenantId: 1, orderId: 1 });
db.adminCommand({ refineCollectionShardKey: 'shop.orders', key: { tenantId: 1, orderId: 1 } });

// 5. Replace the whole key online (5.0+): data is copied, then switched
db.adminCommand({ reshardCollection: 'shop.events', key: { eventId: 'hashed' } });

// 6. Inspect distribution and jumbo chunks
db.events.getShardDistribution();
db.getSiblingDB('config').chunks.find({ jumbo: true });
```

Quick evaluation checklist as code:
```javascript
// Estimate cardinality & skew of a candidate key BEFORE sharding
db.orders.aggregate([
  { $group: { _id: '$customerId', c: { $sum: 1 } } },   // frequency per key value
  { $sort: { c: -1 } }, { $limit: 5 }                    // top heavy values
]);
// If the top value holds a large share of all documents, it will form a jumbo chunk.
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Make the shard key part of every hot query and every document insert
orderSchema.add({ tenantId: { type: String, required: true } });  // shard key field must exist

// Always supply the key => single-shard routing
async function ordersForTenant(tenantId, limit = 20) {
  return Order.find({ tenantId })                 // targeted: prefix of {tenantId, orderId}
    .sort({ orderId: 1 }).limit(limit).lean();
}

// Updates/deletes on sharded collections must include the full shard key or _id
// (in 8.0 some multi-shard cases are allowed, but targeted ops are much cheaper)
await Order.updateOne({ tenantId, orderId }, { $set: { status: 'PACKED' } });
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Monotonic ranged key
```javascript
sh.shardCollection('shop.events', { _id: 1 });         // Wrong: ObjectId increases => hotspot
sh.shardCollection('shop.events', { _id: 'hashed' });  // Right: spreads writes (loses range scans on _id)
```

❌ Mistake 2: Low-cardinality key
✅ Correct: `{ status: 1 }` (4 values) or `{ country: 1 }` creates a handful of huge chunks that never split. Combine with a high-cardinality field: `{ country: 1, customerId: 1 }`.

❌ Mistake 3: Choosing a key that no query uses
✅ Correct: Even perfectly spread data is slow if every query is scatter-gather. Start from your access patterns.

❌ Mistake 4: Hashed key and range queries
✅ Correct: `find({ customerId: { $gt: 'C100' } })` on a hashed key must hit all shards, because adjacent values are hashed far apart.

❌ Mistake 5: Forgetting the key must exist in documents
✅ Correct: Documents missing the key are placed as `null`, concentrating them in one chunk (we inserted `{n:1}` without `customerId` and it was accepted). Enforce with schema `required`.

---

## 🧠 Tricky Interview Question

Q: Is a hashed `_id` shard key always better than a ranged `_id` key?

Answer: It's better for **write distribution** — ObjectIds are monotonic so ranged `_id` sends all inserts to the last chunk (we saw 20,000 of 20,000 documents on one shard). But hashed has costs: range queries and sorts on `_id` become scatter-gather, and "data locality" is lost (documents of one customer scatter everywhere). If most queries are `find({customerId})`, then `customerId` (hashed, or compound with another field) is the better key, because it both distributes writes AND targets reads. The best key is the one aligned with the dominant query plus good distribution, not simply "hash everything".

---

## ⚫ Interview Questions + Answers

Q1: What are the properties of a good shard key?
A1: High cardinality, low frequency (even value distribution), non-monotonic change, and presence in common queries (query isolation). A compound key often achieves this mix.

Q2: Hashed vs ranged sharding?
A2: Hashed gives an even spread and good insert scaling but kills range queries on the key. Ranged keeps contiguous values together (efficient range queries, zone sharding) but risks hotspots with monotonic keys.

Q3: What is a jumbo chunk?
A3: A chunk larger than the max size (128 MB default) that cannot be split because all documents share one shard-key value. The balancer won't move it automatically (until 5.0+ improvements). Fix with a more granular key (`refineCollectionShardKey`) or resharding.

Q4: Can you change a shard key?
A4: Yes: `refineCollectionShardKey` (4.4+) adds suffix fields; `reshardCollection` (5.0+) changes it completely online. Both are heavy operations — plan carefully.

Q5: Are shard key values mutable?
A5: Since 4.2 the shard key VALUE of a document can be updated (via `updateOne` with the full key in the filter or in a transaction), and the document may migrate to another shard. The field itself must remain present.

---

## 🔷 When to Use + When Not to Use
✅ Use hashed key when:
- Write-heavy, point-lookup workloads (events, logs, orders by id/customer)

✅ Use ranged / compound key when:
- Range queries matter, multi-tenant isolation, or zone sharding (data locality by region)

❌ Avoid:
- Timestamps/ObjectIds/auto-increment alone as ranged keys; low-cardinality fields alone

---

## 📊 Visual Diagram
```
 MONOTONIC RANGED KEY (ts)              HASHED KEY (customerId)
 ───────────────────────────            ───────────────────────────
 writes ─► [chunk MAX] on s1            writes ─► hash(key) ─► spread
 s1 ███████████ (hot)                   s1 █████
 s2 ░                                   s2 █████
 s3 ░                                   s3 █████
 Result: one shard bottleneck           Result: parallel writes

 Checklist:  cardinality ↑   frequency ↓   monotonic ✗   in queries ✓
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cardinality | Number of distinct key values | Key के अलग-अलग values की संख्या |
| Frequency | How often a value repeats | Value कितनी बार दोहराई जाती है |
| Monotonic | Always increasing/decreasing | हमेशा बढ़ने/घटने वाला |
| Hotspot | One shard taking all load | एक shard पर सारा load |
| Jumbo chunk | Unsplittable oversized chunk | न बँटने वाला बड़ा chunk |
| Hashed key | Key hashed for even spread | समान फैलाव के लिए hash की गई key |
| `refineCollectionShardKey` | Append fields to key (4.4+) | Key में fields जोड़ना |
| `reshardCollection` | Change key online (5.0+) | Key पूरी तरह बदलना |

---

## ⚡ 3-Line Summary
English:
1. A good shard key has high cardinality, low frequency, no monotonic growth, and appears in your main queries.
2. Monotonic ranged keys create hotspots (20,000 of 20,000 docs landed on one shard in our test); hashed keys spread writes but lose range queries.
3. Use compound keys for tenant isolation, and fix mistakes with `refineCollectionShardKey` or `reshardCollection`.

Hindi:
1. अच्छी shard key में high cardinality, low frequency, कोई monotonic growth नहीं होती, और वह आपकी मुख्य queries में आती है।
2. Monotonic ranged keys hotspot बनाती हैं (हमारे test में 20,000 में से 20,000 docs एक shard पर); hashed keys writes फैलाती हैं पर range queries खो देती हैं।
3. Tenant isolation के लिए compound keys इस्तेमाल करो, और गलतियाँ `refineCollectionShardKey` या `reshardCollection` से सुधारो।

---

## ➡️ Next Topic
**100. Chunks, Balancer and mongos** — How chunks split and migrate, and how mongos routes requests.
