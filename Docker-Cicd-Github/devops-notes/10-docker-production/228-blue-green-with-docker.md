# 228. Blue-Green with Docker
# हिंदी में: Docker के साथ Blue-Green Deployment

---

## 🔵 Simple Definition (English)
**Blue-green deployment** keeps two identical production environments: **blue** (currently live) and **green** (idle). You deploy the new version to green, test it, then switch the router (Nginx) from blue to green in one step. If something breaks, switch back. With Docker on a VPS this is two Compose projects (or two containers) and an Nginx upstream you flip.

## 🔵 सरल परिभाषा (Hindi)
**Blue-green deployment** में दो एक जैसे production environments रहते हैं: **blue** (अभी live) और **green** (खाली)। नया version green पर deploy करो, test करो, फिर router (Nginx) को blue से green पर एक ही कदम में switch करो। कुछ गड़बड़ हो तो वापस switch कर दो। VPS पर Docker के साथ यह दो Compose projects (या दो containers) और एक Nginx upstream है जिसे आप पलटते हो।

---

## 🔴 Problem it Solves
Plain `docker compose up -d` recreates the container: during that time (seconds) requests fail, and if the new version is broken you are already down and must rebuild the old one under pressure. Blue-green gives zero-downtime releases, a tested new version before any user sees it, and instant rollback (the old version is still running, just not receiving traffic).

## 🔴 यह क्यों बना? (Hindi)
साधारण `docker compose up -d` container दोबारा बनाता है: उस दौरान (कुछ सेकंड) requests fail होती हैं, और नया version टूटा हो तो आप पहले से down हो और दबाव में पुराना वापस बनाना पड़ता है। Blue-green zero-downtime release देता है, किसी user के देखने से पहले नए version की testing, और instant rollback (पुराना version चल रहा है, बस traffic नहीं ले रहा)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Blue (v1) serves 100% traffic. Nginx upstream points to blue:3000.
Step 2 → Start green (v2) next to it with the new image. It gets no public traffic.
Step 3 → Wait for green health check = healthy. Run smoke tests directly on green (e.g. localhost:3002).
Step 4 → Switch: rewrite the Nginx upstream to green and `nginx -s reload` (graceful, no dropped connections).
Step 5 → Watch errors/latency for some minutes. Blue stays running as the rollback target.
Step 6 → If bad: point Nginx back to blue (seconds). If good: stop blue; green becomes the new "blue".
Caveat → Database must be compatible with both versions (expand-contract migrations).
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Blue (v1) 100% traffic दे रहा है। Nginx upstream blue:3000 पर है।
Step 2 → Green (v2) को नई image के साथ बगल में start करो। उसे public traffic नहीं मिलता।
Step 3 → Green health check = healthy होने तक रुको। Green पर सीधे smoke tests चलाओ (जैसे localhost:3002)।
Step 4 → Switch: Nginx upstream green पर करो और `nginx -s reload` (graceful, connections नहीं गिरते)।
Step 5 → कुछ मिनट errors/latency देखो। Blue rollback target के रूप में चलता रहता है।
Step 6 → खराब हो तो Nginx को वापस blue पर करो (सेकंड)। ठीक हो तो blue बंद करो; green नया "blue" बन जाता है।
Caveat → Database दोनों versions के साथ compatible होना चाहिए (expand-contract migrations)।
```

---

## 🟡 Real World Example
An online exam platform cannot have downtime during a test window. They run blue and green Node.js containers on one EC2 host with Nginx in front. Release night: deploy v2 to green, run a smoke script (login, start exam, submit), flip Nginx at 10:05. At 10:09 error rate climbs because of a missing index; they flip back to blue in 5 seconds, students barely notice, and fix v2 calmly. Large companies do the same at load-balancer level (AWS ALB target groups, CodeDeploy blue/green for ECS).

## 🟡 Real Example Hindi mein
एक online exam platform test window में downtime नहीं झेल सकता। वे एक EC2 host पर आगे Nginx के साथ blue और green Node.js containers चलाते हैं। Release की रात: v2 green पर deploy, smoke script (login, exam शुरू, submit), 10:05 पर Nginx flip। 10:09 पर missing index से error rate बढ़ा; 5 सेकंड में blue पर वापस flip, students को लगभग पता नहीं चला, और v2 आराम से ठीक किया। बड़ी companies यही load-balancer level पर करती हैं (AWS ALB target groups, ECS के लिए CodeDeploy blue/green)।

---

## 💻 Code / Config Example — Basic

```nginx
# /etc/nginx/conf.d/active_upstream.conf - the only file the deploy script changes
upstream app_active {              # name used by the main server block
    server 127.0.0.1:3001;         # BLUE container published on host port 3001
}
```

```nginx
# /etc/nginx/conf.d/app.conf - main site config (does not change between deploys)
server {
    listen 80;                                  # HTTP port (add 443 + TLS in real life)
    server_name example.com;                    # your domain
    location / {
        proxy_pass http://app_active;           # forward to the active color
        proxy_set_header Host $host;            # keep original Host header
        proxy_set_header X-Real-IP $remote_addr; # pass client IP to the app
    }
}
```

```bash
# Manual flip: green is on 3002, make it live
sed -i 's/127.0.0.1:3001/127.0.0.1:3002/' /etc/nginx/conf.d/active_upstream.conf   # change the upstream port
nginx -t && nginx -s reload                     # validate config, then graceful reload (old workers finish requests)
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.bluegreen.yml - two colors from ONE file, selected by project name and env vars
# blue :  COLOR=blue  PORT=3001 TAG=sha-old  docker compose -p app-blue  -f docker-compose.bluegreen.yml up -d
# green:  COLOR=green PORT=3002 TAG=sha-new  docker compose -p app-green -f docker-compose.bluegreen.yml up -d
services:
  api:
    image: ghcr.io/myorg/node-api:${TAG}        # image tag for this color
    environment:
      APP_COLOR: ${COLOR}                       # shown in /version so you can verify who answers
    ports:
      - "127.0.0.1:${PORT}:3000"                # bind to localhost only; Nginx is the public door
    healthcheck:
      test: ["CMD", "wget", "-q", "-O-", "http://127.0.0.1:3000/readyz"]  # readiness probe
      interval: 5s                              # fast checks for deploys
      timeout: 3s                               # max wait
      retries: 5                                # failures before unhealthy
      start_period: 20s                         # warm-up
    stop_grace_period: 30s                      # graceful shutdown time
    restart: unless-stopped                     # survive reboots
```

```bash
#!/usr/bin/env bash
# deploy-bluegreen.sh <new-image-tag>  - zero-downtime switch with automatic rollback
set -euo pipefail                                        # stop on any error

NEW_TAG=$1                                               # image tag to release
UPSTREAM=/etc/nginx/conf.d/active_upstream.conf          # file Nginx includes
CURRENT_PORT=$(grep -oE '[0-9]{4}' "$UPSTREAM" | head -1) # 3001 or 3002

if [ "$CURRENT_PORT" = "3001" ]; then                    # decide the idle color
  OLD=blue;  OLD_PORT=3001; NEW=green; NEW_PORT=3002
else
  OLD=green; OLD_PORT=3002; NEW=blue;  NEW_PORT=3001
fi
echo "live=$OLD:$OLD_PORT  deploying to $NEW:$NEW_PORT"  # log intent

COLOR=$NEW PORT=$NEW_PORT TAG=$NEW_TAG \
  docker compose -p "app-$NEW" -f docker-compose.bluegreen.yml up -d --pull always   # start idle color with new image

for i in $(seq 1 30); do                                 # wait up to 60s for readiness
  if curl -fsS "http://127.0.0.1:$NEW_PORT/readyz" >/dev/null; then break; fi   # healthy -> continue
  [ "$i" = 30 ] && { echo "new color unhealthy, aborting"; docker compose -p "app-$NEW" down; exit 1; }   # abort, live untouched
  sleep 2
done

curl -fsS "http://127.0.0.1:$NEW_PORT/" >/dev/null       # tiny smoke test (replace with real tests)

printf 'upstream app_active {\n    server 127.0.0.1:%s;\n}\n' "$NEW_PORT" > "$UPSTREAM"   # point Nginx to new color
nginx -t && nginx -s reload                              # validate and reload gracefully

sleep 60                                                 # observation window (watch your dashboards)
if ! curl -fsS "http://127.0.0.1/readyz" >/dev/null; then   # post-switch check through Nginx
  printf 'upstream app_active {\n    server 127.0.0.1:%s;\n}\n' "$OLD_PORT" > "$UPSTREAM"  # rollback config
  nginx -s reload                                        # rollback is instant
  echo "ROLLED BACK to $OLD"; exit 1
fi
docker compose -p "app-$OLD" down                        # retire old color (or keep it for a longer window)
echo "done: $NEW is live"
```

Checked: `bash -n` on the script and YAML parse; Nginx config not tested (`nginx` not installed here); containers not run. / Script `bash -n` और YAML parse हुआ; nginx और containers यहाँ नहीं चले।

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: same Compose file, ports 3001/3002 (or 8001/8002). Keep stateless; sessions in Redis or JWT so users do not lose login on flip.
- **Nginx on the VPS**: include `active_upstream.conf` as shown. The flip is `nginx -s reload`, which is graceful.
- **React**: static container behind the same Nginx, or switch an S3/CloudFront origin.
- **Database**: one shared PostgreSQL, never blue/green databases in a simple setup. Use backward-compatible migrations (add column first, remove later).
- **AWS**: ALB with two target groups; shift the listener rule weight 0 -> 100. ECS has native blue/green via CodeDeploy.
- **Cost**: during the switch you run 2x containers: size the VPS RAM for it (resource limits matter).

```yaml
# AWS ALB idea (described, not complete): two target groups, one listener rule
# aws elbv2 modify-listener --listener-arn <arn> \
#   --default-actions Type=forward,ForwardConfig='{"TargetGroups":[{"TargetGroupArn":"<green>","Weight":100},{"TargetGroupArn":"<blue>","Weight":0}]}'
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Incompatible DB migration (drop column) while blue still runs. Rollback then fails.
✅ Correct: Expand-contract: add new, deploy, migrate data, remove old in a later release.

❌ Mistake 2: Flipping without a health check, sending users to a booting container.
✅ Correct: Switch only after `readyz` passes and a smoke test succeeds.

❌ Mistake 3: `nginx -s restart` instead of reload; connections drop.
✅ Correct: `nginx -t && nginx -s reload`.

❌ Mistake 4: Exposing blue/green ports publicly (`0.0.0.0:3001`).
✅ Correct: Bind to `127.0.0.1`; only Nginx is public.

❌ Mistake 5: Stopping the old color immediately.
✅ Correct: Keep it for an observation window so rollback is instant.

---

## 🧠 Tricky Interview Question
**Q:** You switch traffic to green, then roll back to blue after 10 minutes. Some users are now logged out and a few orders are missing. What went wrong?

**Answer:** State was not shared or not compatible. If sessions lived in blue's memory, users lose login on every flip. If green wrote data in a new format (or a new column / enum value) that blue cannot read, blue misbehaves after rollback; orders created in the window may be mishandled. Blue-green only swaps stateless code. Fix: externalize sessions (Redis/JWT), make DB changes backward and forward compatible, use feature flags for risky behaviour, and treat the DB as a shared dependency that migrates separately.

---

## ⚫ Interview Questions + Answers

Q1: Blue-green vs rolling update?
A1: Blue-green switches all traffic at once between two full environments (fast rollback, double resources). Rolling replaces instances gradually (less resource, mixed versions during rollout, slower rollback).

Q2: Blue-green vs canary?
A2: Canary sends a small percentage of users to the new version first; blue-green is all-or-nothing, though you can test green before switching.

Q3: How do you handle database schema changes?
A3: Expand-contract pattern with backward-compatible migrations; run migrations before the switch; never drop or rename in the same release.

Q4: How do you implement it in Kubernetes?
A4: Two Deployments (`app-blue`, `app-green`) and a Service whose selector `version:` label you flip; or use Argo Rollouts blue/green strategy.

Q5: Downsides?
A5: Double resource cost during release, complex DB handling, long-lived connections (WebSockets) are cut at switch, and cache warm-up on the new side.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Zero downtime and instant rollback are required
- Stateless services and compatible database changes
- You have spare capacity on the host

❌ Avoid when:
- Host RAM cannot fit two copies
- Breaking schema changes with no compatibility plan
- You want gradual validation with real users (use canary)

---

## 📊 Visual Diagram
```
                     Users
                       |
                  +----v-----+
                  |  Nginx   |  upstream app_active
                  +----+-----+
          before ------|------ after flip
        +--------------+----------------+
        v                               v
  +------------+                  +------------+
  | BLUE  v1   |  <-- live        | GREEN v2   |  <-- live
  | :3001      |  (kept 10 min    | :3002      |  tested first,
  +------+-----+   for rollback)  +------+-----+  then flipped
         \_____________  ____________/
                       v
              Shared PostgreSQL / Redis (compatible schema)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Blue | Currently live version | अभी live version |
| Green | New version, idle until switch | नया version, switch तक idle |
| Cutover | Moment of traffic switch | Traffic switch का क्षण |
| Rollback | Return to previous version | पिछले version पर वापसी |
| Expand-contract | Safe DB change pattern | सुरक्षित DB बदलाव पैटर्न |
| Upstream | Backend group in Nginx | Nginx में backend group |

---

## ⚡ 3-Line Summary
English: Run new version beside the old one, test it, then flip Nginx to it.
Rollback is flipping back, so keep the old color alive for a while.
Share state externally and keep database changes backward compatible.

Hindi: नया version पुराने के बगल में चलाओ, test करो, फिर Nginx को उस पर flip करो।
Rollback यानी वापस flip, इसलिए पुराना color कुछ देर चलने दो।
State बाहर रखो और database बदलाव backward compatible रखो।

---

## ➡️ Next Topic
**229. Rolling Updates with Docker** - replacing instances one by one instead of two full environments, with less resource cost.
