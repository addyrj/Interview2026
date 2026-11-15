---

# Q099. LIKE '%pattern' — Why No Index?
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
`WHERE email LIKE 'user777%'` is fast but `WHERE email LIKE '%777@yahoo.com'` scans the whole table. Why, and what are the fixes in MySQL and PostgreSQL?

---

## 💡 Quick Concept (2 lines only)
A B-tree is sorted left to right, so a known prefix gives a contiguous range to seek; a leading wildcard has no starting point, so every entry must be checked. Fixes: index the reversed string (suffix search), full-text, or PostgreSQL trigram GIN/GiST.
हिंदी: B-tree शुरुआत से sorted होता है, इसलिए '%' शुरू में हो तो seek की जगह पूरा scan होता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL (verified on MySQL 9.1.0)
-- ============================================

CREATE TABLE customers (
  id        INT PRIMARY KEY AUTO_INCREMENT,
  email     VARCHAR(100) NOT NULL,
  full_name VARCHAR(60)  NOT NULL,
  KEY idx_email (email)
);
SET SESSION cte_max_recursion_depth = 50000;
INSERT INTO customers (email, full_name)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 50000)
SELECT CONCAT('user', i, '@', ELT(i % 4 + 1, 'gmail.com','yahoo.com','outlook.com','corp.io')),
       CONCAT('Name ', i)
FROM n;
ANALYZE TABLE customers;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: prefix search -> index range scan
EXPLAIN SELECT * FROM customers WHERE email LIKE 'user777%';

-- Step 2: suffix search -> full scan
EXPLAIN SELECT * FROM customers WHERE email LIKE '%777@yahoo.com';
EXPLAIN ANALYZE SELECT * FROM customers WHERE email LIKE '%777@yahoo.com';

-- Step 3: fix = stored generated column holding REVERSE(email) + index, then search by reversed prefix
ALTER TABLE customers
  ADD COLUMN email_rev VARCHAR(100) AS (REVERSE(email)) STORED,
  ADD KEY idx_email_rev (email_rev);
ANALYZE TABLE customers;
EXPLAIN SELECT * FROM customers WHERE email_rev LIKE CONCAT(REVERSE('777@yahoo.com'), '%');

-- Step 4: wrapping the column in REVERSE() directly does NOT use the plain index
EXPLAIN SELECT * FROM customers WHERE REVERSE(email) LIKE 'moc.oohay@777%';

-- ============================================
-- EXPECTED OUTPUT (real, MySQL 9.1.0)
-- ============================================
-- Step 1: type=range, key=idx_email, rows=11, Extra: Using index condition
-- Step 2: type=ALL,   key=NULL,      rows=50230, filtered=11.11, Extra: Using where
--         EXPLAIN ANALYZE: Table scan on customers ... rows=50000 -> Filter -> rows=50 (~33 ms)
-- Step 3: type=range, key=idx_email_rev, rows=50, Extra: Using index condition   (50 matching rows)
-- Step 4: type=ALL, key=NULL, rows=50044    <- function on column = no index
```

```sql
-- ============================================
-- POSTGRESQL (verified on PGlite = PostgreSQL 18.6, pg_trgm loaded)
-- ============================================
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE TABLE customers (id SERIAL PRIMARY KEY, email TEXT NOT NULL, full_name TEXT NOT NULL);
INSERT INTO customers (email, full_name)
SELECT 'user'||i||'@'||(ARRAY['gmail.com','yahoo.com','outlook.com','corp.io'])[i%4+1], 'Name '||i
FROM generate_series(1,50000) i;
CREATE INDEX idx_email ON customers(email);
ANALYZE customers;

EXPLAIN SELECT * FROM customers WHERE email LIKE 'user777%';
-- Index Scan using idx_email (worked on PGlite, whose default collation is binary/C - not independently confirmed;
--   with a non-C collation (en_US.UTF-8) a plain btree CANNOT serve LIKE -> create text_pattern_ops index)
CREATE INDEX idx_email_pattern ON customers(email text_pattern_ops);
EXPLAIN SELECT * FROM customers WHERE email LIKE '%777@yahoo.com';
-- Seq Scan on customers  Filter: (email ~~ '%777@yahoo.com')

-- Fix A: expression index on reverse()
CREATE INDEX idx_email_rev ON customers (reverse(email) text_pattern_ops);
EXPLAIN SELECT * FROM customers WHERE reverse(email) LIKE reverse('777@yahoo.com') || '%';
-- Index Scan using idx_email_rev   -> returns 50 rows

-- Fix B (best, handles %anything% and ILIKE): trigram GIN
CREATE INDEX idx_email_trgm ON customers USING gin (email gin_trgm_ops);
EXPLAIN SELECT * FROM customers WHERE email ILIKE '%ser77%';
-- Bitmap Heap Scan -> Bitmap Index Scan on idx_email_trgm
```

---

## 🔍 Why This Works (3 lines max)
Reversing turns "ends with X" into "starts with reverse(X)", which is a prefix range again; trigrams index every 3-character chunk so any substring becomes an index lookup plus recheck. Both trade extra index size and write cost for read speed.
हिंदी: Suffix को reverse करके prefix बना दो, या PostgreSQL में trigram index लगाओ; दोनों में extra storage लगता है।

---

## ⚡ Alternative Solution

```sql
-- MySQL full-text (word-based, not arbitrary substring): verified, returns 12500 'gmail' rows
ALTER TABLE customers ADD FULLTEXT KEY ft_email (email);
SELECT COUNT(*) FROM customers WHERE MATCH(email) AGAINST('gmail' IN BOOLEAN MODE);
EXPLAIN SELECT id FROM customers WHERE MATCH(email) AGAINST('gmail' IN BOOLEAN MODE);
-- type=fulltext, key=ft_email, Extra: Using where; Ft_hints: no_ranking
-- Beyond one box: Elasticsearch/OpenSearch or PostgreSQL tsvector for real text search.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Leading wildcard on a big table in an OLTP path
SELECT * FROM customers WHERE email LIKE '%yahoo.com';        -- full scan every request
-- ❌ "Fixing" it with a function on the column
SELECT * FROM customers WHERE REVERSE(email) LIKE 'moc.oohay%';  -- verified: type=ALL
-- ✅ Match the index expression exactly (generated column / expression index), or use trigram/full-text.
-- Note: a covering index (SELECT id, email only) can make MySQL do a full INDEX scan - still O(n), only cheaper.
```

---

## 🎯 Interview Tip (1 line)
Say: "B-trees need a left-anchored prefix; for contains/suffix search I use pg_trgm GIN in Postgres, a reversed generated column or FULLTEXT in MySQL, and for real search workloads a dedicated search engine."

---

## 🔗 Related Questions
→ Q004 (LIKE vs ILIKE) | Q089 (Functional index) | Q091 (Full-text index) | Q119 (Function on indexed column)
