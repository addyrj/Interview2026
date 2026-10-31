---

# 288. API Call Tool
# हिंदी में: API Call Tool (LLM से external API call)

---

## 🔵 Simple Definition (English)
An API call tool lets an LLM trigger an HTTP request to an external service (exchange rates, weather, shipping, internal microservice) through a function you control. The model picks the tool and arguments; your code makes the request, handles timeouts and errors, and returns a trimmed JSON result.

## 🔵 सरल परिभाषा (Hindi)
API call tool से LLM किसी external service (exchange rate, weather, shipping, internal microservice) को HTTP request भेजने वाला function चला सकता है। Model tool और arguments चुनता है; आपका code request करता है, timeout और errors संभालता है और छोटा JSON result लौटाता है।

---

## 🔴 Problem it Solves
An LLM is frozen in time and cannot act on the world. It does not know today's USD to INR rate or a parcel's live status. Letting it generate URLs freely is risky: SSRF (hitting internal addresses like `http://169.254.169.254`), leaked API keys, unbounded responses and hanging requests.

## 🔴 यह क्यों बना? (Hindi)
LLM पुराने data पर चलता है; आज का USD-INR rate या parcel status नहीं जानता। Model को खुद URL बनाने देना खतरनाक है: SSRF (internal addresses पर हमला), API key leak, बहुत बड़े responses और अटकी requests। इसलिए **allowlisted, timeout वाला API tool** चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a tool with typed args (not a free-form URL)
Step 2 → LLM returns tool_call: get_exchange_rate(base="USD", target="INR")
Step 3 → Code builds the URL itself from an allowlisted base URL
Step 4 → httpx request with timeout, API key from env (never from the LLM)
Step 5 → Check status code, parse JSON, keep only needed fields
Step 6 → Return compact JSON (or error payload) as role="tool"
Step 7 → LLM answers; tokens = tool schema + call + trimmed JSON + answer
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Typed arguments वाला tool बनाओ (free URL नहीं)
Step 2 → LLM tool_call देता है: get_exchange_rate(base="USD", target="INR")
Step 3 → Code खुद allowlisted base URL से URL बनाता है
Step 4 → httpx request: timeout के साथ, API key env से (LLM से कभी नहीं)
Step 5 → Status check, JSON parse, सिर्फ़ ज़रूरी fields रखो
Step 6 → Compact JSON role="tool" में लौटाओ
Step 7 → LLM जवाब देता है; tokens = schema + call + trimmed JSON + answer
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs value must be converted from USD to INR using the day's exchange rate. The LLM calls `get_exchange_rate("USD", "INR")` against the central bank API, then the calculator tool computes duty on the INR value.

**Zomato AI**: "Is my rider close?" calls the internal `GET /orders/{id}/tracking` service and returns `{eta_min: 7}`.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs value को USD से INR में बदलना है। LLM `get_exchange_rate("USD", "INR")` call करता है, फिर calculator tool INR value पर duty निकालता है।

**Zomato AI**: "Rider कितनी दूर है?" → internal `GET /orders/{id}/tracking` call, जवाब `{eta_min: 7}`।

---

## 💻 Code Example — Basic
```python
# Basic API tool using urllib only (stdlib) with a mocked transport so it runs offline
import json                                  # parse/serialise JSON
from typing import Any
from urllib.parse import urlparse            # to validate the host

ALLOWED_HOSTS = {"api.exchangerate.example"}  # only these hosts may be called

def fake_http_get(url: str, timeout: float) -> dict[str, Any]:
    """Stand-in for a real HTTP call so the demo works without internet."""
    return {"base": "USD", "rates": {"INR": 83.2, "EUR": 0.92}, "date": "2026-10-28"}

def get_exchange_rate(base: str, target: str) -> str:
    """Tool: returns the exchange rate as a JSON string."""
    url = f"https://api.exchangerate.example/latest?base={base}"   # URL built by OUR code
    host = urlparse(url).hostname                                  # extract host name
    if host not in ALLOWED_HOSTS:                                  # SSRF protection
        return json.dumps({"ok": False, "error": "host not allowed"})
    if not (base.isalpha() and len(base) == 3 and target.isalpha() and len(target) == 3):
        return json.dumps({"ok": False, "error": "currency must be 3 letters"})
    try:
        data = fake_http_get(url, timeout=5.0)                     # real code: httpx.get(...)
        rate = data["rates"][target.upper()]                       # keep only what we need
        return json.dumps({"ok": True, "base": base.upper(), "target": target.upper(), "rate": rate})
    except KeyError:
        return json.dumps({"ok": False, "error": f"unknown currency {target}"})

print(get_exchange_rate("USD", "INR"))       # {"ok": true, ... "rate": 83.2}
print(get_exchange_rate("USD", "XXX"))       # unknown currency
print(get_exchange_rate("US", "INR"))        # validation error
```

## 💻 Code Example — Advanced
```python
# Production: async httpx + retries + trimmed output + tool loop
import asyncio, json, os
from typing import Any
import httpx                                   # pip install httpx
from openai import AsyncOpenAI

client = AsyncOpenAI()
BASE_URL = "https://api.exchangerate.host"      # fixed base; the LLM never controls it
API_KEY = os.environ.get("FX_API_KEY", "")      # secret stays server-side
MAX_BYTES = 20_000                              # refuse huge responses

async def get_exchange_rate(base: str, target: str) -> dict[str, Any]:
    """Async tool with timeout, retry on 5xx, and structured errors."""
    params = {"base": base.upper(), "symbols": target.upper(), "access_key": API_KEY}
    timeout = httpx.Timeout(5.0, connect=2.0)   # total 5s, connect 2s
    async with httpx.AsyncClient(timeout=timeout) as http:
        for attempt in range(3):                # up to 3 tries
            try:
                resp = await http.get(f"{BASE_URL}/latest", params=params)
                if resp.status_code >= 500:     # server problem: retry
                    await asyncio.sleep(2 ** attempt * 0.3)
                    continue
                if resp.status_code >= 400:     # client problem: do not retry
                    return {"ok": False, "error": f"HTTP {resp.status_code}"}
                if len(resp.content) > MAX_BYTES:
                    return {"ok": False, "error": "response too large"}
                rate = resp.json()["rates"][target.upper()]   # trim to one field
                return {"ok": True, "rate": rate, "base": base.upper(), "target": target.upper()}
            except (httpx.TimeoutException, httpx.TransportError):
                await asyncio.sleep(2 ** attempt * 0.3)       # network glitch: retry
            except (KeyError, ValueError):
                return {"ok": False, "error": "unexpected response format"}
    return {"ok": False, "error": "service unavailable after 3 attempts"}

TOOLS: list[dict[str, Any]] = [{
    "type": "function",
    "function": {
        "name": "get_exchange_rate",
        "description": "Live exchange rate between two 3-letter currency codes.",
        "parameters": {
            "type": "object",
            "properties": {
                "base": {"type": "string", "description": "e.g. USD"},
                "target": {"type": "string", "description": "e.g. INR"},
            },
            "required": ["base", "target"],
        },
    },
}]

async def ask(question: str) -> str:
    """One tool-calling conversation."""
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]
    for _ in range(3):
        resp = await client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=TOOLS)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content or ""
        messages.append(msg)
        # run independent calls in parallel with gather
        results = await asyncio.gather(*[
            get_exchange_rate(**json.loads(c.function.arguments)) for c in msg.tool_calls
        ], return_exceptions=True)
        for call, res in zip(msg.tool_calls, results):
            payload = {"ok": False, "error": str(res)} if isinstance(res, Exception) else res
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(payload)})
    return "Stopped after 3 rounds."
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class FxQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=500)

@app.post("/fx/ask")
async def fx_ask(body: FxQuestion) -> dict:
    """Chat endpoint where the LLM may call the FX API."""
    try:
        return {"answer": await asyncio.wait_for(ask(body.question), timeout=20)}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="timed out")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

@app.get("/fx/{base}/{target}")
async def fx(base: str, target: str) -> dict:
    """Plain endpoint using the same tool function (no LLM)."""
    return await get_exchange_rate(base, target)
```
Tip: FastAPI itself is often the "external API" the agent calls, so reuse the same service function in both places.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

@tool
async def fx_rate(base: str, target: str) -> str:
    """Live exchange rate between two currency codes like USD and INR."""
    return json.dumps(await get_exchange_rate(base, target))   # async tools are supported

agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), [fx_rate])
# await agent.ainvoke({"messages": [("user", "Convert 500 USD to INR")]})
```
LangChain also has `requests` toolkits and OpenAPI toolkits that turn a whole OpenAPI spec into tools, which is convenient but exposes many endpoints, so allowlist carefully.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Letting the LLM pass a full URL
✅ Correct: Typed arguments, fixed base URL, host allowlist.

```python
# Wrong — SSRF risk, model may call http://localhost:8080/admin:
def http_get(url: str) -> str:
    return requests.get(url).text
# Right:
def get_exchange_rate(base: str, target: str) -> dict: ...
```

❌ Mistake 2: No timeout and no response trimming
✅ Correct: Always set a timeout and return only needed fields.

```python
# Wrong — can hang forever and dump 200KB into the prompt:
return requests.get(url).text
# Right:
data = httpx.get(url, timeout=5).json()
return {"rate": data["rates"]["INR"]}
```

❌ Mistake 3: Putting API keys in the prompt or tool args. Keep secrets in env/server code.

---

## 🧠 Tricky Interview Question

**Q**: "Your agent calls a payment-refund API tool. A network timeout happens after the request was sent. The retry refunds twice. How do you prevent it?"

**Answer**: Use idempotency keys. Generate a unique key per logical operation (e.g. hash of order_id + action) and send it in an `Idempotency-Key` header; the server returns the original result on duplicates. Also: do not auto-retry non-idempotent calls (POST) without a key, require human confirmation for money-moving tools, and log every call with its key.

---

## ⚫ Interview Questions + Answers

Q1: Why use typed args instead of letting the model send a URL? (Easy)
A1: A free URL enables SSRF, data exfiltration and calls to unintended endpoints. Typed args with a fixed base URL give control and validation.

Q2: Where should API keys live? (Easy)
A2: Server-side in environment variables or a secret manager. Never in prompts, tool arguments or model-visible text.

Q3: Which errors should be retried? (Medium)
A3: Timeouts, connection errors, 429 (honour `Retry-After`) and 5xx with exponential backoff. Not 4xx such as 400, 401, 404, because retrying cannot fix them. Return the error to the LLM instead.

Q4: How do you handle large API responses? (Medium)
A4: Cap bytes, parse JSON, return only needed fields, paginate or summarise. Large payloads waste tokens and can overflow context.

Q5: How do you make API tools safe at scale? (Hard)
A5: Host allowlist and egress firewall, per-tool timeout and circuit breaker, rate limits per user, idempotency keys, schema validation of responses (pydantic), audit logs, secrets management, confirmation step for side-effect tools, and cached GET results to reduce calls and tokens.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data is live (rates, status, weather)
- Action must happen in another system
- You have stable, documented APIs

❌ Avoid when:
- Data rarely changes (cache or embed it)
- API is slow and the user needs instant replies (pre-fetch)
- Call has irreversible side effects with no approval step

---

## 📊 Visual Diagram
```
 LLM ──tool_call(base,target)──► Tool wrapper ──► allowlist check
                                     │                │
                                     │ build URL      ▼
                                     │ add API key  External API
                                     │ timeout 5s     │
                                     ▼                │
                          trim JSON  ◄────────────────┘
                                     │
 LLM ◄──────── {"rate": 83.2} ───────┘
```

---

## 💰 Cost Impact
Raw API responses can be thousands of tokens; trimming to 2-3 fields makes them about 30 tokens. Each tool round trip re-sends the history, so 3 rounds cost roughly 3x input tokens. Parallel tool calls save latency but not tokens.

Optimize: trim responses, cache (e.g. FX rate for 1 hour), avoid chatty multi-step API sequences by writing one composite tool, and keep descriptions short.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SSRF | Server tricked into calling internal URLs | Server से internal URL call करवाना |
| Allowlist | Approved hosts only | अनुमत hosts की सूची |
| Idempotency key | Unique key so retries do not repeat effects | दोहराव रोकने वाली key |
| Timeout | Max wait time | अधिकतम इंतज़ार |
| Backoff | Increasing delay between retries | Retry में बढ़ता delay |
| Circuit breaker | Stop calling a failing service | खराब service पर call बंद |

---

## ⚡ 3-Line Summary
English: An API call tool lets the LLM reach live external data through typed, validated functions. Fix the base URL, allowlist hosts, set timeouts, hide keys and trim responses. Use idempotency keys for anything with side effects.
Hindi: API call tool से LLM live external data तक पहुँचता है, typed और validated functions के ज़रिए। Base URL fixed रखो, hosts allowlist करो, timeout लगाओ, keys छुपाओ और response trim करो। Side-effect वाले calls के लिए idempotency key ज़रूर।

---

## ➡️ Next Topic
**289. File Read/Write Tool** — giving the LLM safe access to files (path sandboxing, size limits).
