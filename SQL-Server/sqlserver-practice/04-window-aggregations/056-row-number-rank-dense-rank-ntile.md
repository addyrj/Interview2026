---

# Q056. ROW_NUMBER, RANK, DENSE_RANK, NTILE
# Category: Window Functions & Aggregations
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (2005+; same functions in MySQL 8 and PostgreSQL; NTILE bucket sizes follow the same rule)

---

## ❓ Question
For a `Students(StudentId, Name, Score)` table show each student's ROW_NUMBER, RANK, DENSE_RANK and NTILE(3) side by side, explain how ties behave, and say which function to use for "top 3", "rank with gaps" and "split into quartiles/thirds".

---

## 💡 Quick Concept (2 lines only)
All four need `OVER (ORDER BY ...)`. ROW_NUMBER = unique 1,2,3...; RANK = ties share a number and the next number is skipped; DENSE_RANK = ties share a number with no skip; NTILE(n) = split rows into n nearly equal buckets.
हिंदी: ROW_NUMBER = हर row को unique नंबर। RANK = ties को same नंबर, फिर gap। DENSE_RANK = ties same, gap नहीं। NTILE(n) = n बराबर हिस्सों में बाँटना।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Students (
  StudentId INT PRIMARY KEY,
  Name      VARCHAR(100) NOT NULL,
  Score     INT          NOT NULL
);

INSERT INTO Students (StudentId, Name, Score) VALUES
  (1, 'Asha',   95),
  (2, 'Bhavna', 90),
  (3, 'Chetan', 90),   -- tied with Bhavna
  (4, 'Deepak', 85),
  (5, 'Esha',   80),
  (6, 'Farhan', 80),   -- tied with Esha
  (7, 'Gita',   70);

-- ============================================
-- ALL FOUR SIDE BY SIDE
-- ============================================
SELECT Name, Score,
       ROW_NUMBER() OVER (ORDER BY Score DESC, StudentId) AS RowNum,
       RANK()       OVER (ORDER BY Score DESC)            AS Rnk,
       DENSE_RANK() OVER (ORDER BY Score DESC)            AS DenseRnk,
       NTILE(3)     OVER (ORDER BY Score DESC, StudentId) AS Bucket
FROM Students
ORDER BY Score DESC, StudentId;

-- EXPECTED OUTPUT (derived on SQLite; these window functions behave the same in SQL Server):
-- Name   | Score | RowNum | Rnk | DenseRnk | Bucket
-- Asha   | 95    | 1      | 1   | 1        | 1
-- Bhavna | 90    | 2      | 2   | 2        | 1
-- Chetan | 90    | 3      | 2   | 2        | 1
-- Deepak | 85    | 4      | 4   | 3        | 2
-- Esha   | 80    | 5      | 5   | 4        | 2
-- Farhan | 80    | 6      | 5   | 4        | 3
-- Gita   | 70    | 7      | 7   | 5        | 3

-- NTILE(3) on 7 rows: 7 / 3 = 2 remainder 1, so the first bucket gets the extra row (3, 2, 2).
-- Result derived on SQLite; not executed on SQL Server (documented NTILE behaviour matches).

-- ============================================
-- PER-GROUP RANKING (add PARTITION BY)
-- ============================================
-- ROW_NUMBER() OVER (PARTITION BY Class ORDER BY Score DESC)   -- rank restarts per class
-- (Students has no Class column in this demo; see Q047 for a full per-department example.)
```

---

## 🔍 Why This Works (3 lines max)
Each function numbers the rows after sorting by the OVER clause. ROW_NUMBER never repeats (so you must add a tiebreaker for repeatable results), RANK repeats on ties and then jumps by the tie count (1,2,2,4), DENSE_RANK repeats without jumping (1,2,2,3), and NTILE distributes rows into buckets, giving the extra rows to the first buckets.
हिंदी: ROW_NUMBER कभी repeat नहीं होता (tiebreaker लगाओ)। RANK ties के बाद नंबर छोड़ता है (1,2,2,4), DENSE_RANK नहीं छोड़ता (1,2,2,3)। NTILE बचे हुए rows पहले buckets को देता है।

---

## ⚡ Alternative Solution

```sql
-- Which one to choose:
--   "Exactly top 3 rows"                -> ROW_NUMBER   (WHERE rn <= 3)
--   "Competition ranking, gaps ok"      -> RANK         (Olympic style: two golds, no silver)
--   "Top 3 distinct scores / levels"    -> DENSE_RANK   (WHERE dr <= 3)
--   "Quartiles / deciles / thirds"      -> NTILE(4) / NTILE(10) / NTILE(3)

-- Window functions cannot be used in WHERE, so wrap in a CTE:
WITH Ranked AS (
  SELECT Name, Score, DENSE_RANK() OVER (ORDER BY Score DESC) AS dr
  FROM Students
)
SELECT Name, Score FROM Ranked WHERE dr <= 3 ORDER BY Score DESC, Name;

-- For true percentile logic prefer PERCENT_RANK / CUME_DIST (Q060): NTILE buckets are equal-SIZE, not equal-VALUE,
-- and tied scores can land in different buckets (Esha is in bucket 2, Farhan in bucket 3 above).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: ROW_NUMBER without a tiebreaker when results must be repeatable
ROW_NUMBER() OVER (ORDER BY Score DESC)
-- Bhavna and Chetan can swap row numbers between executions. Add StudentId.

-- ❌ Wrong: window function in WHERE
SELECT Name FROM Students WHERE RANK() OVER (ORDER BY Score DESC) <= 3;   -- error: windowed functions
-- only allowed in SELECT or ORDER BY. Use a CTE / subquery.

-- ❌ Wrong: ORDER BY missing inside OVER for ranking functions -> syntax error in SQL Server
-- (ROW_NUMBER / RANK / DENSE_RANK / NTILE require ORDER BY; PARTITION BY is optional.)

-- ❌ Wrong: assuming NTILE buckets split by value. They split by row COUNT only.
```

---

## 🎯 Interview Tip (1 line)
Say: "ROW_NUMBER for unique ordering and dedupe/top-N, RANK for competition-style gaps, DENSE_RANK for 'Nth distinct', NTILE for equal-sized buckets. I always add a unique tiebreaker to ROW_NUMBER, and remember that window functions cannot appear in WHERE so I filter in an outer CTE."

---

## 🔗 Related Questions
→ Q047 (top N per group) | Q045 (Nth highest salary) | Q066 (deduplicate with ROW_NUMBER) | Q060 (PERCENT_RANK, CUME_DIST, PERCENTILE_CONT)
