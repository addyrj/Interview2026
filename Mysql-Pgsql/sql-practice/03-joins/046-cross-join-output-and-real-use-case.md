---

# Q046. CROSS JOIN — Output + Real Use Case
# Category: Joins
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
What does CROSS JOIN return and how many rows? Show two real use cases: (1) generate all product variants (size x color), (2) build a "store x month" report skeleton so months with zero sales still appear.

---

## 💡 Quick Concept (2 lines only)
CROSS JOIN returns the Cartesian product: every row of A paired with every row of B, so rows = |A| x |B| and there is no ON clause. Real uses: combinatorial generation, report skeletons (dimension x dimension), then LEFT JOIN facts onto it.
हिंदी: CROSS JOIN = हर row का हर row से जोड़, rows = m x n। Variants और zero-sales report skeleton बनाने में काम आता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE sizes  (size_code  VARCHAR(5)  PRIMARY KEY);
CREATE TABLE colors (color_name VARCHAR(20) PRIMARY KEY);
CREATE TABLE stores (store_id INT PRIMARY KEY, store_name VARCHAR(50));
CREATE TABLE months (month_start DATE PRIMARY KEY);
CREATE TABLE store_sales (
  sale_id    INT PRIMARY KEY,
  store_id   INT,
  sale_month DATE,
  amount     DECIMAL(10,2)
);

INSERT INTO sizes  VALUES ('S'), ('M'), ('L');
INSERT INTO colors VALUES ('Black'), ('Navy');
INSERT INTO stores VALUES (1, 'Mumbai'), (2, 'Delhi');
INSERT INTO months VALUES ('2024-01-01'), ('2024-02-01'), ('2024-03-01');
INSERT INTO store_sales VALUES
  (1, 1, '2024-01-01', 5000.00),
  (2, 1, '2024-03-01', 7000.00),
  (3, 2, '2024-02-01', 4000.00);   -- Delhi has no Jan/Mar sales, Mumbai has no Feb sales

-- ============================================
-- USE CASE 1: all product variants (3 sizes x 2 colors = 6 rows)
-- ============================================

SELECT s.size_code, c.color_name
FROM sizes s
CROSS JOIN colors c            -- no ON clause: every size pairs with every color
ORDER BY s.size_code, c.color_name;
-- Output:
-- size_code | color_name
-- L         | Black
-- L         | Navy
-- M         | Black
-- M         | Navy
-- S         | Black
-- S         | Navy

-- Row count check: 3 x 2
SELECT COUNT(*) AS variant_count FROM sizes CROSS JOIN colors;
-- Output:
-- variant_count
-- 6

-- ============================================
-- USE CASE 2: report skeleton (store x month) + LEFT JOIN facts
-- ============================================

-- Step 1: CROSS JOIN builds all 2 x 3 = 6 combinations
-- Step 2: LEFT JOIN brings in real sales; missing combos get NULL -> COALESCE to 0
SELECT st.store_name,
       m.month_start,
       COALESCE(SUM(ss.amount), 0.00) AS revenue
FROM stores st
CROSS JOIN months m
LEFT JOIN store_sales ss
       ON ss.store_id   = st.store_id
      AND ss.sale_month = m.month_start
GROUP BY st.store_name, m.month_start
ORDER BY st.store_name, m.month_start;
-- Output:
-- store_name | month_start | revenue
-- Delhi      | 2024-01-01  | 0.00
-- Delhi      | 2024-02-01  | 4000.00
-- Delhi      | 2024-03-01  | 0.00
-- Mumbai     | 2024-01-01  | 5000.00
-- Mumbai     | 2024-02-01  | 0.00
-- Mumbai     | 2024-03-01  | 7000.00

-- Without the skeleton, a plain GROUP BY on store_sales would return only 3 rows
-- (missing months silently disappear from the report/chart).

-- ============================================
-- IMPLICIT CROSS JOIN (old comma syntax) - same result, avoid it
-- ============================================

SELECT COUNT(*) AS same_count FROM sizes, colors;
-- Output:
-- same_count
-- 6
```

---

## 🔍 Why This Works (3 lines max)
CROSS JOIN has no join predicate, so every pair survives: 3 sizes x 2 colors = 6, 2 stores x 3 months = 6. LEFT JOIN of the facts onto that skeleton keeps all 6 pairs and fills gaps with NULL, which COALESCE turns into 0.
हिंदी: CROSS JOIN में condition नहीं होती, सारे pairs बनते हैं। Skeleton पर LEFT JOIN करने से missing months भी 0 के साथ दिखते हैं।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL: generate the month skeleton on the fly with generate_series (no months table needed)
SELECT st.store_name, m::date AS month_start
FROM stores st
CROSS JOIN generate_series('2024-01-01'::date, '2024-03-01'::date, interval '1 month') AS m
ORDER BY st.store_name, month_start;
-- Output:
-- store_name | month_start
-- Delhi      | 2024-01-01
-- Delhi      | 2024-02-01
-- Delhi      | 2024-03-01
-- Mumbai     | 2024-01-01
-- Mumbai     | 2024-02-01
-- Mumbai     | 2024-03-01
```

```sql
-- MySQL has no generate_series: use a recursive CTE (8.0+) to build the same skeleton
WITH RECURSIVE m (month_start) AS (
  SELECT DATE '2024-01-01'
  UNION ALL
  SELECT month_start + INTERVAL 1 MONTH FROM m WHERE month_start < '2024-03-01'
)
SELECT st.store_name, m.month_start
FROM stores st
CROSS JOIN m
ORDER BY st.store_name, m.month_start;
-- Output:
-- store_name | month_start
-- Delhi      | 2024-01-01
-- Delhi      | 2024-02-01
-- Delhi      | 2024-03-01
-- Mumbai     | 2024-01-01
-- Mumbai     | 2024-02-01
-- Mumbai     | 2024-03-01
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: forgetting the join condition by accident (comma join / missing ON)
SELECT * FROM orders o, customers c;
-- 1M orders x 50K customers = 50 BILLION rows. Query "hangs" and fills temp disk.

-- ❌ Wrong: putting the fact filter in WHERE after LEFT JOIN on a skeleton
--   ... LEFT JOIN store_sales ss ON ss.store_id = st.store_id
--   WHERE ss.sale_month = m.month_start      -- turns LEFT JOIN into INNER JOIN, zero rows vanish again
-- ✅ Put both conditions in the ON clause (as in the solution above)
```

---

## 🎯 Interview Tip (1 line)
Say: "CROSS JOIN is a deliberate Cartesian product - I use it for dimension skeletons (store x month, user x feature flag) and then LEFT JOIN facts so gaps show as zero; an accidental one is a classic production incident, so I always check row-count estimates in EXPLAIN."

---

## 🔗 Related Questions
→ Q042 (LEFT JOIN with NULL detection) | Q047 (JOIN with aggregation) | Q050 (LATERAL JOIN) | Q048 (Multi-table JOIN)
