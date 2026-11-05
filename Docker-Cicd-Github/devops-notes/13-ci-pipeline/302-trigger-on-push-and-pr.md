# 302. Trigger on Push + PR
# हिंदी में: Push और PR पर Workflow Trigger करना

---

## 🔵 Simple Definition (English)
The `on:` key tells GitHub **when** to start a workflow. For CI the two main events are `push` (someone pushed commits to a branch or tag) and `pull_request` (a PR was opened, updated, or reopened). You can narrow them with `branches`, `tags`, `paths`, and `types` filters.

## 🔵 सरल परिभाषा (Hindi)
`on:` key GitHub को बताती है कि workflow **कब** शुरू करना है। CI के लिए दो मुख्य events हैं: `push` (किसी ने branch या tag पर commits push किए) और `pull_request` (PR खुली, update हुई या दोबारा खुली)। इन्हें `branches`, `tags`, `paths` और `types` filters से सीमित किया जा सकता है।

---

## 🔴 Problem it Solves
A pipeline that runs on every event wastes minutes: pushing a README typo triggers a full build; every push to a PR branch runs twice (once as `push`, once as `pull_request`); docs-only PRs run 10 minutes of tests. A pipeline that runs too rarely lets broken code reach `main`.
Good triggers give fast feedback with no duplicate or wasted runs.

## 🔴 यह क्यों बना? (Hindi)
जो pipeline हर event पर चले वह minutes बर्बाद करती है: README की typo पर पूरा build; PR branch के हर push पर दो बार run (एक `push` से, एक `pull_request` से); docs-only PR पर 10 मिनट के tests। बहुत कम चले तो टूटा code `main` तक पहुँच जाता है।
सही triggers बिना duplicate या फ़ालतू runs के तेज़ feedback देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → An event occurs on GitHub (push, PR opened, PR new commit...)
Step 2 → GitHub scans workflow files on the relevant ref
         push: file from the pushed commit
         pull_request: file from the MERGE commit (PR into base)
Step 3 → For each workflow, match event name + filters
         (branches, tags, paths, types)
Step 4 → Filters AND together: branch must match AND paths must match
Step 5 → Matching workflows are queued and start on runners
Step 6 → github.event_name, github.ref, github.sha are set accordingly
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → GitHub पर event होता है (push, PR opened, PR में नया commit...)
Step 2 → GitHub संबंधित ref पर workflow files scan करता है
         push: pushed commit की file
         pull_request: MERGE commit (PR को base में) की file
Step 3 → हर workflow का event name + filters (branches, tags, paths, types) match होता है
Step 4 → Filters AND होते हैं: branch भी match हो और paths भी
Step 5 → Match हुए workflows queue में जाकर runners पर शुरू होते हैं
Step 6 → github.event_name, github.ref, github.sha उसी अनुसार set होते हैं
```

---

## 🟡 Real World Example
Your team uses `main` (production) and short-lived `feature/*` branches. You want: PRs to `main` get full CI; pushes to `main` run CI again plus deploy; pushes to `feature/*` without a PR run nothing (to avoid duplicates). Docs changes under `docs/**` or `*.md` skip CI. Tags like `v1.2.3` trigger a release workflow.

## 🟡 Real Example Hindi mein
आपकी team `main` (production) और छोटी उम्र की `feature/*` branches इस्तेमाल करती है। आप चाहते हैं: `main` की PRs पर पूरा CI; `main` पर push होने पर फिर से CI और deploy; PR के बिना `feature/*` पर push हो तो कुछ नहीं (duplicates से बचने के लिए)। `docs/**` या `*.md` बदलने पर CI skip। `v1.2.3` जैसे tags पर release workflow।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/ci.yml
name: CI                              # shown in the Actions tab

on:                                   # list of triggering events
  push:                               # event 1: a push
    branches:                         # only these branches
      - main
  pull_request:                       # event 2: PR activity
    branches:                         # PRs whose TARGET (base) is main
      - main

jobs:
  test:
    runs-on: ubuntu-latest            # runner
    steps:
      - uses: actions/checkout@v4     # get code
      - run: echo "event=${{ github.event_name }} ref=${{ github.ref }}"
                                      # print what triggered us
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/ci.yml  (careful triggers for a monorepo)
name: CI

on:
  push:
    branches:
      - main                          # exact branch
      - "release/**"                  # glob: release/1.0, release/2.x/hotfix
    tags:
      - "v*.*.*"                      # semver tags like v1.2.3
    paths-ignore:                     # skip if ONLY these changed
      - "**.md"
      - "docs/**"
      - ".github/ISSUE_TEMPLATE/**"
  pull_request:
    branches: [main, "release/**"]    # PR base branches
    types:                            # PR activity types (default are first three)
      - opened                        # PR created
      - synchronize                   # new commits pushed to PR
      - reopened                      # PR reopened
      - ready_for_review              # draft turned ready
    paths:                            # run only if these paths changed
      - "api/**"
      - "web/**"
      - "pricing/**"
      - ".github/workflows/ci.yml"    # changes to the workflow itself must be tested
  merge_group:                        # needed if you use GitHub merge queue
    types: [checks_requested]
  workflow_dispatch:                  # manual button
  schedule:
    - cron: "0 2 * * 1"               # weekly Monday 02:00 UTC safety run

concurrency:
  group: ci-${{ github.ref }}         # one run per ref
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
                                      # cancel old PR runs, never cancel main runs

permissions:
  contents: read                      # least privilege

jobs:
  test:
    # Skip draft PRs to save minutes
    if: github.event_name != 'pull_request' || github.event.pull_request.draft == false
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Testing ${{ github.sha }} for ${{ github.event_name }}"
```

---

## 🟠 My Stack Integration
- **Node.js / React:** trigger on `web/**` and `package*.json` changes only.
- **FastAPI:** trigger on `pricing/**` and `requirements*.txt`.
- **Nginx / VPS:** a separate workflow with `on.push.paths: ["deploy/nginx/**"]` that runs `nginx -t`.
- **AWS:** tag push `v*` starts a release workflow that builds the image and pushes to ECR.
- Avoid the duplicate-run trap: if you trigger `push` on all branches and `pull_request`, every PR commit runs twice. Limit `push` to `main`/`release/**`.

```yaml
# The "no duplicates" pattern for your repo
on:
  push:
    branches: [main]                  # post-merge verification only
  pull_request:                       # all PR checks (any target branch)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `on: [push, pull_request]` with no filters, so each PR commit runs twice.
✅ Correct: `push` only for `main`/release branches; PR commits use `pull_request`.

❌ Mistake 2: Mixing `paths` and `paths-ignore` for the same event (not allowed), or same for `branches`/`branches-ignore`.
✅ Correct: Use one style per event; use `!` negation patterns inside `paths` if you need both.

❌ Mistake 3: Using `paths:` on a workflow that is a **required** status check. If it is skipped by path filter, the check stays "Expected - waiting" and the PR can never merge.
✅ Correct: Run the workflow always and decide inside (path-filter job + `if`), or add a fallback job that reports success.

❌ Mistake 4: Writing `branches: [feature/*]` when you want nested names; `*` does not match `/`.
✅ Correct: Use `feature/**` to match `feature/login/ui`.

❌ Mistake 5: Using `pull_request_target` to get secrets for forks and then checking out the PR code. This lets attackers run code with your secrets.
✅ Correct: Use plain `pull_request` for untrusted code; use `pull_request_target` only for metadata tasks (labels, comments) without running PR code.

---

## 🧠 Tricky Interview Question
**Q:** You changed only `README.md` in a PR. The workflow has `paths-ignore: ['**.md']`, and branch protection requires the `test` check. What happens?

**Answer:** The workflow does not run, so the required check `test` is never reported. GitHub shows "Expected - Waiting for status to be reported", and the PR is blocked. (Skipped by `paths` is different from a skipped job, which does report success.) Solutions: remove the path filters from the workflow and use a `changes` job with `if`, or add a lightweight companion workflow with the same job name that reports success when only docs changed.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `push` and `pull_request`?
A1: `push` runs on the pushed commit in the repo. `pull_request` runs on a temporary merge of the PR head into the base, with a read-only token and no secrets for forks. Use `pull_request` to validate proposals; `push` to `main` to verify after merge and to deploy.

Q2: Default activity types for `pull_request`?
A2: `opened`, `synchronize`, `reopened`. Others like `ready_for_review`, `labeled`, `closed` must be listed explicitly.

Q3: How do you run a workflow on tags only?
A3: `on: push: tags: ['v*.*.*']` and no branches filter. Note that if you specify both `branches` and `tags`, either match triggers it.

Q4: How can you restrict a push workflow to certain files?
A4: `paths:` (allow list) or `paths-ignore:` (deny list); for combos use `!` patterns in `paths`. For tags, path filters are ignored.

Q5: How do you test a workflow change without merging?
A5: Use `workflow_dispatch` on the branch, or open a PR; for `pull_request` GitHub uses the workflow file from the PR merge commit, so edits to the workflow apply to the PR itself. For `push`, it uses the file on the pushed branch.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `pull_request` for every CI quality gate
- `push` on `main` for post-merge verification and deploy
- `tags` for releases; `schedule` for nightly deep scans

❌ Avoid when:
- `push` to all branches together with `pull_request` (double runs)
- `paths:` filters on required checks without a fallback
- `pull_request_target` with untrusted checkout

---

## 📊 Visual Diagram
```
 feature/login (no PR)  -- push --> no workflow (filtered out)
        |
        | open PR to main
        v
 pull_request: opened ------------+
 pull_request: synchronize (new commits) --> CI runs (cancel older)
        |
        | merge
        v
 push to main ---------------------> CI runs again (+ deploy job)
        |
        | git tag v1.4.0 && git push --tags
        v
 push tag v*.*.* -----------------> release workflow
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `on:` | Declares triggering events | कौन से events trigger करें |
| `branches` | Branch name filter (glob) | branch filter |
| `paths` | File path filter | file path filter |
| `types` | Activity types for an event | event के प्रकार |
| `synchronize` | New commits pushed to PR | PR में नए commits |
| `workflow_dispatch` | Manual trigger | manual trigger |
| `merge_group` | Merge queue event | merge queue event |
| `cron` | Scheduled trigger (UTC) | समय-निर्धारित trigger |

---

## ⚡ 3-Line Summary
English: `on:` decides when CI runs; use `pull_request` for checks and `push` to `main` for post-merge runs.
Filters (`branches`, `paths`, `types`) cut waste, but path filters can block required checks.
Avoid duplicate runs and never combine `pull_request_target` with checkout of untrusted code.
Hindi: `on:` तय करता है कि CI कब चले; checks के लिए `pull_request` और merge के बाद के लिए `main` पर `push` इस्तेमाल करें।
Filters (`branches`, `paths`, `types`) फ़ालतू runs घटाते हैं, पर path filters required checks को अटका सकते हैं।
Duplicate runs से बचें और `pull_request_target` को untrusted code के checkout के साथ कभी न जोड़ें।

---

## ➡️ Next Topic
**303. Checkout Code (actions/checkout)** — the first step of nearly every job: getting your repository onto the runner.
