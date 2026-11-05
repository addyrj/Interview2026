# 313. Upload Coverage Report
# हिंदी में: Coverage Report Upload करना

---

## 🔵 Simple Definition (English)
Uploading a coverage report means sending the files produced by Jest/pytest (lcov.info, coverage.xml, HTML) out of the temporary runner, either as a GitHub artifact (download later) or to a service like Codecov (history, graphs, PR diff coverage).

## 🔵 सरल परिभाषा (Hindi)
Coverage report upload करने का मतलब है Jest/pytest से बनी files (lcov.info, coverage.xml, HTML) को अस्थायी runner से बाहर भेजना, या तो GitHub artifact के रूप में (बाद में download के लिए) या Codecov जैसी service पर (history, graphs, PR diff coverage)।

---

## 🔴 Problem it Solves
The runner is deleted when the job ends, so the HTML report disappears. Reviewers cannot see which lines are untested, and nobody can compare coverage between today and last month. Upload makes results visible, shareable and trackable over time.

## 🔴 यह क्यों बना? (Hindi)
Job खत्म होते ही runner मिट जाता है, इसलिए HTML report भी गायब हो जाती है। Reviewers नहीं देख पाते कि कौन सी lines untested हैं, और आज बनाम पिछले महीने की तुलना नहीं हो पाती। Upload से नतीजे दिखने योग्य, share योग्य और समय के साथ trackable बनते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Coverage step produces files (coverage/lcov.info, coverage.xml)
Step 2 → Option A: actions/upload-artifact zips them to the run page
Step 3 → Option B: codecov/codecov-action reads the report file
Step 4 → Action authenticates (CODECOV_TOKEN secret, or OIDC/tokenless for public repos)
Step 5 → Codecov stores data against the commit SHA and PR number
Step 6 → Codecov compares with base branch, computes patch coverage
Step 7 → A status check + optional PR comment appears on the pull request
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Coverage step files बनाता है (coverage/lcov.info, coverage.xml)
Step 2 → Option A: actions/upload-artifact उन्हें run page पर zip करके रखता है
Step 3 → Option B: codecov/codecov-action report file पढ़ता है
Step 4 → Action authenticate होता है (CODECOV_TOKEN secret, या public repo में tokenless)
Step 5 → Codecov data को commit SHA और PR number के साथ store करता है
Step 6 → Codecov base branch से तुलना करके patch coverage निकालता है
Step 7 → PR पर status check + वैकल्पिक comment दिखता है
```

---

## 🟡 Real World Example
Your team merges 15 PRs a week. Using Codecov, each PR shows "patch coverage 62%, project coverage -0.4%". The reviewer clicks through to the file view and sees the red lines of the new refund function with no test. The author adds tests, patch coverage turns 94%, the Codecov status goes green.

## 🟡 Real Example Hindi mein
आपकी टीम हफ़्ते में 15 PRs merge करती है। Codecov से हर PR पर दिखता है "patch coverage 62%, project coverage -0.4%"। Reviewer file view खोलकर नए refund function की बिना test वाली लाल lines देखता है। Author tests जोड़ता है, patch coverage 94% होता है, Codecov status हरा हो जाता है।

---

## 💻 Code / Config Example — Basic
```yaml
# Basic: keep the HTML report as a downloadable artifact
name: Coverage Upload Basic            # Workflow name

on: [pull_request]                     # Run on PRs

jobs:
  coverage:
    runs-on: ubuntu-latest             # Runner
    steps:
      - uses: actions/checkout@v4      # Get code
      - uses: actions/setup-node@v4    # Node
        with:
          node-version: 20
          cache: npm
      - run: npm ci                    # Install
      - run: npx jest --ci --coverage  # Produces ./coverage
      - uses: actions/upload-artifact@v4   # Upload the folder
        if: always()                   # Even if tests failed
        with:
          name: coverage-report        # Name shown in run summary
          path: coverage/              # Folder to zip
          if-no-files-found: error     # Fail loudly if path is wrong
          retention-days: 14           # Auto delete after 14 days
```

## 💻 Code / Config Example — Advanced
```yaml
# Advanced: artifact + Codecov for Node and Python, with flags
name: Coverage Upload

on:
  pull_request:
  push:
    branches: [main]                   # Main uploads define the baseline for comparison

permissions:
  contents: read                       # Read-only

jobs:
  backend:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: backend/package-lock.json
      - run: npm ci
      - run: npx jest --ci --coverage --coverageReporters=lcov --coverageReporters=text
      - uses: codecov/codecov-action@v5      # Version is an example; check releases
        with:
          token: ${{ secrets.CODECOV_TOKEN }}      # Repo upload token stored as secret
          files: backend/coverage/lcov.info        # Report path from repo root
          flags: backend-node                      # Separate series in Codecov UI
          fail_ci_if_error: true                   # Do not silently skip a failed upload
          disable_search: true                     # Use only the file listed above

  api:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    defaults:
      run:
        working-directory: api
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: api/requirements*.txt
      - run: pip install -r requirements.txt -r requirements-dev.txt pytest-cov
      - run: pytest --cov=app --cov-report=xml --cov-report=html   # coverage.xml + htmlcov/
      - uses: actions/upload-artifact@v4       # Human-readable HTML for reviewers
        if: always()
        with:
          name: api-htmlcov
          path: api/htmlcov/
          retention-days: 14
      - uses: codecov/codecov-action@v5
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: api/coverage.xml
          flags: api-fastapi
          fail_ci_if_error: true
          disable_search: true
```

Optional `codecov.yml` at repo root (controls PR gating, check against Codecov docs for your version):
```yaml
# codecov.yml
coverage:                              # Section for status checks
  status:
    project:                           # Whole-project coverage check
      default:
        target: auto                   # Compare to base commit
        threshold: 1%                  # Allow a 1% drop
    patch:                             # Only the lines changed in the PR
      default:
        target: 80%                    # New code must be 80% covered
comment:                               # PR comment layout
  layout: "diff, files"                # Show diff and file list
```

---

## 🟠 My Stack Integration
- **Node.js backend / React frontend:** Upload separate `flags` (`backend-node`, `frontend`) so one failing area is visible.
- **FastAPI:** Upload `coverage.xml`; keep `htmlcov/` as an artifact for quick review.
- **Secrets:** Add `CODECOV_TOKEN` under repo Settings, Secrets and variables, Actions. Forked PRs do not get secrets, so uploads may be skipped or use tokenless mode for public repos.
- **VPS/AWS:** Not involved; but a Dockerfile with `COPY . .` can accidentally ship `coverage/`. Keep it in `.dockerignore`.

```yaml
# Guard: do not fail forked PRs that cannot read secrets
      - uses: codecov/codecov-action@v5
        if: github.event.pull_request.head.repo.full_name == github.repository || github.event_name == 'push'
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: backend/coverage/lcov.info
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting `CODECOV_TOKEN` in the YAML in plain text.
✅ Correct: Store as an encrypted secret and reference `${{ secrets.CODECOV_TOKEN }}`.

❌ Mistake 2: Wrong `path:` so the artifact is empty and nobody notices.
✅ Correct: `if-no-files-found: error`.

❌ Mistake 3: Uploading only on PRs, never on main, so Codecov has no baseline.
✅ Correct: Run on `push` to main as well.

❌ Mistake 4: Upload step skipped when tests fail, hiding the very report you need.
✅ Correct: `if: always()` for artifacts.

❌ Mistake 5: Same artifact name in matrix legs (v4 artifacts are immutable, so conflicts occur).
✅ Correct: Include the matrix value in `name:`.

---

## 🧠 Tricky Interview Question
Codecov upload works on your branch PRs but fails for a contributor's fork PR with "token required". Why, and what are the options?

Answer: GitHub does not pass repository secrets to workflows triggered by `pull_request` from forks, so `CODECOV_TOKEN` is empty. Options: for public repos enable tokenless uploads in Codecov settings, make the step conditional, or use a separate trusted `workflow_run` workflow to upload. Do not switch to `pull_request_target` and check out fork code with secrets: that allows untrusted code to steal the token.

---

## ⚫ Interview Questions + Answers

Q1: Artifact vs Codecov?
A1: Artifacts are raw files stored per run for a limited time. Codecov stores parsed history, compares commits, and posts PR checks.

Q2: Why `fail_ci_if_error: true`?
A2: By default an upload failure only warns. With true, a broken upload fails CI, so you do not silently lose coverage data.

Q3: What is a coverage flag?
A3: A label (backend, frontend) that segments reports so each part has its own trend and threshold.

Q4: How long are artifacts kept?
A4: Default 90 days (repo/org settings can change); set `retention-days` smaller to save storage.

Q5: Is the coverage report sensitive?
A5: It reveals source structure and file paths. For private repos use a token and a trusted service; HTML artifacts are visible to anyone with repo read access.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need history, trends and patch coverage on PRs.
- Reviewers need to browse uncovered lines.
- Several services (Node, FastAPI) need combined view.

❌ Avoid when:
- Repo is tiny and a text summary in `$GITHUB_STEP_SUMMARY` is enough.
- Policy forbids sending code metadata to third parties (use artifacts or self-hosted tools).

---

## 📊 Visual Diagram
```
 jest/pytest ──▶ coverage/lcov.info, coverage.xml, htmlcov/
                         │
          ┌──────────────┴───────────────┐
          ▼                              ▼
  upload-artifact                  codecov-action
  (zip on run page)             (token + commit SHA)
          │                              │
          ▼                              ▼
  download & browse           Codecov: history, graphs
                                         │
                                         ▼
                           PR: status check + comment
                           (project %, patch %)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Artifact | File saved from a workflow run | workflow run से सहेजी file |
| Codecov | Hosted coverage tracking service | hosted coverage tracking service |
| Flag | Label to group coverage uploads | uploads को group करने का label |
| Patch coverage | Coverage of PR-changed lines | PR में बदली lines का coverage |
| Retention | How long data is kept | data कितने दिन रखा जाए |
| Baseline | Reference coverage on main | main का संदर्भ coverage |

---

## ⚡ 3-Line Summary
English: Runner files vanish, so upload coverage as artifacts or to Codecov.
English: Codecov gives history, flags and patch coverage checks on every PR.
English: Keep tokens in secrets, upload from main too, and handle fork PRs safely.
Hindi: Runner की files गायब हो जाती हैं, इसलिए coverage को artifact या Codecov पर upload करें।
Hindi: Codecov हर PR पर history, flags और patch coverage checks देता है।
Hindi: Tokens secrets में रखें, main से भी upload करें, और fork PRs सुरक्षित तरीके से संभालें।

Note: action versions and codecov.yml keys are examples to verify against current docs; not run on GitHub.

---

## ➡️ Next Topic
314. Code Quality (SonarCloud): coverage tells what is tested; SonarCloud also finds bugs, code smells and duplication.
