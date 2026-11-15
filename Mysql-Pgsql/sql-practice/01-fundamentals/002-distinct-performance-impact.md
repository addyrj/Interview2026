---

# Q002. DISTINCT and Its Performance Impact
# Category: Fundamentals
# Difficulty: ⭐ Easy
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
From a `page_views` table, list the distinct countries, distinct (country, device) pairs, and the number of unique users. Then explain why `DISTINCT` can be slow, how an index helps, and why "DISTINCT to fix duplicate rows" is a code smell.

---

## 💡 Quick Concept (2 lines only)
DISTINCT deduplicates the whole selected row (not just the first column) using a sort or hash step, so cost grows with row count and number of columns. An index on the distinct column lets the engine walk unique values instead of scanning and sorting everything.
हिंदी: DISTINCT पूरी row का duplicate हटाता है (sort/hash से), बड़ी table पर महँगा; सही index हो तो सिर्फ unique values पढ़ता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE page_views (
  id        INT PRIMARY KEY,
  user_id   INT,
  country   VARCHAR(20),
  device    VARCHAR(20),
  viewed_at DATE
);

INSERT INTO page_views VALUES
  (1, 101, 'IN', 'mobile',  '2024-05-01'),
  (2, 101, 'IN', 'mobile',  '2024-05-02'),
  (3, 101, 'IN', 'desktop', '2024-05-03'),
  (4, 102, 'US', 'mobile',  '2024-05-01'),
  (5, 103, 'IN', 'desktop', '2024-05-02'),
  (6, 103, 'IN', 'desktop', '2024-05-04'),
  (7, 104, NULL, 'mobile',  '2024-05-04'),   -- NULL country
  (8, 105, NULL, 'mobile',  '2024-05-05');   -- NULL counts as ONE distinct value

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: distinct single column (NULLs collapse into one NULL row)
SELECT DISTINCT country FROM page_views ORDER BY country;

-- Step 2: distinct applies to the COMBINATION of all selected columns
SELECT DISTINCT country, device FROM page_views ORDER BY country, device;

-- Step 3: counting unique values (COUNT(DISTINCT) ignores NULL)
SELECT COUNT(*)                   AS total_rows,
       COUNT(DISTINCT user_id)    AS unique_users,
       COUNT(DISTINCT country)    AS unique_countries
FROM page_views;

-- Step 4: index so the engine can skip duplicates instead of scanning everything
CREATE INDEX idx_pv_country ON page_views(country);

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Step 1 (NULL ordering DIFFERS: MySQL 9.1.0 puts NULL first, PostgreSQL/PGlite puts NULL last)
-- MySQL:        PostgreSQL:
-- NULL          IN
-- IN            US
-- US            NULL

-- Step 2 (MySQL; PostgreSQL same rows but NULL row last):
-- country | device
-- NULL    | mobile
-- IN      | desktop
-- IN      | mobile
-- US      | mobile

-- Step 3 (same on both):
-- total_rows | unique_users | unique_countries
--          8 |            5 |                2

-- MySQL 9.1.0 EXPLAIN SELECT DISTINCT country ... (after the index):
--   type=range, key=idx_pv_country, Extra="Using index for group-by"
-- EXPLAIN SELECT DISTINCT device ... (no index on device):
--   type=ALL, Extra="Using temporary"   <- full scan + temp table
```

---

## 🔍 Why This Works (3 lines max)
DISTINCT compares the full tuple of selected columns, so adding a column can increase the result size. Without an index the engine builds a temp table / hash / sort to dedupe; with an index on the column it can jump between unique values (loose index scan in MySQL, index-only scan in PostgreSQL).
हिंदी: Selected सभी columns मिलकर unique माने जाते हैं; index न हो तो temp table/sort लगता है, index हो तो सीधे unique values पर कूदता है।

---

## ⚡ Alternative Solution

```sql
-- GROUP BY gives the same result as DISTINCT (and lets you add aggregates):
SELECT country FROM page_views GROUP BY country ORDER BY country;

-- Users seen on more than one device:
SELECT user_id, COUNT(DISTINCT device) AS devices
FROM page_views
GROUP BY user_id
HAVING COUNT(DISTINCT device) > 1;
-- Output: 101 | 2

-- PostgreSQL ONLY: DISTINCT ON = latest row per user (MySQL: syntax error, verified)
SELECT DISTINCT ON (user_id) user_id, device, viewed_at
FROM page_views
ORDER BY user_id, viewed_at DESC;
-- PGlite output: 101 desktop 2024-05-03 | 102 mobile 2024-05-01 | 103 desktop 2024-05-04
--                104 mobile 2024-05-04 | 105 mobile 2024-05-05
-- MySQL equivalent: ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY viewed_at DESC) = 1
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: DISTINCT is NOT a function applied to one column
SELECT id, DISTINCT country FROM page_views;
-- MySQL: ERROR 1064 syntax error;  PostgreSQL: ERROR: syntax error at or near "DISTINCT"
-- ✅ DISTINCT goes right after SELECT and covers ALL columns:
SELECT DISTINCT country, device FROM page_views;

-- ❌ Wrong: slapping DISTINCT on a join to hide a fan-out bug
-- SELECT DISTINCT o.* FROM orders o JOIN order_items i ON i.order_id = o.id;
-- ✅ Use EXISTS (or fix the join) so duplicates are never produced:
-- SELECT o.* FROM orders o WHERE EXISTS (SELECT 1 FROM order_items i WHERE i.order_id = o.id);
```

---

## 🎯 Interview Tip (1 line)
Say: "If I need DISTINCT to make a join correct, the join is probably wrong - I'd use EXISTS or fix the grain; and for real dedupe I back it with an index and check EXPLAIN for temp tables or sorts."

---

## 🔗 Related Questions
→ Q005 (IN vs EXISTS) | Q003 (NULL handling) | Q075 (Top N per group) | Q239 (Find duplicates)
