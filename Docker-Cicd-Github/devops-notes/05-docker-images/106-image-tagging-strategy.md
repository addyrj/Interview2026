# 106. Image Tagging Strategy
# हिंदी में: Image Tagging की रणनीति

---

## 🔵 Simple Definition (English)
An **image tagging strategy** is the set of rules your team uses to name image versions, so every image can be traced to a commit, a release and an environment. Good tags are unique, predictable and (mostly) immutable.

## 🔵 सरल परिभाषा (Hindi)
**Image tagging strategy** वे नियम हैं जिनसे आपकी team image versions के नाम रखती है, ताकि हर image को एक commit, release और environment तक trace किया जा सके। अच्छे tags unique, predictable और (ज़्यादातर) immutable होते हैं।

---

## 🔴 Problem it Solves
- Without rules, tags like `final`, `final2`, `new`, `test` appear and nobody knows what runs in prod.
- You cannot connect a running container to a Git commit during an incident.
- Rollbacks and audits become guesswork.
- Different environments (dev/staging/prod) need clear promotion paths.

## 🔴 यह क्यों बना? (Hindi)
- नियम न हों तो `final`, `final2`, `new`, `test` जैसे tags बन जाते हैं और prod में क्या चल रहा है कोई नहीं जानता।
- Incident के समय running container को Git commit से जोड़ना मुश्किल।
- Rollback और audit अंदाज़े पर होते हैं।
- Dev/staging/prod के बीच promotion का साफ रास्ता चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → CI builds the image once per commit
Step 2 → Tag with git short SHA (unique, immutable): myorg/api:3f9a1c2
Step 3 → On a Git release tag v1.4.2, also add semver tags: 1.4.2, 1.4, 1
Step 4 → Moving aliases per environment (optional): staging, prod-current
Step 5 → Deploy the SHA/semver tag; promote the SAME image (no rebuild) to the next environment
Step 6 → Registry lifecycle policy deletes old SHA tags after N days
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → CI हर commit पर image एक बार build करता है
Step 2 → git short SHA से tag (unique, immutable): myorg/api:3f9a1c2
Step 3 → Git release tag v1.4.2 पर semver tags भी: 1.4.2, 1.4, 1
Step 4 → Environment aliases (optional): staging, prod-current
Step 5 → SHA/semver tag deploy करो; वही image अगले environment में promote करो (rebuild नहीं)
Step 6 → Registry lifecycle policy N दिन बाद पुराने SHA tags हटा देती है
```

---

## 🟡 Real World Example
Zomato-like delivery backend: every merge to `main` produces `orders-api:<sha>` and is auto-deployed to staging. After QA approval a release manager creates Git tag `v2.8.0`; the pipeline retags the same digest as `2.8.0` and `2.8`, and production pulls `2.8.0`. When a bug appears, the on-call engineer reads the container's image label, finds the exact commit and rolls back to `2.7.4` in minutes.

## 🟡 Real Example Hindi mein
Zomato जैसे delivery backend में `main` पर हर merge से `orders-api:<sha>` बनता है और staging पर auto-deploy होता है। QA approval के बाद release manager Git tag `v2.8.0` बनाता है; pipeline उसी digest को `2.8.0` और `2.8` के रूप में retag करती है, और production `2.8.0` pull करता है। Bug आए तो on-call engineer image label से सही commit ढूंढकर कुछ मिनटों में `2.7.4` पर rollback कर देता है।

---

## 💻 Code / Config Example — Basic
```bash
# Get the short git SHA for the current commit
SHA=$(git rev-parse --short HEAD)
# Build once and give two tags: unique SHA and human alias
docker build -t myorg/api:"$SHA" -t myorg/api:dev .
# Push the immutable SHA tag
docker push myorg/api:"$SHA"
# Add another tag to an existing image without rebuilding
docker tag myorg/api:"$SHA" myorg/api:1.4.2
# Push the release tag
docker push myorg/api:1.4.2
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/release.yml - SHA tag on every push, semver tags on v* tags
name: release
# Trigger on main pushes and version tags
on:
  push:
    branches: [main]
    tags: ["v*.*.*"]
jobs:
  image:
    runs-on: ubuntu-latest
    permissions:
      # Needed to read repo code
      contents: read
      # Needed to push to GitHub Container Registry
      packages: write
    steps:
      # Get the code
      - uses: actions/checkout@v4
      # Log in to GHCR using the built-in token (no extra secret)
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      # Compute tags and OCI labels automatically
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,format=short
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=ref,event=branch
      # Build and push using the computed tags and labels
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```
(Action versions are examples. Workflow not run locally.)

---

## 🟠 My Stack Integration
Use one image name per service (`myorg/api`, `myorg/web`) and one scheme everywhere. On the VPS, a deploy script receives the tag and writes it into `.env`.

```yaml
# docker-compose.yml on VPS - tag comes from .env (TAG=3f9a1c2)
services:
  api:
    # FastAPI service pinned to the tag CI produced
    image: ghcr.io/myorg/api:${TAG}
    restart: unless-stopped
  web:
    # React build served by Nginx, same tag scheme
    image: ghcr.io/myorg/web:${TAG}
    restart: unless-stopped
    ports:
      - "80:80"
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Rebuilding for each environment (`staging` build, then `prod` build).
✅ Correct: Build once, promote the same digest.

❌ Mistake 2: Using branch names or `dev` as the only tag.
✅ Correct: Always include an immutable SHA tag too.

❌ Mistake 3: Tags with characters Docker rejects (`feature/login` has a slash which is invalid in a tag).
✅ Correct: Sanitize to `feature-login`.

❌ Mistake 4: No retention policy, registry grows to hundreds of GB.
✅ Correct: Lifecycle rules (ECR) or cleanup jobs keep last N tags.

---

## 🧠 Tricky Interview Question
"Production is `1.4.2`. A hotfix is pushed with the same tag `1.4.2` to fix a typo. Is that safe?"

Answer: No. Re-pushing a released tag breaks immutability: nodes that already pulled it keep the old bits, new nodes get the new bits, and audit logs mislead. Publish `1.4.3` (a new patch). Enable tag immutability where the registry supports it (AWS ECR does).

---

## ⚫ Interview Questions + Answers

Q1: Why tag with git SHA?
A1: It is unique per commit and links runtime to source code.

Q2: Why also semver tags?
A2: Humans and release notes use them; `1.4` style floating tags let consumers follow patches.

Q3: What is "build once, promote many"?
A3: Build a single image, test it, and move the same digest through environments, avoiding "works in staging, differs in prod".

Q4: How to find which commit a running container uses?
A4: Check the tag, or OCI labels (`org.opencontainers.image.revision`) via `docker inspect`.

Q5: Can one image have many tags?
A5: Yes. Tags are just pointers to one digest.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one environment or more than one deploy per week.
- Teams need audit trails and fast rollbacks.

❌ Avoid when:
- Using floating tags (`1`, `1.4`) as the deployment reference in critical prod; they move.
- Embedding timestamps only; they say nothing about the code.

---

## 📊 Visual Diagram
```
 git commit 3f9a1c2 ─► CI build ─► image digest D1
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
        api:3f9a1c2           api:1.4.2              api:1.4
       (immutable)          (release, fixed)     (floating minor)
              │
   staging ◄──┘      prod ◄── same digest D1 (promoted, not rebuilt)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tag | Human label for an image | image का label |
| Digest | Content hash identity | content hash पहचान |
| Promotion | Moving same image to next env | वही image अगले env में |
| Floating tag | Tag that moves (1.4) | बदलने वाला tag |
| Retention | Auto-delete old images | पुरानी images हटाना |
| OCI label | Metadata on image | image का metadata |

---

## ⚡ 3-Line Summary
English: Use unique SHA tags plus semver release tags.
Build once and promote the same digest across environments.
Never reuse a released tag; add retention rules.
Hindi: Unique SHA tags के साथ semver release tags रखो।
एक बार build करो और वही digest हर environment में promote करो।
Released tag दोबारा मत इस्तेमाल करो; retention rules लगाओ।

---

## ➡️ Next Topic
**107. Semantic Versioning for Images** - how MAJOR.MINOR.PATCH maps to image tags and what counts as a breaking change.
