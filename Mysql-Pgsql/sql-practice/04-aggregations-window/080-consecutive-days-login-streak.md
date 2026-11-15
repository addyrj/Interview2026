---

# Q080. Consecutive Days Login Streak
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL) - date arithmetic differs

---

## ❓ Question
From `user_logins`, find every user's login **streaks** (runs of consecutive calendar days) with start, end and length. Then get each user's longest streak, and users with a streak of 3+ days. Duplicate logins on the same day must not break or inflate a streak.

---

## 💡 Quick Concept (2 lines only)
Gap-and-island on dates: dedupe to one row per user per day, then `login_date - ROW_NUMBER()` days is constant inside a streak. Group by it for start/end/length.
हिंदी: पहले हर user-दिन की एक row बनाओ, फिर date minus ROW_NUMBER दिन = streak id; उसी पर GROUP BY करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE user_logins (
  id         INT PRIMARY KEY,
  user_id    INT NOT NULL,
  login_date DATE NOT NULL
);

INSERT INTO user_logins VALUES
  (1, 1, '2024-05-01'), (2, 1, '2024-05-02'), (3, 1, '2024-05-03'),
  (4, 1, '2024-05-03'),                                   -- duplicate login same day
  (5, 1, '2024-05-05'), (6, 1, '2024-05-06'),             -- 05-04 missed -> streak breaks
  (7, 2, '2024-05-01'),
  (8, 2, '2024-05-03'), (9, 2, '2024-05-04'), (10, 2, '2024-05-05'),
  (11, 2, '2024-05-06'), (12, 2, '2024-05-07'),
  (13, 3, '2024-05-10');

-- ============================================
-- SOLUTION - MySQL 8.0+
-- ============================================

-- Step 1: daily   = DISTINCT user/day (removes duplicate logins)
-- Step 2: numbered = ROW_NUMBER per user ordered by date
-- Step 3: grp     = date minus rn days  (constant within a streak)
-- Step 4: GROUP BY user, grp

WITH daily AS (
  SELECT DISTINCT user_id, login_date FROM user_logins
),
numbered AS (
  SELECT user_id, login_date,
         ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS rn
  FROM daily
),
streaks AS (
  SELECT user_id, login_date,
         DATE_SUB(login_date, INTERVAL rn DAY) AS grp      -- MySQL date arithmetic
  FROM numbered
)
SELECT user_id,
       MIN(login_date) AS streak_start,
       MAX(login_date) AS streak_end,
       COUNT(*)        AS streak_days
FROM streaks
GROUP BY user_id, grp
ORDER BY user_id, streak_start;

-- ============================================
-- SOLUTION - PostgreSQL (only the grp line changes)
-- ============================================
--   login_date - rn::int AS grp        -- DATE minus INTEGER = DATE in PgSQL

-- ============================================
-- EXPECTED OUTPUT (verified on MySQL 9.1 and PGlite)
-- ============================================

-- user_id | streak_start | streak_end | streak_days
-- --------+--------------+------------+------------
-- 1       | 2024-05-01   | 2024-05-03 | 3
-- 1       | 2024-05-05   | 2024-05-06 | 2
-- 2       | 2024-05-01   | 2024-05-01 | 1
-- 2       | 2024-05-03   | 2024-05-07 | 5
-- 3       | 2024-05-10   | 2024-05-10 | 1

-- Longest streak per user (wrap the query above in a CTE `agg`, then MAX):
--   SELECT user_id, MAX(streak_days) AS longest_streak FROM agg GROUP BY user_id;
-- user_id | longest_streak
-- 1       | 3
-- 2       | 5
-- 3       | 1

-- Users with a streak of at least 3 days -> add  HAVING COUNT(*) >= 3  to the GROUP BY query
-- Result: user_id 1 and 2
```

---

## 🔍 Why This Works (3 lines max)
Consecutive dates increase by 1 day and ROW_NUMBER also by 1, so `date - rn` stays the same; any missed day makes the date jump and the group value change. DISTINCT first is essential, otherwise a duplicate day shifts rn.
हिंदी: लगातार दिनों में date और rn दोनों +1 बढ़ते हैं, इसलिए date - rn स्थिर रहता है; दिन छूटा तो वैल्यू बदल जाती है।

---

## ⚡ Alternative Solution

```sql
-- LAG flag + running SUM (works the same in both DBs except the date difference)
WITH daily AS (
  SELECT DISTINCT user_id, login_date FROM user_logins
),
flagged AS (
  SELECT user_id, login_date,
         CASE WHEN DATEDIFF(login_date,
                   LAG(login_date) OVER (PARTITION BY user_id ORDER BY login_date)) = 1
              THEN 0 ELSE 1 END AS is_new            -- 1 = a new streak starts here
         -- PgSQL: CASE WHEN login_date - LAG(login_date) OVER (...) = 1 ...
  FROM daily
),
grouped AS (
  SELECT user_id, login_date,
         SUM(is_new) OVER (PARTITION BY user_id ORDER BY login_date) AS streak_id
  FROM flagged
)
SELECT user_id, streak_id,
       MIN(login_date) AS streak_start, MAX(login_date) AS streak_end, COUNT(*) AS streak_days
FROM grouped
GROUP BY user_id, streak_id
ORDER BY user_id, streak_id;
-- Same 5 rows as above, with streak_id 1,2 for user 1 and 1,2 for user 2, 1 for user 3.
-- First row of each user: LAG is NULL -> comparison is NULL -> ELSE 1 (new streak). Correct.
-- Prefer this form if you also need to treat gaps of N days as a streak (change "= 1" to "<= N").
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: skipping the DISTINCT step
-- User 1 has two logins on 2024-05-03: rn becomes 3 and 4 for the same date,
-- date - rn differs, and the 05-01..05-03 streak is split into pieces.
-- ✅ Always dedupe to one row per user per day first (SELECT DISTINCT or GROUP BY).

-- ❌ Wrong: using a timestamp column directly
-- '2024-05-03 09:00' - rn gives different values than expected; CAST/DATE() it first:
--   MySQL: DATE(login_ts)      PgSQL: login_ts::date

-- ❌ Wrong: copying MySQL's DATE_SUB(..., INTERVAL rn DAY) into PostgreSQL
-- PgSQL has no DATE_SUB. Use:  login_date - rn::int   (or login_date - rn * INTERVAL '1 day')
-- and for DATEDIFF use plain subtraction: date1 - date2 (returns integer days).
```

---

## 🎯 Interview Tip (1 line)
Say: "I dedupe to user-day first, then use the date-minus-ROW_NUMBER trick for streaks; timezone matters, so I bucket by the user's local date, and for a rolling 'current streak' I'd keep a streak_days counter updated incrementally rather than recomputing from raw events."

---

## 🔗 Related Questions
→ Q067 (LEAD/LAG) | Q078 (Cumulative distinct count) | Q079 (Gap and island problem) | Q239 (Find duplicates)
