# 123. Docker Content Trust
# हिंदी में: Docker Content Trust (DCT)

---

## 🔵 Simple Definition (English)
Docker Content Trust (DCT) is Docker's built-in image signing feature (based on Notary v1 and The Update Framework). When you turn it on with `DOCKER_CONTENT_TRUST=1`, Docker signs images on push and refuses to pull or run unsigned tags.

## 🔵 सरल परिभाषा (Hindi)
Docker Content Trust (DCT), Docker का अपना built-in image signing feature है (Notary v1 और The Update Framework पर आधारित)। `DOCKER_CONTENT_TRUST=1` चालू करने पर Docker push के समय image sign करता है और unsigned tags को pull या run करने से मना कर देता है।

---

## 🔴 Problem it Solves
- Pulling by tag trusts the registry blindly. A hijacked account can replace `myorg/api:1.0.0`.
- Man-in-the-middle or registry compromise can serve altered images.
- Teams wanted a simple switch in the Docker client itself, with no extra tools, to enforce "only signed images".

## 🔴 यह क्यों बना? (Hindi)
- Tag से pull करना registry पर आँख मूँदकर भरोसा है। Hijack हुआ account `myorg/api:1.0.0` बदल सकता है।
- Man-in-the-middle या registry compromise से बदली हुई image आ सकती है।
- Teams चाहती थीं कि Docker client में ही एक switch हो, बिना अतिरिक्त tool के, जो "सिर्फ signed images" लागू करे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → export DOCKER_CONTENT_TRUST=1 (client side environment variable)
Step 2 → First docker push of a tag: Docker creates keys
         root key (offline, most important) + repository key (per repo) + timestamp/snapshot keys (server side)
Step 3 → You set passphrases; keys live in ~/.docker/trust/
Step 4 → Push uploads the image AND signed metadata to a Notary server (Docker Hub has one)
Step 5 → docker pull / run / build FROM checks the metadata: signature valid? tag points to expected digest?
Step 6 → Unsigned tag -> error "No valid trust data for <tag>"; the command stops
Step 7 → Inspect: docker trust inspect --pretty myorg/api
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → export DOCKER_CONTENT_TRUST=1 (client की environment variable)
Step 2 → किसी tag का पहला docker push: Docker keys बनाता है
         root key (offline, सबसे ज़रूरी) + repository key (हर repo की) + timestamp/snapshot keys (server की तरफ)
Step 3 → आप passphrase रखते हैं; keys ~/.docker/trust/ में रहती हैं
Step 4 → Push image और signed metadata दोनों Notary server पर भेजता है (Docker Hub में Notary है)
Step 5 → docker pull / run / build FROM metadata जाँचते हैं: signature सही? tag अपेक्षित digest पर है?
Step 6 → Unsigned tag -> "No valid trust data for <tag>" error; command रुक जाता है
Step 7 → देखने के लिए: docker trust inspect --pretty myorg/api
```

---

## 🟡 Real World Example
A bank's ops team sets `DOCKER_CONTENT_TRUST=1` on all production Docker hosts. The release engineer signs images with a hardware-protected key. When a developer accidentally pushes an unsigned `api:1.9.1-test` and the host tries to pull it, Docker refuses. The mistake is caught before production runs anything unreviewed.

## 🟡 Real Example Hindi mein
एक bank की ops team सभी production Docker hosts पर `DOCKER_CONTENT_TRUST=1` सेट करती है। Release engineer hardware-protected key से images sign करता है। जब developer गलती से unsigned `api:1.9.1-test` push करता है और host उसे pull करने की कोशिश करता है, तो Docker मना कर देता है। गलती production पर कुछ भी चलने से पहले पकड़ ली जाती है।

---

## 💻 Code / Config Example — Basic
```bash
# Turn DCT on for the current shell (client side only; not a server setting)
export DOCKER_CONTENT_TRUST=1                           # 1 = enforce signed images

# Pushing now signs the tag. First time it asks for root + repository passphrases
docker push myorg/api:1.0.0                             # uploads image and signed trust data

# Pulling an unsigned tag now fails
docker pull myorg/api:dev-unsigned                      # error: No valid trust data

# Look at who signed what
docker trust inspect --pretty myorg/api                 # signers, signed tags, digests

# One-off bypass for a single command (use rarely, for debugging)
DOCKER_CONTENT_TRUST=0 docker pull myorg/api:dev-unsigned   # overrides env for this command only

# Explicitly sign an already pushed tag (needs signer keys set up)
docker trust sign myorg/api:1.0.0                       # signs the tag in the registry

# Add a delegated signer (team member / CI) using their public cert
docker trust signer add --key ci.pub ci-bot myorg/api   # authorise another signer for this repo
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# ci-trust-push.sh - sign and push from CI using a delegation key (example flow; test in a sandbox first)
set -euo pipefail                                        # fail fast on errors and unset variables

export DOCKER_CONTENT_TRUST=1                            # enforce signing on push
export DOCKER_CONTENT_TRUST_REPOSITORY_PASSPHRASE="${DCT_PASSPHRASE}"   # passphrase from CI secret, never hardcode

# Import the CI delegation PRIVATE key (stored as a CI secret, written to a temp file)
umask 077                                                # new files readable only by owner
printf '%s' "${DCT_CI_KEY}" > /tmp/ci.key                # write secret to file (key secret from CI)
docker trust key load /tmp/ci.key --name ci-bot          # load the key into ~/.docker/trust
shred -u /tmp/ci.key 2>/dev/null || rm -f /tmp/ci.key    # delete the key file right away

docker build -t myorg/api:"${GIT_SHA}" ./api             # build image tagged with commit SHA
docker push myorg/api:"${GIT_SHA}"                       # push + sign in one step (DCT enabled)
docker trust inspect myorg/api:"${GIT_SHA}" >/dev/null   # confirm trust data exists, else fail the job
```

```yaml
# docker-compose.yml fragment: Compose follows DOCKER_CONTENT_TRUST from the environment
services:
  api:                                                   # service using a signed image
    image: myorg/api:1.0.0                               # with DCT=1, pull fails if tag is unsigned
    restart: unless-stopped                              # keep service running after reboot
# Run with: DOCKER_CONTENT_TRUST=1 docker compose pull   # enforce at pull time on the VPS
```

---

## 🟠 My Stack Integration
- **VPS:** set `DOCKER_CONTENT_TRUST=1` in the deploy user's shell profile or CD script so `docker compose pull` refuses unsigned tags (verify behavior on your Compose version).
- **Docker Hub:** works out of the box for Hub repos (Notary service included).
- **GHCR / ECR:** Notary v1 is NOT supported there. Use Cosign (note 122) instead.
- **Node.js / FastAPI / React:** nothing changes in the app; only push/pull behavior changes. Note `FROM node:20` also needs signed official images (Docker Official Images are signed).
- **Status:** Docker has been retiring Notary v1 for Docker Official Images/Hub signing; check the current Docker docs before building new processes on DCT.

```yaml
# GitHub Actions step on the deploy job (fragment)
- name: Pull with trust enforced             # step name
  env:
    DOCKER_CONTENT_TRUST: "1"                # env var read by the docker CLI
  run: docker pull myorg/api:${{ github.sha }}   # fails if no valid trust data for this tag
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Losing the root key or its passphrase.
✅ Correct: Back up `~/.docker/trust/private` offline in a secure place; without it you cannot rotate or recover signers.

❌ Mistake 2: Turning DCT on globally and then wondering why `docker build` fails on base images without signatures.
✅ Correct: Use signed base images, or disable DCT per command only when you understand the risk.

❌ Mistake 3: Believing DCT protects `docker save/load` files or images already pulled before enabling.
✅ Correct: Trust is checked at pull/push/run-from-tag time on the client; local images are not re-verified.

❌ Mistake 4: Using DCT on registries without Notary.
✅ Correct: On GHCR/ECR use Cosign.

---

## 🧠 Tricky Interview Question
You enabled `DOCKER_CONTENT_TRUST=1` on the server, but `docker run myorg/api:1.0.0` still started an unsigned image. Why?

Answer: The image was already on the host from before DCT, and local images are not re-checked. Also `docker run` by digest (`@sha256:`) is allowed because the digest itself pins content, and DCT is a client-side environment setting, so a different user or shell without the variable bypasses it. Make the setting part of the deploy script and remove stale local images.

---

## ⚫ Interview Questions + Answers

Q1: What does DCT do?
A1: Signs images on push and verifies signatures on pull, using Notary and TUF metadata.

Q2: How do you enable it?
A2: `export DOCKER_CONTENT_TRUST=1` on the client. The environment variable is the standard way.

Q3: Which keys exist in DCT?
A3: Root (offline, identity), repository/targets (signs tags), snapshot and timestamp (freshness, often managed by the server).

Q4: DCT vs Cosign?
A4: DCT is Docker-specific (Notary v1) and needs a Notary server. Cosign is OCI-native, works with any registry and supports keyless signing; it is the modern choice.

Q5: What happens if a tag has no trust data under DCT?
A5: `docker pull` and `docker run` fail with "No valid trust data".

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You are on Docker Hub with a Notary-based signing process already.
- You need a quick client-side enforcement switch.

❌ Avoid when:
- Your registry is GHCR or ECR (no Notary).
- You are starting a new project; choose Cosign/Sigstore.

---

## 📊 Visual Diagram
```
 Developer / CI
   DOCKER_CONTENT_TRUST=1
        | docker push
        v
 +----------------+        signed metadata        +----------------+
 | Docker Registry| <---------------------------> | Notary server  |
 | image layers   |                               | TUF metadata   |
 +----------------+                               +----------------+
        ^
        | docker pull (DCT=1)
        |  1. fetch metadata  2. verify signature  3. compare digest
        v
 +----------------+
 | VPS            |  valid -> run     invalid / unsigned -> ERROR
 +----------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DCT | Docker Content Trust, client side signing | Docker का signing feature |
| Notary | Server storing signed metadata | signed metadata रखने वाला server |
| TUF | The Update Framework, secure update design | सुरक्षित update की design |
| Root key | Offline master key of trust | trust की मुख्य offline key |
| Delegation | Letting another key sign | दूसरे को sign करने का अधिकार |
| Trust data | Signed info for a tag | tag की signed जानकारी |

---

## ⚡ 3-Line Summary
English: DCT enforces signed images through the Docker client with `DOCKER_CONTENT_TRUST=1`.
English: It relies on Notary v1 and works mainly with Docker Hub.
English: For new projects, prefer Cosign because it works everywhere and supports keyless signing.
Hindi: DCT, `DOCKER_CONTENT_TRUST=1` से Docker client में signed images लागू करता है।
Hindi: यह Notary v1 पर चलता है और मुख्यतः Docker Hub के साथ काम करता है।
Hindi: नए projects में Cosign चुनें क्योंकि वह हर जगह चलता है और keyless signing देता है।

---

## ➡️ Next Topic
**124. OCI Image Spec** — the open standard that defines what an image really is (manifest, config, layers), which signing and registries all build on.
