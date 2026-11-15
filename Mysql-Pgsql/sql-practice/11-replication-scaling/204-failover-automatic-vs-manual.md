---

# Q204. Failover — Automatic vs Manual
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
The primary database dies. Compare manual and automatic failover for MySQL and PostgreSQL: the step-by-step manual promotion, the tools that automate it, and the risks (split brain, data loss).

---

## 💡 Quick Concept (2 lines only)
Failover promotes a replica to primary and repoints clients. Manual is slow but safe (a human checks lag and fences the old node); automatic is fast but needs a consensus/fencing mechanism (Orchestrator, Patroni, InnoDB Cluster) to avoid split brain.
हिंदी: Failover में replica को primary बनाया जाता है; manual धीमा पर सुरक्षित, automatic तेज़ पर split-brain से बचने के लिए fencing/consensus ज़रूरी।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
-- Needs a multi-node cluster: NOT RUN. Below are concrete runbooks/commands.
-- Verified on a single MySQL 9.1.0: STOP REPLICA / RESET REPLICA ALL / SET GLOBAL read_only
-- parse and execute (with no replication configured they are effectively no-ops).

-- ============================================
-- SOLUTION A: MANUAL FAILOVER -- MySQL (GTID)           [not run on a real pair]
-- ============================================
-- 1. FENCE the old primary: power off / remove from LB / revoke network. Never skip.
-- 2. Pick the most caught-up replica:
--      SHOW REPLICA STATUS\G      -- compare Executed_Gtid_Set across replicas (largest superset wins)
--      SELECT WAIT_FOR_EXECUTED_GTID_SET('<primary-last-gtid-set>', 30);  -- drain relay log
-- 3. Promote:
STOP REPLICA;
RESET REPLICA ALL;                -- forget the old source (verified command)
SET GLOBAL super_read_only = 0;
SET GLOBAL read_only = 0;
-- 4. Repoint the other replicas to the new primary:
--      CHANGE REPLICATION SOURCE TO SOURCE_HOST='<new-primary>', SOURCE_AUTO_POSITION=1; START REPLICA;
-- 5. Switch app endpoint (DNS / VIP / ProxySQL hostgroup).
-- 6. Rebuild the old primary as a replica later (it may have errant GTIDs -> re-clone it).

-- ============================================
-- SOLUTION B: MANUAL FAILOVER -- PostgreSQL              [not run]
-- ============================================
--   pg_ctl promote -D /var/lib/postgresql/data           -- or:
SELECT pg_promote();                    -- PG12+; run on the chosen standby
SELECT pg_is_in_recovery();             -- false once promoted
--   other standbys: update primary_conninfo, restart; old primary: pg_rewind or re-basebackup

-- ============================================
-- SOLUTION C: AUTOMATIC                                  [not run]
-- ============================================
--  MySQL:  InnoDB Cluster / Group Replication (built-in, Paxos-based) + MySQL Router
--          Orchestrator (+ ProxySQL), or managed: RDS Multi-AZ / Aurora failover (~30-60 s)
--  PgSQL:  Patroni (etcd/Consul leader key) + HAProxy/vip-manager ; repmgr ; managed: RDS/Cloud SQL HA

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- Typical RTO (documented/typical, not measured here): manual 5-30 min, automatic 10-60 s.
-- After promotion:  MySQL  SELECT @@read_only -> 0 ;  PgSQL  SELECT pg_is_in_recovery() -> f
-- RPO: async replication may lose the last un-replicated transactions;
--      semi-sync / synchronous_commit = remote_apply reduces it to ~0 at a latency cost.
```

---

## 🔍 Why This Works (3 lines max)
Promotion is just "make a copy writable and move traffic", and the hard parts are choosing the most up-to-date replica and guaranteeing only ONE primary exists (fencing/quorum). Automation encodes those checks; manual relies on a human following a runbook.
हिंदी: Promotion आसान है, कठिन हिस्सा सबसे updated replica चुनना और यह पक्का करना है कि सिर्फ एक primary रहे।

---

## ⚡ Alternative Solution

```sql
-- Synchronous commit in PostgreSQL to prevent data loss on failover (postgresql.conf):
--   synchronous_standby_names = 'ANY 1 (standby1, standby2)'
--   synchronous_commit = on
-- MySQL semi-sync / Group Replication (group_replication_consistency = BEFORE_ON_PRIMARY_FAILOVER)

-- Planned switchover (zero data loss, no emergency): stop writes on old primary
--   MySQL:  SET GLOBAL super_read_only = 1;  wait replica catches up;  promote;
--   Patroni: patronictl switchover       | MySQL Shell: cluster.setPrimaryInstance('host:3306')
-- Drill it regularly (game days): untested failover = broken failover.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Automatic failover with no fencing: old primary "comes back" and accepts writes
--    => split brain, divergent data, painful reconciliation
-- ✅ STONITH / quorum / lease-based leader key (Patroni) / super_read_only on revival

-- ❌ Promoting a replica that is far behind -> silent data loss
-- ✅ Pick by GTID/LSN, and alert on lag so the candidate is always close (Q202)

-- ❌ Hard-coded primary IP in apps -> failover = redeploy. ✅ DNS/VIP/proxy endpoint + connection retry
-- ❌ Flapping failover on a network blip: set sane timeouts / cool-down
```

---

## 🎯 Interview Tip (1 line)
Say: "I choose by RTO/RPO: managed or Patroni/InnoDB Cluster automatic failover with fencing and quorum for tight RTO, semi-sync or synchronous replication where RPO must be near zero, a rehearsed manual runbook as the fallback, and I always test failover and the app's reconnect behaviour."

---

## 🔗 Related Questions
→ Q201 (Replication setup) | Q202 (Replication lag) | Q203 (Read replica routing) | Q198 (PgSQL replication)
