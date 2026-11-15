---

# Q044. UNION, UNION ALL, INTERSECT, EXCEPT
# Category: Joins, Subqueries & CTEs
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: INTERSECT/EXCEPT only from 8.0.31; PostgreSQL: all supported, EXCEPT is also EXCEPT, Oracle calls it MINUS)

---

## ❓ Question
`Buyers2023` and `Buyers2024` list customers who bought in each year (duplicates exist because one customer can buy twice). Find: all customers who bought in either year, every row from both, customers who bought in both years, customers who bought in 2023 but not 2024, and the reverse.

---

## 💡 Quick Concept (2 lines only)
`UNION` removes duplicates (extra sort/hash step), `UNION ALL` keeps everything and is faster. `INTERSECT` = rows in both, `EXCEPT` = rows in the first query not in the second; both also de-duplicate and treat NULLs as equal.
हिंदी: UNION = duplicates हटाता है, UNION ALL = सब रखता है (तेज़)। INTERSECT = दोनों में common, EXCEPT = पहले में है पर दूसरे में नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Buyers2023 (CustomerId INT NOT NULL, Email VARCHAR(100) NOT NULL);
CREATE TABLE Buyers2024 (CustomerId INT NOT NULL, Email VARCHAR(100) NOT NULL);

INSERT INTO Buyers2023 (CustomerId, Email) VALUES
  (1, 'a@x.com'), (2, 'b@x.com'), (3, 'c@x.com'), (3, 'c@x.com');  -- 3 bought twice
INSERT INTO Buyers2024 (CustomerId, Email) VALUES
  (2, 'b@x.com'), (3, 'c@x.com'), (4, 'd@x.com');

-- ============================================
-- UNION (distinct)
-- ============================================
SELECT CustomerId FROM Buyers2023
UNION
SELECT CustomerId FROM Buyers2024
ORDER BY CustomerId;          -- ORDER BY only once, at the very end
-- EXPECTED OUTPUT (derived on SQLite; engine-neutral set logic):
-- 1, 2, 3, 4

-- ============================================
-- UNION ALL (keeps duplicates)
-- ============================================
SELECT CustomerId FROM Buyers2023
UNION ALL
SELECT CustomerId FROM Buyers2024
ORDER BY CustomerId;
-- EXPECTED OUTPUT: 1, 2, 2, 3, 3, 3, 4   (7 rows)

-- ============================================
-- INTERSECT (in both)
-- ============================================
SELECT CustomerId FROM Buyers2023
INTERSECT
SELECT CustomerId FROM Buyers2024
ORDER BY CustomerId;
-- EXPECTED OUTPUT: 2, 3

-- ============================================
-- EXCEPT (2023 only, then 2024 only)
-- ============================================
SELECT CustomerId FROM Buyers2023
EXCEPT
SELECT CustomerId FROM Buyers2024;
-- EXPECTED OUTPUT: 1

SELECT CustomerId FROM Buyers2024
EXCEPT
SELECT CustomerId FROM Buyers2023;
-- EXPECTED OUTPUT: 4

-- Result sets above derived from equivalent queries on SQLite; not executed on SQL Server.
-- Precedence in T-SQL: INTERSECT binds tighter than UNION / EXCEPT (evaluated first);
-- use parentheses when mixing operators.
```

---

## 🔍 Why This Works (3 lines max)
Set operators compare whole rows, column by column, and need the same number of columns with compatible types in the same order; column names come from the first query. UNION/INTERSECT/EXCEPT add a distinct step, UNION ALL does not. That is why UNION ALL is the right default when you know the inputs cannot overlap.
हिंदी: Set operators पूरी row compare करते हैं; columns की गिनती और type मेल खाने चाहिए। Overlap नहीं है तो UNION ALL use करो — distinct का extra काम नहीं।

---

## ⚡ Alternative Solution

```sql
-- INTERSECT / EXCEPT rewritten with EXISTS (lets you return extra columns from the left table):
SELECT DISTINCT b23.CustomerId, b23.Email
FROM Buyers2023 AS b23
WHERE EXISTS (SELECT 1 FROM Buyers2024 AS b24 WHERE b24.CustomerId = b23.CustomerId);   -- INTERSECT

SELECT DISTINCT b23.CustomerId, b23.Email
FROM Buyers2023 AS b23
WHERE NOT EXISTS (SELECT 1 FROM Buyers2024 AS b24 WHERE b24.CustomerId = b23.CustomerId); -- EXCEPT

-- INTERSECT/EXCEPT treat NULL = NULL as a match; a plain "=" join does not.
-- That is the main behavioural difference between them and a join.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: ORDER BY inside each branch
SELECT CustomerId FROM Buyers2023 ORDER BY CustomerId
UNION ALL
SELECT CustomerId FROM Buyers2024;
-- Msg: ORDER BY is not allowed in a branch of a set operation (only in the last statement).
-- ✅ Put one ORDER BY at the end (it may use the first query's column names).

-- ❌ Wrong: using UNION "just to be safe" on millions of rows
-- It forces a sort/hash distinct. Use UNION ALL when branches are disjoint (e.g. archive + current table).

-- ❌ Wrong: mismatched column order or types
SELECT CustomerId, Email FROM Buyers2023
UNION ALL
SELECT Email, CustomerId FROM Buyers2024;   -- errors on conversion or silently mixes data
```

---

## 🎯 Interview Tip (1 line)
Say: "UNION ALL by default, UNION only when I truly need de-duplication. INTERSECT and EXCEPT are null-safe and set-based, but when I need columns that are not part of the comparison I use EXISTS / NOT EXISTS. Also remember INTERSECT has higher precedence than UNION and EXCEPT in T-SQL."

---

## 🔗 Related Questions
→ Q053 (anti-joins) | Q036 (joins) | Q175 (UNION vs UNION ALL) | Q039 (subqueries, EXISTS)
