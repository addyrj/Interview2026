---

# Q240. Consecutive Dates — Find Gaps and Streaks
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Given a table of user login dates, find: (1) users with a 7+ day login streak, (2) all gaps where a user missed at least one day, (3) the longest streak per user.

---

## 💡 Quick Concept (2 lines only)
The "gap-and-island" trick: for consecutive dates, (date − row_number) is constant. GROUP BY this constant to find each unbroken streak (island). Gaps = rows where LAG(date) differs by more than 1 day.
हिंदी: Consecutive dates trick = date − row_number constant रहता है consecutive rows में। Same constant = same island (streak)। Gap = LAG(date) से difference > 1।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE user_logins (
  user_id    INT,
  login_date DATE,
  PRIMARY KEY (user_id, login_date)  -- unique per user per day
);

INSERT INTO user_logins VALUES
  -- User 1: streak Jan 1-3, gap, streak Jan 5-11 (7 days!)
  (1, '2024-01-01'), (1, '2024-01-02'), (1, '2024-01-03'),
  (1, '2024-01-05'), (1, '2024-01-06'), (1, '2024-01-07'),
  (1, '2024-01-08'), (1, '2024-01-09'), (1, '2024-01-10'),
  (1, '2024-01-11'),
  -- User 2: only 4-day streak
  (2, '2024-01-01'), (2, '2024-01-02'), (2, '2024-01-03'), (2, '2024-01-04'),
  -- User 3: many small streaks
  (3, '2024-01-01'), (3, '2024-01-03'), (3, '2024-01-05'), (3, '2024-01-07');

-- ============================================
-- PART 1: FIND ALL STREAKS (Gap and Island)
-- ============================================

-- The trick: for consecutive dates, (date - ROW_NUMBER) = constant
-- Because each date increases by 1 AND each row_number increases by 1 → difference constant

WITH streaks AS (
  SELECT
    user_id,
    login_date,
    -- MySQL: DATE_SUB(login_date, INTERVAL ROW_NUMBER() OVER (...) DAY)
    login_date - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) || ' days')::interval AS grp
    -- PgSQL: subtract interval to get grp date
  FROM user_logins
)
SELECT
  user_id,
  MIN(login_date) AS streak_start,
  MAX(login_date) AS streak_end,
  COUNT(*) AS streak_length,
  (MAX(login_date) - MIN(login_date) + 1) AS days_span
FROM streaks
GROUP BY user_id, grp
ORDER BY user_id, streak_start;

-- Output:
-- user_id | streak_start | streak_end  | streak_length
-- 1       | 2024-01-01   | 2024-01-03  | 3
-- 1       | 2024-01-05   | 2024-01-11  | 7   ← 7-day streak!
-- 2       | 2024-01-01   | 2024-01-04  | 4
-- 3       | 2024-01-01   | 2024-01-01  | 1
-- 3       | 2024-01-03   | 2024-01-03  | 1
-- (each isolated day = streak of 1)

-- MySQL version:
WITH streaks AS (
  SELECT
    user_id,
    login_date,
    DATE_SUB(login_date, INTERVAL ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) DAY) AS grp
  FROM user_logins
)
SELECT
  user_id,
  MIN(login_date) AS streak_start,
  MAX(login_date) AS streak_end,
  COUNT(*) AS streak_length
FROM streaks
GROUP BY user_id, grp
ORDER BY user_id, streak_start;

-- ============================================
-- PART 2: USERS WITH A 7+ DAY STREAK
-- ============================================

WITH streaks AS (
  SELECT
    user_id,
    DATE_SUB(login_date, INTERVAL ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) DAY) AS grp
  FROM user_logins
),
streak_lengths AS (
  SELECT user_id, MIN(login_date) AS start, MAX(login_date) AS end, COUNT(*) AS len
  FROM streaks GROUP BY user_id, grp
)
SELECT DISTINCT user_id, start AS streak_start, end AS streak_end, len AS streak_days
FROM streak_lengths
WHERE len >= 7
ORDER BY user_id, streak_start;

-- Output:
-- user_id | streak_start | streak_end  | streak_days
-- 1       | 2024-01-05   | 2024-01-11  | 7

-- ============================================
-- PART 3: LONGEST STREAK PER USER
-- ============================================

WITH streaks AS (
  SELECT
    user_id,
    DATE_SUB(login_date, INTERVAL ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) DAY) AS grp
  FROM user_logins
),
streak_lengths AS (
  SELECT user_id, COUNT(*) AS len, MIN(login_date) AS start, MAX(login_date) AS end
  FROM streaks GROUP BY user_id, grp
),
max_streaks AS (
  SELECT user_id, MAX(len) AS max_streak
  FROM streak_lengths GROUP BY user_id
)
SELECT sl.user_id, sl.len AS longest_streak, sl.start, sl.end
FROM streak_lengths sl
JOIN max_streaks ms ON sl.user_id = ms.user_id AND sl.len = ms.max_streak
ORDER BY sl.user_id;

-- Output:
-- user_id | longest_streak | start       | end
-- 1       | 7              | 2024-01-05  | 2024-01-11
-- 2       | 4              | 2024-01-01  | 2024-01-04
-- 3       | 1              | 2024-01-01  | 2024-01-01   (any of the isolated days)

-- ============================================
-- PART 4: FIND ALL GAPS (missed days)
-- ============================================

-- A gap exists when the difference between consecutive logins > 1 day:
WITH consecutive AS (
  SELECT
    user_id,
    login_date,
    LAG(login_date) OVER (PARTITION BY user_id ORDER BY login_date) AS prev_login,
    -- MySQL: DATEDIFF(login_date, LAG(login_date) OVER (...)) AS gap_days
    (login_date - LAG(login_date) OVER (PARTITION BY user_id ORDER BY login_date)) AS gap_days
    -- PgSQL: interval subtraction (result is integer for DATE type in PgSQL)
  FROM user_logins
)
SELECT
  user_id,
  prev_login AS last_login,
  login_date AS returned_on,
  gap_days - 1 AS days_missed  -- gap_days - 1 = actual days skipped
FROM consecutive
WHERE gap_days > 1
ORDER BY user_id, returned_on;

-- Output:
-- user_id | last_login  | returned_on | days_missed
-- 1       | 2024-01-03  | 2024-01-05  | 1    ← missed Jan 4
-- 3       | 2024-01-01  | 2024-01-03  | 1    ← missed Jan 2
-- 3       | 2024-01-03  | 2024-01-05  | 1    ← missed Jan 4
-- 3       | 2024-01-05  | 2024-01-07  | 1    ← missed Jan 6

-- MySQL version (DATEDIFF instead of interval subtraction):
WITH consecutive AS (
  SELECT
    user_id,
    login_date,
    LAG(login_date) OVER (PARTITION BY user_id ORDER BY login_date) AS prev_login,
    DATEDIFF(login_date, LAG(login_date) OVER (PARTITION BY user_id ORDER BY login_date)) AS gap_days
  FROM user_logins
)
SELECT user_id, prev_login, login_date AS returned_on, gap_days - 1 AS days_missed
FROM consecutive WHERE gap_days > 1;

-- ============================================
-- BONUS: USERS ACTIVE EVERY DAY IN A DATE RANGE
-- ============================================

-- Users who logged in every single day in January 2024:
SELECT user_id
FROM user_logins
WHERE login_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY user_id
HAVING COUNT(DISTINCT login_date) = 31;  -- 31 = days in January
-- Must have exactly 31 distinct login dates (one per day)

-- More flexible (use DATEDIFF to compute the range):
HAVING COUNT(DISTINCT login_date) = DATEDIFF('2024-01-31', '2024-01-01') + 1;
-- PgSQL: HAVING COUNT(DISTINCT login_date) = ('2024-01-31'::date - '2024-01-01'::date + 1)

-- ============================================
-- BONUS: RUNNING STREAK AS OF TODAY
-- ============================================

-- Current streak = days from today backward where there's no gap:
WITH recent AS (
  SELECT user_id, login_date,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date DESC) AS rn,
    -- Date should be today - (rn - 1) for a continuous streak:
    CURRENT_DATE - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date DESC) - 1) AS expected_date
  FROM user_logins
  WHERE login_date <= CURRENT_DATE
)
SELECT user_id, COUNT(*) AS current_streak
FROM recent
WHERE login_date = expected_date  -- only count rows in the unbroken streak from today
GROUP BY user_id
ORDER BY current_streak DESC;
-- Streak breaks as soon as login_date != expected_date (gap detected)
```

---

## 🔍 Why This Works (3 lines max)
The gap-and-island trick exploits the fact that consecutive calendar dates increase by exactly 1 per row. When you subtract an incrementing row number from consecutive dates, the result stays constant — the same constant = the same streak (island). The moment a gap appears, the date jumps by more than 1 while row_number jumps by exactly 1, so the constant changes and a new island begins.
हिंदी: Consecutive dates में date और row_number दोनों 1 से बढ़ते हैं → difference constant। Gap = date 2 बढ़ी, row_number 1 बढ़ा → constant change = new island।

---

## ⚡ Alternative Solution

```sql
-- Recursive CTE approach for streak (different perspective):
WITH RECURSIVE current_streak AS (
  -- Base: start with the most recent login per user
  SELECT user_id, login_date, 1 AS streak
  FROM user_logins ul1
  WHERE NOT EXISTS (
    SELECT 1 FROM user_logins ul2
    WHERE ul2.user_id = ul1.user_id AND ul2.login_date = ul1.login_date + INTERVAL '1 day'
  )  -- no login tomorrow = this is the start of the latest streak end

  UNION ALL

  SELECT ul.user_id, ul.login_date, cs.streak + 1
  FROM user_logins ul
  JOIN current_streak cs ON ul.user_id = cs.user_id
    AND ul.login_date = cs.login_date - INTERVAL '1 day'
)
SELECT user_id, MAX(streak) AS current_streak
FROM current_streak GROUP BY user_id;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Using UNION instead of UNION ALL in gap-island CTE
-- Some developers write UNION — UNION deduplicates, may remove valid rows

-- ❌ Wrong: Not partitioning by user_id in ROW_NUMBER
ROW_NUMBER() OVER (ORDER BY login_date)  -- ← global row number!
-- Row numbers run across ALL users together → trick doesn't work
-- ✅ Must partition:
ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date)

-- ❌ Wrong: Not accounting for same-day logins
-- If user logs in twice on same day, ROW_NUMBER treats them as 2 rows
-- date - rn won't be constant for same-day rows
-- ✅ Either: use DISTINCT on login_date (the PRIMARY KEY already prevents this in our setup)
-- OR: aggregate daily first: SELECT user_id, DATE(login_time) AS login_date FROM logins GROUP BY 1,2

-- ❌ Wrong: Comparing streak of 7 days with DATEDIFF of start and end
-- A streak from Jan 5 to Jan 11:
-- DATEDIFF('2024-01-11', '2024-01-05') = 6 (not 7!)
-- ✅ Count of rows in the streak = 7 (COUNT(*) = correct)
-- Days span = DATEDIFF + 1 if inclusive: Jan11 - Jan5 + 1 = 7
```

---

## 🎯 Interview Tip (1 line)
Say: "I use the gap-and-island trick: `date - ROW_NUMBER() OVER (PARTITION BY user ORDER BY date)` gives a constant value for each unbroken streak — GROUP BY that constant to find each island. For gaps, I use `LAG(login_date)` and filter where the difference > 1 day. This pattern comes up constantly in analytics: active day streaks, consecutive purchases, uninterrupted uptime windows."

---

## 🔗 Related Questions
→ Q067 (LEAD/LAG) | Q066 (ROW_NUMBER) | Q019 (recursive CTE) | Q075 (top N per group)
