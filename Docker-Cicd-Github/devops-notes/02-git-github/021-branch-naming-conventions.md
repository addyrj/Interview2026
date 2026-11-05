# 21. Branch Naming Conventions
# हिंदी में: Branch Naming Conventions (Branch के नाम रखने के नियम)

---

## 🔵 Simple Definition (English)
A **branch naming convention** is a team rule for naming branches in a predictable pattern, usually `type/short-description` or `type/TICKET-123-short-description` (for example `feature/login-otp`, `fix/PAY-482-double-charge`). Tools and people can then see the purpose and owner of a branch at a glance.

## 🔵 सरल परिभाषा (Hindi)
**Branch naming convention** branches के नाम एक predictable pattern में रखने का team नियम है, आमतौर पर `type/short-description` या `type/TICKET-123-short-description` (जैसे `feature/login-otp`, `fix/PAY-482-double-charge`)। इससे tools और लोग एक नज़र में branch का उद्देश्य और ticket समझ लेते हैं।

---

## 🔴 Problem it Solves
Branches named `test`, `new-branch`, `aditya-final2` say nothing. Nobody knows what can be deleted, which ticket it belongs to, or which CI rule applies. Automation also needs patterns: "deploy preview for `feature/*`", "run security scan for `release/*`". A convention gives clean history, simple automation, easy cleanup and traceability to Jira/GitHub issues.

## 🔴 यह क्यों बना? (Hindi)
`test`, `new-branch`, `aditya-final2` जैसे नाम कुछ नहीं बताते। पता नहीं क्या delete हो सकता है, कौन-सा ticket है, कौन-सा CI rule लगेगा। Automation को patterns चाहिए: "`feature/*` के लिए preview deploy", "`release/*` के लिए security scan"। Convention साफ history, आसान automation, आसान cleanup और Jira/GitHub issues से traceability देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Agree on prefixes: feature, fix (or bugfix), hotfix, release, chore, docs, refactor, test.
Step 2 → Pattern: <type>/<ticket-optional>-<kebab-case-description>
Step 3 → Rules: lowercase, hyphens, no spaces, short (< ~50 chars), no personal names.
Step 4 → Enforce with a Git hook or CI check (and GitHub rulesets "branch name pattern" if available on your plan).
Step 5 → Use the same prefix in CI triggers (on: push: branches: ['feature/**']).
```

Valid examples: `feature/login-otp`, `fix/PAY-482-double-charge`, `hotfix/1.4.1`, `release/1.5.0`, `chore/bump-node-20`.
Invalid: `Feature/Login OTP`, `aditya-test`, `fix`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Prefixes तय करो: feature, fix (या bugfix), hotfix, release, chore, docs, refactor, test।
Step 2 → Pattern: <type>/<ticket-optional>-<kebab-case-description>
Step 3 → नियम: lowercase, hyphens, spaces नहीं, छोटा नाम (< ~50 chars), personal नाम नहीं।
Step 4 → Git hook या CI check से enforce करो (और plan में हो तो GitHub rulesets का branch name pattern)।
Step 5 → CI triggers में वही prefix use करो (on: push: branches: ['feature/**'])।

---

## 🟡 Real World Example
A team on Jira ticket `SHOP-231` "Add coupon codes" names the branch `feature/SHOP-231-coupon-codes`. Jira auto-links the branch and PR to the ticket. Actions deploys `feature/**` to a preview URL and `hotfix/**` to a fast-track pipeline. When cleaning up, the team deletes all merged `feature/*` branches safely.

## 🟡 Real Example Hindi mein
Jira ticket `SHOP-231` "Add coupon codes" के लिए team branch का नाम `feature/SHOP-231-coupon-codes` रखती है। Jira branch और PR को ticket से अपने-आप link कर देता है। Actions `feature/**` को preview URL पर और `hotfix/**` को fast-track pipeline पर deploy करता है। Cleanup में merged `feature/*` branches सुरक्षित रूप से delete हो जाती हैं।

---

## 💻 Code / Config Example — Basic

A local `commit-msg`-style guard is not for branches; use a `pre-push` hook to block badly named branches (save as `.git/hooks/pre-push`, `chmod +x`).

```bash
#!/usr/bin/env bash
# .git/hooks/pre-push - reject pushes from badly named branches
branch="$(git symbolic-ref --short HEAD)"                  # current branch name
pattern='^(feature|fix|bugfix|hotfix|release|chore|docs|refactor|test)/[a-zA-Z0-9._-]+$'   # allowed pattern

# main and develop are allowed as long-lived names
if [[ "$branch" == "main" || "$branch" == "develop" ]]; then
  exit 0                                                   # nothing to check
fi

if [[ ! "$branch" =~ $pattern ]]; then                     # regex match test
  echo "ERROR: branch '$branch' must match: $pattern"      # tell the developer what is wrong
  echo "Rename with: git branch -m feature/short-name"     # show the fix
  exit 1                                                   # non-zero exit blocks the push
fi
exit 0                                                     # name is valid
```

## 💻 Code / Config Example — Advanced

CI check that also extracts a ticket id and posts a clear error; runs for every PR so bypassing local hooks does not help.

```yaml
# .github/workflows/branch-name.yml
name: branch-name-check                                    # check name in the PR UI
on:
  pull_request:                                            # every PR event
    types: [opened, edited, synchronize, reopened]         # re-check when PR changes
jobs:
  validate:
    runs-on: ubuntu-latest                                 # runner
    steps:
      - name: Validate branch name
        env:
          BRANCH: ${{ github.head_ref }}                   # pass via env (never inline into shell script text)
        run: |
          REGEX='^(feature|fix|bugfix|hotfix|release|chore|docs|refactor|test)/([A-Z]+-[0-9]+-)?[a-z0-9][a-z0-9._-]*$'
          if [[ "$BRANCH" =~ $REGEX ]]; then
            echo "OK: $BRANCH"                             # valid
          else
            echo "::error::Branch '$BRANCH' does not follow type/[TICKET-]kebab-name"   # annotate failure in UI
            exit 1                                         # fail the check
          fi
      - name: Extract ticket id (optional)
        env:
          BRANCH: ${{ github.head_ref }}                   # same safe env passing
        run: |
          TICKET=$(echo "$BRANCH" | grep -oE '[A-Z]+-[0-9]+' || true)   # find e.g. SHOP-231 or nothing
          echo "Ticket: ${TICKET:-none}"                   # print result
```

---

## 🟠 My Stack Integration
- **Monorepo:** include the service in the name when useful: `feature/api-rate-limit`, `fix/web-cart-bug`, `feature/ml-embeddings`.
- **CI mapping:** `feature/web-*` triggers React build; `feature/api-*` triggers Node tests (via `paths:` filters or name filters).
- **Docker tag from branch:** slashes are invalid in image tags, so sanitise.
- **Nginx previews:** subdomain from sanitised branch name (`feature-login-otp.preview.example.com`).

```bash
# Turn a branch name into a safe Docker tag / DNS label (run in CI)
RAW="${GITHUB_HEAD_REF:-$(git rev-parse --abbrev-ref HEAD)}"      # branch name
SAFE=$(echo "$RAW" | tr '[:upper:]' '[:lower:]' | sed 's#[^a-z0-9]#-#g' | cut -c1-40)  # lowercase, replace / and others with -, limit length
echo "Docker tag: myorg/api:${SAFE}"                              # e.g. myorg/api:feature-login-otp
```

**Security:** never put secrets, customer names or vulnerability details in branch names (they are visible in the repo and logs). In workflows, always pass `github.head_ref` through `env:` because a malicious branch name can inject shell commands if interpolated directly into `run:`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using spaces, uppercase or special characters.
✅ Correct: lowercase kebab-case with a type prefix.

❌ Mistake 2: Personal names such as `aditya/work`.
✅ Correct: Describe purpose, not owner (Git already shows the author).

❌ Mistake 3: Writing `${{ github.head_ref }}` directly inside a `run:` script.
✅ Correct: Pass it through `env:` to prevent script injection.

❌ Mistake 4: Creating `feature` and `feature/x` in the same repo.
✅ Correct: A branch name cannot be both a file and a directory in refs, so always use prefixes consistently (Git refuses this conflict).

---

## 🧠 Tricky Interview Question
You try `git branch feature` when `feature/login` already exists. What happens and why?

**Answer:** Git errors out because refs are stored as paths: `refs/heads/feature/login` needs `feature` to be a directory, so `refs/heads/feature` cannot exist as a file. That is why a consistent prefix scheme must be chosen early. (Packed refs can differ in edge cases, but Git still rejects the conflict.)

---

## ⚫ Interview Questions + Answers

Q1: Why use prefixes like feature/ and fix/?
A1: They communicate intent, enable glob-based CI triggers and make cleanup and filtering easy.

Q2: Should the ticket ID be in the name?
A2: Yes if you use a tracker; it links branch, PR and ticket automatically.

Q3: How to rename a branch already pushed?
A3: `git branch -m old new`, `git push origin -u new`, `git push origin --delete old`, and update any open PR.

Q4: How do you enforce naming?
A4: Local hook (optional), CI check (reliable), GitHub rulesets (where available).

Q5: Why avoid slashes in Docker tags?
A5: Tags allow only letters, digits, `_`, `.`, `-`; slashes would be read as repository path.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one contributor or automated pipelines react to branches.

❌ Avoid when:
- Over-strict rules that block urgent hotfixes (keep the pattern simple).

---

## 📊 Visual Diagram

```
 <type> / [TICKET-] <kebab-description>
   |         |              |
 feature   SHOP-231    coupon-codes
   |
   +--> CI trigger: on.push.branches: ['feature/**']
   +--> Preview URL: feature-shop-231-coupon-codes.preview.example.com
   +--> Jira auto-link via SHOP-231
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Convention | Agreed naming rule | तय नामकरण नियम |
| Kebab-case | words-with-hyphens | हाइफ़न वाले शब्द |
| Prefix | Leading type label | शुरुआती type label |
| Ticket ID | Tracker issue key | issue tracker की key |
| Glob | Wildcard pattern like feature/** | wildcard pattern |

---

## ⚡ 3-Line Summary
English: Name branches as type/[ticket-]short-kebab-name.
This enables clean history, CI automation and traceability.
Enforce it in CI and pass branch names safely via env.
Hindi: Branches का नाम type/[ticket-]short-kebab-name रखो।
इससे साफ history, CI automation और traceability मिलती है।
CI में enforce करो और branch नाम env के ज़रिए safely पास करो।

---

## ➡️ Next Topic
**22. Commit Message Best Practices (Conventional Commits)** - naming for commits, not branches.

---
