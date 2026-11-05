# 392. Serverless Framework + GitHub Actions
# हिंदी में: Serverless Framework + GitHub Actions

---

## 🔵 Simple Definition (English)
**Serverless Framework** lets you describe Lambda functions, API Gateway routes, queues and tables in one **`serverless.yml`** file and deploy everything with `serverless deploy`. Under the hood it generates a **CloudFormation** stack. With GitHub Actions you run that command per branch/stage (`dev`, `staging`, `prod`).

## 🔵 सरल परिभाषा (Hindi)
**Serverless Framework** Lambda functions, API Gateway routes, queues और tables को एक **`serverless.yml`** file में describe करने देता है और `serverless deploy` से सब कुछ deploy करता है। अंदर से यह **CloudFormation** stack बनाता है। GitHub Actions में यह command हर branch/stage (`dev`, `staging`, `prod`) के लिए चलाई जाती है।

---

## 🔴 Problem it Solves
Deploying with raw `aws lambda` commands means one script per function, hand-made API Gateway routes, IAM roles by clicking, and no way to recreate the environment. Dev and prod drift apart.

Serverless Framework = infrastructure + code in git, one command, per-stage isolation (`orders-dev-api`, `orders-prod-api`), plugin ecosystem (offline testing, esbuild bundling).

## 🔴 यह क्यों बना? (Hindi)
सीधे `aws lambda` commands से deploy करने में हर function की अलग script, API Gateway routes हाथ से, IAM roles click करके बनाने पड़ते हैं, और environment दोबारा बनाना मुश्किल। Dev और prod अलग-अलग हो जाते हैं।

Serverless Framework = infrastructure + code git में, एक command, हर stage अलग (`orders-dev-api`, `orders-prod-api`), और plugins (offline testing, esbuild bundling)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write serverless.yml (service, provider, functions, events, resources)
Step 2 → CI: npm ci, tests
Step 3 → CI authenticates to AWS (OIDC) and to Serverless (license/access key, v4)
Step 4 → "serverless deploy --stage prod" packages every function
Step 5 → Framework uploads zips + generated CloudFormation template to an S3 bucket
Step 6 → CloudFormation creates/updates: Lambda, API GW, IAM roles, log groups
Step 7 → Outputs the API URL; failure -> CloudFormation auto-rolls back the stack
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप serverless.yml लिखते हैं (service, provider, functions, events, resources)
Step 2 → CI: npm ci, tests
Step 3 → CI AWS (OIDC) और Serverless (license/access key, v4) में authenticate होता है
Step 4 → "serverless deploy --stage prod" हर function package करता है
Step 5 → Framework zips + generated CloudFormation template को S3 bucket में upload करता है
Step 6 → CloudFormation बनाता/update करता है: Lambda, API GW, IAM roles, log groups
Step 7 → API URL print होता है; failure पर CloudFormation stack खुद rollback करता है
```

---

## 🟡 Real World Example
A logistics startup has a "track shipment" API: 8 Lambda functions behind API Gateway, an SQS queue for webhooks, and a DynamoDB table. One `serverless.yml` defines it all. Pull requests deploy a temporary stage `pr-142` for QA; when the PR closes, a workflow runs `serverless remove --stage pr-142`. Prod deploys only from `main` after manual approval.

## 🟡 Real Example Hindi mein
एक logistics startup की "track shipment" API में 8 Lambda functions API Gateway के पीछे, webhooks के लिए SQS queue, और DynamoDB table है। सब कुछ एक `serverless.yml` में है। हर Pull Request एक temporary stage `pr-142` deploy करता है ताकि QA जाँच सके; PR बंद होने पर workflow `serverless remove --stage pr-142` चलाता है। Prod सिर्फ `main` से manual approval के बाद deploy होता है।

---

## 💻 Code / Config Example — Basic

```yaml
# serverless.yml : minimal service with one HTTP function
service: orders-api                              # service name, part of the stack name
frameworkVersion: '4'                            # pin major version (v4 needs an account/licence key)

provider:
  name: aws                                      # cloud provider
  runtime: nodejs20.x                            # Lambda runtime (check supported list)
  region: ap-south-1                             # deploy region
  stage: ${opt:stage, 'dev'}                     # --stage flag, default dev

functions:
  hello:                                         # logical function name
    handler: handler.hello                       # file.exportedFunction
    events:
      - httpApi:                                 # HTTP API (cheaper than REST API)
          path: /hello                           # URL path
          method: get                            # HTTP method
```

```javascript
// handler.js : matches handler: handler.hello
module.exports.hello = async () => ({            // Lambda entry point
  statusCode: 200,                               // OK
  body: JSON.stringify({ ok: true }),            // JSON body
});
```

## 💻 Code / Config Example — Advanced

Production-style `serverless.yml` plus a workflow that deploys `dev` from PRs/develop and `prod` from main.

```yaml
# serverless.yml : production-style config
service: orders-api                              # service name
frameworkVersion: '4'                            # major version pin

provider:
  name: aws                                      # AWS
  runtime: nodejs20.x                            # runtime
  architecture: arm64                            # Graviton: cheaper and often faster
  region: ap-south-1                             # region
  stage: ${opt:stage, 'dev'}                     # stage from CLI
  memorySize: 256                                # MB, also scales CPU
  timeout: 10                                    # seconds; keep below API Gateway's limit
  logRetentionInDays: 14                         # avoid infinite log cost
  environment:                                   # non-secret config
    STAGE: ${self:provider.stage}                # expose stage to code
    TABLE: ${self:service}-${self:provider.stage}-orders   # table name per stage
    DB_URL: ${ssm:/orders/${self:provider.stage}/db_url}   # read at DEPLOY time from Parameter Store (see security note)
  iam:
    role:
      statements:                                # least-privilege inline policy
        - Effect: Allow
          Action: [dynamodb:GetItem, dynamodb:PutItem, dynamodb:Query]   # only what code needs
          Resource: !GetAtt OrdersTable.Arn      # only this table

functions:
  createOrder:
    handler: src/create.handler                  # entry
    events:
      - httpApi: { path: /orders, method: post } # POST /orders
  getOrder:
    handler: src/get.handler
    events:
      - httpApi: { path: '/orders/{id}', method: get }   # GET /orders/{id}
  worker:
    handler: src/worker.handler
    events:
      - sqs:
          arn: !GetAtt OrdersQueue.Arn          # trigger from queue
          batchSize: 10                          # messages per invocation

resources:
  Resources:                                     # raw CloudFormation
    OrdersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:provider.environment.TABLE}   # per-stage name
        BillingMode: PAY_PER_REQUEST             # no capacity planning
        AttributeDefinitions:
          - { AttributeName: id, AttributeType: S }
        KeySchema:
          - { AttributeName: id, KeyType: HASH }
    OrdersQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:service}-${self:provider.stage}-queue
        VisibilityTimeout: 60                    # >= 6x function timeout recommended
```

```yaml
# .github/workflows/serverless.yml
name: serverless-deploy                          # workflow name

on:
  push:
    branches: [main, develop]                    # main -> prod, develop -> dev

permissions:
  id-token: write                                # OIDC
  contents: read                                 # checkout

jobs:
  deploy:
    runs-on: ubuntu-latest                       # runner
    environment: ${{ github.ref_name == 'main' && 'production' || 'development' }}   # prod needs approval
    env:
      STAGE: ${{ github.ref_name == 'main' && 'prod' || 'dev' }}   # pick stage
      SERVERLESS_ACCESS_KEY: ${{ secrets.SERVERLESS_ACCESS_KEY }}  # Serverless v4 auth (store as secret)
    steps:
      - uses: actions/checkout@v4                # code
      - uses: actions/setup-node@v4              # Node
        with:
          node-version: 20
          cache: npm
      - run: npm ci                              # exact deps
      - run: npm test                            # tests first
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: arn:aws:iam::111122223333:role/gha-serverless-${{ env.STAGE }}
          aws-region: ap-south-1
      - run: npx serverless deploy --stage "$STAGE" --verbose   # package + CloudFormation deploy
      - name: Smoke test                         # check deployed API
        run: |
          URL=$(aws cloudformation describe-stacks --stack-name "orders-api-$STAGE" --query "Stacks[0].Outputs[?OutputKey=='HttpApiUrl'].OutputValue" --output text)
          curl --fail --retry 5 --retry-delay 3 "$URL/hello"
```

Version-dependent: Serverless v4 requires a (free for small orgs) account/licence key; v3 does not but is no longer maintained. Alternatives with the same idea: AWS SAM, SST. Check current licensing before adopting.

---

## 🟠 My Stack Integration
- **Node.js**: native fit; add `serverless-esbuild` to bundle TypeScript and shrink packages.
- **FastAPI**: use a container image function (`image:` in `functions`) or `serverless-python-requirements`; consider Mangum.
- **React**: S3 + CloudFront (topic 397); Serverless can create the bucket in `resources`, but deploy files via CI.
- **Nginx / VPS**: not needed for the Lambda part. Hybrid is common: VPS runs the main API, Lambda handles webhooks and cron jobs.
- **AWS**: stack outputs (API URL) feed the React app env at build time.

```yaml
# per-PR preview stage: add to a separate workflow triggered on pull_request
# deploy:  npx serverless deploy --stage pr-${{ github.event.number }}
# cleanup: npx serverless remove --stage pr-${{ github.event.number }}   (on pull_request: types [closed])
on:
  pull_request:
    types: [opened, synchronize, closed]         # deploy on update, remove on close
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `${ssm:...}` for secrets in `environment`, which writes the plaintext value into the CloudFormation template and the Lambda config.
✅ Correct: Store only the parameter NAME in env and fetch/decrypt at runtime (or use `${ssm(raw):...}` carefully with SecureString and know the exposure).

❌ Mistake 2: Same stage name from two branches or laptops.
✅ Correct: Stage per environment; CI is the only one that deploys `prod`.

❌ Mistake 3: `iam: role` with `Resource: '*'` and `Action: '*'`.
✅ Correct: Narrow statements per function.

❌ Mistake 4: Forgetting `serverless remove` for preview stages, leaving costs and clutter.
✅ Correct: Cleanup workflow on PR close.

❌ Mistake 5: CloudFormation stack stuck in `UPDATE_ROLLBACK_FAILED` after a manual console change.
✅ Correct: Never edit managed resources by hand; fix drift via config and redeploy.

---

## 🧠 Tricky Interview Question
`serverless deploy` shows "No changes to deploy" although you changed an environment variable in the GitHub secret used by `${env:...}`. Why, and how do you deal with it?

Answer: Variables are resolved at deploy time on the runner, but the CLI also compares package hashes; if only an externally resolved value changed and the template hash is the same, it may skip, or the cached package is reused. Use `--force` for a redeploy, and better, avoid baking config in the template: read config at runtime from SSM/Secrets Manager so a change needs no redeploy.

---

## ⚫ Interview Questions + Answers

Q1: What does Serverless Framework generate?
A1: A CloudFormation template (`.serverless/cloudformation-template-update-stack.json`) plus zip artifacts uploaded to a deployment S3 bucket.

Q2: `serverless deploy` vs `serverless deploy function -f name`?
A2: The first updates the whole stack through CloudFormation (safe, slower). The second only uploads one function's code (fast, for dev; it bypasses CloudFormation, so not for prod).

Q3: How do you deal with multiple environments?
A3: `--stage`, stage-specific variables (`${self:custom.x.${self:provider.stage}}`), separate AWS accounts per environment with separate OIDC roles.

Q4: Serverless Framework vs SAM vs CDK?
A4: Serverless: simple YAML, many plugins, multi-cloud history. SAM: AWS official, CloudFormation extension. CDK: real programming language, broader than serverless apps.

Q5: How do you roll back a bad release?
A5: CloudFormation auto-rolls back failed deploys. For a successful but bad release, redeploy the previous git commit (`serverless deploy` is idempotent) or use `serverless rollback --timestamp ...` (uses the S3 artifacts).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many functions/events described together in one repo
- Need per-branch preview environments
- Team prefers YAML config over code

❌ Avoid when:
- Only one or two functions (plain CLI is enough)
- You need heavy non-serverless infra (VPC, RDS, ECS): use CDK/Terraform
- Licensing of v4 is a blocker; consider SAM/SST

---

## 📊 Visual Diagram
```
 serverless.yml + src/
        |
 GitHub Actions: npm ci -> test -> serverless deploy --stage prod
        |
        v
  +-----------------+     upload      +------------------+
  | Deployment S3   | <-------------- | package (zips +  |
  | bucket          |                 | CFN template)    |
  +--------+--------+                 +------------------+
           | CloudFormation stack "orders-api-prod"
           v
  +---------+  +-------------+  +--------+  +----------+
  | Lambda  |  | API Gateway |  |  SQS   |  | DynamoDB |
  +---------+  +-------------+  +--------+  +----------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stage | Environment name (dev/prod) | environment का नाम |
| CloudFormation | AWS infrastructure-as-code engine | AWS का IaC engine |
| Stack | Group of resources managed together | साथ-साथ manage होने वाले resources |
| Plugin | Extension for the framework | framework का extension |
| HTTP API | Cheaper API Gateway type | सस्ता API Gateway प्रकार |
| Drift | Real infra differs from config | असल infra का config से अलग होना |

---

## ⚡ 3-Line Summary
English: Serverless Framework turns one YAML into a CloudFormation stack of functions, APIs and queues.
English: GitHub Actions runs tests and `serverless deploy --stage` with OIDC credentials.
English: Use stages for isolation, least-privilege IAM and runtime secret lookup.
Hindi: Serverless Framework एक YAML को functions, APIs और queues के CloudFormation stack में बदलता है।
Hindi: GitHub Actions tests और OIDC credentials के साथ `serverless deploy --stage` चलाता है।
Hindi: Isolation के लिए stages, least-privilege IAM और runtime पर secret lookup इस्तेमाल करें।

---

## ➡️ Next Topic
**393. AWS IAM for GitHub Actions**: every pipeline above needs a role; next we design the permissions properly with least privilege.
