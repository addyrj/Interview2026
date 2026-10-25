# 244. Health Check Endpoints
# हिंदी में: Health Check Endpoints

---

## 🔵 Simple Definition (English)
A health check endpoint is a dedicated API route (commonly `/health`, `/healthz`, `/ready`, `/live`) that reports whether a service instance is running correctly and able to serve traffic. Load balancers, Kubernetes, and monitoring tools call these endpoints periodically to decide whether to route traffic to an instance or restart/remove it.

## 🔵 सरल परिभाषा (Hindi)
Health check endpoint एक dedicated API route है (commonly `/health`, `/healthz`, `/ready`, `/live`) जो report करता है कि एक service instance सही से चल रही है और traffic serve करने में सक्षम है। Load balancers, Kubernetes, और monitoring tools इन endpoints को periodically call करते हैं यह decide करने के लिए कि किसी instance पर traffic route करें या उसे restart/remove करें।

---

## 🔴 Problem it Solves
In a horizontally-scaled or orchestrated system (Kubernetes, load balancers), there's no automatic way to know if a specific instance has crashed, is stuck, or is unable to reach its database — without health checks, a load balancer might keep sending traffic to a broken instance, causing failed requests for users, or an orchestrator might not know to restart a hung container. Health check endpoints give infrastructure a simple, standardized way to ask "are you okay?" and act accordingly (remove from rotation, restart, or wait before sending traffic).

## 🔴 यह क्यों बना? (Hindi)
Horizontally-scaled या orchestrated system (Kubernetes, load balancers) में, यह जानने का कोई automatic तरीका नहीं है कि कोई specific instance crash हुआ है, stuck है, या अपने database तक नहीं पहुंच पा रहा — health checks के बिना, load balancer broken instance पर traffic भेजता रह सकता है, users के लिए failed requests होती हैं, या orchestrator को नहीं पता चलता कि hung container को restart करना है। Health check endpoints infrastructure को एक simple, standardized तरीका देते हैं "are you okay?" पूछने का और accordingly act करने का (rotation से हटाना, restart करना, या traffic भेजने से पहले wait करना)।

---

## 🟢 How it Works — Step by Step

Step 1 → The service exposes a lightweight HTTP endpoint (e.g., `GET /health`) that any monitoring system can call.
Step 2 → A **liveness** check answers "is the process alive and responding at all?" — typically a trivial check (just returning 200 OK if the server can respond).
Step 3 → A **readiness** check answers "is the service ready to handle real traffic?" — typically checks critical dependencies (DB connection, cache connection) and returns 503 if any are down.
Step 4 → The load balancer/orchestrator polls these endpoints at a configured interval.
Step 5 → If a liveness check fails repeatedly, the orchestrator (e.g., Kubernetes) restarts the container, assuming it's stuck/crashed.
Step 6 → If a readiness check fails, the instance is removed from the load balancer's active pool (no new traffic sent) WITHOUT restarting it — useful for temporary issues (e.g., DB connection blip) that might self-resolve.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Service एक lightweight HTTP endpoint expose करती है (जैसे `GET /health`) जिसे कोई भी monitoring system call कर सके।
Step 2 → एक **liveness** check answer करता है "क्या process alive है और respond कर रहा है?" — typically एक trivial check (सिर्फ 200 OK return करना अगर server respond कर सकता है)।
Step 3 → एक **readiness** check answer करता है "क्या service real traffic handle करने के लिए ready है?" — typically critical dependencies (DB connection, cache connection) check करता है और कोई down हो तो 503 return करता है।
Step 4 → Load balancer/orchestrator इन endpoints को एक configured interval पर poll करता है।
Step 5 → अगर liveness check repeatedly fail हो, orchestrator (जैसे Kubernetes) container को restart करता है, यह मानते हुए कि वो stuck/crashed है।
Step 6 → अगर readiness check fail हो, instance को load balancer के active pool से हटा दिया जाता है (कोई नया traffic नहीं भेजा जाता) बिना restart किए — temporary issues (जैसे DB connection blip) के लिए useful जो खुद resolve हो सकते हैं।

---

## 🟡 Real World Example
**Zomato's order service on Kubernetes:** Each pod exposes `/live` (liveness: "is the Node.js process responding?") and `/ready` (readiness: "can I reach the orders database and the payment service?"). During a brief database connection pool exhaustion, the readiness check starts failing for one pod — Kubernetes immediately stops routing new orders to that pod (readiness failure), giving it a chance to recover without disrupting users, while the liveness check still passes (the process itself is fine) so Kubernetes doesn't unnecessarily restart it.

## 🟡 Real Example Hindi mein
**Zomato की order service Kubernetes पर:** हर pod `/live` (liveness: "क्या Node.js process respond कर रहा है?") और `/ready` (readiness: "क्या मैं orders database और payment service तक पहुंच सकता हूं?") expose करता है। एक brief database connection pool exhaustion के दौरान, एक pod का readiness check fail होने लगता है — Kubernetes उस pod पर नए orders भेजना तुरंत बंद कर देता है (readiness failure), उसे बिना users को disrupt किए recover होने का मौका देता है, जबकि liveness check फिर भी pass होता है (process खुद ठीक है) इसलिए Kubernetes उसे unnecessarily restart नहीं करता।

---

## 💻 Code Example — Basic

```javascript
// health-check-basic.js
// Run: node health-check-basic.js
const express = require('express');
const app = express();

// Simplest possible health check: "is the process alive and responding?"
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', uptime: process.uptime() });
});

app.listen(3000, () => console.log('Service running with basic health check on 3000'));

// A load balancer calling GET /health every 10s and getting 200 OK
// knows this instance is alive and can keep receiving traffic.
```

## 💻 Code Example — Advanced

```javascript
// health-check-advanced.js — separate liveness and readiness checks with dependency checks
const express = require('express');
const app = express();

// Simulated dependencies (replace with real DB/Redis clients)
let dbConnected = true;
let redisConnected = true;

// ─── LIVENESS: is the process itself alive? (very cheap check, no dependencies) ──
app.get('/live', (req, res) => {
  // If this handler can even execute, the event loop is responsive — that's enough for liveness
  res.status(200).json({ status: 'alive', pid: process.pid });
});

// ─── READINESS: can this instance actually handle real traffic right now? ───────
app.get('/ready', async (req, res) => {
  const checks = {
    database: await checkDatabase(),
    redis: await checkRedis(),
  };

  const allHealthy = Object.values(checks).every(Boolean);

  if (allHealthy) {
    res.status(200).json({ status: 'ready', checks });
  } else {
    // 503 tells the load balancer/orchestrator: "don't send me traffic yet"
    res.status(503).json({ status: 'not_ready', checks });
  }
});

async function checkDatabase() {
  try {
    // In real code: await db.query('SELECT 1')
    return dbConnected;
  } catch {
    return false;
  }
}

async function checkRedis() {
  try {
    // In real code: await redisClient.ping()
    return redisConnected;
  } catch {
    return false;
  }
}

// Simulate a dependency going down (for demo purposes)
app.post('/simulate/db-down', (req, res) => { dbConnected = false; res.sendStatus(200); });
app.post('/simulate/db-up', (req, res) => { dbConnected = true; res.sendStatus(200); });

app.listen(3000, () => console.log('Service with liveness/readiness checks on 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const app = express();

// Health checks should be registered BEFORE heavy middleware (auth, body parsing)
// so they respond fast and don't depend on unrelated app state.
app.get('/health', (req, res) => res.sendStatus(200));

app.get('/health/detailed', async (req, res) => {
  const dbOk = await pingDatabase().catch(() => false);
  const cacheOk = await pingCache().catch(() => false);
  const memoryUsage = process.memoryUsage();

  res.json({
    status: dbOk && cacheOk ? 'healthy' : 'degraded',
    dependencies: { database: dbOk, cache: cacheOk },
    memory: { heapUsedMB: Math.round(memoryUsage.heapUsed / 1024 / 1024) },
    uptimeSeconds: process.uptime(),
  });
});

async function pingDatabase() { return true; }
async function pingCache() { return true; }

// Business routes come after — health checks should never require auth or heavy setup
app.get('/orders', (req, res) => res.json({ orders: [] }));

app.listen(3000, () => console.log('Express app with health endpoints on 3000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Making the health check itself expensive (e.g., running a full DB query with joins)
✅ Correct: Keep checks lightweight (a simple `SELECT 1` or `PING`), since they run frequently and under load

```javascript
// Wrong — heavy query run every few seconds by the load balancer, adding real load
app.get('/health', async (req, res) => { await db.query('SELECT COUNT(*) FROM huge_table'); res.sendStatus(200); });

// Right — cheap connectivity check
app.get('/health', async (req, res) => { await db.query('SELECT 1'); res.sendStatus(200); });
```

❌ Mistake 2: Conflating liveness and readiness into a single check, causing unnecessary restarts
✅ Correct: Separate them — a failing dependency should affect readiness (remove from LB), not liveness (restart)

```javascript
// Wrong — DB being briefly down causes Kubernetes to RESTART the pod (liveness fails)
app.get('/health', async (req, res) => { await db.ping(); res.sendStatus(200); });   // used as liveness probe

// Right — liveness is cheap/independent; readiness checks the DB and triggers removal-from-LB, not restart
app.get('/live', (req, res) => res.sendStatus(200));
app.get('/ready', async (req, res) => { const ok = await db.ping().catch(() => false); res.sendStatus(ok ? 200 : 503); });
```

---

## 🧠 Tricky Interview Question

```javascript
// A pod's /live endpoint is configured as BOTH the liveness AND readiness probe in Kubernetes.
// The pod's database connection drops for 2 minutes due to a network blip, but the Node.js
// process itself is fine. What happens if /live doesn't check the DB (good) but IS being used
// for both probes, and some OTHER endpoint checks the DB and returns 503 when DB is down,
// and THAT endpoint is mistakenly the one used as the liveness probe?
```
Answer: If a DB-dependent check is wired as the LIVENESS probe (not readiness), Kubernetes will interpret the DB being briefly unreachable as "the process is broken" and will REPEATEDLY RESTART the pod — even though the actual Node.js process was perfectly healthy and would have recovered on its own once the DB connection blip passed. This is a classic misconfiguration: restarting a healthy process doesn't fix a database network issue, it just adds restart churn and potential request failures during restarts, while the real problem (DB connectivity) remains unaffected. The DB check belongs in readiness, which only removes the pod from traffic routing without needlessly restarting it.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a liveness check and a readiness check?
A1: Liveness answers "is this process alive and functioning at a basic level?" — if it fails repeatedly, the orchestrator assumes the process is stuck/crashed and RESTARTS it. Readiness answers "is this instance currently able to serve real traffic?" — if it fails, the instance is temporarily REMOVED from the load balancer's routing pool (no restart), since the issue (e.g., a dependency being briefly down) might resolve on its own without needing a restart. Conflating the two can cause unnecessary restarts for transient dependency issues.

Q2: Why should health check endpoints avoid expensive operations?
A2: Health checks are called frequently (often every few seconds) by load balancers/orchestrators monitoring potentially many instances. An expensive check (heavy DB query, external API call with no timeout) adds real, repeated load to the system and can itself become a source of slowness or failure, ironically making the service LESS healthy because of the health check itself. Checks should be cheap connectivity/sanity checks (e.g., `SELECT 1`, `PING`), not full business-logic validations.

Q3: What should a readiness check verify, and what shouldn't it?
A3: It should verify the minimum set of CRITICAL dependencies required to serve traffic correctly — e.g., database connectivity, essential cache/queue connectivity. It should NOT check every single downstream dependency the service might ever use (including optional/non-critical ones), since that would cause the instance to be marked "not ready" for failures that don't actually prevent it from serving most requests, unnecessarily reducing available capacity.

Q4: How do health checks support zero-downtime deployments?
A4: During a rolling deployment, new instances start up but aren't immediately ready (they may still be connecting to the database, warming caches, etc.). The orchestrator uses the READINESS check to hold off sending traffic to a new instance until it reports ready, and similarly waits for old instances being terminated to finish in-flight requests before fully removing them. This coordination — driven by health check responses — is what allows deployments to roll out without dropping user requests.

Q5: How would you design a health check for a service with multiple dependencies (DB, cache, message queue) where some are critical and some aren't?
A5: Separate the dependencies by criticality: critical ones (e.g., the primary database, needed for almost every request) should cause readiness to fail (503) if unreachable. Non-critical ones (e.g., an analytics queue that, if down, only delays non-essential logging) should be reported in a detailed health response for visibility/alerting but NOT cause the readiness check to fail — the service can still serve its core function without them. This is often modeled as `{ status: 'degraded', checks: {...} }` with a 200 status for degraded-but-functional states, versus 503 only for truly blocking failures.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running behind a load balancer or orchestrator (Kubernetes, ECS) that needs to make routing/restart decisions
- You want zero-downtime deployments and automatic recovery from stuck processes
- You need visibility into dependency health for monitoring/alerting

❌ Avoid when:
- A single, manually-managed instance with no automated infrastructure watching it (rare in modern deployments, but health checks still don't hurt to have for manual debugging)

---

## 📊 Visual Diagram
```
  Load Balancer / Kubernetes
         │  polls every few seconds
         ▼
  ┌─────────────────┐
  │  GET /live        │ ──▶ 200 OK → process alive, no restart needed
  │  GET /ready       │ ──▶ 200 OK → DB/cache reachable, keep sending traffic
  │                    │ ──▶ 503    → remove from LB rotation (no restart)
  └─────────────────┘

  /live fails repeatedly  → RESTART the container
  /ready fails            → REMOVE from traffic routing (temporary)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Liveness check | Is the process alive? | क्या process alive है? |
| Readiness check | Can this instance serve traffic now? | क्या यह instance अभी traffic serve कर सकता है? |
| Health endpoint | HTTP route reporting service health | Service health report करने वाला HTTP route |
| Rolling deployment | Gradual instance replacement with health checks | Health checks के साथ gradual instance replacement |
| Degraded status | Partially healthy but still functional | Partially healthy पर फिर भी functional |

---

## ⚡ 3-Line Summary
**English:**
1. Health check endpoints let load balancers and orchestrators know if an instance can serve traffic or needs restarting.
2. Liveness checks are cheap and independent; readiness checks verify critical dependencies and should be separate.
3. Keep health checks lightweight and only fail readiness for truly blocking dependency issues, not every minor one.

**Hindi:**
1. Health check endpoints load balancers और orchestrators को बताते हैं कि instance traffic serve कर सकता है या restart चाहिए।
2. Liveness checks cheap और independent होते हैं; readiness checks critical dependencies verify करते हैं और अलग होने चाहिए।
3. Health checks को lightweight रखो और readiness को सिर्फ truly blocking dependency issues के लिए fail करो, हर minor issue के लिए नहीं।

---

## ➡️ Next Topic
**245. Graceful Shutdown** — Ensuring in-flight requests complete and resources are cleaned up properly when a service stops.
