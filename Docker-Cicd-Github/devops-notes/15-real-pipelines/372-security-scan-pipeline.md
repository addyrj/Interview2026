---

# 372. Security Scan Pipeline
# हिंदी में: Security Scan Pipeline

---

## 🔵 Simple Definition (English)
A security scan pipeline automatically checks every change for known-vulnerable dependencies, leaked secrets, insecure code patterns, risky Dockerfiles and vulnerable images. This is often called "shift-left security": find the problem in the pull request, not in production.

## 🔵 सरल परिभाषा (Hindi)
Security scan pipeline हर बदलाव में automatically ज्ञात-vulnerable dependencies, leaked secrets, असुरक्षित code patterns, जोखिम भरी Dockerfiles और vulnerable images जाँचता है। इसे "shift-left security" कहते हैं: समस्या production में नहीं, pull request में पकड़ो।

---

## 🔴 Problem it Solves
- A developer accidentally commits an AWS key; bots find it in minutes.
- Vulnerable dependency versions ship unnoticed.
- Base images carry hundreds of CVEs.
- Security review at the end of the project is too late and too costly.

## 🔴 यह क्यों बना? (Hindi)
- Developer गलती से AWS key commit कर देता है; bots मिनटों में ढूँढ लेते हैं।
- Vulnerable dependency versions बिना ध्यान दिए ship होते हैं।
- Base images में सैकड़ों CVEs होती हैं।
- प्रोजेक्ट के अंत में security review बहुत देर और बहुत महँगी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Secrets scan (gitleaks): fail on any detected credential
Step 2 → Dependency scan (npm audit / pip-audit / Trivy fs)
Step 3 → SAST: CodeQL analyses source for injection, XSS, etc.
Step 4 → Dockerfile/IaC scan (Trivy config or hadolint)
Step 5 → Image scan after build (Trivy image), SARIF uploaded to Security tab
Step 6 → Weekly scheduled full scan to catch newly published CVEs
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Secrets scan (gitleaks): कोई credential मिला तो fail
Step 2 → Dependency scan (npm audit / pip-audit / Trivy fs)
Step 3 → SAST: CodeQL source में injection, XSS आदि खोजता है
Step 4 → Dockerfile/IaC scan (Trivy config या hadolint)
Step 5 → Build के बाद image scan (Trivy image), SARIF Security tab में upload
Step 6 → नई प्रकाशित CVEs पकड़ने के लिए weekly full scan
```

---

## 🟡 Real World Example
A fintech team found an exposed Razorpay test key in a PR through gitleaks and blocked the merge; the key was rotated before merge. A week later Trivy flagged a critical OpenSSL CVE in the `node:20` base layer; rebuilding on the patched tag fixed it in one PR. The scheduled scan also flagged a CVE published after release, with no code change needed.

## 🟡 Real Example Hindi mein
एक fintech team ने gitleaks से PR में खुली Razorpay test key पकड़ी और merge रोका; merge से पहले key rotate हो गई। एक हफ़्ते बाद Trivy ने `node:20` base layer में critical OpenSSL CVE बताई; patched tag पर rebuild से एक PR में ठीक हुई। Scheduled scan ने release के बाद प्रकाशित CVE भी बताई, code बदले बिना।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/security-basic.yml
name: Security basic                   # Name
on: [pull_request]                     # Scan every PR
jobs:
  deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4      # Get code
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci                    # Install
      - run: npm audit --omit=dev --audit-level=high   # Fail on high+ runtime vulns
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/security.yml
name: Security
on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: "0 3 * * 1"                # Weekly rescan for new CVEs
permissions:
  contents: read
  security-events: write               # Upload SARIF to the Security tab
jobs:
  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0               # Full history so old commits are scanned too
      - uses: gitleaks/gitleaks-action@v2   # Secret scanner (example version; check license terms for orgs)
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  codeql:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        language: [javascript-typescript, python]   # Match your React/Nest and FastAPI code
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3          # Prepare analysis
        with:
          languages: ${{ matrix.language }}
      - uses: github/codeql-action/analyze@v3       # Run and upload results
  deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trivy filesystem scan (deps + config)
        uses: aquasecurity/trivy-action@0.28.0       # Example version
        with:
          scan-type: fs
          scanners: vuln,secret,misconfig
          severity: HIGH,CRITICAL
          exit-code: "1"                             # Fail the job on findings
          ignore-unfixed: true                       # Skip CVEs with no fix available
  image:
    needs: [secrets, deps]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t app:scan .              # Build locally, no push
      - uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: app:scan
          format: sarif                              # GitHub-compatible report
          output: trivy.sarif
          severity: HIGH,CRITICAL
          exit-code: "0"                             # Report here; gate in the next step
      - uses: github/codeql-action/upload-sarif@v3   # Show findings in Security tab
        if: always()
        with:
          sarif_file: trivy.sarif
      - uses: aquasecurity/trivy-action@0.28.0       # Gate: fail on CRITICAL only
        with:
          image-ref: app:scan
          severity: CRITICAL
          exit-code: "1"
          ignore-unfixed: true
```

---

## 🟠 My Stack Integration
- Node/NestJS/React: `npm audit --omit=dev`. FastAPI: `pip install pip-audit && pip-audit -r requirements.txt`.
- Dockerfile: run non-root, pin base image tags, no secrets in `ARG`/`ENV`.
- Nginx on VPS: scan its image too, and add headers (`X-Content-Type-Options`, HSTS).
- Add a pre-commit hook locally so secrets are blocked before push:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks   # Local secret scan before commit
    rev: v8.18.4                                 # Example tag, update it
    hooks:
      - id: gitleaks                             # Hook id from the project
```

Findings should become tickets with owners and SLAs, for example critical within 7 days. Tool versions above were not run locally.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deleting a leaked secret from the latest commit only.
✅ Correct: Rotate the secret immediately; Git history keeps it.

❌ Mistake 2: Failing on every low-severity finding, so teams disable scanners.
✅ Correct: Gate on HIGH/CRITICAL with a fix available; track the rest.

❌ Mistake 3: Scanning only on PRs.
✅ Correct: Add scheduled scans since new CVEs appear after release.

❌ Mistake 4: Ignoring base image.
✅ Correct: Use slim/distroless images and rebuild regularly.

Security: scanners need `security-events: write` only where uploading SARIF; keep other permissions read-only.

---

## 🧠 Tricky Interview Question
Trivy reports a critical CVE in a library, but your code never calls the vulnerable function. Do you ignore it?

Answer: Not blindly. Assess reachability and exploitability. If truly unreachable, add a documented, time-limited ignore (`.trivyignore` with reason and expiry, or a VEX statement). Prefer upgrading when a fix exists, because code paths and configurations change.

---

## ⚫ Interview Questions + Answers

Q1: SAST vs DAST vs SCA?
A1: SAST scans source code, DAST attacks a running app, SCA scans third-party dependencies.

Q2: What is SARIF?
A2: A standard JSON format for static analysis results that GitHub renders in the Security tab.

Q3: A secret was committed. Steps?
A3: Revoke and rotate first, then remove from history if needed, then add scanning to prevent repeats.

Q4: Why `ignore-unfixed`?
A4: There is nothing to action yet; it reduces noise while still tracking.

Q5: Where do secrets scanners run best?
A5: Locally (pre-commit) and in CI; server-side push protection on GitHub as a third layer.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always. Start with secrets and dependency scans, then add SAST and image scans.

❌ Avoid when:
- Never skip; only tune thresholds to avoid alert fatigue.

---

## 📊 Visual Diagram
```
 PR / push / weekly cron
        |
  +-----+------+--------+-----------+
  v            v        v           v
gitleaks   CodeQL   Trivy fs     Trivy image
secrets    (SAST)   deps/config  (OS+libs)
  \____________ \_____|___________/
                  |
         fail on HIGH/CRITICAL --> block merge
         SARIF --> GitHub Security tab
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CVE | Public vulnerability ID | सार्वजनिक vulnerability ID |
| SAST | Static code analysis | Static code विश्लेषण |
| SCA | Dependency vulnerability scan | Dependency vulnerability scan |
| SARIF | Scan result format | Scan result का format |
| Shift-left | Check earlier in the process | प्रक्रिया में जल्दी जाँच |

---

## ⚡ 3-Line Summary
English: Scan secrets, dependencies, code and images on every PR plus weekly.
English: Gate on high and critical findings with fixes available.
English: Rotate leaked secrets at once and keep scanners tuned.
Hindi: हर PR और हर हफ़्ते secrets, dependencies, code और images scan करें।
Hindi: Fix उपलब्ध high और critical findings पर gate लगाएँ।
Hindi: Leaked secrets तुरंत rotate करें और scanners tuned रखें।

---

## ➡️ Next Topic
373. Performance Test Pipeline: catch slow endpoints with load tests before users do.
