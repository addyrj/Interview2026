# 160. AWS SDK (Node.js + Python)
# AWS: AWS SDK for JavaScript v3 (@aws-sdk/*) and boto3
# Azure: Azure SDK (@azure/* for JS, azure-* for Python)
# हिंदी में: AWS SDK - अपने कोड से AWS सेवाओं को कॉल करने की लाइब्रेरी

---

## 🔵 Simple Definition
The AWS SDKs sign and send API requests to AWS from your app. JS v3 is modular (one package per service); Python uses `boto3`. Credentials come from the default provider chain.
हिंदी: कोड में S3, SQS जैसी सेवाओं को बुलाने की लाइब्रेरी; क्रेडेंशियल अपने-आप (env, role) मिल जाते हैं।

## 🔴 Why it Exists
Hand-signing SigV4 requests is error-prone. SDKs add signing, retries, pagination and typed clients.

## 🟢 How it Works
```
Credential chain: env vars -> shared config/SSO -> container role (ECS)
                  -> EC2 instance profile / Lambda role
Client(region) --> sign (SigV4) --> HTTPS --> AWS API (auto retry w/ backoff)
```

## 💻 Code / Config Example
```javascript
// Node.js (@aws-sdk/client-s3, v3) - ES module
import { S3Client, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";

const s3 = new S3Client({ region: "ap-south-1" }); // no keys in code
await s3.send(new PutObjectCommand({ Bucket: "my-uploads", Key: "a.txt", Body: "hello" }));
const out = await s3.send(new GetObjectCommand({ Bucket: "my-uploads", Key: "a.txt" }));
console.log(await out.Body.transformToString());
```
```python
# Python (boto3) - FastAPI-style helper
import boto3
from botocore.config import Config

s3 = boto3.client("s3", region_name="ap-south-1",
                  config=Config(retries={"max_attempts": 5, "mode": "standard"}))
s3.put_object(Bucket="my-uploads", Key="a.txt", Body=b"hello")
print(s3.get_object(Bucket="my-uploads", Key="a.txt")["Body"].read().decode())

# Paginate big listings
for page in s3.get_paginator("list_objects_v2").paginate(Bucket="my-uploads"):
    for o in page.get("Contents", []):
        print(o["Key"])
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| JS package | @aws-sdk/client-s3 | @azure/storage-blob |
| Python package | boto3 | azure-storage-blob |
| Auth default | Provider chain | DefaultAzureCredential |
| Pricing | SDK free; pay for API usage | SDK free |

## ⚠️ Common Mistakes
❌ Hardcoding access keys. ✅ Use IAM roles / SSO; the SDK finds them.
❌ Creating a client per request. ✅ Create once and reuse (also across Lambda invocations).

## ⚫ Interview Q&A
Q1 [Easy]: Where do SDK credentials come from? A1: The default provider chain (env, profile, role).
Q2 [Medium]: JS v2 vs v3? A2: v3 is modular, uses `client.send(Command)`, and is the maintained line; v2 is end-of-support.
Q3 [Hard]: Handling throttling? A3: SDK retries with exponential backoff and jitter; tune max attempts and make calls idempotent.

## ✅ Quick Checklist
□ No keys in code
□ Client reused
□ Pagination used for lists

## ⚡ 1-Line Summary
SDK = signed, retried AWS calls from your code | SDK आपके कोड से AWS को सुरक्षित तरीके से कॉल करता है।

## ➡️ Next: Section 08 (next topic in the series)
