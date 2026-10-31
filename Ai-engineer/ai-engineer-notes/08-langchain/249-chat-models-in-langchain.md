---

# 249. Chat Models in LangChain
# हिंदी में: LangChain में Chat Models

---

## 🔵 Simple Definition (English)
A **Chat Model** in LangChain is a wrapper around an LLM that takes a list of **messages** (`SystemMessage`, `HumanMessage`, `AIMessage`) and returns an `AIMessage`. All providers (`ChatOpenAI`, `ChatAnthropic`, `ChatOllama`...) share the same Runnable interface: `invoke`, `ainvoke`, `stream`, `batch`. Swap the provider by changing one line.

## 🔵 सरल परिभाषा (Hindi)
LangChain में **Chat Model** एक LLM का wrapper है जो **messages** की list (`SystemMessage`, `HumanMessage`, `AIMessage`) लेता है और `AIMessage` लौटाता है। सभी providers (`ChatOpenAI`, `ChatAnthropic`, `ChatOllama`...) का interface एक जैसा है: `invoke`, `ainvoke`, `stream`, `batch`। Provider बदलना = सिर्फ़ एक line बदलना।

---

## 🔴 Problem it Solves
OpenAI's SDK returns `choices[0].message.content`; Anthropic's returns `content[0].text` with a separate `system` parameter; streaming formats differ; retry and tool-calling formats differ. Code written for one provider breaks on another, and vendor lock-in grows.

Chat Models give one message format, one response type, one way to stream, retry, call tools and get structured output.

## 🔴 यह क्यों बना? (Hindi)
OpenAI का response `choices[0].message.content` में आता है, Anthropic का `content[0].text` में और `system` अलग parameter है। Streaming, retry और tool-calling के formats भी अलग हैं। एक provider का code दूसरे पर टूट जाता है। Chat Models एक message format, एक response type और streaming/retry/tools का एक ही तरीका देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create model: ChatOpenAI(model="gpt-4o-mini", temperature=0)
Step 2 → Build messages: [SystemMessage(...), HumanMessage(...)]  (or a plain string / tuples)
Step 3 → model.invoke(messages) -> provider-specific request is built internally
Step 4 → API responds; LangChain converts it to AIMessage(content, usage_metadata, response_metadata)
Step 5 → Optional: stream() yields AIMessageChunk pieces as tokens arrive
Step 6 → Optional: bind_tools / with_structured_output / with_retry / with_fallbacks add features
Step 7 → usage_metadata (input_tokens, output_tokens) used for cost tracking
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Model बनाओ: ChatOpenAI(model="gpt-4o-mini", temperature=0)
Step 2 → Messages बनाओ: [SystemMessage(...), HumanMessage(...)]
Step 3 → model.invoke(messages) -> अंदर provider का request बनता है
Step 4 → Response AIMessage(content, usage_metadata, response_metadata) में बदलता है
Step 5 → stream() tokens आते ही AIMessageChunk देता है
Step 6 → bind_tools / with_structured_output / with_retry / with_fallbacks से features जुड़ते हैं
Step 7 → usage_metadata (input_tokens, output_tokens) से cost track होती है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A classifier node uses `ChatOpenAI("gpt-4o-mini")` for 95% of products. For ambiguous items it escalates to a stronger model. When OpenAI has an outage, `.with_fallbacks([ChatAnthropic(...)])` keeps the service up. All of this without changing the chain code because every model is a Runnable.

**Zomato AI**: Support chatbot streams the reply token by token to the app (`astream`), so the user sees text immediately.

## 🟡 Real Example Hindi mein
**Tariff System**: 95% products के लिए `ChatOpenAI("gpt-4o-mini")`, ambiguous items के लिए मज़बूत model। OpenAI down हो तो `.with_fallbacks([ChatAnthropic(...)])` service चालू रखता है। Chain का code नहीं बदलता क्योंकि हर model एक Runnable है।

**Zomato AI**: Support chatbot reply को token-by-token stream करता है (`astream`), user को text तुरंत दिखता है।

---

## 💻 Code Example — Basic
```python
# Basic: chat model interface using a fake model (offline, no API key)
# Real: from langchain_openai import ChatOpenAI; llm = ChatOpenAI(model="gpt-4o-mini")
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # scripted model for tests
from langchain_core.messages import HumanMessage, SystemMessage                # message types

llm = FakeListChatModel(responses=["HS 8507 (lithium batteries)", "second answer"])  # replies in order

messages = [                                                           # conversation as message objects
    SystemMessage(content="You are a tariff classification assistant."),  # behaviour instructions
    HumanMessage(content="HS code for a power bank?"),                 # the user turn
]
reply = llm.invoke(messages)                                           # call the model -> AIMessage
print(type(reply).__name__, "->", reply.content)                       # AIMessage -> text

# Shortcuts: tuples or a plain string also work
print(llm.invoke("second question").content)                           # string becomes a HumanMessage

# Streaming: tokens/chunks arrive one by one
llm2 = FakeListChatModel(responses=["abc"])                            # fresh fake with one answer
print([c.content for c in llm2.stream("hi")])                          # list of chunks (characters here)

# batch: many inputs in parallel
llm3 = FakeListChatModel(responses=["x", "y"])                         # two answers
print([m.content for m in llm3.batch(["q1", "q2"])])                   # two AIMessages
```

## 💻 Code Example — Advanced
```python
# Production: provider-agnostic factory, retries, fallbacks, usage tracking, async
# pip install langchain langchain-openai langchain-anthropic
import asyncio                                                         # async
import logging                                                         # logs
from langchain_core.language_models import BaseChatModel               # common type
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

logger = logging.getLogger("tariff.llm")                               # logger


def build_llm() -> BaseChatModel:
    """Primary model with retries; Anthropic as backup. Needs API keys in env vars."""
    from langchain_openai import ChatOpenAI                            # imported lazily (optional dependency)
    from langchain_anthropic import ChatAnthropic                      # backup provider

    primary = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=30, max_retries=0)
    primary = primary.with_retry(stop_after_attempt=3)                 # retry transient errors (Runnable retry)
    backup = ChatAnthropic(model="claude-haiku-4-5", temperature=0, timeout=30)
    return primary.with_fallbacks([backup])                            # type: ignore[return-value]


def usage_of(msg: AIMessage) -> dict[str, int]:
    """Read standardized token usage from any provider."""
    meta = msg.usage_metadata or {}                                    # may be None (e.g. some streams)
    return {
        "input": meta.get("input_tokens", 0),                          # prompt tokens
        "output": meta.get("output_tokens", 0),                        # completion tokens
    }


async def classify(llm: BaseChatModel, product: str) -> tuple[str, dict[str, int]]:
    """Async call + error handling; returns (answer, token usage)."""
    messages: list[BaseMessage] = [
        SystemMessage(content="Return only the HS code and a one-line reason."),
        HumanMessage(content=f"Product: {product}"),
    ]
    try:
        msg = await asyncio.wait_for(llm.ainvoke(messages), timeout=45)  # never wait forever
    except Exception:                                                  # both providers failed / timeout
        logger.exception("LLM call failed")                            # log traceback
        raise                                                          # let the API layer map to 503
    return str(msg.content), usage_of(msg)                             # text + usage
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI, HTTPException                    # FastAPI
from fastapi.responses import StreamingResponse                        # for token streaming
from pydantic import BaseModel, Field                                  # schemas
from langchain_core.language_models import BaseChatModel

app = FastAPI()                                                        # app


def get_llm() -> BaseChatModel:
    raise NotImplementedError                                          # return a shared model instance


class Ask(BaseModel):                                                  # request body
    question: str = Field(min_length=3, max_length=1000)


@app.post("/ask")                                                      # normal JSON answer
async def ask(body: Ask, llm: BaseChatModel = Depends(get_llm)) -> dict:
    try:
        msg = await llm.ainvoke(body.question)                         # async: does not block the loop
    except Exception as exc:                                           # provider error
        raise HTTPException(status_code=503, detail="LLM unavailable") from exc
    return {"answer": msg.content, "usage": msg.usage_metadata}        # answer + tokens


@app.post("/ask/stream")                                               # streaming answer
async def ask_stream(body: Ask, llm: BaseChatModel = Depends(get_llm)) -> StreamingResponse:
    async def gen():                                                   # async generator of text
        async for chunk in llm.astream(body.question):                 # yields AIMessageChunk
            yield str(chunk.content)                                   # send text piece to client
    return StreamingResponse(gen(), media_type="text/plain")           # chunked HTTP response
```

---

## 🔗 LangChain / LangGraph Connection
```python
# Chat model is the LLM step of every LCEL chain:
chain = prompt | llm | StrOutputParser()

# Tool calling and structured output are methods on the chat model:
llm_with_tools = llm.bind_tools([lookup_duty_rate])        # model may return tool_calls
structured = llm.with_structured_output(TariffResult)      # returns a pydantic object (topic 255)

# LangGraph: nodes call llm.invoke(state["messages"]); MessagesState keeps list[BaseMessage].
# Provider-agnostic loader (langchain >= 0.3): init_chat_model("gpt-4o-mini", model_provider="openai")
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Creating a new model object per request
```python
# Wrong — new HTTP client + config on every call:
@app.post("/ask")
async def ask(q: str):
    return (await ChatOpenAI(model="gpt-4o-mini").ainvoke(q)).content

# Correct — create once (module level / dependency) and reuse.
llm = ChatOpenAI(model="gpt-4o-mini")
```

❌ Mistake 2: Using the old completion-style LLM class
```python
# Wrong — legacy text-completion wrapper:
from langchain_openai import OpenAI
llm = OpenAI(model="gpt-3.5-turbo-instruct")

# Correct — chat models (messages in, AIMessage out):
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")
```

❌ Mistake 3: Treating `.content` as always a string
```python
# Wrong — content can be a list of blocks (Anthropic, multimodal, tool use):
text = msg.content.strip()

# Correct — for plain text use a parser, or check the type:
text = StrOutputParser().invoke(msg)
```

---

## 🧠 Tricky Interview Question

**Q**: "You set `max_retries=6` on ChatOpenAI and also wrapped it with `.with_retry(stop_after_attempt=5)`. During a rate-limit storm your latency explodes. Why?"

**Answer**: Retries multiply. Each of the 5 outer attempts triggers up to 6 inner SDK retries — up to 30 requests per user call, each with backoff sleeps, and every retry adds load to an already rate-limited API. Pick ONE retry layer (usually the SDK's `max_retries` for transient 429/5xx, or `with_retry` for custom exceptions), add jitter/backoff, set `timeout`, and use fallbacks to a different provider or model instead of hammering the same one.

---

## ⚫ Interview Questions + Answers

Q1: What does a chat model take and return? (Easy)
A1: A list of messages (or string/tuples) in; an `AIMessage` out (with `content`, `tool_calls`, `usage_metadata`).

Q2: Why use `ChatOpenAI` instead of the openai SDK directly? (Easy)
A2: Uniform Runnable interface (invoke/stream/batch/async), easy provider swap, built-in retry/fallback, callbacks/tracing, and compatibility with LCEL and LangGraph. Direct SDK gives the newest provider-specific features first.

Q3: How do you get token usage? (Medium)
A3: `AIMessage.usage_metadata` has `input_tokens`, `output_tokens`, `total_tokens` in a standard format. Provider extras are in `response_metadata`. For streaming, usage is available on the final chunk when the provider supports it (OpenAI requires `stream_usage=True` or equivalent).

Q4: Explain `with_fallbacks` vs `with_retry`. (Medium)
A4: `with_retry` re-runs the same runnable on failure. `with_fallbacks` switches to a different runnable (another model/provider) after failure. Use retry for transient errors, fallback for outages or context-length errors.

Q5: How do you make a multi-provider system with consistent behaviour? (Hard)
A5: Use `init_chat_model` or a factory that returns `BaseChatModel`; keep prompts provider-neutral; pin temperature and max tokens; test with the same eval set per provider because tokenization, system-prompt handling and tool-call formats differ; normalise output through parsers/structured output; log provider, latency and token usage per request.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building LCEL chains or LangGraph agents
- You may switch or combine providers
- You need streaming, retries, fallbacks, tracing in one interface

❌ Avoid when:
- A single simple call where the raw SDK is enough
- You need a brand-new provider feature not yet wrapped (use the SDK or pass extra params)

---

## 📊 Visual Diagram
```
 string / tuples / [Message, ...]
              │
              ▼
   ┌─────────────────────────┐
   │  BaseChatModel          │   invoke / ainvoke / stream / batch
   │  ┌───────────────────┐  │
   │  │ ChatOpenAI        │  │──► OpenAI API
   │  │ ChatAnthropic     │  │──► Anthropic API
   │  │ ChatOllama        │  │──► local model
   │  └───────────────────┘  │
   └─────────────────────────┘
              │
              ▼
   AIMessage(content, tool_calls, usage_metadata)
```

---

## 💰 Cost Impact
Cost = input tokens + output tokens, available in `usage_metadata`. Example: 600 input + 150 output on gpt-4o-mini = 600×0.15/1M + 150×0.60/1M = $0.00018. At 100K calls/day ≈ $18/day.

Optimise: choose the smallest model that passes your eval, set `max_tokens`, keep system prompts short, route easy requests to cheap models, cache repeated prompts (provider prompt caching or a semantic cache), and log `usage_metadata` per request to find expensive paths. Remember retries and fallbacks are billed too.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Chat model | Messages in, AIMessage out | Messages वाला LLM wrapper |
| Message | System / Human / AI / Tool | बातचीत की एक entry |
| `AIMessage` | Model's reply object | Model का जवाब |
| `usage_metadata` | Token counts | Token की गिनती |
| Fallback | Backup model on failure | Fail होने पर दूसरा model |
| Streaming | Output in pieces | जवाब टुकड़ों में |

---

## ⚡ 3-Line Summary
English: Chat models give every provider the same Runnable interface: messages in, AIMessage out. Retry, fallback, streaming, tools and token usage work uniformly. Create one instance and reuse it.
Hindi: Chat models हर provider को एक जैसा Runnable interface देते हैं: messages अंदर, AIMessage बाहर। Retry, fallback, streaming, tools और token usage सब एक तरह से चलते हैं। एक instance बनाकर बार-बार reuse करो।

---

## ➡️ Next Topic
**250. Prompt Templates** — how to build the messages you send to a chat model with variables, safely and reusably.
