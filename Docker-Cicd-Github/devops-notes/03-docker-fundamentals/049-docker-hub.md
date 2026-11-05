# 49. Docker Hub
# हिंदी में: Docker Hub (डॉकर हब)

---

## 🔵 Simple Definition (English)
**Docker Hub** (hub.docker.com) is Docker's public cloud registry and the **default** registry: when you run `docker pull nginx`, the client silently means `docker.io/library/nginx:latest`. It hosts **Docker Official Images**, verified publisher images, community images, and private repos, plus automated tooling like vulnerability scanning and access tokens.

## 🔵 सरल परिभाषा (Hindi)
**Docker Hub** (hub.docker.com) Docker की public cloud registry है और **default** registry भी: जब आप `docker pull nginx` चलाते हैं तो client चुपचाप `docker.io/library/nginx:latest` समझता है। यहाँ **Docker Official Images**, verified publishers की images, community images और private repos होते हैं, साथ में vulnerability scanning और access tokens जैसे tools भी।

---

## 🔴 Problem it Solves
Every developer needed Node, Python, Postgres, Nginx, Redis base images, and building them from scratch was slow and insecure. Docker Hub gave one trusted, searchable place with maintained official images, so `FROM node:20-slim` just works anywhere in the world. It also gave teams free public hosting for open-source images.

## 🔴 यह क्यों बना? (Hindi)
हर developer को Node, Python, Postgres, Nginx, Redis जैसी base images चाहिए थीं और scratch से बनाना धीमा और असुरक्षित था। Docker Hub ने एक भरोसेमंद, searchable जगह दी जहाँ maintained official images हैं, इसलिए `FROM node:20-slim` दुनिया में कहीं भी चल जाता है। Open-source images की मुफ़्त public hosting भी मिली।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create account (hub.docker.com), create repository  myuser/myapi  (public or private)
Step 2 → Create an Access Token (Account Settings -> Security) with Read/Write scope
Step 3 → docker login -u myuser  (use the token as the password)
Step 4 → docker build -t myuser/myapi:1.0 .
Step 5 → docker push myuser/myapi:1.0  -> appears in the repo's Tags tab
Step 6 → Anyone (or only team members for private) runs docker pull myuser/myapi:1.0
Step 7 → Optional: vulnerability scanning (Docker Scout), webhooks, team permissions
Name rules: "nginx" = docker.io/library/nginx ; "myuser/myapi" = docker.io/myuser/myapi
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Account बनाओ (hub.docker.com), repository बनाओ  myuser/myapi  (public या private)
Step 2 → Access Token बनाओ (Account Settings -> Security) Read/Write scope के साथ
Step 3 → docker login -u myuser  (password की जगह token दो)
Step 4 → docker build -t myuser/myapi:1.0 .
Step 5 → docker push myuser/myapi:1.0  -> repo के Tags tab में दिखेगा
Step 6 → कोई भी (private हो तो सिर्फ़ team) docker pull myuser/myapi:1.0 कर सकता है
Step 7 → वैकल्पिक: vulnerability scanning (Docker Scout), webhooks, team permissions
नाम के नियम: "nginx" = docker.io/library/nginx ; "myuser/myapi" = docker.io/myuser/myapi
```

---

## 🟡 Real World Example
Almost every Dockerfile in the world starts with an image from Docker Hub: `node`, `python`, `nginx`, `postgres`, `redis`. A startup on a small VPS builds `myuser/api` in CI and pushes it to a free private Docker Hub repo. A real operational problem: CI runners that pull many base images anonymously hit **pull rate limits** (HTTP 429 `toomanyrequests`), so pipelines log in with a token or mirror base images to ECR/GHCR.

## 🟡 Real Example Hindi mein
दुनिया का लगभग हर Dockerfile Docker Hub की image से शुरू होता है: `node`, `python`, `nginx`, `postgres`, `redis`। छोटे VPS वाला startup CI में `myuser/api` बनाकर free private Docker Hub repo में push करता है। असली operational समस्या: जो CI runners बहुत सारी base images anonymous pull करते हैं वे **pull rate limits** (HTTP 429 `toomanyrequests`) में फँसते हैं, इसलिए pipelines token से login करते हैं या base images ECR/GHCR में mirror करते हैं।

---

## 💻 Code / Config Example — Basic
```bash
# Docker Hub basics (needs a Docker daemon and a Hub account)
docker search nginx --limit 5                      # search Hub from the CLI (official + community results)
docker pull nginx:1.27-alpine                      # official image, explicit tag (example tag)
docker pull docker.io/library/nginx:1.27-alpine    # identical, fully qualified name

docker login -u myuser                             # prompts for an ACCESS TOKEN, not your account password
docker build -t myuser/myapi:1.0 .                 # build and name it <hub-user>/<repo>:<tag>
docker push myuser/myapi:1.0                       # upload to Docker Hub
docker tag myuser/myapi:1.0 myuser/myapi:latest    # extra moving tag (do not deploy it)
docker push myuser/myapi:latest                    # publish that tag too
docker logout                                      # remove stored credentials from this machine
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/dockerhub.yml - multi-arch build, push to Docker Hub, token auth
name: dockerhub-publish                              # workflow name
on:
  push:
    tags: ["v*.*.*"]                                 # publish on version tags
permissions:
  contents: read                                     # only read the repo
jobs:
  publish:
    runs-on: ubuntu-latest                           # runner
    steps:
      - uses: actions/checkout@v4                    # fetch code
      - uses: docker/setup-qemu-action@v3            # emulation to build ARM images on x86 runner
      - uses: docker/setup-buildx-action@v3          # modern builder (multi-platform)
      - uses: docker/login-action@v3                 # authenticate to Docker Hub
        with:
          username: ${{ vars.DOCKERHUB_USERNAME }}   # non-secret repo variable
          password: ${{ secrets.DOCKERHUB_TOKEN }}   # access token stored as a secret (scope: Read & Write only)
      - id: meta                                     # derive tags/labels
        uses: docker/metadata-action@v5              # tags from git tag
        with:
          images: myuser/myapi                       # Hub repository
          tags: |
            type=semver,pattern={{version}}          # 1.4.0
            type=semver,pattern={{major}}.{{minor}}  # 1.4
      - uses: docker/build-push-action@v6            # build and push
        with:
          context: .                                 # repo root build context
          platforms: linux/amd64,linux/arm64         # for EC2 x86 and Graviton ARM servers
          push: true                                 # upload after build
          tags: ${{ steps.meta.outputs.tags }}       # generated tags
          labels: ${{ steps.meta.outputs.labels }}   # OCI labels
          cache-from: type=gha                       # read build cache
          cache-to: type=gha,mode=max                # write build cache
```

---

## 🟠 My Stack Integration
- **Dockerfiles:** pull bases from Hub: `node:20-slim`, `python:3.12-slim`, `nginx:1.27-alpine`. Pin versions (and optionally digests).
- **VPS:** `docker compose pull` fetches from Hub; log in to avoid anonymous limits.
- **AWS:** copy base images into ECR once (`docker pull` -> `docker tag` -> `docker push`) or use ECR pull-through cache to remove Hub dependence.
- **CI rate limits:** log in with `docker/login-action` before builds.

```dockerfile
# Dockerfile for the FastAPI service - pinned official bases from Docker Hub
# Example tag; update to the current supported Python version
FROM python:3.12-slim
# Work directory inside the image
WORKDIR /app
# Copy requirements first to reuse the cached layer
COPY requirements.txt .
# Install dependencies without pip cache to keep the image small
RUN pip install --no-cache-dir -r requirements.txt
# Copy application code
COPY . .
# Create and switch to an unprivileged user (security)
RUN useradd --system --uid 10001 appuser
USER appuser
# Start uvicorn listening on all interfaces inside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using your account password in CI.
✅ Correct: Create scoped Access Tokens (revocable, per-purpose) and store them in GitHub Secrets.

❌ Mistake 2: Trusting any image by name, e.g. a random `someuser/nginx-fast`.
✅ Correct: Prefer Docker Official Images and Verified Publisher badges, check update dates, and scan. Typosquatted and cryptominer images exist.

❌ Mistake 3: Putting secrets in a "private" Hub repo image.
✅ Correct: Private still means anyone with access (or a leaked token) can read layers. Inject secrets at runtime.

❌ Mistake 4: Ignoring 429 rate-limit errors until production deploys fail.
✅ Correct: Authenticate pulls, mirror critical base images to your own registry.

---

## 🧠 Tricky Interview Question
"`docker pull nginx` and `docker pull myuser/nginx` and `docker pull ghcr.io/myuser/nginx` - which registries and repositories do they hit?"

Answer: First: `docker.io/library/nginx:latest` (Docker Hub, official namespace `library`). Second: `docker.io/myuser/nginx:latest` (Hub, user namespace). Third: GitHub Container Registry because the first path component contains a dot (`ghcr.io`), which the client treats as a registry host. Rule: if the first segment has a `.` or `:` or is `localhost`, it is a registry hostname; otherwise Docker Hub is assumed.

---

## ⚫ Interview Questions + Answers

Q1: What is Docker Hub and what are Official Images?
A1: Default public registry. Official Images are curated, reviewed, regularly updated repos (nginx, node, postgres) in the `library` namespace.

Q2: Docker Hub vs GHCR vs ECR?
A2: Hub: biggest public catalog, rate limits for pulls. GHCR: integrated with GitHub permissions/Actions. ECR: AWS, IAM-integrated, immutable tags, scanning, pairs with ECS/EKS.

Q3: How do you avoid Hub rate limits?
A3: Authenticate, use a paid plan, configure registry mirror / pull-through cache, or host base images yourself.

Q4: What is an access token for?
A4: A revocable, scoped credential replacing the password for CLI/CI; supports read-only, read/write, or admin scopes.

Q5: How do you verify an image is trustworthy?
A5: Use official/verified images, pin digests, scan (Docker Scout/Trivy), check Dockerfile source, use Docker Content Trust or cosign signatures.

---

## 🔷 When to Use + When Not to Use
✅ Use Docker Hub when:
- Pulling official base images, publishing open-source images, small teams with free private repos

❌ Avoid when:
- Production pipelines that must not depend on external rate limits (mirror to ECR/GHCR)
- Highly regulated code needing private network registries

---

## 📊 Visual Diagram
```
 docker pull nginx
        │  (no host given -> default)
        v
 +-----------------------------------+
 | docker.io  (Docker Hub)           |
 |  library/   <- Official Images    |   nginx  node  python  postgres  redis
 |  myuser/    <- user namespaces    |   myuser/myapi:1.0
 |  verified publishers, scanning    |
 +-----------------------------------+
        ^ push (token)      │ pull (anonymous = rate-limited, logged-in = higher)
 CI ────┘                   v
                       VPS / EC2 / laptop
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Docker Hub | Default public registry | डिफ़ॉल्ट public registry |
| Official Image | Curated image in `library/` | Docker द्वारा जाँची हुई image |
| Verified Publisher | Vendor-verified images | सत्यापित प्रकाशक |
| Access Token | Scoped login credential | सीमित अधिकार वाला login token |
| Rate limit | Max pulls per time | pull की सीमा |
| Docker Scout | Vulnerability analysis | कमज़ोरियों की जाँच |
| Namespace | User/org prefix | user/संस्था का prefix |

---

## ⚡ 3-Line Summary
English: Docker Hub is the default registry hosting official and community images.
English: Log in with scoped tokens, expect pull rate limits, and mirror critical bases for production.
English: Prefer official/verified images, pin versions, and scan before trusting.
Hindi: Docker Hub default registry है जहाँ official और community images मिलती हैं।
Hindi: Scoped tokens से login करो, pull rate limits मानकर चलो, और production के लिए ज़रूरी bases mirror करो।
Hindi: Official/verified images चुनो, versions pin करो, और भरोसा करने से पहले scan करो।

---

## ➡️ Next Topic
**50. Docker Objects Overview** - images, containers, networks, volumes: the things the daemon manages.
