---

# Q183. Array Data Type — Operators + Indexing
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐ Medium
# DB: PostgreSQL only (verified on PostgreSQL 18.6 via PGlite)

---

## ❓ Question
How do PostgreSQL arrays work? Show the containment/overlap operators, `ANY`/`ALL`, `unnest`, `array_agg`, NULL/empty-array behaviour, and which queries a GIN index accelerates.

---

## 💡 Quick Concept (2 lines only)
Any type can be an array (`TEXT[]`, `INT[]`), indexed from 1; `@>` (contains), `<@` (contained by) and `&&` (overlaps) are the operators a GIN index accelerates. `unnest` turns an array into rows and `array_agg` turns rows back into an array.
हिंदी: Array 1 से index होता है; `@>`, `<@`, `&&` पर GIN index काम करता है, और `unnest`/`array_agg` से rows और array के बीच convert करते हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE articles (id INT PRIMARY KEY, title TEXT, tags TEXT[], scores INT[]);

INSERT INTO articles VALUES
 (1,'Intro to Postgres', ARRAY['db','sql','beginner'], ARRAY[5,7,9]),
 (2,'Index Deep Dive',   ARRAY['db','performance','index'], ARRAY[8,9]),
 (3,'Docker Basics',     ARRAY['devops','docker','beginner'], ARRAY[6]),
 (4,'Tuning Queries',    ARRAY['sql','performance'], '{}'),      -- empty array
 (5,'Untagged Draft',    NULL, NULL);                            -- NULL array

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: access + length (1-based!)
SELECT id, tags[1] AS first_tag, array_length(tags,1) AS n_tags, cardinality(tags) AS c FROM articles ORDER BY id;
-- id | first_tag | n_tags | c
-- 1  | db        | 3      | 3
-- 2  | db        | 3      | 3
-- 3  | devops    | 3      | 3
-- 4  | sql       | 2      | 2
-- 5  | NULL      | NULL   | NULL

-- Step 2: contains ALL of these
SELECT id FROM articles WHERE tags @> ARRAY['sql','performance'];     -- 4

-- Step 3: overlaps ANY of these
SELECT id FROM articles WHERE tags && ARRAY['docker','index'];        -- 2, 3

-- Step 4: contained BY (every element of tags is in the given list)
SELECT id FROM articles WHERE tags <@ ARRAY['sql','performance','db','extra'];   -- 4

-- Step 5: single value tests
SELECT id FROM articles WHERE 'beginner' = ANY(tags);                 -- 1, 3
SELECT id FROM articles WHERE 'beginner' = ALL(tags);                 -- (no rows)

-- Step 6: modify (returns new arrays, does not change the row)
SELECT array_append(tags,'new') a, array_remove(tags,'db') r, array_cat(tags, ARRAY['x']) c FROM articles WHERE id = 1;
-- a = {db,sql,beginner,new} | r = {sql,beginner} | c = {db,sql,beginner,x}

-- Step 7: array -> rows, then aggregate back
SELECT t AS tag, count(*) FROM articles, unnest(tags) AS t GROUP BY t ORDER BY 2 DESC, 1;
-- beginner 2 | db 2 | performance 2 | sql 2 | devops 1 | docker 1 | index 1

SELECT array_agg(title ORDER BY id) FROM articles WHERE tags @> ARRAY['db'];
-- {"Intro to Postgres","Index Deep Dive"}

-- Step 8: edge cases (real output)
SELECT tags[0] AS zero_idx, tags[10] AS out_of_bounds FROM articles WHERE id = 1;
-- NULL | NULL                       <- no error, just NULL
SELECT ARRAY[1,2] < ARRAY[1,3] AS lt;                   -- true (element-wise compare)
SELECT id, cardinality(scores) FROM articles ORDER BY id;
-- 1:3  2:2  3:1  4:0  5:NULL         <- empty array = 0, NULL array = NULL
SELECT id FROM articles WHERE array_length(scores,1) IS NULL;   -- 4, 5  (array_length of '{}' is NULL, not 0!)

-- ============================================
-- INDEXING: GIN on array column
-- ============================================
CREATE TABLE articles_big AS
SELECT i AS id, ARRAY['t'||(i%100), 't'||(i%37), 'all'] AS tags FROM generate_series(1,30000) i;
CREATE INDEX idx_articles_big_tags ON articles_big USING GIN (tags);
ANALYZE articles_big;
SET enable_seqscan = off;      -- to prove applicability on small data

EXPLAIN SELECT id FROM articles_big WHERE tags @> ARRAY['t5'];
-- Bitmap Index Scan on idx_articles_big_tags     (uses GIN)
EXPLAIN SELECT id FROM articles_big WHERE tags && ARRAY['t5'];
-- Bitmap Index Scan on idx_articles_big_tags     (uses GIN)
EXPLAIN SELECT id FROM articles_big WHERE 't5' = ANY(tags);
-- Seq Scan (Disabled: true)                      <- ANY() is NOT indexable by GIN
```

---

## 🔍 Why This Works (3 lines max)
GIN indexes each array element separately, so `@>` and `&&` become "find rows in these elements' posting lists" (intersection or union). `= ANY(col)` is a scalar-vs-array expression the operator class does not recognise, so it scans. Arrays are fine for small, tightly-owned lists; if elements need their own attributes or foreign keys, use a child table.
हिंदी: GIN हर element को अलग index करता है इसलिए `@>`/`&&` तेज़ हैं; `= ANY(col)` index नहीं use करता, इसलिए `@> ARRAY[x]` लिखो।

---

## ⚡ Alternative Solution

```sql
-- Same "has tag" test written index-friendly:
SELECT id FROM articles WHERE tags @> ARRAY['beginner'];       -- instead of 'beginner' = ANY(tags)

-- Normalised alternative (many-to-many) - better for FKs, per-tag metadata, and cross-article joins:
CREATE TABLE article_tags (article_id INT REFERENCES articles(id), tag TEXT, PRIMARY KEY (article_id, tag));
CREATE INDEX idx_article_tags_tag ON article_tags (tag);

-- MySQL contrast: no array type. Use JSON array + multi-valued index (8.0.17+):
--   CREATE TABLE articles (id INT PRIMARY KEY, tags JSON, INDEX idx_tags ((CAST(tags->'$' AS CHAR(30) ARRAY))));
--   SELECT id FROM articles WHERE 'sql' MEMBER OF (tags);
--   SELECT id FROM articles WHERE JSON_CONTAINS(tags, '"sql"');
--   (MySQL JSON syntax shown from documentation; not run in this verification set.)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Assuming 0-based indexing
SELECT tags[0] FROM articles;           -- NULL (no error). First element is tags[1].

-- ❌ Using array_length to test emptiness
WHERE array_length(scores,1) = 0        -- never true; array_length('{}',1) is NULL
-- ✅ WHERE cardinality(scores) = 0     -- or coalesce(cardinality(scores),0) = 0

-- ❌ WHERE 'x' = ANY(tags) on a big table expecting the GIN index  -> seq scan
-- ✅ WHERE tags @> ARRAY['x']

-- ❌ Using arrays for data that needs referential integrity (no FK from array elements).
```

---

## 🎯 Interview Tip (1 line)
Say: "Arrays are great for small immutable lists queried with `@>`/`&&` plus a GIN index, but anything needing foreign keys, per-element attributes, or frequent single-element updates belongs in a child table."

---

## 🔗 Related Questions
→ Q181 (JSONB operators) | Q182 (JSONB GIN) | Q184 (Full-text search) | Q244 (JSON vs relational)
