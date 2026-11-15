---

# Q107. Reading an Execution Plan (Scan vs Seek, Key Lookup)
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL uses EXPLAIN ANALYZE, MySQL EXPLAIN / EXPLAIN ANALYZE)

---

## ❓ Question
How do you capture and read an execution plan in SQL Server? Explain Index Scan vs Index Seek vs Key Lookup, what the thick arrows and the warning icons mean, and what the difference is between an estimated and an actual plan.

---

## 💡 Quick Concept (2 lines only)
A plan is a tree of operators read right-to-left, top-to-bottom (data flows from leaf operators toward SELECT). Compare estimated vs actual row counts: a big mismatch means bad statistics, and it explains most slow-query puzzles.
हिंदी: Plan को right से left पढ़ो, जहाँ से data शुरू होता है। Estimated और actual rows में बड़ा फर्क मतलब statistics खराब हैं।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available). No plan XML or operator costs are shown:
-- they depend on your data/version. Operator names below are from Microsoft docs.
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Orders (
  OrderId INT PRIMARY KEY CLUSTERED, CustomerId INT NOT NULL, OrderDate DATE NOT NULL,
  Status VARCHAR(20) NOT NULL, Amount DECIMAL(10,2) NOT NULL
);
CREATE NONCLUSTERED INDEX IX_Orders_Customer ON dbo.Orders (CustomerId);
GO

-- ============================================
-- HOW TO CAPTURE
-- ============================================
-- SSMS / Azure Data Studio: Ctrl+L = ESTIMATED plan (query is not run)
--                           Ctrl+M then run = ACTUAL plan (includes actual rows, executions, memory grants)

SET STATISTICS XML ON;     -- returns the actual plan as XML for the next statements
SELECT OrderId, CustomerId, Amount FROM dbo.Orders WHERE CustomerId = 101;
SET STATISTICS XML OFF;

-- ============================================
-- WHAT YOU EXPECT TO SEE for the query above (operator names only)
-- ============================================
-- SELECT
--   +-- Nested Loops (Inner Join)
--         +-- Index Seek (NonClustered)  IX_Orders_Customer   -- finds CustomerId = 101 via the B-tree
--         +-- Key Lookup (Clustered)     PK_Orders            -- fetches Amount (not in the index) once per matching row
--
-- Fix when the lookup count is high: widen the index with INCLUDE (Amount)  -> seek only (see Q103)

-- Table-wide predicate with no usable index:
SELECT OrderId FROM dbo.Orders WHERE Status = 'Pending';
-- Expected: Clustered Index Scan (reads every row/page; fine for small tables or very non-selective filters)

-- ============================================
-- CHEAT SHEET
-- ============================================
-- Seek  = B-tree navigation to a start point + range; good when the predicate is selective and SARGable
-- Scan  = read the whole index/table; not "bad" per se - bad when you needed few rows
-- Key Lookup = per-row jump into the clustered index; cost multiplies with row count (random reads)
-- Thick arrow = many rows flowing; check where the estimate was wrong
-- Yellow warning triangle = e.g. missing statistics, implicit conversion, spill to tempdb, no join predicate
-- Sort / Hash Match spills = memory grant too low (often a cardinality estimate problem)
```

---

## 🔍 Why This Works (3 lines max)
Each operator reports estimated vs actual rows and executions, so you can spot the first operator where the estimate diverges from reality. A seek plus many key lookups can cost more than a scan once the row count passes a tipping point, which is why the optimizer sometimes ignores your index. Fixing the root cause (statistics, SARGability, covering columns) beats forcing a hint.
हिंदी: पहला operator ढूँढो जहाँ estimated और actual rows बहुत अलग हों, वहीं असली समस्या है। Seek हमेशा अच्छा और scan हमेशा बुरा नहीं होता।

---

## ⚡ Alternative Solution

```sql
-- Text-ish output and cached plans:
SET SHOWPLAN_XML ON;   -- estimated plan only; must be the only statement in its batch
GO
SELECT OrderId FROM dbo.Orders WHERE CustomerId = 101;
GO
SET SHOWPLAN_XML OFF;
GO
-- Cached plans (needs VIEW SERVER STATE; on Azure SQL use VIEW DATABASE STATE):
SELECT TOP (5) st.text, qp.query_plan
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
CROSS APPLY sys.dm_exec_query_plan(qs.plan_handle) qp;
-- Query Store (Q113) keeps plan history persistently.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: trusting the "cost %" shown in an ESTIMATED plan as real time - it is a model; use the ACTUAL plan + SET STATISTICS IO/TIME
-- ❌ Wrong: "Scan = bad, Seek = good" - a scan of a 50-row table is perfect; a seek with 1M key lookups is not
-- ❌ Wrong: tuning on a dev DB with 100 rows - plans change with data volume and statistics
-- ❌ Wrong: ignoring the warning on a Nested Loops / Hash Match about implicit conversion (see Q143)
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "I capture the actual plan, find the operator with the biggest gap between estimated and actual rows, and then check statistics, parameter sniffing (Q114) and SARGability (Q110). I read lookups and spills as signals - key lookup means a missing INCLUDE column, spill means bad memory grant - and I confirm any fix with SET STATISTICS IO before and after."

---

## 🔗 Related Questions
→ Q103 (Covering index) | Q108 (SET STATISTICS IO and TIME) | Q109 (Statistics and cardinality) | Q113 (Query Store basics)
