# 359. Release Notes Generation
# हिंदी में: Release Notes बनाना (Automation)

---

## 🔵 Simple Definition (English)
Release notes are a human-readable summary of what changed in a version: new features, fixes, breaking changes. Release notes generation means the pipeline builds this text automatically from merged pull requests or commits and attaches it to a GitHub Release when you push a version tag.

## 🔵 सरल परिभाषा (Hindi)
Release notes किसी version में क्या बदला उसका आसान सारांश हैं: नए features, fixes, breaking changes। Release notes generation का मतलब है कि pipeline merged pull requests या commits से यह text अपने-आप बनाता है और version tag push करने पर GitHub Release में जोड़ देता है।

---

## 🔴 Problem it Solves
Writing release notes by hand is slow, so people skip it or forget changes. Users and QA do not know what to test; support does not know what changed; other teams are surprised by breaking changes. Automation makes notes consistent, complete and available the minute you release.

## 🔴 यह क्यों बना? (Hindi)
Release notes हाथ से लिखना धीमा है, इसलिए लोग छोड़ देते हैं या बदलाव भूल जाते हैं। Users और QA को पता नहीं होता क्या test करना है; support को नहीं पता क्या बदला; दूसरी teams breaking changes से चौंक जाती हैं। Automation notes को consistent, पूरे और release के उसी मिनट उपलब्ध बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developers merge PRs with labels (feature, bug, breaking) or conventional commits
Step 2 → You push a tag like v1.4.0 (or a release is published)
Step 3 → The workflow runs on: push: tags: ['v*']
Step 4 → Notes are generated: GitHub's built-in generator, or a tool grouping by label
Step 5 → A GitHub Release is created with the notes and optional artifacts
Step 6 → Notification posts the link to Slack; docker image is tagged with the version
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Developers labels (feature, bug, breaking) या conventional commits के साथ PRs merge करते हैं
Step 2 → आप v1.4.0 जैसा tag push करते हैं (या release publish होता है)
Step 3 → Workflow चलता है: push: tags: ['v*']
Step 4 → Notes बनते हैं: GitHub का built-in generator, या label से group करने वाला tool
Step 5 → Notes (और optional artifacts) के साथ GitHub Release बनता है
Step 6 → Notification Slack में link भेजती है; docker image version से tag होती है
```

---

## 🟡 Real World Example
A mobile backend team ships weekly. Every PR must carry one label. On Friday the lead pushes `v2.7.0`. The workflow publishes a release with sections "Features", "Bug fixes", "Breaking changes", each listing PR titles and authors. QA uses the list as a test checklist; support pastes the "What is new" section to customers; the CTO sees at a glance what went to production. Total effort: one command, `git tag v2.7.0 && git push origin v2.7.0`.

## 🟡 Real Example Hindi mein
एक mobile backend team हर हफ्ते release करती है। हर PR पर एक label ज़रूरी है। शुक्रवार को lead `v2.7.0` push करता है। Workflow "Features", "Bug fixes", "Breaking changes" sections के साथ release publish करता है जिनमें PR titles और authors होते हैं। QA इसे test checklist बनाती है; support "What is new" भाग customers को भेजता है; CTO एक नज़र में देख लेता है क्या production गया। मेहनत: एक command, `git tag v2.7.0 && git push origin v2.7.0`।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/release.yml - simplest: GitHub generates the notes
name: Release
on:
  push:
    tags: ['v*']                         # runs when a tag like v1.2.3 is pushed
permissions:
  contents: write                        # needed to create a release
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4        # get the code
      - name: Create GitHub Release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}   # gh CLI authentication
        run: |
          # --generate-notes asks GitHub to build notes from merged PRs since last tag
          gh release create "${GITHUB_REF_NAME}" --title "${GITHUB_REF_NAME}" --generate-notes
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/release.yml - tells GitHub how to group auto-generated notes by PR label
changelog:
  exclude:
    labels:
      - skip-changelog                   # PRs with this label are hidden
    authors:
      - dependabot                       # hide bot PRs (name may need [bot] suffix in your org)
  categories:
    - title: "Breaking changes"
      labels: ["breaking"]
    - title: "Features"
      labels: ["feature", "enhancement"]
    - title: "Bug fixes"
      labels: ["bug", "fix"]
    - title: "Security"
      labels: ["security"]
    - title: "Other changes"
      labels: ["*"]                      # everything else
```

```yaml
# .github/workflows/release-advanced.yml
name: Release Advanced
on:
  push:
    tags: ['v[0-9]+.[0-9]+.[0-9]+*']     # semver tags, e.g. v1.4.0 or v1.4.0-rc1
permissions:
  contents: write                        # create releases
  packages: write                        # push versioned images
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0                 # full history so tools can see previous tags
      - name: Validate tag is on main
        run: |
          # refuse releases from commits that are not on main
          git fetch origin main
          git merge-base --is-ancestor "$GITHUB_SHA" origin/main || { echo "Tag not on main"; exit 1; }
      - name: Detect pre-release
        id: pre
        run: |
          # tags containing a hyphen (v1.4.0-rc1) are marked as pre-release
          if [[ "$GITHUB_REF_NAME" == *-* ]]; then echo "flag=--prerelease" >> "$GITHUB_OUTPUT"; else echo "flag=" >> "$GITHUB_OUTPUT"; fi
      - name: Create release with generated notes
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh release create "$GITHUB_REF_NAME" \
            --title "$GITHUB_REF_NAME" \
            --generate-notes \
            ${{ steps.pre.outputs.flag }}
      - uses: docker/login-action@v3     # login to GHCR
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5   # push image tagged with the version
        with:
          context: .
          push: true
          tags: ghcr.io/myorg/myapp/api:${{ github.ref_name }}
```

```bash
# release by hand from your laptop (what triggers the workflow)
git checkout main && git pull                 # be on latest main
git tag -a v1.4.0 -m "Release 1.4.0"          # annotated tag
git push origin v1.4.0                        # tag push triggers the workflow
```

---

## 🟠 My Stack Integration
- One tag per service in a monorepo: `api-v1.4.0`, `web-v2.1.0` with matching `on.push.tags` patterns.
- The deploy workflow can listen to `release: published` so "release" equals "deploy to production" for Node, FastAPI and React.
- FastAPI exposes the version (`/api/version`) from the tag via a build arg so support can match bug reports to release notes.
- Nginx serves the React build of the same tag; include the tag in a `/version.txt` file.

```dockerfile
# pass the release tag into the image so the app can report it
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION
```

Security: the workflow gets `contents: write` only; use least privilege. Restrict tag creation with a tag ruleset so only maintainers can create `v*` tags, otherwise anyone with push access can trigger a production release.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using raw commit messages like "fix", "wip", "test".
✅ Correct: Use meaningful PR titles or conventional commits; squash-merge with clean titles.

❌ Mistake 2: Shallow clone, so tools cannot find the previous tag.
✅ Correct: `fetch-depth: 0` when your tool compares tags.

❌ Mistake 3: Forgetting `permissions: contents: write`.
✅ Correct: Grant it, otherwise the release step gets 403.

❌ Mistake 4: Hiding breaking changes among others.
✅ Correct: Create a dedicated "Breaking changes" category with a required label.

❌ Mistake 5: Moving or reusing a tag.
✅ Correct: Tags are immutable by convention; publish a new patch version instead.

---

## 🧠 Tricky Interview Question
You pushed tag `v1.4.0` but the workflow did not run. Why?

Answer: Common reasons: the workflow file did not exist on the commit the tag points to (the workflow definition is read from the tagged commit), the tag pattern does not match (`v*` vs `1.4.0`), the tag was created by a workflow using `GITHUB_TOKEN` (events from that token do not trigger new workflows, use a PAT or GitHub App), or Actions is disabled for the repo.

---

## ⚫ Interview Questions + Answers

Q1: Difference between a tag and a release?
A1: A tag is a Git pointer to a commit; a GitHub Release is a page built on a tag with notes and assets.

Q2: How does `--generate-notes` work?
A2: GitHub lists merged PRs and contributors between the previous release tag and the new one, grouped using `.github/release.yml` if present.

Q3: Why semantic versioning?
A3: MAJOR.MINOR.PATCH signals impact: breaking, feature, fix, so consumers know how risky an upgrade is.

Q4: How do you release only when tests pass?
A4: Make the release job `needs:` a test job, or protect `main` and only tag commits whose CI is green.

Q5: What is a pre-release?
A5: A release marked as not production-ready (rc, beta), shown differently and not counted as "latest".

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple people ship changes and others need to know what changed.
- You publish libraries, APIs or versioned apps.

❌ Avoid when:
- A solo project that deploys continuously and nobody reads notes (still tag major points).
- PR titles are meaningless; fix the habit first.

---

## 📊 Visual Diagram
```
 PRs merged (labels: feature / bug / breaking)
            |
   git tag v1.4.0 && git push origin v1.4.0
            |
            v
   Workflow: on push tags v*
            |
   gh release create --generate-notes
            |
            +--> GitHub Release page: Features / Bug fixes / Breaking
            +--> Docker image :v1.4.0
            +--> Slack message with link
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Release | Published version with notes | notes सहित प्रकाशित version |
| Tag | Named pointer to a commit | commit का नामित pointer |
| SemVer | MAJOR.MINOR.PATCH numbering | MAJOR.MINOR.PATCH संख्या पद्धति |
| Pre-release | Not final version | अंतिम नहीं, test version |
| Squash merge | Merge as one commit | एक commit के रूप में merge |

---

## ⚡ 3-Line Summary
English: Push a version tag and let the workflow create a GitHub Release with auto-generated notes.
Use PR labels and `.github/release.yml` to group changes, with a clear breaking-changes section.
Protect who can create tags and give the job minimal permissions.
Hindi: Version tag push करो और workflow auto-generated notes के साथ GitHub Release बनाए।
PR labels और `.github/release.yml` से बदलाव group करो, breaking changes का साफ section रखो।
Tag कौन बनाए यह सीमित करो और job को न्यूनतम permissions दो।

---

## ➡️ Next Topic
**360. Changelog Automation** — maintaining a CHANGELOG.md and version numbers automatically from commits.
