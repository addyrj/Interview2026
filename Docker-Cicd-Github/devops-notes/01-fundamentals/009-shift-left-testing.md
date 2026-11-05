# 9. Shift Left Testing
# हिंदी में: Shift Left Testing (testing को पहले करना)

---

## 🔵 Simple Definition (English)
**Shift Left** means moving testing, security checks and quality checks earlier in the delivery timeline (to the "left" of a Plan -> Code -> Test -> Deploy diagram). Instead of finding bugs at the end, you find them while coding, in the editor, in pre-commit hooks and in CI on every pull request.

## 🔵 सरल परिभाषा (Hindi)
**Shift Left** का मतलब testing, security checks और quality checks को timeline में पहले (diagram में "बाईं" तरफ) ले आना। बग आखिर में ढूँढने की जगह आप उन्हें code लिखते समय, editor में, pre-commit hooks में और हर pull request पर CI में पकड़ते हैं।

---

## 🔴 Problem it Solves
The later a bug is found, the more it costs. A typo found while coding costs seconds; the same bug found in production costs hours of debugging, an incident, customer trust and sometimes money. Late testing also creates a QA bottleneck: developers wait days for test results. Shift left keeps feedback loops short.

## 🔴 यह क्यों बना? (Hindi)
Bug जितनी देर से मिलता है, उतना महँगा पड़ता है। Code लिखते समय मिला typo सेकंड में ठीक होता है; वही bug production में मिले तो घंटों की debugging, incident, ग्राहकों का भरोसा और कभी पैसा भी जाता है। देर से testing से QA पर bottleneck भी बनता है: developers को test results के लिए दिनों इंतज़ार। Shift left feedback loops छोटे रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 -> In the editor   : linters + type checks (ESLint, TypeScript, ruff, mypy)
Step 2 -> Before commit   : pre-commit hooks (format, secret scan, quick tests)
Step 3 -> On pull request : CI runs unit tests, integration tests, SAST, dependency scan
Step 4 -> Build time      : container image scan (Trivy), Dockerfile lint (hadolint)
Step 5 -> Pre-deploy      : infra checks (terraform validate, tfsec), contract tests
Step 6 -> After deploy    : smoke tests (shift right adds canary + monitoring)
Step 7 -> Result          : most bugs die in minutes, on the developer's machine or PR
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 -> Editor में       : linters + type checks (ESLint, TypeScript, ruff, mypy)
Step 2 -> Commit से पहले   : pre-commit hooks (format, secret scan, quick tests)
Step 3 -> Pull request पर  : CI unit tests, integration tests, SAST, dependency scan चलाता है
Step 4 -> Build के समय     : container image scan (Trivy), Dockerfile lint (hadolint)
Step 5 -> Deploy से पहले   : infra checks (terraform validate, tfsec), contract tests
Step 6 -> Deploy के बाद    : smoke tests (shift right में canary + monitoring जुड़ते हैं)
Step 7 -> नतीजा            : ज़्यादातर bugs मिनटों में, developer की machine या PR में ही मर जाते हैं
```

---

## 🟡 Real World Example
**An e-commerce checkout bug.** A developer accidentally removes a null check on the coupon field. With shift left: TypeScript flags it in the editor; if missed, the unit test fails in pre-push; if still missed, CI fails the PR in 3 minutes. Without it: QA finds it a week later, or customers find it during a sale and the support team is flooded.

**Your repo:** a leaked AWS key in `.env` committed by mistake. Shift left: a pre-commit secret scanner (gitleaks) blocks the commit locally, so the key never reaches GitHub history.

## 🟡 Real Example Hindi mein
**E-commerce checkout bug।** Developer ने गलती से coupon field का null check हटा दिया। Shift left के साथ: TypeScript editor में चेतावनी देता है; छूटा तो pre-push में unit test fail; फिर भी छूटा तो CI 3 मिनट में PR fail कर देता है। इसके बिना: QA हफ्ते भर बाद पकड़ता है, या sale के दौरान ग्राहक पकड़ते हैं और support team पर बोझ।

**आपका repo:** गलती से commit हुई `.env` में AWS key। Shift left: pre-commit secret scanner (gitleaks) commit को local पर ही रोक देता है, key कभी GitHub history में नहीं पहुँचती।

---

## 💻 Code / Config Example — Basic
Pre-commit hooks (Python `pre-commit` framework) that run before every commit.

```yaml
# .pre-commit-config.yaml - install: pip install pre-commit && pre-commit install
repos:                                           # list of hook sources
  - repo: https://github.com/pre-commit/pre-commit-hooks   # standard hooks
    rev: v4.6.0                                  # example version, update with: pre-commit autoupdate
    hooks:
      - id: trailing-whitespace                  # remove trailing spaces
      - id: end-of-file-fixer                    # ensure newline at EOF
      - id: check-yaml                           # block invalid YAML
      - id: check-added-large-files              # block accidental huge files
      - id: detect-private-key                   # block committed private keys
  - repo: https://github.com/gitleaks/gitleaks   # secret scanner
    rev: v8.18.4                                 # example version
    hooks:
      - id: gitleaks                             # scan staged changes for secrets
```

## 💻 Code / Config Example — Advanced
A PR workflow with fast checks first, then deeper scans, all failing the PR early.

```yaml
# .github/workflows/shift-left.yml
name: Shift Left                                   # workflow name
on:
  pull_request:                                    # run on PRs
permissions:
  contents: read                                   # read-only
  security-events: write                           # allow uploading scan results
concurrency:
  group: sl-${{ github.event.pull_request.number }}   # one run per PR
  cancel-in-progress: true                         # cancel outdated runs
jobs:
  fast:                                            # cheap checks, give feedback in ~1 minute
    runs-on: ubuntu-latest                         # runner
    timeout-minutes: 10                            # never hang
    steps:
      - uses: actions/checkout@v4                  # code
      - uses: actions/setup-node@v4                # Node
        with:
          node-version: 20                         # version
          cache: npm                               # cache
      - run: npm ci                                # install
      - run: npm run lint --if-present             # lint
      - run: npx tsc --noEmit                      # type check (remove if not using TypeScript)
      - run: npm test -- --coverage                # unit tests with coverage
  secrets:                                         # secret scanning
    runs-on: ubuntu-latest                         # runner
    steps:
      - uses: actions/checkout@v4                  # code
        with:
          fetch-depth: 0                           # full history so old commits are scanned too
      - uses: gitleaks/gitleaks-action@v2          # scan repo for leaked secrets
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}   # needed to comment on PR
  deps-and-image:                                  # dependency + image scan
    needs: fast                                    # only run slower checks if fast ones pass
    runs-on: ubuntu-latest                         # runner
    steps:
      - uses: actions/checkout@v4                  # code
      - name: Build image for scanning             # build locally, do not push
        run: docker build -t app:scan .            # needs a Dockerfile in repo root
      - uses: aquasecurity/trivy-action@0.24.0     # example version; check latest
        with:
          image-ref: app:scan                      # image to scan
          severity: CRITICAL,HIGH                  # report only serious issues
          exit-code: "1"                           # fail the job if found
          ignore-unfixed: true                     # skip issues with no fix available
```

---

## 🟠 My Stack Integration
- **Node.js / React:** ESLint + Prettier, TypeScript strict mode, Jest/Vitest, `npm audit --audit-level=high`.
- **FastAPI:** `ruff`, `mypy`, `pytest`, Pydantic models already validate input at the edge, `pip-audit` for dependencies.
- **Dockerfile:** lint with hadolint; scan with Trivy.
- **Nginx:** test config in CI: `docker run --rm -v "$PWD/nginx":/etc/nginx/conf.d:ro nginx:1.27-alpine nginx -t` (example; needs Docker and may need an upstream host fix, not run here).
- **AWS/Terraform:** `terraform validate`, `tfsec`/`checkov` on PR.

```bash
# Local quick check script - run before pushing (bash)
set -euo pipefail                                # strict mode
npm run lint --if-present                        # style + obvious bugs
npm test                                         # unit tests
npm audit --audit-level=high || true             # show serious dependency issues (do not block locally)
```
Security: shift left is the heart of DevSecOps; secrets, dependency and image scans must run on every PR, not only before release.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting all slow tests on every commit so developers wait 40 minutes.
✅ Correct: Fast checks on PR (under 10 minutes), slow end-to-end tests nightly or before release.

❌ Mistake 2: Scanners that report hundreds of low-value findings.
✅ Correct: Tune severity; fail on critical/high, track the rest.

❌ Mistake 3: Thinking shift left means "no testing on the right".
✅ Correct: Also test in production (monitoring, canary, synthetic checks): "shift left and right".

❌ Mistake 4: Hooks that can be skipped silently.
✅ Correct: Repeat the same checks in CI; local hooks are convenience, CI is the gate.

---

## 🧠 Tricky Interview Question
**"If we shift testing left, do we still need QA engineers?"**

Answer: Yes, but their role changes. Instead of manual testing at the end, QA helps design test strategy, builds automation frameworks, tests risky areas (exploratory testing, performance, accessibility) and coaches developers to write good tests. Developers own unit and integration tests; QA owns quality as a team goal. Shift left removes the late-stage bottleneck, not the quality expertise.

---

## ⚫ Interview Questions + Answers

Q1: What does "shift left" mean?
A1: Doing testing and security checks earlier in the lifecycle, so defects are found when they are cheapest to fix.

Q2: Give examples of shift-left practices.
A2: Linting and type checks in the editor, pre-commit hooks, unit tests in CI, SAST and dependency scanning on PRs, TDD, infrastructure validation before apply.

Q3: What is the test pyramid?
A3: Many fast unit tests at the base, fewer integration tests in the middle, few slow end-to-end tests at the top. It keeps feedback fast.

Q4: What is "shift right"?
A4: Testing and learning in production: canary releases, feature flags, chaos testing, observability. It complements shift left.

Q5: How do you stop secrets from reaching Git?
A5: Pre-commit secret scanning (gitleaks), CI scanning, GitHub push protection, and use secret managers so keys are never in code. If leaked, rotate the key immediately; deleting the commit is not enough.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always for lint, unit tests and secret scanning (cheap and high value).
- Teams with frequent releases and costly production incidents.

❌ Avoid / limit when:
- Heavy checks make PR feedback slow; move them to a later stage.
- No one maintains the tests (flaky tests destroy trust).

---

## 📊 Visual Diagram
```
 Cost to fix a bug grows to the right:

 Editor  -> Pre-commit -> PR (CI) -> Staging -> Production
  $1        $5            $10        $100       $1000+
  ^^^^^^^^^^^^^^^^^^^^^^^^
  SHIFT LEFT: catch bugs here (cheap, fast feedback)
                                                  ^^^^^^^^^^
                                      (shift right: monitor, canary)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Shift left | Test earlier in the lifecycle | Lifecycle में पहले test करना |
| Pre-commit hook | Script run before git commit | Commit से पहले चलने वाली script |
| SAST | Static code security analysis | Code को बिना चलाए security जाँच |
| Linter | Tool finding style/bug patterns | Style/bug patterns ढूँढने वाला tool |
| Test pyramid | Many unit, few E2E tests | कई unit, कम E2E tests |
| Flaky test | Test that passes/fails randomly | कभी pass कभी fail होने वाला test |

---

## ⚡ 3-Line Summary
English: Shift left moves tests and security checks earlier, to the editor, commit and PR stage.
Early bugs are cheap to fix and feedback is fast.
Keep fast checks on every PR and add monitoring on the right side too.

Hindi: Shift left tests और security checks को पहले ले आता है: editor, commit और PR stage।
शुरुआती bugs सस्ते में ठीक होते हैं और feedback तेज़ मिलता है।
हर PR पर तेज़ checks रखें और दाईं तरफ monitoring भी जोड़ें।

---

## ➡️ Next Topic
**10. DevSecOps Basics** — security is the most important thing to shift left.
