---

# 233. LangChain Architecture
# हिंदी में: LangChain की Architecture

---

## 🔵 Simple Definition (English)
LangChain's architecture is a set of layered packages: `langchain-core` (base interfaces + LCEL), `langchain` (chains, agents, retrieval logic), `langchain-community` (third-party integrations), partner packages (`langchain-openai`...), plus `langgraph` (orchestration) and `langsmith` (observability).

## 🔵 सरल परिभाषा (Hindi)
LangChain की architecture layered packages का set है: `langchain-core` (base interfaces + LCEL), `langchain` (chains, agents), `langchain-community` (third-party integrations), partner packages (`langchain-openai`...), साथ में `langgraph` (orchestration) और `langsmith` (observability)।

---

## 🔴 Problem it Solves
Early LangChain was one giant package with hundreds of integrations: huge installs, dependency conflicts, and breaking changes whenever any vendor changed. Splitting it into core + integrations makes installs lighter, versions independent, and the core stable.

## 🔴 यह क्यों बना? (Hindi)
शुरुआती LangChain एक विशाल package था जिसमें सैकड़ों integrations थे: भारी install, dependency conflicts, और किसी vendor के बदलने पर breaking changes। Core + integrations में बाँटने से install हल्का, versions स्वतंत्र और core stable रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → langchain-core: Runnable, messages, prompts, parsers, tools, retriever base
Step 2 → Partner packages implement core interfaces (ChatOpenAI is a Runnable)
Step 3 → langchain-community: long-tail integrations (loaders, vector stores)
Step 4 → langchain: higher-level helpers (create_retrieval_chain, agents)
Step 5 → LCEL composes Runnables with | into chains
Step 6 → langgraph: stateful graphs of Runnables (loops, branches, persistence)
Step 7 → langsmith: callbacks send traces for debugging and evals
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → langchain-core: Runnable, messages, prompts, parsers, tools, retriever base
Step 2 → Partner packages core interfaces implement करते हैं (ChatOpenAI भी Runnable है)
Step 3 → langchain-community: बाकी integrations (loaders, vector stores)
Step 4 → langchain: higher-level helpers (retrieval chain, agents)
Step 5 → LCEL Runnables को | से जोड़ता है
Step 6 → langgraph: state वाले graphs (loops, branches, persistence)
Step 7 → langsmith: callbacks traces भेजते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System** dependencies: `langchain-core` (prompt, parser, Runnable), `langchain-openai` (ChatOpenAI, embeddings), `langchain-community` (PDF loader, BM25), `langchain-text-splitters`, `langchain-chroma` or `langchain-postgres` (vector store), `langgraph` (workflow with review). Only these are installed, so the Docker image stays small. **Zomato**: their bot only needs core + openai + langgraph.

## 🟡 Real Example Hindi mein
**Tariff System** की dependencies: `langchain-core` (prompt, parser, Runnable), `langchain-openai`, `langchain-community` (PDF loader, BM25), `langchain-text-splitters`, `langchain-chroma`/`langchain-postgres`, `langgraph`। सिर्फ यही install होते हैं, इसलिए Docker image छोटी रहती है।

---

## 💻 Code Example — Basic
```python
# Inspect the architecture from code (needs: pip install langchain-core)
from importlib import metadata
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.prompts import PromptTemplate

# 1) Everything is a Runnable:
prompt = PromptTemplate.from_template("Hello {name}")  # prompts are Runnables
fn = RunnableLambda(lambda s: s.text.upper())  # so are functions wrapped with RunnableLambda
print(isinstance(prompt, Runnable), isinstance(fn, Runnable))  # True True

# 2) Chains are Runnables too (RunnableSequence):
chain = prompt | fn
print(type(chain).__name__, "->", chain.invoke({"name": "tariff"}))  # RunnableSequence -> HELLO TARIFF

# 3) Which LangChain packages are installed?
for pkg in ("langchain-core", "langchain", "langchain-community", "langchain-openai", "langgraph"):
    try:
        print(pkg, metadata.version(pkg))  # installed version
    except metadata.PackageNotFoundError:
        print(pkg, "not installed")  # that is fine: packages are separate
```

## 💻 Code Example — Advanced
```python
# Layered design: your code depends on core interfaces; vendors are plugged in at the edge
from typing import Protocol
from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class Deps(Protocol):
    llm: BaseChatModel  # any chat model implementing core interface
    embeddings: Embeddings  # any embeddings
    store: VectorStore  # any vector store

def build_chain(deps: Deps):
    retriever = deps.store.as_retriever(search_kwargs={"k": 4})  # VectorStore -> Retriever
    prompt = ChatPromptTemplate.from_template("Context:\n{context}\n\nQ: {q}")
    fmt = lambda docs: "\n".join(d.page_content for d in docs)  # docs -> text
    return ({"context": retriever | fmt, "q": lambda x: x} | prompt | deps.llm | StrOutputParser())

def make_deps(env: str) -> Deps:
    """Composition root: the ONLY place that imports vendor packages."""
    from types import SimpleNamespace
    if env == "prod":
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        from langchain_chroma import Chroma
        emb = OpenAIEmbeddings(model="text-embedding-3-small")
        return SimpleNamespace(llm=ChatOpenAI(model="gpt-4o-mini"), embeddings=emb,
                               store=Chroma(collection_name="tariff", embedding_function=emb))
    raise ValueError(f"unknown env {env}")  # explicit failure
```

---

## 🟠 FastAPI Integration
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    deps = make_deps("prod")  # build once at startup
    app.state.chain = build_chain(deps)  # chain is reusable and thread-safe to invoke
    yield  # app runs
    # cleanup (close clients) here if needed

app = FastAPI(lifespan=lifespan)

@app.get("/ask")
async def ask(q: str) -> dict:
    return {"answer": await app.state.chain.ainvoke(q)}  # async by default
```

---

## 🔗 LangChain / LangGraph Connection
`langgraph` depends on `langchain-core`: graph nodes can be any Runnable, and LangGraph reuses messages, tools and chat models. Checkpointers (`MemorySaver`, Postgres) add persistence. LangSmith attaches through callbacks/environment variables and traces both layers together.

```python
# graph.add_node("answer", build_chain(deps))   # a core Runnable as a graph node
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Installing the umbrella and importing everything from `langchain`
```python
# Wrong
from langchain.vectorstores import Chroma
# Right
from langchain_chroma import Chroma
```

❌ Mistake 2: Mismatched package versions
```python
# Wrong: langchain-core 0.1 with langchain-openai 0.3 -> import errors
# Right: pin compatible versions in requirements (pip install -U together; use a lockfile)
```

---

## 🧠 Tricky Interview Question
**Q**: "Why can `ChatOpenAI` be piped into a prompt even though it lives in a different package?"

**Answer**: Because it implements the `Runnable` interface defined in `langchain-core` (via `BaseChatModel`). `|` is defined on `Runnable` (`__or__`), so anything implementing the interface composes. Partner packages depend only on core, not on each other.

---

## ⚫ Interview Questions + Answers

Q1: What lives in langchain-core? (Easy)
A1: Base abstractions: Runnable, messages, prompts, output parsers, tools, retrievers, vector store and embedding interfaces, and LCEL.

Q2: What is langchain-community? (Easy)
A2: Third-party integrations maintained by the community that don't have their own partner package.

Q3: Why partner packages? (Medium)
A3: Independent versioning, smaller deps, vendor-specific features, tests owned by the vendor/maintainers.

Q4: How does LangSmith fit the architecture? (Medium)
A4: Via callbacks/tracers on every Runnable; no code change needed beyond env vars. It records inputs, outputs, latency and tokens per step.

Q5: How would you structure a large app around LangChain? (Hard)
A5: Domain layer with Protocols; adapters wrapping LangChain/LangGraph; composition root for wiring; config-driven model/vector store; tests with fake models (`FakeListChatModel`); pinned dependency lockfile; tracing enabled.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want to depend on stable core interfaces and swap vendors

❌ Avoid when:
- You import deep internals (private modules) that change often

---

## 📊 Visual Diagram
```
 ┌───────────────────── your app ─────────────────────┐
 │                                                    │
 │  langgraph (stateful flows)      langsmith (traces)│
 │        │                              ▲            │
 │  langchain (chains/agents)            │ callbacks  │
 │        │                              │            │
 │  langchain-community  langchain-openai  langchain-chroma ...
 │        └──────────────┬──────────────┘            │
 │                langchain-core (Runnable, LCEL)     │
 └────────────────────────────────────────────────────┘
```

---

## 💰 Cost Impact
Architecture affects infra cost more than token cost: fewer packages = smaller images and cold starts. Token cost depends on how high-level helpers build prompts: check what a chain actually sends (LangSmith trace). Optimise: use core primitives you can inspect, avoid helpers that silently add history, enable caching at the model layer.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| langchain-core | Base interfaces + LCEL | बुनियादी interfaces |
| Partner package | Vendor integration package | Vendor का package |
| Runnable | Common callable interface | Common interface |
| Composition root | Single wiring place | Wiring की एक जगह |
| Callback/Tracer | Hook for tracing | Trace करने का hook |

---

## ⚡ 3-Line Summary
English: LangChain is layered: core interfaces, higher-level langchain, community and partner integrations, plus LangGraph and LangSmith. Everything implements Runnable so it composes with `|`. Keep vendor imports at the edge.
Hindi: LangChain layered है: core interfaces, langchain, community/partner integrations, साथ में LangGraph और LangSmith। सब Runnable implement करते हैं इसलिए `|` से जुड़ते हैं। Vendor imports किनारे पर रखो।

---

## ➡️ Next Topic
**234. LangChain v0.1 vs v0.2 vs v0.3** — what changed across versions and how to migrate.
