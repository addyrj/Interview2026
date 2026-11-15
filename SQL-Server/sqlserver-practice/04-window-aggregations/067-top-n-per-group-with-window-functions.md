# Q067. Top-N per Group with Window Functions
# Category: WINDOW FUNCTIONS + AGGREGATIONS
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server — T-SQL also has CROSS APPLY + TOP (MySQL/PostgreSQL use LATERAL ... LIMIT)

---

## ❓ Question
From `Orders`, return each customer's top 2 orders by amount, then: (a) behave correctly when amounts tie, (b) return the latest order per customer (1 row per group), and (c) write the CROSS APPLY version.

---

## 💡 Quick Concept (2 lines only)
ROW_NUMBER() OVER (PARTITION BY group ORDER BY metric DESC) filtered with `rn <= N` gives exactly N rows per group; RANK/DENSE_RANK keep ties. CROSS APPLY with TOP (N) does the same per group and can seek an index.
हिंदी: Exactly N rows चाहिए तो ROW_NUMBER, ties सहित चाहिए तो RANK। T-SQL में CROSS APPLY + TOP भी बहुत तेज़ तरीका है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Orders (
    OrderId    INT PRIMARY KEY,
    CustomerId INT           NOT NULL,
    Amount     DECIMAL(10,2) NOT NULL,
    OrderDate  DATE          NOT NULL
);

INSERT INTO Orders (OrderId, CustomerId, Amount, OrderDate) VALUES
 (1, 101, 500, '2024-01-10'), (2, 101, 900, '2024-02-10'),
 (3, 101, 900, '2024-03-10'), (4, 101, 200, '2024-04-10'),
 (5, 102, 300, '2024-01-15'), (6, 102, 700, '2024-02-15'),
 (7, 103, 400, '2024-03-20');

-- ============================================
-- (1) Exactly top 2 per customer — ROW_NUMBER with deterministic tiebreaker
-- ============================================
SELECT CustomerId, OrderId, Amount, rn
FROM (
    SELECT CustomerId, OrderId, Amount,
           ROW_NUMBER() OVER (PARTITION BY CustomerId ORDER BY Amount DESC, OrderId) AS rn
    FROM Orders
) AS t
WHERE rn <= 2
ORDER BY CustomerId, rn;

-- EXPECTED OUTPUT (result derived from equivalent query on PostgreSQL (PGlite); not executed on SQL Server):
-- CustomerId | OrderId | Amount | rn
-- 101        | 2       | 900.00 | 1
-- 101        | 3       | 900.00 | 2
-- 102        | 6       | 700.00 | 1
-- 102        | 5       | 300.00 | 2
-- 103        | 7       | 400.00 | 1

-- ============================================
-- (2) Ties kept — RANK (here customer 101 has a tie for 1st, so rank 2 does not exist)
-- ============================================
SELECT CustomerId, OrderId, Amount, rk
FROM (
    SELECT CustomerId, OrderId, Amount,
           RANK() OVER (PARTITION BY CustomerId ORDER BY Amount DESC) AS rk
    FROM Orders
) AS t
WHERE rk <= 1
ORDER BY CustomerId, OrderId;
-- 101 | 2 | 900.00 | 1   and   101 | 3 | 900.00 | 1   <- both tied orders returned
-- 102 | 6 | 700.00 | 1
-- 103 | 7 | 400.00 | 1
-- (hand-checked against the PostgreSQL RANK output; the same result is obtained with TOP (1) WITH TIES ... ORDER BY)

-- ============================================
-- (3) Latest order per customer
-- ============================================
SELECT CustomerId, OrderId, OrderDate
FROM (
    SELECT CustomerId, OrderId, OrderDate,
           ROW_NUMBER() OVER (PARTITION BY CustomerId ORDER BY OrderDate DESC) AS rn
    FROM Orders
) AS t
WHERE rn = 1;
-- 101 | 4 | 2024-04-10 ;  102 | 6 | 2024-02-15 ;  103 | 7 | 2024-03-20   (PostgreSQL (PGlite))
```

---

## 🔍 Why This Works (3 lines max)
Window functions are evaluated after WHERE and before the outer query, so the rank must be computed in a derived table/CTE and filtered outside. ROW_NUMBER never repeats a number, giving exactly N rows; RANK repeats on ties and skips numbers, so `rk <= 2` can return fewer or more rows than expected. Adding OrderId to ORDER BY removes non-determinism.
हिंदी: Window function का alias उसी SELECT में filter नहीं होता, इसलिए subquery/CTE चाहिए। Tie-break column ज़रूर जोड़ो।

---

## ⚡ Alternative Solution

```sql
-- CROSS APPLY + TOP: one index seek per customer (needs index on Orders(CustomerId, Amount DESC) INCLUDE (OrderDate))
SELECT c.CustomerId, o.OrderId, o.Amount
FROM (SELECT DISTINCT CustomerId FROM Orders) AS c      -- or your real Customers table
CROSS APPLY (
    SELECT TOP (2) x.OrderId, x.Amount
    FROM Orders AS x
    WHERE x.CustomerId = c.CustomerId
    ORDER BY x.Amount DESC, x.OrderId
) AS o
ORDER BY c.CustomerId, o.Amount DESC, o.OrderId;
-- Same 5 rows as (1). Result checked with the equivalent CROSS JOIN LATERAL ... LIMIT 2 on PostgreSQL (PGlite);
-- CROSS APPLY itself is not executed on SQL Server.
-- Rule of thumb: many rows per customer and few customers -> APPLY; few rows per customer -> ROW_NUMBER.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Filtering the window alias in the same SELECT
SELECT *, ROW_NUMBER() OVER (PARTITION BY CustomerId ORDER BY Amount DESC) AS rn
FROM Orders WHERE rn <= 2;      -- error: invalid column name 'rn'

-- ❌ RANK() for "exactly 2 rows" -> a tie for first makes ranks 1,1,3: WHERE rk <= 2 returns only the two tied rows
-- ❌ ROW_NUMBER without a tiebreaker -> OrderId 2 vs 3 may swap between runs
-- ❌ Applying WHERE Status = 'Completed' AFTER ranking -> you rank cancelled orders too; filter inside the subquery
-- ❌ GROUP BY CustomerId with MAX(Amount) -> loses the other columns of the order
```

---

## 🎯 Interview Tip (1 line)
Say: "I use ROW_NUMBER for exactly N and RANK/DENSE_RANK or TOP WITH TIES when ties must survive; for large tables I compare against CROSS APPLY + TOP with a supporting (CustomerId, Amount DESC) index and look at the actual plan, because a Sort on the window version is usually where the cost goes."

---

## 🔗 Related Questions
→ Q047 (Top N per group) | Q056 (ROW_NUMBER, RANK, DENSE_RANK, NTILE) | Q038 (CROSS APPLY and OUTER APPLY) | Q002 (TOP WITH TIES and OFFSET FETCH) | Q066 (Deduplicate with ROW_NUMBER)
