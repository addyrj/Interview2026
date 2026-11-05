# 310. Run Unit Tests (Jest/pytest)
# हिंदी में: Unit Tests चलाना (Jest/pytest) CI में

---

## 🔵 Simple Definition (English)
Running unit tests in CI means a GitHub Actions job installs dependencies and executes your fast, isolated tests (Jest for Node.js/React, pytest for FastAPI) on every push and pull request. If any test fails, the job turns red and the merge is blocked.

## 🔵 सरल परिभाषा (Hindi)
CI में unit tests चलाने का मतलब है कि GitHub Actions का job हर push और pull request पर dependencies install करके आपके तेज़, isolated tests (Node.js/React के लिए Jest, FastAPI के लिए pytest) चलाता है। कोई भी test fail हो तो job लाल हो जाता है और merge रुक जाता है।

---

## 🔴 Problem it Solves
Before CI, developers ran tests "on my machine" or forgot to run them. A broken function reached production and was found by customers. Local machines also differ (Node 18 vs 20, Python 3.10 vs 3.12), so "works for me" was not proof. CI runs the same tests on a clean runner every time.

## 🔴 यह क्यों बना? (Hindi)
CI से पहले developers "मेरी machine पर चल रहा है" कहकर tests चलाते थे या चलाना भूल जाते थे। टूटा हुआ function production तक पहुँच जाता और customer उसे पकड़ते। Local machines भी अलग होती हैं (Node 18 बनाम 20, Python 3.10 बनाम 3.12), इसलिए "मेरे पास चलता है" कोई सबूत नहीं था। CI हर बार साफ़ runner पर वही tests चलाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developer pushes code / opens a PR  (event: push, pull_request)
Step 2 → GitHub starts a fresh Ubuntu runner (VM)
Step 3 → actions/checkout downloads the code
Step 4 → setup-node / setup-python installs the pinned runtime (+ cache)
Step 5 → npm ci / pip install -r requirements.txt  (exact, reproducible deps)
Step 6 → npm test / pytest runs; exit code 0 = pass, non-zero = fail
Step 7 → Job status (green/red) is reported on the PR as a status check
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Developer code push करता है / PR खोलता है  (event: push, pull_request)
Step 2 → GitHub एक नया Ubuntu runner (VM) शुरू करता है
Step 3 → actions/checkout code download करता है
Step 4 → setup-node / setup-python pinned runtime install करते हैं (+ cache)
Step 5 → npm ci / pip install -r requirements.txt  (सटीक, reproducible deps)
Step 6 → npm test / pytest चलता है; exit code 0 = pass, non-zero = fail
Step 7 → Job का status (हरा/लाल) PR पर status check बनकर दिखता है
```

---

## 🟡 Real World Example
A Swiggy-like order service: the pricing function `calculateTotal(items, coupon)` is covered by 40 Jest tests. A developer changes GST logic and accidentally breaks coupon rounding. The PR job `unit-tests` fails in 25 seconds with a clear diff of expected vs received value. The bug never reaches your VPS.

## 🟡 Real Example Hindi mein
Swiggy जैसी order service: pricing function `calculateTotal(items, coupon)` को 40 Jest tests cover करते हैं। Developer GST logic बदलता है और गलती से coupon rounding तोड़ देता है। PR का `unit-tests` job 25 सेकंड में expected बनाम received value के साफ़ diff के साथ fail हो जाता है। Bug आपके VPS तक पहुँचता ही नहीं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/unit-tests.yml  (Node.js + Jest, basic)
name: Unit Tests                       # Name shown in the Actions tab

on:                                    # When should this workflow run?
  push:                                # On every push...
    branches: [main]                   # ...to main
  pull_request:                        # And on every pull request

jobs:                                  # All jobs of this workflow
  unit-tests:                          # Job id (becomes the status check name)
    runs-on: ubuntu-latest             # GitHub-hosted Linux runner
    steps:                             # Steps run in order
      - uses: actions/checkout@v4      # Download repository code
      - uses: actions/setup-node@v4    # Install Node.js
        with:                          # Inputs of the action
          node-version: 20             # Node 20 LTS (example, update as needed)
          cache: npm                   # Cache ~/.npm using package-lock.json
      - run: npm ci                    # Clean, exact install from lockfile
      - run: npm test -- --ci          # Run Jest; --ci means no interactive/snapshot writes
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/unit-tests.yml  (Jest + pytest, matrix, production style)
name: Unit Tests

on:
  pull_request:                        # Run for every PR
  push:
    branches: [main]                   # And after merge to main

concurrency:                           # Cancel older runs of the same branch
  group: unit-${{ github.ref }}        # One group per branch/PR ref
  cancel-in-progress: true             # New push cancels the stale run

permissions:
  contents: read                       # Least privilege: only read the code

jobs:
  node-tests:
    name: Jest (Node ${{ matrix.node }})   # Visible check name
    runs-on: ubuntu-latest
    timeout-minutes: 10                # Kill hung tests, do not burn minutes
    strategy:
      fail-fast: false                 # Let all matrix legs finish
      matrix:
        node: [18, 20, 22]             # Test on all supported Node versions
    defaults:
      run:
        working-directory: backend     # Node API lives in backend/
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: npm
          cache-dependency-path: backend/package-lock.json   # Lockfile for cache key
      - run: npm ci
      - run: npx jest --ci --runInBand --reporters=default --reporters=jest-junit
        env:
          NODE_ENV: test               # Never use production config in tests
          JEST_JUNIT_OUTPUT_DIR: reports   # jest-junit writes XML here (devDependency)
      - uses: actions/upload-artifact@v4   # Keep test report even when tests fail
        if: always()                   # Run this step on success AND failure
        with:
          name: jest-report-${{ matrix.node }}   # Unique name per matrix leg
          path: backend/reports/       # Folder produced above

  python-tests:
    name: pytest (Python ${{ matrix.python }})
    runs-on: ubuntu-latest
    timeout-minutes: 10
    strategy:
      fail-fast: false
      matrix:
        python: ["3.11", "3.12"]       # Quote versions so 3.10 is not read as 3.1
    defaults:
      run:
        working-directory: api         # FastAPI project folder
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
          cache: pip                   # Cache pip downloads
          cache-dependency-path: api/requirements*.txt
      - run: pip install -r requirements.txt -r requirements-dev.txt   # App + test deps
      - run: pytest -q --maxfail=5 --junitxml=reports/pytest.xml   # Stop after 5 failures
        env:
          APP_ENV: test                # FastAPI reads this to pick test settings
```

---

## 🟠 My Stack Integration
- **Node.js API (Express/Nest):** Jest with `supertest` tests route handlers in memory; no real DB needed for unit tests (mock the repository layer).
- **FastAPI:** `pytest` with `fastapi.testclient.TestClient` and dependency overrides (`app.dependency_overrides`) replace DB/Redis.
- **React/Next.js:** Jest or Vitest with React Testing Library; run with `--ci`.
- **Nginx/VPS/AWS:** Unit tests do NOT touch them. The deploy job (later topics) uses `needs: [unit-tests]` so a red test means no deploy to the VPS.

```yaml
# Gate the deploy on tests in your monorepo workflow
jobs:
  unit-tests:                          # Job defined as above
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "tests here"         # Replace with real test steps
  deploy:
    needs: [unit-tests]                # Wait for unit-tests; skip if it fails
    if: github.ref == 'refs/heads/main'   # Only deploy main
    runs-on: ubuntu-latest
    steps:
      - run: echo "ssh to VPS and docker compose up -d"   # Placeholder deploy
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `npm install` in CI, which can change the lockfile and install different versions.
✅ Correct: Use `npm ci` (fails if lockfile and package.json disagree).

❌ Mistake 2: Running Jest in watch mode (`jest --watch`) or `npm test` that prompts, so the job hangs until timeout.
✅ Correct: Use `--ci` and set `timeout-minutes`.

❌ Mistake 3: Unit tests that call real APIs, real databases, or the internet, making them flaky.
✅ Correct: Mock external calls; real DB belongs in integration tests (topic 311).

❌ Mistake 4: `continue-on-error: true` on the test step "to keep it green".
✅ Correct: Let the job fail; fix or quarantine the flaky test.

❌ Mistake 5: Printing secrets or using production env values in tests.
✅ Correct: Use fake values in `env:`; keep `permissions: contents: read`.

---

## 🧠 Tricky Interview Question
Your tests pass locally and fail in CI only for a date-formatting test. What do you check?

Answer: Time zone and locale. GitHub runners use UTC and `en_US`; your laptop may be IST. Tests that use `new Date()` or `datetime.now()` depend on the machine. Fix by injecting a fixed clock (`jest.useFakeTimers().setSystemTime(...)`, `freezegun` in Python) or setting `TZ: UTC` in `env`. Also check missing env files (`.env` is git-ignored), different Node versions, and file-name case sensitivity (macOS is case-insensitive, Linux is not).

---

## ⚫ Interview Questions + Answers

Q1: Why `npm ci` and not `npm install` in CI?
A1: `npm ci` deletes `node_modules`, installs exactly from `package-lock.json`, and errors on mismatch. It is faster, deterministic and never edits the lockfile.

Q2: What is the difference between unit and integration tests?
A2: Unit tests check one function/class in isolation with mocks and run in milliseconds. Integration tests check several parts together (API + real DB) and are slower. CI runs unit tests first for fast feedback.

Q3: How does the CI know a test failed?
A3: By process exit code. Jest and pytest exit non-zero on failure, and a step with non-zero exit fails the job (the shell runs with `-e` by default).

Q4: How do you speed up unit tests in CI?
A4: Cache dependencies (`cache: npm`), run only changed tests on PRs if suitable (`jest --changedSince`), split with matrix or `--shard=1/3` (Jest) / `pytest-xdist -n auto`, and cancel stale runs with `concurrency`.

Q5: A test is flaky 1 in 20 runs. What do you do?
A5: Find the root cause (shared state, timers, ordering, network). Short term, quarantine it with an issue; avoid blind retries because they hide real bugs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every PR and every push to main (always).
- You want fast feedback (under 2-3 minutes) before slower checks.
- You need a deploy gate for your VPS/AWS pipeline.

❌ Avoid when:
- Testing needs a real DB/queue; use integration tests instead.
- Test is a UI visual check; use end-to-end tools (Playwright) in a separate job.
- Do not run huge suites on every tiny docs change; use `paths-ignore` carefully (see topic 321 on required checks).

---

## 📊 Visual Diagram
```
 Developer ──push/PR──▶ GitHub ──▶ Runner (fresh VM)
                                      │
                 ┌────────────────────┼────────────────────┐
                 ▼                    ▼                    ▼
           checkout code        setup runtime         restore cache
                 └────────────────────┬────────────────────┘
                                      ▼
                              npm ci / pip install
                                      ▼
                         ┌────── Jest / pytest ──────┐
                         │ exit 0            exit ≠0 │
                         ▼                           ▼
                   ✅ check green              ❌ check red
                   deploy allowed              merge/deploy blocked
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Unit test | Test of one small unit in isolation | एक छोटे हिस्से का अलग test |
| Exit code | Number returned by a process; 0 = success | process का लौटाया number; 0 = सफल |
| `npm ci` | Clean, lockfile-exact install | lockfile के अनुसार साफ़ install |
| Matrix | Run the same job on many versions | कई versions पर वही job |
| Mock | Fake replacement of a dependency | dependency की नकली जगह |
| Flaky test | Test that sometimes passes, sometimes fails | कभी pass कभी fail होने वाला test |

---

## ⚡ 3-Line Summary
English: CI installs deps on a clean runner and runs Jest/pytest on every push and PR.
English: A non-zero exit code fails the job, which blocks merge and deploy.
English: Use `npm ci`, cache, timeouts and matrix; keep unit tests fast and mocked.
Hindi: CI साफ़ runner पर deps install करके हर push और PR पर Jest/pytest चलाता है।
Hindi: Non-zero exit code job को fail करता है, जिससे merge और deploy रुकते हैं।
Hindi: `npm ci`, cache, timeout और matrix इस्तेमाल करें; unit tests तेज़ और mocked रखें।

Note: workflow YAML above was parsed locally but not executed on GitHub; action versions are examples, update them.

---

## ➡️ Next Topic
311. Run Integration Tests: unit tests mock the database, so next we run tests against real PostgreSQL/MongoDB/Redis using service containers.
