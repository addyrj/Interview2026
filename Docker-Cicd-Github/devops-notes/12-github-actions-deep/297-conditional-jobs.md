# 297. Conditional Jobs
# हिंदी में: Conditional Jobs (शर्त के आधार पर Jobs चलाना)

---

## 🔵 Simple Definition (English)
A **conditional job** is a job that has an `if:` expression. GitHub evaluates it before the job starts. If the result is true, the job runs. If false, the job is **skipped** (shown grey, not failed).
You use it to run deploy only on `main`, skip jobs for forks, or run cleanup even when earlier jobs fail.

## 🔵 सरल परिभाषा (Hindi)
**Conditional job** वह job है जिस पर `if:` expression लगा होता है। Job शुरू होने से पहले GitHub इसे evaluate करता है। True आए तो job चलती है, false आए तो job **skip** हो जाती है (grey दिखती है, fail नहीं)।
इसका इस्तेमाल होता है: deploy सिर्फ `main` पर चलाना, forks पर secrets वाली jobs skip करना, या पिछली job fail होने पर भी cleanup चलाना।

---

## 🔴 Problem it Solves
Without conditions, every push would run every job: build, test, **and deploy to production**. A feature-branch push would deploy to your VPS. A fork PR would try to use secrets it cannot read. A failed test would leave a temporary preview environment alive forever because the cleanup job never ran.
Conditions let one workflow file handle many situations safely.

## 🔴 यह क्यों बना? (Hindi)
Conditions के बिना हर push पर हर job चलती: build, test, **और production deploy भी**। Feature branch push करने पर भी VPS पर deploy हो जाता। Fork की PR secrets इस्तेमाल करने की कोशिश करती जो उसे मिल ही नहीं सकते। Test fail होने पर preview environment हमेशा के लिए चलता रहता क्योंकि cleanup job कभी चली ही नहीं।
Conditions से एक ही workflow file कई situations को safely संभालती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Event happens (push, pull_request, workflow_dispatch, schedule)
Step 2 → Workflow starts; GitHub builds the job graph (needs: ordering)
Step 3 → Before a job starts, GitHub waits for all jobs in needs:
Step 4 → GitHub evaluates the job's if: expression with contexts
         (github, needs, vars, inputs). Secrets are NOT allowed in job-level if.
Step 5 → true  -> job runs
         false -> job is "skipped"
Step 6 → Default rule: if a needed job was skipped/failed, this job is
         skipped too, UNLESS the if: uses always() / failure() / !cancelled()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Event आता है (push, pull_request, workflow_dispatch, schedule)
Step 2 → Workflow शुरू होता है; GitHub job graph बनाता है (needs: से order)
Step 3 → Job शुरू होने से पहले needs: की सारी jobs का इंतज़ार होता है
Step 4 → GitHub job के if: को contexts (github, needs, vars, inputs) के साथ evaluate करता है
         Job-level if में secrets allowed नहीं हैं।
Step 5 → true  -> job चलती है
         false -> job "skipped" हो जाती है
Step 6 → Default rule: अगर needed job skip/fail हुई तो यह job भी skip होती है,
         जब तक if: में always() / failure() / !cancelled() न हो
```

---

## 🟡 Real World Example
Your repo has a FastAPI backend and a React frontend. Every PR runs `test`. Only a push to `main` runs `deploy` to the VPS. A `notify-failure` job posts to Slack only when `test` or `deploy` fails. A `cleanup` job removes the temporary Docker network with `if: always()`. This is the same pattern Swiggy-style teams use: PRs get fast feedback, only merged code goes live.

## 🟡 Real Example Hindi mein
आपके repo में FastAPI backend और React frontend है। हर PR पर `test` चलता है। सिर्फ `main` पर push होने पर VPS पर `deploy` चलता है। `notify-failure` job तभी Slack पर message भेजती है जब `test` या `deploy` fail हो। `cleanup` job `if: always()` से temporary Docker network हटाती है। Swiggy जैसी teams यही pattern अपनाती हैं: PR पर तेज़ feedback, और सिर्फ merge हुआ code live जाता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/conditional-basic.yml
name: Conditional Basic            # workflow name shown in the Actions tab

on:                                # events that trigger this workflow
  push:                            # run on every push
    branches: [main, develop]      # only for these two branches
  pull_request:                    # also run on pull requests

jobs:
  test:                            # job 1: always runs
    runs-on: ubuntu-latest         # GitHub-hosted Linux runner
    steps:
      - uses: actions/checkout@v4  # download repo code
      - run: echo "Running tests"  # placeholder for real tests

  deploy:                          # job 2: conditional
    needs: test                    # wait for test to succeed
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
                                   # run only for a push on main (not PRs)
    runs-on: ubuntu-latest         # runner for deploy
    steps:
      - run: echo "Deploying to production"   # placeholder for deploy

  staging:                         # job 3: conditional on another branch
    needs: test                    # wait for test
    if: github.ref == 'refs/heads/develop'   # only on develop branch
    runs-on: ubuntu-latest         # runner
    steps:
      - run: echo "Deploying to staging"      # placeholder
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/conditional-advanced.yml
name: CI-CD with status functions

on:
  push:
    branches: [main]               # production releases
  pull_request:                    # PR checks
  workflow_dispatch:               # manual run button
    inputs:
      deploy:                      # manual input: should we deploy?
        description: "Deploy after tests?"
        type: boolean
        default: false

permissions:
  contents: read                   # least privilege for GITHUB_TOKEN

jobs:
  changes:                         # detects which part of repo changed
    runs-on: ubuntu-latest
    outputs:                       # expose results to other jobs
      backend: ${{ steps.filter.outputs.backend }}    # 'true' or 'false'
      frontend: ${{ steps.filter.outputs.frontend }}  # 'true' or 'false'
    steps:
      - uses: actions/checkout@v4  # needed so the filter can read files
      - uses: dorny/paths-filter@v3   # third-party action (pin SHA in prod)
        id: filter                 # id used in outputs above
        with:
          filters: |               # path groups to test
            backend:
              - 'backend/**'
            frontend:
              - 'frontend/**'

  test-backend:
    needs: changes                 # depends on the detector
    if: needs.changes.outputs.backend == 'true'   # skip if backend untouched
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "pytest backend/"            # placeholder test command

  test-frontend:
    needs: changes
    if: needs.changes.outputs.frontend == 'true'  # skip if frontend untouched
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "npm test --prefix frontend"   # placeholder

  deploy:
    needs: [test-backend, test-frontend]   # both may be skipped, so see below
    # !cancelled() lets deploy run even if one test job was SKIPPED.
    # We still block it when any needed job FAILED.
    if: >-
      ${{ !cancelled()
      && !contains(needs.*.result, 'failure')
      && (github.ref == 'refs/heads/main' || inputs.deploy == true)
      && github.event.pull_request.head.repo.fork != true }}
    runs-on: ubuntu-latest
    environment: production        # can require manual approval
    steps:
      - run: echo "ssh deploy to VPS"          # placeholder

  notify-failure:
    needs: [test-backend, test-frontend, deploy]
    if: failure()                  # runs only when a needed job failed
    runs-on: ubuntu-latest
    steps:
      - run: echo "Send Slack alert"           # placeholder

  cleanup:
    needs: [deploy]
    if: always()                   # runs on success, failure, AND cancel
    runs-on: ubuntu-latest
    steps:
      - run: echo "Remove temp resources"      # placeholder
```

---

## 🟠 My Stack Integration
- **Node.js / React:** run `test-frontend` only when `frontend/**` changes; saves minutes in a monorepo.
- **FastAPI:** `test-backend` runs pytest only for `backend/**`.
- **Nginx / VPS:** `deploy` runs only on `main`, SSHes to the VPS, reloads Nginx.
- **AWS:** `if: github.ref == 'refs/heads/main'` gate before `aws-actions/configure-aws-credentials`.
- **Fork safety:** forks cannot read secrets, so skip deploy for them.

```yaml
# Snippet: production deploy gate for your VPS
  deploy-vps:
    needs: [test-backend, test-frontend]      # tests must pass
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production                   # approval + environment secrets
    steps:
      - name: Deploy over SSH                 # secrets are fine inside steps
        run: |                                # multi-line shell
          echo "$SSH_KEY" > key && chmod 600 key   # write key with safe perms
          ssh -i key -o StrictHostKeyChecking=accept-new \
            deploy@"$VPS_HOST" "cd /srv/app && docker compose pull && docker compose up -d"
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}  # secret from environment
          VPS_HOST: ${{ vars.VPS_HOST }}       # non-secret host variable
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `secrets.X` inside a job-level `if:` (not allowed; it errors or is always empty).
✅ Correct: Copy the secret into an `env` var or an earlier job output (`has_secret: ${{ env.X != '' }}`) and test that.

❌ Mistake 2: Writing `if: ${{ github.ref }} == 'refs/heads/main'`. A string with text outside `${{ }}` is always truthy.
✅ Correct: `if: github.ref == 'refs/heads/main'` (no braces) or put the whole expression inside `${{ }}`.

❌ Mistake 3: Expecting `deploy` to run when a `needs` job was skipped. It is skipped too by default.
✅ Correct: Add `!cancelled() && !contains(needs.*.result, 'failure')`.

❌ Mistake 4: Using `always()` on deploy. It runs even if tests failed and even when the run is cancelled.
✅ Correct: Use `always()` only for cleanup/notify. For deploy use `success()` or `!cancelled()` plus a failure check.

❌ Mistake 5: Starting an expression with `!` without quotes in YAML (`if: !cancelled()`). YAML treats `!` as a tag and the file breaks.
✅ Correct: Wrap in `${{ }}` or quotes: `if: ${{ !cancelled() }}`.

---

## 🧠 Tricky Interview Question
**Q:** `test-backend` is skipped because only frontend files changed. `deploy` has `needs: [test-backend, test-frontend]` and `if: github.ref == 'refs/heads/main'`. Will deploy run?

**Answer:** No. When any job in `needs` is skipped, the dependent job is skipped as well, because the implicit check is `success()`. Once you write your own `if:` without a status function, GitHub still prepends the implicit `success()`. Fix: add `!cancelled() && !contains(needs.*.result,'failure')`. Any status function in your `if` (`always`, `failure`, `cancelled`, `success`) replaces the implicit check.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a skipped job and a failed job?
A1: Skipped means the `if:` was false (or a dependency was skipped); no steps ran and the check shows grey. Failed means steps ran and returned non-zero. A skipped required check can still satisfy branch protection only when configured so; a skipped job does not block merging by itself in most setups, but a job depending on it is skipped.

Q2: What are the four status check functions?
A2: `success()` (default; all previous succeeded), `failure()` (any previous failed), `always()` (run regardless, even if cancelled), `cancelled()` (workflow was cancelled).

Q3: Job-level `if` vs step-level `if`?
A3: Job-level decides whether a whole runner is even started (saves cost). Step-level decides one step inside a running job. Step-level `if` can use `secrets` indirectly via `env`; job-level cannot use `secrets` or `env` context at all.

Q4: How do you run a job only if specific files changed?
A4: Use a small `changes` job with `dorny/paths-filter` (or `git diff`) that outputs booleans, then `if: needs.changes.outputs.backend == 'true'`. Workflow-level `paths:` filters apply to the whole workflow, not to individual jobs.

Q5: How do you prevent deploys from forked PRs?
A5: Check `github.event.pull_request.head.repo.fork != true` or `github.repository == 'owner/repo'`. Also forks do not receive secrets for `pull_request` events, and `pull_request_target` is dangerous with checkout of untrusted code.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Deploy must run only on `main` or on tags
- Monorepo: run backend/frontend jobs only when their paths changed
- Cleanup / notification must run even after failure
- Skip expensive jobs for draft PRs or forks

❌ Avoid when:
- The logic is really "different pipelines" (split into separate workflows or reusable workflows)
- Branch/path rules fit in `on.push.branches` or `on.paths` (simpler, and the workflow never starts)
- Condition needs a secret value (compute it earlier into an output or env)

---

## 📊 Visual Diagram
```
   push to feature/x                push to main
          |                               |
          v                               v
      +--------+                     +--------+
      |  test  | ---- passes ----->  |  test  |
      +--------+                     +--------+
          |                               |
   if: ref==main ?                 if: ref==main ?
          |                               |
        FALSE                           TRUE
          |                               |
   deploy = SKIPPED (grey)          deploy = RUNS
                                          |
                                  +---------------+
                                  | cleanup       |  if: always()
                                  +---------------+
                                  | notify-fail   |  if: failure()
                                  +---------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `jobs.<id>.if` | Expression deciding if job runs | job चलेगी या नहीं तय करने वाली शर्त |
| Skipped | Job not run because condition false | शर्त false होने से job नहीं चली |
| `success()` | True if all previous jobs passed | पिछली सब jobs पास हुईं |
| `failure()` | True if any previous job failed | कोई पिछली job fail हुई |
| `always()` | True regardless of status | हमेशा true, चाहे कुछ भी हो |
| `cancelled()` | True if run was cancelled | run cancel हुआ |
| `needs.*.result` | Result of each needed job | needed jobs के नतीजे |
| Context | Data object like `github`, `needs` | data object |

---

## ⚡ 3-Line Summary
English: A job-level `if:` decides whether a job runs or is skipped.
Status functions (`success`, `failure`, `always`, `cancelled`) control behavior around failed or skipped dependencies.
Use it for main-only deploys, path-based jobs, and always-run cleanup, and never put secrets in job-level `if`.
Hindi: Job-level `if:` तय करता है कि job चलेगी या skip होगी।
Status functions (`success`, `failure`, `always`, `cancelled`) fail या skipped dependencies के आसपास व्यवहार नियंत्रित करते हैं।
इसे main-only deploy, path-based jobs और हमेशा चलने वाले cleanup के लिए इस्तेमाल करें, और job-level `if` में secrets कभी न रखें।

---

## ➡️ Next Topic
**298. Reusable Workflows** — once you have many conditional jobs repeated across repos, you extract them into one callable workflow with `workflow_call`.
