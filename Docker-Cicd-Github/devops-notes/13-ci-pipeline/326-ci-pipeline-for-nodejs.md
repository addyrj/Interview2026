# 326. CI Pipeline for Node.js
# हिंदी में: Node.js के लिए CI Pipeline

---

## 🔵 Simple Definition (English)
A **Node.js CI pipeline** automatically installs dependencies, lints, type-checks, tests (with a real database), builds and verifies the Docker image on every push and pull request, so only healthy code can be merged and deployed.

## 🔵 सरल परिभाषा (Hindi)
**Node.js CI pipeline** हर push और pull request पर अपने आप dependencies install करती है, lint, type-check, tests (असली database के साथ), build और Docker image की जाँच करती है, ताकि सिर्फ स्वस्थ code merge और deploy हो।

---

## 🔴 Problem it Solves
"Works on my machine": a developer forgets to commit `package-lock.json`, uses Node 22 locally while the VPS runs Node 20, skips tests before merging, or pushes a Dockerfile that no longer builds. These problems are found on production at 2 AM instead of in a PR.

## 🔴 यह क्यों बना? (Hindi)
"मेरी machine पर चलता है": developer `package-lock.json` commit करना भूल जाता है, local में Node 22 है जबकि VPS पर Node 20, merge से पहले tests skip कर देता है, या ऐसा Dockerfile push करता है जो build ही नहीं होता। ये समस्याएँ PR में पकड़ी जाने की जगह रात 2 बजे production पर मिलती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Trigger: pull_request to main and push to main
Step 2 → Checkout code and set up Node with the same version as production (from .nvmrc)
Step 3 → Restore npm cache keyed by package-lock.json
Step 4 → npm ci (exact, reproducible install)
Step 5 → Lint + type-check (fast gate)
Step 6 → Unit tests, then integration tests against a Postgres/Redis service container
Step 7 → npm run build, upload coverage/build artifact
Step 8 → docker build (no push) to prove the Dockerfile works; npm audit for security
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Trigger: main पर pull_request और main पर push
Step 2 → Code checkout और Node वही version जो production में है (.nvmrc से)
Step 3 → package-lock.json के key से npm cache restore
Step 4 → npm ci (सटीक, reproducible install)
Step 5 → Lint + type-check (तेज़ gate)
Step 6 → Unit tests, फिर Postgres/Redis service container के साथ integration tests
Step 7 → npm run build, coverage/build artifact upload
Step 8 → Dockerfile सही है यह दिखाने के लिए docker build (push नहीं); security के लिए npm audit
```

---

## 🟡 Real World Example
A Zomato-style restaurant-search API (Express + Postgres) deploys to an AWS EC2 box. The team's CI runs on every PR: ESLint, TypeScript check, 300 Jest tests, an integration suite with a Postgres service container, and a Docker build. A PR that upgraded `pg` and broke the connection string handling was caught by the integration job in 4 minutes, before reviewers even opened it.

## 🟡 Real Example Hindi mein
Zomato-जैसा restaurant-search API (Express + Postgres) AWS EC2 पर deploy होता है। टीम का CI हर PR पर चलता है: ESLint, TypeScript check, 300 Jest tests, Postgres service container के साथ integration suite, और Docker build। `pg` upgrade करने वाला एक PR जिसने connection string handling तोड़ दी, integration job में 4 मिनट में पकड़ा गया, reviewers के खोलने से पहले ही।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/ci.yml  (minimal Node.js CI)
name: CI                            # workflow name
on:                                 # triggers
  push:                             # on push
    branches: [main]                # to main
  pull_request:                     # and on PRs
jobs:                               # jobs
  test:                             # job id
    runs-on: ubuntu-latest          # runner OS
    steps:                          # steps
      - uses: actions/checkout@v4   # clone the repo (example version)
      - uses: actions/setup-node@v4 # install Node
        with:                       # inputs
          node-version: 20          # same major as production
          cache: npm                # cache based on package-lock.json
      - run: npm ci                 # reproducible install, fails if lock is out of sync
      - run: npm run lint           # style and bug rules
      - run: npm test               # unit tests
      - run: npm run build          # compile / bundle
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/ci.yml  (production Node.js CI with DB, matrix, artifacts, docker)
name: CI                            # workflow name
on:                                 # triggers
  push:                             # push
    branches: [main]                # main
  pull_request:                     # PRs
    branches: [main]                # to main
concurrency:                        # stop stale runs
  group: ci-${{ github.ref }}       # per branch
  cancel-in-progress: true          # newer push wins
permissions:                        # least privilege
  contents: read                    # read only
env:                                # workflow-wide env
  NODE_ENV: test                    # test mode
jobs:                               # jobs
  quality:                          # fast gate
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 10             # cap
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-node@v4 # node
        with:                       # inputs
          node-version-file: .nvmrc # single source of truth for Node version
          cache: npm                # npm cache
      - run: npm ci                 # install
      - run: npm run lint           # ESLint
      - run: npx tsc --noEmit       # type check (remove if no TypeScript)
      - run: npm audit --audit-level=high --omit=dev  # fail on high/critical prod vulns
  test:                             # unit + integration
    needs: quality                  # after gate
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 15             # cap
    strategy:                       # matrix
      matrix:                       # variants
        node: [18, 20, 22]          # supported versions
    services:                       # service containers
      postgres:                     # db
        image: postgres:16          # example tag
        env:                        # env
          POSTGRES_USER: app        # user
          POSTGRES_PASSWORD: app    # CI-only password
          POSTGRES_DB: app_test     # test db
        ports: ['5432:5432']        # port
        options: --health-cmd "pg_isready -U app" --health-interval 5s --health-retries 10  # wait ready
      redis:                        # cache
        image: redis:7              # example tag
        ports: ['6379:6379']        # port
        options: --health-cmd "redis-cli ping" --health-interval 5s --health-retries 10  # health
    env:                            # job env
      DATABASE_URL: postgres://app:app@localhost:5432/app_test  # connection string
      REDIS_URL: redis://localhost:6379  # redis url
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-node@v4 # node
        with:                       # inputs
          node-version: ${{ matrix.node }}  # matrix version
          cache: npm                # cache
      - run: npm ci                 # install
      - run: npm run migrate        # apply schema to the test DB
      - run: npm test -- --coverage # run Jest with coverage
      - uses: actions/upload-artifact@v4  # keep coverage report
        if: matrix.node == 20       # upload once only
        with:                       # inputs
          name: coverage            # artifact name
          path: coverage/           # folder
          retention-days: 7         # delete after a week
  docker:                           # verify image builds
    needs: test                     # after tests
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 20             # cap
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: docker/setup-buildx-action@v3  # buildx builder
      - uses: docker/build-push-action@v6    # build image
        with:                       # inputs
          context: .                # build context
          push: false               # CI does not push; CD does
          tags: myapp:ci            # local tag
          cache-from: type=gha      # reuse GitHub cache
          cache-to: type=gha,mode=max  # save layers
```

---

## 🟠 My Stack Integration
`.nvmrc` holds `20`, the same version as the `node:20-alpine` base image in the Dockerfile, so CI and the VPS agree. The Docker job proves the image builds; a separate CD workflow later pushes it and SSHes to the VPS where Nginx proxies to the container.

```dockerfile
# Node API Dockerfile used by the CI docker job (copy-paste ready)
# syntax=docker/dockerfile:1

# Stage 1: install production dependencies only
FROM node:20-alpine AS deps
# Working directory inside the image
WORKDIR /app
# Copy manifests first so the dependency layer is cached
COPY package*.json ./
# Exact install from lock file, no devDependencies
RUN npm ci --omit=dev

# Stage 2: small final image
FROM node:20-alpine
# Working directory
WORKDIR /app
# Production mode
ENV NODE_ENV=production
# Reuse installed dependencies from stage 1
COPY --from=deps /app/node_modules ./node_modules
# Application source (keep node_modules out via .dockerignore)
COPY . .
# Do not run as root
USER node
# API port that Nginx proxies to
EXPOSE 3000
# Start command
CMD ["node", "server.js"]
```

Security: `npm audit` plus `permissions: contents: read`; DB passwords in CI are throwaway values, real secrets live in GitHub Secrets and only the CD workflow uses them.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `npm install` in CI.
✅ Correct: Use `npm ci` for exact versions from the lock file.

❌ Mistake 2: Testing only on one Node version while production differs.
✅ Correct: Use `.nvmrc`/`node-version-file` and a matrix covering supported versions.

❌ Mistake 3: Mocking the database in all tests and never running a real one.
✅ Correct: Add a service container for integration tests.

❌ Mistake 4: Pushing the Docker image from the PR workflow, so forks and unreviewed code reach the registry.
✅ Correct: CI only builds; CD pushes after merge to main.

---

## 🧠 Tricky Interview Question
**Q:** CI is green on Node 20 but the app crashes in production with "Cannot find module". `package.json` is fine. What could differ?

Answer: Likely a dev dependency used at runtime. CI installs with `npm ci` (including devDependencies), so tests pass, but the production image runs `npm ci --omit=dev`, which removes it. Fix: move the package to `dependencies`, and make the CI docker job start the container and run a smoke test (`docker run ... node -e "require('./server')"`/health check) so this class of bug fails in CI.

---

## ⚫ Interview Questions + Answers

Q1: Why `npm ci` over `npm install`?
A1: `npm ci` deletes `node_modules`, installs exactly from the lock file and errors if `package.json` and the lock disagree. It is faster and reproducible.

Q2: How does `cache: npm` work?
A2: `setup-node` caches the npm download cache directory with a key derived from the lock file hash, so unchanged dependencies are not downloaded again.

Q3: Why service containers instead of mocks?
A3: They give real SQL behaviour (constraints, transactions) and catch driver/config bugs mocks cannot.

Q4: How do you speed up a slow Node CI?
A4: Cache dependencies, run lint/type-check in parallel to tests, shard tests, use `--bail`, limit matrix size, and use Docker layer cache.

Q5: What belongs in CI vs CD?
A5: CI verifies (lint, test, build, scan). CD ships (push image, deploy, migrate). Secrets for production belong only in CD.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any Node.js service with more than one contributor.
- You deploy via Docker to a VPS/AWS.

❌ Avoid when:
- A throwaway script with no tests; a lighter lint-only workflow is enough.
- Don't run the big matrix on every push if the lib only supports one version.

---

## 📊 Visual Diagram
```
 PR / push
    |
    v
[quality: lint, tsc, audit] --fail--> RED
    |
    v
[test matrix 18|20|22 + Postgres + Redis] --fail--> RED
    |        \-> coverage artifact
    v
[docker build (push:false)] --fail--> RED
    |
    v
 GREEN -> merge allowed -> CD workflow ships image to VPS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `npm ci` | Clean exact install | सटीक clean install |
| Service container | Sidecar DB for tests | test के लिए साथ चलने वाला DB |
| Matrix | Run over versions | कई versions पर चलाना |
| `.nvmrc` | Pins Node version | Node version तय करने की file |
| Artifact | File saved from a run | run से सहेजी file |

---

## ⚡ 3-Line Summary
English: Node CI = checkout, cached `npm ci`, lint, test with real services, build, docker build.
English: Pin Node via `.nvmrc`, use a matrix, and keep CI read-only.
English: CI verifies; CD (with secrets) pushes and deploys.

Hindi: Node CI = checkout, cached `npm ci`, lint, असली services के साथ test, build, docker build।
Hindi: Node version `.nvmrc` से pin करो, matrix रखो, और CI को read-only रखो।
Hindi: CI जाँचता है; CD (secrets के साथ) push और deploy करता है।

---

## ➡️ Next Topic
**327. CI Pipeline for Python/FastAPI** — same idea for the Python half of your stack.
