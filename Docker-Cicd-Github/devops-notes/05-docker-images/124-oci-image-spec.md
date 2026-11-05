# 124. OCI Image Spec
# हिंदी में: OCI Image Spec (container image का खुला standard)

---

## 🔵 Simple Definition (English)
The OCI (Open Container Initiative) Image Specification is the open standard that defines how a container image is structured: a manifest, a config JSON and a list of compressed layers, all addressed by sha256 digests. Any compliant tool can build, push or run it.

## 🔵 सरल परिभाषा (Hindi)
OCI (Open Container Initiative) Image Specification वह खुला standard है जो बताता है कि container image की बनावट कैसी हो: एक manifest, एक config JSON और compressed layers की सूची, सब sha256 digest से पहचाने जाते हैं। कोई भी compliant tool इसे build, push या run कर सकता है।

---

## 🔴 Problem it Solves
- Early on, Docker's image format was the only one; rivals (rkt, CoreOS) had their own. Tools could not share images.
- Registries, runtimes (containerd, CRI-O, Podman) and builders (BuildKit, Buildah, Kaniko) need a common language.
- Vendor lock-in: an image built with Docker should run on Kubernetes with containerd and be stored in ECR, GHCR or Harbor.

## 🔴 यह क्यों बना? (Hindi)
- शुरुआत में सिर्फ Docker का image format था; प्रतिद्वंद्वियों (rkt, CoreOS) के अपने formats थे। Tools images साझा नहीं कर सकते थे।
- Registries, runtimes (containerd, CRI-O, Podman) और builders (BuildKit, Buildah, Kaniko) को एक साझा भाषा चाहिए।
- Vendor lock-in: Docker से बनी image Kubernetes पर containerd में चले और ECR, GHCR या Harbor में रखी जा सके।

---

## 🟢 How it Works — Step by Step

```
Step 1 → An image = INDEX (optional) -> MANIFEST -> CONFIG + LAYERS
Step 2 → Image Index (manifest list): one tag, many platforms (linux/amd64, linux/arm64)
Step 3 → Manifest: JSON listing the config blob digest and each layer blob digest + size + mediaType
Step 4 → Config: JSON with env, cmd, entrypoint, exposed ports, user, and rootfs diff_ids + build history
Step 5 → Layers: tar (gzip or zstd) archives of filesystem changes, stacked in order
Step 6 → Everything is content-addressed: digest = sha256 of the bytes; any change changes the digest
Step 7 → Registry API (OCI Distribution Spec): push/pull blobs and manifests over HTTPS
Step 8 → Runtime (runc via containerd) unpacks layers into a rootfs and starts the process (OCI Runtime Spec)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Image = INDEX (वैकल्पिक) -> MANIFEST -> CONFIG + LAYERS
Step 2 → Image Index (manifest list): एक tag, कई platforms (linux/amd64, linux/arm64)
Step 3 → Manifest: config blob और हर layer blob का digest + size + mediaType वाला JSON
Step 4 → Config: env, cmd, entrypoint, ports, user, और rootfs diff_ids + build history वाला JSON
Step 5 → Layers: filesystem बदलावों के tar (gzip या zstd) archives, क्रम में ऊपर-नीचे
Step 6 → सब कुछ content-addressed है: digest = bytes का sha256; ज़रा सा बदलाव digest बदल देता है
Step 7 → Registry API (OCI Distribution Spec): HTTPS पर blobs और manifests push/pull
Step 8 → Runtime (containerd के ज़रिए runc) layers को rootfs में खोलकर process शुरू करता है (OCI Runtime Spec)
```

---

## 🟡 Real World Example
A team builds on Apple M-series laptops (arm64) and deploys to AWS x86 servers. They build a multi-platform image: one tag `api:1.0.0` is an OCI image index with two manifests. The Graviton server pulls the arm64 manifest, the x86 server pulls amd64, using the same tag and same Compose file. The same image also runs unchanged on Kubernetes with containerd.

## 🟡 Real Example Hindi mein
एक team Apple M-series laptops (arm64) पर build करती है और AWS x86 servers पर deploy करती है। वे multi-platform image बनाते हैं: एक tag `api:1.0.0` असल में दो manifests वाला OCI image index है। Graviton server arm64 manifest खींचता है, x86 server amd64, वही tag और वही Compose file। वही image Kubernetes पर containerd में भी बिना बदलाव चलती है।

---

## 💻 Code / Config Example — Basic
```bash
# Look at the raw manifest/index of a public image (shows platforms)
docker buildx imagetools inspect node:20-alpine        # prints index with each platform manifest and digest

# Raw JSON of the manifest of an image you pulled
docker manifest inspect node:20-alpine                 # may need experimental CLI on very old Docker versions

# Save an image as a tarball and look inside it
docker save myorg/api:1.0.0 -o api.tar                 # export image to a tar
mkdir -p api-oci && tar -xf api.tar -C api-oci         # extract it
ls api-oci                                             # manifest.json, blobs/sha256/..., index.json (newer Docker)

# Show the image config (env, cmd, user, layers) without extracting
docker image inspect myorg/api:1.0.0 --format '{{json .Config}}' | jq .   # Config section as JSON

# Layer digests of the image
docker image inspect myorg/api:1.0.0 --format '{{json .RootFS.Layers}}' | jq .   # list of layer sha256 ids

# Add standard OCI labels in a Dockerfile (annotations that tools understand)
# LABEL org.opencontainers.image.source="https://github.com/myorg/api"
```

## 💻 Code / Config Example — Advanced
```dockerfile
# Dockerfile - Node.js API with standard OCI annotations (example, adjust names)
FROM node:20-alpine AS base
# Build args supplied by CI so labels are filled automatically
ARG GIT_SHA=unknown
ARG BUILD_DATE=unknown
ARG VERSION=0.0.0
# OCI pre-defined annotation keys (org.opencontainers.image.*) read by Scout, Trivy, registries
LABEL org.opencontainers.image.title="api" \
      org.opencontainers.image.description="Orders API (Node.js)" \
      org.opencontainers.image.source="https://github.com/myorg/api" \
      org.opencontainers.image.revision="${GIT_SHA}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.licenses="MIT"
# Work directory inside the image
WORKDIR /app
# Copy manifest files first so dependency layer is cached
COPY package*.json ./
# Reproducible, production-only install
RUN npm ci --omit=dev
# Copy application code
COPY . .
# Do not run as root (security)
USER node
# Start the server
CMD ["node", "server.js"]
```

```yaml
# .github/workflows/multiarch.yml - build one OCI index for amd64 + arm64 (example versions)
name: multiarch                                # workflow name
on:
  push:
    tags: ['v*']                               # run on version tags
permissions:
  contents: read                               # read code
  packages: write                              # push to GHCR
jobs:
  build:
    runs-on: ubuntu-latest                     # hosted runner
    steps:
      - uses: actions/checkout@v4              # get source
      - uses: docker/setup-qemu-action@v3      # emulate other CPU types
      - uses: docker/setup-buildx-action@v3    # buildx builder
      - uses: docker/login-action@v3           # login to GHCR
        with:
          registry: ghcr.io                    # registry host
          username: ${{ github.actor }}        # actor name
          password: ${{ secrets.GITHUB_TOKEN }}# built in token
      - uses: docker/build-push-action@v6      # build and push
        with:
          context: .                           # Dockerfile folder
          platforms: linux/amd64,linux/arm64   # makes an OCI image index with two manifests
          push: true                           # push result
          tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}   # one tag, many platforms
          build-args: |                        # fill the label values
            GIT_SHA=${{ github.sha }}
            VERSION=${{ github.ref_name }}
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI / React:** add `org.opencontainers.image.source` so GHCR links the package to the repo automatically and shows it on the repo page.
- **AWS:** ECR stores OCI images and indexes; ECS/EKS on Graviton (arm64) is cheaper, so build multi-arch.
- **VPS:** old Docker versions (before ~20.10) handle OCI indexes poorly; keep Docker updated.
- **Security:** because everything is addressed by digest, pin deploys with `image: myorg/api@sha256:...` for immutability.

```yaml
# docker-compose.yml - pin by digest (value comes from the CI build output)
services:
  api:                                         # Node.js / FastAPI service
    image: ghcr.io/myorg/api@sha256:REPLACE_WITH_REAL_DIGEST   # immutable: exact manifest, never changes
    restart: unless-stopped                    # restart policy
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Building on an M1/M2 Mac and deploying to x86 EC2 with a single-platform image ("exec format error").
✅ Correct: Build with `--platform linux/amd64` or multi-platform via buildx.

❌ Mistake 2: Assuming an image tag and digest are the same thing.
✅ Correct: A tag is a movable name; a digest is the immutable content hash of the manifest.

❌ Mistake 3: Confusing the Docker image digest (RepoDigest, manifest hash) with the image ID (config hash).
✅ Correct: `docker images --digests` shows the manifest digest; the ID is the hash of the config JSON.

❌ Mistake 4: Thinking OCI replaced Docker.
✅ Correct: Docker builds and runs OCI-compatible images; OCI is the standard, Docker is one implementation.

---

## 🧠 Tricky Interview Question
Two image tags have different names but the same digest. Does the registry store the data twice?

Answer: No. Blobs and manifests are content-addressed: identical bytes have an identical digest and are stored once. Tags are just pointers. This also means two layers with the same content are shared between images, which is why pushing a rebuilt image often says "Layer already exists" and uploads only the changed layers.

---

## ⚫ Interview Questions + Answers

Q1: What are the OCI specs?
A1: Three: Image Spec (format), Runtime Spec (how to run a container, implemented by runc) and Distribution Spec (registry API).

Q2: What does an image manifest contain?
A2: The mediaType, the config descriptor and an ordered list of layer descriptors, each with digest and size.

Q3: What is an image index?
A3: A manifest list that maps platforms (os/arch) to platform-specific manifests, enabling one tag for multiple architectures.

Q4: Is a Docker image the same as an OCI image?
A4: Docker's v2 schema 2 format is very close; modern Docker builds OCI-compatible images and registries accept both.

Q5: Why use digests?
A5: Digests are immutable and verify content integrity; tags can be moved or overwritten.

---

## 🔷 When to Use + When Not to Use
✅ Use (know) when:
- Debugging "exec format error" or multi-arch issues.
- Pinning production deploys by digest.
- Choosing tools like Podman, Buildah, Kaniko that are not Docker.

❌ Avoid when:
- Hand-editing blobs or manifests; use tools like `crane`, `skopeo`, `docker buildx imagetools`.

---

## 📊 Visual Diagram
```
 tag  api:1.0.0
   |
   v
 +---------------------------+
 | Image Index               |  mediaType: application/vnd.oci.image.index.v1+json
 |  linux/amd64 -> sha256:A  |
 |  linux/arm64 -> sha256:B  |
 +---------------------------+
          | (pick platform)
          v
 +---------------------------+
 | Manifest (sha256:A)       |
 |  config -> sha256:C       |-----> Config JSON (env, cmd, user, history)
 |  layers -> sha256:L1      |-----> tar.gz  base OS
 |            sha256:L2      |-----> tar.gz  node_modules
 |            sha256:L3      |-----> tar.gz  app code
 +---------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OCI | Open Container Initiative (standards body) | container standards की संस्था |
| Manifest | JSON listing config and layers | config और layers की सूची |
| Image index | One tag for many platforms | कई platforms के लिए एक tag |
| Digest | sha256 hash of content | content का sha256 hash |
| Layer | Tar of filesystem changes | filesystem बदलावों का tar |
| Content-addressed | Named by hash of content | content के hash से नाम |

---

## ⚡ 3-Line Summary
English: OCI defines the standard format of images, runtimes and registry APIs.
English: An image is index, manifest, config and layers, all identified by sha256 digests.
English: Use digests for immutable deploys and multi-platform indexes for amd64/arm64.
Hindi: OCI images, runtimes और registry APIs का standard format तय करता है।
Hindi: Image = index, manifest, config और layers, सब sha256 digest से पहचाने जाते हैं।
Hindi: Immutable deploy के लिए digest और amd64/arm64 के लिए multi-platform index इस्तेमाल करें।

---

## ➡️ Next Topic
**125. Pushing to Docker Hub** — now that you know how an image is structured, publish one to the most common public registry.
