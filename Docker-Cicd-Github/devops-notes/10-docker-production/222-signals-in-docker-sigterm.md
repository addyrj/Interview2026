# 222. Signals in Docker (SIGTERM)
# हिंदी में: Docker में Signals (SIGTERM)

---

## 🔵 Simple Definition (English)
A **signal** is a small message the operating system sends to a process ("please stop", "stop now", "reload config"). When you run `docker stop`, Docker sends **SIGTERM** to the main process (PID 1) of the container, waits for a grace period (10 seconds by default), and then sends **SIGKILL** if the process is still alive. Your app must handle SIGTERM to shut down cleanly.

## 🔵 सरल परिभाषा (Hindi)
**Signal** एक छोटा message है जो operating system किसी process को भेजता है ("रुक जाओ", "अभी बंद हो जाओ", "config reload करो")। जब आप `docker stop` चलाते हो, Docker container के main process (PID 1) को **SIGTERM** भेजता है, grace period (default 10 सेकंड) तक इंतज़ार करता है, और अगर process फिर भी ज़िंदा है तो **SIGKILL** भेज देता है। आपके app को SIGTERM handle करना चाहिए ताकि वह साफ़-सुथरे तरीके से बंद हो।

---

## 🔴 Problem it Solves
Without proper signal handling, every deploy kills containers in the middle of work. A payment request that was half-processed is cut off, database transactions are left open, files are half-written, and users see 502 errors. Worse, many containers never even receive SIGTERM: if you start your app through a shell (`CMD npm start` or `CMD "node server.js"`), the shell becomes PID 1 and does not forward signals to Node.js. Docker then waits the full 10 seconds and sends SIGKILL, so every deploy is slow (10 s per container) and violent.

## 🔴 यह क्यों बना? (Hindi)
सही signal handling के बिना हर deploy पर containers काम के बीच में मार दिए जाते हैं। आधा process हुआ payment request कट जाता है, database transactions खुले रह जाते हैं, files आधी लिखी रह जाती हैं और users को 502 error दिखता है। और बुरा यह कि कई containers को SIGTERM मिलता ही नहीं: अगर आप app को shell से start करते हो (`CMD npm start` या `CMD "node server.js"`) तो shell PID 1 बन जाता है और signal को Node.js तक forward नहीं करता। तब Docker पूरे 10 सेकंड रुकता है और SIGKILL भेजता है, यानी हर deploy धीमा और हिंसक होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You run `docker stop web` (or CI/CD / Compose / Swarm / Kubernetes replaces the container).
Step 2 → Docker daemon sends SIGTERM (or the image's STOPSIGNAL) to PID 1 inside the container.
Step 3 → If PID 1 is your app and it has a handler: it stops accepting new requests,
         finishes in-flight requests, closes DB / Redis connections, then exits with code 0.
Step 4 → If PID 1 is a shell that ignores the signal, nothing happens (app keeps running).
Step 5 → After the grace period (default 10s, change with `-t` or `stop_grace_period`)
         Docker sends SIGKILL. SIGKILL cannot be caught: the process dies instantly (exit code 137).
Step 6 → Container state becomes "exited". Exit 0/143 = clean, 137 = was force-killed.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → आप `docker stop web` चलाते हो (या CI/CD / Compose / Swarm / Kubernetes container बदलता है)।
Step 2 → Docker daemon container के अंदर PID 1 को SIGTERM (या image का STOPSIGNAL) भेजता है।
Step 3 → अगर PID 1 आपका app है और handler लगा है: नए requests लेना बंद, चल रहे requests पूरे,
         DB / Redis connections बंद, फिर exit code 0 के साथ बाहर।
Step 4 → अगर PID 1 shell है जो signal को ignore करता है, तो कुछ नहीं होता (app चलता रहता है)।
Step 5 → Grace period (default 10s; `-t` या `stop_grace_period` से बदलो) के बाद Docker SIGKILL भेजता है।
         SIGKILL पकड़ा नहीं जा सकता: process तुरंत मरता है (exit code 137)।
Step 6 → Container "exited" हो जाता है। Exit 0/143 = साफ़, 137 = ज़बरदस्ती मारा गया।
```

Common signals to remember / याद रखने वाले signals:

| Signal | Number | Catchable? | Meaning |
|--------|--------|-----------|---------|
| SIGTERM | 15 | Yes | "Please terminate" - default of `docker stop` |
| SIGKILL | 9 | No | Immediate kill - `docker kill` default, or after grace period |
| SIGINT | 2 | Yes | Ctrl+C in a terminal |
| SIGHUP | 1 | Yes | Reload config (nginx `nginx -s reload` uses this) |
| SIGQUIT | 3 | Yes | Graceful stop for nginx (`STOPSIGNAL SIGQUIT` in the official nginx image) |

---

## 🟡 Real World Example
Think of a Swiggy-like order service on your VPS. At 8 PM (peak time) you deploy a new version. The old container has 40 orders being written to PostgreSQL. With a proper SIGTERM handler, the old container stops listening on the port, finishes those 40 writes, closes the DB pool, and exits in 2 seconds. Without it (`CMD npm start`), npm swallows SIGTERM, Docker waits 10 seconds, kills the container with SIGKILL, and 40 customers see "order failed" while some have already been charged.

## 🟡 Real Example Hindi mein
अपने VPS पर Swiggy जैसी order service सोचिए। रात 8 बजे (peak time) आप नया version deploy करते हो। पुराने container में 40 orders PostgreSQL में लिखे जा रहे हैं। सही SIGTERM handler हो तो पुराना container port पर सुनना बंद करता है, वे 40 writes पूरे करता है, DB pool बंद करता है और 2 सेकंड में exit हो जाता है। handler न हो (`CMD npm start`) तो npm SIGTERM निगल जाता है, Docker 10 सेकंड रुकता है, SIGKILL से मार देता है, और 40 customers को "order failed" दिखता है जबकि कुछ के पैसे कट चुके होते हैं।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile (basic): make Node.js PID 1 so it receives SIGTERM
FROM node:20-alpine
# Work inside /app
WORKDIR /app
# Copy dependency manifests first for cache
COPY package*.json ./
# Install only production dependencies, reproducibly
RUN npm ci --omit=dev
# Copy the application code
COPY . .
# EXEC form (JSON array): node itself becomes PID 1, signals reach it directly
# NEVER write: CMD npm start  or  CMD node server.js  (shell form -> /bin/sh is PID 1)
CMD ["node", "server.js"]
```

```javascript
// server.js (basic): minimal SIGTERM handler for a Node.js HTTP server
const http = require('http'); // built-in HTTP module

// Create a simple server
const server = http.createServer((req, res) => {
  res.end('hello\n'); // respond to every request
});

// Listen on 3000 (EXPOSE/publish is done by docker run -p)
server.listen(3000, () => console.log('listening on 3000'));

// Handler: runs when Docker sends SIGTERM (docker stop) or SIGINT (Ctrl+C)
function shutdown(signal) {
  console.log(`${signal} received, closing server`); // log for debugging
  // server.close stops NEW connections and waits for existing ones to finish
  server.close(() => {
    console.log('closed cleanly'); // all requests done
    process.exit(0);               // exit code 0 = success
  });
  // Safety net: if something hangs, force exit before Docker's SIGKILL (9s < 10s)
  setTimeout(() => process.exit(1), 9000).unref(); // unref: timer will not keep process alive
}
process.on('SIGTERM', () => shutdown('SIGTERM')); // docker stop
process.on('SIGINT', () => shutdown('SIGINT'));   // Ctrl+C in docker run -it
```

```bash
# Try it (commands you would run on a machine with Docker installed)
docker build -t sigdemo .                 # build the image
docker run -d --name sig -p 3000:3000 sigdemo   # run in background
time docker stop sig                      # should take ~1s, not 10s
docker logs sig                           # shows "SIGTERM received, closing server"
docker inspect sig --format '{{.State.ExitCode}}'  # 0 = clean, 137 = SIGKILLed
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml (production-style): proper signals + init + grace period
services:
  api:
    image: myorg/api:1.4.2            # pinned tag (example, update to yours)
    init: true                        # run tini as PID 1: forwards signals + reaps zombie processes
    stop_signal: SIGTERM              # signal Docker sends on stop (SIGTERM is already default)
    stop_grace_period: 30s            # wait up to 30s (default 10s) before SIGKILL; match your longest request
    restart: unless-stopped           # restart after crash or reboot, but not after manual stop
    environment:
      NODE_ENV: production            # production mode
      SHUTDOWN_TIMEOUT_MS: "25000"    # app-level force-exit timer, must be < stop_grace_period
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]  # readiness endpoint
      interval: 10s                   # check every 10s
      timeout: 3s                     # fail check after 3s
      retries: 3                      # unhealthy after 3 failures
  nginx:
    image: nginx:1.27-alpine          # official nginx image sets STOPSIGNAL SIGQUIT (graceful)
    ports:
      - "80:80"                       # public HTTP
    depends_on:
      - api                           # start api first
```

```javascript
// server.js (advanced): graceful shutdown with DB close, readiness flip, and timeout
const http = require('http');
const { Pool } = require('pg');            // PostgreSQL client (npm i pg)
const pool = new Pool({ connectionString: process.env.DATABASE_URL }); // connection pool
let shuttingDown = false;                  // flag read by /health

const server = http.createServer(async (req, res) => {
  if (req.url === '/health') {             // health endpoint used by Docker / Nginx
    res.statusCode = shuttingDown ? 503 : 200; // tell load balancer to stop sending traffic
    return res.end(shuttingDown ? 'draining' : 'ok');
  }
  const r = await pool.query('SELECT now()'); // normal work
  res.end(String(r.rows[0].now));
});
server.listen(3000);

async function shutdown(signal) {
  if (shuttingDown) return;                // ignore a second signal
  shuttingDown = true;                     // /health now returns 503
  console.log(`${signal}: draining`);
  const force = setTimeout(() => process.exit(1), Number(process.env.SHUTDOWN_TIMEOUT_MS || 25000));
  force.unref();                           // do not block exit
  server.close(async () => {               // no more new connections, existing finish
    await pool.end();                      // close DB connections cleanly
    process.exit(0);                       // success
  });
  server.closeIdleConnections?.();         // Node 18.2+: drop idle keep-alive sockets so close() returns faster
}
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
```

---

## 🟠 My Stack Integration
- **Node.js (Express/Nest):** use exec-form `CMD ["node","dist/main.js"]`. In NestJS call `app.enableShutdownHooks()` so `onModuleDestroy` / `OnApplicationShutdown` run on SIGTERM.
- **FastAPI:** run `CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]` (exec form). Uvicorn handles SIGTERM itself and runs the lifespan shutdown block. With gunicorn, use `gunicorn -k uvicorn.workers.UvicornWorker`; gunicorn does a graceful stop on SIGTERM (`--graceful-timeout`).
- **React:** the build is static files served by Nginx. The Nginx image already uses `STOPSIGNAL SIGQUIT` (finish current requests, then exit).
- **VPS:** `docker compose up -d` recreates changed containers: it sends SIGTERM and waits `stop_grace_period`. Set that value above your slowest request.
- **AWS:** ECS sends SIGTERM and waits `stopTimeout` (default 30 s) before SIGKILL; behind an ALB set deregistration delay to match.

```yaml
# docker-compose.yml fragment for your VPS stack
services:
  fastapi:
    build: ./backend                  # FastAPI Dockerfile with exec-form CMD
    init: true                        # tini as PID 1 (handles signals and zombies)
    stop_grace_period: 20s            # uvicorn finishes in-flight requests
  node-api:
    build: ./node-api                 # Node Dockerfile with exec-form CMD
    stop_grace_period: 30s            # long uploads allowed
  nginx:
    image: nginx:1.27-alpine          # SIGQUIT graceful stop built in
    stop_grace_period: 15s            # time for open connections to drain
```

**Security aspects:** PID 1 has special kernel rules (no default signal handlers), so a bare app that does not install handlers ignores SIGTERM. Use `init: true` or `tini`. Do not run the app as root: add `USER node`. A SIGKILL leaves no cleanup, so locks, temp files and half-written secrets may remain; keep secrets in memory or tmpfs, not in files you must delete on exit.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `CMD npm start` or `CMD node server.js` (shell form). `/bin/sh -c` becomes PID 1 and does not forward SIGTERM.
✅ Correct: `CMD ["node", "server.js"]` (exec form). Even better, avoid `npm start`; npm does not forward signals reliably.

❌ Mistake 2: Writing a SIGTERM handler but never calling `process.exit`, or never closing keep-alive connections, so shutdown hangs until SIGKILL.
✅ Correct: `server.close()` + close DB pool + `process.exit(0)`, plus a force-exit timer below the grace period.

❌ Mistake 3: Entrypoint shell script that starts the app as a child (`./start.sh` runs `node app.js`).
✅ Correct: end the script with `exec node app.js` so the app replaces the shell and becomes PID 1.

❌ Mistake 4: Setting `stop_grace_period` shorter than the app's own shutdown timer.
✅ Correct: app timer (25 s) < grace period (30 s), otherwise Docker kills you mid-cleanup.

---

## 🧠 Tricky Interview Question
**Q:** Your Node.js container takes exactly 10 seconds to stop on every deploy and the exit code is 137. Logs show no "shutting down" message. The Dockerfile has `CMD npm start`. What is going on and how do you fix it?

**Answer:** `CMD npm start` is shell form, so `/bin/sh -c "npm start"` is PID 1, and npm spawns node as a child. SIGTERM goes to the shell/npm, which does not forward it to node. Node never sees the signal, so Docker waits the 10 s grace period and sends SIGKILL (137 = 128 + 9). Fix: use exec form `CMD ["node","server.js"]`, add a SIGTERM handler, and optionally `init: true`.

---

## ⚫ Interview Questions + Answers

Q1: What does `docker stop` do exactly?
A1: It sends SIGTERM (or the image's `STOPSIGNAL`) to PID 1, waits the timeout (default 10 s, `-t` to change), then sends SIGKILL. `docker kill` sends SIGKILL (or any signal with `-s`) immediately.

Q2: Why is PID 1 special in a container?
A2: The kernel gives PID 1 no default signal actions: a signal with no handler is ignored. PID 1 also must reap orphaned child processes (zombies). Use an init such as tini (`docker run --init` or Compose `init: true`).

Q3: Difference between shell form and exec form of CMD/ENTRYPOINT?
A3: Shell form (`CMD node app.js`) wraps in `/bin/sh -c`, shell is PID 1 and signals are not forwarded. Exec form (`CMD ["node","app.js"]`) runs the binary directly as PID 1.

Q4: What exit codes tell you how a container stopped?
A4: 0 = clean exit, 143 = terminated by SIGTERM (128+15) without a handler, 137 = SIGKILL (128+9), often after grace timeout or OOM kill.

Q5: How do you pick a good `stop_grace_period`?
A5: Slightly above your longest normal request or job (e.g. 30 s for APIs, minutes for workers), and keep the app's own force-exit timer lower than it. Also align with load balancer deregistration delay.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production container that serves requests, consumes queues or writes data.
- Rolling deploys, autoscaling, spot instance termination, Swarm/Kubernetes pod replacement.

❌ Avoid when:
- Short-lived one-shot jobs that are safe to kill and re-run (idempotent); a handler adds little there.
- Do not replace graceful handling with a huge grace period (waiting 5 minutes hides a bug).

---

## 📊 Visual Diagram
```
 docker stop api
      |
      v
 +-----------+   SIGTERM    +--------------------+
 |  Docker   | -----------> | PID 1 in container |
 |  daemon   |              +---------+----------+
 +-----+-----+                        |
       |                    handler?  |
       |                  +-----------+-----------+
       |                  | YES                   | NO (shell form / no handler)
       |                  v                       v
       |        stop accepting new req     signal ignored
       |        finish in-flight req              |
       |        close DB, exit 0                  |
       |                  |                       |
       |   wait grace period (10s default)        |
       +------------------+-----------------------+
                          |
                still alive after timeout?
                          | yes
                          v
                      SIGKILL -> exit 137
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Signal | Message from OS to a process | OS से process को भेजा गया संदेश |
| SIGTERM | Polite stop request (15) | विनम्र बंद करने का अनुरोध |
| SIGKILL | Forced kill, cannot be caught (9) | ज़बरदस्ती मारना, पकड़ा नहीं जा सकता |
| PID 1 | First process in a container | Container का पहला process |
| Exec form | `CMD ["a","b"]` no shell | बिना shell वाला CMD रूप |
| tini / init | Tiny init process for signals + zombies | signal और zombie संभालने वाला छोटा init |
| Grace period | Wait time before SIGKILL | SIGKILL से पहले का इंतज़ार |
| STOPSIGNAL | Dockerfile instruction to change stop signal | stop signal बदलने का instruction |

---

## ⚡ 3-Line Summary
English: `docker stop` sends SIGTERM to PID 1, waits the grace period, then SIGKILL.
English: Use exec-form CMD (or `init: true`) so your app really gets the signal, and handle it by draining requests and closing connections.
English: Keep app timeout below `stop_grace_period`; exit code 137 means you were force-killed.

Hindi: `docker stop` PID 1 को SIGTERM भेजता है, grace period रुकता है, फिर SIGKILL।
Hindi: Exec-form CMD (या `init: true`) इस्तेमाल करो ताकि app को signal सच में मिले, और requests drain व connections बंद करो।
Hindi: App का timeout `stop_grace_period` से कम रखो; exit code 137 मतलब ज़बरदस्ती मारा गया।

---

## ➡️ Next Topic
**223. Container Orchestration Need** - once you can stop single containers gracefully, the next question is how to manage dozens of containers across many servers (scheduling, restarts, scaling, rolling updates), which is why orchestrators exist.
