# 42. Database Sharding
# हिंदी में: Sharding — डेटा को कई अलग-अलग database सर्वरों (shards) में बाँटना, ताकि writes और storage कई मशीनों में फैल जाएँ

---

## 🔵 Simple Definition (English)
**Sharding** is horizontal partitioning **across multiple database servers**. Each **shard** holds a subset of the rows (e.g. users 1–10M on shard A, 10–20M on shard B). A **shard key** decides which shard a row lives on, and a **router** (app code, proxy, or the DB itself) sends each query to the right shard.
It scales **writes, storage, and CPU** beyond a single machine, at the cost of significant complexity.

## 🔵 सरल परिभाषा (Hindi)
Sharding में डेटा कई DB सर्वरों में बँट जाता है — जैसे कुछ users एक सर्वर पर, बाक़ी दूसरे पर। Shard key (जैसे user_id) तय करती है कि row किस सर्वर पर जाएगी।
इससे writes और storage कई मशीनों में फैलते हैं, पर सिस्टम काफ़ी जटिल हो जाता है।

---

## 🔴 Problem it Solves
After vertical scaling, read replicas, caching and partitioning, a single primary can still hit limits:
- **Write throughput:** one primary can only commit so many transactions per second.
- **Storage:** tens of TB on one machine → slow backups and restores, long failovers.
- **Working set:** hot data no longer fits in one machine's RAM.
- **Blast radius:** one DB down = everyone down.

Sharding splits the data so **each shard handles a fraction of the load**; add shards to grow.

## 🔴 यह क्यों बना? (Hindi)
Vertical scaling, replicas, cache, partitioning के बाद भी एक primary की writes की सीमा है, storage बहुत बड़ा हो जाता है, और hot डेटा RAM में नहीं समाता।
Sharding से हर सर्वर पर load का एक हिस्सा आता है; ज़रूरत हो तो और shards जोड़ो। एक shard गिरे तो सिर्फ़ कुछ यूज़र प्रभावित होते हैं।

---

## 🟢 How it Works — Step by Step

### Architecture

```
                           App / API
                              │
                     ┌────────▼────────┐
                     │  Shard Router   │  shard = f(shard_key)
                     │ (app lib/proxy/ │  e.g. hash(user_id) % N  or lookup table
                     │  Vitess/Citus)  │
                     └──┬─────┬─────┬──┘
                        │     │     │
                 ┌──────▼┐ ┌──▼────┐ ┌▼──────┐
                 │Shard 0│ │Shard 1│ │Shard 2│   each = primary + replicas
                 │users  │ │users  │ │users  │
                 │0,3,6..│ │1,4,7..│ │2,5,8..│
                 └───────┘ └───────┘ └───────┘
```

### Sharding strategies

```
1. Hash-based:     shard = hash(user_id) % N
   ✅ even distribution   ❌ changing N moves almost all data → use consistent hashing or
                             many LOGICAL shards (e.g. 4096) mapped to fewer physical servers

2. Range-based:    user_id 1–1M → S0, 1M–2M → S1 ...    (or by date)
   ✅ range scans, easy to split ranges   ❌ hotspots (newest range gets all writes)

3. Directory / lookup-based:  table: tenant_id → shard
   ✅ flexible, move single tenant anytime, big tenants get own shard
   ❌ lookup service = extra hop + must be highly available (cache it)

4. Geo-based:      India users → Mumbai shard, EU users → Frankfurt shard
   ✅ data residency (GDPR, RBI data localization), low latency   ❌ uneven sizes
```

### Logical shards (the trick everyone uses)

```
Create MANY logical shards up front (e.g. 1024), map them to a few physical DBs:
  logical 0–255   → db-server-1
  logical 256–511 → db-server-2
  logical 512–767 → db-server-3
  logical 768–1023→ db-server-4
shard_id = hash(user_id) % 1024   ← never changes
To scale: move some logical shards to a new server (copy + switch mapping). No re-hashing.
(Instagram: thousands of logical shards as Postgres schemas; Notion: 480 logical shards)
```

### Choosing the shard key — the most important decision

```
Good shard key:
  ✓ High cardinality (millions of distinct values)
  ✓ Even distribution of data AND traffic (no celebrity hotspots)
  ✓ Present in almost every query → single-shard queries
  ✓ Keeps data that's queried/transacted together on the SAME shard (co-location)
     e.g. shard by user_id → user's orders, addresses, wallet all on one shard ✓
     e.g. shard by tenant_id for SaaS → every tenant's data together ✓

Bad shard key:
  ✗ created_at (all new writes → one shard)
  ✗ country (India shard = 90% of data)
  ✗ status (few values)
```

### The hard parts

```
Cross-shard queries:   "top 10 restaurants across all users" → scatter-gather to all shards,
                       merge results → slow; better: separate analytics store/search index
Cross-shard txns:      transfer between users on different shards → no single ACID txn
                       → saga / 2PC / design so related data shares a shard
Global unique IDs:     auto-increment per shard collides → Snowflake IDs, UUIDv7, or
                       ID that embeds shard id (Instagram: timestamp + shard + sequence)
Joins:                 only within a shard; denormalize or co-locate
Resharding:            moving data live without downtime (double-write/backfill/cutover)
Hot shards:            one tenant/celebrity overloads a shard → isolate to dedicated shard
Ops:                   N× backups, migrations on every shard, monitoring per shard
```

### Before you shard — try these first
```
1. Indexes + query fixes   2. Caching (Redis/CDN)   3. Read replicas
4. Vertical scaling         5. Partitioning          6. Move hot workloads to specialized stores
7. Split by service/domain (each microservice its own DB = "functional sharding")
Shard only when the WRITE workload or data size truly exceeds one machine.
Or use a DB that shards for you: Citus (Postgres), Vitess (MySQL), CockroachDB, Yugabyte,
MongoDB sharding, DynamoDB, Cassandra.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Shard key चुनो (जैसे user_id); `hash(user_id) % N` या lookup टेबल से तय होता है कि row किस सर्वर पर।
2. Router हर query को सही shard पर भेजता है; हर shard का अपना primary + replicas।
3. शुरू में ही बहुत सारे logical shards (जैसे 1024) बनाओ और कुछ सर्वरों पर बाँटो — बढ़ाना हो तो logical shards नए सर्वर पर खिसका दो।
4. एक यूज़र का सारा डेटा (orders, wallet) एक ही shard पर रखो, ताकि query और transaction एक जगह हों।
5. मुश्किलें: कई shards पर query, कई shards का transaction, global unique ID, resharding — इसलिए sharding आख़िरी उपाय है।

---

## 🟡 Real World Example

**Instagram** — sharded Postgres into thousands of **logical shards** (Postgres schemas) mapped onto fewer physical servers. IDs are 64-bit: `41 bits timestamp + 13 bits logical shard ID + 10 bits sequence`, so every ID tells you which shard it lives on and is time-sortable.

**Notion (2021)** — its Postgres `block` table hit limits, so Notion sharded into **480 logical shards across 32 physical databases**, keyed by **workspace ID** (all of a workspace's blocks together). The migration used double-writes plus backfill, then a cutover.

**Discord** — messages are sharded/partitioned by `channel_id` + time bucket in Cassandra/ScyllaDB. A huge, active channel became a hot partition, which led them to add request coalescing and "data services" in front of the DB.

**YouTube (Vitess)** — YouTube created **Vitess** to shard MySQL transparently. It's now open source and used by Slack, GitHub, HubSpot and others.

**Data localization (India)** — RBI rules require payment data to be stored in India. Global companies use geo-sharding so Indian payment data lives in Indian regions.

## 🟡 Real Example Hindi में
Instagram ने Postgres को हज़ारों logical shards में बाँटा; हर ID के अंदर ही shard नंबर होता है, तो ID देखकर पता चल जाता है कि डेटा कहाँ है।
Notion ने workspace ID से 480 logical shards बनाए, 32 सर्वरों पर। YouTube ने MySQL sharding के लिए Vitess बनाया, जो अब Slack और GitHub भी इस्तेमाल करते हैं।

---

## 🟠 My Stack Example

### App-level shard routing (Node + pg)
```js
const LOGICAL_SHARDS = 1024;
// mapping can live in config / etcd / a small DB, cached in memory
const shardMap = [
  { from: 0,   to: 511,  pool: new pg.Pool({ connectionString: process.env.DB_SHARD_A }) },
  { from: 512, to: 1023, pool: new pg.Pool({ connectionString: process.env.DB_SHARD_B }) },
];

function logicalShard(userId) {
  // stable hash (don't use JS Math.random or object hash); murmurhash/xxhash in prod
  return Number(BigInt.asUintN(32, BigInt(userId) * 2654435761n) % BigInt(LOGICAL_SHARDS));
}
export function dbForUser(userId) {
  const s = logicalShard(userId);
  return shardMap.find((m) => s >= m.from && s <= m.to).pool;
}

// All of a user's data on one shard → normal transactions work
const db = dbForUser(req.user.id);
await db.query('INSERT INTO orders(user_id, total) VALUES ($1, $2)', [req.user.id, total]);
```

### Globally unique, time-sortable IDs (Snowflake-style)
```js
// 41 bits ms since epoch | 10 bits shard | 12 bits sequence
const EPOCH = 1704067200000n; // 2024-01-01
let seq = 0n, lastMs = 0n;
export function nextId(shardId) {
  let ms = BigInt(Date.now()) - EPOCH;
  if (ms === lastMs) seq = (seq + 1n) & 4095n; else { seq = 0n; lastMs = ms; }
  return (ms << 22n) | (BigInt(shardId) << 12n) | seq;   // (handle seq overflow by waiting 1ms in prod)
}
const shardFromId = (id) => Number((BigInt(id) >> 12n) & 1023n);
```

### Citus — sharding Postgres for you
```sql
CREATE EXTENSION citus;
SELECT create_distributed_table('orders', 'user_id');      -- shard by user_id
SELECT create_distributed_table('order_items', 'user_id', colocate_with => 'orders'); -- co-located
SELECT create_reference_table('restaurants');               -- small table copied to all nodes
-- Queries with WHERE user_id = ? go to one node; others are parallelized across nodes.
```

### MongoDB sharding
```js
sh.enableSharding('foodapp');
sh.shardCollection('foodapp.orders', { userId: 'hashed' });   // hashed shard key → even spread
// mongos router sends queries with userId to one shard; others → scatter-gather
```

### Cross-shard reads: don't query all shards for analytics
```
Shards (OLTP) ──CDC/Debezium──► Kafka ──► ClickHouse / BigQuery / Elasticsearch
Admin "search all orders" & dashboards query the analytics/search store, not every shard.
```

### Resharding (moving logical shard 300 from A to new server C) — outline
```
1. Copy shard 300 data A → C (logical replication / pg_dump of schema)
2. Keep in sync (replication / double-write)
3. Briefly pause writes for shard 300 (or use per-shard lock), verify counts
4. Flip mapping: 300 → C   (config push, cache invalidation)
5. Resume; later delete from A
```

---

## ⚫ Interview Questions + Answers

**Q1: What is sharding and when should you do it?**
A1: Splitting a dataset across multiple independent database servers by a shard key, so each holds a subset and handles part of the load. Do it when write throughput, data size or the working set exceeds what one well-tuned primary can handle, after exhausting indexing, caching, read replicas, vertical scaling, partitioning and functional decomposition. Or adopt a natively distributed DB from the start if huge scale is a known requirement.

**Q2: How do you choose a shard key?**
A2: High cardinality with an even distribution of both data and traffic. It should be included in most queries so they hit one shard, and it should co-locate data that's accessed or transacted together (shard by user_id or tenant_id so a user's orders, wallet and addresses live together). Avoid monotonic keys (timestamps), low-cardinality keys (country, status) and keys with celebrity hotspots. Think about future cross-shard needs.

**Q3: What problems does sharding introduce and how do you handle them?**
A3: Cross-shard queries (handle with scatter-gather or, better, CDC into a search or analytics store), cross-shard transactions (co-location, sagas, rarely 2PC), global IDs (Snowflake, UUIDv7, IDs embedding the shard), joins (denormalize, reference tables), hot shards (isolate big tenants, split shards), resharding (logical shards plus online migration), and operational overhead (automated migrations, backups and monitoring per shard).

**Q4: Why use many logical shards instead of hash % number_of_servers?**
A4: With `hash % N`, adding a server changes N and remaps nearly every key, which forces massive data movement. With a fixed large number of logical shards (1024) mapped to physical servers, a key's logical shard never changes. Scaling just moves some logical shards to new servers and updates the mapping. Consistent hashing gives a similar benefit with less data movement when nodes change.

**Q5: Design the data layer for a multi-tenant SaaS with 50,000 businesses, a few of them huge.**
A5: Shard by tenant_id using a directory (lookup) mapping tenants to shards, so all of a tenant's data is co-located and transactions stay single-shard. Small tenants are packed many per shard. Huge tenants get dedicated shards, and the lookup can move them. Use global small tables as reference tables, a tenant-aware connection router with caching, CDC to a warehouse for cross-tenant analytics, and per-tenant rate limits to avoid noisy neighbours. Citus or a schema-per-tenant approach can simplify it.

---

## 🔷 Trade-offs
✅ Advantages:
- Scales writes, storage and compute horizontally; smaller blast radius per shard; data residency.

❌ Disadvantages:
- Big complexity: routing, cross-shard queries/txns, global IDs, resharding.
- Harder operations (migrations, backups, monitoring × N).
- Bad shard key choice is very expensive to undo.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Shard | One DB server holding part of data | डेटा का एक हिस्सा रखने वाला सर्वर |
| Shard key | Column deciding the shard | shard तय करने वाली key |
| Router | Sends queries to the right shard | सही shard पर भेजने वाला |
| Logical shard | Virtual shard mapped to physical server | आभासी shard |
| Resharding | Redistributing data across shards | डेटा दोबारा बाँटना |
| Scatter-gather | Query all shards and merge | सब shards से पूछकर जोड़ना |
| Co-location | Related data on same shard | जुड़ा डेटा एक ही shard पर |
| Hot shard | Overloaded shard | ज़्यादा भार वाला shard |
| Snowflake ID | Time + shard + sequence ID | समय + shard वाली ID |

---

## ⚡ 3-Line Summary
**English:**
1. Sharding splits data across multiple DB servers by a shard key to scale writes and storage.
2. Pick a high-cardinality, evenly distributed key that's in most queries and co-locates related data; use many logical shards.
3. It's complex (cross-shard queries/txns, IDs, resharding) — exhaust simpler options first or use Citus/Vitess/distributed DBs.

**Hindi:**
1. Sharding = डेटा को shard key से कई DB सर्वरों में बाँटना, ताकि writes और storage स्केल हों।
2. ऐसी key जो ज़्यादा अलग values वाली, बराबर बँटने वाली, और ज़्यादातर queries में हो; logical shards इस्तेमाल करो।
3. बहुत जटिल है — पहले आसान उपाय आज़माओ, या Citus/Vitess जैसे टूल लो।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — Database Sharding](https://www.youtube.com/results?search_query=database+sharding+bytebytego) | Visual sharding strategies, hotspot problem |
| 📺 YouTube | [Gaurav Sen — Sharding and Partitioning](https://www.youtube.com/results?search_query=database+sharding+partitioning+gaurav+sen) | Range vs hash sharding, re-sharding |
| 📝 Article | [MongoDB Sharding Docs](https://www.mongodb.com/docs/manual/sharding/) | Hash vs range keys, balancer, chunk migration |
| 📝 Article | [AWS DynamoDB Partitioning](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.Partitions.html) | How DynamoDB handles hot partitions internally |
| 🐙 GitHub | [system-design-primer — Sharding](https://github.com/donnemartin/system-design-primer#sharding) | Sharding patterns, pros/cons, federation |

---

## ➡️ Next Topic Suggestion
**43. Redis — Caching** — Before sharding, the most common fix for DB load is caching. Next: Redis, what it is, why it's so fast, and how to use it as a cache in Node/FastAPI.
