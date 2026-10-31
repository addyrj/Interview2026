---

# 173. Contextual Chunking (Anthropic method)
# हिंदी में: Contextual Chunking (Anthropic का तरीका - Contextual Retrieval)

---

## 🔵 Simple Definition (English)
Before embedding a chunk, ask an LLM to write one or two short sentences that place the chunk inside the whole document (for example "This chunk is from the 2025 customs ruling on 5G smartphones, classification section"). Prepend that sentence to the chunk, then embed and BM25-index the combined text. Anthropic calls this "Contextual Retrieval" (contextual embeddings + contextual BM25).

## 🔵 सरल परिभाषा (Hindi)
Chunk को embed करने से पहले LLM से एक-दो छोटे वाक्य लिखवाओ जो बताएँ कि यह chunk पूरे document में कहाँ आता है (जैसे "यह chunk 2025 की 5G smartphones वाली customs ruling के classification section से है")। उस वाक्य को chunk के आगे जोड़ो, फिर जुड़े हुए text को embed और BM25 index करो। Anthropic इसे "Contextual Retrieval" कहता है।

---

## 🔴 Problem it Solves
- Chunk "The rate rose by 3% over the previous year" has no company, product or year. Embeddings and keyword search cannot tell which document it belongs to.
- Chunks lose context when cut from a long document; overlap does not restore the title or topic.
- Anthropic reported (in their Contextual Retrieval write-up) that adding context cut top-20 retrieval failures by about 35% with contextual embeddings, about 49% when combined with contextual BM25, and about 67% when also reranking. Treat these as published reference numbers, and measure on your own data.

## 🔴 यह क्यों बना? (Hindi)
- Chunk "The rate rose by 3% over the previous year" में company, product, साल कुछ नहीं। Embedding और keyword search नहीं जान सकते कि यह किस document का है।
- लंबे document से कटने पर chunk context खो देता है; overlap से title या topic वापस नहीं आता।
- Anthropic की write-up के अनुसार context जोड़ने से top-20 retrieval failures लगभग 35% घटे (contextual embeddings), लगभग 49% (contextual BM25 के साथ), और लगभग 67% (reranking के साथ)। इन्हें reference numbers मानो; अपने data पर खुद मापो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Split the document into normal chunks (any splitter, 200-500 tokens)
Step 2 → For each chunk, build a prompt: <document>WHOLE DOC</document> + <chunk>CHUNK</chunk>
Step 3 → Ask a small, cheap LLM: "Write 1-2 sentences situating this chunk in the document"
Step 4 → Contextualised chunk = context sentence + "\n" + original chunk
Step 5 → Embed the contextualised chunk (contextual embeddings)
Step 6 → Also add it to the BM25 / keyword index (contextual BM25)
Step 7 → At query time: vector search + BM25, merge (rank fusion), optionally rerank
Step 8 → Use prompt caching so the whole document is paid for only once across its chunks
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Document को सामान्य chunks में बाँटो (200-500 tokens)
Step 2 → हर chunk के लिए prompt: <document>पूरा doc</document> + <chunk>chunk</chunk>
Step 3 → छोटे, सस्ते LLM से कहो: "इस chunk को document में situate करने वाले 1-2 वाक्य लिखो"
Step 4 → Contextualised chunk = context वाक्य + original chunk
Step 5 → Contextualised chunk embed करो
Step 6 → BM25 / keyword index में भी डालो
Step 7 → Query पर: vector + BM25, merge, फिर optional rerank
Step 8 → Prompt caching से पूरे document का पैसा सिर्फ एक बार लगता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A chunk from a ruling says: "The goods are classified under 8517.13.00 because the modem function is principal." Alone, nothing says which goods. The generated context: "From Customs Ruling 2025-114 on imported 5G smartphones with foldable displays; this passage states the classification decision." Now a query "classification of foldable smartphone" finds it, and BM25 matches the words "foldable" and "smartphone" even though the original chunk never said them.

**Zomato style**: A review chunk "The portion was too small" gets the context "Review of Biryani House, Koramangala, about the family-size chicken biryani." Searching "Biryani House portion size" now works.

## 🟡 Real Example Hindi mein
**Tariff System**: Ruling के एक chunk में लिखा है: "Goods 8517.13.00 में classified हैं क्योंकि modem function मुख्य है।" अकेले यह नहीं बताता कि कौन से goods। Generated context: "Customs Ruling 2025-114 से, foldable display वाले imported 5G smartphones के बारे में; यह हिस्सा classification का निर्णय बताता है।" अब "foldable smartphone का classification" query मिल जाती है, और BM25 भी "foldable" और "smartphone" शब्द match करता है।

**Zomato**: Review chunk "Portion बहुत छोटा था" को context मिलता है "Biryani House, Koramangala के family-size chicken biryani का review"। अब "Biryani House portion size" search काम करती है।

---

## 💻 Code Example — Basic
```python
# Basic contextual chunking WITHOUT any API: a rule-based "LLM" stands in so this runs offline.
document = (  # title line + body
    "Customs Ruling 2025-114: imported 5G foldable smartphones. "
    "The goods have a modem and a display. "
    "The goods are classified under 8517.13.00 because the modem function is principal."
)  # whole document

chunks = [  # chunks cut from the document (note: no product names in chunk 2)
    "The goods have a modem and a display.",
    "The goods are classified under 8517.13.00 because the modem function is principal.",
]

def fake_llm_context(doc: str, chunk: str) -> str:  # stand-in for the real LLM call
    title = doc.split(".")[0]  # first sentence acts as the title
    return f"From {title}."  # a one-line situating sentence

def contextualise(doc: str, chunk: str) -> str:  # prepend context to the chunk
    return fake_llm_context(doc, chunk) + "\n" + chunk  # context + original

def keyword_score(query: str, text: str) -> int:  # naive keyword matching
    return len(set(query.lower().split()) & set(text.lower().replace(".", " ").split()))  # overlap

query = "classification of foldable smartphones"  # user question
for c in chunks:  # compare plain vs contextual
    print("plain     :", keyword_score(query, c), "|", c[:50])  # misses 'foldable smartphones'
    print("contextual:", keyword_score(query, contextualise(document, c)), "|", c[:50])  # matches
```

## 💻 Code Example — Advanced
```python
# Production: async contextualiser with concurrency limit, retries, fallback and caching.
# The LLM is injected: in production it wraps the Anthropic SDK (messages.create with a cached
# document block) or LangChain's ChatAnthropic. A stub is used here so the file runs offline.
from __future__ import annotations  # modern hints

import asyncio  # async
import hashlib  # cache keys
from dataclasses import dataclass  # container
from typing import Awaitable, Callable  # types

LLM = Callable[[str, str], Awaitable[str]]  # (document, chunk) -> context sentence

PROMPT = (  # Anthropic's published style of prompt
    "<document>\n{doc}\n</document>\nHere is the chunk we want to situate within the whole document\n"
    "<chunk>\n{chunk}\n</chunk>\nPlease give a short succinct context to situate this chunk within the "
    "overall document for the purposes of improving search retrieval of the chunk. "
    "Answer only with the succinct context and nothing else."
)


@dataclass
class CtxChunk:  # output record
    original: str  # raw chunk
    context: str  # generated context
    text: str  # context + original (what you embed and BM25-index)


class Contextualiser:  # the worker
    def __init__(self, llm: LLM, max_concurrency: int = 8, retries: int = 2) -> None:
        self.llm, self.retries = llm, retries  # dependencies
        self.sem = asyncio.Semaphore(max_concurrency)  # limit parallel calls
        self.cache: dict[str, str] = {}  # (doc, chunk) hash -> context

    async def _one(self, doc: str, chunk: str) -> CtxChunk:  # contextualise a single chunk
        key = hashlib.sha256((doc + "\x00" + chunk).encode()).hexdigest()  # stable cache key
        if key in self.cache:  # already generated
            ctx = self.cache[key]  # reuse
        else:  # call the LLM
            ctx = ""  # default = no context
            async with self.sem:  # respect concurrency limit
                for attempt in range(self.retries + 1):  # retry loop
                    try:  # LLM calls can fail
                        ctx = (await self.llm(doc, chunk)).strip()  # generate
                        break  # success
                    except Exception:  # network, rate limit...
                        await asyncio.sleep(0.1 * 2 ** attempt)  # exponential backoff
            self.cache[key] = ctx  # remember (empty string if all attempts failed)
        return CtxChunk(chunk, ctx, f"{ctx}\n{chunk}".strip())  # fall back to plain chunk if no context

    async def run(self, doc: str, chunks: list[str]) -> list[CtxChunk]:  # all chunks of one document
        if not chunks:  # validate
            return []  # nothing to do
        return await asyncio.gather(*(self._one(doc, c) for c in chunks))  # concurrent


async def stub_llm(doc: str, chunk: str) -> str:  # offline stand-in for the real model
    await asyncio.sleep(0)  # pretend I/O
    return "From " + doc.split(".")[0] + "."  # title as context


if __name__ == "__main__":  # demo
    doc = "Customs Ruling 2025-114: 5G foldable smartphones. The goods are classified under 8517.13.00."  # doc
    out = asyncio.run(Contextualiser(stub_llm).run(doc, ["The goods are classified under 8517.13.00."]))  # run
    print(out[0].text)  # context + chunk
    # Real LLM call (sketch, needs ANTHROPIC_API_KEY):
    #   import anthropic; client = anthropic.AsyncAnthropic()
    #   msg = await client.messages.create(model=MODEL, max_tokens=150, messages=[{"role": "user",
    #         "content": [{"type": "text", "text": f"<document>{doc}</document>",
    #                      "cache_control": {"type": "ephemeral"}},   # cache the document part
    #                     {"type": "text", "text": chunk_instruction}]}])
```

---

## 🟠 FastAPI Integration
An ingestion endpoint accepts a document and its chunks, contextualises them in the background, and returns a job id (contextualising a whole PDF can take minutes). Here the work is shown inline for clarity; use `BackgroundTasks` or a queue (Celery/RQ) for real workloads.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel, Field  # pydantic v2

app = FastAPI()  # app
worker = Contextualiser(stub_llm)  # replace stub_llm with a real LLM call


class CtxIn(BaseModel):  # request
    document: str = Field(min_length=1)  # full document text
    chunks: list[str] = Field(min_length=1, max_length=500)  # chunks from your splitter


@app.post("/ingest/contextual")  # route
async def ingest(req: CtxIn) -> dict:  # handler
    if len(req.document) > 400_000:  # very long document will not fit the LLM window
        raise HTTPException(413, "document too long; contextualise per section instead")  # guard
    res = await worker.run(req.document, req.chunks)  # generate contexts
    return {"count": len(res), "failed_context": sum(1 for r in res if not r.context),  # monitor failures
            "sample": res[0].text}  # preview
```

---

## 🔗 LangChain / LangGraph Connection
Contextualisation is a simple LCEL chain: prompt | chat model | string parser, applied with `.abatch` over chunks. Then wrap the result in `Document` objects and feed both a vector store and a BM25 retriever; combine with `EnsembleRetriever`.

```python
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_core.output_parsers import StrOutputParser  # parser
# from langchain_anthropic import ChatAnthropic

prompt = ChatPromptTemplate.from_template(PROMPT)  # same prompt text as above
# llm = ChatAnthropic(model=MODEL, max_tokens=150)  # a small, cheap Claude model
# chain = prompt | llm | StrOutputParser()  # LCEL pipeline
# contexts = await chain.abatch([{"doc": doc, "chunk": c} for c in chunks], config={"max_concurrency": 8})
# docs = [Document(page_content=f"{ctx}\n{c}", metadata={"source": src}) for ctx, c in zip(contexts, chunks)]
# retriever = EnsembleRetriever(retrievers=[bm25_retriever, vector_retriever], weights=[0.4, 0.6])
# LangGraph: nodes split -> contextualise -> index; add a retry edge for failed LLM calls.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Embedding the context only and dropping the chunk (or the reverse)
✅ Correct: Embed and BM25-index `context + chunk` together; return the original chunk text to the LLM if you prefer.

```python
# Wrong - context alone loses the details
text = ctx  # no actual content

# Right
text = f"{ctx}\n{chunk}"  # situating sentence + real content
```

❌ Mistake 2: Re-sending the whole document uncached for every chunk
✅ Correct: Use prompt caching (cache the document block) so you pay full price once, cheap cache-read price for the rest.

❌ Mistake 3: Using only vector search after contextualising.
✅ Correct: Also index the contextual text in BM25; exact terms (HS codes, names) gain a lot.

---

## 🧠 Tricky Interview Question
**Q**: "Contextual chunking improved retrieval, but your ingestion bill for 10,000 documents is huge. How do you cut it without losing the benefit?"

**Answer**: The cost comes from sending the full document with each chunk (documents x chunks x doc tokens). Options: (1) prompt caching - mark the document block as cacheable so chunk 2..N read it at a fraction of the price; (2) a small cheap model for context generation; (3) limit the context to 50-100 output tokens; (4) pass only the relevant section (not the whole document) for very long documents; (5) skip contextualising atomic chunks (FAQ) that are already self-contained; (6) content-hash cache so unchanged chunks are never regenerated; (7) use the Batch API for non-urgent ingestion (discounted).

---

## ⚫ Interview Questions + Answers

Q1: What problem does contextual chunking solve?
A1: Chunks lose the document context after splitting. Prepending an LLM-written context sentence restores it for both embeddings and BM25.

Q2: What exactly do you embed?
A2: The contextual text: generated context sentence plus the original chunk.

Q3: Why add contextual BM25 too?
A3: BM25 matches exact words (product names, HS codes). The context adds those words to chunks that lacked them, so keyword search benefits too.

Q4: How do you control the cost?
A4: Prompt caching of the document, a small model, short outputs, batch processing, and caching generated contexts by content hash.

Q5: (Hard) What are the failure modes?
A5: Hallucinated context (wrong facts get baked into the index - hard to detect), cost scaling with document length, stale context after document edits, and prompt-injection text in documents influencing the context. Mitigate with a strict prompt, spot-check evaluations, deterministic regeneration on change, and treating document text as data.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Chunks are ambiguous without their document (rulings, reports, contracts)
- Retrieval quality matters more than ingestion cost
- You can use prompt caching or batch pricing

❌ Avoid when:
- Chunks are self-contained (FAQ entries, product records)
- Documents change every minute (regeneration cost)
- Budget is very small and late chunking or simple heading prefixes are enough

---

## 📊 Visual Diagram
```
 Whole document ─────────────────────────────┐ (cached once)
                                              ▼
 chunk_i ──► [ small LLM: "situate this chunk" ] ──► context_i
                                              │
                      context_i + "\n" + chunk_i
                       │                       │
                       ▼                       ▼
              embedding model            BM25 index
                       │                       │
                       └──── query ──► merge (rank fusion) ──► rerank ──► top-k ──► LLM
```

---

## 💰 Cost Impact
- Per chunk call input = document tokens + chunk tokens; output about 50-100 tokens. A 20,000-token document with 100 chunks uncached = about 2M input tokens (about $0.30 at $0.15 per 1M with a small model, more with larger ones).
- With prompt caching, repeated document tokens are read at a reduced rate (Anthropic documents cache reads at a small fraction of the base input price), so the same job costs several times less. Check the current pricing page for exact numbers.
- Output: 100 chunks x 80 tokens = 8,000 output tokens - negligible.
- Optimise: caching, small model, batch API, content-hash cache, skip atomic chunks, contextualise only on ingest (never at query time).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Contextual Retrieval | Anthropic's method of adding chunk context | Chunk में context जोड़ने की Anthropic की विधि |
| Context sentence | LLM-written situating text | LLM का लिखा संदर्भ वाक्य |
| Contextual BM25 | Keyword index on context+chunk | Context सहित keyword index |
| Prompt caching | Reuse repeated prompt prefix cheaply | दोहराए prompt part को सस्ते में reuse |
| Rank fusion | Merge ranked lists | Ranked lists मिलाना |
| Reranker | Re-scores top results | Top results का दोबारा scoring |

---

## ⚡ 3-Line Summary
English: Contextual chunking asks an LLM to write a short situating sentence for each chunk, then embeds and BM25-indexes context plus chunk. It fixes lost context and improves both vector and keyword retrieval. Use prompt caching and a small model to keep ingestion cost low.
Hindi: Contextual chunking में LLM हर chunk के लिए छोटा संदर्भ वाक्य लिखता है, फिर context + chunk को embed और BM25 index किया जाता है। इससे खोया context लौटता है और vector व keyword दोनों retrieval सुधरते हैं। Prompt caching और छोटे model से ingestion cost कम रखो।

---

## ➡️ Next Topic
**174. Agentic Chunking** - let an LLM decide where the chunk boundaries should be.
