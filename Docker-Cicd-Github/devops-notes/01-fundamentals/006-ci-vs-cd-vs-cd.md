# 6. CI vs CD vs CD (Continuous Integration vs Delivery vs Deployment)
# हिंदी में: CI बनाम Continuous Delivery बनाम Continuous Deployment

---

## 🔵 Simple Definition (English)
- **Continuous Integration (CI):** merge code often; every merge is built and tested automatically.
- **Continuous Delivery (CD):** every passing build is always ready to release; a human presses the button for production.
- **Continuous Deployment (CD):** every passing build goes to production automatically, with no human approval.

## 🔵 सरल परिभाषा (Hindi)
- **Continuous Integration (CI):** code बार-बार merge करो; हर merge अपने आप build और test होता है।
- **Continuous Delivery (CD):** हर passing build हमेशा release के लिए तैयार रहता है; production के लिए इंसान button दबाता है।
- **Continuous Deployment (CD):** हर passing build बिना किसी मंज़ूरी के अपने आप production पर पहुँचता है।

---

## 🔴 Problem it Solves
People mix up the three terms, and teams pick the wrong level for their risk. A bank cannot auto-deploy every commit without approval; a small SaaS can. Knowing the difference lets you choose how much automation and how much human control fits your product, regulations and test quality.

## 🔴 यह क्यों बना? (Hindi)
लोग तीनों शब्दों को मिला देते हैं और teams अपने risk के हिसाब से गलत level चुन लेती हैं। बैंक हर commit बिना approval के auto-deploy नहीं कर सकता; छोटा SaaS कर सकता है। फर्क समझने से आप तय कर सकते हैं कि आपके product, नियमों और test quality के लिए कितनी automation और कितना human control सही है।

---

## 🟢 How it Works — Step by Step

```
              CI                  Continuous Delivery        Continuous Deployment
Commit -> Build -> Test -> Artifact -> Staging deploy -> [ MANUAL APPROVAL ] -> Production
                                                         (Delivery stops here)
Commit -> Build -> Test -> Artifact -> Staging deploy -> automated checks pass -> Production
                                                         (Deployment: no human step)

Step 1 -> CI: build + test on each commit (all three levels do this)
Step 2 -> Delivery: package is always deployable, approval gate before production
Step 3 -> Deployment: gate is replaced by automated checks + monitoring + auto-rollback
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 -> CI: हर commit पर build + test (तीनों levels में होता है)
Step 2 -> Delivery: package हमेशा deploy-योग्य, production से पहले approval gate
Step 3 -> Deployment: gate की जगह automated checks + monitoring + auto-rollback
```

---

## 🟡 Real World Example
- **Continuous Delivery:** a company with payment features (like a PhonePe-style app) has CI/CD up to staging. A release manager approves production deploys during a low-traffic window because compliance requires sign-off.
- **Continuous Deployment:** a content website or internal tool merges to `main` and the change is live in 6 minutes, many times a day, protected by tests, feature flags and auto-rollback.

**Your VPS:** staging subdomain deploys automatically (Deployment); production uses a GitHub Environment with a required reviewer (Delivery).

## 🟡 Real Example Hindi mein
- **Continuous Delivery:** payment features वाली कंपनी (PhonePe जैसा app) में staging तक CI/CD है। Release manager कम traffic वाले समय में production deploy approve करता है क्योंकि compliance को sign-off चाहिए।
- **Continuous Deployment:** content website या internal tool में `main` में merge होते ही change 6 मिनट में live, दिन में कई बार, tests, feature flags और auto-rollback की सुरक्षा के साथ।

**आपका VPS:** staging subdomain अपने आप deploy (Deployment); production में GitHub Environment पर required reviewer (Delivery)।

---

## 💻 Code / Config Example — Basic
Continuous Delivery: production job waits for a human approval via a GitHub Environment.

```yaml
# .github/workflows/delivery.yml
name: Delivery                              # workflow name
on:
  push:
    branches: [main]                        # trigger on main
jobs:
  ci:                                       # CI part
    runs-on: ubuntu-latest                  # runner
    steps:
      - uses: actions/checkout@v4           # code
      - uses: actions/setup-node@v4         # Node
        with:
          node-version: 20                  # version
      - run: npm ci && npm test             # install and test
  deploy-prod:                              # delivery to production
    needs: ci                               # after CI passes
    runs-on: ubuntu-latest                  # runner
    environment: production                 # set "Required reviewers" in repo Settings > Environments
    steps:
      - run: echo "Deploying approved build"   # replace with real deploy command
```

## 💻 Code / Config Example — Advanced
Continuous Deployment: staging then production automatically, with smoke test and rollback on failure.

```yaml
# .github/workflows/deployment.yml
name: Deployment                                  # workflow name
on:
  push:
    branches: [main]                              # every merge to main
permissions:
  contents: read                                  # minimal rights
concurrency:
  group: deploy                                   # one deploy at a time
  cancel-in-progress: false                       # do not kill a running deploy
jobs:
  ci:
    runs-on: ubuntu-latest                        # runner
    steps:
      - uses: actions/checkout@v4                 # code
      - uses: actions/setup-node@v4               # Node
        with:
          node-version: 20                        # version
          cache: npm                              # cache
      - run: npm ci                               # install
      - run: npm test                             # tests
  staging:
    needs: ci                                     # after CI
    runs-on: ubuntu-latest                        # runner
    environment: staging                          # no approval configured = fully automatic
    steps:
      - name: Deploy staging                      # label
        run: echo "deploy to staging here"        # replace with real deploy (ssh/compose)
      - name: Smoke test staging                  # automated gate
        run: curl -fsS https://staging.example.com/health   # replace with your URL
  production:
    needs: staging                                # only if staging is healthy
    runs-on: ubuntu-latest                        # runner
    environment: production                       # leave reviewers EMPTY for deployment, or add them to get delivery
    steps:
      - name: Deploy production                   # label
        id: deploy                                # id so later steps can read the outcome
        run: echo "deploy to production here"     # replace with real deploy
      - name: Smoke test production               # post-deploy check
        id: smoke                                 # id
        run: curl -fsS https://example.com/health # replace with your URL
      - name: Rollback on failure                 # automatic safety net
        if: failure()                             # runs only if a previous step failed
        run: echo "run rollback script (previous image tag)"   # replace with real rollback
```

---

## 🟠 My Stack Integration
- Use **GitHub Environments**: `staging` (no reviewers = auto deploy) and `production` (reviewers = delivery). One toggle switches between Delivery and Deployment.
- **Node/FastAPI:** run DB migrations as a separate pre-deploy step; make them backward compatible so rollback of code is safe.
- **React:** static files can be deployed atomically (new folder + symlink swap) for instant rollback.
- **Nginx / VPS:** `docker compose up -d` plus health checks; keep the previous image tag for rollback.
- **AWS:** ECS rolling update with circuit breaker gives auto-rollback for Deployment.

```bash
# Atomic symlink deploy for React build on VPS (bash, run by pipeline over SSH)
set -euo pipefail                                  # strict mode
REL=/var/www/app/releases/$(date +%Y%m%d%H%M%S)    # new release folder named by timestamp
mkdir -p "$REL"                                    # create it
tar -xzf /tmp/build.tgz -C "$REL"                  # unpack the uploaded build
ln -sfn "$REL" /var/www/app/current                # switch "current" symlink in one step; Nginx root points at /var/www/app/current
```
Security: for Continuous Deployment keep strong automated gates (tests, scans); for Delivery, restrict who can approve (CODEOWNERS / environment reviewers).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Saying "CD" without saying which one.
✅ Correct: Always clarify: Delivery (manual gate) or Deployment (no gate).

❌ Mistake 2: Auto-deploying with weak or no tests.
✅ Correct: Continuous Deployment needs strong tests, monitoring and rollback first.

❌ Mistake 3: Deploying DB schema changes that break the old code.
✅ Correct: Use expand/contract migrations so old and new versions both work.

❌ Mistake 4: Different artifacts for staging and production.
✅ Correct: Promote the same image.

---

## 🧠 Tricky Interview Question
**"Is it possible to practice Continuous Delivery without Continuous Deployment? And the reverse?"**

Answer: Delivery without Deployment: yes, that is the normal case (approval before prod). Deployment without Delivery: no, because Deployment includes everything in Delivery (always-releasable builds) and just removes the manual gate. Also, you can do "continuous delivery" while releasing to customers rarely, as the point is being able to release at any time.

---

## ⚫ Interview Questions + Answers

Q1: One-line difference between Delivery and Deployment?
A1: Delivery needs a manual approval before production; Deployment pushes to production automatically.

Q2: Which needs more mature testing?
A2: Continuous Deployment, because no human catches mistakes before users do.

Q3: How do feature flags help?
A3: You can deploy code that is switched off, then enable it for a few users, so deploy and release are separated and risk is lower.

Q4: How do you get auto-rollback?
A4: Health checks plus a script or platform feature (ECS circuit breaker, Kubernetes rollout undo, Compose with previous tag) that reverts when checks fail.

Q5: Where do approvals live in GitHub Actions?
A5: In Environments: add required reviewers and wait timers to an environment; jobs targeting it pause until approved.

---

## 🔷 When to Use + When Not to Use
✅ Continuous Delivery when:
- Regulation or business wants sign-off (finance, health).
- Test coverage is still growing.

✅ Continuous Deployment when:
- Strong tests, monitoring, feature flags, quick rollback exist.
- Changes are small and frequent (SaaS, web apps).

❌ Avoid Deployment when:
- Releases need coordination (marketing launches, mobile app store review).

---

## 📊 Visual Diagram
```
 CI:          commit -> build -> unit tests ----------------+
                                                            v
 Delivery:    ... -> package -> staging -> [HUMAN OK] -> production
 Deployment:  ... -> package -> staging -> [auto checks] -> production

 Automation:   CI < Delivery < Deployment
 Human gate:   -      yes         no
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Approval gate | Manual check before production | Production से पहले manual जाँच |
| Environment | Named target (staging, production) with rules | नाम वाला target, नियमों के साथ |
| Promotion | Moving the same build to the next stage | वही build अगले stage पर ले जाना |
| Rollback | Return to the previous version | पिछले version पर वापसी |
| Feature flag | Runtime on/off switch for a feature | Runtime पर feature on/off |
| Canary | Gradual rollout to a few users | कुछ users पर धीरे-धीरे rollout |

---

## ⚡ 3-Line Summary
English: CI = integrate and test often. Delivery = always releasable with manual approval.
Deployment = every passing change goes live automatically.
Choose by risk, test maturity and compliance.

Hindi: CI = बार-बार integrate और test। Delivery = हमेशा release-योग्य, manual approval के साथ।
Deployment = हर passing change अपने आप live।
Risk, test maturity और compliance के हिसाब से चुनें।

---

## ➡️ Next Topic
**7. DevOps Tools Overview** — which tools fill each stage of these pipelines.
