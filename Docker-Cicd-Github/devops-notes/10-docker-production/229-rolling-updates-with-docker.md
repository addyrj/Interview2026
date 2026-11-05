# 229. Rolling Updates with Docker
# हिंदी में: Docker के साथ Rolling Updates

---

## 🔵 Simple Definition (English)
A **rolling update** replaces running containers with the new version **a few at a time** while the rest keep serving traffic. At any moment some instances run the old version and some the new one, until all are new. Swarm does this natively (`docker service update`, `update_config`). On a single VPS with Compose you can do a rolling replace of scaled replicas with a script.

## 🔵 सरल परिभाषा (Hindi)
**Rolling update** चल रहे containers को नए version से **कुछ-कुछ करके** बदलता है जबकि बाकी traffic देते रहते हैं। किसी भी पल कुछ instances पुराने और कुछ नए version पर होते हैं, जब तक सब नए न हो जाएँ। Swarm यह natively करता है (`docker service update`, `update_config`)। एक VPS पर Compose के साथ scaled replicas को script से rolling तरीके से बदल सकते हैं।

---

## 🔴 Problem it Solves
Stopping all containers and starting new ones (`down` then `up`) causes downtime. Blue-green avoids it but needs double capacity. Rolling updates give near-zero downtime with only a little extra capacity (one extra instance at a time), and if the new version fails its health check the update pauses or rolls back automatically before it reaches every instance.

## 🔴 यह क्यों बना? (Hindi)
सारे containers रोककर नए चालू करना (`down` फिर `up`) downtime देता है। Blue-green इससे बचाता है पर दोगुनी capacity माँगता है। Rolling update लगभग zero downtime देता है और बहुत कम extra capacity (एक बार में एक extra instance) लेता है, और नया version health check में fail हो तो update सभी instances तक पहुँचने से पहले रुक जाता है या अपने-आप rollback हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Start: 4 replicas of v1 behind a load balancer.
Step 1 → parallelism=1: Docker picks 1 replica. order=start-first: start a v2 replica first.
Step 2 → Wait until v2 is healthy (HEALTHCHECK) and has run for `monitor` seconds.
Step 3 → Stop one v1 replica (SIGTERM -> graceful -> after stop_grace_period SIGKILL).
Step 4 → Wait `delay` seconds, then repeat for the next replica. Now 3 v1 + 1 v2, then 2+2 ...
Step 5 → If a new task fails: `failure_action` decides: pause (default), continue, or rollback.
Step 6 → Done when all replicas are v2. Manual undo: `docker service rollback <service>`.
Note → During the rollout BOTH versions serve traffic: API and DB changes must be compatible.
```

## 🟢 कैसे काम करता है? (Hindi)

```
शुरू: Load balancer के पीछे v1 की 4 replicas।
Step 1 → parallelism=1: Docker 1 replica चुनता है। order=start-first: पहले v2 replica start करो।
Step 2 → v2 healthy (HEALTHCHECK) होने और `monitor` सेकंड चलने तक रुको।
Step 3 → एक v1 replica रोको (SIGTERM -> graceful -> stop_grace_period के बाद SIGKILL)।
Step 4 → `delay` सेकंड रुको, अगली replica के लिए दोहराओ। अब 3 v1 + 1 v2, फिर 2+2 ...
Step 5 → नया task fail हो तो `failure_action` तय करता है: pause (default), continue, या rollback।
Step 6 → सब replicas v2 होने पर पूरा। Manual undo: `docker service rollback <service>`।
नोट → Rollout के दौरान DONO versions traffic देते हैं: API और DB बदलाव compatible होने चाहिए।
```

---

## 🟡 Real World Example
A food-delivery API runs 6 replicas on a 3-node Swarm. Each release uses `parallelism: 2`, `delay: 15s`, `order: start-first`, `failure_action: rollback`. One Friday a release has a bug that crashes at startup: the first two new tasks fail their health check, Swarm automatically rolls back, and only 2 of 6 replicas ever saw the bad version for a few seconds. Customers noticed nothing, and the on-call got a Slack alert from the deploy script instead of a 2 a.m. incident.

## 🟡 Real Example Hindi mein
एक food-delivery API 3-node Swarm पर 6 replicas चलाती है। हर release में `parallelism: 2`, `delay: 15s`, `order: start-first`, `failure_action: rollback`। एक शुक्रवार release में startup पर crash करने वाला bug था: पहले दो नए tasks health check में fail, Swarm ने अपने-आप rollback किया, और 6 में से सिर्फ 2 replicas ने कुछ सेकंड के लिए bad version देखा। Customers को पता नहीं चला, और on-call को रात 2 बजे incident की जगह deploy script से Slack alert मिला।

---

## 💻 Code / Config Example — Basic

```bash
# Swarm: create the service with 4 replicas
docker service create --name api --replicas 4 -p 3000:3000 myorg/node-api:1.4.1   # initial version v1

# Rolling update to v2, one replica at a time, 10s apart, start the new one BEFORE stopping the old
docker service update \
  --image myorg/node-api:1.4.2 \
  --update-parallelism 1 \
  --update-delay 10s \
  --update-order start-first \
  --update-failure-action rollback \
  api                                            # flags: batch size, pause between batches, order, action on failure

docker service ps api                            # watch old tasks shut down and new ones start
docker service rollback api                      # manual undo to the previous spec
```

## 💻 Code / Config Example — Advanced

```yaml
# stack.yml - production rolling update policy (deploy with: docker stack deploy -c stack.yml shop)
services:
  api:
    image: ghcr.io/myorg/node-api:${TAG}         # TAG set by CI (example: sha-abc1234)
    environment:
      NODE_ENV: production                       # production mode
    healthcheck:
      test: ["CMD", "wget", "-q", "-O-", "http://127.0.0.1:3000/readyz"]  # Swarm only routes to healthy tasks
      interval: 5s                               # fast feedback
      timeout: 3s
      retries: 3
      start_period: 20s                          # warm-up grace
    stop_grace_period: 30s                       # drain in-flight requests
    deploy:
      replicas: 6                                # total instances
      update_config:
        parallelism: 2                           # replace 2 at a time
        delay: 15s                               # wait between batches
        order: start-first                       # new before old: no capacity dip
        failure_action: rollback                 # auto rollback on failure
        monitor: 30s                             # watch each new task for 30s before moving on
        max_failure_ratio: 0.1                   # tolerate up to 10% failed tasks
      rollback_config:
        parallelism: 3                           # roll back faster than we roll forward
        order: stop-first                        # free resources first when rolling back
      restart_policy:
        condition: on-failure                    # restart crashed tasks
        max_attempts: 3                          # but not forever
      resources:
        limits: { cpus: "0.5", memory: 384M }    # caps (rolling needs headroom: start-first runs extra tasks)
        reservations: { cpus: "0.1", memory: 128M }
```

```bash
#!/usr/bin/env bash
# rolling-compose.sh - poor man's rolling update for plain Docker Compose on ONE VPS
# Requires: Nginx upstream with several api containers (api-1..api-3), each with its own port
set -euo pipefail                                          # stop on error
TAG=$1                                                     # new image tag
for n in 1 2 3; do                                         # one replica at a time
  export TAG
  docker compose pull "api$n"                              # fetch new image first
  docker compose up -d --no-deps "api$n"                   # recreate ONLY this service (others keep serving)
  for i in $(seq 1 30); do                                 # wait until it is healthy
    s=$(docker inspect -f '{{.State.Health.Status}}' "$(docker compose ps -q "api$n")")  # read health
    [ "$s" = healthy ] && break                            # ready, go on
    [ "$i" = 30 ] && { echo "api$n failed, stop rollout"; exit 1; }   # stop; remaining replicas still on old version
    sleep 2
  done
  echo "api$n updated"                                     # progress log
done
```

```yaml
# docker-compose.yml for the script above (three named replicas, Nginx balances across them)
services:
  api1: &api                                               # YAML anchor: reuse config below
    image: ghcr.io/myorg/node-api:${TAG:-latest}           # tag injected by the script
    healthcheck:
      test: ["CMD", "wget", "-q", "-O-", "http://127.0.0.1:3000/readyz"]
      interval: 5s
      timeout: 3s
      retries: 3
    stop_grace_period: 30s
    restart: unless-stopped
  api2: *api                                               # same config, second replica
  api3: *api                                               # third replica
  nginx:
    image: nginx:1.27-alpine                               # balances api1:3000, api2:3000, api3:3000 by Docker DNS name
    ports: ["80:80"]
    depends_on: [api1, api2, api3]
```

Checked: YAML parses (stack and Compose), `bash -n` passes. Not run on a real Swarm. `update_config.order` needs Compose file format 3.4+ / current Compose spec. / Swarm cluster पर नहीं चलाया।

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: health check + graceful shutdown are mandatory. Without them rolling update drops requests.
- **Nginx on VPS**: upstream block with multiple `server api1:3000; server api2:3000; ...`. Nginx tries the next upstream on a connection error (`proxy_next_upstream error timeout`), which hides single-replica restarts.
- **FastAPI**: uvicorn workers drain on SIGTERM; set `--timeout-graceful-shutdown`.
- **React**: static Nginx container; rolling is trivial. Use content-hashed filenames so old and new HTML both find their JS during rollout.
- **AWS ECS**: rolling is the default deployment type; set `minimumHealthyPercent=100`, `maximumPercent=200` to mimic start-first. ALB health checks gate traffic.
- **Database migrations**: run as a separate one-off job before the rollout, backward compatible.

```nginx
# upstream for the Compose rolling script
upstream api_pool {
    server api1:3000 max_fails=2 fail_timeout=5s;   # mark a server failed after 2 errors for 5s
    server api2:3000 max_fails=2 fail_timeout=5s;
    server api3:3000 max_fails=2 fail_timeout=5s;
    keepalive 16;                                    # reuse connections to backends
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No HEALTHCHECK, so Swarm thinks a started-but-broken task is fine and keeps rolling.
✅ Correct: Real readiness check and `monitor` period.

❌ Mistake 2: `order: stop-first` with only 2 replicas, which halves capacity during update.
✅ Correct: `start-first` and `parallelism: 1`, or more replicas.

❌ Mistake 3: Ignoring mixed versions. v2 API response shape breaks v1 frontend calls in flight.
✅ Correct: Backward-compatible APIs; version your endpoints; deploy DB changes first.

❌ Mistake 4: `failure_action: pause` unattended, so a half-updated service stays inconsistent.
✅ Correct: Use `rollback` plus alerts.

❌ Mistake 5: No graceful shutdown, so each replacement drops in-flight requests.
✅ Correct: SIGTERM handler and adequate `stop_grace_period`.

---

## 🧠 Tricky Interview Question
**Q:** During a rolling update from v1 to v2 your users randomly see errors like "unknown field" and logout loops, but both versions pass their tests individually. Why?

**Answer:** During rollout a single user's consecutive requests can hit v1 and v2 alternately (no sticky version). If v2 changed the session format, token structure, cache keys or API contract, v1 cannot read what v2 wrote and vice versa. Each version is correct alone, but not compatible with the other. Fix: make every change backward and forward compatible for one release (two-phase deploy: first release reads both formats, next release starts writing the new one), use versioned cache keys, and consider canary or blue-green with session pinning if compatibility is impossible.

---

## ⚫ Interview Questions + Answers

Q1: What does `order: start-first` do?
A1: Starts the new task before stopping the old one, avoiding a capacity dip. `stop-first` (default) stops the old task first.

Q2: Rolling vs recreate strategy?
A2: Recreate stops everything then starts new: simple, with downtime. Rolling replaces gradually without downtime.

Q3: How does Kubernetes do rolling updates?
A3: Deployment `strategy.rollingUpdate` with `maxSurge` and `maxUnavailable`; readiness probes gate progress; `kubectl rollout undo` reverts.

Q4: How to pause or undo?
A4: Swarm: `docker service rollback`, K8s: `kubectl rollout pause|undo`. Always keep previous image tags in the registry.

Q5: How do you minimise request loss on each replacement?
A5: Readiness gating, SIGTERM handling, graceful drain, load balancer deregistration delay, and `proxy_next_upstream` retries for idempotent requests.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several replicas of a stateless service
- Limited spare capacity (cheaper than blue-green)
- Backward-compatible releases

❌ Avoid when:
- Single replica (rolling = restart; consider blue-green)
- Breaking changes that cannot coexist with the old version
- You need instant full rollback with zero mixed-version exposure

---

## 📊 Visual Diagram
```
 time ->  t0        t1        t2        t3        t4
 api-1    v1        v2(new)   v2        v2        v2
 api-2    v1        v1        v2(new)   v2        v2
 api-3    v1        v1        v1        v2(new)   v2
 api-4    v1        v1        v1        v1        v2(new)
          |         |
          |         +-- start-first: new healthy -> then old stops
 Traffic always served by at least N healthy replicas.
 Failure at any step -> pause / automatic rollback.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Rolling update | Gradual replacement | धीरे-धीरे बदलाव |
| Parallelism | Replicas updated at once | एक बार में कितनी replicas |
| start-first | New before old | पहले नया |
| failure_action | What to do on failure | Failure पर क्या करें |
| monitor | Watch time per new task | नए task की निगरानी का समय |
| maxSurge | Extra pods allowed (K8s) | अतिरिक्त pods की सीमा |

---

## ⚡ 3-Line Summary
English: Rolling updates replace replicas gradually, keeping the service up with little extra capacity.
Health checks, graceful shutdown and automatic rollback make it safe.
Both versions run together, so changes must be backward compatible.

Hindi: Rolling update replicas को धीरे-धीरे बदलता है, कम extra capacity में service चालू रहती है।
Health checks, graceful shutdown और automatic rollback इसे सुरक्षित बनाते हैं।
दोनों versions साथ चलते हैं, इसलिए बदलाव backward compatible हों।

---

## ➡️ Next Topic
**230. Canary Deployment with Docker** - send only a small percentage of real users to the new version first and increase slowly.
