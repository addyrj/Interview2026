---

# Q238. Difference Between MySQL and PostgreSQL (Top 5)
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: Both

---

## ❓ Question
List the top 5 practical differences between MySQL (InnoDB) and PostgreSQL, and prove the ones you can with a small runnable demo.

---

## 💡 Quick Concept (2 lines only)
MySQL: clustered-PK InnoDB, simple, fast reads, huge ecosystem. PostgreSQL: heap + MVCC with VACUUM, stricter SQL, richer types/indexes/extensions, transactional DDL.
हिंदी: MySQL सरल और तेज़ read-heavy workloads के लिए; PostgreSQL ज़्यादा features और strict SQL के लिए।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- THE TOP 5 (interview answer)
-- ============================================
-- 1. Storage + MVCC: InnoDB clustered PK, undo log for old versions (no VACUUM).
--    PostgreSQL heap tables, old row versions stay in the table until VACUUM; PK lookup = index + heap.
-- 2. Transactional DDL: PostgreSQL can ROLLBACK CREATE/ALTER TABLE. MySQL DDL implicitly commits.
-- 3. SQL features: PG has RETURNING, DISTINCT ON, FILTER, partial/expression indexes, arrays, jsonb+GIN,
--    ILIKE, range types, many extensions (PostGIS, pg_trgm). MySQL 8 has CTEs/windows/JSON but fewer index kinds.
-- 4. Strictness/semantics: PG integer division, case-sensitive LIKE, "double quotes" = identifiers.
--    MySQL 7/2 = 3.5, LIKE case-insensitive by collation, "double quotes" = string literals by default.
-- 5. Replication/ops: MySQL = binlog replication, mature (Group Replication, Vitess).
--    PG = WAL streaming/logical replication, needs autovacuum tuning and connection pooling (PgBouncer).

-- ============================================
-- SETUP (run in both; only the AUTO id keyword differs)
-- ============================================
-- MySQL:
CREATE TABLE customers (id INT PRIMARY KEY AUTO_INCREMENT, email VARCHAR(100), city VARCHAR(50));
-- PostgreSQL:
-- CREATE TABLE customers (id SERIAL PRIMARY KEY, email VARCHAR(100), city VARCHAR(50));

INSERT INTO customers (email, city) VALUES ('Asha@Example.com', 'Pune'), ('ravi@example.com', 'Delhi');

-- ============================================
-- DEMO 1: transactional DDL
-- ============================================
START TRANSACTION;   -- PostgreSQL: BEGIN;
CREATE TABLE audit_tmp (id INT);
ROLLBACK;

-- MySQL:      SHOW TABLES LIKE 'audit_tmp';  -> audit_tmp  (STILL EXISTS: DDL auto-committed)
-- PostgreSQL: SELECT to_regclass('audit_tmp'); -> NULL      (rolled back cleanly)

-- ============================================
-- DEMO 2: case sensitivity of LIKE
-- ============================================
SELECT id FROM customers WHERE email LIKE 'asha%';
-- MySQL:      1   (case-insensitive collation)
-- PostgreSQL: no rows; use ILIKE 'asha%' -> 1

-- ============================================
-- DEMO 3: integer division
-- ============================================
SELECT 7 / 2 AS div_result;
-- MySQL:      3.5000     (use 7 DIV 2 for 3)
-- PostgreSQL: 3          (use 7 / 2.0 for 3.5000000000000000)

-- ============================================
-- DEMO 4: RETURNING and DISTINCT ON
-- ============================================
-- PostgreSQL:
INSERT INTO customers (email, city) VALUES ('new@example.com', 'Goa') RETURNING id;   -- 3
SELECT DISTINCT ON (city) city, email FROM customers ORDER BY city;
-- city  | email
-- Delhi | ravi@example.com
-- Goa   | new@example.com
-- Pune  | Asha@Example.com

-- MySQL: both are syntax errors (ERROR 1064 near 'RETURNING id' / near 'ON (city)').
INSERT INTO customers (email, city) VALUES ('new@example.com', 'Goa');
SELECT LAST_INSERT_ID() AS new_id;   -- 3

-- ============================================
-- DEMO 5: identifier quoting
-- ============================================
SELECT `email` FROM customers WHERE city = 'Pune';   -- MySQL OK; PostgreSQL: syntax error at backtick
SELECT "email" FROM customers WHERE city = 'Pune';
-- PostgreSQL: Asha@Example.com
-- MySQL:      returns the literal string 'email' (not the column!) unless sql_mode has ANSI_QUOTES

-- Verified: MySQL 9.1.0 (real server) and PostgreSQL via PGlite. Outputs above are the observed ones.
```

---

## 🔍 Why This Works (3 lines max)
The demos expose the root causes: PostgreSQL's catalog changes are transactional and its parser follows the SQL standard more strictly, while MySQL favours convenience (implicit commits, case-insensitive collations, decimal division). Storage design (clustered PK vs heap + VACUUM) drives most performance and ops differences.
हिंदी: MySQL = सुविधा और speed, PostgreSQL = standard SQL, transactional DDL और ज़्यादा features।

---

## ⚡ Alternative Solution

```sql
-- Make behaviours match when migrating:
-- MySQL -> PG: replace backticks, AUTO_INCREMENT -> GENERATED ... AS IDENTITY, DATETIME -> TIMESTAMP,
--              IFNULL -> COALESCE, LIMIT a,b -> LIMIT b OFFSET a, TINYINT(1) -> BOOLEAN.
-- PG -> MySQL: ILIKE -> LIKE (ci collation) or LOWER(col) LIKE, RETURNING -> LAST_INSERT_ID(),
--              DISTINCT ON -> ROW_NUMBER() subquery, jsonb -> JSON (no GIN), arrays -> child table.
SET sql_mode = CONCAT(@@sql_mode, ',ANSI_QUOTES');   -- MySQL: make "x" an identifier like PG
```

---

## ⚠️ Common Mistake

```sql
-- ❌ "PostgreSQL is always slower/faster" -> depends on workload
-- ❌ Assuming MySQL DDL can be rolled back inside a migration transaction (it cannot -> half-applied schema)
-- ❌ Porting 'LIKE' search from MySQL and getting zero rows on PostgreSQL
-- ✅ Test migrations on a copy, use ILIKE / citext, and design DDL migrations to be idempotent on MySQL
```

---

## 🎯 Interview Tip (1 line)
Say: "I pick by workload: MySQL for simple, read-heavy OLTP with a mature replication/sharding ecosystem; PostgreSQL when I need transactional DDL, strong constraints, jsonb/GIN, extensions, complex analytics. Both are ACID with MVCC, the difference is storage (undo log vs heap+VACUUM) and feature depth."

---

## 🔗 Related Questions
→ Q221 (DELETE vs TRUNCATE vs DROP) | Q225 (ACID real examples) | Q243 (Materialized view) | Q244 (JSON vs relational)
