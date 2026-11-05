---

# 374. Multi-Environment Pipeline
# हिंदी में: Multi-Environment Pipeline

---

## 🔵 Simple Definition (English)
A multi-environment pipeline promotes the same built image through dev, staging and production. Each environment has its own secrets, URL and protection rules (for example, manual approval for production). The key rule: build once, deploy the same artifact everywhere.

## 🔵 सरल परिभाषा (Hindi)
Multi-environment pipeline एक ही बनी हुई image को dev, staging और production तक promote करता है। हर environment के अपने secrets, URL और सुरक्षा नियम होते हैं (जैसे production के लिए manual approval)। मुख्य नियम: एक बार build करो, हर जगह वही artifact deploy करो।

---

## 🔴 Problem it Solves
- "It worked in staging" because staging was built differently from production.
- Production secrets used in test runs.
- Anyone can push straight to production.
- Config values hard-coded per environment inside the image.

## 🔴 यह क्यों बना? (Hindi)
- "Staging में चला था" क्योंकि staging production से अलग तरीके से बना था।
- Test runs में production secrets का इस्तेमाल।
- कोई भी सीधे production में push कर सकता है।
- Image के भीतर हर environment के config values hard-coded।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Merge to main: build image once, tag with SHA, push to registry
Step 2 → Deploy to "dev" automatically (no approval)
Step 3 → Run smoke tests against dev, then deploy to "staging"
Step 4 → Staging: integration + load checks
Step 5 → "production" environment requires reviewer approval + wait timer
Step 6 → Deploy the SAME SHA with production config; health check; rollback on failure
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → main पर merge: image एक बार build, SHA tag, registry में push
Step 2 → "dev" पर automatic deploy (approval नहीं)
Step 3 → dev पर smoke tests, फिर "staging" पर deploy
Step 4 → Staging: integration + load checks
Step 5 → "production" environment में reviewer approval + wait timer ज़रूरी
Step 6 → वही SHA production config के साथ deploy; health check; fail पर rollback
```

---

## 🟡 Real World Example
A lending app (like a Paytm or Razorpay style product) keeps three servers: dev (small EC2), staging (production-sized), and production. Merges go to dev automatically. A QA lead triggers staging promotion by approving; the CTO or on-call lead approves production. Because the image is identical, a bug found in staging was reproducible and the exact same SHA was patched, not rebuilt differently.

## 🟡 Real Example Hindi mein
एक lending app (Paytm या Razorpay जैसा) के तीन servers हैं: dev (छोटा EC2), staging (production जितना) और production। Merge dev पर automatic जाता है। QA lead approve करके staging promotion चलाता है; CTO या on-call lead production approve करता है। Image identical होने से staging में मिला bug reproduce हुआ और उसी SHA का patch बना, अलग तरीके से rebuild नहीं।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/two-env.yml
name: Two environments                 # Name
on:
  push:
    branches: [main]
jobs:
  staging:
    runs-on: ubuntu-latest
    environment: staging               # Uses staging secrets and rules
    steps:
      - run: echo "Deploy to ${{ vars.APP_URL }}"   # vars come from the environment settings
  production:
    needs: staging                     # Only after staging succeeds
    runs-on: ubuntu-latest
    environment: production            # Pauses for required reviewers
    steps:
      - run: echo "Deploy to ${{ vars.APP_URL }}"
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/promote.yml
name: Build and promote
on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      rollback_tag:
        description: Existing tag to redeploy to production (rollback)
        required: false
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false            # Never cancel a deploy mid-way
permissions:
  contents: read
  packages: write
jobs:
  build:
    if: github.event.inputs.rollback_tag == ''     # Skip build on rollback
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.meta.outputs.tag }}
    steps:
      - uses: actions/checkout@v4
      - id: meta
        run: echo "tag=${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ steps.meta.outputs.tag }}   # Repo must be lowercase
  deploy-dev:
    needs: build
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.HOST }}                  # Environment-scoped secret
          username: deploy
          key: ${{ secrets.SSH_KEY }}
          script: cd /opt/app && TAG=${{ needs.build.outputs.tag }} docker compose up -d
  deploy-staging:
    needs: [build, deploy-dev]
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.HOST }}                  # Different value because environment differs
          username: deploy
          key: ${{ secrets.SSH_KEY }}
          script: cd /opt/app && TAG=${{ needs.build.outputs.tag }} docker compose up -d
      - name: Smoke test
        run: curl -fsS "${{ vars.APP_URL }}/health"  # URL from environment variable
  deploy-prod:
    needs: [build, deploy-staging]
    runs-on: ubuntu-latest
    environment: production                           # Required reviewers + wait timer configured in Settings
    steps:
      - uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.HOST }}
          username: deploy
          key: ${{ secrets.SSH_KEY }}
          script: cd /opt/app && TAG=${{ needs.build.outputs.tag }} docker compose up -d
      - run: curl -fsS "${{ vars.APP_URL }}/health"
  rollback-prod:
    if: github.event.inputs.rollback_tag != ''
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.HOST }}
          username: deploy
          key: ${{ secrets.SSH_KEY }}
          script: cd /opt/app && TAG=${{ github.event.inputs.rollback_tag }} docker compose up -d
```

Note: when `build` is skipped (rollback run), `deploy-*` jobs depending on it are skipped too, which is the intended behaviour.

---

## 🟠 My Stack Integration
- Create environments in Settings > Environments: `dev`, `staging`, `production`. Add secrets (`HOST`, `SSH_KEY`) per environment and variables (`APP_URL`).
- Production: required reviewers, wait timer, and "deployment branches: main only".
- Configuration differs only by env vars/`.env` on each server. Nginx server_name and certificates also differ per host:

```nginx
# /etc/nginx/conf.d/app.conf (production; staging uses staging.example.com)
server {
  listen 443 ssl;                                  # TLS terminated at Nginx
  server_name app.example.com;                     # Environment specific
  ssl_certificate     /etc/letsencrypt/live/app.example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;
  location / { proxy_pass http://127.0.0.1:8000; } # FastAPI/Node container
}
```

Nginx config not tested with `nginx -t` here. Required reviewers on private repos need a paid plan in some GitHub tiers; check your plan.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Rebuilding the image per environment.
✅ Correct: Build once and promote the same tag.

❌ Mistake 2: Sharing one set of secrets across all environments.
✅ Correct: Environment-scoped secrets; production secrets unreachable from dev jobs.

❌ Mistake 3: Letting feature branches deploy to production.
✅ Correct: Restrict deployment branches on the environment.

❌ Mistake 4: Staging unlike production (smaller DB, different versions).
✅ Correct: Keep versions and topology aligned.

Security: approvals prevent self-approval option, audit logs record who approved, and production SSH keys differ from lower environments.

---

## 🧠 Tricky Interview Question
Why is "build once, deploy many" better than building from the same commit in each environment?

Answer: Two builds from the same commit can differ (new base-image patch, a dependency resolved differently, build-time env vars). Then what you tested in staging is not what runs in production. A single immutable image, with config injected at runtime, guarantees the tested artifact is the deployed artifact.

---

## ⚫ Interview Questions + Answers

Q1: What are GitHub Environments?
A1: Named deployment targets with their own secrets, variables, protection rules, and deployment history.

Q2: Where does environment-specific config live?
A2: Outside the image: env vars, mounted files, secret managers, per environment.

Q3: How do you roll back?
A3: Redeploy a previous immutable tag (the rollback job), possibly with DB backward compatibility.

Q4: Trunk-based or branch-per-environment?
A4: Trunk-based promotion of artifacts is preferred; branch-per-env invites drift and merge pain.

Q5: How do you stop two deploys colliding?
A5: `concurrency` group with `cancel-in-progress: false`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Real users and money are involved, with QA or approvals needed.

❌ Avoid when:
- Solo hobby project; a single environment with good rollback may suffice.

---

## 📊 Visual Diagram
```
 push main --> BUILD once (SHA abc1234) --> GHCR
                         |
        +----------------+----------------+
        v                v                v
      dev  --smoke-->  staging  --approval--> production
   (auto)             (auto, tests)         (reviewers + timer)
   secrets A           secrets B             secrets C
        same image, different runtime config
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Environment | Named deploy target | नामित deploy target |
| Promotion | Move same artifact forward | वही artifact आगे बढ़ाना |
| Immutable image | Image never changed after build | Build के बाद न बदलने वाली image |
| Required reviewers | Approval gate | Approval की शर्त |
| Drift | Environments diverge over time | Environments का धीरे-धीरे अलग होना |

---

## ⚡ 3-Line Summary
English: Build once, promote the same SHA through dev, staging, production.
English: Use GitHub Environments for scoped secrets and approvals.
English: Keep config outside the image and rollback by tag.
Hindi: एक बार build करें, वही SHA dev, staging, production तक promote करें।
Hindi: Scoped secrets और approvals के लिए GitHub Environments इस्तेमाल करें।
Hindi: Config image के बाहर रखें और tag से rollback करें।

---

## ➡️ Next Topic
375. Multi-Region Deploy Pipeline: roll the same release out across several regions safely.
