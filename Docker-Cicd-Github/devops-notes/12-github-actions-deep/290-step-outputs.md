# 290. Step Outputs
# हिंदी में: Step Outputs (step के नतीजे)

---

## 🔵 Simple Definition (English)
A step output is a named string value a step produces and later steps in the same job read through `steps.<step_id>.outputs.<name>`. Shell steps write it by appending `name=value` to the file `$GITHUB_OUTPUT`; JavaScript/composite actions declare `outputs:` in their `action.yml`. The step must have an `id`. Related: `steps.<id>.outcome` (before `continue-on-error`) and `steps.<id>.conclusion` (after).

## 🔵 सरल परिभाषा (Hindi)
Step output एक नाम वाली string value है जिसे कोई step बनाता है और उसी job के बाद के steps `steps.<step_id>.outputs.<name>` से पढ़ते हैं। Shell steps इसे `$GITHUB_OUTPUT` file में `name=value` जोड़कर लिखते हैं; JavaScript/composite actions अपनी `action.yml` में `outputs:` declare करती हैं। Step पर `id` होना ज़रूरी है। संबंधित: `steps.<id>.outcome` (`continue-on-error` से पहले) और `steps.<id>.conclusion` (बाद में)।

---

## 🔴 Problem it Solves
Within one job, steps are separate shell processes: a variable set in step 1 is gone in step 2. You need a clean channel to hand values forward (a computed version, a cache hit flag, a deploy URL). Environment files (`$GITHUB_ENV`) work too, but outputs are explicit, scoped to one step id (no pollution) and can be exported to job outputs.

## 🔴 यह क्यों बना? (Hindi)
एक job के अंदर भी हर step अलग shell process है: step 1 में set variable step 2 में नहीं मिलता। Values आगे बढ़ाने के लिए साफ़ रास्ता चाहिए (निकाला हुआ version, cache hit flag, deploy URL)। `$GITHUB_ENV` भी चलता है, पर outputs स्पष्ट हैं, एक step id तक सीमित (गंदगी नहीं), और job outputs में export हो सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Give the producing step an id:            - id: ver
Step 2 → Inside run: write                          echo "value=1.2.3" >> "$GITHUB_OUTPUT"
Step 3 → Runner reads the file after the step ends and registers outputs
Step 4 → Later steps read                           ${{ steps.ver.outputs.value }}
Step 5 → For multi-line: name<<DELIM ... DELIM  (random delimiter for untrusted data)
Step 6 → To use across jobs: map to jobs.<job>.outputs (topic 289)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Output बनाने वाले step को id दें:        - id: ver
Step 2 → run: के अंदर लिखें                         echo "value=1.2.3" >> "$GITHUB_OUTPUT"
Step 3 → Step खत्म होने पर runner file पढ़कर outputs register करता है
Step 4 → बाद के steps पढ़ते हैं                      ${{ steps.ver.outputs.value }}
Step 5 → Multi-line के लिए: name<<DELIM ... DELIM (untrusted data के लिए random delimiter)
Step 6 → Jobs के बीच इस्तेमाल के लिए jobs.<job>.outputs में map करें (topic 289)
```

---

## 🟡 Real World Example
A deploy pipeline for a React app on a VPS: step `release` creates folder name `20261105-1530-a1b2c3d` and writes it as an output. The next steps rsync into `/var/www/releases/<name>`, switch the `current` symlink to it, and finally the smoke-test step curls the site. If the smoke test fails, the rollback step uses the previous release name captured as another output. All values flow through step outputs with no files on disk.

## 🟡 Real Example Hindi mein
VPS पर React app की deploy pipeline: step `release` folder नाम `20261105-1530-a1b2c3d` बनाकर output में लिखता है। अगले steps उसी नाम से `/var/www/releases/<name>` में rsync करते हैं, `current` symlink बदलते हैं, और आख़िर में smoke-test step site पर curl करता है। Smoke test fail हो तो rollback step पिछला release नाम (दूसरे output में रखा) इस्तेमाल करता है। सब values step outputs से बहती हैं, disk पर कोई file नहीं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/step-outputs-basic.yml
name: step-outputs-basic                  # workflow name
on: [workflow_dispatch]                   # manual run
jobs:
  demo:
    runs-on: ubuntu-latest                # runner
    steps:
      - id: now                           # id required to read the output
        run: echo "stamp=$(date +%Y%m%d-%H%M)" >> "$GITHUB_OUTPUT"   # write output
      - run: echo "Stamp is ${{ steps.now.outputs.stamp }}"          # read it in later step
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/step-outputs-advanced.yml
# Release name, multi-line changelog, outcome vs conclusion, safe usage via env
name: step-outputs-advanced               # workflow name
on:
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0                  # full history for changelog
      - id: rel                           # step with outputs
        run: |
          NAME="$(date -u +%Y%m%d-%H%M)-$(git rev-parse --short HEAD)"   # release folder name
          echo "name=$NAME" >> "$GITHUB_OUTPUT"                          # simple output
          # multi-line output: choose a delimiter unlikely to be in the text
          DELIM="EOF_$(openssl rand -hex 8)"
          {
            echo "log<<$DELIM"                         # start of the multi-line value
            git log --oneline -n 5                     # last five commits
            echo "$DELIM"                              # end marker
          } >> "$GITHUB_OUTPUT"
      - name: Print using env (injection-safe)
        env:
          REL_NAME: ${{ steps.rel.outputs.name }}      # value passed as data
          REL_LOG: ${{ steps.rel.outputs.log }}        # multi-line value
        run: |
          echo "Release: $REL_NAME"                    # use shell variable, not inline expr
          printf '%s\n' "$REL_LOG"                     # print changelog
      - id: smoke                         # a step that may fail
        continue-on-error: true           # do not stop the job on failure
        run: curl --fail --max-time 10 https://example.com/health   # example URL
      - name: Report result
        run: |
          echo "outcome=${{ steps.smoke.outcome }}"       # real result: success/failure
          echo "conclusion=${{ steps.smoke.conclusion }}" # after continue-on-error: success
      - name: Rollback on failed smoke test
        if: steps.smoke.outcome == 'failure'              # use outcome, not conclusion
        run: echo "would roll back to previous release"   # placeholder for real rollback
```

---

## 🟠 My Stack Integration
- **Node.js**: `node -p "require('./package.json').version"` into an output used for the Docker tag.
- **FastAPI**: output the git SHA used as `APP_VERSION` build arg for `/health` version display.
- **React + Nginx**: output release folder name for symlink-based zero-downtime deploys.
- **AWS**: `aws cloudformation describe-stacks ... --query ...` into an output used by later steps; mask if sensitive with `::add-mask::`.
- **Docker build-push-action** exposes outputs like `digest` and `imageid`; read with `steps.<id>.outputs.digest`.

```yaml
# Snippet: use the pushed image digest in a later step
      - id: push                          # build-push-action step id
        uses: docker/build-push-action@v6 # example version
        with:
          context: ./api
          push: true
          tags: ghcr.io/${{ github.repository }}/api:latest
      - run: echo "Deployed digest ${{ steps.push.outputs.digest }}"   # sha256:... immutable id
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No `id` on the step, so `steps.x.outputs` is empty.
✅ Correct: Always add `id:`.

❌ Mistake 2: `echo "::set-output name=x::y"` (deprecated and removed).
✅ Correct: `echo "x=y" >> "$GITHUB_OUTPUT"`.

❌ Mistake 3: Reading an output in the same step that writes it. It is available only to later steps.
✅ Correct: Use a shell variable inside the step, output for next steps.

❌ Mistake 4: Using `${{ steps.x.outputs.title }}` directly in `run:` with untrusted values (PR title).
✅ Correct: Pass through `env:` and quote `"$VAR"`.

❌ Mistake 5: Mixing up `outcome` and `conclusion` with `continue-on-error`.
✅ Correct: `outcome` is raw result, `conclusion` is after `continue-on-error` is applied.

---

## 🧠 Tricky Interview Question
A step writes `echo "msg=hello world" >> $GITHUB_OUTPUT` and the next step prints `${{ steps.a.outputs.msg }}` and sees `hello world` fine. But when the message comes from `git log -1 --pretty=%B` containing a newline, only the first line shows. Why and how to fix?

Answer: The output file format is one `name=value` per line, so a newline ends the value and the extra lines are parsed as garbage or ignored. Use the multi-line syntax `name<<DELIMITER` / value / `DELIMITER`. If the content can be attacker-controlled, use a random delimiter (as in the example) so the content cannot contain the terminator and inject extra outputs. This is a known injection vector.

---

## ⚫ Interview Questions + Answers

Q1: How is a step output different from `$GITHUB_ENV`?
A1: `$GITHUB_ENV` sets environment variables for all later steps in the job, with no namespacing. Outputs are namespaced by step id and can be mapped to job outputs.

Q2: What is `steps.<id>.outcome` used for?
A2: The real result (`success`, `failure`, `cancelled`, `skipped`) before `continue-on-error`; `conclusion` is the result after it.

Q3: How do JavaScript actions set outputs?
A3: With `core.setOutput('name', value)` from `@actions/core`, which writes to `$GITHUB_OUTPUT`.

Q4: How to hide a value in logs?
A4: `echo "::add-mask::$VALUE"` before printing; do not put masked secrets in outputs.

Q5: Can step outputs be used in `if:`?
A5: Yes: `if: steps.check.outputs.changed == 'true'`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Handing computed values to later steps of the same job.
- Branching on a detection result with `if:`.
- Feeding job outputs.

❌ Avoid when:
- Value is needed in another job without mapping (use job outputs).
- It is a secret.
- It is large data or a file (write a file or use artifacts).

---

## 📊 Visual Diagram
```
 JOB (one runner, many shells)
 +-------------------------------------------------------------+
 | step 1 (id: rel)                                            |
 |   echo "name=2026-abc" >> $GITHUB_OUTPUT   --+              |
 +----------------------------------------------|--------------+
                                                v
                                  runner registers steps.rel.outputs.name
 +----------------------------------------------|--------------+
 | step 2                                       |              |
 |   env: REL: ${{ steps.rel.outputs.name }} <--+              |
 |   run: echo "$REL"                                          |
 +-------------------------------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Step id | Name used to reference a step | Step का reference नाम |
| `$GITHUB_OUTPUT` | File for writing outputs | Outputs लिखने की file |
| `outcome` | Raw step result | Step का असली नतीजा |
| `conclusion` | Result after continue-on-error | continue-on-error के बाद का नतीजा |
| Delimiter | Marks multi-line value end | Multi-line value का अंत-चिह्न |
| `add-mask` | Hide value in logs | Logs में value छुपाना |

---

## ⚡ 3-Line Summary
English: Steps publish values by appending `name=value` to `$GITHUB_OUTPUT`; the step needs an `id`.
English: Read them with `steps.<id>.outputs.<name>`; multi-line values need a delimiter.
English: Pass them to scripts through `env:` to avoid injection, and map to job outputs for other jobs.
Hindi: Steps `$GITHUB_OUTPUT` में `name=value` जोड़कर values देते हैं; step पर `id` ज़रूरी है।
Hindi: `steps.<id>.outputs.<name>` से पढ़ें; multi-line values को delimiter चाहिए।
Hindi: Injection से बचने के लिए scripts में `env:` से दें, और दूसरे jobs के लिए job outputs में map करें।

---

## ➡️ Next Topic
**291. Passing Data Between Jobs** — comparing outputs, artifacts, cache and external storage.
