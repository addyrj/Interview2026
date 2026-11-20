---

# Q188. Find Duplicate Rows
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL/PostgreSQL: same GROUP BY logic; SQL Server can DELETE through a CTE, MySQL cannot)

---

## ❓ Question
The Customers table has duplicate sign-ups (same email, sometimes different casing). (1) List the duplicated emails with counts. (2) Show every row that is a duplicate. (3) Delete the duplicates, keeping the lowest CustomerId, safely and inside a transaction.

---

## 💡 Quick Concept (2 lines only)
Find duplicates with GROUP BY + HAVING COUNT(*) > 1. To delete, number rows with ROW_NUMBER() OVER (PARTITION BY key ORDER BY CustomerId) and delete rn > 1 — T-SQL allows DELETE directly on a CTE.
हिंदी: Duplicate = GROUP BY + HAVING COUNT > 1। Delete के लिए ROW_NUMBER लगाओ और rn > 1 वाली rows CTE से सीधे delete करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Customers (
    CustomerId INT IDENTITY(1,1) PRIMARY KEY,
    FullName   NVARCHAR(100) NOT NULL,
    Email      NVARCHAR(255) NOT NULL,
    CreatedAt  DATE NOT NULL
);

INSERT INTO Customers (FullName, Email, CreatedAt) VALUES
 (N'Asha Rao',    N'asha@shop.com',   '2024-01-05'),
 (N'Asha R',      N'ASHA@shop.com',   '2024-02-11'),  -- same email, different case
 (N'Asha Rao',    N'asha@shop.com',   '2024-03-02'),
 (N'Vikram Sen',  N'vikram@shop.com', '2024-01-20'),
 (N'Meera Nair',  N'meera@shop.com',  '2024-02-01'),
 (N'Meera N',     N'meera@shop.com',  '2024-04-09'),
 (N'Rohit Jain',  N'rohit@shop.com',  '2024-03-15');
GO

-- ============================================
-- STEP 1: WHICH EMAILS ARE DUPLICATED?
-- ============================================
SELECT LOWER(Email) AS Email, COUNT(*) AS Occurrences
FROM Customers
GROUP BY LOWER(Email)
HAVING COUNT(*) > 1
ORDER BY Occurrences DESC, Email;

-- Output (result derived from equivalent query on SQLite; not executed on SQL Server):
-- Email          | Occurrences
-- asha@shop.com  | 3
-- meera@shop.com | 2

-- ============================================
-- STEP 2: SHOW THE EXTRA ROWS (everything except the survivor)
-- ============================================
SELECT CustomerId, Email, rn
FROM (
    SELECT CustomerId, Email,
           ROW_NUMBER() OVER (PARTITION BY LOWER(Email) ORDER BY CustomerId) AS rn
    FROM Customers
) t
WHERE rn > 1
ORDER BY CustomerId;

-- Output (SQLite equivalent):
-- CustomerId | Email          | rn
-- 2          | ASHA@shop.com  | 2
-- 3          | asha@shop.com  | 3
-- 6          | meera@shop.com | 2

-- ============================================
-- STEP 3: DELETE THEM SAFELY (T-SQL: DELETE through a CTE)
-- ============================================
BEGIN TRAN;

WITH Numbered AS (
    SELECT ROW_NUMBER() OVER (PARTITION BY LOWER(Email) ORDER BY CustomerId) AS rn
    FROM Customers
)
DELETE FROM Numbered WHERE rn > 1;

SELECT @@ROWCOUNT AS RowsDeleted;   -- expect 3 (checked via the same delete logic on SQLite)

-- Review, then COMMIT; (or ROLLBACK; if the count looks wrong)
COMMIT;

-- Remaining rows: CustomerId 1, 4, 5, 7

-- Prevent it from happening again:
CREATE UNIQUE INDEX UX_Customers_Email ON Customers (Email);
-- Note: default SQL Server collation is case-insensitive, so ASHA@ and asha@ collide here.
```

---

## 🔍 Why This Works (3 lines max)
ROW_NUMBER restarts per email, so rn = 1 is the survivor and every rn > 1 is a duplicate. SQL Server lets DELETE target a CTE, which deletes the underlying base-table rows — no self-join or NOT IN needed. Wrapping it in a transaction with @@ROWCOUNT lets you verify before COMMIT.
हिंदी: rn = 1 बचता है, rn > 1 delete होता है। CTE पर DELETE चलाने से base table की rows हटती हैं। COMMIT से पहले @@ROWCOUNT check करो।

---

## ⚡ Alternative Solution

```sql
-- Classic: keep MIN(CustomerId) per email
DELETE FROM Customers
WHERE CustomerId NOT IN (
    SELECT MIN(CustomerId) FROM Customers GROUP BY LOWER(Email)
);
-- Works because CustomerId is NOT NULL. Slower and less flexible than ROW_NUMBER
-- when "which one to keep" is not simply the lowest id (e.g. keep the latest CreatedAt).

-- Also valid: self-join delete
DELETE c1
FROM Customers c1
JOIN Customers c2
  ON LOWER(c1.Email) = LOWER(c2.Email) AND c1.CustomerId > c2.CustomerId;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: GROUP BY Email without thinking about casing/whitespace
-- (fine on a case-insensitive collation, silently wrong on a _CS collation; also misses 'asha@shop.com ')
-- ✅ Normalise first: GROUP BY LOWER(LTRIM(RTRIM(Email)))

-- ❌ Wrong: running the DELETE with no transaction and no preview
-- ✅ SELECT the rn > 1 rows first, wrap in BEGIN TRAN, check @@ROWCOUNT, then COMMIT

-- ❌ Wrong: NOT IN with a subquery that can return NULL -> deletes nothing
-- ✅ Use NOT EXISTS or ROW_NUMBER

-- ❌ Wrong: deleting 50M duplicates in one statement -> huge log growth, long blocking
-- ✅ DELETE TOP (10000) ... in a loop (see Q145)
```

---

## 🎯 Interview Tip (1 line)
Say: "I preview with ROW_NUMBER, delete through the CTE inside a transaction, verify @@ROWCOUNT, and then add a unique index so the problem cannot come back. On big tables I batch the delete, and I check whether foreign keys point at the rows I am removing." Duplicates are a data-model bug — fixing the constraint is the senior answer.

---

## 🔗 Related Questions
→ Q046 (Find duplicates and delete them safely) | Q066 (Deduplicate with ROW_NUMBER) | Q053 (Anti-joins / NOT IN trap) | Q145 (Batching large deletes)
