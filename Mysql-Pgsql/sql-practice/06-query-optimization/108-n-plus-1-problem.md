---

# Q108. N+1 Query Problem — Detection and Fix
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
What is the N+1 query problem? How do you detect it? Show the fix in raw SQL and in an ORM (Sequelize / Prisma). What is the JOIN + aggregate pattern?

---

## 💡 Quick Concept (2 lines only)
N+1 = 1 query to load N parent records + N individual queries to load each child's data = N+1 total queries. Fix: one query with JOIN + aggregate, or batch loading. At scale, N=1000 users → 1001 queries instead of 1.
हिंदी: N+1 = N records load करो + N separate queries = total N+1 queries। Fix = JOIN + aggregate या batch load।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE users (
  id    INT PRIMARY KEY AUTO_INCREMENT,
  name  VARCHAR(100),
  email VARCHAR(255)
);

CREATE TABLE orders (
  id         INT PRIMARY KEY AUTO_INCREMENT,
  user_id    INT NOT NULL,
  amount     DECIMAL(10,2),
  status     VARCHAR(20),
  created_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_orders_user ON orders(user_id);

-- ============================================
-- THE N+1 PROBLEM (Raw SQL version)
-- ============================================

-- ❌ BAD CODE PATTERN (what naive code does):

-- Step 1: 1 query to get all users
SELECT id, name, email FROM users LIMIT 100;
-- Returns 100 users (N = 100)

-- Step 2: For EACH user in the loop, run a separate query:
SELECT COUNT(*), SUM(amount) FROM orders WHERE user_id = 1;
SELECT COUNT(*), SUM(amount) FROM orders WHERE user_id = 2;
SELECT COUNT(*), SUM(amount) FROM orders WHERE user_id = 3;
-- ... 100 more queries ...
SELECT COUNT(*), SUM(amount) FROM orders WHERE user_id = 100;

-- Total: 1 + 100 = 101 queries
-- At N=10000 users → 10,001 queries!
-- Each query: network round-trip + DB parse + index lookup = ~5-10ms
-- Total: 10,000 × 10ms = 100 seconds! 🔥

-- ============================================
-- FIX 1: JOIN + AGGREGATE (1 query instead of N+1)
-- ============================================

-- ✅ GOOD: Single query with LEFT JOIN + GROUP BY
SELECT
  u.id,
  u.name,
  u.email,
  COUNT(o.id)     AS order_count,
  COALESCE(SUM(o.amount), 0) AS total_spent,
  MAX(o.created_at) AS last_order_date
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name, u.email
LIMIT 100;

-- EXPLAIN: 1 query, idx_orders_user used for JOIN
-- Total: 1 query, ~10ms vs 1000+ queries × 10ms = 10+ seconds
-- LEFT JOIN ensures users with no orders are included (order_count = 0)

-- Why COUNT(o.id) instead of COUNT(*)?
-- COUNT(*) counts all rows including NULLs (when user has no orders, LEFT JOIN returns NULL row)
-- COUNT(o.id) counts only non-NULL ids → correctly returns 0 for users with no orders

-- ============================================
-- FIX 2: IN-CLAUSE BATCH LOAD
-- ============================================

-- When you can't use a JOIN (e.g., data from different services):
-- Step 1: load users (1 query)
SELECT id, name FROM users LIMIT 100;
-- Get ids: [1, 2, 3, ..., 100]

-- Step 2: load ALL related orders in ONE query (not 100 separate queries)
SELECT user_id, COUNT(*) AS order_count, SUM(amount) AS total
FROM orders
WHERE user_id IN (1, 2, 3, ..., 100)  -- all ids from step 1
GROUP BY user_id;

-- Step 3: In application code — merge by user_id:
-- ordersByUser = Map<userId, {count, total}>
-- users.forEach(u => u.orderSummary = ordersByUser.get(u.id))

-- Total: 2 queries instead of 101! ✅

-- ============================================
-- FIX 3: SUBQUERY IN SELECT (simple but can be slow)
-- ============================================

SELECT
  u.id,
  u.name,
  (SELECT COUNT(*) FROM orders WHERE user_id = u.id) AS order_count,
  (SELECT SUM(amount) FROM orders WHERE user_id = u.id) AS total_spent
FROM users u
LIMIT 100;

-- Correlated subquery: runs once per user = still N+1 queries internally!
-- Optimizer may or may not optimize this to a single scan
-- Better than application-level N+1 (one DB round-trip) but still O(N)
-- Use only for small N or when JOIN is too complex

-- ============================================
-- ORM PATTERNS — SEQUELIZE (NODE.JS)
-- ============================================

/*
// ❌ N+1 in Sequelize:
const users = await User.findAll({ limit: 100 });
for (const user of users) {
  const orders = await Order.findAll({ where: { userId: user.id } });
  // ← 1 query per user = N+1!
  user.dataValues.orders = orders;
}

// ✅ Fix: Eager loading with include
const users = await User.findAll({
  limit: 100,
  include: [{
    model: Order,
    attributes: ['id', 'amount', 'status'],
    required: false  // LEFT JOIN (include users with no orders)
  }]
});
// Sequelize generates: SELECT users.*, orders.* FROM users LEFT JOIN orders ON ...
// 1 query! ✅

// ✅ Fix: include with separate batch query (for large child datasets)
const users = await User.findAll({
  limit: 100,
  include: [{
    model: Order,
    separate: true,  // ← generates: SELECT * FROM orders WHERE user_id IN (...)
    attributes: ['id', 'amount']
  }]
});
// 2 queries: 1 for users, 1 batched for all orders ✅
// Use separate:true when N children per parent is large (avoids huge JOIN result)
*/

-- ============================================
-- ORM PATTERNS — PRISMA (NODE.JS)
-- ============================================

/*
// ❌ N+1 in Prisma:
const users = await prisma.user.findMany({ take: 100 });
for (const user of users) {
  const count = await prisma.order.count({ where: { userId: user.id } });
  // ← 1 query per user!
}

// ✅ Fix: include (eager loading)
const users = await prisma.user.findMany({
  take: 100,
  include: {
    orders: {
      select: { id: true, amount: true, status: true }
    }
  }
});
// Prisma generates: 2 queries (SELECT users THEN SELECT orders WHERE user_id IN (...))
// Prisma always uses the "batch" strategy for relations — avoids huge JOINs ✅

// ✅ Fix: Use _count for just the count (even more efficient)
const users = await prisma.user.findMany({
  take: 100,
  include: {
    _count: { select: { orders: true } }  // ← one extra COUNT query
  }
});
// users[0]._count.orders = 5
*/

-- ============================================
-- DETECTING N+1 IN PRODUCTION
-- ============================================

-- MySQL: Enable slow query log + general query log temporarily
-- Set: general_log = ON, general_log_file = '/tmp/mysql-general.log'
-- Look for patterns: same query with different parameter values repeated N times:
-- SELECT * FROM orders WHERE user_id = 1
-- SELECT * FROM orders WHERE user_id = 2
-- (repeating 100 times = N+1!)

-- PgSQL: pg_stat_statements — find queries with high call count:
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
WHERE query LIKE '%orders%'
ORDER BY calls DESC
LIMIT 10;
-- If "SELECT ... WHERE user_id = $1" called 100,000 times = N+1 pattern!

-- Application level: APM tools (DataDog, New Relic, Sentry Performance)
-- Show "N+1 detected: 100 identical queries differing only by parameter"
-- Identify the source code location

-- ============================================
-- WHEN TO USE EACH FIX
-- ============================================

/*
Scenario                                  → Fix
──────────────────────────────────────────────────────
Simple parent + child aggregation          → JOIN + GROUP BY (1 query)
Parent + children (flat list, not aggregate) → ORM eager load / batch IN query
Different services (can't JOIN)            → Batch load with IN clause
Small N (< 10 parents)                     → N+1 is OK (10 queries is fine)
Complex per-row calculation                → CTE + window function
Real-time dashboard aggregation            → Materialized view + refresh
*/
```

---

## 🔍 Why This Works (3 lines max)
N+1 happens because code iterates parent records and issues a new query per record — each query has overhead from network round-trips, connection pool acquisition, and query parsing. The JOIN + GROUP BY fix collapses N queries into one, letting the database engine apply indexes once across all data. The batch IN query fix is the right choice when JOINs aren't possible — two round-trips instead of N+1.
हिंदी: N+1 में प्रत्येक record के लिए separate query = N×overhead। JOIN+GROUP BY = 1 query में सब। Batch IN = 2 queries।

---

## ⚡ Alternative Solution

```sql
-- CTE for complex N+1 fix (readable alternative to JOIN):
WITH user_stats AS (
  SELECT
    user_id,
    COUNT(*) AS order_count,
    SUM(amount) AS total_spent,
    MAX(created_at) AS last_order
  FROM orders
  GROUP BY user_id
)
SELECT u.id, u.name, u.email,
  COALESCE(us.order_count, 0) AS order_count,
  COALESCE(us.total_spent, 0) AS total_spent,
  us.last_order
FROM users u
LEFT JOIN user_stats us ON u.id = us.user_id;
-- Same performance as JOIN + GROUP BY but CTE makes intent clearer
-- PgSQL: may be slightly different plan (CTE sometimes materializes)
-- MySQL 8.0+: CTE is generally optimized inline
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "But my ORM handles it" (it doesn't by default!)
const users = await User.findAll();
users.forEach(async u => { u.orders = await u.getOrders() });
-- getOrders() is a lazy-loaded query — 1 per user = N+1!
-- ORM "associations" don't automatically eager-load — you must explicitly include

-- ❌ Wrong: Fixing N+1 with a giant JOIN that returns duplicate rows
SELECT u.id, u.name, o.id, o.amount
FROM users u JOIN orders o ON u.id = o.user_id;
-- User with 1000 orders → 1000 rows for that user!
-- If users have 1M total orders across 100 users → 1M rows returned!
-- ✅ For aggregates: GROUP BY. For lists: use batch IN query with LIMIT per user.

-- ❌ Wrong: Using SELECT * in the N+1 fix
-- SELECT *, COUNT(o.id) ... GROUP BY u.id
-- MySQL: GROUP BY u.id with SELECT * non-deterministic without full GROUP BY
-- PgSQL: ERROR — must GROUP BY all non-aggregate columns
-- ✅ Explicitly list columns: SELECT u.id, u.name, COUNT(o.id)
```

---

## 🎯 Interview Tip (1 line)
Say: "N+1 is 1 query to load N records then N queries for related data — it compounds badly at scale (100 users = 101 queries, 10,000 users = 10,001 queries). I fix it with a single JOIN + GROUP BY for aggregates, or a batch IN query for full child records. In ORMs I use eager loading (Sequelize `include`, Prisma `include`) and check pg_stat_statements for high-call-count queries to detect N+1 in production."

---

## 🔗 Related Questions
→ Q086 (EXPLAIN output) | Q083 (composite index) | Q109 (slow query optimization) | Q011 (pagination)
