---

# 097. Structured Output in FastAPI
# हिंदी में: FastAPI में Structured Output

---

## 🔵 Simple Definition (English)
FastAPI is built on Pydantic, so the same model can validate the incoming request, define the LLM's output schema and shape the API response. A good LLM endpoint is: validate request, call the LLM with a schema, validate the result, map failures to proper HTTP status codes, and return a typed response.

## 🔵 सरल परिभाषा (Hindi)
FastAPI Pydantic पर बना है, इसलिए एक ही model incoming request validate कर सकता है, LLM का output schema बना सकता है और API response की shape तय कर सकता है। अच्छा LLM endpoint: request validate करो, schema के साथ LLM call करो, result validate करो, failures को सही HTTP status codes में बदलो, और typed response लौटाओ।

---

## 🔴 Problem it Solves
Naive endpoints return whatever the LLM said, crash with 500 on a bad parse, hang on slow calls and leak raw errors. A well-designed structured-output endpoint gives clients a stable contract (OpenAPI docs), safe failures and observability.

## 🔴 यह क्यों बना? (Hindi)
Naive endpoints LLM का कहा कुछ भी लौटा देते हैं, bad parse पर 500 से crash होते हैं, slow calls पर अटकते हैं और raw errors leak करते हैं। अच्छा structured-output endpoint clients को stable contract (OpenAPI docs), सुरक्षित failures और observability देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define request model (ClassifyRequest) and response model (ClassifyResponse)
Step 2 → Create ONE shared AsyncOpenAI client at app startup (lifespan)
Step 3 → Route receives validated request (FastAPI returns 422 for bad input)
Step 4 → Call LLM with response_format=TariffResult, timeout set
Step 5 → Map outcomes: success 200 | refusal 422 | LLM invalid 502 | rate limit 429/503 | timeout 504
Step 6 → Wrap in response model (add usage, request_id)
Step 7 → Log tokens, latency, status for monitoring
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Request model (ClassifyRequest) और response model (ClassifyResponse) define करो
Step 2 → App startup (lifespan) में एक shared AsyncOpenAI client बनाओ
Step 3 → Route को validated request मिलती है (bad input पर FastAPI 422 देता है)
Step 4 → timeout के साथ response_format=TariffResult से LLM call करो
Step 5 → Outcomes map करो: success 200 | refusal 422 | LLM invalid 502 | rate limit 429/503 | timeout 504
Step 6 → Response model में wrap करो (usage, request_id जोड़ो)
Step 7 → Tokens, latency, status monitoring के लिए log करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: `POST /v1/classify` accepts `{product, country}` and returns `{result: {hs_code, duty_percent, confidence}, usage: {...}, needs_review: bool}`. The mobile app and the customs back-office both rely on this stable JSON, and OpenAPI docs are auto-generated.

**Amazon-style**: `POST /v1/listing/normalize` returns a cleaned product schema for catalog ingestion.

## 🟡 Real Example Hindi mein
**Tariff System**: `POST /v1/classify` `{product, country}` लेता है और `{result: {hs_code, duty_percent, confidence}, usage: {...}, needs_review: bool}` लौटाता है। Mobile app और customs back-office दोनों इसी stable JSON पर निर्भर हैं, और OpenAPI docs अपने-आप बनते हैं।

**Amazon-style**: `POST /v1/listing/normalize` catalog ingestion के लिए साफ product schema लौटाता है।

---

## 💻 Code Example — Basic
```python
# Basic: a FastAPI endpoint with a FAKE LLM so it runs without an API key.
# Run: pip install fastapi uvicorn pydantic ; uvicorn this_file:app --reload
from fastapi import FastAPI, HTTPException            # framework + error type
from pydantic import BaseModel, Field                 # models

app = FastAPI(title="Tariff API")                     # app object

class ClassifyRequest(BaseModel):                     # request contract
    product: str = Field(min_length=3, max_length=500)

class TariffResult(BaseModel):                        # LLM output contract
    hs_code: str
    duty_percent: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)

class ClassifyResponse(BaseModel):                    # API response contract
    result: TariffResult
    needs_review: bool

def fake_llm(product: str) -> dict:
    """Stand-in for a real LLM call."""
    return {"hs_code": "8518.30", "duty_percent": 0.0, "confidence": 0.62}

@app.post("/classify", response_model=ClassifyResponse)
async def classify(req: ClassifyRequest) -> ClassifyResponse:
    try:
        result = TariffResult.model_validate(fake_llm(req.product))   # validate LLM output
    except ValueError as exc:                                         # ValidationError subclasses ValueError
        raise HTTPException(status_code=502, detail="Invalid LLM output") from exc
    return ClassifyResponse(result=result, needs_review=result.confidence < 0.7)

if __name__ == "__main__":
    # Quick offline test without a server, using FastAPI's TestClient (needs httpx):
    from fastapi.testclient import TestClient
    client = TestClient(app)
    print(client.post("/classify", json={"product": "earbuds"}).json())   # 200 with needs_review True
    print(client.post("/classify", json={"product": "x"}).status_code)    # 422 from request validation
```

## 💻 Code Example — Advanced
```python
# Production: lifespan-managed client, timeout, status mapping, usage logging, request id.
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional
import openai
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

log = logging.getLogger("tariff")                      # structured logs go here

class ClassifyRequest(BaseModel):
    product: str = Field(min_length=3, max_length=500)

class TariffResult(BaseModel):
    hs_code: str
    duty_percent: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)

class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    latency_ms: int

class ClassifyResponse(BaseModel):
    request_id: str
    result: TariffResult
    usage: Usage
    needs_review: bool

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.llm = openai.AsyncOpenAI(timeout=20.0, max_retries=2)   # one shared client
    yield                                                              # app runs here
    await app.state.llm.close()                                        # clean shutdown

app = FastAPI(lifespan=lifespan)

@app.post("/v1/classify", response_model=ClassifyResponse)
async def classify(req: ClassifyRequest, request: Request) -> ClassifyResponse:
    rid = str(uuid.uuid4())                                            # trace id
    start = time.perf_counter()
    llm: openai.AsyncOpenAI = request.app.state.llm
    try:
        completion = await llm.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "Classify the product for customs."},
                      {"role": "user", "content": req.product}],
            response_format=TariffResult, temperature=0, max_tokens=200)
    except openai.RateLimitError as exc:
        raise HTTPException(status_code=503, detail="LLM busy, retry later") from exc
    except openai.APITimeoutError as exc:
        raise HTTPException(status_code=504, detail="LLM timeout") from exc
    except openai.LengthFinishReasonError as exc:
        raise HTTPException(status_code=502, detail="LLM output truncated") from exc
    except openai.APIError as exc:                                     # catch-all for SDK errors
        log.exception("openai failure rid=%s", rid)
        raise HTTPException(status_code=502, detail="LLM upstream error") from exc
    msg = completion.choices[0].message
    parsed: Optional[TariffResult] = msg.parsed
    if msg.refusal or parsed is None:
        raise HTTPException(status_code=422, detail="Request could not be classified")
    usage = completion.usage
    latency = int((time.perf_counter() - start) * 1000)
    log.info("rid=%s in=%s out=%s ms=%s", rid, usage.prompt_tokens, usage.completion_tokens, latency)
    return ClassifyResponse(
        request_id=rid, result=parsed,
        usage=Usage(input_tokens=usage.prompt_tokens, output_tokens=usage.completion_tokens, latency_ms=latency),
        needs_review=parsed.confidence < 0.7)
```

---

## 🟠 FastAPI Integration
This whole topic is the FastAPI integration. Extra production touches:

```python
from fastapi import Depends, Header

async def require_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != "secret":                          # replace with real auth store
        raise HTTPException(status_code=401, detail="bad key")

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}                            # for load balancers

# Add: Depends(require_api_key) on routes, rate limiting (slowapi), request size limits,
# BackgroundTasks for logging, and a semaphore to cap concurrent LLM calls.
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI

chain = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(TariffResult)

@app.post("/v2/classify", response_model=TariffResult)
async def classify_lc(req: ClassifyRequest) -> TariffResult:
    return await chain.ainvoke(req.product)            # ainvoke keeps the event loop free
# A LangGraph compiled graph is invoked the same way: await graph.ainvoke({"product": ...}).
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blocking calls in `async def`
✅ Correct: Use the async client (`AsyncOpenAI`) and `await`.

```python
# Wrong: client = OpenAI(); def/async def route: client.chat.completions.create(...)  # blocks loop
# Right: AsyncOpenAI + await ...
```

❌ Mistake 2: Creating a new client per request
✅ Correct: One shared client in `lifespan`/app state (connection reuse).

```python
# Wrong: async def route(): client = AsyncOpenAI(); ...
# Right: request.app.state.llm
```

---

## 🧠 Tricky Interview Question

**Q**: "Under load, your FastAPI classify endpoint's latency spikes to 40s and you get 429s from OpenAI. The server CPU is idle. What do you do?"

**Answer**: The bottleneck is the upstream rate limit and unbounded concurrency, not CPU. Add an `asyncio.Semaphore` to limit concurrent LLM calls, client timeouts, retries with backoff for 429, queueing (Celery/Redis/RQ) for non-interactive work, caching of repeated products, a cheaper model for easy cases, and request shedding (return 503 with `Retry-After`). Monitor tokens-per-minute usage against your tier limits.

---

## ⚫ Interview Questions + Answers

Q1: Why is FastAPI a good fit for LLM apps?
A1: Async support, Pydantic validation and automatic OpenAPI docs; one model can serve request, LLM schema and response.

Q2: Which HTTP status for an invalid LLM output?
A2: 502 (Bad Gateway) when the upstream gave bad data; 422 if the client's input was unprocessable; 504 for timeouts; 503/429 for overload.

Q3: What is `lifespan` used for?
A3: Startup/shutdown: create shared resources like the LLM client and close them cleanly.

Q4: Why use `response_model`?
A4: It validates and filters the returned data, hides extra fields and documents the contract.

Q5: How do you limit cost abuse on an LLM endpoint?
A5: Auth, per-user rate limits and daily token quotas, input length caps (`max_length`), `max_tokens`, caching, and anomaly alerts on spend.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Serving LLM features to apps/other services
- You need typed, documented JSON

❌ Avoid when:
- One-off scripts/notebooks
- Long jobs that should be queued instead of held in an HTTP request

---

## 📊 Visual Diagram
```
 Client ──► FastAPI ─────────────────────────────────────────────┐
            │ 1 validate ClassifyRequest (422 on error)          │
            │ 2 call LLM (shared client, timeout, schema)        │
            │ 3 validate TariffResult                            │
            │ 4 map errors -> 422/502/503/504                    │
            │ 5 ClassifyResponse {result, usage, needs_review}   │
 Client ◄───┘ 200 JSON                                           │
            logs: request_id, tokens, latency ───────────────────┘
```

---

## 💰 Cost Impact
Costs come from tokens per request x traffic. Endpoint design controls waste: input caps, `max_tokens`, caching, retries that are bounded, and rate limits. Returning `usage` in the response lets clients see and budget spend.
Optimise: cache by normalised product text (Redis), use `gpt-4o-mini`, batch offline requests via the Batch API, reject oversized inputs early, alert on tokens per minute.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| response_model | Declares/filters API output | API output की shape |
| lifespan | Startup/shutdown hook | Startup/shutdown hook |
| 502 / 504 | Bad upstream / timeout | खराब upstream / timeout |
| Semaphore | Concurrency limiter | एक साथ calls की सीमा |
| OpenAPI | Auto API documentation | अपने-आप बनने वाले API docs |

---

## ⚡ 3-Line Summary
English: Use one Pydantic model family for request, LLM output and response. Share one async client and map errors to correct HTTP codes. Log tokens and latency for every request.
Hindi: Request, LLM output और response के लिए Pydantic models का एक परिवार use करो। एक shared async client रखो और errors को सही HTTP codes में map करो। हर request के tokens और latency log करो।

---

## ➡️ Next Topic
**098. Schema Design Best Practices** — how to design schemas that LLMs fill accurately and cheaply.
