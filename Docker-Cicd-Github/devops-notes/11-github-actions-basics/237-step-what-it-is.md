# 237. Step — What it is
# हिंदी में: Step — यह क्या है

---

## 🔵 Simple Definition (English)
A **step** is the smallest unit of work inside a job. Each step either runs a shell command (`run:`) or calls a reusable action (`uses:`). Steps in a job run one after another on the same runner and share the same workspace folder.

## 🔵 सरल परिभाषा (Hindi)
**Step** job के अंदर काम की सबसे छोटी इकाई है। हर step या तो shell command चलाता है (`run:`) या reusable action बुलाता है (`uses:`)। एक job के steps एक के बाद एक उसी runner पर चलते हैं और एक ही workspace folder share करते हैं।

---

## 🔴 Problem it Solves
A pipeline is a list of small actions: get code, install Node, install dependencies, test, build. If everything lives in one opaque shell script, a failure says only "script exited with 1". You cannot see which part was slow, cannot skip one part conditionally, and cannot reuse parts.

Steps give each action its own name, log group, timing, condition (`if`), environment and status, so debugging and optimisation become simple.

## 🔴 यह क्यों बना? (Hindi)
Pipeline छोटे कामों की सूची है: code लाओ, Node install करो, dependencies install करो, test, build। अगर सब कुछ एक अपारदर्शी shell script में हो तो failure बस "script exited with 1" बताती है। आप नहीं देख सकते कि कौन सा हिस्सा धीमा था, किसी हिस्से को शर्त पर skip नहीं कर सकते और हिस्सों को दोबारा इस्तेमाल नहीं कर सकते।

Steps हर काम को अपना नाम, log group, timing, शर्त (`if`), environment और status देते हैं, इसलिए debugging और optimisation आसान हो जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Runner starts the job and creates the workspace ($GITHUB_WORKSPACE)
Step 2 → Steps are read top to bottom
Step 3 → Before each step, `if:` is evaluated (default is success())
Step 4 → `run:` -> a new shell process starts and executes the commands
         `uses:` -> runner downloads the action and executes it
Step 5 → Exit code 0 = step success; non-zero = failure (job stops)
Step 6 → Output / env changes are saved through files:
         $GITHUB_OUTPUT, $GITHUB_ENV, $GITHUB_PATH, $GITHUB_STEP_SUMMARY
Step 7 → Later steps can read earlier results via `steps.<id>.outputs.<name>`
```

Useful step keys: `name`, `id`, `if`, `uses`, `run`, `with`, `env`, `shell`, `working-directory`, `continue-on-error`, `timeout-minutes`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Runner job शुरू करता है और workspace (`$GITHUB_WORKSPACE`) बनाता है।
Step 2 → Steps ऊपर से नीचे पढ़े जाते हैं।
Step 3 → हर step से पहले `if:` जाँचा जाता है (default `success()`)।
Step 4 → `run:` में नई shell process बनकर commands चलाती है; `uses:` में runner action download करके चलाता है।
Step 5 → Exit code 0 = सफल; non-zero = fail (job रुक जाता है)।
Step 6 → Output / env बदलाव files से सहेजे जाते हैं: `$GITHUB_OUTPUT`, `$GITHUB_ENV`, `$GITHUB_PATH`, `$GITHUB_STEP_SUMMARY`।
Step 7 → आगे के steps पिछले नतीजे `steps.<id>.outputs.<name>` से पढ़ सकते हैं।

---

## 🟡 Real World Example
Swiggy-style API CI steps, each visible as its own collapsible log group:
1. Checkout code (2 s)
2. Setup Node 20 with cache (4 s)
3. `npm ci` (25 s)
4. `npm run lint` (10 s)
5. `npm test` (40 s)
6. Upload coverage on failure only (`if: failure()`)
When the run is slow, you open the timings and see `npm ci` took 25 s: that tells you to add dependency caching, which you could never see in one big script.

## 🟡 Real Example Hindi mein
Swiggy जैसे API CI के steps, हर एक अलग collapsible log group में: 1. code checkout (2 s) 2. cache के साथ Node 20 setup (4 s) 3. `npm ci` (25 s) 4. `npm run lint` (10 s) 5. `npm test` (40 s) 6. सिर्फ failure पर coverage upload (`if: failure()`)। Run धीमा हो तो timings में दिखता है कि `npm ci` में 25 s लगे, यानी dependency caching जोड़नी चाहिए; यह एक बड़ी script में कभी दिखता नहीं।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/steps-basic.yml
name: Steps Basic                     # Workflow name
on: [push]                            # Trigger
jobs:
  demo:                               # One job
    runs-on: ubuntu-latest            # Runner
    steps:                            # List of steps, each starts with "-"
      - name: Checkout code           # Friendly name shown in logs
        uses: actions/checkout@v4     # "uses" = call a reusable action
      - name: Print date              # Another step
        run: date                     # "run" = shell command
      - name: Multi-line script       # Step with many commands
        run: |                        # "|" keeps newlines
          echo "Line 1"
          echo "Line 2"
          pwd
      - name: Use an id and output    # Step that produces an output
        id: greet                     # id lets later steps refer to this one
        run: echo "msg=hello" >> "$GITHUB_OUTPUT"   # Save output as key=value
      - name: Read the output         # Consumer step
        run: echo "${{ steps.greet.outputs.msg }}"  # Prints hello
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/steps-advanced.yml
name: Steps Advanced                  # Conditions, env, shells, summaries
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      CI: "true"                      # Job-level env for every step
    steps:
      - uses: actions/checkout@v4     # Source code
      - uses: actions/setup-node@v4
        with:
          node-version: 20            # Pin major version
          cache: npm                  # Cache npm
      - name: Install
        run: npm ci                   # Reproducible install
        working-directory: api        # Run inside api/ folder
      - name: Lint (may warn but not block)
        run: npm run lint
        working-directory: api
        continue-on-error: true       # Failure does not fail the job
      - name: Test with timeout
        run: npm test
        working-directory: api
        timeout-minutes: 10           # This step alone is limited to 10 min
        env:
          NODE_ENV: test              # Step-level env, only this step
      - name: Add custom PATH entry
        run: echo "$PWD/node_modules/.bin" >> "$GITHUB_PATH"   # PATH change for later steps
        working-directory: api
      - name: Write job summary
        if: always()                  # Run even if earlier steps failed
        run: |
          echo "### Build finished" >> "$GITHUB_STEP_SUMMARY"           # Markdown shown on run page
          echo "Commit: ${GITHUB_SHA::7}" >> "$GITHUB_STEP_SUMMARY"     # Short SHA
      - name: Upload logs on failure
        if: failure()                 # Only when something failed
        uses: actions/upload-artifact@v4
        with:
          name: debug-logs            # Artifact name
          path: api/npm-debug.log*    # Files to save (may not exist; add if-no-files-found if needed)
          if-no-files-found: ignore   # Do not error if no log exists
      - name: Strict bash
        shell: bash                   # Explicit shell
        run: |
          set -euo pipefail           # Fail on error, unset var, or pipe failure
          echo "strict mode on"
```

---

## 🟠 My Stack Integration
Typical step sequence to build and deploy the Dockerised Node.js API to a VPS:

```yaml
# .github/workflows/stack-steps.yml
name: Stack Steps
on:
  push:
    branches: [main]
jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4                 # 1. Get source
      - uses: actions/setup-node@v4               # 2. Node toolchain
        with: { node-version: 20, cache: npm }
      - run: npm ci                               # 3. Install exact deps
      - run: npm test                             # 4. Run tests
      - name: Build Docker image (no push yet)    # 5. Verify Dockerfile builds
        run: docker build -t myapi:${{ github.sha }} .   # Tag with commit SHA
      - name: Smoke test the container            # 6. Run container, hit health URL
        run: |
          docker run -d --name api -p 3000:3000 myapi:${{ github.sha }}
          for i in $(seq 1 15); do curl -fs http://localhost:3000/health && exit 0; sleep 2; done
          docker logs api
          exit 1
```

Security: do not `echo` secrets; GitHub masks registered secrets but derived values (base64 of a secret) may leak. Use `set -x` carefully since it prints commands. Pin third-party `uses:` to commit SHA for sensitive pipelines.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `export VAR=1` in one step and reading it in the next.
✅ Correct: `echo "VAR=1" >> "$GITHUB_ENV"`.

❌ Mistake 2: Using `uses` and `run` in the same step.
✅ Correct: Two separate steps.

❌ Mistake 3: `cd folder` in one step and expecting the next step to be inside it.
✅ Correct: Use `working-directory:` on each step or `defaults.run.working-directory`.

❌ Mistake 4: Piping a failing command into another (`npm test | tee out.txt`) and missing the failure.
✅ Correct: Default `bash -e` shell for `run:` has `pipefail` when `shell: bash` is explicit; otherwise add `set -o pipefail`.

---

## 🧠 Tricky Interview Question
"A step runs `npm test || true`. The tests fail but the job is green. Another engineer replaced it with `continue-on-error: true`. What is the difference?"

Answer: `|| true` hides the exit code **inside the shell**, so the step is reported successful (green check) and later `if: failure()` steps never fire. `continue-on-error: true` lets the job continue but the step outcome is still recorded as `failure` (`steps.x.outcome == 'failure'`, while `conclusion` is `success`), and the UI shows a warning. The second is more transparent and queryable, but remember the job's final result stays success.

---

## ⚫ Interview Questions + Answers

Q1: What are the two kinds of steps?
A1: `run` steps execute shell commands; `uses` steps execute an action (from a repo, Marketplace, Docker image or local path).

Q2: Do steps in one job share environment variables set with `export`?
A2: No, each `run` step is a new shell. Use `$GITHUB_ENV` for env, `$GITHUB_OUTPUT` for outputs, `$GITHUB_PATH` for PATH.

Q3: How do you make a step run only on failure?
A3: `if: failure()`. Other status functions: `success()`, `always()`, `cancelled()`.

Q4: What is the default shell for `run` on Linux?
A4: `bash -e {0}` when `shell` is not set (falls back to `sh` if bash is unavailable). Explicit `shell: bash` adds `-eo pipefail`.

Q5: How can a step set a job summary?
A5: Append Markdown to `$GITHUB_STEP_SUMMARY`.

---

## 🔷 When to Use + When Not to Use
✅ Use many small steps when:
- You want clear logs, timings and conditional execution.
- Each task has a clear name (install, lint, test, build).

❌ Avoid when:
- A 100-line inline script belongs in a repo file (`scripts/deploy.sh`) that you can test locally and call from one step.
- You duplicate the same 5 steps in many workflows; build a composite action.

---

## 📊 Visual Diagram

```
JOB (runner VM)
 workspace: /home/runner/work/repo/repo
 |
 +--[1] uses: actions/checkout@v4      -> code appears in workspace
 +--[2] uses: actions/setup-node@v4    -> node on PATH
 +--[3] run:  npm ci                   -> node_modules created
 +--[4] run:  npm test                 -> exit code 0 / non-zero
 +--[5] if: failure()  run: upload logs
 |
 files shared between steps: workspace, $GITHUB_ENV, $GITHUB_PATH, $GITHUB_OUTPUT
 NOT shared: shell variables, cwd changes (cd), exported vars
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Step | Smallest unit in a job | job की सबसे छोटी इकाई |
| run | Execute shell command | shell command चलाना |
| uses | Call an action | action बुलाना |
| id | Name to reference a step | step का संदर्भ नाम |
| GITHUB_OUTPUT | File to save step outputs | step outputs की file |
| GITHUB_ENV | File to set env for later steps | आगे के steps के लिए env |
| continue-on-error | Do not fail job on step failure | step fail पर भी job जारी |

---

## ⚡ 3-Line Summary
English: A step is one command (`run`) or one action (`uses`) inside a job, run in order on one runner.
Each `run` is a fresh shell, so pass data using GITHUB_ENV / GITHUB_OUTPUT.
Use `if`, `id`, `working-directory` and `continue-on-error` to control flow.

Hindi: Step job के अंदर एक command (`run`) या एक action (`uses`) है जो क्रम से चलता है।
हर `run` नई shell है, इसलिए data GITHUB_ENV / GITHUB_OUTPUT से भेजें।
Flow नियंत्रित करने के लिए `if`, `id`, `working-directory` और `continue-on-error` इस्तेमाल करें।

---

## ➡️ Next Topic
**238. Action — What it is** — the reusable building blocks you call with `uses:`: JavaScript, Docker and composite actions, versions and trust.

---
