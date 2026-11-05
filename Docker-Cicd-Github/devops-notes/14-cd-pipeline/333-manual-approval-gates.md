# 333. Manual Approval Gates
# हिंदी में: Manual Approval Gates (इंसान की मंज़ूरी)

---

## 🔵 Simple Definition (English)
A **manual approval gate** pauses a deployment until a designated person approves it. In GitHub Actions you create it with an **environment** that has **Required reviewers**; any job that says `environment: production` waits until a reviewer approves in the UI (or via API).

## 🔵 सरल परिभाषा (Hindi)
**Manual approval gate** deployment को तब तक रोकता है जब तक कोई तय व्यक्ति मंज़ूरी न दे। GitHub Actions में इसे **environment** और उसके **Required reviewers** से बनाते हैं; जो job `environment: production` लिखता है वह UI (या API) में reviewer के approve करने तक इंतज़ार करता है।

---

## 🔴 Problem it Solves
Full automation is risky for some releases: payment changes, database migrations, releases during peak sale hours. Teams need a human checkpoint ("is marketing ready? is the on-call aware?") and an audit trail of who approved what and when, without leaving the pipeline and deploying by hand.

## 🔴 यह क्यों बना? (Hindi)
कुछ releases के लिए पूरा automation जोखिम भरा है: payment बदलाव, database migrations, peak sale के समय releases। टीमों को इंसानी checkpoint ("marketing तैयार है? on-call को पता है?") और audit trail चाहिए कि किसने कब क्या approve किया, बिना pipeline छोड़े और बिना हाथ से deploy किए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Settings -> Environments -> New environment "production"
Step 2 → Enable "Required reviewers", add up to 6 people or teams
Step 3 → Optionally tick "Prevent self-review" and set a wait timer
Step 4 → In the workflow, the deploy job declares `environment: production`
Step 5 → When it is reached, the run shows "Waiting for review"; reviewers get a notification
Step 6 → A reviewer opens the run, reviews the commit, and clicks Approve and deploy (or Reject)
Step 7 → Job continues with the environment's secrets; approval is recorded in the deployment history
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Settings -> Environments -> New environment "production"
Step 2 → "Required reviewers" चालू करो, 6 लोगों या teams तक जोड़ो
Step 3 → चाहो तो "Prevent self-review" टिक करो और wait timer रखो
Step 4 → Workflow में deploy job `environment: production` घोषित करता है
Step 5 → जब वह job आता है, run "Waiting for review" दिखाता है; reviewers को notification जाती है
Step 6 → Reviewer run खोलकर commit देखता है और Approve and deploy (या Reject) दबाता है
Step 7 → Job environment के secrets के साथ आगे बढ़ता है; मंज़ूरी deployment history में दर्ज होती है
```

---

## 🟡 Real World Example
A fintech lending app deploys the API and a schema migration. Staging deploys automatically on merge. The production job waits for either the tech lead or the on-call SRE. During a festival sale the SRE rejected a release because the traffic dashboard showed a spike, and approved it two hours later. The run history shows who approved and when, which satisfied the company's audit requirement.

## 🟡 Real Example Hindi mein
एक fintech lending app API और schema migration deploy करता है। Staging merge पर अपने आप deploy होता है। Production job tech lead या on-call SRE का इंतज़ार करता है। त्योहार की sale के दौरान SRE ने traffic dashboard में spike देखकर release reject कर दी और दो घंटे बाद approve की। Run history में दिखता है किसने कब approve किया, जिससे कंपनी की audit ज़रूरत पूरी हुई।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/release.yml  (basic approval gate)
name: Release                       # workflow name
on:                                 # triggers
  push:                             # push
    branches: [main]                # main
jobs:                               # jobs
  deploy-production:                # job that needs approval
    runs-on: ubuntu-latest          # runner
    environment: production         # environment with Required reviewers -> job pauses here
    steps:                          # steps
      - run: echo "Approved by a human, deploying ${{ github.sha }}"  # runs only after approval
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/release.yml  (staging auto, production gated, rollback-friendly)
name: Release                       # workflow name
on:                                 # triggers
  push:                             # push
    branches: [main]                # main
  workflow_dispatch:                # manual trigger
    inputs:                         # inputs
      tag:                          # image tag to deploy
        description: 'Image tag (blank = this commit)'  # help
        required: false             # optional
concurrency:                        # serialize
  group: release-prod               # lane
  cancel-in-progress: false         # queue
permissions:                        # least privilege
  contents: read                    # read repo
jobs:                               # jobs
  staging:                          # automatic stage
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 10             # cap
    environment: staging            # no reviewers configured here
    outputs:                        # share tag
      tag: ${{ steps.t.outputs.tag }}  # chosen tag
    steps:                          # steps
      - id: t                       # step id
        run: echo "tag=${{ inputs.tag || github.sha }}" >> "$GITHUB_OUTPUT"  # use given tag or commit SHA
      - uses: actions/checkout@v4   # checkout
      - run: ./deploy/deploy.sh staging ${{ steps.t.outputs.tag }}  # deploy script from repo
        env:                        # env
          HOST: ${{ secrets.HOST }}        # staging host (environment secret)
          SSH_KEY: ${{ secrets.SSH_KEY }}  # staging key (environment secret)
  production:                       # gated stage
    needs: staging                  # only after staging success
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 10             # cap (approval wait time does NOT count toward the job runtime)
    environment:                    # production environment
      name: production              # name; reviewers + timer configured in repo settings
      url: https://app.example.com  # link in the UI (example URL)
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - name: Summary for the approver  # context for later audits
        run: |                      # shell
          {
            echo "### Production deploy"                       # heading
            echo "- tag: ${{ needs.staging.outputs.tag }}"     # what ships
            echo "- triggered by: ${{ github.actor }}"         # who started
          } >> "$GITHUB_STEP_SUMMARY"                          # write to run summary
      - run: ./deploy/deploy.sh production ${{ needs.staging.outputs.tag }}  # deploy
        env:                        # env
          HOST: ${{ secrets.HOST }}        # production host (different secret value)
          SSH_KEY: ${{ secrets.SSH_KEY }}  # production key
```

---

## 🟠 My Stack Integration
For your VPS, create environments `staging` and `production`, each with its own `HOST` and `SSH_KEY` secrets. Only the `production` environment gets reviewers (you plus a teammate), restricted to the `main` branch. The approval also protects the Nginx/Docker host: a leaked workflow change on a feature branch cannot reach production secrets.

```bash
# Optional: approve from the terminal with gh API (needs pending deployment id)
# 1) find the run
gh run list --workflow release.yml --limit 1                                  # latest run id
# 2) list pending deployment environments for that run
gh api repos/OWNER/REPO/actions/runs/RUN_ID/pending_deployments               # shows environment ids
# 3) approve (replace ids); comment is stored in audit history
gh api -X POST repos/OWNER/REPO/actions/runs/RUN_ID/pending_deployments \
  -F 'environment_ids[]=ENV_ID' -f state=approved -f comment='Checked dashboards'  # OWNER/REPO/RUN_ID/ENV_ID are placeholders
```

Security: enable "Prevent self-review" so the author cannot approve their own release; limit deployment branches; keep reviewer lists in a team, not individuals.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Adding reviewers but forgetting `environment: production` in the job, so nothing pauses.
✅ Correct: The job must reference the environment by exact name.

❌ Mistake 2: Using required reviewers on a private-plan-limited repo and finding the feature is missing.
✅ Correct: Check plan limits: environment protection rules are available for public repos on all plans and for private repos on paid plans (Pro/Team/Enterprise). Verify on current GitHub docs.

❌ Mistake 3: Approvers rubber-stamp without looking.
✅ Correct: Put the commit list, tag and staging result in `$GITHUB_STEP_SUMMARY`.

❌ Mistake 4: Letting approvals wait forever, so stale releases deploy days later.
✅ Correct: Re-run or redeploy the latest tag; unapproved runs time out after 30 days anyway, so cancel old ones.

---

## 🧠 Tricky Interview Question
**Q:** The approval takes 6 hours. Does the job's `timeout-minutes: 10` fail the run, and are runner minutes billed while waiting?

Answer: No on both. While waiting for approval the job has not started on a runner, so it uses no runner minutes and the job timeout clock starts only after approval. The pending run itself expires if not approved within 30 days. The trap is concurrency: a waiting run still holds the concurrency group, so with `cancel-in-progress: false` later runs queue behind it (only one pending is kept; older pending ones may be cancelled).

---

## ⚫ Interview Questions + Answers

Q1: How do you require approval before production deploy?
A1: Create an environment with Required reviewers and reference it with `environment:` in the deploy job.

Q2: Who can approve?
A2: Users or teams you list (up to 6), who must have access to the repo; with "Prevent self-review" the user who triggered the run cannot approve.

Q3: Are environment secrets available before approval?
A3: No. Secrets of a protected environment are released to the job only after the protection rules pass.

Q4: Approval vs branch protection?
A4: Branch protection controls what merges into a branch; environment approval controls whether a specific deployment runs.

Q5: Can approval be automated?
A5: You can use deployment protection rule apps (custom rules via GitHub Apps) to approve based on external checks like change tickets or monitoring status.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Production deploys with compliance, financial or user-data impact.
- Releases need business sign-off or timing windows.

❌ Avoid when:
- Staging/dev environments (slows the team).
- A one-person project (approval adds friction without a second pair of eyes).

---

## 📊 Visual Diagram
```
 staging deploy OK
        |
        v
 +--------------------------+
 | production job reached   |
 | status: WAITING          |  <- no runner used, secrets locked
 +------------+-------------+
              |
   notify reviewers (email / UI)
              |
      +-------+--------+
      |                |
  Approve           Reject
      |                |
      v                v
 job starts,        run fails,
 secrets released   nothing deployed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Approval gate | Human checkpoint | इंसानी checkpoint |
| Required reviewers | People who must approve | जिन्हें approve करना है |
| Prevent self-review | Author cannot approve | लेखक खुद approve नहीं कर सकता |
| Environment secret | Secret scoped to an environment | environment तक सीमित secret |
| Audit trail | Record of who did what | किसने क्या किया उसका record |

---

## ⚡ 3-Line Summary
English: Environment + Required reviewers pauses the job until a person approves.
English: Secrets stay locked and no runner minutes are used while waiting.
English: Enable self-review prevention and add context to the run summary.

Hindi: Environment + Required reviewers job को तब तक रोकता है जब तक कोई व्यक्ति approve न करे।
Hindi: इंतज़ार के दौरान secrets locked रहते हैं और runner minutes खर्च नहीं होते।
Hindi: Self-review रोकना चालू करो और run summary में context जोड़ो।

---

## ➡️ Next Topic
**334. Environment Protection Rules** — the other rules beyond reviewers: wait timers, branch limits and custom checks.
