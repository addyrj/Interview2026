# 348. Deploy to Railway
# हिंदी में: Railway पर Deploy करना

---

## 🔵 Simple Definition (English)
Railway is a Platform-as-a-Service that builds and runs backends from a repo or Dockerfile, with managed databases (Postgres, Redis, MongoDB), environment variables and private networking. You can deploy by its GitHub integration or from Actions with the **Railway CLI** (`railway up`) and a project token.

## 🔵 सरल परिभाषा (Hindi)
Railway एक Platform-as-a-Service है जो repo या Dockerfile से backend build करके चलाता है, साथ में managed databases (Postgres, Redis, MongoDB), environment variables और private networking देता है। आप उसके GitHub integration से या Actions में **Railway CLI** (`railway up`) और project token से deploy कर सकते हैं।

---

## 🔴 Problem it Solves
Running a backend on a VPS means managing the OS, Docker, Nginx, TLS, backups and monitoring. For small teams and prototypes that is too much. Railway auto-detects Node.js/Python (or uses your Dockerfile), provisions HTTPS domains and databases, and redeploys on every push.

## 🔴 यह क्यों बना? (Hindi)
VPS पर backend चलाने में OS, Docker, Nginx, TLS, backups और monitoring संभालना पड़ता है। छोटी teams और prototypes के लिए यह बहुत ज़्यादा है। Railway Node.js/Python अपने आप पहचानता है (या आपका Dockerfile इस्तेमाल करता है), HTTPS domain और databases देता है और हर push पर redeploy करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a Railway project; add services (api, postgres, redis)
Step 2 → Service settings: builder = Dockerfile or Nixpacks/Railpack (auto)
Step 3 → Create a Project Token (Project > Settings > Tokens)
Step 4 → Add RAILWAY_TOKEN as GitHub secret
Step 5 → CI: install CLI → railway up --service api --ci
Step 6 → Railway builds, runs healthcheck (healthcheckPath), swaps traffic
Step 7 → Variables (DATABASE_URL) are injected from the linked database
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Railway project बनाओ; services जोड़ो (api, postgres, redis)।
Step 2 → Service settings में builder = Dockerfile या Nixpacks/Railpack (auto)।
Step 3 → Project Token बनाओ (Project > Settings > Tokens)।
Step 4 → `RAILWAY_TOKEN` GitHub secret में रखो।
Step 5 → CI: CLI install → `railway up --service api --ci`।
Step 6 → Railway build करता है, healthcheck चलाता है, फिर traffic स्विच करता है।
Step 7 → Variables (`DATABASE_URL`) linked database से inject होते हैं।

---

## 🟡 Real World Example
A hackathon team ships a FastAPI backend plus Postgres in an evening. Railway gives `https://api-production-xxxx.up.railway.app`, `DATABASE_URL` is auto-injected, and each merge redeploys. When the product grows, they move heavy services to ECS/VPS, but internal tools and staging stay on Railway.

## 🟡 Real Example Hindi mein
एक hackathon team एक शाम में FastAPI backend और Postgres चालू कर लेती है। Railway `https://api-production-xxxx.up.railway.app` देता है, `DATABASE_URL` अपने आप inject होता है और हर merge पर redeploy होता है। Product बढ़ने पर भारी services ECS/VPS पर जाती हैं, पर internal tools और staging Railway पर रहते हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/railway-basic.yml
name: railway-basic                    # workflow name
on:
  push:
    branches: [main]                   # deploy on main
jobs:
  deploy:
    runs-on: ubuntu-latest             # runner
    container: ghcr.io/railwayapp/cli:latest   # image with the Railway CLI preinstalled
    env:
      RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}   # project token (scoped to one environment)
    steps:
      - uses: actions/checkout@v4      # get code to upload
      - name: Deploy                   # upload and build on Railway
        run: railway up --service api --ci   # --ci streams build logs and exits when done
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/railway-advanced.yml (tests first, staging then production)
name: railway-advanced
on:
  push:
    branches: [main]
concurrency:
  group: railway-deploy                # avoid overlapping deploys
  cancel-in-progress: false
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci                    # install
      - run: npm test                  # gate deployment on tests
  deploy-staging:
    needs: test                        # only after tests pass
    runs-on: ubuntu-latest
    container: ghcr.io/railwayapp/cli:latest
    environment: staging
    env:
      RAILWAY_TOKEN: ${{ secrets.RAILWAY_STAGING_TOKEN }}   # token of the staging environment
    steps:
      - uses: actions/checkout@v4
      - run: railway up --service api --ci
  deploy-production:
    needs: deploy-staging              # promote after staging succeeds
    runs-on: ubuntu-latest
    container: ghcr.io/railwayapp/cli:latest
    environment: production            # add required reviewers here
    env:
      RAILWAY_TOKEN: ${{ secrets.RAILWAY_PROD_TOKEN }}
    steps:
      - uses: actions/checkout@v4
      - run: railway up --service api --ci
```

```toml
# railway.toml - config as code, placed in repo root
[build]
builder = "DOCKERFILE"                 # use the repo Dockerfile
dockerfilePath = "Dockerfile"          # path to it

[deploy]
startCommand = "node dist/main.js"     # optional override of CMD
healthcheckPath = "/health"            # Railway waits for 200 before switching traffic
healthcheckTimeout = 60                # seconds to wait
restartPolicyType = "ON_FAILURE"       # restart if the process crashes
restartPolicyMaxRetries = 5            # stop after 5 retries
```

Railway's CLI, token types and `railway.toml` keys evolve; the names above match the documented config at the time of writing, but confirm in Railway docs for your version. The workflow was not run against a real Railway project here.

---

## 🟠 My Stack Integration
Node.js and FastAPI services reuse your Dockerfile. Use Railway's private networking so the API reaches Postgres without a public URL, and put the React frontend on Vercel/Netlify.

```dockerfile
# Dockerfile for FastAPI on Railway (reads PORT, which Railway injects)
FROM python:3.12-slim
WORKDIR /app
# install dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# copy application code
COPY . .
# run as non-root user
RUN useradd -m appuser
USER appuser
# bind to the PORT environment variable provided by the platform
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

Your own Nginx is not needed; Railway terminates TLS on its edge. If you keep a VPS Nginx for other apps, point your custom domain's CNAME to Railway only for services hosted there.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Hardcoding the port (`3000`), so the app is "unhealthy".
✅ Correct: Listen on `process.env.PORT` / `${PORT}` and bind to `0.0.0.0`.

❌ Mistake 2: Using an account-wide token in CI.
✅ Correct: Use a project (environment-scoped) token; separate tokens for staging and production.

❌ Mistake 3: Using a public DB URL from the API.
✅ Correct: Use the private network hostname to avoid egress cost and exposure.

❌ Mistake 4: Relying on local disk for uploads (ephemeral).
✅ Correct: Attach a volume or use S3.

---

## 🧠 Tricky Interview Question
The deploy builds fine, yet it is marked failed, and the old version keeps running. Why?

Answer: Railway only switches traffic after the new instance passes its healthcheck. If the app binds to `localhost` or the wrong port, the endpoint returns non-200, or startup (migrations) takes longer than `healthcheckTimeout`, the deploy fails and the previous deployment stays live. That is the safety feature working; fix the bind address/port or raise the timeout.

---

## ⚫ Interview Questions + Answers

Q1: PaaS vs IaaS?
A1: PaaS (Railway, Heroku) hides servers and gives deploy-by-push; IaaS (EC2, VPS) gives full control and requires you to run everything.

Q2: How are secrets handled?
A2: Environment variables per service/environment in Railway; reference variables between services; never commit them.

Q3: How do you roll back?
A3: Redeploy a previous successful deployment from the dashboard.

Q4: Risks of PaaS?
A4: Vendor lock-in, cost growth with usage, limited low-level control, and dependence on the vendor's reliability.

Q5: Database migrations in this flow?
A5: Run them as a pre-deploy/start command (e.g. `npm run migrate && node dist/main.js`) and make migrations backward compatible.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- MVPs, hackathons, staging and internal tools.
- You want a backend plus database in minutes.

❌ Avoid when:
- Strict compliance/data residency needs (Mumbai region may not be available).
- Very large, cost-sensitive steady workloads.

---

## 📊 Visual Diagram
```
 push main ─► Actions: tests ─► railway up --service api --ci
                                         │ upload source / Dockerfile
                                         ▼
   ┌──────────────── Railway project (environment: production) ─────────────┐
   │ build ─► new instance ─► healthcheck /health ──ok──► switch traffic     │
   │                                  └─fail─► keep old deployment live      │
   │ api ◄── private network ──► postgres / redis (DATABASE_URL injected)    │
   └──────────────────────────────────────────────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| PaaS | Platform that runs your app | app चलाने वाला platform |
| Project token | Scoped CI credential | सीमित CI चाबी |
| Service | One deployable app/db | एक deployable इकाई |
| Healthcheck | Gate before traffic switch | traffic से पहले जाँच |
| Private networking | Internal service-to-service link | आंतरिक connection |
| Nixpacks | Auto build system | auto build तरीका |

---

## ⚡ 3-Line Summary
English: Railway builds and runs your repo or Dockerfile with managed databases. Deploy via the CLI with a scoped project token. Healthchecks protect production; always honor PORT.
Hindi: Railway आपके repo या Dockerfile को managed databases के साथ build और run करता है। Scoped project token से CLI द्वारा deploy करो। Healthcheck production बचाता है; हमेशा PORT मानो।

---

## ➡️ Next Topic
**349. Deploy Next.js** - deploying a full Next.js app (SSR, standalone output, Docker or Vercel).
