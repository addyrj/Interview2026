---

# Q195. PgSQL Advisory Locks — pg_try_advisory_lock
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL

---

## ❓ Question
Three app servers run the same nightly cron job; only one may run it at a time. How do you implement this with PostgreSQL advisory locks, and what is the difference between session-level and transaction-level locks?

---

## 💡 Quick Concept (2 lines only)
Advisory locks are application-defined locks on a 64-bit number (or two 32-bit ints); the DB enforces them but attaches no meaning to them. `pg_try_advisory_lock` returns true/false immediately instead of waiting.
हिंदी: Advisory lock एक number पर app-defined lock है; try वाला version wait नहीं करता, तुरंत true/false देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)  -- PostgreSQL
-- ============================================
-- No tables needed. Choose a stable integer key per job, e.g. hash of a name:
SELECT hashtext('nightly-report') AS lock_key;   -- 759228614 (hashtext is internal; any fixed int works)

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1 (cron worker): try to take the lock, never wait
SELECT pg_try_advisory_lock(42) AS got_lock;      -- true  -> I am the runner
-- other workers (OTHER sessions) running the same call get: false -> exit quietly

-- Step 2: same session asking again SUCCEEDS (locks are re-entrant and stack)
SELECT pg_try_advisory_lock(42);                  -- true (count = 2)

-- Step 3: inspect
SELECT locktype, classid, objid, mode, granted FROM pg_locks WHERE locktype = 'advisory';

-- Step 4: release -- once per acquisition!
SELECT pg_advisory_unlock(42);                    -- true
SELECT pg_advisory_unlock(42);                    -- true
SELECT pg_advisory_unlock(42) AS third_unlock;    -- false (warning: not held)

-- Step 5: transaction-level lock: auto-released on COMMIT/ROLLBACK, no unlock call
BEGIN;
SELECT pg_try_advisory_xact_lock(7) AS got;       -- true
SELECT count(*) FROM pg_locks WHERE locktype = 'advisory';   -- 1
COMMIT;
SELECT count(*) FROM pg_locks WHERE locktype = 'advisory';   -- 0

-- Step 6: two-int form (namespace, id), and release everything
SELECT pg_try_advisory_lock(1, 2);                -- true
SELECT pg_advisory_unlock_all();

-- ============================================
-- EXPECTED OUTPUT (real, PGlite = PostgreSQL 18, single connection)
-- ============================================

-- got_lock true | again true
-- pg_locks: advisory | classid 0 | objid 42 | ExclusiveLock | granted t
-- unlock: true, true, false
-- xact lock: 1 row inside tx, 0 after COMMIT
-- NOT VERIFIED: the "other session gets false" behaviour. PGlite has one connection,
-- so cross-session contention was not run. It is documented PostgreSQL behaviour.
```

---

## 🔍 Why This Works (3 lines max)
The lock manager treats the number as a lockable resource, so only one session can hold it exclusively; a second session's `try` returns false instead of blocking. Session-level locks live until unlock or disconnect (so a crashed worker releases automatically); xact-level locks vanish at transaction end.
हिंदी: Lock manager number को resource मानता है; session lock disconnect पर अपने आप छूट जाता है, xact lock transaction खत्म होने पर।

---

## ⚡ Alternative Solution

```sql
-- Blocking version: waits until available
SELECT pg_advisory_lock(42);
-- ... critical work ...
SELECT pg_advisory_unlock(42);

-- Per-entity lock, e.g. serialize payouts for one merchant (xact-level, safest):
BEGIN;
SELECT pg_advisory_xact_lock(hashtext('merchant:' || 9001));
-- ... do work ...
COMMIT;

-- MySQL equivalent: named locks
--   SELECT GET_LOCK('nightly-report', 0);   -- 1 = got it, 0 = busy (timeout 0 = don't wait)
--   SELECT RELEASE_LOCK('nightly-report');
--   SELECT IS_FREE_LOCK('nightly-report');
-- (MySQL 5.7+ allows multiple GET_LOCKs per session; names are strings, max 64 chars. Not run here.)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Session-level lock through a transaction-pooling PgBouncer
SELECT pg_try_advisory_lock(42);   -- may run on connection A
SELECT pg_advisory_unlock(42);     -- may run on connection B -> returns false, lock leaked on A!
-- ✅ Use pg_try_advisory_xact_lock inside one transaction when behind a pooler

-- ❌ Forgetting that acquisitions stack: lock twice, unlock once = still held
-- ❌ Using colliding keys across features -> use the two-int form (feature_id, entity_id)
```

---

## 🎯 Interview Tip (1 line)
Say: "For leader election or single-runner jobs I use pg_try_advisory_lock so workers skip instead of queueing; behind a transaction pooler I switch to xact-level locks, and I prefer them anyway because they cannot leak."

---

## 🔗 Related Questions
→ Q017 / Q242 (SELECT FOR UPDATE) | Q185 (LISTEN/NOTIFY) | Q196 (pg_stat_activity — find who holds locks)
