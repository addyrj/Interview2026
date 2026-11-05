# 338. Push to GitHub Container Registry (GHCR)
# हिंदी में: GitHub Container Registry पर Push करना

---

## 🔵 Simple Definition (English)
GHCR (`ghcr.io`) is GitHub's own container registry. A workflow can push to it using the built-in `GITHUB_TOKEN` when the job has `packages: write` permission, so no extra registry account or stored password is needed.

## 🔵 सरल परिभाषा (Hindi)
GHCR (`ghcr.io`) GitHub की अपनी container registry है। Workflow में `packages: write` permission देने पर built-in `GITHUB_TOKEN` से push हो जाता है, अलग registry account या stored password नहीं चाहिए।

---

## 🔴 Problem it Solves
With Docker Hub you manage a second account, tokens and rate limits, and package access is not tied to repo permissions. GHCR links images to the repo: whoever can read the repo can pull (for private images), and CI authenticates with a short-lived token that expires after the job.

## 🔴 यह क्यों बना? (Hindi)
Docker Hub में दूसरा account, tokens और rate limits संभालने पड़ते हैं, और package access repo permissions से जुड़ा नहीं होता। GHCR image को repo से जोड़ता है: repo पढ़ सकने वाला private image pull कर सकता है, और CI एक short-lived token से login करता है जो job के बाद expire हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Workflow declares permissions: packages: write, contents: read
Step 2 → login-action: registry ghcr.io, user github.actor, pass GITHUB_TOKEN
Step 3 → Image name must be lowercase: ghcr.io/<owner>/<repo>
Step 4 → build-push-action pushes tags
Step 5 → Package appears under the repo/org "Packages"
Step 6 → Servers pull using a Personal Access Token (read:packages)
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Workflow में `permissions: packages: write, contents: read` घोषित करो।
Step 2 → login: registry `ghcr.io`, user `github.actor`, password `GITHUB_TOKEN`।
Step 3 → Image name lowercase होना चाहिए: `ghcr.io/<owner>/<repo>`।
Step 4 → `build-push-action` tags push करता है।
Step 5 → Package repo/org के "Packages" में दिखता है।
Step 6 → Servers `read:packages` वाले Personal Access Token से pull करते हैं।

---

## 🟡 Real World Example
A company already uses GitHub for code and Actions for CI. Their `acme/orders-api` repo pushes to `ghcr.io/acme/orders-api:sha-ab12cd3`. Developers get access through team membership, and the VPS uses a fine-grained read-only token. No Docker Hub subscription is needed, and there are no anonymous pull limits for their private images.

## 🟡 Real Example Hindi mein
एक company code और CI के लिए पहले से GitHub इस्तेमाल करती है। उसकी `acme/orders-api` repo `ghcr.io/acme/orders-api:sha-ab12cd3` पर push करती है। Developers को team membership से access मिलता है, और VPS read-only token इस्तेमाल करता है। Docker Hub subscription नहीं चाहिए।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/push-ghcr.yml (basic)
name: push-ghcr                        # workflow name
on:
  push:
    branches: [main]                   # only on main
permissions:
  contents: read                       # read the repo
  packages: write                      # allow pushing to GHCR
jobs:
  push:
    runs-on: ubuntu-latest             # runner
    steps:
      - uses: actions/checkout@v4      # get code
      - uses: docker/login-action@v3   # login to GHCR
        with:
          registry: ghcr.io            # registry host
          username: ${{ github.actor }}        # user who triggered the run
          password: ${{ secrets.GITHUB_TOKEN }}  # automatic, short-lived token
      - uses: docker/build-push-action@v6      # build and push
        with:
          context: .                   # build context
          push: true                   # upload image
          tags: ghcr.io/${{ github.repository }}:latest   # must be lowercase
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/push-ghcr-advanced.yml
name: push-ghcr-advanced
on:
  push:
    branches: [main]
    tags: ["v*.*.*"]
env:
  REGISTRY: ghcr.io                    # registry host
  IMAGE_NAME: ${{ github.repository }} # owner/repo (metadata-action lowercases it)
permissions:
  contents: read
  packages: write                      # push
  id-token: write                      # needed for keyless signing
  attestations: write                  # needed for build attestation
jobs:
  push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta                       # tags and labels
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,format=long       # full commit SHA tag
            type=semver,pattern={{version}}
            type=raw,value=latest,enable={{is_default_branch}}
      - id: build
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}   # links image to the repo
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - name: Attest build provenance  # signed supply-chain proof
        uses: actions/attest-build-provenance@v1   # example version, update
        with:
          subject-name: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}   # image name
          subject-digest: ${{ steps.build.outputs.digest }}         # exact digest
          push-to-registry: true       # store attestation next to image
```

---

## 🟠 My Stack Integration
Pull on the VPS with a classic PAT (`read:packages`) or fine-grained token stored only on the server.

```bash
# On the VPS: one-time login (token read from a root-only file, not shell history)
cat /root/.ghcr_token | docker login ghcr.io -u addyrj --password-stdin
# Deploy: pull the SHA tag and restart
export TAG=sha-3f9a1c2
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

```yaml
# docker-compose.prod.yml fragment
services:
  api:
    image: ghcr.io/addyrj/api:${TAG}   # Node.js or FastAPI image on GHCR
    restart: unless-stopped            # auto restart
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `packages: write` so push returns "denied".
✅ Correct: Add it at job or workflow `permissions`.

❌ Mistake 2: Uppercase in image name (`ghcr.io/MyOrg/App`).
✅ Correct: Lowercase only; use metadata-action or `${GITHUB_REPOSITORY,,}`.

❌ Mistake 3: Package not linked to repo, so `GITHUB_TOKEN` cannot push the next time.
✅ Correct: Add the `org.opencontainers.image.source` label (metadata-action does) or grant the repo access in package settings.

❌ Mistake 4: Using your personal PAT with full scopes on the server.
✅ Correct: Use a token with only `read:packages`.

---

## 🧠 Tricky Interview Question
Push works for the first run but fails with 403 on a later run from a different repo. Why?

Answer: The package was created and is owned/linked to the first repo. A workflow in another repo has no write access to that package unless you add that repo under Package settings > "Manage Actions access". Also, packages first pushed are private by default.

---

## ⚫ Interview Questions + Answers

Q1: Why is `GITHUB_TOKEN` safer than a PAT?
A1: It is auto-generated per job, scoped by `permissions`, and expires when the job ends.

Q2: Can PRs from forks push to GHCR?
A2: No. Fork PRs get a read-only token, which is by design.

Q3: How do you make a GHCR image public?
A3: Package settings > Change visibility. Public images can be pulled anonymously.

Q4: GHCR vs Docker Hub vs ECR?
A4: GHCR: tied to GitHub permissions. Docker Hub: largest public ecosystem, rate limits. ECR: IAM auth, best on AWS.

Q5: How do you clean old images?
A5: Use `actions/delete-package-versions` or retention rules to remove untagged and old SHA versions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Code and CI are already on GitHub.
- You want repo-based access control with no extra secrets.

❌ Avoid when:
- Your runtime is AWS and you prefer IAM roles (ECR).
- You need very high-volume pulls from outside GitHub with strict SLAs.

---

## 📊 Visual Diagram
```
 workflow (permissions: packages: write)
        │  GITHUB_TOKEN (short-lived)
        ▼
 ┌───────────────────┐  push  ┌────────────────────────────┐
 │ build-push-action │───────►│ ghcr.io/owner/repo:sha-... │
 └───────────────────┘        └──────────────┬─────────────┘
                                             │ pull (PAT read:packages)
                                             ▼
                                        VPS / server
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GHCR | GitHub's container registry | GitHub की registry |
| GITHUB_TOKEN | Auto token per job | हर job का अपना token |
| permissions | Scopes granted to that token | token के अधिकार |
| PAT | Personal access token | निजी access token |
| Provenance | Proof of how image was built | build का प्रमाण |
| OCI label | Standard image metadata | image का metadata |

---

## ⚡ 3-Line Summary
English: GHCR needs `packages: write` and GITHUB_TOKEN, no stored password. Image names must be lowercase and linked to a repo. Servers pull with a read-only PAT.
Hindi: GHCR को `packages: write` और GITHUB_TOKEN चाहिए, password store नहीं करना। Image name lowercase और repo से linked हो। Servers read-only PAT से pull करें।

---

## ➡️ Next Topic
**339. Push to AWS ECR** - the AWS-native registry with IAM authentication, ideal for ECS/EKS/EC2 deployments.
