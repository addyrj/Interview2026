
---

# 549. AWS Lambda for AI (Light)
# हिंदी में: AI के लिए AWS Lambda (हल्के workloads)

---

## 🔵 Simple Definition (English)
AWS Lambda runs a function only when an event arrives (HTTP request, queue message, S3 upload) and bills per millisecond. "Light" AI means calling an external LLM API, doing classification routing, or small glue work, not hosting big models. Lambda has limits: 15 minutes max runtime, up to 10 GB memory, and cold starts.

## 🔵 सरल परिभाषा (Hindi)
AWS Lambda function तभी चलता है जब कोई event आए (HTTP request, queue message, S3 upload) और millisecond के हिसाब से bill होता है। "Light" AI का मतलब है बाहरी LLM API call करना, classification routing, छोटा glue काम, बड़े models host करना नहीं। Limits: अधिकतम 15 मिनट, 10 GB तक memory, और cold start।

---

## 🔴 Problem it Solves
Running a server 24x7 for a workload that gets 50 requests a day wastes money, and you still patch and monitor it. Event-driven jobs (summarise each uploaded PDF, classify each email) need to scale from 0 to 1000 instantly and back to 0.

## 🔴 यह क्यों बना? (Hindi)
दिन में 50 requests वाले काम के लिए 24x7 server चलाना पैसा बर्बाद है, और patching/monitoring भी करनी पड़ती है। Event-driven काम (हर uploaded PDF का summary, हर email की classification) को 0 से 1000 तक तुरंत scale होना और फिर 0 पर लौटना चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Package code (zip or container image up to 10 GB) and create the function
Step 2 → Attach a trigger: API Gateway / Function URL / SQS / S3
Step 3 → Event arrives; Lambda finds or starts an execution environment (cold start)
Step 4 → Code outside the handler runs once per environment (init: clients, config)
Step 5 → handler(event, context) runs for each invocation
Step 6 → Result returned; environment stays warm for a few minutes for reuse
Step 7 → Billed = requests + (GB-seconds of memory x duration)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Code package करो (zip या 10 GB तक container image), function बनाओ
Step 2 → Trigger जोड़ो: API Gateway / Function URL / SQS / S3
Step 3 → Event आता है; Lambda environment ढूँढता या शुरू करता है (cold start)
Step 4 → Handler के बाहर का code हर environment में एक बार चलता है (clients, config)
Step 5 → हर invocation पर handler(event, context) चलता है
Step 6 → Result लौटता है; environment कुछ मिनट warm रहता है
Step 7 → Bill = requests + (memory GB-seconds x duration)
```

---

## 🟡 Real World Example
**Tariff Classification System**: When a customs broker uploads an invoice to S3, a Lambda function extracts line items, calls an LLM to propose an HS code for each, and writes the result to DynamoDB. Traffic is bursty, so Lambda is cheaper than an always-on service. The slow part (LLM call) is I/O wait, which Lambda handles well as long as it finishes inside the timeout.

**Amazon-style**: Each product review posted triggers a Lambda that classifies sentiment with a small LLM call.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs broker जब S3 में invoice upload करता है, Lambda line items निकालता है, LLM से हर item का HS code propose करवाता है और DynamoDB में लिखता है। Traffic bursty है, इसलिए Lambda always-on service से सस्ता है।

**Amazon-style**: हर नए product review पर Lambda छोटे LLM call से sentiment classify करता है।

---

## 💻 Code Example — Basic
```python
# A Lambda handler that you can run locally with a fake event (no AWS needed)
import json  # parse and build JSON bodies
from typing import Any  # loose typing for event and context


def handler(event: dict[str, Any], context: Any = None) -> dict[str, Any]:
    """Classify a product text using a tiny rule (stand-in for an LLM call)."""
    try:
        body = json.loads(event.get("body") or "{}")  # API Gateway sends body as a string
        text: str = body["text"]  # required field
    except (json.JSONDecodeError, KeyError):  # bad input
        return {"statusCode": 400, "body": json.dumps({"error": "text is required"})}  # client error
    # Simple keyword rule so the example runs offline
    code = "8517.13" if "phone" in text.lower() else "9999.00"  # pick a code
    return {"statusCode": 200, "body": json.dumps({"hs_code": code})}  # success response


if __name__ == "__main__":  # local test
    fake = {"body": json.dumps({"text": "Smart phone 128GB"})}  # fake API Gateway event
    print(handler(fake))  # prints the response dict
```

## 💻 Code Example — Advanced
```python
# Production Lambda: reuse client across invocations, async LLM call, timeout awareness, partial SQS failures
import asyncio  # run async code inside the sync Lambda handler
import json  # parse SQS bodies
import os  # read config from env vars
from typing import Any  # loose typing

import httpx  # async HTTP client

# Created once per execution environment (outside handler) so warm invocations reuse it
MODEL: str = os.environ.get("LLM_MODEL", "gpt-4o-mini")  # model name from config
API_KEY: str = os.environ.get("OPENAI_API_KEY", "")  # in production load from Secrets Manager


async def classify(client: httpx.AsyncClient, text: str) -> str:
    """Call an LLM API and return the answer text."""
    resp = await client.post(
        "https://api.openai.com/v1/chat/completions",  # OpenAI chat endpoint
        headers={"Authorization": f"Bearer {API_KEY}"},  # auth header
        json={
            "model": MODEL,  # model
            "messages": [{"role": "user", "content": f"HS code for: {text}"}],  # prompt
            "max_tokens": 50,  # cap output tokens
        },
        timeout=20.0,  # never exceed the function timeout
    )
    resp.raise_for_status()  # raise on 4xx/5xx
    return resp.json()["choices"][0]["message"]["content"]  # answer text


async def process(records: list[dict[str, Any]], remaining_ms: int) -> list[dict[str, str]]:
    """Process SQS records concurrently; return the failed ones."""
    failures: list[dict[str, str]] = []  # collects failed message ids
    async with httpx.AsyncClient() as client:  # one client for all records
        async def one(rec: dict[str, Any]) -> None:
            try:
                text = json.loads(rec["body"])["text"]  # message payload
                await asyncio.wait_for(classify(client, text), timeout=remaining_ms / 1000 - 2)  # leave 2s margin
            except Exception:  # any failure marks this record for retry
                failures.append({"itemIdentifier": rec["messageId"]})  # SQS partial batch response
        await asyncio.gather(*(one(r) for r in records))  # run concurrently
    return failures  # failed ids


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """SQS-triggered entry point."""
    failed = asyncio.run(process(event["Records"], context.get_remaining_time_in_millis()))  # run async work
    return {"batchItemFailures": failed}  # only failed messages are retried
```

---

## 🟠 FastAPI Integration
You can run a whole FastAPI app on Lambda using the **Mangum** adapter, which translates API Gateway events to ASGI. Good for low traffic APIs; streaming is limited, so prefer a Function URL with response streaming only where supported.

```python
# FastAPI on Lambda via Mangum
from fastapi import FastAPI  # web framework
from mangum import Mangum  # ASGI to Lambda adapter

app = FastAPI()  # the same app you run locally


@app.get("/health")  # simple route
async def health() -> dict[str, str]:
    return {"status": "ok"}  # response


handler = Mangum(app)  # Lambda entry point: handler = "main.handler"
```

---

## 🔗 LangChain / LangGraph Connection
LangChain works in Lambda, but the package is large, so use a container image or Lambda layers and import lazily to reduce cold start. A short LangGraph flow is fine; long agent loops should move to ECS or Step Functions because of the 15 minute limit and no persistent memory.

```python
# Build the chain at module level (once per environment)
from langchain_openai import ChatOpenAI  # LLM wrapper
from langchain_core.prompts import ChatPromptTemplate  # prompt

llm = ChatOpenAI(model="gpt-4o-mini", timeout=20, max_retries=1)  # short timeout for Lambda
chain = ChatPromptTemplate.from_template("HS code for {text}") | llm  # LCEL chain


def handler(event: dict, context: object) -> dict:
    out = chain.invoke({"text": event["text"]})  # sync call inside handler
    return {"answer": out.content}  # return text
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Creating the client inside the handler on every call
```python
# Wrong: a new connection and import cost every invocation
def handler(event, context):
    from openai import OpenAI
    client = OpenAI()
    return client.chat.completions.create(model="gpt-4o-mini", messages=[])
# Correct: create once outside the handler
from openai import OpenAI
client = OpenAI()
def handler(event, context):
    return client.chat.completions.create(model="gpt-4o-mini", messages=[])
```

❌ Mistake 2: Timeout equal to the LLM timeout, no retry safety
```python
# Wrong: function timeout 30s, LLM call can wait 60s, so Lambda is killed mid-call and the SQS message retries forever
# Correct: LLM client timeout (20s) < function timeout (30s) < SQS visibility timeout (>= 6x function timeout, AWS guidance)
# and send poison messages to a dead-letter queue
```

---

## 🧠 Tricky Interview Question
**Q**: "Your Lambda LLM function works but p99 latency spikes to 6 seconds a few times an hour. Why and what do you do?"

**Answer**: Cold starts: a new execution environment must download the package, start the runtime, and run init code (imports of LangChain, SDK clients). Fix: keep the package small, lazy-import heavy libs, increase memory (this also gives more CPU), use provisioned concurrency for the latency-critical path, or move to ECS if traffic is steady. Also check whether the LLM provider itself is slow; compare Lambda `Init Duration` in logs with the LLM call time.

---

## ⚫ Interview Questions + Answers

Q1: What is the maximum run time of a Lambda function?
A1: 15 minutes.

Q2: What is a cold start?
A2: The extra delay when Lambda creates a new execution environment, loads code, and runs init code before the first request.

Q3: Why is Lambda a poor fit for streaming LLM responses to end users?
A3: Classic API Gateway buffers responses; streaming requires Function URLs with response streaming and a supported runtime, and connection time still counts toward the timeout. Long chats are better on ECS.

Q4: How do you avoid reprocessing messages when only some SQS records fail?
A4: Enable `ReportBatchItemFailures` and return `batchItemFailures` with the failed message IDs, plus a dead-letter queue.

Q5: When does Lambda cost more than ECS for an LLM service?
A5: When the function waits a long time on the LLM (you pay for the whole duration at full memory price) at high steady volume. Compute: 1 GB x 10 s waiting per request across millions of requests exceeds a small always-on Fargate task that handles many concurrent requests via async.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Event-driven, bursty or low traffic
- Short tasks (< a few minutes) calling external LLM APIs
- You want zero idle cost

❌ Avoid when:
- Local model inference or GPUs are needed
- Long agent loops, websockets, heavy streaming
- Constant high traffic where an always-on service is cheaper

---

## 📊 Visual Diagram
```
 S3 upload / SQS / API Gateway
              │ event
              ▼
     ┌──────────────────┐   cold: init (imports, clients)
     │ Lambda environment│──▶ warm: handler only
     └────────┬─────────┘
              │ HTTPS
              ▼
        LLM API ──▶ result ──▶ DynamoDB / response
 Billing: requests + memory(GB) x seconds
```

---

## 💰 Cost Impact
Illustrative Lambda pricing (verify current): about $0.20 per 1M requests plus about $0.0000166667 per GB-second. A 1 GB function that waits 3 s on an LLM costs about $0.00005 per call, roughly $50 per million calls, plus tokens. Tokens are separate: 600 input and 100 output tokens on gpt-4o-mini (illustrative $0.15/$0.60 per 1M) is about $0.00015 per call. So the LLM tokens often cost more than Lambda itself. Optimise: lower memory if CPU is idle (but test, since memory also sets CPU), cap `max_tokens`, cache repeated inputs in DynamoDB, batch SQS records and call concurrently, and set reserved concurrency so a flood cannot create an unlimited LLM bill.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lambda | Event-driven serverless function | Event पर चलने वाला function |
| Cold start | Delay creating new environment | नया environment बनने की देरी |
| Provisioned concurrency | Pre-warmed environments | पहले से गरम रखे environments |
| Mangum | ASGI adapter for Lambda | FastAPI को Lambda पर चलाने वाला |
| DLQ | Dead-letter queue for failed messages | असफल messages की queue |
| Reserved concurrency | Max parallel executions cap | Parallel runs की सीमा |

---

## ⚡ 3-Line Summary
English: Lambda is pay-per-use serverless compute, great for bursty, short LLM glue tasks. Create clients outside the handler, keep timeouts nested correctly, and watch cold starts. Use ECS for streaming, long agents, or steady high traffic.
Hindi: Lambda pay-per-use serverless compute है, bursty और छोटे LLM glue कामों के लिए बढ़िया। Clients handler के बाहर बनाओ, timeouts सही क्रम में रखो, cold start पर नज़र रखो। Streaming, लंबे agents या steady high traffic के लिए ECS इस्तेमाल करो।

---

## ➡️ Next Topic
**550. AWS Bedrock Basics** — managed access to foundation models on AWS, so you do not call external LLM APIs at all.
