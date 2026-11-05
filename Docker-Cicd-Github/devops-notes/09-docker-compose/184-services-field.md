# 184. services Field
# हिंदी में: Compose का `services` Field

---

## 🔵 Simple Definition (English)
`services:` is the main top-level key in a Compose file. Each child under it (like `api`, `db`, `nginx`) describes one container configuration: its image or build, ports, environment, volumes, networks and so on. Compose creates one or more containers for each service.

## 🔵 सरल परिभाषा (Hindi)
`services:` Compose file की सबसे ज़रूरी top-level key है। इसके नीचे हर child (जैसे `api`, `db`, `nginx`) एक container की configuration बताता है: image या build, ports, environment, volumes, networks आदि। Compose हर service के लिए एक या ज़्यादा containers बनाता है।

---

## 🔴 Problem it Solves
Without Compose you start each container with a long `docker run` command: `docker run -d --name api --network app -e ... -p ... -v ... image`. For 4 containers this is 4 long commands, easy to mistype, impossible to review in Git, and the start order lives only in someone's head. `services:` turns every `docker run` into declarative YAML that is version controlled and reproducible.

## 🔴 यह क्यों बना? (Hindi)
Compose के बिना हर container के लिए लंबा `docker run -d --name api --network app -e ... -p ... -v ... image` चलाना पड़ता है। 4 containers के लिए 4 लंबे commands, गलती की संभावना, Git में review नहीं, और start order सिर्फ किसी के दिमाग में। `services:` हर `docker run` को declarative YAML में बदल देता है जो Git में रहता है और हर बार वही result देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Compose parses the file and reads every key under `services:`.
Step 2 → Service name becomes DNS name on the project network (http://api:3000).
Step 3 → For each service: pull `image` or build from `build:`.
Step 4 → Compose creates a default network + named volumes if missing.
Step 5 → Containers are created as <project>-<service>-<index> (shop-api-1).
Step 6 → Order follows depends_on; containers start, healthchecks run.
Step 7 → `docker compose ps` shows each service with its state.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Compose file parse करके `services:` के नीचे की हर key पढ़ता है।
Step 2 → Service का नाम project network पर DNS नाम बन जाता है (http://api:3000)।
Step 3 → हर service के लिए `image` pull होती है या `build:` से build होती है।
Step 4 → Default network और named volumes न हों तो बनाए जाते हैं।
Step 5 → Containers <project>-<service>-<index> नाम से बनते हैं (shop-api-1)।
Step 6 → depends_on के हिसाब से start order चलता है, healthchecks चलते हैं।
Step 7 → `docker compose ps` हर service की state दिखाता है।
```

---

## 🟡 Real World Example
An e-commerce side project on a 2 vCPU VPS runs `web` (React behind nginx), `api` (Node.js), `worker` (BullMQ consumer using the same image as api but a different command), `db` (PostgreSQL) and `redis`. Using `services:`, the `api` and `worker` share one image but have different `command:`; scaling the worker is just `docker compose up -d --scale worker=3`. New teammates run one command to get the entire stack.

## 🟡 Real Example Hindi mein
2 vCPU VPS पर चलता e-commerce side project: `web` (nginx के पीछे React), `api` (Node.js), `worker` (BullMQ consumer, api वाली ही image पर अलग `command:`), `db` (PostgreSQL) और `redis`। `services:` में api और worker एक image share करते हैं पर `command:` अलग है; worker scale करना बस `docker compose up -d --scale worker=3` है। नया teammate एक command से पूरा stack चला लेता है।

---

## 💻 Code / Config Example — Basic

```yaml
services:                        # top-level key: all containers live here
  api:                           # service name = DNS hostname "api"
    image: node:20-alpine        # example image tag, update to your LTS
    working_dir: /app            # set working directory inside container
    command: node server.js      # command to run (overrides image CMD)
    volumes:                     # bind mount source code (dev only)
      - ./api:/app               # host ./api -> container /app
    ports:                       # publish to host
      - "3000:3000"              # host:container
  db:                            # second service: database
    image: postgres:16-alpine    # example tag
    environment:                 # postgres initial settings
      POSTGRES_PASSWORD: example # DEV ONLY, use secrets in production
```

## 💻 Code / Config Example — Advanced

```yaml
name: shop                       # project name
services:                        # all services
  api:                           # Node.js API
    build:                       # build from local Dockerfile
      context: ./api             # build context folder
    image: shop/api:2.1.0        # tag for built image
    command: ["node", "dist/server.js"]   # exec form, no shell, proper signals
    init: true                   # tiny init process reaps zombies, forwards signals
    restart: unless-stopped      # restart policy
    user: "1000:1000"            # run as non-root user
    read_only: true              # root filesystem read-only (security)
    tmpfs:                       # writable in-memory dir for temp files
      - /tmp                     # /tmp is allowed to be written
    cap_drop:                    # remove all Linux capabilities
      - ALL                      # least privilege
    security_opt:                # extra hardening
      - no-new-privileges:true   # prevent privilege escalation
    environment:                 # runtime config
      NODE_ENV: production       # production mode
      DATABASE_URL: postgres://app:${DB_PASSWORD:?set DB_PASSWORD}@db:5432/shop  # fails fast if missing
    depends_on:                  # wait for dependencies
      db:                        # database service
        condition: service_healthy   # until pg_isready passes
    networks: [backend]          # private network only
  worker:                        # background jobs
    image: shop/api:2.1.0        # same image as api
    command: ["node", "dist/worker.js"]   # different entrypoint
    restart: unless-stopped      # restart policy
    networks: [backend]          # private network only
    depends_on: [db]             # short syntax: just start order
  db:                            # PostgreSQL
    image: postgres:16-alpine    # example tag
    restart: unless-stopped      # restart policy
    environment:                 # DB config
      POSTGRES_USER: app         # database user
      POSTGRES_PASSWORD: ${DB_PASSWORD:?set DB_PASSWORD}   # from .env or shell
      POSTGRES_DB: shop          # initial database
    volumes:                     # persist data
      - pgdata:/var/lib/postgresql/data   # named volume
    healthcheck:                 # used by depends_on condition
      test: ["CMD-SHELL", "pg_isready -U app -d shop"]   # ready check
      interval: 10s              # every 10s
      timeout: 5s                # per check
      retries: 5                 # then unhealthy
    networks: [backend]          # private network only
volumes:                         # top-level named volumes
  pgdata: {}                     # managed by Docker
networks:                        # top-level networks
  backend: {}                    # default bridge driver
```

---

## 🟠 My Stack Integration
Map each part of your stack to one service: `nginx` (public, 80/443), `react` (static files), `api` (Node.js or FastAPI, not published), `db`, `redis`. Only nginx publishes ports; the others are reached via service names.

```yaml
services:                        # your VPS stack
  nginx:                         # reverse proxy
    image: nginx:1.27-alpine     # example tag
    ports: ["80:80", "443:443"]  # only public entry
    volumes:                     # config mounted read-only
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro   # proxy_pass http://api:8000
    depends_on: [api]            # start after api
  api:                           # FastAPI service
    image: ghcr.io/addyrj/fastapi-app:1.4.2   # example image
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]  # bind all interfaces
    env_file: [.env]             # secrets from file on the server
    restart: unless-stopped      # restart policy
  redis:                         # cache / queue
    image: redis:7-alpine        # example tag
    command: ["redis-server", "--requirepass", "${REDIS_PASSWORD:?required}"]  # password required
    restart: unless-stopped      # restart policy
```

Security: do not publish `db` or `redis` to the internet. Add resource limits and run as non-root where the image allows.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `localhost` to reach another service (`DATABASE_URL=...@localhost:5432`).
✅ Correct: Use the service name (`@db:5432`). localhost is the container itself.

❌ Mistake 2: Using underscores/uppercase in service names (hostname issues in some libraries).
✅ Correct: Use lowercase with hyphens, e.g. `api`, `redis-cache`.

❌ Mistake 3: Setting `container_name:` on every service, then failing to scale.
✅ Correct: Remove `container_name`; scaling needs unique names.

❌ Mistake 4: Putting both `image` and no `build` and expecting a local build.
✅ Correct: Add `build:` if the image must be built from source.

---

## 🧠 Tricky Interview Question
"`docker compose up --scale api=3` fails with a port already allocated error. Why, and how do you fix it?"

Answer: The service publishes a fixed host port (`"3000:3000"`). Three replicas cannot all bind host port 3000. Fix: do not publish the api port; put nginx (or Traefik) in front, and let it reach `api` by service DNS, which round-robins across replicas. Or publish a range (`"3000-3002:3000"`). Also remove any `container_name`.

---

## ⚫ Interview Questions + Answers

Q1: What does a service name do besides naming?
A1: It becomes a DNS alias on the Compose networks, so other containers connect via `http://servicename:port`.

Q2: Service vs container?
A2: Service is the definition (template); containers are running instances of it. One service can have many containers via `--scale`.

Q3: How do two services share an image but run different processes?
A3: Same `image:` with different `command:` (api and worker).

Q4: What is the minimum a service needs?
A4: Either `image` or `build` (or both).

Q5: How do you run only some services?
A5: `docker compose up -d api db`; dependencies start automatically. Or use `profiles`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running multi-container apps on one host (laptop, CI, single VPS).
- You want one reviewed YAML as the source of truth.

❌ Avoid when:
- You need multi-node scheduling, rolling updates, auto-healing across hosts (use Kubernetes / ECS).
- Zero-downtime deployments are strict (Compose recreates containers).

---

## 📊 Visual Diagram
```
 docker-compose.yml
 +----------------------------------------------+
 | services:                                    |
 |   nginx ----> api ----> db                   |
 |     |          |         |                   |
 +-----|----------|---------|-------------------+
       v          v         v
  [nginx-1]   [api-1,2,3]  [db-1]   <- containers
       \__________|_________/
           project network "shop_default"
         (DNS: nginx, api, db resolve to IPs)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| service | Definition of a container type | container का template/definition |
| replica | One running container of a service | service का एक चलता container |
| service name | DNS hostname on the network | network पर DNS नाम |
| command | Overrides image CMD | image का CMD बदलता है |
| scale | Run N containers of a service | N containers चलाना |

---

## ⚡ 3-Line Summary
English: `services:` declares each container of your app as YAML.
English: Service names are DNS names, so containers talk by name, not IP.
English: Same image can power many services; use `--scale` for replicas.
Hindi: `services:` आपके app के हर container को YAML में declare करता है।
Hindi: Service का नाम DNS नाम है, इसलिए containers IP नहीं, नाम से बात करते हैं।
Hindi: एक image कई services चला सकती है; replicas के लिए `--scale` use करें।

---

## ➡️ Next Topic
185. networks Field - services need to talk to each other safely; the `networks:` key controls who can reach whom.
