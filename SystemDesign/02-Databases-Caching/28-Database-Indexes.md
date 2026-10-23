# 28. Database Indexes
# हिंदी में: Index — किताब की "विषय-सूची" की तरह, जिससे DB पूरी टेबल पढ़े बिना सीधे सही row तक पहुँच जाता है

---

## 🔵 Simple Definition (English)
An **index** is a separate data structure (usually a **B-tree**) that stores column values in **sorted order** with pointers to the matching rows. It lets the database find rows **without scanning the whole table**, turning a query from seconds into milliseconds. The cost: extra storage and slower writes.

## 🔵 सरल परिभाषा (Hindi)
Index एक अलग, sorted सूची है जिसमें column की value और उसकी row का पता होता है — जैसे किताब के पीछे का index।
इससे DB करोड़ों rows पढ़े बिना सीधे सही row ढूँढ लेता है। नुक़सान: थोड़ी ज़्यादा जगह और writes थोड़े धीमे।

---

## 🔴 Problem it Solves
Without an index, `SELECT * FROM orders WHERE user_id = 42` on 50 million rows means a **full table scan**: read every row and check it. That's seconds of disk I/O and CPU per query, which multiplies with traffic until the DB falls over.

With a B-tree index on `user_id`: about 3–4 page reads → **~1 ms**.

Indexes are the **#1 fix for slow queries** in real life and the most common DB question in interviews.

## 🔴 यह क्यों बना? (Hindi)
Index के बिना DB को 5 करोड़ rows में से हर row पढ़कर देखना पड़ता है (full table scan) — हर query में सेकंड लगते हैं।
Index से सिर्फ़ 3-4 पन्ने पढ़कर ~1 ms में जवाब। असल ज़िंदगी में धीमी query का सबसे बड़ा इलाज यही है।

---

## 🟢 How it Works — Step by Step

### B-tree (B+tree) index

```
                         [ 500 | 1000 ]                    ← root (in RAM)
                  ┌──────────┼──────────────┐
          [100|250|400]   [600|800]     [1200|1500]        ← internal pages
           ┌──┬──┼──┐       ...            ...
   [..|42|..|99] ...                                        ← leaf pages: sorted keys
        │                                                      + pointer (row location / TID)
        ▼                                                      leaves linked → range scans
  heap row: (id=9001, user_id=42, total=450, ...)

Find user_id = 42:  root → internal → leaf → row     ≈ 3–4 page reads, O(log n)
Range user_id BETWEEN 40 AND 50: find 40, then walk linked leaves → fast
50M rows → tree height ~4. 5B rows → ~5. Grows very slowly.
```

### Full scan vs index scan

```
WITHOUT index (Seq Scan)               WITH index (Index Scan)
┌──────────────────────────┐           root → branch → leaf → 3 rows
│ row 1   check ✗          │
│ row 2   check ✗          │           ~4 page reads
│ ...  50,000,000 rows ... │           ~1 ms
│ row N   check ✓          │
└──────────────────────────┘
~seconds, heavy I/O
```

### What indexes help with

```
✅ WHERE col = ?                 (equality)
✅ WHERE col > ? / BETWEEN       (ranges — B-tree)
✅ ORDER BY col LIMIT n          (already sorted → no sort step)
✅ JOIN ON a.col = b.col         (foreign keys! Postgres does NOT auto-index FKs)
✅ UNIQUE constraints            (enforced via unique index)
✅ MIN/MAX
❌ WHERE lower(email) = ?        (function on column → need expression index)
❌ WHERE name LIKE '%kumar'      (leading wildcard → need trigram/full-text index)
❌ low-selectivity columns alone (WHERE is_active = true when 95% are true → scan is cheaper)
```

### Index types (Postgres)

```
┌────────────┬────────────────────────────────────────┬───────────────────────────────┐
│ Type       │ Good for                               │ Example                       │
├────────────┼────────────────────────────────────────┼───────────────────────────────┤
│ B-tree     │ =, <, >, ranges, ORDER BY (default)    │ user_id, created_at, email    │
│ Hash       │ equality only                          │ rarely needed                 │
│ GIN        │ "contains": JSONB, arrays, full-text   │ attrs @> '{"ram":"8GB"}'      │
│ GiST       │ geo, ranges, nearest-neighbour         │ PostGIS locations             │
│ BRIN       │ huge append-only tables, natural order │ logs by timestamp (tiny index)│
│ HNSW/IVF   │ vector similarity (pgvector)           │ embeddings for RAG            │
└────────────┴────────────────────────────────────────┴───────────────────────────────┘
Special forms:
  Unique index        → CREATE UNIQUE INDEX ON users(email)
  Partial index       → CREATE INDEX ON orders(created_at) WHERE status = 'PENDING'   (small!)
  Expression index    → CREATE INDEX ON users(lower(email))
  Covering index      → CREATE INDEX ON orders(user_id) INCLUDE (total, status) → index-only scan
  Composite index     → (user_id, created_at)   ← next topic
```

### Clustered vs non-clustered

```
Clustered (MySQL InnoDB primary key): table rows are PHYSICALLY stored in PK order inside
  the B-tree. Only one per table. Secondary indexes store the PK, then look up the row.
  → Use short, increasing PKs (BIGINT auto-increment / UUIDv7), not random UUIDv4
    (random inserts cause page splits).
Non-clustered (Postgres default): index separate from heap; points to row location (TID).
```

### The cost of indexes

```
Every INSERT/UPDATE/DELETE must also update EVERY index on the table.
  1 table + 8 indexes → 1 write becomes ~9 writes
More disk + RAM (indexes compete for cache)
Too many indexes → slow writes, bloated memory
Unused indexes → pure cost. Find them:  SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;
```

## 🟢 कैसे काम करता है? (Hindi)
1. Index एक B-tree है — values sorted रहती हैं, ऊपर से नीचे 3-4 कदम में सही value मिल जाती है।
2. हर value के साथ row का पता होता है, तो DB सीधे वहीं जाता है।
3. `=`, range, ORDER BY, JOIN — सब में index मदद करता है; पर `LIKE '%abc'` या column पर function में नहीं।
4. JSON/array/search के लिए GIN, लोकेशन के लिए GiST, बड़े log tables के लिए BRIN।
5. हर index से writes धीमे और जगह ज़्यादा — इसलिए सिर्फ़ ज़रूरी index बनाओ, बेकार हटाओ।

---

## 🟡 Real World Example

**A classic startup incident** — the "My Orders" screen in an app gets slow as the orders table grows to 20M rows. `EXPLAIN` shows `Seq Scan on orders`. Adding `CREATE INDEX CONCURRENTLY ON orders(user_id, created_at DESC)` drops latency from 3 s to 2 ms and DB CPU from 90% to 15%. This exact story happens at almost every company.

**GitLab** — has published many incidents and performance fixes where a missing or wrong index on huge Postgres tables caused slow pages, and dropping unused indexes improved write performance.

**Stack Overflow** — tunes indexes very carefully. Its huge throughput on few servers comes from queries that are almost all index seeks, with covering indexes to avoid table lookups.

## 🟡 Real Example Hindi में
लगभग हर स्टार्टअप में यह होता है: orders टेबल 2 करोड़ rows की हुई, "My Orders" स्क्रीन 3 सेकंड लेने लगी। `EXPLAIN` में Seq Scan दिखा — `(user_id, created_at)` पर index बनाया और समय 2 ms हो गया, DB का CPU 90% से 15%।

---

## 🟠 My Stack Example

### Create indexes safely in production (Postgres)
```sql
-- CONCURRENTLY: doesn't lock the table for writes (takes longer, can't run in a transaction)
CREATE INDEX CONCURRENTLY idx_orders_user_created ON orders (user_id, created_at DESC);

-- Foreign keys need manual indexes in Postgres
CREATE INDEX CONCURRENTLY idx_order_items_order ON order_items (order_id);

-- Case-insensitive email lookup
CREATE UNIQUE INDEX idx_users_email_lower ON users (lower(email));
SELECT * FROM users WHERE lower(email) = lower($1);

-- Partial index: only pending orders (tiny, fast for the worker that polls them)
CREATE INDEX idx_orders_pending ON orders (created_at) WHERE status = 'PENDING';

-- JSONB attributes
CREATE INDEX idx_products_attrs ON products USING GIN (attrs jsonb_path_ops);

-- Search names with LIKE '%term%'
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_rest_name_trgm ON restaurants USING GIN (name gin_trgm_ops);
```

### Check that the index is used
```sql
EXPLAIN ANALYZE
SELECT id, total FROM orders WHERE user_id = 42 ORDER BY created_at DESC LIMIT 20;
-- Good:  Index Scan using idx_orders_user_created ... (actual time=0.03..0.05 rows=20)
-- Bad:   Seq Scan on orders ... Rows Removed by Filter: 19999980
```

### Prisma / TypeORM / SQLAlchemy
```prisma
model Order {
  id        BigInt   @id @default(autoincrement())
  userId    BigInt
  status    String
  createdAt DateTime @default(now())
  @@index([userId, createdAt(sort: Desc)])
  @@index([status], map: "idx_orders_status")
}
```
```python
class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (Index("idx_orders_user_created", "user_id", text("created_at DESC")),)
```

### MongoDB indexes
```js
db.orders.createIndex({ userId: 1, createdAt: -1 });
db.users.createIndex({ email: 1 }, { unique: true });
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 });   // TTL index
db.orders.find({ userId: 42 }).sort({ createdAt: -1 }).explain('executionStats'); // IXSCAN vs COLLSCAN
```

### Find missing & unused indexes
```sql
-- tables with many sequential scans (candidate for index)
SELECT relname, seq_scan, idx_scan, n_live_tup FROM pg_stat_user_tables ORDER BY seq_scan DESC LIMIT 10;

-- unused indexes (consider dropping)
SELECT indexrelname, idx_scan, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes WHERE idx_scan = 0 ORDER BY pg_relation_size(indexrelid) DESC;
```

### ORM trap
```js
// Looks innocent, but if no index on (status, city) this scans the table on every request
await prisma.restaurant.findMany({ where: { status: 'OPEN', city: 'Mumbai' }, orderBy: { rating: 'desc' }, take: 20 });
// → add @@index([city, status, rating(sort: Desc)])
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a database index and how does it work?**
A1: An auxiliary data structure, typically a B+tree, that keeps a column's values sorted with pointers to the rows. A lookup walks from root to leaf in O(log n) page reads instead of scanning the whole table, and the linked leaves allow efficient range scans and ordered reads. The database's query planner decides when to use it based on statistics and selectivity.

**Q2: Why not index every column?**
A2: Every index must be updated on each insert, update and delete, so writes slow down. Indexes consume disk and memory, crowding out useful cached data. Many indexes go unused, or the planner prefers a sequential scan for low-selectivity columns. Index based on real query patterns (WHERE, JOIN, ORDER BY), monitor usage, and drop unused ones.

**Q3: When will the database NOT use an index even if one exists?**
A3: When the query wraps the column in a function or cast (`lower(email)`, `date(created_at)`), uses a leading wildcard (`LIKE '%x'`), has a type mismatch, or uses OR conditions across different columns. Also when the predicate matches a large fraction of rows (a scan is cheaper), when statistics are stale (run ANALYZE), and with composite indexes when the query doesn't use the leftmost column. Solutions: expression indexes, trigram/full-text indexes, rewriting queries, updating stats.

**Q4: What is a covering index / index-only scan?**
A4: An index that contains all the columns a query needs, either as key columns or via `INCLUDE`, so the DB answers from the index alone without visiting the table heap. Example: `CREATE INDEX ON orders(user_id) INCLUDE (status, total)` for `SELECT status, total FROM orders WHERE user_id=?`. Fewer I/Os, faster. In Postgres it also depends on the visibility map being up to date (VACUUM).

**Q5: How do you add an index to a 500 GB production table without downtime?**
A5: In Postgres, use `CREATE INDEX CONCURRENTLY`, which builds without blocking writes. It takes longer and must run outside a transaction, and if it fails, drop the INVALID index and retry. In MySQL, use online DDL (`ALGORITHM=INPLACE, LOCK=NONE`) or tools like gh-ost/pt-online-schema-change. Run during low traffic, watch replication lag and disk space, and test on a staging copy first.

---

## 🔷 Trade-offs
✅ Advantages:
- Massive read speedups (O(log n) vs O(n)), faster sorts, joins, uniqueness enforcement.

❌ Disadvantages:
- Slower writes, extra storage and memory.
- Need maintenance (bloat, reindexing) and monitoring.
- Wrong/unused indexes give cost without benefit.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Index | Sorted structure for fast lookup | तेज़ खोज के लिए sorted सूची |
| B-tree | Balanced tree used by most indexes | संतुलित पेड़ ढाँचा |
| Full table scan / Seq Scan | Reading every row | पूरी टेबल पढ़ना |
| Selectivity | Fraction of rows matched | कितनी rows मेल खाती हैं |
| Covering index | Index has all needed columns | index में ही सारा डेटा |
| Partial index | Index on subset of rows | कुछ rows का index |
| Expression index | Index on a function of column | function वाला index |
| Clustered index | Table stored in index order | index के क्रम में टेबल |
| CONCURRENTLY | Build index without blocking writes | बिना lock के index बनाना |

---

## ⚡ 3-Line Summary
**English:**
1. An index (B-tree) keeps values sorted with row pointers → O(log n) lookups instead of full scans.
2. Index columns used in WHERE, JOIN, ORDER BY; use GIN/GiST/BRIN/partial/expression indexes for special cases.
3. Every index slows writes — verify with EXPLAIN ANALYZE, build CONCURRENTLY, drop unused ones.

**Hindi:**
1. Index (B-tree) से DB सीधे सही row तक पहुँचता है — पूरी टेबल नहीं पढ़नी पड़ती।
2. WHERE, JOIN, ORDER BY वाले columns पर index; ख़ास ज़रूरत के लिए GIN, GiST, partial index।
3. हर index writes धीमा करता है — EXPLAIN से जाँचो, CONCURRENTLY से बनाओ, बेकार index हटाओ।

---

## ➡️ Next Topic Suggestion
**29. Composite Indexes** — Real queries filter on multiple columns (`user_id AND status ORDER BY created_at`). Next: multi-column indexes, the leftmost-prefix rule, and how column order changes everything.
