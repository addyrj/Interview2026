# 256. name: Field
# हिंदी में: name: Field (नाम देना)

---

## 🔵 Simple Definition (English)
`name:` is an optional label you can put on a **workflow**, a **job**, a **step**, and on matrix/environment contexts. It controls what humans see in the Actions tab, PR status checks, and logs. Without it GitHub falls back to the file path (workflow), the job id (job), or the `uses`/`run` text (step). A related key `run-name:` customizes the title of each workflow run.

## 🔵 सरल परिभाषा (Hindi)
`name:` एक वैकल्पिक label है जो **workflow**, **job** और **step** को दिया जा सकता है। यह तय करता है कि Actions tab, PR status checks और logs में इंसानों को क्या दिखेगा। न दें तो GitHub workflow के लिए file path, job के लिए job id, और step के लिए `uses`/`run` text दिखाता है। संबंधित key `run-name:` हर workflow run का title बदलता है।

---

## 🔴 Problem it Solves
Open a failing run with 14 steps showing `Run actions/checkout@v4`, `Run npm ci`, `Run ./scripts/x.sh`, and 3 jobs called `build`, `build`, `build (1)`. At 2 a.m. the on-call engineer cannot tell what failed. Clear names make logs scannable, required status checks understandable, and run lists searchable ("Deploy production v1.4.0 by Aditya"). A poor name also breaks branch protection: required checks are matched **by name**, so renaming a job silently un-requires the old check.

## 🔴 यह क्यों बना? (Hindi)
सोचिए 14 steps वाला failing run जिसमें `Run actions/checkout@v4`, `Run npm ci`, `Run ./scripts/x.sh` दिखें और 3 jobs के नाम `build`, `build`, `build (1)` हों। रात 2 बजे on-call engineer समझ नहीं पाएगा कि क्या फेल हुआ। साफ़ नाम logs को पढ़ने योग्य, required status checks को समझने योग्य और run list को खोजने योग्य ("Deploy production v1.4.0 by Aditya") बनाते हैं। खराब नाम branch protection भी तोड़ सकता है: required checks **नाम से** match होते हैं, इसलिए job का नाम बदलने पर पुराना check चुपचाप required नहीं रहता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Workflow-level `name:` appears in the left list of the Actions tab and in the badge URL.
Step 2 → Job-level `name:` appears as the check name: "<workflow name> / <job name>" on PRs.
Step 3 → Matrix jobs get auto-suffixes: "test (ubuntu-24.04, 20)"; custom `name:` can interpolate matrix values.
Step 4 → Step-level `name:` replaces the default "Run <command>" heading in the log.
Step 5 → `run-name:` (workflow-level) sets the title of each run using github/inputs contexts.
Step 6 → Names accept expressions ${{ }} (github, inputs, matrix, vars contexts; NOT secrets).
Step 7 → Branch protection stores the check name string - keep job names stable once required.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Workflow-level `name:` Actions tab की बाईं सूची और badge URL में दिखता है।
Step 2 → Job-level `name:` PR पर check का नाम बनता है: "<workflow name> / <job name>"।
Step 3 → Matrix jobs को अपने-आप suffix मिलता है: "test (ubuntu-24.04, 20)"; custom `name:` में matrix values जोड़ सकते हैं।
Step 4 → Step-level `name:` log में default "Run <command>" heading की जगह लेता है।
Step 5 → `run-name:` (workflow-level) github/inputs contexts से हर run का title तय करता है।
Step 6 → Names में expressions ${{ }} चलते हैं (github, inputs, matrix, vars contexts; secrets नहीं)।
Step 7 → Branch protection check का नाम string के रूप में रखती है - required होने के बाद job names स्थिर रखें।
```

---

## 🟡 Real World Example
A company with one deploy workflow for staging and production uses `run-name: Deploy ${{ inputs.environment }} ${{ inputs.image_tag }} by ${{ github.actor }}`. The Actions list reads "Deploy production v1.4.0 by priya", so the audit trail needs no click-through. Their PR checks are named `CI / Lint`, `CI / Unit tests (Node 20)`, `CI / Docker build` - and branch protection requires exactly those three, so renames go through a reviewed PR that also updates the rule.

## 🟡 Real Example Hindi mein
एक कंपनी staging और production के लिए एक ही deploy workflow रखती है और `run-name: Deploy ${{ inputs.environment }} ${{ inputs.image_tag }} by ${{ github.actor }}` लगाती है। Actions list में "Deploy production v1.4.0 by priya" दिखता है, इसलिए audit trail के लिए अंदर जाना नहीं पड़ता। उनके PR checks के नाम `CI / Lint`, `CI / Unit tests (Node 20)`, `CI / Docker build` हैं - और branch protection ठीक यही तीन माँगती है, इसलिए नाम बदलना एक reviewed PR से होता है जो rule भी update करता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/name-basic.yml
name: CI                                  # WORKFLOW name: shown in the Actions tab

on: [push]                                # trigger

jobs:
  test:                                   # job ID (used in needs:, never changes the displayed name)
    name: Unit tests                      # JOB name: shown on PR checks as "CI / Unit tests"
    runs-on: ubuntu-latest                # runner
    steps:
      - name: Checkout code               # STEP name: replaces "Run actions/checkout@v4"
        uses: actions/checkout@v4         # action
      - name: Install dependencies        # STEP name
        run: npm ci                       # command
      - name: Run unit tests              # STEP name
        run: npm test                     # command
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/name-advanced.yml
name: CI                                  # stable workflow name (part of required check names)

run-name: >-                              # title of EACH run in the Actions list
  CI for ${{ github.event_name }} on ${{ github.ref_name }} by ${{ github.actor }}

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Unit tests (Node ${{ matrix.node }})   # matrix value in job name => unique, readable checks
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node: [20, 22]                    # produces two jobs with distinct names
    steps:
      - name: Checkout                    # short, verb-first step names
        uses: actions/checkout@v4

      - name: Set up Node ${{ matrix.node }}      # expressions allowed in step names
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: npm

      - name: Install dependencies (clean)
        run: npm ci

      - name: Test with coverage
        run: npm test -- --coverage

      - name: Print summary on failure
        if: failure()                     # name explains the condition
        run: echo "Tests failed on Node ${{ matrix.node }}"

  required-gate:
    name: CI passed                       # ONE stable aggregate check to make "required" in branch protection
    if: always()                          # always report, even when needed jobs fail or are skipped
    needs: [test]                         # waits for matrix jobs
    runs-on: ubuntu-latest
    steps:
      - name: Fail if any test job failed
        run: |
          # needs.test.result is success | failure | cancelled | skipped for the whole matrix
          [ "${{ needs.test.result }}" = "success" ]   # non-zero exit if not success
```

(YAML parsed locally; GitHub UI naming behavior documented but not visually verified here.)

---

## 🟠 My Stack Integration
- **Node.js / FastAPI / React:** names like `API / Lint`, `API / Tests`, `Web / Build`, `Docker / Build image`.
- **Nginx / VPS:** step names such as `Validate nginx.conf`, `Reload nginx`, `Smoke test /health`, so deploy failures say exactly what broke.
- **AWS:** `Assume role (OIDC)`, `Login to ECR`, `Update ECS service`.
- **Branch protection:** require the stable aggregate job (`CI passed`) rather than every matrix leg, so adding Node 24 later does not break the rule.

```yaml
# Pattern: rename-proof required check -> require only "CI passed"; matrix names can change freely.
# GitHub UI path: Settings -> Branches (or Rulesets) -> Require status checks -> add "CI passed".
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Renaming a job that is a required check - PRs show "Expected - waiting for status" forever.
✅ Correct: Update branch protection in the same change, or require a stable aggregate job.

❌ Mistake 2: Two jobs with the same `name:` (e.g. both "build") - indistinguishable checks.
✅ Correct: Unique, descriptive names; include matrix values.

❌ Mistake 3: Putting secrets or tokens in names (names are visible in UI and logs).
✅ Correct: Names should contain non-sensitive info only; `secrets` context is not available there anyway.

❌ Mistake 4: Confusing job `id` with `name` - `needs: [Unit tests]` fails.
✅ Correct: `needs` uses the job ID (the YAML key), not the display name.

❌ Mistake 5: Very long names that get truncated.
✅ Correct: Keep under about 40 characters; verb-first for steps.

---

## 🧠 Tricky Interview Question
Branch protection requires the check `build`. You rename the job's `name:` from `build` to `Build image`. PRs can no longer be merged, though all checks are green. Why?

Answer: Required status checks are matched by their exact name string. The new check is called `Build image`, but the rule still waits for a check named `build` that nothing reports anymore. Fix by editing the rule to the new name (or by using one stable aggregate job). Also note the displayed check name is the job `name` when given, otherwise the job id; the workflow name is shown as a prefix in UI but the context stored in the rule is the job name.

---

## ⚫ Interview Questions + Answers

Q1: Is `name:` required?
A1: No. Defaults: workflow = file path relative to repo root; job = job id; step = `Run <command>` or the action reference.

Q2: What does `run-name:` do?
A2: Sets the display name of each run, supports `github` and `inputs` contexts.

Q3: Can names contain expressions?
A3: Yes for workflow `run-name`, job `name` (with matrix/github/inputs/vars) and step `name`.

Q4: Job id vs job name?
A4: ID is the YAML key, used in `needs`, outputs and expressions. Name is only the label.

Q5: How do you show a badge for a workflow?
A5: `https://github.com/OWNER/REPO/actions/workflows/<file>.yml/badge.svg` in the README.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Always, on workflows, jobs and non-obvious steps.
- Using matrices (include values), reusable workflows, and required checks.

❌ Avoid when:
- Never skip entirely, but avoid frequent renames of required-check jobs.
- Do not stuff data into names; use job summaries for details.

---

## 📊 Visual Diagram

```
 workflow name: CI
 ├── job id: test      name: "Unit tests (Node ${{matrix.node}})"
 │     ├── step name: "Checkout"
 │     ├── step name: "Set up Node 20"
 │     └── step name: "Test with coverage"
 └── job id: required-gate   name: "CI passed"
         ▲
         │  branch protection requires the string:  "CI passed"
 PR checks list:  CI / Unit tests (Node 20)  ✔
                  CI / Unit tests (Node 22)  ✔
                  CI / CI passed             ✔  <- required
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| name | Display label | दिखने वाला नाम |
| run-name | Title of one run | एक run का शीर्षक |
| job id | YAML key used in needs | `needs` में काम आने वाली key |
| status check | Reported pass/fail context | रिपोर्ट किया pass/fail |
| aggregate job | One job summarizing others | बाकी का सार देने वाला job |
| badge | Status image for README | README का status चित्र |

---

## ⚡ 3-Line Summary
English: `name:` labels workflows, jobs and steps for humans; `run-name:` titles each run.
English: Required checks match job names exactly, so keep them stable or use an aggregate job.
English: Use clear verb-first step names and matrix values in job names.
Hindi: `name:` workflows, jobs और steps को इंसानों के लिए label करता है; `run-name:` हर run का शीर्षक देता है।
Hindi: Required checks job names से ठीक-ठीक match होते हैं, इसलिए उन्हें स्थिर रखें या aggregate job लें।
Hindi: साफ़ क्रिया-पहले step names और job names में matrix values रखें।

---

## ➡️ Next Topic
**257. id: Field** - give steps (and jobs) an identifier so later steps can read their outputs and status.
