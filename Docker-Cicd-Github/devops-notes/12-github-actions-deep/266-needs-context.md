# 266. needs Context
# हिंदी में: needs Context

---

## 🔵 Simple Definition (English)
The `needs` context contains the outputs and results of jobs listed in the current job's `needs:` key. You read `needs.<job_id>.outputs.<name>` to get data and `needs.<job_id>.result` to know if that job was `success`, `failure`, `cancelled` or `skipped`.

## 🔵 सरल परिभाषा (Hindi)
`needs` context में उन jobs के outputs और results होते हैं जो मौजूदा job की `needs:` key में लिखे हैं। डेटा के लिए `needs.<job_id>.outputs.<name>` और job का नतीजा (`success`, `failure`, `cancelled`, `skipped`) जानने के लिए `needs.<job_id>.result` पढ़ते हैं।

---

## 🔴 Problem it Solves
Jobs run on separate machines. A `build` job computes an image tag, but the `deploy` job runs on a fresh runner and cannot see files, env vars or step data from `build`. You need an official channel to pass small values (version, tag, "changed?" flag) and to react to success or failure of upstream jobs.

## 🔴 यह क्यों बना? (Hindi)
Jobs अलग-अलग machines पर चलते हैं। `build` job image tag निकालता है, पर `deploy` job नए runner पर चलता है और `build` की files, env vars या step data नहीं देख पाता। छोटी values (version, tag, "बदला क्या?" flag) भेजने और upstream jobs के success/failure पर प्रतिक्रिया देने के लिए official तरीका चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Producer step writes: echo "tag=abc123" >> "$GITHUB_OUTPUT"  (step needs an id)
Step 2 → Producer job maps it: jobs.build.outputs.tag: ${{ steps.meta.outputs.tag }}
Step 3 → Consumer job declares needs: build (this also orders execution)
Step 4 → Consumer reads ${{ needs.build.outputs.tag }}
Step 5 → needs.build.result tells success/failure/cancelled/skipped
Step 6 → If build fails, consumer is skipped unless its if: has always()/failure()
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Producer step लिखता है: echo "tag=abc123" >> "$GITHUB_OUTPUT"  (step को id चाहिए)
Step 2 → Producer job map करता है: jobs.build.outputs.tag: ${{ steps.meta.outputs.tag }}
Step 3 → Consumer job needs: build लिखता है (इससे execution का क्रम भी बनता है)
Step 4 → Consumer ${{ needs.build.outputs.tag }} पढ़ता है
Step 5 → needs.build.result से success/failure/cancelled/skipped पता चलता है
Step 6 → build fail हो तो consumer skip होता है, जब तक उसके if: में always()/failure() न हो
```

---

## 🟡 Real World Example
A monorepo pipeline has `changes` (detect which folders changed), `test-api`, `test-web`, then `deploy`. `changes` outputs `api=true`, `web=false`; `test-web` runs `if: needs.changes.outputs.web == 'true'`. A final `notify` job uses `needs.*.result` to post one Slack summary. This saves CI minutes on large Indian-startup monorepos with hundreds of commits a day.

## 🟡 Real Example Hindi mein
एक monorepo pipeline में `changes` (कौन से folders बदले), `test-api`, `test-web`, फिर `deploy` हैं। `changes` outputs देता है `api=true`, `web=false`; `test-web` में `if: needs.changes.outputs.web == 'true'`। अंत में `notify` job `needs.*.result` से एक Slack summary भेजता है। रोज़ सैकड़ों commits वाले बड़े monorepos में इससे CI minutes बचते हैं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/needs-basic.yml
name: needs-basic                      # workflow name
on: push                               # trigger
jobs:
  build:
    runs-on: ubuntu-24.04              # example runner
    outputs:                           # values exposed to other jobs
      tag: ${{ steps.meta.outputs.tag }}   # map step output to job output
    steps:
      - id: meta                       # id is required to read steps.meta
        run: echo "tag=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"   # write output (name=value)
  deploy:
    needs: build                       # wait for build and unlock needs.build
    runs-on: ubuntu-24.04              # new, clean runner
    steps:
      - run: echo "Deploy tag ${{ needs.build.outputs.tag }}"      # read output
      - run: echo "build result = ${{ needs.build.result }}"       # success
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/needs-advanced.yml
name: monorepo-ci                      # change detection + fan-in
on:
  push:
    branches: [main]                   # main
  pull_request:                        # PRs too
jobs:
  changes:
    runs-on: ubuntu-24.04              # example runner
    outputs:
      api: ${{ steps.f.outputs.api }}  # 'true' or 'false'
      web: ${{ steps.f.outputs.web }}  # 'true' or 'false'
    steps:
      - uses: actions/checkout@v4      # needed for the filter action
      - id: f                          # step id
        uses: dorny/paths-filter@v3    # third-party action; pin to SHA in production
        with:
          filters: |                   # path rules (YAML string)
            api:
              - 'api/**'
            web:
              - 'web/**'
  test-api:
    needs: changes                     # depends on detection
    if: needs.changes.outputs.api == 'true'   # outputs are strings
    runs-on: ubuntu-24.04              # runner
    steps:
      - uses: actions/checkout@v4      # source
      - run: cd api && npm ci && npm test   # Node API tests
  test-web:
    needs: changes                     # depends on detection
    if: needs.changes.outputs.web == 'true'
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: cd web && npm ci && npm run build   # React build
  deploy:
    needs: [test-api, test-web]        # fan-in: wait for both
    # skipped jobs have result 'skipped'; allow skipped but block failures
    if: ${{ !cancelled() && !contains(needs.*.result, 'failure') && github.ref == 'refs/heads/main' }}
    runs-on: ubuntu-24.04
    steps:
      - run: echo "deploying; api=${{ needs.test-api.result }} web=${{ needs.test-web.result }}"
  notify:
    needs: [test-api, test-web, deploy]    # observe everything
    if: ${{ always() }}                # run even on failure
    runs-on: ubuntu-24.04
    steps:
      - env:
          RESULTS: ${{ toJSON(needs) }}    # whole needs context as JSON
        run: echo "$RESULTS" | head -c 600   # summary (no secrets inside needs)
```
Parsed as YAML locally; not run on GitHub. `dorny/paths-filter` is a third-party example; verify its inputs for your version.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: `build` outputs the image digest; `deploy` pulls `image@digest` (immutable) on the VPS.
- **React**: `build` uploads `dist` as an artifact; `deploy` downloads it (files go via artifacts, small values via outputs).
- **Nginx/VPS**: `needs.test.result == 'success'` gate before `nginx -t && reload`.
- **AWS**: `plan` job outputs "changed" flag; `apply` waits for environment approval.
- **Security**: job outputs are visible in logs/UI and cannot carry secrets (they are redacted or blocked); share secrets by re-referencing `secrets`.

```yaml
      - name: Pull exact image built earlier     # use digest from needs
        run: ssh deploy@"$HOST" "docker pull ghcr.io/acme/api@${{ needs.build.outputs.digest }}"   # immutable reference
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Reading `needs.build.outputs.x` without `build` in `needs:`.
✅ Correct: Only jobs listed in `needs` (direct dependencies) are in the context; transitive jobs must be listed too.

❌ Mistake 2: Forgetting `jobs.<id>.outputs` mapping.
✅ Correct: A step output is not visible to other jobs until mapped under `outputs:`.

❌ Mistake 3: `if: needs.changes.outputs.web` expecting boolean false for `'false'`.
✅ Correct: The string `'false'` is truthy. Compare `== 'true'`.

❌ Mistake 4: Notify job without `always()`.
✅ Correct: Otherwise it is skipped when upstream jobs fail, which is exactly when you need it.

❌ Mistake 5: Passing big files through outputs.
✅ Correct: Outputs are small strings (limit ~1 MB per job, 50 MB per run); use artifacts for files.

---

## 🧠 Tricky Interview Question
`test-web` is skipped (no web changes). `deploy` has `needs: [test-api, test-web]` and no `if:`. Does deploy run?

Answer: No. With the implicit `success()` condition, a skipped dependency causes deploy to be skipped too, even though nothing failed. Fix with an explicit condition such as `if: ${{ !cancelled() && !contains(needs.*.result, 'failure') }}` so skipped counts as acceptable but failures still block.

---

## ⚫ Interview Questions + Answers

Q1: What does `needs.<job>.result` contain?
A1: One of `success`, `failure`, `cancelled`, `skipped`.

Q2: Does `needs:` order execution?
A2: Yes, jobs without `needs` run in parallel; `needs` creates the dependency graph (DAG).

Q3: How do you read outputs from a reusable workflow?
A3: The caller job uses `needs.<call-job>.outputs.<name>` after the reusable workflow declares `on.workflow_call.outputs`.

Q4: Can `needs` create cycles?
A4: No; GitHub rejects circular dependencies when validating the workflow.

Q5: Is `needs` available in `jobs.<id>.if`?
A5: Yes (with github, vars, inputs), but `steps` and `env` are not.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Passing small values (tags, digests, flags) between jobs
- Fan-in jobs that react to many upstream results
- Skipping jobs based on change detection

❌ Avoid when:
- Passing files (use artifacts or cache)
- Passing secrets (reference `secrets` again)
- Everything could be steps in one job (simpler and faster)

---

## 📊 Visual Diagram
```
 changes --outputs {api,web}--+--> test-api (if api=='true') --+
    |                         |                                  |
    |                         +--> test-web (if web=='true') ----+--> deploy --> notify(always)
    v                                                                  ^
 needs.changes.outputs.*                          needs.*.result  <------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| needs | Job dependency list | Job dependency की list |
| outputs | Values a job exposes | Job द्वारा दी गई values |
| result | Final status of a job | Job का अंतिम status |
| Fan-in | Many jobs feeding one | कई jobs का एक में मिलना |
| DAG | Directed acyclic graph | बिना चक्र वाला graph |

---

## ⚡ 3-Line Summary
English: `needs` passes outputs and result of upstream jobs to downstream jobs.
Map step outputs to job outputs first; outputs are strings.
Use `always()` or explicit result checks when skipped or failed jobs matter.
Hindi: `needs` upstream jobs के outputs और result को downstream jobs तक पहुँचाता है।
पहले step outputs को job outputs में map करो; outputs strings होते हैं।
Skipped या failed jobs मायने रखें तो `always()` या साफ़ result checks लगाओ।

---

## ➡️ Next Topic
**267. runner Context** — information about the machine that executes your job.
