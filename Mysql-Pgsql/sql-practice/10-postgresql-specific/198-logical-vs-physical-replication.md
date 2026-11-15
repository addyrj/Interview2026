---

# Q198. Logical Replication vs Physical Replication
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL (MySQL contrast included)

---

## ❓ Question
Compare PostgreSQL physical (streaming) replication with logical replication. When would you use each, and how do you set up a logical publication/subscription?

---

## 💡 Quick Concept (2 lines only)
Physical ships raw WAL blocks, producing a byte-identical standby for the WHOLE cluster (read-only, same major version). Logical decodes WAL into row changes (INSERT/UPDATE/DELETE) per table, so you can replicate a subset, across versions, into a writable target.
हिंदी: Physical पूरे cluster की WAL copy करता है (identical, read-only replica); Logical table-wise row changes भेजता है (selective, cross-version, target writable)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP -- PostgreSQL  (config + commands; NOT RUN end-to-end:
--          PGlite is a single embedded instance with no networking/replication slots)
-- ============================================

-- Both modes need on the PRIMARY (restart):
--   wal_level = logical          -- 'replica' is enough for physical only
--   max_wal_senders = 10
--   max_replication_slots = 10

-- ============================================
-- SOLUTION A: PHYSICAL (streaming replica)   [not run]
-- ============================================
-- primary: CREATE ROLE replicator REPLICATION LOGIN PASSWORD '...';
--          pg_hba.conf: host replication replicator 10.0.0.0/24 scram-sha-256
-- standby: pg_basebackup -h primary -U replicator -D /var/lib/postgresql/data -R -X stream
--          (-R writes standby.signal + primary_conninfo)
-- check on primary:
SELECT client_addr, state, sent_lsn, replay_lsn,
       pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
FROM pg_stat_replication;

-- ============================================
-- SOLUTION B: LOGICAL (publication / subscription)
-- ============================================

-- On the PUBLISHER (the CREATE PUBLICATION part was RUN on PGlite):
CREATE TABLE products (id INT PRIMARY KEY, name TEXT);   -- PK (or REPLICA IDENTITY) needed for UPDATE/DELETE
CREATE PUBLICATION pub_products FOR TABLE products;
SELECT pubname, puballtables, pubinsert, pubupdate, pubdelete FROM pg_publication;

-- On the SUBSCRIBER (separate server; table must already exist; NOT RUN):
CREATE SUBSCRIPTION sub_products
  CONNECTION 'host=primary dbname=shop user=replicator password=...'
  PUBLICATION pub_products;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- Verified on PGlite:  SHOW wal_level -> replica   (so logical needs the config change + restart)
-- pg_publication:  pubname = pub_products | puballtables = f | pubinsert = t | pubupdate = t | pubdelete = t
-- Everything involving a second server (pg_basebackup, CREATE SUBSCRIPTION,
-- pg_stat_replication rows) is NOT verified here.
```

---

## 🔍 Why This Works (3 lines max)
Physical replay applies the same disk-level WAL records, so the standby must match version/architecture and can only be read-only, but it is simple, complete, and lowest overhead. Logical decoding turns WAL into row events via a replication slot, enabling selective, cross-version, zero-downtime upgrade and CDC use cases at the cost of no DDL replication and sequences not being synced.
हिंदी: Physical = identical copy, HA और read scaling के लिए; Logical = चुनिंदा tables, version upgrade और CDC के लिए, पर DDL और sequences अपने आप sync नहीं होते।

---

## ⚡ Alternative Solution

```sql
-- Comparison cheat-sheet
-- Feature            | Physical (streaming)        | Logical (pub/sub)
-- Granularity        | whole cluster               | per table / filtered rows (PG15+)
-- Standby writable?  | no (hot standby read-only)  | yes
-- Cross major ver.   | no                          | yes (upgrade path)
-- DDL replicated?    | yes (it's the same files)   | NO -- apply schema changes manually
-- Sequences          | yes                         | NO -- setval them at cut-over
-- Use for            | HA failover, read replicas  | migration, CDC, partial/multi-source

-- Row filter + column list (PostgreSQL 15+):
CREATE PUBLICATION pub_active_products FOR TABLE products (id, name) WHERE (id > 100);

-- MySQL: its native replication is logical-ish by design (binlog events, binlog_format=ROW
-- verified as the 9.1 default). MySQL has no physical block-level equivalent built in;
-- Percona XtraBackup / clone plugin copy physical data only to seed a replica.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Logical replication on a table without a primary key
-- UPDATE/DELETE fail on the publisher: "cannot update table ... does not have a replica identity"
-- ✅ Add a PK or ALTER TABLE t REPLICA IDENTITY FULL

-- ❌ Forgetting a stuck/unused replication slot: WAL piles up and fills the disk
SELECT slot_name, active, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained
FROM pg_replication_slots;
-- ✅ Monitor it; set max_slot_wal_keep_size; drop dead slots

-- ❌ Expecting schema changes and sequence values to appear on the subscriber
```

---

## 🎯 Interview Tip (1 line)
Say: "Physical streaming replication is my default for HA and read replicas; logical replication is for selective sync, major-version upgrades with minimal downtime and CDC, and I always monitor replication slots because an abandoned slot can fill the WAL disk."

---

## 🔗 Related Questions
→ Q201 (MySQL replication setup) | Q202 (Replication lag) | Q204 (Failover) | Q220 (Zero-downtime migration)
