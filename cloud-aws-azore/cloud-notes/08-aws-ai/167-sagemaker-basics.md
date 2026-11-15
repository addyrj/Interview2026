# 167. SageMaker Basics
# AWS: Amazon SageMaker AI
# Azure: Azure Machine Learning
# हिंदी में: ML models को train और deploy करने का managed platform

---

## 🔵 Simple Definition
SageMaker is a managed platform to build, train and host your own ML models (notebooks, training jobs, real-time endpoints, pipelines).
हिंदी: SageMaker में आप अपने ML model को train करके endpoint के रूप में deploy कर सकते हैं।

---

## 🔴 Why it Exists
Training needs GPUs on demand and serving needs scaling and monitoring.
SageMaker provisions instances only for the job and tears them down.

---

## 🟢 How it Works
```
Data (S3) -> Training job (container + instance, pay while running)
          -> model.tar.gz in S3
          -> Endpoint (real-time) | Serverless | Async | Batch Transform
App -> sagemaker-runtime InvokeEndpoint -> prediction
```

---

## 💻 Code / Config Example
```python
# Call an already-deployed endpoint (boto3)
import boto3, json

rt = boto3.client("sagemaker-runtime", region_name="ap-south-1")
resp = rt.invoke_endpoint(
    EndpointName="churn-model-prod",
    ContentType="application/json",
    Body=json.dumps({"instances": [[0.2, 5, 1, 0]]}),
)
print(json.loads(resp["Body"].read()))
```
```bash
# Always delete idle endpoints: they bill per hour
aws sagemaker delete-endpoint --endpoint-name churn-model-prod
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Platform | SageMaker | Azure Machine Learning |
| Notebook | SageMaker Studio | AML Studio / notebooks |
| Hosting | Endpoints (real-time, serverless, async) | Managed online / batch endpoints |
| Pricing | Per instance-hour for notebooks, training, endpoints (approximate — check current docs) | Per compute-hour |

---

## ⚠️ Common Mistakes
❌ Mistake: Leaving a GPU endpoint or Studio app running.
✅ Correct: Delete or use serverless/async endpoints, set budgets.

❌ Mistake: Using SageMaker when a pre-built API (Bedrock, Rekognition) is enough.
✅ Correct: Use SageMaker only when you need a custom model.

---

## ⚫ Interview Q&A
Q1: [Easy] Training job vs endpoint?
A1: Training job is temporary and produces model artifacts; endpoint is a long-running hosted model.

Q2: [Medium] Real-time vs async vs batch?
A2: Real-time = low-latency; async = large payloads/queued; batch transform = offline over S3 dataset.

Q3: [Hard] How do you cut inference cost?
A3: Right-size instances, autoscale, serverless for spiky traffic, multi-model endpoints, Savings Plans, quantised models.

---

## ✅ Quick Checklist
□ Data and artifacts in S3 with encryption
□ Endpoint autoscaling configured
□ Idle resources deleted

---

## ⚡ 1-Line Summary
SageMaker trains and hosts custom ML models | SageMaker अपने custom ML model को train और host करता है।

## ➡️ Next: 168. Rekognition (Image AI)
