# 242. Workflow YAML Structure
# हिंदी में: Workflow YAML की बनावट

---

## 🔵 Simple Definition (English)
A workflow YAML has a fixed skeleton: optional `name` and `run-name`, a required `on` (triggers), optional `env`, `defaults`, `permissions`, `concurrency`, and a required `jobs` map. Each job has `runs-on` and `steps`. Knowing this skeleton lets you read or write any workflow quickly.

## 🔵 सरल परिभाषा (Hindi)
Workflow YAML का एक तय ढाँचा है: वैकल्पिक `name` और `run-name`, ज़रूरी `on` (triggers), वैकल्पिक `env`, `defaults`, `permissions`, `concurrency`, और ज़रूरी `jobs` map। हर job में `runs-on` और `steps` होते हैं। यह ढाँचा जानने से आप कोई भी workflow जल्दी पढ़-लिख सकते हैं।

---

## 🔴 Problem it Solves
YAML is whitespace-sensitive and GitHub validates keys strictly. A single wrong indent or misspelled key (`step:` instead of `steps:`) gives errors like "Invalid workflow file" or, worse, silently skips the workflow. People waste hours because they do not know which keys belong at which level.

Understanding the levels (workflow -> job -> step) and the valid keys at each level removes guesswork.

## 🔴 यह क्यों बना? (Hindi)
YAML whitespace के प्रति संवेदनशील है और GitHub keys को सख्ती से जाँचता है। एक गलत indent या गलत spelling (`steps:` की जगह `step:`) से "Invalid workflow file" error आता है या workflow चुपचाप skip हो जाता है। लोग घंटों गँवाते हैं क्योंकि उन्हें पता नहीं होता कि कौन सी key किस स्तर पर आती है।

स्तर (workflow -> job -> step) और हर स्तर की मान्य keys समझने से अंदाज़ा लगाना खत्म हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → GitHub parses the YAML (syntax check)
Step 2 → Validates against the workflow schema (known keys, types)
Step 3 → Evaluates `on:` against the event
Step 4 → Builds a job graph from `needs`
Step 5 → Evaluates ${{ }} expressions at runtime (contexts: github, env, secrets, needs...)
Step 6 → Runs each job; steps inherit env/defaults from workflow and job
```

Skeleton with levels:

```
name / run-name                      (workflow, optional)
on                                   (REQUIRED)
env, defaults, permissions, concurrency   (workflow level, optional)
jobs                                 (REQUIRED)
  <job_id>:
    name, runs-on (REQUIRED), needs, if, permissions, env, defaults,
    outputs, strategy, services, container, environment, concurrency,
    timeout-minutes, continue-on-error
    steps (REQUIRED unless job uses a reusable workflow)
      - name, id, if, uses | run, with, env, shell, working-directory,
        continue-on-error, timeout-minutes
```

Precedence for `env`: step > job > workflow (closest wins). Permissions at job level override workflow level.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → GitHub YAML parse करता है (syntax जाँच)।
Step 2 → Workflow schema (ज्ञात keys, types) से validate करता है।
Step 3 → `on:` को event से मिलाता है।
Step 4 → `needs` से job graph बनाता है।
Step 5 → `${{ }}` expressions runtime पर evaluate होते हैं (contexts: github, env, secrets, needs...)।
Step 6 → हर job चलता है; steps workflow और job से env/defaults inherit करते हैं।

ऊपर skeleton दिया है: workflow स्तर पर `name`, `on`, `env`, `permissions`...; job स्तर पर `runs-on`, `needs`, `strategy`...; step स्तर पर `uses`/`run`, `with`, `env`... `env` में सबसे नज़दीकी वाला जीतता है (step > job > workflow)।

---

## 🟡 Real World Example
A new engineer at a Bengaluru startup joins and must fix a failing deploy. Because every workflow follows the same skeleton, they open `deploy.yml`, jump to `jobs.deploy.steps`, see the `env:` at job level overriding the workflow `env:`, and find the bug in 5 minutes: the `NODE_ENV` was set to `development` at the job level. Without a mental map, the same file looks like a wall of text.

## 🟡 Real Example Hindi mein
Bengaluru के एक startup में नया engineer आता है और उसे fail हो रहा deploy ठीक करना है। हर workflow इसी ढाँचे पर है, इसलिए वह `deploy.yml` खोलता है, `jobs.deploy.steps` पर जाता है, देखता है कि job स्तर का `env:` workflow के `env:` को override कर रहा है, और 5 मिनट में bug मिल जाता है: job स्तर पर `NODE_ENV` `development` था। नक्शे के बिना वही file text की दीवार लगती है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/structure-basic.yml
name: Structure Basic                 # [workflow] display name (optional)
on:                                   # [workflow] REQUIRED triggers
  push:
    branches: [main]
env:                                  # [workflow] env visible to all jobs
  APP_NAME: myapi                     # Plain value
jobs:                                 # [workflow] REQUIRED map of jobs
  build:                              # [job] id
    runs-on: ubuntu-latest            # [job] REQUIRED runner
    env:
      NODE_ENV: test                  # [job] env overrides workflow env of same name
    steps:                            # [job] REQUIRED list of steps
      - name: Checkout                # [step] optional name
        uses: actions/checkout@v4     # [step] call an action
      - name: Print variables         # [step]
        run: echo "$APP_NAME in $NODE_ENV"   # [step] shell command
        env:
          NODE_ENV: step-level        # [step] closest scope wins -> prints "myapi in step-level"
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/structure-advanced.yml
name: Structure Advanced              # Every major key in one file
run-name: Deploy ${{ inputs.target || 'auto' }} by ${{ github.actor }}   # Dynamic run title
on:
  push:
    branches: [main]
    tags: ["v*"]
  workflow_dispatch:
    inputs:
      target:                         # Input shown in UI
        description: Target environment
        type: choice
        options: [staging, production]
        default: staging
env:
  REGISTRY: ghcr.io                   # Shared constant
permissions:
  contents: read                      # Workflow default: read only
concurrency:
  group: deploy-${{ github.ref }}     # Serialize by ref
  cancel-in-progress: false           # Do not kill running deploys
defaults:
  run:
    shell: bash                       # Default shell for all run steps
jobs:
  test:
    name: Test (Node ${{ matrix.node }})   # Dynamic job name
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    strategy:
      fail-fast: true                 # Stop other legs on first failure
      matrix:
        node: [20, 22]                # Parallel versions
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: npm
      - run: npm ci && npm test
  build:
    needs: test                       # Dependency
    runs-on: ubuntu-24.04
    permissions:
      contents: read
      packages: write                 # Job-level permission override: only this job can push packages
    outputs:
      image_tag: ${{ steps.tag.outputs.value }}   # Expose to later jobs
    steps:
      - uses: actions/checkout@v4
      - id: tag
        run: echo "value=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"   # Short SHA
      - run: echo "build and push ${{ env.REGISTRY }}/${{ github.repository }}:${{ steps.tag.outputs.value }}"
  deploy:
    needs: build
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v')   # Run only on main or tags
    runs-on: ubuntu-24.04
    environment: ${{ inputs.target || 'staging' }}   # Environment name from input
    steps:
      - run: echo "deploy ${{ needs.build.outputs.image_tag }} to ${{ inputs.target || 'staging' }}"
```

---

## 🟠 My Stack Integration
A clean template for your repo with Node.js API, FastAPI, React and a VPS:

```yaml
# .github/workflows/stack-structure.yml
name: Stack Pipeline                  # One readable pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
env:
  NODE_VERSION: "20"                  # Single place to bump Node
  PYTHON_VERSION: "3.12"              # Single place to bump Python
permissions:
  contents: read
jobs:
  api:
    runs-on: ubuntu-24.04
    defaults:
      run:
        working-directory: api        # All run steps in this job start in api/
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}    # env context in with:
          cache: npm
          cache-dependency-path: api/package-lock.json
      - run: npm ci && npm test
  fastapi:
    runs-on: ubuntu-24.04
    defaults:
      run:
        working-directory: fastapi
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
      - run: pip install -r requirements.txt && pytest
  web:
    runs-on: ubuntu-24.04
    defaults:
      run:
        working-directory: web
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: web/package-lock.json
      - run: npm ci && npm run build
```

Security: set `permissions` explicitly at the top; never place secrets in workflow-level `env` unless every job needs them (they then become visible to every step, including third-party actions). Prefer step-level or job-level `env` for secrets.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Wrong indentation, e.g. `steps:` at the same level as `runs-on` but with list items misaligned.
✅ Correct: 2 spaces per level; list items start with `- ` aligned under `steps:`.

❌ Mistake 2: Writing `on: push` and then adding filters on the next line without nesting.
✅ Correct: Use the map form: `on:` -> `push:` -> `branches: [main]`.

❌ Mistake 3: Unquoted values YAML misreads: `node-version: 20.10` (float) or `on: yes`.
✅ Correct: Quote ambiguous values: `"3.10"`, `"20"`.

❌ Mistake 4: Using `${{ }}` in `if:` plus extra quoting that turns it into always-true string.
✅ Correct: `if: github.ref == 'refs/heads/main'` (no braces needed) or fully wrap with braces and no extra text.

---

## 🧠 Tricky Interview Question
"You set `python-version: 3.10` in YAML and CI installs Python 3.1. Why?"

Answer: YAML parses `3.10` as the floating-point number 3.1 (trailing zero dropped). Quote it: `python-version: "3.10"`. The same trap hits `node-version: 20.10` less often but versions like `1.10` anywhere. Rule: always quote versions that look like decimals.

---

## ⚫ Interview Questions + Answers

Q1: Which top-level keys are required?
A1: `on` and `jobs`. Each job needs `runs-on` and `steps` (or `uses` for a reusable workflow).

Q2: What is the precedence of `env`?
A2: Step overrides job overrides workflow.

Q3: What does `defaults.run` do?
A3: Sets default `shell` and `working-directory` for `run` steps at workflow or job level.

Q4: Where do `permissions` go and what is the effect?
A4: Workflow level or job level; job-level replaces (not merges) the workflow-level set for that job. Unlisted permissions become `none`.

Q5: How do you reuse values across jobs?
A5: Workflow-level `env` for constants, `vars` for repo/org variables, job `outputs` for runtime values.

---

## 🔷 When to Use + When Not to Use
✅ Use defaults/env/permissions at top when:
- Many jobs share the same values or restrictions.

❌ Avoid when:
- A value is secret or used by one step only (scope it narrowly).
- The file becomes huge; split into reusable workflows or composite actions.

---

## 📊 Visual Diagram

```
workflow.yml
├── name / run-name
├── on ───────────── triggers
├── env / defaults / permissions / concurrency   (inherited downward)
└── jobs
    ├── job A
    │   ├── runs-on, needs, if, env, strategy, services
    │   └── steps
    │       ├── step 1  (uses | run, with, env, id, if)
    │       └── step 2
    └── job B (needs: A)
        └── steps ...
env precedence:  step  >  job  >  workflow
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| on | Trigger definition | trigger की परिभाषा |
| jobs | Map of jobs | jobs का map |
| env | Environment variables | environment variables |
| defaults | Default shell/working dir | default shell/folder |
| permissions | GITHUB_TOKEN scopes | token की अनुमतियाँ |
| concurrency | Prevent overlapping runs | runs का overlap रोकना |
| Context | Data object used in `${{ }}` | `${{ }}` में प्रयुक्त data |

---

## ⚡ 3-Line Summary
English: A workflow has `on` and `jobs`; jobs have `runs-on` and `steps`; optional top keys set env, defaults, permissions and concurrency.
Scope narrows downward: workflow, job, step, with the closest `env` winning.
Quote version numbers and keep indentation consistent.

Hindi: Workflow में `on` और `jobs` होते हैं; jobs में `runs-on` और `steps`; वैकल्पिक keys env, defaults, permissions और concurrency तय करती हैं।
Scope नीचे की ओर सँकरा होता है: workflow, job, step, और सबसे नज़दीकी `env` जीतता है।
Version numbers को quotes में लिखें और indentation एक जैसी रखें।

---

## ➡️ Next Topic
**243. on: — Trigger Events** — the full `on:` syntax: lists, maps, filters, types and how multiple triggers combine.

---
