# 89. Leader Election
# हिंदी में: Leader Election — कई एक जैसे nodes में से एक को "leader" चुनना जो ख़ास ज़िम्मेदारी (writes, scheduling, coordination) सँभाले; leader गिरे तो अपने आप नया चुना जाए

---

## 🔵 Simple Definition (English)
**Leader election** is the process by which a group of nodes **agrees on exactly one node** to act as the **leader** (coordinator) for a task: accepting writes (DB primary), scheduling jobs, assigning partitions, or ordering operations. The others are **followers/standbys**. If the leader fails, the group **detects it and elects a new leader** automatically, while ensuring there are **never two leaders at once** (split brain).

## 🔵 सरल परिभाषा (Hindi)
Leader election में कई nodes मिलकर एक को "leader" चुनते हैं — वही writes लेगा या jobs बाँटेगा; बाक़ी followers रहते हैं।
Leader गिरे तो बाक़ी तुरंत नया leader चुनते हैं — और ध्यान रखा जाता है कि एक समय पर दो leaders कभी न हों (split brain)।

---

## 🔴 Problem it Solves
Many tasks are simpler and safer with a **single decision-maker**:
- A database needs **one primary** to order writes.
- A **scheduler** must not run the same job twice.
- **Kafka** needs one leader per partition; **Kubernetes** controllers must not fight each other.
- A **cache warmer** or **cleanup worker** should run once per cluster.

But a single fixed leader is a **SPOF**. Leader election gives you **single-leader simplicity with automatic failover**.

## 🔴 यह क्यों बना? (Hindi)
कई काम एक ही फ़ैसला लेने वाले से आसान और सुरक्षित होते हैं — DB का एक primary, scheduler जो job दो बार न चलाए, Kafka partition का एक leader।
पर एक तय leader = SPOF। Leader election एक leader की सरलता देता है, और गिरने पर अपने आप नया leader।

---

## 🟢 How it Works — Step by Step

### General approach (lease-based, using a CP store)

```
Nodes A, B, C want leadership; coordination store (etcd/ZooKeeper/Consul/K8s Lease/DB) is CP.

1. Each node tries to CREATE the leader key with a lease (TTL 15s):
      A succeeds → A is leader (key value = "A", revision/epoch = 7)
      B, C fail → become followers, WATCH the key
2. Leader renews (heartbeats) its lease every ~5s
3. A crashes / partitions → stops renewing → lease expires after 15s → key deleted
4. B and C notice (watch) → race to create the key → B wins → leader (epoch = 8)
5. If A comes back, it sees it's no longer leader; any writes with old epoch 7 are fenced/rejected
```

### Raft leader election (built into consensus systems)

```
States: FOLLOWER → CANDIDATE → LEADER

- Followers expect heartbeats from the leader.
- No heartbeat within a RANDOMIZED election timeout (e.g. 150–300 ms) → become CANDIDATE:
     term = term + 1, vote for self, request votes from others
- A node grants its vote to at most one candidate per term, and only if the candidate's log is
  at least as up-to-date as its own.
- Candidate with MAJORITY votes → LEADER for that term → sends heartbeats
- Split vote → timeout again (randomization makes it rare) → new term
- Term numbers act as fencing: messages from an older term are rejected

5 nodes: tolerate 2 failures (majority = 3).  3 nodes: tolerate 1.  (Topic 90)
```

### Bully algorithm & ring (classic textbook)
```
Bully: node with highest ID wins; when leader is suspected dead, a node messages all higher IDs;
       if none respond, it declares itself leader. Simple but assumes reliable failure detection.
Ring: election message passed around a logical ring collecting IDs; highest wins.
(Interview: know they exist; production uses Raft/Paxos/ZAB or a lease in a CP store.)
```

### Split brain prevention
```
- Majority quorum: a leader can only be elected (and keep leading) with a majority → a minority partition
  can't elect its own leader
- Lease expiry before new election: new leader waits ≥ old lease duration (clock-bound assumption)
- Fencing with term/epoch numbers: storage/peers reject commands from stale leaders
- Leader steps down when it can't reach a majority (check quorum)
```

### Where you meet leader election
```
Postgres HA (Patroni + etcd), MySQL (Orchestrator, Group Replication), MongoDB replica sets (Raft-like),
Redis Sentinel (sentinels vote), Kafka (KRaft controller quorum + partition leaders),
Elasticsearch (master-eligible nodes), Kubernetes (Lease objects for controllers; etcd itself uses Raft),
ZooKeeper (ZAB), Consul (Raft), your own app (one "singleton worker" via K8s lease / Redis / DB lock).
```

## 🟢 कैसे काम करता है? (Hindi)
1. सारे nodes एक CP store (etcd/ZooKeeper/K8s Lease) में leader key बनाने की कोशिश करते हैं — जो पहले बना ले, वो leader (lease के साथ)।
2. Leader हर कुछ सेकंड में lease नवीनीकृत (heartbeat) करता है; followers key पर नज़र (watch) रखते हैं।
3. Leader गिरा → lease ख़त्म → followers में दौड़, नया leader, नया epoch नंबर।
4. Raft में: heartbeat न मिले तो node random समय बाद उम्मीदवार बनता है, बहुमत के वोट मिले तो leader; term नंबर पुराने leader को रोकता है।
5. Split brain से बचाव: बहुमत (quorum), lease ख़त्म होने का इंतज़ार, fencing (epoch) और majority न मिले तो leader ख़ुद हट जाए।

---

## 🟡 Real World Example

**Kubernetes control plane** — kube-scheduler and kube-controller-manager run multiple replicas, but only one is active, elected via a `Lease` object in etcd (`--leader-elect=true`). If it dies, another takes over in seconds.

**Kafka (KRaft)** — a Raft-based controller quorum elects the active controller. Each partition also has a leader replica, and when a broker dies, partition leadership moves to in-sync replicas.

**MongoDB replica sets** — members hold elections (a Raft-inspired protocol) when the primary is unreachable. A majority is required, so a minority partition can't elect a primary, which prevents split brain.

**GitHub 2018 incident** — MySQL failover tooling elected new primaries across data centers during a partition, causing writes on both sides. It's a cautionary tale about leader election spanning sites without proper fencing.

## 🟡 Real Example Hindi में
Kubernetes में scheduler के कई replicas होते हैं पर एक ही सक्रिय — etcd के Lease से चुना गया। MongoDB replica set में बहुमत के बिना primary नहीं चुना जा सकता, इसलिए split brain नहीं होता।
GitHub 2018 में partition के दौरान दो जगह primary चुने गए और दोनों तरफ़ writes हुए — बिना fencing के leader election का सबक़।

---

## 🟠 My Stack Example

### Singleton worker via Kubernetes Lease (concept)
```
Deploy 3 replicas of "settlement-scheduler"
Each uses client-go / k8s leader-election library (Go) or a sidecar
Only the leader runs cron loops; others idle and take over on failure
```

### Node.js — leader election with etcd (election API)
```js
import { Etcd3 } from 'etcd3';
const etcd = new Etcd3({ hosts: process.env.ETCD });
const election = etcd.election('scheduler-leader', 10);          // lease TTL 10s

async function campaign() {
  const c = election.campaign(process.env.HOSTNAME);
  c.on('elected', () => { logger.info('I am leader'); startSchedulers(); });
  c.on('error', (e) => { logger.error({ e }, 'lost leadership'); stopSchedulers(); setTimeout(campaign, 1000); });
}
campaign();
```

### Simple lease-based leader with Redis (efficiency use cases)
```js
const LEADER_KEY = 'leader:report-worker', ME = `${os.hostname()}:${process.pid}`, TTL = 15_000;
let isLeader = false;

setInterval(async () => {
  try {
    if (isLeader) {
      // renew only if still mine
      const ok = await redis.eval(`if redis.call('GET',KEYS[1])==ARGV[1] then return redis.call('PEXPIRE',KEYS[1],ARGV[2]) else return 0 end`,
                                  { keys: [LEADER_KEY], arguments: [ME, String(TTL)] });
      if (!ok) { isLeader = false; onDemoted(); }
    } else if (await redis.set(LEADER_KEY, ME, { NX: true, PX: TTL })) {
      isLeader = true; onElected();
    }
  } catch { if (isLeader) { isLeader = false; onDemoted(); } }      // can't reach Redis → step down
}, TTL / 3);
```

### Postgres HA leader election (Patroni)
```yaml
# patroni.yml (each DB node)
scope: pg-prod
etcd3: { hosts: etcd1:2379,etcd2:2379,etcd3:2379 }
bootstrap: { dcs: { ttl: 30, loop_wait: 10, retry_timeout: 10, maximum_lag_on_failover: 1048576 } }
# leader key in etcd; replicas with lag > maximum_lag can't become leader
```

### Python — kazoo (ZooKeeper) election
```python
from kazoo.client import KazooClient
zk = KazooClient(hosts="zk1:2181,zk2:2181,zk3:2181"); zk.start()
election = zk.Election("/app/election", identifier=socket.gethostname())
election.run(run_as_leader)        # blocks until elected, then calls run_as_leader()
```

### Simplest in practice
```
- Managed DB (RDS/Aurora) → leader election handled for you
- One scheduler → K8s CronJob (concurrencyPolicy: Forbid) / EventBridge Scheduler
- Background "singleton" logic → Postgres advisory lock held by the leader process
```

---

## ⚫ Interview Questions + Answers

**Q1: What is leader election and why is it needed?**
A1: A distributed protocol where nodes agree on a single leader to coordinate a task (ordering writes, scheduling, assigning work) while others follow, and re-elect automatically when the leader fails. It provides the simplicity and consistency of a single decision-maker without making it a permanent single point of failure.

**Q2: How does Raft elect a leader?**
A2: All nodes start as followers expecting heartbeats. If a follower's randomized election timeout expires without a heartbeat, it becomes a candidate, increments the term, votes for itself and requests votes. Nodes vote for at most one candidate per term, and only for candidates whose log is at least as up-to-date as theirs. A candidate with a majority becomes leader and sends heartbeats. Randomized timeouts reduce split votes, and higher terms supersede stale leaders.

**Q3: How do you prevent split brain in leader election?**
A3: Require a majority quorum to elect and to keep leading, so a minority partition can't have a leader. Use leases with expiry, and have new leaders wait out the old lease. Use monotonically increasing terms or epochs as fencing tokens that resources and peers check, rejecting stale leaders' actions. Leaders step down when they lose contact with the majority. Use an odd number of voters (3 or 5), or a witness or arbiter.

**Q4: How would you implement leader election in your own application?**
A4: Don't write the consensus algorithm yourself. Use a CP coordination service: etcd or ZooKeeper election recipes, Consul sessions, Kubernetes Lease-based leader election, or a DB-based lock (Postgres advisory lock) for simpler cases. The leader renews a lease, followers watch, and on lease loss the leader stops work immediately. Use the lease's revision or epoch as a fencing token for any writes that must not come from a stale leader.

**Q5: What's the difference between a distributed lock and leader election?**
A5: They're closely related, and leader election is often built on a lock. A lock is usually short-lived, protecting one critical section or operation. Leader election grants a long-lived role ("you coordinate until you fail"), with continuous lease renewal, followers watching, and automatic succession. Both need leases, quorum-backed storage and fencing for correctness.

---

## 🔷 Trade-offs
✅ Advantages:
- Single-writer simplicity and consistency; automatic failover; clear ownership.

❌ Disadvantages:
- Leader is a throughput bottleneck; failover gap (seconds) during re-election.
- Split-brain risk if done wrong; needs a CP coordination store (more infrastructure).
- Timing/lease assumptions; flapping leaders under network instability.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Leader | Node coordinating a task | मुखिया node |
| Follower | Node following the leader | पीछे चलने वाला node |
| Candidate | Node seeking votes (Raft) | उम्मीदवार node |
| Term / Epoch | Election generation number | चुनाव की पीढ़ी संख्या |
| Election timeout | Wait before starting election | चुनाव से पहले का इंतज़ार |
| Heartbeat | Periodic "I'm alive" message | "मैं ज़िंदा हूँ" संदेश |
| Quorum | Majority needed | बहुमत |
| Split brain | Two leaders at once | एक साथ दो leaders |
| Lease | Time-limited leadership | समय-सीमित नेतृत्व |
| Fencing | Rejecting stale leaders | पुराने leader को रोकना |

---

## ⚡ 3-Line Summary
**English:**
1. Leader election picks exactly one coordinator among nodes and re-elects on failure.
2. Raft: randomized timeouts → candidates request votes → majority wins; terms fence stale leaders.
3. In apps, use etcd/ZooKeeper/K8s Lease/DB locks (don't hand-roll consensus); require quorum + fencing to avoid split brain.

**Hindi:**
1. Leader election = nodes में से एक मुखिया चुनना, गिरने पर नया।
2. Raft: random timeout → उम्मीदवार → बहुमत वोट से leader; term नंबर पुराने को रोकता है।
3. ऐप में etcd/ZooKeeper/K8s Lease इस्तेमाल करो; split brain से बचने को quorum + fencing।

---

## ➡️ Next Topic Suggestion
**90. Quorum** — Majorities keep appearing: in elections, replication, reads and writes. Next: quorum math (N, R, W), why R + W > N gives consistency, and how Cassandra and DynamoDB use it.
