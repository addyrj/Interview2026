# 327. CI Pipeline for Python/FastAPI
# हिंदी में: Python/FastAPI के लिए CI Pipeline

---

## 🔵 Simple Definition (English)
A **FastAPI CI pipeline** sets up a pinned Python version, installs dependencies from a lock/requirements file with pip caching, runs ruff (lint/format), mypy (types), pytest (with a real Postgres) and finally builds the Docker image, on every push and pull request.

## 🔵 सरल परिभाषा (Hindi)
**FastAPI CI pipeline** pinned Python version set करती है, pip caching के साथ requirements file से dependencies install करती है, ruff (lint/format), mypy (types), pytest (असली Postgres के साथ) चलाती है और अंत में Docker image build करती है, हर push और pull request पर।

---

## 🔴 Problem it Solves
Python projects drift: a dependency upgrades silently and breaks an endpoint, a developer's local Python 3.13 hides a bug that the production Python 3.12 shows, type errors reach production because nobody runs mypy, and Pydantic validation changes break the API contract. CI makes the environment reproducible and checks each PR the same way.

## 🔴 यह क्यों बना? (Hindi)
Python projects drift करते हैं: कोई dependency चुपचाप upgrade होकर endpoint तोड़ देती है, developer के local Python 3.13 में छुपा bug production के Python 3.12 में दिखता है, mypy कोई चलाता नहीं इसलिए type errors production पहुँचते हैं, और Pydantic validation बदलने से API contract टूटता है। CI environment को reproducible बनाता है और हर PR को एक जैसा जाँचता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Trigger on pull_request and push to main
Step 2 → actions/setup-python with a pinned version and cache: pip
Step 3 → pip install -r requirements.txt -r requirements-dev.txt
Step 4 → ruff check + ruff format --check (fast lint)
Step 5 → mypy app/ (static types)
Step 6 → pytest with Postgres service container, coverage report
Step 7 → docker build of the FastAPI image
Step 8 → pip-audit (dependency vulnerabilities)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → pull_request और main पर push पर trigger
Step 2 → pinned version के साथ actions/setup-python और cache: pip
Step 3 → pip install -r requirements.txt -r requirements-dev.txt
Step 4 → ruff check + ruff format --check (तेज़ lint)
Step 5 → mypy app/ (static types)
Step 6 → Postgres service container के साथ pytest, coverage report
Step 7 → FastAPI image का docker build
Step 8 → pip-audit (dependency vulnerabilities)
```

---

## 🟡 Real World Example
A Paytm-style wallet service written in FastAPI + SQLAlchemy runs on a VPS. A PR upgraded Pydantic from v1 style to v2 and changed how `Optional` fields default. Unit tests with mocks passed, but the pytest integration job with a real Postgres and `httpx.AsyncClient` hit `/transactions` and got a 422 error, blocking the merge. Without the real-DB tests this would have broken the mobile app in production.

## 🟡 Real Example Hindi mein
Paytm-जैसी wallet service FastAPI + SQLAlchemy में लिखी है और VPS पर चलती है। एक PR ने Pydantic को v1 style से v2 पर upgrade किया और `Optional` fields के default बदल गए। Mocks वाले unit tests pass हुए, पर असली Postgres और `httpx.AsyncClient` वाले pytest integration job ने `/transactions` hit किया तो 422 error मिला और merge रुक गया। असली-DB tests न होते तो mobile app production में टूटता।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/api-ci.yml  (minimal FastAPI CI)
name: API CI                        # workflow name
on: [push, pull_request]            # run on push and PR
jobs:                               # jobs
  test:                             # job id
    runs-on: ubuntu-latest          # runner
    steps:                          # steps
      - uses: actions/checkout@v4   # get code (example version)
      - uses: actions/setup-python@v5  # install Python
        with:                       # inputs
          python-version: '3.12'    # same as production Dockerfile
          cache: pip                # cache pip downloads (uses requirements*.txt hash)
      - run: pip install -r requirements.txt pytest  # install app deps and pytest
      - run: pytest -q              # quiet test run; non-zero exit fails CI
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/api-ci.yml  (production FastAPI CI)
name: API CI                        # workflow name
on:                                 # triggers
  push:                             # push
    branches: [main]                # main
  pull_request:                     # PRs
    paths: ['api/**', '.github/workflows/api-ci.yml']  # run only when API changes
concurrency:                        # cancel stale runs
  group: api-ci-${{ github.ref }}   # per ref
  cancel-in-progress: true          # newer wins
permissions:                        # least privilege
  contents: read                    # read only
defaults:                           # defaults for run steps
  run:                              # run settings
    working-directory: api          # FastAPI code lives in api/
jobs:                               # jobs
  lint-types:                       # fast gate
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 10             # cap
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-python@v5  # python
        with:                       # inputs
          python-version: '3.12'    # pinned
          cache: pip                # cache
          cache-dependency-path: api/requirements*.txt  # where deps are listed
      - run: pip install -r requirements.txt -r requirements-dev.txt  # install all
      - run: ruff check .           # lint rules
      - run: ruff format --check .  # formatting check without changing files
      - run: mypy app               # static type check
      - run: pip-audit -r requirements.txt  # known CVEs in dependencies
  test:                             # pytest with DB
    needs: lint-types               # after gate
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 15             # cap
    strategy:                       # matrix
      matrix:                       # variants
        python: ['3.11', '3.12']    # supported versions
    services:                       # sidecar
      postgres:                     # db
        image: postgres:16          # example tag
        env:                        # env
          POSTGRES_USER: app        # user
          POSTGRES_PASSWORD: app    # CI-only password
          POSTGRES_DB: app_test     # db
        ports: ['5432:5432']        # port
        options: --health-cmd "pg_isready -U app" --health-interval 5s --health-retries 10  # readiness
    env:                            # env for tests
      DATABASE_URL: postgresql+psycopg://app:app@localhost:5432/app_test  # SQLAlchemy URL
      APP_ENV: test                 # app environment
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-python@v5  # python
        with:                       # inputs
          python-version: ${{ matrix.python }}  # matrix version
          cache: pip                # cache
          cache-dependency-path: api/requirements*.txt  # key files
      - run: pip install -r requirements.txt -r requirements-dev.txt  # install
      - run: alembic upgrade head   # apply migrations to test DB
      - run: pytest --cov=app --cov-report=xml --cov-fail-under=80  # tests + 80% coverage gate
      - uses: actions/upload-artifact@v4  # keep coverage
        if: matrix.python == '3.12'  # once
        with:                       # inputs
          name: coverage-xml        # name
          path: api/coverage.xml    # file (path is relative to repo root here)
  docker:                           # image check
    needs: test                     # after tests
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 20             # cap
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: docker/setup-buildx-action@v3  # buildx
      - uses: docker/build-push-action@v6    # build
        with:                       # inputs
          context: ./api            # build context
          push: false               # no push in CI
          tags: fastapi-app:ci      # tag
          cache-from: type=gha      # cache in
          cache-to: type=gha,mode=max  # cache out
```

---

## 🟠 My Stack Integration
Your FastAPI container sits behind Nginx on the VPS (`proxy_pass http://127.0.0.1:8000`). Keep the CI Python version equal to the Dockerfile's, and run uvicorn in CI as a smoke test so import errors fail early.

```dockerfile
# api/Dockerfile (copy-paste ready, matches the CI docker job)
# Slim base keeps the image small
FROM python:3.12-slim
# No .pyc files, unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# Working directory
WORKDIR /app
# Copy deps first for layer cache
COPY requirements.txt .
# Install without keeping pip cache
RUN pip install --no-cache-dir -r requirements.txt
# Application code
COPY app ./app
# Create a non-root user
RUN useradd -m appuser
# Drop root privileges
USER appuser
# Port Nginx proxies to
EXPOSE 8000
# Start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Security: `pip-audit` for CVEs, non-root user in the image, secrets (JWT key, DB password) only via GitHub Secrets in CD, never in the repo or test fixtures.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Unpinned dependencies (`fastapi` with no version) so CI passes today and fails tomorrow.
✅ Correct: Pin versions (`pip-compile`, `uv lock`, or Poetry lock) and commit the lock.

❌ Mistake 2: Running tests against SQLite while production is Postgres.
✅ Correct: Use a Postgres service container with the same major version.

❌ Mistake 3: Forgetting `working-directory` in a monorepo, so `pytest` finds nothing and exits 5 (no tests) or runs in the wrong folder.
✅ Correct: Set `defaults.run.working-directory` or `cd api`.

❌ Mistake 4: Never running `ruff format --check`, so style diffs pollute every PR.
✅ Correct: Enforce format in CI and via pre-commit.

---

## 🧠 Tricky Interview Question
**Q:** Pytest passes locally but fails in CI with `sqlalchemy.exc.OperationalError: connection refused`. The service container is declared. Why?

Answer: Either the tests start before Postgres is ready (missing `--health-cmd` options, so Actions does not wait), or the host is wrong. With a job running directly on the runner you reach the service at `localhost:5432` (port mapped). If the job runs inside a `container:`, you must use the service name (`postgres`) as hostname. Add health options and use the matching host.

---

## ⚫ Interview Questions + Answers

Q1: How do you cache pip in Actions?
A1: `actions/setup-python` with `cache: pip` (and optionally `cache-dependency-path`). The key comes from the hash of the requirements files.

Q2: Why run mypy and ruff separately from pytest?
A2: They are fast and catch many errors without a DB, so they act as the fail-fast gate before slower tests.

Q3: What does `pytest --cov-fail-under=80` do?
A3: It makes pytest exit non-zero when total coverage is below 80 percent, failing the job (requires pytest-cov).

Q4: How do you test async FastAPI endpoints?
A4: Use `pytest-asyncio` (or `anyio`) with `httpx.AsyncClient(app=app, base_url=...)` or Starlette's `TestClient` for sync-style tests; override dependencies like the DB session.

Q5: How do you avoid leaking secrets in test logs?
A5: Use fake CI-only credentials, keep real secrets out of CI, and rely on GitHub's automatic masking only as a backup.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any FastAPI service with tests and a Docker deploy.
- Several developers or frequent dependency updates (Dependabot).

❌ Avoid when:
- Single prototype script; a simple pytest workflow suffices.
- Don't run the whole matrix on docs-only changes: use `paths` filters.

---

## 📊 Visual Diagram
```
PR (api/** changed)
   |
   v
[ruff -> ruff format -> mypy -> pip-audit] --fail--> RED
   |
   v
[pytest 3.11|3.12 + Postgres + coverage>=80] --fail--> RED
   |
   v
[docker build fastapi-app:ci] --fail--> RED
   |
   v
GREEN -> merge -> CD: push image -> VPS -> Nginx -> uvicorn
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ruff | Fast Python linter/formatter | तेज़ Python linter |
| mypy | Static type checker | static type जाँचने वाला tool |
| pytest | Test framework | test framework |
| pip-audit | Scans deps for CVEs | dependencies की कमजोरियाँ खोजता है |
| Coverage | % code run by tests | tests से चले code का प्रतिशत |

---

## ⚡ 3-Line Summary
English: FastAPI CI = pinned Python, cached pip, ruff and mypy gate, pytest with real Postgres, docker build.
English: Match Python and Postgres versions with production and pin dependencies.
English: Audit dependencies and keep real secrets out of CI.

Hindi: FastAPI CI = pinned Python, cached pip, ruff और mypy gate, असली Postgres के साथ pytest, docker build।
Hindi: Python और Postgres के versions production से मिलाओ और dependencies pin करो।
Hindi: Dependencies audit करो और असली secrets CI से बाहर रखो।

---

## ➡️ Next Topic
**328. CI Pipeline for React** — the frontend half: lint, test, build and bundle checks.
