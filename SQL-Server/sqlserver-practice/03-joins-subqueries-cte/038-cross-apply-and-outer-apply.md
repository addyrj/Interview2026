---

# Q038. CROSS APPLY and OUTER APPLY
# Category: Joins, Subqueries + CTEs
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL 8.0.14+ and PostgreSQL use JOIN LATERAL; CROSS APPLY = INNER JOIN LATERAL, OUTER APPLY = LEFT JOIN LATERAL ... ON TRUE)

---

## ❓ Question
For each customer return their 2 most recent orders (top-N per group). Customers with no orders must still appear in a second version. Why can't a normal JOIN with TOP do this, and what else is APPLY used for?

---

## 💡 Quick Concept (2 lines only)
APPLY runs a right-side subquery or table-valued function once per row of the left side, and the right side may reference left-side columns. CROSS APPLY drops left rows that produce no right rows (like INNER); OUTER APPLY keeps them with NULLs (like LEFT).
हिंदी: APPLY = left की हर row के लिए right side चलता है, और उसमें left के columns use हो सकते हैं। CROSS APPLY = INNER जैसा, OUTER APPLY = LEFT जैसा।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Customers (CustomerId INT PRIMARY KEY, Name VARCHAR(50));
CREATE TABLE Orders (
    OrderId INT PRIMARY KEY, CustomerId INT, OrderDate DATE, Amount DECIMAL(10,2)
);
CREATE INDEX IX_Orders_Cust_Date ON Orders (CustomerId, OrderDate DESC) INCLUDE (Amount);

INSERT INTO Customers VALUES (1,'Asha'),(2,'Rohan'),(3,'Meera'),(4,'Kabir');
INSERT INTO Orders VALUES
  (101,1,'2024-01-05',250.00),(102,1,'2024-02-10',120.00),(107,1,'2024-03-20',80.00),
  (103,2,'2024-02-11', 99.50),(106,2,'2024-04-01', 60.00),
  (105,3,'2024-03-15',410.00);
-- Kabir has no orders.

-- ============================================
-- SOLUTION
-- ============================================
-- Top 2 most recent orders per customer (customers without orders disappear)
SELECT c.Name, t.OrderId, t.Amount
FROM Customers c
CROSS APPLY (
    SELECT TOP (2) o.OrderId, o.Amount
    FROM Orders o
    WHERE o.CustomerId = c.CustomerId       -- correlation to the outer row
    ORDER BY o.OrderDate DESC
) AS t
ORDER BY c.CustomerId, t.OrderId;

-- Same, but keep customers with no orders
SELECT c.Name, t.OrderId, t.Amount
FROM Customers c
OUTER APPLY (
    SELECT TOP (2) o.OrderId, o.Amount
    FROM Orders o
    WHERE o.CustomerId = c.CustomerId
    ORDER BY o.OrderDate DESC
) AS t
ORDER BY c.CustomerId, t.OrderId;

-- ============================================
-- EXPECTED OUTPUT
-- Result derived from equivalent JOIN LATERAL ... LIMIT 2 on MySQL 9.1; not executed on SQL Server
-- ============================================
-- CROSS APPLY:                         OUTER APPLY adds one more row:
-- Asha  | 102 | 120.00                 Asha  | 102 | 120.00
-- Asha  | 107 |  80.00                 Asha  | 107 |  80.00
-- Rohan | 103 |  99.50                 Rohan | 103 |  99.50
-- Rohan | 106 |  60.00                 Rohan | 106 |  60.00
-- Meera | 105 | 410.00                 Meera | 105 | 410.00
--                                      Kabir | NULL | NULL
-- (Asha's two latest are 107 on 2024-03-20 and 102 on 2024-02-10; 101 is excluded)
```

---

## 🔍 Why This Works (3 lines max)
A plain JOIN cannot reference the left row inside a derived table, so a per-customer TOP is impossible; APPLY allows that correlation. With the (CustomerId, OrderDate DESC) index each iteration is a cheap index seek returning 2 rows. OUTER APPLY pads NULLs when the inner query returns nothing.
हिंदी: साधारण JOIN में derived table left row को नहीं देख सकती, APPLY में देख सकती है। Index हो तो हर customer के लिए छोटा seek होता है।

---

## ⚡ Alternative Solution

```sql
-- ROW_NUMBER version (no APPLY): often similar speed, better for large parts of the table
WITH r AS (
    SELECT o.*, ROW_NUMBER() OVER (PARTITION BY CustomerId ORDER BY OrderDate DESC) AS rn
    FROM Orders o
)
SELECT c.Name, r.OrderId, r.Amount
FROM Customers c JOIN r ON r.CustomerId = c.CustomerId AND r.rn <= 2
ORDER BY c.CustomerId, r.OrderId;

-- APPLY also calls inline table-valued functions per row and expands JSON/XML:
-- SELECT o.OrderId, j.[value] FROM Orders o CROSS APPLY OPENJSON(o.Tags) j;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ TOP without ORDER BY inside APPLY: which 2 rows you get is arbitrary
CROSS APPLY (SELECT TOP (2) OrderId FROM Orders o WHERE o.CustomerId = c.CustomerId) t

-- ❌ CROSS APPLY when you need all customers: Kabir silently disappears -> use OUTER APPLY
-- ❌ No supporting index on (CustomerId, OrderDate): every iteration scans/sorts -> very slow on big tables
-- ❌ Using a multi-statement TVF in APPLY: it runs row by row with a fixed-guess cardinality;
--    prefer inline TVFs (Q089).
```

---

## 🎯 Interview Tip (1 line)
Say: "APPLY is my tool for top-N-per-group when the outer set is small and an index supports the lookup, for calling inline TVFs per row, and for expanding JSON/XML. I compare it against ROW_NUMBER on the real data since the winner depends on how many groups and how big each group is." Mention LATERAL as the MySQL/PostgreSQL name.

---

## 🔗 Related Questions
→ Q047 (Top N per group) | Q067 (Top-N with window functions) | Q089 (Inline table-valued functions) | Q031 (JSON/OPENJSON)
