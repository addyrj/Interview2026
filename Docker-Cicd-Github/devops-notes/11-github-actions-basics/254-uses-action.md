# 254. uses: (Action)
# हिंदी में: uses: (Action का उपयोग)

---

## 🔵 Simple Definition (English)
`uses:` in a step runs a reusable **action**: a packaged unit of automation (JavaScript, Docker container, or composite). You reference it as `owner/repo@ref` (e.g. `actions/checkout@v4`), `owner/repo/path@ref` for a subfolder, `./path` for a local action, or `docker://image:tag`. Inputs are given with `with:`. At job level, `uses:` instead calls a reusable workflow.

## 🔵 सरल परिभाषा (Hindi)
Step में `uses:` एक reusable **action** चलाता है: automation की packaged इकाई (JavaScript, Docker container या composite)। इसे `owner/repo@ref` (जैसे `actions/checkout@v4`), subfolder के लिए `owner/repo/path@ref`, local action के लिए `./path`, या `docker://image:tag` से बुलाते हैं। Inputs `with:` से दिए जाते हैं। Job level पर `uses:` reusable workflow बुलाता है।

---

## 🔴 Problem it Solves
Writing shell for every common task (clone repo, install Node, cache dependencies, log in to a registry, upload artifacts) is repetitive and error-prone. Actions package that logic once, versioned and shared through the Marketplace. You get tested building blocks instead of rewriting `docker login` or `aws configure` scripts. The risk: you are running third-party code with access to your repo and secrets, so pinning and trust matter.

## 🔴 यह क्यों बना? (Hindi)
हर आम काम (repo clone, Node install, dependencies cache, registry login, artifacts upload) के लिए shell लिखना दोहराव वाला और गलती-प्रवण है। Actions वह logic एक बार packaged करते हैं, versioned और Marketplace के ज़रिए साझा। आपको `docker login` या `aws configure` scripts दोबारा लिखने की जगह परीक्षित building blocks मिलते हैं। जोखिम: आप तीसरे पक्ष का code चला रहे हैं जिसे आपके repo और secrets तक पहुँच है, इसलिए pinning और भरोसा मायने रखते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Runner reads `uses: actions/setup-node@v4` and resolves owner/repo + ref (tag, branch, or SHA).
Step 2 → It downloads that repo at that ref into the runner's _actions folder (cached per job).
Step 3 → Reads action.yml (metadata): name, inputs, outputs, `runs.using` (node20 | docker | composite).
Step 4 → Maps `with:` keys to inputs (INPUT_<NAME> env vars) and runs main entrypoint.
Step 5 → JavaScript actions run directly on the runner; Docker actions build/pull an image and run it (Linux only).
Step 6 → Composite actions expand to their inner steps. Outputs flow back via `steps.<id>.outputs`.
Step 7 → After the job: `post:` entrypoints run (e.g., cache save).
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Runner `uses: actions/setup-node@v4` पढ़कर owner/repo + ref (tag, branch या SHA) निकालता है।
Step 2 → उस ref पर वह repo runner के _actions folder में download होता है (job में cache)।
Step 3 → action.yml (metadata) पढ़ता है: name, inputs, outputs, `runs.using` (node20 | docker | composite)।
Step 4 → `with:` keys को inputs (INPUT_<NAME> env vars) से जोड़कर main entrypoint चलाता है।
Step 5 → JavaScript actions सीधे runner पर चलते हैं; Docker actions image build/pull करके चलाते हैं (सिर्फ़ Linux)।
Step 6 → Composite actions अपने अंदरूनी steps में फैल जाते हैं। Outputs `steps.<id>.outputs` से लौटते हैं।
Step 7 → Job के बाद: `post:` entrypoints (जैसे cache save) चलते हैं।
```

Reference forms:

| Form | Example | Use |
|---|---|---|
| Public repo | `actions/checkout@v4` | Marketplace/official |
| Subdirectory | `owner/repo/sub/dir@v1` | Monorepo of actions |
| Local | `./.github/actions/deploy` | Your own, same repo (checkout first) |
| Docker Hub | `docker://alpine:3.20` | Run an image as a step |
| Commit SHA | `actions/checkout@<40-char-sha>` | Immutable pin (best security) |

---

## 🟡 Real World Example
A team's pipeline uses six actions: `actions/checkout`, `actions/setup-node`, `docker/login-action`, `docker/build-push-action`, `aws-actions/configure-aws-credentials`, and one in-house composite action `./.github/actions/notify-slack`. After the `tj-actions/changed-files` supply-chain incident (March 2025) in which a popular action was compromised, they pinned all third-party actions by commit SHA and enabled Dependabot to propose updates weekly.

## 🟡 Real Example Hindi mein
एक team के pipeline में छह actions हैं: `actions/checkout`, `actions/setup-node`, `docker/login-action`, `docker/build-push-action`, `aws-actions/configure-aws-credentials` और एक in-house composite action `./.github/actions/notify-slack`। मार्च 2025 में `tj-actions/changed-files` के supply-chain incident (एक लोकप्रिय action compromise हुआ) के बाद उन्होंने सभी third-party actions commit SHA से pin किए और Dependabot से साप्ताहिक update proposals चालू किए।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/uses-basic.yml
name: Uses Basic                          # workflow name
on: [push]                                # trigger

jobs:
  build:                                    # job id
    runs-on: ubuntu-latest                  # runner
    steps:
      - uses: actions/checkout@v4           # official action: clone the repo (v4 = major tag, example version)
      - uses: actions/setup-node@v4         # official action: install Node
        with:                               # inputs of the action
          node-version: 20                  # which Node to install
          cache: npm                        # enable npm cache
      - run: npm ci                         # normal shell step using the installed Node
      - run: npm test                       # run tests
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/uses-advanced.yml
name: Uses Advanced
on:
  push:
    branches: [main]

permissions:
  contents: read                          # token default
  id-token: write                         # needed for AWS OIDC role assumption

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      # 1) Pin by FULL commit SHA (placeholder shown - replace with the real SHA of the tag you reviewed)
      - uses: actions/checkout@v4         # in production prefer: actions/checkout@<40-char-sha> # v4.x.y

      # 2) Action with outputs
      - id: meta                          # id to read outputs later
        uses: docker/metadata-action@v5   # generates tags and labels
        with:
          images: 123456789012.dkr.ecr.ap-south-1.amazonaws.com/api   # example ECR repo
          tags: |
            type=sha
            type=raw,value=latest,enable={{is_default_branch}}

      # 3) OIDC login to AWS (no long-lived keys)
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-ecr-push   # example role ARN
          aws-region: ap-south-1

      - id: ecr
        uses: aws-actions/amazon-ecr-login@v2   # exposes registry output

      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}      # consume outputs from the metadata action
          labels: ${{ steps.meta.outputs.labels }}

      # 4) Local composite action stored in the same repo (checkout must run first)
      - uses: ./.github/actions/notify-slack
        if: always()
        with:
          status: ${{ job.status }}
          webhook: ${{ secrets.SLACK_WEBHOOK_URL }}
```

```yaml
# .github/actions/notify-slack/action.yml  (the local composite action)
name: Notify Slack                        # action name
description: Post job status to Slack     # shown in docs/UI
inputs:                                   # declared inputs
  status:
    description: Job status
    required: true
  webhook:
    description: Slack webhook URL
    required: true
runs:
  using: composite                        # bundle of steps
  steps:
    - shell: bash                         # composite run steps MUST declare shell
      env:
        STATUS: ${{ inputs.status }}      # pass via env (no injection)
        WEBHOOK: ${{ inputs.webhook }}
      run: |
        curl -sS -X POST -H 'Content-type: application/json' \
          --data "{\"text\":\"Build status: $STATUS\"}" "$WEBHOOK"
```

(YAML parsed locally; real action refs and ECR/role names are examples. Not executed.)

---

## 🟠 My Stack Integration
- **Node.js / React:** `actions/setup-node` + `actions/cache` (or `cache: npm`), `actions/upload-artifact`.
- **FastAPI:** `actions/setup-python` with `cache: pip`.
- **Docker/Nginx/VPS:** `docker/login-action`, `docker/build-push-action`, then an SSH step or `appleboy/ssh-action` (third-party; pin it).
- **AWS:** `aws-actions/configure-aws-credentials` with OIDC role, `amazon-ecr-login`, `amazon-ecs-deploy-task-definition`.

```yaml
# .github/dependabot.yml  - keeps action versions fresh (including pinned SHAs)
version: 2
updates:
  - package-ecosystem: "github-actions"   # watch workflow files
    directory: "/"                        # repo root
    schedule:
      interval: "weekly"                  # one PR per week with bumps
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `uses: some-user/cool-action@main` - a moving branch; maintainer (or attacker) can change code anytime.
✅ Correct: Pin to a full commit SHA (with a `# v1.2.3` comment) for third-party actions; tags for GitHub-official ones at minimum.

❌ Mistake 2: Using a local action without `actions/checkout` first.
✅ Correct: Checkout first, since `./path` is read from the workspace.

❌ Mistake 3: Giving secrets to an unreviewed action.
✅ Correct: Review source, limit `permissions`, pass only needed inputs, prefer official/verified creators.

❌ Mistake 4: Putting `uses:` and `run:` in the same step.
✅ Correct: A step has either `uses` or `run`, not both.

❌ Mistake 5: Using Docker-container actions on Windows/macOS runners.
✅ Correct: Docker actions only run on Linux runners.

---

## 🧠 Tricky Interview Question
You pinned `uses: org/action@v1`. The maintainer's account is compromised and they move the `v1` tag to malicious code. What happens, and how to prevent it?

Answer: Tags are mutable pointers, so your next run executes the malicious code with access to the job's secrets and `GITHUB_TOKEN`. Prevention: pin to the full 40-character commit SHA (immutable), review diffs on Dependabot bumps, restrict allowed actions in org settings ("Allow select actions" / SHA pinning policies), scope `permissions` to least privilege, avoid exposing secrets to steps that do not need them, and use OIDC short-lived credentials.

---

## ⚫ Interview Questions + Answers

Q1: What are the three types of actions?
A1: JavaScript (runs on Node on the runner), Docker container (Linux only, isolated), Composite (a list of steps).

Q2: `uses` vs `run`?
A2: `uses` runs a packaged action; `run` executes a shell command. A step has exactly one of them.

Q3: How do you pass data to an action and read its result?
A3: `with:` for inputs, `steps.<id>.outputs.<name>` for outputs (requires `id:`).

Q4: Where do I find action docs?
A4: In the action repo's README and `action.yml` (inputs/outputs), plus GitHub Marketplace.

Q5: How to restrict which actions your org may use?
A5: Org/repo Settings -> Actions -> General -> allow only GitHub-owned, verified creators, or an explicit allowlist (and require SHA pinning where offered).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A well-maintained action does the task (checkout, setup, login, cache).
- You want shared in-house steps packaged as composite actions.

❌ Avoid when:
- A one-line shell command is simpler and safer than adding a dependency.
- The action is unmaintained or unreviewed and needs powerful secrets.

---

## 📊 Visual Diagram

```
 step: uses: docker/build-push-action@<sha>
        │
        ▼
 runner downloads repo @sha ─► reads action.yml
        │                          inputs: context, push, tags ...
        │ with: {context: ., push: true}
        ▼
   runs main.js (node20)  ──►  talks to Docker/Buildx on runner
        │
        ▼
   outputs: digest, imageid  ──►  ${{ steps.build.outputs.digest }}
        │
        ▼
   post: cleanup (runs after job)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| action | Reusable automation unit | Reusable automation इकाई |
| action.yml | Action's metadata file | Action की metadata file |
| composite action | Action made of steps | Steps से बना action |
| SHA pinning | Fix action to exact commit | सटीक commit पर स्थिर करना |
| Marketplace | Directory of actions | Actions की सूची |
| supply-chain attack | Compromise via dependency | Dependency के ज़रिए हमला |

---

## ⚡ 3-Line Summary
English: `uses:` runs a packaged action with `with:` inputs and returns outputs.
English: Types: JavaScript, Docker, composite; local, remote, or Docker Hub references.
English: Pin third-party actions by commit SHA and limit permissions.
Hindi: `uses:` `with:` inputs के साथ packaged action चलाता है और outputs लौटाता है।
Hindi: प्रकार: JavaScript, Docker, composite; local, remote या Docker Hub reference।
Hindi: Third-party actions को commit SHA से pin करें और permissions सीमित रखें।

---

## ➡️ Next Topic
**255. run: (Shell command)** - the other kind of step: running shell commands, multi-line scripts and choosing the shell.
