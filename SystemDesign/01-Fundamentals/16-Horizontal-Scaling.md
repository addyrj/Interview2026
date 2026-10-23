# 16. Horizontal Scaling
# हिंदी में: Horizontal Scaling (Scale Out) — एक बड़ी मशीन की जगह कई मशीनें जोड़कर काम बाँटना

---

## 🔵 Simple Definition (English)
**Horizontal scaling** (scaling **out**) means handling more load by **adding more machines/instances** and spreading traffic across them with a **load balancer**. Instead of one big server, you run many identical smaller ones, and add or remove them as traffic changes (**auto-scaling**).

## 🔵 सरल परिभाषा (Hindi)
Horizontal scaling यानी एक ही ऐप की कई copies कई मशीनों पर चलाना और Load Balancer से ट्रैफ़िक बाँटना।
ट्रैफ़िक बढ़े तो मशीनें जोड़ो, घटे तो हटाओ — इसे auto-scaling कहते हैं।

---

## 🔴 Problem it Solves
Vertical scaling hits limits:
- **Ceiling:** there's a biggest machine.
- **SPOF:** one machine dies → total outage.
- **Cost:** huge machines are expensive and idle at night.
- **Spiky traffic:** IPL final, flash sales, festive offers → 10× traffic for 2 hours.

Horizontal scaling gives:
- **Near-unlimited capacity** (add more nodes),
- **High availability** (one node dies, others continue),
- **Elasticity** (scale with demand, pay for what you use).

## 🔴 यह क्यों बना? (Hindi)
एक मशीन की सीमा है, वो गिरे तो सब बंद, और बड़ी मशीन रात में बेकार पड़ी रहती है।
कई मशीनें जोड़ने से लगभग असीमित क्षमता मिलती है, एक गिरे तो बाक़ी चलती रहती हैं, और IPL या सेल जैसे ट्रैफ़िक के समय मशीनें बढ़ाकर बाद में घटा सकते हैं।

---

## 🟢 How it Works — Step by Step

```
                         ┌──────────────┐
         Users ─────────►│ Load Balancer│
                         └──────┬───────┘
              ┌─────────────────┼─────────────────┬──────────────┐
              ▼                 ▼                 ▼              ▼
         ┌─────────┐       ┌─────────┐       ┌─────────┐    ┌─────────┐
         │ App #1  │       │ App #2  │       │ App #3  │    │ App #N  │  ← identical, STATELESS
         └────┬────┘       └────┬────┘       └────┬────┘    └────┬────┘
              └─────────────────┴────────┬────────┴──────────────┘
                     ┌───────────────────┼────────────────────┐
                     ▼                   ▼                    ▼
               ┌──────────┐        ┌──────────┐         ┌──────────┐
               │  Redis   │        │ Postgres │         │   S3     │   ← SHARED state
               │ sessions │        │ + replicas│        │  files   │
               │ cache    │        └──────────┘         └──────────┘
               └──────────┘
```

### Rule #1: app servers must be STATELESS

```
❌ Stateful (breaks with many servers)          ✅ Stateless
- sessions in server memory                       - JWT, or sessions in Redis
- uploaded files on local disk                    - files in S3
- in-memory cache as source of truth              - Redis cache
- cron job runs on every instance (runs N times!) - one scheduler / distributed lock
- WebSocket rooms in memory                       - Redis pub/sub adapter

Request 1 → App #1 (login, session in memory)
Request 2 → App #3 → "who are you?" → logged out ❌
```

### Auto-scaling

```
Metric: average CPU, requests per target, queue length, custom (latency)
Policy: target tracking — "keep average CPU at 60%"

 instances
   10 │                    ┌────┐
    8 │                ┌───┘    └──┐
    6 │            ┌───┘           └──┐
    4 │        ┌───┘                  └───┐
    2 │────────┘                          └────────
      └──────────────────────────────────────────── time
        9am       7pm (dinner peak)        11pm

Min = 2 (high availability across 2 AZs), Max = 20 (cost cap)
Scale-out fast, scale-in slowly (cooldown) to avoid flapping.
New instance must boot fast: small Docker image, health check ready in seconds.
```

### Scaling each tier

```
Tier            How to scale out
──────────────  ─────────────────────────────────────────────────
Stateless API   Add instances behind LB (easy)            ✅
Workers         Add consumers on the queue (easy)         ✅
Cache (Redis)   Redis Cluster (sharding)                  ⚠️ moderate
DB reads        Read replicas (Topic 40)                  ⚠️ moderate
DB writes       Sharding / partitioning (Topic 42)        ❌ hard
Files           Object storage S3 (already infinite)     ✅
WebSockets      Gateway nodes + pub/sub (Topic 96)        ⚠️ moderate
```

### Vertical vs Horizontal

```
┌──────────────────┬────────────────────────┬──────────────────────────┐
│                  │ Vertical (up)          │ Horizontal (out)         │
├──────────────────┼────────────────────────┼──────────────────────────┤
│ How              │ Bigger machine         │ More machines            │
│ Limit            │ Hardware ceiling       │ Practically none         │
│ Availability     │ SPOF                   │ High (redundancy)        │
│ Code change      │ None                   │ Must be stateless        │
│ Complexity       │ Low                    │ LB, distributed state    │
│ Cost pattern     │ Pay for peak 24×7      │ Elastic (pay for usage)  │
│ Best for         │ DB primary, quick fix  │ Web/API tier, workers    │
└──────────────────┴────────────────────────┴──────────────────────────┘
Real systems use BOTH: scale the DB up, scale the app out.
```

## 🟢 कैसे काम करता है? (Hindi)
1. ऐप की कई एक जैसी copies चलाओ और आगे Load Balancer लगाओ।
2. ऐप stateless होना चाहिए — session Redis/JWT में, फ़ाइलें S3 में, किसी सर्वर की memory में नहीं।
3. Auto-scaling नियम लगाओ: "CPU 60% से ऊपर जाए तो मशीन जोड़ो"।
4. कम से कम 2 मशीनें अलग-अलग zone में रखो ताकि एक गिरे तो दूसरी चले।
5. API और workers आसानी से स्केल होते हैं; DB writes को स्केल करना सबसे मुश्किल है।

---

## 🟡 Real World Example

**Hotstar (JioCinema/Disney+ Hotstar) — IPL**
- Handled 25+ million concurrent viewers. They **pre-scale** (scale out before the match starts) because auto-scaling reacting to a sudden spike at the toss is too slow. They run load tests with simulated millions of users, and keep "panic mode" switches that turn off non-essential features to save capacity.

**Flipkart Big Billion Days**
- Thousands of extra app instances are added for sale days. Stateless services scale out; databases are pre-provisioned and heavily cached.

**Netflix**
- Runs stateless microservices in auto-scaling groups across multiple AWS regions. Its **Chaos Monkey** randomly kills instances in production to make sure horizontal redundancy really works.

## 🟡 Real Example Hindi में
Hotstar IPL के समय 2.5 करोड़ से ज़्यादा लोगों को एक साथ स्ट्रीम करता है — मैच से पहले ही हज़ारों मशीनें जोड़ दी जाती हैं (pre-scaling), क्योंकि toss के समय अचानक ट्रैफ़िक आता है।
Flipkart बिग बिलियन डेज़ में हज़ारों अतिरिक्त सर्वर जोड़ता है और सेल के बाद हटा देता है।

---

## 🟠 My Stack Example

### Make the Node.js app stateless
```js
// Sessions in Redis instead of memory
import session from 'express-session';
import { RedisStore } from 'connect-redis';
app.use(session({ store: new RedisStore({ client: redis }), secret: process.env.SESSION_SECRET,
                  resave: false, saveUninitialized: false }));

// Uploads go straight to S3 (presigned URL), not local disk
app.post('/uploads/url', auth, async (req, res) => {
  const key = `users/${req.user.id}/${randomUUID()}.jpg`;
  const url = await getSignedUrl(s3, new PutObjectCommand({ Bucket: BUCKET, Key: key, ContentType: 'image/jpeg' }), { expiresIn: 300 });
  res.json({ url, key });
});

// Cron runs only once across N instances → distributed lock
async function runDailyReport() {
  const lock = await redis.set('lock:daily-report', process.pid, { NX: true, EX: 600 });
  if (!lock) return;                 // another instance got it
  await generateReport();
}
```

### Docker Compose (single host) → Kubernetes / ECS (multi host)
```bash
docker compose up -d --scale api=4     # 4 replicas behind Nginx on one host
```
```yaml
# Kubernetes HPA — auto-scale pods on CPU
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: api }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 60 } }
```

### AWS ECS / EC2 Auto Scaling (target tracking)
```
ALB → Target Group → ECS Service (Fargate tasks)
Service Auto Scaling:
  min 2, max 20
  Target: ALBRequestCountPerTarget = 500   (or CPU 60%)
  Scale-in cooldown 300s
Spread tasks across ap-south-1a, 1b, 1c
```

### FastAPI workers scale on queue depth
```
Celery/RQ workers ← SQS queue
Scale rule: if ApproximateNumberOfMessagesVisible > 1000 → add workers (KEDA on K8s, or ECS step scaling)
```

### Graceful shutdown (needed when scaling in)
```js
process.on('SIGTERM', () => {
  server.close(async () => {           // stop accepting, finish in-flight requests
    await pool.end(); await redis.quit();
    process.exit(0);
  });
  setTimeout(() => process.exit(1), 25_000).unref();   // hard limit < ECS/K8s stop timeout
});
```

---

## ⚫ Interview Questions + Answers

**Q1: What is horizontal scaling and what does an application need to support it?**
A1: Adding more instances and spreading load with a load balancer. The application must be stateless: no user sessions, uploaded files or authoritative caches in local memory or disk. Store them in shared systems (Redis, a DB, S3), or use JWTs. Background jobs need coordination (a single scheduler or distributed locks), and instances need health checks and graceful shutdown.

**Q2: How does auto-scaling work, and what metrics would you use?**
A2: A controller watches metrics and adjusts instance count between min and max. Use target tracking (keep CPU at about 60%, or requests per target at N), with scale-out fast and scale-in slow (cooldown) to avoid flapping. Metrics depend on the tier: CPU or requests for APIs, queue depth or age for workers, and custom latency or concurrent connections for WebSocket gateways. For predictable spikes (sales, matches), pre-scale on a schedule, because reactive scaling lags behind.

**Q3: Why is the database the hardest part to scale horizontally?**
A3: The DB holds state and must keep it consistent. Reads can be scaled out with read replicas, though replication lag means stale reads. Writes all go to one primary, and spreading them requires sharding: choosing a shard key, cross-shard queries and transactions, and rebalancing, which is complex. So teams first scale the DB vertically, add caching, replicas and partitioning, and shard only when necessary, or adopt distributed SQL/NoSQL stores built for it.

**Q4: During a flash sale, auto-scaling added servers but the site still went down. What could be wrong?**
A4: Typical causes: scaling was too slow (instances take minutes to boot, warm-up, health checks), so you should have pre-scaled. The bottleneck moved to a shared dependency: DB connections exhausted (100 instances × a pool of 20 = 2,000 connections, so use PgBouncer), the DB CPU, Redis, a third-party payment API, or rate limits. There may have been no load shedding or caching for hot items, or the load balancer itself needed pre-warming. Horizontal scaling of one tier just pushes load onto the next.

**Q5: Horizontal vs vertical scaling — which would you choose for (a) a Node.js API and (b) PostgreSQL?**
A5: (a) Horizontal: stateless Node instances behind an ALB, auto-scaled, spread across AZs for availability. (b) Vertical first, with a bigger instance and tuning, plus read replicas for read scaling, caching in Redis, and partitioning big tables. Shard or move to distributed databases only when write volume truly exceeds one machine. Most real architectures combine both.

---

## 🔷 Trade-offs
✅ Advantages:
- Practically unlimited capacity; high availability through redundancy.
- Elastic cost — scale with demand.
- Rolling deploys with zero downtime (replace instances one by one).

❌ Disadvantages:
- Requires stateless design and shared external state.
- More moving parts: load balancer, service discovery, distributed logs.
- Pushes load onto shared dependencies (DB connections, caches).
- Data consistency challenges when state itself is distributed.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Horizontal scaling / Scale out | Add more machines | और मशीनें जोड़ना |
| Stateless | Server keeps no client data between requests | सर्वर कुछ याद नहीं रखता |
| Auto-scaling | Automatically add/remove instances | अपने आप मशीनें घटाना-बढ़ाना |
| Elasticity | Grow/shrink with demand | माँग के हिसाब से फैलना-सिकुड़ना |
| Availability Zone (AZ) | Separate data center in a region | region के अंदर अलग डेटा सेंटर |
| Pre-scaling | Scaling before expected spike | भीड़ से पहले तैयारी |
| Graceful shutdown | Finish requests before stopping | काम पूरा करके बंद होना |
| HPA | Kubernetes Horizontal Pod Autoscaler | K8s का auto-scaler |

---

## ⚡ 3-Line Summary
**English:**
1. Horizontal scaling = more instances behind a load balancer; gives capacity + availability + elasticity.
2. App must be stateless (sessions in Redis/JWT, files in S3, locks for cron).
3. Scale the app out, the DB up (+ replicas/sharding later); watch shared bottlenecks like DB connections.

**Hindi:**
1. Horizontal scaling = Load Balancer के पीछे कई मशीनें; क्षमता + availability + लचीलापन।
2. ऐप stateless हो — session Redis में, फ़ाइलें S3 में।
3. ऐप को scale out, DB को scale up करो; DB connections जैसी साझा रुकावटों पर नज़र रखो।

---

## ➡️ Next Topic Suggestion
**17. Latency** — Scaling handles MORE users; now let's measure how FAST each user is served. Next: what latency is, p50/p95/p99, where it comes from, and how to reduce it.
