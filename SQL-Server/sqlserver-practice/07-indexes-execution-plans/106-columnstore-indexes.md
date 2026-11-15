---

# Q106. Columnstore Indexes
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server 2012+ (updatable clustered columnstore from 2014); PostgreSQL/MySQL need extensions or a separate warehouse

---

## ❓ Question
A reporting query sums `Amount` by month across 200 million `Sales` rows. A rowstore B-tree is slow. Explain columnstore, create a clustered columnstore index (CCI), add a non-clustered columnstore index (NCCI) on an OLTP table for analytics, and say when NOT to use it.

---

## 💡 Quick Concept (2 lines only)
Columnstore stores each column separately in compressed segments (about a million rows per rowgroup), so analytic scans read only the needed columns and use batch-mode processing. Updates go to a delta store (a small B-tree) until a background tuple mover compresses them.
हिंदी: Columnstore में data column-wise compress होकर रखा जाता है, इसलिए aggregate/scan queries बहुत तेज़ होती हैं। Point lookups और बार-बार updates के लिए यह सही नहीं।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available); columnstore has no equivalent engine here.
-- No timings or plan output are shown on purpose; behaviour per Microsoft docs.
-- Expected aggregate result below was derived by hand from the sample rows.
-- ============================================
-- SETUP: fact table
-- ============================================
CREATE TABLE dbo.Sales (
  SaleId     BIGINT        NOT NULL,
  SaleDate   DATE          NOT NULL,
  ProductId  INT           NOT NULL,
  Quantity   INT           NOT NULL,
  Amount     DECIMAL(12,2) NOT NULL
);
INSERT INTO dbo.Sales VALUES
  (1,'2024-01-10',10,2,100.00),
  (2,'2024-01-22',20,1, 20.00),
  (3,'2024-02-03',10,1, 50.00),
  (4,'2024-02-14',30,1,200.00),
  (5,'2024-02-28',20,5,100.00);
GO

-- ============================================
-- 1) Clustered columnstore: the table itself becomes columnar (DW / fact tables)
-- ============================================
CREATE CLUSTERED COLUMNSTORE INDEX CCI_Sales ON dbo.Sales;
GO

SELECT YEAR(SaleDate) AS Yr, MONTH(SaleDate) AS Mo, SUM(Amount) AS Revenue, SUM(Quantity) AS Units
FROM dbo.Sales
GROUP BY YEAR(SaleDate), MONTH(SaleDate)
ORDER BY Yr, Mo;

-- Output (hand-computed from the 5 sample rows):
-- Yr   | Mo | Revenue | Units
-- 2024 | 1  | 120.00  | 3
-- 2024 | 2  | 350.00  | 7

-- ============================================
-- 2) Non-clustered columnstore on an OLTP rowstore table (real-time analytics)
-- ============================================
CREATE TABLE dbo.Orders (
  OrderId INT PRIMARY KEY CLUSTERED, CustomerId INT NOT NULL, OrderDate DATE NOT NULL, Amount DECIMAL(10,2) NOT NULL
);
CREATE NONCLUSTERED COLUMNSTORE INDEX NCCI_Orders_Analytics
  ON dbo.Orders (OrderDate, CustomerId, Amount);   -- only the columns analytics needs
GO

-- Inspect rowgroups (state_desc e.g. OPEN delta store / COMPRESSED):
SELECT object_id, partition_number, state_desc, total_rows, deleted_rows
FROM sys.dm_db_column_store_row_group_physical_stats
WHERE object_id = OBJECT_ID('dbo.Sales');
-- Values depend on your data volume; not shown here.
```

---

## 🔍 Why This Works (3 lines max)
A SUM over one column reads only that column's compressed segments and processes rows in batches of about 900 instead of one at a time. Segment metadata (min/max) lets the engine skip whole rowgroups (segment elimination), especially when data is loaded in date order. Row-level updates are expensive because deletes are marked in a bitmap and inserts land in a delta store first.
हिंदी: सिर्फ ज़रूरी column पढ़ी जाती है और compress होने से I/O कम होता है। Rowgroup skip (segment elimination) से और बचत होती है।

---

## ⚡ Alternative Solution

```sql
-- Small/medium tables or selective seeks: a covering rowstore index may be enough (Q103).
-- Bulk-load tip: load in batches of >= 102,400 rows so rows go straight to compressed rowgroups
-- (smaller batches land in delta stores).
INSERT INTO dbo.Sales WITH (TABLOCK)
SELECT SaleId, SaleDate, ProductId, Quantity, Amount FROM dbo.Sales_Staging;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: clustered columnstore on a hot OLTP table with frequent single-row UPDATEs and point lookups
SELECT * FROM dbo.Sales WHERE SaleId = 4;   -- point lookup: columnstore is not designed for this (add a NC rowstore index if needed)
-- ❌ Wrong: SELECT * on columnstore -> reads every column segment, losing the main benefit
-- ❌ Wrong: trickle inserts of a few rows -> many tiny delta rowgroups until the tuple mover/REORGANIZE compresses them
-- ❌ Wrong: ignoring edition/compat limits (columnstore availability and features vary by edition and version; verify for your target, e.g. Azure SQL tiers)
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "Columnstore is for analytical scans and aggregations over large tables: fact tables, event history, reporting off an OLTP schema with a non-clustered columnstore. I avoid it for point lookups and heavy row-level updates, load in large batches, and partition by date so old rowgroups can be switched out. I verify gains with SET STATISTICS IO/TIME and the actual plan showing Batch mode, never by assumption."

---

## 🔗 Related Questions
→ Q034 (Partitioned tables) | Q103 (Covering index) | Q150 (Partitioning for performance) | Q154 (Compression)
