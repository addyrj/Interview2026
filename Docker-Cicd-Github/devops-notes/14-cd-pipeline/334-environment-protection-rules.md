# 334. Environment Protection Rules
# हिंदी में: Environment Protection Rules (environment की सुरक्षा नियम)

---

## 🔵 Simple Definition (English)
**Environment protection rules** are settings on a GitHub Environment that must pass before a job may use it: **required reviewers**, **wait timer**, **deployment branch/tag restrictions**, and **custom deployment protection rules** (GitHub Apps). Secrets and variables stored on the environment are released only after the rules pass.

## 🔵 सरल परिभाषा (Hindi)
**Environment protection rules** GitHub Environment की वे settings हैं जो job को उसे इस्तेमाल करने देने से पहले पास होनी चाहिए: **required reviewers**, **wait timer**, **deployment branch/tag restrictions**, और **custom deployment protection rules** (GitHub Apps)। Environment पर रखे secrets और variables नियम पास होने के बाद ही job को मिलते हैं।

---

## 🔴 Problem it Solves
Repository-level secrets are visible to any workflow on any branch. A contributor can open a PR that edits the workflow to `echo` the production SSH key, or a feature branch can deploy to production by mistake. Protection rules make production credentials usable only from `main`, only after approval, and optionally only after a cooling-off period.

## 🔴 यह क्यों बना? (Hindi)
Repository-level secrets किसी भी branch के किसी भी workflow को दिखते हैं। कोई contributor workflow बदलकर production SSH key `echo` करने वाला PR खोल सकता है, या feature branch गलती से production पर deploy कर सकती है। Protection rules production credentials को सिर्फ `main` से, सिर्फ approval के बाद और चाहें तो cooling-off अवधि के बाद इस्तेमाल योग्य बनाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Settings -> Environments -> production
Step 2 → Required reviewers: add people/teams (max 6), tick "Prevent self-review"
Step 3 → Wait timer: 0-43200 minutes (30 days max), e.g. 10 min cool-off for abort chance
Step 4 → Deployment branches and tags: "Selected branches" -> only main (and e.g. tags v*)
Step 5 → Environment secrets/variables: put PROD_HOST, PROD_SSH_KEY here (not repo-level)
Step 6 → Workflow job sets `environment: production`
Step 7 → GitHub checks: branch allowed? timer done? reviewers approved? -> then releases secrets
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Settings -> Environments -> production
Step 2 → Required reviewers: लोग/teams जोड़ो (अधिकतम 6), "Prevent self-review" टिक करो
Step 3 → Wait timer: 0-43200 मिनट (अधिकतम 30 दिन), जैसे 10 मिनट cooling-off ताकि रोकने का मौका मिले
Step 4 → Deployment branches and tags: "Selected branches" -> सिर्फ main (और जैसे tags v*)
Step 5 → Environment secrets/variables: PROD_HOST, PROD_SSH_KEY यहाँ रखो (repo-level नहीं)
Step 6 → Workflow job में `environment: production`
Step 7 → GitHub जाँचता है: branch allowed? timer पूरा? reviewers ने approve किया? -> तब secrets देता है
```

---

## 🟡 Real World Example
An e-commerce company hosts its API on AWS. Early on, `AWS_ACCESS_KEY_ID` was a repo secret. An intern's experimental branch had a workflow that ran `aws s3 ls` on the production account to "test something". After moving the keys to a `production` environment restricted to `main` with two required reviewers and a 5-minute wait timer, only reviewed code on `main` can ever touch production, and any branch run fails at "branch not allowed".

## 🟡 Real Example Hindi mein
एक e-commerce कंपनी का API AWS पर है। शुरू में `AWS_ACCESS_KEY_ID` repo secret थी। एक intern की experimental branch में ऐसा workflow था जो "कुछ test करने" के लिए production account पर `aws s3 ls` चलाता था। Keys को `production` environment में ले जाने के बाद, जो `main` तक सीमित है, दो required reviewers और 5 मिनट wait timer के साथ, सिर्फ `main` का reviewed code ही production छू सकता है और किसी भी दूसरी branch का run "branch not allowed" पर fail होता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/prod.yml  (workflow side: just reference the environment)
name: Prod Deploy                   # workflow name
on:                                 # triggers
  push:                             # push
    branches: [main]                # main only
jobs:                               # jobs
  deploy:                           # job id
    runs-on: ubuntu-latest          # runner
    environment: production         # rules from Settings -> Environments are enforced here
    steps:                          # steps
      - run: echo "Deploying to ${{ vars.PUBLIC_URL }}"  # `vars` = environment variables (non-secret)
      - run: ./deploy.sh            # deploy script (placeholder)
        env:                        # env
          SSH_KEY: ${{ secrets.PROD_SSH_KEY }}  # secret available only after rules pass
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# setup-environment.sh  (configure protection rules with the gh CLI instead of clicking)
# Requires: gh auth login with repo admin rights. OWNER/REPO, user id and team id are placeholders.
set -euo pipefail                                          # strict shell mode

REPO="OWNER/REPO"                                          # your repository
ENV_NAME="production"                                      # environment to configure

# Look up numeric ids (reviewers must be given by id)
USER_ID=$(gh api users/YOUR_GITHUB_LOGIN --jq .id)        # id of a reviewer user

# 1) Create/update the environment with reviewers, wait timer and self-review prevention
gh api -X PUT "repos/$REPO/environments/$ENV_NAME" \
  --input - <<JSON
{
  "wait_timer": 5,
  "prevent_self_review": true,
  "reviewers": [ { "type": "User", "id": $USER_ID } ],
  "deployment_branch_policy": { "protected_branches": false, "custom_branch_policies": true }
}
JSON

# 2) Allow deployments only from main (custom branch policy)
gh api -X POST "repos/$REPO/environments/$ENV_NAME/deployment-branch-policies" \
  -f name=main                                             # only the branch named main may deploy

# 3) Store environment-scoped secret and variable (values read from stdin / args)
gh secret set PROD_SSH_KEY --env "$ENV_NAME" --repo "$REPO" < ~/.ssh/prod_deploy_key   # private key file
gh variable set PUBLIC_URL --env "$ENV_NAME" --repo "$REPO" --body "https://app.example.com"  # example URL
echo "environment $ENV_NAME configured"                    # done
```

```yaml
# .github/workflows/prod.yml  (advanced workflow using the environment safely)
name: Prod Deploy                   # workflow name
on:                                 # triggers
  push:                             # push
    branches: [main]                # main
concurrency:                        # one prod deploy at a time
  group: prod                       # lane
  cancel-in-progress: false         # queue
permissions:                        # least privilege
  contents: read                    # read only
jobs:                               # jobs
  deploy:                           # job
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 10             # cap
    environment:                    # environment with URL
      name: production              # must match the environment name exactly
      url: ${{ vars.PUBLIC_URL }}   # URL from environment variable shown in UI
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - name: Deploy                # step
        env:                        # env
          HOST: ${{ vars.PROD_HOST }}          # non-secret host from environment variables
          SSH_KEY: ${{ secrets.PROD_SSH_KEY }} # environment secret
        run: |                      # shell
          install -m 600 /dev/null key && printf '%s\n' "$SSH_KEY" > key  # key with 600 perms
          ssh -i key -o StrictHostKeyChecking=accept-new deploy@"$HOST" 'bash /srv/app/deploy.sh'  # run server script
```

---

## 🟠 My Stack Integration
For a VPS fronted by Nginx, use two environments with identical secret NAMES but different values (`HOST`, `SSH_KEY`). Workflow code stays the same; the environment decides the target. Restrict `production` to `main` and tags `v*`, add a teammate as reviewer, and keep the VPS firewall allowing SSH only from your needs (GitHub runner IP ranges change; prefer key-only auth and `fail2ban`).

```yaml
# Excerpt: same job, environment chosen by branch (names must exist in repo settings)
jobs:                               # jobs
  deploy:                           # job
    runs-on: ubuntu-latest          # runner
    environment: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}  # expression picks env
    steps:                          # steps
      - run: echo "target host is hidden, env is ${{ github.ref_name }}"  # secrets stay masked in logs
```

Security: never use pull_request_target to run untrusted code with environment secrets; do not print secrets; rotate keys when a reviewer leaves.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Storing production secrets at repository level while environments exist.
✅ Correct: Move them into the environment so the protection rules apply.

❌ Mistake 2: Leaving "All branches" allowed, so any branch run can request production.
✅ Correct: Restrict deployment branches to `main` (and release tags).

❌ Mistake 3: Same person triggers and approves their own release.
✅ Correct: Enable "Prevent self-review" and have two eligible reviewers.

❌ Mistake 4: Typos in `environment: Production` vs `production` creating a new unprotected environment automatically.
✅ Correct: Use the exact name; an unknown name creates a new environment with no rules.

---

## 🧠 Tricky Interview Question
**Q:** You restricted the `production` environment to the `main` branch. A release tag `v1.4.0` workflow run now fails with "branch not allowed". Why?

Answer: The deployment branch policy matches only branch refs named in the policy. A run triggered by a tag push has `github.ref` of `refs/tags/v1.4.0`, which is not `main`. Add a custom policy of type tag (pattern `v*`) in "Deployment branches and tags". The trap is thinking tags count as the branch they point to.

---

## ⚫ Interview Questions + Answers

Q1: Name the protection rules available for environments.
A1: Required reviewers, wait timer, deployment branches and tags restrictions, and custom deployment protection rules via GitHub Apps. (Administrators can optionally be allowed to bypass.)

Q2: What is the difference between `secrets.X` at repo level and at environment level?
A2: Environment secrets are released only to jobs that reference the environment and pass its rules; repo secrets are available to any job in the repository (subject to fork rules).

Q3: What is the wait timer for?
A3: A forced delay (up to 30 days) before the job starts, giving time to abort a bad release or wait for a change window.

Q4: How do environment variables (`vars`) differ from secrets?
A4: `vars` are plain, visible configuration (URLs, region); secrets are encrypted and masked in logs.

Q5: Are these features available for private repos on free plans?
A5: Environment protection rules are generally limited on private repos for free plans (need Pro, Team or Enterprise); public repos have them. Check current GitHub documentation for your plan.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Production credentials exist (SSH keys, cloud keys, DB passwords).
- Multiple engineers/forks can open PRs.

❌ Avoid when:
- A solo hobby repo where rules only slow you down (but still scope secrets to an environment).
- Do not rely on rules alone; also use branch protection and least-privilege credentials.

---

## 📊 Visual Diagram
```
 workflow job: environment: production
              |
              v
   +-----------------------------+
   | branch/tag allowed?  (main) |--no--> job FAILS
   +--------------+--------------+
                  | yes
   +--------------v--------------+
   | wait timer elapsed? (5 min) |
   +--------------+--------------+
                  | yes
   +--------------v--------------+
   | reviewers approved?         |--reject--> job FAILS
   +--------------+--------------+
                  | yes
                  v
      secrets + vars released -> deploy runs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Environment | Named deployment target with rules | rules वाला नामित target |
| Wait timer | Mandatory delay | अनिवार्य विलंब |
| Deployment branch policy | Allowed refs for the environment | environment के लिए अनुमत refs |
| Environment secret | Secret released after rules pass | rules पास होने पर मिलने वाला secret |
| `vars` | Non-secret configuration variables | गैर-गोपनीय config variables |

---

## ⚡ 3-Line Summary
English: Protection rules gate an environment with reviewers, timers and branch limits.
English: Put production secrets in the environment so they unlock only after the rules pass.
English: Restrict to main/tags, prevent self-review and use exact environment names.

Hindi: Protection rules environment को reviewers, timers और branch limits से सुरक्षित करते हैं।
Hindi: Production secrets environment में रखो ताकि नियम पास होने पर ही खुलें।
Hindi: main/tags तक सीमित करो, self-review रोको और environment के सटीक नाम इस्तेमाल करो।

---

## ➡️ Next Topic
**335. Deployment Environments (dev, staging, production)** — how to design the three environments themselves.
