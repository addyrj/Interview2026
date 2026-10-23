# 81. Failover
# हिंदी में: Failover — मुख्य सर्वर/DB/region के ख़राब होने पर अपने आप (या हाथ से) backup (standby) पर स्विच करना, ताकि सेवा चलती रहे

---

## 🔵 Simple Definition (English)
**Failover** is the process of **switching from a failed primary component to a standby/redundant one** so service continues. It applies to servers, load balancers, databases (primary → replica promotion), caches, and entire regions/data centers. **Failback** is returning to the original primary after it recovers.
Failover can be **automatic** (health checks + orchestration) or **manual** (operator decision).

## 🔵 सरल परिभाषा (Hindi)
Failover यानी मुख्य (primary) सर्वर/DB/region गिरने पर backup (standby) पर स्विच करना, ताकि यूज़र के लिए सेवा चलती रहे।
यह अपने आप भी हो सकता है (health check देखकर) या हाथ से। बाद में primary ठीक होने पर वापस जाना failback कहलाता है।

---

## 🔴 Problem it Solves
Redundancy (Topic 24) only helps if traffic and responsibility **actually move** to the healthy copy when the primary fails:
- A DB primary crash at 2 AM → without failover, writes fail until someone wakes up, restores it and updates config (hours).
- A region outage → without failover plans, the whole product is down.

Failover turns redundancy into **availability**, reducing **RTO** (recovery time) from hours to seconds or minutes.

## 🔴 यह क्यों बना? (Hindi)
Backup copy रखना काफ़ी नहीं — primary गिरने पर ट्रैफ़िक और ज़िम्मेदारी सच में backup पर जानी चाहिए।
रात 2 बजे DB गिरा तो बिना failover के कोई जागकर ठीक करे तब तक सब बंद; failover से यह समय घंटों से घटकर सेकंड/मिनट हो जाता है।

---

## 🟢 How it Works — Step by Step

### Steps in a failover

```
1. DETECT     → health checks / heartbeats fail (e.g. 3 misses × 10s)
2. DECIDE     → confirm it's really down (avoid false positives); quorum/consensus or orchestrator
3. FENCE      → make sure the OLD primary can't keep writing (avoid split brain)
4. PROMOTE    → standby becomes the new primary (DB replica promotion, VIP move)
5. REDIRECT   → clients find the new primary (DNS update, endpoint/proxy switch, LB targets)
6. RECOVER    → rebuild redundancy (new standby), investigate, maybe FAILBACK later
```

### Active-passive vs active-active

```
ACTIVE-PASSIVE (hot/warm/cold standby)
   Primary ──(replication)──► Standby (idle or read-only)
   Primary dies → promote standby
   Hot standby:  running, in sync → failover in seconds (RDS Multi-AZ: ~60–120s)
   Warm standby: running, smaller/partially synced → minutes
   Cold standby: restore from backup/IaC → hours (cheap)

ACTIVE-ACTIVE
   Node/Region A ◄──► Node/Region B — both serve traffic
   One dies → others absorb its traffic (no promotion step) → near-instant
   Needs capacity headroom (each must handle the extra load) and conflict handling for writes
```

### Split brain — the dangerous failure

```
Network partition between Primary and Standby (both alive!)
Standby: "primary is dead" → promotes itself
Now TWO primaries accept writes → divergent data → corruption ❌

Prevention:
  - Quorum/consensus: only promote if a MAJORITY agrees (3+ nodes or witness; Patroni+etcd, Raft)
  - Fencing: STONITH ("shoot the other node in the head"), revoke old primary's access
    (block its network, storage, or use fencing tokens / epoch numbers so stale leader's writes are rejected)
  - Old primary demotes itself if it loses contact with the quorum
```

### Data loss during failover (RPO)

```
Async replication: standby may be seconds behind → acked writes since last replication LOST
Sync replication:  no acked-write loss, but higher write latency
Know your RPO (Recovery Point Objective) and RTO (Recovery Time Objective) — Topic 105
```

### How clients follow the new primary

```
DNS endpoint     → RDS endpoint CNAME flips to new primary (low TTL); apps must reconnect
Virtual IP (VIP) → keepalived moves the IP to the standby (on-prem)
Proxy/pooler     → PgBouncer/HAProxy/RDS Proxy points to new primary; app keeps same address
Service discovery→ Consul/K8s Service updates endpoints
Client libraries → MongoDB/Redis Sentinel/Cluster-aware drivers discover new primary automatically
App MUST: retry on connection errors, re-resolve DNS (don't cache forever), refresh pools
```

### Regional failover
```
Route 53 health checks + failover routing: primary region unhealthy → DNS answers secondary
Requirements: data replicated cross-region (Aurora Global DB, DynamoDB Global Tables, S3 CRR),
secondary has capacity (pre-scaled or quick scale-up), config/secrets present, tested runbooks
```

### Test failovers regularly
```
"A failover you haven't tested doesn't work." → game days, chaos engineering (Topic 108)
RDS: "Reboot with failover" in staging/prod off-peak; measure actual RTO and app behaviour
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहचानो (health check फ़ेल) → पक्का करो कि सच में डाउन है → पुराने primary को रोको (fencing) → standby को primary बनाओ → clients को नए primary पर भेजो।
2. Active-passive: standby इंतज़ार में, primary गिरे तो promote; active-active: दोनों चालू, एक गिरे तो दूसरा पूरा बोझ उठाए।
3. Split brain सबसे ख़तरनाक: नेटवर्क टूटने पर दोनों ख़ुद को primary समझें — quorum और fencing से रोको।
4. Async replication में failover पर पिछले कुछ सेकंड का डेटा जा सकता है (RPO); sync में नहीं, पर धीमा।
5. ऐप को connection error पर retry और DNS दोबारा resolve करना चाहिए; failover को नियमित रूप से टेस्ट करो।

---

## 🟡 Real World Example

**AWS RDS Multi-AZ** — a synchronous standby in another AZ. On primary failure, AWS flips the DNS endpoint to the standby, typically within 60–120 seconds. Apps that cache DNS or don't reconnect see longer outages. That's the classic hot-standby failover.

**GitHub (Oct 2018)** — a 43-second network partition between US East data centers led Orchestrator (MySQL failover tool) to promote primaries in the West Coast data center. Writes then happened in both places, and reconciling the divergent data caused about 24 hours of degraded service. It's a famous split-brain/cross-region failover lesson.

**Netflix regional evacuation** — Netflix regularly practices failing over an entire AWS region, shifting all traffic to the remaining regions in minutes (active-active), as part of chaos engineering.

**Banks & UPI** — run DR sites in another city (e.g. Mumbai primary, Chennai/Hyderabad DR) with mandated periodic DR drills by RBI.

## 🟡 Real Example Hindi में
AWS RDS Multi-AZ में primary गिरने पर DNS standby पर पलट जाता है, 1-2 मिनट में। GitHub 2018 में 43 सेकंड के नेटवर्क टूटने पर दूसरी जगह primary बन गया — दोनों जगह writes हुए और ठीक करने में 24 घंटे लगे (split brain का सबक़)।
Netflix पूरा AWS region खाली करने की प्रैक्टिस करता है; बैंक RBI के नियम से DR site पर नियमित drill करते हैं।

---

## 🟠 My Stack Example

### App must survive DB failover (Node + pg)
```js
const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,          // RDS endpoint (DNS), never an IP
  connectionTimeoutMillis: 3000,
  maxLifetimeSeconds: 300,                              // recycle connections → pick up new primary
});
pool.on('error', (e) => logger.warn({ e }, 'idle client error (failover?)'));

// retry transient connection errors on idempotent operations
const RETRYABLE = new Set(['ECONNRESET', 'ECONNREFUSED', '57P01' /* admin_shutdown */, '08006', '25006' /* read-only (old primary) */]);
export const query = (text, params) =>
  retry(() => pool.query(text, params), { attempts: 5, baseMs: 500, isRetryable: (e) => RETRYABLE.has(e.code) });
// Node caches DNS per OS resolver; avoid custom DNS caching with long TTLs.
```

### Redis Sentinel / ElastiCache failover-aware client
```js
import Redis from 'ioredis';
const redis = new Redis({
  sentinels: [{ host: 'sentinel-1', port: 26379 }, { host: 'sentinel-2', port: 26379 }, { host: 'sentinel-3', port: 26379 }],
  name: 'mymaster',                // client asks sentinels who the current master is
  enableOfflineQueue: false,
  retryStrategy: (times) => Math.min(times * 200, 2000),
});
// ElastiCache: use the primary endpoint (DNS flips on failover) + reconnect logic
```

### Self-managed Postgres HA: Patroni (consensus-based, avoids split brain)
```
3 Postgres nodes + etcd cluster (Raft)
Patroni on each node holds a leader lock in etcd (TTL 30s)
Leader dies → lock expires → a replica with least lag acquires lock → promotes
Old leader that loses etcd contact demotes itself (fencing)
HAProxy/PgBouncer routes to whoever holds the leader key (REST check /primary)
```

### Regional failover with Route 53 (Terraform-ish)
```hcl
resource "aws_route53_health_check" "api_mumbai" { fqdn = "api-ap-south-1.myapp.com"  type = "HTTPS"  resource_path = "/health/ready"  failure_threshold = 3 }

resource "aws_route53_record" "api_primary" {
  zone_id = var.zone  name = "api.myapp.com"  type = "A"
  set_identifier = "primary"  failover_routing_policy { type = "PRIMARY" }
  health_check_id = aws_route53_health_check.api_mumbai.id
  alias { name = aws_lb.mumbai.dns_name  zone_id = aws_lb.mumbai.zone_id  evaluate_target_health = true }
}
resource "aws_route53_record" "api_secondary" {
  zone_id = var.zone  name = "api.myapp.com"  type = "A"
  set_identifier = "secondary"  failover_routing_policy { type = "SECONDARY" }
  alias { name = aws_lb.singapore.dns_name  zone_id = aws_lb.singapore.zone_id  evaluate_target_health = true }
}
```

### Docker on a VPS — cheap warm standby
```
Primary VPS + standby VPS with Postgres streaming replica + same Docker images
Failover runbook (scripted): promote replica (pg_ctl promote / SELECT pg_promote()),
switch DNS (Cloudflare API, TTL 60s) → start api containers on standby → verify
Practice it monthly.
```

### Mobile clients during failover
```
Short blips → React Query retries with backoff; show cached data
Writes → idempotency keys so retries during failover don't duplicate orders
```

---

## ⚫ Interview Questions + Answers

**Q1: What is failover and what are its steps?**
A1: Switching service from a failed primary component to a standby. Steps: detect the failure (health checks or heartbeats), confirm it to avoid false positives (quorum), fence the old primary so it can't keep acting, promote the standby, redirect clients (DNS, VIP, proxy, discovery), then restore redundancy and investigate, possibly failing back later.

**Q2: Active-passive vs active-active — trade-offs?**
A2: Active-passive keeps standby resources idle or read-only. It's simpler, especially for databases (one writer), but failover takes time (promotion plus redirection) and the standby must be kept healthy and tested. Active-active has all nodes or regions serving traffic, so failover is near-instant and capacity is used, but each must have headroom to absorb the failed one's load, and multi-writer setups need conflict resolution or partitioned ownership.

**Q3: What is split brain and how do you prevent it?**
A3: When a network partition causes two nodes to both believe they're the primary and both accept writes, the data diverges. Prevent it with quorum-based leader election (only a majority side can elect a leader: Raft, Patroni with etcd, an odd number of nodes or a witness), fencing (STONITH, revoking storage or network access, or fencing tokens or epochs so a stale leader's writes are rejected), and self-demotion when a node loses quorum contact.

**Q4: Why do applications sometimes stay down longer than the DB failover itself?**
A4: They cache DNS or connection targets and keep talking to the old primary (or get read-only errors). Connection pools hold dead connections without health checks. There's no retry on transient connection errors, or long connect timeouts. And there are thundering-herd reconnects. Fixes: use endpoint DNS with short TTLs and no long-lived DNS caching, pool connection recycling and validation, retries with backoff for idempotent operations, failover-aware drivers, and failover testing.

**Q5: How would you design regional failover for a critical API?**
A5: Deploy the stack in two regions (active-active, or warm standby for cost). Replicate data cross-region (Aurora Global Database, DynamoDB Global Tables, S3 CRR), knowing that async replication means a nonzero RPO. Route via Route 53 latency or failover routing with health checks, or Global Accelerator. Keep infrastructure as code so both regions are identical, pre-provision or quickly scale capacity, keep secrets and config replicated, define RTO and RPO, write runbooks, and run regular regional evacuation drills.

---

## 🔷 Trade-offs
✅ Advantages:
- Converts redundancy into availability; reduces RTO dramatically; automatic recovery at 2 AM.

❌ Disadvantages:
- Standby cost; complexity; risk of split brain and data loss (async).
- False-positive failovers cause disruption; failback is often harder than failover.
- Must be tested regularly or it fails when needed.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Failover | Switch to standby on failure | ख़राबी पर backup पर स्विच |
| Failback | Return to original primary | वापस मूल पर जाना |
| Standby (hot/warm/cold) | Backup readiness levels | backup की तैयारी का स्तर |
| Promotion | Replica becomes primary | replica को primary बनाना |
| Split brain | Two primaries at once | एक साथ दो primary |
| Fencing / STONITH | Stopping the old primary | पुराने primary को रोकना |
| Quorum | Majority agreement | बहुमत की सहमति |
| RTO | Time to recover | ठीक होने का समय |
| RPO | Max data loss window | कितना डेटा खो सकता है |
| VIP | Floating virtual IP | खिसकने वाला IP |

---

## ⚡ 3-Line Summary
**English:**
1. Failover = detect → confirm → fence → promote standby → redirect clients → restore redundancy.
2. Active-passive (simpler, slower) vs active-active (instant, needs headroom/conflict handling); prevent split brain with quorum + fencing.
3. Apps must reconnect/retry and re-resolve endpoints; know RTO/RPO; test failovers regularly.

**Hindi:**
1. Failover = पहचानो → पक्का करो → पुराने को रोको → standby को primary बनाओ → clients भेजो।
2. Active-passive (आसान, धीमा) बनाम active-active (तुरंत, ज़्यादा क्षमता चाहिए); split brain से quorum + fencing।
3. ऐप reconnect/retry करे; RTO/RPO जानो; failover नियमित टेस्ट करो।

---

## ➡️ Next Topic Suggestion
**82. Message Queues** — Many resilience patterns rely on async communication. Next: message queues, how producers and consumers decouple, delivery guarantees, and when to use a queue instead of a direct API call.
