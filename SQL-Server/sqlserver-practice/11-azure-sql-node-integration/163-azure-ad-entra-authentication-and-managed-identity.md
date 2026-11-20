---

# Q163. Azure AD (Entra) Authentication and Managed Identity
# Category: Azure SQL + Node.js Integration
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (Azure SQL Database). MySQL/PostgreSQL: Azure Database for MySQL/PostgreSQL also support Entra tokens, but the user-creation syntax differs.

---

## ❓ Question
Your Express API on Azure App Service currently connects to Azure SQL with a SQL login and password stored in app settings. Security wants no passwords anywhere. Show how to (1) set up a Microsoft Entra admin, (2) create a contained database user for the app's managed identity with least privilege, and (3) connect from Node.js with the `mssql` package using a token.

---

## 💡 Quick Concept (2 lines only)
Managed identity = an identity Azure creates for your App Service/VM; it fetches short-lived Entra access tokens, so no secret exists to leak or rotate. The database maps that identity to a contained user created `FROM EXTERNAL PROVIDER`, and the app presents the token as its login.
हिंदी: Managed identity = password-less login। Azure खुद token देता है। DB में `CREATE USER ... FROM EXTERNAL PROVIDER` से user बनता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT EXECUTED ON SQL SERVER / AZURE: there is no Azure SQL instance in the
-- authoring environment. Syntax checked with sqlglot (tsql); behaviour per Microsoft docs.
-- ============================================

-- STEP 1 (portal / CLI, not T-SQL): set a Microsoft Entra admin on the logical server.
--   az sql server ad-admin create --resource-group rg-shop --server-name sql-shop-prod ^
--       --display-name "DBA Group" --object-id <entra-group-object-id>

-- STEP 2: connect to the USER DATABASE (not master) as the Entra admin, then run:
-- (CREATE USER ... FROM EXTERNAL PROVIDER cannot be run while connected with a SQL login)

CREATE USER [app-shop-api] FROM EXTERNAL PROVIDER;
-- [app-shop-api] = name of the App Service (system-assigned identity) or user-assigned identity

-- Least privilege: read/write data, no schema changes
ALTER ROLE db_datareader ADD MEMBER [app-shop-api];
ALTER ROLE db_datawriter ADD MEMBER [app-shop-api];
GRANT EXECUTE ON SCHEMA::dbo TO [app-shop-api];   -- allow calling stored procedures

-- Verify (expected: one row per member, names depend on your server)
SELECT dp.name AS UserName, dp.type_desc, dp.authentication_type_desc
FROM sys.database_principals AS dp
WHERE dp.name = N'app-shop-api';
-- Expected (per docs): type_desc = EXTERNAL_USER

-- Optional: drop the old SQL login user once the app is switched
-- DROP USER [shop_app_sql_user];
```

```javascript
// db.js : Node.js + mssql + @azure/identity (token-based, no password)
const sql = require('mssql');
const { DefaultAzureCredential } = require('@azure/identity');

const credential = new DefaultAzureCredential(); // managed identity in Azure, `az login` on laptop

async function getPool() {
  const token = await credential.getToken('https://database.windows.net/.default');
  return new sql.ConnectionPool({
    server: 'sql-shop-prod.database.windows.net',
    database: 'ShopDb',
    authentication: {
      type: 'azure-active-directory-access-token',
      options: { token: token.token }
    },
    options: { encrypt: true, trustServerCertificate: false }
  }).connect();
}
module.exports = { getPool };
```

---

## 🔍 Why This Works (3 lines max)
The identity gets an Entra token for the audience `https://database.windows.net/`, Azure SQL validates it, and maps its name to the contained user you created, so permissions come from normal database roles. No password exists in config, and tokens expire (about an hour), so a leak has a short blast radius. Tokens expire, so a long-lived pool must re-acquire tokens for new connections.
हिंदी: Token expire होता है, इसलिए leak का नुकसान कम। Permissions DB roles से आते हैं। Long-running pool में नया token लेना याद रखो।

---

## ⚡ Alternative Solution

```javascript
// Let tedious (inside mssql) fetch the managed identity token itself.
// Type names depend on the tedious/mssql version -- check your installed version's docs.
const config = {
  server: 'sql-shop-prod.database.windows.net',
  database: 'ShopDb',
  authentication: {
    type: 'azure-active-directory-default'   // tries managed identity, env vars, az login
  },
  options: { encrypt: true }
};
// Simpler code, but you control token refresh less than with an explicit token.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: running CREATE USER ... FROM EXTERNAL PROVIDER in master, or while connected
--    with a SQL login. It fails: you must be connected as an Entra principal, in the target DB.

-- ❌ Wrong: granting db_owner "to make it work"
ALTER ROLE db_owner ADD MEMBER [app-shop-api];
-- ✅ datareader/datawriter + EXECUTE on schema (or on specific procedures only)

-- ❌ Wrong: caching one token in a global variable forever -> app breaks after token expiry.
-- ✅ Call credential.getToken() per new connection (the SDK caches and refreshes it for you).
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "I make a group the Entra admin, not a person, then create a contained user per app identity with db roles scoped to what it needs. In Node I use DefaultAzureCredential so the same code works with managed identity in Azure and `az login` locally. I treat token expiry as a real failure mode in long-lived pools. Dev, test and prod each get separate identities." Mention that system-assigned identities die with the resource, while user-assigned ones can be reused across apps.

---

## 🔗 Related Questions
→ Q135 (logins, users and roles) | Q136 (least-privilege permissions) | Q159 (connecting from Node.js) | Q160 (pooling and retries) | Q164 (firewall and TLS)
