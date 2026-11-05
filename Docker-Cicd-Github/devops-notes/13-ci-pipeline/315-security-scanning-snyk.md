# 315. Security Scanning (Snyk)
# हिंदी में: Security Scanning (Snyk)

---

## 🔵 Simple Definition (English)
Snyk is a security platform that scans your dependencies (npm, pip), source code, containers and IaC for known vulnerabilities. In CI, the Snyk CLI or GitHub Action runs on each PR, reports issues with fix advice, and can fail the build above a severity threshold.

## 🔵 सरल परिभाषा (Hindi)
Snyk एक security platform है जो आपकी dependencies (npm, pip), source code, containers और IaC में ज्ञात vulnerabilities ढूँढता है। CI में Snyk CLI या GitHub Action हर PR पर चलकर fix सुझाव के साथ issues बताता है और किसी severity से ऊपर build fail कर सकता है।

---

## 🔴 Problem it Solves
A typical Node.js app has 800+ transitive packages. You wrote none of that code, but a vulnerable `minimist` or `jsonwebtoken` version makes your API exploitable. Nobody reads every advisory. Snyk matches your lockfile against a vulnerability database and tells you which upgrade fixes it.

## 🔴 यह क्यों बना? (Hindi)
एक सामान्य Node.js app में 800+ transitive packages होते हैं। उनमें से कोई code आपने नहीं लिखा, पर कमज़ोर `minimist` या `jsonwebtoken` version आपकी API को exploit योग्य बना देता है। हर advisory कोई नहीं पढ़ता। Snyk आपकी lockfile को vulnerability database से मिलाकर बताता है कि कौन सा upgrade इसे ठीक करेगा।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create free Snyk account, copy API token (Account settings)
Step 2 → Add it as repository secret SNYK_TOKEN
Step 3 → Workflow installs dependencies (lockfile resolves exact versions)
Step 4 → snyk test reads the dependency tree and sends metadata to Snyk
Step 5 → Snyk matches package@version against its vulnerability DB
Step 6 → CLI prints issues (severity, path, fixed-in version)
Step 7 → --severity-threshold=high → exit code 1 if high/critical found
Step 8 → PR check goes red; developer upgrades package or documents ignore
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → मुफ़्त Snyk account बनाएँ, API token copy करें
Step 2 → उसे repository secret SNYK_TOKEN में रखें
Step 3 → Workflow dependencies install करता है (lockfile से सटीक versions)
Step 4 → snyk test dependency tree पढ़कर metadata Snyk को भेजता है
Step 5 → Snyk package@version को vulnerability DB से मिलाता है
Step 6 → CLI issues दिखाता है (severity, path, fixed-in version)
Step 7 → --severity-threshold=high → high/critical मिले तो exit code 1
Step 8 → PR check लाल; developer package upgrade करता है या ignore दर्ज करता है
```

---

## 🟡 Real World Example
Your Node.js API uses `express` -> `body-parser` -> `qs`. A prototype pollution CVE appears in `qs`. Snyk fails the PR with: "High severity: Prototype Pollution in qs, upgrade express to 4.19.2". One dependency bump and the check turns green. Snyk Monitor also emails you later if a new CVE is found in the deployed version.

## 🟡 Real Example Hindi mein
आपकी Node.js API `express` -> `body-parser` -> `qs` इस्तेमाल करती है। `qs` में prototype pollution CVE आती है। Snyk PR fail करता है: "High severity: Prototype Pollution in qs, upgrade express to 4.19.2"। एक dependency bump और check हरा। Snyk Monitor बाद में नई CVE मिलने पर भी email भेजता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/snyk.yml  (basic dependency scan, Node.js)
name: Snyk                             # Workflow name

on: [pull_request]                     # Scan every PR

jobs:
  snyk:
    runs-on: ubuntu-latest             # Runner
    steps:
      - uses: actions/checkout@v4      # Get code
      - uses: actions/setup-node@v4    # Node needed for dependency resolution
        with:
          node-version: 20
      - run: npm ci                    # Install exact lockfile versions
      - uses: snyk/actions/node@master # Official Snyk action (pin to a tag/SHA in production)
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}   # API token secret
        with:
          args: --severity-threshold=high         # Fail only on high or critical
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/snyk.yml  (Node + Python + Docker + code scan, SARIF upload)
name: Snyk Security

on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: "0 3 * * 1"                # Weekly Monday 03:00 UTC: new CVEs appear without code changes

permissions:
  contents: read
  security-events: write               # Needed to upload SARIF to Code Scanning

jobs:
  snyk-node:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    # Fork PRs have no secrets; skip them instead of failing
    if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.full_name == github.repository
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: backend/package-lock.json
      - run: npm ci
        working-directory: backend
      - name: Snyk open source scan
        uses: snyk/actions/node@master
        continue-on-error: true        # Let SARIF upload run even when issues are found
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --file=backend/package.json --severity-threshold=high --sarif-file-output=snyk-node.sarif
      - name: Upload SARIF to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v3
        if: always() && hashFiles('snyk-node.sarif') != ''   # Only if the file exists
        with:
          sarif_file: snyk-node.sarif
          category: snyk-node          # Separate category from CodeQL results
      - name: Fail if high issues remain # Gate after upload
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --file=backend/package.json --severity-threshold=high

  snyk-python:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r api/requirements.txt   # Snyk reads installed env + file
      - uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          command: test
          args: --file=api/requirements.txt --package-manager=pip --severity-threshold=high

  snyk-docker:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapp:ci ./backend    # Build image to scan
      - uses: snyk/actions/docker@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          image: myapp:ci
          args: --file=backend/Dockerfile --severity-threshold=high
```

---

## 🟠 My Stack Integration
- **Node.js:** Scan `package-lock.json`; Snyk shows the dependency path to the vulnerable package and the minimal upgrade.
- **FastAPI:** Pin versions in `requirements.txt` (or use `pip-compile`) so the scan is accurate.
- **React:** Frontend bundles ship to the browser; vulnerable libraries (e.g. old `lodash`) matter. Scan the frontend folder too.
- **Docker/VPS:** Scanning the base image (`node:20-alpine`) finds OS-level CVEs before you `docker compose pull` on the VPS. Pair with Trivy (topic 319).
- **Secrets:** `SNYK_TOKEN` is a secret; do not print it. Use `.snyk` policy file for time-limited ignores with reason and expiry.

```yaml
# .snyk  (policy file at repo root: documented, expiring ignore)
version: v1.25.0                       # Policy schema version
ignore:                                # Section for ignored issues
  SNYK-JS-EXAMPLE-0000000:             # Placeholder issue id (replace with real id)
    - '*':                             # Applies to any path
        reason: "Not reachable: we do not use this API; fix pending upstream"   # Mandatory justification
        expires: 2026-12-31T00:00:00.000Z    # Ignore auto-expires and resurfaces
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `snyk/actions/node@master` unpinned in production, trusting a moving branch.
✅ Correct: Pin to a release tag or commit SHA.

❌ Mistake 2: Scanning before `npm ci`, so the tree is incomplete.
✅ Correct: Install first.

❌ Mistake 3: Ignoring issues permanently with no reason.
✅ Correct: Ignore with `reason` and `expires`.

❌ Mistake 4: `continue-on-error: true` forever, so nothing ever blocks.
✅ Correct: Use it only to allow SARIF upload, then enforce a gate.

❌ Mistake 5: Scanning only on PRs, missing new CVEs in old code.
✅ Correct: Add a weekly `schedule` and `snyk monitor` on main.

---

## 🧠 Tricky Interview Question
Snyk reports a High vulnerability in a dev-only dependency (e.g. a test runner). Should the build fail?

Answer: Usually not the production gate. Dev dependencies are not shipped in the runtime image, so the exploitability in production is low, though CI itself can be an attack surface (supply chain). Scan with `--dev` off (default for production deps) or `--prod`, install production deps in the Docker image with `npm ci --omit=dev`, and treat dev-dependency findings as lower priority tickets. Still upgrade them, because a compromised dev dependency runs in your CI with access to secrets.

---

## ⚫ Interview Questions + Answers

Q1: What does Snyk scan?
A1: Open source dependencies (Snyk Open Source), your own code (Snyk Code, SAST), containers, and IaC (Terraform, Kubernetes, Dockerfile).

Q2: What is a transitive dependency vulnerability?
A2: A flaw in a package your dependency uses. You fix by upgrading the direct parent that pulls a patched version, or via `overrides`/`resolutions`.

Q3: What does `--severity-threshold=high` do?
A3: Only reports/fails for high and critical issues; low and medium are ignored for the exit code.

Q4: Snyk vs `npm audit`?
A4: Both check known CVEs. Snyk has its own curated DB, fix PRs, reachability info, container/IaC/code scanning, and a policy workflow. `npm audit` is built in and free (topic 316).

Q5: How do you handle false positives?
A5: Verify reachability, then add a `.snyk` ignore with reason and expiry, reviewed in PR.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You ship an internet-facing app with many dependencies.
- Compliance asks for evidence of vulnerability scanning.
- You want automated fix PRs.

❌ Avoid when:
- Using it as the only layer; combine with CodeQL, secret scanning, Trivy.
- Private code policy forbids third-party tools (use open-source alternatives).
- Fork PR workflows without secrets (skip, do not fail).

---

## 📊 Visual Diagram
```
 package-lock.json / requirements.txt / Dockerfile
                     │
                     ▼
              snyk test (CLI)
                     │ metadata
                     ▼
        Snyk Vulnerability Database
                     │
         ┌───────────┴────────────┐
         ▼                        ▼
   severity >= high?          below threshold
         │                        │
   exit 1  ❌ PR red          exit 0 ✅ PR green
         │
   SARIF ──▶ GitHub Security tab ──▶ fix PR / upgrade
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CVE | Public ID of a known vulnerability | ज्ञात vulnerability की public ID |
| Transitive dependency | Dependency of a dependency | dependency की dependency |
| Severity | Low / Medium / High / Critical | गंभीरता का स्तर |
| SARIF | Standard format for scan results | scan नतीजों का standard format |
| SAST | Scanning source code for flaws | source code में कमज़ोरी की जाँच |
| Ignore policy | Documented exception for an issue | किसी issue के लिए दर्ज अपवाद |

---

## ⚡ 3-Line Summary
English: Snyk matches your dependency tree and images against a vulnerability database.
English: Set a severity threshold so high issues fail the PR, and upload SARIF for visibility.
English: Pin the action, use secrets safely, schedule weekly scans and expire ignores.
Hindi: Snyk आपके dependency tree और images को vulnerability database से मिलाता है।
Hindi: Severity threshold रखें ताकि high issues PR fail करें, और दिखने के लिए SARIF upload करें।
Hindi: Action pin करें, secrets सुरक्षित रखें, साप्ताहिक scan चलाएँ और ignores की expiry रखें।

Note: not run against Snyk locally; action refs (`@master`), flags and policy-file version are examples to confirm in Snyk docs.

---

## ➡️ Next Topic
316. Dependency Audit (npm audit / pip audit): the free, built-in alternative that needs no external account.
