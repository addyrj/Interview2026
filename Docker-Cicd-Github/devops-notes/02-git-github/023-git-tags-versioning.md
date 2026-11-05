# 23. Git Tags + Versioning
# हिंदी में: Git Tags + Versioning

---

## 🔵 Simple Definition (English)
A **Git tag** is a permanent, human-readable label on one specific commit, usually a release like `v1.4.0`. Unlike a branch, a tag does not move. **Annotated tags** also store author, date and message and can be signed.

## 🔵 सरल परिभाषा (Hindi)
**Git tag** एक specific commit पर लगा permanent, पढ़ने लायक label है, आमतौर पर release जैसे `v1.4.0`। Branch की तरह tag आगे नहीं बढ़ता। **Annotated tags** में author, date और message भी रहता है और उन्हें sign किया जा सकता है।

---

## 🔴 Problem it Solves
Commit hashes like `9fceb02` are unreadable, and branches keep moving. When a customer reports a bug in "the version from March", you must find the exact code. Tags give stable names to releases, let CI trigger deployments, enable one-command rollbacks (`git checkout v1.3.2`), and link Docker images to source.

## 🔴 यह क्यों बना? (Hindi)
`9fceb02` जैसे commit hashes पढ़ने लायक नहीं और branches आगे बढ़ती रहती हैं। जब customer "मार्च वाले version" में bug बताए, तब exact code चाहिए। Tags releases को stable नाम देते हैं, CI से deployment trigger करवाते हैं, one-command rollback (`git checkout v1.3.2`) देते हैं और Docker images को source से जोड़ते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Make sure the commit to release is on main and CI is green.
Step 2 → Create annotated tag:  git tag -a v1.4.0 -m "Release 1.4.0"
Step 3 → Push it (tags are NOT pushed by default):  git push origin v1.4.0
Step 4 → GitHub Actions on: push: tags: ['v*'] builds image :1.4.0 and deploys.
Step 5 → (Optional) create a GitHub Release with notes: gh release create v1.4.0 --generate-notes
Step 6 → Rollback = redeploy previous tag (v1.3.2).
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → पक्का करो कि release वाला commit main पर है और CI green है।
Step 2 → Annotated tag बनाओ: `git tag -a v1.4.0 -m "Release 1.4.0"`
Step 3 → Push करो (tags default में push नहीं होते): `git push origin v1.4.0`
Step 4 → GitHub Actions `on: push: tags: ['v*']` पर image :1.4.0 बनाकर deploy करता है।
Step 5 → (Optional) notes के साथ GitHub Release: `gh release create v1.4.0 --generate-notes`
Step 6 → Rollback = पिछला tag (v1.3.2) redeploy।

---

## 🟡 Real World Example
Your FastAPI service runs on the VPS as `myorg/ml-api:1.4.0`. A bug appears. Because the image tag equals the Git tag, you run `git show v1.4.0` to see the exact code, reproduce locally, fix, tag `v1.4.1`, and deploy. If it gets worse, you point docker compose back to `1.3.2` within a minute.

## 🟡 Real Example Hindi mein
आपकी FastAPI service VPS पर `myorg/ml-api:1.4.0` के रूप में चलती है। Bug आता है। Image tag और Git tag एक जैसे होने से `git show v1.4.0` से exact code दिखता है, local में reproduce करके fix करते हैं, `v1.4.1` tag करते हैं और deploy। बात बिगड़े तो docker compose को एक मिनट में `1.3.2` पर वापस ले जाते हैं।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# tags-basic.sh - everyday tag commands
set -euo pipefail                                          # strict mode

git tag                                                    # list all tags
git tag -l "v1.*"                                          # list tags matching a pattern
git tag -a v1.4.0 -m "Release 1.4.0"                       # annotated tag on current commit (recommended for releases)
git tag v1.4.0-rc.1                                        # lightweight tag (just a pointer, no metadata)
git show v1.4.0                                            # show tag info and the commit
git push origin v1.4.0                                     # push ONE tag
git push origin --tags                                     # push ALL local tags (use carefully)
git tag -a v1.3.9 9fceb02 -m "Backfill tag"                # tag an older commit by hash (replace hash)
git tag -d v1.4.0-rc.1                                     # delete tag locally
git push origin --delete v1.4.0-rc.1                       # delete tag on remote
git checkout v1.3.2                                        # inspect old release (detached HEAD)
git describe --tags                                        # "v1.4.0-3-gabc123" = 3 commits after v1.4.0
```

## 💻 Code / Config Example — Advanced

Tag-triggered release: build Docker image with the version from the tag, push to GHCR, create a GitHub Release. Example action versions; update them.

```yaml
# .github/workflows/release.yml
name: release                                              # workflow name
on:
  push:
    tags: ['v*.*.*']                                       # run only for tags like v1.4.0
permissions:
  contents: write                                          # needed to create the GitHub Release
  packages: write                                          # needed to push to GHCR
jobs:
  release:
    runs-on: ubuntu-latest                                 # runner
    steps:
      - uses: actions/checkout@v4                          # fetch code at the tag
      - name: Compute version
        id: v                                              # step id so later steps can read outputs
        run: echo "version=${GITHUB_REF_NAME#v}" >> "$GITHUB_OUTPUT"   # v1.4.0 -> 1.4.0
      - uses: docker/login-action@v3                       # log in to GHCR
        with:
          registry: ghcr.io                                # registry host
          username: ${{ github.actor }}                    # workflow user
          password: ${{ secrets.GITHUB_TOKEN }}            # built-in token
      - uses: docker/build-push-action@v6                  # build and push
        with:
          context: .                                       # build context
          push: true                                       # push result
          tags: |
            ghcr.io/${{ github.repository }}:${{ steps.v.outputs.version }}
            ghcr.io/${{ github.repository }}:latest
      - name: Create GitHub Release
        env:
          GH_TOKEN: ${{ github.token }}                    # gh CLI auth
        run: gh release create "$GITHUB_REF_NAME" --generate-notes   # auto notes from merged PRs
```

---

## 🟠 My Stack Integration
- **Node.js:** `npm version minor` bumps `package.json`, commits and creates tag `v1.5.0` in one step (`npm version` also supports `--no-git-tag-version`).
- **FastAPI:** keep version in `pyproject.toml`; CI verifies it matches the tag.
- **React:** inject the tag as build-time `VITE_APP_VERSION` and show it in the footer for support.
- **VPS:** deploy script takes `VERSION` and runs `docker compose pull && docker compose up -d`.

```yaml
# docker-compose.yml - pin the deployed version, deploy = change this tag
services:
  api:
    image: ghcr.io/myorg/api:${APP_VERSION:?set APP_VERSION}   # fails fast if APP_VERSION is not set
    restart: unless-stopped                                    # auto restart
    ports:
      - "127.0.0.1:3000:3000"                                  # only Nginx (same host) can reach it
```
Deploy with: `APP_VERSION=1.4.0 docker compose up -d`.

**Security:** protect `v*` tags (rulesets/tag protection) so only maintainers can create them, because tags can trigger production deploys. Use signed tags (`git tag -s`) for supply-chain trust. Never reuse or move a published tag.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `git push origin <tag>`.
✅ Correct: Tags must be pushed explicitly.

❌ Mistake 2: Moving or force-updating a tag after release.
✅ Correct: Tags are immutable by convention; publish a new patch version.

❌ Mistake 3: Using lightweight tags for releases.
✅ Correct: Use annotated (`-a`) for author, date, message.

❌ Mistake 4: Deploying `latest`.
✅ Correct: Deploy exact version tags.

---

## 🧠 Tricky Interview Question
You deleted tag `v1.4.0` locally and recreated it on another commit, then pushed. Colleagues still see the old commit. Why?

**Answer:** `git fetch` does not overwrite existing local tags by default, and the push of a changed tag is rejected without `--force`. Moving tags breaks the immutability promise, so teammates, caches and registries disagree. Correct fix: leave `v1.4.0` alone and release `v1.4.1`.

---

## ⚫ Interview Questions + Answers

Q1: Tag vs branch?
A1: A branch moves as you commit; a tag stays on one commit.

Q2: Lightweight vs annotated tag?
A2: Lightweight is just a ref; annotated is a full object with tagger, date, message, optionally signed.

Q3: How do you see which tag a commit belongs to?
A3: `git describe --tags <commit>` or `git tag --contains <commit>`.

Q4: How to list tags sorted by version?
A4: `git tag --sort=-v:refname`.

Q5: How to build a release from a tag?
A5: CI on `push: tags: ['v*']`, using `GITHUB_REF_NAME` as the version.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Marking releases, deploying versions, enabling rollbacks.

❌ Avoid when:
- Tagging every commit (noise); use CI run numbers or SHA tags for non-release builds.

---

## 📊 Visual Diagram

```
 main:  o---o---o---o---o---o--->
                |           |
             v1.3.2       v1.4.0  (tags stay fixed)

 git push origin v1.4.0 --> CI --> image :1.4.0 --> VPS (docker compose up -d)
 rollback: APP_VERSION=1.3.2 docker compose up -d
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tag | Fixed label on a commit | commit पर fixed label |
| Annotated tag | Tag with metadata | metadata वाला tag |
| Lightweight tag | Plain pointer | सादा pointer |
| Release | Published version | publish हुआ version |
| Detached HEAD | HEAD on a commit, not branch | HEAD commit पर, branch पर नहीं |

---

## ⚡ 3-Line Summary
English: A tag permanently names a commit, usually a release.
Push tags explicitly and let CI build and deploy from them.
Never move a published tag; release a new version instead.
Hindi: Tag एक commit को हमेशा के लिए नाम देता है, आमतौर पर release।
Tags को explicitly push करो और CI से build व deploy करवाओ।
Published tag कभी मत बदलो; नया version release करो।

---

## ➡️ Next Topic
**24. Semantic Versioning (SemVer)** - how to choose the numbers in tags.

---
