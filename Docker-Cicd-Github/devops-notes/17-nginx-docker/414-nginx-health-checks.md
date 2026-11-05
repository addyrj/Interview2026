# 414. Nginx Health Checks
# हिंदी में: Nginx Health Checks (Docker में सेहत की जाँच)

---

## 🔵 Simple Definition (English)
A **health check** is a tiny, cheap request that tells Docker, a load balancer or a monitor whether a service is alive and ready. With Nginx in Docker there are three layers: (1) Docker `HEALTHCHECK` for the Nginx container itself, (2) a `/healthz` endpoint that Nginx answers directly, and (3) **passive upstream checks** (`max_fails`, `fail_timeout`) that stop sending traffic to a broken backend.

## 🔵 सरल परिभाषा (Hindi)
**Health check** एक छोटी और सस्ती request है जो Docker, load balancer या monitor को बताती है कि service ज़िंदा और तैयार है या नहीं। Docker में Nginx के लिए तीन layers हैं: (1) Nginx container के लिए Docker `HEALTHCHECK`, (2) `/healthz` endpoint जिसका जवाब Nginx खुद देता है, और (3) **passive upstream checks** (`max_fails`, `fail_timeout`) जो खराब backend को traffic भेजना बंद कर देते हैं।

---

## 🔴 Problem it Solves
- A container can be "running" but Nginx may have crashed config, or the backend (Node.js) may be hung. `docker ps` still shows `Up`.
- During deploy, Nginx may start before the API is ready and return 502 to real users.
- Without checks, a dead backend keeps receiving a share of traffic in the upstream pool.
- Orchestrators and monitors need one stable URL to ask "are you OK?".

## 🔴 यह क्यों बना? (Hindi)
- Container "running" हो सकता है पर Nginx का config टूटा हो, या backend (Node.js) hang हो। `docker ps` फिर भी `Up` दिखाता है।
- Deploy के समय Nginx API से पहले start हो सकता है और असली users को 502 मिलता है।
- Checks न हों तो मरा हुआ backend upstream pool में traffic का हिस्सा पाता रहता है।
- Orchestrators और monitors को एक fixed URL चाहिए जो पूछ सके "सब ठीक है?"।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add `location = /healthz` in Nginx that returns 200 directly (no backend call)
Step 2 → Turn off access_log for it so probes do not flood logs
Step 3 → Add Docker HEALTHCHECK (wget/curl to 127.0.0.1/healthz) with interval/timeout/retries
Step 4 → Docker marks container: starting -> healthy -> unhealthy based on exit code
Step 5 → Compose `depends_on: condition: service_healthy` waits for it before starting dependents
Step 6 → In upstream, set max_fails + fail_timeout so a bad backend is skipped (passive check)
Step 7 → Add a deep check `/api/health` proxied to the app (DB ping) for monitors
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Nginx में `location = /healthz` बनाओ जो सीधे 200 लौटाए (backend call नहीं)
Step 2 → उसका access_log बंद करो ताकि probes से logs न भरें
Step 3 → Docker HEALTHCHECK जोड़ो (127.0.0.1/healthz पर wget/curl) interval/timeout/retries के साथ
Step 4 → Docker exit code देखकर container को starting -> healthy -> unhealthy मार्क करता है
Step 5 → Compose `depends_on: condition: service_healthy` dependents को इंतज़ार कराता है
Step 6 → upstream में max_fails + fail_timeout लगाओ ताकि खराब backend skip हो (passive check)
Step 7 → Monitors के लिए deep check `/api/health` रखो जो app तक जाकर DB ping करे
```

---

## 🟡 Real World Example
A food-delivery app on a VPS ships a new API image every evening. Earlier, `docker compose up -d` started Nginx instantly and for ~10 seconds customers saw 502 while Node.js connected to MongoDB. The team added a `/healthz` for Nginx, a `/health` for the API with a DB ping, and `depends_on: service_healthy`. Now Nginx only starts after the API reports healthy, and the uptime monitor hits `/healthz` every minute.

## 🟡 Real Example Hindi mein
VPS पर एक food-delivery app हर शाम नया API image deploy करती है। पहले `docker compose up -d` से Nginx तुरंत चालू हो जाता था और Node.js के MongoDB से जुड़ने तक ~10 सेकंड customers को 502 दिखता था। Team ने Nginx का `/healthz`, API का DB-ping वाला `/health` और `depends_on: service_healthy` जोड़ा। अब Nginx तभी चालू होता है जब API healthy बोले, और uptime monitor हर मिनट `/healthz` पर जाता है।

---

## 💻 Code / Config Example — Basic
```yaml
# docker-compose.yml  (basic: Nginx container with its own health check)
services:                                  # list of containers
  web:                                     # our Nginx service
    image: nginx:1.27-alpine               # example tag, update to current stable
    ports:
      - "80:80"                            # publish HTTP port
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro   # mount config read-only
    healthcheck:                           # Docker-level probe
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1/healthz"]  # busybox wget exists in alpine
      interval: 15s                        # run probe every 15 seconds
      timeout: 3s                          # fail probe if no answer in 3 seconds
      retries: 3                           # 3 failures in a row => unhealthy
      start_period: 5s                     # grace time after start (failures not counted)
    restart: unless-stopped                # restart if the process itself dies
```

```nginx
# nginx.conf  (basic: answer /healthz directly)
events {}                                  # required block, defaults are fine
http {                                     # HTTP context
  server {                                 # one virtual host
    listen 80;                             # listen on port 80
    location = /healthz {                  # exact match, fastest lookup
      access_log off;                      # do not log probe requests
      default_type text/plain;             # plain text response
      return 200 "ok\n";                   # answer without touching any backend
    }
  }
}
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml  (production: API health -> Nginx waits -> passive checks)
services:
  mongo:
    image: mongo:7                         # example tag
    healthcheck:
      test: ["CMD", "mongosh", "--quiet", "--eval", "db.adminCommand('ping').ok"]  # ping DB
      interval: 10s                        # every 10s
      timeout: 5s                          # 5s max
      retries: 5                           # 5 failures => unhealthy
      start_period: 20s                    # DB needs time to boot
  api:
    build: ./api                           # Node.js image built from ./api
    environment:
      MONGO_URL: mongodb://mongo:27017/app # service-name DNS on compose network
    depends_on:
      mongo:
        condition: service_healthy         # start only after Mongo is healthy
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://127.0.0.1:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]  # Node 18+ fetch
      interval: 10s                        # probe every 10s
      timeout: 3s                          # fail after 3s
      retries: 3                           # 3 strikes
      start_period: 15s                    # allow app boot
  web:
    image: nginx:1.27-alpine
    ports: ["80:80"]                       # public HTTP
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      api:
        condition: service_healthy         # no 502 at start-up
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1/healthz"]
      interval: 15s
      timeout: 3s
      retries: 3
    restart: unless-stopped
```

```nginx
# nginx.conf  (production: passive checks + stub_status for monitors)
events { worker_connections 1024; }        # max connections per worker
http {
  upstream api_pool {                      # backend pool
    server api:3000 max_fails=3 fail_timeout=10s;  # 3 errors => skip 10s (passive check)
    keepalive 16;                          # reuse upstream connections
  }
  server {
    listen 80;
    location = /healthz {                  # liveness of Nginx only
      access_log off;
      add_header Cache-Control "no-store"; # never cache probe result
      default_type text/plain;
      return 200 "ok\n";
    }
    location = /nginx_status {             # connection counters (needed in 421/417 for exporters)
      stub_status;                         # built-in module
      access_log off;
      allow 127.0.0.1;                     # only local probes
      allow 172.16.0.0/12;                 # docker bridge networks
      deny all;                            # everyone else blocked
    }
    location /api/ {                       # real traffic
      proxy_pass http://api_pool;          # use pool
      proxy_http_version 1.1;              # needed for keepalive
      proxy_set_header Connection "";      # clear header for keepalive
      proxy_next_upstream error timeout http_502 http_503;  # retry on another server
      proxy_connect_timeout 2s;            # fail fast when backend is down
    }
  }
}
```
Note: configs here use only standard Nginx/Compose syntax; they were syntax-parsed for YAML only, not run against a Docker daemon.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: expose `GET /health` (cheap) and `GET /ready` (DB ping). FastAPI: `@app.get("/health")`.
- **React**: static build served by Nginx; `/healthz` proves Nginx is up even when API is down.
- **VPS**: external monitor (Uptime Kuma, 426) hits `https://example.com/healthz`.
- **AWS**: ALB target group health check path `/healthz`, matcher 200, interval 15s.

```yaml
# Same idea on AWS ALB (Terraform-like snippet shown as YAML for brevity)
health_check:
  path: /healthz           # Nginx answers 200
  interval: 15             # seconds between checks
  healthy_threshold: 2     # 2 OK => in service
  unhealthy_threshold: 3   # 3 fail => out of service
  matcher: "200"           # expected status
```

**Security**: keep `/nginx_status` restricted by `allow/deny`; health endpoints must not leak versions, DB names or stack traces. Use `server_tokens off;`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Health check calls `curl` but the `nginx:alpine` image has no curl.
✅ Correct: Use `wget` (busybox, present) or install curl in your own image.

❌ Mistake 2: `/healthz` proxied to the backend, so a slow DB marks Nginx unhealthy and restarts it.
✅ Correct: Liveness (Nginx only) and readiness (backend+DB) are separate URLs.

❌ Mistake 3: Probes logged to `access_log`, burying real traffic and growing logs.
✅ Correct: `access_log off;` in the health location.

❌ Mistake 4: Expecting `depends_on` alone to wait for readiness.
✅ Correct: Add `condition: service_healthy` and a healthcheck on the dependency.

❌ Mistake 5: Assuming open-source Nginx does active upstream checks (`health_check` directive).
✅ Correct: That directive is Nginx Plus only. Open source = passive `max_fails`, or use HAProxy/Traefik/ALB.

---

## 🧠 Tricky Interview Question
Your container shows `healthy`, yet users get 502 for `/api`. How is that possible?

Answer: The Docker healthcheck only tested `/healthz`, which Nginx answers itself. It proves Nginx is alive, not that the upstream works. Fix: add a readiness probe through the proxy (`/api/health`) for monitors, use `max_fails`/`proxy_next_upstream`, and alert on 5xx rate. Also remember `restart: unless-stopped` does NOT restart an `unhealthy` container in plain Compose; only a crash triggers restart (Swarm/Kubernetes act on health).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between liveness and readiness?
A1: Liveness = process is alive (restart if not). Readiness = it can serve traffic (remove from pool if not). Nginx `/healthz` is liveness; `/api/health` with DB ping is readiness.

Q2: What does `start_period` do?
A2: Failures during that grace window are not counted toward `retries`, so slow-booting apps are not marked unhealthy early.

Q3: How does passive health checking work in open-source Nginx?
A3: When a request to a server fails `max_fails` times within `fail_timeout`, Nginx marks it unavailable for `fail_timeout` and skips it. It learns from real traffic, no probe requests.

Q4: Why `127.0.0.1` and not `localhost` in alpine?
A4: `localhost` may resolve to IPv6 `::1` while Nginx listens only on IPv4, so the probe fails. `127.0.0.1` is explicit.

Q5: How do you see health status?
A5: `docker ps` (STATUS column) or `docker inspect --format '{{json .State.Health}}' web`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production container behind a proxy or monitor.
- Deploys where start order matters (DB -> API -> Nginx).
- Load-balancing several backends.

❌ Avoid when:
- Probe is heavy (full DB query every second) and itself causes load.
- You put business logic or secrets in the health response.

---

## 📊 Visual Diagram
```
 Monitor/ALB ──GET /healthz──► [ Nginx ] ──200 ok (self-answered)
                                  │
 Docker daemon ─HEALTHCHECK─►     │ proxy_pass (max_fails=3, fail_timeout=10s)
   starting→healthy→unhealthy     ▼
                         ┌──────────────┐
                         │ api:3000  ✔  │ ◄── /health (DB ping)
                         │ api2:3000 ✘  │ ◄── skipped for 10s
                         └──────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HEALTHCHECK | Docker probe command | Docker की जाँच command |
| Liveness | Process alive? | प्रोसेस ज़िंदा है? |
| Readiness | Ready for traffic? | traffic के लिए तैयार? |
| max_fails | Errors before skipping server | skip से पहले errors |
| fail_timeout | Skip duration / window | skip की अवधि |
| stub_status | Nginx counters page | Nginx counters पेज |

---

## ⚡ 3-Line Summary
English: Nginx health = `/healthz` + Docker HEALTHCHECK + `service_healthy` ordering.
Open-source Nginx checks backends passively via `max_fails`/`fail_timeout`.
Separate liveness from readiness and keep status pages private.

Hindi: Nginx health = `/healthz` + Docker HEALTHCHECK + `service_healthy` ordering।
Open-source Nginx backend को `max_fails`/`fail_timeout` से passively जाँचता है।
Liveness और readiness अलग रखो और status pages private रखो।

---

## ➡️ Next Topic
**415. Nginx Logs in Docker**: health probes and errors are only useful if you can read the logs; next we handle access/error logs, stdout/stderr and rotation in containers.

---
