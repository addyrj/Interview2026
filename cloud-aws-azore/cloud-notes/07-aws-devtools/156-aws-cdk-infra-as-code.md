# 156. AWS CDK - Infra as Code
# AWS: AWS Cloud Development Kit (CDK v2)
# Azure: Bicep / Pulumi / Terraform CDK (closest: Bicep)
# हिंदी में: CDK - असली प्रोग्रामिंग भाषा (TypeScript/Python) में इंफ्रास्ट्रक्चर लिखना

---

## 🔵 Simple Definition
CDK lets you define AWS infrastructure in TypeScript, Python, etc. and synthesizes it to CloudFormation templates, which it then deploys.
हिंदी: YAML की जगह कोड (loops, functions) से इंफ्रा लिखें; पीछे CloudFormation बनकर चलता है।

## 🔴 Why it Exists
YAML gets repetitive. Code gives reuse (constructs), types and loops, with CloudFormation's rollback safety.

## 🟢 How it Works
```
app.ts (Stack + Constructs) --cdk synth--> cdk.out/*.template.json
                            --cdk diff / cdk deploy--> CloudFormation stack
(one-time) cdk bootstrap: creates CDKToolkit stack (S3 assets bucket, roles)
```

## 💻 Code / Config Example
```typescript
// lib/api-stack.ts (aws-cdk-lib v2) - S3 bucket + Lambda
import { Stack, StackProps, RemovalPolicy, Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';

export class ApiStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);
    const bucket = new s3.Bucket(this, 'Uploads', {
      versioned: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: RemovalPolicy.RETAIN,
    });
    const fn = new lambda.Function(this, 'Handler', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda'),
      timeout: Duration.seconds(10),
      environment: { BUCKET: bucket.bucketName },
    });
    bucket.grantReadWrite(fn); // generates least-privilege IAM
  }
}
```
```bash
npm i -g aws-cdk && cdk init app --language typescript
cdk bootstrap && cdk diff && cdk deploy
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Tool | CDK | Bicep (DSL) or Pulumi |
| Output | CloudFormation | ARM |
| Language | TS, Python, Java, C#, Go | Bicep DSL |
| Pricing | Free tool | Free tool |

## ⚠️ Common Mistakes
❌ Forgetting `cdk bootstrap`. ✅ Run once per account/region.
❌ Hardcoding names so replacement fails. ✅ Let CDK generate names.

## ⚫ Interview Q&A
Q1 [Easy]: What does cdk synth do? A1: Generates the CloudFormation template.
Q2 [Medium]: L1 vs L2 vs L3 constructs? A2: L1 = raw CFN (CfnBucket), L2 = curated defaults, L3 = patterns.
Q3 [Hard]: CDK vs Terraform? A3: CDK ties to CloudFormation (state managed by AWS); Terraform is multi-cloud with its own state.

## ✅ Quick Checklist
□ Bootstrapped
□ cdk diff in CI before deploy
□ RemovalPolicy set for stateful resources

## ⚡ 1-Line Summary
CDK = infrastructure as real code over CloudFormation | CDK कोड लिखकर CloudFormation के जरिए इंफ्रा बनाता है।

## ➡️ Next: CloudFormation Basics
