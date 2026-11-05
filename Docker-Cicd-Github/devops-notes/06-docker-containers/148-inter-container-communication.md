---

# 148. Inter-Container Communication
# हिंदी में: Containers के बीच आपसी बातचीत

---

## 🔵 Simple Definition (English)
Inter-container communication (ICC) is how one container calls another: over a **shared Docker network** using the other container's **service name and internal port** (for example `http://api:3000`). Published ports (`-p`) are only for traffic coming from outside the host.

## 🔵 सरल परिभाषा (Hindi)
Inter-container communication (ICC) यानी एक container दूसरे को कैसे call करे: **साझा Docker network** पर दूसरे container के **service name और internal port** से (जैसे `http://api:3000`)। Published ports (`-p`) सिर्फ host के बाहर से आने वाले traffic के लिए हैं।

---

## 🔴 Problem it Solves
Real apps are many containers: Nginx, API, worker, Redis, DB. They must talk reliably, privately, and without exposing everything to the internet. Beginners publish every port and connect through `localhost:PORT` or the host IP, which is fragile, insecure, and goes out and back through NAT. ICC gives a clean internal path and lets you restrict who can talk to whom.

## 🔴 यह क्यों बना? (Hindi)
असली apps कई containers होते हैं: Nginx, API, worker, Redis, DB। इन्हें भरोसेमंद ढंग से, private रूप से और बिना सब कुछ internet पर खोले बात करनी होती है। Beginners हर port publish करके `localhost:PORT` या host IP से connect करते हैं, जो नाज़ुक, असुरक्षित है और NAT से घूमकर जाता है। ICC साफ internal रास्ता देता है और यह सीमित करने देता है कि कौन किससे बात करे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Put containers on the SAME user-defined network (Compose does it for you)
Step 2 → Caller uses service name:  http://api:3000  (Docker DNS -> container IP)
Step 3 → Traffic goes container -> bridge -> container (never leaves the host)
Step 4 → Use the container's INTERNAL port (3000), not any published host port
Step 5 → Containers on different networks cannot reach each other (isolation)
Step 6 → Wait for readiness: healthcheck + depends_on condition, plus app retries
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Containers को **एक ही** user-defined network पर रखो (Compose यह खुद करता है)।
Step 2 → Caller service name इस्तेमाल करता है: `http://api:3000` (Docker DNS -> container IP)।
Step 3 → Traffic container -> bridge -> container जाता है (host से बाहर नहीं निकलता)।
Step 4 → Container का **internal port** (3000) इस्तेमाल करो, host का published port नहीं।
Step 5 → अलग networks के containers एक-दूसरे तक नहीं पहुँच सकते (isolation)।
Step 6 → Readiness का ध्यान रखो: healthcheck + `depends_on` condition + app में retry।

---

## 🟡 Real World Example
A Zomato-like order flow on one VPS: React (served by Nginx) -> `/api` -> Node.js order service -> `http://pricing:8000` (FastAPI) -> Redis cache and PostgreSQL. The order service calls pricing by name. Pricing lives only on the `backend` network; the DB lives on `data` network which only the services (not Nginx) join. If Nginx is hacked, it still has no route to the DB.

## 🟡 Real Example Hindi mein
एक VPS पर Zomato जैसा order flow: React (Nginx से serve) -> `/api` -> Node.js order service -> `http://pricing:8000` (FastAPI) -> Redis cache और PostgreSQL। Order service pricing को नाम से बुलाती है। Pricing सिर्फ `backend` network पर है; DB `data` network पर है जिसमें सिर्फ services हैं (Nginx नहीं)। अगर Nginx hack भी हो जाए तो DB तक रास्ता ही नहीं है।

---

## 💻 Code / Config Example — Basic
```yaml
# docker-compose.yml - simplest working ICC
services:
  api:
    build: ./api                          # Node.js API image
    environment:
      REDIS_URL: redis://cache:6379       # "cache" = service name of redis (internal port 6379)
    depends_on:
      - cache                             # start redis container first
  cache:
    image: redis:7-alpine                 # example tag
    # no "ports:" => not reachable from outside, only from containers on same network
```

```bash
# Test it from inside the api container
docker compose up -d                                  # start both services
docker compose exec api sh -c "nc -zv cache 6379"     # port check by NAME (needs nc in image)
docker compose exec cache redis-cli ping              # expect PONG
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - segmented networks + readiness + least privilege
services:
  nginx:
    image: nginx:1.27-alpine              # example tag
    ports:
      - "80:80"                           # only public entry
    networks:
      - frontend                          # can see only api
    depends_on:
      api:
        condition: service_healthy        # wait until api healthcheck passes
  api:
    build: ./api                          # Node.js
    networks:
      - frontend                          # reachable by nginx
      - data                              # can reach db and cache
    environment:
      PRICING_URL: http://pricing:8000    # call FastAPI by service name
      DATABASE_URL: postgres://app:${DB_PASSWORD}@db:5432/app
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"] # needs wget in image
      interval: 10s                       # probe every 10 s
      timeout: 3s                         # 3 s max per probe
      retries: 5                          # 5 failures => unhealthy
      start_period: 20s                   # grace time for slow start
    depends_on:
      db:
        condition: service_healthy        # wait for DB readiness, not only start
  pricing:
    build: ./pricing                      # FastAPI image
    networks:
      - data                              # not on frontend: Nginx cannot call it
  db:
    image: postgres:16-alpine             # example tag
    environment:
      POSTGRES_USER: app                  # DB user
      POSTGRES_PASSWORD: ${DB_PASSWORD}   # from .env
      POSTGRES_DB: app                    # DB name
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"] # official readiness check
      interval: 5s                        # fast checks while booting
      timeout: 3s
      retries: 10
    networks:
      - data                              # only internal data network
  cache:
    image: redis:7-alpine                 # example tag
    networks:
      - data
networks:
  frontend: {}                            # nginx <-> api
  data:
    internal: true                        # no internet egress for data tier
```
Check: `docker compose config` validates the file on a machine with the compose plugin (not available here; YAML parse only). Remember Compose creates `<project>_<network>` names. `condition: service_healthy` needs Compose v2 (Compose Specification).

---

## 🟠 My Stack Integration
- **FastAPI <-> Node.js**: use `http://pricing:8000`; set client timeouts and retries (axios/httpx) because ICC does not guarantee the other side is ready.
- **Nginx -> Node**: `proxy_pass http://api:3000;` (see Container DNS note about stale IPs after recreation).
- **Docker Swarm/Kubernetes later**: the same idea becomes Service names and NetworkPolicies, so the habit transfers.
- **Security**: by default all containers on a network can reach all ports of each other. Use separate networks per tier, `internal: true` for data, and authenticate between services (DB passwords, service tokens, mTLS when needed). The legacy daemon flag `--icc=false` only affects the **default bridge**; on user-defined networks use separate networks.

```bash
# Quick matrix test: who can reach whom (run from each container)
docker compose exec nginx wget -qO- -T 2 http://api:3000/health    # should work
docker compose exec nginx nc -zv -w 2 db 5432                       # should FAIL (isolated)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Calling `http://localhost:3000` from the Nginx container.
✅ Correct: Use `http://api:3000`.

❌ Mistake 2: Using the **published** port (`http://api:8080` when mapped `8080:3000`).
✅ Correct: Container-to-container always uses the internal port `3000`.

❌ Mistake 3: `depends_on` alone, then the API crashes because DB is not ready.
✅ Correct: Healthcheck + `condition: service_healthy` and connection retry logic in the app.

❌ Mistake 4: Putting every service on one flat network.
✅ Correct: Segment: frontend, backend, data.

❌ Mistake 5: Passing secrets in plain URLs in compose files committed to Git.
✅ Correct: Use `.env` (gitignored), Docker secrets, or AWS Secrets Manager.

---

## 🧠 Tricky Interview Question
Containers A and B are in different Compose projects on the same host. A calls `http://b:3000` and fails. Both work in their own project. Fix it?

Answer: Each project has its own default network, so `b` does not resolve from A. Create an **external** shared network (`docker network create shared`) and attach both via `networks: shared: external: true`; then names resolve. Alternatively merge the projects. Note that with a shared network, **all** members see each other, so share only the services that must talk (use a dedicated network just for that pair).

---

## ⚫ Interview Questions + Answers

Q1: How do containers on the same host communicate?
A1: Over a Docker network (bridge) using Docker DNS names and internal ports.

Q2: Do you need `ports:` for container-to-container calls?
A2: No. `ports:` is for outside access; `expose:` is just documentation.

Q3: How to stop two containers from talking?
A3: Put them on different networks, or use an `internal` network plus firewall rules; do not rely on `--icc=false`.

Q4: `depends_on` guarantees the DB is ready?
A4: No, only start order. Use `condition: service_healthy` with a healthcheck, and retry in the app.

Q5: How would you share a network between two projects?
A5: Create the network once, mark it `external: true` in both compose files.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A multi-service app on one host (Compose on a VPS/EC2).
- You want private data tiers with a single public edge.

❌ Avoid when:
- Services run on different hosts (use overlay, Kubernetes, service discovery, or private VPC addresses with TLS).
- You need traffic policy and observability between services (service mesh).

---

## 📊 Visual Diagram
```
 Internet --:80--> [ nginx ]
                      |  frontend net
                      v
                   [ api :3000 ] ----http://pricing:8000----> [ pricing ]
                      |  data net (internal, no egress)           |
              +-------+--------+                                  |
              v                v                                  v
          [ db :5432 ]    [ cache :6379 ] <-----------------------+
  nginx has NO route to db/cache/pricing (different networks)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ICC | Container-to-container communication | Containers के बीच संचार |
| Service name | DNS name of a Compose service | Compose service का DNS नाम |
| Internal port | Port the app listens on inside | App जिस port पर अंदर सुनता है |
| internal network | Network without outside access | बाहरी पहुँच के बिना network |
| Healthcheck | Command that tests readiness | Readiness जाँचने वाला command |
| External network | Network created outside Compose | Compose के बाहर बना network |

---

## ⚡ 3-Line Summary
English: Containers talk over shared user-defined networks using service names and internal ports.
Segment networks by tier so only needed paths exist.
Use healthchecks and retries; `depends_on` alone does not mean ready.
Hindi: Containers साझा user-defined networks पर service name और internal port से बात करते हैं।
Tier के हिसाब से networks अलग करो ताकि सिर्फ ज़रूरी रास्ते रहें।
Healthcheck और retry लगाओ; सिर्फ `depends_on` का मतलब "ready" नहीं है।

---

## ➡️ Next Topic
**149. Container Security** - network segmentation is one layer; next the full container hardening checklist.
