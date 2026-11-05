---

# 365. Complete Full Stack Pipeline
# हिंदी में: पूरा Full Stack Pipeline

---

## 🔵 Simple Definition (English)
A full stack pipeline builds and releases the frontend (React), backend (FastAPI or Node) and their infrastructure together. It builds both images in parallel, tests them together with a compose-based smoke test, and deploys them as one versioned release behind Nginx.

## 🔵 सरल परिभाषा (Hindi)
Full stack pipeline frontend (React), backend (FastAPI या Node) और उनका infrastructure एक साथ build और release करता है। दोनों images parallel build होती हैं, compose-आधारित smoke test से साथ में test होती हैं और Nginx के पीछे एक versioned release की तरह deploy होती हैं।

---

## 🔴 Problem it Solves
- Frontend and backend deployed separately: for some minutes the UI calls an API field that does not exist yet.
- Each repo has its own scripts, so release knowledge lives in someone's head.
- Integration bugs (CORS, wrong API URL, cookie domain) appear only in production.

## 🔴 यह क्यों बना? (Hindi)
- Frontend और backend अलग-अलग deploy होने से कुछ मिनट UI ऐसे API field को call करता है जो अभी है ही नहीं।
- हर repo की अपनी scripts, release का ज्ञान किसी के दिमाग में।
- Integration bugs (CORS, गलत API URL, cookie domain) सिर्फ production में दिखते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Push to main
Step 2 → Parallel jobs: backend-test, frontend-test
Step 3 → Parallel builds: api image + web image, same SHA tag
Step 4 → Smoke test: docker compose up (api+db+web), curl through Nginx
Step 5 → Push both images
Step 6 → Deploy: backend first (backward compatible), then frontend
Step 7 → Post-deploy checks, auto rollback on failure
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → main पर push
Step 2 → Parallel jobs: backend-test, frontend-test
Step 3 → Parallel builds: api image + web image, एक ही SHA tag
Step 4 → Smoke test: docker compose up (api+db+web), Nginx के through curl
Step 5 → दोनों images push
Step 6 → Deploy: पहले backend (backward compatible), फिर frontend
Step 7 → Post-deploy checks, fail पर auto rollback
```

---

## 🟡 Real World Example
A Zomato-like restaurant dashboard has a React UI and a FastAPI backend. A release adds a new "delivery_fee" field. The pipeline deploys the API first (it still serves the old field too), then the UI that reads the new field. Customers never see a half-working page. A smoke test in CI caught a CORS misconfiguration before it hit production.

## 🟡 Real Example Hindi mein
Zomato जैसे restaurant dashboard में React UI और FastAPI backend है। एक release में नया "delivery_fee" field आता है। Pipeline पहले API deploy करता है (जो पुराना field भी देता है), फिर वह UI जो नया field पढ़ता है। Customers को आधा-टूटा page कभी नहीं दिखता। CI के smoke test ने production से पहले CORS की गलत setting पकड़ ली।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/fullstack-basic.yml
name: Fullstack CI                      # Name
on: [push, pull_request]                # Triggers
jobs:
  backend:                              # Backend job
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend      # All run steps start here
    steps:
      - uses: actions/checkout@v4       # Get code
      - uses: actions/setup-python@v5   # Python
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt pytest   # Install deps
      - run: pytest -q                  # Test
  frontend:                             # Frontend job runs in parallel
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: frontend/package-lock.json   # Lockfile in subfolder
      - run: npm ci                     # Install
      - run: npm run build              # Build
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/fullstack-pipeline.yml
name: Fullstack Pipeline
on:
  push:
    branches: [main]
  pull_request:
concurrency:
  group: fullstack-${{ github.ref }}
  cancel-in-progress: true
permissions:
  contents: read
  packages: write
env:
  REGISTRY: ghcr.io
  API_IMAGE: ghcr.io/${{ github.repository }}/api   # Lowercase owner/repo required
  WEB_IMAGE: ghcr.io/${{ github.repository }}/web
jobs:
  tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        part: [backend, frontend]       # One job per part, in parallel
    steps:
      - uses: actions/checkout@v4
      - if: matrix.part == 'backend'    # Backend-only steps
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - if: matrix.part == 'backend'
        run: pip install -r backend/requirements.txt pytest && pytest -q backend
      - if: matrix.part == 'frontend'   # Frontend-only steps
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - if: matrix.part == 'frontend'
        run: cd frontend && npm ci && npm run lint && npm test -- --run
  images:
    needs: tests
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
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build api (local, for smoke test)
        uses: docker/build-push-action@v6
        with:
          context: backend
          load: true                     # Keep image in local Docker
          tags: api:ci
          cache-from: type=gha,scope=api
          cache-to: type=gha,scope=api,mode=max
      - name: Build web (local, for smoke test)
        uses: docker/build-push-action@v6
        with:
          context: frontend
          load: true
          tags: web:ci
          cache-from: type=gha,scope=web
          cache-to: type=gha,scope=web,mode=max
      - name: Smoke test with compose
        run: |
          docker compose -f deploy/compose.ci.yml up -d       # api + db + web
          for i in $(seq 1 20); do                             # Wait up to 40s
            curl -fs http://localhost:8080/api/health && break
            sleep 2
          done
          curl -fs http://localhost:8080/ | grep -qi "<div id=\"root\"" # SPA is served
          docker compose -f deploy/compose.ci.yml down -v      # Cleanup
      - name: Tag and push (main only)
        if: github.ref == 'refs/heads/main'
        run: |
          docker tag api:ci $API_IMAGE:${{ steps.meta.outputs.tag }}
          docker tag web:ci $WEB_IMAGE:${{ steps.meta.outputs.tag }}
          docker push $API_IMAGE:${{ steps.meta.outputs.tag }}
          docker push $WEB_IMAGE:${{ steps.meta.outputs.tag }}
  deploy:
    if: github.ref == 'refs/heads/main'
    needs: images
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
            cd /opt/app
            export TAG=${{ needs.images.outputs.tag }}
            docker compose pull                      # Pull api and web
            docker compose up -d api                 # Backend first
            sleep 8 && curl -fs http://127.0.0.1:8000/health
            docker compose up -d web                 # Then frontend
            curl -fs http://127.0.0.1:8080/ > /dev/null
```

---

## 🟠 My Stack Integration
`deploy/compose.ci.yml` used for the smoke test and similar on the VPS. Nginx on the host fronts port 8080.

```yaml
# deploy/compose.ci.yml
services:
  db:
    image: postgres:16-alpine             # Test DB
    environment:
      POSTGRES_PASSWORD: ci               # CI-only
      POSTGRES_DB: app
  api:
    image: api:ci                         # Locally built image
    environment:
      DATABASE_URL: postgresql://postgres:ci@db:5432/app
    depends_on: [db]                      # Start order only, app must retry DB
  web:
    image: web:ci                         # Nginx serving React
    ports: ["8080:80"]                    # Exposed to the runner
    depends_on: [api]
```

Web's Nginx config proxies `/api/` to `http://api:8000/`. This was not run locally; verify the proxy path matches your API prefix.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deploying frontend before backend.
✅ Correct: Backend first, backward compatible; frontend after.

❌ Mistake 2: Different tags for api and web, making releases untraceable.
✅ Correct: One SHA tag for the whole release.

❌ Mistake 3: `depends_on` assumed to wait for DB readiness.
✅ Correct: Add a DB healthcheck with `condition: service_healthy` or app retry.

❌ Mistake 4: Hard-coding the API host in the bundle.
✅ Correct: Use relative `/api` behind Nginx so the same image works everywhere.

Security: CORS allow-list instead of `*`, HTTPS only, cookies `Secure; HttpOnly; SameSite`.

---

## 🧠 Tricky Interview Question
How do you release a breaking API change without breaking users who still have the old frontend open in their browser?

Answer: Do not break it in one step. Use expand/contract: ship the API supporting both old and new shape (or versioned `/v2`), deploy the frontend, wait until old clients age out, then remove the old shape in a later release.

---

## ⚫ Interview Questions + Answers

Q1: Monorepo or separate repos for full stack?
A1: Monorepo makes atomic changes and a single pipeline easy; separate repos give independent release cycles. Choose by team size and coupling.

Q2: Why a smoke test in CI?
A2: Unit tests do not prove containers talk to each other. The smoke test checks Nginx, API, DB wiring and static serving.

Q3: How to run the matrix efficiently?
A3: Use `strategy.matrix` and per-part cache scopes to avoid cache collisions.

Q4: What if only the frontend changed?
A4: Add `paths:` filters or `dorny/paths-filter` to skip the backend job (see Monorepo topic).

Q5: How do you roll back both?
A5: Redeploy the previous SHA tag for both; images are immutable so it is deterministic.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- UI and API ship together on the same VPS/host.

❌ Avoid when:
- Teams own separately versioned services with different cadences (use per-service pipelines).

---

## 📊 Visual Diagram
```
        push main
           |
   +-------+--------+
   |                |
[backend tests]  [frontend tests]
   |                |
   +-------+--------+
           v
  build api:ci + web:ci  (same SHA)
           v
  compose smoke test (db+api+web)
           v
  push GHCR --> VPS: api up -> health -> web up
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Smoke test | Quick check the system boots | Quick जाँच कि system चालू होता है |
| Matrix | Run a job with variations | एक job को अलग variations के साथ चलाना |
| Backward compatible | Old clients still work | पुराने clients भी चलते हैं |
| CORS | Browser cross-origin rule | Browser का cross-origin नियम |
| Atomic release | One version for all parts | सब parts का एक version |

---

## ⚡ 3-Line Summary
English: Test and build UI and API in parallel with one shared SHA tag.
English: Smoke test them together with compose before pushing.
English: Deploy backend first, frontend second, roll back by tag.
Hindi: UI और API को parallel test और build करें, एक SHA tag के साथ।
Hindi: Push से पहले compose में साथ smoke test करें।
Hindi: पहले backend, फिर frontend deploy; tag से rollback।

---

## ➡️ Next Topic
366. Monorepo Pipeline Strategy: run only what changed when many apps share a repo.
