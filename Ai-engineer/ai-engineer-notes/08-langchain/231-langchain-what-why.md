---

# 231. LangChain — What + Why
# हिंदी में: LangChain — क्या है और क्यों

---

## 🔵 Simple Definition (English)
LangChain is an open-source framework with ready-made building blocks (models, prompts, parsers, retrievers, tools) and a way to connect them (LCEL) so you can build LLM applications faster and swap providers easily.

## 🔵 सरल परिभाषा (Hindi)
LangChain एक open-source framework है जिसमें तैयार building blocks (models, prompts, parsers, retrievers, tools) और उन्हें जोड़ने का तरीका (LCEL) है, ताकि LLM apps जल्दी बनें और provider आसानी से बदला जा सके।

---

## 🔴 Problem it Solves
Without a framework every team rewrites the same glue: prompt templates, retries, output parsing, streaming, tool calling, vector-store adapters, tracing. Each LLM provider has a different SDK, so switching OpenAI to Anthropic means rewriting code. LangChain gives one common interface and shared patterns.

## 🔴 यह क्यों बना? (Hindi)
Framework के बिना हर team वही glue code दोबारा लिखती है: prompt templates, retries, output parsing, streaming, tool calling, vector-store adapters, tracing। हर provider का SDK अलग है, इसलिए OpenAI से Anthropic जाना = code दोबारा लिखना। LangChain एक common interface देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick a chat model:  ChatOpenAI / ChatAnthropic (same interface)
Step 2 → Build a prompt:     ChatPromptTemplate with {variables}
Step 3 → Add a parser:       StrOutputParser / PydanticOutputParser
Step 4 → Chain with pipe:    chain = prompt | model | parser
Step 5 → Run it:             chain.invoke / ainvoke / stream / batch
Step 6 → Add data/tools:     retriever, tools, memory
Step 7 → Trace + deploy:     LangSmith tracing, FastAPI / LangServe
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Chat model चुनो: ChatOpenAI / ChatAnthropic (interface एक जैसा)
Step 2 → Prompt बनाओ: ChatPromptTemplate में {variables}
Step 3 → Parser जोड़ो: StrOutputParser / PydanticOutputParser
Step 4 → Pipe से जोड़ो: chain = prompt | model | parser
Step 5 → चलाओ: invoke / ainvoke / stream / batch
Step 6 → Data/tools जोड़ो: retriever, tools, memory
Step 7 → Trace + deploy: LangSmith, FastAPI
```

---

## 🟡 Real World Example
**Tariff Classification System**: `prompt | llm | parser` returns a typed `Classification` object. Later we add `retriever` to feed context, then switch the model from gpt-4o-mini to Claude by changing one line, without touching the rest. **Zomato AI**: a support bot chain (intent classifier -> order-status tool -> answer writer) built from the same blocks.

## 🟡 Real Example Hindi mein
**Tariff System**: `prompt | llm | parser` typed `Classification` object लौटाता है। फिर `retriever` जोड़कर context देते हैं, और model को gpt-4o-mini से Claude करने के लिए सिर्फ एक line बदलते हैं। **Zomato AI**: support bot chain (intent -> order tool -> answer) इन्हीं blocks से बनती है।

---

## 💻 Code Example — Basic
```python
# Runs offline: a fake "model" via RunnableLambda shows the LangChain composition idea
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a tariff assistant."),  # fixed instruction
    ("human", "HS code for {product}?"),  # {product} is filled at run time
])

def fake_llm(messages) -> str:
    # Stand-in for ChatOpenAI: reads the prompt and returns a canned reply
    text = messages.to_messages()[-1].content  # last message text
    return f"(fake) Answer for: {text}"

chain = prompt | RunnableLambda(fake_llm) | StrOutputParser()  # LCEL pipeline
print(chain.invoke({"product": "wireless earbuds"}))  # run it
# With a real key: from langchain_openai import ChatOpenAI; llm = ChatOpenAI(model="gpt-4o-mini")
```

## 💻 Code Example — Advanced
```python
# Typed, async, provider-swappable tariff chain with fallback and retry
import asyncio
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

class Classification(BaseModel):
    hs_code: str = Field(description="HS code like 8518.30")
    confidence: float = Field(ge=0, le=1)
    reason: str

prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the product. Be concise."),
    ("human", "{product}"),
])

primary = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=20)  # fast + cheap
backup = ChatAnthropic(model="claude-3-5-haiku-latest", temperature=0)  # another provider
llm = primary.with_retry(stop_after_attempt=2).with_fallbacks([backup])  # resilience built in

chain = prompt | llm.with_structured_output(Classification)  # returns a Classification

async def classify(product: str) -> Classification | None:
    try:
        return await chain.ainvoke({"product": product})  # async call
    except Exception as exc:  # both providers failed
        print(f"classification failed: {exc}")
        return None

if __name__ == "__main__":
    print(asyncio.run(classify("bluetooth earbuds")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Req(BaseModel):
    product: str

@app.post("/classify", response_model=Classification)
async def classify_route(req: Req) -> Classification:
    result = await classify(req.product)  # chain from above
    if result is None:
        raise HTTPException(status_code=503, detail="LLM unavailable")  # clean error
    return result
```

---

## 🔗 LangChain / LangGraph Connection
LangChain = components + LCEL for linear flows. **LangGraph** (same company) builds on it for stateful, looping, multi-agent workflows with persistence. Rule of thumb: simple pipelines use LCEL; agents and branching use LangGraph. Both share the same models, prompts and tools.

```python
# LCEL chain can be used as a LangGraph node:
# graph.add_node("classify", lambda state: {"result": chain.invoke({"product": state["product"]})})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using LangChain for a one-call script
```python
# Wrong: 6 imports to call a model once
# Right: use the provider SDK directly when there is one prompt and one call
from openai import OpenAI
```

❌ Mistake 2: Importing from legacy paths
```python
# Wrong
from langchain.chat_models import ChatOpenAI   # removed/legacy
# Right
from langchain_openai import ChatOpenAI
```

---

## 🧠 Tricky Interview Question
**Q**: "Why do some teams drop LangChain in production?"

**Answer**: Common reasons: heavy abstraction hides prompts and makes debugging harder, fast-changing APIs/deprecations, extra dependencies, and simple apps do not need it. Counter: LCEL + LangSmith give transparency, and the 0.3 line stabilised APIs. Good answer: use it where its value (provider swap, retrievers, tracing, LangGraph) outweighs overhead; use raw SDKs for trivial flows.

---

## ⚫ Interview Questions + Answers

Q1: What is LangChain? (Easy)
A1: A framework of composable components and the LCEL pipe syntax for building LLM apps.

Q2: Which packages make up modern LangChain? (Easy)
A2: `langchain-core` (interfaces, LCEL), `langchain` (chains/agents), `langchain-community` (integrations), partner packages like `langchain-openai`, plus `langgraph` and `langsmith`.

Q3: What does a common model interface buy you? (Medium)
A3: Provider portability, uniform `.invoke/.stream/.batch`, easy fallbacks and A/B tests.

Q4: LangChain vs raw OpenAI SDK? (Medium)
A4: SDK: minimal and explicit, best for simple calls. LangChain: higher-level patterns (RAG, tools, memory, tracing) at the cost of abstraction.

Q5: How would you migrate a legacy `LLMChain` app? (Hard)
A5: Replace `LLMChain` with `prompt | llm | parser`, move imports to partner packages, convert memory to LangGraph state/checkpointer, add tests on a golden set before/after, and migrate route by route behind a feature flag.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- RAG, tools, agents, multiple providers
- You want tracing (LangSmith) and shared patterns

❌ Avoid when:
- Single prompt, single call
- Team needs absolute minimal dependencies

---

## 📊 Visual Diagram
```
  Input ─► Prompt ─► Model ─► Parser ─► Output
             │          │         │
        PromptTemplate ChatOpenAI StrOutputParser
             └──── chain = prompt | model | parser ────┘
  Extras: Retriever, Tools, Memory, Callbacks (LangSmith)
```

---

## 💰 Cost Impact
LangChain itself is free; cost is the tokens of your prompts. Pitfalls: hidden extra LLM calls (some legacy chains/agents call the model many times), long default prompts, and memory that re-sends the whole history. Optimise: inspect traces for call count and tokens, trim history, use small models for routing, enable caching (`set_llm_cache`), and set `max_tokens`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LangChain | LLM app framework | LLM apps का framework |
| LCEL | Pipe-based composition | Pipe से जोड़ने की syntax |
| Chain | Connected steps | जुड़े हुए steps |
| Partner package | e.g. langchain-openai | Provider-विशेष package |
| LangSmith | Tracing/eval platform | Tracing और evaluation |

---

## ⚡ 3-Line Summary
English: LangChain provides standard components and LCEL to compose LLM apps. It makes providers swappable and adds retries, streaming and tracing. Use it for RAG, tools and agents; skip it for trivial calls.
Hindi: LangChain standard components और LCEL देता है जिससे LLM apps जुड़ते हैं। Providers बदलना आसान होता है और retries, streaming, tracing मिलते हैं। RAG, tools, agents के लिए लो; छोटे calls के लिए नहीं।

---

## ➡️ Next Topic
**232. LangChain vs LlamaIndex** — which framework to choose for which job.
