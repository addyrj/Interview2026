# 378. Push Image to ECR
# हिंदी में: ECR में Image Push करना

---

## 🔵 Simple Definition (English)
Pushing to ECR means tagging a locally built image with the full registry path (`ACCOUNT.dkr.ecr.REGION.amazonaws.com/repo:tag`) and uploading it with `docker push`. Docker uploads only layers ECR does not already have.

## 🔵 सरल परिभाषा (Hindi)
ECR में push करने का मतलब है local build की गई image को पूरे registry path (`ACCOUNT.dkr.ecr.REGION.amazonaws.com/repo:tag`) से tag करना और `docker push` से upload करना। Docker सिर्फ वही layers upload करता है जो ECR में पहले से नहीं हैं।

---

## 🔴 Problem it Solves
- Built images exist only on the CI runner or your laptop; the runner disappears after the job.
- Servers need a shared, versioned place to pull the exact image that was tested.
- Without a tagging strategy you cannot tell which code is running or roll back.

## 🔴 यह क्यों बना? (Hindi)
- Build की हुई image सिर्फ CI runner या laptop पर होती है; job के बाद runner गायब हो जाता है।
- Servers को एक shared, versioned जगह चाहिए जहाँ से test हुई वही image pull हो।
- Tagging strategy के बिना पता नहीं चलता कौन-सा code चल रहा है, और rollback मुश्किल होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Login to ECR (topic 377)
Step 2 → docker build -t app:local .
Step 3 → docker tag app:local REGISTRY/REPO:GIT_SHA   (and optionally :v1.4.0)
Step 4 → docker push REGISTRY/REPO:GIT_SHA
Step 5 → Docker checks each layer; skips existing ("Layer already exists")
Step 6 → ECR stores manifest; scan-on-push starts; digest printed (sha256:...)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ECR में login (topic 377)
Step 2 → docker build -t app:local .
Step 3 → docker tag app:local REGISTRY/REPO:GIT_SHA   (और चाहें तो :v1.4.0)
Step 4 → docker push REGISTRY/REPO:GIT_SHA
Step 5 → Docker हर layer जाँचता है; जो मौजूद है उसे skip ("Layer already exists")
Step 6 → ECR manifest रखता है; scan-on-push शुरू; digest (sha256:...) print होता है
```

---

## 🟡 Real World Example
A Razorpay-style payments API deploys 15 times a day. Each push uses the first 12 chars of the commit SHA. Because base layers (Node 20 slim + node_modules) rarely change, only the final app layer (~8 MB) is uploaded, so push takes seconds. When a bug appears, the on-call engineer looks at the running task's image tag, finds the commit, and rolls back by deploying the previous SHA tag.

## 🟡 Real Example Hindi mein
Razorpay जैसी payments API दिन में 15 बार deploy होती है। हर push commit SHA के पहले 12 characters से होता है। Base layers (Node 20 slim + node_modules) कम बदलती हैं, इसलिए सिर्फ आखिरी app layer (~8 MB) upload होती है और push सेकंडों में हो जाता है। Bug आने पर on-call engineer चल रहे task का image tag देखता है, commit ढूँढता है, और पिछला SHA tag deploy करके rollback करता है।

---

## 💻 Code / Config Example — Basic

```bash
# push-basic.sh  - manual push after login
set -euo pipefail                                          # stop on error
REGION=ap-south-1                                          # registry region
ACCOUNT=123456789012                                       # example account id
REPO=myapp-api                                             # ECR repository name
SHA=$(git rev-parse --short=12 HEAD)                       # 12 char commit id as tag
IMAGE="$ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$REPO"       # full repo URL without tag

docker build -t "$IMAGE:$SHA" .                            # build and tag in one step
docker push "$IMAGE:$SHA"                                  # upload
aws ecr describe-images --repository-name "$REPO" --image-ids imageTag="$SHA" \
  --query 'imageDetails[0].imageDigest' --output text      # print digest to confirm it landed
```

## 💻 Code / Config Example — Advanced
GitHub Actions with Buildx, layer cache in GitHub cache, SHA + semver tags, and digest output. Assumes the repo is IMMUTABLE (so do not push the same tag twice).

```yaml
# .github/workflows/push-ecr.yml
name: build-and-push-ecr                   # workflow name
on:
  push:
    branches: [main]                       # build each merge to main
    tags: ["v*.*.*"]                       # also on release tags like v1.4.0
permissions:
  id-token: write                          # OIDC to AWS
  contents: read                           # checkout
jobs:
  push:
    runs-on: ubuntu-latest                 # runner
    outputs:
      digest: ${{ steps.build.outputs.digest }}   # image digest for later jobs
    steps:
      - uses: actions/checkout@v4          # get source (example version)
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-ecr-push   # push-only role
          aws-region: ap-south-1           # registry region
      - id: ecr
        uses: aws-actions/amazon-ecr-login@v2   # docker login to ECR
      - uses: docker/setup-buildx-action@v3     # enables cache export and multi-platform
      - id: meta                           # compute tags automatically
        uses: docker/metadata-action@v5
        with:
          images: ${{ steps.ecr.outputs.registry }}/myapp-api   # full repo without tag
          tags: |
            type=sha,format=short,prefix=  # tag like 4f2a9c1
            type=semver,pattern={{version}} # tag like 1.4.0 when a v1.4.0 tag is pushed
      - id: build
        uses: docker/build-push-action@v6   # build and push in one step
        with:
          context: .                        # Dockerfile folder
          push: true                        # upload after build
          tags: ${{ steps.meta.outputs.tags }}      # tags computed above
          labels: ${{ steps.meta.outputs.labels }}  # OCI labels (commit, source)
          cache-from: type=gha              # reuse layers from previous runs
          cache-to: type=gha,mode=max       # save all layers for next run
          provenance: false                 # simpler manifest; some ECS/ECR tooling prefers it
      - run: echo "pushed ${{ steps.build.outputs.digest }}"   # show digest in logs
```

---

## 🟠 My Stack Integration
Multi-stage Dockerfile for the Node API keeps the pushed image small (fast pull on Fargate). FastAPI is the same idea with Python slim.

```dockerfile
# Dockerfile (Node.js API)
FROM node:20-alpine AS build            # build stage with full tooling
WORKDIR /app                            # working folder
COPY package*.json ./                   # copy dependency files first for caching
RUN npm ci                              # install exact versions
COPY . .                                # copy source
RUN npm run build                       # compile (TypeScript etc.)

FROM node:20-alpine AS runtime          # small final stage
WORKDIR /app                            # working folder
ENV NODE_ENV=production                 # production mode
COPY package*.json ./                   # dependency files
RUN npm ci --omit=dev                   # only runtime deps
COPY --from=build /app/dist ./dist      # compiled output from build stage
USER node                               # do not run as root
EXPOSE 3000                             # documentation of the port
CMD ["node", "dist/main.js"]            # start command
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Pushing only `latest`.
✅ Correct: Always push an immutable SHA tag; optional `latest` is only a convenience.

❌ Mistake 2: Putting `.env` or `.git` in the image via `COPY . .`.
✅ Correct: Use `.dockerignore` (`.env`, `.git`, `node_modules`); secrets in images are readable by anyone with pull access.

❌ Mistake 3: Wrong repo URL region.
✅ Correct: Registry region must match login region; check with `echo $IMAGE`.

❌ Mistake 4: Ignoring scan results.
✅ Correct: Fail the pipeline or alert on CRITICAL findings.

---

## 🧠 Tricky Interview Question
With tag immutability ON, your pipeline re-runs after a flaky test and fails at push with "tag invalid: the tag already exists". How do you handle this safely?

Answer: The first run already pushed that SHA, so the second push is rejected. Do not disable immutability. Either check first (`aws ecr describe-images` for the tag) and skip build/push if it exists, or make the re-run reuse the existing image. Same commit = same image is exactly what immutability enforces.

---

## ⚫ Interview Questions + Answers

Q1: Tag vs digest?
A1: A tag is a movable label (unless immutable). A digest (`@sha256:...`) is the content hash and can never change. Pin digests in prod for exact reproducibility.

Q2: Why was my second push very fast?
A2: Layer deduplication. Unchanged layers already exist in ECR and are skipped.

Q3: Why use multi-stage builds before pushing?
A3: Smaller image, fewer packages (smaller attack surface), faster pull and cheaper storage.

Q4: How to push multi-arch (arm64 for Graviton)?
A4: `docker buildx build --platform linux/amd64,linux/arm64 --push`. ECR stores a manifest list; the correct arch is pulled automatically.

Q5: Where does the max image size limit come from?
A5: Layers have a size limit per layer; check current ECR quotas in AWS docs (values change). Keep images small anyway.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every successful build on main
- Release tags for versioned deploys

❌ Avoid when:
- Pull requests from forks (no secrets/OIDC for them; build without push)
- Pushing from developer laptops to prod repos

---

## 📊 Visual Diagram
```
 git push -> Actions runner
   build (cache: gha) -> image layers
        |  tag: REGISTRY/myapp-api:4f2a9c1
        v
   docker push --> ECR: skip existing layers, upload new ones
        v
   manifest + digest sha256:ab12...  -> scan on push -> ready for ECS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tag | Version label | Version का नाम |
| Digest | Content hash | Content का hash |
| Layer | One build step's file changes | Build step के files का हिस्सा |
| Buildx | Docker's advanced builder | Docker का advanced builder |
| Manifest list | One tag, many architectures | एक tag, कई architectures |
| .dockerignore | Files excluded from build | Build से बाहर रखी फाइलें |

---

## ⚡ 3-Line Summary
English: Tag the image with the full ECR URL and a git SHA, then docker push.
Only new layers upload; use buildx cache and multi-stage builds for speed.
Keep tags immutable and scan every push.

Hindi: Image को पूरे ECR URL और git SHA से tag करो, फिर docker push।
सिर्फ नई layers upload होती हैं; speed के लिए buildx cache और multi-stage build लो।
Tags immutable रखो और हर push scan करो।

---

## ➡️ Next Topic
379. Pull Image from ECR: how ECS, a VPS and local machines fetch what you just pushed.
