# 131. AWS Systems Manager Parameter Store
# AWS: SSM Parameter Store
# Azure: Azure App Configuration (+ Key Vault for secrets)
# हिंदी में: कॉन्फ़िग और छोटे सीक्रेट रखने की सस्ती हाइरार्किकल सेवा

---

## 🔵 Simple Definition
Parameter Store keeps config values as String, StringList or SecureString (KMS-encrypted) in a path hierarchy.
हिंदी: Parameter Store कॉन्फ़िग वैल्यू को पाथ में रखता है, और SecureString एन्क्रिप्टेड होता है।

---

## 🔴 Why it Exists
Per-environment config should live outside code, versioned and access-controlled.

---

## 🟢 How it Works
```
/myapp/prod/DB_HOST        (String)
/myapp/prod/DB_PASSWORD    (SecureString -> KMS)
App role: ssm:GetParametersByPath on /myapp/prod/*
Tiers: Standard (free) | Advanced (paid, bigger values, policies)
```

---

## 💻 Code / Config Example
```python
# ssm_demo.py (boto3, runs against moto)
import boto3
ssm = boto3.client("ssm", region_name="ap-south-1")
ssm.put_parameter(Name="/myapp/prod/DB_HOST", Value="db.internal", Type="String")
ssm.put_parameter(Name="/myapp/prod/DB_PASSWORD", Value="s3cr3t", Type="SecureString")
r = ssm.get_parameters_by_path(Path="/myapp/prod", WithDecryption=True)
print({p["Name"].split("/")[-1]: p["Value"] for p in r["Parameters"]})
```
```bash
aws ssm get-parameter --name /myapp/prod/DB_PASSWORD --with-decryption --query Parameter.Value --output text
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Config store | Parameter Store | App Configuration |
| Secrets | SecureString / Secrets Manager | Key Vault |
| Rotation | None built-in | Via Key Vault patterns |
| Pricing | Standard tier free (approximate - check current docs) | Free/Standard tiers (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Storing passwords as plain String.
✅ Correct: Use SecureString and grant kms:Decrypt.

❌ Mistake: Forgetting `--with-decryption`.
✅ Correct: Always pass WithDecryption for SecureString.

---

## ⚫ Interview Q&A
Q1: [Easy] What are the parameter types?
A1: String, StringList, SecureString.

Q2: [Medium] Parameter Store vs Secrets Manager?
A2: Parameter Store is cheap config storage; Secrets Manager adds rotation and replication.

Q3: [Hard] How do you inject parameters into ECS?
A3: In the task definition `secrets` with `valueFrom` the parameter ARN; execution role needs ssm:GetParameters and kms:Decrypt.

---

## ✅ Quick Checklist
□ Path hierarchy per env
□ SecureString for sensitive values
□ IAM limited to path

---

## ⚡ 1-Line Summary
Parameter Store = cheap hierarchical config and secrets | Parameter Store सस्ता और पाथ-आधारित कॉन्फ़िग स्टोर है।

## ➡️ Next: KMS - Key Management
