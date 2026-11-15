---

# Q183. NOLOCK — Good or Bad?
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL/PostgreSQL have no NOLOCK; PostgreSQL MVCC readers never block, MySQL InnoDB uses consistent reads)

---

## ❓ Question
A reporting query on `Orders` is blocked by a long-running UPDATE, so a teammate adds `WITH (NOLOCK)` everywhere. Explain what NOLOCK really does, what anomalies it allows, and what you would use instead.

---

## 💡 Quick Concept (2 lines only)
`WITH (NOLOCK)` = `READ UNCOMMITTED` for that table: no shared locks taken, uncommitted (dirty) data is visible, and reads can skip or double-count rows during page splits. It is not a "faster, free" switch.
हिंदी: NOLOCK = dirty read, uncommitted data भी दिखता है। Rows skip या दो बार भी आ सकते हैं। Free performance नहीं है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Orders (
  OrderId    INT IDENTITY(1,1) PRIMARY KEY,
  CustomerId INT NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL,
  Status     VARCHAR(20) NOT NULL
);
INSERT INTO dbo.Orders (CustomerId, Amount, Status) VALUES
  (1, 100.00, 'Paid'), (2, 250.00, 'Paid'), (3, 75.00, 'Pending');
GO

-- ============================================
-- DEMO: dirty read (two sessions)
-- ============================================
-- SESSION 1
BEGIN TRANSACTION;
UPDATE dbo.Orders SET Amount = 999999.00 WHERE OrderId = 1;   -- not committed yet

-- SESSION 2 (default READ COMMITTED): waits for Session 1's exclusive lock (blocked)
SELECT SUM(Amount) FROM dbo.Orders;

-- SESSION 2 with NOLOCK: returns immediately, but sees 999999.00 (dirty read)
SELECT SUM(Amount) FROM dbo.Orders WITH (NOLOCK);

-- SESSION 1
ROLLBACK;   -- the 999999.00 value never officially existed, yet the report showed it

-- Expected behaviour (per Microsoft docs; not executed on SQL Server):
--   NOLOCK query -> SUM = 1000324.00 (999999 + 250 + 75) while Session 1 is open
--   After ROLLBACK, true SUM = 425.00

-- ============================================
-- BETTER FIX: row versioning (readers don't block writers)
-- ============================================
ALTER DATABASE CURRENT SET READ_COMMITTED_SNAPSHOT ON WITH ROLLBACK IMMEDIATE;
-- Now the plain SELECT reads the last committed version -> no blocking, no dirty reads
SELECT SUM(Amount) FROM dbo.Orders;     -- 425.00 even while Session 1 is open
```

Result values above are hand-computed (100+250+75 = 425; 999999+250+75 = 1000324). Not executed on SQL Server; behaviour per Microsoft docs.

---

## 🔍 Why This Works (3 lines max)
READ COMMITTED takes short shared locks, so it waits behind an uncommitted writer's exclusive lock. NOLOCK skips the shared lock, so there is nothing to wait for, but it also skips the guarantee that data is committed. RCSI keeps old row versions in tempdb (Azure SQL: in the database's version store) so readers get a consistent committed snapshot without blocking.
हिंदी: NOLOCK lock छोड़ देता है तो wait नहीं होता, पर committed होने की guarantee भी चली जाती है। RCSI पुराने version पढ़ता है, इसलिए safe है।

---

## ⚡ Alternative Solution

```sql
-- Option A: SNAPSHOT isolation for specific reporting sessions
ALTER DATABASE CURRENT SET ALLOW_SNAPSHOT_ISOLATION ON;
SET TRANSACTION ISOLATION LEVEL SNAPSHOT;
BEGIN TRANSACTION;
SELECT Status, COUNT(*) AS Cnt FROM dbo.Orders GROUP BY Status;
COMMIT;

-- Option B: READPAST for queue tables (skip locked rows, do not read dirty)
SELECT TOP (10) OrderId FROM dbo.Orders WITH (READPAST) WHERE Status = 'Pending';

-- Option C: fix the root cause - shorten the writer's transaction, add an index so the UPDATE locks fewer rows
```

Version note: both snapshot options are available from SQL Server 2005; Azure SQL Database has RCSI ON by default.

---

## ⚠️ Common Mistake

```sql
-- Wrong: NOLOCK for money / inventory / anything that drives a decision
SELECT SUM(Amount) FROM dbo.Orders WITH (NOLOCK);   -- may include rolled-back data

-- Wrong: believing NOLOCK only risks "slightly stale" data.
-- It can also return a row twice or miss a row entirely when a page split
-- happens mid-scan (allocation-order scans), and can fail with error on
-- data being moved/deleted while read.

-- Wrong: sprinkling NOLOCK on every table via a code-review "performance rule".
-- It hides the real problem (long transactions, missing indexes).
```

---

## 🎯 Interview Tip (1 line)
Say: "NOLOCK is READ UNCOMMITTED per table - dirty reads plus possible skipped or duplicated rows. I accept it only for rough, non-critical counts. For blocking I turn on READ_COMMITTED_SNAPSHOT (already default in Azure SQL Database), keep transactions short, and index the writers." Mention you know the trade-off: RCSI adds tempdb/version-store load and 14 bytes per row of versioning overhead.

---

## 🔗 Related Questions
→ Q119 (Isolation levels) | Q120 (RCSI) | Q121 (SNAPSHOT) | Q125 (Lock hints) | Q123 (Blocking vs deadlock)
