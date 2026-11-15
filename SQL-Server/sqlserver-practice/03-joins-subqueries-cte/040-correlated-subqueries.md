---

# Q040. Correlated Subqueries
# Category: Joins, Subqueries + CTEs
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (same in MySQL/PostgreSQL)

---

## ❓ Question
(a) Find orders larger than that customer's own average order. (b) Show each customer's latest order date as a column. (c) Return each customer's latest order row. When is a correlated subquery slow, and what replaces it?

---

## 💡 Quick Concept (2 lines only)
A correlated subquery references a column of the outer query, so logically it is evaluated once per outer row. The optimizer often rewrites it into a join or semi-join, but not always, and a bad one can degrade to row-by-row work.
हिंदी: Correlated subquery outer query के column को use करती है, यानी logically हर row के लिए चलती है। Optimizer अक्सर इसे join में बदल देता है, पर हमेशा नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Customers (CustomerId INT PRIMARY KEY, Name VARCHAR(50));
CREATE TABLE Orders (
    OrderId INT PRIMARY KEY, CustomerId INT NULL, OrderDate DATE, Amount DECIMAL(10,2)
);
INSERT INTO Customers VALUES (1,'Asha'),(2,'Rohan'),(3,'Meera'),(4,'Kabir');
INSERT INTO Orders VALUES
  (101,1,'2024-01-05',250.00),(102,1,'2024-02-10',120.00),(103,2,'2024-02-11',99.50),
  (104,NULL,'2024-03-01',75.00),(105,3,'2024-03-15',410.00),(106,2,'2024-04-01',60.00);

-- ============================================
-- SOLUTION
-- ============================================
-- (a) Orders above the customer's own average
SELECT o.OrderId, o.CustomerId, o.Amount
FROM Orders o
WHERE o.Amount > (SELECT AVG(o2.Amount) FROM Orders o2 WHERE o2.CustomerId = o.CustomerId)
ORDER BY o.OrderId;

-- (b) Latest order date per customer, as a column (NULL when none)
SELECT c.Name,
       (SELECT MAX(o.OrderDate) FROM Orders o WHERE o.CustomerId = c.CustomerId) AS LastOrder
FROM Customers c
ORDER BY c.CustomerId;

-- (c) The full latest-order row per customer
SELECT o.CustomerId, o.OrderId, o.Amount
FROM Orders o
WHERE o.OrderDate = (SELECT MAX(x.OrderDate) FROM Orders x WHERE x.CustomerId = o.CustomerId)
ORDER BY o.CustomerId;

-- ============================================
-- EXPECTED OUTPUT (result derived from equivalent queries on SQLite; not executed on SQL Server)
-- ============================================
-- (a) 101 | 1 | 250.00      (Asha avg 185 -> 250 > 185)
--     103 | 2 |  99.50      (Rohan avg 79.75 -> 99.50 > 79.75)
--     (order 104 has NULL CustomerId: AVG of an empty set is NULL -> comparison UNKNOWN -> excluded)
-- (b) Asha  | 2024-02-10
--     Rohan | 2024-04-01
--     Meera | 2024-03-15
--     Kabir | NULL
-- (c) 1 | 102 | 120.00
--     2 | 106 |  60.00
--     3 | 105 | 410.00
```

---

## 🔍 Why This Works (3 lines max)
For each outer row the inner query is parameterized by the outer column (o.CustomerId), so the aggregate is computed within that customer's rows. In (c), ties on the max date would return several rows per customer. With an index on (CustomerId, OrderDate) each inner lookup is a tiny seek, and the optimizer may turn it into an aggregate join anyway.
हिंदी: Outer row की value inner query में जाती है, इसलिए हर customer का अपना aggregate बनता है। Index हो तो हर lookup छोटा seek होता है।

---

## ⚡ Alternative Solution

```sql
-- Window function: one pass over Orders, usually faster for (a) and (c)
SELECT OrderId, CustomerId, Amount
FROM (SELECT *, AVG(Amount) OVER (PARTITION BY CustomerId) AS CustAvg FROM Orders) t
WHERE Amount > CustAvg
ORDER BY OrderId;

-- Latest row per customer with a deterministic tiebreaker
SELECT CustomerId, OrderId, Amount
FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY CustomerId ORDER BY OrderDate DESC, OrderId DESC) AS rn
      FROM Orders) t
WHERE rn = 1 AND CustomerId IS NOT NULL;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Forgetting the correlation: compares to the GLOBAL average, not the customer's
SELECT * FROM Orders WHERE Amount > (SELECT AVG(Amount) FROM Orders);

-- ❌ Ties: two orders on the same max date both come back in (c); add a tiebreaker if you want one row
-- ❌ Correlated subquery in the SELECT list over millions of rows with no index on the join column
--    -> repeated scans. Check the plan for a Nested Loops with a scan on the inner side.
-- ❌ Expecting NULL-keyed rows to match: o2.CustomerId = o.CustomerId is never true for NULL.
```

---

## 🎯 Interview Tip (1 line)
Say: "Correlated subqueries read nicely and are fine when they are indexed and the optimizer unnests them, but for per-group aggregates I usually prefer a window function or APPLY, and I always verify with the execution plan and STATISTICS IO rather than assuming." Mention that a correlated EXISTS is the efficient semi-join form.

---

## 🔗 Related Questions
→ Q039 (Subqueries) | Q038 (CROSS APPLY) | Q047 (Top N per group) | Q056 (ROW_NUMBER, RANK, DENSE_RANK)
