---

# 445. Serverless Python (Mangum)
# हिंदी में: Serverless Python (Mangum)

---

## 🔵 Simple Definition (English)
Mangum is a small adapter that lets an ASGI app (FastAPI, Starlette) run on AWS Lambda. It translates the Lambda event from API Gateway or a Function URL into an ASGI request, runs your app and turns the ASGI response back into the Lambda response format. You write `handler = Mangum(app)`.

## 🔵 सरल परिभाषा (Hindi)
Mangum एक छोटा adapter है जो ASGI app (FastAPI, Starlette) को AWS Lambda पर चलने देता है। यह API Gateway या Function URL के Lambda event को ASGI request में बदलता है, आपका app चलाता है और ASGI response को वापस Lambda के response format में बदल देता है। आप बस `handler = Mangum(app)` लिखते हो।

---

## 🔴 Problem it Solves
Lambda does not speak HTTP. It passes a JSON "event" to a function and expects a JSON dict back. FastAPI speaks ASGI. Without an adapter you would rewrite routing, validation and docs by hand inside one giant handler, losing everything FastAPI gives you. Mangum lets you keep the same FastAPI project and deploy it serverless (and still run it locally with uvicorn).

## 🔴 यह क्यों बना? (Hindi)
Lambda HTTP नहीं बोलता। वह function को JSON "event" देता है और बदले में JSON dict चाहता है। FastAPI ASGI बोलता है। Adapter के बिना आपको routing, validation और docs एक विशाल handler में हाथ से लिखने पड़ते और FastAPI की सारी सुविधाएँ खो जातीं। Mangum से आप वही FastAPI project रखते हैं और उसे serverless deploy करते हैं (और local में uvicorn से भी चलाते हैं)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client sends HTTPS request to API Gateway (or a Lambda Function URL)
Step 2 → API Gateway builds an event JSON (method, path, headers, query, body) and calls Lambda
Step 3 → Lambda calls handler(event, context) -> that is Mangum.__call__
Step 4 → Mangum picks a handler class for the event type (HTTP API v1/v2, REST, ALB, Function URL)
Step 5 → It converts the event into an ASGI scope + receive() body
Step 6 → It runs the FastAPI app (lifespan startup first, if enabled)
Step 7 → App sends ASGI messages (status, headers, body); Mangum collects them
Step 8 → Mangum returns {"statusCode", "headers", "body", "isBase64Encoded"} to Lambda
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client, API Gateway (या Lambda Function URL) को HTTPS request भेजता है
Step 2 → API Gateway event JSON बनाता है (method, path, headers, query, body) और Lambda बुलाता है
Step 3 → Lambda handler(event, context) call करता है -> यही Mangum.__call__ है
Step 4 → Mangum event के प्रकार के लिए handler class चुनता है (HTTP API v1/v2, REST, ALB, Function URL)
Step 5 → वह event को ASGI scope + receive() body में बदलता है
Step 6 → FastAPI app चलाता है (lifespan startup पहले, अगर चालू हो)
Step 7 → App ASGI messages भेजता है (status, headers, body); Mangum इकट्ठा करता है
Step 8 → Mangum {"statusCode", "headers", "body", "isBase64Encoded"} Lambda को लौटाता है
```

---

## 🟡 Real World Example
An internal tool for a company's finance team has 50 users and traffic only in office hours. Running a 24x7 server for it wastes money. The team deploys the existing FastAPI app with Mangum behind an API Gateway HTTP API. Cost is a few rupees per month, there are no servers to patch, and the same code still runs locally with `uvicorn main:app --reload`.

## 🟡 Real Example Hindi mein
Company की finance team के internal tool के 50 users हैं और traffic सिर्फ office समय में। उसके लिए 24x7 server चलाना पैसे की बर्बादी है। Team मौजूदा FastAPI app को Mangum के साथ API Gateway HTTP API के पीछे deploy करती है। महीने का खर्च कुछ रुपये, patch करने को कोई server नहीं, और वही code local में `uvicorn main:app --reload` से भी चलता है।

---

## 💻 Code Example — Basic
FastAPI + Mangum, invoked locally with a hand-built API Gateway HTTP API (v2) event. This is the same call Lambda would make:

```python
# Basic: FastAPI on Lambda with Mangum - invoked with a hand-made API Gateway event
import json                                       # decode response body
from fastapi import FastAPI                       # your normal app
from mangum import Mangum                         # ASGI -> Lambda adapter

app: FastAPI = FastAPI()                          # nothing Lambda-specific in the app


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None) -> dict[str, int | str | None]:
    return {"item_id": item_id, "q": q}           # normal FastAPI route


handler = Mangum(app, lifespan="off")             # Lambda "Handler" setting = main.handler

event = {                                         # API Gateway HTTP API (payload v2) event
    "version": "2.0", "routeKey": "$default", "rawPath": "/items/5", "rawQueryString": "q=abc",
    "headers": {"host": "x.execute-api.ap-south-1.amazonaws.com"},
    "queryStringParameters": {"q": "abc"},
    "requestContext": {"http": {"method": "GET", "path": "/items/5", "protocol": "HTTP/1.1",
                                "sourceIp": "1.2.3.4", "userAgent": "t"},
                       "stage": "$default"},
    "isBase64Encoded": False,
}
resp = handler(event, None)                       # Mangum runs the ASGI app and builds the reply
print(resp["statusCode"], json.loads(resp["body"]))
print(resp["headers"]["content-type"])

# Output (real run, Python 3.13):
# 200 {'item_id': 5, 'q': 'abc'}
# application/json
```

`lifespan="off"` skips startup/shutdown events (fine when the app has none). Not deployed to AWS: no account here.

## 💻 Code Example — Advanced
Lifespan startup, a stage prefix (`/prod`), a POST body validated by Pydantic and an API Gateway REST (v1) event. Ran locally:

```python
# Advanced: Mangum with lifespan, stage prefix, POST body and a REST (v1) event
import json                                       # bodies
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel

state: dict[str, str] = {}                        # filled at startup (cold start only)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    state["db"] = "connected"                     # open pools / load config ONCE per container
    yield
    state.clear()                                 # cleanup on shutdown


app = FastAPI(lifespan=lifespan)


class Pay(BaseModel):
    amount: int


@app.post("/pay")
def pay(p: Pay) -> dict[str, Any]:
    return {"paid": p.amount, "db": state.get("db")}


# api_gateway_base_path strips the stage name ("/prod") before FastAPI routes the request
handler = Mangum(app, lifespan="auto", api_gateway_base_path="/prod")


def v1_event(path: str, body: dict[str, Any]) -> dict[str, Any]:
    return {                                      # API Gateway REST API (payload v1) event
        "httpMethod": "POST", "path": path, "resource": "/{proxy+}",
        "headers": {"content-type": "application/json", "host": "x.amazonaws.com"},
        "multiValueHeaders": {"content-type": ["application/json"], "host": ["x.amazonaws.com"]},
        "queryStringParameters": None, "multiValueQueryStringParameters": None,
        "pathParameters": None, "stageVariables": None,
        "requestContext": {"stage": "prod", "identity": {"sourceIp": "1.2.3.4"},
                           "resourcePath": "/{proxy+}", "httpMethod": "POST"},
        "body": json.dumps(body), "isBase64Encoded": False,
    }


r = handler(v1_event("/prod/pay", {"amount": 250}), None)
print(r["statusCode"], json.loads(r["body"]))     # lifespan ran, db connected
r = handler(v1_event("/prod/pay", {"amount": "abc"}), None)
print(r["statusCode"], json.loads(r["body"])["detail"][0]["type"])   # validation error -> 422

# Output (real run, Python 3.13):
# 200 {'paid': 250, 'db': 'connected'}
# 422 int_parsing
```

What this shows: Mangum ran the lifespan startup (`state["db"]` is set), stripped the `/prod` stage with `api_gateway_base_path`, routed `/pay`, and Pydantic returned a normal FastAPI 422 for the bad body. Deployment commands (**not run**):

```bash
pip install -r requirements.txt --target package/ --platform manylinux2014_x86_64 --only-binary=:all:
cp main.py package/ && (cd package && zip -r ../function.zip .)
aws lambda create-function --function-name orders-api --runtime python3.13 \
  --handler main.handler --zip-file fileb://function.zip --role <role-arn> --memory-size 512 --timeout 15
aws lambda create-function-url-config --function-name orders-api --auth-type NONE   # quick public URL
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | Node.js |
|---------|--------|---------|
| Adapter | Mangum (ASGI -> Lambda) | `serverless-http` (Express -> Lambda) |
| Wrap the app | `handler = Mangum(app)` | `exports.handler = serverless(app)` |
| Framework | FastAPI / Starlette | Express / Koa / Fastify |
| Alternative | AWS Lambda Web Adapter | AWS Lambda Web Adapter |
| IaC helpers | AWS SAM, Serverless Framework, CDK | same |

```python
# Python way
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()
handler = Mangum(app, lifespan="off")      # Lambda handler setting: main.handler
```
```javascript
// JavaScript way — serverless-http plays the same role for Express
const serverless = require("serverless-http");
const express = require("express");
const app = express();
module.exports.handler = serverless(app);  // Lambda handler setting: index.handler
```

Key difference: both libraries are thin translators of events to the framework's request type. The Python version converts to ASGI (async); `serverless-http` converts to Node's `req`/`res`.

---

## 🟠 FastAPI Connection
Mangum makes a FastAPI app serverless without code changes. Things to adapt: (1) put stage prefix handling in `api_gateway_base_path` (HTTP APIs with `$default` stage have no prefix); (2) in `/docs`, the Swagger page needs the correct `root_path` or `servers` entry, otherwise it requests `/openapi.json` without the stage; (3) avoid background tasks that outlive the response (Lambda may freeze the process after returning); (4) use `lifespan="auto"` only if startup is quick, since it runs on every cold start.

```python
# FastAPI example — local development and Lambda share the same app object
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/ping")
def ping() -> dict[str, str]:
    return {"pong": "ok"}

handler = Mangum(app, lifespan="off")      # used by Lambda
# local:  uvicorn main:app --reload        # used by developers
print(type(handler).__name__)              # Mangum
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Wrong handler setting (`main.app` instead of `main.handler`)
✅ Correct: point Lambda to the Mangum object

```text
Wrong:  Handler = main.app        -> Lambda calls the FastAPI app with (event, context): it fails (ASGI app expects scope/receive/send)
Right:  Handler = main.handler    -> handler = Mangum(app)
```

❌ Mistake 2: Ignoring the stage prefix, so every route returns 404 or the docs break
✅ Correct: set `api_gateway_base_path` (REST API stages) and pass the server's root path

```python
# Wrong: URL is /prod/items, but FastAPI only knows /items -> 404
handler = Mangum(app)
# Right
handler = Mangum(app, api_gateway_base_path="/prod")
```

❌ Mistake 3: Fire-and-forget `BackgroundTasks` or threads for important work
✅ Correct: do the work before responding, or send it to SQS / Step Functions

```python
# Wrong: Lambda freezes after the response; the task may never finish
# background_tasks.add_task(send_invoice, order_id)
# Right: queue it
# sqs.send_message(QueueUrl=URL, MessageBody=json.dumps({"order_id": order_id}))
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def root() -> dict[str, int]:
    return {"ok": 1}

handler = Mangum(app, lifespan="off")
event = {"httpMethod": "GET", "path": "/"}   # a stripped-down REST event
try:
    handler(event, None)
except Exception as e:
    print(type(e).__name__)
```
Answer: It prints `RuntimeError` (verified with Mangum 0.22.0). Mangum decides which handler class to use by inspecting the event keys. A real API Gateway REST event has `multiValueHeaders`, `requestContext` and more; the stripped-down dict matches no known event shape, so Mangum raises `RuntimeError: The adapter was unable to infer a handler to use for the event...`. Lesson: when unit-testing a Lambda handler, copy a full sample event from the AWS docs or from a real invocation log instead of inventing a short one, exactly like the advanced example does.

---

## ⚫ Interview Questions + Answers

Q1: What does Mangum do internally?
A1: It implements an ASGI client. For each Lambda event it builds an ASGI scope (type "http"), supplies the request body through `receive`, collects `send` messages from the app and returns a Lambda-formatted response. It can handle API Gateway v1/v2, ALB and Function URL events.

Q2: Mangum vs AWS Lambda Web Adapter?
A2: Mangum is a Python library inside your code, so Lambda calls your handler directly. The Lambda Web Adapter is an extension (a layer or a binary in a container) that starts your normal web server (uvicorn) and forwards events to it as real HTTP, so any framework works with no code change, with a small extra overhead.

Q3: Does FastAPI's lifespan work on Lambda?
A3: Yes with `lifespan="auto"` or `"on"`: startup runs on cold start. Shutdown rarely runs because Lambda just freezes or kills the environment, so do not rely on it for critical cleanup.

Q4: How do you reduce cold start for a FastAPI Lambda?
A4: Slim dependencies (avoid pandas/numpy if you can), lazy imports, pre-built wheels for the Lambda architecture (arm64 is cheaper and often faster), higher memory, and provisioned concurrency for latency-sensitive endpoints. Avoid creating heavy objects (ML models) on every cold start; load them from `/tmp` or EFS, or use a container.

Q5: What are limitations of FastAPI on Lambda?
A5: 6 MB synchronous response limit, no persistent WebSocket connections through plain HTTP events, 29 seconds API Gateway timeout (30 s for HTTP APIs), `/tmp` storage only (up to 10 GB), and DB connection management issues. For streaming or long tasks pick ECS/Fargate or use Lambda response streaming with a Function URL.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Low or spiky traffic APIs, internal tools, prototypes
- You want pay-per-use with a normal FastAPI codebase
- Event-driven systems that also expose a small HTTP API

❌ Avoid when:
- Constant heavy traffic where always-on containers are cheaper
- Long-running requests, WebSockets or streaming-heavy APIs
- Strict low-latency needs where cold starts are unacceptable and you do not want to pay for provisioned concurrency

---

## 📊 Visual Diagram
```
 HTTPS request
     |
 API Gateway  --event JSON-->  Lambda: handler = Mangum(app)
                                     |  1. event -> ASGI scope
                                     v
                               FastAPI app (routes, validation)
                                     |  2. ASGI response messages
                                     v
                               Mangum -> {"statusCode":200,"headers":{...},"body":"..."}
     <---------------------------------------------------------|
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ASGI | Async Python web interface | Python का async web interface |
| Mangum | ASGI to Lambda adapter | ASGI से Lambda adapter |
| API Gateway | AWS service that exposes HTTP endpoints | HTTP endpoints देने वाली AWS service |
| Function URL | Built-in HTTPS URL for a Lambda | Lambda का built-in HTTPS URL |
| Stage | API Gateway version path like /prod | /prod जैसा version path |
| Payload v1 / v2 | Event formats of REST / HTTP API | REST / HTTP API के event formats |

---

## ⚡ 3-Line Summary
English: Mangum wraps a FastAPI app so Lambda can call it. It converts API Gateway events to ASGI and back. Handle stage prefixes, cold starts and background work carefully.
Hindi: Mangum FastAPI app को लपेटता है ताकि Lambda उसे call कर सके। यह API Gateway events को ASGI में और वापस बदलता है। Stage prefix, cold starts और background काम का ध्यान रखो।

---

## ➡️ Next Topic
**446. Deploy on Railway/Render** — the simplest path: push to Git and a platform builds and runs your FastAPI app.
