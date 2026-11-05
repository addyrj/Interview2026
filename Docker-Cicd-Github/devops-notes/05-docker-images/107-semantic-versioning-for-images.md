# 107. Semantic Versioning for Images
# हिंदी में: Images के लिए Semantic Versioning

---

## 🔵 Simple Definition (English)
**Semantic Versioning (SemVer)** names a release `MAJOR.MINOR.PATCH` (for example `2.5.1`). MAJOR = breaking change, MINOR = backward-compatible feature, PATCH = backward-compatible bug fix. For images, we publish several tags per release so users choose how much automatic change they accept.

## 🔵 सरल परिभाषा (Hindi)
**Semantic Versioning (SemVer)** release का नाम `MAJOR.MINOR.PATCH` रखता है (जैसे `2.5.1`)। MAJOR = breaking change, MINOR = backward-compatible feature, PATCH = backward-compatible bug fix। Images के लिए हम एक release पर कई tags publish करते हैं ताकि users तय कर सकें कि कितना automatic बदलाव चाहिए।

---

## 🔴 Problem it Solves
- "Version 7" or "build 4821" tells users nothing about risk.
- Consumers of your image (other teams, customers) cannot know whether an upgrade will break them.
- Without floating tags, people must manually edit every patch release.

## 🔴 यह क्यों बना? (Hindi)
- "Version 7" या "build 4821" से risk का पता नहीं चलता।
- आपकी image इस्तेमाल करने वाले (दूसरी teams, customers) नहीं जान पाते कि upgrade से कुछ टूटेगा या नहीं।
- Floating tags न हों तो हर patch release पर हाथ से edit करना पड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decide the change type: breaking / feature / fix
Step 2 → Bump the number: 2.5.1 -> 3.0.0 | 2.6.0 | 2.5.2
Step 3 → Create the Git tag v2.5.2 (the source of truth)
Step 4 → CI publishes tags: 2.5.2 (exact), 2.5 (latest patch of 2.5), 2 (latest minor of 2)
Step 5 → Consumers pick: exact for prod safety, 2.5 for auto-patching, 2 for auto-features
Step 6 → Pre-release tags (2.6.0-rc.1) are used for testing and never moved into floating tags
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → बदलाव का type तय करो: breaking / feature / fix
Step 2 → नंबर बढ़ाओ: 2.5.1 -> 3.0.0 | 2.6.0 | 2.5.2
Step 3 → Git tag v2.5.2 बनाओ (source of truth)
Step 4 → CI tags publish करती है: 2.5.2 (exact), 2.5 (2.5 का latest patch), 2 (2 का latest minor)
Step 5 → Consumers चुनते हैं: prod में exact, auto-patch के लिए 2.5, auto-feature के लिए 2
Step 6 → Pre-release tags (2.6.0-rc.1) testing के लिए, floating tags में नहीं जाते
```

---

## 🟡 Real World Example
Your company ships an internal `auth-service` image used by 12 teams. v2.5.1 to v2.5.2 fixes a JWT bug, so teams on `2.5` get it automatically after a restart. v2.6.0 adds a new endpoint; teams on `2` get it. v3.0.0 removes the old `/login` route; nobody is moved automatically, and teams migrate on their schedule because the release notes flag a MAJOR bump.

## 🟡 Real Example Hindi mein
आपकी कंपनी का internal `auth-service` image 12 teams इस्तेमाल करती हैं। v2.5.1 से v2.5.2 में JWT bug fix है, तो `2.5` वाली teams को restart के बाद अपने आप मिल जाता है। v2.6.0 में नया endpoint है; `2` वाली teams को मिलता है। v3.0.0 पुराना `/login` route हटाता है; किसी को अपने आप नहीं मिलता, और MAJOR bump देखकर teams अपने समय पर migrate करती हैं।

---

## 💻 Code / Config Example — Basic
```bash
# Release version (normally from a git tag)
VERSION=2.5.2
# Split into parts using bash parameter expansion
MAJOR=${VERSION%%.*}
# Remove the major, then take the minor
MINOR=${VERSION#*.}; MINOR=${MINOR%%.*}
# Build once with the exact version tag
docker build -t myorg/auth:"$VERSION" .
# Add floating tags pointing at the same image
docker tag myorg/auth:"$VERSION" myorg/auth:"$MAJOR.$MINOR"
docker tag myorg/auth:"$VERSION" myorg/auth:"$MAJOR"
# Push all three tags
docker push myorg/auth:"$VERSION"
docker push myorg/auth:"$MAJOR.$MINOR"
docker push myorg/auth:"$MAJOR"
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/semver-image.yml - tags generated from the git tag vX.Y.Z
name: semver-image
# Run only when a version tag is pushed
on:
  push:
    tags: ["v*.*.*"]
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      # Read code
      contents: read
      # Push to GHCR
      packages: write
    steps:
      # Checkout source
      - uses: actions/checkout@v4
      # Authenticate with the built-in token
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      # Generate 2.5.2, 2.5, 2 (major is skipped for 0.x by the action's design)
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=semver,pattern={{major}}
      # Build and push all tags in one go
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```
(Not run locally; action versions are examples.)

---

## 🟠 My Stack Integration
Node.js: keep `package.json` version in sync with the git tag (`npm version patch` creates the tag). FastAPI: expose version from an env var `APP_VERSION` set at build time. In prod compose pin the exact version; in staging use `2.5` to test patches early.

```yaml
# docker-compose.yml - build arg injects version into the app
services:
  api:
    build:
      # Build from current folder
      context: .
      args:
        # APP_VERSION is read by the Dockerfile ARG
        APP_VERSION: ${APP_VERSION:-0.0.0-dev}
    # Exact tag in production
    image: myorg/api:${APP_VERSION:-0.0.0-dev}
    environment:
      # App can return this on /health
      APP_VERSION: ${APP_VERSION:-0.0.0-dev}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Bumping only PATCH while removing an API field.
✅ Correct: Breaking change means MAJOR.

❌ Mistake 2: Production using floating tag `2` with no testing.
✅ Correct: Prod pins `2.5.2`; use floating tags in dev/staging.

❌ Mistake 3: Putting a `v` prefix inconsistently (`v2.5.2` vs `2.5.2`).
✅ Correct: Git tag `v2.5.2`, image tag `2.5.2`. Choose one image convention.

❌ Mistake 4: Treating base image upgrade as "no change".
✅ Correct: A Node 20 to 22 switch can break users; consider a MINOR or MAJOR bump.

---

## 🧠 Tricky Interview Question
"If you only change the base OS package versions (security patches) with no code change, what version bump is that?"

Answer: Usually PATCH (`2.5.2` to `2.5.3`), since the contract is unchanged. A runtime major change (Node 20 to 22) can break consumers, so treat as MINOR/MAJOR depending on risk. Many teams also rebuild the same version for CVEs; if so, document that the tag was re-pushed or add a build suffix like `2.5.2-r1` to preserve traceability.

---

## ⚫ Interview Questions + Answers

Q1: What do MAJOR, MINOR, PATCH mean?
A1: Breaking change, compatible feature, compatible fix.

Q2: Why publish tags 2.5.2, 2.5 and 2?
A2: Consumers choose pinning level: exact, patches-only, or minor-updates.

Q3: Are floating tags immutable?
A3: No. They move on each release, so avoid them for strict reproducibility.

Q4: What is a pre-release tag?
A4: `2.6.0-rc.1`, used before the final release; never aliased to `2.6`.

Q5: Does SemVer apply to apps without a public API?
A5: Still useful as a communication tool; the "API" is what operators depend on (env vars, ports, volumes).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Images consumed by other teams or customers.
- You do regular releases with changelogs.

❌ Avoid when:
- Pure continuous deployment of an internal single-instance service; the git SHA alone may be enough.
- You cannot honestly judge breaking changes (SemVer then becomes misleading).

---

## 📊 Visual Diagram
```
 Git tag v2.5.2
      │
      ▼
 image digest D (one build)
      │
 ┌────┼───────────┬──────────┐
 ▼    ▼           ▼          ▼
2.5.2 2.5         2        (3f9a1c2)
exact patch-float minor-float  SHA

 3.0.0 (breaking) ► new line: 3.0.0, 3.0, 3  (2.x untouched)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SemVer | MAJOR.MINOR.PATCH scheme | version नियम |
| Breaking change | Not backward-compatible | पुराना code टूटे |
| Floating tag | Moves with releases | बदलने वाला tag |
| Pre-release | rc/beta version | test version |
| Pinning | Fixing exact version | exact version तय करना |
| Changelog | List of changes | बदलावों की सूची |

---

## ⚡ 3-Line Summary
English: SemVer tells users how risky an upgrade is.
Publish exact, minor and major tags from one Git tag.
Pin exact versions in prod; float in lower environments.
Hindi: SemVer बताता है कि upgrade कितना risky है।
एक Git tag से exact, minor और major tags publish करो।
Prod में exact pin करो; lower environments में float करो।

---

## ➡️ Next Topic
**108. Base Image Selection** - choosing the foundation (alpine, slim, distroless) that your tags are built on.
