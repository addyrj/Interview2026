# 17. Git Branching Strategy
# हिंदी में: Git Branching Strategy (Branch चलाने की रणनीति)

---

## 🔵 Simple Definition (English)
A **branching strategy** is the team's agreed rule-set for which branches exist, what each is for, how code moves between them, and which branch gets deployed. Common strategies are Git Flow, GitHub Flow and Trunk-Based Development.

## 🔵 सरल परिभाषा (Hindi)
**Branching strategy** team का तय किया हुआ नियम-सेट है: कौन-सी branches होंगी, हर एक किसलिए है, code एक से दूसरी में कैसे जाएगा, और कौन-सी branch deploy होगी। आम strategies हैं Git Flow, GitHub Flow और Trunk-Based Development।

---

## 🔴 Problem it Solves
Without a strategy, five developers push directly to `main`, overwrite each other, ship half-finished features and nobody knows which commit is in production. Hotfixes collide with feature work, and merges become huge, painful "merge hell" events. A strategy gives predictable releases, safe isolation of work-in-progress and clear mapping from branch to environment.

## 🔴 यह क्यों बना? (Hindi)
Strategy के बिना पाँच developers सीधे `main` पर push करते हैं, एक-दूसरे का काम overwrite करते हैं, अधूरे features ship हो जाते हैं और किसी को नहीं पता prod में कौन-सा commit है। Hotfix और feature काम टकराते हैं, merges बड़े और दर्दनाक "merge hell" बन जाते हैं। Strategy predictable releases, अधूरे काम का safe isolation और branch से environment का साफ mapping देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick the model that fits your release style (see table below).
Step 2 → Protect long-lived branches (main/develop): no direct push, PR + CI required.
Step 3 → Developers branch from the agreed base: feature/xyz.
Step 4 → Open PR, review, CI passes, merge (squash/merge/rebase per policy).
Step 5 → Map branch -> environment: main -> prod, develop -> staging.
Step 6 → Delete merged branches; tag releases.
```

| Strategy | Long-lived branches | Release style | Best for |
|---|---|---|---|
| Git Flow | main, develop (+release, hotfix) | scheduled releases | versioned/boxed software |
| GitHub Flow | main only | continuous, per PR | web apps/SaaS |
| Trunk-Based | main (trunk) | continuous, tiny commits | mature CI/CD, feature flags |

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → अपने release style के हिसाब से model चुनो (ऊपर की table)।
Step 2 → Long-lived branches (main/develop) protect करो: direct push नहीं, PR + CI ज़रूरी।
Step 3 → Developers agreed base से branch बनाते हैं: feature/xyz।
Step 4 → PR खोलो, review, CI pass, merge (squash/merge/rebase policy के अनुसार)।
Step 5 → Branch -> environment mapping: main -> prod, develop -> staging।
Step 6 → Merged branches delete करो; releases पर tag लगाओ।

---

## 🟡 Real World Example
A team with a Node.js API, FastAPI service and React app on one VPS picks **GitHub Flow**: `main` is always deployable; each feature is `feature/login-otp`; merging to `main` triggers GitHub Actions which builds a Docker image and deploys. A mobile-app company shipping monthly store releases would choose **Git Flow** with `release/*` branches because they must stabilise a version while new work continues.

## 🟡 Real Example Hindi mein
एक VPS पर Node.js API, FastAPI service और React app वाली team **GitHub Flow** चुनती है: `main` हमेशा deployable; हर feature `feature/login-otp`; `main` में merge होते ही GitHub Actions Docker image बनाकर deploy करता है। महीने में एक बार store release करने वाली mobile-app company **Git Flow** चुनेगी, `release/*` branches के साथ, क्योंकि एक version को stable करते समय नया काम चलता रहता है।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# branching-basic.sh - daily feature-branch loop (GitHub Flow style)
set -euo pipefail                                   # fail on any error

git switch main                                     # go to the main branch
git pull --ff-only origin main                      # update; refuse accidental merge commits
git switch -c feature/login-otp                     # create + switch to a new branch
echo "// otp" >> auth.js                            # make a change
git add auth.js                                     # stage it
git commit -m "feat(auth): add OTP login"           # commit with a clear message
git push -u origin feature/login-otp                # publish branch and set upstream
# now open a Pull Request on GitHub, get review, merge
git switch main                                     # after merge, return to main
git pull --ff-only origin main                      # get the merged result
git branch -d feature/login-otp                     # delete local branch
git push origin --delete feature/login-otp          # delete remote branch
```

## 💻 Code / Config Example — Advanced

Enforce the strategy with a GitHub ruleset-style workflow check: PRs must target `main` and come from an allowed branch name; CI runs on every PR; deploy only on `main`.

```yaml
# .github/workflows/branch-policy.yml
name: branch-policy                                 # shows in the PR checks list
on:
  pull_request:                                     # runs for every PR event
    branches: [main, develop]                       # PRs targeting these branches
jobs:
  check-name:
    runs-on: ubuntu-latest                          # runner
    steps:
      - name: Validate source branch name
        env:
          HEAD: ${{ github.head_ref }}              # source branch name (passed via env to avoid script injection)
        run: |
          if [[ ! "$HEAD" =~ ^(feature|bugfix|hotfix|release|chore)/[a-z0-9._-]+$ ]]; then
            echo "Branch '$HEAD' must look like feature/short-name"   # explain the rule
            exit 1                                  # fail the check
          fi
          echo "Branch name OK: $HEAD"              # success message
  test:
    needs: check-name                               # run only if name check passed
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4                   # fetch code (example version)
      - uses: actions/setup-node@v4                 # install Node (example version)
        with:
          node-version: 20                          # Node 20 LTS-line example
          cache: npm                                # cache npm downloads
      - run: npm ci && npm test                     # install exactly lockfile versions, then test
```

---

## 🟠 My Stack Integration
- **Environments:** `main` -> production VPS, `develop` (if used) -> staging container on same VPS on a different port.
- **Monorepo (api/, ml/, web/):** one strategy for all, use `paths:` filters in Actions so only changed services deploy.
- **Nginx:** staging and prod are separate `server_name` blocks (`staging.example.com`, `example.com`).
- **AWS:** branch -> ECR tag mapping (`main` -> `:prod-<sha>`).

```yaml
# deploy only from main, using branch to choose environment
on:
  push:
    branches: [main, develop]                       # both branches trigger a deploy workflow
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.ref_name == 'main' && 'production' || 'staging' }}   # pick env by branch
    steps:
      - run: echo "Deploying ${{ github.sha }} to ${{ github.ref_name }}"        # replace with real deploy
```

**Security:** enable branch protection on `main`: require PR, 1+ approvals, status checks, no force-push, no deletion. Restrict who can push to production-mapped branches.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Long-lived feature branches (weeks).
✅ Correct: Short branches (1-3 days), merge often; use feature flags for unfinished work.

❌ Mistake 2: Pushing directly to `main`.
✅ Correct: Branch protection + PR + required CI.

❌ Mistake 3: Choosing Git Flow for a web app deployed 10 times a day.
✅ Correct: GitHub Flow or trunk-based.

❌ Mistake 4: Never deleting merged branches.
✅ Correct: Enable "automatically delete head branches" in repo settings.

---

## 🧠 Tricky Interview Question
Two feature branches both changed `package-lock.json`. After the first merges, the second has conflicts. What is the clean way to resolve it?

**Answer:** Rebase or merge `main` into the feature branch, take the incoming `package.json` changes, then regenerate the lock file with `npm install` rather than hand-editing it, commit, and let CI confirm. Hand-merging lockfiles risks inconsistent dependency trees.

---

## ⚫ Interview Questions + Answers

Q1: Why do we need a branching strategy?
A1: Predictable releases, isolation of work, safe hotfixes, clear branch-to-environment mapping.

Q2: Merge vs rebase vs squash?
A2: Merge keeps full history with a merge commit; rebase replays commits for linear history (never rebase shared branches); squash combines a PR into one commit on main.

Q3: How do you handle a production hotfix?
A3: Branch from the production branch (`hotfix/x`), fix, PR, deploy, then ensure the fix flows back into other long-lived branches.

Q4: Which strategy suits CI/CD best?
A4: Trunk-based or GitHub Flow since main is always releasable.

Q5: What is branch protection?
A5: Repo rules that block risky actions (direct push, force push, merge without checks/reviews) on important branches.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one developer touches the same repo.
- You deploy to multiple environments.

❌ Avoid when:
- You over-engineer a solo hobby project with 5 permanent branches.
- The strategy is not enforced by tooling (rules on paper only).

---

## 📊 Visual Diagram

```
 main     o----o--------o--------o-----o--->  (deployable, protected)
           \    \      / \      /
 feature/a  o--o--o----   \    /
 feature/b                 o--o      (short-lived, deleted after merge)

 Env map:  main -> PROD      develop -> STAGING      feature/* -> CI only
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Branch | Parallel line of work | काम की parallel लाइन |
| Merge | Combine branches | branches जोड़ना |
| Rebase | Replay commits on new base | commits को नए base पर दोहराना |
| Squash | Combine commits into one | कई commits को एक बनाना |
| Branch protection | Rules guarding a branch | branch की सुरक्षा के नियम |
| Hotfix | Urgent production fix | urgent production सुधार |

---

## ⚡ 3-Line Summary
English: A branching strategy defines branches, flow and deployment mapping.
Choose Git Flow for scheduled releases, GitHub Flow or trunk-based for continuous delivery.
Enforce it with branch protection and CI.
Hindi: Branching strategy branches, flow और deployment mapping तय करती है।
Scheduled releases के लिए Git Flow, continuous delivery के लिए GitHub Flow या trunk-based चुनो।
इसे branch protection और CI से लागू करो।

---

## ➡️ Next Topic
**18. Git Flow** - the classic multi-branch model in detail.

---
