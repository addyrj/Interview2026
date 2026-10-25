# 227. PM2 Cluster Mode
# हिंदी में: PM2 Cluster Mode — Production-Grade Process Management

---

## 🔵 Simple Definition (English)
**PM2** is a popular production process manager for Node.js that handles clustering, automatic restarts on crash, zero-downtime reloads, log management, and monitoring — all via simple CLI commands, without writing any `cluster` module code yourself. `pm2 start app.js -i max` alone achieves full multi-core clustering with crash recovery built in.

## 🔵 सरल परिभाषा (Hindi)
**PM2** Node.js के लिए एक popular production process manager है जो clustering, crash पर automatic restarts, zero-downtime reloads, log management, और monitoring handle करता है — सब simple CLI commands से, खुद `cluster` module code लिखे बिना। `pm2 start app.js -i max` से ही पूरी multi-core clustering crash recovery के साथ मिल जाती है।

---

## 🔴 Problem it Solves
Hand-rolling the `cluster` module requires writing and maintaining your own worker-restart logic, graceful shutdown handling, log aggregation across multiple processes, and monitoring — all boilerplate that's easy to get subtly wrong (forgotten restart-on-crash handler, no log rotation, no easy way to see per-worker memory/CPU usage). PM2 provides all of this out of the box as a battle-tested, widely-used tool, letting teams get production-grade process management (clustering + resilience + observability) with a single command instead of custom infrastructure code.

## 🔴 यह क्यों बना? (Hindi)
`cluster` module को हाथ से लिखना मतलब खुद worker-restart logic, graceful shutdown handling, कई processes के log aggregation, monitoring सब maintain करना — ये सब boilerplate है जो subtly गलत हो सकता है (crash पर restart handler भूल जाना, log rotation न होना, per-worker memory/CPU usage देखने का आसान तरीका न होना)। PM2 ये सब out of the box देता है एक battle-tested, widely-used tool के रूप में — एक single command से production-grade process management मिल जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Install globally: `npm install -g pm2`
Step 2 → Start your app in cluster mode: `pm2 start app.js -i max` (`-i max` = one instance per CPU core; you can also specify an exact number, e.g., `-i 4`)
Step 3 → PM2 forks the requested number of instances, load-balancing requests across them (built on the same underlying OS-level mechanism as the `cluster` module)
Step 4 → If an instance crashes, PM2 automatically restarts it — configurable restart limits/backoff prevent crash-loop scenarios from spinning endlessly
Step 5 → Deploy a new version with zero downtime: `pm2 reload app` — PM2 restarts instances ONE AT A TIME, keeping some always available to serve traffic during the rollout
Step 6 → Monitor live with `pm2 monit` (CPU/memory per instance) or `pm2 logs` (aggregated logs from all instances in one stream)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Globally install करो: `npm install -g pm2`
Step 2 → App को cluster mode में start करो: `pm2 start app.js -i max` (`-i max` = हर CPU core के लिए एक instance; exact number भी दे सकते हो जैसे `-i 4`)
Step 3 → PM2 requested संख्या में instances fork करता है, requests को उनमें load-balance करता है
Step 4 → Instance crash होने पर, PM2 automatically restart करता है — configurable restart limits/backoff crash-loop scenarios को endlessly spin होने से रोकते हैं
Step 5 → Zero downtime के साथ नया version deploy करो: `pm2 reload app` — PM2 instances को ONE AT A TIME restart करता है, rollout के दौरान हमेशा कुछ available रखते हुए
Step 6 → `pm2 monit` (हर instance का CPU/memory) या `pm2 logs` (सभी instances के aggregated logs एक stream में) से live monitor करो

---

## 🟡 Real World Example
**Paytm's merchant dashboard API** runs under PM2 with `pm2 start ecosystem.config.js --env production`, configured for 8 instances (matching their 8-core VMs). During deployments, instead of taking the entire API down for a restart (causing failed requests for all connected merchants), the team runs `pm2 reload paytm-merchant-api` — PM2 gracefully restarts instances one at a time, draining connections from each before killing it and starting the new code version, so throughout the ENTIRE deployment, 7 of 8 instances are always serving traffic with zero downtime, and PM2's built-in crash counter automatically alerts the on-call engineer via a webhook if any instance restarts more than 3 times in a minute (signaling a real bug, not a transient issue).

## 🟡 Real Example Hindi mein
**Paytm का merchant dashboard API** PM2 के साथ `pm2 start ecosystem.config.js --env production` से चलता है, 8 instances के लिए configured (उनके 8-core VMs के अनुसार)। Deployments के दौरान, पूरे API को restart के लिए नीचे लाने के बजाय (सभी connected merchants के लिए failed requests), team `pm2 reload paytm-merchant-api` चलाती है — PM2 instances को एक-एक करके gracefully restart करता है, पूरे deployment के दौरान 8 में से 7 instances हमेशा traffic serve करते रहते हैं zero downtime के साथ।

---

## 💻 Code Example — Basic

```javascript
// app.js — a plain Express app, NO cluster-specific code needed with PM2!
// This is the beauty of PM2: your application code stays simple
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  // process.env.NODE_APP_INSTANCE is set by PM2 — useful for debugging
  // which instance handled a given request
  res.json({
    message: 'Hello from PM2-managed app',
    instanceId: process.env.NODE_APP_INSTANCE,
    pid: process.pid,
  });
});

app.listen(3000, () => console.log(`App listening on 3000, pid: ${process.pid}`));

module.exports = app;
```

```bash
# Basic PM2 commands — no code changes needed, all via CLI

# Start in cluster mode using ALL available CPU cores
pm2 start app.js -i max --name "my-api"

# Check status of all running instances
pm2 status
# Shows a table: id, name, pid, uptime, cpu %, memory, status (online/errored)

# View aggregated logs from ALL instances in real-time
pm2 logs my-api

# Stop all instances
pm2 stop my-api

# Restart (brief downtime — kills then starts)
pm2 restart my-api

# ZERO-DOWNTIME reload (one instance at a time, always some serving traffic)
pm2 reload my-api

# Save the current process list so it survives server reboots
pm2 save
pm2 startup   # generates a startup script for your OS (systemd, etc.)
```

## 💻 Code Example — Advanced

```javascript
// ecosystem.config.js — PM2's configuration file for production deployments
// Run with: pm2 start ecosystem.config.js --env production
module.exports = {
  apps: [
    {
      name: 'merchant-api',
      script: './app.js',
      instances: 'max',          // one instance per CPU core (or a number like 4)
      exec_mode: 'cluster',      // REQUIRED for multi-instance load balancing

      // Restart behavior tuning
      max_restarts: 10,          // give up auto-restarting after 10 crashes
      min_uptime: '10s',         // a restart counts as a "crash" only if uptime < 10s
      max_memory_restart: '500M', // auto-restart an instance if it exceeds 500MB (leak mitigation)

      // Environment-specific variables
      env: {
        NODE_ENV: 'development',
        PORT: 3000,
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 8080,
      },

      // Logging configuration
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true, // combine logs from all instances into one file

      // Graceful shutdown: give the app time to finish in-flight requests
      kill_timeout: 5000, // wait 5s for graceful shutdown before force-killing
      wait_ready: true,   // wait for the app to signal readiness before considering it "started"
      listen_timeout: 10000,
    },
  ],
};
```

```javascript
// app.js — signaling PM2 when the app is ready (works with wait_ready: true)
const express = require('express');
const app = express();

app.get('/', (req, res) => res.json({ status: 'ok' }));

const server = app.listen(process.env.PORT || 3000, () => {
  console.log(`Ready on port ${process.env.PORT || 3000}`);
  // Tell PM2 this instance is fully ready to receive traffic —
  // important for zero-downtime reloads: PM2 waits for this signal
  // before considering the NEW instance healthy and killing the OLD one
  if (process.send) {
    process.send('ready');
  }
});

// Graceful shutdown handling — PM2 sends SIGINT on reload/stop
process.on('SIGINT', () => {
  console.log('Received SIGINT, closing server gracefully...');
  server.close(() => {
    console.log('Server closed, exiting.');
    process.exit(0);
  });
});
```

---

## 🟠 Express.js Integration

```javascript
// Deploying an Express app with PM2 in a typical CI/CD pipeline

// deploy.sh (simplified)
// #!/bin/bash
// git pull origin main
// npm ci --production
// pm2 reload ecosystem.config.js --env production  # zero-downtime deploy

// health-check middleware — useful alongside PM2's own process monitoring,
// for an external load balancer/uptime checker to verify app-level health
const express = require('express');
const app = express();

let isShuttingDown = false;

app.get('/health', (req, res) => {
  if (isShuttingDown) {
    // During graceful shutdown, tell the load balancer to stop sending
    // NEW traffic to this instance, even though it's still finishing old requests
    return res.status(503).json({ status: 'shutting down' });
  }
  res.json({ status: 'ok', pid: process.pid });
});

const server = app.listen(process.env.PORT || 3000);

process.on('SIGINT', () => {
  isShuttingDown = true; // health check now reports unhealthy immediately
  setTimeout(() => {
    server.close(() => process.exit(0)); // finish in-flight requests, then exit
  }, 1000); // small delay lets the LB notice the health check change first
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `exec_mode: 'cluster'` and only setting `instances`
```javascript
// WRONG: without exec_mode: 'cluster', PM2 runs multiple SEPARATE instances
// in "fork" mode — each tries to bind the SAME port independently, causing
// an EADDRINUSE error (only works if your app doesn't hardcode a shared port
// listener, which is unusual)
module.exports = { apps: [{ name: 'api', script: './app.js', instances: 4 }] };

// CORRECT: explicitly set exec_mode to 'cluster' for proper load balancing
// across instances sharing the same port
module.exports = {
  apps: [{ name: 'api', script: './app.js', instances: 4, exec_mode: 'cluster' }],
};
```

❌ Mistake 2: Using `pm2 restart` instead of `pm2 reload` for production deployments
```bash
# WRONG: `restart` kills ALL instances then starts them — causes a brief
# period where NO instances are serving traffic (downtime)
pm2 restart my-api

# CORRECT: `reload` restarts instances ONE AT A TIME, always keeping some
# online to serve traffic — true zero-downtime deployment
pm2 reload my-api
```

---

## 🧠 Tricky Interview Question

**Q: You deploy a new version with `pm2 reload my-api`, but users briefly see errors during the deployment anyway. What's a likely cause?**
Answer: A common cause is that the NEW instance starts accepting connections and is marked "online" by PM2 BEFORE the app has actually finished its startup work (e.g., connecting to the database, warming a cache) — so early requests routed to it fail or time out while it's still initializing. The fix: use `wait_ready: true` in the PM2 config combined with the app explicitly calling `process.send('ready')` only once it's TRULY ready to serve traffic (DB connected, caches warmed) — PM2 then waits for this signal before considering the reload of that instance complete and moving to the next one, instead of assuming readiness the instant the process starts. Another cause: the OLD instance being killed too quickly without letting its in-flight requests finish — tuning `kill_timeout` to allow enough time for graceful connection draining helps here too.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between PM2's "cluster mode" and "fork mode"?
A1: **Cluster mode** (`exec_mode: 'cluster'`) uses Node's underlying cluster capability — multiple instances share the same port with load balancing, ideal for stateless HTTP servers wanting multi-core utilization. **Fork mode** (default, `exec_mode: 'fork'`) simply runs a SEPARATE independent process per instance, each needing its own port if it's a server — typically used for non-server scripts, workers, or cron-job-style processes rather than load-balanced web servers.

Q2: How does `pm2 reload` achieve zero-downtime deployment?
A2: It restarts instances ONE AT A TIME (not all at once) — stopping instance 1, starting its replacement with the new code, waiting for it to be ready, THEN moving to instance 2, and so on. Throughout the process, at least N-1 of N instances remain online and serving traffic, so from the client's perspective there's no window where the entire service is down.

Q3: What does `max_memory_restart` do, and when is it useful?
A3: It automatically restarts an instance if its memory usage exceeds the specified threshold (e.g., `'500M'`). This is a pragmatic safety net for memory leaks — rather than letting a leaking instance eventually OOM-crash unpredictably (potentially taking down in-flight requests abruptly), PM2 proactively restarts it at a controlled threshold, limiting the leak's blast radius while the actual root cause is being fixed in code.

Q4: Why is `pm2 save` + `pm2 startup` important for production servers?
A4: `pm2 save` persists the current list of running apps/configuration to disk. `pm2 startup` generates an OS-level startup script (systemd on Linux, etc.) so that if the SERVER itself reboots (OS update, hardware restart), PM2 and all its managed apps automatically come back up without manual intervention — essential for production reliability.

Q5: How do you decide between PM2 cluster mode versus deploying with Kubernetes/container orchestration for scaling?
A5: PM2 cluster mode scales within a SINGLE machine across its CPU cores — great for maximizing utilization of one server/VM, simple to set up, good for small-to-medium deployments or as a complement within each container. Kubernetes/container orchestration scales ACROSS MULTIPLE machines/pods, handling cluster-wide load balancing, auto-scaling based on demand, and multi-region deployment — necessary at larger scale. Many production setups actually use BOTH: PM2 cluster mode inside each container/pod (utilizing that pod's CPU allocation), with Kubernetes managing how many pods/containers exist across the broader infrastructure.

---

## 🔷 When to Use + When Not to Use
✅ Use PM2 cluster mode when:
- Deploying a Node.js app on a VM/bare server and wanting simple, reliable multi-core utilization
- Needing production features (auto-restart, zero-downtime reload, log management) without building custom infrastructure
- Running in an environment without a container orchestrator already handling these concerns

❌ Avoid or reconsider when:
- Already running in Kubernetes/ECS with its own scaling, health checks, and rolling deployment mechanisms (PM2 cluster mode inside each pod can still be useful for per-pod core utilization, but PM2's cross-instance deployment features become redundant with the orchestrator's)
- The app isn't stateless across instances (shared state not yet externalized to Redis/DB) — fix that first, regardless of which clustering approach is used

---

## 📊 Visual Diagram
```
PM2 CLUSTER MODE — ZERO-DOWNTIME RELOAD:
────────────────────────────────────────────────
  Before reload: [v1] [v1] [v1] [v1]   (4 instances, all old version)

  pm2 reload my-api:

  Step 1: [v2] [v1] [v1] [v1]   ← instance 1 restarted with new code,
                                    waits for "ready" signal
  Step 2: [v2] [v2] [v1] [v1]   ← instance 2 restarted
  Step 3: [v2] [v2] [v2] [v1]   ← instance 3 restarted
  Step 4: [v2] [v2] [v2] [v2]   ← all instances now on new version

  At every step, at least 3 of 4 instances serve traffic — ZERO downtime

CRASH RECOVERY:
  Instance crashes → PM2 'exit' detected → auto-restart
  (if restarts exceed max_restarts within min_uptime window → PM2 gives up,
   flags as "errored" — prevents infinite crash-loop resource drain)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PM2 | Production process manager for Node.js | Node.js का production process manager |
| cluster mode | Multiple instances sharing a port, load-balanced | एक port share करते कई instances |
| pm2 reload | Zero-downtime, one-at-a-time restart | Zero-downtime, एक-एक करके restart |
| ecosystem.config.js | PM2's app configuration file | PM2 का configuration file |
| max_memory_restart | Auto-restart on exceeding memory threshold | Memory threshold पर auto-restart |
| wait_ready | Wait for app's explicit ready signal | App के ready signal का इंतज़ार |

---

## ⚡ 3-Line Summary
English:
1. PM2 provides production-grade clustering, crash auto-restart, and zero-downtime deployment via simple CLI commands, without hand-writing `cluster` module logic.
2. Use `exec_mode: 'cluster'` with `instances: 'max'` for multi-core load balancing, and `pm2 reload` (never `restart`) for zero-downtime production deployments.
3. Combine `wait_ready`/`process.send('ready')` and `max_memory_restart` to make reloads truly safe and to contain memory leaks automatically.

Hindi:
1. PM2 production-grade clustering, crash auto-restart, और zero-downtime deployment simple CLI commands से देता है, `cluster` module logic हाथ से लिखे बिना।
2. Multi-core load balancing के लिए `exec_mode: 'cluster'` के साथ `instances: 'max'` use करो, और production deployments के लिए `pm2 reload` (कभी `restart` नहीं) use करो।
3. Reloads को truly safe बनाने और memory leaks को automatically contain करने के लिए `wait_ready`/`process.send('ready')` और `max_memory_restart` combine करो।

---

## ➡️ Next Topic
**228. Load Balancing with Node** — multiple server instances के बीच traffic distribute करने के तरीके (nginx, cloud load balancers, DNS-based)।
