# 192. healthcheck in Compose
# हिंदी में: Compose में healthcheck

---

## 🔵 Simple Definition (English)
A **healthcheck** is a command Docker runs inside a container at intervals to test whether the application is really working (not just running). Result: `starting`, `healthy` or `unhealthy`. In Compose it is configured with `test`, `interval`, `timeout`, `retries`, `start_period` (and `start_interval` in recent versions).

## 🔵 सरल परिभाषा (Hindi)
**Healthcheck** एक command है जिसे Docker container के अंदर समय-समय पर चलाकर जाँचता है कि application सच में काम कर रहा है (सिर्फ चल नहीं रहा)। Result: `starting`, `healthy` या `unhealthy`। Compose में यह `test`, `interval`, `timeout`, `retries`, `start_period` (और नए versions में `start_interval`) से set होता है।

---

## 🔴 Problem it Solves
A container can be "Up" while the app inside is deadlocked, out of DB connections, or still booting. Docker only knows the main process exists. Without healthchecks, `depends_on` cannot wait for readiness, Nginx proxies to a dead API (502), and monitoring shows green while users see errors.

## 🔴 यह क्यों बना? (Hindi)
Container "Up" हो सकता है जबकि अंदर app deadlock में है, DB connections खत्म हो गए हैं, या अभी boot हो रहा है। Docker सिर्फ इतना जानता है कि main process मौजूद है। Healthcheck के बिना `depends_on` readiness का इंतज़ार नहीं कर सकता, Nginx मरे हुए API को proxy करता है (502), और monitoring हरा दिखाती है जबकि users को errors दिखते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Container starts; status = "starting" (health: starting)
Step 2 → During start_period, failed checks do not count against retries
Step 3 → Every `interval`, Docker runs `test` inside the container (exec)
Step 4 → Exit code 0 = healthy; exit code 1 = unhealthy; 2 is reserved
Step 5 → A check taking longer than `timeout` counts as a failure
Step 6 → After `retries` consecutive failures -> status becomes "unhealthy"
Step 7 → Compose depends_on (service_healthy), docker ps and monitoring read this status
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Container चालू होता है; status = "starting"
Step 2 → start_period में fail हुई checks retries में नहीं गिनी जातीं
Step 3 → हर `interval` पर Docker container के अंदर `test` चलाता है (exec)
Step 4 → Exit code 0 = healthy; exit code 1 = unhealthy; 2 reserved है
Step 5 → `timeout` से ज़्यादा समय लेने वाली check fail गिनी जाती है
Step 6 → लगातार `retries` failures के बाद status "unhealthy" हो जाता है
Step 7 → Compose depends_on (service_healthy), docker ps और monitoring यही status पढ़ते हैं
```

---

## 🟡 Real World Example
A Swiggy-style order API connects to Postgres and Redis. One night Redis ran out of memory and the API's event loop blocked: the process was alive, port open, but every request hung. A TCP-only check said healthy. After the incident the team added `/health` that pings DB and Redis with a 1-second budget. Now the container becomes `unhealthy` in 30 seconds, an alert fires, and `autoheal` restarts it.

## 🟡 Real Example Hindi mein
Swiggy जैसा order API Postgres और Redis से जुड़ा है। एक रात Redis का memory खत्म हुआ और API का event loop block हो गया: process ज़िंदा, port खुला, पर हर request अटकी। सिर्फ TCP check "healthy" कहता रहा। घटना के बाद टीम ने `/health` जोड़ा जो 1 सेकंड के budget में DB और Redis को ping करता है। अब container 30 सेकंड में `unhealthy` हो जाता है, alert आता है, और `autoheal` उसे restart करता है।

---

## 💻 Code / Config Example — Basic
```yaml
# compose.yaml - minimal healthcheck for a Node.js API
services:
  api:
    image: myorg/api:1.4.2                 # example image that serves GET /health
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]  # exit 0 if HTTP 200
      interval: 30s                        # run the check every 30 seconds
      timeout: 5s                          # fail the check if it takes over 5 seconds
      retries: 3                           # mark unhealthy after 3 failures in a row
```

```bash
docker compose ps                                        # STATUS column shows (healthy)/(unhealthy)
docker inspect --format '{{json .State.Health}}' $(docker compose ps -q api)   # full history of probes
docker ps --filter health=unhealthy                      # list only unhealthy containers
```

## 💻 Code / Config Example — Advanced
```yaml
# compose.yaml - healthchecks for the whole stack
services:
  db:
    image: postgres:16-alpine                          # example tag
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]  # CMD-SHELL runs through /bin/sh
      interval: 5s                                     # frequent: cheap check
      timeout: 3s
      retries: 10
      start_period: 15s                                # allow slow first-time initialisation

  mongo:
    image: mongo:7
    healthcheck:
      test: ["CMD", "mongosh", "--quiet", "--eval", "db.adminCommand('ping').ok"]  # prints 1 when ok
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]               # replies PONG
      interval: 5s
      timeout: 3s
      retries: 10

  api:
    image: myorg/api:1.4.2
    depends_on:
      db:
        condition: service_healthy                     # wait for db health
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://127.0.0.1:3000/health | grep -q ok"]  # body must contain ok
      interval: 15s
      timeout: 4s
      retries: 3
      start_period: 30s                                # JVM/Node cold starts
      start_interval: 2s                               # faster probes during start_period (newer Engine/Compose only)

  fastapi:
    image: myorg/ml-api:2.0.0                          # Python image (slim has no curl)
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status==200 else 1)"]  # no curl needed
      interval: 15s
      timeout: 5s
      retries: 3

  nginx:
    image: nginx:1.27-alpine
    depends_on:
      api:
        condition: service_healthy                     # do not proxy to a booting API
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1/nginx-health"]  # needs a location returning 200
      interval: 30s
      timeout: 3s
      retries: 3
```

```javascript
// api/health.js - /health endpoint worth probing (Express); checks real dependencies
app.get('/health', async (req, res) => {
  try {
    await Promise.race([
      Promise.all([pool.query('SELECT 1'), redis.ping()]),            // verify DB and Redis
      new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), 1000))  // 1s budget
    ]);
    res.status(200).send('ok');                                      // healthy
  } catch (e) {
    res.status(503).send('unhealthy');                               // unhealthy
  }
});
```

---

## 🟠 My Stack Integration
- **Node.js (alpine):** `wget` exists in busybox; on `node:20-slim` neither wget nor curl exists, so use `node -e "fetch('http://127.0.0.1:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"` (Node 18+).
- **FastAPI (python:slim):** no curl; use the Python one-liner above or install curl in the Dockerfile.
- **Nginx:** add `location /nginx-health { access_log off; return 200 "ok"; }`.
- **Dockerfile alternative:** `HEALTHCHECK --interval=30s CMD ...` bakes the check into the image; Compose `healthcheck:` overrides it.
- **VPS/AWS:** Compose does not restart unhealthy containers on its own. Use `willfarrell/autoheal`, or on AWS ALB target-group health checks / ECS task health checks.
- **Security:** keep `/health` shallow and non-sensitive (no versions, no stack traces); bind it to the internal network only.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `curl` in a slim image that does not contain it, so the check always fails.
✅ Correct: Use tools that exist (wget in alpine, python/node one-liners) or install curl.

❌ Mistake 2: `test: curl localhost` without `CMD` / `CMD-SHELL`; the string form gets run via shell, but mixing forms confuses people.
✅ Correct: Use `["CMD", ...]` or `["CMD-SHELL", "..."]` explicitly.

❌ Mistake 3: Using `localhost` that resolves to IPv6 `::1` when the app listens only on IPv4.
✅ Correct: Use `127.0.0.1`.

❌ Mistake 4: Very aggressive intervals (1s) with heavy checks that load the DB.
✅ Correct: Cheap checks, sensible 10 to 30 second intervals.

❌ Mistake 5: No `start_period`, so slow boots flip to unhealthy immediately.
✅ Correct: Set start_period to your worst-case startup time.

---

## 🧠 Tricky Interview Question
**Q:** The healthcheck shows `unhealthy`, but traffic still flows to the container and Docker does not restart it. Why? What does an unhealthy status actually do?

**Answer:** In plain Docker/Compose, `unhealthy` is only a label. It does not restart or stop the container, nor does it remove it from a published port. It affects `depends_on: service_healthy` at startup and is visible to tools. In Docker Swarm, an unhealthy task is replaced automatically; in Kubernetes the liveness/readiness probes drive restarts and traffic. On a single VPS use `autoheal` or a monitoring script to act on it.

---

## ⚫ Interview Questions + Answers

Q1: What do exit codes mean in a healthcheck?
A1: 0 = healthy, 1 = unhealthy; 2 is reserved and should not be used.

Q2: What is `start_period`?
A2: Grace time after start where failures do not count toward `retries`; a success in this window marks the container healthy immediately.

Q3: Compose `healthcheck` vs Dockerfile `HEALTHCHECK`?
A3: Compose overrides the image's. Use `healthcheck: { disable: true }` to turn it off.

Q4: What is the difference between liveness and readiness?
A4: Liveness: is the process alive and should it be restarted? Readiness: can it take traffic now? Docker has one healthcheck covering both; Kubernetes separates them.

Q5: Should the health endpoint check dependencies?
A5: Check critical dependencies with a short timeout for readiness, but avoid cascading failures: a flaky optional dependency should not make everything unhealthy.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Services have a slow start or critical dependencies
- You use `depends_on` conditions
- You want visibility with `docker ps` and monitoring

❌ Avoid when:
- The check is expensive or has side effects (writes)
- The image has no tool to run the check and you cannot add one

---

## 📊 Visual Diagram
```
 start --> [starting] --start_period grace--> probes every 30s
                              |
          test exit 0 ------> [healthy] <-------+
                              |                  |
          fail x retries ---> [unhealthy]        | recovers on next success
                              |                  |
                              +------------------+
 Consumers: depends_on(service_healthy), docker ps, autoheal, monitoring
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Healthcheck | Command that tests app health | सेहत जाँचने वाला command |
| interval | Time between checks | दो जाँचों के बीच का समय |
| timeout | Max time per check | एक जाँच का अधिकतम समय |
| retries | Failures before unhealthy | unhealthy से पहले असफलताएँ |
| start_period | Grace period at boot | शुरुआती छूट |
| autoheal | Tool restarting unhealthy containers | unhealthy को restart करने वाला tool |

---

## ⚡ 3-Line Summary
English: A healthcheck proves the app works, not just that the process exists.
Tune interval, timeout, retries, start_period and use tools present in the image.
Unhealthy is only a label on a single host; act on it with depends_on, autoheal or monitoring.
Hindi: Healthcheck साबित करता है कि app सच में चल रहा है, सिर्फ process मौजूद नहीं।
interval, timeout, retries, start_period tune करो और image में मौजूद tools use करो।
Single host पर unhealthy सिर्फ label है; इस पर depends_on, autoheal या monitoring से कार्रवाई करो।

---

## ➡️ Next Topic
**193. restart Policy** - what makes containers come back after a crash or a VPS reboot.
