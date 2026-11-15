---

# Q051. Join Order — Does It Matter for the Optimizer?
# Category: Joins
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Does the order in which you write tables in a multi-table INNER JOIN affect performance? What about LEFT JOIN? Show that the written order does not change INNER JOIN results, but does change LEFT JOIN results.

---

## 💡 Quick Concept (2 lines only)
For INNER JOINs the optimizer picks its own join order from statistics (cost-based), so the order you write is mostly irrelevant; for OUTER JOINs the order is semantic and restricts reordering. Hints/settings exist when statistics mislead it (STRAIGHT_JOIN, join_collapse_limit).
हिंदी: INNER JOIN में optimizer खुद order चुनता है, लिखने का order ज़्यादातर बेअसर। LEFT JOIN में order का मतलब बदल जाता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE customers (customer_id INT PRIMARY KEY, name VARCHAR(100));
CREATE TABLE orders    (order_id INT PRIMARY KEY, customer_id INT, order_date DATE);
CREATE TABLE payments  (payment_id INT PRIMARY KEY, order_id INT, amount DECIMAL(10,2));

CREATE INDEX idx_orders_customer  ON orders (customer_id);
CREATE INDEX idx_payments_order   ON payments (order_id);

INSERT INTO customers VALUES (1, 'Asha'), (2, 'Rohan'), (3, 'Meera');
INSERT INTO orders VALUES
  (101, 1, '2024-01-05'),
  (102, 1, '2024-02-10'),
  (103, 2, '2024-01-11');          -- Meera has no orders; order 102 has no payment
INSERT INTO payments VALUES
  (1, 101, 1500.00),
  (2, 103,  500.00);

-- ============================================
-- INNER JOIN: written order does NOT change the result
-- ============================================

-- Order A: customers -> orders -> payments
SELECT c.name, o.order_id, p.amount
FROM customers c
JOIN orders   o ON o.customer_id = c.customer_id
JOIN payments p ON p.order_id    = o.order_id
ORDER BY o.order_id;
-- Output:
-- name  | order_id | amount
-- Asha  | 101      | 1500.00
-- Rohan | 103      | 500.00

-- Order B: payments -> orders -> customers (reversed)
SELECT c.name, o.order_id, p.amount
FROM payments p
JOIN orders    o ON o.order_id    = p.order_id
JOIN customers c ON c.customer_id = o.customer_id
ORDER BY o.order_id;
-- Output:
-- name  | order_id | amount
-- Asha  | 101      | 1500.00
-- Rohan | 103      | 500.00
-- ^ identical rows; the planner is free to start from whichever table is cheapest

-- ============================================
-- LEFT JOIN: order IS semantic
-- ============================================

-- Keep all customers, attach orders (Meera survives with NULL)
SELECT c.name, o.order_id
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
ORDER BY c.name, o.order_id;
-- Output:
-- name  | order_id
-- Asha  | 101
-- Asha  | 102
-- Meera | NULL
-- Rohan | 103

-- Reverse the tables: now ORDERS is the preserved side (every order has a customer, so Meera is gone)
SELECT c.name, o.order_id
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
ORDER BY c.name, o.order_id;
-- Output:
-- name  | order_id
-- Asha  | 101
-- Asha  | 102
-- Rohan | 103

-- ============================================
-- HOW TO SEE WHAT THE OPTIMIZER CHOSE
-- ============================================
-- MySQL:       EXPLAIN FORMAT=TREE SELECT ...;   -- rows appear in the order tables are actually joined
-- PostgreSQL:  EXPLAIN SELECT ...;               -- join tree shows Nested Loop / Hash Join / Merge Join order
--
-- Overriding when statistics are wrong:
--   MySQL:       SELECT STRAIGHT_JOIN ... FROM a JOIN b ...      -- forces the written order
--                SELECT /*+ JOIN_ORDER(c, o, p) */ ...           -- optimizer hint (8.0.20+)
--   PostgreSQL:  SET join_collapse_limit = 1;  -- honour written explicit JOIN order (default 8)
--                (from_collapse_limit / geqo_threshold = 12 also limit exhaustive search)
```

---

## 🔍 Why This Works (3 lines max)
INNER JOIN is commutative and associative, so the planner enumerates orders using row estimates and index availability and picks the cheapest. LEFT JOIN is not commutative (it fixes which side is preserved), so it limits reordering and swapping the tables changes the result set, not just the plan.
हिंदी: INNER JOIN commutative है, इसलिए optimizer cost देखकर order बदल देता है। LEFT JOIN commutative नहीं, order बदला तो result बदलता है।

---

## ⚡ Alternative Solution

```sql
-- When the optimizer picks a bad order (stale statistics), first fix the statistics:
-- ANALYZE TABLE orders;   (prints a small status table: Op = analyze, Msg_text = OK)

-- Then (only if still wrong) force an order. MySQL: STRAIGHT_JOIN joins left-to-right exactly as written
SELECT STRAIGHT_JOIN c.name, o.order_id, p.amount
FROM customers c
JOIN orders   o ON o.customer_id = c.customer_id
JOIN payments p ON p.order_id    = o.order_id
ORDER BY o.order_id;
-- Output:
-- name  | order_id | amount
-- Asha  | 101      | 1500.00
-- Rohan | 103      | 500.00
```

```sql
-- PostgreSQL: refresh statistics, then (if needed) honour the written join order for this session only
ANALYZE orders;

SET join_collapse_limit = 1;    -- join in the exact written order
SELECT c.name, o.order_id, p.amount
FROM customers c
JOIN orders   o ON o.customer_id = c.customer_id
JOIN payments p ON p.order_id    = o.order_id
ORDER BY o.order_id;
-- Output:
-- name  | order_id | amount
-- Asha  | 101      | 1500.00
-- Rohan | 103      | 500.00
RESET join_collapse_limit;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "I put the smallest table first so it is faster" (cargo cult for INNER JOIN)
-- The planner already reorders; stale statistics or missing indexes are the real causes of slow joins.

-- ❌ Wrong: swapping LEFT JOIN operands "to optimise" -> silently changes the result
-- ❌ Wrong: LEFT JOIN a, then WHERE b.col = 'x' on the optional table -> becomes INNER JOIN, optimizer reorders
-- ❌ Wrong: using STRAIGHT_JOIN / join_collapse_limit=1 globally -> plan regressions when data grows
-- ✅ Fix order of work: indexes on join keys -> fresh ANALYZE -> read EXPLAIN -> hint only as last resort
```

---

## 🎯 Interview Tip (1 line)
Say: "For INNER JOINs the written order is irrelevant because the cost-based optimizer reorders using statistics; for outer joins order defines semantics. If a plan is bad I fix indexes and statistics first, and only then use STRAIGHT_JOIN or join_collapse_limit as a targeted override."

---

## 🔗 Related Questions
→ Q048 (Multi-table JOIN) | Q049 (JOIN vs subquery) | Q042 (LEFT JOIN with NULL detection) | Q044 (FULL OUTER JOIN)
