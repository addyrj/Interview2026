---

# 444. Deploy on AWS Lambda
# हिंदी में: AWS Lambda पर Deploy करना

---

## 🔵 Simple Definition (English)
AWS Lambda runs your function only when an event arrives (an HTTP request, a queue message, a schedule). You upload code, AWS handles servers, scaling and patching, and you pay per request and per millisecond of run time. Idle time costs nothing.

## 🔵 सरल परिभाषा (Hindi)
AWS Lambda आपका function तभी चलाता है जब कोई event आता है (HTTP request, queue message, schedule)। आप code upload करते हैं, servers, scaling और patching AWS संभालता है, और भुगतान हर request और चलने के हर millisecond के हिसाब से होता है। खाली समय का कोई खर्च नहीं।

---

## 🔴 Problem it Solves
A normal server runs 24 hours even if it gets 10 requests a day, and when traffic spikes 100x you must scale it yourself. Lambda removes server management: it creates as many copies of your function as needed (up to your concurrency limit) and scales to zero when idle. Great for webhooks, scheduled jobs, file processing and spiky APIs.

## 🔴 यह क्यों बना? (Hindi)
सामान्य server दिन में 10 requests आने पर भी 24 घंटे चलता है, और traffic 100 गुना बढ़े तो आपको खुद scale करना पड़ता है। Lambda server management हटा देता है: जितनी ज़रूरत हो उतनी copies बनाता है (concurrency limit तक) और खाली होने पर शून्य तक घट जाता है। Webhooks, scheduled jobs, file processing और spiky APIs के लिए बढ़िया।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write handler(event, context) in Python (runtime python3.13)
Step 2 → Package: zip (code + dependencies) or a container image up to 10 GB
Step 3 → Configure: memory (128 MB-10 GB, CPU scales with it), timeout (max 15 min), IAM role
Step 4 → Trigger: API Gateway / Function URL (HTTP), SQS, S3 event, EventBridge schedule
Step 5 → COLD START: AWS creates an environment, loads runtime, runs your module-level code
Step 6 → INVOKE: AWS calls handler(event, context); you return a result
Step 7 → WARM: the environment is reused for later requests (module globals survive)
Step 8 → Idle for a while -> environment is frozen/destroyed; logs go to CloudWatch
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python में handler(event, context) लिखो (runtime python3.13)
Step 2 → Package: zip (code + dependencies) या container image (10 GB तक)
Step 3 → Configure: memory (128 MB-10 GB, CPU उसी के साथ बढ़ता है), timeout (max 15 मिनट), IAM role
Step 4 → Trigger: API Gateway / Function URL (HTTP), SQS, S3 event, EventBridge schedule
Step 5 → COLD START: AWS environment बनाता है, runtime load करता है, आपका module-level code चलाता है
Step 6 → INVOKE: AWS handler(event, context) call करता है; आप result लौटाते हैं
Step 7 → WARM: environment बाद की requests के लिए reuse होता है (module globals बचे रहते हैं)
Step 8 → कुछ देर खाली रहे तो environment freeze/नष्ट होता है; logs CloudWatch में जाते हैं
```

---

## 🟡 Real World Example
A payment gateway webhook from Razorpay hits `POST /webhook`. A Lambda behind API Gateway verifies the signature, writes the event into SQS and returns 200 in under 100 ms. A second Lambda, triggered by SQS, processes each payment with retries and a dead-letter queue. On a quiet night cost is near zero; on a flash-sale day AWS runs hundreds of copies in parallel without any change.

## 🟡 Real Example Hindi mein
Razorpay का payment webhook `POST /webhook` पर आता है। API Gateway के पीछे एक Lambda signature जाँचता है, event को SQS में डालता है और 100 ms से कम में 200 लौटाता है। SQS से चलने वाला दूसरा Lambda हर payment को retries और dead-letter queue के साथ process करता है। शांत रात में खर्च लगभग शून्य; flash-sale के दिन AWS बिना किसी बदलाव के सैकड़ों copies समानांतर चलाता है।

---

## 💻 Code Example — Basic
A plain Lambda handler for an API Gateway HTTP API (payload format v2). It was run locally by calling the function with a hand-written event, exactly what Lambda does. Not deployed to AWS (no account here):

```python
# Basic: a plain Lambda handler behind API Gateway (HTTP API, payload v2)
import json                                       # build/parse bodies
from typing import Any                            # loose dict types


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda calls this function once per invocation."""
    method: str = event["requestContext"]["http"]["method"]   # GET / POST
    path: str = event["rawPath"]                  # /hello
    if method == "GET" and path == "/hello":
        name: str = (event.get("queryStringParameters") or {}).get("name", "world")
        body = {"message": f"Hello {name}"}       # success payload
        return {"statusCode": 200,                # API Gateway needs this exact shape
                "headers": {"content-type": "application/json"},
                "body": json.dumps(body)}         # body must be a STRING
    return {"statusCode": 404, "body": json.dumps({"error": "not found"})}


class FakeContext:                                # what Lambda passes as context
    aws_request_id = "req-1"                      # unique per call
    def get_remaining_time_in_millis(self) -> int:
        return 29000                              # ms left before timeout


event = {"requestContext": {"http": {"method": "GET"}}, "rawPath": "/hello",
         "queryStringParameters": {"name": "Asha"}}     # trimmed sample event
print(handler(event, FakeContext()))              # local test = just call the function
print(handler({**event, "rawPath": "/x"}, FakeContext())["statusCode"])   # 404

# Output (real run, Python 3.13):
# {'statusCode': 200, 'headers': {'content-type': 'application/json'}, 'body': '{"message": "Hello Asha"}'}
# 404
```

Deploying the zip (**not run**):

```bash
# build a zip with dependencies for Lambda's Linux (use --platform for native wheels)
pip install -r requirements.txt --target package/ --platform manylinux2014_x86_64 --only-binary=:all:
cp handler.py package/ && (cd package && zip -r ../function.zip .)
aws lambda create-function --function-name orders-fn --runtime python3.13 \
  --handler handler.handler --zip-file fileb://function.zip \
  --role arn:aws:iam::123456789012:role/orders-lambda-role --timeout 15 --memory-size 512
```

## 💻 Code Example — Advanced
An SQS-triggered Lambda with **partial batch failure** (only failed messages are retried), idempotency against duplicates and module-level state reused across warm invocations. Ran locally by calling the handler twice:

```python
# Advanced: SQS-triggered Lambda with partial batch failure + idempotency + init reuse
import json                                       # parse SQS bodies
import time                                       # measure cold init
from typing import Any

_START = time.perf_counter()                      # code OUTSIDE handler runs once per cold start
SEEN: set[str] = set()                            # survives between warm invocations (same container)
INIT_MS: float = (time.perf_counter() - _START) * 1000   # init cost (tiny here)


def process(order: dict[str, Any]) -> None:
    if order["amount"] <= 0:                      # business validation
        raise ValueError("bad amount")


def handler(event: dict[str, Any], context: Any) -> dict[str, list[dict[str, str]]]:
    failures: list[dict[str, str]] = []           # message ids to retry
    for record in event["Records"]:               # SQS sends up to 10 per batch
        msg_id: str = record["messageId"]
        try:
            if msg_id in SEEN:                    # SQS is at-least-once: skip duplicates
                continue
            process(json.loads(record["body"]))   # your real work
            SEEN.add(msg_id)                      # mark done only after success
        except Exception:                         # one bad message must not fail the batch
            failures.append({"itemIdentifier": msg_id})
    return {"batchItemFailures": failures}        # needs ReportBatchItemFailures enabled on the mapping


batch = {"Records": [
    {"messageId": "m1", "body": json.dumps({"amount": 100})},
    {"messageId": "m2", "body": json.dumps({"amount": -5})},      # will fail
    {"messageId": "m3", "body": "not json"},                      # will fail
]}
print(handler(batch, None))                       # only m2 and m3 return to the queue
print(handler(batch, None))                       # m1 is skipped as duplicate; m2/m3 fail again
print(sorted(SEEN))

# Output (real run, Python 3.13):
# {'batchItemFailures': [{'itemIdentifier': 'm2'}, {'itemIdentifier': 'm3'}]}
# {'batchItemFailures': [{'itemIdentifier': 'm2'}, {'itemIdentifier': 'm3'}]}
# ['m1']
```

Why this matters: SQS delivers at least once, so duplicates happen. Returning `batchItemFailures` (with *ReportBatchItemFailures* enabled on the event source mapping) stops the whole batch from being retried because one message failed. The `SEEN` set only helps within one warm environment; in real production make idempotency durable with a DynamoDB conditional write or the Powertools for AWS Lambda idempotency utility.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python Lambda | Node.js Lambda |
|---------|--------------|----------------|
| Runtime | `python3.13` | `nodejs22.x` |
| Handler | `def handler(event, context)` | `export const handler = async (event) => {}` |
| Cold start | usually ~200-500 ms plain, more with big deps | similar, often a bit faster |
| Package | zip / container | zip / container |
| Async | sync handler (or asyncio.run) | async/await native |

```python
# Python way
def handler(event: dict, context) -> dict:
    return {"statusCode": 200, "body": "hi"}
```
```javascript
// JavaScript way
export const handler = async (event) => {
  return { statusCode: 200, body: "hi" };
};
```

Key difference: the Python handler is synchronous by default. Lambda handles one event per environment at a time, so you rarely need async inside it. Node handlers are async functions that return promises. Cold-start numbers vary by memory and package size, so measure yours.

---

## 🟠 FastAPI Connection
You can run a whole FastAPI app on Lambda with the **Mangum** adapter (next topics): `handler = Mangum(app)`. Alternatively use AWS Lambda Web Adapter (runs your normal uvicorn inside Lambda). Keep imports light, create DB engines at module level (reused when warm), and use RDS Proxy or a serverless database because hundreds of parallel Lambdas can exhaust PostgreSQL connections.

```python
# FastAPI example — module-level init is reused in warm invocations
import os
from fastapi import FastAPI
from mangum import Mangum

CONFIG = {"table": os.getenv("TABLE", "orders")}   # runs once per cold start

app = FastAPI()

@app.get("/config")
def config() -> dict[str, str]:
    return CONFIG

handler = Mangum(app)      # Lambda handler = "main.handler"
print(callable(handler))   # True
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Opening DB connections inside the handler for every call
✅ Correct: create clients/engines once at module level and reuse them

```python
# Wrong: new boto3 client and DB connection on every invocation
def handler(event, context):
    import boto3
    s3 = boto3.client("s3")
# Right
import boto3
s3 = boto3.client("s3")             # reused while the environment is warm
def handler(event, context): ...
```

❌ Mistake 2: Returning a dict as `body` (body must be a string) or forgetting statusCode
✅ Correct: `json.dumps(...)` for the body

```python
# Wrong
return {"statusCode": 200, "body": {"ok": True}}       # API Gateway returns 502 "malformed response"
# Right
return {"statusCode": 200, "body": '{"ok": true}'}
```

❌ Mistake 3: Long timeouts, big packages and unbounded concurrency
✅ Correct: right-size memory/timeout, keep the package small, set reserved concurrency to protect your database

```text
Wrong:  timeout 900 s, 250 MB package, unlimited concurrency -> slow cold starts, DB overloaded
Right:  timeout 15 s, slim deps (or layers), reserved concurrency 50
```

---

## 🧠 Tricky Interview Question

```python
# What will this output on two consecutive WARM invocations?
counter = 0

def handler(event, context):
    global counter
    counter += 1
    return counter

# invocation 1 -> ?   invocation 2 (same environment) -> ?
# invocation 3 happens while 1 and 2 are still running at the same time -> ?
print(handler({}, None), handler({}, None))
```
Answer: Locally it prints `1 2`. In Lambda, invocation 1 and 2 return `1` and `2` only if they run in the **same** execution environment, because module-level variables survive between warm calls. One environment handles one request at a time, so if a third request arrives while the first two are running, AWS starts a **new** environment (a cold start) and that call returns `1` again. You cannot rely on globals as shared state or counters: use DynamoDB/Redis. Globals are only good as a cache for expensive objects (clients, config, loaded models).

---

## ⚫ Interview Questions + Answers

Q1: What is a cold start and how do you reduce it?
A1: The extra time to create a new environment, load the runtime and run module-level code. Reduce it with smaller packages, fewer imports (lazy-import rarely used modules), more memory (more CPU), a lighter runtime, provisioned concurrency (pre-warmed environments), or SnapStart where supported.

Q2: What are Lambda's main limits?
A2: Timeout up to 15 minutes, memory 128 MB to 10 GB (CPU scales), zip package 50 MB (250 MB unzipped) or container image up to 10 GB, request/response payload about 6 MB for synchronous calls, and 1000 default concurrent executions per region (can be raised).

Q3: How do you connect Lambda to a relational database safely?
A3: Put RDS Proxy in front to pool connections, cap concurrency, and create the engine at module scope with a small pool size (1-2). Alternatively use DynamoDB or an HTTP-based database.

Q4: API Gateway REST vs HTTP API vs Function URL?
A4: HTTP API is cheaper and faster with simple features and payload v2. REST API has more features (API keys, usage plans, request validation, WAF integration). Function URL is a free built-in HTTPS endpoint for one function without gateway features.

Q5: How are retries and failures handled?
A5: Synchronous (API Gateway): the caller sees the error and decides. Asynchronous (S3, EventBridge): Lambda retries twice and can send failures to a DLQ or on-failure destination. SQS: messages return to the queue after the visibility timeout; use batch item failures and a DLQ with a maximum receive count.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Spiky or low traffic, webhooks, cron jobs, file or event processing
- You want zero server management and pay-per-use cost
- Short tasks (seconds to a few minutes)

❌ Avoid when:
- Constant high traffic (an always-on container can be cheaper)
- WebSockets or long connections (use API Gateway WebSocket or ECS)
- Tasks longer than 15 minutes, or heavy GPU/ML with big models and strict latency

---

## 📊 Visual Diagram
```
 Client -> API Gateway (HTTP API) --event--> [ Lambda environment ]
                                              |  cold start: init imports, clients  (once)
                                              |  handler(event, context)            (every call)
                                              v
                                   DynamoDB / RDS Proxy / S3 / SQS
 Warm env reused for later requests; more parallel requests = more environments
 Logs -> CloudWatch      Errors -> DLQ
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Handler | Function Lambda calls | जिस function को Lambda call करता है |
| Event | Input data describing the trigger | trigger का वर्णन करने वाला input |
| Cold start | Time to create a new environment | नया environment बनाने का समय |
| Provisioned concurrency | Pre-warmed environments | पहले से तैयार environments |
| Layer | Shared package of libraries | साझा libraries का package |
| DLQ | Queue for failed messages | असफल messages की queue |
| Idempotent | Safe to run more than once | कई बार चलाना सुरक्षित |

---

## ⚡ 3-Line Summary
English: Lambda runs a function per event, scales automatically and bills per use. Initialize clients once at module level and return the exact response shape the trigger expects. Plan for cold starts, duplicates and database connection limits.
Hindi: Lambda हर event पर function चलाता है, अपने आप scale होता है और उपयोग के हिसाब से बिल देता है। Clients को module level पर एक बार बनाओ और trigger जो response shape चाहता है वही लौटाओ। Cold starts, duplicates और database connection limits की योजना बनाओ।

---

## ➡️ Next Topic
**445. Serverless Python (Mangum)** — run a full FastAPI app on Lambda by translating API Gateway events into ASGI calls.
