---

# 33. Branch Protection Rules
# हिंदी में: Branch Protection Rules (branch की सुरक्षा के नियम)

---

## 🔵 Simple Definition (English)
**Branch protection rules** are GitHub settings that restrict what can happen to important branches (like `main`): require pull requests, approvals, passing CI checks, signed commits, and block force-pushes and deletion. **Rulesets** are the newer, more flexible version of the same idea.

## 🔵 सरल परिभाषा (Hindi)
**Branch protection rules** GitHub की settings हैं जो ज़रूरी branches (जैसे `main`) पर पाबंदी लगाती हैं: Pull Request अनिवार्य, approvals, CI checks पास होना, signed commits, और force-push व delete पर रोक। **Rulesets** इसी विचार का नया, ज़्यादा लचीला रूप हैं।

---

## 🔴 Problem it Solves
If `main` auto-deploys to production, one direct push of broken code takes the site down. Without protection, anyone with write access can push untested code, rewrite history with `--force`, or delete the branch. Rules enforce the process in the platform itself, not by trust or memory.

## 🔴 यह क्यों बना? (Hindi)
अगर `main` से सीधे production deploy होता है, तो एक बार का सीधा push टूटे code से site गिरा सकता है। Protection के बिना write access वाला कोई भी बिना test का code push कर सकता है, `--force` से history बदल सकता है या branch delete कर सकता है। Rules process को platform में ही लागू करते हैं, भरोसे या याददाश्त पर नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Settings → Branches → Add branch protection rule (or Rules → Rulesets → New branch ruleset)
Step 2 → Target pattern: main  (or release/*)
Step 3 → Enable: Require a pull request before merging (1-2 approvals, dismiss stale approvals)
Step 4 → Enable: Require status checks to pass (pick CI job names) + "up to date" branch
Step 5 → Enable: Require conversation resolution, linear history, signed commits (optional)
Step 6 → Enable: Block force pushes and deletions; Do not allow bypassing (include administrators)
Step 7 → Developer opens PR -> CI runs -> reviewer approves -> Merge button turns green
Step 8 → Direct `git push origin main` is rejected: "protected branch hook declined"
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Settings → Branches → Add branch protection rule (या Rules → Rulesets)
Step 2 → Target pattern: main (या release/*)
Step 3 → चालू करो: Require a pull request (1-2 approvals, पुराने approvals dismiss)
Step 4 → चालू करो: Require status checks (CI job names चुनो) + branch "up to date"
Step 5 → चालू करो: conversation resolution, linear history, signed commits (वैकल्पिक)
Step 6 → चालू करो: force push और delete पर रोक; administrators को भी bypass न दो
Step 7 → Developer PR खोलता है -> CI चलता है -> reviewer approve करता है -> Merge button हरा होता है
Step 8 → सीधा git push origin main reject होता है: "protected branch hook declined"
```

---

## 🟡 Real World Example
An e-commerce team auto-deploys `main` to an AWS EC2 box via GitHub Actions. Rules on `main`: 1 approval from CODEOWNERS, required checks `test` and `build`, linear history, no force pushes. A developer tries `git push origin main` at 11 PM before a flight; GitHub rejects it. He opens a PR, CI fails on a broken test, and the bug never reaches the server. The rule saved a Friday-night outage.

## 🟡 Real Example Hindi mein
एक e-commerce team `main` को GitHub Actions से AWS EC2 पर auto-deploy करती है। `main` पर rules: CODEOWNERS से 1 approval, required checks `test` और `build`, linear history, force push नहीं। एक developer फ़्लाइट से पहले रात 11 बजे `git push origin main` करता है; GitHub reject कर देता है। वह PR खोलता है, CI में टूटा test fail होता है और bug server तक पहुँचता ही नहीं। इस rule ने शुक्रवार रात का outage बचा लिया।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# protect-main-basic.sh - classic branch protection through the REST API (gh api)
# Endpoint: PUT /repos/{owner}/{repo}/branches/{branch}/protection  (needs admin)
set -euo pipefail                                   # strict mode
REPO="${1:?usage: $0 owner/repo}"                   # owner/repo argument

gh api -X PUT "repos/$REPO/branches/main/protection" --input - <<'JSON'
{
  "required_status_checks": { "strict": true, "contexts": ["test"] },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
echo "main is protected: PR + 1 approval + check 'test' required"   # confirmation
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# ruleset-main.sh - modern Repository Ruleset (JSON) created via API
# Endpoint: POST /repos/{owner}/{repo}/rulesets  (rule type names are from GitHub's docs)
set -euo pipefail                                   # strict mode
REPO="${1:?usage: $0 owner/repo}"                   # owner/repo

gh api -X POST "repos/$REPO/rulesets" --input - <<'JSON'
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["refs/heads/main"], "exclude": [] } },
  "bypass_actors": [],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_linear_history" },
    { "type": "required_signatures" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": true,
        "required_review_thread_resolution": true
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [ { "context": "gate" } ]
      }
    }
  ]
}
JSON
echo "Ruleset 'protect-main' created (active)"      # done
```
Not run against GitHub here (no account). Private repos need a paid plan for some protection features. Classic rules and rulesets can both apply; the strictest wins.

---

## 🟠 My Stack Integration
The required check name must match a job that ALWAYS runs. Your Node/FastAPI/React CI should end with one job named `gate` or `test`. Deployment to the VPS/AWS happens only on push to `main` (i.e., after a PR merged), so protection = gate to production.

```yaml
# .github/workflows/ci.yml - produces the required status check "test"
name: CI                                   # workflow name
on:
  pull_request:                            # run for PRs (required before merge)
    branches: [main]                       # PRs into main
jobs:
  test:                                    # job id = the check name you require in branch protection
    runs-on: ubuntu-latest                 # hosted runner
    steps:
      - uses: actions/checkout@v4          # example version
      - uses: actions/setup-node@v4        # Node.js
        with:
          node-version: 20                 # example LTS
          cache: npm                       # cache npm
      - run: npm ci                        # install
      - run: npm test                      # tests must pass to unlock Merge
```
Security: turn on "Do not allow bypassing" so admins cannot skip it (compromised admin token is a real attack path); require signed commits for high-risk repos; require review from CODEOWNERS (topic 34) on `.github/workflows/**` because workflows can access secrets.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Requiring a status check by a name no job produces (typo), so PRs are stuck.
✅ Correct: Run the workflow once, then pick the exact check name from the dropdown.

❌ Mistake 2: "Include administrators" left off, so owners push directly "just this once".
✅ Correct: Enforce for admins; use a temporary ruleset bypass actor with audit if truly needed.

❌ Mistake 3: Only protecting `main` while `release/*` or `production` branch deploys.
✅ Correct: Protect every deploy branch with a pattern such as `release/*`.

❌ Mistake 4: Not enabling "dismiss stale approvals", so someone approves, then pushes malicious changes.
✅ Correct: Enable dismiss stale reviews and "require approval of the most recent push".

---

## 🧠 Tricky Interview Question
Branch protection is on and requires the check `build`. A PR from a fork shows "Expected — Waiting for status to be reported" forever. What might be wrong?

Answer: Possible causes: (1) first-time-contributor fork PRs need maintainer approval to run workflows; (2) the workflow is path-filtered or has an `if:` that skipped it so it never reported; (3) the job name changed (renamed `build` to `build-app`) so the required context is never reported; (4) the workflow uses `pull_request` and is disabled for forks. Fix: approve the run, remove workflow-level path filters for required checks, and update required check names.

---

## ⚫ Interview Questions + Answers

Q1: Difference between branch protection rules and rulesets?
A1: Classic rules are per-branch pattern settings. Rulesets are newer: multiple can stack, apply to branches/tags/pushes, support bypass lists, org-wide scope, and have "evaluate" (dry-run) mode.

Q2: What does "Require branches to be up to date" do?
A2: The PR branch must contain the latest base commits before merging, ensuring CI tested the actual merge result (can be handled by a merge queue).

Q3: Can you stop force-push but allow your CI bot to push?
A3: Yes, via bypass actors/allowed actors for that GitHub App or by pushing through a PR with auto-merge.

Q4: What is a merge queue?
A4: A feature that serializes merges: it tests each PR on top of the queue head, avoiding semantic conflicts and "up to date" re-runs.

Q5: How to protect tags?
A5: Use tag rulesets (e.g. `v*`) to block deletion/updates so released versions are immutable.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any branch that deploys or is the source of truth (main, release/*)
- Team of 2+ or any compliance requirement

❌ Avoid (or relax) when:
- Personal throwaway repo or prototype where PR overhead has no value
- Never relax on production-deploy branches

---

## 📊 Visual Diagram
```
 feature/x --PR--> [ main ]  PROTECTED
                      ^
   +------------------+-------------------+
   | 1. CI checks pass (test/gate)        |
   | 2. >=1 approval (CODEOWNERS)         |
   | 3. conversations resolved            |
   | 4. branch up to date / merge queue   |
   +------------------+-------------------+
                      v
                 Merge allowed --> Actions deploy to VPS/AWS
 git push origin main (direct)  --> X REJECTED
 git push --force / delete main --> X REJECTED
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Protected branch | Branch with restrictions | सुरक्षित branch |
| Required status check | CI job that must pass | अनिवार्य CI check |
| Ruleset | Newer flexible rule system | नया rules सिस्टम |
| Stale review | Approval made before new commits | पुराना approval |
| Merge queue | Serialized tested merging | क्रमवार merge queue |
| Bypass actor | User/app allowed to skip rules | नियम से छूट वाला |

---

## ⚡ 3-Line Summary
English: Branch protection forces PRs, reviews and passing CI before code reaches main.
It also blocks force-push and deletion and should apply to admins too.
Make one always-running required check so PRs never get stuck.
Hindi: Branch protection main तक code पहुँचने से पहले PR, review और CI पास होना अनिवार्य करता है।
यह force-push और delete भी रोकता है और admins पर भी लागू होना चाहिए।
एक हमेशा चलने वाला required check रखो ताकि PRs न अटकें।

---

## ➡️ Next Topic
**34. CODEOWNERS File**: decide WHO must review which files, so protection rules can demand the right reviewer.

---
