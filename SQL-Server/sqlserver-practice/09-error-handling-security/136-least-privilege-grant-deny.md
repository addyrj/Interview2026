
---

# Q136. Least-Privilege Permissions (GRANT / DENY)
# Category: ERROR HANDLING + SECURITY
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL has GRANT/REVOKE but no DENY; MySQL has no DENY either)

---

## ❓ Question
A reporting role should read Orders but never see `Customers.CreditCardLast4` or `Customers.Salary`-like sensitive columns, and the API role should only execute procedures, not touch tables. Show GRANT, DENY, REVOKE, column-level permissions, ownership chaining and how to verify effective permissions.

---

## 💡 Quick Concept (2 lines only)
GRANT adds a permission, REVOKE removes a previous GRANT or DENY, DENY blocks it and always wins over GRANT (except sysadmin / owner). Grant EXECUTE on procedures and rely on ownership chaining so callers need no table rights.
हिंदी: GRANT देता है, REVOKE हटाता है, DENY रोकता है और GRANT से भारी पड़ता है। Procedures पर EXECUTE दो, tables पर नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Customers (
  CustomerId   INT PRIMARY KEY,
  Name         NVARCHAR(100) NOT NULL,
  Email        NVARCHAR(200) NOT NULL,
  CardLast4    CHAR(4) NULL
);
CREATE TABLE dbo.Orders (OrderId INT PRIMARY KEY, CustomerId INT NOT NULL, Total DECIMAL(10,2) NOT NULL);
GO
CREATE ROLE role_reporting;
CREATE ROLE role_api;
GO

-- ============================================
-- SOLUTION
-- ============================================
-- 1) Reporting: table-level SELECT on Orders, column-level SELECT on Customers
GRANT SELECT ON dbo.Orders TO role_reporting;
GRANT SELECT ON dbo.Customers (CustomerId, Name) TO role_reporting;   -- Email and CardLast4 not granted
-- a SELECT of CardLast4 now fails with a permission error

-- 2) API: only procedures (ownership chaining: proc and tables share the owner dbo)
CREATE OR ALTER PROCEDURE dbo.usp_GetOrdersByCustomer @CustomerId INT
AS SELECT OrderId, Total FROM dbo.Orders WHERE CustomerId = @CustomerId;
GO
GRANT EXECUTE ON dbo.usp_GetOrdersByCustomer TO role_api;
-- or the whole schema:  GRANT EXECUTE ON SCHEMA::dbo TO role_api;

-- 3) DENY as a guard rail on a broad grant
GRANT SELECT ON SCHEMA::dbo TO role_reporting;                         -- broad
DENY  SELECT ON dbo.Customers (CardLast4, Email) TO role_reporting;    -- wins over the broad GRANT

-- 4) Undo
REVOKE SELECT ON dbo.Orders FROM role_reporting;     -- REVOKE removes the grant, it does not DENY

-- 5) Verify effective permissions
SELECT * FROM fn_my_permissions(N'dbo.Customers', N'OBJECT');          -- as current user
EXECUTE AS USER = 'reporting_user';
  SELECT HAS_PERMS_BY_NAME(N'dbo.Customers', N'OBJECT', N'SELECT');
REVERT;
```

```sql
-- EXPECTED OUTPUT
-- Not executed on SQL Server; permission evaluation has no equivalent engine here. Per Microsoft docs:
-- reporting_user: SELECT CustomerId, Name FROM dbo.Customers  -> allowed
-- reporting_user: SELECT CardLast4 FROM dbo.Customers         -> error 230 (SELECT denied on column) after the DENY
-- api user:       SELECT * FROM dbo.Orders                    -> permission denied (error 229)
-- api user:       EXEC dbo.usp_GetOrdersByCustomer 10         -> works through ownership chaining
```

---

## 🔍 Why This Works (3 lines max)
Permissions are checked on the object the caller touches; when a procedure and its tables have the same owner, the chain is not re-checked on the tables. So callers need EXECUTE only, shrinking attack surface to a small, reviewed API.
हिंदी: Procedure और table का owner एक हो तो table पर दोबारा permission check नहीं होता। इसलिए caller को सिर्फ़ EXECUTE चाहिए।

---

## ⚡ Alternative Solution

```sql
-- Expose a restricted VIEW instead of column grants
CREATE VIEW dbo.vCustomersPublic AS SELECT CustomerId, Name FROM dbo.Customers;
GO
GRANT SELECT ON dbo.vCustomersPublic TO role_reporting;     -- no rights on the base table
-- Dynamic data masking (Q139) or row-level security (Q138) when users must see some data, not all.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: DENY on a role that a sysadmin/db_owner user belongs to expecting it to bind them (owners bypass checks)
-- ❌ Wrong: user in two roles, one GRANT and one DENY: DENY wins, surprising the team
-- ❌ Wrong: ownership chain broken by dynamic SQL (EXEC(@sql) / sp_executesql) or cross-database calls:
--           the caller then needs rights on the tables.
-- ❌ Wrong: GRANT ... WITH GRANT OPTION by default
-- ❌ Wrong: using REVOKE and assuming it blocks; it only removes an explicit entry.
```

---

## 🎯 Interview Tip (1 line)
Say: "Default deny, grant to roles, EXECUTE-only for the app, views/column grants for reporting, and DENY only as an explicit guard rail. I know dynamic SQL breaks ownership chaining, and I verify with fn_my_permissions / EXECUTE AS rather than assuming."

---

## 🔗 Related Questions
→ Q135 (Logins, users and roles) | Q081 (WITH EXECUTE AS) | Q138 (Row-level security) | Q139 (Dynamic data masking)
