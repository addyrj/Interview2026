# 403. Nginx Load Balancer in Docker
# हिंदी में: Docker में Nginx Load Balancer

---

## 🔵 Simple Definition (English)
An **Nginx load balancer** distributes incoming requests across several identical backend containers (replicas) using an `upstream` block. If one replica dies, Nginx stops sending traffic to it, so users keep getting responses.

## 🔵 सरल परिभाषा (Hindi)
**Nginx load balancer** आने वाली requests को कई एक जैसे backend containers (replicas) में `upstream` block से बाँटता है। एक replica मर जाए तो Nginx उसे traffic भेजना बंद कर देता है, इसलिए users को जवाब मिलता रहता है।

---

## 🔴 Problem it Solves
- One Node.js process uses one CPU core; a single container is both a performance limit and a single point of failure.
- Deploys or crashes cause downtime if only one instance exists.
- Traffic spikes (sale day, IPL match) overwhelm one instance.

## 🔴 यह क्यों बना? (Hindi)
- एक Node.js process एक CPU core इस्तेमाल करता है; अकेला container performance की सीमा भी है और single point of failure भी।
- सिर्फ एक instance हो तो deploy या crash पर downtime।
- Traffic spike (sale, IPL match) एक instance को दबा देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Run N replicas of the service (docker compose up --scale api=3)
Step 2 → Define upstream pointing to the service name "api"
Step 3 → Nginx resolves the name to ALL replica IPs (round-robin DNS)
Step 4 → For each request Nginx picks a server by algorithm:
         round-robin (default), least_conn, ip_hash, hash
Step 5 → Passive health: max_fails/fail_timeout marks a server down
         after failed attempts; proxy_next_upstream retries another
Step 6 → Replica recovers -> after fail_timeout Nginx tries it again
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Service के N replicas चलाओ (docker compose up --scale api=3)
Step 2 → Service नाम "api" की ओर इशारा करता upstream define करो
Step 3 → Nginx नाम को सभी replica IPs में resolve करता है
Step 4 → हर request के लिए algorithm से server चुनता है:
         round-robin (default), least_conn, ip_hash, hash
Step 5 → Passive health: max_fails/fail_timeout कई failures के बाद server
         को down मानता है; proxy_next_upstream दूसरे पर retry करता है
Step 6 → Replica ठीक होने पर fail_timeout बाद Nginx उसे फिर आज़माता है
```

---

## 🟡 Real World Example
A ticket-booking site on a Hostinger VPS runs three Node.js containers behind Nginx. During a concert sale, requests spread evenly. One container crashes from a memory leak; Nginx retries the failed request on another replica, Docker restarts the crashed one, and customers never see an error page.

## 🟡 Real Example Hindi mein
Hostinger VPS पर ticket-booking site Nginx के पीछे तीन Node.js containers चलाती है। Concert sale में requests बराबर बँटती हैं। एक container memory leak से crash होता है; Nginx failed request दूसरे replica पर retry करता है, Docker crashed container को restart करता है, और customers को error page नहीं दिखता।

---

## 💻 Code / Config Example — Basic

```nginx
# nginx/conf.d/lb.conf -- static list of three backends, round-robin
upstream api_pool {                         # name used in proxy_pass
    server api1:3000;                       # first replica
    server api2:3000;                       # second replica
    server api3:3000;                       # third replica
}

server {
    listen 80;                              # HTTP
    location / {
        proxy_pass http://api_pool;         # send to the pool
        proxy_set_header Host $host;        # keep original host
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  # client IP
    }
}
```

```yaml
# docker-compose.yml -- three explicit replicas
services:
  nginx:
    image: nginx:1.27-alpine                # load balancer
    ports: ["80:80"]
    volumes: ["./nginx/conf.d:/etc/nginx/conf.d:ro"]
    depends_on: [api1, api2, api3]
  api1: &api                                # YAML anchor: reuse definition
    build: ./api
    restart: unless-stopped
  api2: *api                                # same config as api1
  api3: *api                                # same config as api1
```

## 💻 Code / Config Example — Advanced

```nginx
# nginx/conf.d/lb.conf -- dynamic replicas via compose --scale, health aware
resolver 127.0.0.11 valid=5s ipv6=off;      # Docker DNS; re-resolve every 5s

upstream api_pool {
    zone api_pool 64k;                      # shared memory zone (needed for resolve in some versions)
    least_conn;                             # pick the server with fewest active connections
    server api:3000 max_fails=3 fail_timeout=10s;  # 3 failures -> skip for 10s
    keepalive 32;                           # reuse backend connections
}

server {
    listen 80;
    server_tokens off;

    location /api/ {
        set $backend http://api:3000;       # variable forces DNS lookup at request time
        proxy_pass $backend;                # round-robins across all IPs Docker returns
        proxy_http_version 1.1;
        proxy_set_header Connection "";     # needed for upstream keepalive
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 3s;           # detect dead replica quickly
        proxy_next_upstream error timeout http_502 http_503;  # retry on these failures
        proxy_next_upstream_tries 2;        # at most 2 attempts
    }
}
```

```yaml
# docker-compose.yml -- scale with one line
services:
  nginx:
    image: nginx:1.27-alpine
    restart: unless-stopped
    ports: ["80:80"]
    volumes: ["./nginx/conf.d:/etc/nginx/conf.d:ro"]
    depends_on:
      api: { condition: service_healthy }   # LB starts when at least one replica is healthy
  api:
    build: ./api
    restart: unless-stopped
    # no container_name and no host ports -> can be scaled
    deploy:
      resources:
        limits: { cpus: "0.50", memory: 512M }   # per-replica limits (Compose v2 honours these)
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://127.0.0.1:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
      interval: 10s
      timeout: 3s
      retries: 3
# run:  docker compose up -d --scale api=3
```

Caveats: the variable `proxy_pass` + `resolver` approach cannot use the `upstream` block (variable form ignores upstream group features such as `least_conn`/`max_fails`), so choose one: static upstream with fixed names (as in Basic), or dynamic DNS round-robin (as above, where the `upstream` block is then unused and can be deleted). Open-source Nginx only does passive health checks; active checks need Nginx Plus. Not run locally.

---

## 🟠 My Stack Integration
- Node.js is single-threaded: 3 replicas on a 4-core VPS uses cores better than one container (alternative: Node `cluster` or PM2 inside the container).
- FastAPI: run `uvicorn --workers 2` per container or scale containers; same Nginx pattern with port 8000.
- Sessions: if you keep sessions in memory, use Redis or `ip_hash` (sticky) otherwise logins will "randomly" fail.
- On AWS you might replace this with an ALB, but the same upstream thinking applies.

```nginx
# sticky by client IP for legacy in-memory sessions (temporary measure)
upstream api_pool {
    ip_hash;                                # same client IP -> same replica
    server api1:3000;
    server api2:3000;
}
```

Security: keep replicas on an internal network, never publish replica ports, set `proxy_connect_timeout` to avoid slowloris-style pile-ups, and log `$upstream_addr` for forensics.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `container_name:` on a service you scale; Compose cannot create a second container with the same name.
✅ Correct: Remove `container_name` and `ports` from scaled services.

❌ Mistake 2: Assuming Nginx notices new replicas after `--scale` automatically; with a static upstream it resolved IPs only at start.
✅ Correct: Use `resolver` + variable in `proxy_pass`, or `nginx -s reload` after scaling.

❌ Mistake 3: Keeping state (sessions, uploads, cache) inside a replica.
✅ Correct: Externalise to Redis, S3 or a database.

❌ Mistake 4: Retrying non-idempotent POSTs on another upstream blindly.
✅ Correct: Keep `proxy_next_upstream` limited (default does not retry non-idempotent requests after they were sent); do not add `non_idempotent` casually.

---

## 🧠 Tricky Interview Question
You scaled `api` from 2 to 5 replicas but Nginx still shows traffic on only the first two. Why?

Answer: Nginx resolves hostnames in an `upstream` block (or a constant `proxy_pass`) once at startup/reload and caches the IPs. New containers have new IPs Nginx never learned. Fix with `nginx -s reload` after scaling, or use `resolver 127.0.0.11 valid=5s;` with a variable `proxy_pass` so lookup is repeated. Also confirm clients are not pinned by `ip_hash` or long-lived keepalive connections.

---

## ⚫ Interview Questions + Answers

Q1: Name Nginx balancing algorithms.
A1: Round-robin (default), `least_conn`, `ip_hash`, generic `hash $key consistent`, `random`; weights via `weight=`.

Q2: Active vs passive health checks?
A2: Passive: Nginx reacts to real request failures (`max_fails`). Active: it probes `/health` on a schedule (Nginx Plus or external tools). Open-source Nginx has passive only.

Q3: Layer 4 vs Layer 7 balancing?
A3: L4 (`stream` module) forwards TCP/UDP without reading HTTP; L7 (`http`) understands URLs, headers, cookies and can route by path.

Q4: How do you do weighted traffic, e.g. canary 10%?
A4: `server api_v1:3000 weight=9; server api_v2:3000 weight=1;`.

Q5: What is a single point of failure left in this design?
A5: The Nginx/VPS itself. Mitigate with two nodes + floating IP/keepalived, a cloud LB in front, or auto-restart plus fast rebuild.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- One instance cannot handle load or you want HA across deploys.
- You run a single VPS but want to use all CPU cores.

❌ Avoid when:
- The app is stateful and not ready to scale horizontally.
- You already run Kubernetes/ECS with a managed LB; do not stack redundant layers.

---

## 📊 Visual Diagram
```
 Clients
    |
    v
 +-----------+   least_conn / round-robin
 |  nginx    |----------------+-------------+
 +-----------+                |             |
                              v             v
                        +---------+   +---------+   +---------+
                        | api #1  |   | api #2  |   | api #3  |
                        | :3000   |   | :3000   |   | :3000   |
                        +---------+   +---------+   +---------+
                              \            |            /
                               +--- shared Redis / DB --+
 failed replica -> max_fails -> skipped for fail_timeout
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Upstream | Pool of backend servers | backend servers का pool |
| Round-robin | Take turns in order | बारी-बारी |
| `least_conn` | Fewest active connections wins | सबसे कम connections |
| `ip_hash` | Sticky by client IP | IP के आधार पर sticky |
| `max_fails` | Failures before marking down | कितनी failures पर down |
| Replica | Identical running copy | एक जैसी copy |
| Sticky session | Same user -> same server | एक user, एक server |

---

## ⚡ 3-Line Summary
English: Nginx spreads requests across replicas using upstream and an algorithm.
Passive health checks skip failing servers; DNS caching means you must reload or use a resolver.
Keep replicas stateless and unpublished.
Hindi: Nginx upstream और algorithm से requests replicas में बाँटता है।
Passive health checks failing servers को skip करते हैं; DNS caching की वजह से reload या resolver चाहिए।
Replicas को stateless रखें और publish न करें।

---

## ➡️ Next Topic
404. Nginx SSL in Docker - the load-balanced entry point must now speak HTTPS.
