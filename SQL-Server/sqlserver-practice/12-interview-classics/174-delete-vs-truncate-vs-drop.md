---

# Q174. DELETE vs TRUNCATE vs DROP
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: TRUNCATE auto-commits, cannot roll back; PostgreSQL: TRUNCATE is transactional like SQL Server)

---

## ❓ Question
Compare DELETE, TRUNCATE and DROP for an Orders table: logging, rollback, identity reset, WHERE support, triggers, foreign key behaviour, and permissions. Show each statement and a rollback demo.

---

## 💡 Quick Concept (2 lines only)
DELETE removes rows (DML, optional WHERE, fires triggers, row-by-row logged). TRUNCATE empties the whole table fast (minimal logging, resets IDENTITY, no WHERE). DROP removes the table itself.
हिंदी: DELETE = rows हटाओ (WHERE चलता है)। TRUNCATE = पूरी table खाली, तेज़, identity reset। DROP = table ही गायब।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Orders (
    OrderId    INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId INT,
    Status     VARCHAR(20),
    Amount     DECIMAL(10,2)
);

INSERT INTO Orders (CustomerId, Status, Amount) VALUES
  (101, 'Shipped',   500),
  (101, 'Cancelled', 200),
  (102, 'Shipped',   150),
  (102, 'Shipped',   900),
  (103, 'Pending',   300),
  (103, 'Shipped',    50),
  (104, 'Cancelled', 700),
  (101, 'Shipped',   100);

-- ============================================
-- DELETE: selective, logged per row, fires triggers, identity NOT reset
-- ============================================

DELETE FROM Orders WHERE Status = 'Cancelled';
SELECT @@ROWCOUNT AS RowsDeleted;           -- immediately after the DELETE it would show 2
SELECT COUNT(*) AS Remaining FROM Orders;

-- EXPECTED OUTPUT (row counts derived from equivalent DELETE on SQLite; not executed on SQL Server).
-- Note: the SELECT @@ROWCOUNT above runs after the DELETE, so run them in that order.
-- RowsDeleted = 2
-- Remaining   = 6

-- ============================================
-- TRUNCATE: whole table, minimal logging, resets IDENTITY, no WHERE, no triggers
-- ============================================

BEGIN TRANSACTION;
    TRUNCATE TABLE Orders;
    SELECT COUNT(*) AS InsideTran FROM Orders;   -- 0
ROLLBACK TRANSACTION;                            -- TRUNCATE is transactional in SQL Server
SELECT COUNT(*) AS AfterRollback FROM Orders;    -- 6 (data is back)
-- Rollback behaviour per Microsoft docs (not executed here); MySQL would NOT roll this back.

TRUNCATE TABLE Orders;                           -- now for real
INSERT INTO Orders (CustomerId, Status, Amount) VALUES (105, 'Pending', 10);
SELECT OrderId FROM Orders;                      -- 1  (IDENTITY reseeded to its seed value)
-- After DELETE (not TRUNCATE) the next IDENTITY value would continue, not restart.

-- ============================================
-- DROP: object removed: data, indexes, constraints, permissions
-- ============================================

DROP TABLE Orders;
DROP TABLE IF EXISTS Orders;                     -- IF EXISTS: SQL Server 2016+
```

```text
Comparison (per Microsoft docs; not executed here)
                 DELETE            TRUNCATE                     DROP
Type             DML               DDL                          DDL
WHERE            yes               no                           n/a
Logging          every row         page deallocations (minimal) metadata
Rollback         yes               yes (inside a transaction)   yes (inside a transaction)
Identity         keeps counter     resets to seed               table gone
Triggers         DELETE triggers   do not fire                  n/a
FK referenced    allowed (checks)  BLOCKED if table is referenced by an FK (even if child empty)
Permission       DELETE            ALTER on table               ALTER on schema / CONTROL
Locks            row/page/table    schema-modify (Sch-M) table  Sch-M
```

---

## 🔍 Why This Works (3 lines max)
DELETE has to find, lock, log and fire triggers per row, which is why it is slow on millions of rows but flexible. TRUNCATE deallocates data pages instead, so it is fast and resets IDENTITY, but it needs table-level ALTER rights and refuses when foreign keys reference the table. DROP changes metadata, so everything attached to the table vanishes.
हिंदी: DELETE row-by-row (धीमा, flexible)। TRUNCATE pages deallocate (तेज़, FK होने पर block)। DROP पूरी object हटाता है।

---

## ⚡ Alternative Solution

```sql
-- Delete most of a big table safely: batch it (keeps log small, limits blocking)
DECLARE @Rows INT = 1;
WHILE @Rows > 0
BEGIN
    DELETE TOP (5000) FROM Orders WHERE Status = 'Cancelled';
    SET @Rows = @@ROWCOUNT;
END;

-- Or keep a few rows: copy keepers out, TRUNCATE, copy back (needs FKs dropped/disabled)
-- Or use partition switching / SWITCH OUT for archival (Q034, Q150)
```

---

## ⚠️ Common Mistake

```sql
-- Wrong: DELETE FROM Orders;  with no WHERE on prod (and no transaction / backup check)
-- Safer habit:
BEGIN TRANSACTION;
    DELETE FROM Orders WHERE Status = 'Cancelled';
    SELECT @@ROWCOUNT AS Affected;                 -- verify expected count
-- COMMIT TRANSACTION;   or  ROLLBACK TRANSACTION;

-- Wrong: "TRUNCATE cannot be rolled back" (true in MySQL / Oracle; false in SQL Server and PostgreSQL)
-- Wrong: expecting TRUNCATE to work on a table referenced by a foreign key
--        (it errors; drop the FK, or DELETE + DBCC CHECKIDENT RESEED)
-- Wrong: expecting DELETE triggers (audit) to capture TRUNCATE - they do not fire
```

---

## 🎯 Interview Tip (1 line)
Say: "DELETE is for selective, trigger-aware, row-logged removal; TRUNCATE is the fast reset that needs table-level permission, resets identity and is blocked by FK references; DROP removes the object. Unlike MySQL, TRUNCATE in SQL Server can be rolled back inside a transaction. For large deletes I batch with DELETE TOP (N) in a loop to avoid log growth and blocking."

---

## 🔗 Related Questions
→ Q012 (TRUNCATE vs DELETE vs DROP) | Q010 (OUTPUT clause) | Q013 (IDENTITY) | Q145 (batching large deletes) | Q034 (partitioned tables) | Q098 (triggers)
