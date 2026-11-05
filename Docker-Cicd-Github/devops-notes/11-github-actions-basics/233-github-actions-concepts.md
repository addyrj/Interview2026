# 233. GitHub Actions Concepts
# हिंदी में: GitHub Actions की मूल अवधारणाएँ

---

## 🔵 Simple Definition (English)
GitHub Actions has six core building blocks: **workflow** (the YAML file), **event** (what triggers it), **job** (a group of steps on one machine), **step** (one command or action), **action** (a reusable step) and **runner** (the machine that runs jobs). Once you know how these six nest together, every pipeline becomes easy to read.

## 🔵 सरल परिभाषा (Hindi)
GitHub Actions के छह मूल building blocks हैं: **workflow** (YAML file), **event** (क्या उसे चलाता है), **job** (एक machine पर steps का समूह), **step** (एक command या action), **action** (reusable step) और **runner** (जो machine job चलाती है)। इन छह का आपसी रिश्ता समझ लें तो कोई भी pipeline पढ़ना आसान हो जाता है।

---

## 🔴 Problem it Solves
Beginners open a workflow file, see `on`, `jobs`, `steps`, `uses`, `runs-on`, and cannot tell which word is a trigger, which is a machine and which is a command. They then write steps that assume files created in another job still exist (they do not), or put two jobs expecting them to share one disk.

A clear mental model prevents the most common beginner bugs: wrong nesting, wrong scope of files and variables, and wasted minutes from running everything in one giant job.

## 🔴 यह क्यों बना? (Hindi)
Beginner workflow file खोलता है, `on`, `jobs`, `steps`, `uses`, `runs-on` देखता है और समझ नहीं पाता कि कौन सा शब्द trigger है, कौन सा machine और कौन सा command। फिर वह ऐसे steps लिख देता है जो मानते हैं कि दूसरे job में बनी files अब भी मौजूद हैं (नहीं होतीं), या दो jobs से एक ही disk share होने की उम्मीद करता है।

साफ mental model सबसे आम beginner bugs रोकता है: गलत nesting, files और variables का गलत scope, और एक बड़े job में सब कुछ चलाने से बर्बाद minutes।

---

## 🟢 How it Works — Step by Step

```
Step 1 → An EVENT happens (push, pull_request, schedule, manual click)
Step 2 → GitHub finds every WORKFLOW file whose `on:` matches that event
Step 3 → For each workflow, GitHub creates a RUN
Step 4 → Each JOB in the run is queued for a RUNNER (fresh VM / container)
Step 5 → Jobs run in parallel, unless `needs:` makes one wait for another
Step 6 → Inside a job, STEPS run top to bottom on the same runner
Step 7 → A step either runs a shell command (`run:`) or calls an ACTION (`uses:`)
Step 8 → Run ends with success / failure, shown on the commit and PR
```

Nesting rule to memorise:

```
workflow (file)
 └── on: event(s)
 └── jobs
      └── job (1 runner each)
           └── steps
                └── step = run: command   OR   uses: action
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → कोई **event** होता है (push, pull_request, schedule, manual click)।
Step 2 → GitHub हर **workflow** file ढूँढता है जिसका `on:` उस event से match करे।
Step 3 → हर workflow के लिए एक **run** बनता है।
Step 4 → run के हर **job** को एक **runner** (नई VM / container) के लिए queue किया जाता है।
Step 5 → Jobs parallel चलते हैं, जब तक `needs:` एक को दूसरे का इंतज़ार न करवाए।
Step 6 → एक job के अंदर **steps** ऊपर से नीचे उसी runner पर चलते हैं।
Step 7 → हर step या तो shell command (`run:`) चलाता है या **action** (`uses:`) बुलाता है।
Step 8 → Run success / failure के साथ खत्म होता है और commit व PR पर दिखता है।

---

## 🟡 Real World Example
Zomato-style order service: on every pull request you want (a) lint, (b) unit tests, (c) a Docker build. These are three **jobs**: lint and test run in parallel on two runners, and the Docker build uses `needs: [lint, test]` so it starts only if both pass. Inside the test job, the **steps** are: checkout code (an **action**), set up Node (an **action**), `npm ci` (a **command**), `npm test` (a **command**).

## 🟡 Real Example Hindi mein
Zomato जैसी order service: हर pull request पर आप चाहते हैं (a) lint, (b) unit tests, (c) Docker build। ये तीन **jobs** हैं: lint और test दो runners पर parallel चलते हैं और Docker build `needs: [lint, test]` इस्तेमाल करता है, यानी दोनों pass हों तभी शुरू होता है। test job के अंदर **steps** हैं: code checkout (एक **action**), Node setup (एक **action**), `npm ci` (एक **command**), `npm test` (एक **command**)।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/concepts-basic.yml
name: Concepts Basic              # WORKFLOW name shown in the Actions tab
on:                               # EVENT section: what triggers this workflow
  push:                           # Event 1: someone pushes commits
    branches: [main]              # Only the main branch
  workflow_dispatch:              # Event 2: manual "Run workflow" button
jobs:                             # JOBS section: list of jobs
  hello:                          # JOB id (unique inside this file)
    runs-on: ubuntu-latest        # RUNNER label: GitHub-hosted Ubuntu VM
    steps:                        # STEPS of this job, in order
      - name: Say hello           # Optional human-readable step name
        run: echo "Hello from $GITHUB_WORKFLOW"   # COMMAND step; env var set by GitHub
      - name: Show runner OS      # Second step on the SAME machine
        run: echo "Running on $RUNNER_OS"          # RUNNER_OS is Linux here
      - uses: actions/checkout@v4 # ACTION step: reusable code (example version)
      - name: List repo files     # Works because checkout put files on this runner
        run: ls -la               # Shows repository content
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/concepts-advanced.yml
name: Concepts Advanced           # Workflow with 3 jobs and dependencies
on:
  pull_request:                   # Trigger on PRs
    branches: [main]              # ...targeting main
permissions:
  contents: read                  # Minimal token permission for all jobs
jobs:
  lint:                           # Job 1 runs on its own runner
    runs-on: ubuntu-latest        # Fresh VM
    steps:
      - uses: actions/checkout@v4 # Every job must checkout again: VMs are not shared
      - uses: actions/setup-node@v4 # Install Node
        with:
          node-version: 20        # Node 20
          cache: npm              # Cache npm downloads
      - run: npm ci               # Install
      - run: npm run lint         # Lint
  test:                           # Job 2 runs IN PARALLEL with lint
    runs-on: ubuntu-latest        # Another fresh VM
    steps:
      - uses: actions/checkout@v4 # Checkout again
      - uses: actions/setup-node@v4 # Node
        with:
          node-version: 20
          cache: npm
      - run: npm ci               # Install
      - run: npm test             # Test
      - uses: actions/upload-artifact@v4   # Pass data to later jobs via artifacts
        with:
          name: coverage          # Artifact name
          path: coverage/         # Folder to upload
  build:                          # Job 3 waits for the other two
    needs: [lint, test]           # Starts only if BOTH succeed
    runs-on: ubuntu-latest        # Another fresh VM
    steps:
      - uses: actions/checkout@v4 # Checkout again
      - uses: actions/download-artifact@v4 # Get files made in the test job
        with:
          name: coverage          # Same name as uploaded
          path: coverage/         # Where to place it
      - run: docker build -t myapi:${{ github.sha }} .   # Build image tagged with commit SHA
```

---

## 🟠 My Stack Integration
Map each concept onto your VPS deployment:

| Concept | In your project |
|---|---|
| Event | `push` to `main`, or a `v*` tag |
| Workflow | `deploy.yml` in `.github/workflows/` |
| Jobs | `test` -> `build-image` -> `deploy` |
| Steps | checkout, login to registry, `docker build`, `ssh` and `docker compose up -d` |
| Actions | `actions/checkout`, `docker/login-action`, `docker/build-push-action` |
| Runner | `ubuntu-latest` for build; your VPS is only an SSH target, not a runner |

```yaml
# .github/workflows/stack-concepts.yml
name: Stack Concepts              # Shows event/job/step in your own setup
on:
  push:
    branches: [main]              # Deploy path: main only
jobs:
  test:
    runs-on: ubuntu-latest        # Runner for tests
    steps:
      - uses: actions/checkout@v4 # Get Node.js API code
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci && npm test   # Fail fast on broken code
  deploy:
    needs: test                   # Never deploy if tests fail
    runs-on: ubuntu-latest        # Runner that will SSH out to VPS
    steps:
      - run: echo "ssh to VPS here, covered in later topics"   # Placeholder; real SSH deploy comes later
```

Security: each job gets its own short-lived `GITHUB_TOKEN`; limit it with `permissions:`. Secrets are available per step/job and are masked in logs.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting files from job A to exist in job B.
✅ Correct: Each job has a fresh runner. Use `actions/upload-artifact` / `download-artifact` or cache.

❌ Mistake 2: Forgetting `actions/checkout` in a job and then getting "package.json not found".
✅ Correct: Add `uses: actions/checkout@v4` as the first step of every job that needs the code.

❌ Mistake 3: Putting `uses:` and `run:` in the same step.
✅ Correct: A step is EITHER `uses` OR `run`, never both.

❌ Mistake 4: Assuming jobs run in file order.
✅ Correct: Jobs are parallel by default; add `needs:` for order.

---

## 🧠 Tricky Interview Question
"A step does `export TOKEN=abc` in one step, and the next step prints `$TOKEN` but gets an empty value. The runner is the same. Why?"

Answer: Each `run:` step starts a **new shell process**, so plain `export` dies with that shell. To pass a variable to later steps in the same job, append to the special file: `echo "TOKEN=abc" >> "$GITHUB_ENV"`. To pass a value to other jobs, use step `outputs` plus job `outputs`, then read them via `needs.<job>.outputs.<name>`. Never write real secrets to `GITHUB_ENV` unless they are already masked.

---

## ⚫ Interview Questions + Answers

Q1: Explain workflow, job, step in one line each.
A1: Workflow = one YAML file defining an automation. Job = a set of steps that runs on one runner. Step = a single command (`run`) or action (`uses`).

Q2: Do jobs share a filesystem?
A2: No. Each job runs on a new runner. Share data using artifacts, caches or job outputs.

Q3: Do steps in the same job share a filesystem?
A3: Yes, same machine and same workspace directory, but not the same shell session or exported variables.

Q4: How do you run jobs in order?
A4: With `needs:`. Without it, jobs run in parallel.

Q5: What is the difference between an action and a step?
A5: A step is a position in a job. An action is a reusable unit you call from a step using `uses:`.

---

## 🔷 When to Use + When Not to Use
✅ Split into multiple jobs when:
- Tasks can run in parallel (lint, test, security scan).
- Tasks need different runners (Linux build, Windows test).
- You want a deploy job gated by approvals / environments.

❌ Avoid splitting when:
- Tasks are tiny and share heavy setup (installing deps three times wastes minutes).
- You would need to move large build output between jobs by artifact for no benefit.

---

## 📊 Visual Diagram

```
EVENT (push / PR / cron / manual)
        |
        v
+--------------------- WORKFLOW (.yml) ----------------------+
|                                                            |
|  JOB lint --------+                                        |
|  (runner A)       |                                        |
|   step step step  +--> JOB build  (needs: lint, test)      |
|                   |    (runner C)                          |
|  JOB test --------+     step: uses action                  |
|  (runner B)             step: run command                  |
|   step step step                                           |
+------------------------------------------------------------+
        |
        v
   result on commit / PR
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Workflow | YAML automation file | automation की YAML file |
| Event | Trigger that starts a workflow | workflow शुरू करने वाला trigger |
| Job | Group of steps on one runner | एक runner पर steps का समूह |
| Step | One command or action | एक command या action |
| Action | Reusable step | दोबारा इस्तेमाल होने वाला step |
| Runner | Machine that runs a job | job चलाने वाली machine |
| Artifact | File passed between jobs | jobs के बीच भेजी गई file |

---

## ⚡ 3-Line Summary
English: Event triggers a workflow; a workflow has jobs; a job has steps; a step runs a command or an action.
Each job gets its own fresh runner, so share files with artifacts and order jobs with `needs`.
Learn this nesting once and every pipeline reads easily.

Hindi: Event workflow को चलाता है; workflow में jobs होते हैं; job में steps; step command या action चलाता है।
हर job को नया runner मिलता है, इसलिए files artifacts से share करें और क्रम `needs` से तय करें।
यह nesting एक बार समझ लें तो हर pipeline आसानी से पढ़ी जाती है।

---

## ➡️ Next Topic
**234. Workflow — What it is** — a close look at the workflow file itself: where it lives, naming, run lifecycle and how to read the Actions tab.

---
