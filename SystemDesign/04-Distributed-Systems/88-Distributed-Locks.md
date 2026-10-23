# 88. Distributed Locks
# हिंदी में: Distributed Lock — कई सर्वरों में से सिर्फ़ एक को ही किसी काम या resource तक एक समय पर पहुँचने देना (जैसे एक ही सर्वर cron चलाए)

---

## 🔵 Simple Definition (English)
A **distributed lock** ensures that **only one process across many machines** can perform a critical operation or access a shared resource at a time, e.g. run a scheduled job, process a specific order, or refresh a token. It's implemented with a shared coordination store: **Redis (SET NX PX)**, a **database** (row locks, advisory locks), or a **consensus system** (etcd, ZooKeeper, Consul) using **leases** (locks with expiry) and ideally **fencing tokens**.

## 🔵 सरल परिभाषा (Hindi)
Distributed lock से कई सर्वरों में से एक समय पर सिर्फ़ एक ही process कोई ख़ास काम कर पाता है — जैसे रात का settlement job सिर्फ़ एक सर्वर चलाए, या एक order को एक ही worker प्रोसेस करे।
यह Redis, Database या etcd/ZooKeeper में "ताला" रखकर होता है, जिसकी एक expiry (lease) होती है।

---

## 🔴 Problem it Solves
With horizontal scaling, the same code runs on **N instances**:
- A `setInterval`/cron "daily settlement" runs **N times** → N payouts ❌.
- Two workers pick the **same job**, or two requests refresh the **same OAuth token** simultaneously.
- Two instances update a **shared external resource** (e.g. a partner inventory API) concurrently and corrupt state.

In-process mutexes only protect **one** process. You need coordination **across machines**.

## 🔴 यह क्यों बना? (Hindi)
Horizontal scaling में वही code N सर्वरों पर चलता है — रोज़ का settlement N बार चल जाएगा (N बार payout!), दो workers एक ही job उठा लेंगे, दो requests एक साथ token refresh करेंगी।
एक process का mutex सिर्फ़ उसी process को बचाता है; कई मशीनों के बीच तालमेल के लिए distributed lock चाहिए।

---

## 🟢 How it Works — Step by Step

### Basic Redis lock (single instance)

```
ACQUIRE:  SET lock:settlement <random-token> NX PX 30000
          NX  → only if not exists (atomic "test-and-set")
          PX  → auto-expire in 30s (lease) — if holder crashes, lock frees itself
          → OK = acquired; nil = someone else holds it

WORK:     do the critical section (must finish < lease, or EXTEND the lease)

RELEASE:  only if I still own it (compare token) — atomic Lua:
          if redis.call('GET', KEYS[1]) == ARGV[1] then return redis.call('DEL', KEYS[1]) end
Why the token? If my lease expired and someone else acquired the lock, a plain DEL would
release THEIR lock ❌.
```

### The fundamental problem: leases + pauses

```
Client A acquires lock (lease 30s)
Client A has a long GC pause / network stall for 40s  😴
Lease expires → Client B acquires lock, starts writing
Client A wakes up, THINKS it still holds the lock → writes too → BOTH wrote ❌

No lease-based lock can fully prevent this on its own (clocks, pauses, network delays).
→ FENCING TOKENS
```

### Fencing tokens (the correct fix)

```
Lock service returns a monotonically increasing number with each grant:
   A gets lock → token 33
   A pauses... lease expires
   B gets lock → token 34 → writes to storage with token 34 (storage remembers max = 34)
   A wakes → writes with token 33 → storage REJECTS (33 < 34) ✅

Requires the protected resource to check tokens (DB: WHERE version < :token / conditional update).
etcd/ZooKeeper give natural tokens (revision / zxid). Redis doesn't by default (use INCR as counter).
```

### Implementation options

```
┌────────────────────────┬────────────────────────────────────┬──────────────────────────────────┐
│ Option                 │ How                                │ Safety / notes                   │
├────────────────────────┼────────────────────────────────────┼──────────────────────────────────┤
│ Redis SET NX PX        │ single Redis key with TTL          │ Good for EFFICIENCY locks (avoid │
│                        │                                    │ duplicate work); can fail on     │
│                        │                                    │ failover (async replication)     │
│ Redlock (5 Redis nodes)│ majority of independent masters    │ Debated (Kleppmann vs antirez);  │
│                        │                                    │ still timing-dependent           │
│ Postgres advisory lock │ pg_try_advisory_lock(key)          │ Session-bound, released on       │
│                        │                                    │ disconnect; great if you have PG │
│ DB row lock / unique   │ SELECT ... FOR UPDATE, or INSERT   │ Transactional, strong; DB load   │
│ row                    │ into locks table w/ unique key     │                                  │
│ etcd / ZooKeeper /     │ consensus-backed leases, sessions, │ Strongest (CORRECTNESS locks),   │
│ Consul                 │ revisions as fencing tokens        │ extra infrastructure             │
│ DynamoDB conditional   │ PutItem if not exists + TTL        │ Managed, decent                  │
│ write                  │                                    │                                  │
└────────────────────────┴────────────────────────────────────┴──────────────────────────────────┘
```

### Efficiency lock vs correctness lock (Martin Kleppmann's distinction)
```
Efficiency: prevents duplicate work; occasional double execution is tolerable (sending a digest email
            twice is annoying, not catastrophic) → Redis SET NX PX is fine
Correctness: double execution causes damage (double payout, corrupt data) → use consensus-based
            locks + fencing tokens, AND make the operation idempotent / use DB constraints
Best practice: prefer designs that don't need locks for correctness:
  idempotency keys, unique constraints, conditional updates (optimistic concurrency), single-writer
  partitioning (Kafka partition per key), SKIP LOCKED job queues.
```

### Lock hygiene
```
✓ Always set a TTL/lease          ✓ Random owner token, compare-and-delete on release
✓ Lease > expected work time; renew (watchdog) for long jobs; abort if renewal fails
✓ Use tryLock with timeout, not infinite blocking
✓ Keep critical sections short   ✓ Monitor lock contention and lease expirations
```

## 🟢 कैसे काम करता है? (Hindi)
1. Lock लेना: Redis में `SET lock:job <random token> NX PX 30000` — key नहीं है तो बनाओ (मिल गया), 30 सेकंड की expiry के साथ।
2. काम करो (lease से पहले ख़त्म, या lease बढ़ाओ); छोड़ते समय सिर्फ़ तभी delete जब token अपना हो (Lua script)।
3. समस्या: lock वाला process अटक (GC pause) गया, lease ख़त्म, दूसरे ने lock लिया — पहला जागकर भी लिख देगा।
4. हल: fencing token — हर lock के साथ बढ़ता नंबर; storage पुराने नंबर वाला write मना कर दे।
5. सिर्फ़ दोहराया काम बचाना हो तो Redis काफ़ी; पैसे जैसे सही-ग़लत वाले काम में etcd/DB + fencing + idempotency, या lock की ज़रूरत ही न पड़े ऐसा design।

---

## 🟡 Real World Example

**Martin Kleppmann vs Redis (Redlock debate, 2016)** — Kleppmann's essay "How to do distributed locking" showed that Redlock's safety depends on timing assumptions (bounded pauses and clock drift), and argued for fencing tokens and consensus systems for correctness. Salvatore Sanfilippo (antirez) responded. The debate is now standard interview material.

**Kubernetes leader election** — controllers (scheduler, controller-manager) use Lease objects in etcd so only one active replica makes decisions, which is distributed locking via consensus.

**Cron jobs in scaled apps (very common in Indian startups)** — daily payout, settlement or report jobs run with a Redis or Postgres advisory lock so only one ECS task runs them. Some teams learned this after paying vendors twice.

**Google Chubby** — Google's lock service (Paxos-based) used by GFS and Bigtable for master election and coarse-grained locking. It inspired ZooKeeper and etcd.

## 🟡 Real Example Hindi में
Martin Kleppmann ने 2016 में बताया कि Redis का Redlock समय की मान्यताओं पर टिका है, सही-ग़लत वाले काम के लिए fencing tokens और consensus चाहिए — यह बहस इंटरव्यू में अक्सर आती है।
कई startups में रोज़ का payout job कई सर्वरों पर चला और vendors को दो बार पैसे गए — फिर Redis/Postgres lock लगाया गया। Kubernetes भी etcd lease से एक ही leader चुनता है।

---

## 🟠 My Stack Example

### Redis lock with token, TTL, safe release, renewal (Node)
```js
import crypto from 'node:crypto';
const RELEASE = `if redis.call('GET', KEYS[1]) == ARGV[1] then return redis.call('DEL', KEYS[1]) else return 0 end`;
const EXTEND  = `if redis.call('GET', KEYS[1]) == ARGV[1] then return redis.call('PEXPIRE', KEYS[1], ARGV[2]) else return 0 end`;

export async function withLock(name, ttlMs, fn) {
  const key = `lock:${name}`, token = crypto.randomUUID();
  const ok = await redis.set(key, token, { NX: true, PX: ttlMs });
  if (!ok) return { skipped: true };                                   // someone else is running it

  let lost = false;
  const renew = setInterval(async () => {                              // watchdog for long jobs
    const r = await redis.eval(EXTEND, { keys: [key], arguments: [token, String(ttlMs)] }).catch(() => 0);
    if (!r) { lost = true; clearInterval(renew); }
  }, ttlMs / 3);

  try { return { result: await fn(() => lost) }; }                     // fn can check isLost() and abort
  finally { clearInterval(renew); await redis.eval(RELEASE, { keys: [key], arguments: [token] }).catch(() => {}); }
}

// daily settlement — runs on every instance's scheduler, executes on ONE
cron.schedule('0 2 * * *', () => withLock('daily-settlement', 60_000, async (isLost) => {
  for (const batch of await pendingPayoutBatches()) {
    if (isLost()) throw new Error('lock lost, aborting');
    await payBatchIdempotently(batch);        // idempotency still required for correctness!
  }
}));
```
(Libraries: `redlock` npm, `@sesamecare-oss/redlock`; Python `redis-py` `Lock`.)

### Postgres advisory lock (no extra infra)
```js
const client = await pool.connect();
try {
  const { rows: [{ locked }] } = await client.query('SELECT pg_try_advisory_lock(hashtext($1)) AS locked', ['daily-settlement']);
  if (!locked) return;
  await runSettlement(client);
} finally {
  await client.query('SELECT pg_advisory_unlock(hashtext($1))', ['daily-settlement']).catch(() => {});
  client.release();                       // lock also auto-released if connection dies
}
// Transaction-scoped variant: pg_try_advisory_xact_lock → released at COMMIT/ROLLBACK
```

### Fencing token with DB conditional write
```sql
-- token from lock service (e.g. etcd revision or Redis INCR fence:counter)
UPDATE inventory_sync_state
SET last_synced_at = now(), fence = $1
WHERE resource_id = $2 AND fence < $1;     -- stale holders (smaller token) are rejected
```

### etcd lock (strong) — Node
```js
import { Etcd3 } from 'etcd3';
const etcd = new Etcd3({ hosts: process.env.ETCD });
await etcd.lock('locks/payout').ttl(30).do(async () => {
  await runPayout();                        // lease kept alive automatically; lost on session expiry
});
```

### FastAPI — redis-py Lock
```python
lock = r.lock("lock:refresh-partner-token", timeout=30, blocking_timeout=2)
if await lock.acquire():
    try:
        await refresh_token()
    finally:
        await lock.release()
```

### Better than locks: design them away
```
- Job queue with SKIP LOCKED / BullMQ (one consumer per job automatically)
- Kafka: partition by key → one consumer per partition = single writer per key
- Unique constraints / idempotency keys → duplicates rejected by the DB
- Conditional updates (optimistic concurrency) instead of "lock, read, write"
- Kubernetes CronJob with concurrencyPolicy: Forbid (single runner)
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you implement a distributed lock with Redis?**
A1: Acquire with `SET key <unique_token> NX PX <ttl>`, which is atomic: it sets only if absent and expires automatically. Do the work within the lease, renewing it for long tasks. Release with a Lua script that deletes only if the value equals your token, so you never release someone else's lock after your lease expired. Use tryLock with short waits rather than blocking forever.

**Q2: What's the problem with lease-based locks, and what are fencing tokens?**
A2: A lock holder can be paused (GC, VM suspend, network delay) beyond its lease. The lock expires, another client acquires it, and the paused client resumes believing it still holds the lock, so both act. Timing can't fully prevent this. Fencing tokens are monotonically increasing numbers issued with each lock grant. The protected resource accepts operations only with a token higher than the last seen, so a stale holder's writes are rejected.

**Q3: Is Redlock safe?**
A3: Redlock acquires the lock on a majority of independent Redis masters within a time bound. Critics (Kleppmann) note it relies on bounded clock drift, network delay and process pauses, provides no fencing tokens, and so isn't safe for correctness-critical locking under adverse timing. It's fine for efficiency locks. For correctness, use consensus systems (etcd, ZooKeeper) with fencing tokens, and make operations idempotent or protected by DB constraints.

**Q4: How would you ensure a scheduled job runs only once across 10 instances?**
A4: Options: a dedicated single scheduler (a Kubernetes CronJob with `concurrencyPolicy: Forbid`, EventBridge Scheduler triggering one task); a lock (Postgres advisory lock or Redis SET NX PX with renewal) around the job on every instance; or enqueueing the job with a deterministic job ID (e.g. `settlement:2026-10-18`) so duplicates are rejected. Regardless, make the job idempotent (per-batch status, unique payout constraints) so an accidental double run causes no damage.

**Q5: When should you avoid distributed locks?**
A5: Whenever the problem can be solved with simpler, safer primitives: DB transactions with row locks or conditional updates, unique constraints and idempotency keys, single-writer partitioning (one consumer per key), job queues that guarantee one consumer per job, or CRDTs and commutative updates. Locks add latency, contention, failure modes (expired leases, a lock service outage) and correctness pitfalls. Use them as a last resort, and use strong ones when correctness matters.

---

## 🔷 Trade-offs
✅ Advantages:
- Prevents duplicate work/concurrent mutation across instances; simple with Redis/PG.

❌ Disadvantages:
- Timing-dependent safety (pauses, clock drift); lock service is a dependency/SPOF.
- Contention reduces throughput; deadlocks/expired leases cause subtle bugs.
- Correctness needs fencing tokens + idempotency anyway.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Distributed lock | Mutual exclusion across machines | कई मशीनों में एक ही को अनुमति |
| Lease | Lock with expiry | expiry वाला ताला |
| SET NX PX | Redis atomic set-if-absent with TTL | Redis का ताला command |
| Owner token | Random value identifying holder | ताले के मालिक की पहचान |
| Fencing token | Increasing number rejecting stale holders | पुराने मालिक को रोकने वाला नंबर |
| Redlock | Multi-node Redis lock algorithm | कई Redis वाला ताला |
| Advisory lock | Application-level DB lock | DB का ऐप-स्तर का ताला |
| Efficiency vs correctness lock | Avoid dup work vs prevent damage | दोहराव रोकना बनाम नुक़सान रोकना |
| Watchdog / renewal | Extending lease while working | काम के दौरान lease बढ़ाना |

---

## ⚡ 3-Line Summary
**English:**
1. Distributed locks give mutual exclusion across instances: Redis SET NX PX + token + safe release, PG advisory locks, or etcd/ZooKeeper leases.
2. Leases can expire during pauses → use fencing tokens for correctness; Redis/Redlock are fine for efficiency locks.
3. Prefer lock-free designs (idempotency, unique constraints, conditional updates, single-writer partitions, job queues).

**Hindi:**
1. Distributed lock = कई सर्वरों में एक को ही अनुमति: Redis SET NX PX + token, Postgres advisory lock, या etcd lease।
2. Pause में lease ख़त्म हो सकती है → सही-ग़लत वाले काम में fencing token; दोहराव रोकने के लिए Redis काफ़ी।
3. जहाँ हो सके lock के बिना design: idempotency, unique constraint, conditional update, job queue।

---

## ➡️ Next Topic Suggestion
**89. Leader Election** — A special, long-lived lock: choosing one node to be "the leader" (primary DB, scheduler, partition owner). Next: how leader election works with Raft, ZooKeeper and Kubernetes leases, plus split-brain prevention.
