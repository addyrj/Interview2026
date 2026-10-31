---

# 025. OpenAI API — Complete Guide
# हिंदी में: OpenAI API — पूरी Guide

---

## 🔵 Simple Definition (English)
The OpenAI API is an HTTPS service that lets your code call OpenAI models for text, images, audio, embeddings, and moderation. You send a JSON request with an API key and get a JSON response. The official Python package `openai` (version 1 or later) wraps this in a simple client.

## 🔵 सरल परिभाषा (Hindi)
OpenAI API एक HTTPS service है जिससे आपका code OpenAI के models को text, image, audio, embeddings और moderation के लिए call करता है। आप API key के साथ JSON request भेजते हैं और JSON response मिलता है। Official Python package `openai` (version 1 या उससे ऊपर) इसे simple client में wrap करता है।

---

## 🔴 Problem it Solves
Training and hosting a large model needs huge GPUs and expertise. The API gives you a ready model with pay-per-token pricing, so a small team can add AI features in an afternoon. It also hides scaling, safety updates, and model upgrades behind one endpoint.

## 🔴 यह क्यों बना? (Hindi)
बड़ा model train और host करने के लिए बहुत GPUs और expertise चाहिए। API ready model देती है, pay-per-token pricing के साथ, इसलिए छोटी team भी एक दोपहर में AI feature जोड़ सकती है। Scaling, safety updates और model upgrades एक endpoint के पीछे छिपे रहते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create an API key in the OpenAI dashboard
Step 2 → Store it in an environment variable OPENAI_API_KEY (never in code)
Step 3 → pip install openai ; create OpenAI() or AsyncOpenAI() client
Step 4 → Pick an endpoint: chat.completions, embeddings, moderations, audio, images
Step 5 → Send request: model + messages + options (temperature, max_tokens)
Step 6 → Server runs the model and bills input + output tokens
Step 7 → Read response: choices[0].message.content and usage
Step 8 → Handle errors (rate limit, timeout, bad request) with retries
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → OpenAI dashboard में API key बनाओ
Step 2 → उसे environment variable OPENAI_API_KEY में रखो (code में कभी नहीं)
Step 3 → pip install openai ; OpenAI() या AsyncOpenAI() client बनाओ
Step 4 → Endpoint चुनो: chat.completions, embeddings, moderations, audio, images
Step 5 → Request भेजो: model + messages + options (temperature, max_tokens)
Step 6 → Server model चलाता है और input + output tokens का bill बनता है
Step 7 → Response पढ़ो: choices[0].message.content और usage
Step 8 → Errors (rate limit, timeout, bad request) retries से handle करो
```

---

## 🟡 Real World Example
**Tariff Classification System** uses three endpoints of one API:
1. `embeddings` (text-embedding-3-small) to index tariff chapters for search.
2. `chat.completions` (gpt-4o-mini) to pick the HS code from retrieved chunks.
3. `moderations` to screen free-text user input before processing.

**Zomato AI**: Chat completions answer "suggest a light dinner", embeddings power dish search, and audio transcription handles voice orders.

## 🟡 Real Example Hindi mein
**Tariff Classification System** एक ही API के तीन endpoints use करता है:
1. `embeddings` से tariff chapters को search के लिए index करना।
2. `chat.completions` (gpt-4o-mini) से retrieved chunks देखकर HS code चुनना।
3. `moderations` से user का free text process करने से पहले screen करना।

**Zomato AI**: Chat completions "हल्का dinner suggest करो" का जवाब देते हैं, embeddings dish search चलाते हैं, और audio transcription voice orders संभालता है।

---

## 💻 Code Example — Basic
```python
# Basic OpenAI call (needs: pip install openai, and OPENAI_API_KEY env var)
import os                                        # read environment variables
from openai import OpenAI                        # sync client class

# Fail early with a clear message if the key is missing
if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit("Set OPENAI_API_KEY first (export OPENAI_API_KEY=...)")

client = OpenAI()                                # client reads the key from env automatically

# Send one chat request
response = client.chat.completions.create(
    model="gpt-4o-mini",                         # small, cheap, fast model
    messages=[                                   # conversation so far
        {"role": "system", "content": "You are a customs tariff assistant."},  # behaviour
        {"role": "user", "content": "HS heading for a smartphone?"},           # question
    ],
    max_tokens=100,                              # cap the answer length (cost control)
)

print(response.choices[0].message.content)       # the answer text
print(response.usage.prompt_tokens)              # input tokens billed
print(response.usage.completion_tokens)          # output tokens billed

# Other endpoints use the same client:
# client.embeddings.create(model="text-embedding-3-small", input="power bank")
# client.moderations.create(input="some user text")
```

## 💻 Code Example — Advanced
```python
# Production wrapper: config, timeouts, retries, typed result, sync + async
import asyncio                                           # async runner
import logging                                           # logging
from dataclasses import dataclass                        # typed result object
from typing import Optional                              # optional type

from openai import (                                     # SDK v1 names
    APIConnectionError, APIStatusError, AsyncOpenAI, OpenAI, RateLimitError,
)

logger = logging.getLogger(__name__)                     # module logger


@dataclass
class LLMResult:
    text: str                                            # answer
    prompt_tokens: int                                   # input usage
    completion_tokens: int                               # output usage
    model: str                                           # model that served it


class OpenAIService:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model                               # default model
        # timeout and max_retries are built into the SDK client
        self.sync = OpenAI(timeout=30.0, max_retries=3)
        self.aclient = AsyncOpenAI(timeout=30.0, max_retries=3)

    def ask(self, prompt: str, system: str = "Be concise.") -> Optional[LLMResult]:
        try:
            r = self.sync.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": prompt}],
                max_tokens=300,
            )
        except RateLimitError:                           # 429 after SDK retries
            logger.warning("rate limited")
            return None
        except APIConnectionError as exc:                # network problem
            logger.error("connection error: %s", exc)
            return None
        except APIStatusError as exc:                    # any other 4xx/5xx
            logger.error("status %s: %s", exc.status_code, exc.message)
            return None
        return LLMResult(
            text=r.choices[0].message.content or "",     # content can be None
            prompt_tokens=r.usage.prompt_tokens,
            completion_tokens=r.usage.completion_tokens,
            model=r.model,
        )

    async def aask(self, prompt: str, system: str = "Be concise.") -> Optional[LLMResult]:
        try:
            r = await self.aclient.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": prompt}],
                max_tokens=300,
            )
        except (RateLimitError, APIConnectionError, APIStatusError) as exc:
            logger.error("async call failed: %s", exc)
            return None
        return LLMResult(r.choices[0].message.content or "",
                         r.usage.prompt_tokens, r.usage.completion_tokens, r.model)


if __name__ == "__main__":
    svc = OpenAIService()
    print(asyncio.run(svc.aask("HS heading for a laptop?")))
```

---

## 🟠 FastAPI Integration
Create the client once at startup and reuse it. Do not create a new client per request.

```python
from contextlib import asynccontextmanager       # lifespan helper
from fastapi import FastAPI, HTTPException       # framework
from pydantic import BaseModel                   # request models
from openai import APIStatusError, AsyncOpenAI   # client + error


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = AsyncOpenAI(timeout=30.0, max_retries=2)   # create once
    yield                                                          # app runs
    await app.state.client.close()                                 # clean shutdown


app = FastAPI(lifespan=lifespan)                 # attach lifespan


class Query(BaseModel):
    product: str                                 # product to classify


@app.post("/classify")
async def classify(q: Query) -> dict:
    try:
        r = await app.state.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"HS code for {q.product}? Digits only."}],
            temperature=0,
            max_tokens=20,
        )
    except APIStatusError as exc:                # upstream error
        raise HTTPException(status_code=502, detail=f"OpenAI error {exc.status_code}")
    return {"hs_code": r.choices[0].message.content, "tokens": r.usage.total_tokens}
```

---

## 🔗 LangChain / LangGraph Connection
`langchain-openai` wraps the same API: `ChatOpenAI` (chat) and `OpenAIEmbeddings` (embeddings). LangGraph nodes just call these.

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings   # wrappers over the OpenAI API
from langchain_core.output_parsers import StrOutputParser    # turns message into str
from langchain_core.prompts import ChatPromptTemplate        # prompt template

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_retries=3)  # retries built in
emb = OpenAIEmbeddings(model="text-embedding-3-small")               # embeddings model

chain = (
    ChatPromptTemplate.from_template("HS code for {product}? Digits only.")
    | llm
    | StrOutputParser()
)
# print(chain.invoke({"product": "power bank"}))   # needs OPENAI_API_KEY
# vec = emb.embed_query("power bank")              # list[float]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Hard-coding the API key
✅ Correct: Read from environment or a secret manager.

```python
# Wrong — key leaks to git
client = OpenAI(api_key="sk-abc123...")
# Right — key stays outside code
client = OpenAI()   # uses OPENAI_API_KEY
```

❌ Mistake 2: Creating a new client for every request
✅ Correct: Make one client and reuse it (connection pooling).

❌ Mistake 3: Calling a sync client inside `async def` (blocks the event loop)
✅ Correct: Use `AsyncOpenAI` with `await`.

❌ Mistake 4: Using the old v0 syntax `openai.ChatCompletion.create(...)`
✅ Correct: Use `client.chat.completions.create(...)`.

---

## 🧠 Tricky Interview Question

**Q**: "Your service works locally but in production you see random 429s and slow responses, even though traffic is low. What do you check?"

**Answer**: (1) Is a client created per request, losing connection reuse? (2) Do many workers share one API key and hit the per-minute token limit together (limits are per organisation or project, not per process)? (3) Is `max_tokens` unset, so reserved output tokens count toward the TPM limit estimate? (4) Are retries stacking, where the SDK retries and your own wrapper retries too, multiplying load? Fix with a shared client, a central rate limiter, `max_tokens`, one retry layer, and monitoring of the rate-limit response headers.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] How do you authenticate to the OpenAI API?
A1: With an API key sent as a Bearer token. The SDK reads `OPENAI_API_KEY` from the environment automatically.

Q2: [Easy] What do you get back besides the text?
A2: `usage` (prompt, completion, total tokens), `finish_reason`, `model`, and `id`. Use `usage` for cost tracking.

Q3: [Medium] Which endpoints would a RAG app use?
A3: `embeddings` for indexing and query vectors, `chat.completions` for the final answer, optionally `moderations` for input safety.

Q4: [Medium] What is the difference between `OpenAI` and `AsyncOpenAI`?
A4: `OpenAI` blocks the thread until the response returns. `AsyncOpenAI` returns awaitables, so one process can run many requests concurrently, which is what FastAPI needs.

Q5: [Hard] How would you design for reliability when OpenAI has an outage?
A5: Timeouts, bounded retries with backoff and jitter, a circuit breaker, fallback to another model or provider (LiteLLM or LangChain `with_fallbacks`), cached answers for repeat queries, and graceful degradation (for example, return "classification pending" and queue the job).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need strong general models quickly
- Variable traffic where pay-per-token beats owning GPUs
- You want tool calling, structured outputs, and embeddings in one place

❌ Avoid when:
- Data cannot leave your network (use local models)
- Very high stable volume where self-hosting is cheaper
- You need full control of the model weights

---

## 📊 Visual Diagram
```
 Your app                          OpenAI
+-----------+   HTTPS + API key   +------------------------+
| FastAPI   | ------------------> | /v1/chat/completions   |
| (client)  |                     | /v1/embeddings         |
|           | <------------------ | /v1/moderations ...    |
+-----------+  JSON: text + usage +------------------------+
     |
     +--> logs tokens, cost, errors, latency
```

---

## 💰 Cost Impact
- Billing is per token: input and output are priced separately, and output usually costs several times more than input.
- Illustrative gpt-4o-mini rates of $0.15 per 1M input and $0.60 per 1M output (verify current prices): a 500-in / 200-out call costs about $0.000195.
- Optimise: pick the smallest model that passes your evals, set `max_tokens`, shorten prompts, cache repeated queries, use the Batch API for non-urgent jobs, and log `usage` on every call.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| API key | Secret that identifies you | आपकी पहचान वाला secret |
| Endpoint | URL for one capability | किसी एक काम का URL |
| Client | SDK object that sends requests | Request भेजने वाला object |
| Usage | Token counts in a response | Response में token गिनती |
| Timeout | Max wait for a response | Response का max इंतज़ार |
| Embeddings | Text as number vectors | Text के number vectors |

---

## ⚡ 3-Line Summary
English: The OpenAI API gives pay-per-token access to chat, embeddings, audio, and moderation models. Use one reusable client, keep the key in the environment, and always handle errors and log `usage`. Pick the smallest model that meets quality needs.
Hindi: OpenAI API chat, embeddings, audio और moderation models का pay-per-token access देती है। एक reusable client रखो, key environment में रखो, errors handle करो और `usage` log करो। सबसे छोटा model चुनो जो quality पूरी करे।

---

## ➡️ Next Topic
**026. OpenAI Chat Completions API** — roles, messages, parameters, and the response object in detail.
