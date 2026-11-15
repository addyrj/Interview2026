---

# Q082. Clustered vs Non-Clustered Index (MySQL InnoDB)
# Category: Indexes
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL (InnoDB) with PostgreSQL contrast

---

## ❓ Question
In MySQL InnoDB, what is a clustered index and how does it differ from a secondary (non-clustered) index? Why does a lookup through a secondary index sometimes need a "double lookup", and how does that change PostgreSQL's design?

---

## 💡 Quick Concept (2 lines only)
InnoDB stores the table itself as a B+Tree ordered by the PRIMARY KEY (leaf = full row). Every secondary index leaf stores the indexed columns plus the PRIMARY KEY value, so a non-covering lookup = secondary tree, then PK tree.
हिंदी: InnoDB में table खुद PRIMARY KEY की B+Tree है; secondary index के leaf में PK value होती है, इसलिए दो बार lookup लगता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) - MySQL 8.0+
-- ============================================

SET SESSION cte_max_recursion_depth = 10000;   -- default 1000 is too low for 5000 rows

CREATE TABLE customers (
  customer_id BIGINT PRIMARY KEY,            -- CLUSTERED index (table is stored in this order)
  email       VARCHAR(100) NOT NULL,
  full_name   VARCHAR(100),
  city        VARCHAR(50),
  created_at  DATETIME,
  INDEX idx_email (email),                   -- secondary index: leaf = (email, customer_id)
  INDEX idx_city  (city)                     -- secondary index: leaf = (city,  customer_id)
) ENGINE=InnoDB;

INSERT INTO customers
SELECT n, CONCAT('user', n, '@example.com'), CONCAT('Customer ', n),
       ELT(1 + n % 4, 'Delhi', 'Pune', 'Mumbai', 'Jaipur'), NOW()
FROM (WITH RECURSIVE s AS (SELECT 1 AS n UNION ALL SELECT n + 1 FROM s WHERE n < 5000)
      SELECT n FROM s) x;

ANALYZE TABLE customers;

-- ============================================
-- SOLUTION: see which tree each query walks
-- ============================================

-- 1) PK lookup: one B+Tree descent, leaf already contains the whole row
EXPLAIN SELECT * FROM customers WHERE customer_id = 42;

-- 2) Secondary lookup with SELECT *: idx_email -> get customer_id -> PK tree -> row
EXPLAIN SELECT * FROM customers WHERE email = 'user42@example.com';

-- 3) Secondary lookup selecting only (email, PK): covered, never touches the PK tree
EXPLAIN SELECT customer_id, email FROM customers WHERE email = 'user42@example.com';

-- 4) PK is "free" in every secondary index, so this is covered too
EXPLAIN SELECT customer_id FROM customers WHERE city = 'Pune';

-- ============================================
-- EXPECTED OUTPUT (verified on MySQL 9.1; key columns of EXPLAIN)
-- ============================================

-- Query | type  | key       | key_len | rows | Extra
-- 1     | const | PRIMARY   | 8       | 1    | NULL
-- 2     | ref   | idx_email | 402     | 1    | NULL          <- must go back to clustered index
-- 3     | ref   | idx_email | 402     | 1    | Using index   <- covering, no PK lookup
-- 4     | ref   | idx_city  | 203     | 1250 | Using index   <- PK implicitly stored in idx_city

-- key_len 402 = 100 chars * 4 bytes (utf8mb4) + 2 length bytes.
-- Index pages (MySQL 9.1, 5000 rows; numbers will vary by version/settings):
--   PRIMARY  size 26 pages (25 leaf)   <- the whole table lives here
--   idx_email size 17 pages
--   idx_city  size 10 pages
-- Rows (n_leaf_pages) come from: SELECT index_name, stat_name, stat_value
--   FROM mysql.innodb_index_stats WHERE table_name = 'customers';
```

---

## 🔍 Why This Works (3 lines max)
The clustered index IS the table, so PK lookups and PK range scans are the cheapest reads. Secondary indexes point to the row via the PK value (not a physical address), so a wide or random PK (UUID v4) bloats every secondary index and causes page splits.
हिंदी: Clustered index = table खुद; secondary index PK value से row ढूंढता है, इसलिए बड़ी या random PK सारे indexes को भारी कर देती है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL contrast: tables are HEAPS; every index (including PK) is "secondary"
-- and points to a physical tuple id (ctid = page, offset). Verified on PGlite:
CREATE TABLE customers (customer_id BIGINT PRIMARY KEY, email VARCHAR(100) NOT NULL, city VARCHAR(50));
INSERT INTO customers SELECT n, 'user'||n||'@example.com',
       (ARRAY['Delhi','Pune','Mumbai','Jaipur'])[1 + n % 4] FROM generate_series(1, 5000) n;

SELECT ctid, customer_id FROM customers WHERE customer_id IN (1, 2, 3);
-- (0,1) | 1     (0,2) | 2     (0,3) | 3     <- insertion order, page 0

CREATE INDEX idx_city ON customers(city);
CLUSTER customers USING idx_city;     -- ONE-TIME physical reorder; NOT maintained on later writes
SELECT ctid, customer_id, city FROM customers WHERE customer_id IN (1, 2, 3, 4, 5);
-- (31,31) | 1 | Pune     (20,101) | 2 | Mumbai     (10,51) | 3 | Jaipur ...  <- rows physically moved

-- Consequences:
--  * PgSQL secondary indexes don't contain the PK, so a PK change doesn't rewrite them,
--    but UPDATEs create new tuples (HOT updates help) and need VACUUM.
--  * InnoDB with no PRIMARY KEY uses the first NOT NULL UNIQUE index, else a hidden 6-byte DB_ROW_ID.
--    Always define an explicit, short, monotonic PK (BIGINT AUTO_INCREMENT).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: random UUID (CHAR(36)) as InnoDB PK
CREATE TABLE orders (id CHAR(36) PRIMARY KEY, user_id INT, INDEX (user_id));
-- Each secondary index entry carries a 36-byte (144 bytes in utf8mb4) PK copy, and random
-- inserts split pages all over the clustered tree.
-- ✅ Use BIGINT AUTO_INCREMENT, or UUID_TO_BIN(UUID(), 1) (time-ordered, 16 bytes) / UUIDv7.

-- ❌ Wrong: assuming "SELECT *" via a secondary index is as cheap as the PK lookup
-- ✅ It costs an extra random PK-tree lookup per row; select only needed columns to get "Using index".
```

---

## 🎯 Interview Tip (1 line)
Say: "InnoDB's table is the PK B+Tree and secondary indexes store the PK, so I keep PKs short and monotonic, design covering indexes to skip the bookmark lookup, and I know PostgreSQL is heap-based with ctid pointers, which is why it needs VACUUM and has no true clustered index."

---

## 🔗 Related Questions
→ Q081 (B-Tree index internals) | Q084 (Covering index) | Q086 (EXPLAIN output) | Q093 (Index bloat in PgSQL - VACUUM)
