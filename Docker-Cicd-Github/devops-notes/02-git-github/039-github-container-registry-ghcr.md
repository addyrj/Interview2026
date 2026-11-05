---

# 39. GitHub Container Registry (GHCR)
# हिंदी में: GitHub Container Registry (GHCR) — Docker images का भंडार

---

## 🔵 Simple Definition (English)
**GHCR** (`ghcr.io`) is GitHub's registry for container images (Docker/OCI). You push images to `ghcr.io/OWNER/IMAGE:TAG` and pull them on any server. It uses GitHub identity and permissions, integrates with Actions via `GITHUB_TOKEN`, and supports public and private images.

## 🔵 सरल परिभाषा (Hindi)
**GHCR** (`ghcr.io`) container images (Docker/OCI) के लिए GitHub का registry है। आप images को `ghcr.io/OWNER/IMAGE:TAG` पर push करते हैं और किसी भी server पर pull करते हैं। यह GitHub identity और permissions इस्तेमाल करता है, Actions में `GITHUB_TOKEN` से जुड़ता है, और public व private दोनों images सपोर्ट करता है।

---

## 🔴 Problem it Solves
Building the image on the production VPS (`docker compose up --build`) is slow, uses server CPU/RAM, needs source code and build tools on the server, and gives no immutable artifact to roll back to. A registry lets CI build once, tag precisely (git SHA), and servers just pull the exact tested image. Docker Hub adds pull rate limits; GHCR sits next to your code with unified access control.

## 🔴 यह क्यों बना? (Hindi)
Production VPS पर image बनाना (`docker compose up --build`) धीमा है, server का CPU/RAM खाता है, server पर source code और build tools चाहिए, और rollback के लिए कोई immutable artifact नहीं मिलता। Registry से CI एक बार build करता है, git SHA से tag लगाता है, और servers सिर्फ वही tested image pull करते हैं। Docker Hub पर pull rate limits हैं; GHCR आपके code के पास है और access control एक जगह है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Image name: ghcr.io/<lowercase-owner>/<image>:<tag>
Step 2 → In Actions: docker/login-action with registry ghcr.io, username github.actor, password GITHUB_TOKEN
Step 3 → Job permissions: packages: write (and contents: read)
Step 4 → docker/build-push-action builds and pushes (tags: latest, sha, semver)
Step 5 → First push creates a package linked to the repo (private by default for private repos); set visibility in package settings
Step 6 → Server: docker login ghcr.io -u USER --password-stdin (PAT with read:packages) -> docker pull
Step 7 → Deploy by IMMUTABLE tag (sha-abc123) or digest (@sha256:...) -- not by `latest`
Step 8 → Rollback = redeploy the previous tag; cleanup old versions with a retention policy
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Image नाम: ghcr.io/<lowercase-owner>/<image>:<tag>
Step 2 → Actions में: docker/login-action, registry ghcr.io, username github.actor, password GITHUB_TOKEN
Step 3 → Job permissions: packages: write (और contents: read)
Step 4 → docker/build-push-action build और push करता है (tags: latest, sha, semver)
Step 5 → पहला push package बनाता है जो repo से जुड़ता है; visibility package settings में बदलो
Step 6 → Server पर: docker login ghcr.io -u USER --password-stdin (read:packages वाला PAT) -> docker pull
Step 7 → IMMUTABLE tag (sha-abc123) या digest (@sha256:...) से deploy करो -- `latest` से नहीं
Step 8 → Rollback = पिछला tag दोबारा deploy; पुराने versions retention policy से साफ़ करो
```

---

## 🟡 Real World Example
A startup runs a FastAPI API and a Node.js worker on one AWS EC2 instance behind Nginx. On every merge to `main`, GitHub Actions builds both images, pushes `ghcr.io/acme/api:sha-3f9c2ab`, scans with Trivy, then SSHes into EC2 and runs `docker compose pull && docker compose up -d` with that tag. When release 3f9c2ab breaks login, they redeploy `sha-91d0e7c` in 30 seconds, since images are immutable and stored. The server never had source code or build tools.

## 🟡 Real Example Hindi mein
एक startup एक AWS EC2 instance पर Nginx के पीछे FastAPI API और Node.js worker चलाता है। हर `main` merge पर GitHub Actions दोनों images build करता है, `ghcr.io/acme/api:sha-3f9c2ab` push करता है, Trivy से scan करता है, फिर EC2 पर SSH करके उसी tag के साथ `docker compose pull && docker compose up -d` चलाता है। Release 3f9c2ab से login टूटे तो वे 30 सेकंड में `sha-91d0e7c` दोबारा deploy कर देते हैं, क्योंकि images immutable और stored हैं। Server पर कभी source code या build tools नहीं थे।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# ghcr-manual.sh - push an image to GHCR from your laptop (CI is preferred)
set -euo pipefail                                    # strict mode
OWNER="acme"                                         # your lowercase GitHub user/org (example)
IMAGE="ghcr.io/$OWNER/api"                           # full image name without tag

# PAT (classic) needs write:packages; keep it in an env var, never in the script
echo "$GHCR_PAT" | docker login ghcr.io -u "$GITHUB_USER" --password-stdin   # login; token read from stdin

docker build -t "$IMAGE:1.0.0" .                     # build the image from ./Dockerfile
docker tag "$IMAGE:1.0.0" "$IMAGE:latest"            # add a second tag (convenience only)
docker push "$IMAGE:1.0.0"                           # push the versioned tag
docker push "$IMAGE:latest"                          # push the moving tag

# On the server (needs a token with read:packages):
# echo "$GHCR_READ_PAT" | docker login ghcr.io -u "$GITHUB_USER" --password-stdin
# docker pull ghcr.io/acme/api:1.0.0
```
(Not run here: no Docker daemon available on the authoring machine.)

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/docker-ghcr.yml - build, tag, push to GHCR, deploy to VPS by immutable tag
name: Build and push image                  # workflow name
on:
  push:
    branches: [main]                        # build on every merge to main
    tags: ["v*.*.*"]                        # and on release tags
env:
  REGISTRY: ghcr.io                         # registry host
  IMAGE_NAME: ${{ github.repository }}      # owner/repo (GHCR needs lowercase; see step below)
permissions:
  contents: read                            # read repo
  packages: write                           # push to GHCR
jobs:
  build:                                    # job id
    runs-on: ubuntu-latest                  # hosted runner
    outputs:
      image: ${{ steps.vars.outputs.image }}   # pass lowercase image name to deploy job
    steps:
      - uses: actions/checkout@v4           # code (example version)
      - name: Lowercase image name          # label: GHCR requires lowercase
        id: vars                            # id to read outputs
        run: echo "image=${REGISTRY}/${IMAGE_NAME,,}" >> "$GITHUB_OUTPUT"   # ${VAR,,} = bash lowercase
      - uses: docker/setup-buildx-action@v3 # BuildKit builder (example version)
      - uses: docker/login-action@v3        # login to GHCR
        with:
          registry: ghcr.io                 # registry host
          username: ${{ github.actor }}     # user that triggered the run
          password: ${{ secrets.GITHUB_TOKEN }}   # built-in token (needs packages: write)
      - uses: docker/metadata-action@v5     # computes tags and OCI labels
        id: meta                            # id for outputs
        with:
          images: ${{ steps.vars.outputs.image }}   # target image name
          tags: |                           # tag rules
            type=sha,format=long,prefix=sha-
            type=semver,pattern={{version}}
            type=raw,value=latest,enable={{is_default_branch}}
      - uses: docker/build-push-action@v6   # build and push
        with:
          context: .                        # build context
          push: true                        # push after build
          tags: ${{ steps.meta.outputs.tags }}       # tags from metadata action
          labels: ${{ steps.meta.outputs.labels }}   # labels (source repo link etc.)
          cache-from: type=gha              # reuse GitHub Actions cache
          cache-to: type=gha,mode=max       # save cache for next run
  deploy:                                   # job 2: roll out on the VPS
    needs: build                            # after the image exists
    if: github.ref == 'refs/heads/main'     # only from main
    runs-on: ubuntu-latest                  # hosted runner
    environment: production                 # approvals + prod secrets
    steps:
      - name: Pull and restart on VPS       # label
        uses: appleboy/ssh-action@v1.0.3    # example version; pin SHA in production
        env:
          APP_IMAGE: ${{ needs.build.outputs.image }}:sha-${{ github.sha }}   # see note below on tag length
        with:
          host: ${{ secrets.VPS_HOST }}     # server address
          username: ${{ secrets.VPS_USER }} # deploy user
          key: ${{ secrets.VPS_SSH_KEY }}   # deploy key
          envs: APP_IMAGE                   # forward this runner env var to the remote shell
          script: |                         # commands run on the server
            cd /srv/app && docker compose pull api && docker compose up -d api
```
Note: `type=sha,format=long` makes the tag `sha-<40 chars>`, which matches `github.sha` used in the deploy job. Workflow only YAML-parsed here, not run on GitHub.

---

## 🟠 My Stack Integration
Server-side `docker-compose.yml` pulls from GHCR instead of building; Nginx keeps proxying to the container port. FastAPI and Node images share the same pattern.

```yaml
# /srv/app/docker-compose.yml on the VPS (pulls prebuilt images)
services:
  api:                                      # FastAPI service
    image: ${APP_IMAGE:-ghcr.io/acme/api:latest}   # image from env var set at deploy; default is for dev only
    restart: unless-stopped                 # restart after crash or reboot
    env_file: .env                          # secrets stored only on the server, chmod 600
    ports:
      - "127.0.0.1:8000:8000"               # bind to localhost; Nginx proxy_pass http://127.0.0.1:8000
    healthcheck:                            # lets Docker know if the app is healthy
      test: ["CMD", "python", "-c", "import urllib.request;urllib.request.urlopen('http://localhost:8000/health')"]   # simple HTTP check
      interval: 30s                         # check every 30 seconds
      timeout: 5s                           # fail check after 5 seconds
      retries: 3                            # unhealthy after 3 failures
```
Security: package visibility defaults to private for private repos; use read-only PATs on servers (or a GitHub App), rotate them, scan images (Trivy/Grype) before deploy, run containers as non-root, deploy by digest/sha not `latest`, and set `docker/metadata-action` labels so each image links to its source repo and commit.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Uppercase letters in the image path (`ghcr.io/Acme/Api`).
✅ Correct: Repository/image names must be lowercase; convert with `${VAR,,}`.

❌ Mistake 2: Deploying `:latest` in production, so you cannot tell or roll back what runs.
✅ Correct: Deploy `sha-xxxx` or a semver tag, and record it.

❌ Mistake 3: Forgetting `permissions: packages: write`, causing "denied: permission_denied".
✅ Correct: Add it to the job/workflow and ensure the package is linked to the repo with Actions write access.

❌ Mistake 4: Using a personal PAT with broad scopes on the server.
✅ Correct: Use a token with only `read:packages`, ideally from a machine/bot account, and rotate.

---

## 🧠 Tricky Interview Question
CI pushed `ghcr.io/acme/api:latest` successfully, but `docker pull` on the VPS says "unauthorized" even though you are logged in as a team member. What are the likely causes?

Answer: (1) The token lacks `read:packages` (classic PAT needs it; fine-grained tokens do not yet cover packages in all cases). (2) The package is private and your account has no access to this package (package permissions are separate from repo ones if not inherited). (3) SSO is enforced and the PAT is not authorized for the org. (4) The login was done for a different registry (docker.io) or `~/.docker/config.json` is under another user (e.g. root vs deploy user). Fix: check `docker logout/login ghcr.io` as the same user running compose and verify package access settings.

---

## ⚫ Interview Questions + Answers

Q1: GHCR vs Docker Hub?
A1: GHCR integrates with GitHub identity/permissions, `GITHUB_TOKEN` and has no anonymous pull limits for public images in the same way Docker Hub does; Docker Hub has the largest public ecosystem and its own rate limits.

Q2: How does Actions authenticate to GHCR?
A2: `docker/login-action` with `registry: ghcr.io`, `username: ${{ github.actor }}`, `password: ${{ secrets.GITHUB_TOKEN }}` and `packages: write`.

Q3: Why tag with the git SHA?
A3: It makes the image immutable and traceable to the commit; rollback means deploying an older SHA.

Q4: What is an image digest?
A4: The `sha256:` content hash of the manifest. Pulling by digest guarantees the exact bytes, regardless of tag moves.

Q5: How to delete old images?
A5: Use package settings, the API (`gh api -X DELETE /orgs/OWNER/packages/container/NAME/versions/ID`), or a retention action such as `actions/delete-package-versions`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Your code lives on GitHub and you deploy containers via Actions
- You want per-repo/org access control and build provenance labels

❌ Avoid when:
- You are fully on AWS and prefer ECR (IAM, same-region pulls, vulnerability scanning built in)
- You need geo-replication or enterprise policies only offered by another registry

---

## 📊 Visual Diagram
```
 git push main
     |
 GitHub Actions
   build image --> tag: sha-3f9c2ab, latest
     |  docker push (GITHUB_TOKEN, packages: write)
     v
 [ ghcr.io/acme/api ]  <--- immutable versions, private
     |
     |  docker pull (token: read:packages)
     v
 AWS EC2 / VPS:  docker compose up -d
     |
  Nginx :443  -->  127.0.0.1:8000 (FastAPI container)
 rollback: pull previous sha tag
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GHCR | GitHub's container registry (ghcr.io) | GitHub का container registry |
| Tag | Human label of an image version | image version का नाम |
| Digest | Content hash identifying exact image | image की सटीक पहचान (hash) |
| OCI | Open Container Initiative image standard | container image मानक |
| docker/login-action | Action for registry login | registry login action |
| Immutable tag | Tag never reused (e.g., SHA) | कभी न बदलने वाला tag |

---

## ⚡ 3-Line Summary
English: GHCR stores Docker images at `ghcr.io/owner/image`, authenticated with GitHub tokens.
CI builds once and pushes SHA-tagged images; servers only pull and run.
Use lowercase names, read-only tokens on servers, and never deploy `latest` to production.
Hindi: GHCR Docker images को `ghcr.io/owner/image` पर रखता है, GitHub tokens से authenticate होकर।
CI एक बार build करके SHA-tagged images push करता है; servers सिर्फ pull करके चलाते हैं।
नाम lowercase रखो, servers पर read-only tokens, और production में `latest` कभी deploy मत करो।

---

## ➡️ Next Topic
**40. GitHub Actions basics** (next section of the notes): now that code, secrets, environments and images are ready, learn how workflows automate the entire pipeline.

---
