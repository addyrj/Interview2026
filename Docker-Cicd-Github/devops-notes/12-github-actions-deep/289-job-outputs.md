# 289. Job Outputs
# हिंदी में: Job Outputs (job के नतीजे)

---

## 🔵 Simple Definition (English)
Job outputs are named string values that a job exposes under `jobs.<job_id>.outputs`, so other jobs can read them through `needs.<job_id>.outputs.<name>`. They are the standard way to pass small data (a version, a Docker tag, a flag like `changed=true`) between jobs. Each output is mapped from a step output, e.g. `version: ${{ steps.v.outputs.version }}`. Limits: values are strings, up to about 1 MB per job (total about 50 MB per run), and secrets are not passed through.

## 🔵 सरल परिभाषा (Hindi)
Job outputs नाम वाली string values हैं जिन्हें job `jobs.<job_id>.outputs` में expose करता है, ताकि दूसरे jobs उन्हें `needs.<job_id>.outputs.<name>` से पढ़ सकें। छोटा data (version, Docker tag, `changed=true` जैसा flag) jobs के बीच भेजने का यही standard तरीका है। हर output किसी step output से map होता है, जैसे `version: ${{ steps.v.outputs.version }}`। सीमाएँ: values string होती हैं, लगभग 1 MB प्रति job (पूरे run में लगभग 50 MB), और secrets पास नहीं होते।

---

## 🔴 Problem it Solves
Each job runs on its own VM, so shell variables, files and `$GITHUB_ENV` are not shared. You often must compute something once (e.g. the image tag `1.4.2-abc123`) and reuse it in later jobs (deploy, notify). Recomputing in each job risks mismatches (timestamps differ!). Outputs give one computed value, read by many jobs.

## 🔴 यह क्यों बना? (Hindi)
हर job अपनी VM पर चलता है, इसलिए shell variables, files और `$GITHUB_ENV` साझा नहीं होते। अक्सर कोई चीज़ एक बार निकालनी होती है (जैसे image tag `1.4.2-abc123`) और बाद के jobs (deploy, notify) में इस्तेमाल करनी होती है। हर job में दोबारा निकालने पर mismatch का खतरा (timestamps अलग निकलते हैं!)। Outputs एक बार निकली value कई jobs को देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → In job A, a step writes:  echo "tag=1.4.2" >> "$GITHUB_OUTPUT"
Step 2 → That step has an id (id: meta) so it can be referenced
Step 3 → Job A declares outputs:   outputs: { tag: ${{ steps.meta.outputs.tag }} }
Step 4 → Job A finishes; GitHub stores the output values for the run
Step 5 → Job B has  needs: A   (required, otherwise it is not available / ordering unknown)
Step 6 → Job B reads ${{ needs.A.outputs.tag }}  (in env:, with:, if:, run: via env)
Step 7 → If A was skipped/failed, outputs are empty strings
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Job A में एक step लिखता है:  echo "tag=1.4.2" >> "$GITHUB_OUTPUT"
Step 2 → उस step पर id होती है (id: meta) ताकि reference हो सके
Step 3 → Job A outputs declare करता है: outputs: { tag: ${{ steps.meta.outputs.tag }} }
Step 4 → Job A खत्म होने पर GitHub values को run के लिए रख लेता है
Step 5 → Job B में  needs: A  ज़रूरी है (वरना उपलब्ध नहीं / क्रम तय नहीं)
Step 6 → Job B ${{ needs.A.outputs.tag }} पढ़ता है (env:, with:, if:, या env के रास्ते run: में)
Step 7 → अगर A skip/fail हुआ तो outputs खाली string होते हैं
```

---

## 🟡 Real World Example
A Flipkart-like release pipeline: job `meta` reads `package.json` and `git rev-parse --short HEAD` to build tag `2.7.0-a1b2c3d`. Job `docker` pushes `shop-api:2.7.0-a1b2c3d`, job `deploy` SSHes to the VPS and runs that exact tag, and job `notify` posts the same tag to Slack. One computation, four consumers, zero mismatch.

## 🟡 Real Example Hindi mein
Flipkart जैसी release pipeline: job `meta` `package.json` और `git rev-parse --short HEAD` पढ़कर tag `2.7.0-a1b2c3d` बनाता है। Job `docker` `shop-api:2.7.0-a1b2c3d` push करता है, job `deploy` VPS पर SSH करके वही tag चलाता है, और job `notify` वही tag Slack पर भेजता है। एक गणना, चार उपभोक्ता, कोई mismatch नहीं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/job-outputs-basic.yml
name: job-outputs-basic                   # workflow name
on: [workflow_dispatch]                   # manual trigger for the demo
jobs:
  producer:
    runs-on: ubuntu-latest                # runner for job 1
    outputs:                              # values exposed to other jobs
      greeting: ${{ steps.make.outputs.greeting }}   # map from step output
    steps:
      - id: make                          # step id used in the mapping above
        run: echo "greeting=hello-from-job-1" >> "$GITHUB_OUTPUT"   # write key=value
  consumer:
    needs: producer                       # must declare dependency to read outputs
    runs-on: ubuntu-latest                # runner for job 2
    steps:
      - run: echo "Got ${{ needs.producer.outputs.greeting }}"   # read the value
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/release-meta.yml
# Compute version/tag once, build image, deploy only if the API changed
name: release-meta                        # workflow name
on:
  push:
    branches: [main]                      # release from main
permissions:
  contents: read                          # checkout only
jobs:
  meta:
    runs-on: ubuntu-latest
    outputs:                              # all exposed values
      version: ${{ steps.v.outputs.version }}       # package.json version
      tag: ${{ steps.v.outputs.tag }}               # image tag
      api_changed: ${{ steps.diff.outputs.api_changed }}   # 'true' / 'false'
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2                  # need the previous commit for diff
      - id: v                             # step id
        run: |
          VERSION=$(node -p "require('./package.json').version")   # read version
          SHORT=$(git rev-parse --short HEAD)                      # short commit id
          echo "version=$VERSION" >> "$GITHUB_OUTPUT"              # output 1
          echo "tag=$VERSION-$SHORT" >> "$GITHUB_OUTPUT"           # output 2
      - id: diff                          # detect changes in api/
        run: |
          if git diff --quiet HEAD~1 HEAD -- api/; then            # no change?
            echo "api_changed=false" >> "$GITHUB_OUTPUT"
          else
            echo "api_changed=true" >> "$GITHUB_OUTPUT"
          fi
  build:
    needs: meta                           # reads meta outputs
    if: needs.meta.outputs.api_changed == 'true'   # outputs are strings!
    runs-on: ubuntu-latest
    env:
      TAG: ${{ needs.meta.outputs.tag }}  # pass via env, not inline in script
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t shop-api:"$TAG" api/   # use the shared tag
  deploy:
    needs: [meta, build]                  # needs both (to read meta AND wait for build)
    if: needs.meta.outputs.api_changed == 'true'
    runs-on: ubuntu-latest
    environment: production               # approvals / secrets scope
    steps:
      - run: echo "Deploying ${{ needs.meta.outputs.tag }}"   # same tag everywhere
```

---

## 🟠 My Stack Integration
- **Docker + VPS**: compute image tag once, build/push in one job, deploy in another job via SSH with the same tag.
- **Monorepo (React, Node, FastAPI)**: a `changes` job outputs `web`, `api`, `fastapi` flags (like dorny/paths-filter) so only changed parts build.
- **AWS**: a Terraform job outputs `alb_dns` (non-secret), consumed by a smoke-test job.
- **Nginx**: output the new release folder name `releases/20261105-1200`, symlink in the deploy job.

```yaml
# Snippet: use outputs in a matrix (JSON string -> fromJSON)
  plan:
    runs-on: ubuntu-latest
    outputs:
      services: ${{ steps.s.outputs.services }}    # JSON array string
    steps:
      - id: s
        run: echo 'services=["web","api","fastapi"]' >> "$GITHUB_OUTPUT"
  build:
    needs: plan
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: ${{ fromJSON(needs.plan.outputs.services) }}   # dynamic matrix
    steps:
      - run: echo "building ${{ matrix.service }}"
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `needs:` for the job that reads outputs. The expression yields empty.
✅ Correct: Always list the producer in `needs`.

❌ Mistake 2: Comparing `needs.x.outputs.flag == true`. It is a string.
✅ Correct: Compare with `'true'`.

❌ Mistake 3: Writing outputs the old way (`::set-output`), which is deprecated and disabled.
✅ Correct: Use `echo "k=v" >> "$GITHUB_OUTPUT"`.

❌ Mistake 4: Putting secrets in outputs. GitHub masks and may drop them; they can leak via logs of consumers.
✅ Correct: Pass secrets using the `secrets` context in each job, or pass only a non-secret reference.

❌ Mistake 5: Passing multi-line values with plain `key=value`.
✅ Correct: Use the delimiter form: `{ echo "notes<<EOF"; cat notes.txt; echo "EOF"; } >> "$GITHUB_OUTPUT"`.

---

## 🧠 Tricky Interview Question
Job `deploy` has `needs: build`, and `build` has `needs: meta`. Deploy uses `${{ needs.meta.outputs.tag }}` and gets an empty string. Why?

Answer: `needs.<id>` contains only the jobs listed directly in that job's own `needs`. Transitive dependencies are not included in the context. Fix: `needs: [meta, build]`, or forward the value (`build` re-exposes it as its own output). Another cause could be that `meta` failed/skipped, giving empty values; also check the job-level `outputs:` mapping exists, because step outputs alone do not cross job boundaries.

---

## ⚫ Interview Questions + Answers

Q1: Difference between step outputs and job outputs?
A1: Step outputs live within a job (`steps.<id>.outputs`). Job outputs are explicitly declared and exposed to other jobs via `needs`.

Q2: How do you set an output from a shell step?
A2: Append `name=value` to the file `$GITHUB_OUTPUT`.

Q3: What data types are possible?
A3: Only strings. Use JSON and `fromJSON()` / `toJSON()` for structured data.

Q4: Can a reusable workflow expose outputs?
A4: Yes, through `on.workflow_call.outputs`, mapped from its jobs' outputs; callers read `needs.<call_job>.outputs`.

Q5: Why use env: instead of direct `${{ }}` in `run`?
A5: Direct interpolation pastes text into the script, enabling script injection if the value is attacker-controlled (branch name, PR title). Env variables are passed as data.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Passing small values: versions, tags, flags, URLs, JSON lists.
- Driving `if:` conditions and dynamic matrices.

❌ Avoid when:
- Passing files or big data (artifacts).
- Passing secrets.
- Values larger than the 1 MB output limit.

---

## 📊 Visual Diagram
```
  job: meta                                job: deploy (needs: meta)
 +-----------------------------+          +--------------------------+
 | step id=v                   |          | ${{ needs.meta.outputs.  |
 |  echo "tag=1.4.2-ab12"      |          |        tag }}  = 1.4.2-ab12
 |   >> $GITHUB_OUTPUT         |          +------------^-------------+
 +--------------+--------------+                       |
                | steps.v.outputs.tag                  |
                v                                      |
 outputs:  tag: ${{ steps.v.outputs.tag }} ------------+
          (stored by GitHub for the workflow run)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `jobs.<id>.outputs` | Values a job exposes | Job जो values बाहर देता है |
| `$GITHUB_OUTPUT` | File to write step outputs | Step output लिखने की file |
| `needs` context | Outputs of direct dependencies | सीधी dependencies के outputs |
| `fromJSON()` | Parse string to object | String को object बनाना |
| Script injection | Untrusted text run as code | अविश्वसनीय text का code बन जाना |
| `id` | Step identifier | Step की पहचान |

---

## ⚡ 3-Line Summary
English: Job outputs pass small string values to other jobs via `needs.<job>.outputs.<name>`.
English: Write with `$GITHUB_OUTPUT`, map in `outputs:`, and list the producer in `needs`.
English: Compare as strings, avoid secrets, and use artifacts for files.
Hindi: Job outputs छोटी string values को `needs.<job>.outputs.<name>` से दूसरे jobs तक पहुँचाते हैं।
Hindi: `$GITHUB_OUTPUT` से लिखें, `outputs:` में map करें, और producer को `needs` में रखें।
Hindi: Strings की तरह compare करें, secrets न भेजें, और files के लिए artifacts इस्तेमाल करें।

---

## ➡️ Next Topic
**290. Step Outputs** — how values are produced and consumed inside one job.
