---

# Q138. Two-Phase Commit — Distributed Transactions
# Category: Transactions & ACID
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL XA | PostgreSQL PREPARE TRANSACTION) — MySQL XA run on 9.1.0; PgSQL PREPARE TRANSACTION is DISABLED in PGlite (max_prepared_transactions = 0), so the PgSQL block is NOT run (real error captured)

---

## ❓ Question
A transfer must debit a wallet in database A and credit an account in database B atomically. How does two-phase commit (2PC) achieve this, how do you do it in MySQL and PostgreSQL, and why do most microservice systems avoid it?

---

## 💡 Quick Concept (2 lines only)
Phase 1 (prepare): every participant does the work, makes it durable and promises it can commit. Phase 2 (commit/rollback): a coordinator tells all to commit only if all voted yes.
हिंदी: Phase 1 में सब participants तैयार होकर वादा करते हैं, Phase 2 में coordinator सबको एक साथ commit या rollback का आदेश देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE wallet (
  user_id INT PRIMARY KEY,
  balance DECIMAL(10,2)          -- PgSQL: NUMERIC(10,2)
);

INSERT INTO wallet VALUES (1, 1000.00);

-- ============================================
-- SOLUTION (MySQL XA - one branch shown; the coordinator would run the same on DB B)
-- ============================================

-- Step 1: start a branch with a global transaction id (xid)
XA START 'transfer_77';
UPDATE wallet SET balance = balance - 250 WHERE user_id = 1;
-- Step 2: end the branch, then PREPARE (vote yes: changes are now durable in the redo log)
XA END 'transfer_77';
XA PREPARE 'transfer_77';

-- Step 3: the prepared branch survives disconnects/crashes; list it
XA RECOVER;

-- Step 4a: coordinator decided ROLLBACK (e.g. DB B said no)
XA ROLLBACK 'transfer_77';
-- Step 4b: or COMMIT when all voted yes  ->  XA COMMIT 'transfer_78';

-- ============================================
-- EXPECTED OUTPUT (real MySQL 9.1.0)
-- ============================================

-- XA RECOVER:
-- formatID | gtrid_length | bqual_length | data
-- ---------+--------------+--------------+------------
-- 1        | 11           | 0            | transfer_77
--
-- wallet after XA ROLLBACK 'transfer_77'  -> balance 1000.00 (unchanged)
-- wallet after a second branch: XA START 'transfer_78'; UPDATE (-250); XA END; XA PREPARE; XA COMMIT 'transfer_78'
--                                         -> balance 750.00
-- XA RECOVER afterwards -> empty set

-- ============================================
-- PostgreSQL (NOT RUN - PGlite has prepared transactions disabled)
-- ============================================
-- Real PGlite response:  SHOW max_prepared_transactions -> 0
--                        PREPARE TRANSACTION 'transfer_77' -> ERROR: prepared transactions are disabled
-- On a real server set max_prepared_transactions > 0 in postgresql.conf (restart), then:

BEGIN;
UPDATE wallet SET balance = balance - 250 WHERE user_id = 1;
PREPARE TRANSACTION 'transfer_77';        -- phase 1: durable, locks kept, session detached

SELECT gid, prepared, owner, database FROM pg_prepared_xacts;   -- list in-doubt txns

COMMIT PREPARED 'transfer_77';            -- phase 2 (from ANY session)
-- or: ROLLBACK PREPARED 'transfer_77';
```

---

## 🔍 Why This Works (3 lines max)
After PREPARE a participant can no longer unilaterally abort; it keeps its locks until the coordinator decides, so either everyone commits or everyone rolls back. The price is blocking: if the coordinator dies, prepared transactions hold locks until someone resolves them.
हिंदी: PREPARE के बाद participant अपने मन से abort नहीं कर सकता; coordinator मर जाए तो locks तब तक रुके रहते हैं जब तक कोई फ़ैसला न करे।

---

## ⚡ Alternative Solution

```sql
-- Most systems avoid 2PC across services. Alternatives (design, not run):

-- 1) Saga: local transactions + compensating actions
--    debit(A) -> credit(B) -> on failure: refund(A)  (eventual consistency)

-- 2) Transactional outbox: write business row + event row in ONE local transaction,
--    a relay publishes the event to Kafka/SQS; consumer is idempotent.
CREATE TABLE outbox_events (
  id         BIGINT PRIMARY KEY AUTO_INCREMENT,   -- PgSQL: BIGSERIAL
  aggregate  VARCHAR(50),
  payload    JSON,                                -- PgSQL: JSONB
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  published  BOOLEAN DEFAULT FALSE
);

-- 3) Same-database trick: if both tables live in ONE database, a normal
--    BEGIN ... COMMIT is enough - no 2PC needed.

-- Operational: always monitor leftover prepared transactions
-- PgSQL : SELECT * FROM pg_prepared_xacts;   (they block VACUUM and hold locks!)
-- MySQL : XA RECOVER;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: leaving a prepared transaction forever (app crashed between phases)
XA PREPARE 'transfer_77';      -- never committed or rolled back
-- Row locks stay held, replicas/backups may complain, and in PgSQL it blocks VACUUM
-- -> table bloat + wraparound risk.
-- ✅ Run a recovery job: list XA RECOVER / pg_prepared_xacts and COMMIT or ROLLBACK
--    according to the coordinator's decision log.

-- ❌ Wrong: setting max_prepared_transactions = 0 (PgSQL default) and expecting PREPARE to work
-- (we hit exactly this: "prepared transactions are disabled").

-- ❌ Wrong: thinking 2PC removes all failure modes - the coordinator is a single point of failure
--    and the blocking window is the real cost; latency = slowest participant x 2 round trips.
```

---

## 🎯 Interview Tip (1 line)
Say: "2PC gives atomicity across resources but blocks on coordinator failure and adds latency, so for microservices I prefer sagas or the transactional outbox with idempotent consumers, and use XA / PREPARE TRANSACTION only where strong consistency across two databases is mandatory."

---

## 🔗 Related Questions
→ Q139 (WAL) | Q135 (Long-running transactions) | Q129 (Deadlock) | Q156 (Database per service)
