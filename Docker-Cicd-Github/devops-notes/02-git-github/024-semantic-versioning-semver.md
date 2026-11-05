# 24. Semantic Versioning (SemVer)
# हिंदी में: Semantic Versioning (SemVer)

---

## 🔵 Simple Definition (English)
**Semantic Versioning** uses version numbers `MAJOR.MINOR.PATCH` (for example `2.5.1`). Increase **MAJOR** for incompatible (breaking) changes, **MINOR** for new backward-compatible features, and **PATCH** for backward-compatible bug fixes. Pre-release (`1.0.0-rc.1`) and build metadata (`1.0.0+build.5`) are optional suffixes.

## 🔵 सरल परिभाषा (Hindi)
**Semantic Versioning** version numbers `MAJOR.MINOR.PATCH` में लिखता है (जैसे `2.5.1`)। **MAJOR** बढ़ाओ जब पुराने code को तोड़ने वाला बदलाव हो, **MINOR** जब नया backward-compatible feature जुड़े, और **PATCH** जब backward-compatible bug fix हो। Pre-release (`1.0.0-rc.1`) और build metadata (`1.0.0+build.5`) optional suffixes हैं।

---

## 🔴 Problem it Solves
With random versions ("v2-final", "2024-update"), users cannot know if upgrading will break their app. Dependency managers (npm, pip) cannot auto-update safely. SemVer is a contract: a patch upgrade should be safe, a minor adds features without breaking, a major tells you to read the migration guide.

## 🔴 यह क्यों बना? (Hindi)
Random versions ("v2-final", "2024-update") से users नहीं जान पाते कि upgrade करने पर app टूटेगा या नहीं। Dependency managers (npm, pip) सुरक्षित auto-update नहीं कर पाते। SemVer एक contract है: patch upgrade safe होना चाहिए, minor बिना तोड़े features जोड़ता है, major का मतलब migration guide पढ़ो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Start at 0.1.0 (initial development) or 1.0.0 (first stable public API).
Step 2 → Bug fix, no API change           -> 1.4.2 -> 1.4.3  (PATCH)
Step 3 → New feature, old API still works -> 1.4.3 -> 1.5.0  (MINOR, PATCH resets to 0)
Step 4 → Breaking change                  -> 1.5.0 -> 2.0.0  (MAJOR, MINOR and PATCH reset)
Step 5 → Pre-releases sort BEFORE the release: 2.0.0-alpha.1 < 2.0.0-rc.1 < 2.0.0
Step 6 → Consumers pin ranges: npm ^1.4.2 (>=1.4.2 <2.0.0), ~1.4.2 (>=1.4.2 <1.5.0).
```

Rules: once released, a version must never change. Build metadata (`+abc`) is ignored for precedence. In `0.y.z`, anything may change at any time.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → शुरुआत 0.1.0 (initial development) या 1.0.0 (पहला stable public API) से।
Step 2 → Bug fix, API वही -> 1.4.2 -> 1.4.3 (PATCH)।
Step 3 → नया feature, पुराना API चलता है -> 1.4.3 -> 1.5.0 (MINOR, PATCH 0 हो जाता है)।
Step 4 → Breaking change -> 1.5.0 -> 2.0.0 (MAJOR, MINOR और PATCH reset)।
Step 5 → Pre-release, release से पहले आते हैं: 2.0.0-alpha.1 < 2.0.0-rc.1 < 2.0.0।
Step 6 → Consumers ranges pin करते हैं: npm ^1.4.2 (>=1.4.2 <2.0.0), ~1.4.2 (>=1.4.2 <1.5.0)।

नियम: release होने के बाद कोई version बदला नहीं जा सकता। `0.y.z` में कभी भी कुछ भी बदल सकता है।

---

## 🟡 Real World Example
Express 4.x -> 5.0.0 was a MAJOR bump because behaviour changed in ways that could break apps, so teams read the migration guide before upgrading. A security fix such as 4.18.1 -> 4.18.2 is a PATCH that you can usually take immediately. Your own REST API: adding a new optional `phone` field is MINOR; removing `/v1/users` is MAJOR.

## 🟡 Real Example Hindi mein
Express 4.x -> 5.0.0 MAJOR bump था क्योंकि behaviour ऐसे बदला जो apps तोड़ सकता है, इसलिए teams upgrade से पहले migration guide पढ़ती हैं। Security fix जैसे 4.18.1 -> 4.18.2 PATCH है जिसे आमतौर पर तुरंत ले सकते हैं। आपका अपना REST API: नया optional `phone` field MINOR है; `/v1/users` हटाना MAJOR है।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# semver-basic.sh - bump versions with npm and inspect them
set -euo pipefail                                         # strict mode

npm version patch -m "chore(release): %s"                 # 1.4.2 -> 1.4.3, commit + tag v1.4.3 (needs clean git tree)
npm version minor -m "chore(release): %s"                 # 1.4.3 -> 1.5.0
npm version major -m "chore(release): %s"                 # 1.5.0 -> 2.0.0
npm version prerelease --preid=rc                         # 2.0.0 -> 2.0.1-rc.0 (increments patch then adds rc.0)
git push origin main --follow-tags                        # push commit and its annotated tags

# Check what range a dependency allows (npm semver rules)
npx --yes semver -r "^1.4.2" 1.9.0 2.0.0                  # prints versions that satisfy the range (1.9.0 only)
```

## 💻 Code / Config Example — Advanced

A small Node.js script that decides the next version from Conventional Commit messages since the last tag (the idea behind semantic-release), plus a CI check that the tag matches `package.json`.

```javascript
// next-version.js - decide bump from commit messages (simplified, node >= 18, no dependencies)
const { execSync } = require('child_process');            // run git commands
const pkg = require('./package.json');                    // read current version

// last tag, or empty string if none exists yet
let last = '';
try { last = execSync('git describe --tags --abbrev=0', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim(); } catch (_) {}

const range = last ? `${last}..HEAD` : 'HEAD';            // commits since last tag
const log = execSync(`git log ${range} --pretty=format:%s%n%b`).toString();   // subjects + bodies

let bump = 'patch';                                       // default smallest bump
if (/^feat(\(.+\))?!?:/m.test(log)) bump = 'minor';       // any feat -> minor
if (/BREAKING CHANGE:|^\w+(\(.+\))?!:/m.test(log)) bump = 'major';   // breaking -> major wins

const [maj, min, pat] = pkg.version.split('.').map(Number);   // split current version
const next =
  bump === 'major' ? `${maj + 1}.0.0` :                   // major: reset minor and patch
  bump === 'minor' ? `${maj}.${min + 1}.0` :              // minor: reset patch
  `${maj}.${min}.${pat + 1}`;                             // patch: +1

console.log(next);                                        // print next version for CI to use
```

```yaml
# .github/workflows/verify-tag.yml - ensure tag == package.json version
name: verify-tag                                          # workflow name
on:
  push:
    tags: ['v*.*.*']                                      # only on version tags
jobs:
  check:
    runs-on: ubuntu-latest                                # runner
    steps:
      - uses: actions/checkout@v4                         # fetch code
      - name: Compare versions
        run: |
          TAG="${GITHUB_REF_NAME#v}"                      # strip leading v from tag
          PKG=$(node -p "require('./package.json').version")   # read version from package.json
          if [ "$TAG" != "$PKG" ]; then                   # mismatch means someone forgot to bump
            echo "::error::Tag $TAG != package.json $PKG" # annotate error
            exit 1                                        # fail
          fi
          echo "Version $TAG verified"                    # success message
```

---

## 🟠 My Stack Integration
- **Node.js:** `package.json` version + `npm version`; lockfile pins dependency versions exactly.
- **FastAPI/Python:** `pyproject.toml` uses PEP 440 (e.g., `1.5.0rc1`), which differs slightly from SemVer pre-release spelling.
- **Docker:** tag images `1.5.0`, `1.5`, `1` (multi-tag) so consumers choose their risk level; avoid relying on `latest`.
- **API versioning:** expose major in the URL (`/v2/...`); keep v1 for a deprecation period.

```yaml
# docker/metadata-action generates semver tags from a git tag v1.5.0 (example config)
- uses: docker/metadata-action@v5          # builds tag/label lists (example version)
  id: meta                                 # id to read outputs
  with:
    images: ghcr.io/myorg/api              # image name
    tags: |
      type=semver,pattern={{version}}
      type=semver,pattern={{major}}.{{minor}}
      type=semver,pattern={{major}}
```

**Security:** use `npm ci` and lockfiles so a malicious new PATCH of a dependency is not pulled silently; Dependabot/Renovate PRs let you review upgrades. Fixing a vulnerability should still be a PATCH (or higher) release with an advisory.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Bumping MINOR for a breaking change.
✅ Correct: Breaking = MAJOR.

❌ Mistake 2: Re-publishing the same version with different content.
✅ Correct: Versions are immutable; release a new one.

❌ Mistake 3: Staying on `0.x` forever.
✅ Correct: Release 1.0.0 when the public API is stable.

❌ Mistake 4: Assuming `^0.2.3` allows 0.3.0.
✅ Correct: For 0.x, caret allows only patch bumps within the same minor (`^0.2.3` = >=0.2.3 <0.3.0).

---

## 🧠 Tricky Interview Question
Which is newer: `1.0.0-rc.1` or `1.0.0`? And `1.0.0+build.7` vs `1.0.0+build.9`?

**Answer:** `1.0.0` is newer; pre-releases have lower precedence than the release. The two build-metadata versions have equal precedence because build metadata is ignored when comparing.

---

## ⚫ Interview Questions + Answers

Q1: What does each number mean?
A1: MAJOR breaking, MINOR new compatible features, PATCH compatible fixes.

Q2: npm `^` vs `~`?
A2: `^1.2.3` allows >=1.2.3 <2.0.0; `~1.2.3` allows >=1.2.3 <1.3.0.

Q3: When do you go to 1.0.0?
A3: When the software is used in production and you commit to a stable public API.

Q4: How does SemVer relate to Conventional Commits?
A4: feat -> MINOR, fix -> PATCH, BREAKING CHANGE -> MAJOR, so tools can compute versions.

Q5: Is SemVer enough for APIs?
A5: It signals compatibility, but you must still keep a deprecation policy and changelog.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Libraries, APIs, Docker images consumed by others.

❌ Avoid when:
- Continuously deployed internal web apps where CalVer (2026.11.04) or build numbers are more natural.

---

## 📊 Visual Diagram

```
        MAJOR . MINOR . PATCH
          2   .   5   .   1
          |       |       |
 breaking-+       |       +-- bug fix only
 changes          +-- new feature, compatible

 1.4.3 --feat--> 1.5.0 --BREAKING--> 2.0.0 --fix--> 2.0.1
 order: 2.0.0-alpha.1 < 2.0.0-rc.1 < 2.0.0
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| MAJOR | Breaking change number | breaking बदलाव का number |
| MINOR | Compatible feature number | compatible feature का number |
| PATCH | Compatible fix number | compatible fix का number |
| Pre-release | Version before stable | stable से पहले का version |
| Caret range | ^ allows minor+patch | ^ minor+patch की अनुमति |
| CalVer | Date-based versions | तारीख़ आधारित versions |

---

## ⚡ 3-Line Summary
English: SemVer is MAJOR.MINOR.PATCH: breaking, feature, fix.
It lets users know how risky an upgrade is.
Never change a published version; release a new one.
Hindi: SemVer = MAJOR.MINOR.PATCH: breaking, feature, fix।
इससे users को upgrade का risk पता चलता है।
Published version कभी मत बदलो; नया release करो।

---

## ➡️ Next Topic
**25. Pull Request Best Practices** - how changes get reviewed and merged before they are versioned.

---
