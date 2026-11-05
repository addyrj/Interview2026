# 276. Setting Custom Env Variables
# हिंदी में: Custom Env Variables सेट करना

---

## 🔵 Simple Definition (English)
Custom env variables are values you define yourself. Four ways: YAML `env:` (static), `$GITHUB_ENV` (set at runtime for later steps), `vars.*` (repository/organization/environment configuration variables from Settings), and job `outputs` (pass between jobs).

## 🔵 सरल परिभाषा (Hindi)
Custom env variables वे values हैं जो आप खुद define करते हैं। चार तरीके: YAML `env:` (static), `$GITHUB_ENV` (runtime पर आगे के steps के लिए), `vars.*` (Settings में repo/organization/environment configuration variables), और job `outputs` (jobs के बीच pass करने के लिए)।

---

## 🔴 Problem it Solves
Some values are only known at runtime (version from `package.json`, a generated build id). Others are shared by many workflows but are not secret (API base URL, region). Hard-coding them or duplicating them breaks easily. Each of the four mechanisms fits a different case.

## 🔴 यह क्यों बना? (Hindi)
कुछ values runtime पर ही पता चलती हैं (`package.json` से version, generated build id)। कुछ कई workflows में share होती हैं पर secret नहीं हैं (API base URL, region)। इन्हें hard-code या duplicate करने से गड़बड़ होती है। चारों mechanisms अलग-अलग case के लिए हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Static value?              -> env: in YAML
Step 2 → Same value in many repos?  -> Settings > Variables  -> ${{ vars.NAME }}
Step 3 → Computed in a step?        -> echo "NAME=value" >> "$GITHUB_ENV"
Step 4 → Computed, needed by another JOB? -> echo "name=value" >> "$GITHUB_OUTPUT"
                                            + job outputs: + needs.job.outputs.name
Step 5 → Runner reads GITHUB_ENV after the step ends
Step 6 → Later steps in the same job see $NAME
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Static value?              -> YAML में env:
Step 2 → कई repos में same value?   -> Settings > Variables  -> ${{ vars.NAME }}
Step 3 → किसी step में compute हुई?   -> echo "NAME=value" >> "$GITHUB_ENV"
Step 4 → Compute हुई, दूसरे JOB को चाहिए? -> echo "name=value" >> "$GITHUB_OUTPUT"
                                            + job outputs: + needs.job.outputs.name
Step 5 → Runner step खत्म होने के बाद GITHUB_ENV पढ़ता है
Step 6 → उसी job के आगे के steps में $NAME दिखता है
```

---

## 🟡 Real World Example
A release workflow reads the version from `package.json` in step 1 (`VERSION=1.8.2`), stores it in `$GITHUB_ENV`, then step 2 builds `my-api:1.8.2`, step 3 writes release notes with the same version. The API base URL `https://api.example.com` lives in a repository variable `API_URL` so frontend and backend workflows share it.

## 🟡 Real Example Hindi mein
Release workflow step 1 में `package.json` से version पढ़ता है (`VERSION=1.8.2`), उसे `$GITHUB_ENV` में रखता है, step 2 `my-api:1.8.2` build करता है, step 3 उसी version से release notes लिखता है। API base URL `https://api.example.com` repository variable `API_URL` में रहता है, ताकि frontend और backend दोनों workflows उसे share करें।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/custom-env-basic.yml
name: custom-env-basic                 # workflow name
on: workflow_dispatch                  # run manually from the Actions tab

jobs:
  demo:
    runs-on: ubuntu-latest             # runner
    steps:
      - uses: actions/checkout@v4      # example version
      - name: Set runtime variables
        run: |
          VERSION=$(node -p "require('./package.json').version")   # read version with Node
          echo "VERSION=$VERSION" >> "$GITHUB_ENV"                 # save for next steps
          echo "BUILT_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$GITHUB_ENV"   # UTC timestamp
      - name: Use them
        run: echo "Building v$VERSION at $BUILT_AT"                # both variables exist now
      - name: Use a configuration variable
        run: echo "API is ${{ vars.API_URL }}"                      # defined in Settings > Variables
        # if vars.API_URL is not defined it is an empty string
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/custom-env-advanced.yml
name: custom-env-advanced              # workflow name
on:
  push:
    tags: ["v*"]                       # run on version tags

jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.v.outputs.version }}   # expose to other jobs
      is_prerelease: ${{ steps.v.outputs.pre }} # boolean-like string
    steps:
      - id: v                          # step id
        run: |
          TAG="${GITHUB_REF_NAME}"                    # e.g. v1.4.0-rc1
          VERSION="${TAG#v}"                          # strip leading v -> 1.4.0-rc1
          echo "version=$VERSION" >> "$GITHUB_OUTPUT" # step output
          case "$VERSION" in
            *-*) echo "pre=true"  >> "$GITHUB_OUTPUT" ;;   # has a dash => prerelease
            *)   echo "pre=false" >> "$GITHUB_OUTPUT" ;;   # stable
          esac

  build:
    needs: prepare                     # wait and get outputs
    runs-on: ubuntu-latest
    env:
      VERSION: ${{ needs.prepare.outputs.version }}   # job level env from output
      REGISTRY: ${{ vars.REGISTRY || 'ghcr.io' }}     # repo variable with default
    steps:
      - uses: actions/checkout@v4      # example version
      - name: Multi-line value in GITHUB_ENV
        run: |
          {
            echo "RELEASE_NOTES<<EOF_NOTES"           # heredoc delimiter syntax
            git log -5 --pretty=format:'- %s'          # last five commit subjects
            echo ""                                    # newline before closing delimiter
            echo "EOF_NOTES"                           # closing delimiter
          } >> "$GITHUB_ENV"                           # persists multi-line value
      - name: Print
        run: |
          echo "image: $REGISTRY/my-api:$VERSION"      # uses job env
          printf '%s\n' "$RELEASE_NOTES"               # multi-line var from previous step
```
Not run locally; bash syntax checked and YAML parsed. Use a random delimiter if the value may come from untrusted input (a fixed delimiter in the data could inject extra variables).

---

## 🟠 My Stack Integration
Keep non-secret deployment settings in `vars` (VPS host, region `ap-south-1`, ECR repo name, domain). Keep keys in `secrets`. Let the workflow compute `IMAGE_TAG` and hand it to docker compose on the VPS.

```yaml
# snippet: AWS + VPS variables
    env:
      AWS_REGION: ${{ vars.AWS_REGION }}        # e.g. ap-south-1 (not secret)
      ECR_REPO: ${{ vars.ECR_REPO }}            # e.g. my-api
      DOMAIN: ${{ vars.DOMAIN }}                # e.g. api.example.com for health check
    steps:
      - run: curl --fail --retry 5 --retry-delay 3 "https://$DOMAIN/health"
        # smoke-test through Nginx after the deploy
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `export VERSION=1.0` and expecting it in the next step.
✅ Correct: Append to `$GITHUB_ENV` (each step is a new shell).

❌ Mistake 2: Expecting `$GITHUB_ENV` values in another job.
✅ Correct: Use `outputs` + `needs`.

❌ Mistake 3: Storing tokens in `vars`; they are visible in logs and to anyone with read access.
✅ Correct: Use `secrets` for sensitive values.

❌ Mistake 4: Writing untrusted text to `GITHUB_ENV` (e.g. PR title); newlines can add extra variables like `PATH` or `NODE_OPTIONS`.
✅ Correct: Avoid it, or use a random multi-line delimiter, and never allow writes to `PATH`/`NODE_OPTIONS`/`LD_PRELOAD` from untrusted data.

---

## 🧠 Tricky Interview Question
A step does `echo "TOKEN=$X" >> $GITHUB_ENV` in a pull request from a fork, and a later step runs the contributor's code. What is the risk?

Answer: Data controlled by an attacker can define env variables for later steps, including `NODE_OPTIONS` or `PATH`, leading to arbitrary code execution in the job (and token theft if secrets are present). The fix is not to write untrusted data to `GITHUB_ENV`, use least-privilege `permissions`, and avoid `pull_request_target` with checkout of fork code.

---

## ⚫ Interview Questions + Answers

Q1: How do you pass a value from step A to step B?
A1: `GITHUB_ENV` (as `$NAME`) or `GITHUB_OUTPUT` (as `steps.a.outputs.name`).

Q2: Between jobs?
A2: Job-level `outputs:` mapped from step outputs, read via `needs.<job>.outputs.<name>`. Values are strings, limited in size.

Q3: What are `vars`?
A3: Configuration variables set in repo, org or environment settings; readable via `${{ vars.NAME }}`; not encrypted.

Q4: How to set a multi-line value?
A4: `NAME<<DELIM` newline, value lines, then `DELIM` on its own line, appended to `GITHUB_ENV`.

Q5: Are `::set-env` commands still supported?
A5: No, they were disabled for security; use environment files.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Computed values reused by many steps (version, tag, timestamp).
- Shared non-secret settings via `vars`.

❌ Avoid when:
- Value is secret (use `secrets`).
- Data is untrusted and goes to `GITHUB_ENV`.

---

## 📊 Visual Diagram
```
 JOB A                                      JOB B
 step1: echo VERSION=1.8 >> $GITHUB_ENV     needs: A
        |                                   env: V=${{ needs.A.outputs.version }}
 step2: $VERSION visible  (same job only)          ^
        |                                          |
 step3: echo version=1.8 >> $GITHUB_OUTPUT --> job outputs: --+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GITHUB_ENV | File to persist env for later steps | आगे के steps के लिए env file |
| GITHUB_OUTPUT | File to emit step outputs | Step outputs के लिए file |
| vars | Non-secret configuration variables | Non-secret config variables |
| Output | Value exposed by step/job | Step/job का exposed value |
| Heredoc delimiter | Marker for multi-line values | Multi-line value का marker |

---

## ⚡ 3-Line Summary
English: Use `env:` for static, `$GITHUB_ENV` for runtime-in-job, `vars` for shared config, `outputs` across jobs.
Each step is a fresh shell, so `export` does not persist.
Never put untrusted data into `GITHUB_ENV`.

Hindi: Static के लिए `env:`, job के अंदर runtime के लिए `$GITHUB_ENV`, shared config के लिए `vars`, jobs के बीच `outputs`।
हर step नया shell है, इसलिए `export` persist नहीं होता।
Untrusted data को `GITHUB_ENV` में कभी मत डालो।

---

## ➡️ Next Topic
**277. Secrets — Complete Guide** — for sensitive values (passwords, SSH keys, tokens) you need encrypted `secrets`, not plain env or vars.
