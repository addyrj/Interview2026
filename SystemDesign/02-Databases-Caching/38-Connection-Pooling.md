# 38. Connection Pooling
# हिंदी में: Connection Pooling — DB कनेक्शन को बार-बार बनाने की जगह, पहले से बने कनेक्शनों का एक "पूल" रखकर दोबारा इस्तेमाल करना

---

## 🔵 Simple Definition (English)
A **connection pool** keeps a set of **open, reusable database connections**. When code needs to run a query, it **borrows** a connection from the pool, uses it, and **returns** it, instead of opening and closing a new connection each time.
Pools exist **in the app** (pg Pool, SQLAlchemy, HikariCP) and as **external proxies** (PgBouncer, RDS Proxy, ProxySQL).

## 🔵 सरल परिभाषा (Hindi)
हर query के लिए नया DB कनेक्शन बनाना धीमा और महँगा है। Connection pool कुछ कनेक्शन पहले से खुले रखता है — query के लिए एक उधार लो, काम करो, वापस कर दो।
यह ऐप के अंदर (pg Pool) या बाहर एक proxy (PgBouncer) के रूप में होता है।

---

## 🔴 Problem it Solves
Opening a DB connection is **expensive**:
```
TCP handshake + TLS handshake + authentication (SCRAM) + backend process startup
≈ 20–100 ms   (vs a simple indexed query ≈ 1 ms)
```
And each **Postgres connection = a separate OS process** using ~5–10 MB of RAM. Postgres performs best with a **few hundred** connections at most.

Problems without pooling:
- Every request pays 20–100 ms extra latency.
- Traffic spikes → thousands of connections → DB runs out of memory / hits `max_connections` → "**too many clients already**" errors → outage.
- **Serverless** (Lambda, Vercel functions): each invocation opens its own connection → connection storms.

## 🔴 यह क्यों बना? (Hindi)
नया DB कनेक्शन बनाने में 20-100 ms लगते हैं (TCP, TLS, login), जबकि query ख़ुद 1 ms की होती है। Postgres में हर कनेक्शन एक अलग process है जो RAM खाता है।
बिना pooling के ट्रैफ़िक बढ़ते ही हज़ारों कनेक्शन → "too many clients" error → outage। Serverless में यह समस्या और बड़ी है।

---

## 🟢 How it Works — Step by Step

### In-app pool

```
          Node.js process
 ┌───────────────────────────────────────┐
 │ request 1 ─┐                          │
 │ request 2 ─┼──► Pool (max 10)         │──── 10 persistent TCP connections ────► Postgres
 │ request 3 ─┤    [c1][c2][c3]...[c10]  │
 │ request 4 ─┘    idle / in use          │
 │ request 11 → waits in queue until a   │
 │              connection is free       │
 │              (or times out)           │
 └───────────────────────────────────────┘

Step 1 → pool.query() / pool.connect() borrows an idle connection (or creates one up to max)
Step 2 → run query/transaction
Step 3 → release() → connection goes back to the idle list (NOT closed)
Step 4 → idle connections closed after idleTimeout; broken ones replaced
```

### The scaling problem: many app instances

```
20 Node pods × pool max 20 = 400 connections   ← + workers + cron + migrations…
50 Lambda concurrent × 1–5 each = up to 250
Postgres max_connections = 200 (db.t3.medium ≈ 400 max)   💥

Solution: external pooler in between
  pods/lambdas ──(thousands of client conns)──► PgBouncer ──(~50 server conns)──► Postgres
```

### PgBouncer pool modes

```
┌──────────────┬────────────────────────────────────────┬──────────────────────────────┐
│ Mode         │ Server connection held for…            │ Notes                        │
├──────────────┼────────────────────────────────────────┼──────────────────────────────┤
│ session      │ whole client session                   │ safest, least multiplexing   │
│ transaction  │ one transaction only  ⭐ most used      │ huge multiplexing; no session│
│              │                                        │ features (SET, LISTEN, temp  │
│              │                                        │ tables, session advisory     │
│              │                                        │ locks; prepared stmts need   │
│              │                                        │ PgBouncer ≥1.21 support)     │
│ statement    │ one statement                          │ no multi-statement txns      │
└──────────────┴────────────────────────────────────────┴──────────────────────────────┘
```

### Sizing a pool (don't just make it huge!)

```
Bigger pool ≠ faster. A DB with 8 cores can only run ~8–16 queries truly in parallel;
1000 active connections cause context switching + lock contention → SLOWER.

Starting formula (HikariCP / Postgres wiki):
   connections ≈ (CPU cores × 2) + effective_spindles   → e.g. 8-core DB ≈ 20–30 active

Per app instance:  pool_max = total_db_budget / number_of_instances
   DB budget 100, 10 pods → max 10 per pod (leave room for admin/migrations)

Little's Law check: RPS × avg_query_time = concurrent connections needed
   2,000 RPS × 5 ms = 10 connections busy on average

Always set:
   connectionTimeout (wait for a free conn, e.g. 2–5s) → fail fast instead of hanging
   idleTimeout, maxLifetime (recycle, e.g. 30 min — helps with failover/DNS changes)
   statement_timeout on the DB role
```

### Pool exhaustion — classic symptoms
```
Symptom: requests hang, then time out; DB CPU is LOW; "timeout acquiring connection"
Causes:
  - connection leak: forgot client.release() on an error path
  - long transactions holding connections (external API inside txn)
  - slow queries + pool too small for traffic
  - N+1 queries per request
```

## 🟢 कैसे काम करता है? (Hindi)
1. ऐप शुरू होते ही pool कुछ कनेक्शन खोलकर रखता है।
2. Query आई → pool से एक कनेक्शन उधार → query → वापस pool में (बंद नहीं होता)।
3. सब कनेक्शन व्यस्त हों तो नई request लाइन में इंतज़ार करती है, या timeout।
4. बहुत सारे pods/Lambda हों तो बीच में PgBouncer लगाओ — हज़ारों क्लाइंट, पर DB तक सिर्फ़ ~50 कनेक्शन।
5. Pool बहुत बड़ा मत करो — DB के cores सीमित हैं; हमेशा `release()` करो, नहीं तो pool ख़त्म (leak)।

---

## 🟡 Real World Example

**Instagram / Heroku / most large Postgres users** — run PgBouncer in transaction mode so thousands of app processes share a small number of real DB connections. Instagram has written about PgBouncer being critical to scaling Django on Postgres.

**Serverless + Postgres** — teams moving Next.js API routes to Vercel/Lambda often hit "too many connections" on launch day. That's why **RDS Proxy**, **Supabase Supavisor**, **Neon's pooler** and **Prisma Accelerate** exist: a managed pooler between serverless functions and Postgres.

**Pool leak outage** — a common real incident: an error path skipped `client.release()`. After a few hundred errors, all connections leaked, every request hung, and DB CPU was 2%, so on-call blamed the DB. The cause was a missing `finally`.

## 🟡 Real Example Hindi में
Instagram जैसी कंपनियाँ PgBouncer (transaction mode) से हज़ारों app processes को थोड़े-से असली DB कनेक्शन में चलाती हैं।
Vercel/Lambda पर Next.js API launch होते ही "too many connections" आम है — इसलिए RDS Proxy, Supabase pooler जैसे टूल बने। एक कंपनी में error पर `release()` छूट गया, सारे कनेक्शन फँस गए और ऐप रुक गया, जबकि DB का CPU सिर्फ़ 2% था।

---

## 🟠 My Stack Example

### Node.js — pg Pool (create ONCE per process)
```js
// db.js — module-level singleton
import pg from 'pg';
export const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  max: Number(process.env.DB_POOL_MAX ?? 10),
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 3_000,      // fail fast if pool exhausted
  maxLifetimeSeconds: 1800,
  statement_timeout: 10_000,
});
pool.on('error', (err) => logger.error({ err }, 'idle client error'));

// ✅ simple queries: pool.query auto borrows + releases
await pool.query('SELECT 1');

// ✅ transactions: ALWAYS release in finally
const client = await pool.connect();
try { await client.query('BEGIN'); /* ... */ await client.query('COMMIT'); }
catch (e) { await client.query('ROLLBACK'); throw e; }
finally { client.release(); }

// metrics to export: pool.totalCount, pool.idleCount, pool.waitingCount
```

### Prisma
```bash
DATABASE_URL="postgresql://u:p@host:5432/db?connection_limit=10&pool_timeout=5"
# behind PgBouncer (transaction mode):
DATABASE_URL="postgresql://u:p@pgbouncer:6432/db?pgbouncer=true&connection_limit=10"
DIRECT_URL="postgresql://u:p@host:5432/db"     # used for migrations (need session features)
```

### FastAPI — SQLAlchemy async engine
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,          # steady connections
    max_overflow=5,        # extra under bursts
    pool_timeout=3,        # wait for conn
    pool_recycle=1800,     # recycle every 30 min
    pool_pre_ping=True,    # detect dead connections (after failover)
)
# Gunicorn with 4 workers → 4 separate pools → 4 × (10+5) = 60 connections from ONE container!
```

### PgBouncer with Docker Compose
```yaml
services:
  pgbouncer:
    image: edoburu/pgbouncer:1.23.1
    environment:
      DATABASE_URL: postgres://app:secret@db:5432/app
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 2000
      DEFAULT_POOL_SIZE: 40
    ports: ["6432:5432"]
  api:
    environment:
      DATABASE_URL: postgres://app:secret@pgbouncer:5432/app
```

### Serverless (Next.js on Vercel / Lambda)
```ts
// Reuse the client across warm invocations (global), and point it at a pooler
const globalForDb = globalThis as unknown as { pool?: pg.Pool };
export const pool = globalForDb.pool ?? new pg.Pool({ connectionString: process.env.POOLED_DATABASE_URL, max: 1 });
globalForDb.pool = pool;
```
AWS: put **RDS Proxy** in front of RDS for Lambda functions.

### Redis & HTTP pools too
```js
// one Redis client per process (it multiplexes), one HTTP agent with keep-alive for outbound APIs
export const redis = createClient({ url: process.env.REDIS_URL }); await redis.connect();
```

### Mobile clients
React Native / web clients **never** connect to the DB directly. They call your API, which owns the pool.

---

## ⚫ Interview Questions + Answers

**Q1: What is connection pooling and why is it important?**
A1: Maintaining a set of open, reusable DB connections that requests borrow and return. Creating a connection costs tens of milliseconds (TCP, TLS, auth, backend process spawn) and server memory, and databases support a limited number of connections. Pooling removes per-request connection overhead, caps concurrency against the DB to protect it, and improves latency and stability under load.

**Q2: How do you size a connection pool?**
A2: Based on DB capacity, not app traffic. A DB can only execute roughly `2 × cores` queries efficiently in parallel, and more connections add contention. Set a total connection budget (below `max_connections`, with room for admin and migrations), divide it across app instances and workers, and validate with Little's Law (RPS × average query time). Use a short acquire timeout to fail fast, and monitor waiting count, utilization and DB load, then adjust.

**Q3: What's PgBouncer and when do you need it?**
A3: A lightweight external Postgres connection pooler. Clients connect to PgBouncer, which multiplexes them onto a small number of real server connections. In transaction mode, a server connection is assigned only for the duration of a transaction. You need it when many app instances, processes or serverless functions would otherwise exceed the DB's connection limit, or to absorb connection storms. The caveat is that transaction mode breaks session-level features (SET, LISTEN/NOTIFY, temp tables, session advisory locks, and prepared statements in older versions).

**Q4: Your app's requests are timing out but DB CPU is low. What do you suspect?**
A4: Pool exhaustion: all connections are checked out and requests wait for one. Likely causes are connection leaks (not released on error paths), long-held connections (transactions spanning external API calls or user waits), too small a pool for traffic, or slow queries and N+1 holding connections. Check pool metrics (waiting count), `pg_stat_activity` for idle-in-transaction sessions, and add `finally { release() }`, timeouts and `idle_in_transaction_session_timeout`.

**Q5: How do you handle database connections in serverless functions?**
A5: Each concurrent function instance may open its own connections, which can overwhelm the DB during spikes. Mitigations: reuse the client across warm invocations (global scope), set the per-instance pool size to 1–2, put a managed pooler in front (RDS Proxy, PgBouncer, Supabase/Neon poolers, Prisma Accelerate), or use HTTP-based DB drivers (Neon/PlanetScale serverless drivers). Also cap function concurrency.

---

## 🔷 Trade-offs
✅ Advantages:
- Lower latency (no reconnect), protects DB from overload, stable resource usage.

❌ Disadvantages:
- Pool too small → waiting/timeouts; too large → DB contention.
- External poolers add a hop and break some session features (transaction mode).
- Leaks are silent until everything hangs — needs monitoring and disciplined code.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Connection pool | Reusable set of open connections | दोबारा इस्तेमाल होने वाले कनेक्शन |
| Acquire / Release | Borrow / return a connection | उधार लेना / लौटाना |
| Pool exhaustion | All connections in use | सारे कनेक्शन व्यस्त |
| Connection leak | Borrowed but never returned | उधार लिया पर लौटाया नहीं |
| max_connections | DB's connection limit | DB की अधिकतम कनेक्शन सीमा |
| PgBouncer | External Postgres pooler | Postgres का बाहरी pooler |
| Transaction mode | Server conn per transaction | हर transaction के लिए कनेक्शन |
| RDS Proxy | AWS managed DB pooler | AWS का managed pooler |

---

## ⚡ 3-Line Summary
**English:**
1. Opening DB connections is slow and DB connections are limited — reuse them via a pool.
2. Size pools by DB capacity (≈ 2× cores active), split across instances; use PgBouncer/RDS Proxy for many instances or serverless.
3. Always release connections, keep transactions short, set acquire/statement timeouts, monitor pool waiting.

**Hindi:**
1. DB कनेक्शन बनाना धीमा और सीमित है — pool से दोबारा इस्तेमाल करो।
2. Pool का आकार DB की क्षमता से तय करो; बहुत सारे instances/serverless हों तो PgBouncer/RDS Proxy।
3. हमेशा release करो, transaction छोटे रखो, timeouts लगाओ, pool की monitoring करो।

---

## ➡️ Next Topic Suggestion
**39. Pagination (Cursor vs Offset)** — Every list API (orders, feed, products) needs pagination. Next: offset vs cursor/keyset pagination in depth, with code for Postgres, MongoDB and infinite scroll in React Native.
