# 22. Commit Message Best Practices (Conventional Commits)
# हिंदी में: Commit Message के Best Practices (Conventional Commits)

---

## 🔵 Simple Definition (English)
A good commit message explains **what changed and why** in a short, consistent format. **Conventional Commits** is a spec: `type(scope): description`, with optional body and footer, for example `feat(auth): add OTP login`. Types like `feat` and `fix` can drive automatic version bumps and changelogs.

## 🔵 सरल परिभाषा (Hindi)
अच्छा commit message छोटे, consistent format में बताता है कि **क्या बदला और क्यों**। **Conventional Commits** एक spec है: `type(scope): description`, साथ में optional body और footer, जैसे `feat(auth): add OTP login`। `feat` और `fix` जैसे types से automatic version bump और changelog बन सकते हैं।

---

## 🔴 Problem it Solves
`git log` full of "fix", "update", "changes", "final final" is useless when you must find the commit that broke production at 2 AM. Release notes are written by hand and are wrong. Tools cannot decide whether the next version is a patch, minor or major. Structured messages make history searchable, enable automation (semantic-release, release-please) and help reviewers.

## 🔴 यह क्यों बना? (Hindi)
जब रात 2 बजे production तोड़ने वाला commit ढूँढना हो, तब "fix", "update", "changes", "final final" से भरा `git log` बेकार है। Release notes हाथ से लिखे जाते हैं और गलत होते हैं। Tools तय नहीं कर पाते कि अगला version patch, minor या major है। Structured messages से history searchable बनती है, automation (semantic-release, release-please) संभव होता है और reviewers को मदद मिलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Format:  <type>(<scope>): <subject>
                  <blank line>
                  <body: why, what, trade-offs>
                  <blank line>
                  <footer: BREAKING CHANGE: ..., Closes #123>
Step 2 → Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert.
Step 3 → Subject: imperative mood ("add", not "added"), <= 50-72 chars, no trailing period.
Step 4 → Breaking change: "feat!:" or footer "BREAKING CHANGE: ..." -> MAJOR bump.
Step 5 → Enforce with commitlint + husky (or a CI check on PR titles when squash-merging).
Step 6 → Tools read commits: feat -> MINOR, fix -> PATCH, ! -> MAJOR; generate CHANGELOG.
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Format: `<type>(<scope>): <subject>`, फिर खाली लाइन, body (क्यों/क्या), खाली लाइन, footer (BREAKING CHANGE, Closes #123)।
Step 2 → Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert।
Step 3 → Subject: imperative ("add", "added" नहीं), <= 50-72 chars, अंत में full stop नहीं।
Step 4 → Breaking change: "feat!:" या footer "BREAKING CHANGE: ..." -> MAJOR bump।
Step 5 → commitlint + husky से enforce करो (या squash-merge हो तो PR title का CI check)।
Step 6 → Tools commits पढ़ते हैं: feat -> MINOR, fix -> PATCH, ! -> MAJOR; CHANGELOG बनता है।

---

## 🟡 Real World Example
A payments team finds a bug: users charged twice. In `git log --grep "fix(payment)"` they instantly see the 4 related fixes and the one `feat(payment)!: switch to idempotency keys` that introduced a breaking API change, so release-please bumps from 2.3.0 to 3.0.0 and writes the changelog without a human typing it.

## 🟡 Real Example Hindi mein
Payments team को bug मिलता है: users से दो बार पैसे कटे। `git log --grep "fix(payment)"` से तुरंत 4 related fixes दिखते हैं और एक `feat(payment)!: switch to idempotency keys` जिसने breaking API change किया था। इसलिए release-please version 2.3.0 से 3.0.0 करता है और changelog बिना किसी के टाइप किए बना देता है।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# commits-basic.sh - examples of good Conventional Commits
set -euo pipefail                                                  # strict mode

git commit -m "feat(auth): add OTP login via SMS"                  # new feature -> MINOR
git commit -m "fix(cart): correct total when coupon applied"       # bug fix -> PATCH
git commit -m "docs(readme): document docker compose setup"        # docs only
git commit -m "refactor(api): extract payment service"             # no behaviour change
git commit -m "perf(db): add index on orders.user_id"              # performance improvement
git commit -m "ci: cache npm in GitHub Actions"                    # CI config change
git commit -m "feat(api)!: remove v1 /users endpoint" \
           -m "BREAKING CHANGE: clients must call /v2/users"       # ! + footer -> MAJOR; second -m is the body/footer paragraph
```

## 💻 Code / Config Example — Advanced

commitlint config, a husky hook, and a CI job validating the PR title (useful with squash merge). Package versions are examples.

```bash
#!/usr/bin/env bash
# setup-commitlint.sh - install commitlint + husky in a Node project
set -euo pipefail                                                  # strict mode
npm install --save-dev @commitlint/cli @commitlint/config-conventional husky   # dev dependencies
npx husky init                                                     # creates .husky/ (husky v9+ command)
echo 'npx --no -- commitlint --edit "$1"' > .husky/commit-msg      # run commitlint on every commit message
```

```javascript
// commitlint.config.js - rules for allowed commit messages
module.exports = {
  extends: ['@commitlint/config-conventional'],   // start from the standard Conventional Commits rules
  rules: {
    'subject-case': [2, 'never', ['upper-case', 'pascal-case', 'start-case']],  // error if subject is shouty/Title Case
    'header-max-length': [2, 'always', 72],       // header up to 72 chars
    'scope-enum': [1, 'always', ['api', 'web', 'ml', 'auth', 'payment', 'infra', 'deps']],  // warn on unknown scopes
  },
};
```

```yaml
# .github/workflows/pr-title.yml - validate PR title when using squash merge
name: pr-title                                          # check name
on:
  pull_request:                                         # PR events
    types: [opened, edited, synchronize, reopened]      # re-run when the title is edited
jobs:
  lint-title:
    runs-on: ubuntu-latest                              # runner
    steps:
      - name: Check Conventional Commit title
        env:
          TITLE: ${{ github.event.pull_request.title }} # pass via env (title is user-controlled text)
        run: |
          RE='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9-]+\))?!?: .{1,72}$'
          if [[ "$TITLE" =~ $RE ]]; then echo "OK"; else
            echo "::error::PR title must look like 'feat(scope): message'"   # explain the failure
            exit 1                                      # fail the check
          fi
```

---

## 🟠 My Stack Integration
- **Scopes for your stack:** `api` (Node), `ml` (FastAPI), `web` (React), `infra` (Docker/Nginx), `ci`.
- **Release automation:** release-please or semantic-release reads commits, bumps `package.json`, tags and writes CHANGELOG; the tag then triggers Docker build and VPS deploy.
- **Squash merge:** make PR title the commit message (repo setting), so only titles need linting.

```yaml
# .github/workflows/release-please.yml - auto release PR from Conventional Commits
name: release-please                                     # workflow name
on:
  push:
    branches: [main]                                     # run after merges to main
permissions:
  contents: write                                        # create tags/releases
  pull-requests: write                                   # open the release PR
jobs:
  release:
    runs-on: ubuntu-latest                               # runner
    steps:
      - uses: googleapis/release-please-action@v4        # example version, check docs for current inputs
        with:
          release-type: node                             # bump package.json style versions
```

**Security:** never put secrets or customer data in commit messages (history is permanent and public to all collaborators). Consider signed commits (`git commit -S`) and "Require signed commits" for sensitive repos.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Messages like "fix", "wip", "asdf".
✅ Correct: `fix(login): handle expired OTP`.

❌ Mistake 2: Mixing unrelated changes in one commit.
✅ Correct: One logical change per commit (`git add -p`).

❌ Mistake 3: Past tense and long subject lines.
✅ Correct: Imperative, <= 72 chars; details go in the body.

❌ Mistake 4: Forgetting `BREAKING CHANGE`, so releases bump the wrong version.
✅ Correct: Use `!` or a footer for incompatible changes.

---

## 🧠 Tricky Interview Question
You committed a password into a commit message and pushed. Is `git revert` enough?

**Answer:** No. Revert adds a new commit; history still contains the old message. Rotate the password immediately (assume compromised). Rewriting history (`git filter-repo`, force push) can remove it from the repo but not from forks, clones or caches, so rotation is the real fix.

---

## ⚫ Interview Questions + Answers

Q1: Why imperative mood?
A1: It matches Git's own messages ("Merge...", "Revert...") and reads as "If applied, this commit will <subject>".

Q2: How do Conventional Commits map to SemVer?
A2: `fix` -> PATCH, `feat` -> MINOR, `BREAKING CHANGE`/`!` -> MAJOR.

Q3: How to amend the last commit message?
A3: `git commit --amend` (only if not pushed or you accept force-push on your own branch).

Q4: What should the body explain?
A4: Why the change was needed, what approach, and side effects, not a line-by-line diff.

Q5: How to enforce the format?
A5: commitlint + husky locally, plus a CI check for PR title or commits.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want automated changelogs/versioning and searchable history.

❌ Avoid when:
- Solo throwaway scripts (but a clear message still helps).
- Team not ready to learn it; start with only feat/fix/chore.

---

## 📊 Visual Diagram

```
 feat(auth)!: add OTP login          <- header: type(scope)!: subject
                                     <- blank line
 Replace password login with OTP     <- body: why/what
 to cut credential stuffing.
                                     <- blank line
 BREAKING CHANGE: /login removed     <- footer
 Closes #123

 commits --> release-please --> version bump + CHANGELOG + tag --> deploy
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Conventional Commits | Commit message spec | commit message का standard |
| Scope | Area affected | प्रभावित हिस्सा |
| Breaking change | Incompatible change | पुराने code को तोड़ने वाला बदलाव |
| commitlint | Linter for messages | message जाँचने वाला tool |
| husky | Git hooks manager | Git hooks चलाने वाला tool |
| Changelog | Release notes file | release notes की फ़ाइल |

---

## ⚡ 3-Line Summary
English: Write commits as type(scope): imperative subject, with a body for the why.
feat/fix/! map to MINOR/PATCH/MAJOR so tools can release automatically.
Enforce with commitlint or PR-title checks.
Hindi: Commits type(scope): imperative subject में लिखो, और why के लिए body।
feat/fix/! का मतलब MINOR/PATCH/MAJOR, इसलिए tools automatic release कर सकते हैं।
commitlint या PR-title check से enforce करो।

---

## ➡️ Next Topic
**23. Git Tags + Versioning** - marking commits as releases.

---
