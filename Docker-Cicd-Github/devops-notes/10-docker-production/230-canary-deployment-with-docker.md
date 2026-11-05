# 230. Canary Deployment with Docker
# हिंदी में: Docker के साथ Canary Deployment

---

## 🔵 Simple Definition (English)
A **canary deployment** releases the new version to a **small slice of real traffic** (for example 5%) while the rest stays on the stable version. You watch error rate and latency; if healthy, you raise the slice (5% -> 25% -> 50% -> 100%); if not, you send everyone back to stable. The name comes from the canary in the coal mine. With Docker + Nginx the split is done with weighted upstreams.

## 🔵 सरल परिभाषा (Hindi)
**Canary deployment** नए version को असली traffic के **एक छोटे हिस्से** (जैसे 5%) पर release करता है और बाकी stable version पर रहता है। आप error rate और latency देखते हो; ठीक हो तो हिस्सा बढ़ाते हो (5% -> 25% -> 50% -> 100%); नहीं तो सबको stable पर वापस भेजते हो। नाम कोयले की खान के canary पक्षी से आया है। Docker + Nginx में यह split weighted upstreams से होता है।

---

## 🔴 Problem it Solves
Tests (even staging) never match real users, real data and real load. A bug that appears only with production traffic would hit 100% of users in a normal or even blue-green release. Canary limits the blast radius: only 5% of users see the problem, you detect it from metrics, and roll back in seconds. It turns release risk into a measured experiment.

## 🔴 यह क्यों बना? (Hindi)
Tests (staging भी) असली users, असली data और असली load से कभी पूरी तरह नहीं मिलते। जो bug सिर्फ production traffic में दिखता है वह normal या blue-green release में 100% users को लगता है। Canary नुकसान का दायरा सीमित करता है: सिर्फ 5% users समस्या देखते हैं, आप metrics से पकड़ते हो और सेकंडों में rollback करते हो। यह release के risk को नापे हुए प्रयोग में बदल देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Stable (v1) runs N containers and serves 100%.
Step 2 → Start canary (v2) container(s). Nginx upstream gives it a small weight: v1 weight=19, v2 weight=1 (5%).
Step 3 → Observe for 10-30 min: HTTP 5xx rate, p95 latency, business metrics (checkout success), logs.
Step 4 → Compare canary vs stable. Within thresholds? Raise weight (25%, 50%).
Step 5 → Repeat observation at each step. Any regression -> set canary weight 0 / remove it (rollback).
Step 6 → 100% healthy -> promote: make v2 the stable set, retire v1.
Variants → split by % of requests, by cookie/header (internal users first), or by user ID hash.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Stable (v1) के N containers 100% traffic देते हैं।
Step 2 → Canary (v2) container(s) start करो। Nginx upstream उसे छोटा weight देता है: v1 weight=19, v2 weight=1 (5%)।
Step 3 → 10-30 मिनट देखो: HTTP 5xx rate, p95 latency, business metrics (checkout success), logs।
Step 4 → Canary और stable की तुलना। सीमा में है? weight बढ़ाओ (25%, 50%)।
Step 5 → हर step पर observation दोहराओ। कोई regression -> canary weight 0 / हटा दो (rollback)।
Step 6 → 100% ठीक -> promote: v2 को stable बनाओ, v1 retire करो।
Variants → requests के % से, cookie/header से (पहले internal users), या user ID hash से split।
```

---

## 🟡 Real World Example
A video-streaming company (Hotstar-style) releases a new recommendation API. They send 2% of traffic to the canary, watching p95 latency and "play-start" success rate. At 2% all is fine; at 20% the canary's p95 doubles because of an unindexed query only visible with many users. Automated analysis flags the regression, weight returns to 0, and only about 20% of users for 10 minutes saw slower pages instead of 100% for an hour. Internal staff are also routed via a cookie `X-Canary: 1` to always test the new version.

## 🟡 Real Example Hindi mein
एक video-streaming company (Hotstar जैसी) नई recommendation API release करती है। वे 2% traffic canary पर भेजते हैं और p95 latency व "play-start" success rate देखते हैं। 2% पर सब ठीक; 20% पर canary का p95 दोगुना हो जाता है क्योंकि एक unindexed query सिर्फ ज़्यादा users पर दिखती है। Automated analysis regression पकड़ता है, weight वापस 0, और 10 मिनट के लिए सिर्फ लगभग 20% users को धीमे pages दिखे, घंटे भर 100% को नहीं। Internal staff cookie `X-Canary: 1` से हमेशा नए version पर जाते हैं।

---

## 💻 Code / Config Example — Basic

```nginx
# /etc/nginx/conf.d/canary.conf - weighted split: 95% stable, 5% canary
upstream app_pool {
    server stable:3000 weight=19;       # stable container gets 19 out of 20 requests
    server canary:3000 weight=1;        # canary container gets 1 out of 20 (5%)
}
server {
    listen 80;                          # HTTP port
    location / {
        proxy_pass http://app_pool;     # weighted round-robin between the two
        proxy_set_header Host $host;    # keep the Host header
        add_header X-Served-By $upstream_addr always;   # debug: which backend answered
    }
}
```

```yaml
# docker-compose.canary.yml - stable and canary side by side behind Nginx
services:
  stable:
    image: ghcr.io/myorg/node-api:1.4.1       # current version
    environment: { APP_VERSION: "1.4.1" }     # exposed in metrics/logs
    restart: unless-stopped
  canary:
    image: ghcr.io/myorg/node-api:1.4.2       # new version under test
    environment: { APP_VERSION: "1.4.2" }
    restart: unless-stopped
  nginx:
    image: nginx:1.27-alpine                  # traffic splitter
    ports: ["80:80"]
    volumes:
      - ./canary.conf:/etc/nginx/conf.d/default.conf:ro   # the weighted config above
    depends_on: [stable, canary]
```

## 💻 Code / Config Example — Advanced

```nginx
# nginx-canary-final.conf - sticky percentage split + header override
upstream stable_pool { server stable:3000; keepalive 16; }     # stable backends
upstream canary_pool { server canary:3000; keepalive 16; }     # canary backends

split_clients "${remote_addr}${http_user_agent}" $bucket {     # deterministic hash per client
    5%   "canary_pool";                        # 5% -> value is the FULL upstream name
    *    "stable_pool";                        # rest
}
map $http_x_canary $target {                   # header override for testers
    "1"      "canary_pool";                    # force canary
    default  $bucket;                          # else the hash decision
}

server {
    listen 80;                                 # HTTP
    location / {
        proxy_pass http://$target;             # variable holding a defined upstream name is allowed
        proxy_http_version 1.1;                # needed for keepalive to upstream
        proxy_set_header Connection "";        # clear Connection header for keepalive
        proxy_set_header Host $host;           # keep Host
        add_header X-Pool $target always;      # visible in responses: easy debugging
    }
}
```

```bash
#!/usr/bin/env bash
# canary-promote.sh - step the canary weight up while watching the 5xx ratio from Nginx logs
set -euo pipefail                                          # fail fast
STEPS=(5 25 50 100)                                        # canary percentages
THRESH=1                                                   # allowed 5xx percent on canary
for p in "${STEPS[@]}"; do                                 # for each stage
  sed -E "s/^ *[0-9]+% +\"canary_pool\";/    ${p}%   \"canary_pool\";/" -i /etc/nginx/conf.d/canary.conf  # set new %
  nginx -t && nginx -s reload                              # apply gracefully
  sleep 600                                                # observe 10 minutes
  total=$(grep -c 'pool=canary_pool' /var/log/nginx/access.log || true)           # canary requests (needs log_format with pool=)
  errs=$(grep 'pool=canary_pool' /var/log/nginx/access.log | grep -cE '" 5[0-9]{2} ' || true)  # canary 5xx
  pct=$(( total>0 ? errs*100/total : 0 ))                  # integer percent
  echo "canary=${p}% errors=${pct}%"                       # log result
  if [ "$pct" -gt "$THRESH" ]; then                        # bad?
    sed -E "s/^ *[0-9]+% +\"canary_pool\";/    0%   \"canary_pool\";/" -i /etc/nginx/conf.d/canary.conf   # rollback to 0%
    nginx -s reload; echo "ROLLED BACK"; exit 1
  fi
done
```

Not tested: `nginx` is not installed here, so none of the Nginx configs ran through `nginx -t` (`split_clients` with quoted values, a `0%` bucket and `proxy_pass http://$target` should be verified on your Nginx version first). The bash script passes `bash -n` only. / nginx यहाँ install नहीं है, इसलिए configs `nginx -t` से नहीं गुज़रे; अपने version पर पहले जाँचो।

---

## 🟠 My Stack Integration
- **VPS + Nginx**: the config above. Add `log_format` with `pool=$target` and `$upstream_response_time`, then ship logs to Prometheus (nginx exporter) / Loki, or just `grep` as a start.
- **Node.js / FastAPI**: expose `APP_VERSION` and Prometheus metrics (`prom-client`, `prometheus-fastapi-instrumentator`) labelled by version so Grafana compares canary vs stable.
- **React**: canary the static bundle by cookie (internal users first) at the CDN/Nginx; keep the API compatible.
- **AWS**: ALB weighted target groups (95/5) or CloudFront continuous deployment; ECS/CodeDeploy canary configs such as `CodeDeployDefault.ECSCanary10Percent5Minutes`. Kubernetes: Argo Rollouts or Flagger with Prometheus analysis.
- **Database**: canary and stable share the DB, so schema must work for both.

```nginx
# Log format that makes canary analysis easy
log_format canary '$remote_addr [$time_local] "$request" $status '
                  'pool=$target rt=$request_time urt=$upstream_response_time';   # pool, latency fields
access_log /var/log/nginx/access.log canary;   # use it
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Canary without metrics. Nobody is watching, so it is just a slow rollout.
✅ Correct: Define success criteria first (5xx < 1%, p95 < 300ms) and automate checks.

❌ Mistake 2: Random per-request routing, so one user bounces between versions and sees inconsistent UI.
✅ Correct: Sticky split (hash of user/IP/cookie).

❌ Mistake 3: Too small a canary (0.1%) for low-traffic apps; no data in the window.
✅ Correct: Size the percentage and duration so you get enough requests (at least hundreds).

❌ Mistake 4: Canary writes data in a new format that stable cannot read.
✅ Correct: Compatible schema/API; feature flags for risky behaviour.

❌ Mistake 5: Forgetting to remove the canary after promotion/rollback.
✅ Correct: Automate cleanup and keep the last stable image tag.

---

## 🧠 Tricky Interview Question
**Q:** Your canary at 5% shows the same error rate as stable, so you go to 100% and the site crashes. What did the 5% canary fail to reveal?

**Answer:** Canary tests correctness under small load, not capacity. A memory leak, connection-pool exhaustion, DB lock contention or a cache-stampede appears only when the new version carries full traffic. Also 5% of traffic may not touch a rarely used feature (checkout with coupons) or a time-based job. Mitigation: step up gradually with soak time at each step, watch saturation metrics (CPU, memory, DB connections, queue depth) not only errors, load-test the canary separately, and ensure a fast rollback path.

---

## ⚫ Interview Questions + Answers

Q1: Canary vs blue-green?
A1: Canary shifts traffic gradually and tests with real users in small doses. Blue-green switches all at once after pre-testing. Canary reduces blast radius; blue-green gives faster full rollback and simpler state.

Q2: Canary vs A/B testing?
A2: Canary is about release safety (is it technically healthy?). A/B testing is about product decisions (which design converts better?). The routing mechanism looks the same.

Q3: What metrics do you check?
A3: The golden signals: error rate, latency, traffic, saturation, plus business KPIs and logs/traces tagged by version.

Q4: How do you do canary in Kubernetes?
A4: Two Deployments behind one Service (replica ratio gives approximate %), or Ingress canary annotations, or Argo Rollouts / Flagger / Istio traffic splitting for exact weights and automated analysis.

Q5: How to make users sticky?
A5: Hash a stable key (user ID, cookie, IP) with `split_clients`, cookie set by the proxy, or a consistent-hash balancer.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Large traffic where real-user validation matters
- You have monitoring and alerting in place
- Risky changes (new algorithm, new DB query pattern)

❌ Avoid when:
- No observability (you cannot judge the canary)
- Very low traffic (no signal), use staging tests + blue-green
- Breaking DB/API changes that stable cannot tolerate

---

## 📊 Visual Diagram
```
                 100% users
                     |
                +----v-----+     X-Canary: 1 (testers) ----+
                |  Nginx   |                                |
                | split 5% |                                |
                +--+----+--+                                |
          95%      |    |     5%                            |
        +----------v-+ +-v---------+<-----------------------+
        | STABLE v1  | | CANARY v2 |
        +-----+------+ +-----+-----+
              \             /
          metrics: errors, p95, saturation
                     |
         healthy? --yes--> 5% -> 25% -> 50% -> 100%
                  --no---> weight 0 (rollback)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Canary | Small test release | छोटा test release |
| Blast radius | Users affected by a bug | Bug से प्रभावित users |
| Weighted routing | Split by percentage | % के हिसाब से बाँटना |
| Sticky | Same user, same version | वही user, वही version |
| Golden signals | Errors, latency, traffic, saturation | चार मुख्य संकेत |
| Soak | Observe for a while | कुछ देर निगरानी |

---

## ⚡ 3-Line Summary
English: Canary sends a small share of real traffic to the new version and grows it only while metrics stay healthy.
Use sticky splitting, clear success criteria and fast rollback.
It needs monitoring, and it cannot reveal full-load capacity problems alone.

Hindi: Canary असली traffic का छोटा हिस्सा नए version को भेजता है और metrics ठीक रहने पर ही बढ़ाता है।
Sticky split, साफ़ success criteria और तेज़ rollback use करो।
इसे monitoring चाहिए, और यह अकेले full-load capacity की समस्या नहीं दिखाता।

---

## ➡️ Next Topic
**231. GitHub Actions — What + Why** - Section 11 starts: now that you know how to deploy, let's automate build, test and deploy with GitHub Actions.
