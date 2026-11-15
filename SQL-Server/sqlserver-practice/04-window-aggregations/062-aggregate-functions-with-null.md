# Q062. Aggregate Functions with NULL
# Category: WINDOW FUNCTIONS + AGGREGATIONS
# Difficulty: ⭐⭐ Medium
# DB: SQL Server — NULL semantics are the same in MySQL and PostgreSQL; T-SQL additionally prints a warning when NULLs are skipped

---

## ❓ Question
`Payments` has some NULL amounts and discounts. Predict the result of COUNT(*), COUNT(col), SUM, AVG, MAX on these columns, SUM over an empty set, and why `SUM(Amount - Discount)` differs from `SUM(Amount) - SUM(Discount)`.

---

## 💡 Quick Concept (2 lines only)
Aggregates ignore NULL inputs (except COUNT(*), which counts rows). If every input is NULL or there are no rows, SUM/AVG/MAX return NULL while COUNT(col) returns 0.
हिंदी: COUNT(*) सब rows गिनता है, बाकी aggregates NULL को skip करते हैं। Empty set पर SUM = NULL, COUNT = 0।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Payments (
    PaymentId INT PRIMARY KEY,
    Customer  VARCHAR(10)   NOT NULL,
    Amount    DECIMAL(10,2) NULL,
    Discount  DECIMAL(10,2) NULL
);

INSERT INTO Payments (PaymentId, Customer, Amount, Discount) VALUES
 (1, 'Asha',  100, 10),
 (2, 'Asha',  200, NULL),
 (3, 'Ravi',  300, 20),
 (4, 'Meena', NULL, NULL);

-- ============================================
-- SOLUTION
-- ============================================
SELECT
    COUNT(*)                   AS CntStar,
    COUNT(Amount)              AS CntAmount,
    COUNT(Discount)            AS CntDiscount,
    SUM(Discount)              AS SumDiscount,
    AVG(Amount)                AS AvgAmount,
    AVG(COALESCE(Amount, 0))   AS AvgAmountNullAsZero,
    MAX(Discount)              AS MaxDiscount
FROM Payments;

-- EXPECTED OUTPUT (result derived from equivalent query on PostgreSQL (PGlite); not executed on SQL Server):
-- CntStar | CntAmount | CntDiscount | SumDiscount | AvgAmount | AvgAmountNullAsZero | MaxDiscount
-- 4       | 3         | 2           | 30.00       | 200.00    | 150.00              | 20.00
-- (PostgreSQL printed more decimal places for AVG; SQL Server keeps a DECIMAL result type)
-- T-SQL also raises the informational message: "Warning: Null value is eliminated by an aggregate or other SET operation."

-- Per-group and empty-set behaviour
SELECT Customer, SUM(Discount) AS SumDiscount FROM Payments GROUP BY Customer ORDER BY Customer;
-- Asha | 10.00 ;  Meena | NULL ;  Ravi | 20.00        (Meena has only NULLs -> SUM is NULL, not 0)

SELECT SUM(Discount) AS S, COUNT(Discount) AS C FROM Payments WHERE 1 = 0;
-- S = NULL, C = 0

-- Row-wise vs column-wise arithmetic
SELECT SUM(Amount - Discount) AS SumOfDiff, SUM(Amount) - SUM(Discount) AS DiffOfSums FROM Payments;
-- SumOfDiff = 370.00 (rows 2 and 4 become NULL and vanish), DiffOfSums = 570.00 (600 - 30)

-- NULL in comparisons
SELECT COUNT(*) FROM Payments WHERE Discount <> 10;                       -- 1  (NULL rows are dropped)
SELECT COUNT(*) FROM Payments WHERE Discount <> 10 OR Discount IS NULL;   -- 3
```

---

## 🔍 Why This Works (3 lines max)
NULL means "unknown", so aggregates skip it rather than guess; COUNT(*) is the only form that counts rows regardless of content. Arithmetic with NULL yields NULL (200 - NULL = NULL), so the row-wise subtraction loses whole rows while the column-wise version only skips the NULL cells. The 3-valued logic of `<>` makes NULL rows neither true nor false, so WHERE discards them.
हिंदी: NULL = unknown। 200 - NULL = NULL, इसलिए पूरी row का result गायब हो जाता है। Comparison में भी NULL row बाहर हो जाती है।

---

## ⚡ Alternative Solution

```sql
-- Make the intent explicit: treat NULL discount as 0 before aggregating
SELECT SUM(Amount - ISNULL(Discount, 0)) AS NetAmount FROM Payments;   -- 590.00 (hand-checked: 90 + 200 + 280)

-- Always return a number for an empty/all-NULL group:
SELECT Customer, COALESCE(SUM(Discount), 0) AS SumDiscount FROM Payments GROUP BY Customer;

-- Average that does NOT skip NULLs (counts them as 0 on purpose):
SELECT SUM(Amount) * 1.0 / COUNT(*) AS AvgPerRow FROM Payments;   -- 600 / 4 = 150
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Thinking AVG(Amount) = SUM/COUNT(*) -> it is SUM/COUNT(Amount): 200, not 150
-- ❌ AVG on an INT column does integer arithmetic in T-SQL: AVG of (1, 2) returns 1, not 1.5
SELECT AVG(Quantity * 1.0) FROM OrderItems;   -- ✅ force decimal (OrderItems.Quantity is an INT column)

-- ❌ Expecting SUM over zero rows to be 0 -> it is NULL; the API layer may crash on null.toFixed()
-- ❌ Using = NULL / <> NULL -> always unknown; use IS NULL / IS NOT NULL
-- ❌ Ignoring the "Null value is eliminated" warning in ETL logs -> it signals silent data loss in totals
```

---

## 🎯 Interview Tip (1 line)
Say: "I decide per metric whether NULL means 'zero' or 'unknown' and write it explicitly with COALESCE; I also cast INT inputs to DECIMAL before AVG, because T-SQL's integer-average truncation has caused real reporting bugs."

---

## 🔗 Related Questions
→ Q004 (NULL handling — ISNULL, COALESCE, NULLIF, IIF) | Q003 (DISTINCT, GROUP BY and HAVING) | Q053 (Anti-joins — NOT IN NULL trap) | Q061 (ROLLUP, CUBE, GROUPING SETS)
