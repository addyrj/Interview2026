---

# 389. LlamaIndex Basics
# हिंदी में: LlamaIndex Basics (अपने डेटा पर RAG बनाने की library)

---

## 🔵 Simple Definition (English)
LlamaIndex is a Python framework for building RAG (Retrieval-Augmented Generation) apps. It loads your documents, splits them into chunks (nodes), embeds them into a vector index, and at question time retrieves the best chunks and passes them to an LLM to answer. Install: `pip install llama-index-core` (plus provider packages such as `llama-index-llms-openai`).

## 🔵 सरल परिभाषा (Hindi)
LlamaIndex RAG apps बनाने का Python framework है। यह आपके documents load करता है, उन्हें chunks (nodes) में बाँटता है, vector index में embed करता है और सवाल आने पर सबसे मिलते-जुलते chunks निकालकर LLM को देता है ताकि वह जवाब बनाए।

---

## 🔴 Problem it Solves
An LLM does not know your private data (company PDFs, FAQs) and has a limited context window. You cannot paste 10,000 pages in a prompt. LlamaIndex gives ready-made pieces: readers, node parsers, indexes, retrievers, query engines, and storage, so you do not write the chunk-embed-search-prompt pipeline from scratch.

## 🔴 यह क्यों बना? (Hindi)
LLM आपका private data (company PDFs, FAQs) नहीं जानता और उसकी context window सीमित है। 10,000 pages prompt में नहीं डाल सकते। LlamaIndex readers, node parsers, indexes, retrievers, query engines और storage तैयार देता है, ताकि chunk-embed-search-prompt pipeline खुद न लिखनी पड़े।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Load: SimpleDirectoryReader / Document(text=...)         -> Document objects
Step 2 → Split: SentenceSplitter(chunk_size=512)                   -> Node chunks
Step 3 → Embed: embed_model turns each node into a vector
Step 4 → Index: VectorStoreIndex stores vectors (in memory by default)
Step 5 → Retrieve: query -> embed -> top-k similar nodes
Step 6 → Synthesize: LLM gets question + retrieved nodes -> answer (+ source_nodes)
Step 7 → Persist: index.storage_context.persist(dir) to avoid re-embedding
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Load: documents पढ़ना (SimpleDirectoryReader या Document)
Step 2 → Split: SentenceSplitter से chunks (nodes) बनाना
Step 3 → Embed: embed model हर node को vector में बदलता है
Step 4 → Index: VectorStoreIndex vectors को memory में रखता है
Step 5 → Retrieve: सवाल को embed करके top-k मिलते-जुलते nodes लाना
Step 6 → Synthesize: LLM को सवाल + nodes देकर जवाब बनवाना
Step 7 → Persist: दोबारा embed न करना पड़े इसलिए index disk पर सेव करना
```

---

## 🟡 Real World Example
A Razorpay-style support bot answers "How long do UPI refunds take?" from the company's help-center docs. Documents are ingested once into an index; each user question retrieves the 3 most relevant chunks and the LLM writes the answer with citations from `source_nodes`.

## 🟡 Real Example Hindi mein
Razorpay जैसा support bot "UPI refund कितने दिन में आता है?" का जवाब help-center docs से देता है। Documents एक बार index में डाले जाते हैं; हर सवाल पर 3 सबसे relevant chunks मिलते हैं और LLM `source_nodes` के हवाले के साथ जवाब लिखता है।

---

## 💻 Code Example — Basic
```python
# VERIFIED with llama-index-core 0.14.25 using MockEmbedding/MockLLM (offline, no API key).
# Install: pip install llama-index-core
# With real models you would set OpenAI (or other) embeddings/LLM instead of the mocks.
from llama_index.core import Document, Settings, VectorStoreIndex  # core classes
from llama_index.core.embeddings import MockEmbedding  # fake embeddings for tests
from llama_index.core.llms import MockLLM  # fake LLM for tests
from llama_index.core.node_parser import SentenceSplitter  # chunking

Settings.embed_model = MockEmbedding(embed_dim=8)  # global default embedder (8 numbers per text)
Settings.llm = MockLLM(max_tokens=30)  # global default LLM (echoes placeholder text)

docs = [  # two small in-memory documents with metadata
    Document(text="Refunds are processed within 5 business days. Contact support for UPI refunds.",
             metadata={"source": "faq.md"}),
    Document(text="Delivery is free above Rs 499. Express delivery takes 30 minutes.",
             metadata={"source": "delivery.md"}),
]

splitter = SentenceSplitter(chunk_size=64, chunk_overlap=0)  # chunks of up to 64 tokens
nodes = splitter.get_nodes_from_documents(docs)  # Documents -> Nodes
print(len(nodes), nodes[0].metadata)  # Output: 2 {'source': 'faq.md'}

index = VectorStoreIndex.from_documents(docs, transformations=[splitter])  # embed + store
retriever = index.as_retriever(similarity_top_k=1)  # get only the best chunk
hits = retriever.retrieve("refund")  # list of NodeWithScore
print(len(hits), type(hits[0]).__name__, hits[0].node.metadata)
# Output: 1 NodeWithScore {'source': 'faq.md'}
# NOTE: with MockEmbedding the "best" hit is NOT semantic (vectors are fake/random);
# with a real embedding model the refund document would rank first.

engine = index.as_query_engine(similarity_top_k=2)  # retriever + LLM synthesizer
response = engine.query("How long do refunds take?")  # runs the full RAG chain
print(type(response).__name__, len(response.source_nodes))  # Output: Response 2
print(str(response)[:20])  # Output: text text text text   (MockLLM filler, a real LLM gives an answer)
```

## 💻 Code Example — Advanced
```python
# VERIFIED (persist/reload and structure) with llama-index-core 0.14.25 + mocks.
# Production style: build once, persist, reload, return answer + citations, handle errors.
from pathlib import Path  # filesystem paths
from typing import Dict, List, Optional  # type hints

from llama_index.core import (  # core API
    Document, Settings, StorageContext, VectorStoreIndex, load_index_from_storage,
)
from llama_index.core.embeddings import MockEmbedding  # replace with OpenAIEmbedding in production
from llama_index.core.llms import MockLLM  # replace with OpenAI / Anthropic LLM in production
from llama_index.core.node_parser import SentenceSplitter  # chunker

Settings.embed_model = MockEmbedding(embed_dim=8)  # fake embedder for the demo
Settings.llm = MockLLM(max_tokens=30)  # fake LLM for the demo
PERSIST_DIR: Path = Path("store")  # where the index is saved


def build_or_load_index(docs: List[Document]) -> VectorStoreIndex:
    """Reuse the saved index if present so we do not pay for embeddings again."""
    if PERSIST_DIR.exists():  # already built earlier
        storage = StorageContext.from_defaults(persist_dir=str(PERSIST_DIR))  # read files
        return load_index_from_storage(storage)  # type: ignore[return-value]
    index = VectorStoreIndex.from_documents(  # first run: embed everything
        docs, transformations=[SentenceSplitter(chunk_size=256, chunk_overlap=20)]
    )
    index.storage_context.persist(persist_dir=str(PERSIST_DIR))  # save docstore + vectors
    return index


def answer(index: VectorStoreIndex, question: str, top_k: int = 3) -> Dict[str, object]:
    """Return the answer plus the sources used."""
    if not question.strip():  # validate input
        raise ValueError("question must not be empty")
    engine = index.as_query_engine(similarity_top_k=top_k)  # build the engine
    result = engine.query(question)  # run retrieval + generation
    sources: List[Optional[str]] = [
        n.node.metadata.get("source") for n in result.source_nodes  # citations
    ]
    return {"answer": str(result), "sources": sources}  # JSON-friendly


documents = [Document(text="Refunds take 5 business days.", metadata={"source": "faq.md"}),
             Document(text="Delivery is free above Rs 499.", metadata={"source": "delivery.md"})]
idx = build_or_load_index(documents)  # builds and saves
idx2 = build_or_load_index(documents)  # loads from disk this time
print(len(idx2.docstore.docs))  # Output: 2   (nodes stored on disk)
out = answer(idx2, "refund time?", top_k=2)  # ask a question
print(sorted(s for s in out["sources"] if s))  # Output: ['delivery.md', 'faq.md']
```

---

## 🟠 JavaScript vs Python Comparison
LlamaIndex also exists for JavaScript/TypeScript (`llamaindex` on npm) and the concepts are the same.

```python
# Python
from llama_index.core import VectorStoreIndex, Document
index = VectorStoreIndex.from_documents([Document(text="hello")])
answer = index.as_query_engine().query("what is hello?")
```
```javascript
// JavaScript / TypeScript (llamaindex)
import { Document, VectorStoreIndex } from "llamaindex";
const index = await VectorStoreIndex.fromDocuments([new Document({ text: "hello" })]);
const response = await index.asQueryEngine().query({ query: "what is hello?" });
```

Key differences: the Python library is far larger (many readers, vector store integrations) and usually gets features first. In Python each provider is a separate package (`llama-index-llms-openai`), whereas in JS providers live in a few packages. Python calls can be blocking (`query`) or async (`aquery`).

---

## 🟠 FastAPI Connection
Build the index once at startup, keep it in `app.state`, and expose an async `/ask` endpoint using `aquery`.

```python
# FastAPI + LlamaIndex (structure checked; uses mocks so it runs without API keys)
from contextlib import asynccontextmanager  # lifespan
from typing import AsyncIterator, Dict, List
from fastapi import FastAPI  # web framework
from pydantic import BaseModel, Field  # request validation
from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.embeddings import MockEmbedding
from llama_index.core.llms import MockLLM

Settings.embed_model = MockEmbedding(embed_dim=8)  # swap for a real model in production
Settings.llm = MockLLM(max_tokens=20)


class Ask(BaseModel):  # request body
    question: str = Field(min_length=3, max_length=500)  # basic validation


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    docs = [Document(text="Refunds take 5 business days.", metadata={"source": "faq.md"})]
    app.state.engine = VectorStoreIndex.from_documents(docs).as_query_engine()  # built once
    yield  # app runs


app = FastAPI(lifespan=lifespan)  # register


@app.post("/ask")
async def ask(body: Ask) -> Dict[str, object]:
    resp = await app.state.engine.aquery(body.question)  # async query, does not block the loop
    sources: List[str] = [n.node.metadata["source"] for n in resp.source_nodes]
    return {"answer": str(resp), "sources": sources}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Re-embedding every time the app starts
```python
# Wrong: pays for embeddings on each restart
index = VectorStoreIndex.from_documents(docs)

# Right: persist once, then load_index_from_storage(...)
index.storage_context.persist("store")
```

❌ Mistake 2: Forgetting to configure an LLM / embedding model
```python
# Wrong: the default is OpenAI, so without OPENAI_API_KEY you get an error
index = VectorStoreIndex.from_documents(docs)

# Right: set Settings.llm and Settings.embed_model explicitly (OpenAI, Anthropic, local HuggingFace, Mock for tests)
```

❌ Mistake 3: Mixing different embedding models in one index
```python
# Wrong: index built with model A, queried with model B -> meaningless similarity
# Right: store the embedding model name with the index and always use the same one
```

❌ Mistake 4: Importing old paths
```python
# Wrong (pre-0.10 style): from llama_index import VectorStoreIndex
# Right: from llama_index.core import VectorStoreIndex
```

---

## 🧠 Tricky Interview Question

**Q**: A RAG bot answers "I don't know" although the answer exists in your PDF. Name likely causes.

**Answer**: (1) Chunks too small or too large, so the answer sentence is split from its context; tune `chunk_size` and `chunk_overlap`. (2) `similarity_top_k` is too low, so the right chunk is not retrieved. (3) Different embedding models used at index time and query time. (4) PDF text extraction failed (scanned images, tables). (5) The prompt told the LLM to answer only from context and the retrieved context was wrong. Debug by printing `response.source_nodes` and their scores first; retrieval problems are far more common than LLM problems.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a Document and a Node?
A1: A Document is a whole source (a PDF, a page). A Node is a chunk of a Document with metadata and relationships (previous/next). Indexes store Nodes.

Q2: Retriever vs query engine?
A2: A retriever only returns the relevant nodes. A query engine = retriever + response synthesizer (LLM) that returns a final answer.

Q3: LlamaIndex vs LangChain?
A3: LlamaIndex focuses on data ingestion, indexing and retrieval (RAG). LangChain is broader (chains, agents, tools). They can be combined.

Q4: What is `similarity_top_k`?
A4: How many most-similar chunks are retrieved and given to the LLM. More gives more context but more cost/noise.

Q5: How do you keep costs low?
A5: Persist the index, use a cheaper embedding model, tune chunk size, use `top_k` of 3 to 5, and cache frequent answers.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You build question-answering over your own documents (RAG)
- You need many data connectors and vector store integrations
- You want quick prototypes with sensible defaults

❌ Avoid when:
- A simple keyword/SQL search is enough
- You need full control over each step and want fewer abstractions (call the embedding API and a vector DB directly)
- The data is tiny enough to fit in one prompt

---

## 📊 Visual Diagram

```
Documents ─► SentenceSplitter ─► Nodes ─► Embedding model ─► VectorStoreIndex
                                                                   │
Question ─► Embedding ─► Retriever (top-k nodes) ◄─────────────────┘
                              │
                              ▼
                  LLM (question + nodes) ─► Answer + source_nodes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RAG | Retrieve then generate | पहले खोजो, फिर जवाब बनाओ |
| Document | Source data unit | मूल डेटा इकाई |
| Node | A chunk of a document | document का टुकड़ा |
| Embedding | Text as a number vector | text का number vector |
| Retriever | Finds relevant nodes | relevant nodes खोजने वाला |
| Query engine | Retriever + LLM | retriever + LLM मिलाकर जवाब |

---

## ⚡ 3-Line Summary
English: LlamaIndex turns your documents into a vector index and answers questions using retrieved chunks plus an LLM. Persist the index, always set the embedding model and LLM explicitly, and inspect `source_nodes` when debugging.
Hindi: LlamaIndex आपके documents को vector index बनाकर retrieved chunks और LLM से सवालों के जवाब देता है। Index persist करें, embedding model और LLM साफ़ सेट करें और debug में `source_nodes` देखें।

---

## ➡️ Next Topic
**390. Hugging Face Transformers** — run and fine-tune open-source models locally.
