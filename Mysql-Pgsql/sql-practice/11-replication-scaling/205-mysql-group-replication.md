---

# Q205. MySQL Group Replication
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL (8.0+)

---

## ❓ Question
How does MySQL Group Replication (GR) differ from classic async replication? Show the config to bootstrap a 3-node group, how to check member state, and what happens when a node fails or the network partitions.

---

## 💡 Quick Concept (2 lines only)
GR is a Paxos-based group communication layer: every transaction is certified by a majority before commit, giving automatic failover and no lost committed writes (single-primary by default).
हिंदी: Group Replication = majority (Paxos) से certify होकर commit, automatic failover, committed data lose नहीं होता।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOTE: A real group needs 3 servers. NOT RUN here (only a standalone
-- MySQL 9.1 was available). What WAS run: the monitoring queries on a
-- standalone server (they return an empty set because no group exists).
-- ============================================

-- ============================================
-- Prerequisites on EVERY node (my.cnf) -- NOT RUN
-- ============================================
-- [mysqld]
-- server_id                         = 1            # unique per node
-- gtid_mode                         = ON
-- enforce_gtid_consistency          = ON
-- binlog_format                     = ROW
-- log_replica_updates               = ON
-- plugin_load_add                   = 'group_replication.so'
-- group_replication_group_name      = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
-- group_replication_local_address   = 'db1:33061'
-- group_replication_group_seeds     = 'db1:33061,db2:33061,db3:33061'
-- group_replication_bootstrap_group = OFF
-- group_replication_single_primary_mode = ON       # 1 writer, N readers
-- All tables MUST be InnoDB and have a PRIMARY KEY.

-- ============================================
-- Bootstrap (ONLY on the first node, ONLY once) -- NOT RUN
-- ============================================
CREATE USER 'repl'@'%' IDENTIFIED BY 'Str0ng!Pass' REQUIRE SSL;
GRANT REPLICATION SLAVE, BACKUP_ADMIN ON *.* TO 'repl'@'%';
CHANGE REPLICATION SOURCE TO
  SOURCE_USER='repl', SOURCE_PASSWORD='Str0ng!Pass'
  FOR CHANNEL 'group_replication_recovery';

SET GLOBAL group_replication_bootstrap_group = ON;
START GROUP_REPLICATION;
SET GLOBAL group_replication_bootstrap_group = OFF;   -- never leave ON

-- On db2, db3: just START GROUP_REPLICATION; (they join + clone/recover)

-- ============================================
-- Monitoring (this part was run on standalone 9.1.0)
-- ============================================
SELECT MEMBER_HOST, MEMBER_STATE, MEMBER_ROLE
FROM performance_schema.replication_group_members;

-- Expected on a healthy 3-node group (NOT RUN):
-- MEMBER_HOST | MEMBER_STATE | MEMBER_ROLE
-- db1         | ONLINE       | PRIMARY
-- db2         | ONLINE       | SECONDARY
-- db3         | ONLINE       | SECONDARY

-- Real output on my standalone server: Empty set (no group configured)

SHOW VARIABLES LIKE 'binlog_format';   -- Real: ROW
SHOW VARIABLES LIKE 'gtid_mode';       -- Real: OFF  (GR needs ON)

-- Who is primary right now?
SELECT MEMBER_HOST FROM performance_schema.replication_group_members
WHERE MEMBER_ROLE = 'PRIMARY';

-- Lag / backlog per member
SELECT MEMBER_ID, COUNT_TRANSACTIONS_REMOTE_IN_APPLIER_QUEUE AS queue
FROM performance_schema.replication_group_member_stats;
```

PgSQL: no GR. Closest equivalents are streaming replication + Patroni (Q207, Q208), or extensions like BDR (multi-master).

---

## 🔍 Why This Works (3 lines max)
A transaction is broadcast to the group; a majority must certify it (no write-set conflict) before the origin commits. Losing 1 of 3 nodes keeps quorum (2/3); losing 2 blocks writes to protect against split-brain.
हिंदी: Majority ने OK किया तभी commit। 3 में से 1 node गिरे तो चलता है, 2 गिरे तो writes रुक जाते हैं (split-brain से बचाव)।

---

## ⚡ Alternative Solution

```sql
-- InnoDB Cluster = Group Replication + MySQL Shell + MySQL Router (NOT RUN)
-- mysqlsh> dba.createCluster('prodCluster')
-- mysqlsh> cluster.addInstance('root@db2:3306')
-- mysqlsh> cluster.status()
-- Router: port 6446 = read/write (primary), 6447 = read-only (secondaries)

-- Multi-primary mode (all nodes accept writes) -- avoid unless needed:
-- SET GLOBAL group_replication_single_primary_mode = OFF;
-- SET GLOBAL group_replication_enforce_update_everywhere_checks = ON;
-- Conflicting writes -> the later certifier gets rolled back (error 3101).

-- Classic async/semi-sync alternative: can lose last txns on source crash.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Leaving bootstrap ON, or bootstrapping on 2 nodes -> two independent
--    groups = split brain.
SET GLOBAL group_replication_bootstrap_group = ON;   -- on db1 AND db2  (WRONG)

-- ❌ Tables without a PRIMARY KEY or MyISAM tables -> transactions rejected.
-- ❌ Assuming "synchronous" = zero lag. Apply is async: reads on a
--    secondary can be stale. Use group_replication_consistency:
-- ✅ SET SESSION group_replication_consistency = 'BEFORE_ON_PRIMARY_FAILOVER';
-- ✅ or 'AFTER' / 'BEFORE_AND_AFTER' for read-your-writes (costs latency).
```

---

## 🎯 Interview Tip (1 line)
Say: "GR gives majority-certified commits and automatic primary election, but it's not free: write latency includes a network round trip to a quorum, large transactions hurt, and I'd run it as InnoDB Cluster with MySQL Router across 3 zones, still monitoring applier queue and using group_replication_consistency where read-your-writes matters."

---

## 🔗 Related Questions
→ Q206 (ProxySQL) | Q207 (PgSQL streaming replication) | Q208 (Patroni) | Q216 (database proxy)
