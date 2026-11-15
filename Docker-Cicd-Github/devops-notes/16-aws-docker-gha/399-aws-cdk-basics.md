# 399. AWS CDK Basics
# हिंदी में: AWS CDK की बुनियाद

---

## 🔵 Simple Definition (English)
**AWS CDK (Cloud Development Kit)** lets you define AWS infrastructure (S3, CloudFront, ECS, Lambda, IAM roles) in a real programming language such as TypeScript or Python. When you run `cdk deploy`, CDK **synthesizes** your code into a **CloudFormation** template and deploys it as a stack. It is Infrastructure as Code with loops, functions and types.

## 🔵 सरल परिभाषा (Hindi)
**AWS CDK (Cloud Development Kit)** आपको AWS infrastructure (S3, CloudFront, ECS, Lambda, IAM roles) असली programming language जैसे TypeScript या Python में define करने देता है। `cdk deploy` चलाने पर CDK आपके code को **CloudFormation** template में **synthesize** करता है और stack की तरह deploy करता है। यह Infrastructure as Code है, पर loops, functions और types के साथ।

---

## 🔴 Problem it Solves
Click-ops in the console is not repeatable: "who created this bucket and with which settings?" Raw CloudFormation YAML is verbose (a Fargate service can be 300+ lines) and has no real abstraction or reuse.

CDK gives high-level constructs (`ApplicationLoadBalancedFargateService` creates VPC wiring, ALB, service, roles, logs in a few lines), type checking in your editor, unit tests for infra, and the same pipeline flow as app code (PR, review, deploy).

## 🔴 यह क्यों बना? (Hindi)
Console में click करके बनाना repeatable नहीं है: "यह bucket किसने किन settings से बनाया?" Raw CloudFormation YAML बहुत लंबा होता है (एक Fargate service 300+ lines) और उसमें असली abstraction या reuse नहीं।

CDK high-level constructs देता है (`ApplicationLoadBalancedFargateService` कुछ lines में VPC wiring, ALB, service, roles, logs बना देता है), editor में type checking, infra के unit tests, और app code जैसा ही pipeline flow (PR, review, deploy)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → npm i -g aws-cdk ; cdk init app --language typescript
Step 2 → Write constructs in lib/*.ts (Stack contains resources)
Step 3 → cdk bootstrap aws://ACCOUNT/REGION   (once per account+region:
         creates the CDKToolkit stack: staging bucket, ECR, deploy roles)
Step 4 → cdk synth     -> cdk.out/ with CloudFormation templates
Step 5 → cdk diff      -> shows what will be created/changed/destroyed
Step 6 → cdk deploy    -> CloudFormation creates/updates the stack
Step 7 → CI runs steps 4-6 on merge; PRs run synth + diff only
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → npm i -g aws-cdk ; cdk init app --language typescript
Step 2 → lib/*.ts में constructs लिखें (Stack में resources होते हैं)
Step 3 → cdk bootstrap aws://ACCOUNT/REGION   (हर account+region में एक बार:
         CDKToolkit stack बनाता है: staging bucket, ECR, deploy roles)
Step 4 → cdk synth     -> cdk.out/ में CloudFormation templates
Step 5 → cdk diff      -> क्या बनेगा/बदलेगा/हटेगा दिखाता है
Step 6 → cdk deploy    -> CloudFormation stack बनाता/update करता है
Step 7 → CI merge पर steps 4-6 चलाता है; PRs पर सिर्फ synth + diff
```

---

## 🟡 Real World Example
A platform team keeps a `StaticSite` construct: private S3 bucket, CloudFront with OAC, HTTPS certificate, and a deploy role for GitHub OIDC. Every product team imports it and writes `new StaticSite(this, 'Web', { domain: 'shop.example.com' })`. Security fixes (for example enforcing TLS 1.2 and access logs) are made once in the construct and roll out to all sites on their next deploy.

## 🟡 Real Example Hindi mein
एक platform टीम के पास `StaticSite` construct है: private S3 bucket, OAC वाला CloudFront, HTTPS certificate और GitHub OIDC के लिए deploy role। हर product टीम उसे import करके लिखती है `new StaticSite(this, 'Web', { domain: 'shop.example.com' })`। Security fixes (जैसे TLS 1.2 और access logs लागू करना) construct में एक बार होते हैं और सभी sites पर अगले deploy में पहुँच जाते हैं।

---

## 💻 Code / Config Example — Basic

A stack that creates a private versioned S3 bucket (TypeScript, CDK v2).

```typescript
// lib/site-stack.ts
import { Stack, StackProps, RemovalPolicy } from 'aws-cdk-lib';   // core classes from the single CDK v2 package
import { Construct } from 'constructs';                           // base class for all constructs
import * as s3 from 'aws-cdk-lib/aws-s3';                          // S3 module

export class SiteStack extends Stack {                             // a stack = one CloudFormation stack
  constructor(scope: Construct, id: string, props?: StackProps) {  // standard construct signature
    super(scope, id, props);                                       // register the stack in the app

    new s3.Bucket(this, 'SiteBucket', {                            // logical id 'SiteBucket'
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,           // never public
      encryption: s3.BucketEncryption.S3_MANAGED,                  // server-side encryption
      enforceSSL: true,                                            // deny non-HTTPS requests
      versioned: true,                                             // keep old versions for rollback
      removalPolicy: RemovalPolicy.RETAIN,                         // do not delete data if stack is destroyed
    });
  }
}
```

```typescript
// bin/app.ts : entry point that CDK runs
import { App } from 'aws-cdk-lib';                                  // root construct
import { SiteStack } from '../lib/site-stack';                      // our stack

const app = new App();                                              // the CDK app
new SiteStack(app, 'SiteStack-prod', {                              // stack name in CloudFormation
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: 'ap-south-1' },   // explicit account/region
});
```

```bash
# typical local commands
npm ci                                  # install dependencies from the lockfile
npx cdk bootstrap                       # once per account+region
npx cdk synth                           # generate CloudFormation (check for errors)
npx cdk diff                            # preview changes
npx cdk deploy --require-approval broadening   # ask only when IAM/security-group permissions get broader
```

## 💻 Code / Config Example — Advanced

Static site (bucket + CloudFront with OAC) and a GitHub OIDC deploy role, as code, plus the CI workflow with a PR diff and a gated deploy. Construct names reflect CDK v2; confirm API names against your installed version (for example `S3BucketOrigin.withOriginAccessControl` exists in recent releases).

```typescript
// lib/static-site-stack.ts
import { Stack, StackProps, CfnOutput, RemovalPolicy, Duration } from 'aws-cdk-lib';   // core
import { Construct } from 'constructs';                                                  // base
import * as s3 from 'aws-cdk-lib/aws-s3';                                                // buckets
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';                                // CDN
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';                           // origins
import * as iam from 'aws-cdk-lib/aws-iam';                                              // IAM

export class StaticSiteStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);                                         // init stack

    const bucket = new s3.Bucket(this, 'Bucket', {                   // private site bucket
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,             // no public access
      enforceSSL: true,                                              // HTTPS only
      encryption: s3.BucketEncryption.S3_MANAGED,                    // encrypt at rest
      removalPolicy: RemovalPolicy.RETAIN,                           // keep on stack delete
    });

    const dist = new cloudfront.Distribution(this, 'Dist', {         // CloudFront distribution
      defaultRootObject: 'index.html',                               // serve index for '/'
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessControl(bucket),   // OAC: only CloudFront can read
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,   // force HTTPS
        compress: true,                                              // gzip/brotli
      },
      errorResponses: [                                              // SPA fallback
        { httpStatus: 403, responseHttpStatus: 200, responsePagePath: '/index.html', ttl: Duration.seconds(0) },
        { httpStatus: 404, responseHttpStatus: 200, responsePagePath: '/index.html', ttl: Duration.seconds(0) },
      ],
    });

    const provider = iam.OpenIdConnectProvider.fromOpenIdConnectProviderArn(   // reuse existing OIDC provider
      this, 'GhProvider',
      `arn:aws:iam::${this.account}:oidc-provider/token.actions.githubusercontent.com`,
    );

    const role = new iam.Role(this, 'GhDeployRole', {                // role assumed by GitHub Actions
      assumedBy: new iam.WebIdentityPrincipal(provider.openIdConnectProviderArn, {
        StringEquals: {
          'token.actions.githubusercontent.com:aud': 'sts.amazonaws.com',               // audience
          'token.actions.githubusercontent.com:sub': 'repo:myorg/shop-web:environment:production',   // exact repo + environment
        },
      }),
      maxSessionDuration: Duration.hours(1),                         // short sessions
    });
    bucket.grantReadWrite(role);                                     // least-privilege grants generated for you
    role.addToPolicy(new iam.PolicyStatement({                       // allow invalidation of this distribution only
      actions: ['cloudfront:CreateInvalidation'],
      resources: [`arn:aws:cloudfront::${this.account}:distribution/${dist.distributionId}`],
    }));

    new CfnOutput(this, 'BucketName', { value: bucket.bucketName });          // used by deploy workflow
    new CfnOutput(this, 'DistributionId', { value: dist.distributionId });    // used for invalidation
    new CfnOutput(this, 'DeployRoleArn', { value: role.roleArn });            // paste into GitHub variable
  }
}
```

```yaml
name: infra-cdk                                  # workflow name
on:
  pull_request:
    paths: ['infra/**']                          # only when infra changes
  push:
    branches: [main]
    paths: ['infra/**']
permissions:
  id-token: write                                # OIDC
  contents: read                                 # checkout
  pull-requests: write                           # allow commenting the diff (optional)
defaults:
  run:
    working-directory: infra                     # CDK app folder
jobs:
  diff:
    if: github.event_name == 'pull_request'      # PR: preview only
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm, cache-dependency-path: infra/package-lock.json }
      - run: npm ci
      - run: npm test                            # CDK assertion tests (jest)
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.CDK_DIFF_ROLE_ARN }}   # read-only role
          aws-region: ap-south-1
      - run: npx cdk diff --fail                 # print changes; --fail exits non-zero if there are differences (use with care)
  deploy:
    if: github.event_name == 'push'              # main: deploy
    runs-on: ubuntu-latest
    environment: production                      # manual approval
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm, cache-dependency-path: infra/package-lock.json }
      - run: npm ci
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.CDK_DEPLOY_ROLE_ARN }}
          aws-region: ap-south-1
      - run: npx cdk deploy --all --require-approval never   # approval happens in the GitHub environment instead
```

Not run against a real account. `cdk diff --fail` makes PR checks red whenever the infra changes; remove `--fail` if you only want the printout.

---

## 🟠 My Stack Integration
- **React**: the static-site stack above replaces manual bucket/CloudFront setup; the workflow in topics 397/398 uses its outputs.
- **Node.js / FastAPI**: `ecs_patterns.ApplicationLoadBalancedFargateService` for the API, with secrets from `ecs.Secret.fromSecretsManager(...)`.
- **Nginx**: ALB replaces it on AWS; if you keep Nginx, run it as a sidecar container defined in the same task.
- **VPS**: start by codifying only new resources (bucket, ECR, roles); import existing ones later with `cdk import`.
- **Language choice**: TypeScript for a Node team (same language as app), Python CDK if your team is FastAPI-heavy.
- **Testing**: `Template.fromStack(stack).hasResourceProperties(...)` assertions in jest catch accidental public buckets.

```typescript
// test/site.test.ts : fail the build if the bucket ever becomes public
import { App } from 'aws-cdk-lib';                                   // CDK app
import { Template } from 'aws-cdk-lib/assertions';                   // assertion helper
import { StaticSiteStack } from '../lib/static-site-stack';          // stack under test

test('bucket blocks public access', () => {                          // jest test case
  const stack = new StaticSiteStack(new App(), 'T', { env: { account: '111122223333', region: 'ap-south-1' } });
  Template.fromStack(stack).hasResourceProperties('AWS::S3::Bucket', {
    PublicAccessBlockConfiguration: { BlockPublicAcls: true, RestrictPublicBuckets: true },   // must stay enabled
  });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Skipping `cdk bootstrap`; deploy fails with "SSM parameter /cdk-bootstrap/hnb659fds/version not found".
✅ Correct: Bootstrap each account+region once.

❌ Mistake 2: Hard-coding resource names (`bucketName: 'my-site'`); replacement of the resource then fails because names must be unique.
✅ Correct: Let CDK generate names, output them, or use `Names.uniqueId`.

❌ Mistake 3: Stateful resources (DB, bucket) with the default `DESTROY`-like behaviour in prod.
✅ Correct: `RemovalPolicy.RETAIN` / `SNAPSHOT` and termination protection on the stack.

❌ Mistake 4: Deploying from a laptop with admin keys.
✅ Correct: CI with OIDC role and `cdk diff` review in PRs.

❌ Mistake 5: Using `--require-approval never` locally with no reviewer anywhere.
✅ Correct: Review `diff` in PR plus environment approval in CI.

---

## 🧠 Tricky Interview Question
You renamed a construct id from `'Bucket'` to `'SiteBucket'` in code and `cdk diff` shows "destroy old bucket, create new bucket". Why is this dangerous and what do you do?

Answer: The logical ID of a CloudFormation resource is derived from the construct path; changing the id changes the logical ID, so CloudFormation sees a new resource and replaces the old (data loss if DeletionPolicy is Delete). Never rename ids of stateful resources casually. Fix by reverting the id or using `bucket.node.defaultChild.overrideLogicalId('OldLogicalId')`, and keep `RemovalPolicy.RETAIN`.

---

## ⚫ Interview Questions + Answers

Q1: What are L1, L2, L3 constructs?
A1: L1 (`CfnBucket`) maps 1:1 to CloudFormation. L2 (`s3.Bucket`) adds sensible defaults and helper methods (`grantRead`). L3 (patterns, e.g. `ApplicationLoadBalancedFargateService`) wires many resources for a use case.

Q2: CDK vs Terraform?
A2: CDK uses general languages and compiles to CloudFormation (AWS only, state handled by CloudFormation). Terraform uses HCL, multi-cloud, own state file/backend (topic 400). Choose based on team skills and multi-cloud needs.

Q3: What does `cdk synth` output?
A3: CloudFormation templates and assets in `cdk.out/`. It runs your code, so any language error appears here; it makes no AWS changes.

Q4: What is bootstrapping?
A4: Creating the helper resources CDK needs (S3 staging bucket, ECR repository, IAM roles for deployment) in each target account/region.

Q5: How do you manage multiple environments?
A5: One stack class instantiated per environment with props (`new Stack(app, 'Api-prod', {env: prodEnv})`), different accounts, and context values or config files.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- AWS-only infra and the team prefers TypeScript/Python
- You want reusable patterns and unit-tested infra
- Many similar environments or services

❌ Avoid when:
- Multi-cloud or non-AWS providers (use Terraform)
- Tiny one-off resource (CLI is faster)
- Team with no software-engineering habits for IaC review

---

## 📊 Visual Diagram
```
 bin/app.ts + lib/*.ts   (TypeScript constructs)
        |  cdk synth
        v
 cdk.out/*.template.json  (CloudFormation)
        |  cdk deploy  (CI with OIDC role)
        v
 +--------------------- CloudFormation stack ---------------------+
 |  S3 bucket   CloudFront (OAC)   IAM role (GitHub OIDC)         |
 +----------------------------------------------------------------+
        ^
 cdk bootstrap (once): staging bucket, ECR, deploy roles
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Construct | Building block of CDK | CDK का building block |
| Stack | Unit deployed as CloudFormation stack | CloudFormation stack की इकाई |
| Synthesize | Turn code into templates | code को templates में बदलना |
| Bootstrap | One-time setup for CDK in an account | account में CDK का एक-बार setup |
| Logical ID | Resource identity in a template | template में resource की पहचान |
| Removal policy | What happens to a resource on delete | delete पर resource का क्या हो |

---

## ⚡ 3-Line Summary
English: CDK defines AWS infrastructure in TypeScript/Python and deploys through CloudFormation.
English: Use bootstrap once, diff in PRs, and deploy from CI with an OIDC role.
English: Protect stateful resources with RETAIN and never rename their construct ids casually.
Hindi: CDK AWS infrastructure को TypeScript/Python में define करके CloudFormation से deploy करता है।
Hindi: Bootstrap एक बार, PR में diff, और CI से OIDC role के साथ deploy करें।
Hindi: Stateful resources को RETAIN से सुरक्षित रखें और उनके construct ids बिना सोचे न बदलें।

---

## ➡️ Next Topic
**400. Terraform + GitHub Actions**: the multi-cloud alternative to CDK, with its own state file and plan/apply workflow.
