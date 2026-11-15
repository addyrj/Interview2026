---

# Q006. String Functions — LEN, SUBSTRING, CHARINDEX, STRING_AGG, STRING_SPLIT
# Category: T-SQL Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (STRING_AGG 2017+, STRING_SPLIT 2016+ (compat 130), TRIM 2017+; MySQL: GROUP_CONCAT, PostgreSQL: string_agg/string_to_table)

---

## ❓ Question
Given user emails and padded names: extract the domain, measure lengths (and explain `LEN` vs `DATALENGTH`), trim spaces, concatenate emails per department with `STRING_AGG` in a defined order, and split a comma-separated tag list into rows.

---

## 💡 Quick Concept (2 lines only)
`CHARINDEX(find, text)` is 1-based (0 = not found); `SUBSTRING(text, start, length)` needs the length. `LEN` ignores TRAILING spaces and counts characters; `DATALENGTH` counts bytes (NVARCHAR = 2 bytes/char).
हिंदी: CHARINDEX 1 से शुरू होता है, 0 मतलब नहीं मिला। LEN trailing spaces नहीं गिनता।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.AppUsers (
  UserId     INT           NOT NULL PRIMARY KEY,
  Department NVARCHAR(30)  NOT NULL,
  FullName   NVARCHAR(100) NOT NULL,
  Email      VARCHAR(100)  NOT NULL
);

INSERT INTO dbo.AppUsers (UserId, Department, FullName, Email) VALUES
  (1, N'Eng',   N'  Aditya Ranjan  ', 'aditya.r@contoso.com'),
  (2, N'Eng',   N'Bob Mehta',         'bob@contoso.com'),
  (3, N'Eng',   N'Carol Shah',        'carol@fabrikam.org'),
  (4, N'Sales', N'Dave Nair',         'dave@contoso.com'),
  (5, N'Sales', N'Eve Iyer',          'eve@fabrikam.org');

-- ============================================
-- 1. CHARINDEX + SUBSTRING (domain), LEN, TRIM
-- ============================================

SELECT UserId,
       Email,
       LEN(Email)                                             AS EmailLen,
       CHARINDEX('@', Email)                                  AS AtPos,
       SUBSTRING(Email, CHARINDEX('@', Email) + 1, LEN(Email)) AS Domain,
       LEN(LTRIM(RTRIM(FullName)))                            AS TrimmedLen
FROM dbo.AppUsers
WHERE UserId IN (1, 3);

-- UserId | Email                | EmailLen | AtPos | Domain       | TrimmedLen
-- 1      | aditya.r@contoso.com | 20       | 9     | contoso.com  | 13
-- 3      | carol@fabrikam.org   | 18       | 6     | fabrikam.org | 10

-- LEN vs DATALENGTH on the padded name (N'  Aditya Ranjan  ', 2+13+2 chars):
--   LEN(FullName)        = 15  (trailing 2 spaces ignored, leading 2 counted)
--   DATALENGTH(FullName) = 34  (17 chars * 2 bytes, NVARCHAR)

-- ============================================
-- 2. STRING_AGG with a defined order (2017+)
-- ============================================

SELECT Department,
       STRING_AGG(Email, ', ') WITHIN GROUP (ORDER BY Email DESC) AS Emails
FROM dbo.AppUsers
GROUP BY Department
ORDER BY Department;

-- Department | Emails
-- Eng        | carol@fabrikam.org, bob@contoso.com, aditya.r@contoso.com
-- Sales      | eve@fabrikam.org, dave@contoso.com

-- ============================================
-- 3. STRING_SPLIT (2016+, db compatibility level >= 130)
-- ============================================

SELECT value AS Tag
FROM STRING_SPLIT('sql,azure,nodejs', ',');
-- sql
-- azure
-- nodejs
-- Order of rows is NOT guaranteed by STRING_SPLIT (an ordinal column was added in
-- SQL Server 2022 / Azure SQL via the optional 3rd argument enable_ordinal).

-- Note: lengths/positions/domains and the ordered aggregation were derived from
-- equivalent queries on SQLite (length/instr/substr/group_concat);
-- not executed on SQL Server. LEN vs DATALENGTH and STRING_SPLIT ordering follow
-- Microsoft docs.
```

---

## 🔍 Why This Works (3 lines max)
Domain extraction = find the `@` with CHARINDEX, then take everything after it; passing LEN(Email) as the length is a safe "to the end" idiom. STRING_AGG replaces the old `FOR XML PATH('')` hack and `WITHIN GROUP` controls the concatenation order; STRING_SPLIT turns a delimited string into a one-column table named `value`.
हिंदी: CHARINDEX से position, SUBSTRING से टुकड़ा। STRING_AGG = एक group की values को एक string में जोड़ता है।

---

## ⚡ Alternative Solution

```sql
-- Pre-2017: FOR XML PATH concatenation (fragile with special characters like & <)
SELECT d.Department,
       STUFF((SELECT ', ' + u.Email
              FROM dbo.AppUsers u
              WHERE u.Department = d.Department
              ORDER BY u.Email DESC
              FOR XML PATH('')), 1, 2, '') AS Emails
FROM (SELECT DISTINCT Department FROM dbo.AppUsers) d;

-- Other handy functions: LEFT/RIGHT, REPLACE, CONCAT (NULL-safe), CONCAT_WS (2017+),
-- TRIM (2017+), STUFF, FORMAT, REVERSE, UPPER/LOWER
SELECT CONCAT(N'Hello ', NULL, N'World');   -- 'Hello World' (NULL ignored, unlike +)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: '+' with NULL swallows the whole string
SELECT 'Hello ' + NULL + 'World';           -- NULL (with default CONCAT_NULL_YIELDS_NULL ON)
-- ✅ CONCAT(...) or ISNULL each piece.

-- ❌ Wrong: STRING_AGG result longer than 8000 bytes
SELECT STRING_AGG(Email, ',') FROM dbo.AppUsers;
-- If the input is VARCHAR(n)/NVARCHAR(n) the output is limited to 8000 / 4000 chars
-- and can raise a truncation error. ✅ STRING_AGG(CAST(Email AS VARCHAR(MAX)), ',')

-- ❌ Wrong: trusting LEN for trailing-space checks
SELECT LEN('abc   ');          -- 3, not 6  -> use DATALENGTH if bytes/spaces matter

-- ❌ Wrong: SUBSTRING with start 0 / forgetting 1-based indexing
-- ❌ Wrong: STRING_SPLIT on a DB with compatibility level < 130 -> "invalid object name" error
-- ❌ Wrong: relying on STRING_SPLIT output order for position-sensitive logic
```

---

## 🎯 Interview Tip (1 line)
Say: "For delimited lists from Node I prefer table-valued parameters or OPENJSON over STRING_SPLIT because they give types and order; if I must use STRING_SPLIT I note the compatibility level 130 requirement and that ordering isn't guaranteed (an ordinal option exists in 2022+). Storing CSV in a column is a normalisation smell."

---

## 🔗 Related Questions
→ Q063 (STRING_AGG and ordering) | Q076 (Table-valued parameters) | Q031 (JSON - OPENJSON) | Q110 (SARGable predicates) | Q022 (VARCHAR vs NVARCHAR)
