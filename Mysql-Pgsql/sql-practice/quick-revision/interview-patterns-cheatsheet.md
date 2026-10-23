# SQL Interview Patterns — Quick Cheatsheet
# Recognize the question type → apply the right pattern immediately

---

## 🔴 Pattern Recognition Guide

### "Find duplicate [emails/names/records]"
```sql
-- Pattern: GROUP BY + HAVING COUNT > 1
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;
-- Delete keeping MIN(id): DELETE ... WHERE id NOT IN (SELECT MIN(id) ... GROUP BY email)
-- File: 12-interview-classics/239-find-duplicates.md
```

### "Nth highest salary / 2nd highest / top N"
```sql
-- Pattern: DENSE_RANK (handles ties, no gaps)
SELECT salary FROM (SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS dr FROM employees) r WHERE dr = 2;
-- File: 03-joins/055-nth-highest-salary.md
```

### "Top N per group / best employee per department"
```sql
-- Pattern: ROW_NUMBER + PARTITION BY
SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn FROM employees) r WHERE rn <= 3;
-- File: 04-aggregations-window/075-top-n-per-group.md
```

### "Latest record per user / most recent order"
```sql
-- Pattern: ROW_NUMBER WHERE rn = 1
SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn FROM orders) r WHERE rn = 1;
-- Or PgSQL: SELECT DISTINCT ON (user_id) * FROM orders ORDER BY user_id, created_at DESC;
```

### "Day-over-day change / compare to previous row"
```sql
-- Pattern: LAG()
SELECT date, revenue, revenue - LAG(revenue) OVER (ORDER BY date) AS change FROM daily_sales;
-- File: 04-aggregations-window/067-lead-lag.md
```

### "Running total / cumulative sum"
```sql
-- Pattern: SUM() OVER (ORDER BY ...)
SELECT date, amount, SUM(amount) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total FROM sales;
```

### "Find employees earning more than their department average"
```sql
-- Pattern: Window AVG or JOIN to subquery (avoid correlated subquery!)
SELECT name, salary FROM (SELECT *, AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg FROM employees) x WHERE salary > dept_avg;
-- File: 02-subqueries/035-correlated-subquery.md
```

### "Consecutive login streak / gap and island"
```sql
-- Pattern: date - ROW_NUMBER() = constant for consecutive dates
SELECT user_id, MIN(login_date), MAX(login_date), COUNT(*) FROM
  (SELECT user_id, login_date, login_date - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) * INTERVAL '1 day' AS grp FROM user_logins) g
GROUP BY user_id, grp;
-- File: 12-interview-classics/240-consecutive-dates.md
```

### "Find records in A not in B"
```sql
-- Pattern: LEFT JOIN IS NULL (or NOT EXISTS)
SELECT a.* FROM tableA a LEFT JOIN tableB b ON a.id = b.id WHERE b.id IS NULL;
-- NOT EXISTS is safer with NULLs: SELECT * FROM a WHERE NOT EXISTS (SELECT 1 FROM b WHERE b.id = a.id)
```

### "Pagination on large table"
```sql
-- Pattern: Keyset pagination (WHERE id > last_seen_id)
-- BAD: LIMIT 20 OFFSET 1000000  → scans 1M rows
-- GOOD: WHERE id > 1000000 LIMIT 20  → O(log N) index seek
-- File: 01-fundamentals/011-pagination-keyset.md
```

### "Recursive hierarchy / org chart / tree traversal"
```sql
-- Pattern: WITH RECURSIVE CTE
WITH RECURSIVE tree AS (
  SELECT id, name, manager_id, 0 AS depth FROM employees WHERE manager_id IS NULL  -- anchor
  UNION ALL
  SELECT e.id, e.name, e.manager_id, t.depth + 1 FROM employees e JOIN tree t ON e.manager_id = t.id
) SELECT * FROM tree;
-- File: 01-fundamentals/019-recursive-cte.md
```

---

## 🟠 Index Decision Tree

```
Query has WHERE clause?
├── YES: What columns?
│   ├── Single column equality → Single B-Tree index
│   ├── Multiple columns (WHERE a = ? AND b = ?) → Composite index (a, b) [a first if more selective]
│   ├── Range on col + equality on another → Equality col FIRST, range col SECOND
│   ├── LIKE 'prefix%' → B-Tree index works
│   ├── LIKE '%suffix' → Full-text or no index (leading wildcard = no index)
│   └── JSONB key (PgSQL) → GIN index with @> operator
├── Has ORDER BY without matching index → Add order col to index → avoid filesort
├── SELECT only a few columns → Consider covering index (add SELECT cols to index)
└── NO useful WHERE → full scan, consider partitioning

EXPLAIN says:
  type=ALL (MySQL) / Seq Scan (PgSQL) on large table → MISSING INDEX
  "Using filesort" → ORDER BY needs index
  "Rows Removed by Filter" high → Add filter col to composite index
  "Index Scan" not "Index Only Scan" → Consider covering index
```

---

## 🟡 Transaction Pattern Reference

```
Bank transfer / inventory:
  BEGIN → FOR UPDATE (lock rows in ID order!) → validate → UPDATE → COMMIT
  On error: ROLLBACK
  On deadlock (MySQL 1213 / PgSQL 40P01): retry with backoff

Optimistic locking (low conflict):
  SELECT ... (read version) → UPDATE WHERE version = read_version AND id = ?
  If 0 rows affected → retry

Queue processing (no deadlock):
  SELECT FOR UPDATE SKIP LOCKED → process → UPDATE status = 'done' → COMMIT
```

---

## 🟢 Window Function Quick Reference

```sql
ROW_NUMBER()  OVER (PARTITION BY dept ORDER BY salary DESC)  → 1,2,3,4 (unique)
RANK()        OVER (PARTITION BY dept ORDER BY salary DESC)  → 1,2,2,4 (skip on tie)
DENSE_RANK()  OVER (PARTITION BY dept ORDER BY salary DESC)  → 1,2,2,3 (no skip)
LAG(col, N)   OVER (PARTITION BY dept ORDER BY date)         → prev row's value
LEAD(col, N)  OVER (PARTITION BY dept ORDER BY date)         → next row's value
SUM(col)      OVER (ORDER BY date ROWS UNBOUNDED PRECEDING)  → running total
AVG(col)      OVER (PARTITION BY dept)                       → group average (keeps all rows)
NTILE(4)      OVER (ORDER BY salary)                         → quartile (1-4)
FIRST_VALUE(col) OVER (PARTITION BY dept ORDER BY salary DESC) → dept max salary

WINDOW frame:
  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW  → from first to current
  ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING          → 5-row moving window
  RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW  → 7-day rolling (PgSQL)
```

---

## 🔵 MySQL vs PgSQL — Key Syntax Differences to Remember

```
Operation          | MySQL                          | PostgreSQL
───────────────────┼────────────────────────────────┼──────────────────────────────
Auto-increment     | AUTO_INCREMENT                 | SERIAL / GENERATED ALWAYS AS IDENTITY
Last insert ID     | LAST_INSERT_ID()               | RETURNING id
String concat      | CONCAT(a, b)                   | a || b
Random             | RAND()                         | RANDOM()
Date diff          | DATEDIFF(d1, d2) → int days    | d1 - d2 → interval
Date add           | DATE_ADD(d, INTERVAL 1 DAY)    | d + INTERVAL '1 day'
Regex              | col REGEXP 'pattern'           | col ~ 'pattern' / col ~* (case-insensitive)
Case-insensitive   | LIKE (default case-insensitive)| ILIKE
Upsert             | ON DUPLICATE KEY UPDATE        | ON CONFLICT (col) DO UPDATE
UPDATE with JOIN   | UPDATE a JOIN b SET ...        | UPDATE a SET ... FROM b WHERE ...
TRUNCATE rollback  | ❌ Auto-commits!               | ✅ Transactional
DDL rollback       | ❌ Auto-commits!               | ✅ Transactional
Default isolation  | REPEATABLE READ                | READ COMMITTED
JSON               | JSON (text, limited)           | JSONB (binary, GIN indexed)
Partial index      | ❌                             | CREATE INDEX ... WHERE condition
Concurrent index   | Online DDL (8.0)               | CREATE INDEX CONCURRENTLY
FK auto-index      | ✅ Auto-created                | ❌ Must create manually!
```

---

## ⚡ N+1 Detection and Fix Quick Reference

```
SYMPTOM: Same query repeated N times with different parameter values
         pg_stat_statements shows high call count for parameterized query

FIX 1 (aggregates): JOIN + GROUP BY
  FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id

FIX 2 (full records): IN-clause batch
  WHERE user_id IN (1, 2, 3, ... N)

FIX 3 (ORM): Eager loading
  Sequelize: include: [{ model: Order }]
  Prisma: include: { orders: true }
  Django: select_related('orders') / prefetch_related('orders')
```

---

## 🔴 Zero-Downtime Migration Checklist

```
ADD nullable column:      ALTER TABLE ADD COLUMN col TYPE NULL  → instant
ADD NOT NULL column:      1. Add NULL  2. Backfill in batches  3. ADD NOT NULL constraint (NOT VALID)  4. VALIDATE CONSTRAINT
ADD index:                CREATE INDEX CONCURRENTLY (PgSQL) / ALGORITHM=INPLACE,LOCK=NONE (MySQL 8)
RENAME column:            1. Add new  2. Dual-write trigger  3. Backfill  4. Switch reads  5. Drop old
CHANGE column type:       Same as rename — new column, backfill, switch, drop

Backfill rule: 1000-5000 rows per batch, 10-50ms sleep between batches
Always: test migration duration on staging with production-size data first
```

---

## 🟣 ACID + Isolation Quick Reference

```
Isolation Level   | Dirty Read | Non-Repeatable | Phantom | MySQL Default | PgSQL Default
──────────────────┼────────────┼────────────────┼─────────┼───────────────┼──────────────
READ UNCOMMITTED  | ✅ allowed | ✅ allowed     | ✅      | ·             | ·
READ COMMITTED    | ❌ blocked | ✅ allowed     | ✅      | ·             | DEFAULT ✓
REPEATABLE READ   | ❌ blocked | ❌ blocked     | ❌*     | DEFAULT ✓     | ·
SERIALIZABLE      | ❌ blocked | ❌ blocked     | ❌      | ·             | ·

* MySQL InnoDB: no phantom for non-locking reads. PgSQL: no phantom at all.
```

---

## 🟡 Schema Design Quick Decisions

```
Soft delete:       Add deleted_at TIMESTAMP NULL, partial index WHERE deleted_at IS NULL
Multi-tenant:      tenant_id in EVERY table, tenant_id LEFTMOST in every index
                   PgSQL: RLS with current_setting('app.tenant_id')
Hierarchies:       Adjacency list (parent_id) + recursive CTE for traversal
                   OR closure table for read-heavy trees
Audit log:         Separate audit table, trigger AFTER INSERT/UPDATE/DELETE
JSON storage:      PgSQL: JSONB + GIN index. MySQL: JSON column + generated column for common keys
Full-text search:  PgSQL: to_tsvector @@ to_tsquery + GIN index. MySQL: FULLTEXT + MATCH AGAINST
```
