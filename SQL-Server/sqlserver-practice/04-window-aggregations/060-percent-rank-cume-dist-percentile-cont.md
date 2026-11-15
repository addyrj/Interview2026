# Q060. PERCENT_RANK, CUME_DIST, PERCENTILE_CONT
# Category: WINDOW FUNCTIONS + AGGREGATIONS
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (2012+) — in PostgreSQL PERCENTILE_CONT is a normal ordered-set aggregate (no OVER); MySQL has no PERCENTILE_CONT

---

## ❓ Question
Given exam scores, show each student's PERCENT_RANK and CUME_DIST, the median score using PERCENTILE_CONT and PERCENTILE_DISC, and the 90th percentile. Explain how the functions differ when there are ties.

---

## 💡 Quick Concept (2 lines only)
PERCENT_RANK = (rank - 1) / (rows - 1), CUME_DIST = (rows with value <= current) / rows. PERCENTILE_CONT interpolates between values; PERCENTILE_DISC picks an actual value from the data.
हिंदी: PERCENT_RANK 0 से शुरू होता है, CUME_DIST कभी 0 नहीं होता। CONT = interpolation, DISC = असली value।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE ExamScores (
    Student VARCHAR(10) NOT NULL PRIMARY KEY,
    Score   INT         NOT NULL
);

INSERT INTO ExamScores (Student, Score) VALUES
 ('Aman', 50), ('Bela', 60), ('Chirag', 60), ('Dev', 80), ('Esha', 95);

-- ============================================
-- SOLUTION (T-SQL: PERCENTILE_* are WINDOW functions -> need OVER, no ORDER BY inside OVER)
-- ============================================
SELECT
    Student, Score,
    PERCENT_RANK() OVER (ORDER BY Score) AS PctRank,
    CUME_DIST()    OVER (ORDER BY Score) AS CumeDist,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Score) OVER () AS MedianCont,
    PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY Score) OVER () AS MedianDisc,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY Score) OVER () AS P90
FROM ExamScores
ORDER BY Score, Student;

-- EXPECTED OUTPUT (result derived from equivalent query on PostgreSQL (PGlite) using scalar subqueries for the percentiles; not executed on SQL Server):
-- Student | Score | PctRank | CumeDist | MedianCont | MedianDisc | P90
-- Aman    | 50    | 0       | 0.2      | 60         | 60         | 89
-- Bela    | 60    | 0.25    | 0.6      | 60         | 60         | 89
-- Chirag  | 60    | 0.25    | 0.6      | 60         | 60         | 89
-- Dev     | 80    | 0.75    | 0.8      | 60         | 60         | 89
-- Esha    | 95    | 1       | 1        | 60         | 60         | 89
-- (SQL Server returns these as FLOAT; display formatting of trailing digits may differ)
-- P90 by hand: position = 0.9 * (5-1) = 3.6 -> between 80 (index 3) and 95 (index 4): 80 + 0.6*15 = 89
```

---

## 🔍 Why This Works (3 lines max)
Ties share one rank, so Bela and Chirag both get PercentRank (2-1)/(5-1) = 0.25, and CUME_DIST counts both of them (3 of 5 = 0.6). PERCENTILE_CONT finds the fractional position (n-1)*p in the sorted list and interpolates; with an even row count the median would be the average of the two middle rows. In T-SQL the PERCENTILE functions repeat the same value on every row, so use DISTINCT or TOP 1 to collapse it.
हिंदी: Ties को same rank मिलती है। PERCENTILE_CONT बीच की value interpolate करता है, DISC data की असली value देता है।

---

## ⚡ Alternative Solution

```sql
-- One row per group: collapse the repeated window value with DISTINCT
SELECT DISTINCT
    Dept,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Salary) OVER (PARTITION BY Dept) AS MedianSalary
FROM Employees;   -- Employees table as created in Q059
-- Not executed here (PGlite has no OVER form of percentile_cont); semantics per Microsoft docs.

-- Pre-2012 / "bucket" approach: NTILE(100) gives a percentile bucket per row
SELECT Student, Score, NTILE(4) OVER (ORDER BY Score) AS Quartile FROM ExamScores;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Using PostgreSQL syntax in SQL Server: aggregate form without OVER
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY Score) FROM ExamScores;   -- error in T-SQL: OVER clause is required

-- ❌ Putting ORDER BY in the OVER clause of PERCENTILE_CONT -> only PARTITION BY is allowed there;
--    the ordering goes inside WITHIN GROUP

-- ❌ Mixing up PERCENT_RANK and CUME_DIST: PERCENT_RANK of the lowest row is always 0,
--    CUME_DIST of the highest row is always 1 and of any row is > 0

-- ❌ Using PERCENTILE_DISC and expecting an average of the middle two rows for an even count
```

---

## 🎯 Interview Tip (1 line)
Say: "In SQL Server PERCENTILE_CONT is a window function, so I partition with OVER and dedupe the result; on large tables I check the plan because it sorts per partition. If the team is on PostgreSQL the same logic is an ordered-set aggregate, and MySQL needs a ROW_NUMBER workaround."

---

## 🔗 Related Questions
→ Q056 (ROW_NUMBER, RANK, DENSE_RANK, NTILE) | Q064 (Median calculation) | Q058 (SUM/AVG OVER with frames) | Q067 (Top-N per group with window functions)
