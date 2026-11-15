---

# Q146. Table Variables vs Temp Tables for Performance
# Category: Performance Tuning
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL has only TEMPORARY tables | PostgreSQL has TEMP tables). Optimizer behaviour not executed on SQL Server; per Microsoft docs.

---

## ❓ Question
A procedure stages 200,000 pending-order rows, then joins them to other tables. With `@t` it is slow, with `#t` it is fast. Why? When is a table variable still the right choice?

---

## 💡 Quick Concept (2 lines only)
#temp tables live in tempdb, get column statistics and can have extra indexes, so estimates are good. Table variables have no column statistics (estimate was fixed at 1 row; since compat level 150 / SQL Server 2019 deferred compilation uses the real row count but still no column stats).
हिंदी: Large data पर #temp (stats मिलते हैं), बहुत छोटे data पर @table variable ठीक है। दोनों tempdb में ही बनते हैं, "memory में" वाला myth गलत है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL,
  Status     VARCHAR(20) NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);

INSERT INTO Orders VALUES
  (1,1,'Pending',10), (2,1,'Pending',20), (3,2,'Shipped',30), (4,1,'Pending',40),
  (5,3,'Pending',50), (6,1,'Pending',60), (7,2,'Shipped',70), (8,1,'Pending',80),
  (9,4,'Pending',90), (10,1,'Pending',100);

-- ============================================
-- Temp table: statistics + optional indexes
-- ============================================
CREATE TABLE #Pending (OrderId INT PRIMARY KEY, CustomerId INT NOT NULL, Amount DECIMAL(10,2));

INSERT INTO #Pending (OrderId, CustomerId, Amount)
SELECT OrderId, CustomerId, Amount FROM Orders WHERE Status = 'Pending';

CREATE INDEX IX_Pending_Customer ON #Pending (CustomerId);   -- allowed after creation

SELECT CustomerId, COUNT(*) AS PendingCount, SUM(Amount) AS PendingTotal
FROM #Pending
GROUP BY CustomerId
ORDER BY CustomerId;

-- EXPECTED OUTPUT (result derived from equivalent query on SQLite; not executed on SQL Server):
-- CustomerId | PendingCount | PendingTotal
-- 1          | 6            | 310.00
-- 3          | 1            | 50.00
-- 4          | 1            | 90.00

DROP TABLE #Pending;

-- ============================================
-- Table variable: fine for small sets (<~100 rows), no stats, no ALTER, no rollback of data
-- ============================================
DECLARE @Pending TABLE (OrderId INT PRIMARY KEY, CustomerId INT NOT NULL, Amount DECIMAL(10,2));
INSERT INTO @Pending SELECT OrderId, CustomerId, Amount FROM Orders WHERE Status = 'Pending';
SELECT COUNT(*) AS Cnt FROM @Pending;
-- Cnt = 8 (hand-checked: 8 Pending rows in the setup)
```

---

## 🔍 Why This Works (3 lines max)
With statistics the optimizer picks hash/merge joins and proper memory grants for big sets; without them it may choose nested loops that execute 200,000 times. Temp tables can also be indexed after creation and participate in parallel plans more reliably.
हिंदी: Stats नहीं तो optimizer को row count का सही अंदाज़ा नहीं -> खराब join plan।

---

## ⚡ Alternative Solution

```sql
-- OPTION (RECOMPILE) on a statement using @t lets the optimizer see the real row count
SELECT o.OrderId FROM Orders o JOIN @Pending p ON p.OrderId = o.OrderId OPTION (RECOMPILE);

-- Table-valued parameters (Q076) are table variables under the hood: read-only, no stats.
-- Memory-optimized table variables avoid tempdb (Q155, Q149).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ "Table variables are in memory, so they are faster": both use tempdb pages
-- ❌ Expecting ROLLBACK to undo table variable inserts: it does NOT (no transaction scope)
-- ❌ Staging 1M rows into @t and joining: nested-loop disaster
-- ❌ Creating #temp inside a loop/proc without dropping: recompiles and tempdb churn (Q149)
```

---

## 🎯 Interview Tip (1 line)
Say: "My default is #temp for anything beyond a few hundred rows or when I join/filter it, because of statistics and indexing. Table variables for tiny lists, TVP inputs, and to avoid recompiles. On 2019+ deferred compilation helps, but there are still no column statistics."

---

## 🔗 Related Questions
→ Q016 (Temp tables vs table variables vs CTEs) | Q179 (CTE vs temp table vs table variable) | Q149 (tempdb contention) | Q076 (Table-valued parameters)
