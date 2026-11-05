---

# 129. Registry Mirror
# हिंदी में: Registry Mirror (Pull-through Cache)

---

## 🔵 Simple Definition (English)
A **registry mirror** is a caching proxy for Docker Hub. When a machine pulls `node:20-alpine`, the Docker daemon asks the mirror first; the mirror serves it from its cache or fetches it once from Docker Hub and keeps a copy. It is configured with `registry-mirrors` in `daemon.json` and is often run as `registry:2` in pull-through (proxy) mode.

## 🔵 सरल परिभाषा (Hindi)
**Registry mirror** Docker Hub के लिए एक caching proxy है। जब कोई machine `node:20-alpine` pull करती है, Docker daemon पहले mirror से पूछता है; mirror अपनी cache से देता है या Docker Hub से एक बार लाकर copy रख लेता है। यह `daemon.json` में `registry-mirrors` से configure होता है और अक्सर `registry:2` को pull-through (proxy) mode में चलाकर बनाया जाता है।

---

## 🔴 Problem it Solves
Docker Hub limits anonymous pulls (about 100 per 6 hours per IP) and authenticated free users (about 200 per 6 hours); limits can change, so check Docker's current docs. A CI fleet or a team behind one NAT IP hits `429 Too Many Requests` and builds fail at random. Pulling the same 150 MB base image on 20 servers wastes bandwidth, and Docker Hub outages break deploys.

## 🔴 यह क्यों बना? (Hindi)
Docker Hub anonymous pulls पर limit लगाता है (लगभग 100 pulls प्रति 6 घंटे प्रति IP) और free logged-in users पर भी (लगभग 200); limits बदल सकती हैं, इसलिए Docker के current docs देखो। CI fleet या एक NAT IP के पीछे बैठी team को `429 Too Many Requests` मिलता है और builds अचानक fail होते हैं। 20 servers पर वही 150 MB base image बार-बार खींचना bandwidth की बर्बादी है, और Docker Hub down हो तो deploy रुक जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Run registry:2 with REGISTRY_PROXY_REMOTEURL=https://registry-1.docker.io
Step 2 → Add "registry-mirrors": ["https://mirror.example.com"] to /etc/docker/daemon.json
Step 3 → Restart dockerd (daemon reads mirrors only at start; live-restore keeps containers up)
Step 4 → docker pull node:20-alpine -> daemon asks the mirror first
Step 5 → Cache MISS: mirror downloads from Docker Hub, stores layers, streams to client
Step 6 → Cache HIT (next machines): mirror serves from local disk, no Hub request
Step 7 → If mirror is down, daemon falls back to Docker Hub directly
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → registry:2 चलाओ REGISTRY_PROXY_REMOTEURL=https://registry-1.docker.io के साथ
Step 2 → /etc/docker/daemon.json में "registry-mirrors": ["https://mirror.example.com"] जोड़ो
Step 3 → dockerd restart करो (daemon mirrors सिर्फ़ start पर पढ़ता है; live-restore containers चालू रखता है)
Step 4 → docker pull node:20-alpine -> daemon पहले mirror से पूछता है
Step 5 → Cache MISS: mirror Docker Hub से download करके layers रखता है और client को stream करता है
Step 6 → Cache HIT (बाकी machines): mirror अपनी disk से देता है, Hub को request नहीं जाती
Step 7 → Mirror down हो तो daemon सीधे Docker Hub पर fallback करता है
```

---

## 🟡 Real World Example
A coaching-platform company has 8 self-hosted GitHub Actions runners and 4 VPS servers, all behind one office/datacenter IP. Every morning a deploy storm pulled `node`, `python`, `nginx`, `postgres` and `redis` on every machine and hit Docker Hub's 429 limit around 10 AM. They added a pull-through mirror on one small VPS. The first pull of each image fills the cache; the other 11 machines get it over the LAN in seconds. Failed builds due to rate limits dropped to zero and CI got about 40% faster on image pulls.

## 🟡 Real Example Hindi mein
एक coaching-platform company के पास 8 self-hosted GitHub Actions runners और 4 VPS servers हैं, सब एक ही IP के पीछे। हर सुबह deploy के समय हर machine `node`, `python`, `nginx`, `postgres`, `redis` pull करती थी और 10 बजे के आसपास Docker Hub का 429 limit लग जाता था। उन्होंने एक छोटे VPS पर pull-through mirror लगाया। हर image का पहला pull cache भरता है; बाकी 11 machines उसे LAN पर सेकंडों में पा लेती हैं। Rate-limit वाले failed builds शून्य हो गए और image pull में CI लगभग 40% तेज़ हो गया।

---

## 💻 Code / Config Example — Basic

```json
{
  "registry-mirrors": ["https://mirror.example.com"]
}
```

```bash
# /etc/docker/daemon.json holds the JSON above (JSON allows no comments, so they are here)
# registry-mirrors: list of mirrors tried in order for Docker Hub images only

# Write the file (needs root); keep any existing keys when you merge by hand
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "registry-mirrors": ["https://mirror.example.com"]
}
EOF
# tee with sudo writes the file as root; quoted EOF stops shell expansion

# Restart the daemon so it reads the new config
sudo systemctl restart docker

# Verify: the mirror must appear in the output
docker info --format '{{.RegistryConfig.Mirrors}}'
# prints the mirror list as a Go template; empty [] means config not applied

# Pull a Docker Hub image, now routed through the mirror
docker pull alpine:3.20
```

Important: mirrors only work for Docker Hub images (`docker.io`). Images from `ghcr.io` or `quay.io` are not mirrored by this setting.

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.mirror.yml
# Pull-through cache for Docker Hub with TLS terminated by a separate Nginx (see 128)
services:
  mirror:
    image: registry:2.8.3                         # example tag, update to current
    restart: unless-stopped                       # survive reboots
    environment:
      REGISTRY_PROXY_REMOTEURL: https://registry-1.docker.io   # upstream to cache
      REGISTRY_PROXY_USERNAME: ${HUB_USER}        # authenticated pulls get a higher rate limit
      REGISTRY_PROXY_PASSWORD: ${HUB_TOKEN}       # use a read-only access token, not your password
      REGISTRY_STORAGE_DELETE_ENABLED: "true"     # allow cleanup of cached repos
      REGISTRY_STORAGE_CACHE_BLOBDESCRIPTOR: inmemory  # fast layer lookups
      REGISTRY_PROXY_TTL: 168h                    # expire cached content after 7 days
    volumes:
      - mirror-data:/var/lib/registry             # cache survives container recreation
    ports:
      - "127.0.0.1:5000:5000"                     # reachable by local Nginx only
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:5000/v2/"]  # API must answer
      interval: 30s                               # every 30 seconds
      timeout: 5s                                 # give up after 5 seconds
      retries: 3                                  # three strikes then unhealthy

volumes:
  mirror-data: {}                                 # named volume for cached layers
```

```json
{
  "registry-mirrors": ["https://mirror.example.com"],
  "live-restore": true,
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
```

```bash
# Per-machine rollout script (run with sudo on each server or via Ansible)
set -euo pipefail                                # stop on error, unset var or pipe failure
CONF=/etc/docker/daemon.json                     # daemon config path
[ -f "$CONF" ] && cp "$CONF" "$CONF.bak"         # keep a backup if one exists
cat > "$CONF" <<'EOF'
{
  "registry-mirrors": ["https://mirror.example.com"],
  "live-restore": true
}
EOF
systemctl restart docker                         # apply (live-restore keeps containers running)
docker info --format '{{.RegistryConfig.Mirrors}}'   # confirm mirror is active
```

The YAML parses cleanly and the JSON and shell blocks were syntax-checked; the mirror itself was not run here. Note `REGISTRY_PROXY_TTL` and the proxy variables follow the Distribution config docs, verify against your registry version.

---

## 🟠 My Stack Integration
Your Node.js, FastAPI and React Dockerfiles all start with `FROM node:...`, `FROM python:...`, `FROM nginx:...`. With the mirror, every `docker build` on the VPS and every CI runner resolves those bases from the cache. For GitHub-hosted runners (shared IPs) set the mirror in the workflow; for self-hosted runners use `daemon.json`.

```yaml
# .github/workflows/build.yml (excerpt): use a mirror on a hosted runner via buildx
name: build                                      # workflow name
on: [push]                                       # run on any push
jobs:
  build:
    runs-on: ubuntu-latest                       # GitHub hosted runner
    steps:
      - uses: actions/checkout@v4                # fetch code
      - uses: docker/setup-buildx-action@v3      # create buildx builder
        with:
          buildkitd-config-inline: |             # inline BuildKit config
            [registry."docker.io"]
              mirrors = ["mirror.example.com"]
      - uses: docker/build-push-action@v6        # build the Node.js API image
        with:
          context: ./api                         # path of the API Dockerfile
          push: false                            # only build in this example
```

BuildKit uses its own config for mirrors on the buildx builder, which is why we set it here and not only in `daemon.json`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Adding a mirror but forgetting `systemctl restart docker`; pulls still go to Docker Hub.
✅ Correct: Restart, then check `docker info` for the mirror entry.

❌ Mistake 2: Expecting the mirror to cache `ghcr.io/...` or private images.
✅ Correct: `registry-mirrors` covers Docker Hub only. For other registries run a separate proxy or use full registry paths via Harbor proxy-cache projects.

❌ Mistake 3: Putting your Docker Hub account password into the mirror config.
✅ Correct: Create a read-only access token and pass it through env vars or Docker secrets.

❌ Mistake 4: Exposing the mirror publicly without auth, turning it into a free open proxy that uses your Hub quota.
✅ Correct: Restrict by firewall or VPN, or add basic auth in Nginx.

---

## 🧠 Tricky Interview Question
Your mirror is configured, but a build still shows a 429 from Docker Hub. The mirror is healthy. How is that possible?

Answer: The mirror helps only for pulls that go through the Docker daemon with that config. Possible causes: (1) BuildKit/buildx builders running in a container (`docker-container` driver) ignore `daemon.json` and need their own `buildkitd.toml` mirror config; (2) the Dockerfile uses `FROM ghcr.io/...` or another registry; (3) the first pull of an uncached image still reaches Hub, and many parallel first pulls can burn the limit; (4) the manifest check (HEAD request) for mutable tags like `latest` still counts against some limits. Fix with pre-warming the cache and configuring the builder.

---

## ⚫ Interview Questions + Answers

Q1: Difference between a registry mirror and a private registry?
A1: A mirror is a read-through cache of an upstream (Docker Hub); clients still pull the original names like `node:20`. A private registry stores your own images under your own hostname and you must push to it.

Q2: Does a mirror affect `docker push`?
A2: No. Pushes always go to the registry named in the image tag. A pull-through registry is read-only.

Q3: What happens if the mirror is down?
A3: The daemon tries the next mirror, then falls back to Docker Hub. Pulls slow down but do not fail unless Hub is also unreachable.

Q4: How do you keep the mirror cache from growing forever?
A4: Set `proxy.ttl`, enable delete, run `registry garbage-collect`, and monitor disk. Or use Harbor/Nexus with retention policies.

Q5: Is a mirror a security risk?
A5: It can be: a compromised mirror could serve tampered layers. Digests protect you if you pin `image@sha256:...`, and content trust or signature verification adds more. Always use TLS and restrict who can write to the cache.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many machines or CI runners share an IP and hit Docker Hub rate limits
- Servers have slow or expensive internet but fast LAN
- You want resilience to Docker Hub outages

❌ Avoid when:
- You have one dev laptop and a handful of pulls a day
- You can simply authenticate pulls (`docker login`) and stay under limits
- You cannot secure and maintain another server

---

## 📊 Visual Diagram
```
  Runner 1 ─┐                                    ┌────────────────────┐
  Runner 2 ─┼─ docker pull node:20 ─► MIRROR ──► │ Docker Hub (cold)  │
  VPS A    ─┤        ▲                  │ miss   └────────────────────┘
  VPS B    ─┘        │ hit (LAN speed)  │
                     └──────────────────┘
                     cache volume: /var/lib/registry
  If MIRROR is down ──► daemon falls back straight to Docker Hub
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mirror | Cache copy of a registry | Registry की cache copy |
| Pull-through cache | Fetches on first miss, then serves locally | पहली बार लाकर बाद में local से देना |
| Rate limit | Max pulls per time window | समय में pulls की सीमा |
| registry-mirrors | daemon.json key listing mirrors | Mirrors की list वाली key |
| live-restore | Keeps containers running during daemon restart | Daemon restart में containers चालू |
| TTL | Cache lifetime | Cache कितने समय रहेगी |

---

## ⚡ 3-Line Summary
English: A registry mirror caches Docker Hub images close to your servers. Configure `registry-mirrors` in `daemon.json` and run `registry:2` in proxy mode. It cuts rate-limit failures and pull time, but covers Docker Hub only.
Hindi: Registry mirror Docker Hub की images आपके servers के पास cache करता है। `daemon.json` में `registry-mirrors` set करो और `registry:2` को proxy mode में चलाओ। इससे rate-limit failures और pull time घटता है, पर यह सिर्फ़ Docker Hub के लिए है।

---

## ➡️ Next Topic
**130. Image Pull Policy**: now that you know where images come from, learn when Docker and Kubernetes actually re-pull them (Always, IfNotPresent, Never).

---
