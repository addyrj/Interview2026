# 228. Load Balancing with Node
# हिंदी में: Load Balancing — Traffic को Multiple Instances में Distribute करना

---

## 🔵 Simple Definition (English)
**Load balancing** distributes incoming traffic across multiple server instances (processes, containers, or machines) so no single instance is overwhelmed, enabling horizontal scaling and high availability. Layers range from PM2/`cluster` module (multi-core, single machine) to reverse proxies like **nginx** (multi-machine) to cloud **load balancers** (AWS ALB/ELB, GCP Load Balancer) that distribute across many servers/regions, with health checks routing traffic away from unhealthy instances.

## 🔵 सरल परिभाषा (Hindi)
**Load balancing** incoming traffic को कई server instances (processes, containers, या machines) में distribute करती है ताकि कोई एक instance overwhelmed न हो, horizontal scaling और high availability enable होती है। Layers PM2/`cluster` module (multi-core, एक machine) से nginx जैसे reverse proxies (multi-machine) तक से cloud **load balancers** (AWS ALB/ELB, GCP Load Balancer) तक जाते हैं जो कई servers/regions में distribute करते हैं, health checks unhealthy instances से traffic हटाते हैं।

---

## 🔴 Problem it Solves
A single server instance (no matter how well-optimized) has a hard ceiling on how much traffic it can handle before response times degrade or it crashes. Scaling VERTICALLY (bigger machine) has diminishing returns and a hard upper limit; scaling HORIZONTALLY (more machines/instances) is the standard way to handle growth, but requires something to DISTRIBUTE incoming requests across all those instances intelligently — and to detect and route around instances that have crashed or become unhealthy, so users don't experience errors when one instance has a problem.

## 🔴 यह क्यों बना? (Hindi)
एक single server instance (कितना भी well-optimized हो) की traffic handle करने की एक hard ceiling होती है जिसके बाद response times degrade होते हैं या crash हो जाता है। VERTICAL scaling (बड़ी machine) की diminishing returns और hard upper limit होती है; HORIZONTAL scaling (ज़्यादा machines/instances) growth handle करने का standard तरीका है, पर इसके लिए कुछ चाहिए जो incoming requests को उन सभी instances में intelligently DISTRIBUTE करे — और crashed/unhealthy instances को detect करके उनसे traffic हटाए।

---

## 🟢 How it Works — Step by Step

Step 1 → Deploy the same app across multiple instances (could be multiple PM2 cluster workers on one machine, multiple VMs/containers across machines, or both layered together)
Step 2 → Place a load balancer in front: nginx (self-managed reverse proxy), a cloud load balancer (AWS ALB, GCP LB), or a service mesh — all instances register behind it
Step 3 → The load balancer chooses a distribution algorithm: **round-robin** (cycle through instances evenly), **least-connections** (send to the instance with fewest active connections), or **IP hash** (same client always routes to the same instance — useful for sticky sessions)
Step 4 → The load balancer periodically runs **health checks** (e.g., `GET /health` every few seconds) against each instance — if an instance fails checks, it's automatically removed from rotation until it recovers
Step 5 → For stateful concerns (user sessions), either use **sticky sessions** (same client → same instance) or (better) make instances **stateless** by storing session data in Redis, so ANY instance can serve ANY request
Step 6 → Monitor aggregate metrics (total requests, per-instance latency/error rate) to know when to scale the instance count up or down

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Same app को कई instances में deploy करो (एक machine पर कई PM2 cluster workers, या कई machines/containers, या दोनों एक साथ)
Step 2 → सामने एक load balancer रखो: nginx (self-managed reverse proxy), cloud load balancer (AWS ALB, GCP LB), या service mesh — सभी instances उसके पीछे register होते हैं
Step 3 → Load balancer एक distribution algorithm चुनता है: **round-robin** (instances में बराबर घूमना), **least-connections** (सबसे कम active connections वाले instance को भेजना), या **IP hash** (same client हमेशा same instance पर जाए)
Step 4 → Load balancer हर instance पर **health checks** (जैसे `GET /health` हर कुछ seconds में) चलाता है — fail होने पर instance rotation से हट जाता है
Step 5 → Stateful concerns (user sessions) के लिए **sticky sessions** use करो या (बेहतर) instances को **stateless** बनाओ Redis में session data store करके
Step 6 → Aggregate metrics (total requests, per-instance latency/error rate) monitor करो instance count बढ़ाने/घटाने के लिए

---

## 🟡 Real World Example
**Flipkart's checkout service** runs 20 instances across 5 VMs (4 PM2 cluster workers each), behind an AWS Application Load Balancer. The ALB performs health checks on `/health` every 10 seconds; during a deployment, new instances register and must pass 2 consecutive health checks before receiving traffic, while old instances are drained (no new requests, but in-flight ones complete) before being terminated. During a flash sale traffic spike, auto-scaling adds 10 more instances within minutes, and the ALB automatically starts routing to them as soon as they pass health checks — all without any manual intervention or downtime, because the service is fully stateless (sessions in Redis, no sticky-session dependency).

## 🟡 Real Example Hindi mein
**Flipkart की checkout service** 5 VMs (हर एक 4 PM2 cluster workers) में 20 instances चलाती है, AWS Application Load Balancer के पीछे। ALB हर 10 seconds में `/health` पर health checks चलाता है; deployment के दौरान, नए instances register होते हैं और traffic मिलने से पहले 2 consecutive health checks pass करना ज़रूरी है, जबकि पुराने instances drain होते हैं। Flash sale traffic spike के दौरान, auto-scaling मिनटों में 10 और instances add करता है, और ALB automatically उन पर route करना शुरू कर देता है जैसे ही वो health checks pass करते हैं।

---

## 💻 Code Example — Basic

```javascript
// health-check-endpoint.js — the foundation every load balancer relies on
const express = require('express');
const app = express();

let isHealthy = true;
let dbConnected = false;

// Simulate DB connection check
async function checkDbConnection() {
  try {
    // await db.query('SELECT 1'); // real check in production
    dbConnected = true;
  } catch {
    dbConnected = false;
  }
}
setInterval(checkDbConnection, 5000);
checkDbConnection();

app.get('/health', (req, res) => {
  // A GOOD health check verifies actual DEPENDENCIES, not just "process is alive"
  if (!dbConnected) {
    return res.status(503).json({ status: 'unhealthy', reason: 'db disconnected' });
  }
  res.status(200).json({ status: 'healthy', pid: process.pid });
});

// Readiness vs liveness — common distinction in k8s/cloud load balancers:
// /health/live  → is the process running at all? (simple check)
// /health/ready → is the app ready to accept traffic? (checks dependencies)
app.get('/health/live', (req, res) => res.status(200).json({ alive: true }));
app.get('/health/ready', (req, res) => {
  res.status(dbConnected ? 200 : 503).json({ ready: dbConnected });
});

app.listen(3000);
```

## 💻 Code Example — Advanced

```javascript
// node-http-proxy-demo.js — a simple load balancer written in Node itself
// (in production, nginx/cloud LBs are typically used, but understanding
// the mechanics by building one helps for interviews)
const http = require('http');
const httpProxy = require('http-proxy'); // npm install http-proxy

const proxy = httpProxy.createProxyServer({});

// List of backend instances to balance across
const backends = [
  { url: 'http://localhost:3001', healthy: true, activeConnections: 0 },
  { url: 'http://localhost:3002', healthy: true, activeConnections: 0 },
  { url: 'http://localhost:3003', healthy: true, activeConnections: 0 },
];

// LEAST-CONNECTIONS algorithm: pick the healthy backend with fewest active requests
function pickBackend() {
  const healthyBackends = backends.filter(b => b.healthy);
  if (healthyBackends.length === 0) return null;
  return healthyBackends.reduce((min, b) =>
    b.activeConnections < min.activeConnections ? b : min
  );
}

const server = http.createServer((req, res) => {
  const backend = pickBackend();
  if (!backend) {
    res.writeHead(503);
    return res.end('No healthy backends available');
  }

  backend.activeConnections++;
  proxy.web(req, res, { target: backend.url }, (err) => {
    if (err) {
      res.writeHead(502);
      res.end('Backend error');
    }
  });

  res.on('finish', () => {
    backend.activeConnections--; // decrement once the request completes
  });
});

// HEALTH CHECKING: periodically ping each backend, mark unhealthy ones
async function runHealthChecks() {
  for (const backend of backends) {
    try {
      const healthUrl = `${backend.url}/health`;
      const response = await fetch(healthUrl, { signal: AbortSignal.timeout(2000) });
      backend.healthy = response.ok;
    } catch {
      backend.healthy = false; // unreachable or timed out — remove from rotation
    }
  }
}
setInterval(runHealthChecks, 5000);
runHealthChecks();

server.listen(8080, () => console.log('Load balancer listening on :8080'));
```

```nginx
# nginx.conf — the production-standard way to load balance Node.js instances
# (much more battle-tested than hand-rolling a Node-based LB for real traffic)

upstream node_backends {
    least_conn;  # use least-connections algorithm instead of default round-robin

    server 127.0.0.1:3001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:3002 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:3003 max_fails=3 fail_timeout=30s;
    # max_fails/fail_timeout: after 3 failed health checks, mark unhealthy
    # for 30s before retrying
}

server {
    listen 80;

    location / {
        proxy_pass http://node_backends;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # Health check-aware timeouts
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }

    location /health {
        proxy_pass http://node_backends/health;
        access_log off;  # don't clutter logs with frequent health check hits
    }
}
```

---

## 🟠 Express.js Integration

```javascript
// Making an Express app LOAD-BALANCER-READY: stateless design is the key requirement

const express = require('express');
const session = require('express-session');
const RedisStore = require('connect-redis').default;
const Redis = require('ioredis');
const app = express();

const redisClient = new Redis(process.env.REDIS_URL);

// CRITICAL for load-balanced deployments: session data in Redis, NOT in-memory
// This way, ANY instance behind the load balancer can handle ANY request from
// a given user — no "sticky session" dependency required
app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
}));

// Comprehensive health check that a load balancer relies on
app.get('/health', async (req, res) => {
  const checks = { server: true, redis: false, database: false };

  try {
    await redisClient.ping();
    checks.redis = true;
  } catch { /* redis down */ }

  try {
    // await db.query('SELECT 1');
    checks.database = true;
  } catch { /* db down */ }

  const allHealthy = Object.values(checks).every(Boolean);
  res.status(allHealthy ? 200 : 503).json(checks);
});

app.get('/api/orders', async (req, res) => {
  // req.session works correctly regardless of WHICH instance handles this
  // request, because session data lives in Redis, shared across all instances
  res.json({ userId: req.session.userId, orders: [] });
});

app.listen(process.env.PORT || 3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using sticky sessions as a crutch instead of making the app stateless
```javascript
// WRONG: relying on sticky sessions (same client always → same instance)
// means if THAT instance crashes, the user loses their session entirely,
// and uneven traffic distribution occurs if some clients make many more
// requests than others (defeats the purpose of load balancing)

// CORRECT: externalize session state to Redis — any instance can serve
// any request, enabling true even load distribution and resilience
// to any single instance failing
```

❌ Mistake 2: A health check that only confirms "the process is running," not that dependencies work
```javascript
// WRONG: this ALWAYS returns healthy even if the DB is completely down —
// load balancer keeps sending traffic to an instance that can't actually
// serve real requests
app.get('/health', (req, res) => res.status(200).send('OK'));

// CORRECT: verify the dependencies the app actually needs to function
app.get('/health', async (req, res) => {
  try {
    await db.query('SELECT 1');
    res.status(200).json({ status: 'healthy' });
  } catch {
    res.status(503).json({ status: 'unhealthy' }); // LB removes this instance from rotation
  }
});
```

---

## 🧠 Tricky Interview Question

**Q: Your load balancer uses round-robin across 3 instances, but one instance is on a much slower/older machine than the other two. What problem does round-robin cause here, and what's a better algorithm?**
Answer: Round-robin sends an EQUAL SHARE of requests to every instance regardless of its actual capacity or current load — the slower machine gets the same request volume as the faster ones, causing it to fall behind, queue up requests, and potentially become a bottleneck or even fail health checks under load while the faster instances sit comparatively underutilized. A better algorithm here is **least-connections** (route to whichever instance currently has the fewest active/in-flight requests) or a **weighted** algorithm (explicitly configure the slower machine to receive a smaller proportional share, e.g., `weight=1` for the slow one vs `weight=3` for faster ones in nginx config) — both adapt to actual capacity/load rather than blindly distributing evenly by request COUNT alone.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between round-robin, least-connections, and IP hash load balancing algorithms?
A1: **Round-robin** cycles through instances in fixed order, giving each an equal share of NEW requests regardless of current load. **Least-connections** sends each new request to whichever instance currently has the fewest active connections — adapts better when request durations vary. **IP hash** routes based on a hash of the client's IP, ensuring the same client always reaches the same instance (a simple form of session affinity/sticky sessions), useful when you haven't externalized session state but want some consistency.

Q2: Why is making your app "stateless" important for effective load balancing?
A2: If any instance can handle ANY request (no dependency on which specific instance served a previous request from the same user), the load balancer can distribute traffic freely and evenly, and any instance can fail/restart without affecting OTHER users' sessions on other instances. Stateless apps (session/cache data externalized to Redis, no local in-memory user-specific state) are a prerequisite for reliable horizontal scaling and graceful failure handling.

Q3: What's the difference between a "liveness" check and a "readiness" check (common in Kubernetes/cloud environments)?
A3: **Liveness** answers "is this process still running and not deadlocked?" — a failing liveness check typically causes the orchestrator to KILL and restart the instance. **Readiness** answers "is this instance currently able to serve real traffic?" (e.g., DB connection established, cache warmed) — a failing readiness check just REMOVES the instance from the load balancer's rotation temporarily, without killing it, until it becomes ready again. Conflating the two can cause unnecessary restarts for transient readiness issues (like a brief DB blip) that would have self-resolved.

Q4: How does connection draining work during a deployment, and why does it matter?
A4: When an instance is being taken out of rotation (deployment, scale-down), "draining" means the load balancer stops sending NEW requests to it immediately, but allows requests ALREADY in flight to that instance to complete normally before it's terminated. Without draining, in-flight requests would be abruptly cut off mid-response, causing errors for users whose requests happened to be in progress at the exact moment of termination.

Q5: How do PM2 cluster mode, nginx load balancing, and cloud load balancers (AWS ALB) relate to each other — are they redundant?
A5: They operate at different layers and often combine: PM2 cluster mode balances across CPU CORES within ONE machine. nginx (or a cloud ALB) balances across MULTIPLE machines/containers, each of which might internally be running PM2 cluster mode across its own cores. A typical large-scale architecture: Cloud Load Balancer → multiple VMs/containers → each running PM2 with N cluster workers (N = that machine's core count) → shared Redis/DB for cross-instance state. Each layer solves a different scaling dimension (vertical core utilization vs horizontal machine scaling), not redundant but complementary.

---

## 🔷 When to Use + When Not to Use
✅ Set up load balancing when:
- Running more than one instance/machine to handle traffic (almost always, for any production service beyond a toy project)
- You need high availability — the ability to lose one instance without taking down the whole service
- Scaling horizontally to handle growing or spiky traffic

❌ Less critical (but still good practice) when:
- Running a single-instance hobby project or internal tool with very low, predictable traffic and no availability requirements
- Using a serverless platform that already handles this transparently (the platform IS the load balancer, in effect)

---

## 📊 Visual Diagram
```
LOAD BALANCING ARCHITECTURE (layered):
────────────────────────────────────────────────
                  Internet
                     │
                     ▼
          ┌─────────────────────┐
          │  Cloud Load Balancer │  ← distributes across MACHINES
          │  (AWS ALB / nginx)   │     (health checks each)
          └──────────┬───────────┘
          ┌───────────┼───────────┐
          ▼           ▼            ▼
      ┌───────┐   ┌───────┐    ┌───────┐
      │ VM/     │   │ VM/     │    │ VM/     │
      │ Container│   │ Container│    │ Container│
      │         │   │         │    │         │
      │ PM2     │   │ PM2     │    │ PM2     │  ← distributes across
      │ cluster │   │ cluster │    │ cluster │     CPU CORES within
      │ (4 wkrs)│   │ (4 wkrs)│    │ (4 wkrs)│     each machine
      └───────┘   └───────┘    └───────┘
          │           │            │
          └───────────┴────────────┘
                     │
                     ▼
              ┌───────────┐
              │   Redis    │  ← shared state (sessions, cache)
              └───────────┘     accessible by ALL instances
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Load balancer | Distributes traffic across multiple instances | Traffic को कई instances में distribute करने वाला |
| Round-robin | Equal, cyclic distribution | बराबर, cyclic distribution |
| Least-connections | Routes to instance with fewest active requests | सबसे कम active requests वाले instance को |
| Health check | Periodic check if an instance is working | Instance ठीक काम कर रहा या नहीं check |
| Sticky session | Same client always → same instance | Same client हमेशा same instance पर |
| Stateless app | No per-instance state, any instance can serve any request | कोई per-instance state नहीं |
| Connection draining | Letting in-flight requests finish before removal | Hटाने से पहले in-flight requests पूरी होने देना |

---

## ⚡ 3-Line Summary
English:
1. Load balancing distributes traffic across multiple instances/machines, enabling horizontal scaling and high availability by routing around unhealthy instances via health checks.
2. Making your app stateless (session/cache in Redis, not local memory) is essential — it lets ANY instance serve ANY request, maximizing load balancer effectiveness and resilience.
3. Real deployments layer load balancing: cloud LB across machines, PM2/cluster across CPU cores within each machine, all coordinated through shared external state.

Hindi:
1. Load balancing traffic को कई instances/machines में distribute करती है, health checks से unhealthy instances को route से हटाकर horizontal scaling और high availability enable करती है।
2. App को stateless बनाना (session/cache Redis में, local memory में नहीं) ज़रूरी है — ये किसी भी instance को किसी भी request serve करने देता है, load balancer की effectiveness और resilience maximize होती है।
3. Real deployments load balancing को layer करते हैं: machines में cloud LB, हर machine के CPU cores में PM2/cluster, सब shared external state के through coordinated।

---

## ➡️ Next Topic
**229. Microservices Architecture with Node.js** — एक monolith app को छोटे, independently deployable services में split करना।
