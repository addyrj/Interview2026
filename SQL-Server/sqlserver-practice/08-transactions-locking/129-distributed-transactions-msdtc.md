
---

# Q129. Distributed Transactions (MSDTC) Concepts
# Category: TRANSACTIONS + LOCKING
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (concept question; not executed on SQL Server; behaviour per Microsoft docs)

---

## ❓ Question
An order must be written to the `Orders` database on server A and a ledger row to the `Billing` database on server B atomically. What is a distributed transaction, what is MSDTC, what does two-phase commit do, why is it a poor default in Azure SQL and microservices, and what do you use instead?

---

## 💡 Quick Concept (2 lines only)
A distributed transaction spans more than one resource manager (two servers, or SQL Server plus a queue); the Microsoft Distributed Transaction Coordinator (MSDTC) runs two-phase commit (prepare, then commit) so all commit or all abort. It is slow, holds locks across the network and needs an extra service.
हिंदी: Distributed transaction = कई servers पर एक साथ commit; MSDTC two-phase commit चलाता है (पहले prepare, फिर commit)। यह धीमा है और locks लंबे समय रखता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP: linked server pointing at the second instance (names are examples)
-- ============================================
-- EXEC sp_addlinkedserver @server = N'BILLSRV', @srvproduct = N'', @provider = N'MSOLEDBSQL', @datasrc = N'billing.contoso.local';
-- EXEC sp_serveroption N'BILLSRV', N'rpc out', N'true';

-- ============================================
-- SOLUTION 1: explicit distributed transaction
-- ============================================
SET XACT_ABORT ON;               -- REQUIRED for remote modifications inside a distributed tran
BEGIN DISTRIBUTED TRANSACTION;   -- escalates the tran to MSDTC
  INSERT INTO dbo.Orders (CustomerId, Total) VALUES (10, 100.00);
  INSERT INTO BILLSRV.Billing.dbo.Ledger (CustomerId, Amount) VALUES (10, 100.00);
COMMIT TRANSACTION;              -- MSDTC: phase 1 PREPARE on both, phase 2 COMMIT on both

-- Note: a plain BEGIN TRAN that touches a linked server with XACT_ABORT ON is
-- promoted to a distributed transaction automatically.

-- ============================================
-- How to see it (DMV exists, output not reproduced here)
-- ============================================
-- SELECT * FROM sys.dm_tran_active_transactions;
```

```sql
-- EXPECTED OUTPUT
-- No engine available here supports linked servers or MSDTC; not executed on SQL Server.
-- Documented behaviour: both inserts become visible together on COMMIT, or neither on failure.
-- If MSDTC is unreachable the statement fails at BEGIN DISTRIBUTED TRANSACTION / first remote
-- statement with an error (exact number not asserted here).
```

**Two-phase commit in one glance**
```
Coordinator -> A,B : PREPARE   (each flushes log, votes yes/no, keeps locks)
Coordinator -> A,B : COMMIT    (only if all voted yes; otherwise ROLLBACK)
Risk: if coordinator dies between phases, participants stay "in doubt" holding locks.
```

---

## 🔍 Why This Works (3 lines max)
Prepare makes every participant promise it can commit; only then does the coordinator log the decision and send commit. This gives atomicity across servers at the cost of extra round trips, longer locking and an availability dependency on the coordinator.
हिंदी: पहले सब "हाँ" बोलते हैं (prepare), फिर coordinator commit का आदेश देता है। इसकी कीमत है ज़्यादा latency और locks।

---

## ⚡ Alternative Solution

```sql
-- Prefer: Outbox pattern in ONE database transaction + async delivery with idempotent consumer
BEGIN TRAN;
  INSERT INTO dbo.Orders (CustomerId, Total) VALUES (10, 100.00);
  INSERT INTO dbo.Outbox (EventType, Payload, CreatedAt)
  VALUES (N'OrderPlaced', N'{"customerId":10,"total":100.00}', SYSUTCDATETIME());
COMMIT;
-- A worker reads Outbox, calls Billing (idempotency key = OrderId), marks row Sent.
-- Failures are handled by retries / compensating actions (saga), not by distributed locks.
-- Azure SQL: cross-database transactions work inside an elastic pool via elastic transactions
-- (limited); Managed Instance supports distributed transactions across MIs in a Server Trust Group.
-- Verify current Azure support before promising it in a design.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: leaving XACT_ABORT OFF with remote modifications (error: remote tran needs XACT_ABORT ON)
-- ❌ Wrong: assuming TransactionScope in .NET / Node never escalates; a second connection to another
--    server inside one scope silently escalates to MSDTC and needs firewall + DTC config.
-- ❌ Wrong: treating Azure SQL Database like on-prem: it does not host a local MSDTC for you,
--    so design for eventual consistency instead.
-- ❌ Wrong: holding a distributed transaction open while calling an HTTP API.
```

---

## 🎯 Interview Tip (1 line)
Say: "I avoid distributed transactions in modern designs: two-phase commit couples availability and holds locks across hops. I keep each transaction in one database, use an outbox plus idempotent consumers or a saga for cross-service consistency, and only use MSDTC when a legacy requirement forces it."

---

## 🔗 Related Questions
→ Q117 (ACID in SQL Server) | Q118 (BEGIN TRAN, XACT_ABORT) | Q157 (Azure SQL DB vs MI vs VM) | Q189 (Transfer money safely)
