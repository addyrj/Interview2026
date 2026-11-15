---

# Q244. JSON vs Relational — When to Choose
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ JSON | PostgreSQL jsonb)

---

## ❓ Question
When should you store data in a JSON column versus normal relational columns? Show querying, indexing and updating JSON on both databases, and what you lose.

---

## 💡 Quick Concept (2 lines only)
Use relational columns for core, queried, constrained data (keys, money, status, joins); use JSON for sparse, flexible or rarely-filtered attributes that vary per row (product specs, settings, API payloads). JSON trades schema enforcement, joins and statistics for flexibility.
हिंदी: Core और बार-बार query होने वाला data columns में, बदलते या optional attributes JSON में।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL 8.0+ (PostgreSQL: SERIAL, NUMERIC, JSONB; see Alternative)
-- ============================================

CREATE TABLE products (
  id    INT PRIMARY KEY AUTO_INCREMENT,
  name  VARCHAR(100) NOT NULL,          -- core, always present, relational
  price DECIMAL(10,2) NOT NULL,
  attrs JSON                            -- flexible, differs per product type
);

INSERT INTO products (name, price, attrs) VALUES
  ('Phone X',    29999, '{"brand":"Acme","ram_gb":8,"colors":["black","blue"]}'),
  ('Laptop Pro', 79999, '{"brand":"Zen","ram_gb":16,"gpu":"RTX","colors":["silver"]}'),
  ('T-Shirt',      499, '{"size":"M","fabric":"cotton","colors":["red","blue"]}');

-- ============================================
-- SOLUTION (MySQL)
-- ============================================

-- Step 1: extract values (->> returns unquoted text; missing key = NULL)
SELECT name, attrs->>'$.brand' AS brand, attrs->>'$.ram_gb' AS ram FROM products ORDER BY id;
-- name       | brand | ram
-- Phone X    | Acme  | 8
-- Laptop Pro | Zen   | 16
-- T-Shirt    | NULL  | NULL

-- Step 2: filter
SELECT name FROM products WHERE JSON_EXTRACT(attrs, '$.ram_gb') >= 16;     -- Laptop Pro
SELECT name FROM products WHERE JSON_CONTAINS(attrs->'$.colors', '"blue"'); -- Phone X, T-Shirt

-- Step 3: JSON cannot be indexed directly -> index a generated column
ALTER TABLE products
  ADD COLUMN brand VARCHAR(50) GENERATED ALWAYS AS (attrs->>'$.brand') STORED,
  ADD INDEX idx_brand (brand);

EXPLAIN SELECT name FROM products WHERE brand = 'Zen';
-- type: ref | key: idx_brand | rows: 1

-- Step 4: partial update
UPDATE products SET attrs = JSON_SET(attrs, '$.ram_gb', 12) WHERE name = 'Phone X';
-- {"brand": "Acme", "colors": ["black", "blue"], "ram_gb": 12}   (MySQL normalises key order)

-- Step 5: validity is checked, shape is not
INSERT INTO products (name, price, attrs) VALUES ('Broken', 1, '{"brand":');
-- ERROR 3140 (22032): Invalid JSON text: "Invalid value." at position 9 in value for column 'products.attrs'.

-- ============================================
-- SOLUTION (PostgreSQL jsonb) — ran on PGlite
-- ============================================
-- CREATE TABLE products (id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL,
--                        price NUMERIC(10,2) NOT NULL, attrs JSONB);   -- same 3 INSERT rows

SELECT name, attrs->>'brand' AS brand, attrs->>'ram_gb' AS ram FROM products ORDER BY id;   -- same result as MySQL
SELECT name FROM products WHERE (attrs->>'ram_gb')::int >= 16;     -- Laptop Pro (cast needed: ->> is text)
SELECT name FROM products WHERE attrs->'colors' ? 'blue';          -- Phone X, T-Shirt
SELECT name FROM products WHERE attrs @> '{"brand":"Zen"}';        -- Laptop Pro (containment)

CREATE INDEX idx_products_attrs ON products USING GIN (attrs);          -- indexes ALL keys/values
CREATE INDEX idx_products_brand ON products ((attrs->>'brand'));        -- expression index for one key

-- Plans (enable_seqscan=off, tiny table, to show index eligibility):
-- @> query:        Bitmap Heap Scan -> Bitmap Index Scan on idx_products_attrs
-- ->> = 'Zen':     Index Scan using idx_products_brand

UPDATE products SET attrs = jsonb_set(attrs, '{ram_gb}', '12') WHERE name = 'Phone X';
-- {"brand":"Acme","colors":["black","blue"],"ram_gb":12}

INSERT INTO products (name, price, attrs) VALUES ('Broken', 1, '{"brand":');
-- ERROR: invalid input syntax for type json
```

---

## 🔍 Why This Works (3 lines max)
Relational columns give types, constraints, foreign keys, statistics and cheap joins; JSON gives schema flexibility with path functions and (generated-column or GIN) indexes. Index only the JSON keys you filter on, otherwise every query is a full scan that parses documents.
हिंदी: Columns = constraints, joins, indexes आसान; JSON = flexible schema, पर filter के लिए index खुद बनाना पड़ता है।

---

## ⚡ Alternative Solution

```sql
-- Hybrid (best in practice): promote hot keys to real columns, keep the long tail in JSON.
-- ✅ Relational wins when: you JOIN/aggregate on the field, need FK/CHECK/NOT NULL, field is in most queries.
-- ✅ JSON wins when: attributes vary per row (EAV replacement), payloads stored as-is (webhooks, audit),
--                    config/preferences, rapid prototyping.
-- Differences:
-- * PostgreSQL jsonb: binary, GIN indexes, @> ? operators, jsonb_set, CHECK constraints on keys.
-- * MySQL JSON: no direct index (generated column or multi-valued index CAST(... AS ... ARRAY) in 8.0.17+),
--   JSON_SET/JSON_CONTAINS/JSON_TABLE. Partial in-place update is supported but still rewrites more than a column.
-- * MySQL operator ->> is available on 5.7.13+; PostgreSQL ->> returns text so cast numbers.
ALTER TABLE products ADD CONSTRAINT chk_ram CHECK (JSON_EXTRACT(attrs, '$.ram_gb') IS NULL
                                                   OR JSON_EXTRACT(attrs, '$.ram_gb') > 0);   -- MySQL 8.0.16+ (not run)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Storing everything as one JSON blob (id, status, amount, user_id inside JSON) -> no FK, no stats, slow joins
-- ❌ Filtering on an unindexed JSON path:
SELECT name FROM products WHERE attrs->>'$.brand' = 'Zen';   -- full table scan, parses every document
-- ❌ PostgreSQL: comparing text to number: attrs->>'ram_gb' >= 16 -> operator/type error or string comparison
-- ✅ Index the path (generated column / GIN / expression index), cast types, keep core fields relational
```

---

## 🎯 Interview Tip (1 line)
Say: "I model stable, queried, constrained data relationally and put sparse or evolving attributes in JSON/jsonb, then index the exact paths I filter on (GIN or expression index in PostgreSQL, generated column in MySQL); if a JSON key shows up in joins or most WHERE clauses, I promote it to a real column."

---

## 🔗 Related Questions
→ Q238 (MySQL vs PostgreSQL) | Q237 (Covering index) | Q243 (Materialized view) | Q240 (Multi-tenant design)
