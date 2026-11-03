
---

# 551. AWS SageMaker Basics
# हिंदी में: AWS SageMaker की बुनियादी बातें

---

## 🔵 Simple Definition (English)
Amazon SageMaker is AWS's platform to build, train and host machine learning models. For AI apps the key feature is a **real-time endpoint**: a managed HTTPS service running your model (open-source LLM, embedding model, classifier) on instances you choose, including GPUs. You call it with `sagemaker-runtime` `invoke_endpoint`.

## 🔵 सरल परिभाषा (Hindi)
Amazon SageMaker AWS का platform है ML models बनाने, train करने और host करने के लिए। AI apps के लिए मुख्य feature **real-time endpoint** है: एक managed HTTPS service जो आपका model (open-source LLM, embedding model, classifier) आपके चुने instances (GPU सहित) पर चलाती है। आप `sagemaker-runtime` के `invoke_endpoint` से call करते हैं।

---

## 🔴 Problem it Solves
Hosting your own model means provisioning GPUs, installing drivers, packaging inference servers, scaling and monitoring. Fine-tuned or custom models are often not available on Bedrock or API providers. SageMaker packages the serving stack, autoscaling, and model registry.

## 🔴 यह क्यों बना? (Hindi)
अपना model host करने का मतलब GPUs लेना, drivers install करना, inference server package करना, scaling और monitoring करना। Fine-tuned या custom models अक्सर Bedrock या API providers पर नहीं मिलते। SageMaker serving stack, autoscaling और model registry package करके देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Store model artifacts (weights) in S3, or pick a prebuilt container / JumpStart model
Step 2 → Create a Model (container image + S3 artifact + IAM role)
Step 3 → Create an Endpoint Config (instance type, count, variants)
Step 4 → Create the Endpoint; SageMaker launches instances and the container
Step 5 → App calls invoke_endpoint with a JSON payload
Step 6 → Autoscaling adjusts instance count by invocations per instance
Step 7 → Update by creating a new config; traffic shifts (blue/green)
Step 8 → Delete endpoints you do not use, because they bill while running
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Model weights S3 में रखो, या prebuilt container / JumpStart model चुनो
Step 2 → Model बनाओ (container image + S3 artifact + IAM role)
Step 3 → Endpoint Config बनाओ (instance type, count, variants)
Step 4 → Endpoint बनाओ; SageMaker instances और container चालू करता है
Step 5 → App JSON payload के साथ invoke_endpoint call करती है
Step 6 → Autoscaling invocations per instance से instance count बदलती है
Step 7 → नई config बनाकर update करो; traffic blue/green शिफ्ट होता है
Step 8 → बिना इस्तेमाल वाले endpoints delete करो, चलते समय bill होता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: The team fine-tuned a small open model on 200K labelled HS code descriptions. It beats a general LLM on accuracy and is cheaper per call at high volume. It is deployed to a SageMaker endpoint on a GPU instance; the FastAPI `tariff-api` calls it, and falls back to a hosted LLM if the endpoint is unhealthy.

**Amazon-style**: Product-embedding model served on SageMaker to power semantic search.

## 🟡 Real Example Hindi mein
**Tariff System**: Team ने 200K labelled HS code descriptions पर छोटा open model fine-tune किया। यह general LLM से ज़्यादा accurate और high volume पर सस्ता है। इसे GPU instance वाले SageMaker endpoint पर deploy किया; FastAPI `tariff-api` इसे call करती है और endpoint unhealthy हो तो hosted LLM पर fallback करती है।

**Amazon-style**: Semantic search के लिए product-embedding model SageMaker पर serve होता है।

---

## 💻 Code Example — Basic
```python
# Build the request payload and parse a response offline; the real call is shown in a comment
import json  # JSON encoding


def build_payload(text: str, max_new_tokens: int = 64) -> bytes:
    """Create the JSON body many Hugging Face containers expect."""
    body = {"inputs": text, "parameters": {"max_new_tokens": max_new_tokens, "temperature": 0.1}}  # request
    return json.dumps(body).encode("utf-8")  # endpoint expects bytes


def parse_response(raw: bytes) -> str:
    """Parse a text-generation response."""
    data = json.loads(raw)  # bytes to Python object
    return data[0]["generated_text"]  # first generated text


if __name__ == "__main__":
    payload = build_payload("HS code for smartphone:")  # create the payload
    print(payload)  # show it
    fake = json.dumps([{"generated_text": "8517.13"}]).encode()  # pretend endpoint reply
    print(parse_response(fake))  # prints 8517.13
    # Real call (needs AWS):
    # import boto3
    # rt = boto3.client("sagemaker-runtime")
    # r = rt.invoke_endpoint(EndpointName="tariff-llm", ContentType="application/json", Body=payload)
    # print(parse_response(r["Body"].read()))
```

## 💻 Code Example — Advanced
```python
# Production client: timeouts, retries, fallback, async wrapper
import asyncio  # async wrapper
import json  # JSON
import logging  # logging
from typing import Awaitable, Callable  # type hints

import boto3  # AWS SDK
from botocore.config import Config  # timeouts and retries
from botocore.exceptions import BotoCoreError, ClientError  # AWS errors

log = logging.getLogger("sagemaker")  # logger


class SageMakerClient:
    """Calls a real-time endpoint with a fallback function."""

    def __init__(self, endpoint: str, fallback: Callable[[str], Awaitable[str]] | None = None) -> None:
        self.endpoint = endpoint  # endpoint name
        self.fallback = fallback  # used if endpoint fails
        cfg = Config(read_timeout=30, retries={"max_attempts": 2, "mode": "standard"})  # sane limits
        self.rt = boto3.client("sagemaker-runtime", config=cfg)  # runtime client

    def _invoke(self, text: str) -> str:
        """Blocking call to the endpoint."""
        resp = self.rt.invoke_endpoint(
            EndpointName=self.endpoint,  # which endpoint
            ContentType="application/json",  # body type
            Body=json.dumps({"inputs": text, "parameters": {"max_new_tokens": 64}}),  # payload
        )
        return json.loads(resp["Body"].read())[0]["generated_text"]  # parsed answer

    async def predict(self, text: str) -> str:
        """Async predict with fallback."""
        try:
            return await asyncio.to_thread(self._invoke, text)  # do not block the loop
        except (ClientError, BotoCoreError) as exc:  # endpoint down or throttled
            log.warning("endpoint failed: %s", exc)  # record it
            if self.fallback is None:  # no fallback configured
                raise  # propagate
            return await self.fallback(text)  # use the hosted LLM instead
```

---

## 🟠 FastAPI Integration
```python
# FastAPI route using the SageMaker client
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # request model

app = FastAPI()  # app


async def hosted_llm(text: str) -> str:  # fallback stub
    return "9999.00"  # replace with a real LLM call


sm = SageMakerClient("tariff-llm", fallback=hosted_llm)  # client


class Item(BaseModel):  # body
    description: str  # product text


@app.post("/classify")  # route
async def classify(item: Item) -> dict[str, str]:
    code = await sm.predict(f"HS code for: {item.description}")  # call endpoint
    return {"hs_code": code}  # response
```

---

## 🔗 LangChain / LangGraph Connection
`langchain-aws` provides `SagemakerEndpoint` (an LLM wrapper) which needs a content handler class to map prompts to the container's JSON format. Newer code often wraps SageMaker in a custom runnable. In LangGraph, treat the endpoint as a node and add a conditional edge to the fallback model.

```python
# Wrap the client as a LangChain runnable
from langchain_core.runnables import RunnableLambda  # runnable wrapper

sm_chain = RunnableLambda(lambda text: sm._invoke(f"HS code for: {text}"))  # sync runnable
print(sm_chain.invoke("laptop"))  # call the endpoint through LangChain
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Leaving endpoints running
```python
# Wrong: a GPU endpoint left on over the weekend still bills hourly
# Correct: delete it, or use serverless / asynchronous endpoints (scale to zero) for rare traffic
sm = boto3.client("sagemaker")
sm.delete_endpoint(EndpointName="tariff-llm-dev")
```

❌ Mistake 2: Using an undersized instance for an LLM
```python
# Wrong: model does not fit in GPU memory, container crashes on load
instance_type = "ml.t3.medium"
# Correct: size by parameters x bytes (7B in fp16 is about 14 GB) plus KV cache headroom
instance_type = "ml.g5.2xlarge"  # example GPU instance; verify fit
```

---

## 🧠 Tricky Interview Question
**Q**: "SageMaker endpoint is healthy but 20% of requests time out under load. Instances look idle. Why?"

**Answer**: Real-time endpoints have a 60 second invocation limit and the container may have too few worker processes, so requests queue inside the container while GPU/CPU metrics look average. Also a long generation (`max_new_tokens` large) holds the worker. Fix: use the latency and `InvocationsPerInstance` metrics for autoscaling, enable response streaming or async inference for long outputs, tune container concurrency (e.g. continuous batching in the serving framework), and cap output tokens.

---

## ⚫ Interview Questions + Answers

Q1: What is a SageMaker endpoint?
A1: A managed, always-on HTTPS service that serves a model on chosen instances.

Q2: Name the endpoint types.
A2: Real-time, serverless (scale to zero, no GPU), asynchronous (queue plus S3 output for large or slow jobs), and batch transform for offline bulk scoring.

Q3: When choose SageMaker over Bedrock?
A3: When you need your own fine-tuned or open model, special hardware, custom containers, or full control of the serving stack.

Q4: How do you scale a SageMaker endpoint?
A4: Application Auto Scaling target-tracking on `SageMakerVariantInvocationsPerInstance`, with min and max instance counts and cooldowns.

Q5: How do you roll out a new model version safely?
A5: Create a new endpoint config and update the endpoint with a blue/green deployment policy, canary traffic shifting, CloudWatch alarms and automatic rollback.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You host custom or fine-tuned models
- You need GPUs, VPC isolation, MLOps tooling
- Volume is high enough to beat per-token API prices

❌ Avoid when:
- A managed API (Bedrock, OpenAI) meets accuracy needs
- Traffic is low and endpoints would idle
- You lack MLOps skills to run it

---

## 📊 Visual Diagram
```
 S3 (weights) ──┐
 ECR container ─┼─▶ SageMaker Model ─▶ Endpoint Config ─▶ Endpoint
 IAM role ──────┘                                         │
                                         ┌────────────────┴──┐
 FastAPI ── invoke_endpoint ───────────▶ │ ml.g5 instance(s) │
     ▲                                   └───────────────────┘
     └── fallback to hosted LLM if error   autoscale on invocations
```

---

## 💰 Cost Impact
Endpoints bill per instance-hour while running, regardless of traffic. Illustrative: a single GPU instance such as `ml.g5.xlarge` is on the order of a dollar or more per hour, i.e. roughly $800 or more per month always on (check current pricing). Token usage is free of per-token fees, so it only wins when volume is high: compute break-even as monthly instance cost divided by your API cost per request. Optimise: quantised models, smaller models, serverless or async endpoints for bursty traffic, autoscaling with a minimum of 1, scheduled shutdown of dev endpoints, Savings Plans for steady use, and multi-model endpoints to share one instance.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SageMaker | AWS ML platform | AWS का ML platform |
| Endpoint | Hosted model HTTPS service | Hosted model की service |
| Endpoint config | Instance and variant settings | Instance settings |
| Async inference | Queue-based long jobs | Queue वाला inference |
| JumpStart | Catalog of prebuilt models | तैयार models की list |
| Multi-model endpoint | Many models on shared instances | एक instance पर कई models |

---

## ⚡ 3-Line Summary
English: SageMaker hosts your own models on managed endpoints with autoscaling and GPUs. It beats APIs only for custom models or high volume, because endpoints bill by the hour. Always add a fallback, timeouts, and delete idle endpoints.
Hindi: SageMaker आपके अपने models managed endpoints पर host करता है, autoscaling और GPUs के साथ। यह APIs से तभी बेहतर है जब custom model या high volume हो, क्योंकि endpoints घंटे के हिसाब से bill होते हैं। Fallback, timeouts रखो और idle endpoints delete करो।

---

## ➡️ Next Topic
**552. Deploy on Railway (Easy)** — the fastest path to put a FastAPI AI app online without AWS complexity.
