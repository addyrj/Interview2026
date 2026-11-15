---

# Q092. Hash Index - When Better Than B-Tree?
# Category: Indexes
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (PostgreSQL hash | MySQL MEMORY engine / adaptive hash)

---

## ❓ Question
When is a hash index better than a B-Tree? What are its limits, is it crash-safe in PostgreSQL, and does MySQL InnoDB let you create one?

---

## 💡 Quick Concept (2 lines only)
A hash index maps hash(value) to row locations: O(1) equality lookups and a small size for long keys, but NO range scans, ORDER BY, prefix LIKE or multi-column partial use. Use it for pure `=` lookups on large keys (URLs, tokens); otherwise B-Tree.
हिंदी: Hash index सिर्फ = के लिए तेज़ है और लंबे keys पर छोटा रहता है; range, ORDER BY, LIKE के लिए B-Tree चाहिए।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) - PostgreSQL
-- ============================================

CREATE TABLE page_visits (
  visit_id   BIGINT PRIMARY KEY,
  url        TEXT NOT NULL,                 -- long values (~150 chars)
  visited_at TIMESTAMP NOT NULL
);

INSERT INTO page_visits
SELECT n,
       'https://shop.example.com/products/category/' || (n % 300) || '/item/' || n
         || '?utm_source=newsletter&utm_campaign=spring_sale_2024&ref=' || md5(n::text),
       TIMESTAMP '2024-01-01' + n * INTERVAL '1 second'
FROM generate_series(1, 50000) n;

-- ============================================
-- SOLUTION - PostgreSQL
-- ============================================

CREATE INDEX idx_url_btree ON page_visits USING btree (url);
CREATE INDEX idx_url_hash  ON page_visits USING hash  (url);     -- WAL-logged and crash-safe since PG 10
ANALYZE page_visits;

-- Size comparison
SELECT indexname, pg_size_pretty(pg_relation_size(indexname::regclass)) AS size
FROM pg_indexes WHERE tablename = 'page_visits' ORDER BY indexname;

-- Drop the B-Tree to see what the hash index can and cannot do
DROP INDEX idx_url_btree;
EXPLAIN SELECT * FROM page_visits WHERE url = (SELECT url FROM page_visits WHERE visit_id = 777);   -- equality
EXPLAIN SELECT * FROM page_visits WHERE url LIKE 'https://shop.example.com/products/category/7/%';  -- prefix
EXPLAIN SELECT * FROM page_visits WHERE url > 'https://shop.example.com/products/category/299';     -- range
EXPLAIN SELECT * FROM page_visits ORDER BY url LIMIT 5;                                             -- sort

-- ============================================
-- EXPECTED OUTPUT (verified on PostgreSQL 18 via PGlite; sizes approximate)
-- ============================================

-- indexname        | size
-- idx_url_btree    | 9376 kB       <- stores the full key (~150 bytes) in every entry
-- idx_url_hash     | 2064 kB       <- stores only a 4-byte hash code (+ tid): ~4.5x smaller
-- page_visits_pkey | 1112 kB
--
-- equality: Index Scan using idx_url_hash on page_visits  (Index Cond: (url = (InitPlan 1).col1))
-- prefix LIKE: Seq Scan on page_visits  (Filter: url ~~ '.../7/%')
-- range:       Seq Scan on page_visits  (Filter: url > '...')
-- ORDER BY:    Sort -> Seq Scan  (hash indexes keep no order)
```

---

## 🔍 Why This Works (3 lines max)
A hash index stores a fixed-size hash code per key, so size does not grow with key length and an equality probe goes straight to a bucket; the hash destroys ordering, so range/sort/prefix cannot use it. The hash may collide, so rows are rechecked against the real value.
हिंदी: Hash index में key की जगह fixed-size hash रहता है, इसलिए लंबे keys पर छोटा; पर ordering नहीं बचती, तो range और sort नहीं चलते।

---

## ⚡ Alternative Solution

```sql
-- MySQL: InnoDB does NOT support user-created hash indexes.
-- Verified on 9.1: INDEX idx_k_hash (k) USING HASH on an InnoDB table is accepted but SHOW INDEX reports BTREE.
CREATE TABLE a (id INT PRIMARY KEY, k VARCHAR(50), INDEX idx_k_hash (k) USING HASH) ENGINE=InnoDB;   -- silently BTREE

-- Real hash indexes exist only in the MEMORY engine (data lost on restart, table-level locks) - useful for caches:
CREATE TABLE sessions_mem (
  session_id CHAR(32) NOT NULL,
  user_id    INT,
  UNIQUE KEY uq_sid (session_id) USING HASH,
  INDEX idx_user (user_id) USING BTREE
) ENGINE=MEMORY;
-- Verified: WHERE session_id = MD5('b') -> type=const, key=uq_sid (HASH);
--           WHERE session_id > MD5('a') -> type=ALL (hash can't do ranges)

-- InnoDB's Adaptive Hash Index is an internal, automatic hash over hot B-Tree pages. It cannot be created by you
-- and is OFF by default on MySQL 9.1 here (@@innodb_adaptive_hash_index = 0); can cause contention on busy servers.

-- Portable pattern for long-key equality lookups in BOTH databases: B-Tree over a hash column
--   MySQL:  url_hash BINARY(16) AS (UNHEX(MD5(url))) STORED, INDEX (url_hash)  + WHERE url_hash = UNHEX(MD5(?)) AND url = ?
--   PgSQL:  CREATE INDEX ON page_visits (md5(url));  + WHERE md5(url) = md5(?) AND url = ?    (not run here)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming USING HASH in MySQL InnoDB gives hash performance - it quietly creates a B-Tree.
-- ❌ Wrong: hash index for columns queried with <, >, BETWEEN, LIKE 'abc%' or ORDER BY (shown above: Seq Scan)
-- ❌ Wrong: hash UNIQUE constraints in PostgreSQL: CREATE UNIQUE INDEX ... USING hash is NOT supported
--    (uniqueness needs a B-Tree; use EXCLUDE USING hash (col WITH =) as a workaround).
-- ❌ Wrong: relying on PostgreSQL hash indexes before version 10 - they were not WAL-logged (not crash-safe, not replicated).
-- ✅ Default to B-Tree; choose hash only after measuring size/latency for pure equality on long keys.
```

---

## 🎯 Interview Tip (1 line)
Say: "B-Tree is the default because it handles equality, ranges, sorting and prefixes; PostgreSQL hash (crash-safe since 10) wins only for pure equality on long keys where it is several times smaller, and in MySQL InnoDB you can't create hash indexes at all, only MEMORY tables and the internal adaptive hash index."

---

## 🔗 Related Questions
→ Q081 (B-Tree index internals) | Q088 (When MySQL does NOT use an index) | Q091 (Full-text index) | Q093 (Index bloat)
