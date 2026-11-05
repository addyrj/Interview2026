# 316. Dependency Audit (npm audit / pip audit)
# हिंदी में: Dependency Audit (npm audit / pip-audit)

---

## 🔵 Simple Definition (English)
Dependency audit commands compare the exact package versions in your lockfile against public advisory databases. `npm audit` (built into npm) checks the GitHub Advisory Database; `pip-audit` (PyPA tool) checks PyPI advisories/OSV. Both exit non-zero when issues at or above your chosen level are found.

## 🔵 सरल परिभाषा (Hindi)
Dependency audit commands आपकी lockfile के सटीक package versions को public advisory databases से मिलाती हैं। `npm audit` (npm में built-in) GitHub Advisory Database देखता है; `pip-audit` (PyPA का tool) PyPI advisories/OSV देखता है। चुने गए level या उससे ऊपर के issues मिलने पर दोनों non-zero exit देते हैं।

---

## 🔴 Problem it Solves
Libraries get CVEs after you install them. A project that was clean in January can be vulnerable in March without a single code change. You need a free, zero-signup check that runs on every build and also on a schedule.

## 🔴 यह क्यों बना? (Hindi)
Libraries में CVE आपके install करने के बाद आती हैं। जनवरी में साफ़ project मार्च में बिना किसी code बदलाव के vulnerable हो सकता है। आपको मुफ़्त, बिना signup वाली जाँच चाहिए जो हर build पर और schedule पर भी चले।

---

## 🟢 How it Works — Step by Step

```
Step 1 → npm: reads package-lock.json  | pip-audit: reads requirements.txt or env
Step 2 → Sends the package names + versions (not your code) to the advisory API
Step 3 → Advisory DB returns known vulnerabilities and patched ranges
Step 4 → Tool prints a table / JSON with severity and fix suggestion
Step 5 → --audit-level=high (npm) filters what counts as failure
Step 6 → Exit code ≠ 0 when matching issues exist → CI job fails
Step 7 → Fix: npm audit fix / upgrade pin in requirements / add override
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → npm: package-lock.json पढ़ता है  | pip-audit: requirements.txt या env पढ़ता है
Step 2 → Package नाम + versions (आपका code नहीं) advisory API को भेजे जाते हैं
Step 3 → Advisory DB ज्ञात vulnerabilities और patched ranges लौटाता है
Step 4 → Tool severity और fix सुझाव के साथ table / JSON छापता है
Step 5 → --audit-level=high (npm) तय करता है कि failure क्या गिना जाए
Step 6 → मेल खाते issues पर exit code ≠ 0 → CI job fail
Step 7 → Fix: npm audit fix / requirements में pin upgrade / override जोड़ना
```

---

## 🟡 Real World Example
Your FastAPI service pins `cryptography==41.0.0`. A weekly scheduled `pip-audit` run (no code change) fails with "GHSA-... fixed in 42.0.4". The team gets a red scheduled run on Monday morning, bumps the pin, runs tests, and deploys the patch the same day, before any attacker exploits it.

## 🟡 Real Example Hindi mein
आपकी FastAPI service `cryptography==41.0.0` pin करती है। बिना code बदलाव के साप्ताहिक scheduled `pip-audit` run fail होता है: "GHSA-... fixed in 42.0.4"। सोमवार सुबह टीम को लाल scheduled run दिखता है, pin बढ़ाकर tests चलाती है और उसी दिन patch deploy कर देती है, attacker के exploit करने से पहले।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/audit.yml  (basic: npm audit only)
name: Dependency Audit                 # Workflow name

on: [pull_request]                     # Run on PRs

jobs:
  npm-audit:
    runs-on: ubuntu-latest             # Runner
    steps:
      - uses: actions/checkout@v4      # Get code
      - uses: actions/setup-node@v4    # Install Node (npm comes with it)
        with:
          node-version: 20
      - run: npm audit --audit-level=high   # Fail on high or critical only
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/audit.yml  (npm + pip-audit, production deps, JSON artifacts, schedule)
name: Dependency Audit

on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: "30 2 * * 1"               # Mondays 02:30 UTC; catches new CVEs in unchanged code

permissions:
  contents: read

jobs:
  npm-audit:
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
      - name: Audit production dependencies (gate)
        run: npm audit --omit=dev --audit-level=high   # Only runtime deps can fail the build
      - name: Full audit report (informational)
        if: always()                   # Run even if the gate failed
        run: npm audit --json > npm-audit.json || true   # Save JSON; || true keeps step green
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: npm-audit-report
          path: backend/npm-audit.json
          retention-days: 30

  pip-audit:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install pip-audit      # Install the auditing tool
      - name: Audit requirements (gate)
        run: pip-audit -r api/requirements.txt --strict   # --strict: also fail if a package cannot be audited
      - name: JSON report
        if: always()
        run: pip-audit -r api/requirements.txt -f json -o pip-audit.json || true
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: pip-audit-report
          path: pip-audit.json
```

Shell helper for local use (same checks, run before pushing):
```bash
#!/usr/bin/env bash
# scripts/audit.sh : run the same dependency checks locally
set -euo pipefail                      # Stop on error, unset var, pipe failure
cd backend                             # Node API folder
npm audit --omit=dev --audit-level=high    # Production deps, fail on high+
cd ../api                              # FastAPI folder
python -m pip install --quiet pip-audit    # Ensure the tool exists
pip-audit -r requirements.txt          # Audit the pinned requirements
echo "audit OK"                        # Reached only if all passed
```

---

## 🟠 My Stack Integration
- **Node.js:** `--omit=dev` (npm 7+) ignores devDependencies; older npm used `--production`. Fix with `npm audit fix`; use `overrides` in `package.json` for transitive fixes.
- **FastAPI:** `pip-audit -r requirements.txt` resolves in an isolated env; with lockfiles (`pip-compile`) results are exact.
- **React:** Audit the frontend separately; build-time-only packages are less risky but still run in CI.
- **VPS/Docker:** Audit in CI, then also `npm ci --omit=dev` in the Dockerfile so dev tools never reach the VPS image.
- **Dependabot:** Enable `.github/dependabot.yml` so fix PRs open automatically.

```yaml
# .github/dependabot.yml  (automatic update PRs)
version: 2                             # Dependabot config schema version
updates:
  - package-ecosystem: npm             # Node dependencies
    directory: /backend                # Where package.json lives
    schedule:
      interval: weekly                 # Check weekly
    open-pull-requests-limit: 5        # Avoid PR floods
  - package-ecosystem: pip             # Python dependencies
    directory: /api
    schedule:
      interval: weekly
  - package-ecosystem: github-actions  # Keep action versions fresh
    directory: /
    schedule:
      interval: weekly
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running `npm audit fix --force` blindly, which can install breaking major versions.
✅ Correct: Run `npm audit fix`, review the diff, run tests; handle majors manually.

❌ Mistake 2: Failing on every `low` advisory so the team disables the check.
✅ Correct: `--audit-level=high` and track lower ones as tickets.

❌ Mistake 3: Auditing only on PRs.
✅ Correct: Add a weekly `schedule`.

❌ Mistake 4: Unpinned `requirements.txt` (`fastapi>=0.1`), so audit results differ every run.
✅ Correct: Pin exact versions or compile a lock file.

❌ Mistake 5: Treating "0 vulnerabilities" as "secure".
✅ Correct: Audits only know published CVEs; keep other scanners and code review.

---

## 🧠 Tricky Interview Question
`npm audit` reports a vulnerability but `npm audit fix` says "fix available via npm audit fix --force (breaking change)". What do you do?

Answer: Do not force it blindly. Check the dependency path (`npm ls <pkg>`), see if the vulnerable function is reachable, and look for a patched version of the direct parent. Try targeted upgrade of the parent, or add an `overrides` entry in `package.json` to pin the safe transitive version, then run the test suite. If the risk is not exploitable in your usage, document an exception with an expiry date and a ticket. A forced major bump can break the API in production.

---

## ⚫ Interview Questions + Answers

Q1: What does `npm audit` send to the registry?
A1: The dependency tree (names/versions) from the lockfile, not your source code.

Q2: Difference between `npm audit` and `npm audit fix`?
A2: `audit` only reports; `fix` upgrades packages within semver ranges to patched versions and updates the lockfile.

Q3: Why `--omit=dev`?
A3: Production exposure is what matters for the deploy gate; dev tools do not ship in the runtime image.

Q4: How do you audit Python?
A4: `pip install pip-audit`, then `pip-audit -r requirements.txt` (or audit the active environment). Output can be JSON for tooling.

Q5: How does this relate to Dependabot?
A5: Audit detects problems in CI; Dependabot automatically opens PRs that update vulnerable versions. Use both.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want a free, no-account check on every build.
- Lockfiles are committed.
- As a baseline gate before heavier tools.

❌ Avoid when:
- It is your only security control.
- Lockfile is missing (results are unreliable).
- You block on low/moderate dev-only advisories (noise).

---

## 📊 Visual Diagram
```
 package-lock.json ──▶ npm audit ──┐
                                   ├──▶ advisory DB (GitHub / PyPI / OSV)
 requirements.txt ──▶ pip-audit ───┘            │
                                                ▼
                                  vulnerable versions + fixed ranges
                                                │
                     ┌──────────────────────────┴──────────┐
                     ▼                                     ▼
              ≥ high found                           none / low only
              exit 1 ❌ fail                         exit 0 ✅ pass
                     │
              Dependabot PR / manual upgrade → tests → deploy
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Advisory | Published vulnerability notice | प्रकाशित vulnerability सूचना |
| Lockfile | Exact resolved versions file | सटीक versions की file |
| Audit level | Minimum severity that fails | fail कराने वाली न्यूनतम severity |
| Override | Force a transitive version | transitive version थोपना |
| OSV | Open Source Vulnerabilities database | open source vulnerabilities database |
| Dependabot | GitHub bot that opens update PRs | update PR खोलने वाला GitHub bot |

---

## ⚡ 3-Line Summary
English: `npm audit` and `pip-audit` check pinned versions against public advisories for free.
English: Gate on high severity for production deps and also run weekly on a schedule.
English: Fix with careful upgrades or overrides, and let Dependabot open the PRs.
Hindi: `npm audit` और `pip-audit` pinned versions को public advisories से मुफ़्त में जाँचते हैं।
Hindi: Production deps पर high severity का gate रखें और साप्ताहिक schedule भी चलाएँ।
Hindi: सावधानी से upgrade या overrides से fix करें, और PRs Dependabot से खुलवाएँ।

Note: commands and workflows syntax-checked (YAML parse, bash -n) only; not run against live advisory data.

---

## ➡️ Next Topic
317. SAST Scanning (CodeQL): dependencies are checked; now we scan your own source code for security flaws.
