# 360. Changelog Automation
# हिंदी में: Changelog Automation

---

## 🔵 Simple Definition (English)
A changelog is a file (`CHANGELOG.md`) that records notable changes per version. Changelog automation derives the file, and the next version number, from commit messages written in the Conventional Commits style (`feat:`, `fix:`, `feat!:`), using tools like release-please, semantic-release, or changesets.

## 🔵 सरल परिभाषा (Hindi)
Changelog एक file (`CHANGELOG.md`) है जो हर version के ज़रूरी बदलाव दर्ज करती है। Changelog automation इस file और अगले version number को commit messages से निकालता है, जो Conventional Commits style (`feat:`, `fix:`, `feat!:`) में लिखे हों, release-please, semantic-release या changesets जैसे tools से।

---

## 🔴 Problem it Solves
Manual changelogs go stale. Version numbers are picked by guesswork ("is this 1.4.1 or 1.5.0?"), and breaking changes slip into patch releases. Automation reads the commit history and decides: `fix` bumps PATCH, `feat` bumps MINOR, a breaking change bumps MAJOR. The result is consistent versions and an always-current changelog.

## 🔴 यह क्यों बना? (Hindi)
हाथ से लिखे changelog पुराने पड़ जाते हैं। Version number अंदाज़े से चुना जाता है ("यह 1.4.1 है या 1.5.0?") और breaking changes patch release में छिप जाते हैं। Automation commit history पढ़कर तय करता है: `fix` से PATCH, `feat` से MINOR, breaking change से MAJOR बढ़ता है। नतीजा: consistent versions और हमेशा ताज़ा changelog।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Team writes commits/PR titles: feat(api): add refunds, fix: null email
Step 2 → A tool scans commits since the last release tag
Step 3 → It decides the next version (semver) from the types
Step 4 → It opens/updates a "Release PR" with the CHANGELOG.md diff and version bump
Step 5 → A human reviews and merges that PR
Step 6 → Merge creates the tag and GitHub Release, which triggers deploy
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Team commits/PR titles लिखती है: feat(api): add refunds, fix: null email
Step 2 → Tool आखिरी release tag के बाद के commits scan करता है
Step 3 → Types से अगला version (semver) तय करता है
Step 4 → CHANGELOG.md diff और version bump के साथ "Release PR" खोलता/update करता है
Step 5 → इंसान उस PR को review करके merge करता है
Step 6 → Merge tag और GitHub Release बनाता है, जो deploy trigger करता है
```

---

## 🟡 Real World Example
A payments company has 15 services. Each service uses release-please. Developers write `feat:` and `fix:` titles when squash-merging. A bot keeps one open PR per service named "chore: release api 3.2.0" showing the changelog. On Monday the tech lead merges the PRs, tags are created automatically, and the deploy pipeline ships exactly those versions. No one edits CHANGELOG.md by hand, and auditors can see precisely what shipped in each release.

## 🟡 Real Example Hindi mein
एक payments company के 15 services हैं। हर service release-please इस्तेमाल करती है। Developers squash-merge करते समय `feat:` और `fix:` titles लिखते हैं। एक bot हर service के लिए एक खुला PR रखता है "chore: release api 3.2.0" जिसमें changelog दिखता है। सोमवार को tech lead PRs merge करता है, tags अपने-आप बनते हैं और deploy pipeline ठीक वही versions भेजती है। CHANGELOG.md हाथ से कोई नहीं बदलता, और auditors देख सकते हैं कि हर release में क्या गया।

---

## 💻 Code / Config Example — Basic

```text
# Conventional Commit format
<type>(<optional scope>): <short description>

# Examples
feat(api): add refund endpoint          -> MINOR bump (1.4.0 -> 1.5.0)
fix(web): correct cart total rounding   -> PATCH bump (1.4.0 -> 1.4.1)
feat(api)!: remove v1 orders endpoint   -> MAJOR bump (1.4.0 -> 2.0.0)
docs: update README                     -> no release
chore: bump dependencies                -> no release
```

```markdown
<!-- CHANGELOG.md - Keep a Changelog style (what automation produces/maintains) -->
# Changelog

## [1.5.0] - 2026-11-05
### Features
- api: add refund endpoint (#212)

### Bug Fixes
- web: correct cart total rounding (#215)

## [1.4.0] - 2026-10-20
### Features
- api: order history pagination (#201)
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/release-please.yml - release-please keeps a Release PR up to date
name: release-please
on:
  push:
    branches: [main]                         # run after every merge to main
permissions:
  contents: write                            # create tags/releases
  pull-requests: write                       # open and update the Release PR
jobs:
  release-please:
    runs-on: ubuntu-latest
    outputs:
      released: ${{ steps.rp.outputs.release_created }}   # true when a release was just made
      tag: ${{ steps.rp.outputs.tag_name }}               # e.g. v1.5.0
    steps:
      - id: rp
        uses: googleapis/release-please-action@v4          # example major version, check docs
        with:
          release-type: node                               # node, python, simple ... per project
          # for v4 you may use config files instead (release-please-config.json)
  deploy:
    needs: release-please
    if: needs.release-please.outputs.released == 'true'    # deploy only on an actual release
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - run: echo "Deploying ${{ needs.release-please.outputs.tag }}"   # call real deploy here
```

```json
// release-please-config.json - monorepo example (api = Python, web = Node)
{
  "packages": {
    "services/api": { "release-type": "python", "component": "api" },
    "apps/web":     { "release-type": "node",   "component": "web" }
  },
  "changelog-sections": [
    { "type": "feat", "section": "Features" },
    { "type": "fix", "section": "Bug Fixes" },
    { "type": "perf", "section": "Performance" }
  ]
}
```

```json
// .release-please-manifest.json - current versions release-please tracks
{
  "services/api": "1.4.0",
  "apps/web": "2.1.0"
}
```

```yaml
# .github/workflows/pr-title.yml - enforce Conventional Commit PR titles (squash merge uses the title)
name: PR title
on:
  pull_request:
    types: [opened, edited, synchronize, reopened]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Validate title
        env:
          TITLE: ${{ github.event.pull_request.title }}   # via env to avoid shell injection
        run: |
          # regex of allowed types, optional scope, optional "!" for breaking
          if ! [[ "$TITLE" =~ ^(feat|fix|docs|chore|refactor|perf|test|ci|build)(\([a-z0-9._-]+\))?!?:\ .+ ]]; then
            echo "PR title must follow Conventional Commits, e.g. 'feat(api): add refunds'"
            exit 1
          fi
```

Config and workflow YAML were parsed for syntax; the release-please inputs and option names are version dependent, so confirm against the current release-please docs before use.

---

## 🟠 My Stack Integration
- Node.js/React: `release-type: node` bumps `package.json`; alternatives are semantic-release and changesets (popular in npm monorepos).
- FastAPI: `release-type: python` updates `pyproject.toml`/`setup.py`; expose the version at `/api/version`.
- The merged Release PR creates a tag; your deploy workflow (349/350) listens to `release: published` or to the `released` output above.
- Enforce squash-merge on GitHub so the PR title becomes the commit message.

```bash
# local preview of the commit types since the last tag (quick sanity check)
git log "$(git describe --tags --abbrev=0)"..HEAD --pretty=format:'%s' | sort
```

Security: the release bot needs `contents: write` and `pull-requests: write`; keep it scoped and do not use a personal token unless required for triggering other workflows. Protect `main` so only reviewed Release PRs publish versions.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Writing commits like "update" or "fixes".
✅ Correct: Use `type(scope): description`; enforce with a PR-title check.

❌ Mistake 2: Merge commits with free-form messages.
✅ Correct: Use squash merge with the PR title as the message.

❌ Mistake 3: Hiding breaking changes without `!` or `BREAKING CHANGE:` footer.
✅ Correct: Mark them so MAJOR bumps happen.

❌ Mistake 4: Editing CHANGELOG.md by hand and fighting the bot.
✅ Correct: Let the tool own the file; edit PR titles instead.

❌ Mistake 5: Releasing from non-main branches by accident.
✅ Correct: Trigger only on `main` and use protected branches.

---

## 🧠 Tricky Interview Question
A developer pushes `fix: patch login` that actually changes an API response format, breaking mobile clients. The tool released a PATCH version. Whose fault is it, and how do you prevent it?

Answer: Automation trusts the commit message, so it is a process failure: the commit should have been `fix!:` or carried a `BREAKING CHANGE:` footer, marking a MAJOR bump. Prevent it with PR review that checks the type, contract tests or OpenAPI diff checks in CI that fail on breaking changes, and API versioning for external clients.

---

## ⚫ Interview Questions + Answers

Q1: What are Conventional Commits?
A1: A convention `type(scope): description` with `!` or a `BREAKING CHANGE:` footer for breaking changes, readable by humans and tools.

Q2: release-please vs semantic-release?
A2: release-please opens a reviewable Release PR and releases when merged; semantic-release releases directly on every qualifying push with no human gate.

Q3: How is the next version chosen?
A3: Highest impact since the last release wins: breaking => MAJOR, any feat => MINOR, else fix/perf => PATCH.

Q4: What is the benefit of a Release PR?
A4: A human checkpoint with the changelog diff visible before anything is published.

Q5: What about monorepos?
A5: Configure per-package paths and components, each with its own version, tag and changelog (release-please manifest or changesets).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several developers contribute and versions matter (libraries, APIs, mobile backends).
- You want audit-friendly, consistent release history.

❌ Avoid when:
- The team will not follow commit conventions and there is no enforcement.
- A tiny internal service that deploys by SHA and has no consumers of versions.

---

## 📊 Visual Diagram
```
 feat: ...   fix: ...   feat!: ...        (merged to main via squash)
      \          |          /
       v         v         v
   [ release-please scans commits since v1.4.0 ]
                 |
        next version = 2.0.0 (breaking found)
                 |
   Release PR: CHANGELOG.md + package.json bump   <-- human reviews/merges
                 |
        tag v2.0.0 + GitHub Release  ---> deploy workflow
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Changelog | History of notable changes | महत्वपूर्ण बदलावों का इतिहास |
| Conventional Commits | Standard commit message format | commit message का मानक रूप |
| SemVer bump | Increase MAJOR/MINOR/PATCH | version संख्या बढ़ाना |
| Release PR | Bot PR that prepares a release | release तैयार करने वाला bot PR |
| Monorepo | Many packages in one repo | एक repo में कई packages |

---

## ⚡ 3-Line Summary
English: Write Conventional Commits and let a tool compute the version and CHANGELOG.md.
A Release PR gives a human gate; merging it creates the tag and triggers deploy.
Enforce PR titles and mark breaking changes properly.
Hindi: Conventional Commits लिखो और tool को version व CHANGELOG.md निकालने दो।
Release PR इंसानी gate देता है; merge tag बनाकर deploy trigger करता है।
PR titles enforce करो और breaking changes सही से mark करो।

---

## ➡️ Next Topic
**361. Complete Node.js Pipeline (Test → Build → Push → Deploy)** — putting everything together in one real pipeline.
