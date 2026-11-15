---

# Q039. Subqueries — Scalar, IN, EXISTS
# Category: Joins, Subqueries + CTEs
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (same semantics in MySQL/PostgreSQL, including the NOT IN NULL trap)

---

## ❓ Question
Using Customers and Orders: (a) show each order next to the overall average amount (scalar subquery), (b) customers with an order above 100 (IN), (c) customers with any order (EXISTS), (d) customers with no orders — and explain why the NOT IN version returns nothing here.

---

## 💡 Quick Concept (2 lines only)
A scalar subquery returns exactly one value; IN compares against a list of values; EXISTS only checks whether any row exists. NOT IN returns no rows if the list contains even one NULL (three-valued logic); NOT EXISTS does not have this problem.
हिंदी: Scalar = एक value, IN = list में है या नहीं, EXISTS = कोई row है या नहीं। List में एक भी NULL हो तो NOT IN कुछ नहीं लौटाता — NOT EXISTS use करो।

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
INSERT INTO Customers VALUES (1,'Asha','Pune'),(2,'Rohan','Delhi'),(3,'Meera','Mumbai'),(4,'Kabir','Pune');
INSERT INTO Orders VALUES
  (101,1,'2024-01-05',250.00),(102,1,'2024-02-10',120.00),(103,2,'2024-02-11',99.50),
  (104,NULL,'2024-03-01',75.00),(105,3,'2024-03-15',410.00),(106,2,'2024-04-01',60.00);

-- ============================================
-- SOLUTION
-- ============================================
-- (a) Scalar subquery: must return one row, one column
SELECT OrderId, Amount, (SELECT AVG(Amount) FROM Orders) AS AvgAmount
FROM Orders ORDER BY OrderId;

-- (b) IN
SELECT Name FROM Customers
WHERE CustomerId IN (SELECT CustomerId FROM Orders WHERE Amount > 100)
ORDER BY Name;

-- (c) EXISTS
SELECT Name FROM Customers c
WHERE EXISTS (SELECT 1 FROM Orders o WHERE o.CustomerId = c.CustomerId)
ORDER BY Name;

-- (d) customers with NO orders
SELECT Name FROM Customers c
WHERE NOT EXISTS (SELECT 1 FROM Orders o WHERE o.CustomerId = c.CustomerId);   -- correct

SELECT Name FROM Customers
WHERE CustomerId NOT IN (SELECT CustomerId FROM Orders);                       -- returns nothing!

-- ============================================
-- EXPECTED OUTPUT (result derived from equivalent queries on SQLite; not executed on SQL Server)
-- ============================================
-- (a) AvgAmount = 169.083333... on every row (SQL Server shows DECIMAL scale, e.g. 169.083333)
--     101 250.00 | 102 120.00 | 103 99.50 | 104 75.00 | 105 410.00 | 106 60.00
-- (b) Asha, Meera
-- (c) Asha, Meera, Rohan
-- (d) NOT EXISTS -> Kabir
--     NOT IN     -> (0 rows) because order 104 has CustomerId NULL
```

---

## 🔍 Why This Works (3 lines max)
`x NOT IN (1, 2, NULL)` expands to `x<>1 AND x<>2 AND x<>NULL`, and the last term is UNKNOWN, so the whole predicate is never TRUE. EXISTS tests row presence and ignores the select list, so SELECT 1 / SELECT * make no difference. A scalar subquery that returns more than one row fails at runtime with an error.
हिंदी: `NOT IN` में NULL आते ही पूरा predicate UNKNOWN हो जाता है, इसलिए कोई row नहीं मिलती। EXISTS इस जाल से बचाता है।

---

## ⚡ Alternative Solution

```sql
-- NOT IN made safe by filtering NULLs (works, but NOT EXISTS is the idiom)
SELECT Name FROM Customers
WHERE CustomerId NOT IN (SELECT CustomerId FROM Orders WHERE CustomerId IS NOT NULL);

-- LEFT JOIN ... IS NULL anti-join
SELECT c.Name FROM Customers c
LEFT JOIN Orders o ON o.CustomerId = c.CustomerId WHERE o.OrderId IS NULL;

-- Scalar subquery alternative: window function avoids re-reading
SELECT OrderId, Amount, AVG(Amount) OVER () AS AvgAmount FROM Orders;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ NOT IN against a nullable column (shown above)
-- ❌ Scalar subquery returning many rows:
SELECT Name, (SELECT Amount FROM Orders o WHERE o.CustomerId = c.CustomerId) FROM Customers c;
-- Runtime error as soon as a customer has 2+ orders (subquery returned more than 1 value)
-- ✅ Aggregate it (MAX/SUM) or use TOP (1) ... ORDER BY.

-- ❌ Unqualified column name that exists only in the OUTER table silently binds to it:
SELECT Name FROM Customers WHERE CustomerId IN (SELECT City FROM Orders);
-- Orders has no City column, so City resolves to Customers.City (no error!) and the query
-- compares CustomerId with an outer column. Always alias-qualify columns inside subqueries.
```

---

## 🎯 Interview Tip (1 line)
Say: "I default to EXISTS / NOT EXISTS for presence checks because they are NULL-safe and the optimizer turns IN/EXISTS into the same semi-join in most cases. The NOT IN NULL trap is the one I always call out, and I qualify every column with an alias inside subqueries."

---

## 🔗 Related Questions
→ Q040 (Correlated subqueries) | Q041 (EXISTS vs IN vs JOIN) | Q053 (Anti-joins) | Q004 (NULL handling)
