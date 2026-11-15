# 168. Rekognition (Image AI)
# AWS: Amazon Rekognition
# Azure: Azure AI Vision (and Face)
# हिंदी में: फोटो/वीडियो में चीज़ें, चेहरे और text पहचानना

---

## 🔵 Simple Definition
Rekognition is a pre-trained API for labels, faces, text in images, content moderation and video analysis; no ML skills needed.
हिंदी: Rekognition photo में objects, faces और text अपने-आप पहचान लेता है।

---

## 🔴 Why it Exists
Building computer-vision models needs data and GPUs.
A single API call gives labels or moderation flags for user uploads.

---

## 🟢 How it Works
```
User upload -> S3 -> (S3 event) Lambda
Lambda -> rekognition.detect_labels / detect_moderation_labels
       -> labels + confidence -> save to DB / reject image
```

---

## 💻 Code / Config Example
```python
import boto3

rek = boto3.client("rekognition", region_name="ap-south-1")

resp = rek.detect_labels(
    Image={"S3Object": {"Bucket": "my-uploads", "Name": "photo.jpg"}},
    MaxLabels=5,
    MinConfidence=80,
)
for l in resp["Labels"]:
    print(l["Name"], round(l["Confidence"], 1))

# moderation
mod = rek.detect_moderation_labels(
    Image={"S3Object": {"Bucket": "my-uploads", "Name": "photo.jpg"}},
    MinConfidence=70,
)
print("blocked" if mod["ModerationLabels"] else "ok")
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Rekognition | AI Vision / Face / Content Safety |
| Custom model | Custom Labels | Custom Vision (check current status) |
| Input | S3 object or bytes | URL or bytes |
| Pricing | Per image / per video minute (approximate — check current docs) | Per transaction |

---

## ⚠️ Common Mistakes
❌ Mistake: Treating confidence as certainty for face matching in decisions about people.
✅ Correct: Use high thresholds, human review, and check legal/ethical limits.

❌ Mistake: Bucket in a different region from the API call.
✅ Correct: Call Rekognition in the same region as the S3 bucket.

---

## ⚫ Interview Q&A
Q1: [Easy] What can Rekognition detect?
A1: Labels, faces, celebrities, text, unsafe content, PPE, video activity.

Q2: [Medium] Sync vs async for video?
A2: Video uses async Start* APIs with SNS completion notifications; images are synchronous.

Q3: [Hard] Build a moderation pipeline for uploads.
A3: Presigned upload to S3 -> event to Lambda/SQS -> detect_moderation_labels -> approve/quarantine tag -> notify; DLQ for failures.

---

## ✅ Quick Checklist
□ Same region as bucket
□ MinConfidence tuned
□ Human review for sensitive use

---

## ⚡ 1-Line Summary
Rekognition analyses images and video via API | Rekognition API से image और video का analysis करता है।

## ➡️ Next: 169. Textract (Document AI)
