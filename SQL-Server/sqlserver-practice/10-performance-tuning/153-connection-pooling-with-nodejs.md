---

# Q153. Connection Pooling with Node.js
# Category: Performance Tuning
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server / Azure SQL with Node.js `mssql` (tedious driver + tarn pool). Not executed against SQL Server; settings per mssql documentation.

---

## ❓ Question
Under load the API logs `Timeout: Request failed to complete` and SQL Server shows thousands of sessions. Show a correct shared-pool setup and explain pool sizing and leak patterns.

---

## 💡 Quick Concept (2 lines only)
Opening a connection is expensive (TCP, TLS, login). `mssql` keeps a pool (default max 10); create ONE pool per process and reuse it. Pool size x app instances must stay below what the database tier can serve.
हिंदी: Pool एक बार बनाओ और पूरे app में reuse करो। हर request पर नया connect = slow + sessions का ढेर।

---

## ✅ Answer / Solution

```js
// db.js - single shared pool (module cache makes it a singleton)
const sql = require('mssql');

const config = {
  server: process.env.DB_SERVER,            // e.g. myserver.database.windows.net
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  options: { encrypt: true, trustServerCertificate: false },
  pool: {
    max: 20,                  // per process; default is 10
    min: 2,
    idleTimeoutMillis: 30000
  },
  connectionTimeout: 15000,   // establishing a connection
  requestTimeout: 30000       // per query
};

const poolPromise = new sql.ConnectionPool(config)
  .connect()
  .then(pool => {
    pool.on('error', err => console.error('pool error', err));
    return pool;
  });

module.exports = { sql, poolPromise };

// usage in a route
// const { sql, poolPromise } = require('./db');
// const pool = await poolPromise;
// const r = await pool.request().input('id', sql.Int, req.params.id)
//                      .query('SELECT OrderId, Amount FROM dbo.Orders WHERE CustomerId = @id');
```

```sql
-- Server side: how many sessions does each app/host hold? (not executed on SQL Server)
SELECT program_name, host_name, COUNT(*) AS sessions
FROM sys.dm_exec_sessions
WHERE is_user_process = 1
GROUP BY program_name, host_name
ORDER BY sessions DESC;
-- EXPECTED OUTPUT: shape only; values depend on your deployment (nothing invented)
-- program_name | host_name | sessions
```

Sizing rule of thumb (arithmetic, not a benchmark): 8 pods x max 20 = 160 possible connections. Check this against the tier's worker/session limits in Azure docs.

---

## 🔍 Why This Works (3 lines max)
A pool amortises login cost and caps concurrency, so bursts queue in Node (visible, tunable) rather than flooding SQL Server. Requests borrow a connection, run, and return it; only `max` queries execute at once per process.
हिंदी: Pool concurrency सीमित करता है। Burst आए तो queue Node में लगती है, database पर नहीं।

---

## ⚡ Alternative Solution

```js
// Wrong tool for transactions? Use the same connection for the whole transaction:
const tx = new sql.Transaction(await poolPromise);
await tx.begin();
try {
  await new sql.Request(tx).input('id', sql.Int, 1).query('UPDATE dbo.Orders SET Status = N''Paid'' WHERE OrderId = @id');
  await tx.commit();
} catch (e) { await tx.rollback(); throw e; }
// Azure SQL: transient errors (e.g. failover) need retry with backoff (Q160); retries must be idempotent.
```

---

## ⚠️ Common Mistake

```js
// ❌ sql.connect() / new ConnectionPool() inside each request handler: a pool per request
// ❌ pool.close() after every query: destroys the pool you wanted
// ❌ Forgetting to end/rollback a transaction on error: connection stays checked out (pool leak)
// ❌ Raising max to "fix" timeouts: moves the queue into SQL Server (blocking, CPU, worker limits)
// ❌ Long-running queries holding connections while the pool is small: increase throughput, not pool size
```

---

## 🎯 Interview Tip (1 line)
Say: "One pool per process, sized from the database's capacity divided by instance count, with timeouts set, pool 'error' handled, transactions always closed in finally, and retry on transient Azure errors. Pool exhaustion usually means slow queries or leaks, not a too-small pool."

---

## 🔗 Related Questions
→ Q159 (Connecting from Node.js) | Q160 (Pooling and retries with mssql) | Q162 (Transactions from Node.js) | Q152 (N+1 problem)
