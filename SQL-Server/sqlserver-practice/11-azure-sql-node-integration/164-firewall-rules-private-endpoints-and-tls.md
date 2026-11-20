---

# Q164. Firewall Rules, Private Endpoints and TLS
# Category: Azure SQL + Node.js Integration
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (Azure SQL Database). MySQL/PostgreSQL on Azure have the same firewall/Private Link concepts but different T-SQL (no sp_set_firewall_rule).

---

## ❓ Question
Your Node.js API on App Service cannot connect to Azure SQL ("client IP not allowed"), and the security team also wants the database off the public internet. Explain server vs database firewall rules, how Private Endpoint changes the picture, and how to enforce TLS from the app.

---

## 💡 Quick Concept (2 lines only)
Public access is gated by the server-level firewall (IP rules, stored in master) and optional database-level rules; a Private Endpoint gives the server a private IP in your VNet so public access can be turned off entirely. Transport is always encrypted in Azure SQL; the client should set `encrypt: true`, never trust an unknown certificate, and the server can enforce a minimum TLS version.
हिंदी: Firewall = कौन सा IP allow। Private Endpoint = DB का private IP, public बंद। TLS = encrypt true, trustServerCertificate false।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT EXECUTED ON SQL SERVER / AZURE (no Azure instance available here).
-- Syntax parsed with sqlglot (tsql); behaviour per Microsoft docs.
-- ============================================

-- SERVER-LEVEL rule: run in the master database of the logical server
EXECUTE sp_set_firewall_rule
    @name = N'office-bengaluru',
    @start_ip_address = '203.0.113.10',
    @end_ip_address   = '203.0.113.10';

-- List server-level rules (run in master)
SELECT name, start_ip_address, end_ip_address
FROM sys.firewall_rules;

-- DATABASE-LEVEL rule: run in the user database; travels with the DB (e.g. geo-replication/restore)
EXECUTE sp_set_database_firewall_rule
    @name = N'ci-runner',
    @start_ip_address = '198.51.100.20',
    @end_ip_address   = '198.51.100.20';

SELECT name, start_ip_address, end_ip_address
FROM sys.database_firewall_rules;

-- Remove rules when no longer needed
EXECUTE sp_delete_firewall_rule @name = N'office-bengaluru';
EXECUTE sp_delete_database_firewall_rule @name = N'ci-runner';

-- Expected per docs: sys.firewall_rules returns one row per rule, with the IP range you set.
-- (203.0.113.x and 198.51.100.x are documentation-only example ranges.)

-- Private Endpoint + disabling public network access is configured outside T-SQL:
--   az network private-endpoint create ...   (Private Link, port 1433, private DNS zone
--   privatelink.database.windows.net)
--   az sql server update -g rg-shop -n sql-shop-prod --enable-public-network false
```

```javascript
// Node.js: always encrypt, never blindly trust the certificate
const config = {
  server: 'sql-shop-prod.database.windows.net', // resolves to the private IP inside the VNet via private DNS
  database: 'ShopDb',
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  options: {
    encrypt: true,                 // TLS on
    trustServerCertificate: false  // validate the certificate chain
  }
};
```

---

## 🔍 Why This Works (3 lines max)
The firewall evaluates database-level rules first, then server-level rules; a Private Endpoint adds a separate private path, and turning off public access makes IP rules irrelevant for that path. The private DNS zone makes the same server name resolve to the private IP inside your VNet, so connection strings do not change. TLS validation stops man-in-the-middle attacks even on a private network.
हिंदी: Private DNS की वजह से connection string वही रहती है। Public access बंद तो IP rules काम के नहीं। Certificate validate करो।

---

## ⚡ Alternative Solution

```sql
-- Option: service endpoints / VNet rules instead of Private Endpoint (portal/CLI: az sql server vnet-rule create).
-- Option: "Allow Azure services and resources to access this server" = 0.0.0.0 rule
--   convenient but lets ANY Azure customer's IP attempt a login. Prefer Private Endpoint.

-- Enforce minimum TLS version on the server (CLI, not T-SQL):
--   az sql server update -g rg-shop -n sql-shop-prod --minimal-tls-version 1.2
```

---

## ⚠️ Common Mistake

```javascript
// ❌ Wrong: trustServerCertificate: true "to get rid of the cert error" in production
options: { encrypt: true, trustServerCertificate: true }   // disables certificate validation
// ✅ Fix the cause (wrong host name, proxy, missing CA) instead of turning validation off.

// ❌ Wrong: opening 0.0.0.0 - 255.255.255.255 on the firewall while debugging, then forgetting it.
// ❌ Wrong: App Service outbound IPs change/are many - hard-coding one IP breaks later.
// ✅ Use VNet integration + Private Endpoint, or list all possible outbound IPs deliberately.
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "Public IP rules are fine for a dev laptop; production gets a Private Endpoint, public network access disabled, private DNS zone linked to the app's VNet, minimum TLS 1.2, and Entra auth. I verify DNS resolution from the app host with `nslookup` because most 'Private Endpoint doesn't work' tickets are DNS, not the firewall." Also mention that database-level rules are the portable option because they move with a restored or replicated database.

---

## 🔗 Related Questions
→ Q163 (Entra authentication) | Q159 (connecting from Node.js) | Q137 (SQL injection and parameterization) | Q140 (Always Encrypted and TDE concepts) | Q165 (geo-replication and failover groups)
