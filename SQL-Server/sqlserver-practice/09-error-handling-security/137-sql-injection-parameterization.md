
---

# Q137. SQL Injection and Parameterization
# Category: ERROR HANDLING + SECURITY
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (same principle in MySQL/PostgreSQL; T-SQL specifics: sp_executesql, QUOTENAME)

---

## ❓ Question
A Node.js endpoint builds `SELECT * FROM Customers WHERE Email = '` + input + `'`. Show the attack, the fix with `mssql` parameters and with `sp_executesql`, and how to safely accept a column name / sort order that cannot be parameterized.

---

## 💡 Quick Concept (2 lines only)
Injection happens when user input becomes part of the SQL text. Parameters travel separately from the statement, so they are always data, never code. Identifiers (table/column/ORDER BY) cannot be parameters: whitelist them or wrap with QUOTENAME.
हिंदी: Input को SQL text में जोड़ने से injection होता है। Parameter हमेशा data रहता है, code नहीं। Column/ORDER BY नाम parameter नहीं बन सकते, उन्हें whitelist करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Customers (
  CustomerId INT PRIMARY KEY,
  Email      NVARCHAR(200) NOT NULL,
  Name       NVARCHAR(100) NOT NULL
);
INSERT INTO dbo.Customers VALUES (1, N'a@x.com', N'Asha'), (2, N'b@x.com', N'Ben'), (3, N'c@x.com', N'Chen');
GO

-- ============================================
-- THE ATTACK: input = ' OR '1'='1
-- ============================================
DECLARE @in NVARCHAR(200) = N'''' + N' OR ''1''=''1';
DECLARE @bad NVARCHAR(MAX) = N'SELECT * FROM dbo.Customers WHERE Email = ''' + @in + N'''';
-- @bad = SELECT * FROM dbo.Customers WHERE Email = '' OR '1'='1'   -> returns every customer
EXEC (@bad);

-- ============================================
-- SOLUTION 1: sp_executesql with parameters
-- ============================================
DECLARE @email NVARCHAR(200) = N''' OR ''1''=''1';
EXEC sp_executesql
  N'SELECT CustomerId, Email, Name FROM dbo.Customers WHERE Email = @Email',
  N'@Email NVARCHAR(200)',
  @Email = @email;                          -- treated as one literal string; no match -> 0 rows

-- ============================================
-- SOLUTION 2: dynamic ORDER BY via whitelist + QUOTENAME
-- ============================================
CREATE OR ALTER PROCEDURE dbo.usp_SearchCustomers
  @Name NVARCHAR(100) = NULL, @SortCol SYSNAME = N'Name', @SortDir VARCHAR(4) = 'ASC'
AS
BEGIN
  SET NOCOUNT ON;
  IF @SortCol NOT IN (N'Name', N'Email', N'CustomerId') THROW 50100, 'Invalid sort column.', 1;
  IF UPPER(@SortDir) NOT IN ('ASC', 'DESC')            THROW 50101, 'Invalid sort direction.', 1;

  DECLARE @sql NVARCHAR(MAX) =
    N'SELECT CustomerId, Email, Name FROM dbo.Customers
      WHERE (@Name IS NULL OR Name LIKE @Name + N''%'')
      ORDER BY ' + QUOTENAME(@SortCol) + N' ' + UPPER(@SortDir);

  EXEC sp_executesql @sql, N'@Name NVARCHAR(100)', @Name = @Name;
END;
GO
```

```js
// Node.js (mssql): ALWAYS use .input(); never template strings
const r = await pool.request()
  .input('Email', sql.NVarChar(200), req.query.email)    // explicit type + length
  .query('SELECT CustomerId, Email, Name FROM dbo.Customers WHERE Email = @Email');
// Template-literal query(`... '${email}'`) is the vulnerable version.
```

```sql
-- EXPECTED OUTPUT
-- Result derived from equivalent query on SQLite (string-concatenated vs bound parameter); not executed on SQL Server.
-- Concatenated input  ' OR '1'='1  -> 3 rows: (1,a@x.com,Asha), (2,b@x.com,Ben), (3,c@x.com,Chen)   <- data leak
-- Parameterized same input        -> 0 rows
-- usp_SearchCustomers behaviour (whitelist, QUOTENAME) is per Microsoft docs; not executed.
```

---

## 🔍 Why This Works (3 lines max)
With parameters the statement is compiled with a placeholder, and the value is passed in a separate typed slot, so quote characters can never end the string literal. It also lets the plan be cached and reused.
हिंदी: Parameter में value अलग typed slot में जाती है, इसलिए quote लगाकर string तोड़ना असंभव है। Plan cache भी reuse होता है।

---

## ⚡ Alternative Solution

```sql
-- Stored procedure with typed parameters (no dynamic SQL) + least privilege (EXECUTE only)
CREATE OR ALTER PROCEDURE dbo.usp_GetCustomerByEmail @Email NVARCHAR(200)
AS SELECT CustomerId, Email, Name FROM dbo.Customers WHERE Email = @Email;
-- Even procedures are injectable if they build EXEC('...' + @param). Use sp_executesql inside them (Q078).
-- ORMs (Prisma, TypeORM) parameterize by default, but raw-query helpers ($queryRawUnsafe) do not.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "escaping" quotes by REPLACE(@in, '''', '''''') as the only defense (Unicode and second-order tricks exist)
-- ❌ Wrong: parameterizing the values but concatenating the table/column name from the request
-- ❌ Wrong: EXEC('SELECT ... ' + @param) inside a procedure; the proc gives no protection
-- ❌ Wrong: IN-list built by joining ids into a string. Use a table-valued parameter or OPENJSON with a JSON parameter.
-- ❌ Wrong: connecting as db_owner, so one injection means total compromise.
```

---

## 🎯 Interview Tip (1 line)
Say: "Parameters for values, whitelist plus QUOTENAME for identifiers, EXECUTE-only least-privilege accounts, no sa. Validate type and length at the API boundary as defence in depth, and watch second-order injection where stored data is later concatenated into dynamic SQL."

---

## 🔗 Related Questions
→ Q017 (Dynamic SQL with sp_executesql) | Q078 (Dynamic SQL in procedures + injection safety) | Q161 (Parameterized queries from Node) | Q087 (Search procedure with dynamic filters)
