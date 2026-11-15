---

# Q005. CASE Expressions
# Category: T-SQL Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (CASE is ANSI - identical in MySQL/PostgreSQL; IIF and CHOOSE are T-SQL extras)

---

## ❓ Question
For an `Orders` table: label each order Low/Medium/High by amount, bucket statuses into Done/Open, compute conditional sums (delivered vs cancelled vs open) in one pass, and sort by a custom status order.

---

## 💡 Quick Concept (2 lines only)
`CASE` returns the first matching branch (searched form: `WHEN condition`, simple form: `CASE col WHEN value`); no match and no ELSE gives NULL. It works anywhere an expression works: SELECT, WHERE, ORDER BY, inside aggregates.
हिंदी: CASE पहली matching branch देता है। ELSE भूल गए तो NULL आएगा।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId     INT           NOT NULL PRIMARY KEY,
  CustomerId  INT           NOT NULL,
  Amount      DECIMAL(10,2) NOT NULL,
  Status      VARCHAR(20)   NOT NULL
);

INSERT INTO dbo.Orders (OrderId, CustomerId, Amount, Status) VALUES
  (1, 1,   49.99, 'Delivered'),
  (2, 1, 1250.00, 'Shipped'),
  (3, 2,  300.00, 'Cancelled'),
  (4, 3,  899.50, 'Delivered'),
  (5, 4,   15.00, 'Pending'),
  (6, 2, 2500.00, 'Delivered');

-- ============================================
-- 1. Searched CASE: amount tiers
-- ============================================

SELECT OrderId, Amount,
       CASE WHEN Amount >= 1000 THEN 'High'
            WHEN Amount >= 100  THEN 'Medium'
            ELSE 'Low' END AS Tier
FROM dbo.Orders
ORDER BY OrderId;

-- OrderId | Amount  | Tier
-- 1       | 49.99   | Low
-- 2       | 1250.00 | High
-- 3       | 300.00  | Medium
-- 4       | 899.50  | Medium
-- 5       | 15.00   | Low
-- 6       | 2500.00 | High

-- ============================================
-- 2. Simple CASE + GROUP BY the expression
-- ============================================

SELECT CASE Status WHEN 'Delivered' THEN 'Done'
                   WHEN 'Cancelled' THEN 'Done'
                   ELSE 'Open' END AS Bucket,
       COUNT(*) AS Cnt
FROM dbo.Orders
GROUP BY CASE Status WHEN 'Delivered' THEN 'Done'
                     WHEN 'Cancelled' THEN 'Done'
                     ELSE 'Open' END;     -- SQL Server cannot GROUP BY the alias

-- Bucket | Cnt
-- Done   | 4
-- Open   | 2

-- ============================================
-- 3. Conditional aggregation (pivot-style, one scan)
-- ============================================

SELECT SUM(CASE WHEN Status = 'Delivered' THEN Amount ELSE 0 END) AS DeliveredAmt,
       SUM(CASE WHEN Status = 'Cancelled' THEN Amount ELSE 0 END) AS CancelledAmt,
       SUM(CASE WHEN Status NOT IN ('Delivered','Cancelled') THEN Amount END) AS OpenAmt
FROM dbo.Orders;

-- DeliveredAmt | CancelledAmt | OpenAmt
-- 3449.49      | 300.00       | 1265.00

-- ============================================
-- 4. Custom sort order
-- ============================================

SELECT OrderId, Status
FROM dbo.Orders
ORDER BY CASE Status WHEN 'Pending' THEN 1 WHEN 'Shipped' THEN 2 WHEN 'Delivered' THEN 3 ELSE 4 END, OrderId;
-- 5 Pending | 2 Shipped | 1 Delivered | 4 Delivered | 6 Delivered | 3 Cancelled

-- Note: results derived from equivalent queries on SQLite (CASE is engine-neutral);
-- not executed on SQL Server. Decimal display (e.g. 49.99) follows the DECIMAL(10,2) type.
```

---

## 🔍 Why This Works (3 lines max)
CASE is an expression, not a statement, so it can be nested inside aggregates to compute several filtered totals in a single table scan. Branches are tested in order and the first true one wins, so put the most restrictive condition first.
हिंदी: CASE expression है, statement नहीं, इसलिए SUM के अंदर भी चलता है। Order of WHEN मायने रखता है।

---

## ⚡ Alternative Solution

```sql
-- IIF (SQL Server 2012+, shorthand for a 2-way CASE) and CHOOSE (index lookup)
SELECT OrderId,
       IIF(Amount >= 1000, 'High', 'Normal')                  AS Tier2,
       CHOOSE(CASE Status WHEN 'Pending' THEN 1 WHEN 'Shipped' THEN 2 ELSE 3 END,
              'Open', 'In transit', 'Closed')                 AS StatusLabel
FROM dbo.Orders;

-- Conditional aggregation with COUNT: COUNT(CASE WHEN Status='Pending' THEN 1 END)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: overlapping ranges in the wrong order
CASE WHEN Amount >= 100 THEN 'Medium' WHEN Amount >= 1000 THEN 'High' END
-- 1250 hits the first branch -> 'Medium'. Put the strictest condition first.

-- ❌ Wrong: forgetting ELSE -> silent NULLs; SUM(CASE ... END) over no match gives NULL not 0
-- ✅ Add ELSE 0 (or wrap in COALESCE) when you need a number.

-- ❌ Wrong: simple CASE with NULL
CASE Status WHEN NULL THEN 'Unknown' END      -- never true (it compares Status = NULL)
-- ✅ CASE WHEN Status IS NULL THEN 'Unknown' END

-- ❌ Wrong: mixing result types without thinking
CASE WHEN Amount > 100 THEN 'High' ELSE 0 END -- tries to convert 'High' to INT -> error
```

---

## 🎯 Interview Tip (1 line)
Say: "I use conditional aggregation (SUM/COUNT over CASE) to build pivot-like reports in one scan, and CASE in ORDER BY for custom sorting. I remember that CASE returns the highest-precedence type among its branches, and that a CASE in WHERE on an indexed column can kill seeks."

---

## 🔗 Related Questions
→ Q004 (NULL handling) | Q050 (PIVOT and UNPIVOT) | Q003 (GROUP BY and HAVING) | Q062 (Aggregate functions with NULL)
