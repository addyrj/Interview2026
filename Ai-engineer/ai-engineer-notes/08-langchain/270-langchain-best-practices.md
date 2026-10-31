---

# 270. LangChain Best Practices
# हिंदी में: LangChain Best Practices (Production के नियम)

---

## 🔵 Simple Definition (English)
LangChain best practices are the rules that turn a demo chain into a reliable service: use LCEL, keep prompts versioned, return structured output, set timeouts/retries, test with fake models, trace everything, keep dependencies injected, and use LangGraph when you need loops or state.

## 🔵 सरल परिभाषा (Hindi)
LangChain best practices वे नियम हैं जो demo chain को भरोसेमंद service बनाते हैं: LCEL use करो, prompts को version करो, structured output लो, timeout/retry लगाओ, fake models से test करो, सब कुछ trace करो, dependencies inject करो, और loops या state चाहिए तो LangGraph use करो।

---

## 🔴 Problem it Solves
Typical beginner LangChain code: a 300-line notebook, prompt strings inside functions, a global `llm`, `print()` for debugging, no tests, no timeouts, a deprecated API (`LLMChain`, `initialize_agent`) and unpredictable string output. It works on a demo day and breaks in production, and nobody can change the prompt safely.

## 🔴 यह क्यों बना? (Hindi)
Beginner का LangChain code अक्सर 300 line का notebook होता है: prompt strings functions के अंदर, global `llm`, debug के लिए `print()`, कोई test नहीं, कोई timeout नहीं, deprecated API (`LLMChain`, `initialize_agent`) और unpredictable string output। Demo में चलता है, production में टूटता है, और prompt बदलना असुरक्षित होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Structure: prompts/, chains/, tools/, api/, tests/ -- one responsibility per file
Step 2 → Compose with LCEL (prompt | model | parser); avoid legacy Chain classes
Step 3 → Prompts as versioned constants/files; variables explicit; no f-string prompt building
Step 4 → Output: with_structured_output(PydanticModel) instead of parsing free text
Step 5 → Reliability: timeout, max_retries (one layer), fallbacks, max_tokens, concurrency cap
Step 6 → Build chains once at startup; inject the model (dependency injection) for tests
Step 7 → Observe + test: tracing with tags, unit tests with fake models, eval set for quality
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Structure: prompts/, chains/, tools/, api/, tests/ -- हर file की एक ज़िम्मेदारी
Step 2 → LCEL से compose करो (prompt | model | parser); legacy Chain classes से बचो
Step 3 → Prompts versioned constants/files में; variables साफ; f-string से prompt मत बनाओ
Step 4 → Output: free text parse करने की जगह with_structured_output(PydanticModel)
Step 5 → Reliability: timeout, max_retries (एक ही layer में), fallbacks, max_tokens, concurrency cap
Step 6 → Chains startup पर एक बार बनाओ; model inject करो ताकि test हो सके
Step 7 → Observe + test: tags के साथ tracing, fake models से unit tests, quality के लिए eval set
```

---

## 🟡 Real World Example
**Tariff Classification System** (project layout):
```
app/
  prompts/classify_v3.py     # PROMPT_VERSION = "v3", the template
  chains/classify.py         # build_classify_chain(llm) -> Runnable
  schemas.py                 # HSResult (pydantic)
  api.py                     # FastAPI routes
tests/test_classify.py       # fake model tests, golden examples
evals/golden.jsonl           # 200 labelled products
```
Changing `v3 -> v4` of the prompt runs the golden set first (accuracy must not drop), then ships with tag `prompt_v4` so traces compare both versions. The model is injected, so tests run in 50 ms with no API key.

**Zomato/Amazon-style**: Same structure per feature: one chain per use case, shared tools, one graph for the multi-step agent.

## 🟡 Real Example Hindi mein
**Tariff System** (project layout): ऊपर वाला folder structure। Prompt को `v3 -> v4` बदलने पर पहले golden set (200 labelled products) चलता है (accuracy गिरनी नहीं चाहिए), फिर `prompt_v4` tag के साथ ship होता है ताकि traces में दोनों versions compare हों। Model inject होता है, इसलिए tests बिना API key के 50 ms में चलते हैं।

**Zomato/Amazon-style**: हर feature में यही structure: use case के लिए एक chain, shared tools, multi-step agent के लिए एक graph।

---

## 💻 Code Example — Basic
```python
# Best-practice skeleton: versioned prompt + injected model + pure chain builder + fake-model test
# Runs OFFLINE. pip install langchain-core pydantic
import json                                                        # to feed fake JSON output
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel  # fake LLM
from langchain_core.messages import AIMessage                      # message
from langchain_core.output_parsers import PydanticOutputParser     # JSON -> pydantic object
from langchain_core.prompts import ChatPromptTemplate              # prompt
from langchain_core.language_models import BaseChatModel           # type for dependency injection
from langchain_core.runnables import Runnable                      # return type of the builder
from pydantic import BaseModel, Field                              # pydantic v2

PROMPT_VERSION = "classify_v3"                                     # explicit version, appears in traces


class HSResult(BaseModel):                                         # structured output schema
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")                # validated format e.g. 8518.30
    confidence: float = Field(ge=0.0, le=1.0)                      # range-checked


parser = PydanticOutputParser(pydantic_object=HSResult)            # validates model output

PROMPT = ChatPromptTemplate.from_messages([                        # prompt lives in ONE place
    ("system", "You are a customs tariff expert. {format_instructions}"),
    ("user", "Product: {product}"),
]).partial(format_instructions=parser.get_format_instructions())   # fill constant parts once


def build_classify_chain(llm: BaseChatModel) -> Runnable[dict, HSResult]:
    """Pure function: model in, chain out. Easy to test and to swap models."""
    return (PROMPT | llm | parser).with_config(                    # LCEL composition
        run_name="classify", tags=[PROMPT_VERSION]                 # trace labels
    )


# ---- test with a fake model (no network, no cost) ----
good = AIMessage(content=json.dumps({"hs_code": "8518.30", "confidence": 0.93}))  # valid answer
chain = build_classify_chain(GenericFakeChatModel(messages=iter([good])))          # inject fake
out = chain.invoke({"product": "wireless earbuds"})                # run
assert out.hs_code == "8518.30" and out.confidence > 0.9           # golden check
print("OK ->", out)                                                # show typed result

bad = AIMessage(content=json.dumps({"hs_code": "85183", "confidence": 2}))  # invalid answer
chain_bad = build_classify_chain(GenericFakeChatModel(messages=iter([bad])))  # inject bad fake
try:
    chain_bad.invoke({"product": "x"})                             # parser must reject
except Exception as exc:                                           # OutputParserException expected
    print("rejected invalid output ->", type(exc).__name__)        # validation worked
```

## 💻 Code Example — Advanced
```python
# Production wiring: settings, structured output, reliability, caching hook, async, tracing config
# pip install langchain-openai langchain-core pydantic pydantic-settings
import logging                                                     # logs
from functools import lru_cache                                    # build once, reuse
from typing import Any                                             # hints

from langchain_core.language_models import BaseChatModel           # DI type
from langchain_core.prompts import ChatPromptTemplate              # prompt
from langchain_openai import ChatOpenAI                            # model
from pydantic import BaseModel, Field                              # schema
from pydantic_settings import BaseSettings                         # typed config from env

logger = logging.getLogger("tariff.chain")                         # logger


class Settings(BaseSettings):                                      # all knobs in one place (env vars)
    primary_model: str = "gpt-4o-mini"                             # default cheap model
    fallback_model: str = "gpt-4o"                                 # stronger model as backup
    request_timeout: int = 20                                      # seconds per call
    max_output_tokens: int = 150                                   # cost cap
    max_concurrency: int = 10                                      # batch parallelism
    prompt_version: str = "classify_v3"                            # shown in traces


class HSResult(BaseModel):                                         # output schema
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")                # strict format
    confidence: float = Field(ge=0, le=1)                          # 0..1
    reasoning: str = Field(max_length=300)                         # short explanation


def make_llm(name: str, s: Settings) -> BaseChatModel:
    return ChatOpenAI(                                             # one place that configures models
        model=name, temperature=0, timeout=s.request_timeout,      # deterministic + timeout
        max_tokens=s.max_output_tokens, max_retries=0,             # retries are handled in the chain
    )


@lru_cache(maxsize=1)                                              # build once per process
def get_settings() -> Settings:
    return Settings()                                              # reads env


PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a customs tariff expert. Use official HS format NNNN.NN."),
    ("user", "Product: {product}"),
])


def build_chain(s: Settings):
    primary = PROMPT | make_llm(s.primary_model, s).with_structured_output(HSResult)    # schema enforced by provider
    backup = PROMPT | make_llm(s.fallback_model, s).with_structured_output(HSResult)    # same schema, stronger model
    return (
        primary.with_retry(stop_after_attempt=2, wait_exponential_jitter=True)          # one retry layer
        .with_fallbacks([backup])                                                       # then stronger model
        .with_config(run_name="classify", tags=[s.prompt_version])                      # tracing labels
    )


@lru_cache(maxsize=1)
def get_chain():
    return build_chain(get_settings())                             # singleton chain, not rebuilt per request


async def classify(product: str, user_id: str) -> HSResult:
    cfg: dict[str, Any] = {"metadata": {"user_id": user_id}}       # per-request trace metadata
    try:
        return await get_chain().ainvoke({"product": product}, config=cfg)  # async + typed result
    except Exception:
        logger.exception("classification failed")                  # log with traceback
        raise                                                      # API layer converts to HTTP error
```

---

## 🟠 FastAPI Integration
Use FastAPI **dependency injection** and **lifespan** so chains are built once and tests can override them. Convert domain errors to HTTP codes. Keep the route thin: validate, call chain, shape the response.

```python
# FastAPI app: thin routes + DI + lifespan
from contextlib import asynccontextmanager                         # lifespan helper
from fastapi import Depends, FastAPI, HTTPException                # framework
from pydantic import BaseModel, Field                              # validation

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.chain = get_chain()                                  # warm up at startup (fail fast on bad config)
    yield                                                          # app runs
    # shutdown: close clients/pools here if needed

app = FastAPI(lifespan=lifespan)                                   # create app

class Req(BaseModel):                                              # input schema
    product: str = Field(min_length=2, max_length=300)             # reject junk early

def chain_dep():                                                   # dependency returns the chain
    return get_chain()                                             # tests: app.dependency_overrides[chain_dep]=fake

@app.post("/classify", response_model=HSResult)                    # typed response
async def classify_route(req: Req, chain=Depends(chain_dep)) -> HSResult:
    try:
        return await chain.ainvoke({"product": req.product})       # thin route
    except Exception as exc:
        raise HTTPException(status_code=502, detail="classification unavailable") from exc

@app.get("/healthz")                                               # health check, no LLM call
async def healthz() -> dict[str, str]:
    return {"status": "ok"}                                        # cheap liveness probe
```

---

## 🔗 LangChain / LangGraph Connection
**LangChain vs LangGraph rule of thumb**: straight line (A -> B -> C), no loops = LCEL chain. Branching, loops, retries-with-state, human approval, multiple agents, long-running resume = **LangGraph** (state + checkpointer).

Current-API checklist:
- Use `langchain-core` interfaces, provider packages (`langchain-openai`, `langchain-anthropic`), not the old monolithic imports.
- Prefer `with_structured_output`, `bind_tools`, `create_react_agent` / LangGraph over `LLMChain`, `AgentExecutor`, `initialize_agent` (legacy).
- Pin versions (`langchain-core==x.y.z`) in `requirements.txt` - minor versions move fast; read changelogs before upgrading.
- Keep chains stateless; put conversation/state in LangGraph state or your DB.

```python
# Minimal LangGraph for a flow that needs a loop (retry when confidence is low)
from typing import TypedDict                                       # state type
from langgraph.graph import END, START, StateGraph                # graph API

class S(TypedDict):                                                # graph state
    product: str                                                   # input
    result: dict                                                   # last result
    tries: int                                                     # loop counter

async def run(s: S) -> dict:                                       # node: classify
    r = await get_chain().ainvoke({"product": s["product"]})       # call chain
    return {"result": r.model_dump(), "tries": s["tries"] + 1}     # partial state update

def route(s: S) -> str:                                            # conditional edge
    return END if s["result"]["confidence"] >= 0.8 or s["tries"] >= 2 else "run"  # loop at most twice

g = StateGraph(S)                                                  # builder
g.add_node("run", run)                                             # add node
g.add_edge(START, "run")                                           # entry
g.add_conditional_edges("run", route)                              # loop or finish
graph = g.compile()                                                # ready: await graph.ainvoke({...})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building the model/chain inside the request handler
```python
# Wrong -- new client + connection pool on every request; slow and leaks sockets
@app.post("/x")
async def x(r: Req):
    chain = PROMPT | ChatOpenAI(model="gpt-4o") | StrOutputParser()
    return await chain.ainvoke(...)

# Right -- build once (lifespan / lru_cache) and reuse
```

❌ Mistake 2: Parsing free text with regex / `split()`
```python
# Wrong
text = llm.invoke(p).content; code = text.split("HS code:")[1][:7]    # breaks when wording changes

# Right
result = llm.with_structured_output(HSResult).invoke(p)                # validated pydantic object
```

❌ Mistake 3: Using legacy APIs (`LLMChain`, `.run()`, `initialize_agent`) or hard-coding API keys in code. Use LCEL + env vars/secret manager.

❌ Mistake 4: Testing only by hand against the real API. Use fake models for unit tests and a small golden set for quality checks.

---

## 🧠 Tricky Interview Question

**Q**: "A prompt tweak that 'obviously improves' answers was shipped, and two weeks later accuracy had dropped 8% but nobody noticed. What process failures led to this, and how do you prevent it?"

**Answer**: (1) No evaluation set - quality was judged by a few hand-picked examples. (2) The prompt was not versioned, so traces could not be compared before and after. (3) No monitoring of quality signals (user corrections, low confidence rate). Prevention: keep prompts in version control with a version tag in every trace; maintain a golden dataset (100-500 labelled cases, including past failures) and run it in CI - fail the build if accuracy drops by more than a threshold; deploy gradually (canary 5%), compare metrics by tag, and roll back by config. Use LLM-as-judge only as a supplement to labelled data, and track drift weekly.

---

## ⚫ Interview Questions + Answers

Q1: Why prefer LCEL over the old `LLMChain`?
A1: LCEL gives one uniform interface (`invoke/stream/batch` + async), automatic streaming and parallelism, built-in retry/fallback and tracing. `LLMChain` and friends are legacy and deprecated.

Q2: Why should chains be built once?
A2: Building creates model clients and HTTP pools. Doing it per request wastes time and resources. Build at startup (lifespan or cached factory) and reuse - chains are stateless and safe to share.

Q3: What is dependency injection in this context and why does it help?
A3: Pass the model (or the whole chain) in as an argument instead of creating it inside the function. Tests pass a fake model; production passes `ChatOpenAI`; changing providers touches one place.

Q4: How do you make LLM output reliable for downstream code?
A4: `with_structured_output(PydanticModel)` (provider-enforced JSON/tool call), Pydantic validation with constraints, `temperature=0`, retries on parse failure, and fallbacks. Never `eval()` or regex-parse free text.

Q5 (Hard): When would you choose LangGraph over a plain LCEL chain, and what changes in testing and deployment?
A5: Choose LangGraph when the control flow depends on results: loops (retry until confident), branches (route by product type), tool-using agents, human approval, parallel sub-tasks with a join, or long jobs that must resume after a crash (checkpointer + thread_id). Testing: unit-test each node as a plain function with fake models; test routing functions separately; run whole-graph tests with scripted fake responses and assert the path taken. Deployment: persist checkpoints in Postgres/Redis (not in-memory), set recursion limits to stop infinite loops, add per-node retry policies and timeouts, and trace with node-level tags. Keep LCEL for the simple pieces inside nodes.

---

## 🔷 When to Use + When Not to Use
✅ Use LangChain when:
- You need many providers/tools/retrievers behind one interface
- Tracing, retries, streaming and structured output are needed quickly
- Building agents or RAG with LangGraph

❌ Consider avoiding / simplifying when:
- A single API call with a fixed prompt (the provider SDK alone is simpler and has fewer dependencies)
- Hard latency budgets where abstraction overhead matters (rare - overhead is small compared to LLM time)
- Team cannot track fast API changes (pin versions, wrap LangChain behind your own interface)

---

## 📊 Visual Diagram
```
                ┌──────────────── FastAPI (thin) ────────────────┐
 request ─────► │ validate (Pydantic) ─► Depends(chain) ─► route │
                └───────────────────────────┬────────────────────┘
                                            ▼
                  chains/classify.py  (built once, injected model)
                  PROMPT(v3) | llm.with_structured_output(HSResult)
                       │ with_retry(2) ─► with_fallbacks([gpt-4o])
                       ▼
                  tracing tags: prompt_v3, user_id  ──► LangSmith / metrics
 CI:  tests (fake LLM)  +  golden set accuracy gate  ─► deploy (canary) ─► monitor
```

---

## 💰 Cost Impact
- Structured output removes "repair" retries and long chatty answers: typically 20-40% fewer output tokens.
- `max_tokens`, `temperature=0`, cheap primary model + strong fallback: if 90% of requests are handled by gpt-4o-mini, blended cost is about 0.9 x $0.15 + 0.1 x $2.50 = about $0.39 per 1M input tokens vs $2.50 all-gpt-4o (check current prices). That is roughly 6x cheaper.
- Cache (268) for repeats; prompt caching for long static system prompts; trim retrieval context (269 traces show where tokens go).
- Guard against runaway agent loops: `recursion_limit` in LangGraph, max iterations, per-request token budget.
- CI evals cost tokens too (200 cases x ~700 tokens x $0.15/1M = about $0.02 per run) - cheap insurance.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LCEL | Pipe-style way to compose Runnables | Runnables जोड़ने का pipe तरीका |
| Dependency injection | Pass dependencies in, do not create inside | Dependencies बाहर से देना |
| Structured output | Typed, validated model output | Typed और validated output |
| Golden set | Labelled examples for regression tests | Regression test के लिए labelled examples |
| Prompt versioning | Tracking prompt changes like code | Prompt बदलाव का version रखना |
| Canary release | Ship to small % first | पहले थोड़े users को देना |
| Recursion limit | Max steps in a graph | Graph के steps की सीमा |
| Legacy API | Old deprecated interfaces | पुराने deprecated interfaces |

---

## ⚡ 3-Line Summary
English: Compose with LCEL, version prompts, get structured output, and build chains once with injected models. Add timeouts, one retry layer, fallbacks, tracing tags and a golden-set CI gate. Use LangGraph only when you need loops, state or resumability.
Hindi: LCEL से compose करो, prompts version करो, structured output लो, और chains एक बार बनाकर model inject करो। Timeout, एक retry layer, fallbacks, tracing tags और golden-set CI gate जोड़ो। Loops, state या resume चाहिए तभी LangGraph use करो।

---

## ➡️ Next Topic
**271. Tool Use - What + Why** - how an LLM can call functions (search, database, calculators) and why this turns a text generator into an agent.
