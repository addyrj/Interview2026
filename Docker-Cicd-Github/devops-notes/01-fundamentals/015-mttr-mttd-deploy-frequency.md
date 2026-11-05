# 15. MTTR + MTTD + Deploy Frequency
# हिंदी में: MTTR + MTTD + Deploy Frequency

---

## 🔵 Simple Definition (English)
**MTTD** (Mean Time To Detect) is how long it takes to notice a problem. **MTTR** (Mean Time To Restore/Recover/Repair) is how long it takes to fix it after it started. **Deploy Frequency** is how often you release to production. Together they describe how fast you ship and how fast you recover when shipping goes wrong.

## 🔵 सरल परिभाषा (Hindi)
**MTTD** (Mean Time To Detect) = problem का पता चलने में लगा समय। **MTTR** (Mean Time To Restore/Recover/Repair) = problem शुरू होने के बाद उसे ठीक करने में लगा समय। **Deploy Frequency** = production में कितनी बार release होता है। तीनों मिलकर बताते हैं कि आप कितनी तेज़ी से ship करते हैं और गड़बड़ी होने पर कितनी तेज़ी से संभालते हैं।

---

## 🔴 Problem it Solves
Without these numbers, outages are handled by gut feeling. A bug may live in production for hours simply because nobody noticed (high MTTD), or because the fix needs a slow manual release (high MTTR). Large infrequent releases also hide risk: if you deploy once a month, each deploy contains hundreds of changes and is hard to debug. Tracking all three pushes teams towards monitoring, alerting, small releases and fast rollback.

## 🔴 यह क्यों बना? (Hindi)
इन numbers के बिना outage अंदाज़े से संभाला जाता है। Bug घंटों production में पड़ा रह सकता है क्योंकि किसी को पता ही नहीं चला (high MTTD), या क्योंकि fix के लिए slow manual release चाहिए (high MTTR)। बड़े और कम-बार होने वाले releases risk छुपाते हैं: महीने में एक deploy में सैकड़ों changes होते हैं और debug मुश्किल। तीनों को track करने से teams monitoring, alerting, छोटे releases और fast rollback की तरफ जाती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Incident starts (bad deploy at 10:00).
Step 2 → Monitoring/alert fires (10:07)            => MTTD = 7 min
Step 3 → On-call acknowledges, finds cause (10:15)
Step 4 → Rollback or hotfix deployed (10:22)
Step 5 → Service healthy again (10:25)            => MTTR = 25 min (from start)
Step 6 → Post-mortem: add alert, test, or auto-rollback to shrink both numbers.
```

Formulas:

```
MTTD = sum(detected_at - started_at) / number_of_incidents
MTTR = sum(restored_at - started_at) / number_of_incidents
Deploy Frequency = production_deploys / days
```

(Definitions of MTTR vary between companies: some measure from detection, some from start. Pick one and stay consistent.)

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Incident शुरू (10:00 पर bad deploy)।
Step 2 → Monitoring/alert बजता है (10:07) => MTTD = 7 मिनट।
Step 3 → On-call ack करता है और कारण खोजता है (10:15)।
Step 4 → Rollback या hotfix deploy (10:22)।
Step 5 → Service healthy (10:25) => MTTR = 25 मिनट (start से)।
Step 6 → Post-mortem: alert, test या auto-rollback जोड़ो ताकि दोनों numbers घटें।

---

## 🟡 Real World Example
**Zomato on New Year's Eve:** order volume spikes. A payment-service deploy raises errors from 0.1% to 8%. Because Zomato has error-rate alerts, MTTD is 2 minutes; because the deploy pipeline supports one-click rollback, MTTR is 6 minutes. Without alerts, customers on Twitter would be the "monitoring" and MTTD could be 40 minutes.

**Your VPS:** a Node.js API crashes at 3 AM. With no alert, you find out at 9 AM (MTTD = 6 h). With UptimeRobot/Prometheus alert to Telegram, MTTD = 1 minute, and PM2/Docker `restart: unless-stopped` brings it back in seconds.

## 🟡 Real Example Hindi mein
**New Year's Eve पर Zomato:** order volume बढ़ता है। payment-service का एक deploy error rate 0.1% से 8% कर देता है। Error-rate alerts होने से MTTD 2 मिनट; one-click rollback होने से MTTR 6 मिनट। Alerts न हों तो Twitter पर customers ही "monitoring" बन जाते और MTTD 40 मिनट हो सकता था।

**आपका VPS:** रात 3 बजे Node.js API crash होती है। Alert नहीं तो सुबह 9 बजे पता चलेगा (MTTD = 6 घंटे)। UptimeRobot/Prometheus से Telegram alert हो तो MTTD = 1 मिनट, और Docker का `restart: unless-stopped` सेकंडों में service वापस ला देता है।

---

## 💻 Code / Config Example — Basic

A tiny bash health check you can run from cron on the VPS (every minute). It detects downtime and logs timestamps so you can compute MTTD/MTTR later.

```bash
#!/usr/bin/env bash
# healthcheck.sh - log UP/DOWN transitions for later MTTD/MTTR math
set -u                                              # error on unset variables
URL="${URL:-http://127.0.0.1:3000/health}"          # app health endpoint (override via env)
STATE_FILE="/var/tmp/app.state"                     # remembers the previous state (UP or DOWN)
LOG_FILE="/var/log/app-availability.log"            # transition log

prev=$(cat "$STATE_FILE" 2>/dev/null || echo UP)    # default previous state is UP
if curl -fsS --max-time 5 "$URL" >/dev/null; then   # -f fail on HTTP error, --max-time avoid hanging
  now=UP                                            # request succeeded
else
  now=DOWN                                          # request failed or timed out
fi

if [ "$now" != "$prev" ]; then                      # only log when state changes
  echo "$(date -u +%FT%TZ) $now" >> "$LOG_FILE"     # UTC timestamp + new state
fi
echo "$now" > "$STATE_FILE"                         # save current state for next run
```

Cron entry: `* * * * * /opt/scripts/healthcheck.sh`

## 💻 Code / Config Example — Advanced

Prometheus alert rules (high error rate and instance down) with Alertmanager-ready labels. Pair with a Telegram/Slack receiver.

```yaml
# prometheus/alerts.yml
groups:
  - name: availability                    # group of related rules
    rules:
      - alert: InstanceDown               # fires when a scrape target is unreachable
        expr: up == 0                     # "up" is 1 when scrape works, 0 when it fails
        for: 1m                           # must be true for 1 minute (avoids flapping, adds ~1 min to MTTD)
        labels:
          severity: critical              # used by Alertmanager to route to on-call
        annotations:
          summary: "{{ $labels.instance }} is down"        # human readable title
          description: "No scrape for 1m on {{ $labels.job }}"   # extra detail

      - alert: HighErrorRate              # fires on too many 5xx responses
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 2m                           # sustained 2 minutes
        labels:
          severity: page                  # page a human
        annotations:
          summary: "5xx error rate above 5%"               # shown in the notification
          runbook: "https://wiki.example.com/runbooks/5xx" # example link: put the real fix steps here
```

---

## 🟠 My Stack Integration
- **Node.js/FastAPI:** expose `/health` (liveness) and `/ready` (dependencies OK) endpoints; export request counters via `prom-client` / `prometheus-fastapi-instrumentator`.
- **Nginx:** `stub_status` and access-log 5xx counts give an early signal; Nginx `proxy_next_upstream` can hide a single failing backend.
- **Docker/VPS:** `restart: unless-stopped` + `healthcheck` reduces MTTR for crashes automatically.
- **AWS:** Route 53 health checks / CloudWatch alarms feed MTTD; keep the previous image tag so rollback is one command.

```yaml
# docker-compose.yml fragment: auto-heal + health-based detection
services:
  api:
    image: myorg/api:1.4.2               # pinned tag (never "latest") so rollback = previous tag
    restart: unless-stopped              # restart after crash/reboot (cuts MTTR)
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]   # image must contain wget (alpine busybox does)
      interval: 15s                      # check every 15 seconds
      timeout: 3s                        # fail if slower than 3 seconds
      retries: 3                         # 3 failures => unhealthy
      start_period: 20s                  # grace time while app boots
```

**Security:** alert webhooks (Telegram/Slack) are secrets; store them in Alertmanager config files with restricted permissions, never in git. Do not expose `/metrics` or Prometheus to the public internet; bind to localhost or protect with Nginx basic auth/VPN.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Only measuring MTTR from when the engineer started working.
✅ Correct: Measure from when users were affected (incident start); otherwise slow detection is hidden.

❌ Mistake 2: Alerting on everything (alert fatigue), so real alerts get ignored.
✅ Correct: Alert on user-facing symptoms (error rate, latency, downtime), with `for:` durations.

❌ Mistake 3: Rollback needs rebuilding the image.
✅ Correct: Keep previous immutable image tags and redeploy them directly.

❌ Mistake 4: Reducing deploy frequency after an outage "to be safe".
✅ Correct: Make deploys smaller and more frequent; big batches are the riskier thing.

---

## 🧠 Tricky Interview Question
Your MTTR is 4 hours but the actual fix always takes 10 minutes. Where is the time going?

**Answer:** Likely in detection (no alerts), triage (no runbook, unclear ownership), or deploy (slow pipeline, approval delays). Break MTTR into stages: detect, respond, diagnose, fix, deploy, verify. Improve the biggest slice: add alerts, runbooks, on-call rotation, faster CI, and automated rollback.

---

## ⚫ Interview Questions + Answers

Q1: MTTD vs MTTR?
A1: MTTD = time to detect an issue; MTTR = time to restore service. Detection is part of restoring if MTTR starts at incident start.

Q2: Does MTTR stand for repair, recover, or restore?
A2: All three are used. DORA uses "time to restore service". Always clarify the definition in an interview.

Q3: How to reduce MTTR quickly?
A3: Alerts, runbooks, one-click rollback, feature flags, health checks with auto-restart, good logs/traces.

Q4: Why does higher deploy frequency often lower risk?
A4: Smaller changes are easier to review, test, and revert; the blast radius is smaller.

Q5: What is a good alert?
A5: Actionable, user-impact based, has a runbook link, and fires only when a human must act.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You run production services with users depending on uptime.
- You want to justify monitoring/automation investment.
- You review incidents in post-mortems.

❌ Avoid when:
- Incident count is tiny (a mean of 1-2 incidents is meaningless; read each post-mortem instead).
- Used to blame on-call engineers.

---

## 📊 Visual Diagram

```
 bad deploy        alert        fix starts      rollback done
    |                |              |                |
 ---t0--------------t1------------t2---------------t3----> time
    |<-- MTTD ------>|
    |<-------------- MTTR (restore) ---------------->|

 Deploy Frequency:  | | | |  |  | | |  (each | = prod deploy per week)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MTTD | Mean time to detect | पता लगाने का औसत समय |
| MTTR | Mean time to restore | ठीक करने का औसत समय |
| Incident | Event hurting users | ऐसी घटना जिससे users प्रभावित हों |
| Runbook | Step-by-step fix guide | समस्या ठीक करने की गाइड |
| Rollback | Return to previous version | पिछले version पर वापसी |
| Alert fatigue | Too many alerts ignored | बहुत ज़्यादा alerts से ignore करने की आदत |

---

## ⚡ 3-Line Summary
English: MTTD measures how fast you notice problems; MTTR how fast you restore.
Deploy frequency shows how often you release, and small frequent releases reduce risk.
Improve them with alerts, health checks, runbooks and instant rollback.
Hindi: MTTD बताता है problem कितनी जल्दी पकड़ी गई; MTTR बताता है कितनी जल्दी ठीक हुई।
Deploy frequency बताती है release कितनी बार होता है; छोटे बार-बार releases से risk घटता है।
Alerts, health checks, runbooks और instant rollback से इन्हें सुधारो।

---

## ➡️ Next Topic
**16. Git vs GitHub vs GitLab vs Bitbucket** - the tooling where code and pipelines live.

---
