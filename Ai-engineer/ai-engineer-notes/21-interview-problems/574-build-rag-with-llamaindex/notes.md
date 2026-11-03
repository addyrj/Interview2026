---

# 574. Build RAG with LlamaIndex
# हिंदी में: LlamaIndex के साथ RAG बनाना

---

## 🔵 Simple Definition (English)
LlamaIndex is a framework focused on connecting LLMs to your data. You wrap text in `Document`s, build a `VectorStoreIndex` (it chunks, embeds and stores for you), and call `index.as_query_engine()` to get a ready RAG engine that retrieves and answers.

## 🔵 सरल परिभाषा (Hindi)
LlamaIndex एक framework है जो LLMs को आपके data से जोड़ने पर केंद्रित है। आप text को `Document` में रखते हैं, `VectorStoreIndex` बनाते हैं (यह chunk, embed और store खुद करता है) और `index.as_query_engine()` से retrieve और answer करने वाला RAG engine पाते हैं।

---

## 🔴 Problem it Solves
Ingesting many file types (PDF, HTML, DB rows), chunking them well, indexing and querying takes lots of glue code. LlamaIndex provides data connectors, node parsers, indexes, retrievers and response synthesizers in a few lines. Interviewers ask for it to see whether you can compare frameworks (LangChain vs LlamaIndex) sensibly.

## 🔴 यह क्यों बना? (Hindi)
कई file types (PDF, HTML, DB rows) ingest करना, ठीक से chunk करना, index और query करना बहुत glue code माँगता है। LlamaIndex data connectors, node parsers, indexes, retrievers और response synthesizers कुछ lines में देता है। Interviewer framework तुलना (LangChain vs LlamaIndex) समझने के लिए पूछते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Load data into Document objects (readers like SimpleDirectoryReader)
Step 2 → Node parser (SentenceSplitter) splits Documents into Nodes (chunks + metadata)
Step 3 → Embedding model converts nodes to vectors
Step 4 → VectorStoreIndex stores them (in-memory by default, or Qdrant etc.)
Step 5 → Query engine: retriever fetches top-k nodes
Step 6 → Response synthesizer builds the prompt and calls the LLM
Step 7 → Response object holds the answer + source_nodes (citations)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Data को Document objects में लोड करो (SimpleDirectoryReader जैसे readers)
Step 2 → Node parser (SentenceSplitter) Documents को Nodes (chunks + metadata) में बाँटता है
Step 3 → Embedding model nodes को vectors बनाता है
Step 4 → VectorStoreIndex उन्हें store करता है (default in-memory, या Qdrant आदि)
Step 5 → Query engine: retriever top-k nodes लाता है
Step 6 → Response synthesizer prompt बनाकर LLM call करता है
Step 7 → Response में answer + source_nodes (citations) होते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: A folder of customs circular PDFs is read with `SimpleDirectoryReader`, indexed once, and persisted to disk (`index.storage_context.persist()`). Officers query it; the answer comes with `source_nodes` showing file name and page, which is what auditors want.

**Amazon-style**: Seller-policy assistant over hundreds of policy PDFs.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs circular PDFs का folder `SimpleDirectoryReader` से पढ़ा जाता है, एक बार index होकर disk पर persist होता है। Officers query करते हैं; जवाब के साथ `source_nodes` (file name और page) मिलते हैं, जो auditors को चाहिए।

---

## 💻 Code Example — Basic
Full file: `main.py` (needs `pip install llama-index-core`; it is not installed in this environment, so I only syntax-checked it and did not run it). Without `OPENAI_API_KEY` it uses `MockEmbedding` and `MockLLM`, which prove the wiring but return placeholder text and meaningless similarity.

```python
# Core RAG in LlamaIndex (from main.py)
Settings.llm = MockLLM()                             # global LLM (swap for OpenAI)
Settings.embed_model = MockEmbedding(embed_dim=64)   # global embeddings (swap for real)
docs = [Document(text=t, metadata={"id": i}) for i, t in RAW_DOCS]   # raw data
index = VectorStoreIndex.from_documents(docs)        # chunk + embed + index in one call
engine = index.as_query_engine(similarity_top_k=2)   # retriever + synthesizer
print(engine.query("What is the duty on smartphones?"))   # answer
```

## 💻 Code Example — Advanced
`main.py` also includes model selection by environment, `SentenceSplitter` configuration, an async `aquery` demo and a FastAPI `/ask` route returning the answer and source ids. Production additions: a persistent vector store (Qdrant), `index.storage_context.persist()`, metadata filters, a node postprocessor/reranker, and `response_mode` choice (`compact`, `refine`, `tree_summarize`).

```python
# Excerpt: async route with sources (main.py)
@app.post("/ask")
async def ask(q: Q) -> dict[str, object]:
    try:
        resp = await engine.aquery(q.question)                 # async query
    except Exception as exc:                                   # provider/retrieval errors
        raise HTTPException(status_code=502, detail=type(exc).__name__) from exc
    sources = [n.node.metadata.get("id") for n in resp.source_nodes]   # citations
    return {"answer": str(resp), "sources": sources}
```

---

## 🟠 FastAPI Integration
```python
# Build the engine once at startup; reuse across requests
engine = build_query_engine()      # loads/creates index

@app.post("/ask")
async def ask(q: Q) -> dict[str, object]:
    resp = await engine.aquery(q.question)               # non-blocking
    return {"answer": str(resp), "sources": [n.node.metadata.get("id") for n in resp.source_nodes]}
```
Persist the index to disk or a vector DB so restarts do not re-embed everything.

---

## 🔗 LangChain / LangGraph Connection
LlamaIndex and LangChain interoperate: a LlamaIndex query engine can be wrapped as a LangChain tool, and LangGraph can call it inside a node. Rule of thumb: LlamaIndex shines for data ingestion and indexing variety; LangChain/LangGraph for orchestration and agents. Verify current wrapper class names in the docs.

```python
# Use the engine as a tool inside a LangGraph/LangChain agent (illustrative)
from typing import Callable

def tariff_tool(question: str) -> str:
    """Tool wrapper: agents call this to search tariff docs."""
    return str(engine.query(question))      # engine from build_query_engine()
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Relying on hidden global defaults
✅ Correct: Set `Settings.llm` and `Settings.embed_model` explicitly (default may require an OpenAI key and silently choose a model).
```python
# Wrong
index = VectorStoreIndex.from_documents(docs)    # which embedding model? whatever default
# Right
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
index = VectorStoreIndex.from_documents(docs)
```

❌ Mistake 2: Not persisting the index
✅ Correct: Persist or use a vector DB.
```python
# Wrong: rebuild index at every process start (re-pay embedding tokens)
# Right: index.storage_context.persist("./storage")  then load_index_from_storage(...)
```

---

## 🧠 Tricky Interview Question
**Q**: "`response_mode='refine'` gave better answers than `compact` but your bill tripled. Why?"

**Answer**: `compact` stuffs as many chunks as fit into one LLM call. `refine` calls the LLM once per chunk, feeding the previous answer forward, so N chunks means N calls and growing prompts. That improves use of all chunks but multiplies calls, latency and tokens. Use `compact` by default, `tree_summarize` for summaries, and use `refine` only when accuracy needs it; reduce `similarity_top_k` or rerank first.

---

## ⚫ Interview Questions + Answers

Q1: What is a Node in LlamaIndex?
A1: A chunk of a Document with metadata and relationships; the unit that is embedded and retrieved.

Q2: What does `VectorStoreIndex.from_documents` do?
A2: Parses documents into nodes, embeds them, and stores the vectors in a vector store.

Q3: What is `Settings`?
A3: Global configuration for LLM, embedding model, node parser and similar defaults.

Q4: LlamaIndex vs LangChain?
A4: LlamaIndex: data ingestion/indexing/query focus with strong connectors. LangChain: general orchestration (chains, agents, tools). They are often combined.

Q5: How do you improve retrieval quality in LlamaIndex?
A5: Better chunking (sentence/semantic), metadata filters, hybrid retrieval, a reranker postprocessor, query transformation (rewrite, HyDE), and an eval set measuring hit rate and MRR.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many data sources and formats to ingest
- Fast RAG with built-in citations

❌ Avoid when:
- You need complex multi-step agent control as the main feature (use LangGraph)
- You want minimal dependencies

---

## 📊 Visual Diagram
```
 files/DB ─► Reader ─► Documents ─► SentenceSplitter ─► Nodes
                                                          │ embed
                                                          ▼
 question ─► QueryEngine ─► Retriever ─► top-k Nodes ◄─ VectorStoreIndex
                  │
                  └─► ResponseSynthesizer ─► LLM ─► Response(answer, source_nodes)
```

---

## 💰 Cost Impact
Indexing cost = chunk tokens x embedding price (one time per change). Query cost depends on `response_mode` and `similarity_top_k`: `compact` ~ one LLM call; `refine` ~ k calls. Example: k=4, 256-token chunks gives ~1,100 input tokens in compact mode. Optimise: persist the index, use `compact`, lower k with reranking, cache answers, cap output tokens.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Document | Source data unit | Source data की इकाई |
| Node | Chunk with metadata | Metadata वाला chunk |
| Index | Searchable structure | Search योग्य संरचना |
| Query engine | Retrieve + answer | खोजकर जवाब देने वाला |
| Synthesizer | Builds final answer | अंतिम जवाब बनाने वाला |
| Persist | Save index to disk | Index को disk पर सेव करना |

---

## ⚡ 3-Line Summary
English: LlamaIndex turns Documents into Nodes, embeds and indexes them, and offers a query engine that retrieves and answers with sources. Set models explicitly and persist the index. Pick response modes carefully because they change cost.
Hindi: LlamaIndex Documents को Nodes में बदलकर embed और index करता है और sources के साथ जवाब देने वाला query engine देता है। Models साफ़ सेट करें और index persist करें। Response mode सोचकर चुनें क्योंकि cost बदलती है।

---

## ➡️ Next Topic
**575. Build Streaming Chat API** — stream tokens to the user with Server-Sent Events.
