---

# Q047. JOIN with Aggregation — COUNT per Group
# Category: Joins
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Show each customer with their number of orders and total spend, including customers with zero orders. Then show only customers with 2+ orders, and explain why `COUNT(*)` gives the wrong answer after a LEFT JOIN.

---

## 💡 Quick Concept (2 lines only)
LEFT JOIN first, GROUP BY the parent key, then aggregate child columns: `COUNT(o.order_id)` ignores NULLs so zero-order customers get 0, while `COUNT(*)` counts the NULL-extended row as 1. Filter groups with HAVING, filter rows with WHERE (or the ON clause).
हिंदी: LEFT JOIN + GROUP BY parent। COUNT(o.order_id) NULL को नहीं गिनता, COUNT(*) गिनता है (1 आता है)। Group filter = HAVING।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE customers (
  customer_id INT PRIMARY KEY,
  name        VARCHAR(100),
  city        VARCHAR(50)
);

CREATE TABLE orders (
  order_id    INT PRIMARY KEY,
  customer_id INT,
  amount      DECIMAL(10,2),
  status      VARCHAR(20),
  order_date  DATE
);

INSERT INTO customers VALUES
  (1, 'Asha',   'Mumbai'),
  (2, 'Rohan',  'Delhi'),
  (3, 'Meera',  'Pune'),
  (4, 'Vikram', 'Delhi');       -- Vikram has no orders

INSERT INTO orders VALUES
  (101, 1, 1200.00, 'completed', '2024-01-05'),
  (102, 1,  800.00, 'completed', '2024-01-20'),
  (103, 1,  300.00, 'cancelled', '2024-02-02'),
  (104, 2, 2500.00, 'completed', '2024-01-11'),
  (105, 3,  150.00, 'cancelled', '2024-02-14');

-- ============================================
-- SOLUTION: orders count + total per customer (zero-order customers included)
-- ============================================

-- Step 1: LEFT JOIN keeps every customer (Vikram gets NULL order columns)
-- Step 2: GROUP BY customer key, aggregate the order columns
SELECT c.customer_id,
       c.name,
       COUNT(o.order_id)             AS order_count,   -- NULL not counted -> 0 for Vikram
       COALESCE(SUM(o.amount), 0.00) AS total_spend
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY c.customer_id;
-- Output:
-- customer_id | name   | order_count | total_spend
-- 1           | Asha   | 3           | 2300.00
-- 2           | Rohan  | 1           | 2500.00
-- 3           | Meera  | 1           | 150.00
-- 4           | Vikram | 0           | 0.00

-- ============================================
-- ONLY CUSTOMERS WITH 2+ ORDERS (HAVING filters groups)
-- ============================================

SELECT c.name, COUNT(o.order_id) AS order_count
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) >= 2;
-- Output:
-- name | order_count
-- Asha | 3

-- ============================================
-- WRONG COUNT: COUNT(*) after LEFT JOIN
-- ============================================

SELECT c.name, COUNT(*) AS wrong_count
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE c.name = 'Vikram'
GROUP BY c.name;
-- Output:
-- name   | wrong_count
-- Vikram | 1
-- ^ Vikram has 0 orders but shows 1 (the NULL-extended row is counted)

-- ============================================
-- FILTER ON CHILD ROWS: completed orders only, but keep all customers
-- ============================================

SELECT c.name,
       COUNT(o.order_id) AS completed_orders
FROM customers c
LEFT JOIN orders o
       ON o.customer_id = c.customer_id
      AND o.status = 'completed'      -- filter in ON, not WHERE, so Meera/Vikram stay with 0
GROUP BY c.customer_id, c.name
ORDER BY c.customer_id;
-- Output:
-- name   | completed_orders
-- Asha   | 2
-- Rohan  | 1
-- Meera  | 0
-- Vikram | 0
```

---

## 🔍 Why This Works (3 lines max)
LEFT JOIN produces one NULL-padded row for customers without orders; `COUNT(column)` skips that NULL but `COUNT(*)` does not. HAVING runs after grouping, so it can filter on aggregates, while a condition on the child table belongs in ON to preserve the outer rows.
हिंदी: Zero-order customer को चाहिए तो LEFT JOIN + COUNT(child column)। Aggregate पर filter = HAVING, child filter = ON clause में।

---

## ⚡ Alternative Solution

```sql
-- Aggregate first, join after (avoids fan-out when joining several child tables)
SELECT c.name,
       COALESCE(t.order_count, 0)  AS order_count,
       COALESCE(t.total_spend, 0.00) AS total_spend
FROM customers c
LEFT JOIN (
  SELECT customer_id, COUNT(*) AS order_count, SUM(amount) AS total_spend
  FROM orders
  GROUP BY customer_id
) t ON t.customer_id = c.customer_id
ORDER BY c.customer_id;
-- Output:
-- name   | order_count | total_spend
-- Asha   | 3           | 2300.00
-- Rohan  | 1           | 2500.00
-- Meera  | 1           | 150.00
-- Vikram | 0           | 0.00

-- Correlated scalar subquery version (fine for small result sets, one lookup per customer)
SELECT c.name,
       (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id) AS order_count
FROM customers c
ORDER BY c.customer_id;
-- Output:
-- name   | order_count
-- Asha   | 3
-- Rohan  | 1
-- Meera  | 1
-- Vikram | 0

-- Difference: MySQL (default ONLY_FULL_GROUP_BY) and PostgreSQL both accept
-- GROUP BY c.customer_id and then selecting c.name, because customer_id is the primary key
-- (functional dependency). Listing both columns, as above, is the portable habit.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: COUNT(*) with LEFT JOIN -> customers with no orders show 1
SELECT c.name, COUNT(*) FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id GROUP BY c.name;

-- ❌ Wrong: WHERE on the child table kills the zero-order customers
SELECT c.name, COUNT(o.order_id)
FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.status = 'completed'          -- NULL = 'completed' is not true -> Vikram disappears
GROUP BY c.name;
-- ✅ Move the condition into ON (shown above)

-- ❌ Wrong: joining two child tables then SUM -> fan-out inflates totals
-- customers JOIN orders JOIN payments: each order row repeats per payment row
-- ✅ Aggregate each child in its own derived table, then join (Alternative Solution)

-- ❌ Wrong: GROUP BY c.name only - two customers with the same name merge into one group
```

---

## 🎯 Interview Tip (1 line)
Say: "LEFT JOIN, group by the parent's primary key, COUNT a child column not star, and put child filters in ON; if I join multiple child tables I pre-aggregate each one first to avoid row fan-out inflating the sums."

---

## 🔗 Related Questions
→ Q042 (LEFT JOIN with NULL detection) | Q046 (CROSS JOIN) | Q048 (Multi-table JOIN) | Q049 (JOIN vs subquery)
