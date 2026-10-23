# 106. Multi-Region Architecture
# हिंदी में: Multi-Region Architecture — ऐप को दुनिया/देश के कई cloud regions में एक साथ चलाना, ताकि पूरा region गिरने पर भी सेवा चले और दूर के यूज़र्स को कम latency मिले

---

## 🔵 Simple Definition (English)
A **multi-region architecture** deploys an application across **two or more geographic cloud regions** (e.g. AWS `ap-south-1` Mumbai + `ap-south-2` Hyderabad, or Mumbai + Singapore + Frankfurt). Goals:
1. **Resilience:** survive a full region outage (DR, Topic 105).
2. **Latency:** serve users from the nearest region.
3. **Compliance:** keep data in specific countries (data residency).
Patterns: **active-passive** (one region serves, the other stands by) and **active-active** (all regions serve traffic), with data either **replicated**, **partitioned by geography (home region)**, or stored in **globally distributed databases**.

## 🔵 सरल परिभाषा (Hindi)
Multi-region में ऐप कई जगहों (जैसे Mumbai और Hyderabad, या Mumbai और Singapore) पर एक साथ चलता है।
फ़ायदे: पूरा region गिरे तो भी सेवा चले, दूर के यूज़र्स को पास का सर्वर मिले, और क़ानून के हिसाब से डेटा सही देश में रहे। दो तरीके: active-passive (एक चलता, दूसरा इंतज़ार में) और active-active (सब चलते)।

---

## 🔴 Problem it Solves
Single-region (even multi-AZ) systems are exposed to:
- **Regional outages:** AWS us-east-1 has had multiple multi-hour, region-wide incidents (2017 S3, 2020 Kinesis, 2021 network, 2023 Lambda). Everything in that region was affected.
- **Latency for distant users:** Mumbai → US users ~200 ms RTT per round trip; a page needing 10 round trips feels slow.
- **Regulations:** RBI payment data localization (India), GDPR expectations (EU), data sovereignty in some countries.
- **Scale ceilings** of a single region (capacity limits for some instance types during massive events).

## 🔴 यह क्यों बना? (Hindi)
एक region (कई AZ के साथ भी) पूरे region के outage से नहीं बचता — AWS us-east-1 कई बार घंटों तक डाउन रहा। दूर के यूज़र्स के लिए हर round trip 200 ms। RBI और GDPR जैसे नियम डेटा को ख़ास देश में रखने को कहते हैं।
Multi-region इन सबका हल है — पर महँगा और जटिल।

---

## 🟢 How it Works — Step by Step

### Pattern 1: Active-passive (simplest multi-region)

```
          Route 53 failover (health checks)
                 │ (all traffic)
        ┌────────▼────────┐                ┌──────────────────┐
        │ Region A (prim) │ ──async repl──►│ Region B (standby)│
        │ app + DB primary│                │ app (scaled down) │
        │                 │                │ DB replica         │
        └─────────────────┘                └──────────────────┘
Region A fails → promote B's DB replica → scale up B → DNS points to B
✅ simpler data model (single writer)   ❌ RTO minutes, RPO = replication lag, idle cost
```

### Pattern 2: Active-active — read local, write to one primary

```
        Latency-based routing (Route 53 / Global Accelerator / Cloudflare)
          ┌──────────────────────────┴──────────────────────────┐
   ┌──────▼──────┐                                       ┌──────▼──────┐
   │ Region A    │                                       │ Region B    │
   │ app (serve) │                                       │ app (serve) │
   │ DB PRIMARY  │══════════ async replication ═════════►│ DB replica  │
   └─────────────┘ ◄──── writes from B forwarded to A ───└─────────────┘
Reads local & fast everywhere; writes cross-region to primary (higher write latency).
Common with Aurora Global Database (write forwarding), MongoDB with regional secondaries.
```

### Pattern 3: Active-active — geo-partitioned "home region" ⭐

```
Each user/tenant has a HOME region where their data lives and their writes go.
 India users → Mumbai (data stays in India ✔ compliance)
 EU users    → Frankfurt
 Global router (edge/gateway) looks up user → home region → routes there
✅ local reads+writes, no conflicts, compliance  ❌ cross-region interactions (an India user messaging
an EU user) need async replication or global services; failover of a region's users is complex
```

### Pattern 4: Active-active — multi-writer (hardest)

```
Writes accepted in EVERY region → replicated to others
Need conflict resolution: last-writer-wins (DynamoDB Global Tables), CRDTs, app-level merges,
or a globally consistent DB (Spanner, CockroachDB, YugabyteDB) paying cross-region latency on writes.
Use for: data that tolerates eventual consistency (profiles, carts, sessions) or with distributed SQL.
```

### What must be multi-region (checklist)
```
✓ Compute (containers/Lambda) + autoscaling in each region
✓ Data stores: replication strategy per store (DB, Redis, S3 CRR, search index rebuildable)
✓ Global routing: latency/geo DNS, health checks, anycast (Global Accelerator/Cloudflare)
✓ Container images, secrets, config, feature flags replicated
✓ Async messaging: regional Kafka/SQS + cross-region replication where needed (MirrorMaker 2)
✓ Observability per region + global view
✓ IaC identical across regions; deploy region-by-region (bad deploy shouldn't hit all at once)
✓ Avoid hidden single-region dependencies (auth provider, a global config service, CI/CD, DNS in one place)
✓ Regular regional evacuation drills
```

### Costs & complexity
```
- 2× (or more) infrastructure; cross-region data transfer charges
- Data consistency & conflict handling; replication lag → stale reads in other regions
- Testing and debugging get harder; operational maturity required
→ Many companies do: multi-AZ in one region + backups/pilot light in a 2nd region,
  and go active-active only for Tier-0 services or very large global user bases.
```

## 🟢 कैसे काम करता है? (Hindi)
1. Active-passive: एक region सब ट्रैफ़िक लेता है, दूसरे में DB replica और छोटा ऐप; गिरने पर promote करके DNS बदलो।
2. Active-active (reads local): हर region पढ़ता है, पर writes एक primary region में जाते हैं।
3. Home region: हर यूज़र का डेटा उसके region में (भारत के यूज़र Mumbai में — RBI नियम भी पूरा); router यूज़र को सही region भेजता है।
4. Multi-writer सबसे कठिन: हर region में writes, conflicts के लिए LWW/CRDT या Spanner/CockroachDB जैसे DB।
5. Checklist: compute, डेटा replication, global routing, images/secrets, region-दर-region deploy, और regional drill। ख़र्च 2 गुना+ और जटिलता बहुत।

---

## 🟡 Real World Example

**Netflix** — runs active-active across multiple AWS regions. In "regional evacuation" exercises, it shifts all traffic out of a region in minutes, and Cassandra replicates data across regions. This let Netflix stay up during several AWS regional outages that took down other services.

**Slack / Atlassian / Stripe** — use cell-based, multi-region designs. Stripe routes API traffic to multiple regions and invests heavily in data consistency for payments.

**Indian payments (RBI data localization, 2018)** — global companies (Visa, Mastercard, Google Pay, WhatsApp Pay) had to store Indian payment data only in India. Multi-region within India (e.g. Mumbai + Hyderabad on AWS, or Mumbai + Delhi on GCP) became the standard resilience pattern.

**Uber** — multi-region active-active with data centers in different geographies, routing trips to the region nearest the city and handling failover so trips continue.

## 🟡 Real Example Hindi में
Netflix कई AWS regions में active-active चलता है — कुछ मिनटों में पूरा region ख़ाली करने का अभ्यास करता है, इसलिए AWS outage में भी चलता रहा।
RBI के 2018 के नियम से Visa, Google Pay जैसी कंपनियों को भारतीय पेमेंट डेटा भारत में ही रखना पड़ा — इसलिए Mumbai + Hyderabad जैसा multi-region भारत में आम है।

---

## 🟠 My Stack Example

### Practical setup for an Indian startup (step up gradually)
```
Stage 1: ap-south-1 (Mumbai), 3 AZs, RDS Multi-AZ, backups copied to ap-south-2 (Hyderabad)
Stage 2: Pilot light in ap-south-2: Aurora Global DB secondary, ECR replication, Terraform ready
Stage 3: Warm standby: small ECS service running in ap-south-2, Route 53 failover routing
Stage 4: Active-active reads: latency routing; writes to primary via Aurora write forwarding
```

### Route 53 latency routing (two active regions)
```hcl
resource "aws_route53_record" "api_mumbai" {
  zone_id = var.zone  name = "api.myapp.com"  type = "A"
  set_identifier = "ap-south-1"  latency_routing_policy { region = "ap-south-1" }
  health_check_id = aws_route53_health_check.mumbai.id
  alias { name = aws_lb.mumbai.dns_name  zone_id = aws_lb.mumbai.zone_id  evaluate_target_health = true }
}
resource "aws_route53_record" "api_hyd" {
  zone_id = var.zone  name = "api.myapp.com"  type = "A"
  set_identifier = "ap-south-2"  latency_routing_policy { region = "ap-south-2" }
  health_check_id = aws_route53_health_check.hyd.id
  alias { name = aws_lb.hyd.dns_name  zone_id = aws_lb.hyd.zone_id  evaluate_target_health = true }
}
```

### App: region-aware reads and writes (Node)
```js
const REGION = process.env.AWS_REGION;
const writer = new pg.Pool({ connectionString: process.env.GLOBAL_WRITER_URL });   // primary region cluster
const reader = new pg.Pool({ connectionString: process.env.LOCAL_READER_URL });    // local replica

app.get('/api/v1/menu/:rid', async (req, res) => res.json(await reader.query(/* ... */).then(r => r.rows)));
app.post('/api/v1/orders', authenticate, async (req, res) => {
  const order = await writer.query(/* ... */);     // cross-region write if we're the secondary region
  res.set('X-Served-Region', REGION).status(201).json(order.rows[0]);
});
```

### Home-region routing at the edge (Cloudflare Worker / Lambda@Edge idea)
```js
export default {
  async fetch(req) {
    const userId = await userIdFromToken(req);
    const home = (await KV.get(`home:${userId}`)) ?? 'ap-south-1';     // e.g. EU users → eu-central-1
    const origin = { 'ap-south-1': 'https://in.api.myapp.com', 'eu-central-1': 'https://eu.api.myapp.com' }[home];
    return fetch(new Request(origin + new URL(req.url).pathname, req));
  },
};
```

### DynamoDB Global Tables for multi-writer session/cart data
```
Table "sessions" replicated to ap-south-1 + ap-southeast-1; last-writer-wins; ~1s replication.
Good for: sessions, carts, preferences. NOT for: wallet balances.
```

### Deploy region by region (blast-radius control)
```yaml
# GitHub Actions: deploy to Hyderabad first (smaller traffic), bake 30 min with SLO check, then Mumbai
jobs:
  deploy-hyd:    { uses: ./.github/workflows/deploy.yml, with: { region: ap-south-2 } }
  bake:          { needs: deploy-hyd, runs-on: ubuntu-latest, steps: [ { run: ./scripts/check-slo.sh ap-south-2 30m } ] }
  deploy-mumbai: { needs: bake, uses: ./.github/workflows/deploy.yml, with: { region: ap-south-1 } }
```

### Mobile clients
```
- Single API hostname with latency DNS; app shouldn't hardcode region endpoints
- Remote config can steer clients during incidents
- Retry with idempotency keys handles failover blips safely
```

---

## ⚫ Interview Questions + Answers

**Q1: Why go multi-region, and when is it not worth it?**
A1: For resilience against full-region outages, lower latency for geographically distributed users, data residency compliance, and capacity beyond one region. It's not worth it when users are concentrated near one region, the availability target is achievable with multi-AZ plus backups, or the team lacks the operational maturity. It roughly doubles infrastructure, adds cross-region data transfer costs, and introduces consistency complexity. Many companies use one region with multi-AZ plus pilot-light DR.

**Q2: Active-passive vs active-active multi-region?**
A2: Active-passive: one region serves all traffic while another holds replicated data and minimal or warm infrastructure. On failure you promote and switch, so RTO is minutes and RPO equals the replication lag, with a single-writer data model. Active-active: multiple regions serve traffic simultaneously, giving lower latency and near-instant failover with capacity in use, but writes need a strategy (a single primary with write forwarding, geo-partitioned home regions, or multi-writer with conflict resolution or distributed SQL).

**Q3: How do you handle data in an active-active setup?**
A3: Choose per data type. Read-mostly data is replicated to all regions. User-owned data is partitioned by a home region (writes are local, with no conflicts, which helps compliance). Data needing global strong consistency uses a distributed SQL database (Spanner, CockroachDB), accepting cross-region write latency. Data tolerant of eventual consistency (sessions, carts, preferences) uses multi-writer replication with LWW or CRDTs. Search and caches are rebuilt per region from events.

**Q4: What hidden single-region dependencies break multi-region designs?**
A4: Centralized auth or identity providers, a single global config or feature-flag service, CI/CD and container registries in one region, secrets stored in one region, DNS managed by a single provider or account, monitoring that lives only in the failed region, third-party APIs with single endpoints, cron or leader jobs pinned to one region, and global databases whose primary sits in the failed region. Audit dependencies and run regional evacuation drills to find them.

**Q5: How would you route users to the right region?**
A5: Latency-based or geolocation DNS routing with health checks (Route 53, Cloud DNS), or anycast-based global load balancers (AWS Global Accelerator, Cloudflare, GCP global LB) that direct users to the nearest healthy region. For home-region data designs, an edge layer or gateway maps the user or tenant to their home region and forwards the request there. Clients use a single hostname, and failover happens by health checks removing the unhealthy region.

---

## 🔷 Trade-offs
✅ Advantages:
- Survives regional disasters; lower global latency; data residency compliance; more capacity.

❌ Disadvantages:
- High cost (duplicate infra, data transfer); complex data consistency & conflict handling.
- Harder testing, deploys, debugging; hidden single-region dependencies.
- Replication lag → stale reads; cross-region writes are slow.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Region | Geographic cloud location | भौगोलिक cloud स्थान |
| Multi-region | Running in 2+ regions | कई regions में चलाना |
| Active-passive | One serves, one standby | एक चालू, एक इंतज़ार में |
| Active-active | All regions serve | सब regions चालू |
| Home region | Region owning a user's data | यूज़र के डेटा का region |
| Data residency | Data must stay in a country | डेटा देश में ही रहे |
| Write forwarding | Secondary forwards writes to primary | writes को primary पर भेजना |
| Latency-based routing | Send users to fastest region | सबसे तेज़ region पर भेजना |
| Regional evacuation | Moving all traffic out of a region | region ख़ाली करना |
| Global Tables | DynamoDB multi-region replication | DynamoDB का multi-region |

---

## ⚡ 3-Line Summary
**English:**
1. Multi-region gives resilience to region outages, lower latency and data residency — at high cost and complexity.
2. Patterns: active-passive, active-active with single primary (local reads), geo-partitioned home regions, multi-writer (LWW/CRDT/distributed SQL).
3. Replicate everything needed (data, images, secrets, config), route with latency/health DNS or anycast, deploy region-by-region, and drill evacuations.

**Hindi:**
1. Multi-region = region outage से बचाव, कम latency, डेटा नियम — पर महँगा और जटिल।
2. तरीके: active-passive, active-active (एक primary), home region, multi-writer।
3. डेटा, images, secrets सब replicate करो, latency DNS से routing, region-दर-region deploy, और drill।

---

## ➡️ Next Topic Suggestion
**107. Kubernetes Basics** — Running services across AZs and regions needs a good way to deploy, scale and heal containers. Next: Kubernetes, with pods, deployments, services, ingress, config, autoscaling and probes, explained for app developers.
