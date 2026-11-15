# 166. Bedrock — Managed LLMs
# AWS: Amazon Bedrock
# Azure: Azure OpenAI Service / Azure AI Foundry
# हिंदी में: API से managed LLM models इस्तेमाल करना

---

## 🔵 Simple Definition
Bedrock gives API access to foundation models (Anthropic Claude, Amazon Nova/Titan, Meta Llama, etc.) with no servers, inside your AWS account and IAM.
हिंदी: Bedrock में बिना server चलाए IAM के साथ LLM models का API मिलता है।

---

## 🔴 Why it Exists
Hosting LLMs needs GPUs and ops; sending data to third-party APIs raises compliance questions.
Bedrock keeps traffic in AWS, bills per token and adds Guardrails, Knowledge Bases (RAG) and Agents.

---

## 🟢 How it Works
```
App (Node/FastAPI) -> bedrock-runtime Converse API (modelId, messages)
   IAM role: bedrock:InvokeModel
   -> model response / streaming (ConverseStream)
Optional: Guardrails filter in/out, Knowledge Base = vector store + retrieval
Note: model access must be enabled/available per region and model
```

---

## 💻 Code / Config Example
```python
# pip install boto3  (use a model id available to your account/region)
import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

resp = client.converse(
    modelId="anthropic.claude-3-haiku-20240307-v1:0",  # example id; check console for current ids
    messages=[{"role": "user", "content": [{"text": "Explain ECS in one line"}]}],
    inferenceConfig={"maxTokens": 200, "temperature": 0.2},
)
print(resp["output"]["message"]["content"][0]["text"])
print(resp["usage"])  # inputTokens / outputTokens -> cost tracking
```
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
    "Resource": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
  }]
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Bedrock | Azure OpenAI / AI Foundry |
| Models | Multi-vendor (Anthropic, Meta, Amazon, etc.) | Mainly OpenAI plus catalog models |
| RAG | Knowledge Bases | Azure AI Search "on your data" |
| Pricing | Per input/output token, or provisioned throughput (approximate — check current docs) | Per token or provisioned throughput units |

---

## ⚠️ Common Mistakes
❌ Mistake: Calling a model without access or in the wrong region (AccessDenied / ValidationException).
✅ Correct: Verify the model is available in your region and the IAM policy ARN matches.

❌ Mistake: No `maxTokens`, no usage logging.
✅ Correct: Cap tokens, log `usage`, set budgets and alarms.

---

## ⚫ Interview Q&A
Q1: [Easy] What is Bedrock?
A1: Serverless API for foundation models with IAM, VPC endpoints and pay-per-token.

Q2: [Medium] Converse vs InvokeModel?
A2: Converse is a uniform message API across models; InvokeModel takes the model-specific request body.

Q3: [Hard] How would you build a private RAG chatbot?
A3: Documents in S3 -> Knowledge Base (embeddings into a vector store) -> RetrieveAndGenerate or own retrieval + Converse, Guardrails for PII, VPC endpoint, IAM least privilege, logging to CloudWatch.

---

## ✅ Quick Checklist
□ Model available in region
□ IAM scoped to model ARN
□ Token limits and cost alarms

---

## ⚡ 1-Line Summary
Bedrock is pay-per-token LLM API inside AWS | Bedrock AWS के अंदर token के हिसाब से चलने वाला LLM API है।

## ➡️ Next: 167. SageMaker Basics
