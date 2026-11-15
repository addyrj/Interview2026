---

# Q155. In-Memory OLTP Concepts
# Category: PERFORMANCE TUNING
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (2014+; MySQL has MEMORY engine, PostgreSQL has UNLOGGED tables — neither is equivalent: In-Memory OLTP is fully transactional and can be durable)

---

## ❓ Question
A `SessionState` table has heavy concurrent inserts/updates and suffers latch/lock contention. Explain In-Memory OLTP (memory-optimized tables), show how to create one, and say when you would NOT use it.

---

## 💡 Quick Concept (2 lines only)
Memory-optimized tables live in RAM with lock-free/latch-free row versioning (optimistic MVCC) and hash/range indexes; `SCHEMA_AND_DATA` is durable (logged), `SCHEMA_ONLY` loses data on restart. Natively compiled procedures turn T-SQL into machine code for the hottest paths.
हिंदी: In-Memory OLTP = RAM में table, बिना locks/latches के (optimistic versioning)। SCHEMA_ONLY तेज़ है पर restart पर data जाता है; hot paths के लिए natively compiled proc।

---

## ✅ Answer / Solution

NOTE: not executed on SQL Server; behaviour per Microsoft docs. No equivalent engine exists here, so no result sets are shown.

```sql
-- ============================================
-- SETUP (one-time, on-prem / VM; needs a MEMORY_OPTIMIZED_DATA filegroup)
-- ============================================
ALTER DATABASE ShopDb ADD FILEGROUP ShopDb_mod CONTAINS MEMORY_OPTIMIZED_DATA;
ALTER DATABASE ShopDb ADD FILE (NAME = 'ShopDb_mod1', FILENAME = 'D:\Data\ShopDb_mod1')
  TO FILEGROUP ShopDb_mod;
GO
-- (Azure SQL Database: no filegroup step; feature is tier-dependent -> verify your tier in docs)

-- ============================================
-- MEMORY-OPTIMIZED TABLE
-- ============================================
CREATE TABLE dbo.SessionState (
  SessionId   INT IDENTITY(1,1) NOT NULL
              PRIMARY KEY NONCLUSTERED HASH WITH (BUCKET_COUNT = 1048576),
  UserId      INT           NOT NULL,
  Payload     NVARCHAR(2000) NULL,
  LastTouched DATETIME2     NOT NULL
)
WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA);
GO

-- ============================================
-- NATIVELY COMPILED PROCEDURE
-- ============================================
CREATE PROCEDURE dbo.usp_TouchSession @SessionId INT
WITH NATIVE_COMPILATION, SCHEMABINDING
AS
BEGIN ATOMIC WITH (TRANSACTION ISOLATION LEVEL = SNAPSHOT, LANGUAGE = N'us_english')
  UPDATE dbo.SessionState SET LastTouched = SYSUTCDATETIME() WHERE SessionId = @SessionId;
END;
GO

-- Interpreted T-SQL can query it normally:
SELECT TOP (10) SessionId, UserId FROM dbo.SessionState ORDER BY LastTouched DESC;

-- Memory use check (DMV; columns per docs, verify on your build):
-- SELECT * FROM sys.dm_db_xtp_table_memory_stats;
```

---

## 🔍 Why This Works (3 lines max)
Rows are versioned instead of locked, so writers do not block readers and there are no page latches; indexes are never logged, only data. Hash index = point lookups (BUCKET_COUNT near the expected distinct key count), range (NONCLUSTERED) index = scans/ORDER BY.
हिंदी: Locks की जगह row versions → readers/writers block नहीं होते। Hash index = equality lookup; range index = range scan। BUCKET_COUNT गलत हुआ तो chains लंबी होंगी।

---

## ⚡ Alternative Solution

```sql
-- Cheaper first step: memory-optimized TABLE TYPE instead of #temp/@table variable
CREATE TYPE dbo.OrderIdList AS TABLE (
  OrderId INT NOT NULL PRIMARY KEY NONCLUSTERED HASH WITH (BUCKET_COUNT = 1024)
) WITH (MEMORY_OPTIMIZED = ON);

-- Or fix the real cause first: last-page insert contention -> OPTIMIZE_FOR_SEQUENTIAL_KEY (2019+)
CREATE CLUSTERED INDEX CIX_Sessions ON dbo.DiskSessions (SessionId)
  WITH (OPTIMIZE_FOR_SEQUENTIAL_KEY = ON);
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming it is "just faster" and migrating everything
--    Limits: data must fit in RAM; some T-SQL/features unsupported in native procs;
--    FKs/triggers/ALTER restrictions vary by version; recovery reloads all data into memory (slow startup).
-- ❌ Wrong: BUCKET_COUNT too small -> long hash chains; too large -> wasted RAM
-- ❌ Wrong: SCHEMA_ONLY for data you cannot lose (it vanishes on restart/failover)
-- ✅ Right: benchmark a contended hot table (sessions, queues, staging), keep durable tables on disk
```

---

## 🎯 Interview Tip (1 line)
Say: "In-Memory OLTP fits high-concurrency, short transactions with contention — session state, ingest/staging, queues — and I confirm the bottleneck (latch waits via wait stats) first; it costs RAM, has feature limits, and needs retry logic for validation/conflict errors under snapshot isolation, so I pilot it on one table rather than migrate the schema."

---

## 🔗 Related Questions
→ Q148 (Wait stats basics) | Q149 (tempdb contention) | Q146 (Table variables vs temp tables) | Q121 (Snapshot isolation)
