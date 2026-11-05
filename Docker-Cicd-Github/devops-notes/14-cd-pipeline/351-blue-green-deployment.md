# 351. Blue-Green Deployment
# हिंदी में: Blue-Green Deployment

---

## 🔵 Simple Definition (English)
Blue-green deployment keeps two identical production environments. "Blue" serves live traffic while you deploy the new version to "green". After testing green, you switch the router (Nginx or a load balancer) to green. If something breaks, you switch back to blue in seconds.

## 🔵 सरल परिभाषा (Hindi)
Blue-green deployment में दो एक जैसे production environments रखे जाते हैं। "Blue" live traffic देता है और नया version "green" पर deploy होता है। Green test होने के बाद router (Nginx या load balancer) को green पर switch कर देते हैं। कुछ गड़बड़ हो तो सेकंडों में वापस blue पर आ जाते हैं।

---

## 🔴 Problem it Solves
In-place deploys stop the old container and start the new one, causing downtime, and if the new version is broken you must rebuild the old one to roll back. Users see errors during the gap, and rollback is slow and stressful.

## 🔴 यह क्यों बना? (Hindi)
In-place deploy में पुराना container बंद करके नया शुरू करते हैं, जिससे downtime होता है, और नया version खराब निकले तो rollback के लिए पुराना फिर से बनाना पड़ता है। उस gap में users को errors दिखते हैं और rollback धीमा और तनाव भरा होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Blue (v1) is live; Nginx upstream points to blue port 8001
Step 2 → Deploy v2 to green on port 8002 (blue is untouched)
Step 3 → Run smoke tests and health checks directly against green
Step 4 → Switch Nginx upstream to green and reload (no dropped connections)
Step 5 → Watch errors and latency for a few minutes
Step 6 → Keep blue idle as the instant rollback target
Step 7 → Later stop blue; next release deploys to blue (roles swap)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Blue (v1) live है; Nginx upstream blue के port 8001 पर है
Step 2 → v2 को green (port 8002) पर deploy करो (blue को छुआ नहीं)
Step 3 → Green पर सीधे smoke tests और health checks चलाओ
Step 4 → Nginx upstream green पर बदलो और reload करो (connections नहीं टूटते)
Step 5 → कुछ मिनट errors और latency देखो
Step 6 → Blue को instant rollback target के रूप में चालू रखो
Step 7 → बाद में blue बंद करो; अगला release blue पर जाएगा (roles बदलते हैं)
```

---

## 🟡 Real World Example
An e-commerce company releases right before a sale. A bad release at 9 AM would cost lakhs per minute. They deploy v2 to green, run a checkout smoke test against green's private port, and flip traffic. At 9:04 error rates rise because of a payment SDK bug; they flip back to blue in 10 seconds. Customers barely notice. Netflix, Amazon and many Indian fintechs use this idea with load balancers.

## 🟡 Real Example Hindi mein
एक e-commerce company sale से ठीक पहले release करती है। सुबह 9 बजे खराब release से हर मिनट लाखों का नुकसान होता। वे v2 को green पर deploy करते हैं, green के private port पर checkout smoke test चलाते हैं और traffic flip करते हैं। 9:04 पर payment SDK bug से errors बढ़ते हैं; वे 10 सेकंड में वापस blue पर flip कर देते हैं। Customers को लगभग पता भी नहीं चलता।

---

## 💻 Code / Config Example — Basic

```nginx
# /etc/nginx/conf.d/upstream-active.conf
# This single file decides which color is live.
upstream app_backend {
    server 127.0.0.1:8001;    # BLUE is live now (change to 8002 for GREEN)
}
```

```nginx
# /etc/nginx/conf.d/app.conf
server {
    listen 80;                          # HTTP (add TLS in production)
    server_name app.example.com;        # your domain
    location / {
        proxy_pass http://app_backend;  # send traffic to the active upstream
        proxy_set_header Host $host;    # keep the host header
        proxy_set_header X-Forwarded-For $remote_addr;
    }
}
```

```bash
# switch.sh - basic manual switch from blue to green
set -e                                                       # stop on error
sudo sed -i 's/8001/8002/' /etc/nginx/conf.d/upstream-active.conf   # point to green
sudo nginx -t                                                # validate config first
sudo nginx -s reload                                         # graceful reload
```

## 💻 Code / Config Example — Advanced

```yaml
# /srv/myapp/docker-compose.bluegreen.yml
# Two copies of the API; only one receives traffic via Nginx.
services:
  api-blue:
    image: ${BLUE_IMAGE}                     # current live image
    restart: unless-stopped                  # auto-restart
    env_file: .env                           # shared secrets/config
    ports:
      - "127.0.0.1:8001:8000"                # blue on host port 8001
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/health')"]
      interval: 5s                           # check frequently
      retries: 5
  api-green:
    image: ${GREEN_IMAGE}                    # new candidate image
    restart: unless-stopped
    env_file: .env
    ports:
      - "127.0.0.1:8002:8000"                # green on host port 8002
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/health')"]
      interval: 5s
      retries: 5
```

```bash
#!/usr/bin/env bash
# /srv/myapp/bluegreen.sh - usage: ./bluegreen.sh <new-image>
set -euo pipefail                                   # strict mode
cd /srv/myapp                                       # project directory
NEW_IMAGE="$1"                                      # image tag to release
CONF=/etc/nginx/conf.d/upstream-active.conf         # file that holds active port

# detect which color is live from the upstream file
if grep -q '8001' "$CONF"; then LIVE=blue; IDLE=green; IDLE_PORT=8002; IDLE_VAR=GREEN_IMAGE
else LIVE=green; IDLE=blue; IDLE_PORT=8001; IDLE_VAR=BLUE_IMAGE; fi
echo "live=$LIVE idle=$IDLE"

# start the idle color with the new image
export "$IDLE_VAR=$NEW_IMAGE"                       # BLUE_IMAGE or GREEN_IMAGE
export BLUE_IMAGE="${BLUE_IMAGE:-$NEW_IMAGE}"       # make compose happy for the other var
export GREEN_IMAGE="${GREEN_IMAGE:-$NEW_IMAGE}"
docker compose -f docker-compose.bluegreen.yml pull "api-$IDLE"
docker compose -f docker-compose.bluegreen.yml up -d "api-$IDLE"

# smoke test the idle color directly (not through public Nginx)
for i in $(seq 1 20); do
  if curl -fsS "http://127.0.0.1:${IDLE_PORT}/health" >/dev/null; then OK=1; break; fi
  sleep 3
done
[ "${OK:-0}" = "1" ] || { echo "idle failed health check, aborting"; docker compose -f docker-compose.bluegreen.yml stop "api-$IDLE"; exit 1; }

# keep a backup of the current upstream file for fast rollback
sudo cp "$CONF" "$CONF.prev"
# write the new upstream
printf 'upstream app_backend {\n    server 127.0.0.1:%s;\n}\n' "$IDLE_PORT" | sudo tee "$CONF" >/dev/null
# validate; restore on error
sudo nginx -t || { sudo cp "$CONF.prev" "$CONF"; exit 1; }
sudo nginx -s reload                                # graceful switch
echo "switched to $IDLE. rollback: cp $CONF.prev $CONF && nginx -s reload"
```

```yaml
# .github/workflows/bluegreen.yml (deploy step only)
name: Blue-Green Deploy
on:
  workflow_dispatch:                # run manually or call from the main pipeline
    inputs:
      image:
        description: "Image tag to release"
        required: true
jobs:
  switch:
    runs-on: ubuntu-latest
    environment: production         # gate with required reviewers if wanted
    steps:
      - uses: appleboy/ssh-action@v1.0.3      # example version
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: /srv/myapp/bluegreen.sh "${{ inputs.image }}"
```

---

## 🟠 My Stack Integration
On a single VPS you can run blue and green as two containers on different local ports and flip Nginx between them, as above. On AWS use an Application Load Balancer with two target groups (blue, green) and shift the listener rule; ECS and CodeDeploy automate this. The database is shared, so schema changes must work for both versions at once (see 355).

```nginx
# Optional: a private route to test green before switching
server {
    listen 127.0.0.1:8081;                  # reachable only from the server itself
    location / { proxy_pass http://127.0.0.1:8002; }   # always green
}
```

Security: bind both colors to `127.0.0.1`, keep the test route private, restrict who can trigger the workflow (environment reviewers), and keep `.env` permission at 600.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Incompatible database migration (dropping a column the blue version still uses).
✅ Correct: Use expand/contract migrations so both versions work on the same schema.

❌ Mistake 2: Switching without testing green first.
✅ Correct: Health check and smoke test the idle color directly before the flip.

❌ Mistake 3: `nginx -s reload` without `nginx -t`.
✅ Correct: Always validate; a typo can leave Nginx on the old config or fail.

❌ Mistake 4: Stopping blue immediately.
✅ Correct: Keep blue running for a rollback window (for example 30 minutes).

❌ Mistake 5: Sticky data in memory (sessions in process) lost at the switch.
✅ Correct: Store sessions in Redis or a database shared by both colors.

---

## 🧠 Tricky Interview Question
Blue-green gives instant rollback, but the new version already ran a migration that added a NOT NULL column. Can you still roll back safely?

Answer: Not necessarily. The old code does not know the new column and its inserts will fail on NOT NULL. That is why you add columns as nullable (or with a default) first, deploy code, and only enforce constraints in a later release. The rollback speed of blue-green is only as good as the database compatibility.

---

## ⚫ Interview Questions + Answers

Q1: What is the main advantage over rolling deployment?
A1: Instant, atomic switch and instant rollback, with the new version fully tested before it gets real traffic.

Q2: What is the main cost?
A2: Double the infrastructure during the release, and the extra work of keeping the shared database compatible.

Q3: How is it different from canary?
A3: Blue-green switches all traffic at once; canary sends a small percentage first and increases gradually.

Q4: How does Nginx reload avoid dropped requests?
A4: `reload` starts new workers with the new config and lets old workers finish in-flight requests before exiting.

Q5: How do you do it on AWS?
A5: ALB with two target groups, or ECS/CodeDeploy blue-green; shift the listener weight to the new group and keep the old group for rollback.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Downtime is costly and you need fast rollback.
- You can afford a second copy of the service.

❌ Avoid when:
- The service holds heavy local state that cannot be shared.
- Resources are tight and a rolling update on several replicas is enough.

---

## 📊 Visual Diagram
```
                    +--> BLUE  (v1) :8001   <-- live now
 Users --> Nginx ---|
        (upstream)  +--> GREEN (v2) :8002   <-- deployed, tested, idle
                            |
          after test: flip upstream to 8002, reload
                            |
 Users --> Nginx ----------> GREEN (v2)  ;  BLUE kept for instant rollback
                  both colors share ONE database (schema must fit both)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Blue/Green | Two identical environments | दो एक जैसे environments |
| Cutover | Moment traffic is switched | traffic बदलने का क्षण |
| Smoke test | Quick check of critical paths | ज़रूरी paths की जल्दी जाँच |
| Target group | AWS ALB set of backends | ALB के backends का समूह |
| Expand/contract | Backward-compatible schema changes | पीछे-संगत schema बदलाव |

---

## ⚡ 3-Line Summary
English: Run new code on an idle copy, test it, then flip traffic with a router reload.
Keep the old copy for instant rollback during a window.
Make database changes backward compatible because both versions share the data.
Hindi: नया code idle copy पर चलाओ, test करो, फिर router reload से traffic flip करो।
Rollback के लिए पुरानी copy कुछ देर चालू रखो।
Database बदलाव backward compatible रखो क्योंकि दोनों versions एक ही data share करते हैं।

---

## ➡️ Next Topic
**352. Canary Deployment** — release to a small slice of users first and expand only if metrics stay healthy.
