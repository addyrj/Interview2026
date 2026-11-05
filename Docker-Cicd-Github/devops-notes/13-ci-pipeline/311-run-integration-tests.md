# 311. Run Integration Tests
# हिंदी में: Integration Tests चलाना (असली DB के साथ)

---

## 🔵 Simple Definition (English)
Integration tests check that several parts work together: your API, a real database, cache or queue. In GitHub Actions you start these dependencies as `services:` containers next to the job, run migrations, then execute the tests against them.

## 🔵 सरल परिभाषा (Hindi)
Integration tests जाँचते हैं कि कई हिस्से मिलकर सही काम करते हैं: आपकी API, असली database, cache या queue। GitHub Actions में इन dependencies को job के साथ `services:` containers के रूप में चालू करते हैं, migrations चलाते हैं और फिर उन्हीं के विरुद्ध tests चलाते हैं।

---

## 🔴 Problem it Solves
Unit tests with mocks pass even when the SQL is wrong, the migration is missing a column, or the Mongo index conflicts. These bugs appear only in production. Integration tests catch real wiring errors (connection strings, schema, transactions, serialization) before merge.

## 🔴 यह क्यों बना? (Hindi)
Mocks वाले unit tests तब भी pass हो जाते हैं जब SQL गलत हो, migration में column छूट गया हो या Mongo index टकरा रहा हो। ऐसे bugs सिर्फ production में दिखते थे। Integration tests असली wiring की गलतियाँ (connection string, schema, transactions, serialization) merge से पहले पकड़ लेते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Job declares services: postgres, redis (each is a Docker container)
Step 2 → Runner pulls images and starts them BEFORE the steps
Step 3 → health-cmd in options waits until the DB is really ready
Step 4 → Ports are mapped to localhost (job runs directly on the VM)
Step 5 → Steps: checkout, install, run migrations on the empty DB
Step 6 → Tests connect via DATABASE_URL env and exercise the real stack
Step 7 → Job ends, runner is destroyed, containers vanish (clean state)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Job में services घोषित होती हैं: postgres, redis (हर एक Docker container)
Step 2 → Runner images pull करके steps से पहले उन्हें शुरू करता है
Step 3 → options का health-cmd तब तक रुकता है जब तक DB सच में ready न हो
Step 4 → Ports localhost पर map होते हैं (job सीधे VM पर चलता है)
Step 5 → Steps: checkout, install, खाली DB पर migrations चलाना
Step 6 → Tests DATABASE_URL env से connect होकर असली stack को चलाते हैं
Step 7 → Job खत्म, runner नष्ट, containers गायब (साफ़ state)
```

---

## 🟡 Real World Example
Zomato-style restaurant search: a FastAPI endpoint `/restaurants?city=Pune` uses a PostgreSQL full-text index and Redis cache. Unit tests with mocks passed, but a migration renamed a column. The integration job started Postgres 16, ran Alembic migrations, called the endpoint with `httpx`, and failed with `column "city_name" does not exist`. Caught in the PR, not on the VPS.

## 🟡 Real Example Hindi mein
Zomato जैसा restaurant search: FastAPI endpoint `/restaurants?city=Pune` PostgreSQL full-text index और Redis cache इस्तेमाल करता है। Mocks वाले unit tests pass थे, पर एक migration ने column का नाम बदल दिया था। Integration job ने Postgres 16 चालू किया, Alembic migrations चलाईं, `httpx` से endpoint बुलाया और `column "city_name" does not exist` से fail हुआ। PR में पकड़ा गया, VPS पर नहीं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/integration.yml  (Node.js + PostgreSQL, basic)
name: Integration Tests                # Workflow name

on: [pull_request]                     # Run on every PR

jobs:
  integration:                         # Job id
    runs-on: ubuntu-latest             # Linux runner (service containers need Linux)
    services:                          # Containers started before steps
      postgres:                        # Service label (hostname inside Docker network)
        image: postgres:16             # Official image (example tag)
        env:                           # Container environment
          POSTGRES_USER: app           # DB user created at first start
          POSTGRES_PASSWORD: testpass  # Throwaway password, CI only
          POSTGRES_DB: app_test        # DB name created at start
        ports:
          - 5432:5432                  # host:container, reachable at localhost:5432
        options: >-                    # Extra docker create options
          --health-cmd "pg_isready -U app"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
    steps:
      - uses: actions/checkout@v4      # Get the code
      - uses: actions/setup-node@v4    # Install Node
        with:
          node-version: 20
          cache: npm
      - run: npm ci                    # Install dependencies
      - run: npm run migrate           # Apply schema (your own script)
        env:
          DATABASE_URL: postgres://app:testpass@localhost:5432/app_test   # Service via mapped port
      - run: npm run test:integration  # Jest/Mocha integration suite
        env:
          DATABASE_URL: postgres://app:testpass@localhost:5432/app_test
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/integration.yml  (FastAPI + Postgres + Redis + Mongo, production style)
name: Integration Tests

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read                       # Read-only token

jobs:
  api-integration:
    runs-on: ubuntu-latest
    timeout-minutes: 15                # Hard stop for hung containers
    services:
      postgres:
        image: postgres:16-alpine      # Small image, faster pull
        env:
          POSTGRES_USER: app
          POSTGRES_PASSWORD: ${{ github.run_id }}   # Unique, non-secret throwaway value
          POSTGRES_DB: app_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U app -d app_test"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 10
      mongo:
        image: mongo:7
        ports: ["27017:27017"]
        options: >-
          --health-cmd "mongosh --quiet --eval 'db.runCommand({ping:1}).ok'"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 10
    env:                               # Job-level env, shared by all steps
      DATABASE_URL: postgresql+psycopg://app:${{ github.run_id }}@localhost:5432/app_test
      REDIS_URL: redis://localhost:6379/0
      MONGO_URL: mongodb://localhost:27017/app_test
      APP_ENV: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: api/requirements*.txt
      - name: Install dependencies
        working-directory: api
        run: pip install -r requirements.txt -r requirements-dev.txt
      - name: Run migrations
        working-directory: api
        run: alembic upgrade head      # Build schema on empty DB
      - name: Run integration tests
        working-directory: api
        run: pytest tests/integration -q -m integration --maxfail=3   # Only marked tests
      - name: Dump service logs on failure
        if: failure()                  # Helpful debugging, only when red
        run: docker ps -a              # Show container states (logs via docker logs <id>)
```

---

## 🟠 My Stack Integration
- **Node.js:** Use Jest with `supertest`; seed data with a `beforeAll` and truncate tables in `afterEach` so tests stay independent.
- **FastAPI:** Mark tests `@pytest.mark.integration` and register the marker in `pytest.ini`; unit tests stay fast.
- **Containerised job:** If the job itself uses `container: node:20`, reach services by label (`postgres:5432`), not `localhost`.
- **Nginx/VPS/AWS:** Nginx is not needed here. Staging checks against the VPS are smoke tests, a later topic. Use the same Postgres major version as your RDS/VPS.

```yaml
# Same job, but running inside a container: use service label as host
jobs:
  integration:
    runs-on: ubuntu-latest
    container: node:20                 # Job runs in a container
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: testpass
    env:
      DATABASE_URL: postgres://postgres:testpass@postgres:5432/postgres   # host = label "postgres"
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run test:integration
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No `health-cmd`, so tests start before Postgres accepts connections and fail randomly.
✅ Correct: Add health options; the runner waits for "healthy".

❌ Mistake 2: Using `localhost` when the job runs in a `container:`.
✅ Correct: Use the service label as hostname (`postgres`, `redis`).

❌ Mistake 3: Sharing data between tests so order matters.
✅ Correct: Reset DB per test (transaction rollback or truncate).

❌ Mistake 4: Pointing integration tests at a real staging/production database with real secrets.
✅ Correct: Only throwaway service containers; never production credentials in CI.

❌ Mistake 5: Using `postgres:latest`, so a new major version silently breaks CI.
✅ Correct: Pin the major version that matches production.

---

## 🧠 Tricky Interview Question
Tests pass on `localhost:5432` mapping but fail with "connection refused" after you add `container: node:20` to the job. Why?

Answer: When the job runs inside a container, it joins the same Docker network as service containers and no ports are published to the host for it. `localhost` now refers to the job container itself. Service containers are reachable by their label (`postgres`). Port mapping (`ports:`) is only needed when the job runs directly on the runner VM.

---

## ⚫ Interview Questions + Answers

Q1: What are service containers?
A1: Docker containers GitHub starts for a job (DB, cache, broker) that live only for that job and are destroyed afterward.

Q2: Why do health checks matter?
A2: A container being "started" does not mean the database is ready. `--health-cmd` makes the runner wait until it is truly healthy.

Q3: How do you avoid slow integration tests blocking PR feedback?
A3: Run unit tests first as a separate job, run integration in parallel, use `needs` only where required, and keep a smaller set of integration tests focused on boundaries.

Q4: Can service containers run on macOS or Windows runners?
A4: No. They are supported on Linux runners only; use docker compose steps otherwise.

Q5: How do you make integration tests deterministic?
A5: Fresh DB per run, migrations from scratch, seeded fixtures, fixed clock and random seed, no external network, and cleanup between tests.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Code touches SQL, ORM, migrations, cache or queues.
- API contract between layers must be verified.
- Before deploying to your VPS.

❌ Avoid when:
- Testing pure functions; unit tests are cheaper.
- A third-party paid API is involved; use a contract or mock server.
- Full browser flows; use end-to-end tests in a separate workflow.

---

## 📊 Visual Diagram
```
  ┌──────────────── GitHub Runner (ubuntu VM) ────────────────┐
  │                                                           │
  │   Job steps                      Service containers       │
  │  ┌──────────────┐  localhost    ┌─────────────────────┐   │
  │  │ checkout     │  :5432   ───▶ │ postgres:16 (health)│   │
  │  │ npm ci       │  :6379   ───▶ │ redis:7    (health) │   │
  │  │ migrate      │  :27017  ───▶ │ mongo:7    (health) │   │
  │  │ run tests    │               └─────────────────────┘   │
  │  └──────┬───────┘                                         │
  │         ▼ exit code → ✅ / ❌ status check                │
  └───────────────────────────────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Integration test | Test of multiple parts together | कई हिस्सों का मिलकर test |
| Service container | Helper container (DB, cache) for a job | job के लिए सहायक container |
| Health check | Command proving a service is ready | service तैयार है यह जाँचने की command |
| Migration | Script that changes DB schema | DB schema बदलने की script |
| Fixture / seed | Prepared test data | पहले से तैयार test data |
| Teardown | Cleanup after test | test के बाद सफ़ाई |

---

## ⚡ 3-Line Summary
English: Integration tests run your code against real DB/cache started as service containers.
English: Health checks, migrations and clean state per test make them reliable.
English: Use localhost with a mapped port on the VM, or the service label inside a container job.
Hindi: Integration tests आपका code असली DB/cache के विरुद्ध चलाते हैं जो service containers से शुरू होते हैं।
Hindi: Health check, migrations और हर test पर साफ़ state उन्हें भरोसेमंद बनाते हैं।
Hindi: VM पर mapped port के साथ localhost, और container job में service label इस्तेमाल करें।

Note: workflows here were YAML-parsed but not run on GitHub; image tags are examples.

---

## ➡️ Next Topic
312. Generate Test Coverage: now that tests run, we measure how much of the code they actually exercise.
