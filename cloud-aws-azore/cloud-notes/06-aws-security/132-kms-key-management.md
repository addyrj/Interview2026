# 132. KMS - Key Management
# AWS: AWS Key Management Service (KMS)
# Azure: Azure Key Vault (Keys) / Managed HSM
# हिंदी में: एन्क्रिप्शन कीज़ बनाने, संभालने और इस्तेमाल पर नियंत्रण की सेवा

---

## 🔵 Simple Definition
KMS creates and controls cryptographic keys; other AWS services use them for encryption. Key material never leaves KMS unencrypted.
हिंदी: KMS एन्क्रिप्शन कीज़ बनाता और नियंत्रित करता है, और की कभी बाहर साफ़ रूप में नहीं आती।

---

## 🔴 Why it Exists
Encrypting data needs safe key storage, access control, rotation and audit.

---

## 🟢 How it Works
```
Envelope encryption:
 App -> KMS GenerateDataKey -> {plaintext DEK, encrypted DEK}
 App encrypts data with plaintext DEK, discards it, stores encrypted DEK with data
 Decrypt: KMS Decrypt(encrypted DEK) -> DEK -> decrypt data
Direct Encrypt/Decrypt limited to small payloads (4 KB)
Key types: AWS managed | customer managed (CMK)
```

---

## 💻 Code / Config Example
```python
# kms_demo.py (boto3, runs against moto)
import boto3
kms = boto3.client("kms", region_name="ap-south-1")
key = kms.create_key(Description="app-data")["KeyMetadata"]["KeyId"]
kms.create_alias(AliasName="alias/app-data", TargetKeyId=key)
ct = kms.encrypt(KeyId="alias/app-data", Plaintext=b"hello")["CiphertextBlob"]
print(kms.decrypt(CiphertextBlob=ct)["Plaintext"])
dk = kms.generate_data_key(KeyId="alias/app-data", KeySpec="AES_256")
print(len(dk["Plaintext"]), "byte data key")
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | KMS | Key Vault keys |
| HSM | CloudHSM | Managed HSM |
| Rotation | Optional automatic yearly rotation for CMKs | Rotation policy |
| Pricing | Per key/month + requests (approximate - check current docs) | Per key/operation (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Deleting a key still in use.
✅ Correct: Use scheduled deletion (waiting period) and disable first; data becomes unrecoverable.

❌ Mistake: Using * in key policy.
✅ Correct: Limit kms:Decrypt to specific roles.

---

## ⚫ Interview Q&A
Q1: [Easy] What is KMS for?
A1: Managing encryption keys used to protect data.

Q2: [Medium] What is envelope encryption?
A2: Encrypt data with a data key, encrypt the data key with a KMS key.

Q3: [Hard] AWS managed vs customer managed keys?
A3: AWS managed are automatic and not configurable; customer managed give custom policy, rotation, cross-account use and disable/delete control.

---

## ✅ Quick Checklist
□ CMK for sensitive data
□ Key policy least privilege
□ CloudTrail logs key use

---

## ⚡ 1-Line Summary
KMS = managed keys and envelope encryption | KMS एन्क्रिप्शन कीज़ का सुरक्षित प्रबंधन करता है।

## ➡️ Next: Certificate Manager (ACM)
