# 337. Push to Docker Hub
# हिंदी में: Docker Hub पर Image Push करना

---

## 🔵 Simple Definition (English)
Docker Hub is the default public registry. In CI you log in with `docker/login-action` using an **access token** (not your password), then `docker/build-push-action` with `push: true` uploads the tagged image so any server can `docker pull` it.

## 🔵 सरल परिभाषा (Hindi)
Docker Hub default public registry है। CI में आप `docker/login-action` से **access token** (password नहीं) के साथ login करते हैं, फिर `build-push-action` में `push: true` से tagged image upload होती है और कोई भी server उसे `docker pull` कर सकता है।

---

## 🔴 Problem it Solves
A built image lives only on the runner, which is destroyed after the job. Servers cannot reach it. Copying images with `docker save | scp` is slow, manual and unversioned. A registry gives one central, versioned store with pull access control.

## 🔴 यह क्यों बना? (Hindi)
Build हुई image सिर्फ runner पर होती है जो job के बाद delete हो जाता है। Servers उस तक नहीं पहुँच सकते। `docker save | scp` धीमा, manual और बिना version के है। Registry एक central, versioned store देती है जहाँ से कोई भी authorised server pull कर सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create Docker Hub access token (Account Settings > Security)
Step 2 → Store DOCKERHUB_USERNAME and DOCKERHUB_TOKEN as GitHub secrets
Step 3 → Workflow runs docker/login-action on main only
Step 4 → build-push-action builds and pushes myorg/api:sha-xxxx
Step 5 → Registry stores layers; only missing layers are uploaded
Step 6 → VPS/ECS/K8s pulls the same tag in the deploy job
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Docker Hub में access token बनाओ (Account Settings > Security)।
Step 2 → `DOCKERHUB_USERNAME` और `DOCKERHUB_TOKEN` को GitHub secrets में रखो।
Step 3 → Workflow सिर्फ main पर `login-action` चलाता है।
Step 4 → `build-push-action` build करके `myorg/api:sha-xxxx` push करता है।
Step 5 → Registry सिर्फ नई layers लेती है, पुरानी दोबारा upload नहीं होतीं।
Step 6 → Deploy job में VPS/ECS/K8s वही tag pull करता है।

---

## 🟡 Real World Example
A small startup keeps a private repo `myorg/api` on Docker Hub. Every merge to `main` pushes `myorg/api:sha-3f9a1c2` and `myorg/api:latest`. The VPS runs `docker compose pull && up -d`. Note: Docker Hub rate-limits anonymous and free pulls, so production servers should log in as well, otherwise a busy deploy day can hit `toomanyrequests`.

## 🟡 Real Example Hindi mein
एक छोटा startup Docker Hub पर private repo `myorg/api` रखता है। `main` पर हर merge से `myorg/api:sha-3f9a1c2` और `latest` push होते हैं। VPS पर `docker compose pull && up -d` चलता है। ध्यान दें: Docker Hub anonymous/free pulls पर rate limit लगाता है, इसलिए production server को भी login करना चाहिए वरना `toomanyrequests` आ सकता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/push-dockerhub.yml (basic)
name: push-dockerhub                   # workflow name
on:
  push:
    branches: [main]                   # run only when main changes
jobs:
  push:
    runs-on: ubuntu-latest             # Linux runner
    steps:
      - uses: actions/checkout@v4      # get the code
      - name: Login to Docker Hub      # authenticate with token
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}   # Docker Hub user
          password: ${{ secrets.DOCKERHUB_TOKEN }}      # access token, not password
      - name: Build and push           # build then upload
        uses: docker/build-push-action@v6
        with:
          context: .                   # build context
          push: true                   # upload to registry
          tags: myorg/api:latest       # single tag (basic)
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/push-dockerhub-advanced.yml
name: push-dockerhub-advanced
on:
  push:
    branches: [main]                   # normal merges
    tags: ["v*.*.*"]                   # release tags
permissions:
  contents: read                       # minimal token permissions
jobs:
  push:
    runs-on: ubuntu-latest
    environment: production            # lets you add approval + env secrets
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-qemu-action@v3      # arm64 emulation
      - uses: docker/setup-buildx-action@v3    # BuildKit
      - uses: docker/login-action@v3           # login before push
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - id: meta                       # generate tags and OCI labels
        uses: docker/metadata-action@v5
        with:
          images: myorg/api            # repository on Docker Hub
          tags: |
            type=sha,format=short      # immutable per-commit tag
            type=semver,pattern={{version}}   # 1.4.2 on tag v1.4.2
            type=raw,value=latest,enable={{is_default_branch}}  # latest only on main
      - id: build
        uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64   # multi-arch image
          push: true                   # upload
          tags: ${{ steps.meta.outputs.tags }}      # all computed tags
          labels: ${{ steps.meta.outputs.labels }}  # OCI metadata labels
          cache-from: type=gha         # reuse cache
          cache-to: type=gha,mode=max  # store cache
          provenance: true             # attach build provenance attestation
      - name: Print digest             # digest is the immutable identity
        run: echo "Pushed digest ${{ steps.build.outputs.digest }}"
```

---

## 🟠 My Stack Integration
Push one repo per service: `myorg/api` (Node.js), `myorg/ml-api` (FastAPI), `myorg/web` (React + Nginx). The VPS compose file refers to the SHA tag written by the deploy job.

```yaml
# docker-compose.prod.yml on the VPS (images pulled from Docker Hub)
services:
  api:
    image: myorg/api:${TAG:-latest}    # TAG exported by the deploy script
    restart: unless-stopped            # restart after crash/reboot
    env_file: .env                     # secrets stay on the server
  web:
    image: myorg/web:${TAG:-latest}    # React build served by nginx
    ports: ["80:80"]                   # public port
    depends_on: [api]                  # start api first
```

On the VPS run `docker login -u myorg` once (read-only token) so pulls are not rate-limited.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using the Docker Hub account password as the secret.
✅ Correct: Create a scoped access token (Read/Write for CI, Read-only for servers) and rotate it.

❌ Mistake 2: Pushing on pull requests from forks.
✅ Correct: Guard with `if: github.event_name != 'pull_request'` or trigger only on `push`.

❌ Mistake 3: Deploying `latest` and having no way to roll back.
✅ Correct: Deploy the SHA tag; keep `latest` only as a convenience.

❌ Mistake 4: Public repo by accident for proprietary code.
✅ Correct: Create the repo as private (free plan has limited private repos) and verify visibility.

---

## 🧠 Tricky Interview Question
The workflow log says "pushed", yet the server still runs old code after `docker compose up -d`. Why?

Answer: The compose file uses a mutable tag (`latest`) and the server already has a local `latest`; `up -d` does not re-pull. You need `docker compose pull` first (or `--pull always`), and better, deploy an immutable SHA/digest tag so a changed tag forces a new pull.

---

## ⚫ Interview Questions + Answers

Q1: Why use an access token rather than a password?
A1: Tokens are scoped, revocable and bypass 2FA prompts safely; a leaked token does not expose the account.

Q2: What is the difference between a tag and a digest?
A2: A tag is a movable label; a digest (`sha256:...`) is the content hash and never changes. Pinning by digest guarantees the exact image.

Q3: How do you avoid Docker Hub rate limits?
A3: Authenticate pulls, cache base images, mirror to ECR/GHCR, or use a pull-through cache.

Q4: Why `if: github.ref == 'refs/heads/main'` before login?
A4: Secrets are unavailable to fork PRs and you never want PR code publishing images.

Q5: What does multi-arch (`platforms`) give you?
A5: One tag works on amd64 servers and arm64 (Graviton, Apple Silicon); the registry serves the right manifest per client.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want the simplest registry and public images.
- Small teams, open-source projects.

❌ Avoid when:
- You are fully on AWS (ECR gives IAM auth, no rate limits).
- You already use GitHub and want repo-linked permissions (GHCR).
- Strict compliance needs private, in-account registries.

---

## 📊 Visual Diagram
```
GitHub Actions runner                 Docker Hub                 VPS / ECS
┌──────────────────────┐   login      ┌──────────────┐  pull    ┌──────────┐
│ build image          │────token────►│ myorg/api    │◄─────────│ docker   │
│ tags: sha-3f9a1c2    │   push       │  :sha-3f9a1c2│          │ compose  │
│       latest         │─────────────►│  :latest     │          │ up -d    │
└──────────────────────┘              └──────────────┘          └──────────┘
        secrets: DOCKERHUB_USERNAME / DOCKERHUB_TOKEN
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Registry | Server that stores images | images का store |
| Repository | Named set of image tags | एक image के सारे tags |
| Access token | Scoped, revocable credential | सीमित अधिकार वाली चाबी |
| Rate limit | Max pulls per period | pull की सीमा |
| Manifest | Describes layers and platforms | image का विवरण |
| Digest | Content hash of image | content की पहचान |

---

## ⚡ 3-Line Summary
English: Log in with an access token, push SHA and release tags from main only. Servers pull the immutable tag. Authenticate pulls to avoid rate limits.
Hindi: Access token से login करो, सिर्फ main से SHA और release tags push करो। Server immutable tag pull करता है। Rate limit से बचने के लिए pull भी authenticated रखो।

---

## ➡️ Next Topic
**338. Push to GitHub Container Registry** - same flow, but permissions come from `GITHUB_TOKEN`, with no extra secrets.
