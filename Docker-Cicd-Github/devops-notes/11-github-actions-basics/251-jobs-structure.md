# 251. jobs: Structure
# हिंदी में: jobs: की संरचना

---

## 🔵 Simple Definition (English)
`jobs:` is the top-level map in a workflow file that holds one or more **jobs**. Each job has an id, runs on its own fresh runner (`runs-on`), contains ordered `steps`, and can depend on other jobs with `needs`. Jobs run **in parallel by default**; each can define `outputs`, `if`, `env`, `permissions`, `strategy`, `timeout-minutes`, `services`, `container`, and `environment`.

## 🔵 सरल परिभाषा (Hindi)
`jobs:` workflow file का top-level map है जिसमें एक या अधिक **jobs** होते हैं। हर job का एक id होता है, वह अपने नए runner (`runs-on`) पर चलता है, क्रम से `steps` रखता है, और `needs` से दूसरे jobs पर निर्भर हो सकता है। Jobs **default रूप से parallel** चलते हैं; हर job `outputs`, `if`, `env`, `permissions`, `strategy`, `timeout-minutes`, `services`, `container` और `environment` तय कर सकता है।

---

## 🔴 Problem it Solves
A single long shell script that lints, tests, builds and deploys is slow (serial), hard to debug, and wastes minutes when only lint failed. Splitting into jobs gives parallelism (lint and test together), isolation (each on a clean VM), selective re-runs ("re-run failed jobs"), different runners per task (Linux build, Windows test), and clear gates (deploy `needs` test). It also allows different permissions and secrets per job.

## 🔴 यह क्यों बना? (Hindi)
एक लंबी shell script जो lint, test, build और deploy करती है, धीमी (serial) होती है, debug करना कठिन होता है और सिर्फ़ lint फेल होने पर भी पूरा समय बर्बाद करती है। Jobs में बाँटने से parallelism (lint और test साथ), isolation (हर job साफ़ VM पर), चुनिंदा re-run ("re-run failed jobs"), काम के हिसाब से अलग runner (Linux build, Windows test) और साफ़ gates (deploy `needs` test) मिलते हैं। हर job के लिए अलग permissions और secrets भी रखे जा सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Workflow starts; GitHub reads `jobs:` and builds a dependency graph from `needs`.
Step 2 → Jobs without `needs` are queued immediately, in parallel, each waiting for a free runner.
Step 3 → Each job gets a FRESH runner: no files, env or caches carry over from other jobs.
Step 4 → To share data: `outputs` (small strings) or artifacts/cache (files).
Step 5 → A job runs its steps in order; first failing step stops the job (unless `continue-on-error`/`if: always()`).
Step 6 → Dependent jobs start only if all `needs` jobs succeeded (override with `if: always()` / `!cancelled()`).
Step 7 → Workflow result = all jobs; skipped jobs count as success for required checks only if skipped by `if`, check docs.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Workflow शुरू होता है; GitHub `jobs:` पढ़कर `needs` से dependency graph बनाता है।
Step 2 → बिना `needs` वाले jobs तुरंत, parallel, free runner के इंतज़ार में queue होते हैं।
Step 3 → हर job को नया runner मिलता है: दूसरे jobs की files, env या caches साथ नहीं आते।
Step 4 → Data साझा करने के लिए: `outputs` (छोटी strings) या artifacts/cache (files)।
Step 5 → Job अपने steps क्रम से चलाता है; पहला fail होने वाला step job रोक देता है (जब तक `continue-on-error`/`if: always()` न हो)।
Step 6 → Dependent jobs तभी चलते हैं जब सभी `needs` jobs सफल हों (`if: always()` / `!cancelled()` से बदल सकते हैं)।
Step 7 → Workflow का नतीजा = सभी jobs; skipped jobs की स्थिति के लिए docs देखें।
```

Useful job-level keys: `name`, `needs`, `if`, `runs-on`, `environment`, `concurrency`, `outputs`, `env`, `defaults.run`, `permissions`, `timeout-minutes`, `strategy`, `continue-on-error`, `container`, `services`, `steps`, `uses` (reusable workflow call).

---

## 🟡 Real World Example
A food-delivery backend pipeline: `lint` and `unit-test` run in parallel (2 minutes), `integration-test` needs Postgres and Redis as `services` containers, `build-image` needs all three and outputs the image digest, `deploy-staging` needs `build-image`, and `deploy-production` needs `deploy-staging` plus manual approval via `environment: production`. When only integration test flakes, the team re-runs just that job.

## 🟡 Real Example Hindi mein
Food-delivery backend का pipeline: `lint` और `unit-test` parallel चलते हैं (2 मिनट), `integration-test` को Postgres और Redis `services` containers चाहिए, `build-image` तीनों पर निर्भर है और image digest output करता है, `deploy-staging` `build-image` पर, और `deploy-production` `deploy-staging` तथा `environment: production` की manual approval पर। सिर्फ़ integration test flaky हो तो team केवल वही job दोबारा चलाती है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/jobs-basic.yml
name: Jobs Basic                          # workflow name

on: [push]                                # run on every push

jobs:                                     # map of jobs
  lint:                                   # job id (unique, letters/digits/-/_ only)
    runs-on: ubuntu-latest                # fresh Ubuntu VM
    steps:
      - uses: actions/checkout@v4         # clone repo
      - run: echo "linting..."            # placeholder lint step

  test:                                   # runs IN PARALLEL with lint (no needs)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "testing..."            # placeholder test step

  build:                                  # sequential job
    needs: [lint, test]                   # waits for BOTH to succeed
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "building..."           # placeholder build step
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/jobs-advanced.yml
name: Backend Pipeline

on:
  push:
    branches: [main]

permissions:
  contents: read                          # workflow default for all jobs

jobs:
  integration-test:
    runs-on: ubuntu-latest
    timeout-minutes: 15                   # fail fast on hangs
    services:                             # sidecar containers for this job
      postgres:
        image: postgres:16-alpine         # example version
        env:
          POSTGRES_PASSWORD: test         # test-only credential, not a real secret
        ports: ["5432:5432"]              # expose to the runner host
        options: >-                       # docker create options: wait for healthy DB
          --health-cmd="pg_isready -U postgres"
          --health-interval=5s
          --health-timeout=3s
          --health-retries=10
    defaults:
      run:
        working-directory: api            # default folder for all run steps
    env:
      DATABASE_URL: postgres://postgres:test@localhost:5432/postgres   # job-wide env
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm, cache-dependency-path: api/package-lock.json }
      - run: npm ci
      - run: npm run test:integration

  build-image:
    needs: integration-test               # gate: only after tests pass
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write                     # job-level: only this job may push images
    outputs:
      tag: ${{ steps.vars.outputs.tag }}  # exposes a value to downstream jobs
    steps:
      - uses: actions/checkout@v4
      - id: vars
        run: echo "tag=sha-${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"   # short SHA as tag
      - run: echo "would build ghcr.io/acme/api:${{ steps.vars.outputs.tag }}"   # real build omitted

  deploy-production:
    needs: build-image                    # needs also gives access to its outputs
    if: github.ref == 'refs/heads/main'   # job-level condition
    runs-on: ubuntu-latest
    environment:                          # approval + environment secrets
      name: production
      url: https://app.example.com        # link shown on the run page
    concurrency: deploy-production        # serialize production deploys
    steps:
      - run: echo "deploy ${{ needs.build-image.outputs.tag }}"

  notify:
    needs: [integration-test, build-image, deploy-production]
    if: always()                          # run even if earlier jobs failed
    runs-on: ubuntu-latest
    steps:
      - run: echo "Result deploy=${{ needs.deploy-production.result }}"   # success|failure|cancelled|skipped
```

(YAML parsed locally; `services` health options not run with Docker here.)

---

## 🟠 My Stack Integration
- **Node.js:** `lint`, `test`, `build` jobs; Postgres/Redis in `services`.
- **FastAPI:** job with `services: postgres` and `pytest`; separate job to build the image.
- **React:** `build` job uploads `dist` as artifact; `deploy` job downloads it and rsyncs to the Nginx VPS.
- **AWS:** `permissions: id-token: write` only on the single job that assumes the AWS role, keeping other jobs unprivileged.

```yaml
# Pattern: share built files between jobs (jobs do NOT share a filesystem)
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build      # produce dist/
      - uses: actions/upload-artifact@v4  # save files for later jobs
        with: { name: web-dist, path: dist, retention-days: 3 }
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4  # get dist/ back
        with: { name: web-dist, path: dist }
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming job B sees files created by job A.
✅ Correct: Use artifacts, cache or outputs; each job has a clean VM.

❌ Mistake 2: Forgetting `needs`, so `deploy` runs in parallel with `test`.
✅ Correct: Add `needs: [test]` (and `build`) to every gate.

❌ Mistake 3: Putting secrets in job `outputs` (they get masked/dropped and are logged-risky).
✅ Correct: Output non-sensitive identifiers; fetch secrets in the job that needs them.

❌ Mistake 4: Notification job skipped because a needed job failed.
✅ Correct: `if: always()` (or `failure()`).

❌ Mistake 5: No `timeout-minutes` (default 360 minutes).
✅ Correct: Set a realistic limit per job.

---

## 🧠 Tricky Interview Question
`deploy` has `needs: [test, lint]`. `lint` is skipped by an `if:` condition. Does `deploy` run?

Answer: By default, a job whose needed job was skipped is also skipped (skipped is neither success nor failure for dependency purposes, and the implicit `success()` check fails). To run deploy anyway use `if: ${{ !failure() && !cancelled() }}`, which treats skipped needs as acceptable while still stopping on real failure.

---

## ⚫ Interview Questions + Answers

Q1: Do jobs run in parallel or sequence?
A1: Parallel by default; sequence through `needs`. Available runners and concurrency limits still apply.

Q2: How do jobs share data?
A2: Small values via `outputs`; files via `upload-artifact`/`download-artifact` or caches.

Q3: Max number of jobs / duration?
A3: Job time limit is 6 hours on hosted runners (default timeout 360 min); a workflow run is limited to 35 days queued+run; matrix up to 256 jobs per workflow run (check current limits).

Q4: Valid job id characters?
A4: Must start with a letter or `_` and contain only letters, numbers, `-`, `_`.

Q5: How to run a job only if previous failed?
A5: `needs: other` + `if: failure()` (or `needs.other.result == 'failure'`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want parallel checks, gates, different runners or permissions.
- You want to re-run just a failing stage.

❌ Avoid when:
- Steps share a lot of local state (big builds): splitting into jobs forces artifact upload/download cost; keep them in one job.

---

## 📊 Visual Diagram

```
          ┌────────┐   ┌────────┐
 push ───►│  lint  │   │  test  │      (parallel, fresh VMs)
          └───┬────┘   └───┬────┘
              └─────┬──────┘
                    ▼ needs: [lint, test]
              ┌───────────┐  outputs.tag
              │   build   │───────────────┐
              └─────┬─────┘               │
                    ▼ needs: build        ▼
           ┌──────────────────┐   ┌──────────────┐
           │ deploy (approval)│──►│ notify(always)│
           └──────────────────┘   └──────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| job | Group of steps on one runner | एक runner पर steps का समूह |
| needs | Dependency on other jobs | दूसरे jobs पर निर्भरता |
| outputs | Values passed to later jobs | आगे के jobs को दिए values |
| services | Sidecar containers (DB, Redis) | साथ चलने वाले containers |
| artifact | File shared between jobs | Jobs के बीच साझा file |
| timeout-minutes | Max job duration | Job की अधिकतम अवधि |

---

## ⚡ 3-Line Summary
English: `jobs:` defines parallel units, each on a fresh runner with ordered steps.
English: Use `needs` for order, `outputs`/artifacts for data, `if` for conditions.
English: Set permissions and timeouts per job.
Hindi: `jobs:` parallel इकाइयाँ तय करता है, हर एक नए runner पर क्रमवार steps के साथ।
Hindi: क्रम के लिए `needs`, data के लिए `outputs`/artifacts, शर्त के लिए `if`।
Hindi: हर job के permissions और timeouts तय करें।

---

## ➡️ Next Topic
**252. runs-on** - choose where each job runs: GitHub-hosted labels, larger runners, self-hosted runners.
