---

# Q052. Find Records in Table A Not in Table B (3 Ways)
# Category: Joins
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Find customers who have never placed an order (rows in customers with no match in orders). Show LEFT JOIN ... IS NULL, NOT EXISTS and NOT IN, and explain which one is unsafe.

---

## 💡 Quick Concept (2 lines only)
This is an anti-join. LEFT JOIN + `WHERE b.key IS NULL` and `NOT EXISTS` are both NULL-safe and optimised into an anti-join; `NOT IN` returns nothing if the subquery contains even one NULL.
हिंदी: A में है B में नहीं = anti-join। LEFT JOIN IS NULL या NOT EXISTS safe हैं; NOT IN में एक NULL आया तो result खाली।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE customers (
  customer_id INT PRIMARY KEY,
  name        VARCHAR(100),
  signup_date DATE
);

CREATE TABLE orders (
  order_id    INT PRIMARY KEY,
  customer_id INT,                -- nullable: guest checkout has no customer
  amount      DECIMAL(10,2)
);

CREATE INDEX idx_orders_customer ON orders (customer_id);

INSERT INTO customers VALUES
  (1, 'Asha',   '2024-01-01'),
  (2, 'Rohan',  '2024-01-15'),
  (3, 'Meera',  '2024-02-01'),
  (4, 'Vikram', '2024-02-10');

INSERT INTO orders VALUES
  (101, 1, 1500.00),
  (102, 1,  700.00),
  (103, 3,  500.00);              -- Rohan (2) and Vikram (4) never ordered

-- ============================================
-- WAY 1: LEFT JOIN ... IS NULL
-- ============================================

SELECT c.customer_id, c.name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL          -- test the child's PRIMARY KEY: NULL only when no match
ORDER BY c.customer_id;
-- Output:
-- customer_id | name
-- 2           | Rohan
-- 4           | Vikram

-- ============================================
-- WAY 2: NOT EXISTS  (usually the clearest and safest)
-- ============================================

SELECT c.customer_id, c.name
FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
)
ORDER BY c.customer_id;
-- Output:
-- customer_id | name
-- 2           | Rohan
-- 4           | Vikram

-- ============================================
-- WAY 3: NOT IN  (works only while the subquery has no NULLs)
-- ============================================

SELECT c.customer_id, c.name
FROM customers c
WHERE c.customer_id NOT IN (SELECT customer_id FROM orders)
ORDER BY c.customer_id;
-- Output:
-- customer_id | name
-- 2           | Rohan
-- 4           | Vikram

-- Now add a guest order with customer_id NULL and run WAY 3 again:
INSERT INTO orders VALUES (104, NULL, 99.00);

SELECT c.customer_id, c.name
FROM customers c
WHERE c.customer_id NOT IN (SELECT customer_id FROM orders)
ORDER BY c.customer_id;
-- Output:
-- (0 rows)
-- ^ EMPTY! x NOT IN (1, 3, NULL) evaluates to UNKNOWN for every x that is not 1 or 3

-- Ways 1 and 2 are unaffected by the NULL row:
SELECT COUNT(*) AS never_ordered
FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);
-- Output:
-- never_ordered
-- 2
```

---

## 🔍 Why This Works (3 lines max)
LEFT JOIN keeps every customer and leaves the order columns NULL when nothing matched, so IS NULL on the child's primary key isolates the non-matches. NOT EXISTS asks "is there no matching row?" per customer and never compares against NULL; NOT IN uses three-valued logic, so a single NULL poisons it.
हिंदी: LEFT JOIN में match न हो तो child columns NULL आते हैं, वही filter करो। NOT EXISTS NULL-safe है; NOT IN नहीं।

---

## ⚡ Alternative Solution

```sql
-- Set-operation version (same data type columns; MySQL 8.0.31+ and PostgreSQL support EXCEPT)
SELECT customer_id FROM customers
EXCEPT
SELECT customer_id FROM orders WHERE customer_id IS NOT NULL
ORDER BY customer_id;
-- Output:
-- customer_id
-- 2
-- 4

-- Fixing NOT IN the quick way (filter NULLs in the subquery):
SELECT c.name
FROM customers c
WHERE c.customer_id NOT IN (SELECT customer_id FROM orders WHERE customer_id IS NOT NULL)
ORDER BY c.customer_id;
-- Output:
-- name
-- Rohan
-- Vikram

-- Version notes: EXCEPT arrived in MySQL 8.0.31 (older: use NOT EXISTS / LEFT JOIN).
-- PostgreSQL spells it EXCEPT too (Oracle uses MINUS). EXCEPT also removes duplicates.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: testing a nullable/outer column that could be NULL for other reasons
LEFT JOIN orders o ON o.customer_id = c.customer_id WHERE o.amount IS NULL
-- an order whose amount really is NULL is now wrongly reported as "no order"
-- ✅ Test the child's primary key (or the join key) for NULL

-- ❌ Wrong: putting the filter on the child table in WHERE instead of ON
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.amount > 1000 AND o.order_id IS NULL       -- contradictory, always empty
-- ✅ "Never ordered over 1000": put amount > 1000 in the ON clause, then WHERE o.order_id IS NULL

-- ❌ Wrong: NOT IN on a nullable column (see above)
```

---

## 🎯 Interview Tip (1 line)
Say: "I default to NOT EXISTS (or LEFT JOIN ... IS NULL) for anti-joins because both are NULL-safe and become hash anti-joins in MySQL 8 and PostgreSQL; I only use NOT IN when the column is NOT NULL, and I always index the foreign key."

---

## 🔗 Related Questions
→ Q042 (LEFT JOIN with NULL detection) | Q059 (Jan but not Feb) | Q049 (JOIN vs subquery) | Q060 (Common rows between tables)
