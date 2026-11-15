# 308. Deploy FastAPI to Lambda
# AWS: Lambda + API Gateway HTTP API (Mangum adapter, SAM)
# Azure: Azure Functions (ASGI via AsgiFunctionApp) or Container Apps
# हिंदी में: FastAPI ऐप को Mangum के ज़रिए Lambda पर चलाना, बिना सर्वर

---

## 🔵 Simple Definition
Mangum translates API Gateway events into ASGI calls so an unchanged FastAPI app runs inside a Lambda handler.
हिंदी: Mangum अडैप्टर API Gateway के इवेंट को FastAPI समझ सके ऐसे बदल देता है।

## 🔴 Why it Exists
Keep a normal FastAPI codebase but get scale-to-zero and per-request billing for low or spiky traffic.

## 🟢 How it Works
```
Client -> HTTP API (ANY / and /{proxy+}) -> Lambda python3.12 (arm64)
        -> Mangum(app) -> FastAPI router -> response
Package: zip (SAM builds requirements.txt) or container image (up to 10 GB) for heavy deps
```

## 💻 Code / Config Example
Files: `app/main.py` (FastAPI + `handler = Mangum(app, lifespan="off")`), `app/requirements.txt`, `template.yaml` (SAM). Deploy: `sam build && sam deploy --guided` (not run here).
Tested locally with FastAPI TestClient and by calling `handler` with a synthetic HTTP API v2 event.

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Compute | Lambda | Azure Functions |
| ASGI adapter | Mangum | `azure.functions.AsgiFunctionApp` |
| Front door | API Gateway HTTP API / Function URL | built-in HTTP trigger / APIM |
| Pricing | requests + GB-s (approximate - check current docs) | executions + GB-s |

## 💰 Cost / HA / Security
- Cost: cheap for spiky load; steady high traffic is cheaper on Fargate/EC2.
- HA: multi-AZ managed; set reserved concurrency to protect downstream DB; use RDS Proxy for SQL.
- Security: least-privilege function role, authorizer on the API, secrets from Secrets Manager (cache outside handler), disable `/docs` in prod if not needed.

## ⚠️ Common Mistakes
❌ Relying on in-memory state or local files.
✅ Use DynamoDB/S3/RDS; `/tmp` is temporary only.

❌ Running uvicorn inside Lambda.
✅ Use the Mangum handler.

## ⚫ Interview Q&A
Q1 [Easy]: What does Mangum do?
A1: It is an ASGI adapter converting Lambda/API Gateway events to ASGI requests and back.

Q2 [Medium]: Zip vs container image?
A2: Zip is simpler and faster to cold start for small apps (50 MB zipped / 250 MB unzipped limits, approximate - check current docs); containers fit big dependencies like ML libs.

Q3 [Hard]: How do you handle WebSockets or long requests?
A3: API Gateway timeout and Lambda 15 min cap make long work unsuitable; use API Gateway WebSocket APIs, async jobs via SQS, or move to Fargate.

## ✅ Quick Checklist
□ App state externalised
□ `lifespan="off"` or tested lifespan
□ Memory tuned, timeout under API limit

## ⚡ 1-Line Summary
Mangum makes FastAPI a Lambda handler. | Mangum से FastAPI सीधे Lambda हैंडलर बन जाता है।

## ➡️ Next: 309. Setup S3 + CloudFront
