# 258. env: in Steps
# हिंदी में: Steps में env: (Environment Variables)

---

## 🔵 Simple Definition (English)
`env:` written under a single step sets environment variables only for that one step's process. It is the most specific level (step > job > workflow), so it overrides the same name set higher up. Other steps never see it.

## 🔵 सरल परिभाषा (Hindi)
किसी एक step के नीचे लिखा `env:` environment variables सिर्फ उसी step के process के लिए set करता है। यह सबसे specific level है (step > job > workflow), इसलिए ऊपर वाले उसी नाम की value को override कर देता है। बाकी steps इसे नहीं देखते।

---

## 🔴 Problem it Solves
If you export a variable at workflow level, every step and every third-party action sees it. A secret token that only the deploy step needs would leak into `npm install` scripts, test runners and any action you `uses:`. Also, one flaky test step may need `LOG_LEVEL=debug` without changing the rest of the job. Step-level `env:` gives least-privilege scoping and one-off overrides.

## 🔴 यह क्यों बना? (Hindi)
अगर आप variable workflow level पर export करते हैं तो हर step और हर third-party action उसे देख सकता है। जिस secret token की ज़रूरत सिर्फ deploy step को है वह `npm install` scripts, test runner और हर `uses:` action तक पहुँच जाएगा। साथ ही किसी एक flaky test step को बाकी job बदले बिना `LOG_LEVEL=debug` चाहिए हो सकता है। Step-level `env:` least-privilege scoping और one-off override देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Runner reaches the step and reads its env: map
Step 2 → It starts from workflow env, overlays job env, then overlays step env
Step 3 → Expressions like ${{ secrets.X }} inside env: are evaluated first
Step 4 → The merged map is passed as the process environment of that step
Step 5 → run: scripts read $NAME; actions read it via process.env / INPUT_*
Step 6 → Step finishes -> the step-level values vanish (next step starts clean)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Runner step पर पहुँचकर उसका env: map पढ़ता है
Step 2 → पहले workflow env, उसके ऊपर job env, फिर उसके ऊपर step env लगता है
Step 3 → env: के अंदर ${{ secrets.X }} जैसे expressions पहले evaluate होते हैं
Step 4 → Merge हुआ map उस step के process environment के रूप में जाता है
Step 5 → run: scripts $NAME पढ़ते हैं; actions process.env / INPUT_* से पढ़ते हैं
Step 6 → Step खत्म -> step-level values गायब (अगला step साफ़ environment से शुरू)
```

---

## 🟡 Real World Example
Your VPS deploy step runs `ssh` and needs `SSH_KEY` from secrets. The `npm ci` and `npm test` steps right before it do not. By putting `SSH_KEY` only in the deploy step's `env:`, a compromised npm package (supply-chain attack) running during `npm ci` cannot read it. Same idea at Swiggy-scale: only the "push image to ECR" step gets AWS credentials.

## 🟡 Real Example Hindi mein
आपका VPS deploy step `ssh` चलाता है और secrets से `SSH_KEY` चाहिए। उससे ठीक पहले के `npm ci` और `npm test` steps को यह नहीं चाहिए। `SSH_KEY` सिर्फ deploy step के `env:` में रखने से `npm ci` के दौरान चलने वाला कोई compromised npm package (supply-chain attack) इसे पढ़ नहीं सकता। Swiggy-scale पर भी यही idea: सिर्फ "ECR पर image push" step को AWS credentials मिलते हैं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/env-step-basic.yml
name: env-step-basic                   # workflow display name
on: push                               # run on every push
env:
  APP_NAME: orders-api                 # workflow-level default, visible to all steps
jobs:
  demo:                                # job id
    runs-on: ubuntu-24.04              # GitHub-hosted runner (example label)
    steps:
      - name: Uses workflow env only   # step 1
        run: echo "App is $APP_NAME"   # prints orders-api
      - name: Step level override      # step 2
        env:
          APP_NAME: orders-api-canary  # overrides workflow value for THIS step only
          LOG_LEVEL: debug             # new variable that exists only in this step
        run: |                         # multi-line shell script
          echo "App is $APP_NAME"      # prints orders-api-canary
          echo "Log level $LOG_LEVEL"  # prints debug
      - name: Back to default          # step 3
        run: echo "App is $APP_NAME, level=${LOG_LEVEL:-unset}"  # orders-api, unset
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/env-step-advanced.yml
name: node-api-ci-cd                   # production style pipeline
on:
  push:
    branches: [main]                   # only main triggers deploy
permissions:
  contents: read                       # least privilege for GITHUB_TOKEN
env:
  NODE_ENV: production                 # workflow default
  CI: "true"                           # quote so YAML keeps it a string
jobs:
  build-deploy:
    runs-on: ubuntu-24.04              # example runner label
    timeout-minutes: 15                # fail stuck jobs
    env:
      IMAGE: ghcr.io/${{ github.repository }}/api   # job-level, visible to all steps
    steps:
      - uses: actions/checkout@v4      # example version, check latest
      - uses: actions/setup-node@v4    # example version
        with:
          node-version: 20             # LTS example
          cache: npm                   # cache npm downloads
      - name: Install (no secrets here)
        run: npm ci                    # runs with NO deploy secrets in env
      - name: Test with debug logs
        env:
          NODE_ENV: test               # step override of workflow value
          LOG_LEVEL: debug             # one-off, only for this step
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test  # CI-only DB
        run: npm test                  # tests see NODE_ENV=test
      - name: Deploy to VPS
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}   # secret scoped to this step only
          VPS_HOST: ${{ vars.VPS_HOST }}        # non-secret config from repo variables
        run: |                         # script block
          set -euo pipefail            # stop on first error / unset var
          install -m 600 /dev/null key # create key file with 600 permissions
          printf '%s\n' "$SSH_KEY" > key   # write key from env (never echo it)
          ssh -i key -o StrictHostKeyChecking=accept-new deploy@"$VPS_HOST" \
            "docker pull $IMAGE:${GITHUB_SHA} && docker compose up -d"  # remote deploy
          rm -f key                    # remove key file after use
```
Note: example action versions and runner labels change over time; the YAML was parsed locally but the workflow was not run on GitHub.

---

## 🟠 My Stack Integration
- **Node.js**: `NODE_ENV=test` only on the test step, `production` on the build step (so devDependencies are not accidentally skipped during tests).
- **FastAPI**: set `PYTHONUNBUFFERED=1` and `DATABASE_URL` on the `pytest` step only.
- **React**: `VITE_API_URL` (or `REACT_APP_*`) on the build step only; remember these get baked into public JS, so never put secrets there.
- **Nginx/VPS**: `VPS_HOST` and `SSH_KEY` only on the SSH deploy step.
- **AWS**: `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` only on the ECR push step (better: OIDC role, no static keys).

```yaml
# Step-scoped env for FastAPI tests + React build
      - name: FastAPI tests            # python tests step
        env:
          PYTHONUNBUFFERED: "1"        # flush logs immediately in CI
          DATABASE_URL: sqlite:///./test.db   # throwaway test DB
        run: pytest -q                 # quiet test run
      - name: React build              # frontend build step
        env:
          VITE_API_URL: https://api.example.com   # public value, safe to bake in
        run: npm run build             # Vite reads VITE_* at build time
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting a step's `env:` to be visible in the next step.
✅ Correct: Write to `$GITHUB_ENV` (`echo "NAME=value" >> "$GITHUB_ENV"`) to pass values to later steps, or use step outputs.

❌ Mistake 2: Putting `${{ secrets.X }}` in workflow-level `env:` "for convenience".
✅ Correct: Scope secrets to the single step that needs them.

❌ Mistake 3: Using `$VAR` inside `with:` or `if:` and expecting shell expansion.
✅ Correct: Those are not shell contexts. Use `${{ env.VAR }}` there.

❌ Mistake 4: Writing `CI: true` or `PORT: 08080` unquoted, so YAML turns it into a boolean or octal-looking number.
✅ Correct: Quote values: `CI: "true"`, `PORT: "8080"`. Env values are always strings.

❌ Mistake 5: `echo "$SSH_KEY"` for debugging.
✅ Correct: Never print secrets; masking is best-effort (a transformed value, e.g. base64, is not masked).

---

## 🧠 Tricky Interview Question
Workflow env has `MODE: prod`, the job env has `MODE: staging`, and a step has `env: { MODE: dev }`. The step runs `echo $MODE`, then the next step (with no env of its own) also runs `echo $MODE`. What does each print, and why?

Answer: The first prints `dev` (step beats job beats workflow). The next prints `staging`: the step-level value existed only in the first step's process, and job env now beats workflow env. Many people wrongly expect `dev` to stick. To make it stick, write `MODE=dev` into `$GITHUB_ENV` (avoid reusing a name already set in YAML env, to prevent precedence confusion; use a new name).

---

## ⚫ Interview Questions + Answers

Q1: What is the precedence of env at workflow, job and step level?
A1: Step overrides job, job overrides workflow. The most specific scope wins.

Q2: How do you pass a variable from one step to the next?
A2: Append `NAME=value` to the file `$GITHUB_ENV`, or write to `$GITHUB_OUTPUT` and read it via `steps.<id>.outputs.NAME`.

Q3: Why scope secrets at step level instead of job level?
A3: To shrink the blast radius. Any third-party action or script in the job can read job-level env; step-level limits exposure to one step.

Q4: Are env values typed?
A4: No, they are always strings. `true`, `1`, `null` all become text; compare with strings in `if:`.

Q5: Can `env:` use expressions?
A5: Yes. `env: TAG: ${{ github.sha }}` evaluates before the step starts. Contexts allowed at step env: github, needs, strategy, matrix, job, runner, env, vars, secrets, steps, inputs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Only one step needs a secret or special setting
- You need a one-off override (debug flag, test DB URL)
- You want config visible and reviewable next to the command

❌ Avoid when:
- Many steps need the same value (use job or workflow `env:`)
- The value must change during the run (use `$GITHUB_ENV` or outputs)
- The value is a big or sensitive file (use secrets files with strict permissions)

---

## 📊 Visual Diagram
```
 workflow env          job env             step env           process env
 +-----------+       +-----------+       +-----------+       +-------------+
 | MODE=prod |  -->  | MODE=stg  |  -->  | MODE=dev  |  -->  | MODE=dev    |
 | CI="true" |       | IMAGE=... |       | LOG=debug |       | CI="true"   |
 +-----------+       +-----------+       +-----------+       | IMAGE=...   |
   lowest priority                         highest           | LOG=debug   |
                                                             +-------------+
 Next step starts again from: workflow + job (step env is gone)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| env: | Map of environment variables | Environment variables का map |
| Scope | Where a value is visible | Value कहाँ दिखती है |
| Override | Higher specificity replaces lower | ऊपर वाली value को बदलना |
| $GITHUB_ENV | File to persist vars to later steps | आगे के steps के लिए variable file |
| Least privilege | Give only what is needed | सिर्फ ज़रूरी access देना |

---

## ⚡ 3-Line Summary
English: Step `env:` sets variables for one step only and beats job and workflow values.
It is the safest place for secrets because other steps and actions cannot see it.
For later steps use `$GITHUB_ENV` or step outputs; values are always strings.
Hindi: Step `env:` सिर्फ एक step के लिए variables set करता है और job/workflow values को override करता है।
Secrets रखने की यह सबसे सुरक्षित जगह है क्योंकि बाकी steps और actions इसे नहीं देखते।
आगे के steps के लिए `$GITHUB_ENV` या step outputs इस्तेमाल करो; values हमेशा string होती हैं।

---

## ➡️ Next Topic
**259. with: Parameters** — after setting environment for shell commands, learn how to pass inputs to actions with `with:`.
