
---

# Q135. Logins, Users and Roles
# Category: ERROR HANDLING + SECURITY
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (not executed on SQL Server; no equivalent engine; behaviour per Microsoft docs)

---

## ❓ Question
Create access for a Node.js API service that must read and write the `Orders` database but never alter schema. Explain server-level login vs database-level user, fixed database roles, contained users (Azure SQL) and orphaned users.

---

## 💡 Quick Concept (2 lines only)
A LOGIN authenticates at the server (master); a USER maps that login inside one database and holds permissions. Put users in roles (custom or fixed like db_datareader) rather than granting directly. In Azure SQL Database use contained database users or Entra identities.
हिंदी: LOGIN server स्तर पर पहचान देता है, USER database के अंदर permission रखता है। Permission सीधे user को नहीं, role को दो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- ON-PREM / MANAGED INSTANCE / VM
-- ============================================
USE master;
CREATE LOGIN app_orders_api WITH PASSWORD = N'<<generate-strong-secret>>', CHECK_POLICY = ON;

USE OrdersDb;
CREATE USER app_orders_api FOR LOGIN app_orders_api;

-- custom role instead of db_owner
CREATE ROLE role_orders_rw;
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO role_orders_rw;
ALTER ROLE role_orders_rw ADD MEMBER app_orders_api;

-- ============================================
-- AZURE SQL DATABASE: contained user (no login in master)
-- ============================================
-- run inside the user database:
CREATE USER app_orders_api WITH PASSWORD = N'<<generate-strong-secret>>';
-- better: Microsoft Entra identity / managed identity (no password to store):
CREATE USER [my-orders-api-app] FROM EXTERNAL PROVIDER;
ALTER ROLE role_orders_rw ADD MEMBER [my-orders-api-app];

-- ============================================
-- INSPECT who is in which role
-- ============================================
SELECT r.name AS RoleName, m.name AS MemberName
FROM sys.database_role_members rm
JOIN sys.database_principals r ON r.principal_id = rm.role_principal_id
JOIN sys.database_principals m ON m.principal_id = rm.member_principal_id;

-- ============================================
-- ORPHANED USER after restoring to another server (SID mismatch)
-- ============================================
ALTER USER app_orders_api WITH LOGIN = app_orders_api;   -- remap, preferred over sp_change_users_login
```

```sql
-- EXPECTED OUTPUT
-- Not executed on SQL Server. Expected shape of the role-membership query:
-- RoleName       | MemberName
-- role_orders_rw | app_orders_api
-- (fixed roles such as db_owner also appear if members exist; list depends on the database)
```

| Fixed database role | Use |
|---|---|
| db_datareader / db_datawriter | read / write all user tables (broad) |
| db_ddladmin | schema changes (avoid for app accounts) |
| db_owner | everything in the database (never for an app) |

---

## 🔍 Why This Works (3 lines max)
The app identity can connect and do DML only through the role, so a stolen credential cannot drop tables or read other databases. Contained users travel with the database in restores and failovers, which is why Azure SQL favours them.
हिंदी: App सिर्फ़ role के ज़रिये DML कर सकता है, इसलिए credential चोरी होने पर भी tables drop नहीं होंगी। Contained user database के साथ ही चलता है।

---

## ⚡ Alternative Solution

```sql
-- Windows/Entra group instead of individual accounts: add people to the group, grant the group once.
CREATE USER [corp\orders-developers] FROM EXTERNAL PROVIDER;      -- Azure SQL with Entra group
-- Separate accounts per purpose: app_orders_api (DML), app_orders_migrator (DDL, used only by CI), reporting_ro (read).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: connecting the app as sa / db_owner "because it works"
-- ❌ Wrong: shared password in source control; use Key Vault or a managed identity.
-- ❌ Wrong: CREATE USER with no login on a restored database, then wondering why the old login cannot connect (orphan).
-- ❌ Wrong: granting to individual users instead of roles, making audits impossible.
-- ❌ Wrong: confusing server roles (sysadmin, dbcreator) with database roles; Azure SQL Database has no sysadmin.
```

---

## 🎯 Interview Tip (1 line)
Say: "Separate identities per purpose, permissions through roles, Entra managed identity for the Node app so there is no password at all, and the migration account is the only one with DDL. I audit membership with sys.database_role_members and review orphaned users after every restore."

---

## 🔗 Related Questions
→ Q136 (Least-privilege permissions) | Q163 (Azure AD authentication and managed identity) | Q164 (Firewall, private endpoints, TLS) | Q081 (WITH EXECUTE AS)
