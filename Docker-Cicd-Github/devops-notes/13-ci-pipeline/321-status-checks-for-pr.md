# 321. Status Checks for PR
# हिंदी में: PR के लिए Status Checks

---

## 🔵 Simple Definition (English)
A status check is a pass/fail/pending signal attached to a commit and shown on a pull request. Every GitHub Actions job automatically becomes a check run (green tick, red cross, yellow dot). Third-party tools (Codecov, SonarCloud, Vercel) report checks too. They tell reviewers whether the code is healthy.

## 🔵 सरल परिभाषा (Hindi)
Status check एक pass/fail/pending संकेत है जो commit से जुड़ा होता है और pull request पर दिखता है। GitHub Actions का हर job अपने-आप check run बन जाता है (हरा tick, लाल cross, पीला dot)। तीसरे पक्ष के tools (Codecov, SonarCloud, Vercel) भी checks report करते हैं। ये reviewers को बताते हैं कि code स्वस्थ है या नहीं।

---

## 🔴 Problem it Solves
Without checks, "is this PR safe to merge?" depends on someone remembering to run tests and read results. Checks make the answer visible and machine-readable at the bottom of every PR, and (with required checks, topic 322) enforceable.

## 🔴 यह क्यों बना? (Hindi)
Checks के बिना "क्या यह PR merge के लिए सुरक्षित है?" इस पर निर्भर करता है कि किसी को tests चलाना और results पढ़ना याद रहा या नहीं। Checks जवाब को हर PR के नीचे दिखने योग्य और machine-readable बनाते हैं, और (required checks से, topic 322) लागू भी करवाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → PR opened / new commit pushed → workflows with matching triggers start
Step 2 → Each job creates a check run on the head commit (queued → in_progress)
Step 3 → Check name = job name (or "workflow / job" in the UI); matrix adds suffixes
Step 4 → Job ends: conclusion = success | failure | cancelled | skipped
Step 5 → PR "Checks" box lists all runs with details links to logs
Step 6 → Apps (Codecov, SonarCloud) also post checks or commit statuses via API
Step 7 → Merge box summarises: "All checks have passed" or "Some checks failed"
Step 8 → If branch protection requires them, merge button stays disabled until green
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → PR खुला / नया commit push → मेल खाते triggers वाले workflows शुरू
Step 2 → हर job head commit पर check run बनाता है (queued → in_progress)
Step 3 → Check का नाम = job का नाम (UI में "workflow / job"); matrix में suffix जुड़ता है
Step 4 → Job खत्म: conclusion = success | failure | cancelled | skipped
Step 5 → PR का "Checks" box सभी runs को logs के links के साथ दिखाता है
Step 6 → Apps (Codecov, SonarCloud) भी API से checks या commit statuses भेजते हैं
Step 7 → Merge box सार देता है: "All checks have passed" या "Some checks failed"
Step 8 → Branch protection में required हों तो green होने तक merge button बंद रहता है
```

---

## 🟡 Real World Example
A PR shows six checks: `lint`, `unit-tests (node 20)`, `integration`, `CodeQL`, `trivy`, `codecov/patch`. The first five pass; `codecov/patch` is red at 62% (target 80%). The author sees exactly which signal failed, clicks Details, adds tests, pushes, and the check re-runs automatically.

## 🟡 Real Example Hindi mein
एक PR पर छह checks दिखते हैं: `lint`, `unit-tests (node 20)`, `integration`, `CodeQL`, `trivy`, `codecov/patch`। पहले पाँच pass हैं; `codecov/patch` 62% पर लाल है (target 80%)। Author को ठीक पता चलता है कि कौन सा signal fail हुआ, Details क्लिक करके tests जोड़ता है, push करता है और check अपने-आप दोबारा चलता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/ci.yml  (basic: two jobs = two status checks)
name: CI                               # Workflow name shown as prefix in the checks list

on: [pull_request]                     # Create checks on every PR

jobs:
  lint:                                # Check named "CI / lint"
    runs-on: ubuntu-latest             # Runner
    steps:
      - uses: actions/checkout@v4      # Get code
      - uses: actions/setup-node@v4    # Node
        with:
          node-version: 20
          cache: npm
      - run: npm ci                    # Install
      - run: npm run lint              # Non-zero exit = failed check
  test:                                # Check named "CI / test"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm test -- --ci
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/ci.yml  (stable check names, matrix, one summary check for branch protection)
name: CI

on:
  pull_request:                        # No paths filter here, see mistakes section
  push:
    branches: [main]

permissions:
  contents: read
  checks: write                        # Only needed if you create custom check runs

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true             # Superseded runs show as cancelled, not failed

jobs:
  lint:
    name: Lint                         # Explicit, stable check name
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run lint

  unit:
    name: Unit tests (Node ${{ matrix.node }})   # Names: "Unit tests (Node 18)" etc.
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      fail-fast: false
      matrix:
        node: [18, 20]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: npm
      - run: npm ci
      - run: npm test -- --ci

  api-tests:
    name: FastAPI tests
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip, cache-dependency-path: api/requirements*.txt }
      - run: pip install -r api/requirements.txt -r api/requirements-dev.txt
      - run: pytest api -q

  ci-ok:                               # One aggregate check: protect THIS name only
    name: CI OK
    if: always()                       # Run even if upstream jobs failed or were skipped
    needs: [lint, unit, api-tests]     # Wait for all of them
    runs-on: ubuntu-latest
    steps:
      - name: Evaluate results
        env:
          RESULTS: ${{ join(needs.*.result, ' ') }}   # e.g. "success success failure"
        run: |
          echo "Job results: $RESULTS"
          # Fail if any needed job failed or was cancelled
          if echo "$RESULTS" | grep -Eq 'failure|cancelled'; then
            echo "One or more required jobs failed"
            exit 1
          fi
          echo "All good"
```

Optional custom check from a script (rare; commit status via API):
```bash
#!/usr/bin/env bash
# post-status.sh : report a custom commit status (needs repo status permission)
set -euo pipefail                      # Safe shell options
# $1 = state (success|failure|pending), $2 = context name, $3 = description
gh api "repos/${GITHUB_REPOSITORY}/statuses/${GITHUB_SHA}" \
  -f state="$1" \
  -f context="$2" \
  -f description="$3" \
  -f target_url="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"
```

---

## 🟠 My Stack Integration
- **Monorepo (Node API + FastAPI + React):** Separate jobs per service give separate, readable checks. Use the aggregate `CI OK` job to protect a single stable name.
- **Docs-only PRs:** If you use `paths:` filters, a skipped workflow leaves required checks "Expected, waiting" forever. Prefer job-level `if` or `dorny/paths-filter` inside one workflow, keeping the aggregate job running.
- **Deploy to VPS:** Deploy jobs run on `push` to main, not as PR checks. Optionally a preview deploy job on PRs reports a check with the URL.
- **Security:** Checks from workflows on forks run with read-only tokens; do not rely on them for secrets-dependent steps. Names must not leak internal info.

```yaml
# Show which checks a PR currently has (GitHub CLI), useful when naming required checks
# gh pr checks 57              # Lists name, state, duration, link for PR number 57
# gh pr checks 57 --watch      # Waits and prints updates until done
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Renaming a job after it was set as required, so branch protection waits forever for the old name.
✅ Correct: Keep names stable; update the protection rule when renaming.

❌ Mistake 2: `paths:` filter on the workflow while the check is required.
✅ Correct: Run always and skip inside, or use an aggregate job with `if: always()`.

❌ Mistake 3: Duplicate names across workflows (two jobs called `test`), making it unclear which is required.
✅ Correct: Unique, descriptive `name:` values.

❌ Mistake 4: `continue-on-error: true` on a job making a broken job show green.
✅ Correct: Remove it, or report the problem as a separate warning.

❌ Mistake 5: Aggregate job without `if: always()`, so it is skipped when a dependency fails and appears as passed/neutral.
✅ Correct: `if: always()` and an explicit result check.

---

## 🧠 Tricky Interview Question
All your jobs pass but the PR merge box still says "Expected: waiting for status to be reported" and cannot merge. What happened?

Answer: A required check never reported. Common causes: the workflow did not trigger (a `paths`/`branches` filter excluded this PR), the job was renamed so the required name no longer exists, the job is in a workflow that needs approval (first-time contributor), or a matrix changed the check names (`Unit tests (Node 20)` vs `Unit tests`). Fix by making the workflow always run (or add an aggregate job), match the exact check name in the protection rule, and approve pending workflow runs.

---

## ⚫ Interview Questions + Answers

Q1: Check run vs commit status?
A1: Check runs (Checks API, used by Actions) have rich output, annotations and re-run buttons. Commit statuses (Statuses API) are simpler state+context+URL, used by older integrations.

Q2: What are possible job conclusions?
A2: success, failure, cancelled, skipped, neutral, timed_out, action_required, stale.

Q3: How do matrix jobs appear?
A3: One check per combination; the name is `job-name (value1, value2)` unless you set `name:`.

Q4: How can you re-run only failed jobs?
A4: In the Actions run page, "Re-run failed jobs", or `gh run rerun <id> --failed`.

Q5: Why use an aggregate job?
A5: Matrix and conditional job names change; one stable `CI OK` check is easy to require and tolerates refactoring.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every repo with a shared main branch.
- You combine tests, lint, scans, coverage in one PR view.
- You want merge decisions based on evidence.

❌ Avoid when:
- Checks take 40 minutes (people bypass them; speed them up).
- Flaky checks are required (they train people to click re-run blindly).
- Too many tiny checks that clutter the PR; group them logically.

---

## 📊 Visual Diagram
```
  PR #57 (head commit abc123)
   ┌───────────────────────────────────────────────┐
   │ Checks                                        │
   │  ✅ CI / Lint                                 │
   │  ✅ CI / Unit tests (Node 18)                 │
   │  ✅ CI / Unit tests (Node 20)                 │
   │  ❌ CI / FastAPI tests      ← Details → logs  │
   │  🟡 CodeQL / Analyze        (in progress)     │
   │  ✅ codecov/patch                             │
   │  ❌ CI / CI OK              (aggregate)       │
   └───────────────────────────────────────────────┘
                     │
        Merge button: disabled until required checks are ✅
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Status check | Pass/fail signal on a commit | commit पर pass/fail संकेत |
| Check run | A single result from Actions/App | Actions/App का एक नतीजा |
| Commit status | Older simple state API | पुराना सरल state API |
| Conclusion | Final result of a check | check का अंतिम नतीजा |
| Aggregate job | One job summarising others | बाकी jobs का सार देने वाला job |
| Required check | Check that must pass to merge | merge के लिए pass होना ज़रूरी check |

---

## ⚡ 3-Line Summary
English: Each job becomes a status check on the PR, plus checks from apps like Codecov.
English: Stable names, no risky path filters and an aggregate job keep checks reliable.
English: Checks turn CI results into visible, enforceable merge signals.
Hindi: हर job PR पर status check बन जाता है, साथ में Codecov जैसे apps के checks भी।
Hindi: स्थिर नाम, जोखिम भरे path filters से बचाव और aggregate job checks को भरोसेमंद रखते हैं।
Hindi: Checks CI नतीजों को दिखने योग्य और लागू करने योग्य merge signals बना देते हैं।

Note: YAML parsed and bash syntax-checked locally; check-name behaviour not observed on live GitHub.

---

## ➡️ Next Topic
322. Required Status Checks: make selected checks mandatory with branch protection or rulesets so failing code cannot merge.
