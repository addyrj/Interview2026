---

# Q115. Index Hints and Query Hints (When to Avoid)
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: USE/FORCE INDEX; PostgreSQL has no hints without pg_hint_plan)

---

## ❓ Question
What table hints and query hints exist (`WITH (INDEX(...))`, `FORCESEEK`, `OPTION (HASH JOIN)`, `MAXDOP`, `RECOMPILE`), when are they legitimate, and why are they risky as a permanent fix?

---

## 💡 Quick Concept (2 lines only)
Hints override the optimizer's choices (index, join type, parallelism). They freeze a decision that was right on today's data, and become wrong when data or schema changes — and a dropped hinted index makes the query fail.
हिंदी: Hint = optimizer को order देना। आज सही है, कल data बदला तो गलत। Hinted index drop हुआ तो query error देगी।

---

## ✅ Answer / Solution

NOTE: not executed on SQL Server; behaviour per Microsoft docs. Hints change plans, not results, so output is the same rows; no plan output is shown.

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
    OrderId     INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId  INT           NOT NULL,
    OrderDate   DATE          NOT NULL,
    Amount      DECIMAL(10,2) NOT NULL
);
CREATE INDEX IX_Orders_CustomerId ON dbo.Orders (CustomerId);
CREATE INDEX IX_Orders_OrderDate  ON dbo.Orders (OrderDate);
GO

-- ============================================
-- TABLE HINTS (per table, inside WITH)
-- ============================================

-- Force a specific index
SELECT OrderId, Amount
FROM dbo.Orders WITH (INDEX (IX_Orders_OrderDate))
WHERE OrderDate >= '2025-01-01';

-- Force a seek (fails with an error if a seek is impossible, e.g. non-SARGable predicate)
SELECT OrderId, Amount
FROM dbo.Orders WITH (FORCESEEK)
WHERE CustomerId = 42;

-- ============================================
-- QUERY HINTS (whole statement, inside OPTION)
-- ============================================

-- Join algorithm
SELECT o.OrderId, c.CustomerName
FROM dbo.Orders AS o
JOIN dbo.Customers AS c ON c.CustomerId = o.CustomerId
OPTION (HASH JOIN);

-- Limit parallelism for one heavy report so it does not starve OLTP
SELECT CustomerId, SUM(Amount) AS Total
FROM dbo.Orders
GROUP BY CustomerId
OPTION (MAXDOP 2);

-- Fresh plan for this execution (see Q114)
SELECT OrderId FROM dbo.Orders WHERE CustomerId = @CustomerId OPTION (RECOMPILE);

-- Fix the join order exactly as written
SELECT o.OrderId, c.CustomerName
FROM dbo.Customers AS c
JOIN dbo.Orders AS o ON o.CustomerId = c.CustomerId
OPTION (FORCE ORDER);

-- ============================================
-- LEGITIMATE USES
-- ============================================
-- * Emergency mitigation during an incident, with a ticket to remove it
-- * A known optimizer limitation you have proven (compare plans + STATISTICS IO, Q108)
-- * MAXDOP / RECOMPILE / OPTIMIZE FOR: workload-shaping hints, much less brittle than index hints
-- Better first: update statistics, fix a non-SARGable predicate (Q110), add a covering index (Q103),
-- or use Query Store plan forcing (Q113), which does not change the SQL text.
```

---

## 🔍 Why This Works (3 lines max)
The optimizer is cost-based and usually right because it sees statistics; a hint replaces its judgement with yours. That is fine when you have proof, but the hint stays after the data changes. Plan forcing in Query Store or fixing the root cause (stats, SARGability, indexing) is safer.
हिंदी: Optimizer statistics देखकर decide करता है, hint उसकी जगह तुम्हारा फैसला डालता है। Data बदलने पर hint पुराना पड़ जाता है। पहले root cause ठीक करो।

---

## ⚡ Alternative Solution

```sql
-- Instead of hardcoding the index in application SQL, force the plan from outside the query text:
EXEC sys.sp_query_store_force_plan @query_id = 42, @plan_id = 17;   -- see Q113

-- Or refresh statistics first - many "bad plan" problems disappear:
UPDATE STATISTICS dbo.Orders WITH FULLSCAN;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: hardcoding an index name in a query and then dropping/renaming the index
SELECT OrderId FROM dbo.Orders WITH (INDEX (IX_Orders_OldName)) WHERE CustomerId = 1;
-- The query fails at compile time because the index no longer exists (a production outage).

-- ❌ Wrong: WITH (INDEX(0)) / INDEX(1) used casually to force a scan / clustered scan.

-- ❌ Wrong: OPTION (HASH JOIN) applied to every query "to be safe" - it also forces join order
-- behaviour for the whole statement and can be slow for small inputs.

-- ✅ Right: leave a comment with why, the date, and the ticket; review hints after every major data change.
```

---

## 🎯 Interview Tip (1 line)
Say: "Hints are a last resort. I first check statistics, SARGability and indexing, and use Query Store plan forcing when I need to pin a plan without touching code. When I do use a hint, I prefer workload hints like MAXDOP or RECOMPILE over index or join hints, and I document it so it gets reviewed."

---

## 🔗 Related Questions
→ Q052 (join order and join hints) | Q107 (reading an execution plan) | Q110 (SARGable predicates) | Q113 (Query Store)
