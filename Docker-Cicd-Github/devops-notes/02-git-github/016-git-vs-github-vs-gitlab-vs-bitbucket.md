# 16. Git vs GitHub vs GitLab vs Bitbucket
# हिंदी में: Git बनाम GitHub बनाम GitLab बनाम Bitbucket

---

## 🔵 Simple Definition (English)
**Git** is a free, open-source distributed version control tool that runs on your machine and tracks changes in files. **GitHub, GitLab and Bitbucket** are hosting platforms that store Git repositories online and add collaboration features: pull/merge requests, issues, permissions and CI/CD. Git is the engine; the others are services built around it.

## 🔵 सरल परिभाषा (Hindi)
**Git** एक free, open-source distributed version control tool है जो आपकी machine पर चलता है और files के changes track करता है। **GitHub, GitLab और Bitbucket** hosting platforms हैं जो Git repositories को online रखते हैं और collaboration features देते हैं: pull/merge requests, issues, permissions और CI/CD। Git इंजन है; बाकी उसके ऊपर बनी services हैं।

---

## 🔴 Problem it Solves
Before Git, teams used central systems (SVN, CVS) or zip files on email. One server failure lost history, branching was painful, and offline work was impossible. Git made every clone a full backup with cheap branches. But Git alone does not give code review, access control, issue tracking or automated pipelines for a team. Hosting platforms fill that gap, so a team can review a PR, run tests, and deploy automatically.

## 🔴 यह क्यों बना? (Hindi)
Git से पहले teams central systems (SVN, CVS) या email पर zip files use करती थीं। Server fail होने पर history खो जाती, branching दर्दनाक थी, और offline काम असंभव। Git ने हर clone को full backup और branches को सस्ता बना दिया। पर सिर्फ Git team को code review, access control, issue tracking या automated pipelines नहीं देता। Hosting platforms यह gap भरते हैं ताकि team PR review कर सके, tests चला सके और automatically deploy कर सके।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developer runs `git init` / `git clone` : local repo with full history.
Step 2 → Work locally: `git add`, `git commit` (all offline).
Step 3 → `git push` sends commits to a remote hosted on GitHub/GitLab/Bitbucket.
Step 4 → Platform shows a Pull Request / Merge Request for review.
Step 5 → Platform CI (GitHub Actions / GitLab CI / Bitbucket Pipelines) runs tests.
Step 6 → Merge -> deploy pipeline ships to the VPS/AWS.
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Developer `git init` / `git clone` चलाता है: local repo, पूरी history के साथ।
Step 2 → Local काम: `git add`, `git commit` (सब offline)।
Step 3 → `git push` commits को GitHub/GitLab/Bitbucket के remote पर भेजता है।
Step 4 → Platform Pull Request / Merge Request दिखाता है review के लिए।
Step 5 → Platform की CI (GitHub Actions / GitLab CI / Bitbucket Pipelines) tests चलाती है।
Step 6 → Merge -> deploy pipeline VPS/AWS पर ship करती है।

---

## 🟡 Real World Example
A startup with a Node.js API, FastAPI ML service and React app hosts code on **GitHub** (huge ecosystem, GitHub Actions, Dependabot). A bank-like enterprise may self-host **GitLab** on its own servers for compliance, using built-in CI and container registry. A team already paying for Jira may choose **Bitbucket** for tight Jira linking. The Git commands they use are identical in all three.

## 🟡 Real Example Hindi mein
Node.js API, FastAPI ML service और React app वाला startup code **GitHub** पर रखता है (बड़ा ecosystem, GitHub Actions, Dependabot)। Bank जैसी enterprise compliance के लिए अपने servers पर **GitLab** self-host कर सकती है, built-in CI और container registry के साथ। Jira इस्तेमाल करने वाली team **Bitbucket** चुन सकती है क्योंकि Jira से tight linking है। तीनों में Git commands बिल्कुल एक जैसे हैं।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# git-basic.sh - same Git workflow works with any host
set -euo pipefail                                         # fail fast on errors

git config --global user.name  "Aditya Ranjan"            # name stored in every commit
git config --global user.email "aditya@example.com"       # email stored in every commit (use your real one)
git init demo-app                                         # create a new local repository
cd demo-app                                               # enter it
echo "console.log('hi')" > index.js                       # create a file
git add index.js                                          # stage the file
git commit -m "feat: first commit"                        # save snapshot locally
git branch -M main                                        # name the default branch "main"

# Add a remote: pick ONE host (URLs are examples, replace OWNER)
git remote add origin git@github.com:OWNER/demo-app.git   # GitHub
# git remote set-url origin git@gitlab.com:OWNER/demo-app.git      # GitLab
# git remote set-url origin git@bitbucket.org:OWNER/demo-app.git   # Bitbucket
git remote -v                                             # show configured remotes
# git push -u origin main                                 # uncomment when remote repo exists
```

## 💻 Code / Config Example — Advanced

The same "test on every PR" idea expressed in each platform's own CI syntax. Only the CI file differs; Git does not.

```yaml
# .github/workflows/ci.yml  (GitHub Actions)
name: ci                                   # workflow name
on:
  pull_request:                            # run on every PR
    branches: [main]                       # that targets main
jobs:
  test:
    runs-on: ubuntu-latest                 # GitHub-hosted Linux runner
    steps:
      - uses: actions/checkout@v4          # get the code (example version)
      - uses: actions/setup-node@v4        # install Node (example version)
        with:
          node-version: 20                 # Node major version
          cache: npm                       # cache ~/.npm between runs
      - run: npm ci                        # clean, reproducible install
      - run: npm test                      # run unit tests
```

```yaml
# .gitlab-ci.yml  (GitLab CI equivalent)
stages: [test]                             # list of pipeline stages
test:
  stage: test                              # job belongs to the test stage
  image: node:20-alpine                    # container the job runs in
  script:
    - npm ci                               # install dependencies
    - npm test                             # run tests
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"   # only for merge requests
```

```yaml
# bitbucket-pipelines.yml  (Bitbucket equivalent)
image: node:20-alpine                      # default build image
pipelines:
  pull-requests:
    '**':                                  # all branches with a PR
      - step:
          name: test                       # step label in the UI
          script:
            - npm ci                       # install dependencies
            - npm test                     # run tests
```

---

## 🟠 My Stack Integration
- **GitHub** is the best default for you: Actions to build Docker images, push to GHCR/ECR, SSH deploy to the VPS.
- **FastAPI/Node monorepo or polyrepo:** same hosting works for both; use path filters in Actions to deploy only the changed service.
- **Self-hosted option:** GitLab CE on an AWS EC2 box if code must stay in-house.
- **SSH deploy key:** create a read-only deploy key per repo for the VPS `git pull`.

```bash
# Create a dedicated, read-only deploy key for the VPS (run on the VPS)
ssh-keygen -t ed25519 -C "vps-deploy" -f ~/.ssh/deploy_key -N ""   # new keypair, no passphrase (automation)
cat ~/.ssh/deploy_key.pub                                          # paste in Repo > Settings > Deploy keys (read-only)
git -c core.sshCommand="ssh -i ~/.ssh/deploy_key" clone git@github.com:OWNER/app.git   # clone using that key
```

**Security:** enable 2FA, use SSH keys or fine-grained tokens, never commit secrets (enable GitHub secret scanning/push protection), protect `main` with branch rules.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Saying "Git and GitHub are the same thing".
✅ Correct: Git is the tool; GitHub is a hosting service for Git repos.

❌ Mistake 2: Committing `.env` or private keys because "the repo is private".
✅ Correct: Use `.gitignore` + secrets managers; rotate any leaked secret (deleting the commit is not enough).

❌ Mistake 3: Using a personal admin token in CI.
✅ Correct: Use `GITHUB_TOKEN` with minimal `permissions:` or a scoped deploy key.

---

## 🧠 Tricky Interview Question
If GitHub goes down, can your team still commit, branch and view history?

**Answer:** Yes for all local work, since Git is distributed and every clone has full history. What you lose is the platform features: PRs, Actions pipelines, issues. You could even push to another remote (GitLab mirror) as a fallback. This is exactly the Git vs GitHub difference.

---

## ⚫ Interview Questions + Answers

Q1: Git vs GitHub?
A1: Git is a local version control system; GitHub is a cloud platform hosting Git repos with collaboration and CI/CD.

Q2: GitHub vs GitLab main difference?
A2: GitLab is an all-in-one DevOps platform that is easily self-hosted with built-in CI, registry and security scans; GitHub has the largest community and marketplace, Actions for CI. Both now cover most features.

Q3: Why would a team pick Bitbucket?
A3: Deep Jira/Atlassian integration and Bitbucket Pipelines in an Atlassian-based workflow.

Q4: What does "distributed" mean in Git?
A4: Every clone contains the full history, so work is possible offline and any clone can act as a backup.

Q5: Can a repo have multiple remotes?
A5: Yes, e.g. `origin` on GitHub and `mirror` on GitLab; push to both with `git push mirror main`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- GitHub: open source, startups, Actions-heavy pipelines.
- GitLab: self-hosted, single-platform DevSecOps, compliance.
- Bitbucket: Jira-centric teams.

❌ Avoid when:
- Choosing a platform only by popularity without checking CI minutes, pricing, SSO and compliance needs.
- Locking all pipeline logic into one vendor's YAML with no portable scripts (keep logic in shell/Makefile).

---

## 📊 Visual Diagram

```
   Developer laptop                  Hosting platform
 +--------------------+  git push  +-----------------------+
 |  GIT (local)       | ---------> | GitHub / GitLab /     |
 |  - commits         | <--------- | Bitbucket             |
 |  - branches        |  git pull  | - Pull/Merge Requests |
 |  - full history    |            | - Issues, Permissions |
 +--------------------+            | - CI/CD pipelines     |
                                   +-----------+-----------+
                                               | deploy
                                               v
                                        VPS / AWS (Nginx)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Git | Distributed version control tool | distributed version control tool |
| Remote | Repo copy on a server | server पर repo की copy |
| Clone | Full copy of a repo | repo की पूरी copy |
| Pull Request | Request to merge changes | changes merge करने का अनुरोध |
| Merge Request | GitLab's name for PR | GitLab में PR का नाम |
| Deploy key | SSH key for one repo | एक repo के लिए SSH key |

---

## ⚡ 3-Line Summary
English: Git is the local version control tool; GitHub, GitLab, Bitbucket host repos online.
Hosts add pull requests, permissions, issues and CI/CD on top of Git.
Git commands are the same everywhere; only CI syntax differs.
Hindi: Git local version control tool है; GitHub, GitLab, Bitbucket repos को online host करते हैं।
Hosts Git के ऊपर pull requests, permissions, issues और CI/CD जोड़ते हैं।
Git commands हर जगह एक जैसे हैं; सिर्फ CI syntax अलग है।

---

## ➡️ Next Topic
**17. Git Branching Strategy** - how a team organises branches on top of these platforms.

---
