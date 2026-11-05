# 260. if: Conditionals
# हिंदी में: if: Conditionals (शर्त के आधार पर चलाना)

---

## 🔵 Simple Definition (English)
`if:` lets a job or a step run only when an expression evaluates to true. If you omit it, the default is `success()`, meaning "run only if all previous steps/jobs succeeded". Status functions `always()`, `failure()`, `cancelled()` change that.

## 🔵 सरल परिभाषा (Hindi)
`if:` किसी job या step को तभी चलने देता है जब expression true हो। न लिखो तो default `success()` होता है, यानी "सिर्फ तब चलो जब पिछले सब steps/jobs सफल रहे"। `always()`, `failure()`, `cancelled()` इस behaviour को बदलते हैं।

---

## 🔴 Problem it Solves
A single workflow often serves many situations: PR vs main, tag vs branch, fork vs same repo, success vs failure (send Slack alert only on failure, clean up always). Without conditions you would duplicate workflows or write fragile shell `if` logic that still shows the step as "success" in the UI. `if:` gives declarative, visible skipping.

## 🔴 यह क्यों बना? (Hindi)
एक ही workflow कई हालातों में चलता है: PR बनाम main, tag बनाम branch, fork बनाम same repo, success बनाम failure (Slack alert सिर्फ failure पर, cleanup हमेशा)। Conditions के बिना workflows duplicate करने पड़ते या नाज़ुक shell `if` लिखना पड़ता जो UI में फिर भी "success" दिखाता। `if:` declarative और साफ़ दिखने वाला skipping देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Runner reaches job/step and reads its if:
Step 2 → If no if: -> implicit success() (skip when anything earlier failed)
Step 3 → Expression is evaluated (no need for ${{ }} wrapper in if:)
Step 4 → Result is coerced to boolean (empty string, 0, null, false = false)
Step 5 → true -> run; false -> mark "skipped" (shown grey, not failed)
Step 6 → Status functions look at the job/previous steps' result
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Runner job/step पर पहुँचकर उसका if: पढ़ता है
Step 2 → if: नहीं है -> implicit success() (पहले कुछ fail हुआ तो skip)
Step 3 → Expression evaluate होता है (if: में ${{ }} wrapper ज़रूरी नहीं)
Step 4 → Result boolean बनता है (खाली string, 0, null, false = false)
Step 5 → true -> चलता है; false -> "skipped" (grey, failed नहीं)
Step 6 → Status functions job/पिछले steps का result देखते हैं
```

---

## 🟡 Real World Example
Your pipeline: PRs run lint + tests only. Pushes to `main` also build the Docker image and deploy to the VPS. A Slack message goes out only when something fails, and a "stop temp containers" cleanup runs always. Big teams (Flipkart-style Big Billion Days releases) also gate production deploys with `if: github.ref == 'refs/heads/main'` so a feature-branch push can never reach prod.

## 🟡 Real Example Hindi mein
आपकी pipeline: PRs पर सिर्फ lint + tests चलते हैं। `main` पर push होने पर Docker image build और VPS पर deploy भी होता है। Slack message सिर्फ failure पर जाता है और temp containers रोकने वाला cleanup हमेशा चलता है। बड़ी टीमें (Flipkart-style Big Billion Days release) production deploy को `if: github.ref == 'refs/heads/main'` से gate करती हैं ताकि feature branch का push कभी prod तक न पहुँचे।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/if-basic.yml
name: if-basic                         # workflow name
on: [push, pull_request]               # two triggers
jobs:
  demo:
    runs-on: ubuntu-24.04              # example runner
    steps:
      - name: Always runs first        # no if: -> implicit success()
        run: echo "start"              # prints start
      - name: Only on main             # branch condition
        if: github.ref == 'refs/heads/main'   # no ${{ }} needed in if:
        run: echo "on main"            # skipped on other branches
      - name: Only on pull requests    # event condition
        if: github.event_name == 'pull_request'   # compare event name
        run: echo "PR build"           # skipped on push
      - name: Might fail               # step that can fail
        id: flaky                      # id lets later steps inspect it
        continue-on-error: true        # failure will not fail the job
        run: exit 1                    # force a failure for demo
      - name: Runs only after failure  # failure branch
        if: failure()                  # true if any previous step failed
        run: echo "something failed"   # still runs
      - name: Cleanup                  # always cleanup
        if: always()                   # runs even when cancelled or failed
        run: echo "cleanup"            # prints cleanup
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/if-advanced.yml
name: ci-cd                            # full pipeline with gated deploy
on:
  push:
    branches: [main]                   # main pushes
    tags: ['v*']                       # version tags
  pull_request:                        # PR validation
jobs:
  test:
    runs-on: ubuntu-24.04              # example runner
    steps:
      - uses: actions/checkout@v4      # source
      - uses: actions/setup-node@v4    # Node toolchain
        with: { node-version: 20, cache: npm }   # inline map form
      - run: npm ci && npm test        # install + test
  deploy:
    needs: test                        # wait for tests
    # job-level if: runs only for pushes to main in THIS repo (not forks, not PRs)
    if: github.event_name == 'push' && github.ref == 'refs/heads/main' && github.repository == 'acme/orders-api'
    runs-on: ubuntu-24.04              # deploy runner
    environment: production            # can require manual approval
    steps:
      - name: Deploy over SSH          # real deploy would go here
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}   # secret in env, not in if:
        run: echo "deploying $GITHUB_SHA"       # placeholder command
  notify:
    needs: [test, deploy]              # depends on both
    # always() so it runs even if needs failed; then inspect results explicitly
    if: ${{ always() && (needs.test.result == 'failure' || needs.deploy.result == 'failure') }}
    runs-on: ubuntu-24.04              # light runner
    steps:
      - name: Slack alert              # message on failure only
        env:
          HOOK: ${{ secrets.SLACK_WEBHOOK }}    # webhook secret
        run: |                         # build and send JSON
          curl -sS -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"Pipeline failed on $GITHUB_REF_NAME\"}" "$HOOK"
```
Example only: repo name and action versions are placeholders; parsed as YAML locally, not run on GitHub.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: run unit tests always, run slow integration tests only on `main` or with a `run-e2e` label: `if: contains(github.event.pull_request.labels.*.name, 'run-e2e')`.
- **React**: deploy preview builds only for same-repo PRs: `if: github.event.pull_request.head.repo.full_name == github.repository`.
- **Nginx / VPS**: reload Nginx only if config changed (use a step output from `git diff`/paths filter).
- **AWS**: `if: github.ref == 'refs/heads/main'` before ECR push / ECS update; use `environment:` approval for prod.
- **Security**: skip steps that use secrets for forked PRs (forks do not get secrets anyway).

```yaml
      - name: Reload nginx only if conf changed    # conditional on previous step output
        if: steps.changes.outputs.nginx == 'true'  # output is a string, compare with quotes
        run: ssh deploy@$HOST 'sudo nginx -t && sudo systemctl reload nginx'   # test before reload
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `if: !startsWith(github.ref, 'refs/tags/')` (leading `!` without wrapper).
✅ Correct: When the expression begins with `!`, use `${{ }}` or quote the whole value; YAML treats a leading `!` as a tag.

❌ Mistake 2: Using `failure()` in a job whose `needs` failed expecting it to run.
✅ Correct: A job with failed `needs` is skipped unless its `if:` contains a status function such as `always()` or `failure()`.

❌ Mistake 3: `if: steps.x.outputs.ok == true` (boolean).
✅ Correct: Outputs are strings; use `== 'true'`.

❌ Mistake 4: Referencing `secrets.X` directly in `if:`.
✅ Correct: Secrets are not available in `if:`. Copy to `env:` and check `env.X != ''`, or use `vars`/inputs.

❌ Mistake 5: Using `always()` when you meant "even on failure but not when cancelled".
✅ Correct: `always()` also runs on cancel. Use `if: success() || failure()` to exclude cancelled runs.

---

## 🧠 Tricky Interview Question
`if: github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'` plus a previous step that failed. Will this step run?

Answer: No (usually). Once an `if:` does not contain a status function, GitHub implicitly adds `success() &&` in front. The earlier failure makes `success()` false, so the step is skipped even though your own condition is true. Write `if: ${{ failure() || (github.ref == ... ) }}` or add `always() &&` explicitly when you want it to run regardless.

---

## ⚫ Interview Questions + Answers

Q1: What is the default `if:`?
A1: `success()`. Skipped if any earlier step (or needed job) failed.

Q2: Do you need `${{ }}` in `if:`?
A2: No, GitHub wraps it automatically. Required only when the expression starts with `!` or contains characters YAML might misparse, or when mixing text.

Q3: Difference between skipped and failed?
A3: Skipped means the condition was false (neutral). Failed means it ran and returned non-zero.

Q4: How to run a cleanup step even if the job was cancelled?
A4: `if: always()`. Be careful: this also runs on cancel; use `${{ !cancelled() }}` to avoid that.

Q5: Can job-level `if:` use `steps`?
A5: No. Job-level `if:` is evaluated before steps exist; it can use github, needs, vars and inputs contexts only.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Gating deploys by branch, tag or event
- Notifying only on failure, cleaning up always
- Skipping expensive jobs for docs-only changes

❌ Avoid when:
- Whole workflow should not run at all (use `on.<event>.paths`/`branches` filters)
- Complex logic better done in a script (compute in a step, output a boolean)
- Hiding security-sensitive logic behind untrusted input expressions

---

## 📊 Visual Diagram
```
            +-----------+
 push main  | job: test | ---- success ----+
            +-----------+                  v
                  |                +----------------+   if: ref==main
               failure             | job: deploy    |-- true --> runs
                  |                +----------------+
                  v                         |  false
        +----------------------+            v
        | job: notify          |         skipped (grey)
        | if: failure() ...    |
        +----------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| if: | Condition to run job/step | Job/step चलाने की शर्त |
| success() | True if all earlier OK | पिछला सब ठीक हो तो true |
| failure() | True if any earlier failed | कोई पिछला fail हो तो true |
| always() | Run regardless of status | हर हाल में चलना |
| Skipped | Not run because condition false | शर्त false होने से न चला |

---

## ⚡ 3-Line Summary
English: `if:` conditionally runs a job or step; the default is `success()`.
Use status functions for failure alerts and cleanup; outputs are strings.
Secrets are not usable in `if:`, and job-level `if:` cannot read `steps`.
Hindi: `if:` job या step को शर्त पर चलाता है; default `success()` है।
Failure alerts और cleanup के लिए status functions लगाओ; outputs string होते हैं।
`if:` में secrets सीधे नहीं चलते, और job-level `if:` `steps` नहीं पढ़ सकता।

---

## ➡️ Next Topic
**261. Contexts in GitHub Actions** — `if:`, `env:` and `with:` all read data from contexts; next we learn the whole context system.
