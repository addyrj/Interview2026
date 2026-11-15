---

# Q186. LATERAL JOIN with Function
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL (MySQL 8.0.14+ supports LATERAL for derived tables, not table functions)

---

## ❓ Question
Use `LATERAL` to call a set-returning function (or subquery) once per row of another table: "last 2 orders per customer" via a SQL function, keeping customers with no orders. Explain `CROSS JOIN LATERAL` vs `LEFT JOIN LATERAL ... ON true`.

---

## 💡 Quick Concept (2 lines only)
`LATERAL` lets a FROM item reference columns of FROM items to its left, so a function or subquery runs once per outer row. Use `CROSS JOIN LATERAL` (or plain comma) to drop outer rows with no result, and `LEFT JOIN LATERAL ... ON true` to keep them.
हिंदी: LATERAL से बाईं तरफ की table के columns function/subquery में use होते हैं, हर row पर एक बार चलता है; खाली result वाली rows रखनी हों तो LEFT JOIN LATERAL ON true।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) - verified on PostgreSQL 18.6 (PGlite)
-- ============================================

CREATE TABLE customers (id INT PRIMARY KEY, name TEXT, tier TEXT);
CREATE TABLE orders (id INT PRIMARY KEY, customer_id INT, amount NUMERIC(10,2), created_at DATE);

INSERT INTO customers VALUES (1,'Asha','gold'),(2,'Bilal','silver'),(3,'Chen','gold'),(4,'Divya','bronze');  -- Divya: no orders
INSERT INTO orders VALUES
 (1,1,120.00,'2024-01-05'),(2,1,80.00,'2024-02-10'),(3,1,200.00,'2024-03-15'),(4,1,50.00,'2024-04-01'),
 (5,2,300.00,'2024-01-20'),(6,2,45.00,'2024-03-02'),
 (7,3,75.00,'2024-02-14');

CREATE FUNCTION recent_orders(p_customer INT, p_limit INT)
RETURNS TABLE (order_id INT, amount NUMERIC, created_at DATE)
LANGUAGE sql STABLE AS $$
  SELECT id, amount, created_at FROM orders
  WHERE customer_id = p_customer ORDER BY created_at DESC LIMIT p_limit
$$;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: CROSS JOIN LATERAL - customers with no orders disappear
SELECT c.name, r.order_id, r.amount, r.created_at
FROM customers c
CROSS JOIN LATERAL recent_orders(c.id, 2) r
ORDER BY c.id, r.created_at DESC;
-- name  | order_id | amount | created_at
-- Asha  | 4        | 50.00  | 2024-04-01
-- Asha  | 3        | 200.00 | 2024-03-15
-- Bilal | 6        | 45.00  | 2024-03-02
-- Bilal | 5        | 300.00 | 2024-01-20
-- Chen  | 7        | 75.00  | 2024-02-14        <- Divya missing

-- Step 2: LEFT JOIN LATERAL ... ON true - keep customers without orders
SELECT c.name, r.order_id, r.amount
FROM customers c
LEFT JOIN LATERAL recent_orders(c.id, 2) r ON true
ORDER BY c.id, r.created_at DESC;
-- Asha 4 50.00 | Asha 3 200.00 | Bilal 6 45.00 | Bilal 5 300.00 | Chen 7 75.00 | Divya NULL NULL

-- Step 3: functions in FROM are implicitly LATERAL (comma form), so LATERAL keyword is optional for functions
SELECT c.name, r.order_id FROM customers c, recent_orders(c.id, 1) r ORDER BY c.id;
-- Asha 4 | Bilal 6 | Chen 7

-- Step 4: aggregate per outer row with a LATERAL subquery
SELECT c.name, s.total, s.n
FROM customers c
CROSS JOIN LATERAL (
  SELECT sum(amount) AS total, count(*) AS n FROM orders o WHERE o.customer_id = c.id
) s
ORDER BY c.id;
-- Asha 450.00 4 | Bilal 345.00 2 | Chen 75.00 1 | Divya NULL 0     <- aggregate subquery always returns 1 row

-- Step 5: variable-length expansion per row
SELECT c.name, g.d
FROM customers c
CROSS JOIN LATERAL generate_series(1, CASE c.tier WHEN 'gold' THEN 2 ELSE 1 END) AS g(d)
ORDER BY c.id, g.d;
-- Asha 1,2 | Bilal 1 | Chen 1,2 | Divya 1

-- Step 6: unnest an expression built from the outer row
SELECT c.name, j.k FROM customers c
CROSS JOIN LATERAL unnest(ARRAY[c.name, upper(c.tier)]) AS j(k) WHERE c.id <= 2 ORDER BY 1,2;
-- Asha Asha | Asha GOLD | Bilal Bilal | Bilal SILVER
```

---

## 🔍 Why This Works (3 lines max)
The planner executes the right side as a parameterised nested loop: for each outer row it passes `c.id` in and gets 0..N rows back, which makes "top-N per group" cheap with an index on `(customer_id, created_at DESC)`. `LEFT JOIN LATERAL ... ON true` is a left join with a condition that is always true, so only emptiness of the lateral result decides whether the NULL row appears.
हिंदी: हर outer row के लिए right side parameter के साथ चलता है; `LEFT JOIN ... ON true` खाली result पर भी outer row बचाता है।

---

## ⚡ Alternative Solution

```sql
-- Window-function version (scans everything once, good when most groups are needed):
SELECT name, order_id, amount FROM (
  SELECT c.name, o.id AS order_id, o.amount,
         ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY o.created_at DESC) AS rn
  FROM customers c JOIN orders o ON o.customer_id = c.id
) x WHERE rn <= 2;

-- Rule of thumb: LATERAL wins when few outer rows / big inner table + index; window wins for "all groups".

-- MySQL 8.0.14+: LATERAL derived table works, but there are no table-returning functions:
--   SELECT c.name, r.id FROM customers c
--   LEFT JOIN LATERAL (SELECT id FROM orders o WHERE o.customer_id = c.id ORDER BY created_at DESC LIMIT 2) r ON true;
--   (MySQL syntax from documentation; not run in this verification set.)
-- Older MySQL: correlated subqueries or ROW_NUMBER() (Q075).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Referencing the outer table in an ordinary derived table
SELECT c.name FROM customers c, (SELECT * FROM orders WHERE customer_id = c.id LIMIT 1) x;
-- ERROR: invalid reference to FROM-clause entry for table "c"   (real error)
-- ✅ Add the LATERAL keyword: ..., LATERAL (SELECT ...) x

-- ❌ CROSS JOIN LATERAL when you need customers without orders -> Divya silently vanishes
-- ✅ LEFT JOIN LATERAL (...) ON true

-- ❌ LATERAL subquery with no index on the lookup column -> N full scans (a nested loop of seq scans).
-- ✅ CREATE INDEX ON orders (customer_id, created_at DESC);

-- ❌ Putting a real condition in ON when you wanted a filter: ON r.amount > 100 turns LEFT into odd semantics. Keep ON true, filter inside.
```

---

## 🎯 Interview Tip (1 line)
Say: "LATERAL is a per-row parameterised subquery; I use it for top-N-per-group and to call set-returning functions with outer columns, with a matching index so each probe is an index seek, and LEFT JOIN LATERAL ON true when I must keep empty groups."

---

## 🔗 Related Questions
→ Q075 (Top N per group) | Q050 (LATERAL join intro) | Q185 (LISTEN/NOTIFY - unrelated PgSQL feature) | Q183 (unnest)
