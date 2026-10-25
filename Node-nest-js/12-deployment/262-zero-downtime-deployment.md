# 262. Zero Downtime Deployment
# हिंदी में: Zero Downtime Deployment — बिना Request खोए Deploy करना

---

## 🔵 Simple Definition (English)
**Zero downtime deployment** means deploying a new version of your app without dropping a single incoming request or showing users an error/downtime window. Instead of stopping the old version and then starting the new one (which creates a gap), you keep some instances of the old version serving traffic while new instances start up, then switch traffic over gradually — so users never notice a deploy happened.

## 🔵 सरल परिभाषा (Hindi)
**Zero downtime deployment** का मतलब है नया version deploy करना बिना एक भी incoming request खोए या users को कोई error/downtime window दिखाए। पुराना version रोककर फिर नया शुरू करने के बजाय (जिससे gap बनता है), कुछ पुराने instances traffic serve करते रहते हैं जब तक नए instances ready नहीं हो जाते, फिर traffic धीरे-धीरे switch होता है — users को पता भी नहीं चलता कि deploy हुआ है।

---

## 🔴 Problem it Solves
```
NAIVE DEPLOY (causes downtime):
  1. SSH into server
  2. Stop old process:     pm2 stop app     ──▶ SERVER IS NOW DOWN
  3. Pull new code:        git pull
  4. Install deps:         npm install
  5. Start new process:    pm2 start app     ──▶ server back up
  
  Downtime window = steps 2-5 duration (could be 10-60+ seconds)
  
  Real consequences:
  - In-flight requests get connection errors (502/504)
  - Users mid-checkout on Flipkart see "Something went wrong"
  - Payment gateway webhooks (Razorpay) arriving during this window are LOST
    if your server isn't listening to receive them
  - If deploy script has a bug, server might not come back up at all

ZERO DOWNTIME SOLUTION:
  1. Keep old instances running and serving traffic
  2. Start NEW instances with new code, one at a time
  3. Wait for each new instance to pass a health check (ready to serve)
  4. ONLY THEN route traffic to it and stop the corresponding old instance
  5. Repeat until all instances are on the new version
  
  Result: at every moment, there is at least one healthy instance serving
  traffic — users and webhooks never see a gap.
```

## 🔴 यह क्यों बना? (Hindi)
Naive deploy में process को stop करके फिर start करने के बीच एक gap होता है जिसमें server down रहता है — in-flight requests fail होती हैं, users को errors दिखते हैं, और payment webhooks जैसी critical calls miss हो सकती हैं। E-commerce/fintech apps (Flipkart checkout, Razorpay webhooks) के लिए even कुछ seconds का downtime भी लाखों का नुकसान कर सकता है। Zero downtime deployment इसे solve करता है — पुराने instances तब तक चलते रहते हैं जब तक नए instances health check पास नहीं कर लेते, फिर traffic गradually switch होता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Rolling restart (PM2 cluster)**: `pm2 reload app` restarts cluster instances ONE AT A TIME. Instance 1 restarts while instances 2,3,4 keep serving. Once instance 1 is back up and accepting connections, instance 2 restarts, and so on.
Step 2 → **Graceful shutdown**: before killing an old instance, PM2 sends `SIGINT`. The app must stop accepting NEW connections (`server.close()`) but let in-flight requests finish before actually exiting — this is "draining".
Step 3 → **Health checks**: a load balancer (Nginx, AWS ALB) or PM2 itself waits for the new instance to respond successfully on a `/health` endpoint before sending it real traffic.
Step 4 → **Blue-Green deployment** (bigger-scale alternative): run two complete, identical environments — "Blue" (current live) and "Green" (new version). Deploy fully to Green, test it, then flip the load balancer / DNS to point all traffic to Green instantly. Blue stays as instant rollback if something's wrong.
Step 5 → **Kubernetes rolling deployment** (for contrast at scale): Kubernetes replaces pods gradually, checking `readinessProbe` before routing traffic to a new pod, and `livenessProbe` to kill unhealthy ones — conceptually the same idea as PM2 reload but managed per-pod across many nodes, with the scheduler handling placement automatically.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Rolling restart (PM2 cluster)**: `pm2 reload app` cluster instances को एक-एक करके restart करता है। Instance 1 restart होता है जबकि 2,3,4 traffic serve करते रहते हैं। Instance 1 ready होने पर instance 2 restart होता है, और आगे।
Step 2 → **Graceful shutdown**: पुराने instance को kill करने से पहले PM2 `SIGINT` भेजता है। App को नए connections लेना बंद करना चाहिए (`server.close()`) लेकिन in-flight requests को finish होने देना चाहिए — इसे "draining" कहते हैं।
Step 3 → **Health checks**: load balancer (Nginx, AWS ALB) या PM2 खुद नए instance के `/health` endpoint पर successful response मिलने तक इंतज़ार करता है, तब ही real traffic भेजता है।
Step 4 → **Blue-Green deployment** (बड़े scale पर alternative): दो complete identical environments चलाओ — "Blue" (current live) और "Green" (नया version)। पूरा deploy Green पर करो, test करो, फिर load balancer/DNS को instantly Green की तरफ flip करो। Blue instant rollback के लिए मौजूद रहता है।
Step 5 → **Kubernetes rolling deployment** (scale पर comparison के लिए): Kubernetes pods को धीरे-धीरे replace करता है, नए pod को traffic भेजने से पहले `readinessProbe` check करता है, और unhealthy pods को kill करने के लिए `livenessProbe` use करता है — concept PM2 reload जैसा ही है, बस कई nodes पर managed, scheduler automatic placement करता है।

---

## 🟡 Real World Example
**Amazon-style flash sale deploy:** During a Big Billion Days-style sale, the checkout service cannot afford even a 5-second downtime window — thousands of checkouts happen per second. The team uses PM2 cluster mode with 8 instances behind an Nginx load balancer. A hotfix deploy runs `pm2 reload checkout-service`, restarting instances one by one. Each restarting instance is removed from Nginx's upstream pool (via a health check failing temporarily), restarts with the new code, passes `/health`, gets added back to the pool — then the next instance starts. Throughout this, 7/8 instances are always serving, and Nginx never routes a request to a dead instance. Total user-visible impact: zero.

## 🟡 Real Example Hindi mein
**Amazon-style flash sale deploy:** Big Billion Days-style sale के दौरान, checkout service 5 second का भी downtime afford नहीं कर सकती — हज़ारों checkouts per second हो रहे होते हैं। Team PM2 cluster mode में 8 instances चलाती है, Nginx load balancer के पीछे। Hotfix deploy `pm2 reload checkout-service` चलाता है, instances को एक-एक करके restart करता है। हर restarting instance को Nginx के upstream pool से temporarily हटा दिया जाता है (health check fail होने से), नया code लेकर restart होता है, `/health` pass करता है, pool में वापस add होता है — फिर अगला instance start होता है। इस पूरे समय, 7/8 instances हमेशा serving करते रहते हैं, और Nginx कभी किसी dead instance को request नहीं भेजता। User को दिखने वाला impact: zero।

---

## 💻 Code Example — Basic

```javascript
// server.js — graceful shutdown is the FOUNDATION of zero-downtime deploys
const express = require('express');
const app = express();

app.get('/health', (req, res) => res.status(200).json({ status: 'ok' })); // health check endpoint

app.get('/orders/:id', async (req, res) => {
  // simulate a slow DB call — this request must be allowed to FINISH during shutdown
  await new Promise((resolve) => setTimeout(resolve, 2000));
  res.json({ orderId: req.params.id, status: 'confirmed' });
});

const server = app.listen(3000, () => console.log(`PID ${process.pid} listening`));

// ─── GRACEFUL SHUTDOWN ──────────────────────────────────────────────────
// PM2 sends SIGINT when reloading this instance (cluster mode rolling restart)
process.on('SIGINT', () => {
  console.log(`PID ${process.pid}: received SIGINT, draining connections...`);

  server.close(() => {
    // server.close() stops accepting NEW connections,
    // but waits for in-flight requests (like the 2s order lookup above) to finish
    console.log(`PID ${process.pid}: all connections drained, exiting.`);
    process.exit(0); // clean exit — PM2 considers this a successful restart step
  });

  // Safety net: force-exit if draining takes too long (hung connections)
  setTimeout(() => {
    console.error(`PID ${process.pid}: forced shutdown after timeout`);
    process.exit(1);
  }, 10000); // 10 second grace period
});
```

```bash
# Basic zero-downtime deploy with PM2
pm2 start server.js -i max --name "checkout-service"  # start 4 instances (4-core box)

# Deploy new code:
git pull origin main                                    # get new code
npm install                                              # install any new deps
pm2 reload checkout-service                              # ROLLING restart, not `pm2 restart`!

# Verify all instances came back healthy
pm2 list
```

## 💻 Code Example — Advanced

```javascript
// advanced-graceful-shutdown.js — production pattern with connection tracking + DB cleanup
const express = require('express');
const app = express();
let isShuttingDown = false;       // flag to reject new work during shutdown
let activeConnections = 0;        // track in-flight requests manually

// Middleware: track active requests, reject new ones mid-shutdown
app.use((req, res, next) => {
  if (isShuttingDown) {
    res.set('Connection', 'close');                 // tell client not to reuse this connection
    return res.status(503).json({ error: 'Server restarting, retry shortly' });
  }
  activeConnections++;
  res.on('finish', () => activeConnections--);        // decrement when response is sent
  next();
});

// Health check — load balancer polls this; returns 503 during shutdown so LB stops routing here
app.get('/health', (req, res) => {
  if (isShuttingDown) return res.status(503).json({ status: 'draining' });
  res.status(200).json({ status: 'ok', activeConnections });
});

app.post('/payments', async (req, res) => {
  // simulate payment processing
  await new Promise((r) => setTimeout(r, 1500));
  res.json({ status: 'success' });
});

const server = app.listen(3000, () => console.log(`PID ${process.pid} ready`));

// ─── GRACEFUL SHUTDOWN SEQUENCE ─────────────────────────────────────────
async function shutdown(signal) {
  console.log(`PID ${process.pid}: ${signal} received, starting graceful shutdown`);
  isShuttingDown = true;                 // 1. stop claiming to be healthy — LB removes us from pool

  // 2. Wait a moment for the load balancer to notice /health failing and stop sending new traffic
  await new Promise((r) => setTimeout(r, 2000));

  // 3. Stop accepting new connections at the HTTP server level
  server.close(async () => {
    console.log(`PID ${process.pid}: HTTP server closed`);

    // 4. Close DB connections, flush logs, etc. cleanly
    // await mongoose.connection.close();
    // await redisClient.quit();

    process.exit(0);                     // 5. exit cleanly — PM2 moves to the next instance
  });

  // 6. Hard timeout safety net — don't hang forever waiting on a stuck connection
  setTimeout(() => {
    console.error(`PID ${process.pid}: forced exit, ${activeConnections} connections still active`);
    process.exit(1);
  }, 15000);
}

process.on('SIGINT', () => shutdown('SIGINT'));    // PM2 reload sends this
process.on('SIGTERM', () => shutdown('SIGTERM'));  // Kubernetes/Docker sends this
```

---

## 🟠 Express.js Integration

```javascript
// Express app designed to be deploy-safe behind Nginx/ALB
const express = require('express');
const app = express();
app.use(express.json());

let draining = false;

// Health endpoint — THE critical piece every LB/orchestrator checks before routing traffic
app.get('/health', (req, res) => {
  if (draining) return res.status(503).send('draining');     // tells LB "don't send me traffic"
  res.status(200).send('ok');
});

app.get('/orders', async (req, res) => {
  const orders = await Order.find({ userId: req.query.userId }); // normal business logic
  res.json({ orders });
});

const server = app.listen(process.env.PORT || 3000);

process.on('SIGTERM', () => {
  draining = true;                                    // mark unhealthy FIRST
  setTimeout(() => {
    server.close(() => process.exit(0));                // then actually stop accepting connections
  }, 3000);                                             // give LB time to notice /health failing
});
```

```nginx
# nginx.conf snippet — upstream health checking (conceptual, via a module like nginx_upstream_check)
upstream checkout_backend {
  server 10.0.1.10:3000 max_fails=1 fail_timeout=5s;  # mark server down after 1 failed health check
  server 10.0.1.11:3000 max_fails=1 fail_timeout=5s;
  server 10.0.1.12:3000 max_fails=1 fail_timeout=5s;
  server 10.0.1.13:3000 max_fails=1 fail_timeout=5s;
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Using `pm2 restart` for production deploys
```bash
# WRONG — kills ALL cluster instances simultaneously, real downtime window
pm2 restart checkout-service

# RIGHT — restarts one instance at a time, others keep serving
pm2 reload checkout-service
```

❌ **Mistake 2:** Killing the process without draining in-flight requests
```javascript
// WRONG — process.exit() immediately, cuts off any request currently being processed
process.on('SIGTERM', () => process.exit(0));

// RIGHT — close the server first, exit only after existing requests finish
process.on('SIGTERM', () => {
  server.close(() => process.exit(0));
});
```

❌ **Mistake 3:** No health check endpoint, so the load balancer can't tell a restarting instance is unavailable
```javascript
// WRONG — load balancer keeps sending traffic to an instance that's mid-restart, causing errors
// (no /health route defined at all)

// RIGHT — expose /health and make it reflect real readiness, including during shutdown
app.get('/health', (req, res) => {
  res.status(isShuttingDown ? 503 : 200).json({ ready: !isShuttingDown });
});
```

---

## 🧠 Tricky Interview Question

**Q: Your app has graceful shutdown code using `server.close()`, but during `pm2 reload`, you still see a handful of failed requests in your logs. What's the most likely missing piece?**

```javascript
process.on('SIGINT', () => {
  server.close(() => process.exit(0));   // closes server immediately on SIGINT
});
```

**Answer:** The missing piece is usually the **load balancer not knowing yet** that the instance is shutting down. `server.close()` stops accepting *new* TCP connections right away, but the load balancer (Nginx/ALB) might still be routing new requests to this instance for a brief window — until its next health check cycle notices the instance is gone. The fix is to mark the instance "unhealthy" via the `/health` endpoint FIRST, wait a few seconds for the load balancer to notice and stop routing (its health-check interval, e.g. 2-5s), and only THEN call `server.close()`. This two-phase approach — "announce unhealthy, wait, then actually close" — is the real pattern behind true zero-downtime deploys, not just closing the server immediately on signal.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `pm2 restart` and `pm2 reload`?**
A1: `pm2 restart` stops and restarts ALL cluster instances at (roughly) the same time — there's a brief window where no instance is serving traffic, causing real downtime. `pm2 reload` restarts cluster instances ONE AT A TIME in a rolling fashion — PM2 waits for each new instance to be up before moving to the next, so at every moment at least N-1 of N instances are serving requests, achieving zero downtime. `reload` only works in cluster mode, not fork mode.

**Q2: What is Blue-Green deployment and how does it differ from PM2's rolling reload?**
A2: Blue-Green maintains two FULLY SEPARATE, identical production environments — "Blue" (currently live) and "Green" (new version). You deploy the new version entirely to Green while Blue keeps serving all live traffic, run tests against Green, then switch the load balancer/DNS to route 100% of traffic to Green instantly. If something's wrong, you switch back to Blue immediately (instant rollback). PM2 reload, in contrast, does a rolling restart WITHIN the same environment/fleet, instance by instance — it's simpler and needs less infrastructure (no duplicate environment), but rollback means reloading again with the old code, which is slower than a Blue-Green instant switch.

**Q3: Why is a graceful shutdown handler for SIGTERM/SIGINT essential for zero-downtime deployment?**
A3: Without it, `process.exit()` (or the default Node behavior on receiving a kill signal) terminates the process immediately, abruptly cutting off any request currently being processed — the client gets a connection reset error. A graceful shutdown handler calls `server.close()`, which stops accepting NEW connections but lets existing in-flight requests complete normally before the process actually exits. This ensures no user-facing request is lost during a restart, which is the core requirement of zero-downtime deployment.

**Q4: How do health checks gate traffic during a deployment, and what happens if you skip them?**
A4: A health check (`/health` endpoint) tells the load balancer or orchestrator whether an instance is ready to receive traffic. During a deploy, the LB only routes requests to instances that report healthy; a newly-started instance that hasn't finished initializing (e.g., still connecting to the DB) will fail its health check and get no traffic until it's actually ready. Skipping health checks means the LB might send live user traffic to an instance that's still starting up or mid-shutdown, causing connection errors, timeouts, and partial failures exactly during the riskiest moment — the deploy itself.

**Q5: How does a Kubernetes rolling deployment compare conceptually to PM2's cluster reload?**
A5: Both follow the same core principle — replace instances/pods gradually while keeping enough healthy ones running to serve all traffic, using health checks to gate the switch. Kubernetes does this at a larger scale and across multiple machines: it uses `readinessProbe` to decide when a new pod can receive traffic and `livenessProbe` to restart unhealthy pods, with the deployment controller managing how many old vs new pods exist at once (`maxUnavailable`/`maxSurge`). PM2 reload does the equivalent within cluster-mode instances on a SINGLE machine. Kubernetes additionally handles scheduling pods across nodes, auto-scaling, and self-healing across an entire fleet — capabilities PM2 alone doesn't provide.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Deploying any production-facing service where users/webhooks must not see downtime (checkout, payments, public APIs)
- Running PM2 in cluster mode on a single server, or any multi-instance/multi-pod setup behind a load balancer
- Your deploy frequency is high enough that even small downtime windows add up to real business cost

❌ Avoid when:
- It's an internal batch/cron job with no live traffic — there's no "downtime" concept to protect against
- A single-instance (fork mode) hobby project where a few seconds of restart downtime is genuinely acceptable and the infrastructure cost of Blue-Green/health-check gating isn't worth it
- Early-stage prototypes where deploy simplicity matters more than deploy smoothness

---

## 📊 Visual Diagram
```
NAIVE DEPLOY vs ZERO-DOWNTIME DEPLOY
──────────────────────────────────────────────────────────

NAIVE (pm2 restart):
  Instances: [1][2][3][4]  all serving
       │
       ▼  (stop all)
  Instances: [ ][ ][ ][ ]  <-- NOBODY serving, requests fail (502/504)
       │
       ▼  (start all with new code)
  Instances: [1'][2'][3'][4']  serving again

ROLLING RELOAD (pm2 reload):
  [1][2][3][4]  all old, all serving
   │
   ▼ restart instance 1 only
  [1'][2][3][4]  3 old still serving, 1 new coming up
   │
   ▼ instance 1 passes health check, restart instance 2
  [1'][2'][3][4]
   │
   ▼ ... repeat ...
  [1'][2'][3'][4']  ALL new, traffic never had a gap

BLUE-GREEN:
  Blue (live, v1) ◀── 100% traffic
  Green (v2, being deployed + tested, 0% traffic)
       │
       ▼ flip load balancer / DNS
  Blue (v1, idle, ready for instant rollback)
  Green (v2, live) ◀── 100% traffic
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Zero Downtime | No dropped requests during deploy | Deploy के दौरान कोई request नहीं खोती |
| Rolling Restart | Restart instances one at a time | एक-एक करके restart |
| Graceful Shutdown | Drain requests before exiting | Exit से पहले requests finish करना |
| Draining | Letting in-flight requests complete | चल रही requests को पूरा होने देना |
| Health Check | Endpoint reporting readiness | Readiness बताने वाला endpoint |
| Blue-Green Deployment | Two environments, instant switch | दो environments, instant switch |
| SIGTERM / SIGINT | OS signals to stop a process | Process रोकने के signals |
| readinessProbe | K8s check before routing traffic | K8s का readiness check |
| livenessProbe | K8s check to detect unhealthy pods | K8s का health check |
| Rollback | Reverting to the previous version | पुराने version पर वापस जाना |

---

## ⚡ 3-Line Summary
**English:**
1. Zero downtime deployment keeps enough healthy old instances serving traffic while new instances start, gated by health checks, so users never see a gap.
2. `pm2 reload` does this via rolling restarts in cluster mode; graceful shutdown (`server.close()` on SIGTERM/SIGINT) ensures in-flight requests finish before an instance exits.
3. Blue-Green deployment and Kubernetes rolling deployments apply the same core idea at larger scale, with instant-switch or automated pod-by-pod replacement respectively.

**Hindi:**
1. Zero downtime deployment में पुराने healthy instances traffic serve करते रहते हैं जब तक नए instances health check पास नहीं करते — users को कोई gap नहीं दिखता।
2. `pm2 reload` cluster mode में rolling restart करता है; graceful shutdown (SIGTERM/SIGINT पर `server.close()`) से in-flight requests exit से पहले पूरी होती हैं।
3. Blue-Green deployment और Kubernetes rolling deployments बड़े scale पर यही concept apply करते हैं — instant-switch या automated pod-by-pod replacement के through।

---

## ➡️ Next Topic
**263. Deploy on AWS EC2** — EC2 instance launch करना, security groups, Nginx + PM2 setup, Elastic IP, और Load Balancer के साथ scaling।
