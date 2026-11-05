# 249. release Event
# हिंदी में: release Event (Release publish होने पर workflow)

---

## 🔵 Simple Definition (English)
The `release` event fires when a GitHub **Release** is created, published, edited, deleted, or marked pre-release/released. Most pipelines use `types: [published]` to build and ship a versioned artifact (Docker image, npm package, zip) whenever someone publishes a release tagged like `v1.4.0`.

## 🔵 सरल परिभाषा (Hindi)
`release` event तब चलता है जब GitHub **Release** बनाया, publish, edit, delete या pre-release/released चिह्नित किया जाए। ज़्यादातर pipelines `types: [published]` इस्तेमाल करते हैं ताकि `v1.4.0` जैसे tag वाला release publish होते ही versioned artifact (Docker image, npm package, zip) बने और भेजा जाए।

---

## 🔴 Problem it Solves
Deploying on every push to `main` is too eager for many products (mobile backends, SDKs, regulated apps). Teams need an explicit "this is version 1.4.0" moment with notes and approval. Tagging by hand and running scripts is error-prone. A GitHub Release is a human-visible, auditable decision; the `release` event connects it to automation: immutable version tags, release notes, and production deploys.

## 🔴 यह क्यों बना? (Hindi)
हर `main` push पर deploy करना कई products (mobile backend, SDK, regulated apps) के लिए बहुत जल्दबाज़ी है। Team को "यह version 1.4.0 है" जैसा स्पष्ट क्षण चाहिए, notes और approval के साथ। हाथ से tag लगाकर scripts चलाना गलती-प्रवण है। GitHub Release इंसान को दिखने वाला, audit होने वाला निर्णय है; `release` event उसे automation से जोड़ता है: अपरिवर्तनीय version tags, release notes और production deploy।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developer merges to main, then creates a Release in UI/CLI: tag v1.4.0 + notes.
Step 2 → If tag does not exist, GitHub creates it at the chosen target commit.
Step 3 → On "Publish release" GitHub emits `release` with action `published` (and `created`, `released`).
Step 4 → Workflow runs; github.ref = refs/tags/v1.4.0, github.sha = tagged commit, github.event.release.* has metadata.
Step 5 → Jobs build image with tag = github.event.release.tag_name, push to registry.
Step 6 → Optionally upload assets to the release (gh release upload) and deploy to production.
Step 7 → Drafts do NOT trigger `published`; pre-release triggers `prereleased`, final `released`.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Developer main में merge करके UI/CLI से Release बनाता है: tag v1.4.0 + notes।
Step 2 → Tag न हो तो GitHub चुने हुए commit पर tag बना देता है।
Step 3 → "Publish release" पर GitHub `release` event भेजता है, action `published` (और `created`, `released`)।
Step 4 → Workflow चलता है; github.ref = refs/tags/v1.4.0, github.sha = tag वाला commit, github.event.release.* में metadata।
Step 5 → Jobs image को tag = github.event.release.tag_name से बनाकर registry में push करते हैं।
Step 6 → चाहें तो release में assets upload (gh release upload) और production deploy।
Step 7 → Draft `published` trigger नहीं करता; pre-release पर `prereleased`, final पर `released`।
```

Release activity types: `published`, `unpublished`, `created`, `edited`, `deleted`, `prereleased`, `released`. Note: workflows triggered by `GITHUB_TOKEN`-created releases do not start new runs; use a PAT or GitHub App token if automation creates the release.

---

## 🟡 Real World Example
A B2B analytics company ships a self-hosted Docker image to customers. Engineering publishes release `v3.2.0`; the workflow builds multi-arch images (`amd64`, `arm64`), tags `3.2.0`, `3.2`, `latest`, pushes to Docker Hub/GHCR, attaches an SBOM file to the release, and deploys the same version to their own production VPS after approval. Pre-releases (`v3.3.0-rc1`) only deploy to staging.

## 🟡 Real Example Hindi mein
एक B2B analytics कंपनी customers को self-hosted Docker image देती है। Engineering release `v3.2.0` publish करती है; workflow multi-arch images (`amd64`, `arm64`) बनाता है, tags `3.2.0`, `3.2`, `latest` लगाता है, Docker Hub/GHCR में push करता है, release में SBOM file जोड़ता है, और approval के बाद वही version अपने production VPS पर deploy करता है। Pre-releases (`v3.3.0-rc1`) सिर्फ़ staging पर जाते हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/release-basic.yml
name: Release Basic                       # workflow name

on:
  release:                                # trigger on GitHub Release events
    types: [published]                    # only when a release is published (not drafts)

jobs:
  show:                                   # job id
    runs-on: ubuntu-latest                # runner
    steps:
      - run: echo "Tag is ${{ github.event.release.tag_name }}"        # e.g. v1.4.0
      - run: echo "Pre-release? ${{ github.event.release.prerelease }}" # true/false
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/release.yml
name: Release

on:
  release:
    types: [published]                    # fires for both stable and pre-releases when published

permissions:
  contents: write                         # needed to upload assets to the release
  packages: write                         # push image to GHCR

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    outputs:
      version: ${{ steps.ver.outputs.version }}   # pass clean version to later jobs
    steps:
      - uses: actions/checkout@v4         # checkout the tagged commit
      - id: ver                           # compute version without leading "v"
        env:
          TAG: ${{ github.event.release.tag_name }}   # via env, not inline in script
        run: |
          [[ "$TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.]+)?$ ]] || { echo "Bad tag: $TAG"; exit 1; }  # semver check
          echo "version=${TAG#v}" >> "$GITHUB_OUTPUT"   # strip "v" and expose as output
      - uses: docker/setup-qemu-action@v3 # emulation for arm64 builds
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64   # multi-arch
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ steps.ver.outputs.version }}
            ghcr.io/${{ github.repository }}:latest
          provenance: true                # attach build provenance attestation

  attach-assets:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create tarball of compose files
        run: tar czf deploy-bundle.tgz docker-compose.yml nginx/    # package deploy files
      - name: Upload to release
        env:
          GH_TOKEN: ${{ github.token }}   # gh CLI auth
          TAG: ${{ github.event.release.tag_name }}
        run: gh release upload "$TAG" deploy-bundle.tgz --clobber   # attach (overwrite if exists)

  deploy-production:
    needs: build-and-push
    if: github.event.release.prerelease == false   # stable releases only
    runs-on: ubuntu-latest
    environment: production               # approval gate
    steps:
      - name: Deploy
        env:
          HOST: ${{ secrets.VPS_HOST }}
          KEY: ${{ secrets.VPS_SSH_KEY }}
          VERSION: ${{ needs.build-and-push.outputs.version }}
        run: |
          install -m 600 /dev/null key && printf '%s\n' "$KEY" > key
          ssh -i key -o StrictHostKeyChecking=accept-new "deploy@$HOST" \
            "cd /srv/app && VERSION=$VERSION docker compose up -d --pull always"   # compose file reads ${VERSION}
```

(YAML parsed locally; not executed on GitHub.)

---

## 🟠 My Stack Integration
- **Node.js / FastAPI:** release tag becomes image tag and `/health` returns the version (injected as build arg).
- **React:** build static bundle, upload zip to release, sync to S3/Nginx directory `releases/v1.4.0` and switch symlink `current`.
- **Nginx / VPS:** immutable folder-per-release, rollback = repoint symlink / old tag.
- **AWS:** release triggers ECR push + ECS task definition revision with the exact tag.

```yaml
# Compose file on VPS that consumes the release version
services:
  api:
    image: ghcr.io/acme/api:${VERSION:?set VERSION}   # fail fast if VERSION is missing
    restart: unless-stopped
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Listening to `created` AND `published` - runs twice or on drafts.
✅ Correct: Use `types: [published]`.

❌ Mistake 2: Creating the release from a workflow with `GITHUB_TOKEN` and expecting another workflow to start.
✅ Correct: Use a PAT/GitHub App token, or call the next workflow with `workflow_call`.

❌ Mistake 3: Using `latest` only; no way to roll back.
✅ Correct: Push immutable version tags; update `latest` as an extra pointer.

❌ Mistake 4: Trusting the tag name in shell: tag `v1;rm -rf` is possible.
✅ Correct: Validate semver with regex and pass via env.

---

## 🧠 Tricky Interview Question
You publish a release from a draft and notice the workflow ran on the wrong code - the tag was created from `main` an hour ago, but `main` has moved. What commit does the workflow build?

Answer: The commit the tag points to (`github.sha`), not the latest `main`. The release's `target_commitish` was resolved to a SHA when the tag was created. `actions/checkout` on a release event checks out `refs/tags/<tag>`. That is a feature: the build reproduces exactly what was tagged. If you wanted newer code, create a new tag.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `published` and `released`?
A1: `published` fires for any publish (stable or pre-release). `released` fires when a release or pre-release is edited to a full release. `prereleased` for pre-releases.

Q2: Where is the version available?
A2: `github.event.release.tag_name`, and `github.ref_name` (the tag).

Q3: Release vs `push: tags: ["v*"]`?
A3: Tag push fires without creating release notes; the `release` event requires a Release object (notes, assets, UI). Tag-push is easier for pure automation; release event suits human-gated publishing.

Q4: How can you restrict who releases?
A4: Repository roles (write access) and tag protection/rulesets; deploy job behind a protected environment.

Q5: How do you avoid deploying pre-releases to prod?
A5: `if: github.event.release.prerelease == false` or listen to `types: [released]`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Versioned artifacts and changelogs are part of the product.
- You want a human gate for production.

❌ Avoid when:
- You deploy continuously on every merge (use `push`).
- Release creation is automated in the same workflow (just continue in that workflow).

---

## 📊 Visual Diagram

```
 merge to main ─► Create Release v1.4.0 (notes) ─► Publish
                                                    │ event: release/published
                                                    ▼
                                      checkout refs/tags/v1.4.0
                                                    │
                       ┌────────────────────────────┼─────────────────────────┐
                       ▼                            ▼                         ▼
              build + push image         attach assets to release     deploy (stable only)
              :1.4.0 :latest             deploy-bundle.tgz            environment: production
                                                                       approval -> VPS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| release | Tagged, published version with notes | Notes सहित tag वाला version |
| tag | Fixed pointer to a commit | Commit का स्थिर संकेतक |
| semver | MAJOR.MINOR.PATCH versioning | संस्करण नियम |
| pre-release | Not-final release | अंतिम नहीं वाला release |
| asset | File attached to a release | Release से जुड़ी file |
| provenance | Proof of how an image was built | Image कैसे बनी इसका प्रमाण |

---

## ⚡ 3-Line Summary
English: `release` fires on Release actions; use `published` for builds and deploys.
English: Workflow runs on the tagged commit with `github.event.release` metadata.
English: Validate tags, skip pre-releases for prod, use environments.
Hindi: `release` Release की क्रियाओं पर चलता है; build और deploy के लिए `published` लें।
Hindi: Workflow tag वाले commit पर `github.event.release` metadata के साथ चलता है।
Hindi: Tags validate करें, prod के लिए pre-release छोड़ें, environments इस्तेमाल करें।

---

## ➡️ Next Topic
**250. repository_dispatch Event** - trigger a workflow from outside GitHub (another system or repo) through the API with a custom payload.
