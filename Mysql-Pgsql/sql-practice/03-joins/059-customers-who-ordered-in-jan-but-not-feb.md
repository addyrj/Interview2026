---

# Q059. Customers Who Placed an Order in Jan but Not Feb
# Category: Joins
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Find customers who ordered in January 2024 but did not order in February 2024. Show NOT EXISTS, LEFT JOIN anti-join, and conditional aggregation.

---

## 💡 Quick Concept (2 lines only)
"In period A but not in period B" is an anti-join on the same orders table: take customers with a January order and require that no February order exists. Always use date range predicates (`>= start AND < next_start`) rather than month functions on the column.
हिंदी: "Jan में हाँ, Feb में नहीं" = anti-join। Jan order हो और Feb order न हो। Date range (>= और <) use करो, function column पर नहीं।

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

CREATE INDEX idx_orders_date_cust ON orders (order_date, customer_id);

INSERT INTO customers VALUES (1, 'Asha'), (2, 'Rohan'), (3, 'Meera'), (4, 'Vikram'), (5, 'Isha');
INSERT INTO orders VALUES
  (101, 1, 500.00, '2024-01-05'),   -- Asha: Jan only        -> expected
  (102, 2, 300.00, '2024-01-20'),   -- Rohan: Jan AND Feb    -> excluded
  (103, 2, 450.00, '2024-02-03'),
  (104, 3, 200.00, '2024-02-14'),   -- Meera: Feb only       -> excluded
  (105, 4, 100.00, '2024-01-31'),   -- Vikram: Jan only      -> expected
  (106, 4, 250.00, '2024-03-10'),   -- (March does not matter)
  (107, 1, 150.00, '2024-01-25');   -- Asha has 2 Jan orders -> must appear once

-- ============================================
-- SOLUTION 1: EXISTS + NOT EXISTS
-- ============================================

-- Step 1: customer has at least one order in [2024-01-01, 2024-02-01)
-- Step 2: and has no order in [2024-02-01, 2024-03-01)
SELECT c.customer_id, c.name
FROM customers c
WHERE EXISTS (
        SELECT 1 FROM orders o
        WHERE o.customer_id = c.customer_id
          AND o.order_date >= '2024-01-01' AND o.order_date < '2024-02-01')
  AND NOT EXISTS (
        SELECT 1 FROM orders o
        WHERE o.customer_id = c.customer_id
          AND o.order_date >= '2024-02-01' AND o.order_date < '2024-03-01')
ORDER BY c.customer_id;
-- Output:
-- customer_id | name
-- 1           | Asha
-- 4           | Vikram

-- ============================================
-- SOLUTION 2: LEFT JOIN anti-join (Feb orders joined in the ON clause)
-- ============================================

SELECT DISTINCT c.customer_id, c.name           -- DISTINCT: Asha has two Jan rows
FROM customers c
JOIN orders jan
  ON jan.customer_id = c.customer_id
 AND jan.order_date >= '2024-01-01' AND jan.order_date < '2024-02-01'
LEFT JOIN orders feb
  ON feb.customer_id = c.customer_id
 AND feb.order_date >= '2024-02-01' AND feb.order_date < '2024-03-01'
WHERE feb.order_id IS NULL                       -- no February match
ORDER BY c.customer_id;
-- Output:
-- customer_id | name
-- 1           | Asha
-- 4           | Vikram

-- ============================================
-- SOLUTION 3: one scan with conditional aggregation
-- ============================================

SELECT c.customer_id, c.name
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
HAVING SUM(CASE WHEN o.order_date >= '2024-01-01' AND o.order_date < '2024-02-01' THEN 1 ELSE 0 END) > 0
   AND SUM(CASE WHEN o.order_date >= '2024-02-01' AND o.order_date < '2024-03-01' THEN 1 ELSE 0 END) = 0
ORDER BY c.customer_id;
-- Output:
-- customer_id | name
-- 1           | Asha
-- 4           | Vikram
```

---

## 🔍 Why This Works (3 lines max)
EXISTS proves January activity, NOT EXISTS proves February absence, and both can use an index on (order_date, customer_id) as range lookups. Conditional aggregation reaches the same answer in a single pass by counting orders per month per customer and filtering in HAVING.
हिंदी: EXISTS = Jan में order, NOT EXISTS = Feb में नहीं। Conditional aggregation एक ही scan में दोनों शर्तें जाँच लेता है।

---

## ⚡ Alternative Solution

```sql
-- Set operation: January customers EXCEPT February customers (MySQL 8.0.31+, PostgreSQL)
SELECT customer_id FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2024-02-01'
EXCEPT
SELECT customer_id FROM orders WHERE order_date >= '2024-02-01' AND order_date < '2024-03-01'
ORDER BY customer_id;
-- Output:
-- customer_id
-- 1
-- 4

-- NOT IN variant of the same question (safe only because of the NULL guard inside):
SELECT jan.customer_id
FROM (SELECT DISTINCT customer_id FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2024-02-01') jan
WHERE jan.customer_id NOT IN (
  SELECT customer_id FROM orders
  WHERE order_date >= '2024-02-01' AND order_date < '2024-03-01' AND customer_id IS NOT NULL   -- NULL guard
)
ORDER BY jan.customer_id;
-- Output:
-- customer_id
-- 1
-- 4

-- Syntax differences: month extraction is MONTH(order_date) / YEAR(order_date) in MySQL
-- and EXTRACT(MONTH FROM order_date) in PostgreSQL (MySQL supports EXTRACT too).
-- Avoid either on the column in WHERE - it blocks index use. Use half-open ranges as above.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: a plain filter cannot express "no February order"
SELECT DISTINCT customer_id FROM orders
WHERE MONTH(order_date) = 1 AND MONTH(order_date) <> 2;      -- <> 2 is trivially true for January rows

-- ❌ Wrong: self join without the anti-join test -> returns customers who HAVE a Feb order
-- ❌ Wrong: BETWEEN '2024-01-01' AND '2024-01-31' on a DATETIME column -> drops orders on Jan 31 after 00:00:00
-- ❌ Wrong: MONTH(order_date) = 1 with no year -> mixes January 2023 and January 2024
-- ❌ Wrong: NOT IN with a nullable customer_id (guest orders) -> empty result
-- ✅ Half-open date ranges + NOT EXISTS (or EXCEPT) + DISTINCT where joins multiply rows
```

---

## 🎯 Interview Tip (1 line)
Say: "It's an anti-join across two time windows: I write half-open date ranges so indexes work, use EXISTS/NOT EXISTS (NULL-safe), dedupe if I join, and mention conditional aggregation as the single-scan variant - the same shape answers churn and retention questions."

---

## 🔗 Related Questions
→ Q052 (A not in B, 3 ways) | Q060 (Common rows between tables) | Q049 (JOIN vs subquery) | Q047 (JOIN with aggregation)
