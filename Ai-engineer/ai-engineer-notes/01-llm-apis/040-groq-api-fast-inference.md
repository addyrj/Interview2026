---

# 040. Groq API (Fast Inference)
# हिंदी में: Groq API (तेज़ Inference)

---

## 🔵 Simple Definition (English)
Groq is a company that runs open-weight models (such as Llama and others) on its own custom inference chips (LPUs), giving very high tokens-per-second and low latency. Its API is OpenAI-compatible: you can use the `groq` Python package or the normal OpenAI client with Groq's base URL. Groq hosts models; it does not train them.

## 🔵 सरल परिभाषा (Hindi)
Groq एक कंपनी है जो open-weight models (जैसे Llama आदि) को अपनी custom inference chips (LPUs) पर चलाती है, जिससे tokens-per-second बहुत ज़्यादा और latency बहुत कम मिलती है। इसकी API OpenAI-compatible है: आप `groq` Python package या Groq के base URL के साथ सामान्य OpenAI client use कर सकते हैं। Groq models host करता है, train नहीं करता।

---

## 🔴 Problem it Solves
Real-time apps (voice agents, autocomplete, interactive classification) suffer when LLM latency is seconds. Large GPU-hosted models are often slow per token. Groq's hardware focuses on fast token generation, so open models answer in a fraction of the usual time, often at low prices.

## 🔴 यह क्यों बना? (Hindi)
Real-time apps (voice agents, autocomplete, interactive classification) को तब दिक्कत होती है जब LLM latency seconds में होती है। बड़े GPU-hosted models अक्सर प्रति token धीमे होते हैं। Groq का hardware तेज़ token generation पर केंद्रित है, इसलिए open models सामान्य समय के एक हिस्से में जवाब देते हैं, अक्सर कम price पर।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a key at the Groq console; set GROQ_API_KEY
Step 2 → pip install groq   (or use the openai package with base_url)
Step 3 → client = Groq()    -- same shape as OpenAI(): client.chat.completions.create(...)
Step 4 → Pick a hosted model id (for example a Llama model); list with client.models.list()
Step 5 → Send messages, get choices[0].message.content and usage
Step 6 → Rate limits are per model (RPM, TPM, daily); 429s need backoff
Step 7 → Use streaming for the best "instant" feel
Step 8 → Keep an OpenAI/Claude fallback for models or features Groq does not host
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Groq console से key बनाओ; GROQ_API_KEY set करो
Step 2 → pip install groq   (या openai package को base_url के साथ use करो)
Step 3 → client = Groq()    -- OpenAI() जैसा ही: client.chat.completions.create(...)
Step 4 → Hosted model id चुनो (जैसे कोई Llama model); client.models.list() से देखो
Step 5 → messages भेजो, choices[0].message.content और usage पाओ
Step 6 → Rate limits हर model के लिए हैं (RPM, TPM, daily); 429 पर backoff चाहिए
Step 7 → "तुरंत" वाले feel के लिए streaming use करो
Step 8 → जो models/features Groq पर नहीं हैं उनके लिए OpenAI/Claude fallback रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A live "type-ahead" widget suggests HS headings while the broker types the product name. It needs answers in under a second, so it uses a small open model on Groq with `max_tokens=30`. The final legally-binding classification still runs through a stronger model plus a human review step.

**Zomato AI**: A voice assistant for ordering needs fast replies; Groq-hosted models keep the conversation natural.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: Live "type-ahead" widget broker के product name type करते समय HS headings सुझाता है। जवाब एक सेकंड से कम में चाहिए, इसलिए `max_tokens=30` के साथ Groq पर छोटा open model use होता है। अंतिम कानूनी classification फिर भी मज़बूत model और human review से गुज़रता है।

**Zomato AI**: Order के लिए voice assistant को तेज़ जवाब चाहिए; Groq-hosted models बातचीत को natural रखते हैं।

---

## 💻 Code Example — Basic
```python
# Basic Groq call (needs: pip install groq, and GROQ_API_KEY)
import os                                        # env access
from groq import Groq                            # Groq SDK (OpenAI-shaped)

if not os.getenv("GROQ_API_KEY"):                # fail early
    raise SystemExit("Set GROQ_API_KEY first")

client = Groq()                                  # reads GROQ_API_KEY from env
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")   # check the console for current models

r = client.chat.completions.create(
    model=MODEL,                                 # hosted open model id
    messages=[
        {"role": "system", "content": "Return only the 6-digit HS code."},
        {"role": "user", "content": "lithium power bank"},
    ],
    temperature=0,                               # deterministic
    max_tokens=20,                               # tiny output = very fast
)
print(r.choices[0].message.content)              # answer
print(r.usage.prompt_tokens, r.usage.completion_tokens)   # token usage

# Alternative: the OpenAI client works too, only base_url and key change
# from openai import OpenAI
# oc = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
```

## 💻 Code Example — Advanced
```python
# Production: async Groq with streaming, retry on 429, and fallback to OpenAI
import asyncio                                           # async runner
import logging                                           # logs
import os                                                # env
from typing import Optional                              # type hints

import groq                                              # error classes
from groq import AsyncGroq                               # async client
from openai import AsyncOpenAI, OpenAIError              # fallback provider

logger = logging.getLogger(__name__)                     # logger
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
gclient = AsyncGroq(max_retries=2, timeout=15.0)         # short timeout: Groq is fast
oclient = AsyncOpenAI(max_retries=2, timeout=30.0)       # fallback


async def fast_classify(product: str) -> Optional[str]:
    msgs = [{"role": "system", "content": "Return only the 6-digit HS code."},
            {"role": "user", "content": product}]
    try:
        r = await gclient.chat.completions.create(
            model=GROQ_MODEL, messages=msgs, temperature=0, max_tokens=20)
        return r.choices[0].message.content
    except (groq.RateLimitError, groq.APIConnectionError, groq.InternalServerError) as exc:
        logger.warning("groq unavailable (%s), falling back", type(exc).__name__)
    except groq.APIStatusError as exc:                   # 4xx like bad model id: do not fall back blindly
        logger.error("groq status %s: %s", exc.status_code, exc.message)
        return None
    try:                                                 # fallback path
        r2 = await oclient.chat.completions.create(
            model="gpt-4o-mini", messages=msgs, temperature=0, max_tokens=20)
        return r2.choices[0].message.content
    except OpenAIError as exc:
        logger.error("fallback failed: %s", exc)
        return None


async def stream_demo(prompt: str) -> None:
    stream = await gclient.chat.completions.create(
        model=GROQ_MODEL, messages=[{"role": "user", "content": prompt}],
        stream=True, max_tokens=150)
    async for chunk in stream:                           # same chunk shape as OpenAI
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()


if __name__ == "__main__":
    print(asyncio.run(fast_classify("lithium power bank")))
```

---

## 🟠 FastAPI Integration
Use Groq for low-latency endpoints. Because the API is OpenAI-shaped, the route looks the same as with OpenAI.

```python
import os                                          # env
import groq                                        # errors
from groq import AsyncGroq                         # client
from fastapi import FastAPI, HTTPException         # framework
from pydantic import BaseModel, Field              # models

app = FastAPI()                                    # app
client = AsyncGroq(max_retries=1, timeout=10.0)    # fail fast for interactive use
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


class Typing(BaseModel):
    partial: str = Field(min_length=2, max_length=100)   # what the user has typed so far


@app.post("/suggest")
async def suggest(t: Typing) -> dict:
    try:
        r = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": "Suggest 3 HS headings, one per line."},
                      {"role": "user", "content": t.partial}],
            temperature=0.2, max_tokens=60)
    except groq.RateLimitError:
        raise HTTPException(status_code=429, detail="Busy", headers={"Retry-After": "2"})
    except groq.APIError:
        raise HTTPException(status_code=502, detail="Suggestion service unavailable")
    return {"suggestions": (r.choices[0].message.content or "").splitlines()}
```

---

## 🔗 LangChain / LangGraph Connection
`langchain-groq` provides `ChatGroq`. It supports tool calling and streaming for models that allow it, and plugs into LCEL and LangGraph. Mix it with other providers via `with_fallbacks`.

```python
from langchain_groq import ChatGroq                     # pip install langchain-groq
from langchain_openai import ChatOpenAI                 # fallback provider

fast = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_tokens=50)   # reads GROQ_API_KEY
safe = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=50)

llm = fast.with_fallbacks([safe])                       # use Groq first, OpenAI if it fails
# print(llm.invoke("HS code for a power bank? digits only").content)

# LangGraph: put `fast` in latency-sensitive nodes (routing, classification)
# and a stronger model in the final-answer node.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Assuming Groq hosts every model or the same model names as OpenAI
✅ Correct: Use Groq's own model ids and list them.

```python
# Wrong
client.chat.completions.create(model="gpt-4o-mini", ...)   # 404 on Groq
# Right
client.chat.completions.create(model="llama-3.3-70b-versatile", ...)
```

❌ Mistake 2: Ignoring that limits differ per model
✅ Correct: Check the console for each model's RPM/TPM/daily limits; free tiers are tight.

❌ Mistake 3: Using a fast model for tasks that need strong reasoning without testing
✅ Correct: Fast does not mean accurate. Evaluate quality, then decide.

❌ Mistake 4: Sending sensitive data without checking data policies
✅ Correct: Read the provider's data-retention terms.

---

## 🧠 Tricky Interview Question

**Q**: "Groq is much faster than your current provider. Why not move everything to Groq?"

**Answer**: Speed is one axis. Check (1) quality: the hosted open models may score lower than frontier models on your hard tasks; (2) feature coverage: structured outputs, tool-calling reliability, vision, embeddings, and context length differ; (3) rate limits and capacity for your peak load; (4) model lifecycle: hosted models are deprecated and replaced; (5) compliance and data residency; (6) vendor concentration risk. Best practice: use Groq for latency-critical, simpler steps, keep a stronger model for hard steps, and maintain a fallback provider. Decide with latency percentiles and accuracy from your own eval set.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is Groq known for?
A1: Very fast inference of open models on custom LPU hardware.

Q2: [Easy] Is the Groq API compatible with OpenAI's?
A2: Yes. The `groq` SDK mirrors it, and the OpenAI client works with `base_url="https://api.groq.com/openai/v1"`.

Q3: [Medium] Does Groq train its own models?
A3: No. It hosts open-weight models from other organisations and serves them quickly.

Q4: [Medium] What latency metrics matter?
A4: Time to first token (TTFT), tokens per second, and end-to-end p95 latency, measured from your region with realistic prompt sizes.

Q5: [Hard] Design a router that sends requests across Groq, OpenAI, and Claude.
A5: Classify the task (latency-critical, simple versus complex reasoning, long context), pick the provider by policy, enforce per-provider rate limiters, retry with backoff, fall back on 429/5xx, normalise responses in an adapter, log latency/cost/quality per provider, and run a weekly eval to adjust the policy. A gateway such as LiteLLM can implement much of this.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Real-time UX, voice, autocomplete, high-volume simple tasks

❌ Avoid when:
- You need frontier-level reasoning, strict compliance terms not met, or features it does not host

---

## 📊 Visual Diagram
```
Typing "power ba..." --> FastAPI --> Groq (LPU) --> 3 suggestions in ~0.3s
                                  \-- 429/5xx --> OpenAI fallback

Latency feel:
 GPU-hosted large model : [..........2.5s..........]
 Groq small/medium model: [..0.4s..]
```

---

## 💰 Cost Impact
- Groq bills per token with rates per model; hosted open models are often cheaper than frontier models. Confirm on the pricing page; free tiers are rate-limited.
- Faster responses can cut infrastructure cost (shorter-held connections) and improve conversion.
- Optimise: use the smallest model that passes evals, cap `max_tokens`, cache repeated suggestions, and keep fallback calls to a small share of traffic.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Groq | Fast inference provider | तेज़ inference देने वाली कंपनी |
| LPU | Groq's custom inference chip | Groq की custom inference chip |
| Open-weight model | Model with downloadable weights | Weights उपलब्ध वाला model |
| TTFT | Time to first token | पहले token तक का समय |
| Tokens/sec | Generation speed | Generation की गति |
| base_url | Server address for the client | Client का server पता |

---

## ⚡ 3-Line Summary
English: Groq serves open models with very low latency through an OpenAI-shaped API (`groq` SDK or OpenAI client with a custom base URL). Use it for real-time, simple tasks, and keep stronger models and a fallback for hard cases. Check model ids, limits, and data terms.
Hindi: Groq open models को OpenAI जैसी API (`groq` SDK या custom base URL वाले OpenAI client) से बहुत कम latency पर serve करता है। Real-time और सरल tasks के लिए use करो, कठिन cases के लिए मज़बूत models और fallback रखो। Model ids, limits और data terms जाँचो।

---

## ➡️ Next Topic
**041. Ollama (Local Models)** — run open models on your own machine for privacy and zero API cost.
