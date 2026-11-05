# 252. runs-on
# हिंदी में: runs-on (job किस machine पर चलेगा)

---

## 🔵 Simple Definition (English)
`runs-on` is a required job key that selects the **runner** (machine) where the job executes. Value can be a GitHub-hosted label (`ubuntu-latest`, `ubuntu-24.04`, `windows-latest`, `macos-latest`), a **self-hosted** label set (`[self-hosted, linux, x64, gpu]`), a larger-runner group, or an expression such as `${{ matrix.os }}`.

## 🔵 सरल परिभाषा (Hindi)
`runs-on` job की ज़रूरी key है जो **runner** (machine) चुनती है जहाँ job चलेगा। Value GitHub-hosted label (`ubuntu-latest`, `ubuntu-24.04`, `windows-latest`, `macos-latest`), **self-hosted** labels का सेट (`[self-hosted, linux, x64, gpu]`), larger-runner group या `${{ matrix.os }}` जैसी expression हो सकती है।

---

## 🔴 Problem it Solves
Different work needs different machines: Linux for Docker builds, macOS for iOS, Windows for .NET, ARM for arm64 images, GPUs for ML tests, private network access to a database or VPS firewall. Maintaining those build machines was painful. `runs-on` lets one line pick from managed ephemeral VMs, or route jobs to your own machines when you need special hardware, big caches, or private network access.

## 🔴 यह क्यों बना? (Hindi)
अलग काम के लिए अलग machine चाहिए: Docker builds के लिए Linux, iOS के लिए macOS, .NET के लिए Windows, arm64 images के लिए ARM, ML tests के लिए GPU, और database या VPS firewall तक private network पहुँच। इन build machines को सँभालना कठिन था। `runs-on` एक लाइन में managed ephemeral VMs में से चुनने देता है, या जब खास hardware, बड़े caches या private network चाहिए तो job को आपकी अपनी machines पर भेजता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Job is queued with its `runs-on` labels.
Step 2 → GitHub looks for an idle runner whose labels include ALL requested labels.
Step 3 → Hosted label (ubuntu-latest): GitHub provisions a fresh VM from an image (tools preinstalled).
Step 4 → Self-hosted: a registered runner agent polls GitHub, picks the job, runs it on your host.
Step 5 → Job executes steps; after finish a hosted VM is destroyed (ephemeral). Self-hosted may persist state!
Step 6 → If no runner matches labels, job waits in "Queued" (until timeout ~24h) - a classic typo symptom.
Step 7 → `ubuntu-latest` is a MOVING alias (now Ubuntu 24.04 as of docs; check) - pin for stability.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Job अपने `runs-on` labels के साथ queue होता है।
Step 2 → GitHub ऐसा idle runner खोजता है जिसके labels में माँगे गए सभी labels हों।
Step 3 → Hosted label (ubuntu-latest): GitHub image से नया VM बनाता है (tools पहले से installed)।
Step 4 → Self-hosted: registered runner agent GitHub को poll करके job उठाता है और आपके host पर चलाता है।
Step 5 → Job चलकर खत्म; hosted VM नष्ट (ephemeral)। Self-hosted पर state बचा रह सकता है!
Step 6 → कोई runner labels से न मिले तो job "Queued" में रुका रहता है (लगभग 24 घंटे तक) - typo का क्लासिक लक्षण।
Step 7 → `ubuntu-latest` बदलने वाला alias है - स्थिरता के लिए version pin करें।
```

| Label (examples) | Notes |
|---|---|
| `ubuntu-latest`, `ubuntu-24.04`, `ubuntu-22.04` | Most common; Docker preinstalled |
| `ubuntu-24.04-arm` | Native arm64 hosted runner (availability depends on plan/repo visibility) |
| `windows-latest`, `windows-2022` | Windows Server |
| `macos-latest`, `macos-14` | Apple silicon; billed at higher multiplier |
| `[self-hosted, linux, x64]` | Your machine |

---

## 🟡 Real World Example
A startup builds Docker images for both Intel EC2 and Graviton (ARM) ECS tasks. Builds run on `ubuntu-24.04` with QEMU, taking 18 minutes for arm64; they move that job to `ubuntu-24.04-arm` (native) and cut it to 4 minutes. Their integration tests must reach a database inside a private VPC, so that one job uses `[self-hosted, linux, vpc]` runners on an EC2 instance with no inbound ports.

## 🟡 Real Example Hindi mein
एक startup Intel EC2 और Graviton (ARM) ECS tasks दोनों के लिए Docker images बनाती है। Builds `ubuntu-24.04` पर QEMU से चलते हैं और arm64 में 18 मिनट लगते हैं; वे यह job `ubuntu-24.04-arm` (native) पर ले जाते हैं और 4 मिनट में हो जाता है। Integration tests को private VPC के अंदर database तक पहुँचना है, इसलिए वह job बिना inbound ports वाले EC2 पर `[self-hosted, linux, vpc]` runners से चलता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/runs-on-basic.yml
name: RunsOn Basic                        # workflow name
on: [push]                                # trigger

jobs:
  linux-job:                              # job 1
    runs-on: ubuntu-latest                # GitHub-hosted Linux (alias, moves over time)
    steps:
      - run: uname -a                     # print kernel info to prove where we are
      - run: docker --version             # Docker is preinstalled on hosted Ubuntu runners

  pinned-job:                             # job 2
    runs-on: ubuntu-24.04                 # pinned OS version for predictable tooling
    steps:
      - run: cat /etc/os-release          # show OS release
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/runs-on-advanced.yml
name: RunsOn Advanced
on:
  pull_request:                           # PR trigger (note the self-hosted warning below)
    branches: [main]

jobs:
  test-matrix:
    strategy:
      fail-fast: false                    # keep other OS legs running if one fails
      matrix:
        os: [ubuntu-24.04, ubuntu-22.04, windows-2022]   # one job per OS
        node: [20, 22]                    # x two Node versions = 6 jobs
    runs-on: ${{ matrix.os }}             # expression: picks runner per matrix leg
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm ci
      - run: npm test

  build-multi-arch:
    strategy:
      matrix:
        include:                          # explicit pairs: runner + docker platform
          - runner: ubuntu-24.04          # x86_64
            platform: linux/amd64
          - runner: ubuntu-24.04-arm      # native ARM runner (check availability for your plan)
            platform: linux/arm64
    runs-on: ${{ matrix.runner }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: .
          platforms: ${{ matrix.platform }}
          push: false                     # build only in this example

  private-network-tests:
    # SECURITY: only for trusted events. Never run fork PR code on self-hosted runners.
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: [self-hosted, linux, x64, vpc]   # ALL labels must match one runner
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/run-db-integration.sh   # reaches the private DB from inside the VPC
```

(YAML parsed locally; runner availability/labels must be confirmed in your GitHub org.)

---

## 🟠 My Stack Integration
- **Node.js / FastAPI:** `ubuntu-24.04` for tests and Docker builds; matrix over Node 20/22 and Python 3.11/3.12.
- **React:** `ubuntu-latest` is enough; build output goes to artifacts.
- **Nginx / VPS:** keep deploy jobs on hosted runners using SSH. If the VPS firewall allows only your office IP, use a self-hosted runner on a machine with that IP rather than opening SSH to the world.
- **AWS:** self-hosted runner on EC2 with an instance profile (no stored keys), or hosted runner with OIDC. Prefer ephemeral runners (one job, then terminate).

```bash
# Register an EPHEMERAL self-hosted runner (run on the runner host; token from repo Settings -> Actions -> Runners)
./config.sh --url https://github.com/acme/api --token "$REG_TOKEN" \
  --labels linux,x64,vpc --ephemeral --unattended   # --ephemeral: takes one job then deregisters
./run.sh                                            # start listening for jobs
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Typo in label (`ubuntu-lastest`) - job queues forever.
✅ Correct: Copy labels from docs; check "Waiting for a runner" quickly.

❌ Mistake 2: Using `ubuntu-latest` and being surprised when a tool version changes.
✅ Correct: Pin `ubuntu-24.04`, and pin tool versions with setup actions.

❌ Mistake 3: Self-hosted runners on public repos running PR code from forks.
✅ Correct: Use self-hosted only for private repos or trusted events; prefer ephemeral runners and isolation.

❌ Mistake 4: Assuming self-hosted runners are clean.
✅ Correct: Clean workspace (`actions/checkout` with `clean: true`), use containers or `--ephemeral`.

❌ Mistake 5: Running macOS for everything - it costs a 10x minute multiplier on private repos.
✅ Correct: Use macOS only where required.

---

## 🧠 Tricky Interview Question
You wrote `runs-on: [self-hosted, linux]` and you have two runners labeled `linux` and `gpu` respectively (one has `self-hosted, linux`, another `self-hosted, gpu`). Which one runs the job?

Answer: Only runners having ALL listed labels qualify: `self-hosted` and `linux`. The first runner matches; the gpu one does not (unless it also has `linux`). Labels are an AND filter, not OR. Every self-hosted runner automatically has `self-hosted` plus OS and architecture labels.

---

## ⚫ Interview Questions + Answers

Q1: Is `runs-on` required?
A1: Yes for normal jobs. Not allowed on jobs that call a reusable workflow with `uses:`.

Q2: Hosted vs self-hosted?
A2: Hosted: managed, ephemeral, clean, billed per minute (free quota). Self-hosted: you manage patching/security, can access private network/hardware, persistent unless ephemeral.

Q3: How to choose runner dynamically?
A3: Expression such as `runs-on: ${{ matrix.os }}` or `${{ github.event_name == 'push' && 'ubuntu-24.04' || 'ubuntu-22.04' }}`, or `fromJSON` of an input.

Q4: What does a job do if no runner is available?
A4: Waits in queue; fails after about 24 hours if never picked.

Q5: Is Docker available on hosted runners?
A5: Linux hosted runners have Docker; Windows/macOS hosted runners generally do not support running Linux containers the same way (macOS has no Docker by default).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Choose OS/arch for compatibility, speed (native ARM), or special hardware.
- Self-hosted for private network access, large caches, GPUs.

❌ Avoid when:
- Self-hosted for public repos with outside PRs.
- Pointing to `latest` aliases in reproducible release pipelines.

---

## 📊 Visual Diagram

```
 job: runs-on: ubuntu-24.04            job: runs-on: [self-hosted, linux, vpc]
        │                                         │
        ▼                                         ▼
  GitHub provisions fresh VM               runner agent on YOUR EC2 (polls GitHub, outbound HTTPS)
  (destroyed after job)                            │
        │                                         ▼
        ▼                                 private VPC: DB, Redis, internal API
  Docker build, tests, SSH deploy                  (no inbound ports opened)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| runner | Machine that executes a job | Job चलाने वाली machine |
| label | Tag used to select runners | Runner चुनने वाला tag |
| ephemeral | Used once then discarded | एक बार इस्तेमाल, फिर नष्ट |
| self-hosted | Runner you operate | आपका अपना runner |
| matrix | Run job for multiple combinations | कई संयोजनों पर job |
| larger runner | Paid bigger hosted machine | बड़ी paid hosted machine |

---

## ⚡ 3-Line Summary
English: `runs-on` selects the machine; hosted labels are ephemeral and self-hosted need security care.
English: Labels are an AND filter; typos queue forever.
English: Pin OS versions and prefer ephemeral runners.
Hindi: `runs-on` machine चुनता है; hosted labels ephemeral हैं और self-hosted में सुरक्षा का ध्यान चाहिए।
Hindi: Labels AND filter हैं; typo से job हमेशा queue में रहता है।
Hindi: OS versions pin करें और ephemeral runners पसंद करें।

---

## ➡️ Next Topic
**253. steps:** - the ordered list of actions and commands that actually do the work inside a job.
