---

# 041. Ollama (Local Models)
# हिंदी में: Ollama (Local Models)

---

## 🔵 Simple Definition (English)
Ollama is a tool that downloads and runs open LLMs (Llama, Mistral, Qwen, Gemma and others) on your own computer or server. It starts a local server on `http://localhost:11434` with its own REST API and an OpenAI-compatible endpoint at `/v1`. Your data stays on your machine and there is no per-token fee.

## 🔵 सरल परिभाषा (Hindi)
Ollama एक tool है जो open LLMs (Llama, Mistral, Qwen, Gemma आदि) को आपके अपने computer या server पर download करके चलाता है। यह `http://localhost:11434` पर local server शुरू करता है, जिसकी अपनी REST API है और `/v1` पर OpenAI-compatible endpoint भी। आपका data आपकी machine पर रहता है और per-token fee नहीं लगती।

---

## 🔴 Problem it Solves
Cloud APIs mean sending data to a third party, paying per token, and needing internet. Some tariff, legal, or health documents cannot leave the company network. Developers also want free local experiments and offline demos. Ollama makes running a model as easy as `ollama run llama3.2`.

## 🔴 यह क्यों बना? (Hindi)
Cloud APIs का मतलब है data तीसरे पक्ष को भेजना, per token भुगतान और internet की ज़रूरत। कुछ tariff, legal या health documents company network से बाहर नहीं जा सकते। Developers को free local experiments और offline demos भी चाहिए। Ollama model चलाना `ollama run llama3.2` जितना आसान बना देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install Ollama (ollama.com); it runs a background server on port 11434
Step 2 → Pull a model: ollama pull llama3.2   (downloads quantised weights)
Step 3 → Test in the terminal: ollama run llama3.2
Step 4 → From Python: pip install ollama ; ollama.chat(model=..., messages=[...])
Step 5 → Or use the OpenAI client with base_url="http://localhost:11434/v1", api_key="ollama"
Step 6 → The model loads into RAM/VRAM on first request and stays warm for a while (keep_alive)
Step 7 → Response comes from CPU/GPU on your machine; speed depends on hardware and model size
Step 8 → Options such as temperature and num_ctx (context length) are set per request
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Ollama install करो (ollama.com); यह port 11434 पर background server चलाता है
Step 2 → Model pull करो: ollama pull llama3.2   (quantised weights download होते हैं)
Step 3 → Terminal में test करो: ollama run llama3.2
Step 4 → Python से: pip install ollama ; ollama.chat(model=..., messages=[...])
Step 5 → या OpenAI client base_url="http://localhost:11434/v1", api_key="ollama" के साथ
Step 6 → पहली request पर model RAM/VRAM में load होता है और कुछ देर warm रहता है (keep_alive)
Step 7 → Response आपकी machine की CPU/GPU से आता है; speed hardware और model size पर निर्भर
Step 8 → temperature और num_ctx (context length) जैसे options हर request में सेट होते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs agency has confidential shipment data that cannot go to external clouds. They deploy Ollama on an internal GPU server with a mid-size open model and run the classifier fully on-premises. Development laptops use a small model for tests, so CI needs no API keys or cost.

**Zomato AI**: Developers run a small local model for prototyping the chatbot without spending API money.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: एक customs agency के पास गोपनीय shipment data है जो बाहरी clouds पर नहीं जा सकता। वे internal GPU server पर mid-size open model के साथ Ollama deploy करते हैं और classifier पूरी तरह on-premises चलाते हैं। Development laptops tests के लिए छोटा model use करते हैं, इसलिए CI को API keys या cost नहीं चाहिए।

**Zomato AI**: Developers chatbot prototype करने के लिए छोटा local model चलाते हैं, API पर पैसा खर्च किए बिना।

---

## 💻 Code Example — Basic
```python
# Basic Ollama call (needs: Ollama installed and running, `ollama pull llama3.2`, pip install ollama)
import ollama                                    # official Python client

MODEL = "llama3.2"                               # any model you have pulled

try:
    response = ollama.chat(
        model=MODEL,                             # local model name
        messages=[
            {"role": "system", "content": "Return only the 6-digit HS code."},
            {"role": "user", "content": "lithium power bank"},
        ],
        options={"temperature": 0, "num_predict": 20},   # num_predict caps output tokens
    )
    print(response["message"]["content"])        # answer text (response.message.content also works)
    print("in:", response.get("prompt_eval_count"), "out:", response.get("eval_count"))  # token counts
except ollama.ResponseError as exc:              # e.g. model not found -> pull it first
    print("Ollama error:", exc.error, exc.status_code)
except Exception as exc:                         # server not running / connection refused
    print("Is Ollama running? ", exc)
```

## 💻 Code Example — Advanced
```python
# Production-style: OpenAI-compatible access, async, streaming, health check, fallback
import asyncio                                           # async runner
import logging                                           # logs
import os                                                # env
from typing import Optional                              # type hints

import httpx                                             # health check (installed with openai)
from openai import AsyncOpenAI, OpenAIError              # OpenAI-compatible client

logger = logging.getLogger(__name__)                     # logger
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "llama3.2")

local = AsyncOpenAI(base_url=f"{OLLAMA_URL}/v1", api_key="ollama",   # key is ignored but required
                    timeout=120.0, max_retries=1)        # local models can be slow on first load
cloud = AsyncOpenAI(max_retries=2, timeout=30.0)         # optional cloud fallback (needs OPENAI_API_KEY)


async def ollama_up() -> bool:
    try:
        async with httpx.AsyncClient(timeout=2.0) as h:
            r = await h.get(f"{OLLAMA_URL}/api/tags")    # lists installed models
            return r.status_code == 200
    except httpx.HTTPError:
        return False


async def classify(product: str, allow_cloud: bool = False) -> Optional[str]:
    msgs = [{"role": "system", "content": "Return only the 6-digit HS code."},
            {"role": "user", "content": product}]
    if await ollama_up():
        try:
            r = await local.chat.completions.create(
                model=LOCAL_MODEL, messages=msgs, temperature=0, max_tokens=20)
            return r.choices[0].message.content
        except OpenAIError as exc:
            logger.error("local model error: %s", exc)
    if allow_cloud:                                      # only if policy allows data to leave
        try:
            r = await cloud.chat.completions.create(
                model="gpt-4o-mini", messages=msgs, temperature=0, max_tokens=20)
            return r.choices[0].message.content
        except OpenAIError as exc:
            logger.error("cloud fallback failed: %s", exc)
    return None


if __name__ == "__main__":
    print(asyncio.run(classify("lithium power bank")))
```

---

## 🟠 FastAPI Integration
Run FastAPI and Ollama on the same private network. Add a readiness check so the load balancer knows when the model server is up.

```python
import os                                          # env
import httpx                                       # health check
from fastapi import FastAPI, HTTPException         # framework
from openai import AsyncOpenAI, OpenAIError        # OpenAI-compatible client
from pydantic import BaseModel                     # models

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("LOCAL_MODEL", "llama3.2")
app = FastAPI()                                    # app
client = AsyncOpenAI(base_url=f"{OLLAMA_URL}/v1", api_key="ollama", timeout=120.0)


class Body(BaseModel):
    product: str


@app.get("/ready")
async def ready() -> dict:
    async with httpx.AsyncClient(timeout=2.0) as h:
        try:
            r = await h.get(f"{OLLAMA_URL}/api/tags")
            r.raise_for_status()
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Model server down")
    return {"status": "ok"}


@app.post("/classify")
async def classify(b: Body) -> dict:
    try:
        r = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": "Return only the 6-digit HS code."},
                      {"role": "user", "content": b.product}],
            temperature=0, max_tokens=20)
    except OpenAIError:
        raise HTTPException(status_code=502, detail="Local model error")
    return {"hs_code": (r.choices[0].message.content or "").strip(), "model": MODEL}
```

---

## 🔗 LangChain / LangGraph Connection
`langchain-ollama` provides `ChatOllama` and `OllamaEmbeddings`. Local embeddings plus a local chat model give a fully offline RAG stack. Note that smaller local models may need simpler prompts and may handle tool calling less reliably.

```python
from langchain_ollama import ChatOllama, OllamaEmbeddings   # pip install langchain-ollama
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOllama(model="llama3.2", temperature=0, num_ctx=4096)   # num_ctx sets context window
emb = OllamaEmbeddings(model="nomic-embed-text")                  # after: ollama pull nomic-embed-text

chain = ChatPromptTemplate.from_template("HS code for {product}? Digits only.") | llm
# print(chain.invoke({"product": "power bank"}).content)
# vec = emb.embed_query("power bank")
# LangGraph: use `llm` in nodes exactly like any other chat model.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to pull the model
✅ Correct: Run `ollama pull <model>` first, or you get a "model not found" error.

```python
# Wrong — model not downloaded -> ResponseError 404
ollama.chat(model="llama3.2", messages=msgs)
# Right (once, in a shell): ollama pull llama3.2
```

❌ Mistake 2: Leaving the default context length for long RAG prompts
✅ Correct: Ollama's default `num_ctx` is small (a few thousand tokens), so long prompts are silently truncated. Set `num_ctx` explicitly (more memory needed).

❌ Mistake 3: Expecting GPT-4-level quality from a small local model
✅ Correct: Test on your eval set; pick a larger or better-suited model, or route hard cases to the cloud.

❌ Mistake 4: Exposing the Ollama port to the internet
✅ Correct: It has no authentication; keep it on localhost or behind a private network/proxy with auth.

---

## 🧠 Tricky Interview Question

**Q**: "Your local Ollama RAG gives worse answers than the cloud version even with the same retrieved chunks, and long prompts seem ignored. What do you check?"

**Answer**: (1) Context truncation: the default `num_ctx` may be far smaller than your prompt, so the start (instructions or early chunks) is cut. Set `num_ctx` to fit the prompt and verify with `prompt_eval_count`. (2) Quantisation and model size: a 7B/8B 4-bit model is much weaker than a frontier model; try a larger model or less aggressive quantisation. (3) Prompt format: local models are more sensitive to instructions; simplify and add examples. (4) Temperature and stop settings. (5) Hardware: running out of VRAM can force slow CPU offloading and timeouts. Measure with an eval set before blaming retrieval.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What does Ollama do?
A1: It downloads and serves open LLMs locally with a simple CLI and HTTP API.

Q2: [Easy] Which port and endpoint?
A2: Port 11434. Native API at `/api/chat`, `/api/generate`; OpenAI-compatible at `/v1/chat/completions`.

Q3: [Medium] Why use local models?
A3: Privacy and data control, no per-token cost, offline use, predictable latency inside your network, and easy experimentation. Trade-offs: hardware cost, lower quality for small models, and you manage scaling.

Q4: [Medium] What is quantisation?
A4: Storing model weights with fewer bits (for example 4-bit) to cut memory and speed up inference, at a small quality cost.

Q5: [Hard] How would you serve many concurrent users from local models?
A5: Ollama is great for dev and small deployments; for high concurrency use a serving engine built for batching (such as vLLM or TGI) on GPUs, or configure Ollama's parallel request settings with enough VRAM. Add a queue, timeouts, health checks, autoscaling, and a cloud fallback if policy allows.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Sensitive data must stay in-house
- Offline demos, dev/test without API cost
- Low-stakes, high-volume tasks with a small model

❌ Avoid when:
- You need frontier quality or very long contexts
- No GPU and strict latency targets
- High concurrency without proper serving infrastructure

---

## 📊 Visual Diagram
```
 Your app (FastAPI)
      |  HTTP  localhost:11434
      v
 +--------------------- Ollama ----------------------+
 |  /api/chat   /v1/chat/completions (OpenAI-style)  |
 |  model: llama3.2 (quantised) in RAM / VRAM        |
 +---------------------------------------------------+
      |
   CPU / GPU on YOUR machine  -->  data never leaves

 Cloud API:  app --internet--> provider (pay per token)
 Ollama:     app --localhost-> your hardware (pay for hardware)
```

---

## 💰 Cost Impact
- No per-token fee, but you pay for hardware (GPU server or laptop), power, and maintenance. Token usage is reported (`prompt_eval_count`, `eval_count`) and is useful for capacity planning, not billing.
- Break-even: steady high volume often favours self-hosting; spiky or low volume favours cloud APIs.
- Optimise: pick the smallest model that passes evals, quantise, set `num_predict`, reuse loaded models (`keep_alive`), batch work, and send only hard cases to a paid API.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ollama | Local LLM runner | Local LLM चलाने वाला tool |
| Quantisation | Fewer bits per weight | कम bits वाले weights |
| num_ctx | Context window size setting | Context window का size setting |
| keep_alive | How long model stays loaded | Model कितनी देर loaded रहे |
| On-premises | Runs in your own infrastructure | अपने infrastructure पर |
| VRAM | GPU memory | GPU की memory |

---

## ⚡ 3-Line Summary
English: Ollama runs open LLMs locally with a simple API on port 11434, including an OpenAI-compatible `/v1` endpoint. It gives privacy and zero per-token cost, but you manage hardware and accept lower quality from small models. Set `num_ctx` explicitly and protect the port.
Hindi: Ollama port 11434 पर simple API के साथ open LLMs locally चलाता है, जिसमें OpenAI-compatible `/v1` endpoint भी है। इससे privacy और zero per-token cost मिलती है, लेकिन hardware आपको संभालना पड़ता है और छोटे models की quality कम होती है। `num_ctx` साफ़ तौर पर set करो और port को सुरक्षित रखो।

---

## ➡️ Next Topic
**042. LiteLLM — Unified API** — one interface and a gateway for OpenAI, Claude, Gemini, Groq, Ollama, and more.
