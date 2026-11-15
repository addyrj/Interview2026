---

# Q154. Compression — Row and Page
# Category: Performance Tuning
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: InnoDB page compression | PostgreSQL: TOAST/LZ4). Not executed on SQL Server; behaviour per Microsoft docs. Savings are data dependent.

---

## ❓ Question
A 500 GB `OrderEvents` table is I/O-bound and memory-starved. Estimate and apply ROW or PAGE compression, and explain the trade-offs.

---

## 💡 Quick Concept (2 lines only)
ROW compression stores fixed-length types in variable-length form (cheap CPU, modest saving). PAGE compression adds prefix and dictionary compression on each page (higher saving, more CPU). Data stays compressed in the buffer pool, so more fits in memory.
हिंदी: ROW = हल्का, PAGE = ज़्यादा बचत पर ज़्यादा CPU। Compressed data memory में भी compressed रहता है, इसलिए IO कम।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE OrderEvents (
  EventId    BIGINT IDENTITY(1,1) PRIMARY KEY,
  OrderId    INT           NOT NULL,
  EventType  VARCHAR(30)   NOT NULL,
  Payload    NVARCHAR(500) NULL,
  CreatedAt  DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);

-- ============================================
-- 1) Estimate first (not executed on SQL Server; behaviour per Microsoft docs)
-- ============================================
EXEC sp_estimate_data_compression_savings
     @schema_name = 'dbo', @object_name = 'OrderEvents',
     @index_id = NULL, @partition_number = NULL, @data_compression = 'PAGE';
-- returns size_with_current_compression_setting(KB) and size_with_requested_compression_setting(KB)

-- 2) Apply (rebuild; offline unless ONLINE = ON - Enterprise/Azure; takes locks and log space)
ALTER TABLE dbo.OrderEvents REBUILD WITH (DATA_COMPRESSION = PAGE, ONLINE = ON);
ALTER INDEX ALL ON dbo.OrderEvents REBUILD WITH (DATA_COMPRESSION = ROW);

-- 3) Check current setting
SELECT OBJECT_NAME(p.object_id) AS table_name, p.index_id, p.data_compression_desc
FROM sys.partitions p
WHERE p.object_id = OBJECT_ID(N'dbo.OrderEvents');

-- EXPECTED OUTPUT (shape; not executed on SQL Server, ratios depend on your data):
-- table_name  | index_id | data_compression_desc
-- OrderEvents | 1        | PAGE
```

---

## 🔍 Why This Works (3 lines max)
Fewer pages mean fewer reads and a larger effective buffer pool; the cost is CPU on read/write to compress and decompress. Low-cardinality, repetitive, read-mostly data benefits most; already-compact or random data (GUIDs, encrypted blobs) benefits little.
हिंदी: कम pages = कम IO। Repetitive read-heavy data में फ़ायदा ज़्यादा, random data में कम।

---

## ⚡ Alternative Solution

```sql
-- Columnstore (Q106) compresses far more for analytics tables (and archive compression):
CREATE CLUSTERED COLUMNSTORE INDEX CCI_OrderEvents ON dbo.OrderEvents;   -- replaces the rowstore clustered index
-- COMPRESS()/DECOMPRESS() (2016+) gzip individual large values (e.g. Payload) as VARBINARY(MAX).
-- Availability: all editions since SQL Server 2016 SP1; Azure SQL supports it.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Applying PAGE to a write-heavy hot table without testing CPU headroom
-- ❌ Skipping the estimate: LOB / off-row and GUID-heavy tables can shrink very little
-- ❌ Rebuilding a huge table in peak hours: log growth, locks, replication/AG lag
-- ❌ Forgetting that new indexes default to NONE: set DATA_COMPRESSION per index/partition
-- ❌ Assuming VARCHAR(MAX) / out-of-row data gets ROW/PAGE compressed (it generally does not)
```

---

## 🎯 Interview Tip (1 line)
Say: "I run sp_estimate_data_compression_savings, start with PAGE on cold/read-heavy partitions and ROW on hot ones, rebuild ONLINE off-peak with log space planned, and re-measure I/O and CPU. Columnstore for analytic tables."

---

## 🔗 Related Questions
→ Q106 (Columnstore indexes) | Q150 (Partitioning for performance) | Q111 (Index fragmentation) | Q034 (Partitioned tables basics)
