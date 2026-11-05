# 301. CI Pipeline — Complete Guide
# हिंदी में: CI Pipeline — पूरी गाइड

---

## 🔵 Simple Definition (English)
**CI (Continuous Integration)** means every code change is automatically built and tested, many times a day, in a clean machine. A **CI pipeline** is the ordered list of automatic checks: checkout, install, lint, type-check, test, build. If any check fails, the change is blocked from merging.

## 🔵 सरल परिभाषा (Hindi)
**CI (Continuous Integration)** का मतलब है कि हर code change एक साफ़ machine पर अपने आप build और test हो, दिन में कई बार। **CI pipeline** automatic checks की क्रमबद्ध सूची है: checkout, install, lint, type-check, test, build। कोई भी check fail हो तो change merge नहीं हो सकता।

---

## 🔴 Problem it Solves
Before CI, developers merged big changes once a week. "Works on my machine" bugs, broken `main`, forgotten lint rules, and a different Node version on each laptop were normal. Finding which commit broke the build took hours. Release day was fear day.
CI gives a fast, objective, repeatable answer to one question: "Is this change safe to merge?"

## 🔴 यह क्यों बना? (Hindi)
CI से पहले developers हफ़्ते में एक बार बड़े changes merge करते थे। "मेरी machine पर चलता है" वाले bugs, टूटा हुआ `main`, भूले हुए lint rules और हर laptop पर अलग Node version आम बात थी। कौन सा commit build तोड़ गया, यह ढूँढने में घंटे लगते। Release का दिन डर का दिन होता।
CI एक सवाल का तेज़, निष्पक्ष और repeatable जवाब देता है: "क्या यह change merge करने लायक है?"

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developer pushes branch / opens Pull Request
Step 2 → GitHub fires event (push / pull_request) -> workflow starts
Step 3 → Fresh runner VM is created (ubuntu-latest)
Step 4 → actions/checkout downloads the code
Step 5 → setup-node / setup-python installs the runtime (+ dependency cache)
Step 6 → Install dependencies (npm ci / pip install)
Step 7 → Quality gates: lint -> type-check -> unit tests -> integration tests
Step 8 → Build (npm run build / docker build) and upload artifacts/coverage
Step 9 → Result (green/red) is reported on the PR as a status check
Step 10 → Branch protection: PR can merge only when required checks are green
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Developer branch push करता है / Pull Request खोलता है
Step 2 → GitHub event भेजता है (push / pull_request) -> workflow शुरू
Step 3 → नया runner VM बनता है (ubuntu-latest)
Step 4 → actions/checkout code download करता है
Step 5 → setup-node / setup-python runtime install करता है (+ dependency cache)
Step 6 → Dependencies install (npm ci / pip install)
Step 7 → Quality gates: lint -> type-check -> unit tests -> integration tests
Step 8 → Build (npm run build / docker build) और artifacts/coverage upload
Step 9 → Result (हरा/लाल) PR पर status check के रूप में दिखता है
Step 10 → Branch protection: required checks हरे हों तभी PR merge हो सकता है
```

---

## 🟡 Real World Example
A food-delivery startup has an Express API, a FastAPI pricing service, and a React web app in one monorepo. On every PR: lint and type-check run in 1 minute, unit tests in 3 minutes, and a Docker build in 4 minutes, all in parallel jobs. The PR cannot merge until the 4 required checks are green. Since adopting CI, broken `main` incidents dropped from weekly to near zero.

## 🟡 Real Example Hindi mein
एक food-delivery startup के एक monorepo में Express API, FastAPI pricing service और React web app हैं। हर PR पर lint और type-check 1 मिनट में, unit tests 3 मिनट में और Docker build 4 मिनट में चलते हैं, सब parallel jobs में। 4 required checks हरे होने तक PR merge नहीं हो सकता। CI अपनाने के बाद `main` टूटने की घटनाएँ हफ़्तावार से लगभग शून्य हो गईं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/ci.yml
name: CI                              # workflow name in the Actions tab

on:
  push:
    branches: [main]                  # run when main changes
  pull_request:                       # run for every PR

jobs:
  build-and-test:
    runs-on: ubuntu-latest            # fresh Linux VM
    steps:
      - uses: actions/checkout@v4     # 1. get the code
      - uses: actions/setup-node@v4   # 2. install Node
        with:
          node-version: 20            # example, use your project's version
          cache: npm                  # cache npm downloads
      - run: npm ci                   # 3. exact install from lockfile
      - run: npm run lint             # 4. style/bug rules
      - run: npm test                 # 5. unit tests
      - run: npm run build            # 6. make sure it builds
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/ci.yml  (monorepo: Node API + React web + FastAPI)
name: CI

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:                  # manual re-run button

# Cancel older runs of the same PR when new commits arrive (saves minutes)
concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read                      # least privilege for GITHUB_TOKEN

env:
  CI: "true"                          # many tools change behavior in CI

jobs:
  node-api:
    runs-on: ubuntu-latest
    timeout-minutes: 15               # kill stuck jobs
    defaults:
      run:
        working-directory: api        # all run steps start in ./api
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: api/.nvmrc            # single source of Node version
          cache: npm
          cache-dependency-path: api/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npx tsc --noEmit                      # type check only
      - run: npm test -- --ci --coverage           # unit tests with coverage

  react-web:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    defaults:
      run:
        working-directory: web
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: web/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --ci
      - run: npm run build                         # production bundle
      - uses: actions/upload-artifact@v4           # keep build for later jobs
        with:
          name: web-dist
          path: web/dist
          retention-days: 7

  fastapi:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    defaults:
      run:
        working-directory: pricing
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: pricing/requirements*.txt
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: ruff check .                          # lint
      - run: pytest -q --cov=app                   # tests + coverage

  docker-build:
    needs: [node-api, react-web, fastapi]          # only after all checks pass
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t api:ci api            # build image, do not push in CI-only
```

---

## 🟠 My Stack Integration
- **Node.js / React:** `npm ci`, ESLint, `tsc --noEmit`, Jest/Vitest, `npm run build`.
- **FastAPI:** `ruff`/`flake8`, `mypy` (optional), `pytest` with Postgres/Redis service containers.
- **Nginx:** add a step `docker run --rm -v $PWD/nginx.conf:/etc/nginx/nginx.conf:ro nginx:1.27 nginx -t` to validate the config in CI.
- **VPS / AWS:** CI only proves code is good; CD (later topics) deploys the same commit. Use branch protection so deploy runs only from green `main`.

```yaml
# Nginx config validation step for your VPS repo (needs Docker on runner; ubuntu-latest has it)
      - name: Validate nginx.conf
        run: |                                       # multi-line shell
          docker run --rm \
            -v "$PWD/deploy/nginx.conf:/etc/nginx/conf.d/default.conf:ro" \
            nginx:1.27-alpine nginx -t               # example tag; updates welcome
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `npm install` in CI. It may modify the lockfile and install different versions.
✅ Correct: `npm ci` (fails if lockfile and package.json disagree).

❌ Mistake 2: One giant job with 30 steps; the slowest step blocks feedback.
✅ Correct: Split lint, tests, build into parallel jobs; use `needs` only where order matters.

❌ Mistake 3: No `timeout-minutes` or `concurrency`. Hung jobs burn minutes; ten pushes queue ten runs.
✅ Correct: Set timeouts and `cancel-in-progress: true` for PR workflows.

❌ Mistake 4: CI passes but the branch is not protected, so people merge red PRs.
✅ Correct: Enable branch protection with "Require status checks to pass" and select job names.

❌ Mistake 5: Giving CI broad write tokens or deploy secrets on PRs from forks.
✅ Correct: `permissions: contents: read`; keep deploy secrets for `main`/environments only.

---

## 🧠 Tricky Interview Question
**Q:** Your CI is green on the PR but `main` breaks right after merge. How is that possible and how do you stop it?

**Answer:** `pull_request` CI tests the PR merged with the base **at the time it ran** (GitHub tests a temporary merge commit). If another PR merged in between and conflicts semantically (not textually), the combination was never tested. Fixes: enable "Require branches to be up to date before merging", or use a **merge queue** (`merge_group` event) so CI runs on the exact final result before it lands; and also run CI on `push` to `main`.

---

## ⚫ Interview Questions + Answers

Q1: CI vs CD vs Continuous Deployment?
A1: CI = automatic build+test per change. Continuous Delivery = every green build is releasable, deploy is a manual click. Continuous Deployment = every green build deploys automatically.

Q2: What makes a good CI pipeline?
A2: Fast (under ~10 minutes), reliable (no flaky tests), deterministic (pinned versions, lockfiles), and informative (clear failure messages, artifacts, coverage).

Q3: Why `npm ci` and lockfiles?
A3: For reproducible installs; the same dependency tree on every run, preventing "works on my machine".

Q4: How do you speed up a slow pipeline?
A4: Cache dependencies, parallelize jobs, run only affected parts with path filters, cancel superseded runs, use bigger runners if needed, and split slow integration tests.

Q5: `push` vs `pull_request` trigger?
A5: `pull_request` validates proposed changes before merge (and fork safety applies); `push` to `main` validates the result after merge and can trigger deploy.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one developer pushes to the same repo
- You deploy regularly and want confidence
- You want enforced standards (lint, types, tests)

❌ Avoid when:
- Never skip it, but do not put slow, flaky end-to-end suites on every PR (run nightly or on `main`)
- Do not use CI to hold long-running deploy logic (that is CD)

---

## 📊 Visual Diagram
```
 git push / PR
      |
      v
 +-----------+   +----------+   +-----------+   +---------+   +--------+
 | checkout  |-->| setup +  |-->| install   |-->| lint +  |-->| tests  |
 |           |   | cache    |   | npm ci    |   | types   |   | unit   |
 +-----------+   +----------+   +-----------+   +---------+   +--------+
                                                                   |
                                                                   v
                                                  +----------+  +--------------+
                                                  | build /  |->| coverage +   |
                                                  | docker   |  | artifacts    |
                                                  +----------+  +--------------+
                                                                   |
                       PR status check: GREEN -> merge allowed  <--+
                                        RED   -> merge blocked
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CI | Automatic build/test on each change | हर change पर auto build/test |
| Pipeline | Ordered automatic checks | क्रमबद्ध automatic checks |
| Runner | Machine that executes jobs | job चलाने वाली machine |
| Status check | Pass/fail shown on PR | PR पर pass/fail |
| Branch protection | Rules blocking bad merges | खराब merges रोकने के नियम |
| Merge queue | Tests final merge result | final result टेस्ट करने वाली queue |
| Flaky test | Test that sometimes fails randomly | कभी-कभी random fail होने वाला test |

---

## ⚡ 3-Line Summary
English: CI builds and tests every change automatically on a clean machine and blocks bad merges.
A typical pipeline is checkout, setup, cache, install, lint, type-check, test, and build.
Keep it fast, deterministic, least-privilege, and enforced by branch protection.
Hindi: CI हर change को साफ़ machine पर अपने आप build और test करता है और खराब merges रोकता है।
सामान्य pipeline: checkout, setup, cache, install, lint, type-check, test और build।
इसे तेज़, deterministic, least-privilege रखें और branch protection से अनिवार्य करें।

---

## ➡️ Next Topic
**302. Trigger on Push + PR** — the first decision in any pipeline is when it should run.
