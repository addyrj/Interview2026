---

# 211. Production Docker Checklist
# हिंदी में: Production Docker Checklist

---

## 🔵 Simple Definition (English)
A **production Docker checklist** is a list of checks you run before shipping containers to real users: small pinned images, non-root user, no secrets in images, healthchecks, resource limits, logging, restart policy, scanning, and backups. It turns "it runs" into "it is safe to run".

## 🔵 सरल परिभाषा (Hindi)
**Production Docker checklist** उन checks की list है जो containers को असली users तक भेजने से पहले चलाते हैं: छोटी pinned images, non-root user, images में secrets नहीं, healthchecks, resource limits, logging, restart policy, scanning और backups। यह "चल रहा है" को "चलाना सुरक्षित है" में बदलता है।

---

## 🔴 Problem it Solves
Dev containers are forgiving: root user, `latest` tag, 1 GB images, no limits, secrets in env, logs filling the disk. In production these become incidents: a memory leak kills the VPS, a leaked `.env` baked in an image gets pulled from a public registry, an unpatched base image gets exploited, a disk full of JSON logs crashes Docker. The checklist prevents the repeat incidents.

## 🔴 यह क्यों बना? (Hindi)
Dev containers बहुत माफ़ करने वाले होते हैं: root user, `latest` tag, 1 GB images, कोई limit नहीं, env में secrets, logs से disk भरना। Production में ये incidents बन जाते हैं: memory leak पूरा VPS गिरा देता है, image में baked `.env` public registry से pull हो जाती है, unpatched base image exploit होती है, JSON logs से disk full होकर Docker crash। Checklist इन दोहराई जाने वाली गलतियों को रोकती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → BUILD   : multi-stage, pinned base, .dockerignore, no secrets, small image
Step 2 → SECURE  : non-root, read-only fs, drop caps, scan image (Trivy), sign/pin digest
Step 3 → RUN     : restart policy, healthcheck, CPU/RAM/PID limits, log rotation
Step 4 → CONFIG  : env/secrets from outside the image, 12-factor
Step 5 → OBSERVE : logs to stdout, metrics, alerts on restarts and OOM
Step 6 → DEPLOY  : immutable tags (git SHA), rollback plan, graceful shutdown
Step 7 → RECOVER : volume backups tested, host patched, registry access controlled
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → BUILD   : multi-stage, pinned base, .dockerignore, secrets नहीं, छोटी image
Step 2 → SECURE  : non-root, read-only fs, caps drop, image scan (Trivy), digest pin
Step 3 → RUN     : restart policy, healthcheck, CPU/RAM/PID limits, log rotation
Step 4 → CONFIG  : env/secrets image के बाहर से, 12-factor
Step 5 → OBSERVE : logs stdout पर, metrics, restarts और OOM पर alerts
Step 6 → DEPLOY  : immutable tags (git SHA), rollback plan, graceful shutdown
Step 7 → RECOVER : volume backups की testing, host patched, registry access controlled
```

---

## 🟡 Real World Example
A food-delivery startup deploys its FastAPI order service on one AWS EC2 box. Before launch the DevOps engineer walks the checklist: image tagged `orders-api:3f9c2ab` (git SHA), runs as UID 10001, memory limit 512 MB, log rotation 10 MB x 3, Trivy scan in GitHub Actions blocks CRITICAL CVEs, and a rollback script re-deploys the previous SHA. Two weeks later a memory leak triggers: only that container is OOM-killed and restarted, the DB and Nginx stay alive.

## 🟡 Real Example Hindi mein
एक food-delivery startup अपनी FastAPI order service एक AWS EC2 पर deploy करता है। Launch से पहले DevOps engineer checklist पर चलता है: image `orders-api:3f9c2ab` (git SHA) tag, UID 10001 पर run, memory limit 512 MB, log rotation 10 MB x 3, GitHub Actions में Trivy scan CRITICAL CVE पर block करता है, और rollback script पिछला SHA फिर deploy करती है। दो हफ्ते बाद memory leak आता है: सिर्फ वही container OOM-kill होकर restart होता है, DB और Nginx चलते रहते हैं।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile (BASIC production-minded Node.js image)
FROM node:20-alpine
# pinned major version, small alpine base (example tag, update regularly)
WORKDIR /app
# fixed working directory
COPY package*.json ./
# manifests first for build cache
RUN npm ci --omit=dev
# exact versions, production deps only
COPY . .
# copy source (.dockerignore must exclude .env, .git, node_modules)
USER node
# run as the built-in non-root user
EXPOSE 3000
# documentation of the listening port
HEALTHCHECK --interval=30s --timeout=3s CMD node -e "fetch('http://localhost:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
# container reports health to Docker
CMD ["node", "server.js"]
# exec form so Node receives SIGTERM directly
```

```text
# .dockerignore
node_modules
.git
.env
*.log
Dockerfile
docker-compose*.yml
```

The checklist as a bash script you can run in CI:
```bash
#!/usr/bin/env bash
# checklist.sh <image>  -> quick automated checks
set -euo pipefail                                   # stop on any error
IMG="$1"                                            # image name passed as argument

echo "[1] user is not root?"                        # check 1
USER_ID=$(docker run --rm --entrypoint id "$IMG" -u)   # print UID inside the image
[ "$USER_ID" != "0" ] && echo "OK uid=$USER_ID" || { echo "FAIL runs as root"; exit 1; }

echo "[2] image size (MB)?"                         # check 2
docker image inspect "$IMG" --format '{{.Size}}' | awk '{printf "%.0f MB\n", $1/1048576}'

echo "[3] healthcheck defined?"                     # check 3
docker image inspect "$IMG" --format '{{if .Config.Healthcheck}}OK{{else}}MISSING{{end}}'

echo "[4] tag is not latest?"                       # check 4
case "$IMG" in *:latest|*[!:]) echo "WARN use a version/sha tag";; *) echo "OK";; esac
```

---

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.prod.yml  (checklist applied)
services:
  api:
    image: registry.example.com/orders-api:3f9c2ab   # immutable git-SHA tag, never latest
    pull_policy: always                              # fetch the exact tag on deploy
    restart: unless-stopped                          # survive crashes and reboots
    user: "10001:10001"                              # non-root UID:GID
    read_only: true                                  # read-only root filesystem
    tmpfs:
      - /tmp:size=64m,noexec,nosuid                  # small RAM scratch space, no exec
    cap_drop: [ALL]                                  # remove all Linux capabilities
    security_opt:
      - no-new-privileges:true                       # block setuid escalation
    environment:
      NODE_ENV: production                           # production mode
    env_file:
      - /etc/orders/api.env                          # secrets live on host, not in image
    healthcheck:
      test: ["CMD", "node", "healthcheck.js"]        # app-specific probe
      interval: 30s                                  # every 30 seconds
      timeout: 3s                                    # fail after 3s
      retries: 3                                     # 3 failures -> unhealthy
      start_period: 20s                              # boot grace
    deploy:
      resources:
        limits:
          cpus: "1.0"                                # at most 1 CPU
          memory: 512m                               # OOM-kill above 512 MB
    pids_limit: 200                                  # stop fork bombs
    stop_grace_period: 30s                           # time for graceful shutdown
    logging:
      driver: json-file                              # default driver, but with rotation
      options:
        max-size: "10m"                              # rotate at 10 MB
        max-file: "3"                                # keep 3 files
    ports:
      - "127.0.0.1:3000:3000"                        # only host Nginx can reach it
```

Pre-deploy pipeline snippet (GitHub Actions):
```yaml
# .github/workflows/docker-checks.yml
name: docker-checks                      # workflow name
on: [pull_request]                       # run on every PR
jobs:
  scan:
    runs-on: ubuntu-latest               # GitHub hosted runner
    steps:
      - uses: actions/checkout@v4        # fetch code (example version)
      - name: Build image                # build without pushing
        run: docker build -t orders-api:ci .
      - name: Trivy scan                 # vulnerability scan
        uses: aquasecurity/trivy-action@0.28.0   # example version, pin and update
        with:
          image-ref: orders-api:ci       # image to scan
          severity: CRITICAL,HIGH        # only these levels
          exit-code: "1"                 # fail the job if found
          ignore-unfixed: true           # skip CVEs with no fix yet
```

Verification note: YAML/bash syntax checked only; images were not built or scanned locally. The `[!:]` glob in the bash tag check is a simple heuristic.

---

## 🟠 My Stack Integration
- **Node.js/FastAPI**: non-root user, `CMD` in exec form, `/health` endpoint, `NODE_ENV=production`, `uvicorn --workers` sized to the memory limit.
- **React**: multi-stage build, ship only static files in Nginx image; no source maps with secrets.
- **Nginx on VPS**: host Nginx terminates TLS, containers bind to `127.0.0.1`.
- **AWS**: images in ECR with scan-on-push, IAM role on EC2 (no access keys in env), CloudWatch logs via `awslogs` driver, SSM Parameter Store for secrets.

```yaml
# AWS logging driver for the service (instead of json-file)
    logging:
      driver: awslogs                       # ship logs to CloudWatch
      options:
        awslogs-region: ap-south-1          # AWS region
        awslogs-group: /orders/api          # log group
        awslogs-create-group: "true"        # create group if missing
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `FROM node:latest` and `image: app:latest`.
✅ Correct: Pin versions and deploy immutable tags (git SHA); `latest` makes rollbacks impossible.

❌ Mistake 2: `COPY . .` without `.dockerignore`, baking `.env` and `.git` into the image.
✅ Correct: Add `.dockerignore`, pass secrets at runtime, and rotate any secret that ever entered an image.

❌ Mistake 3: No log rotation on `json-file`.
✅ Correct: Set `max-size` and `max-file` (or daemon-wide in `/etc/docker/daemon.json`).

❌ Mistake 4: No memory limit, so one leak OOM-kills random host processes.
✅ Correct: Set `mem_limit`/`deploy.resources.limits`, and alert on restarts.

❌ Mistake 5: Mounting `/var/run/docker.sock` into app containers.
✅ Correct: Never, unless it is an audited tool; socket access equals root on the host.

---

## 🧠 Tricky Interview Question
**Q:** Your image is scanned clean and runs as non-root, yet the host got compromised through the container. Name three things the checklist may have missed.

**Answer:** (1) The container was started with `--privileged` or the Docker socket mounted, so root-equivalent access existed anyway. (2) A writable bind mount of a host directory such as `/etc` or `~/.ssh`. (3) Kernel-level escape because the host kernel was unpatched (containers share the host kernel), or capabilities like `SYS_ADMIN` were added. A clean image scan only covers packages inside the image, not how it is run.

---

## ⚫ Interview Questions + Answers

**Q1: Why pin image tags and even digests?**
A1: Tags are mutable; `node:20` changes over time. A digest (`image@sha256:...`) is immutable, guaranteeing the exact bytes, which helps reproducibility and supply-chain security. Trade-off: you must update deliberately (Dependabot/Renovate).

**Q2: What are restart policies and which do you use?**
A2: `no`, `on-failure[:N]`, `always`, `unless-stopped`. For servers use `unless-stopped` (restarts after reboot/crash, but respects a manual `docker stop`).

**Q3: Where should secrets live?**
A3: Not in the Dockerfile, image layers or git. Use runtime injection: Docker/Compose secrets (files), env from a secret manager (AWS Secrets Manager/SSM), or orchestrator secrets. Remember env vars are visible in `docker inspect`.

**Q4: How do you keep images small and why?**
A4: Multi-stage builds, alpine/slim/distroless bases, `--omit=dev`, cleaning package caches. Smaller means faster pulls and fewer CVEs.

**Q5: What must you monitor for containers?**
A5: Restart count, OOM kills, CPU/memory against limits, healthcheck status, disk usage (images, volumes, logs), and application error rates.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Before every first production release and in each PR review via CI
- After incidents, to add the missing item to the list

❌ Avoid when:
- Never skip it; but do not treat it as a one-time task. Dev-only containers can relax some items (read-only fs, limits).

---

## 📊 Visual Diagram
```
 CODE -> BUILD -> SCAN -> PUSH -> DEPLOY -> RUN -> OBSERVE
  |        |        |       |        |       |        |
  |  multi-stage  Trivy   ECR    pinned   limits   logs
  | .dockerignore  gate   tags    SHA    healthchk metrics
  |  no secrets          (scan)  rollback non-root  alerts
  +------------------ feedback: incidents add items ------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Immutable tag | Tag that never changes (git SHA) | कभी न बदलने वाला tag |
| Digest | SHA256 hash of image content | Image content का hash |
| OOM kill | Kernel kills process over memory limit | Memory limit पार करने पर kernel द्वारा kill |
| Log rotation | Cap size and count of log files | Log files की size/संख्या सीमित करना |
| Supply chain | Everything your image depends on | वह सब जिस पर आपकी image निर्भर है |

---

## ⚡ 3-Line Summary
English: A production checklist covers build, security, runtime limits, config, observability and recovery.
Pin versions, run non-root, keep secrets out of images, rotate logs, set limits.
Automate the checks in CI so they never depend on memory.

Hindi: Production checklist में build, security, runtime limits, config, observability और recovery आते हैं।
Versions pin करो, non-root चलाओ, secrets images से बाहर रखो, logs rotate करो, limits लगाओ।
Checks को CI में automate करो ताकि याददाश्त पर निर्भर न रहना पड़े।

---

## ➡️ Next Topic
**212. Docker Security Hardening**: we go deeper into the security part of this checklist.

---
