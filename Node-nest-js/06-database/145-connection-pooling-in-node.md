# 145. Connection Pooling in Node
# हिंदी में: Node में Connection Pooling

---

## 🔵 Simple Definition (English)
**Connection pooling** maintains a pre-established set of reusable database connections ("the pool") instead of opening a new connection for every query. The app borrows a connection from the pool, uses it, and returns it — dramatically reducing the overhead of repeated TCP handshakes and authentication.

## 🔵 सरल परिभाषा (Hindi)
**Connection pooling** reusable database connections का एक pre-established set ("pool") maintain करती है, हर query के लिए नया connection खोलने के बजाय। App pool से एक connection borrow करती है, use करती है, और वापस कर देती है — repeated TCP handshakes और authentication का overhead बहुत कम हो जाता है।

---

## 🔴 Problem it Solves
Opening a database connection involves a TCP handshake + authentication round-trip, taking tens of milliseconds — trivial for ONE request, but devastating at scale (thousands of requests/second each paying this cost). Also, a single shared connection (topic 143's basic pattern) becomes a serialization bottleneck: queries queue up one after another since MySQL connections generally process one query at a time per connection. Connection pooling solves both: connections are created once (upfront or lazily, up to a limit) and REUSED across many requests, while having MULTIPLE connections in the pool allows genuinely concurrent query execution.

## 🔴 यह क्यों बना? (Hindi)
Database connection खोलना TCP handshake + authentication round-trip involve करता है, तेज़ी से costly हो जाता है scale पर (हज़ारों requests/second हर एक यह cost pay करते हुए)। एक single shared connection भी bottleneck बन जाता है — queries एक के बाद एक queue होती हैं। Connection pooling दोनों problems solve करता है — connections एक बार बनते हैं और reuse होते हैं, multiple connections genuinely concurrent execution allow करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → App creates a pool at startup with config: `connectionLimit` (max simultaneous connections, e.g., 10), host/user/password/database
Step 2 → Pool pre-creates some connections (or creates them lazily on first demand, up to the limit) — all authenticated and ready
Step 3 → When code calls `pool.execute(sql)`, the pool internally: grabs an IDLE connection from the pool (or creates a new one if under the limit and none idle), runs the query, then returns the connection to the idle pool automatically
Step 4 → If ALL connections are busy and the limit is reached, new requests QUEUE (wait) until a connection frees up — `waitForConnections: true` (default) handles this gracefully instead of erroring immediately
Step 5 → Pool monitors connection health — if a connection errors/dies, the pool removes it and creates a replacement transparently
Step 6 → For explicit transaction control (BEGIN/COMMIT/ROLLBACK spanning multiple queries), you must get a DEDICATED connection via `pool.getConnection()`, use it for the whole transaction, then release it back manually
Step 7 → Tune `connectionLimit` based on expected concurrency and the DB server's own `max_connections` limit (don't let app pools collectively exceed what the DB server can handle across all app instances)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → App startup पर pool बनाती है `connectionLimit` config के साथ
Step 2 → Pool connections pre-create या lazily create करती है
Step 3 → `pool.execute()` call पर idle connection मिलती है, query चलती है, connection वापस pool में जाती है
Step 4 → Limit पहुंचने पर नए requests queue होते हैं
Step 5 → Dead connections pool automatically replace करता है
Step 6 → Transactions के लिए `pool.getConnection()` से dedicated connection लो
Step 7 → `connectionLimit` को concurrency और DB के `max_connections` के according tune करो

---

## 🟡 Real World Example
**Flipkart's inventory service during a flash sale:** Thousands of concurrent requests check/update product stock simultaneously. A single shared connection would serialize ALL these queries — catastrophic during a sale spike. Instead, the service runs a pool with `connectionLimit: 50` per app instance (across, say, 20 instances = 1000 total connections, tuned against the MySQL server's `max_connections` setting of e.g. 2000, leaving headroom for other services). Queries borrow a connection, execute, and release — allowing genuinely parallel stock checks across many concurrent customers, while the pool queues any requests beyond the 50-connection limit per instance rather than crashing.

## 🟡 Real Example Hindi mein
**Flipkart का inventory service flash sale के दौरान:** हज़ारों concurrent requests stock check/update करती हैं। Single shared connection सब कुछ serialize कर देता। Service pool use करता है `connectionLimit: 50` के साथ, parallel stock checks allow होते हैं, limit से ज़्यादा requests queue होती हैं।

---

## 💻 Code Example — Basic

```javascript
// pool-basic.js — creating and using a connection pool
// Run with: node pool-basic.js (requires running MySQL + npm install mysql2)

const mysql = require('mysql2/promise');

// ─── 1. CREATE A POOL (once, at app startup) ─────────────────────────────────
const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: 'password',
  database: 'shop',
  waitForConnections: true,   // queue requests if pool is at capacity, don't error immediately
  connectionLimit: 10,         // max simultaneous connections in this pool
  queueLimit: 0,                // 0 = unlimited queued requests (be cautious in production)
});

async function main() {
  // ─── 2. USE THE POOL DIRECTLY — no need to manually get/release for simple queries ──
  // pool.execute() automatically borrows AND returns a connection internally
  const [products] = await pool.execute('SELECT * FROM products LIMIT 5');
  console.log('Products:', products.length);

  // ─── 3. SIMULATE CONCURRENT QUERIES (this is where pooling shines) ──────────
  const queries = Array.from({ length: 20 }, (_, i) =>
    pool.execute('SELECT * FROM products WHERE id = ?', [i + 1])
  );
  const results = await Promise.all(queries);  // all 20 run concurrently, sharing 10 connections
  console.log(`Ran ${results.length} concurrent queries using a pool of 10 connections`);

  await pool.end();  // closes ALL connections in the pool
}

main().catch(console.error);
```

## 💻 Code Example — Advanced

```javascript
// pool-advanced.js — explicit connection checkout for transactions + pool monitoring

const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 20,
  queueLimit: 50,              // cap queued requests — reject beyond this instead of unbounded growth
  enableKeepAlive: true,        // periodic pings to prevent idle connections being dropped by MySQL/firewall
  keepAliveInitialDelay: 10000,
});

// ─── 1. TRANSACTIONS REQUIRE A DEDICATED CONNECTION (not pool.execute directly) ─
async function transferStock(fromWarehouseId, toWarehouseId, productId, quantity) {
  const connection = await pool.getConnection();  // checkout ONE specific connection from the pool
  try {
    await connection.beginTransaction();

    const [[source]] = await connection.execute(
      'SELECT stock FROM warehouse_stock WHERE warehouse_id = ? AND product_id = ? FOR UPDATE',
      [fromWarehouseId, productId]
    );
    if (!source || source.stock < quantity) {
      throw new Error('Insufficient stock at source warehouse');
    }

    await connection.execute(
      'UPDATE warehouse_stock SET stock = stock - ? WHERE warehouse_id = ? AND product_id = ?',
      [quantity, fromWarehouseId, productId]
    );
    await connection.execute(
      'UPDATE warehouse_stock SET stock = stock + ? WHERE warehouse_id = ? AND product_id = ?',
      [quantity, toWarehouseId, productId]
    );

    await connection.commit();
    return { success: true };
  } catch (err) {
    await connection.rollback();
    throw err;
  } finally {
    connection.release();  // CRITICAL: always return the connection to the pool, even on error
  }
}

// ─── 2. POOL HEALTH MONITORING ────────────────────────────────────────────────
function logPoolStats() {
  // mysql2 pool exposes internal counts (implementation detail, varies by version)
  const poolAny = pool.pool || pool;  // access underlying pool state
  console.log(
    `Pool stats — active: ${poolAny._allConnections?.length || 'n/a'}, ` +
    `idle: ${poolAny._freeConnections?.length || 'n/a'}, ` +
    `queued: ${poolAny._connectionQueue?.length || 'n/a'}`
  );
}

setInterval(logPoolStats, 30000);  // log every 30s for observability

module.exports = { pool, transferStock };
```

---

## 🟠 Express.js Integration

```javascript
// server.js
const express = require('express');
const mysql = require('mysql2/promise');

const app = express();
app.use(express.json());

const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectionLimit: 15,
  waitForConnections: true,
});

// Simple queries: use pool directly (pool handles checkout/release automatically)
app.get('/products', async (req, res) => {
  try {
    const [products] = await pool.execute('SELECT * FROM products LIMIT 20');
    res.json(products);
  } catch (err) {
    res.status(500).json({ error: 'Query failed' });
  }
});

// Transactions: explicitly checkout a connection, ALWAYS release in finally
app.post('/orders', async (req, res) => {
  const { productId, quantity, customerId } = req.body;
  const connection = await pool.getConnection();

  try {
    await connection.beginTransaction();
    const [[product]] = await connection.execute(
      'SELECT stock, price FROM products WHERE id = ? FOR UPDATE',
      [productId]
    );
    if (!product || product.stock < quantity) {
      await connection.rollback();
      return res.status(400).json({ error: 'Insufficient stock' });
    }
    await connection.execute('UPDATE products SET stock = stock - ? WHERE id = ?', [quantity, productId]);
    const [result] = await connection.execute(
      'INSERT INTO orders (product_id, customer_id, quantity) VALUES (?, ?, ?)',
      [productId, customerId, quantity]
    );
    await connection.commit();
    res.status(201).json({ orderId: result.insertId });
  } catch (err) {
    await connection.rollback();
    res.status(500).json({ error: 'Order failed' });
  } finally {
    connection.release();  // return to pool regardless of success/failure
  }
});

// Health check: verify pool can still get a connection
app.get('/health', async (req, res) => {
  try {
    const connection = await pool.getConnection();
    connection.release();
    res.json({ status: 'ok' });
  } catch {
    res.status(503).json({ status: 'db unreachable' });
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));

process.on('SIGTERM', async () => {
  await pool.end();
  process.exit(0);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to release a manually-checked-out connection
```javascript
// WRONG: connection.release() missing in error path — connection leaks, pool exhausts over time
async function badTransaction() {
  const connection = await pool.getConnection();
  await connection.beginTransaction();
  await connection.execute('UPDATE ...');  // if this throws, release() never runs!
  await connection.commit();
  connection.release();
}

// CORRECT: ALWAYS release in a finally block, regardless of success or failure
async function goodTransaction() {
  const connection = await pool.getConnection();
  try {
    await connection.beginTransaction();
    await connection.execute('UPDATE ...');
    await connection.commit();
  } catch (err) {
    await connection.rollback();
    throw err;
  } finally {
    connection.release();  // guaranteed to run
  }
}
```

❌ Mistake 2: Setting `connectionLimit` too high without considering total across all instances
```javascript
// WRONG: 20 app instances × connectionLimit: 100 = 2000 potential connections
// MySQL server's max_connections might be set to only 500 — pool creation starts failing!
const pool = mysql.createPool({ connectionLimit: 100, ...config });  // per instance!

// CORRECT: calculate total capacity across ALL instances, leave headroom
// If max_connections = 500, and you run 20 instances, budget ~20 per instance (400 total, 100 headroom)
const pool = mysql.createPool({ connectionLimit: 20, ...config });
```

---

## 🧠 Tricky Interview Question

```javascript
const pool = mysql.createPool({ connectionLimit: 2, waitForConnections: true });

async function slowQuery() {
  const conn = await pool.getConnection();
  await new Promise((r) => setTimeout(r, 5000));  // simulate a slow query, 5 seconds
  conn.release();
}

slowQuery();
slowQuery();
slowQuery();  // third call — what happens?
console.log('All three calls issued');
```
Answer: The pool has `connectionLimit: 2`. The first two `slowQuery()` calls each immediately grab one of the 2 available connections and start their 5-second "query." The THIRD call's `pool.getConnection()` call does NOT throw or fail immediately — because `waitForConnections: true` (the default), it instead QUEUES, waiting for one of the first two connections to be released. `console.log('All three calls issued')` prints right away (synchronously, since none of these are awaited at the top level) — but the third `slowQuery()`'s internal `await pool.getConnection()` won't resolve until ~5 seconds later when one of the first two connections releases. This demonstrates the pool's queuing behavior: it gracefully backpressures excess demand rather than failing outright, as long as `queueLimit` isn't exceeded.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `pool.execute()` and `pool.getConnection()` + `connection.execute()`?
A1: `pool.execute(sql, params)` is a convenience method: internally it checks out a connection, runs the query, and releases the connection back automatically — ideal for single, standalone queries with no cross-query state needed. `pool.getConnection()` explicitly checks out ONE specific connection object that you hold onto and reuse across MULTIPLE queries — required for transactions (BEGIN/COMMIT need to run on the SAME connection) or any scenario needing session-level state (like `SET @variable` or temporary tables scoped to a session). You MUST manually call `.release()` when done with a connection obtained via `getConnection()`.

Q2: What happens if a query fails to release its connection back to the pool — what's the symptom under load?
A2: The pool's available connections gradually shrink as "leaked" connections stay checked out forever (never released), even though they're not actually doing anything anymore. Under sustained load, eventually ALL connections in the pool become checked-out/leaked, and new requests calling `pool.getConnection()` queue indefinitely (or time out, if a connection timeout is configured) — manifesting as the app appearing to "hang" or become unresponsive even though the database itself is healthy. This is a classic production incident pattern: "connection pool exhaustion" from a missing `finally { connection.release() }`.

Q3: How do you decide the right `connectionLimit` for a connection pool?
A3: Consider: (1) the database server's own `max_connections` limit, divided by the number of app instances that will each have their own pool (leaving headroom for other services/admin connections); (2) your app's actual concurrency needs — CPU-bound Node apps rarely need huge pools since Node itself processes requests somewhat serially per event loop tick for non-I/O work; (3) empirically test under realistic load — too small causes queuing/latency, too large wastes DB server resources and can even DEGRADE performance (context-switching overhead on the DB server with too many simultaneous connections). A common starting point is 10-20 per instance, tuned based on load testing.

Q4: Does a connection pool help with database CPU/disk bottlenecks?
A4: No — pooling only reduces the OVERHEAD of connection establishment (TCP handshake, auth) and allows CONCURRENT query execution instead of serializing on one connection. If the database itself is CPU-bound (complex queries, missing indexes) or disk I/O-bound, adding more pooled connections won't help and can actually make it WORSE (more concurrent queries competing for the same limited DB server resources, increasing contention/lock waits). Pooling solves a connection-overhead and concurrency problem, not a query-performance or database-capacity problem — those need query optimization, indexing, or scaling the DB itself.

Q5: What's `queueLimit` and why would you set it to a non-zero, bounded value in production?
A5: `queueLimit` caps how many pending `getConnection()` requests can queue once all pool connections are busy; `0` means unlimited queuing. In production, an UNBOUNDED queue under a traffic spike can cause memory to grow unboundedly (holding thousands of pending Promise objects and their associated request contexts) and users experience ever-increasing latency with no fast failure. Setting a bounded `queueLimit` (e.g., 50-100) makes the pool FAIL FAST once truly overwhelmed (clients get an immediate error to retry/backoff) rather than degrading into unbounded memory growth and silent, ever-growing latency.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production app serving concurrent HTTP requests that query a relational database — pooling is essentially mandatory, not optional.

❌ Avoid when:
- A one-off script or migration tool that runs a handful of sequential queries and exits — a single connection is simpler and sufficient there, pooling adds unnecessary complexity.

---

## 📊 Visual Diagram

```
CONNECTION POOL LIFECYCLE:
──────────────────────────────────────────────────────────

  Pool created (connectionLimit: 10)
       │
       ▼
  [idle][idle][idle]...[idle]   (up to 10 connections, created lazily or upfront)
       │
  Request A: pool.execute() ──► borrows conn #1 ──► runs query ──► returns conn #1 to idle
  Request B: pool.getConnection() ──► borrows conn #2 (for transaction) ──► ... ──► connection.release()
       │
  If all 10 busy:
  Request K: getConnection() ──► QUEUED (waitForConnections: true) ──► waits for a release
       │
  Connection dies (network blip):
  Pool detects error ──► removes dead connection ──► creates replacement transparently
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Connection pool | Reusable set of pre-established DB connections | Pre-established DB connections का reusable set |
| connectionLimit | Max simultaneous connections in the pool | Pool में max simultaneous connections |
| Checkout/Release | Borrowing and returning a connection | Connection borrow करना और वापस करना |
| Connection leak | Checked-out connection never released | Checked-out connection कभी release न होना |
| Queueing | Waiting for a free connection when pool is full | Pool full होने पर free connection के लिए wait करना |
| Pool exhaustion | All connections busy/leaked, new requests stall | सभी connections busy/leaked, नए requests stall |

---

## ⚡ 3-Line Summary
English:
1. Connection pooling reuses a fixed set of pre-established DB connections across requests, avoiding the cost of repeated handshakes and enabling true query concurrency.
2. Use `pool.execute()` for standalone queries (auto checkout/release) and `pool.getConnection()` + manual `release()` for transactions.
3. Always release checked-out connections in a `finally` block, and size `connectionLimit` based on both app concurrency needs and the DB server's total connection capacity.

Hindi:
1. Connection pooling pre-established DB connections के fixed set को reuse करती है, handshakes का cost बचाती है, true query concurrency enable करती है।
2. Standalone queries के लिए `pool.execute()`, transactions के लिए `pool.getConnection()` + manual `release()` use करो।
3. Checked-out connections को हमेशा `finally` block में release करो, `connectionLimit` को app concurrency और DB capacity के according size करो।

---

## ➡️ Next Topic
**146. Raw Queries vs ORM** — कब direct SQL लिखो, कब ORM use करो — trade-offs।
