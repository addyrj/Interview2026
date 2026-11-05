---

# 128. Private Registry Setup
# हिंदी में: Private Registry सेटअप (अपना खुद का Image Store)

---

## 🔵 Simple Definition (English)
A **private registry** is your own server that stores and serves Docker images, so only people and machines you allow can push or pull them. The open-source `registry:2` image (Docker Distribution) is the simplest way to run one on a VPS, with TLS and basic authentication in front of it.

## 🔵 सरल परिभाषा (Hindi)
**Private registry** आपका अपना server है जो Docker images store और serve करता है, ताकि सिर्फ़ वही लोग और machines push/pull कर सकें जिन्हें आप allow करें। Open-source `registry:2` image (Docker Distribution) VPS पर इसे चलाने का सबसे आसान तरीका है, जिसके आगे TLS और basic authentication लगाया जाता है।

---

## 🔴 Problem it Solves
Docker Hub free tier has pull rate limits and public repos expose your code. Private repos on SaaS registries cost money per seat or storage. Some companies cannot let images leave their network (banking, healthcare, air-gapped servers). Without a private registry, teams copy images with `docker save | scp | docker load`, which is slow, unversioned and error-prone.

## 🔴 यह क्यों बना? (Hindi)
Docker Hub के free tier में pull rate limit है और public repos में आपका code खुला रहता है। SaaS registries के private repos पर seat या storage के हिसाब से पैसा लगता है। कुछ companies (bank, hospital, air-gapped servers) images को अपने network से बाहर जाने ही नहीं दे सकतीं। Private registry न हो तो लोग `docker save | scp | docker load` करते हैं, जो धीमा, बिना versioning का और error-prone है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Point a DNS name (registry.example.com) at your VPS
Step 2 → Run registry:2 container, store layers in a named volume
Step 3 → Create an htpasswd file (bcrypt) for users
Step 4 → Put Nginx (or registry's own TLS) in front, get a Let's Encrypt cert
Step 5 → docker login registry.example.com  (credentials saved in ~/.docker/config.json)
Step 6 → docker tag app:1.0 registry.example.com/app:1.0 ; docker push ...
Step 7 → Other servers: docker pull registry.example.com/app:1.0
Step 8 → Run garbage collection regularly, because deleted tags still leave blobs on disk
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → DNS name (registry.example.com) अपने VPS की IP पर point करो
Step 2 → registry:2 container चलाओ, layers एक named volume में रखो
Step 3 → Users के लिए htpasswd file (bcrypt) बनाओ
Step 4 → आगे Nginx (या registry का अपना TLS) लगाओ, Let's Encrypt cert लो
Step 5 → docker login registry.example.com  (credentials ~/.docker/config.json में save होते हैं)
Step 6 → docker tag app:1.0 registry.example.com/app:1.0 ; फिर docker push
Step 7 → दूसरे servers पर: docker pull registry.example.com/app:1.0
Step 8 → Garbage collection नियमित चलाओ, क्योंकि tag delete करने पर भी blobs disk पर रहते हैं
```

---

## 🟡 Real World Example
A fintech startup in Bengaluru runs 12 microservices on three VPS machines. Their CI builds images on GitHub Actions and must deploy to servers inside a private VPC that can only reach one internal host. They run `registry:2` on a small VPS behind Nginx with TLS, pushing from CI with a robot account. Production servers pull over the private network, no Docker Hub limit, no image ever leaves the company, and the monthly cost is the price of one 2 GB VPS plus a 50 GB disk.

## 🟡 Real Example Hindi mein
Bengaluru का एक fintech startup तीन VPS पर 12 microservices चलाता है। CI GitHub Actions पर images बनाता है और उन्हें private VPC के servers पर deploy करना है जो सिर्फ़ एक internal host तक पहुँच सकते हैं। वे एक छोटे VPS पर Nginx + TLS के पीछे `registry:2` चलाते हैं, CI एक robot account से push करता है। Production servers private network से pull करते हैं, Docker Hub limit नहीं, image company से बाहर नहीं जाती, और खर्च सिर्फ़ एक 2 GB VPS और 50 GB disk का है।

---

## 💻 Code / Config Example — Basic

```bash
# Quick test registry on localhost (no TLS, no auth: only for learning)
docker run -d \
  --name registry \
  -p 127.0.0.1:5000:5000 \
  -v registry-data:/var/lib/registry \
  --restart unless-stopped \
  registry:2
# -d runs in background; name makes it easy to manage
# 127.0.0.1 binding keeps the port off the public internet
# named volume keeps the image layers when the container is replaced
# registry:2 is the official Distribution image (pin a patch tag in real use)

# Tag an existing image so its name carries the registry host:port
docker tag node-api:1.0 localhost:5000/node-api:1.0

# Push it to the local registry
docker push localhost:5000/node-api:1.0

# List repositories via the registry HTTP API v2
curl -s http://localhost:5000/v2/_catalog

# List tags of one repository
curl -s http://localhost:5000/v2/node-api/tags/list

# Pull it back (after removing the local copy) to prove it works
docker rmi localhost:5000/node-api:1.0
docker pull localhost:5000/node-api:1.0
```

Note: Docker treats `localhost` registries as secure by default, so plain HTTP works only there. Any other host needs HTTPS.

## 💻 Code / Config Example — Advanced

Production layout: registry (basic auth, delete enabled) behind Nginx with TLS.

```yaml
# docker-compose.registry.yml
# Private registry + Nginx TLS front. Image tags are examples: update them.
services:
  registry:
    image: registry:2.8.3                       # pinned example tag, check for newer
    restart: unless-stopped                     # come back after reboot or crash
    environment:
      REGISTRY_STORAGE_DELETE_ENABLED: "true"   # allow API deletes so GC can reclaim space
      REGISTRY_AUTH: htpasswd                   # use htpasswd authentication
      REGISTRY_AUTH_HTPASSWD_REALM: "Private Registry"  # realm string shown in 401 header
      REGISTRY_AUTH_HTPASSWD_PATH: /auth/htpasswd       # file inside the container
      REGISTRY_HTTP_ADDR: 0.0.0.0:5000          # listen on all container interfaces
    volumes:
      - registry-data:/var/lib/registry         # image layers and manifests live here
      - ./auth:/auth:ro                         # htpasswd file mounted read-only
    networks:
      - regnet                                  # private network shared with nginx only
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:5000/v2/"]  # 200 or 401 both mean alive
      interval: 30s                             # check every 30 seconds
      timeout: 5s                               # fail if no answer in 5 seconds
      retries: 3                                # unhealthy after 3 failures

  nginx:
    image: nginx:1.27-alpine                    # reverse proxy that terminates TLS
    restart: unless-stopped                     # keep proxy up
    ports:
      - "443:443"                               # only HTTPS is exposed publicly
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro   # proxy config
      - /etc/letsencrypt:/etc/letsencrypt:ro    # certificates from certbot on the host
    depends_on:
      - registry                                # start registry first
    networks:
      - regnet                                  # reach registry by service name

volumes:
  registry-data: {}                             # named volume managed by Docker

networks:
  regnet: {}                                    # default bridge network for these two
```

```bash
# Create the htpasswd file (bcrypt, -B) using the httpd image so no tools are needed on host
mkdir -p auth                                   # folder that compose mounts
docker run --rm --entrypoint htpasswd httpd:2 -Bbn ci-bot 'S3cretPass!' > auth/htpasswd
# --rm deletes helper container; -B bcrypt; -b password on command line; -n print to stdout

# Garbage collect unreferenced blobs (run in maintenance window)
docker compose -f docker-compose.registry.yml exec registry \
  registry garbage-collect /etc/docker/registry/config.yml --delete-untagged
# --delete-untagged also removes manifests with no tag (flag exists in Distribution 2.x)
```

```nginx
# nginx.conf (mounted as conf.d/default.conf)
server {
    listen 443 ssl;                                  # HTTPS only
    server_name registry.example.com;                # your registry hostname
    ssl_certificate     /etc/letsencrypt/live/registry.example.com/fullchain.pem;  # cert chain
    ssl_certificate_key /etc/letsencrypt/live/registry.example.com/privkey.pem;    # private key
    client_max_body_size 0;                          # layers can be GBs: disable body limit
    chunked_transfer_encoding on;                    # registry uploads use chunked transfer
    location /v2/ {
        proxy_pass http://registry:5000;             # forward to the registry container
        proxy_set_header Host $http_host;            # keep original Host header
        proxy_set_header X-Forwarded-Proto $scheme;  # tell registry the client used https
        proxy_read_timeout 900;                      # big pushes need long timeouts
    }
}
```

The compose file and shell blocks were syntax-checked locally; the stack itself was not run (no Docker daemon here).

---

## 🟠 My Stack Integration
CI on GitHub Actions builds the Node.js API, FastAPI service and React/Nginx image, then pushes them to `registry.example.com`. The VPS pulls them during deploy. If you are on AWS, ECR is the managed equivalent, but a self-hosted registry is cheaper for a single VPS.

```yaml
# .github/workflows/push-private.yml (excerpt)
name: push-private-registry                      # workflow name
on:
  push:
    branches: [main]                             # run on every push to main
jobs:
  build-push:
    runs-on: ubuntu-latest                       # GitHub hosted runner
    steps:
      - uses: actions/checkout@v4                # get the source code
      - uses: docker/login-action@v3             # login to custom registry
        with:
          registry: registry.example.com         # your private host
          username: ${{ secrets.REG_USER }}      # robot user stored as secret
          password: ${{ secrets.REG_PASS }}      # password stored as secret
      - uses: docker/build-push-action@v6        # build and push in one step
        with:
          context: ./api                         # Node.js API folder
          push: true                             # push after build
          tags: registry.example.com/node-api:${{ github.sha }}  # immutable tag per commit
```

On the VPS: `docker login registry.example.com` once, then `docker compose pull && docker compose up -d`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Exposing `registry:2` on port 5000 to the internet without TLS or auth, so anyone can pull your code or push malicious images.
✅ Correct: Bind to localhost or a private network, put Nginx TLS in front, require htpasswd or token auth.

❌ Mistake 2: Adding the host to `insecure-registries` in daemon.json to "make it work" instead of fixing the certificate.
✅ Correct: Get a real Let's Encrypt cert. `insecure-registries` disables verification and allows man-in-the-middle attacks.

❌ Mistake 3: Never running garbage collection; the disk fills with orphaned layers.
✅ Correct: Enable delete, schedule `registry garbage-collect` in a maintenance window (stop pushes during it).

❌ Mistake 4: No backup of the `registry-data` volume.
✅ Correct: Back up the volume or store blobs in S3 using the registry's S3 storage driver.

---

## 🧠 Tricky Interview Question
You deleted a tag with `curl -X DELETE` on your registry, but disk usage did not drop. Why, and what next?

Answer: The API delete removes only the manifest reference. The layer blobs stay on disk because other images might share them. Space returns only after you run `registry garbage-collect`. Also the registry must have `REGISTRY_STORAGE_DELETE_ENABLED=true`, otherwise the DELETE call returns 405. GC must run while no pushes happen, or a freshly pushed layer could be wrongly collected.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a registry and a repository?
A1: A registry is the server (registry.example.com). A repository is a named collection of image versions inside it (node-api). A tag identifies one version inside the repository.

Q2: Why does `docker push` to `192.168.1.10:5000` fail with "http: server gave HTTP response to HTTPS client"?
A2: Docker requires HTTPS for non-localhost registries. Fix by enabling TLS. As a last resort in a lab, add the host to `insecure-registries` in `/etc/docker/daemon.json` and restart Docker.

Q3: How does authentication work?
A3: `docker login` sends credentials to the registry's `/v2/` endpoint. With htpasswd the registry checks basic auth; with token auth it redirects to a separate auth server that issues a JWT. Docker stores the result in `~/.docker/config.json` (use a credential helper to avoid plain base64).

Q4: What alternatives exist to self-hosting?
A4: Docker Hub private repos, GHCR, AWS ECR, Google Artifact Registry, Harbor (self-hosted with UI, RBAC, scanning, replication).

Q5: How do you move images between registries?
A5: `docker pull old/app:1`, `docker tag`, `docker push new/app:1`. For many images or multi-arch use `crane copy` or `skopeo copy`, which copy manifests without a Docker daemon.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Compliance or air-gap rules keep images inside your network
- You deploy to many servers and want fast LAN pulls and no rate limits
- You want full control over retention, access and cost

❌ Avoid when:
- You have one small project and GHCR or Docker Hub private repo is enough
- Nobody can own patching, backups and GC of the registry
- You need vulnerability scanning and RBAC out of the box (use Harbor or a managed service)

---

## 📊 Visual Diagram
```
 GitHub Actions (CI)                         Production VPS
 ┌──────────────────┐   docker push          ┌──────────────────┐
 │ build node-api   │──────────────┐         │ docker compose   │
 └──────────────────┘              │         │ pull + up -d     │
                                   ▼         └────────▲─────────┘
                        HTTPS :443 │                  │ docker pull
                   ┌───────────────┴──────────────────┴───┐
                   │  Nginx (TLS, big body, long timeout) │
                   └───────────────┬──────────────────────┘
                                   │ http://registry:5000 (private net)
                         ┌─────────▼─────────┐
                         │ registry:2        │  htpasswd auth
                         │ /var/lib/registry │──► volume: registry-data
                         └───────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Registry | Server storing images | Image रखने वाला server |
| Repository | Named set of image versions | एक image के versions का समूह |
| htpasswd | File of user:hash lines for basic auth | Basic auth की password file |
| Garbage collection | Removes unreferenced blobs | बेकार layers हटाना |
| insecure-registries | Daemon setting that skips TLS checks | TLS जाँच बंद करने वाली setting |
| Harbor | Full-featured self-hosted registry | UI + RBAC वाला registry |

---

## ⚡ 3-Line Summary
English: A private registry (`registry:2`) stores images on your own server. Always protect it with TLS and authentication and keep layers on a volume or S3. Run garbage collection, because deleting a tag does not free disk.
Hindi: Private registry (`registry:2`) आपके अपने server पर images रखती है। इसे हमेशा TLS और authentication से सुरक्षित रखो और layers volume या S3 में रखो। Garbage collection चलाओ, क्योंकि tag delete करने से disk खाली नहीं होती।

---

## ➡️ Next Topic
**129. Registry Mirror**: after hosting your own registry, you learn to cache Docker Hub pulls through a mirror so builds and servers stay fast and avoid rate limits.

---
