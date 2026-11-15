---

# Q223. How Does a B-Tree Index Work?
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Explain how a B-Tree (B+Tree) index works internally. Why is lookup O(log n), why does column order in a composite index matter, and which predicates can or cannot use it? Prove it with real plans on 100,000 rows.

---

## 💡 Quick Concept (2 lines only)
A B-Tree is a shallow, wide, balanced tree of fixed-size pages (InnoDB 16 KB, PostgreSQL 8 KB): root → branch pages → sorted leaf pages linked together, so equality, range and ORDER BY are all fast. A 100k-row index is only 2-3 levels deep, so a lookup touches ~3 pages.
हिंदी: B-Tree = चौड़ा और कम गहरा sorted tree; leaf pages sorted और linked होते हैं, इसलिए equality, range और ORDER BY तीनों तेज़ हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL 9.1 (100,000 rows, composite index)
-- ============================================

CREATE TABLE members (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  last_name  VARCHAR(30) NOT NULL,
  first_name VARCHAR(30) NOT NULL,
  city       VARCHAR(30) NOT NULL,
  joined     DATE NOT NULL
);

SET SESSION cte_max_recursion_depth = 100000;

INSERT INTO members (last_name, first_name, city, joined)
WITH RECURSIVE seq AS (SELECT 1 AS n UNION ALL SELECT n+1 FROM seq WHERE n < 100000)
SELECT CONCAT('Surname', LPAD((n*37) % 20000, 5, '0')),          -- ~20,000 distinct surnames
       CONCAT('First', n % 500),
       ELT(n % 5 + 1, 'Delhi','Pune','Mumbai','Goa','Agra'),
       DATE('2020-01-01') + INTERVAL (n % 1500) DAY
FROM seq;

CREATE INDEX idx_name ON members (last_name, first_name);        -- composite B-Tree
ANALYZE TABLE members;

-- ============================================
-- SOLUTION — what the tree can and cannot do
-- ============================================

-- 1) Equality on the leftmost column: tree descent -> OK
EXPLAIN FORMAT=TREE SELECT id FROM members WHERE last_name = 'Surname00037';
-- -> Covering index lookup on members using idx_name (last_name = 'Surname00037')  (rows=5)

-- 2) Equality on both columns -> OK (uses both parts)
EXPLAIN FORMAT=TREE SELECT id FROM members WHERE last_name = 'Surname00037' AND first_name = 'First1';
-- -> Covering index lookup ... (last_name = 'Surname00037', first_name = 'First1')

-- 3) Only the SECOND column -> leftmost-prefix rule broken, no seek possible
EXPLAIN FORMAT=TREE SELECT id FROM members WHERE first_name = 'First1';
-- -> Filter: first_name = 'First1'
--      -> Covering index scan on members using idx_name   (rows=99963)  <- reads whole index

-- 4) Prefix LIKE -> range scan on the sorted leaves -> OK
EXPLAIN FORMAT=TREE SELECT id FROM members WHERE last_name LIKE 'Surname0003%';
-- -> Covering index range scan using idx_name over ('Surname0003' <= last_name <= ...) (rows=50)

-- 5) Leading wildcard -> cannot seek (sorted order is useless) -> full index scan
EXPLAIN FORMAT=TREE SELECT id FROM members WHERE last_name LIKE '%0037';
-- -> Filter: last_name like '%0037' -> Covering index scan (rows=99963)

-- 6) ORDER BY matching the index -> no sort, stops after LIMIT
EXPLAIN FORMAT=TREE SELECT last_name, first_name FROM members ORDER BY last_name, first_name LIMIT 3;
-- -> Limit: 3 row(s) -> Covering index scan on members using idx_name  (cost=0.0027 rows=3)

-- 7) Range on first column + equality on second: range stops further index narrowing
EXPLAIN FORMAT=TREE SELECT id FROM members WHERE last_name > 'Surname19990' AND first_name = 'First1';
-- -> Filter: first_name='First1' and last_name > ...
--      -> Covering index range scan over ('Surname19990' < last_name)  (rows=45)

-- 8) Size of the tree (InnoDB persistent stats)
SELECT index_name, stat_name, stat_value
FROM mysql.innodb_index_stats
WHERE database_name = DATABASE() AND table_name = 'members' AND stat_name IN ('n_leaf_pages','size')
ORDER BY index_name, stat_name;
-- Result:
-- index_name | stat_name    | stat_value
-- -----------+--------------+-----------
-- PRIMARY    | n_leaf_pages | 348      <- the table itself (clustered index)
-- PRIMARY    | size         | 353
-- idx_name   | n_leaf_pages | 193      <- 100,000 entries fit in ~193 pages of 16 KB
-- idx_name   | size         | 225

-- ============================================
-- POSTGRESQL — look inside the tree (PGlite with the pageinspect extension)
-- ============================================
-- (same table/data created with generate_series, same CREATE INDEX idx_name)

SELECT root, level FROM bt_metap('idx_name');
-- Result: root=3, level=1          <- level 1 = ONE branch level above leaves: root page + leaves

SELECT type, count(*) FROM (
  SELECT (bt_page_stats('idx_name', g)).type
  FROM generate_series(1, (pg_relation_size('idx_name')/8192)::int - 1) g
) t GROUP BY type;
-- Result: l (leaf) = 186 pages, r (root) = 1 page
-- => a lookup reads root -> one leaf = 2 index pages (+1 heap page) for 100,000 rows.

-- PostgreSQL plans for the same predicates:
--   last_name='..' AND first_name='..'  -> Index Scan using idx_name
--   first_name = 'First1' only          -> Bitmap Index Scan on idx_name (scans whole index; PG can do this, slowly)
--   last_name LIKE 'Surname0003%'       -> Index Cond: >= 'Surname0003' AND < 'Surname0004'
--   last_name LIKE '%0037'              -> Seq Scan
--   ORDER BY last_name, first_name LIMIT 3 -> Index Only Scan using idx_name
-- NOTE: prefix LIKE with a non-C collation in PostgreSQL needs the index built with text_pattern_ops.
```

---

## 🔍 Why This Works (3 lines max)
Entries are kept sorted inside leaf pages, and each branch page holds hundreds of keys, so the tree is very wide and very shallow: height = log_fanout(n), about 2-3 for millions of rows. A composite index is sorted by column 1, then column 2, so only a leftmost prefix (plus one range) can be located by descent.
हिंदी: Index phone-book जैसा sorted है: पहले last_name, फिर first_name; सिर्फ left से शुरू होने वाले prefix पर seek हो सकता है।

---

## ⚡ Alternative Solution

```sql
-- B-Tree is not the only index type:
--   Hash index      : equality only (PostgreSQL USING hash; MySQL MEMORY engine / adaptive hash index)
--   GIN (PG)        : arrays, JSONB, full-text      GiST/SP-GiST: geometry, ranges
--   BRIN (PG)       : huge append-only tables ordered by time, tiny index
--   FULLTEXT (MySQL): word search;  pg_trgm GIN: LIKE '%x%' in PostgreSQL

-- InnoDB specifics:
--   PRIMARY KEY = clustered index (leaf pages hold the full row)
--   secondary index leaf = indexed columns + PK value (so a long PK bloats every index)
--   Lookup by secondary index then needs a second descent into the PK tree unless "covering".
-- PostgreSQL: all indexes are secondary; leaf holds a heap pointer (ctid).

-- MySQL 8.0+: descending / invisible indexes
CREATE INDEX idx_joined_desc ON members (joined DESC);
ALTER TABLE members ALTER INDEX idx_joined_desc INVISIBLE;   -- test dropping safely
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: index on (first_name, last_name) when the queries filter by last_name -> not usable for seek
-- ❌ Wrong: indexing low-cardinality columns alone (gender, boolean) -> planner prefers a table scan
-- ❌ Wrong: WHERE last_name LIKE '%0037' or WHERE LOWER(last_name)='x' expecting index use
-- ❌ Wrong: "more indexes = faster": every INSERT/UPDATE/DELETE must update each index tree
-- ✅ Correct: design composite indexes from the WHERE (equality first, then range/ORDER BY),
--    keep them few, and confirm with EXPLAIN
```

---

## 🎯 Interview Tip (1 line)
Say: "It is a balanced B+Tree with sorted, linked leaf pages, so lookups are O(log n) with ~3 page reads for millions of rows and range/ORDER BY are cheap; composite indexes follow the leftmost-prefix rule, and in InnoDB the PK is the clustered index which every secondary index carries — so I keep PKs narrow."

---

## 🔗 Related Questions
→ Q224 (adding an index to a running table) | Q229 (optimize slow query) | Q231 (PK vs UNIQUE) | Q004 (LIKE vs ILIKE)
