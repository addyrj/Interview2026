---

# 210. Full Stack Compose Example
# हिंदी में: Full Stack Compose उदाहरण

---

## 🔵 Simple Definition (English)
A **full stack Compose example** runs a complete production-style system from one file: reverse proxy (Nginx), React frontend, FastAPI backend, background worker, PostgreSQL and Redis. It shows networks, volumes, healthchecks, secrets, profiles and resource limits working together.

## 🔵 सरल परिभाषा (Hindi)
**Full stack Compose example** एक ही file से पूरा production-जैसा system चलाता है: reverse proxy (Nginx), React frontend, FastAPI backend, background worker, PostgreSQL और Redis। इसमें networks, volumes, healthchecks, secrets, profiles और resource limits साथ काम करते दिखते हैं।

---

## 🔴 Problem it Solves
Real apps are not just "API + DB". They also need a cache, a queue worker for slow jobs (emails, reports), a proxy for TLS and routing, and separate dev/prod behaviour. Managing six containers with separate commands leads to wrong start order, exposed internal ports, and config drift between laptop and server. A single declarative file makes the whole topology reviewable in a pull request.

## 🔴 यह क्यों बना? (Hindi)
असली apps सिर्फ "API + DB" नहीं होते। उन्हें cache, slow jobs (email, reports) के लिए queue worker, TLS और routing के लिए proxy, और dev/prod अलग behaviour भी चाहिए। छह containers को अलग commands से चलाने पर start order गलत होता है, internal ports expose हो जाते हैं, और laptop-server के बीच config drift आता है। एक declarative file पूरी topology को pull request में review करने लायक बनाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide tiers: edge (proxy) / app (web, api, worker) / data (db, redis)
Step 2 → Create 3 networks: edge, app, data  (data is internal)
Step 3 → Put each service only on the networks it needs
Step 4 → Add healthchecks and depends_on conditions for start order
Step 5 → Secrets via files, config via env, state via named volumes
Step 6 → Use profiles (e.g. "debug") for optional tools like pgadmin
Step 7 → docker compose config (validate) -> up -d --build -> ps -> logs
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Tiers तय करो: edge (proxy) / app (web, api, worker) / data (db, redis)
Step 2 → 3 networks बनाओ: edge, app, data  (data internal है)
Step 3 → हर service को सिर्फ ज़रूरी networks में रखो
Step 4 → Start order के लिए healthcheck और depends_on conditions जोड़ो
Step 5 → Secrets files से, config env से, state named volumes से
Step 6 → Optional tools (जैसे pgadmin) के लिए profiles (जैसे "debug") इस्तेमाल करो
Step 7 → docker compose config (validate) -> up -d --build -> ps -> logs
```

---

## 🟡 Real World Example
A Zomato-like **restaurant onboarding portal**: restaurant owners upload menus (React), FastAPI validates and stores them in Postgres, and a **worker** (Celery/RQ with Redis) resizes images and sends WhatsApp/email notifications in the background. Redis also caches the city-wise restaurant list. One EC2 `t3.medium` runs the whole thing with Compose, Nginx at the edge, and nightly `pg_dump` to S3.

## 🟡 Real Example Hindi mein
Zomato जैसा **restaurant onboarding portal**: restaurant owners menu upload करते हैं (React), FastAPI validate करके Postgres में रखता है, और **worker** (Redis के साथ Celery/RQ) background में images resize करता और WhatsApp/email भेजता है। Redis city-wise restaurant list भी cache करता है। एक EC2 `t3.medium` पर पूरा system Compose से चलता है, edge पर Nginx, और रात को `pg_dump` S3 पर।

---

## 💻 Code / Config Example — Basic

```yaml
# docker-compose.yml  (BASIC: api + worker + db + redis)
services:
  db:                                  # PostgreSQL
    image: postgres:16-alpine          # example tag
    environment:
      POSTGRES_PASSWORD: secret        # demo only
      POSTGRES_DB: appdb               # database name
    volumes:
      - pgdata:/var/lib/postgresql/data   # persist data

  redis:                               # cache + job queue
    image: redis:7-alpine              # example tag
    command: ["redis-server", "--appendonly", "yes"]   # persist writes to disk (AOF)
    volumes:
      - redisdata:/data                # persist AOF file

  api:                                 # FastAPI
    build: ./api                       # api/Dockerfile
    environment:
      DATABASE_URL: postgresql://postgres:secret@db:5432/appdb   # DB by service name
      REDIS_URL: redis://redis:6379/0  # Redis by service name
    ports:
      - "8000:8000"                    # expose API for testing
    depends_on:
      - db                             # start order only
      - redis

  worker:                              # same image as api, different command
    build: ./api                       # reuse the api image
    command: ["python", "-m", "rq", "worker", "--url", "redis://redis:6379/0"]   # RQ worker
    environment:
      DATABASE_URL: postgresql://postgres:secret@db:5432/appdb   # worker also uses DB
    depends_on:
      - redis                          # needs the queue

volumes:
  pgdata:                              # named volume for Postgres
  redisdata:                           # named volume for Redis
```

```dockerfile
# api/Dockerfile (used by api and worker)
FROM python:3.12-slim
# small Python base (example tag)
WORKDIR /app
# working directory
COPY requirements.txt .
# copy deps first for layer cache
RUN pip install --no-cache-dir -r requirements.txt
# install fastapi uvicorn psycopg2-binary redis rq etc.
COPY . .
# copy source
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# default command: API server (worker overrides it)
```

---

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml  (ADVANCED full stack)
name: onboarding                       # project name prefix

x-app-defaults: &app-defaults          # YAML anchor: settings shared by api and worker
  build: ./api                         # same image for both
  restart: unless-stopped              # auto restart
  read_only: true                      # immutable root filesystem
  tmpfs:
    - /tmp                             # writable scratch in RAM
  cap_drop:
    - ALL                              # no Linux capabilities
  security_opt:
    - no-new-privileges:true           # no privilege escalation
  secrets:
    - db_password                      # DB password file
  networks:
    - app                              # app tier
    - data                             # reach db and redis
  environment: &app-env                # shared environment
    DB_HOST: db                        # Postgres host
    DB_USER: app                       # Postgres user
    DB_NAME: appdb                     # Postgres database
    DB_PASSWORD_FILE: /run/secrets/db_password   # secret file path
    REDIS_URL: redis://redis:6379/0    # Redis URL

services:
  proxy:                               # edge Nginx: TLS + routing
    image: nginx:1.27-alpine           # example tag
    restart: unless-stopped            # auto restart
    ports:
      - "80:80"                        # HTTP
      - "443:443"                      # HTTPS
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro   # config, read-only
      - ./certs:/etc/nginx/certs:ro    # TLS certs (from certbot), read-only
    depends_on:
      api:
        condition: service_healthy     # route only when API is up
      web:
        condition: service_started     # web has no healthcheck needed
    networks:
      - edge                           # public side
      - app                            # to reach api and web
    deploy:
      resources:
        limits: { cpus: "0.25", memory: 128m }   # tiny proxy

  web:                                 # React static files in Nginx
    build: ./web                       # multi-stage build
    restart: unless-stopped            # auto restart
    networks:
      - app                            # only talks to proxy
    read_only: true                    # static files need no writes
    tmpfs:
      - /var/cache/nginx               # nginx cache dir
      - /var/run                       # pid file
      - /tmp                           # temp
    cap_drop: [ALL]                    # drop all caps
    cap_add: [CHOWN, SETGID, SETUID]   # nginx image needs these to start workers

  api:
    <<: *app-defaults                  # merge shared settings
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"]   # no curl needed in slim image
      interval: 15s                    # every 15s
      timeout: 5s                      # 5s max
      retries: 3                       # 3 strikes
      start_period: 20s                # boot grace
    depends_on:
      db:
        condition: service_healthy     # DB must be ready
      redis:
        condition: service_healthy     # Redis must be ready
    deploy:
      resources:
        limits: { cpus: "1.0", memory: 512m }   # API cap

  worker:
    <<: *app-defaults                  # same hardening
    command: ["python", "-m", "rq", "worker", "--url", "redis://redis:6379/0"]   # run the queue worker
    depends_on:
      redis:
        condition: service_healthy     # needs Redis
    stop_grace_period: 60s             # let the running job finish on stop
    deploy:
      resources:
        limits: { cpus: "0.50", memory: 512m }   # worker cap

  db:
    image: postgres:16-alpine          # example tag
    restart: unless-stopped            # auto restart
    environment:
      POSTGRES_USER: app               # user
      POSTGRES_DB: appdb               # database
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password   # secret file
    secrets:
      - db_password                    # mount secret
    volumes:
      - pgdata:/var/lib/postgresql/data   # persistent data
    networks:
      - data                           # internal network only
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]   # readiness probe
      interval: 10s                    # every 10s
      timeout: 5s                      # 5s max
      retries: 5                       # 5 strikes
    deploy:
      resources:
        limits: { memory: 1g }         # DB RAM cap

  redis:
    image: redis:7-alpine              # example tag
    restart: unless-stopped            # auto restart
    command: ["redis-server", "--appendonly", "yes", "--maxmemory", "128mb", "--maxmemory-policy", "allkeys-lru"]   # cap memory, evict old keys
    volumes:
      - redisdata:/data                # AOF persistence
    networks:
      - data                           # internal only
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]   # returns PONG when healthy
      interval: 10s                    # every 10s
      timeout: 3s                      # 3s max
      retries: 5                       # 5 strikes

  pgadmin:                             # optional DB UI, only when requested
    image: dpage/pgadmin4:8            # example tag
    profiles: ["debug"]                # started only with --profile debug
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com   # login email
      PGADMIN_DEFAULT_PASSWORD: change-me        # change it, debug use only
    ports:
      - "127.0.0.1:5050:80"            # localhost only; use SSH tunnel
    networks:
      - data                           # reach db

networks:
  edge:                                # internet-facing
  app:                                 # app tier
  data:                                # db + redis
    internal: true                     # no internet from data tier

secrets:
  db_password:
    file: ./secrets/db_password.txt    # keep out of git

volumes:
  pgdata:                              # Postgres data
  redisdata:                           # Redis AOF data
```

```nginx
# nginx/default.conf  (edge proxy)
server {
    listen 80;                                    # accept HTTP
    server_name example.com;                      # your domain
    return 301 https://$host$request_uri;         # force HTTPS
}
server {
    listen 443 ssl;                               # accept HTTPS
    server_name example.com;                      # your domain
    ssl_certificate     /etc/nginx/certs/fullchain.pem;   # cert chain
    ssl_certificate_key /etc/nginx/certs/privkey.pem;     # private key
    location /api/ {
        proxy_pass http://api:8000;               # FastAPI by service name
        proxy_set_header Host $host;              # keep host
        proxy_set_header X-Forwarded-Proto $scheme;   # tell app it was HTTPS
        proxy_set_header X-Real-IP $remote_addr;      # client IP
    }
    location / {
        proxy_pass http://web:80;                 # React static server
    }
}
```

Commands:
```bash
docker compose config -q                 # validate syntax, prints nothing if OK
docker compose up -d --build             # start everything
docker compose --profile debug up -d     # include pgadmin
docker compose ps                        # check health column
docker compose logs -f api worker        # follow logs
```

Verification note: YAML was parsed and the structure checked, but the stack was not built or run locally (no Docker daemon). The `cap_add` list for Nginx may need adjusting per image version; test with `docker compose logs web`.

---

## 🟠 My Stack Integration
Maps one-to-one: **FastAPI** = `api`, **React** = `web`, **Nginx** = `proxy`, **VPS/AWS** = host running `docker compose up -d`. On a VPS, get certificates with certbot on the host and mount `./certs`. On AWS, keep `proxy` + ALB or drop `proxy` and let ALB route `/api` to `api`. Swap `db` for RDS and `redis` for ElastiCache when load grows; only the env values change.

```yaml
# docker-compose.prod.yml  -> override for AWS with managed services
services:
  api:
    environment:
      DB_HOST: mydb.xxxx.ap-south-1.rds.amazonaws.com   # RDS endpoint (example)
      REDIS_URL: redis://my-cache.xxxx.cache.amazonaws.com:6379/0   # ElastiCache (example)
  db:
    profiles: ["local-only"]           # never started in prod unless this profile is enabled
  redis:
    profiles: ["local-only"]           # same for redis
```
Note: `api` still lists `db`/`redis` in `depends_on`, so for a real AWS setup remove those entries from the base file (or use the `!reset` tag, Compose v2.24+).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting every service on one default network.
✅ Correct: Split edge/app/data networks; the DB should not be reachable from the proxy.

❌ Mistake 2: Running the worker with a default 10s stop timeout, killing jobs mid-way.
✅ Correct: Set `stop_grace_period` and handle SIGTERM in the worker.

❌ Mistake 3: Redis without `maxmemory`, growing until the host OOMs.
✅ Correct: Set `maxmemory` and an eviction policy (cache) or use persistence plus limits (queue).

❌ Mistake 4: Copy-pasting `latest` tags.
✅ Correct: Pin versions (and digests for high security) and update on purpose.

❌ Mistake 5: Exposing pgadmin/Redis ports publicly.
✅ Correct: Bind to `127.0.0.1` and use SSH tunnel or a VPN.

---

## 🧠 Tricky Interview Question
**Q:** `docker compose up` shows all containers "Up", but users get 502 from Nginx for the first minute after every deploy. Why, and how do you fix it?

**Answer:** "Up" only means the process started, not that the app is ready. FastAPI may still be connecting to DB/running migrations while Nginx already forwards traffic. Fix: add a `healthcheck` to `api`, make `proxy` depend on `service_healthy`, and use `start_period`. Also Nginx resolves `api` once at startup; if the API container gets recreated with a new IP, Nginx may keep the stale IP. Solutions: restart proxy on deploy, or use `resolver 127.0.0.11` with a variable in `proxy_pass`.

---

## ⚫ Interview Questions + Answers

**Q1: What is a YAML anchor and why use it here?**
A1: `&name` defines a reusable block and `<<: *name` merges it. It removes duplicated hardening settings between `api` and `worker`.

**Q2: What do Compose profiles do?**
A2: Services with `profiles` start only when that profile is enabled (`--profile debug`). Good for admin tools, test seeders, or one-off jobs.

**Q3: Why a separate worker container instead of threads inside the API?**
A3: Independent scaling, restart and resource limits; a heavy job cannot slow API responses, and you can run `docker compose up --scale worker=3`.

**Q4: How do you do zero-downtime deploys with plain Compose?**
A4: Plain Compose is not truly zero-downtime. Options: run two api replicas behind Nginx and recreate one at a time, use blue/green with two projects, or move to ECS/Kubernetes rolling updates.

**Q5: How do you back up this stack?**
A5: `docker compose exec -T db pg_dump -U app appdb | gzip > backup.sql.gz` on cron, upload to S3 with lifecycle rules, and test restores. Redis AOF/RDB if the queue matters.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- One server hosts the whole product (startup, internal tool, staging)
- You need a reproducible stack for developers and CI

❌ Avoid when:
- You need auto-scaling, self-healing across nodes, or strict zero downtime
- Team size and traffic justify ECS/EKS and managed databases

---

## 📊 Visual Diagram
```
 Internet
    |
 +--v-------------- edge network ----------------+
 |  proxy (Nginx :80/:443)                       |
 +--+---------------------------------------------+
    |            app network
 +--v----+   +--------+   +----------+
 |  web  |   |  api   |   |  worker  |
 | React |   |FastAPI |   |  RQ/Celery|
 +-------+   +---+----+   +----+-----+
                 |             |       data network (internal)
            +----v-------------v----+
            |  db (Postgres)  redis |
            +-----------------------+
                 [pgdata]  [redisdata]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Profile | Optional service group | Optional services का group |
| Anchor/alias | Reusable YAML block | दोबारा इस्तेमाल होने वाला YAML block |
| Worker | Background job processor | Background jobs चलाने वाला process |
| Tier | Layer of architecture | Architecture की परत |
| stop_grace_period | Wait time before SIGKILL | SIGKILL से पहले रुकने का समय |

---

## ⚡ 3-Line Summary
English: A full stack file wires proxy, web, API, worker, DB and Redis with tiered networks.
Healthchecks control start order; secrets, limits and read-only roots harden it.
Great for one server; move to ECS/Kubernetes when you need scale.

Hindi: Full stack file proxy, web, API, worker, DB और Redis को tiered networks से जोड़ती है।
Healthchecks start order तय करते हैं; secrets, limits और read-only root से hardening होती है।
एक server के लिए बढ़िया; scale चाहिए तो ECS/Kubernetes पर जाओ।

---

## ➡️ Next Topic
**211. Production Docker Checklist**: now that the stack runs, we learn what to verify before it faces real users.

---
