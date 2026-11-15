---

# Q054. Most Recent Record Per Group (JOIN Pattern)
# Category: Joins
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Get each customer's most recent order (full row, not just the date) using JOIN-based patterns, and show what goes wrong with ties on the date.

---

## 💡 Quick Concept (2 lines only)
Join the table back to a per-group `MAX(date)` derived table, or use an anti-join (no newer row exists). Both are plain-JOIN answers that work even without window functions; they return multiple rows if two orders share the max timestamp.
हिंदी: Group का MAX(date) निकालकर table से वापस JOIN करो, या anti-join (इससे नया कोई नहीं)। Date tie हो तो एक से ज़्यादा rows आती हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE orders (
  order_id    INT PRIMARY KEY,
  customer_id INT,
  amount      DECIMAL(10,2),
  status      VARCHAR(20),
  order_date  DATE
);

CREATE INDEX idx_orders_cust_date ON orders (customer_id, order_date);

INSERT INTO orders VALUES
  (1, 101,  49.99, 'completed', '2024-01-10'),
  (2, 101, 149.99, 'completed', '2024-02-15'),
  (3, 101,  29.99, 'pending',   '2024-03-01'),   -- latest for 101
  (4, 102,  99.99, 'completed', '2024-01-20'),
  (5, 102, 199.99, 'refunded',  '2024-02-28'),   -- tie on date with order 6
  (6, 102,  19.99, 'completed', '2024-02-28'),   -- tie! two "latest" orders
  (7, 103,  59.99, 'completed', '2024-03-05');   -- only order

-- ============================================
-- PATTERN 1: JOIN to a MAX(date) derived table
-- ============================================

-- Step 1: derived table finds the latest date per customer
-- Step 2: join back on (customer_id, date) to fetch the full row
SELECT o.customer_id, o.order_id, o.amount, o.status, o.order_date
FROM orders o
JOIN (
  SELECT customer_id, MAX(order_date) AS max_date
  FROM orders
  GROUP BY customer_id
) latest
  ON latest.customer_id = o.customer_id
 AND latest.max_date    = o.order_date
ORDER BY o.customer_id, o.order_id;
-- Output:
-- customer_id | order_id | amount | status    | order_date
-- 101         | 3        | 29.99  | pending   | 2024-03-01
-- 102         | 5        | 199.99 | refunded  | 2024-02-28
-- 102         | 6        | 19.99  | completed | 2024-02-28
-- 103         | 7        | 59.99  | completed | 2024-03-05
-- ^ customer 102 returns BOTH orders 5 and 6 (date tie)

-- ============================================
-- PATTERN 2: anti-join "no newer row exists" with deterministic tie-break
-- ============================================

SELECT o.customer_id, o.order_id, o.amount, o.status, o.order_date
FROM orders o
LEFT JOIN orders newer
       ON newer.customer_id = o.customer_id
      AND (newer.order_date > o.order_date
           OR (newer.order_date = o.order_date AND newer.order_id > o.order_id))  -- tie-break on id
WHERE newer.order_id IS NULL          -- nobody is newer -> this row is the latest
ORDER BY o.customer_id;
-- Output:
-- customer_id | order_id | amount | status    | order_date
-- 101         | 3        | 29.99  | pending   | 2024-03-01
-- 102         | 6        | 19.99  | completed | 2024-02-28
-- 103         | 7        | 59.99  | completed | 2024-03-05
-- ^ exactly one row per customer: ties resolved by the higher order_id

-- ============================================
-- PATTERN 3: tuple comparison against the max id per date (compact but harder to read; prefer ROW_NUMBER)
-- ============================================

SELECT o.customer_id, o.order_id, o.order_date
FROM orders o
WHERE (o.customer_id, o.order_date, o.order_id) IN (
  SELECT customer_id, order_date, MAX(order_id)
  FROM orders
  WHERE (customer_id, order_date) IN (SELECT customer_id, MAX(order_date) FROM orders GROUP BY customer_id)
  GROUP BY customer_id, order_date
)
ORDER BY o.customer_id;
-- Output:
-- customer_id | order_id | order_date
-- 101         | 3        | 2024-03-01
-- 102         | 6        | 2024-02-28
-- 103         | 7        | 2024-03-05
```

---

## 🔍 Why This Works (3 lines max)
Pattern 1 reduces each group to its max date and joins back to recover the other columns that GROUP BY cannot return. Pattern 2 says "keep the row only if no newer row exists in the same group"; adding the order_id comparison makes the ordering total, so ties cannot produce two winners.
हिंदी: GROUP BY से बाकी columns नहीं मिलते, इसलिए MAX निकालकर वापस JOIN करते हैं। Tie-break (order_id) जोड़ो तो हर group से सिर्फ एक row।

---

## ⚡ Alternative Solution

```sql
-- Window function (MySQL 8+, PostgreSQL): shortest and deterministic
SELECT customer_id, order_id, amount, status, order_date
FROM (
  SELECT o.*,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC, order_id DESC) AS rn
  FROM orders o
) ranked
WHERE rn = 1
ORDER BY customer_id;
-- Output:
-- customer_id | order_id | amount | status    | order_date
-- 101         | 3        | 29.99  | pending   | 2024-03-01
-- 102         | 6        | 19.99  | completed | 2024-02-28
-- 103         | 7        | 59.99  | completed | 2024-03-05
```

```sql
-- PostgreSQL only: DISTINCT ON keeps the first row per group after ORDER BY
SELECT DISTINCT ON (customer_id) customer_id, order_id, amount, status, order_date
FROM orders
ORDER BY customer_id, order_date DESC, order_id DESC;
-- Output:
-- customer_id | order_id | amount | status    | order_date
-- 101         | 3        | 29.99  | pending   | 2024-03-01
-- 102         | 6        | 19.99  | completed | 2024-02-28
-- 103         | 7        | 59.99  | completed | 2024-03-05
-- MySQL has no DISTINCT ON: use ROW_NUMBER or Pattern 2.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: selecting non-aggregated columns with MAX() and trusting they belong to the same row
SELECT customer_id, order_id, MAX(order_date) FROM orders GROUP BY customer_id;
-- MySQL (ONLY_FULL_GROUP_BY default) and PostgreSQL reject it; with the mode off MySQL returns an
-- arbitrary order_id that is NOT the one dated MAX(order_date).

-- ❌ Wrong: Pattern 1 on a table with timestamp ties and assuming one row per group
-- ✅ Break ties with a unique column (order_id) or use ROW_NUMBER with a total ordering

-- ❌ Wrong: ORDER BY order_date DESC LIMIT 1 on the whole table (gives ONE row overall, not per customer)
-- ❌ Wrong: no (customer_id, order_date) index -> derived table and join both scan everything
```

---

## 🎯 Interview Tip (1 line)
Say: "I'd use ROW_NUMBER with a deterministic tie-break on 8.0+/PostgreSQL, or LATERAL with LIMIT 1 when I have a supporting index; the join-back-to-MAX and anti-join patterns are the pre-window-function answers, and I call out date ties because they silently return duplicates."

---

## 🔗 Related Questions
→ Q075 (Top N per group) | Q050 (LATERAL JOIN) | Q055 (Nth highest salary) | Q052 (A not in B)
