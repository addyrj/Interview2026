---

# 369. Scheduled Jobs Pipeline
# हिंदी में: Scheduled Jobs Pipeline

---

## 🔵 Simple Definition (English)
A scheduled jobs pipeline runs workflows on a clock using the `schedule:` trigger with cron syntax. It is used for nightly backups, health pings, report generation, and dependency checks, without a separate cron server.

## 🔵 सरल परिभाषा (Hindi)
Scheduled jobs pipeline `schedule:` trigger और cron syntax से घड़ी के हिसाब से workflows चलाता है। इसका उपयोग nightly backups, health pings, reports और dependency checks के लिए होता है, अलग cron server के बिना।

---

## 🔴 Problem it Solves
- Cron on one VPS is a hidden single point of failure; if the box dies, jobs silently stop.
- Nobody knows if last night's backup actually ran.
- Job logic lives only on the server, not in Git.

## 🔴 यह क्यों बना? (Hindi)
- एक VPS पर cron छिपा single point of failure है; box मरे तो jobs चुपचाप बंद।
- किसी को पता नहीं कि कल रात backup चला या नहीं।
- Job का logic सिर्फ server पर है, Git में नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add "on: schedule: - cron: '30 20 * * *'" (UTC time!)
Step 2 → Add workflow_dispatch so you can also run it manually
Step 3 → Job runs on default branch only
Step 4 → Job does its work (backup, report, check)
Step 5 → On failure, notify (Slack/email) so silence is never "success"
Step 6 → Optional heartbeat ping to an external monitor (dead man's switch)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → "on: schedule: - cron: '30 20 * * *'" जोड़ें (UTC समय!)
Step 2 → workflow_dispatch भी जोड़ें ताकि हाथ से भी चला सकें
Step 3 → Job सिर्फ default branch पर चलता है
Step 4 → Job अपना काम करता है (backup, report, check)
Step 5 → Failure पर notify (Slack/email), ताकि चुप्पी कभी "success" न लगे
Step 6 → Optional: external monitor को heartbeat ping (dead man's switch)
```

---

## 🟡 Real World Example
A small e-commerce store runs a nightly workflow at 02:00 IST (20:30 UTC): dump Postgres, upload to S3, delete dumps older than 30 days, and ping Healthchecks.io. One night GitHub scheduled runs were delayed by 40 minutes (this can happen under load); because the monitor expects a ping "within 3 hours", no false alarm fired. A real failure, an expired AWS key, produced a Slack alert within minutes.

## 🟡 Real Example Hindi mein
एक छोटा e-commerce store रोज़ 02:00 IST (20:30 UTC) पर workflow चलाता है: Postgres dump, S3 upload, 30 दिन से पुराने dumps delete और Healthchecks.io को ping। एक रात GitHub scheduled run 40 मिनट देर से चला (load में ऐसा हो सकता है); monitor "3 घंटे के भीतर ping" की उम्मीद करता है, इसलिए false alarm नहीं आया। असली failure, यानी expired AWS key, पर कुछ मिनट में Slack alert आ गया।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/nightly.yml
name: Nightly job                      # Name
on:
  schedule:
    - cron: "30 20 * * *"              # 20:30 UTC every day = 02:00 IST
  workflow_dispatch:                   # Allow manual runs for testing
jobs:
  nightly:
    runs-on: ubuntu-latest             # Runner
    steps:
      - uses: actions/checkout@v4      # Get scripts
      - run: ./scripts/nightly.sh      # Your task script
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/db-backup.yml
name: Nightly DB backup
on:
  schedule:
    - cron: "30 20 * * *"              # Daily 02:00 IST
    - cron: "0 */6 * * *"              # Also a health ping every 6 hours
  workflow_dispatch:
permissions:
  contents: read
  id-token: write                      # For AWS OIDC
concurrency:
  group: db-backup
  cancel-in-progress: false            # Do not kill a running backup
jobs:
  backup:
    if: github.event.schedule != '0 */6 * * *'   # Skip this job on the 6-hourly trigger
    runs-on: ubuntu-latest
    timeout-minutes: 30                # Hard limit so hangs do not burn minutes
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-db-backup   # Example ARN
          aws-region: ap-south-1
      - uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: deploy
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            set -euo pipefail
            F=/var/backups/app-$(date +%Y%m%d).dump
            docker compose -f /opt/app/docker-compose.yml exec -T db pg_dump -U app -Fc app > "$F"
            test -s "$F"               # Fail if the dump is empty
      - name: Copy dump to S3
        run: |
          # In practice, pull from the VPS with scp, or run pg_dump from a runner via a tunnel.
          echo "Upload step placeholder: aws s3 cp <file> s3://my-db-backups/prod/"
      - name: Heartbeat (dead man's switch)
        run: curl -fsS --retry 3 "${{ secrets.HEALTHCHECK_URL }}"   # Monitor alerts if this stops
  ping:
    if: github.event.schedule == '0 */6 * * *'
    runs-on: ubuntu-latest
    steps:
      - run: curl -fsS https://api.example.com/health   # Fails workflow if API is down
  notify-failure:
    if: failure()                      # Runs only if an earlier job failed
    needs: [backup, ping]
    runs-on: ubuntu-latest
    steps:
      - run: |
          curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"Scheduled job failed: ${{ github.workflow }} run ${{ github.run_id }}"}' \
            "${{ secrets.SLACK_WEBHOOK_URL }}"
```

---

## 🟠 My Stack Integration
Good scheduled tasks for your stack: Postgres/MongoDB dumps, `certbot renew --dry-run` check for Nginx certs, `docker system prune` (see Cleanup Pipeline), broken-link or SSL-expiry checks, FastAPI report generation.

```yaml
# Snippet: SSL expiry check for your domain (add as a job)
  ssl-check:
    runs-on: ubuntu-latest
    steps:
      - run: |
          # Days left on the certificate; fail if fewer than 14
          END=$(echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
          DAYS=$(( ( $(date -d "$END" +%s) - $(date +%s) ) / 86400 ))
          echo "Days left: $DAYS"
          test "$DAYS" -ge 14
```

The ssh and S3 copy details above are illustrative and were not run locally. Make the S3 step real before relying on it.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming cron is IST.
✅ Correct: GitHub cron is always UTC.

❌ Mistake 2: Expecting exact-minute starts.
✅ Correct: Runs can be delayed at busy times (top of hour especially); avoid `0 * * * *` for critical timing.

❌ Mistake 3: Forgetting that schedules run only on the default branch and that inactive repos (60 days no activity) can have schedules disabled.
✅ Correct: Keep repo active or add a monitor that tells you when pings stop.

❌ Mistake 4: No failure alert.
✅ Correct: `if: failure()` notify job and a dead-man heartbeat.

Security: use OIDC rather than static AWS keys; encrypt backups; never print connection strings.

---

## 🧠 Tricky Interview Question
Your nightly backup workflow has been green for two months, but the restore fails: the dump is 0 bytes. How did the pipeline lie?

Answer: Without `set -euo pipefail` and a size check, a failed `pg_dump` piped to a file still exits 0 for the shell step. Always assert non-empty output, verify the dump (for example `pg_restore --list`), and periodically perform a real restore test. A green job only proves the script finished.

---

## ⚫ Interview Questions + Answers

Q1: Cron syntax `*/15 9-17 * * 1-5` means?
A1: Every 15 minutes between 09:00 and 17:59 UTC on Monday to Friday.

Q2: Minimum interval?
A2: Every 5 minutes is the shortest GitHub supports.

Q3: How to run a scheduled workflow on a non-default branch?
A3: You cannot; the schedule uses the default branch. Use `workflow_dispatch` or `gh workflow run --ref`.

Q4: GitHub Actions or server cron?
A4: Actions for visibility, logs and Git-versioned logic; server cron for second-level precision or when the task must run on private networks without runners.

Q5: How to know a job stopped running?
A5: External heartbeat monitors alert on missing pings.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Daily or hourly maintenance, checks and reports.

❌ Avoid when:
- You need guaranteed exact timing or sub-minute jobs (use a queue/worker scheduler such as Celery beat or EventBridge).

---

## 📊 Visual Diagram
```
 cron (UTC) --> GitHub scheduler (may delay) --> runner
                                                   |
                    +------------------------------+
                    v
               task: backup / check / report
                    |
          success --+-- failure
             |            |
     heartbeat ping   Slack alert
   (monitor expects     (immediate)
    ping or it alerts)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cron | Time schedule syntax | समय-सारणी syntax |
| UTC | Universal time, used by GitHub | GitHub द्वारा इस्तेमाल सार्वभौमिक समय |
| Heartbeat | Periodic "I am alive" ping | समय-समय पर "मैं जीवित हूँ" ping |
| workflow_dispatch | Manual trigger | हाथ से चलाने वाला trigger |
| timeout-minutes | Max job runtime | Job का अधिकतम समय |

---

## ⚡ 3-Line Summary
English: `schedule` with cron (UTC) runs workflows without a server.
English: Always add timeouts, failure alerts and heartbeat monitoring.
English: Verify outputs, because green does not mean correct.
Hindi: cron (UTC) वाला `schedule` बिना server के workflows चलाता है।
Hindi: Timeout, failure alert और heartbeat monitoring हमेशा जोड़ें।
Hindi: Output verify करें, क्योंकि green का मतलब सही नहीं।

---

## ➡️ Next Topic
370. Cleanup Pipeline: automatically delete old images, caches, artifacts and branches.
