---

# Q097. Find Unused Indexes
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
A write-heavy `users` table has 5 indexes. How do you find which are never used (so they can be dropped) in MySQL and in PostgreSQL? What traps exist before you actually drop anything?

---

## 💡 Quick Concept (2 lines only)
Both engines count index usage since the last stats reset/restart: MySQL via `sys.schema_unused_indexes` (performance_schema), PostgreSQL via `pg_stat_user_indexes.idx_scan = 0`. Unused indexes still cost every INSERT/UPDATE/DELETE and disk.
हिंदी: Usage counters से बिना-काम के index मिलते हैं; उन्हें drop करने से writes तेज़ होते हैं, पर पहले पूरा business cycle देखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL (verified on MySQL 9.1.0)
-- ============================================

CREATE TABLE users (
  id         INT PRIMARY KEY AUTO_INCREMENT,
  email      VARCHAR(100) NOT NULL,
  country    CHAR(2) NOT NULL,
  created_at DATETIME NOT NULL,
  UNIQUE KEY uq_email (email),
  KEY idx_country (country),
  KEY idx_created (created_at),
  KEY idx_country_created (country, created_at)
);
INSERT INTO users (email, country, created_at) VALUES
  ('a@x.com','IN','2024-01-01'), ('b@x.com','US','2024-01-02'), ('c@x.com','IN','2024-01-03');

-- some workload
SELECT * FROM users WHERE email = 'a@x.com';
SELECT * FROM users WHERE country = 'IN' AND created_at > '2024-01-01';

-- ============================================
-- SOLUTION — MySQL
-- ============================================

-- Step 1: raw usage counters per index
SELECT index_name, count_read
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'd97' AND object_name = 'users' ORDER BY index_name;   -- use your schema name

-- Step 2: ready-made view (excludes PRIMARY and UNIQUE indexes)
SELECT * FROM sys.schema_unused_indexes WHERE object_schema = 'd97';

-- Step 3: also find redundant (prefix-duplicate) indexes
SELECT table_name, redundant_index_name, dominant_index_name, sql_drop_index
FROM sys.schema_redundant_indexes WHERE table_schema = 'd97';

-- ============================================
-- EXPECTED OUTPUT (real, MySQL 9.1.0)
-- ============================================
-- Step 1:
-- index_name          | count_read
-- idx_country         | 2          <- optimizer chose it for the 2nd query (tiny table)
-- idx_country_created | 0
-- idx_created         | 0
-- PRIMARY             | 0
-- uq_email            | 1
-- Step 2:
-- d97 | users | idx_created
-- d97 | users | idx_country_created
-- Step 3:
-- redundant: idx_country   dominant: idx_country_created
-- sql_drop_index: ALTER TABLE `d97`.`users` DROP INDEX `idx_country`
-- NOTE: the "unused" list and the "redundant" list disagree - proof you must judge, not just trust a view.
```

```sql
-- ============================================
-- POSTGRESQL (verified on PGlite = PostgreSQL 18.6)
-- ============================================
CREATE TABLE users (id SERIAL PRIMARY KEY, email TEXT NOT NULL UNIQUE, country CHAR(2) NOT NULL, created_at TIMESTAMP NOT NULL);
CREATE INDEX idx_country ON users(country);
CREATE INDEX idx_created ON users(created_at);
CREATE INDEX idx_country_created ON users(country, created_at);
INSERT INTO users (email,country,created_at)
SELECT 'u'||i||'@x.com', (ARRAY['IN','US','UK','DE','SG'])[i%5+1], TIMESTAMP '2024-01-01'+i*INTERVAL '1 minute'
FROM generate_series(1,20000) i;
ANALYZE users;
SELECT * FROM users WHERE email = 'u5@x.com';
SELECT * FROM users WHERE country='IN' AND created_at > '2024-01-10';
SELECT * FROM users WHERE country='IN' AND created_at > '2024-01-10';

-- unused, non-unique, non-PK indexes, biggest first
SELECT s.indexrelname, s.idx_scan, pg_size_pretty(pg_relation_size(s.indexrelid)) AS size
FROM pg_stat_user_indexes s JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.relname = 'users' AND s.idx_scan = 0 AND NOT i.indisunique AND NOT i.indisprimary
ORDER BY pg_relation_size(s.indexrelid) DESC;

-- Output (after stats flush):
-- idx_created | 0 | 456 kB
-- idx_country | 0 | 176 kB
-- (idx_country_created idx_scan = 2, users_email_key idx_scan = 1)
```

---

## 🔍 Why This Works (3 lines max)
Every index lookup increments a per-index counter; idx_scan/count_read of zero over a long window means no query needs it. Excluding unique/PK indexes matters because they enforce constraints even if never read.
हिंदी: Counter शून्य यानी index पढ़ा ही नहीं गया; पर UNIQUE/PK constraints के लिए होते हैं, उन्हें कभी मत हटाओ।

---

## ⚡ Alternative Solution

```sql
-- MySQL 8.0+: don't drop immediately - make it INVISIBLE first, watch for a week, then drop (see Q094)
ALTER TABLE users ALTER INDEX idx_created INVISIBLE;
-- rollback is instant:  ALTER TABLE users ALTER INDEX idx_created VISIBLE;

-- PostgreSQL: dangerous-free test = drop in a transaction on a replica / use hypopg; or
SELECT pg_stat_reset_single_table_counters('users'::regclass);  -- restart counting for one table
-- PGlite note: stats are flushed lazily; call SELECT pg_stat_force_next_flush(); before reading pg_stat_*.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Dropping every idx_scan = 0 index right after a restart / stats reset (counters are since reset!)
-- ❌ Missing that monthly/quarterly reports, failover replicas, and cron jobs use the index
--    (PostgreSQL stats are per server: check EVERY replica that serves reads)
-- ❌ Dropping an index that backs a FOREIGN KEY (MySQL needs one) or a UNIQUE constraint
-- ✅ Observe >= 1 full business cycle, make INVISIBLE first (MySQL), then DROP INDEX CONCURRENTLY (PostgreSQL)
```

---

## 🎯 Interview Tip (1 line)
Say: "I check usage counters across a full business cycle and on all replicas, exclude constraint-backed indexes, test removal with INVISIBLE indexes in MySQL, and drop with CONCURRENTLY in Postgres - the win is lower write amplification and less buffer-pool pressure."

---

## 🔗 Related Questions
→ Q094 (Invisible index) | Q093 (Index bloat) | Q083 (Composite index order) | Q112 (pg_stat_statements)
