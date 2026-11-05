# 218. Docker Bench Security
# हिंदी में: Docker Bench Security (CIS Audit Tool)

---

## 🔵 Simple Definition (English)
**Docker Bench for Security** is an open-source shell script (from Docker) that checks a Docker host and its containers against the **CIS Docker Benchmark**, a list of security best practices. It prints PASS, WARN, INFO or NOTE for each check: host config, daemon config, images, container runtime, and more.

## 🔵 सरल परिभाषा (Hindi)
**Docker Bench for Security** Docker का open-source shell script है जो Docker host और उसके containers को **CIS Docker Benchmark** (security best practices की list) के against check करता है। यह हर check के लिए PASS, WARN, INFO या NOTE print करता है: host config, daemon config, images, container runtime आदि।

---

## 🔴 Problem it Solves
Hardening has dozens of small rules: audit rules for `/var/lib/docker`, TLS on the Docker socket, `userns-remap`, no `--privileged`, health checks, memory limits. Nobody remembers them all, and a new server or a new teammate easily misses one. Manual review is slow and not repeatable. A scanner gives a repeatable, evidence-based report that you can attach to a security audit and re-run after every change.

## 🔴 यह क्यों बना? (Hindi)
Hardening में दर्जनों छोटे rules होते हैं: `/var/lib/docker` के audit rules, Docker socket पर TLS, `userns-remap`, `--privileged` नहीं, health checks, memory limits। सब किसी को याद नहीं रहते, और नया server या नया teammate आसानी से कुछ भूल जाता है। Manual review धीमा है और repeat नहीं होता। Scanner एक repeatable, सबूत वाली report देता है जो security audit में लगाई जा सकती है और हर बदलाव के बाद दोबारा चलाई जा सकती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Run the script on the Docker host (as root) - directly or inside a container with host mounts.
Step 2 → It reads /etc/docker/daemon.json, systemd units, file permissions, auditd rules.
Step 3 → It calls `docker ps`, `docker inspect`, `docker info` for every container and image.
Step 4 → Each check from the CIS benchmark gets a result:
         [PASS] OK   [WARN] fix this   [INFO] manual review   [NOTE] advisory
Step 5 → It prints a score and writes docker-bench-security.log (+ JSON log).
Step 6 → You fix WARNs (config changes), re-run, and compare scores over time (or in CI).
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Script Docker host पर root से चलाओ - सीधे या host mounts के साथ container में।
Step 2 → यह /etc/docker/daemon.json, systemd units, file permissions, auditd rules पढ़ता है।
Step 3 → हर container और image के लिए `docker ps`, `docker inspect`, `docker info` call करता है।
Step 4 → CIS benchmark के हर check को result मिलता है:
         [PASS] ठीक   [WARN] ठीक करो   [INFO] manual देखो   [NOTE] सलाह
Step 5 → यह score print करता है और docker-bench-security.log (+ JSON log) लिखता है।
Step 6 → आप WARNs fix करते हो, दोबारा चलाते हो, और समय के साथ scores compare करते हो (या CI में)।
```

Sections covered / कौन-से sections:

| Section | Topic |
|---------|-------|
| 1 | Host configuration (audit rules, separate partition) |
| 2 | Docker daemon configuration (TLS, userns, logging) |
| 3 | Daemon config files (permissions on docker.sock) |
| 4 | Container images and build files (USER, HEALTHCHECK) |
| 5 | Container runtime (privileged, caps, limits, read-only) |
| 6 | Operations (security updates, image sprawl) |
| 7 | Swarm configuration |

---

## 🟡 Real World Example
A startup is preparing for a SOC 2 audit. The auditor asks "show evidence that container hosts follow CIS". The DevOps engineer runs Docker Bench on the EC2 host and finds 18 WARNs: no `live-restore`, containers without memory limits, one container running as root, no audit rule for `docker.sock`. After a week of fixing (daemon.json changes, Compose limits, `USER node`) the score goes from 24 to 61 and the PASS report is attached as evidence. The script is then scheduled weekly via cron and the output is sent to Slack.

## 🟡 Real Example Hindi mein
एक startup SOC 2 audit की तैयारी कर रहा है। Auditor पूछता है "दिखाओ कि container hosts CIS follow करते हैं"। DevOps engineer EC2 host पर Docker Bench चलाता है और 18 WARNs मिलते हैं: `live-restore` नहीं, containers पर memory limit नहीं, एक container root से चल रहा, `docker.sock` का audit rule नहीं। एक हफ्ते के fixes (daemon.json बदलाव, Compose limits, `USER node`) के बाद score 24 से 61 हो गया और PASS report सबूत के रूप में लगाई गई। फिर script weekly cron से चलती है और output Slack में जाता है।

---

## 💻 Code / Config Example — Basic

```bash
# Option A: clone and run directly on the host (needs root)
git clone https://github.com/docker/docker-bench-security.git   # official repo
cd docker-bench-security                                         # enter the folder
sudo sh docker-bench-security.sh                                 # run all checks, print results

# Run only specific checks (-c) or exclude some (-e); the check IDs come from the benchmark
sudo sh docker-bench-security.sh -c container_runtime            # only section 5 (container runtime)
sudo sh docker-bench-security.sh -l /tmp/bench.log               # custom log file path
sudo sh docker-bench-security.sh -p                              # print remediation text with each WARN

# Typical output lines:
# [PASS] 5.4  - Ensure that privileged containers are not used
# [WARN] 5.10 - Ensure that the memory usage for containers is limited
# [WARN] 4.1  - Ensure that a user for the container has been created
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# bench-weekly.sh - run Docker Bench weekly, save JSON, alert Slack if WARN count is high
# Cron:  0 3 * * 1 /opt/security/bench-weekly.sh      (Monday 03:00)
set -euo pipefail                                      # stop on errors

WORKDIR=/opt/security/docker-bench-security            # where the repo is cloned
OUTDIR=/var/log/docker-bench                           # report folder
MAX_WARN=25                                            # alert threshold (tune for your baseline)
DATE=$(date +%F)                                       # 2026-11-05 style date for filenames

mkdir -p "$OUTDIR"                                     # make sure report folder exists
cd "$WORKDIR"                                          # script must run from its folder
git pull --ff-only                                     # update to latest checks

sudo sh docker-bench-security.sh -l "$OUTDIR/bench-$DATE.log" >/dev/null 2>&1 || true  # run; ignore exit code

WARNS=$(grep -c '\[WARN\]' "$OUTDIR/bench-$DATE.log.json" 2>/dev/null || grep -c '\[WARN\]' "$OUTDIR/bench-$DATE.log")  # count WARNs
echo "Docker Bench $DATE: $WARNS warnings"             # local log line

if [ "$WARNS" -gt "$MAX_WARN" ]; then                  # too many warnings?
  curl -s -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"Docker Bench: $WARNS WARNs on $(hostname) (limit $MAX_WARN)\"}" \
    "$SLACK_WEBHOOK_URL"                               # notify the team (webhook from env/secret)
fi
```

```yaml
# docker-compose.bench.yml - run Docker Bench as a container (the project's documented approach)
# Usage: docker compose -f docker-compose.bench.yml run --rm bench
services:
  bench:
    image: docker/docker-bench-security     # official image name; pin a digest in real use
    network_mode: host                      # check host network settings
    pid: host                               # see host processes
    userns_mode: host                       # needed to read host namespaces
    cap_add: [AUDIT_CONTROL]                # required to read audit config
    labels:
      - docker_bench_security               # label used by the project
    volumes:
      - /var/lib:/var/lib:ro                # read-only host paths the checks inspect
      - /var/run/docker.sock:/var/run/docker.sock:ro   # Docker API (read-only)
      - /usr/lib/systemd:/usr/lib/systemd:ro           # systemd unit files
      - /etc:/etc:ro                        # host configuration files
```

Not run here (no Docker daemon). The compose file mirrors the project's README `docker run` flags; verify against the current README before use. / इस machine पर Docker daemon नहीं है, इसलिए नहीं चलाया; उपयोग से पहले README से flags मिलाओ।

---

## 🟠 My Stack Integration
Run Docker Bench on your VPS and on every EC2 Docker host after provisioning (Ansible/Terraform user-data). Typical WARNs on a Node.js + FastAPI + Nginx stack: containers without memory limits, root user in Python image, no HEALTHCHECK, no `--read-only`, `docker.sock` mounted into a container (for example in Traefik or Portainer). Fix them in `Dockerfile` and `docker-compose.yml`, then re-run. Keep the report in your repo wiki or an S3 bucket for audits.

```yaml
# .github/workflows/bench.yml - scheduled audit of a self-hosted runner / staging VPS over SSH
name: docker-bench                          # workflow name
on:
  schedule:
    - cron: "0 3 * * 1"                     # every Monday 03:00 UTC
  workflow_dispatch: {}                     # also run manually
jobs:
  bench:
    runs-on: ubuntu-latest                  # GitHub-hosted runner
    steps:
      - name: Run Docker Bench on staging via SSH
        run: |
          # Key comes from repo secrets; write it and lock permissions
          echo "${{ secrets.STAGING_SSH_KEY }}" > key.pem && chmod 600 key.pem
          # Run the script remotely and keep the output as a file
          ssh -i key.pem -o StrictHostKeyChecking=accept-new deploy@${{ secrets.STAGING_HOST }} \
            'cd /opt/security/docker-bench-security && sudo sh docker-bench-security.sh' | tee bench.txt
      - name: Upload report
        uses: actions/upload-artifact@v4    # example version; check latest
        with:
          name: docker-bench-report         # artifact name
          path: bench.txt                   # the saved report
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Treating a 100% score as the goal and breaking apps to get it.
✅ Correct: Review each WARN. Some do not fit your setup; document accepted risks.

❌ Mistake 2: Running it once and forgetting.
✅ Correct: Schedule it (cron/CI) and track the WARN count over time.

❌ Mistake 3: Running the cloned script from an untrusted fork or random URL (`curl | sh`).
✅ Correct: Use the official repo, pin a tag or commit, review the script, since it runs as root.

❌ Mistake 4: Expecting it to scan image vulnerabilities (CVEs).
✅ Correct: Bench checks configuration. Use Trivy/Grype/Docker Scout for CVEs.

---

## 🧠 Tricky Interview Question
**Q:** Docker Bench shows all PASS for section 5, yet a pentester got root on the host through a container. How is that possible?

**Answer:** Docker Bench checks configuration at the time it runs, against a fixed checklist. It does not find vulnerable software (an outdated kernel or runc), application bugs, leaked secrets, or runtime behaviour after the scan. A container could also have been created after the scan with `--privileged`. Bench is a baseline, not a guarantee. Combine it with image scanning, patching, runtime monitoring (Falco) and admission policies.

---

## ⚫ Interview Questions + Answers

Q1: What is the CIS Docker Benchmark?
A1: A consensus document from the Center for Internet Security listing recommended secure settings for the Docker host, daemon, images and containers. Docker Bench automates checking it.

Q2: What do PASS, WARN, INFO, NOTE mean?
A2: PASS: compliant. WARN: not compliant, should fix. INFO: needs manual review. NOTE: advisory only.

Q3: Why is mounting docker.sock into a container flagged?
A3: Whoever controls the socket controls the Docker daemon, which is root on the host. A compromised container with the socket can start a privileged container and take over the host.

Q4: How do you integrate it in CI/CD?
A4: Run on provisioning (Ansible), on a schedule, parse the JSON log, fail or alert if WARN count exceeds a threshold, store the report as an artifact.

Q5: What are alternatives?
A5: Trivy (CVE scan), Dockle (image lint on CIS), Falco (runtime), Lynis (host audit), kube-bench for Kubernetes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Setting up a new Docker host (baseline)
- Preparing for SOC 2, ISO 27001, PCI-DSS audits
- After big config changes or Docker upgrades
- Regular scheduled hygiene checks

❌ Avoid when:
- You expect it to replace CVE scanning or runtime security
- Running on production at peak load without testing (it is light, but run off-peak)
- Using managed Kubernetes/Fargate where you do not own the host (use provider tools)

---

## 📊 Visual Diagram
```
   +-------------------- Docker Host (VPS / EC2) --------------------+
   |  /etc/docker/daemon.json   systemd units   auditd rules         |
   |  docker.sock               containers      images               |
   +---------------------------^-------------------------------------+
                               | reads (root)
                 +-------------+-------------+
                 | docker-bench-security.sh  |
                 +-------------+-------------+
                               v
          [PASS] [WARN] [INFO] [NOTE]  + score + .log / .json
                               v
              Fix config -> re-run -> track trend (cron / CI)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CIS | Center for Internet Security | Security standards संस्था |
| Benchmark | Checklist of secure settings | Secure settings की list |
| WARN | Failed check | Fail हुआ check |
| Baseline | Starting security level | शुरुआती security स्तर |
| Audit evidence | Proof for auditors | Auditors के लिए सबूत |
| docker.sock | Docker daemon API socket | Docker daemon का socket |

---

## ⚡ 3-Line Summary
English: Docker Bench automatically checks your Docker host against the CIS benchmark.
Fix the WARNs, re-run it on a schedule, and keep reports as audit evidence.
It checks configuration only; pair it with CVE scanning and runtime monitoring.

Hindi: Docker Bench आपके Docker host को CIS benchmark के against अपने-आप check करता है।
WARNs fix करो, schedule पर दोबारा चलाओ, और reports को audit सबूत के रूप में रखो।
यह सिर्फ configuration देखता है; CVE scanning और runtime monitoring के साथ use करो।

---

## ➡️ Next Topic
**219. Resource Limits in Production** - one of the most common Bench WARNs is "memory/CPU not limited". Next: how to set CPU, memory and PID limits properly.
