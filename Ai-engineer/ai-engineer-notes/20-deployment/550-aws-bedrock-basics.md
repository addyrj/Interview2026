
---

# 550. AWS Bedrock Basics
# हिंदी में: AWS Bedrock की बुनियादी बातें

---

## 🔵 Simple Definition (English)
Amazon Bedrock is a managed AWS service that gives API access to foundation models (Anthropic Claude, Amazon Nova, Meta Llama, Mistral and others) without you hosting anything. You call it with boto3 (`bedrock-runtime`), pay per token, and your data stays inside AWS with IAM control. Model availability differs per region.

## 🔵 सरल परिभाषा (Hindi)
Amazon Bedrock एक managed AWS service है जो foundation models (Anthropic Claude, Amazon Nova, Meta Llama, Mistral आदि) की API देती है, खुद host नहीं करना पड़ता। आप boto3 (`bedrock-runtime`) से call करते हैं, per token pay करते हैं, और data IAM control के साथ AWS के अंदर रहता है। Model availability region के हिसाब से बदलती है।

---

## 🔴 Problem it Solves
Sending company data to many third-party LLM endpoints creates security reviews, separate bills, and separate keys. Hosting open models needs GPUs and MLOps. Bedrock gives one AWS API, IAM permissions, VPC endpoints, CloudWatch metrics, guardrails, and a single invoice.

## 🔴 यह क्यों बना? (Hindi)
कई third-party LLM endpoints को company data भेजने से security reviews, अलग bills और अलग keys की झंझट होती है। Open models host करने के लिए GPUs और MLOps चाहिए। Bedrock एक AWS API, IAM permissions, VPC endpoints, CloudWatch metrics, guardrails और एक invoice देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → In the console, request access to the models you need (per region)
Step 2 → Give your ECS task / Lambda role bedrock:InvokeModel permission (IAM)
Step 3 → Create boto3 client: boto3.client("bedrock-runtime", region_name=...)
Step 4 → Call converse() (unified chat API) or invoke_model() (model-specific body)
Step 5 → Bedrock routes to the model, returns text plus usage (input/output tokens)
Step 6 → For streaming use converse_stream()
Step 7 → Optional: Guardrails, Knowledge Bases (managed RAG), Agents, Batch inference
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Console में ज़रूरी models का access request करो (region के अनुसार)
Step 2 → ECS task / Lambda role को bedrock:InvokeModel permission दो (IAM)
Step 3 → boto3 client बनाओ: boto3.client("bedrock-runtime", region_name=...)
Step 4 → converse() (unified chat API) या invoke_model() (model-specific body) call करो
Step 5 → Bedrock model तक route करता है, text और usage (tokens) लौटाता है
Step 6 → Streaming के लिए converse_stream()
Step 7 → Optional: Guardrails, Knowledge Bases (managed RAG), Agents, Batch inference
```

---

## 🟡 Real World Example
**Tariff Classification System**: A bank-grade customer will not allow tariff documents to leave AWS. The `tariff-api` on ECS calls Claude on Bedrock through a VPC endpoint, using the task IAM role instead of an API key. Guardrails mask personal data in invoices.

**Zomato-style**: A restaurant-review summariser uses a cheap model on Bedrock for bulk jobs through Batch inference.

## 🟡 Real Example Hindi mein
**Tariff System**: Bank-grade customer अपने tariff documents AWS से बाहर नहीं जाने देगा। ECS पर `tariff-api` Claude को Bedrock से VPC endpoint के ज़रिए call करती है, API key की जगह task IAM role से। Guardrails invoices में personal data mask करते हैं।

**Zomato-style**: Restaurant-review summariser bulk jobs के लिए Bedrock पर सस्ता model और Batch inference इस्तेमाल करता है।

---

## 💻 Code Example — Basic
```python
# Basic Bedrock Converse call (needs AWS credentials and model access; model id is an example)
import boto3  # AWS SDK

client = boto3.client("bedrock-runtime", region_name="us-east-1")  # runtime client

MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"  # example id; check the console for current ids

response = client.converse(  # unified chat API that works across models
    modelId=MODEL_ID,  # which model to use
    messages=[  # conversation messages
        {"role": "user", "content": [{"text": "HS code for a smartphone? Answer in one line."}]}
    ],
    inferenceConfig={"maxTokens": 100, "temperature": 0.0},  # limit output, deterministic
)

print(response["output"]["message"]["content"][0]["text"])  # the answer text
print(response["usage"])  # inputTokens, outputTokens, totalTokens
```

## 💻 Code Example — Advanced
```python
# Production wrapper: retries, error handling, token logging, async via thread
import asyncio  # async wrapper
import logging  # logging usage
from typing import Any  # loose typing

import boto3  # AWS SDK
from botocore.config import Config  # client retry configuration
from botocore.exceptions import ClientError  # AWS errors

log = logging.getLogger("bedrock")  # logger


class BedrockLLM:
    """Small wrapper around the Converse API."""

    def __init__(self, model_id: str, region: str = "us-east-1") -> None:
        self.model_id = model_id  # model to call
        cfg = Config(
            retries={"max_attempts": 3, "mode": "adaptive"},  # backoff on throttling
            read_timeout=60,  # seconds to wait for a response
        )
        self.client = boto3.client("bedrock-runtime", region_name=region, config=cfg)  # configured client

    def ask(self, system: str, user: str, max_tokens: int = 300) -> dict[str, Any]:
        """Return answer text and token usage."""
        try:
            resp = self.client.converse(
                modelId=self.model_id,  # model
                system=[{"text": system}],  # system prompt
                messages=[{"role": "user", "content": [{"text": user}]}],  # user message
                inferenceConfig={"maxTokens": max_tokens, "temperature": 0.0},  # bounded output
            )
        except ClientError as exc:
            code = exc.response["Error"]["Code"]  # e.g. ThrottlingException
            log.error("bedrock error %s", code)  # log it
            if code == "ThrottlingException":  # too many requests
                raise RuntimeError("Bedrock throttled; retry later") from exc  # caller can back off
            if code == "AccessDeniedException":  # IAM or model access missing
                raise PermissionError("No access to model or IAM permission") from exc  # clear message
            raise  # unknown error
        usage = resp["usage"]  # token counts
        log.info("tokens in=%s out=%s", usage["inputTokens"], usage["outputTokens"])  # cost tracking
        return {"text": resp["output"]["message"]["content"][0]["text"], "usage": usage}  # result

    async def ask_async(self, system: str, user: str, max_tokens: int = 300) -> dict[str, Any]:
        """Async wrapper (boto3 is blocking)."""
        return await asyncio.to_thread(self.ask, system, user, max_tokens)  # offload to thread
```

---

## 🟠 FastAPI Integration
```python
# FastAPI route that calls Bedrock
from fastapi import FastAPI, HTTPException  # web framework and errors
from pydantic import BaseModel  # request model

app = FastAPI()  # app
llm = BedrockLLM("anthropic.claude-3-haiku-20240307-v1:0")  # wrapper from the advanced example


class Req(BaseModel):  # request body
    description: str  # product description


@app.post("/classify")  # route
async def classify(req: Req) -> dict:
    try:
        out = await llm.ask_async("You are a tariff assistant. Be brief.", req.description, 120)  # call
    except PermissionError as exc:
        raise HTTPException(status_code=500, detail=str(exc))  # config problem
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))  # throttled, retry
    return {"answer": out["text"], "tokens": out["usage"]}  # include token usage
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has `ChatBedrockConverse` in the `langchain-aws` package. Swap it for `ChatOpenAI` and the rest of your chain or LangGraph graph stays the same.

```python
# LangChain with Bedrock
from langchain_aws import ChatBedrockConverse  # Bedrock chat model

llm = ChatBedrockConverse(  # create model
    model="anthropic.claude-3-haiku-20240307-v1:0",  # example model id
    region_name="us-east-1",  # region
    temperature=0,  # deterministic
)
print(llm.invoke("HS code for a laptop?").content)  # call and print
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting model access or using the wrong region
```python
# Wrong: model not enabled in this region, AccessDeniedException / ValidationException
client = boto3.client("bedrock-runtime", region_name="ap-south-1")
# Correct: enable the model in the console and use a region where it exists (or use a cross-region inference profile)
client = boto3.client("bedrock-runtime", region_name="us-east-1")
```

❌ Mistake 2: Using `bedrock` instead of `bedrock-runtime` client
```python
# Wrong: "bedrock" is the control plane (list models), it has no converse()
client = boto3.client("bedrock")
# Correct: inference uses bedrock-runtime
client = boto3.client("bedrock-runtime")
```

---

## 🧠 Tricky Interview Question
**Q**: "Locally your Bedrock code works, but in ECS it returns AccessDeniedException. Same code, same model. Why?"

**Answer**: Locally you used your own admin credentials; in ECS the **task role** (not the execution role) is used. The task role lacks `bedrock:InvokeModel` (or `InvokeModelWithResponseStream`) on that model ARN, or the model access was never enabled in that account and region. Also check any service control policies and VPC endpoint policies. Fix: grant least-privilege permission on the specific model ARN to the task role.

---

## ⚫ Interview Questions + Answers

Q1: What is Amazon Bedrock?
A1: A managed service giving API access to multiple foundation models, with IAM security, guardrails and no infrastructure to manage.

Q2: What is the difference between `bedrock` and `bedrock-runtime` clients?
A2: `bedrock` is for management (list models, customization jobs); `bedrock-runtime` is for inference (`converse`, `invoke_model`).

Q3: Why use `converse` instead of `invoke_model`?
A3: `converse` has one request/response shape across models, so switching models is a config change; `invoke_model` needs each model's own body format.

Q4: What are Bedrock Guardrails?
A4: Configurable filters for denied topics, harmful content, PII masking and grounding checks applied to inputs and outputs.

Q5: Compare Bedrock with calling the provider API directly for a regulated customer.
A5: Bedrock keeps traffic in AWS (VPC endpoints/PrivateLink), uses IAM instead of shared keys, gives CloudTrail audit, and consolidates billing. Direct APIs may release new features earlier and sometimes cost differently. For regulated data, Bedrock usually wins; for newest features, direct may.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You are already on AWS and need IAM, audit, private networking
- You want to swap between several models easily
- You want managed RAG or guardrails

❌ Avoid when:
- You need a model or beta feature not offered on Bedrock
- You need to host your own fine-tuned custom architecture (consider SageMaker)

---

## 📊 Visual Diagram
```
 ECS task (role: bedrock:InvokeModel)
        │ boto3 bedrock-runtime
        ▼
 ┌────────────────────────────┐
 │ VPC endpoint (PrivateLink) │
 └─────────────┬──────────────┘
               ▼
 ┌─────────────────────────────┐
 │ Bedrock: Guardrails ▶ Model │──▶ answer + usage tokens
 └─────────────────────────────┘
 CloudTrail / CloudWatch record every call
```

---

## 💰 Cost Impact
On-demand Bedrock bills per 1K or 1M input and output tokens, with prices that differ per model (illustrative: a small model might be around $0.25 input and $1.25 output per 1M tokens, a large one about $3 and $15; check the pricing page). A tariff call with 700 input and 150 output tokens on a small model is roughly $0.00036. Optimise: pick the smallest model that passes your evals, cap `maxTokens`, use prompt caching where the model supports it, use Batch inference (discounted, asynchronous) for bulk jobs, cache repeated answers, and use Provisioned Throughput only for steady high volume.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bedrock | AWS managed foundation model service | AWS की managed model service |
| Converse API | Unified chat API across models | सभी models के लिए एक chat API |
| Model access | Per-account permission to use a model | Model इस्तेमाल की अनुमति |
| Guardrails | Safety and PII filters | Safety और PII filters |
| Knowledge Base | Managed RAG on Bedrock | Managed RAG |
| Inference profile | Cross-region routing alias | Cross-region routing नाम |

---

## ⚡ 3-Line Summary
English: Bedrock is AWS's managed API for many foundation models with IAM, guardrails and private networking. Use `bedrock-runtime` and `converse`, and give the task role the right permission. Cost is per token, so choose small models and cap output.
Hindi: Bedrock AWS की managed API है कई foundation models के लिए, IAM, guardrails और private networking के साथ। `bedrock-runtime` और `converse` इस्तेमाल करो और task role को सही permission दो। Cost per token है, इसलिए छोटे models चुनो और output सीमित रखो।

---

## ➡️ Next Topic
**551. AWS SageMaker Basics** — hosting your own or fine-tuned models on managed endpoints when Bedrock is not enough.
