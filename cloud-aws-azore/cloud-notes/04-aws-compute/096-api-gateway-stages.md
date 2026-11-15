---

# 96. API Gateway Stages
# AWS: API Gateway stages and stage variables
# Azure: APIM revisions/versions + named values (or separate instances)
# हिंदी में: API गेटवे स्टेजेस

---

## 🔵 Simple Definition (2 lines)
A stage is a named, deployed snapshot of your API (dev, staging, prod) with its own URL, settings and variables.
हिंदी: Stage आपकी API का डिप्लॉय किया हुआ नामित संस्करण है (dev, prod), जिसका अपना URL और सेटिंग होती है।

---

## 🔴 Why it Exists (2 lines)
You need to test changes without touching production and roll out safely. Stages separate environments and settings (throttle, logging, variables).

---

## 🟢 How it Works
```
API definition (routes)  --deploy-->  Stage "dev"   https://abc.execute-api.../dev
                                      Stage "prod"  https://abc.execute-api.../prod
Per stage: throttling, access logs, caching (REST), stage variables, canary (REST)
Stage variable example: lambdaAlias=live  -> integration uses fn:${stageVariables.lambdaAlias}
HTTP API: "$default" stage + auto-deploy option
Best practice: separate AWS accounts per environment, stages for versions/canary
```

---

## 💻 Code / Config Example
```yaml
# CloudFormation: HTTP API with two stages and different throttling
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  Api:
    Type: AWS::ApiGatewayV2::Api
    Properties: { Name: demo, ProtocolType: HTTP }
  DevStage:
    Type: AWS::ApiGatewayV2::Stage
    Properties:
      ApiId: !Ref Api
      StageName: dev
      AutoDeploy: true
      StageVariables: { env: dev }
      DefaultRouteSettings: { ThrottlingBurstLimit: 20, ThrottlingRateLimit: 10 }
  ProdStage:
    Type: AWS::ApiGatewayV2::Stage
    Properties:
      ApiId: !Ref Api
      StageName: prod
      AutoDeploy: false
      StageVariables: { env: prod }
      DefaultRouteSettings: { ThrottlingBurstLimit: 500, ThrottlingRateLimit: 200 }
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Environment | Stage | Separate APIM instance / product / revision |
| Variables | Stage variables | Named values |
| Canary | REST API canary settings | Revisions + gradual routing (via Front Door etc.) |
| Pricing | No extra per stage (approximate — check current docs) | Per APIM tier (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Editing REST API and forgetting to redeploy to the stage.
✅ Correct: Create a deployment (CI/CD does it) — changes are not live until deployed.

❌ Mistake: Putting secrets in stage variables.
✅ Correct: Use Secrets Manager/SSM; stage variables are plain config.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a stage?
A1: A named deployment of an API such as dev or prod with its own URL.

Q2: [Medium] How does a Lambda alias combine with stage variables?
A2: Use `${stageVariables.alias}` in the integration so dev stage calls `dev` alias and prod calls `live`.

Q3: [Hard] How to do a safe prod release?
A3: Canary on REST stage (small traffic % to new deployment) or weighted Lambda alias; watch alarms; promote or roll back.

---

## ✅ Quick Checklist
□ Per-stage throttling and logging
□ Redeploy after changes
□ Separate accounts for prod

---

## ⚡ 1-Line Summary
Stages = named environments of one API | Stage = एक API के अलग-अलग एनवायरनमेंट।

## ➡️ Next: API Gateway Auth

---
