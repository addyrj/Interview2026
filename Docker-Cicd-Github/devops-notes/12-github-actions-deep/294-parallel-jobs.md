# 294. Parallel Jobs
# हिंदी में: Parallel Jobs (एक साथ चलने वाले jobs)

---

## 🔵 Simple Definition (English)
In GitHub Actions, jobs in one workflow run **in parallel by default**. A job waits only if it declares `needs:`. Each parallel job gets its own runner, so lint, unit tests, type-check and security scan can run at the same time and finish in the time of the slowest one. Limits come from your plan's concurrent-job quota, `strategy.max-parallel` for matrices, and `concurrency` groups for whole workflows or jobs.

## 🔵 सरल परिभाषा (Hindi)
GitHub Actions में एक workflow के jobs **default रूप से parallel** चलते हैं। Job तभी इंतज़ार करता है जब वह `needs:` लिखे। हर parallel job को अपना runner मिलता है, इसलिए lint, unit tests, type-check और security scan एक साथ चलकर सबसे धीमे job जितने समय में पूरे हो जाते हैं। सीमाएँ आती हैं plan के concurrent-job quota, matrix के `strategy.max-parallel`, और पूरे workflow/job के `concurrency` groups से।

---

## 🔴 Problem it Solves
A pipeline that does `lint -> test -> build -> scan` in one long job takes 18 minutes and gives feedback late. Developers wait, merge queues grow, and a failing lint is found after the tests ran. Splitting independent work into parallel jobs cuts wall-clock time and gives faster, more specific failures.

## 🔴 यह क्यों बना? (Hindi)
एक लंबे job में `lint -> test -> build -> scan` करने वाली pipeline 18 मिनट लेती है और feedback देर से आता है। Developers इंतज़ार करते हैं, merge queue बढ़ती है, और lint की गलती tests चलने के बाद पता चलती है। स्वतंत्र काम को parallel jobs में बाँटने से दीवार-घड़ी का समय घटता है और failures जल्दी व साफ़ मिलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Workflow starts; GitHub reads all jobs
Step 2 → Jobs without "needs" are queued immediately, all at once
Step 3 → Each job is assigned its own runner (VM) as capacity allows
         (free plan: 20 concurrent jobs, Linux/Windows; macOS fewer; paid plans more)
Step 4 → If capacity is exhausted, extra jobs wait "Queued"
Step 5 → Jobs run independently; one failing does not stop the others
         (except matrix fail-fast or manual cancel)
Step 6 → Workflow ends when every job finishes; status = failure if any failed
Step 7 → Total time ~ slowest path, not the sum
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Workflow शुरू होता है; GitHub सारे jobs पढ़ता है
Step 2 → बिना "needs" वाले jobs तुरंत, सब एक साथ queue होते हैं
Step 3 → हर job को capacity के हिसाब से अपना runner (VM) मिलता है
         (free plan: 20 concurrent jobs, Linux/Windows; macOS कम; paid plans में ज़्यादा)
Step 4 → Capacity खत्म हो तो बाकी jobs "Queued" में इंतज़ार करते हैं
Step 5 → Jobs स्वतंत्र चलते हैं; एक का fail होना बाकी को नहीं रोकता
         (matrix fail-fast या manual cancel को छोड़कर)
Step 6 → हर job खत्म होने पर workflow खत्म; कोई fail तो status = failure
Step 7 → कुल समय ~ सबसे धीमा रास्ता, जोड़ नहीं
```
(Concurrency numbers are plan dependent and change; check the current GitHub billing docs.)

---

## 🟡 Real World Example
An Indian fintech's PR pipeline had 5 independent checks: ESLint (2 min), Jest unit tests (6 min), TypeScript check (3 min), `npm audit` + CodeQL (8 min), and Docker build (7 min). Sequentially that is 26 minutes. Run in parallel it is about 8 minutes, bounded by the security scan. Developers get lint and type errors at minute 2-3, long before the slow scan completes.

## 🟡 Real Example Hindi mein
एक भारतीय fintech की PR pipeline में 5 स्वतंत्र checks थे: ESLint (2 मिनट), Jest unit tests (6), TypeScript check (3), `npm audit` + CodeQL (8), और Docker build (7)। क्रम से चलाएँ तो 26 मिनट। Parallel चलाने पर लगभग 8 मिनट, जो security scan से तय होता है। Developers को lint और type errors मिनट 2-3 पर ही मिल जाते हैं, धीमे scan के पूरा होने से बहुत पहले।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/parallel-basic.yml
name: parallel-basic                      # workflow name
on: [pull_request]                        # run on PRs
jobs:
  lint:                                   # no needs => starts immediately
    runs-on: ubuntu-latest                # own runner
    steps:
      - uses: actions/checkout@v4         # code
      - run: echo "linting..."            # replace with: npm run lint
  test:                                   # also no needs => runs at the same time
    runs-on: ubuntu-latest                # another runner
    steps:
      - uses: actions/checkout@v4
      - run: echo "testing..."            # replace with: npm test
  typecheck:                              # third parallel job
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "type-checking..."      # replace with: npx tsc --noEmit
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/parallel-advanced.yml
# Fast-feedback parallel checks, cancel stale runs, split slow tests into shards
name: parallel-advanced                   # workflow name
on:
  pull_request:                           # every PR update
concurrency:
  group: pr-${{ github.event.pull_request.number }}   # one active run per PR
  cancel-in-progress: true                # cancel older run when a new commit arrives
permissions:
  contents: read                          # least privilege
defaults:
  run:
    shell: bash                           # consistent shell
jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10                   # cap cost
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run lint                 # fastest check, gives feedback first
  typecheck:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx tsc --noEmit             # compile check only
  unit:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      fail-fast: false                    # see every failing shard
      matrix:
        shard: [1, 2, 3]                  # three parallel slices of the test suite
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx jest --shard=${{ matrix.shard }}/3 --ci   # Jest 28+ supports --shard
  api-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12', cache: pip, cache-dependency-path: api/requirements.txt }
      - run: pip install -r api/requirements.txt
      - run: pytest api -q                # FastAPI tests in parallel with the Node ones
  security:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - run: npm audit --audit-level=high # fails on high+ vulnerabilities (needs network)
  ready:                                  # one gate for branch protection
    if: always()                          # run even if some jobs failed
    needs: [lint, typecheck, unit, api-tests, security]
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo '${{ toJSON(needs) }}'     # print all results for debugging
          [ "${{ contains(needs.*.result, 'failure') }}" = "false" ] && [ "${{ contains(needs.*.result, 'cancelled') }}" = "false" ]
```

---

## 🟠 My Stack Integration
- **Node.js + FastAPI monorepo**: separate parallel jobs per language; each with its own cache.
- **React**: `lint`, `typecheck`, `unit`, `build` run together; `build` artifact feeds a later `e2e` job.
- **Docker**: image build in parallel with tests (build only pushes after `ready`).
- **AWS/VPS cost control**: `concurrency` prevents two deploys to the same VPS racing each other.

```yaml
# Snippet: deploy lock so two pipelines never deploy simultaneously
  deploy:
    needs: ready
    concurrency:
      group: deploy-production            # shared lock name across runs
      cancel-in-progress: false           # queue, never kill a running deploy
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploying one at a time"
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Adding `needs:` out of habit between independent jobs, which makes them sequential.
✅ Correct: Add `needs` only for real data/order dependencies.

❌ Mistake 2: Each parallel job repeats an expensive setup (install, build) with no cache.
✅ Correct: Cache dependencies, or build once and share artifacts.

❌ Mistake 3: Requiring five separate status checks in branch protection, then renaming a job and getting stuck.
✅ Correct: Use a single `ready` aggregator.

❌ Mistake 4: Parallel jobs that touch the same external resource (shared test database, same S3 prefix).
✅ Correct: Isolate (service containers per job, unique prefixes using `${{ github.run_id }}`).

❌ Mistake 5: Forgetting `cancel-in-progress` for PR runs, so pushes pile up and burn minutes.
✅ Correct: Concurrency group per PR, cancel older runs (not for deploy jobs).

---

## 🧠 Tricky Interview Question
You have 30 parallel jobs but only 20 start at once, and the PR takes much longer than the slowest job. Why, and what are the options?

Answer: Concurrent job quota (20 on the free plan; plan dependent) means 10 jobs sit in Queued, so total time is roughly two waves. Options: reduce the number of jobs (merge tiny ones, a job has about 30-60 seconds of startup overhead), use `max-parallel` to avoid one matrix starving others, upgrade plan or use larger runners / self-hosted runners, and cancel stale runs via `concurrency`. Parallel does not mean unlimited; the tradeoff is startup cost per job vs. wall-clock savings.

---

## ⚫ Interview Questions + Answers

Q1: Are jobs parallel or sequential by default?
A1: Parallel. Sequential order requires `needs`.

Q2: Do parallel jobs share files?
A2: No. Each has its own runner and file system. Use artifacts/outputs.

Q3: What stops two runs from deploying simultaneously?
A3: A `concurrency` group with `cancel-in-progress: false` (queues; note only one pending run is kept per group, older pending ones are cancelled).

Q4: How does a failing job affect others?
A4: Independent jobs continue. Jobs that `needs` it are skipped unless `if: always()` / `!cancelled()` is used.

Q5: How to speed up one slow test job?
A5: Shard it with a matrix and a test runner that supports sharding (Jest `--shard`, pytest-xdist or `pytest-split`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Checks are independent (lint, type, tests, security).
- You want fast feedback.
- Splitting long test suites.

❌ Avoid when:
- Jobs are tiny (startup overhead dominates).
- Jobs share mutable external state.
- Cost of runner minutes is a concern and the job is already fast.

---

## 📊 Visual Diagram
```
 time ------------------------------------------------------>
 lint        |====|
 typecheck   |=====|
 unit[1]     |==========|
 unit[2]     |===========|
 unit[3]     |==========|
 api-tests   |=============|
 security    |===================|     <- slowest decides total
                                  \
 ready (needs all, if: always)     +--> |=|  gate
 deploy (needs ready, concurrency lock)   +-> |======|
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Parallel job | Job running at the same time | साथ चलने वाला job |
| Runner | Machine executing a job | Job चलाने वाली machine |
| Queued | Waiting for capacity | क्षमता का इंतज़ार |
| `concurrency` | Lock/cancel group | Lock/cancel group |
| Shard | Slice of a test suite | Test suite का हिस्सा |
| Wall-clock time | Real elapsed time | असली बीता समय |

---

## ⚡ 3-Line Summary
English: Jobs without `needs` run in parallel on separate runners, finishing in the slowest job's time.
English: Quotas, `max-parallel` and `concurrency` control the limits; shard slow tests with a matrix.
English: Use an aggregator gate and isolate shared resources.
Hindi: बिना `needs` वाले jobs अलग runners पर parallel चलते हैं और सबसे धीमे job जितना समय लेते हैं।
Hindi: Quota, `max-parallel` और `concurrency` सीमाएँ तय करते हैं; धीमे tests को matrix से shard करें।
Hindi: Aggregator gate रखें और साझा resources अलग रखें।

---

## ➡️ Next Topic
**295. Sequential Jobs** — forcing order with `needs` for build, test, deploy flows.
