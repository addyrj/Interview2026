# 130. AWS Secrets Manager
# AWS: AWS Secrets Manager
# Azure: Azure Key Vault (Secrets)
# हिंदी में: पासवर्ड और API कीज़ को सुरक्षित रखने और अपने-आप बदलने की सेवा

---

## 🔵 Simple Definition
Secrets Manager stores secrets encrypted with KMS, controls access with IAM, and can rotate them automatically.
हिंदी: Secrets Manager गोपनीय जानकारी एन्क्रिप्ट करके रखता है और ऑटो-रोटेशन कर सकता है।

---

## 🔴 Why it Exists
Secrets in .env files, images or git leak easily and are never rotated.

---

## 🟢 How it Works
```
App role (IAM) --GetSecretValue--> Secrets Manager --decrypt--> KMS key
                                        |
                          Rotation Lambda (RDS etc.) changes password on schedule
Versions: AWSCURRENT / AWSPREVIOUS
```

---

## 💻 Code / Config Example
```python
# secrets_demo.py - boto3 (runs against moto)
import boto3, json
sm = boto3.client("secretsmanager", region_name="ap-south-1")
sm.create_secret(Name="prod/api/db",
                 SecretString=json.dumps({"user": "app", "password": "s3cr3t"}))
val = json.loads(sm.get_secret_value(SecretId="prod/api/db")["SecretString"])
print(val["user"])
```
```javascript
// Node.js (AWS SDK v3): @aws-sdk/client-secrets-manager
import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";
const c = new SecretsManagerClient({ region: "ap-south-1" });
const r = await c.send(new GetSecretValueCommand({ SecretId: "prod/api/db" }));
const db = JSON.parse(r.SecretString);
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Secrets Manager | Key Vault secrets |
| Rotation | Built-in (Lambda) | Event Grid + Function / some auto rotation |
| Access | IAM policy / resource policy | RBAC / access policy, Managed Identity |
| Pricing | Per secret/month + API calls (approximate - check current docs) | Per operation (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Fetching the secret on every request.
✅ Correct: Cache in memory for a short TTL.

❌ Mistake: Putting secrets in Docker image ENV.
✅ Correct: Fetch at runtime via task role or inject through ECS `secrets`.

---

## ⚫ Interview Q&A
Q1: [Easy] Why not a .env file?
A1: Not encrypted, not audited, hard to rotate.

Q2: [Medium] Secrets Manager vs Parameter Store?
A2: SM has rotation and cross-account sharing but costs per secret; Parameter Store is cheaper/simple config with SecureString.

Q3: [Hard] How does zero-downtime rotation work?
A3: Rotation Lambda creates a new version (AWSPENDING), tests it, then promotes to AWSCURRENT; apps refetch on auth failure or by TTL.

---

## ✅ Quick Checklist
□ Access via IAM role only
□ Rotation enabled for DB creds
□ Client-side caching

---

## ⚡ 1-Line Summary
Secrets Manager = encrypted, audited, rotating secrets | Secrets Manager गुप्त जानकारी को एन्क्रिप्टेड और रोटेट होने वाली रखता है।

## ➡️ Next: Systems Manager Parameter Store
