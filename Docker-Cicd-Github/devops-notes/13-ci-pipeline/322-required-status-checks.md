# 322. Required Status Checks
# हिंदी में: Required Status Checks (अनिवार्य checks)

---

## 🔵 Simple Definition (English)
Required status checks are checks that must pass before a pull request can be merged into a protected branch. You configure them in branch protection rules or repository rulesets. Without them, a red check is only a warning; with them, GitHub disables the merge button.

## 🔵 सरल परिभाषा (Hindi)
Required status checks वे checks हैं जो protected branch में pull request merge होने से पहले pass होने ज़रूरी हैं। आप इन्हें branch protection rules या repository rulesets में configure करते हैं। इनके बिना लाल check सिर्फ़ चेतावनी है; इनके साथ GitHub merge button बंद कर देता है।

---

## 🔴 Problem it Solves
CI that can be ignored will be ignored. Under deadline pressure someone merges a red PR, main breaks, and the auto-deploy ships it to your VPS. Required checks (plus required reviews) make the rule a technical guarantee rather than team etiquette.

## 🔴 यह क्यों बना? (Hindi)
जिस CI को अनदेखा किया जा सकता है, उसे अनदेखा किया जाएगा। Deadline के दबाव में कोई लाल PR merge कर देता है, main टूट जाती है और auto-deploy उसे आपके VPS पर भेज देता है। Required checks (और required reviews) नियम को शिष्टाचार की जगह तकनीकी गारंटी बनाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Run the workflows at least once so check names exist in GitHub
Step 2 → Settings → Branches (rule) or Settings → Rules → Rulesets
Step 3 → Target: main (or ~DEFAULT_BRANCH)
Step 4 → Enable "Require status checks to pass before merging"
Step 5 → Pick exact check names (e.g. "CI OK", "Analyze (python)")
Step 6 → Enable "Require branches to be up to date" (strict) if wanted
Step 7 → Add "Require a pull request before merging" + approvals
Step 8 → PR merge button stays disabled until all required checks are green
Step 9 → Admins can bypass unless "include administrators" / no bypass actors
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Workflows कम से कम एक बार चलाएँ ताकि check names GitHub में दिखें
Step 2 → Settings → Branches (rule) या Settings → Rules → Rulesets
Step 3 → Target: main (या ~DEFAULT_BRANCH)
Step 4 → "Require status checks to pass before merging" चालू करें
Step 5 → सटीक check names चुनें (जैसे "CI OK", "Analyze (python)")
Step 6 → चाहें तो "Require branches to be up to date" (strict) चालू करें
Step 7 → "Require a pull request before merging" + approvals जोड़ें
Step 8 → सभी required checks हरे होने तक PR का merge button बंद रहता है
Step 9 → Admins bypass कर सकते हैं जब तक "include administrators" / कोई bypass actor न हो
```

---

## 🟡 Real World Example
Friday evening, a developer force-merges a "tiny fix". With no protection, a typo breaks login and the pipeline deploys it to the VPS. After this incident the team requires `CI OK`, `CodeQL`, `trivy` and one approval on `main`. The next risky PR sits red until fixed, and production stays healthy over the weekend.

## 🟡 Real Example Hindi mein
शुक्रवार शाम, एक developer "छोटा fix" जबरदस्ती merge कर देता है। Protection के बिना एक typo login तोड़ देती है और pipeline उसे VPS पर deploy कर देती है। इस घटना के बाद टीम `main` पर `CI OK`, `CodeQL`, `trivy` और एक approval required करती है। अगला जोखिम भरा PR ठीक होने तक लाल पड़ा रहता है, और weekend में production स्वस्थ रहता है।

---

## 💻 Code / Config Example — Basic
```bash
#!/usr/bin/env bash
# protect-main.sh : classic branch protection via GitHub CLI (needs admin rights on the repo)
set -euo pipefail                      # Stop on any error
REPO="${1:?usage: protect-main.sh owner/repo}"     # First argument is required
# PUT replaces the whole protection config for the branch with this JSON body
gh api -X PUT "repos/${REPO}/branches/main/protection" --input - <<'JSON'
{
  "required_status_checks": { "strict": true, "contexts": ["CI OK"] },
  "enforce_admins": true,
  "required_pull_request_reviews": { "required_approving_review_count": 1 },
  "restrictions": null
}
JSON
echo "Protection applied to ${REPO}:main"
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# ruleset-main.sh : modern repository ruleset (recommended over classic rules)
set -euo pipefail
REPO="${1:?usage: ruleset-main.sh owner/repo}"
# Create a ruleset that targets the default branch and enforces checks + reviews
gh api -X POST "repos/${REPO}/rulesets" --input - <<'JSON'
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] }
  },
  "bypass_actors": [],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": true,
        "required_review_thread_resolution": true
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          { "context": "CI OK" },
          { "context": "Analyze (python)" },
          { "context": "Analyze (javascript-typescript)" },
          { "context": "scan" }
        ]
      }
    }
  ]
}
JSON
echo "Ruleset created for ${REPO}"
```

The workflow side that supplies the stable `CI OK` check (see topic 321 for the full file):
```yaml
# .github/workflows/ci.yml (essential part)
name: CI
on:
  pull_request:                        # Required checks must run on PRs, with no paths filter
jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "run tests here"     # Replace with real steps
  ci-ok:
    name: CI OK                        # This exact name goes into the ruleset
    if: always()                       # Report even when upstream jobs fail
    needs: [tests]
    runs-on: ubuntu-latest
    steps:
      - run: |
          if [ "${{ needs.tests.result }}" != "success" ]; then
            echo "tests did not succeed"
            exit 1
          fi
```

---

## 🟠 My Stack Integration
- **Node.js + FastAPI + React in one repo:** Require only the aggregate `CI OK`, `CodeQL` analysis jobs and the image scan; individual matrix names can change freely.
- **Deploy to VPS/AWS:** Make `main` the deploy branch; because merges require green checks, the deploy workflow on `push: main` only ever ships verified code. Protect the `production` environment with required reviewers too.
- **Bots:** Dependabot PRs must pass the same checks; allow auto-merge only after checks pass (`gh pr merge --auto --squash`).
- **Security:** Enable "dismiss stale approvals on new commits" and "require last push approval" so a reviewer's approval cannot be reused after malicious changes. Restrict who can bypass; log bypasses.
- **Secrets:** Required checks that need secrets will fail on fork PRs; design them to skip safely and still report success where appropriate.

```bash
# Inspect the current protection and the exact context names GitHub knows
gh api repos/OWNER/REPO/branches/main/protection/required_status_checks   # Shows strict + contexts
gh pr checks 57                                                          # Check names on a real PR
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Typing the check name incorrectly, so it waits forever ("Expected").
✅ Correct: Copy the name from a real PR's checks list or the API.

❌ Mistake 2: Requiring checks from a workflow with `paths:` or `branches:` filters.
✅ Correct: Make the workflow run on every PR, or use an aggregate job.

❌ Mistake 3: Leaving admins able to bypass without a record.
✅ Correct: Enforce for admins; if bypass is needed, restrict to named actors.

❌ Mistake 4: Requiring flaky checks.
✅ Correct: Fix or remove the flake first; otherwise people learn to ignore red.

❌ Mistake 5: Only protecting `main` while deploys run from `release/*` branches.
✅ Correct: Apply rules to every branch that can deploy (pattern rules).

---

## 🧠 Tricky Interview Question
You require the check `test`, and a developer adds a matrix to that job. After merging that workflow change, every PR is stuck at "Expected - Waiting for status to be reported". Why?

Answer: Adding a matrix changes the check names from `test` to `test (node 18)`, `test (node 20)`, so no check called `test` is ever reported anymore, and the rule waits for it. The workflow change itself could be merged only because it was tested in a different state. Fix: update the required list to the new names, or better, require a single aggregate job (`CI OK`) that does not change when the matrix changes, and set the `name:` of matrix jobs explicitly.

---

## ⚫ Interview Questions + Answers

Q1: Branch protection rules vs rulesets?
A1: Rulesets are newer: multiple rulesets layer together, can target many branches/tags by pattern, have bypass lists, evaluate mode ("evaluate" to test), and are viewable by all collaborators. Classic rules are one-per-pattern and simpler.

Q2: What does "Require branches to be up to date" (strict) do?
A2: The PR branch must contain the latest base commit, so checks ran against the merged result. It is safer but forces rebases or "update branch" clicks; merge queue automates it.

Q3: What is a merge queue?
A3: A GitHub feature that tests PRs in order against the latest main combined with queued changes, merging automatically when green. Workflows must also trigger on `merge_group`.

Q4: Who can bypass?
A4: Repo admins unless "do not allow bypassing" / enforce for admins is set; in rulesets only listed bypass actors.

Q5: Why only pick checks that run on every PR?
A5: Anything conditional may not report, leaving the required check pending forever.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Anything deploys automatically from main.
- More than one person commits.
- Compliance needs enforced review and testing.

❌ Avoid when:
- Solo throwaway repo where friction beats value (still protect deploy branches).
- Checks are unreliable or take too long.
- You lack a break-glass process for emergency fixes; define one (bypass actor with audit).

---

## 📊 Visual Diagram
```
 Developer PR ──▶ CI jobs ──▶ ✅/❌ checks reported to commit
                                     │
        Ruleset on main:  required = [CI OK, Analyze (...), scan]
                                     │
                      all required ✅ ? ── no ──▶ 🚫 Merge disabled
                                     │ yes
                      approvals ≥ 1 ? ── no ──▶ 🚫 Merge disabled
                                     │ yes
                                     ▼
                              ✅ Merge allowed
                                     │
                     push to main ──▶ deploy workflow ──▶ VPS / AWS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Branch protection | Rules guarding a branch | branch की सुरक्षा के नियम |
| Ruleset | Newer layered rules system | नई परतदार नियम प्रणाली |
| Strict policy | Branch must be up to date | branch का अद्यतन होना ज़रूरी |
| Bypass actor | Role/user allowed to skip rules | नियम छोड़ने की अनुमति वाला user/role |
| Merge queue | Ordered auto-testing before merge | merge से पहले क्रम से auto-testing |
| Context | The exact name of a check | check का सटीक नाम |

---

## ⚡ 3-Line Summary
English: Required status checks block merges until chosen checks pass.
English: Configure with branch protection or rulesets, using stable names such as an aggregate `CI OK`.
English: Avoid path-filter and rename traps, restrict bypass, and combine with required reviews.
Hindi: Required status checks चुने हुए checks pass होने तक merge रोकते हैं।
Hindi: Branch protection या rulesets से configure करें, `CI OK` जैसे स्थिर aggregate नाम इस्तेमाल करें।
Hindi: Path-filter और rename के जाल से बचें, bypass सीमित रखें और required reviews साथ जोड़ें।

Note: the gh/JSON payloads were JSON-validated and bash syntax-checked but NOT sent to GitHub; field names follow the REST API docs and may change, so check the current API reference. Needs repo admin rights.

---

## ➡️ Next Topic
323. Fail Fast Strategy: stop wasting minutes by cancelling or skipping work as soon as a failure is certain.
