---

# Q180. MySQL Connection Handling — max_connections
# Category: MySQL Specific
# Difficulty: ⭐⭐ Medium
# DB: MySQL (8.0+ / 9.x)

---

## ❓ Question
How does MySQL handle client connections? What happens when `max_connections` is reached (error 1040), what is the extra SUPER connection, how do you monitor usage, and why is "just raise max_connections" usually the wrong fix?

---

## 💡 Quick Concept (2 lines only)
By default MySQL uses one OS thread per connection (`one-thread-per-connection`, with a `thread_cache_size` cache); once `max_connections` is hit new clients get ERROR 1040 "Too many connections". Each connection costs memory (session buffers, thread stack), so fix leaks and add pooling instead of raising the limit.
हिंदी: MySQL हर connection के लिए एक thread चलाता है; limit भरने पर ERROR 1040 आता है, इसलिए pooling/leaks ठीक करो, सिर्फ़ limit बढ़ाना हल नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP + current settings (real defaults, MySQL 9.1.0)
-- ============================================
SHOW GLOBAL VARIABLES LIKE 'max_connections';        -- 151
SHOW GLOBAL VARIABLES LIKE 'max_user_connections';   -- 0 (unlimited per account)
SHOW GLOBAL VARIABLES LIKE 'wait_timeout';           -- 28800 (8 h idle before server closes it)
SHOW GLOBAL VARIABLES LIKE 'thread_handling';        -- one-thread-per-connection
SHOW GLOBAL VARIABLES LIKE 'thread_cache_size';      -- 9 (auto-sized default)

-- ============================================
-- SOLUTION: reproduce error 1040 safely
-- ============================================
CREATE USER 'app'@'%' IDENTIFIED BY 'pw';
SET GLOBAL max_connections = 2;                      -- tiny on purpose

-- From the shell, three sessions as 'app' each running SELECT SLEEP(6):
--   mysql -uapp -ppw -e "select sleep(6)" &   (x3)
-- Real result: sessions 1 and 2 ran; session 3 failed immediately with
--   ERROR 1040 (08004): Too many connections

SELECT COUNT(*) FROM information_schema.processlist;   -- 4  (2 app sessions + my root session + event_scheduler thread)
SHOW GLOBAL STATUS LIKE 'Connection_errors_max_connections';  -- 1   <- the rejected attempt
SHOW GLOBAL STATUS LIKE 'Max_used_connections';               -- 3   <- limit 2 + 1 extra admin connection

-- Note: the server allows max_connections + 1 so a privileged account (CONNECTION_ADMIN / SUPER)
-- can still log in and diagnose. Never give application users that privilege.

SET GLOBAL max_connections = 151;                    -- restore

-- ============================================
-- MONITORING queries
-- ============================================
SHOW GLOBAL STATUS WHERE Variable_name IN
 ('Threads_connected','Threads_running','Max_used_connections','Aborted_connects',
  'Connection_errors_max_connections','Connections');
-- Real values on the idle test box:
-- Aborted_connects 0 | Connection_errors_max_connections 0 | Connections 13
-- Max_used_connections 1 | Threads_connected 1 | Threads_running 2

-- Headroom check: how close have we been to the ceiling?
SELECT ROUND(100 * (SELECT VARIABLE_VALUE FROM performance_schema.global_status
                    WHERE VARIABLE_NAME = 'Max_used_connections') / @@max_connections, 1) AS pct_used_peak;
-- Result (real, after restoring max_connections=151): 2.0 shown as 2   (peak 3 of 151 connections)

-- Who is hogging connections?
SELECT user, host, COUNT(*) AS conns, SUM(command = 'Sleep') AS idle
FROM information_schema.processlist
GROUP BY user, host ORDER BY conns DESC;
-- Result (real, idle box): root@localhost 1 conn / 0 idle ; event_scheduler@localhost 1 conn / 0 idle
```

---

## 🔍 Why This Works (3 lines max)
Threads_connected counts open sessions while Threads_running counts those executing; a big gap means mostly idle pooled connections, a Threads_running spike means contention. The limit protects memory: each session can allocate sort/join/read buffers, so 5000 connections x tens of MB can OOM the box.
हिंदी: Threads_connected = खुले sessions, Threads_running = चल रहे queries; हर connection memory खाता है, इसलिए limit memory की रक्षा करती है।

---

## ⚡ Alternative Solution

```sql
-- Per-account cap so one noisy service cannot starve the rest:
ALTER USER 'app'@'%' WITH MAX_USER_CONNECTIONS 50;
-- or CREATE USER ... WITH MAX_USER_CONNECTIONS 50 MAX_QUERIES_PER_HOUR 0;

-- Persist a changed limit across restarts (8.0+):
SET PERSIST max_connections = 500;

-- Kill idle sessions sooner (interactive vs non-interactive):
SET GLOBAL wait_timeout = 600;

-- Real fix: connection pooling in the app (HikariCP, SQLAlchemy pool) or a proxy (ProxySQL, MySQL Router)
-- that multiplexes thousands of clients onto ~50-100 backend connections.
-- Enterprise/Percona offer a thread pool (thread_handling = pool-of-threads) for high concurrency.

-- PostgreSQL contrast: process-per-connection is much heavier, so PgBouncer is near-mandatory beyond a few hundred connections.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ "Too many connections? Set max_connections = 10000."
-- Memory = max_connections x per-session buffers; also context-switch overhead kills throughput.
-- ✅ Find WHY: connection leak, missing pool, slow query pile-up holding connections (check Threads_running).

-- ❌ Connecting as root/SUPER from applications
-- Consumes the reserved extra slot, so you cannot even log in during an incident.

-- ❌ Pool size per app instance x number of instances > max_connections
-- 40 pods x pool 20 = 800 connections vs limit 151.
-- ✅ Budget: sum(pool_max across all instances) < max_connections - admin headroom.

-- ❌ SET GLOBAL max_connections=... and forgetting my.cnf / SET PERSIST -> reverts on restart.
```

---

## 🎯 Interview Tip (1 line)
Say: "Error 1040 is a symptom: I check Threads_running vs Threads_connected, find leaks or slow queries, cap per-user connections, budget pool sizes across instances, and put ProxySQL or a pooler in front instead of inflating max_connections."

---

## 🔗 Related Questions
→ Q178 (Slow query log) | Q162 (Buffer pool) | Q242 (SELECT FOR UPDATE, long txns hold connections) | Q241 (Sharding)
