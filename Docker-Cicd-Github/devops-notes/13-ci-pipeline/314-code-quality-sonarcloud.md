# 314. Code Quality (SonarCloud)
# हिंदी में: Code Quality जाँच (SonarCloud)

---

## 🔵 Simple Definition (English)
SonarCloud is a hosted static analysis service. A CI step sends your code and coverage to it; it detects bugs, vulnerabilities, security hotspots, code smells and duplication, then applies a Quality Gate (pass/fail) to the pull request.

## 🔵 सरल परिभाषा (Hindi)
SonarCloud एक hosted static analysis service है। CI का एक step आपका code और coverage उसे भेजता है; वह bugs, vulnerabilities, security hotspots, code smells और duplication ढूँढता है, फिर pull request पर Quality Gate (pass/fail) लगाता है।

---

## 🔴 Problem it Solves
Linters catch style issues, tests catch behaviour, but neither measures maintainability trends: duplicated blocks, huge functions, hard-coded secrets, SQL built by string concatenation. Manual review misses them. SonarCloud automates this and focuses on "new code" so legacy debt does not block work.

## 🔴 यह क्यों बना? (Hindi)
Linters style की गलतियाँ पकड़ते हैं, tests behaviour पकड़ते हैं, पर maintainability का trend कोई नहीं नापता: duplicate blocks, बहुत बड़े functions, hard-coded secrets, string जोड़कर बनी SQL। Manual review इन्हें चूक जाता है। SonarCloud यह automate करता है और "new code" पर ध्यान देता है ताकि पुराना कर्ज़ काम न रोके।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create SonarCloud project (import GitHub repo), note organization + project key
Step 2 → Generate SONAR_TOKEN, save it as a GitHub secret
Step 3 → Add sonar-project.properties (sources, tests, coverage paths)
Step 4 → Workflow: checkout with fetch-depth 0 (full history for blame/new code)
Step 5 → Run tests + coverage first so lcov.info / coverage.xml exist
Step 6 → SonarCloud scan action analyses and uploads results
Step 7 → Quality Gate evaluated (new bugs, coverage on new code, duplication)
Step 8 → Result shows on the PR as a check; fail gate = red check
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → SonarCloud project बनाएँ (GitHub repo import), organization + project key नोट करें
Step 2 → SONAR_TOKEN बनाकर GitHub secret में रखें
Step 3 → sonar-project.properties जोड़ें (sources, tests, coverage paths)
Step 4 → Workflow: fetch-depth 0 के साथ checkout (पूरी history चाहिए)
Step 5 → पहले tests + coverage चलाएँ ताकि lcov.info / coverage.xml बन जाएँ
Step 6 → SonarCloud scan action analyse करके नतीजे upload करता है
Step 7 → Quality Gate जाँचा जाता है (नए bugs, new code का coverage, duplication)
Step 8 → नतीजा PR पर check बनकर दिखता है; gate fail = लाल check
```

---

## 🟡 Real World Example
A developer in your FastAPI team builds a query as `f"SELECT * FROM users WHERE email = '{email}'"`. SonarCloud flags it as a SQL injection vulnerability (rating E on new code) and the Quality Gate fails: "Security Rating on New Code is worse than A". The developer switches to parameterised queries before review even starts.

## 🟡 Real Example Hindi mein
आपकी FastAPI टीम का developer query ऐसे बनाता है: `f"SELECT * FROM users WHERE email = '{email}'"`। SonarCloud इसे SQL injection vulnerability (new code पर rating E) बताता है और Quality Gate fail होता है: "Security Rating on New Code is worse than A"। Review शुरू होने से पहले ही developer parameterised queries पर आ जाता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/sonar.yml  (basic scan, no coverage)
name: SonarCloud                       # Workflow name

on:
  pull_request:                        # Analyse PRs
    types: [opened, synchronize, reopened]   # New PR, new commits, reopened
  push:
    branches: [main]                   # Analyse main to keep the baseline

jobs:
  sonar:
    runs-on: ubuntu-latest             # Runner
    steps:
      - uses: actions/checkout@v4      # Get code
        with:
          fetch-depth: 0               # Full history; shallow clones break new-code detection
      - uses: SonarSource/sonarcloud-github-action@v3   # Example version; newer: sonarqube-scan-action
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}       # Auth token from secrets
          # GITHUB_TOKEN is injected automatically for PR decoration where needed
```

`sonar-project.properties` (repo root):
```properties
# sonar-project.properties
sonar.organization=your-org-key
sonar.projectKey=your-org-key_your-repo
sonar.sources=backend/src,api/app,frontend/src
sonar.tests=backend/tests,api/tests
sonar.exclusions=**/node_modules/**,**/migrations/**,**/*.min.js
sonar.javascript.lcov.reportPaths=backend/coverage/lcov.info
sonar.python.coverage.reportPaths=api/coverage.xml
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/sonar.yml  (tests + coverage + scan + quality gate wait)
name: SonarCloud

on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main]

permissions:
  contents: read                       # Code read
  pull-requests: read                  # Needed so the scanner can read PR info

concurrency:
  group: sonar-${{ github.ref }}
  cancel-in-progress: true             # Skip stale scans

jobs:
  analyse:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    # Same-repo PRs only: fork PRs do not receive SONAR_TOKEN
    if: github.event_name == 'push' || github.event.pull_request.head.repo.full_name == github.repository
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0               # Required for blame and new code period
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: backend/package-lock.json
      - name: Node tests with lcov
        working-directory: backend
        run: |
          npm ci
          npx jest --ci --coverage --coverageReporters=lcov
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: api/requirements*.txt
      - name: Python tests with coverage.xml
        working-directory: api
        run: |
          pip install -r requirements.txt -r requirements-dev.txt pytest-cov
          pytest --cov=app --cov-report=xml
      - name: SonarCloud scan
        uses: SonarSource/sonarcloud-github-action@v3
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        with:
          args: >
            -Dsonar.qualitygate.wait=true
            -Dsonar.qualitygate.timeout=300
```

---

## 🟠 My Stack Integration
- **Node.js/React:** point `sonar.javascript.lcov.reportPaths` to Jest's `lcov.info`; exclude `build/`, `.next/`.
- **FastAPI:** `sonar.python.coverage.reportPaths=api/coverage.xml`; set `sonar.python.version=3.12`.
- **Monorepo:** Keep one Sonar project with multiple source folders, or one project per service using `sonar.projectBaseDir`.
- **Security:** Sonar flags hard-coded credentials, weak crypto, unsafe `eval`, SQL/NoSQL injection. Treat Security Hotspots as review tasks, not auto-bugs.
- **Dockerfiles/YAML:** SonarCloud can also analyse Dockerfile and GitHub Actions workflows for risky patterns.

```yaml
# Branch protection: add the "SonarCloud Code Analysis" check as required (topic 322)
# Quality Gate suggestion (set in SonarCloud UI, not in YAML):
#  - Coverage on New Code >= 80%
#  - Duplicated Lines on New Code <= 3%
#  - Security / Reliability / Maintainability Rating on New Code = A
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Checkout without `fetch-depth: 0`, giving warnings and wrong new-code detection.
✅ Correct: Full-history checkout.

❌ Mistake 2: Scanning before tests, so coverage is 0%.
✅ Correct: Generate coverage first, then scan.

❌ Mistake 3: Committing `SONAR_TOKEN` or pasting it in logs.
✅ Correct: Repository secret; never echo it.

❌ Mistake 4: Analysing `node_modules`, `dist`, migrations.
✅ Correct: Use `sonar.exclusions`.

❌ Mistake 5: Forcing zero issues on legacy code.
✅ Correct: Gate on "New Code" only (Clean as You Code).

---

## 🧠 Tricky Interview Question
The SonarCloud check is green, but your teammate says a hard-coded API key got merged. How is that possible?

Answer: The Quality Gate only judges rules and thresholds you configured. A secret may be reported as a hotspot or issue that is outside "new code" (older code), downgraded in severity, marked "safe" by someone, or in a file excluded by `sonar.exclusions`. Also static analysis is not a dedicated secret scanner. Add GitHub secret scanning/push protection, gitleaks in CI, and rotate the key immediately; removing it from the file does not remove it from git history.

---

## ⚫ Interview Questions + Answers

Q1: SonarCloud vs ESLint?
A1: ESLint enforces JS style and some bugs per file. Sonar tracks bugs, vulnerabilities, smells, duplication and coverage across languages, over time, with a gate.

Q2: What is a Quality Gate?
A2: A set of conditions on metrics (usually for new code). If any fails, the analysis is marked failed and CI/PR check turns red.

Q3: What is "Clean as You Code"?
A3: Focus on keeping new/changed code clean instead of fixing all legacy issues at once.

Q4: Why are fork PRs a problem?
A4: Secrets such as `SONAR_TOKEN` are not available to fork PR workflows, so scans fail or are skipped; handle with a condition or trusted workflow.

Q5: SonarCloud vs SonarQube?
A5: SonarCloud is SaaS (free for public repos); SonarQube is self-hosted. Same engine concept.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Team wants a measurable quality bar and PR decoration.
- Multiple languages (JS/TS, Python, Docker) in one repo.
- Need duplication and maintainability trends.

❌ Avoid when:
- Private repo with strict no-external-code policy (use self-hosted SonarQube).
- Tiny prototype where the noise exceeds value.
- As the only security tool (add dependency and secret scanning).

---

## 📊 Visual Diagram
```
 PR / push ──▶ checkout (full history)
                  │
                  ▼
           tests + coverage  ──▶ lcov.info / coverage.xml
                  │
                  ▼
        SonarCloud scanner ──(SONAR_TOKEN)──▶ SonarCloud server
                                                   │
              bugs · vulnerabilities · smells · duplication
                                                   ▼
                                           Quality Gate
                                         ┌─────┴──────┐
                                       PASS ✅       FAIL ❌
                                    PR check green   PR check red
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Static analysis | Analysing code without running it | code चलाए बिना जाँच |
| Quality Gate | Pass/fail rules for metrics | metrics के pass/fail नियम |
| Code smell | Maintainability problem | maintainability की समस्या |
| Security hotspot | Code needing manual security review | जिसे हाथ से security review चाहिए |
| New Code | Code changed since baseline | baseline के बाद बदला code |
| Technical debt | Estimated time to fix issues | issues सुधारने में लगने वाला अनुमानित समय |

---

## ⚡ 3-Line Summary
English: SonarCloud statically analyses code and applies a Quality Gate to every PR.
English: Run tests first, checkout full history, give it coverage paths and a token secret.
English: Gate new code, exclude noise, and pair it with secret and dependency scanners.
Hindi: SonarCloud code का static analysis करके हर PR पर Quality Gate लगाता है।
Hindi: पहले tests चलाएँ, पूरी history checkout करें, coverage paths और token secret दें।
Hindi: New code पर gate रखें, शोर बाहर रखें, और secret व dependency scanners साथ जोड़ें।

Note: workflow YAML parsed locally only. SonarSource action names/versions change (sonarcloud-github-action is being superseded by sonarqube-scan-action); verify current docs.

---

## ➡️ Next Topic
315. Security Scanning (Snyk): next we scan dependencies and containers for known vulnerabilities.
