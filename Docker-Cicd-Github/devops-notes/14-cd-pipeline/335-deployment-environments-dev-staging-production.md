# 335. Deployment Environments (dev, staging, production)
# हिंदी में: Deployment Environments (dev, staging, production)

---

## 🔵 Simple Definition (English)
**Deployment environments** are separate places where the same application runs at different stages of confidence: **dev** (latest work, breaks often), **staging** (production copy used for final checks), and **production** (real users). The code and image are identical; only configuration, data and access differ.

## 🔵 सरल परिभाषा (Hindi)
**Deployment environments** अलग-अलग जगहें हैं जहाँ वही application भरोसे के अलग स्तरों पर चलती है: **dev** (नवीनतम काम, अक्सर टूटता है), **staging** (production की copy, अंतिम जाँच के लिए) और **production** (असली users)। Code और image एक ही रहते हैं; सिर्फ configuration, data और access अलग होते हैं।

---

## 🔴 Problem it Solves
Testing directly on production risks real users and money; testing only on a laptop hides differences (different DB version, no Nginx, no HTTPS). Without staging, the first time a migration meets production-sized data is on production. Environments give a safe path: try early in dev, rehearse the exact release in staging, then ship to production.

## 🔴 यह क्यों बना? (Hindi)
सीधे production पर test करना असली users और पैसे को जोखिम में डालता है; सिर्फ laptop पर test करने से अंतर छुप जाते हैं (अलग DB version, Nginx नहीं, HTTPS नहीं)। Staging न हो तो migration पहली बार production-आकार के data से production पर ही मिलती है। Environments सुरक्षित रास्ता देते हैं: dev में जल्दी आज़माओ, staging में असली release का rehearsal करो, फिर production में भेजो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define environments in GitHub: dev, staging, production (each with own secrets/vars)
Step 2 → Build the image ONCE, tagged by commit SHA
Step 3 → dev: auto-deploy every push to a feature/develop branch (or each PR preview)
Step 4 → staging: auto-deploy on merge to main, run smoke + e2e tests against it
Step 5 → production: deploy the SAME image after approval, from main/tags only
Step 6 → Configuration differs via env vars (DATABASE_URL, API_URL, LOG_LEVEL), never via code changes
Step 7 → Data differs: dev = fake, staging = anonymized copy, production = real
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → GitHub में environments बनाओ: dev, staging, production (हर एक के अपने secrets/vars)
Step 2 → Image सिर्फ एक बार बनाओ, commit SHA से tag
Step 3 → dev: feature/develop branch के हर push पर auto-deploy (या हर PR का preview)
Step 4 → staging: main पर merge होते ही auto-deploy, उसके ख़िलाफ़ smoke + e2e tests
Step 5 → production: वही image approval के बाद, सिर्फ main/tags से deploy
Step 6 → अंतर env vars (DATABASE_URL, API_URL, LOG_LEVEL) से, code बदलकर कभी नहीं
Step 7 → Data अलग: dev = नकली, staging = anonymized copy, production = असली
```

---

## 🟡 Real World Example
A Swiggy-like team runs the order API on three small VPS hosts. Developers deploy their work to `dev` many times a day. Each merge to main goes to `staging`, where QA runs a checkout flow against an anonymized copy of last week's data. One release failed staging because a new index took 40 minutes on realistic data; they changed the migration plan before it ever touched production. Production receives only the staged, approved image.

## 🟡 Real Example Hindi mein
Swiggy-जैसी टीम तीन छोटे VPS hosts पर order API चलाती है। Developers दिन में कई बार अपना काम `dev` पर deploy करते हैं। main पर हर merge `staging` पर जाता है, जहाँ QA पिछले हफ्ते के anonymized data की copy पर checkout flow चलाता है। एक release staging पर fail हुई क्योंकि नया index असली-जैसे data पर 40 मिनट ले रहा था; production को छूने से पहले ही migration plan बदल दिया गया। Production को सिर्फ staged, approved image मिलती है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/deploy-env.yml  (one reusable job, three environments)
name: Deploy Environments           # workflow name
on:                                 # triggers
  push:                             # push
    branches: [develop, main]       # develop -> dev, main -> staging
jobs:                               # jobs
  deploy:                           # job id
    runs-on: ubuntu-latest          # runner
    environment: ${{ github.ref_name == 'main' && 'staging' || 'dev' }}  # pick environment by branch
    steps:                          # steps
      - run: echo "Deploying ${{ github.sha }} to ${{ vars.APP_ENV }}"  # APP_ENV is an environment variable
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/pipeline.yml  (build once -> dev -> staging -> production)
name: Pipeline                      # workflow name
on:                                 # triggers
  push:                             # push
    branches: [main]                # main
concurrency:                        # no overlapping pipelines
  group: pipeline                   # lane
  cancel-in-progress: false         # queue
permissions:                        # least privilege
  contents: read                    # read repo
  packages: write                   # push image
jobs:                               # jobs
  build:                            # build once
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 20             # cap
    outputs:                        # pass image reference on
      image: ${{ steps.meta.outputs.image }}  # full image name with tag
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - id: meta                    # step id
        run: echo "image=ghcr.io/acme/app:${GITHUB_SHA}" >> "$GITHUB_OUTPUT"  # example repo path, lowercase
      - uses: docker/login-action@v3  # login
        with:                       # inputs
          registry: ghcr.io         # registry
          username: ${{ github.actor }}  # user
          password: ${{ secrets.GITHUB_TOKEN }}  # token
      - uses: docker/build-push-action@v6  # build+push
        with:                       # inputs
          context: .                # context
          push: true                # push
          tags: ${{ steps.meta.outputs.image }}  # SHA tag
  dev:                              # lowest-risk environment
    needs: build                    # after image exists
    runs-on: ubuntu-latest          # runner
    environment: dev                # no reviewers
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - run: ./deploy/deploy.sh "${{ needs.build.outputs.image }}"  # same script for every environment
        env:                        # env
          HOST: ${{ vars.HOST }}              # environment-specific host
          SSH_KEY: ${{ secrets.SSH_KEY }}     # environment-specific key
          APP_ENV: ${{ vars.APP_ENV }}        # "dev"
  staging:                          # production rehearsal
    needs: [build, dev]             # after dev success
    runs-on: ubuntu-latest          # runner
    environment: staging            # optional reviewers
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - run: ./deploy/deploy.sh "${{ needs.build.outputs.image }}"  # same script
        env:                        # env
          HOST: ${{ vars.HOST }}              # staging host
          SSH_KEY: ${{ secrets.SSH_KEY }}     # staging key
          APP_ENV: ${{ vars.APP_ENV }}        # "staging"
      - name: Smoke test            # verify before promoting
        run: curl -fsS "${{ vars.PUBLIC_URL }}/health"  # PUBLIC_URL e.g. https://staging.example.com
  production:                       # real users
    needs: [build, staging]         # after staging success
    runs-on: ubuntu-latest          # runner
    environment: production         # reviewers + main-only rule
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - run: ./deploy/deploy.sh "${{ needs.build.outputs.image }}"  # the SAME image that passed staging
        env:                        # env
          HOST: ${{ vars.HOST }}              # production host
          SSH_KEY: ${{ secrets.SSH_KEY }}     # production key
          APP_ENV: ${{ vars.APP_ENV }}        # "production"
```

---

## 🟠 My Stack Integration
On the VPS each environment has its own folder and compose project, with env files not in Git. Same `docker-compose.yml`, different `.env`, and Nginx server blocks per hostname (`dev.example.com`, `staging.example.com`, `app.example.com`).

```yaml
# docker-compose.yml  (same file in every environment; values come from .env on the server)
services:                           # containers
  api:                              # Node or FastAPI service
    image: ${IMAGE}                 # full image reference injected by deploy script
    restart: unless-stopped         # restart after crash/reboot
    env_file: .env                  # DATABASE_URL, LOG_LEVEL, JWT_SECRET live on the server only
    environment:                    # non-secret defaults
      APP_ENV: ${APP_ENV:-dev}      # dev/staging/production label
    ports:                          # publish only to localhost; Nginx is the public entry
      - "127.0.0.1:${API_PORT:-3000}:3000"  # different port per environment on shared hosts
    healthcheck:                    # lets `up --wait` detect a bad release
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]  # needs wget in the image (alpine has busybox wget)
      interval: 10s                 # check every 10s
      timeout: 3s                   # fail if no answer in 3s
      retries: 5                    # unhealthy after 5 failures
```

```nginx
# /etc/nginx/conf.d/staging.conf  (example; not tested with nginx -t here)
server {                                    # virtual host for staging
  listen 80;                                # HTTP (add TLS with certbot in real use)
  server_name staging.example.com;          # example hostname
  location / {                              # all requests
    proxy_pass http://127.0.0.1:3001;       # staging API port from compose
    proxy_set_header Host $host;            # preserve host header
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  # client IP chain
  }
}
```

Security: separate credentials per environment (dev key must not open production), anonymize data copied to staging, and protect dev/staging with basic auth or IP allow-lists so they are not public test targets.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Rebuilding the image for production, so the tested artifact differs from the shipped one.
✅ Correct: Build once, promote the same SHA-tagged image.

❌ Mistake 2: Staging so different from production (small DB, no Nginx, other OS) that it proves nothing.
✅ Correct: Match versions and topology; scale only the size down.

❌ Mistake 3: Sharing one database or one set of credentials across environments.
✅ Correct: Separate databases and secrets; dev can never reach production data.

❌ Mistake 4: Using real customer data in dev/staging.
✅ Correct: Use anonymized or synthetic data.

---

## 🧠 Tricky Interview Question
**Q:** Staging passes every test, yet production fails right after deploy with "relation does not exist". The same image was used. What differs?

Answer: Not the code but state. Most likely the database migration was run in staging manually (or staging DB was created from a newer schema) and was never applied in production because the pipeline did not run migrations there. Fix: run migrations as an explicit, versioned deploy step in every environment, keep migrations backward compatible, and rehearse them on a staging copy of production data.

---

## ⚫ Interview Questions + Answers

Q1: Why not just dev and production?
A1: Staging is the last realistic rehearsal: same infrastructure and versions, so config, migration and integration issues appear before users see them.

Q2: What should differ between environments?
A2: Secrets, URLs, database instances, scale, log levels and feature flags. Not the code or the image.

Q3: What is "config drift"?
A3: Environments slowly diverging (different package versions, manual server edits). Prevent with infrastructure-as-code and containers.

Q4: How do GitHub Environments help?
A4: They scope secrets/vars per environment, add protection rules, and record deployment history and URLs on the repo.

Q5: What are preview environments?
A5: Temporary environments per pull request (own URL), destroyed on merge or close, great for design and QA review.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one person ships changes, or users depend on uptime.
- Migrations and integrations need a rehearsal.

❌ Avoid when:
- A tiny hobby app where three servers cost more than the risk (use one staging at least, or a local compose copy).
- Do not copy production data raw into lower environments.

---

## 📊 Visual Diagram
```
 commit -> CI -> build image :SHA (once)
                      |
      +---------------+----------------+
      v               v                v
   [ dev ]  ----> [ staging ] ----> [ production ]
   auto           auto + smoke       approval + main-only
   fake data      anonymized data    real data
   dev secrets    staging secrets    prod secrets
      \               |                /
       same image, different config (.env / vars)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Environment | Isolated deployment target | अलग-थलग deployment target |
| Staging | Production-like rehearsal | production जैसा rehearsal |
| Promotion | Moving same artifact forward | वही artifact आगे बढ़ाना |
| Config drift | Environments diverge | environments का अलग हो जाना |
| Preview environment | Temporary per-PR environment | हर PR का अस्थायी environment |

---

## ⚡ 3-Line Summary
English: dev, staging and production run the same image with different config, secrets and data.
English: Build once, promote by SHA, and gate production with approval and branch rules.
English: Keep staging production-like, separate credentials, and anonymize data.

Hindi: dev, staging और production वही image अलग config, secrets और data के साथ चलाते हैं।
Hindi: एक बार build करो, SHA से promote करो, और production को approval व branch rules से सुरक्षित रखो।
Hindi: Staging को production जैसा रखो, credentials अलग रखो और data anonymize करो।

---

## ➡️ Next Topic
**336. Build Docker Image** — the build step of the CD pipeline in depth: tags, caching and multi-platform builds.
