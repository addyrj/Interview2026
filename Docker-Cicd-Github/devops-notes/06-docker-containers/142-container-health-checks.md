---

# 142. Container Health Checks
# हिंदी में: Container Health Checks (Container सच में ठीक है या नहीं)

---

## 🔵 Simple Definition (English)
A **health check** is a command Docker runs inside a container at an interval to test if the app really works (for example an HTTP call to `/health`). The container gets a status: `starting`, `healthy` or `unhealthy`. It is defined by the Dockerfile `HEALTHCHECK` instruction or the Compose `healthcheck:` key.

## 🔵 सरल परिभाषा (Hindi)
**Health check** एक command है जिसे Docker container के अंदर तय अंतराल पर चलाकर जाँचता है कि app सच में काम कर रहा है या नहीं (जैसे `/health` पर HTTP call)। Container को status मिलता है: `starting`, `healthy` या `unhealthy`। यह Dockerfile की `HEALTHCHECK` instruction या Compose की `healthcheck:` key से बनता है।

---

## 🔴 Problem it Solves
Docker only knows whether PID 1 is running. A Node.js API can be deadlocked, out of DB connections, or still booting, yet `docker ps` says "Up". Load balancers send traffic to it, and `depends_on` starts the API before Postgres is truly ready, causing connection errors. Health checks make "running" and "working" different things.

## 🔴 यह क्यों बना? (Hindi)
Docker सिर्फ़ इतना जानता है कि PID 1 चल रहा है या नहीं। Node.js API deadlock में हो सकता है, DB connections खत्म हो सकते हैं, या अभी boot हो रहा हो, फिर भी `docker ps` "Up" दिखाता है। Load balancer उसी को traffic भेजता है, और `depends_on` API को Postgres के तैयार होने से पहले शुरू कर देता है। Health checks "चल रहा है" और "काम कर रहा है" को अलग करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Container starts; status = starting (start_period grace window begins)
Step 2 → Every interval Docker runs the test command inside the container
Step 3 → Exit code 0 = success, 1 = failure (2 is reserved, do not use)
Step 4 → Command slower than timeout counts as a failure
Step 5 → retries consecutive failures -> status becomes unhealthy
Step 6 → One success -> healthy again
Step 7 → Plain Docker only LABELS it; Compose depends_on condition: service_healthy,
         Swarm, ECS and load balancers can ACT on it (restart, route, wait)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Container शुरू होता है; status = starting (start_period की grace अवधि शुरू)
Step 2 → हर interval पर Docker container के अंदर test command चलाता है
Step 3 → Exit code 0 = सफल, 1 = असफल (2 reserved है, इस्तेमाल मत करो)
Step 4 → Command timeout से धीमा हो तो failure गिना जाता है
Step 5 → लगातार retries failures -> status unhealthy
Step 6 → एक success -> फिर healthy
Step 7 → अकेला Docker सिर्फ़ LABEL लगाता है; Compose का depends_on condition: service_healthy,
         Swarm, ECS और load balancers उस पर ACTION लेते हैं (restart, route, wait)
```

---

## 🟡 Real World Example
A Swiggy-style order service ran fine until a Postgres connection pool leaked: the Node.js process stayed up but every request hung. `docker ps` showed "Up 3 days". After adding a `/health` endpoint that runs `SELECT 1` and a Docker health check, the container turned `unhealthy` within 45 seconds; ECS replaced the task automatically, and the incident that once needed a human at 3 AM healed itself. In Compose, the API now waits for `db: condition: service_healthy`, ending the boot-time "connection refused" errors.

## 🟡 Real Example Hindi mein
Swiggy जैसी order service तब तक ठीक चलती रही जब तक Postgres connection pool leak नहीं हुआ: Node.js process चालू रहा पर हर request अटकी रही। `docker ps` में "Up 3 days" दिखता रहा। `SELECT 1` चलाने वाला `/health` endpoint और Docker health check जोड़ने के बाद container 45 सेकंड में `unhealthy` हो गया; ECS ने task अपने आप बदल दिया और जिस incident के लिए रात 3 बजे इंसान चाहिए था वह खुद ठीक हो गया। Compose में API अब `db: condition: service_healthy` का इंतज़ार करती है, इसलिए boot-time "connection refused" खत्म हो गए।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile: Node.js API with a health check
FROM node:20-alpine
# small Node.js base image (example tag, update regularly)
WORKDIR /app
# all following commands run in /app
COPY package*.json ./
# copy manifests first for better layer caching
RUN npm ci --omit=dev
# install production dependencies only
COPY . .
# copy the application source
USER node
# run as the non-root user that exists in the node image
EXPOSE 3000
# document the port (does not publish it)
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1
# interval: how often; timeout: max time per probe; start-period: grace while booting;
# retries: failures before unhealthy; wget is available in alpine busybox, curl is not
CMD ["node", "server.js"]
# start the app as PID 1
```

```bash
# Watch the status change
docker ps --format 'table {{.Names}}\t{{.Status}}'
# Status shows (health: starting), (healthy) or (unhealthy)

# See the last probe results in detail
docker inspect api --format '{{json .State.Health}}'
# prints Status, FailingStreak and the Log of recent probes with output
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml: dependency ordering based on health
services:
  db:
    image: postgres:16-alpine                  # database image (example tag)
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass   # read password from a secret file
    secrets:
      - db_pass                                # mount the secret into the container
    volumes:
      - pgdata:/var/lib/postgresql/data        # persist the database
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d postgres"]  # ready to accept connections?
      interval: 10s                            # probe every 10 seconds
      timeout: 3s                              # fail if no answer in 3 seconds
      retries: 5                               # five failures -> unhealthy
      start_period: 30s                        # ignore failures while initialising

  api:
    image: ghcr.io/acme/node-api:1.8.3         # Node.js API (example tag)
    depends_on:
      db:
        condition: service_healthy             # start only when db is healthy
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000/health',r=>process.exit(r.statusCode===200?0:1)).on('error',()=>process.exit(1))"]
      interval: 15s                            # probe often enough to react quickly
      timeout: 3s                              # strict timeout
      retries: 3                               # three strikes
      start_period: 20s                        # Node boot time
    restart: unless-stopped                    # restart on crash (not on unhealthy by itself)

  web:
    image: nginx:1.27-alpine                   # reverse proxy for React build
    depends_on:
      api:
        condition: service_healthy             # proxy starts after API is up
    ports:
      - "80:80"                                # public HTTP
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost/healthz"]   # Nginx location returning 200
      interval: 30s                            # relaxed interval for a static proxy
      timeout: 3s                              # fast answer expected
      retries: 3                               # three failures -> unhealthy

secrets:
  db_pass:
    file: ./secrets/db_pass.txt                # local secret file, never commit it

volumes:
  pgdata: {}                                   # named volume for Postgres data
```

```python
# FastAPI health endpoint with a real dependency check
from fastapi import FastAPI, Response            # web framework and response object
import asyncpg                                   # async Postgres driver
import os                                        # read environment variables

app = FastAPI()                                  # create the application

@app.get("/health")                              # route used by the Docker health check
async def health(response: Response):
    try:
        conn = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=2)  # short DB timeout
        await conn.execute("SELECT 1")           # prove the DB answers
        await conn.close()                       # release the connection
        return {"status": "ok"}                  # HTTP 200 means healthy
    except Exception:
        response.status_code = 503               # unhealthy status code
        return {"status": "db_unreachable"}      # no internal details leaked
```

YAML and the Python snippet were parsed or compiled locally and the Dockerfile instructions sanity-checked; nothing was built or run. Plain Docker does not restart `unhealthy` containers by itself; Swarm, ECS, Kubernetes (probes) or an autoheal tool do.

---

## 🟠 My Stack Integration
Node.js: add `/health` (liveness: process alive) and `/ready` (readiness: DB reachable). FastAPI: the endpoint above. React: Nginx serves a static `/healthz`. VPS with Compose: use `service_healthy` ordering. AWS: set the ALB target group health path to the same `/health`, and ECS task definition `healthCheck` to the container command.

```nginx
# nginx default.conf snippet for the web container
location = /healthz {
    access_log off;                       # keep health probes out of the access log
    default_type text/plain;              # plain text response
    return 200 "ok";                      # cheap success answer without touching upstream
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Health check uses `curl` in an Alpine/distroless image that has no curl, so it is always unhealthy.
✅ Correct: Use `wget` (busybox), a `node -e` one-liner, or install curl deliberately; for distroless use a tiny compiled healthcheck binary.

❌ Mistake 2: No `start_period`; a slow-booting app is marked unhealthy before it starts.
✅ Correct: Set `start_period` longer than your normal boot time.

❌ Mistake 3: Health endpoint always returns 200 even when the DB is down.
✅ Correct: Check real dependencies in readiness, but keep liveness cheap to avoid restart storms when only the DB is slow.

❌ Mistake 4: Believing `restart: always` restarts unhealthy containers.
✅ Correct: Restart policies react to exit, not to health status. Use orchestrator checks or an autoheal sidecar.

---

## 🧠 Tricky Interview Question
`docker compose up` with `depends_on: [db]` still gives "ECONNREFUSED" from the API on boot. Why, and how do you fix it without sleep loops?

Answer: Short-form `depends_on` only waits for the db container to be started, not ready. Postgres needs seconds to initialise. Add a `healthcheck` to db with `pg_isready` and use `depends_on: db: condition: service_healthy`. Also make the app retry its DB connection with backoff, because the DB can restart later anyway; ordering alone is not resilience.

---

## ⚫ Interview Questions + Answers

Q1: What are the three health statuses?
A1: `starting` (within start_period or before first success), `healthy`, `unhealthy`.

Q2: What exit codes does a health command use?
A2: 0 success, 1 failure. 2 is reserved. Any other code is treated as failure.

Q3: Liveness vs readiness?
A3: Liveness asks "should I restart this?" (process stuck). Readiness asks "can it take traffic now?" (dependencies ready). Docker has one check; Kubernetes has separate probes.

Q4: Where do you disable a Dockerfile health check from Compose?
A4: `healthcheck: disable: true` in the service.

Q5: Does a health check affect performance?
A5: Slightly; each probe spawns a process. Keep it cheap, with sensible intervals, and avoid expensive queries.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Services depend on each other (DB, cache, API)
- An orchestrator or load balancer should route or replace based on health
- You want `docker ps` to show real state

❌ Avoid when:
- The check is heavier than the app work itself
- The check hits a flaky external API (cascading failures)
- You have no consumer of the status (it only adds noise)

---

## 📊 Visual Diagram
```
 start ──► [starting] ──(start_period grace, failures ignored)──┐
                                                                ▼
                       probe every interval ──► exit 0 ──► [healthy]
                              │                                  │
                              │ exit 1 / timeout                 │
                              ▼                                  │
                     FailingStreak++ ── < retries ───────────────┘
                              │ >= retries
                              ▼
                        [unhealthy] ──► orchestrator / LB / autoheal acts
                              ▲                │ next success
                              └────────────────┘ -> healthy again
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HEALTHCHECK | Dockerfile instruction defining the probe | Probe तय करने वाली instruction |
| interval | Time between probes | Probes के बीच का समय |
| timeout | Max time for one probe | एक probe का अधिकतम समय |
| start_period | Grace time at boot | Boot के समय की छूट |
| retries | Failures before unhealthy | Unhealthy होने से पहले failures |
| service_healthy | Compose condition waiting for healthy | Healthy होने तक इंतज़ार |

---

## ⚡ 3-Line Summary
English: A health check tests if the app truly works, giving `healthy` or `unhealthy`, not just "running". Use it with `depends_on: service_healthy` and orchestrators that can react. Keep probes cheap and provide a start period.
Hindi: Health check जाँचता है कि app सच में काम कर रहा है, और `healthy` या `unhealthy` देता है, सिर्फ़ "running" नहीं। इसे `depends_on: service_healthy` और ऐसे orchestrators के साथ इस्तेमाल करो जो react कर सकें। Probes सस्ते रखो और start period दो।

---

## ➡️ Next Topic
**143. Exec into Container**: when a container is unhealthy, the next step is getting a shell inside it with `docker exec`.

---
