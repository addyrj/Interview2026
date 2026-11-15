---

# Q143. Avoiding Implicit Conversions
# Category: Performance Tuning
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL also converts silently; PostgreSQL mostly errors instead of converting). Plan behaviour not executed on SQL Server; per Microsoft docs.

---

## ❓ Question
`Customers.Phone` is `VARCHAR(15)` with an index. The Node.js API sends the phone as an NVARCHAR parameter and a query compares `Phone = 5551234` (INT). Both are slow. Why, and how do you fix it?

---

## 💡 Quick Concept (2 lines only)
When types differ, SQL Server converts the lower-precedence side using the data type precedence list (NVARCHAR and INT rank above VARCHAR). If the column gets converted, the index seek becomes a scan (not SARGable).
हिंदी: Types अलग हों तो SQL Server column को convert कर देता है -> index seek की जगह scan। Parameter का type column से match करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Customers (
  CustomerId INT IDENTITY(1,1) PRIMARY KEY,
  Name       NVARCHAR(100) NOT NULL,
  Phone      VARCHAR(15)   NOT NULL
);
CREATE INDEX IX_Customers_Phone ON Customers(Phone) INCLUDE (Name);

INSERT INTO Customers (Name, Phone) VALUES
  (N'Aarav', '5551234'), (N'Diya', '5559876'), (N'Kabir', '5550001');

-- ============================================
-- BAD: INT literal vs VARCHAR column -> VARCHAR column converted to INT (precedence)
-- ============================================
SELECT CustomerId, Name FROM Customers WHERE Phone = 5551234;
-- plan: CONVERT_IMPLICIT(int, Phone) -> index SCAN; also fails if any row holds 'N/A'

-- BAD: NVARCHAR parameter vs VARCHAR column (default for JS strings in mssql)
DECLARE @p NVARCHAR(15) = N'5551234';
SELECT CustomerId, Name FROM Customers WHERE Phone = @p;
-- With SQL collations the column is converted -> scan. With Windows collations
-- the seek can still happen but with a residual convert; do not rely on it.

-- ============================================
-- GOOD: match the column type exactly
-- ============================================
DECLARE @p2 VARCHAR(15) = '5551234';
SELECT CustomerId, Name FROM Customers WHERE Phone = @p2;

-- Find implicit conversions in cached plans (look for plan warnings)
SELECT TOP 10 st.text, qp.query_plan
FROM sys.dm_exec_cached_plans cp
CROSS APPLY sys.dm_exec_query_plan(cp.plan_handle) qp
CROSS APPLY sys.dm_exec_sql_text(cp.plan_handle) st
WHERE CAST(qp.query_plan AS NVARCHAR(MAX)) LIKE N'%PlanAffectingConvert%';

-- EXPECTED OUTPUT of the GOOD query (derived from equivalent query on SQLite;
-- seek vs scan itself not executed on SQL Server):
-- CustomerId | Name
-- 1          | Aarav
```

---

## 🔍 Why This Works (3 lines max)
With identical types the optimizer can compare index keys directly and seek. Any function or conversion applied to the column makes the predicate non-SARGable; converting the parameter side is free because it happens once.
हिंदी: Conversion column पर नहीं, parameter पर होना चाहिए। Column पर function = scan।

---

## ⚡ Alternative Solution

```sql
-- Convert the parameter explicitly (cost: once) instead of letting the column be converted
SELECT CustomerId, Name FROM Customers WHERE Phone = CAST(5551234 AS VARCHAR(15));

-- Node.js mssql: declare the type explicitly
-- request.input('phone', sql.VarChar(15), phone);   // NOT sql.NVarChar / default inference
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Joining VARCHAR to NVARCHAR columns across tables (e.g. legacy vs new schema)
SELECT * FROM LegacyOrders l JOIN Orders o ON o.RefCode = l.RefCode; -- RefCode types differ
-- ✅ Align the column types in DDL; it fixes every query at once

-- ❌ Comparing a numeric-looking VARCHAR to an INT: one bad row ('N/A') raises a conversion error
--    that only shows up in production data.

-- ❌ Passing JS numbers/strings without typing params: the driver may send NVARCHAR(4000)
--    and also bloats the plan cache with different parameter lengths.
```

---

## 🎯 Interview Tip (1 line)
Say: "I check the actual plan for CONVERT_IMPLICIT warnings, especially on seek predicates and joins. The fix is matching types in DDL and in the Node.js parameter declaration, not wrapping the column in CAST. Data type precedence decides which side converts."

---

## 🔗 Related Questions
→ Q110 (SARGable predicates) | Q022 (VARCHAR vs NVARCHAR) | Q008 (CAST vs CONVERT vs TRY_CAST) | Q161 (Parameterized queries from Node)
