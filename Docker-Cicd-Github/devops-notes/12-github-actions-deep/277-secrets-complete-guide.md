# 277. Secrets — Complete Guide
# हिंदी में: Secrets — पूरी गाइड

---

## 🔵 Simple Definition (English)
GitHub **Secrets** are encrypted values (passwords, API keys, SSH private keys, cloud credentials) stored at repository, environment or organization level. Workflows read them through `${{ secrets.NAME }}`; GitHub masks them in logs and never shows them again after saving.

## 🔵 सरल परिभाषा (Hindi)
GitHub **Secrets** encrypted values हैं (passwords, API keys, SSH private keys, cloud credentials) जो repository, environment या organization level पर store होती हैं। Workflows इन्हें `${{ secrets.NAME }}` से पढ़ते हैं; GitHub logs में इन्हें mask करता है और save के बाद दोबारा नहीं दिखाता।

---

## 🔴 Problem it Solves
Developers used to commit `.env` files or paste keys in YAML. Once pushed, a key lives forever in git history and in every fork/clone; bots scan GitHub for AWS keys within minutes. CI still needs credentials to push images and SSH into the VPS, so it needs a safe vault attached to the repo.

## 🔴 यह क्यों बना? (Hindi)
Developers `.env` files commit कर देते थे या keys को YAML में paste करते थे। एक बार push होने पर key git history और हर fork/clone में हमेशा रहती है; bots कुछ मिनटों में GitHub से AWS keys ढूँढ लेते हैं। CI को फिर भी image push करने और VPS में SSH करने के लिए credentials चाहिए, इसलिए repo से जुड़ी एक सुरक्षित vault चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Admin saves secret in Settings (encrypted with libsodium sealed box)
Step 2 → Workflow run starts; secrets are NOT available to fork PRs by default
Step 3 → Runner requests only the secrets referenced in the workflow
Step 4 → ${{ secrets.NAME }} is substituted; value is registered as a mask
Step 5 → Any occurrence of the value in logs is replaced with ***
Step 6 → Job ends; runner VM is destroyed (no leftover on GitHub-hosted runners)
```

Scopes: repository, environment (with approvals), organization (shared by selected repos).

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Admin Settings में secret save करता है (libsodium sealed box से encrypted)
Step 2 → Workflow run शुरू होता है; fork PRs को default में secrets नहीं मिलते
Step 3 → Runner सिर्फ वही secrets लेता है जो workflow में reference हुए हैं
Step 4 → ${{ secrets.NAME }} replace होता है; value mask list में जुड़ जाती है
Step 5 → Logs में value जहाँ भी दिखे, *** से बदल जाती है
Step 6 → Job खत्म, runner VM नष्ट (GitHub-hosted runners पर कुछ नहीं बचता)
```

Scopes: repository, environment (approvals के साथ), organization (चुने हुए repos में shared)।

---

## 🟡 Real World Example
Your pipeline needs: `DOCKERHUB_TOKEN` to push images, `VPS_SSH_KEY` and `VPS_HOST` to deploy, `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` (or better, OIDC) for S3/ECR. A past incident: a developer printed `env` for debugging; masking hid exact matches, but a base64 version of the token was visible. The team then rotated the token and moved to short-lived OIDC credentials.

## 🟡 Real Example Hindi mein
आपके pipeline को चाहिए: image push के लिए `DOCKERHUB_TOKEN`, deploy के लिए `VPS_SSH_KEY` और `VPS_HOST`, S3/ECR के लिए `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` (या बेहतर, OIDC)। पुरानी घटना: एक developer ने debugging के लिए `env` print किया; masking exact match छुपाता है, पर token का base64 रूप दिख गया। Team ने token rotate किया और short-lived OIDC credentials पर चली गई।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/secrets-basic.yml
name: secrets-basic                    # workflow name
on:
  push:
    branches: [main]                   # only trusted branch

jobs:
  push-image:
    runs-on: ubuntu-latest             # runner
    steps:
      - uses: actions/checkout@v4      # example version
      - name: Docker login
        env:
          DOCKERHUB_USER: ${{ secrets.DOCKERHUB_USER }}     # username stored as secret
          DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}   # access token, not password
        run: |
          # --password-stdin keeps the token out of the process list and shell history
          echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USER" --password-stdin
      - name: Build and push
        run: |
          docker build -t "${{ secrets.DOCKERHUB_USER }}/my-api:${{ github.sha }}" .   # build
          docker push  "${{ secrets.DOCKERHUB_USER }}/my-api:${{ github.sha }}"         # push
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/secrets-advanced.yml
name: secrets-advanced                 # workflow name
on:
  push:
    branches: [main]

permissions:
  contents: read                       # least privilege for GITHUB_TOKEN

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production            # environment secrets + required reviewers
    steps:
      - name: Install SSH key
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}       # multi-line private key
          KNOWN_HOSTS: ${{ secrets.VPS_KNOWN_HOSTS }}  # pinned host key (ssh-keyscan output)
        run: |
          install -m 700 -d ~/.ssh                    # create ~/.ssh with 700
          printf '%s\n' "$SSH_KEY" > ~/.ssh/id_ed25519   # write key, keep newlines
          chmod 600 ~/.ssh/id_ed25519                    # ssh refuses keys that are too open
          printf '%s\n' "$KNOWN_HOSTS" > ~/.ssh/known_hosts   # prevents MITM, no blind trust
      - name: Mask a derived value
        run: |
          TOKEN=$(openssl rand -hex 16)               # runtime-generated sensitive value
          echo "::add-mask::$TOKEN"                   # tell runner to mask it in logs
      - name: Deploy
        run: |
          ssh -i ~/.ssh/id_ed25519 deploy@"${{ secrets.VPS_HOST }}" \
            "cd /srv/app && docker compose pull && docker compose up -d"   # pull new image
      - name: Cleanup key
        if: always()                                  # remove even when deploy fails
        run: rm -f ~/.ssh/id_ed25519                  # good hygiene (VM is destroyed anyway)
```
Not run locally; bash syntax checked, YAML parsed. `VPS_KNOWN_HOSTS` is produced once with `ssh-keyscan -t ed25519 host` and verified by you.

---

## 🟠 My Stack Integration
Secrets for Node.js/FastAPI: DB URLs, JWT secret, third-party keys go on the VPS inside a root-owned `.env` (mode 600) or are written from GitHub secrets during deploy. React gets no secrets. Prefer OIDC for AWS so there are no long-lived keys.

```yaml
# snippet: AWS via OIDC instead of stored access keys
permissions:
  id-token: write                      # allow requesting an OIDC token
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@v4   # example version
    with:
      role-to-assume: arn:aws:iam::123456789012:role/gha-deploy   # example ARN
      aws-region: ap-south-1           # Mumbai region
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `echo ${{ secrets.TOKEN }}` or `set -x` in scripts.
✅ Correct: Pass through `env:` and never print; avoid debug tracing near secrets.

❌ Mistake 2: Structured secrets (JSON) stored as one blob; masking fails on parts of it.
✅ Correct: Store each sensitive value as its own secret.

❌ Mistake 3: Passing secrets as `docker build --build-arg`; they stay in image history.
✅ Correct: Use BuildKit `--secret` mounts.

❌ Mistake 4: Using long-lived admin keys and never rotating.
✅ Correct: Least-privilege keys, rotation schedule, prefer OIDC.

❌ Mistake 5: Running untrusted PR code with `pull_request_target` and secrets.
✅ Correct: Use `pull_request` for fork code (no secrets) and gate privileged jobs.

---

## 🧠 Tricky Interview Question
Secrets are masked in logs, so is it safe for a workflow to run code from any contributor's pull request?

Answer: No. Masking only hides exact text in logs. Malicious code in the PR can send `$SECRET` to an attacker's server over the network or encode it (base64, reversed) to bypass masking. That is why fork PRs do not receive secrets, why environments need approvals, and why you must not combine `pull_request_target` with checking out untrusted code.

---

## ⚫ Interview Questions + Answers

Q1: How are secrets stored?
A1: Encrypted (libsodium sealed boxes) before reaching GitHub and decrypted only on the runner for the job.

Q2: Can you read a secret back in the UI?
A2: No. You can only update or delete it.

Q3: Secret size limit?
A3: 48 KB per secret; for larger files, encrypt with gpg and store the passphrase as the secret.

Q4: Are secrets passed to reusable workflows automatically?
A4: Not unless you pass them explicitly or use `secrets: inherit`.

Q5: How do you reduce secrets risk?
A5: OIDC short-lived creds, environment protection, least privilege, rotation, no secrets in forks, secret scanning and push protection.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tokens, passwords, private keys, API keys for CI/CD.

❌ Avoid when:
- Non-sensitive config (use `vars`).
- Application runtime secrets that should live in a secrets manager (AWS Secrets Manager / SSM) rather than in CI.

---

## 📊 Visual Diagram
```
 Settings > Secrets (encrypted)
        |
        |  only referenced names are sent
        v
 +--------------------+    log output    +------------------+
 | Runner (ephemeral) | ---------------> | ***** masked     |
 | env: TOKEN=****    |                  +------------------+
 +--------+-----------+
          | ssh / docker login / aws
          v
     VPS / Registry / AWS      <-- fork PRs: NO secrets
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Secret | Encrypted credential | Encrypted credential |
| Masking | Hiding value in logs as *** | Logs में *** दिखाना |
| OIDC | Short-lived token exchange with cloud | Cloud के साथ छोटी अवधि वाले tokens |
| Rotation | Replacing a key regularly | Key नियमित बदलना |
| Least privilege | Minimum permissions only | न्यूनतम अनुमति |

---

## ⚡ 3-Line Summary
English: Secrets hold credentials encrypted and masked, read by `secrets.NAME`.
Masking is not a security boundary; do not run untrusted code with secrets.
Prefer OIDC, least privilege, environments and rotation.

Hindi: Secrets credentials को encrypted और masked रखते हैं, `secrets.NAME` से पढ़े जाते हैं।
Masking कोई security boundary नहीं है; untrusted code के साथ secrets मत चलाओ।
OIDC, least privilege, environments और rotation को प्राथमिकता दो।

---

## ➡️ Next Topic
**278. GitHub Secrets Setup** — click-by-click and CLI (`gh secret set`) steps to create repository secrets.
