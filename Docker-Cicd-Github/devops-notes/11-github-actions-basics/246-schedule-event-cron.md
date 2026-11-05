# 246. schedule Event (cron)
# हिंदी में: schedule Event (cron से समय पर workflow)

---

## 🔵 Simple Definition (English)
The `schedule` event runs a workflow at fixed times using POSIX **cron** syntax (five fields: minute hour day-of-month month day-of-week). All times are in **UTC**. Scheduled workflows run only from the **default branch** and can be delayed during busy periods; the shortest interval is every 5 minutes.

## 🔵 सरल परिभाषा (Hindi)
`schedule` event POSIX **cron** syntax (पाँच fields: minute hour day-of-month month day-of-week) से तय समय पर workflow चलाता है। सारे समय **UTC** में होते हैं। Scheduled workflow सिर्फ़ **default branch** से चलता है, busy समय में देर हो सकती है, और सबसे छोटा अंतराल 5 मिनट है।

---

## 🔴 Problem it Solves
Teams used to keep a "cron box" (a VPS with crontab or Jenkins) for nightly jobs: dependency audits, DB backups, stale-image cleanup, smoke tests of production. That box itself needed patching and monitoring. `schedule` moves these jobs next to the code, versioned in Git, with logs, retries (re-run) and secrets management, without any extra server.

## 🔴 यह क्यों बना? (Hindi)
पहले nightly jobs (dependency audit, DB backup, पुरानी images की सफ़ाई, production smoke test) के लिए "cron box" रखना पड़ता था - crontab वाला VPS या Jenkins। उस box को भी patch और monitor करना पड़ता था। `schedule` इन jobs को code के पास ले आता है: Git में version, logs, re-run और secrets management के साथ, बिना किसी अतिरिक्त server के।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You add `on: schedule: - cron: "30 20 * * *"` to a workflow on the DEFAULT branch.
Step 2 → GitHub's scheduler evaluates cron expressions in UTC.
Step 3 → At/near the time it queues a run with github.event_name == "schedule".
Step 4 → Runner starts, checks out the default branch latest commit (github.ref = refs/heads/main).
Step 5 → Jobs run like any workflow; logs and status appear in Actions tab.
Step 6 → If the repo is inactive for 60 days (public repos), GitHub auto-disables scheduled workflows.
Step 7 → Runs can be delayed (minutes) under high load; never rely on exact-second timing.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Default branch पर workflow में `on: schedule: - cron: "30 20 * * *"` जोड़ें।
Step 2 → GitHub का scheduler cron expressions को UTC में पढ़ता है।
Step 3 → उस समय के आसपास github.event_name == "schedule" वाला run queue होता है।
Step 4 → Runner शुरू होकर default branch का latest commit checkout करता है (github.ref = refs/heads/main)।
Step 5 → Jobs सामान्य workflow की तरह चलते हैं; logs और status Actions tab में दिखते हैं।
Step 6 → Public repo 60 दिन निष्क्रिय रहे तो GitHub scheduled workflows अपने-आप disable कर देता है।
Step 7 → Load ज़्यादा हो तो run में कुछ मिनट की देरी हो सकती है; सेकंड-सटीक समय पर भरोसा न करें।
```

Cron cheat sheet: `*/15 * * * *` every 15 min; `0 2 * * *` daily 02:00 UTC; `0 9 * * 1-5` weekdays 09:00 UTC; `0 0 1 * *` first of month. IST = UTC + 5:30, so 02:00 IST = `30 20 * * *` (previous day UTC).

---

## 🟡 Real World Example
An e-commerce startup runs a nightly workflow at 02:00 IST: it executes `npm audit`, runs an end-to-end smoke test against the staging URL, deletes untagged images from ECR older than 14 days, and posts a Slack message if anything fails. On Sundays another schedule rebuilds the base Docker image to pick up OS security patches, then opens a PR with the new digest.

## 🟡 Real Example Hindi mein
एक e-commerce startup रोज़ रात 02:00 IST पर workflow चलाती है: `npm audit`, staging URL पर end-to-end smoke test, ECR से 14 दिन पुरानी untagged images हटाना, और कुछ fail हो तो Slack संदेश। रविवार को दूसरा schedule base Docker image दोबारा बनाता है ताकि OS security patches आएँ, फिर नई digest के साथ PR खोलता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/nightly-audit.yml
name: Nightly Audit                       # workflow name

on:                                       # triggers
  schedule:                               # time-based trigger
    - cron: "30 20 * * *"                 # 20:30 UTC daily = 02:00 IST next day (quote it: YAML treats * specially)

jobs:
  audit:                                  # job id
    runs-on: ubuntu-latest                # hosted Linux runner
    steps:
      - uses: actions/checkout@v4         # get the default branch code (example version)
      - uses: actions/setup-node@v4       # install Node.js
        with:
          node-version: 20                # LTS used by the project
      - run: npm ci                       # reproducible install
      - run: npm audit --audit-level=high # fail only on high/critical vulnerabilities
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/scheduled-maintenance.yml
name: Scheduled Maintenance

on:
  schedule:                               # several schedules allowed in one workflow
    - cron: "30 20 * * *"                 # nightly 02:00 IST
    - cron: "0 3 * * 0"                   # weekly Sunday 03:00 UTC
  workflow_dispatch:                      # also allow manual run for testing (scheduled runs cannot be tested otherwise)

permissions:
  contents: read                          # default least privilege

concurrency:
  group: scheduled-maintenance            # only one maintenance run at a time
  cancel-in-progress: false               # let a running job finish rather than cancel it

jobs:
  nightly:
    # github.event.schedule holds the cron string that triggered this run
    if: github.event_name == 'workflow_dispatch' || github.event.schedule == '30 20 * * *'
    runs-on: ubuntu-latest
    timeout-minutes: 20                   # never let a stuck cron job burn minutes
    steps:
      - uses: actions/checkout@v4
      - name: Smoke test staging          # health check of the deployed staging app
        run: |                            # multi-line shell
          set -euo pipefail               # stop on error, unset var, or pipe failure
          code=$(curl -s -o /dev/null -w '%{http_code}' https://staging.example.com/health)  # get HTTP status
          echo "status=$code"             # log result
          test "$code" = "200"            # non-200 fails the job
      - name: Notify on failure           # alert humans
        if: failure()                     # run only when a previous step failed
        run: |
          curl -sS -X POST -H 'Content-type: application/json' \
            --data '{"text":"Nightly smoke test FAILED"}' "$SLACK_WEBHOOK"   # post to Slack
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}   # webhook kept in secrets

  weekly-base-image:
    if: github.event.schedule == '0 3 * * 0'   # only the weekly cron triggers this job
    runs-on: ubuntu-latest
    permissions:
      contents: read                      # job-level permissions
      packages: write                     # allowed to push base image to GHCR
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3      # login to GitHub Container Registry
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6 # rebuild with --pull to get fresh OS patches
        with:
          context: .
          pull: true                      # always pull latest base layers
          push: true                      # publish refreshed image
          tags: ghcr.io/${{ github.repository }}/base:weekly   # example tag
```

(YAML syntax parsed locally; schedules not executed on GitHub.)

---

## 🟠 My Stack Integration
- **Node.js / FastAPI:** nightly `npm audit` / `pip-audit`, and dependency update checks.
- **React:** weekly Lighthouse or build test on the deployed URL.
- **Nginx / VPS:** cron-trigger an SSH step that runs `certbot renew --dry-run` check or `docker system prune -f` on the VPS (use a restricted deploy key).
- **AWS:** clean old ECR images, check unused EBS snapshots, run `aws ecr describe-image-scan-findings`; auth through OIDC, not long-lived keys.

```yaml
# Fragment: scheduled VPS cleanup using a restricted SSH key
on:
  schedule:
    - cron: "0 21 * * 0"                  # Sunday 21:00 UTC = Monday 02:30 IST
jobs:
  prune:
    runs-on: ubuntu-latest
    steps:
      - name: Prune unused Docker data on VPS
        run: |
          echo "$SSH_KEY" > key && chmod 600 key        # write key with strict permissions
          ssh -i key -o StrictHostKeyChecking=accept-new deploy@${{ secrets.VPS_HOST }} \
            'docker image prune -af --filter "until=168h"'   # remove images unused for 7 days
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Thinking cron uses local time (IST). 
✅ Correct: It is always UTC. Convert: 09:00 IST = `30 3 * * *`.

❌ Mistake 2: Putting the schedule on a feature branch and wondering why it never runs.
✅ Correct: The workflow file must be on the default branch.

❌ Mistake 3: Scheduling at `0 * * * *` exactly on the hour with heavy jobs - top-of-hour is congested and runs get delayed or dropped.
✅ Correct: Use odd minutes (`17 * * * *`).

❌ Mistake 4: Forgetting 60-day inactivity disable and missing backups silently.
✅ Correct: Monitor with a heartbeat (e.g., healthchecks.io ping) and keep the repo active.

❌ Mistake 5: Unquoted cron strings starting with `*` break YAML parsing.
✅ Correct: Always quote: `- cron: "*/15 * * * *"`.

---

## 🧠 Tricky Interview Question
Your nightly workflow has `cron: "0 0 31 * *"` for "last day of month". What happens in April?

Answer: Nothing - April has 30 days so day 31 never occurs, the job skips that month (also February). Cron has no "last day" token. Run daily on `28-31`, then inside the job check whether tomorrow is the 1st (`[ "$(date -d tomorrow +%d)" = "01" ]`) and exit successfully otherwise.

---

## ⚫ Interview Questions + Answers

Q1: What timezone does GitHub cron use?
A1: UTC only; there is no timezone option.

Q2: What is the minimum interval?
A2: Every 5 minutes; shorter intervals are not supported and runs may be delayed.

Q3: On which branch does a schedule run?
A3: Only the default branch's latest commit. `github.ref` is the default branch.

Q4: How can two cron entries drive different jobs?
A4: Compare `github.event.schedule` in each job's `if:` to the exact cron string.

Q5: How do you test a scheduled workflow without waiting?
A5: Add `workflow_dispatch` to the same workflow and run it manually (on default branch or select the branch via CLI/UI).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Nightly/weekly audits, cleanups, synthetic monitoring, report generation.
- Rebuilding images regularly for OS patches.

❌ Avoid when:
- You need exact timing or sub-5-minute frequency (use AWS EventBridge, a real cron on the server, or Kubernetes CronJob).
- The job is critical (backups) and you have no alerting if it silently stops.

---

## 📊 Visual Diagram

```
   cron "30 20 * * *"  (UTC)
          │
   ┌──────▼───────┐   every day 20:30 UTC (= 02:00 IST)
   │ GitHub       │──────────────────────────────┐
   │ scheduler    │   (may be delayed minutes)   │
   └──────────────┘                              ▼
                                     Run on DEFAULT branch (main)
                                                 │
                              ┌──────────────────┼──────────────────┐
                              ▼                  ▼                  ▼
                         npm audit        smoke test         prune ECR/VPS
                              └──────────────────┬──────────────────┘
                                                 ▼
                                      fail? -> Slack alert
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cron | 5-field time expression | समय बताने वाली 5-field expression |
| UTC | Global reference time (IST = UTC+5:30) | वैश्विक संदर्भ समय |
| default branch | Branch scheduled runs use | Scheduled runs की branch |
| github.event.schedule | Cron string that fired the run | जिस cron से run चला |
| heartbeat | Ping proving the job ran | जाँच कि job चला |
| workflow_dispatch | Manual trigger for testing | परीक्षण हेतु हाथ से trigger |

---

## ⚡ 3-Line Summary
English: `schedule` runs workflows by cron, in UTC, from the default branch only.
English: Minimum 5 minutes, may be delayed, auto-disabled after 60 inactive days on public repos.
English: Add `workflow_dispatch` for testing and alerts for failures.
Hindi: `schedule` cron से, UTC में, सिर्फ़ default branch से workflow चलाता है।
Hindi: कम से कम 5 मिनट, देर हो सकती है, public repo 60 दिन निष्क्रिय हो तो disable।
Hindi: परीक्षण के लिए `workflow_dispatch` जोड़ें और failure पर alert रखें।

---

## ➡️ Next Topic
**247. workflow_dispatch Event** - the manual "Run workflow" button with inputs, ideal for on-demand deploys and testing scheduled jobs.
