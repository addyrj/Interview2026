# 319. Docker Image Scan (Trivy)
# हिंदी में: Docker Image Scan (Trivy)

---

## 🔵 Simple Definition (English)
Trivy is a free, open-source scanner from Aqua Security. It scans container images (OS packages and app libraries), filesystems, IaC and secrets for known vulnerabilities and misconfigurations. In CI you run it right after the image is built, and fail the pipeline if it finds issues above a severity.

## 🔵 सरल परिभाषा (Hindi)
Trivy Aqua Security का मुफ़्त, open-source scanner है। यह container images (OS packages और app libraries), filesystems, IaC और secrets में ज्ञात vulnerabilities और misconfigurations ढूँढता है। CI में इसे image बनने के तुरंत बाद चलाते हैं और किसी severity से ऊपर issues मिलें तो pipeline fail करा देते हैं।

---

## 🔴 Problem it Solves
Your app code can be perfect, yet the base image `node:20` ships Debian packages (openssl, glibc, zlib) that carry CVEs. Dependency scanners (npm audit) do not see OS packages. Trivy opens every image layer and checks both the OS package database and language lockfiles, so you catch vulnerable images before they reach your VPS or ECS.

## 🔴 यह क्यों बना? (Hindi)
आपका app code बिल्कुल सही हो सकता है, फिर भी base image `node:20` में Debian packages (openssl, glibc, zlib) होते हैं जिनमें CVEs हो सकती हैं। Dependency scanners (npm audit) OS packages नहीं देखते। Trivy image की हर layer खोलकर OS package database और language lockfiles दोनों जाँचता है, ताकि vulnerable images VPS या ECS तक पहुँचने से पहले पकड़ी जाएँ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → CI builds the image (topic 318) and keeps it locally (load: true)
Step 2 → Trivy downloads/updates its vulnerability DB (cached between runs)
Step 3 → It unpacks image layers and detects OS (alpine/debian) + packages
Step 4 → It also reads lockfiles inside the image (package-lock, requirements)
Step 5 → Each package@version is matched against the DB (NVD, vendor advisories)
Step 6 → Filters apply: --severity HIGH,CRITICAL, --ignore-unfixed
Step 7 → Report written (table, JSON, or SARIF for the Security tab)
Step 8 → --exit-code 1 makes the step fail when findings remain
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → CI image बनाता है (topic 318) और उसे local रखता है (load: true)
Step 2 → Trivy अपना vulnerability DB download/update करता है (runs के बीच cache)
Step 3 → वह image layers खोलकर OS (alpine/debian) और packages पहचानता है
Step 4 → image के अंदर lockfiles (package-lock, requirements) भी पढ़ता है
Step 5 → हर package@version को DB (NVD, vendor advisories) से मिलाया जाता है
Step 6 → Filters लगते हैं: --severity HIGH,CRITICAL, --ignore-unfixed
Step 7 → Report लिखी जाती है (table, JSON, या Security tab के लिए SARIF)
Step 8 → --exit-code 1 से findings बचे हों तो step fail होता है
```

---

## 🟡 Real World Example
Your FastAPI image is based on `python:3.9-slim` built months ago. Trivy reports CRITICAL `CVE-XXXX` in `libexpat1` with a fixed version available. The pipeline stops before the push. You rebuild on `python:3.12-slim`, the report is clean, and the image reaches the VPS. Without Trivy, that vulnerable library would have run in production silently.

## 🟡 Real Example Hindi mein
आपकी FastAPI image कई महीने पहले बनी `python:3.9-slim` पर आधारित है। Trivy `libexpat1` में CRITICAL `CVE-XXXX` बताता है जिसका fixed version मौजूद है। Pipeline push से पहले रुक जाती है। आप `python:3.12-slim` पर rebuild करते हैं, report साफ़ आती है और image VPS पर पहुँचती है। Trivy के बिना वह vulnerable library production में चुपचाप चलती रहती।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/trivy.yml  (basic: build then scan)
name: Trivy Scan                       # Workflow name

on: [pull_request]                     # Scan on PRs

jobs:
  scan:
    runs-on: ubuntu-latest             # Runner
    steps:
      - uses: actions/checkout@v4      # Get code
      - run: docker build -t myapi:ci ./backend    # Build the image locally
      - uses: aquasecurity/trivy-action@0.28.0     # Example tag; pin to latest release or SHA
        with:
          image-ref: myapi:ci          # Which image to scan
          severity: HIGH,CRITICAL      # Only these severities count
          exit-code: "1"               # Fail the step if any are found
          ignore-unfixed: true         # Skip CVEs that have no fix yet
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/image-scan.yml  (Buildx build, Trivy table gate + SARIF, secret/config scan)
name: Image Build and Scan

on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: "0 5 * * *"                # Daily: new CVEs appear for images that already shipped

permissions:
  contents: read
  security-events: write               # Upload SARIF results

jobs:
  scan:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Build image into local daemon
        uses: docker/build-push-action@v6
        with:
          context: ./backend
          load: true                   # Needed so Trivy sees the image
          push: false                  # Never push before the scan passes
          tags: myapi:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - name: Trivy SARIF report (never fails the step)
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: myapi:${{ github.sha }}
          format: sarif                # Machine-readable for GitHub Code Scanning
          output: trivy-results.sarif
          severity: CRITICAL,HIGH
          ignore-unfixed: true
          vuln-type: os,library        # OS packages and app libraries
          exit-code: "0"               # Report only; the gate is the next step
      - name: Upload SARIF to Security tab
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy-results.sarif
          category: trivy-image
      - name: Trivy gate (fails on CRITICAL)
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: myapi:${{ github.sha }}
          format: table                # Human-readable in the log
          severity: CRITICAL
          ignore-unfixed: true
          exit-code: "1"               # Block merge/push on critical findings
      - name: Scan repo for secrets and misconfig (Dockerfile, IaC)
        uses: aquasecurity/trivy-action@0.28.0
        with:
          scan-type: fs                # Filesystem mode on the checkout
          scan-ref: .
          scanners: secret,misconfig   # Hard-coded keys and bad Dockerfile settings
          severity: HIGH,CRITICAL
          exit-code: "1"
```

A `.trivyignore` file for reviewed exceptions (repo root):
```bash
# .trivyignore : one CVE id per line, with a comment and a review date
# Reviewed 2026-11-01, not reachable in our runtime, fix pending upstream. Re-check 2026-12-01.
CVE-2099-00000
```

---

## 🟠 My Stack Integration
- **Node.js image:** Prefer `node:20-alpine` or distroless to reduce OS packages; rebuild regularly to pick up patched bases.
- **FastAPI image:** `python:3.12-slim`; pin versions and rebuild weekly so Trivy stays green.
- **React + Nginx image:** Scan the final `nginx:alpine` stage; build stage packages are discarded in multi-stage builds.
- **VPS:** Scan in CI before pushing to GHCR; a nightly scheduled scan of the `:latest` pushed image tells you when a running container turns vulnerable.
- **AWS:** ECR has built-in scanning (basic/enhanced). Trivy in CI shifts the check left, before the push.
- **Security:** Run as non-root, no secrets in layers. Trivy `secret` scanner catches keys accidentally copied into the image.

```bash
# Run Trivy locally against any image (no CI), exact same checks
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 myapi:ci   # Fails with code 1 if found
trivy image --format json --output trivy.json myapi:ci                         # JSON report for tooling
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Scanning an image that was not built or loaded (`image-ref` not found).
✅ Correct: Use `load: true` or build with `docker build` first.

❌ Mistake 2: Failing on LOW/MEDIUM and unfixed CVEs, so the team ignores red builds.
✅ Correct: `HIGH,CRITICAL` plus `ignore-unfixed`; track the rest separately.

❌ Mistake 3: Scanning only at build time.
✅ Correct: Add a daily schedule; new CVEs hit old images.

❌ Mistake 4: Permanent `.trivyignore` entries with no comment.
✅ Correct: Reason, owner and review date for each.

❌ Mistake 5: Unpinned `trivy-action@master`.
✅ Correct: Pin to a release tag or full commit SHA, since the action runs with your repo permissions.

---

## 🧠 Tricky Interview Question
Trivy fails your build with a CRITICAL CVE in the base image, but no patched version exists. What do you do?

Answer: First verify exploitability and whether the vulnerable component is used. Options: switch to a different or smaller base (alpine, distroless, `-slim`) that does not include the package, remove the package in the Dockerfile, wait for upstream, or add a time-limited `.trivyignore` entry with a documented justification and ticket. Using `--ignore-unfixed` hides it from the gate but the risk still exists, so keep it visible in the SARIF report and re-scan daily.

---

## ⚫ Interview Questions + Answers

Q1: Trivy vs Snyk?
A1: Trivy is open-source and CLI-first, covering images, filesystems, IaC and secrets for free. Snyk is a commercial platform with its own DB, fix PRs and dashboards. Many teams use Trivy in CI and Snyk or ECR for management.

Q2: Why does a small base image matter?
A2: Fewer packages mean fewer CVEs, smaller attack surface, faster pulls.

Q3: What does `--ignore-unfixed` do?
A3: Hides vulnerabilities with no available fix, so the gate only fails on things you can actually act on.

Q4: How can the scan itself be fast?
A4: Cache the Trivy DB (`actions/cache`, or the action's built-in caching), scan after the build in the same job, avoid scanning huge unused layers.

Q5: Scan before or after pushing?
A5: Before. Push only if the gate passes, so vulnerable images never enter the registry the VPS pulls from.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You build any container image for VPS, ECS, Kubernetes.
- You want free, fast, CI-friendly scanning.
- You need a daily re-scan of deployed images.

❌ Avoid when:
- Gating on every low severity (noise).
- You do not rebuild images regularly; findings never get fixed.
- Treating it as proof of security (it only knows published CVEs).

---

## 📊 Visual Diagram
```
 Dockerfile ──build──▶ image myapi:sha (local)
                           │
                    Trivy (DB cached)
        ┌──────────────────┼───────────────────┐
        ▼                  ▼                   ▼
   OS packages       app libraries      secrets / misconfig
 (alpine/debian)   (npm, pip lockfiles)  (keys in layers)
        └──────────────────┬───────────────────┘
                           ▼
              severity filter + ignore-unfixed
                  ┌────────┴─────────┐
               findings           clean
                  ▼                  ▼
          exit 1 ❌ no push    ✅ push to GHCR → VPS pulls
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trivy | Open-source vulnerability scanner | open-source vulnerability scanner |
| CVE | Public ID of a known flaw | ज्ञात कमज़ोरी की public ID |
| Base image | Image your Dockerfile starts FROM | जिस image से Dockerfile शुरू होती है |
| Distroless | Image with only app + runtime | सिर्फ़ app + runtime वाली image |
| SARIF | Standard scan result format | scan नतीजों का standard format |
| Shift left | Check earlier in the pipeline | जाँच को pipeline में पहले करना |

---

## ⚡ 3-Line Summary
English: Trivy scans image layers for OS and library CVEs, secrets and misconfigurations.
English: Build into the local daemon, scan, fail on HIGH/CRITICAL, and push only if clean.
English: Pin the action, ignore with reasons, and re-scan daily for new CVEs.
Hindi: Trivy image layers में OS और library CVEs, secrets और misconfigurations ढूँढता है।
Hindi: Local daemon में build करें, scan करें, HIGH/CRITICAL पर fail करें, साफ़ हो तभी push करें।
Hindi: Action pin करें, कारण के साथ ignore करें, और नई CVEs के लिए रोज़ दोबारा scan करें।

Note: Trivy and the images were NOT run locally (no Docker daemon); action tag 0.28.0 and input names are examples to verify against the current trivy-action README.

---

## ➡️ Next Topic
320. PR Comments with Results: surface test, coverage and scan results directly inside the pull request conversation.
