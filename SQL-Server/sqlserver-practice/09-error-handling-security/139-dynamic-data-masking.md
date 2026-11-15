
---

# Q139. Dynamic Data Masking
# Category: ERROR HANDLING + SECURITY
# Difficulty: ⭐⭐ Medium
# DB: SQL Server 2016+ and Azure SQL (PostgreSQL needs the anon extension or views; MySQL has no native masking in Community)

---

## ❓ Question
Support agents may look up customers but must see email as `aXXX@XXXX.com`, phone as `XXXX-XXXX-1234` and card numbers fully hidden. Implement dynamic data masking (DDM), show who sees unmasked data, and explain its limits.

---

## 💡 Quick Concept (2 lines only)
DDM masks column values in query RESULTS for users lacking the UNMASK permission, using default(), email(), partial() or random() functions. Data on disk is unchanged, so it is a presentation-layer control, not encryption.
हिंदी: DDM सिर्फ़ query के result में value छुपाता है, disk पर data वैसा ही रहता है। UNMASK permission वाले को असली data दिखता है; यह encryption नहीं है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Customers (
  CustomerId INT IDENTITY(1,1) PRIMARY KEY,
  Name       NVARCHAR(100) NOT NULL,
  Email      NVARCHAR(200) MASKED WITH (FUNCTION = 'email()') NOT NULL,
  Phone      VARCHAR(20)   MASKED WITH (FUNCTION = 'partial(0,"XXXX-XXXX-",4)') NULL,
  CardNo     VARCHAR(19)   MASKED WITH (FUNCTION = 'default()') NULL,
  Score      INT           MASKED WITH (FUNCTION = 'random(1,100)') NULL
);
INSERT INTO dbo.Customers (Name, Email, Phone, CardNo, Score)
VALUES (N'Asha', N'asha@contoso.com', '9876543210', '4111111111111111', 720);
GO

-- ============================================
-- SOLUTION: who sees what
-- ============================================
CREATE USER support_agent WITHOUT LOGIN;
GRANT SELECT ON dbo.Customers TO support_agent;

EXECUTE AS USER = 'support_agent';
  SELECT Name, Email, Phone, CardNo, Score FROM dbo.Customers;     -- masked
REVERT;

GRANT UNMASK TO support_agent;                 -- 2022+: granular on column/table/schema too
-- 2016-2019: UNMASK is database-level only (GRANT UNMASK TO ...)
REVOKE UNMASK FROM support_agent;

-- Add / drop on an existing column
ALTER TABLE dbo.Customers ALTER COLUMN Name ADD MASKED WITH (FUNCTION = 'partial(1,"XXXXX",0)');
ALTER TABLE dbo.Customers ALTER COLUMN Name DROP MASKED;

-- List masked columns
SELECT OBJECT_NAME(object_id) AS TableName, name AS ColumnName, masking_function
FROM sys.masked_columns;
```

```sql
-- EXPECTED OUTPUT
-- Masking is a SQL Server feature with no equivalent engine; not executed on SQL Server. Per Microsoft docs
-- the masked row seen by support_agent is:
-- Name  | Email         | Phone          | CardNo | Score
-- Asha  | aXXX@XXXX.com | XXXX-XXXX-3210 | xxxx   | (random 1-100 each query)
-- Documented formats: email() -> first letter + XXX@XXXX.com ; default() on strings -> XXXX (length rules vary by type);
-- default() on numbers -> 0. Exact CardNo rendering depends on column length; verify in your instance.
```

---

## 🔍 Why This Works (3 lines max)
The engine applies the mask function as the last step of the result set, based on the caller's permissions, with no application change. Table contents and storage are untouched, so jobs and privileged logins still see real data.
हिंदी: Mask result बनने के आख़िर में लगता है और caller की permission देखता है। App बदलने की ज़रूरत नहीं, पर data disk पर असली ही रहता है।

---

## ⚡ Alternative Solution

```sql
-- Need real protection (even from DBAs / backups): Always Encrypted (Q140) or application-layer encryption.
-- Need to hide rows rather than values: row-level security (Q138).
-- Need hiding with logic (show last 4 only for role X): view with CASE + IS_MEMBER
CREATE VIEW dbo.vCustomersSupport AS
SELECT CustomerId, Name,
       CASE WHEN IS_MEMBER('role_fraud') = 1 THEN CardNo ELSE '************' END AS CardNo
FROM dbo.Customers;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: treating DDM as security. A user can infer values by filtering:
--   SELECT * FROM dbo.Customers WHERE Score > 700;    -- predicates run on real data, so ranges leak the value
-- ❌ Wrong: giving the app login db_owner / UNMASK so nothing is ever masked
-- ❌ Wrong: expecting masked data in exports: users with UNMASK, owners and sysadmin always see real values
-- ❌ Wrong: copying masked results with SELECT INTO / INSERT ... SELECT and expecting real data in the copy (it stores the masked text)
```

---

## 🎯 Interview Tip (1 line)
Say: "DDM is a cheap, no-code way to reduce accidental exposure in support tools, but it is obfuscation: brute-force filtering can infer values, so for compliance data I add least privilege, RLS and Always Encrypted or tokenisation, and I keep UNMASK to a small role."

---

## 🔗 Related Questions
→ Q136 (Least-privilege permissions) | Q138 (Row-level security) | Q140 (Always Encrypted and TDE) | Q091 (Views — benefits and limitations)
