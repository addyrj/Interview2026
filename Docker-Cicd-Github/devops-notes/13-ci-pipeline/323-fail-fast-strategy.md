# 323. Fail Fast Strategy
# हिंदी में: Fail Fast Strategy (जल्दी fail करो, जल्दी सीखो)

---

## 🔵 Simple Definition (English)
**Fail fast** means arranging a CI pipeline so that the cheapest and quickest checks (lint, type-check, unit tests) run first, and the whole run stops as soon as something breaks. In GitHub Actions there are two levers: job order with `needs:` and the matrix setting `strategy.fail-fast`.

## 🔵 सरल परिभाषा (Hindi)
**Fail fast** का मतलब है CI pipeline ऐसी बनाना कि सबसे सस्ते और तेज़ checks (lint, type-check, unit tests) पहले चलें, और जैसे ही कुछ टूटे पूरा run रुक जाए। GitHub Actions में दो तरीके हैं: `needs:` से job का क्रम, और matrix का `strategy.fail-fast` setting।

---

## 🔴 Problem it Solves
Without fail fast, a typo in a lint rule is discovered only after a 12-minute Docker build and a 9-minute integration test suite have finished. Runner minutes are wasted (private repos pay per minute), the developer waits for feedback, and the PR queue gets slow. In a matrix (Node 18/20/22), if one version fails, the other two keep running even though the PR is already red.

## 🔴 यह क्यों बना? (Hindi)
Fail fast के बिना lint की एक छोटी गलती 12 मिनट के Docker build और 9 मिनट के integration test के बाद पता चलती है। Runner minutes बर्बाद होते हैं (private repo में हर minute का पैसा लगता है), developer feedback का इंतज़ार करता है और PR queue धीमी हो जाती है। Matrix (Node 18/20/22) में एक version fail हो जाए तब भी बाकी दो चलते रहते हैं जबकि PR पहले से red है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Order checks by cost: lint (20s) -> unit tests (1m) -> integration (5m) -> docker build (8m)
Step 2 → Put the cheap job first; expensive jobs use `needs: [lint]` so they never start if lint fails
Step 3 → Inside a matrix, `fail-fast: true` (default) cancels sibling jobs when one fails
Step 4 → Inside a job, steps stop at first non-zero exit code automatically (default behaviour)
Step 5 → Use `concurrency` + `cancel-in-progress` so a newer push cancels the older, now-useless run
Step 6 → Choose `fail-fast: false` only when you WANT the full compatibility report
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Checks को cost के हिसाब से लगाओ: lint (20s) -> unit tests (1m) -> integration (5m) -> docker build (8m)
Step 2 → सस्ता job पहले रखो; महंगे jobs में `needs: [lint]` लगाओ ताकि lint fail होने पर वे शुरू ही न हों
Step 3 → Matrix में `fail-fast: true` (default) एक fail होते ही बाकी sibling jobs cancel कर देता है
Step 4 → Job के अंदर कोई step non-zero exit code दे तो आगे के steps अपने आप रुक जाते हैं
Step 5 → `concurrency` + `cancel-in-progress` से नया push पुराने बेकार run को cancel कर देता है
Step 6 → `fail-fast: false` तभी रखो जब तुम्हें पूरी compatibility report चाहिए
```

---

## 🟡 Real World Example
A Swiggy-style food-ordering backend on a VPS has 400 unit tests (45 s), 60 integration tests with Postgres (6 min) and a Docker build (7 min). Earlier every push ran everything in parallel; a failing ESLint rule still burned 13 minutes of runner time. After restructuring, `lint` and `unit` run first; `integration` and `docker` wait via `needs`. A broken lint now gives red feedback in 25 seconds and the heavy jobs never start.

## 🟡 Real Example Hindi mein
VPS पर चल रहे Swiggy-जैसे food-ordering backend में 400 unit tests (45 s), Postgres वाले 60 integration tests (6 min) और Docker build (7 min) हैं। पहले हर push पर सब कुछ parallel चलता था; ESLint की एक गलती पर भी 13 मिनट का runner time जल जाता था। Restructure के बाद `lint` और `unit` पहले चलते हैं; `integration` और `docker` `needs` से इंतज़ार करते हैं। अब lint टूटे तो 25 सेकंड में red feedback मिलता है और भारी jobs शुरू ही नहीं होते।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/ci-basic.yml
name: CI Basic                      # name shown in the Actions tab
on:                                 # events that trigger the workflow
  pull_request:                     # run on every pull request
    branches: [main]                # only PRs that target main
jobs:                               # all jobs of this workflow
  lint:                             # cheap job runs first
    runs-on: ubuntu-latest          # GitHub hosted Linux runner
    steps:                          # ordered steps
      - uses: actions/checkout@v4   # download repository code (example version, update as needed)
      - uses: actions/setup-node@v4 # install Node.js
        with:                       # inputs for the action
          node-version: 20          # Node version to use
          cache: npm                # cache ~/.npm using package-lock.json
      - run: npm ci                 # clean, reproducible install
      - run: npm run lint           # non-zero exit fails the job and stops later steps
  test:                             # expensive job
    needs: lint                     # does NOT start unless lint succeeded (fail fast)
    runs-on: ubuntu-latest          # runner for this job
    steps:                          # steps of the test job
      - uses: actions/checkout@v4   # get code again (jobs do not share a workspace)
      - uses: actions/setup-node@v4 # install Node again
        with:                       # inputs
          node-version: 20          # same Node version
          cache: npm                # restore npm cache
      - run: npm ci                 # install dependencies
      - run: npm test               # run unit tests
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/ci-fail-fast.yml
name: CI Fail Fast                  # workflow name
on:                                 # triggers
  pull_request:                     # on PRs
    branches: [main]                # targeting main
  push:                             # and on pushes
    branches: [main]                # to main
concurrency:                        # prevent duplicate runs of the same ref
  group: ci-${{ github.workflow }}-${{ github.ref }}  # one group per workflow+branch
  cancel-in-progress: true          # new push cancels the old run = fail fast on stale work
permissions:                        # least privilege for GITHUB_TOKEN
  contents: read                    # only read the repo
jobs:                               # job graph
  lint:                             # stage 1: seconds
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 5              # hard cap, a hung lint must not eat 6 hours
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-node@v4 # setup node
        with:                       # inputs
          node-version: 20          # Node 20
          cache: npm                # npm cache
      - run: npm ci                 # install
      - run: npm run lint           # ESLint
      - run: npx tsc --noEmit       # type-check without emitting files
  unit:                             # stage 2: unit tests in a matrix
    needs: lint                     # wait for lint
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 10             # cap
    strategy:                       # matrix settings
      fail-fast: true               # one failing version cancels the others (default, explicit for clarity)
      matrix:                       # variants
        node: [18, 20, 22]          # Node versions to support
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-node@v4 # setup node
        with:                       # inputs
          node-version: ${{ matrix.node }}  # version from matrix
          cache: npm                # cache
      - run: npm ci                 # install
      - run: npm test -- --bail     # Jest --bail stops after first failing test suite
  integration:                      # stage 3: slow, with Postgres
    needs: [unit]                   # only after unit tests pass
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 15             # cap
    services:                       # sidecar containers
      postgres:                     # service name = hostname
        image: postgres:16          # example tag, pin and update
        env:                        # container env
          POSTGRES_PASSWORD: test   # throwaway CI password (not a real secret)
        ports: ['5432:5432']        # expose to the runner
        options: >-                 # wait until DB is ready
          --health-cmd pg_isready --health-interval 5s --health-retries 10
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-node@v4 # setup node
        with:                       # inputs
          node-version: 20          # Node 20
          cache: npm                # cache
      - run: npm ci                 # install
      - run: npm run test:integration  # integration tests
        env:                        # step env
          DATABASE_URL: postgres://postgres:test@localhost:5432/postgres  # CI db url
  docker:                           # stage 4: most expensive
    needs: [integration]            # only if everything before is green
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 20             # cap
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - run: docker build -t app:ci .  # build image to prove Dockerfile works (no push here)
```

---

## 🟠 My Stack Integration
For Node.js + React + FastAPI on a VPS behind Nginx, run the cheap gate (`eslint`, `tsc`, `ruff`) first and only then the Docker build whose image you later pull on the VPS. A failure before the build means a broken image can never reach the registry, so the VPS deploy job (which `needs` everything) never fires.

```yaml
# Excerpt: fast gate for both services, expensive build only after both pass
jobs:                               # jobs map
  lint-api:                         # FastAPI lint
    runs-on: ubuntu-latest          # runner
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-python@v5  # python
        with: { python-version: '3.12', cache: pip }  # version + pip cache
      - run: pip install ruff       # linter
      - run: ruff check .           # fails fast on style/bug rules
  lint-web:                         # React lint
    runs-on: ubuntu-latest          # runner
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-node@v4 # node
        with: { node-version: 20, cache: npm }  # version + cache
      - run: npm ci && npm run lint # install and lint
  build-images:                     # expensive
    needs: [lint-api, lint-web]     # both gates must be green
    runs-on: ubuntu-latest          # runner
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - run: docker build -t api ./api && docker build -t web ./web  # build both images
```

Security: set `permissions: contents: read` at workflow level so a compromised lint step cannot push code; fail fast also limits the time untrusted PR code can run.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running every job in parallel with no `needs`, so lint failures still pay for the Docker build.
✅ Correct: Chain expensive jobs behind cheap ones with `needs:`.

❌ Mistake 2: Setting `fail-fast: false` everywhere "to be safe" and then waiting for 3 more doomed matrix legs.
✅ Correct: Keep the default `true` for gating PRs; use `false` only for nightly compatibility reports.

❌ Mistake 3: Using `continue-on-error: true` on a test step to "keep going", which hides failures and turns the PR green.
✅ Correct: Let the step fail; if you need cleanup, use `if: always()` or `if: failure()` on a separate step.

❌ Mistake 4: Forgetting `concurrency`, so five pushes in a minute create five full runs.
✅ Correct: Add `cancel-in-progress: true` on PR workflows (but not on deploy workflows).

---

## 🧠 Tricky Interview Question
**Q:** A matrix of Node 18/20/22 has `fail-fast: true`. Node 22 fails in 30 s. What happens to Node 18 and 20 that were already running, and what does the PR show?

Answer: GitHub cancels the in-progress sibling jobs, and they show as "cancelled", not "failed". The PR check is red because at least one leg failed. The trap: a cancelled leg proves nothing about whether Node 18 passes, so a developer might fix 22 and discover a separate Node 18 failure on the next run. If you need the full picture on every run, set `fail-fast: false`.

---

## ⚫ Interview Questions + Answers

Q1: What is fail fast in CI?
A1: Ordering and configuring a pipeline so the quickest checks run first and the run stops at the first failure, giving fast feedback and saving runner minutes.

Q2: What is the default value of `strategy.fail-fast`?
A2: `true`. When any matrix job fails, GitHub cancels the remaining in-progress and queued matrix jobs.

Q3: How do you stop a Docker build from running if lint fails?
A3: Put `needs: lint` (or the list of gate jobs) on the build job. If a needed job fails or is skipped, the dependent job is skipped.

Q4: Difference between `fail-fast` and `continue-on-error`?
A4: `fail-fast` controls whether sibling matrix jobs are cancelled. `continue-on-error` makes a single job or step failure not fail the workflow. They solve opposite problems.

Q5: Does `concurrency: cancel-in-progress` belong on a deploy workflow?
A5: Generally no. Cancelling a half-finished deploy can leave the VPS in a mixed state. Use `cancel-in-progress: false` there so deploys queue up.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- PR checks gate merging and developers wait on them.
- You pay for runner minutes (private repos, large runners).
- Pipelines have clear cheap-to-expensive stages.

❌ Avoid when:
- You need a full compatibility matrix report (library authors): use `fail-fast: false`.
- Flaky infra means one failure is not conclusive; combine with retries first.
- Deploy workflows where cancellation can corrupt state.

---

## 📊 Visual Diagram
```
push / PR
   |
   v
+--------+   fail   +-------------------------+
| lint   |--------->| STOP: red in ~25 sec    |
+--------+          +-------------------------+
   | pass
   v
+--------+   fail   +-------------------------+
| unit   |--------->| STOP: siblings cancelled|
| 18|20|22          +-------------------------+
+--------+
   | pass
   v
+-------------+  fail
| integration |------> STOP
+-------------+
   | pass
   v
+--------------+
| docker build |  (most expensive, runs last)
+--------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fail fast | Stop early on first failure | पहली failure पर रुक जाना |
| `needs` | Job dependency | job निर्भरता |
| Matrix | Same job over many variants | कई variants पर वही job |
| `cancel-in-progress` | Cancel older runs of same group | पुराने run रद्द करना |
| Runner minutes | Billed CI compute time | CI compute का billed समय |

---

## ⚡ 3-Line Summary
English: Run cheap checks first and chain expensive jobs with `needs`.
English: Matrix `fail-fast: true` cancels siblings after the first failure; `concurrency` cancels stale runs.
English: Never hide failures with `continue-on-error`; do not cancel deploys mid-way.

Hindi: सस्ते checks पहले चलाओ और महंगे jobs को `needs` से जोड़ो।
Hindi: Matrix का `fail-fast: true` पहली failure के बाद बाकी legs cancel करता है; `concurrency` पुराने runs cancel करता है।
Hindi: `continue-on-error` से failures मत छुपाओ; deploy को बीच में cancel मत करो।

---

## ➡️ Next Topic
**324. Timeout Configuration** — fail fast handles known failures; timeouts handle jobs that hang forever.
