---

# 186. Modular RAG
# हिंदी में: Modular RAG (मॉड्यूलर RAG)

---

## 🔵 Simple Definition (English)
Modular RAG breaks a RAG system into independent, swappable modules (router, retriever, reranker, generator, validator) connected by a flexible flow. A router decides per query which modules run, so simple questions take a cheap path and hard ones take a deeper path.

## 🔵 सरल परिभाषा (Hindi)
Modular RAG, RAG system को independent और swappable modules (router, retriever, reranker, generator, validator) में तोड़ता है जो flexible flow से जुड़े होते हैं। Router हर query के लिए तय करता है कौन से modules चलें: आसान सवाल सस्ते रास्ते से, कठिन सवाल गहरे रास्ते से।

---

## 🔴 Problem it Solves
A fixed linear pipeline treats "What is HS code for tea?" and "Compare duties for 3 products across 2 countries" the same. That wastes money on easy queries and under-serves hard ones. Hard-wired pipelines are also difficult to test, upgrade (swap the vector DB) or extend (add a SQL module).

## 🔴 यह क्यों बना? (Hindi)
Fixed linear pipeline "चाय का HS code?" और "3 products की 2 देशों में duty compare करो" को एक जैसा treat करता है। आसान queries पर पैसा बर्बाद, कठिन queries पर कम quality। Hard-wired pipeline को test, upgrade (vector DB बदलना) या extend (SQL module जोड़ना) करना भी मुश्किल है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a common interface: every module takes a State and returns a State
Step 2 → Build modules: router, rewriter, retriever(s), reranker, generator, validator
Step 3 → Router classifies the query (simple lookup / multi-hop / SQL / chit-chat)
Step 4 → Flow engine runs only the modules on that route (sequence, branch, loop)
Step 5 → Validator checks grounding; if it fails, loop back (max N times)
Step 6 → Swap or A/B test one module without touching the others
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Common interface: हर module State लेता है और State लौटाता है
Step 2 → Modules बनाओ: router, rewriter, retriever, reranker, generator, validator
Step 3 → Router query classify करता है (simple / multi-hop / SQL / chit-chat)
Step 4 → Flow engine सिर्फ उसी route के modules चलाता है
Step 5 → Validator grounding जाँचता है; fail हो तो loop (max N बार)
Step 6 → एक module बदलो या A/B test करो, बाकी को छुए बिना
```

---

## 🟡 Real World Example
**Tariff Classification System**: Route A "lookup" (one HS code question) goes retriever, generator (1 LLM call). Route B "comparison" goes decomposer, parallel retrievers, generator. Route C "rate table" goes text-to-SQL module over the duty-rate database. Route D "chit-chat" skips retrieval completely.
**Amazon AI**: "Where is my order?" routes to the order API module, while "best laptop under 50k" routes to the product-search RAG module.

## 🟡 Real Example Hindi mein
**Tariff System**: Route A "lookup" में retriever + generator (1 LLM call)। Route B "comparison" में decomposer + parallel retrievers + generator। Route C "rate table" में text-to-SQL module। Route D "chit-chat" में retrieval बिल्कुल नहीं।
**Amazon AI**: "मेरा order कहाँ है?" -> order API module; "50k से कम best laptop" -> product-search RAG module।

---

## 💻 Code Example — Basic
```python
# Basic modular RAG: modules share one interface (dict in -> dict out), router picks the path
from typing import Callable, Dict, List

State = Dict[str, object]  # shared state passed between modules
Module = Callable[[State], State]  # every module has the same signature

def router(state: State) -> State:
    """Classify the query into a route."""
    q = str(state["query"]).lower()  # normalise
    if any(w in q for w in ("compare", "versus", " vs ")):  # multi-part question
        state["route"] = "comparison"
    elif any(w in q for w in ("hello", "thanks")):  # small talk
        state["route"] = "chitchat"
    else:
        state["route"] = "lookup"  # default simple lookup
    return state  # modules always return state

def retriever(state: State) -> State:
    """Toy retriever returning canned chunks."""
    state["chunks"] = ["8517.13 smartphones duty 0", "8471.30 laptops duty 0"]  # fake hits
    return state

def generator(state: State) -> State:
    """Toy generator that echoes the first chunk."""
    chunks: List[str] = state.get("chunks", [])  # type: ignore[assignment]
    state["answer"] = chunks[0] if chunks else "Hi! Ask me about tariffs."  # fallback
    return state

# Route table: route name -> ordered list of modules
ROUTES: Dict[str, List[Module]] = {
    "lookup": [retriever, generator],
    "comparison": [retriever, retriever, generator],  # placeholder for decomposer path
    "chitchat": [generator],  # no retrieval at all
}

def run(query: str) -> str:
    state: State = router({"query": query})  # step 1: route
    for module in ROUTES[str(state["route"])]:  # step 2: run modules of that route
        state = module(state)
    return str(state["answer"])  # final answer

if __name__ == "__main__":
    for q in ("duty on smartphones", "hello", "compare phones vs laptops"):  # three routes
        print(q, "->", run(q))  # print result per query
```

## 💻 Code Example — Advanced
```python
# Async modular pipeline: registry, per-module timeout, error isolation, token accounting
import asyncio
import logging
from typing import Awaitable, Callable, Dict, List, TypedDict

logger = logging.getLogger("modular_rag")  # logger

class RagState(TypedDict, total=False):
    query: str  # user question
    route: str  # chosen route
    chunks: List[str]  # retrieved context
    answer: str  # final answer
    tokens: int  # running token estimate
    errors: List[str]  # non-fatal module errors

AsyncModule = Callable[[RagState], Awaitable[RagState]]  # async module type

class Pipeline:
    """Runs modules by route; a failing optional module is skipped, not fatal."""

    def __init__(self, routes: Dict[str, List[AsyncModule]], optional: set[str],
                 timeout_s: float = 5.0) -> None:
        self.routes, self.optional, self.timeout_s = routes, optional, timeout_s  # config

    async def run(self, state: RagState) -> RagState:
        state.setdefault("errors", [])  # init error list
        state.setdefault("tokens", 0)  # init token counter
        for module in self.routes[state["route"]]:  # modules for this route
            name = module.__name__  # module id
            try:
                state = await asyncio.wait_for(module(state), self.timeout_s)  # bounded time
            except Exception as exc:  # timeout or module bug
                logger.exception("module %s failed", name)
                state["errors"].append(f"{name}: {exc!r}")  # record
                if name not in self.optional:  # required modules abort the run
                    state["answer"] = "Service temporarily unavailable."
                    break
        return state

async def rerank(state: RagState) -> RagState:
    state["chunks"] = sorted(state["chunks"], key=len)[:2]  # toy rerank
    return state

async def retrieve(state: RagState) -> RagState:
    state["chunks"] = ["8504.40 adapters duty 0", "8517.13 phones duty 0", "6403 shoes duty 20"]
    state["tokens"] += 30  # rough cost accounting
    return state

async def generate(state: RagState) -> RagState:
    state["answer"] = f"Answer from {len(state['chunks'])} chunks"  # replace with LLM call
    state["tokens"] += 120
    return state

if __name__ == "__main__":
    pipe = Pipeline({"lookup": [retrieve, rerank, generate]}, optional={"rerank"})  # rerank optional
    out = asyncio.run(pipe.run({"query": "duty on adapters", "route": "lookup"}))  # run
    print(out["answer"], out["tokens"], out["errors"])  # show result
```

---

## 🟠 FastAPI Integration
Keep the module registry and route table in config, and build the `Pipeline` at startup. The API layer stays thin: validate input, call the router, run the pipeline, return answer + route + token estimate. Because modules are isolated, you can feature-flag a new reranker for 10 percent of traffic.

```python
# FastAPI route that exposes the chosen route and cost
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()  # app

class Q(BaseModel):
    query: str  # user question

@app.post("/ask")
async def ask(q: Q) -> dict:
    route = "comparison" if " vs " in q.query.lower() else "lookup"  # cheap router (swap for LLM router)
    state = await pipe.run({"query": q.query, "route": route})  # pipe from the Advanced example
    return {"answer": state.get("answer"), "route": route, "tokens": state.get("tokens", 0),
            "degraded": bool(state.get("errors"))}  # tell client if modules failed
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph is a natural fit: each module is a node, the router is a conditional edge, the validator creates a loop. `RunnableBranch` in LCEL handles simple routing.

```python
# LangGraph modular RAG: router -> (lookup | chitchat) -> END
from typing import TypedDict
from langgraph.graph import StateGraph, END

class S(TypedDict, total=False):
    query: str  # input
    answer: str  # output

def lookup(s: S) -> S: return {"answer": "retrieved answer"}  # retrieval+generation node
def chitchat(s: S) -> S: return {"answer": "Hello! Ask about tariffs."}  # no-retrieval node
def pick(s: S) -> str: return "chitchat" if "hello" in s["query"].lower() else "lookup"  # router edge

g = StateGraph(S)  # graph over state schema
g.add_node("lookup", lookup); g.add_node("chitchat", chitchat)  # modules
g.set_conditional_entry_point(pick, {"lookup": "lookup", "chitchat": "chitchat"})  # routing
g.add_edge("lookup", END); g.add_edge("chitchat", END)  # finish
app_graph = g.compile()  # runnable
print(app_graph.invoke({"query": "hello"}))  # {'query': 'hello', 'answer': 'Hello! ...'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Modules that read and write hidden globals, so they cannot be swapped.
✅ Correct: Pass everything through an explicit State object with a typed schema.

```python
# Wrong
CURRENT_CHUNKS = []
def rerank(): global CURRENT_CHUNKS; ...
# Right
def rerank(state: RagState) -> RagState: ...
```

❌ Mistake 2: Using an expensive LLM router for every request.
✅ Correct: Start with rules or a small classifier/embedding router; call an LLM router only for ambiguous queries.

```python
# Wrong: gpt-4o call just to decide "hello" is chit-chat
# Right: regex/keyword first, small model fallback
```

---

## 🧠 Tricky Interview Question
**Q**: "How is Modular RAG different from Advanced RAG? Isn't it the same stages?"

**Answer**: Advanced RAG is still mostly a fixed sequence of better stages. Modular RAG changes the architecture: modules are decoupled behind interfaces, and the flow is dynamic (routing, branching, looping, parallel). Same building blocks, different control flow. The practical gains are per-query cost control, independent testing and easy replacement of components.

---

## ⚫ Interview Questions + Answers

Q1: What is a router in Modular RAG?
A1: A module that classifies the query and picks the path: which retriever, whether to retrieve at all, SQL vs vector, etc.

Q2: Give two benefits of modularity.
A2: Swap components (new vector DB, new reranker) with no rewrite; test and monitor each module separately.

Q3: How do you keep latency low with many modules?
A3: Run independent modules in parallel (`asyncio.gather`), skip modules via routing, set per-module timeouts, make non-essential ones optional.

Q4: How do you test a modular pipeline?
A4: Unit test each module with fixed State input/output, then run end-to-end evals with a labeled set and measure per-route metrics.

Q5: Design a self-correcting modular RAG for tariffs.
A5: Router, retriever, grader (are chunks relevant?), conditional edge: if no, rewrite and retry up to 2 times, else generate; validator checks the answer is supported by context; if not, abstain. Implement as a LangGraph with a retry counter in State and per-node token logging for cost caps.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple data sources (vector, SQL, API) or query types
- You need per-query cost/latency control
- Many engineers or frequent component upgrades

❌ Avoid when:
- Single data source, uniform queries
- Small team, early prototype (a simple chain is easier to debug)

---

## 📊 Visual Diagram
```
                 ┌──────────┐
   query ───────►│  ROUTER  │
                 └────┬─────┘
        ┌─────────────┼───────────────┐
        ▼             ▼               ▼
   [lookup]     [comparison]       [sql]
   retrieve      decompose        text2sql
   generate    ┌─►retrieve×N         │
        │      │   generate          │
        └──────┴──────┬──────────────┘
                      ▼
                 [VALIDATOR] ──fail──► back to retrieve (max 2)
                      │ ok
                      ▼
                    Answer
```

---

## 💰 Cost Impact
Routing saves money: 70 percent of queries are simple lookups (about 1 LLM call, ~800 tokens), while only 10 percent need decomposition (3-4 calls, ~3000 tokens). Average cost drops compared with running the deepest pipeline for everything. Router cost: rules are free; a small LLM router is ~100 tokens per query.
Optimize: cache router decisions, cap loop iterations, log tokens per module and set budgets.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Module | Swappable pipeline component | बदलने लायक component |
| Router | Picks the path for a query | Query का रास्ता चुनने वाला |
| State | Shared data between modules | Modules के बीच shared data |
| Flow engine | Runs modules in the chosen order | Modules चलाने वाला engine |
| Validator | Checks answer grounding | Answer की जाँच करने वाला |
| Fallback | Backup path on failure | Fail होने पर backup |

---

## ⚡ 3-Line Summary
English: Modular RAG splits the pipeline into swappable modules and a routing flow.
Simple queries take a cheap path, hard queries take a deeper path.
It improves cost control, testing and upgrades, at the price of more design effort.
Hindi: Modular RAG pipeline को swappable modules और routing flow में बाँटता है।
आसान queries सस्ते रास्ते से और कठिन queries गहरे रास्ते से जाती हैं।
इससे cost control, testing और upgrade आसान होते हैं, पर design में ज़्यादा मेहनत लगती है।

---

## ➡️ Next Topic
**187. RAG Pipeline Components**: a closer look at each building block (loader, splitter, embedder, store, retriever, generator) that modules are made of.
