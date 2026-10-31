---

# 076. Context Stuffing
# हिंदी में: Context Stuffing — Prompt में सब कुछ ठूँस देना

---

## 🔵 Simple Definition (English)
Context stuffing means putting as much text as possible into the prompt (whole documents, many retrieved chunks, long chat history) and hoping the model will find what it needs. Long-context models make it easy, but it raises cost and latency and can lower accuracy.

## 🔵 सरल परिभाषा (Hindi)
Context stuffing का मतलब है prompt में जितना हो सके उतना text भर देना (पूरे documents, बहुत सारे retrieved chunks, लंबी chat history) और उम्मीद करना कि model ज़रूरी चीज़ ढूँढ लेगा। Long-context models इसे आसान बनाते हैं, पर cost और latency बढ़ती है और accuracy घट भी सकती है।

---

## 🔴 Problem it Solves
Stuffing exists because it is the simplest approach: no retrieval pipeline, no chunking, just paste everything. It works for small corpora (a 30-page contract) and prototypes.

The problem it creates: (1) you pay for every token on every call, (2) latency grows, (3) irrelevant text distracts the model, (4) important facts get lost in the middle (topic 077), (5) it can exceed the context limit.

## 🔴 यह क्यों बना? (Hindi)
Stuffing इसलिए है क्योंकि यह सबसे सरल तरीका है: retrieval pipeline नहीं, chunking नहीं, बस सब paste कर दो। छोटे corpora (30 पन्नों के contract) और prototypes में यह चलता है। इससे होने वाली दिक्कतें: (1) हर call पर हर token का पैसा, (2) latency बढ़ती है, (3) बेकार text model को भटकाता है, (4) ज़रूरी facts बीच में खो जाते हैं (topic 077), (5) context limit पार हो सकती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect all possibly-relevant text (docs, history, notes)
Step 2 → Concatenate into one big prompt
Step 3 → Add the question at the end
Step 4 → Send; model attends over every token
Step 5 → Cost = all tokens x price; latency grows with length
Step 6 → Quality may drop if the answer is buried or the prompt is noisy

Better alternatives:
  RAG (retrieve top-k), reranking, summarising, context caching, long-context only when needed
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → संभावित रूप से काम का सारा text इकट्ठा करो (docs, history, notes)
Step 2 → सबको जोड़कर एक बड़ा prompt बनाओ
Step 3 → आख़िर में सवाल जोड़ो
Step 4 → भेजो; model हर token पर attention करता है
Step 5 → Cost = सारे tokens x price; length के साथ latency बढ़ती है
Step 6 → जवाब दबा हो या prompt noisy हो तो quality गिर सकती है

बेहतर विकल्प:
  RAG (top-k retrieve), reranking, summarise, context caching, long-context सिर्फ ज़रूरत पर
```

---

## 🟡 Real World Example
**Tariff Classification System**: The full tariff schedule is 1.5M tokens, which cannot fit in any prompt. Early prototype: paste Chapter 85 (electronics, ~120K tokens) for every question. It works, but each query costs about $0.02 to $0.30 depending on the model, answers take 10+ seconds and accuracy on rare headings is mediocre. Production: retrieve the 5 most relevant heading texts (~2K tokens), cutting cost by roughly 98% and improving accuracy.

**Zomato-style**: Pasting the entire menu of 500 dishes to answer "is there a vegan dessert?" instead of filtering the menu first.

## 🟡 Real Example Hindi mein
**Tariff System**: पूरा tariff schedule 1.5M tokens का है, जो किसी भी prompt में नहीं समाता। शुरुआती prototype: हर सवाल के लिए Chapter 85 (electronics, ~120K tokens) paste करना। चलता है, पर हर query की cost model के हिसाब से लगभग $0.02 से $0.30, जवाब 10+ सेकंड में, और rare headings पर accuracy औसत। Production: सबसे relevant 5 heading texts (~2K tokens) retrieve करो; cost लगभग 98% कम और accuracy बेहतर।

**Zomato-style**: "कोई vegan dessert है?" के लिए 500 dishes का पूरा menu paste करना, बजाय पहले menu filter करने के।

---

## 💻 Code Example — Basic
```python
# Basic: compare stuffing vs selecting relevant chunks (offline, rough token math)

DOCS = {                                              # pretend tariff knowledge base
    "8518": "Heading 8518: microphones, loudspeakers, headphones, earphones. " * 40,
    "8517": "Heading 8517: telephone sets, smartphones, network apparatus. " * 40,
    "3926": "Heading 3926: other articles of plastics, including phone cases. " * 40,
    "0901": "Heading 0901: coffee, whether or not roasted. " * 40,
}

def tokens(text: str) -> int:
    return len(text) // 4                              # rough: 4 characters per token

def stuffed_prompt(question: str) -> str:
    return "\n".join(DOCS.values()) + f"\nQ: {question}"        # everything, always

def selected_prompt(question: str, k: int = 1) -> str:
    words = set(question.lower().split())              # simple keyword "retrieval"
    scored = sorted(DOCS.items(),
                    key=lambda kv: -len(words & set(kv[1].lower().split())))   # overlap score
    return "\n".join(t for _, t in scored[:k]) + f"\nQ: {question}"

q = "which heading covers headphones?"
print("stuffed :", tokens(stuffed_prompt(q)), "tokens")     # large
print("selected:", tokens(selected_prompt(q)), "tokens")    # much smaller
```

## 💻 Code Example — Advanced
```python
# Production: decide between stuffing and retrieval using a token budget, with fallbacks (async)
from __future__ import annotations

import asyncio                                    # async runner
from typing import Awaitable, Callable            # type hints

import tiktoken                                   # exact token counts

ENC = tiktoken.get_encoding("o200k_base")         # gpt-4o family encoding
LLM = Callable[[str], Awaitable[str]]             # prompt -> reply
Retriever = Callable[[str, int], Awaitable[list[str]]]   # (query, k) -> chunks

def count(text: str) -> int:
    return len(ENC.encode(text))                  # exact token count

async def build_context(question: str, full_docs: list[str], retrieve: Retriever,
                        stuff_limit: int = 8_000, k: int = 5) -> tuple[str, str]:
    """Stuff only when the whole corpus is small; otherwise retrieve. Returns (context, mode)."""
    full = "\n\n".join(full_docs)                 # candidate stuffed context
    if count(full) <= stuff_limit:                # small enough: stuffing is fine and simple
        return full, "stuffed"
    try:
        chunks = await retrieve(question, k)      # retrieval path
    except Exception:                             # retriever down: degrade gracefully
        chunks = []
    if not chunks:                                # fallback: head of the corpus within budget
        return ENC.decode(ENC.encode(full)[:stuff_limit]), "truncated-fallback"
    return "\n\n".join(chunks), "retrieved"

async def answer(llm: LLM, question: str, docs: list[str], retrieve: Retriever) -> dict[str, str | int]:
    context, mode = await build_context(question, docs, retrieve)       # choose context
    prompt = f"Answer ONLY from CONTEXT.\nCONTEXT:\n{context}\n\nQ: {question}"
    try:
        reply = await llm(prompt)                 # model call
    except Exception as exc:
        raise RuntimeError(f"LLM failed: {exc}") from exc
    return {"answer": reply, "mode": mode, "prompt_tokens": count(prompt)}   # report cost driver

async def _demo() -> None:
    docs = ["Heading 8518 headphones. " * 2000, "Heading 8517 phones. " * 2000]
    async def retrieve(q: str, k: int) -> list[str]:
        return ["Heading 8518 headphones."]
    async def llm(p: str) -> str:
        return "8518"
    print(await answer(llm, "headphones?", docs, retrieve))

if __name__ == "__main__":
    asyncio.run(_demo())
```
Token usage: stuffing cost = corpus tokens x requests. 120K tokens x 10K requests/day = 1.2B input tokens/day. Always log `prompt_tokens` per request.

---

## 🟠 FastAPI Integration
Expose the chosen mode and token count so you can see when the system is stuffing. Put a hard cap on request size so a user upload cannot create a million-token prompt.

```python
from fastapi import FastAPI, HTTPException        # framework
from pydantic import BaseModel, Field             # models
from openai import AsyncOpenAI                    # openai>=1

app = FastAPI()                                   # app
client = AsyncOpenAI()                            # client
CORPUS = ["Heading 8518 headphones. " * 50]       # placeholder knowledge base

class Q(BaseModel):
    question: str = Field(max_length=2000)        # input cap

async def retrieve(q: str, k: int) -> list[str]:  # placeholder retriever
    return CORPUS[:k]

async def llm(prompt: str) -> str:
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=200,
        messages=[{"role": "user", "content": prompt}])
    return r.choices[0].message.content or ""

@app.post("/ask")
async def ask(q: Q) -> dict:
    try:
        return await answer(llm, q.question, CORPUS, retrieve)    # from the advanced block
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's older "stuff" document chain (`create_stuff_documents_chain`) literally stuffs retrieved documents into one prompt; "map-reduce" and "refine" strategies handle corpora that do not fit. In LangGraph, a retrieval node plus a "grade documents" node filters noise before generation.

```python
from langchain.chains.combine_documents import create_stuff_documents_chain   # pip install langchain
from langchain_core.prompts import ChatPromptTemplate                         # prompt
from langchain_core.documents import Document                                 # doc type
from langchain_openai import ChatOpenAI                                       # model

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer ONLY from the context.\n\n{context}"), ("user", "{input}")])
chain = create_stuff_documents_chain(ChatOpenAI(model="gpt-4o-mini", temperature=0), prompt)
# result = await chain.ainvoke({"context": [Document(page_content="Heading 8518 ...")], "input": "headphones?"})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: "The context window is 128K, so I will fill it"
✅ Correct: Use the minimum context that contains the answer.
```python
# Wrong
prompt = all_documents + question

# Right
prompt = top_k_chunks(question, k=5) + question
```

❌ Mistake 2: Ignoring cost and latency until the bill arrives
✅ Correct: Log tokens per request and alert on spikes.
```python
# Wrong
reply = await llm(prompt)

# Right
log.info("prompt_tokens=%d", count(prompt))
```

❌ Mistake 3: Putting the question before 100K tokens of text, or the key evidence in the middle (see topic 077). Put the question and key evidence at the edges.

---

## 🧠 Tricky Interview Question
**Q**: "A model supports 1M tokens. A colleague says RAG is now obsolete. Do you agree?"

**Answer**: No. Long context helps for small to medium corpora and one-off analysis, but RAG is still better for most production uses: cost scales with tokens per request, latency grows, accuracy can drop with noise and position effects, corpora are often larger than any window, and RAG gives citations, access control and fresh data. A practical design uses RAG for selection and long context for the selected material, with prompt caching when the same large context is reused.

---

## ⚫ Interview Questions + Answers

Q1: What is context stuffing?
A1: Putting all available text into the prompt instead of selecting only the relevant parts.

Q2: Name two downsides.
A2: Higher cost and latency, and possible accuracy loss because of noise and "lost in the middle".

Q3: When is stuffing acceptable?
A3: Small corpora that fit comfortably in the window, prototypes, one-off analysis, or when the same context is reused with prompt caching.

Q4: What are alternatives?
A4: RAG with reranking, hierarchical summaries, map-reduce, metadata filters, and caching.

Q5 (Hard): How do you decide between stuffing and RAG with data?
A5: Run an eval on both strategies with real questions: measure accuracy, cost per query, p95 latency. Include questions where the evidence is in the middle and where many distractors exist. Pick the cheapest approach that meets accuracy targets, re-evaluate when the corpus grows or models change, and consider a hybrid (RAG select, then long-context read with caching).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Corpus is small and fits easily
- Prototyping quickly
- One-off analysis of a single document

❌ Avoid when:
- High request volume (cost)
- Corpus is large or changes often
- Low latency is needed
- You need citations and access control per document

---

## 📊 Visual Diagram
```
 STUFFING                               RAG
 +--------------------------+           +----------------+
 | doc1 doc2 doc3 ... doc40 |           | question       |
 | (120,000 tokens)         |           |   -> retrieve  |
 | question                 |           | top-5 chunks   |
 +--------------------------+           | (2,000 tokens) |
   cost: high  latency: high            +----------------+
   risk: lost in the middle               cost: low  latency: low
```

---

## 💰 Cost Impact
Example (illustrative; check current prices): 120K-token prompts at $0.15 per 1M input tokens = $0.018 per call; 10K calls/day = $180/day. A 2K-token RAG prompt = $0.0003 per call = $3/day (before retrieval costs). With a more expensive model, multiply accordingly.

Optimisation: retrieve then rerank, set k by eval, compress chunks, use prompt caching for repeated large contexts, route small corpora to stuffing only when cheap, and track tokens per request.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context stuffing | Putting everything in the prompt | Prompt में सब कुछ डालना |
| Context window | Max tokens model can read | Model कितने tokens पढ़ सकता है |
| RAG | Retrieve relevant text first | पहले relevant text ढूँढना |
| Distractor | Irrelevant text that confuses | भटकाने वाला बेकार text |
| Top-k | Best k retrieved items | सबसे अच्छे k items |
| Map-reduce | Process parts, then combine | हिस्सों को process करके जोड़ना |

---

## ⚡ 3-Line Summary
English: Context stuffing pastes everything into the prompt: simple, but costly, slow and sometimes less accurate. Use it for small corpora and prototypes; use RAG for production scale. Measure tokens and quality instead of assuming a bigger window is better.
Hindi: Context stuffing सब कुछ prompt में डाल देता है: सरल, पर महँगा, धीमा और कभी-कभी कम सटीक। छोटे corpora और prototypes के लिए ठीक; production scale के लिए RAG। बड़ी window बेहतर है यह मान लेने की जगह tokens और quality मापो।

---

## ➡️ Next Topic
**077. Lost in the Middle Problem** — why models miss facts placed in the middle of long prompts, and how to position information.
