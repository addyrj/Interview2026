---

# Q005. IN vs EXISTS - Which Is Faster?
# Category: Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Find customers who have placed at least one order, and customers who have placed none. Compare `IN`, `EXISTS`, and `JOIN`, explain which is faster, and show the NULL trap with `NOT IN`.

---

## 💡 Quick Concept (2 lines only)
Modern optimizers (MySQL 8+, PostgreSQL) rewrite both `IN (subquery)` and `EXISTS` into the same semi-join, so performance is usually identical - the real difference is correctness with NULLs. `NOT EXISTS` is NULL-safe; `NOT IN` is not.
हिंदी: आज के optimizer में IN और EXISTS दोनों semi-join बन जाते हैं, speed लगभग same; असली फ़र्क NULL में है - NOT IN खतरनाक, NOT EXISTS safe।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE customers (
  id   INT PRIMARY KEY,
  name VARCHAR(50)
);

CREATE TABLE orders (
  id          INT PRIMARY KEY,
  customer_id INT,                 -- nullable on purpose (guest checkout)
  amount      DECIMAL(10,2)
);
CREATE INDEX idx_orders_cust ON orders(customer_id);   -- index on the correlated column

INSERT INTO customers VALUES (1,'Asha'), (2,'Ben'), (3,'Chitra'), (4,'Dev');
INSERT INTO orders VALUES
  (1, 1,    500),
  (2, 1,    250),
  (3, 3,    120),
  (4, NULL,  80);                  -- guest order, customer_id is NULL

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: customers WITH orders - IN
SELECT id, name FROM customers
WHERE id IN (SELECT customer_id FROM orders) ORDER BY id;

-- Step 2: same with EXISTS (correlated; stops at the first match per customer)
SELECT c.id, c.name FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id) ORDER BY c.id;

-- Step 3: customers WITHOUT orders - NOT EXISTS (NULL-safe)
SELECT c.id, c.name FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id) ORDER BY c.id;

-- ============================================
-- EXPECTED OUTPUT (identical on MySQL 9.1.0 and PGlite)
-- ============================================

-- Step 1 and Step 2:        Step 3:
-- id | name                 id | name
--  1 | Asha                  2 | Ben
--  3 | Chitra                4 | Dev

-- MySQL 9.1.0 EXPLAIN FORMAT=TREE for BOTH the IN and the EXISTS version printed the same plan:
--   Nested loop inner join (LooseScan) -> covering index scan on idx_orders_cust
--   -> single-row PRIMARY lookup on customers
-- i.e. the optimizer turned both into the same semi-join.
```

---

## 🔍 Why This Works (3 lines max)
A semi-join returns each outer row at most once, as soon as one match exists, so no duplicates and no full inner scan. Both syntaxes express a semi-join, and the optimizer picks the best physical plan. Index on `orders(customer_id)` is what really matters.
हिंदी: Semi-join हर outer row को एक बार लौटाता है; दोनों syntax वही बनते हैं, असली speed `orders(customer_id)` index से आती है।

---

## ⚡ Alternative Solution

```sql
-- JOIN + DISTINCT: same customers, but JOIN multiplies rows, so DISTINCT is required
SELECT DISTINCT c.id, c.name FROM customers c JOIN orders o ON o.customer_id = c.id ORDER BY c.id;
-- Output: 1 Asha, 3 Chitra
-- Without DISTINCT: Asha appears TWICE (she has 2 orders) - verified on both engines

-- Anti-join via LEFT JOIN (customers with no orders):
SELECT c.id, c.name
FROM customers c LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;
-- Output: 2 Ben, 4 Dev

-- NOT IN made safe (filter NULLs in the subquery):
SELECT id, name FROM customers
WHERE id NOT IN (SELECT customer_id FROM orders WHERE customer_id IS NOT NULL);
-- Output: 2 Ben, 4 Dev

-- Rule of thumb: IN suits a small, uncorrelated list; EXISTS suits correlated checks and
-- multi-column conditions. Always confirm with EXPLAIN (EXPLAIN ANALYZE in PostgreSQL).
-- Syntax is the same on both engines for all queries above.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: NOT IN when the subquery can return NULL
SELECT id, name FROM customers WHERE id NOT IN (SELECT customer_id FROM orders);
-- Output on BOTH engines: 0 rows!  (order 4 has customer_id NULL -> id <> NULL is UNKNOWN)
-- Ben and Dev silently disappear - no error, wrong answer.
-- ✅ Use NOT EXISTS (returns Ben, Dev) or add WHERE customer_id IS NOT NULL

-- ❌ Wrong: "EXISTS is always faster" folklore
-- True on very old MySQL (< 5.6) with no semi-join; today it's the same plan.
-- ❌ Wrong: SELECT * inside EXISTS "for performance" - the select list is ignored; SELECT 1 is convention.
```

---

## 🎯 Interview Tip (1 line)
Say: "IN and EXISTS compile to the same semi-join in modern MySQL and PostgreSQL, so I decide by readability and NULL-safety - always NOT EXISTS over NOT IN - and I verify with EXPLAIN and an index on the join column."

---

## 🔗 Related Questions
→ Q003 (NULL handling) | Q002 (DISTINCT) | Q239 (Find duplicates) | Q185 (LATERAL join)
