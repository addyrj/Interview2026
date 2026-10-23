# 30. Query Optimization + EXPLAIN
# हिंदी में: Query Optimization — धीमी SQL query को पहचानकर तेज़ बनाना; EXPLAIN बताता है कि DB query को कैसे चला रहा है

---

## 🔵 Simple Definition (English)
**Query optimization** is the process of finding slow queries and making them faster: better indexes, rewritten SQL, fewer round trips, less data.
**EXPLAIN** shows the **execution plan** the database chose (which indexes, join methods, sort steps). **EXPLAIN ANALYZE** actually runs the query and shows **real time and row counts** per step.

## 🔵 सरल परिभाषा (Hindi)
Query optimization यानी धीमी query ढूँढकर उसे तेज़ करना — सही index, बेहतर SQL, कम डेटा।
EXPLAIN बताता है DB query को किस तरीके से चलाएगा; EXPLAIN ANALYZE असल में चलाकर हर कदम का समय बताता है।

---

## 🔴 Problem it Solves
In most production systems, **a few bad queries cause most of the DB load**:
- One unindexed query running 200×/s can push DB CPU to 100% → the whole app slows down.
- ORMs hide SQL: an innocent `for` loop makes **N+1 queries** (1 + 500 queries for one page).
- Without a plan, you're guessing. EXPLAIN shows exactly **why** a query is slow.

## 🔴 यह क्यों बना? (Hindi)
आम तौर पर कुछ ही ख़राब queries DB का ज़्यादातर बोझ बनती हैं — एक बिना index वाली query पूरे ऐप को धीमा कर देती है, और ORM चुपचाप N+1 queries बना देता है।
EXPLAIN अंदाज़े की जगह सही वजह बताता है।

---

## 🟢 How it Works — Step by Step

### The optimization workflow

```
1. FIND    → which queries are slow / most expensive in total?
              pg_stat_statements, slow query log, APM (Datadog/New Relic), RDS Performance Insights
2. EXPLAIN → EXPLAIN (ANALYZE, BUFFERS) on the real query with real parameters
3. DIAGNOSE→ Seq Scan on big table? Sort spilling to disk? Wrong row estimates? Nested loop × 1M?
4. FIX     → index / rewrite / reduce data / cache / denormalize / batch
5. VERIFY  → re-run EXPLAIN ANALYZE, compare; watch p95 latency + DB CPU after deploy
```

### Reading EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT o.id, o.total, u.name
FROM orders o JOIN users u ON u.id = o.user_id
WHERE o.status = 'PAID' AND o.created_at > now() - interval '1 day'
ORDER BY o.created_at DESC LIMIT 50;
```
```
Limit  (cost=0.85..210.4 rows=50) (actual time=0.09..1.10 rows=50 loops=1)
  ->  Nested Loop  (actual time=0.08..1.05 rows=50 loops=1)
        ->  Index Scan Backward using idx_orders_status_created on orders o
              Index Cond: ((status = 'PAID') AND (created_at > ...))
              (actual time=0.05..0.40 rows=50 loops=1)
        ->  Index Scan using users_pkey on users u
              Index Cond: (id = o.user_id)
              (actual time=0.01..0.01 rows=1 loops=50)
  Buffers: shared hit=212
Planning Time: 0.3 ms
Execution Time: 1.2 ms
```
```
How to read:
- Read bottom-up / innermost first; each node feeds its parent.
- cost=startup..total   → planner's estimate (unitless)
- actual time=..ms      → real time (per loop!)  × loops = total
- rows (estimate) vs actual rows → big mismatch = stale stats → run ANALYZE
- Buffers: shared hit (RAM) vs read (disk)
```

### Red flags in a plan

```
Seq Scan on big table + "Rows Removed by Filter: 9,999,950"  → missing index
Sort ... Sort Method: external merge Disk: 500MB             → index for ORDER BY, or more work_mem
Nested Loop with loops=100000                                → missing index on join column
Hash Join on huge tables                                     → filter earlier / index
Estimated rows=10, actual rows=2,000,000                      → stale stats / correlated columns
Bitmap Heap Scan with "Recheck" + lossy                       → index not selective enough
"Index Scan" but reading 1M rows                              → filter not selective, rethink query
```

### Join algorithms (know names)
```
Nested Loop  → for each row in A, look up B (great with index on B, small A)
Hash Join    → build hash table of smaller side, probe with bigger (big unsorted sets)
Merge Join   → both sides sorted on join key → walk together
```

### Common query problems & fixes

```
┌──────────────────────────────────┬──────────────────────────────────────────────┐
│ Problem                          │ Fix                                          │
├──────────────────────────────────┼──────────────────────────────────────────────┤
│ N+1 queries (ORM loops)          │ JOIN / include / IN (...) batch / DataLoader │
│ SELECT * (wide rows, TOAST)      │ select only needed columns                   │
│ OFFSET 100000 LIMIT 20           │ cursor/keyset pagination (Topic 39)          │
│ WHERE date(created_at) = ...     │ WHERE created_at >= d AND created_at < d+1   │
│ WHERE lower(email) = ...         │ expression index or citext                   │
│ LIKE '%term%'                    │ pg_trgm GIN index or full-text / Elastic     │
│ OR across columns                │ UNION ALL of two indexed queries             │
│ COUNT(*) on huge table per page  │ approximate count, cached counters           │
│ Implicit casts (id = '42' text)  │ correct parameter types                      │
│ Huge IN list (10k ids)           │ = ANY($1::bigint[]) or temp table/join       │
│ Correlated subquery per row      │ rewrite as JOIN / LATERAL                    │
│ Heavy report on primary          │ read replica / materialized view / OLAP      │
│ Lock waits                       │ shorter transactions, proper indexes on FKs  │
└──────────────────────────────────┴──────────────────────────────────────────────┘
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहले ढूँढो कौन-सी query सबसे ज़्यादा समय ले रही है (pg_stat_statements, slow query log)।
2. उस पर EXPLAIN ANALYZE चलाओ — नीचे से ऊपर पढ़ो, हर कदम का असली समय और rows देखो।
3. ख़तरे के निशान: बड़ी टेबल पर Seq Scan, disk पर Sort, बहुत सारे loops, अनुमान और असली rows में बड़ा फ़र्क़।
4. इलाज: index, query दोबारा लिखना, सिर्फ़ ज़रूरी columns, N+1 हटाना, cursor pagination, cache।
5. फिर दोबारा EXPLAIN करके और production में p95 देखकर पक्का करो।

---

## 🟡 Real World Example

**N+1 in an "Orders" API** — the endpoint returns 50 orders, and for each it loads the restaurant and items via the ORM: 1 + 50 + 50 = 101 queries, ~400 ms. Using `include`/JOIN and batching brings it to 3 queries, ~15 ms. Teams at Shopify, GitHub and Basecamp have built tooling (Bullet gem, n+1 detectors) just to catch this.

**Offset pagination meltdown** — a public API allowed `?page=50000`. `OFFSET 1,000,000` made Postgres read and discard a million rows per request, and scrapers brought the DB down. Switching to cursor pagination fixed it permanently.

**RDS Performance Insights** — many Indian startups discover that a single dashboard query (`COUNT(*)` with filters on a 100M-row table) consumed 40% of DB CPU. Moving it to a read replica plus a materialized view refreshed every 5 minutes fixed it.

## 🟡 Real Example Hindi में
Orders API में ORM हर order के लिए अलग से restaurant और items ला रहा था — 101 queries, 400 ms। JOIN/include से 3 queries और 15 ms हो गया।
किसी API में `?page=50000` की इजाज़त थी — DB हर बार 10 लाख rows पढ़कर फेंकता था। Cursor pagination से हमेशा के लिए ठीक हुआ।

---

## 🟠 My Stack Example

### 1. Find the worst queries (Postgres)
```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;   -- add to shared_preload_libraries
SELECT round(total_exec_time::numeric/1000, 1) AS total_s, calls,
       round(mean_exec_time::numeric, 2) AS mean_ms, rows, left(query, 120)
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;
```
```conf
# postgresql.conf / RDS parameter group: log queries slower than 200 ms
log_min_duration_statement = 200
# auto_explain: log the plan of slow queries automatically
shared_preload_libraries = 'pg_stat_statements,auto_explain'
auto_explain.log_min_duration = 500
```

### 2. Fix N+1 in Node (Prisma)
```js
// ❌ N+1
const orders = await prisma.order.findMany({ where: { userId }, take: 50 });
for (const o of orders) o.restaurant = await prisma.restaurant.findUnique({ where: { id: o.restaurantId } });

// ✅ one query with join / batched IN
const orders = await prisma.order.findMany({
  where: { userId }, take: 50, orderBy: { createdAt: 'desc' },
  select: { id: true, total: true, status: true, restaurant: { select: { id: true, name: true } } },
});
```
```js
// Log every query in dev to spot N+1
const prisma = new PrismaClient({ log: ['query'] });
```

### 3. Fix N+1 in FastAPI (SQLAlchemy)
```python
# ❌ lazy loading in a loop → N+1
orders = (await session.scalars(select(Order).where(Order.user_id == uid).limit(50))).all()
# ✅ eager load
stmt = select(Order).where(Order.user_id == uid).options(selectinload(Order.items),
                                                          joinedload(Order.restaurant)).limit(50)
orders = (await session.scalars(stmt)).unique().all()
```

### 4. Rewrite non-sargable predicates
```sql
-- ❌ function on column: can't use index on created_at
SELECT * FROM orders WHERE date(created_at) = '2024-10-01';
-- ✅
SELECT * FROM orders WHERE created_at >= '2024-10-01' AND created_at < '2024-10-02';

-- ❌ OR across columns
SELECT * FROM users WHERE email = $1 OR phone = $1;
-- ✅
SELECT * FROM users WHERE email = $1
UNION ALL
SELECT * FROM users WHERE phone = $1 AND email IS DISTINCT FROM $1;
```

### 5. Expensive aggregates → materialized view (on replica/background)
```sql
CREATE MATERIALIZED VIEW daily_revenue AS
SELECT restaurant_id, date_trunc('day', created_at) AS day, SUM(total) AS revenue, COUNT(*) AS orders
FROM orders WHERE status = 'PAID' GROUP BY 1, 2;
CREATE UNIQUE INDEX ON daily_revenue (restaurant_id, day);
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_revenue;   -- cron every 5 min
```

### 6. Keep statistics fresh & tables healthy
```sql
ANALYZE orders;                          -- update planner stats
SELECT relname, n_dead_tup, last_autovacuum FROM pg_stat_user_tables ORDER BY n_dead_tup DESC;
```

### 7. MongoDB equivalent
```js
db.orders.find({ userId: 42, status: 'PAID' }).sort({ createdAt: -1 }).explain('executionStats')
// check: winningPlan.stage = IXSCAN (not COLLSCAN), totalDocsExamined ≈ nReturned
```

### Checklist before shipping a new endpoint
```
✓ Log SQL in dev; count queries per request (should be small & constant, not O(n))
✓ EXPLAIN ANALYZE each new query on production-size data
✓ Index for WHERE + ORDER BY; LIMIT always; select only needed columns
✓ Load test the endpoint; watch DB CPU and p95
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you find and fix a slow query in production?**
A1: Identify it via `pg_stat_statements`, the slow query log or APM, ranking by total time (calls × mean), not just the slowest single run. Get the plan with `EXPLAIN (ANALYZE, BUFFERS)` using real parameters. Look for sequential scans on large tables, sorts spilling to disk, nested loops with huge loop counts, and wrong row estimates. Fix with a suitable index, a query rewrite, less data selected, pagination, caching or moving the work off the hot path. Verify the new plan and monitor p95 and DB CPU afterwards.

**Q2: What's the difference between EXPLAIN and EXPLAIN ANALYZE?**
A2: EXPLAIN shows the planner's chosen plan with estimated costs and rows, without running the query. EXPLAIN ANALYZE executes the query and adds actual time, actual rows and loops per node, so you can compare estimates with reality. Be careful: ANALYZE really runs INSERT/UPDATE/DELETE, so wrap them in a transaction and roll back.

**Q3: What is the N+1 query problem and how do you fix it?**
A3: Fetching a list with 1 query and then running 1 extra query per item to load related data, which gives N+1 round trips that grow with page size. It's common with ORM lazy loading and GraphQL resolvers. Fix it with eager loading or joins (`include`, `selectinload`), batching into one `WHERE id IN (...)` query, or DataLoader in GraphQL. Detect it by logging query counts per request in dev and tests.

**Q4: Why is OFFSET pagination slow for deep pages?**
A4: `OFFSET N LIMIT 20` makes the database produce and discard the first N rows on every request, so the cost grows linearly with page depth. The results also shift when rows are inserted, causing duplicates or skips. Keyset/cursor pagination (`WHERE (created_at, id) < (last_ts, last_id) ORDER BY ... LIMIT 20`) uses the index to jump straight to the position, so the cost is constant.

**Q5: The planner isn't using your index. What could be happening?**
A5: Stale statistics (run ANALYZE). The predicate isn't sargable (function on the column, implicit cast, leading wildcard). The query doesn't match the composite index's leftmost prefix. Low selectivity makes a sequential scan genuinely cheaper. A parameter type mismatch or generic plan in prepared statements. A small table where a scan is faster anyway. Check `EXPLAIN` while testing variations, and never force plans blindly.

---

## 🔷 Trade-offs
✅ Optimizing queries:
- Lower latency and DB load → fewer servers, cheaper, more headroom.

❌ Costs/risks:
- More indexes → slower writes.
- Denormalized/materialized data → staleness and sync logic.
- Over-optimizing rare queries wastes effort — prioritize by total time.
- Query hints/forcing plans can break when data changes.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Execution plan | Steps DB will take to run a query | query चलाने का नक्शा |
| EXPLAIN ANALYZE | Run query and show real timings | असल समय के साथ plan |
| Seq Scan | Full table read | पूरी टेबल पढ़ना |
| N+1 problem | One query per item in a list | हर item के लिए अलग query |
| Sargable | Predicate that can use an index | index इस्तेमाल करने लायक शर्त |
| Statistics | Data distribution info for planner | डेटा के आँकड़े |
| Materialized view | Stored result of a query | सेव किया हुआ query नतीजा |
| pg_stat_statements | Postgres query stats extension | query आँकड़े का टूल |

---

## ⚡ 3-Line Summary
**English:**
1. Find expensive queries (pg_stat_statements/slow log), then read EXPLAIN ANALYZE bottom-up.
2. Red flags: Seq Scan on big tables, disk sorts, huge loops, bad estimates; fix with indexes and rewrites.
3. Kill N+1, avoid SELECT * and deep OFFSET, make predicates sargable, and move heavy reports off the primary.

**Hindi:**
1. महँगी queries ढूँढो, फिर EXPLAIN ANALYZE नीचे से ऊपर पढ़ो।
2. ख़तरे: Seq Scan, disk sort, बहुत loops, ग़लत अनुमान — index और rewrite से ठीक करो।
3. N+1 हटाओ, SELECT * और बड़ा OFFSET मत करो, भारी रिपोर्ट replica पर चलाओ।

---

## ➡️ Next Topic Suggestion
**31. Normalization** — Queries also depend on how tables are designed. Next: normalization (1NF, 2NF, 3NF), how to remove duplicate data and anomalies, and why good schema design prevents bugs.
