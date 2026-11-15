---

# Q010. Date/Time Functions - NOW(), DATEDIFF, DATE_ADD
# Category: Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
On a `subscriptions` table, compute days since start, add one month, subtract 7 days, hours until expiry, format a year-month label and find the month end. Show the MySQL and PostgreSQL versions, because `DATEDIFF`, `DATE_ADD` and `DATE_FORMAT` do not exist in PostgreSQL.

---

## 💡 Quick Concept (2 lines only)
MySQL uses functions (`DATEDIFF`, `DATE_ADD`, `TIMESTAMPDIFF`, `DATE_FORMAT`, `LAST_DAY`); PostgreSQL uses operators and `INTERVAL` arithmetic (`date - date`, `date + INTERVAL '1 month'`), plus `EXTRACT`, `TO_CHAR`, `DATE_TRUNC`. `EXTRACT(YEAR FROM x)` and `CURRENT_DATE` work in both.
हिंदी: MySQL में date के functions हैं (DATEDIFF, DATE_ADD), PostgreSQL में operators और INTERVAL (`date - date`, `+ INTERVAL '1 month'`)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE subscriptions (
  id         INT PRIMARY KEY,
  user_name  VARCHAR(30),
  started_on DATE,
  ends_at    TIMESTAMP
);

INSERT INTO subscriptions VALUES
  (1, 'Asha',   '2024-01-31', '2024-02-29 18:00:00'),   -- month-end start
  (2, 'Ben',    '2024-03-15', '2024-03-20 09:30:00'),
  (3, 'Chitra', '2023-12-25', '2024-01-05 00:00:00');

-- ============================================
-- SOLUTION: MySQL
-- ============================================
SELECT id,
  DATEDIFF('2024-03-01', started_on)             AS days_since,   -- (later - earlier) in days
  DATE_ADD(started_on, INTERVAL 1 MONTH)         AS plus_month,
  DATE_SUB(started_on, INTERVAL 7 DAY)           AS minus7,
  TIMESTAMPDIFF(HOUR, started_on, ends_at)       AS hrs_to_end,   -- whole hours, truncated
  DATE_FORMAT(started_on, '%Y-%m')               AS ym,
  LAST_DAY(started_on)                           AS month_end
FROM subscriptions ORDER BY id;

-- ============================================
-- SOLUTION: PostgreSQL
-- ============================================
SELECT id,
  DATE '2024-03-01' - started_on                         AS days_since,   -- date - date = integer days
  started_on + INTERVAL '1 month'                        AS plus_month,   -- returns TIMESTAMP
  started_on - INTERVAL '7 days'                         AS minus7,
  EXTRACT(EPOCH FROM (ends_at - started_on)) / 3600      AS hrs_to_end,   -- fractional hours
  TO_CHAR(started_on, 'YYYY-MM')                         AS ym,
  (DATE_TRUNC('month', started_on) + INTERVAL '1 month - 1 day')::DATE AS month_end
FROM subscriptions ORDER BY id;
-- (PostgreSQL has no LAST_DAY; the DATE_TRUNC trick above was run and gives the month end)

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- id | days_since | plus_month | minus7     | hrs_to_end | ym      | month_end
--  1 |         30 | 2024-02-29 | 2024-01-24 | 714        | 2024-01 | 2024-01-31   <- Jan 31 + 1 month = Feb 29 (clamped)
--  2 |        -14 | 2024-04-15 | 2024-03-08 | 129 (MySQL) / 129.5 (PG) | 2024-03 | 2024-03-31
--  3 |         67 | 2024-01-25 | 2023-12-18 | 264        | 2023-12 | 2023-12-31
-- (days_since is negative for id 2: it starts AFTER 2024-03-01)
-- (PG plus_month/minus7 print as timestamps, e.g. 2024-02-29 00:00:00; MySQL prints a DATE)
-- (PG's hrs_to_end prints as 714.0000000000000000 - numeric)
```

---

## 🔍 Why This Works (3 lines max)
Interval arithmetic respects calendar rules: adding one month to Jan 31 clamps to Feb 29, it does not overflow to March. MySQL's DATEDIFF ignores the time part and returns whole days; PostgreSQL's `date - date` is an integer day count, while `timestamp - timestamp` returns an INTERVAL. Use EXTRACT(EPOCH ...) to turn an interval into seconds.
हिंदी: Interval जोड़ने पर calendar के नियम लगते हैं (31 जनवरी + 1 महीना = 29 फरवरी); MySQL DATEDIFF पूरे दिन देता है, PostgreSQL में `date - date` integer दिन।

---

## ⚡ Alternative Solution

```sql
-- Cross-engine usage checks (all verified):
-- PostgreSQL: DATEDIFF(...)  -> ERROR: function datediff(date, date) does not exist
-- PostgreSQL: DATE_FORMAT / LAST_DAY -> ERROR function does not exist
-- MySQL:      TO_CHAR / DATE_TRUNC   -> ERROR 1305 FUNCTION does not exist
-- MySQL:      started_on + INTERVAL '1 month' -> ERROR 1064 (MySQL wants INTERVAL 1 MONTH, no quotes)
-- MySQL:      EXTRACT(EPOCH FROM ...) -> ERROR 1064 (use UNIX_TIMESTAMP(a) - UNIX_TIMESTAMP(b))

-- Portable bits that worked in both:
SELECT EXTRACT(YEAR FROM started_on) AS y, EXTRACT(MONTH FROM started_on) AS m FROM subscriptions;
SELECT CURRENT_DATE;      -- both; also CURRENT_TIMESTAMP

-- "Expired in the last 24 hours" (NOW() is time-dependent, so I did not capture output):
-- MySQL:      WHERE ends_at < NOW() AND ends_at > NOW() - INTERVAL 1 DAY
-- PostgreSQL: WHERE ends_at < NOW() AND ends_at > NOW() - INTERVAL '1 day'
-- NOW() = transaction start time in PostgreSQL (constant inside one transaction); use clock_timestamp()
-- for wall-clock time. In MySQL NOW() is the statement start time; SYSDATE() is wall-clock.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: PostgreSQL-style subtraction in MySQL
SELECT DATE '2024-03-01' - started_on FROM subscriptions;
-- MySQL 9.1.0 returned 170, -14, 9076 : it subtracted the numbers 20240301 - 20240131 !
-- PostgreSQL returned 30, -14, 67 (correct days).
-- ✅ MySQL: DATEDIFF(later, earlier)   ✅ PostgreSQL: later - earlier

-- ❌ Wrong: DATEDIFF argument order - it is (end, start); swapping gives a negative number
-- ❌ Wrong: ignoring time zones - TIMESTAMP in MySQL is stored as UTC and converted using the session
--           time_zone; PostgreSQL's TIMESTAMPTZ is the one to use for real instants.
-- ❌ Wrong: WHERE DATE(created_at) = '2024-03-15'  (function on column, index unusable)
-- ✅ WHERE created_at >= '2024-03-15' AND created_at < '2024-03-16'
```

---

## 🎯 Interview Tip (1 line)
Say: "I keep timestamps in UTC (TIMESTAMPTZ in PostgreSQL), filter with half-open ranges instead of wrapping the column in DATE(), and I know the dialect differences - DATEDIFF/DATE_ADD in MySQL versus date arithmetic and INTERVAL in PostgreSQL."

---

## 🔗 Related Questions
→ Q006 (BETWEEN edge cases) | Q008 (Type casting) | Q009 (String functions) | Q240 (Consecutive date ranges)
