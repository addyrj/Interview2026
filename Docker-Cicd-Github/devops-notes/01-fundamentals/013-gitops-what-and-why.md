# 13. GitOps — What + Why
# हिंदी में: GitOps — क्या है और क्यों

---

## 🔵 Simple Definition (English)
**GitOps** is a way of running infrastructure and deployments where **Git is the single source of truth**. You describe the desired state of your system (manifests, compose files, Terraform) in a Git repo; an automated agent continuously compares the real system with Git and fixes any difference. To deploy or roll back, you change Git (merge or revert a PR), not run commands on servers.

## 🔵 सरल परिभाषा (Hindi)
**GitOps** infrastructure और deployments चलाने का तरीका है जहाँ **Git ही सच का एकमात्र स्रोत (single source of truth)** है। आप system की चाही हुई state (manifests, compose files, Terraform) Git repo में लिखते हैं; एक automated agent असली system की Git से लगातार तुलना करता है और फ़र्क ठीक कर देता है। Deploy या rollback करने के लिए आप Git बदलते हैं (PR merge या revert), servers पर commands नहीं चलाते।

---

## 🔴 Problem it Solves
- **Push-based deploys with powerful credentials:** the CI system holds admin keys to production; if CI is hacked, production is hacked.
- **Drift:** someone runs `kubectl edit` or edits a file on the server; now Git says one thing and production another.
- **No audit trail:** "who changed this and why?" has no answer.
- **Hard rollback:** you must remember what the previous state was.

## 🔴 यह क्यों बना? (Hindi)
- **शक्तिशाली credentials वाले push-based deploys:** CI system के पास production की admin keys हैं; CI hack हुआ तो production hack।
- **Drift:** कोई `kubectl edit` चलाता है या server पर file बदलता है; अब Git कुछ और कहता है, production कुछ और।
- **कोई audit trail नहीं:** "यह किसने और क्यों बदला?" का जवाब नहीं।
- **कठिन rollback:** पिछली state क्या थी, यह याद रखना पड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 -> Config repo holds desired state (Kubernetes manifests / compose files) - separate from app code
Step 2 -> App CI builds image and pushes it (tag: git SHA), then opens a PR / commit that bumps the image tag in the config repo
Step 3 -> Humans review and merge the config PR (approval + audit trail)
Step 4 -> A GitOps agent inside the cluster/server (Argo CD, Flux) PULLS the repo regularly
Step 5 -> Agent compares Git (desired) with cluster (actual)
Step 6 -> If different, the agent applies Git's version (sync); manual changes are reverted (self-heal)
Step 7 -> Rollback = git revert; the agent syncs the old state back
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 -> Config repo में desired state (Kubernetes manifests / compose files), app code से अलग
Step 2 -> App CI image बनाकर push करता है (tag: git SHA), फिर config repo में image tag बदलने का PR / commit बनाता है
Step 3 -> इंसान config PR review और merge करते हैं (approval + audit trail)
Step 4 -> Cluster/server के अंदर GitOps agent (Argo CD, Flux) repo को नियमित PULL करता है
Step 5 -> Agent Git (चाहा हुआ) और cluster (असली) की तुलना करता है
Step 6 -> फ़र्क हो तो agent Git वाला version apply करता है (sync); manual changes वापस पलट जाते हैं (self-heal)
Step 7 -> Rollback = git revert; agent पुरानी state वापस sync कर देता है
```

---

## 🟡 Real World Example
**A fintech with 40 microservices on Kubernetes.** Developers merge to the app repo; CI builds `payments:abc123` and updates `deploy/payments/values.yaml` in the config repo. Argo CD notices, rolls out the new version, and shows the sync status on a dashboard. An engineer manually scales a deployment to 20 pods during debugging; Argo CD detects the drift and reverts it to the Git value unless the change is committed. When a bad release hits, the on-call engineer runs `git revert` and the platform returns to the last good state in minutes, with a clear audit trail.

**Your VPS (lightweight GitOps):** keep `docker-compose.yml` in a `deploy-config` repo; a small script on the VPS pulls the repo and runs `docker compose up -d`.

## 🟡 Real Example Hindi mein
**Kubernetes पर 40 microservices वाली fintech।** Developers app repo में merge करते हैं; CI `payments:abc123` बनाता है और config repo में `deploy/payments/values.yaml` अपडेट करता है। Argo CD देखता है, नया version rollout करता है और dashboard पर sync status दिखाता है। Debugging में कोई engineer manually deployment 20 pods पर scale करता है; Argo CD drift पकड़कर उसे Git की value पर लौटा देता है जब तक change commit न हो। बुरी release आए तो on-call `git revert` चलाता है और platform मिनटों में आखिरी अच्छी state पर लौटता है, साफ audit trail के साथ।

**आपका VPS (हल्का GitOps):** `docker-compose.yml` को `deploy-config` repo में रखिए; VPS पर एक छोटी script repo pull करके `docker compose up -d` चलाती है।

---

## 💻 Code / Config Example — Basic
An Argo CD Application that watches a Git path and keeps a cluster in sync. (Needs Argo CD installed on Kubernetes; not run here. Repo URL and namespace are examples.)

```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1            # Argo CD custom resource API
kind: Application                           # one deployed app tracked by Argo CD
metadata:
  name: payments-api                        # name of the Application
  namespace: argocd                         # Argo CD runs in this namespace
spec:
  project: default                          # Argo CD project (permission boundary)
  source:
    repoURL: https://github.com/your-org/deploy-config.git   # config repo (example URL)
    targetRevision: main                    # branch to track
    path: apps/payments-api                 # folder with manifests
  destination:
    server: https://kubernetes.default.svc  # the same cluster Argo CD runs in
    namespace: payments                     # target namespace
  syncPolicy:
    automated:                              # sync without manual click
      prune: true                           # delete resources removed from Git
      selfHeal: true                        # revert manual changes in the cluster
    syncOptions:
      - CreateNamespace=true                # create the namespace if missing
```

## 💻 Code / Config Example — Advanced
App CI that builds the image and updates the image tag in the config repo (the "GitOps handoff"), plus a VPS pull-based sync script.

```yaml
# .github/workflows/gitops-handoff.yml (in the APP repo)
name: Build and update config repo               # workflow name
on:
  push:
    branches: [main]                             # on merge to main
permissions:
  contents: read                                 # read this repo
  packages: write                                # push image to ghcr.io
jobs:
  build-and-bump:
    runs-on: ubuntu-latest                       # runner
    steps:
      - uses: actions/checkout@v4                # app code
      - uses: docker/login-action@v3             # registry login
        with:
          registry: ghcr.io                      # host
          username: ${{ github.actor }}          # user
          password: ${{ secrets.GITHUB_TOKEN }}  # token
      - uses: docker/build-push-action@v6        # build + push
        with:
          context: .                             # context
          push: true                             # publish
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}   # immutable tag
      - name: Bump image tag in config repo      # the only "deploy" action: change Git
        env:
          CONFIG_TOKEN: ${{ secrets.CONFIG_REPO_TOKEN }}   # fine-grained token with write access ONLY to the config repo
          NEW_TAG: ${{ github.sha }}             # tag to deploy
        run: |                                   # shell script
          set -euo pipefail                      # strict mode
          git clone "https://x-access-token:${CONFIG_TOKEN}@github.com/your-org/deploy-config.git" cfg   # clone config repo (example URL)
          cd cfg                                 # enter it
          sed -i "s|^\(\s*image: ghcr.io/.*:\).*|\1${NEW_TAG}|" apps/payments-api/deployment.yaml   # replace tag (adjust path/pattern)
          git config user.name  "ci-bot"         # commit identity
          git config user.email "ci-bot@example.com"   # commit identity
          git commit -am "deploy: payments-api ${NEW_TAG}"   # commit the change
          git push origin HEAD:main              # Argo CD / Flux notices and syncs
```

```bash
#!/usr/bin/env bash
# /opt/gitops/sync.sh - lightweight pull-based GitOps for a VPS (run by cron or a systemd timer every minute)
set -euo pipefail                                # stop on any error
cd /opt/deploy-config                            # local clone of the config repo (clone it once manually)
git fetch origin main --quiet                    # download latest commits without changing files
LOCAL=$(git rev-parse HEAD)                      # current commit on the server
REMOTE=$(git rev-parse origin/main)              # latest commit in Git
if [ "$LOCAL" != "$REMOTE" ]; then               # only act if Git changed
  git reset --hard origin/main                   # make server files EXACTLY match Git (manual edits are discarded)
  docker compose pull                            # fetch images referenced by the new compose file
  docker compose up -d --remove-orphans          # apply desired state, remove services deleted from Git
fi
```

---

## 🟠 My Stack Integration
- **VPS + Docker Compose:** the pull script above (cron `* * * * *`) gives GitOps-lite. The VPS only needs read access to the config repo (a read-only deploy key), so a hacked CI cannot SSH in.
- **Node/FastAPI/React:** the app repo builds images; the config repo says which tag runs where (`staging`, `production` folders).
- **Nginx:** config lives in the config repo and is mounted into the container; an Nginx change is a PR.
- **AWS/Kubernetes (EKS):** Argo CD or Flux in the cluster; Terraform for cluster itself.
- **Secrets are not stored in plain Git:** use Sealed Secrets, SOPS or External Secrets with AWS Secrets Manager.

```yaml
# docker-compose.yml in the config repo (desired state for production)
services:
  api:
    image: ghcr.io/you/api:3f9c2ab        # tag changed only through a reviewed commit (replace "you")
    restart: unless-stopped               # self-heal on crash
    env_file: /opt/secrets/api.env        # secrets live ONLY on the server, never in this repo
    ports:
      - "127.0.0.1:3000:3000"             # reachable by host Nginx only
```
Security: pull-based means no inbound cluster credentials in CI. Protect the config repo with branch protection and required reviews, since whoever can merge there can change production.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing plain-text secrets to the config repo.
✅ Correct: Encrypt with SOPS/Sealed Secrets or reference an external secret manager.

❌ Mistake 2: Same repo and same trigger for app code and deploy config.
✅ Correct: Separate repos (or folders) so config changes and app changes have different review and history.

❌ Mistake 3: Using the `latest` tag in manifests.
✅ Correct: Use immutable tags or digests so Git history equals real history.

❌ Mistake 4: Still running manual `kubectl`/SSH fixes in production.
✅ Correct: Fix through a PR; use manual access only for emergencies and commit afterwards.

❌ Mistake 5: Enabling `prune` and `selfHeal` without understanding them.
✅ Correct: Try them in staging first; they can delete resources not in Git.

---

## 🧠 Tricky Interview Question
**"With GitOps, an engineer needs an emergency fix in 2 minutes but the PR needs two approvals. What do you do?"**

Answer: Have a documented break-glass process: a faster path (single approver or on-call override) in Git rather than bypassing Git. The change is still a commit, so the audit trail and drift detection survive. If someone must edit the cluster directly, pause self-heal for that app, apply the fix, then commit the same change to Git immediately; otherwise the agent reverts it. Always record it in the post-mortem.

---

## ⚫ Interview Questions + Answers

Q1: What are the core principles of GitOps?
A1: (1) System described declaratively, (2) desired state versioned in Git, (3) approved changes applied automatically, (4) software agents continuously reconcile and alert on drift.

Q2: Push vs pull deployment?
A2: Push: CI runs commands against production (needs credentials). Pull: an agent inside the environment fetches desired state from Git. Pull is safer and corrects drift.

Q3: Argo CD vs Flux?
A3: Both are CNCF GitOps tools for Kubernetes. Argo CD has a rich UI and Application model; Flux is a set of lightweight controllers that is very Git/Kubernetes-native, often CLI-first.

Q4: How do you roll back in GitOps?
A4: `git revert` the commit (or reset the tag) and let the agent sync. History shows what happened.

Q5: Is GitOps only for Kubernetes?
A5: It started there because Kubernetes is declarative, but the idea applies to Terraform (Atlantis/Spacelift), Docker Compose with a pull script, and configuration generally.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running Kubernetes or many environments where consistency and auditability matter.
- You want PR-based review for every production change.

❌ Avoid when:
- A single small VPS with one app and one person: plain CI deploy is simpler (or GitOps-lite script).
- The team is not ready to give up manual production edits.

---

## 📊 Visual Diagram
```
 App repo ---(CI builds image: app:abc123)--->  Registry
    |
    +--- CI opens commit: "image: app:abc123" --> Config repo (Git = truth)
                                                       |
                                           pull / watch|
                                                       v
                                  +----------- GitOps agent (Argo CD / Flux) -----------+
                                  |  compare desired (Git) vs actual (cluster/server)   |
                                  +------------------------+----------------------------+
                                                           | sync / self-heal
                                                           v
                                             Production (Kubernetes / VPS)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GitOps | Git as source of truth for deployments | Deployments के लिए सच का स्रोत Git |
| Desired state | What Git says should run | Git के अनुसार जो चलना चाहिए |
| Reconciliation | Agent making actual match desired | असली को चाहे हुए जैसा बनाना |
| Drift | Actual differs from Git | असली का Git से अलग होना |
| Self-heal | Auto-revert manual changes | Manual changes अपने आप पलटना |
| Pull-based | Agent fetches changes itself | Agent खुद changes लाता है |
| Break-glass | Emergency access procedure | आपातकालीन पहुँच की प्रक्रिया |

---

## ⚡ 3-Line Summary
English: GitOps makes Git the single source of truth; an agent keeps the real system equal to Git.
Deploy and rollback are PRs and reverts, with a full audit trail and drift correction.
Pull-based sync is safer, but keep secrets out of plain Git.

Hindi: GitOps में Git सच का एकमात्र स्रोत है; agent असली system को Git के बराबर रखता है।
Deploy और rollback PR और revert हैं, पूरे audit trail और drift सुधार के साथ।
Pull-based sync ज़्यादा सुरक्षित है, लेकिन secrets को plain Git में न रखें।

---

## ➡️ Next Topic
**14. Git Basics** (next folder: Git and GitHub) — since everything in DevOps, from pipelines to GitOps, starts with Git, learn it properly.
