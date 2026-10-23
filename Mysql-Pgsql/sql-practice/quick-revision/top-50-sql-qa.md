# Top 50 SQL Interview Q&A — Quick Revision
# 5+ YOE — MySQL + PostgreSQL — Must Know Cold

---

## 🔴 Fundamentals (Q1-Q10)

**Q1. What is the difference between WHERE and HAVING?**
A: WHERE filters rows BEFORE aggregation (acts on individual rows). HAVING filters AFTER aggregation (acts on groups). WHERE cannot reference aggregate functions (COUNT, SUM, etc.) because aggregation hasn't happened yet. HAVING can. Example: `WHERE salary > 50000` (individual row filter). `HAVING COUNT(*) > 5` (group filter — only groups with more than 5 members). You can use both together: WHERE filters input rows first, then GROUP BY aggregates, then HAVING filters groups.

**Q2. What is the difference between DELETE, TRUNCATE, and DROP?**
A: DELETE is DML — removes specific rows (WHERE clause), fires triggers, transactional (rollbackable), slow on large tables, no auto-increment reset. TRUNCATE is DDL — removes ALL rows, no WHERE, no triggers, fast (deallocates pages), resets auto-increment. In MySQL: TRUNCATE auto-commits (can't rollback!). In PgSQL: TRUNCATE is transactional. DROP removes the entire table (structure + data + indexes) — irreversible in MySQL, rollbackable in PgSQL.

**Q3. What does NULL mean and how do you handle it correctly?**
A: NULL means "unknown" — not zero, not empty string. NULL does NOT equal NULL: `NULL = NULL` is NULL (not true!). Always use `IS NULL` or `IS NOT NULL`. Aggregate functions (SUM, AVG, COUNT) ignore NULLs — `COUNT(column)` skips NULLs, `COUNT(*)` counts all rows. Use `COALESCE(col, 0)` for NULL replacement. `NULLIF(a, b)` returns NULL if a=b (useful for division: `NULLIF(denominator, 0)` prevents division by zero error).

**Q4. What is the difference between UNION and UNION ALL?**
A: UNION removes duplicates (requires sorting — slower). UNION ALL keeps all rows including duplicates (faster). Use UNION when you need distinct results. Use UNION ALL when you know there are no duplicates or don't care. Both require same number of columns with compatible types. UNION ALL is significantly faster for large datasets — avoid UNION unless deduplication is required.

**Q5. What is the difference between IN and EXISTS?**
A: IN evaluates the subquery first, produces a value list, then checks each row against the list — efficient when the subquery returns a small result set. EXISTS stops as soon as it finds the first matching row — efficient when the subquery returns a large result set or when you just need to check existence. `IN` with NULL: `WHERE id IN (1, NULL, 3)` — NULL in the list can cause unexpected results. `NOT IN` with any NULL → returns no rows! `NOT EXISTS` doesn't have this NULL issue. For large tables: EXISTS is generally preferred.

**Q6. How does LIMIT + OFFSET work and what is the problem with large offsets?**
A: `LIMIT 20 OFFSET 10000` — database scans and discards 10,000 rows then returns 20. Performance degrades linearly with offset size: OFFSET 100,000 = scan 100,000 rows. Fix: Keyset/cursor pagination — instead of OFFSET, use `WHERE id > last_seen_id LIMIT 20`. This is O(log N) using the index — doesn't scan discarded rows. Trade-off: can't jump to arbitrary page (must paginate forward).

**Q7. What are CTEs and what is a recursive CTE?**
A: CTE (WITH clause) is a named temporary result set within a query — improves readability, can be referenced multiple times, doesn't improve performance over subquery (optimizer usually treats them the same). Recursive CTE has two parts separated by UNION ALL: base case (anchor) + recursive case (references the CTE itself). Use for hierarchical data: `WITH RECURSIVE org AS (SELECT id, parent_id, name FROM employees WHERE parent_id IS NULL UNION ALL SELECT e.id, e.parent_id, e.name FROM employees e JOIN org ON e.parent_id = org.id) SELECT * FROM org;`

**Q8. What is the difference between CHAR and VARCHAR and TEXT?**
A: CHAR(n) is fixed-length — always uses n bytes, padded with spaces. Fast for fixed-length data (country codes, status codes). VARCHAR(n) is variable-length — uses only actual content length + 1-2 bytes overhead. TEXT has no length limit. In MySQL: CHAR is slightly faster for fixed-length (no length calculation), VARCHAR better for variable data. In PostgreSQL: VARCHAR(n) and TEXT are the same internally — no performance difference (TEXT preferred). Use CHAR only for truly fixed-length fields (ISO country code = CHAR(2), UUID = CHAR(36)).

**Q9. What is a covering index?**
A: A covering index contains ALL columns needed by a query — the query can be answered from the index alone without touching the actual table rows. "Covering" = the index "covers" the query. Example: `SELECT email FROM users WHERE username = 'alice'` — if index is `(username, email)`, MySQL shows "Using index" in EXPLAIN (no table lookup needed). PostgreSQL: `CREATE INDEX idx ON users(username) INCLUDE (email)` (PG11+ INCLUDE syntax). Covering indexes dramatically reduce I/O for read-heavy queries.

**Q10. When does MySQL NOT use an index?**
A: Index is skipped when: (1) Function on indexed column: `WHERE YEAR(created_at) = 2024` — rewrite as range. (2) LIKE with leading wildcard: `WHERE name LIKE '%alice'`. (3) Type mismatch: `WHERE int_col = '123'` (string vs int). (4) OR without index on all conditions: use UNION instead. (5) NOT IN / NOT LIKE on non-selective index. (6) Low cardinality: if matching rows > ~15% of table, full scan is cheaper. (7) Missing leftmost index prefix in composite index. (8) Small table (optimizer picks full scan for <~1000 rows).

---

## 🟠 Joins (Q11-Q18)

**Q11. What is the difference between INNER JOIN and LEFT JOIN with an example?**
A: INNER JOIN returns only matching rows (intersection). LEFT JOIN returns ALL rows from left table, matching rows from right (NULLs for no match). Example: `users LEFT JOIN orders ON users.id = orders.user_id` — returns ALL users, even those with no orders (orders columns are NULL). INNER JOIN would exclude users with no orders. Use LEFT JOIN when you need to find records without matches: `WHERE orders.id IS NULL` — finds users who have NEVER ordered.

**Q12. How do you find records in Table A that are NOT in Table B?**
A (3 methods):
```sql
-- Method 1: LEFT JOIN + IS NULL (most common, fast)
SELECT a.* FROM tableA a LEFT JOIN tableB b ON a.id = b.id WHERE b.id IS NULL;
-- Method 2: NOT EXISTS (stops at first match — efficient for large B)
SELECT * FROM tableA a WHERE NOT EXISTS (SELECT 1 FROM tableB WHERE id = a.id);
-- Method 3: NOT IN (careful with NULLs in tableB!)
SELECT * FROM tableA WHERE id NOT IN (SELECT id FROM tableB WHERE id IS NOT NULL);
```
Performance: LEFT JOIN IS NULL ≈ NOT EXISTS (optimizer usually picks same plan). NOT IN is dangerous if subquery can return NULLs.

**Q13. What is a SELF JOIN and when is it used?**
A: A SELF JOIN joins a table to itself — used for hierarchical/relational data within the same table. Classic example: employee-manager relationship where both are in the same employees table. `SELECT e.name AS employee, m.name AS manager FROM employees e LEFT JOIN employees m ON e.manager_id = m.id` — joins employees table to itself, treating each row as both employee and manager. Also used for: finding duplicate rows, comparing rows within the same table (pairs, sequences).

**Q14. What is the nth highest salary classic problem?**
A:
```sql
-- DENSE_RANK approach (best — handles ties):
SELECT salary FROM (
  SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS dr FROM employees
) ranked WHERE dr = 2;  -- 2nd highest

-- Simple LIMIT/OFFSET (MySQL, doesn't handle ties):
SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1;
-- OFFSET N-1 for Nth highest

-- PgSQL with OFFSET:
SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1;
```
DENSE_RANK is preferred — handles ties correctly and works for any N.

**Q15. What is a LATERAL JOIN in PostgreSQL?**
A: LATERAL allows a subquery in FROM to reference columns from preceding tables — like a correlated subquery in the FROM clause. Regular JOIN: right side can't reference left side. LATERAL: right side CAN reference left side. Use case: `SELECT u.name, recent.* FROM users u JOIN LATERAL (SELECT * FROM orders WHERE user_id = u.id ORDER BY created_at DESC LIMIT 1) AS recent ON true` — gets each user's most recent order. Equivalent to: for each user, run a separate query. Can replace complex subqueries or window functions.

**Q16. What is the difference between JOIN and subquery performance?**
A: Modern optimizers often produce the same plan for equivalent JOIN and subquery. Generally: correlated subquery (references outer query) is slower — runs once per outer row. Non-correlated subquery or JOIN: similar. Window functions beat both for running totals/rankings (single pass). Rule of thumb: JOIN when combining data. EXISTS subquery when checking existence (stops at first match). Window function when ranking or running aggregates. Check EXPLAIN to see actual plan — don't assume.

**Q17. How do you delete duplicate rows keeping only one?**
A:
```sql
-- Keep the row with MIN(id):
DELETE FROM employees WHERE id NOT IN (
  SELECT MIN(id) FROM employees GROUP BY name, salary, dept_id
);
-- MySQL: can't reference same table in DELETE subquery directly
-- Wrap in subquery:
DELETE FROM employees WHERE id NOT IN (
  SELECT id FROM (
    SELECT MIN(id) AS id FROM employees GROUP BY name, salary, dept_id
  ) keep
);
-- PgSQL: use CTE
WITH keep AS (SELECT MIN(id) AS id FROM employees GROUP BY name, dept_id)
DELETE FROM employees WHERE id NOT IN (SELECT id FROM keep);
```

**Q18. Find customers who ordered in January but NOT in February.**
A:
```sql
SELECT DISTINCT user_id FROM orders
WHERE MONTH(created_at) = 1 AND YEAR(created_at) = 2024
  AND user_id NOT IN (
    SELECT user_id FROM orders
    WHERE MONTH(created_at) = 2 AND YEAR(created_at) = 2024
  );
-- Or with LEFT JOIN (more efficient):
SELECT DISTINCT jan.user_id FROM orders jan
LEFT JOIN orders feb
  ON jan.user_id = feb.user_id
  AND MONTH(feb.created_at) = 2 AND YEAR(feb.created_at) = 2024
WHERE MONTH(jan.created_at) = 1 AND YEAR(jan.created_at) = 2024
  AND feb.user_id IS NULL;  -- no matching Feb row
```

---

## 🟡 Aggregations & Window Functions (Q19-Q26)

**Q19. What is the difference between ROW_NUMBER, RANK, and DENSE_RANK?**
A: ROW_NUMBER: always unique sequential (1,2,3,4) — ties get different numbers arbitrarily. RANK: ties get same number, next number skips (1,2,2,4 — no 3). DENSE_RANK: ties get same number, next is consecutive (1,2,2,3 — no skip). Use: ROW_NUMBER for exactly-one-per-group. RANK for medal-style (ties allowed, gaps OK). DENSE_RANK for "Nth highest value" queries (WHERE dr = 2 always works, gaps would mean WHERE rank = 2 might return nothing if N=3 skipped).

**Q20. What are LEAD and LAG window functions?**
A: LAG(col, N) accesses the Nth previous row's value. LEAD(col, N) accesses the Nth next row's value. Use case: day-over-day change: `SELECT date, revenue, LAG(revenue, 1) OVER (ORDER BY date) AS prev_revenue, revenue - LAG(revenue, 1) OVER (ORDER BY date) AS daily_change FROM daily_sales`. Also: detect gaps in sequences (compare current row's value with previous). Can provide a default value: `LAG(col, 1, 0)` — returns 0 when no previous row.

**Q21. How do you calculate a running total?**
A:
```sql
SELECT date, amount,
  SUM(amount) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM sales;
-- ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW: sum from first row to current
-- Can also partition: SUM(amount) OVER (PARTITION BY user_id ORDER BY date)
-- → running total per user
```

**Q22. What is the difference between ROWS BETWEEN and RANGE BETWEEN?**
A: ROWS uses physical row positions. RANGE uses logical value ranges. With duplicate ORDER BY values: ROWS treats them as separate rows (deterministic). RANGE includes all rows with the same value as the current row (may include/exclude more rows). For running totals: ROWS is usually what you want. RANGE default in `SUM() OVER (ORDER BY col)` = `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` — includes all rows with same value as current in the aggregate, which can produce unexpected results with ties.

**Q23. How do you get the top N rows per group?**
A:
```sql
-- Using ROW_NUMBER (recommended):
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rn
  FROM employees
) ranked WHERE rn <= 3;  -- top 3 per department
-- Add tiebreaker in ORDER BY for determinism: ORDER BY salary DESC, id ASC

-- MySQL pre-8.0 (no window functions):
SELECT e1.* FROM employees e1
WHERE (SELECT COUNT(*) FROM employees e2 WHERE e2.dept_id = e1.dept_id AND e2.salary > e1.salary) < 3;
-- Slow! O(n²) — use window functions when available
```

**Q24. What is GROUP BY ROLLUP?**
A:
```sql
SELECT dept, job_title, SUM(salary) FROM employees
GROUP BY ROLLUP(dept, job_title);
-- Produces: subtotals for each dept (job_title = NULL) + grand total (both NULL)
-- Results:
-- Engineering | Backend  | 300000
-- Engineering | Frontend | 200000
-- Engineering | NULL     | 500000  ← subtotal for Engineering
-- Sales       | SDR      | 150000
-- Sales       | NULL     | 150000  ← subtotal for Sales
-- NULL        | NULL     | 650000  ← grand total
-- Use GROUPING(dept) to distinguish real NULLs from ROLLUP NULLs
```

**Q25. How do you find the gap and island in a sequence?**
A:
```sql
-- Islands: consecutive groups of values
-- Find start and end of each consecutive run of logins:
SELECT MIN(login_date) AS start, MAX(login_date) AS end
FROM (
  SELECT login_date,
    DATE_SUB(login_date, INTERVAL ROW_NUMBER() OVER (ORDER BY login_date) DAY) AS grp
  FROM user_logins WHERE user_id = 1
) groups
GROUP BY grp;
-- Each "island" of consecutive days gets the same grp value
-- (date - row_number is constant for consecutive dates)
```

**Q26. What is PARTITION BY vs GROUP BY?**
A: GROUP BY collapses multiple rows into one group — you get one row per group. PARTITION BY (in window functions) divides rows into groups but KEEPS all individual rows — adds a window calculation alongside each row without collapsing. `SELECT dept, SUM(salary) FROM employees GROUP BY dept` → one row per dept. `SELECT name, dept, SUM(salary) OVER (PARTITION BY dept) AS dept_total FROM employees` → all rows preserved, each row shows its department's total alongside.

---

## 🟢 Indexes + Query Optimization (Q27-Q35)

**Q27. How do you read EXPLAIN output in MySQL?**
A: Key columns: `type` = access method (ALL=full scan, range=index range, ref=index lookup, const/eq_ref=best). `key` = index used (NULL=no index). `rows` = estimated rows examined (lower=better). `Extra` = important flags: "Using index" (covering — good!), "Using filesort" (needs sort in memory/disk — bad for large sets), "Using temporary" (temp table created — bad!), "Using where" (WHERE applied after index). Goal: avoid `type=ALL` and `Extra: Using filesort` on large tables.

**Q28. What is the N+1 query problem?**
A: N+1 = 1 query to get N records + N individual queries for each record's related data. Example: `SELECT * FROM users` returns 100 users → loop makes 100 separate `SELECT * FROM orders WHERE user_id = ?` queries = 101 total queries. Fix in SQL: JOIN + aggregate: `SELECT u.*, COUNT(o.id) AS order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id`. In ORM: use eager loading (`include` in Sequelize, `with` in Eloquent, `select_related` in Django).

**Q29. How do you optimize a COUNT(*) on a large table?**
A: (1) MySQL InnoDB: `SELECT TABLE_ROWS FROM information_schema.TABLES WHERE table_name='orders'` — approximate count stored in metadata (fast but not exact). (2) Maintain a counter table with triggers or application-level increment. (3) Add a covering index and use `COUNT(id)` instead of `COUNT(*)` — may help MySQL use a smaller index. (4) PgSQL: `SELECT reltuples FROM pg_class WHERE relname = 'orders'` — fast estimate. (5) Exact count with condition: ensure WHERE uses index — `EXPLAIN` to verify. Note: InnoDB doesn't store exact count (MVCC requires counting visible rows).

**Q30. What is a partial index in PostgreSQL?**
A:
```sql
-- Index only the rows you actually query:
CREATE INDEX idx_active_users ON users(email) WHERE active = true;
-- Only indexes active users (say 5% of table) — tiny index vs full table index!

-- Queries that use it:
SELECT * FROM users WHERE email = 'alice@example.com' AND active = true;
-- Index is only used when WHERE clause matches the partial condition

-- Benefits: smaller index, faster reads/writes, less maintenance
-- MySQL: doesn't support partial indexes (workaround: index on generated column)
```

**Q31. How do you add an index to a large production table without downtime?**
A: MySQL 8.0: Online DDL — `ALTER TABLE ADD INDEX` uses online DDL by default (reads/writes allowed during build). Check with `ALGORITHM=INPLACE, LOCK=NONE`. PgSQL: `CREATE INDEX CONCURRENTLY idx_name ON table(col)` — builds index without exclusive lock, reads/writes continue. Tradeoff: takes longer (needs two scans), can fail (retry), slightly different from regular CREATE INDEX. Never use regular `CREATE INDEX` without CONCURRENTLY on large PgSQL tables in production — it takes an exclusive lock.

**Q32. What causes "Using filesort" and how to fix it?**
A: "Using filesort" appears when MySQL can't serve ORDER BY from an index — must sort in memory or on disk. Fix: create an index that matches the ORDER BY (same columns, same direction). If query has WHERE + ORDER BY: composite index `(where_col, order_col)`. If ORDER BY has mixed ASC/DESC: MySQL 8.0 supports descending indexes. Check if query has LIMIT — small LIMIT with filesort may still be fast (sorts small result). For large tables without ORDER BY index: add the right composite index.

**Q33. When should you use a composite index vs multiple single-column indexes?**
A: Composite index `(a, b)` is one tree structure — can serve queries on `a`, `a,b`, and sometimes `a,c`. Multiple single-column indexes: optimizer can only use one per query (unless index merge). Composite is better when you consistently query the combination. Single columns better when: columns are queried independently in different queries. Rule: match the most selective filter as leftmost column. For ORDER BY: include the sort column in composite index to avoid filesort. Too many composite indexes = write overhead.

**Q34. What is connection pooling and why is it needed?**
A: Opening a DB connection is expensive (~50-100ms for TCP handshake, auth, init). Without pooling: each request opens/closes connection — waste at scale. Connection pool: maintain N persistent connections, requests borrow/return them. PgBouncer (PgSQL): pool modes: session (1:1 connection), transaction (borrow per transaction — most efficient), statement (borrow per statement). PgBouncer transaction mode allows hundreds of app connections to share ~20 real DB connections. Set `pool_size` based on `max_connections` setting. Too many DB connections = memory + scheduling overhead on PostgreSQL.

**Q35. How do you optimize pagination for a 100M row table?**
A:
```sql
-- BAD: OFFSET gets slower as page increases
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 5000000;
-- → Scans and discards 5M rows!

-- GOOD: Keyset pagination (cursor-based)
-- First page:
SELECT * FROM orders ORDER BY id ASC LIMIT 20;
-- → Returns rows up to id=20

-- Next page (pass last_id = 20 from previous response):
SELECT * FROM orders WHERE id > 20 ORDER BY id ASC LIMIT 20;
-- → Uses index on id directly, O(log N) lookup, no scanning!

-- For compound sort (e.g., created_at + id):
SELECT * FROM orders
WHERE (created_at, id) > ('2024-01-15', 1234)  -- PgSQL row comparison
ORDER BY created_at ASC, id ASC
LIMIT 20;
```

---

## 🔵 Transactions + Schema (Q36-Q45)

**Q36. What is MVCC (Multi-Version Concurrency Control)?**
A: MVCC allows readers and writers to not block each other — each transaction sees a snapshot of the database at a point in time. Readers don't block writers (no shared lock needed), writers don't block readers. How: on UPDATE, old version of row is kept alongside new version. Each transaction sees the version that was current at its start (based on transaction ID). MySQL InnoDB: stores old versions in undo log (purged by background thread). PgSQL: stores old row versions as "dead tuples" in heap — needs VACUUM to reclaim space.

**Q37. What are the four transaction isolation levels?**
A: READ UNCOMMITTED (weakest) — can read uncommitted changes (dirty reads). READ COMMITTED — reads only committed data, but same query in same transaction can return different results (non-repeatable reads). REPEATABLE READ (MySQL default) — same query returns same result within transaction (snapshot), but new rows can appear (phantom reads). SERIALIZABLE (strictest) — fully isolated, transactions run as if serial, no anomalies, lowest concurrency. MySQL's InnoDB REPEATABLE READ also prevents most phantom reads using next-key locks. PostgreSQL default is READ COMMITTED.

**Q38. What is optimistic vs pessimistic locking?**
A: Pessimistic: assume conflicts are frequent — lock before reading (`SELECT FOR UPDATE`), hold until transaction ends. Safe but reduces concurrency. Use for: high-conflict resources (bank accounts, inventory). Optimistic: assume conflicts are rare — read without locking, validate before writing (version check: `UPDATE ... WHERE version = read_version AND id = ?`, check 0 rows affected = conflict → retry). More concurrent but requires retry logic. Use for: low-conflict resources (user profile updates, blog posts). SELECT FOR UPDATE is pessimistic. Version column is optimistic.

**Q39. What is SELECT FOR UPDATE SKIP LOCKED?**
A: `SKIP LOCKED` skips rows that are locked by another transaction instead of waiting. Use case: job queue — multiple workers claim tasks without stepping on each other's toes. `SELECT id FROM tasks WHERE status = 'pending' LIMIT 1 FOR UPDATE SKIP LOCKED` — Worker A gets task 1, Worker B gets task 2 (skips locked task 1). No waiting, no deadlocks. Without SKIP LOCKED: all workers queue on the same row → serialized, slow. MySQL 8.0+, PgSQL both support.

**Q40. What is database normalization?**
A: Organizing tables to minimize redundancy. 1NF: atomic values (no repeating groups, no arrays in columns). 2NF: 1NF + no partial dependencies (non-key columns depend on WHOLE key, not part of it — matters for composite keys). 3NF: 2NF + no transitive dependencies (non-key column depends on another non-key column). Example: `orders(order_id, customer_id, customer_city)` — customer_city depends on customer_id, not order_id → violates 3NF → move to customers table. Denormalize when read performance outweighs update complexity.

**Q41. What are the three approaches to multi-tenancy?**
A: (1) **Separate databases** — each tenant gets their own DB. Best isolation, easy backup per tenant, scales independently. But: expensive, hard to manage 1000+ DBs. (2) **Separate schemas** (PgSQL) — one DB, one schema per tenant. Good isolation, easier than separate DBs. PgSQL `search_path = 'tenant_123'` routes queries. (3) **Shared table with tenant_id column** — all tenants share tables, every query filters by `tenant_id`. Cheapest, easiest to manage, but data mixing risk — row-level security (PgSQL RLS) can enforce this automatically.

**Q42. How do you design a soft delete?**
A: Add `deleted_at TIMESTAMP NULL DEFAULT NULL` column. Delete = `UPDATE SET deleted_at = NOW()` instead of DELETE. Query = always add `WHERE deleted_at IS NULL`. Problems: indexes don't filter deleted rows → create partial index: `CREATE INDEX idx_active ON orders(user_id) WHERE deleted_at IS NULL`. Unique constraints include deleted rows — add deleted_at to unique: `UNIQUE(email, deleted_at)`. OR use dedicated archive table: move deleted rows to `orders_archived`. PgSQL RLS can enforce soft delete transparently (policy `USING (deleted_at IS NULL)`).

**Q43. What is table partitioning and when to use it?**
A: Partitioning splits one logical table into multiple physical storage segments (partitions). Types: RANGE (by date range — orders_2024, orders_2023), LIST (by value — orders_us, orders_eu), HASH (by hash of column — even distribution). Benefits: query pruning (only scan relevant partition), faster deletes (DROP PARTITION vs DELETE millions), parallel I/O. Use when: table > 100M rows, most queries filter on the partition key (e.g., by date). Drawback: foreign keys not supported across partitions in MySQL. PgSQL declarative partitioning since PG10.

**Q44. How do you do zero-downtime schema migration?**
A: Expand/Contract pattern: (1) Add new column (nullable, no DEFAULT — fast). (2) Backfill data in batches: `UPDATE table SET new_col = X WHERE id BETWEEN ? AND ?` — 1000 rows at a time with sleep between batches. (3) Deploy app code to read new column (with fallback to old). (4) Add NOT NULL constraint after backfill. (5) Deploy app to write new column. (6) Drop old column after verifying. For index: PgSQL `CREATE INDEX CONCURRENTLY`. For MySQL: `ALTER TABLE` with `ALGORITHM=INPLACE, LOCK=NONE`. Never add a NOT NULL column without DEFAULT to a large table — it rewrites the whole table!

**Q45. What is the difference between replication and sharding?**
A: Replication: copies data across multiple servers — read replicas for scale reads, standby for HA/failover. Same data on all servers. Sharding: splits data across servers (horizontal partitioning) — each shard has a subset of rows. Used for write scale and very large datasets. Sharding tradeoffs: cross-shard queries become complex/expensive, resharding is painful. Choose replication first (read scaling is usually enough). Only shard when: write throughput exceeds what one server can handle + dataset too large for one server's storage.

---

## ⚫ PostgreSQL Specific (Q46-Q50)

**Q46. What is JSONB and how is it different from JSON in PostgreSQL?**
A: JSON stores data as text (preserves whitespace, key order). JSONB stores binary (parsed, indexable, faster queries). JSONB: supports operators `@>` (contains), `?` (key exists), `#>` (nested path), GIN indexes for fast lookup. Deduplicates keys (last wins), doesn't preserve whitespace or key order. Use JSONB for querying/indexing. JSON only when you need to preserve exact format. Index: `CREATE INDEX ON users USING GIN(data jsonb_path_ops)` — enables fast `@>` queries on any nested key.

**Q47. What is VACUUM in PostgreSQL and why is it needed?**
A: MVCC leaves old row versions ("dead tuples") in the heap after UPDATE/DELETE. VACUUM reclaims space from dead tuples, updates statistics, prevents transaction ID wraparound (32-bit counter). VACUUM (regular) — marks space as reusable, doesn't shrink file. VACUUM FULL — acquires exclusive lock, rewrites table, reclaims actual disk space. Autovacuum: background daemon runs VACUUM automatically. Monitor with `pg_stat_user_tables (n_dead_tup)`. Signs of bloat: large table size vs actual data, slow sequential scans. Tune autovacuum if write-heavy tables bloat.

**Q48. What is LISTEN/NOTIFY in PostgreSQL?**
A: A lightweight pub/sub mechanism within PostgreSQL. `NOTIFY channel_name, 'payload'` — sends a notification. `LISTEN channel_name` — a connection subscribes. Notifications are received asynchronously after COMMIT. Use case: database triggers notify Node.js app of changes — app reacts without polling. Example: `INSERT trigger → NOTIFY 'new_order', order_id` → Node.js `pg` client receives notification → pushes to WebSocket → real-time UI update. Much simpler than polling or external message queue for DB-driven events.

**Q49. What is Row-Level Security (RLS) in PostgreSQL?**
A: RLS applies policies to restrict which rows a user/role can see or modify. `ALTER TABLE orders ENABLE ROW LEVEL SECURITY` + `CREATE POLICY user_orders ON orders USING (user_id = current_user_id())`. Every query on that table automatically has the policy's condition appended. Use case: multi-tenant SaaS — each tenant can only see their own rows, even if app code forgets to filter. Set tenant ID: `SET app.tenant_id = 123` — policy references `current_setting('app.tenant_id')`. Bypassed by superusers/table owner unless `FORCE ROW LEVEL SECURITY` is set.

**Q50. What is the difference between MySQL and PostgreSQL you would mention for a 5+ YOE interview?**
A: Five key differences: (1) **Clustered index**: MySQL InnoDB PK is clustered (row data in leaf) — PK lookups are fastest; PgSQL heap tables (all indexes non-clustered). (2) **Transactional DDL**: PgSQL DDL is rollbackable (safe schema migrations in transactions); MySQL DDL auto-commits. (3) **JSONB**: PgSQL JSONB is indexed binary with rich operators; MySQL JSON is less capable for complex queries. (4) **VACUUM**: PgSQL needs periodic VACUUM due to MVCC dead tuples; MySQL's undo log is purged automatically. (5) **Features**: PgSQL has arrays, ranges, RLS, LISTEN/NOTIFY, lateral joins, custom types — MySQL is more focused/simpler. For new projects: PostgreSQL is more feature-rich. MySQL is better supported in some legacy ecosystems.
