---

# Q092. Indexed (Materialized) Views
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: no materialized views; PostgreSQL: MATERIALIZED VIEW refreshed manually, not auto-maintained)

---

## ❓ Question
A dashboard query sums Amount per product category over 50 million OrderLines and takes seconds. How can you make the aggregate instant without changing the application query, and what are the costs and rules?

---

## 💡 Quick Concept (2 lines only)
An indexed view is a SCHEMABINDING view with a unique clustered index: SQL Server materialises the rows and keeps them updated on every DML. It needs COUNT_BIG(*) with GROUP BY, deterministic expressions, two-part names and the right SET options.
हिंदी: Indexed view = SCHEMABINDING view + unique clustered index। Result physically store होता है और हर DML पर auto-update। Reads fast, writes slow।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.OrderLines (
  LineId   INT PRIMARY KEY,
  Category VARCHAR(30)   NOT NULL,
  Quantity INT           NOT NULL,
  Amount   DECIMAL(10,2) NOT NULL
);

INSERT INTO dbo.OrderLines VALUES
  (1, 'Electronics', 1, 1200), (2, 'Electronics', 2, 1600), (3, 'Home', 1, 35),
  (4, 'Home', 3, 450), (5, 'Electronics', 1, 150);
GO

-- ============================================
-- SOLUTION
-- ============================================

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

CREATE VIEW dbo.vSalesByCategory
WITH SCHEMABINDING
AS
SELECT Category,
       COUNT_BIG(*)  AS LineCount,      -- mandatory with GROUP BY
       SUM(Amount)   AS TotalAmount,    -- Amount is NOT NULL
       SUM(Quantity) AS TotalQty
FROM dbo.OrderLines
GROUP BY Category;
GO

CREATE UNIQUE CLUSTERED INDEX UCX_vSalesByCategory ON dbo.vSalesByCategory (Category);
GO

-- Enterprise/Developer edition: the optimizer may use the view automatically for the base query.
-- Standard edition (and to be sure): reference the view with NOEXPAND.
SELECT Category, LineCount, TotalAmount, TotalQty
FROM dbo.vSalesByCategory WITH (NOEXPAND)
ORDER BY Category;

-- EXPECTED OUTPUT (result derived from the equivalent GROUP BY on SQLite; materialisation,
-- NOEXPAND and automatic matching are not executed on SQL Server; behaviour per Microsoft docs):
-- Category    | LineCount | TotalAmount | TotalQty
-- Electronics | 3         | 2950.00     | 4
-- Home        | 2         | 485.00      | 4
```

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
The clustered index physically stores the aggregated result, and SQL Server updates it inside the same transaction as each INSERT/UPDATE/DELETE on OrderLines. COUNT_BIG(*) lets the engine maintain groups incrementally (it knows when a group disappears). Reads become a tiny seek/scan instead of an aggregate over millions of rows.
हिंदी: Clustered index aggregate को physically store करता है, base table के हर change पर साथ में update। COUNT_BIG(*) से group maintain होता है।

---

## ⚡ Alternative Solution

```sql
-- Pre-aggregated summary table refreshed by a job or computed in batches:
-- + no write-path overhead, works with any query shape, allows outer joins/windows,
-- - stale between refreshes, you own the refresh logic.
-- Also consider a nonclustered columnstore index for analytic aggregates on large fact tables (Q106).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: forgetting COUNT_BIG(*) or SCHEMABINDING -> CREATE UNIQUE CLUSTERED INDEX fails.
-- ❌ Wrong: using unsupported constructs (outer joins, subqueries, DISTINCT, MIN/MAX, UNION,
--    non-deterministic functions like GETDATE) in the view definition.
-- ❌ Wrong: indexing a view on a hot OLTP table without testing -> every write also updates
--    the view (contention on popular groups, e.g. one 'Electronics' row).
-- ❌ Wrong: assuming Standard edition matches the view automatically -> use WITH (NOEXPAND).
-- ✅ Check the rules in the docs, load-test write throughput.
```

---

## 🎯 Interview Tip (1 line)
Say: "Indexed views trade write cost for read speed, so I use them on read-heavy aggregates with a low-cardinality GROUP BY. I know the restrictions (SCHEMABINDING, COUNT_BIG, deterministic, no outer joins), NOEXPAND on Standard edition, and I compare against a summary table or columnstore before choosing."

---

## 🔗 Related Questions
→ Q091 (Views) | Q106 (Columnstore indexes) | Q102 (Clustered vs non-clustered) | Q061 (ROLLUP, CUBE, GROUPING SETS) | Q107 (Reading an execution plan)
