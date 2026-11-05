# 125. Pushing to Docker Hub
# हिंदी में: Docker Hub पर image push करना

---

## 🔵 Simple Definition (English)
Docker Hub (`docker.io`) is the default public registry. Pushing means tagging a local image as `username/repo:tag`, logging in, and running `docker push` so the layers are uploaded and anyone (or your servers) can pull it.

## 🔵 सरल परिभाषा (Hindi)
Docker Hub (`docker.io`) default public registry है। Push का मतलब है local image को `username/repo:tag` नाम देना, login करना और `docker push` चलाना, ताकि layers upload हों और कोई भी (या आपके servers) उसे pull कर सकें।

---

## 🔴 Problem it Solves
- An image built on your laptop or CI runner exists only there. The VPS cannot run it.
- Copying images with `docker save` and scp is slow and manual.
- A registry gives one central, versioned place that every server pulls from.

## 🔴 यह क्यों बना? (Hindi)
- आपके laptop या CI runner पर बनी image सिर्फ वहीं रहती है। VPS उसे चला नहीं सकता।
- `docker save` और scp से images कॉपी करना धीमा और manual है।
- Registry एक केंद्रीय, versioned जगह देती है जहाँ से हर server pull करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create account + repository on hub.docker.com (public free; private limited on free plan)
Step 2 → Create an Access Token (Account Settings -> Security) with Read & Write scope
Step 3 → docker login -u <user> (paste TOKEN as password)  -> creds saved in ~/.docker/config.json
Step 4 → docker build -t myorg/api:1.0.0 .   (name = namespace/repo:tag)
Step 5 → docker push myorg/api:1.0.0         (only missing layers are uploaded)
Step 6 → On the server: docker pull myorg/api:1.0.0 -> docker compose up -d
Step 7 → Automate in GitHub Actions with docker/login-action + build-push-action
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → hub.docker.com पर account + repository बनाएँ (public free; private की सीमा free plan में)
Step 2 → Access Token बनाएँ (Account Settings -> Security) Read & Write scope के साथ
Step 3 → docker login -u <user> (password की जगह TOKEN डालें) -> creds ~/.docker/config.json में
Step 4 → docker build -t myorg/api:1.0.0 .   (नाम = namespace/repo:tag)
Step 5 → docker push myorg/api:1.0.0         (सिर्फ missing layers upload होती हैं)
Step 6 → Server पर: docker pull myorg/api:1.0.0 -> docker compose up -d
Step 7 → GitHub Actions में docker/login-action + build-push-action से automate करें
```

---

## 🟡 Real World Example
A freelancer deploys a FastAPI app to a $6 VPS. GitHub Actions builds `myorg/fastapi-app` on every push to main, tags it with the commit SHA and `latest`, and pushes to Docker Hub. A deploy step SSHes into the VPS and runs `docker compose pull && docker compose up -d`. Build time is spent on GitHub's runners, not on the tiny VPS.

## 🟡 Real Example Hindi mein
एक freelancer $6 के VPS पर FastAPI app deploy करता है। GitHub Actions हर main push पर `myorg/fastapi-app` build करता है, commit SHA और `latest` से tag करता है और Docker Hub पर push करता है। Deploy step VPS में SSH करके `docker compose pull && docker compose up -d` चलाता है। Build का बोझ छोटे VPS पर नहीं, GitHub के runners पर पड़ता है।

---

## 💻 Code / Config Example — Basic
```bash
# 1. Log in with an ACCESS TOKEN (not your account password). Prompts for the token
docker login -u myuser                                 # saves credentials for docker.io

# 2. Build and name the image: <hub-username-or-org>/<repo>:<tag>
docker build -t myuser/api:1.0.0 .                     # local build with the full registry name

# 3. Add a second tag to the SAME image (no rebuild; just another name)
docker tag myuser/api:1.0.0 myuser/api:latest          # latest points to the same image ID

# 4. Push both tags; shared layers are uploaded once
docker push myuser/api:1.0.0                           # push the version tag
docker push myuser/api:latest                          # push moving tag (optional convenience)

# 5. Verify from anywhere
docker pull myuser/api:1.0.0                           # pulls what you just uploaded

# 6. Log out on shared machines
docker logout                                          # removes stored credentials
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/dockerhub.yml  (example versions: verify before use)
name: build-push-dockerhub                     # workflow name
on:
  push:
    branches: [main]                           # build when main changes
    tags: ['v*.*.*']                           # and when a version tag is pushed
permissions:
  contents: read                               # least privilege
jobs:
  push:
    runs-on: ubuntu-latest                     # hosted runner
    steps:
      - uses: actions/checkout@v4              # get source
      - uses: docker/setup-qemu-action@v3      # allow multi-arch emulation
      - uses: docker/setup-buildx-action@v3    # buildx builder with cache support
      - name: Log in to Docker Hub
        uses: docker/login-action@v3           # official login action
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}   # Hub username in secrets
          password: ${{ secrets.DOCKERHUB_TOKEN }}      # access TOKEN in secrets
      - name: Generate tags and labels
        id: meta                               # exposes steps.meta.outputs.*
        uses: docker/metadata-action@v5        # builds tag list from git info
        with:
          images: myorg/api                    # Docker Hub repo name
          tags: |                              # tag rules
            type=sha,format=short              # short git SHA tag, e.g. sha-3f9a1c2
            type=semver,pattern={{version}}    # 1.2.3 from tag v1.2.3
            type=raw,value=latest,enable={{is_default_branch}}  # latest only on main
      - name: Build and push
        uses: docker/build-push-action@v6      # build + push in one step
        with:
          context: ./api                       # folder with Dockerfile
          platforms: linux/amd64,linux/arm64   # multi-arch image
          push: true                           # upload to Docker Hub
          tags: ${{ steps.meta.outputs.tags }}       # tags computed above
          labels: ${{ steps.meta.outputs.labels }}   # OCI labels computed above
          cache-from: type=gha                 # reuse layer cache from GitHub cache
          cache-to: type=gha,mode=max          # save cache for next run
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI:** one repo per service: `myorg/node-api`, `myorg/fastapi-app`. Tag by SHA, keep `latest` for convenience only.
- **React:** push the final Nginx static image `myorg/web`; or skip the registry and upload `dist/` to S3, depending on your design.
- **Nginx / VPS:** the VPS compose file uses `image:` instead of `build:`, so servers only pull.
- **AWS:** if the app later moves to ECS, switch to ECR (note 127) to avoid Docker Hub pull-rate limits.
- **Rate limits:** anonymous and free accounts have pull limits per 6 hours (check current numbers in Docker docs). A VPS should `docker login` before pulling.

```yaml
# docker-compose.prod.yml on the VPS (pull only, no build)
services:
  api:                                         # Node.js / FastAPI container
    image: myorg/api:${TAG:?TAG is required}   # tag comes from the deploy script; fail if missing
    env_file: .env                             # secrets stay on the server, not in the image
    restart: unless-stopped                    # auto restart
    ports:
      - "127.0.0.1:8000:8000"                  # only Nginx on the host can reach it
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using your Docker Hub password in CI.
✅ Correct: Use an access token with only the scope needed (Read & Write, or Read-only for servers) and keep it in GitHub Secrets.

❌ Mistake 2: Forgetting the namespace: `docker push api:1.0.0` fails with "denied: requested access".
✅ Correct: Tag as `myuser/api:1.0.0` first.

❌ Mistake 3: Pushing images that contain `.env`, SSH keys or source secrets to a public repo.
✅ Correct: Use `.dockerignore`, build secrets (`--secret`), and scan; assume public images are read by everyone. Rotate a secret if it was ever pushed.

❌ Mistake 4: Deploying only `latest`.
✅ Correct: Deploy a SHA or version tag so rollback is possible (note 105).

---

## 🧠 Tricky Interview Question
`docker push` says "denied: requested access to the resource is denied" although `docker login` succeeded. Why?

Answer: Common causes: (1) the image name has no or wrong namespace, so Docker tries `docker.io/library/api`; (2) the logged-in user is not a member of the org that owns the repo or the token has Read-only scope; (3) the repo does not exist and the plan blocks auto-creating private repos; (4) you logged in to a different registry than the image name points at. Fix by checking `docker images`, the full name and the token scope.

---

## ⚫ Interview Questions + Answers

Q1: What is the full name format of an image?
A1: `[registry-host/]namespace/repository:tag`. For Docker Hub the host `docker.io` is implied.

Q2: Why use an access token?
A2: It can be scoped and revoked without changing the account password and is safe to store in CI.

Q3: What happens if you push the same tag twice?
A3: The tag moves to the new image. The old image stays as an untagged manifest but is no longer reachable by that name.

Q4: How do you avoid Hub rate limits?
A4: Log in before pulling, mirror/cache images (note 129), or store images in ECR/GHCR.

Q5: How to push a multi-architecture image?
A5: `docker buildx build --platform linux/amd64,linux/arm64 --push -t myorg/api:1.0.0 .`

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Open source images, quick personal projects, public base images.
- Simple small-team deploys to a VPS.

❌ Avoid when:
- Strict private enterprise images needing IAM (prefer ECR) or tight GitHub integration (prefer GHCR).
- Heavy pulls from many servers that could hit rate limits.

---

## 📊 Visual Diagram
```
 Laptop / GitHub Actions                Docker Hub (docker.io)              VPS / EC2
 +--------------------+  docker push   +-----------------------+  docker pull +---------+
 | docker build       | -------------> | myorg/api:1.0.0       | -----------> | compose |
 | -t myorg/api:1.0.0 |  (token auth)  | myorg/api:sha-3f9a1c2 |  (login)     | up -d   |
 +--------------------+                +-----------------------+              +---------+
        layers: only new ones uploaded        stores layers + manifest by digest
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Registry | Server storing images | images रखने वाला server |
| Repository | Collection of tags for one image | एक image के tags का संग्रह |
| Namespace | User or org prefix | user या org का prefix |
| Access token | Scoped password for CLI/CI | CLI/CI के लिए सीमित password |
| `docker tag` | Add another name to an image | image को दूसरा नाम देना |
| Rate limit | Max pulls per time | समय में अधिकतम pulls |

---

## ⚡ 3-Line Summary
English: Tag the image as `namespace/repo:tag`, log in with a token, then `docker push`.
English: Automate with `docker/login-action` and `build-push-action` using GitHub Secrets.
English: Tag by SHA/version and mind rate limits and public visibility.
Hindi: Image को `namespace/repo:tag` नाम दें, token से login करें, फिर `docker push`।
Hindi: GitHub Secrets के साथ `docker/login-action` और `build-push-action` से automate करें।
Hindi: SHA/version से tag करें और rate limits तथा public visibility का ध्यान रखें।

---

## ➡️ Next Topic
**126. Pushing to GitHub Container Registry** — a registry tied to your GitHub repo and permissions, with no extra account.
