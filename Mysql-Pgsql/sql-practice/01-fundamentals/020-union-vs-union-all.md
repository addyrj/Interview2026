---

# Q020. UNION vs UNION ALL — Difference + Output
# Category: Fundamentals
# Difficulty: ⭐ Easy
# DB: Both (INTERSECT/EXCEPT need MySQL 8.0.31+ | PostgreSQL)

---

## ❓ Question
What is the difference between `UNION` and `UNION ALL`? Show the output on two overlapping customer lists, explain the performance cost, and cover ordering/column rules. Also mention `INTERSECT` and `EXCEPT`.

---

## 💡 Quick Concept (2 lines only)
`UNION` stacks result sets and removes duplicate rows (needs a sort/hash step); `UNION ALL` just appends them, keeping duplicates, so it is cheaper. Both need the same number of columns with compatible types; names come from the first SELECT.
हिंदी: UNION duplicates हटाता है (धीमा), UNION ALL सब rows रखता है (तेज़)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first; works on MySQL and PostgreSQL)
-- ============================================

CREATE TABLE customers_online (id INT PRIMARY KEY, email VARCHAR(100), city VARCHAR(30));
CREATE TABLE customers_store  (id INT PRIMARY KEY, email VARCHAR(100), city VARCHAR(30));

INSERT INTO customers_online VALUES
  (1, 'asha@mail.com',   'Pune'),
  (2, 'bala@mail.com',   'Chennai'),    -- also in store
  (3, 'chitra@mail.com', 'Delhi');      -- also in store

INSERT INTO customers_store VALUES
  (1, 'bala@mail.com',   'Chennai'),
  (2, 'chitra@mail.com', 'Delhi'),
  (3, 'dev@mail.com',    'Mumbai');

-- ============================================
-- SOLUTION
-- ============================================

-- 1) UNION: duplicates removed (row is a duplicate only if ALL selected columns match)
SELECT email, city FROM customers_online
UNION
SELECT email, city FROM customers_store
ORDER BY email;
-- email           | city
-- asha@mail.com   | Pune
-- bala@mail.com   | Chennai
-- chitra@mail.com | Delhi
-- dev@mail.com    | Mumbai            <- 4 rows

-- 2) UNION ALL: everything kept
SELECT email, city FROM customers_online
UNION ALL
SELECT email, city FROM customers_store
ORDER BY email;
-- asha@mail.com   | Pune
-- bala@mail.com   | Chennai
-- bala@mail.com   | Chennai           <- duplicate kept
-- chitra@mail.com | Delhi
-- chitra@mail.com | Delhi             <- duplicate kept
-- dev@mail.com    | Mumbai            <- 6 rows

-- 3) UNION ALL with a literal "source" column to keep track of the origin
SELECT 'online' AS source, email FROM customers_online
UNION ALL
SELECT 'store', email FROM customers_store
ORDER BY email, source;
-- source | email
-- online | asha@mail.com
-- online | bala@mail.com
-- store  | bala@mail.com
-- online | chitra@mail.com
-- store  | chitra@mail.com
-- store  | dev@mail.com

-- 4) ORDER BY / LIMIT apply to the WHOLE union (written once, at the end)
SELECT email FROM customers_online
UNION ALL
SELECT email FROM customers_store
ORDER BY email LIMIT 3;
-- asha@mail.com, bala@mail.com, bala@mail.com

-- 5) Count distinct people across both sources
SELECT COUNT(*) AS total_unique
FROM (SELECT email FROM customers_online UNION SELECT email FROM customers_store) u;
-- total_unique = 4

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- Identical on MySQL 9.1.0 and PostgreSQL 18 (PGlite) for all five queries above.
-- Without ORDER BY the row order of a UNION is not guaranteed.
```

---

## 🔍 Why This Works (3 lines max)
UNION = UNION ALL + a DISTINCT over the combined rows, which costs a sort or hash aggregate over the full result. If you know the sets cannot overlap (or duplicates are fine), UNION ALL skips that step and can also stream rows.
हिंदी: UNION = UNION ALL + DISTINCT; जब duplicates नहीं आ सकते तब हमेशा UNION ALL use करो।

---

## ⚡ Alternative Solution

```sql
-- INTERSECT: rows in BOTH; EXCEPT: rows in the first but not the second
-- (PgSQL always; MySQL only from 8.0.31 — older MySQL needs INNER JOIN / NOT EXISTS)
SELECT email, city FROM customers_online
INTERSECT
SELECT email, city FROM customers_store ORDER BY email;
-- bala@mail.com | Chennai
-- chitra@mail.com | Delhi

SELECT email, city FROM customers_online
EXCEPT                               -- PgSQL / MySQL 8.0.31+ (Oracle calls it MINUS)
SELECT email, city FROM customers_store ORDER BY email;
-- asha@mail.com | Pune

-- Pre-8.0.31 MySQL equivalent of EXCEPT:
SELECT o.email, o.city FROM customers_online o
WHERE NOT EXISTS (SELECT 1 FROM customers_store s WHERE s.email = o.email AND s.city = o.city);

-- Ordering inside a branch needs parentheses (and LIMIT): (SELECT ... ORDER BY x LIMIT 5) UNION ALL (...)
-- Type note: PgSQL is strict (INT UNION TEXT -> error); MySQL silently coerces types.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: using UNION by habit on large tables -> unnecessary sort/dedupe of millions of rows
SELECT id FROM orders_2023 UNION SELECT id FROM orders_2024;     -- partitions can't overlap!
-- ✅ Correct:
SELECT id FROM orders_2023 UNION ALL SELECT id FROM orders_2024;

-- ❌ Wrong: different number of columns
SELECT id FROM customers_online UNION SELECT email, city FROM customers_store;
-- MySQL: ERROR 1222 (21000): The used SELECT statements have a different number of columns

-- ❌ Wrong: ORDER BY with a table-qualified column after the union
... UNION ALL SELECT email FROM customers_store ORDER BY customers_online.email;
-- MySQL: ERROR 1250: Table 'customers_online' from one of the SELECTs cannot be used in global ORDER clause
-- ✅ Correct: ORDER BY email   (use the output column name or position)

-- ❌ Wrong: expecting UNION to dedupe on ONE column — it compares the whole row
-- UNION on (id, email) kept 6 rows in the id/email test because ids differ even where emails repeat.
```

---

## 🎯 Interview Tip (1 line)
Say: "UNION ALL is my default; I use UNION only when I truly need set semantics, since it adds a sort/hash dedupe — and I remember column count/type must match and ORDER BY applies to the whole result."

---

## 🔗 Related Questions
→ Q018 (CTE — recursive CTEs use UNION ALL) | Q019 (Recursive CTE) | Q239 (Find duplicates) | Q016 (RETURNING)
