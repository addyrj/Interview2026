---

# Q078. Cumulative Distinct Count (Running Unique Users)
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
From a `user_logins` table, report for each login date the **cumulative number of distinct users** seen so far (e.g. "total unique users up to and including this day"). Note: `COUNT(DISTINCT user_id) OVER (ORDER BY ...)` is NOT allowed in either database.

---

## 💡 Quick Concept (2 lines only)
Window functions cannot take DISTINCT, so first reduce to each user's FIRST appearance (`MIN(date) GROUP BY user`), count new users per day, then run a plain `SUM() OVER (ORDER BY date)`. Each user is counted exactly once, on the day they first appear.
हिंदी: Window में DISTINCT नहीं चलता, इसलिए हर user की पहली date निकालो, daily new users गिनो, फिर running SUM लगाओ।

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
  (1,  101, '2024-03-01'), (2,  102, '2024-03-01'), (3, 101, '2024-03-01'),  -- 101 logs in twice same day
  (4,  101, '2024-03-02'), (5,  103, '2024-03-02'), (6, 102, '2024-03-02'),
  (7,  104, '2024-03-03'), (8,  101, '2024-03-03'),
  (9,  105, '2024-03-05'), (10, 103, '2024-03-05');                          -- note: no logins on 03-04

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: first_seen = first login date per user (each user appears once)
-- Step 2: daily_new  = how many users appeared for the FIRST time on each date
-- Step 3: running SUM of daily_new = cumulative distinct users

WITH first_seen AS (
  SELECT user_id, MIN(login_date) AS first_date
  FROM user_logins
  GROUP BY user_id
),
daily_new AS (
  SELECT first_date AS login_date, COUNT(*) AS new_users
  FROM first_seen
  GROUP BY first_date
)
SELECT login_date,
       new_users,
       SUM(new_users) OVER (ORDER BY login_date) AS cumulative_distinct_users
FROM daily_new
ORDER BY login_date;

-- ============================================
-- EXPECTED OUTPUT (verified on MySQL 9.1 and PostgreSQL via PGlite)
-- ============================================

-- login_date | new_users | cumulative_distinct_users
-- -----------+-----------+--------------------------
-- 2024-03-01 | 2         | 2
-- 2024-03-02 | 1         | 3
-- 2024-03-03 | 1         | 4
-- 2024-03-05 | 1         | 5
--
-- Dates with zero new users (03-04) are absent. To list every calendar day, join to a calendar table / generate_series (see Q079).
```

---

## 🔍 Why This Works (3 lines max)
Collapsing to first appearance guarantees each user contributes `1` once, so a plain running SUM equals the running distinct count. Duplicate logins (user 101 on 03-01) and returning users (101, 102, 103 later) never add again.
हिंदी: हर user सिर्फ अपनी पहली date पर count होता है, इसलिए running SUM = running distinct count।

---

## ⚡ Alternative Solution

```sql
-- Alt 1: Daily active users + cumulative unique side by side (both DBs)
WITH first_seen AS (
  SELECT user_id, MIN(login_date) AS first_date FROM user_logins GROUP BY user_id
)
SELECT d.login_date,
       d.dau,                                                     -- distinct users THAT day
       SUM(COALESCE(n.new_users, 0)) OVER (ORDER BY d.login_date) AS cumulative_distinct_users
FROM (SELECT login_date, COUNT(DISTINCT user_id) AS dau
      FROM user_logins GROUP BY login_date) d
LEFT JOIN (SELECT first_date, COUNT(*) AS new_users
           FROM first_seen GROUP BY first_date) n
       ON n.first_date = d.login_date
ORDER BY d.login_date;
-- Result (same cumulative column): dau = 2, 3, 2, 2 ; cumulative = 2, 3, 4, 5

-- Alt 2: Self-join (simple, O(days x rows) - fine only for small data)
SELECT d.login_date, COUNT(DISTINCT l.user_id) AS cumulative_distinct_users
FROM (SELECT DISTINCT login_date FROM user_logins) d
JOIN user_logins l ON l.login_date <= d.login_date
GROUP BY d.login_date
ORDER BY d.login_date;

-- MySQL vs PgSQL: identical SQL works in both (MySQL needs 8.0+ for CTE/window).
-- PgSQL-only trick: SELECT DISTINCT ON (user_id) user_id, login_date ... ORDER BY user_id, login_date
-- gives the first-seen row per user without GROUP BY.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: DISTINCT inside a window function
SELECT login_date, COUNT(DISTINCT user_id) OVER (ORDER BY login_date) FROM user_logins;
-- MySQL 9.1: ERROR 1235: This version of MySQL doesn't yet support '<window function>(DISTINCT ..)'
-- PostgreSQL: ERROR: DISTINCT is not implemented for window functions

-- ❌ Wrong: cumulative SUM of daily distinct counts
-- SUM(dau) OVER (...) = 2, 5, 7, 9  -> counts returning users again (101 counted 3 times)

-- ✅ Correct: cumulative SUM of NEW users (first appearance only), as in the solution.
```

---

## 🎯 Interview Tip (1 line)
Say: "DISTINCT isn't supported in window functions, so I dedupe first by taking each user's MIN(date), count new users per day and then use a running SUM; for huge tables I'd precompute first_seen in a summary table instead of rescanning the events."

---

## 🔗 Related Questions
→ Q066 (ROW_NUMBER vs RANK vs DENSE_RANK) | Q079 (Gap and island) | Q080 (Consecutive login streak) | Q239 (Find duplicates)
