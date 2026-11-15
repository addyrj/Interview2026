---

# Q091. Views — Benefits and Limitations
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: views similar, MERGE/TEMPTABLE algorithms; PostgreSQL: plain views + MATERIALIZED VIEW with REFRESH)

---

## ❓ Question
Create a reporting view summarising non-cancelled orders per customer. List what views are good for, and the limitations (ORDER BY, parameters, SELECT *, performance myths) an interviewer expects you to know.

---

## 💡 Quick Concept (2 lines only)
A view is a stored SELECT, not stored data: it is expanded into the outer query at compile time. Use it for abstraction, security (expose columns/rows) and reuse; it cannot take parameters (use an inline TVF) and has no guaranteed order.
हिंदी: View = saved SELECT, data नहीं। Abstraction, security, reuse के लिए। Parameter नहीं ले सकता (inline TVF use करो), ORDER BY की guarantee नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId INT PRIMARY KEY, CustomerId INT NOT NULL,
  Status VARCHAR(20) NOT NULL, Amount DECIMAL(10,2) NOT NULL
);

INSERT INTO dbo.Orders VALUES
  (1, 1, 'Shipped',   100), (2, 1, 'Shipped',   250), (3, 2, 'Pending',  80),
  (4, 2, 'Shipped',   120), (5, 3, 'Cancelled',  60), (6, 1, 'Pending',  40);
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER VIEW dbo.vOrderSummary
WITH SCHEMABINDING                    -- blocks changes to underlying columns that would break the view
AS
SELECT CustomerId,
       COUNT(*)    AS OrderCount,
       SUM(Amount) AS TotalAmount
FROM dbo.Orders                       -- SCHEMABINDING needs two-part names, no SELECT *
WHERE Status <> 'Cancelled'
GROUP BY CustomerId;
GO

SELECT CustomerId, OrderCount, TotalAmount FROM dbo.vOrderSummary ORDER BY CustomerId;
SELECT CustomerId, OrderCount, TotalAmount FROM dbo.vOrderSummary WHERE TotalAmount > 200;

-- EXPECTED OUTPUT (result derived from the same view on SQLite; not executed on SQL Server):
-- CustomerId | OrderCount | TotalAmount
-- 1          | 3          | 390.00
-- 2          | 2          | 200.00
--
-- CustomerId | OrderCount | TotalAmount
-- 1          | 3          | 390.00

-- Security use: grant access to the view only, not the base table
-- GRANT SELECT ON dbo.vOrderSummary TO reporting_role;   -- DENY on dbo.Orders stays in place
```

Limitations to state:
- No parameters (use an inline TVF); ORDER BY is invalid in a view unless TOP/OFFSET is used, and even then the outer query decides the order.
- `SELECT *` is expanded at creation: new base columns do not appear until `sp_refreshview`/ALTER.
- Nested views hide complexity, producing huge plans; a plain view stores no data and gives no speed-up by itself.
- Writes through a view are limited (Q093).

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
The optimizer merges the view definition into the calling query, so the filter on TotalAmount is optimised together with the underlying table access. SCHEMABINDING prevents a column drop or type change from silently breaking the view. Permissions on the view let you expose a safe subset.
हिंदी: View का definition outer query में merge होता है। SCHEMABINDING से base table के columns accidentally नहीं टूटते। Security के लिए सिर्फ़ view पर permission दो।

---

## ⚡ Alternative Solution

```sql
-- Need parameters? Inline TVF:
CREATE OR ALTER FUNCTION dbo.fn_OrderSummary (@MinTotal DECIMAL(10,2))
RETURNS TABLE
AS RETURN
  SELECT CustomerId, COUNT(*) AS OrderCount, SUM(Amount) AS TotalAmount
  FROM dbo.Orders WHERE Status <> 'Cancelled'
  GROUP BY CustomerId HAVING SUM(Amount) >= @MinTotal;
-- Need physical speed-up? Indexed view (Q092).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: relying on ORDER BY inside the view for ordered output
CREATE VIEW dbo.vBad AS SELECT TOP 100 PERCENT * FROM dbo.Orders ORDER BY Amount;
-- The outer query can reorder; TOP 100 PERCENT ... ORDER BY guarantees nothing about final order.

-- ❌ Wrong: SELECT * in a view, then ALTER TABLE adds/renames a column -> stale or wrong output.
-- ❌ Wrong: stacking views 5 deep and joining them -> optimizer cannot simplify, plan explodes.
-- ✅ ORDER BY in the outer query; list columns explicitly; keep views shallow.
```

---

## 🎯 Interview Tip (1 line)
Say: "Views are for abstraction and security, not performance. I use SCHEMABINDING with explicit column lists for views that matter, expose live-rows views over soft-delete tables, avoid nesting, and use an indexed view or a summary table when I actually need precomputed aggregates."

---

## 🔗 Related Questions
→ Q092 (Indexed views) | Q093 (Updatable views, WITH CHECK OPTION) | Q089 (Inline TVF) | Q079 (Procedure vs function vs view) | Q110 (SARGable predicates)
