# 14. DevOps Metrics (DORA Metrics)
# हिंदी में: DevOps Metrics (DORA Metrics)

---

## 🔵 Simple Definition (English)
**DORA metrics** are four measurements from Google's DevOps Research and Assessment team that show how well a team ships software: **Deployment Frequency**, **Lead Time for Changes**, **Change Failure Rate**, and **Time to Restore Service** (older name: MTTR). Two measure speed, two measure stability. (Newer DORA reports also discuss a fifth, reliability, and rename restore time as "failed deployment recovery time"; the core idea is unchanged.)

## 🔵 सरल परिभाषा (Hindi)
**DORA metrics** चार measurements हैं जो Google की DevOps Research and Assessment team ने बताईं, ताकि पता चले कि team कितनी अच्छी तरह software ship करती है: **Deployment Frequency**, **Lead Time for Changes**, **Change Failure Rate**, और **Time to Restore Service** (पुराना नाम MTTR)। दो metrics speed नापते हैं, दो stability। (नई reports में एक पाँचवाँ reliability metric और restore time का नया नाम "failed deployment recovery time" भी आता है; मूल idea वही है।)

---

## 🔴 Problem it Solves
Before DORA, teams measured the wrong things: lines of code, number of commits, story points, or "how busy everyone looks". None of these tell you if customers get value safely. Managers also believed "move fast" and "stay stable" are a trade-off. DORA's multi-year research showed that elite teams are good at both at the same time. The metrics give an objective, comparable scoreboard so you can find the real bottleneck (slow reviews? flaky tests? manual deploys?).

## 🔴 यह क्यों बना? (Hindi)
DORA से पहले teams गलत चीज़ें नापती थीं: lines of code, commits की गिनती, story points, या "सब कितने busy दिख रहे हैं"। इनसे यह पता नहीं चलता कि customer को value safely मिल रही है या नहीं। Managers यह भी मानते थे कि "तेज़ चलना" और "stable रहना" में trade-off है। DORA की research ने दिखाया कि elite teams दोनों में एक साथ अच्छी होती हैं। ये metrics एक objective scoreboard देते हैं ताकि असली bottleneck मिले (slow reviews? flaky tests? manual deploys?)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define "deployment" = a release that reaches production (not staging).
Step 2 → Collect events: commit time, PR merge time, deploy start/end, incident open/close.
Step 3 → Compute 4 metrics per service per week/month (use median, not average).
Step 4 → Compare with DORA bands (Elite / High / Medium / Low).
Step 5 → Pick ONE bottleneck metric, change the process, re-measure next month.
```

The four metrics:

```
1. Deployment Frequency   = number of prod deploys / time
2. Lead Time for Changes  = time from commit merged -> running in prod
3. Change Failure Rate    = failed deploys (rollback/hotfix) / total deploys * 100
4. Time to Restore (MTTR) = time from incident start -> service restored
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → "Deployment" define करो = ऐसा release जो production तक पहुँचे (staging नहीं)।
Step 2 → Events collect करो: commit time, PR merge time, deploy start/end, incident open/close।
Step 3 → चारों metrics हर service के लिए हर हफ्ते/महीने निकालो (average नहीं, median use करो)।
Step 4 → DORA bands (Elite / High / Medium / Low) से compare करो।
Step 5 → एक bottleneck metric चुनो, process बदलो, अगले महीने फिर नापो।

चारों metrics: Deployment Frequency (कितनी बार prod deploy), Lead Time (merge से prod तक का समय), Change Failure Rate (कितने % deploys fail/rollback हुए), Time to Restore (incident से recovery तक का समय)।

---

## 🟡 Real World Example
**Your VPS deployment.** You run a Node.js API + React app on one VPS behind Nginx. Today you SSH in, `git pull`, and restart PM2 once a week (Deployment Frequency = weekly, Lead Time = ~3 days because you batch changes, CFR = 25% because big batches break, MTTR = 2 hours because you debug on the server). After moving to GitHub Actions with small PRs and auto-rollback, you deploy daily, lead time becomes 40 minutes, CFR 8%, MTTR 15 minutes. Same team, same server, measurably better.

**Swiggy-style example:** during IPL nights Swiggy cannot afford long outages, so MTTR and CFR matter more than raw deploy count.

## 🟡 Real Example Hindi mein
**आपका VPS deployment।** Node.js API + React app एक VPS पर Nginx के पीछे चलता है। अभी आप SSH करके `git pull` और PM2 restart हफ्ते में एक बार करते हैं (Deployment Frequency = weekly, Lead Time = ~3 दिन क्योंकि changes batch होते हैं, CFR = 25% क्योंकि बड़े batch टूटते हैं, MTTR = 2 घंटे क्योंकि server पर debug करते हैं)। GitHub Actions, छोटे PRs और auto-rollback के बाद: daily deploy, lead time 40 मिनट, CFR 8%, MTTR 15 मिनट। Team वही, server वही, पर नतीजा measurable बेहतर।

**Swiggy-style:** IPL की रात लंबा outage affordable नहीं, इसलिए वहाँ MTTR और CFR, deploy count से ज़्यादा मायने रखते हैं।

---

## 💻 Code / Config Example — Basic

Measure Deployment Frequency from GitHub deployments with the `gh` CLI (needs `gh auth login`; replace OWNER/REPO).

```bash
#!/usr/bin/env bash
# dora-basic.sh - count production deployments in the last 30 days
set -euo pipefail                                   # stop on error, unset var, or pipe failure

REPO="${1:?usage: dora-basic.sh OWNER/REPO}"        # first argument is required: OWNER/REPO
SINCE=$(date -u -d '30 days ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null \
  || date -u -v-30d +%Y-%m-%dT%H:%M:%SZ)            # GNU date (Linux) first, BSD date (macOS) as fallback

# list deployments for the "production" environment (GitHub REST API via gh)
gh api "repos/${REPO}/deployments?environment=production&per_page=100" \
  --jq "[.[] | select(.created_at >= \"${SINCE}\")] | length" \
  | xargs -I{} echo "Deploys in last 30 days: {}"   # print the count
```

## 💻 Code / Config Example — Advanced

A GitHub Actions workflow that records deploy events (deploy time + lead time) on every production deploy, so metrics are computed automatically. Action versions are examples; update them.

```yaml
# .github/workflows/dora-deploy.yml
name: deploy-and-record-dora            # workflow name shown in the Actions tab

on:                                      # when this workflow runs
  push:
    branches: [main]                     # every merge to main = candidate prod deploy

permissions:                             # least privilege for GITHUB_TOKEN
  contents: read                         # only read the repo
  deployments: write                     # allow creating deployment records

concurrency:                             # never run two prod deploys at once
  group: prod-deploy
  cancel-in-progress: false              # queue instead of cancelling a running deploy

jobs:
  deploy:
    runs-on: ubuntu-latest               # GitHub-hosted runner
    environment: production              # creates a "deployment" entry GitHub can query
    steps:
      - uses: actions/checkout@v4        # fetch code (example version, update as needed)
      - name: Record start time
        run: echo "DEPLOY_START=$(date +%s)" >> "$GITHUB_ENV"   # save epoch seconds for later steps
      - name: Deploy to VPS over SSH
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}     # private key stored as encrypted secret
          HOST: ${{ secrets.VPS_HOST }}           # server address stored as secret
        run: |
          install -m 600 /dev/null key.pem        # create key file readable only by owner
          printf '%s\n' "$SSH_KEY" > key.pem      # write the secret key into it
          ssh -i key.pem -o StrictHostKeyChecking=accept-new deploy@"$HOST" '/opt/app/deploy.sh'
      - name: Compute lead time
        run: |
          COMMIT_TS=$(git log -1 --format=%ct)    # commit time (epoch) of the deployed commit
          NOW=$(date +%s)                          # current time (epoch)
          echo "Lead time seconds: $((NOW - COMMIT_TS))"   # commit -> prod duration (log or push to Prometheus)
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI:** each service is deployed independently, so measure DORA per service, not per company.
- **React:** frontend deploys (static build to Nginx/S3+CloudFront) are cheap, so deploy frequency is usually highest here.
- **Nginx/VPS:** log every deploy to a file; Nginx 5xx rate right after a deploy is a good "failed change" signal.
- **AWS:** use CloudWatch alarms to auto-detect incidents (MTTD), then close them to compute MTTR.

```yaml
# docker-compose.yml fragment: expose a tiny exporter so Prometheus can scrape deploy metrics
services:
  dora-exporter:                         # custom small service that publishes deploy counters
    image: myorg/dora-exporter:1.0.0     # example image name, build your own
    restart: unless-stopped              # survive VPS reboot
    environment:
      - GITHUB_REPO=myorg/myapp          # which repo to read deployments from
      - GITHUB_TOKEN_FILE=/run/secrets/gh_token   # read token from a secret file, not an env value
    secrets:
      - gh_token                         # mount the secret
    ports:
      - "127.0.0.1:9101:9101"            # bind to localhost only, Nginx/Prometheus on same host scrapes it
secrets:
  gh_token:
    file: ./secrets/gh_token.txt         # local file, keep it out of git (.gitignore)
```

**Security:** metrics tooling needs only read tokens; never reuse the deploy SSH key. Do not use DORA numbers to rank or punish individuals (Goodhart's law: people will game it).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Counting deploys to staging as "deployment frequency".
✅ Correct: Count only production releases.

❌ Mistake 2: Using averages; one 3-day outage hides everything.
✅ Correct: Use the median (and look at p90).

❌ Mistake 3: Using metrics as individual performance targets.
✅ Correct: They are team/system metrics to find bottlenecks.

❌ Mistake 4: Chasing deploy frequency by splitting tiny meaningless releases while CFR rises.
✅ Correct: Watch speed and stability together.

---

## 🧠 Tricky Interview Question
Your team deploys 20 times a day but customers complain about instability. Are you "elite"?

**Answer:** No. DORA needs both speed and stability. High frequency with a high Change Failure Rate and long Time to Restore is not elite. Look at CFR and MTTR, add automated tests, canary/blue-green deploys and fast rollback. Also check whether "deploys" include no-op or config-only changes inflating the count.

---

## ⚫ Interview Questions + Answers

Q1: What are the four DORA metrics?
A1: Deployment Frequency, Lead Time for Changes, Change Failure Rate, Time to Restore Service. First two = throughput, last two = stability.

Q2: How do you measure Lead Time for Changes?
A2: From the commit (or PR merge) to the moment it runs in production. Take the timestamp from git and the deploy-finish timestamp from CI/CD.

Q3: What is a "failure" for Change Failure Rate?
A3: Any production change that needed a rollback, hotfix, or caused an incident. Define it once and keep the definition stable.

Q4: How can you improve Lead Time?
A4: Smaller PRs, faster CI (cache, parallel jobs), automated tests instead of manual QA, trunk-based development, auto-deploy on merge.

Q5: Why median and not average?
A5: Distributions are skewed; a few extreme values distort the average. Median shows the typical experience.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want an objective view of delivery health over months.
- You are justifying CI/CD or automation investment to management.
- You compare services inside the same org to find bottlenecks.

❌ Avoid when:
- Used to compare different companies or rank individuals.
- Team has too few deploys (tiny hobby app) for statistics to mean anything.
- You treat the numbers as targets instead of signals.

---

## 📊 Visual Diagram

```
        SPEED                         STABILITY
  +-------------------+         +----------------------+
  | Deploy Frequency  |         | Change Failure Rate  |
  | Lead Time Changes |         | Time to Restore      |
  +---------+---------+         +----------+-----------+
            \                              /
             \                            /
              v                          v
        commit --> CI --> deploy --> monitor --> incident?
          |                 |                       |
          t0                t1 (lead = t1-t0)      t2..t3 (MTTR = t3-t2)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DORA | DevOps Research and Assessment team | DevOps research टीम |
| Deployment Frequency | How often prod is released | कितनी बार prod release |
| Lead Time | Commit to production time | commit से prod तक का समय |
| Change Failure Rate | % of deploys that fail | कितने % deploys fail हुए |
| MTTR | Mean/median time to restore | service वापस लाने का समय |
| Median | Middle value | बीच का मान |

---

## ⚡ 3-Line Summary
English: DORA has four metrics: deploy frequency, lead time, change failure rate, restore time.
They balance speed with stability and show the real bottleneck.
Use them as team signals, never as individual targets.
Hindi: DORA के चार metrics हैं: deploy frequency, lead time, change failure rate, restore time।
ये speed और stability का संतुलन दिखाकर असली bottleneck बताते हैं।
इन्हें team के signals की तरह use करो, individual targets की तरह नहीं।

---

## ➡️ Next Topic
**15. MTTR + MTTD + Deploy Frequency** - a deeper look at the time-based metrics and how to reduce them with alerting and rollback.

---
