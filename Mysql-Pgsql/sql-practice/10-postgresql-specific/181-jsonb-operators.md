---

# Q181. PostgreSQL JSONB — Operators, Indexing, and Real Use Cases
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL only

---

## ❓ Question
Explain JSONB vs JSON in PostgreSQL. Show the key operators (@>, ?, #>, #>>). How do you index JSONB for fast queries? When should you use JSONB vs a relational column?

---

## 💡 Quick Concept (2 lines only)
JSONB stores JSON as parsed binary — supports indexing, operators (@> contains, ? key exists, #> nested path), and deduplicates keys. JSON stores as text (exact input preserved, no indexing). Always use JSONB unless preserving exact input is required.
हिंदी: JSONB = binary (indexed, fast queries)। JSON = text (exact input preserve, no index)। Production में हमेशा JSONB।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- JSONB vs JSON
-- ============================================

/*
Feature               | JSON          | JSONB
──────────────────────┼───────────────┼──────────────────────
Storage               | Text (exact)  | Binary (parsed)
Key order             | Preserved     | NOT preserved (sorted)
Duplicate keys        | Allowed       | Last value wins
Whitespace            | Preserved     | Stripped
Indexing              | ❌ No GIN     | ✅ GIN index supported
Operators (@>, ?)     | ❌            | ✅
Read performance      | Slower (parse)| Faster (already parsed)
Write performance     | Faster        | Slightly slower (parse on write)
Use when              | Preserving    | Querying, indexing,
                      | exact format  | most production use
*/

-- ============================================
-- SETUP
-- ============================================

CREATE TABLE products (
  id    SERIAL PRIMARY KEY,
  name  VARCHAR(200),
  data  JSONB   -- use JSONB not JSON!
);

INSERT INTO products (name, data) VALUES
('Laptop Pro', '{
  "brand": "Dell",
  "specs": {"cpu": "i7", "ram": 16, "storage": 512},
  "tags": ["electronics", "laptop", "sale"],
  "price": 1299.99,
  "available": true,
  "variants": [
    {"color": "black", "stock": 10},
    {"color": "silver", "stock": 5}
  ]
}'),
('Wireless Mouse', '{
  "brand": "Logitech",
  "specs": {"wireless": true, "dpi": 1200},
  "tags": ["electronics", "peripheral"],
  "price": 49.99,
  "available": true
}'),
('USB-C Hub', '{
  "brand": "Anker",
  "specs": {"ports": 7, "power_delivery": true},
  "tags": ["electronics", "accessory"],
  "price": 79.99,
  "available": false
}');

-- ============================================
-- BASIC ACCESS OPERATORS
-- ============================================

-- -> returns JSONB (key or array index):
SELECT data -> 'brand' FROM products;
-- "Dell"     (JSONB — quoted!)
-- "Logitech"
-- "Anker"

-- ->> returns TEXT (key or array index):
SELECT data ->> 'brand' FROM products;
-- Dell       (text — no quotes)
-- Logitech
-- Anker

-- Nested access with ->:
SELECT data -> 'specs' -> 'cpu' FROM products WHERE name = 'Laptop Pro';
-- "i7"  (JSONB)

-- Nested with ->> (cast to text):
SELECT data -> 'specs' ->> 'cpu' FROM products WHERE name = 'Laptop Pro';
-- i7  (text)

-- Array element:
SELECT data -> 'tags' -> 0 FROM products WHERE name = 'Laptop Pro';
-- "electronics"

-- ============================================
-- PATH OPERATORS (#> and #>>)
-- ============================================

-- #> navigates nested path (returns JSONB):
SELECT data #> '{specs, cpu}' FROM products WHERE name = 'Laptop Pro';
-- "i7"

-- #>> navigates nested path (returns TEXT):
SELECT data #>> '{specs, ram}' FROM products WHERE name = 'Laptop Pro';
-- 16

-- Array path:
SELECT data #>> '{variants, 0, color}' FROM products WHERE name = 'Laptop Pro';
-- black  (first variant's color)

SELECT data #>> '{variants, 1, stock}' FROM products WHERE name = 'Laptop Pro';
-- 5

-- ============================================
-- CONTAINMENT OPERATOR @> (MOST IMPORTANT FOR INDEXING)
-- ============================================

-- @> left contains right (tests if left includes the right structure):

-- Find all Dell products:
SELECT name FROM products WHERE data @> '{"brand": "Dell"}';
-- Laptop Pro ✅

-- Find products available for sale:
SELECT name FROM products WHERE data @> '{"available": true}';
-- Laptop Pro, Wireless Mouse

-- Find products with "sale" tag:
SELECT name FROM products WHERE data @> '{"tags": ["sale"]}';
-- Laptop Pro ✅ (array containment — does tags array contain "sale"?)

-- Find products with specific nested spec:
SELECT name FROM products WHERE data @> '{"specs": {"cpu": "i7"}}';
-- Laptop Pro ✅

-- @> is invertible:
SELECT name FROM products WHERE '{"brand": "Dell", "available": true}' <@ data;
-- <@ is "contained by" (right contains left) — equivalent

-- ============================================
-- KEY EXISTENCE OPERATORS ? and ?| and ?&
-- ============================================

-- ? tests if key exists at top level:
SELECT name FROM products WHERE data ? 'brand';
-- All products (all have 'brand' key)

SELECT name FROM products WHERE data -> 'specs' ? 'cpu';
-- Only Laptop Pro (only one with cpu key in specs)

-- ?| any key exists:
SELECT name FROM products WHERE data ?| ARRAY['discount', 'brand'];
-- All products (all have 'brand')

-- ?& all keys exist:
SELECT name FROM products WHERE data ?& ARRAY['brand', 'price', 'available'];
-- All products (all have all three keys)

-- ============================================
-- MODIFYING JSONB (jsonb_set, ||)
-- ============================================

-- Update a field: jsonb_set(target, path, new_value)
UPDATE products
SET data = jsonb_set(data, '{price}', '999.99')
WHERE name = 'Laptop Pro';
-- Sets price to 999.99

-- Update nested field:
UPDATE products
SET data = jsonb_set(data, '{specs, ram}', '32')
WHERE name = 'Laptop Pro';
-- Sets specs.ram to 32

-- Merge/add keys with || (concatenation operator):
UPDATE products
SET data = data || '{"discount": 0.1, "featured": true}'
WHERE name = 'Laptop Pro';
-- Adds discount and featured keys (overwrites if key exists)

-- Remove a key with - operator:
UPDATE products
SET data = data - 'discount'
WHERE name = 'Laptop Pro';

-- Remove nested key with #- operator:
UPDATE products
SET data = data #- '{specs, storage}'
WHERE name = 'Laptop Pro';

-- ============================================
-- GIN INDEX ON JSONB (CRITICAL FOR PERFORMANCE!)
-- ============================================

-- Without index: @> does sequential scan on all rows!
-- With GIN index: @> uses index → O(log N) lookup

-- Default GIN index (supports @>, ?, ?|, ?&):
CREATE INDEX idx_products_data_gin ON products USING GIN(data);

-- EXPLAIN ANALYZE after index:
EXPLAIN ANALYZE SELECT name FROM products WHERE data @> '{"brand": "Dell"}';
-- Bitmap Index Scan on idx_products_data_gin
-- ← Index used! Fast for any @> query on any key

-- jsonb_path_ops (smaller index — supports only @> and jsonpath):
CREATE INDEX idx_products_data_path ON products USING GIN(data jsonb_path_ops);
-- Smaller and faster for @> only
-- Cannot use for ? and ?| operators
-- Use when you only need @> containment queries

-- Index specific key (smaller, faster for that key):
CREATE INDEX idx_products_brand ON products((data ->> 'brand'));
-- B-Tree index on extracted brand value (not GIN)
-- Use for: WHERE data ->> 'brand' = 'Dell' (equality only, no containment)
-- Much smaller than full GIN index

-- ============================================
-- JSONB AGGREGATION AND QUERYING
-- ============================================

-- Expand JSONB array to rows with jsonb_array_elements:
SELECT name, tag
FROM products, jsonb_array_elements_text(data -> 'tags') AS tag
ORDER BY name, tag;
-- Laptop Pro   | electronics
-- Laptop Pro   | laptop
-- Laptop Pro   | sale
-- Wireless Mouse | electronics
-- Wireless Mouse | peripheral

-- Build JSONB from aggregate (jsonb_agg):
SELECT jsonb_agg(jsonb_build_object('name', name, 'price', data ->> 'price'))
FROM products WHERE data @> '{"available": true}';
-- [{"name":"Laptop Pro","price":"1299.99"},{"name":"Wireless Mouse","price":"49.99"}]

-- Extract to relational columns (json_populate_record — for migration):
SELECT name, (jsonb_populate_record(NULL::products_spec, data -> 'specs')).*
FROM products WHERE name = 'Laptop Pro';

-- ============================================
-- WHEN TO USE JSONB vs RELATIONAL COLUMNS
-- ============================================

/*
Use JSONB for:
  ✅ Schema varies per row (products with different attributes)
  ✅ Storing external API responses (unpredictable structure)
  ✅ Feature flags / user preferences (sparse, variable keys)
  ✅ Audit logs / event sourcing (capture arbitrary payloads)
  ✅ Prototyping (iterate quickly before schema stabilizes)

Use relational columns for:
  ✅ Fixed, known schema (all rows have same columns)
  ✅ Columns used in JOINs (can't JOIN on JSONB key efficiently)
  ✅ Columns with constraints (NOT NULL, UNIQUE, FK references)
  ✅ Columns used in aggregations (SUM, AVG — cast overhead from JSONB)
  ✅ Columns in high-cardinality WHERE (B-Tree index more efficient than GIN)

Hybrid pattern (BEST practice):
  - Fixed, critical columns as proper columns (id, user_id, created_at, status)
  - Variable, optional attributes in JSONB (metadata, settings, extra_data)
*/

-- Hybrid example:
CREATE TABLE events (
  id         BIGSERIAL PRIMARY KEY,
  user_id    INT NOT NULL,       -- relational (used in JOINs, FK)
  event_type VARCHAR(50) NOT NULL,  -- relational (indexed, filtered)
  occurred_at TIMESTAMPTZ NOT NULL, -- relational (partitioned on this)
  payload    JSONB             -- arbitrary event-specific data
);

CREATE INDEX ON events(user_id);
CREATE INDEX ON events(event_type);
CREATE INDEX ON events(occurred_at);
CREATE INDEX ON events USING GIN(payload);  -- for payload queries
```

---

## 🔍 Why This Works (3 lines max)
JSONB's GIN index creates an inverted index over all keys and values in the document — a single GIN index supports `@>`, `?`, `?|`, and `?&` queries on ANY key without knowing the schema in advance. The `@>` containment operator is the most powerful for complex nested queries, and it benefits from the GIN index directly. For known, frequently-queried keys, a targeted B-Tree index on the extracted value is faster than GIN.
हिंदी: GIN index = inverted index over all keys — ANY key पर @> और ? queries fast होती हैं। Known keys के लिए B-Tree on extracted value ज्यादा efficient।

---

## ⚡ Alternative Solution

```sql
-- JSON path queries (PgSQL 12+) — XPath-style for JSON:
SELECT name FROM products
WHERE jsonb_path_exists(data, '$.variants[*].stock ? (@ > 8)');
-- Finds products where ANY variant has stock > 8
-- More expressive than @> for complex conditions

SELECT jsonb_path_query(data, '$.variants[*].color') AS color
FROM products WHERE name = 'Laptop Pro';
-- "black"
-- "silver"
-- Extracts all variant colors using JSON path expression
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Using JSON instead of JSONB
CREATE TABLE events (data JSON);  -- ← no GIN index support!
-- ✅ Always: data JSONB

-- ❌ Wrong: Querying with ->> in WHERE (misses GIN index!)
SELECT * FROM products WHERE data ->> 'brand' = 'Dell';
-- This uses a sequential scan! ->> extracts text, index not used for @>
-- ✅ Fix: use @> for GIN index benefit:
SELECT * FROM products WHERE data @> '{"brand": "Dell"}';
-- OR: create B-Tree index on extracted value:
CREATE INDEX idx_brand ON products((data ->> 'brand'));
-- THEN: WHERE data ->> 'brand' = 'Dell' uses the B-Tree index

-- ❌ Wrong: Storing large binary data (images, files) in JSONB
-- JSONB is for structured metadata, not blob storage
-- ✅ Store files in S3/object storage, store the URL in JSONB/column

-- ❌ Wrong: Deep nesting (5+ levels) in JSONB
-- Deeply nested paths are hard to index and query
-- ✅ Flatten frequently-queried nested fields to top level:
-- data @> '{"meta": {"user": {"settings": {"theme": "dark"}}}}'  ← hard to index
-- vs: settings @> '{"theme": "dark"}'  ← clean
```

---

## 🎯 Interview Tip (1 line)
Say: "I always use JSONB over JSON — it's stored as parsed binary, supports GIN indexing, and has rich operators: `@>` for containment (benefits from GIN), `?` for key existence, and `#>>` for nested paths. For fixed, known columns I use relational columns; for variable per-row attributes (product specs, user preferences, event payloads) I use a JSONB `metadata` column with a GIN index."

---

## 🔗 Related Questions
→ Q185 (LISTEN/NOTIFY) | Q190 (materialized views) | Q196 (row-level security) | Q083 (composite indexes)
