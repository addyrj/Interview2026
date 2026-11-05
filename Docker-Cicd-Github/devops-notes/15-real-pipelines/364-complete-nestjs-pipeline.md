---

# 364. Complete NestJS Pipeline
# हिंदी में: पूरा NestJS Pipeline

---

## 🔵 Simple Definition (English)
A NestJS pipeline lints, runs unit and e2e tests (with a real database), compiles TypeScript to `dist/`, builds a small production Docker image and deploys it. NestJS needs a build step (`nest build`), so the runtime image should contain only compiled JS and production dependencies.

## 🔵 सरल परिभाषा (Hindi)
NestJS pipeline lint करता है, असली database के साथ unit और e2e tests चलाता है, TypeScript को `dist/` में compile करता है, छोटी production Docker image बनाता है और deploy करता है। NestJS में build step (`nest build`) चाहिए, इसलिए runtime image में सिर्फ compiled JS और production dependencies होनी चाहिए।

---

## 🔴 Problem it Solves
- Running `ts-node` or `npm run start:dev` in production: slow and heavy.
- devDependencies (jest, typescript, eslint) shipped in the image: big and risky.
- e2e tests mocked away, so DB/migration bugs appear only in production.
- Environment variables missing at boot cause crashes after deploy.

## 🔴 यह क्यों बना? (Hindi)
- Production में `ts-node` या `npm run start:dev` चलाना: धीमा और भारी।
- devDependencies (jest, typescript, eslint) image में चली जाती हैं: बड़ी और risky।
- e2e tests mock हो जाते हैं, इसलिए DB/migration bugs production में दिखते हैं।
- Environment variables गायब हों तो deploy के बाद app crash होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Trigger on push/PR
Step 2 → npm ci, eslint, unit tests (jest)
Step 3 → Start Postgres + Redis service containers, run e2e tests
Step 4 → nest build -> dist/
Step 5 → Docker multi-stage: build stage, prune dev deps, runtime stage
Step 6 → Push image tagged with SHA; deploy; run migrations; health check
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Push/PR पर trigger
Step 2 → npm ci, eslint, unit tests (jest)
Step 3 → Postgres + Redis service containers चालू करके e2e tests
Step 4 → nest build -> dist/
Step 5 → Docker multi-stage: build stage, dev deps हटाना, runtime stage
Step 6 → SHA tag के साथ image push; deploy; migrations; health check
```

---

## 🟡 Real World Example
A food-delivery startup (Swiggy-like) runs an NestJS orders service. Before the pipeline, a dev deployed with a missing `JWT_SECRET`; the app booted but every login failed. Now the e2e job starts the app with required env vars, and the app uses a config validation schema, so a missing variable fails CI and also fails the container healthcheck at deploy, which triggers a rollback.

## 🟡 Real Example Hindi mein
एक food-delivery startup (Swiggy जैसा) NestJS orders service चलाता है। Pipeline से पहले एक dev ने `JWT_SECRET` के बिना deploy किया; app चालू हुआ पर हर login fail था। अब e2e job ज़रूरी env vars के साथ app चलाता है और app config validation schema इस्तेमाल करता है, इसलिए missing variable पर CI fail होता है और deploy में container healthcheck भी fail होकर rollback करता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/nest-basic.yml
name: NestJS CI                        # Workflow name
on: [push, pull_request]               # Run on push and PRs
jobs:
  ci:                                  # Single job
    runs-on: ubuntu-latest             # Runner OS
    steps:
      - uses: actions/checkout@v4      # Get code
      - uses: actions/setup-node@v4    # Node setup
        with:
          node-version: 20             # Same as Dockerfile
          cache: npm                   # Cache npm downloads
      - run: npm ci                    # Reproducible install
      - run: npm run lint              # ESLint
      - run: npm test                  # Unit tests
      - run: npm run build             # nest build -> dist/
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/nest-pipeline.yml
name: NestJS Pipeline
on:
  push:
    branches: [main]
  pull_request:
concurrency:
  group: nest-${{ github.ref }}
  cancel-in-progress: true
permissions:
  contents: read
  packages: write
env:
  IMAGE: ghcr.io/${{ github.repository }}/orders-api   # Must be lowercase
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: test      # CI-only password
          POSTGRES_DB: orders_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s --health-timeout 5s --health-retries 10
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 5s --health-timeout 5s --health-retries 10
    env:
      DATABASE_URL: postgresql://postgres:test@localhost:5432/orders_test
      REDIS_URL: redis://localhost:6379
      JWT_SECRET: ci-only-secret       # Throwaway test value
      NODE_ENV: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --ci --coverage      # Unit tests with coverage
      - run: npm run migration:run            # Apply migrations to the test DB (your script)
      - run: npm run test:e2e                 # e2e against real Postgres and Redis
  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.meta.outputs.tag }}
    steps:
      - uses: actions/checkout@v4
      - id: meta
        run: echo "tag=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' }}   # No push for PRs
          tags: ${{ env.IMAGE }}:${{ steps.meta.outputs.tag }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
  deploy:
    if: github.ref == 'refs/heads/main'
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: deploy
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            set -e
            cd /opt/orders
            export TAG=${{ needs.build.outputs.tag }}
            docker compose pull api                      # Fetch new image
            docker compose run --rm api node dist/migrate.js   # Migrations first (your script)
            docker compose up -d api                     # Swap container
            for i in 1 2 3 4 5 6; do                     # Wait for health up to ~30s
              curl -fs http://127.0.0.1:3000/health && exit 0
              sleep 5
            done
            echo "Health check failed" && exit 1
```

---

## 🟠 My Stack Integration
Multi-stage Dockerfile for NestJS and Nginx in front.

```dockerfile
# Stage 1: install all deps and compile
FROM node:20-alpine AS build
# Working directory
WORKDIR /app
# Manifests first for caching
COPY package.json package-lock.json ./
# Install everything, including dev deps
RUN npm ci
# Copy source
COPY . .
# Compile TypeScript to dist/
RUN npm run build
# Remove dev dependencies
RUN npm prune --omit=dev
# Stage 2: runtime
FROM node:20-alpine AS runtime
# Production mode
ENV NODE_ENV=production
# Working directory
WORKDIR /app
# Copy only what runtime needs
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./package.json
# Use built-in non-root node user
USER node
# App port
EXPOSE 3000
# Start compiled app
CMD ["node", "dist/main.js"]
```

```yaml
# /opt/orders/docker-compose.yml on the VPS
services:
  api:
    image: ghcr.io/youruser/yourrepo/orders-api:${TAG}   # Version from deploy script
    restart: unless-stopped                              # Auto restart
    env_file: .env                                       # Server-side secrets
    ports: ["127.0.0.1:3000:3000"]                       # Nginx proxies here
```

Not built or run locally. `migrate.js` and `migration:run` are placeholders for your own migration tooling (TypeORM/Prisma).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running `nest start` in the container.
✅ Correct: `node dist/main.js` from a compiled build.

❌ Mistake 2: Shipping devDependencies.
✅ Correct: `npm prune --omit=dev` in the build stage.

❌ Mistake 3: Running migrations from every replica at start.
✅ Correct: Run once in a single deploy step before swapping traffic.

❌ Mistake 4: No `/health` endpoint, so deploys cannot be verified.
✅ Correct: Add `@nestjs/terminus` health checks.

Security: run as `node` user, validate env with Joi/zod, keep `.env` off the image, and run `npm audit`.

---

## 🧠 Tricky Interview Question
e2e tests pass in CI but the deployed app fails with "relation does not exist". Why?

Answer: CI created the schema (migration or `synchronize: true`), while production DB never got the migration. Never rely on `synchronize` in prod. Run migrations explicitly in the deploy step, before starting the new version, and make migrations backward compatible.

---

## ⚫ Interview Questions + Answers

Q1: Why prune dev dependencies?
A1: Smaller image, faster pulls, fewer vulnerable packages.

Q2: Unit vs e2e in CI?
A2: Unit tests isolate logic with mocks (fast). e2e boots the app against real services to catch wiring, DB and auth bugs.

Q3: Why `services:` instead of docker compose in CI?
A3: GitHub starts and health-checks them before steps run, with less YAML and simple localhost access.

Q4: How to avoid downtime while migrating?
A4: Use expand/contract migrations: add columns first, deploy code, remove old columns later.

Q5: How do you pass secrets at runtime?
A5: `env_file` on the server, Docker secrets, or AWS Secrets Manager. Not baked via `ARG`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- NestJS/Node API deployed as a container to VPS or ECS.

❌ Avoid when:
- Serverless deploys (use SAM/Serverless Framework flow instead).

---

## 📊 Visual Diagram
```
 push --> lint --> unit --> [Postgres+Redis] e2e
                                  |
                             nest build
                                  |
                  Docker: build stage -> prune -> runtime (USER node)
                                  |
                              GHCR (SHA)
                                  |
              VPS: pull -> migrate -> up -d -> /health -> OK / fail
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| e2e test | Test whole app with real services | असली services के साथ पूरा test |
| Migration | Versioned DB schema change | DB schema का versioned बदलाव |
| Prune | Remove dev packages | Dev packages हटाना |
| Terminus | NestJS health check module | NestJS का health check module |
| Expand/contract | Safe schema change pattern | सुरक्षित schema बदलाव का तरीका |

---

## ⚡ 3-Line Summary
English: Lint, unit, e2e with real DB, build, containerise, deploy.
English: Runtime image has only dist and production dependencies.
English: Run migrations once, then health-check the new version.
Hindi: Lint, unit, असली DB के साथ e2e, build, container, deploy।
Hindi: Runtime image में सिर्फ dist और production dependencies।
Hindi: Migrations एक बार चलाएँ, फिर नए version का health check करें।

---

## ➡️ Next Topic
365. Complete Full Stack Pipeline: combine React, API and database into one release flow.
