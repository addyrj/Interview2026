# 4. DevOps Lifecycle
# हिंदी में: DevOps Lifecycle (जीवन चक्र)

---

## 🔵 Simple Definition (English)
The **DevOps lifecycle** is the endless loop of phases a team repeats for every change: **Plan, Code, Build, Test, Release, Deploy, Operate, Monitor**, and then back to Plan using what monitoring taught. It is drawn as an infinity symbol because it never ends.

## 🔵 सरल परिभाषा (Hindi)
**DevOps lifecycle** उन phases का अंतहीन चक्र है जिसे team हर change के लिए दोहराती है: **Plan, Code, Build, Test, Release, Deploy, Operate, Monitor**, और फिर monitoring से सीखकर वापस Plan। इसे infinity (∞) चिह्न की तरह बनाते हैं क्योंकि यह कभी खत्म नहीं होता।

---

## 🔴 Problem it Solves
Without a clear lifecycle, teams do some phases well and ignore others: lots of coding, little testing, no monitoring. Work then moves in a line (Waterfall) and feedback from production never reaches planning, so the same problems return. The lifecycle makes every phase visible, assigns tools to each, and closes the loop.

## 🔴 यह क्यों बना? (Hindi)
साफ lifecycle के बिना teams कुछ phases अच्छे से करती हैं और बाकी भूल जाती हैं: coding बहुत, testing कम, monitoring बिल्कुल नहीं। काम सीधी रेखा (Waterfall) में चलता है और production का feedback planning तक पहुँचता ही नहीं, इसलिए वही problems लौटती हैं। Lifecycle हर phase को दिखाता है, हर phase के tools तय करता है और loop बंद करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 -> PLAN     : write tickets, user stories, acceptance criteria (Jira, GitHub Issues)
Step 2 -> CODE     : write code on a branch, review via Pull Request (Git, GitHub)
Step 3 -> BUILD    : compile / bundle / create a Docker image (npm, Docker, GitHub Actions)
Step 4 -> TEST     : unit, integration, security tests run automatically (Jest, Pytest, Trivy)
Step 5 -> RELEASE  : version and tag the tested artifact (git tag v1.2.0, registry image tag)
Step 6 -> DEPLOY   : roll out to servers (SSH, Docker Compose, Kubernetes, ECS)
Step 7 -> OPERATE  : run, scale, patch, manage config and infra (Nginx, Terraform, Ansible)
Step 8 -> MONITOR  : metrics, logs, alerts, user feedback (Prometheus, Grafana, CloudWatch)
Step 9 -> back to PLAN with new bugs, ideas and lessons
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 -> PLAN    : tickets, user stories, acceptance criteria लिखो (Jira, GitHub Issues)
Step 2 -> CODE    : branch पर code, Pull Request से review (Git, GitHub)
Step 3 -> BUILD   : compile / bundle / Docker image बनाओ (npm, Docker, GitHub Actions)
Step 4 -> TEST    : unit, integration, security tests अपने आप चलते हैं (Jest, Pytest, Trivy)
Step 5 -> RELEASE : tested artifact को version/tag दो (git tag v1.2.0, registry image tag)
Step 6 -> DEPLOY  : servers पर रोल-आउट (SSH, Docker Compose, Kubernetes, ECS)
Step 7 -> OPERATE : चलाओ, scale, patch, config और infra संभालो (Nginx, Terraform, Ansible)
Step 8 -> MONITOR : metrics, logs, alerts, user feedback (Prometheus, Grafana, CloudWatch)
Step 9 -> नए bugs, ideas और सीख के साथ वापस PLAN
```

---

## 🟡 Real World Example
**Zomato adds a "Group order" feature.**
Plan: product writes stories. Code: devs build it behind a feature flag. Build and Test: CI builds the image and runs 2,000 tests. Release: tag `v5.12.0`. Deploy: canary to 5% of users. Operate: autoscaling handles the dinner peak. Monitor: dashboards show order failures rising from 0.2% to 1.5%. That data goes back to Plan: a bug ticket is created, fixed, and the loop runs again within hours.

**Your VPS:** push to GitHub (Code), Actions builds image (Build), runs tests (Test), tags image (Release), SSH deploy (Deploy), Nginx + Docker restart policy (Operate), uptime check + logs (Monitor).

## 🟡 Real Example Hindi mein
**Zomato "Group order" feature जोड़ता है।**
Plan: product stories लिखता है। Code: devs feature flag के पीछे बनाते हैं। Build और Test: CI image बनाता है और 2,000 tests चलाता है। Release: tag `v5.12.0`। Deploy: 5% users पर canary। Operate: autoscaling dinner peak संभालता है। Monitor: dashboard दिखाता है कि order failures 0.2% से 1.5% हो गए। यह data वापस Plan में जाता है: bug ticket बनता है, fix होता है और loop घंटों में फिर चलता है।

**आपका VPS:** GitHub में push (Code), Actions image बनाता है (Build), tests चलाता है (Test), image tag करता है (Release), SSH deploy (Deploy), Nginx + Docker restart policy (Operate), uptime check + logs (Monitor)।

---

## 💻 Code / Config Example — Basic
Each lifecycle phase as a simple script you can run locally (bash).

```bash
#!/usr/bin/env bash
# lifecycle-local.sh - run each DevOps phase by hand to understand it
set -euo pipefail                          # stop on error, unset variable, or failed pipe

echo "== CODE ==";   git status --short    # see what changed in your working copy
echo "== BUILD ==";  npm ci && npm run build   # clean install + build the app
echo "== TEST ==";   npm test              # run automated tests
echo "== RELEASE =="; git tag -a v1.0.0 -m "release 1.0.0" || true   # tag the version (skip if it exists)
echo "== PACKAGE =="; docker build -t myapp:1.0.0 .    # create an image (needs Docker installed)
echo "== MONITOR =="; curl -fsS http://localhost:3000/health || echo "app not running"   # simple health check
```

## 💻 Code / Config Example — Advanced
One workflow where each job maps to a lifecycle phase.

```yaml
# .github/workflows/lifecycle.yml
name: Lifecycle                                   # workflow name
on:
  push:
    branches: [main]                              # run on merge to main
permissions:
  contents: read                                  # read repo
  packages: write                                 # push to ghcr.io
env:
  IMAGE: ghcr.io/${{ github.repository }}         # image name, reused below
jobs:
  build-test:                                     # BUILD + TEST phases
    runs-on: ubuntu-latest                        # runner
    steps:
      - uses: actions/checkout@v4                 # CODE is fetched here
      - uses: actions/setup-node@v4               # install Node
        with:
          node-version: 20                        # version
          cache: npm                              # cache
      - run: npm ci                               # install
      - run: npm run build --if-present           # BUILD
      - run: npm test                             # TEST
  release:                                        # RELEASE phase
    needs: build-test                             # after tests pass
    runs-on: ubuntu-latest                        # runner
    steps:
      - uses: actions/checkout@v4                 # code again
      - uses: docker/login-action@v3              # log in to registry
        with:
          registry: ghcr.io                       # host
          username: ${{ github.actor }}           # user
          password: ${{ secrets.GITHUB_TOKEN }}   # token
      - uses: docker/build-push-action@v6         # build and publish image
        with:
          context: .                              # build context
          push: true                              # publish
          tags: ${{ env.IMAGE }}:${{ github.sha }}   # immutable tag per commit
  deploy:                                         # DEPLOY phase
    needs: release                                # after image exists
    runs-on: ubuntu-latest                        # runner
    environment: production                       # protection rules
    steps:
      - name: SSH deploy                          # step label
        env:
          KEY: ${{ secrets.VPS_SSH_KEY }}         # private key secret
          HOST: ${{ secrets.VPS_HOST }}           # server
        run: |                                    # shell script
          set -euo pipefail                       # strict mode
          install -m 600 /dev/null k              # key file, owner-only
          printf '%s\n' "$KEY" > k                # write key
          ssh -i k -o StrictHostKeyChecking=accept-new deploy@"$HOST" "cd /opt/app && IMAGE_TAG=${GITHUB_SHA} docker compose up -d"   # roll out
          rm -f k                                 # cleanup
  verify:                                         # MONITOR phase (post-deploy check)
    needs: deploy                                 # after rollout
    runs-on: ubuntu-latest                        # runner
    steps:
      - name: Smoke test                          # quick health check
        run: curl -fsS --retry 5 --retry-delay 5 --retry-all-errors https://example.com/health   # replace with your URL
```

---

## 🟠 My Stack Integration
| Phase | Node/React/FastAPI/VPS example |
|-------|--------------------------------|
| Plan | GitHub Issues + Projects board |
| Code | Git feature branches, PR review |
| Build | `npm run build` (React), `docker build` (Node, FastAPI) |
| Test | Jest/Vitest, Pytest, Trivy image scan |
| Release | image tag = git SHA, `git tag` for versions |
| Deploy | SSH + `docker compose up -d` on VPS, or ECS on AWS |
| Operate | Nginx reverse proxy, restart policies, certbot TLS renewal |
| Monitor | `/health` endpoint, Uptime Kuma, Prometheus + Grafana, CloudWatch |

```yaml
# Nginx upstream health route you can monitor (compose snippet for the VPS)
services:
  api:
    image: ghcr.io/you/api:${IMAGE_TAG}      # image from RELEASE phase (replace "you")
    healthcheck:                              # feeds the MONITOR phase
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]   # health URL
      interval: 30s                           # check interval
      retries: 3                              # failures before unhealthy
```
Security: add SAST/dependency scan in Test, image scan in Release, least-privilege keys in Deploy, and alert on suspicious logs in Monitor.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Treating Monitor as optional.
✅ Correct: Without monitoring, the loop is open; you do not learn from production.

❌ Mistake 2: Rebuilding the artifact for each environment.
✅ Correct: Build once, promote the same image through staging to prod.

❌ Mistake 3: Using the `latest` tag for releases.
✅ Correct: Use immutable tags (git SHA or semver) so you can roll back.

❌ Mistake 4: Phases owned by different silos again.
✅ Correct: One team, shared visibility into all phases.

---

## 🧠 Tricky Interview Question
**"Where does security fit in the DevOps lifecycle?"**

Answer: Everywhere, not as one phase at the end. Plan: threat modeling. Code: secret scanning, code review. Build: dependency and SAST checks. Test: DAST, container scan. Release: signed images. Deploy: least privilege, secrets manager. Operate: patching, WAF. Monitor: audit logs, alerts. This is DevSecOps (topic 10).

---

## ⚫ Interview Questions + Answers

Q1: List the DevOps lifecycle phases.
A1: Plan, Code, Build, Test, Release, Deploy, Operate, Monitor (sometimes Configure/Continuous Feedback), in a continuous loop.

Q2: Why is the lifecycle shown as an infinity loop?
A2: Because monitoring and feedback from production feed the next Plan; delivery is never "done".

Q3: What is the difference between Release and Deploy?
A3: Release prepares a versioned, approved artifact. Deploy puts it onto servers. You can deploy without releasing to users (feature flags) and release without new deploy (turning a flag on).

Q4: Which phases are "CI" and which are "CD"?
A4: Code, Build, Test are CI. Release and Deploy are CD. Operate and Monitor keep the service healthy and feed back.

Q5: Name one tool per phase for your stack.
A5: Plan: GitHub Issues; Code: Git; Build: Docker; Test: Jest/Pytest; Release: GHCR tags; Deploy: Docker Compose over SSH; Operate: Nginx + Terraform; Monitor: Prometheus/Grafana.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need to find which part of delivery is weak (e.g., no monitoring).
- Choosing tools: map one per phase.
- Onboarding people to the pipeline.

❌ Avoid when:
- Treating it as strict stages with sign-offs; it is a loop with overlap, not Waterfall.

---

## 📊 Visual Diagram
```
        PLAN -> CODE -> BUILD -> TEST            (Dev side / CI)
         ^                         |
         |                         v
      MONITOR <- OPERATE <- DEPLOY <- RELEASE    (Ops side / CD)
         |
         +--- feedback (errors, metrics, user ideas) ---> next PLAN
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Artifact | Built output (Docker image, zip) | Build से बना output |
| Release | Versioned, approved build | Version किया हुआ build |
| Deploy | Put a build onto servers | Servers पर चढ़ाना |
| Feature flag | Switch a feature on/off without deploy | बिना deploy feature on/off |
| Feedback loop | Production data back to planning | Production data वापस planning में |
| Smoke test | Quick check that the basics work | बुनियादी जाँच कि सब चल रहा है |

---

## ⚡ 3-Line Summary
English: The lifecycle is Plan, Code, Build, Test, Release, Deploy, Operate, Monitor, repeating.
Each phase has automation and tools; monitoring feeds the next plan.
Skipping a phase breaks the loop and the learning.

Hindi: Lifecycle है Plan, Code, Build, Test, Release, Deploy, Operate, Monitor, बार-बार।
हर phase के लिए automation और tools हैं; monitoring अगला plan तय करती है।
कोई phase छोड़ने से loop और सीख दोनों टूट जाते हैं।

---

## ➡️ Next Topic
**5. CI/CD - What + Why** — the automation engine that runs Code to Deploy phases.
