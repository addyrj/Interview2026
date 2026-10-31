---

# 393. Context Precision Score
# हिंदी में: Context Precision Score

---

## 🔵 Simple Definition (English)
Context precision measures whether the useful chunks appear at the TOP of the retrieved list. If the 5 chunks returned are [relevant, relevant, noise, noise, noise], precision is high. If they are [noise, noise, noise, relevant, relevant], it is low, because the ranking is poor.

## 🔵 सरल परिभाषा (Hindi)
Context precision नापता है कि काम के chunks retrieved list में सबसे ऊपर आए या नहीं। 5 chunks [सही, सही, noise, noise, noise] आएँ तो precision ज़्यादा है। [noise, noise, noise, सही, सही] आएँ तो कम, क्योंकि ranking खराब है।

---

## 🔴 Problem it Solves
LLMs read noisy context poorly, and noise costs tokens. Even when the right chunk is retrieved, if it sits below four irrelevant ones, it may be cut off by a token limit or ignored ("lost in the middle"). Precision shows whether your retriever and reranker order results well.

## 🔴 यह क्यों बना? (Hindi)
LLM noisy context को ठीक से नहीं पढ़ पाते और noise tokens भी खाता है। सही chunk मिल भी जाए पर चार irrelevant chunks के नीचे हो, तो token limit में कट सकता है या ignore हो सकता है ("lost in the middle")। Precision बताता है कि retriever और reranker results को सही क्रम में लगा रहे हैं या नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → For a question, take the retrieved chunks in rank order: c1, c2, ... ck
Step 2 → Judge each chunk: relevant (1) or not (0)  [LLM judge vs reference, or label]
Step 3 → For each position k compute Precision@k = relevant_in_top_k / k
Step 4 → Average Precision@k ONLY at positions where the chunk is relevant
Step 5 → context_precision = that average (0..1)
        Example [1,1,0,0,0]: P@1=1, P@2=1 -> (1+1)/2 = 1.0
        Example [0,0,0,1,1]: P@4=1/4, P@5=2/5 -> (0.25+0.4)/2 = 0.325
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → एक सवाल के लिए retrieved chunks को rank order में लो: c1, c2, ... ck
Step 2 → हर chunk judge करो: relevant (1) या नहीं (0)  [LLM judge + reference, या labels]
Step 3 → हर position k पर Precision@k = top-k में relevant / k
Step 4 → Precision@k का average सिर्फ उन positions पर जहाँ chunk relevant है
Step 5 → context_precision = वो average (0..1)
        उदाहरण [1,1,0,0,0]: P@1=1, P@2=1 -> (1+1)/2 = 1.0
        उदाहरण [0,0,0,1,1]: P@4=1/4, P@5=2/5 -> (0.25+0.4)/2 = 0.325
```

---

## 🟡 Real World Example
**Tariff Classification System**: Question "HS code and duty for lithium-ion batteries". Retriever (top 5) returns: (1) HS 8507 heading text - relevant, (2) Chapter 85 note on batteries - relevant, (3) cotton shirts HS 6109, (4) steel pipes HS 7306, (5) FAQ on customs forms. Order [1,1,0,0,0] gives precision 1.0. After a bad embedding change the order becomes [0,0,1,0,1] giving about 0.37, a clear drop. Fix: add a cross-encoder reranker or reduce top-k.

**Amazon AI**: For "waterproof running shoes" search chunks, product pages should come before generic shoe-care articles.

## 🟡 Real Example Hindi mein
**Tariff System**: सवाल "lithium-ion batteries का HS code और duty"। Retriever (top 5) लौटाता है: (1) HS 8507 heading - relevant, (2) Chapter 85 की battery note - relevant, (3) cotton shirts HS 6109, (4) steel pipes HS 7306, (5) customs forms FAQ। क्रम [1,1,0,0,0] से precision 1.0। Embedding बदलने के बाद क्रम [0,0,1,0,1] हो जाए तो precision लगभग 0.37, साफ गिरावट। Fix: cross-encoder reranker लगाओ या top-k घटाओ।

**Amazon AI**: "waterproof running shoes" के लिए product pages, shoe-care articles से पहले आने चाहिए।

---

## 💻 Code Example — Basic
```python
# Basic: context precision from relevance labels (pure Python, runs offline).
def context_precision(relevance: list[int]) -> float:
    """relevance[i] is 1 if the chunk at rank i+1 is relevant else 0."""
    if not any(relevance):                       # no relevant chunk at all
        return 0.0
    hits = 0                                     # relevant chunks seen so far
    precisions: list[float] = []                 # Precision@k at relevant positions
    for k, rel in enumerate(relevance, start=1): # k = rank starting from 1
        if rel:                                  # only count at relevant positions
            hits += 1
            precisions.append(hits / k)          # Precision@k
    return sum(precisions) / len(precisions)     # average


print(context_precision([1, 1, 0, 0, 0]))        # 1.0   (best ordering)
print(context_precision([1, 0, 1, 0, 0]))        # (1 + 2/3)/2 = 0.833
print(round(context_precision([0, 0, 0, 1, 1]), 3))   # 0.325 (worst useful ordering)
print(context_precision([0, 0, 0, 0, 0]))        # 0.0
```

## 💻 Code Example — Advanced
```python
# Advanced: async precision with a pluggable relevance judge (LLM in prod, rule offline).
import asyncio
from typing import Awaitable, Callable

RelJudge = Callable[[str, str, str], Awaitable[bool]]   # (question, reference, chunk) -> relevant?


async def llm_relevance_judge(question: str, reference: str, chunk: str) -> bool:
    """Production judge using OpenAI; imported lazily. Returns True if chunk is useful."""
    from openai import AsyncOpenAI
    client = AsyncOpenAI()
    prompt = (f"Question: {question}\nReference answer: {reference}\nChunk: {chunk}\n"
              "Is the chunk useful to arrive at the reference answer? Reply YES or NO.")
    r = await client.chat.completions.create(
        model="gpt-4o-mini", temperature=0, max_tokens=3,
        messages=[{"role": "user", "content": prompt}])
    return (r.choices[0].message.content or "").strip().upper().startswith("YES")


async def rule_judge(question: str, reference: str, chunk: str) -> bool:
    """Offline stand-in: chunk is relevant if it shares >=2 words with the reference."""
    ref = set(reference.lower().split())
    return len(ref & set(chunk.lower().split())) >= 2


async def precision_async(question: str, reference: str, chunks: list[str],
                          judge: RelJudge, concurrency: int = 5) -> float:
    sem = asyncio.Semaphore(concurrency)               # respect rate limits

    async def one(c: str) -> int:
        async with sem:
            try:
                return int(await judge(question, reference, c))
            except Exception:                           # judge failed -> treat as unknown=0
                return 0

    rel = await asyncio.gather(*(one(c) for c in chunks))   # order preserved by gather
    return context_precision(list(rel))                      # from the basic example


async def main() -> None:
    chunks = ["HS 8507 lithium-ion batteries duty 0 percent",
              "Chapter 85 note batteries duty",
              "cotton shirts HS 6109", "steel pipes HS 7306"]
    ref = "lithium-ion batteries HS 8507 duty 0 percent"
    print(await precision_async("duty on batteries?", ref, chunks, rule_judge))


asyncio.run(main())
```

---

## 🟠 FastAPI Integration
```python
# FastAPI: debug endpoint that shows retrieval quality for a query (internal use)
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class RetrievalCheck(BaseModel):
    question: str
    reference: str
    chunks: list[str]                                  # retriever output in rank order


@app.post("/debug/context-precision")
async def check(body: RetrievalCheck) -> dict:
    score = await precision_async(body.question, body.reference, body.chunks, rule_judge)
    return {"context_precision": round(score, 3),
            "advice": "add reranker or lower top_k" if score < 0.6 else "ranking ok"}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# Ragas has LLMContextPrecisionWithReference (needs reference) and
# LLMContextPrecisionWithoutReference (uses the response). Needs an LLM key.
from ragas import SingleTurnSample
from ragas.metrics import LLMContextPrecisionWithReference
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI

metric = LLMContextPrecisionWithReference(llm=LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini")))
sample = SingleTurnSample(
    user_input="Duty on lithium-ion batteries?",
    retrieved_contexts=["HS 8507 batteries duty 0 percent", "cotton shirts HS 6109"],
    reference="Duty on lithium-ion batteries is 0 percent.",
)
# score = await metric.single_turn_ascore(sample)
```
In LangChain, improve precision with `ContextualCompressionRetriever` plus a reranker (e.g. a cross-encoder or Cohere Rerank) wrapped around your base retriever; in LangGraph add a "grade documents" node that filters irrelevant chunks before generation.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Confusing precision with recall
✅ Correct: Precision = ordering/purity of retrieved chunks; recall = coverage of needed information.

```python
# Wrong: "we retrieved 20 chunks so retrieval is great"
# Right: report both
print({"context_precision": 0.4, "context_recall": 0.95})   # recall ok, ranking/noise bad
```

❌ Mistake 2: Raising top_k to fix recall without checking precision
✅ Correct: More chunks usually adds noise and cost; add a reranker, then raise k.

```python
# Wrong
retriever = vs.as_retriever(search_kwargs={"k": 30})
# Right: fetch 30, rerank, keep best 5
candidates = vs.as_retriever(search_kwargs={"k": 30}).invoke(q)
top = rerank(q, candidates)[:5]
```

❌ Mistake 3: Using a different judge prompt per run
✅ Correct: Freeze judge prompt and model.

---

## 🧠 Tricky Interview Question

**Q**: "You reduce top_k from 10 to 3. Context precision rises from 0.55 to 0.85, but answer correctness drops. Why?"

**Answer**: With fewer chunks there is less noise (precision up), but you may have cut off a needed chunk (recall down). Precision looks only at the ordering of what is retrieved, not at what is missing. Check context recall. The right solution is to keep a larger candidate pool, rerank with a cross-encoder, and then pass the best 3-5 to the LLM, improving both precision and recall.

---

## ⚫ Interview Questions + Answers

Q1: What does high context precision tell you?
A1: Relevant chunks are ranked near the top, so the LLM sees little noise at the start of its context.

Q2: Is context precision reference-free?
A2: The standard Ragas version uses the reference answer to judge relevance; a without-reference variant judges using the generated response instead (weaker signal).

Q3: Compute precision for relevance [1,0,1].
A3: P@1 = 1, P@3 = 2/3. Average over relevant positions = (1 + 0.667)/2 = 0.833.

Q4: How can you improve context precision?
A4: Reranker (cross-encoder), metadata filters, hybrid search (BM25 + vectors), better chunking, query rewriting, and lower top_k after reranking.

Q5 (Hard): Explain how context precision relates to Mean Average Precision (MAP) and why it is order-sensitive.
A5: Context precision is essentially Average Precision for one query: it averages Precision@k at each relevant rank. Because early positions count with a bigger denominator effect, a relevant item at rank 1 contributes 1.0 while at rank 5 contributes at most 0.2. MAP is the mean of this over many queries. Order-sensitivity matters because LLMs weigh early context more heavily and truncation removes late chunks, so ranking quality directly affects answer quality.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tuning retriever, reranker, hybrid search
- Debugging why the right chunk is retrieved but ignored

❌ Avoid when:
- You use a single-chunk lookup (no ranking to evaluate)
- You have no references and no judge budget (use cheaper hit-rate / MRR with labels)

---

## 📊 Visual Diagram
```
 rank:      1     2     3     4     5
 chunks:  [REL] [REL] [ - ] [ - ] [ - ]   P@1=1  P@2=1          → precision 1.00
 chunks:  [ - ] [ - ] [REL] [ - ] [REL]   P@3=.33 P@5=.40       → precision 0.37
                       ▲
        good ranking pushes relevant chunks LEFT (top)
```

---

## 💰 Cost Impact
- LLM judging is one call per retrieved chunk: 5 chunks x ~500 tokens = 2,500 input tokens plus tiny outputs per sample, about $0.0004 on gpt-4o-mini. 1,000 rows cost around $0.40.
- Payoff: higher precision lets you send fewer chunks to the generator. Cutting from 10 chunks to 4 (about 400 tokens each) saves 2,400 input tokens per query; at 100K queries/day on gpt-4o-mini that is about $36/day.
- Optimise evaluation by caching chunk judgements (same chunk and reference reused) and using label-based hit-rate for large sweeps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Context precision | Relevant chunks ranked high | सही chunks का ऊपर होना |
| Precision@k | Relevant fraction in top k | Top k में relevant का अनुपात |
| Reranker | Model that reorders results | Results का क्रम सुधारने वाला model |
| top_k | Number of chunks retrieved | कितने chunks लाने हैं |
| Noise | Irrelevant retrieved text | बेकार retrieved text |
| MAP | Mean average precision | Average precision का औसत |

---

## ⚡ 3-Line Summary
English: Context precision rewards putting relevant chunks at the top of the retrieved list (average of Precision@k at relevant ranks). Low precision means noisy or badly ordered retrieval, fixed by reranking and filters. Always read it together with context recall.
Hindi: Context precision उस retrieval को पुरस्कृत करता है जो relevant chunks को list में ऊपर रखे (relevant ranks पर Precision@k का average)। कम precision का मतलब noisy या गलत क्रम की retrieval, जिसे reranking और filters से सुधारते हैं। इसे हमेशा context recall के साथ पढ़ो।

---

## ➡️ Next Topic
**394. Context Recall Score** — precision says the top is clean; recall says whether we fetched everything needed.
