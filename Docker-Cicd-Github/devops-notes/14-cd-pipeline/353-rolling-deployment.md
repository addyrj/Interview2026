# 353. Rolling Deployment
# हिंदी में: Rolling Deployment

---

## 🔵 Simple Definition (English)
A rolling deployment replaces the running instances of an app one at a time (or in small batches) with the new version. At any moment some instances run the old version and some the new one, so the service stays up and capacity never drops to zero.

## 🔵 सरल परिभाषा (Hindi)
Rolling deployment में चल रहे app के instances को एक-एक करके (या छोटे batches में) नए version से बदला जाता है। किसी भी समय कुछ instances पुराने और कुछ नए version पर होते हैं, इसलिए service चालू रहती है और capacity कभी शून्य नहीं होती।

---

## 🔴 Problem it Solves
Stopping all instances and starting new ones ("recreate") creates downtime. Blue-green avoids that but needs double the infrastructure. Rolling updates give near-zero downtime using the capacity you already have, with health checks guarding each step.

## 🔴 यह क्यों बना? (Hindi)
सभी instances बंद करके नए चालू करना ("recreate") downtime देता है। Blue-green इससे बचाता है पर दोगुना infrastructure माँगता है। Rolling update मौजूद capacity से ही लगभग शून्य downtime देता है, और हर कदम पर health checks पहरेदारी करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → 4 replicas of v1 are healthy behind the load balancer
Step 2 → Remove replica 1 from rotation (drain connections)
Step 3 → Start replica 1 on v2, wait for its health check
Step 4 → Add replica 1 back; move to replica 2
Step 5 → Repeat until all replicas run v2
Step 6 → If a new replica fails health checks, STOP the rollout and keep v1 ones
Step 7 → Rollback = roll the old image forward the same way
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → v1 की 4 replicas load balancer के पीछे healthy हैं
Step 2 → Replica 1 को rotation से हटाओ (connections drain करो)
Step 3 → Replica 1 को v2 पर शुरू करो, उसके health check का इंतज़ार करो
Step 4 → Replica 1 को वापस जोड़ो; replica 2 पर जाओ
Step 5 → तब तक दोहराओ जब तक सब replicas v2 पर न हों
Step 6 → नई replica health checks में fail हो तो rollout रोको और v1 वाली रखो
Step 7 → Rollback = पुरानी image को उसी तरह roll करना
```

---

## 🟡 Real World Example
A SaaS API runs 4 Node.js containers on two EC2 instances behind an ALB. The team deploys 10 times a day. Using ECS rolling updates (`minimumHealthyPercent=75`, `maximumPercent=125`), ECS starts one new task, waits for it to pass the ALB health check, drains one old task, and repeats. Users never see an outage, and nobody pays for a duplicate environment.

## 🟡 Real Example Hindi mein
एक SaaS API की 4 Node.js containers दो EC2 पर ALB के पीछे चलती हैं। Team दिन में 10 बार deploy करती है। ECS rolling updates (`minimumHealthyPercent=75`, `maximumPercent=125`) में ECS एक नया task शुरू करता है, ALB health check pass होने का इंतज़ार करता है, एक पुराना task drain करता है और दोहराता है। Users को outage नहीं दिखता और duplicate environment का खर्च भी नहीं।

---

## 💻 Code / Config Example — Basic

```yaml
# docker-compose.yml - simple multi-replica service (Compose v2)
services:
  api:
    image: ${API_IMAGE}            # image tag injected by CD
    restart: unless-stopped        # restart on crash
    deploy:
      replicas: 3                  # run three copies
    expose:
      - "3000"                     # internal port only (Nginx connects here)
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://127.0.0.1:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
      interval: 5s                 # probe every 5 seconds
      retries: 5                   # unhealthy after 5 failures
```

```bash
# basic: recreate containers with the new image
docker compose pull api            # fetch the new image
docker compose up -d               # Compose recreates changed services
# note: with plain Compose this recreates all replicas of the service at once,
# so it is NOT a true rolling update. See the advanced script below.
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# /srv/myapp/rolling.sh - true rolling update with Docker Compose and Nginx
# Assumes the service is called "api" and Nginx resolves it via Docker DNS (round-robin).
set -euo pipefail                                         # fail on error, unset vars, pipe errors
cd /srv/myapp                                             # compose project dir
REPLICAS=3                                                # desired replica count
OLD_IDS=$(docker compose ps -q api)                       # ids of current (old) containers

echo "Pulling new image"
docker compose pull api                                   # fetch image first (no downtime)

for ID in $OLD_IDS; do
  echo "Starting one NEW replica"
  # add one extra container using the new image (Compose recreates only if config changed;
  # --no-recreate keeps existing ones untouched, --scale adds a fresh one)
  docker compose up -d --no-recreate --scale api=$((REPLICAS+1)) api
  NEW_ID=$(docker compose ps -q api | grep -v -F "$OLD_IDS" | head -n1 || true)
  # wait until the new container reports healthy (max ~60s)
  for i in $(seq 1 20); do
    STATUS=$(docker inspect -f '{{.State.Health.Status}}' "$NEW_ID" 2>/dev/null || echo starting)
    [ "$STATUS" = "healthy" ] && break
    sleep 3
  done
  if [ "$STATUS" != "healthy" ]; then
    echo "New replica unhealthy, aborting rollout"
    docker rm -f "$NEW_ID"                                # remove the bad one
    exit 1                                                # old replicas still serve traffic
  fi
  echo "Retiring old replica $ID"
  docker stop --time 30 "$ID"                             # graceful stop (30s to drain)
  docker rm "$ID"                                         # remove the old container
done
echo "Rolling update finished"
```

```yaml
# Kubernetes equivalent (most common "real" rolling update) - deployment.yaml
apiVersion: apps/v1                      # API version for Deployments
kind: Deployment                         # workload type
metadata:
  name: api                              # name of the deployment
spec:
  replicas: 4                            # desired pods
  strategy:
    type: RollingUpdate                  # default strategy
    rollingUpdate:
      maxUnavailable: 0                  # never reduce capacity during update
      maxSurge: 1                        # create one extra pod at a time
  selector:
    matchLabels:
      app: api                           # pods this deployment manages
  template:
    metadata:
      labels:
        app: api                         # pod label
    spec:
      containers:
        - name: api
          image: ghcr.io/me/myapp/api:abc1234   # example tag; CD updates this
          ports:
            - containerPort: 3000
          readinessProbe:                # gate: pod gets traffic only when ready
            httpGet:
              path: /health
              port: 3000
            periodSeconds: 5
          lifecycle:
            preStop:
              exec:
                command: ["sleep", "10"] # let the LB stop sending before shutdown
      terminationGracePeriodSeconds: 30  # time to finish in-flight requests
```

```yaml
# GitHub Actions step to run the rolling script on the VPS
- uses: appleboy/ssh-action@v1.0.3        # example version
  with:
    host: ${{ secrets.VPS_HOST }}         # server
    username: ${{ secrets.VPS_USER }}     # deploy user
    key: ${{ secrets.VPS_SSH_KEY }}       # private key secret
    script: /srv/myapp/rolling.sh         # run the rolling update
```

The shell script was syntax checked with `bash -n` only; it has not been run against a live Docker daemon, so test it on a staging VPS first.

---

## 🟠 My Stack Integration
For Node.js/FastAPI on one VPS, run 2-3 replicas of the container and let Nginx balance them. Make the app handle SIGTERM (stop accepting new connections, finish in-flight requests, then exit). On AWS, ECS rolling updates or an Auto Scaling group "instance refresh" do this natively; on Kubernetes it is the default strategy.

```javascript
// Node.js graceful shutdown so rolling updates do not drop requests
const server = app.listen(3000);                 // start the HTTP server
process.on('SIGTERM', () => {                    // Docker/K8s sends SIGTERM first
  server.close(() => process.exit(0));           // stop new conns, finish current ones
  setTimeout(() => process.exit(1), 25000).unref();   // hard stop before SIGKILL
});
```

```nginx
upstream api_pool {
    server api:3000 max_fails=2 fail_timeout=10s;   # Docker DNS name; failed backends are skipped
    keepalive 16;                                   # reuse connections to backends
}
```

Security: pull images from a trusted registry by digest or immutable tag, and keep the same security settings (non-root user, read-only filesystem where possible) on every replica.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No readiness/health check, so traffic reaches a replica that is still starting.
✅ Correct: Gate traffic on a real health endpoint.

❌ Mistake 2: Ignoring SIGTERM, so in-flight requests are cut.
✅ Correct: Handle SIGTERM and set a sensible stop grace period.

❌ Mistake 3: Breaking changes (API or DB) while old and new versions run together.
✅ Correct: Keep backward compatibility during the rollout window.

❌ Mistake 4: `maxUnavailable` too high, so capacity drops under load.
✅ Correct: Use `maxUnavailable: 0` with `maxSurge: 1` for critical services.

❌ Mistake 5: Believing `docker compose up -d` is rolling.
✅ Correct: Plain Compose recreates all replicas of a changed service together; use a script, Swarm or Kubernetes for rolling.

---

## 🧠 Tricky Interview Question
During a rolling update, a user gets a page from v2 that loads a JavaScript file which then calls an API that lands on a v1 replica, and it fails. Why, and how do you prevent it?

Answer: During the rollout both versions serve traffic, and requests of one page can be spread across them. If v2 front-end calls an endpoint that only v2 backend has, a v1 replica returns 404. Prevent it with backward/forward-compatible API changes (deploy backend first, frontend after), versioned APIs, or version affinity routing, and keep old static assets available.

---

## ⚫ Interview Questions + Answers

Q1: Rolling vs recreate?
A1: Recreate stops everything first (downtime); rolling replaces gradually and keeps the service available.

Q2: What do `maxSurge` and `maxUnavailable` mean?
A2: `maxSurge` is how many extra pods may exist above the desired count; `maxUnavailable` is how many may be missing. They control rollout speed and capacity.

Q3: How do you roll back a rolling update?
A3: In Kubernetes `kubectl rollout undo deployment/api`; elsewhere redeploy the previous image tag using the same rolling procedure.

Q4: Why is a readiness probe essential?
A4: It prevents sending traffic to a pod that is up but not ready, which would cause errors during the rollout.

Q5: Main drawback?
A5: Two versions run at once, rollback is slower than blue-green, and compatibility must be managed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have multiple replicas and want zero-downtime without extra infrastructure.
- Changes are backward compatible.

❌ Avoid when:
- You have a single instance: there is nothing to roll.
- Versions cannot coexist (breaking protocol/schema); use recreate in a maintenance window or blue-green with care.

---

## 📊 Visual Diagram
```
 t0:  [v1][v1][v1][v1]
 t1:  [v1][v1][v1][v1][v2*]      surge: new replica starts (* = health checking)
 t2:  [v1][v1][v1][v2 ]          v2 healthy, one v1 drained and stopped
 t3:  [v1][v1][v2 ][v2*]
 ...
 tN:  [v2][v2][v2][v2]           done; capacity never below 4 healthy
 if v2* fails health check -> STOP, remaining v1 keep serving
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| maxSurge | Extra instances allowed during update | update में अतिरिक्त instances की सीमा |
| maxUnavailable | Instances allowed to be down | बंद रह सकने वाले instances |
| Readiness probe | Check before sending traffic | traffic देने से पहले की जाँच |
| Draining | Letting requests finish before stop | रुकने से पहले requests पूरी होने देना |
| SIGTERM | Polite shutdown signal | शालीन shutdown signal |

---

## ⚡ 3-Line Summary
English: Rolling deployment swaps instances gradually so the service stays up with no extra environment.
Health checks and graceful shutdown make each step safe.
Old and new versions overlap, so keep changes backward compatible.
Hindi: Rolling deployment instances को धीरे-धीरे बदलता है, बिना अतिरिक्त environment के service चालू रहती है।
Health checks और graceful shutdown हर कदम को सुरक्षित बनाते हैं।
पुराने और नए versions साथ चलते हैं, इसलिए बदलाव backward compatible रखो।

---

## ➡️ Next Topic
**354. Feature Flags Deploy** — separate deploying code from releasing features, using flags to turn behavior on and off.
