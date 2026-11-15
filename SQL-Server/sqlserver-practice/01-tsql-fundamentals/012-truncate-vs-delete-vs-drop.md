---

# Q012. TRUNCATE vs DELETE vs DROP
# Category: T-SQL Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (TRUNCATE is transactional/rollback-able in SQL Server; MySQL TRUNCATE auto-commits, PostgreSQL TRUNCATE is transactional)

---

## ❓ Question
Compare `DELETE`, `TRUNCATE TABLE` and `DROP TABLE` on an `AuditLog` table: logging, identity reset, WHERE support, triggers, foreign keys, locking and rollback. Show a safe way to empty a table that is referenced by a foreign key.

---

## 💡 Quick Concept (2 lines only)
`DELETE` removes rows one by one (fully logged, fires triggers, supports WHERE, keeps IDENTITY counter); `TRUNCATE` deallocates pages (minimal logging, no WHERE, resets IDENTITY to the seed, no DELETE triggers); `DROP` removes the table itself.
हिंदी: DELETE = row-by-row + WHERE, TRUNCATE = पूरी table जल्दी खाली + identity reset, DROP = table ही खत्म।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.AuditLog (
  LogId     INT IDENTITY(1,1) PRIMARY KEY,
  Message   NVARCHAR(200) NOT NULL,
  CreatedAt DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME()
);

INSERT INTO dbo.AuditLog (Message) VALUES (N'a'), (N'b'), (N'c');   -- LogId 1,2,3

-- ============================================
-- 1. DELETE: identity keeps counting
-- ============================================

DELETE FROM dbo.AuditLog;                             -- removes 3 rows, fully logged
INSERT INTO dbo.AuditLog (Message) VALUES (N'd');
SELECT LogId, Message FROM dbo.AuditLog;              -- LogId = 4  | d

-- ============================================
-- 2. TRUNCATE: identity resets to the seed (1)
-- ============================================

TRUNCATE TABLE dbo.AuditLog;
INSERT INTO dbo.AuditLog (Message) VALUES (N'e');
SELECT LogId, Message FROM dbo.AuditLog;              -- LogId = 1  | e

-- ============================================
-- 3. TRUNCATE inside a transaction can be rolled back (SQL Server)
-- ============================================

BEGIN TRANSACTION;
  TRUNCATE TABLE dbo.AuditLog;
  SELECT COUNT(*) AS RowsInside FROM dbo.AuditLog;    -- 0
ROLLBACK TRANSACTION;
SELECT COUNT(*) AS RowsAfterRollback FROM dbo.AuditLog;  -- 1

-- ============================================
-- 4. DROP: the table is gone
-- ============================================

DROP TABLE IF EXISTS dbo.AuditLog;                    -- IF EXISTS: SQL Server 2016+

-- Summary
-- Feature        | DELETE        | TRUNCATE            | DROP
-- WHERE clause   | yes           | no                  | no
-- Logging        | full, per row | page deallocations  | metadata
-- Identity       | keeps counter | reset to seed       | gone
-- Triggers       | DELETE fires  | not fired           | n/a
-- Referenced FK  | allowed       | blocked             | blocked
-- Permission     | DELETE        | ALTER on table      | ALTER on schema

-- Note: the DELETE identity-continues behaviour was verified on SQLite (AUTOINCREMENT
-- gave LogId 4 after DELETE; SQLite has no TRUNCATE). The TRUNCATE reset, rollback and the
-- summary table follow Microsoft docs; not executed on SQL Server.
```

---

## 🔍 Why This Works (3 lines max)
DELETE logs every row so it can be rolled back and fires triggers, but is slow and can escalate locks on big tables. TRUNCATE logs only page deallocation, takes a schema-modification lock and resets the identity seed, which makes it fast but unavailable when a foreign key references the table.
हिंदी: Big table खाली करनी हो तो TRUNCATE तेज़ है, पर FK reference हो तो पहले constraint हटाओ।

---

## ⚡ Alternative Solution

```sql
-- Table referenced by a foreign key: TRUNCATE fails. Options:
-- (a) delete in batches (keeps the log small, lets log backups/AG keep up)
WHILE 1 = 1
BEGIN
  DELETE TOP (5000) FROM dbo.Orders WHERE CreatedAt < '2023-01-01';
  IF @@ROWCOUNT = 0 BREAK;
END;

-- (b) drop FK -> TRUNCATE -> re-create FK (needs a maintenance window)
-- (c) reseed manually after DELETE:
DBCC CHECKIDENT ('dbo.AuditLog', RESEED, 0);

-- Partitioned tables (2016+): TRUNCATE TABLE ... WITH (PARTITIONS (1, 2))
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "TRUNCATE cannot be rolled back" (that is Oracle/MySQL; in SQL Server it can inside a transaction)

-- ❌ Wrong: TRUNCATE a table referenced by a FK, even if the child table is empty
TRUNCATE TABLE dbo.Customers;   -- error: cannot truncate a table referenced by a FOREIGN KEY constraint

-- ❌ Wrong: expecting DELETE triggers (audit) to fire on TRUNCATE -> they do not.

-- ❌ Wrong: one giant DELETE of 50M rows -> lock escalation, huge transaction log, blocking.
-- ✅ Batch it, or use partition switching / TRUNCATE for purge jobs.

-- ❌ Wrong: DROP TABLE in a deploy script without checking dependents (views, procs, FKs).
```

---

## 🎯 Interview Tip (1 line)
Say: "DELETE is DML with a WHERE and triggers, TRUNCATE is a minimally-logged DDL-like operation that resets identity and is still transactional in SQL Server, DROP removes the object. For purges I batch DELETE with TOP and a short delay, or partition-switch/TRUNCATE when the table design allows."

---

## 🔗 Related Questions
→ Q174 (DELETE vs TRUNCATE vs DROP) | Q145 (Batching large updates/deletes) | Q013 (IDENTITY) | Q026 (PRIMARY KEY, UNIQUE, FOREIGN KEY) | Q131 (Transaction log and recovery models)
