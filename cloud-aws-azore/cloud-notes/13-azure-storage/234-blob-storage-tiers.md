# 234. Blob Storage Tiers
# AWS: S3 storage classes (Standard, IA, Glacier)
# Azure: Blob access tiers (Hot, Cool, Cold, Archive)
# हिंदी में: एक्सेस की आवृत्ति के हिसाब से सस्ता स्टोरेज चुनना

---

## 🔵 Simple Definition (2 lines)
Tiers trade storage price against access price: Hot (frequent), Cool, Cold, and Archive (offline, cheapest storage).
हिंदी: कम इस्तेमाल होने वाला डेटा ठंडे tier में डालें तो स्टोरेज बिल घटता है।

---

## 🔴 Why it Exists (2 lines)
Logs and backups are rarely read after a month, so Hot pricing wastes money.
Lifecycle rules move data automatically.

---

## 🟢 How it Works
```
Hot -> Cool (30d) -> Cold (90d) -> Archive (365d) -> Delete
 - Cooler tier: lower storage cost, higher read cost, minimum retention
   (approx: Cool 30d, Cold 90d, Archive 180d - early deletion fee; check docs)
 - Archive is offline: rehydrate to Hot/Cool first (takes hours)
```

---

## 💻 Code / Config Example
```json
{
  "rules": [
    {
      "enabled": true,
      "name": "age-out-logs",
      "type": "Lifecycle",
      "definition": {
        "filters": { "blobTypes": ["blockBlob"], "prefixMatch": ["logs/"] },
        "actions": {
          "baseBlob": {
            "tierToCool":    { "daysAfterModificationGreaterThan": 30 },
            "tierToArchive": { "daysAfterModificationGreaterThan": 180 },
            "delete":        { "daysAfterModificationGreaterThan": 730 }
          }
        }
      }
    }
  ]
}
```
```bash
az storage account management-policy create --account-name myappstore \
  --resource-group rg-app --policy @policy.json
az storage blob set-tier --account-name myappstore -c logs -n old.log --tier Archive --auth-mode login
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Hot | S3 Standard | Hot |
| Infrequent | Standard-IA | Cool / Cold |
| Offline | Glacier Flexible / Deep Archive | Archive |
| Auto-tiering | Intelligent-Tiering | Lifecycle rules (+ last-access tracking) |

---

## ⚠️ Common Mistakes
❌ Mistake: Archiving data you still query.
✅ Correct: Archive only compliance data; rehydration is slow and costs money.

❌ Mistake: Moving tiny files to Cool.
✅ Correct: Account for per-operation and early-deletion charges.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Which tier is offline?
A1: Archive.

Q2: [Medium] How to automate tiering?
A2: Lifecycle management policy with days-since-modified or last-access rules.

Q3: [Hard] Cost of reading Archive data?
A3: Rehydrate (standard priority takes hours; high priority faster at higher cost), pay rehydration and read fees; plan DR runbooks accordingly.

---

## ✅ Quick Checklist
□ Lifecycle policy per prefix
□ Early-deletion windows known
□ Archive restore time accepted by the business

---

## ⚡ 1-Line Summary
Colder tier = cheaper storage, costlier access | ठंडा tier = सस्ता स्टोरेज, महँगा एक्सेस

## ➡️ Next: Azure Files

---
