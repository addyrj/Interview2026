# 361. Complete Node.js Pipeline (Test → Build → Push → Deploy)
# हिंदी में: पूरा Node.js Pipeline (Test → Build → Push → Deploy)

---

## 🔵 Simple Definition (English)
A complete Node.js pipeline is one GitHub Actions workflow that, on every push, installs dependencies, lints and tests the code, builds a Docker image, pushes it to a registry, and deploys it to a server (VPS or AWS), then verifies the release with a health check and notifies the team.

## 🔵 सरल परिभाषा (Hindi)
पूरा Node.js pipeline एक GitHub Actions workflow है जो हर push पर dependencies install करता है, code को lint और test करता है, Docker image बनाता है, registry में push करता है, server (VPS या AWS) पर deploy करता है, फिर health check से release verify करके team को बताता है।

---

## 🔴 Problem it Solves
Separate manual steps (test on laptop, build by hand, `scp` files, restart pm2) are slow, inconsistent and error prone. One forgotten step means broken production. A single pipeline gives repeatable, auditable releases: the same image that passed tests is what runs in production, with a documented path to rollback.

## 🔴 यह क्यों बना? (Hindi)
अलग-अलग manual steps (laptop पर test, हाथ से build, `scp` से files, pm2 restart) धीमे, असंगत और गलतियों वाले हैं। एक भी step भूलने पर production टूट सकता है। एक pipeline repeatable, audit योग्य releases देता है: जो image tests में pass हुई वही production में चलती है, और rollback का साफ रास्ता रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → git push / merge to main starts the workflow
Step 2 → Job "test": checkout, setup Node with cache, npm ci, lint, test (with Postgres service)
Step 3 → Job "build-push": Buildx builds image, tags with git SHA, pushes to GHCR
Step 4 → Job "deploy": needs both, uses "production" environment (approval optional)
Step 5 → SSH to VPS: login to registry, set new tag, docker compose pull + up -d
Step 6 → Health check on /health; automatic rollback to previous tag if it fails
Step 7 → Notify job posts success/failure to Slack with the run link
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → main पर git push / merge से workflow शुरू
Step 2 → Job "test": checkout, cache के साथ Node setup, npm ci, lint, test (Postgres service के साथ)
Step 3 → Job "build-push": Buildx image बनाता है, git SHA से tag, GHCR में push
Step 4 → Job "deploy": दोनों पर निर्भर, "production" environment (approval optional)
Step 5 → VPS पर SSH: registry login, नया tag set, docker compose pull + up -d
Step 6 → /health पर health check; fail हो तो पिछले tag पर अपने-आप rollback
Step 7 → Notify job Slack में run link के साथ success/failure भेजता है
```

---

## 🟡 Real World Example
A small team runs an Express + PostgreSQL order API on a 2 GB Ubuntu VPS behind Nginx. Before the pipeline, deploys took 25 minutes and happened only on Fridays. After this pipeline, any merged PR ships in about 4 minutes: tests run against a real Postgres service container, the image is 120 MB, and a failed health check restores the last version automatically. The team now deploys several times a day and the Friday ritual is gone.

## 🟡 Real Example Hindi mein
एक छोटी team 2 GB के Ubuntu VPS पर Nginx के पीछे Express + PostgreSQL order API चलाती है। Pipeline से पहले deploy में 25 मिनट लगते थे और सिर्फ शुक्रवार को होता था। इस pipeline के बाद कोई भी merged PR लगभग 4 मिनट में चला जाता है: tests असली Postgres service container पर चलते हैं, image 120 MB की है, और health check fail होने पर पिछला version अपने-आप लौट आता है। अब team दिन में कई बार deploy करती है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/basic.yml - minimal test + build check
name: Basic CI                          # workflow name
on:
  push:
    branches: [main]                    # run on pushes to main
  pull_request:                         # and on pull requests
jobs:
  test:
    runs-on: ubuntu-latest              # GitHub hosted Ubuntu runner
    steps:
      - uses: actions/checkout@v4       # fetch repository code
      - uses: actions/setup-node@v4     # install Node.js
        with:
          node-version: 20              # Node major version
          cache: npm                    # cache npm downloads between runs
      - run: npm ci                     # clean install from package-lock.json
      - run: npm test                   # run tests; failure stops the job
      - run: docker build -t myapp:ci . # check the Dockerfile builds
```

## 💻 Code / Config Example — Advanced

```dockerfile
# Dockerfile - multi-stage, non-root Node.js image
# ---- stage 1: production dependencies only ----
FROM node:20-alpine AS deps
WORKDIR /app
# manifests first so dependency layers are cached
COPY package.json package-lock.json ./
# install only runtime dependencies, from the lockfile
RUN npm ci --omit=dev

# ---- stage 2: final runtime image ----
FROM node:20-alpine AS runner
WORKDIR /app
# production mode enables Express optimizations
ENV NODE_ENV=production
# copy node_modules from stage 1
COPY --from=deps /app/node_modules ./node_modules
# copy application source (use .dockerignore to skip node_modules, .git, .env)
COPY . .
# the node image ships a non-root "node" user
USER node
# document the port
EXPOSE 3000
# built-in health check using Node fetch (Node 18+)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
# start the server directly (no npm) so SIGTERM reaches Node
CMD ["node", "src/server.js"]
```

```yaml
# .github/workflows/pipeline.yml - the full pipeline
name: Node.js CI/CD
on:
  push:
    branches: [main]                           # deploy from main only
  pull_request:                                # PRs run tests but never deploy
concurrency:
  group: pipeline-${{ github.ref }}            # one run per branch at a time
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}   # cancel old PR runs only
permissions:
  contents: read                               # least privilege default
env:
  IMAGE: ghcr.io/${{ github.repository }}/api  # image name (GHCR needs lowercase)
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:                                # real database for integration tests
        image: postgres:16-alpine              # example tag
        env:
          POSTGRES_PASSWORD: ci_only_password  # CI-only value
          POSTGRES_DB: app_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
    env:
      DATABASE_URL: postgres://postgres:ci_only_password@localhost:5432/app_test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci                            # reproducible install
      - run: npm run lint --if-present         # style and static checks
      - run: npm test                          # unit and integration tests
      - run: npm audit --omit=dev --audit-level=high   # fail on high severity prod vulns

  build-push:
    needs: test                                # only after tests pass
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write                          # push to GHCR
    outputs:
      image: ${{ steps.vars.outputs.image }}   # exact image reference for deploy job
    steps:
      - uses: actions/checkout@v4
      - id: vars                               # compute lowercase image + short sha
        run: echo "image=${IMAGE,,}:${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"
      - uses: docker/setup-buildx-action@v3    # modern builder with cache support
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.vars.outputs.image }}
          cache-from: type=gha                 # reuse cache from previous runs
          cache-to: type=gha,mode=max

  deploy:
    needs: build-push
    runs-on: ubuntu-latest
    environment: production                    # secrets + optional required reviewers
    concurrency:
      group: production-deploy                 # never deploy twice at once
      cancel-in-progress: false
    steps:
      - uses: appleboy/ssh-action@v1.0.3       # SSH deploy (example version)
        env:
          NEW_IMAGE: ${{ needs.build-push.outputs.image }}   # passed as env, not inline
          GHCR_TOKEN: ${{ secrets.GHCR_PULL_TOKEN }}
          GH_ACTOR: ${{ github.actor }}
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          envs: NEW_IMAGE,GHCR_TOKEN,GH_ACTOR  # forward these variables to the remote shell
          script: |
            set -euo pipefail
            cd /srv/myapp
            echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GH_ACTOR" --password-stdin
            PREV=$(grep '^API_IMAGE=' .env | cut -d= -f2-)          # remember old image
            sed -i "s|^API_IMAGE=.*|API_IMAGE=${NEW_IMAGE}|" .env   # set new image
            docker compose pull api
            docker compose run --rm api node src/migrate.js || { echo migration failed; exit 1; }
            docker compose up -d api
            for i in $(seq 1 20); do
              if curl -fsS http://127.0.0.1:3000/health > /dev/null; then echo healthy; exit 0; fi
              sleep 3
            done
            echo "unhealthy, rolling back to $PREV"
            sed -i "s|^API_IMAGE=.*|API_IMAGE=${PREV}|" .env
            docker compose up -d api
            exit 1

  notify:
    needs: [test, build-push, deploy]
    if: always() && github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - env:
          WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
          RESULT: ${{ needs.deploy.result }}
          URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        run: |
          curl -sS -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"${GITHUB_REPOSITORY} deploy: ${RESULT} - ${URL}\"}" "$WEBHOOK"
```

---

## 🟠 My Stack Integration
Server layout on the VPS and the Nginx front door that completes the picture:

```yaml
# /srv/myapp/docker-compose.yml (on the VPS)
services:
  api:
    image: ${API_IMAGE}                    # read from .env, updated by the pipeline
    restart: unless-stopped                # survive crashes and reboots
    env_file: .env                         # DATABASE_URL, JWT_SECRET, ...
    ports:
      - "127.0.0.1:3000:3000"              # reachable only from Nginx on the host
    depends_on:
      db:
        condition: service_healthy         # start after the DB is ready
  db:
    image: postgres:16-alpine              # example tag
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}    # from .env, chmod 600
    volumes:
      - pgdata:/var/lib/postgresql/data    # persistent data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10
volumes:
  pgdata:
```

```nginx
server {
  listen 443 ssl http2;                              # HTTPS
  server_name api.example.com;                       # your domain
  ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
  location / {
    proxy_pass http://127.0.0.1:3000;                # to the container
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

On AWS replace the SSH step with `aws-actions/configure-aws-credentials` (OIDC), push to ECR, and `aws ecs update-service --force-new-deployment`. Keep the same test and build jobs.

Security: use a deploy user with only Docker rights, a dedicated SSH key, `permissions:` set per job, GitHub Environments for secrets, OIDC instead of long-lived AWS keys, `npm audit`, non-root image, and port bound to `127.0.0.1`. Pin third-party actions to a version or commit SHA. The workflow and compose YAML were parsed for syntax, but nothing here was built or run against a real Docker daemon or server.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Building the image separately for deploy, so tested code differs from deployed code.
✅ Correct: Build once, tag with SHA, deploy that exact tag.

❌ Mistake 2: Deploying from pull requests.
✅ Correct: Gate build and deploy with `if: github.ref == 'refs/heads/main'` and push events.

❌ Mistake 3: Two deploys running at once.
✅ Correct: Use a `concurrency` group without cancel-in-progress for production.

❌ Mistake 4: No health check or rollback after `up -d`.
✅ Correct: Poll `/health` and restore the previous tag on failure.

❌ Mistake 5: Secrets in the repo or in image layers.
✅ Correct: Use GitHub Secrets/Environments and server `.env`; add `.dockerignore`.

---

## 🧠 Tricky Interview Question
The tests pass in CI, the image deploys, `docker compose up -d` returns success, but users get 502 from Nginx. What do you check?

Answer: `up -d` only means the container started, not that the app is ready. Check `docker compose logs api` (crash at boot, missing env var, DB not reachable), whether the app listens on `0.0.0.0` and the port Nginx proxies to, whether the published port binding matches, and `docker inspect` health status. This is why the pipeline polls `/health` after the deploy and fails (and rolls back) if it never passes.

---

## ⚫ Interview Questions + Answers

Q1: Why separate test, build-push and deploy jobs?
A1: Clear failure points, parallelism where possible, different permissions per job (only the build job can write packages), and the ability to re-run or gate each stage.

Q2: How do you pass the image tag between jobs?
A2: Job `outputs` read via `needs.<job>.outputs.<name>`.

Q3: How do you prevent a PR from deploying?
A3: Use `if:` conditions on branch and event, and protect the `production` environment with required reviewers.

Q4: How do you speed up the pipeline?
A4: Cache npm and Docker layers (`cache: npm`, `type=gha`), use `npm ci`, run independent jobs in parallel and skip unchanged paths with `paths:` filters.

Q5: How would this change for AWS ECS?
A5: Authenticate with OIDC, push to ECR, render a new task definition and call `ecs update-service`; ECS handles the rolling update and health checks.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You ship a Node.js API/service to a VPS, EC2 or ECS more than occasionally.
- You want every release tested, traceable and reversible.

❌ Avoid when:
- It is a throwaway prototype; a manual deploy is fine until it matters.
- The app is already on a platform with built-in CI/CD that meets your needs.

---

## 📊 Visual Diagram
```
 push/PR
   |
   v
 [test]  --lint, jest, npm audit, Postgres service
   |  pass (main only)
   v
 [build-push] --Buildx--> GHCR  api:abc1234
   |
   v
 [deploy] (env: production, concurrency lock)
   SSH -> docker compose pull -> migrate -> up -d -> /health
        |                                      |
        | healthy                              | unhealthy
        v                                      v
      done                              rollback to PREV tag
   |
   v
 [notify] Slack: success / failure + run link
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pipeline | Automated stages from commit to deploy | commit से deploy तक के automated चरण |
| Job outputs | Values passed between jobs | jobs के बीच भेजे जाने वाले मान |
| Environment | GitHub scope for secrets and approvals | secrets और approvals का scope |
| Service container | Helper container (DB) during tests | tests के दौरान सहायक container (DB) |
| Concurrency | Limit parallel runs | parallel runs की सीमा |

---

## ⚡ 3-Line Summary
English: One workflow tests, builds once, pushes a SHA-tagged image, deploys it and verifies with a health check.
Use job permissions, environments, concurrency and automatic rollback for safety.
Notify the team and keep secrets out of the repo and image.
Hindi: एक workflow test करता है, एक बार build करता है, SHA tag वाली image push करता है, deploy करता है और health check से verify करता है।
सुरक्षा के लिए job permissions, environments, concurrency और automatic rollback इस्तेमाल करो।
Team को notify करो और secrets को repo व image से बाहर रखो।

---

## ➡️ Next Topic
**362. Complete FastAPI Pipeline** — the same end-to-end flow for a Python backend with pytest, Alembic and Gunicorn.
