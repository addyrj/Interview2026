---

# Q053. Anti-Joins — NOT EXISTS vs LEFT JOIN IS NULL vs the NOT IN Trap
# Category: Joins, Subqueries & CTEs
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (NULL semantics of NOT IN are identical in MySQL and PostgreSQL)

---

## ❓ Question
Find customers who have never placed an order. `Orders.CustomerId` is nullable and one order has a NULL customer (guest checkout). Show the three ways to write an anti-join and explain why `NOT IN` silently returns nothing.

---

## 💡 Quick Concept (2 lines only)
An anti-join returns rows with NO match: `NOT EXISTS`, `LEFT JOIN ... WHERE right.key IS NULL`, or `NOT IN`. `NOT IN` is dangerous: if the subquery returns even one NULL, the whole predicate becomes UNKNOWN and no rows come back.
हिंदी: Anti-join = जिनका match नहीं है। NOT IN में subquery का एक भी NULL हो तो result खाली आता है — यही trap है। NOT EXISTS सुरक्षित है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Customers (CustomerId INT PRIMARY KEY, Name VARCHAR(100) NOT NULL);
CREATE TABLE Orders    (OrderId INT PRIMARY KEY, CustomerId INT NULL);   -- NULL = guest order

INSERT INTO Customers (CustomerId, Name) VALUES
  (1, 'Asha'), (2, 'Bhavna'), (3, 'Chetan'), (4, 'Divya');

INSERT INTO Orders (OrderId, CustomerId) VALUES
  (10, 1), (11, 1), (12, 2), (13, NULL);      -- guest order with NULL customer

-- ============================================
-- 1) NOT EXISTS  (recommended)
-- ============================================
SELECT c.Name
FROM Customers AS c
WHERE NOT EXISTS (SELECT 1 FROM Orders AS o WHERE o.CustomerId = c.CustomerId)
ORDER BY c.Name;
-- EXPECTED OUTPUT (derived on SQLite): Chetan, Divya

-- ============================================
-- 2) LEFT JOIN ... IS NULL
-- ============================================
SELECT c.Name
FROM Customers AS c
LEFT JOIN Orders AS o ON o.CustomerId = c.CustomerId
WHERE o.OrderId IS NULL            -- test a NOT NULL column of the right table (the PK)
ORDER BY c.Name;
-- EXPECTED OUTPUT (derived on SQLite): Chetan, Divya

-- ============================================
-- 3) NOT IN  (the trap)
-- ============================================
SELECT Name
FROM Customers
WHERE CustomerId NOT IN (SELECT CustomerId FROM Orders);
-- EXPECTED OUTPUT (derived on SQLite, three-valued logic is standard SQL): ZERO ROWS
-- Why: 3 NOT IN (1, 1, 2, NULL)  ->  3<>1 AND 3<>1 AND 3<>2 AND 3<>NULL  ->  ... AND UNKNOWN  -> UNKNOWN -> row rejected

-- Fixed NOT IN: remove NULLs from the subquery
SELECT Name
FROM Customers
WHERE CustomerId NOT IN (SELECT CustomerId FROM Orders WHERE CustomerId IS NOT NULL)
ORDER BY Name;
-- EXPECTED OUTPUT (derived on SQLite): Chetan, Divya

-- Results derived from equivalent queries on SQLite; not executed on SQL Server.
-- Execution plans for these in SQL Server are often identical (anti semi join) when the columns
-- are NOT NULL; with nullable columns NOT IN needs extra NULL-handling work. No plan output is claimed here.
```

---

## 🔍 Why This Works (3 lines max)
`NOT EXISTS` only asks "is there a matching row?" and never compares against NULL, so NULLs in Orders cannot poison it. `LEFT JOIN` keeps every customer and fills the right side with NULLs when nothing matches, so `OrderId IS NULL` identifies the non-matches. `NOT IN` expands to a chain of `<>` comparisons joined by AND; one UNKNOWN makes the whole chain UNKNOWN.
हिंदी: NOT EXISTS सिर्फ "match है या नहीं" देखता है, NULL से फर्क नहीं पड़ता। NOT IN एक `<>` की chain है — एक UNKNOWN आया तो पूरी chain UNKNOWN।

---

## ⚡ Alternative Solution

```sql
-- EXCEPT also works when you only need the key (and it is NULL-safe: NULLs compare as equal):
SELECT CustomerId FROM Customers
EXCEPT
SELECT CustomerId FROM Orders;          -- returns 3 and 4 (NULL in Orders matches nothing in Customers)

-- Guard the root cause: make Orders.CustomerId NOT NULL (guest orders get a dedicated "Guest" customer row),
-- or always filter IS NOT NULL inside NOT IN. NOT EXISTS needs neither.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: LEFT JOIN with the filter in ON instead of WHERE
SELECT c.Name FROM Customers c
LEFT JOIN Orders o ON o.CustomerId = c.CustomerId AND o.OrderId IS NULL;
-- Returns ALL customers: the IS NULL test inside ON just changes which right rows match.

-- ❌ Wrong: testing a nullable column of the right table
WHERE o.CustomerId IS NULL    -- may be true because the ORDER itself has a NULL customer, not because of "no match"
-- ✅ Test the right table's primary key (never NULL in a real row).

-- ❌ Wrong: NOT IN on a nullable column "because it worked in testing" (no NULLs in the test data)
-- It breaks the day the first guest order is inserted.
```

---

## 🎯 Interview Tip (1 line)
Say: "I default to NOT EXISTS: it is NULL-safe and the optimizer turns it into an anti semi join. LEFT JOIN ... IS NULL is equivalent if I test the right table's primary key. I avoid NOT IN on nullable columns because one NULL makes the result empty — a bug that only shows up in production data."

---

## 🔗 Related Questions
→ Q039 (subqueries — scalar, IN, EXISTS) | Q041 (EXISTS vs IN vs JOIN performance) | Q004 (NULL handling) | Q044 (UNION, INTERSECT, EXCEPT)
