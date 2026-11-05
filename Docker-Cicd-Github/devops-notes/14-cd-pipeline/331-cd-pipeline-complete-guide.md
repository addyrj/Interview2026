# 331. CD Pipeline — Complete Guide
# हिंदी में: CD Pipeline — पूरी गाइड

---

## 🔵 Simple Definition (English)
**CD** means **Continuous Delivery** (every green build is ready to release, a human clicks deploy) or **Continuous Deployment** (every green build is deployed automatically). A CD pipeline takes the tested code, builds an immutable artifact (Docker image), pushes it to a registry, deploys it to servers, checks health and rolls back if it fails.

## 🔵 सरल परिभाषा (Hindi)
**CD** का मतलब **Continuous Delivery** (हर green build release के लिए तैयार, इंसान deploy दबाता है) या **Continuous Deployment** (हर green build अपने आप deploy)। CD pipeline tested code से immutable artifact (Docker image) बनाती है, registry में push करती है, servers पर deploy करती है, health जाँचती है और fail होने पर rollback करती है।

---

## 🔴 Problem it Solves
Manual deployment means SSH into the VPS, `git pull`, `npm install`, restart and hope. Each person does it slightly differently; steps are forgotten; nobody knows which version runs in production; a Friday-night release takes 2 hours and leaves downtime. CD makes every release scripted, repeatable, auditable and reversible.

## 🔴 यह क्यों बना? (Hindi)
Manual deployment यानी VPS में SSH, `git pull`, `npm install`, restart और उम्मीद। हर व्यक्ति थोड़ा अलग करता है; steps भूल जाते हैं; किसी को पता नहीं production में कौन सा version चल रहा है; शुक्रवार रात की release 2 घंटे लेती है और downtime छोड़ती है। CD हर release को scripted, दोहराने योग्य, audit योग्य और वापस लेने योग्य बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → CI passes on main (tests, lint, scan)
Step 2 → Build Docker image tagged with the commit SHA (immutable, never :latest only)
Step 3 → Push image to a registry (GHCR / Docker Hub / ECR)
Step 4 → Deploy to staging automatically; run smoke tests
Step 5 → (Delivery) wait for manual approval, (Deployment) continue automatically
Step 6 → Deploy to production: pull image on VPS, `docker compose up -d`, run migrations
Step 7 → Health check via Nginx; on failure roll back to previous SHA
Step 8 → Notify the team (Slack/email) and record the deployed version
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → main पर CI pass (tests, lint, scan)
Step 2 → Commit SHA के tag के साथ Docker image build (immutable, सिर्फ :latest नहीं)
Step 3 → Image को registry (GHCR / Docker Hub / ECR) में push
Step 4 → Staging पर अपने आप deploy; smoke tests चलाओ
Step 5 → (Delivery) manual approval का इंतज़ार, (Deployment) अपने आप आगे
Step 6 → Production deploy: VPS पर image pull, `docker compose up -d`, migrations
Step 7 → Nginx के ज़रिए health check; fail हो तो पिछले SHA पर rollback
Step 8 → टीम को सूचना (Slack/email) और deployed version का record
```

---

## 🟡 Real World Example
A Swiggy-like delivery-tracking service deploys 15 times a day. Each merge to main builds `ghcr.io/acme/tracker:3f9c2ab`, rolls it to staging, runs a 30-second smoke test, then (after a one-click approval) updates the production VPS. When a bad release raised the 5xx rate, the on-call engineer re-ran the deploy workflow for the previous SHA and was back to normal in 90 seconds, with no SSH and no guesswork.

## 🟡 Real Example Hindi mein
Swiggy-जैसी delivery-tracking service दिन में 15 बार deploy होती है। main पर हर merge `ghcr.io/acme/tracker:3f9c2ab` बनाता है, staging पर roll करता है, 30 सेकंड का smoke test चलाता है, फिर (एक click approval के बाद) production VPS अपडेट करता है। खराब release से 5xx बढ़े तो on-call engineer ने पिछले SHA के लिए deploy workflow दोबारा चलाया और 90 सेकंड में सब सामान्य हो गया, बिना SSH और अंदाज़े के।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/cd-basic.yml  (build, push, deploy in one workflow)
name: CD Basic                      # workflow name
on:                                 # triggers
  push:                             # on push
    branches: [main]                # only main
permissions:                        # token permissions
  contents: read                    # read repo
  packages: write                   # push to GHCR
jobs:                               # jobs
  deploy:                           # one job for simplicity
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 20             # cap
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout (example version)
      - uses: docker/login-action@v3  # login to registry
        with:                       # inputs
          registry: ghcr.io         # GitHub Container Registry
          username: ${{ github.actor }}  # current user
          password: ${{ secrets.GITHUB_TOKEN }}  # auto token
      - uses: docker/build-push-action@v6  # build and push
        with:                       # inputs
          context: .                # build context
          push: true                # push to registry
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}  # immutable tag (repo name must be lowercase)
      - name: Deploy over SSH       # update the VPS
        env:                        # secrets to env
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}  # private key
          HOST: ${{ secrets.VPS_HOST }}  # server address
        run: |                      # shell
          install -m 600 /dev/null key && echo "$SSH_KEY" > key  # key file with safe perms
          ssh -i key -o StrictHostKeyChecking=accept-new deploy@"$HOST" \
            "IMAGE_TAG=${{ github.sha }} docker compose -f /srv/app/docker-compose.yml up -d"  # restart with new tag
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/cd.yml  (staging -> approval -> production with rollback)
name: CD                            # workflow name
on:                                 # triggers
  workflow_run:                     # start after CI finishes
    workflows: ['CI']               # name of the CI workflow
    types: [completed]              # when it completes
    branches: [main]                # on main only
  workflow_dispatch:                # manual run / redeploy of an older SHA
    inputs:                         # inputs
      sha:                          # commit to deploy
        description: 'Commit SHA to deploy (rollback)'  # help text
        required: false             # optional
concurrency:                        # never run two deploys at once
  group: deploy-production          # one lane
  cancel-in-progress: false         # queue, never cancel a running deploy
permissions:                        # least privilege
  contents: read                    # read repo
  packages: write                   # push image
jobs:                               # jobs
  build:                            # build and push image
    if: github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success'  # only after green CI
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 20             # cap
    outputs:                        # pass tag to later jobs
      tag: ${{ steps.vars.outputs.tag }}  # image tag
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
        with:                       # inputs
          ref: ${{ inputs.sha || github.event.workflow_run.head_sha }}  # exact commit to ship
      - id: vars                    # step id
        run: echo "tag=$(git rev-parse --short=12 HEAD)" >> "$GITHUB_OUTPUT"  # short SHA as tag
      - uses: docker/login-action@v3  # login
        with:                       # inputs
          registry: ghcr.io         # registry
          username: ${{ github.actor }}  # user
          password: ${{ secrets.GITHUB_TOKEN }}  # token
      - uses: docker/build-push-action@v6  # build+push
        with:                       # inputs
          context: .                # context
          push: true                # push
          tags: ghcr.io/acme/app:${{ steps.vars.outputs.tag }}  # example repo path (lowercase)
  staging:                          # auto deploy to staging
    needs: build                    # after build
    runs-on: ubuntu-latest          # runner
    environment: staging            # GitHub environment (secrets + rules)
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout deploy scripts
      - run: ./deploy/deploy.sh staging ${{ needs.build.outputs.tag }}  # your script: pull image, up -d, health check
        env:                        # env
          SSH_KEY: ${{ secrets.SSH_KEY }}  # environment-scoped secret
          HOST: ${{ secrets.HOST }}  # environment-scoped host
  production:                       # gated production deploy
    needs: [build, staging]         # only after staging is green
    runs-on: ubuntu-latest          # runner
    environment: production         # required reviewers configured on this environment
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - run: ./deploy/deploy.sh production ${{ needs.build.outputs.tag }}  # same script, different target
        env:                        # env
          SSH_KEY: ${{ secrets.SSH_KEY }}  # production-scoped secret
          HOST: ${{ secrets.HOST }}  # production-scoped host
      - name: Notify on failure     # rollback hint
        if: failure()               # only if deploy failed
        run: echo "Deploy failed. Redeploy previous SHA via workflow_dispatch."  # replace with Slack webhook
```

---

## 🟠 My Stack Integration
On the VPS keep `docker-compose.yml` using `image: ghcr.io/acme/app:${IMAGE_TAG}` and Nginx in front (`proxy_pass` to the container). The deploy script pulls the tag, runs `docker compose up -d --wait`, then curls `/health` through Nginx. Roll back by redeploying the previous tag.

```bash
#!/usr/bin/env bash
# deploy/deploy.sh  usage: deploy.sh <env> <tag>
set -euo pipefail                                   # stop on any error or unset variable
ENV_NAME="$1"; TAG="$2"                             # arguments
ssh -i key -o StrictHostKeyChecking=accept-new deploy@"$HOST" bash -s <<EOF
  set -euo pipefail                                 # strict mode on the server
  cd /srv/app                                       # app directory
  export IMAGE_TAG="$TAG"                           # tag consumed by docker-compose.yml
  docker compose pull                               # fetch new image
  docker compose up -d --wait                       # start and wait for healthchecks
  curl -fsS http://127.0.0.1/health                 # confirm through Nginx
EOF
```

Security: use environment-scoped secrets, a dedicated low-privilege `deploy` SSH user, pin deploys to SHA tags, and restrict who can approve production.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deploying only the `:latest` tag, so you cannot tell or restore versions.
✅ Correct: Tag by commit SHA (and optionally also move `latest`).

❌ Mistake 2: Building a different artifact for staging and production.
✅ Correct: Build once, promote the same image through environments.

❌ Mistake 3: No health check after deploy, so broken releases look "successful".
✅ Correct: Use `--wait`, curl `/health`, and fail the job if unhealthy.

❌ Mistake 4: `cancel-in-progress: true` on deploys, killing a release halfway.
✅ Correct: Use a concurrency group with `cancel-in-progress: false`.

---

## 🧠 Tricky Interview Question
**Q:** What is the difference between Continuous Delivery and Continuous Deployment, and which should a payments company choose?

Answer: Delivery keeps the pipeline always releasable but requires a human approval before production; Deployment removes that gate and ships every green commit. A payments company usually chooses Delivery for the production step (approval, change windows, audit trail) while keeping staging fully automated, plus strong automated tests and instant rollback to limit risk either way.

---

## ⚫ Interview Questions + Answers

Q1: What is an immutable artifact and why does CD use it?
A1: A build output that never changes (a Docker image identified by a SHA). It guarantees what you tested is exactly what you ship.

Q2: Where do secrets live in CD?
A2: GitHub environment secrets (scoped to staging/production), never in the repo, and only exposed to jobs that reference that environment.

Q3: How do you roll back?
A3: Redeploy the previous image tag (workflow_dispatch with an older SHA); database changes should be backward compatible (expand/contract migrations) so code rollback is safe.

Q4: How do you get zero downtime on a single VPS?
A4: Blue/green with two compose services and an Nginx upstream switch, or `docker compose up -d --wait` with healthchecks plus a quick reload; with one container expect a brief restart.

Q5: Push vs pull deployment?
A5: Push: CI SSHes into the server. Pull: an agent on the server (Watchtower, Argo CD, Flux) fetches changes. Pull needs no inbound credentials in CI but adds a component to run.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You release often and want repeatable, auditable deploys.
- Several people deploy to the same servers.

❌ Avoid when:
- Fully automatic deployment with no tests or monitoring (that is gambling).
- One-off hobby site where a script on your laptop is enough (still consider it).

---

## 📊 Visual Diagram
```
 git push main
      |
      v
  [ CI: lint+test+scan ] --fail--> stop
      | pass
      v
  [ build image :SHA ] --> [ registry: GHCR ]
      |
      v
  [ deploy staging ] -> smoke test --fail--> stop
      |
      v
  [ approval gate (reviewers) ]
      |
      v
  [ deploy production VPS ]
      |-- health check OK --> notify success
      |-- health check FAIL -> rollback to previous :SHA
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Continuous Delivery | Always releasable, manual release | हमेशा release योग्य, manual release |
| Continuous Deployment | Auto release of every green build | हर green build का auto release |
| Artifact | Built output (image) | build का नतीजा (image) |
| Rollback | Return to previous version | पिछले version पर लौटना |
| Smoke test | Quick basic check | तेज़ बुनियादी जाँच |

---

## ⚡ 3-Line Summary
English: CD builds one immutable image, pushes it, and promotes it through environments.
English: Every deploy ends with a health check and has a rollback path.
English: Secrets are environment-scoped and deploys never overlap.

Hindi: CD एक immutable image बनाता है, push करता है और environments में आगे बढ़ाता है।
Hindi: हर deploy health check पर खत्म होता है और उसका rollback रास्ता होता है।
Hindi: Secrets environment-scoped होते हैं और deploys कभी overlap नहीं करते।

---

## ➡️ Next Topic
**332. Deploy on Push to Main** — the most common trigger, explained in detail.
