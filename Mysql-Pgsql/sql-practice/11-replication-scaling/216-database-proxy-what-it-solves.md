---

# Q216. Database Proxy — What It Solves
# Category: Replication & Scaling
# Difficulty: ⭐⭐ Medium
# DB: Both

---

## ❓ Question
What problems does a database proxy (ProxySQL, PgBouncer, Pgpool-II, HAProxy, RDS Proxy) solve, what does it not solve, and what new risks does it add?

---

## 💡 Quick Concept (2 lines only)
A proxy decouples apps from database topology: it pools connections, routes reads and writes, hides failover, and can add caching, rewriting and throttling in one place.
हिंदी: Proxy app को DB की topology से अलग करता है — pooling, read/write routing, failover छुपाना और query control एक जगह।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- Mostly conceptual (no server to run). The two SQL probes below were run:
-- MySQL 9.1.0 standalone and PGlite 18.6 respectively.
-- ============================================

-- Problem 1: too many connections
--   MySQL probe:
SHOW VARIABLES LIKE 'max_connections';        -- Real MySQL 9.1.0: 151
SHOW STATUS LIKE 'Threads_connected';
--   PgSQL probe:
SHOW max_connections;                         -- Real PGlite: 100
--   Fix: pool/multiplex (ProxySQL, PgBouncer, RDS Proxy)

-- Problem 2: read/write split without app changes
--   Fix: ProxySQL query rules (Q206), Pgpool-II load_balance_mode, HAProxy on
--   Patroni /primary and /replica endpoints (Q208)

-- Problem 3: failover visible to the app
--   Fix: stable endpoint; proxy retries and reroutes to the new primary
--   (RDS Proxy cuts failover from ~60s to ~20s of app-visible errors, vendor claim)

-- Problem 4: one bad query / tenant overloads DB
--   Fix: ProxySQL query rules with max_connections per user, mysql_query_rules.timeout,
--   digest stats to find slow offenders; kill or rewrite without a deploy.

-- Problem 5: central visibility
--   Fix: stats_mysql_query_digest (ProxySQL), SHOW STATS (PgBouncer) -> one place
--   for QPS, latency, errors.

-- Problem 6: sharding routing   -> Vitess VTGate (Q213), Citus coordinator (Q214)

-- ============================================
-- Comparison
-- ============================================
-- Tool         | DB    | Pooling | R/W split | Failover aware | Notes
-- ProxySQL     | MySQL | yes     | yes       | yes            | rules, mirroring, caching
-- PgBouncer    | PgSQL | yes     | no        | no             | light, single-threaded
-- Pgpool-II    | PgSQL | yes     | yes       | yes            | heavier, more features
-- HAProxy      | both  | L4 only | by port   | via health chk | no SQL awareness
-- RDS Proxy    | both  | yes     | no        | yes            | managed AWS
-- MySQL Router | MySQL | no      | by port   | yes (InnoDB Cluster) | official
-- (qualitative summary, not benchmarked)
```

---

## 🔍 Why This Works (3 lines max)
Placing a stateless-ish tier at the database protocol boundary gives one control point for connection counts, routing and failover. It does not make slow SQL fast or fix a lagging replica; it only manages how traffic reaches them.
हिंदी: Protocol boundary पर proxy से connections, routing और failover एक जगह control होते हैं; slow SQL ठीक नहीं होता।

---

## ⚡ Alternative Solution

```sql
-- No proxy: client-side pooling + multi-host DSN (no extra hop, no new SPOF).
--   PostgreSQL JDBC/libpq: host=db1,db2 target_session_attrs=read-write
--   MySQL Connector/J : jdbc:mysql:replication://primary,replica1,replica2/shop
-- Good for few services; painful when 50 services each need failover/lag logic.

-- Service mesh / sidecar proxies (Envoy) support MySQL/Postgres filters mostly for metrics.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Single proxy instance = new single point of failure.
-- ✅ Run 2+ behind a VIP/NLB or as sidecars, health-checked.
-- ❌ Proxy read/write split on a replica that lags: user writes then reads stale data.
-- ✅ Pin to primary inside transactions / for N seconds after write; cap replica lag.
-- ❌ Hiding connection identity: audit logs show proxy IP, not the end user.
-- ✅ Pass client info via PROXY protocol or app-level query comments.
-- ❌ Using transaction pooling with session state (SET, temp tables) -> Q215.
```

---

## 🎯 Interview Tip (1 line)
Say: "A proxy is justified when I need connection multiplexing, centralized routing or failover abstraction across many services; I run it redundantly, measure the extra hop (typically sub-millisecond), and don't treat it as a fix for bad queries or replica lag."

---

## 🔗 Related Questions
→ Q206 (ProxySQL) | Q215 (PgBouncer) | Q208 (Patroni) | Q213 (Vitess)
