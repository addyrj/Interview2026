# 329. CI Pipeline for NestJS
# हिंदी में: NestJS के लिए CI Pipeline

---

## 🔵 Simple Definition (English)
A **NestJS CI pipeline** verifies a TypeScript Nest app on each change: install, lint, compile with `nest build`, run unit tests (`*.spec.ts`), run e2e tests (`test/*.e2e-spec.ts`) against real Postgres/Redis, and build the Docker image.

## 🔵 सरल परिभाषा (Hindi)
**NestJS CI pipeline** हर change पर TypeScript Nest app जाँचती है: install, lint, `nest build` से compile, unit tests (`*.spec.ts`), असली Postgres/Redis के साथ e2e tests (`test/*.e2e-spec.ts`), और Docker image build।

---

## 🔴 Problem it Solves
Nest apps rely on dependency injection and decorators. A missing `providers` entry or a circular dependency compiles fine but crashes at bootstrap ("Nest can't resolve dependencies of..."). Unit tests with mocked providers do not see this; only booting the real module graph (e2e) does. CI that only runs unit tests ships apps that cannot start.

## 🔴 यह क्यों बना? (Hindi)
Nest apps dependency injection और decorators पर चलते हैं। `providers` में missing entry या circular dependency compile तो हो जाती है पर bootstrap पर crash करती है ("Nest can't resolve dependencies of...")। Mocked providers वाले unit tests यह नहीं देखते; सिर्फ असली module graph boot करने वाले e2e tests देखते हैं। जो CI सिर्फ unit tests चलाए वह ऐसा app ship कर देता है जो start ही नहीं होता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Trigger on PR and push to main
Step 2 → setup-node (cache npm) and npm ci
Step 3 → npm run lint (ESLint + Prettier check)
Step 4 → npm run build (nest build -> dist/): compile errors fail here
Step 5 → npm test (Jest unit tests, mocked providers)
Step 6 → npm run test:e2e (boots AppModule with supertest against Postgres/Redis services)
Step 7 → Run migrations (TypeORM/Prisma) on test DB before e2e
Step 8 → docker build the production image, run it, hit /health
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → PR और main पर push पर trigger
Step 2 → setup-node (npm cache) और npm ci
Step 3 → npm run lint (ESLint + Prettier check)
Step 4 → npm run build (nest build -> dist/): compile errors यहीं fail होते हैं
Step 5 → npm test (Jest unit tests, mocked providers)
Step 6 → npm run test:e2e (AppModule boot करके supertest, Postgres/Redis services पर)
Step 7 → e2e से पहले test DB पर migrations (TypeORM/Prisma) चलाओ
Step 8 → Production image build करो, चलाओ, /health hit करो
```

---

## 🟡 Real World Example
A Zerodha-style order-book backend built in NestJS has modules for Auth, Orders and Notifications. A refactor moved `NotificationsService` into its own module but forgot to `export` it. Unit tests (mocked) were green, but the e2e job crashed with "Nest can't resolve dependencies of the OrdersService", failing the PR in 3 minutes instead of failing the production container restart.

## 🟡 Real Example Hindi mein
Zerodha-जैसा order-book backend NestJS में बना है, जिसमें Auth, Orders और Notifications modules हैं। एक refactor ने `NotificationsService` को अपने module में डाला पर उसे `export` करना भूल गया। Unit tests (mocked) green थे, पर e2e job "Nest can't resolve dependencies of the OrdersService" से crash हुआ और PR 3 मिनट में fail हो गया, production container restart पर नहीं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/nest-ci.yml  (minimal NestJS CI)
name: Nest CI                       # workflow name
on: [push, pull_request]            # run on push and PR
jobs:                               # jobs
  test:                             # job id
    runs-on: ubuntu-latest          # runner
    steps:                          # steps
      - uses: actions/checkout@v4   # get code (example version)
      - uses: actions/setup-node@v4 # install Node
        with:                       # inputs
          node-version: 20          # Node 20
          cache: npm                # cache
      - run: npm ci                 # exact install
      - run: npm run lint           # lint (default Nest script may auto-fix; see note below)
      - run: npm run build          # nest build, catches TypeScript errors
      - run: npm test               # unit tests
```

Note: the Nest CLI template's `lint` script uses `--fix`; in CI prefer a separate non-mutating script such as `"lint:ci": "eslint \"{src,apps,libs,test}/**/*.ts\""`.

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/nest-ci.yml  (production NestJS CI)
name: Nest CI                       # workflow name
on:                                 # triggers
  push:                             # push
    branches: [main]                # main
  pull_request:                     # PRs
    branches: [main]                # to main
concurrency:                        # cancel stale
  group: nest-ci-${{ github.ref }}  # per ref
  cancel-in-progress: true          # newer wins
permissions:                        # least privilege
  contents: read                    # read only
jobs:                               # jobs
  verify:                           # lint + build + unit
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 12             # cap
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-node@v4 # node
        with:                       # inputs
          node-version-file: .nvmrc # pinned version
          cache: npm                # cache
      - run: npm ci                 # install
      - run: npm run lint:ci        # non-mutating lint script you add to package.json
      - run: npm run build          # compile TypeScript with nest build
      - run: npm test -- --ci --coverage  # Jest unit tests in CI mode
  e2e:                              # boots the real module graph
    needs: verify                   # after verify
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 15             # cap
    services:                       # sidecars
      postgres:                     # db
        image: postgres:16          # example tag
        env:                        # env
          POSTGRES_USER: nest       # user
          POSTGRES_PASSWORD: nest   # CI-only password
          POSTGRES_DB: nest_e2e     # db
        ports: ['5432:5432']        # port
        options: --health-cmd "pg_isready -U nest" --health-interval 5s --health-retries 10  # readiness
      redis:                        # queue/cache
        image: redis:7              # example tag
        ports: ['6379:6379']        # port
        options: --health-cmd "redis-cli ping" --health-interval 5s --health-retries 10  # readiness
    env:                            # env read by ConfigModule
      NODE_ENV: test                # test mode
      DATABASE_URL: postgres://nest:nest@localhost:5432/nest_e2e  # db url
      REDIS_URL: redis://localhost:6379  # redis url
      JWT_SECRET: ci-only-not-a-real-secret  # fake secret for tests
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-node@v4 # node
        with:                       # inputs
          node-version-file: .nvmrc # pinned
          cache: npm                # cache
      - run: npm ci                 # install
      - run: npm run migration:run  # your script, e.g. typeorm migration:run or prisma migrate deploy
      - run: npm run test:e2e       # Jest with test/jest-e2e.json
  docker:                           # image smoke test
    needs: e2e                      # after e2e
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 15             # cap
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - run: docker build -t nest-app:ci .  # build production image
      - name: Boot and probe health   # run container and curl it
        run: |                      # shell
          docker run -d --name api -p 3000:3000 -e NODE_ENV=production nest-app:ci  # start container
          for i in $(seq 1 15); do                              # wait loop up to ~30s
            curl -fs http://localhost:3000/health && exit 0     # /health endpoint (Terminus) returns 200
            sleep 2                                             # wait
          done                                                  # end loop
          docker logs api                                       # show logs for debugging
          exit 1                                                # fail the step
```

---

## 🟠 My Stack Integration
Nest runs as a container behind Nginx. Use a multi-stage Dockerfile: build with dev dependencies, ship only `dist/` and production dependencies. Nginx proxies `/api` to port 3000. Add a `/health` route (`@nestjs/terminus`) used by CI smoke test, Docker `HEALTHCHECK` and the deploy script.

```dockerfile
# Dockerfile for NestJS (copy-paste ready)
# Stage 1: build with all dependencies
FROM node:20-alpine AS build
# Working directory
WORKDIR /app
# Copy manifests for layer caching
COPY package*.json ./
# Install all deps (dev needed for nest build)
RUN npm ci
# Copy source
COPY . .
# Compile TypeScript to dist/
RUN npm run build

# Stage 2: runtime image
FROM node:20-alpine
# Working directory
WORKDIR /app
# Production mode
ENV NODE_ENV=production
# Copy manifests
COPY package*.json ./
# Install only production dependencies
RUN npm ci --omit=dev
# Copy compiled output
COPY --from=build /app/dist ./dist
# Run as non-root
USER node
# Nest default port
EXPOSE 3000
# Start compiled app
CMD ["node", "dist/main.js"]
```

Security: use a fake `JWT_SECRET` in CI, real secrets only in CD; run `npm audit --omit=dev`; keep the image non-root.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running only unit tests and skipping e2e, so DI wiring bugs reach production.
✅ Correct: Keep a small e2e suite that boots `AppModule` against real services.

❌ Mistake 2: Using the default `npm run lint` (which runs `--fix`) in CI.
✅ Correct: Add a read-only `lint:ci`; CI must check, not rewrite code.

❌ Mistake 3: `synchronize: true` (TypeORM) in the e2e DB config and then trusting it.
✅ Correct: Run real migrations in e2e so you test the same path as production.

❌ Mistake 4: Hardcoding `localhost` in the app config when the app runs inside a Docker network in production.
✅ Correct: Read hosts from env (`DATABASE_URL`) in both CI and production.

---

## 🧠 Tricky Interview Question
**Q:** Unit tests pass at 95 percent coverage and `nest build` succeeds, but the container exits immediately in production with a DI error. How did CI miss it, and what is the cheapest fix?

Answer: Unit tests construct providers manually or mock them, and `nest build` only type-checks; neither resolves the real dependency graph. The container fails at bootstrap when Nest instantiates modules. The cheapest fix is an e2e or smoke test that calls `NestFactory.create(AppModule)` (or `Test.createTestingModule({ imports: [AppModule] })`) in CI, or the Docker smoke test that starts the image and probes `/health`.

---

## ⚫ Interview Questions + Answers

Q1: Difference between unit and e2e tests in Nest?
A1: Unit tests isolate a class with mocked providers; e2e tests create the app from `AppModule`, use `supertest` over HTTP, and exercise guards, pipes, interceptors and DB together.

Q2: What does `nest build` produce?
A2: A compiled `dist/` folder (`dist/main.js`) using the TypeScript compiler (or SWC if configured).

Q3: How do you override a provider in e2e?
A3: `Test.createTestingModule({ imports: [AppModule] }).overrideProvider(MailService).useValue(fakeMail).compile()`.

Q4: How do you speed up e2e runs?
A4: Run with `--runInBand` only when needed for DB isolation, use transactions or truncate tables, cache dependencies, and keep the suite focused.

Q5: Why is `synchronize: true` risky?
A5: It auto-alters schema from entities and can drop columns; fine locally, dangerous in production, and it skips testing real migrations.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any Nest API with modules, guards and a database.
- You deploy the Docker image to a VPS/AWS.

❌ Avoid when:
- A tiny script project with no DI graph: simple Node CI is enough.
- Don't run e2e against production data or real third-party APIs.

---

## 📊 Visual Diagram
```
PR
 |
 v
[lint:ci -> nest build -> jest unit] --fail--> RED
 |
 v
[services: Postgres + Redis]
[migrations -> jest e2e (AppModule + supertest)] --fail--> RED (DI errors found here)
 |
 v
[docker build -> run -> GET /health] --fail--> RED
 |
 v
GREEN -> CD -> VPS (Nginx -> :3000)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DI | Dependency Injection | dependency injection |
| `AppModule` | Root Nest module | root module |
| e2e test | Tests through HTTP end to end | HTTP से end-to-end test |
| supertest | HTTP assertion library | HTTP assertions library |
| Terminus | Nest health-check module | health-check module |

---

## ⚡ 3-Line Summary
English: NestJS CI = lint, `nest build`, unit tests, e2e with real DB, docker smoke test.
English: Only e2e/smoke tests prove the DI graph boots.
English: Use a non-mutating lint script and real migrations in CI.

Hindi: NestJS CI = lint, `nest build`, unit tests, असली DB के साथ e2e, docker smoke test।
Hindi: सिर्फ e2e/smoke tests साबित करते हैं कि DI graph boot होता है।
Hindi: CI में non-mutating lint script और असली migrations इस्तेमाल करो।

---

## ➡️ Next Topic
**330. Monorepo CI Strategy** — one repo with api, web and shared packages needs smart, selective pipelines.
