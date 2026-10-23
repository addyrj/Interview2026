# 80. Health Checks (Liveness + Readiness)
# हिंदी में: Health Checks — Load Balancer/Kubernetes का हर कुछ सेकंड में पूछना "तुम ज़िंदा हो? (liveness)" और "ट्रैफ़िक लेने को तैयार हो? (readiness)", ताकि बीमार instance को हटाया या restart किया जा सके

---

## 🔵 Simple Definition (English)
**Health checks** are periodic probes (usually HTTP endpoints) that tell infrastructure whether an instance is healthy:
- **Liveness:** "Is the process alive, not deadlocked?" If it fails → **restart** the container.
- **Readiness:** "Can it serve traffic right now?" If it fails → **remove from the load balancer** (don't restart).
- **Startup:** "Has it finished booting?" Delays liveness checks for slow-starting apps.
Load balancers (ALB target groups), Kubernetes probes, ECS, Consul and Docker all use them.

## 🔵 सरल परिभाषा (Hindi)
Health check में सिस्टम हर कुछ सेकंड में instance से पूछता है:
Liveness — "ज़िंदा हो?" (नहीं तो restart); Readiness — "ट्रैफ़िक लेने को तैयार हो?" (नहीं तो LB से कुछ देर हटाओ, restart नहीं); Startup — "शुरू हो गए?" (धीमे शुरू होने वाले ऐप के लिए)।

---

## 🔴 Problem it Solves
Without health checks:
- A crashed, hung or misconfigured instance keeps receiving traffic → users get errors.
- During deploys, traffic hits instances that are **still starting** (DB not connected, cache not warm) → errors.
- A deadlocked process (alive but stuck) is never restarted.
- During shutdown, instances keep getting requests → dropped connections.

Health checks let the platform **automatically route around failures and self-heal**, which is the foundation of high availability and zero-downtime deploys.

## 🔴 यह क्यों बना? (Hindi)
बिना health check के crash या अटका हुआ instance भी ट्रैफ़िक लेता रहता है, deploy के समय अधूरे शुरू हुए instance पर requests जाती हैं, और जाम (deadlock) हुआ process कभी restart नहीं होता।
Health checks से सिस्टम अपने आप बीमार instance को हटाता या restart करता है — high availability और बिना downtime deploy की नींव यही है।

---

## 🟢 How it Works — Step by Step

```
          every 5–10s
 LB / K8s ─── GET /health/ready ───► Instance A  → 200 ✅  (in rotation)
          ─── GET /health/ready ───► Instance B  → 503 ❌  (3 failures → removed from rotation)
          ─── GET /health/live  ───► Instance C  → timeout ❌ (K8s restarts container)

healthyThreshold   = 2 consecutive passes → add back
unhealthyThreshold = 3 consecutive fails  → remove / restart
```

### Liveness vs Readiness vs Startup

```
┌───────────┬───────────────────────────────┬──────────────────────┬────────────────────────────┐
│ Probe     │ Question                      │ On failure           │ Should check               │
├───────────┼───────────────────────────────┼──────────────────────┼────────────────────────────┤
│ Liveness  │ Is the process alive/healthy  │ RESTART container    │ Only the process itself:   │
│           │ (not deadlocked)?             │                      │ event loop responsive.     │
│           │                               │                      │ NO dependency checks!      │
│ Readiness │ Can I serve requests now?     │ STOP sending traffic │ Critical deps reachable    │
│           │                               │ (no restart)         │ (DB pool, required cache), │
│           │                               │                      │ warmed up, not shutting    │
│           │                               │                      │ down, not overloaded       │
│ Startup   │ Finished initialization?      │ keep waiting; restart│ App booted (migrations,    │
│           │                               │ after max time       │ caches loaded)             │
└───────────┴───────────────────────────────┴──────────────────────┴────────────────────────────┘
```

### The #1 mistake: dependencies in liveness

```
Liveness checks the database → DB has a 30-second blip
→ ALL pods fail liveness → Kubernetes RESTARTS ALL pods at once
→ restart storm, cold caches, connection storm to the recovering DB → much bigger outage ❌
Restarting your app doesn't fix the database!
→ Liveness = "am I stuck?" only. Dependencies belong in readiness (and even there, carefully).
```

### Readiness — careful with shared dependencies
```
If readiness requires a shared dependency (DB) and it goes down → ALL instances become unready
→ LB has zero healthy targets → returns 503 for everything (even cached/degraded responses
   that could have worked).
Options:
  - readiness checks only things THIS instance can fix/own (its pool, its warm-up, shutdown state)
  - let the app degrade gracefully instead of declaring itself unready
  - ALB: if all targets unhealthy it "fails open" and sends to all anyway
```

### Shallow vs deep health checks
```
Shallow: returns 200 if the HTTP server responds          → cheap, liveness
Deep:    checks DB, Redis, queue, disk, downstream APIs    → readiness / monitoring dashboards
Keep probe endpoints FAST (< 100 ms), unauthenticated (but not exposing secrets), cached (don't
hammer DB with checks from 100 pods every 2s), and excluded from access logs/metrics noise.
Expose a separate detailed /health/details for humans/monitoring.
```

### Health checks during deploys & shutdown (zero downtime)
```
Deploy new pod → startup probe → readiness passes → LB adds it → old pod gets SIGTERM
Old pod: mark NOT ready (readiness → 503) → LB stops sending new traffic (wait ~5–10 s)
         → finish in-flight requests → close DB/Redis → exit
(K8s: preStop hook sleep 5–10 s; terminationGracePeriodSeconds 30)
```

## 🟢 कैसे काम करता है? (Hindi)
1. LB/Kubernetes हर 5-10 सेकंड में `/health/live` और `/health/ready` बुलाता है।
2. Liveness फ़ेल (process अटका) → container restart; Readiness फ़ेल → कुछ देर ट्रैफ़िक बंद, restart नहीं।
3. सबसे बड़ी ग़लती: liveness में DB जाँचना — DB थोड़ी देर गिरा तो सारे pods एक साथ restart हो जाएँगे।
4. Readiness में सिर्फ़ ज़रूरी चीज़ें (अपना DB pool, warm-up, shutdown की हालत); endpoint तेज़ और हल्का रखो।
5. Deploy/shutdown पर: पहले readiness 503 करो, LB के हटने का इंतज़ार करो, चल रही requests पूरी करो, फिर बंद।

---

## 🟡 Real World Example

**Kubernetes restart storms** — many public postmortems describe liveness probes that checked a database or downstream API. A brief dependency outage made Kubernetes kill every pod at once, turning a 30-second blip into a 20-minute outage. The guidance since then: keep liveness shallow.

**AWS ALB target groups** — ALB marks targets unhealthy after N failed checks and stops routing to them. If all targets are unhealthy, ALB fails open and routes to all of them anyway, which is a deliberate design to avoid total blackout from a bad health check.

**Zero-downtime deploys at Swiggy/Zomato-scale companies** — readiness gates plus graceful shutdown (preStop sleep, draining) make thousands of daily deploys invisible to users.

**Netflix Eureka** — instances send heartbeats to service discovery. Missing heartbeats remove them from the registry, a client-side form of health checking.

## 🟡 Real Example Hindi में
कई कंपनियों में liveness probe DB जाँचता था — DB 30 सेकंड के लिए गिरा और Kubernetes ने सारे pods एक साथ मार दिए, छोटी गड़बड़ी 20 मिनट का outage बन गई।
AWS ALB सारे targets बीमार होने पर भी सब पर ट्रैफ़िक भेज देता है (fail open), ताकि ग़लत health check से पूरा सिस्टम बंद न हो।

---

## 🟠 My Stack Example

### Node.js (Express) — live, ready, startup + graceful shutdown
```js
let isReady = false, isShuttingDown = false, lastDbOk = 0;

// Liveness: only "is the event loop responsive?"
app.get('/health/live', (_, res) => res.status(200).send('ok'));

// Readiness: warmed up, not shutting down, DB pool usable (cached result, cheap)
app.get('/health/ready', async (_, res) => {
  if (!isReady || isShuttingDown) return res.status(503).send('not ready');
  if (Date.now() - lastDbOk > 5000) {                       // check at most every 5 s
    try { await pool.query('SELECT 1'); lastDbOk = Date.now(); }
    catch { return res.status(503).send('db unavailable'); }
  }
  res.status(200).send('ready');
});

// Detailed (for humans/monitoring) — protect with auth or internal network only
app.get('/health/details', internalOnly, async (_, res) => res.json({
  db: await probe(() => pool.query('SELECT 1')),
  redis: await probe(() => redis.ping()),
  version: process.env.GIT_SHA, uptime: process.uptime(),
}));

const server = app.listen(3000, async () => {
  await warmUp();                // load config, prime caches, connect pools
  isReady = true;
});

process.on('SIGTERM', () => {
  isShuttingDown = true;                         // readiness → 503 → LB drains
  setTimeout(() => {
    server.close(async () => { await pool.end(); await redis.quit(); process.exit(0); });
  }, 10_000);                                    // wait for LB to notice (> 2 × probe interval)
  setTimeout(() => process.exit(1), 25_000).unref();
});
```

### Kubernetes probes
```yaml
containers:
- name: api
  image: myapp/api:1.8.0
  ports: [{ containerPort: 3000 }]
  startupProbe:   { httpGet: { path: /health/live,  port: 3000 }, periodSeconds: 5, failureThreshold: 30 }  # up to 150s to boot
  livenessProbe:  { httpGet: { path: /health/live,  port: 3000 }, periodSeconds: 10, timeoutSeconds: 2, failureThreshold: 3 }
  readinessProbe: { httpGet: { path: /health/ready, port: 3000 }, periodSeconds: 5,  timeoutSeconds: 2, failureThreshold: 2 }
  lifecycle: { preStop: { exec: { command: ["sh", "-c", "sleep 5"] } } }
terminationGracePeriodSeconds: 30
```

### Docker Compose healthcheck (dependency ordering)
```yaml
services:
  db:
    image: postgres:16
    healthcheck: { test: ["CMD-SHELL", "pg_isready -U app"], interval: 5s, retries: 10 }
  api:
    build: .
    depends_on: { db: { condition: service_healthy } }     # start api only after DB is healthy
    healthcheck: { test: ["CMD", "wget", "-qO-", "http://localhost:3000/health/live"], interval: 10s }
```

### AWS ALB target group
```
Health check path: /health/ready   interval 10s   timeout 5s   healthy 2   unhealthy 3
Deregistration delay: 30s (draining)
```

### FastAPI
```python
ready = False
@app.on_event("startup")
async def startup():
    global ready; await warm_up(); ready = True

@app.get("/health/live")
async def live(): return {"ok": True}

@app.get("/health/ready")
async def readiness():
    if not ready: raise HTTPException(503)
    try: await asyncio.wait_for(db.execute(text("SELECT 1")), timeout=1)
    except Exception: raise HTTPException(503)
    return {"ok": True}
```

### Mobile apps
Apps can call a lightweight `/status` or `/app-config` endpoint on launch to show a maintenance banner or degraded-mode message, without treating it as an infrastructure health check.

---

## ⚫ Interview Questions + Answers

**Q1: What's the difference between liveness and readiness probes?**
A1: Liveness answers "is this process alive and not stuck?". If it fails, the orchestrator restarts the container. Readiness answers "should this instance receive traffic right now?". If it fails, the instance is removed from load balancing but not restarted. Readiness covers warm-up, temporary overload, dependency unavailability or shutdown. A startup probe delays liveness for slow-booting apps.

**Q2: Why shouldn't a liveness probe check the database?**
A2: Restarting the app doesn't fix the database. If the DB has a blip, every pod fails liveness simultaneously and gets restarted, causing restart storms, cold caches, connection floods on the recovering DB, and a much longer outage. Liveness should only detect conditions that a restart fixes (deadlock, an unresponsive event loop, memory corruption).

**Q3: What makes a good health check endpoint?**
A3: Fast (well under the probe timeout), cheap (cache dependency results, don't run heavy queries on every probe from every instance), accurate for its purpose (shallow for liveness, critical-dependency-aware for readiness), unauthenticated but safe (no secrets exposed), excluded from noisy logs and metrics, and versioned or detailed info available on a separate protected endpoint for humans.

**Q4: How do health checks enable zero-downtime deployments?**
A4: New instances only receive traffic once their startup and readiness probes pass. On shutdown, the old instance flips readiness to failing (or the orchestrator deregisters it), the load balancer stops sending new requests (deregistration delay or preStop sleep), in-flight requests complete within the grace period, and then the process exits. Rolling updates proceed one batch at a time, gated by readiness.

**Q5: What can go wrong if readiness depends on a shared downstream service?**
A5: When that dependency fails, all instances become unready at once, the load balancer has zero healthy targets, and everything returns 503, including requests that could have been served degraded or from cache. Be selective: readiness should mostly reflect instance-local state. Handle shared dependency failures with graceful degradation and circuit breakers, and rely on load balancer fail-open behaviour as a last resort.

---

## 🔷 Trade-offs
✅ Advantages:
- Automatic failure detection, self-healing, safe deploys, traffic only to healthy instances.

❌ Disadvantages:
- Misconfigured probes cause restart storms or total blackouts.
- Deep checks add load and can create correlated failures.
- Probe tuning (intervals, thresholds) trades detection speed vs false positives.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Health check | Periodic instance health probe | सेहत की जाँच |
| Liveness | Is the process alive | ज़िंदा है या नहीं |
| Readiness | Can it serve traffic | ट्रैफ़िक के लिए तैयार |
| Startup probe | Finished booting | शुरू हो चुका या नहीं |
| Shallow check | Only app responds | सिर्फ़ ऐप जवाब दे |
| Deep check | Checks dependencies | dependencies भी जाँचे |
| Draining | Stop new traffic before shutdown | बंद होने से पहले ट्रैफ़िक रोकना |
| Restart storm | Many pods restarting together | सब pods एक साथ restart |
| Fail open | Route to all if all unhealthy | सब बीमार हों तो भी भेजना |

---

## ⚡ 3-Line Summary
**English:**
1. Liveness = alive? (restart on failure); readiness = can serve? (remove from LB); startup = booted?
2. Keep liveness shallow (no DB!); readiness checks instance-critical state, cheaply and with caching.
3. Use readiness + draining + graceful shutdown for zero-downtime deploys; avoid correlated failures.

**Hindi:**
1. Liveness = ज़िंदा? (नहीं तो restart); Readiness = तैयार? (नहीं तो LB से हटाओ); Startup = शुरू हुआ?
2. Liveness हल्का रखो (DB नहीं!); readiness में ज़रूरी चीज़ें, cache के साथ।
3. Readiness + draining + graceful shutdown से बिना downtime deploy।

---

## ➡️ Next Topic Suggestion
**81. Failover** — Health checks detect failure; failover is what happens next: switching to a standby DB, region or server. Next: active-passive vs active-active failover, RTO, split-brain and fencing.
