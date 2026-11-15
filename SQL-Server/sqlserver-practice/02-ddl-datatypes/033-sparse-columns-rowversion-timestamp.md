---

# Q033. Sparse Columns, rowversion and timestamp
# Category: DDL + Data Types
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: no sparse columns; PostgreSQL: NULLs already cost ~1 bit via the null bitmap; no rowversion, use xmin or an updated_at/version column)

---

## ❓ Question
(a) A `Products` table has 200 optional attributes that are NULL for most rows. How can SQL Server store NULLs for free? (b) What is `rowversion`, how does it relate to the `timestamp` data type, and how do you use it to detect lost updates?

---

## 💡 Quick Concept (2 lines only)
SPARSE columns store NULL using zero bytes but cost extra bytes for non-NULL values, so they pay off only when most rows are NULL. `rowversion` is an auto-incrementing 8-byte binary counter, unique per database, changed on every row insert or update; `timestamp` is its deprecated synonym and has nothing to do with dates.
हिंदी: Sparse column = NULL के लिए 0 bytes। rowversion = हर update पर बदलने वाला 8-byte counter, date/time नहीं। `timestamp` उसी का पुराना नाम है।

---

## ✅ Answer / Solution

```sql
-- NOT EXECUTED ON SQL SERVER: no equivalent engine. rowversion values are
-- engine-generated and non-deterministic, so none are shown. Behaviour per docs.

-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Products (
    ProductId  INT IDENTITY(1,1) PRIMARY KEY,
    Name       NVARCHAR(100) NOT NULL,
    Price      DECIMAL(10,2) NOT NULL,
    Color      NVARCHAR(30)  SPARSE NULL,     -- mostly NULL attributes
    WeightKg   DECIMAL(6,2)  SPARSE NULL,
    VoltageV   INT           SPARSE NULL,
    RowVer     ROWVERSION                      -- auto-maintained, one per table
);

INSERT INTO Products (Name, Price, Color) VALUES (N'Keyboard', 25.00, N'Black');
INSERT INTO Products (Name, Price)        VALUES (N'Mouse', 12.50);

-- ============================================
-- SOLUTION (a): sparse + column set (optional)
-- ============================================
-- A column set returns all sparse columns as one XML column
-- (declared at CREATE TABLE time): AllAttrs XML COLUMN_SET FOR ALL_SPARSE_COLUMNS

-- ============================================
-- SOLUTION (b): optimistic concurrency with rowversion
-- ============================================
DECLARE @ver BINARY(8);
SELECT @ver = RowVer FROM Products WHERE ProductId = 1;      -- read and remember

-- ... user edits ... then update only if nobody changed the row meanwhile
UPDATE Products
SET Price = 27.00
WHERE ProductId = 1 AND RowVer = @ver;

IF @@ROWCOUNT = 0
    PRINT 'Conflict: row was modified by someone else';    -- reload and retry

-- ============================================
-- EXPECTED OUTPUT (per Microsoft docs; not executed)
-- ============================================
-- If the row is unchanged since read: 1 row affected, no PRINT.
-- If another session updated it first: 0 rows affected, 'Conflict: ...' printed.
-- RowVer is a BINARY(8) such as 0x00000000000007D1 (value differs per database/run).
```

---

## 🔍 Why This Works (3 lines max)
Every write bumps the database-wide rowversion counter and stamps the row, so equality with the value you read proves nothing changed in between. The WHERE clause makes the check and the update one atomic statement; @@ROWCOUNT = 0 signals the lost-update case. Sparse columns skip storage for NULL but add about 4 bytes per non-NULL value, so use them only when roughly 60-90%+ are NULL (see Microsoft's per-type thresholds).
हिंदी: Row पढ़ते समय का version और update के समय का version मिलाओ। मेल न खाए तो किसी और ने बदल दिया (0 rows)। Sparse तभी जब ज़्यादातर NULL हों।

---

## ⚡ Alternative Solution

```sql
-- Compare all editable columns (no extra column, but verbose and fragile)
UPDATE Products SET Price = 27.00
WHERE ProductId = 1 AND Price = 25.00 AND Name = N'Keyboard';

-- Or: an integer Version column you bump manually (portable across MySQL/PostgreSQL)
UPDATE Products SET Price = 27.00, Version = Version + 1
WHERE ProductId = 1 AND Version = 3;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Treating timestamp/rowversion as a date or time
SELECT CAST(RowVer AS DATETIME) FROM Products;    -- meaningless result
-- ✅ Use datetime2 + a DEFAULT/trigger for "last modified"

-- ❌ Making every nullable column SPARSE: non-NULL values cost more, rows can get bigger
-- ❌ Using the keyword 'timestamp' in new code (deprecated in this meaning); use ROWVERSION.
-- ❌ Copying a rowversion as BINARY(8) is fine; trying to INSERT a value into it is not (it cannot be written).
```

---

## 🎯 Interview Tip (1 line)
Say: "For optimistic concurrency I add a rowversion column, send the value back with the update, and treat @@ROWCOUNT = 0 as a conflict I surface as HTTP 409 from the Node API. I only use SPARSE after measuring that most rows are NULL." Mention it is a per-database counter and unrelated to wall-clock time.

---

## 🔗 Related Questions
→ Q020 (@@ROWCOUNT) | Q127 (Optimistic concurrency with rowversion) | Q021 (Data types) | Q025 (CREATE TABLE)
