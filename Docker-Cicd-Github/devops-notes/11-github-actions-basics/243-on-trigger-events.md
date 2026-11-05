# 243. on: — Trigger Events
# हिंदी में: on: — Trigger Events (workflow कब चले)

---

## 🔵 Simple Definition (English)
`on:` is the required top-level key that tells GitHub **when** to run the workflow. It accepts a single event name, a list of events, or a map where each event has filters (branches, tags, paths, activity types). If any listed event matches, the workflow runs.

## 🔵 सरल परिभाषा (Hindi)
`on:` ज़रूरी top-level key है जो GitHub को बताती है कि workflow **कब** चलाना है। यह एक event का नाम, events की list, या map ले सकती है जहाँ हर event के filters (branches, tags, paths, activity types) होते हैं। सूची का कोई भी event match करे तो workflow चलता है।

---

## 🔴 Problem it Solves
Without precise triggers, CI either runs too often (every branch, every README edit: wasted minutes and noise) or too rarely (tests miss PRs; deploy misses tags). Triggering production deploy from a feature branch by mistake is a classic incident.

`on:` with filters lets you say "tests on every PR, deploy only from main or a version tag, ignore docs".

## 🔴 यह क्यों बना? (Hindi)
सटीक triggers के बिना CI या तो बहुत ज़्यादा चलता है (हर branch, README की हर edit: minutes बर्बाद और शोर) या बहुत कम (PR पर tests नहीं; tag पर deploy नहीं)। Feature branch से गलती से production deploy हो जाना एक क्लासिक incident है।

Filters वाला `on:` कहने देता है: "हर PR पर tests, deploy सिर्फ main या version tag से, docs को अनदेखा करो"।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Event arrives at GitHub (push, pull_request, ...)
Step 2 → GitHub loads each workflow file from the event's commit
Step 3 → Checks `on:` -> is this event name listed?
Step 4 → Applies filters: branches / branches-ignore / tags / tags-ignore / paths / paths-ignore / types
Step 5 → ALL filters under one event are ANDed; multiple events are ORed
Step 6 → Match -> create run.  No match -> nothing happens (no error)
```

Three syntax forms:

```yaml
on: push                          # 1. single event
on: [push, pull_request]          # 2. list (no filters possible)
on:                               # 3. map (filters allowed)
  push:
    branches: [main]
```

Filter cheat sheet:
- `branches` / `branches-ignore` (cannot use both for the same event; use `!` patterns inside `branches` for mixes)
- `tags` / `tags-ignore`
- `paths` / `paths-ignore`
- `types` (activity types, e.g. `[opened, synchronize]`)
- Glob patterns: `*` (no `/`), `**` (any including `/`), `?`, `[]`, `!` for negation. Example: `releases/**`, `v[0-9]+.[0-9]+.[0-9]+`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → GitHub के पास event आता है (push, pull_request, ...)।
Step 2 → GitHub event के commit से हर workflow file लोड करता है।
Step 3 → `on:` में देखता है: क्या यह event नाम सूची में है?
Step 4 → Filters लगाता है: branches / tags / paths / types।
Step 5 → एक event के सारे filters AND होते हैं; अलग-अलग events OR होते हैं।
Step 6 → Match -> run बनता है। Match नहीं -> कुछ नहीं होता (error भी नहीं)।

Syntax के तीन रूप: single event, list (filters नहीं लग सकते), और map (filters लग सकते हैं)। Glob patterns: `*` (बिना `/`), `**` (`/` समेत कुछ भी), `!` से negation।

---

## 🟡 Real World Example
An e-commerce team's monorepo has `api/`, `web/` and `docs/`. Their `on:` rules:
- PR touching `api/**` runs API tests only.
- Push to `main` touching `web/**` rebuilds the React app.
- Edits to `docs/**` or `*.md` trigger nothing.
- Tag `v2.3.1` deploys to production.
During a Big Billion Days style sale week, this saves thousands of CI minutes because unrelated pushes skip the pipeline.

## 🟡 Real Example Hindi mein
एक e-commerce team की monorepo में `api/`, `web/` और `docs/` हैं। उनके `on:` नियम: `api/**` बदलने वाला PR सिर्फ API tests चलाता है; `main` पर `web/**` बदलने वाला push React app दोबारा build करता है; `docs/**` या `*.md` की edit कुछ trigger नहीं करती; tag `v2.3.1` production पर deploy करता है। Sale वाले हफ्ते में अलग-अलग pushes pipeline skip करके हज़ारों CI minutes बचाते हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/on-basic.yml
name: On Basic                        # Workflow name
on:                                   # Triggers (map form so filters work)
  push:                               # Event 1
    branches:                         # Only these branches
      - main                          # Exact name
      - "release/**"                  # Any branch starting with release/ (quote because of *)
    paths-ignore:                     # Skip when ONLY these files changed
      - "**.md"                       # Any markdown file
      - "docs/**"                     # Everything in docs/
  pull_request:                       # Event 2
    branches: [main]                  # PRs whose base is main
  workflow_dispatch:                  # Event 3: manual button, no config needed
jobs:
  info:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Triggered by ${{ github.event_name }} on ${{ github.ref }}"   # Show cause
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/on-advanced.yml
name: On Advanced                     # Filters, types, schedule, calls
on:
  push:
    branches:
      - main                          # Include main
      - "feature/**"                  # Include feature branches
      - "!feature/experimental-**"    # Exclude experimental ones (negation after an include)
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"       # Semantic version tags like v1.2.3
    paths:
      - "api/**"                      # Run only when API code changes
      - "package*.json"               # ...or dependency files
      - ".github/workflows/on-advanced.yml"   # ...or this workflow itself
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]   # Explicit PR activities
    branches: [main]
  schedule:
    - cron: "0 21 * * 1-5"            # 21:00 UTC Mon-Fri = 02:30 IST next morning
  workflow_dispatch:
    inputs:
      reason:
        description: Why are you running this?
        required: true                # UI forces an answer
        type: string
  workflow_call:                      # Also usable as a reusable workflow
    inputs:
      env_name:
        required: false
        type: string
        default: staging
jobs:
  main:
    runs-on: ubuntu-latest
    if: github.event_name != 'pull_request' || !github.event.pull_request.draft   # Skip draft PRs
    steps:
      - uses: actions/checkout@v4
      - run: |
          echo "event=${{ github.event_name }}"       # Which trigger fired
          echo "ref=${{ github.ref }}"                # What ref
          echo "reason=${{ inputs.reason }}"          # Only set for manual runs
```

Note: `paths` and `tags` filters: when a push has both `branches` and `paths`, both must match. For tag pushes, `paths` filters are not evaluated against file changes in the same way, so avoid combining `tags` with `paths` expecting file filtering on tags.

---

## 🟠 My Stack Integration
Trigger map for your repo (Node API, FastAPI, React, deploy to VPS/AWS):

```yaml
# .github/workflows/stack-on.yml
name: Stack Triggers
on:
  pull_request:
    branches: [main]                  # Validate before merge
    paths:
      - "api/**"                      # Node.js API
      - "fastapi/**"                  # Python service
      - "web/**"                      # React app
      - "docker-compose*.yml"         # Compose changes
  push:
    branches: [main]                  # Merge to main deploys to staging
    tags: ["v*"]                      # Version tag deploys to production
  schedule:
    - cron: "30 20 * * *"             # 02:00 IST nightly dependency/image scan
  workflow_dispatch:
    inputs:
      image_tag:
        description: Image tag to roll back to
        required: false
        type: string
jobs:
  decide:
    runs-on: ubuntu-latest
    outputs:
      target: ${{ steps.pick.outputs.target }}   # Environment chosen for later jobs
    steps:
      - id: pick
        run: |
          if [[ "${GITHUB_REF}" == refs/tags/v* ]]; then echo "target=production" >> "$GITHUB_OUTPUT"
          elif [[ "${GITHUB_EVENT_NAME}" == "push" ]]; then echo "target=staging" >> "$GITHUB_OUTPUT"
          else echo "target=none" >> "$GITHUB_OUTPUT"; fi
```

Security: avoid `pull_request_target` unless you understand it. For `workflow_dispatch` inputs, treat values as untrusted text (pass via `env:`, never inline in `run:`). Restrict who can trigger manual deploys with environment protection rules.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `branches: [main]` and `branches-ignore: [dev]` together for one event.
✅ Correct: Use one of them; use `!pattern` inside `branches` for exclusions.

❌ Mistake 2: Unquoted patterns starting with `*` or `!`, e.g. `- *.md`.
✅ Correct: Quote: `- "*.md"`, `- "!docs/**"`.

❌ Mistake 3: Expecting `paths` filters to work on `schedule` or `workflow_dispatch`.
✅ Correct: Filters apply only to `push`/`pull_request` (and a few others).

❌ Mistake 4: `on: [push, pull_request]` without filters: every push to a PR branch runs twice (once for push, once for PR).
✅ Correct: Run `push` only on `main` and `pull_request` for PRs.

---

## 🧠 Tricky Interview Question
"A PR changes only `README.md`. Your workflow has `paths-ignore: ['**.md']` and is a **required status check**. The PR can never be merged. Why?"

Answer: When a workflow is skipped by path filters, its check never reports. A required check that never appears stays "Expected - waiting for status", blocking the merge. Solutions: remove path filters on required workflows and use job-level logic (e.g., `dorny/paths-filter` plus `if:`) so the workflow always runs and quickly exits successful; or create a lightweight workflow with the same job names that reports success for ignored paths. Note this differs from a job skipped via `if:`, which reports as skipped/success.

---

## ⚫ Interview Questions + Answers

Q1: Are multiple events combined by AND or OR?
A1: OR. Any matching event starts the workflow. Filters inside one event are ANDed.

Q2: How do you trigger only for tags like v1.2.3?
A2: `on: push: tags: ["v[0-9]+.[0-9]+.[0-9]+"]`.

Q3: Which timezone does cron use?
A3: UTC. Minimum interval is 5 minutes.

Q4: Why does my workflow not run on the PR from a fork?
A4: First-time contributors need approval, or the workflow file on the base branch does not match; for `pull_request`, the workflow definition comes from the merge commit of the PR.

Q5: How do you run a workflow only for non-draft PRs?
A5: Add `if: github.event.pull_request.draft == false` and include `ready_for_review` in `types`.

---

## 🔷 When to Use + When Not to Use
✅ Use filters when:
- Monorepo with independent parts.
- Cost matters; docs changes should not run CI.
- You need different behaviour for branches vs tags.

❌ Avoid filters when:
- The workflow is a required status check (use always-run + conditional jobs).
- Filters become so complex nobody understands them; split into separate workflows.

---

## 📊 Visual Diagram

```
 EVENT: push to refs/heads/feature/login, changed api/user.js
        |
        v
  on:
   push:
     branches: [main, "feature/**"]   -> matches?  YES
     paths: ["api/**"]                -> matches?  YES
        |  (all filters inside the event must pass: AND)
        v
      RUN CREATED

 EVENT: schedule 20:30 UTC     --OR--   EVENT: workflow_dispatch click
        (any one event in the list is enough: OR)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| on | Trigger section | trigger वाला हिस्सा |
| Filter | Limits when event matches | event को सीमित करने वाला filter |
| Glob | Wildcard pattern like `**` | wildcard pattern |
| Activity type | Sub-action of event (opened, closed) | event की उप-क्रिया |
| Cron | Schedule expression (UTC) | समय-सारणी (UTC) |
| Required check | Check needed before merge | merge से पहले ज़रूरी check |

---

## ⚡ 3-Line Summary
English: `on:` defines events and optional filters that decide when a workflow runs.
Multiple events are ORed, filters within an event are ANDed, and cron uses UTC.
Be careful with path filters on required checks.

Hindi: `on:` events और वैकल्पिक filters तय करता है कि workflow कब चले।
अलग events OR होते हैं, एक event के अंदर filters AND होते हैं, और cron UTC में चलता है।
Required checks पर path filters लगाने में सावधान रहें।

---

## ➡️ Next Topic
**244. push Event** — branches, tags, paths and what exactly a push event contains.

---
