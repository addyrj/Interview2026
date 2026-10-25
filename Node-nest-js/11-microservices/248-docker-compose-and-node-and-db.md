# 248. Docker Compose + Node + DB
# हिंदी में: Docker Compose + Node + DB

---

## 🔵 Simple Definition (English)
Docker Compose lets you define and run a multi-container application (e.g., a Node.js API + a PostgreSQL database + Redis) using a single YAML file. Instead of manually starting each container with separate `docker run` commands and wiring up networking, `docker-compose up` starts everything together, pre-configured to talk to each other.

## 🔵 सरल परिभाषा (Hindi)
Docker Compose एक multi-container application (जैसे Node.js API + PostgreSQL database + Redis) को define और run करने देता है एक single YAML file use करके। हर container को अलग `docker run` commands से manually start करने और networking wire up करने के बजाय, `docker-compose up` सब कुछ एक साथ start करता है, एक-दूसरे से बात करने के लिए pre-configured।

---

## 🔴 Problem it Solves
A real Node.js app rarely runs alone — it typically needs a database, a cache, maybe a message queue, running alongside it. Setting these up manually (installing Postgres locally, configuring Redis, managing versions) is tedious, inconsistent across team members' machines, and doesn't match production topology. Docker Compose solves this by describing the ENTIRE local development stack (app + all its dependencies) as code in one file, so any developer can run `docker-compose up` and get an identical, fully-wired environment in one command — no manual installation of dependent services required.

## 🔴 यह क्यों बना? (Hindi)
एक real Node.js app शायद ही कभी अकेला चलता है — इसे typically एक database, एक cache, शायद एक message queue चाहिए साथ में चलने के लिए। इन्हें manually setup करना (locally Postgres install करना, Redis configure करना, versions manage करना) tedious है, team members की machines में inconsistent है, और production topology से match नहीं करता। Docker Compose पूरे local development stack (app + उसकी सभी dependencies) को एक file में code के रूप में describe करके यह solve करता है, ताकि कोई भी developer `docker-compose up` run करके एक identical, fully-wired environment एक command में पा सके — dependent services की कोई manual installation जरूरी नहीं।

---

## 🟢 How it Works — Step by Step

Step 1 → Define each component (Node.js app, database, cache) as a **service** in a `docker-compose.yml` file.
Step 2 → For the app's own code, specify `build: .` (build from the local Dockerfile); for third-party services (Postgres, Redis), specify a pre-built `image:` from Docker Hub.
Step 3 → Compose automatically creates a shared Docker network so services can reach each other by SERVICE NAME (e.g., the app connects to `postgres://db:5432`, not `localhost`).
Step 4 → Define environment variables, port mappings, and volumes (for persistent data like database files) per service.
Step 5 → Use `depends_on` to control startup ordering (though note: this only waits for the container to START, not for the service inside it to be READY — healthchecks handle true readiness).
Step 6 → Run `docker-compose up` to start everything together, and `docker-compose down` to tear it all down cleanly.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → हर component (Node.js app, database, cache) को एक `docker-compose.yml` file में एक **service** के रूप में define करो।
Step 2 → App के खुद के code के लिए, `build: .` specify करो (local Dockerfile से build); third-party services (Postgres, Redis) के लिए, Docker Hub से एक pre-built `image:` specify करो।
Step 3 → Compose automatically एक shared Docker network बनाता है ताकि services एक-दूसरे तक SERVICE NAME से पहुंच सकें (जैसे app `postgres://db:5432` से connect करता है, `localhost` से नहीं)।
Step 4 → हर service के लिए environment variables, port mappings, और volumes (persistent data जैसे database files के लिए) define करो।
Step 5 → Startup ordering control करने के लिए `depends_on` use करो (हालांकि note करो: यह सिर्फ container के START होने का wait करता है, service के अंदर READY होने का नहीं — true readiness healthchecks handle करते हैं)।
Step 6 → सब कुछ एक साथ start करने के लिए `docker-compose up` run करो, और सब कुछ cleanly tear down करने के लिए `docker-compose down`।

---

## 🟡 Real World Example
**A Paytm-style wallet service's local dev setup:** A new developer joining the team needs the Node.js wallet API, a PostgreSQL database for transaction records, and Redis for session caching — all running together and correctly networked. Instead of a multi-page setup wiki, the team provides a single `docker-compose.yml`; the developer runs `docker-compose up`, and within a minute has the full stack running locally, identical to how other teammates run it, with zero manual database installation or configuration.

## 🟡 Real Example Hindi mein
**एक Paytm-style wallet service का local dev setup:** Team में नए join हुए developer को Node.js wallet API, transaction records के लिए एक PostgreSQL database, और session caching के लिए Redis चाहिए — सब एक साथ चलते हुए और correctly networked। एक multi-page setup wiki के बजाय, team एक single `docker-compose.yml` provide करती है; developer `docker-compose up` run करता है, और एक मिनट के अंदर पूरा stack locally चल रहा होता है, exactly जैसे बाकी teammates चलाते हैं, बिना किसी manual database installation या configuration के।

---

## 💻 Code Example — Basic

```yaml
# docker-compose.yml — basic Node.js app + PostgreSQL database
version: '3.8'

services:
  app:
    build: .                      # build from the Dockerfile in this directory
    ports:
      - "3000:3000"                # map host:3000 → container:3000
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
      # NOTE: hostname is "db" (the service name below), NOT "localhost"!
    depends_on:
      - db                          # start db's container before starting app's

  db:
    image: postgres:16-alpine       # pre-built official Postgres image, no custom Dockerfile needed
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb
    ports:
      - "5432:5432"
```

```javascript
// server.js — connects to the database using the SERVICE NAME as hostname
const express = require('express');
const { Pool } = require('pg');

const app = express();
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
// Inside Docker Compose's network, "db" resolves to the postgres container's IP automatically

app.get('/db-check', async (req, res) => {
  const result = await pool.query('SELECT NOW()');
  res.json({ dbTime: result.rows[0].now });
});

app.listen(3000, () => console.log('App connected via Compose network on 3000'));

// Run:  docker-compose up
// Visit: http://localhost:3000/db-check
```

## 💻 Code Example — Advanced

```yaml
# docker-compose.yml — production-like multi-service setup with healthchecks, volumes, Redis
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/walletdb
      - REDIS_URL=redis://cache:6379
      - NODE_ENV=production
    depends_on:
      db:
        condition: service_healthy    # waits for DB's healthcheck to PASS, not just container start
      cache:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=walletdb
    volumes:
      - pgdata:/var/lib/postgresql/data   # named volume persists data across container restarts
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      timeout: 3s
      retries: 5

  cache:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  pgdata:   # declared named volume — survives `docker-compose down` (unless -v flag is used)
```

```javascript
// server.js — advanced app connecting to both Postgres and Redis via Compose service names
const express = require('express');
const { Pool } = require('pg');
const Redis = require('ioredis');

const app = express();
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const redis = new Redis(process.env.REDIS_URL);

app.get('/health', (req, res) => res.sendStatus(200));

app.get('/wallet/:userId', async (req, res) => {
  const cached = await redis.get(`wallet:${req.params.userId}`);
  if (cached) return res.json({ balance: cached, source: 'cache' });

  const result = await pool.query('SELECT balance FROM wallets WHERE user_id = $1', [req.params.userId]);
  const balance = result.rows[0]?.balance ?? 0;
  await redis.set(`wallet:${req.params.userId}`, balance, 'EX', 60);

  res.json({ balance, source: 'db' });
});

app.listen(3000, () => console.log('Wallet service running on 3000'));

// Run: docker-compose up --build
```

---

## 🟠 Express.js Integration

```yaml
# docker-compose.override.yml — local dev overrides (hot reload, exposed debug ports)
# Compose automatically merges this with docker-compose.yml during local development
version: '3.8'

services:
  app:
    volumes:
      - .:/app                      # mount local code into the container for live editing
      - /app/node_modules           # but DON'T override node_modules with the host's
    command: npm run dev             # use nodemon/ts-node-dev instead of the production CMD
    environment:
      - NODE_ENV=development
    ports:
      - "3000:3000"
      - "9229:9229"                  # expose Node.js debugger port for attaching a debugger
```

```javascript
// Express app unaffected by Compose — same code runs in dev (with hot reload mount)
// and production (built into the image without the volume mount) seamlessly.
const express = require('express');
const app = express();
app.get('/health', (req, res) => res.sendStatus(200));
app.listen(3000, () => console.log('Dev server with hot reload via Compose volume mount'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Connecting to the database using `localhost` instead of the Compose SERVICE NAME
✅ Correct: Use the service name as the hostname — Compose's internal DNS resolves it automatically

```yaml
# Wrong — "localhost" inside the app container refers to the APP container itself, not the DB container
environment:
  - DATABASE_URL=postgres://user:pass@localhost:5432/mydb

# Right — "db" is the DB service's name, resolvable via Compose's internal network
environment:
  - DATABASE_URL=postgres://user:pass@db:5432/mydb
```

❌ Mistake 2: Relying on `depends_on` alone to guarantee the dependency is actually READY (not just started)
✅ Correct: Use `depends_on` with `condition: service_healthy`, paired with a proper `healthcheck`

```yaml
# Wrong — app might start and try connecting before Postgres has finished initializing
depends_on:
  - db

# Right — waits for db's healthcheck to actually pass first
depends_on:
  db:
    condition: service_healthy
```

---

## 🧠 Tricky Interview Question

```yaml
services:
  app:
    build: .
    depends_on:
      - db
  db:
    image: postgres:16
```
```javascript
// App's startup code immediately runs: pool.query('SELECT 1') right when the process starts.
// Running `docker-compose up` sometimes causes the app to crash with a connection error.
// Why, given that depends_on IS configured?
```
Answer: `depends_on` (without a `condition: service_healthy`) only guarantees that the `db` CONTAINER has been STARTED before the `app` container starts — it does NOT wait for PostgreSQL's actual database process inside that container to finish initializing and start accepting connections (which can take a few seconds after container start). The app's immediate `SELECT 1` query can race ahead and hit the database before it's truly ready, causing a connection refused error. The fix is adding a proper `healthcheck` to the `db` service and using `depends_on: db: condition: service_healthy` so Compose actually waits for Postgres to report healthy before starting the app — or implementing connection retry logic in the app itself.

---

## ⚫ Interview Questions + Answers

Q1: How do services in a Docker Compose setup communicate with each other?
A1: Compose automatically creates a shared Docker network for all services defined in the same `docker-compose.yml`, and each service is reachable by its SERVICE NAME as a hostname (Compose's built-in DNS resolves it to the correct container's internal IP). So an `app` service connects to a `db` service using `db` as the hostname, not `localhost` or a specific IP address — this works consistently regardless of which machine runs the stack.

Q2: What's the difference between `depends_on` (plain) and `depends_on` with `condition: service_healthy`?
A2: Plain `depends_on` only controls STARTUP ORDER — it ensures the dependency's container is started before the dependent service's container starts, but does NOT wait for the actual application/service inside that container to be ready to accept connections. `depends_on` with `condition: service_healthy` additionally waits for that dependency's `healthcheck` to report "healthy" before starting the dependent service — giving a true readiness guarantee, assuming a correct healthcheck is defined.

Q3: Why use a named volume (like `pgdata`) for a database service in Docker Compose?
A3: Containers are ephemeral by design — if you remove/recreate the `db` container (e.g., during `docker-compose down && docker-compose up`), any data written to the container's own filesystem would normally be lost. A named volume persists data OUTSIDE the container's lifecycle, on the Docker host, so database data survives container recreation; without it, every `docker-compose down` would wipe your entire local database.

Q4: How would you set up a development environment with hot-reload using Docker Compose, while keeping production builds clean?
A4: Use a `docker-compose.override.yml` (automatically merged with the base `docker-compose.yml` by Compose) that mounts the local source code as a volume into the running container (`volumes: - .:/app`) and overrides the `command` to use a file-watching tool like `nodemon`. This lets code changes on the host be reflected immediately inside the running container without rebuilding the image, while the production Dockerfile/image (without these dev-only overrides) remains lean and doesn't include this volume-mount/hot-reload setup.

Q5: What are the main benefits of Docker Compose for local development compared to manually installing dependencies?
A5: Consistency across team members (everyone runs the exact same versions of Postgres/Redis/etc. defined in the YAML, no "works on my machine" due to version drift), fast onboarding (one command spins up the entire stack instead of a long manual setup guide), easy teardown/reset (`docker-compose down -v` wipes everything cleanly for a fresh start), and closer parity with how services are actually networked/configured in production-like multi-container environments.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Local development or testing requires multiple interdependent services (app + DB + cache + queue)
- You want consistent, reproducible environments across team members and CI
- You need a quick way to spin up/tear down a full stack for integration testing

❌ Avoid when:
- Deploying to production at scale — Compose is primarily a local/single-host development tool; production orchestration typically uses Kubernetes or managed cloud services instead
- The app has no external dependencies at all (a single container with `docker run` is simpler)

---

## 📊 Visual Diagram
```
docker-compose.yml
┌─────────────────────────────────────────────┐
│              Compose-managed network           │
│                                                   │
│   ┌───────────┐   ┌───────────┐   ┌───────────┐ │
│   │   app      │──▶│    db      │   │   cache    │ │
│   │ (Node.js)  │   │ (Postgres) │   │  (Redis)   │ │
│   └───────────┘   └───────────┘   └───────────┘ │
│   connects via        named volume: pgdata        │
│   service names:       (persists DB data)         │
│   "db", "cache"                                    │
└─────────────────────────────────────────────┘
          │
  docker-compose up  → starts everything together
  docker-compose down → stops/removes containers (data persists via volume)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Service | A container definition in docker-compose.yml | docker-compose.yml में एक container definition |
| Compose network | Shared network letting services reach each other by name | Services को नाम से एक-दूसरे तक पहुंचाने वाला shared network |
| depends_on | Controls startup order between services | Services के बीच startup order control करना |
| Healthcheck | Defines how Compose checks if a service is ready | Compose service ready है या नहीं कैसे check करे |
| Named volume | Persistent storage outside container lifecycle | Container lifecycle के बाहर persistent storage |

---

## ⚡ 3-Line Summary
**English:**
1. Docker Compose defines a multi-container app (Node.js + DB + cache) in one YAML file, networked automatically by service name.
2. `depends_on` alone only waits for container start, not true readiness — pair it with healthchecks for reliable startup order.
3. Named volumes persist database data across container recreation, and override files enable dev-specific setups like hot reload.

**Hindi:**
1. Docker Compose एक multi-container app (Node.js + DB + cache) को एक YAML file में define करता है, service name से automatically networked।
2. `depends_on` अकेला सिर्फ container start का wait करता है, true readiness का नहीं — reliable startup order के लिए इसे healthchecks के साथ pair करो।
3. Named volumes database data को container recreation के across persist करते हैं, और override files dev-specific setups जैसे hot reload enable करती हैं।

---

## ➡️ Next Topic
**249. Kubernetes Basics for Node.js** — Orchestrating containerized Node.js services at production scale beyond a single host.
