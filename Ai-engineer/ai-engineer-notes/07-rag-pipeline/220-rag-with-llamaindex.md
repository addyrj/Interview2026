---

# 220. RAG with LlamaIndex
# हिंदी में: RAG with LlamaIndex

---

## 🔵 Simple Definition (English)
LlamaIndex is a framework focused on data and indexing for LLM apps. In a few lines you load documents, build an index, and get a query engine that retrieves relevant nodes (chunks) and asks the LLM to answer with sources.

## 🔵 सरल परिभाषा (Hindi)
LlamaIndex LLM apps के लिए data और indexing पर केंद्रित framework है। कुछ lines में documents load करके index बनाते हैं और एक query engine मिलता है जो relevant nodes (chunks) लाकर LLM से sources के साथ answer बनवाता है।

---

## 🔴 Problem it Solves
Getting from "a folder of PDFs" to a working Q&A needs parsing, chunking, embedding, storage, retrieval and synthesis. LlamaIndex packages these into high-level abstractions (Document, Node, Index, Retriever, QueryEngine) with sensible defaults, plus many data connectors (LlamaHub) and advanced retrieval modules.

## 🔴 यह क्यों बना? (Hindi)
"PDFs का folder" से working Q&A तक जाने में parsing, chunking, embedding, storage, retrieval और synthesis चाहिए। LlamaIndex इन्हें high-level abstractions (Document, Node, Index, Retriever, QueryEngine) में पैक करता है, अच्छे defaults, कई data connectors (LlamaHub) और advanced retrieval modules के साथ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Settings: set the LLM and embedding model (Settings.llm, Settings.embed_model)
Step 2 → SimpleDirectoryReader loads files into Document objects
Step 3 → NodeParser (SentenceSplitter) cuts documents into Nodes (chunks + metadata)
Step 4 → VectorStoreIndex embeds nodes and stores them (in memory or a vector DB)
Step 5 → index.as_retriever(similarity_top_k=4) -> NodeWithScore list
Step 6 → Response synthesizer builds the prompt and calls the LLM
Step 7 → query_engine.query(q) -> Response with .response and .source_nodes
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Settings: LLM और embedding model set करो (Settings.llm, Settings.embed_model)
Step 2 → SimpleDirectoryReader files को Document objects में load करता है
Step 3 → NodeParser (SentenceSplitter) documents को Nodes (chunks + metadata) में काटता है
Step 4 → VectorStoreIndex nodes को embed करके store करता है (memory या vector DB में)
Step 5 → index.as_retriever(similarity_top_k=4) -> NodeWithScore की list
Step 6 → Response synthesizer prompt बनाकर LLM को call करता है
Step 7 → query_engine.query(q) -> Response (.response और .source_nodes) लौटाता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: Drop all tariff PDFs and circulars into `data/`. LlamaIndex parses them, keeps `file_name` and `page_label` metadata, and the query engine answers "duty on refurbished phones" with `source_nodes` showing page numbers. A `MetadataFilters` restricts to `country=IN`. **Zomato**: index of policy docs. **Amazon**: product manuals index with a sub-question query engine for comparisons.

## 🟡 Real Example Hindi mein
**Tariff System**: सारे tariff PDFs और circulars `data/` में डालो। LlamaIndex उन्हें parse करता है, `file_name` और `page_label` metadata रखता है, और query engine "refurbished phones पर duty" का answer देता है, `source_nodes` में page numbers के साथ। `MetadataFilters` से `country=IN` तक सीमित करो। **Zomato**: policy docs का index। **Amazon**: product manuals का index, तुलना के लिए sub-question query engine।

---

## 💻 Code Example — Basic
```python
# Basic LlamaIndex RAG, offline: MockLLM + MockEmbedding so no API key is needed.
# pip install llama-index-core
from llama_index.core import Document, Settings, VectorStoreIndex  # core classes
from llama_index.core.embeddings import MockEmbedding  # fake embeddings
from llama_index.core.llms import MockLLM  # fake LLM

Settings.llm = MockLLM(max_tokens=50)  # replace with OpenAI(model="gpt-4o-mini")
Settings.embed_model = MockEmbedding(embed_dim=64)  # replace with OpenAIEmbedding(...)
Settings.chunk_size = 256  # chunk size in tokens
Settings.chunk_overlap = 20  # overlap

docs = [  # in-memory documents
    Document(text="Smartphones HS 8517.13 duty 20 percent.", metadata={"file_name": "tariff.pdf", "page_label": "412"}),
    Document(text="Laptops HS 8471.30 duty 0 percent.", metadata={"file_name": "tariff.pdf", "page_label": "380"}),
]

index = VectorStoreIndex.from_documents(docs)  # embed + store
query_engine = index.as_query_engine(similarity_top_k=1)  # retriever + synthesizer

if __name__ == "__main__":
    response = query_engine.query("What is the duty on smartphones?")  # run
    print("Answer:", response.response[:80])  # MockLLM output (not meaningful)
    for n in response.source_nodes:  # sources used
        print("Source:", n.node.metadata, "score:", n.score)  # metadata + score
```

## 💻 Code Example — Advanced
```python
# Production: persistent index, metadata filters, async query, custom prompt, error handling.
import logging  # logs
from pathlib import Path  # paths

from llama_index.core import (  # core API
    PromptTemplate, Settings, StorageContext, VectorStoreIndex, load_index_from_storage,
)
from llama_index.core.vector_stores import FilterOperator, MetadataFilter, MetadataFilters  # filters
from llama_index.embeddings.openai import OpenAIEmbedding  # pip install llama-index-embeddings-openai
from llama_index.llms.openai import OpenAI  # pip install llama-index-llms-openai

logger = logging.getLogger("li_rag")  # logger
Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0, max_tokens=400)  # generation model
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")  # embedding model

QA_PROMPT = PromptTemplate(  # grounded prompt
    "Context:\n{context_str}\n\n"
    "Answer ONLY from the context. Cite file and page. If missing say NOT_FOUND.\n"
    "Question: {query_str}\nAnswer: "
)


def load_or_build(persist_dir: str = "storage", data_dir: str = "data") -> VectorStoreIndex:
    """Load a saved index, else build from files and save it."""
    if Path(persist_dir).exists():  # already indexed
        return load_index_from_storage(StorageContext.from_defaults(persist_dir=persist_dir))  # load
    from llama_index.core import SimpleDirectoryReader  # delayed import
    docs = SimpleDirectoryReader(data_dir).load_data()  # parse files
    index = VectorStoreIndex.from_documents(docs)  # build
    index.storage_context.persist(persist_dir=persist_dir)  # save to disk
    return index


async def ask(index: VectorStoreIndex, question: str, file_name: str | None = None) -> dict:
    """Async query with an optional metadata filter."""
    filters = MetadataFilters(filters=[MetadataFilter(key="file_name", value=file_name, operator=FilterOperator.EQ)]) if file_name else None
    engine = index.as_query_engine(similarity_top_k=4, filters=filters, text_qa_template=QA_PROMPT)  # engine
    try:  # network errors
        resp = await engine.aquery(question)  # async query
        return {"answer": str(resp), "sources": [n.node.metadata for n in resp.source_nodes]}  # result
    except Exception as exc:  # any failure
        logger.exception("query failed: %s", exc)  # log
        return {"answer": "Service temporarily unavailable", "sources": []}  # safe fallback
```

---

## 🟠 FastAPI Integration
Build or load the index at startup (never per request) and call `aquery`.

```python
from contextlib import asynccontextmanager  # lifespan
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.index = load_or_build()  # one-time load
    yield


app = FastAPI(lifespan=lifespan)  # app


class Q(BaseModel):
    question: str  # question
    file_name: str | None = None  # optional filter


@app.post("/ask")  # route
async def ask_route(q: Q) -> dict:
    return await ask(app.state.index, q.question, q.file_name)  # shared index
```

---

## 🔗 LangChain / LangGraph Connection
LlamaIndex and LangChain can be combined: use a LlamaIndex retriever as a node inside a LangGraph workflow, or wrap a LlamaIndex query engine as a LangChain tool. LlamaIndex also has its own `Workflow` and `AgentWorkflow` for event-driven pipelines.

```python
from langchain_core.tools import tool  # tool decorator


# @tool
# def tariff_search(question: str) -> str:
#     """Search the tariff index and answer from it."""
#     return str(query_engine.query(question))     # sync call inside a LangChain tool
#
# LangGraph agent: tools=[tariff_search]  (the agent decides when to call the index)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Rebuilding the index every start
✅ Correct: Persist and reload (or use an external vector DB).

```python
# Wrong: re-embeds all PDFs each deploy, costs money
index = VectorStoreIndex.from_documents(SimpleDirectoryReader("data").load_data())

# Right: persist once, load afterwards
index = load_index_from_storage(StorageContext.from_defaults(persist_dir="storage"))
```

❌ Mistake 2: Leaving defaults unchecked (hidden OpenAI use)
✅ Correct: Set `Settings.llm` and `Settings.embed_model` explicitly.

```python
# Wrong: default OpenAI models used silently, and fails without OPENAI_API_KEY
index = VectorStoreIndex.from_documents(docs)

# Right: choose models deliberately
Settings.llm = OpenAI(model="gpt-4o-mini"); Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
```

---

## 🧠 Tricky Interview Question
**Q**: "Same documents, same question: LangChain RAG and LlamaIndex RAG give different answers. Which is 'right' and why do they differ?"

**Answer**: Neither is wrong by default; defaults differ. Chunk size and overlap, splitter type (sentence-based vs recursive characters), top-k, embedding model, prompt wording, response mode (`compact`, `refine`, `tree_summarize`) all change the context the LLM sees. Align these settings, then compare using a labelled evaluation set (retrieval recall, faithfulness, answer correctness) instead of eyeballing single answers.

---

## ⚫ Interview Questions + Answers

Q1: What are Document and Node in LlamaIndex?
A1: A Document is a whole source (like a PDF). A Node is a chunk of it with metadata and relationships; indexes work on Nodes.

Q2: What is a query engine?
A2: A retriever plus a response synthesizer packaged behind `.query()` / `.aquery()`.

Q3: What are response modes?
A3: How retrieved chunks are fed to the LLM: `compact` (stuff as much as fits), `refine` (iterate chunk by chunk), `tree_summarize` (hierarchical), `simple_summarize`, etc.

Q4: How do you use an external vector DB?
A4: Create a vector store integration (Chroma, Qdrant, pgvector ...), wrap it in `StorageContext.from_defaults(vector_store=...)`, and build `VectorStoreIndex.from_documents(..., storage_context=...)`.

Q5: When choose LlamaIndex over LangChain?
A5: When the problem is data-heavy: many document types, complex parsing (LlamaParse), hierarchical or structured retrieval, sub-question engines, and index management. LangChain/LangGraph shine for general orchestration and agents. Many teams combine them. Evaluate on your data rather than choosing by popularity.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Document-heavy RAG with many formats
- You want fast start with strong defaults
- You need advanced retrieval modules (auto-merging, sub-question, routers)

❌ Avoid when:
- You already have a stable LangChain stack and simple needs
- You need minimal dependencies
- You want complete control of the prompt flow (raw SDK may be easier)

---

## 📊 Visual Diagram
```
 files ─► SimpleDirectoryReader ─► Documents ─► SentenceSplitter ─► Nodes
                                                                     │ embed
                                                                     ▼
                                                             VectorStoreIndex
 query ─► Retriever (top_k) ─► NodesWithScore ─► ResponseSynthesizer ─► LLM
                                                                     │
                                                       Response + source_nodes
```

---

## 💰 Cost Impact
- Indexing cost: embedding tokens for all documents (one time). E.g. 1M tokens with text-embedding-3-small is about $0.02 (check current pricing).
- Query cost: `compact` mode makes about 1 LLM call; `refine` makes one call per chunk (k calls, more tokens and latency).
- Optimise: pick `compact`, small top-k, persist indexes, use cheaper embeddings, cache, check `response.source_nodes` sizes, and use token counting handler (`TokenCountingHandler`) to monitor usage.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Document | Whole source file/text | पूरा source |
| Node | Chunk with metadata | Metadata वाला chunk |
| Index | Structure for retrieval | Retrieval के लिए structure |
| Query engine | Retrieve + answer | Retrieve और answer |
| Response mode | How context is fed to LLM | LLM को context देने का तरीका |

---

## ⚡ 3-Line Summary
English: LlamaIndex turns documents into Nodes, indexes them, and gives a query engine that returns answers with source nodes. Persist indexes, set models explicitly, and pick the response mode wisely. Use it when data handling is the hard part.
Hindi: LlamaIndex documents को Nodes में बदलता है, index करता है और source nodes के साथ answer देने वाला query engine देता है। Index persist करो, models साफ़ set करो और response mode सोच-समझकर चुनो। जब data handling मुश्किल हो तब इसे use करो।

---

## ➡️ Next Topic
**221. Conversational RAG** — handling follow-up questions such as "and for laptops?" by rewriting them using chat history.
