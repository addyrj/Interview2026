---

# 176. Chunk Size Impact on RAG
# हिंदी में: RAG पर Chunk Size का असर

---

## 🔵 Simple Definition (English)
Chunk size changes almost every part of a RAG system: how sharp the vectors are, how much noise reaches the LLM, how many tokens you pay for, how fast search is, and whether the full answer fits in one chunk. Topic 166 was about choosing a number; this topic explains what each choice does to the system, so you can diagnose problems.

## 🔵 सरल परिभाषा (Hindi)
Chunk size RAG system के लगभग हर हिस्से को बदलता है: vectors कितने तेज़ हैं, LLM तक कितना noise पहुँचता है, कितने tokens का पैसा लगता है, search कितनी तेज़ है, और क्या पूरा जवाब एक chunk में आता है। Topic 166 एक number चुनने के बारे में था; यह topic बताता है कि हर choice system पर क्या असर डालती है ताकि आप समस्याएँ diagnose कर सकें।

---

## 🔴 Problem it Solves
- Symptoms such as "answers are incomplete", "answers are vague", "bill is too high", "search is slow" often come from chunk size, but teams blame the LLM.
- Without understanding the effects you tune blindly.
- Knowing the effect map lets you go from symptom to the right knob in one step.

## 🔴 यह क्यों बना? (Hindi)
- "जवाब अधूरे हैं", "जवाब धुंधले हैं", "bill बहुत है", "search धीमी है" जैसे लक्षण अक्सर chunk size से आते हैं, पर teams LLM को दोष देती हैं।
- असर समझे बिना tuning अंधेरे में तीर है।
- Effect map से लक्षण देखकर सीधे सही knob तक पहुँच सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Chunk size sets the unit of meaning stored in ONE vector
Step 2 → Small chunk: vector is sharp (one idea) -> high precision, but answer may be split -> low completeness
Step 3 → Large chunk: vector is an average of many ideas -> blurry ranking, but answer is complete
Step 4 → Prompt tokens = top_k x chunk_size (+ prompt): large chunks raise cost and latency
Step 5 → Large prompts risk "lost in the middle" -> the LLM ignores middle chunks
Step 6 → Index size: smaller chunks = more vectors = more storage and slower ANN search
Step 7 → Embedding limit: chunk must fit the embedding model window
Step 8 → Net effect = a curve; find the best point with an eval set (topic 175)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Chunk size तय करता है कि एक vector में कितना अर्थ बैठेगा
Step 2 → छोटा chunk: vector तेज़ (एक idea) -> precision ऊँची, पर जवाब बँट सकता है -> completeness कम
Step 3 → बड़ा chunk: vector कई ideas का औसत -> ranking धुंधली, पर जवाब पूरा
Step 4 → Prompt tokens = top_k x chunk_size: बड़े chunks से cost और latency बढ़ती है
Step 5 → बड़े prompts में "lost in the middle" का जोखिम
Step 6 → Index size: छोटे chunks = ज़्यादा vectors = ज़्यादा storage
Step 7 → Embedding limit: chunk model की window में fit होना चाहिए
Step 8 → असर एक curve है; eval set से best point खोजो
```

---

## 🟡 Real World Example
**Tariff Classification System** - symptom to cause:
- "The bot gives the right code but forgets the exemption" -> chunks too small; the exemption sits in the next chunk. Use parent expansion or 500-800 token chunks for notes.
- "The bot returns codes from the wrong chapter" -> chunks too large for line items; vectors blurry. Use one tariff line per chunk.
- "Cost per query doubled after we moved to 1500-token chunks" -> top_k x size. Reduce top_k or size.

**Zomato style**: Reviews are short; 1000-token chunks would glue many reviews and the "spicy" signal gets diluted.

## 🟡 Real Example Hindi mein
**Tariff System** - लक्षण से कारण:
- "Bot सही code देता है पर exemption भूल जाता है" -> chunks बहुत छोटे; exemption अगले chunk में है। Notes के लिए parent expansion या 500-800 token chunks।
- "Bot गलत chapter के codes देता है" -> line items के लिए chunks बहुत बड़े; vectors धुंधले। एक tariff line प्रति chunk।
- "1500-token chunks के बाद cost दोगुनी" -> top_k x size। top_k या size घटाओ।

**Zomato**: Reviews छोटे होते हैं; 1000-token chunk कई reviews जोड़ देगा और "spicy" signal पतला हो जाएगा।

---

## 💻 Code Example — Basic
```python
# Basic simulation: chunk size vs. (a) noise sent to the LLM, (b) prompt tokens, (c) answer completeness.
facts = [  # 8 facts; each fact is 6 words
    "smartphones heading 8517 duty ten percent",
    "microphones heading 8518 duty seven percent",
    "batteries heading 8507 duty twenty percent",
    "televisions heading 8528 duty fifteen percent",
    "cameras heading 8525 duty ten percent",
    "speakers heading 8518 duty eight percent",
    "monitors heading 8528 duty twelve percent",
    "routers heading 8517 duty five percent",
]
words = " ".join(facts).split()  # whole corpus as words
FACT_LEN = 6  # words per fact

def chunks(size: int) -> list[tuple[int, int]]:  # chunk spans in words
    return [(i, min(i + size, len(words))) for i in range(0, len(words), size)]  # (start, end)

def analyse(size: int, target_fact: int = 3, top_k: int = 2) -> dict[str, float]:  # metrics for one size
    fs, fe = target_fact * FACT_LEN, (target_fact + 1) * FACT_LEN  # target fact word span
    best = [c for c in chunks(size) if c[0] < fe and c[1] > fs]  # chunks overlapping the target fact
    chunk = best[0]  # the chunk we would retrieve
    inside = min(fe, chunk[1]) - max(fs, chunk[0])  # words of the fact inside the chunk
    return {"size": size,  # chunk size in words
            "completeness": inside / FACT_LEN,  # share of the fact that is in this chunk
            "noise": 1 - inside / (chunk[1] - chunk[0]),  # share of chunk that is irrelevant
            "prompt_words": top_k * (chunk[1] - chunk[0])}  # words sent to the LLM

for s in (4, 6, 12, 48):  # tiny, exact, medium, huge
    print(analyse(s))  # tiny -> incomplete; huge -> mostly noise and many words
```

## 💻 Code Example — Advanced
```python
# Production-style benchmark: for each chunk size measure recall, precision proxy, prompt tokens,
# estimated cost and latency, then print one comparison table. Retriever is injected (async).
from __future__ import annotations  # modern hints

import asyncio  # async
import statistics  # mean
import time  # latency
from dataclasses import dataclass  # container
from typing import Awaitable, Callable  # types

Retriever = Callable[[list[str], str, int], Awaitable[list[str]]]  # (chunks, query, k) -> top chunks


@dataclass
class SizeResult:  # one row of the table
    size_words: int  # chunk size
    n_chunks: int  # index size
    recall: float  # gold found in top-k
    noise: float  # share of retrieved text that is not the gold sentence
    prompt_tokens: float  # average tokens sent per query (words * 1.3)
    cost_per_1k_queries: float  # USD at given input price
    latency_ms: float  # average retrieval latency


def chunk_words(text: str, size: int) -> list[str]:  # non-overlapping chunks
    if size <= 0:  # validate
        raise ValueError("size must be positive")  # error
    w = text.split()  # words
    return [" ".join(w[i:i + size]) for i in range(0, len(w), size)]  # slices


async def benchmark(text: str, cases: list[tuple[str, str]], retrieve: Retriever, sizes: list[int],
                    k: int = 2, price_per_m: float = 0.15) -> list[SizeResult]:  # price = USD per 1M input tokens
    rows: list[SizeResult] = []  # table
    for size in sizes:  # each size
        chunks = chunk_words(text, size)  # build chunks
        hits, noises, toks, lats = [], [], [], []  # metrics
        for q, gold in cases:  # each question
            t0 = time.perf_counter()  # start timer
            try:  # retrieval may fail
                top = await retrieve(chunks, q, k)  # retrieve
            except Exception:  # count as a miss
                hits.append(0); noises.append(1.0); toks.append(0.0); lats.append(0.0)  # defaults
                continue  # next question
            lats.append((time.perf_counter() - t0) * 1000)  # latency in ms
            joined = " ".join(top)  # context sent to LLM
            ok = gold.lower() in joined.lower()  # recall hit
            hits.append(1 if ok else 0)  # record
            noises.append(1 - len(gold.split()) / max(1, len(joined.split())) if ok else 1.0)  # noise
            toks.append(len(joined.split()) * 1.3)  # rough tokens
        avg_tok = statistics.mean(toks)  # average prompt tokens
        rows.append(SizeResult(size, len(chunks), statistics.mean(hits), statistics.mean(noises), avg_tok,
                               avg_tok * 1000 * price_per_m / 1_000_000, statistics.mean(lats)))  # row
    return rows  # all rows


async def keyword_retrieve(chunks: list[str], q: str, k: int) -> list[str]:  # demo retriever
    await asyncio.sleep(0)  # async placeholder
    qw = set(q.lower().split())  # query words
    return sorted(chunks, key=lambda c: -len(qw & set(c.lower().split())))[:k]  # top-k


if __name__ == "__main__":  # demo
    text = ("smartphones heading 8517 duty ten percent microphones heading 8518 duty seven percent "
            "batteries heading 8507 duty twenty percent televisions heading 8528 duty fifteen percent")  # corpus
    cases = [("heading smartphones", "8517"), ("duty batteries", "twenty percent")]  # eval
    for r in asyncio.run(benchmark(text, cases, keyword_retrieve, [3, 6, 12, 24])):  # run
        print(r)  # print rows
```

---

## 🟠 FastAPI Integration
Add chunk-size diagnostics to your API: log chunk token counts and prompt tokens per request, and return them in a debug field. This reveals when oversized chunks are inflating cost.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # pydantic v2

app = FastAPI()  # app


class Ask(BaseModel):  # request
    question: str  # user question


@app.post("/ask")  # route
async def ask(req: Ask) -> dict:  # handler
    chunks = ["smartphones heading 8517 duty ten percent", "batteries heading 8507 duty twenty percent"]  # from your retriever
    top = await keyword_retrieve(chunks, req.question, 2)  # retrieve
    sizes = [len(c.split()) for c in top]  # chunk sizes in words
    return {"context": top,  # context for the LLM
            "debug": {"chunk_words": sizes, "approx_prompt_tokens": int(sum(sizes) * 1.3),  # visible diagnostics
                      "warn": "chunks very large" if sizes and max(sizes) > 400 else None}}  # alert
```

---

## 🔗 LangChain / LangGraph Connection
In LangChain the size lives in the splitter, and `search_kwargs={"k": ...}` multiplies it. Compute prompt budget as `k * chunk_size`. LangGraph can hold `chunk_size` and `k` in config so the same graph is benchmarked with several values.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter  # splitter

def build_retriever_config(chunk_size: int, k: int, context_budget: int = 3000) -> dict[str, int]:  # sanity check
    if chunk_size * k > context_budget:  # prompt budget guard
        k = max(1, context_budget // chunk_size)  # reduce k automatically
    return {"chunk_size": chunk_size, "k": k}  # final config

cfg = build_retriever_config(chunk_size=1000, k=8)  # k reduced to 3
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=cfg["chunk_size"], chunk_overlap=cfg["chunk_size"] // 10)  # tokens
# retriever = vectorstore.as_retriever(search_kwargs={"k": cfg["k"]})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Increasing chunk_size to fix "incomplete answers" without checking top_k and cost
✅ Correct: Prefer parent expansion or neighbour retrieval for the top hit only.

```python
# Wrong - doubles cost for every query
chunk_size, top_k = 1600, 6  # 9,600 tokens per prompt

# Right - small chunks to search, expand only the best hit
chunk_size, top_k, expand_top = 300, 6, 1  # about 300*5 + 1500 tokens
```

❌ Mistake 2: Using recall@k as the only metric when comparing sizes (bigger chunks inflate recall).
✅ Correct: Also track precision, tokens per query and end-to-end answer accuracy.

❌ Mistake 3: Ignoring token differences across languages (Hindi text uses more tokens per character).
✅ Correct: Set sizes in tokens, per language.

---

## 🧠 Tricky Interview Question
**Q**: "You halve the chunk size. Index size doubles, but latency barely changes and quality improves. Why is latency not worse?"

**Answer**: Vector search uses approximate nearest-neighbour indexes (HNSW/IVF) whose query time grows roughly with log of the number of vectors, so doubling vectors adds only a small cost. The dominant latency is usually the LLM call, which gets faster when the prompt shrinks (fewer input tokens, less time to first token). So smaller chunks can reduce total latency while raising precision; the costs you pay are storage, embedding calls at ingestion, and possibly incomplete answers, which parent expansion or rerankers can fix.

---

## ⚫ Interview Questions + Answers

Q1: What happens when chunks are too small?
A1: High precision but fragments: answers split across chunks, missing context, more vectors to store.

Q2: What happens when chunks are too large?
A2: Blurry embeddings, noisy context, higher prompt cost and latency, risk of "lost in the middle".

Q3: How does chunk size relate to top_k?
A3: Prompt tokens are about top_k x chunk_size. Bigger chunks usually need a smaller top_k to stay within budget.

Q4: Does chunk size affect the vector database?
A4: Yes: number of vectors (storage, index build time), and metadata overhead per vector. Smaller chunks mean more of both.

Q5: (Hard) A product team wants both precise search and complete answers. What do you propose?
A5: Decouple search size from answer size: parent-child (small-to-big) or window retrieval, plus a reranker for precision and a context budget manager that trims low-score chunks. Evaluate with recall@k, precision, answer correctness and tokens per query on a labelled set.

---

## 🔷 When to Use + When Not to Use
✅ Think about size effects when:
- Debugging answer quality, cost or latency problems
- Changing embedding model, LLM or language mix

❌ Do not tune size endlessly when:
- Quality is already good and the budget is met
- A structural splitter (headings/records) already gives natural units

---

## 📊 Visual Diagram
```
 chunk size →     SMALL                MEDIUM               LARGE
 ─────────────────────────────────────────────────────────────────────
 vector sharpness  sharp ████████      ok ████              blurry █
 answer complete   low █               good ██████          high ████████
 noise in prompt   low █               medium ███           high ████████
 prompt tokens     low █               medium ███           high ████████
 #vectors/storage  high ████████       medium ████          low █
 lost-in-middle    low                 low                  HIGH
                      ▲
                      └─ best quality is usually in the middle (the knee)
```

---

## 💰 Cost Impact
- Prompt tokens per query = top_k x chunk_tokens. Examples at $0.15 per 1M input tokens, 100K queries/day: 5 x 200 = 1,000 tokens -> $15/day; 5 x 800 = 4,000 tokens -> $60/day; 5 x 1,500 = 7,500 -> $112.50/day.
- Embedding cost at ingestion is about constant (same total text); storage grows with smaller chunks (more vectors, more metadata).
- Optimise: small chunks + reranker + top 3 instead of 8; expand only the best hit; cache frequent queries; use prompt caching for stable context.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Precision | Relevant share of retrieved text | Retrieved में काम का हिस्सा |
| Completeness | Whole answer present | पूरा जवाब मौजूद |
| Noise | Irrelevant text in prompt | Prompt में बेकार text |
| Lost in the middle | LLM ignores middle context | बीच का context अनदेखा |
| ANN index | Approximate nearest neighbour index | Approximate नज़दीकी search index |
| Context budget | Max tokens for context | Context के लिए max tokens |

---

## ⚡ 3-Line Summary
English: Chunk size trades vector sharpness and cost against answer completeness. Small chunks are precise but fragmented; large chunks are complete but noisy and expensive. Diagnose by symptom, then use parent expansion or reranking instead of just growing chunks.
Hindi: Chunk size में vector की तेज़ी और cost बनाम जवाब की पूर्णता का trade-off है। छोटे chunks precise पर बिखरे; बड़े chunks पूरे पर noisy और महँगे। लक्षण देखकर diagnose करो, और chunks बड़े करने की बजाय parent expansion या reranking इस्तेमाल करो।

---

## ➡️ Next Topic
**177. Chunk Overlap Impact** - what overlap really does to recall, duplicates and cost.
