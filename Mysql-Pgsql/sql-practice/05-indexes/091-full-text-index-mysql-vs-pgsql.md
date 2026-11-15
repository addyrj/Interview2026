---

# Q091. Full-Text Index - MySQL vs PgSQL
# Category: Indexes
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
`WHERE body LIKE '%search%'` is a full scan. How do you build full-text search with an index in MySQL (FULLTEXT / MATCH AGAINST) and in PostgreSQL (tsvector + GIN)? Compare ranking, stemming and query syntax.

---

## 💡 Quick Concept (2 lines only)
Full-text indexes tokenize text into words (an inverted index: word -> rows), so word searches and relevance ranking avoid LIKE '%x%' scans. MySQL: `FULLTEXT` + `MATCH() AGAINST()`; PostgreSQL: `tsvector` column + `GIN` index + `@@ tsquery`, with language-aware stemming.
हिंदी: Full-text index शब्दों का inverted index है; MySQL में FULLTEXT + MATCH AGAINST, PostgreSQL में tsvector + GIN + @@।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP - MySQL 8.0+ (InnoDB FULLTEXT)
-- ============================================

CREATE TABLE articles (
  article_id INT PRIMARY KEY AUTO_INCREMENT,
  title      VARCHAR(200) NOT NULL,
  body       TEXT NOT NULL,
  FULLTEXT KEY ft_title_body (title, body)
) ENGINE=InnoDB;

INSERT INTO articles (title, body) VALUES
 ('Indexing basics in MySQL', 'A B-Tree index speeds up lookups. Full text indexes help with word search.'),
 ('PostgreSQL vacuum explained', 'Vacuum removes dead tuples and reduces table bloat in PostgreSQL.'),
 ('Optimizing slow queries', 'Use EXPLAIN to see whether an index is used for the query.'),
 ('Scaling databases with replication', 'Replication copies data to replicas for read scaling.'),
 ('Full text search tutorial', 'Search engines rank documents by relevance using full text indexes.');

-- ============================================
-- SOLUTION - MySQL
-- ============================================

-- Natural language mode: ranked by relevance
SELECT article_id, title, ROUND(MATCH(title, body) AGAINST ('index search'), 4) AS score
FROM articles
WHERE MATCH(title, body) AGAINST ('index search' IN NATURAL LANGUAGE MODE)
ORDER BY score DESC;

-- Boolean mode: + must, - must not, * prefix, "phrase"
SELECT article_id, title FROM articles WHERE MATCH(title, body) AGAINST ('+index -replication' IN BOOLEAN MODE);
SELECT article_id, title FROM articles WHERE MATCH(title, body) AGAINST ('optim*'              IN BOOLEAN MODE);
SELECT article_id, title FROM articles WHERE MATCH(title, body) AGAINST ('"full text"'         IN BOOLEAN MODE);

-- ============================================
-- SETUP + SOLUTION - PostgreSQL
-- ============================================

CREATE TABLE articles (
  article_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  title      VARCHAR(200) NOT NULL,
  body       TEXT NOT NULL,
  search_vec tsvector GENERATED ALWAYS AS (                 -- PG 12+ stored generated column
      setweight(to_tsvector('english', title), 'A') ||      -- title matches rank higher
      setweight(to_tsvector('english', body),  'B')) STORED
);
CREATE INDEX idx_articles_fts ON articles USING GIN (search_vec);
-- (same 5 INSERT rows as above)

SELECT article_id, title,
       ROUND(ts_rank(search_vec, plainto_tsquery('english', 'index search'))::numeric, 4) AS score
FROM articles
WHERE search_vec @@ plainto_tsquery('english', 'index search')
ORDER BY score DESC;

SELECT article_id, title FROM articles WHERE search_vec @@ plainto_tsquery('english', 'index');
SELECT article_id, title FROM articles WHERE search_vec @@ to_tsquery('english', 'index & !replication');
SELECT article_id, title FROM articles WHERE search_vec @@ to_tsquery('english', 'optim:*');
SELECT article_id, title FROM articles WHERE search_vec @@ websearch_to_tsquery('english', '"full text" -replication');

-- ============================================
-- EXPECTED OUTPUT (verified: MySQL 9.1 and PostgreSQL 18 via PGlite)
-- ============================================

-- MySQL natural language 'index search':
-- article_id | title                     | score
-- 1          | Indexing basics in MySQL  | 0.3167      <- ties can come back in either order
-- 5          | Full text search tutorial | 0.3167
-- 3          | Optimizing slow queries   | 0.1584
-- MySQL '+index -replication' -> ids 1, 3  |  'optim*' -> id 3  |  '"full text"' -> ids 5, 1
--
-- PostgreSQL ts_rank 'index search':
-- 1 | Indexing basics in MySQL  | 0.4894
-- 5 | Full text search tutorial | 0.3558
-- PG plainto_tsquery('index') -> ids 1, 3, 5      <- id 5 found: "indexes" stemmed to "index"
-- PG 'index & !replication' -> ids 1, 3, 5 | 'optim:*' -> id 3 | websearch '"full text" -replication' -> ids 1, 5
-- to_tsvector('english','The indexes are being optimized') = 'index':2 'optim':5   (stop words removed, stemmed)
--
-- Plan with SET enable_seqscan = off (tiny table): Bitmap Index Scan on idx_articles_fts
--   Index Cond: (search_vec @@ '''index'''::tsquery)
-- MySQL EXPLAIN: type=fulltext, key=ft_title_body, Extra: Using where; Ft_hints: sorted
```

---

## 🔍 Why This Works (3 lines max)
Both build an inverted index (token -> row ids) so a word lookup is an index probe, and the engine scores relevance (MySQL natural-language mode, PostgreSQL ts_rank). PostgreSQL applies a language dictionary (stemming, stop words) so "indexes" matches "index"; MySQL InnoDB does not stem, so id 5 was missed by 'index'.
हिंदी: दोनों inverted index बनाते हैं; PostgreSQL stemming करता है (indexes = index), MySQL नहीं करता।

---

## ⚡ Alternative Solution

```sql
-- Substring / typo-tolerant search in PostgreSQL: pg_trgm + GIN supports LIKE '%x%' and similarity()
--   CREATE EXTENSION pg_trgm;
--   CREATE INDEX idx_body_trgm ON articles USING GIN (body gin_trgm_ops);
--   (extension not run here)
-- MySQL has no trigram index; for substring search use an external engine (Elasticsearch/OpenSearch/Meilisearch).

-- MySQL FULLTEXT parser knobs (defaults seen on 9.1): innodb_ft_min_token_size = 3, innodb_ft_enable_stopword = 1
--   -> words shorter than 3 chars and stop words ('is', 'the') are ignored: AGAINST('is') returned 0 rows (verified).
--   Chinese/Japanese/Korean: WITH PARSER ngram.
-- Other MySQL modes: WITH QUERY EXPANSION; MyISAM and InnoDB both support FULLTEXT since 5.6.

-- Compare: LIKE '%search%' always scans the table (leading wildcard, Q088).
--   SELECT ... WHERE body LIKE '%search%'  -> matches ids 1 and 5 here but cannot use any B-Tree.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: MATCH(title) AGAINST (...) when the FULLTEXT index is on (title, body)
-- MySQL requires the MATCH column list to match an existing FULLTEXT index exactly (InnoDB: error 1191).
-- ✅ MATCH(title, body) or create a separate FULLTEXT(title).

-- ❌ Wrong: PostgreSQL  WHERE to_tsvector('english', body) @@ ... with no stored column/expression index
-- Recomputes tokens for every row on every query (Seq Scan).
-- ✅ Stored tsvector column (as above) or  CREATE INDEX ... USING GIN (to_tsvector('english', body)).
--    The query must then use the SAME expression and the same language config.

-- ❌ Wrong: expecting MySQL to find 'indexes' when you search 'index' (no stemming) or short/stop words ('is', 'a')
-- ✅ Use boolean prefix  index*  or switch to PostgreSQL / a search engine.

-- ❌ Wrong: to_tsquery('full text') with spaces -> syntax error; use plainto_tsquery / websearch_to_tsquery for user input.
```

---

## 🎯 Interview Tip (1 line)
Say: "LIKE '%x%' can't use a B-Tree, so I use MySQL FULLTEXT with MATCH AGAINST or PostgreSQL tsvector with a GIN index and a weighted stored column; PostgreSQL gives stemming, dictionaries and phrase queries, and at real scale or for fuzzy relevance I'd move to Elasticsearch/OpenSearch."

---

## 🔗 Related Questions
→ Q081 (B-Tree index internals) | Q088 (When MySQL does NOT use an index) | Q089 (Functional index) | Q092 (Hash index)
