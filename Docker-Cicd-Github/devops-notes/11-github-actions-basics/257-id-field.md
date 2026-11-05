# 257. id: Field
# हिंदी में: id: Field (step की पहचान)

---

## 🔵 Simple Definition (English)
`id:` gives a **step** a unique identifier inside its job so that later steps can reference it through the `steps` context: `steps.<id>.outputs.<name>`, `steps.<id>.outcome`, and `steps.<id>.conclusion`. (Job ids are the keys under `jobs:` and are used by `needs`.) Without an `id`, you cannot read a step's outputs.

## 🔵 सरल परिभाषा (Hindi)
`id:` job के अंदर **step** को unique पहचान देता है ताकि बाद के steps `steps` context से उसे बुला सकें: `steps.<id>.outputs.<name>`, `steps.<id>.outcome` और `steps.<id>.conclusion`। (Job ids `jobs:` के नीचे की keys हैं और `needs` में काम आती हैं।) `id` के बिना आप किसी step के outputs नहीं पढ़ सकते।

---

## 🔴 Problem it Solves
Steps are isolated shell processes. You often compute something in one step (a version string, a Docker digest, a changed-files list, whether cache hit) and need it in a later step's `with:`, `if:` or `env:`. Without an identifier there is no way to address "that step's result". `id` is the handle that connects steps: it makes data flow explicit and lets you branch on what actually happened (`cache-hit`, `outcome`).

## 🔴 यह क्यों बना? (Hindi)
Steps अलग-अलग shell processes हैं। अक्सर एक step में कुछ निकालते हैं (version string, Docker digest, बदली files की सूची, cache hit हुआ या नहीं) और उसे बाद के step के `with:`, `if:` या `env:` में चाहिए होता है। पहचान के बिना "उस step का नतीजा" बुलाने का तरीका नहीं है। `id` वह handle है जो steps जोड़ता है: data flow स्पष्ट बनाता है और असल घटना (`cache-hit`, `outcome`) के आधार पर शाखा लेने देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You add `id: meta` to a step (letters, numbers, - and _ ; unique within the job; must start with a letter or _).
Step 2 → The step writes outputs: `echo "version=1.4.0" >> "$GITHUB_OUTPUT"` (shell) or an action sets outputs itself.
Step 3 → Runner records them under the steps context for this job.
Step 4 → Later steps read `${{ steps.meta.outputs.version }}`.
Step 5 → `steps.meta.outcome` = result BEFORE continue-on-error is applied; `conclusion` = AFTER (success|failure|cancelled|skipped).
Step 6 → Use in conditions: `if: steps.cache.outputs.cache-hit != 'true'`.
Step 7 → To pass a value to another JOB, map it to `jobs.<job>.outputs` and read via `needs.<job>.outputs`.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Step में `id: meta` जोड़ें (अक्षर, अंक, - और _ ; job में unique; अक्षर या _ से शुरू)।
Step 2 → Step outputs लिखता है: `echo "version=1.4.0" >> "$GITHUB_OUTPUT"` (shell) या action खुद outputs देता है।
Step 3 → Runner इन्हें इस job के steps context में दर्ज करता है।
Step 4 → बाद के steps `${{ steps.meta.outputs.version }}` पढ़ते हैं।
Step 5 → `steps.meta.outcome` = continue-on-error लगने से पहले का नतीजा; `conclusion` = बाद का (success|failure|cancelled|skipped)।
Step 6 → Conditions में: `if: steps.cache.outputs.cache-hit != 'true'`।
Step 7 → दूसरे JOB को value देने के लिए उसे `jobs.<job>.outputs` में map करें और `needs.<job>.outputs` से पढ़ें।
```

---

## 🟡 Real World Example
A React + Node monorepo pipeline restores `node_modules` via `actions/cache` with `id: npm-cache`. A later step `npm ci` has `if: steps.npm-cache.outputs.cache-hit != 'true'` so the install is skipped on cache hits, saving 90 seconds. Another step with `id: ver` computes the version from `package.json` (`jq -r .version`) and that value tags the Docker image and names the release artifact.

## 🟡 Real Example Hindi mein
एक React + Node monorepo pipeline `actions/cache` से `node_modules` restore करता है और उसका `id: npm-cache` है। बाद का `npm ci` step `if: steps.npm-cache.outputs.cache-hit != 'true'` के साथ है, इसलिए cache hit पर install छूट जाता है और 90 सेकंड बचते हैं। एक और step `id: ver` से `package.json` (`jq -r .version`) से version निकालता है और वही Docker image का tag तथा release artifact का नाम बनता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/id-basic.yml
name: Id Basic                            # workflow name
on: [push]                                # trigger

jobs:
  demo:                                   # job id
    runs-on: ubuntu-latest                # runner
    steps:
      - id: greet                         # step id: needed to read this step's outputs
        run: echo "message=hello-from-step" >> "$GITHUB_OUTPUT"   # write output name=value

      - name: Use the output              # later step
        run: echo "Got ${{ steps.greet.outputs.message }}"        # read it via steps.<id>.outputs.<name>
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/id-advanced.yml
name: Id Advanced
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:                              # JOB outputs: publish step values to other jobs
      version: ${{ steps.ver.outputs.version }}   # map step output -> job output
      image: ${{ steps.ver.outputs.image }}
    steps:
      - uses: actions/checkout@v4

      - id: ver                           # compute version + image name once
        env:
          REPO: ${{ github.repository }}  # via env to stay injection-safe
        run: |
          v=$(jq -r .version package.json)                       # read version from package.json
          echo "version=$v" >> "$GITHUB_OUTPUT"                  # step output 1
          echo "image=ghcr.io/${REPO,,}:$v" >> "$GITHUB_OUTPUT"  # step output 2 (${REPO,,} = lowercase)

      - id: npm-cache                     # cache step with id so we can read cache-hit
        uses: actions/cache@v4
        with:
          path: node_modules              # what to cache
          key: node-${{ runner.os }}-${{ hashFiles('package-lock.json') }}   # cache key from lock file

      - name: Install only on cache miss
        if: steps.npm-cache.outputs.cache-hit != 'true'   # skip when restored from cache
        run: npm ci

      - id: tests                         # id on a step that may fail
        continue-on-error: true           # do not fail the job immediately
        run: npm test

      - name: Report test result
        run: |
          echo "outcome=${{ steps.tests.outcome }} conclusion=${{ steps.tests.conclusion }}"  # outcome=failure conclusion=success

      - name: Fail now if tests really failed
        if: steps.tests.outcome == 'failure'          # outcome ignores continue-on-error
        run: exit 1

  deploy:
    needs: build                          # job id used here (not step id)
    runs-on: ubuntu-latest
    steps:
      - name: Show what we would deploy
        run: echo "Deploy ${{ needs.build.outputs.image }}"   # job outputs come through needs
```

(YAML parsed locally; `jq` expressions and `${REPO,,}` use bash 4 features present on ubuntu runners; syntax checked with `bash -n`, not executed on GitHub.)

---

## 🟠 My Stack Integration
- **Node.js / React:** `id: ver` from `package.json`; image tag and S3 folder use `steps.ver.outputs.version`.
- **FastAPI:** `id: ver` from `pyproject.toml`/git describe; reuse in Docker `build-args`.
- **Docker:** `docker/build-push-action` with `id: build` exposes `steps.build.outputs.digest` for signing (cosign) or ECS deploy by digest.
- **VPS / AWS:** `id: deploy` records the previous image tag in outputs so a failed smoke test can trigger rollback with the saved tag.

```yaml
# Rollback pattern using ids
- id: prev                                # remember currently running tag on the VPS
  run: echo "tag=$(ssh deploy@$HOST 'cat /srv/app/CURRENT_TAG')" >> "$GITHUB_OUTPUT"
  env: { HOST: "${{ secrets.VPS_HOST }}" }
- id: smoke                               # new version health check
  continue-on-error: true
  run: curl --fail https://app.example.com/health
- if: steps.smoke.outcome == 'failure'    # smoke failed -> roll back to the saved tag
  run: echo "rollback to ${{ steps.prev.outputs.tag }}"
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Reading `steps.build.outputs.x` without `id: build` on that step.
✅ Correct: Add `id`; ids are case-sensitive and must match exactly.

❌ Mistake 2: Duplicate step ids in the same job.
✅ Correct: Unique within the job (same id in different jobs is fine).

❌ Mistake 3: Using `::set-output` (deprecated, removed).
✅ Correct: Append to `$GITHUB_OUTPUT`; multi-line values need a delimiter (`name<<EOF ... EOF`).

❌ Mistake 4: Expecting `steps.x.outputs` to be visible in another job.
✅ Correct: Declare `jobs.<job>.outputs` and use `needs`.

❌ Mistake 5: Treating output cache-hit as boolean - it is a string `'true'`.
✅ Correct: Compare with `== 'true'`.

---

## 🧠 Tricky Interview Question
A step has `continue-on-error: true` and fails. What are `steps.x.outcome` and `steps.x.conclusion`, and does the job fail?

Answer: `outcome` is `failure` (the real result before `continue-on-error` is applied); `conclusion` is `success` (after being applied). The job does not fail because of that step. Use `outcome` when you must know the true result (to decide on rollback or to fail later).

---

## ⚫ Interview Questions + Answers

Q1: Difference between step id and job id?
A1: Step id is under `steps[].id` and is used in the `steps` context within one job. Job id is the key under `jobs:`; used in `needs` and `needs.<id>.outputs`.

Q2: How do I set a multiline output?
A2: `{ echo "notes<<EOF"; cat CHANGELOG.md; echo "EOF"; } >> "$GITHUB_OUTPUT"` (choose a random delimiter for untrusted content).

Q3: What can the `steps` context hold?
A3: `outputs`, `outcome`, `conclusion` per step id.

Q4: Are outputs strings?
A4: Yes, always strings; use `fromJSON()` for structures and compare booleans as strings.

Q5: Max output size?
A5: About 1 MB per job output, 50 MB total per run (check current docs); use artifacts for large data.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a later step or job to consume a result, or branch on step status.
- Using cache-hit, digest, version, changed-files outputs.

❌ Avoid when:
- Nothing reads the step - extra ids add noise.
- You need to pass secrets between jobs (outputs are not secret-safe; use a secret store).

---

## 📊 Visual Diagram

```
 job: build
 ┌────────────────────────────────────────────────────────────┐
 │ step id: ver ──► GITHUB_OUTPUT: version=1.4.0              │
 │       │                                                    │
 │       ├──► step id: npm-cache ... cache-hit=true           │
 │       │          └─► if cache-hit != 'true' -> npm ci      │
 │       │                                                    │
 │       └── steps.ver.outputs.version                        │
 └────────────────────────┬───────────────────────────────────┘
          jobs.build.outputs.version = ${{ steps.ver.outputs.version }}
                          │
                          ▼
 job: deploy (needs: build) reads ${{ needs.build.outputs.version }}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| step id | Handle for a step | Step की पहचान |
| steps context | Info about previous steps | पिछले steps की जानकारी |
| outputs | Values a step exposes | Step के दिए values |
| outcome | Result before continue-on-error | continue-on-error से पहले का नतीजा |
| conclusion | Result after continue-on-error | continue-on-error के बाद का नतीजा |
| GITHUB_OUTPUT | File used to set outputs | Outputs लिखने की file |

---

## ⚡ 3-Line Summary
English: `id:` names a step so later steps can read `steps.<id>.outputs/outcome/conclusion`.
English: Write outputs to `$GITHUB_OUTPUT`; map to job outputs for other jobs.
English: Outputs are strings; ids must be unique per job.
Hindi: `id:` step को नाम देता है ताकि बाद के steps `steps.<id>.outputs/outcome/conclusion` पढ़ सकें।
Hindi: Outputs `$GITHUB_OUTPUT` में लिखें; दूसरे jobs के लिए job outputs में map करें।
Hindi: Outputs strings होते हैं; ids एक job में unique होने चाहिए।

---

## ➡️ Next Topic
**258. env: in Steps** - set environment variables at workflow, job and step levels, and understand their scope and precedence.
