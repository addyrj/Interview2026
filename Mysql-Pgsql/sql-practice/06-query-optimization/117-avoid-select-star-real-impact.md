---

# Q117. Avoid SELECT * — Real Impact
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: Both

---

## ❓ Question
Everyone says "never use SELECT *". Prove why: show how it changes the execution plan (covering index vs table lookups), row width, network payload and resilience to schema changes on a `products` table with a large `description` column.

---

## 💡 Quick Concept (2 lines only)
`SELECT *` forces the engine to fetch every column from the table heap/clustered index, so a covering index (index-only scan) cannot be used, and wide TEXT/BLOB columns get read, sent and parsed for nothing. Naming columns lets the index answer the query alone.
हिंदी: `SELECT *` से हर column table से पढ़ना पड़ता है, covering index बेकार हो जाता है और बड़े TEXT columns network पर बेवजह जाते हैं।

---

## ✅ Answer / Solution

```sql
-- Verified: PostgreSQL on PGlite 18.6 and MySQL 9.1.0 (20,000 rows, EXPLAIN only; timings vary).

-- ============================================
-- SETUP (PostgreSQL)
-- ============================================

CREATE TABLE products (
  id          SERIAL PRIMARY KEY,
  sku         VARCHAR(20),
  name        VARCHAR(100),
  category_id INT,
  price       NUMERIC(10,2),
  description TEXT                      -- ~1.7 KB per row
);

INSERT INTO products (sku, name, category_id, price, description)
SELECT 'SKU' || g, 'Product ' || g, g % 50, (g % 1000) + 0.99, repeat('long description ', 100)
FROM generate_series(1, 20000) g;

CREATE INDEX idx_products_cat_price ON products (category_id, price);
VACUUM ANALYZE products;                -- needed for index-only scans (visibility map)

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: SELECT * -> must visit the table for every matching row
EXPLAIN SELECT * FROM products WHERE category_id = 7 AND price < 100;

-- Step 2: only needed columns -> answered from the index alone
EXPLAIN SELECT category_id, price FROM products WHERE category_id = 7 AND price < 100;

-- Step 3: measure row width and table size
SELECT pg_size_pretty(pg_relation_size('products')) AS heap_size,
       avg(pg_column_size(p.*))::int AS avg_row_bytes_star,
       avg(pg_column_size(p.id) + pg_column_size(p.name) + pg_column_size(p.price))::int AS avg_bytes_3cols
FROM products p;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Step 1 (PostgreSQL, real):
-- Bitmap Heap Scan on products  (cost=4.70..154.56 rows=40 width=1739)
--   ->  Bitmap Index Scan on idx_products_cat_price  (cost=0.00..4.69 rows=40 width=0)
-- Step 2 (PostgreSQL, real):
-- Index Only Scan using idx_products_cat_price on products  (cost=0.29..5.09 rows=40 width=10)
--
-- heap_size 39 MB | avg_row_bytes_star 1768 | avg_bytes_3cols 24
-- width: 1739 bytes/row vs 10 bytes/row; cost 154.56 vs 5.09
--
-- MySQL 9.1.0 EXPLAIN (real), index idx_cat_price(category_id, price):
-- SELECT *                          -> type=range key=idx_cat_price rows=40 Extra: Using index condition
-- SELECT category_id, price         -> type=range key=idx_cat_price rows=40 Extra: Using where; Using index   (covering)
-- SELECT id, category_id, price     -> same, Using index (InnoDB secondary indexes include the PK)
```

---

## 🔍 Why This Works (3 lines max)
Both plans use the same index to find the 40 rows, but only the narrow query avoids the extra random lookup into the 39 MB table for each row. Fewer bytes also means smaller sort/hash memory, less network traffic and fewer cache evictions.
हिंदी: दोनों query index से 40 rows ढूँढती हैं, पर narrow query को table में वापस जाना नहीं पड़ता; इसलिए I/O और network दोनों बचते हैं।

---

## ⚡ Alternative Solution

```sql
-- Extra safety: schema evolution
-- ALTER TABLE products ADD COLUMN internal_notes TEXT;   -- SELECT * now leaks/transfers it
-- Also breaks code that relies on column ORDER, and INSERT INTO t SELECT * FROM s.

-- PostgreSQL: INCLUDE columns make an index "wide enough" without bloating the key
CREATE INDEX idx_products_cat_incl ON products (category_id) INCLUDE (name, price);

-- MySQL: no INCLUDE; add trailing columns to the composite index instead
-- ALTER TABLE products ADD INDEX idx_cat_price_name (category_id, price, name);

-- Fine uses of *:
SELECT count(*) FROM products;                 -- count(*) is not "SELECT *"
SELECT EXISTS (SELECT * FROM products WHERE id = 1);   -- optimizer ignores the select list in EXISTS
-- Ad-hoc exploration in psql/mysql: fine. In application code and views: avoid.
```

---

## ⚠️ Common Mistake
```sql
-- ❌ ORM default loads every column, including TEXT/JSON blobs, for list pages
SELECT * FROM products WHERE category_id = 7;
-- ❌ CREATE VIEW v AS SELECT * FROM products;   -- PgSQL expands * at creation time: new columns
--    do NOT appear later, and dropping a column can fail with dependency errors.
-- ❌ Believing index-only scan always works: in PostgreSQL it needs a recently VACUUMed table
--    (visibility map), otherwise it still visits the heap ("Heap Fetches: N").
-- ✅ SELECT id, name, price FROM products WHERE category_id = 7;   -- list columns explicitly
-- ✅ Move huge columns to a side table or fetch them only on the detail page.
```

---

## 🎯 Interview Tip (1 line)
Say: "SELECT * costs me three ways: it defeats covering/index-only scans, it ships large columns over the wire and through the app's memory, and it silently changes behaviour when the schema changes - I project explicit columns and design indexes to cover the hot read paths."

---

## 🔗 Related Questions
→ Q109 (Slow query diagnosis) | Q118 (OR vs UNION) | Q119 (Function on indexed column) | Q108 (N+1 problem)
