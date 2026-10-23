# 19. Availability
# हिंदी में: Availability — सिस्टम कितने प्रतिशत समय चालू और इस्तेमाल लायक रहता है (uptime)

---

## 🔵 Simple Definition (English)
**Availability** is the percentage of time a system is **up and working correctly** for users.
`Availability = Uptime / (Uptime + Downtime)`. It's usually expressed in **"nines"**: 99.9% ("three nines"), 99.99% ("four nines").

## 🔵 सरल परिभाषा (Hindi)
Availability यानी सिस्टम कितने % समय चालू रहता है और यूज़र उसे इस्तेमाल कर पाते हैं।
99.9% का मतलब साल में लगभग 8.7 घंटे डाउन रह सकता है; 99.99% का मतलब सिर्फ़ ~52 मिनट।

---

## 🔴 Problem it Solves
Everything fails eventually: servers crash, disks die, AZs lose power, deployments have bugs, certificates expire, DNS breaks.
- **Downtime = lost money + lost trust.** Amazon loses millions per hour of downtime; a payment app being down during Diwali sends users to competitors.
- Availability gives a **measurable target** so teams can decide **how much redundancy to pay for**. Going from 99.9% to 99.99% costs a lot more; is it worth it for this feature?

## 🔴 यह क्यों बना? (Hindi)
सर्वर, डिस्क, डेटा सेंटर, deploy — सब कभी न कभी फ़ेल होते हैं, और downtime = पैसे और भरोसे का नुकसान।
Availability एक नापने लायक लक्ष्य देती है, ताकि तय कर सकें कि कितना backup/redundancy ख़र्च करना सही है।

---

## 🟢 How it Works — Step by Step

### The nines table (memorize roughly)

```
┌──────────────┬──────────────────┬────────────────┬──────────────┐
│ Availability │ Downtime / year  │ / month        │ / day        │
├──────────────┼──────────────────┼────────────────┼──────────────┤
│ 99%          │ 3.65 days        │ 7.3 hours      │ 14.4 min     │
│ 99.9%        │ 8.76 hours       │ 43.8 min       │ 1.44 min     │
│ 99.95%       │ 4.38 hours       │ 21.9 min       │ 43 s         │
│ 99.99%       │ 52.6 min         │ 4.38 min       │ 8.6 s        │
│ 99.999%      │ 5.26 min         │ 26 s           │ 0.86 s       │
└──────────────┴──────────────────┴────────────────┴──────────────┘
Each extra nine ≈ 10× less downtime ≈ much higher cost & effort.
```

### Availability of components in SERIES (chain) — multiplies DOWN

```
Client → LB (99.99%) → App (99.9%) → DB (99.95%)

Total = 0.9999 × 0.999 × 0.9995 = 0.9984 → 99.84%   (worse than each part!)
More dependencies in a chain → lower availability.
```

### Availability of components in PARALLEL (redundancy) — goes UP

```
         ┌─► App A (99%) ─┐
LB ──────┤                ├──►
         └─► App B (99%) ─┘
System fails only if BOTH fail:
Total = 1 − (1 − 0.99)² = 1 − 0.0001 = 99.99%

Three copies at 99% → 1 − 0.01³ = 99.9999%
(assumes failures are independent → put them in different AZs!)
```

### MTBF and MTTR

```
MTBF = Mean Time Between Failures   (how often it breaks)
MTTR = Mean Time To Recovery        (how fast you fix it)

Availability = MTBF / (MTBF + MTTR)

Two ways to improve:
  1. Fail less often  (testing, redundancy, good hardware)
  2. Recover faster   (auto-failover, health checks, fast rollback, alerts, runbooks)
In practice, reducing MTTR is often cheaper and more effective.
```

### Building highly available systems — the checklist

```
✓ Redundancy at every tier       → ≥ 2 instances, multiple AZs, DB standby (Multi-AZ)
✓ No single point of failure     → LB, DB, cache, DNS, even your CI deploy key (Topic 24)
✓ Health checks + auto-replace   → LB removes bad instances; ASG/K8s replaces them
✓ Automatic failover             → DB primary → standby (Topic 81)
✓ Graceful degradation           → feature off instead of site down (Topic 77)
✓ Timeouts, retries, circuit breakers (Topics 73–79)
✓ Safe deploys                   → rolling/blue-green/canary + fast rollback
✓ Backups + tested restore       → Disaster recovery (Topic 105)
✓ Monitoring + alerting + on-call → detect in seconds, not when users tweet
✓ Multi-region                   → for 99.99%+ (Topic 106)
```

### Availability vs related terms

```
Availability → "Is it up?"                     (uptime %)
Reliability  → "Does it work correctly over time?" (no wrong results, data loss)
Durability   → "Will my data survive?"         (S3: 99.999999999% — 11 nines — of durability)
Fault tolerance → keeps working DURING a failure (no visible downtime)
High availability → minimizes downtime, maybe brief blip during failover
```

## 🟢 कैसे काम करता है? (Hindi)
1. Availability = चालू समय / कुल समय; इसे "nines" में बताते हैं (99.9%, 99.99%)।
2. एक के बाद एक जुड़े components (series) की availability गुणा होकर घटती है।
3. एक जैसे components साथ-साथ (parallel/backup) रखने से availability बढ़ती है — दोनों एक साथ गिरें तभी सिस्टम गिरेगा।
4. सुधार के दो रास्ते: कम फ़ेल हो (MTBF बढ़ाओ) या जल्दी ठीक हो (MTTR घटाओ)।
5. हर परत पर कम से कम 2 copies, अलग-अलग AZ में, health check, auto-failover और अच्छी monitoring।

---

## 🟡 Real World Example

**AWS us-east-1 outages (2017 S3, 2021)** — a typo during S3 maintenance in 2017 took down S3 in us-east-1 for ~4 hours, breaking thousands of websites (Slack, Trello, Quora). Companies that were **multi-region** stayed up. Lesson: even AWS services fail; design for it.

**UPI / banks** — NPCI publishes bank "technical decline" rates. Banks with frequent downtime get pressure from regulators. Payment apps show "Bank X is facing issues, use another account", which is graceful degradation at the business level.

**Google SRE** — Google sets an availability **SLO** for each service (e.g. 99.95%), and the leftover 0.05% is the **error budget** (Topic 104). If a team burns the budget, feature launches stop until reliability improves.

**CrowdStrike (July 2024)** — a bad update crashed ~8.5 million Windows machines worldwide (airlines, banks, hospitals). A single dependency with no staged rollout caused a global availability event. Canary deploys matter.

## 🟡 Real Example Hindi में
2017 में AWS S3 पर एक typo से 4 घंटे तक हज़ारों वेबसाइट्स डाउन रहीं — जिनका सिस्टम कई regions में था, वो बच गए।
2024 में CrowdStrike के एक ग़लत अपडेट से दुनिया भर में 85 लाख कंप्यूटर बंद हो गए — इसलिए अपडेट हमेशा धीरे-धीरे (canary) रोलआउट करो।

---

## 🟠 My Stack Example

### From single VPS (≈99%) to highly available AWS (≈99.95%+)

```
❌ Single VPS (everything on one box)
   Nginx + Node + Postgres + Redis on one machine
   → any reboot/disk issue = full outage

✅ HA on AWS (ap-south-1, 3 AZs)
   Route 53 (health-checked)
        │
   ALB (multi-AZ by default)
        │
   ECS/EKS: api tasks in 1a, 1b, 1c (min 2–3)
        │
   RDS Postgres Multi-AZ (sync standby, auto failover ~60s)
   ElastiCache Redis with replica + auto-failover
   S3 for files (11 nines durability)
   SQS for async jobs (managed, multi-AZ)
```

### Health checks that mean something
```js
// Liveness: process is alive
app.get('/health/live', (req, res) => res.sendStatus(200));

// Readiness: can serve traffic (dependencies OK)
app.get('/health/ready', async (req, res) => {
  try {
    await Promise.all([pool.query('SELECT 1'), redis.ping()]);
    res.sendStatus(200);
  } catch {
    res.sendStatus(503);          // LB stops sending traffic here
  }
});
```

### Zero-downtime deploys (deploys are the #1 cause of downtime)
```yaml
# ECS / K8s rolling update: never drop below 100% capacity
deployment:
  minimumHealthyPercent: 100
  maximumPercent: 200
# + graceful SIGTERM handling (Topic 16) + automatic rollback on failed health checks
```
```bash
# Docker Compose on a VPS: at least run 2 replicas so restarts aren't outages
docker compose up -d --scale api=2 --no-deps api
```

### Measure it: uptime monitoring
```
External checks every 30–60s from multiple locations: UptimeRobot, Better Stack, Pingdom,
Route 53 health checks, CloudWatch Synthetics.
Track: availability % per month = successful checks / total checks
Better: availability = (good requests / total requests) from your LB/APM logs (user-centric)
```

### Client-side resilience (mobile & web)
```ts
// React Native: retries with backoff for idempotent GETs, offline cache, friendly error state
const { data, error } = useQuery({
  queryKey: ['menu', id], queryFn: () => getMenu(id),
  retry: 3, retryDelay: (n) => Math.min(1000 * 2 ** n, 8000),
  staleTime: 60_000,             // show cached menu if server is briefly down
});
if (error && !data) return <ErrorState onRetry={refetch} message="We're having trouble. Please try again." />;
```

---

## ⚫ Interview Questions + Answers

**Q1: What does 99.99% availability mean in downtime?**
A1: About 52.6 minutes per year, ~4.4 minutes per month, or ~8.6 seconds per day. 99.9% allows about 8.76 hours per year (~43.8 minutes per month). Each additional nine is roughly 10× less downtime and significantly higher cost.

**Q2: How do you calculate availability of components in series and in parallel?**
A2: In series (all must work), multiply the availabilities: 0.999 × 0.999 = 0.998. In parallel (any one is enough), use 1 − product of the failure probabilities: two components at 99% give 1 − 0.01² = 99.99%. This is why long synchronous dependency chains hurt availability and redundancy helps, as long as failures are independent (different AZs, hardware, deploy times).

**Q3: How would you design a system for high availability?**
A3: Remove single points of failure with redundancy at every layer: multiple app instances across AZs behind a load balancer, a DB with synchronous standby and automatic failover, a replicated cache, and managed queues. Add health checks with auto-replacement, timeouts, retries, circuit breakers, graceful degradation for non-critical dependencies, zero-downtime deploys (rolling or canary with auto-rollback), and backups with tested restores. Use monitoring and alerting to reduce MTTR, and multi-region deployment for the highest targets.

**Q4: What's the difference between availability, reliability and durability?**
A4: Availability: is the system reachable and responding (uptime). Reliability: does it work correctly and consistently over time, with no wrong results or data corruption. Durability: once data is stored, will it survive (S3 is designed for 11 nines of durability through replication across facilities). A system can be available but unreliable (returns errors or wrong data), or durable but temporarily unavailable.

**Q5: Why might adding a cache or a new microservice reduce availability?**
A5: Each new synchronous dependency in the request path adds a component in series, and its availability multiplies into the total. If the cache is required (requests fail when Redis is down), availability drops. Mitigate by making the dependency optional (fall back to the DB if the cache is down), making it redundant (replicas, cluster), using async communication, and setting timeouts and circuit breakers so its failure doesn't cascade.

---

## 🔷 Trade-offs
✅ Higher availability:
- Fewer outages → revenue, trust, SLA compliance.

❌ Costs:
- Redundancy = 2–3× infrastructure cost.
- Complexity: failover logic, data replication, consistency trade-offs (CAP, Topic 65).
- Multi-region active-active is very expensive and hard.
- Choose target per feature: payments 99.99%, recommendations 99.5% is fine.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Availability | % time system is usable | सिस्टम चालू रहने का % |
| Uptime / Downtime | Time working / not working | चालू / बंद समय |
| Nines | 99.9%, 99.99% notation | कितने 9 |
| Redundancy | Extra copies of components | अतिरिक्त backup copies |
| MTBF | Mean time between failures | दो ख़राबियों के बीच औसत समय |
| MTTR | Mean time to recovery | ठीक होने का औसत समय |
| Failover | Switching to backup on failure | ख़राबी पर backup पर जाना |
| Durability | Data won't be lost | डेटा सुरक्षित रहना |
| Multi-AZ | Spread across data centers in region | कई डेटा सेंटर में फैलाव |

---

## ⚡ 3-Line Summary
**English:**
1. Availability = uptime %; 99.9% ≈ 8.8 h/year down, 99.99% ≈ 53 min/year.
2. Series dependencies multiply availability down; parallel redundancy pushes it up.
3. Achieve HA with redundancy across AZs, health checks, auto-failover, safe deploys, and low MTTR.

**Hindi:**
1. Availability = चालू रहने का %; 99.99% = साल में सिर्फ़ ~53 मिनट डाउन।
2. Series में जुड़े हिस्से availability घटाते हैं; parallel backup बढ़ाते हैं।
3. HA के लिए: कई AZ में copies, health check, auto-failover, सुरक्षित deploy, जल्दी recovery।

---

## ➡️ Next Topic Suggestion
**20. Bandwidth** — The last of the core performance metrics. Next: bandwidth, the maximum data a network link can carry, how it differs from throughput and latency, and why it matters for video, images, and mobile users on slow networks.
