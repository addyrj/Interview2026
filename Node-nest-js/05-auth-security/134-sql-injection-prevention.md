# 134. SQL Injection Prevention
# हिंदी में: SQL Injection से बचाव

---

## 🔵 Simple Definition (English)
**SQL Injection (SQLi)** is an attack where malicious SQL code is inserted into a query via unsanitized user input, letting attackers read, modify, or delete database data — or bypass authentication entirely. **Prevention** means never concatenating user input directly into SQL strings — always use parameterized queries/prepared statements or an ORM.

## 🔵 सरल परिभाषा (Hindi)
**SQL Injection (SQLi)** एक attack है जहाँ malicious SQL code unsanitized user input के through query में insert हो जाता है, attackers database data पढ़, बदल, या delete कर सकते हैं — या authentication bypass कर सकते हैं। **Prevention** का मतलब है user input को कभी SQL string में directly concatenate मत करो — हमेशा parameterized queries/prepared statements या ORM use करो।

---

## 🔴 Problem it Solves
If code builds queries by string concatenation (`"SELECT * FROM users WHERE email = '" + email + "'"`), an attacker can enter `' OR '1'='1` as the email, turning the query into `SELECT * FROM users WHERE email = '' OR '1'='1'` — which returns ALL rows (bypassing authentication). Worse, `'; DROP TABLE users; --` could delete the entire table. SQL injection has caused some of history's biggest data breaches. Prevention ensures user input is always treated as DATA, never as executable SQL syntax.

## 🔴 यह क्यों बना? (Hindi)
अगर code string concatenation से queries बनाता है, attacker `' OR '1'='1` जैसा input दे सकता है, जो query को ऐसा बना देता है कि सभी rows return हो जाएं (authentication bypass)। `'; DROP TABLE users; --` पूरी table delete कर सकता है। SQL injection history के सबसे बड़े data breaches का कारण रहा है। Prevention सुनिश्चित करता है कि user input हमेशा DATA की तरह treat हो, कभी executable SQL syntax की तरह नहीं।

---

## 🟢 How it Works — Step by Step

Step 1 → Identify every place user input flows into a SQL query (search, login, filters, sort params)
Step 2 → Replace string concatenation with **parameterized queries** — placeholders (`?` or `$1`) in the query, values passed separately
Step 3 → The database driver sends the query structure and the data SEPARATELY to the DB server — the DB never interprets data as SQL syntax
Step 4 → Use an **ORM** (Sequelize, Prisma, TypeORM) which parameterizes queries automatically under the hood
Step 5 → Apply the **principle of least privilege**: DB user account for the app should have only the permissions it needs (no `DROP`, `ALTER` if not required)
Step 6 → Validate/whitelist input types (e.g., sort column must be from an allowed list, not raw user string) since parameterization doesn't help for dynamic identifiers like table/column names
Step 7 → Use a WAF (Web Application Firewall) and ORM-level logging/monitoring as additional defense layers

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → हर जगह पहचानो जहाँ user input SQL query में जाता है
Step 2 → String concatenation को **parameterized queries** से replace करो
Step 3 → Database driver query structure और data को अलग-अलग भेजता है
Step 4 → **ORM** use करो जो automatically parameterize करे
Step 5 → **Least privilege** apply करो — app का DB user सिर्फ ज़रूरी permissions रखे
Step 6 → Dynamic identifiers (column/table names) के लिए whitelist validate करो
Step 7 → WAF और monitoring को additional layer की तरह use करो

---

## 🟡 Real World Example
**Amazon/Flipkart search bar:** User searches for a product: `SELECT * FROM products WHERE name LIKE '%iPhone%'`. If the search term is concatenated unsafely, an attacker could search for `%'; UPDATE products SET price=1 WHERE id=1; --` attempting to set a product's price to ₹1. Using a parameterized query (`db.query('SELECT * FROM products WHERE name LIKE ?', [`%${term}%`])`) ensures the entire search term — including any SQL-looking characters — is treated as a single string value for the `LIKE` comparison, never as executable SQL.

## 🟡 Real Example Hindi mein
**Amazon/Flipkart search bar:** User product search करता है। अगर search term unsafely concatenate हो, attacker price को ₹1 set करने की कोशिश कर सकता है SQL injection से। Parameterized query use करने से पूरा search term सिर्फ एक string value की तरह treat होता है, executable SQL की तरह कभी नहीं।

---

## 💻 Code Example — Basic

```javascript
// sqli-basic.js — vulnerable vs safe query, using mysql2
// Run with: node sqli-basic.js (requires a running MySQL + mysql2 package)

const mysql = require('mysql2/promise');

async function main() {
  const connection = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'password',
    database: 'shop',
  });

  const userInput = "' OR '1'='1";  // classic SQLi payload

  // ─── VULNERABLE: string concatenation ──────────────────────────────────────
  // const unsafeQuery = `SELECT * FROM users WHERE email = '${userInput}'`;
  // await connection.query(unsafeQuery);
  // Resulting query: SELECT * FROM users WHERE email = '' OR '1'='1'
  // → returns ALL users! Authentication bypassed.

  // ─── SAFE: parameterized query ─────────────────────────────────────────────
  const [rows] = await connection.execute(
    'SELECT * FROM users WHERE email = ?',   // placeholder, not string interpolation
    [userInput]                               // value bound separately
  );
  console.log('Rows returned:', rows.length);
  // The entire malicious string is treated as a literal email value to match —
  // since no email equals "' OR '1'='1", ZERO rows are returned. Attack neutralized.

  await connection.end();
}

main().catch(console.error);
```

## 💻 Code Example — Advanced

```javascript
// sqli-advanced.js — safe dynamic sorting/filtering + ORM comparison

const mysql = require('mysql2/promise');

// ─── 1. SAFE DYNAMIC SORT COLUMN (whitelist approach) ────────────────────────
// Parameterization does NOT work for column/table names (only for values),
// so dynamic identifiers MUST be validated against a whitelist.
const ALLOWED_SORT_COLUMNS = ['price', 'name', 'created_at', 'rating'];
const ALLOWED_SORT_DIRECTIONS = ['ASC', 'DESC'];

async function getProductsSorted(connection, sortBy, direction) {
  // Validate against whitelist — reject anything not explicitly allowed
  if (!ALLOWED_SORT_COLUMNS.includes(sortBy)) {
    throw new Error(`Invalid sort column: ${sortBy}`);
  }
  if (!ALLOWED_SORT_DIRECTIONS.includes(direction.toUpperCase())) {
    throw new Error(`Invalid sort direction: ${direction}`);
  }

  // Safe to interpolate HERE only because both values passed whitelist validation
  const query = `SELECT * FROM products ORDER BY ${sortBy} ${direction.toUpperCase()}`;
  const [rows] = await connection.execute(query);
  return rows;
}

// ─── 2. SAFE DYNAMIC WHERE CLAUSE WITH MULTIPLE OPTIONAL FILTERS ─────────────
async function searchProducts(connection, filters) {
  const conditions = [];
  const values = [];

  if (filters.category) {
    conditions.push('category = ?');   // placeholder
    values.push(filters.category);      // value bound safely
  }
  if (filters.minPrice) {
    conditions.push('price >= ?');
    values.push(filters.minPrice);
  }
  if (filters.search) {
    conditions.push('name LIKE ?');
    values.push(`%${filters.search}%`); // LIKE wildcard is safe — it's still a bound value
  }

  const whereClause = conditions.length ? `WHERE ${conditions.join(' AND ')}` : '';
  const query = `SELECT * FROM products ${whereClause}`;

  const [rows] = await connection.execute(query, values);  // values array matches ? count
  return rows;
}

// ─── 3. SEQUELIZE ORM EQUIVALENT (auto-parameterized) ────────────────────────
// const { Op } = require('sequelize');
// const products = await Product.findAll({
//   where: {
//     category: filters.category,
//     price: { [Op.gte]: filters.minPrice },
//     name: { [Op.like]: `%${filters.search}%` },
//   },
//   order: [[sortBy, direction]],   // Sequelize validates column exists in model
// });
// ORM builds parameterized SQL internally — no manual escaping needed.

module.exports = { getProductsSorted, searchProducts };
```

---

## 🟠 Express.js Integration

```javascript
// server.js
const express = require('express');
const mysql = require('mysql2/promise');
const { searchProducts, getProductsSorted } = require('./sqli-advanced');

const app = express();
app.use(express.json());

let pool;
(async () => {
  pool = mysql.createPool({
    host: 'localhost',
    user: 'app_readonly_user',   // least-privilege: separate restricted DB user
    password: process.env.DB_PASSWORD,
    database: 'shop',
    waitForConnections: true,
    connectionLimit: 10,
  });
})();

// Search endpoint — user input bound safely via parameterized query
app.get('/products/search', async (req, res) => {
  try {
    const { category, minPrice, q } = req.query;
    const rows = await searchProducts(pool, { category, minPrice, search: q });
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: 'Search failed' });
  }
});

// Sorted listing — sortBy/direction validated against whitelist before use
app.get('/products', async (req, res) => {
  try {
    const { sortBy = 'created_at', direction = 'DESC' } = req.query;
    const rows = await getProductsSorted(pool, sortBy, direction);
    res.json(rows);
  } catch (err) {
    // Invalid sort column/direction throws — return 400, not 500
    res.status(400).json({ error: err.message });
  }
});

// Login — the classic injection target, always parameterized
app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  const [rows] = await pool.execute('SELECT * FROM users WHERE email = ? LIMIT 1', [email]);
  if (rows.length === 0) return res.status(401).json({ error: 'Invalid credentials' });
  // ... bcrypt.compare(password, rows[0].passwordHash) happens next
  res.json({ message: 'Checked' });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: String concatenation/template literals directly in SQL
```javascript
// WRONG: directly interpolating user input into the query string
const query = `SELECT * FROM users WHERE id = ${req.params.id}`;
await connection.query(query);  // id = "1 OR 1=1" → returns all users!

// CORRECT: always use placeholders + bound parameters
await connection.execute('SELECT * FROM users WHERE id = ?', [req.params.id]);
```

❌ Mistake 2: Thinking escaping quotes manually is "good enough"
```javascript
// WRONG: manual escaping is error-prone and misses edge cases (encoding tricks, nulls)
const safeEmail = email.replace(/'/g, "\\'");  // naive, incomplete, don't do this
const query = `SELECT * FROM users WHERE email = '${safeEmail}'`;

// CORRECT: let the driver/ORM handle escaping via parameterization — never reinvent it
await connection.execute('SELECT * FROM users WHERE email = ?', [email]);
```

---

## 🧠 Tricky Interview Question

```javascript
// Developer "fixes" SQL injection like this:
const sortBy = req.query.sortBy;  // e.g. "price; DROP TABLE users;"
const query = `SELECT * FROM products ORDER BY ?`;
await connection.execute(query, [sortBy]);
// Does parameterizing the ORDER BY column fix the vulnerability?
```
Answer: **No — this actually breaks the query (or silently does nothing useful), it doesn't fix the vulnerability the right way.** Parameterized placeholders (`?`) work for VALUES (data being compared/inserted), not for SQL **identifiers** like column/table names. MySQL will treat `?` in `ORDER BY ?` as a string literal value, not a column reference — producing an error or a no-op sort, not the intended dynamic sorting. The correct fix is to validate `sortBy` against a hardcoded whitelist array (`['price','name','rating']`) and only then safely interpolate it directly into the query string, since by that point it's a known-safe value, not attacker-controlled.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a parameterized query and simply escaping special characters?
A1: Escaping (e.g., replacing `'` with `\'`) tries to neutralize dangerous characters within the SAME string that gets concatenated into SQL — it's fragile and easy to get wrong (different DBs/encodings have different escaping rules, and attackers find bypasses). Parameterized queries send the SQL structure and the data as two SEPARATE channels to the database driver/server — the data is NEVER parsed as SQL syntax at all, regardless of what characters it contains. This is categorically safer, not just "better escaping."

Q2: Can an ORM like Sequelize or Prisma still be vulnerable to SQL injection?
A2: Yes, if you bypass the ORM's safe query builder and use raw queries with string concatenation — e.g., `sequelize.query(\`SELECT * FROM users WHERE name = '${input}'\`)`. ORMs are safe by default when using their query builder methods (`.findAll({ where: {...} })`), which auto-parameterize, but `sequelize.query()` with manual string building reintroduces the exact same vulnerability as raw SQL.

Q3: What's the "principle of least privilege" in the context of SQL injection defense?
A3: Configure the database user account your app connects with to have ONLY the permissions it actually needs (e.g., `SELECT`, `INSERT`, `UPDATE` on specific tables) — never `DROP`, `ALTER`, or superuser rights, and never access to unrelated databases on the same server. This way, even if an SQL injection vulnerability exists and is exploited, the damage is limited (e.g., attacker can't drop tables or access other databases) because the DB connection itself lacks those permissions.

Q4: How does SQL injection differ from NoSQL injection (e.g., in MongoDB)?
A4: SQL injection exploits string-based query construction. NoSQL injection (common in MongoDB) exploits passing untrusted OBJECTS directly as query filters — e.g., `User.find({ password: req.body.password })` where an attacker sends `{ "password": { "$ne": null } }` as JSON, making MongoDB match ANY non-null password (bypassing auth). Prevention: validate/sanitize input types strictly (reject objects where strings are expected), and use libraries like `express-mongo-sanitize` to strip `$`-prefixed keys from user input.

Q5: Besides parameterized queries, name two other layers of defense against SQL injection.
A5: (1) **Least-privilege DB accounts** — limit what damage a successful injection can do. (2) **Input validation/whitelisting** — especially for dynamic identifiers (sort columns, table names) that can't be parameterized; reject unexpected types/formats early. Additional layers: **WAF (Web Application Firewall)** to detect/block common injection patterns at the network edge, and **error message hygiene** (never leak raw DB errors/stack traces to clients, which can reveal schema details useful for crafting injections).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- ANY query includes user-controlled input (search terms, IDs, filters, login credentials) — always parameterize.
- Building dynamic queries with optional filters — use parameter arrays matched to placeholder count.

❌ Avoid when:
- N/A for parameterization itself — there's no valid reason to skip it. The only exception is validated, whitelisted dynamic identifiers (column/table names) which require a different approach (whitelist, not parameterization).

---

## 📊 Visual Diagram

```
SQL INJECTION ATTACK (vulnerable code):
──────────────────────────────────────────────────────────

  Attacker input: ' OR '1'='1
       │
       ▼
  String concatenation:
  "SELECT * FROM users WHERE email = '" + input + "'"
       │
       ▼
  Resulting query:
  SELECT * FROM users WHERE email = '' OR '1'='1'
       │
       ▼
  '1'='1' is ALWAYS true → ALL rows match ❌ AUTH BYPASSED

WITH PARAMETERIZED QUERY (safe):
  Query template:  SELECT * FROM users WHERE email = ?
  Bound value:     "' OR '1'='1"
       │
       ▼
  DB driver sends query + value SEPARATELY to DB server
       │
       ▼
  DB treats entire string as a literal value to compare
       │
       ▼
  No email matches that literal string → 0 rows ✅ SAFE
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SQL Injection | Malicious SQL inserted via input | Input से insert हुआ malicious SQL |
| Parameterized query | Query with placeholders, data bound separately | Placeholders वाली query, data अलग से bound |
| Prepared statement | Precompiled query template reused with different data | Precompiled query template |
| Least privilege | DB account with minimal needed permissions | Minimal ज़रूरी permissions वाला DB account |
| Whitelist validation | Only allowing known-safe values | सिर्फ known-safe values allow करना |
| NoSQL injection | Object-based query injection (MongoDB etc.) | Object-based query injection |

---

## ⚡ 3-Line Summary
English:
1. SQL injection exploits string concatenation of user input into queries — attackers can bypass auth, read, or destroy data.
2. Always use parameterized queries/prepared statements (or an ORM's safe query builder) — never build SQL via string concatenation.
3. For dynamic identifiers (sort columns) that can't be parameterized, validate against a hardcoded whitelist instead.

Hindi:
1. SQL injection user input को query में concatenate करने का फायदा उठाता है — auth bypass, data read/destroy कर सकता है।
2. हमेशा parameterized queries/prepared statements (या ORM) use करो — string concatenation कभी नहीं।
3. Dynamic identifiers के लिए whitelist validation use करो, parameterization वहाँ काम नहीं करता।

---

## ➡️ Next Topic
**135. Helmet.js — All Headers Explained** — Security headers जो Express app को automatically protect करते हैं।
