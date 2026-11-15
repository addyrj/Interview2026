---

# Q152. EAV (Entity-Attribute-Value) — When and Pitfalls
# Category: Schema Design
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite

---

## ❓ Question
A catalog has phones, laptops and T-shirts, each with different attributes. Compare an EAV table with a JSON column: write "black products with RAM >= 8 GB", show the pivot query, and explain the pitfalls.

---

## 💡 Quick Concept (2 lines only)
EAV stores one row per (entity, attribute, value) so new attributes need no ALTER TABLE, but you lose types, constraints and simple queries (every filter is a self-join). Prefer a JSON/JSONB column for sparse attributes unless you need per-attribute metadata.
हिंदी: EAV = हर attribute एक row; schema flexible लेकिन type/constraint/query सब मुश्किल। आजकल JSON column बेहतर विकल्प है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE products_eav (id INT PRIMARY KEY, name VARCHAR(100) NOT NULL);
CREATE TABLE product_attributes (
  product_id INT NOT NULL,
  attr_name  VARCHAR(50) NOT NULL,
  attr_value VARCHAR(255),                 -- everything is text: the root of most pitfalls
  PRIMARY KEY (product_id, attr_name)
);
INSERT INTO products_eav VALUES (1,'Galaxy Phone'),(2,'Dell Laptop'),(3,'Cotton T-Shirt');
INSERT INTO product_attributes VALUES
  (1,'color','black'),(1,'ram_gb','8'),(1,'screen_in','6.1'),
  (2,'color','silver'),(2,'ram_gb','16'),(2,'screen_in','15.6'),
  (3,'color','black'),(3,'size','M');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: filter on 2 attributes = 2 self-joins (N filters = N joins)
SELECT p.id, p.name
FROM products_eav p
JOIN product_attributes a1 ON a1.product_id = p.id AND a1.attr_name = 'color'  AND a1.attr_value = 'black'
JOIN product_attributes a2 ON a2.product_id = p.id AND a2.attr_name = 'ram_gb'
                          AND CAST(a2.attr_value AS UNSIGNED) >= 8      -- PgSQL: AS INTEGER
ORDER BY p.id;
-- id | name
-- 1  | Galaxy Phone

-- Step 2: pivot back to a normal row shape (conditional aggregation)
SELECT p.id, p.name,
  MAX(CASE WHEN a.attr_name = 'color'  THEN a.attr_value END) AS color,
  MAX(CASE WHEN a.attr_name = 'ram_gb' THEN a.attr_value END) AS ram_gb,
  MAX(CASE WHEN a.attr_name = 'size'   THEN a.attr_value END) AS size
FROM products_eav p LEFT JOIN product_attributes a ON a.product_id = p.id
GROUP BY p.id, p.name ORDER BY p.id;
-- id | name           | color  | ram_gb | size
-- 1  | Galaxy Phone   | black  | 8      | NULL
-- 2  | Dell Laptop    | silver | 16     | NULL
-- 3  | Cotton T-Shirt | black  | NULL   | M

-- Step 3: pitfall — nothing stops garbage values
INSERT INTO product_attributes VALUES (3,'ram_gb','lots');

SELECT product_id FROM product_attributes
WHERE attr_name = 'ram_gb' AND CAST(attr_value AS UNSIGNED) >= 8;
-- MySQL : returns 1 and 2 (the 'lots' row is silently cast to 0, only a warning)
-- PgSQL : ERROR: invalid input syntax for type integer: "lots"   (whole query fails)

-- Step 4: same data as JSON — one row per product, one query
CREATE TABLE products_json (id INT PRIMARY KEY, name VARCHAR(100) NOT NULL, specs JSON NOT NULL);
INSERT INTO products_json VALUES
  (1,'Galaxy Phone','{"color":"black","ram_gb":8,"screen_in":6.1}'),
  (2,'Dell Laptop','{"color":"silver","ram_gb":16}'),
  (3,'Cotton T-Shirt','{"color":"black","size":"M"}');

SELECT id, name FROM products_json
WHERE specs->>'$.color' = 'black' AND CAST(specs->>'$.ram_gb' AS UNSIGNED) >= 8;
-- id | name
-- 1  | Galaxy Phone
-- PgSQL (JSONB): WHERE specs->>'color' = 'black' AND (specs->>'ram_gb')::int >= 8
```

---

## 🔍 Why This Works (3 lines max)
Each EAV filter needs its own join on the attribute table, so cost and SQL length grow with the number of conditions, and the text column cannot enforce numeric or enum types. A JSON column keeps attributes with the row, needs no joins, and can be indexed on specific paths.
हिंदी: EAV में हर filter = एक extra join और type safety नहीं; JSON में attributes उसी row में, join नहीं।

---

## ⚡ Alternative Solution

```sql
-- Better EAV if you must: typed value columns + FK to an attribute definition table
CREATE TABLE attribute_defs (attr_id INT PRIMARY KEY, attr_name VARCHAR(50) UNIQUE, data_type ENUM('int','decimal','text'));
CREATE TABLE product_attr_values (
  product_id INT, attr_id INT, int_val BIGINT NULL, dec_val DECIMAL(12,3) NULL, text_val VARCHAR(255) NULL,
  PRIMARY KEY (product_id, attr_id)
);   -- (not run; PgSQL: use a CHECK that exactly one *_val is not null)

-- PostgreSQL JSONB + GIN index (the usual modern answer; GIN index itself not run here)
CREATE INDEX idx_specs ON products_json USING GIN (specs);
SELECT id FROM products_json WHERE specs @> '{"color":"black"}';

-- MySQL: index a JSON path via a generated column (see Q168)
-- Hybrid: common attributes (price, brand, color) as real columns, long-tail attributes in JSON.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: modelling the whole app as EAV ("flexible schema")
--    -> no FKs, no NOT NULL, no CHECK, every report needs pivots, optimizer has no useful statistics
-- ❌ Wrong: comparing values as strings
SELECT * FROM product_attributes WHERE attr_name = 'ram_gb' AND attr_value >= '8';
-- '16' >= '8' is FALSE as text ('1' < '8')  -> the 16 GB laptop disappears
-- ✅ CAST to a number (and validate on write), or store typed columns / JSON numbers
```

---

## 🎯 Interview Tip (1 line)
Say: "EAV is an anti-pattern for core data, but acceptable for a small long-tail of user-defined fields; today I'd use real columns for known attributes plus JSONB with a GIN index (or a generated-column index in MySQL) for the flexible rest."

---

## 🔗 Related Questions
→ Q168 (MySQL JSON) | Q244 (JSON vs relational) | Q167 (ENUM) | Q159 (CHECK constraints)
