# 312. Generate Test Coverage
# हिंदी में: Test Coverage बनाना

---

## 🔵 Simple Definition (English)
Test coverage is a measurement of how much of your source code (lines, branches, functions) is executed while the tests run. In CI you generate a report (lcov, XML, HTML) and can fail the build if coverage drops below a threshold.

## 🔵 सरल परिभाषा (Hindi)
Test coverage यह नापता है कि tests चलने के दौरान आपके source code का कितना हिस्सा (lines, branches, functions) सच में execute हुआ। CI में आप report (lcov, XML, HTML) बनाते हैं और coverage threshold से नीचे गिरे तो build fail करा सकते हैं।

---

## 🔴 Problem it Solves
"We have tests" says nothing about what is untested. A payment module with 0% coverage can hide behind a green build. Without numbers, coverage silently decays as features are added. A threshold in CI makes the team notice.

## 🔴 यह क्यों बना? (Hindi)
"हमारे पास tests हैं" यह नहीं बताता कि क्या untested है। 0% coverage वाला payment module हरे build के पीछे छिप सकता है। संख्या के बिना नई features जुड़ने पर coverage चुपचाप गिरता रहता है। CI में threshold टीम को इसका एहसास कराता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Test runner is started with an instrumentation flag
         (jest --coverage / pytest --cov)
Step 2 → Code is instrumented (Istanbul for Jest, coverage.py for Python)
Step 3 → Tests run; every executed line/branch is recorded
Step 4 → Reports are written: coverage/lcov.info, coverage.xml, HTML folder
Step 5 → Thresholds are compared (coverageThreshold / --cov-fail-under)
Step 6 → Below threshold → non-zero exit → job fails
Step 7 → Reports are uploaded (topic 313) and summarised on the PR
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Test runner instrumentation flag के साथ शुरू होता है
         (jest --coverage / pytest --cov)
Step 2 → Code instrument होता है (Jest के लिए Istanbul, Python के लिए coverage.py)
Step 3 → Tests चलते हैं; हर executed line/branch record होती है
Step 4 → Reports लिखी जाती हैं: coverage/lcov.info, coverage.xml, HTML folder
Step 5 → Thresholds से तुलना होती है (coverageThreshold / --cov-fail-under)
Step 6 → Threshold से कम → non-zero exit → job fail
Step 7 → Reports upload होती हैं (topic 313) और PR पर सार दिखता है
```

---

## 🟡 Real World Example
Your FastAPI billing service sits at 82% coverage. A developer adds a refund feature with no tests, dropping the total to 76%. The CI step `pytest --cov=app --cov-fail-under=80` fails, and the PR cannot merge until refund paths (success, partial, double refund) are tested.

## 🟡 Real Example Hindi mein
आपकी FastAPI billing service 82% coverage पर है। Developer बिना tests के refund feature जोड़ता है और कुल coverage 76% हो जाता है। CI step `pytest --cov=app --cov-fail-under=80` fail होता है, और जब तक refund के रास्तों (success, partial, double refund) के tests नहीं लिखे जाते PR merge नहीं हो सकता।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/coverage.yml  (Jest coverage, basic)
name: Coverage                         # Workflow name

on: [pull_request]                     # Run on PRs

jobs:
  coverage:                            # Job id
    runs-on: ubuntu-latest             # Runner
    steps:
      - uses: actions/checkout@v4      # Get code
      - uses: actions/setup-node@v4    # Install Node
        with:
          node-version: 20
          cache: npm                   # Cache npm downloads
      - run: npm ci                    # Install deps
      - run: npx jest --ci --coverage  # Generates ./coverage (text, lcov, html per config)
      - run: ls -la coverage           # Show produced files (debug)
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/coverage.yml  (Jest + pytest, thresholds, step summary)
name: Coverage

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  node-coverage:
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
      - name: Jest with coverage         # Thresholds are defined in jest.config.js
        run: npx jest --ci --coverage --coverageReporters=text --coverageReporters=lcov --coverageReporters=json-summary
      - name: Write summary to job page  # Show numbers without opening artifacts
        if: always()
        run: |
          {
            echo "### Node coverage"
            echo
            head -c 600 coverage/coverage-summary.json
            echo
          } >> "$GITHUB_STEP_SUMMARY"
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: node-coverage
          path: backend/coverage/
          retention-days: 7

  python-coverage:
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
      - name: pytest with coverage and gate
        run: >-
          pytest --cov=app --cov-branch
          --cov-report=term-missing --cov-report=xml --cov-report=html
          --cov-fail-under=80
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: python-coverage
          path: |
            api/coverage.xml
            api/htmlcov/
```

Jest threshold config (the file the workflow relies on, `backend/jest.config.js`):
```javascript
// backend/jest.config.js
module.exports = {
  testEnvironment: 'node',              // Node API, not browser
  collectCoverageFrom: ['src/**/*.js', '!src/**/index.js', '!src/migrations/**'], // What to measure
  coverageDirectory: 'coverage',        // Output folder
  coverageThreshold: {                  // Fail if below these numbers
    global: { statements: 80, branches: 70, functions: 80, lines: 80 }, // Global gate
    './src/payments/': { lines: 90 },   // Stricter gate for critical folder
  },
};
```

---

## 🟠 My Stack Integration
- **Node.js:** Jest uses Istanbul. For ESM/TypeScript use `ts-jest` or `@swc/jest`; `coverageProvider: 'v8'` is faster.
- **FastAPI:** `pytest-cov` wraps `coverage.py`. Configure in `.coveragerc` (omit `tests/*`, `migrations/*`).
- **React/Next.js:** `collectCoverageFrom` should exclude generated files (`.next/`, stories).
- **VPS/AWS:** Coverage is only a CI gate; never deploy `coverage/` folders into your Docker image. Add `coverage` to `.dockerignore`.

```yaml
# .coveragerc style config for FastAPI (put in api/.coveragerc)
# [run]
# branch = True
# source = app
# omit = tests/*, app/migrations/*
# [report]
# exclude_lines =
#     pragma: no cover
#     if __name__ == .__main__.:
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Chasing 100% by writing assertion-free tests.
✅ Correct: Coverage shows what ran, not what was verified. Review assertions; use branch coverage.

❌ Mistake 2: Measuring generated code, migrations, config.
✅ Correct: Exclude them with `collectCoverageFrom` / `omit`.

❌ Mistake 3: Setting threshold too high at first, so everyone disables it.
✅ Correct: Start at current level and ratchet upward; protect critical folders more.

❌ Mistake 4: Committing the `coverage/` folder.
✅ Correct: Add to `.gitignore` and `.dockerignore`.

❌ Mistake 5: Running coverage on every matrix leg and wasting minutes.
✅ Correct: Collect coverage on one leg (e.g. Node 20) only.

---

## 🧠 Tricky Interview Question
A file has 100% line coverage but a bug still reached production. How?

Answer: Line coverage only says a line executed. A line like `return a > 0 ? x : y` is covered when only one branch is tested; branch coverage would show the other side missing. Also tests may call the code without asserting results, or never test edge values (null, empty list, boundary). Coverage is a floor to find untested code, not proof of correctness. Use branch coverage, meaningful assertions, and mutation testing for deeper confidence.

---

## ⚫ Interview Questions + Answers

Q1: Line vs branch coverage?
A1: Line coverage counts executed lines; branch coverage counts each decision path (if/else, ternary, switch). Branch is stricter.

Q2: How do you fail CI on low coverage?
A2: Jest `coverageThreshold`, pytest `--cov-fail-under=N`. The tool exits non-zero.

Q3: What percentage is good?
A3: There is no universal number. 70-85% is common; critical modules (payments, auth) deserve more. Trend and meaningful tests matter more than the exact figure.

Q4: How to avoid coverage dropping on new code only?
A4: Use "patch/diff coverage" in Codecov/SonarCloud (topics 313-314), which gates new code regardless of the legacy total.

Q5: Does coverage slow tests?
A5: Yes, instrumentation adds overhead (Jest with `v8` provider is lighter). Run on one matrix leg.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Team wants a visible quality trend.
- Critical business logic needs a safety net.
- You want to detect untested new code in PRs.

❌ Avoid when:
- It becomes a vanity metric used to rank people.
- Legacy code with no tests and a hard 90% gate (blocks all work).
- Measuring generated or vendor code.

---

## 📊 Visual Diagram
```
 source code ──instrument──▶ tests run ──▶ hit/miss data
                                              │
                          ┌───────────────────┼──────────────────┐
                          ▼                   ▼                  ▼
                    lcov.info            coverage.xml        htmlcov/
                          │                   │                  │
                          └─────────▶ threshold check ◀─────────┘
                                         │        │
                                    ≥ 80%  ✅    < 80% ❌ fail job
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Coverage | % of code executed by tests | tests से चले code का प्रतिशत |
| Branch coverage | Each decision path executed | हर decision path का execute होना |
| lcov | Text coverage format | coverage का text format |
| Threshold | Minimum allowed coverage | न्यूनतम स्वीकृत coverage |
| Instrumentation | Adding counters to code | code में गिनती जोड़ना |
| Patch coverage | Coverage of changed lines only | सिर्फ़ बदली lines का coverage |

---

## ⚡ 3-Line Summary
English: Coverage tools record which lines and branches tests execute.
English: Thresholds turn the number into a CI gate that fails the build.
English: Use branch coverage, exclude generated code, ratchet the target up slowly.
Hindi: Coverage tools record करते हैं कि tests ने कौन सी lines और branches चलाईं।
Hindi: Threshold इस संख्या को CI gate बना देता है जो build fail करता है।
Hindi: Branch coverage लें, generated code बाहर रखें, target धीरे-धीरे बढ़ाएँ।

Note: YAML parsed and JS syntax checked locally; not executed on GitHub.

---

## ➡️ Next Topic
313. Upload Coverage Report: store the reports as artifacts and send them to Codecov for history and PR diffs.
