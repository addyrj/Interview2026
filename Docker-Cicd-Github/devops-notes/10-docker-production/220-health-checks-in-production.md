# 220. Health Checks in Production
# हिंदी में: Production में Health Checks

---

## 🔵 Simple Definition (English)
A **health check** is a command Docker runs inside a container at intervals to find out if the app is really working, not just if the process exists. The container's status becomes `starting`, `healthy` or `unhealthy`. In production you design two kinds of endpoints: **liveness** ("is the process alive?") and **readiness** ("can it serve traffic now?").

## 🔵 सरल परिभाषा (Hindi)
**Health check** एक command है जो Docker container के अंदर समय-समय पर चलाता है ताकि पता चले कि app सच में काम कर रहा है, सिर्फ process मौजूद नहीं। Container का status `starting`, `healthy` या `unhealthy` बनता है। Production में दो तरह के endpoints बनाते हैं: **liveness** ("process ज़िंदा है?") और **readiness** ("अभी traffic ले सकता है?")।

---

## 🔴 Problem it Solves
A container can be "Up" while the app inside is deadlocked, out of DB connections, or still warming up. Docker only sees that PID 1 is running. Result: Nginx sends users to a dead backend and they see 502/504, deploys declare success while the new version crashes seconds later, and Compose `depends_on` starts the API before PostgreSQL can accept connections. Health checks make the real state visible and let tools react.

## 🔴 यह क्यों बना? (Hindi)
Container "Up" दिखता है जबकि अंदर app deadlock में है, DB connections खत्म हैं, या अभी warm-up में है। Docker को सिर्फ इतना दिखता है कि PID 1 चल रहा है। नतीजा: Nginx users को मरे हुए backend पर भेजता है और 502/504 आता है, deploy "success" बोलता है जबकि नया version कुछ सेकंड में crash कर जाता है, और Compose `depends_on` API को PostgreSQL तैयार होने से पहले start कर देता है। Health checks असली स्थिति दिखाते हैं और tools को react करने देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Container starts. Status = "starting". Docker waits --start-period (failures ignored).
Step 2 → Every --interval, Docker runs the check command inside the container.
Step 3 → Command exit code 0 = success, 1 = failure (anything else is reserved/unwanted).
Step 4 → Each run has a --timeout; exceeding it counts as a failure.
Step 5 → After --retries consecutive failures: status = "unhealthy". One success: "healthy".
Step 6 → Who uses it?  `depends_on: condition: service_healthy`, Swarm (replaces task),
         monitoring tools, deploy scripts (wait until healthy). Plain Docker does NOT restart
         an unhealthy container by itself, and Compose does not either.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Container start होता है। Status = "starting"। Docker --start-period तक failures ignore करता है।
Step 2 → हर --interval पर Docker container के अंदर check command चलाता है।
Step 3 → Exit code 0 = success, 1 = failure (बाकी values reserved/अनचाही)।
Step 4 → हर run का --timeout होता है; पार करने पर failure गिना जाता है।
Step 5 → लगातार --retries failures के बाद status = "unhealthy"। एक success से "healthy"।
Step 6 → कौन use करता है?  `depends_on: condition: service_healthy`, Swarm (task बदलता है),
         monitoring tools, deploy scripts (healthy होने तक रुको)। Plain Docker/Compose
         unhealthy container को अपने-आप restart नहीं करते।
```

Liveness vs readiness / दोनों का फर्क:

| Type | Question | Checks | Failure means |
|------|----------|--------|---------------|
| Liveness `/livez` | Is the process OK? | No dependencies, just returns 200 | Restart it |
| Readiness `/readyz` | Can it serve now? | DB, Redis ping | Remove from load balancer, do not restart |

---

## 🟡 Real World Example
Swiggy-style order API: after a deploy the Node.js app starts in 2 seconds but needs 15 seconds to load menus into cache and open DB pools. Without a readiness check, Nginx sends dinner-rush traffic to the half-ready container and 5% of orders fail. With `/readyz` returning 503 until cache is warm and Compose waiting on `service_healthy`, the traffic only arrives when the app is ready. Later, when the DB connection pool deadlocks, the check turns unhealthy, the monitor pages the on-call, and an auto-heal script restarts it.

## 🟡 Real Example Hindi mein
Swiggy जैसी order API: deploy के बाद Node.js app 2 सेकंड में start होता है पर menus cache में load करने और DB pool खोलने में 15 सेकंड लगते हैं। Readiness check के बिना Nginx dinner-rush का traffic आधे तैयार container पर भेजता है और 5% orders fail होते हैं। `/readyz` जब तक cache गरम न हो 503 देता है और Compose `service_healthy` का इंतज़ार करता है, तो traffic तभी आता है जब app तैयार हो। बाद में जब DB pool deadlock होता है, check unhealthy हो जाता है, monitor on-call को page करता है और auto-heal script restart करती है।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile - Node.js app with a simple HEALTHCHECK
FROM node:20-alpine                         # small base image (example tag)
WORKDIR /app                                # app directory
COPY package*.json ./                       # dependency manifests first (cache)
RUN npm ci --omit=dev                       # install production deps only
COPY . .                                    # app source
USER node                                   # non-root user
EXPOSE 3000                                 # documentation of the port
# Alpine has busybox wget, no curl needed: -q quiet, -O- print to stdout, exit code 1 on HTTP error
HEALTHCHECK --interval=15s --timeout=3s --start-period=20s --retries=3 \
  CMD wget -q -O- http://127.0.0.1:3000/livez || exit 1
CMD ["node", "server.js"]                   # exec form so SIGTERM reaches Node
```

```bash
# See the health status and recent check output
docker ps --format 'table {{.Names}}\t{{.Status}}'                 # shows (healthy) / (unhealthy)
docker inspect --format '{{json .State.Health}}' api | head -c 600 # last 5 check results with output
```

## 💻 Code / Config Example — Advanced

```javascript
// server.js - separate liveness and readiness endpoints (Express)
const express = require('express');                       // web framework
const { Pool } = require('pg');                           // PostgreSQL client
const app = express();                                    // app instance
const pool = new Pool({ connectionString: process.env.DATABASE_URL }); // DB pool
let shuttingDown = false;                                 // flips on SIGTERM

app.get('/livez', (req, res) => res.status(200).send('ok')); // liveness: no dependencies, cheap

app.get('/readyz', async (req, res) => {                  // readiness: checks dependencies
  if (shuttingDown) return res.status(503).send('shutting down'); // drain traffic during shutdown
  try {
    await pool.query('SELECT 1');                         // DB reachable?
    res.status(200).send('ready');                        // yes
  } catch (e) {
    res.status(503).send('db not ready');                 // no -> not ready
  }
});

const server = app.listen(3000);                          // start server
process.on('SIGTERM', () => {                             // graceful shutdown hook
  shuttingDown = true;                                    // readiness now fails
  server.close(() => pool.end().then(() => process.exit(0))); // finish requests, close DB, exit
});
```

```yaml
# docker-compose.prod.yml - health checks + dependency ordering
services:
  db:
    image: postgres:16-alpine                  # database
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass   # secret from file, not env text
    secrets: [db_pass]                         # mount the secret
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d postgres"]  # official readiness tool
      interval: 10s                            # run every 10 seconds
      timeout: 3s                              # fail if no answer in 3s
      retries: 5                               # 5 failures = unhealthy
      start_period: 20s                        # grace time for first boot
  api:
    image: myorg/node-api:1.4.2                # Node.js API image with HEALTHCHECK baked in
    depends_on:
      db:
        condition: service_healthy             # wait until DB reports healthy
    healthcheck:
      test: ["CMD", "wget", "-q", "-O-", "http://127.0.0.1:3000/readyz"]  # readiness probe
      interval: 10s                            # every 10s
      timeout: 3s                              # 3s max
      retries: 3                               # 3 strikes
      start_period: 30s                        # app warm-up time
    restart: unless-stopped                    # restarts on crash (not on unhealthy)
  nginx:
    image: nginx:1.27-alpine                   # reverse proxy
    depends_on:
      api:
        condition: service_healthy             # start proxy only after API is healthy
    ports: ["80:80"]                           # public port
secrets:
  db_pass:
    file: ./secrets/db_pass.txt                # local secret file (never commit)
```

Checked: YAML parses; JS passes `node --check`. Not run against a live Docker daemon. / YAML और JS syntax check हुआ; Docker daemon पर नहीं चलाया।

---

## 🟠 My Stack Integration
- **Node.js**: `/livez` and `/readyz` as above. **FastAPI**: add `@app.get("/readyz")` that pings DB; slim Python images have no curl, so use `python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/readyz', timeout=2)"`.
- **Nginx**: check with `wget -q -O- http://127.0.0.1/nginx-health` after adding a `location = /nginx-health { access_log off; return 200; }`.
- **React**: static files; health check is just Nginx responding.
- **AWS**: ALB target group health check (path `/readyz`, interval 15s, healthy threshold 2) is the real production gate; ECS uses the container `healthCheck` too. Docker's own check is for Compose/Swarm and local dev.
- **VPS auto-heal**: since Docker will not restart unhealthy containers, use a tiny watcher (e.g. `willfarrell/autoheal` image, mounts docker.sock so apply security care) or systemd/monitoring.

```bash
# Deploy script: wait until the new container is healthy or fail the pipeline
docker compose up -d api                                     # start the new version
for i in $(seq 1 30); do                                      # up to 30 tries
  s=$(docker inspect -f '{{.State.Health.Status}}' "$(docker compose ps -q api)")  # read status
  [ "$s" = "healthy" ] && echo "healthy" && exit 0            # success
  sleep 2                                                     # wait 2 seconds
done
echo "unhealthy - rolling back"; exit 1                       # fail the deploy
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Health check that only returns 200 without testing anything while the app is deadlocked.
✅ Correct: Use readiness that does a cheap real check (`SELECT 1`), with a short timeout.

❌ Mistake 2: Making liveness depend on the database. A DB outage makes every API container "unhealthy" and mass restarts follow.
✅ Correct: Liveness has no external dependencies; DB goes into readiness.

❌ Mistake 3: Using `curl` in the image that does not have it (alpine, slim), so the check always fails.
✅ Correct: Use `wget` (busybox), or a Node/Python one-liner, or install curl on purpose.

❌ Mistake 4: No `start_period`, so slow boots are marked unhealthy.
✅ Correct: Set `start_period` to the real warm-up time.

❌ Mistake 5: Expecting Docker to restart unhealthy containers.
✅ Correct: Only Swarm/Kubernetes/ECS replace them; on plain Docker add an autoheal or monitoring step.

---

## 🧠 Tricky Interview Question
**Q:** Your database goes down for 30 seconds. All API containers have health checks hitting `/health` which runs `SELECT 1`, and your orchestrator restarts unhealthy containers. What happens, and how do you fix the design?

**Answer:** Every API container becomes unhealthy at the same moment and the orchestrator restarts all of them (restart storm). They come back, hit the still-recovering DB with many new connections (thundering herd), and the outage gets longer. The app was fine; it only needed to wait. Fix: liveness must not check dependencies; readiness may check DB, but failing readiness only removes the pod/task from the load balancer and does not restart it. Add retries/backoff for DB reconnection inside the app.

---

## ⚫ Interview Questions + Answers

Q1: HEALTHCHECK exit codes?
A1: 0 healthy, 1 unhealthy, 2 reserved (do not use). Any other code is treated as unhealthy-ish but should be avoided.

Q2: Healthcheck vs depends_on?
A2: `depends_on` alone only orders start. With `condition: service_healthy` it waits until the dependency's health check passes.

Q3: Liveness vs readiness vs startup probes?
A3: Liveness: restart if dead. Readiness: send traffic only if ready. Startup (Kubernetes): give slow apps time before liveness begins. Docker has one HEALTHCHECK plus `start_period`.

Q4: How to disable an inherited HEALTHCHECK?
A4: `HEALTHCHECK NONE` in the Dockerfile, or `healthcheck: disable: true` in Compose.

Q5: Does the health check run on the host?
A5: No, inside the container, so the tool (wget/curl) must exist in the image and the app must listen on 127.0.0.1 or 0.0.0.0.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every long-running production service
- Dependencies with startup order (API after DB)
- Behind a load balancer or reverse proxy
- Zero-downtime deploys (wait for healthy before switching)

❌ Avoid when:
- The check is expensive (heavy queries every 5s add load)
- One-off/batch containers that exit
- Check calls external third-party APIs (their outage kills your service)

---

## 📊 Visual Diagram
```
 start --> [starting] --(start_period)--> run check every 10s
                                   |
                  exit 0 ----------+---------- exit 1 / timeout
                    |                              |
                 healthy <--- 1 success     failures >= retries
                    |                              |
                    v                              v
        Nginx/ALB sends traffic          [unhealthy]
        depends_on proceeds                 |
                                  Swarm/ECS replace task
                                  Plain Docker: alert / autoheal
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HEALTHCHECK | Command that tests the app | App test करने वाला command |
| Liveness | Is it alive | ज़िंदा है या नहीं |
| Readiness | Is it ready for traffic | Traffic के लिए तैयार |
| start_period | Warm-up grace time | Warm-up की छूट |
| Restart storm | All instances restart together | सब एक साथ restart |
| Autoheal | Tool that restarts unhealthy containers | Unhealthy को restart करने वाला tool |

---

## ⚡ 3-Line Summary
English: Health checks tell Docker whether the app really works; use liveness and readiness separately.
Use `service_healthy` for startup order, and `start_period` for slow boots.
Plain Docker does not auto-restart unhealthy containers, so add monitoring or an orchestrator.

Hindi: Health checks बताते हैं कि app सच में काम कर रहा है; liveness और readiness अलग रखो।
Startup order के लिए `service_healthy` और slow boot के लिए `start_period` use करो।
Plain Docker unhealthy को restart नहीं करता, इसलिए monitoring या orchestrator जोड़ो।

---

## ➡️ Next Topic
**221. Graceful Shutdown in Docker** - readiness fails first, then the app must finish in-flight requests and exit cleanly when it receives SIGTERM.
