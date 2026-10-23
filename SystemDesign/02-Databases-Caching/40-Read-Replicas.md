# 40. Read Replicas
# हिंदी में: Read Replica — मुख्य database (primary) की लगातार अपडेट होने वाली copy, जिससे सिर्फ़ पढ़ने (reads) का काम लिया जाता है

---

## 🔵 Simple Definition (English)
A **read replica** is a copy of the **primary** database that continuously receives changes via **replication**. All **writes go to the primary**; **reads can be spread across replicas**. This scales read traffic and isolates heavy queries (reports, analytics) from the primary.
Replication is usually **asynchronous**, so replicas can be slightly behind (**replication lag**).

## 🔵 सरल परिभाषा (Hindi)
Read replica मुख्य DB (primary) की copy है जो लगातार अपडेट होती रहती है। सारे writes primary पर, और reads कई replicas में बाँट दिए जाते हैं।
ध्यान: replica थोड़ा पीछे (lag) हो सकता है — अभी लिखा डेटा तुरंत replica पर न दिखे।

---

## 🔴 Problem it Solves
Most apps are **read-heavy** (90%+ reads: browsing menus, feeds, product pages). One primary DB:
- CPU saturates on reads, so **writes slow down too**.
- Heavy analytics/report queries compete with user traffic.
- Vertical scaling hits limits.

Read replicas give:
- **Read scalability:** add replicas to add read capacity.
- **Workload isolation:** reports, exports, BI tools, search indexers read from a replica.
- **Availability:** a replica can be **promoted** to primary if the primary fails.
- **Geo reads:** a replica in another region gives local reads for distant users.

## 🔴 यह क्यों बना? (Hindi)
ज़्यादातर ऐप में 90% काम पढ़ने का होता है — एक primary DB पर reads से CPU भर जाता है और writes भी धीमे हो जाते हैं; भारी रिपोर्ट भी यूज़र ट्रैफ़िक से टकराती हैं।
Replicas से पढ़ने की क्षमता बढ़ती है, रिपोर्ट अलग चलती हैं, primary गिरे तो replica primary बन सकता है।

---

## 🟢 How it Works — Step by Step

```
                     WRITES (INSERT/UPDATE/DELETE)
   App ─────────────────────────────────────────────► ┌──────────┐
    │                                                 │ PRIMARY  │
    │                                                 └────┬─────┘
    │                                       WAL / binlog   │  streamed continuously
    │                                    ┌─────────────────┼─────────────────┐
    │   READS                            ▼                 ▼                 ▼
    └──────────────────────────────► ┌────────┐       ┌────────┐       ┌────────────┐
           (load balanced)            │Replica1│       │Replica2│       │ Replica 3  │
                                      └────────┘       └────────┘       │ (reports/  │
                                                                         │ other region)
                                                                         └────────────┘
```

### How replication works (Postgres streaming / MySQL binlog)

```
1. Primary writes every change to its WAL (Postgres) / binlog (MySQL)
2. Replica connects and STREAMS those log records
3. Replica REPLAYS them → same data (physical replication = byte-level copy of pages)
4. Replica is read-only (hot standby)

Logical replication (Postgres) = replicate row changes per table (can filter, different versions)
                                 → used for migrations, CDC, partial replicas
```

### Sync vs async replication

```
ASYNC (default for read replicas)
  Primary commits → ACK to app immediately → replica applies a few ms–seconds later
  ✅ fast writes   ❌ replica lag; if primary dies, last few transactions may be lost

SYNC (used for HA standby, e.g. RDS Multi-AZ)
  Primary waits until standby confirms WAL received/flushed → then ACK
  ✅ no data loss on failover   ❌ higher write latency; standby down → writes stall (unless fallback)

SEMI-SYNC (MySQL) / quorum (Aurora: 4 of 6 copies) — middle ground
```

### Replication lag — the #1 problem

```
t=0ms   User updates profile name → PRIMARY ✓
t=5ms   App redirects to profile page → reads from REPLICA → still OLD name ❌
        "I just saved it, why didn't it change?!"

Typical lag: ms (healthy) → seconds/minutes (heavy writes, long queries on replica, network)
```

### Solutions for read-after-write consistency

```
1. Read-your-own-writes routing:
   after a user writes, send THEIR reads to the primary for N seconds (sticky flag in session/cookie)
2. Critical reads → primary always (checkout, balance, "my orders" just after placing)
3. LSN / GTID tracking: remember primary's log position after write; read from a replica
   only if it has replayed past that position (otherwise primary)
4. Return the updated object in the write response → client doesn't need to re-read
5. Optimistic UI on the client (show the new value immediately)
6. Accept staleness where fine (product listing, feeds, counts)
```

### What replicas don't do
```
✗ Don't scale WRITES (all writes still hit one primary) → partitioning/sharding (Topics 41–42)
✗ Not a backup (a bad DELETE replicates instantly!) → backups + PITR still needed
✗ Each replica needs full storage + similar instance size
```

## 🟢 कैसे काम करता है? (Hindi)
1. Primary हर बदलाव WAL/binlog में लिखता है; replicas उसे stream करके वही बदलाव अपने ऊपर दोहराते हैं।
2. ऐप writes primary पर भेजता है, reads replicas पर (बाँटकर)।
3. Async replication में replica कुछ ms-सेकंड पीछे होता है (lag) — अभी सेव किया नाम तुरंत न दिखे।
4. हल: लिखने के बाद कुछ सेकंड उस यूज़र के reads primary से, ज़रूरी reads (balance, checkout) हमेशा primary से।
5. Replica writes स्केल नहीं करता और backup भी नहीं है — ग़लत DELETE replica पर भी तुरंत पहुँच जाता है।

---

## 🟡 Real World Example

**Facebook / Instagram** — replicate MySQL/Postgres data to many replicas and regions. Instagram served reads from replicas in multiple data centers, with careful handling of read-after-write: just after you post, your own reads go to the primary region.

**GitHub** — runs MySQL clusters with one primary and many replicas. Reads are routed to replicas, with tooling to avoid stale reads for the user who just wrote. Their 2018 incident (a 43-second network partition led to 24 hours of degraded service) involved replication topology and failover across data centers.

**E-commerce reporting** — companies like Flipkart and Myntra run BI dashboards and data exports against read replicas or CDC-fed warehouses, never the primary, so a heavy analyst query can't slow down checkout.

## 🟡 Real Example Hindi में
Instagram अपना डेटा कई replicas और regions में रखता था; post करने के तुरंत बाद आपके अपने reads primary से आते थे ताकि पुराना डेटा न दिखे।
Flipkart जैसी कंपनियाँ dashboard और रिपोर्ट replica या warehouse पर चलाती हैं, primary पर नहीं — ताकि checkout धीमा न हो।

---

## 🟠 My Stack Example

### Two pools: writer and reader (Node)
```js
export const writer = new pg.Pool({ connectionString: process.env.DATABASE_URL, max: 10 });
export const reader = new pg.Pool({ connectionString: process.env.DATABASE_READER_URL, max: 20 });
// AWS Aurora: cluster endpoint (writer) + reader endpoint (load-balances across replicas)

// read-your-own-writes: mark user as "recently wrote"
async function afterWrite(userId) { await redis.set(`rw:${userId}`, '1', { EX: 5 }); }
async function dbFor(userId) { return (await redis.exists(`rw:${userId}`)) ? writer : reader; }

app.patch('/api/v1/me', auth, async (req, res) => {
  const { rows: [u] } = await writer.query('UPDATE users SET name=$1 WHERE id=$2 RETURNING *', [req.body.name, req.user.id]);
  await afterWrite(req.user.id);
  res.json(u);                                   // return fresh data → no need to re-read
});

app.get('/api/v1/me', auth, async (req, res) => {
  const db = await dbFor(req.user.id);
  const { rows: [u] } = await db.query('SELECT * FROM users WHERE id=$1', [req.user.id]);
  res.json(u);
});

app.get('/api/v1/restaurants', async (req, res) => {   // staleness OK → replica
  const { rows } = await reader.query('SELECT ... LIMIT 20');
  res.json(rows);
});
```

### Prisma read replicas extension
```js
import { readReplicas } from '@prisma/extension-read-replicas';
const prisma = new PrismaClient().$extends(readReplicas({ url: process.env.DATABASE_READER_URL }));
await prisma.restaurant.findMany();            // → replica
await prisma.$primary().user.findUnique(...);  // → force primary
```

### FastAPI — route sessions
```python
writer_engine = create_async_engine(DATABASE_URL)
reader_engine = create_async_engine(DATABASE_READER_URL)

def get_db(read_only: bool = False):
    return async_sessionmaker(reader_engine if read_only else writer_engine)()
```

### Monitor replication lag
```sql
-- on replica
SELECT now() - pg_last_xact_replay_timestamp() AS replica_lag;
-- on primary
SELECT client_addr, state, write_lag, flush_lag, replay_lag FROM pg_stat_replication;
```
```
CloudWatch (RDS): ReplicaLag metric → alarm if > 5–10s; take lagging replica out of the reader pool
```

### Docker: local primary + replica (bitnami image)
```yaml
services:
  pg-primary:
    image: bitnami/postgresql:16
    environment: { POSTGRESQL_REPLICATION_MODE: master, POSTGRESQL_REPLICATION_USER: repl, POSTGRESQL_REPLICATION_PASSWORD: replpass, POSTGRESQL_PASSWORD: secret }
  pg-replica:
    image: bitnami/postgresql:16
    depends_on: [pg-primary]
    environment: { POSTGRESQL_REPLICATION_MODE: slave, POSTGRESQL_MASTER_HOST: pg-primary, POSTGRESQL_REPLICATION_USER: repl, POSTGRESQL_REPLICATION_PASSWORD: replpass, POSTGRESQL_PASSWORD: secret }
```

### Frontend / mobile impact
- After a mutation, update the React Query cache from the response (`setQueryData`) instead of immediately refetching, which avoids showing stale replica data.
- MongoDB: `readPreference: 'secondaryPreferred'` for feeds, `primary` for the user's own fresh data.

---

## ⚫ Interview Questions + Answers

**Q1: What are read replicas and when would you use them?**
A1: Copies of the primary database kept up to date via replication (usually async). They serve read-only queries. Use them when the workload is read-heavy and the primary's CPU or IO is saturated by reads, to isolate heavy reporting, analytics or exports from OLTP traffic, to serve reads closer to users in other regions, and as standby candidates for failover. They don't scale writes.

**Q2: What is replication lag and how do you handle it?**
A2: The delay between a commit on the primary and its application on a replica, ranging from milliseconds to seconds or more under load. It causes stale reads, especially read-after-write anomalies. Handle it by routing critical and just-written reads to the primary (read-your-own-writes for a short window), tracking the replication position (LSN/GTID) and only reading from caught-up replicas, returning updated data in write responses, monitoring lag and removing lagging replicas from rotation, and accepting staleness where it's fine.

**Q3: Synchronous vs asynchronous replication — trade-offs?**
A3: Synchronous: the primary waits for the replica to confirm before acknowledging a commit. There's no data loss on failover (RPO ≈ 0), but write latency is higher, and writes can stall if the standby is slow or unavailable. Asynchronous: the commit is acknowledged immediately, so writes are fast, but replicas lag, and if the primary fails, recent commits may be lost. Common setup: one synchronous standby for HA and async read replicas for scaling.

**Q4: Can read replicas replace backups?**
A4: No. Replication copies every change instantly, including mistakes: an accidental `DELETE FROM users` or `DROP TABLE` replicates to all replicas within milliseconds, and logical corruption propagates too. Backups with point-in-time recovery (snapshots + WAL archiving), ideally in another region or account, are needed to restore to a moment before the mistake. A delayed replica is a partial safety net, not a substitute.

**Q5: Your read replicas are lagging minutes behind. What could cause it?**
A5: Heavy write bursts on the primary (bulk imports, large migrations), a replica that's under-provisioned (smaller instance, less IOPS) or overloaded by heavy queries, long-running queries on the replica conflicting with WAL replay (Postgres `max_standby_streaming_delay`/hot standby feedback), network bottlenecks between regions, or single-threaded apply (older MySQL). Fix by right-sizing replicas, batching bulk writes, moving analytics to a dedicated replica or warehouse, tuning replay settings, and monitoring.

---

## 🔷 Trade-offs
✅ Advantages:
- Scales reads horizontally; isolates heavy reads; enables failover and geo-local reads.

❌ Disadvantages:
- Replication lag → stale reads; app needs routing logic.
- Doesn't scale writes; extra cost (full copy per replica).
- More operational complexity (monitoring lag, failover, connection routing).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Primary | DB that accepts writes | मुख्य DB (लिखने वाला) |
| Read replica | Read-only copy of primary | सिर्फ़ पढ़ने वाली copy |
| Replication | Copying changes to other nodes | बदलाव दूसरी copy तक भेजना |
| Replication lag | Delay before replica has change | replica का पीछे रहना |
| Async / Sync replication | ACK before / after replica confirms | बिना / साथ में इंतज़ार |
| Read-your-own-writes | User sees their own latest change | अपना बदलाव तुरंत दिखे |
| Promotion | Replica becomes primary | replica को primary बनाना |
| WAL / binlog | Change log shipped to replicas | बदलावों का log |
| LSN / GTID | Position in replication log | log में स्थिति |

---

## ⚡ 3-Line Summary
**English:**
1. Read replicas copy the primary (via WAL/binlog) and serve reads; writes stay on the primary.
2. Async replication causes lag → route critical/just-written reads to primary, monitor lag.
3. Replicas scale reads and help failover — they don't scale writes and aren't backups.

**Hindi:**
1. Read replica = primary की copy, reads के लिए; writes सिर्फ़ primary पर।
2. Lag की वजह से ज़रूरी या अभी लिखे डेटा के reads primary से, lag की monitoring करो।
3. Replica reads स्केल करता है और failover में मदद — writes स्केल नहीं करता, backup भी नहीं।

---

## ➡️ Next Topic Suggestion
**41. Database Partitioning** — When a single table gets enormous (billions of rows), even with indexes and replicas it gets hard to manage. Next: splitting big tables into partitions (range, list, hash) inside one database.
