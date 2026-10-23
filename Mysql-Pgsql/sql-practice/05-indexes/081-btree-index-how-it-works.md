---

# Q081. B-Tree Index — How Does It Work?
# Category: Indexes
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Explain how a B-Tree index works internally. How does MySQL InnoDB differ from PostgreSQL in index structure? When does an index help, and when is a full table scan chosen instead?

---

## 💡 Quick Concept (2 lines only)
B-Tree (Balanced Tree) keeps data sorted in a multi-level tree — lookup is O(log N) instead of O(N) full scan. MySQL InnoDB's PRIMARY KEY is a clustered index (actual row data in leaf nodes), while secondary indexes store the primary key as a pointer. PgSQL uses heap tables with all indexes as non-clustered.
हिंदी: B-Tree sorted tree है — O(log N) lookup। MySQL में PRIMARY KEY clustered index है (leaf में actual data)। PgSQL में सभी indexes non-clustered हैं (heap table separate)।

---

## ✅ Answer / Solution

```
// ============================================
// B-TREE STRUCTURE (conceptual)
// ============================================

Table: employees (id INT PK, name VARCHAR, salary INT, dept_id INT)
CREATE INDEX idx_salary ON employees(salary);

B-Tree for salary index:
                    [50000]                     ← root node (splits range)
                   /       \
          [30000]            [70000]            ← internal nodes
          /     \            /     \
    [20000]  [40000]   [60000]  [80000]         ← leaf nodes
       ↓        ↓        ↓        ↓
  Row ptrs   Row ptrs  Row ptrs  Row ptrs       ← points to actual row

Leaf nodes are DOUBLY LINKED:
[20000] ←→ [30000] ←→ [40000] ←→ [50000] ←→ [60000] ←→ [70000] ←→ [80000]
→ Enables RANGE SCANS efficiently!
  SELECT * WHERE salary BETWEEN 30000 AND 60000 → traverse from [30000] to [60000]

Height of tree:
  1M rows → B-Tree height ≈ 3-4 levels
  Each node holds ~100-200 keys (page size 16KB / key+pointer size)
  1 disk read per level → 3-4 disk reads to find any value
  vs Full scan: 1M rows → potentially 1M disk reads!

// ============================================
// MySQL InnoDB — CLUSTERED INDEX (Primary Key)
// ============================================

InnoDB PRIMARY KEY structure:
Leaf nodes contain:
  ┌────────────────────────────────────────────────────────┐
  │ PK value (id) │ ALL other columns (name, salary, dept) │  ← ACTUAL ROW DATA!
  └────────────────────────────────────────────────────────┘
→ This is a CLUSTERED INDEX — the row IS the index leaf!
→ Physical row order on disk ≈ primary key order
→ PRIMARY KEY lookup = reach leaf = done (no extra pointer)

InnoDB SECONDARY INDEX (idx_salary) structure:
Leaf nodes contain:
  ┌────────────────────────────────────────────────────────┐
  │ indexed column (salary) │ PRIMARY KEY value (id)       │
  └────────────────────────────────────────────────────────┘
→ Secondary index stores PK, not row pointer
→ Lookup: find salary in secondary index → get id → look up id in PRIMARY KEY tree
→ This second lookup is called "DOUBLE LOOKUP" or "KEY LOOKUP" (bookmark lookup)

// ============================================
// PostgreSQL — HEAP TABLE (All indexes non-clustered)
// ============================================

PgSQL heap table:
  - Rows stored in heap pages (no inherent order)
  - ALL indexes (including "PRIMARY KEY") are separate B-Tree files
  - Index leaf nodes store: indexed_value + heap tuple id (TID = page+offset)
  - Lookup: find value in index → TID → fetch row from heap page
  - Same cost for all index types (no "clustered" advantage)

PgSQL CLUSTER command (one-time):
  CLUSTER employees USING idx_salary;
  → Physically reorders heap to match index order
  → NOT automatic — table unsorted again after new inserts

// ============================================
// WHEN INDEX IS USED vs FULL TABLE SCAN
// ============================================

-- Optimizer uses index when:
-- 1. Selective query (few rows) — index useful if selectivity < ~5-15% of table

SELECT * FROM employees WHERE id = 5;           -- ALWAYS uses PK index
SELECT * FROM employees WHERE salary = 90000;   -- uses idx_salary (few matches)
SELECT * FROM employees WHERE salary BETWEEN 80000 AND 100000;  -- range scan

-- Optimizer SKIPS index (full scan) when:
-- 2. Low cardinality — too many matching rows (e.g., status IN ('active','inactive'))

SELECT * FROM employees WHERE dept_id = 1;
-- If dept_id=1 is 60% of rows → full scan is cheaper!
-- Optimizer estimates: 60% of rows × row size vs index overhead → full scan wins

-- 3. Function on indexed column (function prevents index use!)
SELECT * FROM employees WHERE UPPER(name) = 'ALICE';   -- ❌ no index on UPPER(name)
SELECT * FROM employees WHERE YEAR(created_at) = 2024; -- ❌ kills index!

-- ✅ Fix: rewrite to avoid function on column:
SELECT * FROM employees WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';

-- 4. Leading wildcard in LIKE:
SELECT * FROM employees WHERE name LIKE '%Alice%';  -- ❌ full scan (% at start)
SELECT * FROM employees WHERE name LIKE 'Alice%';   -- ✅ uses index (fixed prefix)

-- 5. Implicit type conversion:
SELECT * FROM employees WHERE id = '5';  -- id is INT, '5' is string → ❌ may skip index (MySQL)
-- ✅ Always match data types

-- 6. Small table (< ~1000 rows) → optimizer picks full scan anyway

// ============================================
// COMPOSITE INDEX — COLUMN ORDER MATTERS
// ============================================

CREATE INDEX idx_dept_salary ON employees(dept_id, salary);
-- This index is sorted by: dept_id FIRST, then salary within each dept

-- Uses index:
SELECT * FROM employees WHERE dept_id = 1;               -- ✅ leftmost prefix
SELECT * FROM employees WHERE dept_id = 1 AND salary > 80000; -- ✅ both columns
SELECT * FROM employees WHERE dept_id = 1 ORDER BY salary;    -- ✅ avoids sort

-- Does NOT use index:
SELECT * FROM employees WHERE salary > 80000;            -- ❌ missing leftmost (dept_id)
-- Can't skip to salary in the index without knowing dept_id!

-- RULE: Leftmost prefix rule
-- Composite index (a, b, c) → usable for queries on: a | a,b | a,b,c | a,c*
-- NOT for: b | c | b,c (missing leftmost column a)
-- *a,c is trickier — optimizer uses a part, filters c in memory
```

---

## 🔍 Why This Works (3 lines max)
B-Tree keeps keys sorted at all levels — finding any value is O(log N) because the tree height is logarithmic in the number of rows. The linked leaf nodes allow efficient range scans without returning to the root. MySQL's clustered primary key means a primary key lookup reads the actual data in one tree traversal; secondary indexes require a second traversal to the clustered index.
हिंदी: B-Tree sorted tree है, हर lookup O(log N) है। MySQL PK lookup = एक tree traversal में actual data। Secondary index में PK milega फिर second lookup।

---

## ⚡ Alternative Solution

```sql
-- Check if index is being used (EXPLAIN):
EXPLAIN SELECT * FROM employees WHERE salary = 80000;
-- Look for: type = 'ref' or 'range' (good) vs 'ALL' (full scan, bad)
-- key: shows which index was chosen
-- rows: estimated rows examined

-- MySQL EXPLAIN output:
-- id | type | key         | key_len | ref   | rows | Extra
-- 1  | ref  | idx_salary  | 5       | const |  3   |
-- type=ref → using index! rows=3 → only 3 rows examined!

-- vs full scan:
-- id | type | key  | rows  | Extra
-- 1  | ALL  | NULL | 10000 | Using where
-- type=ALL → full table scan!

-- PgSQL EXPLAIN ANALYZE:
EXPLAIN ANALYZE SELECT * FROM employees WHERE salary = 80000;
-- Index Scan using idx_salary on employees (cost=0.29..8.30 rows=1 width=50)
--   (actual time=0.062..0.065 rows=1 loops=1)
-- Planning time: 0.3ms | Execution time: 0.1ms
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Indexing low-cardinality columns alone
CREATE INDEX idx_status ON orders(status);
-- status has only 3 values (pending/completed/cancelled)
-- 33% of rows per value → optimizer chooses full scan anyway!
-- This index wastes space and causes write overhead

-- ✅ Better: Composite index with high-cardinality column first
CREATE INDEX idx_user_status ON orders(user_id, status);
-- user_id has high cardinality → filters down to small set → then status

-- ❌ Wrong: Too many indexes on write-heavy table
-- Every INSERT/UPDATE/DELETE must update ALL indexes!
-- 5 indexes on orders → each INSERT updates 5 tree structures!
-- ✅ Balance: index columns you actually query, remove unused ones

-- ❌ Wrong: Expecting index on expression to work automatically
SELECT * FROM users WHERE LOWER(email) = 'alice@example.com';
-- Regular index on email won't help!
-- ✅ MySQL 8.0 / PgSQL: Create functional index:
-- PgSQL: CREATE INDEX idx_email_lower ON users(LOWER(email));
-- MySQL 8.0: CREATE INDEX idx_email_lower ON users((LOWER(email)));
```

---

## 🎯 Interview Tip (1 line)
Say: "MySQL InnoDB's clustered primary key means PK lookups are fastest (row IS the leaf node). Secondary index lookups do a double-lookup — first in the secondary tree, then in the PK tree. In PgSQL, all indexes are equal but CLUSTER can physically order the heap to match one index."

---

## 🔗 Related Questions
→ Q082 (clustered vs non-clustered) | Q083 (composite index order) | Q084 (covering index) | Q086 (EXPLAIN reading) | Q099 (LIKE and index)
