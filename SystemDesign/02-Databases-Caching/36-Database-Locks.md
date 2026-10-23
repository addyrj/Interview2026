# 36. Database Locks
# हिंदी में: Database Locks — एक समय पर एक ही transaction किसी row/table को बदल सके, इसके लिए लगाया गया "ताला"

---

## 🔵 Simple Definition (English)
A **lock** is a mechanism the database uses to control **concurrent access** to data. A transaction acquires a lock on a row, page or table; other transactions that need a **conflicting** lock must **wait** until it's released (at COMMIT/ROLLBACK).
Main types: **shared (read) locks**, **exclusive (write) locks**, at **row** or **table** level, plus advisory locks.

## 🔵 सरल परिभाषा (Hindi)
Lock एक ताला है — जब एक transaction किसी row को बदल रहा है, तो दूसरा उसी row को बदलने के लिए इंतज़ार करता है।
Shared lock = कई लोग पढ़ सकते हैं; Exclusive lock = सिर्फ़ एक बदल सकता है। ताला COMMIT/ROLLBACK पर खुलता है।

---

## 🔴 Problem it Solves
Without locks, two transactions updating the same row at once would **overwrite each other** (lost updates) or create invalid states (double-spending a wallet, two bookings for one seat).
Locks **serialize conflicting operations** while letting non-conflicting ones run in parallel.

But locks also cause real production problems: **blocking, deadlocks, and migrations that freeze the whole app**, so you must understand them.

## 🔴 यह क्यों बना? (Hindi)
बिना ताले के दो transactions एक ही row को एक साथ बदलें तो एक का काम मिट जाता है — wallet से दो बार पैसे निकल सकते हैं।
Lock टकराने वाले कामों को एक-एक करके चलाता है। पर ग़लत इस्तेमाल से blocking, deadlock और migration के समय पूरा ऐप रुक सकता है।

---

## 🟢 How it Works — Step by Step

### Shared vs Exclusive

```
                     Requested →   Shared (S)     Exclusive (X)
Held ↓
Shared (S)                         ✅ compatible   ❌ wait
Exclusive (X)                      ❌ wait         ❌ wait

S lock: "I'm reading, don't change it"     (SELECT ... FOR SHARE)
X lock: "I'm changing it, nobody else write" (UPDATE, DELETE, SELECT ... FOR UPDATE)

In MVCC databases (Postgres/MySQL), plain SELECT takes NO row lock → readers never block writers.
```

### Row-level locking timeline

```
Time  T1                                   T2
 1    BEGIN
 2    UPDATE wallets SET bal=bal-100
      WHERE user_id=1;   (X lock row 1)
 3                                         BEGIN
 4                                         UPDATE wallets SET bal=bal-50
                                           WHERE user_id=1;   ⏳ WAITS for row 1
 5    COMMIT  (lock released)
 6                                         → proceeds with the NEW balance ✅
 7                                         COMMIT
```

### Lock granularity

```
Row lock     → finest, best concurrency (Postgres, InnoDB default for DML)
Page lock    → some engines (SQL Server)
Table lock   → DDL: ALTER TABLE, TRUNCATE, VACUUM FULL, some index builds
               LOCK TABLE explicit
Advisory     → app-defined locks on any number (pg_advisory_lock(42)) — like a mutex
Gap / Next-key (MySQL InnoDB) → locks ranges between index values to prevent phantoms
```

### Explicit row locks in SQL

```sql
SELECT ... FOR UPDATE;               -- exclusive: I will update these rows
SELECT ... FOR NO KEY UPDATE;        -- weaker (PG): doesn't block FK inserts referencing row
SELECT ... FOR SHARE;                -- shared: nobody may update/delete while I hold it
SELECT ... FOR UPDATE NOWAIT;        -- fail immediately instead of waiting
SELECT ... FOR UPDATE SKIP LOCKED;   -- skip rows others locked → JOB QUEUE pattern ⭐
```

### SKIP LOCKED — Postgres as a job queue

```
jobs table: id | status | payload
Worker A: SELECT * FROM jobs WHERE status='pending' ORDER BY id LIMIT 10 FOR UPDATE SKIP LOCKED;
          → gets jobs 1–10
Worker B: same query → skips locked 1–10 → gets 11–20
No double processing, no blocking. (Used by pg-boss, Graphile Worker, Oban, Que)
```

### Deadlock

```
T1: locks row A ──────────────► wants row B ⏳
T2: locks row B ──────────────► wants row A ⏳
        ↑                              │
        └──────── cycle ───────────────┘
DB detects (Postgres deadlock_timeout = 1s) → aborts one: ERROR 40P01 deadlock detected
Prevention:
  - Lock rows in a CONSISTENT ORDER (e.g. ORDER BY id ... FOR UPDATE)
  - Keep transactions short
  - Index foreign keys (unindexed FK → broader locks)
  - Retry the aborted transaction
```

### The migration trap (lock queue)

```
ALTER TABLE orders ADD COLUMN note TEXT DEFAULT 'x';   ← needs ACCESS EXCLUSIVE lock (briefly)

Long-running SELECT (report, 5 min) holds a weak lock on orders
  → ALTER waits for it
    → EVERY new query on orders queues BEHIND the waiting ALTER  ❌ app frozen for 5 min

Safe migrations:
  SET lock_timeout = '3s';        -- give up instead of freezing the app; retry later
  SET statement_timeout = '15s';
  CREATE INDEX CONCURRENTLY ...   -- no write block
  Add column nullable / with constant default (PG 11+ instant), backfill in batches
  Add constraints NOT VALID, then VALIDATE CONSTRAINT separately
```

### Optimistic vs Pessimistic locking

```
Pessimistic: lock first (FOR UPDATE), then work. Good for high contention, short operations.
Optimistic:  no lock; on write check a version → 0 rows updated = someone changed it → retry/409.
             UPDATE docs SET body=$1, version=version+1 WHERE id=$2 AND version=$3;
             Good for low contention, long user edits (forms, docs), HTTP ETag/If-Match.
```

## 🟢 कैसे काम करता है? (Hindi)
1. UPDATE/DELETE अपने आप उस row पर exclusive lock लगाते हैं; दूसरा उसी row को बदलना चाहे तो इंतज़ार करता है।
2. Postgres/MySQL में साधारण SELECT ताला नहीं लगाता (MVCC) — पढ़ने वाले लिखने वालों को नहीं रोकते।
3. `FOR UPDATE` से पहले ही row को ताला लगा सकते हो; `SKIP LOCKED` से कई workers बिना टकराए jobs उठाते हैं।
4. Deadlock: दो transactions एक-दूसरे का ताला माँगते हैं — DB एक को abort करता है; हमेशा एक ही क्रम में lock लो।
5. ALTER TABLE पूरी टेबल पर ताला लगाता है — `lock_timeout` लगाओ और migrations सुरक्षित तरीके से करो।

---

## 🟡 Real World Example

**Migration outages** — many companies (GitLab, Braintree, and lots of startups) have had outages where a simple `ALTER TABLE` on a hot table waited behind a long query and then blocked all traffic for minutes. That's why tools like `strong_migrations` (Rails), `squawk` (Postgres lint) and gh-ost (MySQL, from GitHub) exist.

**Ticket booking (IRCTC/BookMyShow)** — seats are held with short locks or reservations. Without proper locking, two users would get the same berth. Seat holds also expire so locks aren't held forever.

**Job queues on Postgres** — companies use `FOR UPDATE SKIP LOCKED` queues (pg-boss, Graphile Worker, Oban in Elixir) instead of running a separate RabbitMQ, which keeps the stack simple and gives jobs transactional consistency with business data.

## 🟡 Real Example Hindi में
कई कंपनियों में एक साधारण `ALTER TABLE` किसी लंबी query के पीछे रुका और फिर पूरे ऐप की queries उसके पीछे लाइन में लग गईं — मिनटों का outage। इसलिए migration में `lock_timeout` ज़रूरी है।
कई टीमें अलग queue सर्वर की जगह Postgres में `SKIP LOCKED` से job queue बनाती हैं — सिस्टम सरल रहता है।

---

## 🟠 My Stack Example

### Wallet debit with pessimistic lock (Node)
```js
await withTx(async (tx) => {
  const { rows: [w] } = await tx.query(
    'SELECT balance FROM wallets WHERE user_id = $1 FOR UPDATE', [uid]);   // lock row
  if (w.balance < amount) throw new AppError(422, 'INSUFFICIENT_BALANCE');
  await tx.query('UPDATE wallets SET balance = balance - $1 WHERE user_id = $2', [amount, uid]);
  await tx.query('INSERT INTO ledger(user_id, amount, type) VALUES ($1, $2, $3)', [uid, -amount, 'DEBIT']);
});
```

### Transfer without deadlocks: lock in consistent order
```js
const [first, second] = [fromId, toId].sort((a, b) => a - b);
await tx.query('SELECT 1 FROM wallets WHERE user_id = ANY($1) ORDER BY user_id FOR UPDATE', [[first, second]]);
```

### Postgres job queue worker (SKIP LOCKED)
```js
async function workLoop() {
  while (true) {
    const jobs = await withTx(async (tx) => {
      const { rows } = await tx.query(`
        UPDATE jobs SET status = 'running', started_at = now()
        WHERE id IN (
          SELECT id FROM jobs WHERE status = 'pending' AND run_at <= now()
          ORDER BY id LIMIT 10 FOR UPDATE SKIP LOCKED)
        RETURNING *`);
      return rows;
    });
    if (!jobs.length) { await sleep(1000); continue; }
    await Promise.all(jobs.map(processJob));
  }
}
```

### Advisory lock — run a cron only once across instances
```js
const { rows: [{ ok }] } = await pool.query('SELECT pg_try_advisory_lock(424242) AS ok');
if (ok) {
  try { await runDailySettlement(); }
  finally { await pool.query('SELECT pg_advisory_unlock(424242)'); }
}
```
(Redis alternative: `SET lock:daily NX EX 600`, see Topic 88 Distributed Locks.)

### Optimistic locking with Prisma (document editing)
```js
const res = await prisma.document.updateMany({
  where: { id, version: clientVersion },
  data: { body, version: { increment: 1 } },
});
if (res.count === 0) throw new AppError(409, 'Document was changed by someone else. Reload.');
```
Same idea over HTTP: `ETag` + `If-Match` → `412 Precondition Failed`.

### FastAPI + SQLAlchemy
```python
stmt = select(Wallet).where(Wallet.user_id == uid).with_for_update()   # FOR UPDATE
wallet = (await session.execute(stmt)).scalar_one()
```

### Safe migration settings
```sql
SET lock_timeout = '3s';
SET statement_timeout = '30s';
ALTER TABLE orders ADD COLUMN note TEXT;                         -- nullable: instant
ALTER TABLE orders ADD CONSTRAINT note_len CHECK (length(note) < 500) NOT VALID;
ALTER TABLE orders VALIDATE CONSTRAINT note_len;                 -- doesn't block writes
```

### See who is blocking whom
```sql
SELECT pid, pg_blocking_pids(pid) AS blocked_by, state, wait_event_type, left(query, 80)
FROM pg_stat_activity WHERE cardinality(pg_blocking_pids(pid)) > 0;
-- kill a stuck blocker:  SELECT pg_terminate_backend(<pid>);
```

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between shared and exclusive locks?**
A1: A shared lock allows other transactions to also take shared locks (read) but blocks exclusive ones (write). An exclusive lock blocks both. UPDATE and DELETE take exclusive row locks automatically, and `SELECT ... FOR UPDATE` takes them explicitly. In MVCC databases, plain SELECTs read a snapshot without locks, so reads and writes don't block each other.

**Q2: What is a deadlock and how do you prevent it?**
A2: A cycle of transactions each waiting for a lock held by another. The DB detects it and aborts one (Postgres error 40P01). Prevent it by acquiring locks in a consistent global order (sort IDs), keeping transactions short, avoiding user interaction or network calls inside them, and indexing foreign keys. Handle it with automatic retries with backoff.

**Q3: Optimistic vs pessimistic locking — when to use which?**
A3: Pessimistic (`FOR UPDATE`) locks before modifying, which is good for high-contention, short critical sections like wallet debits or stock decrements, where conflicts are likely and retries are expensive. Optimistic uses no lock and checks a version or timestamp at write time, then retries or reports a conflict. It's good for low contention and long user think-time, like editing a profile or document in a form, and maps naturally to HTTP ETag/If-Match.

**Q4: How can a schema migration take down production, and how do you avoid it?**
A4: DDL like ALTER TABLE needs a strong table lock. If a long query is running, the ALTER waits, and every new query on the table queues behind the waiting ALTER, so the table is effectively frozen. Avoid it by setting `lock_timeout` (fail fast and retry), using non-blocking operations (`CREATE INDEX CONCURRENTLY`, nullable columns or constant defaults, `NOT VALID` constraints then VALIDATE), backfilling in small batches, running during low traffic, and linting migrations with tools like squawk or strong_migrations.

**Q5: How would you build a reliable job queue on PostgreSQL?**
A5: A jobs table with status and run_at columns. Workers claim jobs with `SELECT ... FOR UPDATE SKIP LOCKED LIMIT n` inside a transaction (or an UPDATE ... RETURNING with that subquery), so each job is claimed by exactly one worker without blocking others. Add retries with attempt counts and backoff, a visibility timeout for stuck "running" jobs, and an index on (status, run_at). You get transactional enqueue with business data (same commit). For very high throughput, use a dedicated broker.

---

## 🔷 Trade-offs
✅ Locks: guarantee correctness for concurrent writes; SKIP LOCKED enables simple queues.
❌ Locks: blocking reduces throughput; deadlocks; long transactions + DDL can freeze tables.
✅ Optimistic: no blocking, scales for low contention.
❌ Optimistic: retries/conflict UX under high contention.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lock | Controls concurrent access | एक साथ पहुँच पर ताला |
| Shared lock | Many readers allowed | कई पढ़ने वाले |
| Exclusive lock | One writer only | सिर्फ़ एक लिखने वाला |
| Row / Table lock | Granularity of lock | row / पूरी टेबल पर ताला |
| FOR UPDATE | Explicit row write lock | पहले से row पर ताला |
| SKIP LOCKED | Skip rows locked by others | ताले वाली rows छोड़ दो |
| Deadlock | Circular wait | गोल-गोल इंतज़ार |
| Advisory lock | App-defined lock (mutex) | ऐप का अपना ताला |
| lock_timeout | Max wait for a lock | ताले का अधिकतम इंतज़ार |

---

## ⚡ 3-Line Summary
**English:**
1. Locks serialize conflicting access: shared (read) vs exclusive (write), row vs table; MVCC means plain reads don't lock.
2. Use FOR UPDATE for read-then-write, SKIP LOCKED for queues, advisory locks for single-run jobs, optimistic versions for edits.
3. Avoid deadlocks (consistent order, short txns) and lock-queue outages (lock_timeout, concurrent/safe migrations).

**Hindi:**
1. Lock टकराने वाले कामों को क्रम में चलाता है: shared (पढ़ना) और exclusive (लिखना); साधारण SELECT ताला नहीं लगाता।
2. FOR UPDATE, SKIP LOCKED (queue), advisory lock (एक बार चलने वाला cron), optimistic version (edit)।
3. Deadlock से बचो (एक क्रम, छोटे txn) और migration में lock_timeout लगाओ।

---

## ➡️ Next Topic Suggestion
**37. MVCC** — We kept saying "plain reads don't take locks." Next: Multi-Version Concurrency Control, how Postgres keeps multiple versions of rows, snapshots, VACUUM, and table bloat.
