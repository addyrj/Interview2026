---

# Q235. INNER JOIN vs LEFT JOIN — Output Difference
# Category: Interview Classics
# Difficulty: ⭐ Easy
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Given `customers` (4 rows) and `orders` (4 rows, one with NULL customer_id), what rows do INNER JOIN and LEFT JOIN return? Then explain the classic trap: LEFT JOIN + a WHERE filter on the right table, versus the same filter in the ON clause.

---

## 💡 Quick Concept (2 lines only)
INNER JOIN keeps only rows that match on both sides. LEFT JOIN keeps ALL left rows and fills right columns with NULL when there is no match; a WHERE on a right-table column silently turns it back into an INNER JOIN.
हिंदी: INNER = सिर्फ matching rows; LEFT = left की सारी rows, match न मिले तो right में NULL।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE customers (
  id   INT PRIMARY KEY,
  name VARCHAR(50) NOT NULL
);

CREATE TABLE orders (
  id          INT PRIMARY KEY,
  customer_id INT,                       -- nullable on purpose (guest checkout)
  amount      DECIMAL(10,2) NOT NULL,
  status      VARCHAR(20) NOT NULL
);

INSERT INTO customers VALUES (1,'Alice'),(2,'Bob'),(3,'Carol'),(4,'Dave');

INSERT INTO orders VALUES
  (10, 1, 100.00, 'paid'),
  (11, 1, 250.00, 'refunded'),
  (12, 2,  80.00, 'paid'),
  (13, NULL, 999.00, 'paid');            -- guest order, matches no customer

-- ============================================
-- SOLUTION
-- ============================================

-- 1) INNER JOIN: only customers that HAVE orders
SELECT c.name, o.id AS order_id, o.amount
FROM customers c
INNER JOIN orders o ON o.customer_id = c.id
ORDER BY c.id, o.id;

-- Result (3 rows):
-- name  | order_id | amount
-- ------+----------+-------
-- Alice | 10       | 100.00
-- Alice | 11       | 250.00
-- Bob   | 12       | 80.00

-- 2) LEFT JOIN: all customers, NULLs where no order
SELECT c.name, o.id AS order_id, o.amount
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
ORDER BY c.id, o.id;

-- Result (5 rows):
-- name  | order_id | amount
-- ------+----------+-------
-- Alice | 10       | 100.00
-- Alice | 11       | 250.00
-- Bob   | 12       | 80.00
-- Carol | NULL     | NULL
-- Dave  | NULL     | NULL

-- 3) Anti-join: customers with NO orders
SELECT c.name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;                     -- NULL-check on a NOT NULL right column = "no match"

-- Result:
-- name
-- -----
-- Carol
-- Dave

-- 4) Row counts side by side
SELECT 'inner' AS join_type, COUNT(*) AS n FROM customers c INNER JOIN orders o ON o.customer_id = c.id
UNION ALL
SELECT 'left',  COUNT(*) FROM customers c LEFT  JOIN orders o ON o.customer_id = c.id
UNION ALL
SELECT 'right', COUNT(*) FROM customers c RIGHT JOIN orders o ON o.customer_id = c.id;

-- Result:
-- join_type | n
-- ----------+---
-- inner     | 3
-- left      | 5     -- 3 matches + Carol + Dave
-- right     | 4     -- 3 matches + guest order 13 (NULL name)

-- Verified: identical output on MySQL 9.1 and PostgreSQL (PGlite).
-- Without ORDER BY the row order is not guaranteed by either engine.
```

---

## 🔍 Why This Works (3 lines max)
The join condition decides matching; the join TYPE decides what happens to non-matching rows (dropped for INNER, kept with NULLs for LEFT). WHERE runs after the join, so `WHERE o.status='paid'` removes the NULL-padded rows too and the LEFT JOIN degrades to an INNER JOIN.
हिंदी: Join type तय करता है unmatched rows का क्या होगा; WHERE बाद में चलता है और NULL वाली rows हटा देता है।

---

## ⚡ Alternative Solution

```sql
-- Keep the LEFT JOIN semantics AND filter the right table: put the filter in ON
SELECT c.name, o.id AS order_id, o.amount
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id
 AND o.status = 'paid'                  -- filter applied BEFORE NULL-padding
ORDER BY c.id, o.id;

-- Result: Alice(10), Bob(12), Carol(NULL), Dave(NULL)   -- 4 rows, Carol/Dave survive

-- Same filter in WHERE:
SELECT c.name, o.id AS order_id, o.amount
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.status = 'paid';
-- Result: Alice(10), Bob(12)             -- only 2 rows, Carol/Dave lost

-- Anti-join alternative (often same plan): NOT EXISTS
SELECT c.name FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- MySQL vs PgSQL: both support INNER/LEFT/RIGHT.
-- FULL OUTER JOIN exists in PostgreSQL only; MySQL emulates it with LEFT JOIN UNION RIGHT JOIN.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: COUNT(*) after LEFT JOIN counts the NULL-padded row as 1
SELECT c.name, COUNT(*) AS cnt FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id GROUP BY c.id, c.name;
-- Carol -> 1, Dave -> 1   (misleading: they have zero orders)

-- ✅ Correct: count a column from the right table (NULLs are ignored)
SELECT c.name, COUNT(o.id) AS cnt FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id GROUP BY c.id, c.name;
-- Alice 2, Bob 1, Carol 0, Dave 0   (verified)

-- ❌ Wrong: LEFT JOIN ... WHERE o.status = 'paid'  (acts like INNER JOIN)
-- ✅ Correct: move it to ON, or write WHERE o.status = 'paid' OR o.id IS NULL
```

---

## 🎯 Interview Tip (1 line)
Say: "INNER drops unmatched rows, LEFT preserves the left side with NULLs — and for a LEFT JOIN, predicates on the right table belong in ON, not WHERE, otherwise I silently convert it to an INNER JOIN; I also use COUNT(right.col) instead of COUNT(*) to count children correctly."

---

## 🔗 Related Questions
→ Q222 (WHERE vs HAVING) | Q041 (INNER JOIN output question) | Q042 (LEFT JOIN null detection) | Q005 (IN vs EXISTS)
