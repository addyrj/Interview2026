---

# Q149. Hierarchical Data — Adjacency List vs Nested Set vs Closure Table
# Category: Schema Design
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite

---

## ❓ Question
Model a product category tree (Electronics > Laptops > Gaming Laptops, ...). Show the three classic designs and fetch (a) all descendants of Electronics and (b) the breadcrumb (ancestors) of Gaming Laptops with each.

---

## 💡 Quick Concept (2 lines only)
Adjacency list stores only parent_id (simple writes, needs recursive CTE to read). Nested set stores lft/rgt numbers (fast reads, painful writes). Closure table stores every ancestor-descendant pair (fast reads, moderate storage, easy writes).
हिंदी: Adjacency = सिर्फ parent_id (write आसान), Nested set = lft/rgt (read तेज़, write भारी), Closure = सारे ancestor-descendant pairs (दोनों balanced)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE categories (
  id        INT PRIMARY KEY,
  name      VARCHAR(50) NOT NULL,
  parent_id INT NULL,
  FOREIGN KEY (parent_id) REFERENCES categories(id)
);
INSERT INTO categories VALUES
  (1,'Electronics',NULL),(2,'Laptops',1),(3,'Phones',1),
  (4,'Gaming Laptops',2),(5,'Ultrabooks',2),(6,'Books',NULL);

-- ============================================
-- 1) ADJACENCY LIST — recursive CTE (MySQL 8.0+, all PgSQL)
-- ============================================

-- (a) all descendants of Electronics
WITH RECURSIVE subtree AS (
  SELECT id, name, parent_id, 0 AS depth FROM categories WHERE id = 1
  UNION ALL
  SELECT c.id, c.name, c.parent_id, s.depth + 1
  FROM categories c JOIN subtree s ON c.parent_id = s.id
)
SELECT id, name, depth FROM subtree ORDER BY depth, id;
-- id | name           | depth
-- 1  | Electronics    | 0
-- 2  | Laptops        | 1
-- 3  | Phones         | 1
-- 4  | Gaming Laptops | 2
-- 5  | Ultrabooks     | 2

-- (b) breadcrumb of Gaming Laptops (walk UP)
WITH RECURSIVE ancestors AS (
  SELECT id, name, parent_id FROM categories WHERE id = 4
  UNION ALL
  SELECT c.id, c.name, c.parent_id FROM categories c JOIN ancestors a ON c.id = a.parent_id
)
SELECT id, name FROM ancestors;
-- 4 Gaming Laptops | 2 Laptops | 1 Electronics

-- ============================================
-- 2) NESTED SET — subtree = lft BETWEEN parent.lft AND parent.rgt
-- ============================================

CREATE TABLE categories_ns (
  id INT PRIMARY KEY, name VARCHAR(50) NOT NULL, lft INT NOT NULL, rgt INT NOT NULL,
  INDEX (lft, rgt)
);
INSERT INTO categories_ns VALUES
  (1,'Electronics',1,10),(2,'Laptops',2,7),(4,'Gaming Laptops',3,4),
  (5,'Ultrabooks',5,6),(3,'Phones',8,9),(6,'Books',11,12);

SELECT child.id, child.name
FROM categories_ns parent
JOIN categories_ns child ON child.lft BETWEEN parent.lft AND parent.rgt
WHERE parent.id = 1 AND child.id <> parent.id ORDER BY child.lft;
-- 2 Laptops | 4 Gaming Laptops | 5 Ultrabooks | 3 Phones     (no recursion!)

SELECT a.id, a.name FROM categories_ns a
JOIN categories_ns n ON n.lft BETWEEN a.lft AND a.rgt
WHERE n.id = 4 AND a.id <> n.id ORDER BY a.lft;
-- 1 Electronics | 2 Laptops

-- ============================================
-- 3) CLOSURE TABLE — one row per (ancestor, descendant) incl. itself at depth 0
-- ============================================

CREATE TABLE category_closure (
  ancestor_id   INT NOT NULL,
  descendant_id INT NOT NULL,
  depth         INT NOT NULL,
  PRIMARY KEY (ancestor_id, descendant_id),
  INDEX (descendant_id)
);
INSERT INTO category_closure VALUES
  (1,1,0),(2,2,0),(3,3,0),(4,4,0),(5,5,0),(6,6,0),
  (1,2,1),(1,3,1),(2,4,1),(2,5,1),(1,4,2),(1,5,2);

SELECT c.id, c.name, cc.depth FROM category_closure cc
JOIN categories c ON c.id = cc.descendant_id
WHERE cc.ancestor_id = 1 AND cc.depth > 0 ORDER BY cc.depth, c.id;
-- 2 Laptops 1 | 3 Phones 1 | 4 Gaming Laptops 2 | 5 Ultrabooks 2

-- Insert a new leaf "Tablets" under Phones (id 3): copy parent's ancestor rows, +1 depth
INSERT INTO categories VALUES (7,'Tablets',3);
INSERT INTO category_closure
SELECT ancestor_id, 7, depth + 1 FROM category_closure WHERE descendant_id = 3
UNION ALL SELECT 7, 7, 0;

SELECT ancestor_id, descendant_id, depth FROM category_closure WHERE descendant_id = 7 ORDER BY depth;
-- ancestor_id | descendant_id | depth
-- 7           | 7             | 0
-- 3           | 7             | 1
-- 1           | 7             | 2
```

---

## 🔍 Why This Works (3 lines max)
Adjacency needs one recursive step per level but writes touch one row. Nested set encodes the whole subtree as a numeric interval so reads are one range scan, but any insert renumbers lft/rgt of many rows. Closure table trades extra rows (N x avg depth) for join-only reads and cheap inserts.
हिंदी: Adjacency = write सस्ता, read recursive; Nested set = read सस्ता, write महंगा; Closure = extra storage देकर दोनों आसान।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL: ltree extension (materialized path) — not available in PGlite, not run
CREATE EXTENSION ltree;
CREATE TABLE categories_path (id INT PRIMARY KEY, path ltree);
CREATE INDEX ON categories_path USING GIST (path);
SELECT * FROM categories_path WHERE path <@ 'electronics';   -- all descendants

-- MySQL / any DB: materialized path string
-- path = '/1/2/4/'  ->  descendants: WHERE path LIKE '/1/2/%'  (prefix LIKE can use an index)

-- Both recursive-CTE queries above ran unchanged on MySQL 9.1 and PGlite.
-- MySQL < 8.0 has no recursive CTE: use nested set, closure table or a stored procedure loop.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: app-side loop, one query per level (N+1 queries for a tree)
-- SELECT * FROM categories WHERE parent_id = 1;  then for each child ... again ...

-- ❌ Wrong: recursive CTE with UNION on a graph that can contain cycles -> infinite loop
-- ✅ Add a depth limit (WHERE s.depth < 10), or in PgSQL use CYCLE clause (v14+),
--    and enforce "no cycles" in the write path. MySQL stops with cte_max_recursion_depth (default 1000).

-- ❌ Wrong: nested set for a tree that is edited constantly (every insert renumbers half the table)
```

---

## 🎯 Interview Tip (1 line)
Say: "For a mostly-read tree I'd use a closure table; for a small or write-heavy tree adjacency list plus a recursive CTE is enough; nested set only for near-static trees — and I'd mention the trade-off: write cost vs read cost vs storage."

---

## 🔗 Related Questions
→ Q172 (MySQL 8 CTEs) | Q147 (Multi-tenancy) | Q152 (EAV) | Q239 (Interview classics: self-join patterns)
