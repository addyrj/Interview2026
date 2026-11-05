---

# 362. Complete FastAPI Pipeline
# हिंदी में: पूरा FastAPI Pipeline

---

## 🔵 Simple Definition (English)
A complete FastAPI pipeline is one GitHub Actions workflow that takes a push, then lints, tests, builds a Docker image, scans it, pushes it to a registry and deploys it to your server. Every stage must pass before the next one runs. The goal: a `git push` becomes a safe production release with no manual steps.

## 🔵 सरल परिभाषा (Hindi)
Complete FastAPI pipeline एक GitHub Actions workflow है जो push मिलने पर lint, test, Docker image build, scan, registry में push और server पर deploy करता है। हर stage pass होने पर ही अगला चलता है। मकसद: `git push` से बिना manual काम के safe production release।

---

## 🔴 Problem it Solves
- Manual deploy: SSH into the VPS, `git pull`, `pip install`, restart. Easy to forget a step, and "works on my machine" bugs reach production.
- No automatic tests means a broken endpoint is found by users, not by CI.
- Python dependency drift: the server has different package versions than your laptop.
- No rollback path: you do not know which version is running.

## 🔴 यह क्यों बना? (Hindi)
- Manual deploy: VPS में SSH, `git pull`, `pip install`, restart। कोई step भूल सकते हैं और "मेरी machine पर चलता है" वाले bugs production तक पहुँचते हैं।
- Automatic tests नहीं तो टूटा endpoint users पकड़ते हैं, CI नहीं।
- Python dependency drift: server पर packages के version laptop से अलग।
- Rollback का रास्ता नहीं: पता नहीं कौन सा version चल रहा है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developer pushes to main (or opens a PR)
Step 2 → Job "test": install deps (pip cache), ruff lint, pytest with Postgres service
Step 3 → Job "build": docker buildx build, tag with git SHA, scan with Trivy
Step 4 → Push image to GHCR (only on main)
Step 5 → Job "deploy": SSH to VPS, docker pull new SHA, restart compose service
Step 6 → Health check /health; if it fails, roll back to previous SHA
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Developer main पर push करता है (या PR खोलता है)
Step 2 → Job "test": deps install (pip cache), ruff lint, Postgres service के साथ pytest
Step 3 → Job "build": docker buildx build, git SHA से tag, Trivy से scan
Step 4 → Image को GHCR में push (सिर्फ main पर)
Step 5 → Job "deploy": VPS पर SSH, नया SHA docker pull, compose service restart
Step 6 → /health check; fail हो तो पिछले SHA पर rollback
```

---

## 🟡 Real World Example
A fintech startup runs a FastAPI payments-status API on a single AWS EC2 box behind Nginx. Earlier, the founder deployed by hand at night. After this pipeline, every merged PR is tested against a real Postgres container, built once, and deployed in about 4 minutes. When a bad release returned HTTP 500 on `/health`, the script rolled back automatically and no customer noticed.

## 🟡 Real Example Hindi mein
एक fintech startup का FastAPI payments-status API एक AWS EC2 box पर Nginx के पीछे चलता है। पहले founder रात को हाथ से deploy करता था। इस pipeline के बाद हर merged PR असली Postgres container पर test होता है, एक बार build होता है और लगभग 4 मिनट में deploy हो जाता है। एक बुरे release में `/health` पर HTTP 500 आया तो script ने खुद rollback कर दिया और किसी customer को पता नहीं चला।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/fastapi-basic.yml
name: FastAPI CI                      # Name shown in the Actions tab
on:                                   # Trigger section
  push:                               # Run on every push
    branches: [main]                  # ...but only to main
  pull_request:                       # Also run on pull requests
jobs:                                 # All jobs live here
  test:                               # Job id
    runs-on: ubuntu-latest            # Runner OS
    steps:                            # Ordered steps
      - uses: actions/checkout@v4     # Get the repo code (example version)
      - uses: actions/setup-python@v5 # Install Python (example version)
        with:                         # Inputs for the action
          python-version: "3.12"      # Match your Dockerfile base image
          cache: pip                  # Cache pip downloads between runs
      - run: pip install -r requirements.txt   # Install app dependencies
      - run: pip install pytest ruff            # Install test and lint tools
      - run: ruff check .             # Lint: fail on style or obvious bugs
      - run: pytest -q                # Run unit tests quietly
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/fastapi-pipeline.yml
name: FastAPI Pipeline                # Workflow display name
on:                                   # Triggers
  push:
    branches: [main]                  # Deploy only from main
  pull_request:                       # PRs get test + build, no deploy
concurrency:                          # Avoid two deploys at once
  group: fastapi-${{ github.ref }}    # One run per branch
  cancel-in-progress: true            # Cancel older runs of same branch
permissions:                          # Least privilege for GITHUB_TOKEN
  contents: read                      # Read code
  packages: write                     # Push to GHCR
env:                                  # Shared variables
  IMAGE: ghcr.io/${{ github.repository }}/api   # Image name (lowercase repo needed)
jobs:
  test:
    runs-on: ubuntu-latest
    services:                         # Sidecar containers for tests
      postgres:
        image: postgres:16-alpine     # Real DB, not a mock
        env:
          POSTGRES_PASSWORD: test     # Throwaway CI password only
          POSTGRES_DB: app_test       # Test database name
        ports: ["5432:5432"]          # Expose to runner
        options: >-                   # Wait until DB is ready
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
    env:
      DATABASE_URL: postgresql://postgres:test@localhost:5432/app_test  # Used by app
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements.txt -r requirements-dev.txt   # Runtime + dev deps
      - run: ruff check .             # Lint
      - run: pytest --cov=app --cov-fail-under=70   # Tests with coverage gate
  build:
    needs: test                       # Only after tests pass
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.meta.outputs.tag }}   # Pass tag to deploy job
    steps:
      - uses: actions/checkout@v4
      - id: meta                      # Compute a lowercase image tag
        run: echo "tag=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"   # Short SHA
      - uses: docker/setup-buildx-action@v3   # Buildx for cache support
      - uses: docker/login-action@v3  # Log in to GHCR
        with:
          registry: ghcr.io
          username: ${{ github.actor }}        # Current user
          password: ${{ secrets.GITHUB_TOKEN }} # Built-in token
      - uses: docker/build-push-action@v6
        with:
          context: .                  # Build from repo root
          push: ${{ github.ref == 'refs/heads/main' }}   # Push only on main
          load: ${{ github.ref != 'refs/heads/main' }}   # Load locally on PRs for scan
          tags: ${{ env.IMAGE }}:${{ steps.meta.outputs.tag }}   # SHA tag
          cache-from: type=gha        # Reuse layers from Actions cache
          cache-to: type=gha,mode=max # Save layers for next run
      - uses: aquasecurity/trivy-action@0.28.0   # Image vulnerability scan (example version)
        with:
          image-ref: ${{ env.IMAGE }}:${{ steps.meta.outputs.tag }}
          severity: CRITICAL          # Fail only on critical CVEs
          exit-code: "1"              # Non-zero exit fails the job
  deploy:
    if: github.ref == 'refs/heads/main'    # Never deploy PRs
    needs: build
    runs-on: ubuntu-latest
    environment: production           # Enables approvals and env secrets
    steps:
      - uses: appleboy/ssh-action@v1.0.3   # SSH into VPS (example version)
        with:
          host: ${{ secrets.VPS_HOST }}    # Server IP from secrets
          username: deploy                 # Non-root deploy user
          key: ${{ secrets.VPS_SSH_KEY }}  # Private key from secrets
          script: |                        # Commands run on the server
            set -e
            cd /opt/api
            PREV=$(cat .current_tag || echo none)       # Remember old version
            echo "${{ secrets.GHCR_PULL_TOKEN }}" | docker login ghcr.io -u deploy --password-stdin
            TAG=${{ needs.build.outputs.tag }} docker compose pull api
            TAG=${{ needs.build.outputs.tag }} docker compose up -d api
            sleep 8
            if curl -fs http://127.0.0.1:8000/health; then
              echo "${{ needs.build.outputs.tag }}" > .current_tag   # Record success
            else
              TAG=$PREV docker compose up -d api        # Roll back
              exit 1
            fi
```

---

## 🟠 My Stack Integration
The matching `Dockerfile` for FastAPI plus the compose file on the VPS that Nginx proxies to.

```yaml
# /opt/api/docker-compose.yml  (on the VPS)
services:
  api:                                          # FastAPI service
    image: ghcr.io/youruser/yourrepo/api:${TAG} # TAG comes from the deploy script
    restart: unless-stopped                     # Come back after reboot or crash
    env_file: .env                              # Secrets stay on the server
    ports:
      - "127.0.0.1:8000:8000"                   # Only Nginx can reach it
    healthcheck:                                # Docker-level health
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 15s
      timeout: 3s
      retries: 3
```

```dockerfile
# Dockerfile (repo root)
# Small base image
FROM python:3.12-slim
# App directory
WORKDIR /app
# curl is needed for the container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
# Copy deps first so the layer is cached
COPY requirements.txt .
# Install deps without pip cache
RUN pip install --no-cache-dir -r requirements.txt
# Copy source last
COPY app ./app
# Create a non-root user
RUN useradd -m appuser
# Never run as root
USER appuser
# Start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Nginx stays unchanged: `proxy_pass http://127.0.0.1:8000;`. Not built or run locally in these notes, so test on a staging box first.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Tagging only `latest`, so rollback is impossible.
✅ Correct: Tag with the git SHA and keep the last good tag on the server.

❌ Mistake 2: Running tests against SQLite while production uses Postgres.
✅ Correct: Use a `services: postgres` container in CI.

❌ Mistake 3: Putting `.env` or the DB password inside the image.
✅ Correct: Keep `.env` on the server or in GitHub Secrets and pass it at runtime.

❌ Mistake 4: Deploying on `pull_request` events.
✅ Correct: Guard the deploy job with `if: github.ref == 'refs/heads/main'`.

Security: use a non-root container user, a dedicated `deploy` SSH user, scoped pull tokens, and Trivy scans. Never `echo` secrets without GitHub masking.

---

## 🧠 Tricky Interview Question
Your pipeline is green, the container started, but users see 502 from Nginx for 10 seconds after each deploy. Why, and how do you fix it?

Answer: `docker compose up -d` returns as soon as the container starts, not when Uvicorn is ready. Nginx forwards to a port that is not listening yet. Fix with a healthcheck plus waiting for healthy status (or a retry loop on `/health`), and for true zero downtime run two replicas (blue/green) and switch Nginx upstream only after the new one is healthy.

---

## ⚫ Interview Questions + Answers

Q1: Why use `needs:` between jobs?
A1: It enforces order and stops later jobs if an earlier one fails, so a failing test never produces a deployed image.

Q2: Why a short git SHA as the image tag?
A2: It is unique, traceable to a commit, and enables exact rollbacks. `latest` is mutable and hides what is running.

Q3: How do you speed up builds?
A3: Order Dockerfile layers (deps before source), use `cache-from/cache-to type=gha`, and use pip caching in `setup-python`.

Q4: How do secrets reach the server safely?
A4: GitHub Secrets for the SSH key and pull token; app secrets stay in a server-side `.env` or AWS Secrets Manager, never in the image or repo.

Q5: What does `concurrency` do here?
A5: It prevents overlapping runs on the same ref so two deploys do not fight over the same container.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You deploy a containerised FastAPI app to one or a few VPS/EC2 hosts.
- You want repeatable, audited releases with tests and scans.

❌ Avoid when:
- You run many services on Kubernetes (use GitOps or Helm-based deploy instead).
- It is a throwaway prototype where setup cost exceeds value.

---

## 📊 Visual Diagram
```
 git push main
      |
      v
 +---------+   +-----------------+   +------------------+
 |  test   |-->| build + scan    |-->| push to GHCR     |
 | ruff    |   | buildx, Trivy   |   | tag = git SHA    |
 | pytest  |   +-----------------+   +--------+---------+
 +---------+                                  |
                                              v
                                   +--------------------+
                                   | deploy via SSH     |
                                   | pull, up -d        |
                                   +---------+----------+
                                             |
                          health OK? --yes-> done
                                    --no--> rollback to previous SHA
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pipeline | Ordered automated stages | क्रमबद्ध automatic stages |
| Service container | Sidecar like Postgres in CI | CI में साथ चलने वाला container |
| Image tag | Version label of an image | Image का version label |
| Rollback | Return to previous good version | पिछले सही version पर वापसी |
| Healthcheck | Probe that proves app is ready | App तैयार है यह जाँचने वाला probe |

---

## ⚡ 3-Line Summary
English: One workflow runs lint, tests, build, scan, push and deploy in order.
English: Tag images with the git SHA and health-check after deploy for safe rollback.
English: Keep secrets out of images; deploy only from main.
Hindi: एक workflow क्रम से lint, test, build, scan, push और deploy चलाता है।
Hindi: Image को git SHA से tag करें और deploy के बाद health check से safe rollback रखें।
Hindi: Secrets image में नहीं; deploy सिर्फ main से।

---

## ➡️ Next Topic
363. Complete React Pipeline: after the API, we build and ship the front-end the same way.
