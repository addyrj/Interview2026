# 085. HEALTHCHECK Instruction
# हिंदी में: HEALTHCHECK इंस्ट्रक्शन (Container Health जाँच)

---

## 🔵 Simple Definition (English)
`HEALTHCHECK` tells Docker how to test whether a running container is actually working. Docker runs your command repeatedly; exit code `0` means healthy and `1` means unhealthy. The container shows `healthy`, `unhealthy` or `starting` in `docker ps`.

## 🔵 सरल परिभाषा (Hindi)
`HEALTHCHECK` Docker को बताता है कि चलते container की सही काम करने की जाँच कैसे करे। Docker आपका command बार-बार चलाता है; exit code `0` का मतलब healthy और `1` का मतलब unhealthy। `docker ps` में container `healthy`, `unhealthy` या `starting` दिखता है।

---

## 🔴 Problem it Solves
A container can be "Up" while the app inside is deadlocked, out of memory in a loop, or has lost its DB connection. Docker only knows the process is alive (PID exists), not that it serves requests. Without a healthcheck, Compose starts the frontend before the API is ready, load balancers send traffic to a broken instance, and you learn about it from users. HEALTHCHECK adds an application-level "is it really working?" signal.

## 🔴 यह क्यों बना? (Hindi)
Container "Up" दिख सकता है जबकि अंदर की app deadlock में है, memory की वजह से loop में है, या DB connection खो चुकी है। Docker सिर्फ यह जानता है कि process ज़िंदा है (PID मौजूद है), यह नहीं कि requests serve हो रही हैं। Healthcheck के बिना Compose API तैयार होने से पहले frontend शुरू कर देता है, load balancer टूटे instance पर traffic भेजता है, और आपको users से पता चलता है। HEALTHCHECK application-level संकेत जोड़ता है: "क्या सच में काम कर रहा है?"

---

## 🟢 How it Works — Step by Step

```
Step 1 → Container starts; status = "starting" (start-period: failures are ignored)
Step 2 → Every --interval (default 30s) Docker runs CMD inside the container
Step 3 → CMD must finish within --timeout (default 30s) else counts as failure
Step 4 → Exit 0 = success (healthy); exit 1 = failure; (exit 2 is reserved)
Step 5 → --retries (default 3) consecutive failures -> status "unhealthy"
Step 6 → One success -> back to "healthy"
Step 7 → Plain Docker does NOT restart unhealthy containers; Compose
         `depends_on: condition: service_healthy`, Swarm, and your monitoring DO act on it
```

Options: `--interval=30s --timeout=30s --start-period=0s --retries=3`. (Newer Docker, 25.0 and later, also has `--start-interval`; version-dependent.) `HEALTHCHECK NONE` disables an inherited check.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Container शुरू होता है; status = "starting" (start-period में failures ignore होते हैं)
Step 2 → हर --interval (default 30s) पर Docker container के अंदर CMD चलाता है
Step 3 → CMD --timeout (default 30s) में खत्म होना चाहिए वरना failure गिना जाता है
Step 4 → Exit 0 = सफल (healthy); exit 1 = failure; (exit 2 reserved है)
Step 5 → लगातार --retries (default 3) failures -> status "unhealthy"
Step 6 → एक सफलता -> वापस "healthy"
Step 7 → साधारण Docker unhealthy container को restart नहीं करता; Compose का
         `depends_on: condition: service_healthy`, Swarm और आपकी monitoring इस पर काम करते हैं
```

---

## 🟡 Real World Example
On your VPS, Compose runs Nginx, a FastAPI API and PostgreSQL. After a deploy, the API needs 20 seconds to run migrations and open the DB pool. Without a healthcheck, Nginx starts immediately and returns 502 for 20 seconds. With a healthcheck on `/health` and `depends_on: condition: service_healthy`, Nginx waits until the API is healthy. In addition, an uptime script runs `docker ps --filter health=unhealthy` and alerts Slack when a container goes unhealthy.

## 🟡 Real Example Hindi mein
आपके VPS पर Compose Nginx, FastAPI API और PostgreSQL चलाता है। Deploy के बाद API को migrations चलाने और DB pool खोलने में 20 सेकंड लगते हैं। Healthcheck के बिना Nginx तुरंत शुरू होकर 20 सेकंड 502 देता है। `/health` पर healthcheck और `depends_on: condition: service_healthy` के साथ Nginx तब तक रुकता है जब तक API healthy न हो। साथ ही एक uptime script `docker ps --filter health=unhealthy` चलाकर container unhealthy होने पर Slack alert भेजती है।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Basic HEALTHCHECK (Node.js, no curl needed: uses Node 18+ built-in fetch)
# Base image (example tag, node:20 has global fetch)
FROM node:20-alpine
# Working directory
WORKDIR /app
# Copy source
COPY . .
# Install production dependencies
RUN npm ci --omit=dev
# Document the port
EXPOSE 3000
# Check every 30s, allow 3s per check, ignore failures for the first 15s, 3 failures = unhealthy
# fetch() rejects on connection error; we exit 1 if status is not OK
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
# Run unprivileged
USER node
# Start app
CMD ["node", "server.js"]
```

```bash
# Run and watch the status change: starting -> healthy
docker run -d --name api -p 3000:3000 myapi
docker ps --format 'table {{.Names}}\t{{.Status}}'
# See the last check results and output
docker inspect --format '{{json .State.Health}}' api
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Advanced: FastAPI image with a dependency-free healthcheck script, plus Compose gating
# Python slim base (example tag; slim has no curl or wget)
FROM python:3.12-slim
# Python runtime flags
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
# Working directory
WORKDIR /app
# Dependencies
COPY requirements.txt .
# Install without cache
RUN pip install --no-cache-dir -r requirements.txt
# App code
COPY app ./app
# Small healthcheck script using only the standard library
COPY healthcheck.py /usr/local/bin/healthcheck.py
# Non-root user
USER 10001
# Document the port
EXPOSE 8000
# Exec form: no shell needed. start-period covers migrations/startup time
HEALTHCHECK --interval=15s --timeout=3s --start-period=30s --retries=3 \
  CMD ["python", "/usr/local/bin/healthcheck.py"]
# Start the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```python
# healthcheck.py: exit 0 if /health returns 200, else exit 1
import sys
import urllib.request

try:
    # Short timeout so a hung app is detected quickly
    with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as resp:
        # Healthy only for HTTP 200
        sys.exit(0 if resp.status == 200 else 1)
except Exception:
    # Connection refused, timeout, 5xx (raises HTTPError) -> unhealthy
    sys.exit(1)
```

```yaml
# docker-compose.yml: wait for health before starting dependants (Compose Specification)
services:
  # PostgreSQL with its own healthcheck
  db:
    # Official image (example tag)
    image: postgres:16-alpine
    # Password from server .env
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    # pg_isready is shipped inside the postgres image
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 3s
      retries: 5
    # Persist data
    volumes:
      - pg_data:/var/lib/postgresql/data
  # FastAPI backend
  api:
    # Build with the Dockerfile above (HEALTHCHECK is inherited from it)
    build: ./backend
    # Start only after the DB reports healthy
    depends_on:
      db:
        condition: service_healthy
    # Restart if the process crashes (does not react to "unhealthy" by itself)
    restart: unless-stopped
  # Nginx reverse proxy
  nginx:
    # Official image (example tag)
    image: nginx:1.27-alpine
    # Public ports
    ports:
      - "80:80"
    # Start only when the API is healthy
    depends_on:
      api:
        condition: service_healthy
# Named volume
volumes:
  pg_data:
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: add a cheap `/health` route (no heavy DB queries; optionally a `/ready` that checks the DB).
- **Nginx**: `wget -qO- http://127.0.0.1/ >/dev/null || exit 1` works in the alpine image (busybox wget).
- **React**: static build served by Nginx; check `/` returns 200.
- **VPS**: wire `docker ps --filter health=unhealthy` into cron/Uptime Kuma. To self-heal on a single host use `restart` scripts or autoheal-style sidecars (third-party).
- **AWS**: ALB target group health checks hit `/health` on the instance/task and remove bad targets. ECS task definitions have their own `healthCheck` (the Dockerfile HEALTHCHECK is not used by ECS), and Kubernetes ignores HEALTHCHECK in favour of liveness/readiness probes. Remember: define the check in the orchestrator you actually use.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `CMD curl -f http://localhost/health` in `alpine` or `slim` images where curl does not exist, so it is always unhealthy.
✅ Correct: Use `wget` (busybox), Node/Python one-liners, or install curl deliberately.

❌ Mistake 2: No `--start-period`, so a slow-starting app is marked unhealthy during boot.
✅ Correct: Set `--start-period` bigger than the normal startup time.

❌ Mistake 3: A health endpoint that runs heavy queries or hits third parties, causing load and flapping.
✅ Correct: Keep it light; separate liveness (process OK) from readiness (dependencies OK).

❌ Mistake 4: Assuming Docker restarts unhealthy containers.
✅ Correct: It only labels them (outside Swarm). Add monitoring/automation or use an orchestrator.

❌ Mistake 5: Using `localhost` that resolves to IPv6 `::1` while the app listens on IPv4 only.
✅ Correct: Use `127.0.0.1` explicitly.

---

## 🧠 Tricky Interview Question
Your container shows `unhealthy`, yet users can still use the site. Another time, it shows `healthy` while the site returns 500s. How can both happen?

Answer: HEALTHCHECK only reports what the command measures. `unhealthy` with working users means the check itself is wrong (missing curl, wrong port/path, timeout too short, hitting IPv6 localhost). `healthy` with 500s means the check is too shallow (for example it only tests that the port is open or `/health` returns 200 without checking the DB). Design checks to represent real readiness, and verify them with `docker inspect --format '{{json .State.Health}}'`, which stores the last command outputs.

---

## ⚫ Interview Questions + Answers

Q1: What exit codes does HEALTHCHECK use?
A1: `0` healthy, `1` unhealthy. `2` is reserved and should not be used.

Q2: Does Docker restart an unhealthy container?
A2: Not in plain `docker run`/Compose. Swarm does (reschedules tasks). Otherwise you need monitoring or a tool to act on the status.

Q3: Liveness vs readiness?
A3: Docker has one check. Kubernetes separates liveness (restart me) from readiness (do not send traffic yet). Kubernetes ignores Dockerfile HEALTHCHECK.

Q4: How does `depends_on` use health?
A4: `condition: service_healthy` delays the dependant service until the target reports healthy.

Q5: How to disable an inherited healthcheck?
A5: `HEALTHCHECK NONE` in the Dockerfile, or `healthcheck: disable: true` in Compose.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Services have dependencies (API waits for DB; Nginx waits for API).
- Single-host VPS deployments where you want visibility into real health.
- Zero-downtime deploy scripts that wait for `healthy` before switching traffic.

❌ Avoid when:
- Orchestrator already defines probes (Kubernetes, ECS) and you would duplicate them (keep one source of truth).
- The check would be expensive or flap.

---

## 📊 Visual Diagram

```
 container start
      |
      v
  [starting] --(start-period: failures ignored)-->
      |
  every 30s: run CMD  ---- exit 0 ----> [healthy]
      |                                    ^
      | exit 1 (x retries=3)               | one success
      v                                    |
  [unhealthy] -------------------------- --+
      |
      +--> Compose depends_on waits / monitoring alerts / Swarm reschedules
           (plain Docker: no auto restart)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HEALTHCHECK | Command that tests app health | app की सेहत जाँचने वाला command |
| start-period | Grace time at startup | शुरुआत में दी गई छूट |
| interval | Time between checks | दो जाँचों के बीच का समय |
| retries | Failures before unhealthy | unhealthy होने से पहले failures |
| Liveness | Is the process alive? | process ज़िंदा है? |
| Readiness | Can it serve traffic? | traffic लेने को तैयार? |

---

## ⚡ 3-Line Summary
English: HEALTHCHECK runs a command in the container to mark it healthy or unhealthy. Use tools that exist in the image, set a start-period, and keep checks light. Docker only labels the status; Compose, Swarm and monitoring act on it.
Hindi: HEALTHCHECK container में command चलाकर उसे healthy या unhealthy mark करता है। Image में मौजूद tools use करो, start-period दो और check हल्का रखो। Docker सिर्फ status लगाता है; Compose, Swarm और monitoring उस पर काम करते हैं।

---

## ➡️ Next Topic
**086. ONBUILD Instruction**: healthchecks run at runtime; ONBUILD is the odd instruction that runs later, when someone builds a child image from yours.
