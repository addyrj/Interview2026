---

# Q098. Index Cardinality — Low vs High Cardinality Impact
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
What is index cardinality? Is an index on `is_active` (2 values) or `country` (5 values) useful compared to one on `email` (unique)? Show how to measure it and what the optimizer does in MySQL and PostgreSQL.

---

## 💡 Quick Concept (2 lines only)
Cardinality = number of distinct values in the indexed column(s); selectivity = distinct / total rows. High selectivity (email) lets an index jump to a few rows; low selectivity (boolean) returns a large share of the table, so a scan is often cheaper - unless the query targets the rare value.
हिंदी: Cardinality = कितनी अलग values; ज़्यादा unique values वाला index कम rows लौटाता है और तेज़ होता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL (verified on MySQL 9.1.0)
-- ============================================

CREATE TABLE users (
  id        INT PRIMARY KEY AUTO_INCREMENT,
  email     VARCHAR(100) NOT NULL,
  is_active TINYINT NOT NULL,          -- 99% = 1, 1% = 0
  country   CHAR(2) NOT NULL,          -- 5 values
  KEY idx_active  (is_active),
  KEY idx_country (country),
  UNIQUE KEY uq_email (email)
);
SET SESSION cte_max_recursion_depth = 50000;
INSERT INTO users (email, is_active, country)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 50000)
SELECT CONCAT('user', i, '@mail.com'), IF(i % 100 = 0, 0, 1),
       ELT(i % 5 + 1, 'IN','US','UK','DE','SG')
FROM n;
ANALYZE TABLE users;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: what MySQL believes (estimated cardinality per index)
SELECT index_name, column_name, cardinality
FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name = 'users';

-- Step 2: exact distinct counts and selectivity
SELECT COUNT(*) total, COUNT(DISTINCT is_active) d_active, COUNT(DISTINCT country) d_country,
       COUNT(DISTINCT email) d_email FROM users;

-- Step 3: plans for each predicate
EXPLAIN SELECT * FROM users WHERE is_active = 1;           -- 99% of table
EXPLAIN SELECT * FROM users WHERE is_active = 0;           -- 1% of table
EXPLAIN SELECT * FROM users WHERE country = 'IN';          -- 20%
EXPLAIN SELECT * FROM users WHERE email = 'user777@mail.com';

-- Step 4: does the index actually help the 99% case? Compare real run time
EXPLAIN ANALYZE SELECT * FROM users WHERE is_active = 1;
EXPLAIN ANALYZE SELECT * FROM users IGNORE INDEX (idx_active) WHERE is_active = 1;

-- ============================================
-- EXPECTED OUTPUT (real, MySQL 9.1.0; cardinality is a sampled estimate)
-- ============================================
-- Step 1:  idx_active=2 | idx_country=4 | PRIMARY=50190 | uq_email=49212   (true values 2/5/50000/50000)
-- Step 2:  total=50000 | d_active=2 | d_country=5 | d_email=50000
-- Step 3:
--   is_active=1 -> type=ref key=idx_active rows=25095 (estimate = table/2; truth is 49500)
--   is_active=0 -> type=ref key=idx_active rows=500
--   country='IN'-> type=ref key=idx_country rows=10000, Extra: Using index condition
--   email=...   -> type=const key=uq_email rows=1
-- Step 4 (milliseconds vary by machine):
--   with idx_active : Index lookup ... actual time=0.199..30   rows=49500
--   IGNORE INDEX    : Table scan    ... actual time=0.0469..11.3 rows=49500   <- scan WON
```

```sql
-- ============================================
-- POSTGRESQL (verified on PGlite = PostgreSQL 18.6)
-- ============================================
CREATE TABLE users (id SERIAL PRIMARY KEY, email TEXT NOT NULL UNIQUE, is_active BOOLEAN NOT NULL, country CHAR(2) NOT NULL);
INSERT INTO users (email,is_active,country)
SELECT 'user'||i||'@mail.com', (i%100<>0), (ARRAY['IN','US','UK','DE','SG'])[i%5+1] FROM generate_series(1,50000) i;
CREATE INDEX idx_active ON users(is_active);
CREATE INDEX idx_country ON users(country);
ANALYZE users;

SELECT attname, n_distinct, most_common_vals, most_common_freqs FROM pg_stats
WHERE tablename='users' AND attname IN ('is_active','country','email');
-- email     | -1 (= unique)  | NULL
-- is_active | 2              | {t,f} | 0.98983335,0.0101666665      <- PG knows the skew (MCV list)
-- country   | 5              | {UK,SG,IN,US,DE} | ~0.20 each

EXPLAIN SELECT * FROM users WHERE is_active;        -- Seq Scan (rows=49492)   <- common value: scan
EXPLAIN SELECT * FROM users WHERE NOT is_active;    -- Index Scan using idx_active (rows=508) <- rare value: index
EXPLAIN SELECT * FROM users WHERE country='IN';     -- Bitmap Heap Scan via idx_country (rows=9983)

-- Partial index = the right tool for the rare value (see Q090)
CREATE INDEX idx_inactive_only ON users(id) WHERE NOT is_active;
EXPLAIN SELECT id FROM users WHERE NOT is_active;   -- Index Only Scan using idx_inactive_only
```

---

## 🔍 Why This Works (3 lines max)
An index lookup costs random I/O per matching row; once a predicate matches more than a few percent of rows, sequential scanning wins. PostgreSQL's histogram/MCV statistics make that choice per value; MySQL (without histograms) only knows average rows-per-key, so it happily uses a poor index for the 99% value.
हिंदी: ज़्यादातर rows match हों तो index बेकार है; PostgreSQL value-wise skew जानता है, MySQL औसत पर चलता है।

---

## ⚡ Alternative Solution

```sql
-- MySQL 8.0+: histograms tell the optimizer about skew WITHOUT an index
ANALYZE TABLE users UPDATE HISTOGRAM ON is_active, country WITH 16 BUCKETS;   -- not run in this verification
-- Low-cardinality column? Put it AFTER a selective column in a composite index:
ALTER TABLE users ADD KEY idx_country_active (country, is_active);   -- useful combined, poor alone
-- PostgreSQL: multi-column stats for correlated columns
CREATE STATISTICS st_country_active (dependencies) ON country, is_active FROM users;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ "Every column in WHERE needs its own index" -> index on a boolean/status flag, never used, still taxes writes
CREATE INDEX idx_active ON users (is_active);     -- 2 distinct values
-- ❌ Putting the low-cardinality column FIRST in a composite for no reason
-- ✅ Index low-cardinality columns only (a) combined with selective ones, (b) as a PostgreSQL partial index
--    for the rare value, (c) when the query always filters the rare value.
-- ❌ Trusting SHOW INDEX cardinality blindly: it is sampled (50190 vs true 50000) -> ANALYZE TABLE to refresh
```

---

## 🎯 Interview Tip (1 line)
Say: "Cardinality is about selectivity per query, not the column alone - a boolean index is fine for the 1% value (partial index in Postgres) and useless for the 99% value; I verify with EXPLAIN ANALYZE and keep stats fresh."

---

## 🔗 Related Questions
→ Q085 (Index on NULL values) | Q088 (When MySQL doesn't use an index) | Q090 (Partial index PgSQL) | Q114 (Statistics / ANALYZE)
