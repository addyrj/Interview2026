# 241. Self-hosted Runners
# हिंदी में: Self-hosted Runners (अपने खुद के runners)

---

## 🔵 Simple Definition (English)
A **self-hosted runner** is a machine you own and manage (a VPS, EC2 instance, on-prem server or Kubernetes pod) on which you install the GitHub Actions runner application. It registers with your repo or organization and picks up jobs whose `runs-on` labels match.

## 🔵 सरल परिभाषा (Hindi)
**Self-hosted runner** वह machine है जो आपकी अपनी है और आप ही संभालते हैं (VPS, EC2 instance, on-prem server या Kubernetes pod), जिस पर आप GitHub Actions runner application install करते हैं। वह आपकी repo या organization में register होता है और उन jobs को उठाता है जिनके `runs-on` labels match करें।

---

## 🔴 Problem it Solves
Hosted runners cannot reach your private database, internal APIs or a VPS whose firewall is closed. They also have fixed hardware, no GPUs, no custom software and cost per minute. Big teams with 50,000 build minutes a month can pay more than a few servers cost.

Self-hosted runners give you private network access, custom hardware and tools, persistent caches (faster builds), and flat cost.

## 🔴 यह क्यों बना? (Hindi)
Hosted runners आपके private database, internal APIs या बंद firewall वाले VPS तक नहीं पहुँच सकते। उनका hardware तय है, GPU नहीं, custom software नहीं और हर minute का पैसा लगता है। जिन बड़ी teams के महीने में 50,000 build minutes होते हैं वे कुछ servers की कीमत से ज़्यादा दे सकती हैं।

Self-hosted runners private network access, custom hardware और tools, persistent caches (तेज़ builds) और तय cost देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Repo/Org Settings -> Actions -> Runners -> New self-hosted runner
Step 2 → GitHub shows OS-specific commands + a short-lived registration token
Step 3 → On your machine: download runner tarball, run ./config.sh --url ... --token ...
Step 4 → Give labels (e.g. vps, linux, x64) and a name
Step 5 → Start it: ./run.sh (test) or install as a service: sudo ./svc.sh install && sudo ./svc.sh start
Step 6 → Runner shows "Idle" in GitHub; it long-polls GitHub over outbound HTTPS
Step 7 → A job with runs-on: [self-hosted, vps] is assigned; runner executes it
Step 8 → Runner returns to Idle (persistent) or exits (if --ephemeral)
```

Key points:
- No inbound ports needed; only outbound HTTPS.
- The machine is **not** cleaned between jobs unless you use ephemeral runners or clean up manually.
- You are responsible for OS patching, runner updates (it auto-updates itself), Docker, disk space and monitoring.
- Runner groups (organization level) control which repos can use which runners.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Repo/Org Settings -> Actions -> Runners -> New self-hosted runner।
Step 2 → GitHub OS के हिसाब से commands और थोड़े समय वाला registration token दिखाता है।
Step 3 → अपनी machine पर runner tarball download करें और `./config.sh --url ... --token ...` चलाएँ।
Step 4 → Labels (जैसे `vps`, `linux`, `x64`) और नाम दें।
Step 5 → चालू करें: `./run.sh` (test के लिए) या service की तरह: `sudo ./svc.sh install && sudo ./svc.sh start`।
Step 6 → GitHub में runner "Idle" दिखता है; वह outbound HTTPS से poll करता है।
Step 7 → `runs-on: [self-hosted, vps]` वाला job उसे मिलता है और वह चलाता है।
Step 8 → Runner वापस Idle (persistent) या बंद (अगर `--ephemeral`)।

ध्यान रखें: inbound port नहीं चाहिए; machine jobs के बीच साफ़ नहीं होती (जब तक ephemeral न हो); OS patching, disk, Docker और monitoring आपकी ज़िम्मेदारी है।

---

## 🟡 Real World Example
A fintech runs its production database in a private AWS subnet. Their pipeline must run DB migrations during deploy. A hosted runner cannot reach the subnet, and opening the DB to the internet is forbidden. They launch an EC2 instance inside the subnet, install a self-hosted runner with label `prod-vpc`, and the `migrate` job runs on it. Another team runs a runner on a small Hetzner/DigitalOcean VPS to cut the monthly Actions bill for long Docker builds with a warm layer cache.

## 🟡 Real Example Hindi mein
एक fintech का production database private AWS subnet में है। Deploy के दौरान DB migrations चलाने हैं। Hosted runner उस subnet तक नहीं पहुँचता और DB को internet पर खोलना मना है। वे subnet के अंदर एक EC2 instance चलाते हैं, उस पर `prod-vpc` label वाला self-hosted runner लगाते हैं, और `migrate` job उसी पर चलता है। दूसरी team लंबे Docker builds का Actions bill घटाने के लिए छोटे VPS पर runner चलाती है, जहाँ layer cache गर्म रहता है।

---

## 💻 Code / Config Example — Basic
Install on a Linux VPS (Ubuntu). Version and token are placeholders; copy the exact commands GitHub shows for your repo.

```bash
#!/usr/bin/env bash
# install-runner.sh  - run on the VPS as a NON-root user (e.g. "runner")
set -euo pipefail                                   # Stop on any error or unset variable

RUNNER_VERSION="2.321.0"                            # EXAMPLE version; check github.com/actions/runner/releases
REPO_URL="https://github.com/YOUR_ORG/YOUR_REPO"    # Repo (or org) the runner belongs to
REG_TOKEN="PASTE_TOKEN_FROM_GITHUB_UI"              # Short-lived token, expires in about 1 hour

mkdir -p "$HOME/actions-runner" && cd "$HOME/actions-runner"   # Working folder for the runner
curl -fsSLO "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"   # Download runner
tar xzf "actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"    # Unpack it

./config.sh \
  --url "$REPO_URL" \
  --token "$REG_TOKEN" \
  --name "vps-runner-1" \
  --labels "vps,linux,x64" \
  --work "_work" \
  --unattended                                      # Register without interactive prompts

sudo ./svc.sh install                               # Install as a systemd service (runs as current user)
sudo ./svc.sh start                                 # Start now and on boot
sudo ./svc.sh status                                # Confirm it is running
```

Use it in a workflow:

```yaml
# .github/workflows/selfhosted-basic.yml
name: Self-hosted Basic               # Workflow name
on: [workflow_dispatch]               # Manual trigger
jobs:
  whoami:
    runs-on: [self-hosted, linux, vps]   # ALL labels must exist on one runner
    steps:
      - run: |                        # Show where we run
          hostname                    # VPS hostname
          whoami                      # Should be the non-root runner user
          docker --version            # Docker must be installed by you
```

## 💻 Code / Config Example — Advanced
Ephemeral, autoscaled-style runner using Docker Compose (one job per container, then it exits and Docker restarts a fresh one). Registration token must be fetched fresh; in production use a GitHub App/PAT to request tokens automatically (shown as env placeholders). Not run locally here.

```yaml
# docker-compose.runner.yml  - ephemeral runner container (example image: myoung34/github-runner, community image)
services:
  runner:
    image: myoung34/github-runner:latest     # Community image; pin a tag/digest in production
    restart: always                          # After an ephemeral job exits, start a fresh runner
    environment:
      REPO_URL: https://github.com/YOUR_ORG/YOUR_REPO   # Where to register
      RUNNER_NAME_PREFIX: vps-eph            # Name prefix
      RUNNER_SCOPE: repo                     # Repo-level runner
      ACCESS_TOKEN: ${RUNNER_PAT}            # PAT with repo admin scope, from .env (never commit)
      EPHEMERAL: "true"                      # One job per container lifetime
      LABELS: vps,linux,ephemeral            # Labels used in runs-on
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock   # DANGER: gives root-equivalent access to host Docker
    deploy:
      resources:
        limits:
          cpus: "2"                          # Cap CPU used by job containers (honoured by Compose v2 outside Swarm)
          memory: 4g                         # Cap memory
```

```yaml
# .github/workflows/selfhosted-advanced.yml
name: Self-hosted Advanced            # Use ephemeral runner safely
on:
  push:
    branches: [main]                  # Only trusted branch (never run fork PRs here)
permissions:
  contents: read
jobs:
  build:
    runs-on: [self-hosted, linux, ephemeral]   # Matches the labels above
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapi:${{ github.sha }} .   # Layer cache persists on the host daemon
      - if: always()                  # Cleanup even on failure
        run: docker image prune -f    # Avoid filling the VPS disk
```

Mounting `docker.sock` is convenient but lets any job take over the host. For stronger isolation use rootless Docker, Sysbox, Kubernetes with Actions Runner Controller (ARC), or VM-per-job tools.

---

## 🟠 My Stack Integration
On your VPS (Nginx + Docker Compose running Node.js, FastAPI, React), a self-hosted runner lets the deploy job run **locally** without opening SSH to GitHub:

```yaml
# .github/workflows/deploy-selfhosted.yml
name: Deploy via Self-hosted Runner
on:
  push:
    branches: [main]
concurrency:
  group: deploy-vps                   # Never two deploys at once on the same box
  cancel-in-progress: false
jobs:
  test:
    runs-on: ubuntu-24.04             # Hosted runner: untrusted-ish work, no access to VPS
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci && npm test
  deploy:
    needs: test
    runs-on: [self-hosted, linux, vps]   # Runner lives on the VPS
    environment: production           # Approval + scoped secrets
    steps:
      - uses: actions/checkout@v4     # Get docker-compose.yml
      - run: docker compose pull      # Pull new images
      - run: docker compose up -d --remove-orphans   # Recreate changed services
      - run: docker image prune -f    # Remove dangling images
```

Security checklist: run the runner as a dedicated non-root user (add to `docker` group only if you accept that it equals root); public repos must never use it; restrict the repo in a runner group; firewall the VPS; keep OS patched; consider `--ephemeral`; remove the runner and delete secrets from disk when decommissioning (`./config.sh remove --token ...`).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Registering a self-hosted runner on a public repo.
✅ Correct: Use only private repos. A fork PR could run arbitrary code on your server.

❌ Mistake 2: Running the runner as root.
✅ Correct: Dedicated unprivileged user.

❌ Mistake 3: Letting disk fill with old Docker images and `_work` folders.
✅ Correct: Scheduled `docker system prune`, cleanup step in jobs, disk monitoring.

❌ Mistake 4: Storing secrets in files on the runner between jobs.
✅ Correct: Secrets come from GitHub per job; ephemeral runners avoid leftovers.

---

## 🧠 Tricky Interview Question
"A contributor forks your private-org public repo and opens a PR that edits the workflow to run `cat ~/.ssh/*` on your self-hosted runner. How do you stop this?"

Answer: Do not use self-hosted runners for public repos at all. If unavoidable: require approval for all outside collaborators' workflow runs, restrict the runner group to selected private repos, use ephemeral runners in disposable VMs with no credentials on disk, run on a segregated network, and protect `.github/workflows` with CODEOWNERS. The default token for fork PRs is read-only, but the runner machine itself is the asset at risk, since code runs directly on it.

---

## ⚫ Interview Questions + Answers

Q1: How does a self-hosted runner communicate with GitHub?
A1: Outbound HTTPS long polling; no inbound ports.

Q2: What does `--ephemeral` do?
A2: The runner accepts exactly one job, then unregisters and exits, giving a clean slate each time.

Q3: What are runner labels?
A3: Tags like `self-hosted`, OS, architecture and custom values; a job needs a runner having all labels in `runs-on`.

Q4: Who updates the runner software?
A4: The runner auto-updates itself, but you patch the OS, Docker and tooling.

Q5: What is ARC?
A5: Actions Runner Controller, a Kubernetes operator that autoscales ephemeral runner pods based on queued jobs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Jobs need private network, special hardware or large persistent caches.
- Minutes cost is high and you can operate servers.
- Compliance forbids shared infrastructure.

❌ Avoid when:
- Repo is public or accepts untrusted PRs.
- Nobody can patch and monitor the machine.
- Hosted runners already meet needs.

---

## 📊 Visual Diagram

```
        GitHub
   +----------------+
   | job queue      |<------- outbound HTTPS (poll) ------+
   | runs-on:       |                                     |
   | [self-hosted,  |                              +------+--------+
   |  vps]          |------- job assigned -------> | Your VPS      |
   +----------------+                              | runner (svc)  |
                                                   | docker, nginx |
                                                   | /_work/...    |
                                                   +---------------+
   Firewall: inbound CLOSED, outbound 443 OPEN
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Self-hosted runner | Runner on your machine | आपकी machine पर runner |
| Registration token | Short-lived token to register | register करने का अल्पकालिक token |
| Ephemeral | One job then exits | एक job के बाद बंद |
| Runner group | Controls which repos use runners | किन repos को runner मिले |
| ARC | Kubernetes runner autoscaler | Kubernetes runner autoscaler |
| svc.sh | Script to install runner as service | runner को service बनाने की script |

---

## ⚡ 3-Line Summary
English: Self-hosted runners run Actions jobs on machines you manage, giving private access, custom hardware and flat cost.
They connect outbound only, but you own patching, cleanup and security.
Never use them with public repos; prefer ephemeral runners.

Hindi: Self-hosted runners आपकी अपनी machines पर jobs चलाते हैं, जिससे private access, custom hardware और तय cost मिलता है।
वे सिर्फ outbound जुड़ते हैं, लेकिन patching, सफाई और सुरक्षा आपकी ज़िम्मेदारी है।
Public repos के साथ कभी न इस्तेमाल करें; ephemeral runners बेहतर हैं।

---

## ➡️ Next Topic
**242. Workflow YAML Structure** — all top-level keys (`name`, `on`, `env`, `permissions`, `jobs`) and how they fit together.

---
