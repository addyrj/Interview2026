# 245. pull_request Event
# हिंदी में: pull_request Event (PR पर workflow चलाना)

---

## 🔵 Simple Definition (English)
`pull_request` is a GitHub Actions trigger that starts a workflow when a pull request is opened, updated with new commits, or reopened. By default it runs on the **merge result** of the PR branch and the base branch, with a read-only token and no secrets for PRs coming from forks. It is the main trigger for CI checks (lint, test, build) before code is merged.

## 🔵 सरल परिभाषा (Hindi)
`pull_request` एक GitHub Actions trigger है जो तब workflow चलाता है जब pull request खुलता है, उसमें नए commits आते हैं या वह दोबारा खोला जाता है। Default रूप से यह PR branch और base branch के **merge result** पर चलता है, और fork से आए PR के लिए token read-only होता है तथा secrets नहीं मिलते। Merge से पहले CI checks (lint, test, build) चलाने का यही मुख्य trigger है।

---

## 🔴 Problem it Solves
Before PR-based CI, developers merged code and found failures only on `main` or in production. Reviewers had to pull the branch locally and run tests by hand. A broken `main` blocks the whole team and can reach the VPS through auto-deploy. With `pull_request`, every proposed change is tested automatically in a clean runner, the result appears as a status check on the PR, and branch protection can **refuse the merge** until checks are green.

## 🔴 यह क्यों बना? (Hindi)
PR-based CI से पहले developers code merge करते थे और failure `main` या production में पता चलता था। Reviewers को branch local में खींचकर tests हाथ से चलाने पड़ते थे। टूटा हुआ `main` पूरी team को रोक देता है और auto-deploy के ज़रिए VPS तक पहुँच सकता है। `pull_request` से हर प्रस्तावित बदलाव साफ़ runner में अपने-आप test होता है, नतीजा PR पर status check के रूप में दिखता है, और branch protection checks green होने तक **merge रोक** सकती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developer pushes branch `feature/login` and opens a PR into `main`.
Step 2 → GitHub emits a `pull_request` event with action `opened` (default activity types: opened, synchronize, reopened).
Step 3 → GitHub creates a TEMPORARY merge commit (refs/pull/<n>/merge) = PR head merged into base.
Step 4 → Workflow files are read from that merge commit; jobs run on fresh runners and check out the merge ref.
Step 5 → Each new push to the PR branch fires `synchronize` -> workflow runs again (use `concurrency` to cancel old runs).
Step 6 → Results appear as status checks; branch protection requires them green before "Merge" is enabled.
Step 7 → For PRs from forks: GITHUB_TOKEN is read-only and secrets are NOT passed (security by design).
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Developer branch `feature/login` push करता है और `main` में PR खोलता है।
Step 2 → GitHub `pull_request` event भेजता है, action `opened` (default types: opened, synchronize, reopened)।
Step 3 → GitHub एक अस्थायी merge commit (refs/pull/<n>/merge) बनाता है = PR head + base का merge।
Step 4 → Workflow file उसी merge commit से पढ़ी जाती है; jobs नए runner पर चलते हैं और merge ref checkout करते हैं।
Step 5 → PR branch पर हर नया push `synchronize` भेजता है -> workflow फिर चलता है (`concurrency` से पुराने runs cancel करें)।
Step 6 → नतीजे status checks में दिखते हैं; branch protection उन्हें green माँगती है तभी "Merge" चालू होता है।
Step 7 → Fork के PR के लिए: GITHUB_TOKEN read-only और secrets नहीं दिए जाते (सुरक्षा के लिए)।
```

Activity types you can filter: `opened`, `synchronize`, `reopened`, `closed`, `edited`, `labeled`, `unlabeled`, `ready_for_review`, `converted_to_draft`, `assigned`, `review_requested`, and more.

---

## 🟡 Real World Example
A fintech team in Bengaluru keeps a Node.js API and a React admin panel in one repo. Every PR runs ESLint, Jest, and a Docker build (no push). `main` is protected: 1 review + the `ci / test` check must pass. A developer pushes 5 times while fixing review comments; `concurrency` cancels the 4 stale runs so runners and minutes are saved. When the PR is merged, a separate `push: branches: [main]` workflow deploys to the VPS.

## 🟡 Real Example Hindi mein
Bengaluru की एक fintech team एक ही repo में Node.js API और React admin panel रखती है। हर PR पर ESLint, Jest और Docker build (बिना push) चलता है। `main` protected है: 1 review + `ci / test` check pass होना ज़रूरी। Review comments ठीक करते हुए developer 5 बार push करता है; `concurrency` 4 पुराने runs cancel कर देता है जिससे runner और minutes बचते हैं। PR merge होने पर अलग `push: branches: [main]` workflow VPS पर deploy करता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/pr-basic.yml
name: PR Basic Check                      # name shown in the Actions tab and PR checks list

on:                                       # trigger section
  pull_request:                           # run for pull request events
    branches: [main]                      # only PRs whose BASE branch is main

jobs:                                     # all jobs of this workflow
  test:                                   # job id
    runs-on: ubuntu-latest                # GitHub-hosted Linux runner
    steps:                                # ordered steps
      - uses: actions/checkout@v4         # clone the merge commit of the PR (example version, update as needed)
      - uses: actions/setup-node@v4       # install Node.js
        with:                             # inputs of the action
          node-version: 20                # Node major version used by the project
      - run: npm ci                       # clean, reproducible dependency install from package-lock.json
      - run: npm test                     # run unit tests; non-zero exit fails the check
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/pr-advanced.yml
name: PR Pipeline                         # display name

on:
  pull_request:                           # PR trigger
    branches: [main, develop]             # run when the PR targets main or develop
    types: [opened, synchronize, reopened, ready_for_review]  # explicit activity types
    paths:                                # run only if these files changed (saves minutes in monorepos)
      - "api/**"                          # Node.js / FastAPI service code
      - "web/**"                          # React app code
      - ".github/workflows/pr-advanced.yml"  # re-test when the pipeline itself changes

concurrency:                              # avoid duplicate runs for the same PR
  group: pr-${{ github.event.pull_request.number }}  # one group per PR number
  cancel-in-progress: true                # cancel the older run when a new commit arrives

permissions:                              # least privilege for GITHUB_TOKEN
  contents: read                          # read-only repo access
  pull-requests: write                    # needed only if a step comments on the PR

jobs:
  lint-test:                              # job id
    if: github.event.pull_request.draft == false   # skip draft PRs
    runs-on: ubuntu-latest                # runner label
    timeout-minutes: 15                   # kill hung jobs
    steps:
      - uses: actions/checkout@v4         # checkout merge commit
      - uses: actions/setup-node@v4       # Node setup
        with:
          node-version: 20                # version
          cache: npm                      # cache ~/.npm keyed on package-lock.json
          cache-dependency-path: api/package-lock.json   # lock file location in monorepo
      - run: npm ci                       # install exactly locked versions
        working-directory: api            # run inside api/ folder
      - run: npm run lint                 # ESLint
        working-directory: api
      - run: npm test -- --ci             # Jest in CI mode
        working-directory: api

  docker-build:                           # verify the image still builds
    needs: lint-test                      # run only after lint-test passes
    if: github.event.pull_request.draft == false
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4         # source
      - uses: docker/setup-buildx-action@v3   # enable Buildx
      - uses: docker/build-push-action@v6     # build image
        with:
          context: ./api                  # build context
          push: false                     # NEVER push from PR builds
          tags: myapp-api:pr-${{ github.event.pull_request.number }}  # local tag only
          cache-from: type=gha            # reuse GitHub cache layers
          cache-to: type=gha,mode=max     # store layers for the next run
```

(Syntax checked as YAML locally; workflow not executed on GitHub. Action versions are examples.)

---

## 🟠 My Stack Integration
- **Node.js / FastAPI:** PR runs lint + tests; for FastAPI swap steps with `setup-python` + `pytest`.
- **React:** `npm run build` on PR proves the production bundle compiles; upload `dist` as artifact for preview if needed.
- **Nginx / VPS:** do NOT deploy from `pull_request`. Deploy only from `push` to `main` (or a tag), because PR code is untrusted until reviewed.
- **AWS:** if PR jobs need AWS (e.g. `terraform plan`), use OIDC with a read-only role scoped to `pull_request` subject, never static keys.

```yaml
# Branch protection companion (set in GitHub UI: Settings -> Branches -> main)
# Require status checks:  "PR Pipeline / lint-test"  and  "PR Pipeline / docker-build"
# Require 1 approving review, dismiss stale approvals on new commits.
# Result: merge is impossible until the pull_request workflow is green.
on:
  pull_request:                           # same trigger name must stay stable, or required checks go "pending forever"
    branches: [main]
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `pull_request` and expecting secrets from fork PRs (`secrets.X` is empty, the step fails mysteriously).
✅ Correct: Design fork-safe checks that need no secrets; deploy/preview steps run only after merge.

❌ Mistake 2: Not using `concurrency`, so 10 pushes produce 10 parallel full runs.
✅ Correct: Add `concurrency` with `cancel-in-progress: true` for PR workflows.

❌ Mistake 3: Using `paths:` filter while the check is marked "required" - skipped workflows never report, PR is stuck.
✅ Correct: Make required checks always run, or add a lightweight always-on job that aggregates results.

❌ Mistake 4: Pushing Docker images from PR builds.
✅ Correct: `push: false` for PRs; push only on `main`/tags.

---

## 🧠 Tricky Interview Question
A contributor opens a PR from a fork that modifies `.github/workflows/ci.yml` to print `${{ secrets.AWS_SECRET_ACCESS_KEY }}`. Will the secret leak?

Answer: No, with `pull_request` it will not. For fork PRs GitHub does not pass repository secrets and gives a read-only `GITHUB_TOKEN`. The danger is `pull_request_target`: it runs in the context of the BASE repo with secrets available, so if it checks out and runs the PR's code, an attacker can steal secrets. Rule: never check out untrusted PR head code inside `pull_request_target` together with secrets.

---

## ⚫ Interview Questions + Answers

Q1: What are the default activity types of `pull_request`?
A1: `opened`, `synchronize`, `reopened`. Others like `labeled` or `ready_for_review` must be listed under `types:`.

Q2: Which commit does the workflow run on?
A2: On the temporary merge commit `refs/pull/<n>/merge` (PR head merged into base). `github.sha` is that merge commit; the PR head SHA is `github.event.pull_request.head.sha`.

Q3: `pull_request` vs `push` - when both fire?
A3: Pushing to a branch with an open PR fires both if both are configured, causing duplicates. Fix: `push` only for `main`, `pull_request` for PR branches.

Q4: How do you stop a PR from merging if tests fail?
A4: Branch protection / rulesets with "Require status checks to pass", selecting the job names produced by the workflow.

Q5: How do you run only on changes in a folder?
A5: `on.pull_request.paths` (or `paths-ignore`). Beware required-check deadlocks when a workflow is skipped.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running lint, unit tests, type checks, security scans before merge.
- Building Docker images without pushing to validate the Dockerfile.
- Running `terraform plan` or preview builds for review.

❌ Avoid when:
- You need to deploy or use production secrets (use `push` to protected branch or `workflow_dispatch` with environments).
- You want to comment on fork PRs with write permission (needs a careful two-workflow pattern, not plain `pull_request`).

---

## 📊 Visual Diagram

```
 feature branch                      GitHub                         Runner
 --------------                      ------                         ------
  git push  ───────────►  Open PR (feature -> main)
                                  │  event: pull_request (opened)
                                  ▼
                       build refs/pull/12/merge  (head + base)
                                  │
                                  ▼
                        queue workflow jobs  ───────►  lint -> test -> docker build
                                  │                           │
        new commit pushed ──► synchronize ──► cancel old run  │
                                  ▼                           ▼
                        status checks on PR  ◄──────  pass / fail
                                  │
                   branch protection: all green + review ?
                                  │ yes
                                  ▼
                              MERGE to main  ──►  (separate push workflow deploys)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pull request | Proposal to merge one branch into another | Branch merge करने का प्रस्ताव |
| activity type | Sub-action of an event (opened, synchronize) | Event की उप-क्रिया |
| merge commit ref | `refs/pull/N/merge`, temporary merge for testing | परीक्षण हेतु अस्थायी merge |
| status check | Pass/fail result shown on a PR | PR पर pass/fail नतीजा |
| branch protection | Rules that block merges until conditions pass | शर्तें पूरी होने तक merge रोकना |
| concurrency | Limit/cancel parallel runs of a group | समान runs को सीमित/रद्द करना |
| fork PR | PR from someone's copy of the repo | Repo की copy से आया PR |

---

## ⚡ 3-Line Summary
English: `pull_request` runs CI on the merge result of a PR before merging.
English: Default types are opened/synchronize/reopened; fork PRs get no secrets and a read-only token.
English: Pair it with branch protection and `concurrency`; never deploy from it.
Hindi: `pull_request` merge से पहले PR के merge result पर CI चलाता है।
Hindi: Default types opened/synchronize/reopened हैं; fork PR को secrets नहीं और token read-only मिलता है।
Hindi: इसे branch protection और `concurrency` के साथ इस्तेमाल करें; इससे कभी deploy न करें।

---

## ➡️ Next Topic
**246. schedule Event (cron)** - after PR-time checks, learn how to run workflows on a timer (nightly builds, dependency audits, cleanup jobs).
