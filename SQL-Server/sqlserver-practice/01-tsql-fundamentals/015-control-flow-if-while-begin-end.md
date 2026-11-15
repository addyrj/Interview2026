---

# Q015. Control Flow — IF, WHILE, BEGIN...END
# Category: T-SQL FUNDAMENTALS
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: IF/WHILE only inside procedures, `END IF`/`END WHILE`; PostgreSQL: PL/pgSQL `DO $$ ... $$` blocks)

---

## ❓ Question
Orders has many `Pending` rows older than 1 Feb 2024. Write a T-SQL batch that (1) checks with IF EXISTS whether any such rows exist, (2) expires them in batches of 2 rows using WHILE, so the transaction log and locks stay small, and (3) prints how many batches ran. Explain why BEGIN...END is required for multi-statement branches and why there is no `ELSE IF` keyword-pair problem.

---

## 💡 Quick Concept (2 lines only)
T-SQL has IF...ELSE and WHILE, but each branch runs exactly ONE statement unless you wrap several in BEGIN...END. WHILE + `@@ROWCOUNT` is the standard way to batch large UPDATE/DELETE jobs.
हिंदी: IF/WHILE सिर्फ एक statement control करते हैं; एक से ज़्यादा हों तो BEGIN...END लगाओ। बड़े updates को WHILE + @@ROWCOUNT से batches में तोड़ो।

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
  Amount     DECIMAL(10,2) NOT NULL,
  OrderDate  DATE NOT NULL
);

INSERT INTO Orders (OrderId, CustomerId, Status, Amount, OrderDate) VALUES
  (1, 101, 'Pending',   500.00, '2024-01-05'),
  (2, 101, 'Shipped',  1200.00, '2024-02-10'),
  (3, 102, 'Pending',   300.00, '2024-01-20'),
  (4, 103, 'Pending',   750.00, '2024-01-25'),
  (5, 104, 'Pending',    90.00, '2024-03-01'),
  (6, 102, 'Delivered',2000.00, '2024-02-01'),
  (7, 105, 'Pending',   640.00, '2024-01-15');
GO

-- ============================================
-- SOLUTION: IF EXISTS + WHILE batching
-- ============================================

DECLARE @BatchSize INT = 2;
DECLARE @Batches   INT = 0;
DECLARE @Rows      INT = 1;

IF EXISTS (SELECT 1 FROM Orders WHERE Status = 'Pending' AND OrderDate < '2024-02-01')
BEGIN
    WHILE @Rows > 0
    BEGIN
        UPDATE TOP (@BatchSize) Orders
        SET Status = 'Expired'
        WHERE Status = 'Pending' AND OrderDate < '2024-02-01';

        SET @Rows = @@ROWCOUNT;          -- read it IMMEDIATELY after the UPDATE
        IF @Rows > 0 SET @Batches += 1;  -- single statement: no BEGIN...END needed
    END
    PRINT 'Batches run: ' + CAST(@Batches AS VARCHAR(10));
END
ELSE
    PRINT 'Nothing to expire';

SELECT Status, COUNT(*) AS Cnt FROM Orders GROUP BY Status ORDER BY Status;

-- Output (PRINT goes to the Messages tab):
-- Batches run: 2
--
-- Status    | Cnt
-- Delivered | 1
-- Expired   | 4
-- Pending   | 1
-- Shipped   | 1

-- Result derived from an equivalent loop (UPDATE ... LIMIT 2 repeated until 0 rows) on SQLite
-- 3.49 driven from Python; the T-SQL batch itself was not executed on SQL Server.
-- Batch 1 touches 2 rows, batch 2 touches 2 rows, batch 3 touches 0 rows -> loop ends.
```

---

## 🔍 Why This Works (3 lines max)
`UPDATE TOP (n)` touches at most n rows per iteration, so each loop commits a small unit of work; `@@ROWCOUNT` becomes 0 once no qualifying rows remain and WHILE exits. Without BEGIN...END only the first statement after IF/WHILE belongs to it, the rest always runs. The ELSE branch is a single PRINT, so it needs no block.
हिंदी: UPDATE TOP (n) हर loop में छोटा batch बदलता है; @@ROWCOUNT = 0 होते ही WHILE रुक जाता है। BEGIN...END के बिना सिर्फ पहला statement IF का हिस्सा होता है।

---

## ⚡ Alternative Solution

```sql
-- IIF / CASE are EXPRESSIONS (return a value); IF is a STATEMENT (controls flow). Use CASE in SELECT:
SELECT OrderId,
       CASE WHEN OrderDate < '2024-02-01' AND Status = 'Pending' THEN 'Stale' ELSE 'OK' END AS Flag
FROM Orders;

-- WHILE with BREAK / CONTINUE and a counter table (generate numbers 1..5):
DECLARE @i INT = 1;
DECLARE @n TABLE (Num INT);
WHILE @i <= 5
BEGIN
    INSERT INTO @n (Num) VALUES (@i);
    SET @i += 1;
    IF @i = 4 CONTINUE;   -- skip nothing here, just shows syntax
END
SELECT Num FROM @n;
-- Set-based is almost always better: GENERATE_SERIES(1,5) needs SQL Server 2022 / Azure SQL;
-- before that use a recursive CTE or a numbers table.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: two statements after IF without BEGIN...END
DECLARE @Cnt INT = 0;
IF @Cnt > 0
    PRINT 'Rows found';
    DELETE FROM Orders WHERE Status = 'Expired';   -- ALWAYS runs, even when @Cnt = 0!

-- ✅ Fix:
IF @Cnt > 0
BEGIN
    PRINT 'Rows found';
    DELETE FROM Orders WHERE Status = 'Expired';
END

-- ❌ Wrong: infinite loop - the WHILE condition never changes
DECLARE @Rows INT = 1;
WHILE @Rows > 0
BEGIN
    UPDATE Orders SET Status = 'Pending' WHERE Status = 'Pending';  -- keeps matching the same rows
    SET @Rows = @@ROWCOUNT;
END
-- ✅ Make the UPDATE remove rows from its own WHERE predicate, or loop on a key range.

-- ❌ Wrong: reading @@ROWCOUNT after another statement (the intervening statement overwrites it)
```

---

## 🎯 Interview Tip (1 line)
Say: "I use WHILE only for batching (UPDATE TOP (n) until @@ROWCOUNT = 0, often with a short WAITFOR DELAY to let log backups catch up); for row-by-row logic I go set-based first. And I always wrap IF/WHILE bodies in BEGIN...END, even for one statement, so a later edit can't silently break it."

---

## 🔗 Related Questions
→ Q014 (variables, SET vs SELECT, GO) | Q020 (@@ROWCOUNT) | Q100 (cursors vs set-based) | Q145 (batching large updates/deletes)
