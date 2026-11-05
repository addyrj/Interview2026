# 119. Image Scanning (Trivy)
# हिंदी में: Image Scanning (Trivy से सुरक्षा जाँच)

---

## 🔵 Simple Definition (English)
Image scanning reads every package and library inside a Docker image and compares them with databases of known vulnerabilities (CVEs). Trivy is a free, open source scanner from Aqua Security that does this in seconds, also for config files and secrets.

## 🔵 सरल परिभाषा (Hindi)
Image scanning Docker image के अंदर के हर package और library को known vulnerabilities (CVE) के database से मिलाता है। Trivy, Aqua Security का free और open source scanner है जो यह सेकंडों में करता है, config files और secrets की भी जाँच करता है।

---

## 🔴 Problem it Solves
- Your image contains an OS (Debian/Alpine) plus npm or pip packages. Any of them may have a published security hole.
- Without scanning you find out after an attacker does (e.g. a vulnerable `openssl`, `log4j`, `express` version).
- Manual checking of hundreds of packages is impossible.
- Compliance (SOC2, ISO) asks for proof that images are scanned before release.

## 🔴 यह क्यों बना? (Hindi)
- आपकी image में OS (Debian/Alpine) और npm या pip packages होते हैं। इनमें से किसी में भी published security hole हो सकता है।
- Scan के बिना आपको तब पता चलता है जब attacker पहले ही फायदा उठा ले (जैसे vulnerable `openssl`, `log4j`, `express` version)।
- सैकड़ों packages हाथ से जाँचना नामुमकिन है।
- Compliance (SOC2, ISO) में सबूत माँगा जाता है कि release से पहले images scan हुईं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Trivy downloads/updates its vulnerability DB (NVD, Debian, Alpine, GitHub advisories)
Step 2 → It unpacks the image layers and finds OS packages (dpkg/apk) and app deps (package-lock.json, requirements.txt)
Step 3 → It matches each name+version against the DB
Step 4 → It prints findings with severity: LOW, MEDIUM, HIGH, CRITICAL, and the fixed version if any
Step 5 → --exit-code 1 makes the command FAIL when severity filter matches -> CI pipeline stops
Step 6 → You fix: update base image, bump the dependency, rebuild, scan again
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Trivy अपना vulnerability DB download/update करता है (NVD, Debian, Alpine, GitHub advisories)
Step 2 → वह image की layers खोलकर OS packages (dpkg/apk) और app deps (package-lock.json, requirements.txt) ढूँढता है
Step 3 → हर नाम+version को DB से match करता है
Step 4 → Severity (LOW, MEDIUM, HIGH, CRITICAL) और fixed version (अगर है) के साथ नतीजा दिखाता है
Step 5 → --exit-code 1 से filter match होने पर command FAIL होता है -> CI pipeline रुक जाती है
Step 6 → आप ठीक करते हैं: base image update, dependency bump, rebuild, फिर scan
```

---

## 🟡 Real World Example
A fintech team ships a Node.js image on `node:18`. Trivy in the pull request check reports a CRITICAL CVE in `libssl` and a HIGH one in `jsonwebtoken`. The build fails, the developer moves to `node:20-alpine` and upgrades the package, and the PR turns green. Without the gate, the vulnerable image would have gone to production on the VPS that same evening.

## 🟡 Real Example Hindi mein
एक fintech team `node:18` पर Node.js image भेजती है। Pull request check में Trivy `libssl` में CRITICAL और `jsonwebtoken` में HIGH CVE बताता है। Build fail होता है, developer `node:20-alpine` पर जाता है और package upgrade करता है, PR हरा हो जाता है। Gate न होता तो वही vulnerable image उसी शाम VPS पर production में चली जाती।

---

## 💻 Code / Config Example — Basic
```bash
# Install on macOS with Homebrew (Linux: see Trivy docs for apt/rpm repos)
brew install trivy

# Scan a local or remote image; prints a table of all severities
trivy image node:20-alpine

# Only show serious problems
trivy image --severity HIGH,CRITICAL myorg/api:1.0.0

# Hide vulnerabilities that have no fix yet (less noise, only actionable items)
trivy image --ignore-unfixed --severity HIGH,CRITICAL myorg/api:1.0.0

# Fail (exit code 1) if HIGH or CRITICAL found - use in CI
trivy image --exit-code 1 --severity HIGH,CRITICAL myorg/api:1.0.0

# Scan project files (package-lock.json, requirements.txt) without building an image
trivy fs --scanners vuln,secret .

# Scan Dockerfile/compose/k8s YAML for misconfiguration (root user, no healthcheck...)
trivy config .

# Machine readable output for dashboards
trivy image --format json --output trivy-report.json myorg/api:1.0.0
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/scan.yml  (example versions: check the latest before use)
name: build-and-scan                           # workflow name
on:
  pull_request:                                # scan every pull request
  push:
    branches: [main]                           # and every merge to main
permissions:
  contents: read                               # least privilege for checkout
  security-events: write                       # needed to upload SARIF to the Security tab
jobs:
  scan:
    runs-on: ubuntu-latest                     # GitHub hosted runner with Docker
    steps:
      - uses: actions/checkout@v4              # get the source code
      - name: Build image (not pushed yet)
        run: docker build -t myorg/api:${{ github.sha }} ./api   # tag with commit SHA
      - name: Trivy scan - fail on serious issues
        uses: aquasecurity/trivy-action@0.28.0 # pinned example version
        with:
          image-ref: myorg/api:${{ github.sha }}   # image to scan
          format: table                        # human readable log output
          exit-code: '1'                       # fail the job when findings match
          ignore-unfixed: true                 # skip CVEs without a fix
          severity: CRITICAL,HIGH              # only block on serious ones
      - name: Trivy scan - SARIF for GitHub Security tab
        if: always()                           # run even if previous step failed
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: myorg/api:${{ github.sha }}
          format: sarif                        # GitHub code scanning format
          output: trivy-results.sarif          # report file name
      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3   # publishes findings in the repo Security tab
        with:
          sarif_file: trivy-results.sarif      # file produced above
```

```yaml
# trivy.yaml - optional config file (check key names against your Trivy version)
severity:                                      # severities to report
  - HIGH
  - CRITICAL
ignore-unfixed: true                           # skip unfixable CVEs
```

```text
# .trivyignore - accepted risks, one CVE per line. ALWAYS add a comment and a review date
# CVE-2024-00000  accepted: not reachable, no network input, review 2026-12-01
```

---

## 🟠 My Stack Integration
- **Node.js:** Trivy reads `package-lock.json` inside the image; fix with `npm audit fix` or upgrading the package.
- **FastAPI:** reads `requirements.txt` / `poetry.lock`; python base images (`python:3.12-slim`) get regular fixes, so rebuild often.
- **React:** the final Nginx image has no node_modules, so scanning it is quick and low noise. Scan the builder stage only if you ship it.
- **VPS / AWS:** scan in CI before pushing to GHCR or ECR; ECR can also scan on push (basic or enhanced with Inspector).

```yaml
# docker-compose.yml fragment: run Trivy on demand on the VPS without installing it
services:
  trivy:                                       # one-off scanner, not a long-running app
    image: aquasec/trivy:0.57.0                # example pinned tag
    profiles: ["tools"]                        # starts only with --profile tools
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro   # read access to local images
      - trivy-cache:/root/.cache/             # keep DB between runs
    command: image --severity HIGH,CRITICAL myorg/api:latest   # what to scan
volumes:
  trivy-cache:                                 # named volume for the DB cache
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Scanning once at release and never again.
✅ Correct: New CVEs appear daily. Rescan on a schedule (nightly workflow) as well as on each build.

❌ Mistake 2: Blocking on every LOW/MEDIUM finding, so the team ignores the tool.
✅ Correct: Gate on HIGH,CRITICAL with `--ignore-unfixed`, track the rest as tickets.

❌ Mistake 3: Using `.trivyignore` to silence everything without notes.
✅ Correct: Each ignore needs a reason and expiry date.

❌ Mistake 4: Mounting the Docker socket read-write into a scanner container.
✅ Correct: Mount `:ro` or scan an exported tar: `docker save -o img.tar` then `trivy image --input img.tar`.

---

## 🧠 Tricky Interview Question
Trivy shows 0 vulnerabilities today for your image but a pen tester finds a known CVE a week later, with no code change. How?

Answer: Scan results depend on the vulnerability DB at the scan time. A CVE published after your scan was not known then. Also an old DB cache (offline runner) or `--ignore-unfixed` can hide issues. Therefore rescan stored images on a schedule, update DB, and rebuild images regularly. Trivy also cannot detect zero-days or logic bugs in your own code.

---

## ⚫ Interview Questions + Answers

Q1: What does Trivy scan?
A1: Container images, filesystems, git repos, IaC/Dockerfile misconfigs, secrets, licenses and SBOMs.

Q2: How do you make the pipeline fail on critical issues?
A2: `--exit-code 1 --severity CRITICAL,HIGH`. The default exit code is 0 even when issues exist.

Q3: Why `--ignore-unfixed`?
A3: It hides CVEs with no available patch so the team only handles actionable items.

Q4: Trivy vs Docker Scout vs ECR scanning?
A4: All compare packages with CVE data. Trivy is open source and works anywhere; Scout is integrated with Docker Hub/Desktop; ECR scans in the registry. Many teams use Trivy in CI plus registry scanning.

Q5: What is the best way to reduce findings?
A5: Smaller base images (alpine, slim, distroless), multi-stage builds, and updating dependencies.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every CI build before push.
- Nightly rescans of images running in production.
- Checking Dockerfile and Kubernetes manifests for misconfigurations.

❌ Avoid when:
- Treating it as the only security control; it misses runtime attacks and logic bugs.
- Blocking deploys on unfixable LOW findings.

---

## 📊 Visual Diagram
```
  Dockerfile --> docker build --> image
                                    |
                                    v
                             +-------------+      +------------------+
                             |   Trivy     | <--- | Vulnerability DB |
                             +-------------+      +------------------+
                                    |
                 +------------------+-----------------+
                 | no HIGH/CRITICAL                   | found
                 v                                    v
           docker push (GHCR/ECR)              exit 1 -> pipeline FAIL
                 |                                    |
                 v                                    v
            deploy to VPS                    fix base image / deps
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CVE | Public ID of a known vulnerability | ज्ञात कमजोरी की public ID |
| Severity | LOW / MEDIUM / HIGH / CRITICAL | गंभीरता स्तर |
| SARIF | Standard report format for code scanning | scan report का standard format |
| Unfixed | CVE without a patch yet | जिसका patch अभी नहीं है |
| Exit code | Number returned; non-zero fails CI | command का return number |
| Misconfiguration | Risky setting in Dockerfile/YAML | जोखिम भरी गलत setting |

---

## ⚡ 3-Line Summary
English: Trivy compares everything inside an image with known CVE databases.
English: Use `--exit-code 1 --severity HIGH,CRITICAL` to block bad builds in CI.
English: Rescan regularly because new CVEs appear after you ship.
Hindi: Trivy image के अंदर की हर चीज़ को known CVE databases से मिलाता है।
Hindi: CI में खराब build रोकने के लिए `--exit-code 1 --severity HIGH,CRITICAL` लगाएँ।
Hindi: बार-बार दोबारा scan करें क्योंकि ship करने के बाद भी नए CVE आते हैं।

---

## ➡️ Next Topic
**120. Docker Scout** — Docker's own built-in analysis tool with recommendations and policy checks, a good comparison to Trivy.
