# 205. Compose for Testing
# हिंदी में: Testing के लिए Compose

---

## 🔵 Simple Definition (English)
Compose for testing starts a throwaway copy of your dependencies (database, cache, mocks) and runs the test suite against them, then tears everything down. Each run starts from a clean state, locally and in CI.

## 🔵 सरल परिभाषा (Hindi)
Testing के लिए Compose आपकी dependencies (database, cache, mocks) की एक throwaway copy चालू करता है, उनके सामने test suite चलाता है, और फिर सब हटा देता है। हर run साफ़ state से शुरू होता है, local और CI दोनों में।

---

## 🔴 Problem it Solves
Tests that share a long-lived dev database become flaky: leftover rows, parallel runs colliding, "works after I clean the DB manually". Mocking the database hides real SQL bugs. Compose gives a real Postgres and Redis per run in seconds.

## 🔴 यह क्यों बना? (Hindi)
जो tests एक लंबे समय से चल रहे dev database को share करते हैं वे flaky हो जाते हैं: बचे हुए rows, parallel runs की टक्कर, "DB हाथ से साफ़ करने पर चलता है"। Database को mock करने से असली SQL bugs छिप जाते हैं। Compose हर run के लिए सेकंडों में असली Postgres और Redis देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → compose.test.yaml defines db (tmpfs, no persistence), redis and a "tests" service
Step 2 → `docker compose -f compose.yaml -f compose.test.yaml up --build --abort-on-container-exit --exit-code-from tests`
Step 3 → db becomes healthy, then the tests container starts
Step 4 → Tests run (migrate, seed, execute)
Step 5 → When tests exits, --abort-on-container-exit stops everything
Step 6 → --exit-code-from tests passes the test exit code to the shell / CI (0 = pass)
Step 7 → `docker compose down -v --remove-orphans` cleans containers, networks, volumes
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → compose.test.yaml में db (tmpfs, बिना persistence), redis और "tests" service होती है
Step 2 → `docker compose -f compose.yaml -f compose.test.yaml up --build --abort-on-container-exit --exit-code-from tests`
Step 3 → db healthy होता है, फिर tests container चालू होता है
Step 4 → Tests चलते हैं (migrate, seed, execute)
Step 5 → tests exit होते ही --abort-on-container-exit सब कुछ रोक देता है
Step 6 → --exit-code-from tests, test का exit code shell / CI तक पहुँचाता है (0 = pass)
Step 7 → `docker compose down -v --remove-orphans` containers, networks, volumes साफ़ करता है
```

---

## 🟡 Real World Example
A fintech team's GitHub Actions job runs integration tests for a payments API. Each pull request spins up Postgres 16 and Redis in the runner using the test compose file; 180 tests hit a real DB. A failing test returns exit code 1, the PR check turns red, and the runner is discarded. Developers run the exact same command on laptops to reproduce failures.

## 🟡 Real Example Hindi mein
एक fintech team का GitHub Actions job payments API के integration tests चलाता है। हर pull request पर runner में test compose file से Postgres 16 और Redis चालू होते हैं; 180 tests असली DB पर चलते हैं। कोई test fail हो तो exit code 1 आता है, PR check लाल हो जाता है, और runner फेंक दिया जाता है। Developers वही command laptop पर चलाकर failure reproduce करते हैं।

---

## 💻 Code / Config Example — Basic
```yaml
# compose.test.yaml  (Basic: DB + test runner)
services:
  db:
    image: postgres:16-alpine            # example tag
    environment:
      POSTGRES_PASSWORD: test            # throwaway password
      POSTGRES_DB: app_test              # test database
    tmpfs:
      - /var/lib/postgresql/data         # in-memory data: fast, nothing to clean
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]  # ready when it accepts connections
      interval: 2s                       # poll quickly
      timeout: 2s
      retries: 20
  tests:
    build: .                             # same image as the app
    command: ["npm", "test"]             # run the test suite
    environment:
      DATABASE_URL: postgres://postgres:test@db:5432/app_test  # test DB URL
    depends_on:
      db: { condition: service_healthy } # wait for DB
```
Run: `docker compose -f compose.test.yaml up --build --abort-on-container-exit --exit-code-from tests`

## 💻 Code / Config Example — Advanced
```yaml
# compose.test.yaml  (Advanced: Node tests + FastAPI tests, Redis, mock API, profiles)
name: myapp-test-${CI_RUN_ID:-local}      # unique project name so parallel CI runs do not collide
services:
  db:
    image: postgres:16-alpine
    environment: { POSTGRES_PASSWORD: test, POSTGRES_DB: app_test }
    tmpfs: ["/var/lib/postgresql/data"]   # no disk I/O
    command: ["postgres", "-c", "fsync=off", "-c", "synchronous_commit=off"]  # faster, TEST ONLY (unsafe for real data)
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d app_test"]
      interval: 2s
      timeout: 2s
      retries: 30
  redis:
    image: redis:7-alpine
    command: ["redis-server", "--save", "", "--appendonly", "no"]  # no persistence
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]  # returns PONG
      interval: 2s
      timeout: 2s
      retries: 20
  payment-mock:
    image: wiremock/wiremock:3.9.1        # example tag; fakes the external payment gateway
    volumes: ["./test/mocks:/home/wiremock/mappings:ro"]  # stub definitions
  tests-node:
    build: { context: ./api, target: dev }   # image with dev dependencies
    command: ["npm", "run", "test:ci"]    # CI test script
    environment:
      DATABASE_URL: postgres://postgres:test@db:5432/app_test
      REDIS_URL: redis://redis:6379
      PAYMENT_URL: http://payment-mock:8080
      NODE_ENV: test
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
      payment-mock: { condition: service_started }
    volumes: ["./reports:/app/reports"]   # export JUnit/coverage files to the host
  tests-fastapi:
    profiles: ["fastapi"]                 # only runs with --profile fastapi
    build: ./fastapi
    command: ["pytest", "-q", "--maxfail=1"]  # stop on first failure
    environment:
      DATABASE_URL: postgresql://postgres:test@db:5432/app_test
    depends_on:
      db: { condition: service_healthy }
```
```bash
# run-tests.sh  (comments on each line)
set -euo pipefail                                                        # fail fast
trap 'docker compose -f compose.test.yaml down -v --remove-orphans' EXIT # always clean up
docker compose -f compose.test.yaml up --build --abort-on-container-exit --exit-code-from tests-node  # run and propagate result
```

---

## 🟠 My Stack Integration
- **Node.js:** Jest/Vitest run inside `tests-node`; the DB hostname is `db`.
- **FastAPI:** `pytest` with a real Postgres is closer to production than SQLite.
- **React:** component tests run without Compose; end-to-end tests (Playwright) need the full stack plus Nginx running.
- **GitHub Actions:** call the script in a job; reports go to `./reports` and get uploaded as artifacts.
- **Security:** test credentials should be fake and ports not published (services talk over the internal network), so nothing is exposed on CI hosts.

```yaml
# .github/workflows/test.yml  (my CI job)
name: test                                   # workflow name
on: [pull_request]                           # run on every PR
jobs:
  integration:
    runs-on: ubuntu-latest                   # GitHub-hosted runner with Docker
    steps:
      - uses: actions/checkout@v4            # example action version
      - name: Run tests in Compose
        run: bash run-tests.sh               # exit code decides pass/fail
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `--exit-code-from`. CI shows green even if tests failed.
✅ Correct: Always pass `--exit-code-from <test service>` with `--abort-on-container-exit`.

❌ Mistake 2: Starting tests before the DB is ready ("connection refused" flakiness).
✅ Correct: healthcheck + `service_healthy`.

❌ Mistake 3: Reusing volumes between runs, leaking data across tests.
✅ Correct: tmpfs or `down -v`.

❌ Mistake 4: Copying `fsync=off` to production.
✅ Correct: It is for disposable test databases only.

---

## 🧠 Tricky Interview Question
Your test job passes locally but CI hangs forever after tests finish. What is likely wrong?

Answer: Without `--abort-on-container-exit` (or `up --exit-code-from`), Compose keeps the DB and Redis running after the test container exits, so the command never returns. Add the flag, and also use a job timeout. Another cause is a test process that does not exit because open DB handles keep Node alive (use `--forceExit` or close connections).

---

## ⚫ Interview Questions + Answers

Q1: Why tmpfs for the test DB?
A1: Memory-backed storage is fast and disappears automatically, so each run is clean.

Q2: How do you run two CI builds at once on one host?
A2: Give each a unique project name (`-p` or `name:`) and avoid fixed host ports.

Q3: `docker compose run` vs `up` for tests?
A3: `run --rm tests` starts the dependencies and runs one command, returning its exit code; `up --exit-code-from` is the multi-service alternative. Both work.

Q4: How to get coverage files out?
A4: Bind-mount a `reports` folder, or `docker compose cp`.

Q5: What to mock and what to run for real?
A5: Run real infrastructure you own (DB, cache). Mock third parties (payment gateways, SMS) with WireMock or similar.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Integration and end-to-end tests need real services.
- You want identical local and CI behaviour.

❌ Avoid when:
- Pure unit tests; they should run without containers for speed.
- Load tests that need production-sized hardware.

---

## 📊 Visual Diagram
```
 CI runner / laptop
 +-------------------------------------------------+
 |  compose up --abort-on-container-exit           |
 |                                                 |
 |  [db tmpfs] [redis] [payment-mock]              |
 |        \       |        /                       |
 |         +---- tests (npm test / pytest) ----+   |
 |                         | exit code         |   |
 +-------------------------+-------------------+---+
                           v
                   shell / CI pass or fail
              then: down -v (everything vanishes)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| integration test | Test with real dependencies | असली dependencies के साथ test |
| tmpfs | RAM storage | RAM storage |
| `--exit-code-from` | Use one service's exit code | एक service का exit code लेना |
| mock | Fake external service | नकली बाहरी service |
| flaky test | Sometimes passes, sometimes fails | कभी pass कभी fail |
| profile | Optional service group | optional services का समूह |

---

## ⚡ 3-Line Summary
English: Test Compose spins up real but disposable dependencies and runs tests against them. Use healthchecks, tmpfs, unique project names and `--exit-code-from`. Always clean up.
Hindi: Test Compose असली पर disposable dependencies चालू करके उन पर tests चलाता है। Healthchecks, tmpfs, unique project names और `--exit-code-from` इस्तेमाल करें। हमेशा cleanup करें।

---

## ➡️ Next Topic
**206. Compose for Production (basics)**: tests pass; next we run the stack safely on a real server.
