# 101. Docker Image Layers
# हिंदी में: Docker Image Layers

---

## 🔵 Simple Definition (English)
A Docker image is a stack of read-only layers. Each filesystem-changing Dockerfile instruction (`RUN`, `COPY`, `ADD`) creates one layer that stores only the differences from the layer below. Layers are identified by a content hash, cached and shared between images.

## 🔵 सरल परिभाषा (Hindi)
Docker image read-only layers का stack होती है। Filesystem बदलने वाला हर Dockerfile instruction (`RUN`, `COPY`, `ADD`) एक layer बनाता है जिसमें सिर्फ नीचे वाली layer से अंतर (differences) होता है। Layers content hash से पहचानी जाती हैं, cache होती हैं और images के बीच share होती हैं।

---

## 🔴 Problem it Solves
Without layers each image would be a full copy of the OS and dependencies: 10 services on `node:20-alpine` would store the 50 MB base 10 times, and any one-line code change would force re-uploading everything. Layers allow sharing the base once on disk, pulling only the missing layers, and rebuilding only from the first changed instruction.

## 🔴 यह क्यों बना? (Hindi)
Layers के बिना हर image OS और dependencies की पूरी copy होती: `node:20-alpine` पर 10 services हों तो 50 MB base 10 बार store होता, और code की एक लाइन बदलने पर सब कुछ दोबारा upload करना पड़ता। Layers से base disk पर एक बार share होता है, सिर्फ missing layers pull होती हैं, और rebuild पहले बदले instruction से ही शुरू होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → FROM node:20-alpine        -> base layers (pulled, shared)
Step 2 → COPY package*.json ./      -> layer A (hash of those files)
Step 3 → RUN npm ci                 -> layer B (node_modules)
Step 4 → COPY . .                   -> layer C (your source)
Step 5 → Build cache: if instruction + inputs unchanged -> reuse layer
Step 6 → First changed instruction invalidates ALL layers after it
Step 7 → Container start adds one thin writable layer on top
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → FROM node:20-alpine        -> base layers (pull, shared)
Step 2 → COPY package*.json ./      -> layer A (उन files का hash)
Step 3 → RUN npm ci                 -> layer B (node_modules)
Step 4 → COPY . .                   -> layer C (आपका source)
Step 5 → Build cache: instruction + inputs वही हों -> layer reuse
Step 6 → पहला बदला instruction उसके बाद की सब layers invalid कर देता है
Step 7 → Container start पर ऊपर एक पतली writable layer जुड़ती है
```

---

## 🟡 Real World Example
A CI pipeline at an Indian fintech took 9 minutes per build because `COPY . .` came before `npm ci`; every commit reinstalled 900 packages. After reordering (manifests, install, then source) CI builds with only a code change took 40 seconds, because the 600 MB dependency layer was reused. On the VPS, `docker pull` only fetched the 2 MB source layer, not the whole image.

## 🟡 Real Example Hindi mein
एक Indian fintech की CI pipeline हर build में 9 मिनट लेती थी क्योंकि `COPY . .` , `npm ci` से पहले था; हर commit पर 900 packages दोबारा install होते थे। Order बदलने (manifests, install, फिर source) के बाद सिर्फ code बदलने पर build 40 सेकंड में हुई, क्योंकि 600 MB की dependency layer reuse हुई। VPS पर `docker pull` ने पूरी image की जगह सिर्फ 2 MB की source layer खींची।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile - see layers being created
# Layer(s): base image (shared by every node:20-alpine user)
FROM node:20-alpine
# Metadata only, no filesystem layer content
WORKDIR /app
# Layer 1: dependency manifests (changes rarely)
COPY package.json package-lock.json ./
# Layer 2: installed packages (expensive, cached while manifests unchanged)
RUN npm ci --omit=dev
# Layer 3: source code (changes on every commit)
COPY . .
# Metadata: default command
CMD ["node", "server.js"]
```

```bash
# Inspect layers of an image
docker build -t layers-demo .                  # build
docker history layers-demo                     # one line per layer with SIZE
docker inspect layers-demo --format '{{json .RootFS.Layers}}'   # layer content hashes (diff IDs)
docker image inspect layers-demo --format '{{len .RootFS.Layers}}'  # number of layers
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Demonstrates layer pitfalls and fixes
FROM debian:bookworm-slim
# BAD (3 layers, files remain in layer 1 and 2):
#   RUN apt-get update
#   RUN apt-get install -y curl
#   RUN rm -rf /var/lib/apt/lists/*
# GOOD: one layer, cleanup in the same instruction
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
# BAD: a secret copied then deleted is still readable in the earlier layer
#   COPY id_rsa /root/.ssh/id_rsa
#   RUN git clone git@... && rm /root/.ssh/id_rsa
# GOOD: use a BuildKit secret mount, which is never stored in a layer
RUN --mount=type=secret,id=gitcreds,target=/run/secrets/gitcreds \
    test -f /run/secrets/gitcreds && echo "secret available only during this RUN" || true
# Large, rarely-changing content first; volatile content last
COPY vendor-data/ /opt/vendor-data/
# Frequently changing code last, so earlier layers stay cached
COPY app/ /opt/app/
# Default command
CMD ["ls", "/opt/app"]
```

```bash
# Build with a secret that does NOT end up in any layer (BuildKit)
echo "token123" > /tmp/gitcreds.txt                        # temp secret file for the demo
docker build --secret id=gitcreds,src=/tmp/gitcreds.txt -t layers-adv .   # pass it only at build
docker history --no-trunc layers-adv | grep -i token || echo "secret not found in history"
rm /tmp/gitcreds.txt                                        # cleanup
```

---

## 🟠 My Stack Integration
**Node.js**: layer order manifests -> `npm ci` -> source. **FastAPI**: `requirements.txt` -> `pip install` -> `app/`. **React**: install layer cached, build layer changes each commit. **GitHub Actions**: `cache-from/cache-to type=gha` stores layers between runs. **VPS/ECR**: only changed layers are pushed/pulled, so deploys are fast.

```yaml
# .github/workflows/build.yml - layer caching in CI (action versions are examples)
name: build
on: [push]                                   # run on each push
jobs:
  image:
    runs-on: ubuntu-latest                   # GitHub runner
    steps:
      - uses: actions/checkout@v4            # fetch code
      - uses: docker/setup-buildx-action@v3  # BuildKit builder with cache export
      - uses: docker/build-push-action@v6    # build image
        with:
          context: .                         # Dockerfile directory
          push: false                        # just build in this example
          tags: myorg/api:ci                 # tag
          cache-from: type=gha               # import cached layers
          cache-to: type=gha,mode=max        # export all layers to cache
```

Security: every layer is permanent history; anyone with the image can `docker history` or extract layers. Never COPY secrets, even if deleted later.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `COPY . .` first, then install dependencies.
✅ Correct: Copy manifests, install, then copy source.

❌ Mistake 2: Deleting files in a later `RUN` hoping to shrink the image.
✅ Correct: Create and delete in the same `RUN`, or use multi-stage.

❌ Mistake 3: Hundreds of tiny `RUN` lines or, the opposite, one giant `RUN` that breaks caching.
✅ Correct: Group related commands that change together; separate stable from volatile steps.

---

## 🧠 Tricky Interview Question
You change only a comment in `app.js`. Which layers are rebuilt, and why does `RUN npm ci` run again if `COPY . .` came before it?

Answer: Cache validity is checked top-down. `COPY . .` includes `app.js`, so its checksum changed, so this layer and every layer after it (including `npm ci`) are invalid. Layers before it remain cached. This is why `COPY package*.json` and install must come before `COPY . .`.

---

## ⚫ Interview Questions + Answers

Q1: Which instructions create layers?
A1: `RUN`, `COPY`, `ADD` create filesystem layers; `ENV`, `CMD`, `EXPOSE`, `WORKDIR`, `LABEL` only add metadata (empty layers in history).

Q2: Are layers writable?
A2: Image layers are read-only; a container gets one thin writable layer on top, deleted with the container.

Q3: How do layers get shared?
A3: By content-addressable IDs; images with the same base layer store it once and pull only missing ones.

Q4: What invalidates the build cache?
A4: A changed instruction text, changed copied file contents (checksum) or a changed parent layer; later layers are then rebuilt.

Q5: How many layers can an image have?
A5: Historically a 127 limit with some storage drivers; keep it low (tens), but it is rarely the real constraint now.

---

## 🔷 When to Use + When Not to Use
✅ Use (optimize layers) when:
- CI build time or pull time matters.
- You deploy many images with a shared base.

❌ Avoid over-optimizing when:
- A prototype where readability is more important.
- Merging everything into one `RUN` makes debugging harder.

---

## 📊 Visual Diagram
```
  Container (running)   +-----------------------+  writable layer (thin)
                        +-----------------------+
  Image (read-only)     | COPY . .    (source)  |  changes every commit
                        | RUN npm ci  (modules) |  cached
                        | COPY package*.json    |  cached
                        | WORKDIR /app          |  metadata
                        | node:20-alpine layers |  shared with other images
                        +-----------------------+
  Change at layer N  -->  layers above N are rebuilt
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Layer | Read-only diff of the filesystem | filesystem के बदलाव की read-only परत |
| Build cache | Reused layers from earlier builds | पुरानी builds की reuse layers |
| Writable layer | Thin top layer of a container | container की ऊपरी writable परत |
| Diff ID | Hash of an uncompressed layer | layer का hash |
| Cache invalidation | Rebuilding after a change | बदलाव पर दोबारा build |

---

## ⚡ 3-Line Summary
English: Images are stacks of read-only layers created by RUN, COPY and ADD.
Layers are cached and shared, so put stable steps first and changing steps last.
Never put secrets in layers because history keeps them.
Hindi: Images RUN, COPY और ADD से बनी read-only layers का stack हैं।
Layers cache और share होती हैं, इसलिए stable steps पहले और बदलने वाले बाद में रखो।
Secrets कभी layers में मत डालो क्योंकि history उन्हें रखती है।

---

## ➡️ Next Topic
**102. Union File System**: how Docker stacks those layers into one filesystem view (overlay2) and copy-on-write.
