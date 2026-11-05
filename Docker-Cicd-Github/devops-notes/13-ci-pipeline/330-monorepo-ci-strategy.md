# 330. Monorepo CI Strategy
# हिंदी में: Monorepo के लिए CI Strategy

---

## 🔵 Simple Definition (English)
A **monorepo** keeps several projects (api, web, shared libraries) in one Git repository. A **monorepo CI strategy** runs only the pipelines affected by a change, using `paths` filters, change detection (`dorny/paths-filter`), reusable workflows and per-package caches, so CI time stays flat as the repo grows.

## 🔵 सरल परिभाषा (Hindi)
**Monorepo** में कई projects (api, web, shared libraries) एक ही Git repository में रहते हैं। **Monorepo CI strategy** सिर्फ वही pipelines चलाती है जो change से प्रभावित हों, `paths` filters, change detection (`dorny/paths-filter`), reusable workflows और per-package caches से, ताकि repo बढ़ने पर भी CI का समय स्थिर रहे।

---

## 🔴 Problem it Solves
In a naive setup every commit triggers every pipeline: a typo fix in `README.md` rebuilds the React app, runs FastAPI tests and builds three Docker images. CI takes 25 minutes, costs money and developers stop trusting it. Worse, a required status check that is skipped by `paths` filtering can leave a PR stuck "waiting" forever.

## 🔴 यह क्यों बना? (Hindi)
Naive setup में हर commit हर pipeline चलाता है: `README.md` का typo fix React app rebuild करता है, FastAPI tests चलाता है और तीन Docker images बनाता है। CI 25 मिनट लेता है, पैसे खर्च होते हैं और developers का भरोसा खत्म होता है। और बुरा: `paths` filter से skip हुआ required status check PR को हमेशा "waiting" में अटका सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Layout: api/ (FastAPI), web/ (React), packages/shared/, .github/workflows/
Step 2 → A `changes` job detects which folders changed (dorny/paths-filter)
Step 3 → Downstream jobs run only if their output flag is true (`if: needs.changes.outputs.api == 'true'`)
Step 4 → Shared package changes mark both api and web as affected
Step 5 → Common logic lives in a reusable workflow (`workflow_call`) called per project
Step 6 → One final `ci-ok` job aggregates results; ONLY that job is the required check
Step 7 → Caches are keyed per project lock file; docker builds use per-image cache scope
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Layout: api/ (FastAPI), web/ (React), packages/shared/, .github/workflows/
Step 2 → `changes` job पता लगाता है कि कौन से folders बदले (dorny/paths-filter)
Step 3 → आगे के jobs तभी चलते हैं जब उनका output flag true हो (`if: needs.changes.outputs.api == 'true'`)
Step 4 → Shared package बदले तो api और web दोनों affected माने जाते हैं
Step 5 → साझा logic reusable workflow (`workflow_call`) में रहता है, हर project इसे call करता है
Step 6 → एक अंतिम `ci-ok` job सारे results जोड़ता है; सिर्फ वही required check बनता है
Step 7 → Caches हर project की lock file के key पर; docker builds में per-image cache scope
```

---

## 🟡 Real World Example
A startup keeps a Node.js API, a React dashboard and a FastAPI ML service in one repo deployed to one VPS. Before filtering, a docs change ran 22 minutes of CI. After adding a `changes` job, a frontend-only PR runs only the web pipeline (4 min), an API change runs api + integration (7 min), and the aggregate `ci-ok` job makes branch protection simple and robust even when some jobs are skipped.

## 🟡 Real Example Hindi mein
एक startup अपना Node.js API, React dashboard और FastAPI ML service एक ही repo में रखता है और एक VPS पर deploy करता है। Filtering से पहले docs की change पर भी 22 मिनट CI चलता था। `changes` job जोड़ने के बाद frontend-only PR सिर्फ web pipeline (4 min) चलाता है, API change api + integration (7 min), और aggregate `ci-ok` job branch protection को सरल और भरोसेमंद बनाता है चाहे कुछ jobs skip हों।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/web-only.yml  (simplest approach: native paths filter)
name: Web CI                        # workflow name
on:                                 # triggers
  pull_request:                     # PRs
    paths:                          # run only when these files change
      - 'web/**'                    # anything in web/
      - 'packages/shared/**'        # shared code used by web
      - '.github/workflows/web-only.yml'  # this workflow itself
jobs:                               # jobs
  test:                             # job id
    runs-on: ubuntu-latest          # runner
    defaults:                       # defaults
      run:                          # run steps
        working-directory: web      # operate inside web/
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout (example version)
      - uses: actions/setup-node@v4 # node
        with:                       # inputs
          node-version: 20          # version
          cache: npm                # cache
          cache-dependency-path: web/package-lock.json  # lock inside web/
      - run: npm ci                 # install
      - run: npm test -- --run      # tests (Vitest syntax)
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/ci.yml  (change detection + reusable workflows + aggregate gate)
name: Monorepo CI                   # workflow name
on:                                 # triggers
  pull_request:                     # PRs
  push:                             # pushes
    branches: [main]                # main
concurrency:                        # cancel stale
  group: ci-${{ github.ref }}       # per ref
  cancel-in-progress: true          # newer wins
permissions:                        # least privilege
  contents: read                    # read repo
  pull-requests: read               # paths-filter reads PR file list
jobs:                               # jobs
  changes:                          # detect affected projects
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 5              # cap
    outputs:                        # values for later jobs
      api: ${{ steps.f.outputs.api }}  # true/false
      web: ${{ steps.f.outputs.web }}  # true/false
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout (needed on push events)
      - uses: dorny/paths-filter@v3 # change-detection action (pin SHA in production)
        id: f                       # step id used above
        with:                       # inputs
          filters: |                # YAML filter map
            api:
              - 'api/**'
              - 'packages/shared/**'
            web:
              - 'web/**'
              - 'packages/shared/**'
  api:                              # api pipeline
    needs: changes                  # wait for detection
    if: needs.changes.outputs.api == 'true'  # run only if api affected
    uses: ./.github/workflows/_node-ci.yml   # call reusable workflow in same repo
    with:                           # inputs of reusable workflow
      working-directory: api        # project folder
      node-version: '20'            # node version
  web:                              # web pipeline
    needs: changes                  # wait
    if: needs.changes.outputs.web == 'true'  # run only if web affected
    uses: ./.github/workflows/_node-ci.yml   # same reusable workflow
    with:                           # inputs
      working-directory: web        # project folder
      node-version: '20'            # node version
  ci-ok:                            # single required status check
    if: always()                    # run even if others failed or were skipped
    needs: [changes, api, web]      # depends on all
    runs-on: ubuntu-latest          # runner
    steps:                          # steps
      - name: Fail if any needed job failed or was cancelled  # step
        run: |                      # shell
          echo "api=${{ needs.api.result }} web=${{ needs.web.result }}"   # log results
          if [ "${{ needs.api.result }}" = "failure" ] || [ "${{ needs.web.result }}" = "failure" ] || \
             [ "${{ needs.api.result }}" = "cancelled" ] || [ "${{ needs.web.result }}" = "cancelled" ] || \
             [ "${{ needs.changes.result }}" != "success" ]; then       # skipped is OK
            exit 1                                                      # block merge
          fi                                                            # end if
```

```yaml
# .github/workflows/_node-ci.yml  (reusable workflow called above)
name: Reusable Node CI              # name
on:                                 # reusable trigger
  workflow_call:                    # allows `uses:` from other workflows
    inputs:                         # parameters
      working-directory:            # folder of the project
        required: true              # must be passed
        type: string                # string type
      node-version:                 # node version
        required: false             # optional
        type: string                # string type
        default: '20'               # default value
permissions:                        # least privilege
  contents: read                    # read only
jobs:                               # jobs
  ci:                               # job id
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 15             # cap
    defaults:                       # defaults
      run:                          # run steps
        working-directory: ${{ inputs.working-directory }}  # project folder
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-node@v4 # node
        with:                       # inputs
          node-version: ${{ inputs.node-version }}  # from caller
          cache: npm                # cache
          cache-dependency-path: ${{ inputs.working-directory }}/package-lock.json  # per-project lock
      - run: npm ci                 # install
      - run: npm run lint           # lint
      - run: npm test               # test
      - run: npm run build          # build
```

---

## 🟠 My Stack Integration
Typical layout for your stack: `api/` (Node or FastAPI), `web/` (React), `deploy/` (docker-compose.yml, nginx.conf). Add a `deploy/**` path to a separate "config check" job (e.g. `docker compose config`, `nginx -t` in a container) so infrastructure changes are also validated.

```yaml
# Excerpt: filter for infra files and a compose validation job
  infra:                            # job id
    needs: changes                  # wait
    if: needs.changes.outputs.infra == 'true'  # add `infra: ['deploy/**']` to the filters above
    runs-on: ubuntu-latest          # runner
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - run: docker compose -f deploy/docker-compose.yml config -q  # validates compose file syntax, prints nothing on success
```

Security: path filters do not protect secrets; still restrict `permissions`, and never expose deploy secrets to `pull_request` runs from forks.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Making each path-filtered workflow a required check. A skipped workflow never reports, so the PR waits forever.
✅ Correct: Use change detection inside one workflow and require only the aggregate `ci-ok` job (which always runs).

❌ Mistake 2: Forgetting shared packages in the filters, so a change in `packages/shared` skips both api and web.
✅ Correct: Include shared paths in every dependent project's filter.

❌ Mistake 3: One giant cache key for the whole repo.
✅ Correct: Key caches by each project's lock file (`cache-dependency-path`).

❌ Mistake 4: Treating `skipped` as failure in the aggregate job (or `success` as the only OK).
✅ Correct: Accept `success` and `skipped`; fail on `failure` and `cancelled`.

---

## 🧠 Tricky Interview Question
**Q:** Branch protection requires the check "Web CI / test". A PR changes only `api/`, so `web-only.yml` (with a `paths` filter) never runs. Why can't the PR merge, and what is the fix?

Answer: Because of the path filter the workflow is not triggered, so the required check never reports and GitHub keeps it "Expected - Waiting for status". Fix options: (1) one workflow that always runs and contains a `changes` job plus an aggregate `ci-ok` job set as the only required check, or (2) a companion workflow with the inverse `paths-ignore` that reports a passing job with the same name.

---

## ⚫ Interview Questions + Answers

Q1: Monorepo vs polyrepo for CI?
A1: Monorepo gives atomic cross-project changes and shared tooling but needs selective CI. Polyrepo isolates pipelines but makes cross-repo changes and versioning harder.

Q2: How does `dorny/paths-filter` differ from the `paths:` trigger?
A2: `paths:` decides whether the whole workflow starts. `paths-filter` runs inside a workflow and outputs flags per area, so you can skip individual jobs while the workflow itself still reports.

Q3: How do you reuse CI logic across projects?
A3: Reusable workflows with `on: workflow_call` and `uses: ./.github/workflows/file.yml`, or composite actions for step bundles.

Q4: Tools that help beyond Actions?
A4: Nx, Turborepo, Bazel: they compute the affected graph and cache task results (remote cache), cutting CI time further.

Q5: How should deployment work in a monorepo?
A5: Build and deploy each service only when its flag is true, tag images with the commit SHA, and deploy through environments with protection rules.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several deployable apps or shared libraries live in one repo.
- CI time grows with repo size.

❌ Avoid when:
- A single small app: change detection adds complexity for no gain.
- Without discipline on ownership: a monorepo with no CODEOWNERS becomes chaos.

---

## 📊 Visual Diagram
```
                    PR / push
                        |
                  +-----v------+
                  |  changes   | (paths-filter)
                  +-----+------+
          api? ---------+--------- web?
            |                         |
     +------v------+           +------v------+
     | api CI      |           | web CI      |  (reusable workflow)
     | (skipped if |           | (skipped if |
     |  no change) |           |  no change) |
     +------+------+           +------+------+
            \                       /
             +----------+----------+
                        v
                  +-----------+
                  |  ci-ok    |  <- the ONLY required check
                  +-----------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Monorepo | Many projects, one repo | एक repo में कई projects |
| `paths` filter | Trigger by changed files | बदली files पर trigger |
| Reusable workflow | Callable workflow template | बार-बार बुलाया जाने वाला workflow |
| Aggregate job | Single summary check | सारांश वाला एक check |
| Affected graph | Projects impacted by a change | change से प्रभावित projects |

---

## ⚡ 3-Line Summary
English: Detect what changed and run only affected pipelines through reusable workflows.
English: Require a single always-running `ci-ok` job, not path-filtered workflows.
English: Include shared packages in filters and key caches per project.

Hindi: पता लगाओ क्या बदला और reusable workflows से सिर्फ प्रभावित pipelines चलाओ।
Hindi: Path-filtered workflows की जगह एक हमेशा चलने वाला `ci-ok` job required रखो।
Hindi: Filters में shared packages शामिल करो और caches हर project के हिसाब से key करो।

---

## ➡️ Next Topic
**331. CD Pipeline — Complete Guide** — CI proves the code is good; CD ships it to your VPS or AWS.
