---

# Q057. Find Duplicate Rows
# Category: Joins
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Find duplicate emails in a users table, list the full duplicated rows, and find rows that are duplicates on several columns. Show GROUP BY/HAVING, self join and window-function approaches.

---

## 💡 Quick Concept (2 lines only)
Duplicates = same business key appearing more than once: `GROUP BY key HAVING COUNT(*) > 1` finds the keys; join back (or use `COUNT(*) OVER (PARTITION BY key)`) to see every row. Compare keys case-insensitively and trimmed if the data is messy.
हिंदी: Duplicate = same key एक से ज़्यादा बार। GROUP BY + HAVING COUNT > 1 से keys, फिर JOIN/window से पूरी rows।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE users (
  user_id    INT PRIMARY KEY,
  name       VARCHAR(100),
  email      VARCHAR(255),
  phone      VARCHAR(20),
  created_at DATE
);

INSERT INTO users VALUES
  (1, 'Asha',   'asha@example.com',  '9000000001', '2024-01-01'),
  (2, 'Asha K', 'asha@example.com',  '9000000001', '2024-01-05'),   -- same email + phone
  (3, 'Rohan',  'rohan@example.com', '9000000002', '2024-01-07'),
  (4, 'Meera',  'meera@example.com', '9000000003', '2024-01-09'),
  (5, 'Meera2', 'meera@example.com', '9000000099', '2024-01-12'),   -- same email, other phone
  (6, 'Asha 3', 'asha@example.com',  '9000000005', '2024-01-15');   -- third asha

-- ============================================
-- STEP 1: which emails are duplicated, and how many times
-- ============================================

SELECT email, COUNT(*) AS occurrences
FROM users
GROUP BY email
HAVING COUNT(*) > 1                    -- HAVING filters groups; WHERE cannot
ORDER BY occurrences DESC, email;
-- Output:
-- email             | occurrences
-- asha@example.com  | 3
-- meera@example.com | 2

-- ============================================
-- STEP 2: the full rows behind those emails (join back)
-- ============================================

SELECT u.*
FROM users u
JOIN (
  SELECT email FROM users GROUP BY email HAVING COUNT(*) > 1
) d ON d.email = u.email
ORDER BY u.email, u.user_id;
-- Output:
-- user_id | name   | email             | phone      | created_at
-- 1       | Asha   | asha@example.com  | 9000000001 | 2024-01-01
-- 2       | Asha K | asha@example.com  | 9000000001 | 2024-01-05
-- 6       | Asha 3 | asha@example.com  | 9000000005 | 2024-01-15
-- 4       | Meera  | meera@example.com | 9000000003 | 2024-01-09
-- 5       | Meera2 | meera@example.com | 9000000099 | 2024-01-12

-- ============================================
-- STEP 3: duplicates on a combination of columns (email AND phone)
-- ============================================

SELECT email, phone, COUNT(*) AS occurrences, MIN(user_id) AS first_id
FROM users
GROUP BY email, phone
HAVING COUNT(*) > 1;
-- Output:
-- email            | phone      | occurrences | first_id
-- asha@example.com | 9000000001 | 2           | 1

-- ============================================
-- SELF JOIN: pairs of duplicate rows (a.user_id < b.user_id avoids mirrored pairs)
-- ============================================

SELECT a.user_id AS id_1, b.user_id AS id_2, a.email
FROM users a
JOIN users b
  ON a.email = b.email
 AND a.user_id < b.user_id
ORDER BY a.email, id_1, id_2;
-- Output:
-- id_1 | id_2 | email
-- 1    | 2    | asha@example.com
-- 1    | 6    | asha@example.com
-- 2    | 6    | asha@example.com
-- 4    | 5    | meera@example.com

-- ============================================
-- WINDOW FUNCTION: flag every row that is NOT the first occurrence
-- ============================================

SELECT user_id, email,
       ROW_NUMBER() OVER (PARTITION BY email ORDER BY user_id) AS occurrence_no
FROM users
ORDER BY email, user_id;
-- Output:
-- user_id | email             | occurrence_no
-- 1       | asha@example.com  | 1
-- 2       | asha@example.com  | 2
-- 6       | asha@example.com  | 3
-- 4       | meera@example.com | 1
-- 5       | meera@example.com | 2
-- 3       | rohan@example.com | 1
-- occurrence_no > 1 marks the extra copies (these are the delete candidates in Q058)
```

---

## 🔍 Why This Works (3 lines max)
GROUP BY collapses rows with the same key and COUNT(*) measures the group size, so HAVING COUNT(*) > 1 isolates repeated keys. The self join with `a.user_id < b.user_id` pairs each duplicate once; ROW_NUMBER numbers copies inside each key so you can keep number 1 and treat the rest as extras.
हिंदी: GROUP BY + HAVING COUNT(*) > 1 = repeated keys। Self join में a.id < b.id से हर pair एक ही बार। ROW_NUMBER > 1 = extra copies।

---

## ⚡ Alternative Solution

```sql
-- Case/whitespace-insensitive duplicates (real-world dirty data)
INSERT INTO users VALUES (7, 'Rohan R', ' ROHAN@example.com ', '9000000002', '2024-02-01');

SELECT LOWER(TRIM(email)) AS clean_email, COUNT(*) AS occurrences
FROM users
GROUP BY LOWER(TRIM(email))
HAVING COUNT(*) > 1
ORDER BY clean_email;
-- Output:
-- clean_email       | occurrences
-- asha@example.com  | 3
-- meera@example.com | 2
-- rohan@example.com | 2

-- Collation note: MySQL's default collations (utf8mb4_0900_ai_ci) compare case-insensitively already,
-- so GROUP BY email groups 'A@x.com' and 'a@x.com'; PostgreSQL's default text comparison is case-SENSITIVE,
-- so the LOWER() above is mandatory there (or use the citext extension).

-- Window variant: show the count next to each row
SELECT *
FROM (
  SELECT u.*, COUNT(*) OVER (PARTITION BY email) AS copies
  FROM users u
) t
WHERE copies > 1
ORDER BY email, user_id;
-- Output:
-- user_id | name   | email             | phone      | created_at | copies
-- 1       | Asha   | asha@example.com  | 9000000001 | 2024-01-01 | 3
-- 2       | Asha K | asha@example.com  | 9000000001 | 2024-01-05 | 3
-- 6       | Asha 3 | asha@example.com  | 9000000005 | 2024-01-15 | 3
-- 4       | Meera  | meera@example.com | 9000000003 | 2024-01-09 | 2
-- 5       | Meera2 | meera@example.com | 9000000099 | 2024-01-12 | 2
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: SELECT DISTINCT to "find" duplicates (it hides them, it does not report them)
-- ❌ Wrong: WHERE COUNT(*) > 1                    -- aggregate not allowed in WHERE -> use HAVING
-- ❌ Wrong: GROUP BY name, email, user_id          -- user_id is unique, so every group has 1 row and nothing is found
-- ❌ Wrong: self join with a.user_id <> b.user_id  -- returns every pair twice (A,B) and (B,A)
-- ❌ Wrong: ignoring NULLs - GROUP BY puts all NULL emails in one group, but NULL = NULL is never true in a join
-- ✅ Decide what "duplicate" means (which columns, case, NULL handling) BEFORE writing the query
```

---

## 🎯 Interview Tip (1 line)
Say: "I define the business key first, find keys with GROUP BY/HAVING, then join back or use ROW_NUMBER to inspect the rows; I normalise case and whitespace, remember PostgreSQL is case-sensitive while MySQL's default collation is not, and prevent recurrence with a UNIQUE constraint."

---

## 🔗 Related Questions
→ Q058 (Delete duplicates keeping one) | Q239 (Find duplicates - interview classic) | Q066 (ROW_NUMBER) | Q060 (Common rows)
