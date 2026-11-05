# 395. AWS Secrets in GitHub Actions
# हिंदी में: GitHub Actions में AWS Secrets

---

## 🔵 Simple Definition (English)
Two places can hold secrets for your pipeline: **GitHub Secrets** (encrypted values in repo/environment settings, injected as `${{ secrets.X }}`) and **AWS Secrets Manager** (a managed vault with encryption, rotation and audit, read at runtime through IAM). Best practice: keep only bootstrap values in GitHub, keep real application secrets in AWS, and fetch them just in time.

## 🔵 सरल परिभाषा (Hindi)
Pipeline के secrets दो जगह रखे जा सकते हैं: **GitHub Secrets** (repo/environment settings में encrypted values, `${{ secrets.X }}` से inject होती हैं) और **AWS Secrets Manager** (encryption, rotation और audit वाला managed vault, IAM से runtime पर पढ़ा जाता है)। Best practice: GitHub में सिर्फ bootstrap values रखें, असली application secrets AWS में रखें, और ज़रूरत के समय fetch करें।

---

## 🔴 Problem it Solves
Secrets copied into every repo, every environment and every developer's `.env` file lead to: no rotation, no audit ("who read the DB password?"), many copies to update when a secret changes, and leaks via logs or Docker image layers.

A central vault means one source of truth, rotation without redeploying, per-secret IAM access, and CloudTrail records on every read.

## 🔴 यह क्यों बना? (Hindi)
हर repo, हर environment और हर developer की `.env` में copy किए secrets से ये समस्याएँ आती हैं: rotation नहीं, audit नहीं ("DB password किसने पढ़ा?"), secret बदलने पर कई copies update करनी पड़ती हैं, और logs या Docker image layers से leak।

Central vault में एक source of truth, redeploy के बिना rotation, हर secret पर IAM access और हर read का CloudTrail record मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create the secret in Secrets Manager: prod/orders-api/db  (JSON or string)
Step 2 → Give the CI role secretsmanager:GetSecretValue on that exact ARN only
Step 3 → Workflow logs in with OIDC (topic 394)
Step 4 → aws-actions/aws-secretsmanager-get-secrets reads the secret
Step 5 → Values become masked env vars for later steps (or fetch with the CLI)
Step 6 → Prefer: do NOT pass to the build; let the running app fetch at startup
         using its own task/instance role
Step 7 → Rotation: Secrets Manager rotates the DB password; app re-reads on next start
         or on cache refresh
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Secrets Manager में secret बनाएँ: prod/orders-api/db  (JSON या string)
Step 2 → CI role को सिर्फ उसी ARN पर secretsmanager:GetSecretValue दें
Step 3 → Workflow OIDC से login करता है (topic 394)
Step 4 → aws-actions/aws-secretsmanager-get-secrets secret पढ़ता है
Step 5 → Values आगे के steps के लिए masked env vars बन जाती हैं (या CLI से fetch करें)
Step 6 → बेहतर: build में pass न करें; चलता हुआ app अपने task/instance role से
         startup पर खुद fetch करे
Step 7 → Rotation: Secrets Manager DB password rotate करता है; app अगले start या cache refresh पर दोबारा पढ़ता है
```

---

## 🟡 Real World Example
A payments API (Node.js on ECS) needs `DB_PASSWORD` and `STRIPE_KEY`. Previously both were GitHub secrets baked into a `.env` during the Docker build, so anyone with `docker history` could read them. Now the ECS task definition declares `secrets: [{name: DB_PASSWORD, valueFrom: <secret ARN>}]`; ECS injects them at start using the task execution role. GitHub holds only `AWS_ROLE_ARN`. Rotating the DB password needs no code change or rebuild.

## 🟡 Real Example Hindi mein
एक payments API (ECS पर Node.js) को `DB_PASSWORD` और `STRIPE_KEY` चाहिए। पहले दोनों GitHub secrets थे जो Docker build में `.env` में baked हो जाते थे, इसलिए `docker history` से कोई भी पढ़ सकता था। अब ECS task definition में `secrets: [{name: DB_PASSWORD, valueFrom: <secret ARN>}]` है; ECS इन्हें start पर task execution role से inject करता है। GitHub में सिर्फ `AWS_ROLE_ARN` है। DB password rotate करने के लिए code बदलना या rebuild नहीं चाहिए।

---

## 💻 Code / Config Example — Basic

GitHub Secrets usage with safe habits.

```yaml
name: github-secrets-basic                       # workflow name
on:
  workflow_dispatch: {}                          # manual run
jobs:
  deploy:
    runs-on: ubuntu-latest                       # runner
    environment: production                      # environment-scoped secrets + approvals
    steps:
      - name: Use a secret via env, not inline   # avoids shell-injection and keeps it masked
        env:
          API_TOKEN: ${{ secrets.API_TOKEN }}    # secret value placed in an env var
        run: |                                   # script uses the env var
          curl -sf -H "Authorization: Bearer $API_TOKEN" https://api.example.com/ping   # never echo the token
```

Create an AWS secret (JSON) once:

```bash
# store DB credentials as JSON in Secrets Manager (encrypted with KMS)
aws secretsmanager create-secret \
  --name prod/orders-api/db \
  --description "Orders API database credentials" \
  --secret-string '{"username":"orders","password":"CHANGE_ME_LONG_RANDOM"}'
```

## 💻 Code / Config Example — Advanced

Fetching in the workflow (for steps that truly need it, e.g. running migrations), and injecting at runtime for ECS. Action version and inputs are examples; confirm in the action's README.

```yaml
name: migrate-and-deploy                         # workflow name
on:
  push:
    branches: [main]                             # deploy from main
permissions:
  id-token: write                                # OIDC
  contents: read                                 # checkout
jobs:
  migrate:
    runs-on: ubuntu-latest                       # runner
    environment: production                      # protected environment
    steps:
      - uses: actions/checkout@v4                # code with migration files
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ap-south-1
      - name: Read DB secret                     # puts values in masked env vars
        uses: aws-actions/aws-secretsmanager-get-secrets@v2
        with:
          secret-ids: |                          # alias,secret-name  -> env var prefix DB
            DB, prod/orders-api/db
          parse-json-secrets: true               # DB_USERNAME and DB_PASSWORD env vars
      - name: Run migrations                     # DB_* are available here
        run: npx prisma migrate deploy           # example migration tool
        env:
          DATABASE_URL: postgresql://${{ env.DB_USERNAME }}:${{ env.DB_PASSWORD }}@db.internal:5432/orders   # built at runtime
```

ECS task definition that injects secrets at container start (JSON fragment; the app never sees GitHub):

```json
{
  "containerDefinitions": [
    {
      "name": "api",
      "image": "111122223333.dkr.ecr.ap-south-1.amazonaws.com/orders-api:PLACEHOLDER",
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:ap-south-1:111122223333:secret:prod/orders-api/db-AbCdEf:password::"
        }
      ]
    }
  ]
}
```

The task **execution role** needs `secretsmanager:GetSecretValue` on that ARN (and `kms:Decrypt` if you use a custom KMS key).

---

## 🟠 My Stack Integration
- **Node.js**: read `process.env.DB_PASSWORD` as usual; on EC2 use the AWS SDK v3 `GetSecretValueCommand` at boot and cache the result.
- **FastAPI**: `boto3.client('secretsmanager').get_secret_value(...)` in the startup event; keep in memory, not on disk.
- **React**: browser code can never hold secrets. Only public config (API URL) is built in. Any "secret" in `VITE_*`/`NEXT_PUBLIC_*` is public.
- **Nginx**: basic-auth files or TLS private keys come from the vault into a tmpfs/volume at start, not into the image.
- **VPS**: no IAM role; either use GitHub environment secrets copied over SSH to a `chmod 600` env file, or move to EC2 so the instance role can read Secrets Manager directly.
- **Cost note**: Secrets Manager charges per secret per month plus per API calls; Parameter Store standard parameters are free (topic 396).

```bash
# FastAPI/EC2 example: fetch at deploy time into a root-only env file (not in git, not in the image)
aws secretsmanager get-secret-value --secret-id prod/orders-api/db --query SecretString --output text \
  | jq -r 'to_entries[] | "DB_\(.key | ascii_upcase)=\(.value)"' > /opt/app/.env.prod   # DB_USERNAME=..., DB_PASSWORD=...
chmod 600 /opt/app/.env.prod                     # only the owner can read it
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Passing secrets as Docker `ARG`/`ENV` during build.
✅ Correct: Use BuildKit secret mounts (`--secret`) for build-time needs and runtime injection for the rest; build args are visible in `docker history`.

❌ Mistake 2: `echo ${{ secrets.X }}` or `set -x` in scripts, or base64 "hiding" in logs.
✅ Correct: GitHub masks exact values only; transformed values (base64, substrings) are not masked. Never print secrets.

❌ Mistake 3: `run: ./deploy.sh ${{ secrets.TOKEN }}` (inline expansion).
✅ Correct: Pass via `env:` to avoid shell injection and process-list exposure.

❌ Mistake 4: One repo-level secret shared by dev and prod.
✅ Correct: Environment secrets with required reviewers for production.

❌ Mistake 5: Secret in a structured value (JSON) not masked per field.
✅ Correct: Use `parse-json-secrets` or call `echo "::add-mask::$VALUE"` for derived values.

---

## 🧠 Tricky Interview Question
GitHub masks secrets in logs. A teammate says "so printing a secret in base64 is safe." Is it?

Answer: No. Masking is a string match on the exact stored value. `echo $SECRET | base64` outputs a different string that is not masked, so the secret is trivially recoverable from the log. The same holds for splitting, reversing or URL-encoding. Treat logs as public to everyone with read access, never print secrets in any form, and rotate if it happened.

---

## ⚫ Interview Questions + Answers

Q1: GitHub Secrets vs AWS Secrets Manager?
A1: GitHub Secrets: simple, tied to CI, no rotation or audit of reads. Secrets Manager: central vault, automatic rotation, fine-grained IAM, CloudTrail audit, usable by runtime workloads, costs money.

Q2: Where should a running app get its secrets?
A2: From the platform at runtime with its own role (ECS `secrets`, Lambda env from SSM, SDK call at boot), not from files baked into images or pushed from CI.

Q3: Are secrets available to workflows from forked PRs?
A3: No, not for `pull_request` from forks. `pull_request_target` does expose them, which is dangerous when combined with untrusted code checkout.

Q4: What is secret rotation and why does it matter?
A4: Regularly replacing credentials (Secrets Manager can run a Lambda that changes the DB password). It limits damage from leaks and removes human handling.

Q5: How do you detect committed secrets?
A5: GitHub secret scanning and push protection, plus tools like gitleaks/trufflehog in CI; rotate anything found, since git history is permanent.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Application secrets used at runtime in AWS (DB, third-party keys)
- You need rotation, audit and per-secret access control
- Several services share the same credential

❌ Avoid when:
- A handful of non-sensitive config values (use Parameter Store, cheaper)
- CI-only tokens like a Slack webhook (GitHub environment secret is fine)

---

## 📊 Visual Diagram
```
 GitHub repo/env settings          AWS Secrets Manager (KMS encrypted)
 +---------------------+           +----------------------------------+
 | AWS_ROLE_ARN (var)  |           | prod/orders-api/db  (rotating)   |
 | SLACK_WEBHOOK       |           | prod/orders-api/stripe           |
 +----------+----------+           +----------+-----------------------+
            |                                 ^ GetSecretValue (IAM, audited)
            v                                 |
   GitHub Actions --OIDC--> CI role ----------+  (migrations only)
                                              |
   ECS task / EC2 / Lambda --- own role ------+  (runtime, preferred)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Secret | Sensitive value (password, token) | संवेदनशील मान (password, token) |
| Masking | Hiding exact secret strings in logs | logs में exact secret छिपाना |
| Rotation | Replacing a credential on schedule | समय-समय पर credential बदलना |
| KMS | AWS key service for encryption | encryption के लिए AWS key service |
| Environment secret | Secret scoped to one environment | एक environment तक सीमित secret |
| Execution role | Role ECS uses to start tasks | ECS जिस role से task शुरू करता है |

---

## ⚡ 3-Line Summary
English: Keep only bootstrap values in GitHub; keep app secrets in AWS Secrets Manager.
English: Fetch with OIDC and a narrow role, or better let the runtime inject them at start.
English: Never print, bake into images, or rely on log masking for derived values.
Hindi: GitHub में सिर्फ bootstrap values रखें; app secrets AWS Secrets Manager में रखें।
Hindi: OIDC और संकरे role से fetch करें, या बेहतर है कि runtime खुद start पर inject करे।
Hindi: कभी print न करें, images में न डालें, और derived values के लिए log masking पर भरोसा न करें।

---

## ➡️ Next Topic
**396. Parameter Store in GitHub Actions**: for plain config and cheap encrypted values, SSM Parameter Store is the lighter sibling of Secrets Manager.
