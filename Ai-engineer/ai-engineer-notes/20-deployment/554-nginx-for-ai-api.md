
---

# 554. Nginx for AI API
# हिंदी में: AI API के लिए Nginx

---

## 🔵 Simple Definition (English)
Nginx is a fast web server used as a **reverse proxy** in front of your FastAPI/uvicorn app. It terminates TLS, forwards requests, limits rates, and load balances. For AI APIs the critical settings are long timeouts and **disabled buffering** so streamed tokens (SSE) reach the user immediately.

## 🔵 सरल परिभाषा (Hindi)
Nginx एक तेज़ web server है जो आपके FastAPI/uvicorn app के आगे **reverse proxy** की तरह लगता है। यह TLS संभालता है, requests forward करता है, rate limit और load balancing करता है। AI APIs के लिए ज़रूरी settings हैं लंबे timeouts और **buffering बंद** ताकि streamed tokens (SSE) user तक तुरंत पहुँचें।

---

## 🔴 Problem it Solves
Exposing uvicorn directly means no TLS, no protection from slow clients, no rate limits, and no easy multi-instance routing. But default Nginx settings (60 s read timeout, response buffering) break LLM calls: slow answers get a 504 and streamed tokens arrive in one lump at the end.

## 🔴 यह क्यों बना? (Hindi)
uvicorn को सीधे expose करने पर TLS नहीं, slow clients से बचाव नहीं, rate limits नहीं और multi-instance routing मुश्किल। पर Nginx की default settings (60 s read timeout, response buffering) LLM calls तोड़ देती हैं: धीमे जवाब पर 504 और streamed tokens आख़िर में एक साथ आते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client connects over HTTPS to Nginx (TLS terminates here)
Step 2 → Nginx matches location /api/ and applies rate limit (limit_req)
Step 3 → proxy_pass forwards the request to an upstream (uvicorn on :8000)
Step 4 → For /stream routes: proxy_buffering off, so chunks pass through at once
Step 5 → proxy_read_timeout is raised (e.g. 120s) for slow LLM answers
Step 6 → Upstream block lists several app instances; Nginx round-robins
Step 7 → Passive health: max_fails/fail_timeout take a bad instance out
Step 8 → Access log records status, upstream time ($upstream_response_time)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client HTTPS से Nginx से जुड़ता है (TLS यहीं खत्म)
Step 2 → Nginx location /api/ match करके rate limit (limit_req) लगाता है
Step 3 → proxy_pass request को upstream (uvicorn :8000) तक भेजता है
Step 4 → /stream routes के लिए proxy_buffering off, chunks तुरंत निकलते हैं
Step 5 → proxy_read_timeout बढ़ाया जाता है (जैसे 120s)
Step 6 → Upstream block में कई instances; Nginx round-robin करता है
Step 7 → max_fails/fail_timeout खराब instance को हटाते हैं
Step 8 → Access log में status और $upstream_response_time दर्ज होता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: Two `tariff-api` containers sit behind Nginx on one VM. `/classify` takes up to 30 s for hard products, and `/classify/stream` streams the model's reasoning. Nginx enforces 10 requests/second per IP so one broker script cannot burn the LLM budget.

**Zomato-style**: A chat endpoint streams the assistant's reply word by word; with buffering off users see text appear immediately.

## 🟡 Real Example Hindi mein
**Tariff System**: एक VM पर Nginx के पीछे दो `tariff-api` containers। `/classify` कठिन products पर 30 s तक लेता है और `/classify/stream` model का reasoning stream करता है। Nginx हर IP के लिए 10 requests/second लागू करता है ताकि एक script LLM budget न जला दे।

**Zomato-style**: Chat endpoint reply शब्द-दर-शब्द stream करता है; buffering off होने से text तुरंत दिखता है।

---

## 💻 Code Example — Basic
```python
# Generate an nginx config from Python and sanity check it (offline). The config itself is the deliverable.
from textwrap import dedent  # keeps the template readable

NGINX_CONF: str = dedent("""
    upstream tariff_api {
        server 127.0.0.1:8000 max_fails=3 fail_timeout=10s;
        server 127.0.0.1:8001 max_fails=3 fail_timeout=10s;
        keepalive 32;
    }
    limit_req_zone $binary_remote_addr zone=perip:10m rate=10r/s;
    server {
        listen 80;
        server_name api.example.com;
        location / {
            limit_req zone=perip burst=20 nodelay;
            proxy_pass http://tariff_api;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_read_timeout 120s;
        }
        location /classify/stream {
            proxy_pass http://tariff_api;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_buffering off;
            proxy_cache off;
            proxy_read_timeout 300s;
        }
    }
""")


def check(conf: str) -> list[str]:
    """Return a list of problems found with simple string checks."""
    problems: list[str] = []  # collected problems
    if conf.count("{") != conf.count("}"):  # braces must balance
        problems.append("unbalanced braces")  # report
    if "proxy_buffering off" not in conf:  # needed for SSE
        problems.append("streaming route needs proxy_buffering off")  # report
    return problems  # result


if __name__ == "__main__":
    print(check(NGINX_CONF) or "config looks sane")  # prints "config looks sane"
    # In real use run: nginx -t   (validates syntax properly)
```

## 💻 Code Example — Advanced
```python
# FastAPI streaming endpoint designed to work behind Nginx, plus a client that measures time to first byte
import asyncio  # async sleep and loops
import time  # timing
from collections.abc import AsyncIterator  # type for async generators

import httpx  # async client
from fastapi import FastAPI  # framework
from fastapi.responses import StreamingResponse  # streaming response

app = FastAPI()  # app


async def fake_llm_tokens(prompt: str) -> AsyncIterator[str]:
    """Pretend LLM: yield tokens with a delay (replace with real streaming)."""
    for tok in f"HS code for {prompt} is 8517.13".split():  # split into word tokens
        await asyncio.sleep(0.2)  # simulate generation latency
        yield f"data: {tok}\n\n"  # Server-Sent Events format
    yield "data: [DONE]\n\n"  # end marker


@app.get("/classify/stream")  # streaming route
async def stream(q: str) -> StreamingResponse:
    return StreamingResponse(
        fake_llm_tokens(q),  # async generator
        media_type="text/event-stream",  # SSE content type
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},  # tells Nginx not to buffer
    )


async def time_to_first_byte(url: str) -> float:
    """Measure seconds until the first chunk arrives (should be small if buffering is off)."""
    start = time.perf_counter()  # start timer
    try:
        async with httpx.AsyncClient(timeout=60.0) as c:  # client
            async with c.stream("GET", url) as r:  # open stream
                r.raise_for_status()  # status check
                async for _ in r.aiter_bytes():  # first chunk
                    return time.perf_counter() - start  # elapsed
    except httpx.HTTPError as exc:  # connection or HTTP error
        raise RuntimeError(f"stream test failed: {exc}") from exc  # clear error
    return -1.0  # no data
```

---

## 🟠 FastAPI Integration
Run uvicorn on localhost behind Nginx. Tell uvicorn to trust the proxy headers so `request.client` and URLs are correct: `uvicorn main:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips="127.0.0.1"`. The `X-Accel-Buffering: no` response header (shown above) disables buffering per response without changing Nginx config.

```python
# Read the real client IP behind Nginx
from fastapi import FastAPI, Request  # framework

app = FastAPI()  # app


@app.get("/whoami")  # debug route
async def whoami(request: Request) -> dict[str, str | None]:
    # With --proxy-headers uvicorn fills request.client from X-Forwarded-For
    return {"ip": request.client.host if request.client else None}  # client IP
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `astream` and LangGraph's `astream_events` produce chunks you can forward as SSE. Nginx must not buffer them, and `proxy_read_timeout` must exceed the longest agent step.

```python
# Stream a LangChain chain through FastAPI (works behind Nginx with buffering off)
from fastapi.responses import StreamingResponse  # response
from langchain_openai import ChatOpenAI  # LLM

llm = ChatOpenAI(model="gpt-4o-mini")  # model


async def sse(prompt: str):  # async generator
    async for chunk in llm.astream(prompt):  # stream chunks
        yield f"data: {chunk.content}\n\n"  # SSE format

# return StreamingResponse(sse("HS code for laptop"), media_type="text/event-stream", headers={"X-Accel-Buffering": "no"})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Leaving the default 60 s timeout and buffering on
```python
# Wrong (nginx): default proxy_read_timeout 60s and proxy_buffering on
#   -> 504 on slow LLM calls, tokens arrive all at once
# Correct (nginx): proxy_read_timeout 120s; and for SSE locations: proxy_buffering off;
config_fix = "proxy_read_timeout 120s; proxy_buffering off;"
```

❌ Mistake 2: Not forwarding the client IP, then rate limiting the proxy itself
```python
# Wrong: app sees 127.0.0.1 for every user, so per-user limits hit everyone
# Correct: proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; and uvicorn --proxy-headers
header = "X-Forwarded-For"
```

---

## 🧠 Tricky Interview Question
**Q**: "Streaming works locally and in Docker, but in production the answer appears all at once after 20 seconds. Nothing is wrong in code. What is it?"

**Answer**: Something between the app and the browser is buffering: Nginx `proxy_buffering on` (default), a CDN, or gzip compression holding chunks. Check each hop. Fix: `proxy_buffering off` for the route or send `X-Accel-Buffering: no`, disable gzip for `text/event-stream`, and check that the load balancer or CDN supports streaming (and idle timeouts are large enough).

---

## ⚫ Interview Questions + Answers

Q1: What is a reverse proxy?
A1: A server that receives client requests and forwards them to backend servers, hiding them and adding TLS, caching, limits and balancing.

Q2: Why use Nginx in front of uvicorn?
A2: TLS termination, protection from slow clients, rate limiting, static files, multiple upstreams and better logging.

Q3: Which timeout breaks long LLM calls?
A3: `proxy_read_timeout` (default 60 s): the time between two reads from the upstream. Raise it for slow answers.

Q4: How do you rate limit by IP in Nginx?
A4: `limit_req_zone $binary_remote_addr zone=perip:10m rate=10r/s;` plus `limit_req zone=perip burst=20 nodelay;` in the location.

Q5: How do you make Nginx upstream failover work well for non-idempotent LLM POST calls?
A5: By default Nginx does not retry non-idempotent requests (POST) on other servers after they were sent, which protects against duplicate LLM spend. Keep that, or set `proxy_next_upstream` deliberately with `error timeout` only and use idempotency keys in the app, because a retry doubles token cost.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Self-hosting on a VM or container host
- You need TLS, limits, multiple upstreams
- You need to serve static frontend plus API

❌ Avoid when:
- A managed load balancer (ALB) already provides everything
- Platforms like Render or Railway already terminate TLS for you

---

## 📊 Visual Diagram
```
 Browser ──HTTPS──▶ ┌─────────────────────────┐
                    │ Nginx                   │
                    │ TLS · limit_req · logs  │
                    │ buffering off for /stream│
                    └──────┬─────────┬────────┘
                  round-robin       │
                           ▼        ▼
                   uvicorn :8000  uvicorn :8001
                           └───▶ LLM API
 timeouts: proxy_read_timeout 120s (stream: 300s)
```

---

## 💰 Cost Impact
Nginx itself is free and tiny (a small VM is enough), but its settings change LLM cost. Rate limiting protects the token budget: capping an abusive client at 10 req/s versus unlimited can save thousands of dollars of tokens. Avoid retry settings that duplicate POSTs: each duplicate resends the whole prompt, so 700 input tokens x retries adds up. Streaming does not change token price but improves perceived latency, so users do not resubmit. Optimise: per-IP and per-key limits, `max_tokens` in the app, caching at Nginx for idempotent GET lookups (for example HS code by ID), and gzip for JSON (not SSE).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reverse proxy | Server in front of backends | Backend के आगे का server |
| Upstream | Group of backend servers | Backend servers का समूह |
| proxy_buffering | Holds response before sending | Response रोककर भेजना |
| SSE | Server-Sent Events streaming | Server से streaming |
| limit_req | Request rate limiter | Request की दर सीमा |
| TLS termination | Decrypt HTTPS at the proxy | Proxy पर HTTPS खोलना |

---

## ⚡ 3-Line Summary
English: Nginx is a reverse proxy giving TLS, rate limits and load balancing for your FastAPI app. For AI, raise proxy_read_timeout and turn off buffering for streaming routes. Do not retry POSTs blindly, since each retry costs tokens.
Hindi: Nginx reverse proxy है जो FastAPI app को TLS, rate limits और load balancing देता है। AI के लिए proxy_read_timeout बढ़ाओ और streaming routes पर buffering बंद करो। POST को आँख बंद करके retry मत करो, हर retry में tokens लगते हैं।

---

## ➡️ Next Topic
**555. Load Balancer for AI** — spreading traffic across many instances with algorithms that suit slow, variable LLM requests.
