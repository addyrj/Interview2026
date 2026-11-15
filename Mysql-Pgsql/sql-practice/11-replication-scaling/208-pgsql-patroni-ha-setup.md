---

# Q208. PgSQL Patroni — HA Setup
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL

---

## ❓ Question
How does Patroni give PostgreSQL automatic failover? Show a minimal patroni.yml for a 3-node cluster with etcd, the failover flow, and the commands to inspect and switch over.

---

## 💡 Quick Concept (2 lines only)
Patroni runs next to each Postgres, keeps a leader key with a TTL in a DCS (etcd/Consul/ZooKeeper); whoever holds the key is primary, and if it expires a healthy replica wins the election and is promoted.
हिंदी: Patroni DCS (etcd) में leader key रखता है; primary मरे तो key expire होती है और सबसे अच्छा replica promote हो जाता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT RUN: Patroni/etcd/HAProxy are not installed here. Config is the
-- standard shape from the Patroni docs; verify keys against your version.
-- ============================================

-- ============================================
-- /etc/patroni/patroni.yml on node1  (YAML, NOT RUN)
-- ============================================
-- scope: orders-cluster                 # cluster name, same on all nodes
-- name: pg-node1                        # unique per node
-- restapi:
--   listen: 0.0.0.0:8008
--   connect_address: 10.0.0.1:8008
-- etcd3:
--   hosts: 10.0.0.11:2379,10.0.0.12:2379,10.0.0.13:2379
-- bootstrap:
--   dcs:
--     ttl: 30                           # leader key TTL (s)
--     loop_wait: 10
--     retry_timeout: 10
--     maximum_lag_on_failover: 1048576  # bytes; too-lagging replicas can't be promoted
--     synchronous_mode: false           # true = no data loss, may block writes
--     postgresql:
--       use_pg_rewind: true
--       parameters:
--         wal_level: replica
--         hot_standby: "on"
--         max_wal_senders: 10
--         max_replication_slots: 10
-- postgresql:
--   listen: 0.0.0.0:5432
--   connect_address: 10.0.0.1:5432
--   data_dir: /var/lib/postgresql/16/main
--   authentication:
--     replication: {username: replicator, password: "..."}
--     superuser:   {username: postgres,   password: "..."}

-- ============================================
-- Operate (shell, NOT RUN)
-- ============================================
-- patronictl -c /etc/patroni/patroni.yml list
-- + Cluster: orders-cluster -----+---------+-----------+----+-----------+
-- | Member    | Host      | Role    | State     | TL | Lag in MB |
-- | pg-node1  | 10.0.0.1  | Leader  | running   | 5  |           |
-- | pg-node2  | 10.0.0.2  | Replica | streaming | 5  | 0         |
-- | pg-node3  | 10.0.0.3  | Replica | streaming | 5  | 0         |
-- (illustrative layout, not captured output)

-- patronictl switchover --leader pg-node1 --candidate pg-node2   # planned, graceful
-- patronictl failover                                            # forced
-- patronictl edit-config                                         # change PG params cluster-wide

-- ============================================
-- Client routing: HAProxy health-checks Patroni REST API (NOT RUN)
-- ============================================
-- listen postgres_write
--   bind *:5000
--   option httpchk GET /primary         # 200 only on leader
--   server node1 10.0.0.1:5432 check port 8008
--   server node2 10.0.0.2:5432 check port 8008
-- listen postgres_read
--   bind *:5001
--   option httpchk GET /replica
-- REST: GET /primary, /replica, /health

-- Verify role from SQL on any node:
SELECT pg_is_in_recovery();      -- false on leader, true on replicas
```

MySQL equivalent: InnoDB Cluster/Group Replication (Q205) or Orchestrator + ProxySQL (Q206).

---

## 🔍 Why This Works (3 lines max)
The leader must keep renewing the TTL key; if Patroni or the node dies, the key expires and replicas race to take it, the freshest (within maximum_lag_on_failover) wins. A node that cannot reach the DCS demotes itself, which prevents split-brain.
हिंदी: Leader को TTL key renew करनी पड़ती है; DCS से कटा node खुद demote हो जाता है, इसलिए split-brain नहीं होता।

---

## ⚡ Alternative Solution

```sql
-- repmgr: simpler, no DCS, but needs a witness node and has weaker fencing.
-- Managed (RDS Multi-AZ / Cloud SQL / Aurora): the provider does failover for you.
-- pg_auto_failover (Citus team): a "monitor" node instead of etcd.

-- Zero-data-loss option (NOT RUN): synchronous_mode: true in dcs config
--  -> Patroni sets synchronous_standby_names and only promotes the sync standby.
--  -> if the sync standby is gone, writes block unless synchronous_mode_strict: false.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Running a 2-member etcd (or 2-node DCS): no quorum on one failure.
-- ✅ 3 or 5 DCS members, separate from DB hosts if possible.

-- ❌ Changing postgresql.conf by hand on one node -> Patroni overwrites it / drift.
-- ✅ Use patronictl edit-config.

-- ❌ App connects straight to node1's IP. After failover it writes to a replica
--    ("cannot execute INSERT in a read-only transaction").
-- ✅ Connect via HAProxy/VIP/pgBouncer endpoint that follows the leader.
```

---

## 🎯 Interview Tip (1 line)
Say: "Patroni plus etcd gives leader election with fencing: I keep ttl/loop_wait/retry_timeout consistent with network reality, use pg_rewind for old primaries, HAProxy on /primary for routing, test with switchovers regularly, and accept async data-loss window bounded by maximum_lag_on_failover unless I enable synchronous_mode."

---

## 🔗 Related Questions
→ Q207 (streaming replication) | Q215 (PgBouncer) | Q216 (database proxy) | Q218 (PITR)
