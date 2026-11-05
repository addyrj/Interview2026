# 396. Parameter Store in GitHub Actions
# हिंदी में: GitHub Actions में Parameter Store

---

## 🔵 Simple Definition (English)
**AWS Systems Manager Parameter Store** is a hierarchical key-value store for configuration (`/orders/prod/api_url`) and secrets (`SecureString`, encrypted with KMS). Standard parameters are free. In GitHub Actions you read them with the AWS CLI after an OIDC login, so config lives in AWS, not hard-coded in workflows.

## 🔵 सरल परिभाषा (Hindi)
**AWS Systems Manager Parameter Store** configuration (`/orders/prod/api_url`) और secrets (`SecureString`, KMS से encrypted) के लिए hierarchical key-value store है। Standard parameters मुफ़्त हैं। GitHub Actions में OIDC login के बाद AWS CLI से इन्हें पढ़ा जाता है, यानी config workflows में hard-code नहीं बल्कि AWS में रहता है।

---

## 🔴 Problem it Solves
Config scattered across `.env` files, workflow YAML and GitHub variables drifts: staging points to the prod DB by mistake, a changed URL requires editing 5 repos, and nobody knows which value is live.

Parameter Store gives a path-based tree per app and environment (`/orders/prod/*`), versioned history, IAM per path, and zero cost for standard parameters. It is also a cheap alternative to Secrets Manager when you do not need automatic rotation.

## 🔴 यह क्यों बना? (Hindi)
`.env` files, workflow YAML और GitHub variables में बिखरा config drift करता है: staging गलती से prod DB पर point करता है, URL बदलने के लिए 5 repos edit करने पड़ते हैं, और पता नहीं कौन सी value live है।

Parameter Store हर app और environment के लिए path-based tree (`/orders/prod/*`), versioned history, path के हिसाब से IAM और standard parameters पर शून्य cost देता है। जब automatic rotation नहीं चाहिए तो यह Secrets Manager का सस्ता विकल्प भी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create parameters under a path: /orders/prod/db_host (String),
         /orders/prod/db_password (SecureString)
Step 2 → CI role gets ssm:GetParametersByPath on arn:...:parameter/orders/prod/*
         (+ kms:Decrypt for SecureString key)
Step 3 → Workflow assumes the role via OIDC
Step 4 → "aws ssm get-parameters-by-path --path /orders/prod --with-decryption"
Step 5 → Mask each sensitive value (::add-mask::) and write to $GITHUB_ENV / file
Step 6 → Use them in the step (migration, config render) or let the app read them itself
Step 7 → Change a value later: put-parameter --overwrite; version history is kept
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Path के नीचे parameters बनाएँ: /orders/prod/db_host (String),
         /orders/prod/db_password (SecureString)
Step 2 → CI role को arn:...:parameter/orders/prod/* पर ssm:GetParametersByPath दें
         (+ SecureString की key के लिए kms:Decrypt)
Step 3 → Workflow OIDC से role assume करता है
Step 4 → "aws ssm get-parameters-by-path --path /orders/prod --with-decryption"
Step 5 → हर sensitive value को mask करें (::add-mask::) और $GITHUB_ENV / file में लिखें
Step 6 → Step में इस्तेमाल करें (migration, config render) या app खुद पढ़े
Step 7 → बाद में बदलना: put-parameter --overwrite; version history बनी रहती है
```

---

## 🟡 Real World Example
A SaaS runs `staging` and `prod` in one AWS account. Both use the same workflow file, which takes `ENV=staging|prod` and loads everything under `/crm/$ENV/`. Feature flags like `/crm/prod/max_upload_mb` are edited by the ops team in the console without a code change; the next deploy (or app restart) picks it up. The DB password is a SecureString under the same path. IAM lets the staging role read only `/crm/staging/*`, so staging can never read prod secrets.

## 🟡 Real Example Hindi mein
एक SaaS `staging` और `prod` एक ही AWS account में चलाता है। दोनों एक ही workflow file इस्तेमाल करते हैं जो `ENV=staging|prod` लेकर `/crm/$ENV/` के नीचे सब कुछ load करती है। `/crm/prod/max_upload_mb` जैसे feature flags ops टीम console से बिना code बदले edit करती है; अगला deploy (या app restart) उसे उठा लेता है। DB password उसी path के नीचे SecureString है। IAM staging role को सिर्फ `/crm/staging/*` पढ़ने देता है, इसलिए staging कभी prod secrets नहीं पढ़ सकता।

---

## 💻 Code / Config Example — Basic

Create and read parameters with the CLI.

```bash
# plain config value (String type)
aws ssm put-parameter --name /orders/prod/api_url --type String --value "https://api.example.com"

# secret value (SecureString uses the default aws/ssm KMS key unless --key-id is given)
aws ssm put-parameter --name /orders/prod/db_password --type SecureString --value "CHANGE_ME_LONG_RANDOM"

# read one value; --with-decryption is required for SecureString
aws ssm get-parameter --name /orders/prod/db_password --with-decryption --query Parameter.Value --output text
```

```yaml
name: ssm-basic                                  # workflow name
on:
  workflow_dispatch: {}                          # manual trigger
permissions:
  id-token: write                                # OIDC
  contents: read                                 # checkout
jobs:
  read-config:
    runs-on: ubuntu-latest                       # runner
    steps:
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ap-south-1
      - name: Read one parameter                 # fetch API URL
        run: |
          URL=$(aws ssm get-parameter --name /orders/prod/api_url --query Parameter.Value --output text)   # plain value
          echo "API_URL=$URL" >> "$GITHUB_ENV"   # make it available to later steps
      - run: echo "Deploying against $API_URL"   # safe: not a secret
```

## 💻 Code / Config Example — Advanced

Load a whole path, mask secrets, build a `.env`, then deploy. Also IAM for least privilege.

```yaml
name: deploy-with-ssm                            # workflow name
on:
  push:
    branches: [main]                             # deploy trigger
permissions:
  id-token: write                                # OIDC
  contents: read                                 # checkout
env:
  APP_ENV: prod                                  # environment name used in the parameter path
jobs:
  deploy:
    runs-on: ubuntu-latest                       # runner
    environment: production                      # approvals / environment scope
    steps:
      - uses: actions/checkout@v4                # code
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ap-south-1
      - name: Load parameters into a .env file   # one API call for the whole path
        shell: bash
        run: |
          set -euo pipefail                      # fail on error, unset var, pipe failure
          aws ssm get-parameters-by-path \
            --path "/orders/${APP_ENV}/" --recursive --with-decryption \
            --query 'Parameters[].[Name,Value,Type]' --output json > params.json   # fetch all
          : > .env.build                         # create empty env file
          jq -c '.[]' params.json | while read -r row; do   # iterate over each parameter
            NAME=$(echo "$row" | jq -r '.[0]' | awk -F/ '{print toupper($NF)}')   # last path part, uppercased
            VALUE=$(echo "$row" | jq -r '.[1]')  # parameter value
            TYPE=$(echo "$row" | jq -r '.[2]')   # String / SecureString
            if [ "$TYPE" = "SecureString" ]; then echo "::add-mask::$VALUE"; fi   # mask secret values in logs
            printf '%s=%s\n' "$NAME" "$VALUE" >> .env.build   # write KEY=VALUE
          done
          rm -f params.json                      # remove the raw dump
          chmod 600 .env.build                   # restrict file permissions
      - name: Copy env file to server and restart   # example VPS/EC2 target
        env:
          SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }} # deploy key as environment secret
        run: |
          install -m 600 /dev/null key           # create key file with safe mode
          printf '%s\n' "$SSH_KEY" > key         # write private key
          scp -i key -o StrictHostKeyChecking=yes .env.build deploy@server:/opt/app/.env   # needs known_hosts set up
          ssh -i key deploy@server 'cd /opt/app && docker compose up -d'   # restart with new config
      - name: Cleanup                            # always remove secrets from the runner
        if: always()
        run: rm -f .env.build key
```

Least-privilege IAM for the CI role (JSON, attach as policy):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["ssm:GetParametersByPath", "ssm:GetParameter", "ssm:GetParameters"],
      "Resource": "arn:aws:ssm:ap-south-1:111122223333:parameter/orders/prod/*"
    },
    {
      "Effect": "Allow",
      "Action": "kms:Decrypt",
      "Resource": "arn:aws:kms:ap-south-1:111122223333:key/11111111-2222-3333-4444-555555555555"
    }
  ]
}
```

The `StrictHostKeyChecking=yes` line needs a populated `known_hosts` file (see topic 389). The script is an example, not run against a live AWS account.

---

## 🟠 My Stack Integration
- **Node.js**: at boot, call SDK v3 `GetParametersByPathCommand` and merge into config; or have the deploy step render `.env`.
- **FastAPI**: `boto3.client('ssm').get_parameters_by_path(Path='/orders/prod/', WithDecryption=True, Recursive=True)` in the startup handler.
- **React**: build-time public values only: `VITE_API_URL=$(aws ssm get-parameter ...)` before `npm run build`. Never SecureStrings.
- **Nginx**: render `upstream` hosts or allowed IPs into the config in CI from parameters, then `nginx -t` before reload.
- **ECS**: task definition `secrets: [{name, valueFrom: arn:aws:ssm:...:parameter/orders/prod/db_password}]` injects directly.
- **Lambda**: use the Parameters and Secrets Lambda Extension to read and cache with low latency.

```yaml
# ECS task-definition fragment (as YAML for readability; real file is JSON)
secrets:
  - name: DB_PASSWORD                            # env var inside the container
    valueFrom: arn:aws:ssm:ap-south-1:111122223333:parameter/orders/prod/db_password   # SSM parameter ARN
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Storing a password as plain `String`.
✅ Correct: Use `SecureString`; plain strings are readable by anyone with `ssm:GetParameter`.

❌ Mistake 2: Forgetting `--with-decryption`, so the value comes back as ciphertext.
✅ Correct: Add the flag and grant `kms:Decrypt`.

❌ Mistake 3: IAM `Resource: "*"` for ssm actions.
✅ Correct: Scope by path prefix; separate prod and staging paths and roles.

❌ Mistake 4: Hitting the API rate limit by fetching each parameter in a loop.
✅ Correct: One `get-parameters-by-path` (10 per page, handle pagination) or `get-parameters` (max 10 names).

❌ Mistake 5: Using Parameter Store where you need automatic rotation.
✅ Correct: Use Secrets Manager (topic 395) for rotating DB credentials.

---

## 🧠 Tricky Interview Question
Your workflow reads 25 parameters by path, but only 10 show up in `.env`. No error was raised. Why?

Answer: `get-parameters-by-path` returns at most 10 parameters per call and gives a `NextToken` for more. The AWS CLI v2 normally paginates automatically, but a hand-written SDK call or `--no-paginate` returns only the first page. Also the path may not be `--recursive`, so nested paths like `/orders/prod/db/host` are skipped. Always paginate (SDK paginators) and set `--recursive` for nested trees.

---

## ⚫ Interview Questions + Answers

Q1: Parameter Store vs Secrets Manager?
A1: Parameter Store: free standard tier, hierarchical, good for config and simple secrets, no native rotation. Secrets Manager: paid, built-in rotation, cross-account sharing, replication; use for DB credentials needing rotation.

Q2: Standard vs advanced parameters?
A2: Standard: up to 4 KB, 10,000 parameters, free. Advanced: up to 8 KB, more parameters, parameter policies (expiry), paid per parameter. Check current limits in AWS docs.

Q3: How do you separate environments?
A3: Path prefix (`/app/prod/`, `/app/staging/`) with IAM policies on each prefix, and ideally separate AWS accounts.

Q4: How can the app pick up changed values without redeploy?
A4: Read at runtime with a cache and a TTL, or trigger a restart through EventBridge on parameter change. Build-time injection needs a redeploy.

Q5: Does GitHub mask SecureString values automatically?
A5: No, GitHub only masks registered secrets and values passed through `::add-mask::`. Mask values you fetch yourself.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need central, versioned config per environment
- Budget is tight and rotation is not required
- ECS/Lambda/EC2 workloads should read their own config

❌ Avoid when:
- Automatic secret rotation is required
- Values larger than the parameter size limit (use S3 or Secrets Manager)
- Very high-frequency reads (rate limits; cache them)

---

## 📊 Visual Diagram
```
 /orders
   +-- /prod
   |     +-- api_url        (String)
   |     +-- db_host        (String)
   |     +-- db_password    (SecureString --KMS--> encrypted)
   +-- /staging
         +-- ... (separate IAM, cannot be read by the prod role)

 GitHub Actions --OIDC--> CI role --get-parameters-by-path /orders/prod/--> .env
                                                    |
                                  ECS/Lambda/EC2 --own role--> same path at runtime
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Parameter | One key-value item | एक key-value item |
| SecureString | Encrypted parameter type | encrypted parameter प्रकार |
| Path hierarchy | Folder-like names with `/` | `/` वाले folder जैसे नाम |
| With decryption | Flag to return plaintext | plaintext लौटाने वाला flag |
| Tier | Standard or advanced | standard या advanced स्तर |
| add-mask | Workflow command hiding a value in logs | logs में value छिपाने वाला command |

---

## ⚡ 3-Line Summary
English: Parameter Store holds per-environment config and cheap encrypted secrets under path prefixes.
English: CI reads them via OIDC role, masks sensitive values and renders config files.
English: Scope IAM by path, paginate calls, and use Secrets Manager when rotation is needed.
Hindi: Parameter Store path prefixes के नीचे हर environment का config और सस्ते encrypted secrets रखता है।
Hindi: CI OIDC role से इन्हें पढ़ता है, sensitive values mask करता है और config files बनाता है।
Hindi: IAM को path से scope करें, calls paginate करें, और rotation चाहिए तो Secrets Manager लें।

---

## ➡️ Next Topic
**397. S3 Deploy (Static Sites)**: with credentials and config handled, we deploy the React build to S3.
