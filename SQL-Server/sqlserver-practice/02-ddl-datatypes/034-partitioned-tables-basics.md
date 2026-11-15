---

# Q034. Partitioned Tables Basics
# Category: DDL + Data Types
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (Enterprise-grade feature historically; table partitioning is available in all editions from SQL Server 2016 SP1 and in Azure SQL). MySQL = PARTITION BY RANGE in DDL; PostgreSQL = declarative partitioning.

---

## ❓ Question
Partition a large `Orders` table by year of `OrderDate` so old data can be archived by switching a partition out instead of running a huge DELETE. Show the partition function, scheme, table, how to find which partition a row lands in, and the SWITCH idea.

---

## 💡 Quick Concept (2 lines only)
Partition function = boundary values; partition scheme = maps partitions to filegroups; the table (or index) is created ON the scheme with a partitioning column. Queries filtering on that column can skip partitions (elimination), and SWITCH moves a whole partition as a metadata-only operation.
हिंदी: Function = सीमाएँ, Scheme = filegroup mapping, Table scheme पर बनती है। पुराना partition SWITCH करके instantly archive हो जाता है, DELETE नहीं।

---

## ✅ Answer / Solution

```sql
-- NOT EXECUTED ON SQL SERVER: no equivalent engine for partition DDL here.
-- The partition-number results were verified with an equivalent CASE expression on SQLite
-- (RANGE RIGHT semantics). Everything else follows Microsoft docs.

-- ============================================
-- SETUP
-- ============================================
-- 1) Boundaries. RANGE RIGHT: each boundary value belongs to the partition on its RIGHT,
--    so '2024-01-01' starts partition 2.
CREATE PARTITION FUNCTION pf_OrderYear (DATE)
AS RANGE RIGHT FOR VALUES ('2024-01-01', '2025-01-01');

-- 2) Map partitions to filegroups (all to PRIMARY here for simplicity; 3 partitions need 3 entries or ALL TO)
CREATE PARTITION SCHEME ps_OrderYear
AS PARTITION pf_OrderYear ALL TO ([PRIMARY]);

-- 3) Table on the scheme. The partitioning column must be part of the clustered key
--    (and any unique index) to keep those indexes aligned.
CREATE TABLE dbo.Orders (
    OrderId    BIGINT        NOT NULL,
    OrderDate  DATE          NOT NULL,
    CustomerId INT           NOT NULL,
    Amount     DECIMAL(10,2) NOT NULL,
    CONSTRAINT PK_Orders PRIMARY KEY CLUSTERED (OrderDate, OrderId)
) ON ps_OrderYear (OrderDate);

INSERT INTO dbo.Orders (OrderId, OrderDate, CustomerId, Amount) VALUES
  (1, '2023-06-15', 10, 100.00),
  (2, '2024-01-01', 11, 200.00),
  (3, '2024-12-31', 12, 300.00),
  (4, '2025-03-01', 13, 400.00);

-- ============================================
-- SOLUTION: where did each row land?
-- ============================================
SELECT OrderId, OrderDate, $PARTITION.pf_OrderYear(OrderDate) AS PartitionNo
FROM dbo.Orders
ORDER BY OrderId;

-- Rows per partition (catalog view)
SELECT partition_number, rows
FROM sys.partitions
WHERE object_id = OBJECT_ID('dbo.Orders') AND index_id = 1;

-- Archive: switch partition 1 into an identical, empty table on the same filegroup (metadata only)
-- ALTER TABLE dbo.Orders SWITCH PARTITION 1 TO dbo.Orders_Archive;

-- ============================================
-- EXPECTED OUTPUT (partition numbers derived from CASE equivalent on SQLite; not executed on SQL Server)
-- ============================================
-- OrderId | OrderDate  | PartitionNo
-- 1       | 2023-06-15 | 1
-- 2       | 2024-01-01 | 2     (RANGE RIGHT: boundary belongs to the right partition)
-- 3       | 2024-12-31 | 2
-- 4       | 2025-03-01 | 3
```

---

## 🔍 Why This Works (3 lines max)
N boundary values create N+1 partitions; RANGE RIGHT puts each boundary in the partition to its right, RANGE LEFT to its left. A WHERE on OrderDate lets the optimizer eliminate partitions it does not need. SWITCH reassigns metadata pages instead of copying rows, so archiving millions of rows takes about as long as a catalog change (target must be empty, identical structure, same filegroup, with a matching CHECK constraint).
हिंदी: N boundaries = N+1 partitions। RANGE RIGHT में boundary value दाहिने partition में जाती है। SWITCH सिर्फ metadata बदलता है, इसलिए बहुत तेज़।

---

## ⚡ Alternative Solution

```sql
-- Sliding window maintenance: add a new boundary, merge the oldest
ALTER PARTITION SCHEME ps_OrderYear NEXT USED [PRIMARY];
ALTER PARTITION FUNCTION pf_OrderYear() SPLIT RANGE ('2026-01-01');
ALTER PARTITION FUNCTION pf_OrderYear() MERGE RANGE ('2024-01-01');   -- only after the data was switched out

-- Simpler alternative without partitioning: batched deletes (Q145) or a separate archive table + job.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Believing partitioning automatically makes every query faster
--    Without a predicate on OrderDate, the query scans all partitions; it is a manageability feature first.

-- ❌ Primary key on OrderId alone: the partitioning column must be in unique/clustered keys
CREATE TABLE dbo.Orders2 (OrderId BIGINT PRIMARY KEY, OrderDate DATE NOT NULL) ON ps_OrderYear (OrderDate);
-- Fails/unaligned: PK does not include OrderDate; uniqueness is only per-partition.

-- ❌ SPLIT on a populated partition scans and moves data: split an empty future boundary.
-- ❌ Wrong boundary side (LEFT vs RIGHT) puts '2024-01-01' rows in the 2023 partition.
```

---

## 🎯 Interview Tip (1 line)
Say: "I partition for data lifecycle first — sliding-window archive with SWITCH — and treat query speedup as a bonus via partition elimination. I use RANGE RIGHT with date boundaries, include the partition column in the clustered key, and keep indexes aligned." Also say that in Azure SQL Database you only have filegroup PRIMARY, so partitioning there is mostly for SWITCH/maintenance.

---

## 🔗 Related Questions
→ Q026 (PRIMARY/UNIQUE/FOREIGN KEY) | Q102 (Clustered vs non-clustered index) | Q145 (Batching large updates/deletes) | Q150 (Partitioning for performance)
