# 35. Isolation Levels
# हिंदी में: Isolation Levels — एक साथ चल रहे transactions एक-दूसरे के बदलाव कितना देख सकते हैं, इसके अलग-अलग स्तर

---

## 🔵 Simple Definition (English)
**Isolation levels** define how much concurrent transactions are protected from each other. Higher isolation = fewer anomalies but less concurrency and more retries. The SQL standard defines four:
1. **Read Uncommitted** — can see other transactions' uncommitted changes (dirty reads).
2. **Read Committed** — sees only committed data, but each statement gets a fresh view (**Postgres default**).
3. **Repeatable Read** — the same snapshot for the whole transaction (**MySQL InnoDB default**).
4. **Serializable** — the result equals some one-at-a-time order of transactions (strongest).

## 🔵 सरल परिभाषा (Hindi)
Isolation level तय करता है कि एक transaction दूसरे के बदलाव कब और कितने देख सकता है।
जितना ऊँचा level, उतनी कम गड़बड़ी, पर उतना ही धीमा और ज़्यादा retry। Postgres का default Read Committed है, MySQL का Repeatable Read।

---

## 🔴 Problem it Solves
Perfect isolation (running transactions one by one) would be **very slow**. Databases run transactions in parallel, which can cause **anomalies**:
- Showing a balance that was never committed.
- A report whose numbers don't add up.
- Two doctors both going off-call because each saw the other still on-call.
- Overselling stock.

Isolation levels let you **choose the right trade-off per use case**: fast reads for a feed, strict correctness for money.

## 🔴 यह क्यों बना? (Hindi)
सारे transactions एक-एक करके चलाना बहुत धीमा है, और साथ-साथ चलाने से गड़बड़ियाँ (anomalies) होती हैं — ग़लत balance, न मिलने वाली रिपोर्ट, oversell।
Isolation levels से हर काम के हिसाब से संतुलन चुन सकते हो: feed के लिए तेज़, पैसे के लिए सख़्त।

---

## 🟢 How it Works — Step by Step

### The anomalies

```
1. Dirty Read — read data another txn hasn't committed (and may roll back)
   T1: UPDATE acc SET bal = 0 WHERE id=1;   (not committed)
   T2: SELECT bal FROM acc WHERE id=1;  → 0   ❌ (T1 then ROLLBACKs; 0 never existed)

2. Non-Repeatable Read — same row read twice, different values
   T1: SELECT bal → 100
   T2: UPDATE bal = 50; COMMIT;
   T1: SELECT bal → 50     ❌ (inside one txn)

3. Phantom Read — same query returns different SET of rows
   T1: SELECT COUNT(*) FROM orders WHERE user=1 → 3
   T2: INSERT order for user 1; COMMIT;
   T1: SELECT COUNT(*) ... → 4   ❌

4. Lost Update — two read-modify-write cycles; one overwrites the other
   T1, T2 read stock=10; T1 writes 9; T2 writes 9  → should be 8 ❌

5. Write Skew — both read overlapping data, each writes a DIFFERENT row, invariant breaks
   Rule: at least 1 doctor on call. Alice & Bob both on call.
   T1 (Alice): count on-call = 2 → OK, set Alice off
   T2 (Bob):   count on-call = 2 → OK, set Bob off
   Result: 0 doctors on call ❌
```

### Which level prevents what (standard + real behaviour)

```
┌──────────────────┬───────┬──────────────┬─────────┬───────────┬────────────┐
│ Level            │ Dirty │ Non-repeat.  │ Phantom │ Lost upd. │ Write skew │
├──────────────────┼───────┼──────────────┼─────────┼───────────┼────────────┤
│ Read Uncommitted │ ⚠️*    │ ❌ possible  │ ❌      │ ❌        │ ❌         │
│ Read Committed   │ ✅    │ ❌ possible  │ ❌      │ ❌        │ ❌         │
│ Repeatable Read  │ ✅    │ ✅           │ ✅ PG** │ ✅ PG***  │ ❌         │
│ Serializable     │ ✅    │ ✅           │ ✅      │ ✅        │ ✅         │
└──────────────────┴───────┴──────────────┴─────────┴───────────┴────────────┘
*   Postgres treats Read Uncommitted as Read Committed (never dirty reads).
**  Postgres Repeatable Read = Snapshot Isolation → no phantoms. MySQL uses gap/next-key locks
    for locking reads to prevent phantoms.
*** Postgres RR aborts the 2nd conflicting updater ("could not serialize access") → app retries.
    MySQL RR does NOT prevent lost update for plain read-then-write; use SELECT ... FOR UPDATE.
```

### How it's implemented

```
Read Committed (Postgres):   each STATEMENT takes a new snapshot of committed data.
Repeatable Read (Postgres):  ONE snapshot at the first statement, used for the whole txn
                             (= Snapshot Isolation). Concurrent update of same row → abort.
Serializable (Postgres SSI): snapshot + tracks read/write dependencies; if a dangerous cycle
                             appears, aborts one txn with SQLSTATE 40001 → RETRY.
MySQL InnoDB:                MVCC consistent reads + next-key locks on locking reads;
                             Serializable turns plain SELECTs into locking reads.
```

### Choosing a level

```
Default (Read Committed) + explicit techniques covers most apps:
  - atomic updates:  UPDATE ... SET stock = stock - 1 WHERE stock > 0
  - row locks:       SELECT ... FOR UPDATE
  - unique constraints / exclusion constraints (prevent double booking)
  - optimistic locking (version column)

Use Repeatable Read for:   consistent multi-query reports/exports inside one transaction
Use Serializable for:      complex invariants across rows (write skew risk): on-call schedules,
                           seat/slot allocation across rows, financial rules — with retry loop
```

## 🟢 कैसे काम करता है? (Hindi)
1. Read Committed (Postgres default): हर query को सिर्फ़ commit हो चुका डेटा दिखता है, पर दो queries के बीच डेटा बदल सकता है।
2. Repeatable Read: पूरे transaction में एक ही snapshot — वही row दोबारा पढ़ो तो वही value।
3. Serializable: नतीजा ऐसा जैसे transactions एक-एक करके चले; टकराव हुआ तो एक abort होगा — retry करना पड़ता है।
4. Write skew (दो डॉक्टर दोनों off-call) सिर्फ़ Serializable या explicit lock से रुकता है।
5. ज़्यादातर ऐप में Read Committed + atomic UPDATE / FOR UPDATE / unique constraint काफ़ी हैं।

---

## 🟡 Real World Example

**Hotel / meeting-room booking (double booking = write skew)** — two users check "is room 101 free 3–4 pm?", both see free, both insert bookings in different rows. Read Committed allows it. Fixes: a Postgres **exclusion constraint** on time ranges, SERIALIZABLE with retries, or locking the room row with `FOR UPDATE`.

**Banking reports** — end-of-day reports run in REPEATABLE READ (or from a replica snapshot) so all balances are read as of one moment, even while transfers keep happening.

**Bitcoin exchange exploits** — several crypto exchanges (e.g. Flexcoin in 2014) were drained because of race conditions in withdrawal code: concurrent requests passed the balance check before any of them deducted. Proper isolation or atomic updates would have prevented it.

## 🟡 Real Example Hindi में
होटल बुकिंग में दो लोग एक साथ देखते हैं "कमरा खाली है", दोनों बुक कर देते हैं — Read Committed में यह हो सकता है; exclusion constraint, Serializable या FOR UPDATE से रोकते हैं।
कुछ crypto exchanges में एक साथ कई withdrawal requests ने balance check पार कर लिया और पैसे निकल गए — race condition का असली नुक़सान।

---

## 🟠 My Stack Example

### Prevent double booking with an exclusion constraint (Postgres — best)
```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE TABLE bookings (
  id BIGSERIAL PRIMARY KEY,
  room_id BIGINT NOT NULL,
  during TSTZRANGE NOT NULL,
  EXCLUDE USING gist (room_id WITH =, during WITH &&)   -- no overlapping ranges per room
);
-- Concurrent overlapping inserts → one fails with 23P01 (exclusion_violation) → show "slot taken"
```

### Serializable with retry (Node)
```js
async function serializable(fn, retries = 5) {
  for (let i = 0; ; i++) {
    const c = await pool.connect();
    try {
      await c.query('BEGIN ISOLATION LEVEL SERIALIZABLE');
      const r = await fn(c);
      await c.query('COMMIT');
      return r;
    } catch (e) {
      await c.query('ROLLBACK').catch(() => {});
      if (e.code === '40001' && i < retries) { await sleep(10 * 2 ** i + Math.random() * 10); continue; }
      throw e;
    } finally { c.release(); }
  }
}

// Doctor on-call (write skew safe)
await serializable(async (tx) => {
  const { rows: [{ n }] } = await tx.query(
    'SELECT COUNT(*)::int n FROM doctors WHERE shift_id = $1 AND on_call', [shiftId]);
  if (n <= 1) throw new AppError(409, 'At least one doctor must stay on call');
  await tx.query('UPDATE doctors SET on_call = false WHERE id = $1', [doctorId]);
});
```

### Consistent report in Repeatable Read (FastAPI)
```python
async with engine.connect() as conn:
    conn = await conn.execution_options(isolation_level="REPEATABLE READ")
    async with conn.begin():
        totals = (await conn.execute(text("SELECT SUM(balance) FROM wallets"))).scalar()
        ledger = (await conn.execute(text("SELECT SUM(amount) FROM ledger"))).scalar()
        assert totals == ledger          # both read from the same snapshot
```

### Prisma
```js
await prisma.$transaction(fn, { isolationLevel: Prisma.TransactionIsolationLevel.Serializable });
```

### MySQL note
```sql
SELECT @@transaction_isolation;          -- REPEATABLE-READ by default
SELECT stock FROM items WHERE id = 7 FOR UPDATE;   -- locking read: prevents lost update
```

### MongoDB
```js
session.startTransaction({ readConcern: { level: 'snapshot' }, writeConcern: { w: 'majority' } });
// snapshot isolation within the transaction; write conflicts abort → retry (withTransaction does it)
```

---

## ⚫ Interview Questions + Answers

**Q1: What are the four isolation levels and what does each prevent?**
A1: Read Uncommitted (allows dirty reads; in Postgres it behaves as Read Committed). Read Committed (no dirty reads, but non-repeatable reads and phantoms possible; the Postgres default). Repeatable Read (the same snapshot or rows for the whole transaction, so no non-repeatable reads; in Postgres also no phantoms, since it's snapshot isolation; the MySQL default). Serializable (equivalent to some serial order, prevents all anomalies including write skew, at the cost of aborts and retries).

**Q2: What is write skew? Give an example and fix.**
A2: Two concurrent transactions read an overlapping set of data, each makes a decision based on it, and each updates different rows, so together they violate an invariant that each alone would preserve. Example: two doctors each see two on call and each goes off call, leaving zero. Snapshot isolation (Repeatable Read) doesn't prevent it. Fixes: SERIALIZABLE with retries, explicitly locking the rows read (`FOR UPDATE`), or materializing the constraint (a row or constraint that both transactions must update).

**Q3: What is the default isolation level in PostgreSQL and MySQL, and does it matter?**
A3: Postgres: Read Committed. MySQL InnoDB: Repeatable Read. It matters because code that is safe in one might not be in the other. In Postgres Read Committed, a read-then-update without locking can lose updates. MySQL Repeatable Read gives a stable snapshot for plain reads, but plain read-then-write can still lose updates without `FOR UPDATE`. Always use atomic updates or explicit locking for critical read-modify-write.

**Q4: Why not always use Serializable?**
A4: It reduces concurrency and adds overhead (dependency tracking or locking). Under contention, many transactions abort with serialization failures and must be retried, which hurts latency and throughput, and every code path needs retry logic. Most workloads get correctness from Read Committed plus targeted techniques (atomic updates, row locks, unique or exclusion constraints). Use Serializable where complex invariants span multiple rows.

**Q5: How do you prevent two users from booking the same time slot?**
A5: Best is a database constraint: a unique constraint on (resource, slot) for fixed slots, or a Postgres exclusion constraint with range types for arbitrary intervals. The DB guarantees no overlap even under concurrency, and the losing transaction gets an error to show "slot taken". Alternatives: lock the resource row with `SELECT ... FOR UPDATE` before checking and inserting, or Serializable isolation with retries. For high contention (concert tickets), add short-lived holds in Redis and a queue.

---

## 🔷 Trade-offs
✅ Higher isolation: fewer anomalies, simpler reasoning, safer invariants.
❌ Higher isolation: more blocking/aborts, retries required, lower throughput.
✅ Lower isolation: high concurrency and performance.
❌ Lower isolation: developers must handle races explicitly (locks, atomic updates, constraints).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Isolation level | Degree of separation between transactions | transactions के बीच दूरी का स्तर |
| Dirty read | Reading uncommitted data | अधूरा (uncommitted) डेटा पढ़ना |
| Non-repeatable read | Row changes between reads | दोबारा पढ़ने पर बदली value |
| Phantom | New rows appear in repeated query | नई rows का अचानक आना |
| Write skew | Concurrent decisions break invariant | साथ के फ़ैसले से नियम टूटना |
| Snapshot isolation | Txn reads a fixed snapshot | एक तय snapshot से पढ़ना |
| Serialization failure | Txn aborted to keep serializability | टकराव पर abort |
| Exclusion constraint | No overlapping values allowed | overlap रोकने वाला नियम |

---

## ⚡ 3-Line Summary
**English:**
1. Isolation levels: Read Uncommitted < Read Committed (PG default) < Repeatable Read (MySQL default) < Serializable.
2. Know the anomalies: dirty read, non-repeatable read, phantom, lost update, write skew.
3. Use defaults + atomic updates/locks/constraints; use Serializable (with retries) for multi-row invariants.

**Hindi:**
1. Levels: Read Uncommitted < Read Committed (PG) < Repeatable Read (MySQL) < Serializable।
2. गड़बड़ियाँ याद रखो: dirty read, non-repeatable, phantom, lost update, write skew।
3. Default + atomic update/lock/constraint; कई rows के नियम के लिए Serializable + retry।

---

## ➡️ Next Topic Suggestion
**36. Database Locks** — Isolation is implemented partly with locks. Next: row vs table locks, shared vs exclusive, FOR UPDATE / SKIP LOCKED, deadlocks, and how migrations can lock your whole table.
