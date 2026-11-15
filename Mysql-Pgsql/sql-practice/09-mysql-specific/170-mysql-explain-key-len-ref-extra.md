---

# Q170. MySQL EXPLAIN — key_len, ref, Extra
# Category: MySQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL (verified on MySQL 9.1; row estimates come from ANALYZE TABLE on 3,000 generated rows)

---

## ❓ Question
Read an EXPLAIN plan: use `key_len` to tell how many columns of a composite index are really used, `ref` to see what each index lookup is compared to, and `Extra` (Using index, Using where, Using filesort, Using temporary) to spot problems.

---

## 💡 Quick Concept (2 lines only)
key_len = bytes of the index actually used (sum of used column sizes), so you can count used columns; ref = the constant/column matched to the index; Extra = how rows are produced (covering index, extra filtering, sorting, temp table).
हिंदी: key_len से पता चलता है composite index के कितने columns use हुए; ref = किससे match हुआ; Extra = covering, filesort, temporary जैसी बातें।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

SET SESSION cte_max_recursion_depth = 5000;     -- needed to generate 3000 rows with a recursive CTE

CREATE TABLE customers (
  id INT PRIMARY KEY, email VARCHAR(100) NOT NULL, city VARCHAR(50),
  UNIQUE KEY uq_email (email)
);
CREATE TABLE orders (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT NOT NULL,
  status      VARCHAR(20) NOT NULL,
  note        VARCHAR(50) NULL,
  created_at  DATETIME NOT NULL,
  KEY idx_cust_status_created (customer_id, status, created_at),
  KEY idx_note (note)
) ENGINE=InnoDB;                                -- utf8mb4: 4 bytes per character

INSERT INTO customers
SELECT n, CONCAT('user',n,'@shop.com'), ELT(1+n%3,'Pune','Delhi','Mumbai')
FROM (WITH RECURSIVE s(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM s WHERE n<200) SELECT n FROM s) x;

INSERT INTO orders (customer_id,status,note,created_at)
SELECT 1+n%200, ELT(1+n%3,'paid','pending','shipped'), IF(n%5=0,NULL,'x'), DATE_ADD('2024-01-01', INTERVAL n HOUR)
FROM (WITH RECURSIVE s(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM s WHERE n<3000) SELECT n FROM s) x;

ANALYZE TABLE customers, orders;

-- ============================================
-- SOLUTION  (columns shown: type | key | key_len | ref | rows | Extra)
-- ============================================

-- key_len arithmetic:  customer_id INT NOT NULL = 4
--                      status VARCHAR(20) NOT NULL utf8mb4 = 20*4 + 2 (length bytes) = 82
--                      created_at DATETIME NOT NULL = 5
--                      nullable column adds +1

-- Q1: first column only
EXPLAIN SELECT id FROM orders WHERE customer_id = 7;
-- ref | idx_cust_status_created | 4  | const       | 15 | Using index

-- Q2: first two columns -> key_len 4 + 82 = 86, ref has two consts
EXPLAIN SELECT id FROM orders WHERE customer_id = 7 AND status = 'paid';
-- ref | idx_cust_status_created | 86 | const,const | 5  | Using index

-- Q3: range on the 3rd column -> uses all three (4+82+5 = 91), type becomes range
EXPLAIN SELECT id FROM orders WHERE customer_id = 7 AND status = 'paid' AND created_at >= '2024-03-01';
-- range | idx_cust_status_created | 91 | NULL | 2 | Using where; Using index

-- Q4: skipping the middle column -> key_len stays 4: created_at is only a filter, not a seek
EXPLAIN SELECT id FROM orders WHERE customer_id = 7 AND created_at >= '2024-03-01';
-- ref | idx_cust_status_created | 4 | const | 15 | Using where; Using index   (filtered 33.33%)

-- Q5: SELECT * is not covered (needs note) -> must fetch rows; and ORDER BY id forces a sort
EXPLAIN SELECT * FROM orders WHERE customer_id = 7 ORDER BY id DESC;
-- ref | idx_cust_status_created | 4 | const | 15 | Using filesort

-- Q6: leading column missing -> index unusable, full scan + sort
EXPLAIN SELECT * FROM orders WHERE status = 'paid' ORDER BY created_at;
-- ALL | NULL | NULL | NULL | 3000 | Using where; Using filesort     (filtered 10.00)

-- Q7: unique key lookup -> best case "const"
EXPLAIN SELECT * FROM customers WHERE email = 'user5@shop.com';
-- const | uq_email | 402 | const | 1 | NULL        (100*4 + 2 = 402)

-- Q8: leading wildcard LIKE -> no index
EXPLAIN SELECT * FROM customers WHERE email LIKE '%5@shop.com';
-- ALL | NULL | NULL | NULL | 200 | Using where

-- Q9: nullable column -> key_len = 50*4 + 2 + 1 = 203
EXPLAIN SELECT id FROM orders WHERE note IS NULL;
-- ref | idx_note | 203 | const | 600 | Using where; Using index

-- Q10: GROUP BY on a non-prefix column -> temporary table
EXPLAIN SELECT status, COUNT(*) FROM orders GROUP BY status;
-- index | idx_cust_status_created | 91 | NULL | 3000 | Using index; Using temporary

-- Q11: join - ref shows the driving column (output of a join run on this data)
EXPLAIN SELECT o.id, c.email FROM orders o JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'paid' AND o.customer_id < 5;
-- c: range PRIMARY  4  NULL         4 | Using where
-- o: ref   idx_cust_status_created 86 t.c.id,const 5 | Using index

-- Q12: actual vs estimated rows
EXPLAIN ANALYZE SELECT id FROM orders WHERE customer_id = 7 AND status = 'paid';
-- -> Covering index lookup on orders using idx_cust_status_created (customer_id = 7, status = 'paid')
--    (cost=0.761 rows=5) (actual time=0.00429..0.0055 rows=5 loops=1)       (timings vary per run)
```

---

## 🔍 Why This Works (3 lines max)
The optimizer reports the index bytes used per lookup, so dividing key_len into column sizes tells you how far into a composite index the seek goes; later columns after a gap or a range are only filtered. `Using index` means the index alone answered the query, while filesort/temporary mean extra sorting or grouping work.
हिंदी: key_len को columns के size में तोड़कर देखो कितना index इस्तेमाल हुआ; "Using index" = covering, filesort/temporary = extra काम।

---

## ⚡ Alternative Solution

```sql
-- Tree view and runtime stats (MySQL 8.0.16+/8.0.18+)
EXPLAIN FORMAT=TREE SELECT * FROM orders WHERE customer_id = 7 AND status = 'paid';
-- -> Index lookup on orders using idx_cust_status_created (customer_id = 7, status = 'paid')  (cost=1.75 rows=5)
EXPLAIN FORMAT=JSON SELECT ...;     -- adds used_key_parts, cost_info

-- Reading the type column, best -> worst:
--   system/const > eq_ref > ref > range > index (full index scan) > ALL (full table scan)
-- Other common Extra values: Using index condition (ICP), Using join buffer (no index on join column),
--   Using MRR, Backward index scan, Using index for group-by (loose scan)

-- PostgreSQL equivalent: EXPLAIN (ANALYZE, BUFFERS) -> "Index Only Scan", "Index Cond:" vs "Filter:",
-- "Sort Method", "Rows Removed by Filter". No key_len; Index Cond shows which columns were used.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: seeing "key = idx_cust_status_created" and assuming the whole index is used
--    -> check key_len: 4 means only customer_id is used for seeking
-- ❌ Wrong: ignoring rows/filtered: type=index with rows=3000 is a FULL index scan, not a lookup
-- ❌ Wrong: treating plain EXPLAIN estimates as truth; use EXPLAIN ANALYZE to see actual rows
-- ❌ Wrong: stale statistics -> run ANALYZE TABLE (before ANALYZE the first plan on this data said rows=1, after: 15)
-- ❌ Wrong: LIKE '%abc', functions on indexed columns (DATE(created_at) = ...), or implicit casts
--    (varchar column = number) which silently disable the index
```

---

## 🎯 Interview Tip (1 line)
Say: "I check type for scan style, key_len to see how many composite-index columns are actually used for the seek, ref for what's matched, rows x filtered for cost, and Extra for filesort/temporary/covering — then confirm with EXPLAIN ANALYZE and fresh statistics before changing indexes."

---

## 🔗 Related Questions
→ Q173 (Invisible indexes) | Q162 (InnoDB buffer pool) | Q171 (Window functions) | Q075 (Top N per group)
