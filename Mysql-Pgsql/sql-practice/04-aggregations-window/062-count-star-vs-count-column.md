---

# Q062. COUNT(*) vs COUNT(column) — NULL Difference
# Category: Aggregations & Window Functions
# Difficulty: ⭐ Easy
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite (PostgreSQL)

---

## ❓ Question
In a `customers` table where some phone and city values are NULL, what do `COUNT(*)`, `COUNT(phone)`, `COUNT(DISTINCT city)` return? How do you count missing values?

---

## 💡 Quick Concept (2 lines only)
COUNT(*) counts rows (NULLs irrelevant); COUNT(column) counts only rows where that column is NOT NULL; COUNT(DISTINCT col) counts distinct non-NULL values.
हिंदी: COUNT(*) सब rows गिनता है, COUNT(col) NULL छोड़ देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE customers (
  id    INT PRIMARY KEY,
  name  VARCHAR(50),
  email VARCHAR(100),
  phone VARCHAR(20),
  city  VARCHAR(30)
);

INSERT INTO customers VALUES
 (1,'Asha',  'asha@x.com',  '9990001111','Delhi'),
 (2,'Bilal', 'bilal@x.com', NULL,        'Delhi'),
 (3,'Chitra','chitra@x.com','9990003333','Pune'),
 (4,'Dev',   'dev@x.com',   NULL,        'Pune'),
 (5,'Esha',  'esha@x.com',  NULL,        NULL),
 (6,'Farhan','farhan@x.com','9990006666','Delhi');

-- ============================================
-- SOLUTION
-- ============================================

SELECT
  COUNT(*)             AS total_rows,       -- every row
  COUNT(1)             AS count_one,        -- same as COUNT(*)
  COUNT(phone)         AS with_phone,       -- skips NULL phone
  COUNT(city)          AS with_city,        -- skips NULL city
  COUNT(DISTINCT city) AS distinct_cities,  -- distinct non-NULL
  COUNT(*) - COUNT(phone) AS missing_phone  -- trick to count NULLs
FROM customers;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- total_rows | count_one | with_phone | with_city | distinct_cities | missing_phone
-- -----------+-----------+------------+-----------+-----------------+--------------
-- 6          | 6         | 3          | 5         | 2               | 3

-- Per group (NULL city forms its own group):
SELECT city, COUNT(*) AS customers, COUNT(phone) AS with_phone
FROM customers GROUP BY city ORDER BY city;
-- city  | customers | with_phone
-- Delhi | 3         | 2
-- Pune  | 2         | 1
-- NULL  | 1         | 0
-- NOTE: ORDER BY puts NULL FIRST in MySQL, LAST in PostgreSQL (shown: PostgreSQL).
-- Empty input: COUNT(*) and COUNT(col) return 0 (not NULL), unlike SUM/AVG.
```

---

## 🔍 Why This Works (3 lines max)
Aggregate functions ignore NULL inputs, except COUNT(*) which has no column argument and counts rows. COUNT(1) and COUNT(*) are identical in both engines.
हिंदी: Aggregates NULL को ignore करते हैं, सिर्फ COUNT(*) row गिनता है।

---

## ⚡ Alternative Solution

```sql
-- Count NULLs explicitly (portable)
SELECT SUM(CASE WHEN phone IS NULL THEN 1 ELSE 0 END) AS missing_phone FROM customers;
-- Result: 3

-- PostgreSQL only: FILTER clause (cleaner)
SELECT COUNT(*) FILTER (WHERE phone IS NULL) AS missing_phone FROM customers;
-- (verified: works in PGlite; MySQL 9.1 gives ERROR 1064 syntax error, use the CASE form above)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: <> never matches NULL (NULL <> 'x' is UNKNOWN)
SELECT COUNT(*) FROM customers WHERE phone <> '9990001111';
-- Result: 2   (the 3 NULL-phone rows silently vanish)

-- ✅ Correct: handle NULL explicitly
SELECT COUNT(*) FROM customers WHERE phone IS NULL OR phone <> '9990001111';
-- Result: 5
```

---

## 🎯 Interview Tip (1 line)
Say: "COUNT(*) counts rows, COUNT(col) counts non-NULL values — so COUNT(*) - COUNT(col) gives the NULL count; and I always check NULL behaviour of <> and NOT IN because the three-valued logic hides rows."

---

## 🔗 Related Questions
→ Q063 (aggregates with NULL) | Q061 (HAVING vs WHERE) | Q077 (mode)
