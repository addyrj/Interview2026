---

# Q007. CASE WHEN - Output Question
# Category: Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Predict the output: a grading query written as `CASE WHEN marks >= 40 THEN 'Pass' WHEN marks >= 60 THEN 'Second' WHEN marks >= 90 THEN 'Distinction' END`. What does each student get, what happens for NULL marks, and how do you fix it? Also show CASE for pivoting counts, custom ORDER BY and a conditional UPDATE.

---

## 💡 Quick Concept (2 lines only)
CASE evaluates WHEN branches top to bottom and returns the FIRST true one; with no ELSE the result is NULL. A NULL condition is never true, so NULL input falls through to ELSE (or NULL).
हिंदी: CASE ऊपर से नीचे पहली true शर्त पर रुक जाता है; ELSE न हो तो NULL मिलता है, और NULL marks हमेशा ELSE में जाते हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE students (
  id    INT PRIMARY KEY,
  name  VARCHAR(50),
  marks INT,
  city  VARCHAR(20)
);

INSERT INTO students VALUES
  (1, 'Aman',   92, 'Delhi'),
  (2, 'Bina',   75, 'Pune'),
  (3, 'Chirag', 60, 'Delhi'),
  (4, 'Divya',  45, 'Pune'),
  (5, 'Esha',   NULL, 'Delhi'),    -- absent
  (6, 'Farid',  80, NULL);         -- unknown city

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: the BUGGY query - broadest condition first
SELECT name, marks,
  CASE WHEN marks >= 40 THEN 'Pass'
       WHEN marks >= 60 THEN 'Second'        -- unreachable!
       WHEN marks >= 90 THEN 'Distinction'   -- unreachable!
  END AS wrong_order
FROM students ORDER BY id;

-- Step 2: FIX - most specific first, add ELSE
SELECT name, marks,
  CASE WHEN marks >= 90 THEN 'Distinction'
       WHEN marks >= 60 THEN 'First'
       WHEN marks >= 40 THEN 'Pass'
       ELSE 'Fail'
  END AS result
FROM students ORDER BY id;

-- Step 3: handle NULL explicitly (before any comparison)
SELECT name,
  CASE WHEN marks IS NULL THEN 'Absent'
       WHEN marks >= 40   THEN 'Pass'
       ELSE 'Fail'
  END AS result
FROM students ORDER BY id;

-- ============================================
-- EXPECTED OUTPUT (identical on MySQL 9.1.0 and PGlite)
-- ============================================

-- Step 1 wrong_order:  Aman Pass | Bina Pass | Chirag Pass | Divya Pass | Esha NULL | Farid Pass
--                      (everyone >= 40 is "Pass"; Esha has no ELSE so NULL)
-- Step 2 result:       Aman Distinction | Bina First | Chirag First | Divya Pass
--                      Esha Fail  <- NULL fell to ELSE (misleading!) | Farid First
-- Step 3 result:       Aman Pass | Bina Pass | Chirag Pass | Divya Pass | Esha Absent | Farid Pass
```

---

## 🔍 Why This Works (3 lines max)
Branches are checked in order and evaluation stops at the first TRUE, so ordering from most to least specific matters. `marks >= 40` with NULL gives UNKNOWN, which is not TRUE, so the branch is skipped. Test `IS NULL` first (or use ELSE deliberately).
हिंदी: पहली true branch जीतती है, इसलिए specific शर्त पहले रखो; NULL पर comparison UNKNOWN होता है, तो `IS NULL` पहले check करो।

---

## ⚡ Alternative Solution

```sql
-- Simple CASE (equality only) - same syntax on both engines
SELECT name, CASE city WHEN 'Delhi' THEN 'North' WHEN 'Pune' THEN 'West' ELSE 'Unknown' END AS zone
FROM students ORDER BY id;
-- Output: Aman North | Bina West | Chirag North | Divya West | Esha North | Farid Unknown
-- Simple CASE uses "=", so `CASE city WHEN NULL` never matches (Farid -> 'no-match' on both engines)

-- Pivot-style conditional counts (SUM(CASE) or COUNT(CASE) - COUNT ignores the NULL from missing ELSE)
SELECT SUM(CASE WHEN city = 'Delhi' THEN 1 ELSE 0 END) AS delhi_cnt,
       COUNT(CASE WHEN city = 'Pune' THEN 1 END)       AS pune_cnt,
       COUNT(*) AS total
FROM students;
-- Output: delhi_cnt 3 | pune_cnt 2 | total 6

-- CASE in ORDER BY: highest marks first, NULLs last (portable; PgSQL also has NULLS LAST)
SELECT name, marks FROM students
ORDER BY CASE WHEN marks IS NULL THEN 1 ELSE 0 END, marks DESC;
-- Output: Aman 92, Farid 80, Bina 75, Chirag 60, Divya 45, Esha NULL
-- (MySQL sorts NULL first by default for ASC, PostgreSQL sorts NULL last for ASC - CASE removes the ambiguity)

-- Conditional UPDATE (grace marks): rows keep their value via ELSE
UPDATE students SET marks = CASE WHEN marks < 50 THEN marks + 5 ELSE marks END;
-- Divya 45 -> 50, Esha stays NULL (NULL < 50 is UNKNOWN -> ELSE -> NULL)

-- Type difference: branches must share a type in PostgreSQL
SELECT CASE WHEN 1 = 2 THEN 1 ELSE 'x' END;
-- MySQL 9.1.0: returns 'x'   |  PGlite: ERROR: invalid input syntax for type integer: "x"
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: overlapping ranges with the broad condition first (Step 1 above)
CASE WHEN marks >= 40 THEN 'Pass' WHEN marks >= 90 THEN 'Distinction' END
-- ✅ Order from most restrictive to least, or use BETWEEN/non-overlapping ranges

-- ❌ Wrong: forgetting ELSE - unmatched rows become NULL, not an error
-- ❌ Wrong: relying on ELSE to catch NULL - Esha is "Fail" although she was absent
-- ✅ Add an explicit `WHEN marks IS NULL THEN 'Absent'` branch
```

---

## 🎯 Interview Tip (1 line)
Say: "CASE is an expression - first match wins, no ELSE means NULL, NULL never satisfies a comparison - and I use SUM(CASE ...) for conditional aggregation instead of multiple queries."

---

## 🔗 Related Questions
→ Q003 (NULL handling) | Q006 (BETWEEN) | Q008 (Type casting) | Q075 (Top N per group)
