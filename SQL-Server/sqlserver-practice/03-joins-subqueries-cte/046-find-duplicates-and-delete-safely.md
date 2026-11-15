---

# Q046. Find Duplicates and Delete Them Safely
# Category: Joins, Subqueries & CTEs
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL cannot DELETE from a CTE and needs a derived-table wrapper; PostgreSQL uses DELETE ... USING or a subquery on ctid/id)

---

## ❓ Question
`Customers` contains the same email several times. List the duplicated emails, preview exactly which rows would be removed (keep the oldest per email), delete them inside a transaction with a row-count check, and prevent it from happening again.

---

## 💡 Quick Concept (2 lines only)
Find with `GROUP BY ... HAVING COUNT(*) > 1`; delete with `ROW_NUMBER() OVER (PARTITION BY email ORDER BY ...)` and remove rows where `rn > 1`. T-SQL can `DELETE` straight from a CTE, which deletes from the underlying table.
हिंदी: Duplicates = GROUP BY + HAVING। Delete = ROW_NUMBER से rn > 1 वाली rows हटाओ। T-SQL में CTE से सीधे DELETE हो जाता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Customers (
  CustomerId INT IDENTITY(1,1) PRIMARY KEY,
  Name       VARCHAR(100) NOT NULL,
  Email      VARCHAR(255) NOT NULL,
  CreatedAt  DATE         NOT NULL
);

INSERT INTO Customers (Name, Email, CreatedAt) VALUES
  ('Alice',     'alice@example.com', '2024-01-01'),
  ('Alice R',   'alice@example.com', '2024-02-01'),
  ('Alice Rao', 'alice@example.com', '2024-03-01'),
  ('Bob',       'bob@example.com',   '2024-01-05'),
  ('Carol',     'carol@example.com', '2024-01-07'),
  ('Carol S',   'carol@example.com', '2024-02-07');

-- ============================================
-- STEP 1: FIND DUPLICATED EMAILS
-- ============================================
SELECT Email, COUNT(*) AS Occurrences
FROM Customers
GROUP BY Email
HAVING COUNT(*) > 1
ORDER BY Email;
-- EXPECTED OUTPUT (derived on SQLite):
-- Email             | Occurrences
-- alice@example.com | 3
-- carol@example.com | 2

-- ============================================
-- STEP 2: PREVIEW WHAT WOULD BE DELETED (always SELECT first)
-- ============================================
WITH Ranked AS (
  SELECT CustomerId, Email,
         ROW_NUMBER() OVER (PARTITION BY Email ORDER BY CreatedAt, CustomerId) AS rn
  FROM Customers
)
SELECT CustomerId, Email, rn
FROM Ranked
WHERE rn > 1;
-- EXPECTED OUTPUT (derived on SQLite):
-- CustomerId | Email             | rn
-- 2          | alice@example.com | 2
-- 3          | alice@example.com | 3
-- 6          | carol@example.com | 2

-- ============================================
-- STEP 3: DELETE INSIDE A TRANSACTION (CTE delete, T-SQL only)
-- ============================================
BEGIN TRANSACTION;

WITH Ranked AS (
  SELECT ROW_NUMBER() OVER (PARTITION BY Email ORDER BY CreatedAt, CustomerId) AS rn
  FROM Customers
)
DELETE FROM Ranked WHERE rn > 1;       -- deletes the underlying Customers rows

SELECT @@ROWCOUNT AS DeletedRows;      -- NOTE: read it immediately; any statement resets it
-- Expected: 3 deleted rows (ids 2, 3, 6) -- count taken from the preview above.

-- If the number is what you expected:
COMMIT TRANSACTION;
-- otherwise: ROLLBACK TRANSACTION;

-- Remaining rows afterwards (derived on SQLite by running the equivalent delete):
-- CustomerId | Name  | Email
-- 1          | Alice | alice@example.com
-- 4          | Bob   | bob@example.com
-- 5          | Carol | carol@example.com

-- ============================================
-- STEP 4: PREVENT RE-OCCURRENCE
-- ============================================
ALTER TABLE Customers ADD CONSTRAINT UQ_Customers_Email UNIQUE (Email);
-- The CTE-DELETE, @@ROWCOUNT and the constraint are T-SQL behaviour per Microsoft docs;
-- not executed on SQL Server (outputs above come from SQLite equivalents).
```

---

## 🔍 Why This Works (3 lines max)
ROW_NUMBER numbers the rows inside each email group in the order you choose, so `rn = 1` is the survivor and everything else is a duplicate. A CTE over a single table is an updatable/deletable view, so `DELETE FROM Ranked` removes real rows. Wrapping it in a transaction with a row-count check turns a risky delete into a reversible one.
हिंदी: ROW_NUMBER हर email group में क्रम देता है, rn = 1 रखो, बाकी delete। CTE से DELETE असली table की rows हटाता है। Transaction में check करके ही COMMIT करो।

---

## ⚡ Alternative Solution

```sql
-- Archive first, then delete (safest in production):
SELECT c.*
INTO CustomersDuplicateArchive           -- SELECT INTO creates the table (T-SQL)
FROM Customers AS c
WHERE EXISTS (
  SELECT 1 FROM Customers AS older
  WHERE older.Email = c.Email
    AND (older.CreatedAt < c.CreatedAt
         OR (older.CreatedAt = c.CreatedAt AND older.CustomerId < c.CustomerId))
);

DELETE c
FROM Customers AS c
WHERE EXISTS (
  SELECT 1 FROM Customers AS older
  WHERE older.Email = c.Email
    AND (older.CreatedAt < c.CreatedAt
         OR (older.CreatedAt = c.CreatedAt AND older.CustomerId < c.CustomerId))
);

-- For huge tables: delete in batches (DELETE TOP (10000) ... in a WHILE loop) to keep the log small.
-- MySQL/PostgreSQL: use DELETE ... JOIN (MySQL) or DELETE ... USING (PostgreSQL).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: meaningless ORDER BY inside ROW_NUMBER
WITH Ranked AS (SELECT ROW_NUMBER() OVER (PARTITION BY Email ORDER BY (SELECT NULL)) AS rn FROM Customers)
DELETE FROM Ranked WHERE rn > 1;
-- ORDER BY (SELECT NULL) = random survivor. You may keep the newest, wrong, row.
-- ✅ Always order by something meaningful plus a unique tiebreaker (CreatedAt, CustomerId).

-- ❌ Wrong: deleting without previewing or without a transaction
-- ✅ SELECT the rn > 1 rows first, then BEGIN TRAN, DELETE, check @@ROWCOUNT, then COMMIT.

-- ❌ Wrong: adding the UNIQUE constraint before cleaning
-- ALTER TABLE fails because duplicates already exist. Clean first, constrain second.

-- ❌ Wrong: case/trim differences ('Alice@Example.com ' vs 'alice@example.com')
-- Default collations are case-insensitive but trailing/leading spaces and look-alike data still differ;
-- normalise (LTRIM/RTRIM, LOWER) in the PARTITION BY if the business rule says they are the same.
```

---

## 🎯 Interview Tip (1 line)
Say: "I detect with GROUP BY/HAVING, preview with ROW_NUMBER, and delete via a CTE inside an explicit transaction, checking @@ROWCOUNT before commit. For big tables I archive and delete in batches, and I finish by adding a unique constraint or unique index so the application cannot recreate the problem."

---

## 🔗 Related Questions
→ Q066 (deduplicate with ROW_NUMBER) | Q188 (find duplicate rows) | Q010 (INSERT, UPDATE, DELETE, OUTPUT) | Q145 (batching large deletes)
