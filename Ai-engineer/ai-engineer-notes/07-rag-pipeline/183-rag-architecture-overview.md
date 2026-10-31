---

# 183. RAG Architecture Overview
# हिंदी में: RAG Architecture का पूरा चित्र

---

## 🔵 Simple Definition (English)
A RAG system has two pipelines. The offline ingestion pipeline loads, cleans, chunks, embeds and stores documents. The online query pipeline takes a question, retrieves relevant chunks, builds a prompt, calls the LLM and returns a cited answer. Around them sit evaluation, monitoring, caching and security. Knowing each box tells you where a failure comes from.

## 🔵 सरल परिभाषा (Hindi)
RAG system में दो pipelines होती हैं। Offline ingestion pipeline documents को load, clean, chunk, embed और store करती है। Online query pipeline सवाल लेकर relevant chunks खोजती है, prompt बनाती है, LLM call करती है और citations के साथ जवाब लौटाती है। इनके चारों ओर evaluation, monitoring, caching और security रहती है। हर box जानने से पता चलता है कि failure कहाँ से आई।

---

## 🔴 Problem it Solves
- Beginners see RAG as one function `ask(question)` and cannot debug it: is the bad answer from extraction, chunking, embedding, retrieval, prompt or the LLM?
- Without a clear architecture, ingestion code and serving code get mixed, and scaling or updating becomes painful.
- A shared map lets teams split work (data, retrieval, serving, evaluation) and place metrics at each stage.

## 🔴 यह क्यों बना? (Hindi)
- Beginners RAG को एक function `ask(question)` समझते हैं और debug नहीं कर पाते: खराब जवाब extraction, chunking, embedding, retrieval, prompt या LLM में से कहाँ से आया?
- साफ architecture के बिना ingestion और serving code मिल जाता है, scaling और updates कठिन हो जाते हैं।
- साझा नक्शे से teams काम बाँट सकती हैं और हर stage पर metrics रख सकती हैं।

---

## 🟢 How it Works — Step by Step

```
OFFLINE (ingestion, runs when documents change)
Step 1 → Load: PDFs, HTML, DB rows, APIs  -> raw text + source info
Step 2 → Clean: remove boilerplate, fix encoding, OCR if scanned
Step 3 → Chunk: structure-aware splitting + overlap + metadata
Step 4 → Embed: embedding model turns each chunk into a vector
Step 5 → Store: vector DB (+ keyword index, + docstore for parents)

ONLINE (per question)
Step 6 → Understand query: rewrite, expand, extract filters (date, chapter)
Step 7 → Retrieve: vector + keyword (hybrid), metadata filters -> top-N candidates
Step 8 → Rerank: cross-encoder/LLM reorders; keep top-k (3-5)
Step 9 → Build prompt: system rules + chunks (with ids) + question
Step 10 → Generate: LLM answers only from context, cites chunk ids
Step 11 → Post-process: validate citations/JSON, refuse if no evidence
Step 12 → Return answer + sources; log everything for evaluation
```

## 🟢 कैसे काम करता है? (Hindi)
```
OFFLINE (documents बदलने पर)
Step 1 → Load: PDF, HTML, DB rows, APIs -> raw text + source
Step 2 → Clean: boilerplate हटाओ, encoding ठीक करो, scanned हो तो OCR
Step 3 → Chunk: structure-aware split + overlap + metadata
Step 4 → Embed: embedding model हर chunk को vector बनाता है
Step 5 → Store: vector DB (+ keyword index, + parents के लिए docstore)

ONLINE (हर सवाल पर)
Step 6 → Query समझो: rewrite, expand, filters निकालो (date, chapter)
Step 7 → Retrieve: vector + keyword (hybrid), metadata filters -> top-N
Step 8 → Rerank: cross-encoder/LLM क्रम बदलता है; top-k (3-5) रखो
Step 9 → Prompt बनाओ: system rules + chunks (ids सहित) + question
Step 10 → Generate: LLM सिर्फ context से जवाब देता है, chunk ids cite करता है
Step 11 → Post-process: citations/JSON validate, evidence न हो तो मना करो
Step 12 → जवाब + sources लौटाओ; evaluation के लिए सब log करो
```

---

## 🟡 Real World Example
**Tariff Classification System**:
- Ingestion: nightly job loads the new tariff HTML/PDF, chunks per tariff line with breadcrumbs, embeds, upserts by stable id.
- Query: "Duty on foldable 5G phone shipped 2025-06-01?" -> filters {date: 2025-06-01} -> hybrid retrieval -> rerank -> prompt with 4 chunks -> LLM answers `{"hs_code": "8517.13.00", "duty": "10%", "sources": ["c17", "c18"]}`.
- Monitoring: logs question, chunk ids, tokens, latency, user feedback; a golden set runs nightly.

**Amazon / Zomato style**: Help-bot: ingestion of policy pages, query path with city/locale filters, guardrail refusing when no chunk has a score above a threshold.

## 🟡 Real Example Hindi mein
**Tariff System**:
- Ingestion: रात में नया tariff HTML/PDF load, हर tariff line का breadcrumb सहित chunk, embed, stable id से upsert।
- Query: "2025-06-01 को भेजे foldable 5G phone की duty?" -> filter {date} -> hybrid retrieval -> rerank -> 4 chunks वाला prompt -> LLM `{"hs_code": ..., "duty": ..., "sources": [...]}` देता है।
- Monitoring: सवाल, chunk ids, tokens, latency, feedback log; golden set रोज़ रात चलता है।

**Amazon / Zomato**: Help-bot में policy pages की ingestion, city/locale filters वाला query path, और जब कोई chunk threshold से ऊपर न हो तो मना करने वाला guardrail।

---

## 💻 Code Example — Basic
```python
# Basic end-to-end RAG in ~40 lines of pure Python (word-overlap retrieval, fake LLM) so it runs offline.
import re  # tokenizer

DOCS = {  # source documents
    "tariff_2025.pdf": "Smartphones under heading 8517 attract ten percent duty. Cordless phones attract twelve percent duty.",
    "tariff_2025_b.pdf": "Lithium batteries under heading 8507 attract twenty percent duty.",
}

def chunk(text: str) -> list[str]:  # ingestion: one chunk per sentence
    return [s.strip() + "." for s in text.split(".") if s.strip()]  # sentences

INDEX: list[tuple[str, str]] = [(src, c) for src, t in DOCS.items() for c in chunk(t)]  # (source, chunk)

def words(t: str) -> set[str]:  # tokenizer
    return set(re.findall(r"[a-z0-9]+", t.lower()))  # words

def retrieve(q: str, k: int = 2) -> list[tuple[str, str]]:  # query: top-k by word overlap
    return sorted(INDEX, key=lambda x: -len(words(q) & words(x[1])))[:k]  # best chunks

def build_prompt(q: str, hits: list[tuple[str, str]]) -> str:  # prompt assembly
    ctx = "\n".join(f"[{i + 1}] ({s}) {c}" for i, (s, c) in enumerate(hits))  # numbered context
    return f"Answer only from the context and cite [n].\nContext:\n{ctx}\nQuestion: {q}"  # final prompt

def fake_llm(prompt: str) -> str:  # stand-in for a real model call
    first = prompt.split("Context:\n")[1].splitlines()[0]  # take the top chunk
    return f"{first.split(') ', 1)[1]} [1]"  # "answer" = top chunk + citation

q = "duty on smartphones"  # question
hits = retrieve(q)  # retrieval
print(fake_llm(build_prompt(q, hits)))  # answer with citation
print("sources:", [s for s, _ in hits])  # citations
```

## 💻 Code Example — Advanced
```python
# Production-style modular RAG: Protocol interfaces, async stages, timing, errors, refusal guard.
from __future__ import annotations  # modern hints

import asyncio  # async
import time  # timing
from dataclasses import dataclass, field  # containers
from typing import Protocol  # interfaces


@dataclass
class Hit:  # retrieved chunk
    id: str  # chunk id
    text: str  # chunk text
    score: float  # retrieval score
    source: str  # citation source


class Retriever(Protocol):  # any retriever with this method works
    async def retrieve(self, query: str, k: int) -> list[Hit]: ...


class Reranker(Protocol):  # any reranker with this method works
    async def rerank(self, query: str, hits: list[Hit], k: int) -> list[Hit]: ...


class LLM(Protocol):  # any LLM wrapper with this method works
    async def generate(self, prompt: str) -> str: ...


@dataclass
class RagResult:  # response + diagnostics
    answer: str  # final text
    sources: list[str] = field(default_factory=list)  # cited sources
    timings_ms: dict[str, float] = field(default_factory=dict)  # per-stage latency
    refused: bool = False  # True if no evidence


class RagPipeline:  # the online pipeline
    def __init__(self, retriever: Retriever, reranker: Reranker, llm: LLM,
                 n_candidates: int = 20, top_k: int = 4, min_score: float = 0.2) -> None:
        self.retriever, self.reranker, self.llm = retriever, reranker, llm  # components
        self.n_candidates, self.top_k, self.min_score = n_candidates, top_k, min_score  # settings

    @staticmethod
    def build_prompt(q: str, hits: list[Hit]) -> str:  # prompt assembly
        ctx = "\n".join(f"[{h.id}] {h.text}" for h in hits)  # context with ids
        return f"Answer ONLY from the context. Cite chunk ids. If unknown say 'I don't know'.\nContext:\n{ctx}\nQuestion: {q}"

    async def ask(self, question: str) -> RagResult:  # full online flow
        if not question.strip():  # validate
            raise ValueError("empty question")  # error
        t: dict[str, float] = {}  # timings

        t0 = time.perf_counter()  # start retrieval timer
        try:  # retrieval can fail
            cands = await self.retriever.retrieve(question, self.n_candidates)  # step 7
        except Exception as exc:  # wrap
            raise RuntimeError("retrieval failed") from exc  # message
        t["retrieve"] = (time.perf_counter() - t0) * 1000  # ms

        cands = [h for h in cands if h.score >= self.min_score]  # drop weak evidence
        if not cands:  # guard: no evidence -> refuse, do not call the LLM (saves tokens)
            return RagResult("I don't know based on the available documents.", [], t, refused=True)  # refusal

        t0 = time.perf_counter()  # rerank timer
        hits = await self.reranker.rerank(question, cands, self.top_k)  # step 8
        t["rerank"] = (time.perf_counter() - t0) * 1000  # ms

        t0 = time.perf_counter()  # generation timer
        try:  # LLM can fail
            answer = await self.llm.generate(self.build_prompt(question, hits))  # steps 9-10
        except Exception as exc:  # wrap
            raise RuntimeError("generation failed") from exc  # message
        t["generate"] = (time.perf_counter() - t0) * 1000  # ms
        return RagResult(answer, sorted({h.source for h in hits}), t)  # step 12


class KeywordRetriever:  # demo retriever
    def __init__(self, data: list[Hit]) -> None:
        self.data = data  # chunks

    async def retrieve(self, query: str, k: int) -> list[Hit]:  # async retrieve
        qw = set(query.lower().split())  # words
        scored = [Hit(h.id, h.text, len(qw & set(h.text.lower().split())) / max(1, len(qw)), h.source) for h in self.data]
        return sorted(scored, key=lambda h: -h.score)[:k]  # best first


class PassthroughReranker:  # demo reranker (keeps order)
    async def rerank(self, query: str, hits: list[Hit], k: int) -> list[Hit]:
        return hits[:k]  # top-k


class EchoLLM:  # demo LLM
    async def generate(self, prompt: str) -> str:
        return "Answer based on: " + prompt.split("Context:\n")[1].splitlines()[0]  # echo top chunk


if __name__ == "__main__":  # demo
    data = [Hit("c1", "smartphones heading 8517 duty ten percent", 0, "tariff_2025.pdf"),
            Hit("c2", "batteries heading 8507 duty twenty percent", 0, "tariff_2025.pdf")]  # chunks
    rag = RagPipeline(KeywordRetriever(data), PassthroughReranker(), EchoLLM())  # pipeline
    print(asyncio.run(rag.ask("duty on smartphones")))  # answer
    print(asyncio.run(rag.ask("weather in Delhi")).refused)  # no evidence -> True
```

---

## 🟠 FastAPI Integration
Serve the online pipeline; keep ingestion as a separate job (CLI, queue worker or admin endpoint). Return sources and timings so clients and dashboards can use them.

```python
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # pydantic v2

app = FastAPI()  # app
rag = RagPipeline(KeywordRetriever([Hit("c1", "smartphones heading 8517 duty ten percent", 0, "tariff_2025.pdf")]),
                  PassthroughReranker(), EchoLLM())  # build once at startup


class AskIn(BaseModel):  # request
    question: str  # user question


@app.post("/ask")  # route
async def ask(req: AskIn) -> dict:  # handler
    try:  # map errors to HTTP codes
        res = await rag.ask(req.question)  # run pipeline
    except ValueError as exc:  # bad input
        raise HTTPException(422, str(exc))  # client error
    except RuntimeError as exc:  # upstream failure
        raise HTTPException(502, str(exc))  # bad gateway
    return {"answer": res.answer, "sources": res.sources, "refused": res.refused, "timings_ms": res.timings_ms}
```

---

## 🔗 LangChain / LangGraph Connection
Each box maps to a LangChain component: loaders, text splitters, `Embeddings`, vector stores, retrievers, prompt templates, chat models, output parsers. LCEL composes the online path; LangGraph is used when you need branching (query rewrite, retry, refusal, human review).

```python
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_core.output_parsers import StrOutputParser  # parser
from langchain_core.runnables import RunnablePassthrough  # passes the question through

prompt = ChatPromptTemplate.from_template("Answer only from the context.\nContext:\n{context}\nQuestion: {question}")  # prompt
# retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
# llm = ChatOpenAI(model="gpt-4o-mini")
# format_docs = lambda docs: "\n\n".join(d.page_content for d in docs)
# chain = {"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
# answer = await chain.ainvoke("duty on smartphones")
# LangGraph: nodes = rewrite_query -> retrieve -> grade_docs -> (generate | web_fallback | refuse)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blaming the LLM before checking retrieval
✅ Correct: Log retrieved chunks; most bad answers show the right chunk was never retrieved.

```python
# Wrong - only looks at the final answer
print(answer)  # no idea why it is wrong

# Right - log each stage
print("retrieved:", [(h.id, round(h.score, 2)) for h in hits])  # debug retrieval first
```

❌ Mistake 2: Always calling the LLM even when nothing relevant was retrieved
✅ Correct: Score threshold + refusal path (saves tokens, avoids hallucination).

❌ Mistake 3: Mixing ingestion and serving in one process and one deploy
✅ Correct: Separate them; ingestion is batch, serving is latency-sensitive.

---

## 🧠 Tricky Interview Question
**Q**: "Users report that the bot's answers are sometimes wrong, but each component passes its unit tests. How do you find the real problem?"

**Answer**: Component tests do not measure end-to-end quality. Build an evaluation harness: a golden set of questions with gold sources and answers; run the pipeline and compute retrieval metrics (recall@k, MRR) and generation metrics (faithfulness, correctness). Trace failures stage by stage using logged inputs and outputs: was the gold chunk in the candidates? after rerank? did the prompt contain it? did the LLM use it? Classify failures (extraction, chunking, retrieval, ranking, prompt, generation) and fix the biggest bucket first. Add tracing (for example LangSmith or OpenTelemetry) so production failures can be replayed.

---

## ⚫ Interview Questions + Answers

Q1: What are the two pipelines in RAG?
A1: Offline ingestion (load, clean, chunk, embed, store) and online query (retrieve, rerank, prompt, generate).

Q2: Why rerank after retrieval?
A2: Vector search is fast but approximate; a reranker scores query-chunk pairs more accurately, so you can retrieve many candidates cheaply and send only the best few to the LLM.

Q3: Where does hybrid search fit?
A3: In retrieval: combine keyword (BM25) and vector search so exact identifiers (HS codes) and semantic matches both work.

Q4: How do you stop hallucinations in the architecture?
A4: Grounded prompt, citations, relevance threshold with refusal, output validation, and evaluation of faithfulness.

Q5: (Hard) How would you scale this to 10M documents and 100 requests per second?
A5: Shard/partition the vector DB with ANN indexes and metadata filters, cache embeddings and frequent answers, async I/O with connection pooling, batch embedding at ingestion, stream LLM output, rate-limit and retry with backoff, autoscale stateless API pods, separate ingestion workers with queues, and monitor latency, cost per query and quality metrics.

---

## 🔷 When to Use + When Not to Use
✅ Use this architecture when:
- Answers must be grounded in private or changing documents
- You need citations, access control and monitoring

❌ Avoid full RAG when:
- Data is small enough to put directly in the prompt
- Questions need computation over structured data (use SQL/tools instead)

---

## 📊 Visual Diagram
```
 OFFLINE                                                   ONLINE
 ───────                                                   ──────
 sources ► load ► clean ► chunk ► embed ► ┌──────────┐      user question
 (PDF/HTML/DB)               +metadata    │ vector DB │◄──┐       │
                                          │ + BM25    │   │   [query rewrite / filters]
                                          │ + docstore│   │       │
                                          └──────────┘   └── [hybrid retrieve top-20]
                                                                  │
                                                           [rerank → top-4]
                                                                  │
                                                  [prompt: rules + chunks + question]
                                                                  │
                                                              [ LLM ]
                                                                  │
                                              [validate + citations / refuse] ► answer + sources
 cross-cutting: evaluation (golden set) · tracing/logging · caching · auth/tenant filters · cost control
```

---

## 💰 Cost Impact
- Ingestion: one-time embedding cost (corpus tokens x embedding price) plus OCR if needed; re-embed only changed chunks.
- Per query: query embedding (tiny) + reranker (small model/API) + LLM input (top_k x chunk tokens + prompt) + output. Example: 4 x 400 + 300 = 1,900 input tokens, 250 output tokens at $0.15/$0.60 per 1M = about $0.00044 per query; 100K queries/day = about $44/day.
- Optimise: refusal path skips the LLM; semantic cache; smaller top_k after reranking; small model for simple questions; prompt caching for stable system prompts; compress context; batch ingestion.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ingestion | Load, chunk, embed, store | Documents को index बनाना |
| Retriever | Finds relevant chunks | Relevant chunks खोजने वाला |
| Reranker | Re-scores candidates | Candidates का दोबारा scoring |
| Grounding | Answer based on sources | जवाब का source पर आधारित होना |
| Hybrid search | Keyword + vector | Keyword + vector search |
| Tracing | Record each stage | हर stage का record |

---

## ⚡ 3-Line Summary
English: RAG has an offline ingestion pipeline and an online query pipeline: retrieve, rerank, prompt, generate, validate. Debug stage by stage with logs and a golden set. Add refusal, caching and monitoring for production.
Hindi: RAG में offline ingestion pipeline और online query pipeline होती हैं: retrieve, rerank, prompt, generate, validate। Logs और golden set से stage-by-stage debug करो। Production के लिए refusal, caching और monitoring जोड़ो।

---

## ➡️ Next Topic
**184. Naive RAG** - the simplest version (retrieve top-k, stuff into prompt) and its known weaknesses.
