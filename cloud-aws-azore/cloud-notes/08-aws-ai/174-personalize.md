# 174. Personalize
# AWS: Amazon Personalize
# Azure: N/A (no direct managed service; closest is Azure Machine Learning recommenders or AI Search + custom)
# हिंदी में: user के हिसाब से recommendations देना

---

## 🔵 Simple Definition
Personalize trains recommendation models on your interaction data (clicks, purchases) and serves real-time recommendations.
हिंदी: Personalize user के behaviour से सीखकर product/content recommend करता है।

---

## 🔴 Why it Exists
Building recommender systems needs ML expertise and infrastructure.
Personalize automates training and hosting using the same tech as Amazon.com.

---

## 🟢 How it Works
```
Interactions CSV/stream -> Dataset group (Users, Items, Interactions)
 -> Solution (recipe, e.g. user-personalization) -> Solution version (training)
 -> Campaign (real-time endpoint) / Batch job
App -> personalize-runtime get_recommendations(userId)
App -> put_events (live clicks) to keep fresh
```

---

## 💻 Code / Config Example
```python
import boto3

rt = boto3.client("personalize-runtime", region_name="us-east-1")
resp = rt.get_recommendations(
    campaignArn="arn:aws:personalize:us-east-1:123456789012:campaign/home-feed",
    userId="user-42",
    numResults=10,
)
print([i["itemId"] for i in resp["itemList"]])
```
Interactions CSV schema needs `USER_ID`, `ITEM_ID`, `TIMESTAMP` columns (Avro schema defines them).

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Personalize | N/A (AWS-only concept); closest: Azure ML + custom recommender |
| Training | Managed recipes | Build yourself |
| Serving | Campaign endpoint | Managed online endpoint |
| Pricing | Training hours + per-TPS campaign + data ingestion (approximate — check current docs) | Compute-based |

---

## ⚠️ Common Mistakes
❌ Mistake: Too little interaction data (cold start).
✅ Correct: Collect enough events first; use popularity recipes initially.

❌ Mistake: Leaving an unused campaign running (billed for provisioned TPS).
✅ Correct: Set minProvisionedTPS low and delete unused campaigns.

---

## ⚫ Interview Q&A
Q1: [Easy] What data is needed?
A1: User-item interactions with timestamps; items and users optional.

Q2: [Medium] Campaign vs batch?
A2: Campaign = real-time API; batch = precompute recommendations to S3.

Q3: [Hard] Handle cold-start and freshness.
A3: Item metadata and the user-personalization recipe, send live events via PutEvents, retrain on a schedule, fall back to popular items.

---

## ✅ Quick Checklist
□ Enough interaction history
□ Live events streamed
□ Campaign cost watched

---

## ⚡ 1-Line Summary
Personalize is managed recommendations from click data | Personalize click data से managed recommendations देता है।

## ➡️ Next: 175. Forecast
