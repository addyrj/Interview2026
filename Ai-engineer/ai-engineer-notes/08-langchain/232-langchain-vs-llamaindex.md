---

# 232. LangChain vs LlamaIndex
# हिंदी में: LangChain बनाम LlamaIndex

---

## 🔵 Simple Definition (English)
LangChain is a general toolkit for building LLM workflows, agents and tools. LlamaIndex is a data-first framework focused on ingesting, indexing and querying your documents (RAG). They overlap on RAG and are often used together.

## 🔵 सरल परिभाषा (Hindi)
LangChain LLM workflows, agents और tools बनाने का general toolkit है। LlamaIndex data-first framework है जो documents को ingest, index और query करने (RAG) पर focus करता है। RAG में दोनों overlap करते हैं और अक्सर साथ इस्तेमाल होते हैं।

---

## 🔴 Problem it Solves
Teams ask "which one should we pick?" and waste weeks. Picking wrong means fighting the framework: using LangChain for complex document hierarchies (more boilerplate) or LlamaIndex for multi-step tool-using agents (fewer primitives). This note gives a decision framework.

## 🔴 यह क्यों बना? (Hindi)
Teams पूछती हैं "कौन सा चुनें?" और हफ्ते बर्बाद करती हैं। गलत चुनाव = framework से लड़ाई: जटिल document hierarchy के लिए LangChain (ज़्यादा boilerplate) या multi-step tool agents के लिए LlamaIndex (कम primitives)। यह note decision framework देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List the main job: document Q&A? agents? workflows?
Step 2 → Doc-heavy RAG (many formats, hierarchies, indexes) -> LlamaIndex strong
Step 3 → Tools, agents, branching, state machines -> LangChain + LangGraph strong
Step 4 → Need both? use LlamaIndex as retriever inside a LangChain/LangGraph app
Step 5 → Check: team skills, ecosystem, observability, deployment
Step 6 → Prototype both on 20 real questions; compare accuracy, code size, latency
Step 7 → Decide; wrap behind your own interface to stay swappable
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → मुख्य काम लिखो: document Q&A? agents? workflows?
Step 2 → Doc-heavy RAG (कई formats, hierarchies) -> LlamaIndex मज़बूत
Step 3 → Tools, agents, branching, state machines -> LangChain + LangGraph
Step 4 → दोनों चाहिए? LlamaIndex को LangChain app में retriever बनाओ
Step 5 → Team skills, ecosystem, observability, deployment देखो
Step 6 → 20 real सवालों पर दोनों prototype: accuracy, code size, latency
Step 7 → निर्णय; अपने interface के पीछे रखो ताकि बदलना आसान रहे
```

---

## 🟡 Real World Example
**Tariff Classification System**: ingestion of 40 PDF formats with Section/Chapter hierarchy fits LlamaIndex (`HierarchicalNodeParser`, `AutoMergingRetriever`). The classification workflow (normalise -> retrieve -> classify -> validate -> human review) fits LangGraph. Final design: LlamaIndex retriever wrapped as a LangChain tool inside a LangGraph flow. **Amazon**: catalog QA over documents (LlamaIndex style) plus order-action agent (LangChain style).

## 🟡 Real Example Hindi mein
**Tariff System**: 40 PDF formats और Section/Chapter hierarchy का ingestion LlamaIndex (`HierarchicalNodeParser`, `AutoMergingRetriever`) में fit होता है। Classification workflow (normalise -> retrieve -> classify -> validate -> review) LangGraph में। अंतिम design: LlamaIndex retriever को LangChain tool बनाकर LangGraph में।

---

## 💻 Code Example — Basic
```python
# Offline illustration of the SAME task in both styles (no packages needed).
# We mimic the shape of each API with tiny fake classes.

class FakeLlamaIndex:
    """LlamaIndex style: documents -> index -> query_engine.query()"""
    def __init__(self, docs: list[str]) -> None:
        self.docs = docs  # step 1: load documents
    def as_query_engine(self):
        docs = self.docs
        class QE:
            def query(self, q: str) -> str:
                hit = max(docs, key=lambda d: len(set(q.split()) & set(d.split())))  # naive retrieve
                return f"Answer from: {hit}"  # naive synthesise
        return QE()

def langchain_style(q: str, docs: list[str]) -> str:
    """LangChain style: explicit pipeline retrieve | prompt | llm."""
    retrieve = lambda x: max(docs, key=lambda d: len(set(x.split()) & set(d.split())))  # step 1
    prompt = lambda ctx: f"Context: {ctx}\nQ: {q}"  # step 2
    llm = lambda p: f"LLM says based on [{p.splitlines()[0]}]"  # step 3
    return llm(prompt(retrieve(q)))  # compose

docs = ["HS 8518 headphones earphones", "HS 6403 footwear leather"]
print(FakeLlamaIndex(docs).as_query_engine().query("earphones headphones code"))
print(langchain_style("earphones headphones code", docs))
```

## 💻 Code Example — Advanced
```python
# Use both: LlamaIndex as the retriever, LangChain/LangGraph as orchestrator (async)
# pip install llama-index langchain-core langchain-openai
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Build the LlamaIndex index once at startup:
documents = SimpleDirectoryReader("./tariff_docs").load_data()  # PDFs, docx, md...
index = VectorStoreIndex.from_documents(documents)  # embeds with default OpenAI embeddings
retriever = index.as_retriever(similarity_top_k=5)  # returns NodeWithScore objects

@tool
async def search_tariff(query: str) -> str:
    """Search tariff documents and return the most relevant passages."""
    try:
        nodes = await retriever.aretrieve(query)  # async retrieval
    except Exception as exc:
        return f"retrieval error: {exc}"  # tools should return errors as text
    return "\n---\n".join(n.node.get_content()[:800] for n in nodes)  # cap tokens

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([search_tariff])  # LangChain side
# A LangGraph ReAct agent (langgraph.prebuilt.create_react_agent) can now call search_tariff.
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from langgraph.prebuilt import create_react_agent

app = FastAPI()
agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), tools=[search_tariff])  # uses LlamaIndex tool

@app.post("/ask")
async def ask(q: dict) -> dict:
    out = await agent.ainvoke({"messages": [("user", q["question"])]})  # run agent
    return {"answer": out["messages"][-1].content}  # last message is the answer
```

---

## 🔗 LangChain / LangGraph Connection
Integration options: (1) wrap a LlamaIndex retriever/query engine as a LangChain `@tool` (shown above), (2) LlamaIndex has LangChain interop utilities, (3) in LangGraph, treat the LlamaIndex query as a node. Observability: both support OpenTelemetry-style tracing; LangSmith natively traces LangChain/LangGraph.

```python
# LangGraph node calling LlamaIndex:
# async def retrieve_node(state): return {"docs": [n.node.get_content() for n in await retriever.aretrieve(state["q"])]}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Choosing by hype
```python
# Wrong: "everyone uses X"  -> no benchmark
# Right: run 20 real questions through both, compare accuracy, tokens, lines of code
```

❌ Mistake 2: Hard-wiring the framework everywhere
```python
# Wrong: framework objects imported across the codebase
# Right: define class Retriever(Protocol): async def search(q: str) -> list[str]; adapt each framework to it
```

---

## 🧠 Tricky Interview Question
**Q**: "Your LlamaIndex RAG is accurate but the product now needs multi-step tool use and human approval. Rewrite everything in LangChain?"

**Answer**: No. Keep the retrieval layer (it works) and add orchestration with LangGraph around it: expose retrieval as a tool/node, add state, conditional edges and an interrupt for approval. Rewrites risk regressions; a thin adapter keeps both strengths.

---

## ⚫ Interview Questions + Answers

Q1: One-line difference? (Easy)
A1: LangChain = general LLM app/agent toolkit; LlamaIndex = data and retrieval focused framework.

Q2: Which is better for RAG? (Easy)
A2: Both work; LlamaIndex has richer built-in indexing/retrieval abstractions, LangChain is more flexible for pipelines around RAG.

Q3: What are LlamaIndex's core abstractions? (Medium)
A3: Documents, Nodes (chunks), Index, Retriever, Response synthesizer, QueryEngine, plus Workflows for event-driven flows.

Q4: What are LangChain's core abstractions? (Medium)
A4: Runnable interface with LCEL, prompts, chat models, output parsers, retrievers, tools, and LangGraph for stateful agents.

Q5: How do you avoid vendor lock-in with either? (Hard)
A5: Put an interface (Protocol) around retrieval and generation, keep prompts and eval datasets framework-independent, store vectors in a standard DB, and write tests against the interface not the framework.

---

## 🔷 When to Use + When Not to Use
✅ LlamaIndex when:
- Complex ingestion, many data connectors, advanced indexes
✅ LangChain/LangGraph when:
- Agents, tools, branching, human-in-the-loop, many providers

❌ Avoid either when:
- A 30-line script with the provider SDK is enough

---

## 📊 Visual Diagram
```
            ┌──────────── LlamaIndex ────────────┐
 Data ─►    │ Loaders ► Nodes ► Index ► Retriever│ ─┐
            └────────────────────────────────────┘  │ as tool
            ┌──────────── LangChain/LangGraph ───┐  ▼
 User ─►    │ Prompt ► LLM ► Tools ► State graph │ ◄┘ ─► Answer
            └────────────────────────────────────┘
```

---

## 💰 Cost Impact
Neither framework charges, but defaults differ: LlamaIndex response synthesizers may make several LLM calls (refine/tree summarize modes) and use default OpenAI embeddings; LangChain agents may loop tool calls. Check traces for number of LLM calls per query, set `similarity_top_k` low, choose "compact" synthesis, cap agent iterations, and cache embeddings.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| LlamaIndex | Data/RAG framework | Data/RAG framework |
| Node | A chunk in LlamaIndex | LlamaIndex में chunk |
| QueryEngine | Index + synthesis | Query चलाने वाला engine |
| LangGraph | Stateful agent graphs | State वाले agent graphs |
| Adapter | Wrapper to hide framework | Framework छिपाने वाला wrapper |

---

## ⚡ 3-Line Summary
English: LangChain is broad for agents and workflows; LlamaIndex is deep for data and retrieval. They combine well: LlamaIndex retriever as a LangChain tool in LangGraph. Decide by prototype on real questions and hide frameworks behind interfaces.
Hindi: LangChain agents और workflows के लिए broad है; LlamaIndex data और retrieval के लिए deep। दोनों मिलते हैं: LlamaIndex retriever को LangGraph में tool बनाओ। Real सवालों पर prototype से तय करो और interface के पीछे रखो।

---

## ➡️ Next Topic
**233. LangChain Architecture** — the package layout and layers that make the framework work.
