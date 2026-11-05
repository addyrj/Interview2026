---

# 366. Monorepo Pipeline Strategy
# हिंदी में: Monorepo Pipeline की रणनीति

---

## 🔵 Simple Definition (English)
A monorepo keeps several apps (web, api, workers, shared libs) in one Git repository. A monorepo pipeline detects which folders changed and runs only the jobs for those parts, so a typo fix in the docs does not rebuild every Docker image.

## 🔵 सरल परिभाषा (Hindi)
Monorepo में कई apps (web, api, workers, shared libs) एक ही Git repository में रहते हैं। Monorepo pipeline पहचानता है कि कौन से folders बदले और सिर्फ उन्हीं हिस्सों के jobs चलाता है, ताकि docs की typo ठीक करने पर हर Docker image दोबारा build न हो।

---

## 🔴 Problem it Solves
- Every commit triggers every build: 25 minutes of CI for a one-line CSS fix.
- Wasted runner minutes and cost.
- Developers stop waiting for CI or ignore failures.
- Shared library change must still test every app that uses it.

## 🔴 यह क्यों बना? (Hindi)
- हर commit पर हर build: एक लाइन CSS fix के लिए 25 मिनट CI।
- Runner minutes और पैसे की बर्बादी।
- Developers CI का इंतज़ार नहीं करते या failures ignore करते हैं।
- Shared library बदले तो उसे इस्तेमाल करने वाले हर app को फिर भी test करना ज़रूरी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Layout: apps/web, apps/api, packages/shared, .github/workflows
Step 2 → "changes" job runs a path filter against the diff
Step 3 → It outputs booleans: web=true, api=false, shared=true
Step 4 → Downstream jobs use "if: needs.changes.outputs.web == 'true'"
Step 5 → Shared change expands to dependents (web and api both run)
Step 6 → A final "gate" job summarises results for branch protection
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Layout: apps/web, apps/api, packages/shared, .github/workflows
Step 2 → "changes" job diff पर path filter चलाता है
Step 3 → Output booleans: web=true, api=false, shared=true
Step 4 → आगे के jobs "if: needs.changes.outputs.web == 'true'" इस्तेमाल करते हैं
Step 5 → Shared बदला तो dependents (web और api दोनों) भी चलते हैं
Step 6 → अंत में "gate" job branch protection के लिए सारांश देता है
```

---

## 🟡 Real World Example
A company has `apps/storefront` (React), `apps/orders-api` (FastAPI), `apps/admin` and `packages/ui`. Median PR touches one app. After adding path filters, average CI time dropped from 22 to 6 minutes and the monthly GitHub Actions bill fell by about 60 percent. Changing `packages/ui` correctly triggers storefront and admin only, not the API.

## 🟡 Real Example Hindi mein
एक कंपनी में `apps/storefront` (React), `apps/orders-api` (FastAPI), `apps/admin` और `packages/ui` हैं। आम PR एक ही app छूता है। Path filters जोड़ने के बाद औसत CI समय 22 से 6 मिनट हुआ और मासिक GitHub Actions bill लगभग 60 प्रतिशत घटा। `packages/ui` बदलने पर सही तरह सिर्फ storefront और admin चलते हैं, API नहीं।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/api-only.yml  (native path filtering)
name: API CI                           # Workflow name
on:
  pull_request:
    paths:                             # Run only if these paths change
      - "apps/orders-api/**"           # The API code
      - "packages/shared/**"           # Shared code the API imports
      - ".github/workflows/api-only.yml"   # The workflow itself
jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/orders-api   # Run commands inside the app folder
    steps:
      - uses: actions/checkout@v4      # Get code
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt pytest   # Install
      - run: pytest -q                 # Test
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/monorepo.yml
name: Monorepo
on:
  push:
    branches: [main]
  pull_request:
concurrency:
  group: mono-${{ github.ref }}
  cancel-in-progress: true
permissions:
  contents: read
  pull-requests: read                  # paths-filter needs this on PRs
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      web: ${{ steps.f.outputs.web }}   # "true" or "false"
      api: ${{ steps.f.outputs.api }}
    steps:
      - uses: actions/checkout@v4
      - id: f
        uses: dorny/paths-filter@v3     # Third-party action, pin by SHA in production
        with:
          filters: |
            shared: &shared
              - 'packages/shared/**'
            web:
              - 'apps/storefront/**'
              - *shared                 # Shared change triggers web too
            api:
              - 'apps/orders-api/**'
              - *shared
  web:
    needs: changes
    if: needs.changes.outputs.web == 'true'   # Skip when unchanged
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: package-lock.json   # Root lockfile in npm workspaces
      - run: npm ci                                  # Install whole workspace
      - run: npm run build --workspace apps/storefront   # Build only this workspace
  api:
    needs: changes
    if: needs.changes.outputs.api == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: apps/orders-api/requirements.txt
      - run: pip install -r apps/orders-api/requirements.txt pytest
      - run: pytest -q apps/orders-api
  gate:
    if: always()                       # Run even when others are skipped
    needs: [changes, web, api]
    runs-on: ubuntu-latest
    steps:
      - name: Fail if any needed job failed or was cancelled
        run: |
          # "skipped" is fine, "failure" and "cancelled" are not
          if [[ "${{ contains(needs.*.result, 'failure') }}" == "true" || "${{ contains(needs.*.result, 'cancelled') }}" == "true" ]]; then
            exit 1
          fi
```

---

## 🟠 My Stack Integration
Set branch protection to require only the `gate` job. If you require `web` and `api` directly, skipped jobs can block merges. Docker builds use a per-app context:

```yaml
# Snippet for build job of one app in the same workflow
  build-api:
    needs: [changes, api]              # Build only after tests
    if: needs.changes.outputs.api == 'true' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: .                   # Root context so COPY can reach packages/shared
          file: apps/orders-api/Dockerfile   # Per-app Dockerfile
          push: false                  # Add login and push=true for real releases
          tags: orders-api:${{ github.sha }}
```

Tools like Turborepo or Nx add task graphs and remote cache; not covered or run here.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting shared packages in the filter.
✅ Correct: Include shared paths in every dependent app's filter.

❌ Mistake 2: Requiring path-filtered workflows in branch protection; skipped workflows stay "pending".
✅ Correct: Use a single always-running `gate` job.

❌ Mistake 3: `fetch-depth: 1` with git diff tools that need history.
✅ Correct: Use `dorny/paths-filter` (uses the API for PRs) or `fetch-depth: 0` when needed.

❌ Mistake 4: Not including the workflow file itself in paths.
✅ Correct: Add the workflow path so pipeline edits are tested.

Security: third-party actions like paths-filter should be pinned to a commit SHA.

---

## 🧠 Tricky Interview Question
A PR changes only `README.md`, no jobs run, and the merge button stays blocked "Waiting for status". Why?

Answer: Required checks were configured for workflows skipped by `paths:` at workflow level, so those checks never report. Use job-level `if` conditions with a final always-run gate job (reports success), and require that one.

---

## ⚫ Interview Questions + Answers

Q1: Monorepo pros and cons?
A1: Pros: atomic cross-app changes, shared tooling. Cons: slower clones, need smart CI, coarse access control.

Q2: `paths` vs `paths-filter`?
A2: `paths` filters entire workflows. `paths-filter` lets one workflow compute per-area booleans and run chosen jobs.

Q3: How to handle shared lib changes?
A3: Treat it as upstream of dependents; map it into each dependent filter, or use Nx/Turbo dependency graph.

Q4: Docker build context in a monorepo?
A4: Use repo root as context with `-f apps/x/Dockerfile` and a `.dockerignore` so the context stays small.

Q5: How to cache efficiently?
A5: Per-app cache scope (`scope=api`) and per-app dependency lockfile paths.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several apps and libraries evolve together and share code.

❌ Avoid when:
- Teams need strict independent permissions or totally unrelated stacks.

---

## 📊 Visual Diagram
```
 PR diff --> [changes job: path filter]
                 |        |        |
              web=T     api=F   shared=T
                 |                 |
                 v                 v
              web job          (expands to web + api)
                 \_______ gate (always) ________/
                              |
                     branch protection checks gate
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Monorepo | Many projects, one repo | एक repo में कई projects |
| Path filter | Run by changed files | बदली files के हिसाब से चलाना |
| Gate job | Single required status | एकमात्र ज़रूरी status job |
| Workspace | Package group in one repo | एक repo के भीतर package समूह |
| Remote cache | Shared build cache | साझा build cache |

---

## ⚡ 3-Line Summary
English: Detect changed areas and run only affected jobs.
English: Shared packages must trigger their dependents.
English: Use one always-run gate job for branch protection.
Hindi: बदले हुए हिस्से पहचानें और सिर्फ प्रभावित jobs चलाएँ।
Hindi: Shared packages अपने dependents को trigger करें।
Hindi: Branch protection के लिए एक always-run gate job रखें।

---

## ➡️ Next Topic
367. Microservices Pipeline: many independently deployable services, each with its own release.
