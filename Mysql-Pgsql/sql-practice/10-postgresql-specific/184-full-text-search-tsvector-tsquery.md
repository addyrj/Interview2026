---

# Q184. Full-Text Search — tsvector + tsquery
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL only (verified on PostgreSQL 18.6 via PGlite)

---

## ❓ Question
Implement ranked full-text search in PostgreSQL over a `docs` table with a title and body. Cover `tsvector`, `tsquery` variants, ranking, highlighting, weights, a GIN index and a stored generated column.

---

## 💡 Quick Concept (2 lines only)
`to_tsvector` normalises text into stemmed lexemes (stop-words removed), `to_tsquery` builds a boolean query, and `@@` matches them; a GIN index on the tsvector makes it fast. `ts_rank` scores relevance and `ts_headline` highlights matches.
हिंदी: `to_tsvector` text को stemmed शब्दों में बदलता है, `to_tsquery` query बनाता है, `@@` से match होता है और GIN index इसे तेज़ करता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE docs (
  id    INT PRIMARY KEY,
  title TEXT,
  body  TEXT,
  search_vec tsvector GENERATED ALWAYS AS (          -- maintained automatically
      setweight(to_tsvector('english', coalesce(title,'')), 'A') ||   -- title matches rank higher
      setweight(to_tsvector('english', coalesce(body ,'')), 'B')
  ) STORED
);

INSERT INTO docs (id, title, body) VALUES
 (1,'Postgres Indexing Guide','Learn how B-tree and GIN indexes speed up queries in PostgreSQL.'),
 (2,'Running Databases in Docker','Containers make it easy to run Postgres locally for testing.'),
 (3,'Full Text Search Basics','Use tsvector and tsquery to search documents. Ranking sorts results by relevance.'),
 (4,'Cooking Pasta','Boil water, add salt, and cook the pasta until it is al dente.'),
 (5,'Query Tuning','Slow queries can often be fixed by adding the right index; indexing matters.');

CREATE INDEX idx_docs_search ON docs USING GIN (search_vec);

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: what normalisation does (stemming, stop-words dropped, positions kept)
SELECT to_tsvector('english','The quick brown foxes were jumping over lazy dogs');
-- 'brown':3 'dog':9 'fox':4 'jump':6 'lazi':8 'quick':2

-- Step 2: the three ways to build a query
SELECT to_tsquery('english','running & databases'),
       plainto_tsquery('english','running databases'),
       websearch_to_tsquery('english','"full text" -pasta OR docker');
-- 'run' & 'databas' | 'run' & 'databas' | 'full' <-> 'text' & !'pasta' | 'docker'
-- websearch_to_tsquery accepts Google-style input and never raises syntax errors.

-- Step 3: basic matches (stemming: "index" matches "indexes" and "indexing")
SELECT id, title FROM docs WHERE search_vec @@ to_tsquery('english','index') ORDER BY id;
-- 1 Postgres Indexing Guide | 5 Query Tuning

-- Step 4: AND / OR / NOT / prefix
SELECT id FROM docs WHERE search_vec @@ to_tsquery('english','postgres & docker');            -- 2
SELECT id FROM docs WHERE search_vec @@ to_tsquery('english','postgres | pasta');             -- 1, 2, 4
SELECT id FROM docs WHERE search_vec @@ to_tsquery('english','!pasta & (search | index:*)');  -- 1, 3, 5

-- Step 5: ranking (title weight A beats body weight B)
SELECT id, title, round(ts_rank(search_vec, q)::numeric, 4) AS rank
FROM docs, to_tsquery('english','index') q
WHERE search_vec @@ q
ORDER BY rank DESC, id;
-- id | title                   | rank
-- 1  | Postgres Indexing Guide | 0.6687   <- "Indexing" in the title (weight A)
-- 5  | Query Tuning            | 0.3040   <- only in body

-- Step 6: highlight snippets
SELECT id, ts_headline('english', body, to_tsquery('english','index'),
                       'StartSel=<<, StopSel=>>, MaxWords=12, MinWords=5')
FROM docs WHERE id IN (1,5) ORDER BY id;
-- 1 | <<indexes>> speed up queries in PostgreSQL
-- 5 | adding the right <<index>>; <<indexing>> matters.

-- Step 7: language config matters
SELECT id FROM docs WHERE to_tsvector('english', body) @@ to_tsquery('english','running');  -- 2 (stems run/running)
SELECT id FROM docs WHERE to_tsvector('simple',  body) @@ to_tsquery('simple','running');   -- no rows (no stemming; body has "run")

-- Step 8: stop-words produce empty values
SELECT to_tsvector('english','the and of'), to_tsquery('english','the');
-- (empty) | (empty)   <- and PostgreSQL emits a NOTICE "text-search query contains only stop words"

-- Step 9: index is used on larger data (30,000 rows)
CREATE TABLE docs_big AS
SELECT i AS id, to_tsvector('english','word'||(i%500)||' filler text number '||i) AS v FROM generate_series(1,30000) i;
CREATE INDEX idx_docs_big ON docs_big USING GIN (v);
ANALYZE docs_big;
EXPLAIN SELECT id FROM docs_big WHERE v @@ to_tsquery('english','word42');
-- Bitmap Heap Scan on docs_big
--   Recheck Cond: (v @@ '''word42'''::tsquery)
--   ->  Bitmap Index Scan on idx_docs_big
```

---

## 🔍 Why This Works (3 lines max)
Both document and query go through the same text-search configuration, so "indexes", "indexing" and "index" reduce to the same lexeme and match. A GIN index stores lexeme -> row lists, and a stored generated tsvector avoids recomputing `to_tsvector` on every query or needing a trigger.
हिंदी: Document और query एक ही config से गुज़रते हैं इसलिए stemming से शब्द match होते हैं; generated tsvector पर GIN index सबसे तेज़ रहता है।

---

## ⚡ Alternative Solution

```sql
-- Expression index (no extra column) - the query must repeat the EXACT same expression:
CREATE INDEX idx_docs_expr ON docs USING GIN (to_tsvector('english', title || ' ' || body));
SELECT id FROM docs WHERE to_tsvector('english', title || ' ' || body) @@ plainto_tsquery('english','pasta');
-- Always pass the config ('english') explicitly; the 1-argument form depends on default_text_search_config
-- and cannot be used in an index.

-- Typo-tolerant / substring search is a different tool: pg_trgm (Q190).
-- For large-scale relevance (BM25, facets, fuzzy) consider Elasticsearch/OpenSearch.

-- MySQL contrast (InnoDB FULLTEXT, not run here):
--   ALTER TABLE docs ADD FULLTEXT INDEX ft_docs (title, body);
--   SELECT id, MATCH(title, body) AGAINST ('index' IN NATURAL LANGUAGE MODE) AS score
--   FROM docs WHERE MATCH(title, body) AGAINST ('+postgres -pasta' IN BOOLEAN MODE);
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Using LIKE '%word%' for search: no stemming, no ranking, cannot use a B-tree index
SELECT id FROM docs WHERE body ILIKE '%running%';        -- misses "run"
-- ✅ search_vec @@ plainto_tsquery('english','running')

-- ❌ Query on to_tsvector('english', body) when the index is on a different expression
-- Planner cannot match them -> seq scan. Use the stored column or the identical expression.

-- ❌ Raw user input in to_tsquery: to_tsquery('english','c++ & (') raises a syntax error
-- ✅ plainto_tsquery / websearch_to_tsquery for user-typed text

-- ❌ Mixing configs: 'simple' index vs 'english' query returns nothing (shown above).
```

---

## 🎯 Interview Tip (1 line)
Say: "I keep a weighted, stored tsvector column with a GIN index, query it with websearch_to_tsquery, rank with ts_rank, and I know when to hand off to pg_trgm for fuzzy matching or a dedicated search engine at scale."

---

## 🔗 Related Questions
→ Q182 (GIN on JSONB) | Q183 (Array + GIN) | Q190 (pg_trgm) | Q004 (LIKE vs ILIKE)
