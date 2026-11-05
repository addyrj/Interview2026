# 226. Container Registry in Production
# हिंदी में: Production में Container Registry

---

## 🔵 Simple Definition (English)
A **container registry** is a server that stores and distributes container images (like GitHub for images). CI pushes images in, servers pull images out. Common choices: **Docker Hub**, **GitHub Container Registry (GHCR)**, **AWS ECR**, GitLab Registry, or self-hosted (Harbor, `registry:2`). In production the registry must be private, access-controlled, scanned, and highly available.

## 🔵 सरल परिभाषा (Hindi)
**Container registry** एक server है जो container images store और distribute करता है (images के लिए GitHub जैसा)। CI images push करता है, servers pull करते हैं। आम विकल्प: **Docker Hub**, **GitHub Container Registry (GHCR)**, **AWS ECR**, GitLab Registry, या self-hosted (Harbor, `registry:2`)। Production में registry private, access-controlled, scanned और highly available होनी चाहिए।

---

## 🔴 Problem it Solves
Copying images with `docker save` and `scp` does not scale. Public registries have pull-rate limits (Docker Hub throttles anonymous pulls), can be down during your deploy, and pushing company code to a public repo leaks source and secrets baked into layers. Without a proper registry there is no single source of truth for "which image is in production", no vulnerability scan, no retention policy (disks fill with old images), and no audit trail.

## 🔴 यह क्यों बना? (Hindi)
`docker save` और `scp` से images कॉपी करना scale नहीं करता। Public registries में pull-rate limits होती हैं (Docker Hub anonymous pulls throttle करता है), आपके deploy के समय down हो सकती हैं, और company code को public repo में डालने से source और layers में छुपे secrets leak होते हैं। सही registry के बिना "production में कौन-सी image है" का एक सच नहीं होता, vulnerability scan नहीं होता, retention policy नहीं होती (पुरानी images से disk भरती है) और audit trail नहीं मिलता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a private repository (e.g. ECR repo "myorg/node-api").
Step 2 → CI logs in with short-lived credentials (OIDC role, not a long-lived password).
Step 3 → CI builds the image and tags it:  registry/repo:git-sha  (immutable) and optional :1.4.2.
Step 4 → `docker push` uploads layers (only missing layers are sent) and the manifest.
Step 5 → Registry scans the image for CVEs and applies lifecycle rules (delete old untagged images).
Step 6 → Servers (VPS, ECS, K8s) authenticate and `docker pull` by tag, ideally by digest (@sha256:...).
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Private repository बनाओ (जैसे ECR repo "myorg/node-api")।
Step 2 → CI short-lived credentials से login करता है (OIDC role, long-lived password नहीं)।
Step 3 → CI image build करके tag लगाता है:  registry/repo:git-sha (immutable) और optional :1.4.2।
Step 4 → `docker push` layers (सिर्फ missing वाले) और manifest upload करता है।
Step 5 → Registry CVE scan करती है और lifecycle rules लगाती है (पुरानी untagged images delete)।
Step 6 → Servers (VPS, ECS, K8s) authenticate करके tag से, बेहतर होगा digest (@sha256:...) से, `docker pull` करते हैं।
```

Comparison / तुलना:

| Registry | Good for | Notes |
|----------|----------|-------|
| Docker Hub | Public base images | Pull limits for anonymous/free; private repos limited on free plan |
| GHCR | GitHub projects | Free for public, integrated with `GITHUB_TOKEN` in Actions |
| AWS ECR | AWS workloads | IAM auth, scan on push, lifecycle policy, cross-region replication |
| Harbor | Self-hosted enterprise | Scanning, RBAC, replication, signing; you operate it |
| `registry:2` | Quick private registry | Minimal: no UI, no RBAC unless put behind a proxy |

---

## 🟡 Real World Example
A SaaS startup keeps its Node.js and FastAPI images in AWS ECR. GitHub Actions authenticates with OIDC to an IAM role that can only push to those two repos. Each commit is pushed as `:sha-abc1234`. ECR scan-on-push flags a critical OpenSSL CVE in the base image; the build is blocked. A lifecycle rule keeps only the last 30 images, saving storage cost. EC2 instances pull with an instance role, no passwords stored on servers. When Docker Hub rate limits hit another team, theirs was unaffected because the base images are mirrored in ECR.

## 🟡 Real Example Hindi mein
एक SaaS startup अपनी Node.js और FastAPI images AWS ECR में रखती है। GitHub Actions OIDC से एक IAM role के साथ authenticate करता है जो सिर्फ इन दो repos में push कर सकता है। हर commit `:sha-abc1234` से push होता है। ECR scan-on-push base image में critical OpenSSL CVE पकड़ता है और build रुक जाता है। Lifecycle rule सिर्फ आखिरी 30 images रखती है, storage cost बचती है। EC2 instances instance role से pull करते हैं, servers पर password नहीं रखे जाते। जब Docker Hub rate limit ने दूसरी team को रोका, तब इनका काम चलता रहा क्योंकि base images ECR में mirror थीं।

---

## 💻 Code / Config Example — Basic

```bash
# --- GHCR (GitHub Container Registry) ---
echo "$GITHUB_TOKEN" | docker login ghcr.io -u USERNAME --password-stdin   # login; token via stdin keeps it out of history
docker build -t ghcr.io/myorg/node-api:1.4.2 .                              # build and tag with registry path
docker push ghcr.io/myorg/node-api:1.4.2                                    # upload to the registry
docker pull ghcr.io/myorg/node-api:1.4.2                                    # download on the server

# --- AWS ECR ---
aws ecr create-repository --repository-name myorg/node-api \
  --image-scanning-configuration scanOnPush=true \
  --image-tag-mutability IMMUTABLE                                          # private repo, scan on push, tags cannot be overwritten
aws ecr get-login-password --region ap-south-1 | \
  docker login --username AWS --password-stdin 123456789012.dkr.ecr.ap-south-1.amazonaws.com   # 12h token login (example account id)
docker tag node-api:1.4.2 123456789012.dkr.ecr.ap-south-1.amazonaws.com/myorg/node-api:1.4.2   # add registry-qualified tag
docker push 123456789012.dkr.ecr.ap-south-1.amazonaws.com/myorg/node-api:1.4.2                  # push
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/push-ecr.yml - build, scan and push to ECR using OIDC (no stored AWS keys)
name: build-and-push                          # workflow name
on:
  push:
    branches: [main]                          # run on every merge to main
permissions:
  id-token: write                             # allow OIDC token request
  contents: read                              # read the repo
jobs:
  push:
    runs-on: ubuntu-latest                    # GitHub-hosted runner
    steps:
      - uses: actions/checkout@v4             # get code (example version)
      - uses: aws-actions/configure-aws-credentials@v4   # assume role through OIDC (example version)
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-ecr-push   # role limited to ECR push
          aws-region: ap-south-1              # region
      - id: login
        uses: aws-actions/amazon-ecr-login@v2 # docker login to ECR
      - name: Build and push
        env:
          REGISTRY: ${{ steps.login.outputs.registry }}   # 123456789012.dkr.ecr.ap-south-1.amazonaws.com
          IMAGE: myorg/node-api                # repo name
          TAG: sha-${{ github.sha }}           # immutable tag from commit
        run: |
          docker build -t "$REGISTRY/$IMAGE:$TAG" .      # build image
          docker push "$REGISTRY/$IMAGE:$TAG"            # push image
          echo "digest: $(docker inspect --format='{{index .RepoDigests 0}}' "$REGISTRY/$IMAGE:$TAG")"   # print pinned digest for deploys
```

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Expire untagged images after 7 days",
      "selection": { "tagStatus": "untagged", "countType": "sinceImagePushed", "countUnit": "days", "countNumber": 7 },
      "action": { "type": "expire" }
    },
    {
      "rulePriority": 2,
      "description": "Keep only the last 30 sha- images",
      "selection": { "tagStatus": "tagged", "tagPrefixList": ["sha-"], "countType": "imageCountMoreThan", "countNumber": 30 },
      "action": { "type": "expire" }
    }
  ]
}
```

```bash
# Apply the lifecycle policy above (saved as lifecycle.json)
aws ecr put-lifecycle-policy --repository-name myorg/node-api \
  --lifecycle-policy-text file://lifecycle.json      # ECR deletes old images automatically
```

Checked: workflow YAML parses and has jobs/steps/uses; lifecycle JSON valid. Action versions are examples, update them. Not executed against AWS. / Workflow YAML parse हुआ और JSON valid है; AWS पर run नहीं किया।

---

## 🟠 My Stack Integration
- **VPS**: store images in GHCR (free with GitHub) or ECR; on the VPS use a **read-only pull token** and run `docker login` once; deploy script does `docker compose pull && docker compose up -d`.
- **AWS (EC2/ECS)**: ECR + IAM roles; no passwords. ECS tasks pull using the task execution role.
- **Node.js and FastAPI** get one repo each; **React** can be built into an Nginx image `myorg/web` or uploaded to S3 and not need a registry at all.
- **Nginx** custom image with your config baked in goes to the same registry.
- Mirror base images (`node:20-alpine`, `python:3.12-slim`) into your registry to avoid Docker Hub limits.

```yaml
# docker-compose.prod.yml on the VPS - always pull from the private registry
services:
  api:
    image: ghcr.io/myorg/node-api:${TAG}      # TAG supplied by deploy script (e.g. sha-abc1234)
    pull_policy: always                       # always check the registry for this tag
    restart: unless-stopped                   # restart on failure
  fastapi:
    image: ghcr.io/myorg/fastapi:${TAG}       # same tag scheme
    pull_policy: always
    restart: unless-stopped
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deploying `:latest`. You cannot know what version runs, and rollbacks are guesswork.
✅ Correct: Immutable tags (git SHA / semver) and deploy by digest for critical services.

❌ Mistake 2: A public repository holding company images, or secrets (`.env`, keys) baked into layers.
✅ Correct: Private repos; `.dockerignore`; use BuildKit secrets; scan images.

❌ Mistake 3: A personal access token with full rights stored on the server.
✅ Correct: Least-privilege read-only token (`read:packages`) or IAM instance role.

❌ Mistake 4: No retention policy, so the registry grows forever.
✅ Correct: Lifecycle rules, keep last N plus the ones in production.

❌ Mistake 5: One registry in one region; an outage blocks deploys and autoscaling.
✅ Correct: Replication (ECR cross-region) or a pull-through cache; keep recent images on nodes.

---

## 🧠 Tricky Interview Question
**Q:** You pushed `myapp:1.4.2` yesterday. Today a teammate fixes a bug and pushes `myapp:1.4.2` again. Some servers run the old image and others the new one, with the same tag. How did this happen and how do you prevent it?

**Answer:** Tags are mutable pointers. Servers that pulled yesterday keep the old image locally and do not re-pull unless forced (`pull_policy: always` or `docker pull`); new servers pull the new content. Prevention: make tags immutable (ECR `IMMUTABLE`), use a unique tag per build (git SHA), and deploy by digest (`image@sha256:...`) which can never change. Pair with a promotion process.

---

## ⚫ Interview Questions + Answers

Q1: Tag vs digest?
A1: A tag is a human-friendly, movable label. A digest is a SHA-256 hash of the manifest: content-addressed and immutable.

Q2: How does the CI authenticate to ECR securely?
A2: GitHub OIDC to an IAM role with a trust policy for your repo/branch. Short-lived credentials, nothing stored in secrets.

Q3: What is a pull-through cache?
A3: A registry proxy that fetches from an upstream (Docker Hub) once and serves later pulls locally; avoids rate limits. ECR supports pull-through cache rules.

Q4: How do you secure the supply chain?
A4: Scan images (Trivy/ECR scanning), sign them (cosign), generate SBOMs, restrict who can push, pin base images by digest, and verify signatures at deploy.

Q5: Self-hosted vs managed registry?
A5: Managed (ECR/GHCR) = no ops, HA built-in, pay per GB. Self-hosted (Harbor) = more control and on-prem, but you handle storage, TLS, backup, upgrades.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Anything beyond one developer laptop: staging/production servers
- CI/CD pipelines that build once and deploy many times
- Need scanning, access control and audit

❌ Avoid when:
- Self-hosting a registry on the same single VPS it serves (single point of failure) unless you accept it
- Using public repos for private code
- Pulling `latest` from Docker Hub in production

---

## 📊 Visual Diagram
```
 Developer --push--> GitHub --trigger--> CI (Actions)
                                          |  OIDC role
                                          v
                              +------------------------+
                              |  Private Registry      |
                              |  (ECR / GHCR / Harbor) |
                              |  - scan on push        |
                              |  - immutable tags      |
                              |  - lifecycle rules     |
                              +-----+--------------+---+
                                    | pull         | pull
                                    v              v
                               VPS (Compose)   ECS / K8s nodes
                               read-only token  IAM role
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Registry | Image storage server | Image रखने वाला server |
| Repository | Collection of image versions | एक image के versions |
| Tag | Label for a version | Version का label |
| Digest | Immutable content hash | अपरिवर्तनीय hash |
| OIDC | Passwordless short-lived auth | बिना password short-lived auth |
| Lifecycle policy | Auto-delete old images | पुरानी images अपने-आप हटाना |

---

## ⚡ 3-Line Summary
English: A private registry is the single source of truth for your images.
Use immutable tags or digests, short-lived credentials, scanning and cleanup rules.
Mirror base images and avoid `latest` in production.

Hindi: Private registry आपकी images का एकमात्र source of truth है।
Immutable tags या digests, short-lived credentials, scanning और cleanup rules use करो।
Base images mirror करो और production में `latest` से बचो।

---

## ➡️ Next Topic
**227. Image Promotion Strategy** - once images are in the registry, how do you move the same image from dev to staging to production without rebuilding?
