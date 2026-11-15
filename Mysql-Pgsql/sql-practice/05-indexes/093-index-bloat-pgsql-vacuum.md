---

# Q093. Index Bloat in PgSQL - VACUUM
# Category: Indexes
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL (MySQL InnoDB comparison)

---

## ❓ Question
Why do PostgreSQL tables and indexes bloat after many UPDATE/DELETEs? What do `VACUUM`, `VACUUM FULL` and `REINDEX` each do, which ones return disk space to the OS, and how do you fix index bloat on a live system?

---

## 💡 Quick Concept (2 lines only)
PostgreSQL MVCC never overwrites a row: UPDATE writes a new tuple and leaves the old one dead, and every index gets a new entry too. `VACUUM` marks dead space reusable (usually without shrinking files); only `VACUUM FULL` / `REINDEX` rebuild compactly.
हिंदी: PgSQL में UPDATE पुरानी row को dead छोड़कर नई बनाता है; VACUUM जगह दोबारा उपयोग-योग्य करता है, फ़ाइल छोटी REINDEX / VACUUM FULL से होती है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) - PostgreSQL
-- ============================================

CREATE TABLE accounts (
  account_id INT PRIMARY KEY,
  balance    NUMERIC(12,2) NOT NULL,
  last_login TIMESTAMP NOT NULL DEFAULT now(),
  note       TEXT
);
INSERT INTO accounts SELECT n, 1000, now(), 'x' FROM generate_series(1, 50000) n;
CREATE INDEX idx_accounts_last_login ON accounts (last_login, account_id);
CREATE INDEX idx_accounts_balance    ON accounts (balance);
ANALYZE accounts;

-- Helper query reused below
SELECT pg_size_pretty(pg_relation_size('accounts'))                AS table_size,
       pg_size_pretty(pg_relation_size('idx_accounts_balance'))    AS idx_balance,
       pg_size_pretty(pg_relation_size('idx_accounts_last_login')) AS idx_last_login;

-- ============================================
-- SOLUTION: watch bloat grow, then fix it
-- ============================================

-- Two full-table updates that change INDEXED columns (so HOT updates are impossible)
UPDATE accounts SET balance = balance + 1, last_login = now() + (account_id % 1000) * interval '1 second';
UPDATE accounts SET balance = balance + 1, last_login = now() + (account_id % 1000 + 5000) * interval '1 second';
-- (size query)  -> bloated

VACUUM accounts;                      -- plain VACUUM: frees dead tuples for reuse, does NOT shrink files
-- (size query)  -> same sizes

UPDATE accounts SET balance = balance + 1, last_login = now() + (account_id % 1000 + 9000) * interval '1 second';
-- (size query)  -> table did NOT grow (space reused); indexes DID grow again

REINDEX TABLE accounts;               -- rebuild all indexes compactly (PG 12+: REINDEX ... CONCURRENTLY)
-- (size query)  -> indexes back to original size, table still big

VACUUM FULL accounts;                 -- rewrite table + indexes; takes ACCESS EXCLUSIVE lock
-- (size query)  -> table back to original size

-- ============================================
-- EXPECTED OUTPUT (verified on PostgreSQL 18 via PGlite; sizes approximate)
-- ============================================

-- stage                       | table_size | idx_balance | idx_last_login
-- initial                     | 2944 kB    | 1112 kB     | 1552 kB
-- after 2 full-table updates  | 8824 kB    | 3192 kB     | 5584 kB     <- ~3x table, 3-3.6x indexes
-- after VACUUM                | 8824 kB    | 3192 kB     | 5584 kB     <- nothing shrinks
-- after 3rd update            | 8824 kB    | 5160 kB     | 7512 kB     <- table reused dead space; indexes kept growing
-- after REINDEX               | 8824 kB    | 1112 kB     | 1552 kB     <- indexes compact; table still bloated
-- after VACUUM FULL           | 2944 kB    | 1112 kB     | 1552 kB     <- everything compact
--
-- Not shown by PGlite: pg_stat_user_tables.n_dead_tup stayed 0 and the pgstattuple/pgstatindex extension is
-- unavailable ("extension pgstattuple is not available"), so use size comparison here; on a real server see below.
```

---

## 🔍 Why This Works (3 lines max)
Each UPDATE leaves a dead heap tuple and a dead index entry; VACUUM reclaims dead tuples into the free-space map for later inserts, but B-Tree pages that become sparse are rarely returned to the OS. REINDEX rebuilds the tree densely; VACUUM FULL rewrites the whole table.
हिंदी: हर UPDATE dead tuple और dead index entry छोड़ता है; VACUUM उन्हें reuse के लिए free करता है, REINDEX / VACUUM FULL ही file को सिकोड़ते हैं।

---

## ⚡ Alternative Solution

```sql
-- Production approach (not runnable in PGlite - requires a real server):
-- 1) Find bloat (needs extension):  CREATE EXTENSION pgstattuple;
--      SELECT * FROM pgstatindex('idx_accounts_balance');        -- avg_leaf_density, leaf_fragmentation
--      SELECT * FROM pgstattuple('accounts');                      -- dead_tuple_percent
--    Dead tuples / autovacuum health:
--      SELECT relname, n_dead_tup, last_autovacuum FROM pg_stat_user_tables ORDER BY n_dead_tup DESC;
-- 2) Fix without blocking writes:
--      REINDEX INDEX CONCURRENTLY idx_accounts_balance;                 -- PG 12+
--      -- or: CREATE INDEX CONCURRENTLY new ...; DROP INDEX CONCURRENTLY old; (swap)
--    Table bloat online: pg_repack extension (or pg_squeeze).
-- 3) Prevent: tune autovacuum per hot table
--      ALTER TABLE accounts SET (autovacuum_vacuum_scale_factor = 0.02, autovacuum_vacuum_cost_limit = 2000);
--    Keep transactions short (long transactions / idle in transaction / stale replication slots block vacuum),
--    and leave room for HOT updates:  ALTER TABLE accounts SET (fillfactor = 85);  (needs non-indexed updated columns)

-- MySQL InnoDB comparison: updates are in place with old versions in the undo log (purged by background threads),
-- so there is no VACUUM; fragmentation is fixed with  OPTIMIZE TABLE t;  (rebuild; online DDL)  or
-- ALTER TABLE t ENGINE=InnoDB;  and monitored via  information_schema.tables.data_free.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: running VACUUM FULL on a busy table to "fix bloat" - ACCESS EXCLUSIVE lock blocks reads and writes
-- ✅ Use plain VACUUM (autovacuum), REINDEX CONCURRENTLY, or pg_repack.

-- ❌ Wrong: expecting plain VACUUM to shrink the files or the indexes (verified above: sizes unchanged)
--    (it only truncates empty pages at the END of a table file)

-- ❌ Wrong: disabling autovacuum "for performance" -> dead tuples pile up, and transaction-ID wraparound risk grows.

-- ❌ Wrong: indexing columns that are updated constantly (last_login, status counters) - this kills HOT updates
--    and bloats those indexes fastest. Index only what you query.
```

---

## 🎯 Interview Tip (1 line)
Say: "Bloat comes from MVCC dead tuples; I monitor with pg_stat_user_tables and pgstattuple, keep autovacuum tuned per hot table, avoid long-running transactions, rebuild indexes online with REINDEX CONCURRENTLY, and reserve VACUUM FULL or pg_repack for rare table-level bloat - plain VACUUM reuses space but rarely shrinks files."

---

## 🔗 Related Questions
→ Q081 (B-Tree index internals) | Q082 (Clustered vs non-clustered) | Q090 (Partial index) | Q092 (Hash index)
