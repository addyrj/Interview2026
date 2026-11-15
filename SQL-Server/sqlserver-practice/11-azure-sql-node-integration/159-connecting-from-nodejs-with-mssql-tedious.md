---

# Q159. Connecting from Node.js with mssql / tedious
# Category: AZURE SQL + NODE.JS INTEGRATION
# Difficulty: ⭐⭐ Medium
# DB: SQL Server / Azure SQL (Node drivers: `mssql` wraps `tedious`; pg uses `pg`, MySQL uses `mysql2`)

---

## ❓ Question
Connect an Express app to Azure SQL Database using the `mssql` package, run a query, and explain the key connection options (encrypt, trustServerCertificate, timeouts). How do you verify the connection from SQL?

---

## 💡 Quick Concept (2 lines only)
`mssql` is a promise API over the `tedious` TDS driver. Azure SQL requires encrypted connections (`encrypt: true`) and a hostname like `<server>.database.windows.net`; create one pool at startup and reuse it.
हिंदी: `mssql` = `tedious` के ऊपर promise wrapper। Azure SQL में `encrypt: true` ज़रूरी है। Pool एक बार बनाओ और पूरे app में reuse करो।

---

## ✅ Answer / Solution

NOTE: Node code and Azure connectivity not executed here (no SQL Server/Azure available); API usage per `mssql` docs. The T-SQL check parses with sqlglot (tsql).

```js
// db.js  (npm i mssql)
const sql = require('mssql');

const config = {
  server: process.env.SQL_SERVER,              // myserver.database.windows.net
  database: process.env.SQL_DB,
  user: process.env.SQL_USER,                  // better: Entra / managed identity, see Q163
  password: process.env.SQL_PASSWORD,          // from Key Vault / env, never in git
  options: {
    encrypt: true,                             // required for Azure SQL
    trustServerCertificate: false              // keep false in production (validate the cert)
  },
  connectionTimeout: 30000,
  requestTimeout: 15000,
  pool: { max: 10, min: 0, idleTimeoutMillis: 30000 }
};

let poolPromise;
function getPool() {                           // singleton: one pool per process
  if (!poolPromise) poolPromise = new sql.ConnectionPool(config).connect();
  return poolPromise;
}
module.exports = { sql, getPool };

// app.js
app.get('/health/db', async (req, res) => {
  try {
    const pool = await getPool();
    const r = await pool.request().query('SELECT DB_NAME() AS db, SYSDATETIMEOFFSET() AS now');
    res.json(r.recordset[0]);
  } catch (e) { res.status(503).json({ error: 'db unavailable' }); }
});
```

```sql
-- Verify from SQL what the app is connected as and whether the connection is encrypted
SELECT session_id, encrypt_option, auth_scheme, client_net_address
FROM sys.dm_exec_connections
WHERE session_id = @@SPID;
-- Expected for Azure SQL: encrypt_option = TRUE (not executed here; per docs)
```

---

## 🔍 Why This Works (3 lines max)
The pool opens TDS connections on demand up to `max` and reuses them, so each request does not pay TCP+TLS+login cost. Encryption is mandatory for Azure SQL, and certificate validation protects against man-in-the-middle.
हिंदी: Pool connections reuse करता है, हर request पर login का खर्च नहीं। Production में `trustServerCertificate: false` रखो ताकि certificate verify हो।

---

## ⚡ Alternative Solution

```js
// Connection string form
const pool = await sql.connect(
  'Server=tcp:myserver.database.windows.net,1433;Database=OrdersDb;User Id=app;Password=***;Encrypt=true;TrustServerCertificate=false;Connection Timeout=30');
// ORMs (Prisma/TypeORM/Sequelize) use tedious or their own driver underneath - see Q169.
```

---

## ⚠️ Common Mistake

```js
// ❌ Wrong: new ConnectionPool per request (pool leak, exhausts connections, login storm)
app.get('/x', async (req, res) => { const p = await new sql.ConnectionPool(cfg).connect(); ... });
// ❌ Wrong: trustServerCertificate: true "to make the error go away" in production
// ❌ Wrong: hard-coding passwords; or using the admin login for the app
// ❌ Wrong: forgetting the client IP is not in the server firewall (see Q164) -> timeout, not a code bug
// ✅ Single shared pool, secrets from env/Key Vault, least-privilege login
```

---

## 🎯 Interview Tip (1 line)
Say: "One pool per process created at startup, encrypt on with real certificate validation, secrets from Key Vault or better managed identity, explicit timeouts, and a health endpoint — and when connections fail I check the firewall/private endpoint and DNS before touching code."

---

## 🔗 Related Questions
→ Q153 (Connection pooling with Node.js) | Q160 (Pooling and retries) | Q163 (Entra auth) | Q164 (Firewall, private endpoints, TLS)
