# 103. Image Manifest
# हिंदी में: Image Manifest

---

## 🔵 Simple Definition (English)
An image manifest is a JSON document stored in a registry that describes an image: the digest of its config blob and the ordered list of layer blobs (with media types and sizes). A manifest list (OCI image index) points to several manifests, one per CPU architecture.

## 🔵 सरल परिभाषा (Hindi)
Image manifest registry में रखा एक JSON document है जो image का वर्णन करता है: उसके config blob का digest और layer blobs की क्रमबद्ध list (media types और sizes के साथ)। Manifest list (OCI image index) कई manifests की तरफ इशारा करती है, हर CPU architecture के लिए एक।

---

## 🔴 Problem it Solves
A registry needs a standard way to say "this tag means these layers, in this order, with this config". Clients also must verify integrity (no tampered layers) and pick the correct build for their CPU (amd64 for EC2, arm64 for Graviton or Apple Silicon). The manifest gives content-addressed integrity and multi-architecture support under one tag.

## 🔴 यह क्यों बना? (Hindi)
Registry को एक standard तरीका चाहिए कहने के लिए: "यह tag इन layers, इस क्रम और इस config को दर्शाता है"। Clients को integrity भी verify करनी होती है (layers के साथ छेड़छाड़ नहीं) और अपने CPU के लिए सही build चुनना होता है (EC2 के लिए amd64, Graviton या Apple Silicon के लिए arm64)। Manifest एक tag के नीचे content-addressed integrity और multi-architecture support देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker pull myorg/api:1.0.0
Step 2 → GET /v2/<repo>/manifests/1.0.0  (registry API)
Step 3 → If it is an index: choose the manifest for my os/arch
Step 4 → Read manifest: config digest + layers[] digests
Step 5 → GET /v2/<repo>/blobs/<digest> for each missing layer
Step 6 → Verify sha256 of each blob == digest in manifest
Step 7 → Unpack layers (overlay2) and store config
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker pull myorg/api:1.0.0
Step 2 → GET /v2/<repo>/manifests/1.0.0  (registry API)
Step 3 → Index हो तो: अपने os/arch का manifest चुनो
Step 4 → Manifest पढ़ो: config digest + layers[] digests
Step 5 → जो layers missing हैं उनके लिए GET /v2/<repo>/blobs/<digest>
Step 6 → हर blob का sha256 == manifest का digest verify करो
Step 7 → Layers unpack करो (overlay2) और config store करो
```

---

## 🟡 Real World Example
A team on Apple M1 laptops built an image and pushed it, then their amd64 EC2 instance failed with "exec format error". The manifest listed only `linux/arm64`. They fixed it using `docker buildx build --platform linux/amd64,linux/arm64 --push`, producing a manifest list so the same tag now works on laptops, EC2 x86 and Graviton.

## 🟡 Real Example Hindi mein
Apple M1 laptops पर एक team ने image build करके push की, फिर उनके amd64 EC2 instance पर "exec format error" आया। Manifest में सिर्फ `linux/arm64` था। उन्होंने `docker buildx build --platform linux/amd64,linux/arm64 --push` से manifest list बनाई, और अब वही tag laptops, EC2 x86 और Graviton पर चलता है।

---

## 💻 Code / Config Example — Basic

```bash
# Show the manifest (or manifest list) of an image in a registry, no pull needed
docker manifest inspect node:20-alpine                 # JSON list of platforms (may need experimental CLI on very old Docker)

# Newer, recommended way with buildx
docker buildx imagetools inspect node:20-alpine        # human readable: digest, platforms, manifests

# Inspect a local image config
docker image inspect node:20-alpine --format '{{.Architecture}} {{.Os}}'   # arch and os of the local copy
```

An example single-platform OCI manifest (simplified, digests shortened for reading):

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "config": {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "digest": "sha256:aaaa...config",
    "size": 1469
  },
  "layers": [
    { "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip", "digest": "sha256:bbbb...base",   "size": 3400000 },
    { "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip", "digest": "sha256:cccc...deps",   "size": 41000000 },
    { "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip", "digest": "sha256:dddd...source", "size": 120000 }
  ]
}
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# fetch-manifest.sh - read a manifest straight from Docker Hub via the registry API
# Requires: curl, jq. Public image only. Not run on the machine where these notes were written.
set -euo pipefail                                     # fail fast
REPO="library/alpine"                                 # official alpine image repo
TAG="3.20"                                            # example tag

# 1. get an anonymous pull token from Docker Hub auth service
TOKEN=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:${REPO}:pull" | jq -r .token)

# 2. ask for the manifest list / index (Accept header lists the types we understand)
curl -s -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.oci.image.index.v1+json" \
  -H "Accept: application/vnd.docker.distribution.manifest.list.v2+json" \
  "https://registry-1.docker.io/v2/${REPO}/manifests/${TAG}" | jq '.manifests[] | {platform, digest}'
```

```yaml
# .github/workflows/multiarch.yml - publish a multi-arch manifest list (action versions are examples)
name: multiarch
on:
  push:
    tags: ["v*"]                                  # run on version tags
jobs:
  publish:
    runs-on: ubuntu-latest                        # GitHub runner
    permissions:
      contents: read                              # read repo
      packages: write                             # push to GHCR
    steps:
      - uses: actions/checkout@v4                 # get code
      - uses: docker/setup-qemu-action@v3         # emulation for arm64 builds
      - uses: docker/setup-buildx-action@v3       # multi-platform builder
      - uses: docker/login-action@v3              # log in to GHCR
        with:
          registry: ghcr.io                       # registry host
          username: ${{ github.actor }}           # user running the workflow
          password: ${{ secrets.GITHUB_TOKEN }}   # built-in token
      - uses: docker/build-push-action@v6         # build + push manifest list
        with:
          context: .                              # Dockerfile directory
          platforms: linux/amd64,linux/arm64      # one manifest per platform + index
          push: true                              # publish
          tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}  # tag from git tag
```

---

## 🟠 My Stack Integration
**VPS/EC2 x86**: pulls the `linux/amd64` manifest; **Graviton** (cheaper) pulls `arm64`; **Apple Silicon** dev laptops use arm64. Build multi-arch once in GitHub Actions. **Nginx/Node/FastAPI** official bases are already multi-arch. **ECR**: supports manifest lists; `aws ecr batch-get-image` returns the manifest.

```bash
# On the VPS: confirm what you actually pulled
docker image inspect ghcr.io/myorg/api:1.0.0 --format '{{.Os}}/{{.Architecture}} {{.Id}}'  # platform + image id
```

Security: the manifest digest is the integrity root; signing tools (cosign) sign the manifest digest. Pull by digest (topic 104) to guarantee exact content.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Building only on an M-series Mac and deploying to x86 servers.
✅ Correct: Use `--platform linux/amd64` or multi-platform buildx.

❌ Mistake 2: Confusing the image ID with the manifest digest.
✅ Correct: Image ID is the hash of the config; the manifest digest (`RepoDigests`) is the hash of the manifest. They differ.

❌ Mistake 3: Using QEMU-emulated arm64 builds for heavy compiles and waiting 40 minutes.
✅ Correct: Use native arm64 runners or cross-compilation.

---

## 🧠 Tricky Interview Question
`docker pull app:1.0` gives different image IDs on an M1 Mac and an x86 server, yet the tag is identical. Is something wrong?

Answer: No. The tag points to a manifest list; each client resolves its own platform's manifest, which has different layers and config, therefore different image IDs. The list's digest is the same for both, but the platform manifests differ.

---

## ⚫ Interview Questions + Answers

Q1: What is inside a manifest?
A1: Schema version, media type, config descriptor (digest, size) and an ordered layers array with digests and sizes.

Q2: Manifest vs manifest list (index)?
A2: A manifest describes one platform's image; a list/index points to several manifests keyed by platform.

Q3: Config blob vs manifest?
A3: Config holds runtime data (env, cmd, history, diff IDs, arch); the manifest points to the config and compressed layers.

Q4: Docker v2 schema 2 vs OCI?
A4: Nearly identical formats; OCI is the open standard, Docker supports both media types.

Q5: How does a registry verify content?
A5: Every blob/manifest is addressed by its sha256; clients recompute and compare.

---

## 🔷 When to Use + When Not to Use
✅ Use (inspect / build multi-arch) when:
- Mixed x86 and ARM fleet or Apple Silicon developers.
- Debugging "exec format error" or pull mismatches.

❌ Avoid when:
- Single known architecture and no ARM plans; single-platform builds are simpler and faster.

---

## 📊 Visual Diagram
```
 tag  myorg/api:1.0.0
        |
        v
 +-------------------- index (manifest list) --------------------+
 |  linux/amd64 -> sha256:AAA     linux/arm64 -> sha256:BBB      |
 +--------------|---------------------------|--------------------+
                v                           v
        manifest AAA                 manifest BBB
        config  -> blob              config  -> blob
        layers  -> blob, blob, blob  layers  -> blob, blob, blob
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Manifest | JSON describing config + layers | config और layers का JSON |
| Manifest list / Index | Points to per-platform manifests | platform वाले manifests की list |
| Blob | Layer or config stored by digest | digest से रखी layer/config |
| Media type | Format label of a document | document का format label |
| Platform | OS + CPU architecture | OS + CPU architecture |

---

## ⚡ 3-Line Summary
English: A manifest lists the config and layer digests of one image.
A manifest list lets one tag serve multiple CPU architectures.
Everything is addressed by sha256 for integrity.
Hindi: Manifest एक image के config और layer digests की list है।
Manifest list एक tag को कई CPU architectures के लिए चलाती है।
Integrity के लिए सब कुछ sha256 से addressed है।

---

## ➡️ Next Topic
**104. Image Digest vs Tag**: why tags move and digests do not, and how to pin images safely.
