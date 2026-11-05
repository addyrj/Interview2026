---

# 35. GitHub Environments
# हिंदी में: GitHub Environments (staging / production जैसे वातावरण)

---

## 🔵 Simple Definition (English)
A **GitHub Environment** is a named deployment target (like `staging` or `production`) attached to a repo. It can have its own secrets and variables, required reviewers (manual approval), a wait timer, and rules about which branches may deploy to it. A job opts in with `environment: production`.

## 🔵 सरल परिभाषा (Hindi)
**GitHub Environment** repo से जुड़ा एक नाम वाला deployment target है (जैसे `staging` या `production`)। इसके अपने secrets और variables, required reviewers (manual approval), wait timer और यह नियम हो सकते हैं कि कौन सी branches इसमें deploy कर सकती हैं। Job `environment: production` लिखकर इसमें शामिल होता है।

---

## 🔴 Problem it Solves
With only repo-level secrets, a staging job and a production job can both read the production database password, and any merged commit deploys to production instantly. You cannot ask "a human must click approve before prod" or keep different server IPs per stage. Environments add per-stage secrets, gates and an audit trail of deployments.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ repo-level secrets हों तो staging और production दोनों jobs production database password पढ़ सकते हैं, और हर merged commit तुरंत production में चला जाता है। "prod से पहले इंसान approve करे" या हर stage के अलग server IP रखना संभव नहीं होता। Environments हर stage के secrets, gates और deployment का audit trail जोड़ते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Repo → Settings → Environments → New environment: "staging", "production"
Step 2 → production: add Required reviewers (1-6 users/teams), optional Wait timer
Step 3 → production: Deployment branches and tags -> "Selected branches" -> main only
Step 4 → Add environment secrets (e.g. VPS_HOST, SSH_KEY) and variables (e.g. APP_URL) per environment
Step 5 → Workflow job sets:  environment: production
Step 6 → When job starts: branch rule checked -> job PAUSES waiting for approval
Step 7 → Reviewer clicks Approve -> job runs; environment secrets become available ONLY now
Step 8 → Deployment recorded (Environments tab / "Deployments" in repo sidebar), URL shown
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Repo → Settings → Environments → New environment: "staging", "production"
Step 2 → production: Required reviewers जोड़ो (1-6 users/teams), चाहें तो Wait timer
Step 3 → production: Deployment branches -> "Selected branches" -> सिर्फ main
Step 4 → हर environment के अपने secrets (VPS_HOST, SSH_KEY) और variables (APP_URL) जोड़ो
Step 5 → Workflow job में लिखो:  environment: production
Step 6 → Job शुरू होने पर branch rule जाँचा जाता है -> job approval के लिए RUKTA है
Step 7 → Reviewer Approve करता है -> job चलता है; environment secrets सिर्फ अब मिलते हैं
Step 8 → Deployment दर्ज होता है (Environments tab), URL दिखता है
```

---

## 🟡 Real World Example
A food-delivery backend (FastAPI + React) deploys on every merge to `main` to **staging** automatically (QA team tests). After QA signs off, the same workflow waits at **production** for approval by the tech lead. Production has its own `SSH_KEY` and `DB_URL`; developers who can edit workflows still cannot read these secrets unless the approved job runs from `main`. Result: no accidental prod deploys, and the deployment history shows who approved which release.

## 🟡 Real Example Hindi mein
Food-delivery backend (FastAPI + React) हर `main` merge पर **staging** में अपने-आप deploy होता है (QA test करती है)। QA की मंज़ूरी के बाद वही workflow **production** पर tech lead के approval के लिए रुकता है। Production के अपने `SSH_KEY` और `DB_URL` हैं; workflow edit कर सकने वाले developers भी ये secrets नहीं पढ़ सकते जब तक approved job `main` से न चले। नतीजा: कोई ग़लती से prod deploy नहीं, और deployment history में दिखता है किसने कौन सा release approve किया।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/deploy-basic.yml
# Prereq: create environment "production" in Settings -> Environments and add secrets there.
name: Deploy basic                          # workflow name
on:
  push:
    branches: [main]                        # run after a merge to main
jobs:
  deploy:                                   # job id
    runs-on: ubuntu-latest                  # hosted runner
    environment: production                 # links the job to the environment (approval + its secrets)
    steps:
      - uses: actions/checkout@v4           # get code (example version)
      - name: Show which environment secret is visible   # step label
        run: echo "Deploying to ${{ vars.APP_URL }}"     # environment VARIABLE (not secret) is printable
      - name: Deploy over SSH                # step label
        env:
          HOST: ${{ secrets.VPS_HOST }}      # environment secret, only available in this job
        run: echo "would ssh to $HOST here"  # placeholder command; real deploy in advanced example
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/deploy.yml - staging automatically, production after manual approval
name: Deploy                                # workflow name
on:
  push:
    branches: [main]                        # trigger on main only
concurrency:
  group: deploy-${{ github.ref }}           # one deploy at a time per branch
  cancel-in-progress: false                 # never cancel a deploy halfway
permissions:
  contents: read                            # least privilege token
jobs:
  test:                                     # job 1: verify before any deploy
    runs-on: ubuntu-latest                  # hosted runner
    steps:
      - uses: actions/checkout@v4           # code
      - uses: actions/setup-node@v4         # Node
        with:
          node-version: 20                  # example LTS
          cache: npm                        # cache
      - run: npm ci && npm test             # install + test
  deploy-staging:                           # job 2: automatic staging deploy
    needs: test                             # only if tests passed
    runs-on: ubuntu-latest                  # hosted runner
    environment:
      name: staging                         # environment name
      url: https://staging.example.com      # shown on the deployment (example URL)
    steps:
      - name: Deploy to staging VPS         # label
        uses: appleboy/ssh-action@v1.0.3    # third-party SSH action, example version, pin SHA in prod
        with:
          host: ${{ secrets.VPS_HOST }}     # staging secret
          username: ${{ secrets.VPS_USER }} # staging secret
          key: ${{ secrets.VPS_SSH_KEY }}   # staging secret (different value from prod)
          script: |                         # commands executed on server
            cd /srv/app && git pull origin main
            docker compose up -d --build
  deploy-production:                        # job 3: waits for approval
    needs: deploy-staging                   # staging must succeed first
    runs-on: ubuntu-latest                  # hosted runner
    environment:
      name: production                      # required reviewers configured in UI pause the job here
      url: https://app.example.com          # example URL
    steps:
      - name: Deploy to production VPS      # label
        uses: appleboy/ssh-action@v1.0.3    # same action, example version
        with:
          host: ${{ secrets.VPS_HOST }}     # production value of the secret (same name, different environment)
          username: ${{ secrets.VPS_USER }} # production value
          key: ${{ secrets.VPS_SSH_KEY }}   # production value
          script: |                         # commands executed on server
            cd /srv/app && git pull origin main
            docker compose up -d --build
```
Secrets with the same name in different environments resolve to that environment's value. Approval rules are configured in the UI/API, not in YAML. Not executed against real servers here.

---

## 🟠 My Stack Integration
Use two environments for your VPS/EC2: `staging` (auto) and `production` (approval). Store `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` per environment; store non-secret `APP_URL`, `NODE_ENV` as environment variables. You can also create environments via API:

```yaml
# .github/workflows/health-check.yml - post-deploy smoke test using environment variables
name: Health check                          # workflow name
on:
  workflow_dispatch:                        # run manually from Actions tab
jobs:
  check:                                    # job id
    runs-on: ubuntu-latest                  # hosted runner
    environment: production                 # read production variables (may require approval)
    steps:
      - name: Curl the health endpoint      # label
        run: curl --fail --silent --show-error "${{ vars.APP_URL }}/health"   # fails job on non-2xx
```
Security: restrict `production` to branch `main`, add required reviewers (and enable "Prevent self-review"), and use environment secrets instead of repo secrets for anything production. For AWS, prefer OIDC role assumption with the environment in the trust condition rather than long-lived keys.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting production secrets at repo level, available to every workflow and branch.
✅ Correct: Store them as environment secrets guarded by approvals and branch rules.

❌ Mistake 2: Forgetting `environment:` in the job, so approvals and env secrets never apply.
✅ Correct: Every deploy job declares `environment: <name>`.

❌ Mistake 3: Required reviewers include the person who triggers the deploy and "prevent self-review" is off.
✅ Correct: Enable "Prevent self-review" and use a team of 2+.

❌ Mistake 4: Assuming Environments are available on private repos in every plan.
✅ Correct: Check plan limits; on free private repos some protection features need a paid plan.

---

## 🧠 Tricky Interview Question
A workflow job uses `secrets.DB_URL` and `environment: production`. The same secret also exists at repo level with a different value. Which value does the job get, and what happens if the approver rejects?

Answer: The environment secret overrides the repository secret of the same name, so the job gets the production value. If the reviewer rejects, the job fails and never starts, and the secret is never exposed to the runner. Secrets from the environment are only released after the protection rules pass.

---

## ⚫ Interview Questions + Answers

Q1: What can an environment protect?
A1: Required reviewers, wait timer, deployment branch/tag restrictions, and custom protection rules; plus environment-scoped secrets and variables.

Q2: Environment secrets vs repository secrets?
A2: Repo secrets are available to all workflows in the repo. Environment secrets are available only to jobs referencing that environment, after protection rules pass; same-name environment secrets override.

Q3: How do you pause a pipeline for manual approval?
A3: Use an environment with required reviewers; the job waits in "Waiting for review".

Q4: Can environment names be dynamic?
A4: Yes: `environment: ${{ github.ref_name == 'main' && 'production' || 'staging' }}`.

Q5: What is the `url` field for?
A5: It shows a link to the deployed app on the workflow run and Deployments page; it does not affect behavior.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple stages (dev, staging, prod) with different secrets
- You need manual approval or audit of production deploys

❌ Avoid when:
- A single throwaway app with one server where approvals add no value
- You need approvals on a plan/repo type that does not support them (use a manual `workflow_dispatch` instead)

---

## 📊 Visual Diagram
```
 push to main
     |
  [test] --pass--> [deploy-staging]  env: staging (secrets: STAGING_*)
                          |
                          v
                [deploy-production]  env: production
                          |
                +---------+---------+
                | branch rule: main |
                | WAIT: reviewer    |<-- human clicks Approve
                +---------+---------+
                          v
              production secrets released -> deploy runs -> URL recorded
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Environment | Named deployment target | deployment वातावरण |
| Required reviewers | People who must approve a job | अनिवार्य approvers |
| Wait timer | Delay before job starts | रुकने का समय |
| Environment secret | Secret scoped to one environment | environment का secret |
| Deployment branches | Branches allowed to deploy | deploy की अनुमति वाली branches |
| Deployment protection rule | Gate before a job runs | job से पहले की रोक |

---

## ⚡ 3-Line Summary
English: Environments give each stage its own secrets, approval gates and branch rules.
Jobs opt in with `environment:`; secrets are released only after protections pass.
Use staging auto-deploy and production with required reviewers.
Hindi: Environments हर stage को अपने secrets, approval gates और branch rules देते हैं।
Jobs `environment:` से जुड़ते हैं; protections पास होने के बाद ही secrets मिलते हैं।
Staging auto-deploy और production required reviewers के साथ रखो।

---

## ➡️ Next Topic
**36. GitHub Secrets**: how encrypted secrets are stored, used safely in workflows, and what leaks to avoid.

---
