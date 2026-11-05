---

# 373. Performance Test Pipeline
# हिंदी में: Performance Test Pipeline

---

## 🔵 Simple Definition (English)
A performance test pipeline runs automated load tests (k6, Locust, Artillery) against a staging copy of your app and fails the build when latency or error rate crosses a threshold. It catches "this endpoint became 5x slower" before real users do.

## 🔵 सरल परिभाषा (Hindi)
Performance test pipeline आपके app की staging copy पर automated load tests (k6, Locust, Artillery) चलाता है और latency या error rate threshold पार करने पर build fail कर देता है। यह "यह endpoint 5 गुना धीमा हो गया" जैसी समस्या असली users से पहले पकड़ लेता है।

---

## 🔴 Problem it Solves
- Functional tests pass, but a new N+1 query makes the page take 8 seconds under load.
- Capacity is unknown: you learn the limit during a sale day outage.
- Performance regresses slowly, 5 percent per release, until it is a crisis.

## 🔴 यह क्यों बना? (Hindi)
- Functional tests पास होते हैं, पर नया N+1 query load में page को 8 सेकंड का बना देता है।
- Capacity पता नहीं: limit sale के दिन outage में पता चलती है।
- Performance धीरे-धीरे हर release में 5 प्रतिशत गिरती है, जब तक संकट न बन जाए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a k6 script: scenario (virtual users, duration) + thresholds
Step 2 → PR smoke load: 1 minute, small load, runs against ephemeral stack
Step 3 → Nightly/pre-release: bigger load against staging with realistic data
Step 4 → Thresholds: p95 latency < 500ms, error rate < 1 percent
Step 5 → Fail the job if thresholds break; upload the summary as artifact
Step 6 → Compare with the last run (trend) to spot slow drift
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → k6 script लिखें: scenario (virtual users, duration) + thresholds
Step 2 → PR पर smoke load: 1 मिनट, हल्का load, ephemeral stack पर
Step 3 → Nightly/pre-release: असली data वाले staging पर बड़ा load
Step 4 → Thresholds: p95 latency < 500ms, error rate < 1 प्रतिशत
Step 5 → Thresholds टूटें तो job fail; summary artifact में upload
Step 6 → धीमे drift के लिए पिछले run से तुलना (trend)
```

---

## 🟡 Real World Example
An IRCTC-style booking API had to survive a 10x spike at 10 AM. The team ran a nightly k6 ramp (50 to 500 virtual users) against staging. One night, p95 on `/search` jumped from 180 ms to 1.4 s after a PR added an unindexed filter. The job failed, the PR was fixed with an index, and the sale day passed without incident.

## 🟡 Real Example Hindi mein
IRCTC जैसी booking API को सुबह 10 बजे 10 गुना spike झेलना था। Team ने staging पर nightly k6 ramp (50 से 500 virtual users) चलाया। एक रात एक PR में बिना index का filter जुड़ने से `/search` का p95 180 ms से 1.4 s हो गया। Job fail हुआ, PR में index लगाकर fix हुआ, और sale का दिन बिना घटना गुज़रा।

---

## 💻 Code / Config Example — Basic

```javascript
// load/smoke.js  (k6 script, run with: k6 run load/smoke.js)
import http from 'k6/http';            // k6 HTTP client
import { check, sleep } from 'k6';     // Assertions and think time

export const options = {               // Test configuration
  vus: 10,                             // 10 virtual users
  duration: '30s',                     // Run for 30 seconds
  thresholds: {                        // Pass/fail rules
    http_req_failed: ['rate<0.01'],    // Less than 1 percent errors
    http_req_duration: ['p(95)<500'],  // 95 percent of requests under 500 ms
  },
};

export default function () {           // Runs repeatedly per virtual user
  const res = http.get(`${__ENV.BASE_URL}/health`);   // Target from environment
  check(res, { 'status is 200': (r) => r.status === 200 });   // Verify response
  sleep(1);                            // Think time between requests
}
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/perf.yml
name: Performance test
on:
  schedule:
    - cron: "0 21 * * *"               # Nightly (UTC)
  workflow_dispatch:
    inputs:
      base_url:
        description: Target URL (staging only!)
        required: true
        default: https://staging.example.com
  pull_request:
    paths: ["app/**", "load/**"]       # Smoke test when app code changes
jobs:
  smoke-on-pr:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Start ephemeral stack
        run: docker compose -f deploy/compose.ci.yml up -d --build   # api + db for the test
      - name: Wait for health
        run: |
          for i in $(seq 1 30); do curl -fs http://localhost:8000/health && exit 0; sleep 2; done
          exit 1
      - uses: grafana/setup-k6-action@v1     # Installs k6 (example version)
      - name: Run smoke load
        run: k6 run load/smoke.js
        env:
          BASE_URL: http://localhost:8000
  nightly-load:
    if: github.event_name != 'pull_request'
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: grafana/setup-k6-action@v1
      - name: Run ramping load test against staging
        run: k6 run --summary-export=summary.json load/ramp.js
        env:
          BASE_URL: ${{ github.event.inputs.base_url || 'https://staging.example.com' }}
      - uses: actions/upload-artifact@v4     # Keep results for trend comparison
        if: always()
        with:
          name: k6-summary
          path: summary.json
          retention-days: 30
```

```javascript
// load/ramp.js  (used by the nightly job)
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [                            // Gradual traffic shape
    { duration: '2m', target: 50 },    // Warm up to 50 users
    { duration: '5m', target: 200 },   // Hold a realistic peak
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_req_duration{endpoint:search}': ['p(95)<600'],   // Per-endpoint threshold via tag
  },
};

export default function () {
  const r = http.get(`${__ENV.BASE_URL}/api/search?q=phone`, { tags: { endpoint: 'search' } });
  check(r, { ok: (x) => x.status === 200 });
  sleep(Math.random() * 2);            // Random think time to avoid lockstep traffic
}
```

---

## 🟠 My Stack Integration
- Test against staging on the same VPS size as production, or results mislead. GitHub-hosted runners are shared; use them to detect regressions (relative change), not to measure absolute capacity.
- Never load test production without agreement, and never point it at third parties (payment gateways, SMS).
- Watch the server while testing: `docker stats`, Nginx `upstream_response_time` in logs, Postgres `pg_stat_statements`. Add these to Prometheus/Grafana dashboards.
- For FastAPI, `uvicorn --workers N` and DB pool size usually decide the ceiling; for Node, event-loop lag.
- Not run locally; check `grafana/setup-k6-action` current version and inputs.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Load testing an empty database.
✅ Correct: Seed realistic data volume; indexes behave differently at scale.

❌ Mistake 2: Judging by average latency.
✅ Correct: Use p95/p99; averages hide tail pain.

❌ Mistake 3: Running the generator on the same box as the app.
✅ Correct: Separate load generator and target.

❌ Mistake 4: Pointing the test at production by default.
✅ Correct: Require explicit, validated staging URL; guard in the script.

Security: staging endpoints may need a test-only token; store it in secrets, not in the script. Rate limiting and WAF may block your own test, so whitelist the runner deliberately.

---

## 🧠 Tricky Interview Question
Your load test shows 200 ms average and passes, yet users complain of slowness. What did you miss?

Answer: Averages hide the tail. A few requests at 5 s barely move the mean. Check p95/p99, error rate, and "coordinated omission" (a generator that waits for slow responses sends fewer requests). Also test realistic traffic mixes and data sizes, not one fast endpoint.

---

## ⚫ Interview Questions + Answers

Q1: Load vs stress vs spike vs soak test?
A1: Load: expected traffic. Stress: beyond limits to find breaking point. Spike: sudden surge. Soak: long duration to find leaks.

Q2: What is p95?
A2: 95 percent of requests are faster than this value.

Q3: Why use thresholds?
A3: They turn a load test into a pass/fail gate so regressions block releases.

Q4: Virtual user vs requests per second?
A4: VUs model concurrent users with think time; arrival-rate executors fix request rate regardless of response time.

Q5: Common bottlenecks?
A5: DB queries and missing indexes, connection pools, single-threaded work, N+1 calls, and slow third-party calls.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Latency matters (APIs, checkout) or before big events.

❌ Avoid when:
- You only have a prototype with no realistic environment; start with basic monitoring first.

---

## 📊 Visual Diagram
```
 k6 scripts (Git) --> runner (load generator)
                            |
                            v  HTTP traffic
                   [ staging: Nginx -> API -> DB ]
                            |
              metrics: p95, error rate, throughput
                            |
          thresholds ok? --yes--> pass, store summary
                         --no---> fail PR / alert
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| VU | Virtual user | आभासी user |
| p95 | 95th percentile latency | 95वाँ percentile latency |
| Threshold | Pass/fail limit | Pass/fail सीमा |
| Throughput | Requests per second | प्रति सेकंड requests |
| Soak test | Long-duration test | लंबी अवधि का test |

---

## ⚡ 3-Line Summary
English: Automate k6 load tests with thresholds in CI.
English: Smoke test on PRs, heavier ramp nightly against staging.
English: Judge by p95 and errors, on realistic data.
Hindi: CI में thresholds वाले k6 load tests automate करें।
Hindi: PR पर smoke test, staging पर रात में भारी ramp।
Hindi: असली data पर p95 और errors से judge करें।

---

## ➡️ Next Topic
374. Multi-Environment Pipeline: dev, staging and production with promotion and approvals.
