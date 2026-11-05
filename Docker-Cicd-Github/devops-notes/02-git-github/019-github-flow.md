# 19. GitHub Flow
# हिंदी में: GitHub Flow

---

## 🔵 Simple Definition (English)
**GitHub Flow** is a lightweight branching model with one rule: `main` is always deployable. Every change is made on a short-lived branch, reviewed via a Pull Request, tested by CI, merged into `main` and deployed straight away.

## 🔵 सरल परिभाषा (Hindi)
**GitHub Flow** एक हल्का branching model है जिसका एक नियम है: `main` हमेशा deployable रहे। हर change छोटी उम्र वाली branch पर होता है, Pull Request से review होता है, CI test करती है, `main` में merge होता है और तुरंत deploy होता है।

---

## 🔴 Problem it Solves
Git Flow's `develop`, `release` and `hotfix` branches slow down web teams that deploy several times per day. GitHub Flow removes the ceremony: one long-lived branch, one review path, one deploy path. This shortens lead time and makes rollbacks simple (revert the PR or redeploy the previous commit).

## 🔴 यह क्यों बना? (Hindi)
Git Flow की `develop`, `release`, `hotfix` branches उन web teams को धीमा करती हैं जो दिन में कई बार deploy करती हैं। GitHub Flow यह ceremony हटाता है: एक long-lived branch, एक review path, एक deploy path। इससे lead time घटता है और rollback आसान होता है (PR revert करो या पिछला commit redeploy करो)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a branch from main (descriptive name).
Step 2 → Commit changes; push early.
Step 3 → Open a Pull Request (draft if still working).
Step 4 → Discuss, review, CI runs automatically.
Step 5 → (Optional) deploy the branch to a preview/staging environment to verify.
Step 6 → Merge into main after approval and green checks.
Step 7 → Deploy main to production (automatically); delete the branch.
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → main से branch बनाओ (वर्णनात्मक नाम)।
Step 2 → Changes commit करो; जल्दी push करो।
Step 3 → Pull Request खोलो (काम चल रहा हो तो draft)।
Step 4 → Discussion, review; CI अपने-आप चलती है।
Step 5 → (Optional) verify करने के लिए branch को preview/staging पर deploy करो।
Step 6 → Approval और green checks के बाद main में merge करो।
Step 7 → main को production पर (automatically) deploy करो; branch delete करो।

---

## 🟡 Real World Example
Your product: React frontend + Node.js API on a VPS. A developer fixes a checkout bug on `fix/cart-total`, opens a PR; Actions runs tests and builds a Docker image; reviewer approves; merge to `main` triggers SSH deploy; the fix is live in 15 minutes. If it breaks, you revert the PR and the same pipeline redeploys the old code.

## 🟡 Real Example Hindi mein
आपका product: React frontend + VPS पर Node.js API। Developer `fix/cart-total` branch पर checkout bug ठीक करता है, PR खोलता है; Actions tests चलाता और Docker image बनाता है; reviewer approve करता है; `main` में merge से SSH deploy trigger होता है; fix 15 मिनट में live। कुछ टूटे तो PR revert करो और वही pipeline पुराना code फिर deploy कर देती है।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# github-flow-basic.sh - one change from branch to PR using the gh CLI
set -euo pipefail                                          # strict mode

git switch main && git pull --ff-only                      # start from fresh main
git switch -c fix/cart-total                               # 1. new descriptive branch
echo "// fix total" >> cart.js                             # edit code
git add cart.js && git commit -m "fix(cart): correct total with discount"   # 2. commit
git push -u origin fix/cart-total                          # push branch to GitHub
gh pr create --fill --base main                            # 3. open PR using commit info (needs gh auth login)
gh pr checks --watch                                       # 4. wait for CI results
gh pr merge --squash --delete-branch                       # 6. merge after approval; delete branch
```

## 💻 Code / Config Example — Advanced

Full pipeline: CI on PRs, deploy on merge to `main` with image tagged by commit SHA. Example action versions; update them. Deploy step assumes secrets `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` and a registry.

```yaml
# .github/workflows/github-flow.yml
name: github-flow                                    # workflow name
on:
  pull_request:                                      # CI on PRs
    branches: [main]
  push:
    branches: [main]                                 # deploy on merge
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}    # one run per ref
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}   # cancel stale PR runs only, never prod deploys
permissions:
  contents: read                                     # least privilege
  packages: write                                    # push image to GHCR
jobs:
  test:
    runs-on: ubuntu-latest                           # runner
    steps:
      - uses: actions/checkout@v4                    # fetch code
      - uses: actions/setup-node@v4                  # install Node
        with:
          node-version: 20                           # version
          cache: npm                                 # cache deps
      - run: npm ci                                  # install
      - run: npm test                                # test
  build-deploy:
    needs: test                                      # after tests
    if: github.event_name == 'push'                  # skip for PRs
    runs-on: ubuntu-latest
    environment: production                          # supports approval rules and scoped secrets
    steps:
      - uses: actions/checkout@v4                    # fetch code
      - uses: docker/login-action@v3                 # log in to GHCR
        with:
          registry: ghcr.io                          # registry host
          username: ${{ github.actor }}              # user running workflow
          password: ${{ secrets.GITHUB_TOKEN }}      # built-in token
      - uses: docker/build-push-action@v6            # build and push image
        with:
          context: .                                 # build context
          push: true                                 # push after build
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}   # immutable tag = commit SHA
      - name: Deploy over SSH
        env:
          HOST: ${{ secrets.VPS_HOST }}              # server host
          USER_NAME: ${{ secrets.VPS_USER }}         # deploy user
          KEY: ${{ secrets.VPS_SSH_KEY }}            # private key
          IMAGE_TAG: ${{ github.sha }}               # tag to deploy
        run: |
          install -m 600 /dev/null key.pem           # private file with strict perms
          printf '%s\n' "$KEY" > key.pem             # write key
          ssh -i key.pem -o StrictHostKeyChecking=accept-new "$USER_NAME@$HOST" "IMAGE_TAG=$IMAGE_TAG /opt/app/deploy.sh"
```

---

## 🟠 My Stack Integration
- **Node/FastAPI/React in one repo:** one PR can touch all; use `paths` filters to build only changed services.
- **Nginx:** zero-downtime by running the new container on a spare port, health-check, then switch the upstream and reload Nginx.
- **AWS:** swap the SSH step for pushing to ECR and `aws ecs update-service` / SSM command.
- **Preview environments:** deploy each PR to `pr-123.example.com` and destroy it on close.

```nginx
# /etc/nginx/conf.d/app.conf - simple blue/green switch for GitHub Flow deploys
upstream app_backend {
    server 127.0.0.1:3001;        # "blue" container; deploy script changes this to 3002 ("green") then reloads
}
server {
    listen 80;                    # HTTP (add TLS with certbot in production)
    server_name example.com;      # your domain
    location / {
        proxy_pass http://app_backend;      # forward to active container
        proxy_set_header Host $host;        # preserve host header
    }
}
```
(Nginx snippet: not tested with `nginx -t` here.)

**Security:** required reviews + status checks on `main`; use GitHub Environments with required reviewers for production; secrets only in environment secrets; pin third-party actions to a version or commit SHA.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Merging with failing or skipped tests.
✅ Correct: Make CI a required status check.

❌ Mistake 2: Huge PRs (2000 lines).
✅ Correct: Small PRs under ~400 lines, reviewed within a day.

❌ Mistake 3: Deploying a mutable `latest` tag.
✅ Correct: Deploy the commit SHA tag so rollback is exact.

❌ Mistake 4: Half-finished features landing on `main`.
✅ Correct: Hide them behind feature flags.

---

## 🧠 Tricky Interview Question
`main` must always be deployable, but a feature needs 3 weeks. How do you merge safely?

**Answer:** Merge small increments behind a feature flag (off in production), keep each merge releasable, and enable the flag when the feature is complete. Avoid a 3-week branch because it creates conflicts and delays feedback.

---

## ⚫ Interview Questions + Answers

Q1: GitHub Flow vs Git Flow?
A1: GitHub Flow has only `main` plus short feature branches and deploys continuously; Git Flow adds develop/release/hotfix for scheduled releases.

Q2: What does "main is always deployable" imply?
A2: Everything merged is tested and reviewed; broken work stays on branches.

Q3: How do you roll back?
A3: `git revert` the merge commit via PR, or redeploy the previous image tag.

Q4: Squash merge or merge commit?
A4: Squash gives one clean commit per PR (good with Conventional Commits); merge commits preserve detail.

Q5: How do you test a PR before merge?
A5: CI plus a preview/staging deploy of the branch.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Web apps/SaaS, continuous deployment, small to medium teams.

❌ Avoid when:
- You must maintain several released versions in parallel.
- Weak automated tests (main will break).

---

## 📊 Visual Diagram

```
 main    o------o--------o----------o---->  each merge = deploy
          \      ^        \         ^
           \     |PR+CI    \        |PR+CI
 branch     o--o--o          o--o--o
        (feature/x)        (fix/y)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pull Request | Proposal to merge | merge का प्रस्ताव |
| Status check | Required CI result | ज़रूरी CI नतीजा |
| Feature flag | Runtime on/off switch | runtime पर on/off switch |
| Preview env | Temporary test deployment | अस्थायी test deployment |
| Revert | Undo via new commit | नया commit बनाकर undo |

---

## ⚡ 3-Line Summary
English: GitHub Flow = main is always deployable, short branches, PR, CI, merge, deploy.
It is simple and ideal for continuous delivery.
Use feature flags and required checks to keep main safe.
Hindi: GitHub Flow = main हमेशा deployable, छोटी branches, PR, CI, merge, deploy।
यह simple है और continuous delivery के लिए बढ़िया।
main को safe रखने के लिए feature flags और required checks use करो।

---

## ➡️ Next Topic
**20. Trunk Based Development** - the even faster variant with tiny commits and feature flags.

---
