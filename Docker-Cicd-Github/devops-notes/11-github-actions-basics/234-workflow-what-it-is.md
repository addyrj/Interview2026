# 234. Workflow — What it is
# हिंदी में: Workflow — यह क्या है

---

## 🔵 Simple Definition (English)
A **workflow** is a YAML file stored in `.github/workflows/` of your repository. It describes an automated process: which event starts it, which jobs it has, and what each job does. One repo can have many workflows (CI, deploy, nightly cleanup).

## 🔵 सरल परिभाषा (Hindi)
**Workflow** आपकी repository के `.github/workflows/` folder में रखी एक YAML file है। यह एक automated process बताती है: कौन सा event उसे शुरू करता है, उसमें कौन से jobs हैं और हर job क्या करता है। एक repo में कई workflows हो सकते हैं (CI, deploy, रात की सफाई)।

---

## 🔴 Problem it Solves
Earlier, build and release knowledge sat in a wiki page or in someone's head ("run this script, then SSH, then restart"). When that person left, deployments stopped. Pipelines configured by clicking in a web UI could not be reviewed, versioned or rolled back.

A workflow is **pipeline as code**: it lives in Git, is reviewed in pull requests, has history, and changes together with the code it builds.

## 🔴 यह क्यों बना? (Hindi)
पहले build और release का ज्ञान wiki page या किसी के दिमाग में होता था ("ये script चलाओ, फिर SSH करो, फिर restart")। वह आदमी चला जाए तो deployment रुक जाता था। Web UI में click करके बनी pipelines को न review किया जा सकता था, न version, न rollback।

Workflow **pipeline as code** है: यह Git में रहती है, PR में review होती है, उसकी history होती है और जिस code को build करती है उसके साथ ही बदलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You create .github/workflows/ci.yml and commit it
Step 2 → GitHub parses the file on the branch/commit that triggered the event
Step 3 → If the `on:` section matches the event, a "workflow run" is created
Step 4 → The run appears in the repo's Actions tab with a run number
Step 5 → Jobs execute; logs stream live; each step shows pass/fail
Step 6 → Run finishes: success, failure, cancelled or skipped
Step 7 → You can re-run all jobs or only failed jobs from the UI
```

Important facts:
- File extension must be `.yml` or `.yaml`, and it must be directly inside `.github/workflows/` (no sub-folders).
- The workflow version used is the one **at the commit that triggered the event** (for `push`/`pull_request` this is the pushed/merge commit; for `schedule` it is the default branch).
- The top-level `name:` is optional; if missing, GitHub shows the file path.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → आप `.github/workflows/ci.yml` बनाकर commit करते हैं।
Step 2 → जिस branch/commit पर event हुआ, GitHub उसी की file parse करता है।
Step 3 → अगर `on:` event से match हो जाए तो "workflow run" बनता है।
Step 4 → Run repo के Actions tab में run number के साथ दिखता है।
Step 5 → Jobs चलते हैं; logs live आते हैं; हर step का pass/fail दिखता है।
Step 6 → Run खत्म: success, failure, cancelled या skipped।
Step 7 → UI से सारे jobs या सिर्फ failed jobs दोबारा चला सकते हैं।

ज़रूरी बातें: extension `.yml` या `.yaml` हो और file सीधे `.github/workflows/` में हो (sub-folder नहीं)। जिस commit पर event हुआ, उसी commit वाला workflow version इस्तेमाल होता है (`schedule` में default branch वाला)।

---

## 🟡 Real World Example
A fintech team keeps four workflows in one repo:
- `ci.yml` runs lint + tests on every pull request.
- `deploy-staging.yml` runs on push to `develop`.
- `deploy-prod.yml` runs on version tags and needs manual approval.
- `nightly.yml` runs at 2 AM IST via cron to scan dependencies for vulnerabilities.

Each is a separate file, so a failure in the nightly scan never blocks a production deploy, and each has its own history and permissions.

## 🟡 Real Example Hindi mein
एक fintech team एक repo में चार workflows रखती है: `ci.yml` हर PR पर lint + tests चलाता है; `deploy-staging.yml` `develop` पर push होने पर; `deploy-prod.yml` version tag पर और manual approval माँगता है; `nightly.yml` रात 2 बजे IST cron से dependencies की vulnerabilities scan करता है। हर एक अलग file है, इसलिए nightly scan की failure कभी production deploy नहीं रोकती और हर की अपनी history और permissions हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/ci.yml            <- file path matters: must be in .github/workflows/
name: CI                              # Workflow name in the Actions sidebar
run-name: CI for ${{ github.ref_name }} by @${{ github.actor }}   # Title of each run (optional, supports expressions)
on:                                   # What starts this workflow
  push:                               # When commits are pushed
    branches: [main]                  # ...to main only
env:                                  # Workflow-level environment variable
  NODE_ENV: test                      # Visible to every job and step
jobs:                                 # The work to do
  build:                              # Job id
    runs-on: ubuntu-latest            # Machine type
    steps:
      - uses: actions/checkout@v4     # Fetch the repository (example version)
      - uses: actions/setup-node@v4   # Install Node.js
        with:
          node-version: 20            # Version 20
      - run: npm ci                   # Install exact locked dependencies
      - run: npm test                 # Run tests
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/ci-prod-ready.yml
name: CI Production Ready             # Display name
run-name: "CI #${{ github.run_number }} on ${{ github.ref_name }}"   # Readable run title with number
on:
  push:
    branches: [main, develop]         # Two long-lived branches
    paths-ignore:
      - "**.md"                       # Skip CI when only docs change
      - "docs/**"                     # Skip when docs folder changes
  pull_request:                       # Also validate PRs
  workflow_dispatch:                  # Allow manual runs from the UI
    inputs:
      debug:                          # Manual input named debug
        description: "Verbose logs?"  # Shown in the UI form
        type: boolean                 # Checkbox
        default: false                # Off by default
permissions:
  contents: read                      # Read-only token by default (security)
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}   # One run per workflow per branch
  cancel-in-progress: true            # New push cancels the older run
defaults:
  run:
    shell: bash                       # Explicit shell for every run step
    working-directory: .              # Default folder for run steps
jobs:
  ci:
    runs-on: ubuntu-latest            # GitHub-hosted runner
    timeout-minutes: 20               # Safety net against hung jobs
    env:
      DEBUG_MODE: ${{ inputs.debug }} # Input exists only for workflow_dispatch; empty otherwise
    steps:
      - uses: actions/checkout@v4     # Get code
      - uses: actions/setup-node@v4   # Node
        with:
          node-version: 20
          cache: npm                  # Cache dependencies
      - run: npm ci                   # Install
      - run: npm run lint             # Lint
      - run: npm test -- --ci         # Test
      - if: failure()                 # Only runs when a previous step failed
        run: echo "Tests failed, check logs"   # Hook for notifications
```

---

## 🟠 My Stack Integration
Recommended file layout for your Node.js + FastAPI + React repo deployed to a VPS:

```
.github/workflows/
├── ci.yml              # PR checks for api/, fastapi/, web/
├── deploy-vps.yml      # push to main -> build image -> SSH to VPS
└── nightly-scan.yml    # scheduled dependency + image scan
```

```yaml
# .github/workflows/deploy-vps.yml (skeleton, SSH steps come in later topics)
name: Deploy to VPS                   # Clear name for the Actions tab
on:
  push:
    branches: [main]                  # Only production branch deploys
    paths: ["api/**", "docker-compose.yml"]   # Only when backend or compose changes
concurrency:
  group: deploy-vps                   # Never run two deploys at once
  cancel-in-progress: false           # Let a running deploy finish
permissions:
  contents: read                      # Minimal token
jobs:
  deploy:
    runs-on: ubuntu-latest            # Runner that will connect to the VPS
    environment: production           # Can require manual approval + hold secrets
    steps:
      - uses: actions/checkout@v4     # Get compose file
      - run: echo "build, push and ssh here"   # Placeholder for later topics
```

Security: workflow files are code that can access secrets. Protect `.github/workflows/` with CODEOWNERS so only trusted reviewers can change it, and require PR review on `main`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Saving the file as `.github/workflow/ci.yml` (missing `s`) or inside a sub-folder.
✅ Correct: Exactly `.github/workflows/<name>.yml`.

❌ Mistake 2: Using tabs for indentation, or inconsistent indentation.
✅ Correct: Spaces only (2 per level); YAML does not allow tabs.

❌ Mistake 3: Testing a `schedule` workflow on a feature branch and wondering why it never runs.
✅ Correct: Scheduled workflows run only from the default branch.

❌ Mistake 4: Putting secrets in `env:` as plain text.
✅ Correct: Use `${{ secrets.NAME }}`.

---

## 🧠 Tricky Interview Question
"You edit `deploy.yml` in a pull request to add a malicious step that prints secrets. A contributor from a fork opens the PR. Will the new step run with your secrets?"

Answer: No for forks. With the `pull_request` event, workflows from forked PRs run with a read-only token and **without secrets**. The danger is `pull_request_target`, which runs the base repo's workflow with secrets; if you check out and run the PR's code there, you hand secrets to an attacker. Prefer `pull_request`, require approval for workflows from first-time contributors, and never execute untrusted PR code under `pull_request_target`.

---

## ⚫ Interview Questions + Answers

Q1: Where must workflow files live?
A1: In `.github/workflows/` at the repo root, with `.yml` or `.yaml` extension.

Q2: Can one repo have multiple workflows?
A2: Yes, any number. Each is independent and shows separately in the Actions tab.

Q3: What is the minimum a valid workflow needs?
A3: An `on:` trigger and a `jobs:` section with at least one job that has `runs-on` and `steps` (or `uses` for a reusable workflow).

Q4: What does `run-name` do?
A4: Sets the title of each run in the UI; it supports expressions like `${{ github.actor }}`.

Q5: How do you stop two deploy runs overlapping?
A5: Use `concurrency` with a fixed group name; set `cancel-in-progress: false` for deploys so a running deploy is not killed halfway.

---

## 🔷 When to Use + When Not to Use
✅ Use separate workflows when:
- CI, deploy and scheduled tasks have different triggers and permissions.
- You want independent history and re-runs.
- Different teams own different files (CODEOWNERS).

❌ Avoid when:
- Everything is tiny and one file with clear `if:` conditions is simpler.
- You are duplicating steps; use reusable workflows or composite actions instead of copy-paste.

---

## 📊 Visual Diagram

```
repo
 └── .github/workflows/
        ├── ci.yml ----------> on: pull_request
        ├── deploy.yml ------> on: push main
        └── nightly.yml -----> on: schedule

event ──> GitHub reads matching files ──> creates RUN #N
                                              |
                          +-------------------+-------------------+
                          v                   v                   v
                        job A               job B               job C
                      (runner)            (runner)            (runner)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Workflow | YAML pipeline file | YAML pipeline file |
| Run | One execution of a workflow | workflow का एक बार चलना |
| Pipeline as code | Pipeline stored in Git | Git में रखी pipeline |
| run-name | Title of each run | हर run का शीर्षक |
| concurrency | Limits parallel runs | parallel runs की सीमा |
| CODEOWNERS | File naming required reviewers | ज़रूरी reviewers की file |

---

## ⚡ 3-Line Summary
English: A workflow is a YAML file in `.github/workflows/` that defines events, jobs and steps.
It is versioned in Git, reviewed like code, and every execution is a numbered run.
Protect workflow files because they can reach your secrets.

Hindi: Workflow `.github/workflows/` में YAML file है जो events, jobs और steps तय करती है।
यह Git में version होती है, code की तरह review होती है और हर execution एक numbered run है।
Workflow files की सुरक्षा करें क्योंकि ये आपके secrets तक पहुँच सकती हैं।

---

## ➡️ Next Topic
**235. Event — What triggers workflow** — the `on:` side: push, pull_request, schedule and more, and how GitHub decides which workflow to start.

---
