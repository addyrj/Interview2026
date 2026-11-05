# 48. Docker Registry
# हिंदी में: Docker Registry (रजिस्ट्री)

---

## 🔵 Simple Definition (English)
A **Docker registry** is a server that stores and distributes container images. It is organized into **repositories** (one per app), each holding many **tags** (versions). You `push` images to it from CI and `pull` them on servers. Examples: Docker Hub, GitHub Container Registry (GHCR), AWS ECR, or your own self-hosted `registry:2`.

## 🔵 सरल परिभाषा (Hindi)
**Docker registry** एक server है जो container images को store और distribute करता है। यह **repositories** (हर app की एक) में बँटा होता है, और हर repo में कई **tags** (versions) होते हैं। CI से `push` करते हैं और servers पर `pull`। उदाहरण: Docker Hub, GitHub Container Registry (GHCR), AWS ECR, या अपना `registry:2`।

---

## 🔴 Problem it Solves
Images built on one machine must reach many others. Copying tar files by hand (`docker save | scp`) does not scale, has no versioning or access control, and re-sends layers that already exist. A registry stores each layer once (content-addressed by sha256 digest), transfers only missing layers, controls who may push/pull, and gives immutable references for deployments.

## 🔴 यह क्यों बना? (Hindi)
एक machine पर बनी images को कई machines तक पहुँचना होता है। हाथ से tar files कॉपी (`docker save | scp`) करना scale नहीं करता, version या access control नहीं है, और मौजूद layers दोबारा भेजता है। Registry हर layer एक बार रखती है (sha256 digest से पहचान), सिर्फ़ missing layers भेजती है, push/pull की अनुमति नियंत्रित करती है, और deployment के लिए अटल (immutable) reference देती है।

---

## 🟢 How it Works — Step by Step

```
Image name:  registry-host / namespace / repo : tag   e.g. ghcr.io/myorg/api:1.4.0

PUSH
Step 1 → docker login registry  (token saved by client)
Step 2 → docker tag local-image registry/ns/repo:tag
Step 3 → docker push: client/daemon asks "do you have layer sha256:abc?" for each layer
Step 4 → Uploads only missing layers (blobs), then uploads the manifest (list of layers + config)
Step 5 → Registry returns the manifest digest (sha256:...) = immutable identity

PULL
Step 6 → Daemon GETs the manifest for tag/digest, then downloads missing blobs in parallel
Step 7 → Verifies sha256 of each blob, assembles the image locally
```

## 🟢 कैसे काम करता है? (Hindi)
```
Image का नाम:  registry-host / namespace / repo : tag   जैसे ghcr.io/myorg/api:1.4.0

PUSH
Step 1 → docker login registry  (token client में सेव होता है)
Step 2 → docker tag local-image registry/ns/repo:tag
Step 3 → docker push: हर layer के लिए पूछता है "क्या sha256:abc आपके पास है?"
Step 4 → सिर्फ़ missing layers (blobs) अपलोड, फिर manifest (layers + config की सूची)
Step 5 → Registry manifest digest (sha256:...) लौटाती है = अटल पहचान

PULL
Step 6 → Daemon tag/digest का manifest GET करता है, missing blobs parallel डाउनलोड करता है
Step 7 → हर blob का sha256 verify करके image local में जोड़ता है
```

---

## 🟡 Real World Example
A Zomato-like team uses **AWS ECR** for private images because their ECS services already authenticate via IAM roles, so no passwords are stored on servers. Open-source projects publish on **Docker Hub** so anyone can `docker pull`. **Your setup:** GitHub Actions builds the Node.js and FastAPI images, pushes to **GHCR** with `GITHUB_TOKEN`, and the VPS pulls with a read-only token.

## 🟡 Real Example Hindi mein
Zomato जैसी team private images के लिए **AWS ECR** इस्तेमाल करती है क्योंकि उनकी ECS services IAM roles से authenticate होती हैं, servers पर password रखने की ज़रूरत नहीं। Open-source projects **Docker Hub** पर publish करते हैं ताकि कोई भी `docker pull` कर सके। **आपका setup:** GitHub Actions Node.js और FastAPI images बनाकर `GITHUB_TOKEN` से **GHCR** में push करता है, और VPS read-only token से pull करता है।

---

## 💻 Code / Config Example — Basic
```bash
# Run your own private registry (testing/lab; use TLS + auth for anything real). Needs a Docker daemon.
docker run -d --name registry -p 127.0.0.1:5000:5000 registry:2   # official registry image, localhost only
docker pull alpine:3.20                                  # get any small image (example tag)
docker tag alpine:3.20 localhost:5000/demo/alpine:1.0    # re-tag with registry host + repo + tag
docker push localhost:5000/demo/alpine:1.0               # upload to the local registry
curl -s http://localhost:5000/v2/_catalog                # API: list repositories -> {"repositories":["demo/alpine"]}
curl -s http://localhost:5000/v2/demo/alpine/tags/list   # API: list tags of the repo
docker rmi localhost:5000/demo/alpine:1.0                # remove local copy
docker pull localhost:5000/demo/alpine:1.0               # pull it back from the registry
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/publish-image.yml - push to GHCR (+ optional ECR) with immutable tags
name: publish-image                                   # workflow name
on:
  push:
    tags: ["v*.*.*"]                                  # run on version tags such as v1.4.0
permissions:
  contents: read                                      # checkout only
  packages: write                                     # push to GHCR
  id-token: write                                     # needed for AWS OIDC (no long-lived AWS keys)
jobs:
  push:
    runs-on: ubuntu-latest                            # GitHub-hosted runner
    steps:
      - uses: actions/checkout@v4                     # get code
      - uses: docker/setup-buildx-action@v3           # BuildKit builder with cache support
      - uses: docker/login-action@v3                  # login to GHCR
        with:
          registry: ghcr.io                           # registry host
          username: ${{ github.actor }}               # user who triggered the run
          password: ${{ secrets.GITHUB_TOKEN }}       # short-lived token, no secret to manage
      - id: meta                                      # compute tags and labels
        uses: docker/metadata-action@v5               # generates tags from the git ref
        with:
          images: ghcr.io/${{ github.repository }}/api   # target repository
          tags: |                                     # which tags to create
            type=semver,pattern={{version}}           # 1.4.0
            type=semver,pattern={{major}}.{{minor}}   # 1.4
            type=sha                                  # sha-<commit> immutable reference
      - uses: docker/build-push-action@v6             # build and push in one step
        with:
          context: ./api                              # build context directory
          push: true                                  # push after build
          tags: ${{ steps.meta.outputs.tags }}        # tags from metadata step
          labels: ${{ steps.meta.outputs.labels }}    # OCI labels (source repo, revision)
          cache-from: type=gha                        # reuse GitHub Actions cache
          cache-to: type=gha,mode=max                 # save cache for next run
          provenance: true                            # attach build provenance attestation
```

---

## 🟠 My Stack Integration
- **GHCR** fits GitHub-centric stacks (free private packages within limits - verify current pricing).
- **ECR** if you move to AWS ECS/EKS: `aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <acct>.dkr.ecr.<region>.amazonaws.com`.
- **VPS:** log in once with a read-only PAT (`read:packages`), then `docker compose pull`.
- **Nginx / React:** push a tiny `nginx` image that bakes in the React build, or serve `dist` from a volume.

```yaml
# docker-compose.yml on the VPS - pull exact immutable versions from GHCR
services:
  api:
    image: ghcr.io/myorg/api:1.4.0           # pinned semver tag (or @sha256:<digest> for maximum safety)
    restart: unless-stopped                  # survive reboot
  fastapi:
    image: ghcr.io/myorg/fastapi:2.1.0       # pinned semver tag
    restart: unless-stopped                  # survive reboot
```
```bash
echo "$GHCR_READ_TOKEN" | docker login ghcr.io -u myuser --password-stdin   # VPS login with read-only token
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deploying `:latest` - nobody knows what runs and rollback is guesswork.
✅ Correct: Deploy semver or `sha-` tags, or pin by digest `image@sha256:...`.

❌ Mistake 2: Pushing images containing secrets, then making the repo public.
✅ Correct: Never bake secrets in; layers are readable by anyone with pull access. Scan with Trivy/Docker Scout.

❌ Mistake 3: Using a personal admin token on the VPS.
✅ Correct: Least privilege read-only token, or IAM role for ECR.

❌ Mistake 4: Running a self-hosted registry over plain HTTP on the internet.
✅ Correct: Put it behind Nginx with TLS and htpasswd/OIDC auth; add garbage collection.

---

## 🧠 Tricky Interview Question
"You pushed `myapp:1.0`, later pushed a different build to the same tag `myapp:1.0`. Server A (pulled before) and server B (pulled after) behave differently. What happened and how do you prevent it?"

Answer: Tags are mutable pointers; digests are immutable. A still has the old manifest digest and `docker compose up` does not re-pull an existing tag unless told to; B got the new one. Prevent with unique tags per build (commit SHA / semver), deploy by digest, enable tag immutability (ECR "immutable tags" setting, GHCR retention rules), and use `pull_policy: always` or explicit `docker compose pull`.

---

## ⚫ Interview Questions + Answers

Q1: Registry vs repository vs image?
A1: Registry is the server; repository is a collection of versions of one image name; image is one specific tag/digest in it.

Q2: What is a manifest and a digest?
A2: Manifest is JSON listing layer digests and config; digest is the sha256 of content, an immutable ID.

Q3: Public vs private registries?
A3: Public (Docker Hub) for open images; private (ECR, GHCR private, Harbor) for company code, with auth and scanning. Docker Hub applies pull-rate limits to anonymous/free users (check current limits).

Q4: How does ECR auth work?
A4: `aws ecr get-login-password` yields a token valid ~12 hours; on ECS/EC2, the IAM role authenticates automatically.

Q5: How can you speed up pulls and avoid rate limits?
A5: Registry mirror / pull-through cache (`registry-mirrors`, ECR pull-through cache), smaller images, shared layers, authenticated pulls.

---

## 🔷 When to Use + When Not to Use
✅ Use a private registry when:
- CI builds once, many servers pull; you need audit, scanning, and rollbacks

❌ Avoid when:
- A single local dev machine (just build locally)
- Self-hosting without capacity to maintain TLS, auth, storage cleanup - prefer a managed one

---

## 📊 Visual Diagram
```
   CI (GitHub Actions)                 REGISTRY                      Servers
  +-------------------+     push     +-------------------------+    pull   +-----------+
  | docker build      |------------->| ghcr.io/myorg/api       |<----------| VPS       |
  | docker push       |  layers +    |   tags: 1.4.0, 1.4,     |  layers   | compose   |
  +-------------------+  manifest    |         sha-9f2c1ab     |  only if  +-----------+
                                      |   digest: sha256:77e...|  missing  | EC2 / ECS |
                                      +-------------------------+           +-----------+
  name = host / namespace / repo : tag      (auth: tokens / IAM / OIDC)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Registry | Image storage server | images रखने वाला server |
| Repository | Versions of one image | एक image के versions का समूह |
| Tag | Human-friendly version label | version का नाम |
| Digest | sha256 content ID | content की अटल पहचान |
| Manifest | Layer list + config | layers की सूची |
| Pull-through cache | Mirror of upstream registry | upstream registry की प्रतिलिपि |
| Immutable tags | Tags that cannot be overwritten | जिन्हें बदला नहीं जा सकता |

---

## ⚡ 3-Line Summary
English: A registry stores images in repositories with tags; CI pushes, servers pull.
English: Tags can move, digests cannot; deploy semver/sha tags or digests, never `latest`.
English: Use least-privilege tokens or IAM, scan images, and never bake secrets into layers.
Hindi: Registry images को repositories में tags के साथ रखती है; CI push करता है, servers pull।
Hindi: Tags बदल सकते हैं, digests नहीं; semver/sha tags या digest deploy करो, `latest` नहीं।
Hindi: कम से कम अधिकार वाले tokens या IAM इस्तेमाल करो, images scan करो, secrets layers में मत डालो।

---

## ➡️ Next Topic
**49. Docker Hub** - the default public registry, with its rate limits, official images and trust model.
