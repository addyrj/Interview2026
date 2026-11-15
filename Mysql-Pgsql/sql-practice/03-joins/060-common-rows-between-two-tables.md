---

# Q060. Common Rows Between Two Tables
# Category: Joins
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Find rows that exist in both tables: customers who appear in both the newsletter_subscribers and app_users tables. Show INNER JOIN, INTERSECT, IN/EXISTS, and what happens with duplicates and NULLs.

---

## 💡 Quick Concept (2 lines only)
Common rows = intersection. INNER JOIN on the matching key (may multiply rows), `INTERSECT` (distinct set semantics, treats NULL = NULL), or `EXISTS` (each left row once). Pick based on duplicates and NULL behaviour.
हिंदी: Common rows = intersection। INNER JOIN duplicates दे सकता है, INTERSECT distinct देता है और NULL को बराबर मानता है, EXISTS हर row एक बार।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE newsletter_subscribers (
  subscriber_id INT PRIMARY KEY,
  email         VARCHAR(255),
  subscribed_on DATE
);

CREATE TABLE app_users (
  user_id    INT PRIMARY KEY,
  email      VARCHAR(255),
  signup_on  DATE
);

INSERT INTO newsletter_subscribers VALUES
  (1, 'asha@example.com',  '2024-01-01'),
  (2, 'rohan@example.com', '2024-01-02'),
  (3, 'meera@example.com', '2024-01-03'),
  (4, 'meera@example.com', '2024-02-03'),    -- subscribed twice
  (5, NULL,                '2024-02-10');    -- missing email

INSERT INTO app_users VALUES
  (10, 'asha@example.com',  '2024-03-01'),
  (11, 'meera@example.com', '2024-03-02'),
  (12, 'vikram@example.com','2024-03-03'),
  (13, NULL,                '2024-03-04');   -- missing email

-- ============================================
-- WAY 1: INNER JOIN (returns one row per matching PAIR)
-- ============================================

SELECT s.email, s.subscriber_id, u.user_id
FROM newsletter_subscribers s
JOIN app_users u ON u.email = s.email         -- NULL = NULL is not true, so NULL emails never match
ORDER BY s.email, s.subscriber_id;
-- Output:
-- email             | subscriber_id | user_id
-- asha@example.com  | 1             | 10
-- meera@example.com | 3             | 11
-- meera@example.com | 4             | 11
-- ^ meera appears twice (two subscriber rows x one user row)

-- ============================================
-- WAY 2: INTERSECT (distinct values; NULLs compare as equal)
-- ============================================

SELECT email FROM (
  SELECT email FROM newsletter_subscribers
  INTERSECT
  SELECT email FROM app_users
) common
ORDER BY email IS NULL, email;    -- portable NULLs-last (MySQL sorts NULL first, PostgreSQL last)
-- (PostgreSQL cannot ORDER BY an expression directly on a set operation, hence the wrapper)
-- Output:
-- email
-- asha@example.com
-- meera@example.com
-- NULL
-- ^ NULL is returned too: set operators treat NULLs as "not distinct"

-- ============================================
-- WAY 3: EXISTS (one row per LEFT row, no multiplication from the right side)
-- ============================================

SELECT s.subscriber_id, s.email
FROM newsletter_subscribers s
WHERE EXISTS (SELECT 1 FROM app_users u WHERE u.email = s.email)
ORDER BY s.subscriber_id;
-- Output:
-- subscriber_id | email
-- 1             | asha@example.com
-- 3             | meera@example.com
-- 4             | meera@example.com

-- ============================================
-- WAY 4: INNER JOIN + DISTINCT on the key
-- ============================================

SELECT DISTINCT s.email
FROM newsletter_subscribers s
JOIN app_users u ON u.email = s.email
ORDER BY s.email;
-- Output:
-- email
-- asha@example.com
-- meera@example.com
```

---

## 🔍 Why This Works (3 lines max)
JOIN pairs matching rows, so duplicates on either side multiply the result; INTERSECT works on whole-row sets, removing duplicates and treating two NULLs as the same value, while the join and EXISTS predicates use `=`, which is never true for NULL. EXISTS keeps one output row per left row.
हिंदी: JOIN pairs बनाता है (duplicates multiply)। INTERSECT distinct देता है और NULL को बराबर मानता है; `=` वाले join/EXISTS में NULL match नहीं होता।

---

## ⚡ Alternative Solution

```sql
-- NULL-safe equality in a JOIN, if you WANT NULL emails to match:
-- MySQL:       ON u.email <=> s.email
-- PostgreSQL:  ON u.email IS NOT DISTINCT FROM s.email     (MySQL 8 does not support this form)
```

```sql
SELECT s.subscriber_id, u.user_id
FROM newsletter_subscribers s
JOIN app_users u ON u.email <=> s.email       -- MySQL null-safe equals
ORDER BY s.subscriber_id;
-- Output:
-- subscriber_id | user_id
-- 1             | 10
-- 3             | 11
-- 4             | 11
-- 5             | 13
```

```sql
SELECT s.subscriber_id, u.user_id
FROM newsletter_subscribers s
JOIN app_users u ON u.email IS NOT DISTINCT FROM s.email     -- standard SQL null-safe equals
ORDER BY s.subscriber_id;
-- Output:
-- subscriber_id | user_id
-- 1             | 10
-- 3             | 11
-- 4             | 11
-- 5             | 13
```

```sql
-- Compare on more than one column: matching entire rows (all columns equal), as set intersection
SELECT email, signup_on FROM app_users
INTERSECT
SELECT email, subscribed_on FROM newsletter_subscribers
ORDER BY email;
-- Output:
-- (0 rows)
-- (no common (email, date) pairs: dates differ) - INTERSECT needs every selected column to match.

-- INTERSECT ALL (keeps duplicates, min count) exists in PostgreSQL; MySQL 8.0.31+ supports INTERSECT [ALL] too.
-- Before MySQL 8.0.31 there is no INTERSECT: use the INNER JOIN / EXISTS forms above.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: INNER JOIN, then COUNT(*) to count "common customers" -> inflated by duplicates (meera counted twice)
-- ✅ COUNT(DISTINCT s.email) or use INTERSECT / EXISTS

-- ❌ Wrong: expecting INNER JOIN to return NULL-email rows - NULL never equals NULL
-- ❌ Wrong: INTERSECT with different column counts or incompatible types -> error
-- ❌ Wrong: comparing emails with different case/whitespace in PostgreSQL (case-sensitive) - normalise with LOWER(TRIM())
-- ❌ Wrong: using IN (SELECT email ...) when the subquery can contain NULL for NOT IN logic - fine for IN, deadly for NOT IN
```

---

## 🎯 Interview Tip (1 line)
Say: "For common keys I choose by semantics: INTERSECT for distinct set logic (and NULLs equal), EXISTS to keep one row per left row, JOIN when I need columns from both sides - and I always state how duplicates and NULLs behave, since that's what usually trips people up."

---

## 🔗 Related Questions
→ Q052 (A not in B, 3 ways) | Q059 (Jan but not Feb) | Q057 (Find duplicate rows) | Q044 (FULL OUTER JOIN)
