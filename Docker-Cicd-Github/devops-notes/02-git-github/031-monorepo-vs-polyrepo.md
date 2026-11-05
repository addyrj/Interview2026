---

# 31. Monorepo vs Polyrepo
# हिंदी में: Monorepo बनाम Polyrepo

---

## 🔵 Simple Definition (English)
A **monorepo** keeps many projects (frontend, backend, shared libraries) in ONE Git repository. A **polyrepo** gives each project its own repository. It is a trade-off between easy code sharing (monorepo) and independence and isolation (polyrepo).

## 🔵 सरल परिभाषा (Hindi)
**Monorepo** में कई projects (frontend, backend, shared libraries) एक ही Git repository में रहते हैं। **Polyrepo** में हर project की अपनी अलग repository होती है। यह code sharing की आसानी (monorepo) और स्वतंत्रता व अलगाव (polyrepo) के बीच का trade-off है।

---

## 🔴 Problem it Solves
With many repos, a change to a shared type (e.g., the `User` API contract) needs 3 PRs in 3 repos, version bumps, and coordination; versions drift. With a single giant repo, CI runs everything on every commit, permissions are all-or-nothing, and clone gets slow. Both models exist to manage this coordination vs isolation problem.

## 🔴 यह क्यों बना? (Hindi)
कई repos होने पर shared type (जैसे `User` API contract) बदलने के लिए 3 repos में 3 PRs, version bumps और coordination चाहिए; versions अलग-अलग हो जाते हैं। एक बड़ी repo में हर commit पर पूरा CI चलता है, permissions या तो सब या कुछ नहीं, और clone धीमा होता है। दोनों models इसी coordination बनाम isolation की समस्या के लिए हैं।

---

## 🟢 How it Works — Step by Step

```
MONOREPO
Step 1 → One repo: apps/api, apps/web, packages/shared, infra/
Step 2 → One PR can change API + frontend + shared types atomically
Step 3 → CI uses path filters so only affected apps are built/tested
Step 4 → Deploy each app independently from its own workflow

POLYREPO
Step 1 → repos: shop-api, shop-web, shop-shared, shop-infra
Step 2 → Shared code is published as a package (npm / PyPI / GHCR image)
Step 3 → Consumers bump the version; each repo has its own CI/CD, owners, permissions
```

## 🟢 कैसे काम करता है? (Hindi)
```
MONOREPO
Step 1 → एक repo: apps/api, apps/web, packages/shared, infra/
Step 2 → एक PR में API + frontend + shared types एक साथ बदलते हैं
Step 3 → CI में path filters से सिर्फ प्रभावित app build/test होता है
Step 4 → हर app अपने workflow से अलग deploy होता है

POLYREPO
Step 1 → repos: shop-api, shop-web, shop-shared, shop-infra
Step 2 → Shared code package (npm / PyPI / GHCR image) बनकर publish होता है
Step 3 → इस्तेमाल करने वाले version bump करते हैं; हर repo का अपना CI/CD, owners, permissions
```

---

## 🟡 Real World Example
Google and Meta use huge monorepos with custom tooling. A 4-person startup with a React web app, a FastAPI backend and a Node.js notification worker, all deployed to one AWS VPS behind Nginx, is best in a monorepo: one PR adds an API field and shows it in React, with path-filtered GitHub Actions so a README change deploys nothing. A larger company with separate teams, separate release cycles and strict access (payments team vs marketing site) uses polyrepo and shares code via a private npm registry (GitHub Packages).

## 🟡 Real Example Hindi mein
Google और Meta बहुत बड़े monorepos custom tooling के साथ चलाते हैं। 4 लोगों का startup जिसमें React web app, FastAPI backend और Node.js notification worker एक AWS VPS पर Nginx के पीछे चलते हैं, monorepo में सबसे अच्छा रहता है: एक PR में API field जुड़ता है और React में दिखता है, path-filtered Actions से README बदलने पर कुछ deploy नहीं होता। बड़ी कंपनी जहाँ teams अलग, release cycles अलग और access सख़्त है (payments team बनाम marketing site) वहाँ polyrepo चलता है और code private npm registry (GitHub Packages) से share होता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/api.yml - monorepo: run ONLY when backend files change
name: API CI                                # workflow name
on:
  push:
    branches: [main]                        # run on pushes to main
    paths:                                  # path filter: only these changes trigger it
      - "apps/api/**"                       # anything inside the api app
      - "packages/shared/**"                # or the shared package it depends on
      - ".github/workflows/api.yml"         # or this workflow file itself
  pull_request:
    paths:                                  # same filter for PRs
      - "apps/api/**"                       # api changes
      - "packages/shared/**"                # shared changes
jobs:
  test:                                     # job id
    runs-on: ubuntu-latest                  # hosted runner
    defaults:
      run:
        working-directory: apps/api         # every `run` step starts in the api folder
    steps:
      - uses: actions/checkout@v4           # get the code (example version)
      - uses: actions/setup-node@v4         # Node.js toolchain
        with:
          node-version: 20                  # example LTS
          cache: npm                        # cache npm downloads
          cache-dependency-path: apps/api/package-lock.json   # lockfile in subfolder
      - run: npm ci                         # clean install
      - run: npm test                       # run tests
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/monorepo-ci.yml - detect changed apps, then run a matrix only for them
name: Monorepo CI                           # workflow name
on:
  pull_request:                             # run on PRs
    branches: [main]                        # target main
concurrency:                                # cancel older runs of same PR
  group: ci-${{ github.ref }}               # one group per branch/PR ref
  cancel-in-progress: true                  # stop outdated runs to save minutes
permissions:
  contents: read                            # least privilege for GITHUB_TOKEN
jobs:
  changes:                                  # job 1: figure out what changed
    runs-on: ubuntu-latest                  # hosted runner
    outputs:                                # values passed to later jobs
      api: ${{ steps.filter.outputs.api }}  # "true" if api files changed
      web: ${{ steps.filter.outputs.web }}  # "true" if web files changed
    steps:
      - uses: actions/checkout@v4           # need the files for the filter
      - uses: dorny/paths-filter@v3         # third-party action, example version, pin to SHA in production
        id: filter                          # id so we can read outputs
        with:
          filters: |                        # map name -> path globs
            api:
              - 'apps/api/**'
              - 'packages/shared/**'
            web:
              - 'apps/web/**'
              - 'packages/shared/**'
  api:                                      # job 2: backend tests
    needs: changes                          # wait for the filter job
    if: needs.changes.outputs.api == 'true' # skip when api did not change
    runs-on: ubuntu-latest                  # hosted runner
    steps:
      - uses: actions/checkout@v4           # code
      - uses: actions/setup-python@v5       # FastAPI example
        with:
          python-version: "3.12"            # example version
          cache: pip                        # cache pip downloads
          cache-dependency-path: apps/api/requirements.txt   # cache key file
      - run: pip install -r apps/api/requirements.txt         # install dependencies
      - run: python -m pytest apps/api      # run tests
  web:                                      # job 3: frontend build
    needs: changes                          # wait for the filter job
    if: needs.changes.outputs.web == 'true' # skip when web did not change
    runs-on: ubuntu-latest                  # hosted runner
    steps:
      - uses: actions/checkout@v4           # code
      - uses: actions/setup-node@v4         # Node.js
        with:
          node-version: 20                  # example LTS
          cache: npm                        # npm cache
          cache-dependency-path: apps/web/package-lock.json   # lockfile path
      - run: npm ci --prefix apps/web       # install in subfolder
      - run: npm run build --prefix apps/web   # production build
  gate:                                     # job 4: single required status check for branch protection
    if: always()                            # run even if some jobs were skipped
    needs: [api, web]                       # after both
    runs-on: ubuntu-latest                  # hosted runner
    steps:
      - name: Fail if any needed job failed or was cancelled   # label
        run: |                              # shell
          if [ "${{ contains(needs.*.result, 'failure') }}" = "true" ] || [ "${{ contains(needs.*.result, 'cancelled') }}" = "true" ]; then
            exit 1                          # fail the gate
          fi
```
Not run on GitHub here; the workflow syntax is validated only by a YAML parser. Skipped required jobs show as "skipped" (counts as passing), which is why one `gate` job is the standard pattern.

---

## 🟠 My Stack Integration
Recommended layout for your Node.js + FastAPI + React + Nginx stack:

```yaml
# conceptual layout and CODEOWNERS style mapping (as comments in a yaml file)
# repo/
#   apps/
#     web/        # React (Vite) -> built, served by Nginx from /var/www/web
#     api/        # FastAPI      -> Docker image, runs behind Nginx proxy_pass
#     worker/     # Node.js      -> Docker image
#   packages/
#     shared/     # shared TypeScript types / OpenAPI client
#   infra/
#     nginx/      # nginx.conf, deploy scripts for VPS / Terraform for AWS
#   .github/workflows/  # one workflow per app + gate
services:                                   # docker-compose.yml at repo root (valid compose)
  api:                                      # FastAPI service
    build: ./apps/api                       # build context is only the api folder (smaller, cacheable)
    env_file: .env                          # secrets from file not committed
  worker:                                   # Node.js worker
    build: ./apps/worker                    # build context for worker
    env_file: .env                          # same env file
```
Security: in a monorepo everyone who can read the repo reads all code and infra files. Keep secrets only in GitHub Secrets/AWS, use CODEOWNERS (topic 34) to require infra-team review for `infra/**`, and keep the Docker build context narrow.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Monorepo where every push builds and deploys everything.
✅ Correct: Use `paths:` filters or a changed-files action, and cache dependencies.

❌ Mistake 2: Polyrepo with copy-pasted shared code in each repo.
✅ Correct: Publish a versioned package (GitHub Packages / PyPI) or generate clients from an OpenAPI spec.

❌ Mistake 3: Path-filtered workflow marked as a required check; PRs that do not touch the path wait forever for the check.
✅ Correct: Use a single always-running gate job (as above) as the required check.

❌ Mistake 4: Putting the whole monorepo as Docker build context (`docker build .`), so every file change busts the cache.
✅ Correct: Build with a narrow context (`./apps/api`) and a good `.dockerignore`.

---

## 🧠 Tricky Interview Question
Your monorepo has `paths: ['apps/api/**']` on the workflow, and the "API CI" check is required in branch protection. A PR that only edits the README can never be merged. Why, and how do you fix it?

Answer: When a workflow is skipped by path filtering, it never reports a status, so the required check stays "Expected - waiting for status" forever. Fix: do not use workflow-level `paths:` for required checks. Run the workflow always, detect changes inside (paths-filter action) and skip individual jobs (skipped jobs count as success), then make one aggregate `gate` job the required check.

---

## ⚫ Interview Questions + Answers

Q1: Main advantages of a monorepo?
A1: Atomic cross-project changes, easy code sharing and refactoring, one place for tooling/CI standards, simple dependency version consistency.

Q2: Main disadvantages?
A2: Slow clones and CI without optimization, coarse access control, noisy history, need for tooling (path filters, Nx/Turborepo/Bazel).

Q3: Advantages of polyrepo?
A3: Clear ownership and permissions, independent release cycles, small fast repos, simpler CI per repo.

Q4: How do you do independent deployments in a monorepo?
A4: Separate workflows (or jobs) per app with path filters, own Docker image tags, and per-app deploy steps.

Q5: What tools help monorepos?
A5: npm/pnpm workspaces, Turborepo, Nx (JS); Bazel/Pants (polyglot); `git sparse-checkout` and shallow clones for size.

---

## 🔷 When to Use + When Not to Use
✅ Monorepo when:
- Small/medium team, tightly coupled apps sharing types
- You want atomic changes and one consistent CI setup

✅ Polyrepo when:
- Separate teams, security boundaries, different release rhythms, open-source libraries

❌ Avoid monorepo when:
- You lack CI optimization capacity or need strict per-project access control

---

## 📊 Visual Diagram
```
 MONOREPO                          POLYREPO
 shop/                             shop-web    (repo)
  |-- apps/web   --\               shop-api    (repo)
  |-- apps/api   ---+-- 1 PR       shop-shared (repo, npm package)
  |-- packages/shared              shop-infra  (repo)
  |-- infra/                       web --depends--> shared@1.4.0
  CI: paths filter -> only         api --depends--> shared@1.3.2  (drift!)
  affected app builds              3 PRs for 1 contract change
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Monorepo | Many projects, one repo | एक repo में कई projects |
| Polyrepo | One project per repo | हर project की अलग repo |
| Path filter | Trigger CI only for changed paths | बदले paths पर ही CI |
| Workspace | npm/pnpm feature linking local packages | local packages जोड़ना |
| Atomic change | One commit spanning many apps | एक साथ सब बदलाव |
| Gate job | Aggregated required check | एकल अनिवार्य check |

---

## ⚡ 3-Line Summary
English: Monorepo = one repo for all projects; polyrepo = one repo per project.
Monorepo eases sharing and atomic changes but needs path-filtered CI; polyrepo isolates but risks version drift.
Small team on one VPS: monorepo with a gate job is usually best.
Hindi: Monorepo = सब projects एक repo में; polyrepo = हर project की अलग repo।
Monorepo में sharing और atomic changes आसान हैं पर path-filtered CI चाहिए; polyrepo अलग रखता है पर version drift का जोखिम है।
एक VPS पर छोटी team के लिए gate job वाला monorepo आमतौर पर सबसे अच्छा है।

---

## ➡️ Next Topic
**32. GitHub Repository Settings**: configure merge methods, security features and access for whichever repo layout you choose.

---
