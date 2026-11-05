# 10. DevSecOps Basics
# हिंदी में: DevSecOps की बुनियादी बातें

---

## 🔵 Simple Definition (English)
**DevSecOps** means building security into every stage of the DevOps pipeline instead of adding it at the end. Developers, operations and security share responsibility, and automated security checks (secret scanning, dependency scanning, SAST, image scanning, policy checks) run on every change.

## 🔵 सरल परिभाषा (Hindi)
**DevSecOps** का मतलब है security को DevOps pipeline के हर stage में बनाना, आखिर में जोड़ना नहीं। Developers, operations और security तीनों की साझा ज़िम्मेदारी होती है, और automated security checks (secret scanning, dependency scanning, SAST, image scanning, policy checks) हर change पर चलते हैं।

---

## 🔴 Problem it Solves
Traditional security was a gate at the end: a security team reviewed the finished product days before launch and found big problems that forced delays or risky exceptions. Meanwhile, teams deploying daily cannot wait for manual reviews. Modern risks (leaked keys in Git, vulnerable npm/pip packages, outdated base images, open S3 buckets) must be caught automatically and early.

## 🔴 यह क्यों बना? (Hindi)
पारंपरिक security आखिर में एक gate थी: security team launch से कुछ दिन पहले तैयार product की जाँच करती और बड़ी problems मिलतीं जिससे देरी या risky exceptions होते। रोज़ deploy करने वाली teams manual review का इंतज़ार नहीं कर सकतीं। आज के जोखिम (Git में leaked keys, vulnerable npm/pip packages, पुराने base images, खुले S3 buckets) अपने आप और जल्दी पकड़े जाने चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 -> Plan    : threat modeling, decide what must be protected
Step 2 -> Code    : secret scanning, secure coding rules, mandatory code review
Step 3 -> Build   : dependency scan (npm audit, pip-audit, Dependabot), SAST (CodeQL)
Step 4 -> Package : Dockerfile lint, image scan (Trivy), non-root user, SBOM
Step 5 -> Release : sign images, restrict who can push to production
Step 6 -> Deploy  : least-privilege IAM, secrets from a manager, no long-lived keys (OIDC)
Step 7 -> Operate : patching, firewall/WAF, TLS everywhere, network isolation
Step 8 -> Monitor : audit logs, alerts on suspicious activity, incident response plan
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 -> Plan    : threat modeling, तय करो क्या बचाना है
Step 2 -> Code    : secret scanning, secure coding नियम, code review अनिवार्य
Step 3 -> Build   : dependency scan (npm audit, pip-audit, Dependabot), SAST (CodeQL)
Step 4 -> Package : Dockerfile lint, image scan (Trivy), non-root user, SBOM
Step 5 -> Release : images पर sign, production पर कौन push करे यह सीमित
Step 6 -> Deploy  : least-privilege IAM, secrets manager से secrets, लंबी उम्र वाली keys नहीं (OIDC)
Step 7 -> Operate : patching, firewall/WAF, हर जगह TLS, network isolation
Step 8 -> Monitor : audit logs, संदिग्ध गतिविधि पर alerts, incident response plan
```

---

## 🟡 Real World Example
**The Log4Shell vulnerability (2021).** Companies with automated dependency inventories (SBOM) and scanners knew within hours which services used the vulnerable Log4j library and patched them. Companies without them spent weeks searching.

**Your stack:** a React app depends on 1,200 npm packages. Dependabot opens a PR when one has a CVE, CI runs tests, and you merge the fix the same day, instead of discovering it after a breach.

## 🟡 Real Example Hindi mein
**Log4Shell vulnerability (2021)।** जिन कंपनियों के पास automated dependency inventory (SBOM) और scanners थे, उन्हें घंटों में पता चल गया कि कौन सी services vulnerable Log4j इस्तेमाल करती हैं और उन्होंने patch कर दिया। बाकी ने हफ्तों खोजा।

**आपका stack:** आपके React app में 1,200 npm packages हैं। किसी में CVE आए तो Dependabot PR खोलता है, CI tests चलाता है और आप उसी दिन fix merge करते हैं, breach के बाद पता चलने की जगह।

---

## 💻 Code / Config Example — Basic
A hardened Dockerfile for a Node.js API (non-root, pinned base, no dev dependencies). Not built locally here.

```dockerfile
# Dockerfile - security-minded Node.js image
# NOTE: in a Dockerfile a comment must be on its own line (a trailing # becomes part of the instruction)
# small base image; pin to a digest in production
FROM node:20-alpine
# production mode: fewer debug features
ENV NODE_ENV=production
# app folder inside the container
WORKDIR /app
# copy dependency files first for layer caching
COPY package*.json ./
# install only production dependencies from lockfile
RUN npm ci --omit=dev
# copy app code (use .dockerignore to skip .env, .git)
COPY . .
# give ownership to the unprivileged "node" user
RUN chown -R node:node /app
# never run as root
USER node
# documentation: app listens on 3000
EXPOSE 3000
# start the app
CMD ["node", "server.js"]
```

## 💻 Code / Config Example — Advanced
A security workflow: CodeQL (SAST), dependency review on PRs, and Trivy image scan.

```yaml
# .github/workflows/security.yml
name: Security                                    # workflow name
on:
  pull_request:                                   # scan every PR
  push:
    branches: [main]                              # and main
  schedule:
    - cron: "0 3 * * 1"                           # weekly scan on Monday 03:00 UTC to catch new CVEs
permissions:
  contents: read                                  # read code
  security-events: write                          # upload results to the Security tab
  pull-requests: read                             # needed by dependency review
jobs:
  codeql:                                         # SAST: static code analysis
    runs-on: ubuntu-latest                        # runner
    steps:
      - uses: actions/checkout@v4                 # code
      - uses: github/codeql-action/init@v3        # set up CodeQL
        with:
          languages: javascript-typescript, python   # languages in your stack
      - uses: github/codeql-action/analyze@v3     # run analysis and upload findings
  dependency-review:                              # block PRs that add vulnerable packages
    if: github.event_name == 'pull_request'       # only valid on PRs
    runs-on: ubuntu-latest                        # runner
    steps:
      - uses: actions/checkout@v4                 # code
      - uses: actions/dependency-review-action@v4 # compare dependencies in the PR
        with:
          fail-on-severity: high                  # fail on high or critical
  image-scan:                                     # scan the container image
    runs-on: ubuntu-latest                        # runner
    steps:
      - uses: actions/checkout@v4                 # code
      - run: docker build -t app:ci .             # build image (needs Dockerfile)
      - uses: aquasecurity/trivy-action@0.24.0    # example version
        with:
          image-ref: app:ci                       # image to scan
          format: table                           # readable output
          severity: CRITICAL,HIGH                 # serious issues only
          exit-code: "1"                          # fail the job when found
          ignore-unfixed: true                    # skip unfixable issues
```

---

## 🟠 My Stack Integration
- **Node.js:** `npm audit`, `helmet` middleware for HTTP headers, rate limiting, validate input with zod/joi.
- **FastAPI:** Pydantic validation, `pip-audit`, OAuth2/JWT with short expiry, CORS limited to your React domain.
- **React:** no secrets in the bundle (everything in `VITE_*`/`REACT_APP_*` is public), Content-Security-Policy header via Nginx.
- **Nginx:** TLS 1.2+/1.3, hide version, security headers, rate limits.
- **VPS:** SSH keys only, root login disabled, UFW firewall, fail2ban, unattended security upgrades.
- **AWS:** least-privilege IAM, no root account use, Secrets Manager, S3 Block Public Access, security groups minimal.

```nginx
# /etc/nginx/conf.d/security-headers.conf - include inside your server {} block (not tested with nginx -t here)
server_tokens off;                                         # hide Nginx version in headers and error pages
add_header X-Content-Type-Options "nosniff" always;        # stop MIME sniffing
add_header X-Frame-Options "DENY" always;                  # block clickjacking in iframes
add_header Referrer-Policy "strict-origin-when-cross-origin" always;   # limit referrer leakage
add_header Strict-Transport-Security "max-age=31536000" always;        # force HTTPS for a year (only after HTTPS works!)
add_header Content-Security-Policy "default-src 'self'" always;        # example; tune for your app or it will break scripts
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting secrets in Dockerfile `ENV`/`ARG` or the repo.
✅ Correct: Inject at runtime from a secret manager; use BuildKit secrets for build-time needs.

❌ Mistake 2: Running containers as root with `latest` base images.
✅ Correct: Non-root user, pinned versions, regular rebuilds for patches.

❌ Mistake 3: Scanner noise ignored because "too many alerts".
✅ Correct: Fail only on high/critical fixable issues, assign an owner, fix regularly.

❌ Mistake 4: A deploy key with admin rights stored forever in GitHub Secrets.
✅ Correct: OIDC with short-lived credentials and a narrowly scoped role.

❌ Mistake 5: Giving a leaked key a "quick delete" and moving on.
✅ Correct: Rotate/revoke immediately; deleting from Git history does not un-leak it.

---

## 🧠 Tricky Interview Question
**"Our pipeline scan found a critical CVE in a base image but no fixed version exists yet. Block the release?"**

Answer: Judge by exploitability, not just score. Check whether the vulnerable component is used or reachable (many CVEs are in unused packages), whether a mitigation exists (network policy, WAF rule, switching to a distroless/alpine image), and the business impact. Document a time-boxed exception with an owner and re-scan date. Blindly blocking all releases stops the business; blindly ignoring is unsafe. Use VEX statements or `.trivyignore` with expiry notes.

---

## ⚫ Interview Questions + Answers

Q1: What is DevSecOps?
A1: Integrating security practices and automated checks throughout the DevOps lifecycle, with shared responsibility.

Q2: SAST vs DAST vs SCA?
A2: SAST scans source code without running it. DAST attacks a running app from outside. SCA (software composition analysis) checks third-party dependencies for known vulnerabilities.

Q3: What is an SBOM?
A3: Software Bill of Materials: a list of all components and versions inside your software, used to quickly find affected services when a new CVE appears.

Q4: How do you manage secrets in CI/CD?
A4: Use secret stores (GitHub Secrets, AWS Secrets Manager, Vault), restrict access per environment, prefer OIDC short-lived credentials, mask in logs, rotate regularly, and never commit them.

Q5: What is the principle of least privilege?
A5: Give every user, service and pipeline only the permissions it needs. A deploy role should not be able to delete the database.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always. Start with secret scanning, dependency scanning and non-root containers (cheap, high value).
- Compliance (SOC2, ISO 27001, PCI) requires evidence of controls.

❌ Avoid when:
- Adding every possible scanner at once: it creates noise and slows teams. Add gradually and tune.

---

## 📊 Visual Diagram
```
 PLAN -> CODE -> BUILD -> TEST -> RELEASE -> DEPLOY -> OPERATE -> MONITOR
  |       |        |       |        |          |          |          |
 threat  secret   SAST    DAST   image sign  least     patching   audit logs
 model   scan     SCA     image   SBOM       privilege WAF, TLS   alerts, IR
                          scan               OIDC
 <========== security at every stage, automated, shared ownership =========>
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DevSecOps | Security built into DevOps | DevOps में बनी security |
| SAST | Scan source code | Source code की स्थिर जाँच |
| DAST | Test running app from outside | चलते app की बाहरी जाँच |
| SCA | Scan third-party dependencies | Third-party dependencies की जाँच |
| CVE | Public ID for a known vulnerability | ज्ञात vulnerability की public ID |
| SBOM | List of components in software | Software के components की सूची |
| Least privilege | Minimum needed permissions | न्यूनतम ज़रूरी अनुमतियाँ |

---

## ⚡ 3-Line Summary
English: DevSecOps puts automated security checks in every pipeline stage.
Scan secrets, dependencies, code and images; run containers as non-root; use least privilege.
Security is everyone's job, not a final gate.

Hindi: DevSecOps हर pipeline stage में automated security checks डालता है।
Secrets, dependencies, code और images scan करें; containers non-root चलाएँ; least privilege रखें।
Security सबकी ज़िम्मेदारी है, आखिरी gate नहीं।

---

## ➡️ Next Topic
**11. Site Reliability Engineering (SRE)** — once secure code runs in production, SRE keeps it reliable with SLOs and error budgets.
