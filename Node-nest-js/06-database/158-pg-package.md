# 158. pg Package
# हिंदी में: pg Package — Node के लिए PostgreSQL Driver

---

## 🔵 Simple Definition (English)
**`pg`** (node-postgres) is the most widely used low-level PostgreSQL driver/client for Node.js. It provides `Pool` and `Client` classes for connecting, a `query()` method supporting parameterized SQL, type parsing (converting PostgreSQL types to JS types), streaming query results via cursors, and support for transactions, notifications (`LISTEN`/`NOTIFY`), and connection configuration.

## 🔵 सरल परिभाषा (Hindi)
**`pg`** (node-postgres) Node.js के लिए सबसे widely used low-level PostgreSQL driver है। ये `Pool` और `Client` classes देता है connect करने के लिए, parameterized SQL के साथ `query()` method, type parsing (PostgreSQL types को JS types में convert), cursors से streaming results, और transactions, notifications (`LISTEN`/`NOTIFY`) का support।

---

## 🔴 Problem it Solves
Talking to PostgreSQL over its binary/text wire protocol directly would require implementing authentication handshakes, query serialization, result parsing, and connection management from scratch — far too low-level for application code. `pg` abstracts all of this into a simple JS API (`pool.query()`), while still exposing enough low-level control (raw SQL, cursors, custom type parsers, LISTEN/NOTIFY) for advanced use cases that higher-level ORMs don't expose.

## 🔴 यह क्यों बना? (Hindi)
PostgreSQL के binary/text wire protocol से directly बात करने के लिए authentication handshakes, query serialization, result parsing, connection management सब from scratch implement करना पड़ता — application code के लिए बहुत low-level। `pg` इस सब को simple JS API (`pool.query()`) में abstract करता है, फिर भी low-level control (raw SQL, cursors, custom type parsers, LISTEN/NOTIFY) एक्सपोज़ करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Install: `npm install pg`.
Step 2 → Create a `Pool` (recommended for apps) or a single `Client` (for scripts/one-off connections).
Step 3 → Run queries with `query(text, values)` — returns a `Result` object: `{ rows, rowCount, fields, command }`.
Step 4 → For large result sets, use `pg-cursor` or `pg-query-stream` to stream rows instead of loading them all into memory.
Step 5 → Use `LISTEN`/`NOTIFY` with a dedicated `Client` (not pool) for real-time pub/sub notifications from PostgreSQL itself.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Install करो: `npm install pg`।
Step 2 → `Pool` (apps के लिए recommended) या single `Client` (scripts के लिए) बनाओ।
Step 3 → `query(text, values)` चलाओ — `Result` object मिलता है: `{ rows, rowCount, fields, command }`।
Step 4 → Large result sets के लिए `pg-cursor` या `pg-query-stream` से rows stream करो, memory में सब load मत करो।
Step 5 → Real-time notifications के लिए `LISTEN`/`NOTIFY` एक dedicated `Client` से use करो (pool से नहीं)।

---

## 🟢 Also useful: result object fields

```
result.rows       → array of row objects
result.rowCount    → number of rows affected/returned
result.fields      → column metadata (name, type)
result.command     → 'SELECT' | 'INSERT' | 'UPDATE' | 'DELETE'
```

---

## 🟡 Real World Example
**Paytm's fraud-detection service** uses `pg`'s `LISTEN`/`NOTIFY` feature: whenever a new suspicious transaction row is inserted, a PostgreSQL trigger fires `NOTIFY fraud_alerts, '<transaction_id>'`. A dedicated Node.js `Client` (kept open specifically for listening, separate from the query pool) receives this notification instantly and triggers a real-time fraud check — without polling the database every few seconds, saving load and reducing detection latency from seconds to milliseconds.

## 🟡 Real Example Hindi mein
**Paytm की fraud-detection service** `pg` का `LISTEN`/`NOTIFY` feature इस्तेमाल करती है: जब भी suspicious transaction row insert होता, एक PostgreSQL trigger `NOTIFY fraud_alerts, '<id>'` fire करता है। एक dedicated Node.js `Client` (सिर्फ listening के लिए, query pool से अलग) ये notification instantly receive करता है और real-time fraud check trigger करता है — DB को हर कुछ seconds poll करने की ज़रूरत नहीं।

---

## 💻 Code Example — Basic

```javascript
// pg-package-basic.js
// npm install pg
const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL || 'postgres://localhost/myapp' });

async function main() {
  // The Result object: rows, rowCount, fields, command
  const result = await pool.query('SELECT NOW() as current_time, $1::int as doubled', [21]);
  console.log('Command:', result.command);       // "SELECT"
  console.log('Row count:', result.rowCount);     // 1
  console.log('Rows:', result.rows);              // [{ current_time: ..., doubled: 21 }]
  console.log('Field names:', result.fields.map(f => f.name)); // ["current_time", "doubled"]

  // Type parsing: pg automatically converts PG types to JS types
  // INTEGER -> Number, TEXT -> String, TIMESTAMP -> Date, BOOLEAN -> Boolean, JSON/JSONB -> Object
  const typeTest = await pool.query(`SELECT 42 as num, true as flag, '{"a":1}'::jsonb as data`);
  console.log(typeof typeTest.rows[0].num);   // 'number'
  console.log(typeof typeTest.rows[0].flag);  // 'boolean'
  console.log(typeTest.rows[0].data);         // { a: 1 } — parsed as a JS object automatically

  await pool.end();
}

main().catch(console.error);
```

## 💻 Code Example — Advanced

```javascript
// pg-package-advanced.js — streaming large results + LISTEN/NOTIFY
// npm install pg pg-query-stream
const { Pool, Client } = require('pg');
const QueryStream = require('pg-query-stream');

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// ─── 1. STREAMING LARGE RESULT SETS (avoid loading millions of rows into memory) ──
async function exportLargeTable(writableStream) {
  const client = await pool.connect();
  try {
    const query = new QueryStream('SELECT * FROM orders WHERE status = $1', ['completed'], {
      batchSize: 500, // fetch rows in batches of 500 under the hood
    });
    const stream = client.query(query);

    stream.on('data', (row) => {
      writableStream.write(JSON.stringify(row) + '\n'); // process row by row, constant memory
    });

    await new Promise((resolve, reject) => {
      stream.on('end', resolve);
      stream.on('error', reject);
    });
  } finally {
    client.release(); // return the connection to the pool
  }
}

// ─── 2. LISTEN / NOTIFY for real-time events ─────────────────────────────────
async function startFraudListener() {
  // IMPORTANT: use a dedicated Client, NOT the pool — LISTEN requires a persistent, single connection
  const listenerClient = new Client({ connectionString: process.env.DATABASE_URL });
  await listenerClient.connect();

  await listenerClient.query('LISTEN fraud_alerts'); // subscribe to the channel

  listenerClient.on('notification', (msg) => {
    // msg.channel === 'fraud_alerts', msg.payload === the NOTIFY payload string
    console.log(`Fraud alert received for transaction: ${msg.payload}`);
    // trigger real-time fraud check logic here
  });

  listenerClient.on('error', (err) => console.error('Listener connection error:', err.message));

  return listenerClient; // keep reference to close it later during shutdown
}

// ─── 3. CUSTOM TYPE PARSER (e.g., parse NUMERIC as float instead of string) ──
const types = require('pg').types;
// By default, pg returns NUMERIC/DECIMAL as a STRING (to avoid float precision loss)
types.setTypeParser(1700, (val) => parseFloat(val)); // 1700 = OID for NUMERIC

async function run() {
  const listener = await startFraudListener();
  console.log('Fraud listener active. Waiting for notifications...');
  // In a real app, keep this running; here we just demonstrate setup.
  setTimeout(async () => {
    await listener.end();
    await pool.end();
  }, 2000);
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express route streaming a large PostgreSQL result set directly to the HTTP response
const express = require('express');
const { Pool } = require('pg');
const QueryStream = require('pg-query-stream');

const app = express();
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

app.get('/export/orders.csv', async (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  const client = await pool.connect();

  try {
    const query = new QueryStream('SELECT id, amount, status FROM orders');
    const stream = client.query(query);

    res.write('id,amount,status\n');
    stream.on('data', (row) => res.write(`${row.id},${row.amount},${row.status}\n`));
    stream.on('end', () => { res.end(); client.release(); });
    stream.on('error', (err) => { res.status(500).end(); client.release(); });
  } catch (err) {
    client.release();
    res.status(500).json({ error: 'Export failed' });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `pool.query()` for `LISTEN`
```javascript
// Wrong — pool may use a DIFFERENT connection next time, you'll silently miss notifications
await pool.query('LISTEN my_channel');

// Right — use a dedicated Client that stays open for the LISTEN's lifetime
const client = new Client({ connectionString: process.env.DATABASE_URL });
await client.connect();
await client.query('LISTEN my_channel');
client.on('notification', (msg) => console.log(msg));
```

❌ Mistake 2: Loading a huge table with `pool.query()` instead of streaming
✅ Correct: `pool.query('SELECT * FROM huge_table')` loads ALL rows into memory at once — for millions of rows this can crash the process. Use `pg-query-stream` or `pg-cursor` to process rows incrementally.

---

## 🧠 Tricky Interview Question

```javascript
const result = await pool.query('SELECT 99999999999999999999.5::numeric as big_num');
console.log(typeof result.rows[0].big_num, result.rows[0].big_num);
```
Answer: Output is `string '99999999999999999999.5'` — NOT a number. By default, `pg` parses PostgreSQL's `NUMERIC`/`DECIMAL` type as a STRING, because JavaScript's `Number` type (IEEE 754 double) cannot represent arbitrary-precision decimals without losing precision. This is a deliberate safety choice. If you need it as a float (accepting potential precision loss for values within safe range), you must explicitly override with `pg.types.setTypeParser(1700, parseFloat)`.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `Pool` and `Client` in the `pg` package?
A1: `Client` represents a SINGLE database connection — you connect, use it, and disconnect. `Pool` manages MULTIPLE `Client` connections automatically, handing them out and reclaiming them as needed (`pool.query()` auto-checks-out and releases). Use `Pool` for typical app query patterns; use a standalone `Client` for scenarios needing a persistent single connection, like `LISTEN`/`NOTIFY` or explicit session-level settings.

Q2: What does the `Result` object returned by `query()` contain?
A2: `{ rows, rowCount, fields, command, oid }`. `rows` is an array of row objects (column name → value). `rowCount` is the number of rows affected/returned. `fields` describes each column's name and PostgreSQL type OID. `command` tells you which SQL command ran (`SELECT`, `INSERT`, etc.) — useful for generic query-executing utility functions.

Q3: How does `pg` handle automatic type conversion between PostgreSQL and JavaScript?
A3: `pg` ships with built-in type parsers mapping common PostgreSQL OIDs to JS types: `INTEGER`→`Number`, `TEXT`/`VARCHAR`→`String`, `BOOLEAN`→`Boolean`, `TIMESTAMP`/`TIMESTAMPTZ`→`Date`, `JSON`/`JSONB`→parsed `Object`/`Array`. Some types are intentionally kept as strings to avoid precision loss (`NUMERIC`, `BIGINT` beyond safe integer range). You can override any parser via `pg.types.setTypeParser(oid, parserFn)`.

Q4: Why is `LISTEN`/`NOTIFY` useful, and what are its limitations?
A4: `LISTEN`/`NOTIFY` is PostgreSQL's built-in pub/sub mechanism — a client subscribes to a channel (`LISTEN channel`), and any session can broadcast a message (`NOTIFY channel, 'payload'`), instantly delivered to all listeners on that channel, without polling. Limitations: payload is limited to ~8KB, there's no message persistence/replay (if no one's listening when NOTIFY fires, the message is lost), and it doesn't scale to very high-frequency event streams as well as a dedicated message queue (Kafka, Redis Pub/Sub) would.

Q5: How would you stream millions of rows from PostgreSQL without running out of memory?
A5: Use `pg-cursor` or `pg-query-stream` instead of `pool.query()`. These fetch rows in small batches (e.g., 500 at a time) under the hood using PostgreSQL's cursor protocol, exposing them to Node as a readable stream. You process each row/batch as it arrives (e.g., `stream.on('data', row => {...})`), keeping memory usage constant regardless of total row count — essential for exports, ETL jobs, and reports over large tables.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need direct, fine-grained control over SQL and PostgreSQL-specific features (LISTEN/NOTIFY, cursors)
- Building the underlying layer for a custom query builder or even an ORM
- Streaming very large datasets efficiently

❌ Avoid when:
- A higher-level ORM (Prisma, Sequelize, Knex) already covers your needs with less boilerplate and built-in safety (migrations, type generation) — use `pg` directly only when you need its lower-level control

---

## 📊 Visual Diagram
```
pg PACKAGE ARCHITECTURE
──────────────────────────────────────────────
  Pool                         Client
  ┌──────────────┐            ┌──────────────┐
  │ conn 1 (idle) │            │ single conn  │
  │ conn 2 (busy) │            │ (LISTEN/NOTIFY, │
  │ ...           │            │  transactions)  │
  │ conn N        │            └──────────────┘
  └──────────────┘
       │
       ▼
  pool.query(sql, params)
       │
       ▼
  Result { rows, rowCount, fields, command }

STREAMING:
  pg-query-stream → batches of rows → Node Readable stream → process incrementally
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pool | Multiple reusable connections | कई reusable connections |
| Client | Single DB connection | Single DB connection |
| Result object | Query result wrapper | Query result का wrapper |
| type parser | Converts PG type to JS type | PG type को JS type में convert |
| LISTEN/NOTIFY | PostgreSQL pub/sub mechanism | PostgreSQL का pub/sub mechanism |
| pg-query-stream | Streaming query results | Streaming query results |
| OID | PostgreSQL's internal type ID | PostgreSQL का internal type ID |

---

## ⚡ 3-Line Summary
English:
1. `pg` is the core low-level PostgreSQL driver for Node.js, offering `Pool`/`Client`, parameterized queries, and automatic type conversion.
2. Use a dedicated `Client` (not `Pool`) for `LISTEN`/`NOTIFY`, since it needs a persistent single connection to receive events.
3. Stream large result sets with `pg-query-stream`/`pg-cursor` instead of `pool.query()` to keep memory usage constant.

Hindi:
1. `pg` Node.js के लिए core low-level PostgreSQL driver है — `Pool`/`Client`, parameterized queries, automatic type conversion देता है।
2. `LISTEN`/`NOTIFY` के लिए dedicated `Client` (Pool नहीं) इस्तेमाल करो, persistent connection चाहिए।
3. Large result sets के लिए `pg-query-stream`/`pg-cursor` से stream करो, `pool.query()` से नहीं — memory constant रहती है।

---

## ➡️ Next Topic
**159. MongoDB with Node.js** — Connecting to MongoDB using the native driver, basic CRUD, and when to choose MongoDB over a relational DB.
