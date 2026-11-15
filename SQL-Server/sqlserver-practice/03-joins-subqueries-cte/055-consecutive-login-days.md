---

# Q055. Consecutive Login Days
# Category: Joins, Subqueries & CTEs
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (DATEADD/DATEDIFF are T-SQL; MySQL uses DATE_SUB/DATEDIFF, PostgreSQL uses date - integer)

---

## ❓ Question
`Logins(UserId, LoginDate)` may contain several logins on one day. For every user, list each streak of consecutive days (start, end, length) and then return each user's longest streak. Optionally: users with a streak of at least 3 days.

---

## 💡 Quick Concept (2 lines only)
This is gaps-and-islands on dates: de-duplicate days, number them per user with ROW_NUMBER, and subtract that number (in days) from the date. Days in one streak give the SAME anchor date, so group by it.
हिंदी: Gaps-and-islands का date version। हर user के distinct दिन गिनो, date में से row number (दिन) घटाओ — एक streak में anchor date same रहेगी।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Logins (
  UserId    INT  NOT NULL,
  LoginDate DATE NOT NULL
);

INSERT INTO Logins (UserId, LoginDate) VALUES
  (1, '2024-05-01'), (1, '2024-05-02'), (1, '2024-05-03'),
  (1, '2024-05-05'), (1, '2024-05-06'), (1, '2024-05-06'),   -- two logins on 6-May
  (2, '2024-05-01'), (2, '2024-05-03'), (2, '2024-05-04');

-- ============================================
-- ALL STREAKS PER USER
-- ============================================
WITH Days AS (
  SELECT DISTINCT UserId, LoginDate FROM Logins          -- 1 row per user per day
),
Numbered AS (
  SELECT UserId, LoginDate,
         DATEADD(DAY, -ROW_NUMBER() OVER (PARTITION BY UserId ORDER BY LoginDate), LoginDate) AS Anchor
  FROM Days
)
SELECT UserId,
       MIN(LoginDate) AS StreakStart,
       MAX(LoginDate) AS StreakEnd,
       COUNT(*)       AS Days
FROM Numbered
GROUP BY UserId, Anchor
ORDER BY UserId, StreakStart;

-- EXPECTED OUTPUT (derived on SQLite using date(LoginDate, '-N day') in place of DATEADD):
-- UserId | StreakStart | StreakEnd  | Days
-- 1      | 2024-05-01  | 2024-05-03 | 3
-- 1      | 2024-05-05  | 2024-05-06 | 2
-- 2      | 2024-05-01  | 2024-05-01 | 1
-- 2      | 2024-05-03  | 2024-05-04 | 2

-- ============================================
-- LONGEST STREAK PER USER
-- ============================================
WITH Days AS (
  SELECT DISTINCT UserId, LoginDate FROM Logins
),
Numbered AS (
  SELECT UserId, LoginDate,
         DATEADD(DAY, -ROW_NUMBER() OVER (PARTITION BY UserId ORDER BY LoginDate), LoginDate) AS Anchor
  FROM Days
),
Streaks AS (
  SELECT UserId, Anchor, COUNT(*) AS Days
  FROM Numbered
  GROUP BY UserId, Anchor
)
SELECT UserId, MAX(Days) AS LongestStreak
FROM Streaks
GROUP BY UserId
ORDER BY UserId;

-- EXPECTED OUTPUT (derived on SQLite):
-- UserId | LongestStreak
-- 1      | 3
-- 2      | 2

-- Users with a streak of at least 3 days: add  HAVING COUNT(*) >= 3  to the first query
-- (only user 1 qualifies on this data). Not executed on SQL Server; DATEADD semantics per Microsoft docs.
```

---

## 🔍 Why This Works (3 lines max)
After de-duplicating, each user's distinct dates are numbered 1, 2, 3...; consecutive calendar days move forward by 1 day exactly like the row number, so `date - rn days` stays constant for the whole streak and changes after a missed day. Grouping by (UserId, Anchor) therefore yields one row per streak. DISTINCT matters: two logins on one day would otherwise break the arithmetic.
हिंदी: Distinct दिनों को 1,2,3 गिनो; लगातार दिन भी हर बार +1 बढ़ते हैं, इसलिए `date - rn` constant रहता है। दिन छूटते ही बदल जाता है। पहले DISTINCT ज़रूरी है।

---

## ⚡ Alternative Solution

```sql
-- LAG version: flag a new streak whenever the gap to the previous login day is not 1, then running-sum the flags.
WITH Days AS (SELECT DISTINCT UserId, LoginDate FROM Logins),
Flagged AS (
  SELECT UserId, LoginDate,
         CASE WHEN DATEDIFF(DAY, LAG(LoginDate) OVER (PARTITION BY UserId ORDER BY LoginDate), LoginDate) = 1
              THEN 0 ELSE 1 END AS IsNewStreak          -- first row: LAG is NULL -> DATEDIFF NULL -> ELSE 1
  FROM Days
),
Grouped AS (
  SELECT *, SUM(IsNewStreak) OVER (PARTITION BY UserId ORDER BY LoginDate
                                   ROWS UNBOUNDED PRECEDING) AS StreakNo
  FROM Flagged
)
SELECT UserId, MIN(LoginDate) AS StreakStart, MAX(LoginDate) AS StreakEnd, COUNT(*) AS Days
FROM Grouped
GROUP BY UserId, StreakNo;
-- More readable for people new to the anchor-date trick, same result.

-- Index: CREATE INDEX IX_Logins_User_Date ON Logins (UserId, LoginDate);  -- avoids a sort
-- "Streak ending today" needs one more filter: StreakEnd = CAST(GETDATE() AS DATE).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: no DISTINCT / using ROW_NUMBER directly on raw logins
-- The duplicate 6-May login makes the row number advance twice for one day and splits the streak.

-- ❌ Wrong: no PARTITION BY UserId
-- All users share one numbering and the streaks mix across users.

-- ❌ Wrong: comparing datetime values
-- If LoginDate is a DATETIME, convert with CAST(x AS DATE) first; times of day break "+1 day" arithmetic.

-- ❌ Wrong: counting rows instead of distinct days -> inflated streak lengths.
-- ❌ Wrong: ignoring time zones: a login at 23:30 UTC may be "tomorrow" for the user. Decide the business day definition.
```

---

## 🎯 Interview Tip (1 line)
Say: "DISTINCT days, ROW_NUMBER per user, subtract it as days from the date and group by the anchor — one scan, no self-joins. I mention the LAG + running-sum variant as the more readable one, an index on (UserId, LoginDate), and that I would settle time-zone and datetime-to-date rules with the product owner first."

---

## 🔗 Related Questions
→ Q049 (gaps and islands) | Q057 (LAG and LEAD) | Q007 (date functions) | Q056 (ROW_NUMBER, RANK, DENSE_RANK)
