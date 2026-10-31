---

# 193. LlamaIndex Loaders
# हिंदी में: LlamaIndex Loaders (Readers)

---

## 🔵 Simple Definition (English)
In LlamaIndex, loaders are called **readers**. `SimpleDirectoryReader` reads a folder of mixed files; LlamaHub offers hundreds of readers (Notion, Slack, databases, web). They return `Document` objects (text plus metadata) that LlamaIndex parses into **nodes** (chunks) for indexing.

## 🔵 सरल परिभाषा (Hindi)
LlamaIndex में loaders को **readers** कहते हैं। `SimpleDirectoryReader` एक folder की अलग-अलग files पढ़ता है; LlamaHub में सैकड़ों readers हैं (Notion, Slack, databases, web)। ये `Document` objects (text + metadata) लौटाते हैं जिन्हें LlamaIndex indexing के लिए **nodes** (chunks) में बदलता है।

---

## 🔴 Problem it Solves
Teams need one quick way to ingest messy folders and SaaS sources without writing parsers. LlamaIndex focuses on data ingestion for LLMs, so readers, node parsers and indexes fit together with sensible defaults (file-type detection, metadata such as file name and path).

## 🔴 यह क्यों बना? (Hindi)
Teams को messy folders और SaaS sources बिना parsers लिखे जल्दी ingest करने का एक तरीका चाहिए। LlamaIndex का फोकस LLM के लिए data ingestion है, इसलिए readers, node parsers और indexes अच्छे defaults के साथ एक-दूसरे से जुड़ते हैं (file-type detection, file name और path जैसा metadata)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install llama-index (core) and any reader packages you need
Step 2 → Create a reader: SimpleDirectoryReader(input_dir=..., required_exts=[...])
Step 3 → reader.load_data() -> list[Document] (file_name, file_path in metadata)
Step 4 → Node parser (SentenceSplitter) cuts Documents into nodes with overlap
Step 5 → IngestionPipeline can add transforms (splitter, metadata extractor, embeddings) and cache them
Step 6 → VectorStoreIndex(nodes) stores embeddings -> as_query_engine()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install llama-index और ज़रूरी reader packages
Step 2 → Reader बनाओ: SimpleDirectoryReader(input_dir=..., required_exts=[...])
Step 3 → reader.load_data() -> list[Document] (metadata में file_name, file_path)
Step 4 → Node parser (SentenceSplitter) Documents को overlap के साथ nodes में काटता है
Step 5 → IngestionPipeline में transforms (splitter, metadata extractor, embeddings) जोड़कर cache कर सकते हैं
Step 6 → VectorStoreIndex(nodes) embeddings रखता है -> as_query_engine()
```

---

## 🟡 Real World Example
**Tariff Classification System**: A shared folder has PDFs (tariffs), DOCX (internal rulings), CSV (rates) and MD (SOPs). `SimpleDirectoryReader("./tariff_data", recursive=True)` reads all of them, with `file_name` in the metadata so answers can cite "ruling_2024_17.docx". `IngestionPipeline` with a docstore skips unchanged files on re-run.
**Zomato AI**: Restaurant partner docs from Google Drive via a LlamaHub reader.

## 🟡 Real Example Hindi mein
**Tariff System**: Shared folder में PDFs (tariffs), DOCX (internal rulings), CSV (rates) और MD (SOPs) हैं। `SimpleDirectoryReader("./tariff_data", recursive=True)` सब पढ़ता है, metadata में `file_name` होता है ताकि जवाब "ruling_2024_17.docx" cite कर सके। Docstore वाली `IngestionPipeline` दोबारा चलाने पर unchanged files skip करती है।
**Zomato AI**: Google Drive से partner docs, LlamaHub reader के ज़रिए।

---

## 💻 Code Example — Basic
```python
# Offline-friendly: SimpleDirectoryReader + SentenceSplitter, no API key needed
# pip install llama-index-core
import tempfile
from pathlib import Path

from llama_index.core import SimpleDirectoryReader  # folder reader
from llama_index.core.node_parser import SentenceSplitter  # chunker

with tempfile.TemporaryDirectory() as folder:  # temp folder with two files
    Path(folder, "ruling.txt").write_text("HS 8518.30 earphones. Duty is 0 percent. Effective 2025.")
    Path(folder, "rates.md").write_text("# Rates\nHS 6403.99 footwear. Duty is 20 percent.")

    docs = SimpleDirectoryReader(input_dir=folder, required_exts=[".txt", ".md"]).load_data()  # read files
    print(len(docs), "documents")  # 2
    print(docs[0].metadata.get("file_name"))  # e.g. ruling.txt (order may vary)

    nodes = SentenceSplitter(chunk_size=64, chunk_overlap=8).get_nodes_from_documents(docs)  # chunk
    print(len(nodes), "nodes")  # at least 2
    print(nodes[0].get_content()[:60])  # first chunk text
```

## 💻 Code Example — Advanced
```python
# Production: IngestionPipeline with cache + docstore dedupe, custom metadata, async run
# pip install llama-index-core ; embeddings need an API key, so a stub embedding is used for offline runs
import asyncio
import logging
from pathlib import Path

from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document, TextNode
from llama_index.core.storage.docstore import SimpleDocumentStore

logger = logging.getLogger("li_ingest")  # logger

def file_meta(path: str) -> dict:
    """Metadata callback: called per file by the reader."""
    p = Path(path)  # file path
    return {"file_name": p.name, "folder": p.parent.name, "domain": "tariff"}

def load_folder(folder: str) -> list[Document]:
    try:
        reader = SimpleDirectoryReader(
            input_dir=folder, recursive=True, required_exts=[".pdf", ".txt", ".md", ".csv"],
            file_metadata=file_meta,  # custom metadata for every file
            filename_as_id=True,  # stable doc ids -> dedupe on re-run
        )
        return reader.load_data()  # blocking read
    except Exception:
        logger.exception("folder load failed: %s", folder)
        return []

async def ingest(folder: str, store: SimpleDocumentStore) -> list[TextNode]:
    docs = await asyncio.to_thread(load_folder, folder)  # run blocking reader in a thread
    pipeline = IngestionPipeline(
        transformations=[SentenceSplitter(chunk_size=512, chunk_overlap=50)],  # add embed model here for real use
        docstore=store,  # remembers doc hashes -> unchanged docs are skipped
    )
    nodes = await pipeline.arun(documents=docs)  # async run; only new/changed docs processed
    logger.info("ingested %d nodes from %d docs", len(nodes), len(docs))
    return nodes

if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        Path(d, "a.txt").write_text("HS 8518.30 earphones duty 0 percent. " * 20)
        store = SimpleDocumentStore()  # in-memory docstore
        print(len(asyncio.run(ingest(d, store))), "nodes first run")
        print(len(asyncio.run(ingest(d, store))), "nodes second run (unchanged -> 0)")
```

---

## 🟠 FastAPI Integration
Treat LlamaIndex as a library inside your service: ingestion endpoint runs the pipeline in the background; query endpoint calls `query_engine.aquery()`.

```python
# FastAPI + LlamaIndex query engine (needs an LLM + embedding key configured, e.g. OPENAI_API_KEY)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()  # app
query_engine = None  # set at startup after index is built/loaded

class Q(BaseModel):
    question: str  # user question

@app.on_event("startup")  # (newer code may use lifespan handlers)
async def startup() -> None:
    global query_engine
    from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
    docs = SimpleDirectoryReader("./tariff_data").load_data()  # load once
    query_engine = VectorStoreIndex.from_documents(docs).as_query_engine(similarity_top_k=4)

@app.post("/ask")
async def ask(q: Q) -> dict:
    if query_engine is None:
        raise HTTPException(status_code=503, detail="index not ready")
    resp = await query_engine.aquery(q.question)  # async query
    return {"answer": str(resp), "sources": [n.metadata.get("file_name") for n in resp.source_nodes]}
```

---

## 🔗 LangChain / LangGraph Connection
The two frameworks interoperate: LlamaIndex `Document` converts to LangChain `Document` via `doc.to_langchain_format()`, and LangChain's `Document` can be turned back with `Document.from_langchain_format(lc_doc)`. Many teams use LlamaIndex for ingestion and LangGraph for the agent flow, exposing a LlamaIndex retriever as a tool/node.

```python
# Use a LlamaIndex retriever inside a LangChain/LangGraph flow
from langchain_core.runnables import RunnableLambda

# li_retriever = index.as_retriever(similarity_top_k=4)   # LlamaIndex retriever
def li_search(q: str) -> list[str]:
    # nodes = li_retriever.retrieve(q)                    # returns NodeWithScore list
    # return [n.get_content() for n in nodes]
    return ["HS 8518.30 earphones duty 0"]                # stand-in so this block runs

retriever_runnable = RunnableLambda(li_search)  # now usable in LCEL / as a LangGraph node
print(retriever_runnable.invoke("earphones duty"))
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using legacy imports (`from llama_index import ...`).
✅ Correct: Since v0.10, imports come from `llama_index.core` and integration packages.

```python
# Wrong (old)
from llama_index import SimpleDirectoryReader
# Right
from llama_index.core import SimpleDirectoryReader
```

❌ Mistake 2: Re-ingesting all files on each run, creating duplicate nodes.
✅ Correct: Use stable document ids (`filename_as_id=True`) and an `IngestionPipeline` with a docstore.

```python
# Wrong
index = VectorStoreIndex.from_documents(docs)      # every run adds duplicates to a persistent store
# Right
pipeline = IngestionPipeline(transformations=[...], docstore=store, vector_store=vs)
pipeline.run(documents=docs)                       # upserts, skips unchanged
```

---

## 🧠 Tricky Interview Question
**Q**: "You loaded a folder of PDFs with `SimpleDirectoryReader`, and each PDF page became a separate Document. A table spanning pages got split. How do you handle it?"

**Answer**: The default PDF reader yields one Document per page, so cross-page structures are broken. Options: (1) concatenate pages first (`fs`/custom reader that merges), (2) use a layout-aware parser such as LlamaParse, Docling or Unstructured which preserves tables and outputs markdown, then split with a `MarkdownNodeParser`, (3) use hierarchical/auto-merging nodes so a parent node contains both pages, (4) add `page_label` metadata and retrieve neighbouring pages (sentence-window style) at query time.

---

## ⚫ Interview Questions + Answers

Q1: What is a "reader" in LlamaIndex?
A1: LlamaIndex's name for a document loader; `reader.load_data()` returns `Document` objects.

Q2: What is the difference between a Document and a Node?
A2: A Document is a whole source unit (file/page); a Node is a chunk of a Document with its own id, text, metadata and relationships (prev/next/parent).

Q3: What is LlamaHub?
A3: A registry of community readers (Notion, Slack, Google Drive, databases, web). Install the specific reader package.

Q4: Which file types does SimpleDirectoryReader support by default?
A4: Common ones such as PDF, DOCX, PPTX, CSV, MD, TXT, images (with extras); use `required_exts` to limit and `file_extractor` to override a type's parser.

Q5: How would you design incremental ingestion with LlamaIndex?
A5: `IngestionPipeline` with transformations, a persistent `docstore` (e.g., Redis/Mongo) and `vector_store`, stable document ids, and `docstore_strategy=DocstoreStrategy.UPSERTS` so changed docs replace old nodes and unchanged docs are skipped; schedule runs and log counts.

---

## 🔷 When to Use + When Not to Use
✅ Use LlamaIndex readers when:
- Many file types in a folder or many SaaS sources
- You want node-level features (hierarchical nodes, metadata extractors)
- Ingestion-centric apps

❌ Avoid when:
- Your stack is already fully LangChain and a LangChain loader exists (avoid two frameworks)
- You need tiny dependencies

---

## 📊 Visual Diagram
```
 Folder / Notion / Drive / DB
        │  SimpleDirectoryReader / LlamaHub reader
        ▼
   list[Document]  (file_name, file_path, custom meta)
        │  IngestionPipeline: SentenceSplitter (+ extractors, embeddings), docstore cache
        ▼
   list[TextNode]  (text, metadata, relationships)
        ▼
   VectorStoreIndex ──► as_query_engine() / as_retriever()
```

---

## 💰 Cost Impact
Readers are free; ingestion cost is embeddings (and LLM-based metadata extractors if you add them: roughly 1 LLM call per node, so 100k nodes with gpt-4o-mini at ~400 tokens each is about 6 USD).
Optimize: use the ingestion cache and docstore to skip unchanged documents, apply LLM extractors only where needed, keep chunk sizes sensible, and use cheaper embeddings.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reader | LlamaIndex loader | LlamaIndex का loader |
| Document | Source unit | Source की इकाई |
| Node | Chunk with relationships | Relationships वाला chunk |
| LlamaHub | Community reader registry | Community readers का registry |
| IngestionPipeline | Transform + cache pipeline | Transform + cache pipeline |
| Docstore | Stores doc hashes/nodes | Documents का record |

---

## ⚡ 3-Line Summary
English: LlamaIndex readers load files and SaaS data into Documents, which are split into Nodes.
`SimpleDirectoryReader` handles mixed folders; `IngestionPipeline` adds caching and dedupe.
Use `llama_index.core` imports and stable ids for clean re-runs.
Hindi: LlamaIndex readers files और SaaS data को Documents में लाते हैं, जो Nodes में बँटते हैं।
`SimpleDirectoryReader` mixed folders संभालता है; `IngestionPipeline` caching और dedupe देती है।
साफ़ re-runs के लिए `llama_index.core` imports और stable ids इस्तेमाल करो।

---

## ➡️ Next Topic
**194. Text Preprocessing**: cleaning loaded text before chunking and embedding.
