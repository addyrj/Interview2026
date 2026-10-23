# 37. MVCC — Multi-Version Concurrency Control
# हिंदी में: MVCC — एक row के कई version रखकर पढ़ने और लिखने वालों को एक साथ, बिना एक-दूसरे को रोके, काम करने देना

---

## 🔵 Simple Definition (English)
**MVCC** is how modern databases (PostgreSQL, MySQL InnoDB, Oracle, MongoDB WiredTiger, CockroachDB) handle concurrency. Instead of overwriting a row in place, an update **creates a new version**. Each transaction reads a consistent **snapshot**: the versions that were committed when its snapshot was taken.
Result: **readers don't block writers, and writers don't block readers.**

## 🔵 सरल परिभाषा (Hindi)
MVCC में row को बदलने पर पुरानी row मिटती नहीं, एक नया version बनता है। हर transaction को डेटा की एक "तस्वीर" (snapshot) दिखती है।
इसलिए पढ़ने वाले लिखने वालों को नहीं रोकते और लिखने वाले पढ़ने वालों को नहीं।

---

## 🔴 Problem it Solves
With pure locking:
- A long report (`SELECT SUM(...)` over 10M rows) would hold **shared locks** → all updates wait → the app freezes.
- Or writes would hold **exclusive locks** → every read waits.

MVCC gives each reader its own consistent view **without locks**, so OLTP writes and long reads run together. It also makes **snapshot isolation**, consistent backups (`pg_dump` while live) and fast rollbacks possible.

The cost: old versions must be **cleaned up** (VACUUM in Postgres, purge in InnoDB), otherwise you get **bloat**.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ locks से: लंबी रिपोर्ट चले तो सारे updates रुक जाएँ, या update चले तो सारे reads रुक जाएँ — ऐप जाम।
MVCC में हर पढ़ने वाले को अपनी snapshot मिलती है, कोई ताला नहीं। क़ीमत: पुराने versions की सफ़ाई (VACUUM) करनी पड़ती है, नहीं तो टेबल फूलती (bloat) है।

---

## 🟢 How it Works — Step by Step

### Postgres: row versions with xmin / xmax

```
Each row version (tuple) has hidden columns:
  xmin = transaction ID that CREATED this version
  xmax = transaction ID that DELETED/REPLACED it (0 if still live)

Initial:   (xmin=100, xmax=0)   id=1 balance=500

T200: UPDATE ... SET balance=400 WHERE id=1
  old: (xmin=100, xmax=200)  balance=500   ← marked replaced by 200
  new: (xmin=200, xmax=0)    balance=400   ← new version (new physical location)

Reader T150 (snapshot before 200 committed) → sees balance=500
Reader T250 (after 200 committed)           → sees balance=400
Nobody waited for anybody.
```

### Snapshot visibility rule (simplified)

```
A version is visible to my snapshot if:
  ✓ xmin committed before my snapshot was taken
  ✓ and (xmax = 0  OR  xmax not committed before my snapshot)
Read Committed:   new snapshot per statement
Repeatable Read:  one snapshot for the whole transaction
```

### Writers still conflict with writers

```
T1: UPDATE row 1 (creates new version, holds row lock)
T2: UPDATE row 1 → waits for T1
   Read Committed: after T1 commits, T2 re-reads latest version and applies its update
   Repeatable Read/Serializable: T2 ABORTS ("could not serialize access due to concurrent update")
MVCC removes reader/writer blocking — NOT writer/writer conflicts.
```

### Dead tuples, VACUUM and bloat (Postgres)

```
Every UPDATE = INSERT new version + mark old dead. DELETE = mark dead.
Dead tuples stay in the table until VACUUM removes them (once no snapshot needs them).

Table pages:  [live][dead][dead][live][dead][live] ...
               └── VACUUM marks dead space reusable; updates visibility map
               └── VACUUM FULL / pg_repack rewrites table to shrink (FULL locks table!)

Autovacuum runs automatically. Problems when:
  - very high UPDATE rate on a big table (counters!) → dead tuples pile up
  - a LONG-RUNNING transaction (or idle-in-transaction session, or old replication slot)
    holds an old snapshot → VACUUM can't remove ANY tuples newer than it → massive bloat
  - Transaction ID wraparound: 32-bit txn IDs; VACUUM "freezes" old rows. If neglected,
    Postgres forces a shutdown to protect data (rare, but famous outages)
```

### MySQL InnoDB approach (different implementation)

```
Updates happen IN PLACE in the clustered index; the OLD version goes to the UNDO LOG.
Readers needing an old snapshot reconstruct it from undo records.
Purge thread cleans undo logs once no snapshot needs them.
Long transactions → undo log ("history list length") grows → slower reads.
```

### HOT updates (Postgres optimization)
```
If an UPDATE doesn't change any indexed column and there's free space in the same page,
Postgres does a Heap-Only Tuple update → no index updates needed → much cheaper.
Tip: don't index frequently-updated columns (like last_seen_at) unless needed;
     set fillfactor = 80–90 on hot-update tables to leave room.
```

## 🟢 कैसे काम करता है? (Hindi)
1. UPDATE पुरानी row नहीं मिटाता — नया version बनाता है और पुराने पर "replaced by txn X" लिख देता है।
2. हर transaction की एक snapshot होती है; उसे वही versions दिखते हैं जो snapshot से पहले commit हुए।
3. इसलिए SELECT को ताला नहीं चाहिए; पर दो writers एक ही row पर अब भी टकराते हैं।
4. पुराने (dead) versions VACUUM साफ़ करता है; लंबा चलता transaction सफ़ाई रोक देता है → bloat।
5. MySQL पुराने version undo log में रखता है; Postgres टेबल में ही।

---

## 🟡 Real World Example

**Uber's Postgres → MySQL migration (2016)** — one of Uber's stated reasons was Postgres write amplification. Every update created a new tuple and updated **all indexes** (for non-HOT updates), which multiplied writes and replication traffic for their update-heavy tables. InnoDB's in-place updates with undo logs fit that workload better. A classic, real MVCC trade-off.

**Sentry / Mailchimp / others — transaction ID wraparound** — several companies have had Postgres outages when autovacuum couldn't keep up on huge tables and the DB approached XID wraparound, forcing emergency maintenance. Monitoring `age(datfrozenxid)` is now standard practice.

**Long idle transactions** — a common real bug: a script or ORM session opens a transaction and forgets to commit. For days, VACUUM can't clean the hot tables, they bloat 10×, and queries slow down. The fix: `idle_in_transaction_session_timeout`.

## 🟡 Real Example Hindi में
Uber ने 2016 में Postgres से MySQL पर जाने का एक कारण बताया — Postgres में हर update नया version और सारे indexes अपडेट करता था, जिससे बहुत ज़्यादा writes होते थे।
कई कंपनियों में कोई script transaction खोलकर भूल गई — कई दिन VACUUM सफ़ाई नहीं कर पाया, टेबल 10 गुना फूल गई और queries धीमी हो गईं।

---

## 🟠 My Stack Example

### See MVCC in action
```sql
SELECT xmin, xmax, id, balance FROM wallets WHERE id = 1;
-- open two psql sessions:
-- S1: BEGIN ISOLATION LEVEL REPEATABLE READ; SELECT balance FROM wallets WHERE id=1;  -- 500
-- S2: UPDATE wallets SET balance = 400 WHERE id = 1;   -- not blocked!
-- S1: SELECT balance FROM wallets WHERE id=1;  -- still 500 (snapshot)
-- S1: COMMIT; SELECT ...;                       -- now 400
```

### Monitor bloat & vacuum health
```sql
-- dead tuples and last autovacuum per table
SELECT relname, n_live_tup, n_dead_tup,
       round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 1) AS dead_pct,
       last_autovacuum
FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10;

-- long-running / idle-in-transaction sessions (block vacuum)
SELECT pid, state, now() - xact_start AS xact_age, left(query, 80)
FROM pg_stat_activity WHERE xact_start IS NOT NULL ORDER BY xact_start LIMIT 10;

-- XID wraparound risk
SELECT datname, age(datfrozenxid) FROM pg_database ORDER BY 2 DESC;   -- alert if > ~1 billion
```

### Settings that protect you
```conf
idle_in_transaction_session_timeout = '60s'   # kill forgotten open transactions
statement_timeout = '30s'                     # (per role/app) no runaway queries
# Hot tables with many updates: vacuum more aggressively
ALTER TABLE posts SET (autovacuum_vacuum_scale_factor = 0.02, fillfactor = 85);
```

### App-level habits (Node / FastAPI)
```js
// ✅ Always release transactions (finally), never keep a transaction open across awaits on
// external APIs or user actions. Long reports → run on a READ REPLICA, not the primary.
const reportPool = new pg.Pool({ connectionString: process.env.REPLICA_URL });
```
```python
# SQLAlchemy: avoid sessions left open in background tasks; use `async with session.begin():`
```

### Reduce write amplification
```
- Don't store fast-changing counters on wide, heavily-indexed rows → separate small table
  (post_counters(post_id, likes)) or Redis
- Avoid indexing columns updated constantly (last_seen_at) unless needed
- Batch updates instead of updating the same row 1000×/s
```

### Consistent backups thanks to MVCC
```bash
pg_dump --format=custom --file=backup.dump "$DATABASE_URL"   # consistent snapshot while app runs
```

---

## ⚫ Interview Questions + Answers

**Q1: What is MVCC and why is it used?**
A1: Multi-Version Concurrency Control keeps multiple versions of each row. Writers create new versions instead of overwriting, and each transaction reads from a consistent snapshot of committed versions. Readers never wait for writers and vice versa, which gives high concurrency, consistent reads for long queries and backups, and the basis for snapshot isolation. It's used by Postgres, MySQL InnoDB, Oracle, MongoDB and others.

**Q2: Does MVCC eliminate all locking?**
A2: No. It removes read/write blocking, but concurrent writes to the same row still conflict. The second writer waits for the first to commit (row lock), and at higher isolation levels it may be aborted. DDL still needs table locks, and explicit locks (`FOR UPDATE`) are still used for read-modify-write correctness.

**Q3: What is VACUUM in PostgreSQL and why is it needed?**
A3: Because updates and deletes leave dead tuple versions in the table, VACUUM reclaims space from tuples no longer visible to any transaction, updates the visibility map (enabling index-only scans), and freezes old transaction IDs to prevent XID wraparound. Autovacuum runs it automatically, but busy tables may need tuned thresholds. `VACUUM FULL` rewrites the table to shrink it but takes an exclusive lock, so use pg_repack online instead.

**Q4: How can a long-running transaction hurt a Postgres database?**
A4: It holds an old snapshot, so VACUUM can't remove any dead tuples created after it began, anywhere in the database. Hot tables bloat, indexes grow, queries slow down, and in extreme cases it pushes toward XID wraparound. It may also hold locks that block DDL. Mitigate with `idle_in_transaction_session_timeout` and statement timeouts, by running analytics on replicas, by monitoring `pg_stat_activity`, and by watching replication slots too, because abandoned slots have the same effect.

**Q5: How does MVCC differ between PostgreSQL and MySQL InnoDB?**
A5: Postgres stores new row versions in the table heap itself (append-new, mark-old-dead), so old versions live in the table until VACUUM. Non-HOT updates must also update every index, causing write amplification. InnoDB updates rows in place in the clustered index and writes the previous version to the undo log. Readers reconstruct old versions from undo, and a purge thread cleans it. Long transactions in InnoDB grow the undo history and slow reads, while in Postgres they cause table bloat.

---

## 🔷 Trade-offs
✅ Advantages:
- High concurrency: readers/writers don't block each other.
- Consistent snapshots for long reads, backups, repeatable read isolation.

❌ Disadvantages:
- Storage overhead for old versions; needs vacuum/purge maintenance.
- Bloat and performance degradation if cleanup falls behind (long transactions!).
- Write amplification (Postgres index updates on non-HOT updates).
- Writer-writer conflicts still need locks/retries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MVCC | Multiple row versions for concurrency | row के कई version |
| Snapshot | Consistent view at a point in time | एक समय की तस्वीर |
| Tuple | A physical row version (Postgres) | row का एक version |
| xmin / xmax | Creator / deleter transaction IDs | बनाने / हटाने वाला txn |
| Dead tuple | Old version no longer needed | बेकार पुराना version |
| VACUUM | Clean dead tuples, freeze XIDs | पुराने version की सफ़ाई |
| Bloat | Wasted space from dead tuples | बेकार जगह से फूली टेबल |
| Undo log | InnoDB store of old versions | पुराने version का log |
| XID wraparound | Txn ID counter overflow risk | transaction ID ख़त्म होने का ख़तरा |
| HOT update | Update without touching indexes | index छुए बिना update |

---

## ⚡ 3-Line Summary
**English:**
1. MVCC keeps multiple row versions; each transaction reads its own snapshot → reads and writes don't block.
2. Writers still conflict; old versions must be cleaned (Postgres VACUUM, InnoDB purge).
3. Avoid long/idle transactions, tune autovacuum on hot tables, monitor bloat and XID age.

**Hindi:**
1. MVCC = row के कई version; हर transaction अपनी snapshot पढ़ता है → पढ़ना-लिखना एक-दूसरे को नहीं रोकते।
2. दो writers अब भी टकराते हैं; पुराने versions की सफ़ाई (VACUUM) ज़रूरी।
3. लंबे/भूले हुए transactions से बचो, autovacuum ट्यून करो, bloat पर नज़र रखो।

---

## ➡️ Next Topic Suggestion
**38. Connection Pooling** — Each transaction needs a DB connection, and connections are expensive. Next: why pooling is essential, how to size pools, and PgBouncer for many app instances or serverless.
