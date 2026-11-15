---

# 89. Lambda Environment Variables
# AWS: Lambda environment variables (+ Secrets Manager / SSM Parameter Store)
# Azure: Function App application settings (+ Key Vault references)
# हिंदी में: लैम्ब्डा एनवायरनमेंट वेरिएबल्स

---

## 🔵 Simple Definition (2 lines)
Environment variables are key-value settings given to the function at runtime, read via process.env or os.environ.
हिंदी: Environment variables रनटाइम पर फ़ंक्शन को दी गई सेटिंग्स हैं, कोड बदले बिना कॉन्फ़िग बदलने के लिए।

---

## 🔴 Why it Exists (2 lines)
Hard-coding table names, URLs or keys makes one codebase unusable across dev/staging/prod. Env vars separate config from code.

---

## 🟢 How it Works
```
Function config: Environment.Variables = {TABLE=orders, STAGE=prod}
   - total size limit 4 KB (approximate — check current docs)
   - encrypted at rest with KMS (default AWS-managed key, or your CMK)
Secrets? -> store in Secrets Manager / SSM SecureString, put only the NAME in env var,
            fetch at cold start and cache.
Reserved vars (set by Lambda): AWS_REGION, AWS_LAMBDA_FUNCTION_NAME, AWS_ACCESS_KEY_ID...
```

---

## 💻 Code / Config Example
```yaml
# SAM template snippet
Resources:
  Api:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: nodejs20.x
      Handler: index.handler
      Environment:
        Variables:
          TABLE_NAME: orders
          DB_SECRET_ID: prod/db/credentials   # name only, not the secret
```
```python
# Python handler: read env var, fetch secret once, cache across warm invokes
import os, json, boto3
_sm = boto3.client("secretsmanager")
_secret = None

def handler(event, context):
    global _secret
    if _secret is None:
        _secret = json.loads(
            _sm.get_secret_value(SecretId=os.environ["DB_SECRET_ID"])["SecretString"])
    return {"table": os.environ["TABLE_NAME"], "user": _secret["username"]}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Config | Environment variables | Application settings |
| Secrets | Secrets Manager / SSM | Key Vault reference `@Microsoft.KeyVault(...)` |
| Encryption | KMS | Platform-managed / Key Vault |
| Pricing | Free; Secrets Manager charges per secret (approximate — check current docs) | Free settings; Key Vault per operation (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Putting passwords in plain env vars committed in IaC.
✅ Correct: Reference Secrets Manager/SSM and grant read via the role.

❌ Mistake: Fetching the secret on every invocation.
✅ Correct: Cache it outside the handler.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] How do you read an env var in Node.js Lambda?
A1: `process.env.TABLE_NAME`.

Q2: [Medium] Does changing an env var restart anything?
A2: It updates the function configuration and new execution environments pick it up; old warm ones are replaced.

Q3: [Hard] Best way to handle secrets with rotation?
A3: Secrets Manager with rotation, fetch with TTL cache (or the Parameters and Secrets Lambda extension) so rotation is picked up without redeploy.

---

## ✅ Quick Checklist
□ No secrets in plain text
□ Per-stage values in IaC
□ Secrets cached outside handler

---

## ⚡ 1-Line Summary
Env vars keep config out of code | Env vars कॉन्फ़िग को कोड से अलग रखते हैं।

## ➡️ Next: Lambda Concurrency

---
