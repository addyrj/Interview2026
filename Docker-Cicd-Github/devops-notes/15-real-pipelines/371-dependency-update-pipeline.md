---

# 371. Dependency Update Pipeline
# हिंदी में: Dependency Update Pipeline

---

## 🔵 Simple Definition (English)
A dependency update pipeline uses a bot (Dependabot or Renovate) to open pull requests when new versions of npm packages, Python packages, Docker base images and GitHub Actions are released. Your CI tests each PR, and safe ones are merged automatically.

## 🔵 सरल परिभाषा (Hindi)
Dependency update pipeline एक bot (Dependabot या Renovate) इस्तेमाल करता है जो npm packages, Python packages, Docker base images और GitHub Actions के नए versions आने पर pull request खोलता है। आपका CI हर PR test करता है और सुरक्षित PRs अपने-आप merge हो सकते हैं।

---

## 🔴 Problem it Solves
- Packages go years without updates; one day a critical CVE forces a painful jump over five major versions.
- Nobody remembers to check for updates.
- Base images (`node:20`, `python:3.12-slim`) stay on old OS layers with known vulnerabilities.

## 🔴 यह क्यों बना? (Hindi)
- Packages सालों update नहीं होते; एक दिन critical CVE के कारण पाँच major versions की दर्दनाक छलांग।
- Update जाँचना किसी को याद नहीं रहता।
- Base images (`node:20`, `python:3.12-slim`) पुरानी OS layers पर रहती हैं जिनमें ज्ञात vulnerabilities हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add .github/dependabot.yml with ecosystems and schedule
Step 2 → Bot opens grouped PRs (e.g. "all minor/patch updates")
Step 3 → CI runs on each PR (tests, build, scan)
Step 4 → Auto-merge workflow merges patch/minor PRs when CI is green
Step 5 → Major updates wait for human review
Step 6 → Security updates arrive immediately, outside the schedule
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → .github/dependabot.yml में ecosystems और schedule जोड़ें
Step 2 → Bot grouped PRs खोलता है (जैसे "सारे minor/patch updates")
Step 3 → हर PR पर CI चलता है (tests, build, scan)
Step 4 → CI green होने पर auto-merge workflow patch/minor PRs merge करता है
Step 5 → Major updates इंसान की review का इंतज़ार करते हैं
Step 6 → Security updates schedule के बाहर तुरंत आते हैं
```

---

## 🟡 Real World Example
After the `axios` and `lodash` style vulnerabilities in the news, a team with Dependabot got a security PR within hours, CI passed, and it merged the same afternoon. A neighbouring team without it spent two weeks finding where the vulnerable version was pinned. Weekly grouped PRs also kept their Dockerfile base image fresh (`python:3.12-slim` patch rebuilds).

## 🟡 Real Example Hindi mein
`axios` और `lodash` जैसी vulnerabilities की खबरों के बाद Dependabot वाली team को कुछ घंटों में security PR मिल गया, CI pass हुआ और उसी दोपहर merge हो गया। पास की बिना-Dependabot team ने दो हफ़्ते यह खोजने में लगाए कि vulnerable version कहाँ pinned है। Weekly grouped PRs से उनकी Dockerfile base image (`python:3.12-slim` patch rebuilds) भी ताज़ा रही।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/dependabot.yml
version: 2                             # Required schema version
updates:
  - package-ecosystem: "npm"           # Node packages
    directory: "/"                     # Where package.json lives
    schedule:
      interval: "weekly"               # Check once a week
  - package-ecosystem: "github-actions"  # Also update actions/checkout etc.
    directory: "/"                     # Workflows are found automatically
    schedule:
      interval: "weekly"
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/dependabot.yml  (multi-ecosystem, grouped)
version: 2
updates:
  - package-ecosystem: "npm"           # React / NestJS frontend and backend
    directory: "/frontend"
    schedule:
      interval: "weekly"
      day: "monday"                    # Predictable review day
      time: "06:00"
      timezone: "Asia/Kolkata"         # Local time for the team
    open-pull-requests-limit: 5        # Avoid PR floods
    groups:
      minor-and-patch:                 # One PR for all low-risk updates
        update-types: ["minor", "patch"]
    labels: ["dependencies", "frontend"]
    ignore:
      - dependency-name: "react"       # Example: hold major jumps for a planned migration
        update-types: ["version-update:semver-major"]
  - package-ecosystem: "pip"           # FastAPI backend
    directory: "/backend"
    schedule:
      interval: "weekly"
    groups:
      python-minor-and-patch:
        update-types: ["minor", "patch"]
  - package-ecosystem: "docker"        # Base images in Dockerfiles
    directory: "/backend"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
```

```yaml
# .github/workflows/dependabot-automerge.yml
name: Dependabot auto-merge
on: pull_request                       # Runs on every PR; guarded below
permissions:
  contents: write                      # Needed to merge
  pull-requests: write
jobs:
  automerge:
    if: github.actor == 'dependabot[bot]'   # Only for Dependabot PRs
    runs-on: ubuntu-latest
    steps:
      - id: meta
        uses: dependabot/fetch-metadata@v2  # Reads update type (example version)
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
      - name: Enable auto-merge for minor and patch
        if: steps.meta.outputs.update-type != 'version-update:semver-major'
        run: gh pr merge --auto --squash "$PR_URL"   # Merges only after required checks pass
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 🟠 My Stack Integration
- Branch protection must require your CI checks; otherwise `--auto` merges immediately.
- Repo setting "Allow auto-merge" must be enabled.
- Dependabot-triggered workflows get read-only token and no repository secrets by default, so deploy jobs must not depend on secrets for PR runs (they should not deploy PRs anyway).
- For Renovate instead, add a `renovate.json` with `"extends": ["config:recommended"]` and `"automerge": true` for minor/patch (config not run here).
- Rebuild images periodically even without code changes so the OS packages in your Nginx/Node/Python base images get patched: pair this with the Scheduled Jobs Pipeline.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Auto-merging with no tests.
✅ Correct: Auto-merge only behind required status checks.

❌ Mistake 2: One PR per package with no limit, flooding the team.
✅ Correct: Use `groups` and `open-pull-requests-limit`.

❌ Mistake 3: Ignoring base-image updates.
✅ Correct: Add the `docker` ecosystem.

❌ Mistake 4: Blindly accepting major versions.
✅ Correct: Review majors, read changelogs, test in staging.

Security: pin third-party actions by SHA and let Dependabot update the SHA; supply-chain attacks target actions and packages.

---

## 🧠 Tricky Interview Question
A Dependabot PR is green and auto-merged, but production breaks. How can a green CI miss it?

Answer: Tests did not cover the changed behaviour (a runtime-only or integration change), or a lockfile transitive update changed behaviour. Mitigate with integration/smoke tests, canary rollout, grouped minor updates limited to well-tested areas, and never auto-merge for critical packages like ORMs or auth libraries.

---

## ⚫ Interview Questions + Answers

Q1: Dependabot vs Renovate?
A1: Dependabot is built into GitHub and simple. Renovate is more configurable (grouping, regex managers, schedules, many platforms).

Q2: Why update GitHub Actions?
A2: Old actions use deprecated Node runtimes and may contain vulnerabilities.

Q3: Version updates vs security updates?
A3: Version updates follow your schedule; security updates open as soon as an advisory exists.

Q4: What is semver?
A4: MAJOR.MINOR.PATCH; major may break, minor adds features compatibly, patch fixes bugs.

Q5: Why lockfiles?
A5: They pin exact versions so builds are reproducible and updates are explicit PRs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any project with npm/pip/Docker/Actions dependencies and decent tests.

❌ Avoid when:
- No tests exist; fix that first or updates become noise.

---

## 📊 Visual Diagram
```
 dependabot.yml --> weekly scan --> PR (grouped)
                                      |
                                CI: test, build, scan
                                      |
                  minor/patch --green--> auto-merge --> deploy pipeline
                  major -------------> human review
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dependabot | GitHub's update bot | GitHub का update bot |
| Semver | Major.minor.patch versioning | Version देने का नियम |
| Lockfile | Exact pinned versions | Exact pinned versions की file |
| Auto-merge | Merge after checks pass | Checks पास होने पर merge |
| Supply chain | Third-party code you rely on | आप जिस third-party code पर निर्भर हैं |

---

## ⚡ 3-Line Summary
English: A bot opens PRs for packages, base images and actions.
English: CI validates; minor and patch can auto-merge.
English: Review majors by hand and pin actions.
Hindi: Bot packages, base images और actions के लिए PRs खोलता है।
Hindi: CI जाँचता है; minor और patch auto-merge हो सकते हैं।
Hindi: Major को हाथ से review करें और actions pin करें।

---

## ➡️ Next Topic
372. Security Scan Pipeline: find vulnerabilities, secrets and misconfigurations automatically.
