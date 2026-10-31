---

# 245. Retrievers in LangChain
# हिंदी में: LangChain में Retrievers

---

## 🔵 Simple Definition (English)
A **Retriever** is a LangChain component that takes a query string and returns a list of relevant `Document` objects. It is a `Runnable`: `retriever.invoke("query")` → `list[Document]`. Unlike a vector store, a retriever only *returns* documents — it does not need to *store* them. The source can be a vector DB, BM25, SQL, an API or a web search.

## 🔵 सरल परिभाषा (Hindi)
Retriever LangChain का component है जो एक query string लेकर relevant `Document` objects की list लौटाता है। यह एक `Runnable` है: `retriever.invoke("query")` → `list[Document]`। Vector store documents को *store* करता है, जबकि retriever सिर्फ़ *वापस लाता* है। Source कुछ भी हो सकता है: vector DB, BM25, SQL, API या web search।

---

## 🔴 Problem it Solves
Every vector DB (Pinecone, Chroma, FAISS, pgvector) has a different API: `query()`, `similarity_search()`, `search()`. If your RAG chain calls a specific DB directly, switching the DB means rewriting the chain. Also, you want to plug in extra logic (re-ranking, query rewriting, hybrid search) without touching the rest of the chain.

A retriever gives ONE standard interface: `str → list[Document]`. Any chain that accepts a retriever works with any backend.

## 🔴 यह क्यों बना? (Hindi)
हर vector DB का अपना API होता है (`query()`, `similarity_search()`, `search()`)। Chain में सीधे DB call करने पर DB बदलना = chain दोबारा लिखना। Retriever एक standard interface देता है: `str → list[Document]`। Retriever को बदलो, बाकी chain वैसी की वैसी रहती है। Re-ranking, query rewriting, hybrid search जैसी extra logic भी इसी interface के पीछे जुड़ जाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Documents are split into chunks and embedded (indexing time, done once)
Step 2 → Chunks stored in a vector store (or any index)
Step 3 → vectorstore.as_retriever(search_kwargs={"k": 4}) wraps the store as a Retriever
Step 4 → At query time: retriever.invoke(query) is called
Step 5 → Query is embedded, nearest chunks are found (similarity / MMR / threshold)
Step 6 → Retriever returns list[Document] (page_content + metadata)
Step 7 → Chain stuffs documents into the prompt → LLM answers (tokens are billed here)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Documents को chunks में split करके embed करो (indexing, एक बार)
Step 2 → Chunks vector store में store करो
Step 3 → vectorstore.as_retriever(search_kwargs={"k": 4}) से Retriever बनाओ
Step 4 → Query आने पर retriever.invoke(query) call होता है
Step 5 → Query embed होती है, सबसे पास वाले chunks मिलते हैं
Step 6 → Retriever list[Document] लौटाता है
Step 7 → Chain इन्हें prompt में डालती है → LLM जवाब देता है (tokens यहीं charge होते हैं)
```

---

## 🟡 Real World Example
**Tariff Classification System**: User asks "HS code for lithium-ion power bank?". The retriever searches 40,000 tariff-note chunks and returns the top 4 (Chapter 85 notes, heading 8507). Only those 4 chunks go to the LLM, not the whole 5,000-page tariff book. If later the team moves from Chroma to pgvector, only the retriever line changes.

**Zomato AI**: "Best vegan pizza near me under 400" — a retriever fetches 5 matching restaurant-menu documents, the LLM writes the recommendation.

## 🟡 Real Example Hindi mein
**Tariff System**: User पूछता है "Power bank का HS code?"। Retriever 40,000 chunks में से top 4 (Chapter 85, heading 8507) लौटाता है। सिर्फ़ ये 4 chunks LLM को जाते हैं, पूरी 5,000 page की book नहीं। बाद में Chroma से pgvector जाना हो तो सिर्फ़ retriever वाली line बदलेगी।

**Zomato AI**: "400 से कम में vegan pizza" — retriever 5 menu documents लाता है, LLM recommendation लिखता है।

---

## 💻 Code Example — Basic
```python
# Basic: a custom retriever + the standard Runnable interface (runs offline, no API key)
from langchain_core.documents import Document                      # Document = page_content + metadata
from langchain_core.retrievers import BaseRetriever                # base class for all retrievers
from langchain_core.callbacks import CallbackManagerForRetrieverRun  # passed to _get_relevant_documents


class KeywordRetriever(BaseRetriever):                             # our own simple retriever
    docs: list[Document]                                           # the corpus we search in
    k: int = 2                                                     # how many documents to return

    def _get_relevant_documents(                                   # the ONE method we must implement
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        words = set(query.lower().split())                         # split query into lowercase words
        scored: list[tuple[int, Document]] = []                    # (score, doc) pairs
        for doc in self.docs:                                      # go through every document
            overlap = len(words & set(doc.page_content.lower().split()))  # count shared words
            scored.append((overlap, doc))                          # remember the score
        scored.sort(key=lambda pair: pair[0], reverse=True)        # best score first
        return [d for score, d in scored[: self.k] if score > 0]   # top-k with at least 1 match


corpus = [                                                         # tiny tariff knowledge base
    Document(page_content="HS 8507 lithium-ion batteries and power banks", metadata={"chapter": 85}),
    Document(page_content="HS 8517 smartphones and telephone sets", metadata={"chapter": 85}),
    Document(page_content="HS 0901 coffee beans roasted or not", metadata={"chapter": 9}),
]

retriever = KeywordRetriever(docs=corpus, k=2)                     # create the retriever
results = retriever.invoke("lithium power banks")                  # standard Runnable call
for doc in results:                                                # print what we got
    print(doc.metadata, "->", doc.page_content)                    # metadata + text

# Every retriever is a Runnable, so batch() also works:
print(len(retriever.batch(["coffee", "smartphones"])))             # 2 result lists
```

## 💻 Code Example — Advanced
```python
# Production: vector-store retriever with MMR, metadata filter, error handling, async
# pip install langchain-core langchain-openai langchain-chroma
import asyncio                                                     # to run the async demo
import logging                                                     # log failures
from langchain_core.documents import Document                      # document type
from langchain_core.retrievers import BaseRetriever                # retriever type for hints
from langchain_core.vectorstores import VectorStore                # any vector store

logger = logging.getLogger("tariff.retrieval")                     # module logger


def build_retriever(store: VectorStore, chapter: int | None = None) -> BaseRetriever:
    """Wrap a vector store as a retriever (MMR = relevant AND diverse results)."""
    search_kwargs: dict[str, object] = {"k": 4, "fetch_k": 20}     # fetch 20, keep best 4 diverse
    if chapter is not None:                                        # optional metadata filter
        search_kwargs["filter"] = {"chapter": chapter}             # store-specific filter syntax
    return store.as_retriever(search_type="mmr", search_kwargs=search_kwargs)  # returns a Retriever


async def safe_retrieve(retriever: BaseRetriever, query: str) -> list[Document]:
    """Retrieve with validation, timeout and graceful fallback."""
    if not query.strip():                                          # empty query is a caller bug
        raise ValueError("query must not be empty")                # fail fast, no embedding cost
    try:
        # ainvoke is the async twin of invoke; timeout protects the API from slow DBs
        return await asyncio.wait_for(retriever.ainvoke(query), timeout=5.0)
    except asyncio.TimeoutError:                                   # DB too slow
        logger.warning("retrieval timeout for %r", query)          # log for monitoring
        return []                                                  # chain can answer "no context"
    except Exception:                                              # any other backend error
        logger.exception("retrieval failed")                       # full traceback in logs
        return []                                                  # degrade, do not crash


def format_docs(docs: list[Document]) -> str:
    """Join documents into one context string (this text is what costs tokens)."""
    return "\n\n".join(f"[{d.metadata.get('hs_code', '?')}] {d.page_content}" for d in docs)
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI, HTTPException                # FastAPI core
from pydantic import BaseModel, Field                              # request / response models
from langchain_core.retrievers import BaseRetriever                # type hint

app = FastAPI()                                                    # the app


def get_retriever() -> BaseRetriever:
    """Dependency: build retriever once in real code (e.g. in lifespan) and return it."""
    raise NotImplementedError                                      # replace with your retriever


class SearchRequest(BaseModel):                                    # input schema
    query: str = Field(min_length=3, max_length=500)               # reject junk / huge input


class Hit(BaseModel):                                              # one result
    text: str
    hs_code: str | None = None


@app.post("/search", response_model=list[Hit])                     # retrieval-only endpoint
async def search(req: SearchRequest, r: BaseRetriever = Depends(get_retriever)) -> list[Hit]:
    try:
        docs = await r.ainvoke(req.query)                          # async retrieval (no LLM cost)
    except Exception as exc:                                       # backend failure
        raise HTTPException(status_code=503, detail="search backend unavailable") from exc
    return [Hit(text=d.page_content, hs_code=d.metadata.get("hs_code")) for d in docs]
```
A retrieval-only endpoint is useful for debugging: you can see exactly which chunks the LLM would receive.

---

## 🔗 LangChain / LangGraph Connection
```python
# Retriever is a Runnable, so it plugs straight into LCEL with the | operator:
from langchain_core.output_parsers import StrOutputParser          # AIMessage -> str
from langchain_core.prompts import ChatPromptTemplate              # prompt template
from langchain_core.runnables import RunnablePassthrough           # forwards the question

prompt = ChatPromptTemplate.from_template(
    "Context:\n{context}\n\nQuestion: {question}\nAnswer using only the context."
)
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}  # parallel map
    | prompt                                                       # fill the template
    | llm                                                          # any chat model
    | StrOutputParser()                                            # return plain text
)
# answer = chain.invoke("HS code for power bank?")

# LangGraph: a retrieve node just calls retriever.invoke(state["question"])
# and writes state["documents"]; a generate node reads it.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling the vector store directly inside the chain
```python
# Wrong — chain is glued to Chroma's API:
docs = chroma_db.similarity_search(question, k=4)

# Correct — depend on the Retriever interface:
retriever = chroma_db.as_retriever(search_kwargs={"k": 4})
docs = retriever.invoke(question)
```

❌ Mistake 2: Using the sync `invoke` inside an `async def` endpoint
```python
# Wrong — blocks the event loop, other requests wait:
@app.post("/ask")
async def ask(q: str):
    return retriever.invoke(q)

# Correct — await the async method:
@app.post("/ask")
async def ask(q: str):
    return await retriever.ainvoke(q)
```

❌ Mistake 3: Using the removed `get_relevant_documents`
```python
# Wrong (deprecated, removed in newer versions):
docs = retriever.get_relevant_documents(q)

# Correct:
docs = retriever.invoke(q)
```

---

## 🧠 Tricky Interview Question

**Q**: "Your retriever returns 4 chunks but the answer is wrong, even though the correct chunk is in the DB. Where do you look first?"

**Answer**: Debug retrieval separately from generation. Call `retriever.invoke(question)` alone and print the chunks. Typical causes: (1) wrong chunk size (answer split across chunks), (2) `k` too small, (3) embedding model mismatch between indexing and querying, (4) pure semantic search missing exact codes like "8507.60" (needs hybrid/BM25 — see Ensemble), (5) a metadata filter silently excluding the chunk. Measure with recall@k before changing the prompt or the LLM.

---

## ⚫ Interview Questions + Answers

Q1: What is a Retriever in LangChain? (Easy)
A1: A Runnable that maps a query string to `list[Document]`. It is the standard interface between a RAG chain and any data source.

Q2: Difference between a vector store and a retriever? (Easy)
A2: A vector store stores embeddings and supports add/delete/search. A retriever only retrieves. `vectorstore.as_retriever()` converts one into the other. Not every retriever has a vector store (BM25, SQL, web search).

Q3: What are the `search_type` options of `as_retriever`? (Medium)
A3: `"similarity"` (top-k nearest), `"mmr"` (maximal marginal relevance — balances relevance and diversity, uses `fetch_k` and `lambda_mult`), `"similarity_score_threshold"` (returns only docs above `score_threshold`). MMR removes near-duplicate chunks, saving tokens.

Q4: How do you write a custom retriever? (Medium)
A4: Subclass `BaseRetriever` and implement `_get_relevant_documents(self, query, *, run_manager)`. Optionally implement `_aget_relevant_documents` for native async. You get `invoke`, `ainvoke`, `batch`, streaming and callbacks for free.

Q5: Design retrieval for 1M tariff chunks with p95 latency under 300 ms. (Hard)
A5: Use an ANN index (HNSW) with metadata pre-filtering (chapter/country), retrieve `k=20` cheaply, then re-rank to 4 with a cross-encoder (see ContextualCompressionRetriever). Add hybrid search (BM25 + vectors) for exact HS codes. Cache embeddings of frequent queries, set a timeout with graceful fallback, and monitor recall@k on a labelled query set.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building RAG: the LLM needs external, private or fresh knowledge
- You want to swap vector DBs without rewriting chains
- You need a plug-in point for hybrid search, re-ranking or filters

❌ Avoid when:
- The whole knowledge fits comfortably in the prompt (just include it)
- The task needs exact structured lookup — use SQL / a normal API
- You need aggregation over all data ("how many tariffs...") — retrieval returns only top-k

---

## 📊 Visual Diagram
```
 Question ──► Retriever ──► [Doc1, Doc2, Doc3, Doc4] ──► Prompt ──► LLM ──► Answer
                 │
     ┌───────────┼────────────┬──────────┐
     ▼           ▼            ▼          ▼
 VectorStore    BM25       SQL/API    Web search
 (Chroma...)  (keywords)  (structured) (fresh data)

 Same interface:  str  ──►  list[Document]
```

---

## 💰 Cost Impact
Retrieval itself costs only one query embedding (e.g. ~20 tokens ≈ $0.0000004 with text-embedding-3-small). The big cost is what you retrieve: each chunk of ~500 tokens × k=4 = 2,000 extra input tokens per request. With gpt-4o-mini input at $0.15/1M, 100K queries/day × 2,000 tokens = 200M tokens ≈ $30/day just for context.

Optimisations: lower `k`, use MMR to drop duplicates, compress chunks (topic 246), cache frequent queries, and put a cheap filter (metadata) before the vector search.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Retriever | Query → relevant documents Runnable | Query से documents लाने वाला component |
| Document | `page_content` + `metadata` | Text + उसकी जानकारी |
| `as_retriever` | Converts vector store to retriever | Vector store को retriever बनाना |
| MMR | Relevance + diversity ranking | Relevant और अलग-अलग results |
| `k` | Number of docs returned | कितने documents लौटें |
| recall@k | Was the right doc in top k | सही doc top k में आया या नहीं |

---

## ⚡ 3-Line Summary
English: A Retriever turns a query into relevant `Document`s through one standard interface. It is a Runnable, so it composes with LCEL and works with any backend. Retrieved chunk size and `k` directly decide your token cost.
Hindi: Retriever एक standard interface से query को relevant `Document`s में बदलता है। यह Runnable है, इसलिए LCEL में जुड़ता है और किसी भी backend के साथ चलता है। Chunk size और `k` सीधे token cost तय करते हैं।

---

## ➡️ Next Topic
**246. ContextualCompressionRetriever** — shrink retrieved chunks to only the useful sentences, cutting token cost and noise.
