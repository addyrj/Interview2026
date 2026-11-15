---

# Q058. Delete Duplicate Rows Keeping One
# Category: Joins
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Delete duplicate emails from a users table, keeping only the row with the lowest user_id per email. Show the portable subquery version, the MySQL DELETE ... JOIN, the PostgreSQL DELETE ... USING, and a ROW_NUMBER version.

---

## 💡 Quick Concept (2 lines only)
Decide the survivor (MIN(user_id) per email), then delete everything else. MySQL refuses to delete from a table it also selects from in a plain subquery, so wrap the subquery as a derived table; PostgreSQL has no such restriction.
हिंदी: पहले survivor तय करो (हर email का MIN id), बाकी delete। MySQL में subquery को derived table में wrap करना पड़ता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE users (
  user_id INT PRIMARY KEY,
  name    VARCHAR(100),
  email   VARCHAR(255)
);

INSERT INTO users VALUES
  (1, 'Asha',   'asha@example.com'),
  (2, 'Asha K', 'asha@example.com'),    -- duplicate
  (3, 'Rohan',  'rohan@example.com'),
  (4, 'Meera',  'meera@example.com'),
  (5, 'Meera2', 'meera@example.com'),   -- duplicate
  (6, 'Asha 3', 'asha@example.com');    -- duplicate

-- ============================================
-- ALWAYS PREVIEW FIRST: what WOULD be deleted?
-- ============================================

SELECT user_id, email
FROM users
WHERE user_id NOT IN (
  SELECT keep_id FROM (SELECT MIN(user_id) AS keep_id FROM users GROUP BY email) k
)
ORDER BY user_id;
-- Output:
-- user_id | email
-- 2       | asha@example.com
-- 5       | meera@example.com
-- 6       | asha@example.com

-- ============================================
-- SOLUTION (portable: MySQL + PostgreSQL)
-- ============================================

-- Step 1: inner query = one survivor id per email
-- Step 2: derived-table wrapper `k` satisfies MySQL's "can't specify target table" rule
-- Step 3: delete every id that is not a survivor
DELETE FROM users
WHERE user_id NOT IN (
  SELECT keep_id FROM (
    SELECT MIN(user_id) AS keep_id
    FROM users
    GROUP BY email
  ) k
);

SELECT user_id, name, email FROM users ORDER BY user_id;
-- Output:
-- user_id | name  | email
-- 1       | Asha  | asha@example.com
-- 3       | Rohan | rohan@example.com
-- 4       | Meera | meera@example.com
-- ^ survivors: 1, 3, 4

-- Lock it in so duplicates cannot come back:
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
```

---

## 🔍 Why This Works (3 lines max)
`MIN(user_id) GROUP BY email` yields exactly one id to keep per email, so `NOT IN` that set targets only the extra copies. MIN is never NULL here (primary key), so NOT IN is safe; the derived table forces MySQL to materialise the keep-list before the delete starts.
हिंदी: हर email का MIN(user_id) = survivor, बाकी NOT IN से delete। MIN कभी NULL नहीं, इसलिए NOT IN safe। MySQL में derived table ज़रूरी।

---

## ⚡ Alternative Solution

```sql
-- Re-create test data (the main example already deleted the duplicates)
CREATE TABLE users_mysql  (user_id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(255));
CREATE TABLE users_pg     (user_id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(255));
CREATE TABLE users_window (user_id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(255));
INSERT INTO users_mysql  VALUES (1,'Asha','a@x.com'),(2,'Asha K','a@x.com'),(3,'Rohan','r@x.com'),(4,'Meera','m@x.com'),(5,'Meera2','m@x.com'),(6,'Asha 3','a@x.com');
INSERT INTO users_pg     SELECT * FROM users_mysql;
INSERT INTO users_window SELECT * FROM users_mysql;
```

```sql
-- MySQL: DELETE ... JOIN (delete the alias that has a lower-id twin)
DELETE u1
FROM users_mysql u1
JOIN users_mysql u2
  ON u1.email = u2.email
 AND u1.user_id > u2.user_id;     -- u1 is the later copy
SELECT user_id FROM users_mysql ORDER BY user_id;
-- Output:
-- user_id
-- 1
-- 3
-- 4
```

```sql
-- PostgreSQL: DELETE ... USING (join syntax for deletes)
DELETE FROM users_pg u1
USING users_pg u2
WHERE u1.email = u2.email
  AND u1.user_id > u2.user_id;
SELECT user_id FROM users_pg ORDER BY user_id;
-- Output:
-- user_id
-- 1
-- 3
-- 4
```

```sql
-- ROW_NUMBER version (MySQL 8+ and PostgreSQL): number copies, delete rn > 1
-- MySQL cannot read the target table in a plain subquery, hence the extra derived table `t`.
DELETE FROM users_window
WHERE user_id IN (
  SELECT user_id FROM (
    SELECT user_id,
           ROW_NUMBER() OVER (PARTITION BY email ORDER BY user_id) AS rn
    FROM users_window
  ) t
  WHERE rn > 1
);
SELECT user_id FROM users_window ORDER BY user_id;
-- Output:
-- user_id
-- 1
-- 3
-- 4
-- Safe-ish production routine: BEGIN; DELETE ...; SELECT COUNT(*) ...; then COMMIT or ROLLBACK
-- (MySQL InnoDB / PostgreSQL both have transactional DELETE). On huge tables delete in batches (LIMIT in MySQL;
-- ctid/id ranges in PostgreSQL) and run VACUUM afterwards in PostgreSQL.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: MySQL ERROR 1093 - You can't specify target table 'users' for update in FROM clause
DELETE FROM users WHERE user_id NOT IN (SELECT MIN(user_id) FROM users GROUP BY email);
-- ✅ Wrap in a derived table (shown above); PostgreSQL accepts the unwrapped form.

-- ❌ Wrong: MAX/MIN on the wrong column and deleting the newest/original data you meant to keep
-- ❌ Wrong: running the DELETE before the SELECT preview, or outside a transaction
-- ❌ Wrong: deleting in the child's parent table without checking foreign keys that point at the removed ids
-- ❌ Wrong: no UNIQUE constraint afterwards -> duplicates return next week
```

---

## 🎯 Interview Tip (1 line)
Say: "I preview with a SELECT, archive or run it in a transaction, keep MIN(id) per business key, mention MySQL's error 1093 workaround versus PostgreSQL's DELETE ... USING, repoint foreign keys first if needed, and finish with a UNIQUE constraint so it cannot recur."

---

## 🔗 Related Questions
→ Q057 (Find duplicate rows) | Q239 (Find duplicates - interview classic) | Q014 (UPDATE with JOIN, MySQL vs PgSQL) | Q075 (Top N per group)
