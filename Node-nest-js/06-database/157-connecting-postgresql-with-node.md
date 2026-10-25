# 157. Connecting PostgreSQL with Node
# हिंदी में: Node के साथ PostgreSQL Connect करना

---

## 🔵 Simple Definition (English)
Connecting PostgreSQL with Node.js means establishing a network connection from your Node app to a PostgreSQL database server using a driver (most commonly the `pg` package), configuring credentials/host/port via environment variables, and using a **connection pool** (not a single connection) so multiple concurrent requests can query the DB efficiently without exhausting resources.

## 🔵 सरल परिभाषा (Hindi)
Node.js को PostgreSQL से connect करने का मतलब है Node app से PostgreSQL database server तक network connection बनाना (आमतौर पर `pg` package से), credentials/host/port environment variables से configure करना, और **connection pool** (सिर्फ एक connection नहीं) use करना ताकि कई concurrent requests efficiently query कर सकें बिना resources खत्म किए।

---

## 🔴 Problem it Solves
Opening a brand-new TCP connection to PostgreSQL for every single query is slow (TCP handshake + auth overhead on every request) and can quickly exhaust PostgreSQL's `max_connections` limit under load, causing "too many connections" errors and app crashes. A connection pool solves this by keeping a fixed number of connections open and ready, handing them out to queries as needed and returning them to the pool afterward — reusing connections instead of creating new ones constantly.

## 🔴 यह क्यों बना? (Hindi)
हर query के लिए नया TCP connection खोलना slow है (हर request पर handshake + auth overhead) और load में PostgreSQL की `max_connections` limit खत्म हो सकती है, "too many connections" errors और app crash। Connection pool इसे solve करता है — fixed number of connections खुले रखता है, queries को देता है, फिर वापस pool में — connections reuse होते हैं, बार-बार नए नहीं बनते।

---

## 🟢 How it Works — Step by Step

Step 1 → Install the driver: `npm install pg`.
Step 2 → Create a `Pool` instance with connection config (host, port, user, password, database) — ideally from environment variables, never hardcoded.
Step 3 → The pool pre-opens (or lazily opens, up to a `max` limit) several TCP connections to PostgreSQL.
Step 4 → Call `pool.query(sql, params)` — the pool grabs a free connection, runs the query, and automatically releases the connection back to the pool.
Step 5 → For multi-statement transactions, manually check out a client with `pool.connect()`, run queries on it, then `client.release()` when done.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Driver install करो: `npm install pg`।
Step 2 → `Pool` instance बनाओ connection config के साथ (host, port, user, password, database) — environment variables से, hardcode मत करो।
Step 3 → Pool कई TCP connections pre-open करता है (`max` limit तक)।
Step 4 → `pool.query(sql, params)` call करो — pool free connection देता है, query चलती है, connection वापस pool में जाता है।
Step 5 → Multi-statement transactions के लिए `pool.connect()` से client manually checkout करो, queries चलाओ, फिर `client.release()` करो।

---

## 🟡 Real World Example
**Razorpay's payments database layer** uses a single shared `pg.Pool` per service instance, configured with `max: 20` connections and strict `idleTimeoutMillis`/`connectionTimeoutMillis` settings. Under high transaction volume (payment processing spikes during sales events), the pool queues incoming queries rather than opening unbounded new connections — protecting the PostgreSQL server from being overwhelmed, while the app still handles thousands of requests per second by reusing the 20 pooled connections efficiently.

## 🟡 Real Example Hindi mein
**Razorpay की payments database layer** हर service instance में एक shared `pg.Pool` use करती है (`max: 20` connections के साथ)। High transaction volume में (sale events के दौरान), pool आने वाली queries को queue करता है unbounded नए connections खोलने के बजाय — PostgreSQL server को overwhelm होने से बचाता है, फिर भी app हज़ारों requests/second handle करता है 20 pooled connections reuse करके।

---

## 💻 Code Example — Basic

```javascript
// pg-basic.js
// npm install pg
// Requires a running PostgreSQL instance; set env vars or edit config directly
const { Pool } = require('pg');

// Create a connection pool — read config from environment variables (best practice)
const pool = new Pool({
  host: process.env.PGHOST || 'localhost',
  port: Number(process.env.PGPORT) || 5432,
  user: process.env.PGUSER || 'postgres',
  password: process.env.PGPASSWORD || 'postgres',
  database: process.env.PGDATABASE || 'myapp',
  max: 10,                       // max number of clients in the pool
  idleTimeoutMillis: 30000,      // close idle clients after 30s
  connectionTimeoutMillis: 5000, // error if can't connect within 5s
});

async function main() {
  try {
    // pool.query() automatically acquires + releases a connection
    const createTable = `
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        name TEXT
      );
    `;
    await pool.query(createTable);

    // Parameterized query — $1, $2 placeholders prevent SQL injection
    const insertResult = await pool.query(
      'INSERT INTO users (email, name) VALUES ($1, $2) RETURNING *',
      ['rahul@example.com', 'Rahul']
    );
    console.log('Inserted:', insertResult.rows[0]);

    const selectResult = await pool.query('SELECT * FROM users WHERE email = $1', ['rahul@example.com']);
    console.log('Found:', selectResult.rows);
  } catch (err) {
    console.error('DB error:', err.message);
  } finally {
    await pool.end(); // close all connections when the script is done (don't do this in a long-running server)
  }
}

main();
```

## 💻 Code Example — Advanced

```javascript
// pg-advanced.js — Production patterns: transactions, error handling, graceful shutdown
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL, // e.g. postgres://user:pass@host:5432/dbname
  max: 20,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

// Log pool-level errors (e.g., a connection dropped unexpectedly) to avoid crashing the process
pool.on('error', (err) => {
  console.error('Unexpected PG pool error:', err.message);
});

// Transaction helper — checks out a dedicated client for multi-statement atomicity
async function transferFunds(fromId, toId, amount) {
  const client = await pool.connect(); // check out a single connection from the pool
  try {
    await client.query('BEGIN');

    const { rows } = await client.query('SELECT balance FROM wallets WHERE id = $1 FOR UPDATE', [fromId]);
    // "FOR UPDATE" locks the row to prevent concurrent modification (race condition safety)

    if (!rows.length || rows[0].balance < amount) {
      throw new Error('Insufficient balance');
    }

    await client.query('UPDATE wallets SET balance = balance - $1 WHERE id = $2', [amount, fromId]);
    await client.query('UPDATE wallets SET balance = balance + $1 WHERE id = $2', [amount, toId]);

    await client.query('COMMIT');
    return { success: true };
  } catch (err) {
    await client.query('ROLLBACK'); // undo all changes in this transaction on any failure
    throw err;
  } finally {
    client.release(); // ALWAYS release the client back to the pool, even on error
  }
}

// Graceful shutdown — important for containerized deployments (SIGTERM handling)
process.on('SIGTERM', async () => {
  console.log('Closing PG pool before shutdown...');
  await pool.end();
  process.exit(0);
});

async function run() {
  try {
    await transferFunds(1, 2, 500);
    console.log('Transfer completed');
  } catch (err) {
    console.error('Transfer failed:', err.message);
  }
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express app sharing a single pg Pool across all routes
const express = require('express');
const { Pool } = require('pg');

const app = express();
app.use(express.json());

// Create pool ONCE, at module load — shared across every request
const pool = new Pool({ connectionString: process.env.DATABASE_URL, max: 20 });

app.get('/api/users/:id', async (req, res) => {
  try {
    const { rows } = await pool.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
    if (!rows.length) return res.status(404).json({ error: 'Not found' });
    res.json(rows[0]);
  } catch (err) {
    res.status(500).json({ error: 'Database query failed' });
  }
});

app.get('/health/db', async (req, res) => {
  try {
    await pool.query('SELECT 1'); // simple connectivity check
    res.json({ db: 'connected', poolTotal: pool.totalCount, poolIdle: pool.idleCount });
  } catch {
    res.status(503).json({ db: 'disconnected' });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Creating a new `Pool` per request
```javascript
// Wrong — exhausts PostgreSQL max_connections quickly under load
app.get('/users', async (req, res) => {
  const pool = new Pool({...}); // new pool EVERY request!
  res.json(await pool.query('SELECT * FROM users'));
});

// Right — create ONE pool at module/app startup, reuse everywhere
const pool = new Pool({...}); // module-level, created once
app.get('/users', async (req, res) => res.json((await pool.query('SELECT * FROM users')).rows));
```

❌ Mistake 2: Forgetting to release a manually checked-out client
✅ Correct: Every `pool.connect()` MUST be paired with `client.release()` in a `finally` block — otherwise that connection is never returned to the pool, eventually exhausting it ("pool is full" errors).
```javascript
// Wrong — connection leak if an error is thrown before release()
const client = await pool.connect();
await client.query('...'); // if this throws, release() below never runs!
client.release();

// Right — always use try/finally
const client = await pool.connect();
try { await client.query('...'); } finally { client.release(); }
```

---

## 🧠 Tricky Interview Question

```javascript
// Why is string interpolation here dangerous, and what's the fix?
const userInput = "'; DROP TABLE users; --";
await pool.query(`SELECT * FROM users WHERE name = '${userInput}'`);
```
Answer: This is a classic **SQL injection** vulnerability. Because the user input is directly interpolated into the SQL string, an attacker can inject arbitrary SQL (here, a `DROP TABLE` statement). The fix is to use **parameterized queries** with placeholders (`$1`, `$2`, ...) and pass values separately — the `pg` driver sends them to PostgreSQL as DATA, never as executable SQL text: `await pool.query('SELECT * FROM users WHERE name = $1', [userInput]);`. This neutralizes injection regardless of what the input contains.

---

## ⚫ Interview Questions + Answers

Q1: What is a connection pool, and why use `pool.query()` instead of a single persistent connection?
A1: A connection pool maintains a set of ready-to-use DB connections (e.g., `max: 20`) that are handed out to queries as needed and returned afterward. `pool.query()` automatically checks out a connection, runs the query, and releases it — ideal for simple, independent queries. A single persistent connection would serialize ALL queries (one at a time) and risk becoming a bottleneck or single point of failure under concurrent load.

Q2: When do you need to use `pool.connect()` instead of `pool.query()` directly?
A2: When you need MULTIPLE queries to run on the SAME underlying connection — most commonly for transactions (`BEGIN`/`COMMIT`/`ROLLBACK`), since each must execute on the same session/connection to see each other's uncommitted changes. `pool.query()` might use a DIFFERENT connection for each call, which would break transactional consistency.

Q3: How do parameterized queries (`$1`, `$2`) prevent SQL injection?
A3: The `pg` driver sends the SQL query text and the parameter VALUES separately to PostgreSQL using the wire protocol's prepared-statement mechanism. PostgreSQL treats parameters strictly as DATA, never parsing them as part of the SQL syntax — so even malicious strings like `'; DROP TABLE users; --` are just treated as a literal string value, not executable SQL.

Q4: What happens if the connection pool is exhausted (all connections busy)?
A4: New queries/`pool.connect()` calls WAIT in an internal queue until a connection becomes free, up to `connectionTimeoutMillis` — after which they throw a timeout error. This is why setting an appropriate `max` pool size (balanced against PostgreSQL's `max_connections` setting and expected concurrent load) and ALWAYS releasing connections promptly matters for app stability.

Q5: Why should you use environment variables (`DATABASE_URL`, `PGHOST`, etc.) instead of hardcoding DB credentials?
A5: Hardcoding credentials (1) leaks secrets into version control if committed, (2) makes it impossible to use different credentials across dev/staging/production without code changes, and (3) violates basic security hygiene. Using environment variables (loaded via `.env` + `dotenv` locally, or injected by the deployment platform in production) keeps secrets out of code and makes config environment-specific.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building any Node.js app that talks to PostgreSQL directly (with or without an ORM on top)
- You need fine-grained control over SQL, connection pooling, and transactions

❌ Avoid when:
- You'd rather use a higher-level ORM (Prisma/Sequelize) that manages pooling internally — in that case you rarely touch `pg`/`Pool` directly, though it's good to understand what's happening underneath

---

## 📊 Visual Diagram
```
NODE.JS <-> POSTGRESQL VIA pg POOL
──────────────────────────────────────────────
  Express App
       │
       ▼
  pool = new Pool({ max: 20, ... })   ◄── created ONCE at startup
       │
       ├── Connection 1 (idle/busy)
       ├── Connection 2 (idle/busy)
       ├── ...
       └── Connection 20 (idle/busy)
       │
  pool.query(sql, params)
       │
       ▼
  [checkout free connection] → run query → [release back to pool]
       │
       ▼
   PostgreSQL Server (max_connections limit)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pool | Managed set of reusable connections | Reusable connections का managed set |
| pool.query() | Auto checkout + release query | Auto checkout + release query |
| pool.connect() | Manually checkout a client | Client manually checkout करना |
| client.release() | Return connection to pool | Connection pool में वापस करना |
| parameterized query | SQL with placeholder values | Placeholder values वाली SQL |
| SQL injection | Malicious SQL via unsanitized input | Unsanitized input से malicious SQL |
| max_connections | PostgreSQL's connection limit | PostgreSQL की connection limit |

---

## ⚡ 3-Line Summary
English:
1. Use `pg`'s `Pool` (created once, shared app-wide) to connect Node.js to PostgreSQL efficiently, avoiding per-query connection overhead.
2. Always use parameterized queries (`$1`, `$2`) instead of string interpolation to prevent SQL injection.
3. For transactions, manually check out a client with `pool.connect()`, run `BEGIN`/`COMMIT`/`ROLLBACK`, and always `client.release()` in a `finally` block.

Hindi:
1. Node.js को PostgreSQL से efficiently connect करने के लिए `pg` का `Pool` (एक बार बना, पूरे app में shared) इस्तेमाल करो।
2. SQL injection से बचने के लिए हमेशा parameterized queries (`$1`, `$2`) इस्तेमाल करो, string interpolation नहीं।
3. Transactions के लिए `pool.connect()` से client checkout करो, `BEGIN`/`COMMIT`/`ROLLBACK` चलाओ, और `finally` में `client.release()` हमेशा करो।

---

## ➡️ Next Topic
**158. pg Package** — Deep dive into the `pg` driver's API: queries, cursors, streaming, types, and error codes.
