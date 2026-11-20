---

# Q175. UNION vs UNION ALL
# Category: Interview Classics
# Difficulty: ⭐ Easy
# DB: SQL Server (same behaviour in MySQL and PostgreSQL; MySQL 8.0.31+ and PostgreSQL also support INTERSECT/EXCEPT like SQL Server)

---

## ❓ Question
You have customer lists from two years. Combine them into one result. What is the difference between `UNION` and `UNION ALL`, which is faster, and when is `UNION` the wrong choice?

---

## 💡 Quick Concept (2 lines only)
`UNION` appends the results and removes duplicate rows (needs a sort/hash distinct step); `UNION ALL` just appends and keeps every row, so it is cheaper. Both need the same number of columns with compatible types, and ORDER BY goes once at the very end.
हिंदी: UNION = जोड़ो + duplicates हटाओ (महँगा)। UNION ALL = बस जोड़ो (सस्ता)। ORDER BY सबसे अंत में, एक बार।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Customers2023 (Email VARCHAR(100) NOT NULL, Name VARCHAR(50) NOT NULL);
CREATE TABLE dbo.Customers2024 (Email VARCHAR(100) NOT NULL, Name VARCHAR(50) NOT NULL);

INSERT INTO dbo.Customers2023 (Email, Name) VALUES
  ('asha@shop.in',  'Asha'),
  ('ravi@shop.in',  'Ravi'),
  ('meena@shop.in', 'Meena');

INSERT INTO dbo.Customers2024 (Email, Name) VALUES
  ('ravi@shop.in',  'Ravi'),
  ('meena@shop.in', 'Meena'),
  ('karan@shop.in', 'Karan'),
  ('karan@shop.in', 'Karan');   -- duplicate INSIDE the 2024 table itself

-- ============================================
-- UNION : distinct rows across both inputs
-- ============================================
SELECT Email, Name FROM dbo.Customers2023
UNION
SELECT Email, Name FROM dbo.Customers2024
ORDER BY Email;

-- Result derived from equivalent query on SQLite 3 (same semantics); not executed on SQL Server
-- Email          | Name
-- asha@shop.in   | Asha
-- karan@shop.in  | Karan     <- the in-table duplicate is removed too
-- meena@shop.in  | Meena
-- ravi@shop.in   | Ravi

-- ============================================
-- UNION ALL : every row, no distinct step
-- ============================================
SELECT Email, Name FROM dbo.Customers2023
UNION ALL
SELECT Email, Name FROM dbo.Customers2024
ORDER BY Email;

-- Email          | Name
-- asha@shop.in   | Asha
-- karan@shop.in  | Karan
-- karan@shop.in  | Karan
-- meena@shop.in  | Meena
-- meena@shop.in  | Meena
-- ravi@shop.in   | Ravi
-- ravi@shop.in   | Ravi      (7 rows in total)

-- Set operators that compare rows the same way:
SELECT Email FROM dbo.Customers2023 INTERSECT SELECT Email FROM dbo.Customers2024;
-- meena@shop.in, ravi@shop.in
SELECT Email FROM dbo.Customers2023 EXCEPT SELECT Email FROM dbo.Customers2024;
-- asha@shop.in
```

---

## 🔍 Why This Works (3 lines max)
UNION compares whole rows, so it must sort or hash all rows to find duplicates, and that costs CPU, memory and possibly tempdb spills. UNION ALL streams rows straight through. Duplicate detection also treats two NULLs as equal, and in SQL Server the comparison follows the column collation.
हिंदी: UNION को पूरी row compare करनी पड़ती है, इसलिए sort/hash लगता है। UNION ALL सीधा stream। Duplicates ना हों तो ALL use करो।

---

## ⚡ Alternative Solution

```sql
-- Add a source column with UNION ALL: duplicates across sources stay visible and useful
SELECT Email, Name, 2023 AS SourceYear FROM dbo.Customers2023
UNION ALL
SELECT Email, Name, 2024 AS SourceYear FROM dbo.Customers2024;

-- Distinct emails only, with UNION ALL + GROUP BY (control which columns decide uniqueness)
SELECT Email, MIN(Name) AS Name
FROM (
  SELECT Email, Name FROM dbo.Customers2023
  UNION ALL
  SELECT Email, Name FROM dbo.Customers2024
) AS Combined
GROUP BY Email;
-- Result derived from equivalent query on SQLite 3: asha, karan, meena, ravi (4 rows)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: using UNION "by habit" when the inputs cannot overlap (for example, partitions by year).
--    Result is the same but you pay for a pointless distinct step.
-- ✅ Use UNION ALL when duplicates are impossible or wanted.

-- ❌ Wrong: ORDER BY inside the first SELECT
SELECT Email FROM dbo.Customers2023 ORDER BY Email
UNION ALL
SELECT Email FROM dbo.Customers2024;     -- syntax error; ORDER BY only after the last SELECT

-- ❌ Wrong: mismatched columns/types: different counts is an error; types are converted by
--    data type precedence (VARCHAR vs INT can fail at runtime on a non-numeric string).
-- ❌ Wrong: expecting UNION to keep input order. Without ORDER BY, order is not guaranteed.
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "My default is UNION ALL, and I use UNION only when I really need dedup across inputs. If I need dedup on specific keys, I prefer UNION ALL with ROW_NUMBER or GROUP BY, so I choose which row wins. Column names come from the first SELECT, and I always check data type precedence." Mention that in a view over partitioned tables, UNION ALL is what lets the optimizer eliminate branches.

---

## 🔗 Related Questions
→ Q044 (UNION, UNION ALL, INTERSECT, EXCEPT) | Q046 (find duplicates and delete safely) | Q066 (deduplicate with ROW_NUMBER) | Q172 (WHERE vs HAVING) | Q188 (find duplicate rows)
