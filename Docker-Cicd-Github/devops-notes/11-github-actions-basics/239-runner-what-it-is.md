# 239. Runner — What it is
# हिंदी में: Runner — यह क्या है

---

## 🔵 Simple Definition (English)
A **runner** is the machine (virtual machine or container host) that executes a job's steps. It runs the GitHub Actions runner application, listens for jobs, runs them one at a time, and reports logs and results back to GitHub. Runners are either **GitHub-hosted** or **self-hosted**.

## 🔵 सरल परिभाषा (Hindi)
**Runner** वह machine (virtual machine या container host) है जो job के steps चलाती है। उस पर GitHub Actions runner application चलता है जो jobs सुनता है, एक बार में एक job चलाता है और logs व नतीजे GitHub को वापस भेजता है। Runners **GitHub-hosted** या **self-hosted** होते हैं।

---

## 🔴 Problem it Solves
YAML is only text: something must actually execute `npm test`. Teams used to keep long-lived build servers that slowly accumulated old Node versions, leftover files and secrets, which caused "works on build server A, fails on B" problems.

Runners give each job a clean, known environment (for hosted ones: a brand-new VM every time) with pre-installed tools, so builds are reproducible and isolated.

## 🔴 यह क्यों बना? (Hindi)
YAML सिर्फ text है: `npm test` असल में किसी को चलाना पड़ता है। Teams पहले लंबे समय तक चलने वाले build servers रखती थीं जिन पर पुराने Node versions, बची हुई files और secrets जमा हो जाते थे, जिससे "build server A पर चलता है, B पर fail" जैसी समस्याएँ आती थीं।

Runner हर job को साफ़, ज्ञात environment देता है (hosted में: हर बार बिल्कुल नई VM) जिसमें tools पहले से installed होते हैं, इसलिए builds दोहराए जा सकते हैं और isolated रहते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Job is queued with a `runs-on` label (e.g. ubuntu-latest)
Step 2 → GitHub finds an idle runner that has ALL requested labels
Step 3 → Runner app (long poll over HTTPS, outbound only) receives the job
Step 4 → Runner creates the workspace and downloads required actions
Step 5 → Steps execute; logs stream to GitHub in near real time
Step 6 → Job ends -> hosted VM destroyed / self-hosted runner returns to idle
Step 7 → If no runner is available, the job waits in queue (up to 24 hours then fails)
```

Runner facts:
- A runner executes **one job at a time**.
- It connects **outbound** to GitHub (HTTPS 443). GitHub never opens a connection into your network.
- Labels pick the runner: `ubuntu-latest`, `windows-latest`, `macos-latest`, or custom labels like `self-hosted, linux, x64, gpu`.
- Environment variables set on every runner: `RUNNER_OS`, `RUNNER_ARCH`, `RUNNER_TEMP`, `GITHUB_WORKSPACE`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Job `runs-on` label (जैसे `ubuntu-latest`) के साथ queue होता है।
Step 2 → GitHub ऐसा खाली runner ढूँढता है जिसके पास माँगे गए सारे labels हों।
Step 3 → Runner app (सिर्फ outbound HTTPS से लगातार poll) job पाता है।
Step 4 → Runner workspace बनाता है और ज़रूरी actions download करता है।
Step 5 → Steps चलते हैं; logs लगभग real time में GitHub पर stream होते हैं।
Step 6 → Job खत्म: hosted VM नष्ट; self-hosted runner वापस idle।
Step 7 → अगर कोई runner उपलब्ध नहीं तो job queue में इंतज़ार करता है (24 घंटे बाद fail)।

मुख्य बातें: एक runner एक बार में एक ही job चलाता है; वह GitHub से outbound (HTTPS 443) जुड़ता है, GitHub आपके network में अंदर कनेक्शन नहीं खोलता; labels से runner चुना जाता है।

---

## 🟡 Real World Example
A startup builds its React + Node.js app on `ubuntu-latest` hosted runners: each push gets a fresh 4-vCPU VM (public repos; private repo size depends on plan and runner type), with Node, Docker, AWS CLI, Git already installed, and nothing left behind afterwards. Their mobile team needs iOS builds and uses `macos-latest`. A data team needs GPUs for model tests, so they register a **self-hosted** runner with label `gpu` on their own server.

## 🟡 Real Example Hindi mein
एक startup अपना React + Node.js app `ubuntu-latest` hosted runners पर build करता है: हर push को नई VM मिलती है जिसमें Node, Docker, AWS CLI, Git पहले से installed हैं और बाद में कुछ बचता नहीं। Mobile team को iOS builds चाहिए तो वे `macos-latest` लेते हैं। Data team को model tests के लिए GPU चाहिए, तो वे अपने server पर `gpu` label वाला **self-hosted** runner register करते हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/runner-basic.yml
name: Runner Basic                    # Workflow name
on: [workflow_dispatch]               # Manual trigger for easy testing
jobs:
  linux:
    runs-on: ubuntu-latest            # GitHub-hosted Linux runner
    steps:
      - run: |                        # Inspect the runner
          echo "OS:   $RUNNER_OS"     # Linux
          echo "Arch: $RUNNER_ARCH"   # X64 or ARM64
          echo "Temp: $RUNNER_TEMP"   # Per-job temp folder
          echo "Work: $GITHUB_WORKSPACE"   # Where code is checked out
          nproc                       # CPU count
          free -h                     # Memory
          df -h /                     # Disk space
          docker --version            # Docker preinstalled on hosted Linux
          node --version              # Node preinstalled (version varies)
  windows:
    runs-on: windows-latest           # GitHub-hosted Windows runner
    steps:
      - run: echo "OS is $env:RUNNER_OS"   # Default shell on Windows is PowerShell
        shell: pwsh                   # Explicit PowerShell Core
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/runner-advanced.yml
name: Runner Advanced                 # Labels, containers, matrix of OSes
on:
  push:
    branches: [main]
jobs:
  cross-platform:
    strategy:
      fail-fast: false                # Let all OS legs finish
      matrix:
        os: [ubuntu-latest, ubuntu-24.04-arm, windows-latest]   # ARM label availability depends on plan; verify
    runs-on: ${{ matrix.os }}         # Runner chosen from matrix
    timeout-minutes: 20               # Cap runtime
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci && npm test       # Same commands on every OS
  in-container:
    runs-on: ubuntu-latest            # Host runner
    container:                        # Run all steps inside this image
      image: node:20-bookworm-slim    # Example tag; known toolchain
    steps:
      - uses: actions/checkout@v4     # Works inside container
      - run: node -v && npm -v        # Tools come from the image
  private-network:
    runs-on: [self-hosted, linux, x64, vpc-prod]   # ALL labels must match a registered runner
    steps:
      - run: curl -fs http://internal-api.local/health   # Reaches private network resources
```

The last job only works if you registered a self-hosted runner with those labels (next topics). Otherwise it waits in queue.

---

## 🟠 My Stack Integration
Runner choice for your stack:

| Task | Runner |
|---|---|
| Node.js / FastAPI / React tests and Docker build | `ubuntu-latest` hosted |
| Push to ECR/GHCR | hosted + OIDC / `GITHUB_TOKEN` |
| Deploy to VPS | hosted runner SSHes **out** to the VPS (VPS needs open SSH port, restricted by key) |
| Deploy where VPS firewall blocks GitHub IPs | self-hosted runner installed on the VPS itself, label `vps` |

```yaml
# snippet: deploy job executed directly on the VPS by a self-hosted runner
jobs:
  deploy:
    runs-on: [self-hosted, linux, vps]   # Runner process lives on your VPS
    steps:
      - uses: actions/checkout@v4        # Code lands on the VPS workspace
      - run: docker compose pull && docker compose up -d   # Local commands, no SSH needed
```

Security: a self-hosted runner executes whatever workflow tells it. Never attach one to a **public** repo (a fork PR could run code on your VPS). Run it as a non-root user, keep it updated, and prefer ephemeral (`--ephemeral`) runners.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming `ubuntu-latest` is always the same OS version.
✅ Correct: `latest` moves over time. Pin `ubuntu-24.04` (or the version you test) for stable builds.

❌ Mistake 2: Expecting files from yesterday's run on a hosted runner.
✅ Correct: Hosted runners are wiped; use cache/artifacts.

❌ Mistake 3: Using a self-hosted runner on a public repo.
✅ Correct: Only private repos, restricted runner groups.

❌ Mistake 4: Job stuck in "Waiting for a runner" because the label has a typo.
✅ Correct: Labels are case-sensitive and ALL must match; copy from runner settings.

---

## 🧠 Tricky Interview Question
"Your self-hosted runner is behind a corporate firewall that blocks all inbound traffic. Will GitHub still be able to send jobs to it?"

Answer: Yes. The runner makes **outbound** HTTPS (long-poll) connections to GitHub and pulls jobs; no inbound port is needed. You only need to allow outbound 443 to GitHub's required hostnames (github.com, api.github.com, `*.actions.githubusercontent.com` and, for downloads, others listed in the docs). That is why self-hosted runners work well inside strict networks.

---

## ⚫ Interview Questions + Answers

Q1: What is a runner?
A1: A machine running the GitHub Actions runner app that executes jobs.

Q2: How many jobs can a runner run at once?
A2: One. For parallelism, you need more runners (or hosted runners, which scale automatically).

Q3: How is a runner selected?
A3: By `runs-on` labels; all labels must match.

Q4: Are hosted runners persistent?
A4: No. Fresh VM per job, destroyed after.

Q5: Which OS options exist for hosted runners?
A5: Ubuntu (Linux), Windows and macOS, with various versions and architectures; larger paid runners also exist.

---

## 🔷 When to Use + When Not to Use
✅ Use hosted runners when:
- Standard builds, tests, Docker builds, no private-network need.

✅ Use self-hosted when:
- Private network access, special hardware, long builds, cost control at scale.

❌ Avoid self-hosted when:
- Repo is public, or you cannot patch and monitor the machine.

---

## 📊 Visual Diagram

```
 GitHub (control plane)
 +-------------------------+
 | queue: job needs        |
 | runs-on: ubuntu-latest  |
 +-----------+-------------+
             ^ outbound HTTPS (poll, logs)    NO inbound connection
             |
   +---------+----------+------------------+
   |                    |                  |
 Hosted VM            Hosted VM        Self-hosted runner
 (fresh, destroyed)   (macOS/Windows)  (your VPS / VPC, persistent)
   run steps            run steps         run steps
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Runner | Machine that runs jobs | job चलाने वाली machine |
| Label | Tag used to choose runner | runner चुनने का tag |
| Hosted | Managed by GitHub | GitHub द्वारा संचालित |
| Self-hosted | Managed by you | आपके द्वारा संचालित |
| Ephemeral | Runner used for one job only | सिर्फ एक job वाला runner |
| Workspace | Folder where code is checked out | code वाला folder |

---

## ⚡ 3-Line Summary
English: A runner is the machine that executes a job; one job at a time, chosen by `runs-on` labels.
GitHub-hosted runners are fresh and managed; self-hosted runners are yours and need hardening.
Runners connect outbound only, so they work behind firewalls.

Hindi: Runner वह machine है जो job चलाती है; एक बार में एक job, `runs-on` labels से चुनी जाती है।
GitHub-hosted runners नए और managed होते हैं; self-hosted आपके होते हैं और उन्हें सुरक्षित करना पड़ता है।
Runner सिर्फ outbound जुड़ता है, इसलिए firewall के पीछे भी काम करता है।

---

## ➡️ Next Topic
**240. GitHub-hosted Runners** — available images, specs, installed software, limits and costs.

---
