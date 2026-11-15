---

# Q148. Wait Stats Basics
# Category: Performance Tuning
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: performance_schema waits | PostgreSQL: pg_stat_activity wait_event). Not executed on SQL Server; behaviour per Microsoft docs.

---

## ❓ Question
The server feels slow but CPU is only 30%. How do you use wait statistics to find what sessions are waiting for, and what do the common wait types mean?

---

## 💡 Quick Concept (2 lines only)
Every worker is either running, runnable (waiting for CPU) or suspended (waiting on a resource). `sys.dm_os_wait_stats` accumulates time spent waiting per wait type since the last restart or clear; the top waits point to the bottleneck class (I/O, locks, CPU, memory grants).
हिंदी: Wait stats बताते हैं SQL Server किसका इंतज़ार कर रहा है। Top wait से bottleneck (IO / lock / CPU) पता चलता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- Top waits since restart (not executed on SQL Server; behaviour per Microsoft docs)
-- Filter out benign background waits - the list below is a SMALL sample, not complete.
-- ============================================
SELECT TOP 10
    wait_type,
    wait_time_ms / 1000.0                       AS wait_s,
    (wait_time_ms - signal_wait_time_ms) / 1000.0 AS resource_wait_s,
    signal_wait_time_ms / 1000.0                AS signal_wait_s,   -- time waiting for CPU after resource was ready
    waiting_tasks_count,
    100.0 * wait_time_ms / SUM(wait_time_ms) OVER () AS pct
FROM sys.dm_os_wait_stats
WHERE wait_type NOT IN (N'SLEEP_TASK', N'LAZYWRITER_SLEEP', N'XE_TIMER_EVENT',
                        N'REQUEST_FOR_DEADLOCK_SEARCH', N'SQLTRACE_BUFFER_FLUSH',
                        N'BROKER_TO_FLUSH', N'CHECKPOINT_QUEUE', N'WAITFOR')
  AND wait_time_ms > 0
ORDER BY wait_time_ms DESC;

-- Live view: what is each active request waiting on right now
SELECT session_id, status, wait_type, wait_time, blocking_session_id
FROM sys.dm_exec_requests
WHERE session_id > 50;

-- Azure SQL Database: use sys.dm_db_wait_stats (database scope)
-- Reset counters only on a test box:  DBCC SQLPERF (N'sys.dm_os_wait_stats', CLEAR);

-- Commonly seen waits (meaning per Microsoft docs):
--   PAGEIOLATCH_SH / _EX   reading data pages from disk -> slow storage, missing index, low memory
--   WRITELOG               commit waiting for log flush -> log disk latency, too many tiny commits
--   LCK_M_*                blocking on locks -> long transactions, missing index, isolation level
--   CXPACKET / CXCONSUMER  parallelism (not always a problem by itself)
--   SOS_SCHEDULER_YIELD    CPU pressure
--   RESOURCE_SEMAPHORE     queries waiting for memory grant
--   ASYNC_NETWORK_IO       client slow to consume rows (app reading row by row / SELECT *)

-- EXPECTED OUTPUT: shape only; values depend on workload (nothing invented here):
--   wait_type | wait_s | resource_wait_s | signal_wait_s | waiting_tasks_count | pct
```

---

## 🔍 Why This Works (3 lines max)
Waits convert "slow" into a category, so you tune the right layer instead of guessing. High signal_wait relative to total means CPU pressure; high resource wait means the resource itself.
हिंदी: Signal wait ज़्यादा = CPU की कमी। Resource wait ज़्यादा = disk/lock/memory problem।

---

## ⚡ Alternative Solution

```sql
-- Two snapshots a minute apart and diff them to see current behaviour, not history since boot
SELECT wait_type, wait_time_ms INTO #w1 FROM sys.dm_os_wait_stats;
WAITFOR DELAY '00:01:00';
SELECT w2.wait_type, w2.wait_time_ms - w1.wait_time_ms AS delta_ms
FROM sys.dm_os_wait_stats w2 JOIN #w1 w1 ON w1.wait_type = w2.wait_type
WHERE w2.wait_time_ms - w1.wait_time_ms > 0
ORDER BY delta_ms DESC;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Reading cumulative waits since a months-old restart: the current problem is buried
-- ❌ Not excluding benign waits (SLEEP_TASK, WAITFOR...): they dominate the list
-- ❌ "CXPACKET is high, so set MAXDOP 1": parallelism waits are often a symptom
--    (bad estimates, missing index). Check cost threshold and MAXDOP sanely.
-- ❌ Treating NOLOCK as the fix for LCK_M_* waits (Q125, Q183)
```

---

## 🎯 Interview Tip (1 line)
Say: "I diff wait stats over a window, ignore benign waits, then drill from the top wait to the cause: PAGEIOLATCH to I/O or missing indexes, LCK_M to blocking chains, WRITELOG to log latency, ASYNC_NETWORK_IO to the app. Then confirm in Query Store or the plan."

---

## 🔗 Related Questions
→ Q142 (Finding slow queries) | Q123 (Blocking vs deadlock) | Q149 (tempdb contention) | Q156 (Monitoring and baselines)
