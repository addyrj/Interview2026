# 144. mysql2 Package
# हिंदी में: mysql2 Package

---

## 🔵 Simple Definition (English)
**mysql2** is the most widely-used Node.js driver for MySQL/MariaDB — a faster, more feature-complete successor to the original `mysql` package, with native Promise support, prepared statements, connection pooling, and support for modern MySQL 8 authentication and features.

## 🔵 सरल परिभाषा (Hindi)
**mysql2** Node.js का सबसे widely-used MySQL/MariaDB driver है — original `mysql` package का faster, ज़्यादा feature-complete successor, native Promise support, prepared statements, connection pooling, और modern MySQL 8 authentication के साथ।

---

## 🔴 Problem it Solves
The original `mysql` package was callback-only (required extra wrapper libraries like `util.promisify` or third-party add-ons for Promise/async-await support), had slower parsing performance for prepared statements, and lagged in supporting MySQL 8's newer default authentication plugin (`caching_sha2_password`) — meaning apps connecting to modern MySQL 8 servers would fail to authenticate with the old `mysql` package out of the box. `mysql2` was built as a drop-in-compatible but modernized replacement solving all of these.

## 🔴 यह क्यों बना? (Hindi)
Original `mysql` package callback-only था, Promise/async-await support के लिए extra wrapper libraries चाहिए पड़ती थीं, prepared statements के लिए slower parsing performance थी, और MySQL 8 के नए default authentication plugin को support नहीं करता था। `mysql2` एक drop-in-compatible पर modernized replacement के रूप में बना जो यह सब solve करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Install: `npm install mysql2`
Step 2 → Choose API style: `require('mysql2')` (callback-based, original style) or `require('mysql2/promise')` (Promise-based, recommended for async/await)
Step 3 → Create a connection or pool with config object (host, user, password, database, and performance options like `connectionLimit`)
Step 4 → Use `.execute(sql, params)` for prepared statements (parameterized, cached by MySQL server for reuse) or `.query(sql)` for plain queries without server-side preparation
Step 5 → mysql2 automatically handles type conversion: MySQL `DATETIME` → JS `Date`, `DECIMAL` → string (by default, to avoid floating-point precision loss) or number (configurable)
Step 6 → For batch operations, use `.execute()` with array parameters, or multi-statement queries (`multipleStatements: true` config, used cautiously due to injection risk considerations)
Step 7 → Leverage built-in connection pooling (`mysql2.createPool()`) for production apps — handles connection reuse, queuing, and automatic replacement of dead connections

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `npm install mysql2` install करो
Step 2 → API style चुनो: callback या Promise-based
Step 3 → Connection या pool बनाओ config object से
Step 4 → `.execute()` prepared statements के लिए, `.query()` plain queries के लिए use करो
Step 5 → mysql2 automatically type conversion करता है
Step 6 → Batch operations के लिए array parameters use करो
Step 7 → Production में connection pooling use करो

---

## 🟡 Real World Example
**Swiggy's menu service:** Uses `mysql2/promise` to query restaurant menus with hundreds of thousands of items. Because `.execute()` uses server-side prepared statements, repeated queries like "get menu items for restaurant X" (same SQL structure, different restaurant ID each time) benefit from MySQL caching the compiled query plan — meaningfully faster under high load compared to re-parsing full SQL text every time. The service also configures `dateStrings: true` to receive `DATETIME` columns as plain strings rather than JS `Date` objects, avoiding timezone-conversion surprises when displaying order timestamps.

## 🟡 Real Example Hindi mein
**Swiggy का menu service:** `mysql2/promise` use करता है lakhs items वाले restaurant menus query करने के लिए। `.execute()` server-side prepared statements use करता है, repeated queries faster होती हैं high load में। Service `dateStrings: true` configure करता है `DATETIME` columns plain strings की तरह लेने के लिए।

---

## 💻 Code Example — Basic

```javascript
// mysql2-basic.js — core API: query vs execute, callback vs promise
// Run with: node mysql2-basic.js (requires running MySQL + npm install mysql2)

const mysql = require('mysql2/promise');

async function main() {
  const connection = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'password',
    database: 'shop',
  });

  // ─── 1. .query() — plain query, client-side escaping for placeholders ──────
  const [productsQuery] = await connection.query(
    'SELECT * FROM products WHERE category = ?',
    ['electronics']
  );
  console.log('Via .query():', productsQuery.length, 'rows');

  // ─── 2. .execute() — uses MySQL prepared statements (server-side caching) ──
  const [productsExecute] = await connection.execute(
    'SELECT * FROM products WHERE category = ?',
    ['electronics']
  );
  console.log('Via .execute():', productsExecute.length, 'rows');
  // Both return the same data, but .execute() is more efficient for REPEATED queries

  // ─── 3. INSERT and reading the auto-generated ID ───────────────────────────
  const [insertResult] = await connection.execute(
    'INSERT INTO products (name, price, category) VALUES (?, ?, ?)',
    ['Wireless Mouse', 799, 'electronics']
  );
  console.log('Inserted product with ID:', insertResult.insertId);

  await connection.end();
}

main().catch(console.error);
```

## 💻 Code Example — Advanced

```javascript
// mysql2-advanced.js — transactions, batch inserts, and type configuration

const mysql = require('mysql2/promise');

async function main() {
  const connection = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'password',
    database: 'shop',
    dateStrings: true,        // return DATETIME as string, not JS Date (avoid TZ surprises)
    decimalNumbers: true,     // return DECIMAL columns as JS numbers, not strings
  });

  // ─── 1. TRANSACTION: multiple queries, all-or-nothing ───────────────────────
  // Classic use case: deduct stock AND create an order atomically
  async function placeOrder(productId, quantity, customerId) {
    await connection.beginTransaction();
    try {
      const [[product]] = await connection.execute(
        'SELECT stock, price FROM products WHERE id = ? FOR UPDATE',  // row-lock to prevent race conditions
        [productId]
      );

      if (!product || product.stock < quantity) {
        throw new Error('Insufficient stock');
      }

      await connection.execute(
        'UPDATE products SET stock = stock - ? WHERE id = ?',
        [quantity, productId]
      );

      const [orderResult] = await connection.execute(
        'INSERT INTO orders (product_id, customer_id, quantity, total) VALUES (?, ?, ?, ?)',
        [productId, customerId, quantity, product.price * quantity]
      );

      await connection.commit();   // all changes applied together
      return orderResult.insertId;
    } catch (err) {
      await connection.rollback();  // undo everything if ANY step failed
      throw err;
    }
  }

  // ─── 2. BATCH INSERT (efficient multi-row insert in one round trip) ────────
  async function bulkInsertProducts(products) {
    // products = [{ name, price, category }, ...]
    const values = products.map((p) => [p.name, p.price, p.category]);
    const [result] = await connection.query(
      'INSERT INTO products (name, price, category) VALUES ?',  // note: raw ? for VALUES array syntax
      [values]
    );
    return result.affectedRows;
  }

  // ─── 3. USAGE ─────────────────────────────────────────────────────────────────
  try {
    const orderId = await placeOrder(1, 2, 101);
    console.log('Order placed:', orderId);
  } catch (err) {
    console.error('Order failed:', err.message);
  }

  const inserted = await bulkInsertProducts([
    { name: 'Keyboard', price: 1299, category: 'electronics' },
    { name: 'Monitor', price: 8999, category: 'electronics' },
  ]);
  console.log('Bulk inserted rows:', inserted);

  await connection.end();
}

main().catch(console.error);
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

async function init() {
  connection = await mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    dateStrings: true,
  });

  app.post('/orders', async (req, res) => {
    const { productId, quantity, customerId } = req.body;

    await connection.beginTransaction();
    try {
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
        'INSERT INTO orders (product_id, customer_id, quantity, total) VALUES (?, ?, ?, ?)',
        [productId, customerId, quantity, product.price * quantity]
      );
      await connection.commit();

      res.status(201).json({ orderId: result.insertId });
    } catch (err) {
      await connection.rollback();
      res.status(500).json({ error: 'Order failed' });
    }
  });

  app.listen(3000, () => console.log('Server running'));
}

init().catch((err) => { console.error(err); process.exit(1); });
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting that DECIMAL columns return as strings by default
```javascript
// WRONG: assuming price is a number, causing silent bugs in arithmetic
const [[product]] = await connection.execute('SELECT price FROM products WHERE id = ?', [1]);
console.log(product.price + 10);  // "799" + 10 = "79910" (string concatenation!) if decimalNumbers not set

// CORRECT: either configure decimalNumbers: true, or explicitly convert
const connection = await mysql.createConnection({ ...config, decimalNumbers: true });
// OR: const price = Number(product.price);
```

❌ Mistake 2: Using `.query()` with the VALUES array syntax expecting it to work with `.execute()`
```javascript
// WRONG: bulk insert VALUES ? syntax does NOT work with .execute() (prepared statements)
await connection.execute('INSERT INTO products (name, price) VALUES ?', [values]);  // throws/fails!

// CORRECT: use .query() for this specific bulk-insert syntax (not a true prepared statement)
await connection.query('INSERT INTO products (name, price) VALUES ?', [values]);
```

---

## 🧠 Tricky Interview Question

```javascript
const [rows1] = await connection.execute('SELECT * FROM products WHERE id = ?', [1]);
const [rows2] = await connection.execute('SELECT * FROM products WHERE id = ?', ['1']);
// id column is INT. Do both queries return the same result?
```
Answer: **Yes, both return the same result.** mysql2's prepared statement protocol handles type coercion at the protocol level — when a string `'1'` is bound to a parameter being compared against an INT column, MySQL's server-side query execution performs the same numeric comparison it would for the actual integer `1`. This is different from the earlier `process.env` gotcha (topic 140) where JS-level string concatenation caused issues — here, the comparison happens INSIDE MySQL's query engine, which applies its own type coercion rules for `WHERE` clause comparisons, not JavaScript's. This flexibility is convenient but can mask bugs (e.g., unexpectedly matching `'1abc'` depending on MySQL's strict mode settings) — defensive code often still validates/converts types before binding, especially in SQL mode considerations.

---

## ⚫ Interview Questions + Answers

Q1: What is the practical difference between `connection.query()` and `connection.execute()` in mysql2?
A1: `.execute()` uses MySQL's binary PREPARED STATEMENT protocol: the SQL text (with `?` placeholders) is sent once and compiled/cached on the server, then the SAME prepared statement can be reused with different parameter values — faster for repeated queries, and inherently protected against SQL injection for the parameterized values. `.query()` sends the query as plain text (client-side escaping handles placeholders) — simpler, supports some syntax `.execute()` doesn't (like the `VALUES ?` bulk-insert shorthand), but doesn't benefit from server-side statement caching.

Q2: How does mysql2 handle MySQL 8's default authentication plugin, and why did the old `mysql` package struggle with it?
A2: MySQL 8 changed its default authentication plugin to `caching_sha2_password` (more secure than the older `mysql_native_password`). The original `mysql` npm package was built before this change and didn't support the new plugin's handshake out of the box, causing `ER_NOT_SUPPORTED_AUTH_MODE` errors when connecting to fresh MySQL 8 installations. `mysql2` was built with native support for `caching_sha2_password` from early on, making it compatible with modern MySQL 8 servers without needing to downgrade the server's auth plugin as a workaround.

Q3: What does `FOR UPDATE` do in a `SELECT ... FOR UPDATE` query within a transaction?
A3: It places a row-level lock on the selected rows for the duration of the transaction, preventing other transactions from modifying (or sometimes even reading, depending on isolation level) those same rows until the current transaction commits or rolls back. This is essential for patterns like "check stock, then deduct stock" to avoid a RACE CONDITION where two concurrent requests both read the same stock value before either updates it, potentially overselling inventory.

Q4: Why might you configure `dateStrings: true` in mysql2's connection options?
A4: By default, mysql2 converts MySQL `DATETIME`/`DATE` columns into JavaScript `Date` objects, which apply the Node process's LOCAL TIMEZONE during conversion — this can cause subtle bugs/surprises if your server's timezone differs from what you expect, or if you need the EXACT string as stored in MySQL without any timezone interpretation. Setting `dateStrings: true` returns these columns as raw strings (e.g., `'2024-03-15 10:30:00'`) exactly as MySQL stores them, giving you explicit control over how/when to parse them into Date objects (if at all), avoiding implicit timezone conversion bugs.

Q5: What's a practical use case for `multipleStatements: true`, and why is it generally discouraged?
A5: It allows sending multiple semicolon-separated SQL statements in a SINGLE `.query()` call (e.g., running a multi-step migration script). It's discouraged for regular application query code because it SIGNIFICANTLY increases SQL injection risk — if ANY user input ever reaches a query string with this option enabled, an attacker could potentially inject an entirely SECOND statement (`'; DROP TABLE users; --`) that would actually execute, since the driver is explicitly configured to allow multiple statements per call. It's typically reserved for controlled, non-user-facing contexts like running migration files.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any new Node.js project connecting to MySQL/MariaDB — mysql2 is the modern standard choice over the legacy `mysql` package.
- You need Promise/async-await support, modern MySQL 8 auth, or prepared statement performance.

❌ Avoid when:
- An existing legacy project deeply tied to the older `mysql` package's specific callback patterns might require a careful migration rather than an immediate switch — though migrating is still recommended for new feature work.

---

## 📊 Visual Diagram

```
mysql2 API SURFACE:
──────────────────────────────────────────────────────────

  require('mysql2')          → callback-based API (legacy style)
  require('mysql2/promise')  → Promise-based API (recommended, async/await)

  connection.query(sql, params)    → plain text query, client-side param escaping
  connection.execute(sql, params)  → prepared statement, server-side caching

  mysql.createConnection(config)   → single connection
  mysql.createPool(config)        → connection pool (production recommended)

  connection.beginTransaction() ──► execute queries ──► commit() or rollback()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Prepared statement | Precompiled, reusable parameterized query | Precompiled, reusable parameterized query |
| Transaction | Group of queries executed atomically | Atomically execute होने वाली queries का group |
| Row lock (FOR UPDATE) | Prevents concurrent modification of selected rows | Selected rows का concurrent modification रोकना |
| decimalNumbers | Config returning DECIMAL as JS number | DECIMAL को JS number की तरह return करना |
| dateStrings | Config returning DATETIME as raw string | DATETIME को raw string की तरह return करना |
| Batch insert | Inserting multiple rows in one query | एक query में multiple rows insert करना |

---

## ⚡ 3-Line Summary
English:
1. mysql2 is the modern, Promise-supporting, performance-improved successor to the legacy `mysql` package, with native MySQL 8 authentication support.
2. Use `.execute()` for repeated parameterized queries (prepared statements) and `.query()` for plain text or bulk-insert `VALUES ?` syntax.
3. Configure `decimalNumbers`/`dateStrings` deliberately, and use transactions with `FOR UPDATE` row locks for race-condition-sensitive operations.

Hindi:
1. mysql2 legacy `mysql` package का modern, Promise-supporting successor है, MySQL 8 authentication support के साथ।
2. Repeated parameterized queries के लिए `.execute()`, plain text/bulk-insert के लिए `.query()` use करो।
3. `decimalNumbers`/`dateStrings` deliberately configure करो, race-condition-sensitive operations के लिए `FOR UPDATE` के साथ transactions use करो।

---

## ➡️ Next Topic
**145. Connection Pooling in Node** — Multiple connections efficiently manage करना high-traffic apps के लिए।
