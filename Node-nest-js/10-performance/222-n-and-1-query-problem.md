# 222. N+1 Query Problem
# हिंदी में: N+1 Query Problem — Loop में बार-बार Query चलाने की Bug

---

## 🔵 Simple Definition (English)
The **N+1 query problem** happens when fetching a list of N items takes 1 query, but then fetching a related piece of data for EACH item takes N additional queries (loop) — totaling N+1 database round-trips instead of a constant 1-2. It's one of the most common and costly performance bugs in apps using ORMs, because the pattern looks innocent in code but scales terribly.

## 🔵 सरल परिभाषा (Hindi)
**N+1 query problem** तब होता है जब N items की list fetch करने में 1 query लगती है, पर फिर हर item के लिए related data fetch करने में N additional queries (loop में) लगती हैं — कुल N+1 database round-trips, जबकि constant 1-2 काफी होनी चाहिए। ORM use करने वाले apps में ये सबसे common और costly performance bug है, क्योंकि code में ये pattern innocent दिखता है पर scale करने पर बहुत बुरा होता है।

---

## 🔴 Problem it Solves (understanding it = half the fix)
In development with 10 test records, an N+1 pattern runs 11 queries — invisible, feels instant. In production with a page showing 100 orders, the SAME code pattern runs 101 queries — each with network latency to the DB, connection overhead, and query planning cost. This can turn a 50ms endpoint into a 3-second one, and it gets linearly worse as data grows. Recognizing this pattern (a query inside a loop/map over another query's results) and replacing it with a single batched/joined query is one of the highest-value fixes in backend performance work.

## 🔴 यह क्यों बना? (Hindi)
Development में 10 test records के साथ, N+1 pattern 11 queries चलाता है — invisible, instant लगता है। Production में 100 orders वाले page पर, वही code pattern 101 queries चलाता है — हर एक में DB तक network latency, connection overhead, query planning cost। ये 50ms वाले endpoint को 3-second वाला बना सकता है, और data बढ़ने पर linearly बुरा होता जाता है। इस pattern को पहचानना (एक query का result loop/map में दूसरी query चलाना) और उसे single batched/joined query से replace करना backend performance work का सबसे high-value fix है।

---

## 🟢 How it Works — Step by Step

Step 1 → Spot the pattern: a `for`/`.forEach`/`.map` loop over a result set that makes a DB call INSIDE the loop body
Step 2 → Confirm with query logging/APM: enable ORM query logging (e.g., Sequelize's `logging: true`, Mongoose's `mongoose.set('debug', true)`) and watch the query count explode with list size
Step 3 → Identify what data is being fetched per-item (a related record: restaurant per order, author per post, user per comment)
Step 4 → Replace with **eager loading** (ORM's `include`/`populate`/`with`) which generates a single JOIN or a batched second query automatically
Step 5 → If the ORM doesn't support eager loading for the case, manually batch: collect all needed IDs first, run ONE `WHERE id IN (...)` query, then map results back using an in-memory lookup (Map/object)
Step 6 → Verify the fix: query count should now be constant (1-2) regardless of how many items are in the list

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Pattern पहचानो: एक `for`/`.forEach`/`.map` loop जो result set पर चलते हुए loop के अंदर DB call करे
Step 2 → Query logging/APM से confirm करो: ORM query logging enable करो और देखो कि list size बढ़ने पर query count कैसे explode होती है
Step 3 → पहचानो कि per-item कौन सा related data fetch हो रहा है (order का restaurant, post का author, comment का user)
Step 4 → **Eager loading** से replace करो (ORM का `include`/`populate`/`with`) जो automatically single JOIN या batched query बनाता है
Step 5 → अगर ORM eager loading support नहीं करता, manually batch करो: पहले सभी ज़रूरी IDs collect करो, एक `WHERE id IN (...)` query चलाओ, फिर in-memory lookup (Map/object) से results map करो
Step 6 → Fix verify करो: list size कुछ भी हो, query count अब constant (1-2) होनी चाहिए

---

## 🟡 Real World Example
**Swiggy's order-dashboard API** for restaurant partners showed 95 database queries for a page displaying 30 recent orders — one query to fetch orders, then one query PER order to fetch the customer's name and one MORE per order to fetch delivery partner details (30 + 30 + 1 = 61, plus a few more for addresses = 95 total). With Mongoose's `.populate('customer').populate('deliveryPartner')`, the team replaced this with proper eager loading — the same page now runs exactly 3 queries total regardless of whether it shows 30 or 300 orders, cutting dashboard load time from 2.8s to 95ms.

## 🟡 Real Example Hindi mein
**Swiggy का order-dashboard API** restaurant partners के लिए 30 recent orders दिखाने वाले page पर 95 database queries चला रहा था — एक query orders के लिए, फिर हर order के लिए एक query customer name के लिए और एक और delivery partner details के लिए। Mongoose के `.populate('customer').populate('deliveryPartner')` से team ने इसे proper eager loading से replace किया — same page अब exactly 3 queries चलाता है भले ही 30 हो या 300 orders, dashboard load time 2.8s से 95ms हो गया।

---

## 💻 Code Example — Basic

```javascript
// n-plus-1-demo.js — demonstrating the N+1 bug and its fix with plain SQL (pg)
const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// ❌ BAD: N+1 pattern
async function getOrdersWithRestaurantsBad() {
  // Query 1: fetch 30 orders
  const ordersResult = await pool.query('SELECT * FROM orders LIMIT 30');
  const orders = ordersResult.rows;

  // Queries 2 through 31: ONE query PER order inside the loop — this is the bug!
  for (const order of orders) {
    const restaurantResult = await pool.query(
      'SELECT name, rating FROM restaurants WHERE id = $1',
      [order.restaurant_id]
    );
    order.restaurant = restaurantResult.rows[0];
  }
  // Total queries run: 1 + 30 = 31, for just 30 orders!
  return orders;
}

// ✅ GOOD: batch into exactly 2 queries total, regardless of order count
async function getOrdersWithRestaurantsGood() {
  // Query 1: fetch orders
  const ordersResult = await pool.query('SELECT * FROM orders LIMIT 30');
  const orders = ordersResult.rows;

  // Collect all UNIQUE restaurant IDs needed
  const restaurantIds = [...new Set(orders.map(o => o.restaurant_id))];

  // Query 2: fetch ALL needed restaurants in ONE query using IN (...)
  const restaurantsResult = await pool.query(
    'SELECT id, name, rating FROM restaurants WHERE id = ANY($1)',
    [restaurantIds]
  );

  // Build an in-memory lookup map for O(1) access while attaching results
  const restaurantMap = new Map(restaurantsResult.rows.map(r => [r.id, r]));
  orders.forEach(order => {
    order.restaurant = restaurantMap.get(order.restaurant_id);
  });

  // Total queries: always 2, whether there are 30 orders or 3000!
  return orders;
}
```

## 💻 Code Example — Advanced

```javascript
// orm-eager-loading-fixes.js — how different ORMs solve N+1 automatically

// ─── MONGOOSE: .populate() ────────────────────────────────────────────────
const mongoose = require('mongoose');

async function getOrdersMongoose() {
  // Without populate: order.customerId is just an ObjectId — fetching the
  // actual customer per order in a loop would be N+1
  // With populate: Mongoose runs ONE extra query to fetch ALL referenced
  // customers in a single batched $in query internally
  return Order.find()
    .populate('customerId', 'name email')        // batched, not per-document
    .populate('deliveryPartnerId', 'name phone')  // another single batched query
    .limit(30);
}

// ─── SEQUELIZE: include ───────────────────────────────────────────────────
const { Order, Restaurant, Customer } = require('./models');

async function getOrdersSequelize() {
  // Sequelize generates a single SQL query with JOINs (or 2 queries with
  // 'separate: true' for one-to-many, still avoiding the N+1 loop)
  return Order.findAll({
    limit: 30,
    include: [
      { model: Restaurant, attributes: ['name', 'rating'] },
      { model: Customer, attributes: ['name', 'email'] },
    ],
  });
}

// ─── PRISMA: include ───────────────────────────────────────────────────────
// const orders = await prisma.order.findMany({
//   take: 30,
//   include: { restaurant: true, customer: true }, // single query with JOINs
// });

// ─── GraphQL N+1 (DataLoader pattern) ──────────────────────────────────────
// GraphQL resolvers are especially prone to N+1: each "order.restaurant"
// field resolver naively fetches independently per order. DataLoader batches
// and deduplicates these into a single call per tick.
const DataLoader = require('dataloader');

const restaurantLoader = new DataLoader(async (restaurantIds) => {
  // DataLoader collects all requested IDs within the same event loop tick
  // and calls this batch function ONCE with all of them together
  const restaurants = await pool.query(
    'SELECT * FROM restaurants WHERE id = ANY($1)',
    [restaurantIds]
  );
  const map = new Map(restaurants.rows.map(r => [r.id, r]));
  // MUST return results in the SAME ORDER as the input keys
  return restaurantIds.map(id => map.get(id));
});

// GraphQL resolver — looks like it's called per-order, but DataLoader
// automatically batches all these calls into ONE query behind the scenes
const resolvers = {
  Order: {
    restaurant: (order) => restaurantLoader.load(order.restaurantId),
  },
};
```

---

## 🟠 Express.js Integration

```javascript
// routes/orders.js — a real Express route demonstrating the fix in context
const express = require('express');
const router = express.Router();

router.get('/dashboard/orders', async (req, res) => {
  // Fix applied: eager-loaded, exactly 2-3 queries regardless of result size
  const orders = await Order.find({ restaurantId: req.user.restaurantId })
    .populate('customerId', 'name phone')
    .populate('deliveryPartnerId', 'name vehicleNumber')
    .sort({ createdAt: -1 })
    .limit(50)
    .lean();

  res.json(orders);
});

module.exports = router;

// Query logging middleware to CATCH N+1 patterns during development/testing
mongoose.set('debug', (collectionName, method, query) => {
  global.__queryCount = (global.__queryCount || 0) + 1;
  console.log(`[Query #${global.__queryCount}] ${collectionName}.${method}`, query);
});

// In a test: reset __queryCount before the request, assert it stays low after
test('dashboard orders endpoint does not have N+1', async () => {
  global.__queryCount = 0;
  await request(app).get('/dashboard/orders');
  // Assert query count is small and CONSTANT, not proportional to result size
  expect(global.__queryCount).toBeLessThan(5);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `await` inside a `.map()`/`forEach()` over a result set
```javascript
// WRONG: looks clean but is still N+1 — one query per order in the loop
const enriched = await Promise.all(
  orders.map(async (order) => {
    order.restaurant = await Restaurant.findById(order.restaurantId); // N queries!
    return order;
  })
);
// Note: Promise.all() makes these run CONCURRENTLY (faster than sequential),
// but it's STILL N separate round-trips to the DB — not a real fix for N+1.

// CORRECT: batch into one query using collected IDs, then map in-memory
const restaurantIds = [...new Set(orders.map(o => o.restaurantId))];
const restaurants = await Restaurant.find({ _id: { $in: restaurantIds } }); // 1 query
const map = new Map(restaurants.map(r => [r._id.toString(), r]));
orders.forEach(order => { order.restaurant = map.get(order.restaurantId.toString()); });
```

❌ Mistake 2: Assuming ORM eager-loading (`.populate()`/`.include()`) is "automatic everywhere" without checking generated query count
```javascript
// WRONG: deeply NESTED populate calls can still cause N+1 at a deeper level
Order.find().populate({
  path: 'items.product', // populating a field nested inside an array of items
}); // depending on the ORM/version, this can sometimes still generate per-document queries

// CORRECT: always verify with query logging/EXPLAIN that the final query
// count stays CONSTANT as result set size grows — don't just assume
// "I used populate/include so I'm safe"
```

---

## 🧠 Tricky Interview Question

```javascript
async function getPostsWithComments() {
  const posts = await Post.find().limit(10);
  const postsWithComments = await Promise.all(
    posts.map(post => Comment.find({ postId: post._id }))
  );
  return postsWithComments;
}
// ❓ Is this N+1? Is using Promise.all() enough to fix it?
```
Answer: **Yes, this is still N+1 — Promise.all() does NOT fix it, it only parallelizes it.** The code still issues 1 query for posts + 10 separate queries for comments (one per post) = 11 total database round-trips. `Promise.all()` makes those 10 comment queries run CONCURRENTLY instead of sequentially, which is faster than doing them one after another, but it's still 10 separate network round-trips and 10 separate query executions on the database — not the same as ONE batched query. The real fix: `Comment.find({ postId: { $in: posts.map(p => p._id) } })` — a SINGLE query fetching all comments for all 10 posts at once, then group them by `postId` in memory. This is a very common interview trap: candidates think `Promise.all` "solves" N+1 because it's faster, but it doesn't reduce the actual QUERY COUNT, which is what matters for database load at scale.

---

## ⚫ Interview Questions + Answers

Q1: What exactly makes a pattern "N+1" rather than just "a few extra queries"?
A1: The defining trait is that the NUMBER of queries scales linearly with the size of the initial result set — 1 query for the list, plus N more (one per item), where N is the list's length. This means performance degrades proportionally as data grows: 10 items = 11 queries, 10,000 items = 10,001 queries — unlike a fixed, constant number of queries regardless of list size.

Q2: Does `Promise.all()` fix the N+1 problem?
A2: No — it only parallelizes the N queries (runs them concurrently instead of sequentially), reducing WALL-CLOCK time somewhat, but the actual QUERY COUNT hitting the database remains N+1. Under real production load with many concurrent requests, this still means N times more connections/queries hitting the DB than necessary, which can overwhelm connection pools even if each individual request feels "faster."

Q3: How does DataLoader solve N+1 specifically in GraphQL?
A3: GraphQL field resolvers are called independently per object in a result set (e.g., `order.restaurant` resolver runs once per order), naturally creating N+1 patterns. DataLoader batches all `.load(id)` calls made within the same event loop tick into a single batch function call with all collected IDs, then dedupes and caches results — turning what looks like N independent resolver calls into exactly 1 batched query behind the scenes.

Q4: Can N+1 happen with a single SQL query (not just in application code)?
A4: Yes, in rare cases a SQL query with a correlated subquery that re-executes for every outer row can behave like N+1 at the database engine level even without application-level looping. But the overwhelmingly common case is application-level: ORM code looping over a result set and issuing a query per item, which is what "N+1" almost always refers to in interviews and real debugging.

Q5: How do you proactively catch N+1 bugs before they reach production?
A5: Enable query logging in development/test environments (ORM debug flags) and write a test/assertion that checks the TOTAL query count for a given endpoint stays constant regardless of how many records are in the test dataset (e.g., assert fewer than 5 queries whether returning 10 or 100 orders). Tools like `n+1-detector` libraries, or APM tracing (New Relic, Datadog) that groups and counts similar queries per request, also surface this automatically in staging/production.

---

## 🔷 When to Use + When Not to Use
✅ Watch for N+1 when:
- Fetching a list of records and then accessing a RELATED record/collection per item (classic pattern: orders → restaurant, posts → author, comments → user)
- Building GraphQL resolvers where a field is resolved per-object in a list
- Query count in logs scales with result set size instead of staying constant

❌ Not a concern when:
- Fetching a single record and its directly related data (not a list) — this is naturally just 1-2 queries
- The "extra" queries are genuinely a FIXED small number regardless of list size (not actually N+1)

---

## 📊 Visual Diagram
```
N+1 PROBLEM:
────────────────────────────────────────────────
  Query 1: SELECT * FROM orders LIMIT 30   ← returns 30 orders
       │
       ▼
  for each of the 30 orders:
       SELECT * FROM restaurants WHERE id = order.restaurant_id  ← ×30!
       │
  Total: 1 + 30 = 31 queries for just 30 orders

FIXED (batched):
  Query 1: SELECT * FROM orders LIMIT 30
       │
       ▼
  Collect unique restaurant_ids → [12, 45, 78, ...]
       │
       ▼
  Query 2: SELECT * FROM restaurants WHERE id = ANY([12,45,78,...])
       │
  Total: always 2 queries, whether 30 orders or 30,000
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| N+1 problem | 1 query + N queries in a loop for related data | 1 query + loop में N queries |
| Eager loading | Fetching related data upfront in one batched query | Related data पहले ही एक query में |
| Batching | Combining many individual queries into one | कई queries को एक में combine करना |
| DataLoader | Library that auto-batches GraphQL resolver calls | GraphQL calls को auto-batch करने वाली library |
| WHERE ... IN | SQL clause to fetch multiple rows by ID list | ID list से multiple rows fetch करना |
| populate()/include() | ORM methods for eager loading | ORM के eager loading methods |

---

## ⚡ 3-Line Summary
English:
1. N+1 happens when fetching N items leads to N additional queries in a loop for related data — total queries scale with list size instead of staying constant.
2. `Promise.all()` parallelizes N+1 queries but does NOT fix the underlying problem — query count stays N+1, just faster in wall-clock time.
3. Fix with ORM eager loading (`populate`/`include`) or manual batching (`WHERE id IN (...)`) so query count stays constant (1-2) regardless of result set size.

Hindi:
1. N+1 तब होता है जब N items fetch करने पर related data के लिए loop में N additional queries लगती हैं — कुल queries list size के साथ बढ़ती हैं, constant नहीं रहती।
2. `Promise.all()` N+1 queries को parallelize करता है पर असली problem fix नहीं करता — query count N+1 ही रहती है, सिर्फ wall-clock time में तेज़।
3. ORM eager loading (`populate`/`include`) या manual batching (`WHERE id IN (...)`) से fix करो ताकि result set size कुछ भी हो, query count constant (1-2) रहे।

---

## ➡️ Next Topic
**223. Connection Pool Optimization** — database connections को efficiently reuse करना ताकि high traffic में connections exhaust न हों।
