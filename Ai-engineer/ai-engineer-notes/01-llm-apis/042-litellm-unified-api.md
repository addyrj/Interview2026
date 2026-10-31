---

# 042. LiteLLM — Unified API
# हिंदी में: LiteLLM — Unified API

---

## 🔵 Simple Definition (English)
LiteLLM is a Python library (and optional proxy server) that lets you call 100+ LLM providers with one OpenAI-style interface. You call `litellm.completion(model="provider/model", messages=[...])`, and it translates the request to OpenAI, Anthropic, Gemini, Groq, Ollama, and others, then returns an OpenAI-shaped response. It also offers a `Router` for load balancing and fallbacks, and cost tracking.

## 🔵 सरल परिभाषा (Hindi)
LiteLLM एक Python library (और optional proxy server) है जिससे आप 100+ LLM providers को एक ही OpenAI-style interface से call कर सकते हैं। आप `litellm.completion(model="provider/model", messages=[...])` call करते हैं, और यह request को OpenAI, Anthropic, Gemini, Groq, Ollama आदि के format में बदलकर OpenAI-जैसा response लौटाती है। साथ में load balancing और fallbacks के लिए `Router` और cost tracking भी है।

---

## 🔴 Problem it Solves
Each provider has different request shapes, error classes, and token fields (topic 035). Writing and maintaining an adapter for every provider is slow and buggy. LiteLLM gives that adapter ready-made, so switching models is a one-string change and fallbacks, retries, budgets, and logging are built in.

## 🔴 यह क्यों बना? (Hindi)
हर provider के request shapes, error classes और token fields अलग हैं (topic 035)। हर provider के लिए adapter लिखना और संभालना धीमा और bug वाला है। LiteLLM वही adapter तैयार देता है, इसलिए model बदलना एक string बदलने जितना आसान है, और fallbacks, retries, budgets व logging पहले से मिलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install litellm ; set provider keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, ...)
Step 2 → Call litellm.completion(model="gpt-4o-mini", messages=[...])
Step 3 → Switch provider by changing the model string: "anthropic/<claude-model>", "gemini/<model>", "groq/<model>", "ollama/<model>"
Step 4 → LiteLLM converts your OpenAI-style request into the provider's native format
Step 5 → Provider replies; LiteLLM converts it back to an OpenAI-shaped ModelResponse
Step 6 → Read response.choices[0].message.content and response.usage as usual
Step 7 → litellm.completion_cost(response) estimates the cost in USD
Step 8 → Use Router(model_list=[...], fallbacks=[...]) for load balancing and failover
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → pip install litellm ; provider keys set करो (OPENAI_API_KEY, ANTHROPIC_API_KEY, ...)
Step 2 → litellm.completion(model="gpt-4o-mini", messages=[...]) call करो
Step 3 → Model string बदलकर provider बदलो: "anthropic/<claude-model>", "gemini/<model>", "groq/<model>", "ollama/<model>"
Step 4 → LiteLLM आपकी OpenAI-style request को provider के native format में बदलता है
Step 5 → Provider जवाब देता है; LiteLLM उसे OpenAI-shaped ModelResponse में बदल देता है
Step 6 → पहले जैसा response.choices[0].message.content और response.usage पढ़ो
Step 7 → litellm.completion_cost(response) USD cost का अनुमान देता है
Step 8 → Load balancing और failover के लिए Router(model_list=[...], fallbacks=[...]) use करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The classifier calls `completion(model=settings.CLASSIFIER_MODEL, ...)`. The model name lives in config, so the team can A/B test an OpenAI model against a Claude model, add Groq for the fast type-ahead, and use Ollama for confidential files, all without code changes. A Router sends traffic to the primary model and falls back to a second provider on errors.

**Amazon-style AI**: An internal LLM gateway (LiteLLM proxy) gives every team one endpoint, per-team budgets, and central logging of spend.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: Classifier `completion(model=settings.CLASSIFIER_MODEL, ...)` call करता है। Model का नाम config में है, इसलिए team बिना code बदले OpenAI model और Claude model का A/B test कर सकती है, तेज़ type-ahead के लिए Groq जोड़ सकती है और गोपनीय files के लिए Ollama use कर सकती है। Router traffic primary model को भेजता है और errors पर दूसरे provider पर fallback करता है।

**Amazon-style AI**: Internal LLM gateway (LiteLLM proxy) हर team को एक endpoint, per-team budgets और spend की central logging देता है।

---

## 💻 Code Example — Basic
```python
# Basic LiteLLM: same code, different providers (needs the relevant API keys)
import os                                        # env access
from litellm import completion                   # unified call

# Model ids are examples; check each provider's docs for current names.
MODELS = [
    "gpt-4o-mini",                               # OpenAI (needs OPENAI_API_KEY)
    "anthropic/claude-sonnet-4-5",               # Anthropic (needs ANTHROPIC_API_KEY)
    "groq/llama-3.3-70b-versatile",              # Groq (needs GROQ_API_KEY)
    "ollama/llama3.2",                           # local Ollama (no key; server must be running)
]

messages = [
    {"role": "system", "content": "Return only the 6-digit HS code."},   # same for all
    {"role": "user", "content": "lithium power bank"},
]

model = os.getenv("LLM_MODEL", MODELS[0])        # choose by config, not by code
response = completion(model=model, messages=messages, temperature=0, max_tokens=30)

print(response.choices[0].message.content)       # OpenAI-shaped, whichever provider answered
print(response.usage.prompt_tokens, response.usage.completion_tokens)
```

## 💻 Code Example — Advanced
```python
# Production: Router with fallbacks, async calls, cost tracking, error handling
import asyncio                                           # async runner
import logging                                           # logs
from typing import Optional                              # type hints

import litellm                                           # library (exceptions, cost)
from litellm import Router                               # load balancer / fallback engine

logger = logging.getLogger(__name__)                     # logger

model_list = [                                           # logical name -> real deployment(s)
    {"model_name": "classifier",                         # name your code uses
     "litellm_params": {"model": "gpt-4o-mini"}},        # primary: OpenAI
    {"model_name": "classifier-backup",
     "litellm_params": {"model": "anthropic/claude-sonnet-4-5"}},   # backup: Claude
]

router = Router(
    model_list=model_list,
    fallbacks=[{"classifier": ["classifier-backup"]}],   # if "classifier" fails, try backup
    num_retries=2,                                       # retries before falling back
    timeout=30,                                          # seconds per call
)


async def classify(product: str) -> Optional[tuple[str, float]]:
    try:
        resp = await router.acompletion(                 # async call through the router
            model="classifier",
            messages=[{"role": "system", "content": "Return only the 6-digit HS code."},
                      {"role": "user", "content": product}],
            temperature=0, max_tokens=30)
    except litellm.RateLimitError:                       # exceptions mirror OpenAI's names
        logger.warning("all deployments rate limited")
        return None
    except litellm.AuthenticationError:
        logger.error("check provider API keys")
        return None
    except Exception as exc:                             # fallbacks exhausted or other failure
        logger.error("LLM call failed: %s", exc)
        return None
    try:
        cost = litellm.completion_cost(completion_response=resp)   # USD estimate
    except Exception:                                    # unknown model pricing
        cost = 0.0
    return resp.choices[0].message.content, cost


if __name__ == "__main__":
    print(asyncio.run(classify("lithium power bank")))
```

---

## 🟠 FastAPI Integration
Two options: (1) use the LiteLLM library inside FastAPI as below; (2) run the LiteLLM proxy server and point the standard OpenAI client at it, so every service shares keys, budgets, and logging.

```python
import litellm                                          # library
from fastapi import FastAPI, HTTPException              # framework
from litellm import Router                              # router
from pydantic import BaseModel                          # models

app = FastAPI()                                         # app
router = Router(
    model_list=[
        {"model_name": "fast", "litellm_params": {"model": "groq/llama-3.3-70b-versatile"}},
        {"model_name": "smart", "litellm_params": {"model": "gpt-4o"}},
    ],
    fallbacks=[{"fast": ["smart"]}],                    # fast model failing falls back to smart
    num_retries=1,
)


class Body(BaseModel):
    product: str
    tier: str = "fast"                                  # "fast" or "smart"


@app.post("/classify")
async def classify(b: Body) -> dict:
    if b.tier not in ("fast", "smart"):                 # never pass user text as a model name
        raise HTTPException(status_code=422, detail="invalid tier")
    try:
        r = await router.acompletion(
            model=b.tier,
            messages=[{"role": "user", "content": f"HS code digits only: {b.product}"}],
            max_tokens=20)
    except Exception:
        raise HTTPException(status_code=502, detail="AI service unavailable")
    return {"hs_code": r.choices[0].message.content, "served_by": r.model}

# Proxy option: start `litellm --config config.yaml`, then:
# from openai import AsyncOpenAI
# client = AsyncOpenAI(base_url="http://litellm-proxy:4000", api_key="sk-team-key")
```

---

## 🔗 LangChain / LangGraph Connection
`langchain-litellm` provides `ChatLiteLLM`, which wraps LiteLLM as a LangChain chat model (the older `langchain_community.chat_models.ChatLiteLLM` is deprecated, so install the dedicated package). Alternatively, point `ChatOpenAI` at a LiteLLM proxy with `base_url`.

```python
# Option A: dedicated integration (pip install langchain-litellm)
from langchain_litellm import ChatLiteLLM

llm = ChatLiteLLM(model="anthropic/claude-sonnet-4-5", temperature=0)
# print(llm.invoke("HS code for a power bank? digits only").content)

# Option B: talk to a LiteLLM proxy using the standard OpenAI wrapper
from langchain_openai import ChatOpenAI

proxy_llm = ChatOpenAI(model="classifier", base_url="http://localhost:4000", api_key="sk-team-key")
# LangGraph nodes then use `llm` or `proxy_llm` like any other chat model;
# switching providers is a model-name change on the proxy, not a code change.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting the provider prefix
✅ Correct: Use `provider/model` for non-OpenAI models.

```python
# Wrong — LiteLLM cannot guess the provider for every name
completion(model="claude-sonnet-4-5", messages=msgs)
# Right
completion(model="anthropic/claude-sonnet-4-5", messages=msgs)
```

❌ Mistake 2: Assuming all OpenAI parameters work on every provider
✅ Correct: Unsupported params may be ignored or raise errors. Use `litellm.drop_params = True` to silently drop them, or check provider support (`litellm.get_supported_openai_params`).

❌ Mistake 3: Stacking retries (Router retries x provider SDK retries x your own)
✅ Correct: Decide who owns retries; set `num_retries` on the Router and keep your wrapper simple.

❌ Mistake 4: Trusting estimated cost as the invoice
✅ Correct: `completion_cost` uses LiteLLM's price table; reconcile with provider billing.

❌ Mistake 5: Letting users choose the model string
✅ Correct: Map allowed tiers to models on the server.

---

## 🧠 Tricky Interview Question

**Q**: "Why might a unified wrapper like LiteLLM make your results worse or your system harder to debug?"

**Answer**: Abstractions leak. (1) Provider-specific features (prompt caching controls, extended thinking, special tool options, structured-output modes) may not map one-to-one, so you lose capability or pass hidden provider params. (2) Silent parameter dropping can change behaviour without errors. (3) Prompts tuned for one model do not transfer, so a "free" model switch can reduce quality. (4) An extra layer adds latency, a dependency to upgrade, and another place for retries and timeouts to stack. (5) Cost tables can lag new prices. Mitigate with per-provider evals, explicit provider params where needed, logging of the actual served model and raw errors, version pinning, and integration tests against each provider.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] What is LiteLLM?
A1: A library/proxy exposing one OpenAI-style API for 100+ LLM providers.

Q2: [Easy] How do you switch from OpenAI to Claude with it?
A2: Change the model string to `anthropic/<model>` and set `ANTHROPIC_API_KEY`; the rest of the code stays the same.

Q3: [Medium] What does the Router do?
A3: Load balances across deployments, retries, applies fallbacks and cooldowns for failing deployments, and enforces timeouts and rate limits.

Q4: [Medium] Library versus proxy server?
A4: Library: imported in each service, simple. Proxy: a central gateway (OpenAI-compatible endpoint) with virtual keys, budgets, rate limits, caching, and spend logs shared by all services and languages.

Q5: [Hard] Design a company-wide LLM gateway using LiteLLM.
A5: Deploy the proxy behind auth with per-team virtual keys and budgets; define logical model names mapped to multiple deployments with fallbacks and cooldowns; enable Redis for shared rate limits and caching; export logs/metrics to your observability stack (for example Langfuse or Prometheus); store provider keys in a secret manager; add guardrails (PII masking, content filters); enforce data-residency routing; version configs and test failover regularly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multi-provider apps, fallbacks, A/B tests, central budgets and logging

❌ Avoid when:
- You use only one provider and need its newest provider-specific features immediately
- You cannot tolerate an extra dependency or hop

---

## 📊 Visual Diagram
```
 your code:  completion(model="classifier", messages=...)
                     |
              +------v------+
              |  LiteLLM    |  translate request / response
              |  Router     |  retries, fallbacks, cooldown
              +--+---+---+--+
                 |   |   |
        OpenAI  Claude Groq  Ollama ...
                 |
   OpenAI-shaped response + usage + cost
```

---

## 💰 Cost Impact
- LiteLLM itself is free (open source); you pay the underlying providers. The proxy adds hosting cost and a small latency overhead.
- It helps control spend: per-key budgets, rate limits, caching of repeated requests, routing to cheaper models, and `completion_cost` for per-call cost logs.
- Optimise: route easy tasks to cheap models, enable caching, set budgets per team, and alert on spend spikes.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LiteLLM | Unified LLM API library | Unified LLM API library |
| Router | Load balancing + fallbacks | Load balancing और fallbacks |
| Proxy / Gateway | Central OpenAI-style server | Central OpenAI-style server |
| Fallback | Backup model on failure | Failure पर backup model |
| Virtual key | Team-specific API key with budget | Budget वाली team की API key |
| drop_params | Ignore unsupported parameters | Unsupported parameters छोड़ना |
| completion_cost | Estimated USD cost of a call | एक call की अनुमानित USD cost |

---

## ⚡ 3-Line Summary
English: LiteLLM gives one OpenAI-style interface to many providers, so switching is a model-string change. Its Router adds retries, fallbacks, and load balancing, and its proxy adds budgets and logging. Beware leaky abstractions: test each provider and keep prompts per model.
Hindi: LiteLLM कई providers के लिए एक OpenAI-style interface देता है, इसलिए बदलना सिर्फ़ model string बदलना है। इसका Router retries, fallbacks और load balancing जोड़ता है, और proxy budgets व logging। Abstractions की कमियों से सावधान रहो: हर provider test करो और हर model के लिए prompts अलग रखो।

---

## ➡️ Next Topic
**043. Model Selection Strategy** — how to choose the right model across all these providers using evals, cost, and latency.
