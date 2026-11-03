---

# 507. Designing RAG at Scale
# हिंदी में: बड़े Scale पर RAG Design करना

---

## 🔵 Simple Definition (English)
Designing RAG at scale means building retrieval-augmented generation that stays fast, accurate and cheap with millions of documents and many users. It splits the system into an offline ingestion path and an online query path, and scales each separately.

## 🔵 सरल परिभाषा (Hindi)
Scale पर RAG design का मतलब है लाखों documents और बहुत users के साथ भी RAG तेज़, सही और सस्ता रहे। System को offline ingestion path और online query path में बाँटकर दोनों को अलग-अलग scale किया जाता है।

---

## 🔴 Problem it Solves
A demo RAG (one script, in-memory index) breaks at scale: ingestion is slow, indexes do not fit memory, queries are slow, data goes stale, and one user may see another user's documents. Scale design fixes these.

## 🔴 यह क्यों बना? (Hindi)
Demo RAG (एक script, in-memory index) scale पर टूट जाता है: ingestion धीमा, index memory में नहीं आता, queries धीमी, data पुराना, और एक user को दूसरे के documents दिख सकते हैं। Scale design ये सब ठीक करता है।

---

## 🟢 How it Works — Step by Step

```
OFFLINE (ingestion)
Step 1 → Sources → queue (new/changed docs)
Step 2 → Parse, clean, chunk, add metadata (tenant, version, date)
Step 3 → Batch embed with workers
Step 4 → Upsert into vector DB (+ keyword index)

ONLINE (query)
Step 5 → API validates, authenticates, checks cache
Step 6 → Query rewrite -> hybrid retrieval (filtered by tenant)
Step 7 → Rerank top candidates
Step 8 → Build prompt within token budget -> LLM -> verify citations
Step 9 → Log, cache, return
```

## 🟢 कैसे काम करता है? (Hindi)
```
OFFLINE: Sources → queue → parse/chunk/metadata → batch embed → vector DB में upsert
ONLINE: API auth + cache check → query rewrite → hybrid retrieval (tenant filter)
        → rerank → token budget में prompt → LLM → citations verify → log + cache
```

---

## 🟡 Real World Example
**Tariff Classification System**: 2 million tariff notes, rulings and past classifications across many countries. Ingestion runs nightly for changed rulings via a queue and workers. Query path: cache, hybrid search filtered by country and tariff year, rerank top 30 to top 5, LLM answers with ruling citation.
**Amazon-style example**: Product-help search over millions of listings with seller-specific access rules.

## 🟡 Real Example Hindi mein
**Tariff System**: 20 लाख tariff notes, rulings और पुराने classifications। Ingestion रात में बदले हुए rulings के लिए queue + workers से चलता है। Query path: cache, country और tariff year से filtered hybrid search, top 30 को rerank करके top 5, LLM ruling citation के साथ जवाब देता है।

---

## 💻 Code Example — Basic
```python
# Basic: tiny RAG with chunking, keyword scoring and prompt budget (pure Python, offline)
def chunk(text: str, size: int = 8, overlap: int = 2) -> list[str]:  # split words with overlap
    words = text.split()  # tokenise by space
    step = size - overlap  # stride
    return [" ".join(words[i:i + size]) for i in range(0, max(len(words), 1), step)]  # windows


def score(query: str, doc: str) -> int:  # toy relevance
    return len(set(query.lower().split()) & set(doc.lower().split()))  # shared words


docs = chunk("Smartphones are classified under heading 8517 as telephone sets for cellular networks. "
             "Cotton shirts fall under chapter 61 knitted apparel.")  # make chunks
query = "smartphones telephone heading"  # user question
top = sorted(docs, key=lambda d: score(query, d), reverse=True)[:2]  # best two chunks
prompt = "Context:\n" + "\n".join(top) + f"\nQuestion: {query}"  # prompt assembly
print(prompt)  # show final prompt
```

## 💻 Code Example — Advanced
```python
# Advanced: async query path with cache, tenant filter, timeout, fallback (offline mocks)
import asyncio  # async runtime
import hashlib  # cache key
from typing import Optional  # optional type

CACHE: dict[str, str] = {}  # in-memory cache (use Redis in production)
INDEX = [("t1", "Smartphones heading 8517"), ("t2", "Cotton shirts chapter 61")]  # (tenant, text)


def key(tenant: str, q: str) -> str:  # build cache key including tenant (security!)
    return hashlib.sha256(f"{tenant}:{q}".encode()).hexdigest()  # stable hash


async def retrieve(tenant: str, q: str) -> list[str]:  # mock vector search with tenant filter
    await asyncio.sleep(0.01)  # simulate DB latency
    return [t for ten, t in INDEX if ten == tenant]  # only that tenant's data


async def generate(q: str, ctx: list[str]) -> str:  # mock LLM
    await asyncio.sleep(0.02)  # simulate model latency
    return f"Answer based on {len(ctx)} chunk(s)"  # fake answer


async def answer(tenant: str, q: str, timeout: float = 3.0) -> Optional[str]:  # online path
    k = key(tenant, q)  # compute key
    if k in CACHE:  # cache hit
        return CACHE[k]  # return quickly
    try:  # guard the pipeline
        ctx = await asyncio.wait_for(retrieve(tenant, q), timeout)  # retrieve with timeout
        out = await asyncio.wait_for(generate(q, ctx), timeout)  # generate with timeout
    except asyncio.TimeoutError:  # slow dependency
        return None  # caller shows fallback message
    CACHE[k] = out  # store result
    return out  # return


if __name__ == "__main__":
    print(asyncio.run(answer("t1", "phone code?")))  # run once
```

---

## 🟠 FastAPI Integration
Keep the API stateless so you can run many replicas. Use dependency injection for clients (vector DB, LLM, cache), stream tokens, and return citations.

```python
from fastapi import FastAPI, Header, HTTPException  # app, headers, errors
from pydantic import BaseModel  # schema

app = FastAPI()  # app


class Ask(BaseModel):  # request
    question: str  # user question


@app.post("/rag")  # route
async def rag(body: Ask, x_tenant: str = Header(...)) -> dict[str, object]:
    if not x_tenant:  # tenant is mandatory
        raise HTTPException(status_code=401, detail="tenant required")  # reject
    # In production: tenant filter goes INTO the vector query, not after it.
    return {"answer": "stub", "citations": ["ruling-123"], "tenant": x_tenant}  # response
```

---

## 🔗 LangChain / LangGraph Connection
LangChain provides loaders, splitters, vector store integrations and retriever interfaces. LangGraph orchestrates agentic RAG: rewrite, retrieve, grade documents, then generate or re-retrieve.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter  # real splitter class

splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=40)  # chunk config
chunks = splitter.split_text("Tariff note. " * 100)  # split a long text
print(len(chunks), "chunks")  # count
# retriever = vectorstore.as_retriever(search_kwargs={"k": 20, "filter": {"tenant": "t1"}})  # query path
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Filtering by tenant after retrieval
✅ Correct: filter inside the vector query (and cache key).
```python
# Wrong
results = vdb.search(q, k=5); results = [r for r in results if r.tenant == t]  # may return nothing
# Right
results = vdb.search(q, k=5, filter={"tenant": t})  # filter first
```

❌ Mistake 2: Re-embedding everything on each update
✅ Correct: hash chunks and upsert only changed ones.
```python
# Wrong
embed_all(docs)  # costly
# Right
embed_only([d for d in docs if sha(d) not in known_hashes])  # incremental
```

---

## 🧠 Tricky Interview Question
**Q**: "Retrieval latency doubled after growing from 1M to 10M chunks. What do you check?"

**Answer**: Index type and parameters (HNSW ef_search, memory vs disk), whether the index fits RAM, filtered search performance (post-filtering is slow), shard count and replicas, embedding dimension, network hops and cold caches. Fixes: reduce dimensions or use quantisation, add shards, use partitioning by tenant, tune ef_search for recall/latency, add caching.

---

## ⚫ Interview Questions + Answers

Q1: Why separate ingestion and query paths? (Easy)
A1: They have different load patterns and scaling needs; ingestion is batch and heavy, query is latency-sensitive.

Q2: What metadata would you store with each chunk? (Easy)
A2: Source id, version/date, tenant or ACL, section title, language, chunk position.

Q3: How do you handle stale documents? (Medium)
A3: Change detection by hash or event, incremental upsert, delete old versions, store timestamps, and filter by freshness at query time.

Q4: How do you evaluate RAG at scale? (Medium)
A4: Separate retrieval metrics (recall@k, MRR) from generation metrics (faithfulness, answer correctness). Keep a golden set, run in CI, and sample production traffic.

Q5: How do you enforce per-user document permissions? (Hard)
A5: Store ACL or group ids as metadata and apply the filter inside the search query. Include user scope in cache keys. Sync permission changes quickly. Audit logs prove nothing leaked.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Knowledge is large, changing and needs citations
- Many tenants or users with different access

❌ Avoid when:
- Data fits in a prompt (a few pages): simple prompt is cheaper
- Behaviour or style change needed: consider fine-tuning

---

## 📊 Visual Diagram
```
OFFLINE:  Sources → Queue → Parse/Chunk → Embed workers → Vector DB + Keyword idx
                                                              ▲
ONLINE:   User → API → Cache? ──hit──▶ answer                │
                   │miss                                      │
                   ▼                                          │
              Rewrite → Hybrid retrieve (tenant filter) ──────┘
                   ▼
               Rerank → Prompt builder → LLM → Citation check → answer
```

---

## 💰 Cost Impact
Main costs: embedding (one time per chunk), vector DB hosting, and LLM tokens per query. Retrieved context dominates input tokens: 5 chunks x 300 tokens = 1,500 tokens per query (illustrative).
Optimise: fewer, better chunks via reranking, semantic cache, smaller embedding dimensions, quantised vectors, cheaper model for easy queries, and incremental ingestion.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ingestion | Loading and indexing docs | डेटा index करना |
| Sharding | Splitting index across nodes | index बाँटना |
| ACL | Access control list | access नियम |
| Recall@k | Relevant found in top k | top k में सही मिलना |
| Hybrid search | Keyword plus vector | मिला-जुला search |
| Upsert | Insert or update | जोड़ो या बदलो |

---

## ⚡ 3-Line Summary
English: Split RAG into offline ingestion and online query paths and scale each.
Filter by tenant inside the search, cache carefully, and rerank for quality.
Measure retrieval and generation separately.
Hindi: RAG को offline ingestion और online query में बाँटो और अलग scale करो।
Tenant filter search के अंदर लगाओ, cache सावधानी से, quality के लिए rerank।
Retrieval और generation अलग measure करो।

---

## ➡️ Next Topic
**508. RAG Architecture Decisions** — naive vs advanced vs agentic RAG and when each fits.
