# 207. PM2 — Process Manager
# हिंदी में: PM2 — Process Manager

---

## 🔵 Simple Definition (English)
**PM2** is a production process manager for Node.js applications that keeps your app running continuously — auto-restarting it if it crashes, running it in cluster mode across all CPU cores, managing logs, enabling zero-downtime reloads, and giving you monitoring/management commands — all without you writing any of the `cluster` module's low-level bootstrap code yourself.

## 🔵 सरल परिभाषा (Hindi)
**PM2** Node.js applications के लिए production process manager है जो आपके app को continuously चलाता रहता है — crash होने पर auto-restart, सारे CPU cores पर cluster mode, logs manage करना, zero-downtime reloads, और monitoring commands देता है — बिना `cluster` module का low-level code खुद लिखे।

---

## 🔴 Problem it Solves
```
PROBLEM WITHOUT PM2:
  node app.js → if it crashes, it STAYS crashed until someone notices and restarts it
  Manually writing cluster bootstrap code to use all CPU cores
  No built-in log rotation/aggregation — logs scattered, hard to find
  Deploying a new version means stopping the server (downtime) to restart it
  No easy way to monitor CPU/memory usage of a running Node process

PM2 SOLUTION:
  pm2 start app.js → automatically restarts on crash
  pm2 start app.js -i max → cluster mode across ALL CPU cores, one command
  pm2 logs → aggregated, searchable logs
  pm2 reload app → zero-downtime restart (rolling restart across cluster workers)
  pm2 monit → live CPU/memory dashboard in the terminal
```

## 🔴 यह क्यों बना? (Hindi)
```
Problem: node app.js crash हो तो वो crashed ही रहता है जब तक कोई notice न करे
Manually cluster code लिखना पड़ता
Logs scattered रहते, deploy के समय downtime होता

PM2 solution: pm2 start से auto-restart, -i max से cluster mode
pm2 logs से aggregated logs, pm2 reload से zero-downtime restart
```

---

## 🟢 How it Works — Step by Step

Step 1 → Install globally: `npm install -g pm2`
Step 2 → Start your app: `pm2 start app.js --name "my-api"` — PM2 becomes a supervisor process watching your app
Step 3 → PM2 monitors the process; if it crashes or exits unexpectedly, PM2 automatically restarts it (with configurable restart limits/backoff to avoid infinite crash loops)
Step 4 → For multi-core scaling: `pm2 start app.js -i max` spawns one instance per CPU core internally using cluster mode, WITHOUT you writing any `cluster.fork()` code
Step 5 → `pm2 reload app` performs a rolling restart — one instance at a time is restarted while others keep serving traffic, achieving zero-downtime deploys; `pm2 logs`, `pm2 monit`, `pm2 list` give operational visibility

## 🟢 कैसे काम करता है? (Hindi)
```
1. npm install -g pm2 से install करो
2. pm2 start app.js --name "my-api" से app शुरू करो
3. PM2 process monitor करता है, crash होने पर auto-restart करता है
4. pm2 start app.js -i max से multi-core cluster mode, बिना code लिखे
5. pm2 reload से zero-downtime rolling restart, pm2 logs/monit से visibility
```

---

## 🟡 Real World Example
**Razorpay's internal API services running on production servers:** Rather than hand-rolling cluster bootstrap code and custom crash-recovery scripts for every microservice, teams run `pm2 start server.js -i max --name payment-api`. If the payment-api process ever crashes due to an unexpected bug, PM2 detects the exit and restarts it within milliseconds — customers barely notice a blip instead of the service staying down until an on-call engineer manually intervenes. When deploying a new version, `pm2 reload payment-api` restarts instances one at a time, so there's always at least one healthy instance serving traffic — true zero-downtime deployment.

## 🟡 Real Example Hindi mein
**Razorpay internal API services:** हर microservice के लिए `pm2 start server.js -i max` चलाया जाता है। Crash हो तो PM2 milliseconds में restart कर देता है। Deploy के समय `pm2 reload` से zero-downtime होता है — हमेशा कम से कम एक instance traffic handle कर रहा होता है।

---

## 💻 Code Example — Basic

```javascript
// app.js — a simple Express server, UNCHANGED whether run with `node` or PM2
// Run: npm install express   then  node app.js   OR   pm2 start app.js
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  // process.env.NODE_APP_INSTANCE is set by PM2 when running in cluster mode
  // (0, 1, 2, ... one per instance) — useful for debugging which instance served a request
  res.json({
    pid: process.pid,
    instance: process.env.NODE_APP_INSTANCE ?? 'not running under PM2',
  });
});

app.listen(3000, () => console.log(`Server started, PID ${process.pid}`));

/*
  Try these commands after installing PM2 globally (npm install -g pm2):

  pm2 start app.js --name my-api          # start it, supervised by PM2
  pm2 list                                 # see running processes + status
  pm2 logs my-api                          # tail logs in real time
  pm2 stop my-api                          # stop it
  pm2 restart my-api                       # restart it
  pm2 delete my-api                        # remove it from PM2's process list

  # Kill the process manually to see auto-restart in action:
  kill -9 <pid from `pm2 list`>
  pm2 list   # you'll see it already restarted automatically!
*/
```

## 💻 Code Example — Advanced

```javascript
// ecosystem.config.js
// PM2's recommended production config file — defines how to run your app(s)
// Run: pm2 start ecosystem.config.js --env production
module.exports = {
  apps: [
    {
      name: 'payment-api',
      script: './server.js',
      instances: 'max',              // one instance per CPU core (cluster mode)
      exec_mode: 'cluster',           // explicitly enable cluster mode
      watch: false,                   // don't restart on file changes in production
      max_memory_restart: '500M',     // auto-restart if an instance exceeds 500MB RAM (leak protection)
      env: {
        NODE_ENV: 'development',
        PORT: 3000,
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 8080,
      },
      error_file: './logs/payment-api-error.log',  // separate error logs
      out_file: './logs/payment-api-out.log',       // separate stdout logs
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      restart_delay: 3000,            // wait 3s before restarting a crashed instance
      max_restarts: 10,               // give up auto-restarting after 10 rapid crashes
      min_uptime: '10s',               // must run 10s to count as a "successful" start
    },
    {
      name: 'notification-worker',
      script: './worker.js',
      instances: 2,                    // fixed number, not tied to all cores
      exec_mode: 'fork',                // regular fork mode, not cluster (e.g., for a job worker)
    },
  ],
};
```

```javascript
// server.js — referenced by ecosystem.config.js above
const express = require('express');
const app = express();

// Graceful shutdown handling — PM2 sends SIGINT on `pm2 reload`/`pm2 stop`
process.on('SIGINT', () => {
  console.log('Received SIGINT, closing server gracefully...');
  server.close(() => {
    console.log('Server closed, exiting');
    process.exit(0);
  });
});

app.get('/health', (req, res) => res.json({ status: 'ok', pid: process.pid }));

const server = app.listen(process.env.PORT || 3000, () => {
  console.log(`payment-api running on port ${process.env.PORT || 3000}, env: ${process.env.NODE_ENV}`);
});
```

---

## 🟠 Express.js Integration

```javascript
// How a real Express app is structured to work well under PM2's cluster mode:
// avoid in-memory state that assumes a SINGLE process, and handle graceful shutdown.
const express = require('express');
const app = express();

// ❌ In cluster mode, this counter would be PER-INSTANCE, not global —
// each of the N PM2 instances has its own separate `requestCount`
let requestCount = 0;

app.use((req, res, next) => {
  requestCount++;
  next();
});

app.get('/stats', (req, res) => {
  // Honest about per-instance nature — real global stats need Redis/a shared store
  res.json({ pid: process.pid, requestsOnThisInstance: requestCount });
});

const server = app.listen(process.env.PORT || 3000);

// PM2 relies on this to know the app started successfully (for min_uptime tracking)
// and to gracefully stop it (SIGINT) during `pm2 reload`/`pm2 stop`
process.on('SIGINT', () => {
  server.close(() => process.exit(0));
});

module.exports = app;
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using in-memory state (counters, caches, sessions) in an app running under PM2's cluster mode, not realizing each instance has its OWN separate memory.
✅ Correct: Use Redis or a database for any state that must be consistent across all PM2-managed instances.

```javascript
// Wrong — each of the N cluster instances has its own separate inMemorySessions
const inMemorySessions = {};

// Right — shared store accessible from every instance
const session = await redisClient.get(`session:${sessionId}`);
```

❌ Mistake 2: Not handling `SIGINT`/`SIGTERM` gracefully — PM2's `reload`/`stop` sends these signals expecting the app to finish in-flight requests and exit cleanly; without a handler, connections can be dropped abruptly mid-request.
✅ Correct: Listen for `SIGINT`/`SIGTERM` and call `server.close()` to stop accepting new connections while finishing existing ones.

❌ Mistake 3: Running `pm2 start` directly in the terminal without `pm2 save` + `pm2 startup`, so after a server reboot, PM2 (and your app) doesn't automatically come back up.
✅ Correct: Run `pm2 save` after starting your apps, and `pm2 startup` once to configure PM2 to auto-launch on system boot.

---

## 🧠 Tricky Interview Question

**Question:** You run `pm2 start app.js -i max` on an 8-core machine, then `pm2 reload app`. During the reload, is there ANY moment where zero instances are handling requests (i.e., actual downtime)?

Answer: **No, that's the entire point of `pm2 reload` (as opposed to `pm2 restart`).** `reload` performs a ROLLING restart: it starts a replacement instance, waits for it to be ready (listening), THEN stops exactly one of the old instances — repeating this one-at-a-time for all 8 instances. At every moment during this process, at least 7 (and briefly 9, during the brief overlap of starting the new one before stopping the old one) instances are actively serving traffic. Contrast this with `pm2 restart`, which stops then starts each instance WITHOUT that overlap guarantee in older PM2 behavior for fork mode — in cluster mode specifically, `reload` is the command that guarantees true zero-downtime, which is why it's the recommended command for production deploys, not `restart`.

---

## ⚫ Interview Questions + Answers

Q1: What problem does PM2 solve that plain `node app.js` doesn't?
A1: Plain `node app.js` has no automatic crash recovery (if it crashes, it stays down), no built-in multi-core utilization (requires hand-writing `cluster` module code), no log management, and no zero-downtime deployment mechanism. PM2 wraps all of this into simple CLI commands (`pm2 start`, `-i max`, `pm2 reload`, `pm2 logs`), making it a standard tool for running Node.js in production.

Q2: What's the difference between `pm2 restart` and `pm2 reload`?
A2: `pm2 restart` stops and starts instances (potentially with a brief gap where that instance isn't serving). `pm2 reload` is specifically designed for ZERO-downtime restarts in cluster mode — it starts new instances before stopping old ones, one at a time, ensuring there's always at least one instance available to serve traffic throughout the entire deployment.

Q3: How does `instances: 'max'` relate to the `cluster` module?
A3: Under the hood, PM2's cluster mode (`exec_mode: 'cluster'`, `instances: 'max'`) uses Node's native `cluster` module exactly as you would by hand — it forks one worker per CPU core, all listening on the same port, load-balanced by the primary process. PM2 just automates the fork/restart/monitoring logic so you don't write that bootstrap code yourself.

Q4: Why is `max_memory_restart` useful in production?
A4: It automatically restarts an instance if it exceeds a configured memory threshold (e.g., `500M`), acting as a safety net against memory leaks — rather than letting a leaking process slowly consume all available RAM (potentially crashing the whole machine or triggering an OOM-kill of unrelated processes), PM2 proactively restarts just that one instance, limiting the damage.

Q5: What commands would you use to make PM2-managed apps survive a server reboot?
A5: Run `pm2 save` to persist the current list of running apps/configuration, then `pm2 startup` (run once per machine) to generate and install a system startup script (systemd/init.d, depending on OS) that automatically runs `pm2 resurrect` on boot, restoring all previously-saved apps without manual intervention.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running Node.js in production and need crash recovery, multi-core scaling, and zero-downtime deploys without writing that infrastructure yourself
- Managing multiple Node.js apps/workers on the same machine with centralized logs and monitoring

❌ Avoid when:
- Your deployment already uses container orchestration (Kubernetes) that handles restarts/scaling/rolling-deploys at the POD level — running PM2 cluster mode INSIDE each container can be redundant or even conflict with the orchestrator's own scaling logic (common practice there is one process per container, scaled by replicas instead)
- Simple local development — plain `node app.js` or `nodemon` is simpler for iterating

---

## 📊 Visual Diagram
```
PM2 ARCHITECTURE
──────────────────────────────────────────
         pm2 start app.js -i max
                   │
                   ▼
         ┌───────────────────┐
         │   PM2 God Process  │ (supervises everything)
         └─────────┬──────────┘
      ┌─────────────┼─────────────┬─────────────┐
      ▼              ▼             ▼             ▼
  Instance 0      Instance 1   Instance 2    Instance 3
 (cluster mode, one per CPU core, auto-restart on crash)

  pm2 reload app:
  start new-0 → ready → stop old-0
  start new-1 → ready → stop old-1   ← rolling, zero downtime
  ... continues for all instances
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PM2 | Node.js production process manager | Node.js production process manager |
| Cluster mode | Multi-instance load-balanced execution | Multi-instance load-balanced execution |
| Zero-downtime reload | Rolling restart with no downtime | Bina downtime rolling restart |
| ecosystem.config.js | PM2's app configuration file | PM2 का app configuration file |
| max_memory_restart | Auto-restart on memory threshold | Memory threshold पर auto-restart |
| pm2 startup/save | Persist apps across reboots | Reboot के बाद apps persist करना |

---

## ⚡ 3-Line Summary
English:
1. PM2 is a production process manager providing auto-restart, cluster mode, log management, and zero-downtime reloads for Node.js apps.
2. `pm2 start app.js -i max` scales across all CPU cores without hand-writing `cluster` module code.
3. Always handle graceful shutdown (SIGINT/SIGTERM) and avoid in-memory state assumptions since each cluster instance has separate memory.

Hindi:
1. PM2 production process manager है जो auto-restart, cluster mode, log management, zero-downtime reloads देता है।
2. `pm2 start app.js -i max` से सारे CPU cores पर scale होता है, बिना cluster code लिखे।
3. Graceful shutdown handle करो, in-memory state पर भरोसा मत करो — हर instance की memory अलग है।

---

## ➡️ Next Topic
**208. Testing in Node.js — Why Important** — Moving into the Testing fundamentals section, starting with why automated testing matters.
