---

# Q140. Transaction Isolation in Node.js (Sequelize / Prisma / Knex)
# Category: Transactions & ACID
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — Knex 3.3.0 and Sequelize 6.37.8 run against MySQL 9.1.0; Prisma code and all PostgreSQL-driver code NOT run

---

## ❓ Question
How do you run a money transfer in a Node.js app so it is atomic, uses a chosen isolation level, rolls back on any thrown error, and uses row locks correctly? Show it with Knex, Sequelize and Prisma.

---

## 💡 Quick Concept (2 lines only)
Every query inside the transaction callback must use the transaction handle (`trx` / `{ transaction: t }` / `tx`) so it runs on the same connection; throwing inside the callback triggers ROLLBACK, returning commits. Isolation level is passed as an option and sent as SET TRANSACTION ISOLATION LEVEL before BEGIN.
हिंदी: Transaction के अंदर हर query उसी `trx` handle से चलाओ ताकि एक ही connection रहे; error throw होते ही ROLLBACK और सही return पर COMMIT।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE accounts (
  id      INT PRIMARY KEY,
  balance DECIMAL(10,2)          -- PgSQL: NUMERIC(10,2)
);

INSERT INTO accounts VALUES (1, 1000.00), (2, 500.00);

-- ============================================
-- SOLUTION 1: Knex (JavaScript; run on MySQL via mysql2)
-- ============================================

-- const knex = require('knex')({ client: 'mysql2', connection: {...} });  // PgSQL: client 'pg'
--
-- async function transfer(from, to, amt, failAfterDebit) {
--   return knex.transaction(async (trx) => {
--     const [row] = await trx('accounts').where({ id: from }).forUpdate();   // SELECT ... FOR UPDATE
--     if (Number(row.balance) < amt) throw new Error('insufficient funds');
--     await trx('accounts').where({ id: from }).decrement('balance', amt);
--     if (failAfterDebit) throw new Error('simulated failure after debit');
--     await trx('accounts').where({ id: to }).increment('balance', amt);
--   }, { isolationLevel: 'serializable' });                                  // 2nd arg = config
-- }

-- ============================================
-- SOLUTION 2: Sequelize
-- ============================================

-- await sequelize.transaction(
--   { isolationLevel: Transaction.ISOLATION_LEVELS.READ_COMMITTED },
--   async (t) => {
--     await Account.findByPk(1, { transaction: t, lock: t.LOCK.UPDATE });   // FOR UPDATE
--     await Account.decrement('balance', { by: 100, where: { id: 1 }, transaction: t });
--   }
-- );

-- ============================================
-- SOLUTION 3: Prisma (NOT RUN here)
-- ============================================

-- await prisma.$transaction(async (tx) => {
--   const [acc] = await tx.$queryRaw`SELECT * FROM accounts WHERE id = 1 FOR UPDATE`;
--   await tx.accounts.update({ where: { id: 1 }, data: { balance: { decrement: 100 } } });
-- }, { isolationLevel: Prisma.TransactionIsolationLevel.Serializable, maxWait: 5000, timeout: 10000 });

-- ============================================
-- EXPECTED OUTPUT (real Knex run on MySQL 9.1.0; isolation read from information_schema.innodb_trx)
-- ============================================

-- transfer(1,2,100,false)   -> isolation in trx: SERIALIZABLE
--                              accounts: (1, 900.00), (2, 600.00)       committed
-- transfer(1,2,100,true)    -> caught: simulated failure after debit
--                              accounts: (1, 900.00), (2, 600.00)       debit rolled back
-- transfer(1,2,99999,false) -> caught: insufficient funds                nothing changed
-- Sequelize READ_COMMITTED  -> isolation in trx: READ COMMITTED
--                              throw new Error('boom') -> rolled back, balance unchanged

-- Equivalent raw SQL the drivers send:
-- SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;   -- applies to the NEXT transaction only
-- BEGIN;
-- SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- UPDATE accounts SET balance = balance + 100 WHERE id = 2;
-- COMMIT;
```

---

## 🔍 Why This Works (3 lines max)
The library checks out one pooled connection, issues BEGIN, runs your callback, then COMMIT on success or ROLLBACK on a thrown error and returns the connection to the pool. The isolation option is sent as a one-shot SET TRANSACTION before BEGIN, so it never leaks to the next user of the connection.
हिंदी: Library एक connection लेकर BEGIN चलाती है, callback सफल तो COMMIT, error तो ROLLBACK; isolation सिर्फ उसी transaction पर लागू होता है।

---

## ⚡ Alternative Solution

```sql
-- Atomic single statement - often no explicit transaction/lock needed:
UPDATE accounts SET balance = balance - 100 WHERE id = 1 AND balance >= 100;
-- check affectedRows = 1 in the app (0 = insufficient funds). Works at any isolation level.

-- Retry on serialization failure / deadlock (REQUIRED at SERIALIZABLE and REPEATABLE READ in PgSQL):
--   PgSQL error code 40001 (serialization_failure) or 40P01 (deadlock_detected)
--   MySQL error 1213 ER_LOCK_DEADLOCK, 1205 lock wait timeout
-- async function withRetry(fn, n = 3) {
--   for (let i = 0; i < n; i++) {
--     try { return await fn(); }
--     catch (e) { if (!['40001','40P01','ER_LOCK_DEADLOCK'].includes(e.code) || i === n - 1) throw e; }
--   }
-- }

-- Prisma interactive vs batch:  prisma.$transaction([op1, op2])  = batch, no logic between ops.
-- Default isolation: MySQL = REPEATABLE READ, PostgreSQL = READ COMMITTED (see Q126).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: using the global knex / sequelize / prisma inside the callback
--    await knex('accounts').where({id: from}).decrement('balance', amt);   // different connection!
--    -> not part of the transaction, will NOT roll back.
-- ✅ Always use trx / { transaction: t } / tx.

-- ❌ Wrong: SET TRANSACTION ISOLATION LEVEL after BEGIN (we hit this real MySQL error):
-- ERROR 1568: Transaction characteristics can't be changed while a transaction is in progress
-- ✅ Pass isolationLevel as an option so the library issues it BEFORE BEGIN.

-- ❌ Wrong: reading @@transaction_isolation to verify a one-shot level - it shows the SESSION
--    level, not the next transaction's (we saw REPEATABLE-READ even though SERIALIZABLE was active).
-- ✅ Verify with information_schema.innodb_trx.trx_isolation_level (MySQL) or
--    SHOW transaction_isolation inside the txn (PgSQL).

-- ❌ Wrong: slow HTTP calls inside the callback (holds locks + a pool connection) - see Q135.
```

---

## 🎯 Interview Tip (1 line)
Say: "I pass the transaction handle everywhere, pick the weakest isolation that is correct, prefer atomic UPDATE ... WHERE balance >= x or SELECT FOR UPDATE over SERIALIZABLE, and wrap in retry logic for 40001/deadlock errors."

---

## 🔗 Related Questions
→ Q121 (Isolation levels) | Q126 (Default isolation MySQL vs PgSQL) | Q127 (Optimistic vs pessimistic locking) | Q133 (SAVEPOINT)
