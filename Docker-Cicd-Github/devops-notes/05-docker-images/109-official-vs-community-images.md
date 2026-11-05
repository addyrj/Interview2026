# 109. Official vs Community Images
# हिंदी में: Official बनाम Community Images

---

## 🔵 Simple Definition (English)
**Docker Official Images** are curated repositories (like `nginx`, `node`, `postgres`) reviewed by Docker and upstream maintainers. **Community images** are published by anyone under `username/image`. **Verified Publisher** and **Docker-Sponsored Open Source** badges mark trusted vendors. Trust level differs a lot.

## 🔵 सरल परिभाषा (Hindi)
**Docker Official Images** curated repositories हैं (जैसे `nginx`, `node`, `postgres`) जिन्हें Docker और upstream maintainers review करते हैं। **Community images** कोई भी `username/image` के नाम से publish कर सकता है। **Verified Publisher** और **Docker-Sponsored Open Source** badges भरोसेमंद vendors दिखाते हैं। दोनों के भरोसे का स्तर बहुत अलग है।

---

## 🔴 Problem it Solves
- Docker Hub has millions of images; anyone can upload one, including ones with cryptominers or backdoors.
- Unmaintained images carry old, unpatched libraries.
- Typosquatting: `ngnix` or `postgress` look real but are not.
- Teams need a rule for what may appear in `FROM` and in production compose files.

## 🔴 यह क्यों बना? (Hindi)
- Docker Hub पर लाखों images हैं; कोई भी upload कर सकता है, cryptominer या backdoor वाली भी।
- Unmaintained images में पुरानी, बिना patch वाली libraries होती हैं।
- Typosquatting: `ngnix` या `postgress` असली जैसे दिखते हैं पर असली नहीं।
- Teams को नियम चाहिए कि `FROM` और production compose में क्या आ सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Search Docker Hub; look for the "Docker Official Image" / "Verified Publisher" badge
Step 2 → Check: last updated, pull count, source repo link, Dockerfile visible, open issues
Step 3 → Pull and inspect: docker history, docker inspect, scan with Trivy / Docker Scout
Step 4 → Prefer official image; else vendor's verified image; else build yourself from official base
Step 5 → Mirror approved images into your private registry (ECR/GHCR) and pin by digest
Step 6 → Block unknown registries by policy (CI check or admission controller)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Docker Hub पर खोजो; "Docker Official Image" / "Verified Publisher" badge देखो
Step 2 → जाँचो: last updated, pull count, source repo link, Dockerfile दिखता है?, open issues
Step 3 → Pull करके जाँचो: docker history, docker inspect, Trivy / Docker Scout scan
Step 4 → Official image पसंद करो; नहीं तो vendor की verified image; नहीं तो official base से खुद बनाओ
Step 5 → Approved images अपनी private registry (ECR/GHCR) में mirror करो और digest से pin करो
Step 6 → Policy से अज्ञात registries block करो (CI check या admission controller)
```

---

## 🟡 Real World Example
A developer needs Redis quickly and uses `someuser/redis-fast`. A week later security finds it contains an outbound connection to an unknown IP. The company policy changes: only `redis` (official), mirrored into their ECR as `ecr/.../mirror/redis@sha256:...`. Pulls come from ECR, so Docker Hub rate limits and malicious updates no longer matter.

## 🟡 Real Example Hindi mein
एक developer को जल्दी Redis चाहिए और वह `someuser/redis-fast` इस्तेमाल करता है। एक हफ्ते बाद security को पता चलता है कि उसमें किसी अज्ञात IP से outbound connection है। कंपनी policy बदलती है: सिर्फ `redis` (official), जो अपने ECR में `ecr/.../mirror/redis@sha256:...` के रूप में mirror है। Pull ECR से होता है, तो Docker Hub rate limits और malicious updates की चिंता नहीं रहती।

---

## 💻 Code / Config Example — Basic
```bash
# Official image has no username prefix (library/ is implied)
docker pull nginx:1.27-alpine
# Community image has a publisher prefix - inspect before trusting
docker pull someuser/some-tool:1.0
# See how the image was built, layer by layer
docker history someuser/some-tool:1.0
# Check for exposed ports, env, entrypoint and user
docker inspect someuser/some-tool:1.0 --format '{{.Config.User}} {{.Config.Entrypoint}} {{.Config.ExposedPorts}}'
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/mirror-image.yml - mirror an approved official image to your GHCR
name: mirror-image
# Run manually when you approve a new version
on:
  workflow_dispatch:
    inputs:
      version:
        description: "nginx tag to mirror (example 1.27.2-alpine)"
        required: true
jobs:
  mirror:
    runs-on: ubuntu-latest
    permissions:
      # Needed to push packages to GHCR
      packages: write
    steps:
      # Log in to GHCR with built-in token
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      # Pull official image, retag, push (digest is kept the same for a single-arch copy)
      - name: Mirror
        run: |
          docker pull nginx:${{ github.event.inputs.version }}
          docker tag nginx:${{ github.event.inputs.version }} ghcr.io/${{ github.repository_owner }}/mirror-nginx:${{ github.event.inputs.version }}
          docker push ghcr.io/${{ github.repository_owner }}/mirror-nginx:${{ github.event.inputs.version }}
```
(Not run locally. Multi-arch images need `docker buildx imagetools create` or `crane copy` to keep all platforms; the plain pull/push above copies only your runner's platform. Example only.)

---

## 🟠 My Stack Integration
Stack images you will use: `node`, `python`, `nginx`, `postgres`, `redis`, `mongo` are all Docker Official Images. For Prometheus/Grafana use the vendor orgs (`prom/prometheus`, `grafana/grafana`), which are verified publishers.

```yaml
# docker-compose.yml - only official / verified images, pinned
services:
  # Reverse proxy: Docker Official Image
  nginx:
    image: nginx:1.27-alpine
  # Database: Docker Official Image
  postgres:
    image: postgres:16.4-alpine
    environment:
      # Password injected from env file, not committed
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  # Monitoring: verified publisher image
  prometheus:
    image: prom/prometheus:v2.54.1
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using the first search result without checking the publisher.
✅ Correct: Look for the Official/Verified badge and read the source repository.

❌ Mistake 2: Assuming "official" means "no CVEs".
✅ Correct: Official only means reviewed and maintained; still scan.

❌ Mistake 3: Passing secrets to an unverified image.
✅ Correct: Run unknown images in isolation without credentials; prefer not running them.

❌ Mistake 4: Depending directly on Docker Hub in CI (rate limits).
✅ Correct: Authenticate pulls or mirror into your own registry.

---

## 🧠 Tricky Interview Question
"An official image is updated and your pinned tag `nginx:1.27-alpine` suddenly has a different digest. Is this a compromise?"

Answer: Not necessarily. Official image maintainers rebuild tags regularly to pick up OS and library security patches, so a minor-level tag is mutable. If you need bit-for-bit repeatability, pin the digest (`nginx@sha256:...`) and update it deliberately via Renovate/Dependabot.

---

## ⚫ Interview Questions + Answers

Q1: How do you recognise an official image?
A1: No username prefix (`nginx`), the "Docker Official Image" badge on Hub, and source in docker-library repos.

Q2: What is a Verified Publisher?
A2: A commercial vendor verified by Docker (for example Bitnami was one, or Grafana Labs). Badge indicates identity, not a security guarantee.

Q3: How to vet a community image?
A3: Check Dockerfile source, update frequency, scan it, run non-root without secrets, or rebuild it from source yourself.

Q4: What is typosquatting?
A4: Malicious images with names close to popular ones, hoping for typing mistakes.

Q5: Why mirror images to a private registry?
A5: Availability, rate limit avoidance, scanning control, and protection from upstream tag changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Official images for language runtimes, databases, proxies.
- Verified vendor images for tools you do not build.

❌ Avoid when:
- Unknown publisher, no source, last update over a year ago.
- You would have to pass credentials or mount sensitive volumes.

---

## 📊 Visual Diagram
```
 Trust level (high ──► low)

 Docker Official  >  Verified Publisher  >  Open-source sponsored  >  Random community
 (nginx, node)       (grafana/grafana)       (project-owned)          (user/tool)
      │                    │                       │                       │
      └────── scan + pin digest + mirror to private registry ─────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Official Image | Curated Docker Hub image | curated official image |
| Verified Publisher | Vendor verified by Docker | verified vendor |
| Community image | Anyone's image | कोई भी publisher |
| Typosquatting | Look-alike names | मिलते-जुलते नाम |
| Mirror | Copy to own registry | अपनी registry में copy |
| Supply chain | Where your software comes from | software की उत्पत्ति |

---

## ⚡ 3-Line Summary
English: Official and verified images are far safer than random community ones.
Always check source, update frequency and scan results.
Mirror approved images into your own registry and pin them.
Hindi: Official और verified images random community images से कहीं सुरक्षित हैं।
हमेशा source, update frequency और scan results जाँचो।
Approved images अपनी registry में mirror करो और pin करो।

---

## ➡️ Next Topic
**110. Building Images** - now we create our own image from a Dockerfile, layer by layer.
