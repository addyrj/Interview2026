# 170. Comprehend (NLP)
# AWS: Amazon Comprehend
# Azure: Azure AI Language
# हिंदी में: text का sentiment, entities और भाषा पहचानना

---

## 🔵 Simple Definition
Comprehend analyses text for sentiment, entities, key phrases, language and PII without training a model.
हिंदी: Comprehend text से sentiment, नाम/जगह जैसी entities और PII निकालता है।

---

## 🔴 Why it Exists
Support tickets, reviews and chats are unstructured.
A managed NLP API turns them into tags you can filter and alert on.

---

## 🟢 How it Works
```
text (<= API size limit) -> comprehend.detect_sentiment / detect_entities / detect_pii_entities
Large sets -> async jobs reading from S3, writing results to S3
```

---

## 💻 Code / Config Example
```python
import boto3

c = boto3.client("comprehend", region_name="us-east-1")
text = "The delivery was late but support in Mumbai was great."

s = c.detect_sentiment(Text=text, LanguageCode="en")
print(s["Sentiment"], s["SentimentScore"])

e = c.detect_entities(Text=text, LanguageCode="en")
print([(x["Text"], x["Type"]) for x in e["Entities"]])

p = c.detect_pii_entities(Text="Call me at 9999999999", LanguageCode="en")
print(p["Entities"])
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Comprehend | AI Language |
| PII | detect_pii_entities / redaction | PII detection |
| Custom | Custom classification / entities | Custom text classification |
| Pricing | Per unit (100 characters) (approximate — check current docs) | Per text record |

---

## ⚠️ Common Mistakes
❌ Mistake: Sending Hindi text with `LanguageCode="en"`.
✅ Correct: Call `detect_dominant_language` first and check supported languages for each feature.

❌ Mistake: One API call per row for big datasets.
✅ Correct: Use batch_* APIs or async jobs.

---

## ⚫ Interview Q&A
Q1: [Easy] What does sentiment return?
A1: POSITIVE, NEGATIVE, NEUTRAL or MIXED with scores.

Q2: [Medium] Comprehend vs LLM on Bedrock?
A2: Comprehend is cheaper, deterministic and fixed-output; an LLM is flexible but costlier and variable.

Q3: [Hard] Redact PII before storing chats.
A3: Stream -> detect_pii_entities offsets -> mask spans -> store redacted text; keep originals encrypted with strict access or discard.

---

## ✅ Quick Checklist
□ Language code correct
□ Batch for volume
□ PII handled per policy

---

## ⚡ 1-Line Summary
Comprehend gives sentiment, entities and PII from text | Comprehend text से sentiment, entities और PII देता है।

## ➡️ Next: 171. Polly (Text to Speech)
