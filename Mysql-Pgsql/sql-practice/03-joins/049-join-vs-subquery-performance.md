---

# Q049. JOIN vs Subquery — Performance
# Category: Joins
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Find customers who placed at least one order over 1000, written as JOIN, IN subquery, EXISTS and correlated scalar subquery. Which is faster, and when do the results differ?

---

## 💡 Quick Concept (2 lines only)
Modern optimizers (MySQL 8+, PostgreSQL) rewrite IN/EXISTS into a semi-join, so JOIN, IN and EXISTS usually get the same plan - the real differences are semantics (JOIN duplicates rows, EXISTS does not) and correlated subqueries in SELECT that run once per outer row.
हिंदी: IN/EXISTS को optimizer semi-join बना देता है, speed लगभग same। असली फर्क: JOIN duplicate rows देता है, EXISTS नहीं।

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
  order_date  DATE
);

CREATE INDEX idx_orders_customer ON orders (customer_id);   -- FK index: critical for all variants

INSERT INTO customers VALUES
  (1, 'Asha',   'Mumbai'),
  (2, 'Rohan',  'Delhi'),
  (3, 'Meera',  'Pune'),
  (4, 'Vikram', 'Delhi');

INSERT INTO orders VALUES
  (101, 1, 1500.00, '2024-01-05'),
  (102, 1, 2200.00, '2024-01-20'),   -- Asha has TWO big orders
  (103, 2,  500.00, '2024-01-11'),
  (104, 3, 1200.00, '2024-02-14');

-- ============================================
-- 1) JOIN  (duplicates the customer once per matching order!)
-- ============================================

SELECT c.name
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE o.amount > 1000
ORDER BY c.name;
-- Output:
-- name
-- Asha
-- Asha
-- Meera
-- ^ Asha appears twice -> needs DISTINCT, which adds a dedupe step

-- ============================================
-- 2) IN subquery  (each customer at most once)
-- ============================================

SELECT c.name
FROM customers c
WHERE c.customer_id IN (SELECT o.customer_id FROM orders o WHERE o.amount > 1000)
ORDER BY c.name;
-- Output:
-- name
-- Asha
-- Meera

-- ============================================
-- 3) EXISTS  (stops at first match per customer)
-- ============================================

SELECT c.name
FROM customers c
WHERE EXISTS (
  SELECT 1 FROM orders o
  WHERE o.customer_id = c.customer_id AND o.amount > 1000
)
ORDER BY c.name;
-- Output:
-- name
-- Asha
-- Meera

-- ============================================
-- 4) JOIN + DISTINCT (same rows as IN/EXISTS)
-- ============================================

SELECT DISTINCT c.name
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE o.amount > 1000
ORDER BY c.name;
-- Output:
-- name
-- Asha
-- Meera

-- ============================================
-- 5) Correlated scalar subquery in SELECT (runs per outer row - the slow pattern)
-- ============================================

SELECT c.name,
       (SELECT MAX(o.amount) FROM orders o WHERE o.customer_id = c.customer_id) AS biggest_order
FROM customers c
ORDER BY c.name;
-- Output:
-- name   | biggest_order
-- Asha   | 2200.00
-- Meera  | 1200.00
-- Rohan  | 500.00
-- Vikram | NULL
-- ^ Fine with an index on orders(customer_id) and few customers; rewrite as LEFT JOIN + GROUP BY for big scans.

-- ============================================
-- HOW TO COMPARE REAL PLANS
-- ============================================
-- MySQL:       EXPLAIN FORMAT=TREE <query>;      -- look for "Semi-join"/"hash semijoin"/"Nested loop"
-- PostgreSQL:  EXPLAIN (ANALYZE, BUFFERS) <query>;  -- look for "Hash Semi Join" vs "Nested Loop"
-- Always measure on production-sized data; with 4 rows the planner choice is meaningless.
```

---

## 🔍 Why This Works (3 lines max)
IN and EXISTS express a semi-join ("is there a match?") so the planner can stop at the first match; a plain JOIN returns every match and must be de-duplicated if you only want parents. Correlated subqueries in the SELECT list are a per-row lookup, so cost grows with outer row count.
हिंदी: IN/EXISTS = "match है या नहीं" (semi-join)। JOIN हर match return करता है, इसलिए DISTINCT लगता है।

---

## ⚡ Alternative Solution

```sql
-- NOT IN vs NOT EXISTS behave differently with NULLs
INSERT INTO orders VALUES (105, NULL, 99.00, '2024-03-01');   -- guest order, no customer

-- ❌ NOT IN: one NULL in the subquery makes the whole predicate UNKNOWN -> zero rows
SELECT name FROM customers
WHERE customer_id NOT IN (SELECT customer_id FROM orders);
-- Output:
-- (0 rows)

-- ✅ NOT EXISTS: NULL-safe
SELECT name FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);
-- Output:
-- name
-- Vikram

-- Version notes: MySQL < 5.6 handled IN (subquery) badly (ran it per row); 5.6+ materialises or
-- semi-joins it. PostgreSQL has done semi-joins for EXISTS/IN for many versions; NOT IN
-- is NOT converted to an anti-join, so prefer NOT EXISTS in both databases.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "JOIN is always faster than subquery" (an old MySQL 5.5 myth)
-- On MySQL 8+/PostgreSQL the plans are usually identical; readability and correctness decide.

-- ❌ Wrong: JOIN to filter parents, then COUNT(*) -> inflated counts from duplicate rows
SELECT COUNT(*) FROM customers c JOIN orders o ON o.customer_id = c.customer_id WHERE o.amount > 1000;  -- 3, not 2
-- ✅ SELECT COUNT(*) FROM customers c WHERE EXISTS (...)     -- 2 customers

-- ❌ Wrong: NOT IN against a nullable column (see Alternative Solution)
-- ❌ Wrong: no index on the FK -> every variant degrades to a full scan per outer row
```

---

## 🎯 Interview Tip (1 line)
Say: "I choose by semantics first - EXISTS for 'has a match', JOIN when I need columns from both sides, NOT EXISTS for anti-joins because NOT IN breaks on NULLs - and then I confirm with EXPLAIN ANALYZE rather than trusting folklore, because both engines rewrite IN/EXISTS into semi-joins."

---

## 🔗 Related Questions
→ Q052 (A not in B, 3 ways) | Q109 (Subquery to JOIN rewrite) | Q047 (JOIN with aggregation) | Q051 (Join order)
