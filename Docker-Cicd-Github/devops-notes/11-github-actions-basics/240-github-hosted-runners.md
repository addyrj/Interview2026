# 240. GitHub-hosted Runners
# हिंदी में: GitHub-hosted Runners (GitHub द्वारा चलाए जाने वाले runners)

---

## 🔵 Simple Definition (English)
**GitHub-hosted runners** are virtual machines that GitHub creates, patches and destroys for you. You pick one with a label such as `ubuntu-latest`; every job gets a brand-new VM with common tools pre-installed (Git, Docker, Node, Python, AWS CLI). You pay nothing to maintain them.

## 🔵 सरल परिभाषा (Hindi)
**GitHub-hosted runners** ऐसी virtual machines हैं जिन्हें GitHub आपके लिए बनाता, patch करता और नष्ट करता है। आप `ubuntu-latest` जैसे label से चुनते हैं; हर job को नई VM मिलती है जिसमें आम tools पहले से installed हैं (Git, Docker, Node, Python, AWS CLI)। इन्हें maintain करने की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
Running your own CI servers means buying machines, installing toolchains, applying OS patches, cleaning disks, handling scaling on release day, and securing them. A small team loses days per month on this.

Hosted runners remove all of it: clean VM per job, automatic security patching, elastic parallelism (as many jobs as your plan allows), and you only write YAML.

## 🔴 यह क्यों बना? (Hindi)
अपने CI servers चलाने का मतलब है machines खरीदना, toolchain install करना, OS patches लगाना, disk साफ़ करना, release के दिन scaling संभालना और उन्हें सुरक्षित रखना। छोटी team का महीने में कई दिन इसी में जाता है।

Hosted runners यह सब हटा देते हैं: हर job पर साफ़ VM, अपने-आप security patching, elastic parallelism (आपके plan की सीमा तक जितने jobs), और आपको सिर्फ YAML लिखना है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Job with `runs-on: ubuntu-latest` is queued
Step 2 → GitHub provisions a new VM from a prebuilt image (in Azure)
Step 3 → Runner app starts, receives the job, passwords/tokens are injected
Step 4 → Your steps run with passwordless sudo on Linux/macOS, admin on Windows
Step 5 → Logs go back to GitHub
Step 6 → VM is destroyed; disk, files and env vars are gone forever
```

Common standard labels (check the docs for the current list, it changes):
- `ubuntu-latest`, `ubuntu-24.04`, `ubuntu-22.04`
- `windows-latest`, `windows-2022`, `windows-2025`
- `macos-latest`, `macos-14`, `macos-15` (macOS minutes cost more)
- Arm Linux labels such as `ubuntu-24.04-arm` (availability depends on repo type/plan)

Typical specs of standard Linux runner: 4 vCPU, 16 GB RAM, ~14 GB SSD for public repos; private repos on the standard plan typically get 2 vCPU, 7 GB RAM (these numbers change; verify in GitHub docs). **Larger runners** (paid, up to 64+ vCPU and static IPs) exist for heavy builds.

Limits to remember: job time up to 6 hours; workflow run up to 35 days; concurrency depends on plan; usage billed in minutes with OS multipliers (Linux x1, Windows x2, macOS x10 on standard private-repo billing; confirm current rates).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `runs-on: ubuntu-latest` वाला job queue होता है।
Step 2 → GitHub पहले से बनी image से नई VM बनाता है (Azure में)।
Step 3 → Runner app शुरू होकर job पाता है और tokens inject होते हैं।
Step 4 → आपके steps चलते हैं (Linux/macOS पर बिना password के sudo)।
Step 5 → Logs GitHub को वापस जाते हैं।
Step 6 → VM नष्ट; disk, files और env vars हमेशा के लिए गए।

मानक labels: `ubuntu-latest`, `windows-latest`, `macos-latest`, और खास versions। Specs और दरें बदलती रहती हैं, इसलिए current docs देखें। Limits: job अधिकतम 6 घंटे; minutes billing में OS multiplier (Linux सबसे सस्ता, macOS सबसे महँगा)।

---

## 🟡 Real World Example
An Indian SaaS startup has a private monorepo (Node.js API + React). They run ~300 pushes a month; each CI run takes 6 minutes on Linux = ~1,800 minutes, which fits inside the free quota of a small paid plan. When release week brings 3x more pushes, GitHub simply starts more VMs. When they added Windows desktop builds the minutes cost doubled for that job, so they run it only on tags.

## 🟡 Real Example Hindi mein
एक भारतीय SaaS startup के पास private monorepo है (Node.js API + React)। महीने में लगभग 300 pushes; हर CI run Linux पर 6 मिनट = करीब 1,800 minutes, जो छोटे paid plan के free quota में आ जाता है। Release के हफ्ते pushes 3 गुना हों तो GitHub बस और VMs शुरू कर देता है। Windows desktop builds जोड़ने पर उस job की minutes cost दोगुनी हुई, इसलिए वे उसे सिर्फ tags पर चलाते हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/hosted-basic.yml
name: Hosted Runner Basic             # Workflow name
on: [workflow_dispatch]               # Manual run for exploration
jobs:
  inspect:
    runs-on: ubuntu-24.04             # Pin the OS version instead of "latest" for stability
    steps:
      - name: What do I have?         # Step name
        run: |                        # Multi-line script
          cat /etc/os-release | head -3   # OS name and version
          echo "CPUs: $(nproc)"       # CPU count
          free -h | head -2           # Memory
          df -h / | tail -1           # Disk
          git --version               # Preinstalled tools
          docker --version
          aws --version
          python3 --version
          node --version
      - name: Sudo works without password   # Hosted Linux allows it
        run: sudo apt-get update -y && sudo apt-get install -y jq   # Install an extra tool
      - run: jq --version             # Confirm installation
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/hosted-advanced.yml
name: Hosted Runner Advanced          # Save minutes + keep builds stable
on:
  pull_request:
  push:
    branches: [main]
concurrency:
  group: ci-${{ github.ref }}         # One active run per branch
  cancel-in-progress: true            # Cancel stale runs to save paid minutes
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-24.04             # Pinned image
    timeout-minutes: 15               # Hard cap on minutes consumed
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 1              # Shallow clone is faster
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm                  # Avoid re-downloading packages
      - run: npm ci
      - run: npm test -- --ci
      - name: Free disk if needed     # Only when build is huge
        if: ${{ failure() }}          # Show disk usage on failure for diagnosis
        run: df -h
  docker-build:
    needs: test
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3   # Buildx for cache support
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: false                 # Only verify the build on PRs
          load: true                  # Make image available to later steps
          tags: myapi:ci
          cache-from: type=gha        # Use GitHub's cache service for layers
          cache-to: type=gha,mode=max
```

---

## 🟠 My Stack Integration
For your VPS + AWS workflow, hosted runners are the build and test side; the deploy side reaches out:

```yaml
# .github/workflows/stack-hosted.yml
name: Stack Hosted Runner
on:
  push:
    branches: [main]
permissions:
  contents: read
  id-token: write                     # Needed for AWS OIDC login
jobs:
  build-and-push:
    runs-on: ubuntu-24.04             # Hosted runner builds the image
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4   # Example version
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-ecr-push   # Placeholder ARN
          aws-region: ap-south-1
      - uses: aws-actions/amazon-ecr-login@v2             # Docker login to ECR
      - run: echo "docker build + push to ECR here"       # Covered in AWS topics
  deploy-vps:
    needs: build-and-push
    runs-on: ubuntu-24.04             # Same hosted runner type SSHes to VPS
    steps:
      - name: Prepare SSH key         # Key stored as repo/environment secret
        run: |
          install -m 700 -d ~/.ssh                       # Create .ssh with strict perms
          echo "${{ secrets.VPS_SSH_KEY }}" > ~/.ssh/id_ed25519   # Write private key
          chmod 600 ~/.ssh/id_ed25519                    # SSH refuses open permissions
          ssh-keyscan -H "${{ secrets.VPS_HOST }}" >> ~/.ssh/known_hosts   # Trust host (better: pin fingerprint)
      - run: ssh -i ~/.ssh/id_ed25519 deploy@"${{ secrets.VPS_HOST }}" 'cd /srv/app && docker compose pull && docker compose up -d'
```

Security: hosted runner IPs change and are public (GitHub publishes ranges in its meta API), so do not allow-list them on your VPS firewall as the only protection; rely on SSH keys, a dedicated low-privilege `deploy` user, and fail2ban. Use larger runners with static IPs if you must allow-list.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `ubuntu-latest` and being surprised when Ubuntu version changes and a build breaks.
✅ Correct: Pin `ubuntu-24.04` and upgrade deliberately.

❌ Mistake 2: Running tests on macOS "just in case", burning 10x minutes.
✅ Correct: Use Linux unless you need macOS-specific behaviour.

❌ Mistake 3: Not setting `timeout-minutes`, so one hung test uses 360 minutes.
✅ Correct: Set 10-20 minutes for normal CI.

❌ Mistake 4: Relying on preinstalled tool versions.
✅ Correct: Use setup actions (`setup-node`, `setup-python`) to pin versions.

---

## 🧠 Tricky Interview Question
"Your build needs 30 GB of disk but the hosted runner has ~14 GB free. What are your options without buying anything?"

Answer: Free space by removing unneeded preinstalled toolchains (e.g. `sudo rm -rf /usr/share/dotnet /opt/ghc /usr/local/lib/android` is a common trick; verify paths on the current image), reduce what you build or cache, split the work across jobs, or use docker build cache selectively. Paid alternatives: larger runners with more disk or self-hosted runners. Never rely on the free-space trick for production-critical pipelines because image layout can change.

---

## ⚫ Interview Questions + Answers

Q1: What does `ubuntu-latest` mean?
A1: GitHub's current default Ubuntu image; it changes when GitHub migrates, so pin a version for reproducibility.

Q2: Is state kept between jobs on hosted runners?
A2: No, every job is a fresh VM.

Q3: Can I use sudo?
A3: Yes on Linux and macOS hosted runners (passwordless); hosted runners are single-use so it is safe within the VM.

Q4: How is usage billed?
A4: Private repos consume included minutes then pay per minute, with different multipliers per OS. Public repos use standard runners for free.

Q5: How do I get a static IP for my firewall?
A5: Use larger runners with static IP ranges, or a self-hosted runner, or use SSH keys + jump host rather than IP allow-listing.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want zero maintenance and clean environments.
- Builds are small to medium and need no private network.

❌ Avoid when:
- You need access to private databases or on-prem systems.
- You need GPUs, huge disks, or very long jobs beyond limits.
- Minutes bill grows larger than a self-hosted runner would cost.

---

## 📊 Visual Diagram

```
 push event
     |
     v
 +---------+    new VM from image    +---------------------------+
 | GitHub  | ----------------------> | Hosted runner VM          |
 | Actions |                         | ubuntu-24.04  4 vCPU 16GB |
 +----+----+                         | git docker node python aws|
      ^                              +-------------+-------------+
      | logs / status                              | run steps
      +--------------------------------------------+
                                                   |
                                          job ends -> VM DELETED
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hosted runner | VM managed by GitHub | GitHub की managed VM |
| Runner image | Prebuilt OS + tools | OS + tools की तैयार image |
| Larger runner | Paid bigger/static-IP runner | बड़ा paid runner |
| Minutes multiplier | OS-based billing factor | OS के अनुसार बिलिंग गुणक |
| Pinning | Fix to specific version | खास version पर बाँधना |
| Ephemeral | Destroyed after one job | एक job के बाद नष्ट |

---

## ⚡ 3-Line Summary
English: Hosted runners are fresh VMs managed by GitHub, selected by labels like `ubuntu-24.04`.
They come with common tools, scale on demand, and are billed in minutes with OS multipliers.
Pin versions, set timeouts and use caching to control cost and breakage.

Hindi: Hosted runners GitHub की managed नई VMs हैं, जिन्हें `ubuntu-24.04` जैसे labels से चुना जाता है।
इनमें आम tools होते हैं, ज़रूरत पर scale होते हैं और OS multiplier के साथ minutes में बिल होते हैं।
Cost और टूटने से बचने के लिए versions pin करें, timeout लगाएँ और caching इस्तेमाल करें।

---

## ➡️ Next Topic
**241. Self-hosted Runners** — run jobs on your own VPS or VPC when you need private access, more power or lower cost.

---
