# 263. env Context
# हिंदी में: env Context

---

## 🔵 Simple Definition (English)
The `env` context contains the environment variables you set with `env:` at workflow, job or step level, read as `${{ env.NAME }}`. It is different from the shell variable `$NAME`: the context is substituted by GitHub before the shell starts, while `$NAME` is read by the shell at run time.

## 🔵 सरल परिभाषा (Hindi)
`env` context में वे environment variables होते हैं जो आपने workflow, job या step level पर `env:` से set किए, और `${{ env.NAME }}` से पढ़े जाते हैं। यह shell variable `$NAME` से अलग है: context को GitHub shell शुरू होने से पहले replace करता है, जबकि `$NAME` को shell run time पर पढ़ता है।

---

## 🔴 Problem it Solves
Places like `with:`, `if:`, `name:` and `working-directory:` are not shells, so `$NAME` does not expand there. You still want to reuse one definition (like `IMAGE_NAME`) in those places. The `env` context bridges YAML keys and your single source of truth.

## 🔴 यह क्यों बना? (Hindi)
`with:`, `if:`, `name:` और `working-directory:` जैसी जगहें shell नहीं हैं, इसलिए वहाँ `$NAME` expand नहीं होता। फिर भी आप एक definition (जैसे `IMAGE_NAME`) को इन जगहों पर reuse करना चाहते हैं। `env` context YAML keys और आपके single source of truth के बीच पुल है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You define env: at workflow, job and/or step level
Step 2 → Runner merges them (step > job > workflow) for each step
Step 3 → ${{ env.NAME }} in with:/if:/name:/run: is replaced by the merged value
Step 4 → The same value also exists as $NAME inside the shell
Step 5 → Variables written to $GITHUB_ENV in earlier steps are added too
Step 6 → env is NOT available in jobs.<id>.runs-on or jobs.<id>.if
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → आप workflow, job और/या step level पर env: define करते हैं
Step 2 → Runner हर step के लिए इन्हें merge करता है (step > job > workflow)
Step 3 → with:/if:/name:/run: में ${{ env.NAME }} merged value से बदल जाता है
Step 4 → वही value shell के अंदर $NAME के रूप में भी होती है
Step 5 → पिछले steps में $GITHUB_ENV में लिखे variables भी जुड़ जाते हैं
Step 6 → env jobs.<id>.runs-on या jobs.<id>.if में उपलब्ध नहीं है
```

---

## 🟡 Real World Example
One workflow defines `IMAGE: ghcr.io/acme/orders-api` at top. The build step passes `tags: ${{ env.IMAGE }}:${{ github.sha }}` through `with:`; the deploy step uses `docker pull $IMAGE:$GITHUB_SHA` in shell. Rename the image once and every place updates, like changing a constant in code.

## 🟡 Real Example Hindi mein
एक workflow top पर `IMAGE: ghcr.io/acme/orders-api` define करता है। Build step `with:` में `tags: ${{ env.IMAGE }}:${{ github.sha }}` देता है; deploy step shell में `docker pull $IMAGE:$GITHUB_SHA` इस्तेमाल करता है। Image का नाम एक बार बदलो तो हर जगह अपडेट, जैसे code में constant बदलना।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/env-ctx-basic.yml
name: env-ctx-basic                    # workflow name
on: push                               # trigger
env:
  IMAGE: ghcr.io/acme/orders-api       # defined once
  REGION: ap-south-1                   # AWS Mumbai
jobs:
  demo:
    runs-on: ubuntu-24.04              # example runner (env NOT allowed here)
    env:
      STAGE: staging                   # job-level variable
    steps:
      - name: Build ${{ env.IMAGE }}   # env context allowed in step name
        run: |                         # shell block
          echo "context : ${{ env.IMAGE }}"   # replaced by GitHub BEFORE shell runs
          echo "shell   : $IMAGE"             # expanded by bash at run time
          echo "stage   : $STAGE in $REGION"  # job + workflow variables
      - name: Conditional on env       # env in step if:
        if: env.STAGE == 'staging'     # compare string
        run: echo "staging-only step"  # runs
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/env-ctx-advanced.yml
name: env-ctx-advanced                 # shows env context + GITHUB_ENV
on:
  push:
    branches: [main]                   # main only
env:
  NODE_VERSION: "20"                   # quoted string
  IMAGE: ghcr.io/${{ github.repository }}/api   # env value built from github context
jobs:
  build:
    runs-on: ubuntu-24.04              # example runner
    steps:
      - uses: actions/checkout@v4      # source
      - uses: actions/setup-node@v4    # Node
        with:
          node-version: ${{ env.NODE_VERSION }}   # env context inside with:
      - name: Derive tag and persist it   # create new variable for later steps
        run: |                         # bash
          echo "TAG=${GITHUB_SHA::7}" >> "$GITHUB_ENV"   # appears as env.TAG in later steps
      - name: Use derived variable     # next step sees TAG
        run: echo "Image will be ${{ env.IMAGE }}:${{ env.TAG }}"   # both from env context
      - name: Build with step override
        env:
          NODE_ENV: production         # only for this step
        run: npm ci && npm run build   # build as production
      - name: Show that step env is gone
        run: echo "NODE_ENV=${NODE_ENV:-unset}"   # prints unset
```
Parsed locally as YAML; behaviour of `$GITHUB_ENV` follows GitHub docs but the run was not executed here.

---

## 🟠 My Stack Integration
- **Node.js**: `NODE_VERSION` in env, reused for `setup-node`, Docker `--build-arg NODE_VERSION`.
- **FastAPI**: `PYTHON_VERSION: "3.12"` once; used by `setup-python` and Dockerfile build-arg.
- **React**: `VITE_API_URL` in step env of the build step only.
- **Nginx/VPS**: `DEPLOY_PATH: /var/www/app` env reused in rsync and ssh commands.
- **AWS**: `AWS_REGION` env is read automatically by AWS CLI and SDKs.
- **Security**: do not put secrets into workflow-level env just to reuse them.

```yaml
      - name: Pass env into Docker build   # keep versions in sync across CI and image
        run: docker build --build-arg NODE_VERSION="$NODE_VERSION" -t "$IMAGE:$TAG" .   # shell form
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `runs-on: ${{ env.RUNNER }}`.
✅ Correct: Use `vars.RUNNER` or `inputs`; env is not available in `runs-on`.

❌ Mistake 2: Using `$VAR` in `with:` and expecting expansion.
✅ Correct: `with: tags: ${{ env.IMAGE }}`.

❌ Mistake 3: Defining `A: x` and `B: ${{ env.A }}` in the same `env:` block.
✅ Correct: A variable cannot reference a sibling in the same map; compute the value earlier or repeat the expression.

❌ Mistake 4: Setting `$GITHUB_ENV` and reading in the same step.
✅ Correct: The value is available only from the next step.

❌ Mistake 5: Multi-line values written with `echo "X=a\nb" >> $GITHUB_ENV`.
✅ Correct: Use the heredoc delimiter syntax: `X<<EOF ... EOF` with a random delimiter.

---

## 🧠 Tricky Interview Question
`echo "${{ env.TOKEN }}"` and `echo "$TOKEN"` appear to print the same. When is it dangerous to prefer the first form?

Answer: The `${{ }}` form is text-substituted into the script file before bash parses it. If the value contains quotes, `$()` or backticks (for example from `github.event.issue.title` copied into env), the shell treats it as code, which is script injection. The `$TOKEN` form is read as data by the shell. So prefer `$VAR` inside `run:` and keep `${{ env.X }}` for YAML keys such as `with:` and `if:`.

---

## ⚫ Interview Questions + Answers

Q1: `${{ env.X }}` vs `$X`?
A1: First is replaced by GitHub before the shell; second is expanded by the shell. Use `$X` in `run:` for safety.

Q2: Where is the `env` context not available?
A2: `jobs.<id>.runs-on`, `jobs.<id>.if`, `jobs.<id>.strategy`, and workflow-level `name`/`on`.

Q3: How do you create an env var for later steps?
A3: `echo "NAME=value" >> "$GITHUB_ENV"`.

Q4: Are variables inherited by called reusable workflows?
A4: No; each workflow has its own env. Pass values via `with:` inputs.

Q5: Are env values masked in logs?
A5: Only if they come from secrets (or `::add-mask::`). Plain values print as-is.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- One value is needed in `with:`, `if:`, names and shell
- Sharing derived values across steps via `$GITHUB_ENV`
- Keeping versions and image names in a single place

❌ Avoid when:
- Org-wide shared config (use `vars` context)
- Secrets (use `secrets`, scoped to step)
- Anything needed in `runs-on` or job-level `if`

---

## 📊 Visual Diagram
```
 workflow env  --+
 job env       --+--> merged per step --> env context  ${{ env.X }}  (YAML keys)
 step env      --+                    \-> process env  $X            (shell)
 $GITHUB_ENV   --+ (from next step on)

 Not available: jobs.<id>.runs-on, jobs.<id>.if
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| env context | Variables readable in expressions | Expressions में पढ़ने लायक variables |
| $GITHUB_ENV | File to add vars for later steps | आगे के steps के लिए variables की file |
| Substitution | Text replaced before shell | Shell से पहले text बदलना |
| Heredoc | Multi-line shell syntax | Multi-line shell syntax |
| Precedence | Which scope wins | कौन सा scope जीतता है |

---

## ⚡ 3-Line Summary
English: `env` context exposes your `env:` values to YAML keys via `${{ env.X }}`.
It is substituted before the shell, so prefer `$X` in `run:`.
Use `$GITHUB_ENV` for later steps; it is unavailable in `runs-on` and job `if`.
Hindi: `env` context आपके `env:` values को `${{ env.X }}` से YAML keys में देता है।
यह shell से पहले replace होता है, इसलिए `run:` में `$X` बेहतर है।
आगे के steps के लिए `$GITHUB_ENV`; यह `runs-on` और job `if` में उपलब्ध नहीं।

---

## ➡️ Next Topic
**264. vars Context** — non-secret configuration variables defined in repo, environment or organization settings.
