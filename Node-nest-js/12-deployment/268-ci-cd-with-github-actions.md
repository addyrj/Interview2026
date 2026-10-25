# 268. CI/CD with GitHub Actions
# हिंदी में: GitHub Actions से CI/CD Pipeline

---

## 🔵 Simple Definition (English)
**CI/CD (Continuous Integration / Continuous Deployment)** automates testing and deploying your Node.js app every time code is pushed. **GitHub Actions** is GitHub's built-in automation tool — you define a YAML workflow file that runs on events (push, pull request), executing steps like installing dependencies, running lint/tests, and deploying — all automatically, without a human manually running commands.

## 🔵 सरल परिभाषा (Hindi)
**CI/CD (Continuous Integration / Continuous Deployment)** code push hone par apne Node.js app ka testing aur deployment automatically karta hai। **GitHub Actions** GitHub ka built-in automation tool hai — tum ek YAML workflow file define karte ho jo events (push, pull request) par run hota hai, aur steps execute karta hai jaise dependencies install karna, lint/tests chalana, aur deploy karna — sab automatically, bina kisi insaan ke manually command chalaye।

---

## 🔴 Problem it Solves
```
MANUAL DEPLOYMENT/TESTING PROBLEMS:
  - Developer pushes code → forgets to run tests → broken code reaches main
  - "Works on my machine" bugs: different Node versions across team
  - Manual deploy steps: SSH in, git pull, npm install, restart — error-prone
  - Someone forgets a step, or does it in the wrong order
  - No automatic gate preventing bad PRs from being merged
  - Deploying to production is a stressful manual ritual, done by one "DevOps person"

CI/CD WITH GITHUB ACTIONS SOLUTION:
  - Every push/PR automatically triggers: install → lint → test → build
  - Broken tests = PR shows a red ❌, blocking merge (branch protection rules)
  - Test across MULTIPLE Node.js versions simultaneously (matrix builds)
  - Merge to main = automatic deploy to Railway/VPS/AWS — zero manual steps
  - Secrets (API keys, SSH keys, DB passwords) stored securely in GitHub,
    never exposed in code or logs
  - Any team member can safely merge — the pipeline enforces quality gates
```

## 🔴 यह क्यों बना? (Hindi)
Manually deploy karne mein developer code push karta tha, tests run karna bhool jata tha, aur broken code main branch mein pahunch jata tha। Team mein alag-alag Node versions hone se "works on my machine" bugs aate the। Manual deploy steps — SSH karna, git pull, npm install, restart — error-prone tha, koi step miss ho jata ya galat order mein ho jata। Koi automatic gate nahi tha jo bad PR ko merge hone se roke। GitHub Actions se har push/PR par automatically install → lint → test → build chalta hai। Tests fail hone par PR par red ❌ dikhta hai, merge block ho jata hai। Multiple Node.js versions par simultaneously test ho sakta hai (matrix builds)। Main branch par merge hone se automatic deploy ho jata hai Railway/VPS/AWS par — zero manual steps। Secrets GitHub mein securely store hote hain, code ya logs mein kabhi expose nahi hote।

---

## 🟢 How it Works — Step by Step

Step 1 → Create a `.github/workflows/*.yml` file in your repo — GitHub auto-detects and runs it.
Step 2 → Define `on:` triggers — e.g. `push` to specific branches, or `pull_request` to run checks before merge.
Step 3 → Define one or more `jobs:` — each job runs on a fresh virtual machine (`runs-on: ubuntu-latest`).
Step 4 → Each job has `steps:` — checkout code, set up Node.js, `npm install`, `npm run lint`, `npm test`, `npm run build`.
Step 5 → GitHub Actions reports the result as a status check directly on the commit/PR — green ✅ or red ❌.
Step 6 → With **branch protection rules**, a red ❌ blocks merging — enforcing the quality gate automatically.
Step 7 → A separate `deploy` job (often conditioned on `if: github.ref == 'refs/heads/main'`) runs only after tests pass on `main` — deploying via SSH, a platform's CLI, or a webhook, using **secrets** stored in GitHub's encrypted settings.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Repo mein `.github/workflows/*.yml` file banao — GitHub isko auto-detect karke run karta hai।
Step 2 → `on:` triggers define karo — jaise specific branches par `push`, ya merge se pehle checks chalane ke liye `pull_request`।
Step 3 → Ek ya zyada `jobs:` define karo — har job ek fresh virtual machine par run hota hai (`runs-on: ubuntu-latest`)।
Step 4 → Har job mein `steps:` hote hain — code checkout, Node.js setup, `npm install`, `npm run lint`, `npm test`, `npm run build`।
Step 5 → GitHub Actions result ko commit/PR par status check ke roop mein report karta hai — green ✅ ya red ❌।
Step 6 → **Branch protection rules** se red ❌ merge block kar deta hai — quality gate automatically enforce hoti hai।
Step 7 → Ek alag `deploy` job (jo usually `if: github.ref == 'refs/heads/main'` condition par run hota hai) sirf `main` par tests pass hone ke baad chalta hai — SSH, platform CLI, ya webhook ke zariye deploy karta hai, GitHub ke encrypted settings mein store kiye **secrets** use karke।

---

## 🟡 Real World Example
**Swiggy's backend team workflow:** Every developer opens a PR; GitHub Actions automatically installs dependencies, runs ESLint, runs the full Jest test suite across Node 18 and Node 20 (matrix build) to catch version-specific bugs, and reports status on the PR. Only after all checks pass and a teammate approves, the PR can merge — then a separate workflow deploys to a staging server automatically. **Razorpay-style production deploy:** On merge to `main`, GitHub Actions runs tests one more time, then SSHes into the production server using a private key stored as a GitHub secret, pulls the latest code, installs dependencies, and restarts the app with PM2 — a deploy that used to take a human 15 minutes now takes 90 seconds with zero manual steps and zero chance of a forgotten step.

## 🟡 Real Example Hindi mein
**Swiggy ka backend team workflow:** Har developer PR kholta hai; GitHub Actions automatically dependencies install karta hai, ESLint chalata hai, full Jest test suite ko Node 18 aur Node 20 dono par chalata hai (matrix build) version-specific bugs catch karne ke liye, aur PR par status report karta hai। Sab checks pass hone aur teammate ke approve karne ke baad hi PR merge ho sakta hai — phir ek alag workflow automatically staging server par deploy karta hai। **Razorpay-style production deploy:** `main` par merge hone par GitHub Actions ek baar aur tests chalata hai, phir production server mein SSH karta hai GitHub secret mein stored private key use karke, latest code pull karta hai, dependencies install karta hai, aur PM2 se app restart karta hai — jo deploy insaan 15 minute mein karta tha, ab 90 second mein ho jata hai, bina kisi manual step ke aur kisi bhoole step ke chance ke bina।

---

## 💻 Code Example — Basic

```yaml
# .github/workflows/ci.yml — minimal CI: runs on every push and pull request,
# installs dependencies, lints, and runs tests.

name: CI # name shown in GitHub's Actions tab

on: # events that trigger this workflow
  push:
    branches: [main] # run when code is pushed directly to main
  pull_request:
    branches: [main] # run when a PR targets main (before merge)

jobs:
  test: # a single job named "test"
    runs-on: ubuntu-latest # fresh Ubuntu virtual machine for this job

    steps:
      - name: Checkout code # step 1: clone the repo into the runner
        uses: actions/checkout@v4 # official GitHub action for checking out code

      - name: Set up Node.js # step 2: install a specific Node.js version
        uses: actions/setup-node@v4
        with:
          node-version: '20' # must match (or be compatible with) production

      - name: Install dependencies # step 3: npm ci is faster/stricter than npm install
        run: npm ci # uses package-lock.json exactly, fails if lockfile is out of sync

      - name: Run lint # step 4: catch style/syntax issues before tests
        run: npm run lint

      - name: Run tests # step 5: run the actual test suite (e.g. Jest)
        run: npm test
```

```json
// package.json — scripts referenced by the workflow above
{
  "scripts": {
    "lint": "eslint .",
    "test": "jest --ci",
    "build": "echo 'no build step for plain JS'"
  },
  "devDependencies": {
    "eslint": "^8.57.0",
    "jest": "^29.7.0"
  }
}
```

## 💻 Code Example — Advanced

```yaml
# .github/workflows/ci-cd.yml — full pipeline: matrix testing across Node
# versions, build, and automatic deploy to a VPS via SSH on merge to main.

name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  # ─── JOB 1: TEST ──────────────────────────────────────────────────────
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix: # run this entire job multiple times, once per Node version
        node-version: ['18.x', '20.x', '22.x']
      fail-fast: false # don't cancel other versions if one fails — see all results

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js ${{ matrix.node-version }} # ${{ }} interpolates matrix value
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm' # caches node_modules between runs for speed

      - name: Install dependencies
        run: npm ci

      - name: Run lint
        run: npm run lint

      - name: Run tests with coverage
        run: npm test -- --coverage
        env:
          # Secrets needed even for tests (e.g. a test DB connection string)
          NODE_ENV: test
          DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }} # pulled from GitHub secrets, never hardcoded

  # ─── JOB 2: BUILD (only runs if "test" job succeeds) ──────────────────
  build:
    needs: test # waits for the "test" job to pass across ALL matrix versions
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Upload build artifact # save the build output for the deploy job to reuse
        uses: actions/upload-artifact@v4
        with:
          name: app-build
          path: dist/ # whatever directory your build produces

  # ─── JOB 3: DEPLOY (only on push to main, after build succeeds) ───────
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push' # never deploy from a PR

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: app-build
          path: dist/

      - name: Deploy to production VPS via SSH
        uses: appleboy/ssh-action@v1.0.0 # community action for running remote SSH commands
        with:
          host: ${{ secrets.PROD_HOST }} # server IP, stored as a GitHub secret
          username: ${{ secrets.PROD_USER }} # SSH username, e.g. "deploy"
          key: ${{ secrets.PROD_SSH_PRIVATE_KEY }} # private key, stored as a GitHub secret
          script: | # commands run ON the remote server
            cd /var/www/order-api
            git pull origin main
            npm ci --production
            pm2 restart order-api  # zero-downtime restart via PM2

      - name: Notify on failure
        if: failure() # only runs if any previous step in this job failed
        run: echo "Deployment failed! Check logs above."
```

```bash
# Setting up secrets (done once in GitHub UI, not in code):
# Repo → Settings → Secrets and variables → Actions → New repository secret
#
#   PROD_HOST              = 203.0.113.42
#   PROD_USER              = deploy
#   PROD_SSH_PRIVATE_KEY   = -----BEGIN OPENSSH PRIVATE KEY-----...
#   TEST_DATABASE_URL      = postgres://test:test@localhost:5432/test_db
#
# These are encrypted at rest, injected only at workflow run time, and
# automatically masked (shown as ***) in logs even if accidentally printed.
```

---

## 🟠 Express.js Integration

```yaml
# .github/workflows/express-ci.yml — CI specifically exercising an Express
# app's test suite (e.g. using supertest to hit real routes in-process).

name: Express App CI

on:
  pull_request:
    branches: [main]

jobs:
  test-express-app:
    runs-on: ubuntu-latest

    # Spin up a real Postgres service container for integration tests —
    # the Express app's tests can connect to this exactly like production
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: orders_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run Express route tests (supertest)
        run: npm test
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/orders_test
          NODE_ENV: test
```

```javascript
// tests/orders.test.js — the Express app tests this CI workflow actually runs
// npm install --save-dev supertest jest

const request = require('supertest');
const app = require('../server'); // your Express app, exported WITHOUT app.listen() firing in test mode

describe('GET /orders/:orderId', () => {
  it('returns 200 and the order for a valid id', async () => {
    // supertest spins the Express app up in-memory — no real network port needed
    const res = await request(app).get('/orders/123');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('orderId', '123');
  });

  it('returns 404 for a non-existent order', async () => {
    const res = await request(app).get('/orders/does-not-exist');
    expect(res.statusCode).toBe(404);
  });
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Hardcoding secrets directly in the workflow YAML
```yaml
# WRONG: SSH key committed in plain text, visible to anyone with repo access
- name: Deploy
  run: ssh -i "-----BEGIN PRIVATE KEY-----..." deploy@203.0.113.42 "git pull"

# CORRECT: store in GitHub Secrets, reference via ${{ secrets.NAME }}
- name: Deploy
  uses: appleboy/ssh-action@v1.0.0
  with:
    host: ${{ secrets.PROD_HOST }}
    key: ${{ secrets.PROD_SSH_PRIVATE_KEY }}
    script: git pull origin main
```

❌ **Mistake 2:** Using `npm install` instead of `npm ci` in CI
```yaml
# WRONG: npm install can update package-lock.json and install slightly
# different versions than what's actually committed — inconsistent builds
- run: npm install

# CORRECT: npm ci installs EXACTLY what's in package-lock.json, fails loudly
# if the lockfile is out of sync with package.json, and is faster in CI
- run: npm ci
```

❌ **Mistake 3:** Deploying even when tests fail (no job dependency)
```yaml
# WRONG: deploy job has no "needs" — runs independently of test results
jobs:
  test:
    runs-on: ubuntu-latest
    steps: [...]
  deploy:
    runs-on: ubuntu-latest  # runs in parallel with test, ignoring its result!
    steps: [...]

# CORRECT: deploy explicitly waits for test to succeed first
jobs:
  test:
    runs-on: ubuntu-latest
    steps: [...]
  deploy:
    needs: test  # only runs if "test" job completes successfully
    runs-on: ubuntu-latest
    steps: [...]
```

---

## 🧠 Tricky Interview Question

**Q: This workflow has a `deploy` job with `needs: test`, yet it still ran and deployed even though the `test` job failed. Why?**

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    continue-on-error: true   # <-- the clue
    steps:
      - run: npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh
```

**Answer:** `continue-on-error: true` on the `test` job tells GitHub Actions to mark the job as **successful overall** even if individual steps inside it fail — the job's final status becomes "success (with a failed step)" rather than "failure." Since `deploy` uses `needs: test`, it only checks whether the `test` job's overall conclusion was success — and because of `continue-on-error`, it was, despite `npm test` actually failing. This is a real-world gotcha: `continue-on-error` is meant for genuinely optional steps (e.g. a flaky linter you don't want blocking merges yet), but if accidentally left on a critical test step, it silently defeats the entire purpose of `needs:` as a quality gate. Fix: remove `continue-on-error` from steps that must actually gate deployment.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between Continuous Integration and Continuous Deployment?**
A1: **Continuous Integration (CI)** is the practice of automatically building and testing code every time it's pushed or a PR is opened — catching integration bugs early by merging small changes frequently and verifying them immediately. **Continuous Deployment (CD)** extends this by automatically deploying code to production (or staging) once it passes CI, with no manual approval step. Some teams use **Continuous Delivery** instead — code is automatically prepared for release but a human clicks "deploy" — as a middle ground between full automation and manual control.

**Q2: How do GitHub Actions secrets work, and why are they safer than storing credentials in code?**
A2: Secrets are set in repo (or organization) settings, encrypted at rest by GitHub, and only decrypted into the workflow's environment at run time — they're referenced via `${{ secrets.NAME }}` and are never visible in the repo's code or in workflow file history. GitHub also automatically masks secret values in logs (replacing them with `***`) even if a script accidentally prints them. This is safer than hardcoding credentials because code is visible to anyone with repo read access and lives forever in git history, while secrets are scoped, auditable, and rotatable without touching code.

**Q3: What is a matrix build and why is it useful for Node.js projects?**
A3: A matrix build runs the same job multiple times with different parameter combinations — e.g. testing against Node 18, 20, and 22 simultaneously. This catches version-specific bugs (a feature available in Node 20 but not 18, or a dependency behaving differently across versions) before they reach production, especially important for npm packages that must support multiple Node versions, or teams migrating between LTS versions. Each matrix combination runs as a fully independent parallel job, so it doesn't slow down the pipeline — it just reports multiple results.

**Q4: How would you design a GitHub Actions pipeline that deploys to production only after manual approval?**
A4: Use GitHub **Environments** — define a "production" environment with "required reviewers" configured in repo settings. In the workflow, set the deploy job's `environment: production`; GitHub Actions will then pause that job after `needs: test` succeeds and wait for a designated reviewer to approve it in the Actions UI before actually running the deploy steps. This gives Continuous Delivery (automated up to the release gate) while keeping a human decision point before production changes go live — useful for regulated industries like Razorpay/Paytm-style fintech deployments.

**Q5: Why is `npm ci` preferred over `npm install` in a CI/CD pipeline?**
A5: `npm ci` deletes the existing `node_modules` and installs EXACTLY the versions locked in `package-lock.json`, failing immediately if `package.json` and the lockfile are out of sync — this guarantees the CI environment matches what every other developer and production actually run. `npm install` can silently update the lockfile and install slightly different transitive dependency versions, leading to "it worked in CI but broke in prod" discrepancies. `npm ci` is also generally faster in CI because it skips the dependency-resolution step that `npm install` performs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any team project where code quality/test enforcement before merge matters
- You want deploys to be repeatable, auditable, and free of manual SSH rituals
- You need to test across multiple Node.js versions or environments
- You want secrets managed securely instead of scattered across developers' machines

❌ Avoid when:
- A true one-person throwaway script/experiment with no collaborators and no deploy target
- Extremely simple static sites with no build/test step at all (though even then, basic CI costs little)
- (Rare) When your org mandates a different CI system already in place — redundant parallel pipelines add confusion, not safety

---

## 📊 Visual Diagram
```
GITHUB ACTIONS CI/CD PIPELINE:
──────────────────────────────────────────────────────────────────

  git push / PR opened
         │
         ▼
  ┌─────────────────────────────┐
  │ JOB: test (matrix: 18/20/22) │
  │  checkout → setup-node →     │
  │  npm ci → lint → test        │
  └───────────┬───────────────────┘
              │ all pass?
              ▼
  ┌─────────────────────────────┐
  │ JOB: build                   │
  │  checkout → npm ci → build   │
  │  → upload artifact            │
  └───────────┬───────────────────┘
              │ needs: build (success)
              ▼
  ┌─────────────────────────────┐          only if branch == main
  │ JOB: deploy                  │◀──────── and event == push
  │  download artifact →          │
  │  SSH into server / Railway    │
  │  CLI → restart app            │
  └─────────────────────────────┘
              │
              ▼
       App live in production

  SECRETS (encrypted) ───▶ injected as env vars only during job execution
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CI | Continuous Integration — auto build/test on push | Push par auto build/test |
| CD | Continuous Deployment/Delivery — auto release | Auto release/deployment |
| Workflow | A YAML file defining automated steps | Automated steps define karne wali YAML file |
| Job | A set of steps run on one virtual machine | Ek VM par chalne wale steps ka set |
| Matrix Build | Running a job across multiple configs (e.g. Node versions) | Multiple configs mein job chalana |
| Secrets | Encrypted credentials stored in GitHub | GitHub mein encrypted credentials |
| Branch Protection | Rules blocking merge unless checks pass | Checks pass na hone tak merge block karne wale rules |
| Artifact | Build output passed between jobs | Jobs ke beech pass hone wala build output |

---

## ⚡ 3-Line Summary
**English:**
1. GitHub Actions automates install → lint → test → build → deploy on every push/PR via a `.github/workflows/*.yml` file.
2. Branch protection rules use these status checks as a merge gate; matrix builds test across multiple Node.js versions in parallel.
3. Secrets stored in GitHub (never in code) power automatic deployment — to a VPS via SSH, or to Railway/AWS — only after tests pass on `main`.

**Hindi:**
1. GitHub Actions `.github/workflows/*.yml` file ke zariye har push/PR par install → lint → test → build → deploy automate karta hai।
2. Branch protection rules in status checks ko merge gate ke roop mein use karte hain; matrix builds multiple Node.js versions par parallel test karte hain।
3. GitHub mein stored secrets (code mein kabhi nahi) automatic deployment power karte hain — VPS par SSH se, ya Railway/AWS par — sirf `main` par tests pass hone ke baad।

---

## ➡️ Next Topic
**269. Blue-Green Deployment** — Zero-downtime deployment strategy jahan do identical production environments ke beech traffic switch hota hai, rollback ko instant banata hai।
