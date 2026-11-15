---

# Q081. WITH EXECUTE AS and Security
# Category: Stored Procedures
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server / Azure SQL (MySQL: SQL SECURITY DEFINER/INVOKER; PostgreSQL: SECURITY DEFINER/INVOKER)

---

## ❓ Question
Your Node.js app logs in as `app_user` that must NOT have direct SELECT/UPDATE rights on `dbo.Salaries`, yet must be able to call `dbo.usp_GiveRaise`. How do you grant this safely with stored procedures? Explain ownership chaining, `EXECUTE AS`, and when each applies.

---

## 💡 Quick Concept (2 lines only)
Ownership chaining: if a procedure and the tables it touches have the same owner (usually `dbo`), the caller only needs EXECUTE on the procedure — no table permissions. `WITH EXECUTE AS` switches the security context for the procedure body (needed for dynamic SQL, cross-database access or when the chain is broken).
हिंदी: Procedure और table का owner same हो तो caller को सिर्फ EXECUTE permission चाहिए (ownership chaining)। Chain टूटे/dynamic SQL में `EXECUTE AS`।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Salaries (
  EmployeeId INT PRIMARY KEY,
  Salary     DECIMAL(10,2) NOT NULL
);
INSERT INTO dbo.Salaries VALUES (1, 90000), (2, 75000);
GO

-- Least-privilege login-less user for the app (Azure SQL / contained database style)
CREATE USER app_user WITHOUT LOGIN;      -- in a real deployment: CREATE USER app_user FOR LOGIN ... or FROM EXTERNAL PROVIDER (Entra ID)
GO

-- ============================================
-- SOLUTION 1: ownership chaining (no EXECUTE AS needed)
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_GiveRaise
    @EmployeeId INT,
    @Percent    DECIMAL(5,2)
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE dbo.Salaries
    SET Salary = Salary * (1 + @Percent / 100.0)
    WHERE EmployeeId = @EmployeeId;
END;
GO

GRANT EXECUTE ON dbo.usp_GiveRaise TO app_user;      -- only this; NO grant on dbo.Salaries
-- DENY SELECT ON dbo.Salaries TO app_user;          -- optional explicit lock

-- Test as the app user:
EXECUTE AS USER = 'app_user';
    EXEC dbo.usp_GiveRaise @EmployeeId = 1, @Percent = 10;   -- works through the ownership chain
    -- SELECT * FROM dbo.Salaries;                           -- would fail: no SELECT permission on the table
REVERT;
-- Result (hand-calculated, not executed on SQL Server): employee 1 salary 90000 -> 99000.00
-- Permission behaviour per Microsoft docs; not executed on SQL Server.

-- ============================================
-- SOLUTION 2: EXECUTE AS OWNER (needed for dynamic SQL, where chaining does not apply)
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_GetSalaryDyn
    @EmployeeId INT
WITH EXECUTE AS OWNER                          -- body runs as the procedure owner (dbo)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @sql NVARCHAR(MAX) = N'SELECT EmployeeId, Salary FROM dbo.Salaries WHERE EmployeeId = @id';
    EXEC sys.sp_executesql @sql, N'@id INT', @id = @EmployeeId;
END;
GO
GRANT EXECUTE ON dbo.usp_GetSalaryDyn TO app_user;
```

---

## 🔍 Why This Works (3 lines max)
With an unbroken ownership chain SQL Server checks permissions only on the procedure, so the app can change data only through the audited code path. `EXECUTE AS` explicitly impersonates another principal for the procedure body, which also covers dynamic SQL where ownership chaining does not carry over.
हिंदी: Chain unbroken है तो सिर्फ procedure की permission check होती है। Dynamic SQL में chain नहीं चलता, इसलिए `EXECUTE AS`।

---

## ⚡ Alternative Solution

```sql
-- Code signing (certificate-based): grant the needed rights to a certificate user, sign the procedure with it.
-- Permissions apply only while that signed procedure runs -- more granular than EXECUTE AS OWNER.
-- Options for EXECUTE AS: CALLER (default), SELF, OWNER, 'user_name'.
-- Row-level restriction: add Row-Level Security (CREATE SECURITY POLICY) so even the proc sees only allowed rows.
-- Azure SQL: prefer Microsoft Entra ID / managed identity for the app login instead of SQL passwords.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Granting db_owner / db_datareader+db_datawriter to the application login "so it just works".
-- ❌ Using EXECUTE AS OWNER broadly: a SQL injection in that procedure then runs with owner (dbo) rights.
-- ❌ Assuming ownership chaining covers dynamic SQL, TRUNCATE, or cross-database calls -- it does not (cross-database
--    chaining is off by default; TRUNCATE needs ALTER permission on the table).
-- ❌ Forgetting REVERT after EXECUTE AS in test scripts, so the rest of the session runs as the test user.
-- ❌ Using EXECUTE AS with a db user that has TRUSTWORTHY ON as a shortcut -> privilege-escalation risk.
```

---

## 🎯 Interview Tip (1 line)
Say: "The app gets only EXECUTE on a schema or specific procedures; ownership chaining handles table access, and I use `EXECUTE AS` or certificate signing only where chaining breaks, like dynamic SQL — least privilege, and Entra ID auth on Azure SQL." Mention that table-level DENY plus procs gives an auditable data-access layer.

---

## 🔗 Related Questions
→ Q078 (Dynamic SQL + injection) | Q068 (What is a stored procedure) | Q019 (Schemas and object naming) | Q079 (Procedure vs function vs view)
