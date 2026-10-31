---

# 035. Claude API vs OpenAI API
# हिंदी में: Claude API बनाम OpenAI API

---

## 🔵 Simple Definition (English)
Both APIs let you chat with an LLM, but their request and response shapes differ. OpenAI Chat Completions puts the system prompt inside `messages` and returns `choices[0].message.content`. Claude's Messages API has a top-level `system`, a required `max_tokens`, and returns a list of content blocks. Knowing the differences lets you write adapters and switch providers safely.

## 🔵 सरल परिभाषा (Hindi)
दोनों APIs से LLM से chat होती है, लेकिन request और response का आकार अलग है। OpenAI Chat Completions में system prompt `messages` के अंदर होता है और जवाब `choices[0].message.content` में आता है। Claude की Messages API में top-level `system`, ज़रूरी `max_tokens` और content blocks की list वाला जवाब होता है। फ़र्क जानने से आप adapters लिख सकते हैं और provider सुरक्षित तरीके से बदल सकते हैं।

---

## 🔴 Problem it Solves
Teams hard-code one provider's format everywhere. When the provider has an outage, a price hike, or a better competitor appears, switching means rewriting dozens of files. Understanding the differences (and isolating them in one adapter) removes vendor lock-in and enables fallbacks and A/B tests.

## 🔴 यह क्यों बना? (Hindi)
Teams एक provider का format हर जगह hard-code कर देती हैं। Provider का outage, price बढ़ना या बेहतर competitor आने पर बदलने का मतलब दर्जनों files दोबारा लिखना है। फ़र्क समझकर (और उन्हें एक adapter में रखकर) vendor lock-in हटता है और fallbacks व A/B tests संभव होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List what you send: model, messages, system, max_tokens, temperature, tools
Step 2 → Map OpenAI fields to Claude fields (see the table in the diagram)
Step 3 → Build one internal format: LLMRequest(system, messages, max_tokens, temperature)
Step 4 → Write adapters: to_openai(req) and to_claude(req)
Step 5 → Write a normaliser for responses: text, input_tokens, output_tokens, stop_reason
Step 6 → Map errors to your own exception types (rate limit, transient, permanent)
Step 7 → Run the same eval set through both providers
Step 8 → Choose, route, or fall back based on quality, latency, and cost
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → लिखो आप क्या भेजते हैं: model, messages, system, max_tokens, temperature, tools
Step 2 → OpenAI fields को Claude fields से map करो (diagram में table देखो)
Step 3 → एक internal format बनाओ: LLMRequest(system, messages, max_tokens, temperature)
Step 4 → Adapters लिखो: to_openai(req) और to_claude(req)
Step 5 → Response normaliser लिखो: text, input_tokens, output_tokens, stop_reason
Step 6 → Errors को अपने exception types में map करो (rate limit, transient, permanent)
Step 7 → वही eval set दोनों providers पर चलाओ
Step 8 → Quality, latency और cost देखकर चुनो, route करो या fallback रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: The primary classifier uses an OpenAI model. During an OpenAI incident, the router sends traffic to a Claude model through the adapter. Because both return the same internal `LLMResponse`, the rest of the system (validation, audit logging, UI) does not change. Monthly, the team replays 500 labelled products through both and compares accuracy and cost.

**Zomato AI**: Uses a cheap model from one provider for menu Q&A and another provider's model for long review summarisation, chosen by eval.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: Primary classifier OpenAI model use करता है। OpenAI incident के दौरान router traffic adapter के ज़रिए Claude model को भेज देता है। दोनों वही internal `LLMResponse` लौटाते हैं, इसलिए बाकी system (validation, audit logging, UI) नहीं बदलता। हर महीने team 500 labelled products दोनों पर चलाकर accuracy और cost compare करती है।

**Zomato AI**: Menu Q&A के लिए एक provider का सस्ता model और लंबे reviews की summary के लिए दूसरे provider का model, eval के आधार पर।

---

## 💻 Code Example — Basic
```python
# Side-by-side request/response shapes. Runs offline: it only builds dicts and parses fake responses.
from typing import Any, Dict, List                      # type hints

system = "You are a tariff assistant."                  # shared instruction
user_msg = "HS code for a power bank?"                  # shared question

# --- OpenAI Chat Completions request shape ---
openai_request: Dict[str, Any] = {
    "model": "gpt-4o-mini",                             # model id
    "messages": [                                       # system is INSIDE messages
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ],
    "max_tokens": 100,                                  # optional
}

# --- Claude Messages request shape ---
claude_request: Dict[str, Any] = {
    "model": "claude-sonnet-4-5",                       # model id (check docs)
    "system": system,                                   # system is TOP-LEVEL
    "messages": [{"role": "user", "content": user_msg}],
    "max_tokens": 100,                                  # REQUIRED
}

# --- Fake responses shaped like the real ones ---
openai_response = {"choices": [{"message": {"content": "8507.60"}}],
                   "usage": {"prompt_tokens": 30, "completion_tokens": 5}}
claude_response = {"content": [{"type": "text", "text": "8507.60"}],
                   "usage": {"input_tokens": 30, "output_tokens": 5}}

# Extract the same data from both shapes
text_o = openai_response["choices"][0]["message"]["content"]
text_c = "".join(b["text"] for b in claude_response["content"] if b["type"] == "text")
print(text_o == text_c, text_o)                         # True 8507.60
print(openai_response["usage"]["prompt_tokens"], claude_response["usage"]["input_tokens"])
```

## 💻 Code Example — Advanced
```python
# Provider adapter: one interface, two backends, sync + async, normalised errors
import asyncio                                           # async runner
import logging                                           # logs
import os                                                # env
from dataclasses import dataclass                        # simple models
from typing import List, Protocol                        # interface typing

import anthropic                                         # Claude SDK
import openai                                            # OpenAI SDK

logger = logging.getLogger(__name__)                     # logger


@dataclass
class LLMRequest:
    system: str                                          # instructions
    user: str                                            # user text
    max_tokens: int = 300                                # always set (Claude requires it)
    temperature: float = 0.0                             # deterministic by default


@dataclass
class LLMResponse:
    text: str                                            # answer
    input_tokens: int                                    # billed input
    output_tokens: int                                   # billed output
    provider: str                                        # who answered


class ProviderError(Exception):
    def __init__(self, kind: str, msg: str) -> None:     # kind: "rate_limit"|"transient"|"permanent"
        super().__init__(msg)
        self.kind = kind


class Provider(Protocol):
    async def complete(self, req: LLMRequest) -> LLMResponse: ...


class OpenAIProvider:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model, self.client = model, openai.AsyncOpenAI(max_retries=2, timeout=30.0)

    async def complete(self, req: LLMRequest) -> LLMResponse:
        try:
            r = await self.client.chat.completions.create(
                model=self.model, max_tokens=req.max_tokens, temperature=req.temperature,
                messages=[{"role": "system", "content": req.system},
                          {"role": "user", "content": req.user}])
        except openai.RateLimitError as e:
            raise ProviderError("rate_limit", str(e))
        except (openai.APIConnectionError, openai.InternalServerError) as e:
            raise ProviderError("transient", str(e))
        except openai.APIError as e:
            raise ProviderError("permanent", str(e))
        return LLMResponse(r.choices[0].message.content or "", r.usage.prompt_tokens,
                           r.usage.completion_tokens, "openai")


class ClaudeProvider:
    def __init__(self, model: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")) -> None:
        self.model, self.client = model, anthropic.AsyncAnthropic(max_retries=2, timeout=30.0)

    async def complete(self, req: LLMRequest) -> LLMResponse:
        try:
            m = await self.client.messages.create(
                model=self.model, max_tokens=req.max_tokens, temperature=req.temperature,
                system=req.system, messages=[{"role": "user", "content": req.user}])
        except anthropic.RateLimitError as e:
            raise ProviderError("rate_limit", str(e))
        except (anthropic.APIConnectionError, anthropic.InternalServerError) as e:
            raise ProviderError("transient", str(e))
        except anthropic.APIError as e:
            raise ProviderError("permanent", str(e))
        text = "".join(b.text for b in m.content if b.type == "text")
        return LLMResponse(text, m.usage.input_tokens, m.usage.output_tokens, "claude")


async def with_fallback(req: LLMRequest, providers: List[Provider]) -> LLMResponse:
    last: Exception | None = None
    for p in providers:                                  # try in order
        try:
            return await p.complete(req)
        except ProviderError as e:
            logger.warning("%s failed (%s)", type(p).__name__, e.kind)
            last = e
            if e.kind == "permanent":                    # same request will fail elsewhere too
                break
    raise last or RuntimeError("no providers")


if __name__ == "__main__":
    req = LLMRequest(system="Return only the HS code.", user="power bank")
    print(asyncio.run(with_fallback(req, [OpenAIProvider(), ClaudeProvider()])))
```

---

## 🟠 FastAPI Integration

```python
from fastapi import FastAPI, HTTPException            # framework
from pydantic import BaseModel                        # models
# Reuse LLMRequest, OpenAIProvider, ClaudeProvider, with_fallback, ProviderError
# from the adapter module above (for example: from llm_adapter import ...)

app = FastAPI()                                       # app
PROVIDERS = [OpenAIProvider(), ClaudeProvider()]      # primary then fallback


class Body(BaseModel):
    product: str


@app.post("/classify")
async def classify(b: Body) -> dict:
    req = LLMRequest(system="Return only the 6-digit HS code.", user=b.product, max_tokens=30)
    try:
        res = await with_fallback(req, PROVIDERS)     # provider-agnostic call
    except ProviderError as e:
        raise HTTPException(status_code=502, detail=f"All providers failed ({e.kind})")
    return {"hs_code": res.text.strip(), "provider": res.provider,
            "tokens": {"in": res.input_tokens, "out": res.output_tokens}}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's chat model interface hides most differences: `ChatOpenAI` and `ChatAnthropic` accept the same messages and return the same `AIMessage`. Use `with_fallbacks` or LangChain's `init_chat_model` to switch providers by config.

```python
from langchain_openai import ChatOpenAI                 # OpenAI wrapper
from langchain_anthropic import ChatAnthropic           # Claude wrapper
from langchain_core.messages import HumanMessage, SystemMessage

openai_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
claude_llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0, max_tokens=200)

llm = openai_llm.with_fallbacks([claude_llm])           # provider failover in one line
msgs = [SystemMessage("Return only the HS code."), HumanMessage("power bank")]
# print(llm.invoke(msgs).content)                       # same code for both providers

# Config-driven: from langchain.chat_models import init_chat_model
# llm = init_chat_model("anthropic:claude-sonnet-4-5")  # or "openai:gpt-4o-mini"
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Sending a `system` role message to Claude
✅ Correct: Move it to the top-level `system`.

```python
# Wrong (Claude)
messages=[{"role": "system", "content": "Be brief"}, {"role": "user", "content": "hi"}]
# Right
system="Be brief", messages=[{"role": "user", "content": "hi"}]
```

❌ Mistake 2: Assuming identical parameters
✅ Correct: Parameters like `n`, `seed`, `logprobs`, `response_format` are OpenAI-specific; Claude has `top_k`, `stop_sequences`, and uses tools or prompting for structured output.

❌ Mistake 3: Comparing providers without evals
✅ Correct: Run the same labelled test set and compare accuracy, latency, cost.

❌ Mistake 4: Letting provider-specific objects spread through your code
✅ Correct: Normalise to your own `LLMResponse` at the boundary.

---

## 🧠 Tricky Interview Question

**Q**: "Your multi-provider fallback works in tests, but in an outage the fallback produces worse results and sometimes malformed JSON. Why?"

**Answer**: Prompts tuned for one model rarely transfer perfectly. Differences: instruction-following style, JSON habits, default verbosity, tool-call formats, and token counts (different tokenizers, so context budgets differ). Fixes: maintain per-provider prompt variants, validate outputs with pydantic and retry or repair, test the fallback path regularly in CI with the eval set, use structured-output features of each provider, and monitor quality per provider in production.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Where does the system prompt go in each API?
A1: OpenAI: a message with role `system` (or `developer` for newer models). Claude: top-level `system` parameter.

Q2: [Easy] How do you read the answer text in each?
A2: OpenAI: `response.choices[0].message.content`. Claude: join the `text` blocks in `message.content`.

Q3: [Medium] Name two required-parameter differences.
A3: Claude requires `max_tokens`; OpenAI does not. Claude requires the first message to be from `user` and alternating roles.

Q4: [Medium] Compare usage fields.
A4: OpenAI: `prompt_tokens`, `completion_tokens`, `total_tokens`. Claude: `input_tokens`, `output_tokens` (plus cache fields when caching is used).

Q5: [Hard] How would you design provider-agnostic LLM code?
A5: A thin internal interface (request/response dataclasses), one adapter per provider, error normalisation, config-driven model selection, fallback and routing policy, central logging of tokens and cost, and an eval harness that runs every candidate on the same dataset. Libraries such as LiteLLM or LangChain give this off the shelf.

---

## 🔷 When to Use + When Not to Use
✅ Use multi-provider when:
- Uptime is critical, or you want best-model-per-task and price leverage

❌ Avoid when:
- A small project where one provider suffices; extra abstraction adds cost and bugs

---

## 📊 Visual Diagram
```
                OpenAI Chat Completions        Claude Messages
system prompt   messages[{role:"system"}]      system="..." (top-level)
max_tokens      optional                       REQUIRED
reply text      choices[0].message.content     content[i].text (blocks)
usage           prompt/completion_tokens       input/output_tokens
stop reason     finish_reason (stop,length)    stop_reason (end_turn,max_tokens)
tool call       message.tool_calls             content block type="tool_use"
JSON mode       response_format                tools / prompting
stream          stream=True (chunks)           messages.stream() (events)
errors          openai.RateLimitError          anthropic.RateLimitError

 your code --> [ Adapter ] --+--> OpenAI
                             +--> Claude
```

---

## 💰 Cost Impact
- Both bill per input and output token with different prices per model, and each uses its own tokenizer, so the same text can have different token counts. Compare cost per task on your data, not per token.
- Prompt caching exists in both (OpenAI caches automatically for long prompts; Claude uses explicit `cache_control` markers); structure prompts with static content first.
- Optimise: route by task difficulty across providers, cap output tokens, use batch APIs for offline jobs, and track cost per provider in one dashboard.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Adapter | Wrapper hiding provider differences | Provider फ़र्क छिपाने वाला wrapper |
| Vendor lock-in | Hard to switch provider | Provider बदलना मुश्किल |
| Fallback | Backup provider on failure | Failure पर backup provider |
| Normalisation | Convert to one common format | एक common format में बदलना |
| Router | Chooses provider/model per request | Request के लिए provider चुनने वाला |
| Eval set | Labelled tests for comparison | Compare करने के labelled tests |

---

## ⚡ 3-Line Summary
English: OpenAI puts system in `messages` and returns `choices`; Claude uses a top-level `system`, requires `max_tokens`, and returns content blocks. Hide the differences behind one adapter so you can fall back, route, and compare providers. Always judge with evals on your own data.
Hindi: OpenAI system को `messages` में रखता है और `choices` लौटाता है; Claude में top-level `system`, ज़रूरी `max_tokens` और content blocks होते हैं। फ़र्क को एक adapter के पीछे छिपाओ ताकि fallback, routing और comparison हो सके। फ़ैसला हमेशा अपने data पर evals से करो।

---

## ➡️ Next Topic
**036. Claude — System Prompt Difference** — how the top-level `system` field works and why it matters.
