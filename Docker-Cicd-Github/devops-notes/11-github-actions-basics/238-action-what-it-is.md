# 238. Action — What it is
# हिंदी में: Action — यह क्या है

---

## 🔵 Simple Definition (English)
An **action** is a reusable, packaged piece of automation that you call from a step with `uses:`. Examples: `actions/checkout` downloads your code, `actions/setup-node` installs Node.js, `docker/build-push-action` builds and pushes images. Actions come from the Marketplace, other repos, or your own repo.

## 🔵 सरल परिभाषा (Hindi)
**Action** automation का reusable, packaged टुकड़ा है जिसे आप step में `uses:` से बुलाते हैं। उदाहरण: `actions/checkout` आपका code लाता है, `actions/setup-node` Node.js install करता है, `docker/build-push-action` image build और push करता है। Actions Marketplace, दूसरी repos या आपकी अपनी repo से आते हैं।

---

## 🔴 Problem it Solves
Every team was copy-pasting the same 30 lines of bash to install Node, cache modules, log in to AWS or send Slack messages. Each copy had slightly different bugs, and nobody upgraded them.

Actions let experts write that logic once, version it (`@v4`), and everyone reuses it with a two-line `uses:` and a few `with:` inputs.

## 🔴 यह क्यों बना? (Hindi)
हर team वही 30 lines की bash बार-बार copy-paste करती थी: Node install, modules cache, AWS login या Slack message। हर copy में थोड़े अलग bugs थे और कोई उन्हें upgrade नहीं करता था।

Actions से expert वह logic एक बार लिखता है, version देता है (`@v4`) और सब लोग दो line के `uses:` और कुछ `with:` inputs से दोबारा इस्तेमाल करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Step says: uses: owner/repo@ref   (e.g. actions/checkout@v4)
Step 2 → Runner downloads that repo at that ref (tag, branch or commit SHA)
Step 3 → Runner reads action.yml (metadata: inputs, outputs, runs)
Step 4 → Depending on `runs.using`, it executes the action:
           - node20      -> JavaScript action (fast, runs directly on the runner)
           - docker      -> Docker container action (Linux runners only)
           - composite   -> a bundle of steps (run + uses)
Step 5 → Inputs come from `with:`; they become INPUT_<NAME> env vars
Step 6 → Action writes outputs; later steps read steps.<id>.outputs.<name>
```

Three action types:
- **JavaScript**: runs in Node on the runner; fastest, works on Linux/macOS/Windows.
- **Docker container**: any language, packaged in an image; slower start, Linux only.
- **Composite**: shell commands and other actions combined in YAML; easiest to author.

Where `uses:` can point: `owner/repo@ref`, `owner/repo/path@ref`, `./local/path`, `docker://image:tag`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Step लिखता है: `uses: owner/repo@ref` (जैसे `actions/checkout@v4`)।
Step 2 → Runner उस repo को उस ref (tag, branch या commit SHA) पर download करता है।
Step 3 → Runner `action.yml` पढ़ता है (inputs, outputs, runs की metadata)।
Step 4 → `runs.using` के अनुसार चलाता है: `node20` (JavaScript, तेज़), `docker` (container, सिर्फ Linux), `composite` (steps का bundle)।
Step 5 → Inputs `with:` से आते हैं और `INPUT_<NAME>` env vars बनते हैं।
Step 6 → Action outputs लिखता है; आगे के steps `steps.<id>.outputs.<name>` से पढ़ते हैं।

तीन प्रकार: **JavaScript** (runner पर Node में, सबसे तेज़), **Docker** (किसी भी भाषा में, image में पैक, धीमी शुरुआत), **Composite** (YAML में commands और actions का मेल, लिखना सबसे आसान)।

---

## 🟡 Real World Example
A payments team uses 5 actions in its workflow: `actions/checkout`, `actions/setup-node`, `aws-actions/configure-aws-credentials` (logs into AWS using OIDC, no stored keys), `docker/build-push-action`, and an in-house composite action `./.github/actions/notify-slack` that posts the deployment result. When Node 20 got a security patch, they changed nothing: `setup-node` fetches the latest 20.x. When they wanted to harden security, they replaced `@v4` tags by full commit SHAs after reviewing the code.

## 🟡 Real Example Hindi mein
एक payments team अपने workflow में 5 actions इस्तेमाल करती है: `actions/checkout`, `actions/setup-node`, `aws-actions/configure-aws-credentials` (OIDC से AWS login, कोई stored keys नहीं), `docker/build-push-action`, और अपना composite action `./.github/actions/notify-slack` जो deployment का नतीजा post करता है। जब Node 20 को security patch मिला तो कुछ बदलना नहीं पड़ा: `setup-node` नवीनतम 20.x ले आता है। Security कड़ी करने के लिए उन्होंने code review के बाद `@v4` tags की जगह पूरे commit SHA लगा दिए।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/actions-basic.yml
name: Actions Basic                   # Workflow name
on: [push]                            # Trigger
jobs:
  use-actions:
    runs-on: ubuntu-latest            # Runner
    steps:
      - uses: actions/checkout@v4     # Official action, major version tag (example version)
      - uses: actions/setup-node@v4   # Official action to install Node
        with:                         # Inputs for the action
          node-version: 20            # Which Node to install
          cache: npm                  # Enable npm cache
      - id: ver                       # id so we can read outputs
        run: echo "v=$(node -v)" >> "$GITHUB_OUTPUT"   # Save Node version
      - run: echo "Node is ${{ steps.ver.outputs.v }}" # Print it
```

Your own composite action (reusable inside your repo):

```yaml
# .github/actions/notify/action.yml  (file name must be action.yml or action.yaml)
name: Notify                          # Name of the action
description: Print a deployment message   # Required description
inputs:                               # Declared inputs
  message:
    description: Text to print        # Input description
    required: true                    # Caller must pass it
runs:
  using: composite                    # Composite action type
  steps:
    - shell: bash                     # Composite run steps MUST set shell
      run: echo "NOTIFY -> ${{ inputs.message }}"   # Use the input
```

Call it like this (after checkout, because local actions live in the repo):

```yaml
# snippet inside a job's steps (full workflow shown in Advanced below)
      - uses: actions/checkout@v4     # Required so ./.github/actions exists on the runner
      - uses: ./.github/actions/notify   # Local path, no version needed
        with:
          message: "Build finished"   # Pass the input
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/actions-advanced.yml
name: Actions Advanced                # Docker build/push using well-known actions
on:
  push:
    branches: [main]
permissions:
  contents: read                      # Read repo
  packages: write                     # Needed to push to GitHub Container Registry
jobs:
  image:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4     # Get code
      - uses: docker/setup-buildx-action@v3   # Enable Buildx (example major version)
      - uses: docker/login-action@v3  # Log in to registry
        with:
          registry: ghcr.io           # GitHub Container Registry
          username: ${{ github.actor }}   # Current user
          password: ${{ secrets.GITHUB_TOKEN }}   # Auto-created token, no manual secret
      - id: meta                      # Generate tags and labels
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}   # Must be lowercase; adjust if your org has capitals
          tags: |
            type=sha
            type=raw,value=latest,enable={{is_default_branch}}
      - uses: docker/build-push-action@v6   # Build and push
        with:
          context: .                  # Build context
          push: true                  # Push after build
          tags: ${{ steps.meta.outputs.tags }}      # Tags from metadata step
          labels: ${{ steps.meta.outputs.labels }}  # OCI labels
          cache-from: type=gha        # Reuse layers from GitHub cache
          cache-to: type=gha,mode=max # Save layers for next time
      - uses: ./.github/actions/notify   # Your composite action (see Basic above)
        with:
          message: "Pushed ${{ github.sha }}"
```

Action versions above are examples; check each action's releases page and update.

---

## 🟠 My Stack Integration
Actions you will use again and again for Node.js / FastAPI / React / AWS / VPS:

| Need | Action |
|---|---|
| Get code | `actions/checkout` |
| Node / Python toolchain | `actions/setup-node`, `actions/setup-python` |
| Cache | built into setup actions or `actions/cache` |
| Docker image | `docker/build-push-action` |
| AWS login (OIDC) | `aws-actions/configure-aws-credentials` |
| ECR login | `aws-actions/amazon-ecr-login` |
| SSH to VPS | `appleboy/ssh-action` (third-party) or plain `ssh` in a `run:` step |

```yaml
# snippet: AWS OIDC login (no long-lived keys). Role must trust GitHub's OIDC provider.
permissions:
  id-token: write                     # Allows requesting the OIDC token
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@v4   # Example version
    with:
      role-to-assume: arn:aws:iam::123456789012:role/gha-deploy   # Placeholder ARN
      aws-region: ap-south-1          # Mumbai region
```

Security: an action runs with access to your job's secrets and token. Prefer official (`actions/*`, `docker/*`, `aws-actions/*`) or well-reviewed ones, pin to a **full commit SHA** for high-risk pipelines, enable Dependabot for `github-actions`, and avoid unmaintained actions (supply-chain attacks such as tj-actions/changed-files in 2025 showed mutable tags can be hijacked).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `uses: some/action@main` (moving branch) in production.
✅ Correct: Pin to a version tag, or better a full SHA with a comment of the version.

❌ Mistake 2: Using a local action without `actions/checkout` first.
✅ Correct: Checkout first so `./.github/actions/...` exists.

❌ Mistake 3: Forgetting `shell:` in composite action `run` steps.
✅ Correct: Always set `shell: bash` there.

❌ Mistake 4: Passing secrets to random third-party actions.
✅ Correct: Read the source, limit `permissions`, scope secrets to environments.

---

## 🧠 Tricky Interview Question
"Your team pinned `uses: vendor/deploy-action@v2`. One morning production deploys start leaking secrets, though nobody changed your repo. How is this possible and how do you prevent it?"

Answer: Git tags are mutable. The action owner (or an attacker who compromised the account) can move `v2` to a malicious commit, and your workflow pulls it automatically. Prevention: pin to the full 40-character commit SHA (`uses: vendor/deploy-action@<sha> # v2.1.0`), let Dependabot propose updates as PRs, restrict allowed actions in org settings ("allow actions created by GitHub, verified creators, or specific list"), and use short-lived OIDC credentials so leaked secrets are less valuable.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a step and an action?
A1: A step is a slot in a job. An action is reusable code you invoke from a step with `uses:`. A step can also be a plain `run:` command with no action.

Q2: What three types of actions exist?
A2: JavaScript, Docker container and composite.

Q3: What file defines an action?
A3: `action.yml` (or `action.yaml`) at the action's root, with name, description, inputs, outputs and `runs`.

Q4: How do you pass inputs and read outputs?
A4: Inputs via `with:`; outputs via `steps.<id>.outputs.<name>` (the step needs an `id`).

Q5: Reusable workflow vs composite action?
A5: A reusable workflow (`workflow_call`) is a whole workflow with jobs, called at job level via `jobs.<id>.uses`. A composite action is a bundle of steps called at step level inside one job.

---

## 🔷 When to Use + When Not to Use
✅ Use an action when:
- A well-maintained one exists (checkout, setup, login, cache).
- You repeat the same steps in several workflows (make a composite action).

❌ Avoid when:
- It is one simple command (`npm ci`): a `run:` is clearer and safer.
- The action is unmaintained, unverified or asks for broad secrets.

---

## 📊 Visual Diagram

```
 step:  uses: actions/setup-node@v4
              |
              v
   runner downloads repo actions/setup-node @ v4
              |
              v
        reads action.yml
        +-----------------------------+
        | inputs:  node-version, cache|
        | outputs: node-version       |
        | runs:    using: node20      |
        +-----------------------------+
              |
              v
       executes dist/index.js on the runner
              |
              v
   results -> steps.<id>.outputs.*   +  PATH updated
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Action | Reusable step package | reusable step पैकेज |
| action.yml | Action metadata file | action की metadata file |
| Composite action | Steps bundled in YAML | YAML में steps का bundle |
| Marketplace | Public catalog of actions | actions की सार्वजनिक सूची |
| Pinning | Fixing to exact version/SHA | सटीक version/SHA पर बाँधना |
| Supply chain attack | Compromising a dependency | dependency के ज़रिए हमला |

---

## ⚡ 3-Line Summary
English: An action is reusable automation called with `uses:`, defined by `action.yml`.
It can be JavaScript, Docker or composite, and takes inputs via `with:`.
Pin versions (ideally SHAs) because actions run with access to your secrets.

Hindi: Action `uses:` से बुलाई जाने वाली reusable automation है, जो `action.yml` से परिभाषित होती है।
यह JavaScript, Docker या composite हो सकती है और inputs `with:` से लेती है।
Versions (बेहतर हो SHA) pin करें क्योंकि actions आपके secrets तक पहुँच के साथ चलती हैं।

---

## ➡️ Next Topic
**239. Runner — What it is** — the machine that actually executes your jobs and steps.

---
