# 158. SAM - Serverless App Model
# AWS: AWS SAM (Serverless Application Model)
# Azure: Azure Functions Core Tools + Bicep (closest equivalent)
# हिंदी में: SAM - Lambda और API Gateway को छोटे टेम्पलेट में बनाने का शॉर्टकट

---

## 🔵 Simple Definition
SAM is a CloudFormation extension with short syntax for Lambda, API Gateway, DynamoDB, plus a CLI (`sam build/local/deploy`) for local testing.
हिंदी: कम लाइनों में सर्वरलेस ऐप बनाएँ और लोकल में टेस्ट करें।

## 🔴 Why it Exists
Plain CloudFormation needs dozens of lines per Lambda + API. SAM's `Transform` expands a few lines into full resources.

## 🟢 How it Works
```
template.yaml (Transform: AWS::Serverless-2016-10-31)
  sam build  -> packages code/deps
  sam local invoke / start-api (Docker)
  sam deploy -> CloudFormation expands SAM -> stack
```

## 💻 Code / Config Example
```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Runtime: nodejs20.x
    Timeout: 10
    MemorySize: 256
Resources:
  OrdersTable:
    Type: AWS::Serverless::SimpleTable
  GetOrder:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.handler
      CodeUri: src/
      Environment:
        Variables: { TABLE: !Ref OrdersTable }
      Policies:
        - DynamoDBReadPolicy: { TableName: !Ref OrdersTable }
      Events:
        Api:
          Type: Api
          Properties: { Path: "/orders/{id}", Method: get }
Outputs:
  ApiUrl:
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
```
```bash
sam build && sam local start-api && sam deploy --guided
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Tool | SAM | Functions Core Tools (`func`) |
| Local run | sam local (Docker) | func start / Azurite |
| IaC | CloudFormation transform | Bicep/ARM |
| Pricing | Free tool | Free tool |

## ⚠️ Common Mistakes
❌ Docker not running for sam local. ✅ Start Docker first.
❌ Deploying without a samconfig. ✅ Use `sam deploy --guided` once, commit samconfig.toml.

## ⚫ Interview Q&A
Q1 [Easy]: What is the Transform line? A1: Tells CloudFormation to expand SAM resources.
Q2 [Medium]: SAM vs CDK? A2: SAM is a serverless-focused template syntax; CDK is general-purpose code.
Q3 [Hard]: Gradual Lambda deployment? A3: AutoPublishAlias + DeploymentPreference (Canary/Linear) using CodeDeploy.

## ✅ Quick Checklist
□ Globals for shared settings
□ Least-privilege policy templates
□ sam validate in CI

## ⚡ 1-Line Summary
SAM = shorthand CloudFormation for serverless | SAM सर्वरलेस के लिए छोटा CloudFormation है।

## ➡️ Next: X-Ray - Distributed Tracing
