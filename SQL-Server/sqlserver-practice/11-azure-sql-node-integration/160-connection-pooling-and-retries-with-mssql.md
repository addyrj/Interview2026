---

# Q160. Connection Pooling and Retries with mssql
# Category: AZURE SQL + NODE.JS INTEGRATION
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server / Azure SQL (error numbers below are the commonly documented transient ones; verify against current Azure docs)

---

## ❓ Question
Azure SQL connections occasionally fail with transient errors (failover, scaling, throttling). Configure pooling sensibly and write a retry wrapper in Node.js that retries only transient errors with exponential backoff and jitter.

---

## 💡 Quick Concept (2 lines only)
Azure SQL can drop connections during maintenance, failover or scale operations, so apps must treat some errors as transient and retry the whole unit of work. Pool size must also stay under what the database tier allows (max workers/sessions).
हिंदी: Azure में failover/scale के समय connection टूट सकता है। सिर्फ transient errors पर exponential backoff + jitter के साथ retry करो, और pool size tier की limit से कम रखो।

---

## ✅ Answer / Solution

NOTE: not executed (no SQL Server/Azure here). Error numbers are Microsoft-documented transient codes; confirm the list in current docs before relying on it. Retry logic itself is plain JavaScript.

```js
const TRANSIENT = new Set([4060, 40197, 40501, 40613, 49918, 49919, 49920, 10928, 10929, 1205]);
// 40613 db unavailable, 40501 throttled, 40197 service error, 10928/10929 resource limits,
// 1205 deadlock victim (safe to retry only if the whole transaction is retried)

const isTransient = (e) =>
  TRANSIENT.has(e?.number) ||
  ['ETIMEOUT', 'ESOCKET', 'ECONNRESET', 'ECONNCLOSED'].includes(e?.code);

async function withRetry(fn, { retries = 4, baseMs = 200 } = {}) {
  for (let attempt = 0; ; attempt++) {
    try { return await fn(); }
    catch (e) {
      if (attempt >= retries || !isTransient(e)) throw e;
      const delay = Math.min(5000, baseMs * 2 ** attempt) * (0.5 + Math.random()); // jitter
      await new Promise(r => setTimeout(r, delay));
    }
  }
}

// usage: retry a read, or a whole transaction function (Q162)
const rows = await withRetry(async () => {
  const pool = await getPool();
  return (await pool.request().input('id', sql.Int, 42)
           .query('SELECT OrderId, Total FROM dbo.Orders WHERE CustomerId = @id')).recordset;
});

// Pool settings (mssql uses tarn.js): keep max * (app instances) below the tier's connection limits
// pool: { max: 10, min: 2, idleTimeoutMillis: 30000, acquireTimeoutMillis: 15000 }
```

```sql
-- Server side: how many sessions are we really using? (DMV; verify columns in docs)
SELECT COUNT(*) AS sessions FROM sys.dm_exec_sessions WHERE is_user_process = 1;
```

---

## 🔍 Why This Works (3 lines max)
Only errors known to be temporary are retried, a limited number of times, with exponential delay plus jitter so many instances do not hammer the server in lockstep. Retrying inside a pool is safe because a broken connection is discarded and a new one is opened.
हिंदी: सिर्फ अस्थायी errors retry होते हैं, limit के साथ। Jitter से सारे instances एक साथ नहीं टकराते।

---

## ⚡ Alternative Solution

```js
// Use a battle-tested library for the loop (e.g. 'p-retry', 'async-retry') or a resilience policy (cockatiel).
// Driver-level: tedious has connect retry options (e.g. connectTimeout / cancelTimeout) - check docs for your version.
// Azure SQL "connection resiliency": newer driver stacks can auto-reconnect idle connections; do not rely on it for in-flight work.
```

---

## ⚠️ Common Mistake

```js
// ❌ Wrong: retry every error (syntax error, constraint violation, login failure) -> infinite pointless load
// ❌ Wrong: retrying a non-idempotent INSERT/payment after a timeout -> duplicates
//           ✅ add an idempotency key / unique constraint, or check state before re-running
// ❌ Wrong: retrying only the failed statement inside a transaction (the txn is already rolled back)
// ❌ Wrong: pool max = 100 on 20 app instances -> 2000 connections hits the tier limits (error 10928/10929 style)
```

---

## 🎯 Interview Tip (1 line)
Say: "Retry only documented transient errors, bounded, with backoff and jitter, at the transaction boundary, and only for idempotent work or with an idempotency key; and I size pools as max-per-instance times instance count against the tier's limits, with timeouts so a sick database fails fast instead of piling up requests."

---

## 🔗 Related Questions
→ Q130 (Retry for deadlock victims) | Q153 (Connection pooling with Node.js) | Q159 (Connecting with mssql) | Q162 (Transactions from Node.js)
