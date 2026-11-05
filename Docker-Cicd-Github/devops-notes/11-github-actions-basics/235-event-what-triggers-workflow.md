# 235. Event — What triggers workflow
# हिंदी में: Event — जो workflow को शुरू करता है

---

## 🔵 Simple Definition (English)
An **event** is something that happens in or to your GitHub repository (a push, a pull request, an issue comment, a release, a clock time, a manual click, or an API call) that can start a workflow. You choose which events to listen to under the `on:` key.

## 🔵 सरल परिभाषा (Hindi)
**Event** वह घटना है जो आपकी GitHub repository में या उस पर होती है (push, pull request, issue comment, release, घड़ी का समय, manual click या API call) और workflow शुरू कर सकती है। आप `on:` key के नीचे चुनते हैं कि किन events को सुनना है।

---

## 🔴 Problem it Solves
Without events, someone would have to click "build" for each change. Polling systems (Jenkins checking Git every 5 minutes) wasted resources and added delay. And one fixed trigger is not enough: you want tests on PRs, deploys on tags, scans at night, and rollbacks on demand.

Events give you precise, push-based triggers so each workflow runs only when it should, saving minutes and avoiding accidental deploys.

## 🔴 यह क्यों बना? (Hindi)
Events के बिना हर बदलाव के लिए किसी को "build" दबाना पड़ता। Polling वाले systems (Jenkins हर 5 मिनट Git देखता) संसाधन बर्बाद करते और देरी जोड़ते थे। और एक ही trigger काफी नहीं: PR पर tests, tag पर deploy, रात में scan, और ज़रूरत पर rollback चाहिए।

Events सटीक, push-based triggers देते हैं ताकि हर workflow सिर्फ तभी चले जब चलना चाहिए, इससे minutes बचते हैं और गलती से deploy नहीं होता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Something happens (e.g. you push a commit)
Step 2 → GitHub creates an event with a payload (who, what, which ref, which sha)
Step 3 → GitHub scans workflow files on the relevant ref
Step 4 → A workflow whose `on:` matches (event name + filters) starts a run
Step 5 → Event data is available inside the run as `github.event` (JSON payload)
Step 6 → Context values such as github.ref, github.sha, github.actor are also set
```

Categories of events:
- **Repo activity**: `push`, `pull_request`, `release`, `create`, `delete`, `issues`, `issue_comment`.
- **Time based**: `schedule` (cron).
- **Manual / API**: `workflow_dispatch`, `repository_dispatch`.
- **Workflow related**: `workflow_call` (reusable), `workflow_run` (after another workflow).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → कुछ होता है (जैसे आप commit push करते हैं)।
Step 2 → GitHub payload के साथ एक event बनाता है (किसने, क्या, कौन सा ref, कौन सा sha)।
Step 3 → GitHub संबंधित ref पर workflow files देखता है।
Step 4 → जिस workflow का `on:` (event नाम + filters) match करे, उसका run शुरू होता है।
Step 5 → Event का data run के अंदर `github.event` (JSON payload) में मिलता है।
Step 6 → `github.ref`, `github.sha`, `github.actor` जैसे context values भी set होते हैं।

Event की श्रेणियाँ: repo activity (`push`, `pull_request`, `release`...), time based (`schedule`), manual / API (`workflow_dispatch`, `repository_dispatch`), और workflow related (`workflow_call`, `workflow_run`)।

---

## 🟡 Real World Example
Swiggy-like backend team events map:
- Developer opens PR -> `pull_request` -> run tests.
- PR merged to `main` -> `push` -> build image, deploy to staging.
- Tech lead publishes release `v2.4.0` -> `release` (types: published) -> deploy to production.
- 2 AM every night -> `schedule` -> vulnerability scan.
- Support engineer needs a hotfix rollback -> `workflow_dispatch` with input `version`.
- Monitoring tool detects failure -> calls API -> `repository_dispatch` -> run diagnostics.

## 🟡 Real Example Hindi mein
Swiggy जैसी backend team का events map: Developer PR खोलता है -> `pull_request` -> tests। PR `main` में merge -> `push` -> image build और staging deploy। Tech lead release `v2.4.0` publish करता है -> `release` -> production deploy। हर रात 2 बजे -> `schedule` -> vulnerability scan। Support engineer को hotfix rollback चाहिए -> `workflow_dispatch` input `version` के साथ। Monitoring tool failure पकड़ता है -> API call -> `repository_dispatch` -> diagnostics।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/events-basic.yml
name: Events Basic                    # Workflow name
on:                                   # Listen to several events at once
  push:                               # Event 1: new commits pushed
    branches: [main]                  # Filter: only main branch
  pull_request:                       # Event 2: PR opened/updated
    branches: [main]                  # Filter: PRs that target main
  workflow_dispatch:                  # Event 3: manual run button
jobs:
  show-event:                         # Job id
    runs-on: ubuntu-latest            # Runner
    steps:
      - name: Print event info        # Step name
        run: |                        # Multi-line shell script
          echo "Event: ${{ github.event_name }}"   # Name of the triggering event
          echo "Ref:   ${{ github.ref }}"          # Branch or tag ref
          echo "Actor: ${{ github.actor }}"        # Who caused it
          echo "SHA:   ${{ github.sha }}"          # Commit SHA
```

Short forms you will see: `on: push`, `on: [push, pull_request]`. Use the long map form when you need filters.

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/events-advanced.yml
name: Events Advanced                 # Multi-event routing example
on:
  push:
    branches: [main]                  # Branch filter
    tags: ["v*.*.*"]                  # Also fire on version tags like v1.2.3
    paths-ignore: ["**.md"]           # Ignore docs-only pushes
  pull_request:
    types: [opened, synchronize, reopened]   # Run when PR opens, gets new commits, or reopens
  schedule:
    - cron: "30 20 * * *"             # 20:30 UTC = 02:00 IST daily (UTC only)
  workflow_dispatch:
    inputs:
      environment:                    # Manual input
        description: "Target env"
        type: choice                  # Dropdown in UI
        options: [staging, production]
        default: staging
permissions:
  contents: read                      # Least privilege
jobs:
  route:
    runs-on: ubuntu-latest
    steps:
      - name: Decide what to do based on event
        run: |
          case "${{ github.event_name }}" in
            pull_request)  echo "Run tests only" ;;            # PR path
            push)          echo "Build and deploy staging" ;;  # Push path
            schedule)      echo "Run security scan" ;;         # Cron path
            workflow_dispatch) echo "Manual deploy to ${{ inputs.environment }}" ;;   # Manual path
          esac
  deploy-prod:
    if: startsWith(github.ref, 'refs/tags/v')   # Only when the push was a version tag
    needs: route                      # Wait for routing step
    runs-on: ubuntu-latest
    steps:
      - run: echo "Production deploy for ${{ github.ref_name }}"   # Tag name e.g. v1.2.3
```

---

## 🟠 My Stack Integration
Event plan for Node.js API + FastAPI + React on a VPS and AWS:

| Event | Action |
|---|---|
| `pull_request` to `main` | Lint, test, build React, build Docker image (no push) |
| `push` to `main` | Push image to registry, deploy to VPS staging |
| `push` tag `v*` | Deploy to production VPS or ECS |
| `schedule` nightly | `npm audit`, `pip-audit`, Trivy image scan |
| `workflow_dispatch` | Manual rollback with image tag input |

```yaml
# .github/workflows/stack-events.yml
name: Stack Events
on:
  pull_request:
    branches: [main]                  # Validate before merge
  push:
    branches: [main]                  # Deploy path
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4     # Get code
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci && npm test       # Run on both events
  deploy-staging:
    needs: test                       # Only after tests pass
    if: github.event_name == 'push'   # Skip on pull requests
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploy to VPS staging"   # SSH deploy added in later topics
```

Security: events from forks carry no secrets for `pull_request`. Treat `issue_comment` and `pull_request_target` as dangerous because their text/code comes from outsiders; never interpolate `${{ github.event.comment.body }}` straight into `run:` (script injection). Pass it through an env var instead.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `on: push` with no filters, so every branch and docs change triggers deploy.
✅ Correct: Add `branches`, `tags`, `paths` filters.

❌ Mistake 2: Writing cron times in IST.
✅ Correct: Cron is always UTC; convert (IST = UTC + 5:30).

❌ Mistake 3: Expecting `workflow_dispatch` button to appear on a branch that does not yet contain the workflow file.
✅ Correct: The workflow file must exist on the default branch for the button to show (it can then run against other branches).

❌ Mistake 4: Triggering a workflow from another workflow using the default `GITHUB_TOKEN` and expecting it to fire.
✅ Correct: Events created by `GITHUB_TOKEN` do not trigger new workflows (except `workflow_dispatch` and `repository_dispatch`); use a PAT or GitHub App token or `workflow_run`.

---

## 🧠 Tricky Interview Question
"You pushed a tag `v1.0.0` and also pushed to `main` in the same `git push`. Your workflow has `on: push: branches: [main]`. Does it run for the tag?"

Answer: Not for the tag. A filter matches only what is listed. A tag push has `github.ref = refs/tags/v1.0.0`, which does not match `branches: [main]`. The `main` push fires one run, the tag push fires nothing unless you add `tags: ['v*']`. If you list only `tags`, branch pushes do not run. To trigger on both, list both keys under `push`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `push` and `pull_request`?
A1: `push` fires when commits land on a branch or tag. `pull_request` fires on PR activity (opened, synchronize, reopened by default) and runs against the merge commit of the PR.

Q2: How do you read the event payload?
A2: Through the `github.event` context, e.g. `github.event.pull_request.title`. The raw JSON is also at `$GITHUB_EVENT_PATH`.

Q3: How do you trigger a workflow via API?
A3: `workflow_dispatch` (REST: create a workflow dispatch event) or `repository_dispatch` (custom event types), both need a token with proper permission.

Q4: Why does a scheduled workflow sometimes run late?
A4: GitHub queues cron jobs on shared capacity; delays at peak times (top of the hour) are normal. Also, schedules in repos with 60 days of no activity may be disabled for public repos.

Q5: What is script injection via events?
A5: Putting untrusted event data (PR title, branch name, comment body) inside a `run:` shell via `${{ }}` lets an attacker inject commands. Assign it to an `env:` variable and use `"$VAR"`.

---

## 🔷 When to Use + When Not to Use
✅ Use precise event filters when:
- You deploy only from certain branches or tags.
- Docs-only changes should not burn CI minutes.
- You need manual or API-driven operations such as rollback.

❌ Avoid when:
- `pull_request_target` or `issue_comment` would run untrusted code with secrets.
- A cron is used where a real event exists (do not poll if a webhook can notify).

---

## 📊 Visual Diagram

```
   Developer         Cron clock         Human / API
      |                  |                   |
  push / PR /        schedule         workflow_dispatch /
  release / tag                       repository_dispatch
      \                  |                  /
       \                 |                 /
        v                v                v
      +--------------- GitHub ---------------+
      |  create EVENT + payload (github.event)|
      +-------------------+-------------------+
                          | match `on:` + filters
              +-----------+-----------+
              v           v           v
          ci.yml      deploy.yml  nightly.yml
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event | Something that can start a workflow | workflow शुरू करने वाली घटना |
| Payload | JSON data describing the event | event का JSON data |
| Filter | branches / tags / paths limit | सीमित करने वाला filter |
| Cron | Time schedule syntax | समय-सारणी syntax |
| Dispatch | Manual or API trigger | manual या API trigger |
| Script injection | Untrusted text becomes shell code | अविश्वसनीय text का shell code बनना |

---

## ⚡ 3-Line Summary
English: Events are the triggers (push, PR, cron, manual, API) listed under `on:`.
Filters on branches, tags, paths and activity types control exactly when a run starts.
Treat event data from outsiders as untrusted to avoid injection.

Hindi: Events वे triggers हैं (push, PR, cron, manual, API) जो `on:` में लिखे जाते हैं।
Branches, tags, paths और activity types के filters तय करते हैं कि run कब शुरू होगा।
बाहरी लोगों से आए event data को अविश्वसनीय मानें ताकि injection न हो।

---

## ➡️ Next Topic
**236. Job — What it is** — how a job maps to one runner, how jobs run in parallel or in order with `needs`, and how to pass data between them.

---
