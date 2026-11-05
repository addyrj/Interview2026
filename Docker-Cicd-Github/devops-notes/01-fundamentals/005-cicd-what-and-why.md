# 5. CI/CD — What + Why
# हिंदी में: CI/CD — क्या है और क्यों

---

## 🔵 Simple Definition (English)
**CI/CD** stands for Continuous Integration and Continuous Delivery/Deployment. **CI** automatically builds and tests code every time someone pushes a change. **CD** automatically delivers (or deploys) the tested build to servers. Together they form a pipeline from commit to production.

## 🔵 सरल परिभाषा (Hindi)
**CI/CD** यानी Continuous Integration और Continuous Delivery/Deployment। **CI** हर push पर code को अपने आप build और test करता है। **CD** tested build को अपने आप servers तक पहुँचाता (या deploy करता) है। दोनों मिलकर commit से production तक की pipeline बनाते हैं।

---

## 🔴 Problem it Solves
- **Integration hell:** five developers work for 3 weeks on separate branches, then merge on release day and everything conflicts.
- **Manual testing:** slow, skipped under deadline pressure, inconsistent.
- **Manual deploys:** error-prone ("I forgot to run migrations").
- **Slow feedback:** developer learns about a bug days later.

CI/CD makes integration small and constant, tests automatic, and deployment a button (or no button).

## 🔴 यह क्यों बना? (Hindi)
- **Integration hell:** पाँच developers 3 हफ्ते अलग branches पर काम करते हैं, फिर release के दिन merge में सब conflict।
- **Manual testing:** धीमी, deadline में छूट जाती है, हर बार अलग।
- **Manual deploys:** गलतियाँ होती हैं ("migrations चलाना भूल गया")।
- **धीमा feedback:** bug का पता दिनों बाद चलता है।

CI/CD integration को छोटा और लगातार, tests को automatic और deployment को एक button (या बिना button) बना देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 -> Dev pushes a commit / opens a PR
Step 2 -> A webhook tells the CI server (GitHub Actions) "something changed"
Step 3 -> CI starts a clean runner (fresh VM or container)
Step 4 -> CI checks out code, installs dependencies, builds
Step 5 -> CI runs lint, unit tests, security scans; result is pass/fail on the PR
Step 6 -> On merge to main, CI builds a Docker image and pushes it to a registry
Step 7 -> CD deploys it to staging, runs smoke tests, then to production
Step 8 -> Failure at any step stops the pipeline and notifies the team
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 -> Dev commit push करता है / PR खोलता है
Step 2 -> Webhook CI server (GitHub Actions) को बताता है "कुछ बदला है"
Step 3 -> CI एक साफ runner शुरू करता है (नई VM या container)
Step 4 -> CI code checkout, dependencies install, build करता है
Step 5 -> CI lint, unit tests, security scans चलाता है; PR पर pass/fail दिखता है
Step 6 -> main में merge होने पर CI Docker image बनाकर registry में push करता है
Step 7 -> CD पहले staging पर deploy, smoke tests, फिर production
Step 8 -> किसी भी step में failure हो तो pipeline रुकती है और team को सूचना मिलती है
```

---

## 🟡 Real World Example
**Flipkart Big Billion Days prep.** Hundreds of engineers merge code daily. Every PR triggers CI: build, tests in parallel (20 minutes down to 5), image scan. Merged code auto-deploys to a staging copy of production where load tests run. Because every change is small and verified, the team ships fixes even during the sale itself.

**Your VPS:** a FastAPI + React app. On every push: run `pytest` and `npm test`. On merge to `main`: build two images, push to GHCR, SSH to VPS, `docker compose up -d`, and curl `/health`.

## 🟡 Real Example Hindi mein
**Flipkart की Big Billion Days तैयारी।** सैकड़ों engineers रोज़ code merge करते हैं। हर PR पर CI: build, tests parallel में (20 मिनट से 5 मिनट), image scan। Merge हुआ code production की staging copy पर auto-deploy होता है जहाँ load tests चलते हैं। हर change छोटा और verified है, इसलिए sale के दौरान भी fixes भेजे जा सकते हैं।

**आपका VPS:** FastAPI + React app। हर push पर `pytest` और `npm test`। `main` में merge पर: दो images बनाओ, GHCR में push, VPS पर SSH, `docker compose up -d`, और `/health` पर curl।

---

## 💻 Code / Config Example — Basic
A minimal CI workflow for a Node.js app.

```yaml
# .github/workflows/ci.yml
name: CI                                   # name shown in Actions tab
on:
  pull_request:                            # run on every pull request
  push:
    branches: [main]                       # and on pushes to main
jobs:
  build:                                   # job id
    runs-on: ubuntu-latest                 # Linux runner hosted by GitHub
    steps:
      - uses: actions/checkout@v4          # fetch repository code (example version)
      - uses: actions/setup-node@v4        # install Node.js
        with:
          node-version: 20                 # Node major version
          cache: npm                       # cache npm downloads
      - run: npm ci                        # install from lockfile
      - run: npm run build --if-present    # build when a build script exists
      - run: npm test                      # run tests; non-zero exit fails the job
```

## 💻 Code / Config Example — Advanced
Matrix tests (Node + Python), caching, Docker build with cache, and staged deploy.

```yaml
# .github/workflows/cicd.yml
name: CI-CD                                     # workflow name
on:
  pull_request:                                 # CI on PRs
  push:
    branches: [main]                            # CI + CD on main
permissions:
  contents: read                                # least privilege
  packages: write                               # push images
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}   # one run per branch
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}   # cancel old PR runs only
jobs:
  test-node:                                    # frontend/backend Node tests
    runs-on: ubuntu-latest                      # runner
    strategy:
      matrix:
        node: [18, 20]                          # test on two Node versions
    steps:
      - uses: actions/checkout@v4               # code
      - uses: actions/setup-node@v4             # Node
        with:
          node-version: ${{ matrix.node }}      # version from matrix
          cache: npm                            # cache
      - run: npm ci                             # install
      - run: npm test                           # test
  test-python:                                  # FastAPI tests
    runs-on: ubuntu-latest                      # runner
    steps:
      - uses: actions/checkout@v4               # code
      - uses: actions/setup-python@v5           # Python
        with:
          python-version: "3.12"                # version
          cache: pip                            # cache pip
      - run: pip install -r requirements.txt    # install dependencies
      - run: pytest -q                          # run tests quietly
  image:                                        # build and push image
    if: github.event_name == 'push'             # only on push to main, not PRs
    needs: [test-node, test-python]             # wait for both test jobs
    runs-on: ubuntu-latest                      # runner
    steps:
      - uses: actions/checkout@v4               # code
      - uses: docker/setup-buildx-action@v3     # modern builder with cache
      - uses: docker/login-action@v3            # registry login
        with:
          registry: ghcr.io                     # GitHub registry
          username: ${{ github.actor }}         # user
          password: ${{ secrets.GITHUB_TOKEN }}   # token
      - uses: docker/build-push-action@v6       # build + push
        with:
          context: .                            # context
          push: true                            # publish
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}   # immutable tag
          cache-from: type=gha                  # reuse cache from earlier runs
          cache-to: type=gha,mode=max           # save cache for next run
  deploy:                                       # CD to VPS
    needs: image                                # after the image is pushed
    runs-on: ubuntu-latest                      # runner
    environment: production                     # approvals/secrets scope
    steps:
      - name: Deploy and smoke test             # step label
        env:
          KEY: ${{ secrets.VPS_SSH_KEY }}       # SSH private key
          HOST: ${{ secrets.VPS_HOST }}         # server host
        run: |                                  # shell script
          set -euo pipefail                     # strict mode
          install -m 600 /dev/null k            # secure key file
          printf '%s\n' "$KEY" > k              # write key
          ssh -i k -o StrictHostKeyChecking=accept-new deploy@"$HOST" "cd /opt/app && IMAGE_TAG=${GITHUB_SHA} docker compose up -d"   # roll out
          curl -fsS --retry 5 --retry-delay 5 --retry-all-errors https://example.com/health   # smoke test (replace URL)
          rm -f k                               # delete key
```

---

## 🟠 My Stack Integration
- **Node.js:** `npm ci`, `npm test`, Docker build with multi-stage Dockerfile.
- **React:** `npm run build` makes static files; either copy into an Nginx image or sync to `/var/www/app` on the VPS.
- **FastAPI:** `pip install`, `pytest`, image runs `uvicorn`/`gunicorn`.
- **Nginx / VPS:** CD step runs `docker compose up -d`; Nginx keeps serving while containers restart (use health checks to reduce downtime).
- **AWS:** swap GHCR for ECR and the SSH step for `aws ecs update-service` using OIDC (no long-lived AWS keys).

```yaml
# Using GitHub OIDC with AWS (no stored access keys) - job fragment
permissions:
  id-token: write                                # allow requesting an OIDC token
  contents: read                                 # read code
steps:
  - uses: aws-actions/configure-aws-credentials@v4   # exchange OIDC token for temporary AWS credentials
    with:
      role-to-assume: arn:aws:iam::123456789012:role/gha-deploy   # example role ARN, replace
      aws-region: ap-south-1                     # Mumbai region
```
Security: store secrets in GitHub Secrets, pin third-party actions to a version or commit SHA, and never run untrusted PR code with secrets (forks).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: A pipeline that takes 45 minutes.
✅ Correct: Cache dependencies, run jobs in parallel, keep CI under ~10 minutes.

❌ Mistake 2: Ignoring failing (red) builds.
✅ Correct: Red main is top priority; fix or revert immediately.

❌ Mistake 3: Secrets in workflow files or logs.
✅ Correct: Use `${{ secrets.NAME }}`; never `echo` them.

❌ Mistake 4: Different build per environment.
✅ Correct: Build once, deploy the same image everywhere.

❌ Mistake 5: Flaky tests tolerated by re-running.
✅ Correct: Fix or quarantine flaky tests; they destroy trust.

---

## 🧠 Tricky Interview Question
**"Our CI is green but production broke after deploy. Doesn't that mean CI is useless?"**

Answer: No, it means CI tests missed that scenario. CI only proves what its tests check. Common gaps: differences between CI and production config, missing integration tests, database migrations, or env variables. Improve with staging that mirrors production, smoke tests after deploy, canary releases, and monitoring with automatic rollback. Add a regression test for that exact bug.

---

## ⚫ Interview Questions + Answers

Q1: What is CI?
A1: Developers merge to a shared branch frequently; each merge triggers an automated build and test run to catch integration problems early.

Q2: What is CD?
A2: Continuous Delivery keeps every passing build ready to release (manual approval for production). Continuous Deployment goes one step further and releases automatically with no manual gate.

Q3: What are the benefits of CI/CD?
A3: Faster feedback, fewer bugs reaching production, smaller safer releases, consistent deploys, less manual work and faster recovery.

Q4: What is a pipeline artifact?
A4: The output of a build step (Docker image, zip, test report) that later stages use, built once and promoted.

Q5: Name popular CI/CD tools.
A5: GitHub Actions, GitLab CI, Jenkins, CircleCI, Argo CD (CD for Kubernetes), AWS CodePipeline.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one developer or frequent releases.
- You have automated tests (even a few).
- Production uptime matters.

❌ Avoid when:
- One-time scripts or throwaway demos.
- No tests and no willingness to write any (pipeline will only automate risk).

---

## 📊 Visual Diagram
```
 Developer      GitHub            CI (Actions)                CD
 +-------+  push +------+ webhook +-----------------+        +----------+
 | code  |------>| repo |-------->| build -> test   |--pass->| staging  |
 +-------+       +------+         | -> scan -> image|        +----+-----+
                                  +--------+--------+             | smoke test
                                           | fail                 v
                                           v                +----------+
                                    notify developer        |production|
                                                            +----------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CI | Auto build + test on every change | हर change पर auto build + test |
| CD | Auto delivery/deployment of tested builds | Tested build का auto delivery/deploy |
| Pipeline | Ordered automated stages | क्रमबद्ध automatic stages |
| Runner | Machine that executes the jobs | Jobs चलाने वाली machine |
| Artifact | Output produced by a build | Build का output |
| Webhook | HTTP call sent when an event happens | Event होने पर भेजा गया HTTP call |

---

## ⚡ 3-Line Summary
English: CI builds and tests every change automatically; CD delivers tested builds to servers.
Together they give fast feedback and small, safe, repeatable releases.
Keep pipelines fast, secure and trusted.

Hindi: CI हर change को अपने आप build और test करता है; CD tested builds servers तक पहुँचाता है।
दोनों मिलकर तेज़ feedback और छोटी, सुरक्षित, दोहराने योग्य releases देते हैं।
Pipelines को तेज़, सुरक्षित और भरोसेमंद रखें।

---

## ➡️ Next Topic
**6. CI vs CD vs CD** — the three letters hide a difference between Delivery and Deployment that interviewers love to ask.
