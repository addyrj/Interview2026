---

# 94. API Gateway — Complete Guide
# AWS: Amazon API Gateway
# Azure: Azure API Management (APIM)
# हिंदी में: API गेटवे संपूर्ण गाइड

---

## 🔵 Simple Definition (2 lines)
API Gateway is a managed front door for APIs: routing, auth, throttling, caching, transformation and monitoring.
हिंदी: API Gateway आपकी API का मैनेज्ड प्रवेश द्वार है, जो routing, auth और throttling संभालता है।

---

## 🔴 Why it Exists (2 lines)
Every backend (Lambda, ECS, EC2) would otherwise re-implement TLS, auth, rate limits and versioning. A gateway centralises it.

---

## 🟢 How it Works
```
Client -> [Custom domain + TLS (ACM)]
       -> API Gateway: authorizer -> throttle/usage plan -> (cache) -> mapping
       -> Integration: Lambda | HTTP backend | VPC Link (private ALB/NLB) | AWS service
       -> CloudWatch logs/metrics, WAF (REST), X-Ray
Types: REST API, HTTP API, WebSocket API
```

---

## 💻 Code / Config Example
```yaml
# OpenAPI-driven HTTP API in CloudFormation/SAM: proxy to a backend on a VPS/ALB
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Resources:
  Api:
    Type: AWS::Serverless::HttpApi
    Properties:
      DefinitionBody:
        openapi: "3.0.1"
        info: { title: backend-proxy, version: "1.0" }
        paths:
          /{proxy+}:
            x-amazon-apigateway-any-method:
              x-amazon-apigateway-integration:
                type: http_proxy
                httpMethod: ANY
                uri: https://api.example.com/{proxy}
                payloadFormatVersion: "1.0"
                requestParameters:
                  overwrite:path: /$request.path.proxy
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | API Gateway | API Management |
| Policies | Usage plans, authorizers, mapping templates | XML policy engine |
| Private backend | VPC Link | VNet integration |
| Pricing | Per request (approximate — check current docs) | Tier-based per unit/hour (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Putting everything behind a 29-30 s synchronous call.
✅ Correct: Long jobs go async (SQS/Step Functions) and return 202.

❌ Mistake: No throttling, so a bot burns your Lambda bill.
✅ Correct: Set stage throttling, usage plans, and WAF.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What does API Gateway do?
A1: Receives API calls and routes them to backends with auth, throttling and monitoring.

Q2: [Medium] What is VPC Link?
A2: Lets API Gateway reach private resources (internal ALB/NLB) inside a VPC.

Q3: [Hard] Design a secure public API for a private ECS service.
A3: API Gateway (custom domain, JWT authorizer, throttling, WAF) -> VPC Link -> internal ALB -> ECS tasks in private subnets.

---

## ✅ Quick Checklist
□ Auth on every route
□ Throttling and logging on
□ Custom domain with ACM cert

---

## ⚡ 1-Line Summary
API Gateway = managed API front door | API Gateway = API का मैनेज्ड फ्रंट डोर।

## ➡️ Next: API Gateway REST vs HTTP vs WebSocket

---
