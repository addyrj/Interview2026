# 40. GitHub Releases
# हिंदी में: GitHub Releases (रिलीज़ प्रकाशित करना)

---

## 🔵 Simple Definition (English)
A **GitHub Release** is a named, versioned snapshot of your project built on top of a Git **tag** (like `v1.4.0`). It bundles release notes (changelog), auto-generated source code archives, and optional binary assets (zip, tar.gz, build artifacts). It is the official "this is version X" page of a repo.

## 🔵 सरल परिभाषा (Hindi)
**GitHub Release** आपके project का एक नाम और version वाला snapshot है जो Git **tag** (जैसे `v1.4.0`) पर बनता है। इसमें release notes (changelog), source code का अपने-आप बना archive, और चाहें तो binary files (zip, tar.gz, build artifacts) होती हैं। यह repo का आधिकारिक "यह version X है" पेज है।

---

## 🔴 Problem it Solves
Before releases, teams just said "deploy the latest main". Nobody knew which commit was in production, what changed, or how to roll back. Tags alone are bare pointers with no notes and no downloadable files. Releases give a human-readable history, a stable download link, a rollback target, and a trigger point for CI/CD (`on: release`).

## 🔴 यह क्यों बना? (Hindi)
पहले teams बस "main का latest deploy कर दो" बोलती थीं। पता नहीं होता था कि production में कौन सा commit है, क्या बदला, और rollback कैसे करें। सिर्फ tag एक खाली pointer है - उसमें notes या downloadable files नहीं होतीं। Releases human-readable history, fixed download link, rollback target, और CI/CD का trigger (`on: release`) देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Merge finished work into main (CI is green)
Step 2 → Pick next version using SemVer: MAJOR.MINOR.PATCH (v1.4.0)
Step 3 → Create an annotated tag:  git tag -a v1.4.0 -m "..."
Step 4 → Push the tag:             git push origin v1.4.0
Step 5 → Create Release on that tag (UI, `gh release create`, or Actions)
Step 6 → GitHub generates notes (PR titles since last tag) + source zips
Step 7 → Attach assets (build output, checksums) and publish
Step 8 → "release: published" event triggers deploy / docker push workflows
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पूरा काम main में merge करो (CI green होना चाहिए)
Step 2 → SemVer से अगला version चुनो: MAJOR.MINOR.PATCH (v1.4.0)
Step 3 → Annotated tag बनाओ:  git tag -a v1.4.0 -m "..."
Step 4 → Tag push करो:         git push origin v1.4.0
Step 5 → उस tag पर Release बनाओ (UI, `gh release create`, या Actions से)
Step 6 → GitHub notes (पिछले tag के बाद के PR titles) और source zip बना देता है
Step 7 → Assets (build output, checksums) attach करके publish करो
Step 8 → "release: published" event deploy / docker push workflow चला देता है
```

---

## 🟡 Real World Example
Think of how a Node.js library or the `gh` CLI itself ships: every version has a Release page with a changelog and downloadable binaries. For your own stack: your FastAPI backend is on a VPS behind Nginx. Instead of deploying every push, you cut `v2.3.1` on Friday; the release workflow builds a Docker image tagged `2.3.1`, pushes it, and SSHes to the VPS to pull exactly that tag. If a bug appears, you redeploy `v2.3.0` in two minutes because the old release and image still exist.

## 🟡 Real Example Hindi mein
Node.js library या `gh` CLI कैसे ship होती है देखो: हर version का Release page होता है जिसमें changelog और binaries होती हैं। आपके stack में: FastAPI backend VPS पर Nginx के पीछे चलता है। हर push पर deploy करने की जगह आप शुक्रवार को `v2.3.1` release काटते हैं; release workflow Docker image `2.3.1` tag से बनाकर push करता है और VPS पर SSH करके ठीक वही tag pull करता है। Bug आए तो `v2.3.0` दो मिनट में दोबारा deploy हो जाता है क्योंकि पुराना release और image मौजूद हैं।

---

## 💻 Code / Config Example — Basic
```bash
# ---- Create a release from the terminal with GitHub CLI (gh) ----
# Run inside your repo on the main branch, after `gh auth login`

git checkout main                       # switch to the main branch
git pull origin main                    # get the latest commits so the tag lands on the newest code
git tag -a v1.0.0 -m "First stable release"   # annotated tag = has author, date, message
git push origin v1.0.0                  # publish the tag to GitHub (tags are NOT pushed by default)

gh release create v1.0.0 \
  --title "v1.0.0 - First stable release" \
  --generate-notes                      # auto-build notes from merged PRs since previous tag
# ^ creates a published release on tag v1.0.0

gh release list                         # show all releases of this repo
gh release view v1.0.0                  # print the release details
gh release download v1.0.0 -p "*.zip"   # download assets that match the pattern *.zip
gh release delete v1.0.0 --yes          # delete the release (tag stays unless --cleanup-tag is added)
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/release.yml
# Trigger: push of a SemVer tag. Builds a Node.js/React app, creates a
# GitHub Release with notes + assets + checksum, marks pre-releases automatically.
# Action versions are examples - check the Marketplace for current majors.
name: Release                                   # name shown in the Actions tab

on:                                             # events that start this workflow
  push:
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"                 # stable tags like v1.2.3
      - "v[0-9]+.[0-9]+.[0-9]+-*"               # pre-release tags like v1.2.3-rc.1

permissions:                                    # least privilege for GITHUB_TOKEN
  contents: write                               # required to create a release and upload assets

concurrency:                                    # never run two releases for the same ref together
  group: release-${{ github.ref }}              # group key per tag
  cancel-in-progress: false                     # never cancel a half-done release

jobs:
  release:                                      # single job id
    runs-on: ubuntu-latest                      # GitHub-hosted Linux runner
    steps:
      - name: Checkout code                     # step label
        uses: actions/checkout@v4               # fetch the repo at the tagged commit
        with:
          fetch-depth: 0                        # full history so generated notes can diff tags

      - name: Setup Node                        # install Node.js toolchain
        uses: actions/setup-node@v4             # official setup action
        with:
          node-version: 20                      # example LTS version
          cache: npm                            # cache ~/.npm between runs

      - name: Install and build                 # produce the deployable bundle
        run: |                                  # multi-line shell script
          npm ci                                # clean, lockfile-exact install
          npm test --if-present                 # run tests only if a test script exists
          npm run build                         # builds React app into ./dist

      - name: Package artifacts                 # zip the build and compute a checksum
        run: |
          VERSION="${GITHUB_REF_NAME}"          # e.g. v1.2.3 (tag name)
          tar -czf "app-${VERSION}.tar.gz" dist # compress build output
          sha256sum "app-${VERSION}.tar.gz" > "app-${VERSION}.sha256"  # integrity file for downloaders

      - name: Detect pre-release                # tags containing "-" (v1.2.3-rc.1) are pre-releases
        id: meta                                # id lets later steps read outputs
        run: |
          if [[ "${GITHUB_REF_NAME}" == *-* ]]; then
            echo "prerelease=true" >> "$GITHUB_OUTPUT"    # write step output
          else
            echo "prerelease=false" >> "$GITHUB_OUTPUT"   # stable release
          fi

      - name: Publish GitHub Release            # create the Release page and upload files
        uses: softprops/action-gh-release@v2    # popular third-party action (pin a SHA in strict orgs)
        with:
          generate_release_notes: true          # auto notes from merged PRs
          prerelease: ${{ steps.meta.outputs.prerelease }}  # true/false from previous step
          files: |                              # assets attached to the release
            app-*.tar.gz
            app-*.sha256
```

---

## 🟠 My Stack Integration
**Node.js / React:** attach the `dist/` bundle. **FastAPI:** the release event builds and pushes a Docker image tagged with the release version. **VPS + Nginx:** a deploy job pulls that exact tag and restarts the container. **AWS:** the same tag can be pushed to ECR (Elastic Container Registry) for ECS/EC2 later.

```yaml
# .github/workflows/deploy-on-release.yml
# Runs when a release is PUBLISHED (not drafts), deploys that version to the VPS.
name: Deploy on Release                         # workflow name

on:
  release:
    types: [published]                          # only when someone publishes (not draft/edit)

jobs:
  deploy:
    runs-on: ubuntu-latest                      # runner
    environment: production                     # lets you add manual approval + environment secrets
    steps:
      - name: Deploy to VPS over SSH            # run commands on your server
        uses: appleboy/ssh-action@v1.0.3       # example SSH action; version is an example
        with:
          host: ${{ secrets.VPS_HOST }}         # server IP stored as secret
          username: ${{ secrets.VPS_USER }}     # non-root deploy user
          key: ${{ secrets.VPS_SSH_KEY }}       # private key from secrets, never in repo
          script: |                             # commands executed on the VPS
            set -e                              # stop at first error
            cd /srv/myapp                       # app folder holding docker-compose.yml
            export APP_VERSION="${{ github.event.release.tag_name }}"  # e.g. v2.3.1
            docker compose pull                 # pull the image tag referenced by APP_VERSION
            docker compose up -d                # recreate only changed containers
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Creating a release from a lightweight/untested commit on a feature branch.
✅ Correct: Tag only commits on `main` after CI is green; use `--target main` or tag locally first.

❌ Mistake 2: Using `latest` or branch names as the deploy version, so rollback is impossible.
✅ Correct: Deploy immutable SemVer tags (`v2.3.1`) and keep the previous one to roll back.

❌ Mistake 3: Forgetting `permissions: contents: write`, so the workflow fails with 403.
✅ Correct: Grant only that permission on the release job, nothing broader.

❌ Mistake 4: Deleting a release and assuming the tag is gone (or re-pushing a moved tag).
✅ Correct: Tags are separate; never move a published tag, publish a new patch version instead.

❌ Mistake 5 (security): Putting tokens/SSH keys in release assets or notes, or using a third-party action by floating tag with `contents: write`.
✅ Correct: Secrets only in GitHub Secrets; pin actions to a commit SHA; checksum (and ideally sign) release assets; protect tags with rulesets so only maintainers can create `v*`.

---

## 🧠 Tricky Interview Question
You pushed tag `v1.5.0`, the release workflow ran, but you spot a bug minutes later. You delete the tag, fix the code, and push `v1.5.0` again on a new commit. The VPS still runs the old code. Why, and what is the right approach?

Answer: Docker/registries and any machine that already pulled `v1.5.0` cache the old content, and tags are mutable pointers, so consumers cannot know it changed. Re-using a version breaks the promise that a version is immutable. The right approach is to leave `v1.5.0` alone (mark it as a pre-release or note the bug), fix, and publish `v1.5.1`. Also, a deleted release does not delete the git tag, and a pushed tag can cause confusing duplicate triggers.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a Git tag and a GitHub Release?
A1: A tag is a Git object pointing to a commit. A Release is a GitHub feature on top of a tag that adds notes, assets, and events. Releases need a tag; tags do not need releases.

Q2: What is SemVer?
A2: MAJOR.MINOR.PATCH. Bump MAJOR for breaking changes, MINOR for backward-compatible features, PATCH for bug fixes.

Q3: Draft vs pre-release vs published?
A3: Draft is invisible to the public and does not fire `published`. Pre-release is public but marked "not production ready". Published (latest) is the official stable release.

Q4: Which workflow trigger runs on releases?
A4: `on: release: types: [published]` (also `created`, `released`, `prereleased`). A common alternative is `on: push: tags: ['v*']`.

Q5: How do you attach build artifacts to a release automatically?
A5: In Actions use `softprops/action-gh-release` with `files:`, or run `gh release upload <tag> file` with `GH_TOKEN: ${{ github.token }}` and `contents: write`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You ship versioned software, libraries, CLIs, or Docker images
- You need a changelog, rollback target, or audit of what ran in production
- You want a controlled deploy trigger (release published -> deploy)

❌ Avoid when:
- A tiny internal script deploys on every merge (continuous deployment makes releases noise)
- You would use it to store large secrets or huge binaries (use a registry or S3)

---

## 📊 Visual Diagram
```
 developer        GitHub                  GitHub Actions            VPS / AWS
    |                |                          |                       |
    | merge to main  |                          |                       |
    |--------------->|                          |                       |
    | git tag v1.4.0 |                          |                       |
    | git push tag   |                          |                       |
    |--------------->| tag event ------------->| build + test          |
    |                |                          | docker build/push     |
    |                |<--- create Release ------| attach assets         |
    |                | release: published ---->| deploy job ---------->| pull v1.4.0
    |                |                          |                       | restart app
    v                v                          v                       v
 Release page = notes + zip + checksums + rollback target
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tag | Named pointer to a commit | commit पर लगा नाम/निशान |
| Release | Tag + notes + assets | tag का आधिकारिक version पेज |
| SemVer | MAJOR.MINOR.PATCH versioning | version नंबर देने का नियम |
| Pre-release | Public but not stable | अस्थिर/टेस्टिंग release |
| Draft | Unpublished release | अप्रकाशित मसौदा |
| Asset | File attached to release | release से जुड़ी file |
| Changelog | List of changes | बदलावों की सूची |

---

## ⚡ 3-Line Summary
English: A Release is a versioned page on top of a Git tag with notes and downloadable assets.
English: Use SemVer, tag only green commits on main, never move a published tag.
English: `on: release: published` or tag pushes can trigger Docker build and VPS/AWS deploy.
Hindi: Release, Git tag के ऊपर बना version वाला पेज है जिसमें notes और files होती हैं।
Hindi: SemVer इस्तेमाल करो, सिर्फ green commit पर tag लगाओ, publish हुआ tag कभी मत हिलाओ।
Hindi: `release: published` या tag push से Docker build और VPS/AWS deploy शुरू हो सकता है।

---

## ➡️ Next Topic
**41. What is Docker + Why Use It** - releases give you versioned code; Docker packages that code and its dependencies into a versioned, portable image you can actually run anywhere.
