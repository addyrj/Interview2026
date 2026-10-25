# 221. Database Query Optimization
# हिंदी में: Database Query Optimization — Slow Queries को Fast बनाना

---

## 🔵 Simple Definition (English)
**Database query optimization** means restructuring queries and database schema (indexes, query shape, selected columns) so the database can find and return data with the least possible work — avoiding full table scans, redundant joins, and over-fetching. The single highest-leverage technique is almost always **adding the right index**.

## 🔵 सरल परिभाषा (Hindi)
**Database query optimization** का मतलब है queries और database schema (indexes, query shape, selected columns) को इस तरह restructure करना कि database कम से कम काम में data ढूंढ और return कर सके — full table scans, redundant joins, over-fetching से बचते हुए। सबसे ज़्यादा असर करने वाली technique almost हमेशा **सही index add करना** होती है।

---

## 🔴 Problem it Solves
An unoptimized query (missing index, selecting all columns when only 2 are needed, or an inefficient JOIN) might scan every row in a million-row table just to find a handful of matches — taking seconds instead of milliseconds, and getting worse as the table grows. Under load, slow queries also hold database connections longer, starving other requests and causing cascading slowdowns across the whole app. Optimization directly reduces latency and lets the same database hardware handle far more traffic.

## 🔴 यह क्यों बना? (Hindi)
एक unoptimized query (missing index, सिर्फ 2 columns चाहिए फिर भी सब select करना, या inefficient JOIN) एक million-row table में हर row scan कर सकती है सिर्फ कुछ matches ढूंढने के लिए — seconds लगते हैं milliseconds के बजाय, और table बढ़ने पर और बुरा होता जाता है। Load में, slow queries database connections को भी ज़्यादा समय तक hold करती हैं, बाकी requests को starve करती हैं। Optimization latency directly कम करता है और same hardware से ज़्यादा traffic handle होने देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Find slow queries: enable slow query logging (`slow_query_log` in MySQL, `log_min_duration_statement` in Postgres), or use APM tools that trace DB calls
Step 2 → Run `EXPLAIN` (or `EXPLAIN ANALYZE` in Postgres) on the slow query to see the database's execution plan — look for "Seq Scan"/"Full Table Scan" (bad, scans everything) vs "Index Scan" (good, uses an index)
Step 3 → Add an index on columns used in `WHERE`, `JOIN`, and `ORDER BY` clauses — this is usually the single biggest win
Step 4 → Select only needed columns (`SELECT id, name` instead of `SELECT *`) to reduce data transfer and memory use
Step 5 → Restructure N+1 patterns into a single batched query (`WHERE id IN (...)`) instead of looping with individual queries
Step 6 → Re-run `EXPLAIN ANALYZE` after the change to confirm the plan now uses the index and actual execution time dropped

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Slow queries ढूंढो: slow query logging enable करो (MySQL में `slow_query_log`, Postgres में `log_min_duration_statement`), या APM tools use करो
Step 2 → Slow query पर `EXPLAIN` (या Postgres में `EXPLAIN ANALYZE`) चलाओ execution plan देखने के लिए — "Seq Scan"/"Full Table Scan" (बुरा, सब कुछ scan) vs "Index Scan" (अच्छा, index use) देखो
Step 3 → `WHERE`, `JOIN`, `ORDER BY` में use होने वाले columns पर index add करो — ये आम तौर पर सबसे बड़ा win होता है
Step 4 → सिर्फ ज़रूरी columns select करो (`SELECT id, name` न कि `SELECT *`) data transfer और memory use कम करने के लिए
Step 5 → N+1 patterns को single batched query में restructure करो (`WHERE id IN (...)`) individual queries के loop के बजाय
Step 6 → Change के बाद फिर `EXPLAIN ANALYZE` चलाओ confirm करने के लिए कि plan अब index use करता है और actual execution time कम हुआ

---

## 🟡 Real World Example
**Flipkart's order-history page** (`GET /orders?userId=X`) was taking 2.5 seconds to load for power users with thousands of past orders. Running `EXPLAIN ANALYZE` on the query revealed a "Seq Scan" on the `orders` table — there was NO index on `user_id`, so Postgres scanned all 200 million rows in the table to find the handful belonging to that user. Adding `CREATE INDEX idx_orders_user_id ON orders(user_id)` turned the Seq Scan into an Index Scan — the same query now returns in 8ms, a 300x improvement from a single `CREATE INDEX` statement.

## 🟡 Real Example Hindi mein
**Flipkart का order-history page** (`GET /orders?userId=X`) power users के लिए 2.5 seconds ले रहा था जिनके हज़ारों past orders थे। Query पर `EXPLAIN ANALYZE` चलाने पर पता चला "Seq Scan" हो रहा था `orders` table पर — `user_id` पर कोई index नहीं था, तो Postgres 200 million rows scan करता था उस user के कुछ orders ढूंढने के लिए। `CREATE INDEX idx_orders_user_id ON orders(user_id)` add करने से Seq Scan, Index Scan बन गया — same query अब 8ms में return होती है, सिर्फ एक `CREATE INDEX` से 300x improvement।

---

## 💻 Code Example — Basic

```javascript
// slow-query-demo.js — demonstrating the difference an index makes
// Using 'pg' (node-postgres) directly for clarity

const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

async function findUserOrdersSlow(userId) {
  // Without an index on user_id, this does a full table scan on large tables
  const result = await pool.query(
    'SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC',
    [userId]
  );
  return result.rows;
}

async function analyzeQuery(userId) {
  // EXPLAIN ANALYZE shows the REAL execution plan and actual timing
  const result = await pool.query(
    'EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC',
    [userId]
  );
  result.rows.forEach(row => console.log(row['QUERY PLAN']));
  // Look for "Seq Scan on orders" (bad) vs "Index Scan using idx_orders_user_id" (good)
}

// Run this migration to fix the slow query:
// CREATE INDEX idx_orders_user_id ON orders(user_id);
// For queries that filter AND sort, a composite index helps even more:
// CREATE INDEX idx_orders_user_created ON orders(user_id, created_at DESC);
```

```javascript
// select-only-needed-columns.js — reducing over-fetching
// BAD: SELECT * pulls every column, including large unused ones (e.g. a JSON blob)
async function getOrderSummariesBad() {
  const result = await pool.query('SELECT * FROM orders LIMIT 100');
  return result.rows; // wastes bandwidth/memory on unused columns like `raw_payment_response`
}

// GOOD: select only the columns the endpoint actually needs
async function getOrderSummariesGood() {
  const result = await pool.query(
    'SELECT id, user_id, amount, status, created_at FROM orders LIMIT 100'
  );
  return result.rows; // smaller payload, less memory, faster serialization
}
```

## 💻 Code Example — Advanced

```javascript
// orm-query-optimization.js — using Mongoose/Sequelize patterns correctly

// ─── MONGOOSE: lean() + select() + proper indexing ────────────────────────
const mongoose = require('mongoose');

const orderSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, index: true }, // indexed field
  status: String,
  amount: Number,
  createdAt: { type: Date, default: Date.now },
});
// Composite index for the common query pattern: filter by user, sort by date
orderSchema.index({ userId: 1, createdAt: -1 });

const Order = mongoose.model('Order', orderSchema);

async function getUserOrdersOptimized(userId) {
  return Order.find({ userId })
    .select('status amount createdAt') // only needed fields — reduces payload
    .sort({ createdAt: -1 })
    .limit(20)                          // paginate, don't return everything
    .lean();                            // skip Mongoose document overhead (returns plain JS objects, faster)
}

// ─── SEQUELIZE: avoiding N+1 with eager loading ───────────────────────────
const { Order: SeqOrder, Restaurant } = require('./models');

// BAD: N+1 — separate query per order to get its restaurant
async function getOrdersBad() {
  const orders = await SeqOrder.findAll({ limit: 50 });
  for (const order of orders) {
    order.restaurant = await Restaurant.findByPk(order.restaurantId); // 50 extra queries!
  }
  return orders;
}

// GOOD: eager load with `include` — Sequelize generates a single JOIN query
async function getOrdersGood() {
  return SeqOrder.findAll({
    limit: 50,
    include: [{ model: Restaurant, attributes: ['id', 'name'] }], // single JOIN query
    attributes: ['id', 'amount', 'status'], // only needed order columns
  });
}

// ─── PAGINATION: keyset pagination beats OFFSET for large tables ─────────
// BAD: OFFSET gets progressively slower — DB must scan+discard all skipped rows
async function getPageOffsetBad(page, pageSize = 20) {
  return pool.query(
    'SELECT * FROM orders ORDER BY id LIMIT $1 OFFSET $2',
    [pageSize, page * pageSize] // OFFSET 100000 means scanning 100000 rows to skip them!
  );
}

// GOOD: keyset (cursor) pagination — uses the index directly, constant time
async function getPageKeysetGood(lastSeenId, pageSize = 20) {
  return pool.query(
    'SELECT * FROM orders WHERE id > $1 ORDER BY id LIMIT $2',
    [lastSeenId, pageSize] // jumps directly via index, no scanning/discarding
  );
}
```

---

## 🟠 Express.js Integration

```javascript
// middleware/queryTimer.js — log slow DB queries automatically in Express routes
function timeQuery(label) {
  return async function wrapper(queryFn) {
    const start = Date.now();
    const result = await queryFn();
    const duration = Date.now() - start;
    if (duration > 200) { // threshold for "slow" — tune per app
      console.warn(`SLOW QUERY [${label}]: ${duration}ms`);
    }
    return result;
  };
}

app.get('/orders', async (req, res) => {
  const timer = timeQuery('getUserOrders');
  const orders = await timer(() => getUserOrdersOptimized(req.user.id));
  res.json(orders);
});

// Pagination endpoint using keyset pagination (avoids OFFSET performance cliff)
app.get('/orders/page', async (req, res) => {
  const lastSeenId = req.query.cursor ? Number(req.query.cursor) : 0;
  const orders = await getPageKeysetGood(lastSeenId, 20);
  res.json({
    orders: orders.rows,
    nextCursor: orders.rows.length ? orders.rows[orders.rows.length - 1].id : null,
  });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Adding an index on every column "just in case"
```javascript
// WRONG: indexes on EVERY column slow down writes (every INSERT/UPDATE
// must update every index) and waste storage, often with little read benefit
// CREATE INDEX on status, CREATE INDEX on amount, CREATE INDEX on notes...

// CORRECT: index only columns actually used in WHERE/JOIN/ORDER BY of
// real, frequent queries — verify with EXPLAIN ANALYZE before and after
```

❌ Mistake 2: Using `OFFSET`-based pagination on large tables
```javascript
// WRONG: gets dramatically slower as page number increases
// (OFFSET 1000000 forces the DB to scan and discard a million rows)
'SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 1000000'

// CORRECT: keyset/cursor pagination — constant time regardless of "page depth"
'SELECT * FROM orders WHERE id > $1 ORDER BY id LIMIT 20'
```

---

## 🧠 Tricky Interview Question

```sql
-- Table `orders` has 10 million rows and an index on `user_id`.
SELECT * FROM orders WHERE user_id = 123 AND status != 'cancelled';
-- ❓ Does the index on user_id get used efficiently here?
```
Answer: The index on `user_id` DOES get used to quickly find the subset of rows for `user_id = 123` — that part is efficient. However, `status != 'cancelled'` is a **negation filter**, which databases generally CANNOT use an index to accelerate (indexes are efficient for equality/range lookups, not "not equal to" conditions) — so after using the `user_id` index to narrow down candidate rows, the database still has to scan THOSE rows and check the `status` condition one by one. For a user with few orders this is fine, but if you frequently filter on `status`, consider a composite index `(user_id, status)` or restructure the query to use `status IN ('placed', 'confirmed', 'delivered')` (a positive list) instead of `!=`, which composite indexes can leverage more effectively.

---

## ⚫ Interview Questions + Answers

Q1: What does `EXPLAIN ANALYZE` show and why is it the first step in query optimization?
A1: It shows the database's ACTUAL execution plan for a query — which indexes (if any) were used, whether it did a sequential/full table scan, estimated vs actual row counts, and real timing per step. It's essential because guessing why a query is slow is unreliable; `EXPLAIN ANALYZE` gives concrete evidence of exactly where time is being spent (e.g., "Seq Scan on orders (cost=0.00..45000.00 rows=10000000) actual time=1200ms").

Q2: What's the difference between a single-column index and a composite (multi-column) index?
A2: A single-column index speeds up queries filtering/sorting by just that one column. A composite index on `(user_id, created_at)` speeds up queries that filter by `user_id` AND sort/filter by `created_at` TOGETHER, matching that exact column order — the database can use the leftmost columns of a composite index even if only those are used, but it generally can't efficiently use just the SECOND column alone without the first.

Q3: Why does `SELECT *` hurt performance even if the query itself uses an index correctly?
A3: `SELECT *` fetches every column's data, including large or unused ones (JSON blobs, text fields), increasing network transfer, memory on both DB and app side, and serialization/deserialization time — even if finding the ROWS was fast via an index, transferring unnecessary COLUMN data still adds real latency and resource cost, especially at scale.

Q4: How does the N+1 query problem relate to query optimization, and what's the standard fix?
A4: N+1 happens when code fetches a list of N items with one query, then loops to fetch a related item PER entry with N additional queries (total N+1 queries instead of a constant few). Fix: use the ORM's eager-loading feature (`include` in Sequelize, `.populate()` in Mongoose) to generate a single JOIN/batched query, or manually batch with `WHERE id IN (...)` — turning N+1 round-trips into 1-2.

Q5: Why is OFFSET-based pagination a performance problem at scale, and what replaces it?
A5: `OFFSET n` forces the database to still scan and discard the first `n` rows before returning the requested page — as `n` grows (deep pages), this gets linearly slower, becoming a serious bottleneck on large tables (e.g., `OFFSET 500000` might take seconds). Keyset (cursor-based) pagination — `WHERE id > lastSeenId ORDER BY id LIMIT 20` — uses the index to jump directly to the right starting point regardless of how "deep" the page is, giving constant-time performance.

---

## 🔷 When to Use + When Not to Use
✅ Optimize queries when:
- `EXPLAIN ANALYZE` shows sequential/full table scans on large tables for frequent queries
- An endpoint consistently shows up as slow in monitoring/APM traces
- Pagination depth or table size is growing and OFFSET-based paging is becoming a bottleneck

❌ Don't over-optimize when:
- The table is small (a few thousand rows) and queries are already sub-millisecond — added index maintenance cost isn't worth it
- You haven't measured yet — always profile with `EXPLAIN ANALYZE` before assuming a specific fix is needed

---

## 📊 Visual Diagram
```
QUERY OPTIMIZATION WORKFLOW:
────────────────────────────────────────────────
  Slow query reported (APM / slow query log)
        │
        ▼
  EXPLAIN ANALYZE the query
        │
   ┌────┴─────────────┐
   │                   │
 Seq Scan          Index Scan (already good)
 (full table)            │
   │                      ▼
   ▼                 Check: SELECT * ? N+1 pattern?
 Add index on
 WHERE/JOIN/ORDER BY columns
   │
   ▼
 Re-run EXPLAIN ANALYZE → confirm Index Scan + lower actual time

OFFSET vs KEYSET PAGINATION:
  OFFSET 100000  → scan+discard 100,000 rows  (slow, gets worse)
  WHERE id > X   → jump directly via index     (fast, constant time)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Index | Data structure that speeds up lookups | Lookup तेज़ करने वाला data structure |
| EXPLAIN ANALYZE | Shows real query execution plan | असली query execution plan दिखाना |
| Seq Scan | Full table scan (slow for large tables) | पूरे table का scan |
| Composite index | Index on multiple columns together | कई columns पर एक साथ index |
| Eager loading | Fetching related data in one query (no N+1) | Related data एक ही query में |
| Keyset pagination | Cursor-based paging, constant time | Cursor-based paging |
| Over-fetching | Selecting more data than needed | ज़रूरत से ज़्यादा data select करना |

---

## ⚡ 3-Line Summary
English:
1. Query optimization mainly comes from adding the right index on columns used in WHERE/JOIN/ORDER BY, verified with `EXPLAIN ANALYZE`.
2. Avoid over-fetching (`SELECT *`) and N+1 patterns — select only needed columns and batch/eager-load related data in a single query.
3. Replace OFFSET-based pagination with keyset/cursor pagination on large tables to avoid linearly degrading performance on deep pages.

Hindi:
1. Query optimization ज़्यादातर WHERE/JOIN/ORDER BY में use होने वाले columns पर सही index add करने से आती है — `EXPLAIN ANALYZE` से verify करो।
2. Over-fetching (`SELECT *`) और N+1 patterns से बचो — सिर्फ ज़रूरी columns select करो और related data को एक ही query में batch/eager-load करो।
3. बड़े tables पर OFFSET-based pagination की जगह keyset/cursor pagination use करो ताकि deep pages पर performance linearly न गिरे।

---

## ➡️ Next Topic
**222. N+1 Query Problem** — loops में individual queries चलाने की bug pattern और उसे batch queries से fix करना।
