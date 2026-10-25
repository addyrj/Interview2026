# 266. Serverless Framework
# हिंदी में: Serverless Framework — Lambda Deployment के लिए IaC Tool

---

## 🔵 Simple Definition (English)
The **Serverless Framework** is an open-source Infrastructure-as-Code (IaC) tool that lets you define Lambda functions, their triggers, and cloud resources in one YAML file (`serverless.yml`) and deploy everything with a single command (`serverless deploy`) — instead of manually clicking through the AWS console to wire up Lambda + API Gateway + IAM roles + S3 buckets.

## 🔵 सरल परिभाषा (Hindi)
**Serverless Framework** एक open-source Infrastructure-as-Code (IaC) tool है जिसमें tum Lambda functions, unke triggers, aur cloud resources ek hi YAML file (`serverless.yml`) mein define karte ho aur poora setup ek command (`serverless deploy`) se deploy ho jata hai — AWS console mein manually click-click karke Lambda + API Gateway + IAM roles + S3 buckets wire up karne ki zaroorat nahi.

---

## 🔴 Problem it Solves
```
MANUAL AWS CONSOLE DEPLOYMENT PROBLEMS:
  - Creating a Lambda function via console: click, upload zip, set runtime
  - Creating API Gateway route pointing to it: click, click, click
  - Creating IAM role with correct permissions: click, attach policies
  - Creating DynamoDB table for it to use: click, configure
  - Repeat ALL of this for staging, then AGAIN for production
  - No version control — if someone misclicks, no easy rollback
  - New teammate onboarding: "go click these 20 things in AWS console"

SERVERLESS FRAMEWORK SOLUTION:
  - One serverless.yml file describes: functions, triggers, resources, IAM
  - `serverless deploy` creates/updates EVERYTHING via CloudFormation
  - File is version-controlled in git — review changes via PR like any code
  - Same file deploys to dev/staging/prod by changing one --stage flag
  - Rollback: `serverless rollback --timestamp <ts>` undoes a bad deploy
  - New teammate: `git clone` + `serverless deploy` — done in minutes
```

## 🔴 यह क्यों बना? (Hindi)
AWS console mein manually Lambda function banana, API Gateway route jodna, IAM role banana, DynamoDB table create karna — ye sab click-click karke karna padta tha, aur staging + production dono ke liye alag se repeat karna padta tha। Koi version control nahi tha — galti se kisi ne kuch click kar diya to rollback aasan nahi। Serverless Framework ek `serverless.yml` file mein poora setup (functions, triggers, resources, IAM) describe karta hai, aur `serverless deploy` command se CloudFormation ke zariye sab kuch create/update ho jata hai। Ye file git mein version-controlled rehti hai — PR se review ho sakti hai, same file se `--stage` flag change karke dev/staging/prod deploy ho jata hai, aur bad deploy ko `serverless rollback` se undo kiya ja sakta hai।

---

## 🟢 How it Works — Step by Step

Step 1 → Install the CLI globally: `npm install -g serverless` (or use `npx serverless`).
Step 2 → Write a `serverless.yml` describing your `provider` (AWS, region, runtime), `functions` (handler paths + triggers), and optional `resources` (DynamoDB tables, S3 buckets via raw CloudFormation).
Step 3 → Run `serverless deploy` — the framework packages your code, converts your YAML into a CloudFormation template, and submits it to AWS.
Step 4 → AWS CloudFormation creates/updates the actual resources: Lambda functions, API Gateway routes, IAM roles, event source mappings — all tracked as one "stack."
Step 5 → Test locally first with the `serverless-offline` plugin, which emulates API Gateway + Lambda on your machine without deploying.
Step 6 → To update, just change `serverless.yml` or your code and run `serverless deploy` again — CloudFormation calculates the diff and applies only changes.
Step 7 → To tear everything down cleanly, run `serverless remove` — deletes the entire stack (no orphaned resources left behind).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → CLI globally install karo: `npm install -g serverless` (ya `npx serverless` use karo)।
Step 2 → Ek `serverless.yml` likho jisme `provider` (AWS, region, runtime), `functions` (handler paths + triggers), aur optional `resources` (DynamoDB tables, S3 buckets raw CloudFormation ke zariye) ho।
Step 3 → `serverless deploy` chalao — framework code package karta hai, YAML ko CloudFormation template mein convert karta hai, aur AWS ko submit karta hai।
Step 4 → AWS CloudFormation actual resources create/update karta hai: Lambda functions, API Gateway routes, IAM roles, event source mappings — sab ek "stack" ke roop mein track hote hain।
Step 5 → `serverless-offline` plugin se pehle local testing karo, jo API Gateway + Lambda ko local machine par emulate karta hai, bina actual deploy ke।
Step 6 → Update karne ke liye sirf `serverless.yml` ya code change karo aur `serverless deploy` phir se chalao — CloudFormation diff calculate karke sirf changes apply karta hai।
Step 7 → Poora setup clean tear down karne ke liye `serverless remove` chalao — pura stack delete ho jata hai, koi orphaned resource nahi bachta।

---

## 🟡 Real World Example
**Flipkart's internal notification service:** A team manages 15 Lambda functions (order updates, cart reminders, delivery alerts) across dev/staging/prod using one `serverless.yml` with stage-specific variables. CI/CD runs `serverless deploy --stage prod` on merge to main. **Amazon-style seller onboarding pipeline:** When a seller uploads KYC documents to S3, a chain of Lambda functions (defined in one serverless.yml, triggered by S3 events) validates, OCRs, and stores results in DynamoDB — the whole pipeline's infrastructure lives in one reviewable YAML file instead of being scattered across manual console configs.

## 🟡 Real Example Hindi mein
**Flipkart ka internal notification service:** Ek team 15 Lambda functions (order updates, cart reminders, delivery alerts) manage karti hai dev/staging/prod mein ek hi `serverless.yml` se, stage-specific variables ke saath। CI/CD main branch par merge hone par `serverless deploy --stage prod` run karta hai। **Amazon-style seller onboarding pipeline:** Jab seller KYC documents S3 par upload karta hai, ek chain of Lambda functions (ek serverless.yml mein defined, S3 events se triggered) validate, OCR, aur DynamoDB mein results store karti hai — poora pipeline ka infrastructure ek reviewable YAML file mein rehta hai, manual console configs mein scattered nahi।

---

## 💻 Code Example — Basic

```yaml
# serverless.yml — minimal example: one HTTP Lambda function
# Run `serverless deploy` in the same directory to deploy this.

service: order-api # name of this serverless "service" (becomes part of resource names)

provider:
  name: aws # cloud provider
  runtime: nodejs20.x # Node.js version Lambda will run
  region: ap-south-1 # Mumbai region — closer to Indian users
  stage: ${opt:stage, 'dev'} # deployment stage; defaults to 'dev' if not passed via --stage
  environment: # env vars available to ALL functions via process.env
    ORDERS_TABLE: orders-${self:provider.stage} # e.g. "orders-dev" or "orders-prod"

functions:
  getOrder: # logical name of this function
    handler: handlers/order.get # path to exported function: handlers/order.js -> exports.get
    events: # what triggers this function
      - httpApi: # API Gateway HTTP API trigger
          path: /orders/{orderId} # route path
          method: get # HTTP method

  createOrder:
    handler: handlers/order.create # another handler in the same file
    events:
      - httpApi:
          path: /orders
          method: post
```

```javascript
// handlers/order.js — the actual Lambda handler code referenced above

// exports.get -> mapped to "getOrder" function in serverless.yml
exports.get = async (event) => {
  const { orderId } = event.pathParameters; // extracted from the URL path

  // ... normally you'd fetch from DynamoDB here using process.env.ORDERS_TABLE
  return {
    statusCode: 200,
    body: JSON.stringify({ orderId, status: 'confirmed' }),
  };
};

// exports.create -> mapped to "createOrder" function in serverless.yml
exports.create = async (event) => {
  const body = JSON.parse(event.body); // API Gateway sends body as a string

  // ... normally you'd write to DynamoDB here
  return {
    statusCode: 201,
    body: JSON.stringify({ orderId: 'ord_' + Date.now(), ...body }),
  };
};
```

## 💻 Code Example — Advanced

```yaml
# serverless.yml — production-style: multiple triggers, IAM permissions,
# a DynamoDB resource defined inline, and plugins for local testing.

service: payment-service

frameworkVersion: '3' # pin the Serverless Framework version for stability

plugins:
  - serverless-offline # enables local emulation: `serverless offline`

provider:
  name: aws
  runtime: nodejs20.x
  region: ap-south-1
  stage: ${opt:stage, 'dev'}
  memorySize: 256 # default memory for all functions (MB)
  timeout: 10 # default timeout for all functions (seconds)
  environment:
    PAYMENTS_TABLE: ${self:custom.tableName} # reference a custom variable below
  iam:
    role:
      statements: # least-privilege IAM permissions, scoped to just what's needed
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
            - dynamodb:UpdateItem
          Resource:
            - !GetAtt PaymentsTable.Arn # reference the table resource defined below

custom:
  tableName: payments-${self:provider.stage} # reusable variable: e.g. payments-prod

functions:
  webhookHandler:
    handler: handlers/webhook.handle
    events:
      - httpApi:
          path: /webhooks/razorpay
          method: post
    environment:
      WEBHOOK_SECRET: ${env:RAZORPAY_WEBHOOK_SECRET} # pulled from CI/CD secret, not hardcoded

  processQueue:
    handler: handlers/queue.process
    events:
      - sqs: # SQS trigger — Lambda polls the queue automatically
          arn: !GetAtt PaymentQueue.Arn
          batchSize: 10 # process up to 10 messages per invocation

  nightlyReport:
    handler: handlers/report.generate
    events:
      - schedule: cron(0 2 * * ? *) # runs every day at 2 AM UTC

resources: # raw CloudFormation for resources this service owns
  Resources:
    PaymentsTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:custom.tableName}
        BillingMode: PAY_PER_REQUEST # on-demand pricing, no capacity planning
        AttributeDefinitions:
          - AttributeName: paymentId
            AttributeType: S
        KeySchema:
          - AttributeName: paymentId
            KeyType: HASH

    PaymentQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: payment-processing-${self:provider.stage}
        VisibilityTimeout: 60 # seconds a message is hidden after being picked up
```

```bash
# Deployment workflow commands

# Install dependencies and the framework
npm install --save-dev serverless serverless-offline

# Test locally WITHOUT deploying to AWS — emulates API Gateway + Lambda
serverless offline

# Deploy to the "dev" stage (default)
serverless deploy --stage dev

# Deploy to production — separate stack, separate resources entirely
serverless deploy --stage prod

# Deploy just ONE function quickly (faster than full stack deploy)
serverless deploy function --function webhookHandler --stage dev

# View recent deploys for rollback reference
serverless deploy list --stage prod

# Roll back to a previous deployment
serverless rollback --timestamp 1700000000000 --stage prod

# Tear down the entire stack (deletes Lambda, API Gateway, DynamoDB, SQS - all of it)
serverless remove --stage dev
```

---

## 🟠 Express.js Integration

```javascript
// handlers/app.js — wrapping an EXISTING Express app for Serverless Framework
// deployment, so the whole app (not just individual functions) runs on Lambda.

const express = require('express');
const serverlessHttp = require('serverless-http'); // npm install serverless-http

const app = express();
app.use(express.json());

// All your existing Express routes, completely unchanged
app.get('/orders/:orderId', (req, res) => {
  res.json({ orderId: req.params.orderId, status: 'confirmed' });
});

app.post('/orders', (req, res) => {
  res.status(201).json({ orderId: 'ord_' + Date.now(), ...req.body });
});

// Export the wrapped handler for Lambda to call
module.exports.handler = serverlessHttp(app);
```

```yaml
# serverless.yml — route ALL paths to the single Express app handler
# This is the "monolith on Lambda" pattern: one function serves the whole app
# instead of splitting every Express route into a separate Lambda function.

service: express-on-lambda

provider:
  name: aws
  runtime: nodejs20.x
  region: ap-south-1

functions:
  api:
    handler: handlers/app.handler # points to the serverless-http wrapped app
    events:
      - httpApi:
          path: /{proxy+} # catch-all: forward EVERY path to Express's own router
          method: ANY # forward EVERY HTTP method; Express decides what to do with it
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Hardcoding secrets directly in serverless.yml
```yaml
# WRONG: secret committed to git in plain text
environment:
  WEBHOOK_SECRET: "sk_live_abc123xyz"

# CORRECT: pull from environment variable set by CI/CD secrets manager
environment:
  WEBHOOK_SECRET: ${env:RAZORPAY_WEBHOOK_SECRET}
```

❌ **Mistake 2:** Giving every function full admin IAM permissions
```yaml
# WRONG: overly broad — a bug in one function could delete unrelated resources
iam:
  role:
    statements:
      - Effect: Allow
        Action: "*"
        Resource: "*"

# CORRECT: least privilege — only the specific actions/resources needed
iam:
  role:
    statements:
      - Effect: Allow
        Action:
          - dynamodb:GetItem
          - dynamodb:PutItem
        Resource: !GetAtt PaymentsTable.Arn
```

❌ **Mistake 3:** Not separating stages, causing dev deploys to overwrite prod
```yaml
# WRONG: no stage variable — table/function names collide across environments
functions:
  getOrder:
    handler: handlers/order.get
# resources reference a fixed name like "orders" with no stage suffix

# CORRECT: always parameterize with stage
provider:
  stage: ${opt:stage, 'dev'}
custom:
  tableName: orders-${self:provider.stage} # orders-dev vs orders-prod, fully isolated
```

---

## 🧠 Tricky Interview Question

**Q: You run `serverless deploy` twice in a row with no code changes — does it re-create all the AWS resources both times?**

```bash
serverless deploy --stage prod   # first deploy
serverless deploy --stage prod   # run again immediately, same code
```

**Answer:** No. Serverless Framework compiles `serverless.yml` into an AWS **CloudFormation** template and submits it as a "stack" update. CloudFormation compares the new template against the existing stack's current state and computes a **diff** — if nothing changed, it reports "no changes to deploy" (or performs a no-op update) rather than tearing down and recreating resources. This is what makes repeated deploys safe: CloudFormation only creates/modifies/deletes the specific resources that actually differ between template versions, not the entire stack. This also means a bad deploy can be mitigated with `serverless rollback`, since CloudFormation keeps a history of stack versions.

---

## ⚫ Interview Questions + Answers

**Q1: What problem does the Serverless Framework solve that raw AWS Lambda console deployment doesn't?**
A1: It turns infrastructure into version-controlled code (`serverless.yml`) instead of manual console clicks. This enables code review via git PRs, repeatable deployments across stages (dev/staging/prod) with one command, easy rollback, and onboarding a new teammate in minutes (`git clone` + `serverless deploy`) instead of them manually recreating dozens of console settings.

**Q2: How does `serverless deploy` actually work under the hood?**
A2: The CLI packages your function code into zip files, uploads them to an S3 bucket it manages, converts your `serverless.yml` into an AWS CloudFormation template (defining Lambda functions, IAM roles, API Gateway routes, event source mappings, and any custom `resources`), and submits that template to CloudFormation. CloudFormation then creates or updates the actual AWS resources as a single tracked "stack," computing a diff against the previous version so only changed resources are touched.

**Q3: What is `serverless-offline` and why is it useful?**
A3: It's a plugin that emulates API Gateway and Lambda locally, letting you run `serverless offline` and hit your routes (e.g. `http://localhost:3000/orders/123`) exactly as they'd behave in AWS — without deploying anything or incurring any cloud cost. This massively speeds up the development loop since you don't need to redeploy to test every change; it's the serverless equivalent of running `node server.js` locally.

**Q4: How does Serverless Framework compare to AWS SAM and AWS CDK?**
A4: All three are IaC tools for deploying serverless resources, differing mainly in authoring style and vendor lock-in. **Serverless Framework**: YAML-based, multi-cloud capable (AWS/Azure/GCP with plugins), large plugin ecosystem, easiest learning curve. **AWS SAM**: YAML-based but AWS-native only, tightly integrated with AWS CLI/console, good if you're all-in on AWS tooling. **AWS CDK**: define infrastructure in actual programming languages (TypeScript/Python/etc.) that compile down to CloudFormation — most powerful/flexible for complex logic-driven infra, but steeper learning curve. Teams often choose Serverless Framework for simplicity and quick iteration, CDK for large complex infra needing real programming constructs (loops, conditionals, reusable constructs).

**Q5: How do you manage different environments (dev, staging, prod) in one serverless.yml?**
A5: Use the `stage` variable (`${opt:stage, 'dev'}`) throughout the config to parameterize resource names, environment variables, and settings — e.g. `orders-${self:provider.stage}` becomes `orders-dev` or `orders-prod`. Each `serverless deploy --stage <name>` creates a completely separate CloudFormation stack with its own isolated resources, so dev and prod never collide or interfere with each other, even though they're defined by the same file.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You're deploying Lambda-based serverless architectures and want reviewable, repeatable IaC
- You need multiple environments (dev/staging/prod) from one config
- You want local testing before deploying (via serverless-offline)
- Your team wants a simpler YAML-based alternative to writing CDK code

❌ Avoid when:
- Your infrastructure is extremely complex with heavy conditional/programmatic logic (CDK fits better)
- You're deploying only to EC2/containers with no Lambda functions involved (use Terraform/CDK/plain CloudFormation instead)
- You're already deeply invested in AWS SAM tooling and don't need multi-cloud flexibility

---

## 📊 Visual Diagram
```
SERVERLESS FRAMEWORK DEPLOYMENT FLOW:
──────────────────────────────────────────────────────────────────

  serverless.yml  ──┐
  (functions,       │
   events,          │   serverless deploy
   resources)       │
                     ▼
            ┌─────────────────┐
            │ Serverless CLI   │
            │ - zips code      │
            │ - uploads to S3  │
            │ - builds         │
            │   CloudFormation │
            │   template       │
            └────────┬─────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │ AWS CloudFormation   │
            │ (diffs + applies)    │
            └────────┬─────────────┘
                      │
         ┌────────────┼─────────────┬───────────────┐
         ▼            ▼             ▼               ▼
      Lambda      API Gateway    IAM Roles      DynamoDB/SQS
     Functions      Routes      (permissions)   (custom resources)

STAGES: dev / staging / prod = separate stacks, same template, different names
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| IaC | Infrastructure-as-Code — infra defined in files | Infra ko file mein define karna |
| serverless.yml | Main config file for the framework | Framework ki main config file |
| Stage | Deployment environment (dev/staging/prod) | Deployment environment |
| CloudFormation | AWS's underlying provisioning engine | AWS ka resource banane wala engine |
| serverless-offline | Plugin for local API Gateway + Lambda emulation | Local testing ke liye plugin |
| Stack | Group of resources deployed together | Ek saath deploy hue resources ka group |
| Event Source Mapping | Link between trigger (SQS/S3) and Lambda | Trigger aur Lambda ke beech ka link |
| Rollback | Reverting to a previous deployment | Pehle wale deployment par wapas jaana |

---

## ⚡ 3-Line Summary
**English:**
1. Serverless Framework lets you define Lambda functions, triggers, and AWS resources in one `serverless.yml`, deployed with `serverless deploy`.
2. It compiles your YAML into a CloudFormation stack, so deploys are diffed, repeatable, version-controlled, and rollback-able.
3. Test locally with `serverless-offline` before deploying; parameterize with `stage` to safely run dev/staging/prod from the same config.

**Hindi:**
1. Serverless Framework Lambda functions, triggers, aur AWS resources ko ek `serverless.yml` mein define karne deta hai, `serverless deploy` se deploy hota hai।
2. Ye YAML ko CloudFormation stack mein compile karta hai, isliye deploys diffed, repeatable, version-controlled, aur rollback-able hote hain।
3. Deploy se pehle `serverless-offline` se local test karo; `stage` variable se dev/staging/prod ko same config se safely chalao।

---

## ➡️ Next Topic
**267. Deploy on Railway / Render** — Modern PaaS platforms jahan git push karne se hi deployment ho jaata hai, Lambda/AWS ke manual setup ke bina।
