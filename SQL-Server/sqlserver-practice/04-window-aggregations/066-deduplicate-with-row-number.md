# Q066. Deduplicate with ROW_NUMBER
# Category: WINDOW FUNCTIONS + AGGREGATIONS
# Difficulty: ⭐⭐ Medium
# DB: SQL Server — T-SQL can DELETE directly through a CTE; MySQL/PostgreSQL need a join or `WHERE id IN (...)`

---

## ❓ Question
`Customers` contains duplicate rows for the same email (the same person signed up three times). Keep only the most recent record per email and delete the others. First show which rows would be removed, then delete them and report what was deleted.

---

## 💡 Quick Concept (2 lines only)
Number the rows per duplicate key with ROW_NUMBER() OVER (PARTITION BY key ORDER BY keeper-rule), then delete rows where rn > 1. In T-SQL you can run DELETE straight on the CTE and it deletes from the base table.
हिंदी: Duplicate key पर PARTITION BY, जिसे रखना है उसे ORDER BY से पहले रखो (rn = 1), बाकी (rn > 1) DELETE कर दो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Customers (
    CustomerId INT PRIMARY KEY,
    Email      VARCHAR(50) NOT NULL,
    FullName   VARCHAR(30) NOT NULL,
    CreatedAt  DATE        NOT NULL
);

INSERT INTO Customers (CustomerId, Email, FullName, CreatedAt) VALUES
 (1, 'asha@x.com',  'Asha',       '2024-01-01'),
 (2, 'ravi@x.com',  'Ravi',       '2024-01-02'),
 (3, 'asha@x.com',  'Asha K',     '2024-02-01'),
 (4, 'asha@x.com',  'Asha Kumar', '2024-03-01'),
 (5, 'meena@x.com', 'Meena',      '2024-01-05');

-- ============================================
-- STEP 1: PREVIEW (always look before you delete)
-- ============================================
WITH Dups AS (
    SELECT CustomerId, Email, FullName,
           ROW_NUMBER() OVER (PARTITION BY LOWER(Email)
                              ORDER BY CreatedAt DESC, CustomerId DESC) AS rn
    FROM Customers
)
SELECT CustomerId, Email, FullName, rn FROM Dups ORDER BY Email, rn;

-- EXPECTED OUTPUT (result derived from equivalent query on PostgreSQL (PGlite); not executed on SQL Server):
-- CustomerId | Email       | FullName   | rn
-- 4          | asha@x.com  | Asha Kumar | 1     <- keep
-- 3          | asha@x.com  | Asha K     | 2     <- delete
-- 1          | asha@x.com  | Asha       | 3     <- delete
-- 5          | meena@x.com | Meena      | 1
-- 2          | ravi@x.com  | Ravi       | 1

-- ============================================
-- STEP 2: DELETE through the CTE, report with OUTPUT
-- ============================================
BEGIN TRANSACTION;

WITH Dups AS (
    SELECT CustomerId,
           ROW_NUMBER() OVER (PARTITION BY LOWER(Email)
                              ORDER BY CreatedAt DESC, CustomerId DESC) AS rn
    FROM Customers
)
DELETE FROM Dups
OUTPUT deleted.CustomerId, deleted.Email
WHERE rn > 1;

-- Check the OUTPUT / row count, then COMMIT TRANSACTION; (or ROLLBACK TRANSACTION;)

-- EXPECTED: OUTPUT lists CustomerId 3 and 1; 2 rows affected; rows 2, 4, 5 remain.
-- Delete result derived from an equivalent DELETE ... WHERE id IN (...) RETURNING on PostgreSQL (PGlite);
-- the DELETE-through-CTE and OUTPUT clause are not executed on SQL Server; behaviour per Microsoft docs.
```

---

## 🔍 Why This Works (3 lines max)
PARTITION BY puts each email in its own numbered list; ORDER BY decides who gets rn = 1 (newest CreatedAt, CustomerId as tiebreaker), so everything else is a duplicate. A CTE over a single table is updatable, so DELETE FROM Dups removes the underlying rows. Wrapping it in a transaction with OUTPUT gives an audit trail and a chance to roll back.
हिंदी: ORDER BY तय करता है कौन रहेगा (rn=1)। CTE पर सीधे DELETE चलता है, और OUTPUT से पता चलता है क्या हटा।

---

## ⚡ Alternative Solution

```sql
-- Portable form (also works in PostgreSQL / MySQL 8): delete by key list
DELETE FROM Customers
WHERE CustomerId IN (
    SELECT CustomerId FROM (
        SELECT CustomerId,
               ROW_NUMBER() OVER (PARTITION BY LOWER(Email) ORDER BY CreatedAt DESC, CustomerId DESC) AS rn
        FROM Customers
    ) AS t
    WHERE rn > 1
);
-- Verified on PostgreSQL (PGlite): deletes ids 1 and 3, leaves 2, 4, 5.

-- Prevent it from happening again (after cleanup): a unique constraint
-- ALTER TABLE Customers ADD CONSTRAINT UQ_Customers_Email UNIQUE (Email);
```

---

## ⚠️ Common Mistake

```sql
-- ❌ ROW_NUMBER without a tiebreaker: two rows with the same CreatedAt -> which one survives is arbitrary
ROW_NUMBER() OVER (PARTITION BY Email ORDER BY CreatedAt DESC)

-- ❌ Deleting without a transaction or a preview -> a wrong PARTITION BY (e.g. by FullName) silently wipes real customers
-- ❌ Using DISTINCT or GROUP BY and thinking the table is deduplicated -> they only change the SELECT, not the stored rows
-- ❌ Deleting 20 million rows in one statement: huge log growth and long locks; delete in batches (DELETE TOP (10000) ... loop)
-- ❌ Forgetting the other tables: children rows pointing to the deleted CustomerIds break foreign keys or become orphans
```

---

## 🎯 Interview Tip (1 line)
Say: "I preview with the same CTE, pick the survivor with an explicit, deterministic ORDER BY, delete inside a transaction with OUTPUT for the audit trail, batch big deletes, repoint child rows first, and finish with a UNIQUE constraint so it cannot recur."

---

## 🔗 Related Questions
→ Q046 (Find duplicates and delete them safely) | Q056 (ROW_NUMBER, RANK, DENSE_RANK, NTILE) | Q010 (INSERT, UPDATE, DELETE and OUTPUT clause) | Q067 (Top-N per group with window functions)
