---

# Q072. Percent of Total Using Window Function
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite (PostgreSQL)

---

## ❓ Question
For each product show its revenue as a percentage of (a) total company revenue and (b) its own category. Also show category revenue share.

---

## 💡 Quick Concept (2 lines only)
SUM(x) OVER () is the grand total repeated on every row; SUM(x) OVER (PARTITION BY g) is the group total. Divide the row value by it - no self-join needed.
हिंदी: SUM() OVER () हर row पर total देता है, उससे भाग देकर percentage निकालो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE product_sales (
  id       INT PRIMARY KEY,
  category VARCHAR(30),
  product  VARCHAR(30),
  revenue  DECIMAL(10,2)
);

INSERT INTO product_sales VALUES
 (1,'Electronics','Laptop',5000),(2,'Electronics','Phone',3000),(3,'Electronics','Tablet',2000),
 (4,'Books','Novel',600),(5,'Books','Textbook',400),(6,'Grocery','Rice',1000);

-- ============================================
-- SOLUTION
-- ============================================

SELECT category, product, revenue,
  ROUND(100 * revenue / SUM(revenue) OVER (), 2)                   AS pct_of_total,
  ROUND(100 * revenue / SUM(revenue) OVER (PARTITION BY category), 2) AS pct_of_category
FROM product_sales
ORDER BY category, revenue DESC;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- category    | product  | revenue | pct_of_total | pct_of_category
-- ------------+----------+---------+--------------+----------------
-- Books       | Novel    |  600.00 |  5.00        |  60.00
-- Books       | Textbook |  400.00 |  3.33        |  40.00
-- Electronics | Laptop   | 5000.00 | 41.67        |  50.00
-- Electronics | Phone    | 3000.00 | 25.00        |  30.00
-- Electronics | Tablet   | 2000.00 | 16.67        |  20.00
-- Grocery     | Rice     | 1000.00 |  8.33        | 100.00

-- Share of each category (window over an aggregate: SUM(SUM(x)) OVER ())
SELECT category, SUM(revenue) AS cat_revenue,
       ROUND(100 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 2) AS pct_of_total
FROM product_sales GROUP BY category ORDER BY cat_revenue DESC;
-- Electronics | 10000.00 | 83.33
-- Books/Grocery | 1000.00 | 8.33 each (tie: their relative order is not guaranteed)
```

---

## 🔍 Why This Works (3 lines max)
Window functions run after GROUP BY/WHERE and keep every row, so each row can see the total next to its own value. SUM(SUM(x)) OVER () first aggregates per group, then sums those group totals.
हिंदी: Window function row नहीं घटाता, इसलिए हर row के साथ total मिलता है; SUM(SUM(x)) OVER () group-level share देता है।

---

## ⚡ Alternative Solution

```sql
-- CROSS JOIN with a one-row total (works everywhere, even without window support)
SELECT p.product, p.revenue, ROUND(100 * p.revenue / t.total, 2) AS pct
FROM product_sales p
CROSS JOIN (SELECT SUM(revenue) AS total FROM product_sales) t
ORDER BY p.id;
-- 41.67, 25.00, 16.67, 5.00, 3.33, 8.33

-- Cumulative % (Pareto): add ORDER BY inside the first window
SELECT product, ROUND(100 * SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER (), 2) AS cum_pct
FROM product_sales ORDER BY revenue DESC;
-- Laptop 41.67, Phone 66.67, Tablet 83.33, Rice 91.67, Novel 96.67, Textbook 100.00

-- MySQL vs PgSQL: same syntax and values. Only the unrounded division differs in digits
-- (MySQL 1.000000, PostgreSQL 1.00000000000000000000), so ROUND explicitly.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: integer division when the column is INT -> 0
SELECT 100 * clicks / SUM(clicks) OVER () FROM stats;   -- PostgreSQL: integer division truncates
-- ✅ Multiply first / cast: 100.0 * clicks / SUM(clicks) OVER ()   (not run: stats table is illustrative)
-- ❌ Wrong: using GROUP BY then losing product rows; ❌ dividing by zero if total = 0
-- ✅ Guard: revenue / NULLIF(SUM(revenue) OVER (), 0)
```

---

## 🎯 Interview Tip (1 line)
Say: "Percent of total is value / SUM(value) OVER () - one scan, no self-join - and I guard with NULLIF for zero totals and cast to decimal before dividing so integer columns don't truncate."

---

## 🔗 Related Questions
→ Q070 (running total) | Q073 (PARTITION BY vs GROUP BY) | Q064 (ROLLUP)
