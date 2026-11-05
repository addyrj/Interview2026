---

# 32. GitHub Repository Settings
# हिंदी में: GitHub Repository की Settings

---

## 🔵 Simple Definition (English)
**Repository settings** are the controls under a repo's **Settings** tab: who can access it, which merge methods are allowed, branch rules, Actions permissions, security scanning, secrets, webhooks and deploy keys. They define the safety and workflow rules of the project.

## 🔵 सरल परिभाषा (Hindi)
**Repository settings** repo के **Settings** tab के controls हैं: कौन access कर सकता है, कौन से merge methods allowed हैं, branch rules, Actions permissions, security scanning, secrets, webhooks और deploy keys। ये project के सुरक्षा और workflow के नियम तय करते हैं।

---

## 🔴 Problem it Solves
A new repo has permissive defaults: anyone with write access can push to `main`, Actions get broad token permissions, merged branches stay forever, and secrets alerts are off. One bad default (e.g., public repo with an `.env`) can become a breach. Settings let you harden the repo and standardize workflow.

## 🔴 यह क्यों बना? (Hindi)
नई repo के defaults ढीले होते हैं: write access वाला कोई भी `main` में push कर सकता है, Actions को बड़े token permissions मिलते हैं, merged branches हमेशा पड़ी रहती हैं और secret alerts बंद होते हैं। एक गलत default (जैसे public repo में `.env`) breach बन सकता है। Settings से repo को सख़्त और workflow को standard बनाया जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Repo → Settings → General: name, default branch (main), features (Issues, Wiki, Projects)
Step 2 → General → Pull Requests: allow squash merge only, "Automatically delete head branches"
Step 3 → Collaborators and teams: give least privilege (Read/Triage/Write/Maintain/Admin)
Step 4 → Branches / Rulesets: protect main (topic 33)
Step 5 → Actions → General: allowed actions, default GITHUB_TOKEN = read-only, fork PR approval
Step 6 → Secrets and variables (topics 35-37), Environments (topic 35)
Step 7 → Code security: Dependabot alerts/updates, secret scanning + push protection, code scanning (CodeQL)
Step 8 → Webhooks / Deploy keys: integrations (use read-only deploy key for VPS pull)
Step 9 → Danger Zone: visibility, transfer, archive, delete
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Repo → Settings → General: नाम, default branch (main), features (Issues, Wiki, Projects)
Step 2 → General → Pull Requests: सिर्फ squash merge allow करो, "Automatically delete head branches" चालू करो
Step 3 → Collaborators and teams: कम से कम ज़रूरी permission दो (Read/Triage/Write/Maintain/Admin)
Step 4 → Branches / Rulesets: main को protect करो (topic 33)
Step 5 → Actions → General: allowed actions, default GITHUB_TOKEN = read-only, fork PR approval
Step 6 → Secrets and variables (topics 35-37), Environments (topic 35)
Step 7 → Code security: Dependabot, secret scanning + push protection, code scanning (CodeQL)
Step 8 → Webhooks / Deploy keys: integrations (VPS पर pull के लिए read-only deploy key)
Step 9 → Danger Zone: visibility, transfer, archive, delete
```

---

## 🟡 Real World Example
A team deploys a FastAPI app to an AWS EC2 box. After an intern force-pushed over `main`, they hardened settings: only squash merges, auto-delete branches, `main` protected, Actions token read-only by default, Dependabot security updates on, secret scanning push protection on (it blocked a real AWS key two weeks later), and the VPS uses a **read-only deploy key** instead of an engineer's personal SSH key. Settings are applied to all new repos with a script using the `gh` CLI.

## 🟡 Real Example Hindi mein
एक team AWS EC2 पर FastAPI app deploy करती है। एक intern के `main` पर force-push करने के बाद उन्होंने settings सख़्त कीं: सिर्फ squash merge, branches auto-delete, `main` protected, Actions token default read-only, Dependabot security updates चालू, secret scanning push protection चालू (दो हफ़्ते बाद इसने असली AWS key रोकी), और VPS इंजीनियर की personal SSH key की जगह **read-only deploy key** इस्तेमाल करता है। सारी नई repos पर ये settings `gh` CLI script से लगती हैं।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# repo-settings-basic.sh - configure a repo from the terminal with GitHub CLI
# Needs: gh auth login (admin rights on the repo)
set -euo pipefail                                   # strict mode
REPO="${1:?usage: $0 owner/repo}"                   # first argument: owner/repo, required

# PATCH /repos/{owner}/{repo} changes General settings (real REST API fields)
gh api -X PATCH "repos/$REPO" \
  -F allow_squash_merge=true \
  -F allow_merge_commit=false \
  -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true \
  -F allow_auto_merge=true \
  -F has_wiki=false                                 # squash only, delete merged branches, allow auto-merge, no wiki

gh repo view "$REPO" --json name,visibility,defaultBranchRef   # verify what we changed
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# repo-settings-hardened.sh - production hardening via REST API (gh api)
# Endpoint names are real GitHub REST endpoints; some need admin and a plan that supports them.
set -euo pipefail                                   # strict mode
REPO="${1:?usage: $0 owner/repo}"                   # owner/repo

# 1) General merge settings
gh api -X PATCH "repos/$REPO" \
  -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true -F squash_merge_commit_title=PR_TITLE \
  -F squash_merge_commit_message=PR_BODY            # squash commit uses PR title + description

# 2) Actions: default GITHUB_TOKEN is read-only, Actions cannot approve PRs
gh api -X PUT "repos/$REPO/actions/permissions/workflow" \
  -f default_workflow_permissions=read \
  -F can_approve_pull_request_reviews=false         # least privilege for workflows

# 3) Security: Dependabot alerts + automated security fixes
gh api -X PUT "repos/$REPO/vulnerability-alerts"    # turn on Dependabot alerts
gh api -X PUT "repos/$REPO/automated-security-fixes"   # turn on Dependabot security updates

# 4) Secret scanning + push protection (available on public repos, or private with GitHub Advanced Security)
gh api -X PATCH "repos/$REPO" --input - <<'JSON'
{
  "security_and_analysis": {
    "secret_scanning": { "status": "enabled" },
    "secret_scanning_push_protection": { "status": "enabled" }
  }
}
JSON

# 5) Read-only deploy key for the VPS (generate key pair on the server first: ssh-keygen -t ed25519)
# gh repo deploy-key add ./vps_deploy_key.pub --repo "$REPO" --title "prod-vps (read-only)"
# (read-only is the default; add --allow-write only if the server must push)

echo "Hardening applied to $REPO"                   # done
```
Not run against a real repository here (no network/account). Field availability varies by plan; verify in GitHub's REST docs.

---

## 🟠 My Stack Integration
For Node.js/FastAPI/React on a VPS: use a deploy key for `git pull` on the server, GitHub Secrets for SSH deploy from Actions, Dependabot for npm and pip, and Actions read-only default permissions. Add `dependabot.yml` to the repo:

```yaml
# .github/dependabot.yml - automatic dependency update PRs
version: 2                                  # config schema version
updates:                                    # list of ecosystems to watch
  - package-ecosystem: "npm"                # Node.js / React packages
    directory: "/"                          # where package.json lives (change for monorepo e.g. /apps/web)
    schedule:
      interval: "weekly"                    # check once a week
    open-pull-requests-limit: 5             # avoid PR spam
  - package-ecosystem: "pip"                # FastAPI requirements.txt / pyproject
    directory: "/"                          # location of requirements.txt
    schedule:
      interval: "weekly"                    # weekly
  - package-ecosystem: "github-actions"     # keep action versions fresh
    directory: "/"                          # workflows are found automatically
    schedule:
      interval: "weekly"                    # weekly
  - package-ecosystem: "docker"             # base images in Dockerfile
    directory: "/"                          # folder with Dockerfile
    schedule:
      interval: "weekly"                    # weekly
```
Security: enable 2FA for the org, require SSO if available, review "Outside collaborators" quarterly, and never grant Admin when Write is enough.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Giving everyone Admin "to avoid asking".
✅ Correct: Use teams with Write/Maintain; Admin only for 1-2 owners.

❌ Mistake 2: Leaving default `GITHUB_TOKEN` as read-write for all workflows.
✅ Correct: Set default to read, and grant `permissions:` per workflow/job when needed.

❌ Mistake 3: Using a personal SSH key on the VPS for `git pull`.
✅ Correct: Use a per-repo read-only deploy key, so leaving the company does not break deploys and blast radius is small.

❌ Mistake 4: Making a repo public to "quickly share" without scanning history for secrets.
✅ Correct: Scan with gitleaks/trufflehog first; rotate anything found (removing the file does not remove it from history).

---

## 🧠 Tricky Interview Question
A secret was committed and then removed in the next commit, and the repo is private. Is it safe?

Answer: No. The secret remains in Git history, forks, clones, and potentially in cached views. The correct response is to **rotate (revoke) the secret immediately**, then optionally rewrite history (`git filter-repo`) and force push. Rotation is mandatory; history rewriting is only cleanup. Prevention: push protection and pre-commit gitleaks.

---

## ⚫ Interview Questions + Answers

Q1: What repository roles exist?
A1: Read, Triage, Write, Maintain, Admin (plus custom roles on Enterprise). Choose the lowest that does the job.

Q2: Why restrict merge methods?
A2: To keep a consistent history (e.g. squash only) and make reverts easy.

Q3: What is a deploy key?
A3: An SSH public key attached to ONE repository, read-only by default, used by servers to clone/pull without a user account.

Q4: What is secret scanning push protection?
A4: It blocks a push containing known secret patterns (AWS keys, tokens) before it lands in the repo.

Q5: How do you stop forks from running dangerous workflows?
A5: Actions settings: require approval for first-time contributors / all outside collaborators, and never use `pull_request_target` with untrusted code checkout.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Setting up any new repo (do hardening on day 1)
- Automating via script/Terraform so all repos stay consistent

❌ Avoid when:
- Clicking randomly in UI for many repos; use org-level defaults or IaC (e.g., Terraform GitHub provider) instead

---

## 📊 Visual Diagram
```
 Repo Settings
 +-- General ........ merge methods, delete branch on merge
 +-- Access ......... teams, roles, outside collaborators
 +-- Branches/Rules . protect main (reviews, status checks)
 +-- Actions ........ token read-only, allowed actions
 +-- Secrets/Vars ... per repo / per environment
 +-- Code security .. Dependabot, secret scanning, CodeQL
 +-- Deploy keys .... read-only SSH key for VPS
 +-- Webhooks ....... notify external systems
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Default branch | Branch PRs target by default | डिफ़ॉल्ट branch |
| Deploy key | Repo-specific SSH key | repo की SSH key |
| GITHUB_TOKEN | Auto token for workflows | workflow का अपने-आप बना token |
| Push protection | Blocks secrets at push | push पर secret रोकना |
| Dependabot | Auto dependency updates/alerts | dependency अपडेट bot |
| Least privilege | Minimum needed access | न्यूनतम ज़रूरी access |

---

## ⚡ 3-Line Summary
English: Repo settings control access, merge rules, Actions permissions and security scanning.
Harden on day one: squash only, read-only token, Dependabot, push protection, deploy keys.
Automate with `gh api` so every repo has the same baseline.
Hindi: Repo settings access, merge rules, Actions permissions और security scanning तय करती हैं।
पहले दिन सख़्ती करो: सिर्फ squash, read-only token, Dependabot, push protection, deploy keys।
`gh api` से automate करो ताकि हर repo की baseline एक जैसी हो।

---

## ➡️ Next Topic
**33. Branch Protection Rules**: the most important setting, preventing direct pushes and requiring reviews and passing CI.

---
