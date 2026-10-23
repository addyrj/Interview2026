# MySQL vs PostgreSQL — Side-by-Side Cheatsheet
# 5+ YOE Interview — Know the Differences Cold

---

## 🔴 Top 5 Differences (Interview Answer)

```
1. MVCC Implementation:
   MySQL InnoDB → undo log in same tablespace (blocks VACUUM)
   PostgreSQL   → dead tuples remain, needs VACUUM to reclaim

2. Clustered Index:
   MySQL InnoDB → PRIMARY KEY IS the clustered index (row data in leaf)
   PostgreSQL   → All indexes are non-clustered (heap table separate)

3. Transactional DDL:
   MySQL        → DDL (ALTER, TRUNCATE, DROP) auto-commits! Can't rollback.
   PostgreSQL   → All DDL is transactional — rollback works on ALTER TABLE!

4. JSON Support:
   MySQL        → JSON type (stored as text, validated on insert)
   PostgreSQL   → JSONB (binary, indexed, operators @>, ?, #>)

5. Replication:
   MySQL        → Statement-based or row-based binary log replication
   PostgreSQL   → WAL streaming replication (physical) + logical replication
```

---

## 📊 Syntax Differences Table

```
Feature                     | MySQL                      | PostgreSQL
────────────────────────────┼────────────────────────────┼────────────────────────────
Auto increment PK           | AUTO_INCREMENT              | SERIAL or GENERATED ALWAYS AS IDENTITY
Get last inserted ID        | LAST_INSERT_ID()            | RETURNING id (preferred) / lastval()
String concat               | CONCAT(a, b) or a, b       | a || b  or  CONCAT(a, b)
Current timestamp           | NOW()                      | NOW() or CURRENT_TIMESTAMP
Limit + offset              | LIMIT 10 OFFSET 20         | LIMIT 10 OFFSET 20 (same)
Random                      | RAND()                     | RANDOM()
String length               | LENGTH() or CHAR_LENGTH()  | LENGTH() (bytes) / CHAR_LENGTH()
Regex match                 | col REGEXP 'pattern'       | col ~ 'pattern'  (case-sensitive)
                            |                            | col ~* 'pattern' (case-insensitive)
Case-insensitive LIKE       | LIKE (case-insensitive by  | ILIKE  (explicit case-insensitive)
                            | default for utf8_general)  |
Upsert                      | ON DUPLICATE KEY UPDATE    | ON CONFLICT (column) DO UPDATE
String to date              | STR_TO_DATE(str, fmt)      | TO_DATE(str, fmt)
Date format                 | DATE_FORMAT(date, fmt)     | TO_CHAR(date, fmt)
Interval                    | DATE_ADD(date, INTERVAL N) | date + INTERVAL 'N days'
Update with join            | UPDATE a JOIN b ON ... SET | UPDATE a SET ... FROM b WHERE ...
Delete with join            | DELETE a FROM a JOIN b     | DELETE FROM a USING b WHERE ...
Returning deleted rows      | ❌ (not supported)         | DELETE ... RETURNING *
IF function                 | IF(condition, true, false) | CASE WHEN cond THEN ... ELSE ... END
                            |                            | (or: (condition)::int trick)
Boolean type                | TINYINT(1) or bool alias   | BOOLEAN (true/false)
Array type                  | ❌ (use JSON or separate   | ARRAY type + operators
                            | table)                     | e.g., arr && ARRAY[1,2,3]
UUID generation             | UUID()                     | gen_random_uuid() (pg 13+)
                            |                            | uuid_generate_v4() (uuid-ossp ext)
Full-text search            | MATCH() AGAINST()          | to_tsvector() @@ to_tsquery()
Explain format              | EXPLAIN SELECT ...         | EXPLAIN ANALYZE SELECT ...
                            | (estimates only)           | (actual execution stats)
Schema/database             | Database ≈ Schema          | Database > Schema > Table
                            | USE dbname                 | SET search_path TO schema
```

---

## 🟠 Data Types Comparison

```
Purpose           | MySQL                  | PostgreSQL
──────────────────┼────────────────────────┼──────────────────────────
Integer           | INT (4B), BIGINT (8B)  | INTEGER (4B), BIGINT (8B)
Auto-increment    | AUTO_INCREMENT         | SERIAL / BIGSERIAL / IDENTITY
Decimal (money)   | DECIMAL(10,2)          | NUMERIC(10,2) or DECIMAL(10,2)
Floating point    | FLOAT, DOUBLE          | REAL (4B), DOUBLE PRECISION (8B)
Fixed string      | CHAR(n)                | CHAR(n) (pads with spaces)
Variable string   | VARCHAR(n)             | VARCHAR(n) or TEXT (no perf diff!)
Unlimited text    | TEXT (65KB)            | TEXT (no size limit)
                  | LONGTEXT (4GB)         |
Binary data       | BLOB / LONGBLOB        | BYTEA
Boolean           | TINYINT(1) / BOOL      | BOOLEAN (true/false/null)
Date only         | DATE                   | DATE
Time only         | TIME                   | TIME
Date + time       | DATETIME (no TZ)       | TIMESTAMP (no TZ)
Date + time + TZ  | TIMESTAMP (server TZ)  | TIMESTAMPTZ / TIMESTAMP WITH TIME ZONE
JSON              | JSON (text storage)    | JSON (text) / JSONB (binary, indexed)
Array             | ❌ Not native          | ARRAY (int[], text[], etc.)
UUID              | VARCHAR(36) or BINARY  | UUID (native type)
IP address        | VARCHAR(45)            | INET / CIDR (native, indexable)
Enum              | ENUM('a','b','c')      | Custom TYPE or CHECK constraint
Range types       | ❌ Not native          | int4range, daterange, tsrange
```

---

## 🟡 Index Differences

```
Index Type    | MySQL                          | PostgreSQL
──────────────┼────────────────────────────────┼────────────────────────────────
B-Tree        | Default for most              | Default
Hash          | InnoDB: on-disk hash (limited)| In-memory hash (very fast equality)
Full-text     | FULLTEXT index + MATCH AGAINST| GIN with tsvector + tsquery
Composite     | Same syntax                   | Same syntax
Partial index | ❌ Not supported              | CREATE INDEX ... WHERE condition
Functional    | CREATE INDEX ... ((EXPR))     | CREATE INDEX ... (EXPR) — no double ()
              | MySQL 8.0+                    |
JSONB / JSON  | JSON column + generated col   | GIN index on JSONB column
              | as workaround                 | idx ON tbl USING GIN(jsonb_col)
Covering      | INCLUDE not available         | CREATE INDEX ... INCLUDE (extra_cols) PG11+
              | (use composite workaround)    |
Invisible     | MySQL 8+: ALTER TABLE ...     | ❌ Not native (use pg_visibility)
              | ALTER INDEX ... INVISIBLE     |
Concurrent    | ❌ (ADD INDEX locks table     | CREATE INDEX CONCURRENTLY
index build   | in older MySQL, reduced       | (no table lock!)
              | in MySQL 8.0 with online DDL) |
```

---

## 🟢 Transactions & Locking

```
Feature                | MySQL InnoDB              | PostgreSQL
───────────────────────┼───────────────────────────┼──────────────────────────────
Default isolation      | REPEATABLE READ           | READ COMMITTED
Gap locks              | Yes (prevents phantom)    | No gap locks (MVCC handles it)
Next-key locks         | Yes                       | No (predicate locks in SERIALIZABLE)
FOR UPDATE             | ROW lock + gap lock       | ROW lock only
FOR SHARE              | LOCK IN SHARE MODE or     | FOR SHARE
                       | FOR SHARE                 |
SKIP LOCKED            | MySQL 8.0+                | Yes (older support)
Advisory locks         | GET_LOCK('name', timeout) | pg_try_advisory_lock(key)
Deadlock victim        | Transaction with least    | More recent of the two
                       | undo records              |
DDL transactional?     | NO (auto-commit)          | YES (rollbackable!)
TRUNCATE rollback      | NO                        | YES (within transaction)
MVCC                   | Undo log in undo          | Dead tuples in heap
                       | tablespace (purged auto)  | (need VACUUM to reclaim)
```

---

## 🔵 PostgreSQL-Only Features (Differentiators)

```sql
-- 1. JSONB with GIN index:
SELECT data->>'name' FROM users WHERE data @> '{"role": "admin"}';
-- @> = contains operator (indexed via GIN!)

-- 2. LISTEN/NOTIFY (real-time events):
LISTEN channel_name;          -- subscriber
NOTIFY channel_name, 'msg';   -- publisher (any connection)
-- Use case: real-time notifications without polling

-- 3. Array type:
SELECT * FROM posts WHERE 1 = ANY(tag_ids);
SELECT * FROM posts WHERE tag_ids && ARRAY[1, 2, 3];  -- overlap

-- 4. Full-text search built-in:
SELECT * FROM articles
WHERE to_tsvector('english', content) @@ to_tsquery('english', 'PostgreSQL & performance');

-- 5. Materialized Views:
CREATE MATERIALIZED VIEW sales_summary AS
  SELECT date, SUM(amount) FROM orders GROUP BY date;
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_summary;

-- 6. Row-Level Security:
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_orders ON orders
  USING (user_id = current_setting('app.current_user_id')::int);

-- 7. LATERAL JOIN:
SELECT u.name, recent_order.amount
FROM users u
JOIN LATERAL (
  SELECT amount FROM orders WHERE user_id = u.id
  ORDER BY created_at DESC LIMIT 1
) AS recent_order ON true;
-- LATERAL can reference the outer row (u.id) — regular JOIN can't!

-- 8. Table partitioning (declarative, PG10+):
CREATE TABLE orders (id INT, created_at DATE, amount DECIMAL)
PARTITION BY RANGE (created_at);
CREATE TABLE orders_2024 PARTITION OF orders
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- 9. pg_stat_statements (query performance tracking):
SELECT query, calls, mean_exec_time FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 10;
-- Shows top slow queries with execution stats!

-- 10. CTE with RETURNING (powerful pattern):
WITH deleted AS (
  DELETE FROM sessions WHERE expired_at < NOW()
  RETURNING user_id
)
INSERT INTO audit_log (user_id, event, ts)
SELECT user_id, 'session_expired', NOW() FROM deleted;
```

---

## 🔴 MySQL-Only Features

```sql
-- 1. ON DUPLICATE KEY UPDATE (upsert):
INSERT INTO page_views (url, views)
VALUES ('/home', 1)
ON DUPLICATE KEY UPDATE views = views + 1;

-- PgSQL equivalent:
INSERT INTO page_views (url, views) VALUES ('/home', 1)
ON CONFLICT (url) DO UPDATE SET views = page_views.views + 1;

-- 2. REPLACE INTO (delete + insert):
REPLACE INTO settings (key, value) VALUES ('theme', 'dark');
-- Deletes existing row with same PK, inserts new one
-- Warning: triggers DELETE then INSERT, not UPDATE

-- 3. AUTO_INCREMENT behavior:
-- MySQL guarantees AUTO_INCREMENT on PK → clustered physical order
-- Gaps in AUTO_INCREMENT after rollback or DELETE are normal and fine

-- 4. SHOW ENGINE INNODB STATUS:
SHOW ENGINE INNODB STATUS\G
-- Shows: buffer pool stats, deadlocks, row operations, I/O

-- 5. MySQL EXPLAIN key columns:
-- type:     ALL (bad) | range | ref | eq_ref | const (good→best)
-- key:      which index used (NULL = no index)
-- rows:     estimated rows examined
-- filtered: % rows after WHERE (100 = all, 10 = filtered to 10%)
-- Extra:    Using index (covering!) | Using filesort (bad!) | Using temporary (bad!)

-- 6. InnoDB buffer pool:
-- innodb_buffer_pool_size = 70-80% of available RAM
-- Hot data stays in memory → queries served from RAM not disk

-- 7. MySQL GROUP BY mode (important gotcha!):
-- ONLY_FULL_GROUP_BY mode (default MySQL 5.7+):
-- SELECT id, name, MAX(salary) FROM emp GROUP BY dept_id;  ← ERROR!
-- id and name are not in GROUP BY and not aggregated!
-- PgSQL enforces this strictly always (not mode-dependent)
```

---

## ⚡ Quick Decision Guide

```
Choose MySQL when:
  ✅ Existing MySQL infrastructure/team expertise
  ✅ Need MySQL-specific tools (Percona, Vitess, ProxySQL)
  ✅ WordPress/PHP ecosystem (MySQL is default)
  ✅ Simple read-heavy CRUD applications
  ✅ Need Galera Cluster for multi-master

Choose PostgreSQL when:
  ✅ Complex queries (window functions, CTEs, LATERAL)
  ✅ JSONB document storage with indexing
  ✅ Full-text search without external service
  ✅ Advanced data types (arrays, ranges, custom types)
  ✅ Transactional DDL (safe schema migrations!)
  ✅ Row-level security
  ✅ LISTEN/NOTIFY for real-time features
  ✅ Better standards compliance (SQL-92+)
  ✅ PostGIS for geospatial data
  ✅ TimescaleDB for time-series (PgSQL extension)

For new projects (2024): PostgreSQL is generally recommended
For migration: both can be run side by side; Pgloader for MySQL→PgSQL migration
```
