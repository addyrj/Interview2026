---

# 184. Naive RAG
# हिंदी में: Naive RAG (सबसे सरल RAG)

---

## 🔵 Simple Definition (English)
Naive RAG is the first, simplest recipe: split documents into fixed-size chunks, embed them, store them, then for each question embed the question, take the top-k most similar chunks, paste them into a prompt and ask the LLM. No query rewriting, no reranking, no filters, no checks. It is the right place to start and the baseline to beat.

## 🔵 सरल परिभाषा (Hindi)
Naive RAG सबसे पहला, सबसे सरल तरीका है: documents को fixed-size chunks में बाँटो, embed करो, store करो; फिर हर सवाल को embed करो, सबसे मिलते-जुलते top-k chunks लो, उन्हें prompt में चिपकाओ और LLM से पूछो। कोई query rewriting, reranking, filter या जाँच नहीं। शुरुआत के लिए यही सही है और यही वह baseline है जिसे हराना है।

---

## 🔴 Problem it Solves
- It gets a working "chat with your documents" system in a day.
- It gives you a baseline score to measure every later improvement (hybrid search, reranking, better chunking).
- Its failures are very educational: they show exactly why advanced RAG exists.

## 🔴 यह क्यों बना? (Hindi)
- एक दिन में "documents से chat" वाला चलता हुआ system मिल जाता है।
- हर बाद के सुधार (hybrid search, reranking, बेहतर chunking) को नापने के लिए baseline score मिलता है।
- इसकी failures बहुत सिखाती हैं: वे बताती हैं कि advanced RAG क्यों बना।

---

## 🟢 How it Works — Step by Step

```
INDEXING (once)
Step 1 → Load documents -> plain text
Step 2 → Split into fixed-size chunks (e.g. 500 tokens, 50 overlap)
Step 3 → Embed every chunk with one embedding model
Step 4 → Store vectors + chunk text in a vector DB

QUERYING (every question)
Step 5 → Embed the question with the SAME embedding model
Step 6 → Vector search: top-k nearest chunks (k = 3-5)
Step 7 → Prompt = instruction + chunks + question  ("stuffing")
Step 8 → LLM generates the answer; return it (sometimes with sources)

KNOWN WEAKNESSES
Step 9 → Wrong chunks (semantic miss, exact codes), no filters, no reranking
Step 10 → Noisy context, lost in the middle, no refusal, no evaluation
```

## 🟢 कैसे काम करता है? (Hindi)
```
INDEXING (एक बार)
Step 1 → Documents load -> plain text
Step 2 → Fixed-size chunks में split (जैसे 500 tokens, 50 overlap)
Step 3 → हर chunk को एक embedding model से embed करो
Step 4 → Vectors + chunk text vector DB में store करो

QUERYING (हर सवाल पर)
Step 5 → सवाल को उसी embedding model से embed करो
Step 6 → Vector search: top-k नज़दीकी chunks (k = 3-5)
Step 7 → Prompt = instruction + chunks + question ("stuffing")
Step 8 → LLM जवाब बनाता है; लौटाओ

ज्ञात कमज़ोरियाँ
Step 9 → गलत chunks (semantic miss, exact codes), filter नहीं, reranking नहीं
Step 10 → Noisy context, lost in the middle, refusal नहीं, evaluation नहीं
```

---

## 🟡 Real World Example
**Tariff Classification System**: A first prototype indexes the tariff PDF with 1000-character chunks and top_k=3.
- Works: "What is the duty on smartphones?" -> retrieves the 8517 passage -> correct.
- Fails 1: "Duty on 8517.13.00 in 2023?" -> embeddings treat codes as fuzzy; retrieves 8517.18 and the 2025 rate.
- Fails 2: "Duty on foldable phones, and are there exemptions?" -> exemption is in another chunk; answer incomplete.
- Fails 3: "What is the weather?" -> still retrieves 3 chunks and the LLM may produce a confident but irrelevant answer.
These failures become the roadmap: metadata filters, hybrid search, parent-child chunks, refusal threshold.

**Zomato style**: "Chat with menu" prototype: works for dish questions, fails for "cheapest vegetarian dish under 200" (needs structured filtering, not similarity).

## 🟡 Real Example Hindi mein
**Tariff System**: पहला prototype tariff PDF को 1000-character chunks और top_k=3 से index करता है।
- चलता है: "Smartphones की duty?" -> 8517 वाला passage -> सही।
- Fail 1: "2023 में 8517.13.00 की duty?" -> embeddings codes को धुंधला समझते हैं; 8517.18 और 2025 की rate मिलती है।
- Fail 2: "Foldable phones की duty और क्या exemptions हैं?" -> exemption दूसरे chunk में है; जवाब अधूरा।
- Fail 3: "मौसम कैसा है?" -> फिर भी 3 chunks मिलते हैं और LLM आत्मविश्वास से असंबंधित जवाब दे सकता है।
ये failures ही roadmap बनती हैं: metadata filters, hybrid search, parent-child chunks, refusal threshold।

**Zomato**: "Menu से chat" prototype dish questions पर चलता है, "200 से कम सबसे सस्ता veg dish" पर फेल (similarity नहीं, structured filter चाहिए)।

---

## 💻 Code Example — Basic
```python
# Basic naive RAG in pure Python: fixed-size chunks, word-overlap retrieval, prompt stuffing, fake LLM.
import re  # tokenizer

DOC = ("Smartphones under heading 8517 attract ten percent duty. Cordless phones under heading 8517 attract twelve percent duty. "
       "Refurbished smartphones are exempt from the ten percent rate and attract five percent duty. "
       "Lithium batteries under heading 8507 attract twenty percent duty.")  # one tiny document

def fixed_chunks(text: str, size: int = 12) -> list[str]:  # step 2: fixed-size word chunks, NO structure awareness
    w = text.split()  # words
    return [" ".join(w[i:i + size]) for i in range(0, len(w), size)]  # slices

CHUNKS = fixed_chunks(DOC)  # step 3-4 (our "vector store" is just a list)

def words(t: str) -> set[str]:  # tokenizer
    return set(re.findall(r"[a-z0-9]+", t.lower()))  # words

def top_k(q: str, k: int = 2) -> list[str]:  # steps 5-6: retrieve by overlap (stand-in for vectors)
    return sorted(CHUNKS, key=lambda c: -len(words(q) & words(c)))[:k]  # best chunks

def prompt(q: str, ctx: list[str]) -> str:  # step 7: stuffing
    return "Answer from the context only.\n" + "\n".join(f"- {c}" for c in ctx) + f"\nQuestion: {q}"  # prompt text

def fake_llm(p: str) -> str:  # step 8: stand-in LLM returns the first context line
    return p.splitlines()[1][2:]  # first context chunk

for q in ["duty on smartphones", "weather today in Delhi"]:  # one good, one out-of-scope question
    ctx = top_k(q)  # retrieve (always returns something!)
    print(q, "->", fake_llm(prompt(q, ctx)))  # naive RAG answers even the out-of-scope question
```

## 💻 Code Example — Advanced
```python
# Production-minded NAIVE RAG: async, typed, with error handling and token accounting.
# Embedding and LLM clients are injected. A deterministic offline implementation is included;
# a real OpenAI (openai>=1) implementation is shown in comments.
from __future__ import annotations  # modern hints

import asyncio  # async
import math  # cosine
from dataclasses import dataclass  # container
from typing import Awaitable, Callable  # types

Embed = Callable[[list[str]], Awaitable[list[list[float]]]]  # texts -> vectors
Generate = Callable[[str], Awaitable[str]]  # prompt -> answer


@dataclass
class NaiveRag:  # the whole naive system
    embed: Embed  # embedding function
    generate: Generate  # LLM function
    chunk_size: int = 80  # words per chunk (use tokens in production)
    overlap: int = 10  # words of overlap
    k: int = 3  # top-k
    chunks: list[str] | None = None  # stored chunk texts
    vectors: list[list[float]] | None = None  # stored vectors

    async def index(self, docs: list[str]) -> int:  # indexing pipeline
        if not docs:  # validate
            raise ValueError("no documents")  # error
        if not 0 <= self.overlap < self.chunk_size:  # validate settings
            raise ValueError("bad overlap")  # error
        chunks: list[str] = []  # collected chunks
        step = self.chunk_size - self.overlap  # window step
        for d in docs:  # each document
            w = d.split()  # words
            chunks += [" ".join(w[i:i + self.chunk_size]) for i in range(0, max(1, len(w)), step)]  # fixed windows
        try:  # embedding call can fail
            self.vectors = await self.embed(chunks)  # embed all chunks (batched in production)
        except Exception as exc:  # wrap
            raise RuntimeError("embedding failed while indexing") from exc  # message
        self.chunks = chunks  # store text
        return len(chunks)  # count

    @staticmethod
    def _cos(a: list[float], b: list[float]) -> float:  # cosine similarity
        d = sum(x * y for x, y in zip(a, b))  # dot
        n = (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))) or 1.0  # norms
        return d / n  # similarity

    async def ask(self, question: str) -> dict:  # query pipeline
        if self.chunks is None or self.vectors is None:  # not indexed
            raise RuntimeError("call index() first")  # error
        try:  # embed question with the SAME model
            qv = (await self.embed([question]))[0]  # vector
        except Exception as exc:  # wrap
            raise RuntimeError("embedding failed for the question") from exc  # message
        order = sorted(range(len(self.chunks)), key=lambda i: -self._cos(qv, self.vectors[i]))[:self.k]  # top-k
        ctx = "\n\n".join(self.chunks[i] for i in order)  # stuff context (no rerank, no filter)
        prompt = f"Use the context to answer.\n\nContext:\n{ctx}\n\nQuestion: {question}\nAnswer:"  # prompt
        try:  # generation can fail
            answer = await self.generate(prompt)  # LLM call
        except Exception as exc:  # wrap
            raise RuntimeError("generation failed") from exc  # message
        return {"answer": answer, "chunk_ids": order, "approx_prompt_tokens": int(len(prompt.split()) * 1.3)}


async def toy_embed(texts: list[str]) -> list[list[float]]:  # offline embedder (letter counts)
    await asyncio.sleep(0)  # async placeholder
    return [[t.lower().count(c) for c in "abcdefghijklmnopqrstuvwxyz"] for t in texts]  # vectors


async def toy_generate(prompt: str) -> str:  # offline "LLM"
    await asyncio.sleep(0)  # async placeholder
    return "(demo answer) " + prompt.split("Context:\n")[1][:60]  # echo start of context


# Real clients (needs OPENAI_API_KEY), same signatures:
#   from openai import AsyncOpenAI; client = AsyncOpenAI()
#   async def embed(texts): r = await client.embeddings.create(model="text-embedding-3-small", input=texts); return [d.embedding for d in r.data]
#   async def generate(p): r = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": p}], temperature=0); return r.choices[0].message.content or ""

if __name__ == "__main__":  # demo
    async def main() -> None:  # async main
        rag = NaiveRag(toy_embed, toy_generate, chunk_size=12, overlap=2, k=2)  # naive system
        n = await rag.index(["Smartphones under heading 8517 attract ten percent duty. Lithium batteries under heading 8507 attract twenty percent duty. " * 2])
        print("chunks:", n)  # count
        print(await rag.ask("duty on smartphones"))  # answer
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
A minimal naive-RAG service: build the index at startup (lifespan), answer at `/ask`. Notice what is missing: auth, filters, rate limiting, caching, refusal. Those are the next upgrades.

```python
from contextlib import asynccontextmanager  # lifespan helper
from fastapi import FastAPI, HTTPException  # framework
from pydantic import BaseModel  # pydantic v2

rag = NaiveRag(toy_embed, toy_generate, chunk_size=40, overlap=5, k=3)  # global system (swap in real clients)


@asynccontextmanager
async def lifespan(app: FastAPI):  # run once at startup
    await rag.index(["Smartphones under heading 8517 attract ten percent duty. " * 5])  # load documents
    yield  # app runs here


app = FastAPI(lifespan=lifespan)  # app with startup hook


class AskIn(BaseModel):  # request
    question: str  # user question


@app.post("/ask")  # route
async def ask(req: AskIn) -> dict:  # handler
    try:  # map errors
        return await rag.ask(req.question)  # naive RAG answer + chunk ids + token estimate
    except RuntimeError as exc:  # upstream problems
        raise HTTPException(502, str(exc))  # bad gateway
```

---

## 🔗 LangChain / LangGraph Connection
The classic LangChain tutorial is exactly naive RAG: loader -> splitter -> embeddings -> vector store -> retriever -> prompt -> model, composed with LCEL. LangGraph turns it into a 2-node graph (`retrieve`, `generate`) that you can later extend with grading, rewriting and retries (Corrective / Adaptive RAG).

```python
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_core.output_parsers import StrOutputParser  # parser
from langchain_core.runnables import RunnablePassthrough  # passthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter  # splitter

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)  # indexing: split
# vectorstore = Chroma.from_documents(splitter.split_documents(docs), OpenAIEmbeddings())  # embed + store
# retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # top-k
prompt = ChatPromptTemplate.from_template("Answer from the context.\n{context}\nQuestion: {question}")  # prompt
# chain = {"context": retriever | (lambda ds: "\n\n".join(d.page_content for d in ds)),
#          "question": RunnablePassthrough()} | prompt | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
# LangGraph version: START -> retrieve -> generate -> END (state: question, docs, answer)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using different embedding models for indexing and querying
✅ Correct: Use the same model (and same normalisation) for both.

```python
# Wrong - vectors live in different spaces; similarity is meaningless
index_vecs = embed_model_a(chunks)  # index with A
query_vec = embed_model_b(question)  # query with B

# Right
index_vecs = embed_model_a(chunks)  # index with A
query_vec = embed_model_a(question)  # query with A
```

❌ Mistake 2: Shipping naive RAG without any evaluation
✅ Correct: Build a golden set first; naive RAG is the baseline you must beat with numbers.

❌ Mistake 3: Always answering, even with irrelevant chunks
✅ Correct: Add a similarity threshold and an "I don't know" path (next topics).

❌ Mistake 4: Stuffing too many chunks (top_k=20) hoping for recall
✅ Correct: Retrieve many, rerank, and send few.

---

## 🧠 Tricky Interview Question
**Q**: "You built naive RAG, it demos well, and in production 30% of answers are wrong. Without changing the LLM, name the top improvements in the order you would try them."

**Answer**: First measure: build a golden set and log retrieved chunks to classify failures. Then, cheapest and highest impact first: (1) fix ingestion quality (clean text, better chunking by structure, heading prefixes); (2) metadata filters (date, product area) and hybrid search (BM25 + vectors) for exact identifiers; (3) reranking top-20 to top-4; (4) query rewriting/expansion for vague questions; (5) a relevance threshold and refusal path; (6) parent-child or neighbour expansion for incomplete answers; (7) prompt hardening with citations and output validation. Re-run the golden set after each change so every gain is proven.

---

## ⚫ Interview Questions + Answers

Q1: What does naive RAG consist of?
A1: Fixed-size chunking, embedding, vector top-k retrieval, prompt stuffing and one LLM call.

Q2: Why is it called naive?
A2: It assumes the top-k vector hits are exactly what the LLM needs: no query processing, reranking, filtering, or verification.

Q3: Name three common failure modes.
A3: Missed retrieval (exact codes/semantic gaps), incomplete context (answer split across chunks), and hallucination when retrieved context is irrelevant.

Q4: Why must query and document embeddings use the same model?
A4: Embedding models define their own vector spaces; similarity between vectors from different models is meaningless.

Q5: (Hard) How do you prove an upgrade (for example reranking) is worth its added cost?
A5: Run the golden set before and after, compare recall@k, answer correctness, faithfulness, latency and cost per query. Adopt the change if the quality gain justifies the extra latency/tokens, and keep the baseline as a regression reference.

---

## 🔷 When to Use + When Not to Use
✅ Use naive RAG when:
- Building a first prototype or baseline
- Small, clean, homogeneous corpus; low risk of wrong answers

❌ Avoid shipping it as-is when:
- Answers are high stakes (legal, tariff, medical)
- Corpus is large, versioned or full of identifiers/tables
- You need citations, access control, or reliability guarantees

---

## 📊 Visual Diagram
```
 INDEX:  docs ─► fixed chunks ─► embed ─► vector DB

 QUERY:  question ─► embed ─► top-k nearest chunks ─► [ prompt stuffing ] ─► LLM ─► answer
                                  ▲                                            
                                  └── no rewrite · no filters · no rerank · no threshold · no eval

 failure map:  wrong chunk ─► fix: hybrid / filters / rerank
               half answer ─► fix: parent-child / bigger context
               off-topic   ─► fix: threshold + refusal
```

---

## 💰 Cost Impact
- Indexing: corpus tokens x embedding price (one time). Example: 20M tokens x $0.02/1M = $0.40.
- Per query: question embedding (negligible) + LLM input = top_k x chunk_tokens + instructions. Example: 3 x 500 + 100 = 1,600 tokens + 200 output; at $0.15/$0.60 per 1M = about $0.00036 per query, or about $36/day at 100K queries.
- Waste in naive RAG: it always calls the LLM, even when retrieval found nothing useful, and chunks may be noisy.
- Optimise: relevance threshold with refusal (skip LLM), smaller chunks + rerank + lower top_k, semantic caching for repeated questions, small model for simple queries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Naive RAG | Basic retrieve-and-stuff RAG | सबसे सरल RAG |
| Prompt stuffing | Paste all chunks into prompt | सारे chunks prompt में डालना |
| top-k | Number of retrieved chunks | लाए गए chunks की संख्या |
| Baseline | Starting score to beat | तुलना के लिए शुरुआती score |
| Golden set | Labelled eval questions | जाँच के लिए सही प्रश्न-उत्तर |
| Refusal | Saying "I don't know" | "पता नहीं" कहना |

---

## ⚡ 3-Line Summary
English: Naive RAG = fixed chunks, embeddings, top-k retrieval, stuff into prompt, generate. It is the right baseline but fails on exact identifiers, split answers and out-of-scope questions. Evaluate it, then add filters, hybrid search, reranking and refusal one by one.
Hindi: Naive RAG = fixed chunks, embeddings, top-k retrieval, prompt में डालो, generate करो। यह सही baseline है पर exact identifiers, बँटे जवाबों और scope से बाहर के सवालों पर फेल होता है। इसे evaluate करो, फिर filters, hybrid search, reranking और refusal एक-एक करके जोड़ो।

---

## ➡️ Next Topic
**185. Advanced RAG (pre-retrieval and post-retrieval improvements)** - query rewriting, hybrid search, reranking and context compression on top of naive RAG.
