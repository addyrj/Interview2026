# 302. Design Serverless API on AWS
# AWS: API Gateway (HTTP API) + Lambda + DynamoDB
# Azure: API Management / Functions HTTP trigger + Azure Functions + Cosmos DB (or Table Storage)
# हिंदी में: सर्वरलेस API = सर्वर मैनेज किए बिना API Gateway + Lambda + DynamoDB

---

## 🔵 Simple Definition
HTTP API routes requests to Lambda functions that read/write a DynamoDB table; you pay per request.
हिंदी: API Gateway रिक्वेस्ट Lambda को देता है, Lambda DynamoDB में डेटा रखता है, पैसा सिर्फ इस्तेमाल का।

## 🔴 Why it Exists
No servers to patch, scales to zero and to thousands of concurrent requests automatically.

## 🟢 How it Works
```
Client -> CloudFront/WAF (optional) -> API Gateway HTTP API
            JWT authorizer (Cognito) -> Lambda (Node.js 20, arm64)
                                          |  IAM role: PutItem/GetItem on ONE table
                                          v
                                      DynamoDB (on-demand, PITR)
Lambda errors -> DLQ/SQS ; logs -> CloudWatch
```

## 💻 Code / Config Example
Files in this folder:
- `template.yaml` : SAM template (CloudFormation + `Transform: AWS::Serverless-2016-10-31`)
- `src/index.mjs` : handler for `POST /items` and `GET /items/{id}`

Deploy: `sam build && sam deploy --guided` (not run here; no AWS credentials).

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| API front door | API Gateway HTTP/REST API | API Management or Functions HTTP trigger |
| Compute | Lambda | Azure Functions (Consumption/Flex) |
| NoSQL | DynamoDB | Cosmos DB / Table Storage |
| Auth | Cognito JWT authorizer | Entra ID / B2C |
| Pricing | per request + GB-s (approximate - check current docs) | per execution + GB-s |

## 💰 Cost / HA / Security
- Cost: HTTP API is cheaper than REST API; DynamoDB on-demand for spiky load, provisioned + autoscaling for steady load.
- HA: regional services, multi-AZ by default; set reserved concurrency to protect the DB.
- Security: least-privilege role scoped to the table ARN, authorizer on every route, throttling, WAF on REST API/CloudFront.

## ⚠️ Common Mistakes
❌ `dynamodb:*` on `Resource: "*"`.
✅ Only needed actions on the table ARN.

❌ Creating the SDK client inside the handler on every call.
✅ Create it outside the handler so warm invocations reuse it.

## ⚫ Interview Q&A
Q1 [Easy]: Why HTTP API over REST API?
A1: Lower cost/latency and JWT auth built in; REST API adds usage plans, API keys, request validation, WAF integration.

Q2 [Medium]: What is a cold start and how do you reduce it?
A2: Init time for a new execution environment; use smaller packages, arm64, lazy imports, provisioned concurrency or SnapStart where supported.

Q3 [Hard]: How do you make writes idempotent and handle downstream failure?
A3: Client idempotency key with a DynamoDB conditional write, async paths via SQS with DLQ, retries with backoff, partial batch responses.

## ✅ Quick Checklist
□ Authorizer on all routes
□ Role scoped to table ARN
□ DLQ + alarms on Errors/Throttles

## ⚡ 1-Line Summary
API Gateway + Lambda + DynamoDB = pay-per-use API. | बिना सर्वर के स्केलेबल API।

## ➡️ Next: 303. Design High Availability on AWS
