# 260. PM2 — Complete Guide
# हिंदी में: PM2 — Production Process Manager

---

## 🔵 Simple Definition (English)
**PM2** is a production process manager for Node.js applications. It keeps your app running forever (auto-restart on crash), runs it in **cluster mode** to use all CPU cores, manages logs, monitors CPU/memory, and can start your app automatically when the server reboots. Instead of running `node server.js` manually in a terminal (which dies when you close SSH), PM2 runs it as a managed background daemon.

## 🔵 सरल परिभाषा (Hindi)
**PM2** Node.js applications के लिए एक production process manager है। यह आपके app को हमेशा चलता रखता है (crash होने पर auto-restart), **cluster mode** में सभी CPU cores use करता है, logs manage करता है, CPU/memory monitor करता है, और server reboot होने पर app को automatically start कर सकता है। `node server.js` manually terminal में चलाने के बजाय (जो SSH बंद करने पर मर जाता है), PM2 इसे एक managed background daemon की तरह चलाता है।

---

## 🔴 Problem it Solves
```
WITHOUT PM2 (raw node server.js):
  $ node server.js
  Server running on port 3000
  
  Problems:
  1. Close terminal / SSH disconnect → process dies instantly
  2. App crashes (unhandled exception) → server is DOWN, nobody restarts it
  3. Single process → only uses 1 CPU core, even on a 4-core/8-core machine
  4. No centralized logs → console.log scattered, lost on restart
  5. Server reboots (AWS maintenance, power outage) → app doesn't come back
  6. No easy way to see CPU/memory usage of the running app
  7. Deploying a new version means manually kill + restart → downtime + risk

WITH PM2:
  $ pm2 start server.js -i max --name "zomato-api"
  
  Solutions:
  1. Runs as a background daemon — survives SSH disconnect
  2. Auto-restarts on crash (configurable max restarts to avoid infinite loop)
  3. Cluster mode (-i max) spawns one process per CPU core, load balanced
  4. pm2 logs — centralized, rotatable log files
  5. pm2 startup + pm2 save — app restarts automatically after server reboot
  6. pm2 monit — live CPU/memory dashboard in terminal
  7. pm2 reload — rolling restart, zero downtime deploys
```

## 🔴 यह क्यों बना? (Hindi)
Raw `node server.js` production के लिए काफी नहीं है। Terminal बंद होने पर process मर जाता है, crash होने पर कोई restart नहीं करता, और सिर्फ 1 CPU core use होता है जबकि production servers में 4-8 cores होते हैं। PM2 इन सभी problems को solve करता है: daemon की तरह background में चलाना, auto-restart, cluster mode (multi-core), centralized logging, और server reboot के बाद automatic startup। Zomato, Swiggy जैसी companies production में raw node के बजाय हमेशा एक process manager (PM2 या container orchestrator) use करती हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Install PM2 globally: `npm install -g pm2`
Step 2 → Start your app: `pm2 start server.js --name "api-server"` — PM2 forks the process and keeps a reference (PID) in its own daemon process (`pm2 daemon`, called God process).
Step 3 → PM2's God daemon monitors the child process. If it exits/crashes, PM2 immediately spawns a new one (auto-restart), incrementing a restart counter.
Step 4 → For multi-core usage: `pm2 start server.js -i max` — PM2 spawns N instances (N = CPU cores) in **cluster mode** using Node's built-in `cluster` module internally, and load-balances incoming connections across them (round-robin).
Step 5 → Logs: every instance's stdout/stderr is captured into log files under `~/.pm2/logs/`. `pm2 logs` streams them live.
Step 6 → Monitoring: `pm2 monit` opens a live terminal dashboard showing CPU%, memory, and logs per process.
Step 7 → Persistence across reboot: `pm2 startup` generates and installs a systemd/init script for your OS. `pm2 save` dumps the current process list to `~/.pm2/dump.pm2`. On server reboot, the systemd service calls `pm2 resurrect`, which reads that dump and restarts everything exactly as it was.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → PM2 globally install करो: `npm install -g pm2`
Step 2 → App start करो: `pm2 start server.js --name "api-server"` — PM2 process को fork करता है और अपने daemon (God process) में उसका reference रखता है।
Step 3 → PM2 का daemon child process को monitor करता है। Crash होने पर PM2 तुरंत नया process spawn कर देता है (auto-restart), restart counter बढ़ाता है।
Step 4 → Multi-core के लिए: `pm2 start server.js -i max` — PM2 N instances spawn करता है (N = CPU cores), Node के `cluster` module का use करके, और incoming connections को round-robin से balance करता है।
Step 5 → Logs: हर instance का stdout/stderr `~/.pm2/logs/` में capture होता है। `pm2 logs` live stream देता है।
Step 6 → Monitoring: `pm2 monit` से live dashboard मिलता है — CPU%, memory, logs per process।
Step 7 → Reboot के बाद persistence: `pm2 startup` systemd/init script generate करता है। `pm2 save` current process list को `~/.pm2/dump.pm2` में save करता है। Reboot पर systemd `pm2 resurrect` call करता है जो dump पढ़कर सब कुछ वापस start कर देता है।

---

## 🟡 Real World Example
**Swiggy's order-service on an EC2 instance:** The team runs `pm2 start order-service.js -i max --name swiggy-orders`. The EC2 instance has 4 vCPUs, so PM2 spawns 4 cluster instances, each handling ~25% of incoming order requests during lunch-hour traffic spikes. One instance hits a memory leak and crashes at 1 AM — PM2 restarts it in under a second, nobody gets paged. During a planned deploy, `pm2 reload swiggy-orders` restarts the 4 instances one at a time so active orders never get dropped. After an AWS scheduled maintenance reboot, `pm2 resurrect` (triggered automatically via the systemd service from `pm2 startup`) brings the whole order-service back up without anyone SSH-ing in.

## 🟡 Real Example Hindi mein
**Swiggy का order-service EC2 instance पर:** Team `pm2 start order-service.js -i max --name swiggy-orders` चलाती है। EC2 instance में 4 vCPUs हैं, तो PM2 4 cluster instances spawn करता है, हर एक lunch-hour traffic के ~25% requests handle करता है। एक instance memory leak की वजह से रात 1 बजे crash होता है — PM2 उसे 1 second में restart कर देता है, किसी को page नहीं आता। Planned deploy के दौरान, `pm2 reload swiggy-orders` 4 instances को एक-एक करके restart करता है ताकि active orders drop ना हों। AWS scheduled maintenance reboot के बाद, `pm2 resurrect` (systemd service के through automatic) पूरा order-service बिना किसी SSH के वापस ला देता है।

---

## 💻 Code Example — Basic

```javascript
// server.js — a simple Express server to manage with PM2
const express = require('express');               // import express
const app = express();                             // create app instance

// Simple route that reports which PM2 instance handled the request
app.get('/', (req, res) => {
  res.json({
    message: 'Hello from Zomato API',               // response payload
    pid: process.pid,                                // process id — different per cluster instance
    instanceId: process.env.NODE_APP_INSTANCE,        // PM2 sets this for each cluster worker (0,1,2,3...)
  });
});

// Route to simulate a crash — to test PM2 auto-restart
app.get('/crash', (req, res) => {
  process.exit(1);                                   // force exit, PM2 should auto-restart this instance
});

const PORT = process.env.PORT || 3000;               // read port from env, default 3000
app.listen(PORT, () => console.log(`Worker ${process.pid} listening on ${PORT}`));
```

```bash
# Basic PM2 CLI commands — run these in terminal, not in server.js

npm install -g pm2                       # install PM2 globally (one-time setup)

pm2 start server.js --name "zomato-api"  # start app with a readable name
pm2 list                                 # show all running PM2-managed processes
pm2 logs zomato-api                      # stream live logs for this app
pm2 stop zomato-api                      # stop the process (keeps it in PM2 list)
pm2 restart zomato-api                   # hard restart (brief downtime)
pm2 delete zomato-api                    # remove completely from PM2's list
pm2 describe zomato-api                  # detailed info: uptime, restarts, memory
```

## 💻 Code Example — Advanced

```bash
# advanced-pm2-usage.sh — production-grade PM2 setup commands

# 1. Start in CLUSTER MODE using all available CPU cores
pm2 start server.js -i max --name "zomato-api" \
  --max-memory-restart 300M              # auto-restart an instance if it exceeds 300MB RAM

# 2. Check how many instances are running and their health
pm2 list
# ┌─────┬────────────────┬─────────┬─────────┬──────────┬────────┬──────┐
# │ id  │ name           │ mode    │ pid     │ status   │ cpu    │ mem  │
# ├─────┼────────────────┼─────────┼─────────┼──────────┼────────┼──────┤
# │ 0   │ zomato-api     │ cluster │ 11234   │ online   │ 0.2%   │ 42mb │
# │ 1   │ zomato-api     │ cluster │ 11235   │ online   │ 0.1%   │ 40mb │
# │ 2   │ zomato-api     │ cluster │ 11236   │ online   │ 0.3%   │ 41mb │
# │ 3   │ zomato-api     │ cluster │ 11237   │ online   │ 0.2%   │ 39mb │
# └─────┴────────────────┴─────────┴─────────┴──────────┴────────┴──────┘

# 3. Live monitoring dashboard — CPU/memory per instance, live logs
pm2 monit

# 4. ZERO-DOWNTIME RELOAD — restarts instances one by one (not all at once)
pm2 reload zomato-api                    # old instance stays alive until new one is ready

# 5. LOG MANAGEMENT
pm2 logs zomato-api --lines 200          # last 200 lines
pm2 flush zomato-api                     # clear old logs (avoid disk filling up)
pm2 install pm2-logrotate                # auto log rotation module (important in prod!)
pm2 set pm2-logrotate:max_size 10M       # rotate when log file hits 10MB
pm2 set pm2-logrotate:retain 7           # keep only last 7 rotated log files

# 6. STARTUP SCRIPT — survive server reboot
pm2 startup                              # generates + installs systemd service (run the printed sudo command)
pm2 save                                 # saves current process list as the "resurrection" snapshot

# After a server reboot, systemd automatically runs:
#   pm2 resurrect   → restores all apps exactly as they were when `pm2 save` ran

# 7. GRACEFUL SHUTDOWN handling inside the app (important for cluster reload)
#    server.js should listen for SIGINT/SIGTERM and close connections cleanly:
```

```javascript
// graceful-shutdown.js — pairs with `pm2 reload` for true zero downtime
const express = require('express');
const app = express();
const server = app.listen(3000);

// PM2 sends SIGINT during `pm2 reload` to ask this instance to shut down
process.on('SIGINT', () => {
  console.log(`Worker ${process.pid} draining connections...`);
  server.close(() => {                         // stop accepting NEW connections
    console.log(`Worker ${process.pid} closed, exiting.`);
    process.exit(0);                            // exit cleanly only after existing requests finish
  });
});
```

---

## 🟠 Express.js Integration

```javascript
// ecosystem-ready Express app — the actual app file PM2 will run
const express = require('express');
const app = express();
app.use(express.json());

// Health check route — used by load balancers AND by PM2-adjacent monitoring
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', pid: process.pid, uptime: process.uptime() });
});

// Example business route — order placement (Zomato style)
app.post('/orders', (req, res) => {
  const { restaurantId, items } = req.body;             // destructure request
  if (!restaurantId || !items?.length) {
    return res.status(400).json({ error: 'restaurantId and items required' });
  }
  // ... save order to DB ...
  res.status(201).json({ orderId: 'ORD123', pid: process.pid });  // pid shows which cluster worker handled it
});

const PORT = process.env.PORT || 3000;
const server = app.listen(PORT, () => console.log(`PID ${process.pid} up on ${PORT}`));

// Graceful shutdown — REQUIRED for pm2 reload / cluster mode to be truly zero-downtime
process.on('SIGINT', () => server.close(() => process.exit(0)));
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Using `pm2 restart` for deploys instead of `pm2 reload`
```javascript
// WRONG — restart kills ALL instances at once, brief total downtime
// $ pm2 restart zomato-api

// RIGHT — reload restarts one instance at a time (rolling), zero downtime
// $ pm2 reload zomato-api
```

❌ **Mistake 2:** Forgetting `pm2 save` after `pm2 startup`
```bash
# WRONG — app runs fine now, but after a server reboot nothing comes back
pm2 start server.js --name api
pm2 startup
# (forgot pm2 save!)

# RIGHT — always save the process list after any start/stop/delete change
pm2 start server.js --name api
pm2 startup
pm2 save              # <-- without this, pm2 resurrect has nothing to restore
```

❌ **Mistake 3:** Not setting `--max-memory-restart` and letting a memory leak crash the server
```bash
# WRONG — no memory cap, a leaking process can consume all RAM and crash the whole EC2 box
pm2 start server.js -i max

# RIGHT — cap memory per instance; PM2 restarts that instance before it kills the server
pm2 start server.js -i max --max-memory-restart 400M
```

---

## 🧠 Tricky Interview Question

**Q: You run `pm2 start server.js -i max` on a 4-core machine. Inside `server.js` you have `let counter = 0;` at the top level, incremented on every request. Will `counter` be shared across all requests?**

```javascript
// server.js
let counter = 0;
app.get('/inc', (req, res) => {
  counter++;
  res.json({ counter, pid: process.pid });
});
```

**Answer:** No. In cluster mode, PM2 spawns **4 separate OS processes**, each with its own V8 memory space and its own copy of `counter`. A request load-balanced to instance #2 only increments instance #2's `counter` — instance #0's `counter` is unaffected. Hitting `/inc` repeatedly will show the counter looping low values across different `pid`s, not one steadily growing number. For shared state across cluster workers, you need an external store like **Redis**, not in-memory variables — this is the same reason sessions/caches must live outside the process in a clustered/multi-instance deployment.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between PM2's `fork` mode and `cluster` mode?**
A1: **Fork mode** (`pm2 start server.js`) runs exactly one instance of your app as a single process — simplest, but uses only one CPU core. **Cluster mode** (`pm2 start server.js -i max` or `-i 4`) spawns multiple Node.js processes under Node's built-in `cluster` module, with PM2 acting as a master that load-balances incoming TCP connections (round-robin) across the worker processes. Cluster mode uses all available CPU cores, giving much higher throughput for CPU-bound or high-concurrency apps. Cluster mode requires your app to be stateless (or use external storage) since each worker has separate memory.

**Q2: How does PM2 achieve zero-downtime deploys with `pm2 reload`?**
A2: `pm2 reload` performs a **rolling restart**: it stops and restarts cluster instances one at a time, waiting for each new instance to be "ready" (listening) before moving to the next. At every moment, at least N-1 instances are serving traffic, so incoming requests are never dropped. This is different from `pm2 restart`, which kills all instances simultaneously and briefly causes complete downtime while they all come back up.

**Q3: What does `pm2 startup` + `pm2 save` actually do under the hood?**
A3: `pm2 startup` detects your OS/init system (systemd on most Linux distros) and generates + installs a service unit file that calls `pm2 resurrect` on boot. `pm2 save` serializes PM2's current in-memory process list (app name, script path, cluster instances, env vars) into `~/.pm2/dump.pm2`. On the next server boot, systemd starts the PM2 daemon, which runs `pm2 resurrect`, reading that dump file and restarting every app exactly as configured — without any manual intervention.

**Q4: If a Node.js app has a memory leak, how does PM2 help mitigate it in production?**
A4: Using `--max-memory-restart <size>` (e.g., `300M`), PM2 monitors each process's memory usage and automatically restarts any instance that exceeds the threshold — before it can consume all server RAM and crash the entire machine (including other apps/services on it). This doesn't fix the leak, but it contains the blast radius and keeps the service available while the actual leak is investigated and patched.

**Q5: Why might you choose PM2 over Docker/Kubernetes for a small production app, and when would you outgrow it?**
A5: PM2 is much simpler to set up — no containers, no orchestration layer, just SSH into one EC2 box, install PM2, and run the app with cluster mode and auto-restart. It's great for a single-server or small-team setup (startups, side projects, early-stage products). You outgrow PM2 when you need: scaling across **multiple machines** (not just multiple cores on one box), rolling deploys across a fleet with automated health-check-gated traffic shifting, auto-scaling based on load, or isolation between services with different dependencies — that's when Docker + ECS/Kubernetes becomes the better fit.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running a Node.js app on a single VM/EC2 instance in production
- You want automatic crash recovery without writing your own supervisor script
- You need to use all CPU cores on a box without manually forking workers yourself
- You want zero-downtime deploys on a single server without container orchestration

❌ Avoid when:
- You're already using Docker + Kubernetes/ECS — those platforms have their own process supervision, restart policies, and rolling deploy mechanisms; running PM2 *inside* a container is usually redundant
- You need to scale across many machines automatically (PM2 manages processes on one box, not a fleet) — use an orchestrator instead
- Your app is a short-lived script/cron job, not a long-running server

---

## 📊 Visual Diagram
```
PM2 CLUSTER MODE ON A 4-CORE SERVER
──────────────────────────────────────────────────────────

                     ┌─────────────────────┐
  Incoming traffic ──▶    PM2 Master /      │
                     │   Load Balancer      │
                     └──────────┬───────────┘
                 ┌───────┬──────┼──────┬───────┐
                 ▼       ▼      ▼      ▼
            ┌────────┐┌───────┐┌───────┐┌───────┐
            │Worker 0││Worker1││Worker2││Worker3│   <- 4 separate Node processes
            │ pid:111││pid:112││pid:113││pid:114│      (one per CPU core)
            └────────┘└───────┘└───────┘└───────┘
                 │         │        │        │
            each has its OWN memory — counter/cache NOT shared!
                 │
                 ▼
          [ Shared state needs Redis / DB, not in-memory vars ]

ZERO-DOWNTIME RELOAD (pm2 reload):
  Worker0 [old] → restart → Worker0 [new]  (others still serving)
  Worker1 [old] → restart → Worker1 [new]
  Worker2 [old] → restart → Worker2 [new]
  Worker3 [old] → restart → Worker3 [new]
  At every instant: traffic always has 3/4 workers available.

SERVER REBOOT RECOVERY:
  Server reboots → systemd starts pm2 daemon → pm2 resurrect
       → reads ~/.pm2/dump.pm2 → restarts every saved app
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PM2 | Node.js production process manager | Production process manager |
| Cluster Mode | Multiple processes, one per CPU core | Multi-core पर multiple processes |
| Fork Mode | Single instance, single process | सिर्फ एक process |
| pm2 reload | Rolling restart, zero downtime | एक-एक करके restart |
| pm2 restart | Hard restart, brief downtime | सभी एक साथ restart (downtime) |
| pm2 startup | Generates OS startup script | Reboot पर auto-start script |
| pm2 save | Saves process list snapshot | Process list snapshot save |
| pm2 resurrect | Restores saved processes on boot | Reboot पर processes वापस लाना |
| God Process | PM2's internal daemon/supervisor | PM2 का internal daemon |
| max-memory-restart | Auto-restart on exceeding RAM limit | RAM limit पार होने पर restart |

---

## ⚡ 3-Line Summary
**English:**
1. PM2 is a production process manager that keeps Node apps running as background daemons with auto-restart on crash.
2. Cluster mode (`-i max`) uses all CPU cores by running multiple independent processes with separate memory, load-balanced by PM2.
3. `pm2 startup` + `pm2 save` ensure your app survives a server reboot; `pm2 reload` gives zero-downtime rolling deploys.

**Hindi:**
1. PM2 एक production process manager है जो Node apps को background daemon की तरह चलाता है और crash पर auto-restart करता है।
2. Cluster mode (`-i max`) सभी CPU cores use करता है, multiple separate processes चलाकर, जिनकी memory अलग-अलग होती है और PM2 load-balance करता है।
3. `pm2 startup` + `pm2 save` से app server reboot के बाद भी वापस आ जाता है; `pm2 reload` से zero-downtime rolling deploy मिलता है।

---

## ➡️ Next Topic
**261. PM2 Ecosystem File** — `ecosystem.config.js` में multiple apps/environments define करना, और `pm2 deploy` से git-based remote deployment।
