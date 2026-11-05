# 197. profiles in Compose
# हिंदी में: Compose में Profiles

---

## 🔵 Simple Definition (English)
A **profile** is a label you attach to a service with `profiles: [name]`. Services without a profile always start. Services with a profile start only when you activate it with `--profile name` or the `COMPOSE_PROFILES` environment variable. It lets one compose file hold optional services (debug tools, admin UIs, workers, test runners).

## 🔵 सरल परिभाषा (Hindi)
**Profile** एक label है जो आप service पर `profiles: [name]` से लगाते हैं। बिना profile वाली services हमेशा start होती हैं। Profile वाली services तभी start होती हैं जब आप `--profile name` या `COMPOSE_PROFILES` environment variable से उसे activate करें। इससे एक ही compose file में optional services (debug tools, admin UI, workers, test runner) रखी जा सकती हैं।

---

## 🔴 Problem it Solves
A dev stack needs pgAdmin, Mailhog, a seed job, and an e2e test runner. But you do not want them running in production or always eating RAM. Before profiles, teams kept many compose files or commented lines in and out. Profiles keep one file and make optional parts explicit.

## 🔴 यह क्यों बना? (Hindi)
Dev stack को pgAdmin, Mailhog, seed job और e2e test runner चाहिए। पर production में या हमेशा ये चलें तो RAM खराब होती है। Profiles से पहले टीमें कई compose files रखतीं या lines comment/uncomment करतीं। Profiles एक ही file में optional हिस्सों को साफ़ तरीके से अलग करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add `profiles: ["debug"]` under a service
Step 2 → `docker compose up` starts only services with NO profile (the "core")
Step 3 → `docker compose --profile debug up` starts core + services tagged "debug"
Step 4 → `COMPOSE_PROFILES=debug,test` activates several profiles at once
Step 5 → Naming a profiled service explicitly (`docker compose run seed`) starts it even without the flag
Step 6 → A core service that `depends_on` a profiled service fails unless that profile is active
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Service के नीचे `profiles: ["debug"]` जोड़ें
Step 2 → `docker compose up` सिर्फ बिना-profile वाली (core) services चलाता है
Step 3 → `docker compose --profile debug up` core + "debug" वाली services चलाता है
Step 4 → `COMPOSE_PROFILES=debug,test` से कई profiles एक साथ active होते हैं
Step 5 → Profile वाली service का नाम सीधे देने पर (`docker compose run seed`) वह बिना flag के भी चलती है
Step 6 → अगर core service किसी profiled service पर `depends_on` करे और वह profile active न हो तो error आता है
```

---

## 🟡 Real World Example
A **Zomato**-style backend team: every developer runs `docker compose up` and gets API + Postgres + Redis. When debugging, they add `--profile tools` to also get pgAdmin and Redis Commander. CI uses `--profile test` to run the integration-test container. On the production VPS nobody sets a profile, so tools never run and the attack surface stays small.

## 🟡 Real Example Hindi mein
**Zomato** जैसी backend team: हर developer `docker compose up` करता है तो API + Postgres + Redis मिलते हैं। Debug करते समय `--profile tools` जोड़ते हैं तो pgAdmin और Redis Commander भी आ जाते हैं। CI में `--profile test` से integration-test container चलता है। Production VPS पर कोई profile set नहीं होता, इसलिए tools कभी नहीं चलते और attack surface छोटा रहता है।

---

## 💻 Code / Config Example — Basic

```yaml
# docker-compose.yml
services:
  api:                                   # core service: no profile, always starts
    image: node:20-alpine                # example tag
    command: ["node", "-e", "setInterval(()=>console.log('api up'),5000)"]  # placeholder app
  pgadmin:
    image: dpage/pgadmin4:8              # DB admin UI (example tag)
    profiles: ["tools"]                  # starts ONLY with --profile tools
    environment:
      PGADMIN_DEFAULT_EMAIL: dev@example.com   # dev-only login
      PGADMIN_DEFAULT_PASSWORD: dev-only-pass  # never reuse in production
    ports:
      - "127.0.0.1:5050:80"              # bind to loopback so only you can open it
```

```bash
docker compose up -d                     # only "api"
docker compose --profile tools up -d     # api + pgadmin
COMPOSE_PROFILES=tools docker compose up -d   # same using env var
docker compose --profile tools down      # include profiled services when stopping!
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml : core + several profiles
services:
  api:
    build: ./api                          # no profile = core
    depends_on:
      db:
        condition: service_healthy        # wait for DB health (core to core: safe)
    environment:
      DATABASE_URL: postgres://app:app@db:5432/app   # dev credentials only
  db:
    image: postgres:16-alpine             # core database
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]   # healthy when accepting connections
      interval: 5s
      timeout: 3s
      retries: 10
  mailhog:
    image: mailhog/mailhog:v1.0.1         # fake SMTP inbox for dev
    profiles: ["dev", "test"]             # a service can belong to MANY profiles
    ports:
      - "127.0.0.1:8025:8025"             # web UI on loopback
  worker:
    build: ./api                          # same image, different command
    command: ["node", "worker.js"]        # background jobs (queue consumer)
    profiles: ["workers"]                 # optional: scale only when needed
    depends_on:
      db:
        condition: service_healthy
  seed:
    build: ./api
    command: ["node", "seed.js"]          # one-shot data seeding
    profiles: ["seed"]                    # run manually: docker compose run --rm seed
    restart: "no"                         # one-shot, never auto-restart
    depends_on:
      db:
        condition: service_healthy
  e2e:
    image: mcr.microsoft.com/playwright:v1.47.0-jammy   # example tag, update
    profiles: ["test"]                    # CI only
    working_dir: /tests
    volumes:
      - ./e2e:/tests                      # mount tests
    command: ["npx", "playwright", "test"]
    depends_on:
      - api
```

```bash
docker compose --profile dev up -d                # core + mailhog
docker compose --profile test up --exit-code-from e2e   # CI: stop when e2e ends, return its exit code
docker compose run --rm seed                      # run the seed job once (profile auto-enabled)
docker compose --profile workers up -d --scale worker=3   # three workers
```

---

## 🟠 My Stack Integration
- **Node.js**: `worker` profile for BullMQ/queue consumers using the same image as the API.
- **FastAPI**: `migrate` profile that runs `alembic upgrade head` as a one-shot before the API (`docker compose run --rm migrate`).
- **React**: `storybook` profile for a UI preview, not shipped to prod.
- **VPS / AWS**: in production never set `COMPOSE_PROFILES`; GitHub Actions can set it to `test` only in CI.

```yaml
# FastAPI migrate job as a profile
services:
  migrate:
    build: ./fastapi
    command: ["alembic", "upgrade", "head"]   # apply DB migrations
    profiles: ["migrate"]                     # not started by default
    environment:
      DATABASE_URL: postgresql+psycopg://app:app@db:5432/app   # dev example
    depends_on:
      db:
        condition: service_healthy
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running `docker compose down` without the profile and wondering why pgadmin keeps running.
✅ Correct: `docker compose --profile tools down` (or `COMPOSE_PROFILES=tools`), or `down --remove-orphans`.

❌ Mistake 2: A core service `depends_on` a profiled service.
✅ Correct: Dependencies of core services must be core, or give the dependent service the same profile.

❌ Mistake 3: Using profiles as a security boundary.
✅ Correct: Profiles only select what starts. Bind admin UIs to `127.0.0.1` and use strong passwords anyway.

❌ Mistake 4: Putting secrets for tools in the compose file.
✅ Correct: Use `.env` (git-ignored) or Docker secrets.

---

## 🧠 Tricky Interview Question
You run `docker compose run --rm seed`, where `seed` has `profiles: ["seed"]` and depends on `db` (no profile). Does it start without `--profile seed`?

Answer: Yes. When you name a profiled service explicitly on the command line, Compose activates it automatically, and it also starts its non-profiled dependency `db`. But `docker compose up seed` and `docker compose up` (no names) behave differently: the second one skips seed. Check your Compose version since this behaviour was refined across v2 releases.

---

## ⚫ Interview Questions + Answers

Q1: What happens to services with no `profiles` key?
A1: They are always enabled whatever profiles you pass.

Q2: How do you enable multiple profiles?
A2: Repeat the flag `--profile a --profile b`, or `COMPOSE_PROFILES=a,b`.

Q3: Can one service have several profiles?
A3: Yes, it starts when any one of them is active.

Q4: Why use profiles instead of separate files?
A4: One source of truth, fewer duplicated lines, but the file may grow; for environment differences (ports, images) use override files instead.

Q5: How do you run a one-off job like DB seeding?
A5: A profiled service plus `docker compose run --rm seed`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Optional dev tools, one-shot jobs, test runners, workers.
- You want one file but different "modes".

❌ Avoid when:
- Environments differ in config (image tags, replicas, env values): use override files or `-f` files.
- You need hard isolation of services from production: keep them out of the file.

---

## 📊 Visual Diagram
```
docker-compose.yml
 +--------+  +--------+                 always on (no profile)
 |  api   |  |   db   |   <-- docker compose up
 +--------+  +--------+
 +----------+ +---------+
 | pgadmin  | | mailhog |  <-- --profile tools / dev
 +----------+ +---------+
 +--------+  +--------+
 | worker |  |  e2e   |    <-- --profile workers / test
 +--------+  +--------+
 +--------+
 |  seed  |                <-- docker compose run --rm seed
 +--------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| profile | Label that makes a service optional | Service को optional बनाने वाला label |
| COMPOSE_PROFILES | Env var listing active profiles | Active profiles की env variable |
| core service | Service without profile | बिना profile वाली service |
| one-shot job | Container that runs once and exits | एक बार चलकर बंद होने वाला container |
| --exit-code-from | Return exit code of one service | किसी service का exit code लौटाना |

---

## ⚡ 3-Line Summary
English: Profiles mark services as optional inside one compose file.
Only core services start by default; others need `--profile` or `COMPOSE_PROFILES`.
Great for tools, workers, seed jobs and CI tests.
Hindi: Profiles एक compose file में services को optional बनाते हैं।
Default में सिर्फ core services चलती हैं; बाकी के लिए `--profile` या `COMPOSE_PROFILES` चाहिए।
Tools, workers, seed jobs और CI tests के लिए बढ़िया।

---

## ➡️ Next Topic
**198. Docker Compose Commands (up, down, ps, logs, exec, build)**: you have seen several commands already; next we learn the daily command set properly.
