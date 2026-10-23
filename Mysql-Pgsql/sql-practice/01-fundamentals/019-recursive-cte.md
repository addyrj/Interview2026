---

# Q019. Recursive CTE — Hierarchy + Tree Traversal
# Category: Fundamentals
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Write a recursive CTE to traverse an employee-manager hierarchy. How do you prevent infinite loops? Show how to find the full path from root to a node and calculate depth level.

---

## 💡 Quick Concept (2 lines only)
Recursive CTE has two parts: base case (anchor — the starting rows) + recursive case (references the CTE itself to walk the tree). UNION ALL connects them. MySQL and PostgreSQL syntax is nearly identical.
हिंदी: Recursive CTE = base case (starting rows) + recursive case (CTE खुद को reference करता है)। UNION ALL से connect करो। Infinite loop = MAXRECURSION limit से रोको।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP: Employee-Manager Hierarchy
-- ============================================

CREATE TABLE employees (
  id         INT PRIMARY KEY,
  name       VARCHAR(100),
  manager_id INT NULL,  -- NULL for top-level CEO
  dept       VARCHAR(50),
  salary     DECIMAL(10,2),
  FOREIGN KEY (manager_id) REFERENCES employees(id)
);

INSERT INTO employees VALUES
  (1,  'Alice (CEO)',     NULL, 'Exec', 200000),
  (2,  'Bob (CTO)',       1,    'Eng',  150000),
  (3,  'Carol (CFO)',     1,    'Fin',  140000),
  (4,  'Dave (Eng Lead)', 2,    'Eng',  120000),
  (5,  'Eve (Engineer)',  4,    'Eng',   90000),
  (6,  'Frank (Eng)',     4,    'Eng',   85000),
  (7,  'Grace (Analyst)', 3,    'Fin',   80000),
  (8,  'Heidi (Eng)',     2,    'Eng',   95000);

-- Hierarchy:
-- Alice (1)
--   ├── Bob (2)
--   │     ├── Dave (4)
--   │     │     ├── Eve (5)
--   │     │     └── Frank (6)
--   │     └── Heidi (8)
--   └── Carol (3)
--         └── Grace (7)

-- ============================================
-- BASIC RECURSIVE CTE: Full Org Chart
-- ============================================

WITH RECURSIVE org_tree AS (
  -- BASE CASE (anchor): start with the root (CEO, manager_id IS NULL)
  SELECT
    id,
    name,
    manager_id,
    0 AS depth,                          -- root is at depth 0
    CAST(name AS CHAR(500)) AS path      -- MySQL: CAST needed for varchar size
    -- PgSQL: name::text AS path
  FROM employees
  WHERE manager_id IS NULL               -- ← root node(s)

  UNION ALL

  -- RECURSIVE CASE: join each employee to their found manager
  SELECT
    e.id,
    e.name,
    e.manager_id,
    ot.depth + 1,                        -- increment depth
    CONCAT(ot.path, ' → ', e.name)       -- build path string
    -- PgSQL: ot.path || ' → ' || e.name
  FROM employees e
  JOIN org_tree ot ON e.manager_id = ot.id  -- ← join child to its parent in CTE
)
SELECT
  REPEAT('  ', depth) || name AS indented_name,  -- PgSQL
  -- MySQL: CONCAT(REPEAT('  ', depth), name) AS indented_name
  depth,
  path
FROM org_tree
ORDER BY path;

-- Output:
-- indented_name          | depth | path
-- Alice (CEO)            |  0    | Alice (CEO)
--   Bob (CTO)            |  1    | Alice (CEO) → Bob (CTO)
--     Dave (Eng Lead)    |  2    | Alice (CEO) → Bob (CTO) → Dave (Eng Lead)
--       Eve (Engineer)   |  3    | Alice (CEO) → Bob (CTO) → Dave (Eng Lead) → Eve (Engineer)
--       Frank (Eng)      |  3    | Alice (CEO) → Bob (CTO) → Dave (Eng Lead) → Frank (Eng)
--     Heidi (Eng)        |  2    | Alice (CEO) → Bob (CTO) → Heidi (Eng)
--   Carol (CFO)          |  1    | Alice (CEO) → Carol (CFO)
--     Grace (Analyst)    |  2    | Alice (CEO) → Carol (CFO) → Grace (Analyst)

-- ============================================
-- FIND ALL REPORTS UNDER A MANAGER (Subtree)
-- ============================================

-- Everyone under Bob (id=2), including all levels down:
WITH RECURSIVE reports AS (
  -- Base: start with Bob
  SELECT id, name, manager_id, 0 AS depth
  FROM employees
  WHERE id = 2                           -- ← starting manager

  UNION ALL

  -- Recursive: find direct reports of each found employee
  SELECT e.id, e.name, e.manager_id, r.depth + 1
  FROM employees e
  JOIN reports r ON e.manager_id = r.id  -- e's manager is in the CTE
)
SELECT id, name, depth
FROM reports
ORDER BY depth, name;

-- Output (includes Bob himself + all under him):
-- id | name          | depth
--  2 | Bob (CTO)     | 0
--  4 | Dave          | 1
--  8 | Heidi         | 1
--  5 | Eve           | 2
--  6 | Frank         | 2

-- To exclude the starting manager (just direct + indirect reports):
WHERE id != 2  -- add to outer SELECT

-- ============================================
-- FIND PATH FROM NODE UP TO ROOT (Bottom-Up)
-- ============================================

-- Find the management chain for Eve (id=5):
WITH RECURSIVE chain AS (
  -- Base: start with Eve
  SELECT id, name, manager_id, 0 AS level
  FROM employees WHERE id = 5

  UNION ALL

  -- Recursive: go UP to parent
  SELECT e.id, e.name, e.manager_id, c.level + 1
  FROM employees e
  JOIN chain c ON e.id = c.manager_id   -- e is the PARENT of current node
)
SELECT id, name, level
FROM chain
ORDER BY level DESC;  -- CEO first, Eve last

-- Output:
-- id | name           | level
--  1 | Alice (CEO)    | 3     ← root (highest level number = lowest in hierarchy)
--  2 | Bob (CTO)      | 2
--  4 | Dave (Eng Lead)| 1
--  5 | Eve (Engineer) | 0     ← starting point

-- ============================================
-- AGGREGATE BY SUBTREE (Total salary under each manager)
-- ============================================

WITH RECURSIVE subtree AS (
  SELECT id, id AS root_id FROM employees  -- each employee is root of their own subtree

  UNION ALL

  SELECT e.id, s.root_id
  FROM employees e
  JOIN subtree s ON e.manager_id = s.id   -- expand each subtree down
)
SELECT
  r.id AS manager_id,
  r.name AS manager_name,
  COUNT(s.id) - 1 AS team_size,     -- -1 to exclude self
  SUM(e.salary) - r.salary AS team_budget  -- total salary minus own salary
FROM subtree s
JOIN employees e ON s.id = e.id
JOIN employees r ON s.root_id = r.id
GROUP BY r.id, r.name, r.salary
ORDER BY team_size DESC;

-- ============================================
-- PREVENTING INFINITE LOOPS
-- ============================================

-- If data has circular references (e.g., employee A's manager = B, B's manager = A):
-- → Recursive CTE will loop forever (or until max recursion limit)

-- MySQL: default max recursion depth = 1000
-- PgSQL: default = unlimited! Must add cycle detection manually

-- MySQL: set max recursion:
SET SESSION cte_max_recursion_depth = 100;
WITH RECURSIVE ... SELECT ...;

-- PgSQL (14+): CYCLE clause — automatic cycle detection:
WITH RECURSIVE org_tree AS (
  SELECT id, name, manager_id FROM employees WHERE manager_id IS NULL
  UNION ALL
  SELECT e.id, e.name, e.manager_id
  FROM employees e JOIN org_tree ot ON e.manager_id = ot.id
)
CYCLE id SET is_cycle USING cycle_path  -- ← PgSQL 14+ syntax
SELECT * FROM org_tree WHERE NOT is_cycle;
-- is_cycle = true when a cycle is detected → filter them out

-- PgSQL (pre-14): Manual cycle detection with array:
WITH RECURSIVE org_tree AS (
  SELECT id, name, manager_id, ARRAY[id] AS visited
  FROM employees WHERE manager_id IS NULL

  UNION ALL

  SELECT e.id, e.name, e.manager_id, ot.visited || e.id
  FROM employees e JOIN org_tree ot ON e.manager_id = ot.id
  WHERE e.id != ALL(ot.visited)  -- ← skip if already visited!
)
SELECT * FROM org_tree;

-- MySQL: Add depth limit as safeguard:
WHERE depth < 100  -- in the recursive case, stop at depth 100
```

---

## 🔍 Why This Works (3 lines max)
Recursive CTEs work by repeatedly joining the CTE back to itself: starting rows (anchor) feed into the recursive step, which produces new rows that become the input for the next iteration — stops when no new rows are produced. The depth counter and path concatenation are carried forward in each iteration by including them in the SELECT of the recursive part. Cycle detection is critical for real-world data that may have circular references.
हिंदी: Recursive CTE हर iteration में नए rows produce करता है जब तक नए rows नहीं मिलते। Depth और path हर step में carry होते हैं। Cycle detection = real data के लिए जरूरी।

---

## ⚡ Alternative Solution

```sql
-- Closure table approach (alternative to recursive CTE for heavily-queried hierarchies):
-- Pre-compute all ancestor-descendant pairs:
CREATE TABLE org_closure (
  ancestor_id   INT,
  descendant_id INT,
  depth         INT,
  PRIMARY KEY (ancestor_id, descendant_id)
);
-- Populate via recursive CTE once, update via triggers
-- Query: SELECT * FROM employees WHERE id IN (
--   SELECT descendant_id FROM org_closure WHERE ancestor_id = 2
-- );
-- No recursion at query time — pure index lookup! Best for read-heavy trees.

-- Materialized path (simpler for read-only hierarchies):
ALTER TABLE employees ADD COLUMN path VARCHAR(500);
UPDATE employees SET path = '1/2/4/5' WHERE id = 5;  -- store full path
-- Find all under Bob (path starts with '1/2'):
SELECT * FROM employees WHERE path LIKE '1/2/%';
-- Index on path → fast lookups, but updates are expensive
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: UNION instead of UNION ALL in recursive CTE
WITH RECURSIVE tree AS (
  SELECT id FROM employees WHERE manager_id IS NULL
  UNION  -- ← WRONG! UNION deduplicates — causes performance issues and may terminate early
  SELECT e.id FROM employees e JOIN tree t ON e.manager_id = t.id
)
-- ✅ Fix: Always UNION ALL in recursive CTEs

-- ❌ Wrong: Selecting columns in recursive part that don't exist in anchor
WITH RECURSIVE tree AS (
  SELECT id, name, 0 AS depth FROM employees WHERE manager_id IS NULL
  UNION ALL
  SELECT e.id, e.name, e.dept, t.depth + 1  -- ← e.dept not in anchor SELECT!
  FROM employees e JOIN tree t ON e.manager_id = t.id
)
-- ERROR: column count mismatch!
-- ✅ Both parts must have same column count and compatible types

-- ❌ Wrong: Not handling NULL manager_id in OUTER query
-- The root node (WHERE manager_id IS NULL) appears once in base case
-- But if you filter WHERE manager_id IS NOT NULL later, root disappears!
-- Always check what your base case anchor includes

-- ❌ Wrong: Forgetting indexes on the join column
-- WITH RECURSIVE ... JOIN employees e ON e.manager_id = t.id
-- Needs INDEX on manager_id for efficient joins!
CREATE INDEX idx_manager ON employees(manager_id);
```

---

## 🎯 Interview Tip (1 line)
Say: "Recursive CTEs have two parts: an anchor (starting rows) and a recursive step joined to the CTE with UNION ALL — they stop when the recursive step produces no new rows. I always add a depth counter as a safeguard against circular references, and in PgSQL 14+ I use the CYCLE clause for automatic cycle detection. For read-heavy hierarchies I prefer a closure table — no recursion at query time."

---

## 🔗 Related Questions
→ Q017 (CTE basics) | Q018 (nested set model) | Q020 (adjacency list vs closure table) | Q081 (B-Tree indexes)
