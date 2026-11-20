---

# Q180. How Do You Optimize a Slow Query
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: EXPLAIN ANALYZE; PostgreSQL: EXPLAIN (ANALYZE, BUFFERS); the method is the same, the tools differ)

---

## ❓ Question
"This payments report took 2 seconds last month and takes 40 seconds now." Walk through how you diagnose and fix a slow query in SQL Server, with a concrete before/after.

---

## 💡 Quick Concept (2 lines only)
Measure first (duration, logical reads, actual plan), find the dominant cost (scan, key lookup, spill, bad estimate, blocking), fix the cause (SARGable predicate, right index, stats, query shape), then re-measure. Never guess or "add an index" blindly.
हिंदी: पहले measure करो (reads, plan), फिर सबसे महँगा हिस्सा ढूँढो, ठीक करो, दोबारा measure करो। अंदाज़े से index मत डालो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Payments (
  PaymentId  INT IDENTITY(1,1) PRIMARY KEY,
  CustomerId INT NOT NULL,
  PaidOn     DATE NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);
INSERT INTO dbo.Payments (CustomerId, PaidOn, Amount) VALUES
  (1, '2024-01-31', 10), (1, '2024-02-01', 20), (2, '2024-02-15', 30),
  (2, '2024-02-29', 40), (3, '2024-03-01', 50);

-- ============================================
-- STEP 1: MEASURE (numbers, not feelings)
-- ============================================
SET STATISTICS IO ON;
SET STATISTICS TIME ON;
-- Also capture the ACTUAL execution plan in SSMS / Azure Data Studio (Ctrl+M).

-- ============================================
-- STEP 2: SLOW VERSION - function on the column makes the predicate non-SARGable
-- ============================================
SELECT PaymentId, PaidOn
FROM dbo.Payments
WHERE YEAR(PaidOn) = 2024 AND MONTH(PaidOn) = 2;
-- The function is evaluated per row: an index on PaidOn cannot be used for a seek -> scan.

-- ============================================
-- STEP 3: FIX - half-open date range on the bare column + supporting index
-- ============================================
CREATE INDEX IX_Payments_PaidOn ON dbo.Payments (PaidOn) INCLUDE (CustomerId, Amount);

SELECT PaymentId, PaidOn
FROM dbo.Payments
WHERE PaidOn >= '2024-02-01' AND PaidOn < '2024-03-01'
ORDER BY PaymentId;

-- Both queries return the same rows (checked on SQLite 3 with equivalent data; not executed on SQL Server)
-- PaymentId | PaidOn
-- 2         | 2024-02-01
-- 3         | 2024-02-15
-- 4         | 2024-02-29
-- Plan/IO improvement (scan -> seek, fewer logical reads) is expected per docs but is NOT shown here:
-- no SQL Server instance was available, so no plan or read counts are claimed.

-- ============================================
-- STEP 4: CHECKLIST when the query is still slow
-- ============================================
-- 1. Scan vs seek, key lookups on many rows  -> covering index / INCLUDE (Q103)
-- 2. Estimated vs actual rows far apart      -> UPDATE STATISTICS, parameter sniffing (Q109, Q181)
-- 3. Implicit conversion (NVARCHAR vs VARCHAR param) -> match types (Q143)
-- 4. Sort/hash spill warnings                -> better index order, more memory grant fit
-- 5. SELECT * / too many columns             -> select only what you need (Q144)
-- 6. Waiting, not working (blocking)         -> sys.dm_exec_requests, wait stats (Q123, Q148)
-- 7. Chatty app (N+1 queries)                -> batch/join in one round trip (Q152)
-- 8. Last: scale up hardware or tier
```

---

## 🔍 Why This Works (3 lines max)
An index is sorted by the column value; once the column is wrapped in a function the engine cannot navigate the sort order and must compute the function for every row. A range on the bare column lets it seek straight to the month. Measuring logical reads before and after shows whether the fix actually helped.
हिंदी: Column पर function = index बेकार, पूरा scan। Bare column पर range = seek। Logical reads से सच पता चलता है।

---

## ⚡ Alternative Solution

```sql
-- Computed column + index when the function form is unavoidable:
ALTER TABLE dbo.Payments ADD PaidMonth AS (DATEFROMPARTS(YEAR(PaidOn), MONTH(PaidOn), 1));
CREATE INDEX IX_Payments_PaidMonth ON dbo.Payments (PaidMonth);
SELECT PaymentId FROM dbo.Payments WHERE PaidMonth = '2024-02-01';
-- Or Query Store: find the regressed plan and force the previous one (Q113).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: adding an index without reading the plan, or blindly applying every missing-index suggestion.
-- ❌ Wrong: WHERE CONVERT(VARCHAR(10), PaidOn, 120) LIKE '2024-02%'  (function + string compare)
-- ❌ Wrong: NOLOCK as a "performance fix": it hides blocking and can return wrong data (Q183).
-- ❌ Wrong: testing on 100 rows. Plans change with data volume and skew.
-- ❌ Wrong: BETWEEN '2024-02-01' AND '2024-02-29 23:59:59' on datetime: loses rows in the last
--    second (and is wrong in leap vs non-leap years). Use >= start AND < next-start.
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "My process is fixed: reproduce with production-like data, read actual plan plus STATISTICS IO, identify the one dominant cost, change one thing, compare reads and duration, and check Query Store after deployment to catch regressions. I also ask whether the query should exist at all: caching, pre-aggregation or fewer round trips often beat clever tuning." Mention index write cost and maintenance as the trade-off.

---

## 🔗 Related Questions
→ Q107 (reading an execution plan) | Q108 (SET STATISTICS IO and TIME) | Q110 (SARGable predicates) | Q142 (finding slow queries) | Q143 (avoiding implicit conversions)
