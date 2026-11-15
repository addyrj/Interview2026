# 173. Translate
# AWS: Amazon Translate
# Azure: Azure AI Translator
# हिंदी में: text को एक भाषा से दूसरी भाषा में बदलना

---

## 🔵 Simple Definition
Translate is a neural machine translation API for real-time text and batch document translation.
हिंदी: Translate text का अनुवाद एक भाषा से दूसरी में करता है, जैसे English से Hindi।

---

## 🔴 Why it Exists
Serving users in many languages manually is slow and costly.

---

## 🟢 How it Works
```
text + SourceLanguageCode (or "auto") + TargetLanguageCode
 -> translate_text -> TranslatedText
Batch: start_text_translation_job over S3 folder
Custom terminology: CSV of brand terms kept untranslated
```

---

## 💻 Code / Config Example
```python
import boto3

tr = boto3.client("translate", region_name="ap-south-1")
r = tr.translate_text(
    Text="Your payment was successful.",
    SourceLanguageCode="en",
    TargetLanguageCode="hi",
)
print(r["TranslatedText"])
```
```bash
# keep brand names fixed
aws translate import-terminology --name brand --merge-strategy OVERWRITE \
  --data-file fileb://terms.csv --terminology-data Format=CSV
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Translate | AI Translator |
| Glossary | Custom terminology | Custom glossary / Custom Translator |
| Documents | Batch jobs | Document translation |
| Pricing | Per character (approximate — check current docs) | Per character |

---

## ⚠️ Common Mistakes
❌ Mistake: Translating the same strings repeatedly.
✅ Correct: Cache translations (DB/Redis) per string and language.

❌ Mistake: Translating placeholders like `{name}`.
✅ Correct: Protect with HTML/markup tags or custom terminology; test output.

---

## ⚫ Interview Q&A
Q1: [Easy] Real-time vs batch?
A1: Real-time for short text per request; batch for many documents in S3.

Q2: [Medium] Keep product names untranslated?
A2: Custom terminology.

Q3: [Hard] i18n strategy for a SaaS app.
A3: Translate UI strings at build time, cache runtime content, human-review critical text, fall back to English, store language per user.

---

## ✅ Quick Checklist
□ Cache results
□ Terminology for brand terms
□ Human review for legal text

---

## ⚡ 1-Line Summary
Translate is a pay-per-character translation API | Translate अक्षरों के हिसाब से चलने वाला अनुवाद API है।

## ➡️ Next: 174. Personalize
