---

# Q041. EXISTS vs IN vs JOIN — Performance
# Category: Joins, Subqueries + CTEs
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL 8 and PostgreSQL also convert IN/EXISTS to semi-joins)

---

## ❓ Question
"Customers who have placed at least one order" can be written with EXISTS, IN or a JOIN. Do they return the same rows? Which is faster in SQL Server, and which one silently duplicates rows?

---

## 💡 Quick Concept (2 lines only)
EXISTS and IN are semi-joins: they return each outer row at most once and stop at the first match. A JOIN returns one row per match, so a one-to-many join duplicates customers and needs DISTINCT. In modern SQL Server, EXISTS and IN usually get the same plan, so choose by correctness (NULLs) and readability.
हिंदी: EXISTS और IN semi-join हैं — हर customer एक ही बार आता है। JOIN में हर match पर एक row, इसलिए duplicates। ज़्यादातर case में EXISTS और IN का plan एक जैसा होता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Customers (CustomerId INT PRIMARY KEY, Name VARCHAR(50), City VARCHAR(50));
CREATE TABLE Orders (
    OrderId INT PRIMARY KEY, CustomerId INT NULL, OrderDate DATE, Amount DECIMAL(10,2)
);
CREATE INDEX IX_Orders_CustomerId ON Orders (CustomerId);   -- supports all three forms

INSERT INTO Customers VALUES (1,'Asha','Pune'),(2,'Rohan','Delhi'),(3,'Meera','Mumbai'),(4,'Kabir','Pune');
INSERT INTO Orders VALUES
  (101,1,'2024-01-05',250.00),(102,1,'2024-02-10',120.00),(103,2,'2024-02-11',99.50),
  (104,NULL,'2024-03-01',75.00),(105,3,'2024-03-15',410.00),(106,2,'2024-04-01',60.00);

-- ============================================
-- SOLUTION: same question, three shapes
-- ============================================
-- 1) EXISTS (semi-join, NULL-safe, my default)
SELECT c.Name FROM Customers c
WHERE EXISTS (SELECT 1 FROM Orders o WHERE o.CustomerId = c.CustomerId)
ORDER BY c.Name;

-- 2) IN (semi-join; fine for positive IN)
SELECT c.Name FROM Customers c
WHERE c.CustomerId IN (SELECT o.CustomerId FROM Orders o)
ORDER BY c.Name;

-- 3) JOIN: duplicates Asha and Rohan (2 orders each)
SELECT c.Name FROM Customers c JOIN Orders o ON o.CustomerId = c.CustomerId
ORDER BY c.CustomerId;

-- 3b) JOIN + DISTINCT fixes the duplicates, but adds a sort/aggregate step
SELECT DISTINCT c.Name FROM Customers c JOIN Orders o ON o.CustomerId = c.CustomerId
ORDER BY c.Name;

-- Measure it yourself (do not guess):
SET STATISTICS IO, TIME ON;
-- run each form, compare logical reads and the plan operator (Left Semi Join vs Hash/Merge Join + Distinct)

-- ============================================
-- EXPECTED OUTPUT (result derived from equivalent queries on SQLite; not executed on SQL Server)
-- ============================================
-- 1) Asha, Meera, Rohan
-- 2) Asha, Meera, Rohan
-- 3) Asha, Asha, Rohan, Rohan, Meera        (5 rows: duplicates!)
-- 3b) Asha, Meera, Rohan
-- Execution plans / reads are NOT shown: they depend on data volume and statistics and
-- were not run on SQL Server.
```

---

## 🔍 Why This Works (3 lines max)
The optimizer rewrites EXISTS and IN into a semi-join operator, which emits each left row once. A join has no such guarantee, so DISTINCT must be added and may cost a sort or hash aggregate. The real differences are NULL handling (NOT IN) and the index on the inner join column, not a magic "EXISTS is faster" rule.
हिंदी: Optimizer EXISTS/IN को semi-join में बदलता है। असली फर्क NULL handling और inner column पर index का है, "EXISTS हमेशा तेज़" एक myth है।

---

## ⚡ Alternative Solution

```sql
-- If you need columns from Orders as well, a JOIN is the right tool (not a semi-join):
SELECT c.Name, o.OrderId, o.Amount
FROM Customers c JOIN Orders o ON o.CustomerId = c.CustomerId;

-- If you need "has at least one big order" with the order data, use APPLY / ROW_NUMBER (Q038, Q047).
-- Anti-join counterpart: NOT EXISTS is preferred over NOT IN (Q039, Q053).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Using a JOIN for a presence check and getting duplicates, then "fixing" it with DISTINCT
--    everywhere, which hides a wrong join and costs a sort.

-- ❌ "EXISTS is always faster than IN" -- with an indexed inner column both usually compile to
--    the same semi-join; verify in the plan.

-- ❌ NOT IN on a nullable column (returns zero rows) -- Q039.
-- ❌ SELECT COUNT(*) FROM Customers c JOIN Orders o ... to count customers: counts orders instead.
```

---

## 🎯 Interview Tip (1 line)
Say: "They are logically equal for positive checks and the optimizer usually produces the same semi-join, so I pick EXISTS for NULL-safety and clarity, add a supporting index on the inner join column, and prove any claim with STATISTICS IO and the actual plan. A JOIN is for when I need the inner columns, and then I watch row multiplication."

---

## 🔗 Related Questions
→ Q039 (Subqueries) | Q053 (Anti-joins) | Q108 (SET STATISTICS IO and TIME) | Q107 (Reading an execution plan)
