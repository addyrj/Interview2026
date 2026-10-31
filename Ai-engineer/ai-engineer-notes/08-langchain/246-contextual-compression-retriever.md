---

# 246. ContextualCompressionRetriever
# हिंदी में: ContextualCompressionRetriever (Context को छोटा करने वाला Retriever)

---

## 🔵 Simple Definition (English)
`ContextualCompressionRetriever` wraps a normal retriever and a **compressor**. First the base retriever fetches many chunks; then the compressor throws away irrelevant chunks or cuts each chunk down to only the sentences that answer the query. The LLM receives less, cleaner context.

## 🔵 सरल परिभाषा (Hindi)
`ContextualCompressionRetriever` एक normal retriever + एक **compressor** को जोड़ता है। पहले base retriever बहुत सारे chunks लाता है, फिर compressor irrelevant chunks हटा देता है या हर chunk में से सिर्फ़ वही sentences रखता है जो query का जवाब देते हैं। LLM को कम और साफ़ context मिलता है।

---

## 🔴 Problem it Solves
Chunks are written for the whole document, not for your question. A 500-token chunk about "Chapter 85" may contain only one useful sentence. Sending 4 such chunks wastes ~1,500 tokens, costs money, adds noise and triggers the "lost in the middle" problem. Reducing `k` alone fixes cost but risks missing the right chunk.

The idea: **retrieve wide (high recall), then compress (high precision)**.

## 🔴 यह क्यों बना? (Hindi)
Chunks पूरे document के लिए बने होते हैं, आपके सवाल के लिए नहीं। 500 token के chunk में शायद सिर्फ़ 1 sentence काम का हो। ऐसे 4 chunks भेजने से ~1,500 tokens बेकार जाते हैं, cost बढ़ती है और LLM confuse होता है। सिर्फ़ `k` घटाने से सही chunk छूट सकता है। इसलिए: **पहले wide retrieve करो (recall), फिर compress करो (precision)**।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User query arrives
Step 2 → base_retriever.invoke(query) returns k=10 chunks (wide net)
Step 3 → base_compressor.compress_documents(docs, query) runs
Step 4 → Compressor type decides what happens:
           LLMChainExtractor  -> LLM extracts only relevant sentences per chunk
           LLMChainFilter     -> LLM says YES/NO per chunk (drops whole chunks)
           EmbeddingsFilter   -> keeps chunks with cosine similarity >= threshold (no LLM call)
           Pipeline           -> chain several (split -> redundant filter -> relevance filter)
Step 5 → Shorter list[Document] returned to the chain
Step 6 → LLM answers from compact context
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User query आती है
Step 2 → base_retriever 10 chunks लाता है (wide net)
Step 3 → compressor.compress_documents(docs, query) चलता है
Step 4 → Compressor के type के हिसाब से:
           LLMChainExtractor -> LLM हर chunk से सिर्फ़ relevant sentences निकालता है
           LLMChainFilter    -> LLM हर chunk पर YES/NO बोलता है
           EmbeddingsFilter  -> similarity threshold से कम वाले chunks हटते हैं (LLM call नहीं)
           Pipeline          -> कई compressors एक के बाद एक
Step 5 → छोटी list[Document] आगे जाती है
Step 6 → LLM compact context से जवाब देता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: Query "Is a power bank a battery under heading 8507?". The vector search returns 10 chunks of Chapter 85 notes (≈5,000 tokens). `EmbeddingsFilter(similarity_threshold=0.76)` drops 6 unrelated chunks, and `LLMChainExtractor` trims the rest to 2 sentences each. Final context ≈ 400 tokens, 12x smaller, and the LLM focuses on the real rule.

**Amazon AI**: Product Q&A bot — reviews are long; the compressor keeps only the sentences about "battery life" when the question is about battery.

## 🟡 Real Example Hindi mein
**Tariff System**: Query "Power bank heading 8507 में आता है?"। Vector search Chapter 85 के 10 chunks (≈5,000 tokens) देता है। `EmbeddingsFilter` 6 बेकार chunks हटाता है और `LLMChainExtractor` बाकी को 2-2 sentences में छोटा करता है। Final context ≈ 400 tokens, यानी 12 गुना छोटा।

**Amazon AI**: Product Q&A bot — reviews लंबे होते हैं; सवाल battery का हो तो compressor सिर्फ़ battery वाले sentences रखता है।

---

## 💻 Code Example — Basic
```python
# Basic: ContextualCompressionRetriever with a custom compressor (offline, no API key)
# pip install langchain-core langchain-classic   (older versions: from langchain.retrievers import ...)
from typing import Optional, Sequence                                  # type hints
from langchain_core.callbacks import Callbacks                         # callbacks type for compressor
from langchain_core.documents import BaseDocumentCompressor, Document  # compressor base + Document
from langchain_core.retrievers import BaseRetriever                    # retriever base class
from langchain_classic.retrievers import ContextualCompressionRetriever  # the wrapper


class AllDocsRetriever(BaseRetriever):                                 # base retriever: returns everything
    docs: list[Document]                                               # our corpus

    def _get_relevant_documents(self, query: str, *, run_manager) -> list[Document]:
        return self.docs                                               # wide net: no filtering at all


class SentenceCompressor(BaseDocumentCompressor):                      # our compressor
    def compress_documents(                                            # required method
        self, documents: Sequence[Document], query: str, callbacks: Optional[Callbacks] = None
    ) -> Sequence[Document]:
        words = set(query.lower().split())                             # query words
        out: list[Document] = []                                       # compressed docs
        for doc in documents:                                          # each retrieved chunk
            kept = [s for s in doc.page_content.split(".")             # split chunk into sentences
                    if words & set(s.lower().split())]                 # keep sentences sharing a word
            if kept:                                                   # drop chunks with nothing useful
                out.append(Document(page_content=".".join(kept).strip(), metadata=doc.metadata))
        return out                                                     # shorter list, shorter text


corpus = [                                                             # long-ish chunks
    Document(page_content="Chapter 85 covers machines. Power banks are classified under 8507. Fax machines are 8443."),
    Document(page_content="Chapter 9 covers coffee. Roasted beans are 0901."),
]
base = AllDocsRetriever(docs=corpus)                                   # wide base retriever
retriever = ContextualCompressionRetriever(                            # wrap base + compressor
    base_compressor=SentenceCompressor(), base_retriever=base
)
for d in retriever.invoke("power banks"):                              # run the query
    print(d.page_content)                                              # only the useful sentence
```

## 💻 Code Example — Advanced
```python
# Production: pipeline = cheap embeddings filter first, expensive LLM extractor second
# pip install langchain-core langchain-classic langchain-openai
import asyncio                                                         # async demo
import logging                                                         # logging
from langchain_core.documents import Document                          # document type
from langchain_core.embeddings import Embeddings                       # embeddings type
from langchain_core.language_models import BaseChatModel               # llm type
from langchain_core.retrievers import BaseRetriever                    # retriever type
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import (
    DocumentCompressorPipeline,                                        # run compressors in order
    EmbeddingsFilter,                                                  # cheap: no LLM call
    LLMChainExtractor,                                                 # expensive: 1 LLM call per chunk
)

logger = logging.getLogger("tariff.compress")                          # logger


def build_compression_retriever(
    base: BaseRetriever, embeddings: Embeddings, llm: BaseChatModel
) -> ContextualCompressionRetriever:
    """Cheap filter removes obvious noise, so the LLM extractor sees fewer chunks."""
    cheap = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.76)  # tune on real data
    extractor = LLMChainExtractor.from_llm(llm)                        # trims each remaining chunk
    pipeline = DocumentCompressorPipeline(transformers=[cheap, extractor])  # order matters
    return ContextualCompressionRetriever(base_compressor=pipeline, base_retriever=base)


async def retrieve_compressed(r: ContextualCompressionRetriever, query: str) -> list[Document]:
    """Async retrieval with fallback to an empty context on failure."""
    try:
        docs = await asyncio.wait_for(r.ainvoke(query), timeout=10.0)  # compression adds latency
    except Exception:                                                  # timeout or LLM error
        logger.exception("compression failed for %r", query)           # log traceback
        return []                                                      # caller decides the fallback
    logger.info("kept %d docs after compression", len(docs))           # monitor the reduction
    return docs                                                        # compact context
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI, HTTPException                    # FastAPI
from pydantic import BaseModel, Field                                  # schemas
from langchain_classic.retrievers import ContextualCompressionRetriever

app = FastAPI()                                                        # app


def get_retriever() -> ContextualCompressionRetriever:
    raise NotImplementedError                                          # build once at startup, return it


class Query(BaseModel):                                                # request body
    question: str = Field(min_length=3, max_length=500)


@app.post("/context")                                                  # returns compressed context
async def context(q: Query, r: ContextualCompressionRetriever = Depends(get_retriever)) -> dict:
    try:
        docs = await r.ainvoke(q.question)                             # async compress + retrieve
    except Exception as exc:                                           # LLM / DB failure
        raise HTTPException(status_code=503, detail="retrieval failed") from exc
    text = "\n".join(d.page_content for d in docs)                     # final context string
    return {"chunks": len(docs), "chars": len(text), "context": text}  # chars help track size
```

---

## 🔗 LangChain / LangGraph Connection
```python
# Plug it into an LCEL RAG chain exactly like any retriever:
chain = (
    {"context": compression_retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)
# LangGraph: use it inside the "retrieve" node. Add a conditional edge:
# if no documents survive compression -> route to a "fallback / ask user" node
# instead of letting the LLM hallucinate with empty context.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `LLMChainExtractor` on every chunk with a big model
```python
# Wrong — k=20 chunks = 20 extra LLM calls per user query (slow + costly):
compressor = LLMChainExtractor.from_llm(ChatOpenAI(model="gpt-4o"))

# Correct — cheap model, and filter with embeddings first:
compressor = DocumentCompressorPipeline(transformers=[
    EmbeddingsFilter(embeddings=emb, similarity_threshold=0.76),
    LLMChainExtractor.from_llm(ChatOpenAI(model="gpt-4o-mini")),
])
```

❌ Mistake 2: Threshold copied blindly
```python
# Wrong — 0.76 is only an example; on your embedding model it may drop everything:
EmbeddingsFilter(embeddings=emb, similarity_threshold=0.99)

# Correct — measure similarity scores on labelled queries, then choose the threshold
# (or use k instead: EmbeddingsFilter(embeddings=emb, k=4)).
```

❌ Mistake 3: Compressing then losing metadata (sources)
```python
# Wrong — new Document without metadata, citations disappear:
Document(page_content=short_text)

# Correct — copy the metadata:
Document(page_content=short_text, metadata=doc.metadata)
```

---

## 🧠 Tricky Interview Question

**Q**: "You added `LLMChainExtractor` to save tokens, but your bill went UP. Why?"

**Answer**: The extractor makes one LLM call per retrieved chunk. Those calls are billed for the full chunk as input plus the extracted text as output. If the base retriever returns 20 chunks of 500 tokens, you pay ~10,000 input tokens for extraction alone, before the final answer call. Savings only appear on the final call. Fix: put a free `EmbeddingsFilter` first, use a small model, lower the base `k`, or skip LLM extraction and use a cross-encoder re-ranker. Always compare *total* tokens across all calls, not only the final prompt.

---

## ⚫ Interview Questions + Answers

Q1: What does ContextualCompressionRetriever do? (Easy)
A1: It wraps a base retriever and a compressor. It retrieves documents, then compresses or filters them with respect to the query before returning them.

Q2: Name the built-in compressors. (Easy)
A2: `LLMChainExtractor` (extract relevant parts), `LLMChainFilter` (keep/drop whole docs), `EmbeddingsFilter` (similarity threshold or top-k, no LLM), and `DocumentCompressorPipeline` (chain of compressors/transformers).

Q3: LLMChainExtractor vs EmbeddingsFilter? (Medium)
A3: Extractor rewrites each chunk with an LLM — precise but slow and costly. EmbeddingsFilter only keeps or drops whole chunks by cosine similarity — fast and nearly free but cannot shorten a chunk. Combine them in a pipeline.

Q4: How do you build a custom compressor? (Medium)
A4: Subclass `BaseDocumentCompressor` and implement `compress_documents(documents, query, callbacks=None)`. A cross-encoder re-ranker is a common custom compressor.

Q5: Compare compression with simply using smaller chunks and lower k. (Hard)
A5: Small chunks lose surrounding context and hurt recall; low k risks missing the right chunk. Compression lets you retrieve wide for recall and still send little to the LLM. The price is extra latency and possible extra LLM calls. For strict latency budgets prefer a re-ranker or good chunking; for long noisy documents (legal, tariff notes) compression pays off.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chunks are long and mostly irrelevant to a specific question
- Context cost or "lost in the middle" quality issues appear
- You need high recall first, then precision

❌ Avoid when:
- Chunks are already small and focused
- Latency budget is very tight (LLM extractor adds seconds)
- Exact wording matters (legal text) — extraction can drop qualifiers like "except"

---

## 📊 Visual Diagram
```
Query
  │
  ▼
Base Retriever (k=10)  ──►  10 chunks ≈ 5,000 tokens
  │
  ▼
┌─────────────────────────────────────┐
│ DocumentCompressorPipeline          │
│  1. EmbeddingsFilter  (10 → 4)      │  free
│  2. LLMChainExtractor (4 chunks     │  small LLM call each
│     → 2 sentences each)             │
└─────────────────────────────────────┘
  │
  ▼
Compressed context ≈ 400 tokens ──► Final LLM ──► Answer
```

---

## 💰 Cost Impact
Without compression: 10 chunks × 500 = 5,000 input tokens per query. With gpt-4o-mini ($0.15/1M input): $0.00075 per query.
With pipeline: EmbeddingsFilter ≈ 10 chunk embeddings (cheap), LLMChainExtractor on 4 chunks ≈ 2,000 input + 200 output tokens ≈ $0.00042, final call 400 tokens ≈ $0.00006. Total ≈ $0.0005 — a small saving but better answer quality, and a big saving if the final model is expensive (gpt-4o: input at 16x the price of mini).

Optimise: filter before extraction, cache compression results per (query, chunk id), use a small model, and track both calls with callbacks (topic 264).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Compressor | Shrinks or filters retrieved docs | Docs को छोटा/फ़िल्टर करने वाला |
| LLMChainExtractor | LLM keeps relevant sentences | LLM से relevant sentences निकालना |
| EmbeddingsFilter | Similarity threshold filter | Similarity से filter |
| Pipeline | Several compressors in order | कई compressors क्रम में |
| Recall / Precision | Found all / only relevant | सब मिला / सिर्फ़ सही मिला |
| Lost in the middle | LLM ignores middle context | बीच का context ignore होना |

---

## ⚡ 3-Line Summary
English: ContextualCompressionRetriever retrieves wide, then compresses to what matters for the query. Use a cheap EmbeddingsFilter before an LLM extractor to avoid extra calls. Always measure total tokens across all calls.
Hindi: ContextualCompressionRetriever पहले wide retrieve करता है, फिर query के हिसाब से compress करता है। LLM extractor से पहले सस्ता EmbeddingsFilter लगाओ। हमेशा सभी calls के कुल tokens नापो।

---

## ➡️ Next Topic
**247. MultiQueryRetriever** — the opposite problem: one query is too narrow, so generate several rephrasings to improve recall.
