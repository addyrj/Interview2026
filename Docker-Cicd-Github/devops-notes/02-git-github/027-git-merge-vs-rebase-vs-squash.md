---

# 27. Git Merge vs Rebase vs Squash
# हिंदी में: Git Merge बनाम Rebase बनाम Squash

---

## 🔵 Simple Definition (English)
Merge, rebase and squash are three ways to bring the work of one branch into another. **Merge** joins two histories with a merge commit. **Rebase** replays your commits on top of another branch to make a straight line. **Squash** collapses many commits into one commit.

## 🔵 सरल परिभाषा (Hindi)
Merge, rebase और squash एक branch का काम दूसरी branch में लाने के तीन तरीके हैं। **Merge** दो histories को एक merge commit से जोड़ता है। **Rebase** आपके commits को दूसरी branch के ऊपर दोबारा चलाकर सीधी लाइन बनाता है। **Squash** कई commits को एक commit में बदल देता है।

---

## 🔴 Problem it Solves
A team of 5 developers pushes to `main` every day. Without a clear strategy the history becomes a mess: "fix typo", "wip", "again fix", and criss-cross merge lines. Finding which commit broke production (`git bisect`), reverting one feature, or reading the changelog becomes painful.
Each strategy solves a different part: merge keeps the true history, rebase keeps it linear, squash keeps one clean commit per feature.

## 🔴 यह क्यों बना? (Hindi)
5 developers रोज़ `main` में push करते हैं। बिना strategy के history गंदी हो जाती है: "fix typo", "wip", "again fix" और उलझी हुई merge lines। Production किस commit से टूटा (`git bisect`), एक feature को revert करना, या changelog पढ़ना मुश्किल हो जाता है।
हर strategy अलग समस्या हल करती है: merge असली history रखता है, rebase history सीधी रखता है, squash हर feature का एक साफ़ commit रखता है।

---

## 🟢 How it Works — Step by Step

```
Start:        A---B---C   (main)
                   \
                    D---E (feature)

MERGE:   Step 1 → git switch main
         Step 2 → git merge feature
         Step 3 → new merge commit M with 2 parents
                  A---B---C-------M  (main)
                       \         /
                        D---E---/

REBASE:  Step 1 → git switch feature
         Step 2 → git rebase main
         Step 3 → D, E are copied as D', E' on top of C (new hashes!)
                  A---B---C---D'---E'  (feature)
         Step 4 → git switch main && git merge --ff-only feature

SQUASH:  Step 1 → git switch main
         Step 2 → git merge --squash feature
         Step 3 → all changes staged, git commit -m "feat: x"
                  A---B---C---S   (S = D+E in one commit)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Merge  → Step 1: main पर जाओ  Step 2: git merge feature
         Step 3: दो parents वाला नया merge commit बनता है, history जैसी थी वैसी रहती है।
Rebase → Step 1: feature पर जाओ  Step 2: git rebase main
         Step 3: D, E के नए copies (D', E', नए hash) main के ऊपर लगते हैं।
         Step 4: main पर fast-forward merge होता है, सीधी लाइन मिलती है।
Squash → Step 1: git merge --squash feature  Step 2: सारे changes staged होते हैं
         Step 3: एक commit करो, feature के सारे commits एक में।
```

---

## 🟡 Real World Example
A Node.js + FastAPI team on a VPS: developer creates `feature/login-otp` with 14 messy commits ("wip", "fix lint", "oops"). In the GitHub PR they choose **Squash and merge**. `main` gets one commit `feat: login via OTP (#142)`. When OTP breaks production at 2 AM, the on-call engineer runs `git revert <that-one-commit>` and redeploys. Had it been 14 commits plus merge commits, the revert would be risky.
Meanwhile, a long-running release branch uses **merge commits** so that the exact point of integration is visible. Locally, before opening the PR, the developer runs `git pull --rebase` to avoid a useless "Merge branch main into feature" commit.

## 🟡 Real Example Hindi mein
Node.js + FastAPI team VPS पर: developer `feature/login-otp` बनाता है जिसमें 14 गंदे commits हैं ("wip", "fix lint", "oops")। GitHub PR में वह **Squash and merge** चुनता है। `main` में एक ही commit आता है `feat: login via OTP (#142)`। रात 2 बजे OTP production में टूटे तो on-call engineer सिर्फ `git revert <वह-एक-commit>` करके redeploy कर देता है। 14 commits और merge commits होते तो revert जोखिम भरा होता।
Long-running release branch पर **merge commit** इस्तेमाल होता है ताकि integration का सही बिंदु दिखे। PR खोलने से पहले developer local में `git pull --rebase` चलाता है ताकि बेकार "Merge branch main" commit न बने।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# merge-demo.sh - safe playground to see all three strategies
set -euo pipefail                          # stop on first error, undefined vars, pipe errors

rm -rf /tmp/git-demo && mkdir /tmp/git-demo && cd /tmp/git-demo   # fresh sandbox folder
git init -q -b main                        # create repo with branch named main
git config user.email "dev@example.com"    # local identity (needed for commits)
git config user.name "Dev"                 # local name

echo "a" > app.txt && git add . && git commit -qm "A: base"   # first commit on main
git switch -q -c feature                   # create and move to feature branch
echo "b" >> app.txt && git commit -qam "D: feature work 1"    # feature commit 1
echo "c" >> app.txt && git commit -qam "E: feature work 2"    # feature commit 2

git switch -q main                         # go back to main
echo "x" > other.txt && git add . && git commit -qm "C: hotfix on main"  # main moves ahead

# ---- Option 1: MERGE ----
git switch -q -c try-merge main            # throwaway branch from main
git merge --no-ff feature -m "Merge feature"   # --no-ff always creates a merge commit
git log --oneline --graph                  # shows the diamond shape

# ---- Option 2: REBASE ----
git switch -q -c try-rebase feature        # throwaway branch from feature
git rebase main                            # replay D,E on top of C
git log --oneline --graph                  # shows a straight line

# ---- Option 3: SQUASH ----
git switch -q -c try-squash main           # throwaway branch from main
git merge --squash feature                 # stage all feature changes, no commit yet
git commit -qm "feat: feature (squashed)"  # one single commit
git log --oneline --graph                  # one commit for the whole feature
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# team-workflow.sh - production style daily workflow + repo config
set -euo pipefail                                   # strict mode

# ---- one-time repo/global config ----
git config --global pull.rebase true                # git pull = fetch + rebase (no noise merge commits)
git config --global rebase.autoStash true           # auto stash dirty files during rebase
git config --global rerere.enabled true             # remember conflict resolutions and reuse them
git config --global merge.conflictstyle zdiff3      # clearer conflict markers (git >= 2.35)
git config --global fetch.prune true                # delete remote-tracking refs removed on GitHub

# ---- daily feature flow ----
git switch main && git pull                         # update local main
git switch -c feature/otp-login                     # new branch
# ... work, commit often ...
git fetch origin                                    # get latest remote state
git rebase origin/main                              # keep branch on top of latest main (private branch only!)
git push --force-with-lease origin feature/otp-login   # safe force push after rebase (fails if someone else pushed)

# ---- tidy commits before PR (interactive; needs a terminal) ----
# git rebase -i origin/main      # mark commits as squash/fixup/reword in the editor

# ---- undo a bad rebase ----
git reflog                                          # find the HEAD position before rebase
# git reset --hard HEAD@{5}                         # go back to that state (pick the right index!)
```

---

## 🟠 My Stack Integration
Your Node.js/FastAPI/React repos deploy from `main` to a VPS or AWS through GitHub Actions. Decide the merge method in **Settings → General → Pull Requests** and combine with branch protection (topic 33). Recommended: feature PRs = **squash**, release/hotfix back-merges = **merge commit**, local sync = **rebase**.

```yaml
# .github/workflows/ci.yml - works the same for any merge style, but fetch-depth matters
name: CI                                   # workflow name shown in the Actions tab
on:
  pull_request:                            # run on every PR (tests the merge result)
    branches: [main]                       # only PRs targeting main
jobs:
  test:                                    # job id
    runs-on: ubuntu-latest                 # GitHub hosted runner
    steps:
      - uses: actions/checkout@v4          # example version, update to latest v4/v5
        with:
          fetch-depth: 0                   # full history, needed by changelog/semantic-release tools
      - uses: actions/setup-node@v4        # install Node.js
        with:
          node-version: 20                 # LTS example
          cache: npm                       # cache ~/.npm
      - run: npm ci                        # reproducible install from lockfile
      - run: npm test                      # run tests
```
Security: never force-push to `main`; protect it. Rebase rewrites hashes, so signed commits (GPG/SSH) must be re-signed. Squash merge by GitHub signs the resulting commit with GitHub's key.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Rebasing a branch that others already pulled (shared branch like `main` or `develop`).
✅ Correct: Rebase only your own private branches. Golden rule: never rewrite public history.

❌ Mistake 2: Using `git push --force` after rebase.
✅ Correct: Use `git push --force-with-lease`, it refuses if the remote has commits you have not seen.

❌ Mistake 3: Squashing a huge 3-week feature into one commit, losing all useful history.
✅ Correct: Keep PRs small (< 400 lines). Use squash for small PRs, merge commit or rebase-merge for large well-structured ones.

❌ Mistake 4: Continuing to work on a branch after it was squash-merged. Git does not know the commits are already in main, so conflicts reappear.
✅ Correct: After a squash merge, delete the branch and start a new one from the updated `main`.

---

## 🧠 Tricky Interview Question
You squash-merged `feature-A` into `main`. A colleague had branched `feature-B` from `feature-A`. Now `feature-B` shows the same changes again with conflicts. Why, and how do you fix it?

Answer: Squash creates a brand-new commit S with a different hash. `feature-B` still contains the original commits D and E, so Git thinks they are not in `main`. Fix: `git rebase --onto main feature-A feature-B`. This replays only the commits that are in `feature-B` but not in `feature-A` on top of `main`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between merge and rebase?
A1: Merge preserves history and adds a merge commit with two parents. Rebase rewrites your commits as new ones on top of the target, producing a linear history, and changes commit hashes.

Q2: When is `git merge --ff-only` useful?
A2: It succeeds only if the branch can be fast-forwarded (no divergence). It guarantees no merge commit and fails loudly otherwise, perfect after a rebase in CI scripts.

Q3: What is `git pull --rebase`?
A3: It fetches and then rebases your local unpushed commits on top of the remote branch instead of creating a merge commit. It keeps history clean.

Q4: What does "Rebase and merge" on GitHub do?
A4: It rebases each commit of the PR onto the base branch and fast-forwards, keeping all commits individually but with new hashes and no merge commit.

Q5: How do you recover after a bad rebase?
A5: `git reflog` shows every previous HEAD position. Reset the branch to the commit before the rebase with `git reset --hard <hash>`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Merge commit: long-lived branches, release branches, when exact integration history matters
- Rebase: syncing your private feature branch with main, cleaning commits before PR
- Squash: small features or many "wip" commits, one-commit-per-PR policy, easy revert

❌ Avoid when:
- Rebase: on shared/public branches or already-reviewed commits others commented on
- Squash: very large PRs where individual commit history helps debugging, or when others branched from your branch
- Merge: when the team demands strictly linear history (use squash/rebase instead)

---

## 📊 Visual Diagram
```
 BEFORE            MERGE (--no-ff)      REBASE + ff         SQUASH
 A-B-C  main       A-B-C------M         A-B-C-D'-E'         A-B-C-S
    \                 \      /                                   (S = D+E)
     D-E feature       D----E
 history: true,      history: true,     history: linear,    history: linear,
 merge commit        branchy            new hashes          1 commit/feature
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Merge commit | Commit with two parents joining histories | दो parents वाला जोड़ने वाला commit |
| Fast-forward | Just move the branch pointer, no new commit | सिर्फ pointer आगे खिसकाना |
| Rebase | Replay commits on a new base | commits को नए base पर दोबारा चलाना |
| Squash | Combine many commits into one | कई commits को एक बनाना |
| force-with-lease | Safe force push | सुरक्षित force push |
| reflog | Local log of HEAD movements | HEAD की local history |

---

## ⚡ 3-Line Summary
English: Merge keeps true history, rebase makes it linear, squash makes one commit per feature.
Never rebase shared branches; use `--force-with-lease` on private ones.
For most PR-based teams: squash and merge into main is the easiest to revert and read.
Hindi: Merge असली history रखता है, rebase उसे सीधी करता है, squash हर feature का एक commit बनाता है।
Shared branch को कभी rebase मत करो; private branch पर `--force-with-lease` इस्तेमाल करो।
ज़्यादातर PR-based teams के लिए main में squash and merge सबसे आसान है।

---

## ➡️ Next Topic
**28. Merge Conflicts — How to Resolve**: merge and rebase will eventually conflict, so you must know how to read markers and resolve safely.

---
