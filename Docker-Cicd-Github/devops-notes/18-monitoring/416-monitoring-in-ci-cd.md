# 416. Monitoring in CI/CD
# हिंदी में: CI/CD में Monitoring

---

## 🔵 Simple Definition (English)
**Monitoring in CI/CD** means watching the delivery pipeline and the release it ships: how long builds take, how often they fail, whether a deploy is healthy after it lands, and who gets told when something breaks. It covers pipeline health (GitHub Actions runs) and post-deploy health (smoke tests, error rate).

## 🔵 सरल परिभाषा (Hindi)
**CI/CD में monitoring** मतलब delivery pipeline और उससे निकले release पर नज़र रखना: build कितना समय लेता है, कितनी बार fail होता है, deploy के बाद service healthy है या नहीं, और कुछ टूटने पर किसे खबर मिलती है। इसमें pipeline की सेहत (GitHub Actions runs) और deploy के बाद की सेहत (smoke tests, error rate) दोनों आते हैं।

---

## 🔴 Problem it Solves
- A green pipeline can still ship a broken app (deploy succeeded, app returns 500).
- Slow, flaky builds silently waste developer hours and Actions minutes.
- Failures at night go unnoticed until customers complain.
- No history to answer "did this deploy cause the spike?".

## 🔴 यह क्यों बना? (Hindi)
- Green pipeline भी टूटा हुआ app ship कर सकती है (deploy सफल, पर app 500 दे रहा है)।
- धीमे और flaky builds चुपचाप developers का समय और Actions minutes खा जाते हैं।
- रात की failures तब तक पता नहीं चलतीं जब तक customer शिकायत न करे।
- "क्या इस deploy से spike आया?" का जवाब देने के लिए history नहीं होती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pipeline runs: lint -> test -> build -> push image -> deploy
Step 2 → After deploy, a smoke-test job curls /health and key API route (retry for ~60s)
Step 3 → If smoke test fails -> job fails -> automatic rollback step / alert
Step 4 → Notify (Slack/Discord/email) on failure with run URL, commit, actor
Step 5 → Record deploy time + duration as a metric/annotation (Pushgateway or Grafana annotation)
Step 6 → Grafana shows deploy markers on graphs; compare error rate before/after
Step 7 → Weekly review: failure rate, p95 build time, flaky tests, minutes used
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Pipeline चलती है: lint -> test -> build -> image push -> deploy
Step 2 → Deploy के बाद smoke-test job /health और मुख्य API route पर curl करता है (~60s retry)
Step 3 → Smoke test fail -> job fail -> automatic rollback step / alert
Step 4 → Failure पर Slack/Discord/email notification: run URL, commit, actor के साथ
Step 5 → Deploy का समय + duration metric/annotation के रूप में रखो (Pushgateway या Grafana annotation)
Step 6 → Grafana के graphs पर deploy markers दिखते हैं; पहले/बाद का error rate तुलना करो
Step 7 → साप्ताहिक review: failure rate, p95 build time, flaky tests, minutes use
```

---

## 🟡 Real World Example
A Razorpay-style payments API deploys to a VPS from GitHub Actions. One Friday a deploy passed all tests but a missing env var made `/api/pay` return 500. Because the pipeline had a post-deploy smoke test with automatic rollback to the previous image tag, the bad release lived for 90 seconds instead of two hours, and Slack showed the commit and run link.

## 🟡 Real Example Hindi mein
एक Razorpay-जैसी payments API GitHub Actions से VPS पर deploy होती है। एक शुक्रवार को deploy सारे tests पास कर गया, पर एक env var न होने से `/api/pay` 500 देने लगा। Pipeline में post-deploy smoke test और पिछले image tag पर automatic rollback था, इसलिए खराब release सिर्फ 90 सेकंड चला, दो घंटे नहीं, और Slack में commit और run link दिख गया।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/ci.yml  (basic: test, then notify on failure)
name: ci                                   # workflow name shown in Actions tab
on:                                        # triggers
  push:
    branches: [main]                       # run on pushes to main
jobs:
  test:                                    # job id
    runs-on: ubuntu-latest                 # GitHub-hosted runner
    timeout-minutes: 15                    # kill stuck jobs (cost + noise control)
    steps:
      - uses: actions/checkout@v4          # get the code (example version)
      - uses: actions/setup-node@v4        # install Node.js
        with:
          node-version: 20                 # LTS version
          cache: npm                       # cache npm downloads
      - run: npm ci                        # clean install from lockfile
      - run: npm test                      # run tests
      - name: Notify Slack on failure      # only runs if a previous step failed
        if: failure()                      # status check function
        run: |                             # webhook URL kept in a secret, never in code
          curl -sf -X POST -H 'Content-Type: application/json' \
            -d "{\"text\":\"CI failed: ${{ github.repository }} @ ${{ github.sha }} ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}\"}" \
            "${{ secrets.SLACK_WEBHOOK_URL }}"
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/deploy.yml  (production: deploy + smoke test + rollback + metrics)
name: deploy
on:
  push:
    branches: [main]
concurrency:                               # never run two deploys at once
  group: deploy-prod
  cancel-in-progress: false
permissions:
  contents: read                           # least privilege for GITHUB_TOKEN
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    env:
      APP_URL: https://api.example.com     # public URL used for the smoke test
    steps:
      - uses: actions/checkout@v4
      - name: Record start time            # for duration metric
        run: echo "START=$(date +%s)" >> "$GITHUB_ENV"
      - name: Deploy over SSH              # pull new image and restart on the VPS
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_KEY }}" > ~/.ssh/id_ed25519
          chmod 600 ~/.ssh/id_ed25519
          ssh -o StrictHostKeyChecking=accept-new -i ~/.ssh/id_ed25519 \
            "${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }}" \
            "cd /srv/app && IMAGE_TAG=${{ github.sha }} docker compose pull && IMAGE_TAG=${{ github.sha }} docker compose up -d"
      - name: Smoke test (retry 12 x 5s)   # prove the release is healthy
        run: |
          for i in $(seq 1 12); do
            if curl -fsS "$APP_URL/health" >/dev/null; then echo "healthy"; exit 0; fi
            echo "attempt $i failed"; sleep 5
          done
          exit 1
      - name: Rollback on failure          # go back to previous tag stored on server
        if: failure()
        run: |
          ssh -i ~/.ssh/id_ed25519 "${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }}" \
            "cd /srv/app && ./rollback.sh"
      - name: Push deploy metric           # needs a Pushgateway reachable from the runner
        if: always()
        run: |
          DUR=$(( $(date +%s) - START ))
          RESULT=$([ "${{ job.status }}" = "success" ] && echo 1 || echo 0)
          printf 'deploy_duration_seconds %s\ndeploy_success %s\n' "$DUR" "$RESULT" | \
            curl -sf --data-binary @- "${{ secrets.PUSHGATEWAY_URL }}/metrics/job/deploy/app/api"
      - name: Summary                      # visible on the run page
        if: always()
        run: echo "### Deploy ${{ job.status }} for ${{ github.sha }}" >> "$GITHUB_STEP_SUMMARY"
```
Note: YAML structure parse-checked; the SSH, Pushgateway and rollback script parts depend on your server and were not run.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: expose `/health` and Prometheus metrics (417); smoke test hits them.
- **React**: smoke test fetches `/` and checks the built asset hash or a `version.json` file.
- **Nginx/VPS**: deploy script runs `docker compose up -d`, then `nginx -t` inside the container.
- **AWS**: use CloudWatch alarms on ALB 5xx right after deploy, and CodeDeploy-style auto-rollback logic; GitHub OIDC instead of long-lived keys.

```yaml
# Grafana deploy annotation from the pipeline (API token in secret)
- name: Annotate Grafana
  if: success()
  run: |
    curl -sf -X POST "${{ secrets.GRAFANA_URL }}/api/annotations" \
      -H "Authorization: Bearer ${{ secrets.GRAFANA_TOKEN }}" \
      -H "Content-Type: application/json" \
      -d "{\"tags\":[\"deploy\"],\"text\":\"deploy ${{ github.sha }}\"}"
```
**Security**: keep tokens in Secrets, set `permissions:` minimal, never echo secrets (logs are public for public repos), restrict who can approve production environments.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deploy job ends right after `docker compose up -d`, no verification.
✅ Correct: Always add a retrying smoke test and a rollback path.

❌ Mistake 2: Notifications on every success; the channel gets muted.
✅ Correct: Alert on failure and on first success after failure; summarise the rest.

❌ Mistake 3: No `timeout-minutes`; a hung job burns the whole minutes quota.
✅ Correct: Set job and step timeouts.

❌ Mistake 4: Slack webhook URL pasted in YAML.
✅ Correct: Store it in `secrets.*`.

❌ Mistake 5: Running smoke test against `localhost` of the runner.
✅ Correct: Hit the public URL (or via SSH on the server) that users actually use.

---

## 🧠 Tricky Interview Question
Pipeline is green, the smoke test passed, but 20 minutes later the error rate rises. What do you do and what was missing?

Answer: Roll back first (known-good image tag), then investigate. The smoke test only checks a few routes right after start. Missing: post-deploy observation window using metrics (5xx rate, p95 latency compared with the previous hour), canary or gradual rollout, and alerts tied to deploy annotations. Fix: Alertmanager rules (424/425) plus an automated watch job.

---

## ⚫ Interview Questions + Answers

Q1: What do you monitor in CI/CD?
A1: Pipeline: duration, success rate, queue time, flaky tests, minutes used. Release: health after deploy, error rate, latency, rollback count (DORA metrics: deployment frequency, lead time, change failure rate, MTTR).

Q2: What does `if: failure()` vs `if: always()` do?
A2: `failure()` runs only when a previous step failed; `always()` runs regardless (even cancelled), good for cleanup and metrics.

Q3: Why use `concurrency` in deploy workflows?
A3: Prevents two deploys racing on one server; `cancel-in-progress: false` makes the second wait.

Q4: How can batch jobs report metrics to Prometheus?
A4: They are short-lived, so push to Pushgateway; Prometheus scrapes the gateway.

Q5: Where to see Actions usage?
A5: Repository/Org Settings -> Billing/Usage, and the Actions tab run timings.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Auto-deploying to production.
- Several developers merge daily.
- You track DORA metrics.

❌ Avoid when:
- Alerts are noisy; tune before adding more.
- Metrics need secrets exposed to forked-PR workflows (never expose secrets there).

---

## 📊 Visual Diagram
```
 push ─► [Lint]─►[Test]─►[Build+Push]─►[Deploy VPS]─►[Smoke test /health]
                                                         │ pass         │ fail
                                                         ▼              ▼
                                           annotate Grafana     rollback + Slack alert
                                           push deploy metrics  (run URL, sha, actor)
                                                         │
                                  Prometheus/Grafana: 5xx, p95 before vs after deploy
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Smoke test | Quick post-deploy check | deploy के बाद तेज़ जाँच |
| Rollback | Return to last good version | पिछले अच्छे version पर वापसी |
| Pushgateway | Receives metrics from short jobs | छोटे jobs के metrics लेता है |
| DORA metrics | 4 delivery KPIs | 4 delivery KPIs |
| Annotation | Marker on a graph | graph पर निशान |
| Flaky test | Randomly failing test | कभी-कभी fail होने वाला test |

---

## ⚡ 3-Line Summary
English: Monitor both the pipeline and the release it ships.
Smoke-test after deploy, roll back automatically, and notify with the run link.
Track duration, failure rate and deploy markers on dashboards.

Hindi: Pipeline और उससे निकले release दोनों की monitoring करो।
Deploy के बाद smoke test, automatic rollback और run link के साथ notification रखो।
Duration, failure rate और deploy markers dashboards पर देखो।

---

## ➡️ Next Topic
**417. Application Monitoring Setup**: now that pipelines are watched, we instrument the app itself (metrics, health, logs) so there is something to monitor.

---
