# 66. docker pull + docker push
# हिंदी में: docker pull और docker push (Registry से image लाना और भेजना)

---

## 🔵 Simple Definition (English)
`docker pull` downloads an image (its layers) from a registry such as Docker Hub, GitHub Container Registry (GHCR) or AWS ECR to your machine. `docker push` uploads a locally built and tagged image to a registry so other machines (CI, VPS, Kubernetes) can pull it.

## 🔵 सरल परिभाषा (Hindi)
`docker pull` किसी registry (Docker Hub, GHCR, AWS ECR) से image की layers आपकी machine पर download करता है। `docker push` आपकी local बनी और tag की हुई image को registry पर upload करता है ताकि दूसरी machines (CI, VPS, Kubernetes) उसे pull कर सकें।

---

## 🔴 Problem it Solves
Before registries, developers copied code to the server and built it there, or shipped tar files by hand. "Works on my machine" came back as "works on my build". A registry gives one central, versioned store of built images: build once in CI, run the exact same bytes everywhere. Push/pull is the transport between the build place and the run place.

## 🔴 यह क्यों बना? (Hindi)
Registry से पहले लोग server पर code copy करके वहीं build करते थे या tar files हाथ से भेजते थे। नतीजा: "मेरी machine पर चलता है" की जगह "मेरे build में चलता है" वाली दिक्कत। Registry एक central, versioned store है: CI में एक बार build करो, हर जगह वही image चलाओ। Push/pull build वाली जगह से run वाली जगह तक image पहुँचाने का रास्ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker login <registry>        (credentials saved in ~/.docker/config.json)
Step 2 → docker build -t <repo>:<tag> . (image exists only locally)
Step 3 → docker push <repo>:<tag>       (CLI asks registry which layers are missing)
Step 4 → Only missing layers (blobs) are uploaded, then the manifest is written
Step 5 → docker pull <repo>:<tag>       (on VPS: fetch manifest, then download only layers not cached)
Step 6 → Layers are verified by sha256 digest and stored under /var/lib/docker
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker login <registry>        (credentials ~/.docker/config.json में save होते हैं)
Step 2 → docker build -t <repo>:<tag> . (image अभी सिर्फ local है)
Step 3 → docker push <repo>:<tag>       (CLI registry से पूछता है कौन सी layers नहीं हैं)
Step 4 → सिर्फ missing layers upload होती हैं, फिर manifest लिखा जाता है
Step 5 → docker pull <repo>:<tag>       (VPS पर: manifest लाओ, सिर्फ वो layers download जो cache में नहीं)
Step 6 → हर layer sha256 digest से verify होती है और /var/lib/docker में रखी जाती है
```

---

## 🟡 Real World Example
Your team pushes code to GitHub. GitHub Actions builds the FastAPI image and runs `docker push ghcr.io/addyrj/api:1.4.2`. The AWS EC2 / VPS box then runs `docker pull ghcr.io/addyrj/api:1.4.2` and restarts the container. Because 90% of the layers (Python base, pip packages) are unchanged, only the small app layer travels over the network, so a deploy takes seconds, not minutes. Zomato-style teams do exactly this with ECR so that hundreds of nodes pull the same image.

## 🟡 Real Example Hindi mein
आपकी team code GitHub पर push करती है। GitHub Actions FastAPI image build करके `docker push ghcr.io/addyrj/api:1.4.2` चलाता है। फिर AWS EC2 / VPS पर `docker pull ghcr.io/addyrj/api:1.4.2` होता है और container restart होता है। 90% layers (Python base, pip packages) बदलती नहीं, इसलिए सिर्फ छोटी app layer network पर जाती है, deploy कुछ seconds में हो जाता है। Zomato जैसी teams ECR के साथ यही करती हैं ताकि सैकड़ों nodes एक ही image pull करें।

---

## 💻 Code / Config Example — Basic
```bash
# ---- Basic pull and push (Docker Hub) ----
docker pull nginx:1.27-alpine                 # download official nginx image, tag 1.27-alpine (example tag, update it)
docker pull --platform linux/amd64 node:20-alpine  # force CPU arch (useful on Apple Silicon -> amd64 VPS)
docker images nginx                           # list local nginx images to confirm the pull
docker login -u addyrj                        # login to Docker Hub; prompts for password/access token
docker tag myapp:latest addyrj/myapp:1.0.0    # name must be <user>/<repo>:<tag> for Docker Hub
docker push addyrj/myapp:1.0.0                # upload layers + manifest to Docker Hub
docker pull addyrj/myapp:1.0.0                # on any other machine: download the same image
docker logout                                 # remove stored credentials from this machine
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/push-image.yml
# Build and push to GHCR on every push to main, deploy by digest-safe tag.
name: build-and-push                      # workflow name shown in the Actions tab
on:                                       # trigger section
  push:                                   # run on push events
    branches: [main]                      # only for the main branch
permissions:                              # least-privilege token permissions
  contents: read                          # needed to checkout code
  packages: write                         # needed to push to GHCR
jobs:                                     # list of jobs
  push:                                   # job id
    runs-on: ubuntu-latest                # GitHub-hosted runner
    steps:                                # ordered steps
      - uses: actions/checkout@v4         # fetch repo code (example version, update)
      - uses: docker/setup-buildx-action@v3   # enable buildx builder
      - uses: docker/login-action@v3      # login to registry without storing password in repo
        with:                             # inputs of the action
          registry: ghcr.io               # target registry
          username: ${{ github.actor }}   # user who triggered the run
          password: ${{ secrets.GITHUB_TOKEN }}  # auto token, no manual secret needed
      - uses: docker/build-push-action@v6 # build and push in one step
        with:                             # inputs
          context: .                      # build context is repo root
          push: true                      # actually push (false = build only)
          tags: |                         # multiple tags for one image
            ghcr.io/addyrj/api:${{ github.sha }}
            ghcr.io/addyrj/api:latest
          cache-from: type=gha            # reuse layer cache from GitHub cache
          cache-to: type=gha,mode=max     # save layer cache for next run
```

---

## 🟠 My Stack Integration
Node.js / FastAPI / React images are built in CI, pushed to GHCR or ECR, and pulled on the VPS behind Nginx. On the server you never build; you only pull and restart.

```bash
# deploy.sh -- run on VPS (example), image tag passed as argument
set -euo pipefail                                   # stop on first error, undefined var, or pipe failure
TAG="$1"                                            # e.g. git sha from CI
echo "$GHCR_PAT" | docker login ghcr.io -u addyrj --password-stdin   # token via stdin, not visible in ps
docker pull ghcr.io/addyrj/api:"$TAG"               # fetch new image first; old container keeps serving
docker rm -f api 2>/dev/null || true                # remove old container if exists
docker run -d --name api --restart unless-stopped -p 127.0.0.1:8000:8000 \
  --env-file /etc/api.env ghcr.io/addyrj/api:"$TAG" # Nginx proxies to 127.0.0.1:8000
```
For AWS ECR: `aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <acct>.dkr.ecr.ap-south-1.amazonaws.com`. Not run locally; adjust account id and region.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Pushing with `docker push myapp:1.0` and getting "denied: requested access" or pushing to Docker Hub library.
✅ Correct: Tag with the full registry path first (`ghcr.io/addyrj/myapp:1.0` or `addyrj/myapp:1.0`).

❌ Mistake 2: Deploying with `:latest` so nobody knows what is running; `docker pull` may even return a cached old image.
✅ Correct: Deploy immutable tags (git SHA / semver) or digests (`image@sha256:...`).

❌ Mistake 3: `docker login -p password` on CLI (stored in shell history, process list).
✅ Correct: `--password-stdin` with a token that has minimum scope; rotate it.

❌ Mistake 4: Baking secrets (`.env`, keys) into the image and pushing it to a public repo.
✅ Correct: Use `.dockerignore`, runtime env/secret managers, and private repos.

---

## 🧠 Tricky Interview Question
You pushed a new image as `api:latest` but the VPS still runs old code after `docker compose up -d`. Why?

Answer: `docker compose up -d` does not pull automatically if an image with that tag already exists locally. The tag `latest` is just a mutable pointer. You must run `docker compose pull` (or `docker pull`) first, or use unique tags and change the tag in the compose file. Also, running containers keep using the old image ID until recreated.

---

## ⚫ Interview Questions + Answers

Q1: What does `docker pull` actually download?
A1: First the manifest (list of layer digests and config), then only the layers missing locally, each verified by sha256.

Q2: Why is the second push of the same image fast?
A2: The registry already has the unchanged layers (content-addressable by digest), so only new layers and the manifest are uploaded ("Layer already exists").

Q3: Difference between tag and digest?
A3: A tag is a movable label; a digest (`@sha256:...`) is the immutable hash of the manifest. Digests guarantee the exact same image.

Q4: How do you push to a private registry on AWS?
A4: Create an ECR repository, authenticate with `aws ecr get-login-password | docker login`, tag the image with the ECR URI, then `docker push`.

Q5: What is a Docker Hub pull rate limit and how do you avoid it?
A5: Anonymous/free users have limited pulls per period. Authenticate, use a registry mirror or pull-through cache, or host base images in your own ECR/GHCR.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Moving built images from CI to servers or clusters.
- Sharing base/internal images across teams.
- Rolling back by pulling an older tag.

❌ Avoid when:
- You only need a one-off local test (use `docker build`/`run`).
- Image contains secrets or private data and the registry is public.
- Air-gapped servers: use `docker save`/`docker load` instead.

---

## 📊 Visual Diagram
```
 Developer / CI                 Registry                     VPS / EC2 / K8s
+---------------+   push     +--------------+    pull     +----------------+
| docker build  | ---------> | ghcr.io /    | ----------> | docker pull    |
| docker tag    |  (only new | Docker Hub / |  (only new  | docker run     |
|               |   layers)  | ECR          |   layers)   |  -> Nginx :443 |
+---------------+            +--------------+             +----------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Registry | Server storing images | Images रखने वाला server |
| Repository | Collection of tags of one image | एक image के tags का समूह |
| Manifest | JSON listing layers of an image | Image की layers की list |
| Digest | sha256 hash of manifest | Image का अटल hash |
| Layer | Read-only filesystem diff | Filesystem का read-only हिस्सा |
| GHCR / ECR | GitHub / AWS registries | GitHub / AWS की registry |

---

## ⚡ 3-Line Summary
English: `docker pull` fetches missing layers of an image from a registry; `docker push` uploads your tagged image. Only changed layers move, so deploys are fast. Use immutable tags, private repos and token login.
Hindi: `docker pull` registry से image की missing layers लाता है; `docker push` आपकी tag की हुई image upload करता है। सिर्फ बदली हुई layers चलती हैं, इसलिए deploy तेज़ होता है। Immutable tags, private repo और token login इस्तेमाल करो।

---

## ➡️ Next Topic
**67. docker tag** — push से पहले image को सही registry path और version देने के लिए tagging समझना ज़रूरी है।
