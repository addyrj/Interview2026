---

# Q100. Prefix Index — MySQL Solution for Long VARCHAR
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: MySQL (PostgreSQL alternatives shown)

---

## ❓ Question
`page_visits.url` is a long `VARCHAR(500)`. A full index is huge (and VARCHAR(5000) won't index at all). How do you index only the first N characters in MySQL, how do you choose N, and what are the limits? What does PostgreSQL do instead?

---

## 💡 Quick Concept (2 lines only)
`KEY (url(60))` stores only the first 60 characters in the B-tree; pick the smallest N where `COUNT(DISTINCT LEFT(col,N)) / COUNT(*)` is close to the full-column selectivity. Prefix indexes cannot be covering and cannot satisfy ORDER BY/GROUP BY on the column.
हिंदी: Prefix index सिर्फ पहले N characters store करता है; N वहाँ चुनो जहाँ selectivity लगभग full column जितनी हो जाए।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL (verified on MySQL 9.1.0)
-- ============================================

CREATE TABLE page_visits (
  id         BIGINT PRIMARY KEY AUTO_INCREMENT,
  url        VARCHAR(500) NOT NULL,
  visited_at DATETIME NOT NULL
) ENGINE=InnoDB;

SET SESSION cte_max_recursion_depth = 30000;
INSERT INTO page_visits (url, visited_at)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 30000)
SELECT CONCAT('https://www.example-store.com/catalog/',
              ELT(i % 6 + 1, 'shoes','shirts','bags','watches','hats','belts'), '/item-', i),
       NOW() - INTERVAL i MINUTE
FROM n;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: measure selectivity for candidate prefix lengths (1.0 = unique)
SELECT COUNT(DISTINCT url)/COUNT(*)          AS full_sel,
       COUNT(DISTINCT LEFT(url,20))/COUNT(*) AS p20,
       COUNT(DISTINCT LEFT(url,50))/COUNT(*) AS p50,
       COUNT(DISTINCT LEFT(url,58))/COUNT(*) AS p58,
       COUNT(DISTINCT LEFT(url,60))/COUNT(*) AS p60
FROM page_visits;

-- Step 2: a too-short prefix (50) is a trap: URLs share a long common start
ALTER TABLE page_visits ADD KEY idx_url_prefix (url(50));
ANALYZE TABLE page_visits;
SELECT index_name, sub_part, cardinality FROM information_schema.statistics
WHERE table_schema = DATABASE() AND table_name = 'page_visits';

-- Step 3: rebuild with a prefix that is selective
ALTER TABLE page_visits DROP KEY idx_url_prefix, ADD KEY idx_url_prefix (url(60));
ANALYZE TABLE page_visits;

-- Step 4: what it can and cannot do
EXPLAIN SELECT * FROM page_visits WHERE url = 'https://www.example-store.com/catalog/bags/item-8';
EXPLAIN SELECT id, url FROM page_visits WHERE url LIKE 'https://www.example-store.com/catalog/bags/item-99%';
EXPLAIN SELECT url FROM page_visits ORDER BY url LIMIT 5;

-- ============================================
-- EXPECTED OUTPUT (real, MySQL 9.1.0)
-- ============================================
-- Step 1: full_sel=1.0000 | p20=0.0000 | p50=0.0068 | p58=1.0000 | p60=1.0000
-- Step 2: idx_url_prefix sub_part=50 cardinality=238   (of 30,000 rows: terrible - ~126 rows per key)
--         after Step 3: sub_part=60 cardinality=29283   (= PRIMARY's, i.e. effectively unique)
-- Step 4a (=)    : type=ref,   key=idx_url_prefix, key_len=242, rows=1,  Extra: Using where
-- Step 4b (LIKE) : type=range, key=idx_url_prefix, key_len=242, rows=19, Extra: Using where
-- Step 4c (ORDER BY url): type=ALL, key=NULL, rows=29283, Extra: Using filesort   <- prefix can't sort
-- Limit check: CREATE TABLE t (u VARCHAR(5000), KEY k (u));
--   ERROR 1071: Specified key was too long; max key length is 3072 bytes
```

```sql
-- ============================================
-- POSTGRESQL (verified on PGlite = PostgreSQL 18.6): no prefix syntax; use expression or hash/hash-of-value
-- ============================================
CREATE TABLE page_visits (id BIGSERIAL PRIMARY KEY, url TEXT NOT NULL, visited_at TIMESTAMP NOT NULL);
-- (insert like above using generate_series)
CREATE INDEX idx_url_hash ON page_visits USING hash (url);               -- stores 4-byte hash, equality only
CREATE INDEX idx_url_md5  ON page_visits (md5(url));                     -- btree on fixed 32 chars
CREATE INDEX idx_url_left ON page_visits (left(url, 60) text_pattern_ops);  -- true prefix, query must use left(url,60)
-- Sizes at 30,000 rows:  hash 2064 kB | md5 1752 kB | left-60 2320 kB
-- WHERE url = '...'  -> Index Scan using idx_url_hash
-- WHERE left(url,60) LIKE '...item-99%' -> Index Scan using idx_url_left
-- PostgreSQL btree row limit is ~2704 bytes (about 1/3 page) - longer values fail to index.
```

---

## 🔍 Why This Works (3 lines max)
The index entry holds just the prefix, so more entries fit per page (smaller, cache-friendly), and MySQL re-checks the full value in the row (Extra: Using where). It only works if the prefix discriminates; 50 chars here collapsed 30,000 URLs into ~238 distinct keys.
हिंदी: Prefix छोटा हो तो index छोटा होता है, पर बहुत छोटा prefix ज़्यादातर rows को एक जैसा बना देता है और index बेकार हो जाता है।

---

## ⚡ Alternative Solution

```sql
-- MySQL: index a fixed-size hash of the long value (exact-match lookups only)
ALTER TABLE page_visits
  ADD COLUMN url_hash CHAR(32) AS (MD5(url)) STORED,
  ADD KEY idx_url_hash (url_hash);
SELECT * FROM page_visits
WHERE url_hash = MD5('https://www.example-store.com/catalog/bags/item-8')
  AND url      = 'https://www.example-store.com/catalog/bags/item-8';   -- 2nd predicate guards collisions
-- Not run in MySQL here (pattern is standard). In PostgreSQL the md5(url) index was created, but the planner chose the hash index.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Guessing the length
ALTER TABLE page_visits ADD KEY idx_url_prefix (url(50));   -- measured selectivity 0.0068 -> near useless
-- ✅ Measure first: SELECT COUNT(DISTINCT LEFT(url,N))/COUNT(*) ... and pick the smallest N near full_sel
-- ❌ Expecting a covering index / sorted output from a prefix index
SELECT url FROM page_visits ORDER BY url LIMIT 5;          -- verified: ALL + filesort
-- ❌ Prefix on a column whose differences are at the END (URLs, file paths) - consider reversing or hashing
```

---

## 🎯 Interview Tip (1 line)
Say: "I choose the prefix length from measured selectivity, accept that it can't be covering or provide ordering, and for URL-like data with long shared prefixes I prefer a hash/generated column; in Postgres I'd use a hash or expression index."

---

## 🔗 Related Questions
→ Q084 (Covering index) | Q089 (Functional index) | Q092 (Hash vs B-tree) | Q099 (LIKE '%pattern')
