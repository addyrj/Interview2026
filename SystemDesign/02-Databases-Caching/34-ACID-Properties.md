# 34. ACID Properties
# हिंदी में: ACID — Transaction की चार गारंटी: Atomicity (सब या कुछ नहीं), Consistency (नियम सही), Isolation (एक-दूसरे से अलग), Durability (स्थायी)

---

## 🔵 Simple Definition (English)
**ACID** is the set of four guarantees that a database transaction provides:
- **A — Atomicity:** all operations happen, or none do.
- **C — Consistency:** the database moves from one valid state to another (all rules/constraints hold).
- **I — Isolation:** concurrent transactions don't see each other's partial work; the result is as if they ran one by one (to the chosen degree).
- **D — Durability:** once committed, data survives crashes and power loss.

## 🔵 सरल परिभाषा (Hindi)
ACID transaction के चार वादे हैं:
**A** — सारे काम होंगे या कोई नहीं; **C** — DB के सारे नियम हमेशा सही रहेंगे; **I** — एक साथ चल रहे transactions एक-दूसरे का अधूरा काम नहीं देखेंगे; **D** — COMMIT के बाद डेटा crash में भी नहीं खोएगा।

---

## 🔴 Problem it Solves
Applications need to trust their data without writing complex recovery code:
- **Crashes** mid-operation (power failure, OOM kill, deploy).
- **Concurrency**: thousands of users writing at once.
- **Bugs / bad input** that would break business rules (negative balance, orphan rows).
- **Hardware failures** after the user saw "Success".

ACID moves all this hard work into the database engine, which is why banks, e-commerce and booking systems rely on ACID databases.

## 🔴 यह क्यों बना? (Hindi)
सर्वर कभी भी crash हो सकता है, हज़ारों यूज़र एक साथ लिखते हैं, ग़लत डेटा नियम तोड़ सकता है — हर ऐप में इसका इलाज लिखना बहुत मुश्किल है।
ACID यह सारा कठिन काम DB के अंदर कर देता है, इसीलिए बैंक और बुकिंग सिस्टम ACID DB पर भरोसा करते हैं।

---

## 🟢 How it Works — Step by Step

### A — Atomicity (all or nothing)

```
Transfer ₹500 A → B
  step 1: A -= 500   ✓
  step 2: B += 500   💥 crash
Without atomicity: A lost ₹500, B got nothing.
With atomicity: on restart DB sees no COMMIT record → step 1 is undone.

HOW: Write-Ahead Log (WAL) + undo/redo.
  Changes are logged first. Uncommitted changes are rolled back on recovery.
  Postgres: new row versions from an aborted txn are simply invisible (MVCC) and later vacuumed.
```

### C — Consistency (valid state → valid state)

```
Rules enforced by the DB:
  NOT NULL, UNIQUE, PRIMARY KEY, FOREIGN KEY, CHECK (balance >= 0), triggers
A transaction that would violate a rule → error → rolled back.

⚠️ ACID "Consistency" ≠ CAP "Consistency"!
  ACID C = integrity rules hold.
  CAP C  = all replicas return the latest value (linearizability). (Topic 65)
⚠️ Also: business rules not expressed as constraints are the APP's job.
```

### I — Isolation (concurrent txns don't interfere)

```
T1: transfer A→B         T2: report SUM(all balances)
T2 must NOT see A debited but B not yet credited.

HOW:
  - MVCC (Postgres, MySQL InnoDB, Oracle): each txn reads a SNAPSHOT; writers create new versions;
    readers don't block writers and writers don't block readers.
  - Locks: row locks for writes; SELECT ... FOR UPDATE; predicate/range locks (MySQL gap locks).
  - Serializable Snapshot Isolation (Postgres SERIALIZABLE): detects dangerous patterns, aborts one.
Isolation LEVELS trade correctness vs concurrency → Topic 35:
  Read Uncommitted < Read Committed (Postgres default) < Repeatable Read (MySQL default) < Serializable
```

### D — Durability (committed = permanent)

```
COMMIT returns only after the WAL record is flushed to disk (fsync).
Power off 1 ms after "COMMIT OK" → on restart DB replays WAL → data is there.

Stronger durability:
  - synchronous replication to a standby (survives disk/machine loss)  ← RDS Multi-AZ
  - backups + WAL archiving (survive region/operator mistakes)
Weaker (faster) options:
  - Postgres synchronous_commit = off → may lose last few ms of commits on crash (not corruption)
  - Redis default (RDB snapshots / AOF everysec) → may lose ~1s of writes
  - MongoDB writeConcern w:1 vs w:"majority"
```

### Visual summary

```
┌───────────────┬──────────────────────────────┬──────────────────────────────────┐
│ Property      │ Guarantees                   │ Implemented by                   │
├───────────────┼──────────────────────────────┼──────────────────────────────────┤
│ Atomicity     │ all or nothing               │ WAL, undo/rollback, MVCC         │
│ Consistency   │ constraints always hold      │ constraints, triggers, FK checks │
│ Isolation     │ no interference between txns │ MVCC snapshots, locks, SSI       │
│ Durability    │ committed survives crashes   │ WAL fsync, replication, backups  │
└───────────────┴──────────────────────────────┴──────────────────────────────────┘
```

### ACID vs BASE
```
ACID (Postgres, MySQL, Oracle, Spanner, CockroachDB):  correctness first
BASE (Cassandra, DynamoDB default, many caches):       Basically Available, Soft state,
                                                        Eventually consistent — availability/scale first
Many NoSQL DBs now offer ACID for single-item or limited multi-item transactions.
```

## 🟢 कैसे काम करता है? (Hindi)
1. **Atomicity**: पहले बदलाव WAL (log) में; crash के बाद COMMIT न मिला तो सब वापस।
2. **Consistency**: NOT NULL, UNIQUE, FOREIGN KEY, CHECK जैसे नियम DB ख़ुद लागू करता है; टूटा तो rollback।
3. **Isolation**: MVCC — हर transaction को डेटा की एक snapshot दिखती है, दूसरों का अधूरा काम नहीं; ज़रूरत पर locks।
4. **Durability**: COMMIT तभी "OK" जब log disk पर पक्का (fsync) हो जाए; replication और backup से और पक्का।
5. ध्यान: ACID का C (नियम) और CAP का C (सब copies में latest डेटा) अलग चीज़ें हैं।

---

## 🟡 Real World Example

**Banks & UPI ledgers** — double-entry bookkeeping: every debit has a matching credit in the same transaction (atomicity). A CHECK constraint keeps balances ≥ 0 (consistency). Synchronous replication across data centers is used before acknowledging (durability). RBI requires strong audit trails.

**GitLab data loss (2017)** — an engineer accidentally deleted the production database directory, and 5 backup methods turned out not to be working. They lost ~6 hours of data. ACID durability protects against crashes, **not** against operator mistakes. You still need tested backups.

**MongoDB before 4.0** — no multi-document transactions, so apps had to implement two-phase commit patterns manually. Adding ACID transactions in 4.0 was a major milestone that shows how much developers need ACID.

## 🟡 Real Example Hindi में
बैंकों में हर debit के साथ उतना ही credit उसी transaction में (atomicity), balance ≥ 0 का नियम (consistency), और COMMIT से पहले दूसरे डेटा सेंटर में copy (durability)।
2017 में GitLab का production DB ग़लती से delete हो गया और backups काम नहीं कर रहे थे — 6 घंटे का डेटा गया। ACID crash से बचाता है, इंसानी ग़लती से नहीं — इसलिए backup टेस्ट करते रहो।

---

## 🟠 My Stack Example

### Consistency — push rules into the database
```sql
CREATE TABLE wallets (
  user_id BIGINT PRIMARY KEY REFERENCES users(id),
  balance NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (balance >= 0)     -- can never go negative
);
CREATE TABLE ledger (
  id BIGSERIAL PRIMARY KEY,
  txn_id UUID NOT NULL,
  user_id BIGINT NOT NULL REFERENCES users(id),
  amount NUMERIC(12,2) NOT NULL CHECK (amount <> 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (txn_id, user_id)                                           -- idempotency per leg
);
```

### Atomicity + consistency in a transfer (Node)
```js
await withTx(async (tx) => {
  const txnId = randomUUID();
  await tx.query('UPDATE wallets SET balance = balance - $1 WHERE user_id = $2', [amt, from]); // CHECK fails → error → rollback
  await tx.query('UPDATE wallets SET balance = balance + $1 WHERE user_id = $2', [amt, to]);
  await tx.query('INSERT INTO ledger(txn_id, user_id, amount) VALUES ($1,$2,$3), ($1,$4,$5)',
                 [txnId, from, -amt, to, amt]);
});
// Either all 3 statements apply, or none. Balance never < 0. Sum of ledger amounts per txn = 0.
```

### Isolation — choose level per operation
```js
await prisma.$transaction(async (tx) => { /* ... */ }, { isolationLevel: 'Serializable' });
// retry on P2034 (Prisma) / SQLSTATE 40001 — expected under Serializable
```
```python
async with engine.connect() as conn:
    conn = await conn.execution_options(isolation_level="REPEATABLE READ")
    async with conn.begin():
        ...
```

### Durability settings you should know
```sql
SHOW synchronous_commit;   -- 'on' (default) → durable on commit
-- For bulk analytics loads where losing the last second is OK:
SET LOCAL synchronous_commit = off;
```
```
RDS / Aurora: Multi-AZ → committed data is on 2+ AZs before ack (Aurora: 4 of 6 copies across 3 AZs)
Backups: automated snapshots + PITR (restore to any second in retention window)
Redis:   appendonly yes + appendfsync everysec  (still may lose ~1s — never store money only in Redis)
MongoDB: writeConcern { w: "majority", j: true } for important writes
```

### Mobile / frontend angle
- Never treat a local-only write (AsyncStorage, SQLite on the phone) as durable "success" for payments. The server's ACID commit is the source of truth, and the app shows "Processing…" until the server confirms.
- Offline-first apps (Topic M06) use local transactions in SQLite/WatermelonDB, then sync. Conflicts are resolved server-side.

---

## ⚫ Interview Questions + Answers

**Q1: Explain each ACID property with an example.**
A1: Atomicity: a ₹500 transfer debits A and credits B together. If anything fails, neither happens. Consistency: constraints like `balance >= 0` and foreign keys always hold, and a transaction violating them is rejected. Isolation: a report running during the transfer doesn't see A debited before B is credited, so each transaction behaves as if alone (to the isolation level). Durability: once the app gets "committed", the transfer survives a crash or power loss, because the WAL was flushed to disk and possibly replicated.

**Q2: How does a database implement atomicity and durability?**
A2: Mainly with write-ahead logging. Every change is written to a sequential log before the data pages. On COMMIT, the log record is flushed to stable storage (fsync), which gives durability. After a crash, recovery replays committed changes from the log (redo) and discards or undoes uncommitted ones, which gives atomicity. MVCC databases make uncommitted row versions invisible. Replication of the WAL to standbys adds durability across machines.

**Q3: What's the difference between Consistency in ACID and in CAP?**
A3: ACID consistency means a transaction preserves the database's integrity constraints and invariants (valid state to valid state). CAP consistency means linearizability in a distributed system: every read sees the most recent write, across all replicas. A single-node Postgres is ACID-consistent. A replicated system can be ACID per node yet serve stale reads from replicas, which is not CAP-consistent.

**Q4: Does ACID mean my data is safe from all loss?**
A4: No. Durability protects committed transactions from crashes and power loss on the storage it was written to. It doesn't protect against disk or machine destruction without replication, region outages without cross-region copies, accidental `DELETE`/`DROP` by people or bugs, ransomware, or corruption from bad hardware. You need replication, backups with point-in-time recovery, regularly tested restores, and access controls.

**Q5: Why do some systems relax ACID, and what do they gain?**
A5: Strict isolation and synchronous durability cost latency and throughput, and limit availability during network partitions. Distributed NoSQL systems relax them (eventual consistency, single-item atomicity, async replication) to get horizontal scale, low latency and always-on availability, e.g. shopping carts, feeds, metrics and chat. The trade-off moves complexity to the application: handling conflicts, duplicates and stale reads.

---

## 🔷 Trade-offs
✅ ACID advantages:
- Correctness and simplicity for application developers; trusted for money and critical data.

❌ ACID costs:
- Locking/validation overhead lowers throughput; fsync adds latency.
- Strong guarantees across distributed nodes are expensive (consensus, cross-region latency).
- Higher isolation = more aborts/retries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Atomicity | All or nothing | सब या कुछ नहीं |
| Consistency | Constraints always hold | नियम हमेशा सही |
| Isolation | Transactions don't interfere | transactions एक-दूसरे से अलग |
| Durability | Committed data survives crashes | पक्का किया डेटा स्थायी |
| WAL | Write-ahead log | पहले log में लिखना |
| fsync | Force data to physical disk | डेटा को disk पर पक्का करना |
| MVCC | Multiple versions for concurrency | एक row के कई version |
| BASE | Eventually consistent alternative | धीरे-धीरे consistent मॉडल |
| Double-entry | Every debit has a credit | हर debit का credit |

---

## ⚡ 3-Line Summary
**English:**
1. ACID = Atomicity (all-or-nothing), Consistency (constraints hold), Isolation (no interference), Durability (survives crashes).
2. Implemented via WAL, constraints, MVCC/locks, fsync and replication.
3. ACID protects from crashes and concurrency — not from human mistakes; keep tested backups.

**Hindi:**
1. ACID = सब या कुछ नहीं, नियम सही, एक-दूसरे से अलग, और स्थायी डेटा।
2. WAL, constraints, MVCC/locks, fsync और replication से लागू होता है।
3. ACID crash से बचाता है, इंसानी ग़लती से नहीं — backup ज़रूर टेस्ट करो।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [ByteByteGo — ACID properties](https://www.youtube.com/results?search_query=ACID+transactions+database+bytebytego) | Visual walkthrough, why each letter matters |
| 📺 YouTube | [Gaurav Sen — Transactions explained](https://www.youtube.com/results?search_query=database+transactions+ACID+gaurav+sen) | Two-phase locking, serializable schedules |
| 📝 Article | [PostgreSQL Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html) | Official Postgres docs — exact isolation behavior |
| 📝 Article | [Martin Kleppmann — DDIA Chapter 7 summary](https://martin.kleppmann.com/2017/03/13/ddia-outline.html) | The deepest free treatment of transactions anywhere |
| 🐙 GitHub | [system-design-primer — Databases](https://github.com/donnemartin/system-design-primer#relational-database-management-system-rdbms) | ACID, sharding, federation, master-slave in one page |

---

## ➡️ Next Topic Suggestion
**35. Isolation Levels** — "Isolation" comes in levels. Next: Read Uncommitted → Read Committed → Repeatable Read → Serializable, which anomalies each allows, and what Postgres and MySQL use by default.
