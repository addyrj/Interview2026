---

# Q105. Index Merge — What Is It
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ "index_merge" | PostgreSQL "BitmapAnd/BitmapOr")

---

## ❓ Question
EXPLAIN shows `type=index_merge` with `Using union(...)` or `Using intersect(...)`. What does it mean, when does the optimizer choose it, and is it a sign of a missing composite index?

---

## 💡 Quick Concept (2 lines only)
Index merge scans two or more indexes on the same table and combines the row-id sets: union for `OR`, intersect for `AND`. PostgreSQL does the same with bitmap scans (BitmapOr / BitmapAnd). It is a useful fallback, but a composite index (for AND) or UNION of two queries (for OR) is usually faster.
हिंदी: Index merge में कई single indexes के row-ids को जोड़ा (OR) या मिलाया (AND) जाता है; AND के लिए composite index आमतौर पर बेहतर है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL (verified on MySQL 9.1.0)
-- ============================================

CREATE TABLE tickets (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  assignee_id INT NOT NULL,
  reporter_id INT NOT NULL,
  priority    TINYINT NOT NULL,
  title       VARCHAR(80) NOT NULL,
  KEY idx_assignee (assignee_id),
  KEY idx_reporter (reporter_id),
  KEY idx_priority (priority)
);
SET SESSION cte_max_recursion_depth = 100000;
INSERT INTO tickets (assignee_id, reporter_id, priority, title)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 100000)
SELECT (i*7) % 1000 + 1, (i*13) % 1500 + 1, i % 5, CONCAT('Ticket ', i) FROM n;
ANALYZE TABLE tickets;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: OR across two indexed columns -> index_merge union
EXPLAIN SELECT * FROM tickets WHERE assignee_id = 7 OR reporter_id = 9;

-- Step 2: AND of two selective predicates -> index_merge intersection
EXPLAIN SELECT * FROM tickets WHERE assignee_id = 7 AND reporter_id = 91;

-- Step 3: what if the optimizer could not merge? (turn it off for this session to compare)
SET SESSION optimizer_switch = 'index_merge=off';
EXPLAIN ANALYZE SELECT * FROM tickets WHERE assignee_id = 7 OR reporter_id = 9;
SET SESSION optimizer_switch = 'index_merge=on';
EXPLAIN ANALYZE SELECT * FROM tickets WHERE assignee_id = 7 OR reporter_id = 9;

-- Step 4: better plans - composite index for AND, UNION for OR
ALTER TABLE tickets ADD KEY idx_a_r (assignee_id, reporter_id);
ANALYZE TABLE tickets;
EXPLAIN SELECT * FROM tickets WHERE assignee_id = 7 AND reporter_id = 91;
EXPLAIN SELECT * FROM tickets WHERE assignee_id = 7 UNION SELECT * FROM tickets WHERE reporter_id = 9;

-- ============================================
-- EXPECTED OUTPUT (real, MySQL 9.1.0)
-- ============================================
-- Step 1: type=index_merge, key=idx_assignee,idx_reporter, rows=167,
--         Extra: Using union(idx_assignee,idx_reporter); Using where
-- Step 2: type=index_merge, key=idx_reporter,idx_assignee, rows=1,
--         Extra: Using intersect(idx_reporter,idx_assignee); Using where
-- Step 3 (merge off): type=ALL, rows=100147   -> actual time 18.7 ms, scanned 100000 rows for 167 results
--         (merge on):  Deduplicate rows sorted by row ID  -> actual time 0.338 ms
--         (index_merge union is ~55x faster than the scan here; timings machine dependent)
-- Step 4a: type=ref, key=idx_a_r, key_len=8, ref=const,const, rows=1, Extra: NULL
-- Step 4b: id1 PRIMARY ref idx_assignee rows=100 | id2 UNION ref idx_reporter rows=67 | UNION RESULT: Using temporary
-- Also seen: assignee_id BETWEEN 7 AND 30 AND priority=2 -> optimizer skipped merge (type=range, idx_assignee only)
```

```sql
-- ============================================
-- POSTGRESQL (verified on PGlite = PostgreSQL 18.6)
-- ============================================
CREATE TABLE tickets (id SERIAL PRIMARY KEY, assignee_id INT NOT NULL, reporter_id INT NOT NULL,
                      priority SMALLINT NOT NULL, title TEXT NOT NULL);
INSERT INTO tickets (assignee_id, reporter_id, priority, title)
SELECT (i*7)%1000+1, (i*13)%1500+1, i%5, 'Ticket '||i FROM generate_series(1,100000) i;
CREATE INDEX idx_assignee ON tickets(assignee_id);  CREATE INDEX idx_reporter ON tickets(reporter_id);  ANALYZE tickets;

EXPLAIN (COSTS OFF) SELECT * FROM tickets WHERE assignee_id=7 OR reporter_id=9;
-- Bitmap Heap Scan  Recheck Cond: ((assignee_id = 7) OR (reporter_id = 9))
--   -> BitmapOr -> Bitmap Index Scan on idx_assignee, Bitmap Index Scan on idx_reporter
EXPLAIN (COSTS OFF) SELECT * FROM tickets WHERE assignee_id=7 AND reporter_id=91;
-- Bitmap Heap Scan -> BitmapAnd( idx_reporter, idx_assignee )
SET enable_bitmapscan = off;   -- PG: without bitmaps -> Seq Scan (OR can't use a plain index scan)
CREATE INDEX idx_a_r ON tickets(assignee_id, reporter_id);  ANALYZE tickets;
-- AND query -> Index Scan using idx_a_r  Index Cond: ((assignee_id = 7) AND (reporter_id = 91))
```

---

## 🔍 Why This Works (3 lines max)
Each index returns a sorted list of primary keys; union deduplicates them, intersection keeps common ones, and then rows are fetched once (MySQL sort-merges the PKs, PG builds an in-memory bitmap of heap pages). It beats a scan when every predicate is selective.
हिंदी: हर index primary keys की सूची देता है; OR में उन्हें जोड़ा जाता है, AND में common रखा जाता है, फिर rows एक बार पढ़ी जाती हैं।

---

## ⚡ Alternative Solution

```sql
-- Control it in MySQL (global or per session):
SET SESSION optimizer_switch = 'index_merge_intersection=off';  -- if intersect plans are slower than composite
-- Hint per query:
SELECT /*+ NO_INDEX_MERGE(tickets idx_assignee, idx_reporter) */ * FROM tickets WHERE assignee_id=7 OR reporter_id=9;  -- not run
-- OR with a different shape: rewrite as UNION ALL with anti-duplicate predicate when each branch has its own best index.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Treating index_merge as "optimized": one index per predicate often means a composite is missing
-- ❌ OR on one indexed + one UNINDEXED column: merge impossible -> full scan
SELECT * FROM tickets WHERE assignee_id = 7 OR title = 'Ticket 5';
-- ❌ Intersection on non-selective columns (priority has 5 values): reading huge id-lists costs more than a scan
-- ✅ AND-heavy hot query -> composite index; OR-heavy -> ensure EACH side is indexed, or UNION.
```

---

## 🎯 Interview Tip (1 line)
Say: "Index merge is the optimizer combining single-column indexes - fine for OR when every branch is selective, but for AND I'd build a composite index; I check it in EXPLAIN (Using union/intersect) and compare against a UNION rewrite."

---

## 🔗 Related Questions
→ Q096 (Multi-column vs single indexes) | Q118 (OR vs UNION) | Q083 (Composite index order) | Q101 (EXPLAIN key columns)
