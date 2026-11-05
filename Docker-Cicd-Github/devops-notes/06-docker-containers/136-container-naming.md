---

# 136. Container Naming
# हिंदी में: Container का नामकरण

---

## 🔵 Simple Definition (English)
Every container has a unique ID and a unique name. If you do not pass `--name`, Docker invents one (like `eager_turing`). A good name makes scripts, logs and DNS (on user-defined networks) predictable.

## 🔵 सरल परिभाषा (Hindi)
हर container का एक unique ID और एक unique नाम होता है। `--name` न दें तो Docker खुद नाम बनाता है (जैसे `eager_turing`)। अच्छा नाम scripts, logs और DNS (user-defined networks पर) को predictable बनाता है।

---

## 🔴 Problem it Solves
Long hex IDs (`3f4a9c1b2d7e`) are hard to remember and change on every recreate; random names tell you nothing about what runs inside. Scripts like `docker stop <something>` and Nginx upstreams need a stable handle. Naming also prevents accidentally starting two copies of the same service.

## 🔴 यह क्यों बना? (Hindi)
लंबे hex ID (`3f4a9c1b2d7e`) याद रखना मुश्किल है और हर recreate पर बदलते हैं; random नाम से पता नहीं चलता अंदर क्या चल रहा है। `docker stop <कुछ>` जैसी scripts और Nginx upstreams को स्थिर handle चाहिए। नाम से एक ही service की दो copies गलती से शुरू होना भी रुकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker run --name api ...    : dockerd checks the name is unused (names are unique per host)
Step 2 → Name stored in container metadata next to the long 64-char ID
Step 3 → Any command accepts name OR ID (or unique ID prefix): docker logs api
Step 4 → On user-defined networks, embedded DNS resolves "api" to the container IP
Step 5 → Without --name Docker picks adjective_scientist; Compose picks project-service-1
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker run --name api ... : dockerd जाँचता है नाम इस्तेमाल में तो नहीं (host पर unique)
Step 2 → नाम 64-अक्षर वाली ID के साथ metadata में सेव
Step 3 → हर command नाम, ID या ID का unique prefix मानती है: docker logs api
Step 4 → User-defined network पर embedded DNS "api" को container IP में बदलता है
Step 5 → --name न हो तो Docker adjective_scientist चुनता है; Compose project-service-1
```

---

## 🟡 Real World Example
Your deploy script on the VPS does `docker rm -f orders-api && docker run -d --name orders-api ...`. Because the name is fixed, the script is idempotent and Nginx/monitoring always point at `orders-api`. In a Swiggy-style multi-service setup, the order service reaches payments at `http://payments:8000`; "payments" is the service/container name resolved by Docker DNS, so no IPs are hardcoded.

## 🟡 Real Example Hindi mein
VPS पर आपकी deploy script `docker rm -f orders-api && docker run -d --name orders-api ...` चलाती है। नाम fixed है, इसलिए script idempotent है और Nginx/monitoring हमेशा `orders-api` पर इशारा करते हैं। Swiggy जैसे multi-service setup में order service `http://payments:8000` पर payments तक पहुँचती है; "payments" को Docker DNS resolve करता है, कोई IP hardcode नहीं।

---

## 💻 Code / Config Example — Basic
```bash
#!/usr/bin/env bash
# naming-basic.sh
docker run -d alpine:3.20 sleep 300                      # no --name: Docker generates a random name
docker ps --format '{{.ID}} {{.Names}}'                  # e.g. 3f4a9c1b2d7e  eager_turing
docker run -d --name worker alpine:3.20 sleep 300        # explicit name
docker run -d --name worker alpine:3.20 sleep 300        # FAILS: name "/worker" is already in use
docker rename worker worker-old                          # rename an existing container (works while running)
docker stop worker-old                                   # commands accept the name...
docker stop 3f4a                                         # ...or a unique prefix of the ID (use your real ID)
docker inspect -f '{{.Name}} {{.Id}}' worker-old         # show name + full 64-char ID
docker ps -aq | xargs -r docker rm -f                    # cleanup ALL containers (only on a throwaway machine!)
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# deploy.sh - idempotent deploy with convention-based names (example)
set -euo pipefail                                        # fail fast
APP=orders-api                                           # convention: service name
ENVIRONMENT=${ENVIRONMENT:-prod}                         # prod/staging
TAG=${1:?usage: deploy.sh <image-tag>}                   # require a tag argument
NAME="${APP}-${ENVIRONMENT}"                             # e.g. orders-api-prod

docker pull "myorg/${APP}:${TAG}"                        # fetch new image first (fail before touching old one)
if docker inspect "$NAME" >/dev/null 2>&1; then          # does a container with this name exist?
  docker rename "$NAME" "${NAME}-old"                    # keep old one as instant rollback target
  docker stop -t 30 "${NAME}-old"                        # graceful stop
fi
docker run -d --name "$NAME" \
  --label app="$APP" --label env="$ENVIRONMENT" --label tag="$TAG" \
  --network backend --restart unless-stopped \
  -p 127.0.0.1:3000:3000 \
  "myorg/${APP}:${TAG}"                                  # start the new version under the stable name
docker rm "${NAME}-old" 2>/dev/null || true              # drop old one (omit this line if you want manual rollback window)
docker ps --filter "label=app=${APP}" --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'   # verify via labels
```
```yaml
# docker-compose.yml - naming in Compose
name: shop                          # project name => containers named shop-<service>-<index>
services:
  api:
    image: myorg/orders-api:1.4.2   # example tag
    # no container_name: lets Compose scale with `--scale api=3` (names shop-api-1, -2, -3)
  db:
    image: postgres:16-alpine       # example tag
    container_name: shop-db         # fixed name: OK for a singleton, but blocks scaling of this service
    hostname: db                    # hostname inside the container
```

---

## 🟠 My Stack Integration
**Node.js / FastAPI**: connect to dependencies by name: `postgres://app@db:5432/orders`, `http://payments:8000`. These only resolve on user-defined networks (not the default `bridge`).
**React/Nginx**: upstream `server orders-api:3000;` in a Dockerized Nginx on the same network.
**VPS**: use `NAME-env` conventions, add `--label` for filtering and for tools like Prometheus/cAdvisor.
**AWS**: ECS tasks name containers in the task definition; ECS service discovery/Cloud Map gives DNS names similar to Docker names.

```nginx
# nginx.conf inside a container on the same network (not tested here)
upstream api { server orders-api:3000; }   # resolved by Docker DNS at Nginx start
server {
  listen 80;                                # web port inside the container
  location /api/ { proxy_pass http://api; } # forward API calls to the named container
}
```
**Security**: names are not secrets, but predictable names are fine; never put credentials or customer data in names or labels (they are visible in `docker ps`).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Re-running `docker run --name x` without removing the old container.
✅ Correct: `docker rm -f x` first, or use `docker compose up -d` which recreates safely.

❌ Mistake 2: `container_name:` on services you want to scale.
✅ Correct: omit it; let Compose generate names.

❌ Mistake 3: Expecting name-based DNS on the default bridge network.
✅ Correct: create a user-defined network (`docker network create`), or use Compose.

❌ Mistake 4: Nginx caches the container IP at startup; after the API is recreated it gets a new IP and Nginx gives 502.
✅ Correct: use Docker's resolver (`resolver 127.0.0.11;` with a variable in `proxy_pass`) or reload Nginx after deploys.

❌ Mistake 5: Using `--name` with `docker rename` ids in scripts that expect the old name.
✅ Correct: pick one convention and keep it.

---

## 🧠 Tricky Interview Question
Why can't two containers on the same host have the same name even if one is stopped?

Answer: Names are reserved for as long as the container exists, in any state, because the name maps to the container record, not to a running process. A stopped container named `web` still blocks `--name web`. You must `docker rm` it (or `rename` it) first. This is why `--rm` or cleanup steps matter in deploy scripts.

---

## ⚫ Interview Questions + Answers

Q1: How does Docker name containers by default?
A1: Randomly from adjective_surname (e.g. `eager_turing`); Compose uses `project-service-number`.

Q2: Can I use a name instead of an ID in commands?
A2: Yes, names, full IDs and unique ID prefixes all work.

Q3: Can you rename a running container?
A3: Yes, `docker rename old new`, with no restart.

Q4: Does container name equal DNS name?
A4: On user-defined networks yes (plus network aliases and Compose service names). On the default bridge there is no automatic DNS.

Q5: Why avoid `container_name` in Compose?
A5: It prevents scaling (`--scale`) and can clash between projects on the same host.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Single-instance services, deploy scripts, monitoring targets.
- Giving humans and tools a stable handle.

❌ Avoid when:
- Services you plan to scale horizontally.
- Many projects share one host (name collisions): rely on Compose project names.

---

## 📊 Visual Diagram
```
 docker run --name orders-api IMAGE
          |
          v
 +---------------------------------------------+
 | ID   : 3f4a9c1b2d7e... (64 hex, changes)    |
 | NAME : orders-api      (unique, stable)     |
 +---------------------------------------------+
          |                        |
   docker logs orders-api     Docker DNS (network "backend")
                              payments --> "http://orders-api:3000" -> 172.18.0.3
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Container ID | 64-char unique hash | 64 अक्षर की unique पहचान |
| Name | Human-friendly unique label | इंसानों के लिए नाम |
| Label | Key-value metadata for filtering | Filter के लिए metadata |
| Embedded DNS | Docker resolver at 127.0.0.11 | Docker का अपना DNS |
| Project name | Compose prefix | Compose का prefix |

---

## ⚡ 3-Line Summary
English: Names are unique handles for containers; without `--name` Docker makes a random one.
Names stay reserved until the container is removed, and double as DNS names on user-defined networks.
Use conventions plus labels, and skip `container_name` for scalable services.

Hindi: Names container के unique handle हैं; `--name` न दें तो Docker random नाम बनाता है।
Container remove होने तक नाम reserved रहता है, और user-defined networks पर DNS नाम भी है।
Conventions और labels इस्तेमाल करें, और scale होने वाली services में `container_name` न दें।

---

## ➡️ Next Topic
**137. Container Restart Policies**: names let you find a container; restart policies decide whether it comes back after crashes and reboots.
