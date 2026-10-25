# 143. Connecting MySQL with Node.js
# हिंदी में: Node.js में MySQL Connect करना

---

## 🔵 Simple Definition (English)
Connecting MySQL with Node.js means establishing a network connection from your Node.js application to a MySQL database server using a driver (like `mysql2`), so your app can send SQL queries and receive results programmatically.

## 🔵 सरल परिभाषा (Hindi)
Node.js में MySQL connect करने का मतलब है एक driver (जैसे `mysql2`) के through अपने Node.js application से MySQL database server तक network connection बनाना, ताकि आपकी app SQL queries भेज सके और results programmatically receive कर सके।

---

## 🔴 Problem it Solves
Node.js applications need to persist and query structured, relational data (users, orders, products with relationships) — something in-memory variables can't do (data is lost on restart). MySQL is a mature, widely-used relational database, but Node.js (JavaScript) can't talk to it natively — a driver is needed to handle the MySQL wire protocol (the binary protocol MySQL uses for client-server communication), connection lifecycle, authentication, and query execution, translating JavaScript function calls into the actual network requests MySQL understands.

## 🔴 यह क्यों बना? (Hindi)
Node.js applications को structured, relational data persist और query करना होता है (users, orders, products with relationships) — यह in-memory variables से नहीं हो सकता (restart पर data खो जाता है)। MySQL एक mature relational database है, पर Node.js (JavaScript) natively उससे बात नहीं कर सकता — एक driver चाहिए जो MySQL wire protocol, connection lifecycle, authentication, query execution handle करे।

---

## 🟢 How it Works — Step by Step

Step 1 → Install a MySQL driver: `npm install mysql2` (modern, faster, Promise-supporting successor to the older `mysql` package)
Step 2 → Create a connection using credentials: host, port, user, password, database name
Step 3 → Driver performs a TCP handshake with the MySQL server, then authenticates using the provided credentials (MySQL's auth protocol, e.g., `caching_sha2_password`)
Step 4 → Once authenticated, the connection is ready — you send SQL queries as strings (or parameterized queries) through the connection object
Step 5 → MySQL server parses, executes, and returns results over the same connection (as rows + metadata)
Step 6 → The driver parses MySQL's binary response format back into JavaScript objects/arrays
Step 7 → Properly close the connection (`connection.end()`) when done, or (better, for apps) use a connection POOL instead of single connections (covered in topic 145)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → MySQL driver install करो: `npm install mysql2`
Step 2 → Credentials से connection बनाओ
Step 3 → Driver TCP handshake करता है, फिर authenticate करता है
Step 4 → Connection ready होने पर SQL queries भेजो
Step 5 → MySQL server queries execute करके results return करता है
Step 6 → Driver binary response को JS objects में parse करता है
Step 7 → Connection properly close करो या connection pool use करो

---

## 🟡 Real World Example
**Flipkart's order management service:** Uses MySQL to store orders, order items, and customer data with strong relational integrity (foreign keys ensuring an order always references a valid customer). The Node.js order service connects using `mysql2`, with connection credentials pulled from a secrets manager (not hardcoded), and uses a connection pool (not single connections) since the service handles thousands of concurrent requests — a single connection would become a severe bottleneck, serializing every query behind one TCP socket.

## 🟡 Real Example Hindi mein
**Flipkart का order management service:** MySQL use करता है orders, order items, customer data store करने के लिए strong relational integrity के साथ। Node.js order service `mysql2` से connect होता है, credentials secrets manager से आते हैं, और connection pool use करता है क्योंकि service हज़ारों concurrent requests handle करता है।

---

## 💻 Code Example — Basic

```javascript
// mysql-basic.js — single connection, basic query
// Run with: node mysql-basic.js (requires a running MySQL server + npm install mysql2)

const mysql = require('mysql2/promise');  // Promise-based API (cleaner async/await usage)

async function main() {
  // ─── 1. CREATE A CONNECTION ────────────────────────────────────────────────
  const connection = await mysql.createConnection({
    host: 'localhost',
    port: 3306,                 // default MySQL port
    user: 'root',
    password: 'your_password',
    database: 'ecommerce',      // database must already exist
  });

  console.log('Connected to MySQL successfully!');

  // ─── 2. RUN A SIMPLE QUERY ──────────────────────────────────────────────────
  const [rows, fields] = await connection.execute('SELECT * FROM products LIMIT 5');
  console.log('Rows:', rows);     // actual data
  console.log('Fields:', fields.map((f) => f.name));  // column names/metadata

  // ─── 3. ALWAYS CLOSE THE CONNECTION WHEN DONE ───────────────────────────────
  await connection.end();
  console.log('Connection closed.');
}

main().catch((err) => {
  console.error('Connection failed:', err.message);
  process.exit(1);
});
```

## 💻 Code Example — Advanced

```javascript
// mysql-advanced.js — connection with error handling, retries, and graceful shutdown

const mysql = require('mysql2/promise');

class Database {
  constructor(config) {
    this.config = config;
    this.connection = null;
  }

  // ─── 1. CONNECT WITH RETRY LOGIC (handles transient startup race conditions) ─
  async connect(maxRetries = 5, delayMs = 2000) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        this.connection = await mysql.createConnection(this.config);
        console.log(`Connected to MySQL on attempt ${attempt}`);

        // Verify the connection actually works (not just TCP-connected)
        await this.connection.ping();
        return this.connection;
      } catch (err) {
        console.error(`Connection attempt ${attempt} failed: ${err.message}`);
        if (attempt === maxRetries) {
          throw new Error(`Failed to connect to MySQL after ${maxRetries} attempts`);
        }
        await new Promise((resolve) => setTimeout(resolve, delayMs));  // wait before retry
      }
    }
  }

  // ─── 2. HANDLE CONNECTION ERRORS DURING OPERATION (e.g., connection dropped) ─
  async queryWithReconnect(sql, params = []) {
    try {
      return await this.connection.execute(sql, params);
    } catch (err) {
      // PROTOCOL_CONNECTION_LOST or similar — reconnect once and retry the query
      if (err.code === 'PROTOCOL_CONNECTION_LOST' || err.code === 'ECONNRESET') {
        console.warn('Connection lost, reconnecting...');
        await this.connect();
        return this.connection.execute(sql, params);
      }
      throw err;  // other errors (syntax, constraint violations) should propagate
    }
  }

  // ─── 3. GRACEFUL SHUTDOWN ─────────────────────────────────────────────────────
  async disconnect() {
    if (this.connection) {
      await this.connection.end();
      console.log('MySQL connection closed gracefully.');
    }
  }
}

// ─── USAGE ──────────────────────────────────────────────────────────────────────
async function main() {
  const db = new Database({
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME || 'ecommerce',
    connectTimeout: 10000,  // fail fast if server unreachable within 10s
  });

  await db.connect();
  const [products] = await db.queryWithReconnect('SELECT * FROM products WHERE price > ?', [500]);
  console.log('Products over ₹500:', products.length);

  // Graceful shutdown on process signals (SIGTERM from orchestrators like Kubernetes)
  process.on('SIGTERM', async () => {
    await db.disconnect();
    process.exit(0);
  });
}

main().catch(console.error);

module.exports = Database;
```

---

## 🟠 Express.js Integration

```javascript
// server.js
const express = require('express');
const mysql = require('mysql2/promise');

const app = express();
app.use(express.json());

let connection;

// Connect to MySQL BEFORE starting the HTTP server
async function startServer() {
  connection = await mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
  });
  console.log('MySQL connected.');

  app.get('/products', async (req, res) => {
    try {
      const [products] = await connection.execute('SELECT * FROM products LIMIT 20');
      res.json(products);
    } catch (err) {
      console.error('Query error:', err.message);
      res.status(500).json({ error: 'Database query failed' });
    }
  });

  app.get('/health', async (req, res) => {
    try {
      await connection.ping();  // verify DB is still reachable
      res.json({ status: 'ok', db: 'connected' });
    } catch {
      res.status(503).json({ status: 'error', db: 'disconnected' });
    }
  });

  app.listen(3000, () => console.log('Server running on port 3000'));
}

startServer().catch((err) => {
  console.error('Failed to start server:', err.message);
  process.exit(1);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  if (connection) await connection.end();
  process.exit(0);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Creating a new connection for every single request
```javascript
// WRONG: opens and closes a TCP connection + auth handshake on EVERY request — very slow
app.get('/products', async (req, res) => {
  const connection = await mysql.createConnection(config);  // expensive, repeated every time
  const [rows] = await connection.execute('SELECT * FROM products');
  await connection.end();
  res.json(rows);
});

// CORRECT: create ONE connection (or better, a pool) at startup, reuse it for all requests
let connection;
async function init() { connection = await mysql.createConnection(config); }
app.get('/products', async (req, res) => {
  const [rows] = await connection.execute('SELECT * FROM products');  // reuses existing connection
  res.json(rows);
});
```

❌ Mistake 2: Not handling connection failures at startup gracefully
```javascript
// WRONG: app crashes with an unhandled rejection if MySQL isn't ready yet
mysql.createConnection(config).then((conn) => { connection = conn; });
app.listen(3000);  // server starts even if DB connection is still pending/failed!

// CORRECT: await the connection before starting the server, exit clearly on failure
async function startServer() {
  connection = await mysql.createConnection(config);  // await — don't start server until ready
  app.listen(3000);
}
startServer().catch((err) => { console.error(err); process.exit(1); });
```

---

## 🧠 Tricky Interview Question

```javascript
const mysql = require('mysql2/promise');
const connection = await mysql.createConnection(config);

const result1 = connection.execute('SELECT * FROM products');  // no await!
const result2 = await connection.execute('SELECT * FROM orders');

console.log(result1);  // ?
```
Answer: `result1` is a **pending Promise object**, NOT the query results — because `await` was forgotten on the first call. `console.log(result1)` prints something like `Promise { <pending> }` (or possibly already resolved by the time it logs, depending on timing, but you'd still be logging the Promise wrapper, not `[rows, fields]`). This is a common async/await mistake: with `mysql2/promise`, EVERY `.execute()`/`.query()` call returns a Promise that MUST be awaited (or `.then()`-chained) to get actual data — forgetting `await` silently produces a Promise object instead of throwing an obvious error, making this bug easy to miss in code review.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between the `mysql` and `mysql2` npm packages?
A1: `mysql2` is a modern, actively maintained successor offering: built-in Promise support (`mysql2/promise`) without needing extra wrapper libraries, significantly better performance (especially for prepared statements), support for newer MySQL authentication methods (`caching_sha2_password`, MySQL 8's default), and support for binary protocol / prepared statements. The older `mysql` package is callback-based by default and lacks some newer MySQL 8 features. `mysql2` is the recommended choice for new projects.

Q2: What happens if you don't close a MySQL connection when your Node.js process exits?
A2: If using a single raw connection, the TCP socket may linger open until the OS/MySQL server times it out (MySQL has a `wait_timeout` setting, default 8 hours) — this ties up a connection slot on the MySQL server unnecessarily. For graceful shutdowns (deployments, container restarts), always explicitly call `connection.end()` in a `SIGTERM`/`SIGINT` handler so the server doesn't accumulate stale connections, especially important since MySQL has a hard LIMIT on total concurrent connections (`max_connections`).

Q3: Why might `connection.execute()` be preferred over `connection.query()` in mysql2?
A3: `.execute()` uses MySQL's PREPARED STATEMENT protocol — the query structure is sent once, compiled by the server, and can be reused with different parameter values efficiently (also inherently parameterized, preventing SQL injection). `.query()` sends the full SQL text as-is each time (can still be parameterized with `?` placeholders via client-side escaping, but doesn't use server-side prepared statements). For queries executed repeatedly with different parameters, `.execute()` is both safer by default and can be more performant due to statement caching on the server.

Q4: What does `connection.ping()` do, and why is it useful in a health check endpoint?
A4: `ping()` sends a lightweight MySQL protocol command to verify the connection is still alive and the server is responsive, without running an actual data query. It's ideal for `/health` endpoints (used by load balancers/orchestrators to decide if an instance should receive traffic) because it's cheap and directly confirms DB connectivity — more meaningful than just "the Node process is running" which says nothing about whether it can actually serve requests that depend on the database.

Q5: What is `ECONNRESET` or `PROTOCOL_CONNECTION_LOST` and how should an app handle it?
A5: These errors mean the TCP connection to MySQL was unexpectedly closed (server restart, network blip, idle timeout exceeded, MySQL killing a long-idle connection). A single long-lived connection object becomes permanently unusable after this — the app must detect the error code and either reconnect (create a fresh connection) or, in production, rely on a connection POOL (topic 145) which automatically handles replacing dead connections transparently, making this a non-issue for most well-architected apps.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Your app needs structured, relational data storage with strong consistency and relationships (orders, inventory, financial records).

❌ Avoid when:
- Using a single raw connection for a production app serving concurrent traffic — always use connection pooling (topic 145) instead of this single-connection pattern in real apps.
- Data is highly unstructured/document-like with no relational needs — a NoSQL database (MongoDB) might be a better fit.

---

## 📊 Visual Diagram

```
MYSQL CONNECTION LIFECYCLE:
──────────────────────────────────────────────────────────

  Node.js app                          MySQL Server
       │── TCP handshake ──────────────────►│
       │◄──── Server greeting ──────────────│
       │── Authentication (credentials) ───►│
       │◄──── Auth success/failure ─────────│
       │                                     │
       │── Query: SELECT * FROM products ──►│
       │◄──── Rows + metadata ───────────────│
       │                                     │
       │── connection.end() ────────────────►│
       │◄──── Connection closed ─────────────│
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Driver | Library translating JS calls to DB protocol | JS calls को DB protocol में translate करने वाली library |
| Connection | Established link between app and DB server | App और DB server के बीच link |
| Prepared statement | Precompiled query reused with different params | Precompiled query, अलग params के साथ reuse |
| Wire protocol | Binary protocol DB uses for communication | DB communication का binary protocol |
| Graceful shutdown | Cleanly closing resources before exit | Exit से पहले resources cleanly close करना |
| Health check | Endpoint verifying system components are working | System components working check करने वाला endpoint |

---

## ⚡ 3-Line Summary
English:
1. Connecting Node.js to MySQL requires a driver (`mysql2`) that handles the TCP handshake, authentication, and query execution over MySQL's wire protocol.
2. Create the connection once at startup (await it before starting the server), never per-request, and always await every `.execute()`/`.query()` call.
3. Handle connection loss gracefully (retry/reconnect logic) and close connections cleanly on shutdown — but prefer connection pooling for real production apps.

Hindi:
1. Node.js को MySQL से connect करने के लिए driver (`mysql2`) चाहिए जो TCP handshake, authentication, query execution handle करे।
2. Connection एक बार startup पर बनाओ, हर request पर नहीं, और हर `.execute()` call को await करो।
3. Connection loss को gracefully handle करो, shutdown पर cleanly close करो — production apps के लिए connection pooling prefer करो।

---

## ➡️ Next Topic
**144. mysql2 Package** — mysql2 की features, prepared statements, और performance characteristics में गहराई से।
