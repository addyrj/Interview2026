---

# Q050. LATERAL JOIN (PgSQL) — What Is It?
# Category: Joins
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (PostgreSQL 9.3+ | MySQL 8.0.14+)

---

## ❓ Question
What is a LATERAL join? Get the 2 most recent orders per customer (keeping customers with no orders) and show why a normal derived table cannot do this.

---

## 💡 Quick Concept (2 lines only)
LATERAL lets a subquery in FROM reference columns of tables to its left, so it runs "for each row of the left side" - like a correlated subquery that can return multiple rows and columns. It is the cleanest way to do top-N per group with LIMIT.
हिंदी: LATERAL subquery बाईं तरफ की table के columns use कर सकती है, यानी हर row के लिए चलती है। Top-N per group के लिए बढ़िया।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE customers (
  customer_id INT PRIMARY KEY,
  name        VARCHAR(100)
);

CREATE TABLE orders (
  order_id    INT PRIMARY KEY,
  customer_id INT,
  amount      DECIMAL(10,2),
  order_date  DATE
);

-- The index that makes LATERAL + LIMIT fast: one index seek per customer
CREATE INDEX idx_orders_cust_date ON orders (customer_id, order_date);

INSERT INTO customers VALUES (1, 'Asha'), (2, 'Rohan'), (3, 'Meera'), (4, 'Vikram');
INSERT INTO orders VALUES
  (101, 1, 1500.00, '2024-01-05'),
  (102, 1,  700.00, '2024-02-10'),
  (103, 1, 2200.00, '2024-03-20'),
  (104, 2,  500.00, '2024-01-11'),
  (105, 3, 1200.00, '2024-02-14'),
  (106, 3,   90.00, '2024-03-02');     -- Vikram (4) has no orders

-- ============================================
-- SOLUTION: 2 latest orders per customer
-- ============================================

-- Step 1: for each customer row c, run the inner query with c.customer_id plugged in
-- Step 2: ORDER BY ... LIMIT 2 inside gives top-2 for THAT customer only
SELECT c.name, o.order_id, o.amount, o.order_date
FROM customers c
JOIN LATERAL (
  SELECT order_id, amount, order_date
  FROM orders
  WHERE customer_id = c.customer_id      -- references c: only legal because of LATERAL
  ORDER BY order_date DESC
  LIMIT 2
) o ON true                              -- join condition already inside; ON true is required syntax
ORDER BY c.name, o.order_date DESC;
-- Output:
-- name  | order_id | amount  | order_date
-- Asha  | 103      | 2200.00 | 2024-03-20
-- Asha  | 102      | 700.00  | 2024-02-10
-- Meera | 106      | 90.00   | 2024-03-02
-- Meera | 105      | 1200.00 | 2024-02-14
-- Rohan | 104      | 500.00  | 2024-01-11

-- ============================================
-- KEEP CUSTOMERS WITH NO ORDERS: LEFT JOIN LATERAL
-- ============================================

SELECT c.name, o.order_id, o.order_date
FROM customers c
LEFT JOIN LATERAL (
  SELECT order_id, order_date
  FROM orders
  WHERE customer_id = c.customer_id
  ORDER BY order_date DESC
  LIMIT 1
) o ON true
ORDER BY c.name;
-- Output:
-- name   | order_id | order_date
-- Asha   | 103      | 2024-03-20
-- Meera  | 106      | 2024-03-02
-- Rohan  | 104      | 2024-01-11
-- Vikram | NULL     | NULL
-- ^ Vikram appears with NULLs; plain JOIN LATERAL would drop him (like INNER JOIN)

-- ============================================
-- LATERAL FOR REUSABLE CALCULATIONS (compute once, use many times)
-- ============================================

SELECT o.order_id, o.amount, t.gst, o.amount + t.gst AS total_with_gst
FROM orders o
CROSS JOIN LATERAL (SELECT ROUND(o.amount * 0.18, 2) AS gst) t
WHERE o.customer_id = 3
ORDER BY o.order_id;
-- Output:
-- order_id | amount  | gst    | total_with_gst
-- 105      | 1200.00 | 216.00 | 1416.00
-- 106      | 90.00   | 16.20  | 106.20
```

---

## 🔍 Why This Works (3 lines max)
The inner query is re-evaluated per outer row with that row's values, so ORDER BY + LIMIT apply per customer rather than globally. With an index on (customer_id, order_date) each evaluation is a short index range scan, which beats ranking every order with ROW_NUMBER when customers are few and orders are many.
हिंदी: Inner query हर customer row के लिए चलती है, इसलिए LIMIT per-customer लगता है। (customer_id, order_date) index हो तो बहुत तेज़।

---

## ⚡ Alternative Solution

```sql
-- Window-function version (works on any MySQL 8+/PostgreSQL, scans and ranks ALL orders)
SELECT name, order_id, amount, order_date
FROM (
  SELECT c.name, o.order_id, o.amount, o.order_date,
         ROW_NUMBER() OVER (PARTITION BY c.customer_id ORDER BY o.order_date DESC) AS rn
  FROM customers c
  JOIN orders o ON o.customer_id = c.customer_id
) ranked
WHERE rn <= 2
ORDER BY name, order_date DESC;
-- Output:
-- name  | order_id | amount  | order_date
-- Asha  | 103      | 2200.00 | 2024-03-20
-- Asha  | 102      | 700.00  | 2024-02-10
-- Meera | 106      | 90.00   | 2024-03-02
-- Meera | 105      | 1200.00 | 2024-02-14
-- Rohan | 104      | 500.00  | 2024-01-11

-- Version notes:
--  * PostgreSQL: LATERAL since 9.3; also lateral with set-returning functions, e.g.
--      SELECT * FROM customers c, LATERAL generate_series(1, c.customer_id) g;   (the LATERAL keyword is optional for functions)
--  * MySQL: LATERAL derived tables only from 8.0.14 (tested here on 9.1); no function-style lateral.
--  * SQL Server calls this CROSS APPLY / OUTER APPLY; Oracle 12c+ supports LATERAL and APPLY.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: referencing the outer table in a normal derived table
SELECT c.name, o.order_id
FROM customers c
JOIN (SELECT order_id FROM orders WHERE customer_id = c.customer_id LIMIT 2) o ON true;
-- PostgreSQL: ERROR invalid reference to FROM-clause entry for table "c" ... use LATERAL
-- MySQL:      ERROR Unknown column 'c.customer_id' in 'where clause'
-- ✅ Add the LATERAL keyword

-- ❌ Wrong: JOIN LATERAL when you need customers without rows -> use LEFT JOIN LATERAL ... ON true
-- ❌ Wrong: LATERAL without ORDER BY before LIMIT -> arbitrary rows returned
-- ❌ Wrong: no (customer_id, order_date) index -> each per-customer evaluation sorts/scans the whole orders table
```

---

## 🎯 Interview Tip (1 line)
Say: "LATERAL is a for-each join: the subquery sees the left row, so I get top-N per group with ORDER BY/LIMIT and an index seek per group; I use ROW_NUMBER instead when groups are huge in number and I need most rows anyway."

---

## 🔗 Related Questions
→ Q075 (Top N per group) | Q054 (Most recent per group) | Q186 (LATERAL with function) | Q048 (Multi-table JOIN)
