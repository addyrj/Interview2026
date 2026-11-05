# 352. Canary Deployment
# हिंदी में: Canary Deployment

---

## 🔵 Simple Definition (English)
A canary deployment sends the new version to a small share of traffic (for example 5%) while the rest still uses the stable version. You watch errors and latency, then increase the share step by step (5% to 25% to 50% to 100%), or abort and send everyone back to stable.

## 🔵 सरल परिभाषा (Hindi)
Canary deployment में नया version traffic के छोटे हिस्से (जैसे 5%) को मिलता है और बाकी users stable version पर रहते हैं। आप errors और latency देखते हैं, फिर हिस्सा धीरे-धीरे बढ़ाते हैं (5% से 25% से 50% से 100%), या abort करके सबको stable पर भेज देते हैं।

---

## 🔴 Problem it Solves
Staging never matches real traffic. A bug that only appears with real data or load hits 100% of users in a big-bang release. Canary limits the blast radius: only a few users see the problem, and you catch it with real production metrics before it spreads.

## 🔴 यह क्यों बना? (Hindi)
Staging कभी असली traffic जैसा नहीं होता। जो bug सिर्फ असली data या load पर आता है, वह big-bang release में 100% users को लगता है। Canary नुकसान का दायरा छोटा रखता है: सिर्फ कुछ users को दिक्कत दिखती है और फैलने से पहले असली production metrics से पकड़ में आ जाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Stable (v1) runs on 4 replicas and takes 100% of traffic
Step 2 → Deploy canary (v2) as 1 replica or a weighted target
Step 3 → Router sends ~5% of requests to v2
Step 4 → Compare error rate, p95 latency and business metrics vs v1
Step 5 → Healthy? raise to 25%, 50%, then 100%
Step 6 → Unhealthy? set canary weight to 0 and investigate
Step 7 → Promote: v2 becomes the new stable, remove the old
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Stable (v1) 4 replicas पर चलता है और 100% traffic लेता है
Step 2 → Canary (v2) को 1 replica या weighted target के रूप में deploy करो
Step 3 → Router लगभग 5% requests v2 को भेजता है
Step 4 → Error rate, p95 latency और business metrics को v1 से compare करो
Step 5 → ठीक है? 25%, 50%, फिर 100% करो
Step 6 → खराब? canary weight 0 करो और जाँच करो
Step 7 → Promote: v2 नया stable बनता है, पुराना हटाओ
```

---

## 🟡 Real World Example
A food-delivery app changes its restaurant-search ranking. They send 5% of users to the new service. After 20 minutes, p95 latency is the same but order conversion drops 3% in the canary group, so the team aborts and fixes the ranking. Only 5% of users saw the worse results for a short time. Google, Facebook and Swiggy-style companies rely on gradual rollouts like this.

## 🟡 Real Example Hindi mein
एक food-delivery app restaurant-search ranking बदलता है। वे 5% users को नई service पर भेजते हैं। 20 मिनट बाद p95 latency वही है पर canary group में order conversion 3% गिरता है, इसलिए team abort करके ranking ठीक करती है। सिर्फ 5% users ने थोड़ी देर खराब results देखे।

---

## 💻 Code / Config Example — Basic

```nginx
# /etc/nginx/conf.d/canary-basic.conf
# split_clients hashes the client IP so the same user keeps the same version
split_clients "${remote_addr}" $backend_pool {
    5%     canary;          # 5% of clients go to the canary
    *      stable;          # everyone else stays on stable
}

upstream stable { server 127.0.0.1:8001; }   # v1 container
upstream canary { server 127.0.0.1:8002; }   # v2 container

server {
    listen 80;                               # HTTP (add TLS in production)
    server_name app.example.com;             # your domain
    location / {
        proxy_pass http://$backend_pool;     # choose upstream by variable
        proxy_set_header Host $host;         # preserve host
        add_header X-Served-By $backend_pool always;   # debug which pool answered
    }
}
```

## 💻 Code / Config Example — Advanced

```nginx
# Advanced: weights via upstream (about 10% canary) plus opt-in header/cookie
map $http_x_canary $pool_from_header {       # internal testers send X-Canary: 1
    "1"     canary;
    default "";
}
map $cookie_canary $pool_from_cookie {       # cookie lets QA stick to canary
    "1"     canary;
    default "";
}
split_clients "${remote_addr}${http_user_agent}" $pool_random {
    10%     canary;                           # random 10%
    *       stable;
}
map "$pool_from_header$pool_from_cookie" $final_pool {
    "~canary" canary;                         # explicit opt-in wins
    default   $pool_random;                   # otherwise random split
}
```

```yaml
# .github/workflows/canary.yml - staged promotion with manual approval gates
name: Canary Release
on:
  workflow_dispatch:
    inputs:
      image:
        description: "New image tag"
        required: true
jobs:
  canary-5:
    runs-on: ubuntu-latest
    environment: production-canary          # no reviewers: starts automatically
    steps:
      - uses: appleboy/ssh-action@v1.0.3    # example version
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: /srv/myapp/canary.sh deploy "${{ inputs.image }}" 5   # start at 5%
  verify-5:
    needs: canary-5                         # runs after canary starts
    runs-on: ubuntu-latest
    steps:
      - run: sleep 600                      # observe for 10 minutes (use real metrics gate)
      - run: |
          # fail the job if the canary error rate (from your metrics API) is too high
          echo "query Prometheus/CloudWatch here and exit 1 on bad metrics"
  promote:
    needs: verify-5
    runs-on: ubuntu-latest
    environment: production                 # add Required reviewers: human approval
    steps:
      - uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: /srv/myapp/canary.sh promote "${{ inputs.image }}"      # 100%
```

```bash
#!/usr/bin/env bash
# /srv/myapp/canary.sh - helper used above (simplified)
set -euo pipefail                                        # strict mode
ACTION="$1"; IMAGE="$2"; PERCENT="${3:-100}"             # arguments
CONF=/etc/nginx/conf.d/canary-split.conf                 # file holding split_clients
case "$ACTION" in
  deploy)
    # run canary container on 8002 with the new image
    docker rm -f api-canary 2>/dev/null || true          # remove old canary
    docker run -d --name api-canary --env-file /srv/myapp/.env -p 127.0.0.1:8002:8000 "$IMAGE"
    # write the split percentage
    printf 'split_clients "${remote_addr}" $backend_pool {\n    %s%% canary;\n    * stable;\n}\n' "$PERCENT" | sudo tee "$CONF" >/dev/null
    ;;
  promote)
    # make the canary the stable: move traffic 100% to canary port
    printf 'split_clients "${remote_addr}" $backend_pool {\n    * canary;\n}\n' | sudo tee "$CONF" >/dev/null
    ;;
  abort)
    # send 0% to canary
    printf 'split_clients "${remote_addr}" $backend_pool {\n    * stable;\n}\n' | sudo tee "$CONF" >/dev/null
    ;;
esac
sudo nginx -t && sudo nginx -s reload                    # validate then reload
```

---

## 🟠 My Stack Integration
On a VPS, `split_clients` in Nginx is a simple canary. On AWS, use weighted target groups on an ALB, or Route 53 weighted records; ECS/CodeDeploy supports `Canary10Percent5Minutes`-style configurations. In Kubernetes use Argo Rollouts or Flagger. Metrics come from Prometheus, CloudWatch or Nginx logs; add a `version` label or header so you can compare v1 against v2.

```bash
# Quick canary comparison from Nginx access logs (assumes $upstream_addr logged)
# count 5xx per upstream port in the last log file
awk '$9 ~ /^5/ {c[$NF]++} END {for (k in c) print k, c[k]}' /var/log/nginx/access.log
```

Security: canary containers must have the same secrets, auth and security headers as stable; do not expose the canary port publicly, only through Nginx.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Random split per request, so one user flips between versions.
✅ Correct: Hash a stable key (user id, cookie or IP) so each user sticks to one version.

❌ Mistake 2: Judging the canary with too little traffic.
✅ Correct: Wait for enough requests; 5% of a quiet hour proves nothing.

❌ Mistake 3: Only watching CPU, not business metrics.
✅ Correct: Watch error rate, latency, and conversion or checkout success.

❌ Mistake 4: Incompatible database changes.
✅ Correct: Both versions run at once, so the schema must support both.

❌ Mistake 5: No automatic abort.
✅ Correct: Define thresholds and automate rollback (Flagger, Argo Rollouts, scripts).

---

## 🧠 Tricky Interview Question
Your canary at 5% shows the same error rate as stable, but after going to 100% errors spike. What could have been missed?

Answer: Load-dependent problems: connection pool exhaustion, database locks, cache stampedes, or rate limits that only appear at full traffic. Also, 5% may have excluded an affected user segment (specific region, device or tenant). Use staged steps with soak time, segment-aware canaries, and capacity checks, not just one early reading.

---

## ⚫ Interview Questions + Answers

Q1: Canary vs blue-green?
A1: Blue-green flips everything at once; canary exposes a small percentage first and grows gradually, giving real-traffic validation with lower blast radius.

Q2: What metrics define success?
A2: Error rate (4xx/5xx), p95/p99 latency, saturation (CPU, DB connections), and business KPIs like checkout rate.

Q3: How do you keep a user on the same version?
A3: Sticky hashing (client IP, cookie, or user id) in the load balancer.

Q4: How is canary done on AWS?
A4: Weighted ALB target groups, Route 53 weighted DNS, or CodeDeploy canary configs for ECS/Lambda.

Q5: What makes automatic rollback possible?
A5: A metrics source with thresholds plus a controller (Flagger, Argo Rollouts, CodeDeploy alarms) that sets canary weight to zero when alarms fire.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have enough traffic to get a meaningful signal quickly.
- Risky changes (pricing, search, payments) need real-user validation.

❌ Avoid when:
- Traffic is tiny, so the canary sees too few requests.
- The change is a breaking schema or protocol change that cannot coexist with the old version.

---

## 📊 Visual Diagram
```
                         95%  +--> STABLE v1 (4 replicas)
 Users --> Nginx / ALB ------>|
        split by hash    5%   +--> CANARY v2 (1 replica)
                                    |
                      metrics: errors, latency, conversion
                                    |
          ok -> 25% -> 50% -> 100% (promote)   bad -> 0% (abort)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Canary | Small first group on new version | नए version का छोटा पहला समूह |
| Blast radius | How many users a bug affects | bug से प्रभावित users की संख्या |
| Weighted routing | Traffic split by percentage | प्रतिशत के आधार पर traffic बँटवारा |
| Soak time | Waiting period to observe | observe करने का इंतज़ार |
| Auto rollback | Revert triggered by alarms | alarms से अपने-आप वापसी |

---

## ⚡ 3-Line Summary
English: Send a small slice of real traffic to the new version and watch metrics before expanding.
Keep users sticky to one version and compare against stable.
Abort automatically when thresholds are crossed; promote when healthy.
Hindi: असली traffic का छोटा हिस्सा नए version को भेजो और बढ़ाने से पहले metrics देखो।
Users को एक ही version पर sticky रखो और stable से compare करो।
Thresholds पार होने पर अपने-आप abort करो; ठीक हो तो promote।

---

## ➡️ Next Topic
**353. Rolling Deployment** — replace instances one by one so capacity never drops to zero.
