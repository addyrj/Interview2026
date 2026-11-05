# 126. Pushing to GitHub Container Registry
# हिंदी में: GitHub Container Registry (GHCR) पर push करना

---

## 🔵 Simple Definition (English)
GitHub Container Registry (`ghcr.io`) stores Docker/OCI images next to your code. Access is controlled by GitHub permissions, and GitHub Actions can push with the built-in `GITHUB_TOKEN`, so no extra account or password is needed.

## 🔵 सरल परिभाषा (Hindi)
GitHub Container Registry (`ghcr.io`) आपके code के पास ही Docker/OCI images रखती है। Access GitHub permissions से नियंत्रित होता है, और GitHub Actions built-in `GITHUB_TOKEN` से push कर सकता है, यानी अलग account या password नहीं चाहिए।

---

## 🔴 Problem it Solves
- Docker Hub needs a separate account, tokens, and has pull rate limits.
- Managing who can pull which image duplicates the permission model you already have in GitHub.
- You want a package linked to the repository, with the same private/public setting and org teams.

## 🔴 यह क्यों बना? (Hindi)
- Docker Hub को अलग account, tokens चाहिए और pull rate limits हैं।
- कौन सी image कौन pull कर सकता है, यह प्रबंधन आपके GitHub के permission model की नकल बन जाता है।
- आप चाहते हैं कि package repository से जुड़ा हो, वही private/public setting और org teams हों।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Image name: ghcr.io/<owner>/<image>:<tag>  (owner must be LOWERCASE)
Step 2 → Auth for CI: GITHUB_TOKEN with permissions: packages: write (no secret to create)
Step 3 → Auth for humans/servers: Personal Access Token (classic) with read:packages (and write:packages to push)
Step 4 → docker login ghcr.io -u <username> --password-stdin  (token piped in)
Step 5 → docker push ghcr.io/myorg/api:1.0.0 -> package appears under the org/user "Packages"
Step 6 → Link to repo: LABEL org.opencontainers.image.source=<repo url> -> package inherits repo permissions
Step 7 → Visibility: new packages are private by default; change to public in package settings if needed
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Image नाम: ghcr.io/<owner>/<image>:<tag>  (owner छोटे अक्षरों में ज़रूरी)
Step 2 → CI के लिए auth: GITHUB_TOKEN, permissions: packages: write (कोई secret नहीं बनाना)
Step 3 → इंसानों/servers के लिए: Personal Access Token (classic) read:packages (push के लिए write:packages) के साथ
Step 4 → docker login ghcr.io -u <username> --password-stdin  (token pipe से)
Step 5 → docker push ghcr.io/myorg/api:1.0.0 -> package org/user के "Packages" में दिखता है
Step 6 → Repo से जोड़ें: LABEL org.opencontainers.image.source=<repo url> -> package repo की permissions लेता है
Step 7 → Visibility: नए packages default में private होते हैं; ज़रूरत हो तो package settings में public करें
```

---

## 🟡 Real World Example
A startup keeps its Node.js API in a private GitHub repo. The workflow builds and pushes `ghcr.io/startup/api:<sha>` using only `GITHUB_TOKEN`. A new developer joining the GitHub team automatically gets pull access through repo permissions. The VPS uses a read-only PAT stored in `/root/.docker/config.json` through `docker login`. No Docker Hub subscription is needed.

## 🟡 Real Example Hindi mein
एक startup अपना Node.js API private GitHub repo में रखता है। Workflow सिर्फ `GITHUB_TOKEN` से `ghcr.io/startup/api:<sha>` build और push करता है। GitHub team में नया developer जुड़ते ही repo permissions से उसे pull access मिल जाता है। VPS `docker login` से सिर्फ-पढ़ने वाला PAT इस्तेमाल करता है। Docker Hub subscription की ज़रूरत नहीं।

---

## 💻 Code / Config Example — Basic
```bash
# Put the Personal Access Token in an env var (create at GitHub -> Settings -> Developer settings)
export CR_PAT=ghp_xxxxxxxxxxxxxxxxxxxx                 # placeholder; scope: write:packages (read:packages for servers)

# Log in; --password-stdin keeps the token out of shell history and process list
echo "$CR_PAT" | docker login ghcr.io -u myuser --password-stdin   # myuser = your GitHub username

# Build with the full GHCR name (owner and image must be lowercase)
docker build -t ghcr.io/myorg/api:1.0.0 .              # local build

# Push to GHCR
docker push ghcr.io/myorg/api:1.0.0                    # first push creates a PRIVATE package

# Pull on another machine (needs login for private packages)
docker pull ghcr.io/myorg/api:1.0.0                    # same name

# Make the Dockerfile link the package to the repo (add this line to Dockerfile)
# LABEL org.opencontainers.image.source="https://github.com/myorg/api"
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/ghcr.yml  (example versions: verify before use)
name: build-push-ghcr                          # workflow name
on:
  push:
    branches: [main]                           # build on main
    tags: ['v*.*.*']                           # and on release tags
env:
  REGISTRY: ghcr.io                            # registry host
  IMAGE_NAME: ${{ github.repository }}         # owner/repo, e.g. myorg/api (GHCR needs lowercase; check your owner)
permissions:
  contents: read                               # read code
  packages: write                              # REQUIRED to push to GHCR with GITHUB_TOKEN
jobs:
  build-and-push:
    runs-on: ubuntu-latest                     # hosted runner
    steps:
      - uses: actions/checkout@v4              # fetch source
      - uses: docker/setup-buildx-action@v3    # buildx
      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}        # ghcr.io
          username: ${{ github.actor }}        # triggering user
          password: ${{ secrets.GITHUB_TOKEN }}# automatic token, no manual secret
      - name: Docker metadata
        id: meta                               # outputs: tags, labels
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}   # full image path
          tags: |                              # tag rules
            type=sha                           # sha-<short>
            type=semver,pattern={{version}}    # 1.2.3 for tag v1.2.3
            type=ref,event=branch              # main
      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .                           # Dockerfile at repo root
          push: true                           # upload
          tags: ${{ steps.meta.outputs.tags }}       # computed tags
          labels: ${{ steps.meta.outputs.labels }}   # includes image.source -> repo link automatically
          cache-from: type=gha                 # use Actions cache
          cache-to: type=gha,mode=max          # save cache
```

```bash
# On the VPS: one-time login with a READ-ONLY token, then deploy
echo "$GHCR_READ_TOKEN" | docker login ghcr.io -u deploy-bot --password-stdin   # token with read:packages only
docker compose -f docker-compose.prod.yml pull                                    # pull latest tags
docker compose -f docker-compose.prod.yml up -d                                   # recreate containers
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI / React:** each repo pushes to `ghcr.io/<owner>/<repo>`; in a monorepo use sub-names like `ghcr.io/myorg/shop/api` and `.../web`.
- **VPS:** deploy bot uses a PAT with only `read:packages` (or a fine-grained token if packages are supported for your use; check current GitHub docs).
- **AWS:** ECS can pull from GHCR using a Secrets Manager credential (`repositoryCredentials`); ECR is simpler inside AWS.
- **Security:** keep packages private, rotate PATs, prefer `GITHUB_TOKEN` for CI.

```yaml
# docker-compose.prod.yml (fragment)
services:
  api:                                         # Node.js / FastAPI service
    image: ghcr.io/myorg/api:${TAG}            # pull from GHCR; TAG set by deploy script
    restart: unless-stopped                    # keep running
  web:                                         # React static build served by Nginx
    image: ghcr.io/myorg/web:${TAG}            # same TAG for matching versions
    ports:
      - "80:80"                                # public HTTP port
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Uppercase in the owner or image name (`ghcr.io/MyOrg/Api`).
✅ Correct: Always lowercase; use `${GITHUB_REPOSITORY,,}` in bash or the metadata action, which lowercases.

❌ Mistake 2: Missing `permissions: packages: write`, giving "denied: installation not allowed to Create Organization Package".
✅ Correct: Set permissions in the workflow and check Org settings -> Actions -> workflow permissions.

❌ Mistake 3: Putting a PAT with broad scope (`repo`, `admin`) on the server.
✅ Correct: Use a token limited to `read:packages`.

❌ Mistake 4: Package not linked to the repo, so the repo's Actions cannot push later.
✅ Correct: Add the `image.source` label, or connect it in Package settings -> "Manage Actions access".

---

## 🧠 Tricky Interview Question
The workflow pushes to GHCR fine on the first run, but the next run from a different repo in the same org gets "permission denied" for the same package. Why?

Answer: A package is tied to the repository that first created it (via the source label) or has explicit Actions access list. Another repo's `GITHUB_TOKEN` has no write rights on it. Fix: in the package settings, add the second repo under "Manage Actions access" with Write role, or push to a separate image name per repo.

---

## ⚫ Interview Questions + Answers

Q1: Why choose GHCR over Docker Hub?
A1: Integrated with GitHub permissions, uses `GITHUB_TOKEN`, no separate account, and generous limits for pulls in Actions.

Q2: How does CI authenticate?
A2: `docker/login-action` with `username: ${{ github.actor }}`, `password: ${{ secrets.GITHUB_TOKEN }}` and `permissions: packages: write`.

Q3: What is the default visibility of a new package?
A3: Private (unless inherited from a public repo via the source label); you can change it in package settings.

Q4: How does a server pull a private package?
A4: `docker login ghcr.io` with a PAT that has `read:packages`.

Q5: Why must names be lowercase?
A5: OCI/Docker repository names do not allow uppercase letters.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Code is on GitHub and you want one place for permissions.
- CI/CD runs in GitHub Actions.

❌ Avoid when:
- Your runtime is deep inside AWS with IAM only auth (ECR is smoother).
- Your organization does not use GitHub.

---

## 📊 Visual Diagram
```
 GitHub repo myorg/api
   |  push to main
   v
 GitHub Actions  --GITHUB_TOKEN (packages: write)-->  ghcr.io/myorg/api:sha-3f9a1c2
                                                          |
              permissions inherited from repo/org         | docker pull (PAT: read:packages)
                                                          v
                                                    VPS / EC2 / k8s
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GHCR | GitHub Container Registry (`ghcr.io`) | GitHub की container registry |
| GITHUB_TOKEN | Auto token for a workflow run | workflow के लिए अपने आप बना token |
| PAT | Personal Access Token | व्यक्तिगत access token |
| Package visibility | private/public/internal | package कौन देख सकता है |
| image.source label | Links package to repo | package को repo से जोड़ने वाला label |
| `--password-stdin` | Safe way to pass a secret to login | secret सुरक्षित रूप से देने का तरीका |

---

## ⚡ 3-Line Summary
English: GHCR stores images at `ghcr.io/<owner>/<image>` with GitHub permissions.
English: CI pushes with `GITHUB_TOKEN` and `packages: write`; servers pull with a read-only PAT.
English: Use lowercase names and link packages to the repo with the source label.
Hindi: GHCR images को `ghcr.io/<owner>/<image>` पर GitHub permissions के साथ रखती है।
Hindi: CI `GITHUB_TOKEN` और `packages: write` से push करता है; servers सिर्फ-पढ़ने वाले PAT से pull करते हैं।
Hindi: नाम छोटे अक्षरों में रखें और source label से package को repo से जोड़ें।

---

## ➡️ Next Topic
**127. Pushing to AWS ECR** — the AWS-native private registry with IAM auth, lifecycle policies and built-in scanning.
