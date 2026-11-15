---

# Q176. Galera Cluster — How It Works
# Category: MySQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL / MariaDB / Percona XtraDB Cluster (Galera)

---

## ❓ Question
How does Galera Cluster provide multi-primary MySQL? Explain certification-based (virtually synchronous) replication, what a "certification failure" is, how quorum and split-brain are handled, and how it differs from normal async replication.

---

## 💡 Quick Concept (2 lines only)
Every node can accept writes; at COMMIT the write-set (row keys + changes) is broadcast to all nodes, each runs a deterministic certification test, and the txn either commits everywhere or is rolled back on the origin node. It is "virtually synchronous": commit is global, but applying on other nodes is asynchronous.
हिंदी: Galera में हर node पर write हो सकता है; COMMIT पर write-set सब nodes को जाता है और certification pass होने पर सब जगह commit होता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT RUN: Galera needs the wsrep provider (galera library) and 3 nodes.
-- The stock MySQL 9.1 server used for verification has no wsrep support.
-- Everything below is standard configuration / status, flagged as unverified.
-- ============================================

-- ============================================
-- SETUP: minimal my.cnf on each of 3 nodes (unverified)
-- ============================================
-- [mysqld]
-- binlog_format            = ROW          -- Galera requires row-based
-- default_storage_engine   = InnoDB       -- MyISAM is NOT replicated (experimental only)
-- innodb_autoinc_lock_mode = 2            -- interleaved; needed for multi-writer
-- wsrep_on                 = ON
-- wsrep_provider           = /usr/lib/galera/libgalera_smm.so
-- wsrep_cluster_name       = shop_cluster
-- wsrep_cluster_address    = gcomm://10.0.0.1,10.0.0.2,10.0.0.3
-- wsrep_node_address       = 10.0.0.1
-- wsrep_sst_method         = mariabackup  -- or rsync / xtrabackup-v2 (PXC)

-- Bootstrap first node ONLY (never on a restart of an existing cluster blindly):
--   galera_new_cluster          (MariaDB)
--   systemctl start mysql@bootstrap   (PXC)

-- ============================================
-- SOLUTION: inspect cluster health (unverified output shape)
-- ============================================

SHOW STATUS LIKE 'wsrep_cluster_size';          -- 3
SHOW STATUS LIKE 'wsrep_cluster_status';        -- Primary   (anything else = non-primary partition, refuses writes)
SHOW STATUS LIKE 'wsrep_local_state_comment';   -- Synced    (Donor/Desynced, Joiner, Joined also exist)
SHOW STATUS LIKE 'wsrep_ready';                 -- ON
SHOW STATUS LIKE 'wsrep_flow_control_paused';   -- 0.0 ideal; ->1.0 means slowest node is throttling the whole cluster
SHOW STATUS LIKE 'wsrep_local_cert_failures';   -- counts certification conflicts
SHOW STATUS LIKE 'wsrep_local_bf_aborts';       -- local txns aborted by replicated "brute-force" writes

-- ============================================
-- CERTIFICATION CONFLICT EXAMPLE (two nodes update the same row)
-- ============================================

-- Node A:                                   Node B:
-- BEGIN;                                    BEGIN;
-- UPDATE stock SET qty = qty - 1            UPDATE stock SET qty = qty - 1
--   WHERE sku = 'A100';                       WHERE sku = 'A100';
-- COMMIT;  -- broadcast first, wins         COMMIT;  -- certification fails on B
--                                           -- ERROR 1213 (40001): Deadlock found when trying
--                                           --   to get lock; try restarting transaction
-- Optimistic locking: no cross-node locks while the txn runs. Conflict is found only at COMMIT.
-- Application MUST retry on 1213 / 40001.

-- ============================================
-- Quorum rules
-- ============================================
-- Nodes  | tolerates failure of | note
-- 3      | 1 node               | recommended minimum
-- 2      | 0 nodes              | one dies -> survivor loses quorum -> use garbd arbitrator as 3rd vote
-- 4      | 1 node               | 2/2 split = no quorum, so prefer odd counts
-- Minority partition becomes non-Primary and rejects reads/writes (prevents split-brain).
```

---

## 🔍 Why This Works (3 lines max)
Certification is deterministic: every node checks the incoming write-set against write-sets committed since its snapshot, so all nodes reach the same commit/abort decision without a 2-phase-commit round trip. State transfer for a new/rejoining node uses IST (incremental, gcache) or full SST (donor copy). Quorum (>50% of weighted votes) is what prevents two halves both accepting writes.
हिंदी: Certification हर node पर deterministic है इसलिए सब एक ही फैसला लेते हैं; quorum (>50%) split-brain रोकता है।

---

## ⚡ Alternative Solution

```sql
-- Practical pattern: write to ONE node via the load balancer (HAProxy/ProxySQL), read from all.
-- Avoids most certification conflicts and hot-row retry storms.

-- Compare with other MySQL HA options:
-- Async replication        : simple, can lose last commits, single writer
-- Semi-sync (Q174)         : near-lossless, single writer, failover orchestration needed
-- Group Replication / InnoDB Cluster : Oracle-native; same certification idea; single-primary default
-- Galera / PXC             : multi-primary, synchronous-ish, write throughput limited by slowest node

-- Wait for causal consistency after writing on another node (read-your-writes):
SET SESSION wsrep_sync_wait = 1;     -- reads wait until node applied all earlier replicated writes
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Large transactions (e.g. DELETE of 5M rows in one statement)
-- Whole write-set is buffered and replicated at COMMIT -> flow control stalls the cluster.
-- ✅ Batch: DELETE ... LIMIT 5000 in a loop (wsrep_max_ws_rows / wsrep_max_ws_size limits).

-- ❌ Tables without a PRIMARY KEY
-- Row ordering can differ per node -> inconsistent apply, poor performance.
-- ✅ Always define a PK on every table in a Galera cluster.

-- ❌ Using LOCK TABLES / GET_LOCK / SELECT ... FOR UPDATE for cross-node mutual exclusion
-- Those locks are node-local. Two nodes can both "hold" them.

-- ❌ Running 2 nodes without an arbitrator -> any single failure freezes the cluster.
```

---

## 🎯 Interview Tip (1 line)
Say: "Galera gives virtually-synchronous multi-primary with optimistic certification, so I send writes to one node, keep transactions small, retry on deadlock errors, and run an odd number of nodes (or garbd) so quorum can never split."

---

## 🔗 Related Questions
→ Q174 (Async vs semi-sync) | Q175 (GTID replication) | Q179 (xtrabackup, used for SST) | Q180 (max_connections)
