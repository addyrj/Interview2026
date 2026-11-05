# 181. Docker Compose — Complete Guide
# हिंदी में: Docker Compose — पूरी गाइड

---

## 🔵 Simple Definition (English)
**Docker Compose** is a tool to define and run multi-container applications using one YAML file (`compose.yaml` or `docker-compose.yml`). With one command (`docker compose up`) it creates the networks, volumes and containers for your whole stack: API, database, cache, Nginx.

## 🔵 सरल परिभाषा (Hindi)
**Docker Compose** एक tool है जो एक YAML file (`compose.yaml` या `docker-compose.yml`) से multi-container application define और run करता है। एक command (`docker compose up`) से पूरे stack के networks, volumes और containers बन जाते हैं: API, database, cache, Nginx।

---

## 🔴 Problem it Solves
Starting a real app with plain `docker run` means five long commands with networks, volumes, env vars and ports, copied from a wiki and easy to get wrong. New teammates spend a day setting up. Compose turns that into a versioned, reviewable file: "infrastructure as code" for a single host.

## 🔴 यह क्यों बना? (Hindi)
Plain `docker run` से असली app चलाने का मतलब है पाँच लंबे commands, जिनमें networks, volumes, env vars और ports हों, wiki से copy किए हुए और गलत होने में आसान। नए teammate का पूरा दिन setup में जाता है। Compose इसे versioned, review होने वाली file बना देता है: एक host के लिए "infrastructure as code"।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write compose.yaml: services, networks, volumes, env
Step 2 → docker compose up -d reads the file (+ .env for ${VARIABLES})
Step 3 → Compose creates a project network (<project>_default) and named volumes
Step 4 → It pulls or builds images for each service
Step 5 → It starts containers in dependency order (depends_on)
Step 6 → Containers reach each other by service name (Docker DNS)
Step 7 → docker compose ps/logs/exec manage the stack; down removes it
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → तुम compose.yaml लिखते हो: services, networks, volumes, env
Step 2 → docker compose up -d file पढ़ता है (+ ${VARIABLES} के लिए .env)
Step 3 → Compose project network (<project>_default) और named volumes बनाता है
Step 4 → हर service की image pull या build करता है
Step 5 → containers को dependency क्रम (depends_on) में चालू करता है
Step 6 → Containers एक-दूसरे को service नाम से पहुँचते हैं (Docker DNS)
Step 7 → docker compose ps/logs/exec से stack manage होता है; down उसे हटाता है
```

---

## 🟡 Real World Example
A small team builds a Zomato-like ordering app: React frontend, Node.js API, MongoDB, Redis, Nginx. Each developer runs `git clone && cp .env.example .env && docker compose up -d` and gets the same stack in 3 minutes. The same file, with a `compose.prod.yaml` override, deploys to the team's single VPS via GitHub Actions over SSH.

## 🟡 Real Example Hindi mein
एक छोटी team Zomato जैसा ordering app बनाती है: React frontend, Node.js API, MongoDB, Redis, Nginx। हर developer `git clone && cp .env.example .env && docker compose up -d` चलाता है और 3 मिनट में वही stack पा लेता है। वही file, `compose.prod.yaml` override के साथ, GitHub Actions से SSH के ज़रिए team के single VPS पर deploy होती है।

---

## 💻 Code / Config Example — Basic
```yaml
# compose.yaml - smallest useful stack: Node API + MongoDB
services:
  api:                                  # service name = DNS hostname
    build: ./api                        # build image from ./api/Dockerfile
    ports:
      - "3000:3000"                     # host:container
    environment:
      MONGO_URL: mongodb://mongo:27017/app   # "mongo" = service name below
    depends_on:
      - mongo                           # start mongo before api
  mongo:
    image: mongo:7                      # example tag; pin and update deliberately
    volumes:
      - mongo_data:/data/db             # persist database files
volumes:
  mongo_data: {}                        # declare named volume
```

```bash
docker compose up -d            # create + start everything in background
docker compose ps               # list services and their state
docker compose logs -f api      # follow api logs
docker compose exec api sh      # open a shell in the api container
docker compose down             # stop and remove containers + network (volumes kept)
```

## 💻 Code / Config Example — Advanced
```yaml
# compose.yaml - production-minded stack for a single VPS
name: shop                                    # project name (prefix for networks/volumes)

services:
  nginx:
    image: nginx:1.27-alpine                  # example tag
    ports:
      - "80:80"                               # public HTTP
      - "443:443"                             # public HTTPS
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro   # config, read-only
      - ./certs:/etc/nginx/certs:ro           # TLS certificates, read-only
    depends_on:
      api:
        condition: service_healthy            # wait until api reports healthy
    networks: [edge]
    restart: unless-stopped                   # auto-restart except manual stop

  api:
    build:
      context: ./api                          # build context folder
      target: production                      # multi-stage target in Dockerfile
    image: myorg/shop-api:1.4.2               # tag the built image
    env_file: .env                            # secrets/config from file (not committed)
    environment:
      NODE_ENV: production                    # production mode
      MONGO_URL: mongodb://mongo:27017/shop   # service-name URL
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]  # alpine busybox wget
      interval: 10s                           # probe frequency
      timeout: 3s                             # max time per probe
      retries: 5                              # failures before unhealthy
      start_period: 15s                       # grace time on boot
    depends_on:
      mongo:
        condition: service_healthy            # db must be ready
    networks: [edge, backend]                 # bridges both zones
    deploy:
      resources:
        limits:
          cpus: "1.0"                         # max one CPU
          memory: 512M                        # max 512 MB RAM
    restart: unless-stopped

  mongo:
    image: mongo:7
    volumes:
      - mongo_data:/data/db                   # persistent data
    healthcheck:
      test: ["CMD", "mongosh", "--quiet", "--eval", "db.adminCommand('ping').ok"]  # ping the server
      interval: 10s
      timeout: 5s
      retries: 5
    networks: [backend]                       # private
    restart: unless-stopped

networks:
  edge: {}                                    # public zone
  backend:
    internal: true                            # no internet for db tier
volumes:
  mongo_data: {}                              # named volume
```

---

## 🟠 My Stack Integration
- **React:** multi-stage Dockerfile builds static files into an Nginx image; Compose exposes only Nginx.
- **Node.js / FastAPI:** each gets a `build:` context; talk to DB by service name.
- **Nginx:** one service as reverse proxy and TLS terminator; `proxy_pass http://api:3000`.
- **VPS:** `ssh vps "cd /srv/shop && docker compose pull && docker compose up -d"` is a complete deploy for small apps.
- **AWS:** Compose also deploys to ECS (`docker context` + ECS integration was deprecated; prefer ECS task definitions or Copilot). For EC2 single-host, Compose is fine.
- **Config files:** keep `compose.yaml` (base), `compose.override.yaml` (dev, auto-loaded), `compose.prod.yaml` (production, explicit `-f`).

```bash
# deploy on the VPS (run in the project folder)
docker compose -f compose.yaml -f compose.prod.yaml pull      # fetch new images
docker compose -f compose.yaml -f compose.prod.yaml up -d     # recreate only changed services
docker image prune -f                                          # clean old image layers
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing `.env` with passwords.
✅ Correct: Commit `.env.example`, add `.env` to `.gitignore`, use secrets in production.

❌ Mistake 2: Using `latest` tags in production.
✅ Correct: Pin versions for repeatable deploys.

❌ Mistake 3: Using old `docker-compose` (v1, Python) and `version: "3"` mindset.
✅ Correct: Use `docker compose` (v2 plugin); the `version:` field is obsolete.

❌ Mistake 4: `docker compose down -v` on production.
✅ Correct: `-v` deletes named volumes (your data). Use plain `down` or `stop`.

❌ Mistake 5: Treating Compose as an orchestrator for many hosts.
✅ Correct: It is single-host. Use Swarm/Kubernetes/ECS for clusters.

---

## 🧠 Tricky Interview Question
**Q:** You changed an environment variable in `compose.yaml` and ran `docker compose restart api`. The app still shows the old value. Why?

**Answer:** `restart` only restarts the existing container with its original configuration. Environment, ports and image changes need the container to be recreated: `docker compose up -d` (Compose detects the config change and recreates the service) or `up -d --force-recreate api`. Note that changes in an `env_file` are also applied only at container creation.

---

## ⚫ Interview Questions + Answers

Q1: What is Docker Compose used for?
A1: Defining and running multi-container apps on a single host from one YAML file.

Q2: Compose v1 vs v2?
A2: v1 was the Python `docker-compose` binary; v2 is the Go `docker compose` plugin. v1 reached end of life; use v2.

Q3: What does `docker compose down` remove?
A3: Containers and networks (and volumes only with `-v`, images only with `--rmi`).

Q4: Difference between `up`, `start` and `run`?
A4: `up` creates and starts services; `start` starts existing stopped containers; `run` starts a one-off container for a service.

Q5: How are multiple compose files combined?
A5: `-f a.yaml -f b.yaml`; later files override or extend earlier ones. `compose.override.yaml` is auto-merged.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Local development environments
- Single-VPS production for small and medium apps
- CI integration tests with real databases

❌ Avoid when:
- You need multi-node scheduling, auto-scaling or self-healing across hosts
- Zero-downtime rolling deploys with traffic shifting (needs more tooling)

---

## 📊 Visual Diagram
```
 compose.yaml  +  .env
        |
        v   docker compose up -d
 +----------------------- project "shop" -----------------------+
 |  network edge        network backend (internal)              |
 |  [nginx]--->[api]------------>[mongo]                         |
 |    :80/:443   |                  |                            |
 |               +---> healthcheck  +--> volume mongo_data       |
 +--------------------------------------------------------------+
 down -> removes containers+networks | down -v -> also volumes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Service | One container definition in Compose | एक container की परिभाषा |
| Project | A named group of services | services का समूह |
| compose.yaml | Compose definition file | Compose की file |
| Override file | Extra file merged on top | ऊपर से जुड़ने वाली file |
| Healthcheck | Test that app is ready | app तैयार है या नहीं की जाँच |
| Recreate | Replace container with new config | नए config से नया container |

---

## ⚡ 3-Line Summary
English: Compose defines a whole multi-container stack in one YAML file and runs it with one command.
Use v2 (`docker compose`), pin images, keep secrets out of git.
It is great for dev and single-VPS production, not for clusters.
Hindi: Compose पूरे multi-container stack को एक YAML में define करके एक command से चलाता है।
v2 (`docker compose`) use करो, images pin करो, secrets git में मत डालो।
Dev और single-VPS production के लिए बढ़िया, clusters के लिए नहीं।

---

## ➡️ Next Topic
**182. docker-compose.yml Structure** - a line-by-line look at the top-level keys and how the file is organised.
