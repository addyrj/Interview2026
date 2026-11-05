# 268. steps Context
# हिंदी में: steps Context

---

## 🔵 Simple Definition (English)
The `steps` context holds information about steps in the current job that have an `id:` and have already run. For each step you get `steps.<id>.outputs.<name>`, `steps.<id>.outcome` (result before `continue-on-error`) and `steps.<id>.conclusion` (final result after `continue-on-error`).

## 🔵 सरल परिभाषा (Hindi)
`steps` context मौजूदा job के उन steps की जानकारी रखता है जिनमें `id:` है और जो चल चुके हैं। हर step के लिए `steps.<id>.outputs.<name>`, `steps.<id>.outcome` (`continue-on-error` से पहले का result) और `steps.<id>.conclusion` (`continue-on-error` के बाद का अंतिम result) मिलते हैं।

---

## 🔴 Problem it Solves
Steps often depend on each other: the version computed in step 2 is the Docker tag in step 5; a smoke test result decides whether to roll back; a changed-files check decides whether to reload Nginx. Environment variables work but are untyped and easy to pollute; shell state does not carry between steps. `steps` offers explicit, namespaced data passing.

## 🔴 यह क्यों बना? (Hindi)
Steps अक्सर एक-दूसरे पर निर्भर होते हैं: step 2 में निकला version step 5 में Docker tag बनता है; smoke test का नतीजा तय करता है कि rollback हो या नहीं; changed-files check तय करता है कि Nginx reload हो या नहीं। Environment variables चलते हैं पर untyped होते हैं और गंदे हो जाते हैं; shell state steps के बीच नहीं जाती। `steps` साफ़, namespaced data passing देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Give the producing step an id: (letters, digits, - and _)
Step 2 → Inside it write: echo "name=value" >> "$GITHUB_OUTPUT"
Step 3 → Runner records outputs, outcome and conclusion when the step ends
Step 4 → Later steps read ${{ steps.<id>.outputs.name }}
Step 5 → outcome = raw result; conclusion = result after continue-on-error applied
Step 6 → To use in another job, map to jobs.<id>.outputs and read via needs
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Output देने वाले step को id: दो (अक्षर, अंक, - और _)
Step 2 → उसके अंदर लिखो: echo "name=value" >> "$GITHUB_OUTPUT"
Step 3 → Step खत्म होने पर runner outputs, outcome और conclusion दर्ज करता है
Step 4 → बाद के steps ${{ steps.<id>.outputs.name }} पढ़ते हैं
Step 5 → outcome = कच्चा result; conclusion = continue-on-error लगने के बाद का result
Step 6 → दूसरे job में चाहिए तो jobs.<id>.outputs में map करो और needs से पढ़ो
```

---

## 🟡 Real World Example
After deploying to the VPS, a `smoke` step curls `/health` and is marked `continue-on-error: true`. A later step does `if: steps.smoke.outcome == 'failure'` to roll back to the previous image, and the job still ends green or red depending on your design. This pattern is how Swiggy-style teams implement automatic rollback without stopping the pipeline abruptly.

## 🟡 Real Example Hindi mein
VPS पर deploy के बाद `smoke` step `/health` पर curl करता है और `continue-on-error: true` है। बाद का step `if: steps.smoke.outcome == 'failure'` से पिछली image पर rollback करता है। Pipeline अचानक रुके बिना automatic rollback इसी pattern से बनता है, जैसा Swiggy-style टीमें करती हैं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/steps-basic.yml
name: steps-basic                      # workflow name
on: push                               # trigger
jobs:
  demo:
    runs-on: ubuntu-24.04              # example runner
    steps:
      - id: ver                        # id enables steps.ver
        run: echo "version=1.4.${{ github.run_number }}" >> "$GITHUB_OUTPUT"   # create output
      - name: Use the output           # read it
        run: echo "building ${{ steps.ver.outputs.version }}"   # prints 1.4.<n>
      - id: flaky                      # step that may fail
        continue-on-error: true        # job keeps going
        run: exit 1                    # fails on purpose
      - name: Inspect result           # compare outcome vs conclusion
        run: |                         # script
          echo "outcome    = ${{ steps.flaky.outcome }}"      # failure (raw)
          echo "conclusion = ${{ steps.flaky.conclusion }}"   # success (after continue-on-error)
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/steps-advanced.yml
name: deploy-with-rollback             # deploy, smoke test, rollback
on:
  push:
    branches: [main]                   # main only
jobs:
  deploy:
    runs-on: ubuntu-24.04              # example runner
    environment: production            # protected environment
    outputs:
      deployed: ${{ steps.final.outputs.deployed }}   # job output for later jobs
    steps:
      - uses: actions/checkout@v4      # source
      - id: prev                       # remember current version on server
        env:
          HOST: ${{ vars.VPS_HOST }}   # host (not secret)
        run: |                         # script
          PREV=$(ssh deploy@"$HOST" 'cat /srv/app/CURRENT' || echo none)   # read old tag
          echo "tag=$PREV" >> "$GITHUB_OUTPUT"                              # save as output
      - id: ship                       # deploy new version
        env:
          HOST: ${{ vars.VPS_HOST }}
        run: ssh deploy@"$HOST" "/srv/app/deploy.sh ${GITHUB_SHA::7}"   # hypothetical script on server
      - id: smoke                      # health check
        continue-on-error: true        # do not stop; we want to roll back
        run: curl --fail --retry 5 --retry-delay 3 --retry-all-errors https://app.example.com/health   # retry transient errors
      - id: rollback                   # only if smoke failed
        if: steps.smoke.outcome == 'failure' && steps.prev.outputs.tag != 'none'
        env:
          HOST: ${{ vars.VPS_HOST }}
        run: ssh deploy@"$HOST" "/srv/app/deploy.sh ${{ steps.prev.outputs.tag }}"   # redeploy old tag
      - id: final                      # summary output
        if: always()                   # even after failures
        run: |                         # script
          echo "deployed=${{ steps.smoke.outcome == 'success' }}" >> "$GITHUB_OUTPUT"   # true/false string
      - name: Fail the job if we rolled back   # make failure visible
        if: steps.rollback.outcome == 'success'   # rollback step actually ran
        run: echo "Rolled back to ${{ steps.prev.outputs.tag }}" && exit 1   # mark run red
```
Parsed as YAML locally; `/srv/app/deploy.sh` and the SSH setup are hypothetical (SSH key/known_hosts setup omitted for brevity); not executed.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: step outputs for semver (`npm pkg get version`) used in Docker tags and release notes.
- **React**: `steps.build.outcome` + bundle size output compared against a budget.
- **Nginx/VPS**: output `changed=true` when `nginx.conf` differs, then `if: steps.conf.outputs.changed == 'true'` for `nginx -t && reload`.
- **AWS**: `steps.login.outputs.registry` from `amazon-ecr-login` becomes the image prefix.
- **Security**: outputs appear in logs and may be seen by later actions; do not output secrets. Use `::add-mask::` before writing sensitive-looking values.

```yaml
      - id: ecr                        # login action exposes registry output
        uses: aws-actions/amazon-ecr-login@v2   # example version
      - run: docker push ${{ steps.ecr.outputs.registry }}/orders-api:${{ github.sha }}   # use its output
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `id:` on the step.
✅ Correct: Without `id`, the step is absent from `steps`.

❌ Mistake 2: Using `echo "::set-output name=x::y"`.
✅ Correct: `set-output` is deprecated; use `echo "x=y" >> "$GITHUB_OUTPUT"`.

❌ Mistake 3: Expecting `steps.x.outputs` in another job.
✅ Correct: Map to `jobs.<id>.outputs` and read via `needs`.

❌ Mistake 4: Checking `conclusion == 'failure'` with `continue-on-error: true`.
✅ Correct: Conclusion becomes `success`; use `outcome` to see the real failure.

❌ Mistake 5: Multi-line output with a plain `echo "x=line1\nline2"`.
✅ Correct: Use delimiter syntax: `{ echo 'x<<EOF'; cat file; echo EOF; } >> "$GITHUB_OUTPUT"` (random delimiter if content is untrusted).

---

## 🧠 Tricky Interview Question
Step `lint` has `continue-on-error: true` and fails. The next step has `if: steps.lint.conclusion == 'failure'`. Does it run?

Answer: No. `continue-on-error` converts the failure into conclusion `success` while `outcome` stays `failure`. The check should be `steps.lint.outcome == 'failure'`. Also remember the implicit `success()` applies to the job's overall status, which is still success here, so the step is eligible to run.

---

## ⚫ Interview Questions + Answers

Q1: Possible values of outcome/conclusion?
A1: `success`, `failure`, `cancelled`, `skipped`.

Q2: How do you set a step output?
A2: Append `name=value` to the file at `$GITHUB_OUTPUT`.

Q3: Can steps read outputs from a later step?
A3: No, only from steps that already ran (earlier in order).

Q4: Output vs `$GITHUB_ENV`?
A4: Output is namespaced, read through the `steps` context, can be exported at job level; `$GITHUB_ENV` creates env vars for later steps with global names.

Q5: Are outputs always strings?
A5: Yes. Use `fromJSON()` for structured data and compare booleans as `'true'`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Passing computed values between steps
- Reacting to the real result of an allowed-to-fail step
- Using outputs of actions (login registry, cache-hit, metadata tags)

❌ Avoid when:
- You need the value in another job without mapping to job outputs
- Data is sensitive
- Large payloads (use files/artifacts)

---

## 📊 Visual Diagram
```
 step[id=ver]  --> $GITHUB_OUTPUT: version=1.4.7 --+
 step[id=smoke] (continue-on-error) --------------+|
        outcome=failure  conclusion=success        ||
                                                   vv
 later step:  ${{ steps.ver.outputs.version }}   if: steps.smoke.outcome == 'failure'
                                                   |
 job outputs: deployed: ${{ steps.final.outputs.deployed }} --> needs.deploy.outputs.deployed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| steps | Context of earlier steps | पिछले steps का context |
| outcome | Raw step result | कच्चा result |
| conclusion | Result after continue-on-error | continue-on-error के बाद का result |
| $GITHUB_OUTPUT | File to write outputs | Outputs लिखने की file |
| continue-on-error | Don't fail job on step failure | Step fail पर भी job न रोकना |

---

## ⚡ 3-Line Summary
English: `steps.<id>` exposes outputs, outcome and conclusion of earlier steps in the job.
Write outputs via `$GITHUB_OUTPUT`; use `outcome` to see failures hidden by `continue-on-error`.
Outputs are strings and need `id:`; map them for other jobs.
Hindi: `steps.<id>` job के पिछले steps के outputs, outcome और conclusion देता है।
Outputs `$GITHUB_OUTPUT` से लिखो; `continue-on-error` से छुपी failure देखने के लिए `outcome` इस्तेमाल करो।
Outputs strings हैं और `id:` चाहिए; दूसरे jobs के लिए map करो।

---

## ➡️ Next Topic
**269. inputs Context** — values supplied to manual runs and reusable workflows.
