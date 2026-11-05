# 275. Default Environment Variables
# हिंदी में: Default Environment Variables (GitHub अपने-आप देता है)

---

## 🔵 Simple Definition (English)
Default environment variables are values GitHub sets automatically on every runner: `CI`, `GITHUB_ACTIONS`, `GITHUB_SHA`, `GITHUB_REF`, `GITHUB_REF_NAME`, `GITHUB_REPOSITORY`, `GITHUB_ACTOR`, `GITHUB_WORKSPACE`, `GITHUB_RUN_ID`, `RUNNER_OS` and more. You do not declare them; you just read them.

## 🔵 सरल परिभाषा (Hindi)
Default environment variables वे values हैं जो GitHub हर runner पर अपने-आप set करता है: `CI`, `GITHUB_ACTIONS`, `GITHUB_SHA`, `GITHUB_REF`, `GITHUB_REF_NAME`, `GITHUB_REPOSITORY`, `GITHUB_ACTOR`, `GITHUB_WORKSPACE`, `GITHUB_RUN_ID`, `RUNNER_OS` आदि। इन्हें declare नहीं करना पड़ता, सीधे पढ़ सकते हैं।

---

## 🔴 Problem it Solves
Scripts need to know "which commit, which branch, which repo, where is the checkout folder, am I on CI?" Without defaults you would pass them manually in every workflow. Having them in the environment lets plain shell scripts (`deploy.sh`, `npm run build`) work both locally and in CI.

## 🔴 यह क्यों बना? (Hindi)
Scripts को जानना होता है "कौन सा commit, कौन सी branch, कौन सा repo, checkout folder कहाँ है, क्या मैं CI पर हूँ?" Defaults के बिना हर workflow में ये manually pass करने पड़ते। Environment में होने से साधारण shell scripts (`deploy.sh`, `npm run build`) local और CI दोनों जगह चलती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Job starts on a runner
Step 2 → GitHub's runner sets GITHUB_* and RUNNER_* variables in the process env
Step 3 → Your run: script reads them as $GITHUB_SHA etc.
Step 4 → The same data exists in the github / runner contexts: ${{ github.sha }}
Step 5 → Special FILE variables (GITHUB_ENV, GITHUB_OUTPUT, GITHUB_PATH,
         GITHUB_STEP_SUMMARY) are paths you append to, to talk back to the runner
Step 6 → You cannot overwrite GITHUB_* / RUNNER_* by setting env (they are reserved)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Job runner पर start होता है
Step 2 → GitHub का runner process env में GITHUB_* और RUNNER_* variables set करता है
Step 3 → आपकी run: script इन्हें $GITHUB_SHA आदि की तरह पढ़ती है
Step 4 → यही data github / runner contexts में भी है: ${{ github.sha }}
Step 5 → खास FILE variables (GITHUB_ENV, GITHUB_OUTPUT, GITHUB_PATH,
         GITHUB_STEP_SUMMARY) ऐसे paths हैं जिनमें append करके runner से बात करते हैं
Step 6 → GITHUB_* / RUNNER_* को env से overwrite नहीं कर सकते (reserved हैं)
```

---

## 🟡 Real World Example
A deploy script on your VPS tags Docker images as `my-api:$GITHUB_SHA` and logs `$GITHUB_ACTOR` and `$GITHUB_RUN_ID` into a deploy log, so after a bad release the team sees exactly which commit, who and which run produced the running container. Rollback becomes "run `docker compose up` with the previous SHA".

## 🟡 Real Example Hindi mein
आपकी VPS की deploy script Docker images को `my-api:$GITHUB_SHA` tag देती है और `$GITHUB_ACTOR` व `$GITHUB_RUN_ID` को deploy log में लिखती है। खराब release के बाद team को ठीक पता चलता है कि कौन सा commit, किसने और कौन सा run उस चल रहे container के पीछे है। Rollback = पिछले SHA के साथ `docker compose up`।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/default-env-basic.yml
name: default-env-basic                # workflow name
on: [push, pull_request]               # triggers

jobs:
  show:
    runs-on: ubuntu-latest             # Linux runner
    steps:
      - name: Print defaults
        run: |                         # bash multi-line
          echo "CI=$CI"                              # always 'true' on GitHub
          echo "GITHUB_ACTIONS=$GITHUB_ACTIONS"      # 'true' on GitHub Actions
          echo "SHA=$GITHUB_SHA"                     # full 40-char commit SHA
          echo "REF=$GITHUB_REF"                     # refs/heads/main or refs/pull/1/merge
          echo "BRANCH=$GITHUB_REF_NAME"             # short name: main
          echo "REPO=$GITHUB_REPOSITORY"             # owner/repo
          echo "ACTOR=$GITHUB_ACTOR"                 # who triggered
          echo "EVENT=$GITHUB_EVENT_NAME"            # push / pull_request
          echo "RUN_ID=$GITHUB_RUN_ID"               # unique per run
          echo "RUN_NUMBER=$GITHUB_RUN_NUMBER"      # 1,2,3 ... per workflow
          echo "WORKSPACE=$GITHUB_WORKSPACE"         # checkout directory
          echo "RUNNER_OS=$RUNNER_OS"                # Linux / Windows / macOS
          echo "RUNNER_TEMP=$RUNNER_TEMP"            # temp dir cleaned per job
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/default-env-advanced.yml
name: default-env-advanced             # workflow name
on:
  push:
    branches: [main]                   # only main

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4      # example version; checks out into GITHUB_WORKSPACE

      - name: Compute metadata
        id: meta                       # allows steps.meta.outputs.*
        run: |
          SHORT="${GITHUB_SHA::7}"                         # first 7 chars (bash substring)
          echo "short=$SHORT" >> "$GITHUB_OUTPUT"          # pass to later steps
          echo "BUILD_ID=${GITHUB_RUN_NUMBER}-$SHORT" >> "$GITHUB_ENV"   # persists as env
          echo "$HOME/.local/bin" >> "$GITHUB_PATH"        # add folder to PATH for next steps

      - name: Use persisted value
        run: echo "build id is $BUILD_ID"                   # available because of GITHUB_ENV

      - name: Build image with metadata labels
        run: |
          docker build \
            --label "org.opencontainers.image.revision=$GITHUB_SHA" \
            --label "org.opencontainers.image.source=$GITHUB_SERVER_URL/$GITHUB_REPOSITORY" \
            -t "my-api:${{ steps.meta.outputs.short }}" .   # tag with short SHA
        # standard OCI labels let you trace any running image back to the commit

      - name: Job summary
        run: |
          {
            echo "### Build $BUILD_ID"                        # markdown heading
            echo "- commit: \`$GITHUB_SHA\`"                   # list item
            echo "- by: $GITHUB_ACTOR"
          } >> "$GITHUB_STEP_SUMMARY"                          # shows on the run page
```
Not run locally (no Docker daemon here); bash blocks syntax-checked, YAML parsed. Needs a Dockerfile in the repo root to actually build.

---

## 🟠 My Stack Integration
Use `CI=true` knowledge: many tools change behaviour (Create React App treats warnings as errors, Jest disables watch mode). Use `GITHUB_SHA` as image tag for Node.js and FastAPI images, and `GITHUB_REF_NAME` to select the VPS.

```yaml
# snippet: deploy by SHA over SSH (compose file reads IMAGE_TAG)
      - name: Deploy on VPS
        run: |
          ssh deploy@${{ vars.VPS_HOST }} \
            "cd /srv/app && IMAGE_TAG=$GITHUB_SHA docker compose up -d && sudo nginx -s reload"
        # $GITHUB_SHA is expanded LOCALLY on the runner before ssh sends the command
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `GITHUB_REF` as a branch name; on PRs it is `refs/pull/N/merge`.
✅ Correct: Use `GITHUB_HEAD_REF` (PR source branch) or `GITHUB_REF_NAME`, depending on the event.

❌ Mistake 2: Assuming `GITHUB_SHA` on a pull_request is the PR head commit; it is the temporary merge commit.
✅ Correct: Use `github.event.pull_request.head.sha` when you need the real head commit.

❌ Mistake 3: Trying `echo "GITHUB_SHA=abc" >> $GITHUB_ENV` to override it.
✅ Correct: Reserved names cannot be overridden; use a custom variable name.

❌ Mistake 4: Writing files to `/tmp` and assuming they persist across jobs.
✅ Correct: Use artifacts or cache; each job gets a fresh VM.

---

## 🧠 Tricky Interview Question
Why does `echo "BUILD=1" >> $GITHUB_ENV` not make `$BUILD` available in the SAME step?

Answer: `GITHUB_ENV` is read by the runner after the step finishes, and injected into the environment of subsequent steps. The current step process already started with its env. Use a normal `export BUILD=1` for the current step plus `$GITHUB_ENV` for later ones.

---

## ⚫ Interview Questions + Answers

Q1: Is `CI=true` set on GitHub Actions?
A1: Yes, always, together with `GITHUB_ACTIONS=true`.

Q2: Difference between `$GITHUB_SHA` and `${{ github.sha }}`?
A2: Same value. The first is read by bash at run time; the second is substituted by GitHub before the step starts and works in non-shell keys like `with:` and `if:`.

Q3: Which variable points to checked-out code?
A3: `GITHUB_WORKSPACE`, normally `/home/runner/work/<repo>/<repo>`.

Q4: What are `GITHUB_OUTPUT`, `GITHUB_PATH`, `GITHUB_STEP_SUMMARY`?
A4: File paths. Append `name=value` to GITHUB_OUTPUT for step outputs, a directory to GITHUB_PATH to extend PATH, markdown to GITHUB_STEP_SUMMARY to render a summary.

Q5: Can default variables be used in `if:`?
A5: Not as `$VAR`; `if:` is an expression, so use the contexts (`github.ref`, `runner.os`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tagging images and artifacts with SHA/run number.
- Writing portable scripts that behave differently under `CI`.
- Traceability in deploy logs.

❌ Avoid when:
- You need the value in a key evaluated by GitHub (`if`, `with`): use contexts.
- Trusting `GITHUB_ACTOR`/branch names as safe input in shell without quoting.

---

## 📊 Visual Diagram
```
 GitHub event (push)
        |
        v
 +-----------------------+
 | Runner VM             |
 |  CI=true              |
 |  GITHUB_SHA=ab12...   |
 |  GITHUB_REF_NAME=main |
 |  GITHUB_WORKSPACE=... |
 |  RUNNER_OS=Linux      |
 +-----------+-----------+
             |
   deploy.sh reads $GITHUB_SHA -> docker tag my-api:ab12...
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GITHUB_SHA | Commit that triggered the run | Run शुरू करने वाला commit |
| GITHUB_REF_NAME | Short branch/tag name | Branch/tag का छोटा नाम |
| GITHUB_WORKSPACE | Default working directory | Checkout वाला folder |
| RUNNER_TEMP | Per-job temp folder | Job का temp folder |
| Reserved variable | Cannot be overwritten | Overwrite नहीं हो सकता |

---

## ⚡ 3-Line Summary
English: GitHub injects `CI`, `GITHUB_*` and `RUNNER_*` variables on every runner.
They carry commit, branch, repo, actor and paths, and cannot be overridden.
Same data is in contexts; use contexts for `if:`/`with:`, env for shell.

Hindi: GitHub हर runner पर `CI`, `GITHUB_*` और `RUNNER_*` variables inject करता है।
इनमें commit, branch, repo, actor और paths होते हैं, और इन्हें override नहीं कर सकते।
यही data contexts में भी है; `if:`/`with:` में contexts और shell में env use करो।

---

## ➡️ Next Topic
**276. Setting Custom Env Variables** — how to create your own variables that survive between steps using `GITHUB_ENV`, plus `vars` configuration variables.
