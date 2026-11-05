# 236. Job — What it is
# हिंदी में: Job — यह क्या है

---

## 🔵 Simple Definition (English)
A **job** is a set of steps that run together on the same runner (one fresh virtual machine or container). A workflow has one or more jobs. By default jobs run in parallel; you can order them with `needs:`.

## 🔵 सरल परिभाषा (Hindi)
**Job** steps का एक समूह है जो एक ही runner (एक नई virtual machine या container) पर साथ चलते हैं। एक workflow में एक या अधिक jobs होते हैं। Default रूप से jobs parallel चलते हैं; `needs:` से उन्हें क्रम में रखा जा सकता है।

---

## 🔴 Problem it Solves
A single long script that lints, tests, builds, scans and deploys is slow (everything serial), hard to debug (which part failed?), and hard to re-run (one flaky test forces a full rebuild). Also build and deploy need different trust levels: tests should not see production secrets.

Jobs split a pipeline into independent units: parallel for speed, isolated for security, re-runnable for convenience, and with clear dependencies.

## 🔴 यह क्यों बना? (Hindi)
एक लंबी script जो lint, test, build, scan और deploy सब करे वह धीमी है (सब एक के बाद एक), debug करना कठिन है (कौन सा हिस्सा fail हुआ?), और दोबारा चलाना कठिन (एक flaky test से पूरा rebuild)। साथ ही build और deploy के trust levels अलग हैं: tests को production secrets नहीं दिखने चाहिए।

Jobs pipeline को स्वतंत्र इकाइयों में बाँटते हैं: गति के लिए parallel, सुरक्षा के लिए isolated, सुविधा के लिए re-runnable, और साफ dependencies के साथ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Workflow run starts; every job without `needs` is queued immediately
Step 2 → Each job waits for a runner matching its `runs-on` label
Step 3 → Runner starts clean (fresh VM), job steps execute in order
Step 4 → When a job ends, its runner is destroyed (hosted runners)
Step 5 → Jobs that `needs` it start only if it SUCCEEDED (unless `if: always()`)
Step 6 → Data moves between jobs through `outputs`, artifacts or cache
Step 7 → Run status = all jobs succeeded? success : failure
```

Key job-level keys: `runs-on`, `needs`, `if`, `env`, `outputs`, `strategy` (matrix), `timeout-minutes`, `permissions`, `environment`, `services`, `container`, `continue-on-error`, `concurrency`, `defaults`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Workflow run शुरू होता है; जिन jobs में `needs` नहीं, वे तुरंत queue होते हैं।
Step 2 → हर job अपने `runs-on` label वाले runner का इंतज़ार करता है।
Step 3 → Runner साफ़ शुरू होता है (नई VM), job के steps क्रम से चलते हैं।
Step 4 → Job खत्म होते ही runner नष्ट हो जाता है (hosted runners में)।
Step 5 → जो jobs उस पर `needs` रखते हैं वे तभी शुरू होते हैं जब वह SUCCESS हुआ (जब तक `if: always()` न हो)।
Step 6 → Jobs के बीच data `outputs`, artifacts या cache से जाता है।
Step 7 → Run status = सारे jobs सफल हों तो success, नहीं तो failure।

---

## 🟡 Real World Example
A Zomato-style checkout service pipeline:
- `lint` and `unit-test` run in parallel (2 minutes total instead of 4 serial).
- `integration-test` spins up Postgres and Redis as **service containers** inside its own job.
- `build-image` needs all three, builds and pushes the Docker image.
- `deploy-prod` needs `build-image`, uses `environment: production` so a manager must approve first.

If `integration-test` flakes, you click "Re-run failed jobs" and only that job (and the ones depending on it) rerun, saving minutes.

## 🟡 Real Example Hindi mein
Zomato जैसी checkout service की pipeline: `lint` और `unit-test` parallel चलते हैं (4 मिनट की जगह कुल 2 मिनट)। `integration-test` अपने job में Postgres और Redis **service containers** के रूप में चलाता है। `build-image` तीनों पर `needs` रखता है और Docker image बनाकर push करता है। `deploy-prod` `build-image` पर निर्भर है और `environment: production` से पहले manager की approval चाहिए। अगर `integration-test` flake करे तो "Re-run failed jobs" दबाएँ और सिर्फ वही (और उस पर निर्भर jobs) दोबारा चलते हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/jobs-basic.yml
name: Jobs Basic                      # Workflow name
on: [push]                            # Run on every push
jobs:                                 # Section holding all jobs
  lint:                               # Job id 1 (letters, numbers, - and _ only)
    name: Lint code                   # Human-friendly name in UI
    runs-on: ubuntu-latest            # Runner for this job
    steps:
      - uses: actions/checkout@v4     # Get code
      - run: echo "linting..."        # Pretend lint step
  test:                               # Job id 2 runs in parallel with lint
    name: Unit tests                  # UI name
    runs-on: ubuntu-latest            # Its own separate runner
    steps:
      - uses: actions/checkout@v4     # Needs its own checkout
      - run: echo "testing..."        # Pretend test step
  build:                              # Job id 3
    name: Build                       # UI name
    needs: [lint, test]               # Wait for BOTH to succeed
    runs-on: ubuntu-latest            # Another runner
    steps:
      - run: echo "building..."       # Pretend build step
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/jobs-advanced.yml
name: Jobs Advanced                   # Shows outputs, services, matrix, environment
on:
  push:
    branches: [main]
permissions:
  contents: read                      # Workflow-wide minimum
jobs:
  version:                            # Job that produces an output
    runs-on: ubuntu-latest
    outputs:                          # Values other jobs may read
      tag: ${{ steps.vars.outputs.tag }}   # Map step output to job output
    steps:
      - id: vars                      # Step id used to reference its outputs
        run: echo "tag=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"   # First 7 chars of commit SHA
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15               # Stop hung jobs
    strategy:
      matrix:
        node: [18, 20]                # Two parallel copies of this job
    services:                         # Containers started next to the job
      postgres:
        image: postgres:16            # Example tag, update as needed
        env:
          POSTGRES_PASSWORD: testpass # Test-only password, not a real secret
        ports: ["5432:5432"]          # Expose to the runner
        options: >-                   # Docker health check so job waits until DB is ready
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
    env:
      DATABASE_URL: postgres://postgres:testpass@localhost:5432/postgres   # App connects via localhost
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}   # Use matrix value
          cache: npm
      - run: npm ci && npm test
  deploy:
    needs: [version, test]            # Wait for both
    runs-on: ubuntu-latest
    environment: production           # Requires reviewers if configured in repo settings
    concurrency: deploy-prod          # Only one deploy at a time
    steps:
      - run: echo "Deploying tag ${{ needs.version.outputs.tag }}"   # Read output of version job
```

---

## 🟠 My Stack Integration
Recommended job layout for your repo (Node API, FastAPI, React, Nginx on a VPS):

```yaml
# .github/workflows/stack-jobs.yml
name: Stack Jobs
on:
  push:
    branches: [main]
jobs:
  api-test:
    runs-on: ubuntu-latest            # Node.js API tests
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm, cache-dependency-path: api/package-lock.json }
      - run: npm ci && npm test
        working-directory: api        # Run inside api/
  fastapi-test:
    runs-on: ubuntu-latest            # Python tests in parallel with the API tests
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -r requirements.txt && pytest
        working-directory: fastapi    # Run inside fastapi/
  web-build:
    runs-on: ubuntu-latest            # React production build
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm, cache-dependency-path: web/package-lock.json }
      - run: npm ci && npm run build
        working-directory: web
  deploy:
    needs: [api-test, fastapi-test, web-build]   # All must pass
    runs-on: ubuntu-latest
    environment: production           # Gate with approval + environment secrets
    steps:
      - run: echo "ssh VPS, docker compose pull and up -d"   # Real SSH step comes later
```

Security: put production secrets in the **environment** (not repo-wide) so only the `deploy` job can read them, and only after approval. Test jobs then never see them.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting `npm ci` output (`node_modules`) from one job to exist in another.
✅ Correct: Use cache for dependencies; artifacts for build output.

❌ Mistake 2: Writing `needs: build` and forgetting that a skipped or failed `build` makes this job skip.
✅ Correct: Use `if: ${{ !cancelled() }}` or `always()` when you need cleanup/notification to run anyway.

❌ Mistake 3: Using a job id with spaces, like `build and test`.
✅ Correct: IDs use letters, digits, `-`, `_`, and start with a letter or `_`; use `name:` for the pretty label.

❌ Mistake 4: One giant job that does everything.
✅ Correct: Split by purpose; parallelise independent work.

---

## 🧠 Tricky Interview Question
"Job `deploy` has `needs: [test]`. `test` is a matrix with Node 18 and 20, and the Node 18 leg fails. What happens to `deploy`?"

Answer: The matrix job counts as failed if any leg fails (unless that leg is marked `continue-on-error: true` or the matrix uses `fail-fast: false` with only informational legs), so `deploy` is **skipped**. Also note `fail-fast: true` (the default) cancels the other in-progress legs as soon as one fails. If Node 18 is only "nice to have", mark it with `matrix.experimental` and `continue-on-error: ${{ matrix.experimental }}`.

---

## ⚫ Interview Questions + Answers

Q1: Do jobs run in parallel or sequentially by default?
A1: Parallel. Use `needs` for dependencies.

Q2: How do you pass a value from one job to another?
A2: Write to `$GITHUB_OUTPUT` in a step with an `id`, expose it in the job `outputs:`, then read `needs.<job>.outputs.<name>`.

Q3: How do you share files between jobs?
A3: `actions/upload-artifact` and `actions/download-artifact`, or a cache for dependencies.

Q4: What is the default job timeout?
A4: 360 minutes (6 hours) for GitHub-hosted runners; set `timeout-minutes` lower to catch hangs early.

Q5: What are service containers?
A5: Docker containers (Postgres, Redis...) started by the job on Linux runners and reachable at `localhost` (when job runs on the runner) or by service name (when job runs in a `container:`).

---

## 🔷 When to Use + When Not to Use
✅ Use multiple jobs when:
- Work can run in parallel.
- Parts need different runners, permissions or environments.
- You want selective re-runs and clear failure location.

❌ Avoid when:
- Setup cost (checkout + install) dominates and tasks are tiny; combine steps.
- Passing large data between jobs would cost more than it saves.

---

## 📊 Visual Diagram

```
         workflow run
              |
   +----------+-----------+
   v                      v
 [lint]                 [test x2 matrix]
 runner A               runner B1  runner B2
   |                      |          |
   +----------+-----------+----------+
              | needs: [lint, test]
              v
          [build-image]  runner C
              |  needs
              v
          [deploy] runner D  (environment: production, approval)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Job | Steps on one runner | एक runner पर steps |
| needs | Dependency between jobs | jobs की निर्भरता |
| outputs | Values a job exposes | job द्वारा दिए गए values |
| Matrix | Many copies with different values | अलग values से कई copies |
| Service container | Helper container like DB | सहायक container जैसे DB |
| Environment | Named deploy target with rules | नियमों वाला deploy target |
| Artifact | Saved files from a job | job से सहेजी files |

---

## ⚡ 3-Line Summary
English: A job is a group of steps on one fresh runner; jobs run in parallel unless `needs` orders them.
Share data with outputs, artifacts or cache; never assume a shared disk.
Split jobs for speed, isolation and safer secrets.

Hindi: Job एक नए runner पर steps का समूह है; `needs` के बिना jobs parallel चलते हैं।
Data outputs, artifacts या cache से share करें; shared disk न मानें।
गति, isolation और सुरक्षित secrets के लिए jobs बाँटें।

---

## ➡️ Next Topic
**237. Step — What it is** — the smallest unit inside a job: `run` vs `uses`, step ids, environment, conditions and exit codes.

---
