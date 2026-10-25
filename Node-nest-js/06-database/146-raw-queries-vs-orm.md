# 146. Raw Queries vs ORM
# हिंदी में: Raw Queries vs ORM

---

## 🔵 Simple Definition (English)
**Raw queries** are SQL strings written and executed directly against the database driver — full control, no abstraction. An **ORM (Object-Relational Mapper)** like Sequelize/Prisma/TypeORM lets you interact with the database using JavaScript objects/methods, auto-generating SQL behind the scenes — trading some control for productivity, safety, and portability.

## 🔵 सरल परिभाषा (Hindi)
**Raw queries** SQL strings हैं जो database driver के against directly लिखी और execute की जाती हैं — पूरा control, कोई abstraction नहीं। **ORM** (जैसे Sequelize/Prisma) JavaScript objects/methods से database के साथ interact करने देता है, SQL automatically generate होता है — कुछ control की कीमत पर productivity, safety, portability मिलती है।

---

## 🔴 Problem it Solves
Writing raw SQL for every operation means manually handling parameterization (SQL injection risk if done wrong), writing boilerplate CRUD operations repeatedly across every table, manually mapping result rows to JS objects, and database-specific syntax making it hard to switch databases later. ORMs solve this by providing a consistent JS API (`User.findOne({ where: { email } })`) that auto-generates safe parameterized SQL, handles relationships/joins declaratively, provides migrations for schema versioning, and abstracts away some database-specific syntax differences — at the cost of a learning curve, potential performance overhead, and sometimes awkward escape hatches for complex queries.

## 🔴 यह क्यों बना? (Hindi)
हर operation के लिए raw SQL लिखना मतलब manually parameterization handle करना, हर table के लिए repeated CRUD boilerplate लिखना, result rows को manually JS objects में map करना, database-specific syntax से database switch करना मुश्किल होना। ORMs इसे solve करते हैं consistent JS API से जो safe parameterized SQL auto-generate करती है, relationships/joins declaratively handle करती है, migrations देती है — कीमत है learning curve और कभी-कभी performance overhead।

---

## 🟢 How it Works — Step by Step

Step 1 → **Raw queries**: write SQL text with placeholders, bind parameters via driver (`mysql2.execute(sql, params)`), manually map result rows if needed
Step 2 → **ORM**: define models (JS classes) mapping to tables, with fields/types/relationships declared once
Step 3 → ORM translates method calls (`Product.findAll({ where: { price: { [Op.gt]: 500 } } })`) into equivalent parameterized SQL internally
Step 4 → ORM handles relationships: `User.findOne({ include: Order })` auto-generates the appropriate JOIN or separate queries, hydrating nested JS objects
Step 5 → ORM provides migrations: versioned schema change scripts (`npx sequelize migration:generate`) that can be applied/rolled back consistently across environments
Step 6 → For complex/performance-critical queries ORMs struggle to express well, most ORMs provide an "escape hatch" to run raw SQL (`sequelize.query(sql, { replacements })`) while still benefiting from the connection pool/config the ORM manages
Step 7 → Choose per use case: simple CRUD-heavy apps benefit most from ORM productivity; performance-critical paths or complex analytical queries often use raw SQL even within an otherwise ORM-based codebase

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Raw queries: SQL text लिखो, placeholders से parameters bind करो
Step 2 → ORM: models define करो tables map करने के लिए
Step 3 → ORM method calls को parameterized SQL में translate करता है
Step 4 → ORM relationships handle करता है (JOINs auto-generate)
Step 5 → ORM migrations provide करता है schema changes के लिए
Step 6 → Complex queries के लिए ORM में raw SQL escape hatch होता है
Step 7 → Use case के अनुसार चुनो — CRUD-heavy पर ORM, performance-critical पर raw SQL

---

## 🟡 Real World Example
**Zomato's codebase (hypothetical realistic split):** The core restaurant/menu/order CRUD operations (90% of endpoints) use Sequelize ORM for productivity — defining `Restaurant`, `MenuItem`, `Order` models with relationships, letting the team move fast without writing repetitive SQL. BUT the analytics dashboard showing "top 10 restaurants by revenue this month, grouped by city, with complex window functions" is written as RAW SQL — because expressing this efficiently (with specific index hints and aggregate functions) through the ORM's query builder would be awkward, less readable, and potentially generate suboptimal SQL compared to a hand-tuned query.

## 🟡 Real Example Hindi mein
**Zomato का codebase:** Core restaurant/menu/order CRUD operations (90% endpoints) Sequelize ORM use करते हैं productivity के लिए। पर analytics dashboard जैसे complex queries (window functions, aggregations) raw SQL में लिखे जाते हैं — ORM से express करना awkward और suboptimal होता।

---

## 💻 Code Example — Basic

```javascript
// comparison-basic.js — same operation, raw query vs ORM side by side
// Run with: node comparison-basic.js (requires MySQL + mysql2 + sequelize set up)

const mysql = require('mysql2/promise');
const { Sequelize, DataTypes } = require('sequelize');

async function rawQueryExample() {
  const connection = await mysql.createConnection({
    host: 'localhost', user: 'root', password: 'password', database: 'shop',
  });

  // ─── RAW: manually write SQL, bind params, get back raw rows ───────────────
  const [rows] = await connection.execute(
    'SELECT id, name, price FROM products WHERE category = ? AND price > ? ORDER BY price DESC',
    ['electronics', 500]
  );
  console.log('Raw query result:', rows);
  await connection.end();
}

async function ormExample() {
  const sequelize = new Sequelize('shop', 'root', 'password', { host: 'localhost', dialect: 'mysql' });

  // ─── ORM: define model once (typically in its own file, done here for brevity) ─
  const Product = sequelize.define('Product', {
    name: DataTypes.STRING,
    price: DataTypes.DECIMAL(10, 2),
    category: DataTypes.STRING,
  });

  // ─── Equivalent query via ORM method calls, no SQL string written ───────────
  const { Op } = require('sequelize');
  const products = await Product.findAll({
    where: { category: 'electronics', price: { [Op.gt]: 500 } },
    order: [['price', 'DESC']],
    attributes: ['id', 'name', 'price'],
  });
  console.log('ORM query result:', products.map((p) => p.toJSON()));

  await sequelize.close();
}

rawQueryExample().then(ormExample).catch(console.error);
```

## 💻 Code Example — Advanced

```javascript
// comparison-advanced.js — hybrid approach: ORM for CRUD, raw SQL for complex analytics

const { Sequelize, DataTypes, Op } = require('sequelize');

const sequelize = new Sequelize('shop', 'root', 'password', { host: 'localhost', dialect: 'mysql' });

const Order = sequelize.define('Order', {
  customerId: DataTypes.INTEGER,
  total: DataTypes.DECIMAL(10, 2),
  city: DataTypes.STRING,
  createdAt: DataTypes.DATE,
});

// ─── 1. SIMPLE CRUD: ORM is clean and productive here ────────────────────────
async function createOrder(customerId, total, city) {
  return Order.create({ customerId, total, city });  // auto-generates INSERT, returns hydrated object
}

async function getCustomerOrders(customerId) {
  return Order.findAll({
    where: { customerId },
    order: [['createdAt', 'DESC']],
    limit: 10,
  });
}

// ─── 2. COMPLEX ANALYTICS: raw SQL via sequelize.query() escape hatch ────────
// Window functions, complex GROUP BY + aggregates are awkward/impossible cleanly via ORM query builder
async function getTopCitiesByRevenue(month) {
  const [results] = await sequelize.query(
    `
    SELECT
      city,
      SUM(total) AS revenue,
      COUNT(*) AS order_count,
      RANK() OVER (ORDER BY SUM(total) DESC) AS city_rank
    FROM orders
    WHERE MONTH(created_at) = :month
    GROUP BY city
    ORDER BY revenue DESC
    LIMIT 10
    `,
    { replacements: { month } }  // still parameterized — raw SQL doesn't mean unsafe!
  );
  return results;
}

// ─── 3. ORM STILL MANAGES THE CONNECTION POOL FOR BOTH APPROACHES ────────────
// sequelize.query() uses the SAME underlying connection pool as sequelize.define() models —
// you get ORM's connection management benefits even when writing raw SQL through it.

async function main() {
  await createOrder(101, 2500, 'Bangalore');
  const orders = await getCustomerOrders(101);
  console.log('Customer orders (via ORM):', orders.length);

  const topCities = await getTopCitiesByRevenue(3);  // March
  console.log('Top cities by revenue (via raw SQL):', topCities);

  await sequelize.close();
}

main().catch(console.error);

module.exports = { createOrder, getCustomerOrders, getTopCitiesByRevenue };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — hybrid approach exposed via Express routes
const express = require('express');
const { Sequelize, Op } = require('sequelize');
const { createOrder, getCustomerOrders, getTopCitiesByRevenue } = require('./comparison-advanced');

const app = express();
app.use(express.json());

// Standard CRUD endpoint — ORM keeps this concise and safe
app.post('/orders', async (req, res) => {
  try {
    const { customerId, total, city } = req.body;
    const order = await createOrder(customerId, total, city);
    res.status(201).json(order);
  } catch (err) {
    res.status(500).json({ error: 'Order creation failed' });
  }
});

app.get('/orders/customer/:id', async (req, res) => {
  const orders = await getCustomerOrders(req.params.id);
  res.json(orders);
});

// Analytics endpoint — raw SQL for a query the ORM can't express cleanly
app.get('/analytics/top-cities', async (req, res) => {
  try {
    const { month } = req.query;
    const data = await getTopCitiesByRevenue(Number(month));
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: 'Analytics query failed' });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `sequelize.query()` with string concatenation, defeating ORM's safety
```javascript
// WRONG: raw query via ORM's escape hatch, but built with string concatenation
const city = req.query.city;
await sequelize.query(`SELECT * FROM orders WHERE city = '${city}'`);  // SQL injection risk, same as pure raw SQL!

// CORRECT: use replacements/bind parameters even within the ORM's raw query method
await sequelize.query('SELECT * FROM orders WHERE city = :city', {
  replacements: { city },
});
```

❌ Mistake 2: Forcing every query through the ORM even when it fights you
```javascript
// WRONG: contorting a complex analytical query into awkward, hard-to-read ORM syntax
// just to avoid "breaking the pattern" of always using the ORM
const results = await Order.findAll({
  attributes: [[sequelize.fn('SUM', sequelize.col('total')), 'revenue'], 'city'],
  group: ['city'],
  // ... trying to force RANK() OVER() through literal() hacks, fragile and unreadable
});

// CORRECT: use the ORM's raw query escape hatch for queries it doesn't model well
const [results] = await sequelize.query(`SELECT city, SUM(total) AS revenue, RANK() OVER (...) ...`);
```

---

## 🧠 Tricky Interview Question

```javascript
// Using Sequelize:
const products = await Product.findAll({ where: { price: 500 } });
console.log(products[0] instanceof Product);  // ?
console.log(products[0].price);                // ?
console.log(typeof products[0].price);         // ?
```
Answer: `products[0] instanceof Product` is **`true`** — Sequelize returns hydrated MODEL INSTANCES, not plain objects, giving you instance methods (`.save()`, `.destroy()`, `.toJSON()`). `products[0].price` returns the price value, but `typeof products[0].price` is typically **`'string'`**, NOT `'number'` — because Sequelize (like mysql2 directly) returns `DECIMAL` columns as STRINGS by default to avoid floating-point precision loss (critical for money values). This surprises many developers expecting a JS number; the fix is either configuring the model field as `DataTypes.DECIMAL` with explicit getter/casting, or converting with `Number()` when doing arithmetic — the same underlying decimal-precision consideration that applies at the raw mysql2 driver level (topic 144) surfaces through the ORM too, since the ORM doesn't change the fundamental DB type-mapping behavior.

---

## ⚫ Interview Questions + Answers

Q1: What are the main productivity benefits of using an ORM over raw SQL?
A1: (1) Less boilerplate — CRUD operations become one-line method calls instead of hand-written SQL + result mapping for every table. (2) Declarative relationships — `include`/`populate` auto-generates JOINs and hydrates nested objects. (3) Migrations — versioned, trackable schema changes applied consistently across environments. (4) Built-in protection against SQL injection by default (parameterization handled automatically). (5) Some database portability — switching from MySQL to Postgres often requires minimal code changes since the ORM abstracts dialect differences (though not always perfectly).

Q2: What are the main downsides or risks of relying heavily on an ORM?
A2: (1) Performance overhead — ORMs can generate inefficient SQL (e.g., N+1 query problems when relationships aren't eagerly loaded correctly, or over-fetching columns). (2) Abstraction leakage — complex queries (window functions, specific index hints, recursive CTEs) are often awkward or impossible to express cleanly, forcing raw SQL escape hatches anyway. (3) Learning curve and "magic" — debugging what SQL an ORM actually generates requires enabling query logging, adding a layer of indirection when troubleshooting. (4) Over-abstraction can hide important database-specific optimizations a hand-tuned query would exploit.

Q3: What is the "N+1 query problem" and how does it relate to ORM usage?
A3: It occurs when fetching a list of N parent records, then making ONE ADDITIONAL query PER record to fetch related child data (e.g., fetching 100 orders, then running 100 separate queries to get each order's customer) — resulting in 101 total queries instead of 1-2 efficient JOINed queries. ORMs make this mistake easy to fall into accidentally (lazy-loading relationships by default) unless you explicitly use eager loading (`include: [Customer]` in Sequelize, `.populate()` in Mongoose) to fetch related data in the SAME query via JOIN or a single batched follow-up query.

Q4: Is raw SQL through an ORM's `.query()` method still protected against SQL injection?
A4: It CAN be, but it's not automatic the way model-based ORM methods are — you must still explicitly use parameterized placeholders (`replacements`/`bind` in Sequelize) rather than string-concatenating user input into the raw SQL text. The ORM's escape hatch gives you the SAME raw-SQL responsibility as using the underlying driver directly; the ORM doesn't magically sanitize string-concatenated raw SQL just because it's called through `sequelize.query()`.

Q5: In what scenario would a team deliberately choose raw SQL over an ORM for an ENTIRE project, not just specific queries?
A5: When the team has deep SQL expertise and performance is the top priority for a data-intensive, query-heavy application (e.g., a high-frequency trading system, a complex reporting/BI platform with heavy aggregation needs) where ORM abstraction overhead and potential inefficiency in generated SQL are unacceptable. Also when the database schema is extremely complex with many specialized queries (recursive CTEs, custom window functions, database-specific features) that an ORM would constantly fight against, making the ORM's productivity benefit net-negative for that specific codebase's query patterns.

---

## 🔷 When to Use + When Not to Use
✅ Use ORM when:
- Standard CRUD-heavy applications where productivity, consistency, and built-in safety matter most.
- Teams with mixed SQL expertise who benefit from a safer, more guided API.

✅ Use raw SQL when:
- Complex analytical queries, performance-critical hot paths, or database-specific features (window functions, full-text search tuning) the ORM can't express well.

❌ Avoid pure raw SQL everywhere when:
- It leads to repetitive, error-prone boilerplate and inconsistent parameterization discipline across a large team — an ORM (or at least a query builder like Knex) reduces this risk.

❌ Avoid forcing everything through the ORM when:
- It produces unreadable, inefficient, or fragile query-builder code for genuinely complex queries — use the escape hatch.

---

## 📊 Visual Diagram

```
RAW SQL vs ORM — DECISION FLOW:
──────────────────────────────────────────────────────────

  Is it standard CRUD (find/create/update/delete by simple conditions)?
       │
      YES ──► Use ORM model methods (Product.findAll, Order.create, etc.)
       │
      NO (complex aggregation, window functions, specific performance tuning)
       │
       ▼
  Use raw SQL — either via the driver directly, OR via the ORM's
  .query() escape hatch (keeps connection pool/config shared)
       │
       ▼
  EITHER WAY: always parameterize (? placeholders / :named replacements)
  — raw SQL safety is YOUR responsibility, ORM doesn't auto-protect this path
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ORM | Maps DB tables to JS objects/classes | DB tables को JS objects/classes से map करना |
| Query builder | Programmatic API constructing SQL | SQL बनाने वाली programmatic API |
| N+1 problem | One query per related record instead of a JOIN | हर related record के लिए अलग query, JOIN नहीं |
| Eager loading | Fetching related data in the same/batched query | Related data को same query में fetch करना |
| Escape hatch | Raw SQL option within an ORM | ORM के अंदर raw SQL का option |
| Migration | Versioned, trackable schema change script | Versioned schema change script |

---

## ⚡ 3-Line Summary
English:
1. Raw queries give full SQL control and potentially better performance but require manual parameterization and boilerplate; ORMs trade some control for productivity, safety defaults, and relationship handling.
2. Use ORM for standard CRUD operations; drop to raw SQL (via the ORM's escape hatch or the driver directly) for complex analytics or performance-critical queries.
3. Raw SQL — whether standalone or through an ORM's `.query()` — must still be explicitly parameterized; the ORM's automatic injection protection only applies to its model-based methods.

Hindi:
1. Raw queries पूरा control और potentially बेहतर performance देती हैं पर manual parameterization चाहिए; ORMs कुछ control की कीमत पर productivity और safety देते हैं।
2. Standard CRUD के लिए ORM use करो; complex analytics या performance-critical queries के लिए raw SQL पर जाओ।
3. Raw SQL — standalone हो या ORM के through — explicitly parameterize करना ज़रूरी है; ORM की automatic protection सिर्फ model-based methods पर लागू होती है।

---

## ➡️ Next Topic
**147. Sequelize ORM — Complete Guide** — Models, associations, query methods का detailed overview।
