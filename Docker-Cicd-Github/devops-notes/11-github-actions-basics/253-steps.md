# 253. steps:
# हिंदी में: steps: (job के अंदर क्रमवार काम)

---

## 🔵 Simple Definition (English)
`steps:` is the ordered list inside a job. Each step is either an **action** (`uses:`) or a **shell command** (`run:`). Steps run **sequentially on the same runner**, share the same filesystem and environment (via `GITHUB_ENV`, `GITHUB_PATH`), and can set outputs. If a step fails, the remaining steps are skipped unless they have a condition like `if: always()`.

## 🔵 सरल परिभाषा (Hindi)
`steps:` job के अंदर क्रमवार सूची है। हर step या तो **action** (`uses:`) होता है या **shell command** (`run:`)। Steps **एक ही runner पर क्रम से** चलते हैं, वही filesystem और environment साझा करते हैं (`GITHUB_ENV`, `GITHUB_PATH` से), और outputs दे सकते हैं। कोई step fail हो तो बाकी steps skip हो जाते हैं, जब तक `if: always()` जैसी शर्त न हो।

---

## 🔴 Problem it Solves
A pipeline is a sequence: get code, install tools, install dependencies, test, build, publish. Doing this in separate jobs wastes time re-creating the environment. Steps let you chain operations on one machine where files created by an earlier step are available to the next, while still giving each step its own log section, status, timing and conditions.

## 🔴 यह क्यों बना? (Hindi)
Pipeline एक क्रम है: code लाओ, tools install करो, dependencies install करो, test, build, publish। इन्हें अलग jobs में करने से हर बार environment बनाने में समय जाता है। Steps एक ही machine पर operations जोड़ने देते हैं जहाँ पिछले step की बनाई files अगले step को मिलती हैं, साथ ही हर step का अपना log section, status, समय और conditions रहते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Runner starts the job and creates the workspace dir ($GITHUB_WORKSPACE).
Step 2 → Steps execute top to bottom; each `run` step starts a NEW shell process (shell state does not persist).
Step 3 → Files in the workspace persist across steps. Env vars do not, unless written to $GITHUB_ENV.
Step 4 → Step outputs: `echo "k=v" >> $GITHUB_OUTPUT`, read via `${{ steps.<id>.outputs.k }}`.
Step 5 → A non-zero exit code fails the step and (by default) the job; later steps are skipped.
Step 6 → Conditions: `if: success()` (default) | `failure()` | `always()` | `cancelled()`.
Step 7 → After steps, "post" steps of actions run (e.g., cache save, cleanup) in reverse order.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Runner job शुरू करके workspace dir ($GITHUB_WORKSPACE) बनाता है।
Step 2 → Steps ऊपर से नीचे चलते हैं; हर `run` step नई shell process शुरू करता है (shell state नहीं बचती)।
Step 3 → Workspace की files steps के बीच बची रहती हैं। Env vars नहीं, जब तक $GITHUB_ENV में न लिखें।
Step 4 → Step outputs: `echo "k=v" >> $GITHUB_OUTPUT`, पढ़ना `${{ steps.<id>.outputs.k }}` से।
Step 5 → Non-zero exit code step (और default में job) fail करता है; बाद के steps skip।
Step 6 → Conditions: `if: success()` (default) | `failure()` | `always()` | `cancelled()`।
Step 7 → Steps के बाद actions के "post" steps (जैसे cache save, cleanup) उल्टे क्रम में चलते हैं।
```

Step keys: `name`, `id`, `if`, `uses`, `run`, `with`, `env`, `shell`, `working-directory`, `continue-on-error`, `timeout-minutes`.

---

## 🟡 Real World Example
A FastAPI team's job has steps: checkout, set up Python 3.12 with pip cache, install requirements, run `ruff`, run `pytest --cov`, upload coverage, build Docker image, and finally a step with `if: failure()` that posts the failing test name to Slack. When `pytest` fails, the build step is skipped but the Slack step still runs - because steps are conditional, not just linear.

## 🟡 Real Example Hindi mein
एक FastAPI team के job में steps हैं: checkout, pip cache के साथ Python 3.12 setup, requirements install, `ruff`, `pytest --cov`, coverage upload, Docker image build, और अंत में `if: failure()` वाला step जो fail हुए test का नाम Slack पर भेजता है। `pytest` fail हो तो build step skip होता है लेकिन Slack step फिर भी चलता है - क्योंकि steps सिर्फ़ क्रमवार नहीं, conditional भी होते हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/steps-basic.yml
name: Steps Basic                         # workflow name
on: [push]                                # trigger

jobs:
  demo:                                   # job id
    runs-on: ubuntu-latest                # runner
    steps:                                # ordered list
      - uses: actions/checkout@v4         # step 1: action - clone repo into workspace
      - name: Create a file               # step 2: run command, with a label
        run: echo "hello" > note.txt      # write a file in the workspace
      - name: Read the file               # step 3: sees file from step 2 (same runner)
        run: cat note.txt                 # prints "hello"
      - name: Runs only on failure        # step 4: conditional step
        if: failure()                     # skipped when everything above succeeded
        run: echo "something failed"
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/steps-advanced.yml
name: Steps Advanced
on:
  pull_request:
    branches: [main]

jobs:
  api:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    defaults:
      run:
        shell: bash                       # explicit shell (bash -e -o pipefail used by default for 'bash')
        working-directory: api            # all run steps start here
    steps:
      - uses: actions/checkout@v4         # source code
        with:
          fetch-depth: 0                  # full history (for version/changelog tools)

      - id: pyver                         # id lets later steps read its outputs
        name: Detect Python version
        working-directory: .              # override default for this step
        run: |
          v=$(cat .python-version)        # file in repo root with e.g. 3.12
          echo "version=$v" >> "$GITHUB_OUTPUT"   # publish as step output

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ steps.pyver.outputs.version }}   # consume previous step output
          cache: pip                      # cache pip downloads
          cache-dependency-path: api/requirements.txt

      - name: Set env for following steps
        run: |
          echo "APP_ENV=test" >> "$GITHUB_ENV"        # persists to later steps
          echo "$HOME/.local/bin" >> "$GITHUB_PATH"   # add to PATH for later steps

      - run: pip install -r requirements.txt          # install deps

      - name: Lint
        run: ruff check .                 # fails the job on lint errors

      - name: Tests
        id: tests
        continue-on-error: false          # explicit: failure stops the job
        run: pytest --maxfail=1 -q --junitxml=report.xml   # run tests, create report

      - name: Upload report (even if tests failed)
        if: always()                      # run no matter what happened before
        uses: actions/upload-artifact@v4
        with:
          name: junit-report
          path: api/report.xml            # path is relative to workspace root
          if-no-files-found: ignore       # do not fail when tests crashed before writing

      - name: Alert on failure
        if: failure()                     # only if a previous step failed
        env:
          WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: |
          curl -sS -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"PR #${{ github.event.pull_request.number }} failed on ${{ github.job }}\"}" "$WEBHOOK"
```

(YAML parsed locally; not executed on GitHub.)

---

## 🟠 My Stack Integration
- **Node.js:** checkout -> setup-node (cache) -> `npm ci` -> lint -> test -> build.
- **FastAPI:** checkout -> setup-python -> pip install -> ruff -> pytest -> docker build.
- **React:** `npm ci` -> `npm run build` -> upload-artifact (`dist`).
- **Nginx/VPS/AWS:** last steps do `rsync`, `ssh`, `aws ecs update-service`, followed by a smoke test step `curl --fail https://app.example.com/health`.

```yaml
# Smoke test step after deploy, with retries; fails the job (and triggers rollback logic) if unhealthy
- name: Smoke test
  run: |
    for i in 1 2 3 4 5 6; do                        # up to 6 attempts
      if curl --fail --silent --show-error https://app.example.com/health; then exit 0; fi   # success exits
      sleep 10                                      # wait for containers to warm up
    done
    exit 1                                          # all attempts failed
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `cd api` in one step and expecting the next step to be in `api/`.
✅ Correct: Use `working-directory:` or `defaults.run.working-directory`; every step starts in the workspace.

❌ Mistake 2: `export TOKEN=x` in one step and using it in the next.
✅ Correct: `echo "TOKEN=x" >> "$GITHUB_ENV"` (never for secrets you cannot mask).

❌ Mistake 3: Setting outputs with the removed `::set-output` command.
✅ Correct: Append to `$GITHUB_OUTPUT`.

❌ Mistake 4: Missing `if: always()` on artifact upload, so logs are lost exactly when tests fail.
✅ Correct: Add `if: always()` to diagnostics steps.

❌ Mistake 5: Using `continue-on-error: true` broadly and hiding real failures.
✅ Correct: Use it only for non-critical steps (optional linters, notifications).

---

## 🧠 Tricky Interview Question
Step 3 fails; step 5 has `if: always()` and step 6 has no `if`. What runs, and what is the job conclusion?

Answer: Step 4 (no `if`, default `success()`) is skipped, step 5 runs, step 6 is skipped because the implicit condition `success()` is false after a failure. The job conclusion is failure, even if step 5 succeeds. `always()` also runs when the workflow is cancelled; for "run unless cancelled" use `!cancelled()`.

---

## ⚫ Interview Questions + Answers

Q1: Do steps share environment variables?
A1: No by default; each `run` step has its own shell. Persist with `$GITHUB_ENV`. Job/workflow-level `env:` is available to all steps.

Q2: Do steps share the filesystem?
A2: Yes, the workspace and the runner disk are shared by all steps of the job.

Q3: Max number of steps?
A3: Practical limits exist (docs mention up to 1,000 steps per job, verify current docs).

Q4: How do I run a step only on `main`?
A4: `if: github.ref == 'refs/heads/main'`.

Q5: `continue-on-error` vs `if: always()`?
A5: `continue-on-error: true` lets THIS step fail without failing the job. `if: always()` makes a step RUN even after failures; job still fails because of the earlier failure.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Operations need the same files/tools (install -> test -> build).
- You want per-step logs, timing and conditions.

❌ Avoid when:
- Parts can run in parallel or need different runners/permissions (use separate jobs).
- Logic is duplicated across repos (wrap into composite action / reusable workflow).

---

## 📊 Visual Diagram

```
 job (one runner, one workspace)
 ┌──────────────────────────────────────────────────────────┐
 │ 1 checkout ✔ → 2 setup-python ✔ → 3 pytest ✘             │
 │                                        │                 │
 │ 4 build  (success())  ── skipped ◄─────┤                 │
 │ 5 upload report (always())  ── RUNS ◄──┤                 │
 │ 6 deploy (success())  ── skipped ◄─────┤                 │
 │ 7 alert  (failure())  ── RUNS ◄────────┘                 │
 └──────────────────────────────────────────────────────────┘
                 job result: FAILURE
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| step | One unit of work in a job | Job की एक कार्य-इकाई |
| workspace | Folder where repo is checked out | Repo checkout वाला folder |
| GITHUB_ENV | File to persist env vars | Env vars बचाने वाली file |
| GITHUB_OUTPUT | File to set step outputs | Step outputs वाली file |
| status function | success/failure/always/cancelled | स्थिति functions |
| post step | Cleanup run after job steps | Job के बाद की सफ़ाई |

---

## ⚡ 3-Line Summary
English: Steps run in order on one runner, sharing files but not shell state.
English: Use `GITHUB_ENV`/`GITHUB_OUTPUT` to pass data, and `if` functions to control flow.
English: Add `if: always()` to diagnostics and `failure()` to alerts.
Hindi: Steps एक runner पर क्रम से चलते हैं, files साझा करते हैं पर shell state नहीं।
Hindi: Data के लिए `GITHUB_ENV`/`GITHUB_OUTPUT` और flow के लिए `if` functions।
Hindi: Diagnostics में `if: always()` और alerts में `failure()` लगाएँ।

---

## ➡️ Next Topic
**254. uses: (Action)** - how a step reuses community or custom actions, and how to pin them safely.
