# 06. Revision Sheet — Databases + Caching
# हिंदी में: Databases + Caching की Revision Sheet — SQL बनाम NoSQL, indexes, EXPLAIN, normalization, transactions/ACID/isolation, locks/MVCC, pooling, pagination, replicas, partitioning, sharding, Redis और caching patterns, eviction, stampede, CDN, S3, consistent hashing, bloom filters, Elasticsearch (Topics 25–53a)

---

## 🔵 Simple Definition (English)
A **one-page refresher** for `02-Databases-Caching/` (Topics 25–53a). For each concept: what it is, the key mechanism, the interview trap and the rule of thumb. Databases and caching come up in **every** backend design: "Where do you store this? How do you scale reads and writes? What's your cache strategy and invalidation?"

## 🔵 सरल परिभाषा (Hindi)
`02-Databases-Caching/` (Topics 25–53a) की एक पन्ने वाली दोहराई — हर concept: क्या है, मुख्य तरीका, इंटरव्यू का जाल और नियम। हर backend design में पूछा जाता है: "इसे कहाँ रखोगे? reads/writes कैसे scale करोगे? cache कैसे और invalidation कैसे?"

---

## 🔴 Problem it Solves
Database and caching questions decide most designs, and interviewers love follow-ups ("What isolation level?", "How do you avoid a cache stampede?", "Offset or cursor pagination?", "What's your shard key and how do you handle hot keys?"). A compact sheet lets you **recall precise answers quickly** and avoid the classic traps.

## 🔴 यह क्यों बना? (Hindi)
DB और caching के सवाल ज़्यादातर designs तय करते हैं, और interviewer follow-ups पूछते हैं ("कौन-सा isolation level?", "cache stampede कैसे रोकोगे?", "offset या cursor?", "shard key क्या और hot keys कैसे?"); छोटी sheet से सटीक जवाब जल्दी याद आते हैं और आम जालों से बचते हो।

---

## 🟢 How it Works — Step by Step (the cheat sheet)

### Choosing storage (25–27)

```
SQL (25): tables, schemas, joins, ACID transactions, strong consistency; Postgres (rich features, JSONB,
  extensions like pgvector), MySQL (popular, simple ops). Scale: vertical → replicas → partition → shard.
NoSQL (26): key-value (Redis, DynamoDB), document (MongoDB), wide-column (Cassandra, ScyllaDB), graph (Neo4j),
  search (Elasticsearch), time-series. Flexible schema, horizontal scale, model around access patterns.
When to use (27): SQL for relational data + transactions (orders, payments, inventory). NoSQL for massive
  scale/simple access patterns (sessions, feeds, chat messages, IoT), flexible documents, or specialized
  queries (search/graph/time-series). Many systems use BOTH (polyglot persistence).
Trap: "NoSQL is faster/more scalable" without access patterns; "MongoDB has no transactions" (it does now).
```

### Indexes & query performance (28–30)

```
Index (28): B-tree (default; range queries, ordering), hash (equality), GIN (JSONB/array/full-text), GiST,
  BRIN (huge append-only tables), HNSW (vectors). Speeds reads, slows writes, costs storage.
Composite index (29): leftmost-prefix rule — INDEX(user_id, created_at) serves WHERE user_id=? ORDER BY
  created_at, not WHERE created_at alone. Put equality columns first, then range/sort. Covering index
  (INCLUDE) avoids table lookups.
EXPLAIN (30): read plan: Seq Scan vs Index Scan vs Index Only Scan, row estimates vs actual (EXPLAIN ANALYZE),
  join types (nested loop/hash/merge), sorts spilling. Fix: right index, avoid functions on indexed columns,
  SELECT only needed columns, avoid N+1, keep stats updated (ANALYZE).
```

### Modeling (31–32)

```
Normalization (31): remove redundancy (1NF/2NF/3NF) → consistency, smaller writes; more joins.
Denormalization (32): duplicate data for read speed (counters, embedded author name, precomputed feeds);
  must keep copies in sync (triggers, events, background jobs). OLTP → mostly normalized; read-heavy views
  → denormalized/materialized views.
```

### Transactions & concurrency (33–37)

```
Transactions (33): group statements atomically; BEGIN … COMMIT/ROLLBACK; keep them short.
ACID (34): Atomicity, Consistency (constraints), Isolation, Durability (WAL, fsync).
Isolation levels (35):
  Read Uncommitted (dirty reads) < Read Committed (Postgres default; no dirty reads) <
  Repeatable Read (MySQL InnoDB default; snapshot; prevents non-repeatable reads) <
  Serializable (no anomalies; may abort with serialization errors → retry)
  Anomalies: dirty read, non-repeatable read, phantom, lost update, write skew
Locks (36): row vs table locks; shared vs exclusive; SELECT … FOR UPDATE (pessimistic); optimistic locking
  via version column (UPDATE … WHERE version = ?); deadlocks → consistent lock ordering + retries.
MVCC (37): readers don't block writers — each transaction sees a snapshot via row versions (Postgres xmin/xmax,
  vacuum cleans dead tuples; MySQL undo logs). Long transactions bloat & block vacuum.
Trap: preventing double-booking/overselling → atomic conditional UPDATE, SELECT FOR UPDATE, or constraints.
```

### Connections & pagination (38–39)

```
Connection pooling (38): reuse DB connections (pgbouncer, RDS Proxy, app pools); Postgres connections are
  expensive (process per connection); size pool ≈ cores × 2–4 per DB, not "1000 connections".
Pagination (39): OFFSET/LIMIT simple but slow for deep pages & shifts with inserts; cursor/keyset
  (WHERE (created_at, id) < (?, ?) ORDER BY … LIMIT n) fast & stable for feeds; can't jump to page N.
```

### Scaling data (40–42)

```
Read replicas (40): async replication → scale reads; replication lag → stale reads; read-your-writes via
  primary for recently-written data/user; replicas for analytics/reports.
Partitioning (41): split one table within a DB (range by date, list by region, hash) → pruning, easy
  retention (drop old partitions).
Sharding (42): split data across multiple DB servers by shard key (user_id, tenant_id, hash of key).
  Choose a key that matches access patterns & distributes evenly; avoid hotspots (celebrities, big tenants);
  cross-shard queries/transactions are hard; resharding via consistent hashing/virtual shards.
Order of escalation: index/query fixes → cache → vertical → replicas → partition → shard.
```

### Redis & caching patterns (43–50)

```
Redis (43): in-memory data store; µs operations; persistence (RDB/AOF); replication & cluster; use for cache,
  sessions, rate limiting, leaderboards, queues/streams, pub/sub, distributed locks (carefully), geo.
Data structures (44): String, Hash, List, Set, Sorted Set (leaderboards, time-ordered), Bitmap, HyperLogLog
  (unique counts), Geo, Streams (consumer groups).
Cache-aside (45): app reads cache → miss → DB → populate cache; writes go to DB + delete/update cache.
  Most common. Risk: stale data window; race between update & populate (delete-after-write, short TTL).
Write-through (46): write to cache and DB synchronously → cache always fresh; slower writes.
Write-back / write-behind (47): write to cache, flush to DB asynchronously → fastest writes; risk of data loss.
TTL + invalidation (48): TTL bounds staleness; explicit invalidation on writes/events; versioned keys
  (user:42:v7); "There are only two hard things…" → keep it simple, prefer TTL + delete on write.
Eviction (49): LRU (recency), LFU (frequency), TTL-based, allkeys vs volatile policies; maxmemory set.
Stampede / thundering herd (50): hot key expires → many requests hit DB. Fixes: request coalescing/single-
  flight lock, early/probabilistic refresh, stale-while-revalidate, jittered TTLs, never-expire + background
  refresh for very hot keys.
```

### Delivery & storage (51–51a)

```
CDN (51): edge caches near users for static assets/images/video & cacheable API responses; Cache-Control,
  invalidation via versioned URLs; offloads origin & egress; also DDoS protection & TLS at edge.
Object storage / S3 (51a): durable (11 nines) blobs; presigned URLs for direct upload/download; multipart
  upload; storage classes & lifecycle rules; serve via CDN; not a filesystem/DB (no partial updates).
```

### Distribution & probabilistic structures (52–53a)

```
Consistent hashing (52): hash ring with virtual nodes → adding/removing a node moves only ~1/N keys;
  used in distributed caches, Cassandra/Dynamo-style DBs, sharded gateways.
Bloom filter (53): space-efficient set membership; false positives possible, no false negatives;
  used to skip disk/DB lookups (Cassandra SSTables), username availability, "already seen" checks.
Search engines / Elasticsearch (53a): inverted index for full-text, BM25 ranking, analyzers (stemming,
  languages), aggregations; near-real-time indexing; usually a secondary index fed from the primary DB via
  CDC/events — not the source of truth.
```

### Quick decision table

```
Money/inventory consistency → SQL + transactions (+ idempotency)
Huge write volume, simple key access (chat, events, IoT) → Cassandra/DynamoDB (partition by key + time)
Hot reads → Redis cache-aside (+ CDN for public content)
Deep feeds → cursor pagination; reports → read replica / OLAP
Full-text or typeahead → Elasticsearch/OpenSearch; files/media → S3 + CDN
```

## 🟢 कैसे काम करता है? (Hindi)
1. Storage चुनाव: SQL (joins, ACID — orders, payments, inventory), NoSQL (key-value, document, wide-column, graph, search — भारी पैमाना/सरल access); अक्सर दोनों (polyglot); पहले access patterns, फिर DB।
2. Index: B-tree default, GIN (JSONB/full-text), HNSW (vectors); composite में leftmost-prefix (equality पहले, फिर range/sort); EXPLAIN में Seq बनाम Index Scan, अनुमान बनाम असली rows; normalization = कम दोहराव, denormalization = तेज़ पढ़ना पर sync रखना पड़ता है।
3. Transactions: ACID; isolation — Read Committed (Postgres default), Repeatable Read (MySQL default), Serializable (retry चाहिए); anomalies — dirty read, phantom, lost update, write skew; locks — FOR UPDATE (pessimistic) या version column (optimistic); MVCC = पढ़ने वाले लिखने वालों को नहीं रोकते; double booking रोकने के लिए atomic conditional UPDATE।
4. Pool छोटा रखो (pgbouncer/RDS Proxy); feeds के लिए cursor pagination; scaling क्रम — index/query → cache → बड़ी machine → replicas (lag का ध्यान) → partition → shard (सही shard key, hotspots से बचो)।
5. Redis (µs, कई data structures); cache-aside सबसे आम, write-through (हमेशा ताज़ा), write-back (तेज़ पर नुक़सान का ख़तरा); TTL + लिखने पर delete; LRU/LFU; stampede के लिए single-flight, jitter, stale-while-revalidate; CDN, S3 (presigned, multipart), consistent hashing (~1/N keys हिलते हैं), bloom filter (false positive, false negative नहीं), Elasticsearch (secondary index, source of truth नहीं)।

---

## 🟡 Real World Example
- **Instagram** scaled on sharded Postgres with logical shards mapped to physical servers. **Discord** moved messages from MongoDB to Cassandra, then to ScyllaDB.
- **Facebook memcache** (cache-aside at massive scale, with leases to prevent thundering herds) is the classic caching paper.
- **Flipkart/Swiggy** use Redis heavily for sessions, rate limits and hot catalog data during sale peaks.

## 🟡 Real Example Hindi में
- Instagram ने sharded Postgres (logical shards → physical servers) से scale किया; Discord ने messages MongoDB से Cassandra और फिर ScyllaDB पर ले गया।
- Facebook का memcache (बड़े पैमाने पर cache-aside, stampede रोकने के लिए leases) caching का क्लासिक paper है।
- Flipkart/Swiggy sale के समय sessions, rate limits और hot catalog के लिए Redis भारी तौर पर इस्तेमाल करते हैं।

---

## 🟠 My Stack Example

### Snippets to recall instantly
```sql
-- Composite index for "user's latest orders"
CREATE INDEX idx_orders_user_created ON orders (user_id, created_at DESC) INCLUDE (status, total_paise);
-- Keyset pagination
SELECT * FROM orders WHERE user_id = $1 AND (created_at, id) < ($2, $3) ORDER BY created_at DESC, id DESC LIMIT 20;
-- Prevent oversell atomically
UPDATE inventory SET qty = qty - 1 WHERE sku = $1 AND qty > 0 RETURNING qty;
-- Optimistic locking
UPDATE carts SET items = $2, version = version + 1 WHERE id = $1 AND version = $3;
```
```js
// Cache-aside with jittered TTL + single-flight (Node + Redis)
async function getMenu(id) {
  const key = `menu:${id}`; const hit = await redis.get(key); if (hit) return JSON.parse(hit);
  if (!(await redis.set(`${key}:lock`, 1, 'NX', 'EX', 5))) { await sleep(50); return getMenu(id); }
  const menu = await db.menu(id);
  await redis.set(key, JSON.stringify(menu), 'EX', 60 + Math.floor(Math.random() * 15));
  await redis.del(`${key}:lock`); return menu;
}
```

---

## ⚫ Interview Questions + Answers (rapid fire)

**Q1: How do you scale a relational database?**
A1: First optimize queries and indexes (EXPLAIN) and add connection pooling. Then add caching (Redis or CDN) for hot reads, scale vertically, add read replicas for read-heavy traffic (handling replication lag with read-your-writes on the primary), partition large tables by time or key for pruning and retention, and finally shard across servers by a key matching access patterns (user_id or tenant_id), with consistent hashing or a directory for rebalancing. Move analytics to an OLAP store.

**Q2: Explain isolation levels and anomalies.**
A2: Read Uncommitted allows dirty reads. Read Committed prevents dirty reads but allows non-repeatable reads and phantoms. Repeatable Read gives a stable snapshot within a transaction (preventing non-repeatable reads, and in Postgres also phantoms), though write skew may still occur. Serializable makes concurrent transactions behave as if serial, preventing all anomalies, at the cost of aborts that the application must retry. Choose based on correctness needs: payments and inventory often use explicit row locks or conditional updates even at Read Committed.

**Q3: Cache-aside vs write-through vs write-back?**
A3: Cache-aside: the application reads through the cache and on a miss loads from the DB, writing to the DB and invalidating the cache on updates. It's simple, resilient and the most common, with a brief staleness window. Write-through: writes go synchronously to cache and DB, so the cache stays fresh at the cost of higher write latency and caching data that may never be read. Write-back: writes go to the cache and are flushed asynchronously, giving the fastest writes but risking loss on cache failure, so it suits counters and metrics rather than money.

**Q4: How do you prevent a cache stampede?**
A4: Use request coalescing (a single-flight lock, so only one request recomputes a missing key while others wait or get stale data), add jitter to TTLs so hot keys don't expire together, refresh hot keys early or probabilistically before expiry, serve stale-while-revalidate, and for extremely hot keys keep them non-expiring with background refresh. Also protect the DB with rate limits and circuit breakers.

**Q5: How do you choose a shard key?**
A5: Pick a key aligned with the dominant access pattern, so most queries hit a single shard (user_id for user-centric apps, tenant_id for SaaS), with high cardinality and even distribution to avoid hotspots. Plan for skew (celebrities, large tenants) with sub-sharding or dedicated shards. Avoid keys that force frequent cross-shard joins or transactions, and use consistent hashing or many logical shards mapped to physical nodes for easier rebalancing.

---

## 🔷 Trade-offs
✅ Indexes speed reads — ❌ slow writes; replicas scale reads — ❌ lag; sharding scales writes — ❌ complexity; caches speed reads — ❌ staleness & invalidation.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ACID | Transaction guarantees | transaction की गारंटी |
| Isolation level | Concurrency visibility rules | एक साथ चलते काम के नियम |
| MVCC | Versioned rows for snapshots | versions वाली rows |
| Composite index | Multi-column index | कई columns का index |
| Keyset pagination | Cursor-based paging | cursor वाला paging |
| Replication lag | Replica behind primary | replica पीछे |
| Shard key | Data distribution key | बाँटने की key |
| Cache-aside | App-managed caching | ऐप वाला cache |
| Stampede | Mass cache-miss load | एक साथ भारी miss |
| Bloom filter | Probabilistic membership | संभावना वाला set |

---

## ⚡ 3-Line Summary
**English:**
1. Choose SQL for relations + transactions, NoSQL for scale/simple patterns; design indexes (leftmost prefix) and read EXPLAIN plans.
2. Know ACID, isolation anomalies, locks vs optimistic versions, MVCC, pooling, cursor pagination, and the scaling ladder (cache → replicas → partition → shard).
3. Caching: cache-aside default, TTL + invalidation, LRU/LFU, stampede protection; plus CDN, S3, consistent hashing, bloom filters, Elasticsearch as secondary index.

**Hindi:**
1. Relations + transactions → SQL, पैमाना → NoSQL; indexes और EXPLAIN समझो।
2. ACID, isolation, locks/optimistic, MVCC, pooling, cursor pagination, scaling सीढ़ी।
3. Caching: cache-aside, TTL + invalidation, LRU/LFU, stampede बचाव; CDN, S3, consistent hashing, bloom filter, Elasticsearch।

---

## ➡️ Next Topic Suggestion
**07. Revision Sheet — Auth, Security + Distributed Systems** — Next: a fast refresher of JWT/OAuth/OIDC, rate limiting, idempotency, CAP and consistency, sagas, resilience patterns, messaging, coordination and microservice infrastructure (Topics 54–99, plus observability).
