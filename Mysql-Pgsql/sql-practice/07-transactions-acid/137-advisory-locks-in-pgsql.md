---

# Q137. Advisory Locks in PgSQL
# Category: Transactions & ACID
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL (MySQL equivalent: GET_LOCK) — PgSQL run on PGlite (single session, so cross-session blocking NOT shown); MySQL GET_LOCK run on 9.1.0 with two sessions

---

## ❓ Question
You need to make sure only one instance of a cron job (or one worker per customer/invoice) runs at a time across many app servers, with no table row to lock. How do advisory locks solve this, what is the difference between session-level and transaction-level, and what is the MySQL equivalent?

---

## 💡 Quick Concept (2 lines only)
Advisory locks are application-defined mutexes stored in the DB lock manager, identified by a number (or two ints); the DB never checks them against data, your code decides what they mean. Session-level ones live until unlocked or disconnect, `_xact_` ones auto-release at COMMIT/ROLLBACK.
हिंदी: Advisory lock DB में आपका अपना mutex है (एक number से पहचान); इसका किसी row से संबंध नहीं, अर्थ आप तय करते हो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
-- No tables needed: the lock key is just a bigint (or two ints).

-- ============================================
-- SOLUTION (PostgreSQL)
-- ============================================

-- Step 1: try to take the lock without waiting
SELECT pg_try_advisory_lock(42) AS got_first;                 -- true  = you are the leader
-- Step 2: the same session can take it again (re-entrant, counted)
SELECT pg_try_advisory_lock(42) AS got_again_same_session;    -- true
-- Step 3: look at it
SELECT locktype, classid, objid, mode, granted
FROM pg_locks WHERE locktype = 'advisory';
-- Step 4: must unlock as many times as you locked
SELECT pg_advisory_unlock(42);                                -- true
SELECT pg_advisory_unlock(42);                                -- true
SELECT pg_advisory_unlock(42);                                -- false (not held any more)

-- Transaction-scoped lock keyed by a string (hash it to a bigint):
BEGIN;
SELECT pg_try_advisory_xact_lock(hashtext('invoice:1001'));   -- true
-- ... process invoice 1001 safely ...
COMMIT;                                                       -- lock released automatically

-- ============================================
-- EXPECTED OUTPUT (real PGlite)
-- ============================================

-- got_first = true
-- got_again_same_session = true
-- locktype | classid | objid | mode          | granted
-- advisory | 0       | 42    | ExclusiveLock | true
-- unlock calls: true, true, false
-- xact lock: true ; advisory locks while in txn = 1 ; after COMMIT = 0
-- hashtext('invoice:1001') = -361589191   (stable hash; fine as a key)

-- ============================================
-- What a SECOND session would see (standard Postgres behaviour; not runnable on PGlite)
-- ============================================
-- SELECT pg_try_advisory_lock(42);   -> false  (immediately)
-- SELECT pg_advisory_lock(42);       -> BLOCKS until the first session unlocks/disconnects

-- ============================================
-- MySQL equivalent (real MySQL 9.1.0, two sessions)
-- ============================================
-- Session A: SELECT GET_LOCK('nightly_report', 5);          -- 1 (got it)
-- Session B: SELECT GET_LOCK('nightly_report', 0);          -- 0 (timeout 0 = don't wait)
-- Session B: SELECT IS_USED_LOCK('nightly_report') IS NOT NULL;   -- 1 (someone holds it)
-- Session A: SELECT RELEASE_LOCK('nightly_report');         -- 1
-- Session B: SELECT GET_LOCK('nightly_report', 5);          -- 1 (waited ~2s, then acquired)
-- MySQL locks are always session-level (no automatic per-transaction release),
-- names are strings (max 64 chars), and a session releases them on disconnect.
```

---

## 🔍 Why This Works (3 lines max)
The lock manager treats the key like any lock: exclusive holders conflict, others wait or fail on try_. Because it is not tied to a row or table, it works for "one cron leader" or "serialize per tenant" without a dummy table.
हिंदी: Lock manager key को आम lock की तरह संभालता है; row या table से जुड़ा न होने से "एक ही cron चले" जैसे काम बिना dummy table के हो जाते हैं।

---

## ⚡ Alternative Solution

```sql
-- Shared vs exclusive (PgSQL)
SELECT pg_advisory_lock_shared(7);     -- many readers allowed, blocks exclusive
SELECT pg_advisory_lock(7);            -- exclusive

-- Two-int key form: (namespace, id) avoids collisions between features
SELECT pg_try_advisory_lock(1001, 55);  -- 1001 = "invoice jobs", 55 = invoice id

-- Instead of advisory locks:
--  * a real row + SELECT ... FOR UPDATE (lock tied to data, visible in the schema)
--  * a UNIQUE "leader" table row with a lease timestamp (survives failover logic better)
--  * SKIP LOCKED queue (Q136) when you want work distribution, not a single leader
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: session-level lock + connection pooler in transaction mode (PgBouncer)
SELECT pg_advisory_lock(42);   -- may run on server connection #1
-- ... next statement goes to connection #2 -> unlock on #2 returns false,
--     and the lock stays held on #1 forever (leak)
-- ✅ Use pg_advisory_xact_lock inside a transaction (pool-safe), or session pooling.

-- ❌ Wrong: forgetting that locks are counted
-- Locked twice -> must unlock twice (we saw true, true, false above).

-- ❌ Wrong: hashing strings with a weak/colliding scheme -> unrelated jobs block each other.
--    Namespace keys with the two-int form.

-- ❌ Wrong: assuming locks are replicated - they exist only on the primary that took them.
-- MySQL: GET_LOCK on one server does not protect against another server/shard.
```

---

## 🎯 Interview Tip (1 line)
Say: "For cron-leader election or per-entity serialization I use pg_try_advisory_xact_lock so it is released automatically and is safe behind PgBouncer; session-level locks leak with transaction pooling."

---

## 🔗 Related Questions
→ Q128 (FOR UPDATE vs FOR SHARE) | Q136 (SKIP LOCKED queue) | Q129 (Deadlock) | Q132 (Row vs table locking)
