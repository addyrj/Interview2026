---

# Q051. Hierarchies with hierarchyid
# Category: Joins, Subqueries & CTEs
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server / Azure SQL (hierarchyid has no MySQL/PostgreSQL equivalent; PostgreSQL offers the ltree extension)

---

## ❓ Question
Store an org chart with the `hierarchyid` data type instead of a ManagerId column. Insert the root and children, list the whole tree with its level and path, find all descendants of a manager, and explain when hierarchyid is better or worse than a ManagerId + recursive CTE.

---

## 💡 Quick Concept (2 lines only)
`hierarchyid` is a compact binary path (like `/1/2/`) with methods such as `GetRoot()`, `GetDescendant()`, `GetLevel()`, `IsDescendantOf()`, `ToString()`. Subtree queries become range seeks on an index, but YOU must maintain the paths (it does not enforce uniqueness or a valid tree by itself).
हिंदी: hierarchyid एक path है (जैसे /1/2/) और methods से level/descendants निकलते हैं। Subtree query तेज़ है, पर path सही रखना आपकी ज़िम्मेदारी है।

---

## ✅ Answer / Solution

NOTE: hierarchyid cannot be run on SQLite, MySQL or PGlite. Nothing below was executed on SQL Server; behaviour is per Microsoft docs, and the outputs are only the paths implied by the values inserted.

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE OrgNodes (
  NodeId   HIERARCHYID   NOT NULL PRIMARY KEY,
  Name     VARCHAR(100)  NOT NULL,
  Title    VARCHAR(50)   NOT NULL,
  Lvl      AS NodeId.GetLevel()          -- computed column, handy for a breadth-first index
);

-- Root
INSERT INTO OrgNodes (NodeId, Name, Title)
VALUES (hierarchyid::GetRoot(), 'Meera', 'CEO');            -- path '/'

-- Children: use explicit paths (simple and deterministic for a demo)
INSERT INTO OrgNodes (NodeId, Name, Title) VALUES
  (hierarchyid::Parse('/1/'),   'Rohan',  'CTO'),
  (hierarchyid::Parse('/2/'),   'Anita',  'CFO'),
  (hierarchyid::Parse('/1/1/'), 'Vikram', 'Eng Manager'),
  (hierarchyid::Parse('/1/2/'), 'Sneha',  'Eng Manager'),
  (hierarchyid::Parse('/1/1/1/'), 'Arjun', 'Developer');

-- Adding a new child under a given parent without hard-coding the number:
DECLARE @parent HIERARCHYID = hierarchyid::Parse('/1/1/');
DECLARE @lastChild HIERARCHYID;

BEGIN TRANSACTION;
  SELECT @lastChild = MAX(NodeId)
  FROM OrgNodes WITH (UPDLOCK, HOLDLOCK)        -- serialize concurrent inserts under the same parent
  WHERE NodeId.GetAncestor(1) = @parent;

  INSERT INTO OrgNodes (NodeId, Name, Title)
  VALUES (@parent.GetDescendant(@lastChild, NULL), 'Pooja', 'Developer');   -- becomes /1/1/2/
COMMIT TRANSACTION;

-- ============================================
-- WHOLE TREE WITH LEVEL AND PATH
-- ============================================
SELECT NodeId.ToString() AS Path, NodeId.GetLevel() AS Lvl, Name, Title
FROM OrgNodes
ORDER BY NodeId;                                  -- sorts in depth-first order

-- EXPECTED OUTPUT (paths and levels follow from the inserted values; not executed on SQL Server):
-- Path     | Lvl | Name   | Title
-- /        | 0   | Meera  | CEO
-- /1/      | 1   | Rohan  | CTO
-- /1/1/    | 2   | Vikram | Eng Manager
-- /1/1/1/  | 3   | Arjun  | Developer
-- /1/1/2/  | 3   | Pooja  | Developer
-- /1/2/    | 2   | Sneha  | Eng Manager
-- /2/      | 1   | Anita  | CFO

-- ============================================
-- ALL DESCENDANTS OF ROHAN (/1/)
-- ============================================
DECLARE @rohan HIERARCHYID = hierarchyid::Parse('/1/');

SELECT Name, NodeId.ToString() AS Path
FROM OrgNodes
WHERE NodeId.IsDescendantOf(@rohan) = 1
  AND NodeId <> @rohan                            -- IsDescendantOf returns 1 for the node itself
ORDER BY NodeId;
-- Expected rows: Vikram, Arjun, Pooja, Sneha (everything under /1/ except Rohan).
```

---

## 🔍 Why This Works (3 lines max)
hierarchyid encodes the full path in the key, so "all descendants" is a range on the clustered key (depth-first order) instead of a recursive join per level. `GetDescendant(a, b)` generates a new child value between two siblings, and `IsDescendantOf` tests path containment. The cost: moving a subtree means rewriting every path below it (`GetReparentedValue`).
हिंदी: Path key में ही है, इसलिए descendants = एक range scan, recursion नहीं। Subtree move करना महंगा है क्योंकि नीचे के सारे paths बदलते हैं।

---

## ⚡ Alternative Solution

```sql
-- ManagerId + recursive CTE (Q043): simpler, enforces integrity with a foreign key,
-- easy to move a node (change one ManagerId), works on every database and ORM.
-- Add an index on ManagerId so each recursion step is a seek.
CREATE INDEX IX_Employees_ManagerId ON Employees (ManagerId) INCLUDE (Name);

-- Depth-first vs breadth-first index options for hierarchyid (per Microsoft docs):
CREATE UNIQUE INDEX IX_OrgNodes_Lvl ON OrgNodes (Lvl, NodeId);   -- breadth-first (all nodes of one level)
-- The primary key on NodeId itself is the depth-first index (subtree locality).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming hierarchyid keeps the tree valid
INSERT INTO OrgNodes (NodeId, Name, Title) VALUES (hierarchyid::Parse('/9/9/'), 'Ghost', 'None');
-- No parent /9/ exists, and nothing stops this. You need a constraint/trigger or a procedure
-- that always builds children through GetDescendant from an existing parent.

-- ❌ Wrong: two sessions calling GetDescendant under the same parent without a lock
-- They can compute the same value (duplicate path). Use a transaction with UPDLOCK/HOLDLOCK or a unique key on NodeId (PRIMARY KEY above).

-- ❌ Wrong: choosing hierarchyid for a tree that is reorganised often or needs foreign-key integrity.
-- ❌ Wrong: forgetting IsDescendantOf includes the node itself.
```

---

## 🎯 Interview Tip (1 line)
Say: "hierarchyid is best for large, read-heavy trees where subtree queries dominate (bill of materials, org charts, folder paths) — descendants become an index range. For small or frequently re-parented trees I use ManagerId with a recursive CTE because the foreign key keeps it valid and moves are one-row updates. I also state that I would benchmark both for the real workload."

---

## 🔗 Related Questions
→ Q043 (recursive CTE) | Q025 (CREATE TABLE with constraints) | Q029 (computed columns) | Q102 (clustered vs non-clustered index)
