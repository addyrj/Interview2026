---

# Q049. Gaps and Islands
# Category: Joins, Subqueries & CTEs
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (same pattern works in MySQL 8 and PostgreSQL; date version uses DATEADD in T-SQL)

---

## ❓ Question
Invoice numbers are supposed to be consecutive but some are missing. From `Invoices(InvoiceNo)` list (a) the islands — unbroken runs of numbers with start, end and count, and (b) the gaps — the missing ranges.

---

## 💡 Quick Concept (2 lines only)
Islands: `InvoiceNo - ROW_NUMBER() OVER (ORDER BY InvoiceNo)` is constant inside a consecutive run, so group by it. Gaps: `LEAD(InvoiceNo)` and keep rows where the next value is more than +1.
हिंदी: Island = लगातार numbers का group। `value - ROW_NUMBER()` एक run में constant रहता है, उसी पर GROUP BY। Gap = LEAD से अगला number देखो, फर्क > 1 हो तो gap।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Invoices (InvoiceNo INT NOT NULL PRIMARY KEY);

INSERT INTO Invoices (InvoiceNo) VALUES
  (1), (2), (3), (7), (8), (10), (15), (16), (17);

-- ============================================
-- ISLANDS: runs of consecutive numbers
-- ============================================
SELECT MIN(InvoiceNo) AS StartNo,
       MAX(InvoiceNo) AS EndNo,
       COUNT(*)       AS Cnt
FROM (
  SELECT InvoiceNo,
         InvoiceNo - ROW_NUMBER() OVER (ORDER BY InvoiceNo) AS grp
  FROM Invoices
) AS x
GROUP BY grp
ORDER BY StartNo;

-- EXPECTED OUTPUT (derived on SQLite):
-- StartNo | EndNo | Cnt
-- 1       | 3     | 3
-- 7       | 8     | 2
-- 10      | 10    | 1
-- 15      | 17    | 3
-- (grp values: 1-1=0, 2-2=0, 3-3=0, 7-4=3, 8-5=3, 10-6=4, 15-7=8, 16-8=8, 17-9=8)

-- ============================================
-- GAPS: missing ranges
-- ============================================
SELECT InvoiceNo + 1 AS GapStart,
       NextNo - 1    AS GapEnd
FROM (
  SELECT InvoiceNo,
         LEAD(InvoiceNo) OVER (ORDER BY InvoiceNo) AS NextNo
  FROM Invoices
) AS x
WHERE NextNo - InvoiceNo > 1
ORDER BY GapStart;

-- EXPECTED OUTPUT (derived on SQLite):
-- GapStart | GapEnd
-- 4        | 6
-- 9        | 9
-- 11       | 14

-- Results derived from equivalent queries on SQLite; not executed on SQL Server.
-- LEAD needs SQL Server 2012+. Gaps before the first or after the last number are not reported.
```

---

## 🔍 Why This Works (3 lines max)
In a perfectly consecutive run both the value and the row number go up by 1, so their difference stays the same; when a gap appears the value jumps but the row number does not, so the difference changes and a new group starts. LEAD looks at the next value in sorted order, and a difference above 1 means numbers are missing in between.
हिंदी: लगातार run में value और row number दोनों +1 बढ़ते हैं, इसलिए फर्क same रहता है। Gap आते ही फर्क बदल जाता है = नया group।

---

## ⚡ Alternative Solution

```sql
-- Same idea for DATES (T-SQL): subtract the row number in days to get a constant anchor date.
SELECT MIN(LoginDate) AS StartDate, MAX(LoginDate) AS EndDate, COUNT(*) AS Days
FROM (
  SELECT LoginDate,
         DATEADD(DAY, -ROW_NUMBER() OVER (ORDER BY LoginDate), LoginDate) AS grp
  FROM (SELECT DISTINCT LoginDate FROM Logins) AS d
) AS x
GROUP BY grp;

-- Gaps without LEAD (pre-2012 style): anti-join on n + 1
SELECT i.InvoiceNo + 1 AS GapStart
FROM Invoices AS i
WHERE NOT EXISTS (SELECT 1 FROM Invoices AS n WHERE n.InvoiceNo = i.InvoiceNo + 1)
  AND i.InvoiceNo < (SELECT MAX(InvoiceNo) FROM Invoices);
-- (Returns only the first missing number of each gap: 4, 9, 11.)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: duplicates in the source
-- If InvoiceNo (or LoginDate) can repeat, ROW_NUMBER keeps increasing while the value does not,
-- which breaks the islands. ✅ Deduplicate first (SELECT DISTINCT) or use DENSE_RANK.

-- ❌ Wrong: ORDER BY in ROW_NUMBER different from the column you subtract
-- grp is only constant if the sort column and the subtracted column are the same.

-- ❌ Wrong: forgetting the PARTITION BY when there are several entities (per customer, per user)
-- ✅ ROW_NUMBER() OVER (PARTITION BY UserId ORDER BY LoginDate) and GROUP BY UserId, grp.

-- ❌ Wrong: using a numbers/tally table cross join for millions of rows
-- It works for small ranges but window functions scan once and scale far better.
```

---

## 🎯 Interview Tip (1 line)
Say: "For islands I use the value-minus-ROW_NUMBER trick and group on the difference; for gaps I use LEAD and compare with the next value. I mention de-duplication and the PARTITION BY version for per-user streaks — that is the same pattern as the consecutive-login question."

---

## 🔗 Related Questions
→ Q055 (consecutive login days) | Q057 (LAG and LEAD) | Q056 (ROW_NUMBER, RANK, DENSE_RANK) | Q054 (date-range overlap)
