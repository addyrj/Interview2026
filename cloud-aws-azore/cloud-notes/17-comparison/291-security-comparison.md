# 291. Security Comparison
# AWS: IAM, KMS, Secrets Manager, WAF, Shield, GuardDuty, Security Hub
# Azure: Entra ID + RBAC, Key Vault, WAF, DDoS Protection, Defender for Cloud
# हिंदी में: सिक्योरिटी सर्विसेज की तुलना

---

## 🔵 Simple Definition
Both clouds secure identity, secrets, encryption, network edge and threat detection with equivalent services.
हिंदी: दोनों क्लाउड में पहचान, सीक्रेट, एन्क्रिप्शन और थ्रेट डिटेक्शन की बराबर सर्विसेज हैं।

---

## 🔴 Why it Exists
Most breaches come from leaked keys, open ports and over-broad permissions.

---

## 🟢 How it Works
```
Identity   : IAM role            <-> Managed identity + RBAC role assignment
Secrets    : Secrets Manager/SSM <-> Key Vault (secrets)
Keys       : KMS                 <-> Key Vault keys (HSM options)
Edge       : WAF + Shield        <-> WAF (Front Door/App GW) + DDoS Protection
Detection  : GuardDuty/SecHub    <-> Defender for Cloud / Sentinel
```

---

## 💻 Code / Config Example
```bash
# Store and read a secret
aws secretsmanager create-secret --name prod/db --secret-string '{"password":"CHANGE_ME"}'
aws secretsmanager get-secret-value --secret-id prod/db --query SecretString --output text

az keyvault create -n kv-demo-123 -g rg-demo --enable-rbac-authorization true
az keyvault secret set --vault-name kv-demo-123 -n db-password --value CHANGE_ME
az keyvault secret show --vault-name kv-demo-123 -n db-password --query value -o tsv
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Workload identity | IAM role (instance profile, IRSA) | Managed identity |
| Secret store | Secrets Manager | Key Vault |
| Encryption keys | KMS | Key Vault / Managed HSM |
| Audit log | CloudTrail | Activity Log |
| Pricing | Per secret/key + API calls | Per operation (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Access keys/client secrets in repos or env files.
✅ Correct: Roles / managed identities; secrets in vault.

❌ Mistake: Owner/AdministratorAccess for apps.
✅ Correct: Least privilege scoped roles.

---

## ⚫ Interview Q&A
Q1: [Easy] Secrets Manager equivalent?
A1: Key Vault secrets.

Q2: [Medium] IAM role vs managed identity?
A2: Both give a workload short-lived credentials without stored secrets; identity is attached to the resource.

Q3: [Hard] Secure CI/CD to cloud without stored keys?
A3: GitHub OIDC federation: AWS IAM OIDC provider role / Azure federated credential on an app registration.

---

## ✅ Quick Checklist
□ No static keys
□ Least privilege
□ Audit logs and alerts on

---

## ⚡ 1-Line Summary
IAM role=Managed identity, Secrets Manager=Key Vault. | IAM role=Managed identity, Secrets Manager=Key Vault।

## ➡️ Next: 292. Monitoring Comparison
