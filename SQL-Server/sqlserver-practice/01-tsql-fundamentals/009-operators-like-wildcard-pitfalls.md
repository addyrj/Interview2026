---

# Q009. Operators, LIKE and Wildcard Pitfalls
# Category: T-SQL Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (bracket classes [A-C] and [^A-C] are T-SQL only; PostgreSQL uses ~ regex / ILIKE, MySQL uses REGEXP)

---

## ❓ Question
In a `Products` table, find names starting with A, starting with A-C, and NOT starting with A-C; match the literal underscore in SKUs like `AK_100` and the literal percent sign in notes like `50% off`. Explain why `LIKE '%text'` is slow and what happens with NULL and `NOT LIKE`.

---

## 💡 Quick Concept (2 lines only)
T-SQL LIKE wildcards: `%` any string, `_` exactly one char, `[abc]`/`[a-c]` one char in set/range, `[^a-c]` one char NOT in it. To match a wildcard literally wrap it in brackets (`[_]`, `[%]`) or use `ESCAPE`.
हिंदी: `_` और `%` खुद wildcard हैं, literal चाहिए तो `[_]` या ESCAPE use करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Products (
  ProductId   INT           NOT NULL PRIMARY KEY,
  ProductName NVARCHAR(100) NOT NULL,
  Sku         VARCHAR(20)   NOT NULL,
  Notes       NVARCHAR(200) NULL
);

INSERT INTO dbo.Products (ProductId, ProductName, Sku, Notes) VALUES
  (1, N'Apple Keyboard', 'AK_100', N'50% off'),
  (2, N'Acer Laptop',    'AC-200', NULL),
  (3, N'Bose Speaker',   'BS_300', N'Fragile'),
  (4, N'Canon Camera',   'CN-400', N'100% genuine'),
  (5, N'Dell Monitor',   'DL_500', NULL);

-- ============================================
-- SOLUTION
-- ============================================

SELECT ProductName FROM dbo.Products WHERE ProductName LIKE 'A%';        -- Acer Laptop, Apple Keyboard
SELECT ProductName FROM dbo.Products WHERE ProductName LIKE '[A-C]%';    -- Acer, Apple, Bose, Canon
SELECT ProductName FROM dbo.Products WHERE ProductName LIKE '[^A-C]%';   -- Dell Monitor

-- Literal underscore: the bare '_' matches ANY single char
SELECT Sku FROM dbo.Products WHERE Sku LIKE '%[_]%';         -- AK_100, BS_300, DL_500
SELECT Sku FROM dbo.Products WHERE Sku LIKE '%\_%' ESCAPE '\'; -- same result

SELECT Sku FROM dbo.Products WHERE Sku LIKE '%_%';           -- ALL 5 rows (every SKU has >= 1 char)

-- Literal percent sign
SELECT ProductId FROM dbo.Products WHERE Notes LIKE '%[%]%'; -- 1, 4

-- NOT LIKE and NULL
SELECT ProductId FROM dbo.Products WHERE Notes NOT LIKE '%Fragile%';  -- 1, 4 (NULL notes 2 and 5 are dropped)
SELECT ProductId FROM dbo.Products WHERE Notes IS NULL OR Notes NOT LIKE '%Fragile%';  -- 1, 2, 4, 5

-- Note: results derived from equivalent queries on SQLite (GLOB for [A-C] classes,
-- LIKE ... ESCAPE for the literal _ and %); default SQL Server collations are
-- case-insensitive, like SQLite LIKE for ASCII. Not executed on SQL Server.
```

---

## 🔍 Why This Works (3 lines max)
A character class in brackets matches exactly one character, and the caret negates it, which gives you cheap pattern matching without regex. `LIKE 'A%'` is a prefix search and can use an index seek; a leading wildcard (`'%A'` or `'%A%'`) forces a scan because the index is ordered from the first character.
हिंदी: Prefix search (`'A%'`) index use कर सकता है, `'%A'` पूरा scan करता है।

---

## ⚡ Alternative Solution

```sql
-- Range/prefix via comparison operators (SARGable, same result as LIKE 'A%')
SELECT ProductName FROM dbo.Products WHERE ProductName >= N'A' AND ProductName < N'B';

-- Contains-style search at scale: full-text index + CONTAINS
-- SELECT * FROM dbo.Products WHERE CONTAINS(ProductName, N'"keyboard*"');   -- needs a full-text catalog

-- Other operators worth knowing: BETWEEN (inclusive), IN, EXISTS, <> and != (both valid), ALL/ANY
-- PATINDEX('%[0-9]%', Sku) returns the position of the first digit (supports wildcards, unlike CHARINDEX)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: expecting '_' to be a literal underscore
SELECT * FROM dbo.Products WHERE Sku LIKE 'AK_100';   -- also matches 'AKX100', 'AK-100'
-- ✅ Sku LIKE 'AK[_]100'

-- ❌ Wrong: leading wildcard on a big indexed column -> full scan
WHERE ProductName LIKE '%phone%'
-- ✅ prefix search, full-text search, or a computed/reversed column for suffix search

-- ❌ Wrong: assuming LIKE is case-sensitive -> depends on the column collation
-- (default CI; with a _CS_ collation 'a%' will not match 'Apple'). Use COLLATE for explicit control.

-- ❌ Wrong: Notes NOT LIKE '%x%' and expecting NULL rows to appear (NULL -> UNKNOWN -> filtered out)

-- ❌ Wrong: user input concatenated into the pattern: LIKE '%' + @term + '%' with '%'/'[' typed by the user
-- ✅ Escape them (REPLACE(@term, '[', '[[]')) or pass a parameter and sanitise first.
```

---

## 🎯 Interview Tip (1 line)
Say: "Prefix LIKE is index-friendly, a leading wildcard is a scan, so for real search I'd use full-text or an external index. I escape user-supplied wildcards and I'm explicit about collation because case sensitivity is a property of the column, not the operator."

---

## 🔗 Related Questions
→ Q018 (Collation and case sensitivity) | Q110 (SARGable predicates) | Q006 (String functions) | Q137 (SQL injection and parameterization) | Q087 (Search procedure with dynamic filters)
