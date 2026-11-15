---

# Q006. BETWEEN and Edge Cases
# Category: Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Use BETWEEN to filter amounts and dates on a `payments` table. What happens with reversed bounds, with a timestamp column and a date upper bound ("all of March"), with NULLs, and with strings? What is the safer pattern for date ranges?

---

## 💡 Quick Concept (2 lines only)
`x BETWEEN a AND b` is exactly `x >= a AND x <= b` - both ends inclusive, and `a` must be the smaller value. For timestamps, `BETWEEN '2024-03-01' AND '2024-03-31'` means midnight at the start of Mar 31, so it silently drops the rest of that day.
हिंदी: BETWEEN दोनों सिरे शामिल करता है और छोटा मान पहले चाहिए; timestamp में 31 तारीख 00:00 पर कट जाती है, इसलिए half-open range बेहतर है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE payments (
  id      INT PRIMARY KEY,
  amount  DECIMAL(10,2),
  paid_at TIMESTAMP NULL,
  grade   VARCHAR(5)
);

INSERT INTO payments VALUES
  (1, 100.00, '2024-03-01 00:00:00', 'a'),
  (2, 200.00, '2024-03-15 10:30:00', 'B'),
  (3, 200.01, '2024-03-31 00:00:00', 'c'),
  (4, 300.00, '2024-03-31 15:45:00', 'D'),   -- last day of March, afternoon
  (5, 400.00, '2024-04-01 00:00:00', 'e'),
  (6, NULL,   NULL,                  NULL);

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: inclusive on both ends (100 and 200 both match)
SELECT id, amount FROM payments WHERE amount BETWEEN 100 AND 200 ORDER BY id;

-- Step 2: reversed bounds = (x >= 200 AND x <= 100) = always false
SELECT id, amount FROM payments WHERE amount BETWEEN 200 AND 100 ORDER BY id;

-- Step 3: BETWEEN on a timestamp with date-only upper bound (the classic bug)
SELECT id, paid_at FROM payments
WHERE paid_at BETWEEN '2024-03-01' AND '2024-03-31' ORDER BY id;

-- Step 4: the safe pattern - half-open range [start, next_start)
SELECT id, paid_at FROM payments
WHERE paid_at >= '2024-03-01' AND paid_at < '2024-04-01' ORDER BY id;

-- ============================================
-- EXPECTED OUTPUT (identical on MySQL 9.1.0 and PGlite)
-- ============================================

-- Step 1: ids 1 (100.00), 2 (200.00)      <- id 3 (200.01) excluded, id 6 (NULL) excluded
-- Step 2: (0 rows)
-- Step 3: ids 1, 2, 3                     <- id 4 (Mar 31 15:45) is MISSING
-- Step 4: ids 1, 2, 3, 4                  <- correct; id 5 (Apr 1 00:00) rightly excluded
```

---

## 🔍 Why This Works (3 lines max)
The date literal `'2024-03-31'` is cast to `2024-03-31 00:00:00`, so anything later that day fails `<=`. A half-open range `>= start AND < next_start` has no gap or overlap between consecutive ranges and also works for DATETIME, TIMESTAMP and fractional seconds. It also stays index-friendly (no function on the column).
हिंदी: `'2024-03-31'` का मतलब 00:00:00 है, इसलिए उस दिन की बाकी rows छूट जाती हैं; `>= start AND < next_start` हमेशा सही रहता है।

---

## ⚡ Alternative Solution

```sql
-- NOT BETWEEN also drops NULL rows (NULL is neither inside nor outside):
SELECT id, amount FROM payments WHERE amount NOT BETWEEN 150 AND 350 ORDER BY id;
-- Output: ids 1 (100.00), 5 (400.00)   <- id 6 (NULL) NOT returned

-- PostgreSQL ONLY: BETWEEN SYMMETRIC auto-swaps reversed bounds
SELECT id FROM payments WHERE amount BETWEEN SYMMETRIC 200 AND 100 ORDER BY id;
-- PGlite output: 1, 2     |  MySQL 9.1.0: ERROR 1064 syntax error near '200 AND 100'
-- MySQL/portable: WHERE amount BETWEEN LEAST(200,100) AND GREATEST(200,100)

-- Strings compare by collation, so results can differ between engines:
SELECT id, grade FROM payments WHERE grade BETWEEN 'B' AND 'D' ORDER BY id;
-- MySQL (case-insensitive collation): ids 2, 3, 4  ('c' falls between B and D)
-- PGlite (C-style byte ordering, 'c' > 'D'): ids 2, 4
-- A PostgreSQL database created with en_US.UTF-8 collation may differ again - always test.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "all of March" with BETWEEN on a timestamp column
WHERE paid_at BETWEEN '2024-03-01' AND '2024-03-31'      -- drops Mar 31 after 00:00:00
-- ❌ Also wrong: BETWEEN '2024-03-01' AND '2024-03-31 23:59:59'  -- misses 23:59:59.5 (fractional seconds)
-- ✅ WHERE paid_at >= '2024-03-01' AND paid_at < '2024-04-01'

-- ❌ Wrong: BETWEEN with bounds in the wrong order (silently returns 0 rows, no error)
-- ✅ Put the smaller value first, or use SYMMETRIC (PgSQL) / LEAST+GREATEST (MySQL)
```

---

## 🎯 Interview Tip (1 line)
Say: "BETWEEN is inclusive on both sides, so for timestamps I always use a half-open range - `>= start AND < next_period_start` - which avoids the end-of-day bug and fractional-second gaps."

---

## 🔗 Related Questions
→ Q010 (Date/time functions) | Q003 (NULL handling) | Q001 (SELECT/WHERE/ORDER BY/LIMIT) | Q008 (Type casting)
