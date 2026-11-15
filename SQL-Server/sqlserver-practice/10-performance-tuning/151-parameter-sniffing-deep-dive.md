---

# Q151. Parameter Sniffing Deep-Dive
# Category: Performance Tuning
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL has a similar generic-vs-custom plan choice | MySQL has no plan cache for this). Plan choice not executed on SQL Server; row distribution from equivalent query on SQLite.

---

## ❓ Question
`GetOrdersByCustomer @CustomerId` is fast for most customers but times out after a restart. The first call was for a customer with 6 orders out of 10... (imagine 5 million for a big B2B customer). Explain sniffing and list the fixes with trade-offs.

---

## 💡 Quick Concept (2 lines only)
On first execution SQL Server compiles a plan using the actual parameter value ("sniffs" it) and caches it for all later values. With skewed data, a plan good for a small customer (seek + lookup) is terrible for a huge one (scan), and vice versa.
हिंदी: पहली call की value देखकर plan बनता है और cache हो जाता है। Data skewed हो तो वही plan बाकी values के लिए बुरा निकल सकता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (skewed data: customer 1 is "big")
-- ============================================
CREATE TABLE Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL,
  Status     VARCHAR(20) NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);
CREATE INDEX IX_Orders_Customer ON Orders (CustomerId);

INSERT INTO Orders VALUES
  (1,1,'Pending',10), (2,1,'Pending',20), (3,2,'Shipped',30), (4,1,'Pending',40),
  (5,3,'Pending',50), (6,1,'Pending',60), (7,2,'Shipped',70), (8,1,'Pending',80),
  (9,4,'Pending',90), (10,1,'Pending',100);
GO

-- Distribution (what the histogram sees)
SELECT CustomerId, COUNT(*) AS Orders
FROM Orders GROUP BY CustomerId ORDER BY CustomerId;
-- EXPECTED OUTPUT (SQLite equivalent; not executed on SQL Server):
-- CustomerId | Orders
-- 1          | 6      <- skew: "big" customer
-- 2          | 2
-- 3          | 1
-- 4          | 1
GO

CREATE PROCEDURE dbo.GetOrdersByCustomer @CustomerId INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT OrderId, Status, Amount
    FROM dbo.Orders
    WHERE CustomerId = @CustomerId;
END;
GO

EXEC dbo.GetOrdersByCustomer @CustomerId = 3;   -- plan compiled for 1 row: seek + lookup, cached
EXEC dbo.GetOrdersByCustomer @CustomerId = 1;   -- reuses that plan for the big customer (bad at scale)
GO

-- ============================================
-- FIXES (pick by situation)
-- ============================================
-- 1) OPTION (RECOMPILE): new plan every call, uses the real value. Costs CPU on hot paths.
-- 2) OPTION (OPTIMIZE FOR (@CustomerId UNKNOWN)): average-density plan, stable, mediocre for extremes.
-- 3) OPTION (OPTIMIZE FOR (@CustomerId = 1)): plan for a chosen representative value.
-- 4) Split logic: IF big customer -> proc A, else proc B (explicit plans).
-- 5) Query Store forced plan / hints (Q113); Azure SQL: automatic plan correction.
-- 6) SQL Server 2022: Parameter Sensitive Plan optimization (compat level 160) builds multiple plans automatically.
-- 7) Update statistics / fix indexes first: sniffing is often a symptom, not the disease.
CREATE PROCEDURE dbo.GetOrdersByCustomerRC @CustomerId INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT OrderId, Status, Amount
    FROM dbo.Orders
    WHERE CustomerId = @CustomerId
    OPTION (RECOMPILE);
END;
GO
```

---

## 🔍 Why This Works (3 lines max)
Sniffing is a feature: compiled plans are reused to save CPU. It only hurts when parameter values have very different row counts; hints either remove the reuse (RECOMPILE) or pin a more generic plan (OPTIMIZE FOR UNKNOWN).
हिंदी: Sniffing अपने आप में बुरा नहीं, skewed data में problem बनता है। RECOMPILE / OPTIMIZE FOR से control करो।

---

## ⚡ Alternative Solution

```sql
-- Local variable trick (same effect as OPTIMIZE FOR UNKNOWN, older style; hides the value)
CREATE PROCEDURE dbo.GetOrdersByCustomerLV @CustomerId INT
AS
BEGIN
    DECLARE @c INT = @CustomerId;
    SELECT OrderId, Status, Amount FROM dbo.Orders WHERE CustomerId = @c;
END;
GO

-- Clear one proc's plan to test (not on prod during peak): EXEC sp_recompile N'dbo.GetOrdersByCustomer';
```

---

## ⚠️ Common Mistake

```sql
-- ❌ DBCC FREEPROCCACHE on production to "fix" it: it flushes ALL plans -> CPU spike
-- ❌ Blaming sniffing without comparing plans/estimated vs actual rows (check Query Store: two plans?)
-- ❌ Adding RECOMPILE to a procedure called 5,000 times/sec
-- ❌ Local-variable trick forever: loses all value-specific optimisation
```

---

## 🎯 Interview Tip (1 line)
Say: "I prove it first: the cached plan's compile value vs the slow call's value, estimated vs actual rows, two plans in Query Store. Then the least invasive fix: stats/index, then OPTION (RECOMPILE) for cold paths, OPTIMIZE FOR or split procs for hot ones, and on 2022 evaluate PSP optimization."

---

## 🔗 Related Questions
→ Q080 (Recompile and plan caching) | Q114 (Parameter sniffing and fixes) | Q181 (What is parameter sniffing) | Q113 (Query Store basics)
