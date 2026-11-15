---

# Q036. INNER vs LEFT vs RIGHT vs FULL JOIN
# Category: Joins, Subqueries + CTEs
# Difficulty: ⭐ Easy
# DB: SQL Server (MySQL has no FULL JOIN, emulate with LEFT UNION RIGHT; PostgreSQL supports all four)

---

## ❓ Question
Given Customers and Orders (one customer with no orders, one order with no customer), show what INNER, LEFT, RIGHT and FULL OUTER JOIN return. Then: find customers with no orders, and explain why a WHERE filter on the right table turns a LEFT JOIN into an INNER JOIN.

---

## 💡 Quick Concept (2 lines only)
INNER keeps only matches; LEFT keeps all left rows (NULLs where no match); RIGHT keeps all right rows; FULL keeps all rows of both. A condition on the outer side belongs in ON to preserve the outer rows, in WHERE it filters them out.
हिंदी: INNER = सिर्फ़ match। LEFT = बाएँ की सब rows। FULL = दोनों तरफ़ की सब rows। Right table की condition WHERE में डालोगे तो LEFT JOIN INNER बन जाता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Customers (CustomerId INT PRIMARY KEY, Name VARCHAR(50), City VARCHAR(50));
CREATE TABLE Orders (
    OrderId INT PRIMARY KEY, CustomerId INT NULL,
    OrderDate DATE, Amount DECIMAL(10,2)
);

INSERT INTO Customers VALUES (1,'Asha','Pune'),(2,'Rohan','Delhi'),(3,'Meera','Mumbai'),(4,'Kabir','Pune');
INSERT INTO Orders VALUES
  (101,1,'2024-01-05',250.00),(102,1,'2024-02-10',120.00),(103,2,'2024-02-11',99.50),
  (104,NULL,'2024-03-01',75.00),            -- order with no customer
  (105,3,'2024-03-15',410.00),(106,2,'2024-04-01',60.00);
-- Kabir (4) has no orders.

-- ============================================
-- SOLUTION
-- ============================================
-- INNER: matches only
SELECT c.Name, o.OrderId, o.Amount
FROM Customers c INNER JOIN Orders o ON o.CustomerId = c.CustomerId
ORDER BY o.OrderId;

-- LEFT: every customer, even Kabir
SELECT c.Name, o.OrderId
FROM Customers c LEFT JOIN Orders o ON o.CustomerId = c.CustomerId
ORDER BY c.CustomerId, o.OrderId;

-- RIGHT: every order, even order 104
SELECT c.Name, o.OrderId
FROM Customers c RIGHT JOIN Orders o ON o.CustomerId = c.CustomerId
ORDER BY o.OrderId;

-- FULL OUTER: everything from both sides
SELECT c.Name, o.OrderId
FROM Customers c FULL OUTER JOIN Orders o ON o.CustomerId = c.CustomerId
ORDER BY o.OrderId, c.CustomerId;

-- Anti-join: customers with no orders
SELECT c.Name
FROM Customers c LEFT JOIN Orders o ON o.CustomerId = c.CustomerId
WHERE o.OrderId IS NULL;

-- ============================================
-- EXPECTED OUTPUT (result derived from equivalent queries on SQLite 3.49; not executed on SQL Server)
-- ============================================
-- INNER (5 rows):  Asha 101 250.00 | Asha 102 120.00 | Rohan 103 99.50 | Meera 105 410.00 | Rohan 106 60.00
-- LEFT  (6 rows):  Asha 101 | Asha 102 | Rohan 103 | Rohan 106 | Meera 105 | Kabir NULL
-- RIGHT (6 rows):  Asha 101 | Asha 102 | Rohan 103 | NULL 104 | Meera 105 | Rohan 106
-- FULL  (7 rows):  Kabir NULL | Asha 101 | Asha 102 | Rohan 103 | NULL 104 | Meera 105 | Rohan 106
-- Anti-join:       Kabir
```

---

## 🔍 Why This Works (3 lines max)
The join builds matching pairs first; outer joins then add the unmatched rows of the preserved side with NULLs for the other side's columns. `WHERE o.OrderId IS NULL` after a LEFT JOIN keeps exactly those added rows, i.e. customers with no match. Keyword OUTER is optional in LEFT/RIGHT/FULL.
हिंदी: पहले matching pairs बनते हैं, फिर unmatched rows NULL के साथ जुड़ती हैं। `IS NULL` filter से सिर्फ़ बिना-match वाली rows बचती हैं।

---

## ⚡ Alternative Solution

```sql
-- NOT EXISTS anti-join (clearer intent, NULL-safe)
SELECT c.Name FROM Customers c
WHERE NOT EXISTS (SELECT 1 FROM Orders o WHERE o.CustomerId = c.CustomerId);

-- FULL JOIN emulation for MySQL (which lacks it):
-- SELECT ... FROM A LEFT JOIN B ON ... UNION SELECT ... FROM A RIGHT JOIN B ON ...
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Filter on the right table in WHERE: LEFT JOIN silently becomes INNER
SELECT c.Name, o.OrderId
FROM Customers c LEFT JOIN Orders o ON o.CustomerId = c.CustomerId
WHERE o.Amount > 100;
-- Returns only: Asha 101 | Asha 102 | Meera 105   (Rohan and Kabir vanish)

-- ✅ Put it in ON to keep every customer:
SELECT c.Name, o.OrderId
FROM Customers c LEFT JOIN Orders o ON o.CustomerId = c.CustomerId AND o.Amount > 100
ORDER BY c.CustomerId, o.OrderId;
-- Asha 101 | Asha 102 | Rohan NULL | Meera 105 | Kabir NULL
```

---

## 🎯 Interview Tip (1 line)
Say: "I choose the join by the question: INNER for required relationships, LEFT to keep the driving set, and I rarely use RIGHT — I swap the tables and use LEFT for readability. I always check whether a WHERE predicate on the outer table is accidentally making my LEFT JOIN inner, and I watch for duplicate rows from one-to-many joins before aggregating."

---

## 🔗 Related Questions
→ Q037 (CROSS JOIN and self join) | Q053 (Anti-joins) | Q052 (Join order and join hints) | Q044 (UNION, INTERSECT, EXCEPT)
