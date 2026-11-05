# 248. workflow_call Event
# हिंदी में: workflow_call Event (Reusable Workflows)

---

## 🔵 Simple Definition (English)
`workflow_call` turns a workflow into a **reusable workflow**: a function that other workflows can call with `uses: org/repo/.github/workflows/file.yml@ref`. It declares typed `inputs`, `secrets` and `outputs`. The caller passes values, the called workflow runs its own jobs, and results come back as outputs.

## 🔵 सरल परिभाषा (Hindi)
`workflow_call` किसी workflow को **reusable workflow** बना देता है: एक function जिसे दूसरे workflows `uses: org/repo/.github/workflows/file.yml@ref` से बुला सकते हैं। यह typed `inputs`, `secrets` और `outputs` घोषित करता है। Caller values देता है, बुलाया गया workflow अपने jobs चलाता है, और नतीजे outputs के रूप में लौटते हैं।

---

## 🔴 Problem it Solves
With 15 microservices, teams copy-paste the same 80-line CI YAML into every repo. A fix (new Node version, new scan step) must be repeated 15 times and the copies drift. Reusable workflows centralize the pipeline in one repo: change once, all services get it (or pin versions to roll out gradually). It also standardizes security and compliance steps.

## 🔴 यह क्यों बना? (Hindi)
15 microservices में team वही 80 लाइन का CI YAML हर repo में copy-paste करती है। कोई fix (नया Node version, नया scan step) 15 बार करना पड़ता है और copies अलग-अलग हो जाती हैं। Reusable workflows pipeline को एक repo में केंद्रित करते हैं: एक बार बदलो, सभी services को मिल जाए (या versions pin करके धीरे-धीरे rollout)। इससे security और compliance steps भी एक जैसे रहते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Platform repo has .github/workflows/node-ci.yml with `on: workflow_call` + inputs/secrets/outputs.
Step 2 → A service repo workflow has a job with `uses: my-org/platform/.github/workflows/node-ci.yml@v1`.
Step 3 → Caller passes `with:` (inputs) and `secrets:` (or `secrets: inherit`).
Step 4 → GitHub runs the called workflow as its own set of jobs; the caller job shows as a group.
Step 5 → Called workflow publishes `outputs` (e.g., image tag) via `on.workflow_call.outputs`.
Step 6 → Caller reads them with `${{ needs.<job>.outputs.<name> }}` in later jobs.
Step 7 → Limits: nesting up to 4 levels deep (caller + 3 levels, see docs for current), max 20 unique reusable workflows per file (current docs); env/context of caller is NOT inherited automatically.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Platform repo में .github/workflows/node-ci.yml जिसमें `on: workflow_call` + inputs/secrets/outputs हों।
Step 2 → Service repo के workflow में job: `uses: my-org/platform/.github/workflows/node-ci.yml@v1`।
Step 3 → Caller `with:` (inputs) और `secrets:` (या `secrets: inherit`) देता है।
Step 4 → GitHub बुलाए गए workflow को अपने jobs के रूप में चलाता है; caller job एक group की तरह दिखता है।
Step 5 → Called workflow `on.workflow_call.outputs` से outputs देता है (जैसे image tag)।
Step 6 → Caller अगले jobs में उन्हें `${{ needs.<job>.outputs.<name> }}` से पढ़ता है।
Step 7 → सीमाएँ: nesting की गहराई सीमित (current docs देखें), caller का env/context अपने-आप inherit नहीं होता।
```

---

## 🟡 Real World Example
A company has 12 Node.js APIs and 3 FastAPI services. The platform team owns `platform-workflows` with `node-ci.yml`, `python-ci.yml`, and `docker-publish.yml`. Each service workflow is 15 lines: it calls CI, then calls docker-publish with its image name. When security asks for Trivy scanning, the platform team adds it in `docker-publish.yml`, tags `v2`, and teams upgrade `@v1` to `@v2` service by service.

## 🟡 Real Example Hindi mein
एक कंपनी के 12 Node.js APIs और 3 FastAPI services हैं। Platform team के `platform-workflows` repo में `node-ci.yml`, `python-ci.yml` और `docker-publish.yml` हैं। हर service का workflow 15 लाइन का है: CI बुलाता है, फिर अपने image name के साथ docker-publish बुलाता है। Security Trivy scan माँगे तो platform team `docker-publish.yml` में जोड़कर `v2` tag करती है, और teams `@v1` से `@v2` एक-एक करके बदलती हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# ---- File A: .github/workflows/reusable-test.yml (the CALLED workflow) ----
name: Reusable Test                       # name of the reusable workflow

on:
  workflow_call:                          # makes this workflow callable
    inputs:                               # typed parameters from the caller
      node-version:                       # input key
        required: false                   # optional
        type: string                      # string | number | boolean
        default: "20"                     # used when caller omits it

jobs:
  test:                                   # job id
    runs-on: ubuntu-latest                # runner
    steps:
      - uses: actions/checkout@v4         # get caller's code (checkout uses the CALLER repo by default)
      - uses: actions/setup-node@v4       # install Node
        with:
          node-version: ${{ inputs.node-version }}   # use the input
      - run: npm ci && npm test           # install and test
```

```yaml
# ---- File B: .github/workflows/ci.yml (the CALLER workflow, same repo) ----
name: CI                                  # caller name
on:
  push:
    branches: [main]                      # run on pushes to main
jobs:
  call-test:                              # job that calls the reusable workflow
    uses: ./.github/workflows/reusable-test.yml   # same-repo path (no @ref needed)
    with:
      node-version: "20"                  # pass input
```

## 💻 Code / Config Example — Advanced

```yaml
# platform-workflows/.github/workflows/docker-publish.yml  (CALLED, in a shared repo)
name: Docker Publish

on:
  workflow_call:
    inputs:
      image-name:                         # e.g. ghcr.io/acme/orders-api
        required: true
        type: string
      context:                            # docker build context
        required: false
        type: string
        default: "."
      push:                               # allow dry runs on PRs
        required: false
        type: boolean
        default: true
    secrets:
      registry-token:                     # token to push (declared secret)
        required: false                   # optional, GITHUB_TOKEN used if not given
    outputs:
      tag:                                # value returned to the caller
        description: "Primary image tag"
        value: ${{ jobs.build.outputs.tag }}   # map from job output

permissions:
  contents: read                          # default minimal rights
  packages: write                         # needed to push to GHCR (caller must allow this too)

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.meta.outputs.version }}   # expose step output at job level
    steps:
      - uses: actions/checkout@v4         # source
      - id: meta                          # id so outputs can be referenced
        uses: docker/metadata-action@v5   # generate tags/labels
        with:
          images: ${{ inputs.image-name }}
          tags: |
            type=sha                      # tag like sha-abc1234
            type=ref,event=branch         # branch name tag
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        if: inputs.push                   # login only when pushing
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.registry-token || secrets.GITHUB_TOKEN }}   # fallback to built-in token
      - uses: docker/build-push-action@v6
        with:
          context: ${{ inputs.context }}
          push: ${{ inputs.push }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

```yaml
# orders-api/.github/workflows/pipeline.yml  (CALLER in a service repo)
name: Pipeline
on:
  push:
    branches: [main]
permissions:
  contents: read
  packages: write                         # caller must grant at least what the callee asks for
jobs:
  ci:
    uses: acme/platform-workflows/.github/workflows/node-ci.yml@v1   # pinned tag (example)
    with:
      node-version: "20"
  publish:
    needs: ci                             # run after CI passes
    uses: acme/platform-workflows/.github/workflows/docker-publish.yml@v1
    with:
      image-name: ghcr.io/acme/orders-api
    secrets: inherit                      # pass all caller secrets (same org only)
  deploy:
    needs: publish
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploy tag ${{ needs.publish.outputs.tag }}"   # consume the callee output
```

(YAML parsed locally; reusable-workflow resolution is only verifiable on GitHub.)

---

## 🟠 My Stack Integration
- **Node.js / FastAPI:** one `node-ci.yml` and one `python-ci.yml`, called by each service.
- **React:** reusable `static-build.yml` that builds and uploads `dist` to S3/Nginx.
- **VPS / Nginx:** reusable `deploy-vps.yml` taking `host`, `tag`, `compose-path` inputs and `ssh-key` secret.
- **AWS:** reusable workflow with `permissions: id-token: write` for OIDC; callers must also allow `id-token: write`.

```yaml
# Minimal VPS-deploy caller
jobs:
  deploy:
    uses: acme/platform-workflows/.github/workflows/deploy-vps.yml@v1   # shared deploy logic
    with:
      host: app.example.com               # target
      tag: ${{ github.sha }}              # version
    secrets:
      ssh-key: ${{ secrets.VPS_SSH_KEY }} # explicit secret passing
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `uses:` with `runs-on:` in the same job (a caller job cannot have steps or runs-on).
✅ Correct: Caller job = `uses` + `with` + `secrets` (+ `needs`, `if`, `permissions`) only.

❌ Mistake 2: Referencing `@main` of a shared repo - a change can break all 20 repos at once.
✅ Correct: Pin to tags (`@v1`) or full commit SHA.

❌ Mistake 3: Forgetting that secrets are not inherited automatically.
✅ Correct: Declare under `on.workflow_call.secrets` and pass in `secrets:`, or use `secrets: inherit` inside the same org/enterprise.

❌ Mistake 4: Confusing with composite actions.
✅ Correct: Reusable workflow = whole jobs (own runners); composite action = a bundle of steps inside one job.

---

## 🧠 Tricky Interview Question
A reusable workflow declares `permissions: packages: write`, but the caller workflow only has `contents: read`. Does the push work?

Answer: No. The GITHUB_TOKEN permissions of a called workflow can only be maintained or reduced by the callee, never elevated beyond what the caller grants. Add `packages: write` to the caller (workflow or job level) too, otherwise login/push fails with 403.

---

## ⚫ Interview Questions + Answers

Q1: Reusable workflow vs composite action?
A1: Reusable: whole jobs, own runner, can use secrets/matrix, called at job level. Composite: steps only, runs in the caller's job and runner, called at step level.

Q2: How does a callee return data?
A2: `on.workflow_call.outputs` mapped to job outputs; caller reads `needs.<job>.outputs.<name>`.

Q3: Can you call a private repo's reusable workflow?
A3: Yes, if that repo's Actions settings allow access from other repos in the org/user ("Accessible from repositories in the organization").

Q4: Are env variables passed through?
A4: No; use `inputs`. The `env` context of the caller is not available in the called workflow.

Q5: What is `github.event_name` in the callee?
A5: The caller's event (for example `push`), because the context is inherited from the caller.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many repos share the same CI/CD pipeline.
- You need central governance (scan, lint, approvals).

❌ Avoid when:
- One repo, one tiny pipeline - extra indirection costs readability.
- You only need to share a few steps (use a composite action).

---

## 📊 Visual Diagram

```
 service repo A ──┐  uses: platform/node-ci.yml@v1
 service repo B ──┼────────────────────────────┐
 service repo C ──┘   with: node-version=20    │
                                               ▼
                       ┌──────────── platform-workflows repo ────────────┐
                       │  on: workflow_call (inputs, secrets, outputs)   │
                       │   job build -> job scan -> job publish          │
                       └─────────────────────┬───────────────────────────┘
                                             │ outputs: tag
                                             ▼
                        caller: needs.publish.outputs.tag -> deploy job
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| reusable workflow | Workflow callable by others | दूसरों द्वारा बुलाने योग्य workflow |
| caller | Workflow that uses another | बुलाने वाला workflow |
| callee | The reusable workflow itself | बुलाया गया workflow |
| secrets: inherit | Pass all caller secrets | सभी secrets आगे देना |
| pinning | Using fixed tag/SHA | निश्चित tag/SHA प्रयोग करना |
| composite action | Reusable group of steps | Steps का reusable समूह |

---

## ⚡ 3-Line Summary
English: `workflow_call` makes a workflow callable with inputs, secrets and outputs.
English: Centralizes CI/CD across repos; pin versions and mind permissions.
English: Caller job uses `uses:` only; not steps.
Hindi: `workflow_call` workflow को inputs, secrets और outputs के साथ बुलाने योग्य बनाता है।
Hindi: कई repos का CI/CD एक जगह; versions pin करें और permissions का ध्यान रखें।
Hindi: Caller job में सिर्फ़ `uses:` होता है, steps नहीं।

---

## ➡️ Next Topic
**249. release Event** - trigger pipelines when a GitHub Release is published (production builds, changelog, artifacts).
