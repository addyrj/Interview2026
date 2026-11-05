# 191. depends_on
# हिंदी में: depends_on (निर्भरता और start क्रम)

---

## 🔵 Simple Definition (English)
`depends_on` tells Compose which services must start before another one. In its short form it only controls **start order**. In its long form it can wait for a dependency to be `service_started`, `service_healthy` (healthcheck passes) or `service_completed_successfully` (one-shot job finished).

## 🔵 सरल परिभाषा (Hindi)
`depends_on` Compose को बताता है कि कौन सी services पहले चालू होनी चाहिए। Short form में यह सिर्फ **start order** तय करता है। Long form में यह dependency के `service_started`, `service_healthy` (healthcheck पास) या `service_completed_successfully` (one-shot job पूरा) होने तक रुक सकता है।

---

## 🔴 Problem it Solves
Without ordering, the API may start before the database exists and crash with "connection refused". But "container started" is not "database ready": Postgres needs seconds to initialise. Short `depends_on` fixes order only, which is why long-form conditions with healthchecks were added to remove the race condition.

## 🔴 यह क्यों बना? (Hindi)
Order के बिना API database से पहले चालू हो सकता है और "connection refused" से crash हो सकता है। लेकिन "container चालू" का मतलब "database तैयार" नहीं: Postgres को initialise होने में सेकंड लगते हैं। Short `depends_on` सिर्फ order ठीक करता है, इसीलिए healthcheck वाली long-form conditions आईं ताकि race condition हटे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Compose builds a dependency graph from depends_on entries
Step 2 → `up` starts services in topological order (db before api)
Step 3 → Short form: waits only until the dependency container is STARTED
Step 4 → Long form + service_healthy: waits until the dependency's healthcheck is "healthy"
Step 5 → service_completed_successfully: waits until a one-shot (e.g. migration) exits with code 0
Step 6 → If a dependency never becomes healthy, `up` fails with "dependency failed to start"
Step 7 → `down` stops in reverse order (api first, then db)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Compose depends_on entries से dependency graph बनाता है
Step 2 → `up` services को topological क्रम में चालू करता है (api से पहले db)
Step 3 → Short form: dependency container के STARTED होने तक ही रुकता है
Step 4 → Long form + service_healthy: dependency की healthcheck "healthy" होने तक रुकता है
Step 5 → service_completed_successfully: one-shot (जैसे migration) exit code 0 से खत्म होने तक रुकता है
Step 6 → Dependency कभी healthy न हो तो `up` "dependency failed to start" से fail होता है
Step 7 → `down` उल्टे क्रम में रोकता है (पहले api, फिर db)
```

---

## 🟡 Real World Example
A Node.js shop API needs Postgres and must run Prisma migrations before serving. With plain `depends_on: [db]`, 1 in 5 deploys failed because Postgres was still replaying WAL. The team added `pg_isready` healthcheck, `migrate` as a one-shot service, and `depends_on` conditions: `api` waits for `migrate: service_completed_successfully`, which itself waits for `db: service_healthy`. Deploy failures dropped to zero.

## 🟡 Real Example Hindi mein
एक Node.js shop API को Postgres चाहिए और serve करने से पहले Prisma migrations चलानी हैं। सिर्फ `depends_on: [db]` से हर 5 में से 1 deploy fail होता था क्योंकि Postgres अभी WAL replay कर रहा था। टीम ने `pg_isready` healthcheck, one-shot `migrate` service और `depends_on` conditions जोड़ीं: `api` `migrate: service_completed_successfully` का इंतज़ार करता है, जो खुद `db: service_healthy` का इंतज़ार करता है। Deploy failures शून्य हो गए।

---

## 💻 Code / Config Example — Basic
```yaml
# compose.yaml - short form: ORDER ONLY (no readiness guarantee)
services:
  api:
    image: myorg/api:1.4.2          # example image
    depends_on:
      - db                          # start db container first; does NOT wait for db to be ready
      - cache                       # same for redis
  db:
    image: postgres:16-alpine       # example tag
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}   # from .env
  cache:
    image: redis:7-alpine           # example tag
```

## 💻 Code / Config Example — Advanced
```yaml
# compose.yaml - long form with conditions: no race conditions
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app              # database user
      POSTGRES_PASSWORD: ${DB_PASSWORD}   # password from .env
      POSTGRES_DB: app                # database name
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]   # returns 0 when accepting connections
      interval: 5s                    # check every 5 seconds
      timeout: 3s                     # each check may take 3 seconds
      retries: 10                     # unhealthy after 10 failures
      start_period: 10s               # ignore failures during first 10s
    volumes:
      - pgdata:/var/lib/postgresql/data   # persist data

  cache:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]  # expects PONG
      interval: 5s
      timeout: 3s
      retries: 10

  migrate:                            # one-shot job: apply DB migrations then exit
    image: myorg/api:1.4.2            # same image as api
    command: ["npx", "prisma", "migrate", "deploy"]   # example migration command
    environment:
      DATABASE_URL: postgres://app:${DB_PASSWORD}@db:5432/app
    depends_on:
      db:
        condition: service_healthy    # wait until Postgres is accepting connections
    restart: "no"                     # a job must not restart forever

  api:
    image: myorg/api:1.4.2
    environment:
      DATABASE_URL: postgres://app:${DB_PASSWORD}@db:5432/app
      REDIS_URL: redis://cache:6379
    depends_on:
      db:
        condition: service_healthy                 # db ready
      cache:
        condition: service_healthy                 # redis ready
      migrate:
        condition: service_completed_successfully  # migrations finished with exit code 0
        restart: true                              # restart api if migrate is restarted (Compose 2.17+)
    ports:
      - "127.0.0.1:3000:3000"         # loopback only

volumes:
  pgdata: {}
```

---

## 🟠 My Stack Integration
- **Node.js + Mongo/Postgres:** healthcheck on DB, condition `service_healthy`; also keep a retry loop in the app (Mongoose/SQLAlchemy retry) because DBs can restart later.
- **FastAPI + Alembic:** `migrate` service runs `alembic upgrade head`, then API starts.
- **Nginx:** `depends_on: api: condition: service_healthy` avoids 502 during boot.
- **React:** static build, usually no dependency.
- **VPS/AWS:** after reboot with `restart: unless-stopped`, Docker starts containers, but `depends_on` ordering is only enforced by Compose at `up`; apps must tolerate dependencies arriving late.
- **Required syntax check:** conditions need Compose Specification (v2 plugin); old `docker-compose` v1 with file format 3 did not support them.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Believing short `depends_on` waits for readiness.
✅ Correct: Use `condition: service_healthy` with a real healthcheck.

❌ Mistake 2: Declaring `service_healthy` but the dependency has no `healthcheck`.
✅ Correct: Compose errors out; define a healthcheck in the dependency.

❌ Mistake 3: Circular dependencies (A depends on B, B on A).
✅ Correct: Redesign; Compose reports a dependency cycle error.

❌ Mistake 4: Relying on depends_on instead of resilient app code.
✅ Correct: Add connection retries and backoff; databases restart at runtime too.

❌ Mistake 5: Using `wait-for-it.sh` hacks when healthchecks do the job.
✅ Correct: Prefer native conditions; scripts only as a fallback.

---

## 🧠 Tricky Interview Question
**Q:** Your Compose file has `depends_on: [db]`, `docker compose up` works, but after a VPS reboot the API sometimes crashes in a restart loop for 30 seconds. Why, and is `depends_on` to blame?

**Answer:** After a reboot the Docker daemon restarts containers using their restart policies, not Compose's `depends_on` logic. The API container may start before the DB is accepting connections, crash, and be restarted by `restart: unless-stopped` until the DB is ready. `depends_on` is not evaluated at boot. The fix is making the app resilient (retry with backoff on DB connect) and also adding healthchecks so `up` is deterministic. The restart loop is actually acting as a crude retry.

---

## ⚫ Interview Questions + Answers

Q1: What are the three conditions?
A1: `service_started` (default), `service_healthy`, `service_completed_successfully`.

Q2: Does `depends_on` guarantee the database accepts connections?
A2: Only with `condition: service_healthy` and a working healthcheck.

Q3: What is the use of `service_completed_successfully`?
A3: To wait for a one-shot job (migrations, seed) to exit with code 0 before starting dependants.

Q4: What does `restart: true` inside depends_on do?
A4: When the dependency is restarted by an explicit Compose operation, the dependent service restarts too (needs a recent Compose v2).

Q5: Does `depends_on` apply to `docker compose run`?
A5: Yes, dependencies are started by default for `run` unless `--no-deps` is passed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Services need others at boot (DB, cache, migrations)
- You want deterministic `up` ordering

❌ Avoid when:
- You expect it to manage runtime failures; use restart policies and app-level retries
- Cross-project or cross-host dependencies; it works within one Compose project

---

## 📊 Visual Diagram
```
 db (healthcheck pg_isready) ----> healthy? ----+
 cache (redis-cli ping) ---------> healthy? ----+--> migrate runs --> exit 0?
                                                |                      |
                                                +----------------------+
                                                           |
                                                           v
                                                    api starts
                                                           |
                                               api healthy (curl /health)
                                                           |
                                                           v
                                                    nginx starts
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| depends_on | Declare start dependencies | निर्भरता घोषित करना |
| service_started | Container has started | container चालू हुआ |
| service_healthy | Healthcheck passes | healthcheck पास |
| service_completed_successfully | Job exited with 0 | job सफल खत्म |
| Race condition | Outcome depends on timing | timing पर निर्भर गड़बड़ी |
| One-shot job | Runs once then exits | एक बार चलने वाला job |

---

## ⚡ 3-Line Summary
English: `depends_on` orders startup; with conditions and healthchecks it also waits for readiness or job completion.
Short form is order only, so use long form for databases.
Still write apps that retry connections.
Hindi: `depends_on` startup का क्रम तय करता है; conditions और healthchecks के साथ readiness या job पूरा होने का इंतज़ार भी करता है।
Short form सिर्फ order है, इसलिए databases के लिए long form use करो।
फिर भी apps में connection retry लिखो।

---

## ➡️ Next Topic
**192. healthcheck in Compose** - how to write the checks that make `service_healthy` work.
