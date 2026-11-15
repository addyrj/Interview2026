---

# Q228. N+1 Query Problem — What and Fix
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
What is the N+1 query problem? Show how it appears when listing authors with their books, how to detect it, and the SQL-level fixes (JOIN, IN batch, JSON aggregation).

---

## 💡 Quick Concept (2 lines only)
N+1 = 1 query to fetch N parent rows, then N more queries (one per parent) to fetch children — total N+1 round trips instead of 1 or 2. Usually hidden by an ORM's lazy loading; fix with a JOIN, a single `IN (...)` batch, or aggregation.
हिंदी: 1 query parent की + हर parent के लिए 1 query child की = N+1; इसे JOIN या एक batch IN query से ठीक करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE authors (
  id   INT PRIMARY KEY,
  name VARCHAR(50) NOT NULL
);

CREATE TABLE books (
  id        INT PRIMARY KEY,
  author_id INT NOT NULL,
  title     VARCHAR(100) NOT NULL
);

CREATE INDEX idx_books_author ON books (author_id);   -- FK column index: required for fast child lookups

INSERT INTO authors VALUES (1,'Orwell'),(2,'Austen'),(3,'Tolkien'),(4,'Rowling');

INSERT INTO books VALUES
  (1, 1, '1984'),
  (2, 1, 'Animal Farm'),
  (3, 2, 'Emma'),
  (4, 2, 'Persuasion'),
  (5, 2, 'Pride and Prejudice'),
  (6, 3, 'The Hobbit'),
  (7, 4, 'Philosopher''s Stone');

-- ============================================
-- THE PROBLEM — what the app/ORM actually sends
-- ============================================

-- Query 1 (the "1"): fetch all parents
SELECT id, name FROM authors ORDER BY id;               -- 4 rows

-- Queries 2..5 (the "N" = 4): one per author, issued in an application loop
SELECT title FROM books WHERE author_id = 1 ORDER BY id;   -- Orwell: 1984, Animal Farm
SELECT title FROM books WHERE author_id = 2 ORDER BY id;   -- Austen: Emma, Persuasion, Pride and Prejudice
SELECT title FROM books WHERE author_id = 3 ORDER BY id;   -- Tolkien: The Hobbit
SELECT title FROM books WHERE author_id = 4 ORDER BY id;   -- Rowling: Philosopher's Stone

-- Measured on MySQL 9.1 (FLUSH STATUS, then run the 5 queries, SHOW SESSION STATUS LIKE 'Com_select'):
-- Com_select = 5     (1 + N where N = 4).  With 10,000 authors it would be 10,001 round trips.

-- ============================================
-- FIX 1: ONE JOIN (1 query)
-- ============================================

SELECT a.id AS author_id, a.name, b.title
FROM authors a
LEFT JOIN books b ON b.author_id = a.id      -- LEFT keeps authors that have no books
ORDER BY a.id, b.id;

-- Measured: Com_select = 1
-- Result:
-- author_id | name    | title
-- ----------+---------+--------------------
-- 1         | Orwell  | 1984
-- 1         | Orwell  | Animal Farm
-- 2         | Austen  | Emma
-- 2         | Austen  | Persuasion
-- 2         | Austen  | Pride and Prejudice
-- 3         | Tolkien | The Hobbit
-- 4         | Rowling | Philosopher's Stone
-- (parent columns repeat per child: fine for small fan-out, wasteful for wide parents)

-- ============================================
-- FIX 2: BATCH WITH IN (2 queries total — what ORM "eager/prefetch" does)
-- ============================================

SELECT id, name FROM authors ORDER BY id;                         -- query 1
SELECT id, author_id, title FROM books
WHERE author_id IN (1, 2, 3, 4)                                   -- query 2: ids collected from query 1
ORDER BY author_id, id;
-- Result: all 7 books in one round trip; the app groups them by author_id in memory.
-- Cap the IN list (e.g. 500-1000 ids per batch) for very large pages.

-- ============================================
-- FIX 3: AGGREGATE CHILDREN INTO ONE ROW PER PARENT
-- ============================================

-- MySQL:
SELECT a.name, JSON_ARRAYAGG(b.title) AS titles
FROM authors a
JOIN books b ON b.author_id = a.id
GROUP BY a.id, a.name
ORDER BY a.id;

-- Result (MySQL 9.1; array order inside each group is not guaranteed by JSON_ARRAYAGG):
-- name    | titles
-- --------+----------------------------------------------
-- Orwell  | ["1984", "Animal Farm"]
-- Austen  | ["Emma", "Persuasion", "Pride and Prejudice"]
-- Tolkien | ["The Hobbit"]
-- Rowling | ["Philosopher's Stone"]

-- PostgreSQL (verified on PGlite; ORDER BY inside the aggregate makes the order deterministic):
SELECT a.name, json_agg(b.title ORDER BY b.id) AS titles
FROM authors a
JOIN books b ON b.author_id = a.id
GROUP BY a.id, a.name
ORDER BY a.id;
-- Result: same four rows, e.g. Austen -> ["Emma","Persuasion","Pride and Prejudice"]
```

---

## 🔍 Why This Works (3 lines max)
Each query has fixed overhead (network round trip, parsing, planning, connection checkout), so 1 + N small queries cost far more than 1 or 2 set-based queries even when every query is index-fast. Set-based SQL lets the database do the matching in one pass.
हिंदी: हर query का network और parse overhead होता है; set-based एक query सैकड़ों छोटी queries से बहुत तेज़ है।

---

## ⚡ Alternative Solution

```sql
-- Detect N+1 in production:
-- MySQL: top statements by call count
SELECT DIGEST_TEXT, COUNT_STAR, ROUND(SUM_TIMER_WAIT/1e12, 3) AS total_sec
FROM performance_schema.events_statements_summary_by_digest
ORDER BY COUNT_STAR DESC LIMIT 10;
-- Same SELECT ... WHERE author_id = ? with a huge COUNT_STAR and tiny avg time = N+1 signature.

-- PostgreSQL: pg_stat_statements extension (not available in PGlite, so not run here)
-- SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY calls DESC LIMIT 10;

-- ORM equivalents (application side):
--   Django: select_related() (JOIN) / prefetch_related() (IN batch)
--   Hibernate/JPA: JOIN FETCH or @BatchSize
--   Rails: includes()/preload();   Sequelize: include;   SQLAlchemy: joinedload()/selectinload()
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "it's fast, each query takes 0.3 ms" -> ignores 10,001 round trips and pool exhaustion
-- ❌ Wrong: JOIN-fetching two one-to-many children at once (authors -> books AND awards)
--   rows multiply (books x awards) = cartesian explosion. Use separate batch queries instead.
-- ❌ Wrong: no index on the child FK (books.author_id): each of the N lookups scans the table.
-- ✅ Correct: index the FK, batch with IN or JOIN, verify with query counts / pg_stat_statements.
```

---

## 🎯 Interview Tip (1 line)
Say: "N+1 is a round-trip problem, not a slow-query problem — I spot it by a high call count of an identical parameterised query, fix it with a JOIN or a two-query IN batch (select_related/prefetch_related style), always index the foreign key, and avoid joining two to-many relations in one query."

---

## 🔗 Related Questions
→ Q229 (optimize a slow query) | Q234 (connection pooling) | Q235 (INNER vs LEFT JOIN) | Q005 (IN vs EXISTS)
