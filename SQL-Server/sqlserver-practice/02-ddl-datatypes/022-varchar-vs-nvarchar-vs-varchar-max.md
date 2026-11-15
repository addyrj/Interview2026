---

# Q022. VARCHAR vs NVARCHAR vs VARCHAR(MAX)
# Category: DDL + DATA TYPES
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: utf8mb4 VARCHAR handles Unicode natively; PostgreSQL: text/varchar are UTF-8, no N-types)

---

## ❓ Question
A Customers table stores names (some in Hindi), emails and long notes. Which of VARCHAR, NVARCHAR and VARCHAR(MAX) do you use, what is the storage cost, what does the `N'...'` prefix do, and what are the `LEN` vs `DATALENGTH` and silent-truncation traps?

---

## 💡 Quick Concept (2 lines only)
VARCHAR stores single-byte code-page characters; NVARCHAR stores UTF-16 (2 bytes per char) so it holds any language. `(MAX)` lifts the 8000 byte / 4000 char limit to 2 GB but stores large values off-row and cannot be an index key.
हिंदी: Hindi/Unicode चाहिए तो NVARCHAR और string literal पर N'...' prefix। VARCHAR 1 byte/char, NVARCHAR 2 bytes/char। (MAX) बहुत बड़े text के लिए।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Customers (
  CustomerId INT IDENTITY(1,1) PRIMARY KEY,
  Name       NVARCHAR(100)  NOT NULL,   -- people names: Unicode
  Email      VARCHAR(255)   NOT NULL,   -- ASCII by spec: half the storage
  Notes      NVARCHAR(MAX)  NULL        -- free text
);

INSERT INTO Customers (Name, Email, Notes) VALUES
  (N'Aditya',  'aditya@example.com', NULL),
  (N'नमस्ते', 'namaste@example.com', N'VIP customer');
GO

-- ============================================
-- SOLUTION: storage and length behaviour
-- ============================================

SELECT
    LEN(Name)        AS Chars,
    DATALENGTH(Name) AS Bytes
FROM Customers
ORDER BY CustomerId;

-- Output:
-- Chars | Bytes
-- 6     | 12
-- 6     | 12
-- ("Aditya" has 6 letters; the Devanagari word is 6 UTF-16 code units. Both are NVARCHAR so 2 bytes
--  each. Counts confirmed with Python len() and UTF-16 encoding; not executed on SQL Server.)

-- Same text in VARCHAR is 1 byte per char for ASCII
SELECT DATALENGTH('Aditya') AS VarcharBytes, DATALENGTH(N'Aditya') AS NvarcharBytes;
-- Output:
-- VarcharBytes | NvarcharBytes
-- 6            | 12

-- LEN ignores trailing spaces, DATALENGTH does not
SELECT LEN('ab  ') AS LenResult, DATALENGTH('ab  ') AS BytesResult;
-- Output:
-- LenResult | BytesResult
-- 2         | 4

-- Without the N prefix the literal is converted to the database code page FIRST
SELECT 'नमस्ते' AS WithoutN, N'नमस्ते' AS WithN;
-- On a Latin1 (non-UTF-8) collation WithoutN shows ??????; WithN shows the Hindi text.
-- (Per Microsoft docs; depends on collation; not executed.)
```

---

## 🔍 Why This Works (3 lines max)
NVARCHAR(100) means 100 UTF-16 code units (200 bytes); VARCHAR(100) means 100 bytes in the column's code page. Literals without `N` are VARCHAR, so non-Latin characters are lost before they reach the column. `LEN` counts characters excluding trailing spaces, `DATALENGTH` counts bytes.
हिंदी: N prefix के बिना literal पहले code page में बदलता है और Hindi '?' बन जाती है। LEN = characters (trailing space छोड़कर), DATALENGTH = bytes।

---

## ⚡ Alternative Solution

```sql
-- SQL Server 2019+: UTF-8 collations let VARCHAR store full Unicode (often smaller for mostly-ASCII text)
CREATE TABLE Articles (
  ArticleId INT PRIMARY KEY,
  Title     VARCHAR(200) COLLATE Latin1_General_100_CI_AS_SC_UTF8 NOT NULL
);

-- Sizing rule of thumb:
--  * emails, codes, country codes, hashes: VARCHAR(n)
--  * names, addresses, anything user-typed and international: NVARCHAR(n)
--  * > 8000 bytes (or > 4000 NVARCHAR chars): (MAX), keep it out of hot tables and indexes
-- Use CHAR(n)/NCHAR(n) only for truly fixed-length values (e.g., CHAR(2) country code).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: no length: DECLARE/column default is 1, CAST/CONVERT default is 30
DECLARE @v VARCHAR;
SET @v = 'Hello';
SELECT @v AS OneChar;                                  -- H
SELECT CAST(REPLICATE('x', 40) AS VARCHAR) AS Cut;     -- silently truncated to 30 characters

-- ❌ Wrong: implicit conversion in a join/WHERE: NVARCHAR parameter vs VARCHAR column
-- WHERE Email = @p  (where @p is NVARCHAR) makes SQL Server convert the column side -> index scan.
-- ✅ Declare parameters with the SAME type as the column (Node mssql: sql.VarChar, not sql.NVarChar).

-- ❌ Wrong: VARCHAR(MAX) everywhere (cannot be an index key, extra LOB overhead, poor estimates)
-- ❌ Wrong: INSERT longer text than the column: raises "String or binary data would be truncated"
--           (the message text varies by version); SET ANSI_WARNINGS OFF would truncate silently - avoid.
```

---

## 🎯 Interview Tip (1 line)
Say: "NVARCHAR for anything human-typed or international, VARCHAR for known-ASCII fields like emails and codes, MAX only when values really exceed 8000 bytes. I always use the N prefix, match parameter types to column types to avoid implicit-conversion scans, and mention 2019 UTF-8 collations as a storage optimization." In Node `mssql`, the default for JS strings is NVARCHAR, so set `sql.VarChar` explicitly on VARCHAR columns.

---

## 🔗 Related Questions
→ Q006 (string functions) | Q018 (collation and case sensitivity) | Q021 (numeric data types) | Q143 (avoiding implicit conversions)
