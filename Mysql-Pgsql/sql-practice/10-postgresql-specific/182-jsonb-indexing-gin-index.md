---

# Q182. JSONB Indexing — GIN Index
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL only (verified on PostgreSQL 18.6 via PGlite)

---

## ❓ Question
How do you index a JSONB column in PostgreSQL? Compare the default GIN operator class, `jsonb_path_ops`, and a B-tree expression index. Which operators does each accelerate, and what are the size trade-offs?

---

## 💡 Quick Concept (2 lines only)
A GIN index on JSONB maps every key/value to the rows containing it, so containment (`@>`) and key-existence (`?`) queries avoid a full scan. `jsonb_path_ops` is smaller and faster for `@>` only; a B-tree on `(col->>'key')` is best for equality/range on one known key.
हिंदी: JSONB पर GIN index हर key/value को rows से जोड़ता है; `@>` और `?` तेज़ होते हैं, एक fixed key के लिए expression B-tree बेहतर है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE products (id INT PRIMARY KEY, name TEXT, attrs JSONB);

INSERT INTO products
SELECT i, 'Product ' || i,
  jsonb_build_object(
    'brand', (ARRAY['acme','zenith','nova','orbit'])[1 + i % 4],
    'color', (ARRAY['red','blue','green'])[1 + i % 3],
    'tags',  jsonb_build_array('t' || (i % 50), 'sale'),
    'price', i % 1000)
FROM generate_series(1, 20000) i;

CREATE INDEX idx_products_attrs         ON products USING GIN (attrs);                  -- default jsonb_ops
CREATE INDEX idx_products_attrs_pathops ON products USING GIN (attrs jsonb_path_ops);   -- @> only
CREATE INDEX idx_products_brand         ON products ((attrs->>'brand'));                -- B-tree on one key
ANALYZE products;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: containment (matches key AND value, nested ok)
SELECT count(*) FROM products WHERE attrs @> '{"brand":"nova","color":"red"}';
-- count
-- 1667

-- Step 2: key exists
SELECT count(*) FROM products WHERE attrs ? 'brand';
-- 20000

-- Step 3: array element inside a key
SELECT count(*) FROM products WHERE attrs -> 'tags' ? 't7';
-- 400

-- Step 4: which index does the planner pick? (seqscan disabled only to prove index applicability on this small table)
SET enable_seqscan = off;

EXPLAIN SELECT id FROM products WHERE attrs @> '{"tags":["t7"]}';
-- Bitmap Heap Scan on products
--   Recheck Cond: (attrs @> '{"tags": ["t7"]}'::jsonb)
--   ->  Bitmap Index Scan on idx_products_attrs_pathops      <- smaller path_ops index wins for @>

EXPLAIN SELECT id FROM products WHERE attrs ? 'brand';
-- Bitmap Index Scan on idx_products_attrs                    <- only default jsonb_ops supports ?

EXPLAIN SELECT id FROM products WHERE attrs->>'brand' = 'nova';
-- Bitmap Index Scan on idx_products_brand                    <- expression B-tree

EXPLAIN SELECT id FROM products WHERE attrs->>'color' = 'red';
-- Seq Scan on products (Disabled: true)                      <- no index on ->>'color'; GIN can't help ->> equality

-- Step 5: index sizes
SELECT pg_size_pretty(pg_relation_size('idx_products_attrs'))         AS gin_default,
       pg_size_pretty(pg_relation_size('idx_products_attrs_pathops')) AS gin_pathops,
       pg_size_pretty(pg_relation_size('idx_products_brand'))         AS btree_expr;
-- gin_default | gin_pathops | btree_expr
-- 472 kB      | 352 kB      | 152 kB
-- (sizes are specific to this synthetic data)

-- ============================================
-- Operator support
-- ============================================
-- Operator               jsonb_ops (default)   jsonb_path_ops   B-tree on (col->>'k')
-- @>  contains                 yes                  yes (best)        no
-- ?  ?|  ?&  key exists        yes                  no                no
-- @@  @?  (jsonpath)           yes                  yes               no
-- =  <  >  on ->> value        no                   no                yes
```

---

## 🔍 Why This Works (3 lines max)
GIN is an inverted index: each key/value (or hashed path+value in `jsonb_path_ops`) points to a posting list of rows, and a bitmap scan then rechecks the exact condition. `jsonb_path_ops` stores only hashed paths-to-values so it is smaller but cannot answer key-existence. `->>` equality on a specific key is a plain scalar comparison, so a B-tree expression index is the smallest and fastest.
हिंदी: GIN inverted index है; path_ops छोटा है पर सिर्फ `@>` के लिए, और fixed key पर equality के लिए expression B-tree सबसे अच्छा है।

---

## ⚡ Alternative Solution

```sql
-- Partial GIN: index only the rows you query
CREATE INDEX idx_products_attrs_sale ON products USING GIN (attrs jsonb_path_ops)
WHERE attrs @> '{"tags":["sale"]}';

-- Generated column + B-tree for a hot field (also gives you a typed column and stats):
ALTER TABLE products ADD COLUMN price INT GENERATED ALWAYS AS ((attrs->>'price')::int) STORED;
CREATE INDEX idx_products_price ON products (price);

-- MySQL contrast: no GIN. Index JSON via a generated column, or a functional index:
--   ALTER TABLE products ADD COLUMN brand VARCHAR(30) GENERATED ALWAYS AS (attrs->>'$.brand') STORED, ADD INDEX (brand);
--   CREATE INDEX idx_brand ON products ((CAST(attrs->>'$.brand' AS CHAR(30))));
--   Multi-valued index for arrays: INDEX ((CAST(attrs->'$.tags' AS CHAR(20) ARRAY)))   -- 8.0.17+
```

---

## ⚠️ Common Mistake

```sql
-- ❌ GIN index then querying with ->> equality
WHERE attrs->>'color' = 'red'           -- GIN is not used (verified: Seq Scan)
-- ✅ Use containment so GIN applies:
WHERE attrs @> '{"color":"red"}'

-- ❌ Using jsonb_path_ops and then querying with ?
WHERE attrs ? 'brand'                   -- path_ops cannot serve this, falls back to scan
-- ✅ Use default jsonb_ops if you need ?, ?|, ?&

-- ❌ Using json (not jsonb) -> GIN does not exist for json type. Store as JSONB.
-- ❌ Indexing a column that is updated constantly: GIN has expensive writes (fastupdate pending list).
```

---

## 🎯 Interview Tip (1 line)
Say: "For ad-hoc filters I use GIN with jsonb_path_ops if I only need `@>`, default jsonb_ops if I need key-existence, and for one hot field I promote it to an expression or generated-column B-tree; I always check EXPLAIN because ->> equality ignores GIN."

---

## 🔗 Related Questions
→ Q181 (JSONB operators) | Q183 (Array + GIN) | Q184 (Full-text GIN) | Q244 (JSON vs relational)
