# 41. Database Partitioning
# हिंदी में: Partitioning — एक बहुत बड़ी टेबल को छोटे-छोटे हिस्सों (partitions) में बाँटना, जो एक ही database के अंदर रहते हैं

---

## 🔵 Simple Definition (English)
**Partitioning** splits one large logical table into smaller physical pieces (**partitions**) based on a **partition key**, e.g. by month of `created_at`. To the application it still looks like **one table**; the database routes rows and queries to the right partitions.
- **Horizontal partitioning:** split **rows** (by range, list or hash). Usually what "partitioning" means.
- **Vertical partitioning:** split **columns** into separate tables (hot vs cold / large columns).
Partitioning usually happens **inside one database server**. Spreading partitions across servers is **sharding** (next topic).

## 🔵 सरल परिभाषा (Hindi)
Partitioning में एक बड़ी टेबल (जैसे 100 करोड़ orders) को महीने या किसी key के हिसाब से छोटे हिस्सों में बाँटते हैं — पर ऐप को अब भी एक ही टेबल दिखती है।
Query सिर्फ़ ज़रूरी हिस्सों को पढ़ती है, और पुराना डेटा पूरा partition हटाकर एक झटके में साफ़ हो जाता है।

---

## 🔴 Problem it Solves
Huge tables (billions of rows, terabytes) cause:
- **Slow queries** even with indexes (huge indexes don't fit in RAM).
- **Painful maintenance:** VACUUM, index rebuilds and backups on a 2 TB table take hours.
- **Expensive deletes:** `DELETE FROM events WHERE created_at < now() - 90 days` deletes 500M rows → hours of IO, bloat, replication lag.
- **Hot and cold data mixed:** 95% of queries touch the last 30 days, but the DB keeps a 5-year table.

Partitioning gives **partition pruning** (scan only relevant partitions), **instant drops of old data**, smaller indexes per partition, and parallel maintenance.

## 🔴 यह क्यों बना? (Hindi)
अरबों rows वाली टेबल पर index भी RAM में नहीं समाता, VACUUM और backup घंटों लेते हैं, और पुराना डेटा DELETE करने में घंटों का IO और lag होता है।
Partitioning से query सिर्फ़ ज़रूरी partition पढ़ती है (pruning), पुराना डेटा `DROP PARTITION` से तुरंत हटता है, और हर हिस्से का index छोटा रहता है।

---

## 🟢 How it Works — Step by Step

### Range partitioning (most common — by time)

```
orders  (logical table — app queries this)
  ├── orders_2024_08   created_at in [2024-08-01, 2024-09-01)
  ├── orders_2024_09   created_at in [2024-09-01, 2024-10-01)
  ├── orders_2024_10   created_at in [2024-10-01, 2024-11-01)   ← all new inserts
  └── orders_default   (anything else)

SELECT * FROM orders WHERE created_at >= '2024-10-15'
  → PARTITION PRUNING: only orders_2024_10 scanned ✅

Retention: DROP TABLE orders_2024_01;   ← instant, no bloat (vs deleting 50M rows)
```

### List partitioning (by category)

```
orders PARTITION BY LIST (region)
  ├── orders_north  (region IN ('DL','PB','HR'))
  ├── orders_south  (region IN ('KA','TN','KL'))
  └── orders_west   (region IN ('MH','GJ'))
```

### Hash partitioning (even spread)

```
events PARTITION BY HASH (user_id)  — 16 partitions
  user_id hash % 16 → partition 0..15
  ✅ even distribution, smaller indexes, parallel scans
  ❌ no pruning for range queries on time
```

### Vertical partitioning

```
users (id, name, email, phone, status)               ← small, hot, frequently read
user_profiles (user_id, bio TEXT, preferences JSONB, avatar_blob ...)   ← large, rarely read
✅ hot table stays small → more rows per page, better cache hits
```

### Choosing a partition key

```
✓ Appears in WHERE of most queries (so pruning works)      e.g. created_at, tenant_id
✓ Matches data lifecycle (retention by time)               e.g. month
✓ Spreads data reasonably evenly                            avoid 1 giant + 99 tiny partitions
✗ Too many partitions (10,000+) → planning overhead
Rule of thumb: partition when a table is > ~100 GB or retention/deletion is painful.
```

### Limitations (Postgres declarative partitioning)
```
- Primary key / unique constraints MUST include the partition key
    (PRIMARY KEY (id, created_at))
- Queries WITHOUT the partition key scan ALL partitions
- Must create future partitions ahead of time (pg_partman automates this)
- Foreign keys referencing partitioned tables are supported (PG 12+), but add care
```

### Partitioning vs Sharding

```
┌─────────────────────┬─────────────────────────────┬───────────────────────────────┐
│                     │ Partitioning                │ Sharding                      │
├─────────────────────┼─────────────────────────────┼───────────────────────────────┤
│ Where               │ One DB server               │ Many DB servers               │
│ Transparent to app? │ Yes (one logical table)     │ Usually no (routing needed)   │
│ Scales              │ Manageability, query speed  │ Writes, storage, CPU          │
│ Transactions        │ Normal ACID                 │ Cross-shard is hard           │
│ Complexity          │ Low–medium                  │ High                          │
└─────────────────────┴─────────────────────────────┴───────────────────────────────┘
Do partitioning first; shard only when one server can't handle it.
```

## 🟢 कैसे काम करता है? (Hindi)
1. टेबल को partition key से बाँटते हो — समय (महीना) से range, क्षेत्र से list, या user_id के hash से।
2. ऐप उसी `orders` टेबल पर query करता है; DB ख़ुद सही partition में row डालता और पढ़ता है।
3. Query में partition key हो तो DB बाक़ी partitions छोड़ देता है (pruning) — तेज़।
4. पुराना डेटा: `DROP TABLE orders_2024_01` — तुरंत, बिना bloat।
5. Partitioning एक ही सर्वर पर होता है; कई सर्वरों में बाँटना sharding है।

---

## 🟡 Real World Example

**Time-series and event data (analytics, logs, IoT)** — companies storing app events (CleverTap, MoEngage, Mixpanel-style workloads) partition by day or month, keep 90 days hot, and drop or archive older partitions. TimescaleDB automates this with "hypertables" (automatic time partitions, called chunks).

**Payment/transaction tables** — fintechs (Razorpay, Paytm-scale systems) partition transaction tables by month. Reconciliation and settlement queries target recent partitions, and old partitions move to cheaper storage or archives for regulatory retention.

**Notion** — before sharding, Notion's huge `block` table in Postgres had grown so large that vacuum and maintenance became critical issues. That pushed them to partition and later shard it into 480 logical shards.

## 🟡 Real Example Hindi में
Analytics और event वाली कंपनियाँ (CleverTap, MoEngage जैसी) डेटा को दिन/महीने के partition में रखती हैं — 90 दिन का डेटा तेज़ storage पर, पुराना हटा या archive कर देती हैं।
Fintech कंपनियाँ transactions को महीने के हिसाब से partition करती हैं; settlement की queries सिर्फ़ हाल के partitions पढ़ती हैं।

---

## 🟠 My Stack Example

### Postgres declarative range partitioning
```sql
CREATE TABLE orders (
  id          BIGINT GENERATED ALWAYS AS IDENTITY,
  user_id     BIGINT NOT NULL,
  total       NUMERIC(10,2) NOT NULL,
  status      TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (id, created_at)                 -- must include partition key
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2024_10 PARTITION OF orders FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');
CREATE TABLE orders_2024_11 PARTITION OF orders FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');
CREATE TABLE orders_default PARTITION OF orders DEFAULT;

-- index on parent → created on every partition automatically
CREATE INDEX ON orders (user_id, created_at DESC);

-- verify pruning
EXPLAIN SELECT * FROM orders WHERE created_at >= '2024-11-05' AND user_id = 42;
-- → only "orders_2024_11" appears in the plan

-- retention: detach then drop (detach CONCURRENTLY avoids blocking, PG 14+)
ALTER TABLE orders DETACH PARTITION orders_2023_10 CONCURRENTLY;
DROP TABLE orders_2023_10;      -- or archive to S3 first (pg_dump / COPY TO)
```

### Automate future partitions with pg_partman (or a cron job)
```sql
CREATE EXTENSION pg_partman;
SELECT partman.create_parent('public.orders', 'created_at', 'native', 'monthly', p_premake := 3);
-- run partman.run_maintenance() daily (pg_cron) → creates next months, drops old per retention
```

### Simple Node cron alternative
```js
// runs daily: ensure next month's partition exists
const next = startOfMonth(addMonths(new Date(), 1));
const name = `orders_${format(next, 'yyyy_MM')}`;
await pool.query(`CREATE TABLE IF NOT EXISTS ${name} PARTITION OF orders
  FOR VALUES FROM ('${format(next, 'yyyy-MM-dd')}') TO ('${format(addMonths(next, 1), 'yyyy-MM-dd')}')`);
```

### Always include the partition key in queries
```js
// ❌ scans all partitions
await pool.query('SELECT * FROM orders WHERE id = $1', [id]);
// ✅ prune: the order id + its date (encode date in id, or pass created_at from client/URL)
await pool.query('SELECT * FROM orders WHERE id = $1 AND created_at = $2', [id, createdAt]);
```
Tip: time-sortable IDs (ULID / UUIDv7 / Snowflake) let you derive the time and partition from the ID itself.

### MongoDB equivalents
```js
// TTL index = automatic deletion of old docs (simpler than partitions, but deletes cost IO)
db.events.createIndex({ createdAt: 1 }, { expireAfterSeconds: 90 * 86400 });
// Time-series collections (MongoDB 5+): built-in bucketing by time
db.createCollection('metrics', { timeseries: { timeField: 'ts', metaField: 'deviceId', granularity: 'minutes' } });
```

### TimescaleDB (Postgres extension for metrics/IoT)
```sql
SELECT create_hypertable('device_metrics', 'ts', chunk_time_interval => interval '1 day');
SELECT add_retention_policy('device_metrics', interval '90 days');
```

---

## ⚫ Interview Questions + Answers

**Q1: What is database partitioning and why use it?**
A1: Splitting a large table into smaller physical partitions by a key, while it stays one logical table. Benefits: partition pruning (queries scan only relevant partitions), smaller per-partition indexes that fit in memory, faster maintenance (vacuum, reindex, backups per partition), and cheap data lifecycle management (drop or detach old partitions instantly instead of mass DELETEs). It's done within one database server.

**Q2: What are range, list and hash partitioning? When to use each?**
A2: Range: by value ranges, usually time (monthly), for time-series, logs, orders and retention policies. List: by discrete values (region, tenant tier, status), when queries naturally target categories. Hash: by hash of a key, for even distribution when there's no natural range and the goal is spreading data and IO evenly (but no range pruning). Subpartitioning can combine them, e.g. range by month, then hash by user.

**Q3: What's the difference between partitioning and sharding?**
A3: Partitioning divides a table within a single database instance. It's transparent to the app, keeps normal ACID transactions, and improves manageability and query performance, but doesn't add CPU or IO capacity beyond one server. Sharding distributes data across multiple database servers, scaling writes and storage horizontally, but requires routing, makes cross-shard queries and transactions hard, and is much more complex. Partition first, shard when one server isn't enough.

**Q4: What are pitfalls of partitioning in PostgreSQL?**
A4: Queries without the partition key hit all partitions. Unique and primary keys must include the partition key, so global uniqueness of `id` alone needs another approach. Too many partitions increase planning time. Future partitions must be pre-created (pg_partman). Rows landing in a default partition can block creating new ranges. Moving rows between partitions on key updates is costly. And a bad partition key makes partitions uneven.

**Q5: How would you design storage for 2 billion events per month with 90-day retention?**
A5: Range-partition by day or week on event time (or use TimescaleDB hypertables or ClickHouse for analytics), with indexes local to each partition on the common filters (user_id, event_type). Insert in batches. Use automated partition creation and retention that drops partitions older than 90 days (archive to S3/Parquet first if needed). Run heavy analytics on a columnar store fed via CDC. If write volume exceeds one node, shard by user_id or tenant across nodes (Citus, or Cassandra/ClickHouse clusters).

---

## 🔷 Trade-offs
✅ Advantages:
- Faster queries via pruning; smaller indexes; easy retention (drop partitions); parallel maintenance.
- Transparent to application (mostly).

❌ Disadvantages:
- Queries without the key get slower (scan all partitions).
- Constraints must include partition key; partition management overhead.
- Doesn't add server capacity — still one machine.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Partitioning | Splitting a table into parts in one DB | एक DB में टेबल के हिस्से |
| Partition key | Column deciding partition | हिस्सा तय करने वाला column |
| Range partition | By value ranges (dates) | सीमा (तारीख़) के हिसाब से |
| List partition | By discrete values | तय values के हिसाब से |
| Hash partition | By hash of key | hash के हिसाब से बराबर बँटवारा |
| Partition pruning | Skip irrelevant partitions | बेकार हिस्से छोड़ देना |
| Vertical partitioning | Split columns into tables | columns को अलग करना |
| Retention | How long data is kept | डेटा कितने समय रखना है |
| Detach / Drop partition | Remove a partition | हिस्सा हटाना |

---

## ⚡ 3-Line Summary
**English:**
1. Partitioning splits a huge table into smaller partitions (range/list/hash) inside one DB; it still looks like one table.
2. Benefits: partition pruning, smaller indexes, easy retention by dropping partitions.
3. Choose a key used in most queries (often time); it doesn't add server capacity — that's sharding.

**Hindi:**
1. Partitioning = एक DB में बड़ी टेबल के छोटे हिस्से (range/list/hash); ऐप को एक ही टेबल दिखती है।
2. फ़ायदे: pruning, छोटे index, पुराना डेटा partition drop से तुरंत साफ़।
3. ऐसी key चुनो जो ज़्यादातर queries में हो (अक्सर समय); सर्वर की क्षमता नहीं बढ़ती — वो sharding है।

---

## ➡️ Next Topic Suggestion
**42. Database Sharding** — When one server can't handle the writes or storage, you split data across many servers. Next: shard keys, routing, resharding, cross-shard queries, and how Instagram, Notion and Discord shard.
