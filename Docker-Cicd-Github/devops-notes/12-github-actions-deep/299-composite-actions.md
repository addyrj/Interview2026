# 299. Composite Actions
# हिंदी में: Composite Actions (steps का समूह एक action में)

---

## 🔵 Simple Definition (English)
A **composite action** is a custom action defined in an `action.yml` file with `runs.using: "composite"`. It bundles several **steps** (shell commands and other actions) into one reusable step. It runs inside the caller's job, on the caller's runner.

## 🔵 सरल परिभाषा (Hindi)
**Composite action** एक custom action है जो `action.yml` में `runs.using: "composite"` के साथ बनता है। यह कई **steps** (shell commands और दूसरी actions) को एक reusable step में बाँध देता है। यह caller की job के अंदर, caller के runner पर ही चलता है।

---

## 🔴 Problem it Solves
Every Node job in your repo repeats the same five steps: checkout, setup-node, cache, `npm ci`, build. Ten jobs means fifty copied lines; changing the Node version means ten edits. A reusable workflow is too heavy because you do not need a new runner, you just need a shared block of steps.

## 🔴 यह क्यों बना? (Hindi)
आपके repo की हर Node job वही पाँच steps दोहराती है: checkout, setup-node, cache, `npm ci`, build। दस jobs का मतलब पचास copied lines; Node version बदलने के लिए दस edits। Reusable workflow यहाँ भारी है क्योंकि नया runner नहीं चाहिए, सिर्फ steps का साझा block चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Make folder  .github/actions/setup-node-app/
Step 2 → Create action.yml inside with name, description, inputs, outputs
Step 3 → Set  runs: using: "composite"  and list steps:
Step 4 → Every `run:` step MUST declare  shell: bash  (or pwsh, python...)
Step 5 → Use inputs via ${{ inputs.name }}; set outputs via $GITHUB_OUTPUT
Step 6 → Caller job:  - uses: ./.github/actions/setup-node-app
         (checkout must happen BEFORE for local path actions)
Step 7 → Composite steps run in the same job, same filesystem, same runner
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → फ़ोल्डर बनाओ  .github/actions/setup-node-app/
Step 2 → अंदर action.yml बनाओ: name, description, inputs, outputs
Step 3 → runs: using: "composite" रखो और steps: लिखो
Step 4 → हर `run:` step में  shell: bash  देना ज़रूरी है
Step 5 → inputs ${{ inputs.name }} से पढ़ो; outputs $GITHUB_OUTPUT से set करो
Step 6 → Caller job में:  - uses: ./.github/actions/setup-node-app
         (local path वाली action के लिए पहले checkout ज़रूरी है)
Step 7 → Composite steps उसी job, उसी filesystem, उसी runner पर चलते हैं
```

---

## 🟡 Real World Example
A Pune e-commerce team has 8 jobs that all need "Node 20 + npm cache + `npm ci`". They create `.github/actions/node-setup`. Now `lint`, `test`, `build`, `e2e` each have one `uses:` line. When they move to Node 22, they edit one file. They also publish the action in a separate repo (`acme/actions/node-setup@v1`) so the other 10 repos can use it.

## 🟡 Real Example Hindi mein
Pune की एक e-commerce team की 8 jobs को "Node 20 + npm cache + `npm ci`" चाहिए। वे `.github/actions/node-setup` बनाते हैं। अब `lint`, `test`, `build`, `e2e` में हर एक में सिर्फ एक `uses:` line है। Node 22 पर जाना हो तो एक ही file बदलनी है। वे इसे अलग repo (`acme/actions/node-setup@v1`) में publish भी करते हैं ताकि बाकी 10 repos भी इस्तेमाल करें।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/actions/hello/action.yml
name: "Hello Composite"                 # display name
description: "Prints a greeting"        # required field
inputs:
  who:                                  # input name
    description: "Name to greet"
    required: false                     # optional
    default: "world"                    # default value
runs:
  using: "composite"                    # marks this as a composite action
  steps:
    - name: Say hello
      shell: bash                       # REQUIRED for every run step
      run: echo "Hello ${{ inputs.who }}"   # uses the input
```

```yaml
# .github/workflows/demo.yml  (caller)
name: Demo
on: [push]                              # run on every push
jobs:
  greet:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4       # needed to find ./.github/actions/hello
      - uses: ./.github/actions/hello   # local composite action
        with:
          who: "DevOps"                 # override default input
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/actions/node-setup/action.yml
name: "Node setup + install"
description: "Setup Node, restore npm cache, install deps, report cache hit"
author: "platform-team"

inputs:
  node-version:
    description: "Node version"
    required: false
    default: "20"
  working-directory:
    description: "Folder containing package.json"
    required: false
    default: "."
  install-command:
    description: "Install command"
    required: false
    default: "npm ci"                   # lockfile-exact, good for CI

outputs:
  cache-hit:                            # output exposed to the caller
    description: "true if npm cache restored"
    value: ${{ steps.cache.outputs.cache-hit }}   # map from step output
  node-version-used:
    description: "Actual Node version"
    value: ${{ steps.ver.outputs.version }}

runs:
  using: "composite"
  steps:
    - uses: actions/setup-node@v4       # actions can be used inside composite
      with:
        node-version: ${{ inputs.node-version }}   # pass input down

    - id: cache                         # id so outputs can be mapped
      uses: actions/cache@v4            # cache npm download dir
      with:
        path: ~/.npm                    # npm cache folder on Linux runner
        key: npm-${{ runner.os }}-${{ hashFiles(format('{0}/package-lock.json', inputs.working-directory)) }}
        restore-keys: |                 # fallback keys
          npm-${{ runner.os }}-

    - name: Install dependencies
      shell: bash                       # mandatory
      working-directory: ${{ inputs.working-directory }}   # run in subfolder
      run: ${{ inputs.install-command }}   # CAUTION: input is executed as shell

    - id: ver                           # record version for later steps
      shell: bash
      run: echo "version=$(node -v)" >> "$GITHUB_OUTPUT"   # set output

    - name: Summary
      shell: bash
      run: |                            # write a short job summary
        echo "Node ${{ steps.ver.outputs.version }}, cache-hit=${{ steps.cache.outputs.cache-hit }}" >> "$GITHUB_STEP_SUMMARY"
```

```yaml
# caller using it in 3 jobs
name: CI
on: [pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4          # checkout first
      - id: setup
        uses: ./.github/actions/node-setup # our composite
        with:
          working-directory: web           # React app folder
      - run: npm run lint
        working-directory: web
      - run: echo "cache hit was ${{ steps.setup.outputs.cache-hit }}"
```

---

## 🟠 My Stack Integration
- **Node.js / React:** `node-setup` composite shared by `lint`, `test`, `build` jobs.
- **FastAPI:** a second composite `python-setup` (setup-python + pip cache + `pip install -r requirements.txt`).
- **Nginx / VPS:** a composite `ssh-deploy` that writes the key, runs `ssh ... docker compose up -d`, and always removes the key file (the last step cannot use `if: always()` as a cleanup guarantee on cancellation, so keep key in `$RUNNER_TEMP`).
- **AWS:** composite `aws-login` wrapping `aws-actions/configure-aws-credentials` with your role ARN default.

```yaml
# .github/actions/python-setup/action.yml  (FastAPI helper)
name: "Python setup"
description: "Python + pip cache + install"
inputs:
  python-version:
    description: "Python version"
    default: "3.12"                        # example, update as needed
runs:
  using: "composite"
  steps:
    - uses: actions/setup-python@v5        # installs Python
      with:
        python-version: ${{ inputs.python-version }}
        cache: pip                         # built-in pip cache
    - shell: bash                          # required
      run: pip install -r requirements.txt # install FastAPI deps
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `shell:` on a `run` step. The action fails validation.
✅ Correct: Always add `shell: bash` (or another shell) to each `run` step.

❌ Mistake 2: Using `./.github/actions/x` before `actions/checkout`. The folder does not exist yet.
✅ Correct: Checkout first, or use a remote reference `acme/actions/x@v1`.

❌ Mistake 3: Reading `secrets.X` directly in a composite action. Secrets context is not available there.
✅ Correct: Declare an input (`token`) and pass `with: token: ${{ secrets.X }}` from the caller.

❌ Mistake 4: Assuming the caller's step-level `env:` and `if:` behave like inside a normal job for inner steps.
✅ Correct: Pass values as explicit inputs, and test the behavior in a small demo workflow.

❌ Mistake 5: Running `${{ inputs.x }}` directly inside `run:` with untrusted values (script injection).
✅ Correct: Map input into `env:` and use `"$VAR"` in the script.

---

## 🧠 Tricky Interview Question
**Q:** Your composite action has 5 steps, and step 3 fails. In the workflow UI you see only one step ("Run ./.github/actions/node-setup"). How do you debug, and does the caller continue?

**Answer:** The caller step fails as a whole and the job stops (unless `continue-on-error: true` on the caller step). Inner steps are still shown as grouped log sections inside that step. To debug, enable step debug logging (secret `ACTIONS_STEP_DEBUG=true`) and add `name:` to every inner step. Inner steps do support `if:`, `id:`, `name:` and `working-directory:`.

---

## ⚫ Interview Questions + Answers

Q1: Composite action vs reusable workflow?
A1: Composite = steps, runs inside caller's job and runner, referenced at step level. Reusable workflow = jobs, own runners, secrets and environments, referenced at job level. Composite cannot define `runs-on`, `services`, or matrix.

Q2: Why is `shell` required?
A2: Normal workflow steps default to the runner's shell; in composite actions the runner platform is unknown at definition time, so you must say which shell to use explicitly.

Q3: How do you return an output from a composite action?
A3: Write `name=value` to `$GITHUB_OUTPUT` in a step with an `id`, then declare `outputs.<name>.value: ${{ steps.<id>.outputs.<name> }}` in `action.yml`.

Q4: Where can a composite action live?
A4: In the same repo (`./path`), or in another repo (`owner/repo/path@ref`), or at repo root of a dedicated public/private actions repo (`owner/repo@v1`). Private ones need Actions access sharing enabled.

Q5: Can a composite action use other composite actions?
A5: Yes, composite actions can call other actions including other composites, with nesting limits (check current docs for depth limit).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The same group of 3 to 10 steps repeats across jobs/repos
- You want inputs and outputs but no new runner
- You want a stable, versioned building block (`@v1`)

❌ Avoid when:
- You need separate runners, matrix, services or environments (use reusable workflow)
- You need complex logic, API calls, or heavy code (write a JavaScript/Docker action)
- The steps are used once

---

## 📊 Visual Diagram
```
 Caller job (ONE runner, ONE filesystem)
 +-----------------------------------------------------+
 | step 1: actions/checkout                            |
 | step 2: uses: ./.github/actions/node-setup  <-----+ |
 |            +--------------------------------+      | |
 |            | composite action.yml           |      | |
 |            |  - setup-node                  |      | |
 |            |  - cache                       |      | |
 |            |  - npm ci   (shell: bash)      |      | |
 |            |  outputs: cache-hit            |------+ |
 |            +--------------------------------+        |
 | step 3: npm test    (can read steps.setup.outputs)   |
 +-----------------------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `action.yml` | Metadata file of an action | action की metadata file |
| `using: composite` | Action type made of steps | steps से बनी action |
| `shell` | Shell for a run step; required | run step का shell |
| `inputs` / `outputs` | Parameters in / values out | अंदर आने / बाहर जाने वाले values |
| `$GITHUB_OUTPUT` | File to write step outputs | outputs लिखने की file |
| `$RUNNER_TEMP` | Temp dir cleaned per job | अस्थायी folder |

---

## ⚡ 3-Line Summary
English: A composite action packs several steps into one reusable step defined in `action.yml`.
It runs on the caller's runner, needs `shell:` on each `run` step, and takes inputs and gives outputs.
Use it for shared step blocks; use reusable workflows for whole jobs.
Hindi: Composite action कई steps को `action.yml` में एक reusable step बना देता है।
यह caller के runner पर चलता है, हर `run` step में `shell:` चाहिए, और inputs लेकर outputs देता है।
Shared step blocks के लिए इसे लें; पूरी jobs के लिए reusable workflow लें।

---

## ➡️ Next Topic
**300. Custom Actions (JS + Docker)** — when shell steps are not enough, you write a real action in JavaScript or a Docker container.
