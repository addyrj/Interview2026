# 221. Graceful Shutdown in Docker
# हिंदी में: Docker में Graceful Shutdown

---

## 🔵 Simple Definition (English)
**Graceful shutdown** means that when a container is told to stop, the app first stops taking new requests, finishes the requests already running, closes connections (DB, Redis, queues), and only then exits. It is the application-level counterpart to Docker's SIGTERM, and it is what makes deploys invisible to users.

## 🔵 सरल परिभाषा (Hindi)
**Graceful shutdown** का मतलब है कि जब container को रुकने को कहा जाए तो app पहले नए requests लेना बंद करे, चल रहे requests पूरे करे, connections (DB, Redis, queues) बंद करे, और तब exit करे। यह Docker के SIGTERM का app-level हिस्सा है और इसी से deploys users को दिखते नहीं।

---

## 🔴 Problem it Solves
On every deploy, scale-down or server reboot, containers are stopped. A hard kill drops in-flight HTTP requests (users see 502), leaves half-finished jobs in a queue (duplicate or lost emails), skips flushing logs and metrics, and can leave DB transactions or locks hanging. At 20 deploys per day this adds up to many failed payments and angry support tickets.

## 🔴 यह क्यों बना? (Hindi)
हर deploy, scale-down या reboot पर containers रोके जाते हैं। Hard kill चल रहे HTTP requests गिरा देता है (users को 502), queue के आधे jobs छोड़ देता है (email दोहरे या गायब), logs/metrics flush नहीं होते, और DB transactions या locks अटके रह सकते हैं। दिन में 20 deploys पर यह कई failed payments और नाराज़ support tickets बन जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Deploy starts: `docker compose up -d` / `docker stop` / ECS stops the task.
Step 2 → Load balancer / Nginx is told to stop sending new traffic (readiness fails or deregistration).
Step 3 → Docker sends SIGTERM to PID 1 (your app) and starts a timer (stop_grace_period, default 10s).
Step 4 → App handler: flag "shutting down" -> server.close() (no new connections, keep existing).
Step 5 → Wait for in-flight requests / jobs to finish, then close DB, Redis, queue consumers.
Step 6 → process.exit(0) before the timer ends. If the timer ends first -> SIGKILL (exit 137).
Rule → total shutdown time must be LESS than stop_grace_period; set it a bit above your longest request.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Deploy शुरू: `docker compose up -d` / `docker stop` / ECS task रोकता है।
Step 2 → Load balancer / Nginx को नया traffic भेजना बंद करने को कहा जाता है (readiness fail या deregistration)।
Step 3 → Docker PID 1 (आपके app) को SIGTERM भेजता है और timer शुरू (stop_grace_period, default 10s)।
Step 4 → App handler: "shutting down" flag -> server.close() (नए connections नहीं, मौजूदा चलें)।
Step 5 → चल रहे requests / jobs पूरे होने दो, फिर DB, Redis, queue consumers बंद करो।
Step 6 → Timer खत्म होने से पहले process.exit(0)। पहले timer खत्म हुआ -> SIGKILL (exit 137)।
Rule → कुल shutdown समय stop_grace_period से कम हो; इसे अपने सबसे लंबे request से थोड़ा ऊपर रखो।
```

---

## 🟡 Real World Example
A ride-booking backend (Ola-style) runs three Node.js containers behind Nginx. A booking request takes up to 8 seconds (payment gateway call). With default 10-second grace and no handler, a deploy at peak time kills about 4% of in-flight bookings. After the team added a SIGTERM handler, a 2-second pre-stop delay (so Nginx notices the instance is leaving), `server.close()` with a 25-second force timeout, and `stop_grace_period: 30s`, deploy-time errors dropped to zero in the dashboards.

## 🟡 Real Example Hindi mein
Ola जैसा ride-booking backend Nginx के पीछे तीन Node.js containers चलाता है। एक booking request में 8 सेकंड तक लगते हैं (payment gateway call)। Default 10 सेकंड grace और बिना handler के, peak पर deploy से लगभग 4% चल रही bookings मर जाती थीं। Team ने SIGTERM handler, 2 सेकंड pre-stop delay (ताकि Nginx को पता चले instance जा रहा है), 25 सेकंड force timeout वाला `server.close()` और `stop_grace_period: 30s` जोड़ा, तो deploy के समय errors dashboards में शून्य हो गए।

---

## 💻 Code / Config Example — Basic

```javascript
// server-basic.js - minimal graceful shutdown for Express
const express = require('express');               // web framework
const app = express();                            // create app
app.get('/', (req, res) => res.send('hello'));    // sample route

const server = app.listen(3000, () => console.log('listening')); // keep server reference

function shutdown(signal) {                       // one handler for both signals
  console.log(`${signal} received, closing server`);
  server.close(() => {                            // stops new connections, waits for active ones
    console.log('all requests done, exiting');    // called when the last request ends
    process.exit(0);                              // clean exit code 0
  });
  setTimeout(() => process.exit(1), 8000).unref(); // safety net: force exit before Docker's SIGKILL
}

process.on('SIGTERM', () => shutdown('SIGTERM')); // docker stop / orchestrators
process.on('SIGINT', () => shutdown('SIGINT'));   // Ctrl+C in dev
```

```dockerfile
# Dockerfile - exec form so signals reach node (no shell wrapper)
FROM node:20-alpine                               # example base tag
WORKDIR /app                                      # app folder
COPY package*.json ./                             # manifests
RUN npm ci --omit=dev                             # production dependencies
COPY . .                                          # source
USER node                                         # non-root
CMD ["node", "server-basic.js"]                   # exec form: node is PID 1 and gets SIGTERM
```

## 💻 Code / Config Example — Advanced

```javascript
// server.js - production graceful shutdown: readiness flip, keep-alive handling, DB + queue cleanup
const http = require('http');                                  // core http module
const express = require('express');                            // framework
const { Pool } = require('pg');                                // PostgreSQL pool

const app = express();                                         // app
const pool = new Pool({ connectionString: process.env.DATABASE_URL }); // DB pool
let shuttingDown = false;                                      // global flag

app.get('/readyz', (req, res) =>                               // readiness endpoint used by LB/Nginx
  shuttingDown ? res.status(503).send('draining') : res.send('ok')); // 503 once draining

app.use((req, res, next) => {                                  // tell clients to close keep-alive
  if (shuttingDown) res.set('Connection', 'close');            // new requests on old sockets close after reply
  next();
});

app.get('/slow', async (req, res) => {                         // simulates a long request
  await new Promise(r => setTimeout(r, 5000));                 // 5 seconds of work
  res.send('done');
});

const server = http.createServer(app).listen(3000);            // HTTP server

let closing = false;                                           // guard against double signal
async function shutdown(signal) {
  if (closing) return;                                         // ignore second signal
  closing = true;
  shuttingDown = true;                                         // readiness now fails
  console.log(JSON.stringify({ msg: 'shutdown start', signal })); // structured log

  await new Promise(r => setTimeout(r, 2000));                 // let Nginx/LB notice (pre-stop delay)

  const force = setTimeout(() => {                             // hard deadline < stop_grace_period
    console.error('forced exit');
    process.exit(1);                                           // non-zero so you can see it in alerts
  }, 25000).unref();                                           // unref: does not keep the process alive

  server.close(async () => {                                   // all connections ended
    try {
      await pool.end();                                        // close DB connections
      clearTimeout(force);                                     // cancel the deadline
      console.log(JSON.stringify({ msg: 'shutdown complete' }));
      process.exit(0);                                         // success
    } catch (e) {
      console.error(e);
      process.exit(1);
    }
  });
  if (server.closeIdleConnections) server.closeIdleConnections(); // Node 18.2+: drop idle keep-alive sockets
}

process.on('SIGTERM', () => shutdown('SIGTERM'));              // Docker/ECS/K8s
process.on('SIGINT', () => shutdown('SIGINT'));                // local Ctrl+C
```

```yaml
# docker-compose.prod.yml - give the app enough time and use an init process
services:
  api:
    image: myorg/node-api:1.4.2              # Node.js API
    init: true                               # tini as PID 1: forwards signals, reaps zombies
    stop_signal: SIGTERM                     # signal Docker sends (default, explicit for clarity)
    stop_grace_period: 30s                   # must exceed your force timeout (25s) + pre-stop (2s)
    restart: unless-stopped                  # come back after crash
  nginx:
    image: nginx:1.27-alpine                 # proxy
    stop_signal: SIGQUIT                     # nginx graceful stop (finishes requests)
    stop_grace_period: 30s                   # let nginx drain connections
```

Checked with `node --check` (syntax) and YAML parse; the behaviour was not run in Docker here. / Syntax check हुआ; Docker में behaviour नहीं चलाया।

---

## 🟠 My Stack Integration
- **Node.js**: handler as above; use exec-form `CMD ["node", ...]`. Never `CMD npm start` (npm does not forward SIGTERM reliably).
- **FastAPI**: uvicorn handles SIGTERM and runs shutdown events. Use `lifespan` to close DB pools. Give `--timeout-graceful-shutdown 25` (uvicorn flag; check your version supports it). With gunicorn, `--graceful-timeout 25`.
- **Nginx**: official image already uses `STOPSIGNAL SIGQUIT` (graceful). Use `nginx -s reload` for config changes, which also keeps old workers until requests end.
- **React**: static, nothing to drain.
- **AWS**: ECS `stopTimeout` (max 120s on EC2/Fargate) and ALB deregistration delay (default 300s; reduce to 30s) must be coordinated with your app's drain time.
- **VPS**: with systemd + Compose use `TimeoutStopSec` bigger than `stop_grace_period`.

```yaml
# FastAPI service with lifespan shutdown and grace
services:
  fastapi:
    image: myorg/fastapi:2.0.1
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-graceful-shutdown", "25"]  # exec form
    stop_grace_period: 30s                  # larger than uvicorn's 25s
    init: true                              # signal forwarding
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `CMD npm start` or shell-form CMD, so Node never gets SIGTERM and gets SIGKILLed after 10s.
✅ Correct: `CMD ["node","server.js"]` plus `init: true` if needed.

❌ Mistake 2: Handler calls `process.exit(0)` immediately, which defeats the purpose.
✅ Correct: Call `server.close()`, wait for the callback, then exit.

❌ Mistake 3: Keep-alive connections keep `server.close()` waiting forever.
✅ Correct: `closeIdleConnections()` (Node 18.2+), send `Connection: close`, and keep a force timeout.

❌ Mistake 4: `stop_grace_period` shorter than the app's drain time.
✅ Correct: Grace period > pre-stop delay + longest request + cleanup.

❌ Mistake 5: Not removing the instance from the load balancer first, so new requests still arrive during shutdown.
✅ Correct: Fail readiness, wait 2-5 seconds (or use LB deregistration), then close.

---

## 🧠 Tricky Interview Question
**Q:** Your app handles SIGTERM perfectly in local tests, but in production users still get a few 502 errors on every deploy. Why?

**Answer:** Shutdown starts at the same instant the proxy still believes the instance is healthy. Nginx or the ALB keeps sending a few new requests (or reuses keep-alive connections) to a server that has just closed its listener, so they fail with connection refused/reset. The fix is ordering: first make the instance "not ready" (or deregister it) and wait a short delay, then stop accepting connections, then drain. Also set the proxy's upstream keep-alive timeout lower than the app's, and use the ALB deregistration delay.

---

## ⚫ Interview Questions + Answers

Q1: What happens when `docker stop` is called?
A1: SIGTERM to PID 1, wait `stop_grace_period` (10s default), then SIGKILL. `docker stop -t 30` changes the wait.

Q2: Why use `init: true`?
A2: It runs tini as PID 1, which forwards signals and reaps zombie processes. Useful when your app spawns child processes.

Q3: How is graceful shutdown tested?
A3: Start a long request (`curl /slow`), run `docker stop`, and check that the request completes and the exit code is 0. In CI, run it as an integration test.

Q4: What about WebSockets and long jobs?
A4: Notify clients to reconnect (close frame with code 1001), stop consuming from the queue, finish or requeue the current job, and extend the grace period for jobs.

Q5: Exit code 143 vs 137?
A5: 143 = 128+15, ended by SIGTERM unhandled. 137 = 128+9, SIGKILL (grace period ran out or OOM). Seeing 137 on every deploy means shutdown is too slow or ignored.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any HTTP API, WebSocket server, queue worker, cron job in production
- Zero-downtime deploys, autoscaling, spot instances (2-minute notice)
- Services holding DB transactions or locks

❌ Avoid when:
- Never skip it; only the length changes. For stateless tiny scripts the default may be enough
- Do not use long grace periods as an excuse for slow code; investigate slow requests instead

---

## 📊 Visual Diagram
```
 t=0s   deploy -> readiness /readyz returns 503   (LB stops new traffic)
 t=2s   SIGTERM -> app: server.close()            (no new connections)
 t=2-12s in-flight requests finish                 (users see success)
 t=12s  pool.end(), queue closed                   (clean resources)
 t=12s  process.exit(0)                            (exit code 0)
 ----------------------------------------------------------------
 t=32s  if still alive -> SIGKILL (exit 137)       (stop_grace_period 30s)

 Timeline:  [drain LB]--[stop listening]--[finish work]--[cleanup]--[exit]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Graceful shutdown | Finish work, then exit | काम पूरा करके बंद होना |
| Drain | Stop new, finish existing | नया बंद, पुराना पूरा |
| stop_grace_period | Time before SIGKILL | SIGKILL से पहले का समय |
| Pre-stop delay | Wait so LB notices | LB को पता चलने का इंतज़ार |
| tini / init | Tiny PID 1 that forwards signals | Signals forward करने वाला PID 1 |
| Keep-alive | Reused TCP connection | दोबारा use होने वाला connection |

---

## ⚡ 3-Line Summary
English: Handle SIGTERM: fail readiness, stop listening, finish in-flight work, close resources, exit 0.
Keep stop_grace_period longer than your drain time; use exec-form CMD and init.
Test it with a slow request during `docker stop`.

Hindi: SIGTERM handle करो: readiness fail, listening बंद, चल रहा काम पूरा, resources बंद, exit 0।
stop_grace_period को drain time से लंबा रखो; exec-form CMD और init use करो।
`docker stop` के दौरान slow request भेजकर test करो।

---

## ➡️ Next Topic
**222. Signals in Docker (SIGTERM)** - a deeper look at how signals travel to PID 1 and why shell wrappers break shutdown.
