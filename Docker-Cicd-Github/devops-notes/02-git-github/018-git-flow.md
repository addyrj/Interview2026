# 18. Git Flow
# हिंदी में: Git Flow

---

## 🔵 Simple Definition (English)
**Git Flow** is a branching model by Vincent Driessen with two permanent branches (`main` for released code, `develop` for integration) and three kinds of supporting branches: `feature/*`, `release/*` and `hotfix/*`. It is built for software released in planned, versioned batches.

## 🔵 सरल परिभाषा (Hindi)
**Git Flow** Vincent Driessen का branching model है जिसमें दो permanent branches हैं (`main` = released code, `develop` = integration) और तीन तरह की supporting branches: `feature/*`, `release/*`, `hotfix/*`। यह planned, versioned batches में release होने वाले software के लिए बना है।

---

## 🔴 Problem it Solves
When you ship version 2.0 while developers already work on 2.1, you need a place to stabilise 2.0 without blocking new work, and a way to patch the live 1.9 quickly. Single-branch workflows cannot do both. Git Flow separates "what is live" (`main`), "what is next" (`develop`), "what is being stabilised" (`release/*`), and "emergency fix" (`hotfix/*`).

## 🔴 यह क्यों बना? (Hindi)
जब आप version 2.0 ship कर रहे हों और developers 2.1 पर काम कर रहे हों, तब 2.0 को नए काम को रोके बिना stable करने की जगह चाहिए, और live 1.9 को जल्दी patch करने का तरीका भी। Single-branch workflow दोनों नहीं कर पाता। Git Flow अलग करता है: "क्या live है" (`main`), "आगे क्या है" (`develop`), "क्या stabilise हो रहा है" (`release/*`), "emergency fix" (`hotfix/*`)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Feature: branch feature/x from develop; finish -> merge back into develop.
Step 2 → Release: when develop has enough, branch release/1.4.0 from develop.
Step 3 → On release/1.4.0 only bug fixes, version bump, docs (no new features).
Step 4 → Finish release: merge into main, TAG v1.4.0, merge back into develop.
Step 5 → Hotfix: branch hotfix/1.4.1 from main, fix, merge into main (tag v1.4.1) AND develop.
Step 6 → Delete the short-lived branches.
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Feature: develop से feature/x बनाओ; पूरा होने पर develop में merge।
Step 2 → Release: develop में पर्याप्त काम हो जाए तो develop से release/1.4.0 बनाओ।
Step 3 → release/1.4.0 पर सिर्फ bug fixes, version bump, docs (नया feature नहीं)।
Step 4 → Release finish: main में merge, TAG v1.4.0, और develop में वापस merge।
Step 5 → Hotfix: main से hotfix/1.4.1, fix, main में merge (tag v1.4.1) और develop में भी।
Step 6 → Short-lived branches delete करो।

---

## 🟡 Real World Example
A company building an on-premise ERP for banks ships quarterly versions (v3.2, v3.3). Customers run old versions for years, so they need `release/*` stabilisation and `hotfix/*` patches on tagged versions. This fits Git Flow. A SaaS like Swiggy's customer web app deploying many times a day does not need it.

## 🟡 Real Example Hindi mein
Banks के लिए on-premise ERP बनाने वाली company हर तिमाही versions (v3.2, v3.3) ship करती है। Customers पुराने versions सालों चलाते हैं, इसलिए `release/*` stabilisation और tagged versions पर `hotfix/*` patches चाहिए। यह Git Flow में fit होता है। Swiggy जैसा SaaS web app जो दिन में कई बार deploy करता है, उसे इसकी ज़रूरत नहीं।

---

## 💻 Code / Config Example — Basic

Plain Git commands (no git-flow plugin needed). `--no-ff` keeps a merge commit so the feature is visible in history.

```bash
#!/usr/bin/env bash
# gitflow-basic.sh - one feature, one release, one hotfix using plain git
set -euo pipefail                                        # stop on error

git switch develop                                       # integration branch
git switch -c feature/invoice-pdf                        # 1. start feature from develop
echo "pdf" > pdf.txt && git add pdf.txt                  # make a change and stage it
git commit -m "feat(invoice): add PDF export"            # commit
git switch develop                                       # back to develop
git merge --no-ff feature/invoice-pdf -m "Merge feature/invoice-pdf"   # merge with explicit merge commit
git branch -d feature/invoice-pdf                        # delete finished feature

git switch -c release/1.4.0 develop                      # 2. cut a release branch from develop
# ... only bug fixes and version bump here ...
git switch main                                          # 4. finish release: go to main
git merge --no-ff release/1.4.0 -m "Release 1.4.0"      # merge release into main
git tag -a v1.4.0 -m "Release 1.4.0"                     # annotated tag marks the release
git switch develop                                       # merge release fixes back
git merge --no-ff release/1.4.0 -m "Merge release/1.4.0 back"
git branch -d release/1.4.0                              # delete the release branch

git switch -c hotfix/1.4.1 main                          # 5. emergency fix from main
echo "fix" > fix.txt && git add fix.txt && git commit -m "fix: crash on empty invoice"
git switch main && git merge --no-ff hotfix/1.4.1 -m "Hotfix 1.4.1"   # ship to main
git tag -a v1.4.1 -m "Hotfix 1.4.1"                      # tag the patch release
git switch develop && git merge --no-ff hotfix/1.4.1 -m "Merge hotfix back"  # keep develop in sync
git branch -d hotfix/1.4.1                               # cleanup
```

## 💻 Code / Config Example — Advanced

CI mapping for Git Flow: `develop` deploys to staging, `main` tags deploy to production, PRs run tests.

```yaml
# .github/workflows/gitflow-ci.yml
name: gitflow-ci                                    # workflow name
on:
  pull_request:                                     # test every PR
    branches: [develop, main, 'release/**']         # into these branches
  push:
    branches: [develop]                             # develop merges -> staging
    tags: ['v*.*.*']                                # version tags -> production
jobs:
  test:
    runs-on: ubuntu-latest                          # runner image
    steps:
      - uses: actions/checkout@v4                   # fetch code (example version)
      - uses: actions/setup-node@v4                 # install Node (example version)
        with:
          node-version: 20                          # Node version
          cache: npm                                # speed up installs
      - run: npm ci                                 # reproducible install
      - run: npm test                               # run tests
  deploy-staging:
    needs: test                                     # only after tests pass
    if: github.ref == 'refs/heads/develop'          # only for develop pushes
    runs-on: ubuntu-latest
    environment: staging                            # GitHub environment (can hold secrets)
    steps:
      - run: echo "deploy to staging.example.com"   # replace with real SSH/docker deploy
  deploy-prod:
    needs: test                                     # tests must pass
    if: startsWith(github.ref, 'refs/tags/v')       # only for version tags
    runs-on: ubuntu-latest
    environment: production                         # can require manual approval
    steps:
      - run: echo "deploy ${{ github.ref_name }} to production"   # replace with real deploy
```

---

## 🟠 My Stack Integration
- Use Git Flow only if your FastAPI/Node product has versioned releases (e.g., self-hosted customers). For your single VPS SaaS, GitHub Flow is simpler.
- **Docker tags:** `develop` -> `myapp:develop-<sha>`; tag `v1.4.0` -> `myapp:1.4.0` and `myapp:latest`-style pointer only if you accept it.
- **Nginx:** staging vhost on a subdomain for `develop`, production vhost for tags.

```bash
# Build and tag image by Git Flow state (run in CI)
VERSION="${GITHUB_REF_NAME#v}"                      # strip leading v from tag: v1.4.0 -> 1.4.0
docker build -t myorg/api:"$VERSION" .              # image tagged with release version
docker tag myorg/api:"$VERSION" myorg/api:stable    # moving pointer to latest release (example)
```

**Security:** protect both `main` and `develop`; restrict who can create `v*` tags (tag protection / rulesets) since tags trigger production deploys.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to merge `hotfix`/`release` back into `develop`.
✅ Correct: Always merge to both `main` and `develop`, or the bug returns in the next release.

❌ Mistake 2: Adding features on a `release/*` branch.
✅ Correct: Only fixes; features go to `develop`.

❌ Mistake 3: Using Git Flow for continuous deployment.
✅ Correct: Use GitHub Flow / trunk-based.

❌ Mistake 4: Leaving `develop` and `main` diverged for months.
✅ Correct: Release regularly.

---

## 🧠 Tricky Interview Question
A hotfix was merged to `main` and tagged, but two weeks later the same bug reappears in the new release. What went wrong?

**Answer:** The hotfix was not merged back into `develop` (or into the open `release/*` branch). The next release was cut from `develop` which lacked the fix. Git Flow requires hotfixes to merge into both `main` and `develop` (or the current release branch if one exists).

---

## ⚫ Interview Questions + Answers

Q1: Name the five Git Flow branch types.
A1: `main`, `develop`, `feature/*`, `release/*`, `hotfix/*`.

Q2: Where do features branch from and merge into?
A2: From `develop`, back into `develop`.

Q3: Why `--no-ff`?
A3: It forces a merge commit, preserving the fact that a group of commits belonged to one feature.

Q4: Main criticism of Git Flow?
A4: Too heavy for continuous delivery; long-lived branches cause merge conflicts and delay feedback.

Q5: What marks a release?
A5: An annotated tag (e.g., `v1.4.0`) on `main`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Scheduled, versioned releases; multiple supported versions.
- Strict QA phase before release.

❌ Avoid when:
- Web apps deploying many times per day.
- Small teams that want speed.

---

## 📊 Visual Diagram

```
 main     o-----------------o------------o-----> (tags v1.4.0, v1.4.1)
           \               / \          / \
 hotfix     \             /   o--------o   \
 release     \      o----o                  \
 develop  o---o--o---o------o--------o--------o-->
              \     /
 feature       o---o
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| develop | Integration branch | integration branch |
| release branch | Stabilise next version | अगला version stable करने की branch |
| hotfix | Urgent fix on live code | live code पर urgent fix |
| --no-ff | Always create merge commit | हमेशा merge commit बनाओ |
| Annotated tag | Tag with metadata | metadata वाला tag |

---

## ⚡ 3-Line Summary
English: Git Flow uses main, develop, feature, release and hotfix branches.
It fits planned versioned releases with a stabilisation phase.
Hotfixes and releases must merge back into develop.
Hindi: Git Flow में main, develop, feature, release और hotfix branches होती हैं।
यह planned versioned releases और stabilisation phase के लिए ठीक है।
Hotfix और release को develop में वापस merge करना ज़रूरी है।

---

## ➡️ Next Topic
**19. GitHub Flow** - the simpler, continuous-delivery alternative.

---
