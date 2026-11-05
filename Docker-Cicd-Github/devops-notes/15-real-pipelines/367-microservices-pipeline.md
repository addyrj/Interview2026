---

# 367. Microservices Pipeline
# हिंदी में: Microservices Pipeline

---

## 🔵 Simple Definition (English)
A microservices pipeline gives every service its own build, test and deploy flow, but shares the logic through a reusable workflow. Each service ships independently with its own image tag, while contract tests and a shared template keep the system consistent.

## 🔵 सरल परिभाषा (Hindi)
Microservices pipeline में हर service का अपना build, test और deploy flow होता है, लेकिन logic एक reusable workflow से share होता है। हर service अपने image tag के साथ स्वतंत्र रूप से ship होती है, और contract tests तथा shared template पूरे system को consistent रखते हैं।

---

## 🔴 Problem it Solves
- Copy-pasting the same 200-line YAML into 12 repos; a fix must be applied 12 times.
- One slow service blocks releases of others.
- Services break each other through silent API changes.
- No consistent security scan or tagging rules.

## 🔴 यह क्यों बना? (Hindi)
- वही 200 लाइन YAML 12 repos में copy-paste; एक fix 12 बार करना।
- एक धीमी service दूसरों की release रोकती है।
- Silent API बदलाव से services एक-दूसरे को तोड़ती हैं।
- Scan और tagging के नियम consistent नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Platform repo holds reusable workflow: .github/workflows/service-ci.yml (on: workflow_call)
Step 2 → Each service repo has a 10-line caller workflow with inputs
Step 3 → Reusable workflow: test -> build -> scan -> push (tag = semver or SHA)
Step 4 → Consumer-driven contract tests verify API compatibility
Step 5 → Deploy to staging automatically, to production after approval
Step 6 → Each service rolls back independently by tag
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Platform repo में reusable workflow: .github/workflows/service-ci.yml (on: workflow_call)
Step 2 → हर service repo में 10 लाइन का caller workflow, inputs के साथ
Step 3 → Reusable workflow: test -> build -> scan -> push (tag = semver या SHA)
Step 4 → Consumer-driven contract tests API compatibility जाँचते हैं
Step 5 → Staging पर automatic deploy, production पर approval के बाद
Step 6 → हर service tag से स्वतंत्र रूप से rollback होती है
```

---

## 🟡 Real World Example
An Uber-style ride platform has `pricing`, `dispatch`, `payments` and `notifications` services. The platform team maintains one reusable workflow. When they added Trivy scanning, all four services got it in one commit. When `pricing` changed a JSON field, its contract test against `dispatch` failed in CI, so the break never reached staging.

## 🟡 Real Example Hindi mein
Uber जैसे ride platform में `pricing`, `dispatch`, `payments` और `notifications` services हैं। Platform team एक reusable workflow रखती है। Trivy scanning जोड़ी तो चारों services को एक ही commit में मिल गई। `pricing` ने एक JSON field बदला तो `dispatch` के खिलाफ उसका contract test CI में fail हुआ, इसलिए break staging तक नहीं पहुँचा।

---

## 💻 Code / Config Example — Basic

```yaml
# Service repo: .github/workflows/ci.yml  (the small caller)
name: Service CI                       # Caller name
on:
  push:
    branches: [main]
jobs:
  call-template:                       # Job that calls the reusable workflow
    uses: my-org/platform/.github/workflows/service-ci.yml@v1   # Pin to a tag
    with:                              # Inputs defined by the template
      service-name: payments
      language: python
    secrets: inherit                   # Pass repo secrets to the template
```

## 💻 Code / Config Example — Advanced

```yaml
# Platform repo: .github/workflows/service-ci.yml  (reusable)
name: Reusable Service CI
on:
  workflow_call:                       # Makes this workflow callable
    inputs:
      service-name:
        required: true
        type: string                   # Used in image name
      language:
        required: false
        type: string
        default: node                  # node or python
      deploy-staging:
        required: false
        type: boolean
        default: true
    outputs:
      image-tag:
        description: Built image tag
        value: ${{ jobs.build.outputs.tag }}   # Expose to caller
    secrets:
      VPS_SSH_KEY:
        required: false
permissions:
  contents: read
  packages: write
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - if: inputs.language == 'node'
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - if: inputs.language == 'node'
        run: npm ci && npm test
      - if: inputs.language == 'python'
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - if: inputs.language == 'python'
        run: pip install -r requirements.txt pytest && pytest -q
  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.meta.outputs.tag }}
    steps:
      - uses: actions/checkout@v4
      - id: meta
        run: echo "tag=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository_owner }}/${{ inputs.service-name }}:${{ steps.meta.outputs.tag }}
          cache-from: type=gha,scope=${{ inputs.service-name }}
          cache-to: type=gha,scope=${{ inputs.service-name }},mode=max
  staging:
    if: inputs.deploy-staging
    needs: build
    runs-on: ubuntu-latest
    environment: staging               # Separate secrets and approvals
    steps:
      - run: echo "Deploy ${{ inputs.service-name }}:${{ needs.build.outputs.tag }} to staging (replace with real deploy)"
```

---

## 🟠 My Stack Integration
On a single VPS or small AWS setup you can run each service as its own compose project behind one Nginx:

```nginx
# /etc/nginx/conf.d/services.conf  (not tested with nginx -t here)
upstream payments { server 127.0.0.1:8101; }       # payments container
upstream pricing  { server 127.0.0.1:8102; }       # pricing container
server {
  listen 80;
  location /payments/ { proxy_pass http://payments/; }   # Route by path
  location /pricing/  { proxy_pass http://pricing/;  }
}
```

```yaml
# Per-service deploy script input idea: each service owns /opt/<service>/compose.yml
# so "payments" can be redeployed without touching "pricing".
```

Reusable workflows can be nested only to a limited depth and cannot call workflows that need `GITHUB_TOKEN` permissions beyond what the caller grants. Check current GitHub limits.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Calling the template with `@main`.
✅ Correct: Pin to a tag (`@v1`) so template changes do not break all services unexpectedly.

❌ Mistake 2: Shared database between services.
✅ Correct: Each service owns its data; communicate via APIs or events.

❌ Mistake 3: Forgetting `secrets: inherit` or explicit secrets.
✅ Correct: Reusable workflows do not see caller secrets by default.

❌ Mistake 4: Deploying all services together "for safety".
✅ Correct: Independent deploys with backward-compatible APIs.

Security: least-privilege tokens per service, image scanning in the template, separate staging and production environments.

---

## 🧠 Tricky Interview Question
Service A deployed fine and its tests pass, yet Service B starts failing in production. How could your pipeline have prevented it?

Answer: A changed its response contract and B depended on it. Add consumer-driven contract tests (e.g. Pact) run on A's pipeline using B's expectations, plus API versioning and canary deploys. Unit tests alone cannot see cross-service breaks.

---

## ⚫ Interview Questions + Answers

Q1: Reusable workflow vs composite action?
A1: A reusable workflow is a full workflow with jobs, called by `uses:` at job level. A composite action bundles steps inside one job.

Q2: Why version the template?
A2: Controlled rollout of pipeline changes, and an easy rollback if the template breaks.

Q3: How do you tag images?
A3: Git SHA for traceability, semver on releases, and never rely on `latest`.

Q4: How do you deploy to production safely?
A4: GitHub `environment` with required reviewers, health checks, canary or blue/green.

Q5: Biggest pitfall of microservices CI/CD?
A5: Distributed breakage: contract drift, version skew, and observability gaps.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple teams own independently releasable services.

❌ Avoid when:
- A small team with one app; a modular monolith with one pipeline is simpler.

---

## 📊 Visual Diagram
```
 platform repo:  service-ci.yml (workflow_call, v1)
                        ^   ^   ^
        +---------------+   |   +----------------+
   payments repo       pricing repo         dispatch repo
   (caller 10 lines)   (caller)             (caller)
        |                   |                    |
    test->build->scan->push GHCR (own tag)  --> staging --> approval --> prod
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| workflow_call | Trigger to make workflow reusable | Workflow को reusable बनाने वाला trigger |
| Contract test | Verifies API agreement | API समझौते की जाँच |
| Canary | Release to small traffic first | पहले थोड़े traffic पर release |
| Environment | Named deploy target with rules | Rules वाला नामित deploy target |
| Version skew | Services on different versions | Services के अलग versions |

---

## ⚡ 3-Line Summary
English: One reusable workflow, many tiny callers.
English: Each service builds, scans and deploys independently.
English: Contract tests protect against cross-service breaks.
Hindi: एक reusable workflow, कई छोटे callers।
Hindi: हर service स्वतंत्र रूप से build, scan और deploy होती है।
Hindi: Contract tests cross-service breaks से बचाते हैं।

---

## ➡️ Next Topic
368. Database Migration Pipeline: change schemas safely as part of a release.
