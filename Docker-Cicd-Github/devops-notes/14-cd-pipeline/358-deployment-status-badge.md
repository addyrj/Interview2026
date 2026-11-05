# 358. Deployment Status Badge
# हिंदी में: Deployment Status Badge

---

## 🔵 Simple Definition (English)
A status badge is a small image (usually SVG) that shows the current result of a workflow, such as "build passing" or "deploy failing". You embed it in your README. GitHub generates workflow badges for you, and services like Shields.io can show custom badges (version, coverage, uptime).

## 🔵 सरल परिभाषा (Hindi)
Status badge एक छोटी image (आमतौर पर SVG) है जो workflow का मौजूदा result दिखाती है, जैसे "build passing" या "deploy failing"। इसे README में लगाते हैं। GitHub workflow badges खुद बनाता है, और Shields.io जैसी services custom badges (version, coverage, uptime) दिखा सकती हैं।

---

## 🔴 Problem it Solves
New contributors, reviewers and interviewers open a repo and cannot tell if it is healthy. Teams do not notice that `main` has been red for two days. A badge puts pipeline health where everyone looks first, the README, and a green badge is a quick signal of engineering discipline.

## 🔴 यह क्यों बना? (Hindi)
नए contributors, reviewers और interviewers repo खोलकर समझ नहीं पाते कि वह स्वस्थ है या नहीं। Teams को पता ही नहीं चलता कि `main` दो दिन से red है। Badge pipeline की सेहत वहाँ दिखाता है जहाँ सब सबसे पहले देखते हैं, README में, और हरा badge engineering discipline का तेज़ संकेत है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A workflow file exists, e.g. .github/workflows/ci.yml
Step 2 → GitHub exposes a badge URL for it: .../actions/workflows/ci.yml/badge.svg
Step 3 → You add Markdown ![CI](url) to README.md
Step 4 → Every time the README is viewed, the SVG is fetched with the latest status
Step 5 → Optional: ?branch=main&event=push filters which runs count
Step 6 → Custom badges: Shields.io reads JSON/endpoints and draws SVG
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Workflow file मौजूद है, जैसे .github/workflows/ci.yml
Step 2 → GitHub उसके लिए badge URL देता है: .../actions/workflows/ci.yml/badge.svg
Step 3 → README.md में Markdown ![CI](url) जोड़ो
Step 4 → README खुलने पर हर बार SVG नवीनतम status के साथ आती है
Step 5 → Optional: ?branch=main&event=push से तय होता है कौन से runs गिने जाएँ
Step 6 → Custom badges: Shields.io JSON/endpoints पढ़कर SVG बनाता है
```

---

## 🟡 Real World Example
An open-source Node.js library shows four badges at the top of its README: CI (GitHub Actions), npm version, test coverage, and license. A visitor sees "CI passing" and "coverage 94%" and trusts the project. In a company repo, the README of the FastAPI service shows `deploy-production` status for `main`; when it turns red, anyone opening the repo notices immediately.

## 🟡 Real Example Hindi mein
एक open-source Node.js library अपने README के ऊपर चार badges दिखाती है: CI (GitHub Actions), npm version, test coverage और license। Visitor "CI passing" और "coverage 94%" देखकर project पर भरोसा करता है। Company repo में FastAPI service का README `main` के लिए `deploy-production` status दिखाता है; red होते ही repo खोलने वाला हर व्यक्ति तुरंत देख लेता है।

---

## 💻 Code / Config Example — Basic

```markdown
<!-- README.md - basic GitHub Actions badge -->
<!-- Format: https://github.com/<OWNER>/<REPO>/actions/workflows/<FILE>/badge.svg -->
![CI](https://github.com/myorg/myapp/actions/workflows/ci.yml/badge.svg)

<!-- Only show the status of the main branch -->
![CI main](https://github.com/myorg/myapp/actions/workflows/ci.yml/badge.svg?branch=main)

<!-- Make the badge clickable, linking to the workflow runs page -->
[![Deploy](https://github.com/myorg/myapp/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/myorg/myapp/actions/workflows/deploy.yml)
```

## 💻 Code / Config Example — Advanced

```markdown
<!-- README.md - a full badge row (replace OWNER/REPO with yours) -->
[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)
[![Deploy Prod](https://github.com/OWNER/REPO/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/OWNER/REPO/actions/workflows/deploy.yml)
[![Latest release](https://img.shields.io/github/v/release/OWNER/REPO)](https://github.com/OWNER/REPO/releases)
[![License](https://img.shields.io/github/license/OWNER/REPO)](LICENSE)
[![Uptime](https://img.shields.io/uptimerobot/status/m123456789-abcdef)](https://stats.uptimerobot.com/yourpage)
```

```yaml
# .github/workflows/ci.yml - the workflow behind the badge
name: CI                            # the name shown on the badge and in the Actions tab
on:
  push:
    branches: [main]                # badge reflects runs on main
  pull_request:                     # PR runs are separate (use ?event=push to hide them)
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4   # fetch code
      - uses: actions/setup-node@v4 # install Node
        with:
          node-version: 20
          cache: npm
      - run: npm ci                 # install dependencies
      - run: npm test               # a failing test turns the badge red
```

```yaml
# Dynamic custom badge using a public Gist as the data source (e.g. deployed version)
# Needs a Gist id and a personal access token stored as GIST_TOKEN (gist scope only).
name: Update version badge
on:
  workflow_run:
    workflows: ["Deploy"]           # run after the Deploy workflow finishes
    types: [completed]
jobs:
  badge:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}   # only on success
    runs-on: ubuntu-latest
    steps:
      - name: Write badge JSON to Gist
        env:
          GH_TOKEN: ${{ secrets.GIST_TOKEN }}                 # token with gist scope
          GIST_ID: ${{ vars.BADGE_GIST_ID }}                  # id of the public gist
          SHA: ${{ github.event.workflow_run.head_sha }}      # deployed commit
        run: |
          # shields.io endpoint schema: schemaVersion, label, message, color
          printf '{"schemaVersion":1,"label":"deployed","message":"%s","color":"brightgreen"}' "${SHA::7}" > deployed.json
          gh gist edit "$GIST_ID" --add deployed.json           # create/update the file in the gist
```

```markdown
<!-- Badge that reads the gist file through the Shields endpoint -->
![Deployed](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/USER/GIST_ID/raw/deployed.json)
```

The gist badge flow is an example pattern; check `gh gist edit` options with `gh gist edit --help` in your gh version. It has not been run here.

---

## 🟠 My Stack Integration
- Put CI and Deploy badges at the top of each repo README (Node API, FastAPI service, React app).
- A `/health` or `/version` endpoint on your VPS can feed a live badge: Shields supports dynamic JSON badges from a URL (`img.shields.io/badge/dynamic/json?...`).
- External uptime tools (UptimeRobot, Better Stack) give an "uptime" badge for your Nginx-fronted domain.

```markdown
<!-- Dynamic badge reading version from your own API (endpoint must be public JSON) -->
![version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapp.example.com%2Fapi%2Fversion&query=%24.version&label=prod)
```

```python
# FastAPI /version endpoint feeding that badge
import os
from fastapi import FastAPI

app = FastAPI()                                   # application

@app.get("/api/version")                          # public, harmless metadata only
def version():
    # GIT_SHA is injected at build time via Docker build-arg / env
    return {"version": os.getenv("GIT_SHA", "dev")[:7]}
```

Security: for private repos the workflow badge image is only visible to logged-in collaborators, which is fine. Do not expose internal hostnames, secrets or detailed versions of vulnerable libraries in public badges; share only what an attacker could not use.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using the workflow `name` with spaces and special characters in the URL.
✅ Correct: Use the file name (`ci.yml`) in the badge URL.

❌ Mistake 2: Badge shows a failing PR run, scaring people while `main` is green.
✅ Correct: Add `?branch=main` (and `&event=push` if needed).

❌ Mistake 3: Putting tokens in a Shields URL.
✅ Correct: Never put secrets in URLs; use public endpoints or gists.

❌ Mistake 4: Browser caches an old badge.
✅ Correct: GitHub and Shields cache briefly; wait or use `cacheSeconds` options on Shields endpoints.

❌ Mistake 5: Too many badges.
✅ Correct: Keep three to five meaningful ones.

---

## 🧠 Tricky Interview Question
Your README shows "CI passing" but production is broken. How is that possible?

Answer: The badge reflects the result of one workflow run on one branch, not the health of production. Tests may not cover the failure, the deploy may be a different workflow, or an infrastructure fault (database, certificate, disk) happened after a successful deploy. Use separate badges and real monitoring (uptime checks, alerts) to track runtime health.

---

## ⚫ Interview Questions + Answers

Q1: What is the URL format of a GitHub Actions badge?
A1: `https://github.com/<owner>/<repo>/actions/workflows/<file>.yml/badge.svg`, with optional `?branch=` and `?event=` parameters.

Q2: Can a badge show the deployed version?
A2: Yes, with Shields.io dynamic or endpoint badges reading JSON from your API or a gist.

Q3: Does a green badge mean the code is safe?
A3: No, it means that the workflow's checks passed; coverage and quality depend on the tests.

Q4: What happens with a private repo?
A4: Badge images require authentication, so they show only to people with access in the browser.

Q5: Which workflow trigger keeps a badge relevant?
A5: Run on `push` to the main branch (and schedule if you want periodic checks), then filter the badge by `branch=main`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want quick visibility of build and deploy health.
- The repo is public or shared widely.

❌ Avoid when:
- A badge would reveal sensitive internal information.
- You rely on it as monitoring; use proper alerts instead.

---

## 📊 Visual Diagram
```
 workflow run (main) ---> GitHub stores latest conclusion
                                   |
 README.md  --- ![CI](.../badge.svg?branch=main) --->  SVG: [ CI | passing ] (green)
                                                        or  [ CI | failing ] (red)
 custom: deploy ok --> write JSON to Gist --> Shields endpoint --> [ deployed | a1b2c3d ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Badge | Small status image | छोटी status image |
| SVG | Scalable vector image | scalable vector image |
| Shields.io | Service creating custom badges | custom badges बनाने वाली service |
| Endpoint badge | Badge built from a JSON URL | JSON URL से बना badge |
| Gist | Small GitHub-hosted file store | GitHub पर छोटी file store |

---

## ⚡ 3-Line Summary
English: A badge shows workflow status in your README using the workflow file's badge.svg URL.
Filter by branch and event so it represents main.
Use Shields.io for custom info, but never as a replacement for monitoring.
Hindi: Badge README में workflow file के badge.svg URL से workflow status दिखाता है।
Branch और event से filter करो ताकि वह main को दिखाए।
Custom info के लिए Shields.io लो, पर monitoring की जगह नहीं।

---

## ➡️ Next Topic
**359. Release Notes Generation** — automatically turning merged work into readable release notes.
