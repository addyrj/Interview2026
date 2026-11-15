---

# Q069. NTILE() — Divide into Buckets
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite (PostgreSQL)

---

## ❓ Question
Split 10 students into 4 score quartiles (1 = top). What happens when 10 rows do not divide evenly?

---

## 💡 Quick Concept (2 lines only)
NTILE(n) splits the ordered partition into n buckets of (nearly) equal ROW count. When rows % n != 0, the first buckets get one extra row.
हिंदी: NTILE(n) rows को n बराबर buckets में बाँटता है; बचे हुए rows शुरू के buckets में जाते हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE students (
  id    INT PRIMARY KEY,
  name  VARCHAR(50),
  score INT
);

INSERT INTO students VALUES
 (1,'Asha',95),(2,'Bilal',88),(3,'Chitra',82),(4,'Dev',77),(5,'Esha',70),
 (6,'Farhan',65),(7,'Gita',60),(8,'Harsh',55),(9,'Isha',40),(10,'Jai',35);

-- ============================================
-- SOLUTION
-- ============================================

SELECT name, score,
       NTILE(4) OVER (ORDER BY score DESC) AS quartile   -- 1 = highest scores
FROM students
ORDER BY score DESC;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- name   | score | quartile
-- -------+-------+---------
-- Asha   | 95    | 1
-- Bilal  | 88    | 1
-- Chitra | 82    | 1
-- Dev    | 77    | 2
-- Esha   | 70    | 2
-- Farhan | 65    | 2
-- Gita   | 60    | 3
-- Harsh  | 55    | 3
-- Isha   | 40    | 4
-- Jai    | 35    | 4
-- (10 rows / 4 buckets -> sizes 3,3,2,2 -- extras go to buckets 1 and 2)

-- Bucket summary:
SELECT quartile, COUNT(*) AS students, MIN(score) AS min_score, MAX(score) AS max_score
FROM (SELECT score, NTILE(4) OVER (ORDER BY score DESC) AS quartile FROM students) t
GROUP BY quartile ORDER BY quartile;
-- quartile | students | min_score | max_score
-- 1        | 3        | 82        | 95
-- 2        | 3        | 65        | 77
-- 3        | 2        | 55        | 60
-- 4        | 2        | 35        | 40
```

---

## 🔍 Why This Works (3 lines max)
NTILE numbers rows by position, not by value, so it never looks at score ranges. Ties can land in different buckets unless you add a tiebreaker to ORDER BY.
हिंदी: NTILE value नहीं, row position देखता है; ties अलग buckets में जा सकते हैं, इसलिए tiebreaker लगाओ।

---

## ⚡ Alternative Solution

```sql
-- Top 10% (decile 1) -- NTILE(10) on 10 rows = 1 row per bucket
SELECT name, score FROM (
  SELECT name, score, NTILE(10) OVER (ORDER BY score DESC) AS decile FROM students
) t WHERE decile = 1;
-- Asha | 95

-- 7 rows into 3 buckets -> sizes 3,2,2
SELECT name, NTILE(3) OVER (ORDER BY score DESC) AS bucket
FROM (SELECT * FROM students WHERE id <= 7) s;

-- Value-based alternative: PERCENT_RANK() / CUME_DIST() (position by percentile, not equal-size buckets)
-- MySQL vs PgSQL: identical NTILE syntax and results (verified).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming equal-width score ranges (0-25, 26-50 ...) -- NTILE is equal COUNT
-- ❌ Wrong: no tiebreaker -> equal scores may fall in different buckets nondeterministically
NTILE(3) OVER (ORDER BY score DESC)
-- ✅ Add a unique tiebreaker for deterministic output
NTILE(3) OVER (ORDER BY score DESC, id)
-- ❌ Wrong: expecting NTILE to drop empty buckets: if rows < n, only the first `rows` buckets are used
```

---

## 🎯 Interview Tip (1 line)
Say: "NTILE gives equal-sized buckets by row count - great for quartiles/deciles - but it splits ties arbitrarily, so I add a tiebreaker or use PERCENT_RANK/CUME_DIST when ties must stay together."

---

## 🔗 Related Questions
→ Q066 (RANK family) | Q075 (top N per group) | Q072 (percent of total)
