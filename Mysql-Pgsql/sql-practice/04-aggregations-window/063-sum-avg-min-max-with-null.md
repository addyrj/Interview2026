---

# Q063. SUM/AVG/MIN/MAX with NULL
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite (PostgreSQL)

---

## ❓ Question
Some employees have a NULL `bonus`. What do SUM, AVG, MIN, MAX return, and how do you get the average bonus over ALL staff (treating NULL as 0)?

---

## 💡 Quick Concept (2 lines only)
SUM/AVG/MIN/MAX skip NULL inputs; if no non-NULL value exists the result is NULL (not 0). AVG divides by the count of non-NULL rows only.
हिंदी: Aggregates NULL skip करते हैं, और सब NULL हों तो result NULL आता है, 0 नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE emp_pay (
  id     INT PRIMARY KEY,
  name   VARCHAR(50),
  dept   VARCHAR(30),
  salary DECIMAL(10,2),
  bonus  DECIMAL(10,2)
);

INSERT INTO emp_pay VALUES
 (1,'Asha',  'Eng',  100000, 10000),
 (2,'Bilal', 'Eng',   90000, NULL),
 (3,'Chitra','Eng',   80000, 0),        -- 0 is NOT NULL
 (4,'Dev',   'Sales', 70000, NULL),
 (5,'Esha',  'Sales', 60000, NULL);

-- ============================================
-- SOLUTION
-- ============================================

SELECT SUM(bonus) AS sum_bonus, AVG(bonus) AS avg_bonus,
       MIN(bonus) AS min_bonus, MAX(bonus) AS max_bonus,
       COUNT(bonus) AS cnt_bonus, COUNT(*) AS cnt_rows
FROM emp_pay;

-- sum_bonus | avg_bonus | min_bonus | max_bonus | cnt_bonus | cnt_rows
-- ----------+-----------+-----------+-----------+-----------+---------
-- 10000.00  | 5000      | 0.00      | 10000.00  | 2         | 5
-- (avg = 10000 / 2 non-NULL rows. MySQL shows 5000.000000, PgSQL 5000.0000000000000000)

-- Average over ALL staff: treat NULL as 0
SELECT AVG(COALESCE(bonus, 0)) AS avg_bonus_all_staff FROM emp_pay;
-- Result: 2000   (10000 / 5)

-- Group with all-NULL values -> NULL, wrap with COALESCE for reports
SELECT dept, SUM(bonus) AS sum_bonus, COALESCE(SUM(bonus), 0) AS sum_or_zero
FROM emp_pay GROUP BY dept ORDER BY dept;
-- dept  | sum_bonus | sum_or_zero
-- Eng   | 10000.00  | 10000.00
-- Sales | NULL      | 0 (PgSQL: 0, MySQL: 0.00)
```

---

## 🔍 Why This Works (3 lines max)
Aggregates are defined to drop NULL inputs, so AVG(bonus) = SUM/COUNT(bonus), not SUM/COUNT(*). COALESCE inside the aggregate changes the denominator; COALESCE outside only fixes an empty result.
हिंदी: AVG सिर्फ non-NULL rows से भाग देता है; सब staff चाहिए तो COALESCE(bonus,0) अंदर लगाओ।

---

## ⚡ Alternative Solution

```sql
-- Equivalent: sum divided by all rows
SELECT SUM(bonus) / COUNT(*) AS avg_all FROM emp_pay;   -- 2000 in both engines

-- Empty set: SUM/AVG/MAX return NULL, COUNT returns 0
SELECT SUM(bonus), AVG(bonus), MAX(bonus) FROM emp_pay WHERE 1 = 0;
-- NULL | NULL | NULL

-- Syntax is identical in MySQL and PgSQL; only the decimal display
-- precision of AVG differs (6 vs 16 decimals).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: NULL poisons row-level arithmetic, so rows disappear from the SUM
SELECT SUM(salary + bonus) FROM emp_pay;
-- Result: 190000.00  (only Asha and Chitra counted!)

-- ✅ Correct
SELECT SUM(salary + COALESCE(bonus, 0)) FROM emp_pay;     -- 410000.00
SELECT SUM(salary) + SUM(bonus) FROM emp_pay;             -- 410000.00 (also fine)
```

---

## 🎯 Interview Tip (1 line)
Say: "Aggregates ignore NULL, so AVG's denominator is non-NULL rows — I decide explicitly whether NULL means 'unknown' or 'zero' and use COALESCE accordingly, and I remember NULL + x is NULL at row level."

---

## 🔗 Related Questions
→ Q062 (COUNT NULL) | Q061 (HAVING) | Q072 (percent of total)
